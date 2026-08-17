from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
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
TERMINAL_VERDICT_BY_STATE = {
    "COMPLETED_PASS": "PASS",
    "COMPLETED_FAIL": "FAIL",
    "COMPLETED_WITH_FINDINGS": "PASS_WITH_FINDINGS",
}


class InvalidRunRecord(ValueError):
    pass


def _parse_dt(value: str | None) -> datetime | None:
    if value is None:
        return None
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise InvalidRunRecord("TIMESTAMP_MUST_BE_TIMEZONE_AWARE")
    return parsed


def _utc(value: str | None) -> datetime | None:
    parsed = _parse_dt(value)
    return parsed.astimezone(timezone.utc) if parsed is not None else None


def _valid_sha(value: str, length: int) -> bool:
    return len(value) == length and all(ch in "0123456789abcdef" for ch in value)


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _resolve_governed_path(repo_root: Path, locator: str, allowed_root: Path, error: str) -> Path:
    if not locator or Path(locator).is_absolute():
        raise InvalidRunRecord(error)
    root = repo_root.resolve()
    candidate = (root / locator).resolve()
    allowed = allowed_root.resolve()
    try:
        candidate.relative_to(allowed)
    except ValueError as exc:
        raise InvalidRunRecord(error) from exc
    if not candidate.is_file():
        raise InvalidRunRecord(error)
    return candidate


def _yaml_scalar_identity(path: Path, key: str) -> str | None:
    prefix = f"{key}:"
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        if raw_line.startswith((" ", "\t")):
            continue
        line = raw_line.strip()
        if not line.startswith(prefix):
            continue
        value = line[len(prefix):].strip()
        if not value:
            return None
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        return value
    return None


def _load_work_order_identity(repo_root: Path, work_order_id: str) -> Path:
    workorders = repo_root.resolve() / "control" / "workorders"
    if not workorders.is_dir():
        raise InvalidRunRecord(f"WORK_ORDER_REGISTRY_MISSING:{work_order_id}")
    matches: list[Path] = []
    for path in sorted(workorders.iterdir()):
        if not path.is_file() or path.suffix.lower() not in {".yaml", ".yml", ".json"}:
            continue
        try:
            if path.suffix.lower() == ".json":
                raw = json.loads(path.read_text(encoding="utf-8"))
                observed = str(raw.get("work_order_id") or "") if isinstance(raw, dict) else ""
            else:
                observed = _yaml_scalar_identity(path, "work_order_id") or ""
        except (OSError, json.JSONDecodeError) as exc:
            raise InvalidRunRecord(f"INVALID_WORK_ORDER_ARTIFACT:{path.name}") from exc
        if observed == work_order_id:
            matches.append(path)
    if not matches:
        raise InvalidRunRecord(f"WORK_ORDER_NOT_FOUND:{work_order_id}")
    if len(matches) != 1:
        raise InvalidRunRecord(f"WORK_ORDER_ID_NOT_UNIQUE:{work_order_id}")
    return matches[0]


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
        if started is not None and heartbeat is not None:
            if heartbeat.astimezone(timezone.utc) < started.astimezone(timezone.utc):
                raise InvalidRunRecord("HEARTBEAT_PRECEDES_START")
        if self.state == "RUNNING_CONFIRMED" and (started is None or heartbeat is None):
            raise InvalidRunRecord("RUNNING_REQUIRES_START_AND_HEARTBEAT_EVIDENCE")
        if self.state in TERMINAL_STATES and self.terminal_result is None:
            raise InvalidRunRecord("TERMINAL_STATE_REQUIRES_RESULT_ARTIFACT")
        if self.state not in TERMINAL_STATES and self.terminal_result is not None:
            raise InvalidRunRecord("NONTERMINAL_STATE_CANNOT_BIND_TERMINAL_RESULT")
        if self.state in TERMINAL_STATES and self.terminal_result is not None:
            expected = TERMINAL_VERDICT_BY_STATE[self.state]
            if self.terminal_result.verdict != expected:
                raise InvalidRunRecord("TERMINAL_STATE_VERDICT_MISMATCH")

    def effective_state(self, now: datetime | None = None) -> str:
        if self.state != "RUNNING_CONFIRMED":
            return self.state
        started = _parse_dt(self.started_at)
        heartbeat = _parse_dt(self.last_heartbeat_at)
        if started is None or heartbeat is None:
            return "STALE_UNKNOWN"
        reference = now or datetime.now(timezone.utc)
        if reference.tzinfo is None:
            raise InvalidRunRecord("REFERENCE_TIME_MUST_BE_TIMEZONE_AWARE")
        reference_utc = reference.astimezone(timezone.utc)
        started_utc = started.astimezone(timezone.utc)
        heartbeat_utc = heartbeat.astimezone(timezone.utc)
        if started_utc > reference_utc or heartbeat_utc > reference_utc:
            return "STALE_UNKNOWN"
        elapsed = (reference_utc - heartbeat_utc).total_seconds()
        return "STALE_UNKNOWN" if elapsed > self.stale_after_seconds else "RUNNING_CONFIRMED"

    def to_public_dict(self, now: datetime | None = None) -> dict[str, object]:
        payload = asdict(self)
        payload["effective_state"] = self.effective_state(now)
        return payload


def _verify_terminal_result_artifact(repo_root: Path, record: RunRecord) -> None:
    terminal = record.terminal_result
    if terminal is None:
        return
    result_root = repo_root.resolve() / "control" / "aaa" / "results"
    path = _resolve_governed_path(
        repo_root,
        terminal.persistent_locator,
        result_root,
        f"TERMINAL_RESULT_LOCATOR_INVALID:{record.run_id}",
    )
    payload_bytes = path.read_bytes()
    if _sha256_bytes(payload_bytes) != terminal.result_sha256:
        raise InvalidRunRecord(f"TERMINAL_RESULT_SHA256_MISMATCH:{record.run_id}")
    try:
        raw = json.loads(payload_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise InvalidRunRecord(f"TERMINAL_RESULT_INVALID_JSON:{record.run_id}") from exc
    if not isinstance(raw, dict):
        raise InvalidRunRecord(f"TERMINAL_RESULT_MUST_BE_OBJECT:{record.run_id}")

    observed_result_id = str(raw.get("result_id") or "")
    observed_run_id = str(raw.get("run_id") or raw.get("validation_run_id") or "")
    observed_work_order_id = str(raw.get("work_order_id") or "")
    observed_verdict = str(raw.get("verdict") or raw.get("independent_verdict") or "")
    observed_repository = str(raw.get("repository") or "")
    observed_target = str(
        raw.get("exact_base_commit")
        or raw.get("exact_validation_target")
        or raw.get("exact_target_commit")
        or ""
    )

    if observed_result_id != terminal.result_id:
        raise InvalidRunRecord(f"TERMINAL_RESULT_ID_MISMATCH:{record.run_id}")
    if observed_run_id != record.run_id:
        raise InvalidRunRecord(f"TERMINAL_RESULT_RUN_ID_MISMATCH:{record.run_id}")
    if observed_work_order_id != record.work_order_id:
        raise InvalidRunRecord(f"TERMINAL_RESULT_WORK_ORDER_ID_MISMATCH:{record.run_id}")
    if observed_verdict != terminal.verdict:
        raise InvalidRunRecord(f"TERMINAL_RESULT_VERDICT_MISMATCH:{record.run_id}")
    if observed_repository and observed_repository != record.repository:
        raise InvalidRunRecord(f"TERMINAL_RESULT_REPOSITORY_MISMATCH:{record.run_id}")
    if observed_target != record.exact_base_commit:
        raise InvalidRunRecord(f"TERMINAL_RESULT_TARGET_MISMATCH:{record.run_id}")


def _verify_referential_integrity(repo_root: Path, record: RunRecord) -> None:
    _load_work_order_identity(repo_root, record.work_order_id)
    _verify_terminal_result_artifact(repo_root, record)


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
        _verify_referential_integrity(root, record)
        seen.add(record.run_id)
        records.append(record)
    return tuple(records)


def list_runs(repo_root: Path, now: datetime | None = None) -> list[dict[str, object]]:
    return [record.to_public_dict(now) for record in load_run_registry(repo_root)]


def _activity_timestamp(record: RunRecord) -> datetime:
    value = record.terminal_result.completed_at if record.terminal_result is not None else (
        record.last_heartbeat_at or record.started_at
    )
    parsed = _utc(value)
    return parsed if parsed is not None else datetime.min.replace(tzinfo=timezone.utc)


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
