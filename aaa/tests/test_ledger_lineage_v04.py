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

from aaa.state.ledger_lineage import git_blob_sha1, load_ledger_lineage


class LedgerLineageTests(unittest.TestCase):
    def test_actual_control_ledger_chain_replays_with_verified_predecessors(self) -> None:
        report = load_ledger_lineage(ROOT)
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["latest_ledger"], "control/continuity/v1.0/SEMI-CONTROL-EVENT-LEDGER_v3.3.jsonl")
        self.assertGreater(report["ledger_count"], 1)
        self.assertGreater(report["event_count"], 1)
        self.assertEqual(report["first_event_id"], "EVT-GEN-0001")
        self.assertEqual(report["last_event_id"], "EVT-VALIDATION-0005")
        self.assertRegex(report["lineage_sha256"], r"^[0-9a-f]{64}$")
        for identity in report["ledgers"]:
            self.assertRegex(identity["git_blob_sha1"], r"^[0-9a-f]{40}$")
            self.assertRegex(identity["sha256"], r"^[0-9a-f]{64}$")

    def test_predecessor_blob_mismatch_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            continuity = root / "control" / "continuity" / "v1.0"
            continuity.mkdir(parents=True)
            base = continuity / "SEMI-CONTROL-EVENT-LEDGER_v1.0.jsonl"
            base.write_text(json.dumps({"event_id": "E1"}) + "\n", encoding="utf-8")
            successor = continuity / "SEMI-CONTROL-EVENT-LEDGER_v1.1.jsonl"
            successor.write_text(
                json.dumps({
                    "record_type": "LEDGER_CONTINUATION",
                    "predecessor_path": "control/continuity/v1.0/SEMI-CONTROL-EVENT-LEDGER_v1.0.jsonl",
                    "predecessor_blob_sha": "0" * 40,
                }) + "\n" + json.dumps({"event_id": "E2"}) + "\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(RuntimeError, "LEDGER_PREDECESSOR_HASH_MISMATCH"):
                load_ledger_lineage(root)

    def test_valid_synthetic_chain_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            continuity = root / "control" / "continuity" / "v1.0"
            continuity.mkdir(parents=True)
            base = continuity / "SEMI-CONTROL-EVENT-LEDGER_v1.0.jsonl"
            base.write_text(json.dumps({"event_id": "E1", "value": 1}) + "\n", encoding="utf-8")
            successor = continuity / "SEMI-CONTROL-EVENT-LEDGER_v1.1.jsonl"
            successor.write_text(
                json.dumps({
                    "record_type": "LEDGER_CONTINUATION",
                    "predecessor_path": "control/continuity/v1.0/SEMI-CONTROL-EVENT-LEDGER_v1.0.jsonl",
                    "predecessor_blob_sha": git_blob_sha1(base.read_bytes()),
                }) + "\n" + json.dumps({"event_id": "E2", "value": 2}) + "\n",
                encoding="utf-8",
            )
            first = load_ledger_lineage(root)
            second = load_ledger_lineage(root)
            self.assertEqual(first, second)
            self.assertEqual(first["event_count"], 2)
            self.assertEqual([row["event_id"] for row in first["events"]], ["E1", "E2"])


if __name__ == "__main__":
    unittest.main()
