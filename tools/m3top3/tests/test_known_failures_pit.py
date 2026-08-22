from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from tools.m3top3.pit_guard import PITGuard, PITLeakageError
from tools.m3top3.providers import InMemoryFeatureProvider, JsonlFeatureProvider


CUTOFF = "2025-01-02T23:59:59+09:00"


class KnownFailurePITTests(unittest.TestCase):
    def assert_code(self, fn, code):
        with self.assertRaises(PITLeakageError) as caught:
            fn()
        self.assertIn(code, {v.code for v in caught.exception.violations})

    def test_kf_pit_001_missing_publication_key(self):
        self.assert_code(lambda: PITGuard().assert_model_inputs([{"feature_id": "F01"}], CUTOFF), "MISSING_PUBLICATION_AT")

    def test_kf_pit_001_null_publication(self):
        self.assert_code(lambda: PITGuard().assert_model_inputs([{"feature_id": "F01", "publication_at": None}], CUTOFF), "MISSING_PUBLICATION_AT")

    def test_kf_pit_002_naive_publication_string(self):
        self.assert_code(lambda: PITGuard().assert_model_inputs([{"feature_id": "F01", "publication_at": "2025-01-02T12:00:00"}], CUTOFF), "INVALID_PUBLICATION_DATETIME")

    def test_kf_pit_002_naive_publication_datetime(self):
        self.assert_code(lambda: PITGuard().assert_model_inputs([{"feature_id": "F01", "publication_at": datetime(2025, 1, 2, 12)}], CUTOFF), "INVALID_PUBLICATION_DATETIME")

    def test_kf_pit_003_not_available_before_entry(self):
        row = {"feature_id": "F01", "publication_at": "2025-01-02T10:00:00+09:00", "available_before_entry": False}
        self.assert_code(lambda: PITGuard().assert_model_inputs([row], CUTOFF), "NOT_AVAILABLE_BEFORE_ENTRY")

    def test_kf_pit_004_current_only(self):
        row = {"feature_id": "F01", "publication_at": "2025-01-02T10:00:00+09:00", "current_only": True}
        self.assert_code(lambda: PITGuard().assert_model_inputs([row], CUTOFF), "CURRENT_ONLY_FIELD_IN_HISTORY")

    def test_kf_pit_005_in_memory_raw_future_row_excluded_with_receipt(self):
        provider = InMemoryFeatureProvider([{"company_id": "C1", "feature_id": "F01", "publication_at": "2025-01-03T00:00:00+09:00"}])
        self.assertEqual(provider.records_at("C1", datetime.fromisoformat(CUTOFF)), [])
        self.assertEqual(provider.last_retrieval_receipt["excluded_rows"], 1)
        self.assertEqual(provider.last_retrieval_receipt["exclusions"][0]["codes"], ["PIT_PUBLICATION_AFTER_CUTOFF"])

    def test_kf_pit_005_jsonl_raw_future_row_excluded_with_receipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "features.jsonl"
            path.write_text(json.dumps({"company_id": "C1", "feature_id": "F01", "publication_at": "2025-01-03T00:00:00+09:00"}) + "\n", encoding="utf-8")
            provider = JsonlFeatureProvider(path, "test")
            self.assertEqual(provider.records_at("C1", datetime.fromisoformat(CUTOFF)), [])
            receipt=provider.last_retrieval_receipt
            self.assertEqual(receipt["excluded_rows"], 1)
            provider.records_at("C1", datetime.fromisoformat(CUTOFF))
            self.assertEqual(receipt["retrieval_receipt_id"], provider.last_retrieval_receipt["retrieval_receipt_id"])

    def test_kf_pit_005_consumed_future_row_blocks(self):
        row={"feature_id":"F01","publication_at":"2025-01-03T00:00:00+09:00"}
        self.assert_code(lambda: PITGuard().assert_model_inputs([row],CUTOFF),"PIT_PUBLICATION_AFTER_CUTOFF")

    def test_kf_pit_005_cutoff_frozen_bundle_future_row_blocks(self):
        provider=InMemoryFeatureProvider([{"company_id":"C1","feature_id":"F01","publication_at":"2025-01-03T00:00:00+09:00"}],cutoff_frozen_bundle=True)
        self.assert_code(lambda: provider.records_at("C1",datetime.fromisoformat(CUTOFF)),"PIT_PUBLICATION_AFTER_CUTOFF")

    def test_kf_pit_006_raw_effective_after_cutoff_excluded_with_receipt(self):
        row = {"company_id": "C1", "feature_id": "F01", "publication_at": "2025-01-02T10:00:00+09:00", "effective_at": "2025-01-03T00:00:00+09:00"}
        provider = InMemoryFeatureProvider([row])
        self.assertEqual(provider.records_at("C1", datetime.fromisoformat(CUTOFF)), [])
        self.assertEqual(provider.last_retrieval_receipt["exclusions"][0]["codes"], ["PIT_EFFECTIVE_AFTER_CUTOFF"])

    def test_kf_pit_006_consumed_effective_after_cutoff_blocks(self):
        row={"feature_id":"F01","publication_at":"2025-01-02T10:00:00+09:00","effective_at":"2025-01-03T00:00:00+09:00"}
        self.assert_code(lambda: PITGuard().assert_model_inputs([row],CUTOFF),"PIT_EFFECTIVE_AFTER_CUTOFF")

    def test_kf_pit_006_post_snapshot_ca_observation(self):
        row = {"feature_id": "F01", "publication_at": "2025-01-02T10:00:00+09:00", "corporate_action_observed_at": "2025-01-03T00:00:00+09:00"}
        self.assert_code(lambda: PITGuard().assert_model_inputs([row], CUTOFF), "POST_SNAPSHOT_CA_KNOWLEDGE")


if __name__ == "__main__":
    unittest.main()
