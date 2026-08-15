from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import sys


def _bootstrap(repo_root: Path) -> None:
    src = repo_root / "aaa" / "src"
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))


def _load_jsonl(path: Path) -> tuple[dict[str, object], ...]:
    rows: list[dict[str, object]] = []
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise RuntimeError(f"DB_EXPORT_ROW_MUST_BE_OBJECT:{line_number}")
        rows.append(value)
    return tuple(rows)


def reconcile(repo_root: Path, db_jsonl: Path) -> dict[str, object]:
    _bootstrap(repo_root)
    from aaa.ops.operational_state import (
        inventory_json_run_registry,
        load_json_run_rows,
        reconcile_run_rows,
    )

    root = repo_root.resolve()
    authoritative = load_json_run_rows(root)
    shadow = _load_jsonl(db_jsonl)
    report = reconcile_run_rows(authoritative, shadow)

    inventory = {item.run_id: item for item in inventory_json_run_registry(root)}
    shadow_by_id: dict[str, dict[str, object]] = {}
    for row in shadow:
        run_id = str(row.get("run_id") or "")
        if not run_id:
            raise RuntimeError("DB_EXPORT_RUN_ID_REQUIRED")
        if run_id in shadow_by_id:
            raise RuntimeError(f"DB_EXPORT_DUPLICATE_RUN_ID:{run_id}")
        shadow_by_id[run_id] = row

    source_identity_mismatches: list[str] = []
    for run_id, identity in sorted(inventory.items()):
        row = shadow_by_id.get(run_id)
        if row is None:
            continue
        if (
            row.get("source_json_path") != identity.path
            or row.get("source_json_sha256") != identity.sha256
            or int(row.get("source_json_byte_size") or -1) != identity.byte_size
        ):
            source_identity_mismatches.append(run_id)

    status = "MATCH" if report.status == "MATCH" and not source_identity_mismatches else "MISMATCH"
    payload = {
        "status": status,
        "run_count_authoritative_json": len(authoritative),
        "run_count_shadow_postgresql": len(shadow),
        "projection": asdict(report),
        "source_identity_mismatches": source_identity_mismatches,
        "inventory": [asdict(inventory[run_id]) for run_id in sorted(inventory)],
    }
    if status != "MATCH":
        raise RuntimeError("T18_JSON_POSTGRES_RECONCILIATION_MISMATCH:" + json.dumps(payload, sort_keys=True))
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Reconcile JSON Run Registry against PostgreSQL JSONL export")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--db-jsonl", required=True)
    args = parser.parse_args(argv)
    payload = reconcile(Path(args.repo_root), Path(args.db_jsonl))
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
