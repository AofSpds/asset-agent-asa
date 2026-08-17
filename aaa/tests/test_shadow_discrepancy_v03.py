from __future__ import annotations

from contextlib import redirect_stdout
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "aaa" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aaa.cli.main import main as cli_main
from aaa.state.discrepancy import build_discrepancy_report, flatten_yaml_scalars


class ShadowDiscrepancyTests(unittest.TestCase):
    def test_current_control_anchors_match(self) -> None:
        report = build_discrepancy_report(ROOT)
        self.assertEqual(report["status"], "MATCH")
        self.assertEqual(report["projection_scope"], "CONTROL_ANCHORS_V0_1_NOT_FULL_EVENT_REPLAY")
        self.assertEqual(report["current_state"]["version"], "v2.11")
        self.assertEqual(report["event_ledger"]["latest_event_id"], "EVT-VALIDATION-0005")
        self.assertEqual(len(report["comparisons"]), 7)
        self.assertTrue(all(row["status"] == "MATCH" for row in report["comparisons"]))
        self.assertRegex(report["report_sha256"], r"^[0-9a-f]{64}$")

    def test_cli_state_compare_is_deterministic(self) -> None:
        first = io.StringIO()
        second = io.StringIO()
        with redirect_stdout(first):
            rc1 = cli_main(["--repo-root", str(ROOT), "state", "compare", "--json"])
        with redirect_stdout(second):
            rc2 = cli_main(["--repo-root", str(ROOT), "state", "compare", "--json"])
        self.assertEqual((rc1, rc2), (0, 0))
        self.assertEqual(json.loads(first.getvalue()), json.loads(second.getvalue()))

    def test_yaml_scalar_parser_does_not_guess_lists(self) -> None:
        parsed = flatten_yaml_scalars("root:\n  flag: true\n  count: 3\n  items:\n    - A\n")
        self.assertEqual(parsed["root.flag"], True)
        self.assertEqual(parsed["root.count"], 3)
        self.assertNotIn("root.items", parsed)

    def _write_fixture(self, root: Path, *, ledger_head: str, authoritative_target: str, shadow_target: str) -> None:
        continuity = root / "control" / "continuity" / "v1.0"
        continuity.mkdir(parents=True)
        (continuity / "SEMI-CURRENT-STATE_v1.0.yaml").write_text(
            "version: v1.0\n"
            "status: FIXTURE\n"
            "model_v1:\n"
            "  independent_delta_adjudication:\n"
            f"    validated_target: {authoritative_target}\n"
            "    verdict: FAIL\n"
            "    new_successor_required: true\n"
            "actual_replay_readiness:\n"
            "  ready: false\n"
            "scientific_firewall:\n"
            "  model_frozen: false\n"
            "  production_release_authorized: false\n"
            "continuity:\n"
            f"  event_ledger_head: {ledger_head}\n",
            encoding="utf-8",
        )
        event = {
            "event_id": "E1",
            "timestamp": "2026-08-16T00:00:00+09:00",
            "state": {
                "validated_target": shadow_target,
                "independent_delta": "FAIL",
                "new_successor_required": True,
                "actual_replay_authorized": False,
                "model_frozen": False,
                "production_release_authorized": False,
            },
        }
        (continuity / "SEMI-CONTROL-EVENT-LEDGER_v1.0.jsonl").write_text(json.dumps(event) + "\n", encoding="utf-8")

    def test_mismatch_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ledger = "control/continuity/v1.0/SEMI-CONTROL-EVENT-LEDGER_v1.0.jsonl"
            self._write_fixture(root, ledger_head=ledger, authoritative_target="A", shadow_target="B")
            report = build_discrepancy_report(root)
            self.assertEqual(report["status"], "MISMATCH")
            row = next(item for item in report["comparisons"] if item["key"] == "validated_target")
            self.assertEqual(row["status"], "MISMATCH")

    def test_stale_ledger_binding_has_priority(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            old_ledger = "control/continuity/v1.0/SEMI-CONTROL-EVENT-LEDGER_v1.0.jsonl"
            self._write_fixture(root, ledger_head=old_ledger, authoritative_target="A", shadow_target="A")
            continuity = root / "control" / "continuity" / "v1.0"
            event = {
                "event_id": "E2",
                "state": {
                    "validated_target": "A",
                    "independent_delta": "FAIL",
                    "new_successor_required": True,
                    "actual_replay_authorized": False,
                    "model_frozen": False,
                    "production_release_authorized": False,
                },
            }
            (continuity / "SEMI-CONTROL-EVENT-LEDGER_v1.1.jsonl").write_text(json.dumps(event) + "\n", encoding="utf-8")
            report = build_discrepancy_report(root)
            self.assertEqual(report["status"], "STALE")

    def test_work_order_hash_binding(self) -> None:
        path = ROOT / "control" / "aaa" / "v0.1" / "AAA-WO-SHADOW-DISCREPANCY-20260816_v1.json"
        work_order = json.loads(path.read_text(encoding="utf-8"))
        expected = work_order.pop("work_order_sha256")
        canonical = json.dumps(work_order, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        self.assertEqual(hashlib.sha256(canonical).hexdigest(), expected)
        self.assertEqual(work_order["exact_base_identity"]["commit_sha"], "0833dfc1d42814732b3de428428027a3ad990802")
        self.assertIn("NO_OUTCOME_DATA_USE", work_order["scientific_firewall"])


if __name__ == "__main__":
    unittest.main()
