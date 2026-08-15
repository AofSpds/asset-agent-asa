from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "aaa" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aaa.agents.journal import AgentRunJournal, JournalIntegrityError
from aaa.agents.runtime import (
    AgentRunRecord,
    InvalidRunTransition,
    PermissionLevel,
    RunStatus,
    WorkOrderIdentity,
    create_run,
    recover_interrupted_run,
    transition_run,
)
from aaa.core.identity import ExactBaseIdentity


BASE = ExactBaseIdentity("AofSpds/asset-agent-asa", "1" * 40)
WO = WorkOrderIdentity("WO-AAA-T11", "v0.1", "2" * 64)


class AgentRuntimeV03Tests(unittest.TestCase):
    def _run(self) -> AgentRunRecord:
        return create_run(
            run_id="RUN-T11-001",
            work_order_identity=WO,
            expected_base=BASE,
            observed_base=BASE,
            executor_role="ENGINEERING",
            permission_level=PermissionLevel.ISOLATED_BRANCH_WRITE,
            branch="aaa-t11-agent-runtime-v0",
        )

    def test_exact_base_mismatch_fails_closed(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "STALE_BASE"):
            create_run(
                run_id="RUN-X",
                work_order_identity=WO,
                expected_base=BASE,
                observed_base=ExactBaseIdentity(BASE.repository, "3" * 40),
                executor_role="ENGINEERING",
                permission_level=PermissionLevel.READ_ONLY,
            )

    def test_l2_requires_isolated_branch(self) -> None:
        with self.assertRaisesRegex(ValueError, "isolated branch"):
            AgentRunRecord(
                run_id="RUN-X",
                work_order_identity=WO,
                exact_base_identity=BASE,
                executor_role="ENGINEERING",
                permission_level=PermissionLevel.ISOLATED_BRANCH_WRITE,
            )

    def test_run_identity_is_stable_across_state_transitions(self) -> None:
        created = self._run()
        running = transition_run(created, RunStatus.RUNNING)
        succeeded = transition_run(running, RunStatus.SUCCEEDED, result={"changed_files": ["a.py"], "tests": 10})
        self.assertEqual(created.immutable_run_sha256, running.immutable_run_sha256)
        self.assertEqual(running.immutable_run_sha256, succeeded.immutable_run_sha256)
        self.assertRegex(succeeded.result_sha256 or "", r"^[0-9a-f]{64}$")

    def test_terminal_state_is_immutable(self) -> None:
        running = transition_run(self._run(), RunStatus.RUNNING)
        failed = transition_run(running, RunStatus.FAILED, terminal_reason="TEST_FAILURE")
        with self.assertRaisesRegex(InvalidRunTransition, "TERMINAL_RUN_IMMUTABLE"):
            transition_run(failed, RunStatus.RUNNING)

    def test_restart_marks_running_run_blocked_not_success(self) -> None:
        running = transition_run(self._run(), RunStatus.RUNNING)
        recovered = recover_interrupted_run(running)
        self.assertEqual(recovered.status, RunStatus.BLOCKED)
        self.assertEqual(recovered.terminal_reason, "INTERRUPTED_RESTART")
        self.assertIsNone(recovered.result_sha256)

    def test_journal_hash_chain_and_idempotent_exact_reappend(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            journal = AgentRunJournal(Path(tmp) / "RUN-T11-001.jsonl")
            created = self._run()
            first = journal.append(created, event_type="RUN_CREATED")
            duplicate = journal.append(created, event_type="RUN_CREATED")
            self.assertEqual(first, duplicate)
            running = transition_run(created, RunStatus.RUNNING)
            second = journal.append(running, event_type="RUN_STARTED")
            self.assertEqual(second["previous_event_sha256"], first["event_sha256"])
            self.assertEqual(len(journal.read_events()), 2)
            self.assertEqual(journal.latest(), running)

    def test_journal_rejects_identity_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            journal = AgentRunJournal(Path(tmp) / "run.jsonl")
            original = self._run()
            journal.append(original, event_type="RUN_CREATED")
            drifted = create_run(
                run_id=original.run_id,
                work_order_identity=WorkOrderIdentity("WO-DIFFERENT", "v0.1", "4" * 64),
                expected_base=BASE,
                observed_base=BASE,
                executor_role=original.executor_role,
                permission_level=original.permission_level,
                branch=original.branch,
            )
            with self.assertRaisesRegex(JournalIntegrityError, "RUN_IDENTITY_DRIFT"):
                journal.append(drifted, event_type="RUN_STARTED")

    def test_journal_detects_tampering(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "run.jsonl"
            journal = AgentRunJournal(path)
            journal.append(self._run(), event_type="RUN_CREATED")
            row = json.loads(path.read_text(encoding="utf-8"))
            row["record"]["executor_role"] = "TAMPERED"
            path.write_text(json.dumps(row) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(JournalIntegrityError, "JOURNAL_EVENT_HASH_MISMATCH"):
                journal.read_events()


if __name__ == "__main__":
    unittest.main()
