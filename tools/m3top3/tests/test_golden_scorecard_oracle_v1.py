from __future__ import annotations

import json
import unittest
from decimal import Decimal
from pathlib import Path

from tools.m3top3.features_v1 import FEATURE_IDS
from tools.m3top3.golden_scorecard_oracle_v1 import verify_expected_binding
from tools.m3top3.runtime_v1 import build_engine


REPO = Path(__file__).resolve().parents[3]
RUN_DIR = REPO / "control/m3top3/first-scorecard/v1.0/runs/AAA-M3TOP3-FIRST-SCORECARD-20260905-093656-CODEX-01"
FIXTURE = RUN_DIR / "evidence/input-package/extracted/AAA_M3TOP3_GR_FIXTURE_SET_v0.2_WORKING.json"
EXPECTED = RUN_DIR / "GOLDEN_EXPECTED_OUTPUT_BINDINGS_v1.0_WORKING.json"
CONFIG = REPO / "tools/m3top3/configs/m3top3_v1.0.json"
ALIASES = {f"F{index:02d}": feature_id for index, feature_id in enumerate(FEATURE_IDS, start=1)}


class ControlledFeatureEngine:
    def __init__(self, values):
        self.values = values

    def compute_snapshot(self, records, hard_gate_groups=None):
        result = {}
        for record in records:
            features = {}
            for alias, value in self.values[record["company_id"]].items():
                feature_id = ALIASES[alias]
                features[feature_id] = {
                    "feature_id": feature_id,
                    "score": None if value is None else str(value),
                    "availability_state": "NOT_FOUND" if value is None else "AVAILABLE",
                    "missing_reason": "CONTROLLED_NULL" if value is None else None,
                    "event_group_ids": [],
                    "source_lineage_refs": ["CONTROLLED_GOLDEN_FIXTURE"],
                    "trace": {"fixture_adapter": True},
                }
            result[record["company_id"]] = {"features": features, "anti_double_count_audit": []}
        return result


def record(company_id, snapshot, raw_scores):
    code = company_id.split(":", 1)[1]
    return {
        "snapshot_id": f"GOLDEN-{snapshot}",
        "snapshot_date": snapshot,
        "snapshot_cutoff_at": f"{snapshot}T23:59:59+09:00",
        "snapshot_content_hash_or_revision": "GOLDEN-CONTROLLED-v1",
        "window_anchor_date": snapshot,
        "window_mapping_version": "WM-v1.1",
        "company_id": company_id,
        "krx_code": code,
        "universe_release_id": "GOLDEN-CONTROLLED",
        "eligibility_state": "ELIGIBLE",
        "model_version": "M3TOP3-v1.0",
        "feature_schema_version": "M3TOP3-FEATURE-SCHEMA_v1.0_WORKING",
        "scorer_version": "M3TOP3-GATED-LINEAR_v1.0_WORKING",
        "weight_version": "M3TOP3-WEIGHT-VERSION_v1.0_WORKING",
        "model_input_schema_version": "MIS-v1.0",
        "input_release_or_hash": "GOLDEN-CONTROLLED-v1",
        "code_or_executable_identity": "GOLDEN-SCORER-CHECK",
        "feature_raw_inputs": {
            ALIASES[alias]: {"availability_state": "NOT_FOUND", "missing_reason": "CONTROLLED_ADAPTER"}
            for alias in raw_scores
        },
        "hard_risk_gate": {"state": "NONE"},
    }


class TestGoldenScorecardOracle(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = json.loads(FIXTURE.read_text(encoding="utf-8"))
        cls.fixtures = {row["fixture_id"]: row for row in cls.document["fixtures"]}
        cls.expected = json.loads(EXPECTED.read_text(encoding="utf-8"))

    def test_01_independent_expected_binding(self):
        report = verify_expected_binding(FIXTURE, EXPECTED)
        self.assertEqual(report["state"], "PASS_WITH_EXPLICIT_GF09_CONTROL_GAP")

    def test_02_gf09_gap_is_not_defaulted(self):
        gf09 = self.expected["fixtures"]["AAA-M3TOP3-GR-FX-09"]
        self.assertEqual(gf09["state"], "CONTROL_GAP_NOT_EXACTLY_BOUND")
        self.assertTrue(all(row["final_score"] is None for row in gf09["rows"]))
        self.assertNotIn("order", gf09)

    def test_03_production_scorer_matches_exact_gf08_and_gf14_ranking(self):
        for fixture_id in ("AAA-M3TOP3-GR-FX-08", "AAA-M3TOP3-GR-FX-14"):
            fixture = self.fixtures[fixture_id]
            payload = fixture["controlled_payload"]
            source_rows = list(payload.values()) if fixture_id.endswith("08") else payload["rows"]
            scores = {row["company_id"]: row["feature_scores"] for row in source_rows}
            records = [record(row["company_id"], fixture["snapshot_cutoff"], row["feature_scores"]) for row in source_rows]
            engine = build_engine("GOLDEN-SCORER-CHECK", CONFIG)
            engine.features = ControlledFeatureEngine(scores)
            actual = engine.score_snapshot(records)
            actual_order = [
                row["company_id"]
                for row in sorted(actual["outputs"], key=lambda item: item["exact_rank"])
            ]
            expected_rows = self.expected["fixtures"][fixture_id]["rows"]
            self.assertEqual(actual_order, [row["company_id"] for row in expected_rows])
            actual_by_id = {row["company_id"]: row for row in actual["outputs"]}
            for expected_row in expected_rows:
                self.assertEqual(
                    Decimal(actual_by_id[expected_row["company_id"]]["final_score"]),
                    Decimal(expected_row["final_score"]),
                )


if __name__ == "__main__":
    unittest.main()
