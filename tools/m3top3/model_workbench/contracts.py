from __future__ import annotations

import math
import re
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from enum import Enum
from typing import Any, Mapping, Protocol, Sequence

from tools.m3top3.core import parse_datetime
from tools.m3top3.pit_guard import PITGuard, PITLeakageError


WORKBENCH_SCHEMA_VERSION = "model-workbench-envelope-v0.1"
FIXTURE_CLASS = "SYNTHETIC_NON_OUTCOME"
PROVENANCE_CLASS = "HAND_AUTHORED_SYNTHETIC_DEV_ONLY"
GENERATOR_RULE_ID = "M3TOP3-SYNTHETIC-CANDIDATES-v0.1"
FIXTURE_PURPOSE = (
    "Contract, separation, missingness, ordering, and accounting tests only"
)

LOCAL_FORBIDDEN_OUTCOME_FIELDS = frozenset(
    {
        "outcome",
        "outcome_label",
        "target",
        "target_label",
        "forward_return",
        "realized_return",
        "realized_rank",
        "selection_winner",
        "top3_winner",
    }
)

_ENVELOPE_KEYS = frozenset(
    {
        "workbench_schema_version",
        "fixture_class",
        "official_outcome_data",
        "snapshot_cutoff_at",
        "fixture_provenance",
        "set_policy",
        "candidates",
    }
)
_PROVENANCE_KEYS = frozenset(
    {
        "provenance_class",
        "contains_real_market_data",
        "contains_official_w1_w8_data",
        "contains_outcome_labels",
        "source_refs",
        "generator_rule_id",
        "purpose",
    }
)
_POLICY_KEYS = frozenset(
    {
        "policy_id",
        "set_size",
        "eligibility_required",
        "allowed_confidence_states",
        "allowed_risk_states",
        "opportunity_state_required_for_raw_rank",
    }
)
_CANDIDATE_REQUIRED_KEYS = frozenset(
    {
        "candidate_id",
        "company_id",
        "security_code",
        "pit_snapshot_id",
        "eligibility",
        "opportunity",
        "confidence",
        "risk",
    }
)
_CANDIDATE_KEYS = _CANDIDATE_REQUIRED_KEYS | {"metadata"}
_ELIGIBILITY_KEYS = frozenset({"state", "reason_codes"})
_AXIS_REQUIRED_KEYS = frozenset(
    {"evidence_state", "value", "publication_at", "evidence_refs"}
)
_AXIS_KEYS = _AXIS_REQUIRED_KEYS | {"reason_codes"}
_CANONICAL_DECIMAL = re.compile(r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]*[1-9])?\Z")


def utf8_key(value: str) -> bytes:
    return value.encode("utf-8")


class EvidenceState(str, Enum):
    VERIFIED = "VERIFIED"
    UNKNOWN = "UNKNOWN"
    NOT_FOUND = "NOT_FOUND"
    PARTIAL = "PARTIAL"
    CONFLICT = "CONFLICT"
    STALE = "STALE"


class EligibilityState(str, Enum):
    TRUE = "TRUE"
    FALSE = "FALSE"
    UNKNOWN = "UNKNOWN"


class RecallDisposition(str, Enum):
    RECALLED_IDENTITY_PRESERVED = "RECALLED_IDENTITY_PRESERVED"


class RankabilityDisposition(str, Enum):
    RANKED = "RANKED"
    UNRANKED = "UNRANKED"


class SetDisposition(str, Enum):
    SELECTED = "SELECTED"
    SKIPPED = "SKIPPED"
    NOT_SCANNED_CAPACITY_REACHED = "NOT_SCANNED_CAPACITY_REACHED"
    UNRANKED = "UNRANKED"


class SetDecisionAction(str, Enum):
    SELECTED = "SELECTED"
    SKIPPED = "SKIPPED"
    SUBSTITUTED = "SUBSTITUTED"
    UNFILLED = "UNFILLED"


@dataclass(frozen=True)
class ContractViolation:
    path: str
    code: str
    message: str

    def sort_key(self) -> tuple[bytes, bytes, bytes]:
        return (
            self.path.encode("utf-8"),
            self.code.encode("utf-8"),
            self.message.encode("utf-8"),
        )

    def as_dict(self) -> dict[str, str]:
        return {"path": self.path, "code": self.code, "message": self.message}


class WorkbenchContractError(ValueError):
    """One fail-closed error carrying all deterministic contract violations."""

    def __init__(self, violations: Sequence[ContractViolation]):
        unique = {
            (violation.path, violation.code, violation.message): violation
            for violation in violations
        }
        self.violations = tuple(
            sorted(unique.values(), key=ContractViolation.sort_key)
        )
        message = "; ".join(
            f"{v.path} {v.code}: {v.message}" for v in self.violations
        )
        super().__init__(message)

    def as_dict(self) -> dict[str, Any]:
        return {
            "error": "WORKBENCH_CONTRACT_ERROR",
            "violations": [violation.as_dict() for violation in self.violations],
        }


class WorkbenchInvariantError(RuntimeError):
    pass


@dataclass(frozen=True)
class AxisInput:
    evidence_state: EvidenceState
    value: Decimal | None
    publication_at: datetime
    evidence_refs: tuple[str, ...]
    reason_codes: tuple[str, ...]


@dataclass(frozen=True)
class EligibilityInput:
    state: EligibilityState
    reason_codes: tuple[str, ...]


@dataclass(frozen=True)
class CandidateInput:
    candidate_id: str
    company_id: str
    security_code: str
    pit_snapshot_id: str
    eligibility: EligibilityInput
    opportunity: AxisInput
    confidence: AxisInput
    risk: AxisInput
    metadata: Mapping[str, Any] | None


@dataclass(frozen=True)
class FixtureProvenance:
    provenance_class: str
    contains_real_market_data: bool
    contains_official_w1_w8_data: bool
    contains_outcome_labels: bool
    source_refs: tuple[str, ...]
    generator_rule_id: str
    purpose: str


@dataclass(frozen=True)
class SetPolicy:
    policy_id: str
    set_size: int
    eligibility_required: EligibilityState
    allowed_confidence_states: tuple[EvidenceState, ...]
    allowed_risk_states: tuple[EvidenceState, ...]
    opportunity_state_required_for_raw_rank: EvidenceState


@dataclass(frozen=True)
class WorkbenchEnvelope:
    workbench_schema_version: str
    fixture_class: str
    official_outcome_data: bool
    snapshot_cutoff_at: datetime
    fixture_provenance: FixtureProvenance
    set_policy: SetPolicy
    candidates: tuple[CandidateInput, ...]
    normalized_input: Mapping[str, Any]


@dataclass(frozen=True)
class RecalledCandidate:
    candidate: CandidateInput
    disposition: RecallDisposition


@dataclass(frozen=True)
class RankedCandidate:
    recalled: RecalledCandidate
    raw_rank: int
    raw_score: Decimal
    tie_group: str
    tie_break_key: tuple[str, str, str]


@dataclass(frozen=True)
class AssessedCandidate:
    ranked: RankedCandidate
    confidence: AxisInput
    risk: AxisInput


@dataclass(frozen=True)
class SetConstructionResult:
    selected_set: tuple[Mapping[str, Any], ...]
    decision_log: tuple[Mapping[str, Any], ...]
    dispositions: Mapping[str, Mapping[str, Any]]


class CandidateRecallStage(Protocol):
    def recall(
        self, candidates: Sequence[CandidateInput]
    ) -> tuple[RecalledCandidate, ...]: ...


class TailRankingStage(Protocol):
    def rank(
        self, recalled: Sequence[RecalledCandidate], policy: SetPolicy
    ) -> tuple[
        tuple[RankedCandidate, ...], Mapping[str, tuple[str, ...]]
    ]: ...


class ConfidenceRiskAssessmentStage(Protocol):
    def assess(
        self, ranked: Sequence[RankedCandidate]
    ) -> tuple[AssessedCandidate, ...]: ...


class SetConstructionStage(Protocol):
    def construct(
        self, assessed: Sequence[AssessedCandidate], policy: SetPolicy
    ) -> SetConstructionResult: ...


def _add(
    violations: list[ContractViolation], path: str, code: str, message: str
) -> None:
    violations.append(ContractViolation(path, code, message))


def _check_keys(
    value: Any,
    *,
    path: str,
    allowed: frozenset[str],
    required: frozenset[str],
    violations: list[ContractViolation],
) -> bool:
    if not isinstance(value, Mapping):
        _add(violations, path, "EXPECTED_MAPPING", "value must be a mapping")
        return False
    actual = set(value.keys())
    for key in actual:
        if not isinstance(key, str):
            _add(
                violations,
                path,
                "NON_STRING_KEY",
                "all mapping keys must be strings",
            )
    string_keys = {key for key in actual if isinstance(key, str)}
    for key in sorted(string_keys - allowed, key=utf8_key):
        _add(
            violations,
            f"{path}.{key}",
            "UNKNOWN_KEY",
            "key is not allowed by the positive shape contract",
        )
    for key in sorted(required - string_keys, key=utf8_key):
        _add(
            violations,
            f"{path}.{key}",
            "MISSING_REQUIRED_KEY",
            "required key is absent",
        )
    return True


def _require_nonempty_string(
    value: Any, path: str, violations: list[ContractViolation]
) -> None:
    if not isinstance(value, str) or not value.strip():
        _add(
            violations,
            path,
            "EXPECTED_NONEMPTY_STRING",
            "value must be a nonempty string",
        )


def _validate_unique_string_list(
    value: Any,
    path: str,
    violations: list[ContractViolation],
    *,
    require_nonempty: bool = False,
) -> None:
    if not isinstance(value, list):
        _add(violations, path, "EXPECTED_LIST", "value must be a list")
        return
    if require_nonempty and not value:
        _add(violations, path, "EMPTY_LIST", "list must not be empty")
    valid_strings: list[str] = []
    for index, item in enumerate(value):
        item_path = f"{path}[{index}]"
        if not isinstance(item, str) or not item.strip():
            _add(
                violations,
                item_path,
                "EXPECTED_NONEMPTY_STRING",
                "list item must be a nonempty string",
            )
        else:
            valid_strings.append(item)
    if len(set(valid_strings)) != len(valid_strings):
        _add(violations, path, "DUPLICATE_LIST_ITEM", "list items must be unique")


def _validate_json_value(
    value: Any, path: str, violations: list[ContractViolation]
) -> None:
    if value is None or isinstance(value, (str, bool, int)):
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            _add(
                violations,
                path,
                "NONFINITE_JSON_NUMBER",
                "JSON number must be finite",
            )
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            _validate_json_value(item, f"{path}[{index}]", violations)
        return
    if isinstance(value, Mapping):
        for key, item in value.items():
            if not isinstance(key, str):
                _add(
                    violations,
                    path,
                    "NON_STRING_KEY",
                    "metadata mapping keys must be strings",
                )
                continue
            _validate_json_value(item, f"{path}.{key}", violations)
        return
    _add(
        violations,
        path,
        "NON_JSON_VALUE",
        "metadata must contain only JSON-compatible values",
    )


def _walk_fields(value: Any, path: str = "$"):
    if isinstance(value, Mapping):
        for key, item in value.items():
            if not isinstance(key, str):
                continue
            item_path = f"{path}.{key}"
            yield key, item, item_path
            yield from _walk_fields(item, item_path)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from _walk_fields(item, f"{path}[{index}]")


def _validate_local_outcome_firewall(
    envelope: Any, violations: list[ContractViolation]
) -> None:
    for key, _value, path in _walk_fields(envelope):
        if key.lower() in LOCAL_FORBIDDEN_OUTCOME_FIELDS:
            _add(
                violations,
                path,
                "OUTCOME_FIELD_FORBIDDEN",
                f"forbidden outcome field {key!r}",
            )


def _validate_datetime(
    value: Any, path: str, violations: list[ContractViolation]
) -> datetime | None:
    if not isinstance(value, str):
        _add(
            violations,
            path,
            "EXPECTED_ISO_DATETIME_STRING",
            "value must be a timezone-aware ISO-8601 string",
        )
        return None
    try:
        parsed = parse_datetime(value)
    except (TypeError, ValueError):
        _add(
            violations,
            path,
            "INVALID_TIMEZONE_AWARE_DATETIME",
            "value must be a valid timezone-aware ISO-8601 datetime",
        )
        return None
    return parsed


def _validate_axis(
    value: Any,
    path: str,
    cutoff: datetime | None,
    violations: list[ContractViolation],
) -> None:
    if not _check_keys(
        value,
        path=path,
        allowed=_AXIS_KEYS,
        required=_AXIS_REQUIRED_KEYS,
        violations=violations,
    ):
        return

    state_raw = value.get("evidence_state")
    try:
        state = EvidenceState(state_raw)
    except (TypeError, ValueError):
        state = None
        _add(
            violations,
            f"{path}.evidence_state",
            "INVALID_EVIDENCE_STATE",
            "state must be VERIFIED, UNKNOWN, NOT_FOUND, PARTIAL, CONFLICT, or STALE",
        )

    raw_decimal = value.get("value")
    parsed_decimal: Decimal | None = None
    if raw_decimal is not None:
        if not isinstance(raw_decimal, str) or not _CANONICAL_DECIMAL.fullmatch(
            raw_decimal
        ):
            _add(
                violations,
                f"{path}.value",
                "NONCANONICAL_DECIMAL",
                "non-null value must be a canonical finite decimal string",
            )
        else:
            try:
                parsed_decimal = Decimal(raw_decimal)
            except InvalidOperation:
                parsed_decimal = None
            if parsed_decimal is None or not parsed_decimal.is_finite():
                _add(
                    violations,
                    f"{path}.value",
                    "NONFINITE_DECIMAL",
                    "decimal value must be finite",
                )
            elif parsed_decimal.is_zero() and raw_decimal.startswith("-"):
                _add(
                    violations,
                    f"{path}.value",
                    "NONCANONICAL_DECIMAL",
                    "negative zero is not canonical",
                )

    if state is EvidenceState.VERIFIED and raw_decimal is None:
        _add(
            violations,
            f"{path}.value",
            "VERIFIED_VALUE_REQUIRED",
            "VERIFIED evidence requires a non-null decimal value",
        )
    if state in {
        EvidenceState.UNKNOWN,
        EvidenceState.NOT_FOUND,
        EvidenceState.CONFLICT,
    } and raw_decimal is not None:
        _add(
            violations,
            f"{path}.value",
            "STATE_REQUIRES_NULL_VALUE",
            f"{state.value} evidence requires a null value",
        )

    publication = _validate_datetime(
        value.get("publication_at"), f"{path}.publication_at", violations
    )
    if publication is not None and cutoff is not None and publication > cutoff:
        _add(
            violations,
            f"{path}.publication_at",
            "PIT_PUBLICATION_AFTER_CUTOFF",
            "publication_at is after snapshot_cutoff_at",
        )

    _validate_unique_string_list(
        value.get("evidence_refs"), f"{path}.evidence_refs", violations
    )
    if "reason_codes" in value:
        _validate_unique_string_list(
            value.get("reason_codes"), f"{path}.reason_codes", violations
        )


def _validate_eligibility(
    value: Any, path: str, violations: list[ContractViolation]
) -> None:
    if not _check_keys(
        value,
        path=path,
        allowed=_ELIGIBILITY_KEYS,
        required=_ELIGIBILITY_KEYS,
        violations=violations,
    ):
        return
    state_raw = value.get("state")
    try:
        state = EligibilityState(state_raw)
    except (TypeError, ValueError):
        state = None
        _add(
            violations,
            f"{path}.state",
            "INVALID_ELIGIBILITY_STATE",
            "state must be TRUE, FALSE, or UNKNOWN",
        )
    _validate_unique_string_list(
        value.get("reason_codes"),
        f"{path}.reason_codes",
        violations,
        require_nonempty=state in {EligibilityState.FALSE, EligibilityState.UNKNOWN},
    )


def _validate_provenance(
    value: Any, path: str, violations: list[ContractViolation]
) -> None:
    if not _check_keys(
        value,
        path=path,
        allowed=_PROVENANCE_KEYS,
        required=_PROVENANCE_KEYS,
        violations=violations,
    ):
        return
    exact_values = {
        "provenance_class": PROVENANCE_CLASS,
        "contains_real_market_data": False,
        "contains_official_w1_w8_data": False,
        "contains_outcome_labels": False,
        "generator_rule_id": GENERATOR_RULE_ID,
        "purpose": FIXTURE_PURPOSE,
    }
    for key, expected in exact_values.items():
        if value.get(key) != expected or (
            isinstance(expected, bool) and value.get(key) is not expected
        ):
            _add(
                violations,
                f"{path}.{key}",
                "FIXTURE_PROVENANCE_MISMATCH",
                f"value must equal {expected!r}",
            )
    _validate_unique_string_list(
        value.get("source_refs"), f"{path}.source_refs", violations
    )
    if value.get("source_refs") != []:
        _add(
            violations,
            f"{path}.source_refs",
            "NONEMPTY_SOURCE_REFS",
            "synthetic fixture source_refs must be an empty list",
        )


def _validate_policy(
    value: Any, path: str, violations: list[ContractViolation]
) -> None:
    if not _check_keys(
        value,
        path=path,
        allowed=_POLICY_KEYS,
        required=_POLICY_KEYS,
        violations=violations,
    ):
        return
    _require_nonempty_string(value.get("policy_id"), f"{path}.policy_id", violations)
    set_size = value.get("set_size")
    if isinstance(set_size, bool) or not isinstance(set_size, int) or set_size <= 0:
        _add(
            violations,
            f"{path}.set_size",
            "INVALID_SET_SIZE",
            "set_size must be an integer greater than zero",
        )
    exact_scalars = {
        "eligibility_required": "TRUE",
        "opportunity_state_required_for_raw_rank": "VERIFIED",
    }
    for key, expected in exact_scalars.items():
        if value.get(key) != expected:
            _add(
                violations,
                f"{path}.{key}",
                "FROZEN_POLICY_MISMATCH",
                f"value must equal {expected!r}",
            )
    for key in ("allowed_confidence_states", "allowed_risk_states"):
        raw_list = value.get(key)
        _validate_unique_string_list(raw_list, f"{path}.{key}", violations)
        if raw_list != ["VERIFIED"]:
            _add(
                violations,
                f"{path}.{key}",
                "FROZEN_POLICY_MISMATCH",
                "v0.1 allowlist must contain exactly VERIFIED",
            )


def _validate_candidate(
    value: Any,
    index: int,
    cutoff: datetime | None,
    violations: list[ContractViolation],
) -> None:
    path = f"$.candidates[{index}]"
    if not _check_keys(
        value,
        path=path,
        allowed=_CANDIDATE_KEYS,
        required=_CANDIDATE_REQUIRED_KEYS,
        violations=violations,
    ):
        return
    for key in ("candidate_id", "company_id", "security_code", "pit_snapshot_id"):
        _require_nonempty_string(value.get(key), f"{path}.{key}", violations)
    _validate_eligibility(value.get("eligibility"), f"{path}.eligibility", violations)
    for axis in ("opportunity", "confidence", "risk"):
        _validate_axis(value.get(axis), f"{path}.{axis}", cutoff, violations)
    if "metadata" in value:
        metadata = value.get("metadata")
        if not isinstance(metadata, Mapping):
            _add(
                violations,
                f"{path}.metadata",
                "EXPECTED_MAPPING",
                "metadata must be a mapping when present",
            )
        else:
            _validate_json_value(metadata, f"{path}.metadata", violations)


def _prefix_pit_path(candidate_index: int, field: str | None) -> str:
    base = f"$.candidates[{candidate_index}]"
    if not field:
        return base
    if field.startswith("["):
        return f"{base}{field}"
    return f"{base}.{field}"


def _run_existing_pit_guard(
    candidates: Any,
    cutoff_raw: Any,
    violations: list[ContractViolation],
    guard: PITGuard,
) -> None:
    if not isinstance(candidates, list) or not isinstance(cutoff_raw, str):
        return
    try:
        parse_datetime(cutoff_raw)
    except (TypeError, ValueError):
        return
    for index, candidate in enumerate(candidates):
        if not isinstance(candidate, Mapping):
            continue
        try:
            guard.assert_model_inputs([dict(candidate)], cutoff_raw)
        except PITLeakageError as exc:
            for pit_violation in exc.violations:
                _add(
                    violations,
                    _prefix_pit_path(candidate_index=index, field=pit_violation.field),
                    f"PIT_GUARD_{pit_violation.code}",
                    pit_violation.message,
                )
        except (TypeError, ValueError) as exc:
            _add(
                violations,
                f"$.candidates[{index}]",
                "PIT_GUARD_INPUT_INVALID",
                f"existing PIT guard rejected invalid input: {exc}",
            )


def _normalize_axis(value: Mapping[str, Any]) -> dict[str, Any]:
    normalized = {
        "evidence_state": value["evidence_state"],
        "value": value["value"],
        "publication_at": parse_datetime(value["publication_at"]).isoformat(),
        "evidence_refs": sorted(value["evidence_refs"], key=utf8_key),
    }
    if "reason_codes" in value:
        normalized["reason_codes"] = sorted(value["reason_codes"], key=utf8_key)
    return normalized


def _normalize_json(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _normalize_json(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_normalize_json(item) for item in value]
    return value


def _normalize_candidate(value: Mapping[str, Any]) -> dict[str, Any]:
    normalized: dict[str, Any] = {
        "candidate_id": value["candidate_id"],
        "company_id": value["company_id"],
        "security_code": value["security_code"],
        "pit_snapshot_id": value["pit_snapshot_id"],
        "eligibility": {
            "state": value["eligibility"]["state"],
            "reason_codes": sorted(
                value["eligibility"]["reason_codes"], key=utf8_key
            ),
        },
        "opportunity": _normalize_axis(value["opportunity"]),
        "confidence": _normalize_axis(value["confidence"]),
        "risk": _normalize_axis(value["risk"]),
    }
    if "metadata" in value:
        normalized["metadata"] = _normalize_json(value["metadata"])
    return normalized


def normalize_envelope(envelope: Mapping[str, Any]) -> dict[str, Any]:
    candidates = sorted(
        (_normalize_candidate(candidate) for candidate in envelope["candidates"]),
        key=lambda candidate: utf8_key(candidate["candidate_id"]),
    )
    return {
        "workbench_schema_version": envelope["workbench_schema_version"],
        "fixture_class": envelope["fixture_class"],
        "official_outcome_data": envelope["official_outcome_data"],
        "snapshot_cutoff_at": parse_datetime(envelope["snapshot_cutoff_at"]).isoformat(),
        "fixture_provenance": {
            **envelope["fixture_provenance"],
            "source_refs": sorted(
                envelope["fixture_provenance"]["source_refs"], key=utf8_key
            ),
        },
        "set_policy": {
            **envelope["set_policy"],
            "allowed_confidence_states": sorted(
                envelope["set_policy"]["allowed_confidence_states"], key=utf8_key
            ),
            "allowed_risk_states": sorted(
                envelope["set_policy"]["allowed_risk_states"], key=utf8_key
            ),
        },
        "candidates": candidates,
    }


def _axis_from_normalized(value: Mapping[str, Any]) -> AxisInput:
    return AxisInput(
        evidence_state=EvidenceState(value["evidence_state"]),
        value=Decimal(value["value"]) if value["value"] is not None else None,
        publication_at=parse_datetime(value["publication_at"]),
        evidence_refs=tuple(value["evidence_refs"]),
        reason_codes=tuple(value.get("reason_codes", [])),
    )


def validate_and_parse_envelope(
    envelope: Mapping[str, Any], *, pit_guard: PITGuard | None = None
) -> WorkbenchEnvelope:
    """Apply the positive schema and both outcome/PIT guards before any stage runs."""

    violations: list[ContractViolation] = []
    _validate_local_outcome_firewall(envelope, violations)

    if not _check_keys(
        envelope,
        path="$",
        allowed=_ENVELOPE_KEYS,
        required=_ENVELOPE_KEYS,
        violations=violations,
    ):
        raise WorkbenchContractError(violations)

    if envelope.get("workbench_schema_version") != WORKBENCH_SCHEMA_VERSION:
        _add(
            violations,
            "$.workbench_schema_version",
            "SCHEMA_VERSION_MISMATCH",
            f"value must equal {WORKBENCH_SCHEMA_VERSION!r}",
        )
    if envelope.get("fixture_class") != FIXTURE_CLASS:
        _add(
            violations,
            "$.fixture_class",
            "FIXTURE_CLASS_MISMATCH",
            f"value must equal {FIXTURE_CLASS!r}",
        )
    if envelope.get("official_outcome_data") is not False:
        _add(
            violations,
            "$.official_outcome_data",
            "OFFICIAL_OUTCOME_DATA_PROHIBITED",
            "official_outcome_data must be the boolean false",
        )

    cutoff = _validate_datetime(
        envelope.get("snapshot_cutoff_at"), "$.snapshot_cutoff_at", violations
    )
    _validate_provenance(
        envelope.get("fixture_provenance"), "$.fixture_provenance", violations
    )
    _validate_policy(envelope.get("set_policy"), "$.set_policy", violations)

    candidates = envelope.get("candidates")
    if not isinstance(candidates, list):
        _add(violations, "$.candidates", "EXPECTED_LIST", "candidates must be a list")
    elif not candidates:
        _add(
            violations,
            "$.candidates",
            "EMPTY_CANDIDATE_LIST",
            "candidates must contain at least one row",
        )
    else:
        for index, candidate in enumerate(candidates):
            _validate_candidate(candidate, index, cutoff, violations)

        candidate_ids = [
            candidate.get("candidate_id")
            for candidate in candidates
            if isinstance(candidate, Mapping)
            and isinstance(candidate.get("candidate_id"), str)
        ]
        pit_snapshot_ids = [
            candidate.get("pit_snapshot_id")
            for candidate in candidates
            if isinstance(candidate, Mapping)
            and isinstance(candidate.get("pit_snapshot_id"), str)
        ]
        if len(set(candidate_ids)) != len(candidate_ids):
            _add(
                violations,
                "$.candidates",
                "DUPLICATE_CANDIDATE_ID",
                "candidate_id must be unique within the envelope",
            )
        if len(set(pit_snapshot_ids)) != len(pit_snapshot_ids):
            _add(
                violations,
                "$.candidates",
                "DUPLICATE_PIT_SNAPSHOT_ID",
                "pit_snapshot_id must be unique within the envelope",
            )

    _run_existing_pit_guard(
        candidates,
        envelope.get("snapshot_cutoff_at"),
        violations,
        pit_guard or PITGuard(),
    )

    if violations:
        raise WorkbenchContractError(violations)

    normalized = normalize_envelope(envelope)
    normalized_candidates = normalized["candidates"]
    parsed_candidates = tuple(
        CandidateInput(
            candidate_id=value["candidate_id"],
            company_id=value["company_id"],
            security_code=value["security_code"],
            pit_snapshot_id=value["pit_snapshot_id"],
            eligibility=EligibilityInput(
                state=EligibilityState(value["eligibility"]["state"]),
                reason_codes=tuple(value["eligibility"]["reason_codes"]),
            ),
            opportunity=_axis_from_normalized(value["opportunity"]),
            confidence=_axis_from_normalized(value["confidence"]),
            risk=_axis_from_normalized(value["risk"]),
            metadata=value.get("metadata"),
        )
        for value in normalized_candidates
    )
    provenance = normalized["fixture_provenance"]
    policy = normalized["set_policy"]
    return WorkbenchEnvelope(
        workbench_schema_version=normalized["workbench_schema_version"],
        fixture_class=normalized["fixture_class"],
        official_outcome_data=normalized["official_outcome_data"],
        snapshot_cutoff_at=parse_datetime(normalized["snapshot_cutoff_at"]),
        fixture_provenance=FixtureProvenance(
            provenance_class=provenance["provenance_class"],
            contains_real_market_data=provenance["contains_real_market_data"],
            contains_official_w1_w8_data=provenance["contains_official_w1_w8_data"],
            contains_outcome_labels=provenance["contains_outcome_labels"],
            source_refs=tuple(provenance["source_refs"]),
            generator_rule_id=provenance["generator_rule_id"],
            purpose=provenance["purpose"],
        ),
        set_policy=SetPolicy(
            policy_id=policy["policy_id"],
            set_size=policy["set_size"],
            eligibility_required=EligibilityState(policy["eligibility_required"]),
            allowed_confidence_states=tuple(
                EvidenceState(item) for item in policy["allowed_confidence_states"]
            ),
            allowed_risk_states=tuple(
                EvidenceState(item) for item in policy["allowed_risk_states"]
            ),
            opportunity_state_required_for_raw_rank=EvidenceState(
                policy["opportunity_state_required_for_raw_rank"]
            ),
        ),
        candidates=parsed_candidates,
        normalized_input=normalized,
    )


def axis_to_mapping(axis: AxisInput) -> dict[str, Any]:
    result: dict[str, Any] = {
        "evidence_state": axis.evidence_state.value,
        "value": format(axis.value, "f") if axis.value is not None else None,
        "publication_at": axis.publication_at.isoformat(),
        "evidence_refs": list(axis.evidence_refs),
    }
    if axis.reason_codes:
        result["reason_codes"] = list(axis.reason_codes)
    return result


def eligibility_to_mapping(eligibility: EligibilityInput) -> dict[str, Any]:
    return {
        "state": eligibility.state.value,
        "reason_codes": list(eligibility.reason_codes),
    }
