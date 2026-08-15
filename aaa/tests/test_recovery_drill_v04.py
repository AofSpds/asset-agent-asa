from __future__ import annotations

import os
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "aaa" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aaa.agents.journal import AgentRunJournal
from aaa.agents.runtime import PermissionLevel, RunStatus, WorkOrderIdentity, create_run, transition_run
from aaa.core.identity import ExactBaseIdentity
from aaa.recovery.audit import audit_recovery, RecoverySnapshot, StateRecoveryObservation
from aaa.recovery.drill import (
    DrillEvidence,
    evidence_manifest,
    inspect_journal,
    inspect_lock,
    interrupt_worker,
    local_content_identity,
    observe_local_replicas,
    process_alive,
    quarantine_stale_lock,
    start_interruptible_worker,
)


BASE = ExactBaseIdentity("AofSpds/asset-agent-asa", "1" * 40)
WO = WorkOrderIdentity("WO-DRILL", "v0.1", "2" * 64)


class RecoveryDrillV04Tests(unittest.TestCase):
    def test_actual_local_process_interruption_creates_no_success_result(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            proc, handle = start_interruptible_worker(Path(tmp), timeout_seconds=30)
            self.assertTrue(process_alive(handle.pid))
            evidence = interrupt_worker(proc, handle)
            self.assertEqual(evidence.status, "PASS")
            self.assertFalse(Path(handle.result_path).exists())
            self.assertFalse(process_alive(handle.pid))
            self.assertFalse(evidence.real_cloud_infrastructure_exercised)
            self.assertFalse(evidence.canonical_mutation)

    def test_stale_lock_is_detected_and_quarantined_not_silently_deleted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            lock = Path(tmp) / "run.lock"
            lock.write_text("999999999", encoding="utf-8")
            inspection = inspect_lock(lock)
            self.assertEqual(inspection.status, "STALE")
            quarantined = quarantine_stale_lock(lock)
            self.assertFalse(lock.exists())
            self.assertTrue(quarantined.exists())
            self.assertTrue(quarantined.name.endswith(".stale"))

    def test_active_lock_cannot_be_quarantined(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            lock = Path(tmp) / "run.lock"
            lock.write_text(str(os.getpid()), encoding="utf-8")
            self.assertEqual(inspect_lock(lock).status, "ACTIVE")
            with self.assertRaisesRegex(RuntimeError, "LOCK_NOT_STALE:ACTIVE"):
                quarantine_stale_lock(lock)

    def test_partial_journal_bytes_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "run.jsonl"
            path.write_text('{"event_type":"RUN_CREATED"', encoding="utf-8")
            inspection = inspect_journal(path)
            self.assertEqual(inspection.status, "BLOCKED_CORRUPT_OR_PARTIAL")

    def test_valid_journal_inspection_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "run.jsonl"
            journal = AgentRunJournal(path)
            created = create_run(
                run_id="R1",
                work_order_identity=WO,
                expected_base=BASE,
                observed_base=BASE,
                executor_role="ENGINEERING",
                permission_level=PermissionLevel.READ_ONLY,
            )
            journal.append(created, event_type="RUN_CREATED")
            journal.append(transition_run(created, RunStatus.RUNNING), event_type="RUN_STARTED")
            inspection = inspect_journal(path)
            self.assertEqual(inspection.status, "PASS")
            self.assertEqual(inspection.event_count, 2)

    def test_local_replica_loss_feeds_existing_fail_closed_recovery_audit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            primary = root / "primary.bin"
            secondary = root / "secondary.bin"
            primary.write_bytes(b"same-bytes")
            expected = local_content_identity(primary)
            observation = observe_local_replicas(
                artifact_id="A1",
                expected=expected,
                primary_path=primary,
                secondary_path=secondary,
            )
            report = audit_recovery(
                RecoverySnapshot(
                    artifacts=(observation,),
                    runs=(),
                    state=StateRecoveryObservation("a" * 64, "a" * 64, "b" * 40, "b" * 40),
                    llm_provider_available=False,
                    deterministic_core_available=True,
                )
            )
            self.assertEqual(report.status, "BLOCKED")
            self.assertIn("SECONDARY_ARTIFACT_MISSING", {row.code for row in report.findings})

    def test_replica_identity_mismatch_is_visible(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            primary = root / "primary.bin"
            secondary = root / "secondary.bin"
            primary.write_bytes(b"correct")
            secondary.write_bytes(b"wrong")
            expected = local_content_identity(primary)
            observation = observe_local_replicas(
                artifact_id="A1",
                expected=expected,
                primary_path=primary,
                secondary_path=secondary,
            )
            self.assertEqual(observation.observed_primary, expected)
            self.assertNotEqual(observation.observed_secondary, expected)

    def test_evidence_manifest_cannot_claim_real_cloud_or_canonical_mutation(self) -> None:
        evidence = DrillEvidence("LOCAL_TEST", "PASS", {"x": 1})
        first = evidence_manifest(evidence)
        second = evidence_manifest(evidence)
        self.assertEqual(first, second)
        self.assertFalse(first["real_cloud_infrastructure_exercised"])
        self.assertFalse(first["canonical_mutation"])
        self.assertRegex(first["manifest_sha256"], r"^[0-9a-f]{64}$")


if __name__ == "__main__":
    unittest.main()
