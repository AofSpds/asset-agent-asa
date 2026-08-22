from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tools.m3top3.admission import M3Top3AdmissionError, _snapshot_manifest_identity_payload
from tools.m3top3.core import aggregate_hash, deterministic_id, sha256_hex
from tools.m3top3.ledger import PredictionLedger
from tools.m3top3.providers import InMemoryFeatureProvider
from tools.m3top3.snapshot import BatchSnapshotGenerator, SnapshotStore
from tools.m3top3.tests._known_failure_helpers import CountingScorer, diagnostic_runner, materialize_ready_snapshot, ready_builder


class KnownFailureSnapshotTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_kf_snp_001_pit_violation_blocks_scoreable_view(self):
        rows = [{"company_id": "C1", "feature_id": "F01", "publication_at": None}]
        dates, _, builder = ready_builder(self.root, rows)
        built = builder.build(dates[0])
        self.assertEqual(built.status, "SNAPSHOT_BLOCKED")
        self.assertEqual(built.model_inputs, [])
        with self.assertRaises(M3Top3AdmissionError) as caught:
            SnapshotStore(self.root / "blocked-store").write(built, {})
        self.assertEqual(caught.exception.code, "BLOCKED_SNAPSHOT_NOT_READY")
        self.assertFalse((self.root / "blocked-store").exists())

    def _assert_manifest_block(self, status, blockers, expected):
        snapshot_dir, dates, price, _ = materialize_ready_snapshot(self.root)
        manifest_path = snapshot_dir / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["snapshot_status"] = status
        manifest["blockers"] = blockers
        manifest["snapshot_manifest_identity_hash"] = sha256_hex(_snapshot_manifest_identity_payload(manifest))
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        scorer = CountingScorer()
        runner, _ = diagnostic_runner(price, dates, scorer)
        output = self.root / "output"
        ledger_path = output / "prediction-ledger.jsonl"
        ledger = PredictionLedger(ledger_path)
        with self.assertRaises(M3Top3AdmissionError) as caught:
            runner.run_snapshot(snapshot_dir, output / "runs", ledger)
        self.assertEqual(caught.exception.code, expected)
        self.assertEqual(scorer.calls, 0)
        self.assertFalse(output.exists())

    def test_kf_snp_002_partial_manifest_blocked_before_scorer(self):
        self._assert_manifest_block("SNAPSHOT_PARTIAL", ["C1:ELIGIBILITY_UNRESOLVED"], "BLOCKED_SNAPSHOT_NOT_READY")

    def test_kf_snp_003_blocked_manifest_blocked_before_scorer(self):
        self._assert_manifest_block("SNAPSHOT_BLOCKED", ["C1:PIT_PUBLICATION_AFTER_CUTOFF"], "BLOCKED_SNAPSHOT_NOT_READY")

    def test_kf_snp_004_ready_with_blocker_is_contradiction(self):
        self._assert_manifest_block("SNAPSHOT_READY", ["unexpected"], "BLOCKED_MANIFEST_STATE_CONTRADICTION")

    def test_snapshot_block_has_zero_ledger_and_run_mutation(self):
        self._assert_manifest_block("SNAPSHOT_PARTIAL", ["blocked"], "BLOCKED_SNAPSHOT_NOT_READY")

    def test_retrieval_audit_is_hash_bound_and_non_scoreable(self):
        rows=[
            {"company_id":"C1","feature_id":"F01","value":"CURRENT","publication_at":"2025-01-02T10:00:00+09:00","feature_record_id":"CURRENT-ROW"},
            {"company_id":"C1","feature_id":"F02","value":"FUTURE_SECRET","publication_at":"2025-01-03T10:00:00+09:00","feature_record_id":"FUTURE-ROW"},
        ]
        dates,_,builder=ready_builder(self.root,rows)
        built=builder.build(dates[0])
        snapshot_root=self.root/"audited-snapshot"
        manifest=SnapshotStore(snapshot_root).write(built,{"generator_version":"test"})
        target=snapshot_root/dates[0].isoformat()
        pit_text=(target/"pit_snapshot.jsonl").read_text(encoding="utf-8")
        model_text=(target/"model_input.jsonl").read_text(encoding="utf-8")
        audit_text=(target/"retrieval_audit.jsonl").read_text(encoding="utf-8")
        self.assertNotIn("FUTURE_SECRET",pit_text+model_text)
        self.assertNotIn("FUTURE-ROW",pit_text+model_text)
        self.assertIn("FUTURE-ROW",audit_text)
        self.assertIn("PIT_PUBLICATION_AFTER_CUTOFF",audit_text)
        self.assertEqual(manifest["retrieval_audit_row_count"],1)
        self.assertEqual(len(manifest["retrieval_audit_file_sha256"]),64)

    def test_missing_retrieval_receipt_blocks_builder_and_zero_writes(self):
        class BareFeatureProvider:
            source_version="BARE"
            def records_at(self,company_id,cutoff_at):
                return [{"company_id":company_id,"feature_id":"F01","value":"1","publication_at":"2025-01-02T10:00:00+09:00"}]
        dates,_,builder=ready_builder(self.root)
        builder.features=BareFeatureProvider(); output=self.root/"missing-receipt"
        result=BatchSnapshotGenerator(builder,SnapshotStore(output)).run(dates[0],dates[0],{})
        self.assertEqual((result.blocked,result.generated),(1,0))
        self.assertIn("MISSING_DETERMINISTIC_RETRIEVAL_RECEIPT",result.blocked_dates[0])
        self.assertFalse(output.exists())

    def test_unreconciled_retrieval_receipt_blocks_builder_and_zero_writes(self):
        class UnreconciledProvider(InMemoryFeatureProvider):
            def records_at(self,company_id,cutoff_at):
                rows=super().records_at(company_id,cutoff_at)
                self.last_retrieval_receipt["selected_rows"]+=1
                return rows
        rows=[{"company_id":"C1","feature_id":"F01","value":"1","publication_at":"2025-01-02T10:00:00+09:00"}]
        dates,_,builder=ready_builder(self.root)
        builder.features=UnreconciledProvider(rows); output=self.root/"bad-receipt"
        result=BatchSnapshotGenerator(builder,SnapshotStore(output)).run(dates[0],dates[0],{})
        self.assertEqual((result.blocked,result.generated),(1,0))
        self.assertIn("RETRIEVAL_RECEIPT_RECONCILIATION_FAILED",result.blocked_dates[0])
        self.assertFalse(output.exists())

    def test_self_consistent_forged_provider_receipt_is_blocked(self):
        class ForgedProvider(InMemoryFeatureProvider):
            def records_at(self,company_id,cutoff_at):
                rows=super().records_at(company_id,cutoff_at)
                receipt=self.last_retrieval_receipt
                receipt["source_matching_rows"]+=1
                receipt["excluded_rows"]+=1
                receipt["source_hash"]="f"*64
                receipt["exclusions"].append({"row_id":"FORGED-EXCLUSION","codes":["PIT_PUBLICATION_AFTER_CUTOFF"]})
                payload={k:v for k,v in receipt.items() if k!="retrieval_receipt_id"}
                receipt["retrieval_receipt_id"]=deterministic_id("retrieval",payload)
                return rows
        rows=[{"company_id":"C1","feature_id":"F01","value":"1","publication_at":"2025-01-02T10:00:00+09:00"}]
        dates,_,builder=ready_builder(self.root)
        builder.features=ForgedProvider(rows); output=self.root/"forged-receipt"
        result=BatchSnapshotGenerator(builder,SnapshotStore(output)).run(dates[0],dates[0],{})
        self.assertEqual((result.blocked,result.generated),(1,0))
        self.assertIn("RETRIEVAL_RECEIPT_RECONCILIATION_FAILED",result.blocked_dates[0])
        self.assertFalse(output.exists())

    def test_exact_provider_instance_method_forgery_is_independently_reconstructed(self):
        rows=[{"company_id":"C1","feature_id":"F01","value":"1","publication_at":"2025-01-02T10:00:00+09:00"}]
        provider=InMemoryFeatureProvider(rows); original=provider.records_at
        def forged(company_id,cutoff_at):
            selected=original(company_id,cutoff_at)
            provider.last_retrieval_receipt["source_hash"]="f"*64
            payload={k:v for k,v in provider.last_retrieval_receipt.items() if k!="retrieval_receipt_id"}
            provider.last_retrieval_receipt["retrieval_receipt_id"]=deterministic_id("retrieval",payload)
            return selected
        provider.records_at=forged
        dates,_,builder=ready_builder(self.root); builder.features=provider
        output=self.root/"exact-provider-forgery"
        result=BatchSnapshotGenerator(builder,SnapshotStore(output)).run(dates[0],dates[0],{})
        self.assertEqual((result.blocked,result.generated),(1,0))
        self.assertIn("RETRIEVAL_RECEIPT_RECONCILIATION_FAILED",result.blocked_dates[0])
        self.assertFalse(output.exists())

    def test_duplicate_company_slice_is_verified_before_publish(self):
        dates,_,builder=ready_builder(self.root)
        built=builder.build(dates[0])
        built.pit_rows.append(dict(built.pit_rows[0]))
        built.model_inputs.append(dict(built.model_inputs[0]))
        built.retrieval_audits.append(dict(built.retrieval_audits[0]))
        built.snapshot_set_entry_hash=aggregate_hash([sha256_hex(row) for row in built.pit_rows]+[sha256_hex(row) for row in built.model_inputs]+[sha256_hex(row) for row in built.retrieval_audits])
        output=self.root/"prepublish-check"
        with self.assertRaises(M3Top3AdmissionError) as caught:
            SnapshotStore(output).write(built,{})
        self.assertEqual(caught.exception.code,"RETRIEVAL_AUDIT_SEMANTIC_MISMATCH")
        self.assertFalse((output/dates[0].isoformat()).exists())


if __name__ == "__main__":
    unittest.main()
