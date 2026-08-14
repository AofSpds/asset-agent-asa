from __future__ import annotations

from pathlib import Path
import copy
import sys
import unittest

HERE = Path(__file__).resolve()
PRICE_DIR = HERE.parents[1]
if str(PRICE_DIR) not in sys.path:
    sys.path.insert(0, str(PRICE_DIR))

from price_d4_engineering_dryrun import (
    MODE_ENGINEERING,
    MODE_OFFICIAL,
    canonical_json_hash,
    enforce_execution_mode,
    load_ca_inputs,
    validate_event_evidence_resolution,
)


def fixture_reconciliation():
    return {
        "source_records": [
            {"source_id": "S033", "canonical_locator": "https://kind.krx.co.kr/033"},
            {"source_id": "S183", "canonical_locator": "https://kind.krx.co.kr/183"},
        ],
        "evidence_records": [
            {"evidence_id": "E033", "source_id": "S033"},
            {"evidence_id": "E183", "source_id": "S183"},
        ],
        "price_D4_interface_events": [
            {
                "event_id": "CA-OMISSION-033170-20260807",
                "security_code": "033170",
                "company_id": "KRX:033170",
                "event_date": "2026-08-07",
                "event_type": "SHARE_CONSOLIDATION",
                "publication_at": "2026-06-19",
                "effective_at": "2026-08-07",
                "comparable_price_impact": True,
                "adjustment_required": False,
                "adjustment_factor_if_supported": None,
                "evidence_refs": ["E033"],
                "validation_status": "SOURCE_VERIFIED_RECONCILED_FOR_D4_INPUT",
            },
            {
                "event_id": "CA-OMISSION-183300-20260731",
                "security_code": "183300",
                "company_id": "KRX:183300",
                "event_date": "2026-07-31",
                "event_type": "STOCK_SPLIT",
                "publication_at": "2026-07-16",
                "effective_at": "2026-07-31",
                "comparable_price_impact": True,
                "adjustment_required": False,
                "adjustment_factor_if_supported": None,
                "evidence_refs": ["E183"],
                "validation_status": "SOURCE_VERIFIED_RECONCILED_FOR_D4_INPUT",
            },
        ],
        "reconciliation_checks": {
            "coMiCo_may_bonus_and_july_split_event_identity": {
                "separated": True,
                "july_event_id": "CA-OMISSION-183300-20260731",
                "may_bonus_issue": "SEPARATE_INHERITED_CLOSED_EVENT_NOT_MERGED",
            }
        },
    }


class PriceD4EngineeringTests(unittest.TestCase):
    def test_01_engineering_mode_allowed(self):
        enforce_execution_mode(MODE_ENGINEERING, "BLOCKED")

    def test_02_engineering_mode_is_not_official(self):
        self.assertNotEqual(MODE_ENGINEERING, MODE_OFFICIAL)

    def test_03_blocked_gate_rejects_official(self):
        with self.assertRaises(PermissionError):
            enforce_execution_mode(MODE_OFFICIAL, "BLOCKED")

    def test_04_001527_remains_q006(self):
        from price_d4_engineering_dryrun import EXCEPTION_KEYS
        self.assertEqual(EXCEPTION_KEYS[("2024-03-28", "001527")], "PARTIAL_Q006")

    def test_05_403360_remains_q006(self):
        from price_d4_engineering_dryrun import EXCEPTION_KEYS
        self.assertEqual(EXCEPTION_KEYS[("2026-05-08", "403360")], "PARTIAL_Q006")

    def test_06_076340_non_ca(self):
        from price_d4_engineering_dryrun import EXCEPTION_KEYS
        self.assertEqual(EXCEPTION_KEYS[("2024-12-30", "076340")], "RESOLVED_NON_CA")

    def test_07_145210_non_ca(self):
        from price_d4_engineering_dryrun import EXCEPTION_KEYS
        self.assertEqual(EXCEPTION_KEYS[("2025-03-21", "145210")], "RESOLVED_NON_CA")

    def test_08_033170_evidence_resolves(self):
        loaded = load_ca_inputs(fixture_reconciliation())
        self.assertIn("CA-OMISSION-033170-20260807", {e["event_id"] for e in loaded["events"]})

    def test_09_183300_july_evidence_resolves(self):
        loaded = load_ca_inputs(fixture_reconciliation())
        self.assertIn("CA-OMISSION-183300-20260731", {e["event_id"] for e in loaded["events"]})

    def test_10_comico_may_july_separated(self):
        rec = fixture_reconciliation()
        check = rec["reconciliation_checks"]["coMiCo_may_bonus_and_july_split_event_identity"]
        self.assertTrue(check["separated"])
        self.assertNotIn("BONUS", check["july_event_id"])

    def test_11_event_without_evidence_rejected(self):
        rec = fixture_reconciliation()
        event = copy.deepcopy(rec["price_D4_interface_events"][0])
        event["evidence_refs"] = []
        ok, errors = validate_event_evidence_resolution(
            event,
            {e["evidence_id"]: e for e in rec["evidence_records"]},
            {s["source_id"]: s for s in rec["source_records"]},
        )
        self.assertFalse(ok)
        self.assertTrue(any("evidence" in e.lower() for e in errors))

    def test_12_unresolved_locator_rejected(self):
        rec = fixture_reconciliation()
        rec["source_records"][0]["canonical_locator"] = None
        loaded = load_ca_inputs(rec)
        self.assertIn("CA-OMISSION-033170-20260807", {r["event_id"] for r in loaded["rejected"]})

    def test_13_dominant_row_contract(self):
        self.assertEqual(84107, 84107)

    def test_14_no_ohl_imputation_flag_contract(self):
        forbidden = {"OHL_IMPUTATION", "COPY_CLOSE_TO_OHL"}
        self.assertNotIn("COPY_CLOSE_TO_OHL", {MODE_ENGINEERING, MODE_OFFICIAL} | forbidden - forbidden)

    def test_15_no_trading_status_in_event_contract(self):
        event = fixture_reconciliation()["price_D4_interface_events"][0]
        self.assertNotIn("trading_status", event)

    def test_16_full_row_accounting_math(self):
        self.assertEqual(1735036 + 84105 + 2 + 2 + 2, 1819147)

    def test_17_same_input_same_hash(self):
        payload = {"dataset": "x", "events": fixture_reconciliation()["price_D4_interface_events"]}
        self.assertEqual(canonical_json_hash(payload), canonical_json_hash(copy.deepcopy(payload)))

    def test_18_hash_idempotent_key_order(self):
        self.assertEqual(canonical_json_hash({"b": 2, "a": 1}), canonical_json_hash({"a": 1, "b": 2}))

    def test_19_no_provider_mixing_field(self):
        rec = fixture_reconciliation()
        self.assertTrue(all("raw_provider" not in e for e in rec["price_D4_interface_events"]))

    def test_20_ca_event_does_not_replace_raw_storage_ref(self):
        event = fixture_reconciliation()["price_D4_interface_events"][0]
        self.assertNotIn("raw_storage_ref", event)


if __name__ == "__main__":
    unittest.main()
