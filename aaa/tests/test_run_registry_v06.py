from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "aaa" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aaa.ops.run_registry import InvalidRunRecord, RunRecord, list_runs, persona_overview


BASE = {
    "run_id": "RUN-TEST-001",
    "process_id": "P09-INDEPENDENT-VALIDATION",
    "work_order_id": "WO-TEST-001",
    "responsible_persona": "SEMI-VALIDATION-AUDITOR",
    "executor_role": "PREVALIDATION_CHECK",
    "state": "RUNNING_CONFIRMED",
    "repository": "AofSpds/asset-agent-asa",
    "exact_base_commit": "a" * 40,
    "branch": "aaa-test-run",
    "started_at": "2026-08-16T05:00:00+09:00",
    "last_heartbeat_at": "2026-08-16T05:10:00+09:00",
    "stale_after_seconds": 3600,
    "canonical_output": False,
    "terminal_result": None,
}


class RunRegistryV06Tests(unittest.TestCase):
    def test_running_requires_start_and_heartbeat_evidence(self) -> None:
        payload = dict(BASE)
        payload["last_heartbeat_at"] = None
        with self.assertRaisesRegex(InvalidRunRecord, "RUNNING_REQUIRES_START_AND_HEARTBEAT_EVIDENCE"):
            RunRecord.from_dict(payload, "test.json")

    def test_unknown_persona_is_rejected(self) -> None:
        payload = dict(BASE)
        payload["responsible_persona"] = "CORE_A"
        with self.assertRaisesRegex(InvalidRunRecord, "UNKNOWN_PERSONA"):
            RunRecord.from_dict(payload, "test.json")

    def test_running_record_becomes_stale_unknown_after_deadline(self) -> None:
        record = RunRecord.from_dict(dict(BASE), "test.json")
        now = datetime(2026, 8, 16, 0, 30, tzinfo=timezone.utc)
        self.assertEqual(record.effective_state(now), "STALE_UNKNOWN")

    def test_recent_heartbeat_remains_running_confirmed(self) -> None:
        record = RunRecord.from_dict(dict(BASE), "test.json")
        now = datetime(2026, 8, 15, 20, 30, tzinfo=timezone.utc)
        self.assertEqual(record.effective_state(now), "RUNNING_CONFIRMED")

    def test_terminal_state_requires_persistent_result_identity(self) -> None:
        payload = dict(BASE)
        payload["state"] = "COMPLETED_PASS"
        with self.assertRaisesRegex(InvalidRunRecord, "TERMINAL_STATE_REQUIRES_RESULT_ARTIFACT"):
            RunRecord.from_dict(payload, "test.json")

    def test_nonterminal_state_cannot_bind_terminal_result(self) -> None:
        payload = dict(BASE)
        payload["terminal_result"] = {
            "result_id": "RESULT-001",
            "result_sha256": "b" * 64,
            "completed_at": "2026-08-16T05:30:00+09:00",
            "persistent_locator": "control/results/RESULT-001.json",
            "verdict": "PASS",
        }
        with self.assertRaisesRegex(InvalidRunRecord, "NONTERMINAL_STATE_CANNOT_BIND_TERMINAL_RESULT"):
            RunRecord.from_dict(payload, "test.json")

    def test_completed_pass_with_result_is_valid(self) -> None:
        payload = dict(BASE)
        payload["state"] = "COMPLETED_PASS"
        payload["terminal_result"] = {
            "result_id": "RESULT-001",
            "result_sha256": "b" * 64,
            "completed_at": "2026-08-16T05:30:00+09:00",
            "persistent_locator": "control/results/RESULT-001.json",
            "verdict": "PASS",
        }
        record = RunRecord.from_dict(payload, "test.json")
        self.assertEqual(record.effective_state(), "COMPLETED_PASS")

    def test_registry_loader_rejects_duplicate_run_ids(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            registry = root / "control" / "aaa" / "runs"
            registry.mkdir(parents=True)
            (registry / "a.json").write_text(json.dumps(BASE), encoding="utf-8")
            (registry / "b.json").write_text(json.dumps(BASE), encoding="utf-8")
            with self.assertRaisesRegex(InvalidRunRecord, "DUPLICATE_RUN_ID"):
                list_runs(root, datetime(2026, 8, 15, 20, 30, tzinfo=timezone.utc))

    def test_persona_overview_never_infers_unregistered_persona_as_running(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            registry = root / "control" / "aaa" / "runs"
            registry.mkdir(parents=True)
            (registry / "run.json").write_text(json.dumps(BASE), encoding="utf-8")
            rows = persona_overview(root, datetime(2026, 8, 15, 20, 30, tzinfo=timezone.utc))
            by_persona = {row["persona"]: row for row in rows}
            self.assertEqual(by_persona["SEMI-VALIDATION-AUDITOR"]["state"], "RUNNING_CONFIRMED")
            self.assertEqual(by_persona["SEMI-CONTROL-ARCHITECT"]["state"], "IDLE_OR_UNREGISTERED")
            self.assertIsNone(by_persona["SEMI-CONTROL-ARCHITECT"]["run_id"])

    def test_repository_bootstrap_record_is_visible_terminal_and_noncanonical(self) -> None:
        rows = list_runs(ROOT, datetime(2026, 8, 15, 20, 40, tzinfo=timezone.utc))
        match = [row for row in rows if row["run_id"] == "RUN-AAA-T17-OPS-DASHBOARD-20260816-001"]
        self.assertEqual(len(match), 1)
        self.assertFalse(match[0]["canonical_output"])
        self.assertEqual(match[0]["effective_state"], "COMPLETED_PASS")
        self.assertEqual(match[0]["terminal_result"]["result_id"], "RESULT-AAA-T17-OPS-DASHBOARD-v0.1")


if __name__ == "__main__":
    unittest.main()
