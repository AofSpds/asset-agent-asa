#!/usr/bin/env python3
"""Execute the exact R-WP4-03 75-case production-path matrix.

This worker is intentionally self-contained until the external freeze manifest
has been admitted.  Only then does it import the candidate's matrix adapters.
Every report row contains the code, exit, scorer-call, and governed-write
observations captured from the production action itself.

IVA participation: NONE.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import sys
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "r-wp4-03-production-matrix-report-v1"
MANIFEST_SCHEMA = "r-wp4-03-freeze-manifest-v1"
TREE_ALGORITHM = "sha256-canonical-json-relative-path-size-sha256-v1"
TREE_SCOPE = "tools/m3top3"
ACCEPTED_RUNTIME_COMMIT = "4fffdfb03fdd4ae6bf6656d2034abd3ef701ae4f"
EVIDENCE_PARENT_COMMIT = "495c070be37f978c8be536c0b469d2d07cf0c071"
EXCLUDED_PARTS = {"__pycache__", ".pytest_cache", ".mypy_cache"}


class WorkerError(RuntimeError):
    pass


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(char in "0123456789abcdef" for char in value)


def is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def tree_records(source_root: Path) -> list[dict[str, Any]]:
    base = source_root / TREE_SCOPE
    if not base.is_dir():
        raise WorkerError(f"source scope is missing: {base}")
    forbidden = [
        path for path in base.rglob("*")
        if path.is_symlink() or path.suffix in {".pyc", ".pyo"} or any(part in EXCLUDED_PARTS for part in path.parts)
    ]
    if forbidden:
        raise WorkerError(f"source scope contains excluded/generated or symlink entries: {forbidden[0]}")
    records: list[dict[str, Any]] = []
    for path in sorted(base.rglob("*")):
        if not path.is_file():
            continue
        records.append({
            "relative_path":path.relative_to(source_root).as_posix(),
            "size":path.stat().st_size,
            "sha256":sha256_file(path),
        })
    if not records:
        raise WorkerError("source scope is empty")
    return records


def verify_source_manifest(source_root: Path, manifest_path: Path) -> dict[str, Any]:
    if is_within(manifest_path, source_root):
        raise WorkerError("source manifest must be outside the candidate source root")
    try:
        raw = manifest_path.read_bytes()
        manifest = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise WorkerError(f"source manifest is unreadable: {type(exc).__name__}") from exc
    if not isinstance(manifest, dict) or raw != canonical_json_bytes(manifest) + b"\n":
        raise WorkerError("source manifest must be one canonical newline-terminated JSON object")
    required_header = {
        "schema_version":MANIFEST_SCHEMA,
        "accepted_runtime_commit":ACCEPTED_RUNTIME_COMMIT,
        "evidence_parent_commit":EVIDENCE_PARENT_COMMIT,
        "source_tree_scope":TREE_SCOPE,
        "source_tree_algorithm":TREE_ALGORITHM,
        "pyc_excluded":True,
        "iva_participation":"NONE",
    }
    mismatch = {key:(required,manifest.get(key)) for key,required in required_header.items() if manifest.get(key) != required}
    if mismatch:
        raise WorkerError(f"source manifest governance mismatch: {mismatch}")
    if Path(str(manifest.get("candidate_root", ""))).resolve() != source_root:
        raise WorkerError("source manifest candidate_root differs from --source-root")
    declared = manifest.get("files")
    if not isinstance(declared, list):
        raise WorkerError("source manifest files must be a complete list")
    previous = ""
    for row in declared:
        if not isinstance(row, dict) or set(row) != {"relative_path", "size", "sha256"}:
            raise WorkerError("source manifest file row schema is not exact")
        relative = row.get("relative_path")
        candidate = Path(relative) if isinstance(relative, str) else Path("..")
        if (
            not isinstance(relative, str) or not relative.startswith(TREE_SCOPE + "/")
            or candidate.is_absolute() or ".." in candidate.parts or relative <= previous
            or not isinstance(row.get("size"), int) or isinstance(row.get("size"), bool) or row["size"] < 0
            or not is_sha256(row.get("sha256"))
        ):
            raise WorkerError("source manifest file identity is unsafe, malformed, duplicate, or unsorted")
        previous = relative
    live = tree_records(source_root)
    if declared != live:
        raise WorkerError("live source records differ from the exact source manifest")
    tree_sha = sha256_bytes(canonical_json_bytes(live))
    if manifest.get("source_tree_sha256") != tree_sha:
        raise WorkerError("source_tree_sha256 differs from the complete live inventory")
    return {
        "manifest_sha256":sha256_bytes(raw),
        "source_tree_sha256":tree_sha,
        "file_count":len(live),
    }


def run_matrix(source_root: Path, binding: dict[str, Any]) -> dict[str, Any]:
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(source_root))
    module = importlib.import_module("tools.m3top3.tests.test_r_wp4_03_matrix")
    module_path = Path(module.__file__).resolve()
    if not is_within(module_path, source_root):
        raise WorkerError(f"matrix module origin is outside the exact candidate: {module_path}")
    matrix = getattr(module, "MATRIX", None)
    case_type = getattr(module, "RWP403MatrixTests", None)
    if not isinstance(matrix, dict) or len(matrix) != 75 or case_type is None:
        raise WorkerError("production matrix registry is not exactly 75 unique cases")
    cases: list[dict[str, Any]] = []
    for case_id in matrix:
        case = case_type(methodName="runTest")
        observation: dict[str, Any] = {}
        try:
            case.setUp()
            observation = case.execute_case_observation(case_id)
        except Exception as exc:  # This is transport evidence, never a relabelled stable code.
            expected_code, exit_text = matrix[case_id]
            observation = {
                "case_id":case_id,
                "expected":{"code":expected_code,"exit_code":0 if exit_text=="0_OR_3" else int(exit_text),"scorer_calls":None,"no_write":None},
                "actual":{"code":type(exc).__name__,"exit_code":1,"scorer_calls":None,"no_write":None},
                "production_path":True,
                "production_surface":"matrix adapter transport",
                "fabricated_code":False,
                "caught_and_relabelled":False,
                "synthetic_summary_only":False,
                "raw_exception":f"{type(exc).__name__}: {exc}",
                "verdict":"FAIL",
            }
        finally:
            try:
                case.tearDown()
            except Exception as exc:
                observation["raw_exception"] = observation.get("raw_exception") or f"tearDown {type(exc).__name__}: {exc}"
                observation["verdict"] = "FAIL"
        cases.append(observation)
    failures=sum(item.get("verdict")!="PASS" for item in cases)
    raw_exceptions=sum(item.get("raw_exception") is not None for item in cases)
    return {
        "schema_version":SCHEMA_VERSION,
        "status":"PASS" if not failures and not raw_exceptions else "FAIL",
        "iva_participation":"NONE",
        "exact_source_manifest_sha256":binding["manifest_sha256"],
        "source_manifest_sha256":binding["manifest_sha256"],
        "source_tree_sha256":binding["source_tree_sha256"],
        "freeze_binding_start":{"manifest_sha256":binding["manifest_sha256"],"source_tree_sha256":binding["source_tree_sha256"]},
        "freeze_binding_end":{"manifest_sha256":binding["manifest_sha256"],"source_tree_sha256":binding["source_tree_sha256"]},
        "source_file_count":binding["file_count"],
        "cases":cases,
        "summary":{
            "requested":75,
            "passed":75-failures,
            "skips":0,
            "failures":failures,
            "errors":raw_exceptions,
            "raw_exceptions":raw_exceptions,
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", required=True)
    parser.add_argument("--source-manifest", required=True)
    parser.add_argument("--report", required=True)
    args = parser.parse_args(argv)
    source_root = Path(args.source_root).resolve()
    manifest_path = Path(args.source_manifest).resolve()
    report_path = Path(args.report).resolve()
    if is_within(report_path, source_root):
        print(json.dumps({"code":"REPORT_PATH_INSIDE_SOURCE_ROOT","status":"FAIL"},sort_keys=True))
        return 3
    try:
        start = verify_source_manifest(source_root, manifest_path)
        report = run_matrix(source_root, start)
        end = verify_source_manifest(source_root, manifest_path)
        if end != start:
            raise WorkerError("source binding moved during production matrix execution")
        report["freeze_binding_end"]={"manifest_sha256":end["manifest_sha256"],"source_tree_sha256":end["source_tree_sha256"]}
    except WorkerError as exc:
        report={
            "schema_version":SCHEMA_VERSION,
            "status":"FAIL",
            "iva_participation":"NONE",
            "code":"PRODUCTION_MATRIX_BINDING_FAILURE",
            "error":str(exc),
            "cases":[],
            "summary":{"requested":75,"passed":0,"skips":0,"failures":1,"errors":1,"raw_exceptions":1},
        }
    report_path.parent.mkdir(parents=True,exist_ok=True)
    report_path.write_bytes(canonical_json_bytes(report)+b"\n")
    print(json.dumps({"status":report["status"],"report":str(report_path),"case_count":len(report.get("cases",[]))},sort_keys=True))
    return 0 if report["status"]=="PASS" else 3


if __name__ == "__main__":
    raise SystemExit(main())
