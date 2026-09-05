from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import shutil
import tempfile
import unittest
from dataclasses import replace
from datetime import date, timedelta
from decimal import Decimal, localcontext
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from tools.m3top3 import cli_build_f05_r1_inputs as cli
from tools.m3top3.f05_r1_market import (
    EXPECTED_W1_DENOMINATOR,
    EXPECTED_PRICE_PARQUET_SHA256,
    EXPECTED_PRICE_DATASET_ID,
    EXPECTED_W1_COHORT_ARTIFACT_SHA256,
    DECIMAL_PRECISION,
    REQUIRED_CA_RECORDS,
    RETURN_SEMANTICS,
    W1_SESSION_DATES,
    W1_CUTOFF_DATE,
    F05CohortMember,
    F05InputError,
    F05SourceBinding,
    build_w1_f05_inputs,
    compute_company_metrics,
    validate_required_ca_evidence,
)
from tools.m3top3.features_v1 import robust_pct
from tools.m3top3.features_v1_narrow_patch import FeatureEngineV1NarrowPatch
from tools.m3top3.providers import CsvPriceProvider, DuckDBParquetPriceProvider, PriceRow


REPO = Path(__file__).resolve().parents[3]
R0_COHORT = (
    REPO / "control/m3top3/f05-r0-readiness/v1.0/runs/"
    "AAA-M3TOP3-F05-R0-20260905-214409-CODEX-01/W1_57_COHORT_BINDING.json"
)
F05_RUN_ROOT = (
    REPO / "control/m3top3/f05-r1-w1-market-positioning/v1.0/runs/"
    "AAA-M3TOP3-F05-R1-20260905-231028-CODEX-01"
)
CA_CUSTODY_PATH = F05_RUN_ROOT / "F05_R1_OFFICIAL_CA_SOURCE_CUSTODY.json"
CA_MANIFEST_PATH = F05_RUN_ROOT / "F05_R1_OFFICIAL_CA_EVIDENCE_MANIFEST.json"


def trading_dates(count: int = 61, cutoff: date = W1_CUTOFF_DATE) -> list[date]:
    if count != 61 or cutoff != W1_CUTOFF_DATE:
        raise ValueError("F05-R1 tests use only the exact governed W1 grid")
    return list(W1_SESSION_DATES)


def price_rows(
    code: str,
    *,
    daily_ratio: Decimal = Decimal("1"),
    volume: int = 1000,
    stocks: int = 10000,
) -> list[PriceRow]:
    rows = []
    for session in trading_dates():
        reference_base = Decimal("10000")
        changes = reference_base * daily_ratio / Decimal(100)
        close = reference_base + changes
        rows.append(PriceRow(
            session,
            code,
            close,
            close + 2,
            close - 2,
            close,
            volume=volume,
            marcap=close * stocks,
            stocks=stocks,
            amount=Decimal(volume) * close,
            changes=changes,
            changes_ratio=daily_ratio,
        ))
    return rows


def gst_rows() -> list[PriceRow]:
    rows = price_rows("083450", daily_ratio=Decimal("0"), volume=1000, stocks=9317745)
    ex_right = next(i for i, row in enumerate(rows) if row.date == date(2024, 6, 26))
    rows[ex_right - 1] = replace(
        rows[ex_right - 1], close=Decimal("43300"), changes=Decimal("0")
    )
    rows[ex_right] = replace(
        rows[ex_right], open=Decimal("21600"), high=Decimal("21800"),
        low=Decimal("21000"), close=Decimal("21600"),
        changes=Decimal("-100"), changes_ratio=Decimal("-0.46"),
    )
    listing = next(i for i, row in enumerate(rows) if row.date == date(2024, 7, 24))
    rows[listing:] = [replace(row, stocks=18618260) for row in rows[listing:]]
    return rows


def exicon_rows() -> list[PriceRow]:
    rows = price_rows("092870", daily_ratio=Decimal("0"), volume=10848797, stocks=10848797)
    ex_right = next(i for i, row in enumerate(rows) if row.date == date(2024, 6, 3))
    rows[ex_right - 1] = replace(
        rows[ex_right - 1], close=Decimal("30000"), changes=Decimal("0")
    )
    rows[ex_right] = replace(
        rows[ex_right], open=Decimal("20400"), high=Decimal("20500"),
        low=Decimal("19500"), close=Decimal("20400"),
        changes=Decimal("930"), changes_ratio=Decimal("4.78"),
    )
    listing = next(i for i, row in enumerate(rows) if row.date == date(2024, 7, 31))
    rows[listing:] = [replace(row, stocks=13050797) for row in rows[listing:]]
    rows[listing] = replace(rows[listing], volume=814284, stocks=13050797)
    return rows


def cohort_and_prices(count: int = EXPECTED_W1_DENOMINATOR):
    bound = json.loads(R0_COHORT.read_text(encoding="utf-8"))["include_companies"]
    cohort = []
    prices = {}
    for index, item in enumerate(bound[:count], start=1):
        code = item["krx_code"]
        cohort.append(F05CohortMember(item["company_id"], code))
        prices[code] = price_rows(code, daily_ratio=Decimal(index) / Decimal(100))
    # The frozen W1 cohort contains both required CA names.  Even synthetic
    # cohort-wide arithmetic tests must preserve their exact official market
    # rows; otherwise the fixture would bypass the same gate as production.
    if "083450" in prices:
        prices["083450"] = gst_rows()
    if "092870" in prices:
        prices["092870"] = exicon_rows()
    return cohort, prices


def source_binding(**changes):
    values = {
        "dataset_id": EXPECTED_PRICE_DATASET_ID,
        "parquet_sha256": EXPECTED_PRICE_PARQUET_SHA256,
    }
    values.update(changes)
    return F05SourceBinding(**values)


def ca_manifest():
    records = []
    for evidence_id, expected in REQUIRED_CA_RECORDS.items():
        records.append({
            "evidence_id": evidence_id,
            "authority": "KRX",
            "company_id": expected["company_id"],
            "published_date": expected["published_date"],
            "url": expected["url"],
            "facts": dict(expected["facts"]),
            "pit_admissible": True,
        })
    records.append({
        "evidence_id": "KRX-BASE-PRICE-RULES",
        "authority": "KRX",
        "urls": [
            "https://global.krx.co.kr/contents/GLB/06/0602/0602020202/GLB0602020202T2.jsp",
            "https://global.krx.co.kr/contents/GLB/06/0602/0602020202/GLB0602020202T3.jsp",
            "https://global.krx.co.kr/contents/GLB/06/0602/0602010201/GLB0602010201T6.jsp",
        ],
        "pit_admissible": "CONTROL_SEMANTICS_ONLY",
    })
    return {
        "cutoff_date": "2024-08-09",
        "status": "OFFICIAL_EVIDENCE_CLOSED",
        "records": records,
        "post_cutoff_material": {"used_in_input_or_score": False},
        "adjustment_factor_inferred": False,
    }


def ca_custody():
    return json.loads(CA_CUSTODY_PATH.read_text(encoding="utf-8"))


def build_bound_inputs(cohort, prices, **kwargs):
    values = {
        "source_binding": source_binding(),
        "ca_evidence_manifest": ca_manifest(),
        "ca_source_custody": ca_custody(),
        "ca_custody_root": F05_RUN_ROOT,
        "source_lineage_refs": ("R0-W1-57-COHORT-BLOB:d2698e901eabb4013f339ce1f163cd0c7c14d879",),
    }
    values.update(kwargs)
    return build_w1_f05_inputs(cohort, prices, **values)


class TestF05R1MarketArithmetic(unittest.TestCase):
    def test_ordinary_security_uses_exact_21_and_61_observation_windows(self):
        member = F05CohortMember("KRX:000001", "000001")
        result = compute_company_metrics(member, price_rows(member.krx_code))
        with localcontext() as context:
            context.prec = DECIMAL_PRECISION
            expected_20 = Decimal(1)
            expected_60 = Decimal(1)
            for _ in range(20):
                expected_20 *= Decimal("1.01")
            for _ in range(60):
                expected_60 *= Decimal("1.01")
            expected_20 -= Decimal(1)
            expected_60 -= Decimal(1)
        self.assertEqual(len(result.observation_dates), 61)
        self.assertEqual(result.observation_dates[-1], W1_CUTOFF_DATE)
        self.assertEqual(result.trailing_20d_total_return, expected_20)
        self.assertEqual(result.trailing_60d_total_return, expected_60)
        self.assertEqual(result.turnover_acceleration, 0)
        self.assertEqual(result.observation_dates[0], date(2024, 5, 16))
        self.assertEqual(result.observation_dates[-21], date(2024, 7, 12))
        self.assertNotIn(date(2024, 6, 6), result.observation_dates)

    def test_turnover_acceleration_is_exact_recent_20_over_prior_20(self):
        member = F05CohortMember("KRX:000001", "000001")
        rows = price_rows(member.krx_code, daily_ratio=Decimal("0"))
        rows[-40:-20] = [replace(row, volume=100, stocks=1000) for row in rows[-40:-20]]
        rows[-20:] = [replace(row, volume=250, stocks=1000) for row in rows[-20:]]
        result = compute_company_metrics(member, rows)
        self.assertEqual(result.turnover_acceleration, Decimal("1.5"))

    def test_gst_0626_ex_right_uses_changes_ratio_not_naive_close_and_0724_stocks(self):
        member = F05CohortMember("KRX:083450", "083450")
        rows = gst_rows()
        ex_right = next(i for i, row in enumerate(rows) if row.date == date(2024, 6, 26))
        listing = next(i for i, row in enumerate(rows) if row.date == date(2024, 7, 24))

        result = compute_company_metrics(member, rows)
        naive_close = Decimal("21600") / Decimal("43300") - 1
        self.assertEqual(rows[ex_right].close - rows[ex_right].changes, Decimal("21700"))
        self.assertEqual(rows[listing - 1].stocks, 9317745)
        self.assertEqual(rows[listing].stocks, 18618260)
        self.assertEqual(result.trailing_60d_total_return, Decimal("-0.0046"))
        self.assertNotEqual(result.trailing_60d_total_return, naive_close)
        with localcontext() as context:
            context.prec = DECIMAL_PRECISION
            prior = sum(
                (Decimal(row.volume) / Decimal(row.stocks) for row in rows[-40:-20]), Decimal(0)
            ) / Decimal(20)
            recent = sum(
                (Decimal(row.volume) / Decimal(row.stocks) for row in rows[-20:]), Decimal(0)
            ) / Decimal(20)
            self.assertEqual(result.turnover_acceleration, recent / prior - 1)

    def test_exicon_0603_ex_right_and_0731_share_count_boundary_are_observed(self):
        member = F05CohortMember("KRX:092870", "092870")
        rows = exicon_rows()
        ex_right = next(i for i, row in enumerate(rows) if row.date == date(2024, 6, 3))
        listing = next(i for i, row in enumerate(rows) if row.date == date(2024, 7, 31))

        result = compute_company_metrics(member, rows)
        self.assertEqual(rows[ex_right].close - rows[ex_right].changes, Decimal("19470"))
        self.assertEqual(rows[listing - 1].stocks, 10848797)
        self.assertEqual((rows[listing].volume, rows[listing].stocks), (814284, 13050797))
        self.assertEqual(result.trailing_60d_total_return, Decimal("0.0478"))
        with localcontext() as context:
            context.prec = DECIMAL_PRECISION
            prior = sum(
                (Decimal(row.volume) / Decimal(row.stocks) for row in rows[-40:-20]), Decimal(0)
            ) / Decimal(20)
            recent = sum(
                (Decimal(row.volume) / Decimal(row.stocks) for row in rows[-20:]), Decimal(0)
            ) / Decimal(20)
            self.assertEqual(result.turnover_acceleration, recent / prior - 1)

    def test_exact_57_equal_weight_benchmark_identity_and_legacy_aliases(self):
        cohort, prices = cohort_and_prices()
        output = build_bound_inputs(list(reversed(cohort)), prices)
        with localcontext() as context:
            context.prec = DECIMAL_PRECISION
            expected = sum(
                (
                    compute_company_metrics(member, prices[member.krx_code]).trailing_20d_total_return
                    for member in sorted(cohort, key=lambda value: value.company_id)
                ),
                Decimal(0),
            ) / Decimal(57)
            expected_60 = sum(
                (
                    compute_company_metrics(member, prices[member.krx_code]).trailing_60d_total_return
                    for member in sorted(cohort, key=lambda value: value.company_id)
                ),
                Decimal(0),
            ) / Decimal(57)
        self.assertEqual(len(output), 57)
        self.assertEqual(
            [row["company_id"] for row in output],
            sorted(row["company_id"] for row in output),
        )
        self.assertEqual({row["benchmark_member_count"] for row in output}, {57})
        self.assertEqual(
            {Decimal(row["feature_raw_input"]["universe_20d_equal_weight_market_price_return"]) for row in output},
            {expected},
        )
        self.assertEqual(
            {Decimal(row["feature_raw_input"]["universe_60d_equal_weight_market_price_return"]) for row in output},
            {expected_60},
        )
        for row in output:
            raw = row["feature_raw_input"]
            self.assertEqual(raw["trailing_20d_market_price_return"], raw["trailing_20d_total_return"])
            self.assertEqual(
                raw["universe_20d_equal_weight_market_price_return"],
                raw["universe_20d_equal_weight_return"],
            )
            self.assertEqual(raw["trailing_60d_market_price_return"], raw["trailing_60d_total_return"])
            self.assertEqual(
                raw["universe_60d_equal_weight_market_price_return"],
                raw["universe_60d_equal_weight_return"],
            )
            self.assertEqual(raw["calculation_trace"]["benchmark_member_count"], 57)
            self.assertEqual(raw["calculation_trace"]["return_20_observation_count"], 21)
            self.assertEqual(raw["calculation_trace"]["return_60_observation_count"], 61)
            self.assertFalse(raw["calculation_trace"]["cash_dividend_included"])
            self.assertFalse(raw["calculation_trace"]["adjustment_factor_used"])
            self.assertIn(f"Code={row['krx_code']}", "\n".join(raw["source_lineage_refs"]))


class TestF05R1FailClosedInputs(unittest.TestCase):
    def setUp(self):
        self.member = F05CohortMember("KRX:000001", "000001")
        self.rows = price_rows(self.member.krx_code)

    def test_denominator_56_is_rejected(self):
        cohort, prices = cohort_and_prices(56)
        with self.assertRaisesRegex(F05InputError, "exactly 57"):
            build_bound_inputs(cohort, prices)

    def test_wrong_issuer_missing_cutoff_and_missing_return_field_are_rejected(self):
        cases = {
            "wrong_issuer": [replace(self.rows[0], code="999999"), *self.rows[1:]],
            "missing_cutoff": [replace(self.rows[0], date=self.rows[0].date - timedelta(days=1)), *self.rows[:-1]],
            "missing_changes_ratio": [replace(self.rows[0], changes_ratio=None), *self.rows[1:]],
        }
        for name, rows in cases.items():
            with self.subTest(name=name), self.assertRaises(F05InputError):
                compute_company_metrics(self.member, rows)

    def test_mutated_changes_ratio_inconsistent_with_bound_fields_is_rejected(self):
        rows = [replace(self.rows[0], changes_ratio=Decimal("99")), *self.rows[1:]]
        with self.assertRaisesRegex(F05InputError, "inconsistent"):
            compute_company_metrics(self.member, rows)

    def test_post_cutoff_row_is_rejected_not_silently_filtered(self):
        future = replace(self.rows[-1], date=W1_CUTOFF_DATE + timedelta(days=3))
        with self.assertRaisesRegex(F05InputError, "post-cutoff"):
            compute_company_metrics(self.member, [*self.rows, future])

    def test_w1_cutoff_cannot_be_shifted(self):
        with self.assertRaisesRegex(F05InputError, "cutoff must remain"):
            compute_company_metrics(
                self.member,
                self.rows[:-1],
                cutoff_date=W1_CUTOFF_DATE - timedelta(days=3),
            )

    def test_missing_zero_or_nonpositive_price_turnover_inputs_are_rejected(self):
        mutations = {
            "missing_volume": {"volume": None},
            "zero_volume": {"volume": 0},
            "missing_stocks": {"stocks": None},
            "zero_stocks": {"stocks": 0},
            "zero_close": {"close": Decimal(0)},
            "fractional_volume": {"volume": Decimal("1.5")},
            "fractional_stocks": {"stocks": Decimal("1000.5")},
            "boolean_stocks": {"stocks": True},
        }
        for name, fields in mutations.items():
            rows = [replace(self.rows[0], **fields), *self.rows[1:]]
            with self.subTest(name=name), self.assertRaises(F05InputError):
                compute_company_metrics(self.member, rows)

    def test_duplicate_date_and_cross_company_date_misalignment_are_rejected(self):
        with self.assertRaisesRegex(F05InputError, "duplicate"):
            compute_company_metrics(self.member, [*self.rows, self.rows[0]])

        cohort, prices = cohort_and_prices()
        changed = list(prices[cohort[1].krx_code])
        changed[0] = replace(changed[0], date=changed[0].date - timedelta(days=1))
        prices[cohort[1].krx_code] = changed
        with self.assertRaisesRegex(F05InputError, "governed W1 61-session grid"):
            build_bound_inputs(cohort, prices)

    def test_cash_dividend_total_return_substitution_is_rejected(self):
        with self.assertRaisesRegex(F05InputError, "no dividend"):
            compute_company_metrics(
                self.member,
                self.rows,
                return_semantics="CASH_DIVIDEND_TOTAL_RETURN",
            )

    def test_naive_raw_close_ca_semantics_are_explicitly_rejected(self):
        with self.assertRaisesRegex(F05InputError, "KRX ChangesRatio"):
            compute_company_metrics(
                self.member,
                self.rows,
                return_semantics="NAIVE_RAW_CLOSE_ADJACENT_RETURN",
            )

    def test_any_precomputed_or_invented_adjustment_factor_is_rejected(self):
        rows = [replace(self.rows[0], adjustment_factor=Decimal("1")), *self.rows[1:]]
        with self.assertRaisesRegex(F05InputError, "adjustment factor"):
            compute_company_metrics(self.member, rows)

    def test_wrong_company_id_and_extra_price_map_member_are_rejected(self):
        with self.assertRaisesRegex(F05InputError, "identity mismatch"):
            compute_company_metrics(F05CohortMember("KRX:999999", "000001"), self.rows)
        cohort, prices = cohort_and_prices()
        prices["999999"] = price_rows("999999")
        with self.assertRaisesRegex(F05InputError, "does not exactly match"):
            build_bound_inputs(cohort, prices)

    def test_wrong_but_still_57_cohort_and_wrong_source_binding_are_rejected(self):
        cohort, prices = cohort_and_prices()
        removed = cohort[-1]
        replacement = F05CohortMember("KRX:999999", "999999")
        cohort[-1] = replacement
        prices[replacement.krx_code] = price_rows(replacement.krx_code)
        prices.pop(removed.krx_code)
        with self.assertRaisesRegex(F05InputError, "frozen R0"):
            build_bound_inputs(cohort, prices)

        cohort, prices = cohort_and_prices()
        with self.assertRaisesRegex(F05InputError, "unapproved.*Parquet"):
            build_bound_inputs(
                cohort,
                prices,
                source_binding=source_binding(parquet_sha256="0" * 64),
            )
        with self.assertRaisesRegex(F05InputError, "dataset_id"):
            build_bound_inputs(
                cohort,
                prices,
                source_binding=source_binding(dataset_id="WRONG-DATASET"),
            )

    def test_exact_ca_market_row_mutations_are_rejected(self):
        cases = []
        rows = gst_rows()
        index = next(i for i, row in enumerate(rows) if row.date == date(2024, 6, 26))
        cases.append((F05CohortMember("KRX:083450", "083450"), [
            *rows[:index], replace(rows[index], changes_ratio=Decimal("-0.45")), *rows[index + 1:]
        ]))
        rows = gst_rows()
        index = next(i for i, row in enumerate(rows) if row.date == date(2024, 7, 24))
        cases.append((F05CohortMember("KRX:083450", "083450"), [
            *rows[:index], replace(rows[index], stocks=18618261), *rows[index + 1:]
        ]))
        rows = exicon_rows()
        index = next(i for i, row in enumerate(rows) if row.date == date(2024, 6, 3))
        cases.append((F05CohortMember("KRX:092870", "092870"), [
            *rows[:index], replace(rows[index], changes_ratio=Decimal("4.77")), *rows[index + 1:]
        ]))
        rows = exicon_rows()
        index = next(i for i, row in enumerate(rows) if row.date == date(2024, 7, 31))
        cases.append((F05CohortMember("KRX:092870", "092870"), [
            *rows[:index], replace(rows[index], volume=814285), *rows[index + 1:]
        ]))
        for member, mutated in cases:
            with self.subTest(company_id=member.company_id), self.assertRaisesRegex(
                F05InputError, "official CA market-row binding mismatch"
            ):
                compute_company_metrics(member, mutated)

    def test_decimal_results_do_not_depend_on_mutable_global_context(self):
        with localcontext() as context:
            context.prec = 6
            low_context = compute_company_metrics(self.member, self.rows)
        with localcontext() as context:
            context.prec = 48
            high_context = compute_company_metrics(self.member, self.rows)
        self.assertEqual(low_context, high_context)


class TestF05R1CAEvidenceGate(unittest.TestCase):
    def test_exact_required_ca_records_close_and_feed_company_event_groups(self):
        validated = validate_required_ca_evidence(
            ca_manifest(), ca_custody(), F05_RUN_ROOT
        )
        self.assertEqual(len(validated.event_group_ids_by_company["KRX:083450"]), 2)
        self.assertEqual(len(validated.event_group_ids_by_company["KRX:092870"]), 2)
        cohort, prices = cohort_and_prices()
        output = build_bound_inputs(cohort, prices)
        gst = next(row for row in output if row["company_id"] == "KRX:083450")
        exicon = next(row for row in output if row["company_id"] == "KRX:092870")
        self.assertEqual(len(gst["feature_raw_input"]["event_group_ids"]), 2)
        self.assertEqual(len(exicon["feature_raw_input"]["event_group_ids"]), 2)
        self.assertIn("KRX-20240625001437", "\n".join(gst["feature_raw_input"]["source_lineage_refs"]))

    def test_wrong_ca_company_date_or_source_ref_fails_closed(self):
        mutations = {
            "company_id": ("KRX-20240625001437", "company_id", "KRX:999999"),
            "published_date": ("KRX-20240625001437", "published_date", "2024-08-10"),
            "url": ("KRX-20240726001822", "url", "https://example.invalid/wrong"),
        }
        for name, (evidence_id, field, value) in mutations.items():
            manifest = ca_manifest()
            record = next(item for item in manifest["records"] if item["evidence_id"] == evidence_id)
            record[field] = value
            with self.subTest(name=name), self.assertRaises(F05InputError):
                validate_required_ca_evidence(manifest, ca_custody(), F05_RUN_ROOT)

    def test_wrong_custody_hash_fails_even_when_claims_are_unchanged(self):
        custody = ca_custody()
        custody["files"][0]["sha256"] = "0" * 64
        with self.assertRaisesRegex(F05InputError, "body binding"):
            validate_required_ca_evidence(ca_manifest(), custody, F05_RUN_ROOT)

    def test_rehashed_mutated_official_body_is_not_self_authorizing(self):
        with tempfile.TemporaryDirectory(prefix="f05-ca-custody-") as temp:
            root = Path(temp)
            shutil.copytree(F05_RUN_ROOT / "evidence", root / "evidence")
            custody = ca_custody()
            item = custody["files"][0]
            target = root / item["path"]
            data = target.read_bytes()
            changed = bytes((data[0] ^ 1,)) + data[1:]
            target.write_bytes(changed)
            item["bytes"] = len(changed)
            item["sha256"] = hashlib.sha256(changed).hexdigest()
            with self.assertRaisesRegex(F05InputError, "body binding"):
                validate_required_ca_evidence(ca_manifest(), custody, root)


class TestPriceProviderFieldExposure(unittest.TestCase):
    def test_duckdb_row_conversion_exposes_exact_optional_types_without_dependency(self):
        raw = (
            W1_CUTOFF_DATE, "000001", Decimal("100"), Decimal("110"),
            Decimal("90"), Decimal("105"), 123, Decimal("105000"), 1000,
            True, None, Decimal("12915"), Decimal("5"), Decimal("5.00"),
        )
        row = DuckDBParquetPriceProvider._price_row(raw)
        self.assertEqual(row.date, W1_CUTOFF_DATE)
        self.assertEqual(row.code, "000001")
        self.assertEqual(row.close, Decimal("105"))
        self.assertEqual(row.volume, 123)
        self.assertEqual(row.amount, Decimal("12915"))
        self.assertEqual(row.stocks, 1000)
        self.assertEqual(row.changes, Decimal("5"))
        self.assertEqual(row.changes_ratio, Decimal("5.00"))

    def test_duckdb_row_conversion_rejects_fractional_or_boolean_counts(self):
        template = [
            W1_CUTOFF_DATE, "000001", Decimal("100"), Decimal("110"),
            Decimal("90"), Decimal("105"), 123, Decimal("105000"), 1000,
            False, None, Decimal("12915"), Decimal("5"), Decimal("5.00"),
        ]
        for field, position, value in (
            ("Volume", 6, Decimal("1.5")),
            ("Stocks", 8, Decimal("1000.5")),
            ("Volume", 6, True),
            ("Stocks", 8, False),
        ):
            raw = list(template)
            raw[position] = value
            with self.subTest(field=field, value=value), self.assertRaisesRegex(ValueError, field):
                DuckDBParquetPriceProvider._price_row(tuple(raw))

    def test_price_row_and_csv_old_call_remain_compatible_and_new_fields_are_typed(self):
        old = PriceRow(date(2024, 8, 9), "000001", Decimal(1), Decimal(1), Decimal(1), Decimal(1))
        self.assertIsNone(old.volume)
        self.assertIsNone(old.changes_ratio)
        with tempfile.TemporaryDirectory(prefix="f05-provider-") as temp:
            path = Path(temp) / "prices.csv"
            with path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.writer(handle)
                writer.writerow(("date", "code", "open", "high", "low", "close", "volume", "amount", "stocks", "changes", "changes_ratio"))
                writer.writerow(("2024-08-09", "000001", "100", "110", "90", "105", "123", "12915", "1000", "5", "5.00"))
            row = CsvPriceProvider(path).row("000001", date(2024, 8, 9))
        self.assertIsNotNone(row)
        self.assertEqual(row.volume, 123)
        self.assertEqual(row.amount, Decimal("12915"))
        self.assertEqual(row.stocks, 1000)
        self.assertEqual(row.changes, Decimal("5"))
        self.assertEqual(row.changes_ratio, Decimal("5.00"))

    def test_duckdb_parquet_exposes_bound_fields_and_accepts_old_minimal_schema(self):
        if importlib.util.find_spec("duckdb") is None:
            self.skipTest("optional duckdb is not installed")
        try:
            import duckdb
        except ImportError:
            self.skipTest("optional duckdb native extension is not loadable")
        if not hasattr(duckdb, "connect"):
            self.skipTest("optional duckdb installation is incomplete")

        with tempfile.TemporaryDirectory(prefix="f05-duckdb-") as temp:
            root = Path(temp)
            rich = root / "rich.parquet"
            minimal = root / "minimal.parquet"
            con = duckdb.connect()
            con.execute(
                'CREATE TABLE rich("Date" DATE, "Code" VARCHAR, "Open" DECIMAL, '
                '"High" DECIMAL, "Low" DECIMAL, "Close" DECIMAL, "Volume" BIGINT, '
                '"Amount" BIGINT, "Stocks" BIGINT, "Changes" DECIMAL, '
                '"ChangesRatio" DECIMAL(8,2))'
            )
            con.execute(
                "INSERT INTO rich VALUES (DATE '2024-08-09', '000001', 100, 110, 90, "
                "105, 123, 12915, 1000, 5, 5.00)"
            )
            con.execute("COPY rich TO ? (FORMAT PARQUET)", [str(rich)])
            con.execute(
                'CREATE TABLE minimal("Date" DATE, "Code" VARCHAR, "Open" DECIMAL, '
                '"High" DECIMAL, "Low" DECIMAL, "Close" DECIMAL)'
            )
            con.execute("INSERT INTO minimal VALUES (DATE '2024-08-09', '000002', 100, 110, 90, 105)")
            con.execute("COPY minimal TO ? (FORMAT PARQUET)", [str(minimal)])
            con.close()

            rich_row = DuckDBParquetPriceProvider([rich], "RICH", "HASH").row("000001", W1_CUTOFF_DATE)
            old_row = DuckDBParquetPriceProvider([minimal], "OLD", "HASH").row("000002", W1_CUTOFF_DATE)
        self.assertEqual(rich_row.volume, 123)
        self.assertEqual(rich_row.amount, Decimal("12915"))
        self.assertEqual(rich_row.stocks, 1000)
        self.assertEqual(rich_row.changes, Decimal("5"))
        self.assertEqual(rich_row.changes_ratio, Decimal("5.00"))
        self.assertIsNone(old_row.volume)
        self.assertIsNone(old_row.changes_ratio)


class TestF05R1CanonicalMaterializer(unittest.TestCase):
    def test_hash_bound_create_once_jsonl_contains_57_inputs_and_no_scores(self):
        cohort, prices = cohort_and_prices()
        with tempfile.TemporaryDirectory(prefix="f05-materializer-") as temp:
            root = Path(temp)
            cohort_path = root / "cohort.json"
            cohort_path.write_bytes(R0_COHORT.read_bytes())
            parquet_path = root / "bound.parquet"
            parquet_path.write_bytes(b"TEST-BOUND-PARQUET")
            output_path = root / "inputs.jsonl"
            args = SimpleNamespace(
                cohort=str(cohort_path),
                cohort_sha256=EXPECTED_W1_COHORT_ARTIFACT_SHA256,
                parquet=str(parquet_path),
                parquet_sha256=EXPECTED_PRICE_PARQUET_SHA256,
                dataset_id=EXPECTED_PRICE_DATASET_ID,
                source_semantics="RAW_IMMUTABLE_NOT_PRICE_CANONICAL",
                ca_manifest=str(CA_MANIFEST_PATH),
                ca_manifest_sha256=hashlib.sha256(CA_MANIFEST_PATH.read_bytes()).hexdigest(),
                ca_custody=str(CA_CUSTODY_PATH),
                ca_custody_sha256=hashlib.sha256(CA_CUSTODY_PATH.read_bytes()).hexdigest(),
                source_lineage_ref=["TEST-SOURCE"],
                lookback_start="2024-05-16",
                output=str(output_path),
            )

            class FakeProvider:
                def __init__(self, *unused_args, **unused_kwargs):
                    self._cols = {
                        field.lower(): field
                        for field in (
                            "Date", "Code", "Close", "Changes", "ChangesRatio",
                            "Volume", "Amount", "Stocks",
                        )
                    }

                def trading_dates(self, start, end):
                    self_outer.assertEqual((start, end), (W1_SESSION_DATES[0], W1_CUTOFF_DATE))
                    return list(W1_SESSION_DATES)

                def rows(self, code, start, end):
                    self_outer.assertEqual((start, end), (date(2024, 5, 16), W1_CUTOFF_DATE))
                    return prices[code]

            self_outer = self
            with patch.object(cli, "DuckDBParquetPriceProvider", FakeProvider), patch.object(
                cli, "_sha256_file", return_value=EXPECTED_PRICE_PARQUET_SHA256
            ):
                receipt = cli.materialize(args)
                with self.assertRaises(FileExistsError):
                    cli.materialize(args)

            lines = output_path.read_bytes().splitlines()
            decoded = [json.loads(line) for line in lines]
            self.assertEqual(receipt["row_count"], 57)
            self.assertEqual(receipt["sha256"], hashlib.sha256(output_path.read_bytes()).hexdigest())
            self.assertFalse(receipt["contains_scores"])
            self.assertEqual(len(decoded), 57)
            self.assertEqual(
                [row["company_id"] for row in decoded],
                sorted(row["company_id"] for row in decoded),
            )
            self.assertTrue(all("feature_raw_input" in row for row in decoded))
            prohibited = {"score", "final_score", "pre_gate_score", "exact_rank"}

            def keys(value):
                if isinstance(value, dict):
                    for key, nested in value.items():
                        yield key
                        yield from keys(nested)
                elif isinstance(value, list):
                    for nested in value:
                        yield from keys(nested)

            self.assertTrue(all(prohibited.isdisjoint(set(keys(row))) for row in decoded))

    def test_materializer_rejects_rehashed_wrong_cutoff_binding(self):
        with tempfile.TemporaryDirectory(prefix="f05-materializer-cutoff-") as temp:
            path = Path(temp) / "cohort.json"
            path.write_text(
                '{"w1_binding":{"snapshot_cutoff_at":"2024-08-12T23:59:59+09:00"},"include_companies":[]}',
                encoding="utf-8",
            )
            sha256 = hashlib.sha256(path.read_bytes()).hexdigest()
            with self.assertRaisesRegex(ValueError, "cutoff binding"):
                cli._load_bound_cohort(path, sha256)


class TestF05R1UnchangedEngineCompatibility(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = json.loads(
            (REPO / "tools/m3top3/configs/m3top3_v1.0.json").read_text(encoding="utf-8")
        )
        cls.engine = FeatureEngineV1NarrowPatch(cls.config["feature_weights"])

    @staticmethod
    def _engine_row(company_id, return_20, return_60, turnover, **extra):
        raw = {
            "trailing_20d_total_return": str(return_20),
            "universe_20d_equal_weight_return": "0",
            "trailing_60d_total_return": str(return_60),
            "universe_60d_equal_weight_return": "0",
            "turnover_acceleration": str(turnover),
            **extra,
        }
        return {
            "company_id": company_id,
            "eligibility_state": "ELIGIBLE",
            "feature_raw_inputs": {"F05_MARKET_POSITIONING_BALANCE": raw},
        }

    def test_unchanged_f05_component_weights_and_saturation(self):
        rows = [
            self._engine_row("A", 2, 1, 0),
            self._engine_row("B", 1, 0, 2),
            self._engine_row("C", 0, 2, 1),
        ]
        output = self.engine.f05(rows)
        expected = {"A": Decimal(65), "B": Decimal(45), "C": Decimal(40)}
        for company_id, velocity in expected.items():
            self.assertEqual(output[company_id].availability_state, "AVAILABLE")
            self.assertEqual(Decimal(output[company_id].trace["recognition_velocity"]), velocity)
            self.assertEqual(Decimal(output[company_id].trace["saturation_penalty"]), 0)
            self.assertEqual(output[company_id].score, velocity)

        aligned = [
            self._engine_row("LOW", 0, 0, 0),
            self._engine_row("MID", 1, 1, 1),
            self._engine_row(
                "HIGH", 2, 2, 2,
                valuation_percentile="100", diffusion_percentile="100",
            ),
        ]
        high = self.engine.f05(aligned)["HIGH"]
        self.assertEqual(Decimal(high.trace["recognition_velocity"]), 100)
        self.assertEqual(Decimal(high.trace["saturation_penalty"]), 25)
        self.assertEqual(high.score, 75)
        self.assertEqual(
            Decimal(str(self.config["feature_weights"]["F05_MARKET_POSITIONING_BALANCE"])),
            Decimal(20),
        )

    def test_all_57_materialized_blocks_are_accepted_by_unchanged_f05_engine(self):
        cohort, prices = cohort_and_prices()
        materialized = build_bound_inputs(cohort, prices)
        rows = [
            {
                "company_id": item["company_id"],
                "eligibility_state": "ELIGIBLE",
                "feature_raw_inputs": {
                    "F05_MARKET_POSITIONING_BALANCE": item["feature_raw_input"]
                },
            }
            for item in materialized
        ]
        output = self.engine.f05(rows)
        self.assertEqual(len(output), 57)
        self.assertEqual({value.availability_state for value in output.values()}, {"AVAILABLE"})

        raw_by_id = {
            row["company_id"]: row["feature_raw_inputs"]["F05_MARKET_POSITIONING_BALANCE"]
            for row in rows
        }
        relative_20 = {
            cid: Decimal(raw["trailing_20d_total_return"])
            - Decimal(raw["universe_20d_equal_weight_return"])
            for cid, raw in raw_by_id.items()
        }
        relative_60 = {
            cid: Decimal(raw["trailing_60d_total_return"])
            - Decimal(raw["universe_60d_equal_weight_return"])
            for cid, raw in raw_by_id.items()
        }
        turnover = {
            cid: Decimal(raw["turnover_acceleration"])
            for cid, raw in raw_by_id.items()
        }
        p20, p60, pturn = robust_pct(relative_20), robust_pct(relative_60), robust_pct(turnover)
        for company_id, value in output.items():
            velocity = Decimal(".50") * p20[company_id]
            velocity += Decimal(".30") * p60[company_id]
            velocity += Decimal(".20") * pturn[company_id]
            penalty = max(Decimal(0), velocity - Decimal(85))
            self.assertEqual(Decimal(value.trace["recognition_velocity"]), velocity)
            self.assertEqual(Decimal(value.trace["saturation_penalty"]), penalty)
            self.assertEqual(value.score, velocity - penalty)


class TestF05R1FrozenModelPreservation(unittest.TestCase):
    EXPECTED_NORMALIZED_SHA256 = {
        "tools/m3top3/features_v1.py": "d7c48767a05f5fd883e8619a06a25c019be23e9b5dc464ca75014056253a2882",
        "tools/m3top3/features_v1_narrow_patch.py": "02af5d193b4ec38dab61390c214edff8a0997e02a58e1a1e884bc5b25711d7ac",
        "tools/m3top3/scorer_v1.py": "5f940c83acceba1fdc9aaf897a7fe3bbea0469fd80bdc4f9f6d43c32134247fe",
        "tools/m3top3/configs/m3top3_v1.0.json": "eecde22a7744cff505c624bb6f0bdb11714352a122632238ea68d9cd0fbacb98",
    }

    def test_feature_scorer_and_weight_config_digests_are_immutable(self):
        for relative, expected in self.EXPECTED_NORMALIZED_SHA256.items():
            normalized = (REPO / relative).read_bytes().replace(b"\r\n", b"\n")
            with self.subTest(path=relative):
                self.assertEqual(hashlib.sha256(normalized).hexdigest(), expected)


if __name__ == "__main__":
    unittest.main()
