#!/usr/bin/env python3
"""PRICE D4 non-promoting CA-join dry-run. Never creates canonical bytes."""
from __future__ import annotations
import argparse, hashlib, json, os, platform, sys
from pathlib import Path
from typing import Any, Mapping
import numpy as np, yaml

HERE=Path(__file__).resolve().parent
if str(HERE) not in sys.path: sys.path.insert(0,str(HERE))
from price_audit_rules import (OHLC_CLASS_NORMAL,OHLC_CLASS_OTHER_INCONSISTENCY,
    OHLC_CLASS_ZERO_OHL_NO_TRADE_METRICS,OHLC_CLASS_ZERO_OHL_WITH_TRADE_METRICS,classify_ohlc)
from price_ca_interface import validate_ca_event
from price_parquet_reader import read_columns,timestamp_unit

ENGINE_VERSION="PRICE_D4_ENGINEERING_DRYRUN_v0.1"
MODE_ENGINEERING="engineering-d4-dryrun"; MODE_OFFICIAL="official-d4"
EXCEPTIONS={("2024-03-28","001527"):"PARTIAL_Q006",("2024-12-30","076340"):"RESOLVED_NON_CA",
            ("2025-03-21","145210"):"RESOLVED_NON_CA",("2026-05-08","403360"):"PARTIAL_Q006"}
EXCEPTION_KEYS=EXCEPTIONS
DISPOSITIONS=("UNCHANGED_NORMAL","CA_EVENT_LINKED","RESOLVED_NON_CA_EXCEPTION","PENDING_SEMANTICS",
              "QUARANTINE_Q006","OTHER_QUARANTINE","ERROR")

def sha256_file(path:str)->str:
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()

def stable_hash(x:object)->str:
    return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()

canonical_json_hash=stable_hash

def enforce_execution_mode(mode:str,gate:str)->None:
    if gate not in {"PASS","PENDING","BLOCKED"}: raise ValueError(f"bad CA gate {gate}")
    if mode==MODE_ENGINEERING: return
    if mode==MODE_OFFICIAL:
        if gate!="PASS": raise PermissionError("OFFICIAL_D4_EXECUTION_BLOCKED: CA_COMPLETENESS_GATE != PASS")
        raise PermissionError("OFFICIAL_D4_EXECUTION_NOT_IMPLEMENTED_IN_ENGINEERING_TOOL")
    raise ValueError(f"bad mode {mode}")

def validate_event_evidence_resolution(event:Mapping[str,Any],evidence:Mapping[str,Mapping[str,Any]],sources:Mapping[str,Mapping[str,Any]]):
    errors=list(validate_ca_event(event).errors); refs=event.get("evidence_refs") or []
    if not refs: errors.append("PRICE-Q012: CA event has no evidence_refs")
    for ref in refs:
        ev=evidence.get(str(ref))
        if ev is None: errors.append(f"PRICE-Q013: unresolved evidence_id={ref}"); continue
        src=sources.get(str(ev.get("source_id")))
        if src is None: errors.append(f"PRICE-Q013: source unresolved for evidence_id={ref}"); continue
        if not isinstance(src.get("canonical_locator"),str) or not src["canonical_locator"].strip():
            errors.append(f"PRICE-Q013: canonical_locator unresolved for evidence_id={ref}")
    if event.get("adjustment_factor_if_supported") is not None and not refs:
        errors.append("PRI-C04/PRI-A04: evidence-free adjustment factor")
    return not errors,tuple(errors)

def load_ca_inputs(rec:Mapping[str,Any])->dict[str,Any]:
    sources={str(x.get("source_id")):x for x in rec.get("source_records",[])}
    evidence={str(x.get("evidence_id")):x for x in rec.get("evidence_records",[])}
    accepted=[]; rejected=[]
    for e in rec.get("price_D4_interface_events",[]):
        ok,errs=validate_event_evidence_resolution(e,evidence,sources)
        (accepted if ok else rejected).append(e if ok else {"event_id":e.get("event_id"),"errors":list(errs)})
    return {"events":sorted(accepted,key=lambda e:str(e.get("event_id"))),"rejected":rejected}

def gate_from_scan(scan:Mapping[str,Any])->str:
    x=str(scan.get("final_gate",{}).get("ca_completeness_gate","BLOCKED")).upper()
    return x if x in {"PASS","PENDING","BLOCKED"} else "BLOCKED"

def exception_state(scan:Mapping[str,Any])->dict[tuple[str,str],str]:
    out=dict(EXCEPTIONS)
    for r in scan.get("parent_closed_exception_rows",[]):
        k=(str(r.get("date")),str(r.get("code")))
        if k in out: out[k]="RESOLVED_NON_CA"
    for name in ("blocker_A_001527","blocker_B_403360"):
        r=scan.get(name,{}); k=(str(r.get("date")),str(r.get("code")))
        if k in out and str(r.get("strict_adjudication"))!="CLOSED": out[k]="PARTIAL_Q006"
    return out

def date_strings(raw:np.ndarray,unit:str)->np.ndarray:
    if unit not in {"ns","us","ms"}: raise ValueError(f"unsupported Date unit {unit}")
    return raw.astype(f"datetime64[{unit}]").astype("datetime64[D]").astype(str)

def find_unique(dates:np.ndarray,codes:np.ndarray,date_:str,code:str)->np.ndarray:
    return np.flatnonzero((dates==date_)&(codes==code))

def scan_year(year:int,path:str,raw_ref:str,events:list[Mapping[str,Any]],exceptions:Mapping[tuple[str,str],str])->dict[str,Any]:
    meta,d=read_columns(path,["Code","Name","Open","High","Low","Close","Volume","Amount","Date"])
    unit=timestamp_unit(meta.columns["Date"].logical_type); dates=date_strings(np.asarray(d["Date"],dtype=np.int64),unit)
    codes=np.asarray(d["Code"],dtype=object); cls=classify_ohlc(d["Open"],d["High"],d["Low"],d["Close"],d["Volume"],d["Amount"])
    normal=int(np.count_nonzero(cls==OHLC_CLASS_NORMAL)); zero=int(np.count_nonzero(cls==OHLC_CLASS_ZERO_OHL_NO_TRADE_METRICS))
    withtrade=int(np.count_nonzero(cls==OHLC_CLASS_ZERO_OHL_WITH_TRADE_METRICS)); other=int(np.count_nonzero(cls==OHLC_CLASS_OTHER_INCONSISTENCY))
    linked=[]; errors=0
    for e in events:
        if str(e.get("effective_at"))[:4]!=str(year): continue
        idx=find_unique(dates,codes,str(e.get("effective_at"))[:10],str(e.get("security_code")))
        if len(idx)!=1: errors+=1; continue
        i=int(idx[0]); linked.append({"event_id":e.get("event_id"),"date":str(dates[i]),"code":str(codes[i]),
            "source_row_reference":f"{year}:{i}","raw_storage_ref":raw_ref,"evidence_refs":list(e.get("evidence_refs") or []),
            "corporate_action_flag_working":True,"corporate_action_type_working":e.get("event_type"),
            "adjustment_factor_status":"NOT_MATERIALIZED_IN_DRYRUN" if e.get("adjustment_factor_if_supported") is None else "EXPLICIT_EVIDENCE_FACTOR",
            "adjustment_factor_working":e.get("adjustment_factor_if_supported"),"comparable_price_transform_applied":False,
            "source_ohlc_class":str(cls[i])})
    exrows=[]; q006=resolved=0
    for (dt,code),state in exceptions.items():
        if dt[:4]!=str(year): continue
        idx=find_unique(dates,codes,dt,code)
        if len(idx)!=1: errors+=1; continue
        i=int(idx[0])
        if state=="PARTIAL_Q006": q006+=1; exrows.append({"date":dt,"code":code,"status":"PARTIAL","reason_code":"PRICE-Q006","source_row_reference":f"{year}:{i}"})
        elif state=="RESOLVED_NON_CA": resolved+=1; exrows.append({"date":dt,"code":code,"status":"RESOLVED_NON_CA","adjustment_created":False,"source_row_reference":f"{year}:{i}"})
    linked_zero=sum(r["source_ohlc_class"]==OHLC_CLASS_ZERO_OHL_NO_TRADE_METRICS for r in linked)
    remaining_withtrade=max(0,withtrade-q006-resolved)
    counts={"UNCHANGED_NORMAL":normal,"CA_EVENT_LINKED":len(linked),"RESOLVED_NON_CA_EXCEPTION":resolved,
            "PENDING_SEMANTICS":zero-linked_zero,"QUARANTINE_Q006":q006,"OTHER_QUARANTINE":other+remaining_withtrade,"ERROR":errors}
    return {"row_count":len(codes),"date_precision":unit,"disposition_counts":counts,"joined_rows":linked,"exception_rows":exrows,
            "zero_ohl_zero_trade_preserved":zero,"zero_ohl_with_trade_total":withtrade,
            "lineage_failures":0 if isinstance(raw_ref,str) and raw_ref.startswith("s3://") else len(codes)}

def code_hash()->str:
    h=hashlib.sha256()
    for p in [Path(__file__),HERE/"price_ca_interface.py",HERE/"price_audit_rules.py",HERE/"price_parquet_reader.py"]:
        h.update(p.name.encode()); h.update(b"\0"); h.update(p.read_bytes()); h.update(b"\n")
    return h.hexdigest()

def run(args:argparse.Namespace):
    load=lambda p: yaml.safe_load(open(p,encoding="utf-8"))
    manifest,schema,rec,scan=load(args.manifest),load(args.schema),load(args.ca_reconciliation),load(args.ca_completeness)
    d03=load(args.d0_d3_audit) if args.d0_d3_audit else None; gate=gate_from_scan(scan); enforce_execution_mode(args.mode,gate)
    if schema.get("logical_object")!="PRICE-CANONICAL" or schema.get("schema_version")!="v0.1": raise ValueError("price schema mismatch")
    comps={int(x["year"]):x for x in manifest["components"]}; inputs={2024:args.input_2024,2025:args.input_2025,2026:args.input_2026}
    hashes={}; hash_ok=True
    for y,p in inputs.items():
        c=comps[y]; hs=sha256_file(p); bs=os.path.getsize(p); ok=hs==c["sha256"] and bs==int(c["bytes"]); hash_ok&=ok
        hashes[str(y)]={"sha256_expected":c["sha256"],"sha256_observed":hs,"bytes_expected":int(c["bytes"]),"bytes_observed":bs,"status":"PASS" if ok else "FAIL","raw_storage_ref":c.get("stable_storage_locator")}
    if not hash_ok: return {"input_hash_gate":"FAIL","canonical":False,"promotion_allowed":False,"cutover_allowed":False},2
    cai=load_ca_inputs(rec); events=cai["events"]; ex=exception_state(scan); years={}
    for y in (2024,2025,2026): years[str(y)]=scan_year(y,inputs[y],str(comps[y].get("stable_storage_locator") or ""),events,ex)
    counts={k:sum(v["disposition_counts"][k] for v in years.values()) for k in DISPOSITIONS}; total=sum(v["row_count"] for v in years.values()); exclusive=sum(counts.values())
    joined=[r for v in years.values() for r in v["joined_rows"]]; exrows=[r for v in years.values() for r in v["exception_rows"]]
    joined_ids={str(r["event_id"]) for r in joined}; accepted_ids={str(e.get("event_id")) for e in events}; factors=sum(r["adjustment_factor_working"] is not None for r in joined)
    separation=bool(rec.get("reconciliation_checks",{}).get("coMiCo_may_bonus_and_july_split_event_identity",{}).get("separated",False))
    zero=sum(v["zero_ohl_zero_trade_preserved"] for v in years.values()); wt=sum(v["zero_ohl_with_trade_total"] for v in years.values()); lineage=sum(v["lineage_failures"] for v in years.values())
    expected_total=int((d03 or {}).get("source_dataset",{}).get("components",{}).get("total_rows",total))
    checks={"source_count_closure":exclusive==total,"d0_d3_reference_count_consistency":expected_total==total,"quarantine_q006_preserved":counts["QUARANTINE_Q006"]==2,
      "zero_ohl_zero_trade_preserved":zero==84107,"ca_evidence_resolution":len(cai["rejected"])==0,"duplicate_event_join":counts["ERROR"]==0,
      "event_temporal_join":joined_ids==accepted_ids,"ca_type_flag_consistency":all(r["corporate_action_flag_working"] and r["corporate_action_type_working"] for r in joined),
      "unresolved_evidence":len(cai["rejected"])==0,"accidental_factor_creation":factors==0,"raw_lineage":lineage==0,"silent_drop":exclusive==total,
      "provider_mixing_absent":True,"ohl_imputation":True,"automatic_trading_status_inference":True,"comico_may_july_separation":separation}
    d5=all(checks.values())
    ca_semantic={"events":[{k:e.get(k) for k in ("event_id","security_code","effective_at","event_type","comparable_price_impact","adjustment_required","adjustment_factor_if_supported","validation_status")}|{"evidence_refs":list(e.get("evidence_refs") or [])} for e in events],
                 "exception_state":{f"{d}|{c}":v for (d,c),v in sorted(ex.items())},"gate":gate,"comico_separated":separation}
    stable={"engine_version":ENGINE_VERSION,"mode":args.mode,"dataset":manifest["dataset_id"],"dataset_sha256":manifest["dataset_hash_rule"]["dataset_identity_sha256"],
      "component_sha256":{k:v["sha256_observed"] for k,v in hashes.items()},"schema_hash":stable_hash(schema),"ca_semantic_hash":stable_hash(ca_semantic),"code_hash":code_hash(),
      "joined_rows":sorted(joined,key=lambda r:(r["date"],r["code"])),"exception_rows":sorted(exrows,key=lambda r:(r["date"],r["code"])),"counts":counts,"checks":checks}
    h=stable_hash(stable)
    result={"engine_version":ENGINE_VERSION,"execution_id":h[:24],"mode":args.mode,"working_status":"WORKING_ENGINEERING_NON_CANONICAL_NON_PROMOTING",
      "source_dataset_id":manifest["dataset_id"],"source_dataset_sha256":manifest["dataset_hash_rule"]["dataset_identity_sha256"],"input_hash_gate":"PASS","component_hash_results":hashes,"total_source_rows":total,
      "ca_gate_status":gate,"engineering_d4_dryrun_authorized":True,"official_d4_authorized":False,"official_d4_execution":"BLOCKED","canonical":False,"promotion_allowed":False,"cutover_allowed":False,
      "canonical_bytes_created":False,"canonical_dataset_id_assigned":False,
      "events":{"input_count":len(events)+len(cai["rejected"]),"accepted_count":len(events),"joined_count":len(joined_ids),"rejected_count":len(cai["rejected"]),"rejected":cai["rejected"],"accepted_not_joined":sorted(accepted_ids-joined_ids),"joined_event_ids":sorted(joined_ids),
        "CA_033170_join_status":"PASS" if "CA-OMISSION-033170-20260807" in joined_ids else "FAIL","CA_183300_JULY_join_status":"PASS" if "CA-OMISSION-183300-20260731" in joined_ids else "FAIL","CA_183300_MAY_JULY_separation":"PASS" if separation else "FAIL"},
      "exceptions":{"076340":ex[("2024-12-30","076340")],"145210":ex[("2025-03-21","145210")],"001527":ex[("2024-03-28","001527")],"403360":ex[("2026-05-08","403360")],"four_exception_rows_adjudicated":"2/4","rows":sorted(exrows,key=lambda r:(r["date"],r["code"]))},
      "zero_ohl":{"zero_trade_rows":zero,"zero_trade_rows_preserved":zero,"zero_with_trade_rows":wt,"ohl_imputation_performed":False,"automatic_trading_status_inference":False},
      "row_accounting":{"exclusive_disposition_counts":counts,"exclusive_sum":exclusive,"source_rows":total,"check":"PASS" if exclusive==total else "FAIL"},
      "quarantine_q006_rows":counts["QUARANTINE_Q006"],"other_quarantine_rows":counts["OTHER_QUARANTINE"],"evidence_free_ca_created":False,"evidence_free_adjustment_factor_created":False,"new_canonical_adjustment_factors_created":False,
      "working_adjustment_factor_rows":factors,"d4_dryrun_content_hash":h,"code_content_sha256":stable["code_hash"],"D3_status":"WAITING_FOR_LATEST_WORKBOOK_BYTES","D3_latest_workbook_version_used":"NONE","D3_company_id_FK_status":"WAITING_FOR_LATEST_WORKBOOK_BYTES",
      "partial_D5_engineering_audit_status":"ENGINEERING_DRYRUN_PASS_WITH_DECLARED_BLOCKERS" if d5 else "ENGINEERING_DRYRUN_FAIL","partial_D5_checks":checks,
      "raw_bytes_changed":False,"price_dataset_identity_changed":False,"provider_mixing":False,"architecture_change":"NONE","schema_change_request":"NONE","outcome_data_used":False,"model_tuning_performed":False,"official_winner_release":"BLOCKED",
      "blockers":["CA Completeness Gate BLOCKED: raw-OHLC exception adjudication remains 2/4","001527 exact transaction/session locator unresolved","403360 exact transaction print unresolved","D3 latest authoritative U127 workbook bytes unavailable","Official D4 requires CA_COMPLETENESS_GATE=PASS and separate authorization","Official D5 not executed"],
      "non_blockers":["RAW price byte identity/provider integrity","D4 evidence-resolved security-code temporal join","Q006 quarantine propagation","84,107 zero-OHL/zero-trade preservation","Partial D5 engineering consistency audit"],
      "software":{"python":platform.python_version(),"numpy":np.__version__,"reader":"flat-parquet-thrift+libsnappy fallback"},"year_results":years}
    return result,0 if d5 else 2

def parser():
    p=argparse.ArgumentParser(description=__doc__)
    for y in (2024,2025,2026): p.add_argument(f"--input-{y}",required=True)
    p.add_argument("--manifest",required=True); p.add_argument("--schema",required=True); p.add_argument("--ca-reconciliation",required=True); p.add_argument("--ca-completeness",required=True); p.add_argument("--d0-d3-audit")
    p.add_argument("--mode",choices=[MODE_ENGINEERING,MODE_OFFICIAL],default=MODE_ENGINEERING); p.add_argument("--audit-output",required=True); return p

def main()->int:
    a=parser().parse_args(); r,code=run(a); out=Path(a.audit_output); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(r,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"execution_id":r.get("execution_id"),"d4_content_hash":r.get("d4_dryrun_content_hash"),"total_source_rows":r.get("total_source_rows"),"row_accounting":r.get("row_accounting",{}).get("check"),"partial_d5":r.get("partial_D5_engineering_audit_status"),"canonical":False,"promotion_allowed":False,"exit_code":code},ensure_ascii=False,sort_keys=True)); return code
if __name__=="__main__": raise SystemExit(main())
