from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from .cli_run_coverage_limited_replay import MODEL_COMPONENTS
from .core import atomic_write_json, atomic_write_text, sha256_hex
from .coverage_limited_replay_v1 import load_population_bytes, parse_population_bytes
from .real_input_replay_v1 import (
    F02_R1_SOURCE_SCHEMA,
    PREDECESSOR_EXECUTABLE_BUNDLE_IDENTITY,
    commit_selection_seal,
    create_selection_seal,
    execute_strict_w1_model_stage,
    execute_w1_outcomes_from_seal,
    load_feature_sidecar,
    load_source_manifest,
    read_selection_seal,
)


PREDECESSOR_HEAD = "79b46dc1f63f1cd215cc0ebc0c91b4ec09e7dc71"
PREDECESSOR_OUTPUT_PATH = (
    "control/m3top3/first-scorecard/v1.0/runs/"
    "AAA-M3TOP3-FIRST-SCORECARD-20260905-093656-CODEX-01"
)
PREDECESSOR_OUTPUT_TREE = "1d73cc942a3524571ea214724c887c3964dca13f"
SUCCESSOR_COMPONENTS = tuple(
    dict.fromkeys(
        (
            *MODEL_COMPONENTS,
            ".gitattributes",
            "tools/m3top3/real_input_replay_v1.py",
            "tools/m3top3/cli_run_real_input_replay.py",
        )
    )
)
R1_INPUT_PROFILE = "F02_R1_EXPLORATORY_V1"
R1_VALIDATION_ROLES = {"CTLV", "MODV", "ENGV", "PMOV", "IVA"}


def _hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _assert_clean_repo(repo: Path) -> None:
    status = subprocess.check_output(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=repo,
        text=True,
    )
    if status:
        raise ValueError("score-and-seal requires a clean worktree so Git and executable bytes cannot diverge")


def _bind_successor_bundle(
    repo: Path, manifest: dict[str, Any] | None = None,
) -> tuple[str, list[dict[str, Any]]]:
    relatives = list(SUCCESSOR_COMPONENTS)
    if manifest is not None and manifest.get("schema_version") == F02_R1_SOURCE_SCHEMA:
        from . import f02_r1_adapter

        f02_r1_adapter.validate_source_manifest(
            manifest,
            manifest_content_sha256=hashlib.sha256(f02_r1_adapter.json_bytes(manifest)).hexdigest(),
            repo=repo,
            expected_run_id=f02_r1_adapter.RUN_ID,
        )
        relatives.extend([
            "tools/m3top3/f02_r1_adapter.py",
            *[item["path"] for item in manifest["input_profile"]["dependencies"]],
            f"{f02_r1_adapter.RUN_ROOT}/inputs/SOURCE_MANIFEST.json",
            f"{f02_r1_adapter.RUN_ROOT}/inputs/FEATURE_SIDECAR.jsonl",
        ])
    components = []
    for relative in dict.fromkeys(relatives):
        path = repo / relative
        components.append({"path": relative, "byte_size": path.stat().st_size, "sha256": _hash_file(path)})
    return "M3TOP3-REAL-INPUT-EXECUTABLE-BUNDLE-SHA256:" + sha256_hex(components), components


def _verify_r1_validation_gate(
    repo: Path, args: argparse.Namespace, manifest: dict[str, Any],
    manifest_hash: str, sidecar_hash: str, bundle_identity: str,
    components: list[dict[str, Any]],
) -> dict[str, Any]:
    """Bind the exact P4 evidence before any R1 engine call or output write."""
    from . import f02_r1_adapter

    root = repo / f02_r1_adapter.RUN_ROOT
    exact_paths = {
        "source_manifest": root / "inputs/SOURCE_MANIFEST.json",
        "feature_sidecar": root / "inputs/FEATURE_SIDECAR.jsonl",
        "affected_validation_report": root / "AFFECTED_VALIDATION_REPORT.json",
        "output_dir": root / "score-and-seal",
    }
    if args.pmo_run_id != f02_r1_adapter.RUN_ID:
        raise ValueError("R1 requires the approved existing run ID")
    for name, expected in exact_paths.items():
        supplied = getattr(args, name, None)
        if supplied is None or Path(supplied).resolve() != expected.resolve():
            raise ValueError(f"R1 requires the exact approved {name} path")
        if any(path.is_symlink() for path in [expected, *expected.parents] if path != repo.parent):
            raise ValueError("R1 paths cannot be symlink redirected")
    if exact_paths["output_dir"].exists():
        raise ValueError("R1 score-and-seal output is create-once and already exists")
    report_path = exact_paths["affected_validation_report"]
    report = json.loads(report_path.read_text(encoding="utf-8"))
    if (
        report.get("schema_version") != "AAA-M3TOP3-F02-R1-AFFECTED-VALIDATION-REPORT-v1.0"
        or report.get("run_id") != f02_r1_adapter.RUN_ID
        or report.get("status") != "PASS"
        or report.get("scoring_permitted") is not True
        or report.get("validated_bundle_identity") != bundle_identity
        or report.get("source_manifest_sha256") != manifest_hash
        or report.get("feature_sidecar_sha256") != sidecar_hash
        or report.get("validated_components") != components
    ):
        raise ValueError("R1 exact-target affected validation report mismatch")
    target = report.get("target_commit", "")
    if len(target) != 40 or any(c not in "0123456789abcdef" for c in target):
        raise ValueError("R1 validation target requires an exact commit")
    subprocess.run(["git", "merge-base", "--is-ancestor", target, "HEAD"], cwd=repo, check=True)
    target_files = report.get("validated_target_files", [])
    required_paths = {item["path"] for item in components} | {"tools/m3top3/tests/test_f02_r1_adapter.py"}
    if {item["path"] for item in target_files} != required_paths or len(target_files) != len(required_paths):
        raise ValueError("R1 validation target file scope mismatch")
    for item in target_files:
        relative = item["path"]
        target_blob = subprocess.check_output(["git", "rev-parse", f"{target}:{relative}"], cwd=repo, text=True).strip()
        head_blob = subprocess.check_output(["git", "rev-parse", f"HEAD:{relative}"], cwd=repo, text=True).strip()
        if item["git_blob"] != target_blob or head_blob != target_blob or item["sha256"] != _hash_file(repo / relative):
            raise ValueError(f"R1 validated bytes changed: {relative}")
    receipts = report.get("validation_receipts", [])
    if {item["role"] for item in receipts} != R1_VALIDATION_ROLES or len(receipts) != 5:
        raise ValueError("R1 requires all paired and independent validation roles")
    for item in receipts:
        relative = Path(item["path"])
        receipt_path = (repo / relative).resolve()
        if relative.is_absolute() or ".." in relative.parts or not receipt_path.is_relative_to((root / "validation").resolve()):
            raise ValueError("R1 validation receipt escaped the exact run")
        if _hash_file(receipt_path) != item["sha256"]:
            raise ValueError("R1 validation receipt hash mismatch")
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        if (
            receipt.get("target_commit") != target
            or receipt.get("target_bundle_identity") != bundle_identity
            or receipt.get("role_verdicts", {}).get(item["role"]) != "PASS"
            or receipt.get("target_author") is not False
        ):
            raise ValueError("R1 independent exact-target receipt mismatch")
    return {
        "report_path": report_path.relative_to(repo).as_posix(),
        "report_sha256": _hash_file(report_path),
        "target_commit": target,
        "validation_receipts": receipts,
        "state": "EXACT_TARGET_ALL_REQUIRED_ROLES_PASS",
    }


def _verify_r1_preserved_outputs(repo: Path) -> dict[str, Any]:
    baseline = "6b219f9f3a37dd89b26fc1d6ecec6b8eb890fa9f"
    paths = [
        "control/m3top3/process-calibration/v1.0/runs/AAA-M3TOP3-PROCESS-CALIBRATION-PC1-20260905-143739-CODEX-01",
        "control/m3top3/real-input-replay/v1.0/runs/AAA-M3TOP3-REAL-INPUT-STRICT-PRAGMATIC-20260905-114150-CODEX-01",
    ]
    preserved = []
    for relative in paths:
        before = subprocess.check_output(["git", "rev-parse", f"{baseline}:{relative}"], cwd=repo, text=True).strip()
        after = subprocess.check_output(["git", "rev-parse", f"HEAD:{relative}"], cwd=repo, text=True).strip()
        if before != after:
            raise ValueError(f"R1 predecessor output tree changed: {relative}")
        preserved.append({"path": relative, "tree": before})
    return {"baseline_commit": baseline, "preserved_output_trees": preserved}


def _verify_preserved_predecessor(repo: Path) -> dict[str, Any]:
    comparisons = []
    for relative in MODEL_COMPONENTS:
        current = (repo / relative).read_bytes()
        predecessor_blob = subprocess.check_output(
            ["git", "rev-parse", f"{PREDECESSOR_HEAD}:{relative}"], cwd=repo, text=True
        ).strip()
        current_blob = subprocess.check_output(
            ["git", "rev-parse", f"HEAD:{relative}"], cwd=repo, text=True
        ).strip()
        if current_blob != predecessor_blob:
            raise ValueError(f"preserved predecessor model repository object changed: {relative}")
        if subprocess.run(["git", "diff", "--quiet", "--", relative], cwd=repo).returncode != 0:
            raise ValueError(f"preserved predecessor model component has a working diff: {relative}")
        if relative.endswith("m3top3_v1.0.json") and hashlib.sha256(current).hexdigest() != "eecde22a7744cff505c624bb6f0bdb11714352a122632238ea68d9cd0fbacb98":
            raise ValueError("runtime config bytes do not match the preserved bound config SHA-256")
        comparisons.append(
            {
                "path": relative,
                "git_blob": current_blob,
                "byte_size": len(current),
                "runtime_sha256": hashlib.sha256(current).hexdigest(),
                "repository_blob_byte_identical": True,
            }
        )
    predecessor_tree = subprocess.check_output(
        ["git", "rev-parse", f"{PREDECESSOR_HEAD}:{PREDECESSOR_OUTPUT_PATH}"],
        cwd=repo,
        text=True,
    ).strip()
    current_tree = subprocess.check_output(
        ["git", "rev-parse", f"HEAD:{PREDECESSOR_OUTPUT_PATH}"],
        cwd=repo,
        text=True,
    ).strip()
    if predecessor_tree != PREDECESSOR_OUTPUT_TREE or current_tree != PREDECESSOR_OUTPUT_TREE:
        raise ValueError("predecessor ZERO_SCOREABLE output tree identity mismatch")
    return {
        "predecessor_head": PREDECESSOR_HEAD,
        "predecessor_executable_bundle_identity": PREDECESSOR_EXECUTABLE_BUNDLE_IDENTITY,
        "predecessor_zero_scoreable_output_tree": current_tree,
        "model_components": comparisons,
    }


def _jsonl(rows: list[dict[str, Any]]) -> str:
    return "".join(json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n" for row in rows)


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the strict real-input W1 replay in two sealed phases")
    commands = parser.add_subparsers(dest="command", required=True)

    score = commands.add_parser("score-and-seal", help="Score without any price path and durably seal the cohort")
    score.add_argument("--repo", type=Path, required=True)
    score.add_argument("--output-dir", type=Path, required=True)
    score.add_argument("--pmo-run-id", required=True)
    score.add_argument("--source-manifest", type=Path, required=True)
    score.add_argument("--feature-sidecar", type=Path, required=True)
    score.add_argument("--input-profile", choices=["LEGACY_STRICT_V1", R1_INPUT_PROFILE], default="LEGACY_STRICT_V1")
    score.add_argument("--affected-validation-report", type=Path)

    outcome = commands.add_parser("measure-outcomes", help="Verify the durable seal, then open bound price bytes")
    outcome.add_argument("--repo", type=Path, required=True)
    outcome.add_argument("--selection-seal", type=Path, required=True)
    outcome.add_argument("--output-dir", type=Path, required=True)
    outcome.add_argument("--price-2024", type=Path, required=True)
    outcome.add_argument("--price-2025", type=Path, required=True)
    outcome.add_argument("--price-2026", type=Path, required=True)
    return parser.parse_args(argv)


def _score_and_seal(args: argparse.Namespace, effective_argv: list[str]) -> dict[str, Any]:
    repo = args.repo.resolve()
    output_dir = args.output_dir.resolve()
    started_at = datetime.now(ZoneInfo("Asia/Seoul")).isoformat()
    _assert_clean_repo(repo)
    predecessor_binding = _verify_preserved_predecessor(repo)
    manifest, manifest_content_sha256 = load_source_manifest(args.source_manifest.resolve())
    leaves, sidecar_raw_sha256 = load_feature_sidecar(args.feature_sidecar.resolve())
    is_r1 = manifest.get("schema_version") == F02_R1_SOURCE_SCHEMA
    if is_r1 != (getattr(args, "input_profile", "LEGACY_STRICT_V1") == R1_INPUT_PROFILE):
        raise ValueError("manifest schema and explicit CLI input profile disagree")
    if not is_r1 and getattr(args, "affected_validation_report", None) is not None:
        raise ValueError("R1 validation binding cannot be applied to the legacy input profile")
    code_identity, code_components = _bind_successor_bundle(repo, manifest if is_r1 else None)
    validation_binding = None
    if is_r1:
        predecessor_binding["f02_r1_preservation"] = _verify_r1_preserved_outputs(repo)
        validation_binding = _verify_r1_validation_gate(
            repo, args, manifest, manifest_content_sha256, sidecar_raw_sha256,
            code_identity, code_components,
        )
    population = parse_population_bytes(load_population_bytes(repo))
    model_stage = execute_strict_w1_model_stage(
        population,
        pmo_run_id=args.pmo_run_id,
        manifest=manifest,
        manifest_content_sha256=manifest_content_sha256,
        leaf_records=leaves,
        repo=repo,
        config_path=repo / "tools/m3top3/configs/m3top3_v1.0.json",
        code_identity=code_identity,
    )
    model_stage["input_custody"]["feature_sidecar_raw_file_sha256"] = sidecar_raw_sha256
    if is_r1:
        model_stage["input_custody"]["affected_validation_binding"] = validation_binding

    output_dir.mkdir(parents=True, exist_ok=not is_r1)
    atomic_write_json(output_dir / "STRICT_MODEL_INPUT_BATCH.json", model_stage["model_input_batch"])
    atomic_write_json(output_dir / "STRICT_MODEL_SCORE_BATCH.json", model_stage["scorer_output"])
    atomic_write_text(output_dir / "STRICT_SELECTION_LEDGER.jsonl", _jsonl(model_stage["selection_ledger"]))
    light_stage = {
        key: value
        for key, value in model_stage.items()
        if key not in {"model_input_batch", "scorer_output", "selection_ledger"}
    }
    light_stage["persisted_payload_hashes"] = {
        "model_input_batch_sha256": sha256_hex(model_stage["model_input_batch"]),
        "scorer_output_sha256": sha256_hex(model_stage["scorer_output"]),
        "selection_ledger_sha256": sha256_hex(model_stage["selection_ledger"]),
    }
    atomic_write_json(output_dir / "STRICT_MODEL_STAGE_SUMMARY.json", light_stage)

    sealed_at = datetime.now(ZoneInfo("Asia/Seoul")).isoformat()
    seal = create_selection_seal(model_stage, sealed_at_kst=sealed_at)
    durable_seal = commit_selection_seal(output_dir / "SELECTION_SEAL.json", seal)
    finished_at = datetime.now(ZoneInfo("Asia/Seoul")).isoformat()
    run_manifest = {
        "pmo_run_id": args.pmo_run_id,
        "phase": "SCORE_AND_SEAL",
        "status": "COMPLETED_NONEMPTY_STRICT_SCORE_AND_DURABLE_SEAL",
        "started_at_kst": started_at,
        "finished_at_kst": finished_at,
        "execution_environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "repo": str(repo),
            "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip(),
            "git_branch": subprocess.check_output(["git", "branch", "--show-current"], cwd=repo, text=True).strip(),
        },
        "execution_argv": [sys.executable, "-m", "tools.m3top3.cli_run_real_input_replay", *effective_argv],
        "predecessor_binding": predecessor_binding,
        "successor_executable_bundle_identity": code_identity,
        "successor_code_components": code_components,
        "source_manifest_content_sha256": manifest_content_sha256,
        "feature_sidecar_raw_file_sha256": sidecar_raw_sha256,
        "selection_seal_id": durable_seal["seal_id"],
        "future_price_path_argument_present": False,
        "future_price_value_read_count": 0,
        **({
            "input_profile": manifest["input_profile"],
            "affected_validation_binding": validation_binding,
            "scientific_state": "EXPLORATORY_AFTER_W1_OUTCOME_EXPOSURE",
            "outcome_execution_authorized": False,
        } if is_r1 else {}),
    }
    atomic_write_json(output_dir / "SCORE_AND_SEAL_RUN_MANIFEST.json", run_manifest)
    return {
        "status": run_manifest["status"],
        "pmo_run_id": args.pmo_run_id,
        "scoreable_count": model_stage["window"]["scoreable_count"],
        "coverage": model_stage["window"]["scorer_coverage"],
        "seal_id": durable_seal["seal_id"],
        "output_dir": str(output_dir),
    }


def _prepare_outcome_execution_context(repo: Path, selection_seal_path: Path) -> dict[str, Any]:
    # Preserve the strict order: verify the already-persisted seal before checking
    # executable bytes, and check both before touching any supplied price path.
    preflight_seal = read_selection_seal(selection_seal_path)
    _assert_clean_repo(repo)
    predecessor_binding = _verify_preserved_predecessor(repo)
    code_identity, code_components = _bind_successor_bundle(repo)
    sealed_identity = preflight_seal["sealed_payload"]["successor_executable_bundle_identity"]
    if code_identity != sealed_identity:
        raise ValueError("current outcome executable bundle does not match the durable selection seal")
    return {
        "selection_seal_id": preflight_seal["seal_id"],
        "successor_executable_bundle_identity": code_identity,
        "successor_code_components": code_components,
        "predecessor_binding": predecessor_binding,
        "repo": str(repo),
        "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip(),
        "git_tree": subprocess.check_output(["git", "rev-parse", "HEAD^{tree}"], cwd=repo, text=True).strip(),
        "git_branch": subprocess.check_output(["git", "branch", "--show-current"], cwd=repo, text=True).strip(),
    }


def _measure_outcomes(args: argparse.Namespace, effective_argv: list[str]) -> dict[str, Any]:
    repo = args.repo.resolve()
    output_dir = args.output_dir.resolve()
    started_at = datetime.now(ZoneInfo("Asia/Seoul")).isoformat()
    execution_context = _prepare_outcome_execution_context(repo, args.selection_seal.resolve())
    result = execute_w1_outcomes_from_seal(
        selection_seal_path=args.selection_seal.resolve(),
        price_2024_path=args.price_2024,
        price_2025_path=args.price_2025,
        price_2026_path=args.price_2026,
        current_executable_bundle_identity=execution_context["successor_executable_bundle_identity"],
        expected_selection_seal_id=execution_context["selection_seal_id"],
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    atomic_write_json(output_dir / "STRICT_RAW_OUTCOME_RESULT.json", result)
    atomic_write_text(
        output_dir / "STRICT_SELECTED_OUTCOME_LEDGER.jsonl",
        _jsonl(result["selected_outcome_ledger"]),
    )
    atomic_write_text(
        output_dir / "STRICT_W1_INCLUDE57_RAW_OUTCOME_LEDGER.jsonl",
        _jsonl(result["comparison_outcome_ledger"]),
    )
    finished_at = datetime.now(ZoneInfo("Asia/Seoul")).isoformat()
    run_manifest = {
        "pmo_run_id": result["pmo_run_id"],
        "phase": "MEASURE_OUTCOMES",
        "status": result["outcome_stage_state"],
        "started_at_kst": started_at,
        "finished_at_kst": finished_at,
        "execution_environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "repo": execution_context["repo"],
            "git_head": execution_context["git_head"],
            "git_tree": execution_context["git_tree"],
            "git_branch": execution_context["git_branch"],
        },
        "execution_argv": [sys.executable, "-m", "tools.m3top3.cli_run_real_input_replay", *effective_argv],
        "selection_seal_id": result["selection_seal_id"],
        "selection_seal_verified_before_price_access": True,
        "successor_executable_bundle_identity": execution_context["successor_executable_bundle_identity"],
        "successor_code_components": execution_context["successor_code_components"],
        "predecessor_binding": execution_context["predecessor_binding"],
        "outcome_runtime_receipt": result["price_input_binding"]["parquet_reader_runtime"],
        "price_dataset_identity_sha256": result["price_input_binding"]["dataset_identity_sha256"],
        "outcome_semantic_sha256": result["outcome_semantic_sha256"],
    }
    atomic_write_json(output_dir / "OUTCOME_RUN_MANIFEST.json", run_manifest)
    return {
        "status": result["outcome_stage_state"],
        "pmo_run_id": result["pmo_run_id"],
        "selected_item_raw_measured_count": result["selected_item_raw_measured_count"],
        "comparison_complete_raw_path_count": result["comparison_complete_raw_path_count"],
        "output_dir": str(output_dir),
    }


def main(argv: list[str] | None = None) -> int:
    effective_argv = sys.argv[1:] if argv is None else argv
    args = _parse_args(effective_argv)
    result = _score_and_seal(args, effective_argv) if args.command == "score-and-seal" else _measure_outcomes(args, effective_argv)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
