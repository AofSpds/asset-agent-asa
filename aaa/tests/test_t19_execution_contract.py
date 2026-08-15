from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC = REPO_ROOT / "aaa" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aaa.execution.contracts import ClaimedTask, ExecutionContractError, WorkerIdentity, require_worker_authorized
from aaa.execution.dispatcher import build_execution_task
from aaa.execution.profiles import VALIDATION_EXACT_GIT_V0_1, get_execution_profile
from aaa.execution.worker import WorkerRuntime
from aaa.ops.operational_service import OperationalReadService


class FakeBackend:
    def __init__(self, claim: ClaimedTask | None):
        self.claim_value = claim
        self.events: list[object] = []
        self.completed: dict[str, object] | None = None
    def claim(self, worker):
        self.events.append(("claim", worker.worker_id)); value = self.claim_value; self.claim_value = None; return value
    def acknowledge(self, claim): self.events.append(("ack", claim.lease_epoch))
    def start(self, claim, ttl_seconds): self.events.append(("start", claim.lease_epoch, ttl_seconds))
    def heartbeat(self, claim, ttl_seconds): self.events.append(("heartbeat", claim.lease_epoch, ttl_seconds))
    def complete(self, claim, **kwargs): self.events.append(("complete", claim.lease_epoch, kwargs["verdict"])); self.completed = dict(kwargs)


def approved_work_order(**extra):
    value = {"work_order_id": "WO-T19-TEST", "state": "OWNER_APPROVED_READY_FOR_EXECUTION"}; value.update(extra); return value

def dispatched_run(**extra):
    value = {"run_id": "RUN-T19-TEST", "work_order_id": "WO-T19-TEST", "responsible_persona": "SEMI-VALIDATION-AUDITOR", "state": "DISPATCHED_AWAITING_ACK", "exact_target_commit": "1" * 40}; value.update(extra); return value

def worker_identity(**extra):
    values = {"worker_id": "worker-test", "worker_type": "CI_VALIDATION_WORKER", "runtime_version": "v0.1", "host_identity": "test-host", "capabilities": ("INDEPENDENT_VALIDATION",), "authorized_personas": ("SEMI-VALIDATION-AUDITOR",), "permission_level": 1, "max_concurrency": 1}; values.update(extra); return WorkerIdentity(**values)


class T19ExecutionContractTests(unittest.TestCase):
    def test_0004_declares_dispatch_worker_claim_ack_start_heartbeat_and_atomic_completion(self):
        sql = (REPO_ROOT / "aaa" / "db" / "migrations" / "0004_execution_dispatcher_worker_runtime.sql").read_text(encoding="utf-8")
        for token in ("aaa_ops.execution_profiles", "aaa_ops.workers", "aaa_ops.execution_tasks", "aaa_ops.materialize_execution_task", "WORK_ORDER_NOT_APPROVED_FOR_EXECUTION", "FOR UPDATE OF t SKIP LOCKED", "aaa_ops.ack_execution_task", "aaa_ops.start_execution_task", "aaa_ops.heartbeat_execution_task", "aaa_ops.complete_execution_task_atomic", "TASK_NOT_RUNNING_UNDER_CURRENT_LEASE", "execution_task_projection"):
            self.assertIn(token, sql)

    def test_0005_requires_current_unexpired_lease_before_heartbeat_renewal(self):
        sql = (REPO_ROOT / "aaa" / "db" / "migrations" / "0005_t19_lease_heartbeat_fail_closed.sql").read_text(encoding="utf-8")
        self.assertIn("lease_expires_at IS NOT NULL", sql)
        self.assertIn("lease_expires_at >= transaction_timestamp()", sql)
        self.assertIn("STALE_OR_INVALID_LEASE", sql)
        self.assertIn("FOR UPDATE", sql)
        self.assertNotIn("CREATE TABLE", sql)

    def test_profile_is_code_owned_hash_bound_and_shell_free(self):
        profile = get_execution_profile("AAA_VALIDATION_EXACT_GIT_V0_1")
        self.assertEqual(profile, VALIDATION_EXACT_GIT_V0_1)
        self.assertEqual(len(profile.profile_sha256), 64)
        self.assertEqual(profile.network_policy, "DENY")
        self.assertEqual(profile.filesystem_policy, "READ_ONLY_EXACT_CHECKOUT")
        self.assertNotIn("shell", profile.canonical_payload())

    def test_unapproved_work_order_cannot_materialize_task(self):
        with self.assertRaisesRegex(ExecutionContractError, "WORK_ORDER_NOT_APPROVED"):
            build_execution_task({"work_order_id": "WO-T19-TEST", "state": "DRAFT"}, dispatched_run(), "AAA_VALIDATION_EXACT_GIT_V0_1")

    def test_work_order_cannot_supply_arbitrary_command(self):
        with self.assertRaisesRegex(ExecutionContractError, "ARBITRARY_COMMAND_PROHIBITED"):
            build_execution_task(approved_work_order(command="rm -rf /"), dispatched_run(), "AAA_VALIDATION_EXACT_GIT_V0_1")

    def test_dispatch_task_contains_profile_identity_not_command(self):
        task = build_execution_task(approved_work_order(), dispatched_run(), "AAA_VALIDATION_EXACT_GIT_V0_1")
        self.assertEqual(task.execution_profile_id, VALIDATION_EXACT_GIT_V0_1.execution_profile_id)
        self.assertEqual(task.execution_profile_sha256, VALIDATION_EXACT_GIT_V0_1.profile_sha256)
        self.assertFalse(hasattr(task, "command"))

    def test_worker_capability_and_persona_are_enforced(self):
        task = build_execution_task(approved_work_order(), dispatched_run(), "AAA_VALIDATION_EXACT_GIT_V0_1")
        with self.assertRaisesRegex(ExecutionContractError, "WORKER_CAPABILITY"):
            require_worker_authorized(worker_identity(capabilities=("OTHER",)), task, VALIDATION_EXACT_GIT_V0_1)
        with self.assertRaisesRegex(ExecutionContractError, "WORKER_PERSONA"):
            require_worker_authorized(worker_identity(authorized_personas=("SEMI-CONTROL-ARCHITECT",)), task, VALIDATION_EXACT_GIT_V0_1)

    def test_worker_runtime_records_ack_start_heartbeat_and_terminal_result(self):
        task = build_execution_task(approved_work_order(), dispatched_run(), "AAA_VALIDATION_EXACT_GIT_V0_1")
        claim = ClaimedTask(task=task, worker_id="worker-test", lease_epoch=7)
        backend = FakeBackend(claim); commands_seen = []
        def runner(command, **kwargs):
            self.assertFalse(kwargs["shell"]); commands_seen.append(list(command)); return subprocess.CompletedProcess(command, 0, stdout="ok", stderr="")
        with tempfile.TemporaryDirectory() as tmp:
            runtime = WorkerRuntime(worker=worker_identity(), backend=backend, repo_root=REPO_ROOT, output_dir=Path(tmp), git_head_resolver=lambda _: "1" * 40, command_runner=runner)
            result = runtime.run_once()
        self.assertEqual(result["verdict"], "PASS")
        self.assertEqual(commands_seen, [list(VALIDATION_EXACT_GIT_V0_1.commands[0])])
        names = [event[0] for event in backend.events]
        self.assertEqual(names[0:3], ["claim", "ack", "start"]); self.assertIn("heartbeat", names); self.assertEqual(names[-1], "complete")
        self.assertFalse(backend.completed["metadata"]["canonical_output"])

    def test_long_command_timeout_is_strictly_inside_governed_execution_lease(self):
        task = build_execution_task(approved_work_order(), dispatched_run(), "AAA_VALIDATION_EXACT_GIT_V0_1")
        claim = ClaimedTask(task=task, worker_id="worker-test", lease_epoch=11)
        backend = FakeBackend(claim)
        def runner(command, **kwargs):
            return subprocess.CompletedProcess(command, 0, stdout="ok", stderr="")
        with tempfile.TemporaryDirectory() as tmp:
            runtime = WorkerRuntime(
                worker=worker_identity(), backend=backend, repo_root=REPO_ROOT,
                output_dir=Path(tmp), lease_ttl_seconds=300,
                lease_timeout_margin_seconds=60,
                git_head_resolver=lambda _: "1" * 40, command_runner=runner,
            )
            result = runtime.run_once()
        expected_ttl = VALIDATION_EXACT_GIT_V0_1.timeout_seconds + 60
        self.assertEqual(expected_ttl, 1860)
        self.assertEqual(result["governed_execution_lease_ttl_seconds"], expected_ttl)
        start_events = [event for event in backend.events if event[0] == "start"]
        heartbeat_events = [event for event in backend.events if event[0] == "heartbeat"]
        self.assertEqual(start_events, [("start", 11, expected_ttl)])
        self.assertGreaterEqual(len(heartbeat_events), 2)
        self.assertTrue(all(event[2] == expected_ttl for event in heartbeat_events))
        self.assertGreater(expected_ttl, VALIDATION_EXACT_GIT_V0_1.timeout_seconds)

    def test_lease_timeout_margin_must_be_positive(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ExecutionContractError, "LEASE_TIMEOUT_MARGIN_TOO_SMALL"):
                WorkerRuntime(
                    worker=worker_identity(), backend=FakeBackend(None), repo_root=REPO_ROOT,
                    output_dir=Path(tmp), lease_timeout_margin_seconds=0,
                )

    def test_exact_target_mismatch_blocks_before_ack_or_command(self):
        task = build_execution_task(approved_work_order(), dispatched_run(), "AAA_VALIDATION_EXACT_GIT_V0_1")
        backend = FakeBackend(ClaimedTask(task=task, worker_id="worker-test", lease_epoch=1)); invoked = []
        def runner(*args, **kwargs): invoked.append(True); raise AssertionError("command must not run")
        with tempfile.TemporaryDirectory() as tmp:
            runtime = WorkerRuntime(worker=worker_identity(), backend=backend, repo_root=REPO_ROOT, output_dir=Path(tmp), git_head_resolver=lambda _: "2" * 40, command_runner=runner)
            with self.assertRaisesRegex(ExecutionContractError, "EXACT_TARGET_MISMATCH"): runtime.run_once()
        self.assertEqual(backend.events, [("claim", "worker-test")]); self.assertEqual(invoked, [])

    def test_no_task_does_not_fabricate_execution_evidence(self):
        backend = FakeBackend(None)
        with tempfile.TemporaryDirectory() as tmp:
            runtime = WorkerRuntime(worker=worker_identity(), backend=backend, repo_root=REPO_ROOT, output_dir=Path(tmp), git_head_resolver=lambda _: "1" * 40)
            self.assertEqual(runtime.run_once()["status"], "NO_TASK")
        self.assertEqual(backend.events, [("claim", "worker-test")])

    def test_cli_api_and_owner_console_have_worker_task_read_surfaces(self):
        class Reader:
            def list_workers(self): return [{"worker_id": "w", "enabled": True}]
            def list_tasks(self): return [{"task_id": "t", "effective_task_state": "AVAILABLE"}]
        service = OperationalReadService(REPO_ROOT, execution_reader=Reader())
        self.assertEqual(service.workers()[0]["worker_id"], "w"); self.assertEqual(service.tasks()[0]["task_id"], "t")
        cli = (REPO_ROOT / "aaa" / "src" / "aaa" / "cli" / "main.py").read_text(encoding="utf-8")
        server = (REPO_ROOT / "aaa" / "src" / "aaa" / "api" / "server.py").read_text(encoding="utf-8")
        console = (REPO_ROOT / "aaa" / "web" / "src" / "App.tsx").read_text(encoding="utf-8")
        self.assertIn('sub.add_parser("workers"', cli); self.assertIn('sub.add_parser("tasks"', cli)
        self.assertIn('"/api/aaa/workers"', server); self.assertIn('"/api/aaa/tasks"', server)
        self.assertIn("No connected worker evidence", console); self.assertIn("no worker liveness inferred", console)

    def test_existing_validation_targets_are_pinned_in_owner_contract(self):
        contract = (REPO_ROOT / "control" / "aaa" / "architecture" / "AAA-T19-EXECUTION-DISPATCHER-WORKER-ARCHITECTURE-REVIEW_v0.2_OWNER-APPROVED.yaml").read_text(encoding="utf-8")
        for target in ("80378610f9ac9e688c52417f0416e01c057400a7", "30fdb278c218b24e44d66eb5f47935a196dc4f8c", "59c9baf3a24b1cf7542a3643c296711c37d72c3c"):
            self.assertIn(target, contract)


if __name__ == "__main__": unittest.main()
