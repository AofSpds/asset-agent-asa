from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Any

from .core import aggregate_hash, atomic_write_json, deterministic_id, sha256_hex, snapshot_cutoff
from .pit_guard import PITGuard, PITLeakageError
from .providers import PITFeatureProvider, PriceProvider, UniverseProvider, UniverseState


@dataclass(frozen=True)
class SnapshotBuildConfig:
    snapshot_schema_version: str = "v0.1"
    model_input_schema_version: str = "m3top3-input-v0.1-working"
    generator_version: str = "m3top3-infra-v0.1"
    timezone: str = "Asia/Seoul"
    cutoff_local_time: str = "23:59:59"
    price_source_semantics: str = "RAW_IMMUTABLE"
    reconstruction_version: str = "RECONSTRUCTION_v0.1_WORKING"


@dataclass
class BuiltSnapshot:
    snapshot_date: date
    cutoff_at: datetime
    snapshot_set_entry_hash: str
    pit_rows: list[dict[str, Any]]
    model_inputs: list[dict[str, Any]]
    status: str
    blockers: list[str] = field(default_factory=list)


class SnapshotBuilder:
    def __init__(self, universe: UniverseProvider, features: PITFeatureProvider, price: PriceProvider, config: SnapshotBuildConfig, guard: PITGuard | None = None):
        self.universe=universe; self.features=features; self.price=price; self.config=config; self.guard=guard or PITGuard()

    def _build_company(self, state: UniverseState, snapshot_date: date, cutoff_at: datetime):
        raw_features=[dict(r) for r in self.features.records_at(state.company_id, cutoff_at)]; blockers=[]
        try: self.guard.assert_model_inputs(raw_features, cutoff_at)
        except PITLeakageError as exc: blockers.extend(v.code for v in exc.violations)
        observation_refs=[]; evidence_refs=[]; model_features={}; feature_trace=[]
        for r in raw_features:
            if r.get("evidence_id"):
                evidence_refs.append(str(r["evidence_id"])); observation_refs.append({"domain":"EVIDENCE","reference_payload":{"evidence_id":str(r["evidence_id"])}})
            if r.get("event_record_id"): observation_refs.append({"domain":"EVENT","reference_payload":{"event_record_id":str(r["event_record_id"])}})
            feature_id=r.get("feature_id")
            if feature_id:
                model_features[str(feature_id)]=r.get("value")
                feature_trace.append({"feature_id":str(feature_id),"value":r.get("value"),"as_of":r.get("as_of"),"effective_at":r.get("effective_at"),"publication_at":r.get("publication_at"),"source_ref":r.get("source_ref"),"evidence_id":r.get("evidence_id"),"status":r.get("status","VERIFIED")})
        price_row=self.price.row(state.security_code,snapshot_date)
        if price_row is not None:
            if self.price.semantics=="PRICE_CANONICAL": observation_refs.append({"domain":"PRICE_CANONICAL","reference_payload":{"price_dataset_id":self.price.dataset_id,"date":snapshot_date.isoformat(),"code":state.security_code}})
            else: observation_refs.append({"domain":"SOURCE_DATASET_LOCATOR","reference_payload":{"source_id":self.price.dataset_id,"locator":f"row://{snapshot_date.isoformat()}/{state.security_code}"}})
            model_features.setdefault("price_close",str(price_row.close))
            if price_row.marcap is not None: model_features.setdefault("market_cap",str(price_row.marcap))
        eligibility="UNRESOLVED"
        if state.operational_member is False or state.tradable_eligible is False: eligibility="FALSE"
        elif state.operational_member is True and state.tradable_eligible is True: eligibility="TRUE"
        if eligibility=="UNRESOLVED": blockers.append("ELIGIBILITY_UNRESOLVED")
        f1_refs=[]
        for r in raw_features:
            ref=r.get("f1_f2_ref")
            if isinstance(ref,dict) and ref.get("domain") and ref.get("ref_id"): f1_refs.append({"domain":str(ref["domain"]),"ref_id":str(ref["ref_id"])})
        semantic={"company_id":state.company_id,"snapshot_cutoff_at":cutoff_at.isoformat(),"snapshot_schema_version":self.config.snapshot_schema_version,"snapshot_revision":0,"f1_f2_effective_refs":f1_refs,"f3_observation_refs":observation_refs,"evidence_refs":sorted(set(evidence_refs)),"dataset_refs":[{"domain":"SOURCE_DATASET","source_id":self.price.dataset_id,"content_hash":self.price.dataset_hash,"locator":None}],"universe_release_id":self.universe.release_id,"tradability_state_ref":{"domain":"TRADABILITY_HISTORY","ref_id":state.universe_record_id}}
        pit_snapshot_id=deterministic_id("pit",semantic); capture_run_id=deterministic_id("capture",{"pit_snapshot_id":pit_snapshot_id,"generator_version":self.config.generator_version})
        pit_row={"pit_snapshot_id":pit_snapshot_id,"company_id":state.company_id,"snapshot_cutoff_at":cutoff_at.isoformat(),"snapshot_date":snapshot_date.isoformat(),"snapshot_schema_version":self.config.snapshot_schema_version,"snapshot_revision":0,"supersedes_ref":None,"capture_run_id":capture_run_id,"snapshot_frozen":False,"snapshot_frozen_at":None,"f1_f2_effective_refs":f1_refs,"f3_observation_refs":observation_refs,"evidence_refs":sorted(set(evidence_refs)) or None,"dataset_refs":semantic["dataset_refs"],"universe_release_id":self.universe.release_id,"tradability_state_ref":semantic["tradability_state_ref"],"schema_version":self.config.snapshot_schema_version}
        model_input={"pit_snapshot_id":pit_snapshot_id,"snapshot_date":snapshot_date.isoformat(),"snapshot_cutoff_at":cutoff_at.isoformat(),"company_id":state.company_id,"security_code":str(state.security_code).zfill(6),"universe_member":state.operational_member,"entry_eligible":eligibility,"universe_authority_status":self.universe.authority_status,"price_dataset_id":self.price.dataset_id,"price_source_semantics":self.price.semantics,"feature_values":model_features,"feature_trace":feature_trace,"model_input_schema_version":self.config.model_input_schema_version,"reconstruction_version":self.config.reconstruction_version}
        self.guard.assert_model_inputs([model_input],cutoff_at)
        return pit_row,model_input,blockers

    def build(self,snapshot_date:date)->BuiltSnapshot:
        cutoff_at=snapshot_cutoff(snapshot_date,self.config.cutoff_local_time,self.config.timezone); states=self.universe.states_at(snapshot_date); pit_rows=[]; model_inputs=[]; blockers=[]
        for state in sorted(states,key=lambda x:(x.company_id,x.security_code)):
            p,m,b=self._build_company(state,snapshot_date,cutoff_at); pit_rows.append(p); model_inputs.append(m); blockers.extend(f"{state.company_id}:{x}" for x in b)
        entry_hash=aggregate_hash([sha256_hex(p) for p in pit_rows]+[sha256_hex(m) for m in model_inputs])
        if not states: status="SNAPSHOT_BLOCKED"; blockers.append("NO_UNIVERSE_STATES")
        elif blockers: status="SNAPSHOT_PARTIAL"
        else: status="SNAPSHOT_READY"
        return BuiltSnapshot(snapshot_date,cutoff_at,entry_hash,pit_rows,model_inputs,status,sorted(set(blockers)))


class SnapshotStore:
    def __init__(self,root:str|Path): self.root=Path(root)
    def _dir(self,d:date)->Path: return self.root/d.isoformat()
    def valid_existing(self,built:BuiltSnapshot)->bool:
        p=self._dir(built.snapshot_date)/"manifest.json"
        if not p.exists(): return False
        try: manifest=json.loads(p.read_text(encoding="utf-8"))
        except Exception: return False
        return manifest.get("snapshot_content_hash")==built.snapshot_set_entry_hash
    def write(self,built:BuiltSnapshot,metadata:dict[str,Any])->dict[str,Any]:
        d=self._dir(built.snapshot_date); d.mkdir(parents=True,exist_ok=True)
        pit_text="".join(json.dumps(r,ensure_ascii=False,sort_keys=True,separators=(",",":"))+"\n" for r in built.pit_rows); mi_text="".join(json.dumps(r,ensure_ascii=False,sort_keys=True,separators=(",",":"))+"\n" for r in built.model_inputs)
        (d/"pit_snapshot.jsonl").write_text(pit_text,encoding="utf-8"); (d/"model_input.jsonl").write_text(mi_text,encoding="utf-8")
        manifest={**metadata,"snapshot_date":built.snapshot_date.isoformat(),"snapshot_cutoff_at":built.cutoff_at.isoformat(),"snapshot_content_hash":built.snapshot_set_entry_hash,"snapshot_status":built.status,"blockers":built.blockers,"pit_row_count":len(built.pit_rows),"model_input_row_count":len(built.model_inputs),"pit_file_sha256":sha256_hex(pit_text),"model_input_file_sha256":sha256_hex(mi_text)}; atomic_write_json(d/"manifest.json",manifest); return manifest


@dataclass
class BatchResult:
    requested:int; generated:int; failed:int; reused:int; failed_dates:list[str]; manifests:list[dict[str,Any]]
    @property
    def accounting_pass(self)->bool: return self.requested==self.generated+self.failed+self.reused


class BatchSnapshotGenerator:
    def __init__(self,builder:SnapshotBuilder,store:SnapshotStore,retries:int=1): self.builder=builder; self.store=store; self.retries=max(0,retries)
    def run(self,start:date,end:date,metadata:dict[str,Any])->BatchResult:
        dates=self.builder.price.trading_dates(start,end); generated=failed=reused=0; failed_dates=[]; manifests=[]
        for d in dates:
            last_error=None
            for _ in range(self.retries+1):
                try:
                    built=self.builder.build(d)
                    if self.store.valid_existing(built): reused+=1; break
                    manifests.append(self.store.write(built,metadata)); generated+=1; break
                except Exception as exc: last_error=exc
            else:
                failed+=1; failed_dates.append(f"{d.isoformat()}:{type(last_error).__name__}:{last_error}")
        return BatchResult(len(dates),generated,failed,reused,failed_dates,manifests)
