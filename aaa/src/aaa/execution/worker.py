from __future__ import annotations

from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
from typing import Callable, Protocol

from aaa.execution.contracts import ClaimedTask, ExecutionContractError, WorkerIdentity, require_worker_authorized
from aaa.execution.profiles import get_execution_profile


class ExecutionBackend(Protocol):
    def claim(self, worker: WorkerIdentity) -> ClaimedTask | None: ...
    def acknowledge(self, claim: ClaimedTask) -> None: ...
    def start(self, claim: ClaimedTask, ttl_seconds: int) -> None: ...
    def heartbeat(self, claim: ClaimedTask, ttl_seconds: int) -> None: ...
    def complete(self, claim: ClaimedTask, *, result_id: str, verdict: str, artifact_locator: str, artifact_sha256: str, artifact_byte_size: int, metadata: dict[str, object]) -> None: ...


def _resolve_git_head(repo_root: Path) -> str:
    completed = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo_root, check=True, capture_output=True, text=True, shell=False)
    return completed.stdout.strip()


class WorkerRuntime:
    """Bounded T19 worker. Commands come only from the code-owned profile registry."""

    def __init__(
        self,
        *,
        worker: WorkerIdentity,
        backend: ExecutionBackend,
        repo_root: Path,
        output_dir: Path,
        lease_ttl_seconds: int = 300,
        lease_timeout_margin_seconds: int = 60,
        git_head_resolver: Callable[[Path], str] = _resolve_git_head,
        command_runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
    ):
        worker.validate()
        if lease_ttl_seconds < 60:
            raise ExecutionContractError("LEASE_TTL_TOO_SMALL")
        if lease_timeout_margin_seconds < 1:
            raise ExecutionContractError("LEASE_TIMEOUT_MARGIN_TOO_SMALL")
        self.worker = worker
        self.backend = backend
        self.repo_root = repo_root.resolve()
        self.output_dir = output_dir.resolve()
        self.lease_ttl_seconds = lease_ttl_seconds
        self.lease_timeout_margin_seconds = lease_timeout_margin_seconds
        self.git_head_resolver = git_head_resolver
        self.command_runner = command_runner

    def _governed_execution_ttl(self, profile_timeout_seconds: int) -> int:
        """Guarantee one allowlisted command cannot outlive its current lease.

        Claim leases remain short. Immediately before execution starts, the Run lease
        is extended to at least the profile command timeout plus a governed safety
        margin. Every pre/post-command heartbeat uses the same bounded TTL. Database
        heartbeat renewal still fails closed when the pre-existing lease has expired.
        """
        return max(
            self.lease_ttl_seconds,
            int(profile_timeout_seconds) + self.lease_timeout_margin_seconds,
        )

    def run_once(self) -> dict[str, object]:
        claim = self.backend.claim(self.worker)
        if claim is None:
            return {"status": "NO_TASK", "worker_id": self.worker.worker_id}
        claim.validate()
        profile = get_execution_profile(claim.task.execution_profile_id)
        require_worker_authorized(self.worker, claim.task, profile)

        observed_head = self.git_head_resolver(self.repo_root)
        if observed_head != claim.task.exact_target_commit:
            raise ExecutionContractError(f"EXACT_TARGET_MISMATCH:{observed_head}:{claim.task.exact_target_commit}")

        execution_ttl_seconds = self._governed_execution_ttl(profile.timeout_seconds)
        self.backend.acknowledge(claim)
        self.backend.start(claim, execution_ttl_seconds)
        allowed_env = {key: value for key, value in os.environ.items() if key in profile.environment_allowlist}

        steps: list[dict[str, object]] = []
        verdict = "PASS"
        for index, command in enumerate(profile.commands, start=1):
            self.backend.heartbeat(claim, execution_ttl_seconds)
            try:
                completed = self.command_runner(list(command), cwd=self.repo_root, env=allowed_env, capture_output=True, text=True, timeout=profile.timeout_seconds, shell=False, check=False)
                returncode = int(completed.returncode)
                stdout = completed.stdout or ""
                stderr = completed.stderr or ""
            except subprocess.TimeoutExpired as exc:
                returncode = 124
                stdout = exc.stdout or ""
                stderr = exc.stderr or "EXECUTION_PROFILE_TIMEOUT"
            steps.append({"index": index, "command": list(command), "returncode": returncode, "stdout": stdout, "stderr": stderr})
            self.backend.heartbeat(claim, execution_ttl_seconds)
            if returncode != 0:
                verdict = "FAIL"
                break

        result_id = f"RESULT-{claim.task.run_id}-LEASE-{claim.lease_epoch}"
        result_payload = {
            "result_id": result_id,
            "run_id": claim.task.run_id,
            "work_order_id": claim.task.work_order_id,
            "worker_id": self.worker.worker_id,
            "lease_epoch": claim.lease_epoch,
            "execution_profile_id": profile.execution_profile_id,
            "execution_profile_sha256": profile.profile_sha256,
            "exact_target_commit": claim.task.exact_target_commit,
            "governed_execution_lease_ttl_seconds": execution_ttl_seconds,
            "verdict": verdict,
            "canonical_output": False,
            "steps": steps,
        }
        payload_bytes = (json.dumps(result_payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
        digest = sha256(payload_bytes).hexdigest()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        result_path = self.output_dir / f"{result_id}.json"
        result_path.write_bytes(payload_bytes)

        self.backend.complete(
            claim,
            result_id=result_id,
            verdict=verdict,
            artifact_locator=str(result_path),
            artifact_sha256=digest,
            artifact_byte_size=len(payload_bytes),
            metadata={
                "canonical_output": False,
                "execution_profile_id": profile.execution_profile_id,
                "execution_profile_sha256": profile.profile_sha256,
                "governed_execution_lease_ttl_seconds": execution_ttl_seconds,
            },
        )
        return {
            "status": "COMPLETED",
            "worker_id": self.worker.worker_id,
            "run_id": claim.task.run_id,
            "result_id": result_id,
            "verdict": verdict,
            "artifact_locator": str(result_path),
            "artifact_sha256": digest,
            "artifact_byte_size": len(payload_bytes),
            "governed_execution_lease_ttl_seconds": execution_ttl_seconds,
        }
