from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from tools.m3top3.contracts_v1 import ContractError, validate_mis_record
from tools.m3top3.features_v1_narrow_patch import FeatureEngineV1NarrowPatch
from tools.m3top3.scorer_v1 import M3Top3V1Engine
from tools.m3top3.runtime_v1 import build_engine
from tools.m3top3.window_mapping_v11 import WeekdayCalendar, resolve_window, add_calendar_months

HERE = Path(__file__).resolve().parent
CONFIG = json.loads((HERE.parent / "configs" / "m3top3_v1.0.json").read_text(encoding="utf-8"))
FW = CONFIG["feature_weights"]


def feature_raw(i: int):
    runway_milestones = (
        [
            {"milestone_id": f"RUN-{i}-M1", "conversion_step": "QUALIFICATION", "date": "2026-09-15", "verified": True, "source_tier": "S1", "supplier_only": False},
            {"milestone_id": f"RUN-{i}-M2", "conversion_step": "SHIPMENT", "date": "2026-10-15", "verified": True, "source_tier": "S3", "supplier_only": False},
        ]
        if i >= 3
        else [
            {"milestone_id": f"RUN-{i}-M1", "conversion_step": "QUALIFICATION", "date": "2026-09-15", "verified": True, "source_tier": "S2", "supplier_only": False}
        ]
    )
    return {
        "F01_COMMERCIAL_CONVERSION_MOMENTUM": {"commercial_state":"SHIPMENT_OR_BACKLOG_CONVERSION" if i>=2 else "QUALIFICATION_ACCEPTANCE_OR_FIRST_VOLUME_ORDER","latest_positive_transition_at":f"2026-08-0{min(i+1,9)}T09:00:00+09:00","event_group_ids":[f"COMM-{i}"],"source_lineage_refs":[f"SYN-COMM-{i}"]},
        "F02_NUMERIC_BUSINESS_INFLECTION": {"metric_changes":{"revenue":{"value":i*0.10,"operator_id":"SYN_UPSTREAM_REVENUE_CHANGE_v1"},"operating_profit":{"value":i*0.15,"operator_id":"SYN_UPSTREAM_OP_CHANGE_v1"}},"event_group_ids":[f"NUM-{i}"],"source_lineage_refs":[f"SYN-NUM-{i}"]},
        "F03_FORWARD_REVISION_MOMENTUM": {"revision_pcts":{"eps":i*0.05,"op":i*0.04},"event_group_ids":[f"REV-{i}"],"source_lineage_refs":[f"SYN-REV-{i}"]},
        "F04_EVENT_SURPRISE_VS_PRIOR_EXPECTATION": {"independent_pre_event_baseline":True,"observed":100+10*i,"prior_expectation":100,"event_group_ids":[f"SURP-{i}"],"source_lineage_refs":[f"SYN-SURP-{i}"]},
        "F05_MARKET_POSITIONING_BALANCE": {"trailing_20d_total_return":i*0.03,"universe_20d_equal_weight_return":0.02,"trailing_60d_total_return":i*0.06,"universe_60d_equal_weight_return":0.04,"turnover_acceleration":i*0.20,"valuation_percentile":60+i*5,"diffusion_percentile":55+i*5,"event_group_ids":[f"MKT-{i}"],"source_lineage_refs":[f"SYN-MKT-{i}"]},
        "F06_CONVERSION_RUNWAY": {"retrieval_complete":True,"milestones":runway_milestones,"sequential_conversion_steps":i>=3,"event_group_ids":[f"RUN-{i}"],"source_lineage_refs":[f"SYN-RUN-{i}"]},
        "F07_BETA_TRANSMISSION_ALIGNMENT": {"activation_alignment":["PRE_ACTIVATION","APPROACHING_RELEVANT_PHASE","ACTIVE_RELEVANT_PHASE","ACTIVE_WITH_DIRECT_CUSTOMER_CONFIRMATION"][i-1],"event_group_ids":[f"BETA-{i}"],"source_lineage_refs":[f"SYN-BETA-{i}"]},
        "F08_EVIDENCE_RELIABILITY": {"feature_evidence":{f:{"evidence_status":"VERIFIED_HIGH","freshness_penalty":0} for f in FW if f!="F08_EVIDENCE_RELIABILITY"},"source_lineage_refs":[f"SYN-EVI-{i}"]},
        "F09_EXECUTION_THESIS_SAFETY": {"assessment_complete":True,"risk_events":[] if i<4 else [{"severity":"HIGH","event_group_id":"RISK-HARD"},{"severity":"LOW","event_group_id":"RISK-LOW"}],"event_group_ids":[f"RISK-{i}"],"source_lineage_refs":[f"SYN-RISK-{i}"]},
    }


def record(i: int):
    r={"snapshot_id":"SYN-SNAPSHOT-20260814","snapshot_date":"2026-08-14","snapshot_cutoff_at":"2026-08-14T23:59:59+09:00","snapshot_content_hash_or_revision":"synhash-v1","window_anchor_date":"2026-08-14","window_mapping_version":"WM-v1.1","company_id":f"KRX:SYN{i:03d}","krx_code":f"SYN{i:03d}","universe_release_id":"SYN-UNIVERSE-v1","eligibility_state":"ELIGIBLE","model_version":"M3TOP3-v1.0","feature_schema_version":"M3TOP3-FEATURE-SCHEMA_v1.0_WORKING","scorer_version":"M3TOP3-GATED-LINEAR_v1.0_WORKING","weight_version":"M3TOP3-WEIGHT-VERSION_v1.0_WORKING","model_input_schema_version":"MIS-v1.0","input_release_or_hash":"SYN-INPUT-v1","code_or_executable_identity":"LOCAL-TEST","feature_raw_inputs":feature_raw(i)}
    if i==4:r["hard_risk_gate"]={"state":"SEVERE","event_group_id":"RISK-HARD","evidence_status":"VERIFIED_PRIMARY","reason":"synthetic severe risk event"}
    return r


class TestWindowMapping(unittest.TestCase):
    def test_w1_w8_calendar(self):
        expected=[("2024-08-10","2024-11-10","2024-08-09","2024-11-08"),("2024-11-10","2025-02-10","2024-11-08","2025-02-10"),("2025-02-10","2025-05-10","2025-02-10","2025-05-09"),("2025-05-10","2025-08-10","2025-05-09","2025-08-08"),("2025-08-10","2025-11-10","2025-08-08","2025-11-10"),("2025-11-10","2026-02-10","2025-11-10","2026-02-10"),("2026-02-10","2026-05-10","2026-02-10","2026-05-08"),("2026-05-10","2026-08-10","2026-05-08","2026-08-10")]
        for anchor,end,cutoff,last_trade in expected:
            m=resolve_window(anchor,WeekdayCalendar());self.assertEqual(m.nominal_window_end.isoformat(),end);self.assertEqual(m.snapshot_cutoff_date.isoformat(),cutoff);self.assertEqual(m.evaluation_last_trade_date.isoformat(),last_trade)
    def test_daily_window(self):
        m=resolve_window("2026-08-14",WeekdayCalendar());self.assertEqual(m.snapshot_cutoff_date.isoformat(),"2026-08-14");self.assertEqual(m.entry_trade_date.isoformat(),"2026-08-17");self.assertEqual(m.nominal_window_end.isoformat(),"2026-11-14");self.assertEqual(m.evaluation_last_trade_date.isoformat(),"2026-11-13");self.assertEqual(m.exit_trade_date.isoformat(),"2026-11-16")
    def test_month_clip(self):
        import datetime
        self.assertEqual(add_calendar_months(datetime.date(2026,1,31),3).isoformat(),"2026-04-30")


class TestContractsAndFeatures(unittest.TestCase):
    def setUp(self):self.rows=[record(i) for i in range(1,5)];self.engine=FeatureEngineV1NarrowPatch(FW)
    def test_mis_contract(self):
        validate_mis_record(self.rows[0]);bad=copy.deepcopy(self.rows[0]);bad.pop("window_anchor_date")
        with self.assertRaises(ContractError):validate_mis_record(bad)
    def test_pit_firewall_future_field(self):
        bad=copy.deepcopy(self.rows[0]);bad["future_MFE"]=0.42
        with self.assertRaises(Exception):validate_mis_record(bad)
    def test_pit_firewall_future_publication(self):
        bad=copy.deepcopy(self.rows[0]);bad["feature_raw_inputs"]["F01_COMMERCIAL_CONVERSION_MOMENTUM"]["publication_at"]="2026-08-15T00:00:00+09:00"
        with self.assertRaises(Exception):validate_mis_record(bad)
    def test_f01_f09_transformations(self):
        out=self.engine.compute_snapshot(self.rows)
        for r in self.rows:
            fs=out[r["company_id"]]["features"];self.assertEqual(set(fs),set(FW))
            for fid in FW:self.assertIsNotNone(fs[fid]["score"],fid)
        self.assertEqual(out[self.rows[3]["company_id"]]["features"]["F07_BETA_TRANSMISSION_ALIGNMENT"]["score"],"100");self.assertEqual(out[self.rows[2]["company_id"]]["features"]["F06_CONVERSION_RUNWAY"]["score"],"100")
    def test_missingness_not_zero(self):
        rows=copy.deepcopy(self.rows);rows[0]["feature_raw_inputs"]["F01_COMMERCIAL_CONVERSION_MOMENTUM"]={"commercial_state":"NONE","event_group_ids":["NONE-EVENT"]};rows[0]["feature_raw_inputs"].pop("F02_NUMERIC_BUSINESS_INFLECTION");out=self.engine.compute_snapshot(rows)[rows[0]["company_id"]]["features"]
        self.assertEqual(out["F01_COMMERCIAL_CONVERSION_MOMENTUM"]["score"],"0");self.assertEqual(out["F01_COMMERCIAL_CONVERSION_MOMENTUM"]["availability_state"],"AVAILABLE");self.assertIsNone(out["F02_NUMERIC_BUSINESS_INFLECTION"]["score"]);self.assertEqual(out["F02_NUMERIC_BUSINESS_INFLECTION"]["availability_state"],"NOT_FOUND")
    def test_unknown_false_and_not_found_negative_distinctions(self):
        rows=copy.deepcopy(self.rows);rows[0]["feature_raw_inputs"]["F07_BETA_TRANSMISSION_ALIGNMENT"]={"availability_state":"UNKNOWN","missing_reason":"synthetic unknown","activation_alignment":False,"event_group_ids":["UNK-BETA"]};rows[0]["feature_raw_inputs"]["F01_COMMERCIAL_CONVERSION_MOMENTUM"]={"availability_state":"NOT_FOUND","missing_reason":"synthetic retrieval failure","commercial_state":"NONE","event_group_ids":["NF-COMM"]};out=self.engine.compute_snapshot(rows)[rows[0]["company_id"]]["features"]
        self.assertEqual(out["F07_BETA_TRANSMISSION_ALIGNMENT"]["availability_state"],"UNKNOWN");self.assertIsNone(out["F07_BETA_TRANSMISSION_ALIGNMENT"]["score"]);self.assertEqual(out["F01_COMMERCIAL_CONVERSION_MOMENTUM"]["availability_state"],"NOT_FOUND");self.assertIsNone(out["F01_COMMERCIAL_CONVERSION_MOMENTUM"]["score"])
    def test_anti_double_count(self):
        rows=copy.deepcopy(self.rows);shared="SHARED-ECONOMIC-EVENT";rows[0]["feature_raw_inputs"]["F01_COMMERCIAL_CONVERSION_MOMENTUM"]["event_group_ids"]=[shared];rows[0]["feature_raw_inputs"]["F06_CONVERSION_RUNWAY"]["event_group_ids"]=[shared];out=self.engine.compute_snapshot(rows)[rows[0]["company_id"]];self.assertEqual(out["features"]["F06_CONVERSION_RUNWAY"]["availability_state"],"NA_FOR_OVERLAP");self.assertTrue(any(a["action"]=="SUPPRESSED" for a in out["anti_double_count_audit"]))
    def test_independent_f04_overlap_allowed(self):
        rows=copy.deepcopy(self.rows);shared="SHARED-INDEPENDENT";rows[0]["feature_raw_inputs"]["F01_COMMERCIAL_CONVERSION_MOMENTUM"]["event_group_ids"]=[shared];rows[0]["feature_raw_inputs"]["F04_EVENT_SURPRISE_VS_PRIOR_EXPECTATION"]["event_group_ids"]=[shared];out=self.engine.compute_snapshot(rows)[rows[0]["company_id"]];self.assertEqual(out["features"]["F04_EVENT_SURPRISE_VS_PRIOR_EXPECTATION"]["availability_state"],"AVAILABLE")


class TestScorer(unittest.TestCase):
    def setUp(self):self.rows=[record(i) for i in range(1,5)];self.scorer=M3Top3V1Engine(CONFIG,"LOCAL-TEST-COMMIT")
    def test_runtime_config_file_hash_binding(self):
        engine=build_engine("LOCAL-TEST-COMMIT",HERE.parent/"configs"/"m3top3_v1.0.json");self.assertEqual(engine.config_hash,"eecde22a7744cff505c624bb6f0bdb11714352a122632238ea68d9cd0fbacb98")
    def test_sio_and_ranking(self):
        result=self.scorer.score_snapshot(self.rows);self.assertEqual(result["ranking_status"],"OFFICIAL_RANKABLE_CANDIDATE");self.assertEqual(result["scorable_eligible_coverage"],"1");self.assertEqual(sorted(o["exact_rank"] for o in result["outputs"]),[1,2,3,4]);required={"pre_gate_score","risk_gate_state","risk_gate_multiplier","final_score","exact_rank","eligibility_state","exclusion_reason","score_status","feature_coverage_ratio","top3_flag","top10_flag","warning_flags","run_id"}
        for o in result["outputs"]:self.assertTrue(required.issubset(o))
    def test_hard_gate_no_double_penalty(self):
        result=self.scorer.score_snapshot(self.rows);o=next(x for x in result["outputs"] if x["company_id"]==self.rows[3]["company_id"]);self.assertEqual(o["risk_gate_state"],"SEVERE");self.assertEqual(o["risk_gate_multiplier"],"0.85");f09=o["feature_trace"]["F09_EXECUTION_THESIS_SAFETY"];self.assertEqual(f09["trace"]["severity"],"LOW");self.assertIn("RISK-HARD",f09["trace"]["excluded_hard_gate_groups"])
    def test_bad_hard_gate_not_applied(self):
        rows=copy.deepcopy(self.rows);rows[3]["hard_risk_gate"]["evidence_status"]="PARTIAL";o=next(x for x in self.scorer.score_snapshot(rows)["outputs"] if x["company_id"]==rows[3]["company_id"]);self.assertEqual(o["risk_gate_state"],"NONE");self.assertIn("RISK_GATE_EVIDENCE_INSUFFICIENT_NOT_APPLIED",o["warning_flags"])
    def test_deterministic_rerun(self):self.assertEqual(self.scorer.score_snapshot(copy.deepcopy(self.rows)),self.scorer.score_snapshot(copy.deepcopy(self.rows)))
    def test_idempotence(self):
        a=self.scorer.score_snapshot(self.rows);b=self.scorer.score_snapshot(self.rows);self.assertEqual(a["run_id"],b["run_id"]);self.assertEqual(a["input_hash"],b["input_hash"]);self.assertEqual(a["outputs"],b["outputs"])
    def test_exact_tie_company_id(self):
        rows=[record(1),record(1)];rows[0]["company_id"]="KRX:AAA";rows[0]["krx_code"]="AAA";rows[1]["company_id"]="KRX:AAB";rows[1]["krx_code"]="AAB";ordered=sorted(self.scorer.score_snapshot(rows)["outputs"],key=lambda x:x["exact_rank"]);self.assertEqual([o["company_id"] for o in ordered],["KRX:AAA","KRX:AAB"])

if __name__=="__main__":unittest.main()
