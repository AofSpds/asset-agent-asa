from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from enum import Enum, IntEnum
from typing import Callable, Mapping, Any

from aaa.core.identity import ExactBaseIdentity, assert_exact_base, content_sha256


class PermissionLevel(IntEnum):
    READ_ONLY = 0
    TOOL_EXECUTION = 1
    ISOLATED_BRANCH_WRITE = 2


class RunStatus(str, Enum):
    CREATED = "CREATED"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"
    CANCELLED = "CANCELLED"


TERMINAL_STATUSES = {
    RunStatus.SUCCEEDED,
    RunStatus.FAILED,
    RunStatus.BLOCKED,
    RunStatus.CANCELLED,
}

_ALLOWED_TRANSITIONS = {
    RunStatus.CREATED: {RunStatus.RUNNING, RunStatus.BLOCKED, RunStatus.CANCELLED},
    RunStatus.RUNNING: TERMINAL_STATUSES,
}


FORBIDDEN_ALWAYS = {
    "CANONICAL_WRITE",
    "AUTHORITATIVE_ADJUDICATION",
    "INDEPENDENT_VALIDATION_SELF_CERTIFICATION",
    "GROUND_TRUTH_PROMOTION",
    "MODEL_FREEZE",
    "PRODUCTION_RELEASE",
}


@dataclass(frozen=True)
class WorkOrderIdentity:
    work_order_id: str
    work_order_version: str
    work_order_sha256: str

    def __post_init__(self) -> None:
        if not self.work_order_id or not self.work_order_version:
            raise ValueError("work_order_id and work_order_version are required")
        if len(self.work_order_sha256) != 64 or any(c not in "0123456789abcdef" for c in self.work_order_sha256):
            raise ValueError("work_order_sha256 must be a lowercase 64-character SHA256")


@dataclass(frozen=True)
class AgentRunContext:
    run_id: str
    executor_role: str
    permission_level: PermissionLevel
    exact_base_commit: str
    branch: str | None = None


@dataclass(frozen=True)
class AgentRunRecord:
    run_id: str
    work_order_identity: WorkOrderIdentity
    exact_base_identity: ExactBaseIdentity
    executor_role: str
    permission_level: PermissionLevel
    status: RunStatus = RunStatus.CREATED
    branch: str | None = None
    result_sha256: str | None = None
    terminal_reason: str | None = None

    def __post_init__(self) -> None:
        if not self.run_id or not self.executor_role:
            raise ValueError("run_id and executor_role are required")
        if self.permission_level == PermissionLevel.ISOLATED_BRANCH_WRITE and not self.branch:
            raise ValueError("L2 agent run requires an isolated branch")
        if self.result_sha256 is not None:
            if len(self.result_sha256) != 64 or any(c not in "0123456789abcdef" for c in self.result_sha256):
                raise ValueError("result_sha256 must be a lowercase 64-character SHA256")
        if self.status == RunStatus.SUCCEEDED and self.result_sha256 is None:
            raise ValueError("SUCCEEDED run requires result_sha256")
        if self.status in {RunStatus.FAILED, RunStatus.BLOCKED, RunStatus.CANCELLED} and not self.terminal_reason:
            raise ValueError(f"{self.status.value} run requires terminal_reason")

    def identity_payload(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "work_order_identity": asdict(self.work_order_identity),
            "exact_base_identity": asdict(self.exact_base_identity),
            "executor_role": self.executor_role,
            "permission_level": int(self.permission_level),
            "branch": self.branch,
        }

    @property
    def immutable_run_sha256(self) -> str:
        return content_sha256(self.identity_payload())


class PermissionDenied(RuntimeError):
    pass


class InvalidRunTransition(RuntimeError):
    pass


def assert_status_transition(source: RunStatus, target: RunStatus) -> None:
    if source in TERMINAL_STATUSES:
        raise InvalidRunTransition(f"TERMINAL_RUN_IMMUTABLE: {source.value}")
    allowed = _ALLOWED_TRANSITIONS.get(source, set())
    if target not in allowed:
        raise InvalidRunTransition(f"INVALID_RUN_TRANSITION: {source.value}->{target.value}")


def authorize_action(context: AgentRunContext, action: str, required_level: PermissionLevel) -> None:
    if action in FORBIDDEN_ALWAYS:
        raise PermissionDenied(f"FORBIDDEN_AUTHORITY_ACTION: {action}")
    if context.permission_level < required_level:
        raise PermissionDenied(
            f"INSUFFICIENT_PERMISSION: action={action} required={required_level.name} "
            f"actual={context.permission_level.name}"
        )
    if required_level == PermissionLevel.ISOLATED_BRANCH_WRITE and not context.branch:
        raise PermissionDenied("ISOLATED_BRANCH_REQUIRED")


def create_run(
    *,
    run_id: str,
    work_order_identity: WorkOrderIdentity,
    expected_base: ExactBaseIdentity,
    observed_base: ExactBaseIdentity,
    executor_role: str,
    permission_level: PermissionLevel,
    branch: str | None = None,
) -> AgentRunRecord:
    assert_exact_base(expected_base, observed_base)
    return AgentRunRecord(
        run_id=run_id,
        work_order_identity=work_order_identity,
        exact_base_identity=expected_base,
        executor_role=executor_role,
        permission_level=permission_level,
        branch=branch,
    )


def transition_run(
    record: AgentRunRecord,
    target: RunStatus,
    *,
    result: Mapping[str, Any] | None = None,
    terminal_reason: str | None = None,
) -> AgentRunRecord:
    assert_status_transition(record.status, target)

    result_sha256 = None
    if target == RunStatus.SUCCEEDED:
        if result is None:
            raise InvalidRunTransition("SUCCEEDED_REQUIRES_RESULT")
        result_sha256 = content_sha256(dict(result))
        terminal_reason = None
    elif target in {RunStatus.FAILED, RunStatus.BLOCKED, RunStatus.CANCELLED}:
        if not terminal_reason:
            raise InvalidRunTransition(f"{target.value}_REQUIRES_REASON")
        if result is not None:
            raise InvalidRunTransition(f"{target.value}_MUST_NOT_BIND_SUCCESS_RESULT")
    elif result is not None or terminal_reason is not None:
        raise InvalidRunTransition("NON_TERMINAL_TRANSITION_MUST_NOT_BIND_TERMINAL_FIELDS")

    return replace(
        record,
        status=target,
        result_sha256=result_sha256,
        terminal_reason=terminal_reason,
    )


def recover_interrupted_run(record: AgentRunRecord, *, reason: str = "INTERRUPTED_RESTART") -> AgentRunRecord:
    if record.status != RunStatus.RUNNING:
        return record
    return transition_run(record, RunStatus.BLOCKED, terminal_reason=reason)


def execute(
    context: AgentRunContext,
    action: str,
    required_level: PermissionLevel,
    fn: Callable[[], Mapping[str, Any]],
) -> Mapping[str, Any]:
    authorize_action(context, action, required_level)
    result = dict(fn())
    result.setdefault("run_id", context.run_id)
    result.setdefault("executor_role", context.executor_role)
    return result
