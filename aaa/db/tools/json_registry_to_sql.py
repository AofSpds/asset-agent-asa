from __future__ import annotations

from dataclasses import asdict
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys


REPOSITORY = "AofSpds/asset-agent-asa"
_HEX40 = re.compile(r"^[0-9a-f]{40}$")


def _bootstrap(repo_root: Path) -> None:
    src = repo_root / "aaa" / "src"
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))


def _q(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def _sql_text(value: str | None) -> str:
    return "NULL" if value is None else _q(value)


def _sql_timestamp(value: str | None) -> str:
    return "NULL" if value is None else f"{_q(value)}::timestamptz"


def _sql_bool(value: bool) -> str:
    return "true" if value else "false"


def _sql_json(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return f"{_q(payload)}::jsonb"


def _yaml_scalar(path: Path, key: str) -> str | None:
    prefix = f"{key}:"
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        if raw_line.startswith((" ", "\t")):
            continue
        if not raw_line.startswith(prefix):
            continue
        value = raw_line[len(prefix):].strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        return value or None
    return None


def _work_order_identity(repo_root: Path, work_order_id: str, git_commit: str) -> dict[str, object]:
    registry = repo_root / "control" / "workorders"
    matches: list[Path] = []
    for path in sorted(registry.iterdir()):
        if not path.is_file() or path.suffix.lower() not in {".yaml", ".yml", ".json"}:
            continue
        if path.suffix.lower() == ".json":
            raw = json.loads(path.read_text(encoding="utf-8"))
            observed = str(raw.get("work_order_id") or "") if isinstance(raw, dict) else ""
        else:
            observed = _yaml_scalar(path, "work_order_id") or ""
        if observed == work_order_id:
            matches.append(path)
    if len(matches) != 1:
        raise RuntimeError(f"WORK_ORDER_ID_NOT_UNIQUE_OR_MISSING:{work_order_id}:{len(matches)}")
    path = matches[0]
    payload = path.read_bytes()
    return {
        "work_order_id": work_order_id,
        "git_repository": REPOSITORY,
        "git_path": str(path.relative_to(repo_root)),
        "git_commit_or_blob_identity": git_commit,
        "content_sha256": hashlib.sha256(payload).hexdigest(),
    }


def emit_import_sql(repo_root: Path, git_commit: str) -> str:
    if not _HEX40.fullmatch(git_commit):
        raise ValueError("GIT_COMMIT_MUST_BE_40_HEX")
    _bootstrap(repo_root)
    from aaa.ops.operational_state import inventory_json_run_registry
    from aaa.ops.run_registry import load_run_registry

    root = repo_root.resolve()
    records = load_run_registry(root)
    identities = {item.run_id: item for item in inventory_json_run_registry(root)}
    if set(identities) != {record.run_id for record in records}:
        raise RuntimeError("RUN_REGISTRY_INVENTORY_IDENTITY_SET_MISMATCH")

    work_order_ids = sorted({record.work_order_id for record in records})
    work_orders = [_work_order_identity(root, work_order_id, git_commit) for work_order_id in work_order_ids]

    lines = ["\\set ON_ERROR_STOP on", "BEGIN;"]
    for work_order in work_orders:
        lines.append(
            "INSERT INTO aaa_ops.work_order_refs "
            "(work_order_id, git_repository, git_path, git_commit_or_blob_identity, content_sha256) VALUES ("
            f"{_q(str(work_order['work_order_id']))},"
            f"{_q(str(work_order['git_repository']))},"
            f"{_q(str(work_order['git_path']))},"
            f"{_q(str(work_order['git_commit_or_blob_identity']))},"
            f"{_q(str(work_order['content_sha256']))}"
            ");"
        )

    for record in records:
        identity = identities[record.run_id]
        terminal_id = record.terminal_result.result_id if record.terminal_result is not None else None
        lines.append(
            "INSERT INTO aaa_ops.runs ("
            "run_id,process_id,work_order_id,responsible_persona,executor_role,repository,"
            "exact_target_commit,branch_context,state,started_at,last_heartbeat_at,stale_after_seconds,"
            "terminal_result_id,canonical_output,source_json_path,source_json_sha256,source_json_byte_size"
            ") VALUES ("
            f"{_q(record.run_id)},{_q(record.process_id)},{_q(record.work_order_id)},"
            f"{_q(record.responsible_persona)},{_q(record.executor_role)},{_q(record.repository)},"
            f"{_q(record.exact_base_commit)},{_q(record.branch)},{_q(record.state)},"
            f"{_sql_timestamp(record.started_at)},{_sql_timestamp(record.last_heartbeat_at)},"
            f"{record.stale_after_seconds},{_sql_text(terminal_id)},{_sql_bool(record.canonical_output)},"
            f"{_q(identity.path)},{_q(identity.sha256)},{identity.byte_size}"
            ");"
        )

    for record in records:
        terminal = record.terminal_result
        if terminal is None:
            continue
        result_path = (root / terminal.persistent_locator).resolve()
        try:
            result_path.relative_to(root / "control" / "aaa" / "results")
        except ValueError as exc:
            raise RuntimeError(f"RESULT_LOCATOR_OUTSIDE_GOVERNED_ROOT:{record.run_id}") from exc
        result_bytes = result_path.read_bytes()
        observed_hash = hashlib.sha256(result_bytes).hexdigest()
        if observed_hash != terminal.result_sha256:
            raise RuntimeError(f"RESULT_SHA256_MISMATCH:{record.run_id}")
        metadata = {
            "migration_source": "JSON_RUN_REGISTRY",
            "source_run_json_path": identities[record.run_id].path,
            "persistent_locator_preserved": terminal.persistent_locator,
        }
        lines.append(
            "INSERT INTO aaa_ops.results ("
            "result_id,run_id,work_order_id,verdict,artifact_locator,artifact_sha256,artifact_byte_size,"
            "repository,exact_target_commit,completed_at_db,metadata_jsonb"
            ") VALUES ("
            f"{_q(terminal.result_id)},{_q(record.run_id)},{_q(record.work_order_id)},"
            f"{_q(terminal.verdict)},{_q(terminal.persistent_locator)},{_q(terminal.result_sha256)},"
            f"{len(result_bytes)},{_q(record.repository)},{_q(record.exact_base_commit)},"
            f"{_sql_timestamp(terminal.completed_at)},{_sql_json(metadata)}"
            ");"
        )

    lines.extend([
        "COMMIT;",
        "SELECT count(*) AS imported_run_count FROM aaa_ops.runs;",
    ])
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Emit deterministic SQL for the current JSON Run Registry")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--git-commit", required=True)
    args = parser.parse_args(argv)
    sys.stdout.write(emit_import_sql(Path(args.repo_root), args.git_commit))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
