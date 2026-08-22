from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tools.m3top3.admission import M3Top3AdmissionError, verify_snapshot_artifacts
from tools.m3top3.core import aggregate_hash, deterministic_id, sha256_hex
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

    def _rewrite_self_consistent_audit(self, mutator, recompute_receipt_id=True):
        audit_path = self.snapshot_dir / "retrieval_audit.jsonl"
        audit_rows = [json.loads(line) for line in audit_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        mutator(audit_rows)
        if recompute_receipt_id:
            for row in audit_rows:
                payload = {key: value for key, value in row.items() if key != "retrieval_receipt_id"}
                row["retrieval_receipt_id"] = deterministic_id("retrieval", payload)
        audit_text = "".join(json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n" for row in audit_rows)
        audit_path.write_text(audit_text, encoding="utf-8")
        pit_rows = [json.loads(line) for line in (self.snapshot_dir / "pit_snapshot.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
        model_rows = [json.loads(line) for line in (self.snapshot_dir / "model_input.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
        manifest_path = self.snapshot_dir / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["retrieval_audit_row_count"] = len(audit_rows)
        manifest["retrieval_audit_file_sha256"] = sha256_hex(audit_text)
        manifest["retrieval_audit_content_hash"] = aggregate_hash([sha256_hex(row) for row in audit_rows])
        manifest["snapshot_content_hash"] = aggregate_hash(
            [sha256_hex(row) for row in pit_rows]
            + [sha256_hex(row) for row in model_rows]
            + [sha256_hex(row) for row in audit_rows]
        )
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

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

    def test_retrieval_audit_valid_json_mutation_is_detected(self):
        path = self.snapshot_dir / "retrieval_audit.jsonl"
        row = json.loads(path.read_text(encoding="utf-8"))
        row["selected_rows"] = row["selected_rows"] + 1
        path.write_text(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
        self.assert_code(lambda: verify_snapshot_artifacts(self.snapshot_dir), "RETRIEVAL_AUDIT_FILE_HASH_MISMATCH")

    def test_self_consistent_forged_retrieval_counts_are_rejected(self):
        def forge(rows):
            rows[0]["selected_rows"] += 1
        self._rewrite_self_consistent_audit(forge)
        self.assert_code(lambda: verify_snapshot_artifacts(self.snapshot_dir), "RETRIEVAL_AUDIT_SEMANTIC_MISMATCH")

    def test_self_consistent_forged_retrieval_company_is_rejected(self):
        self._rewrite_self_consistent_audit(lambda rows: rows[0].__setitem__("company_id", "FORGED-COMPANY"))
        self.assert_code(lambda: verify_snapshot_artifacts(self.snapshot_dir), "RETRIEVAL_AUDIT_SEMANTIC_MISMATCH")

    def test_self_consistent_forged_retrieval_cutoff_is_rejected(self):
        self._rewrite_self_consistent_audit(lambda rows: rows[0].__setitem__("cutoff_at", "2025-01-01T23:59:59+09:00"))
        self.assert_code(lambda: verify_snapshot_artifacts(self.snapshot_dir), "RETRIEVAL_AUDIT_SEMANTIC_MISMATCH")

    def test_self_consistent_forged_retrieval_id_is_rejected(self):
        self._rewrite_self_consistent_audit(lambda rows: rows[0].__setitem__("retrieval_receipt_id", "FORGED-ID"), recompute_receipt_id=False)
        self.assert_code(lambda: verify_snapshot_artifacts(self.snapshot_dir), "RETRIEVAL_AUDIT_SEMANTIC_MISMATCH")

    def test_self_consistent_missing_retrieval_receipt_is_rejected(self):
        self._rewrite_self_consistent_audit(lambda rows: rows.clear())
        self.assert_code(lambda: verify_snapshot_artifacts(self.snapshot_dir), "RETRIEVAL_AUDIT_SEMANTIC_MISMATCH")

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
