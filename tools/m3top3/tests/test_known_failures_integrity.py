from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tools.m3top3.admission import M3Top3AdmissionError, _snapshot_manifest_identity_payload, verify_snapshot_artifacts
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

    def _rewrite_self_consistent_audit(self, mutator, recompute_receipt_id=True, align_row_lineage=False):
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
        if align_row_lineage:
            receipts={(row["company_id"],row["cutoff_at"]):row for row in audit_rows}
            models={(row["company_id"],row["snapshot_cutoff_at"]):row for row in model_rows}
            for pit in pit_rows:
                receipt=receipts[(pit["company_id"],pit["snapshot_cutoff_at"])]
                pit["retrieval_receipt_id"]=receipt["retrieval_receipt_id"]
                pit["retrieval_source_hash"]=receipt["source_hash"]
                identity_payload={field:pit.get(field) for field in ("company_id","snapshot_cutoff_at","snapshot_schema_version","snapshot_revision","f1_f2_effective_refs","f3_observation_refs","evidence_refs","dataset_refs","universe_release_id","tradability_state_ref","retrieval_receipt_id","retrieval_source_hash")}
                pit["pit_snapshot_id"]=deterministic_id("pit",identity_payload)
                pit["capture_run_id"]=deterministic_id("capture",{"pit_snapshot_id":pit["pit_snapshot_id"],"generator_version":pit["generator_version"]})
                model=models[(pit["company_id"],pit["snapshot_cutoff_at"])]
                model["pit_snapshot_id"]=pit["pit_snapshot_id"]
                model["retrieval_receipt_id"]=receipt["retrieval_receipt_id"]
                model["retrieval_source_hash"]=receipt["source_hash"]
            pit_text="".join(json.dumps(row,ensure_ascii=False,sort_keys=True,separators=(",",":"))+"\n" for row in pit_rows)
            model_text="".join(json.dumps(row,ensure_ascii=False,sort_keys=True,separators=(",",":"))+"\n" for row in model_rows)
            (self.snapshot_dir/"pit_snapshot.jsonl").write_text(pit_text,encoding="utf-8")
            (self.snapshot_dir/"model_input.jsonl").write_text(model_text,encoding="utf-8")
        manifest_path = self.snapshot_dir / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if align_row_lineage:
            manifest["pit_file_sha256"]=sha256_hex(pit_text)
            manifest["model_input_file_sha256"]=sha256_hex(model_text)
        manifest["retrieval_audit_row_count"] = len(audit_rows)
        manifest["retrieval_audit_file_sha256"] = sha256_hex(audit_text)
        manifest["retrieval_audit_content_hash"] = aggregate_hash([sha256_hex(row) for row in audit_rows])
        manifest["snapshot_content_hash"] = aggregate_hash(
            [sha256_hex(row) for row in pit_rows]
            + [sha256_hex(row) for row in model_rows]
            + [sha256_hex(row) for row in audit_rows]
        )
        manifest["retrieval_receipt_ids"] = sorted(row["retrieval_receipt_id"] for row in audit_rows)
        manifest["retrieval_source_hashes"] = sorted({row["source_hash"] for row in audit_rows})
        manifest["snapshot_manifest_identity_hash"] = sha256_hex(_snapshot_manifest_identity_payload(manifest))
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    def _rewrite_manifest_identity(self, manifest):
        manifest["snapshot_manifest_identity_hash"] = sha256_hex(_snapshot_manifest_identity_payload(manifest))

    def _rewrite_self_consistent_price_lineage(self,manifest_id=None,manifest_hash=None,pit_ref_transform=None):
        pit_path=self.snapshot_dir/"pit_snapshot.jsonl"; model_path=self.snapshot_dir/"model_input.jsonl"; audit_path=self.snapshot_dir/"retrieval_audit.jsonl"; manifest_path=self.snapshot_dir/"manifest.json"
        pit_rows=[json.loads(line) for line in pit_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        model_rows=[json.loads(line) for line in model_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        audit_rows=[json.loads(line) for line in audit_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        manifest=json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest_id is not None:
            manifest["price_dataset_id"]=manifest_id
            for model in model_rows: model["price_dataset_id"]=manifest_id
        if manifest_hash is not None: manifest["price_dataset_hash"]=manifest_hash
        models={(row["company_id"],row["snapshot_cutoff_at"]):row for row in model_rows}
        if pit_ref_transform is not None:
            for pit in pit_rows:
                pit["dataset_refs"]=pit_ref_transform(list(pit["dataset_refs"]))
                identity_payload={field:pit.get(field) for field in ("company_id","snapshot_cutoff_at","snapshot_schema_version","snapshot_revision","f1_f2_effective_refs","f3_observation_refs","evidence_refs","dataset_refs","universe_release_id","tradability_state_ref","retrieval_receipt_id","retrieval_source_hash")}
                pit["pit_snapshot_id"]=deterministic_id("pit",identity_payload)
                pit["capture_run_id"]=deterministic_id("capture",{"pit_snapshot_id":pit["pit_snapshot_id"],"generator_version":pit["generator_version"]})
                models[(pit["company_id"],pit["snapshot_cutoff_at"])]["pit_snapshot_id"]=pit["pit_snapshot_id"]
        pit_text="".join(json.dumps(row,ensure_ascii=False,sort_keys=True,separators=(",",":"))+"\n" for row in pit_rows)
        model_text="".join(json.dumps(row,ensure_ascii=False,sort_keys=True,separators=(",",":"))+"\n" for row in model_rows)
        pit_path.write_text(pit_text,encoding="utf-8"); model_path.write_text(model_text,encoding="utf-8")
        manifest["pit_file_sha256"]=sha256_hex(pit_text); manifest["model_input_file_sha256"]=sha256_hex(model_text)
        manifest["snapshot_content_hash"]=aggregate_hash([sha256_hex(row) for row in pit_rows]+[sha256_hex(row) for row in model_rows]+[sha256_hex(row) for row in audit_rows])
        self._rewrite_manifest_identity(manifest); manifest_path.write_text(json.dumps(manifest),encoding="utf-8")

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
            rows[0]["source_matching_rows"] += 1
        self._rewrite_self_consistent_audit(forge,align_row_lineage=True)
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
        self._rewrite_manifest_identity(manifest)
        path.write_text(json.dumps(manifest), encoding="utf-8")
        self.assert_code(lambda: verify_snapshot_artifacts(self.snapshot_dir), "ROW_COUNT_MISMATCH")

    def test_kf_int_004_pit_row_count_mismatch(self):
        path = self.snapshot_dir / "manifest.json"
        manifest = json.loads(path.read_text(encoding="utf-8"))
        manifest["pit_row_count"] = 99
        self._rewrite_manifest_identity(manifest)
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
        self._rewrite_manifest_identity(manifest)
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        self.assert_code(lambda: verify_snapshot_artifacts(self.snapshot_dir), "SNAPSHOT_CONTENT_HASH_MISMATCH")

    def test_self_consistent_manifest_date_forgery_is_rejected(self):
        manifest_path=self.snapshot_dir/"manifest.json"
        manifest=json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["snapshot_date"]="2030-12-31"
        self._rewrite_manifest_identity(manifest)
        manifest_path.write_text(json.dumps(manifest),encoding="utf-8")
        self.assert_code(lambda:verify_snapshot_artifacts(self.snapshot_dir),"RETRIEVAL_AUDIT_SEMANTIC_MISMATCH")

    def test_self_consistent_model_pit_identity_forgery_is_rejected(self):
        model_path=self.snapshot_dir/"model_input.jsonl"
        model_rows=[json.loads(line) for line in model_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        model_rows[0]["pit_snapshot_id"]="pit_FORGED"
        model_text="".join(json.dumps(row,ensure_ascii=False,sort_keys=True,separators=(",",":"))+"\n" for row in model_rows)
        model_path.write_text(model_text,encoding="utf-8")
        pit_rows=[json.loads(line) for line in (self.snapshot_dir/"pit_snapshot.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
        audit_rows=[json.loads(line) for line in (self.snapshot_dir/"retrieval_audit.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
        manifest_path=self.snapshot_dir/"manifest.json"
        manifest=json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["model_input_file_sha256"]=sha256_hex(model_text)
        manifest["snapshot_content_hash"]=aggregate_hash([sha256_hex(row) for row in pit_rows]+[sha256_hex(row) for row in model_rows]+[sha256_hex(row) for row in audit_rows])
        self._rewrite_manifest_identity(manifest)
        manifest_path.write_text(json.dumps(manifest),encoding="utf-8")
        self.assert_code(lambda:verify_snapshot_artifacts(self.snapshot_dir),"RETRIEVAL_AUDIT_SEMANTIC_MISMATCH")

    def test_hidden_staging_directory_is_not_externally_admissible(self):
        staging=self.snapshot_dir.with_name(f".{self.snapshot_dir.name}.deadbeef.staging")
        self.snapshot_dir.rename(staging)
        self.snapshot_dir=staging
        self.assert_code(lambda:verify_snapshot_artifacts(staging),"RETRIEVAL_AUDIT_SEMANTIC_MISMATCH")

    def test_snapshot_and_outcome_price_lineage_mismatch_is_rejected(self):
        runner,_=diagnostic_runner(self.price,self.dates,CountingScorer())
        runner.outcome_builder.price.dataset_id="FORGED-OTHER-DATASET"
        output=self.root/"lineage-mismatch-output"
        self.assert_code(lambda:runner.run_snapshot(self.snapshot_dir,output),"PRICE_LINEAGE_MISMATCH")
        self.assertFalse(output.exists())

    def test_self_consistent_manifest_model_price_drift_from_pit_is_rejected(self):
        self._rewrite_self_consistent_price_lineage("FORGED-DATASET","f"*64)
        self.assert_code(lambda:verify_snapshot_artifacts(self.snapshot_dir),"RETRIEVAL_AUDIT_SEMANTIC_MISMATCH")

    def test_self_consistent_duplicate_pit_price_reference_is_rejected(self):
        self._rewrite_self_consistent_price_lineage(pit_ref_transform=lambda refs:refs+[dict(refs[0])])
        self.assert_code(lambda:verify_snapshot_artifacts(self.snapshot_dir),"RETRIEVAL_AUDIT_SEMANTIC_MISMATCH")

    def test_self_consistent_missing_pit_price_reference_is_rejected(self):
        self._rewrite_self_consistent_price_lineage(pit_ref_transform=lambda refs:[])
        self.assert_code(lambda:verify_snapshot_artifacts(self.snapshot_dir),"RETRIEVAL_AUDIT_SEMANTIC_MISMATCH")


if __name__ == "__main__":
    unittest.main()
