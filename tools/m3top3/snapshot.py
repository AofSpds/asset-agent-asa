from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Any

from .admission import (
    EXIT_BLOCKED,
    EXIT_INTEGRITY,
    M3Top3AdmissionError,
    _snapshot_manifest_identity_payload,
    lineage_ref_map,
    reverify_execution_lineage,
    synthetic_fixture_lineage,
    universe_member_identity,
    verify_feature_release,
    verify_lineage_temporal_compatibility,
    verify_price_release,
    verify_snapshot_artifacts,
    verify_universe_release,
)
from .core import aggregate_hash, atomic_write_json, atomic_write_text, deterministic_id, hash_file, sha256_hex, snapshot_cutoff
from .pit_guard import PITGuard, PITLeakageError
from .providers import InMemoryFeatureProvider, JsonlFeatureProvider, PITFeatureProvider, PriceProvider, UniverseProvider, UniverseState


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
    retrieval_audits: list[dict[str, Any]]
    status: str
    blockers: list[str] = field(default_factory=list)
    lineage: dict[str, Any] = field(default_factory=dict)


class SnapshotBuilder:
    def __init__(self, universe: UniverseProvider, features: PITFeatureProvider, price: PriceProvider, config: SnapshotBuildConfig, guard: PITGuard | None = None, execution_lineage: dict[str,Any]|None=None):
        self.universe=universe; self.features=features; self.price=price; self.config=config; self.guard=guard or PITGuard()
        self.execution_lineage=execution_lineage or synthetic_fixture_lineage(universe,features,price)

    def _build_company(self, state: UniverseState, snapshot_date: date, cutoff_at: datetime, lineage: dict[str, Any]):
        receipts_before=len(getattr(self.features,"retrieval_receipts",[])) if hasattr(self.features,"retrieval_receipts") else None
        raw_features=[dict(r) for r in self.features.records_at(state.company_id, cutoff_at)]; blockers=[]
        retrieval_receipt=self._require_retrieval_receipt(state.company_id,cutoff_at,raw_features,receipts_before)
        expected_features,expected_receipt=self._independent_retrieval_slice(state.company_id,cutoff_at)
        if raw_features!=expected_features or retrieval_receipt!=expected_receipt:
            raise M3Top3AdmissionError(
                "RETRIEVAL_RECEIPT_RECONCILIATION_FAILED",
                "provider output/receipt differs from an independent reconstruction over the admitted raw source",
                {"company_id":state.company_id,"selected_actual":len(raw_features),"selected_expected":len(expected_features)},
                EXIT_BLOCKED,
            )
        raw_features=expected_features; retrieval_receipt=expected_receipt
        self.guard.assert_model_inputs(raw_features, cutoff_at)
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
        member_id=universe_member_identity(state)
        eligibility_record=lineage["eligibility_records"][member_id]
        decision_status=eligibility_record["eligibility_status"]
        eligibility="TRUE" if decision_status=="ELIGIBLE" else "FALSE" if decision_status=="INELIGIBLE" else "UNRESOLVED"
        if eligibility=="UNRESOLVED": blockers.append("ELIGIBILITY_UNRESOLVED")
        f1_refs=[]
        for r in raw_features:
            ref=r.get("f1_f2_ref")
            if isinstance(ref,dict) and ref.get("domain") and ref.get("ref_id"): f1_refs.append({"domain":str(ref["domain"]),"ref_id":str(ref["ref_id"])})
        dataset_refs=[lineage["release_ref_map"][domain] for domain in ("UNIVERSE_RELEASE","DENOMINATOR_ELIGIBILITY_RELEASE","FEATURE_SOURCE_RELEASE","PRICE_RELEASE","TRADING_CALENDAR_RELEASE")]
        semantic={"company_id":state.company_id,"snapshot_cutoff_at":cutoff_at.isoformat(),"snapshot_schema_version":self.config.snapshot_schema_version,"snapshot_revision":0,"f1_f2_effective_refs":f1_refs,"f3_observation_refs":observation_refs,"evidence_refs":sorted(set(evidence_refs)) or None,"dataset_refs":dataset_refs,"universe_lineage_manifest_hash":lineage["universe_lineage_manifest_hash"],"universe_authority_status":lineage["universe_authority_status"],"universe_release_id":self.universe.release_id,"universe_release_revision":lineage["universe_release_revision"],"universe_release_hash":lineage["universe_release_hash"],"universe_release_status":lineage["universe_release_status"],"denominator_release_id":lineage["denominator_release_id"],"denominator_release_revision":lineage["denominator_release_revision"],"denominator_release_hash":lineage["denominator_release_hash"],"denominator_release_status":lineage["denominator_release_status"],"denominator_member_id":member_id,"eligibility_record_id":eligibility_record["eligibility_record_id"],"eligibility_status":eligibility_record["eligibility_status"],"tradability_state_ref":{"domain":"TRADABILITY_HISTORY","ref_id":state.universe_record_id},"retrieval_receipt_id":retrieval_receipt["retrieval_receipt_id"],"retrieval_source_hash":retrieval_receipt["source_hash"]}
        pit_snapshot_id=deterministic_id("pit",semantic); capture_run_id=deterministic_id("capture",{"pit_snapshot_id":pit_snapshot_id,"generator_version":self.config.generator_version})
        pit_row={"pit_snapshot_id":pit_snapshot_id,"company_id":state.company_id,"security_code":str(state.security_code).zfill(6),"snapshot_cutoff_at":cutoff_at.isoformat(),"snapshot_date":snapshot_date.isoformat(),"snapshot_schema_version":self.config.snapshot_schema_version,"snapshot_revision":0,"supersedes_ref":None,"capture_run_id":capture_run_id,"generator_version":self.config.generator_version,"snapshot_frozen":False,"snapshot_frozen_at":None,"f1_f2_effective_refs":f1_refs,"f3_observation_refs":observation_refs,"evidence_refs":semantic["evidence_refs"],"dataset_refs":semantic["dataset_refs"],"universe_lineage_manifest_hash":lineage["universe_lineage_manifest_hash"],"universe_authority_status":lineage["universe_authority_status"],"universe_release_id":self.universe.release_id,"universe_release_revision":lineage["universe_release_revision"],"universe_release_hash":lineage["universe_release_hash"],"universe_release_status":lineage["universe_release_status"],"denominator_release_id":lineage["denominator_release_id"],"denominator_release_revision":lineage["denominator_release_revision"],"denominator_release_hash":lineage["denominator_release_hash"],"denominator_release_status":lineage["denominator_release_status"],"denominator_member_id":member_id,"eligibility_record_id":eligibility_record["eligibility_record_id"],"eligibility_status":eligibility_record["eligibility_status"],"tradability_state_ref":semantic["tradability_state_ref"],"retrieval_receipt_id":retrieval_receipt["retrieval_receipt_id"],"retrieval_source_hash":retrieval_receipt["source_hash"],"schema_version":self.config.snapshot_schema_version}
        model_input={"pit_snapshot_id":pit_snapshot_id,"snapshot_date":snapshot_date.isoformat(),"snapshot_cutoff_at":cutoff_at.isoformat(),"company_id":state.company_id,"security_code":str(state.security_code).zfill(6),"universe_record_id":state.universe_record_id,"universe_valid_from":state.valid_from.isoformat() if state.valid_from else None,"universe_valid_to":state.valid_to.isoformat() if state.valid_to else None,"universe_member":state.operational_member,"tradable_eligible":state.tradable_eligible,"universe_member_status":state.status,"denominator_member_id":member_id,"eligibility_record_id":eligibility_record["eligibility_record_id"],"eligibility_status":eligibility_record["eligibility_status"],"entry_eligible":eligibility,"dataset_refs":semantic["dataset_refs"],"universe_authority_status":self.universe.authority_status,"universe_lineage_manifest_hash":lineage["universe_lineage_manifest_hash"],"universe_release_id":self.universe.release_id,"universe_release_revision":lineage["universe_release_revision"],"universe_release_hash":lineage["universe_release_hash"],"universe_release_status":lineage["universe_release_status"],"denominator_release_id":lineage["denominator_release_id"],"denominator_release_revision":lineage["denominator_release_revision"],"denominator_release_hash":lineage["denominator_release_hash"],"denominator_release_status":lineage["denominator_release_status"],"feature_source_version":self.features.source_version,"feature_source_hash":self.features.source_hash,"feature_source_status":self.features.source_status,"price_dataset_id":self.price.dataset_id,"price_dataset_hash":self.price.dataset_hash,"price_source_semantics":self.price.semantics,"price_release_status":self.price.release_status,"retrieval_receipt_id":retrieval_receipt["retrieval_receipt_id"],"retrieval_source_hash":retrieval_receipt["source_hash"],"feature_values":model_features,"feature_trace":feature_trace,"model_input_schema_version":self.config.model_input_schema_version,"reconstruction_version":self.config.reconstruction_version}
        self.guard.assert_model_inputs([model_input],cutoff_at)
        audit=dict(retrieval_receipt) if isinstance(retrieval_receipt,dict) else None
        if audit is not None:
            audit.update({"security_code_at_cutoff":str(state.security_code).zfill(6),"snapshot_date":snapshot_date.isoformat(),"snapshot_cutoff_at":cutoff_at.isoformat(),"pit_snapshot_id":pit_snapshot_id,"universe_release_id":self.universe.release_id,"universe_release_revision":lineage["universe_release_revision"],"denominator_release_id":lineage["denominator_release_id"],"denominator_release_revision":lineage["denominator_release_revision"],"eligibility_record_id":eligibility_record["eligibility_record_id"],"eligibility_status":eligibility_record["eligibility_status"],"entry_eligible":eligibility})
        return pit_row,model_input,blockers,audit

    def _independent_retrieval_slice(self,company_id:str,cutoff_at:datetime)->tuple[list[dict[str,Any]],dict[str,Any]]:
        if type(self.features) is JsonlFeatureProvider:
            shadow=JsonlFeatureProvider(self.features.path,self.features.source_version,self.features.cutoff_frozen_bundle,self.features.source_status)
        elif type(self.features) is InMemoryFeatureProvider:
            shadow=InMemoryFeatureProvider(self.features._rows,self.features.source_version,self.features.cutoff_frozen_bundle,self.features.source_status)
        elif isinstance(self.features,(JsonlFeatureProvider,InMemoryFeatureProvider)):
            raise M3Top3AdmissionError(
                "RETRIEVAL_RECEIPT_RECONCILIATION_FAILED",
                "feature-provider subclasses are not admitted at the raw-source trust boundary",
                {"provider_type":type(self.features).__name__},
                EXIT_BLOCKED,
            )
        else:
            raise M3Top3AdmissionError(
                "MISSING_DETERMINISTIC_RETRIEVAL_RECEIPT",
                "feature provider has no independently auditable raw-source adapter",
                {"provider_type":type(self.features).__name__},
                EXIT_BLOCKED,
            )
        rows=[dict(row) for row in shadow.records_at(company_id,cutoff_at)]
        receipt=shadow.last_retrieval_receipt
        if not isinstance(receipt,dict):
            raise M3Top3AdmissionError("MISSING_DETERMINISTIC_RETRIEVAL_RECEIPT","independent raw-source reconstruction emitted no receipt",exit_code=EXIT_BLOCKED)
        return rows,dict(receipt)

    def _require_retrieval_receipt(self,company_id:str,cutoff_at:datetime,raw_features:list[dict[str,Any]],receipts_before:int|None)->dict[str,Any]:
        receipts=getattr(self.features,"retrieval_receipts",None); receipt=getattr(self.features,"last_retrieval_receipt",None)
        if not isinstance(receipts,list) or receipts_before is None or len(receipts)!=receipts_before+1 or not isinstance(receipt,dict) or receipts[-1] is not receipt:
            raise M3Top3AdmissionError("MISSING_DETERMINISTIC_RETRIEVAL_RECEIPT","feature provider must emit exactly one deterministic receipt per company/cutoff slice",{"company_id":company_id,"cutoff_at":cutoff_at.isoformat()},EXIT_BLOCKED)
        required={"retrieval_receipt_id","company_id","cutoff_at","source_version","source_status","source_hash","source_matching_rows","selected_rows","excluded_rows","exclusions","cutoff_frozen_bundle"}
        if required-set(receipt) or receipt.get("company_id")!=company_id or receipt.get("cutoff_at")!=cutoff_at.isoformat() or receipt.get("source_version")!=getattr(self.features,"source_version",None) or receipt.get("source_status")!=getattr(self.features,"source_status",None):
            raise M3Top3AdmissionError("RETRIEVAL_RECEIPT_RECONCILIATION_FAILED","retrieval receipt identity does not match the consumed slice",{"company_id":company_id},EXIT_BLOCKED)
        source_hash=receipt.get("source_hash")
        counts=(receipt.get("source_matching_rows"),receipt.get("selected_rows"),receipt.get("excluded_rows"))
        exclusions=receipt.get("exclusions")
        valid_hash=isinstance(source_hash,str) and len(source_hash)==64 and all(c in "0123456789abcdef" for c in source_hash.lower())
        valid_counts=all(isinstance(v,int) and not isinstance(v,bool) and v>=0 for v in counts)
        valid_exclusions=isinstance(exclusions,list) and all(isinstance(item,dict) and item.get("row_id") and isinstance(item.get("codes"),list) and item["codes"] for item in exclusions)
        if not valid_hash or not valid_counts or not valid_exclusions or counts[0]!=counts[1]+counts[2] or counts[1]!=len(raw_features) or counts[2]!=len(exclusions):
            raise M3Top3AdmissionError("RETRIEVAL_RECEIPT_RECONCILIATION_FAILED","retrieval receipt counts/hash/exclusions do not reconcile",{"company_id":company_id,"counts":counts,"selected_actual":len(raw_features)},EXIT_BLOCKED)
        payload={k:v for k,v in receipt.items() if k!="retrieval_receipt_id"}
        if receipt.get("retrieval_receipt_id")!=deterministic_id("retrieval",payload):
            raise M3Top3AdmissionError("RETRIEVAL_RECEIPT_RECONCILIATION_FAILED","retrieval receipt ID is not deterministic for its payload",{"company_id":company_id},EXIT_BLOCKED)
        return receipt

    def build(self,snapshot_date:date)->BuiltSnapshot:
        if not self.execution_lineage.get("synthetic_only"):
            reverify_execution_lineage(self.execution_lineage)
        verify_lineage_temporal_compatibility(self.execution_lineage,snapshot_date)
        cutoff_at=snapshot_cutoff(snapshot_date,self.config.cutoff_local_time,self.config.timezone); states=list(self.universe.states_at(snapshot_date)); pit_rows=[]; model_inputs=[]; retrieval_audits=[]; blockers=[]
        universe_lineage=verify_universe_release(self.universe,snapshot_date,states)
        if universe_lineage.get("snapshot_cutoff_at")!=cutoff_at.isoformat():
            raise M3Top3AdmissionError("DENOMINATOR_LINEAGE_MISMATCH","snapshot build cutoff differs from denominator release cutoff",exit_code=EXIT_INTEGRITY)
        verify_price_release(self.price)
        if self.config.price_source_semantics!=self.price.semantics:
            raise M3Top3AdmissionError("PRICE_LINEAGE_MISMATCH","snapshot build config price semantics differs from the admitted provider",{"config":self.config.price_source_semantics,"provider":self.price.semantics},3)
        release_refs=lineage_ref_map(self.execution_lineage)
        feature_lineage=verify_feature_release(self.features) if not self.execution_lineage.get("synthetic_only") else None
        if release_refs["UNIVERSE_RELEASE"]["release_id"]!=self.universe.release_id or release_refs["UNIVERSE_RELEASE"]["release_revision"]!=universe_lineage["universe_release_revision"] or release_refs["UNIVERSE_RELEASE"]["artifact_sha256"]!=universe_lineage["universe_release_hash"] or release_refs["DENOMINATOR_ELIGIBILITY_RELEASE"]["release_id"]!=universe_lineage["denominator_release_id"] or release_refs["DENOMINATOR_ELIGIBILITY_RELEASE"]["release_revision"]!=universe_lineage["denominator_release_revision"] or release_refs["DENOMINATOR_ELIGIBILITY_RELEASE"]["artifact_sha256"]!=universe_lineage["denominator_release_hash"]:
            raise M3Top3AdmissionError("DATASET_REF_IDENTITY_MISMATCH","Universe/denominator providers differ from execution lineage",exit_code=3)
        if feature_lineage is not None and (release_refs["FEATURE_SOURCE_RELEASE"]["release_id"]!=self.features.source_version or release_refs["FEATURE_SOURCE_RELEASE"]["artifact_sha256"]!=self.features.source_hash or release_refs["PRICE_RELEASE"]["release_id"]!=self.price.dataset_id):
            raise M3Top3AdmissionError("DATASET_REF_IDENTITY_MISMATCH","feature/price providers differ from execution lineage",exit_code=3)
        if not self.execution_lineage.get("synthetic_only"):
            operational={release["domain"]:release for release in self.execution_lineage.get("releases",[])}
            provider_components=getattr(self.price,"component_records",None)
            if isinstance(provider_components,list) and provider_components:
                consumed=sorted((row.get("artifact_sha256"),row.get("byte_size")) for row in provider_components)
            else:
                paths=getattr(self.price,"paths",None) or ([getattr(self.price,"path",None)] if getattr(self.price,"path",None) is not None else [])
                try:
                    consumed=sorted((hash_file(Path(path)),Path(path).stat().st_size) for path in paths)
                except OSError as exc:
                    raise M3Top3AdmissionError("PRICE_LINEAGE_MISMATCH","snapshot price/CA/calendar provider bytes are unavailable",exit_code=3) from exc
            for domain in ("PRICE_RELEASE","CORPORATE_ACTION_RELEASE","TRADING_CALENDAR_RELEASE"):
                release=operational.get(domain); registered=sorted((row.get("artifact_sha256"),row.get("byte_size")) for row in (release or {}).get("components",[]))
                if not release or registered!=consumed:
                    code="PRICE_LINEAGE_MISMATCH" if domain=="PRICE_RELEASE" else "OUTCOME_COMPONENT_LINEAGE_MISMATCH"
                    raise M3Top3AdmissionError(code,f"snapshot provider bytes differ from exact {domain}",exit_code=3)
            if getattr(self.price,"component_set_digest",None) is not None and release_refs["PRICE_RELEASE"].get("component_set_digest")!=self.price.component_set_digest:
                raise M3Top3AdmissionError("PRICE_LINEAGE_MISMATCH","snapshot price semantic component identity differs from PRICE_RELEASE",exit_code=3)
        lineage={**universe_lineage,"execution_lineage_bundle_hash":self.execution_lineage["bundle_sha256"],"execution_lineage_bundle_locator":self.execution_lineage.get("bundle_path"),"execution_lineage_identity_hash":self.execution_lineage["lineage_identity_hash"],"lineage_bundle_synthetic_only":self.execution_lineage.get("synthetic_only") is True,"lineage_releases":self.execution_lineage["portable_releases"],"release_ref_map":release_refs,"price_dataset_id":self.price.dataset_id,"price_dataset_hash":self.price.dataset_hash,"price_source_semantics":self.price.semantics,"price_release_status":self.price.release_status}
        for state in sorted(states,key=lambda x:(x.company_id,x.security_code)):
            try:
                p,m,b,audit=self._build_company(state,snapshot_date,cutoff_at,lineage)
            except PITLeakageError as exc:
                blockers.extend(f"{state.company_id}:{v.code}" for v in exc.violations)
                continue
            pit_rows.append(p); model_inputs.append(m); blockers.extend(f"{state.company_id}:{x}" for x in b)
            if audit is not None: retrieval_audits.append(audit)
        if feature_lineage is None:
            feature_lineage=verify_feature_release(self.features)
            if release_refs["FEATURE_SOURCE_RELEASE"]["release_id"]!=self.features.source_version or release_refs["FEATURE_SOURCE_RELEASE"]["artifact_sha256"]!=self.features.source_hash or release_refs["PRICE_RELEASE"]["release_id"]!=self.price.dataset_id:
                raise M3Top3AdmissionError("DATASET_REF_IDENTITY_MISMATCH","feature/price providers differ from execution lineage",exit_code=3)
        lineage.update(feature_lineage)
        lineage.pop("release_ref_map",None)
        entry_hash=aggregate_hash([sha256_hex(p) for p in pit_rows]+[sha256_hex(m) for m in model_inputs]+[sha256_hex(a) for a in retrieval_audits])
        if not states: status="SNAPSHOT_BLOCKED"; blockers.append("NO_UNIVERSE_STATES")
        elif any(not blocker.endswith(":ELIGIBILITY_UNRESOLVED") for blocker in blockers):
            status="SNAPSHOT_BLOCKED"; model_inputs=[]
            entry_hash=aggregate_hash([sha256_hex(p) for p in pit_rows]+[sha256_hex(a) for a in retrieval_audits])
        elif blockers: status="SNAPSHOT_PARTIAL"
        else: status="SNAPSHOT_READY"
        return BuiltSnapshot(snapshot_date,cutoff_at,entry_hash,pit_rows,model_inputs,retrieval_audits,status,sorted(set(blockers)),lineage)


class SnapshotStore:
    def __init__(self,root:str|Path): self.root=Path(root)
    def _dir(self,d:date)->Path: return self.root/d.isoformat()
    def valid_existing(self,built:BuiltSnapshot)->bool:
        p=self._dir(built.snapshot_date)/"manifest.json"
        if not p.exists(): return False
        verified=verify_snapshot_artifacts(p.parent)
        if verified.manifest.get("snapshot_content_hash") != built.snapshot_set_entry_hash:
            raise M3Top3AdmissionError("IMMUTABLE_SNAPSHOT_COLLISION","existing snapshot identity has different semantic content",{"snapshot_date":built.snapshot_date.isoformat()},3)
        return True
    def write(self,built:BuiltSnapshot,metadata:dict[str,Any])->dict[str,Any]:
        if built.status != "SNAPSHOT_READY" or built.blockers:
            raise M3Top3AdmissionError("BLOCKED_MANIFEST_STATE_CONTRADICTION_OR_BLOCKED_SNAPSHOT_NOT_READY","only READY snapshots with zero blockers may enter the scoreable store",{"snapshot_status":built.status,"blockers":built.blockers},EXIT_BLOCKED)
        d=self._dir(built.snapshot_date)
        pit_text="".join(json.dumps(r,ensure_ascii=False,sort_keys=True,separators=(",",":"))+"\n" for r in built.pit_rows); mi_text="".join(json.dumps(r,ensure_ascii=False,sort_keys=True,separators=(",",":"))+"\n" for r in built.model_inputs); audit_text="".join(json.dumps(r,ensure_ascii=False,sort_keys=True,separators=(",",":"))+"\n" for r in built.retrieval_audits)
        first_pit=built.pit_rows[0] if built.pit_rows else {}
        first_model=built.model_inputs[0] if built.model_inputs else {}
        first_audit=built.retrieval_audits[0] if built.retrieval_audits else {}
        dataset_refs=first_pit.get("dataset_refs") if isinstance(first_pit.get("dataset_refs"),list) else []
        price_ref=next((ref for ref in dataset_refs if isinstance(ref,dict) and ref.get("domain")=="PRICE_RELEASE"),{})
        manifest={**metadata,**built.lineage,"generator_version":first_pit.get("generator_version"),"universe_release_id":first_pit.get("universe_release_id"),"feature_source_version":first_audit.get("source_version"),"feature_source_hash":first_audit.get("source_hash"),"feature_source_status":first_audit.get("source_status"),"price_dataset_id":first_model.get("price_dataset_id"),"price_dataset_hash":first_model.get("price_dataset_hash") or price_ref.get("artifact_sha256"),"price_source_semantics":first_model.get("price_source_semantics"),"price_release_status":first_model.get("price_release_status"),"reconstruction_version":first_model.get("reconstruction_version"),"snapshot_date":built.snapshot_date.isoformat(),"snapshot_cutoff_at":built.cutoff_at.isoformat(),"snapshot_revision":first_pit.get("snapshot_revision",0),"snapshot_content_hash":built.snapshot_set_entry_hash,"snapshot_status":built.status,"blockers":built.blockers,"pit_row_count":len(built.pit_rows),"model_input_row_count":len(built.model_inputs),"retrieval_audit_row_count":len(built.retrieval_audits),"pit_file_sha256":sha256_hex(pit_text),"model_input_file_sha256":sha256_hex(mi_text),"retrieval_audit_file_sha256":sha256_hex(audit_text),"retrieval_audit_content_hash":aggregate_hash([sha256_hex(a) for a in built.retrieval_audits]),"retrieval_receipt_ids":sorted(a["retrieval_receipt_id"] for a in built.retrieval_audits),"retrieval_source_hashes":sorted({a["source_hash"] for a in built.retrieval_audits})}
        manifest["snapshot_manifest_identity_hash"]=sha256_hex(_snapshot_manifest_identity_payload(manifest))
        targets=(d/"pit_snapshot.jsonl",d/"model_input.jsonl",d/"retrieval_audit.jsonl",d/"manifest.json")
        if any(path.exists() for path in targets):
            if not all(path.exists() for path in targets):
                raise M3Top3AdmissionError("IMMUTABLE_SNAPSHOT_COLLISION","incomplete existing snapshot identity cannot be overwritten",{"snapshot_date":built.snapshot_date.isoformat()},3)
            verified=verify_snapshot_artifacts(d)
            prior_manifest=verified.manifest
            if prior_manifest.get("snapshot_content_hash") != built.snapshot_set_entry_hash or (d/"pit_snapshot.jsonl").read_text(encoding="utf-8") != pit_text or (d/"model_input.jsonl").read_text(encoding="utf-8") != mi_text or (d/"retrieval_audit.jsonl").read_text(encoding="utf-8") != audit_text:
                raise M3Top3AdmissionError("IMMUTABLE_SNAPSHOT_COLLISION","existing snapshot identity has different bytes",{"snapshot_date":built.snapshot_date.isoformat()},3)
            return prior_manifest
        d.parent.mkdir(parents=True,exist_ok=True)
        staging=d.with_name(f".{d.name}.{built.snapshot_set_entry_hash[:12]}.staging")
        if staging.exists():
            raise M3Top3AdmissionError("IMMUTABLE_SNAPSHOT_COLLISION","stale create-only snapshot staging identity exists",{"path":str(staging)},3)
        try:
            staging.mkdir(exist_ok=False)
        except OSError as exc:
            raise M3Top3AdmissionError("IMMUTABLE_SNAPSHOT_COLLISION","snapshot staging identity appeared during create-only admission",{"path":str(staging)},3) from exc
        atomic_write_text(staging/"pit_snapshot.jsonl",pit_text)
        atomic_write_text(staging/"model_input.jsonl",mi_text)
        atomic_write_text(staging/"retrieval_audit.jsonl",audit_text)
        atomic_write_json(staging/"manifest.json",manifest)
        try:
            verify_snapshot_artifacts(staging,allow_staging=True)
        except M3Top3AdmissionError:
            raise
        try:
            d.mkdir(exist_ok=False)
        except OSError as exc:
            raise M3Top3AdmissionError("IMMUTABLE_SNAPSHOT_COLLISION","snapshot target appeared before create-only publish",{"snapshot_date":built.snapshot_date.isoformat(),"staging":str(staging)},3) from exc
        publish_order=("pit_snapshot.jsonl","model_input.jsonl","retrieval_audit.jsonl","manifest.json")
        try:
            for name in publish_order:
                os.link(staging/name,d/name)
        except OSError as exc:
            raise M3Top3AdmissionError("IMMUTABLE_SNAPSHOT_COLLISION","snapshot no-replace publish failed; incomplete canonical directory is quarantined by missing/last manifest",{"snapshot_date":built.snapshot_date.isoformat(),"staging":str(staging),"published_manifest":(d/"manifest.json").exists()},3) from exc
        for name in publish_order: (staging/name).unlink()
        staging.rmdir()
        return manifest


@dataclass
class BatchResult:
    requested:int; generated:int; failed:int; reused:int; failed_dates:list[str]; manifests:list[dict[str,Any]]
    blocked:int=0; blocked_dates:list[str]=field(default_factory=list); failed_integrity:int=0; failed_authority:int=0
    @property
    def accounting_pass(self)->bool: return self.requested==self.generated+self.failed+self.reused+self.blocked


class BatchSnapshotGenerator:
    def __init__(self,builder:SnapshotBuilder,store:SnapshotStore,retries:int=1): self.builder=builder; self.store=store; self.retries=max(0,retries)
    def run(self,start:date,end:date,metadata:dict[str,Any])->BatchResult:
        dates=self.builder.price.trading_dates(start,end); generated=failed=reused=blocked=failed_integrity=failed_authority=0; failed_dates=[]; blocked_dates=[]; manifests=[]
        for d in dates:
            last_error=None
            for _ in range(self.retries+1):
                try:
                    built=self.builder.build(d)
                    if built.status != "SNAPSHOT_READY" or built.blockers:
                        blocked+=1; blocked_dates.append(f"{d.isoformat()}:{built.status}:{','.join(built.blockers)}"); break
                    if self.store.valid_existing(built): reused+=1; break
                    manifests.append(self.store.write(built,metadata)); generated+=1; break
                except PITLeakageError as exc:
                    blocked+=1; blocked_dates.append(f"{d.isoformat()}:PIT:{','.join(v.code for v in exc.violations)}"); break
                except M3Top3AdmissionError as exc:
                    if exc.exit_code==EXIT_BLOCKED:
                        blocked+=1; blocked_dates.append(f"{d.isoformat()}:{exc.code}:{exc}")
                    else:
                        failed+=1; failed_dates.append(f"{d.isoformat()}:{exc.code}:{exc}")
                        if exc.exit_code==3: failed_integrity+=1
                        if exc.exit_code==4: failed_authority+=1
                    break
                except Exception as exc: last_error=exc
            else:
                failed+=1; failed_dates.append(f"{d.isoformat()}:{type(last_error).__name__}:{last_error}")
        return BatchResult(len(dates),generated,failed,reused,failed_dates,manifests,blocked,blocked_dates,failed_integrity,failed_authority)
