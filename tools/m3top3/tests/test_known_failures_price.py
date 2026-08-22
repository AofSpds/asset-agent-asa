from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.m3top3.admission import M3Top3AdmissionError
from tools.m3top3.core import hash_file
from tools.m3top3.providers import CsvPriceProvider, DuckDBParquetPriceProvider
from tools.m3top3.tests._known_failure_helpers import price_provider, standard_price_rows, write_price_csv


class KnownFailurePriceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def assert_code(self, code, fn, exit_code=3):
        with self.assertRaises(M3Top3AdmissionError) as caught:
            fn()
        self.assertEqual(caught.exception.code, code)
        self.assertEqual(caught.exception.exit_code, exit_code)

    def test_kf_prc_001_configured_hash_mismatch(self):
        path = self.root / "mismatch.csv"
        write_price_csv(path, standard_price_rows())
        self.assert_code("PRICE_COMPONENT_HASH_MISMATCH", lambda: CsvPriceProvider(path, dataset_hash="0" * 64))

    def test_kf_prc_002_canonical_string_without_receipts(self):
        path = self.root / "canonical.csv"
        write_price_csv(path, standard_price_rows())
        self.assert_code("PRICE_CANONICAL_ADMISSION_DENIED", lambda: CsvPriceProvider(path, dataset_hash=hash_file(path), semantics="PRICE_CANONICAL"), 4)

    def test_kf_prc_003_duplicate_csv_key(self):
        rows = standard_price_rows()[:1] * 2
        self.assert_code("DUPLICATE_PRICE_KEY", lambda: price_provider(self.root, rows))

    def test_kf_prc_003_duplicate_duckdb_key(self):
        parquet = self.root / "duplicate.parquet"
        parquet.write_bytes(b"fixture")

        class Result:
            def __init__(self, rows): self.rows = rows
            def fetchall(self): return self.rows
            def fetchone(self): return self.rows[0] if self.rows else None
        class Connection:
            def execute(self, query, params=None):
                if query.startswith("DESCRIBE"): return Result([(x,) for x in ("date", "code", "open", "high", "low", "close")])
                if "HAVING n>1" in query: return Result([("005930", "2025-01-02", 2)])
                return Result([])
        class Duck:
            @staticmethod
            def connect(): return Connection()

        with patch("tools.m3top3.providers.importlib.import_module", return_value=Duck):
            self.assert_code("DUPLICATE_PRICE_KEY", lambda: DuckDBParquetPriceProvider([parquet], "P", hash_file(parquet)))

    def _assert_invalid_ohlc(self, **changes):
        row = standard_price_rows()[:1][0]
        row.update(changes)
        self.assert_code("INVALID_OHLC", lambda: price_provider(self.root, [row]))

    def test_kf_prc_004_high_below_open_or_close(self):
        self._assert_invalid_ohlc(open=100, high=99, low=97, close=98)

    def test_kf_prc_004_low_above_open_or_close(self):
        self._assert_invalid_ohlc(open=100, high=104, low=102, close=101)

    def test_kf_prc_004_low_above_high(self):
        self._assert_invalid_ohlc(open=100, high=101, low=102, close=100)

    def test_kf_prc_004_non_positive_price(self):
        self._assert_invalid_ohlc(open=0, high=2, low=1, close=1)

    def test_kf_prc_005_ca_missing_factor(self):
        row = standard_price_rows()[:1][0]
        row.update(corporate_action_flag="true", adjustment_factor="", corporate_action_evidence_id="CA1")
        self.assert_code("CA_EVIDENCE_INCOMPLETE", lambda: price_provider(self.root, [row]))

    def test_kf_prc_005_ca_invalid_factor(self):
        row = standard_price_rows()[:1][0]
        row.update(corporate_action_flag="true", adjustment_factor="0", corporate_action_evidence_id="CA1")
        self.assert_code("INVALID_ADJUSTMENT_FACTOR", lambda: price_provider(self.root, [row]))

    def test_kf_prc_005_ca_missing_evidence(self):
        row = standard_price_rows()[:1][0]
        row.update(corporate_action_flag="true", adjustment_factor="1.2", corporate_action_evidence_id="")
        self.assert_code("CA_EVIDENCE_INCOMPLETE", lambda: price_provider(self.root, [row]))

    def test_kf_prc_006_unresolved_canonical_ca_candidates(self):
        path = self.root / "canonical-unresolved.csv"
        write_price_csv(path, standard_price_rows())
        release = {"frozen": True, "authority_receipt": "A1", "ca_receipt": "CA1", "unresolved_ca_candidates": 1}
        self.assert_code("PRICE_CANONICAL_CA_INCOMPLETE", lambda: CsvPriceProvider(path, dataset_hash=hash_file(path), semantics="PRICE_CANONICAL", admission_config=release), 4)

    def test_canonical_price_with_complete_receipt_is_admitted(self):
        path = self.root / "canonical-ready.csv"
        write_price_csv(path, standard_price_rows())
        release = {"frozen": True, "authority_receipt": "A1", "ca_receipt": "CA1", "unresolved_ca_candidates": 0}
        provider = CsvPriceProvider(path, dataset_hash=hash_file(path), semantics="PRICE_CANONICAL", admission_config=release)
        self.assertEqual(provider.semantics, "PRICE_CANONICAL")


if __name__ == "__main__":
    unittest.main()
