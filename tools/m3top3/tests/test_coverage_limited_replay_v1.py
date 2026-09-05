from __future__ import annotations

import copy
import unittest
from pathlib import Path

from tools.m3top3.coverage_limited_replay_v1 import (
    EXPECTED_COUNTS,
    FEATURE_IDS,
    CoverageLimitedReplayError,
    build_window_mis,
    execute_model_stage,
    finalize_without_scored_rows,
    load_population_bytes,
    parse_population_bytes,
    scorecard_markdown,
    validate_replay_mis_shape,
)


REPO = Path(__file__).resolve().parents[3]
CONFIG = REPO / "tools/m3top3/configs/m3top3_v1.0.json"
RUN_ID = "TEST-COVERAGE-LIMITED-REPLAY"
CODE_ID = "TEST-CODE-IDENTITY"


class TestCoverageLimitedReplay(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.population = parse_population_bytes(load_population_bytes(REPO))

    def test_01_exact_population_partition(self):
        self.assertEqual(len(self.population), 1016)
        for window_id, expected in EXPECTED_COUNTS.items():
            rows = [row for row in self.population if row["window_id"] == window_id]
            observed = {
                state: sum(row["historical_eligibility_status"] == state for row in rows)
                for state in expected
            }
            self.assertEqual(observed, expected)

    def test_02_only_complete_include_batch_enters_scorer(self):
        rows = build_window_mis("W1", self.population, pmo_run_id=RUN_ID, code_identity=CODE_ID)
        self.assertEqual(len(rows), 57)
        self.assertTrue(all(row["eligibility_state"] == "ELIGIBLE" for row in rows))
        self.assertEqual(len({row["company_id"] for row in rows}), 57)

    def test_03_explicit_missing_blocks_have_no_scoring_values(self):
        rows = build_window_mis("W1", self.population, pmo_run_id=RUN_ID, code_identity=CODE_ID)
        validate_replay_mis_shape(rows, CODE_ID)
        for row in rows:
            self.assertEqual(set(row["feature_raw_inputs"]), set(FEATURE_IDS))
            for block in row["feature_raw_inputs"].values():
                self.assertEqual(block["availability_state"], "NOT_FOUND")
                self.assertNotIn("value", block)
                self.assertNotIn("score", block)

    def test_04_missing_block_with_value_fails_closed(self):
        rows = build_window_mis("W1", self.population, pmo_run_id=RUN_ID, code_identity=CODE_ID)
        bad = copy.deepcopy(rows)
        bad[0]["feature_raw_inputs"][FEATURE_IDS[0]]["commercial_state"] = "NONE"
        with self.assertRaises(CoverageLimitedReplayError):
            validate_replay_mis_shape(bad, CODE_ID)

    def test_05_all_windows_execute_once_as_include_batches(self):
        result = execute_model_stage(
            self.population,
            pmo_run_id=RUN_ID,
            code_identity=CODE_ID,
            config_path=CONFIG,
        )
        self.assertEqual(result["totals"]["u127_count"], 1016)
        self.assertEqual(result["totals"]["replay_include_eligibility_count"], 465)
        self.assertEqual(result["totals"]["exclude_proven_count"], 37)
        self.assertEqual(result["totals"]["exclude_unresolved_count"], 514)
        self.assertEqual(result["totals"]["replay_data_insufficient_count"], 465)
        self.assertEqual(result["totals"]["scoreable_count"], 0)
        self.assertEqual(len(result["selection_ledger"]), 1016)
        self.assertEqual(len({(r["window_id"], r["company_id"]) for r in result["selection_ledger"]}), 1016)
        self.assertTrue(all(window["ranking_status"] == "INCOMPLETE_COVERAGE" for window in result["windows"]))

    def test_06_execution_is_deterministic(self):
        kwargs = {
            "pmo_run_id": RUN_ID,
            "code_identity": CODE_ID,
            "config_path": CONFIG,
        }
        first = execute_model_stage(self.population, **kwargs)
        second = execute_model_stage(copy.deepcopy(self.population), **kwargs)
        self.assertEqual(first, second)

    def test_07_zero_scoreable_finalization_does_not_load_outcomes(self):
        result = execute_model_stage(
            self.population,
            pmo_run_id=RUN_ID,
            code_identity=CODE_ID,
            config_path=CONFIG,
        )
        final = finalize_without_scored_rows(result)
        self.assertEqual(final["outcome_stage_state"], "NOT_MEASURED_ZERO_SCORED_SELECTIONS")
        self.assertIn("OUTCOME_VALUE_LOAD_SKIPPED_ZERO_SCORED_SELECTIONS", final["stage_sequence"])
        self.assertFalse(final["outcome_firewall"]["future_price_values_loaded_before_model_selection"])

    def test_08_markdown_distinguishes_zero_scoreable_from_zero_performance(self):
        result = execute_model_stage(
            self.population,
            pmo_run_id=RUN_ID,
            code_identity=CODE_ID,
            config_path=CONFIG,
        )
        rendered = scorecard_markdown(finalize_without_scored_rows(result))
        self.assertIn("executed zero-scoreable scorecard, not a zero-performance result", rendered)


if __name__ == "__main__":
    unittest.main()
