from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
import json
from typing import Mapping


APPROVED_WORK_ORDER_STATES = frozenset({
    "OWNER_APPROVED_READY_FOR_EXECUTION",
    "OWNER_APPROVED_FOR_BOUNDED_ENGINEERING",
})


class ExecutionContractError(RuntimeError):
    """Fail-closed T19 execution contract violation."""


@dataclass(frozen=True)
class ExecutionProfile:
    execution_profile_id: str
    version: str
    allowed_personas: tuple[str, ...]
    required_capability: str
    minimum_permission_level: int
    timeout_seconds: int
    network_policy: str
    filesystem_policy: str
    commands: tuple[tuple[str, ...], ...]
    environment_allowlist: tuple[str, ...] = ()
    metadata: Mapping[str, object] = field(default_factory=dict)

    def canonical_payload(self) -> dict[str, object]:
        return {
            "execution_profile_id": self.execution_profile_id,
            "version": self.version,
            "allowed_personas": list(self.allowed_personas),
            "required_capability": self.required_capability,
            "minimum_permission_level": self.minimum_permission_level,
            "timeout_seconds": self.timeout_seconds,
            "network_policy": self.network_policy,
            "filesystem_policy": self.filesystem_policy,
            "commands": [list(step) for step in self.commands],
            "environment_allowlist": list(self.environment_allowlist),
            "metadata": dict(self.metadata),
        }

    @property
    def profile_sha256(self) -> str:
        payload = json.dumps(
            self.canonical_payload(),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return sha256(payload).hexdigest()

    def validate(self) -> None:
        if not self.execution_profile_id:
            raise ExecutionContractError("EXECUTION_PROFILE_ID_REQUIRED")
        if not self.version:
            raise ExecutionContractError("EXECUTION_PROFILE_VERSION_REQUIRED")
        if not self.allowed_personas:
            raise ExecutionContractError("EXECUTION_PROFILE_PERSONA_REQUIRED")
        if not self.required_capability:
            raise ExecutionContractError("EXECUTION_PROFILE_CAPABILITY_REQUIRED")
        if self.minimum_permission_level < 0:
            raise ExecutionContractError("EXECUTION_PROFILE_PERMISSION_INVALID")
        if self.timeout_seconds <= 0:
            raise ExecutionContractError("EXECUTION_PROFILE_TIMEOUT_INVALID")
        if not self.commands:
            raise ExecutionContractError("EXECUTION_PROFILE_COMMANDS_REQUIRED")
        for step in self.commands:
            if not step or not all(isinstance(part, str) and part for part in step):
                raise ExecutionContractError("EXECUTION_PROFILE_COMMAND_INVALID")


@dataclass(frozen=True)
class WorkerIdentity:
    worker_id: str
    worker_type: str
    runtime_version: str
    host_identity: str
    capabilities: tuple[str, ...]
    authorized_personas: tuple[str, ...]
    permission_level: int
    max_concurrency: int = 1

    def validate(self) -> None:
        if not self.worker_id or not self.worker_type or not self.runtime_version or not self.host_identity:
            raise ExecutionContractError("WORKER_IDENTITY_INCOMPLETE")
        if self.permission_level < 0:
            raise ExecutionContractError("WORKER_PERMISSION_INVALID")
        if self.max_concurrency <= 0:
            raise ExecutionContractError("WORKER_CONCURRENCY_INVALID")


@dataclass(frozen=True)
class ExecutionTask:
    task_id: str
    run_id: str
    work_order_id: str
    responsible_persona: str
    exact_target_commit: str
    execution_profile_id: str
    execution_profile_sha256: str
    required_capability: str
    required_permission_level: int
    retry_of_run_id: str | None = None

    def validate(self) -> None:
        if not self.task_id or not self.run_id or not self.work_order_id:
            raise ExecutionContractError("TASK_IDENTITY_INCOMPLETE")
        if len(self.exact_target_commit) != 40 or any(c not in "0123456789abcdef" for c in self.exact_target_commit):
            raise ExecutionContractError("TASK_EXACT_TARGET_INVALID")
        if len(self.execution_profile_sha256) != 64 or any(c not in "0123456789abcdef" for c in self.execution_profile_sha256):
            raise ExecutionContractError("TASK_PROFILE_SHA256_INVALID")
        if self.required_permission_level < 0:
            raise ExecutionContractError("TASK_PERMISSION_INVALID")


@dataclass(frozen=True)
class ClaimedTask:
    task: ExecutionTask
    worker_id: str
    lease_epoch: int

    def validate(self) -> None:
        self.task.validate()
        if not self.worker_id:
            raise ExecutionContractError("CLAIM_WORKER_REQUIRED")
        if self.lease_epoch <= 0:
            raise ExecutionContractError("CLAIM_LEASE_EPOCH_INVALID")


def require_worker_authorized(worker: WorkerIdentity, task: ExecutionTask, profile: ExecutionProfile) -> None:
    worker.validate()
    task.validate()
    profile.validate()
    if task.execution_profile_id != profile.execution_profile_id:
        raise ExecutionContractError("TASK_PROFILE_ID_MISMATCH")
    if task.execution_profile_sha256 != profile.profile_sha256:
        raise ExecutionContractError("TASK_PROFILE_HASH_MISMATCH")
    if task.responsible_persona not in profile.allowed_personas:
        raise ExecutionContractError("PROFILE_PERSONA_NOT_ALLOWED")
    if task.responsible_persona not in worker.authorized_personas:
        raise ExecutionContractError("WORKER_PERSONA_NOT_AUTHORIZED")
    if task.required_capability != profile.required_capability:
        raise ExecutionContractError("TASK_PROFILE_CAPABILITY_MISMATCH")
    if task.required_capability not in worker.capabilities:
        raise ExecutionContractError("WORKER_CAPABILITY_NOT_AUTHORIZED")
    if task.required_permission_level != profile.minimum_permission_level:
        raise ExecutionContractError("TASK_PROFILE_PERMISSION_MISMATCH")
    if worker.permission_level < task.required_permission_level:
        raise ExecutionContractError("WORKER_PERMISSION_INSUFFICIENT")
