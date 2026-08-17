from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
import re
from typing import Any


_CURRENT_STATE_RE = re.compile(r"SEMI-CURRENT-STATE_v(\d+)\.(\d+)\.yaml$")
_EVENT_LEDGER_RE = re.compile(r"SEMI-CONTROL-EVENT-LEDGER_v(\d+)\.(\d+)\.jsonl$")


@dataclass(frozen=True)
class Comparison:
    key: str
    authoritative: Any
    shadow: Any
    status: str


def _scalar(value: str) -> Any:
    value = value.strip()
    if not value:
        return None
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if lowered in {"null", "none", "~"}:
        return None
    try:
        return int(value)
    except ValueError:
        return value


def flatten_yaml_scalars(text: str) -> dict[str, Any]:
    """Parse deterministic map/scalar YAML paths used by the Control State.

    This intentionally does not implement general YAML. Lists and complex YAML values are
    ignored rather than guessed. Unknown data therefore stays UNKNOWN in comparisons.
    """
    result: dict[str, Any] = {}
    stack: list[tuple[int, str]] = []
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        stripped = raw.strip()
        if stripped.startswith("- ") or ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        while stack and indent <= stack[-1][0]:
            stack.pop()
        path_parts = [item[1] for item in stack] + [key]
        path = ".".join(path_parts)
        if value.strip():
            result[path] = _scalar(value)
        else:
            stack.append((indent, key))
    return result


def _latest_versioned(root: Path, pattern: re.Pattern[str]) -> Path:
    candidates: list[tuple[tuple[int, int], Path]] = []
    for path in root.iterdir():
        match = pattern.fullmatch(path.name)
        if match:
            candidates.append(((int(match.group(1)), int(match.group(2))), path))
    if not candidates:
        raise FileNotFoundError(f"NO_VERSIONED_CONTROL_ASSET: {pattern.pattern}")
    return max(candidates, key=lambda row: row[0])[1]


def _latest_event(path: Path) -> dict[str, Any]:
    last_event: dict[str, Any] | None = None
    seen: set[str] = set()
    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw.strip():
            continue
        record = json.loads(raw)
        event_id = record.get("event_id")
        if event_id is None:
            continue
        event_id = str(event_id)
        if event_id in seen:
            raise RuntimeError(f"DUPLICATE_CONTROL_EVENT: {event_id} line={line_number}")
        seen.add(event_id)
        last_event = record
    if last_event is None:
        raise ValueError(f"NO_CONTROL_EVENT: {path}")
    return last_event


def _cmp(key: str, authoritative: Any, shadow: Any) -> Comparison:
    if authoritative is None or shadow is None:
        status = "UNKNOWN"
    elif authoritative == shadow:
        status = "MATCH"
    else:
        status = "MISMATCH"
    return Comparison(key, authoritative, shadow, status)


def build_discrepancy_report(repo_root: Path) -> dict[str, Any]:
    root = repo_root.resolve()
    continuity = root / "control" / "continuity" / "v1.0"
    state_path = _latest_versioned(continuity, _CURRENT_STATE_RE)
    ledger_path = _latest_versioned(continuity, _EVENT_LEDGER_RE)
    state_bytes = state_path.read_bytes()
    ledger_bytes = ledger_path.read_bytes()
    state = flatten_yaml_scalars(state_bytes.decode("utf-8"))
    event = _latest_event(ledger_path)
    event_state = event.get("state") if isinstance(event.get("state"), dict) else {}

    ledger_relative = str(ledger_path.relative_to(root))
    comparisons = [
        _cmp("event_ledger_head", state.get("continuity.event_ledger_head"), ledger_relative),
        _cmp("validated_target", state.get("model_v1.independent_delta_adjudication.validated_target"), event_state.get("validated_target")),
        _cmp("independent_delta", state.get("model_v1.independent_delta_adjudication.verdict"), event_state.get("independent_delta")),
        _cmp("new_successor_required", state.get("model_v1.independent_delta_adjudication.new_successor_required"), event_state.get("new_successor_required")),
        _cmp("actual_replay_authorized", state.get("actual_replay_readiness.ready"), event_state.get("actual_replay_authorized")),
        _cmp("model_frozen", state.get("scientific_firewall.model_frozen"), event_state.get("model_frozen")),
        _cmp("production_release_authorized", state.get("scientific_firewall.production_release_authorized"), event_state.get("production_release_authorized")),
    ]

    statuses = {row.status for row in comparisons}
    if comparisons[0].status == "MISMATCH":
        overall = "STALE"
    elif "MISMATCH" in statuses:
        overall = "MISMATCH"
    elif "UNKNOWN" in statuses:
        overall = "UNKNOWN"
    else:
        overall = "MATCH"

    report: dict[str, Any] = {
        "status": overall,
        "projection_scope": "CONTROL_ANCHORS_V0_1_NOT_FULL_EVENT_REPLAY",
        "canonical_authority": "EXISTING_SEMI_CONTROL_PLANE",
        "current_state": {
            "path": str(state_path.relative_to(root)),
            "sha256": hashlib.sha256(state_bytes).hexdigest(),
            "byte_size": len(state_bytes),
            "version": state.get("version"),
            "status": state.get("status"),
        },
        "event_ledger": {
            "path": ledger_relative,
            "sha256": hashlib.sha256(ledger_bytes).hexdigest(),
            "byte_size": len(ledger_bytes),
            "latest_event_id": event.get("event_id"),
            "latest_event_timestamp": event.get("timestamp"),
        },
        "comparisons": [asdict(row) for row in comparisons],
    }
    canonical = json.dumps(report, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    report["report_sha256"] = hashlib.sha256(canonical).hexdigest()
    return report
