from __future__ import annotations

import json
import os
import subprocess
from typing import Mapping

from aaa.execution.contracts import ClaimedTask, ExecutionContractError, ExecutionProfile, ExecutionTask, WorkerIdentity


class PsqlExecutionBackend:
    """Concrete PostgreSQL T19 backend using psql/libpq environment configuration."""

    def __init__(self, *, database: str, psql_binary: str = "psql", env: Mapping[str, str] | None = None, lease_ttl_seconds: int = 300):
        if not database:
            raise ExecutionContractError("POSTGRES_DATABASE_REQUIRED")
        if lease_ttl_seconds < 60:
            raise ExecutionContractError("LEASE_TTL_TOO_SMALL")
        self.database = database
        self.psql_binary = psql_binary
        self.env = dict(os.environ if env is None else env)
        self.lease_ttl_seconds = lease_ttl_seconds

    def _query(self, sql: str, variables: Mapping[str, object] | None = None) -> str:
        args = [self.psql_binary, "-X", "-v", "ON_ERROR_STOP=1", "-At", "-F", "\t", "-d", self.database]
        for key, value in (variables or {}).items():
            args.extend(["-v", f"{key}={value}"])
        args.extend(["-c", sql])
        completed = subprocess.run(args, env=self.env, capture_output=True, text=True, shell=False, check=False)
        if completed.returncode != 0:
            raise ExecutionContractError("POSTGRES_EXECUTION_BACKEND_ERROR:" + (completed.stderr or "").strip())
        return (completed.stdout or "").strip()

    def register_worker(self, worker: WorkerIdentity) -> None:
        worker.validate()
        self._query("""
            INSERT INTO aaa_ops.workers (worker_id, worker_type, runtime_version, host_identity, capabilities, authorized_personas, permission_level, max_concurrency, enabled, last_seen_at)
            VALUES (:'worker_id', :'worker_type', :'runtime_version', :'host_identity', ARRAY(SELECT jsonb_array_elements_text(:'capabilities'::jsonb)), ARRAY(SELECT jsonb_array_elements_text(:'personas'::jsonb)), :permission_level, :max_concurrency, true, transaction_timestamp())
            ON CONFLICT (worker_id) DO UPDATE SET worker_type=EXCLUDED.worker_type, runtime_version=EXCLUDED.runtime_version, host_identity=EXCLUDED.host_identity, capabilities=EXCLUDED.capabilities, authorized_personas=EXCLUDED.authorized_personas, permission_level=EXCLUDED.permission_level, max_concurrency=EXCLUDED.max_concurrency, last_seen_at=transaction_timestamp();
        """, {"worker_id": worker.worker_id, "worker_type": worker.worker_type, "runtime_version": worker.runtime_version, "host_identity": worker.host_identity, "capabilities": json.dumps(list(worker.capabilities), separators=(",", ":")), "personas": json.dumps(list(worker.authorized_personas), separators=(",", ":")), "permission_level": worker.permission_level, "max_concurrency": worker.max_concurrency})

    def register_profile(self, profile: ExecutionProfile, git_identity: str) -> None:
        profile.validate()
        self._query("""
            INSERT INTO aaa_ops.execution_profiles (execution_profile_id, version, git_identity, profile_sha256, allowed_personas, required_capability, minimum_permission_level, timeout_seconds, network_policy, filesystem_policy, metadata_jsonb)
            VALUES (:'profile_id', :'version', :'git_identity', :'profile_sha256', ARRAY(SELECT jsonb_array_elements_text(:'personas'::jsonb)), :'capability', :permission_level, :timeout_seconds, :'network_policy', :'filesystem_policy', :'metadata'::jsonb)
            ON CONFLICT (execution_profile_id) DO UPDATE SET version=EXCLUDED.version, git_identity=EXCLUDED.git_identity, profile_sha256=EXCLUDED.profile_sha256, allowed_personas=EXCLUDED.allowed_personas, required_capability=EXCLUDED.required_capability, minimum_permission_level=EXCLUDED.minimum_permission_level, timeout_seconds=EXCLUDED.timeout_seconds, network_policy=EXCLUDED.network_policy, filesystem_policy=EXCLUDED.filesystem_policy, metadata_jsonb=EXCLUDED.metadata_jsonb;
        """, {"profile_id": profile.execution_profile_id, "version": profile.version, "git_identity": git_identity, "profile_sha256": profile.profile_sha256, "personas": json.dumps(list(profile.allowed_personas), separators=(",", ":")), "capability": profile.required_capability, "permission_level": profile.minimum_permission_level, "timeout_seconds": profile.timeout_seconds, "network_policy": profile.network_policy, "filesystem_policy": profile.filesystem_policy, "metadata": json.dumps(dict(profile.metadata), sort_keys=True, separators=(",", ":"))})

    def materialize(self, task: ExecutionTask) -> str:
        task.validate()
        return self._query("SELECT aaa_ops.materialize_execution_task(:'task_id', :'run_id', :'profile_id', :'profile_sha256', :'exact_target', :'capability', :permission_level, NULLIF(:'retry_of_run_id',''));", {"task_id": task.task_id, "run_id": task.run_id, "profile_id": task.execution_profile_id, "profile_sha256": task.execution_profile_sha256, "exact_target": task.exact_target_commit, "capability": task.required_capability, "permission_level": task.required_permission_level, "retry_of_run_id": task.retry_of_run_id or ""})

    def claim(self, worker: WorkerIdentity) -> ClaimedTask | None:
        worker.validate()
        output = self._query("SELECT task_id, run_id, lease_epoch, execution_profile_id, execution_profile_sha256, exact_target_commit, work_order_id, responsible_persona, required_capability, required_permission_level FROM aaa_ops.claim_next_execution_task(:'worker_id', :ttl_seconds);", {"worker_id": worker.worker_id, "ttl_seconds": self.lease_ttl_seconds})
        if not output:
            return None
        fields = output.split("\t")
        if len(fields) != 10:
            raise ExecutionContractError("POSTGRES_CLAIM_PROJECTION_INVALID")
        task_id, run_id, lease_epoch, profile_id, profile_sha256, exact_target, work_order_id, persona, capability, permission_level = fields
        task = ExecutionTask(task_id=task_id, run_id=run_id, work_order_id=work_order_id, responsible_persona=persona, exact_target_commit=exact_target, execution_profile_id=profile_id, execution_profile_sha256=profile_sha256, required_capability=capability, required_permission_level=int(permission_level))
        return ClaimedTask(task=task, worker_id=worker.worker_id, lease_epoch=int(lease_epoch))

    def acknowledge(self, claim: ClaimedTask) -> None:
        self._query("SELECT aaa_ops.ack_execution_task(:'task_id', :'worker_id', :lease_epoch);", {"task_id": claim.task.task_id, "worker_id": claim.worker_id, "lease_epoch": claim.lease_epoch})

    def start(self, claim: ClaimedTask, ttl_seconds: int) -> None:
        self._query("SELECT aaa_ops.start_execution_task(:'task_id', :'worker_id', :lease_epoch, :ttl_seconds);", {"task_id": claim.task.task_id, "worker_id": claim.worker_id, "lease_epoch": claim.lease_epoch, "ttl_seconds": ttl_seconds})

    def heartbeat(self, claim: ClaimedTask, ttl_seconds: int) -> None:
        self._query("SELECT aaa_ops.heartbeat_execution_task(:'task_id', :'worker_id', :lease_epoch, :ttl_seconds);", {"task_id": claim.task.task_id, "worker_id": claim.worker_id, "lease_epoch": claim.lease_epoch, "ttl_seconds": ttl_seconds})

    def complete(self, claim: ClaimedTask, *, result_id: str, verdict: str, artifact_locator: str, artifact_sha256: str, artifact_byte_size: int, metadata: dict[str, object]) -> None:
        self._query("SELECT aaa_ops.complete_execution_task_atomic(:'task_id', :'worker_id', :lease_epoch, :'result_id', :'verdict', :'artifact_locator', :'artifact_sha256', :artifact_byte_size, :'metadata'::jsonb);", {"task_id": claim.task.task_id, "worker_id": claim.worker_id, "lease_epoch": claim.lease_epoch, "result_id": result_id, "verdict": verdict, "artifact_locator": artifact_locator, "artifact_sha256": artifact_sha256, "artifact_byte_size": artifact_byte_size, "metadata": json.dumps(metadata, sort_keys=True, separators=(",", ":"))})

    def list_workers(self) -> list[dict[str, object]]:
        output = self._query("SELECT row_to_json(x) FROM (SELECT worker_id, worker_type, runtime_version, host_identity, capabilities, authorized_personas, permission_level, max_concurrency, enabled, last_seen_at FROM aaa_ops.workers ORDER BY worker_id) x;")
        return [json.loads(line) for line in output.splitlines() if line]

    def list_tasks(self) -> list[dict[str, object]]:
        output = self._query("SELECT row_to_json(x) FROM (SELECT task_id, run_id, execution_profile_id, required_persona, required_capability, required_permission_level, state, effective_task_state, claimed_by, lease_epoch, acknowledged_at_db, started_at_db, last_heartbeat_at, lease_expires_at, terminal_result_id FROM aaa_ops.execution_task_projection ORDER BY materialized_at_db, task_id) x;")
        return [json.loads(line) for line in output.splitlines() if line]
