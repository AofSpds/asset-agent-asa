from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
import re
from typing import Any


_LEDGER_RE = re.compile(r"SEMI-CONTROL-EVENT-LEDGER_v(\d+)\.(\d+)\.jsonl$")


@dataclass(frozen=True)
class LedgerIdentity:
    path: str
    git_blob_sha1: str
    sha256: str
    byte_size: int


def git_blob_sha1(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()  # noqa: S324 - Git object identity, not security


def _identity(path: Path, repo_root: Path) -> LedgerIdentity:
    data = path.read_bytes()
    return LedgerIdentity(
        path=str(path.relative_to(repo_root)),
        git_blob_sha1=git_blob_sha1(data),
        sha256=hashlib.sha256(data).hexdigest(),
        byte_size=len(data),
    )


def _latest_ledger(root: Path) -> Path:
    rows: list[tuple[tuple[int, int], Path]] = []
    for path in root.iterdir():
        match = _LEDGER_RE.fullmatch(path.name)
        if match:
            rows.append(((int(match.group(1)), int(match.group(2))), path))
    if not rows:
        raise FileNotFoundError("NO_CONTROL_EVENT_LEDGER")
    return max(rows, key=lambda row: row[0])[1]


def _records(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw.strip():
            continue
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(f"INVALID_LEDGER_JSON: {path}:{line_number}") from exc
        if not isinstance(parsed, dict):
            raise ValueError(f"INVALID_LEDGER_RECORD: {path}:{line_number}")
        records.append(parsed)
    return records


def load_ledger_lineage(repo_root: Path) -> dict[str, Any]:
    root = repo_root.resolve()
    continuity = root / "control" / "continuity" / "v1.0"
    current = _latest_ledger(continuity)
    newest = current
    visited: set[str] = set()
    chain_newest_first: list[tuple[LedgerIdentity, list[dict[str, Any]]]] = []

    while True:
        relative = str(current.relative_to(root))
        if relative in visited:
            raise RuntimeError(f"LEDGER_LINEAGE_CYCLE: {relative}")
        visited.add(relative)
        records = _records(current)
        identity = _identity(current, root)
        chain_newest_first.append((identity, records))

        continuation = records[0] if records and records[0].get("record_type") == "LEDGER_CONTINUATION" else None
        if continuation is None:
            break
        predecessor_path = continuation.get("predecessor_path")
        predecessor_blob = continuation.get("predecessor_blob_sha")
        if not isinstance(predecessor_path, str) or not predecessor_path:
            raise ValueError(f"MISSING_PREDECESSOR_PATH: {relative}")
        if not isinstance(predecessor_blob, str) or not re.fullmatch(r"[0-9a-f]{40}", predecessor_blob):
            raise ValueError(f"INVALID_PREDECESSOR_BLOB_SHA: {relative}")
        candidate = (root / predecessor_path).resolve()
        try:
            candidate.relative_to(root)
        except ValueError as exc:
            raise ValueError(f"LEDGER_PREDECESSOR_ESCAPES_REPOSITORY: {predecessor_path}") from exc
        if not candidate.is_file():
            raise FileNotFoundError(f"MISSING_LEDGER_PREDECESSOR: {predecessor_path}")
        actual_blob = git_blob_sha1(candidate.read_bytes())
        if actual_blob != predecessor_blob:
            raise RuntimeError(
                f"LEDGER_PREDECESSOR_HASH_MISMATCH: {predecessor_path} expected={predecessor_blob} actual={actual_blob}"
            )
        current = candidate

    chain = list(reversed(chain_newest_first))
    events: list[dict[str, Any]] = []
    seen_event_ids: set[str] = set()
    for _, records in chain:
        for record in records:
            event_id = record.get("event_id")
            if event_id is None:
                continue
            event_id = str(event_id)
            if event_id in seen_event_ids:
                raise RuntimeError(f"DUPLICATE_EVENT_ACROSS_LEDGER_LINEAGE: {event_id}")
            seen_event_ids.add(event_id)
            events.append(record)

    identities = [asdict(identity) for identity, _ in chain]
    report = {
        "status": "PASS",
        "latest_ledger": str(newest.relative_to(root)),
        "ledger_count": len(chain),
        "event_count": len(events),
        "first_event_id": events[0].get("event_id") if events else None,
        "last_event_id": events[-1].get("event_id") if events else None,
        "ledgers": identities,
        "events": events,
    }
    canonical = json.dumps(report, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    report["lineage_sha256"] = hashlib.sha256(canonical).hexdigest()
    return report
