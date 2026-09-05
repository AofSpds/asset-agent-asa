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
    PREDECESSOR_EXECUTABLE_BUNDLE_IDENTITY,
    commit_selection_seal,
    create_selection_seal,
    execute_strict_w1_model_stage,
    execute_w1_outcomes_from_seal,
    load_feature_sidecar,
    load_source_manifest,
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


def _bind_successor_bundle(repo: Path) -> tuple[str, list[dict[str, Any]]]:
    components = []
    for relative in SUCCESSOR_COMPONENTS:
        path = repo / relative
        components.append({"path": relative, "byte_size": path.stat().st_size, "sha256": _hash_file(path)})
    return "M3TOP3-REAL-INPUT-EXECUTABLE-BUNDLE-SHA256:" + sha256_hex(components), components


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

    outcome = commands.add_parser("measure-outcomes", help="Verify the durable seal, then open bound price bytes")
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
    code_identity, code_components = _bind_successor_bundle(repo)
    manifest, manifest_content_sha256 = load_source_manifest(args.source_manifest.resolve())
    leaves, sidecar_raw_sha256 = load_feature_sidecar(args.feature_sidecar.resolve())
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

    output_dir.mkdir(parents=True, exist_ok=True)
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


def _measure_outcomes(args: argparse.Namespace, effective_argv: list[str]) -> dict[str, Any]:
    output_dir = args.output_dir.resolve()
    started_at = datetime.now(ZoneInfo("Asia/Seoul")).isoformat()
    result = execute_w1_outcomes_from_seal(
        selection_seal_path=args.selection_seal.resolve(),
        price_2024_path=args.price_2024,
        price_2025_path=args.price_2025,
        price_2026_path=args.price_2026,
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
        "execution_environment": {"python": sys.version, "platform": platform.platform()},
        "execution_argv": [sys.executable, "-m", "tools.m3top3.cli_run_real_input_replay", *effective_argv],
        "selection_seal_id": result["selection_seal_id"],
        "selection_seal_verified_before_price_access": True,
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
