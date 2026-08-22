from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tools.m3top3.admission import M3Top3AdmissionError, verify_snapshot_artifacts
from tools.m3top3.core import sha256_hex
from tools.m3top3.tests._known_failure_helpers import CountingScorer, diagnostic_runner, materialize_ready_snapshot


class KnownFailureIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.snapshot_dir, self.dates, self.price, _ = materialize_ready_snapshot(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def assert_code(self, fn, code):
        with self.assertRaises(M3Top3AdmissionError) as caught:
            fn()
        self.assertEqual(caught.exception.code, code)
        self.assertEqual(caught.exception.exit_code, 3)

    def test_kf_int_001_malformed_jsonl_blocks_before_scorer_and_write(self):
        model = self.snapshot_dir / "model_input.jsonl"
        model.write_text("{malformed\n", encoding="utf-8")
        scorer = CountingScorer()
        runner, _ = diagnostic_runner(self.price, self.dates, scorer)
        output = self.root / "output"
        self.assert_code(lambda: runner.run_snapshot(self.snapshot_dir, output), "BLOCKED_INPUT_INTEGRITY")
        self.assertEqual(scorer.calls, 0)
        self.assertFalse(output.exists())

    def test_kf_int_002_model_input_valid_json_mutation(self):
        path = self.snapshot_dir / "model_input.jsonl"
        row = json.loads(path.read_text(encoding="utf-8"))
        row["company_id"] = "MUTATED"
        path.write_text(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
        self.assert_code(lambda: verify_snapshot_artifacts(self.snapshot_dir), "MODEL_INPUT_FILE_HASH_MISMATCH")

    def test_kf_int_003_pit_valid_json_mutation(self):
        path = self.snapshot_dir / "pit_snapshot.jsonl"
        row = json.loads(path.read_text(encoding="utf-8"))
        row["company_id"] = "MUTATED"
        path.write_text(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
        self.assert_code(lambda: verify_snapshot_artifacts(self.snapshot_dir), "PIT_FILE_HASH_MISMATCH")

    def test_kf_int_004_declared_row_count_mismatch(self):
        path = self.snapshot_dir / "manifest.json"
        manifest = json.loads(path.read_text(encoding="utf-8"))
        manifest["model_input_row_count"] = 99
        path.write_text(json.dumps(manifest), encoding="utf-8")
        self.assert_code(lambda: verify_snapshot_artifacts(self.snapshot_dir), "ROW_COUNT_MISMATCH")

    def test_kf_int_004_pit_row_count_mismatch(self):
        path = self.snapshot_dir / "manifest.json"
        manifest = json.loads(path.read_text(encoding="utf-8"))
        manifest["pit_row_count"] = 99
        path.write_text(json.dumps(manifest), encoding="utf-8")
        self.assert_code(lambda: verify_snapshot_artifacts(self.snapshot_dir), "ROW_COUNT_MISMATCH")

    def test_kf_int_005_forged_file_hash_semantic_mismatch(self):
        model_path = self.snapshot_dir / "model_input.jsonl"
        row = json.loads(model_path.read_text(encoding="utf-8"))
        row["company_id"] = "FORGED"
        payload = json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
        model_path.write_text(payload, encoding="utf-8")
        manifest_path = self.snapshot_dir / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["model_input_file_sha256"] = sha256_hex(payload)
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        self.assert_code(lambda: verify_snapshot_artifacts(self.snapshot_dir), "SNAPSHOT_CONTENT_HASH_MISMATCH")


if __name__ == "__main__":
    unittest.main()
