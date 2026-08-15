from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Iterable, Mapping, Protocol, Sequence


RUN_COMPARISON_FIELDS = (
    "run_id",
    "process_id",
    "work_order_id",
    "responsible_persona",
    "executor_role",
    "state",
    "repository",
    "exact_base_commit",
    "branch",
    "started_at",
    "last_heartbeat_at",
    "stale_after_seconds",
    "canonical_output",
)


class ShadowReconciliationError(RuntimeError):
    pass


@dataclass(frozen=True)
class RunFileIdentity:
    path: str
    byte_size: int
    sha256: str
    run_id: str


@dataclass(frozen=True)
class ReconciliationReport:
    status: str
    compared_run_ids: tuple[str, ...]
    missing_in_shadow: tuple[str, ...]
    extra_in_shadow: tuple[str, ...]
    mismatched_run_ids: tuple[str, ...]


class OperationalStateReader(Protocol):
    def list_runs(self) -> Sequence[Mapping[str, object]]:
        ...


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def inventory_json_run_registry(repo_root: Path) -> tuple[RunFileIdentity, ...]:
    root = repo_root.resolve()
    registry = root / "control" / "aaa" / "runs"
    if not registry.exists():
        return ()

    identities: list[RunFileIdentity] = []
    seen: set[str] = set()
    for path in sorted(registry.glob("*.json")):
        payload = path.read_bytes()
        raw = json.loads(payload.decode("utf-8"))
        if not isinstance(raw, dict):
            raise ShadowReconciliationError(f"RUN_RECORD_MUST_BE_OBJECT:{path.name}")
        run_id = str(raw.get("run_id") or "")
        if not run_id:
            raise ShadowReconciliationError(f"RUN_ID_REQUIRED:{path.name}")
        if run_id in seen:
            raise ShadowReconciliationError(f"DUPLICATE_RUN_ID:{run_id}")
        seen.add(run_id)
        identities.append(
            RunFileIdentity(
                path=str(path.relative_to(root)),
                byte_size=len(payload),
                sha256=sha256_bytes(payload),
                run_id=run_id,
            )
        )
    return tuple(identities)


def load_json_run_rows(repo_root: Path) -> tuple[dict[str, object], ...]:
    root = repo_root.resolve()
    rows: list[dict[str, object]] = []
    for identity in inventory_json_run_registry(root):
        raw = json.loads((root / identity.path).read_text(encoding="utf-8"))
        row = dict(raw)
        row["_source_path"] = identity.path
        row["_source_byte_size"] = identity.byte_size
        row["_source_sha256"] = identity.sha256
        rows.append(row)
    return tuple(rows)


def _normalize_timestamp(value: object) -> object:
    if value is None or not isinstance(value, str):
        return value
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return value
    if parsed.tzinfo is None:
        raise ShadowReconciliationError("TIMESTAMP_MUST_BE_TIMEZONE_AWARE_FOR_RECONCILIATION")
    return parsed.astimezone(timezone.utc).isoformat()


def _normalize_run(row: Mapping[str, object]) -> dict[str, object]:
    normalized = {field: row.get(field) for field in RUN_COMPARISON_FIELDS}
    if normalized["exact_base_commit"] is None:
        normalized["exact_base_commit"] = row.get("exact_target_commit")
    if normalized["branch"] is None:
        normalized["branch"] = row.get("branch_context")
    normalized["started_at"] = _normalize_timestamp(normalized["started_at"])
    normalized["last_heartbeat_at"] = _normalize_timestamp(normalized["last_heartbeat_at"])
    return normalized


def _index_rows(rows: Iterable[Mapping[str, object]], label: str) -> dict[str, dict[str, object]]:
    indexed: dict[str, dict[str, object]] = {}
    for row in rows:
        run_id = str(row.get("run_id") or "")
        if not run_id:
            raise ShadowReconciliationError(f"RUN_ID_REQUIRED_FOR_RECONCILIATION:{label}")
        if run_id in indexed:
            raise ShadowReconciliationError(f"DUPLICATE_RUN_ID_FOR_RECONCILIATION:{label}:{run_id}")
        indexed[run_id] = _normalize_run(row)
    return indexed


def reconcile_run_rows(
    authoritative_json_rows: Iterable[Mapping[str, object]],
    shadow_db_rows: Iterable[Mapping[str, object]],
) -> ReconciliationReport:
    authority = _index_rows(authoritative_json_rows, "AUTHORITY")
    shadow = _index_rows(shadow_db_rows, "SHADOW")

    authority_ids = set(authority)
    shadow_ids = set(shadow)
    shared = sorted(authority_ids & shadow_ids)
    mismatched = tuple(run_id for run_id in shared if authority[run_id] != shadow[run_id])
    missing = tuple(sorted(authority_ids - shadow_ids))
    extra = tuple(sorted(shadow_ids - authority_ids))
    status = "MATCH" if not (mismatched or missing or extra) else "MISMATCH"
    return ReconciliationReport(
        status=status,
        compared_run_ids=tuple(shared),
        missing_in_shadow=missing,
        extra_in_shadow=extra,
        mismatched_run_ids=mismatched,
    )


class JsonRunRegistryReader:
    def __init__(self, repo_root: Path):
        self._repo_root = repo_root

    def list_runs(self) -> Sequence[Mapping[str, object]]:
        return load_json_run_rows(self._repo_root)


class ShadowOperationalStateReader:
    """Fail-closed read shadow.

    JSON remains authoritative during T18 migration shadow. The database reader is
    observed only for reconciliation. A mismatch raises and never selects a winner.
    """

    def __init__(self, authoritative: OperationalStateReader, shadow: OperationalStateReader):
        self._authoritative = authoritative
        self._shadow = shadow

    def list_runs(self) -> Sequence[Mapping[str, object]]:
        authority_rows = tuple(self._authoritative.list_runs())
        shadow_rows = tuple(self._shadow.list_runs())
        report = reconcile_run_rows(authority_rows, shadow_rows)
        if report.status != "MATCH":
            raise ShadowReconciliationError(
                "SHADOW_RUN_REGISTRY_MISMATCH:"
                f"missing={report.missing_in_shadow}:"
                f"extra={report.extra_in_shadow}:"
                f"mismatched={report.mismatched_run_ids}"
            )
        return authority_rows
