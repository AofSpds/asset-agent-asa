from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import re
from typing import Iterable

from aaa.core.balanced_v1 import IdentityEnvelope
from aaa.core.execution_v1 import DependencyLockRef, LogicalRunSpec, RunAttempt


_SHA40_RE = re.compile(r"^[0-9a-f]{40}$")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class ActorType(str, Enum):
    HUMAN_OWNER = "HUMAN_OWNER"
    PERSONA_INSTANCE = "PERSONA_INSTANCE"
    WORKER = "WORKER"
    SERVICE = "SERVICE"
    CI_JOB = "CI_JOB"
    VALIDATOR_RUNTIME = "VALIDATOR_RUNTIME"


class Decision(str, Enum):
    APPROVE = "APPROVE"
    DENY = "DENY"
    REVOKE = "REVOKE"
    SUPERSEDE = "SUPERSEDE"


class ExactTargetKind(str, Enum):
    GIT_COMMIT = "GIT_COMMIT"
    CONTENT_SHA256 = "CONTENT_SHA256"
    RELEASE_SET = "RELEASE_SET"
    ARTIFACT_IDENTITY = "ARTIFACT_IDENTITY"
    SHARED_CONTRACT_RECONCILIATION = "SHARED_CONTRACT_RECONCILIATION"


class OperationalEventFamily(str, Enum):
    RUN_LIFECYCLE = "RUN_LIFECYCLE"
    ATTEMPT_LIFECYCLE = "ATTEMPT_LIFECYCLE"
    DISPATCH = "DISPATCH"
    LEASE = "LEASE"
    RESULT = "RESULT"
    DECISION = "DECISION"
    PROMOTION = "PROMOTION"
    RESTORE = "RESTORE"


def _nonempty(name: str, value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value


def _aware(name: str, value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")
    return value


def _sha40(name: str, value: str) -> str:
    if not _SHA40_RE.fullmatch(value):
        raise ValueError(f"{name} must be a lowercase 40-character Git SHA")
    return value


def _sha256(name: str, value: str) -> str:
    if not _SHA256_RE.fullmatch(value):
        raise ValueError(f"{name} must be a lowercase 64-character SHA256")
    return value


@dataclass(frozen=True)
class ActorRef:
    actor_type: ActorType
    actor_identity: str
    runtime_instance_id: str | None = None
    session_context_ref: str | None = None

    def __post_init__(self) -> None:
        _nonempty("actor_identity", self.actor_identity)
        if self.runtime_instance_id is not None:
            _nonempty("runtime_instance_id", self.runtime_instance_id)
        if self.session_context_ref is not None:
            _nonempty("session_context_ref", self.session_context_ref)


@dataclass(frozen=True)
class AuthorityRef:
    authority_role: str
    authority_identity: str
    authority_scope: str
    authority_source_ref: str

    def __post_init__(self) -> None:
        for name in ("authority_role", "authority_identity", "authority_scope", "authority_source_ref"):
            _nonempty(name, getattr(self, name))


@dataclass(frozen=True)
class ExactTargetIdentity:
    target_kind: ExactTargetKind
    immutable_identity: str
    content_sha256: str | None = None

    def __post_init__(self) -> None:
        value = _nonempty("immutable_identity", self.immutable_identity)
        lowered = value.lower()
        if lowered in {"latest", "head", "current", "main", "master"} or lowered.startswith("refs/heads/"):
            raise ValueError("floating branch/head/latest alias is not an exact governed target")
        if self.target_kind is ExactTargetKind.GIT_COMMIT:
            _sha40("immutable_identity", value)
        if self.target_kind is ExactTargetKind.CONTENT_SHA256:
            _sha256("immutable_identity", value)
        if self.content_sha256 is not None:
            _sha256("content_sha256", self.content_sha256)


@dataclass(frozen=True)
class ExactTargetDecisionReceipt:
    decision_id: str
    decision_type: str
    target: ExactTargetIdentity
    authority_ref: AuthorityRef
    actor_ref: ActorRef
    decision: Decision
    decided_at: datetime
    rationale_ref: str | None = None
    prerequisite_receipt_refs: tuple[str, ...] = field(default_factory=tuple)
    supersedes_decision_ref: str | None = None
    revokes_decision_ref: str | None = None

    def __post_init__(self) -> None:
        _nonempty("decision_id", self.decision_id)
        _nonempty("decision_type", self.decision_type)
        _aware("decided_at", self.decided_at)
        if self.rationale_ref is not None:
            _nonempty("rationale_ref", self.rationale_ref)
        for ref in self.prerequisite_receipt_refs:
            _nonempty("prerequisite_receipt_ref", ref)
        if self.decision is Decision.REVOKE:
            _nonempty("revokes_decision_ref", self.revokes_decision_ref or "")
        elif self.revokes_decision_ref is not None:
            raise ValueError("revokes_decision_ref is only valid for REVOKE")
        if self.decision is Decision.SUPERSEDE:
            _nonempty("supersedes_decision_ref", self.supersedes_decision_ref or "")
        elif self.supersedes_decision_ref is not None:
            raise ValueError("supersedes_decision_ref is only valid for SUPERSEDE")

    def authorizes(self, target: ExactTargetIdentity) -> bool:
        return self.decision is Decision.APPROVE and self.target == target


@dataclass(frozen=True)
class MaterialInputProvenanceRef:
    identity: IdentityEnvelope
    content_sha256: str | None = None
    locator: str | None = None
    schema_version: str | None = None
    snapshot_cutoff_at: datetime | None = None

    def __post_init__(self) -> None:
        if self.content_sha256 is not None:
            _sha256("content_sha256", self.content_sha256)
        if self.locator is not None:
            _nonempty("locator", self.locator)
        if self.schema_version is not None:
            _nonempty("schema_version", self.schema_version)
        if self.snapshot_cutoff_at is not None:
            _aware("snapshot_cutoff_at", self.snapshot_cutoff_at)


@dataclass(frozen=True)
class ExecutionProvenanceReceipt:
    provenance_receipt_id: str
    run_id: str
    run_attempt_id: str
    repository_identity: str
    exact_commit_sha: str
    git_tree_sha: str
    working_tree_clean: bool
    execution_profile_id: str
    execution_profile_version: str
    execution_profile_sha256: str
    dependency_lock_refs: tuple[DependencyLockRef, ...]
    configuration_sha256: str
    material_input_refs: tuple[MaterialInputProvenanceRef, ...]
    runtime_identity: str
    verified_by_actor_ref: ActorRef
    verified_at: datetime

    def __post_init__(self) -> None:
        for name in (
            "provenance_receipt_id",
            "run_id",
            "run_attempt_id",
            "repository_identity",
            "execution_profile_id",
            "execution_profile_version",
            "runtime_identity",
        ):
            _nonempty(name, getattr(self, name))
        _sha40("exact_commit_sha", self.exact_commit_sha)
        _sha40("git_tree_sha", self.git_tree_sha)
        _sha256("execution_profile_sha256", self.execution_profile_sha256)
        _sha256("configuration_sha256", self.configuration_sha256)
        _aware("verified_at", self.verified_at)
        if self.working_tree_clean is not True:
            raise ValueError("governed Balanced-v1 execution requires clean working tree")
        if len(set(self.dependency_lock_refs)) != len(self.dependency_lock_refs):
            raise ValueError("dependency_lock_refs contains duplicates")
        identities = [item.identity for item in self.material_input_refs]
        if len(set(identities)) != len(identities):
            raise ValueError("material_input_refs contains duplicate typed identities")

    def verify_against(self, spec: LogicalRunSpec, attempt: RunAttempt) -> None:
        if self.run_id != spec.run_id or self.run_attempt_id != attempt.run_attempt_id:
            raise ValueError("provenance receipt Run/Attempt identity mismatch")
        if attempt.run_id != spec.run_id:
            raise ValueError("RunAttempt does not belong to Logical Run")
        if attempt.exact_execution_spec_hash != spec.exact_execution_spec_hash:
            raise ValueError("RunAttempt exact execution spec hash mismatch")
        if self.repository_identity != spec.repository_identity:
            raise ValueError("repository identity mismatch")
        if self.exact_commit_sha != spec.exact_target_commit:
            raise ValueError("actual exact commit does not match Logical Run target")
        if self.execution_profile_id != spec.execution_profile_ref:
            raise ValueError("execution profile identity mismatch")
        if self.execution_profile_sha256 != spec.execution_profile_sha256:
            raise ValueError("execution profile hash mismatch")
        if self.configuration_sha256 != spec.configuration_sha256:
            raise ValueError("configuration hash mismatch")
        if tuple(sorted(self.dependency_lock_refs)) != tuple(sorted(spec.dependency_lock_refs)):
            raise ValueError("dependency lock identity/hash mismatch")
        provenance_inputs = {item.identity for item in self.material_input_refs}
        if provenance_inputs != set(spec.material_input_refs):
            raise ValueError("material input identity mismatch")


@dataclass(frozen=True)
class OperationalEvent:
    operational_event_id: str
    project_namespace: str
    event_family: OperationalEventFamily
    event_type: str
    event_schema_version: str
    aggregate_ref: IdentityEnvelope
    sequence_number: int
    observed_at: datetime
    actor_ref: ActorRef
    authority_ref: AuthorityRef
    producer_or_actor_scope: str
    idempotency_scope_key: str
    payload_sha256: str
    decision_receipt_ref: str | None = None
    causation_event_ref: str | None = None
    correlation_id: str | None = None

    def __post_init__(self) -> None:
        for name in (
            "operational_event_id",
            "project_namespace",
            "event_type",
            "event_schema_version",
            "producer_or_actor_scope",
            "idempotency_scope_key",
        ):
            _nonempty(name, getattr(self, name))
        if self.aggregate_ref.project_namespace != self.project_namespace:
            raise ValueError("aggregate project namespace must match operational event")
        if self.sequence_number < 1:
            raise ValueError("sequence_number must start at 1")
        _aware("observed_at", self.observed_at)
        _sha256("payload_sha256", self.payload_sha256)
        for name in ("decision_receipt_ref", "causation_event_ref", "correlation_id"):
            value = getattr(self, name)
            if value is not None:
                _nonempty(name, value)

    @property
    def canonical_identity(self) -> tuple[str, str, str]:
        return (self.project_namespace, self.event_family.value, self.operational_event_id)

    @property
    def idempotency_identity(self) -> tuple[str, str, str, str]:
        return (
            self.project_namespace,
            self.producer_or_actor_scope,
            self.event_family.value,
            self.idempotency_scope_key,
        )

    @property
    def aggregate_sequence_identity(self) -> tuple[str, str, str, int]:
        return (*self.aggregate_ref.canonical_key, self.sequence_number)


class OperationalEventRegistry:
    """Small deterministic validator for append-only operational event semantics.

    This is intentionally not an Event Sourcing/CQRS framework. It validates identity,
    scoped idempotency, aggregate sequence uniqueness, and exact reappend only.
    """

    def __init__(self) -> None:
        self._by_identity: dict[tuple[str, str, str], OperationalEvent] = {}
        self._by_idempotency: dict[tuple[str, str, str, str], tuple[str, str, str]] = {}
        self._by_sequence: dict[tuple[str, str, str, int], tuple[str, str, str]] = {}

    def append(self, event: OperationalEvent) -> bool:
        existing = self._by_identity.get(event.canonical_identity)
        if existing is not None:
            if existing == event:
                return False
            raise ValueError("duplicate operational event identity with different payload/meaning")
        prior_idem = self._by_idempotency.get(event.idempotency_identity)
        if prior_idem is not None:
            raise ValueError("duplicate scoped idempotency key")
        prior_sequence = self._by_sequence.get(event.aggregate_sequence_identity)
        if prior_sequence is not None:
            raise ValueError("duplicate aggregate sequence number")
        self._by_identity[event.canonical_identity] = event
        self._by_idempotency[event.idempotency_identity] = event.canonical_identity
        self._by_sequence[event.aggregate_sequence_identity] = event.canonical_identity
        return True
