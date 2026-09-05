from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.m3top3.cli_run_real_input_replay import _prepare_outcome_execution_context
from tools.m3top3.contracts_v1 import ContractError
from tools.m3top3.core import sha256_hex
from tools.m3top3.coverage_limited_replay_v1 import (
    FEATURE_IDS,
    load_population_bytes,
    parse_population_bytes,
)
from tools.m3top3.real_input_replay_v1 import (
    EXPECTED_W1_HOLDING_DATES,
    F02,
    PREDECESSOR_EXECUTABLE_BUNDLE_IDENTITY,
    RealInputReplayError,
    build_strict_w1_mis,
    calculate_w1_raw_outcomes_from_normalized_rows_for_test,
    commit_selection_seal,
    create_selection_seal,
    execute_strict_w1_model_stage,
    execute_w1_outcomes_from_seal,
    load_feature_sidecar,
    load_source_manifest,
    read_selection_seal,
    validate_selection_seal,
    validate_feature_leaves,
    validate_source_manifest,
)


REPO = Path(__file__).resolve().parents[3]
RUN_ID = "AAA-M3TOP3-REAL-INPUT-STRICT-PRAGMATIC-20260905-114150-CODEX-01"
RUN_ROOT = REPO / "control/m3top3/real-input-replay/v1.0/runs" / RUN_ID
INPUT_ROOT = RUN_ROOT / "inputs"
CONFIG = REPO / "tools/m3top3/configs/m3top3_v1.0.json"
CODE_ID = "M3TOP3-REAL-INPUT-EXECUTABLE-BUNDLE-SHA256:TEST"


class TestRealInputReplay(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.population = parse_population_bytes(load_population_bytes(REPO))
        cls.manifest, cls.manifest_hash = load_source_manifest(INPUT_ROOT / "SOURCE_MANIFEST.json")
        cls.leaves, cls.leaf_file_hash = load_feature_sidecar(INPUT_ROOT / "FEATURE_SIDECAR.jsonl")
        cls.stage = execute_strict_w1_model_stage(
            cls.population,
            pmo_run_id=RUN_ID,
            manifest=cls.manifest,
            manifest_content_sha256=cls.manifest_hash,
            leaf_records=cls.leaves,
            repo=REPO,
            config_path=CONFIG,
            code_identity=CODE_ID,
        )
        cls.seal = create_selection_seal(cls.stage, sealed_at_kst="2026-09-05T12:30:00+09:00")

    def _validate_leaves(self, leaves):
        sources = validate_source_manifest(
            self.manifest,
            manifest_content_sha256=self.manifest_hash,
            repo=REPO,
            expected_run_id=RUN_ID,
        )
        return validate_feature_leaves(
            leaves,
            manifest=self.manifest,
            manifest_content_sha256=self.manifest_hash,
            sources=sources,
            population_rows=self.population,
            expected_run_id=RUN_ID,
        )

    def test_01_real_f02_reaches_unchanged_scorer_in_full_batch(self):
        self.assertEqual(len(self.stage["model_input_batch"]), 57)
        self.assertEqual(self.stage["window"]["scoreable_count"], 1)
        self.assertEqual(self.stage["window"]["replay_data_insufficient_count"], 56)
        self.assertEqual(self.stage["window"]["scorer_coverage"], "0.01754385964912280701754385965")
        self.assertEqual(self.stage["window"]["ranking_status"], "INCOMPLETE_COVERAGE")
        scored = self.stage["window"]["coverage_limited_order"]
        self.assertEqual(scored[0]["company_id"], "KRX:005290")
        self.assertEqual(scored[0]["final_score"], "50.00")
        self.assertEqual(scored[0]["score_status"], "PROVISIONAL_MISSING_FEATURES")

    def test_02_value_states_and_missingness_are_not_fabricated(self):
        self.assertEqual(
            self.stage["strict_value_classification"],
            {
                "observed_numeric_leaf_count": 4,
                "derived_control_leaf_count": 4,
                "calculated_relative_change_count": 2,
                "estimated_leaf_count": 0,
                "unverified_or_missing_feature_block_count": 512,
            },
        )
        target = next(row for row in self.stage["model_input_batch"] if row["company_id"] == "KRX:005290")
        self.assertEqual(target["window_anchor_date"], "2024-08-10")
        self.assertEqual(set(target["feature_raw_inputs"]), set(FEATURE_IDS))
        self.assertEqual(target["feature_raw_inputs"][F02]["availability_state"], "AVAILABLE")
        missing = [
            block
            for feature, block in target["feature_raw_inputs"].items()
            if feature != F02
        ]
        self.assertTrue(all(block["availability_state"] == "NOT_FOUND" for block in missing))

    def test_03_exact_observed_changes_are_traceable(self):
        output = next(row for row in self.stage["scorer_output"]["outputs"] if row["company_id"] == "KRX:005290")
        trace = output["feature_trace"][F02]["trace"]
        self.assertEqual(trace["raw_metric_changes"]["revenue"], "0.07273094951360781366485873046")
        self.assertEqual(trace["raw_metric_changes"]["operating_profit"], "0.09671897289586305278174037090")
        self.assertEqual(set(trace["operator_bindings"].values()), {"M3TOP3_F02_RELATIVE_FROM_OBSERVED_PAIR_v1"})

    def test_04_leaf_order_does_not_change_semantic_input_or_score(self):
        reverse = list(reversed(copy.deepcopy(self.leaves)))
        first, first_custody = build_strict_w1_mis(
            self.population,
            pmo_run_id=RUN_ID,
            manifest=self.manifest,
            manifest_content_sha256=self.manifest_hash,
            leaf_records=self.leaves,
            repo=REPO,
            code_identity=CODE_ID,
        )
        second, second_custody = build_strict_w1_mis(
            copy.deepcopy(self.population),
            pmo_run_id=RUN_ID,
            manifest=copy.deepcopy(self.manifest),
            manifest_content_sha256=self.manifest_hash,
            leaf_records=reverse,
            repo=REPO,
            code_identity=CODE_ID,
        )
        self.assertEqual(first, second)
        self.assertEqual(first_custody, second_custody)

    def test_05_predecessor_bundle_cannot_masquerade_as_successor(self):
        with self.assertRaises(RealInputReplayError):
            build_strict_w1_mis(
                self.population,
                pmo_run_id=RUN_ID,
                manifest=self.manifest,
                manifest_content_sha256=self.manifest_hash,
                leaf_records=self.leaves,
                repo=REPO,
                code_identity=PREDECESSOR_EXECUTABLE_BUNDLE_IDENTITY,
            )

    def test_06_duplicate_and_incomplete_leaves_fail_closed(self):
        with self.assertRaises(RealInputReplayError):
            self._validate_leaves([*copy.deepcopy(self.leaves), copy.deepcopy(self.leaves[0])])
        with self.assertRaises(RealInputReplayError):
            self._validate_leaves(copy.deepcopy(self.leaves[:-1]))

    def test_07_manifest_hash_and_source_hash_fail_closed(self):
        bad = copy.deepcopy(self.leaves)
        bad[0]["source_manifest_sha256"] = "0" * 64
        with self.assertRaises(RealInputReplayError):
            self._validate_leaves(bad)
        manifest = copy.deepcopy(self.manifest)
        manifest["sources"][0]["raw_artifact"]["sha256"] = "0" * 64
        with self.assertRaises(RealInputReplayError):
            validate_source_manifest(
                manifest,
                manifest_content_sha256=self.manifest_hash,
                repo=REPO,
                expected_run_id=RUN_ID,
            )

    def test_08_source_path_and_post_cutoff_fail_closed(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["sources"][0]["raw_storage_ref"] = "tools/m3top3/scorer_v1.py"
        with self.assertRaises(RealInputReplayError):
            validate_source_manifest(
                manifest,
                manifest_content_sha256=self.manifest_hash,
                repo=REPO,
                expected_run_id=RUN_ID,
            )
        leaves = copy.deepcopy(self.leaves)
        leaves[0]["publication_at_or_interval"]["latest_possible_at"] = "2024-08-10T00:00:00+09:00"
        with self.assertRaises(RealInputReplayError):
            self._validate_leaves(leaves)

    def test_09_estimated_or_outcome_leaf_fails_closed(self):
        leaves = copy.deepcopy(self.leaves)
        leaves[0]["evidence_kind"] = "ESTIMATED"
        leaves[0]["contains_estimated_input"] = True
        with self.assertRaises(RealInputReplayError):
            self._validate_leaves(leaves)
        leaves = copy.deepcopy(self.leaves)
        leaves[0]["future_return"] = "9"
        with self.assertRaises((RealInputReplayError, ContractError)):
            self._validate_leaves(leaves)

    def test_10_excluded_row_and_bad_unit_fail_closed(self):
        excluded = next(
            row
            for row in self.population
            if row["window_id"] == "W1" and row["historical_eligibility_status"] == "INELIGIBLE_BY_TRADABILITY"
        )
        leaves = copy.deepcopy(self.leaves)
        for leaf in leaves:
            leaf["company_id"] = excluded["company_id"]
            leaf["krx_code"] = excluded["krx_code"]
            leaf["population_row_key"] = excluded["row_key"]
            leaf["record_id"] = leaf["record_id"].replace("005290", excluded["krx_code"])
        with self.assertRaises(RealInputReplayError):
            self._validate_leaves(leaves)
        leaves = copy.deepcopy(self.leaves)
        leaves[0]["unit_or_category"] = "KRW"
        with self.assertRaises(RealInputReplayError):
            self._validate_leaves(leaves)

    def test_11_strict_json_loader_rejects_duplicate_float_and_nonfinite(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            duplicate = root / "duplicate.json"
            duplicate.write_text('{"a":1,"a":2}', encoding="utf-8")
            with self.assertRaises(RealInputReplayError):
                load_source_manifest(duplicate)
            floating = root / "float.jsonl"
            floating.write_text('{"value":1.2}\n', encoding="utf-8")
            with self.assertRaises(RealInputReplayError):
                load_feature_sidecar(floating)
            nonfinite = root / "nan.jsonl"
            nonfinite.write_text('{"value":NaN}\n', encoding="utf-8")
            with self.assertRaises(RealInputReplayError):
                load_feature_sidecar(nonfinite)

    def test_12_selection_seal_binds_full_denominator_and_is_durable(self):
        payload = self.seal["sealed_payload"]
        self.assertEqual(len(payload["include_57_results"]), 57)
        self.assertEqual(len(payload["outcome_measurement_cohort"]), 1)
        self.assertEqual(payload["official_top3_state"], "NOT_AVAILABLE_INCOMPLETE_57_ROW_SCORE_COVERAGE")
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "SELECTION_SEAL.json"
            first = commit_selection_seal(path, self.seal)
            second = commit_selection_seal(path, copy.deepcopy(self.seal))
            self.assertEqual(first, second)
            self.assertEqual(read_selection_seal(path), self.seal)
            changed = copy.deepcopy(self.seal)
            changed["sealed_at_kst"] = "2026-09-05T12:31:00+09:00"
            with self.assertRaises(RealInputReplayError):
                commit_selection_seal(path, changed)

    def test_13_tampered_seal_fails(self):
        tampered = copy.deepcopy(self.seal)
        tampered["sealed_payload"]["include_57_results"][0]["final_score"] = "99"
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "SELECTION_SEAL.json"
            path.write_text(json.dumps(tampered), encoding="utf-8")
            with self.assertRaises(RealInputReplayError):
                read_selection_seal(path)

    def _price_fixture(self):
        rows = []
        selected_code = "005290"
        for item in self.seal["sealed_payload"]["include_57_results"]:
            code = item["krx_code"]
            values = []
            for day in EXPECTED_W1_HOLDING_DATES:
                value = (day, 100, 101, 99, 100)
                if code == selected_code and day == "2024-08-12":
                    value = (day, 100, 105, 80, 100)
                elif code == selected_code and day == "2024-09-02":
                    value = (day, 110, 120, 100, 115)
                elif code == selected_code and day == "2024-11-08":
                    value = (day, 105, 130, 90, 105)
                elif code != selected_code and day == "2024-09-02":
                    value = (day, 105, 110, 100, 105)
                elif code != selected_code and day == "2024-11-08":
                    value = (day, 110, 120, 105, 110)
                values.append(value)
            values.append(
                ("2024-11-11", 110, 115, 105, 112)
                if code == selected_code
                else ("2024-11-11", 105, 110, 100, 105)
            )
            for day, opened, high, low, close in values:
                rows.append(
                    {"date": day, "krx_code": code, "open": opened, "high": high, "low": low, "close": close}
                )
        return rows

    def test_14_w1_outcome_arithmetic_and_boundaries(self):
        result = calculate_w1_raw_outcomes_from_normalized_rows_for_test(
            self.seal,
            self._price_fixture(),
            price_binding={"dataset_identity_sha256": "TEST", "source_semantics": "RAW"},
        )
        self.assertTrue(result["complete_raw_rank_denominator"])
        selected = result["selected_outcome_ledger"][0]
        self.assertEqual(selected["entry_open_observed_raw"], "100")
        self.assertEqual(selected["mfe_peak_high_observed_raw"], "130")
        self.assertEqual(selected["raw_unadjusted_mfe_return_calculated"], "0.3")
        self.assertEqual(selected["minimum_valid_low_observed_raw"], "80")
        self.assertEqual(selected["raw_unadjusted_exit_open_return_calculated"], "0.1")
        self.assertEqual(selected["raw_unadjusted_horizon_close_return_calculated"], "0.05")
        self.assertEqual(selected["raw_unadjusted_peak_to_exit_giveback_calculated"], "0.2")
        self.assertEqual(selected["w1_include57_raw_unadjusted_mfe_return_rank"], 1)
        self.assertIsNone(selected["mae_return"])

    def test_15_incomplete_denominator_suppresses_every_raw_rank(self):
        rows = self._price_fixture()
        missing_code = next(code for code in {row["krx_code"] for row in rows} if code != "005290")
        rows = [row for row in rows if not (row["krx_code"] == missing_code and row["date"] == "2024-09-02")]
        result = calculate_w1_raw_outcomes_from_normalized_rows_for_test(
            self.seal,
            rows,
            price_binding={"dataset_identity_sha256": "TEST", "source_semantics": "RAW"},
        )
        self.assertFalse(result["complete_raw_rank_denominator"])
        self.assertTrue(
            all(row["w1_include57_raw_unadjusted_mfe_return_rank"] is None for row in result["comparison_outcome_ledger"])
        )

    def test_16_zero_entry_duplicate_and_malformed_code_fail_safely(self):
        rows = self._price_fixture()
        zero = copy.deepcopy(rows)
        next(row for row in zero if row["krx_code"] == "005290" and row["date"] == "2024-08-12")["open"] = 0
        result = calculate_w1_raw_outcomes_from_normalized_rows_for_test(
            self.seal,
            zero,
            price_binding={"dataset_identity_sha256": "TEST"},
        )
        selected = result["selected_outcome_ledger"][0]
        self.assertEqual(selected["measurement_state"], "NOT_MEASURED_REQUIRED_ENDPOINT_OR_PATH_INVALID")
        duplicate = [*rows, copy.deepcopy(rows[0])]
        with self.assertRaises(RealInputReplayError):
            calculate_w1_raw_outcomes_from_normalized_rows_for_test(self.seal, duplicate, price_binding={})
        malformed = copy.deepcopy(rows)
        malformed[0]["krx_code"] = "5290"
        with self.assertRaises(RealInputReplayError):
            calculate_w1_raw_outcomes_from_normalized_rows_for_test(self.seal, malformed, price_binding={})

    def test_17_public_outcome_path_verifies_seal_before_price_access(self):
        order = []

        def read_first(_):
            order.append("seal")
            return {
                "receipt_type": "DURABLE_SELECTION_SEAL_CANONICAL_READBACK",
                "selection_seal": self.seal,
                "selection_seal_id": self.seal["seal_id"],
                "path": "seal.json",
                "byte_size": 1,
                "file_sha256": "TEST",
            }

        def runtime_second(_):
            order.append("runtime")
            return {"binding_state": "TEST"}

        def bind_third(_):
            order.append("price")
            raise RealInputReplayError("stop after proving order")

        with patch(
            "tools.m3top3.real_input_replay_v1._read_durable_selection_seal_receipt",
            side_effect=read_first,
        ), patch(
            "tools.m3top3.real_input_replay_v1._verify_outcome_runtime_before_price_access",
            side_effect=runtime_second,
        ), patch(
            "tools.m3top3.real_input_replay_v1._bind_price_components_after_seal",
            side_effect=bind_third,
        ):
            with self.assertRaises(RealInputReplayError):
                execute_w1_outcomes_from_seal(
                    selection_seal_path="seal.json",
                    expected_selection_seal_id=self.seal["seal_id"],
                    current_executable_bundle_identity=CODE_ID,
                    price_2024_path="2024.parquet",
                    price_2025_path="2025.parquet",
                    price_2026_path="2026.parquet",
                )
        self.assertEqual(order, ["seal", "runtime", "price"])

    def test_18_outcome_code_identity_mismatch_fails_before_runtime_and_price(self):
        receipt = {
            "receipt_type": "DURABLE_SELECTION_SEAL_CANONICAL_READBACK",
            "selection_seal": self.seal,
            "selection_seal_id": self.seal["seal_id"],
            "path": "seal.json",
            "byte_size": 1,
            "file_sha256": "TEST",
        }
        with patch(
            "tools.m3top3.real_input_replay_v1._read_durable_selection_seal_receipt",
            return_value=receipt,
        ), patch(
            "tools.m3top3.real_input_replay_v1._verify_outcome_runtime_before_price_access"
        ) as runtime, patch(
            "tools.m3top3.real_input_replay_v1._bind_price_components_after_seal"
        ) as price:
            with self.assertRaises(RealInputReplayError):
                execute_w1_outcomes_from_seal(
                    selection_seal_path="seal.json",
                    expected_selection_seal_id=self.seal["seal_id"],
                    current_executable_bundle_identity="M3TOP3-REAL-INPUT-EXECUTABLE-BUNDLE-SHA256:OTHER",
                    price_2024_path="2024.parquet",
                    price_2025_path="2025.parquet",
                    price_2026_path="2026.parquet",
                )
        runtime.assert_not_called()
        price.assert_not_called()

    def test_19_outcome_cli_dirty_context_fails_before_bundle_binding(self):
        with patch(
            "tools.m3top3.cli_run_real_input_replay.read_selection_seal",
            return_value=self.seal,
        ), patch(
            "tools.m3top3.cli_run_real_input_replay._assert_clean_repo",
            side_effect=ValueError("dirty"),
        ), patch(
            "tools.m3top3.cli_run_real_input_replay._bind_successor_bundle"
        ) as bundle:
            with self.assertRaises(ValueError):
                _prepare_outcome_execution_context(REPO, Path("seal.json"))
        bundle.assert_not_called()

    def test_20_rehashed_tampered_full_wm_tuple_still_fails(self):
        tampered = copy.deepcopy(self.seal)
        tampered["sealed_payload"]["window_mapping"]["exit_trade_date"] = "2024-11-12"
        digest = sha256_hex(tampered["sealed_payload"])
        tampered["seal_content_sha256"] = digest
        tampered["seal_id"] = f"m3selection_{digest[:32]}"
        with self.assertRaises(RealInputReplayError):
            validate_selection_seal(tampered)

    def test_21_missing_entire_bound_market_date_fails_closed(self):
        rows = [row for row in self._price_fixture() if row["date"] != "2024-09-02"]
        with self.assertRaises(RealInputReplayError):
            calculate_w1_raw_outcomes_from_normalized_rows_for_test(
                self.seal,
                rows,
                price_binding={"dataset_identity_sha256": "TEST"},
            )

    def test_22_in_memory_helper_cannot_claim_durable_firewall(self):
        result = calculate_w1_raw_outcomes_from_normalized_rows_for_test(
            self.seal,
            self._price_fixture(),
            price_binding={"dataset_identity_sha256": "TEST"},
        )
        self.assertEqual(result["execution_proof_state"], "IN_MEMORY_ARITHMETIC_ONLY_NO_DURABLE_FIREWALL_PROOF")
        self.assertFalse(result["outcome_firewall"]["selection_seal_readback_verified_before_price_component_access"])
        self.assertIn("NO_OPERATIONAL_OUTCOME_CLAIM_FROM_IN_MEMORY_TEST_HELPER", result["claim_ceiling"])

    def test_23_bound_w1_holding_spine_has_58_exact_dates(self):
        self.assertEqual(len(EXPECTED_W1_HOLDING_DATES), 58)
        self.assertEqual(EXPECTED_W1_HOLDING_DATES[0], "2024-08-12")
        self.assertEqual(EXPECTED_W1_HOLDING_DATES[-1], "2024-11-08")
        self.assertNotIn("2024-08-15", EXPECTED_W1_HOLDING_DATES)


if __name__ == "__main__":
    unittest.main()
