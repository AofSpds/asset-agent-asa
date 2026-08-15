from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import Callable, Mapping, Any


class PermissionLevel(IntEnum):
    READ_ONLY = 0
    TOOL_EXECUTION = 1
    ISOLATED_BRANCH_WRITE = 2


FORBIDDEN_ALWAYS = {
    "CANONICAL_WRITE",
    "AUTHORITATIVE_ADJUDICATION",
    "INDEPENDENT_VALIDATION_SELF_CERTIFICATION",
    "GROUND_TRUTH_PROMOTION",
    "MODEL_FREEZE",
    "PRODUCTION_RELEASE",
}


@dataclass(frozen=True)
class AgentRunContext:
    run_id: str
    executor_role: str
    permission_level: PermissionLevel
    exact_base_commit: str
    branch: str | None = None


class PermissionDenied(RuntimeError):
    pass


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
