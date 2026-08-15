from __future__ import annotations

from contextlib import contextmanager
from dataclasses import asdict
import json
import os
from pathlib import Path
from typing import Any, Iterator, Mapping

from aaa.core.identity import canonical_json_bytes, sha256_hex
from aaa.agents.runtime import AgentRunRecord, PermissionLevel, RunStatus, WorkOrderIdentity
from aaa.core.identity import ExactBaseIdentity


class JournalIntegrityError(RuntimeError):
    pass


class JournalBusy(RuntimeError):
    pass


def _record_payload(record: AgentRunRecord) -> dict[str, Any]:
    return {
        "run_id": record.run_id,
        "work_order_identity": asdict(record.work_order_identity),
        "exact_base_identity": asdict(record.exact_base_identity),
        "executor_role": record.executor_role,
        "permission_level": int(record.permission_level),
        "status": record.status.value,
        "branch": record.branch,
        "result_sha256": record.result_sha256,
        "terminal_reason": record.terminal_reason,
        "immutable_run_sha256": record.immutable_run_sha256,
    }


def _decode_record(payload: Mapping[str, Any]) -> AgentRunRecord:
    return AgentRunRecord(
        run_id=str(payload["run_id"]),
        work_order_identity=WorkOrderIdentity(**dict(payload["work_order_identity"])),
        exact_base_identity=ExactBaseIdentity(**dict(payload["exact_base_identity"])),
        executor_role=str(payload["executor_role"]),
        permission_level=PermissionLevel(int(payload["permission_level"])),
        status=RunStatus(str(payload["status"])),
        branch=payload.get("branch"),
        result_sha256=payload.get("result_sha256"),
        terminal_reason=payload.get("terminal_reason"),
    )


def _event_hash(event_without_hash: Mapping[str, Any]) -> str:
    return sha256_hex(canonical_json_bytes(dict(event_without_hash)))


@contextmanager
def _exclusive_lock(path: Path) -> Iterator[None]:
    lock_path = path.with_suffix(path.suffix + ".lock")
    try:
        fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise JournalBusy(f"JOURNAL_BUSY: {lock_path}") from exc
    try:
        os.write(fd, str(os.getpid()).encode("ascii"))
        os.fsync(fd)
        os.close(fd)
        yield
    finally:
        try:
            os.close(fd)
        except OSError:
            pass
        lock_path.unlink(missing_ok=True)


class AgentRunJournal:
    """Run-scoped append-only journal. It is never a canonical Control writer."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def read_events(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        events: list[dict[str, Any]] = []
        previous: str | None = None
        immutable_run_sha256: str | None = None
        for line_no, raw in enumerate(self.path.read_text(encoding="utf-8").splitlines(), start=1):
            if not raw.strip():
                continue
            try:
                event = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise JournalIntegrityError(f"INVALID_JOURNAL_JSON:{line_no}") from exc
            if not isinstance(event, dict):
                raise JournalIntegrityError(f"INVALID_JOURNAL_EVENT:{line_no}")
            claimed = event.get("event_sha256")
            material = dict(event)
            material.pop("event_sha256", None)
            actual = _event_hash(material)
            if claimed != actual:
                raise JournalIntegrityError(f"JOURNAL_EVENT_HASH_MISMATCH:{line_no}")
            if material.get("previous_event_sha256") != previous:
                raise JournalIntegrityError(f"JOURNAL_CHAIN_MISMATCH:{line_no}")
            record_payload = material.get("record")
            if not isinstance(record_payload, dict):
                raise JournalIntegrityError(f"MISSING_RECORD:{line_no}")
            current_identity = record_payload.get("immutable_run_sha256")
            if immutable_run_sha256 is None:
                immutable_run_sha256 = current_identity
            elif current_identity != immutable_run_sha256:
                raise JournalIntegrityError(f"RUN_IDENTITY_DRIFT:{line_no}")
            record = _decode_record(record_payload)
            if record.immutable_run_sha256 != current_identity:
                raise JournalIntegrityError(f"RUN_IDENTITY_HASH_MISMATCH:{line_no}")
            previous = claimed
            events.append(event)
        return events

    def latest(self) -> AgentRunRecord | None:
        events = self.read_events()
        if not events:
            return None
        return _decode_record(events[-1]["record"])

    def append(self, record: AgentRunRecord, *, event_type: str) -> dict[str, Any]:
        with _exclusive_lock(self.path):
            events = self.read_events()
            latest = _decode_record(events[-1]["record"]) if events else None
            if latest is not None and latest.immutable_run_sha256 != record.immutable_run_sha256:
                raise JournalIntegrityError("RUN_IDENTITY_DRIFT")
            if latest is not None and latest == record:
                return events[-1]
            if latest is not None and latest.status in {RunStatus.SUCCEEDED, RunStatus.FAILED, RunStatus.BLOCKED, RunStatus.CANCELLED}:
                raise JournalIntegrityError(f"TERMINAL_RUN_IMMUTABLE:{latest.status.value}")
            previous = events[-1]["event_sha256"] if events else None
            event_without_hash = {
                "event_type": event_type,
                "previous_event_sha256": previous,
                "record": _record_payload(record),
            }
            event = dict(event_without_hash)
            event["event_sha256"] = _event_hash(event_without_hash)
            line = json.dumps(event, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
            fd = os.open(self.path, os.O_CREAT | os.O_APPEND | os.O_WRONLY, 0o600)
            try:
                os.write(fd, line.encode("utf-8"))
                os.fsync(fd)
            finally:
                os.close(fd)
            return event
