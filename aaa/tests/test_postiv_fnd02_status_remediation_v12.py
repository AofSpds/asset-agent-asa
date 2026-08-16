from __future__ import annotations

from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "aaa" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aaa.api.operating_structure import _ORG_RE, _select_governed_latest, _status_is_governed


class PostIVFND02GovernedStatusRemediationV12Tests(unittest.TestCase):
    SOURCE_KINDS = ("organization", "channel_registry", "current_state", "process_gate", "roadmap")

    def test_not_reconciled_is_never_governed_current(self) -> None:
        for kind in self.SOURCE_KINDS:
            with self.subTest(kind=kind):
                self.assertFalse(_status_is_governed(kind, "NOT_RECONCILED"))

    def test_reconciled_revoked_is_never_governed_current(self) -> None:
        for kind in self.SOURCE_KINDS:
            with self.subTest(kind=kind):
                self.assertFalse(_status_is_governed(kind, "RECONCILED_REVOKED"))

    def test_active_revoked_is_never_governed_current(self) -> None:
        for kind in self.SOURCE_KINDS:
            with self.subTest(kind=kind):
                self.assertFalse(_status_is_governed(kind, "ACTIVE_REVOKED"))

    def test_owner_approved_revoked_is_never_governed_current(self) -> None:
        for kind in self.SOURCE_KINDS:
            with self.subTest(kind=kind):
                self.assertFalse(_status_is_governed(kind, "OWNER_APPROVED_REVOKED"))

    def test_higher_version_invalid_status_does_not_replace_last_governed_source(self) -> None:
        temp = Path(tempfile.mkdtemp(prefix="aaa-fnd02-status-"))
        try:
            continuity = temp / "control" / "continuity" / "v1.0"
            continuity.mkdir(parents=True, exist_ok=True)
            (continuity / "SEMI-ORG-MAP_v0.2_WORKING.yaml").write_text(
                """org_map_id: SEMI-ORG-MAP
version: v0.2_WORKING
status: OWNER_ACCEPTED
as_of: '2026-08-17T02:00:00+09:00'
""",
                encoding="utf-8",
            )
            (continuity / "SEMI-ORG-MAP_v9.9_WORKING.yaml").write_text(
                """org_map_id: SEMI-ORG-MAP
version: v9.9_WORKING
status: RECONCILED_REVOKED
as_of: '2026-08-17T02:01:00+09:00'
""",
                encoding="utf-8",
            )

            selected, selection = _select_governed_latest(temp, continuity, _ORG_RE, "organization")

            self.assertIsNotNone(selected)
            self.assertEqual(selected.name, "SEMI-ORG-MAP_v0.2_WORKING.yaml")
            self.assertEqual(selection["declared_status"], "OWNER_ACCEPTED")
            self.assertEqual(selection["skipped"][0]["declared_status"], "RECONCILED_REVOKED")
            self.assertEqual(
                selection["skipped"][0]["reason"],
                "UNSUPPORTED_OR_UNPROVEN_GOVERNED_STATUS",
            )
        finally:
            shutil.rmtree(temp)

    def test_existing_governed_status_contract_remains_exactly_admissible(self) -> None:
        accepted = {
            "organization": (
                "STALE",
                "OWNER_ACCEPTED",
                "RECONCILED",
                "ACTIVE",
                "DUAL_CORE_RECONCILED_NOT_FROZEN",
            ),
            "channel_registry": (
                "STALE",
                "WORKING",
                "RECONCILED",
                "ACTIVE",
                "WORKING_CONTROL_REGISTRY",
                "WORKING_CONTROL_REGISTRY_ROTATION_PENDING",
                "WORKING_CONTROL_REGISTRY_SUCCESSOR_ACTIVE",
                "WORKING_CONTROL_REGISTRY_VALIDATION_EXECUTION_EVIDENCE_RECEIVED",
                "WORKING_OWNER_APPROVED_CURRENT_OPERATING_STRUCTURE",
            ),
            "current_state": (
                "STALE",
                "WORKING",
                "RECONCILED",
                "ACTIVE",
                "WORKING_INDEPENDENT_DELTA_FAILED_F06_BOUNDED_FIX_ROUTED",
            ),
            "process_gate": (
                "STALE",
                "WORKING",
                "READY_NOT_DISPATCHED",
                "DISPATCHED_AWAITING_ACK",
                "RUNNING_CONFIRMED",
                "BLOCKED",
                "COMPLETED_PASS",
                "COMPLETED_FAIL",
                "COMPLETED_WITH_FINDINGS",
            ),
            "roadmap": ("STALE", "OWNER_APPROVED"),
        }
        for kind, statuses in accepted.items():
            for status in statuses:
                with self.subTest(kind=kind, status=status):
                    self.assertTrue(_status_is_governed(kind, status))


if __name__ == "__main__":
    unittest.main()
