from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
import re
from typing import Any, Mapping


LEGACY_AAA_RUN_V0_X = "LEGACY_AAA_RUN_V0_X"
BALANCED_V1 = "BALANCED_V1"
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class TimeSemantic(str, Enum):
    FACT_OR_EFFECTIVE_TIME = "FACT_OR_EFFECTIVE_TIME"
    PUBLIC_EVIDENCE_AVAILABLE_TIME = "PUBLIC_EVIDENCE_AVAILABLE_TIME"
    RECORDED_TIME = "RECORDED_TIME"
    SNAPSHOT_CUTOFF_TIME = "SNAPSHOT_CUTOFF_TIME"
    EXECUTION_LIFECYCLE_TIME = "EXECUTION_LIFECYCLE_TIME"


class TimePrecision(str, Enum):
    DATE = "DATE"
    DATETIME_TZ = "DATETIME_TZ"


class TimeAuthorityKind(str, Enum):
    SOURCE_EVIDENCE = "SOURCE_EVIDENCE"
    GOVERNED_OPERATIONAL_STORE_CLOCK = "GOVERNED_OPERATIONAL_STORE_CLOCK"
    IMMUTABLE_CERTIFICATION = "IMMUTABLE_CERTIFICATION"
    EXTERNAL_GOVERNED_CALENDAR_OR_TIME_SOURCE = "EXTERNAL_GOVERNED_CALENDAR_OR_TIME_SOURCE"


class SchemaStatus(str, Enum):
    WORKING = "WORKING"
    CANDIDATE = "CANDIDATE"
    FROZEN = "FROZEN"
    DEPRECATED = "DEPRECATED"


class CompatibilityWithPredecessor(str, Enum):
    NON_BREAKING_ADDITIVE = "NON_BREAKING_ADDITIVE"
    BREAKING_SUCCESSOR = "BREAKING_SUCCESSOR"
    REVISION_ONLY_NO_SCHEMA_CHANGE = "REVISION_ONLY_NO_SCHEMA_CHANGE"
    NOT_APPLICABLE_INITIAL = "NOT_APPLICABLE_INITIAL"


class ReaderPolicy(str, Enum):
    EXACT_VERSION_ONLY = "EXACT_VERSION_ONLY"
    DECLARED_COMPATIBLE_SET = "DECLARED_COMPATIBLE_SET"


def _nonempty(name: str, value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value


def _aware(value: datetime, name: str) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")
    return value


def _sha256(name: str, value: str) -> str:
    if not _SHA256_RE.fullmatch(value):
        raise ValueError(f"{name} must be a lowercase 64-character SHA256")
    return value


@dataclass(frozen=True, order=True)
class IdentityEnvelope:
    project_namespace: str
    entity_family: str
    local_id: str

    def __post_init__(self) -> None:
        _nonempty("project_namespace", self.project_namespace)
        _nonempty("entity_family", self.entity_family)
        _nonempty("local_id", self.local_id)

    @property
    def canonical_key(self) -> tuple[str, str, str]:
        return (self.project_namespace, self.entity_family, self.local_id)


@dataclass(frozen=True)
class GovernedTimeEvidence:
    semantic: TimeSemantic
    precision: TimePrecision
    value: date | datetime
    authority_kind: TimeAuthorityKind
    authority_identity: str
    evidence_or_clock_reference: str

    def __post_init__(self) -> None:
        _nonempty("authority_identity", self.authority_identity)
        _nonempty("evidence_or_clock_reference", self.evidence_or_clock_reference)
        if self.precision is TimePrecision.DATE:
            # datetime is a subclass of date; reject it explicitly so DATE precision
            # can never smuggle in invented intraday precision.
            if isinstance(self.value, datetime) or not isinstance(self.value, date):
                raise ValueError("DATE precision requires a date value and forbids datetime")
        elif self.precision is TimePrecision.DATETIME_TZ:
            if not isinstance(self.value, datetime):
                raise ValueError("DATETIME_TZ precision requires datetime")
            _aware(self.value, "value")
        else:  # pragma: no cover - Enum construction normally prevents this.
            raise ValueError("unsupported time precision")


def validate_pit_admissibility(
    *,
    snapshot_cutoff_at: datetime,
    publication_at: datetime | None = None,
    supported_cutoff_at: datetime | None = None,
) -> bool:
    """Return PIT admissibility under the frozen publication/support cutoff rule.

    This function never infers historical availability from recorded/execution time.
    At least one governed publication/support timestamp must be supplied.
    """
    cutoff = _aware(snapshot_cutoff_at, "snapshot_cutoff_at")
    if publication_at is None and supported_cutoff_at is None:
        raise ValueError("publication_at or supported_cutoff_at is required")
    publication_ok = False
    supported_ok = False
    if publication_at is not None:
        publication_ok = _aware(publication_at, "publication_at") <= cutoff
    if supported_cutoff_at is not None:
        supported_ok = _aware(supported_cutoff_at, "supported_cutoff_at") <= cutoff
    return publication_ok or supported_ok


@dataclass(frozen=True, order=True)
class SchemaRef:
    schema_family_id: str
    schema_version: str

    def __post_init__(self) -> None:
        _nonempty("schema_family_id", self.schema_family_id)
        _nonempty("schema_version", self.schema_version)
        if self.schema_version.lower() == "latest":
            raise ValueError("floating latest is not a governed schema version")


@dataclass(frozen=True)
class SchemaFamilyVersion:
    ref: SchemaRef
    schema_status: SchemaStatus
    compatibility_with_predecessor: CompatibilityWithPredecessor
    reader_policy: ReaderPolicy
    spec_sha256: str
    predecessor: SchemaRef | None = None

    def __post_init__(self) -> None:
        _sha256("spec_sha256", self.spec_sha256)
        initial = self.compatibility_with_predecessor is CompatibilityWithPredecessor.NOT_APPLICABLE_INITIAL
        if initial and self.predecessor is not None:
            raise ValueError("initial schema version must not declare predecessor")
        if not initial and self.predecessor is None:
            raise ValueError("non-initial compatibility declaration requires exact predecessor")
        if self.predecessor == self.ref:
            raise ValueError("schema version cannot be its own predecessor")


@dataclass(frozen=True)
class DeclaredCompatibleSet:
    compatible_set_id: str
    reader: SchemaRef
    members: tuple[SchemaRef, ...]
    component_set_sha256: str

    def __post_init__(self) -> None:
        _nonempty("compatible_set_id", self.compatible_set_id)
        _sha256("component_set_sha256", self.component_set_sha256)
        if not self.members:
            raise ValueError("declared compatible set must contain at least one exact schema ref")
        if len(set(self.members)) != len(self.members):
            raise ValueError("declared compatible set contains duplicate schema refs")

    def permits(self, candidate: SchemaRef) -> bool:
        """Compatibility is deliberately directional: reader -> candidate."""
        return candidate in self.members


def project_legacy_run_semantics(record: Mapping[str, Any]) -> dict[str, Any]:
    """Return a non-persistent compatibility projection for historical AAA Runs.

    The projection labels historical semantics and intentionally does not invent a
    run_attempt_id. Persistence callers must keep the source historical record unchanged.
    """
    if "run_attempt_id" in record:
        raise ValueError("historical legacy projection must not contain run_attempt_id")
    if record.get("semantic_generation") == BALANCED_V1:
        raise ValueError("Balanced-v1 record cannot be projected as legacy")
    projected = dict(record)
    projected["semantic_generation"] = LEGACY_AAA_RUN_V0_X
    return projected


def require_balanced_v1_marker(record: Mapping[str, Any]) -> None:
    if record.get("semantic_generation") != BALANCED_V1:
        raise ValueError("successor record requires explicit BALANCED_V1 semantic_generation")
