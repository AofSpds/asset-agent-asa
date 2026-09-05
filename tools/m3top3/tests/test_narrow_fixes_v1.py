from __future__ import annotations

import json
import unittest
from pathlib import Path

from tools.m3top3.features_v1_narrow_patch import FeatureEngineV1NarrowPatch, FeatureInputGovernanceError
from tools.m3top3.shared_interface_guards_v1 import (
    SharedInterfaceGuardError,
    validate_consumed_value_provenance,
    validate_f08_freshness_provenance,
)
from tools.m3top3.tests.test_model_v1 import record

HERE = Path(__file__).resolve().parent
CONFIG = json.loads((HERE.parent / "configs" / "m3top3_v1.0.json").read_text(encoding="utf-8"))
FW = CONFIG["feature_weights"]


class TestNarrowFixes(unittest.TestCase):
    def setUp(self):
        self.engine = FeatureEngineV1NarrowPatch(FW)

    def test_01_consumed_scoring_value_without_pit_provenance_fails(self):
        r = record(1)
        r["feature_raw_inputs"] = {
            "F01_COMMERCIAL_CONVERSION_MOMENTUM": {
                "commercial_state": "QUALIFICATION_ACCEPTANCE_OR_FIRST_VOLUME_ORDER",
                "latest_positive_transition_at": "2026-08-01T09:00:00+09:00",
            }
        }
        with self.assertRaises(SharedInterfaceGuardError):
            validate_consumed_value_provenance(r)

    def test_02_post_cutoff_derived_permitted_value_fails(self):
        r = record(1)
        r["feature_raw_inputs"] = {
            "F01_COMMERCIAL_CONVERSION_MOMENTUM": {
                "commercial_state": "QUALIFICATION_ACCEPTANCE_OR_FIRST_VOLUME_ORDER",
                "consumed_fields": ["commercial_state"],
                "consumed_value_provenance": {
                    "commercial_state": {
                        "publication_at": "2026-08-15T00:00:00+09:00",
                        "evidence_ref": "EVIDENCE-AFTER-CUTOFF",
                    }
                },
            }
        }
        with self.assertRaises(SharedInterfaceGuardError):
            validate_consumed_value_provenance(r)

    def test_03_f06_duplicate_milestone_cannot_inflate_90_100(self):
        r = record(3)
        r["feature_raw_inputs"]["F06_CONVERSION_RUNWAY"] = {
            "retrieval_complete": True,
            "milestones": [
                {"milestone_id":"DUP-1","conversion_step":"QUALIFICATION","date":"2026-09-15","verified":True,"source_tier":"S1","supplier_only":False},
                {"milestone_id":"DUP-1","conversion_step":"SHIPMENT","date":"2026-10-15","verified":True,"source_tier":"S3","supplier_only":False},
            ],
            "sequential_conversion_steps": True,
        }
        v = self.engine.f06(r)
        self.assertEqual(str(v.score), "70")
        self.assertEqual(v.trace["independent_verified_count"], 1)
        self.assertEqual(v.trace["duplicate_milestones_removed"], 1)

    def test_04_f06_same_event_identity_deduplicated_even_different_rows(self):
        r = record(3)
        r["feature_raw_inputs"]["F06_CONVERSION_RUNWAY"] = {
            "retrieval_complete": True,
            "milestones": [
                {"event_group_id":"SAME-EVENT","conversion_step":"QUALIFICATION","date":"2026-09-10","verified":True,"source_tier":"S1","supplier_only":False,"description":"wording A"},
                {"event_group_id":"SAME-EVENT","conversion_step":"QUALIFICATION","date":"2026-09-11","verified":True,"source_tier":"S2","supplier_only":False,"description":"wording B"},
            ],
            "sequential_conversion_steps": True,
        }
        v = self.engine.f06(r)
        self.assertEqual(v.trace["deduped_milestones"], 1)
        self.assertEqual(str(v.score), "70")

    def test_05_f02_governed_metric_missing_operator_fails(self):
        rows = [record(1)]
        rows[0]["feature_raw_inputs"]["F02_NUMERIC_BUSINESS_INFLECTION"] = {
            "metric_pairs": {"revenue": {"current": 120, "prior": 100}}
        }
        with self.assertRaises(FeatureInputGovernanceError):
            self.engine.f02(rows)

    def test_06_f02_explicit_relative_correct(self):
        rows = [record(1)]
        rows[0]["feature_raw_inputs"]["F02_NUMERIC_BUSINESS_INFLECTION"] = {
            "metric_pairs": {"revenue": {"current": 120, "prior": 100, "change_mode": "RELATIVE"}}
        }
        v = self.engine.f02(rows)[rows[0]["company_id"]]
        self.assertEqual(v.trace["raw_metric_changes"]["revenue"], "0.2")
        self.assertEqual(v.trace["operator_bindings"]["revenue"], "RELATIVE")

    def test_07_f02_explicit_absolute_percentage_point_correct(self):
        rows = [record(1)]
        rows[0]["feature_raw_inputs"]["F02_NUMERIC_BUSINESS_INFLECTION"] = {
            "metric_pairs": {"operating_margin_pp": {"current": 35, "prior": 32, "change_mode": "ABSOLUTE"}}
        }
        v = self.engine.f02(rows)[rows[0]["company_id"]]
        self.assertEqual(v.trace["raw_metric_changes"]["operating_margin_pp"], "3")
        self.assertEqual(v.trace["operator_bindings"]["operating_margin_pp"], "ABSOLUTE")

    def test_08_f08_freshness_penalty_without_governance_fails(self):
        r = record(1)
        ev = r["feature_raw_inputs"]["F08_EVIDENCE_RELIABILITY"]["feature_evidence"]
        next(iter(ev.values()))["freshness_penalty"] = 10
        with self.assertRaises(SharedInterfaceGuardError):
            validate_f08_freshness_provenance(r)

    def test_09_f08_valid_provenance_penalty_capped_at_20(self):
        r = record(1)
        f08 = r["feature_raw_inputs"]["F08_EVIDENCE_RELIABILITY"]
        target = next(iter(f08["feature_evidence"]))
        f08["feature_evidence"][target].update({
            "freshness_penalty": 30,
            "refresh_rule_id": "REFRESH-RULE-SYN-v1",
            "evaluated_at": "2026-08-14T20:00:00+09:00",
        })
        validate_f08_freshness_provenance(r)
        fmap = self.engine.compute_snapshot([r])["KRX:SYN001"]["features"]
        self.assertEqual(fmap["F08_EVIDENCE_RELIABILITY"]["trace"]["feature_evidence"][target]["freshness_penalty"], "20")

    def test_10_governed_upstream_metric_change_with_operator_id_passes(self):
        rows = [record(1)]
        rows[0]["feature_raw_inputs"]["F02_NUMERIC_BUSINESS_INFLECTION"] = {
            "metric_changes": {
                "utilization": {"value": 4.5, "operator_id": "UPSTREAM_PP_CHANGE_v1"}
            }
        }
        v = self.engine.f02(rows)[rows[0]["company_id"]]
        self.assertEqual(v.trace["raw_metric_changes"]["utilization"], "4.5")
        self.assertEqual(v.trace["operator_bindings"]["utilization"], "UPSTREAM_PP_CHANGE_v1")

    def test_11_f06_rotated_milestone_id_cannot_bypass_shared_event(self):
        r = record(3)
        r["feature_raw_inputs"]["F06_CONVERSION_RUNWAY"] = {
            "retrieval_complete": True,
            "milestones": [
                {"milestone_id":"ROW-A","event_group_id":"EVENT-1","conversion_step":"QUALIFICATION","date":"2026-09-10","verified":True,"source_tier":"S1","supplier_only":False},
                {"milestone_id":"ROW-B","event_group_id":"EVENT-1","conversion_step":"SHIPMENT","date":"2026-10-10","verified":True,"source_tier":"S2","supplier_only":False},
            ],
            "sequential_conversion_steps": True,
        }
        v = self.engine.f06(r)
        self.assertEqual(str(v.score), "70")
        self.assertEqual(v.trace["independent_verified_count"], 1)

    def test_12_f06_rotated_milestone_id_cannot_bypass_shared_evidence(self):
        r = record(3)
        r["feature_raw_inputs"]["F06_CONVERSION_RUNWAY"] = {
            "retrieval_complete": True,
            "milestones": [
                {"milestone_id":"ROW-A","evidence_group_id":"EVID-1","conversion_step":"QUALIFICATION","date":"2026-09-10","verified":True,"source_tier":"S1","supplier_only":False},
                {"milestone_id":"ROW-B","evidence_group_id":"EVID-1","conversion_step":"SHIPMENT","date":"2026-10-10","verified":True,"source_tier":"S2","supplier_only":False},
            ],
            "sequential_conversion_steps": True,
        }
        v = self.engine.f06(r)
        self.assertEqual(str(v.score), "70")
        self.assertEqual(v.trace["independent_verified_count"], 1)

    def test_13_f06_transitive_identity_collision_is_one_group(self):
        r = record(3)
        r["feature_raw_inputs"]["F06_CONVERSION_RUNWAY"] = {
            "retrieval_complete": True,
            "milestones": [
                {"milestone_id":"A","event_group_id":"EVENT-1","conversion_step":"QUALIFICATION","date":"2026-09-10","verified":True,"source_tier":"S1","supplier_only":False},
                {"milestone_id":"B","event_group_id":"EVENT-1","evidence_group_id":"EVID-1","conversion_step":"SHIPMENT","date":"2026-10-10","verified":True,"source_tier":"S2","supplier_only":False},
                {"milestone_id":"C","evidence_group_id":"EVID-1","conversion_step":"REPEAT_ORDER","date":"2026-11-10","verified":True,"source_tier":"S3","supplier_only":False},
            ],
            "sequential_conversion_steps": True,
        }
        v = self.engine.f06(r)
        self.assertEqual(str(v.score), "70")
        self.assertEqual(v.trace["independent_verified_count"], 1)
        self.assertEqual(v.trace["duplicate_milestones_removed"], 2)

    def test_14_f06_distinct_governed_groups_preserve_90_and_100(self):
        r = record(3)
        r["feature_raw_inputs"]["F06_CONVERSION_RUNWAY"] = {
            "retrieval_complete": True,
            "milestones": [
                {"milestone_id":"A","event_group_id":"EVENT-1","conversion_step":"QUALIFICATION","date":"2026-09-10","verified":True,"source_tier":"S1","supplier_only":False},
                {"milestone_id":"B","event_group_id":"EVENT-2","conversion_step":"SHIPMENT","date":"2026-10-10","verified":True,"source_tier":"S2","supplier_only":False},
            ],
            "sequential_conversion_steps": False,
        }
        self.assertEqual(str(self.engine.f06(r).score), "90")
        r["feature_raw_inputs"]["F06_CONVERSION_RUNWAY"]["sequential_conversion_steps"] = True
        self.assertEqual(str(self.engine.f06(r).score), "100")

    def test_15_f06_anonymous_verified_rows_do_not_become_independent(self):
        r = record(3)
        r["feature_raw_inputs"]["F06_CONVERSION_RUNWAY"] = {
            "retrieval_complete": True,
            "milestones": [
                {"conversion_step":"QUALIFICATION","date":"2026-09-10","verified":True,"source_tier":"S1","supplier_only":False},
                {"conversion_step":"SHIPMENT","date":"2026-10-10","verified":True,"source_tier":"S2","supplier_only":False},
            ],
            "sequential_conversion_steps": True,
        }
        v = self.engine.f06(r)
        self.assertEqual(str(v.score), "70")
        self.assertEqual(v.trace["independent_verified_count"], 0)
        self.assertEqual(v.trace["anonymous_verified_count"], 2)

    def test_16_f06_identity_namespaces_do_not_collide_by_literal_alone(self):
        r = record(3)
        r["feature_raw_inputs"]["F06_CONVERSION_RUNWAY"] = {
            "retrieval_complete": True,
            "milestones": [
                {"milestone_id":"SHARED-LITERAL","conversion_step":"QUALIFICATION","date":"2026-09-10","verified":True,"source_tier":"S1","supplier_only":False},
                {"event_group_id":"SHARED-LITERAL","conversion_step":"SHIPMENT","date":"2026-10-10","verified":True,"source_tier":"S2","supplier_only":False},
            ],
            "sequential_conversion_steps": False,
        }
        v = self.engine.f06(r)
        self.assertEqual(str(v.score), "90")
        self.assertEqual(v.trace["independent_verified_count"], 2)


if __name__ == "__main__":
    unittest.main()
