from __future__ import annotations

import copy
import unittest

from tools.m3top3.admission import EXIT_INTEGRITY, M3Top3AdmissionError
from tools.m3top3.backtest import (
    FULL_UNIVERSE_VIEW_VERSION,
    RESULT_CONTRACT_VERSION,
    RUN_IDENTITY_FIELDS,
    SELECTED_TOP3_METRICS_VIEW_VERSION,
    MetricsEngine,
    verify_full_run_result,
)
from tools.m3top3.core import deterministic_id


def _fixture(*, fourth_pending: bool = False) -> dict:
    ranked = []
    full = []
    returns = ("0.1", "0.2", "0.3", "-0.75")
    mfes = ("120", "130", "140", "110")
    for rank in range(1, 5):
        score_id = f"S{rank}"
        ranked.append({"model_score_id": score_id, "rank": rank, "selected_top3": rank <= 3})
        pending = fourth_pending and rank == 4
        full.append(
            {
                "model_score_id": score_id,
                "rank": rank,
                "selected_top3": rank <= 3,
                "entry": "100",
                "mfe": None if pending else mfes[rank - 1],
                "return_ratio": None if pending else returns[rank - 1],
                "outcome_validity": "CA_PENDING" if pending else "VALID",
                "status": "PRELIMINARY" if pending else "VALIDATION",
            }
        )
    selected = full[:3]
    payload = {field: f"value:{field}" for field in RUN_IDENTITY_FIELDS}
    payload.update(
        {
            "result_contract_version": RESULT_CONTRACT_VERSION,
            "selected_top3_metrics_view_version": SELECTED_TOP3_METRICS_VIEW_VERSION,
            "full_universe_view_version": FULL_UNIVERSE_VIEW_VERSION,
            "result_revision": 0,
        }
    )
    top3_metrics = MetricsEngine().summarize(selected)
    full_metrics = MetricsEngine().summarize_full_eligible_universe(full, 4)
    return {
        "result_contract_version": RESULT_CONTRACT_VERSION,
        "selected_top3_metrics_view_version": SELECTED_TOP3_METRICS_VIEW_VERSION,
        "full_universe_view_version": FULL_UNIVERSE_VIEW_VERSION,
        "validation_run_identity_payload": payload,
        "validation_run_id": deterministic_id("validationrun", payload),
        "result_revision": 0,
        "status": "PRELIMINARY" if fourth_pending else "EXPERIMENTAL",
        "price_source_semantics": "RAW_IMMUTABLE" if fourth_pending else "PRICE_WORKING_ADJUSTED",
        "eligible_count": 4,
        "ranked_count": 4,
        "ranked": ranked,
        "top3": ranked[:3],
        "selected_top3_count": 3,
        "outcomes": selected,
        "outcome_count": 3,
        "selected_top3_outcomes": selected,
        "selected_top3_outcome_count": 3,
        "metrics": top3_metrics,
        "selected_top3_metrics": top3_metrics,
        "full_universe_outcomes": full,
        "full_universe_outcome_count": 4,
        "full_universe_metrics": full_metrics,
    }


class SemanticPreservationV04Tests(unittest.TestCase):
    def assert_code(self, code: str, action) -> None:
        with self.assertRaises(M3Top3AdmissionError) as caught:
            action()
        self.assertEqual((caught.exception.code, caught.exception.exit_code), (code, EXIT_INTEGRITY))

    def test_legacy_metrics_population_is_selected_top3(self) -> None:
        result = _fixture()
        self.assertEqual(result["metrics"]["mean_return"], "0.2")
        self.assertEqual(result["metrics"]["win_rate"], "1")
        self.assertEqual(result["selected_top3_metrics"], result["metrics"])
        self.assertEqual(len(result["outcomes"]), 3)
        self.assertEqual(len(result["full_universe_outcomes"]), 4)
        verify_full_run_result(result)

    def test_non_top3_pending_does_not_withhold_legacy_top3_metrics(self) -> None:
        result = _fixture(fourth_pending=True)
        self.assertEqual(result["metrics"]["mean_return"], "0.2")
        self.assertEqual(result["metrics"]["valid_return_count"], 3)
        self.assertEqual(result["full_universe_metrics"]["metrics_status"], "WITHHELD_PENDING_OUTCOMES")
        verify_full_run_result(result)

    def test_full_e_cannot_masquerade_as_legacy_outcomes(self) -> None:
        result = _fixture()
        result["outcomes"] = copy.deepcopy(result["full_universe_outcomes"])
        result["outcome_count"] = 4
        self.assert_code("TOP3_PROJECTION_MISMATCH", lambda: verify_full_run_result(result))

    def test_top3_metrics_are_independently_recomputed(self) -> None:
        result = _fixture()
        result["metrics"]["mean_return"] = "-0.0375"
        self.assert_code("METRIC_DENOMINATOR_INTEGRITY_FAILURE", lambda: verify_full_run_result(result))

    def test_selected_top3_metric_alias_cannot_drift(self) -> None:
        result = _fixture()
        result["selected_top3_metrics"]["mean_return"] = "-0.0375"
        self.assert_code("METRIC_DENOMINATOR_INTEGRITY_FAILURE", lambda: verify_full_run_result(result))

    def test_full_universe_view_is_mandatory(self) -> None:
        result = _fixture()
        result.pop("full_universe_outcomes")
        self.assert_code("FULL_OUTCOME_SET_MEMBER_MISSING", lambda: verify_full_run_result(result))

    def test_result_contract_version_is_bound_into_run_identity(self) -> None:
        result = _fixture()
        result["validation_run_identity_payload"]["result_contract_version"] += "-FORGED"
        self.assert_code("RUN_ID_LINEAGE_MISMATCH", lambda: verify_full_run_result(result))

    def test_each_view_version_changes_run_identity(self) -> None:
        result = _fixture()
        payload = result["validation_run_identity_payload"]
        for field in (
            "result_contract_version",
            "selected_top3_metrics_view_version",
            "full_universe_view_version",
        ):
            changed = copy.deepcopy(payload)
            changed[field] += "-MUTATED"
            self.assertNotEqual(
                deterministic_id("validationrun", changed),
                result["validation_run_id"],
                field,
            )

    def test_result_view_version_alias_cannot_drift(self) -> None:
        result = _fixture()
        result["selected_top3_metrics_view_version"] += "-FORGED"
        self.assert_code("RUN_ID_LINEAGE_MISMATCH", lambda: verify_full_run_result(result))


if __name__ == "__main__":
    unittest.main()
