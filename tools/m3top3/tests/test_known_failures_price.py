from __future__ import annotations

import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

from tools.m3top3.admission import M3Top3AdmissionError, canonical_component_set_digest, price_dataset_identity_hash
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
        self.assert_code("PRICE_CANONICAL_GLOBALLY_BLOCKED", lambda: CsvPriceProvider(path, dataset_hash=hash_file(path), semantics="PRICE_CANONICAL"), 4)

    def test_unrecognized_price_semantics_is_fail_closed_at_construction(self):
        path=self.root/"unknown-semantics.csv"
        write_price_csv(path,standard_price_rows())
        self.assert_code("UNSUPPORTED_PRICE_SEMANTICS",lambda:CsvPriceProvider(path,dataset_hash=hash_file(path),semantics="TYPO_CANONICALISH"),4)

    def test_post_construction_semantics_mutation_is_fail_closed(self):
        provider=price_provider(self.root)
        provider.semantics="TYPO_CANONICALISH"
        self.assert_code("UNSUPPORTED_PRICE_SEMANTICS",lambda:provider.trading_dates(date(2025,1,2),date(2025,1,31)),4)

    def test_post_construction_price_byte_mutation_is_rejected_before_read(self):
        provider=price_provider(self.root)
        provider.path.write_bytes(provider.path.read_bytes()+b"tamper")
        self.assert_code("PRICE_COMPONENT_HASH_MISMATCH",lambda:provider.trading_dates(date(2025,1,2),date(2025,1,31)))

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
        self.assert_code("PRICE_CANONICAL_GLOBALLY_BLOCKED", lambda: CsvPriceProvider(path, dataset_hash=hash_file(path), semantics="PRICE_CANONICAL", admission_config=release), 4)

    def test_canonical_price_with_self_asserted_complete_receipt_is_still_blocked(self):
        path = self.root / "canonical-ready.csv"
        write_price_csv(path, standard_price_rows())
        release = {"frozen": True, "authority_receipt": "A1", "ca_receipt": "CA1", "unresolved_ca_candidates": 0}
        self.assert_code("PRICE_CANONICAL_GLOBALLY_BLOCKED",lambda: CsvPriceProvider(path,dataset_hash=hash_file(path),semantics="PRICE_CANONICAL",admission_config=release),4)

    def _fake_duck(self,columns,handler):
        class Result:
            def __init__(self,rows): self.rows=rows
            def fetchall(self): return self.rows
            def fetchone(self): return self.rows[0] if self.rows else None
        class Connection:
            def execute(self,query,params=None): return Result(handler(query,params))
        class Duck:
            @staticmethod
            def connect(): return Connection()
        return Duck

    def test_kf_prc_005_parquet_maps_ca_columns_into_price_row(self):
        parquet=self.root/"ca-map.parquet"; parquet.write_bytes(b"fixture")
        columns=("date","code","open","high","low","close","corporate_action_flag","adjustment_factor","corporate_action_evidence_id")
        def handler(query,params):
            if query.startswith("DESCRIBE"): return [(x,) for x in columns]
            if "HAVING n>1" in query or "GREATEST" in query or "AND (" in query: return []
            if params is not None: return [(date(2025,1,2),"005930",100,103,98,101,True,1.25,"CA-PQ-1")]
            return []
        with patch("tools.m3top3.providers.importlib.import_module",return_value=self._fake_duck(columns,handler)):
            provider=DuckDBParquetPriceProvider([parquet],"P",hash_file(parquet))
            row=provider.row("005930",date(2025,1,2))
        self.assertTrue(row.corporate_action_flag)
        self.assertEqual(str(row.adjustment_factor),"1.25")
        self.assertEqual(row.corporate_action_evidence_id,"CA-PQ-1")

    def test_kf_prc_005_parquet_invalid_ca_factor_rejected(self):
        parquet=self.root/"ca-invalid.parquet"; parquet.write_bytes(b"fixture")
        columns=("date","code","open","high","low","close","corporate_action_flag","adjustment_factor","corporate_action_evidence_id")
        def handler(query,params):
            if query.startswith("DESCRIBE"): return [(x,) for x in columns]
            if "HAVING n>1" in query or "GREATEST" in query: return []
            if "AND (" in query: return [(date(2025,1,2),"005930",0,"CA-PQ-1")]
            return []
        with patch("tools.m3top3.providers.importlib.import_module",return_value=self._fake_duck(columns,handler)):
            self.assert_code("INVALID_ADJUSTMENT_FACTOR",lambda: DuckDBParquetPriceProvider([parquet],"P",hash_file(parquet)))

    def test_kf_prc_005_parquet_missing_ca_evidence_rejected(self):
        parquet=self.root/"ca-missing.parquet"; parquet.write_bytes(b"fixture")
        columns=("date","code","open","high","low","close","corporate_action_flag","adjustment_factor","corporate_action_evidence_id")
        def handler(query,params):
            if query.startswith("DESCRIBE"): return [(x,) for x in columns]
            if "HAVING n>1" in query or "GREATEST" in query: return []
            if "AND (" in query: return [(date(2025,1,2),"005930",1.2,None)]
            return []
        with patch("tools.m3top3.providers.importlib.import_module",return_value=self._fake_duck(columns,handler)):
            self.assert_code("CA_EVIDENCE_INCOMPLETE",lambda: DuckDBParquetPriceProvider([parquet],"P",hash_file(parquet)))

    def test_kf_prc_006_canonical_parquet_is_globally_blocked_before_query(self):
        parquet=self.root/"canonical-no-ca.parquet"; parquet.write_bytes(b"fixture")
        columns=("date","code","open","high","low","close")
        def handler(query,params):
            if query.startswith("DESCRIBE"): return [(x,) for x in columns]
            return []
        release={"frozen":True,"authority_receipt":"SELF","ca_receipt":"SELF","unresolved_ca_candidates":0}
        with patch("tools.m3top3.providers.importlib.import_module",return_value=self._fake_duck(columns,handler)):
            self.assert_code("PRICE_CANONICAL_GLOBALLY_BLOCKED",lambda: DuckDBParquetPriceProvider([parquet],"P",hash_file(parquet),"PRICE_CANONICAL",release),4)

    def test_parquet_hash_mismatch_blocks_before_connect_or_query(self):
        parquet=self.root/"prequery-hash-mismatch.parquet"; parquet.write_bytes(b"fixture")
        calls=[]
        class Result:
            def __init__(self,rows): self.rows=rows
            def fetchall(self): return self.rows
            def fetchone(self): return self.rows[0] if self.rows else None
        class Connection:
            def execute(self,query,params=None):
                calls.append(query)
                if query.startswith("DESCRIBE"): return Result([(name,) for name in ("date","code","open","high","low","close")])
                return Result([])
        class Duck:
            @staticmethod
            def connect():
                calls.append("connect")
                return Connection()
        with patch("tools.m3top3.providers.importlib.import_module",return_value=Duck):
            self.assert_code("PRICE_COMPONENT_HASH_MISMATCH",lambda:DuckDBParquetPriceProvider([parquet],"P","0"*64))
        self.assertEqual(calls,[])

    def _multi_component_fixture(self):
        first=self.root/"part-a.parquet"; second=self.root/"part-b.parquet"
        first.write_bytes(b"component-a"); second.write_bytes(b"component-b")
        paths=[first,second]
        components=[{"component_id":f"P-MULTI:{index}","logical_name":path.name,"semantic_role":f"PRICE_PARTITION_{index}","path":str(path.resolve()),"artifact_sha256":hash_file(path),"byte_size":path.stat().st_size} for index,path in enumerate(paths,1)]
        dataset_hash=price_dataset_identity_hash("P-MULTI",components)
        manifest={
            "manifest_version":"m3top3-price-components-v2",
            "hash_algorithm":"SHA256",
            "dataset_id":"P-MULTI",
            "dataset_hash":dataset_hash,
            "component_set_digest":canonical_component_set_digest(components),
            "components":components,
        }
        columns=("date","code","open","high","low","close","corporate_action_flag","adjustment_factor","corporate_action_evidence_id")
        def handler(query,params):
            if query.startswith("DESCRIBE"): return [(x,) for x in columns]
            return []
        return paths,dataset_hash,manifest,self._fake_duck(columns,handler)

    def test_multi_component_price_requires_versioned_byte_manifest(self):
        paths,dataset_hash,_,duck=self._multi_component_fixture()
        with patch("tools.m3top3.providers.importlib.import_module",return_value=duck):
            self.assert_code(
                "PRICE_COMPONENT_MANIFEST_REQUIRED",
                lambda: DuckDBParquetPriceProvider(paths,"P-MULTI",dataset_hash),
            )

    def test_multi_component_price_manifest_binds_paths_bytes_and_dataset_identity(self):
        paths,dataset_hash,manifest,duck=self._multi_component_fixture()
        with patch("tools.m3top3.providers.importlib.import_module",return_value=duck):
            provider=DuckDBParquetPriceProvider(paths,"P-MULTI",dataset_hash,component_manifest=manifest)
        self.assertEqual(provider.actual_dataset_hash,dataset_hash)
        self.assertEqual(provider.component_manifest,manifest)

    def test_multi_component_price_manifest_tamper_is_hard_failure(self):
        paths,dataset_hash,manifest,duck=self._multi_component_fixture()
        manifest["components"][0]["artifact_sha256"]="0"*64
        with patch("tools.m3top3.providers.importlib.import_module",return_value=duck):
            self.assert_code(
                "LINEAGE_COMPONENT_HASH_MISMATCH",
                lambda: DuckDBParquetPriceProvider(paths,"P-MULTI",dataset_hash,component_manifest=manifest),
            )

    def test_multi_component_price_dataset_identity_tamper_is_hard_failure(self):
        paths,dataset_hash,manifest,duck=self._multi_component_fixture()
        manifest["dataset_hash"]="f"*64
        with patch("tools.m3top3.providers.importlib.import_module",return_value=duck):
            self.assert_code(
                "PRICE_COMPONENT_MANIFEST_MISMATCH",
                lambda: DuckDBParquetPriceProvider(paths,"P-MULTI",dataset_hash,component_manifest=manifest),
            )

    def test_parquet_component_mutation_after_init_is_rejected_before_lazy_query(self):
        paths,dataset_hash,manifest,duck=self._multi_component_fixture()
        with patch("tools.m3top3.providers.importlib.import_module",return_value=duck):
            provider=DuckDBParquetPriceProvider(paths,"P-MULTI",dataset_hash,component_manifest=manifest)
            paths[0].write_bytes(paths[0].read_bytes()+b"tamper")
            self.assert_code("PRICE_COMPONENT_HASH_MISMATCH",lambda:provider.trading_dates(date(2025,1,2),date(2025,1,31)))


if __name__ == "__main__":
    unittest.main()
