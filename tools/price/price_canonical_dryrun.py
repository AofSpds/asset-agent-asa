#!/usr/bin/env python3
"""PRICE-CANONICAL v0.1 D0-D3 deterministic dry-run audit engine.

Reads verified RAW Parquet, emits machine-readable audit/issue records, and stops
before D4 when CA completeness is not closed. It never mutates RAW bytes, creates
canonical bytes, or assigns a released price_dataset_id.
"""
from __future__ import annotations

import argparse, csv, hashlib, json, os, platform, re, subprocess, sys
from datetime import date, datetime
from pathlib import Path
from typing import Any, Mapping
from zoneinfo import ZoneInfo
import numpy as np
import yaml

SCRIPT_DIR=Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path: sys.path.insert(0,str(SCRIPT_DIR))
from price_audit_rules import (OHLC_CLASS_NORMAL,OHLC_CLASS_OTHER_INCONSISTENCY,OHLC_CLASS_ZERO_OHL_NO_TRADE_METRICS,OHLC_CLASS_ZERO_OHL_WITH_TRADE_METRICS,PRICE_REASON_CODES,canonical_row_accounting,classify_ohlc,code_lexical_failures,numeric_audit,validate_company_map)
from price_parquet_reader import physical_type_name,read_columns,timestamp_unit

ENGINE_VERSION="PRICE_ENGINEERING_DRYRUN_v0.1"
EXPECTED_RAW_COLUMNS=["Code","Name","Close","Dept","ChangeCode","Changes","ChangesRatio","Volume","Amount","Open","High","Low","Marcap","Stocks","Market","MarketId","Rank","Date"]
READ_COLUMNS=["Code","Name","Close","Volume","Amount","Open","High","Low","Marcap","Stocks","Market","Date"]
NUMERIC_DECIMAL_FIELDS=["Open","High","Low","Close","Amount","Marcap"]
NUMERIC_CHECK_FIELDS=["Open","High","Low","Close","Volume","Amount","Marcap"]


def sha256_file(path:str)->str:
    d=hashlib.sha256()
    with open(path,"rb") as h:
        for chunk in iter(lambda:h.read(1024*1024),b""): d.update(chunk)
    return d.hexdigest()

def _git_commit()->str:
    if os.getenv("SEMI_SCRIPT_COMMIT"): return os.environ["SEMI_SCRIPT_COMMIT"]
    try: return subprocess.check_output(["git","rev-parse","HEAD"],cwd=SCRIPT_DIR,text=True,stderr=subprocess.DEVNULL).strip()
    except Exception: return "NOT_AVAILABLE_RUNTIME"

def _package_version(name:str)->str:
    try:
        m=__import__(name); return str(getattr(m,"__version__","UNKNOWN"))
    except Exception: return "NOT_INSTALLED"

def _manifest_components(manifest:Mapping[str,Any])->dict[int,Mapping[str,Any]]:
    return {int(item["year"]):item for item in manifest["components"]}

def _date_days(raw:np.ndarray,unit:str)->np.ndarray:
    if unit not in {"ns","us","ms"}: raise ValueError(f"unsupported Date timestamp unit {unit!r}")
    return raw.astype(f"datetime64[{unit}]").astype("datetime64[D]").astype(np.int64)

def _day_string(day_value:int)->str:
    return np.datetime_as_string(np.datetime64(int(day_value),"D"),unit="D")

def _null_mask(values:np.ndarray)->np.ndarray:
    a=np.asarray(values)
    if a.dtype.kind=="f": return np.isnan(a)
    if a.dtype.kind in "iu": return np.zeros(a.shape,dtype=bool)
    return np.fromiter((x is None for x in a.tolist()),dtype=bool,count=len(a))

def _lexical_failure_mask(codes:np.ndarray)->np.ndarray:
    rx=re.compile(r"^[0-9A-Z]{6}$")
    return np.fromiter((x is not None and (not isinstance(x,str) or rx.fullmatch(x) is None) for x in codes.tolist()),dtype=bool,count=len(codes))

def _duplicate_mask(date_days:np.ndarray,codes:np.ndarray)->np.ndarray:
    keys=np.char.add(np.char.add(date_days.astype(str),"|"),codes.astype(str)); _,inverse,counts=np.unique(keys,return_inverse=True,return_counts=True); return counts[inverse]>1


def _load_company_map(path:str|None,sheet:str|None=None)->tuple[list[dict[str,Any]],str]:
    if not path: return [],"NONE"
    suffix=Path(path).suffix.lower(); records=[]
    if suffix==".csv":
        with open(path,newline="",encoding="utf-8-sig") as h: rows=list(csv.DictReader(h))
        for row in rows:
            records.append({"code":(row.get("code") or row.get("KRX Code") or row.get("krx_code") or "").strip(),"company_id":(row.get("company_id") or row.get("Company ID") or "").strip(),"listing_date":(row.get("listing_date") or row.get("Listing Date") or "").strip() or None})
        return records,Path(path).name
    if suffix in (".yaml",".yml",".json"):
        with open(path,"r",encoding="utf-8") as h: payload=json.load(h) if suffix==".json" else yaml.safe_load(h)
        rows=payload if isinstance(payload,list) else payload.get("records",payload.get("companies",[]))
        for row in rows: records.append({"code":str(row.get("code",row.get("krx_code",""))).strip(),"company_id":str(row.get("company_id","")).strip(),"listing_date":row.get("listing_date")})
        return records,Path(path).name
    if suffix==".xlsx":
        try: from openpyxl import load_workbook
        except Exception as exc: raise RuntimeError(".xlsx company map requires openpyxl") from exc
        wb=load_workbook(path,read_only=True,data_only=True); ws=wb[sheet] if sheet else (wb["Identity_Ledger"] if "Identity_Ledger" in wb.sheetnames else wb[wb.sheetnames[0]])
        aliases={"code":{"code","krx code","krx_code","종목코드","security_code"},"company_id":{"company_id","company id","companyid","기업id","기업 id"},"listing_date":{"listing_date","listing date","상장일","listingdate"}}
        header_row=None; colmap={}
        for ridx,row in enumerate(ws.iter_rows(min_row=1,max_row=40,values_only=True),start=1):
            normalized=[str(x).strip().lower() if x is not None else "" for x in row]; found={}
            for target,names in aliases.items():
                for cidx,value in enumerate(normalized):
                    if value in names: found[target]=cidx; break
            if "code" in found and "company_id" in found: header_row=ridx; colmap=found; break
        if header_row is None: raise ValueError("could not locate code/company_id headers in workbook")
        for row in ws.iter_rows(min_row=header_row+1,values_only=True):
            code=row[colmap["code"]] if colmap["code"]<len(row) else None; company_id=row[colmap["company_id"]] if colmap["company_id"]<len(row) else None
            if code is None and company_id is None: continue
            listing=row[colmap["listing_date"]] if "listing_date" in colmap and colmap["listing_date"]<len(row) else None
            if isinstance(listing,(datetime,date)): listing=listing.date().isoformat() if isinstance(listing,datetime) else listing.isoformat()
            records.append({"code":str(code).strip() if code is not None else "","company_id":str(company_id).strip() if company_id is not None else "","listing_date":str(listing).strip() if listing not in (None,"") else None})
        return records,Path(path).name
    raise ValueError(f"unsupported company-map format {suffix}")

def _company_map_index(records:list[dict[str,Any]]):
    company={}; listing_days={}
    for r in records:
        company[r["code"]]=r["company_id"]
        if r.get("listing_date"):
            try: listing_days[r["code"]]=int(np.datetime64(str(r["listing_date"])[:10],"D").astype(np.int64))
            except Exception: pass
    return company,listing_days


def _write_issue_rows(handle,*,year:int,data:Mapping[str,np.ndarray],date_days:np.ndarray,classes:np.ndarray,pending_mask:np.ndarray,quarantine_mask:np.ndarray,reason_masks:Mapping[str,np.ndarray])->None:
    if handle is None: return
    for idx in np.flatnonzero(pending_mask|quarantine_mask).tolist():
        row={"source_year":year,"source_row_reference":f"{year}:{idx}","date":_day_string(int(date_days[idx])),"code":data["Code"][idx],"name":data["Name"][idx],"audit_stage":"D2","disposition":"CLASSIFIED_PENDING_SEMANTICS" if pending_mask[idx] else "QUARANTINE","ohlc_class":classes[idx],"reason_codes":[code for code,mask in reason_masks.items() if bool(mask[idx])],"raw":{"Open":float(data["Open"][idx]),"High":float(data["High"][idx]),"Low":float(data["Low"][idx]),"Close":float(data["Close"][idx]),"Volume":float(data["Volume"][idx]),"Amount":float(data["Amount"][idx])}}
        handle.write(json.dumps(row,ensure_ascii=False,separators=(",",":"))+"\n")


def run(args:argparse.Namespace):
    with open(args.manifest,"r",encoding="utf-8") as h: manifest=yaml.safe_load(h)
    with open(args.schema,"r",encoding="utf-8") as h: schema=yaml.safe_load(h)
    dataset_id=manifest["dataset_id"]; dataset_sha=manifest["dataset_hash_rule"]["dataset_identity_sha256"]; components=_manifest_components(manifest)
    inputs={2024:args.input_2024,2025:args.input_2025,2026:args.input_2026}; component_results={}; input_hash_gate=True
    for year,path in inputs.items():
        expected=components[year]; observed_hash=sha256_file(path); observed_bytes=os.path.getsize(path); ok=observed_hash==expected["sha256"] and observed_bytes==int(expected["bytes"]); input_hash_gate &= ok
        component_results[str(year)]={"filename":Path(path).name,"bytes_expected":int(expected["bytes"]),"bytes_observed":observed_bytes,"sha256_expected":expected["sha256"],"sha256_observed":observed_hash,"status":"PASS" if ok else "FAIL","raw_storage_ref":expected.get("stable_storage_locator")}
    if not input_hash_gate: return {"execution_id":"HASH_GATE_FAILURE","source_dataset_id":dataset_id,"source_dataset_sha256":dataset_sha,"component_hash_results":component_results,"input_hash_gate":"FAIL","canonical_promotion_allowed":False,"blocker_list":["INPUT_HASH_GATE_FAILED"]},2
    schema_field_names=[f["name"] for f in schema.get("fields",[])]
    if schema.get("logical_object")!="PRICE-CANONICAL" or schema.get("schema_version")!="v0.1" or "Universe_Eligible_Flag" in schema_field_names: raise ValueError("governing schema contract mismatch")
    company_records,company_map_source=_load_company_map(args.company_map,args.company_map_sheet); company_map_errors=validate_company_map(company_records) if company_records else []; company_map,listing_days=_company_map_index(company_records) if not company_map_errors else ({},{})
    totals={k:0 for k in ["rows","date_nulls","code_nulls","code_lexical_failures","duplicate_rows","ohlc_required_null_rows","normal","pending_zero","zero_with_trade","other_ohlc","numeric_nonfinite_rows","volume_nonintegral_rows","decimal_failures","pass","pending","quarantine","mapped_rows","listing_boundary_failures"]}
    reason_counts={code:0 for code in PRICE_REASON_CODES}; year_results={}; d0_column_sets=[]; date_units={}; raw_lineage_ok=True
    issue_handle=open(args.row_issues_output,"w",encoding="utf-8") if args.row_issues_output else None
    try:
        for year in (2024,2025,2026):
            path=inputs[year]; meta,data=read_columns(path,READ_COLUMNS); columns=list(meta.columns.keys()); d0_column_sets.append(columns)
            if set(columns)!=set(EXPECTED_RAW_COLUMNS): raise ValueError(f"logical raw column set mismatch in {year}")
            unit=timestamp_unit(meta.columns["Date"].logical_type); date_units[str(year)]=unit; date_days=_date_days(np.asarray(data["Date"],dtype=np.int64),unit); n=len(date_days); totals["rows"]+=n
            code_nulls,code_failures=code_lexical_failures(data["Code"]); code_null_mask=_null_mask(np.asarray(data["Code"],dtype=object)); code_lex_mask=_lexical_failure_mask(np.asarray(data["Code"],dtype=object)); date_null_mask=_null_mask(np.asarray(data["Date"])); duplicate_mask=_duplicate_mask(date_days,data["Code"])
            ohlc_null_mask=np.zeros(n,dtype=bool)
            for field in ("Open","High","Low","Close"): ohlc_null_mask|=_null_mask(np.asarray(data[field]))
            classes=classify_ohlc(data["Open"],data["High"],data["Low"],data["Close"],data["Volume"],data["Amount"]); normal_mask=classes==OHLC_CLASS_NORMAL; pending_mask=classes==OHLC_CLASS_ZERO_OHL_NO_TRADE_METRICS; with_trade_mask=classes==OHLC_CLASS_ZERO_OHL_WITH_TRADE_METRICS; other_ohlc_mask=classes==OHLC_CLASS_OTHER_INCONSISTENCY
            nonfinite_mask=np.zeros(n,dtype=bool)
            for field in NUMERIC_CHECK_FIELDS:
                arr=np.asarray(data[field],dtype=np.float64); nonfinite_mask|=(~np.isfinite(arr)&~np.isnan(arr))
            volume_arr=np.asarray(data["Volume"],dtype=np.float64); volume_nonintegral_mask=np.isfinite(volume_arr)&(volume_arr!=np.trunc(volume_arr)); decimal_failures=0; numeric_detail={}
            for field in NUMERIC_CHECK_FIELDS:
                au=numeric_audit(np.asarray(data[field])); numeric_detail[field]={"null_count":au.null_count,"nonfinite_count":au.nonfinite_count,"fractional_count":au.fractional_count,"exact_decimal_roundtrip_failures":au.exact_decimal_roundtrip_failures}
                if field in NUMERIC_DECIMAL_FIELDS: decimal_failures+=au.exact_decimal_roundtrip_failures
            reason_masks={"PRICE-Q001":date_null_mask,"PRICE-Q002":code_null_mask,"PRICE-Q003":duplicate_mask,"PRICE-Q004":ohlc_null_mask,"PRICE-Q005":other_ohlc_mask&~ohlc_null_mask,"PRICE-Q006":with_trade_mask,"PRICE-Q007":nonfinite_mask,"PRICE-Q008":volume_nonintegral_mask,"PRICE-Q009":code_lex_mask}; quarantine_mask=np.zeros(n,dtype=bool)
            for code,mask in reason_masks.items(): reason_counts[code]+=int(mask.sum()); quarantine_mask|=mask
            pending_semantics_mask=pending_mask&~quarantine_mask; pass_mask=~(quarantine_mask|pending_semantics_mask)
            additions={"date_nulls":int(date_null_mask.sum()),"code_nulls":code_nulls,"code_lexical_failures":code_failures,"duplicate_rows":int(duplicate_mask.sum()),"ohlc_required_null_rows":int(ohlc_null_mask.sum()),"normal":int(normal_mask.sum()),"pending_zero":int(pending_mask.sum()),"zero_with_trade":int(with_trade_mask.sum()),"other_ohlc":int(other_ohlc_mask.sum()),"numeric_nonfinite_rows":int(nonfinite_mask.sum()),"volume_nonintegral_rows":int(volume_nonintegral_mask.sum()),"decimal_failures":decimal_failures,"pass":int(pass_mask.sum()),"pending":int(pending_semantics_mask.sum()),"quarantine":int(quarantine_mask.sum())}
            for k,v in additions.items(): totals[k]+=v
            mapped_rows=0; observed_mapped_codes=set(); listing_failures=0
            if company_map:
                code_list=np.asarray(data["Code"],dtype=object); map_mask=np.fromiter((code in company_map for code in code_list.tolist()),dtype=bool,count=n); mapped_rows=int(map_mask.sum()); observed_mapped_codes=set(code_list[map_mask].tolist())
                for code,listing_day in listing_days.items():
                    code_mask=code_list==code
                    if code_mask.any(): listing_failures+=int(np.count_nonzero(code_mask&(date_days<listing_day)))
                totals["mapped_rows"]+=mapped_rows; totals["listing_boundary_failures"]+=listing_failures
            raw_ref=components[year].get("stable_storage_locator"); lineage_ok=isinstance(raw_ref,str) and raw_ref.startswith("s3://") and components[year].get("sha256")==component_results[str(year)]["sha256_observed"]; raw_lineage_ok &= lineage_ok
            _write_issue_rows(issue_handle,year=year,data=data,date_days=date_days,classes=classes,pending_mask=pending_semantics_mask,quarantine_mask=quarantine_mask,reason_masks=reason_masks)
            year_results[str(year)]={"filename":Path(path).name,"row_count":n,"column_count":len(columns),"columns":columns,"physical_dtypes":{name:(f"{physical_type_name(col.physical_type)}/TIMESTAMP[{timestamp_unit(col.logical_type)}]" if name=="Date" else physical_type_name(col.physical_type)) for name,col in meta.columns.items()},"created_by":meta.created_by,"date_min":_day_string(int(date_days.min())),"date_max":_day_string(int(date_days.max())),"trading_date_count":int(np.unique(date_days).size),"distinct_code_count":int(np.unique(data["Code"]).size),"date_precision":unit,"duplicate_date_code_rows":int(duplicate_mask.sum()),"ohlc_classes":{OHLC_CLASS_NORMAL:int(normal_mask.sum()),OHLC_CLASS_ZERO_OHL_NO_TRADE_METRICS:int(pending_mask.sum()),OHLC_CLASS_ZERO_OHL_WITH_TRADE_METRICS:int(with_trade_mask.sum()),OHLC_CLASS_OTHER_INCONSISTENCY:int(other_ohlc_mask.sum())},"numeric_results":numeric_detail,"mapped_rows":mapped_rows if company_map else None,"observed_company_map_codes":len(observed_mapped_codes) if company_map else None,"company_map_codes_absent_from_raw":sorted(set(company_map)-observed_mapped_codes) if company_map else None,"listing_boundary_failures":listing_failures if company_map else None,"raw_storage_ref":raw_ref,"raw_lineage_status":"PASS" if lineage_ok else "FAIL"}
    finally:
        if issue_handle is not None: issue_handle.close()
    logical_column_set_equal=all(set(cols)==set(d0_column_sets[0]) for cols in d0_column_sets); physical_date_drift=len(set(date_units.values()))>1; row_accounting_ok=canonical_row_accounting(totals["rows"],totals["pass"],totals["pending"],totals["quarantine"])
    hard_contract_failure=any([totals["date_nulls"]>0,totals["code_nulls"]>0,totals["code_lexical_failures"]>0,totals["duplicate_rows"]>0,totals["ohlc_required_null_rows"]>0,totals["other_ohlc"]>0,totals["numeric_nonfinite_rows"]>0,totals["volume_nonintegral_rows"]>0,totals["decimal_failures"]>0,not raw_lineage_ok,not row_accounting_ok,bool(company_map_errors),totals["listing_boundary_failures"]>0])
    d0="PASS_WITH_PHYSICAL_METADATA_DRIFT" if logical_column_set_equal and physical_date_drift else ("PASS" if logical_column_set_equal else "FAIL"); d1="PASS" if not any([totals["date_nulls"],totals["code_nulls"],totals["code_lexical_failures"],totals["numeric_nonfinite_rows"],totals["volume_nonintegral_rows"],totals["decimal_failures"]]) else "FAIL"; d2="BLOCKED_ON_OHLC_SEMANTICS" if totals["pending_zero"] or totals["zero_with_trade"] else ("PASS" if not totals["other_ohlc"] else "FAIL")
    d3="FAIL_COMPANY_MAP_CONTRACT" if company_map_errors else ("PASS_FOR_AVAILABLE_MAPPING" if company_map and totals["listing_boundary_failures"]==0 else ("FAIL_LISTING_BOUNDARY" if company_map else "WAITING_FOR_WORKBOOK_BYTES")); company_version=args.company_map_version or (company_map_source if company_map else "NONE"); d3_v08="PASS" if company_map and "v0.8" in company_version.lower() and totals["listing_boundary_failures"]==0 else "WAITING_FOR_WORKBOOK_BYTES"
    blockers=[]
    if args.ca_gate_status!="PASS": blockers.append("CA Completeness Gate pending")
    if totals["pending_zero"]: blockers.append("OHLC zero-OHL semantics final rule not yet approved")
    if totals["zero_with_trade"]: blockers.append(f"{totals['zero_with_trade']} zero-OHL/nonzero-trade rows require CA/source adjudication")
    if d3_v08!="PASS": blockers.append("D3 latest v0.8 workbook refresh required when actual bytes are available")
    blockers.extend(["D4 not executed","D5 final audit not executed"])
    if hard_contract_failure: blockers.insert(0,"HARD_D0_D3_CONTRACT_FAILURE")
    execution_basis="|".join([ENGINE_VERSION,dataset_sha,component_results["2024"]["sha256_observed"],component_results["2025"]["sha256_observed"],component_results["2026"]["sha256_observed"],_git_commit()]); execution_id=hashlib.sha256(execution_basis.encode()).hexdigest()[:24]
    result={"execution_id":execution_id,"source_dataset_id":dataset_id,"source_dataset_sha256":dataset_sha,"component_hash_results":component_results,"component_row_counts":{y:year_results[y]["row_count"] for y in ("2024","2025","2026")},"total_rows":totals["rows"],"input_hash_gate":"PASS","schema_results":{"expected_raw_columns":EXPECTED_RAW_COLUMNS,"logical_column_set_equal":logical_column_set_equal,"physical_date_precision_drift":physical_date_drift,"canonical_schema_id":schema.get("schema_id"),"canonical_schema_version":schema.get("schema_version"),"Universe_Eligible_Flag_authoritative":False},"component_results":year_results,"date_results":{"null_rows":totals["date_nulls"],"source_units":date_units,"normalization_target":"YYYY-MM-DD","deterministic_ns_us_conversion":"PASS" if set(date_units.values())<={"ns","us"} else "PARTIAL"},"code_results":{"null_rows":totals["code_nulls"],"lexical_failures":totals["code_lexical_failures"],"numeric_only_validation":"PROHIBITED","leading_zero_policy":"PRESERVE_AS_STRING"},"duplicate_results":{"duplicate_date_code_rows":totals["duplicate_rows"]},"numeric_results":{"numeric_nonfinite_rows":totals["numeric_nonfinite_rows"],"volume_nonintegral_rows":totals["volume_nonintegral_rows"],"exact_decimal_value_preservation":"PASS" if totals["decimal_failures"]==0 else "FAIL","exact_decimal_roundtrip_failures":totals["decimal_failures"],"persistent_binary_float":"PROHIBITED"},"ohlc_results":{"required_null_rows":totals["ohlc_required_null_rows"],OHLC_CLASS_NORMAL:totals["normal"],OHLC_CLASS_ZERO_OHL_NO_TRADE_METRICS:totals["pending_zero"],OHLC_CLASS_ZERO_OHL_WITH_TRADE_METRICS:totals["zero_with_trade"],OHLC_CLASS_OTHER_INCONSISTENCY:totals["other_ohlc"],"total_classified_rows":totals["normal"]+totals["pending_zero"]+totals["zero_with_trade"]+totals["other_ohlc"]},"quarantine_counts_by_reason":reason_counts,"quarantine_total_rows":totals["quarantine"],"classified_pending_rows":totals["pending"],"transformed_pass_rows":totals["pass"],"company_id_mapping":{"source":company_map_source,"record_count":len(company_records) if company_records else None,"mapping_contract_errors":company_map_errors,"mapped_raw_rows":totals["mapped_rows"] if company_map else None,"unresolved_nonproject_policy":"NULL_NO_GUESSING","foreign_key_failures":len(company_map_errors)},"listing_boundary_checks":{"listing_dates_available":len(listing_days) if company_map else None,"raw_rows_before_resolved_listing_date":totals["listing_boundary_failures"] if company_map else None,"version_used":company_version,"D3_v0_8_refresh":d3_v08},"raw_lineage_check":"PASS" if raw_lineage_ok else "FAIL","CA_dependent_unresolved_count":totals["pending"]+totals["zero_with_trade"],"row_accounting_equation":{"source":totals["rows"],"pass":totals["pass"],"pending":totals["pending"],"quarantine":totals["quarantine"],"check":"PASS" if row_accounting_ok else "FAIL"},"D0_status":d0,"D1_status":d1,"D2_status":d2,"D3_status":d3,"D4_interface":"IMPLEMENTED_SEPARATE_MODULE","D4_executed":False,"CA_completeness_gate":args.ca_gate_status,"canonical_promotion_allowed":False,"canonical_bytes_created":False,"canonical_dataset_id_assigned":False,"canonical_cutover":False,"raw_bytes_changed":False,"price_dataset_identity_changed":False,"blocker_list":blockers,"software":{"engine_version":ENGINE_VERSION,"python":platform.python_version(),"numpy":np.__version__,"pandas":_package_version("pandas"),"pyarrow":_package_version("pyarrow"),"duckdb":_package_version("duckdb"),"thrift":_package_version("thrift"),"script_git_commit":_git_commit(),"reader":"flat-parquet-thrift+libsnappy fallback"},"control_plane_references":{"manifest":args.manifest,"schema":args.schema},"execution_timestamp":datetime.now(ZoneInfo("Asia/Seoul")).isoformat(timespec="seconds")}
    return result,2 if hard_contract_failure else 0


def build_parser():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument("--input-2024",required=True); p.add_argument("--input-2025",required=True); p.add_argument("--input-2026",required=True); p.add_argument("--manifest",required=True); p.add_argument("--schema",required=True); p.add_argument("--company-map"); p.add_argument("--company-map-sheet"); p.add_argument("--company-map-version"); p.add_argument("--ca-gate-status",choices=["PASS","PENDING","BLOCKED"],default="PENDING"); p.add_argument("--audit-output",required=True); p.add_argument("--row-issues-output"); p.add_argument("--mode",choices=["dry-run"],default="dry-run"); return p

def main()->int:
    args=build_parser().parse_args(); result,exit_code=run(args); Path(args.audit_output).parent.mkdir(parents=True,exist_ok=True)
    with open(args.audit_output,"w",encoding="utf-8") as h: json.dump(result,h,ensure_ascii=False,indent=2,sort_keys=True); h.write("\n")
    print(json.dumps({"execution_id":result.get("execution_id"),"total_rows":result.get("total_rows"),"D0":result.get("D0_status"),"D1":result.get("D1_status"),"D2":result.get("D2_status"),"D3":result.get("D3_status"),"row_accounting":result.get("row_accounting_equation"),"canonical_promotion_allowed":False,"exit_code":exit_code},ensure_ascii=False)); return exit_code
if __name__=="__main__": raise SystemExit(main())
