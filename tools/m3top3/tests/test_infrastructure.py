from __future__ import annotations

import csv
import tempfile
import unittest
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

from tools.m3top3.backtest import ValidationRunner
from tools.m3top3.admission import M3Top3AdmissionError
from tools.m3top3.core import hash_file
from tools.m3top3.ledger import PredictionLedger
from tools.m3top3.model_interface import DiagnosticFixtureScorer, RankingEngine, ScoreResult
from tools.m3top3.outcome import ExplicitWindowResolver, OutcomeBuilder
from tools.m3top3.pit_guard import PITGuard, PITLeakageError
from tools.m3top3.providers import CsvPriceProvider, InMemoryFeatureProvider, StaticUniverseProvider, UniverseState
from tools.m3top3.snapshot import BatchSnapshotGenerator, SnapshotBuildConfig, SnapshotBuilder, SnapshotStore


def business_dates(start: date, count: int):
    out=[]; d=start
    while len(out)<count:
        if d.weekday()<5: out.append(d)
        d+=timedelta(days=1)
    return out


def write_price_csv(path:Path,dates,codes=("005930",),base=100):
    with path.open("w",encoding="utf-8",newline="") as f:
        w=csv.writer(f); w.writerow(["date","code","open","high","low","close","volume"])
        for ci,code in enumerate(codes):
            for i,d in enumerate(dates):
                o=base+ci*10+i; w.writerow([d.isoformat(),code,o,o+3,o-2,o+1,1000+i])


class InfraTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.root=Path(self.tmp.name); self.dates=business_dates(date(2025,1,2),90); self.price_path=self.root/"price.csv"; write_price_csv(self.price_path,self.dates,codes=("005930","000660","035420")); self.price=CsvPriceProvider(self.price_path,dataset_hash=hash_file(self.price_path))
        states=[UniverseState("C1","005930",date(2020,1,1),None,True,True,"U1"),UniverseState("C2","000660",date(2020,1,1),None,True,False,"U2"),UniverseState("C3","035420",date(2020,1,1),None,True,True,"U3")]; partial_states=[*states[:2],UniverseState("C3","035420",date(2020,1,1),None,True,None,"U3")]; self.universe=StaticUniverseProvider(states,"U127-WORKING","WORKING_FREEZE_CANDIDATE"); pub="2025-01-02T10:00:00+09:00"
        self.features=InMemoryFeatureProvider([{"company_id":"C1","feature_id":"diagnostic_score","value":"9","publication_at":pub,"evidence_id":"E1","status":"VERIFIED"},{"company_id":"C2","feature_id":"diagnostic_score","value":"8","publication_at":pub,"evidence_id":"E2","status":"VERIFIED"},{"company_id":"C3","feature_id":"diagnostic_score","value":"7","publication_at":pub,"evidence_id":"E3","status":"VERIFIED"}]); self.builder=SnapshotBuilder(self.universe,self.features,self.price,SnapshotBuildConfig()); self.partial_builder=SnapshotBuilder(StaticUniverseProvider(partial_states,"U127-WORKING","WORKING_FREEZE_CANDIDATE"),self.features,self.price,SnapshotBuildConfig())
    def tearDown(self): self.tmp.cleanup()
    def test_01_single_date_snapshot_deterministic(self):
        a=self.builder.build(self.dates[0]); b=self.builder.build(self.dates[0]); self.assertEqual(a.snapshot_set_entry_hash,b.snapshot_set_entry_hash); self.assertEqual(a.pit_rows,b.pit_rows)
    def test_02_same_input_same_snapshot_ids(self):
        a=self.builder.build(self.dates[0]); b=self.builder.build(self.dates[0]); self.assertEqual([x["pit_snapshot_id"] for x in a.pit_rows],[x["pit_snapshot_id"] for x in b.pit_rows])
    def test_03_publication_after_cutoff_rejected(self):
        with self.assertRaises(PITLeakageError): PITGuard().assert_model_inputs([{"feature_id":"x","publication_at":"2025-01-03T00:00:00+09:00"}],"2025-01-02T23:59:59+09:00")
    def test_04_publication_at_cutoff_allowed(self): PITGuard().assert_model_inputs([{"feature_id":"x","publication_at":"2025-01-02T23:59:59+09:00"}],"2025-01-02T23:59:59+09:00")
    def test_05_future_price_field_rejected(self):
        with self.assertRaises(PITLeakageError): PITGuard().assert_model_inputs([{"feature_values":{"future_close":1}}],"2025-01-02T23:59:59+09:00")
    def test_06_mfe_input_rejected(self):
        with self.assertRaises(PITLeakageError): PITGuard().assert_model_inputs([{"feature_values":{"MFE":1}}],"2025-01-02T23:59:59+09:00")
    def test_07_eligibility_semantics_preserved(self):
        built=self.partial_builder.build(self.dates[0]); self.assertEqual({x["company_id"]:x["entry_eligible"] for x in built.model_inputs},{"C1":"TRUE","C2":"FALSE","C3":"UNRESOLVED"}); self.assertEqual(built.status,"SNAPSHOT_PARTIAL")
    def test_08_leading_zero_code_preserved(self): self.assertEqual(self.builder.build(self.dates[0]).model_inputs[0]["security_code"],"005930")
    def test_09_company_id_survives_name_independence(self): self.assertEqual(self.builder.build(self.dates[0]).pit_rows[0]["company_id"],"C1")
    def test_10_listing_effective_boundary(self):
        u=StaticUniverseProvider([UniverseState("LATE","123456",self.dates[5],None,True,True,"UL")]); b=SnapshotBuilder(u,InMemoryFeatureProvider([]),self.price,SnapshotBuildConfig()); self.assertEqual(len(b.build(self.dates[4]).pit_rows),0)
    def test_11_entry_first_trading_day_after_snapshot(self): self.assertEqual(OutcomeBuilder(self.price,ExplicitWindowResolver({self.dates[0].isoformat():self.dates[10].isoformat()})).build("S1","005930",self.dates[0]).entry_date,self.dates[1])
    def test_12_mfe_begins_entry_and_ends_window(self):
        o=OutcomeBuilder(self.price,ExplicitWindowResolver({self.dates[0].isoformat():self.dates[10].isoformat()})).build("S1","005930",self.dates[0]); held=self.price.rows("005930",self.dates[1],self.dates[10]); self.assertEqual(o.mfe,max(r.high for r in held)); self.assertEqual(o.mae,min(r.low for r in held))
    def test_13_exit_first_open_after_window(self):
        o=OutcomeBuilder(self.price,ExplicitWindowResolver({self.dates[0].isoformat():self.dates[10].isoformat()})).build("S1","005930",self.dates[0]); self.assertEqual(o.exit_date,self.dates[11]); self.assertEqual(o.exit,self.price.row("005930",self.dates[11]).open)
    def test_14_horizon_close_separate(self):
        o=OutcomeBuilder(self.price,ExplicitWindowResolver({self.dates[0].isoformat():self.dates[10].isoformat()})).build("S1","005930",self.dates[0]); self.assertEqual(o.horizon_close,self.price.row("005930",self.dates[10]).close); self.assertEqual(o.exit,self.price.row("005930",self.dates[11]).open)
    def test_15_pending_outcome_valid(self): self.assertEqual(OutcomeBuilder(self.price,ExplicitWindowResolver({self.dates[-2].isoformat():self.dates[-1].isoformat()})).build("S1","005930",self.dates[-2]).outcome_validity,"PENDING_EXIT")
    def test_16_batch_resume_reuses(self):
        store=SnapshotStore(self.root/"snaps"); batch=BatchSnapshotGenerator(self.builder,store); r1=batch.run(self.dates[0],self.dates[4],{"generator_version":"v0"}); r2=batch.run(self.dates[0],self.dates[4],{"generator_version":"v0"}); self.assertEqual((r1.generated,r2.reused),(5,5)); self.assertTrue(r2.accounting_pass)
    def test_17_prediction_ledger_immutable(self):
        p=PredictionLedger(self.root/"pred.jsonl"); row={"prediction_id":"P1","x":1}; self.assertEqual(p.append(row),"APPENDED"); self.assertEqual(p.append(row),"REUSED");
        with self.assertRaises(M3Top3AdmissionError) as caught: p.append({"prediction_id":"P1","x":2})
        self.assertEqual((caught.exception.code,caught.exception.exit_code),("NONDETERMINISTIC_RERUN",3))
    def test_18_multi_model_same_snapshot_possible(self):
        pit=self.builder.build(self.dates[0]).model_inputs[0]["pit_snapshot_id"]; s1=ScoreResult("S1",pit,"C1","005930","m1",Decimal("1"),"OK",[]); s2=ScoreResult("S2",pit,"C1","005930","m2",Decimal("1"),"OK",[]); self.assertEqual(s1.pit_snapshot_id,s2.pit_snapshot_id); self.assertNotEqual(s1.model_version,s2.model_version)
    def test_19_tie_policy_blocks_official_resolution(self):
        pit=self.builder.build(self.dates[0]).model_inputs[0]["pit_snapshot_id"]; scores=[ScoreResult("S1",pit,"C1","005930","m",Decimal("1"),"OK",[]),ScoreResult("S2","P2","C2","000660","m",Decimal("1"),"OK",[])]; self.assertEqual(RankingEngine().rank(scores,{pit:"TRUE","P2":"TRUE"})[0]["status"],"BLOCKED_TIE_POLICY_UNRESOLVED")
    def test_20_snapshot_has_no_model_version(self): self.assertTrue(all("model_version" not in x for x in self.builder.build(self.dates[0]).pit_rows))
    def test_21_raw_outcome_ca_pending(self):
        o=OutcomeBuilder(self.price,ExplicitWindowResolver({self.dates[0].isoformat():self.dates[10].isoformat()})).build("S1","005930",self.dates[0]); self.assertEqual(o.outcome_comparability_status,"CA_PENDING"); self.assertEqual(o.status,"PRELIMINARY")
    def test_22_backtest_runner_separates_outcome(self):
        u=StaticUniverseProvider([UniverseState("C1","005930",date(2020,1,1),None,True,True,"U1")]); f=InMemoryFeatureProvider([{"company_id":"C1","feature_id":"diagnostic_score","value":"9","publication_at":"2025-01-02T10:00:00+09:00"}]); b=SnapshotBuilder(u,f,self.price,SnapshotBuildConfig()); store=SnapshotStore(self.root/"bt_snaps"); built=b.build(self.dates[0]); store.write(built,{"generator_version":"v0"}); runner=ValidationRunner(DiagnosticFixtureScorer(),RankingEngine(),OutcomeBuilder(self.price,ExplicitWindowResolver({self.dates[0].isoformat():self.dates[10].isoformat()}))); out=runner.run_snapshot(self.root/"bt_snaps"/self.dates[0].isoformat(),self.root/"bt_out"); self.assertEqual(out["outcome_count"],1); self.assertNotIn('"mfe"',(self.root/"bt_snaps"/self.dates[0].isoformat()/"model_input.jsonl").read_text().lower())
    def test_23_scale_420_dates_and_resume(self):
        dates=business_dates(date(2024,1,2),420); pp=self.root/"scale.csv"; write_price_csv(pp,dates,codes=("005930",)); price=CsvPriceProvider(pp,dataset_hash=hash_file(pp)); u=StaticUniverseProvider([UniverseState("C1","005930",date(2020,1,1),None,True,True,"U1")]); builder=SnapshotBuilder(u,InMemoryFeatureProvider([]),price,SnapshotBuildConfig()); store=SnapshotStore(self.root/"scale_snaps"); batch=BatchSnapshotGenerator(builder,store); r1=batch.run(dates[0],dates[-1],{"generator_version":"v0"}); r2=batch.run(dates[0],dates[-1],{"generator_version":"v0"}); self.assertEqual((r1.requested,r1.generated,r1.failed),(420,420,0)); self.assertEqual((r2.requested,r2.reused,r2.failed),(420,420,0)); self.assertTrue(r1.accounting_pass and r2.accounting_pass)
    def test_24_failed_date_retry_works(self):
        class FlakyBuilder:
            def __init__(self,inner,target): self.inner=inner; self.price=inner.price; self.target=target; self.seen=False
            def build(self,d):
                if d==self.target and not self.seen: self.seen=True; raise RuntimeError("transient")
                return self.inner.build(d)
        batch=BatchSnapshotGenerator(FlakyBuilder(self.builder,self.dates[2]),SnapshotStore(self.root/"retry_snaps"),retries=1); r=batch.run(self.dates[0],self.dates[4],{"generator_version":"v0"}); self.assertEqual((r.requested,r.generated,r.failed),(5,5,0)); self.assertTrue(r.accounting_pass)
    def test_25_representative_historical_regression_dates(self):
        reps=[date(2025,8,13),date(2025,11,13),date(2026,2,13),date(2026,5,13)]; all_dates=[]
        for d in reps: all_dates.extend([d,d+timedelta(days=1)])
        pp=self.root/"reps.csv"; write_price_csv(pp,all_dates,codes=("005930",)); price=CsvPriceProvider(pp,dataset_hash=hash_file(pp)); u=StaticUniverseProvider([UniverseState("C1","005930",date(2020,1,1),None,True,True,"U1")]); b=SnapshotBuilder(u,InMemoryFeatureProvider([]),price,SnapshotBuildConfig()); hashes=[b.build(d).snapshot_set_entry_hash for d in reps]; self.assertEqual(len(hashes),4); self.assertEqual(len(set(hashes)),4)


if __name__=="__main__": unittest.main()
