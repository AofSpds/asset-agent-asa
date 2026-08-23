from __future__ import annotations

import ast
import copy
import hashlib
import os
import sys
import tempfile
import unittest
from datetime import date
from decimal import Decimal
from pathlib import Path


REMEDIATION_ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_ROOT = Path(
    os.environ.get("M3TOP3_CANDIDATE_ROOT", REMEDIATION_ROOT / "r_wp4_03_final_candidate_v0_4")
).resolve()
VALIDATED_PARENT_ROOT = Path(
    os.environ.get("M3TOP3_LEGACY_REFERENCE_ROOT", REMEDIATION_ROOT / "runtime_checkout")
).resolve()
sys.path.insert(0, str(CANDIDATE_ROOT))

from tools.m3top3.admission import M3Top3AdmissionError, admit_claim_locks  # noqa: E402
from tools.m3top3.backtest import MetricsEngine, verify_full_run_result  # noqa: E402
from tools.m3top3.core import deterministic_id  # noqa: E402
from tools.m3top3.ledger import PredictionLedger  # noqa: E402
from tools.m3top3.providers import (  # noqa: E402
    InMemoryFeatureProvider,
    StaticUniverseProvider,
    UniverseState,
)
from tools.m3top3.snapshot import SnapshotBuildConfig, SnapshotBuilder, SnapshotStore  # noqa: E402
from tools.m3top3.tests._known_failure_helpers import (  # noqa: E402
    business_dates,
    diagnostic_runner,
    price_provider,
)


CODES = ("005930", "000660", "035420", "051910")
COMPANIES = ("C1", "C2", "C3", "C4")
EXIT_OPEN = {"005930": 110, "000660": 120, "035420": 130, "051910": 10}
HOLD_HIGH = {"005930": 120, "000660": 130, "035420": 140, "051910": 110}


def _method_source(path: Path, class_name: str, method_name: str) -> str:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for child in node.body:
                if isinstance(child, ast.FunctionDef) and child.name == method_name:
                    segment = ast.get_source_segment(source, child)
                    if segment is None:
                        raise AssertionError(f"source unavailable for {class_name}.{method_name}")
                    return segment
    raise AssertionError(f"missing {class_name}.{method_name} in {path}")


def _source_sha(path: Path, class_name: str, method_name: str) -> str:
    return hashlib.sha256(_method_source(path, class_name, method_name).encode("utf-8")).hexdigest()


def _legacy_reference(rows: list[dict]) -> dict[str, str | int | None]:
    returns = [Decimal(str(row["return_ratio"])) for row in rows if row.get("return_ratio") is not None]
    mfe_returns = [
        (Decimal(str(row["mfe"])) / Decimal(str(row["entry"]))) - Decimal("1")
        for row in rows
        if row.get("entry") is not None and row.get("mfe") is not None
    ]
    return {
        "valid_return_count": len(returns),
        "mean_return": str(sum(returns) / Decimal(len(returns))) if returns else None,
        "median_return": str(sorted(returns)[len(returns) // 2]) if len(returns) % 2 else (
            str((sorted(returns)[len(returns) // 2 - 1] + sorted(returns)[len(returns) // 2]) / Decimal("2"))
            if returns
            else None
        ),
        "win_rate": str(Decimal(sum(value > 0 for value in returns)) / Decimal(len(returns))) if returns else None,
        "mean_mfe_return": str(sum(mfe_returns) / Decimal(len(mfe_returns))) if mfe_returns else None,
    }


class SEM001V04AcceptanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.dates = business_dates(count=30)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _price_rows(self, omit_codes: frozenset[str] = frozenset()) -> list[dict]:
        rows: list[dict] = []
        for code in CODES:
            if code in omit_codes:
                continue
            for index, trading_date in enumerate(self.dates):
                open_value = EXIT_OPEN[code] if index == 6 else 100
                close_value = open_value
                high_value = max(open_value, HOLD_HIGH[code])
                low_value = min(open_value, 90)
                rows.append(
                    {
                        "date": trading_date.isoformat(),
                        "code": code,
                        "open": open_value,
                        "high": high_value,
                        "low": low_value,
                        "close": close_value,
                        "volume": 1000 + index,
                    }
                )
        return rows

    def _run_four(self, omit_codes: frozenset[str] = frozenset()) -> dict:
        price = price_provider(self.root, self._price_rows(omit_codes))
        states = [
            UniverseState(company, code, date(2020, 1, 1), None, True, True, f"U{index}")
            for index, (company, code) in enumerate(zip(COMPANIES, CODES), 1)
        ]
        features = InMemoryFeatureProvider(
            [
                {
                    "company_id": company,
                    "feature_id": "diagnostic_score",
                    "value": str(10 - index),
                    "publication_at": "2025-01-02T10:00:00+09:00",
                }
                for index, company in enumerate(COMPANIES)
            ]
        )
        builder = SnapshotBuilder(
            StaticUniverseProvider(states, "U-SEM-001", "DIAGNOSTIC"),
            features,
            price,
            SnapshotBuildConfig(),
        )
        built = builder.build(self.dates[0])
        snapshot_root = self.root / "snapshots"
        SnapshotStore(snapshot_root).write(built, {"generator_version": "sem-001-independent-v0.1"})
        runner, _ = diagnostic_runner(price, self.dates)
        return runner.run_snapshot(
            snapshot_root / self.dates[0].isoformat(),
            self.root / "results",
            PredictionLedger(self.root / "prediction-ledger.jsonl"),
        )

    def assert_integrity_code(self, code: str, action) -> None:
        with self.assertRaises(M3Top3AdmissionError) as caught:
            action()
        self.assertEqual(caught.exception.code, code)
        self.assertEqual(caught.exception.exit_code, 3)

    def test_sem_001_a_legacy_metrics_formula_uses_top3_only(self) -> None:
        top3 = [
            {"entry": "100", "mfe": "120", "return_ratio": "0.1", "outcome_validity": "CA_PENDING"},
            {"entry": "100", "mfe": "130", "return_ratio": "0.2", "outcome_validity": "CA_PENDING"},
            {"entry": "100", "mfe": "140", "return_ratio": "0.3", "outcome_validity": "CA_PENDING"},
        ]
        observed = MetricsEngine().summarize(top3)
        expected = _legacy_reference(top3)
        for key, value in expected.items():
            self.assertEqual(observed.get(key), value, key)

    def test_sem_001_b_c_runtime_preserves_top3_and_full_e_separately(self) -> None:
        result = self._run_four()
        self.assertEqual(result["ranked_count"], 4)
        self.assertEqual(result["selected_top3_count"], 3)
        self.assertEqual(result["outcome_count"], 3)
        self.assertEqual(result["selected_top3_outcome_count"], 3)
        self.assertEqual(result["full_universe_outcome_count"], 4)
        self.assertEqual(result["outcomes"], result["selected_top3_outcomes"])
        self.assertEqual([row["rank"] for row in result["outcomes"]], [1, 2, 3])
        self.assertEqual([row["rank"] for row in result["full_universe_outcomes"]], [1, 2, 3, 4])
        expected = _legacy_reference(result["outcomes"])
        for key, value in expected.items():
            self.assertEqual(result["metrics"].get(key), value, key)
        self.assertEqual(result["metrics"].get("mean_return"), "0.2")
        self.assertEqual(result["metrics"].get("win_rate"), "1")
        self.assertEqual(result["selected_top3_metrics"], result["metrics"])
        full_metrics = result["full_universe_metrics"]
        self.assertEqual(full_metrics.get("eligible_count"), 4)
        self.assertEqual(full_metrics.get("outcome_record_count"), 4)

    def test_sem_001_b_non_top3_pending_does_not_withhold_top3_metrics(self) -> None:
        result = self._run_four(frozenset({CODES[3]}))
        fourth = next(row for row in result["full_universe_outcomes"] if row["rank"] == 4)
        self.assertIsNone(fourth["return_ratio"])
        self.assertEqual(result["metrics"].get("valid_return_count"), 3)
        self.assertEqual(result["metrics"].get("mean_return"), "0.2")
        self.assertEqual(result["metrics"].get("win_rate"), "1")
        self.assertNotEqual(result["metrics"].get("metrics_status"), "WITHHELD_PENDING_OUTCOMES")
        self.assertGreaterEqual(result["full_universe_metrics"].get("pending_outcome_count", 0), 1)

    def test_sem_001_d_full_e_cannot_masquerade_as_legacy_outcomes(self) -> None:
        result = self._run_four()
        forged = copy.deepcopy(result)
        forged["outcomes"] = copy.deepcopy(forged["full_universe_outcomes"])
        forged["outcome_count"] = len(forged["outcomes"])
        self.assert_integrity_code("TOP3_PROJECTION_MISMATCH", lambda: verify_full_run_result(forged))

    def test_sem_001_e_top3_metric_value_is_independently_recomputed(self) -> None:
        result = self._run_four()
        forged = copy.deepcopy(result)
        forged["metrics"]["mean_return"] = "-0.075"
        self.assert_integrity_code("METRIC_DENOMINATOR_INTEGRITY_FAILURE", lambda: verify_full_run_result(forged))

    def test_sem_001_f_model_and_outcome_formulas_match_validated_parent(self) -> None:
        checks = (
            ("outcome.py", "OutcomeBuilder", "build"),
            ("model_interface.py", "RankingEngine", "rank"),
            ("model_interface.py", "DiagnosticFixtureScorer", "score"),
        )
        for filename, class_name, method_name in checks:
            parent_sha = _source_sha(VALIDATED_PARENT_ROOT / "tools/m3top3" / filename, class_name, method_name)
            candidate_sha = _source_sha(CANDIDATE_ROOT / "tools/m3top3" / filename, class_name, method_name)
            self.assertEqual(candidate_sha, parent_sha, f"{class_name}.{method_name}")

    def test_sem_001_g_authority_claim_locks_remain_closed(self) -> None:
        for claim in ("official_golden", "full_replay"):
            with self.assertRaises(M3Top3AdmissionError) as caught:
                admit_claim_locks({claim: True})
            self.assertEqual(caught.exception.code, "OFFICIAL_REPLAY_GLOBALLY_BLOCKED")
            self.assertEqual(caught.exception.exit_code, 4)

    def test_sem_001_h_pending_top3_preserves_legacy_non_null_filtering(self) -> None:
        result = self._run_four(frozenset({CODES[1]}))
        second = next(row for row in result["outcomes"] if row["rank"] == 2)
        self.assertIsNone(second["return_ratio"])
        self.assertEqual(result["metrics"].get("valid_return_count"), 2)
        self.assertEqual(result["metrics"].get("mean_return"), "0.2")
        self.assertEqual(result["metrics"].get("median_return"), "0.2")
        self.assertEqual(result["metrics"].get("win_rate"), "1")

    def test_sem_001_i_result_and_view_versions_bind_run_identity(self) -> None:
        result = self._run_four()
        version_fields = (
            "result_contract_version",
            "selected_top3_metrics_view_version",
            "full_universe_view_version",
        )
        payload = result["validation_run_identity_payload"]
        for field in version_fields:
            self.assertIsInstance(result.get(field), str, field)
            self.assertTrue(result[field], field)
            self.assertEqual(payload.get(field), result[field], field)
        self.assertEqual(result["validation_run_id"], deterministic_id("validationrun", payload))
        for field in version_fields:
            changed = copy.deepcopy(payload)
            changed[field] = changed[field] + "-MUTATED"
            self.assertNotEqual(deterministic_id("validationrun", changed), result["validation_run_id"], field)
        forged = copy.deepcopy(result)
        forged["validation_run_identity_payload"][version_fields[0]] += "-FORGED"
        self.assert_integrity_code("RUN_ID_LINEAGE_MISMATCH", lambda: verify_full_run_result(forged))

    def test_sem_001_j_selected_top3_metric_alias_mismatch_is_rejected(self) -> None:
        result = self._run_four()
        forged = copy.deepcopy(result)
        forged["selected_top3_metrics"]["mean_return"] = "-0.075"
        self.assert_integrity_code("METRIC_DENOMINATOR_INTEGRITY_FAILURE", lambda: verify_full_run_result(forged))


if __name__ == "__main__":
    unittest.main(verbosity=2)
