"""Run the validated, create-once F05-R1 score-output stage.

This CLI is intentionally a thin filesystem and Git custody boundary around
``f05_r1_score_outputs``.  It reads every bound byte once, verifies the clean
repository and exact validated target before the scoring callable can run,
then persists the already-rendered in-memory artifacts without overwrite.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path, PurePosixPath
from typing import Any, Mapping, Sequence

from .f05_r1_score_outputs import (
    CLAIM_STATUS,
    EXPECTED_CONFIG_SHA256,
    EXPECTED_F02_INPUT_BATCH_SHA256,
    FIVE_FILENAME,
    RANKING_FILENAME,
    REQUIRED_VALIDATOR_ROLES,
    SCORE_FILENAME,
    F05ScoreArtifacts,
    build_f05_r1_outputs,
    persist_f05_r1_outputs,
)


EXPECTED_F02_INPUT_PATH = (
    "control/m3top3/f02-r1-multi-company-input-repair/v1.0/runs/"
    "AAA-M3TOP3-F02-R1-20260905-171755-CODEX-01/score-and-seal/"
    "STRICT_MODEL_INPUT_BATCH.json"
)
EXPECTED_CONFIG_PATH = "tools/m3top3/configs/m3top3_v1.0.json"
EXPECTED_F05_INPUT_FILENAME = "F05_R1_W1_INPUTS.jsonl"
EXPECTED_REPORT_FILENAME = "F05_R1_AFFECTED_VALIDATION_REPORT.json"

# Every executable dependency that can affect admission, feature computation,
# scoring, ranking, or output bytes must be present in the exact target file
# list.  The two bound input paths are added dynamically below.
REQUIRED_VALIDATED_RUNTIME_PATHS = frozenset(
    {
        "tools/m3top3/__init__.py",
        "tools/m3top3/cli_build_f05_r1_inputs.py",
        "tools/m3top3/cli_score_f05_r1_outputs.py",
        "tools/m3top3/contracts_v1.py",
        "tools/m3top3/core.py",
        "tools/m3top3/coverage_limited_replay_v1.py",
        "tools/m3top3/f05_r1_market.py",
        "tools/m3top3/f05_r1_score_outputs.py",
        "tools/m3top3/features_v1.py",
        "tools/m3top3/features_v1_narrow_patch.py",
        "tools/m3top3/pit_guard.py",
        "tools/m3top3/providers.py",
        "tools/m3top3/real_input_replay_v1.py",
        "tools/m3top3/scorer_v1.py",
        "tools/m3top3/shared_interface_guards_v1.py",
        "tools/m3top3/window_mapping_v11.py",
        EXPECTED_CONFIG_PATH,
        "tools/m3top3/tests/test_cli_score_f05_r1_outputs.py",
        "tools/m3top3/tests/test_f05_r1_market.py",
        "tools/m3top3/tests/test_f05_r1_score_outputs.py",
    }
)


class F05ScoreCLIError(ValueError):
    """A filesystem, Git, hash, or execution-envelope gate failed."""


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _expected_sha256(value: Any, context: str) -> str:
    if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None:
        raise F05ScoreCLIError(f"{context} must be a lowercase 64-hex SHA-256")
    return value


def _strict_json_object(data: bytes, context: str) -> dict[str, Any]:
    def pairs(values):
        result = {}
        for key, value in values:
            if key in result:
                raise F05ScoreCLIError(f"{context} contains duplicate JSON key: {key}")
            result[key] = value
        return result

    def reject_float(value):
        raise F05ScoreCLIError(f"{context} contains an unbound JSON float: {value}")

    def reject_constant(value):
        raise F05ScoreCLIError(f"{context} contains a non-finite number: {value}")

    try:
        parsed = json.loads(
            data.decode("utf-8"),
            object_pairs_hook=pairs,
            parse_float=reject_float,
            parse_constant=reject_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise F05ScoreCLIError(f"{context} is not strict UTF-8 JSON") from exc
    if not isinstance(parsed, dict):
        raise F05ScoreCLIError(f"{context} must be a JSON object")
    return parsed


def _candidate(repo: Path, supplied: str | Path) -> Path:
    path = Path(supplied)
    return path if path.is_absolute() else repo / path


def _assert_no_link_hop(candidate: Path, repo: Path, context: str) -> None:
    cursor = candidate.absolute()
    stop = repo.absolute()
    while True:
        if cursor.exists():
            is_junction = getattr(cursor, "is_junction", lambda: False)()
            if cursor.is_symlink() or is_junction:
                raise F05ScoreCLIError(f"{context} cannot use a symlink or junction")
        if cursor == stop:
            return
        if cursor.parent == cursor:
            raise F05ScoreCLIError(f"{context} escapes the repository")
        cursor = cursor.parent


def _relative(repo: Path, path: Path, context: str) -> str:
    try:
        relative = path.relative_to(repo)
    except ValueError as exc:
        raise F05ScoreCLIError(f"{context} must stay inside the repository") from exc
    if not relative.parts or ".git" in relative.parts:
        raise F05ScoreCLIError(f"{context} cannot target repository metadata")
    return relative.as_posix()


def _read_bound_file(
    repo: Path,
    supplied: str | Path,
    expected_sha256: str,
    context: str,
) -> tuple[Path, str, bytes]:
    candidate = _candidate(repo, supplied)
    _assert_no_link_hop(candidate, repo, context)
    try:
        resolved = candidate.resolve(strict=True)
    except FileNotFoundError as exc:
        raise F05ScoreCLIError(f"{context} does not exist") from exc
    relative = _relative(repo, resolved, context)
    if not resolved.is_file():
        raise F05ScoreCLIError(f"{context} must be a regular file")
    data = resolved.read_bytes()
    expected = _expected_sha256(expected_sha256, f"{context} SHA-256")
    actual = _sha256(data)
    if actual != expected:
        raise F05ScoreCLIError(
            f"{context} SHA-256 mismatch: expected {expected}, got {actual}"
        )
    return resolved, relative, data


def _preflight_output_dir(repo: Path, supplied: str | Path) -> Path:
    candidate = _candidate(repo, supplied)
    if candidate.exists() or candidate.is_symlink():
        raise FileExistsError(f"create-once output directory already exists: {candidate}")
    parent = candidate.parent
    _assert_no_link_hop(parent, repo, "output directory parent")
    try:
        resolved_parent = parent.resolve(strict=True)
    except FileNotFoundError as exc:
        raise F05ScoreCLIError("output directory parent must already exist") from exc
    if not resolved_parent.is_dir():
        raise F05ScoreCLIError("output directory parent must be a directory")
    resolved = resolved_parent / candidate.name
    _relative(repo, resolved, "output directory")
    if resolved.exists():
        raise FileExistsError(f"create-once output directory already exists: {resolved}")
    return resolved


def _git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", *args], cwd=repo, text=True, capture_output=True, check=False
    )
    if check and result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "unknown Git error"
        raise F05ScoreCLIError(f"git {' '.join(args)} failed: {detail}")
    return result


def _assert_clean_worktree(repo: Path) -> None:
    top = _git(repo, "rev-parse", "--show-toplevel").stdout.strip()
    if Path(top).resolve() != repo:
        raise F05ScoreCLIError("--repo must be the exact Git worktree root")
    status = _git(repo, "status", "--porcelain=v1", "--untracked-files=all").stdout
    if status:
        raise F05ScoreCLIError("score execution requires a clean Git worktree")


def _safe_report_path(value: Any, context: str) -> str:
    if not isinstance(value, str) or not value:
        raise F05ScoreCLIError(f"{context} path is missing")
    pure = PurePosixPath(value)
    if (
        pure.is_absolute()
        or "\\" in value
        or ":" in value
        or any(part in {"", ".", ".."} for part in pure.parts)
        or ".git" in pure.parts
    ):
        raise F05ScoreCLIError(f"{context} contains an unsafe repository path")
    return pure.as_posix()


def _verify_head_evidence(repo: Path, paths: Mapping[str, bytes]) -> None:
    for relative, data in paths.items():
        blob = _git(repo, "rev-parse", f"HEAD:{relative}").stdout.strip()
        if re.fullmatch(r"[0-9a-f]{40}", blob) is None:
            raise F05ScoreCLIError(f"HEAD does not contain bound evidence: {relative}")
        # Worktree cleanliness is the first guard; this second read detects a
        # change racing between the clean check and the engine boundary.
        current = (repo / Path(*PurePosixPath(relative).parts)).read_bytes()
        if current != data:
            raise F05ScoreCLIError(f"bound evidence changed during pre-score checks: {relative}")


def _verify_exact_target(
    repo: Path,
    report: Mapping[str, Any],
    required_paths: set[str],
) -> tuple[str, str, str]:
    target_commit = report.get("target_commit")
    target_tree = report.get("target_tree")
    if not isinstance(target_commit, str) or re.fullmatch(r"[0-9a-f]{40}", target_commit) is None:
        raise F05ScoreCLIError("validation target_commit must be lowercase 40-hex")
    if not isinstance(target_tree, str) or re.fullmatch(r"[0-9a-f]{40}", target_tree) is None:
        raise F05ScoreCLIError("validation target_tree must be lowercase 40-hex")
    actual_tree = _git(repo, "rev-parse", f"{target_commit}^{{tree}}").stdout.strip()
    if actual_tree != target_tree:
        raise F05ScoreCLIError("validation target tree does not match target commit")
    head = _git(repo, "rev-parse", "HEAD").stdout.strip()
    if _git(repo, "merge-base", "--is-ancestor", target_commit, head, check=False).returncode != 0:
        raise F05ScoreCLIError("validation target is not an ancestor of current HEAD")

    entries = report.get("validated_target_files")
    if not isinstance(entries, list) or not entries:
        raise F05ScoreCLIError("aggregate validation must bind validated_target_files")
    by_path: dict[str, Mapping[str, Any]] = {}
    for entry in entries:
        if not isinstance(entry, Mapping):
            raise F05ScoreCLIError("validated target file entry must be an object")
        relative = _safe_report_path(entry.get("path"), "validated target file")
        if relative in by_path:
            raise F05ScoreCLIError("validated target file paths must be unique")
        by_path[relative] = entry
    missing = sorted(required_paths - set(by_path))
    if missing:
        raise F05ScoreCLIError(f"validated target file scope is incomplete: {missing}")

    for relative, entry in by_path.items():
        expected_sha = _expected_sha256(entry.get("sha256"), f"{relative} SHA-256")
        expected_blob = entry.get("git_blob")
        if not isinstance(expected_blob, str) or re.fullmatch(r"[0-9a-f]{40}", expected_blob) is None:
            raise F05ScoreCLIError(f"{relative} Git blob must be lowercase 40-hex")
        path = repo / Path(*PurePosixPath(relative).parts)
        _assert_no_link_hop(path, repo, f"validated target file {relative}")
        if not path.is_file() or _sha256(path.read_bytes()) != expected_sha:
            raise F05ScoreCLIError(f"validated target worktree bytes changed: {relative}")
        target_blob = _git(repo, "rev-parse", f"{target_commit}:{relative}").stdout.strip()
        head_blob = _git(repo, "rev-parse", f"HEAD:{relative}").stdout.strip()
        if target_blob != expected_blob or head_blob != expected_blob:
            raise F05ScoreCLIError(f"validated target Git blob changed: {relative}")
    return target_commit, target_tree, head


def execute(args: argparse.Namespace) -> dict[str, Any]:
    try:
        repo = Path(args.repo).resolve(strict=True)
    except FileNotFoundError as exc:
        raise F05ScoreCLIError("repository path does not exist") from exc
    if not repo.is_dir():
        raise F05ScoreCLIError("repository path must be a directory")
    output_dir = _preflight_output_dir(repo, args.output_dir)

    f05_path, f05_relative, f05_bytes = _read_bound_file(
        repo, args.f05_input, args.f05_input_sha256, "F05 input JSONL"
    )
    f02_path, f02_relative, f02_bytes = _read_bound_file(
        repo, args.f02_input, args.f02_input_sha256, "F02 persisted MIS"
    )
    config_path, config_relative, config_bytes = _read_bound_file(
        repo, args.config, args.config_sha256, "model configuration"
    )
    report_path, report_relative, report_bytes = _read_bound_file(
        repo,
        args.aggregate_validation,
        args.aggregate_validation_sha256,
        "aggregate validation report",
    )
    if f05_path.name != EXPECTED_F05_INPUT_FILENAME:
        raise F05ScoreCLIError("F05 input path does not use the approved filename")
    if f02_relative != EXPECTED_F02_INPUT_PATH:
        raise F05ScoreCLIError("F02 input must be the exact persisted F02-R1 MIS path")
    if config_relative != EXPECTED_CONFIG_PATH:
        raise F05ScoreCLIError("configuration must be the exact preserved model config path")
    if report_path.name != EXPECTED_REPORT_FILENAME:
        raise F05ScoreCLIError("aggregate validation report filename is not approved")
    if args.f02_input_sha256 != EXPECTED_F02_INPUT_BATCH_SHA256:
        raise F05ScoreCLIError("F02 input SHA-256 is not the frozen persisted binding")
    if args.config_sha256 != EXPECTED_CONFIG_SHA256:
        raise F05ScoreCLIError("configuration SHA-256 is not the frozen model binding")

    run_root = report_path.parent
    if f05_path.parent != run_root or output_dir.parent != run_root:
        raise F05ScoreCLIError("F05 input, validation report, and output must share one run root")
    report = _strict_json_object(report_bytes, "aggregate validation report")
    if report.get("run_id") != args.run_id:
        raise F05ScoreCLIError("aggregate validation run_id mismatch")

    receipt_bytes: dict[str, bytes] = {}
    receipt_evidence: dict[str, bytes] = {}
    resolved_inputs = {f05_path, f02_path, config_path, report_path}
    for role in REQUIRED_VALIDATOR_ROLES:
        prefix = role.lower()
        path_value = getattr(args, f"{prefix}_receipt")
        sha_value = getattr(args, f"{prefix}_receipt_sha256")
        receipt_path, relative, raw = _read_bound_file(
            repo, path_value, sha_value, f"{role} validation receipt"
        )
        if receipt_path in resolved_inputs:
            raise F05ScoreCLIError("bound input and validation receipt paths must be distinct")
        resolved_inputs.add(receipt_path)
        try:
            receipt_path.relative_to(run_root / "validation")
        except ValueError as exc:
            raise F05ScoreCLIError(
                f"{role} validation receipt must be inside the run validation directory"
            ) from exc
        receipt = _strict_json_object(raw, f"{role} validation receipt")
        if receipt.get("run_id") != args.run_id:
            raise F05ScoreCLIError(f"{role} validation receipt run_id mismatch")
        receipt_bytes[role] = raw
        receipt_evidence[relative] = raw

    _assert_clean_worktree(repo)
    required_paths = set(REQUIRED_VALIDATED_RUNTIME_PATHS)
    required_paths.update({f05_relative, f02_relative, config_relative})
    target_commit, target_tree, head = _verify_exact_target(repo, report, required_paths)
    _verify_head_evidence(
        repo,
        {
            f05_relative: f05_bytes,
            f02_relative: f02_bytes,
            config_relative: config_bytes,
            report_relative: report_bytes,
            **receipt_evidence,
        },
    )
    if output_dir.exists():
        raise FileExistsError(f"create-once output directory already exists: {output_dir}")

    artifacts = build_f05_r1_outputs(
        f05_input_jsonl=f05_bytes,
        f02_input_batch_json=f02_bytes,
        config_json=config_bytes,
        aggregate_validation_json=report_bytes,
        validation_receipt_json_by_role=receipt_bytes,
    )
    if not isinstance(artifacts, F05ScoreArtifacts):
        raise F05ScoreCLIError("score helper returned an invalid artifact bundle")
    if artifacts.target_commit != target_commit or artifacts.target_tree != target_tree:
        raise F05ScoreCLIError("score helper target readback differs from the Git gate")

    # No output was written by the pure helper. Recheck custody immediately
    # before the single create-once persistence call.
    if output_dir.exists():
        raise FileExistsError(f"create-once output directory already exists: {output_dir}")
    _assert_clean_worktree(repo)
    for path, original, context in (
        (f05_path, f05_bytes, "F05 input JSONL"),
        (f02_path, f02_bytes, "F02 persisted MIS"),
        (config_path, config_bytes, "model configuration"),
        (report_path, report_bytes, "aggregate validation report"),
    ):
        if path.read_bytes() != original:
            raise F05ScoreCLIError(f"{context} changed before persistence")
    hashes = persist_f05_r1_outputs(artifacts, output_dir)

    expected_names = {SCORE_FILENAME, RANKING_FILENAME, FIVE_FILENAME}
    if set(hashes) != expected_names:
        raise F05ScoreCLIError("score helper persisted an unexpected artifact set")
    payloads = {
        SCORE_FILENAME: artifacts.score_jsonl,
        RANKING_FILENAME: artifacts.provisional_ranking_csv,
        FIVE_FILENAME: artifacts.f02_f05_exact_five_csv,
    }
    output_entries = {path.name for path in output_dir.iterdir() if path.is_file()}
    if output_entries != expected_names:
        raise F05ScoreCLIError("create-once output directory contains unexpected files")
    artifact_receipts = {}
    for name, payload in payloads.items():
        persisted = (output_dir / name).read_bytes()
        if persisted != payload or hashes[name] != _sha256(payload):
            raise F05ScoreCLIError(f"persisted output readback mismatch: {name}")
        artifact_receipts[name] = {"bytes": len(payload), "sha256": hashes[name]}

    return {
        "schema_version": "AAA-M3TOP3-F05-R1-SCORE-OUTPUT-CLI-RECEIPT-v1.0",
        "status": "COMPLETE_F05_R1_W1_PROVISIONAL_OUTPUT_BYTES_CREATED_ONCE",
        "run_id": args.run_id,
        "claim_status": CLAIM_STATUS,
        "target_commit": target_commit,
        "target_tree": target_tree,
        "execution_head": head,
        "merged_input_hash": artifacts.merged_input_hash,
        "engine_run_id": artifacts.engine_run_id,
        "score_engine_call_count": 1,
        "input_bindings": {
            "f05_input_jsonl_sha256": _sha256(f05_bytes),
            "f02_model_input_batch_sha256": _sha256(f02_bytes),
            "config_sha256": _sha256(config_bytes),
            "aggregate_validation_sha256": _sha256(report_bytes),
        },
        "output_dir": output_dir.relative_to(repo).as_posix(),
        "artifacts": artifact_receipts,
        "official_top3_or_top10": False,
        "outcome_execution": False,
    }


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--repo", type=Path, required=True)
    result.add_argument("--run-id", required=True)
    result.add_argument("--f05-input", type=Path, required=True)
    result.add_argument("--f05-input-sha256", required=True)
    result.add_argument("--f02-input", type=Path, required=True)
    result.add_argument("--f02-input-sha256", required=True)
    result.add_argument("--config", type=Path, required=True)
    result.add_argument("--config-sha256", required=True)
    result.add_argument("--aggregate-validation", type=Path, required=True)
    result.add_argument("--aggregate-validation-sha256", required=True)
    for role in REQUIRED_VALIDATOR_ROLES:
        flag = role.lower()
        result.add_argument(f"--{flag}-receipt", type=Path, required=True)
        result.add_argument(f"--{flag}-receipt-sha256", required=True)
    result.add_argument("--output-dir", type=Path, required=True)
    return result


def _canonical_json_line(value: Any) -> str:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    ) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    receipt = execute(args)
    print(_canonical_json_line(receipt), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
