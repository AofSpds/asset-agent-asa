from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import hashlib
import json
import re
from typing import Iterable

from aaa.core.balanced_v1 import BALANCED_V1, IdentityEnvelope, SchemaRef


_SHA40_RE = re.compile(r"^[0-9a-f]{40}$")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class LogicalRunStatus(str, Enum):
    READY_NOT_DISPATCHED = "READY_NOT_DISPATCHED"
    DISPATCHED = "DISPATCHED"
    ACTIVE = "ACTIVE"
    BLOCKED = "BLOCKED"
    COMPLETED_PASS = "COMPLETED_PASS"
    COMPLETED_FAIL = "COMPLETED_FAIL"
    COMPLETED_WITH_FINDINGS = "COMPLETED_WITH_FINDINGS"
    CANCELLED = "CANCELLED"
    SUPERSEDED = "SUPERSEDED"


class RunAttemptState(str, Enum):
    CREATED = "CREATED"
    CLAIMED = "CLAIMED"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    RUNNING_CONFIRMED = "RUNNING_CONFIRMED"
    STALE_UNKNOWN = "STALE_UNKNOWN"
    COMPLETED_PASS = "COMPLETED_PASS"
    COMPLETED_FAIL = "COMPLETED_FAIL"
    COMPLETED_WITH_FINDINGS = "COMPLETED_WITH_FINDINGS"
    CANCELLED = "CANCELLED"
    TIMED_OUT = "TIMED_OUT"
    INFRASTRUCTURE_FAILED = "INFRASTRUCTURE_FAILED"
    CONTRACT_FAILED = "CONTRACT_FAILED"


TERMINAL_ATTEMPT_STATES = frozenset(
    {
        RunAttemptState.COMPLETED_PASS,
        RunAttemptState.COMPLETED_FAIL,
        RunAttemptState.COMPLETED_WITH_FINDINGS,
        RunAttemptState.CANCELLED,
        RunAttemptState.TIMED_OUT,
        RunAttemptState.INFRASTRUCTURE_FAILED,
        RunAttemptState.CONTRACT_FAILED,
    }
)


class TerminationClass(str, Enum):
    BUSINESS_PASS = "BUSINESS_PASS"
    BUSINESS_FAIL = "BUSINESS_FAIL"
    BUSINESS_PASS_WITH_FINDINGS = "BUSINESS_PASS_WITH_FINDINGS"
    VALIDATION_FAIL = "VALIDATION_FAIL"
    VALIDATION_WITH_FINDINGS = "VALIDATION_WITH_FINDINGS"
    APPLICATION_FAILURE = "APPLICATION_FAILURE"
    INPUT_INTEGRITY_FAILURE = "INPUT_INTEGRITY_FAILURE"
    EXECUTION_CONTRACT_VIOLATION = "EXECUTION_CONTRACT_VIOLATION"
    SECURITY_POLICY_DENIAL = "SECURITY_POLICY_DENIAL"
    INFRASTRUCTURE_TRANSIENT = "INFRASTRUCTURE_TRANSIENT"
    INFRASTRUCTURE_PERMANENT = "INFRASTRUCTURE_PERMANENT"
    STALE_LEASE = "STALE_LEASE"
    TIMEOUT = "TIMEOUT"
    CANCELLED_BY_AUTHORITY = "CANCELLED_BY_AUTHORITY"
    SUPERSEDED = "SUPERSEDED"
    UNKNOWN_FAIL_CLOSED = "UNKNOWN_FAIL_CLOSED"


class RetryableDisposition(str, Enum):
    RETRYABLE_IF_POLICY_ALLOWS = "RETRYABLE_IF_POLICY_ALLOWS"
    RETRYABLE_IF_POLICY_ALLOWS_NEW_ATTEMPT = "RETRYABLE_IF_POLICY_ALLOWS_NEW_ATTEMPT"
    NOT_RETRYABLE = "NOT_RETRYABLE"
    NOT_EXECUTION_RETRY = "NOT_EXECUTION_RETRY"
    REQUIRES_NEW_LOGICAL_RUN = "REQUIRES_NEW_LOGICAL_RUN"


def _nonempty(name: str, value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value


def _sha40(name: str, value: str) -> str:
    if not _SHA40_RE.fullmatch(value):
        raise ValueError(f"{name} must be a lowercase 40-character Git SHA")
    return value


def _sha256(name: str, value: str) -> str:
    if not _SHA256_RE.fullmatch(value):
        raise ValueError(f"{name} must be a lowercase 64-character SHA256")
    return value


def _aware(name: str, value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")
    return value


@dataclass(frozen=True, order=True)
class DependencyLockRef:
    identity: str
    sha256: str

    def __post_init__(self) -> None:
        _nonempty("identity", self.identity)
        _sha256("sha256", self.sha256)


def _sorted_identity_refs(values: Iterable[IdentityEnvelope]) -> list[dict[str, str]]:
    return [
        {
            "project_namespace": item.project_namespace,
            "entity_family": item.entity_family,
            "local_id": item.local_id,
        }
        for item in sorted(values, key=lambda item: item.canonical_key)
    ]


def _sorted_schema_refs(values: Iterable[SchemaRef]) -> list[dict[str, str]]:
    return [
        {"schema_family_id": item.schema_family_id, "schema_version": item.schema_version}
        for item in sorted(values, key=lambda item: (item.schema_family_id, item.schema_version))
    ]


def _sorted_dependency_locks(values: Iterable[DependencyLockRef]) -> list[dict[str, str]]:
    return [
        {"identity": item.identity, "sha256": item.sha256}
        for item in sorted(values, key=lambda item: (item.identity, item.sha256))
    ]


@dataclass(frozen=True)
class LogicalRunSpec:
    run_id: str
    project_namespace: str
    process_id: str
    work_order_ref: str
    responsible_persona: str
    executor_role: str
    repository_identity: str
    exact_target_commit: str
    execution_profile_ref: str
    execution_profile_sha256: str
    configuration_sha256: str
    dependency_lock_refs: tuple[DependencyLockRef, ...] = field(default_factory=tuple)
    material_input_refs: tuple[IdentityEnvelope, ...] = field(default_factory=tuple)
    schema_family_version_refs: tuple[SchemaRef, ...] = field(default_factory=tuple)
    created_at: datetime | None = None
    semantic_generation: str = BALANCED_V1

    def __post_init__(self) -> None:
        for name in (
            "run_id",
            "project_namespace",
            "process_id",
            "work_order_ref",
            "responsible_persona",
            "executor_role",
            "repository_identity",
            "execution_profile_ref",
        ):
            _nonempty(name, getattr(self, name))
        _sha40("exact_target_commit", self.exact_target_commit)
        _sha256("execution_profile_sha256", self.execution_profile_sha256)
        _sha256("configuration_sha256", self.configuration_sha256)
        if self.created_at is not None:
            _aware("created_at", self.created_at)
        if self.semantic_generation != BALANCED_V1:
            raise ValueError("LogicalRunSpec requires BALANCED_V1 semantic generation")
        if len(set(self.dependency_lock_refs)) != len(self.dependency_lock_refs):
            raise ValueError("dependency_lock_refs contains duplicates")
        if len(set(self.material_input_refs)) != len(self.material_input_refs):
            raise ValueError("material_input_refs contains duplicate typed identities")
        if len(set(self.schema_family_version_refs)) != len(self.schema_family_version_refs):
            raise ValueError("schema_family_version_refs contains duplicates")

    def execution_spec_payload(self) -> dict[str, object]:
        """Return fields whose material change creates a different Logical Run."""
        return {
            "project_namespace": self.project_namespace,
            "process_id": self.process_id,
            "work_order_ref": self.work_order_ref,
            "responsible_persona": self.responsible_persona,
            "executor_role": self.executor_role,
            "repository_identity": self.repository_identity,
            "exact_target_commit": self.exact_target_commit,
            "execution_profile_ref": self.execution_profile_ref,
            "execution_profile_sha256": self.execution_profile_sha256,
            "configuration_sha256": self.configuration_sha256,
            "dependency_lock_refs": _sorted_dependency_locks(self.dependency_lock_refs),
            "material_input_refs": _sorted_identity_refs(self.material_input_refs),
            "schema_family_version_refs": _sorted_schema_refs(self.schema_family_version_refs),
        }

    @property
    def exact_execution_spec_hash(self) -> str:
        canonical = json.dumps(
            self.execution_spec_payload(), ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        return hashlib.sha256(canonical).hexdigest()

    def same_logical_execution_as(self, other: "LogicalRunSpec") -> bool:
        return self.exact_execution_spec_hash == other.exact_execution_spec_hash


@dataclass(frozen=True)
class RunAttempt:
    run_attempt_id: str
    run_id: str
    attempt_ordinal: int
    exact_execution_spec_hash: str
    state: RunAttemptState = RunAttemptState.CREATED
    retry_of_attempt_id: str | None = None
    retry_reason_code: str | None = None
    retry_authorization_ref: str | None = None
    worker_id: str | None = None
    lease_epoch: int = 0
    claimed_at: datetime | None = None
    acknowledged_at: datetime | None = None
    started_at: datetime | None = None
    last_heartbeat_at: datetime | None = None
    lease_expires_at: datetime | None = None
    timeout_at: datetime | None = None
    terminal_receipt_ref: str | None = None
    terminal_result_ref: str | None = None

    def __post_init__(self) -> None:
        _nonempty("run_attempt_id", self.run_attempt_id)
        _nonempty("run_id", self.run_id)
        _sha256("exact_execution_spec_hash", self.exact_execution_spec_hash)
        if self.attempt_ordinal < 1:
            raise ValueError("attempt_ordinal must start at 1")
        if self.lease_epoch < 0:
            raise ValueError("lease_epoch must be non-negative")
        for name in (
            "claimed_at",
            "acknowledged_at",
            "started_at",
            "last_heartbeat_at",
            "lease_expires_at",
            "timeout_at",
        ):
            value = getattr(self, name)
            if value is not None:
                _aware(name, value)
        if self.attempt_ordinal == 1 and self.retry_of_attempt_id is not None:
            raise ValueError("first attempt cannot retry another attempt")
        if self.attempt_ordinal > 1:
            for name in ("retry_of_attempt_id", "retry_reason_code", "retry_authorization_ref"):
                _nonempty(name, getattr(self, name) or "")
        if self.state is RunAttemptState.RUNNING_CONFIRMED:
            if self.started_at is None or self.last_heartbeat_at is None or self.lease_expires_at is None:
                raise ValueError("RUNNING_CONFIRMED requires start, heartbeat, and lease expiry")
            if self.last_heartbeat_at < self.started_at:
                raise ValueError("heartbeat cannot precede start")
        if self.state in TERMINAL_ATTEMPT_STATES and not self.terminal_receipt_ref:
            raise ValueError("terminal RunAttempt requires termination receipt")
        if self.state not in TERMINAL_ATTEMPT_STATES and self.terminal_receipt_ref is not None:
            raise ValueError("nonterminal RunAttempt cannot bind termination receipt")

    def running_at(self, observed_at: datetime) -> bool:
        _aware("observed_at", observed_at)
        if self.state is not RunAttemptState.RUNNING_CONFIRMED:
            return False
        if self.started_at is None or self.last_heartbeat_at is None or self.lease_expires_at is None:
            return False
        return self.started_at <= observed_at <= self.lease_expires_at and self.last_heartbeat_at <= observed_at


@dataclass(frozen=True)
class AttemptTerminationReceipt:
    attempt_termination_id: str
    run_id: str
    run_attempt_id: str
    termination_class: TerminationClass
    retryable_disposition: RetryableDisposition
    authority_ref: str
    actor_ref: str
    terminated_at: datetime
    terminal_result_ref: str | None = None

    def __post_init__(self) -> None:
        for name in (
            "attempt_termination_id",
            "run_id",
            "run_attempt_id",
            "authority_ref",
            "actor_ref",
        ):
            _nonempty(name, getattr(self, name))
        _aware("terminated_at", self.terminated_at)


@dataclass(frozen=True)
class LogicalRunFinalDispositionReceipt:
    final_disposition_id: str
    run_id: str
    final_status: LogicalRunStatus
    authority_ref: str
    actor_ref: str
    decided_at: datetime
    selected_attempt_ref: str | None = None
    decision_ref: str | None = None

    def __post_init__(self) -> None:
        for name in ("final_disposition_id", "run_id", "authority_ref", "actor_ref"):
            _nonempty(name, getattr(self, name))
        _aware("decided_at", self.decided_at)
        if self.final_status not in {
            LogicalRunStatus.COMPLETED_PASS,
            LogicalRunStatus.COMPLETED_FAIL,
            LogicalRunStatus.COMPLETED_WITH_FINDINGS,
            LogicalRunStatus.CANCELLED,
            LogicalRunStatus.SUPERSEDED,
        }:
            raise ValueError("final disposition requires a logical terminal status")
        if self.final_status in {
            LogicalRunStatus.COMPLETED_PASS,
            LogicalRunStatus.COMPLETED_FAIL,
            LogicalRunStatus.COMPLETED_WITH_FINDINGS,
        } and not self.selected_attempt_ref:
            raise ValueError("completed Logical Run requires selected terminal attempt")
        if self.final_status in {LogicalRunStatus.CANCELLED, LogicalRunStatus.SUPERSEDED} and not self.decision_ref:
            raise ValueError("cancelled/superseded Logical Run requires decision_ref")


def validate_retry_attempt(previous: RunAttempt, candidate: RunAttempt, spec: LogicalRunSpec) -> None:
    if previous.run_id != candidate.run_id or candidate.run_id != spec.run_id:
        raise ValueError("retry attempt must remain within the same Logical Run")
    if candidate.retry_of_attempt_id != previous.run_attempt_id:
        raise ValueError("retry_of_attempt_id must reference the previous attempt")
    if candidate.attempt_ordinal <= previous.attempt_ordinal:
        raise ValueError("retry attempt ordinal must increase")
    if previous.exact_execution_spec_hash != spec.exact_execution_spec_hash:
        raise ValueError("previous attempt execution spec does not match Logical Run")
    if candidate.exact_execution_spec_hash != spec.exact_execution_spec_hash:
        raise ValueError("material spec change requires a new Logical Run")


def require_new_logical_run(before: LogicalRunSpec, after: LogicalRunSpec) -> bool:
    return before.exact_execution_spec_hash != after.exact_execution_spec_hash
