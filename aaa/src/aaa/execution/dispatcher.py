from __future__ import annotations

from hashlib import sha256
from typing import Mapping

from aaa.execution.contracts import APPROVED_WORK_ORDER_STATES, ExecutionContractError, ExecutionTask
from aaa.execution.profiles import get_execution_profile

_FORBIDDEN_COMMAND_KEYS = frozenset({"command", "commands", "entrypoint", "shell", "script"})


def build_execution_task(
    work_order: Mapping[str, object],
    run_record: Mapping[str, object],
    execution_profile_id: str,
    *,
    retry_of_run_id: str | None = None,
) -> ExecutionTask:
    forbidden = _FORBIDDEN_COMMAND_KEYS.intersection(work_order)
    if forbidden:
        raise ExecutionContractError("WORK_ORDER_ARBITRARY_COMMAND_PROHIBITED:" + ",".join(sorted(forbidden)))

    approval_state = str(work_order.get("state") or work_order.get("approval_state") or "")
    if approval_state not in APPROVED_WORK_ORDER_STATES:
        raise ExecutionContractError("WORK_ORDER_NOT_APPROVED_FOR_EXECUTION")

    work_order_id = str(work_order.get("work_order_id") or "")
    if not work_order_id:
        raise ExecutionContractError("WORK_ORDER_ID_REQUIRED")
    if str(run_record.get("work_order_id") or "") != work_order_id:
        raise ExecutionContractError("RUN_WORK_ORDER_ID_MISMATCH")
    if str(run_record.get("state") or "") != "DISPATCHED_AWAITING_ACK":
        raise ExecutionContractError("RUN_NOT_DISPATCHED_AWAITING_ACK")

    run_id = str(run_record.get("run_id") or "")
    persona = str(run_record.get("responsible_persona") or "")
    exact_target = str(run_record.get("exact_target_commit") or run_record.get("exact_base_commit") or "")
    if not run_id or not persona:
        raise ExecutionContractError("RUN_IDENTITY_INCOMPLETE")

    profile = get_execution_profile(execution_profile_id)
    if persona not in profile.allowed_personas:
        raise ExecutionContractError("PROFILE_PERSONA_NOT_ALLOWED")

    digest = sha256((work_order_id + "\n" + run_id + "\n" + exact_target + "\n" + profile.execution_profile_id + "\n" + profile.profile_sha256 + "\n" + (retry_of_run_id or "")).encode("utf-8")).hexdigest()[:24]
    task = ExecutionTask(
        task_id=f"TASK-{digest}",
        run_id=run_id,
        work_order_id=work_order_id,
        responsible_persona=persona,
        exact_target_commit=exact_target,
        execution_profile_id=profile.execution_profile_id,
        execution_profile_sha256=profile.profile_sha256,
        required_capability=profile.required_capability,
        required_permission_level=profile.minimum_permission_level,
        retry_of_run_id=retry_of_run_id,
    )
    task.validate()
    return task
