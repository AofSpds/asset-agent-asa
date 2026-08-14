from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterable

from .core import parse_datetime

FORBIDDEN_MODEL_INPUT_FIELDS = {
    "future_return", "return", "close_return", "three_month_return", "3m_return",
    "mfe", "mfe_return", "mae", "mae_return", "future_high", "future_close",
    "future_low", "future_rank", "winner", "winner_label", "official_winner",
    "realized_winner", "risk_event_future", "outcome_validity", "validation_id",
}


@dataclass(frozen=True)
class GuardViolation:
    code: str
    message: str
    field: str | None = None


class PITLeakageError(ValueError):
    def __init__(self, violations: list[GuardViolation]):
        self.violations = violations
        super().__init__("; ".join(f"{v.code}: {v.message}" for v in violations))


class PITGuard:
    """Architecture v1.0 leakage guard.

    Authoritative evidence eligibility is publication_at <= snapshot_cutoff_at.
    The guard recursively rejects future/outcome labels from model inputs.
    """

    def validate_publication(self, publication_at: str | datetime | None, cutoff_at: str | datetime) -> list[GuardViolation]:
        if publication_at is None:
            return []
        p = parse_datetime(publication_at)
        c = parse_datetime(cutoff_at)
        if p > c:
            return [GuardViolation("PIT_PUBLICATION_AFTER_CUTOFF", f"publication_at {p.isoformat()} > cutoff {c.isoformat()}", "publication_at")]
        return []

    def _walk(self, value: Any, path: str = ""):
        if isinstance(value, dict):
            for k, v in value.items():
                p = f"{path}.{k}" if path else str(k)
                yield str(k), v, p
                yield from self._walk(v, p)
        elif isinstance(value, list):
            for i, v in enumerate(value):
                yield from self._walk(v, f"{path}[{i}]")

    def validate_model_input(self, record: dict[str, Any], cutoff_at: str | datetime) -> list[GuardViolation]:
        violations: list[GuardViolation] = []
        cutoff = parse_datetime(cutoff_at)
        for key, value, path in self._walk(record):
            lk = key.lower()
            if lk in FORBIDDEN_MODEL_INPUT_FIELDS:
                violations.append(GuardViolation("FUTURE_FIELD_IN_MODEL_INPUT", f"forbidden model-input field {path!r}", path))
            if lk in {"publication_at", "feature_publication_at"} and value is not None:
                try:
                    if parse_datetime(value) > cutoff:
                        violations.append(GuardViolation("PIT_PUBLICATION_AFTER_CUTOFF", f"{path} is after snapshot cutoff", path))
                except (ValueError, TypeError):
                    violations.append(GuardViolation("INVALID_PUBLICATION_DATETIME", f"invalid timezone-aware publication datetime at {path}", path))
            if lk == "corporate_action_observed_at" and value is not None and parse_datetime(value) > cutoff:
                violations.append(GuardViolation("POST_SNAPSHOT_CA_KNOWLEDGE", "corporate-action knowledge was observed after the snapshot cutoff", path))
            if lk == "current_only" and value is True:
                violations.append(GuardViolation("CURRENT_ONLY_FIELD_IN_HISTORY", "current-only record cannot be used in historical PIT input", path))
        return violations

    def assert_model_inputs(self, records: Iterable[dict[str, Any]], cutoff_at: str | datetime) -> None:
        violations: list[GuardViolation] = []
        for r in records:
            violations.extend(self.validate_model_input(r, cutoff_at))
        if violations:
            raise PITLeakageError(violations)
