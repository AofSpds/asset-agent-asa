from __future__ import annotations

from datetime import datetime, timezone
import hashlib
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


def terminal_payload() -> dict[str, object]:
    payload = dict(BASE)
    payload["state"] = "COMPLETED_PASS"
    payload["terminal_result"] = {
        "result_id": "RESULT-001",
        "result_sha256": "b" * 64,
        "completed_at": "2026-08-16T05:30:00+09:00",
        "persistent_locator": "control/aaa/results/RESULT-001.json",
        "verdict": "PASS",
    }
    return payload


def write_work_order(root: Path, work_order_id: str = "WO-TEST-001", observed_id: str | None = None) -> None:
    directory = root / "control" / "workorders"
    directory.mkdir(parents=True, exist_ok=True)
    value = observed_id if observed_id is not None else work_order_id
    (directory / f"{work_order_id}.yaml").write_text(
        f"work_order_id: {value}\nstatus: TEST\n",
        encoding="utf-8",
    )


def write_run(root: Path, payload: dict[str, object], name: str = "run.json") -> None:
    directory = root / "control" / "aaa" / "runs"
    directory.mkdir(parents=True, exist_ok=True)
    (directory / name).write_text(json.dumps(payload), encoding="utf-8")


def bind_physical_result(
    root: Path,
    payload: dict[str, object],
    *,
    result_run_id: str | None = None,
    result_work_order_id: str | None = None,
    result_target: str | None = None,
    result_verdict: str | None = None,
) -> dict[str, object]:
    bound = dict(payload)
    terminal = dict(bound["terminal_result"])
    locator = str(terminal["persistent_locator"])
    path = root / locator
    path.parent.mkdir(parents=True, exist_ok=True)
    result_payload = {
        "result_id": terminal["result_id"],
        "run_id": result_run_id or bound["run_id"],
        "work_order_id": result_work_order_id or bound["work_order_id"],
        "verdict": result_verdict or terminal["verdict"],
        "repository": bound["repository"],
        "exact_base_commit": result_target or bound["exact_base_commit"],
    }
    encoded = (json.dumps(result_payload, indent=2) + "\n").encode("utf-8")
    path.write_bytes(encoded)
    terminal["result_sha256"] = hashlib.sha256(encoded).hexdigest()
    bound["terminal_result"] = terminal
    return bound


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
        payload["terminal_result"] = terminal_payload()["terminal_result"]
        with self.assertRaisesRegex(InvalidRunRecord, "NONTERMINAL_STATE_CANNOT_BIND_TERMINAL_RESULT"):
            RunRecord.from_dict(payload, "test.json")

    def test_completed_pass_with_result_is_valid(self) -> None:
        record = RunRecord.from_dict(terminal_payload(), "test.json")
        self.assertEqual(record.effective_state(), "COMPLETED_PASS")

    def test_registry_loader_rejects_duplicate_run_ids(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_work_order(root)
            write_run(root, dict(BASE), "a.json")
            write_run(root, dict(BASE), "b.json")
            with self.assertRaisesRegex(InvalidRunRecord, "DUPLICATE_RUN_ID"):
                list_runs(root, datetime(2026, 8, 15, 20, 30, tzinfo=timezone.utc))

    def test_persona_overview_never_infers_unregistered_persona_as_running(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_work_order(root)
            write_run(root, dict(BASE))
            rows = persona_overview(root, datetime(2026, 8, 15, 20, 30, tzinfo=timezone.utc))
            by_persona = {row["persona"]: row for row in rows}
            self.assertEqual(by_persona["SEMI-VALIDATION-AUDITOR"]["state"], "RUNNING_CONFIRMED")
            self.assertEqual(by_persona["SEMI-CONTROL-ARCHITECT"]["state"], "IDLE_OR_UNREGISTERED")
            self.assertIsNone(by_persona["SEMI-CONTROL-ARCHITECT"]["run_id"])

    def test_terminal_run_is_latest_history_not_current_persona_activity(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_work_order(root)
            payload = terminal_payload()
            payload["responsible_persona"] = "SEMI-CONTROL-ARCHITECT"
            payload = bind_physical_result(root, payload)
            write_run(root, payload)
            rows = persona_overview(root, datetime(2026, 8, 15, 20, 40, tzinfo=timezone.utc))
            by_persona = {row["persona"]: row for row in rows}
            row = by_persona["SEMI-CONTROL-ARCHITECT"]
            self.assertEqual(row["state"], "IDLE_OR_UNREGISTERED")
            self.assertIsNone(row["run_id"])
            self.assertEqual(row["latest_run_id"], "RUN-TEST-001")
            self.assertEqual(row["latest_run_state"], "COMPLETED_PASS")

    def test_repository_bootstrap_record_is_visible_terminal_and_noncanonical(self) -> None:
        rows = list_runs(ROOT, datetime(2026, 8, 15, 20, 40, tzinfo=timezone.utc))
        match = [row for row in rows if row["run_id"] == "RUN-AAA-T17-OPS-DASHBOARD-20260816-001"]
        self.assertEqual(len(match), 1)
        self.assertFalse(match[0]["canonical_output"])
        self.assertEqual(match[0]["effective_state"], "COMPLETED_PASS")
        self.assertEqual(match[0]["terminal_result"]["result_id"], "RESULT-AAA-T17-OPS-DASHBOARD-v0.1")

    # P09 remediation: temporal evidence must fail closed.
    def test_future_heartbeat_never_produces_running_confirmed(self) -> None:
        record = RunRecord.from_dict(dict(BASE), "test.json")
        before_heartbeat = datetime(2026, 8, 15, 20, 5, tzinfo=timezone.utc)
        self.assertEqual(record.effective_state(before_heartbeat), "STALE_UNKNOWN")

    def test_future_started_at_never_produces_running_confirmed(self) -> None:
        payload = dict(BASE)
        payload["started_at"] = "2026-08-16T06:00:00+09:00"
        payload["last_heartbeat_at"] = "2026-08-16T06:10:00+09:00"
        record = RunRecord.from_dict(payload, "test.json")
        reference = datetime(2026, 8, 15, 20, 30, tzinfo=timezone.utc)
        self.assertEqual(record.effective_state(reference), "STALE_UNKNOWN")

    def test_heartbeat_before_start_is_rejected(self) -> None:
        payload = dict(BASE)
        payload["last_heartbeat_at"] = "2026-08-16T04:59:59+09:00"
        with self.assertRaisesRegex(InvalidRunRecord, "HEARTBEAT_PRECEDES_START"):
            RunRecord.from_dict(payload, "test.json")

    # P09 remediation: terminal state and Result verdict are one invariant.
    def test_terminal_state_verdict_mismatch_is_rejected(self) -> None:
        payload = terminal_payload()
        terminal = dict(payload["terminal_result"])
        terminal["verdict"] = "FAIL"
        payload["terminal_result"] = terminal
        with self.assertRaisesRegex(InvalidRunRecord, "TERMINAL_STATE_VERDICT_MISMATCH"):
            RunRecord.from_dict(payload, "test.json")

    def test_all_terminal_state_verdict_mismatches_are_rejected(self) -> None:
        cases = [
            ("COMPLETED_PASS", "PASS_WITH_FINDINGS"),
            ("COMPLETED_FAIL", "PASS"),
            ("COMPLETED_WITH_FINDINGS", "FAIL"),
        ]
        for state, verdict in cases:
            with self.subTest(state=state, verdict=verdict):
                payload = terminal_payload()
                payload["state"] = state
                terminal = dict(payload["terminal_result"])
                terminal["verdict"] = verdict
                payload["terminal_result"] = terminal
                with self.assertRaisesRegex(InvalidRunRecord, "TERMINAL_STATE_VERDICT_MISMATCH"):
                    RunRecord.from_dict(payload, "test.json")

    # P09 remediation: terminal Result bytes and referential identity are proven.
    def test_missing_persistent_result_locator_is_rejected_by_loader(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_work_order(root)
            payload = terminal_payload()
            write_run(root, payload)
            with self.assertRaisesRegex(InvalidRunRecord, "TERMINAL_RESULT_LOCATOR_INVALID"):
                list_runs(root)

    def test_result_physical_sha256_mismatch_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_work_order(root)
            payload = bind_physical_result(root, terminal_payload())
            terminal = dict(payload["terminal_result"])
            terminal["result_sha256"] = "c" * 64
            payload["terminal_result"] = terminal
            write_run(root, payload)
            with self.assertRaisesRegex(InvalidRunRecord, "TERMINAL_RESULT_SHA256_MISMATCH"):
                list_runs(root)

    def test_result_run_id_mismatch_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_work_order(root)
            payload = bind_physical_result(root, terminal_payload(), result_run_id="RUN-WRONG")
            write_run(root, payload)
            with self.assertRaisesRegex(InvalidRunRecord, "TERMINAL_RESULT_RUN_ID_MISMATCH"):
                list_runs(root)

    def test_result_work_order_id_mismatch_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_work_order(root)
            payload = bind_physical_result(root, terminal_payload(), result_work_order_id="WO-WRONG")
            write_run(root, payload)
            with self.assertRaisesRegex(InvalidRunRecord, "TERMINAL_RESULT_WORK_ORDER_ID_MISMATCH"):
                list_runs(root)

    def test_result_exact_target_mismatch_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_work_order(root)
            payload = bind_physical_result(root, terminal_payload(), result_target="d" * 40)
            write_run(root, payload)
            with self.assertRaisesRegex(InvalidRunRecord, "TERMINAL_RESULT_TARGET_MISMATCH"):
                list_runs(root)

    # P09 remediation: Work Order linkage is resolved by persisted identity, not filename assumption.
    def test_nonexistent_work_order_reference_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_run(root, dict(BASE))
            with self.assertRaisesRegex(InvalidRunRecord, "WORK_ORDER_REGISTRY_MISSING|WORK_ORDER_NOT_FOUND"):
                list_runs(root, datetime(2026, 8, 15, 20, 30, tzinfo=timezone.utc))

    def test_work_order_identity_mismatch_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_work_order(root, observed_id="WO-DIFFERENT")
            write_run(root, dict(BASE))
            with self.assertRaisesRegex(InvalidRunRecord, "WORK_ORDER_NOT_FOUND"):
                list_runs(root, datetime(2026, 8, 15, 20, 30, tzinfo=timezone.utc))

    # P09 remediation: current activity ordering is chronological UTC, not raw ISO text.
    def test_cross_offset_activity_order_uses_chronological_utc(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_work_order(root)
            older = dict(BASE)
            older["run_id"] = "RUN-OLDER"
            older["state"] = "READY_NOT_DISPATCHED"
            older["started_at"] = "2026-08-16T10:00:00+09:00"  # 01:00Z
            older["last_heartbeat_at"] = None
            newer = dict(BASE)
            newer["run_id"] = "RUN-NEWER"
            newer["state"] = "READY_NOT_DISPATCHED"
            newer["started_at"] = "2026-08-16T02:30:00+00:00"  # 02:30Z
            newer["last_heartbeat_at"] = None
            write_run(root, older, "older.json")
            write_run(root, newer, "newer.json")
            rows = persona_overview(root, datetime(2026, 8, 16, 3, 0, tzinfo=timezone.utc))
            row = {item["persona"]: item for item in rows}["SEMI-VALIDATION-AUDITOR"]
            self.assertEqual(row["run_id"], "RUN-NEWER")
            self.assertEqual(row["latest_run_id"], "RUN-NEWER")


if __name__ == "__main__":
    unittest.main()
