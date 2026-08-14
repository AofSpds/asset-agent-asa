#!/usr/bin/env python3
"""Evidence-gated corporate-action interface contract for future D4 execution."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Iterable, Mapping, Sequence

REQUIRED_EVENT_FIELDS = (
    "event_id", "security_code", "company_id", "event_date", "event_type",
    "publication_at", "effective_at", "comparable_price_impact",
    "adjustment_required", "adjustment_factor_if_supported", "evidence_refs",
    "validation_status",
)


@dataclass(frozen=True)
class CAValidationResult:
    valid: bool
    errors: tuple[str, ...]


def _date_part(value) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    text = str(value)
    if len(text) >= 10:
        try:
            return date.fromisoformat(text[:10]).isoformat()
        except ValueError:
            return None
    return None


def validate_ca_event(event: Mapping[str, object]) -> CAValidationResult:
    errors: list[str] = []
    for field in REQUIRED_EVENT_FIELDS:
        if field not in event:
            errors.append(f"missing required CA field: {field}")

    code = event.get("security_code")
    if code is not None and (not isinstance(code, str) or len(code) != 6):
        errors.append("security_code must be a 6-character string")

    evidence = event.get("evidence_refs")
    if evidence is None:
        evidence_list: list[object] = []
    elif isinstance(evidence, (list, tuple)):
        evidence_list = list(evidence)
    else:
        errors.append("evidence_refs must be a list/tuple when populated")
        evidence_list = []

    adjustment_required = bool(event.get("adjustment_required", False))
    factor = event.get("adjustment_factor_if_supported")
    event_type = event.get("event_type")
    comparable_impact = event.get("comparable_price_impact")

    if factor is not None and not evidence_list:
        errors.append("PRI-C04/PRI-A04: adjustment_factor requires evidence_refs")
    if adjustment_required and not evidence_list:
        errors.append("PRICE-Q012: adjustment_required requires evidence_refs")
    if (event_type not in (None, "") or comparable_impact not in (None, "")) and not evidence_list:
        errors.append("PRI-C08/PRI-A06: CA fields require evidence_refs")
    if _date_part(event.get("effective_at")) is None:
        errors.append("effective_at must contain an evidenced calendar date")
    if _date_part(event.get("event_date")) is None:
        errors.append("event_date must contain an evidenced calendar date")
    if not str(event.get("validation_status", "")):
        errors.append("validation_status must be non-empty")

    return CAValidationResult(not errors, tuple(errors))


def validate_ca_events(events: Sequence[Mapping[str, object]]) -> CAValidationResult:
    errors: list[str] = []
    seen_ids: set[str] = set()
    for index, event in enumerate(events):
        result = validate_ca_event(event)
        errors.extend(f"event[{index}] {msg}" for msg in result.errors)
        event_id = event.get("event_id")
        if isinstance(event_id, str):
            if event_id in seen_ids:
                errors.append(f"event[{index}] duplicate event_id={event_id}")
            seen_ids.add(event_id)
    return CAValidationResult(not errors, tuple(errors))


def candidate_events_for_price_row(price_date: str, security_code: str,
                                   events: Iterable[Mapping[str, object]]) -> list[Mapping[str, object]]:
    """Match exact effective date, or an explicit evidence-provided effective interval."""
    out: list[Mapping[str, object]] = []
    for event in events:
        if event.get("security_code") != security_code:
            continue
        start = _date_part(event.get("effective_at"))
        if start is None:
            continue
        explicit_end = _date_part(event.get("effective_until"))
        if explicit_end is None:
            if price_date == start:
                out.append(event)
        elif start <= price_date <= explicit_end:
            out.append(event)
    return sorted(out, key=lambda item: str(item.get("event_id", "")))


def canonical_ca_projection(event: Mapping[str, object]) -> dict[str, object]:
    """Project a validated CA event; evidence-reference resolution remains a D4 gate."""
    result = validate_ca_event(event)
    if not result.valid:
        raise ValueError("; ".join(result.errors))
    refs = list(event.get("evidence_refs") or [])
    factor = event.get("adjustment_factor_if_supported")
    event_type = event.get("event_type")
    flag = bool(event_type not in (None, "") or factor is not None or event.get("adjustment_required"))
    if event_type not in (None, "") and not flag:
        raise ValueError("PRI-C09 violation")
    return {
        "corporate_action_flag": flag,
        "corporate_action_type": event_type if event_type not in (None, "") else None,
        "adjustment_factor": factor,
        "action_evidence_refs": refs or None,
    }
