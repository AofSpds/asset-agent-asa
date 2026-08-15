from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "aaa" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aaa.recovery.audit import (
    ArtifactRecoveryObservation,
    RecoverySnapshot,
    RunRecoveryObservation,
    StateRecoveryObservation,
    audit_recovery,
)
from aaa.storage.identity import ContentIdentity


GOOD = ContentIdentity("a" * 64, 100)
STATE = StateRecoveryObservation("b" * 64, "b" * 64, "c" * 40, "c" * 40)


def clean_snapshot(*, llm: bool = True) -> RecoverySnapshot:
    return RecoverySnapshot(
        artifacts=(ArtifactRecoveryObservation("A1", GOOD, GOOD, GOOD, True, True),),
        runs=(RunRecoveryObservation("R1", "SUCCEEDED", True, True),),
        state=STATE,
        llm_provider_available=llm,
        deterministic_core_available=True,
    )


class RecoveryV03Tests(unittest.TestCase):
    def test_clean_snapshot_passes_and_never_authorizes_canonical_write(self) -> None:
        report = audit_recovery(clean_snapshot())
        self.assertEqual(report.status, "PASS")
        self.assertTrue(report.safe_to_resume_noncanonical_work)
        self.assertFalse(report.canonical_mutation_allowed)
        self.assertRegex(report.report_sha256, r"^[0-9a-f]{64}$")

    def test_llm_off_survives_when_deterministic_core_is_available(self) -> None:
        report = audit_recovery(clean_snapshot(llm=False))
        self.assertEqual(report.status, "PASS")
        self.assertIn("LLM_OFF_CONTROL_PLANE_SURVIVES", {f.code for f in report.findings})

    def test_primary_success_secondary_missing_is_release_incomplete(self) -> None:
        snapshot = clean_snapshot()
        snapshot = RecoverySnapshot(
            artifacts=(ArtifactRecoveryObservation("A1", GOOD, GOOD, None, True, False),),
            runs=snapshot.runs,
            state=snapshot.state,
            llm_provider_available=True,
            deterministic_core_available=True,
        )
        report = audit_recovery(snapshot)
        self.assertEqual(report.status, "BLOCKED")
        self.assertIn("SECONDARY_ARTIFACT_MISSING", {f.code for f in report.findings})

    def test_hash_mismatch_blocks_recovery(self) -> None:
        bad = ContentIdentity("d" * 64, 100)
        snapshot = RecoverySnapshot(
            artifacts=(ArtifactRecoveryObservation("A1", GOOD, bad, GOOD, True, True),),
            runs=(),
            state=STATE,
            llm_provider_available=True,
            deterministic_core_available=True,
        )
        report = audit_recovery(snapshot)
        self.assertEqual(report.status, "BLOCKED")
        self.assertIn("PRIMARY_ARTIFACT_IDENTITY_MISMATCH", {f.code for f in report.findings})

    def test_interrupted_running_run_never_becomes_implicit_success(self) -> None:
        snapshot = RecoverySnapshot(
            artifacts=(),
            runs=(RunRecoveryObservation("R1", "RUNNING", True, False),),
            state=STATE,
            llm_provider_available=True,
            deterministic_core_available=True,
        )
        report = audit_recovery(snapshot)
        self.assertEqual(report.status, "BLOCKED")
        self.assertIn("INTERRUPTED_RUN_REQUIRES_RECONCILIATION", {f.code for f in report.findings})

    def test_succeeded_without_result_identity_blocks(self) -> None:
        snapshot = RecoverySnapshot(
            artifacts=(),
            runs=(RunRecoveryObservation("R1", "SUCCEEDED", True, False),),
            state=STATE,
            llm_provider_available=True,
            deterministic_core_available=True,
        )
        report = audit_recovery(snapshot)
        self.assertIn("SUCCEEDED_RUN_MISSING_RESULT_IDENTITY", {f.code for f in report.findings})

    def test_stale_state_and_stale_base_both_block(self) -> None:
        stale = StateRecoveryObservation("b" * 64, "e" * 64, "c" * 40, "f" * 40)
        snapshot = RecoverySnapshot((), (), stale, True, True)
        report = audit_recovery(snapshot)
        codes = {f.code for f in report.findings}
        self.assertIn("STALE_OR_DIVERGED_CURRENT_STATE", codes)
        self.assertIn("STALE_BASE_COMMIT", codes)

    def test_recovery_cannot_request_canonical_write(self) -> None:
        base = clean_snapshot()
        snapshot = RecoverySnapshot(
            base.artifacts,
            base.runs,
            base.state,
            base.llm_provider_available,
            base.deterministic_core_available,
            canonical_write_requested=True,
        )
        report = audit_recovery(snapshot)
        self.assertEqual(report.status, "BLOCKED")
        self.assertIn("RECOVERY_CANONICAL_WRITE_PROHIBITED", {f.code for f in report.findings})

    def test_report_is_deterministic(self) -> None:
        first = audit_recovery(clean_snapshot(llm=False))
        second = audit_recovery(clean_snapshot(llm=False))
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
