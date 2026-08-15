from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path


PERSONAS = (
    "SEMI-CONTROL-ARCHITECT",
    "SEMI-MODEL-VALIDATION-DESIGN-ARCHITECT",
    "SEMI-RESEARCH-ORCHESTRATOR",
    "SEMI-VALIDATION-AUDITOR",
)

RUN_STATES = {
    "READY_NOT_DISPATCHED",
    "DISPATCHED_AWAITING_ACK",
    "RUNNING_CONFIRMED",
    "BLOCKED",
    "STALE_UNKNOWN",
    "COMPLETED_PASS",
    "COMPLETED_FAIL",
    "COMPLETED_WITH_FINDINGS",
}
TERMINAL_STATES = {"COMPLETED_PASS", "COMPLETED_FAIL", "COMPLETED_WITH_FINDINGS"}
ACTIVE_STATES = RUN_STATES - TERMINAL_STATES


class InvalidRunRecord(ValueError):
    pass


def _parse_dt(value: str | None) -> datetime | None:
    if value is None:
        return None
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise InvalidRunRecord("TIMESTAMP_MUST_BE_TIMEZONE_AWARE")
    return parsed


def _valid_sha(value: str, length: int) -> bool:
    return len(value) == length and all(ch in "0123456789abcdef" for ch in value)


@dataclass(frozen=True)
class TerminalResult:
    result_id: str
    result_sha256: str
    completed_at: str
    persistent_locator: str
    verdict: str

    @classmethod
    def from_dict(cls, value: dict[str, object]) -> "TerminalResult":
        result = cls(
            result_id=str(value.get("result_id") or ""),
            result_sha256=str(value.get("result_sha256") or ""),
            completed_at=str(value.get("completed_at") or ""),
            persistent_locator=str(value.get("persistent_locator") or ""),
            verdict=str(value.get("verdict") or ""),
        )
        if not result.result_id or not _valid_sha(result.result_sha256, 64):
            raise InvalidRunRecord("INVALID_TERMINAL_RESULT_IDENTITY")
        if result.verdict not in {"PASS", "FAIL", "PASS_WITH_FINDINGS"}:
            raise InvalidRunRecord("INVALID_TERMINAL_VERDICT")
        _parse_dt(result.completed_at)
        if not result.persistent_locator:
            raise InvalidRunRecord("TERMINAL_RESULT_LOCATOR_REQUIRED")
        return result


@dataclass(frozen=True)
class RunRecord:
    run_id: str
    process_id: str
    work_order_id: str
    responsible_persona: str
    executor_role: str
    state: str
    repository: str
    exact_base_commit: str
    branch: str
    started_at: str | None
    last_heartbeat_at: str | None
    stale_after_seconds: int
    canonical_output: bool
    terminal_result: TerminalResult | None
    source_path: str

    @classmethod
    def from_dict(cls, value: dict[str, object], source_path: str) -> "RunRecord":
        terminal_raw = value.get("terminal_result")
        terminal_result = TerminalResult.from_dict(terminal_raw) if isinstance(terminal_raw, dict) else None
        record = cls(
            run_id=str(value.get("run_id") or ""),
            process_id=str(value.get("process_id") or ""),
            work_order_id=str(value.get("work_order_id") or ""),
            responsible_persona=str(value.get("responsible_persona") or ""),
            executor_role=str(value.get("executor_role") or ""),
            state=str(value.get("state") or ""),
            repository=str(value.get("repository") or ""),
            exact_base_commit=str(value.get("exact_base_commit") or ""),
            branch=str(value.get("branch") or ""),
            started_at=value.get("started_at") if isinstance(value.get("started_at"), str) else None,
            last_heartbeat_at=value.get("last_heartbeat_at") if isinstance(value.get("last_heartbeat_at"), str) else None,
            stale_after_seconds=int(value.get("stale_after_seconds") or 0),
            canonical_output=bool(value.get("canonical_output")),
            terminal_result=terminal_result,
            source_path=source_path,
        )
        record.validate()
        return record

    def validate(self) -> None:
        if not all((self.run_id, self.process_id, self.work_order_id, self.executor_role, self.branch)):
            raise InvalidRunRecord("RUN_IDENTITY_FIELDS_REQUIRED")
        if self.responsible_persona not in PERSONAS:
            raise InvalidRunRecord("UNKNOWN_PERSONA")
        if self.state not in RUN_STATES:
            raise InvalidRunRecord("UNKNOWN_RUN_STATE")
        if self.repository != "AofSpds/asset-agent-asa":
            raise InvalidRunRecord("UNEXPECTED_REPOSITORY")
        if not _valid_sha(self.exact_base_commit, 40):
            raise InvalidRunRecord("INVALID_EXACT_BASE_COMMIT")
        if self.stale_after_seconds < 60:
            raise InvalidRunRecord("STALE_WINDOW_TOO_SMALL")
        if self.canonical_output:
            raise InvalidRunRecord("RUN_REGISTRY_MUST_BE_NONCANONICAL")
        started = _parse_dt(self.started_at)
        heartbeat = _parse_dt(self.last_heartbeat_at)
        if self.state == "RUNNING_CONFIRMED" and (started is None or heartbeat is None):
            raise InvalidRunRecord("RUNNING_REQUIRES_START_AND_HEARTBEAT_EVIDENCE")
        if self.state in TERMINAL_STATES and self.terminal_result is None:
            raise InvalidRunRecord("TERMINAL_STATE_REQUIRES_RESULT_ARTIFACT")
        if self.state not in TERMINAL_STATES and self.terminal_result is not None:
            raise InvalidRunRecord("NONTERMINAL_STATE_CANNOT_BIND_TERMINAL_RESULT")

    def effective_state(self, now: datetime | None = None) -> str:
        if self.state != "RUNNING_CONFIRMED":
            return self.state
        heartbeat = _parse_dt(self.last_heartbeat_at)
        if heartbeat is None:
            return "STALE_UNKNOWN"
        reference = now or datetime.now(timezone.utc)
        if reference.tzinfo is None:
            raise InvalidRunRecord("REFERENCE_TIME_MUST_BE_TIMEZONE_AWARE")
        elapsed = (reference.astimezone(timezone.utc) - heartbeat.astimezone(timezone.utc)).total_seconds()
        return "STALE_UNKNOWN" if elapsed > self.stale_after_seconds else "RUNNING_CONFIRMED"

    def to_public_dict(self, now: datetime | None = None) -> dict[str, object]:
        payload = asdict(self)
        payload["effective_state"] = self.effective_state(now)
        return payload


def load_run_registry(repo_root: Path) -> tuple[RunRecord, ...]:
    root = repo_root.resolve()
    registry_dir = root / "control" / "aaa" / "runs"
    if not registry_dir.exists():
        return ()
    records: list[RunRecord] = []
    seen: set[str] = set()
    for path in sorted(registry_dir.glob("*.json")):
        raw = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise InvalidRunRecord(f"RUN_RECORD_MUST_BE_OBJECT:{path}")
        record = RunRecord.from_dict(raw, str(path.relative_to(root)))
        if record.run_id in seen:
            raise InvalidRunRecord(f"DUPLICATE_RUN_ID:{record.run_id}")
        seen.add(record.run_id)
        records.append(record)
    return tuple(records)


def list_runs(repo_root: Path, now: datetime | None = None) -> list[dict[str, object]]:
    return [record.to_public_dict(now) for record in load_run_registry(repo_root)]


def _activity_timestamp(record: RunRecord) -> str:
    if record.terminal_result is not None:
        return record.terminal_result.completed_at
    return record.last_heartbeat_at or record.started_at or ""


def persona_overview(repo_root: Path, now: datetime | None = None) -> list[dict[str, object]]:
    """Return current nonterminal work separately from the latest registered Run.

    A completed Run is historical evidence, not current Persona activity. This prevents
    a Persona with only a terminal Run from appearing to be actively working.
    """
    records = load_run_registry(repo_root)
    rows: list[dict[str, object]] = []
    precedence = {
        "RUNNING_CONFIRMED": 70,
        "BLOCKED": 60,
        "STALE_UNKNOWN": 50,
        "DISPATCHED_AWAITING_ACK": 40,
        "READY_NOT_DISPATCHED": 30,
    }
    for persona in PERSONAS:
        candidates = [record for record in records if record.responsible_persona == persona]
        if not candidates:
            rows.append({
                "persona": persona,
                "state": "IDLE_OR_UNREGISTERED",
                "run_id": None,
                "process_id": None,
                "latest_run_id": None,
                "latest_run_state": None,
            })
            continue

        latest = sorted(candidates, key=lambda record: (_activity_timestamp(record), record.run_id), reverse=True)[0]
        active = [record for record in candidates if record.effective_state(now) in ACTIVE_STATES]
        if not active:
            rows.append({
                "persona": persona,
                "state": "IDLE_OR_UNREGISTERED",
                "run_id": None,
                "process_id": None,
                "latest_run_id": latest.run_id,
                "latest_run_state": latest.effective_state(now),
                "latest_process_id": latest.process_id,
            })
            continue

        selected = sorted(
            active,
            key=lambda record: (
                precedence[record.effective_state(now)],
                _activity_timestamp(record),
                record.run_id,
            ),
            reverse=True,
        )[0]
        rows.append({
            "persona": persona,
            "state": selected.effective_state(now),
            "run_id": selected.run_id,
            "process_id": selected.process_id,
            "work_order_id": selected.work_order_id,
            "last_heartbeat_at": selected.last_heartbeat_at,
            "branch": selected.branch,
            "latest_run_id": latest.run_id,
            "latest_run_state": latest.effective_state(now),
            "latest_process_id": latest.process_id,
        })
    return rows
