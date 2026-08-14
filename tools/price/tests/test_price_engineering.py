from __future__ import annotations
from pathlib import Path
import sys, unittest
import numpy as np
HERE=Path(__file__).resolve(); PRICE_DIR=HERE.parents[1]
if str(PRICE_DIR) not in sys.path: sys.path.insert(0,str(PRICE_DIR))
from price_audit_rules import (OHLC_CLASS_NORMAL,OHLC_CLASS_OTHER_INCONSISTENCY,OHLC_CLASS_ZERO_OHL_NO_TRADE_METRICS,OHLC_CLASS_ZERO_OHL_WITH_TRADE_METRICS,canonical_row_accounting,classify_ohlc,code_lexical_failures,map_company_ids,numeric_audit)
from price_ca_interface import canonical_ca_projection,validate_ca_event
from price_canonical_dryrun import _date_days,_duplicate_mask,_manifest_components

class PriceEngineeringTests(unittest.TestCase):
 def test_01_leading_zero_code_preservation(self):
  codes=np.array(["000020","005930"],dtype=object); self.assertEqual(code_lexical_failures(codes),(0,0)); self.assertEqual(codes[0],"000020")
 def test_02_alphanumeric_code_preservation(self):
  codes=np.array(["0017J0","005930"],dtype=object); self.assertEqual(code_lexical_failures(codes),(0,0)); self.assertEqual(codes[0],"0017J0")
 def test_03_ns_date_normalization(self):
  days=_date_days(np.array([1704153600000000000],dtype=np.int64),"ns"); self.assertEqual(np.datetime_as_string(np.datetime64(int(days[0]),"D")),"2024-01-02")
 def test_04_us_date_normalization(self):
  days=_date_days(np.array([1767312000000000],dtype=np.int64),"us"); self.assertEqual(np.datetime_as_string(np.datetime64(int(days[0]),"D")),"2026-01-02")
 def test_05_duplicate_date_code_detection(self):
  self.assertEqual(_duplicate_mask(np.array([1,1,2]),np.array(["005930","005930","005930"],dtype=object)).tolist(),[True,True,False])
 def test_06_normal_ohlc(self):
  c=classify_ohlc(np.array([10.]),np.array([13.]),np.array([9.]),np.array([12.]),np.array([100.]),np.array([1200.])); self.assertEqual(c[0],OHLC_CLASS_NORMAL)
 def test_07_zero_ohl_zero_trade(self):
  c=classify_ohlc(np.array([0.]),np.array([0.]),np.array([0.]),np.array([12.]),np.array([0.]),np.array([0.])); self.assertEqual(c[0],OHLC_CLASS_ZERO_OHL_NO_TRADE_METRICS)
 def test_08_zero_ohl_nonzero_trade(self):
  c=classify_ohlc(np.array([0.]),np.array([0.]),np.array([0.]),np.array([12.]),np.array([1.]),np.array([12.])); self.assertEqual(c[0],OHLC_CLASS_ZERO_OHL_WITH_TRADE_METRICS)
 def test_09_other_ohlc_inconsistency(self):
  c=classify_ohlc(np.array([10.]),np.array([9.]),np.array([8.]),np.array([8.5]),np.array([1.]),np.array([9.])); self.assertEqual(c[0],OHLC_CLASS_OTHER_INCONSISTENCY)
 def test_10_volume_fractional_rejection(self): self.assertEqual(numeric_audit(np.array([1.,2.5])).fractional_count,1)
 def test_11_nonfinite_rejection(self): self.assertEqual(numeric_audit(np.array([1.,np.inf])).nonfinite_count,1)
 def test_12_company_id_nullable_behavior(self): self.assertIsNone(map_company_ids(np.array(["005930"],dtype=object),{})[0])
 def test_13_company_id_no_guessing(self):
  m=map_company_ids(np.array(["005930","000660"],dtype=object),{"005930":"COMPANY:SAMSUNG"}); self.assertEqual(m[0],"COMPANY:SAMSUNG"); self.assertIsNone(m[1])
 def test_14_raw_storage_ref_preserved(self):
  c=_manifest_components({"components":[{"year":2024,"stable_storage_locator":"s3://bucket/raw/price/2024.parquet"}]}); self.assertEqual(c[2024]["stable_storage_locator"],"s3://bucket/raw/price/2024.parquet")
 def test_15_ca_evidence_free_adjustment_rejected(self):
  e={"event_id":"E1","security_code":"005930","company_id":"COMPANY:SAMSUNG","event_date":"2026-01-02","event_type":"SPLIT","publication_at":"2026-01-01T09:00:00+09:00","effective_at":"2026-01-02T00:00:00+09:00","comparable_price_impact":True,"adjustment_required":True,"adjustment_factor_if_supported":"0.5","evidence_refs":[],"validation_status":"VERIFIED"}
  self.assertFalse(validate_ca_event(e).valid)
  with self.assertRaises(ValueError): canonical_ca_projection(e)
 def test_16_row_accounting_closes(self): self.assertTrue(canonical_row_accounting(100,80,15,5)); self.assertFalse(canonical_row_accounting(100,80,15,4))

if __name__=="__main__": unittest.main()
