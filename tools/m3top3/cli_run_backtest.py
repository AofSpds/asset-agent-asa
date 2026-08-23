from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

from .admission import (
    EXIT_AUTHORITY,
    EXIT_BLOCKED,
    EXIT_INTEGRITY,
    M3Top3AdmissionError,
    admit_claim_locks,
    admit_execution_lineage_bundle,
    preflight_diagnostic_scorer,
    preflight_diagnostic_scorer_origin,
    require_execution_units,
    verify_execution_accounting,
)
from .backtest import ValidationRunner
from .ledger import PredictionLedger
from .model_interface import RankingEngine, load_scorer
from .outcome import ExplicitWindowResolver, OutcomeBuilder
from .providers import DuckDBParquetPriceProvider


def _load_json_or_path(value):
    if isinstance(value,dict): return value
    if isinstance(value,str): return json.loads(Path(value).read_text(encoding="utf-8"))
    return None


def main(argv:list[str]|None=None)->int:
    parser=argparse.ArgumentParser(description="Run M3Top3 diagnostic validation over admitted PIT snapshots")
    parser.add_argument("--config",required=True); parser.add_argument("--snapshot-root",required=True); parser.add_argument("--output",required=True)
    args=parser.parse_args(argv)
    try:
        cfg=json.loads(Path(args.config).read_text(encoding="utf-8")); admit_claim_locks(cfg)
        lineage=admit_execution_lineage_bundle(cfg.get("execution_lineage_bundle"),cfg.get("execution_lineage_bundle_sha256"))
        mode=cfg.get("execution_mode","DIAGNOSTIC")
        if mode!="DIAGNOSTIC": raise M3Top3AdmissionError("PLACEHOLDER_CONFIG_NOT_ADMISSIBLE","unsupported execution mode",exit_code=EXIT_AUTHORITY)
        scorer_config_path=cfg.get("scorer_config_path"); scorer_receipt=_load_json_or_path(cfg.get("diagnostic_scorer_receipt"))
        if not isinstance(scorer_config_path,str): raise M3Top3AdmissionError("SCORER_IDENTITY_INCOMPLETE","diagnostic scorer config path is required",exit_code=EXIT_AUTHORITY)
        scorer_config_bytes=Path(scorer_config_path).read_bytes()
        admitted_scorer=preflight_diagnostic_scorer(scorer_receipt,scorer_config_bytes)
        if cfg.get("scorer_plugin")!=admitted_scorer["scorer_plugin"]: raise M3Top3AdmissionError("SCORER_IDENTITY_MISMATCH","configured plugin differs from exact scorer receipt",exit_code=EXIT_AUTHORITY)
        preflight_diagnostic_scorer_origin(admitted_scorer,lineage)
        try: scorer=load_scorer(cfg["scorer_plugin"],cfg.get("scorer_kwargs",{}))
        except (ImportError,AttributeError,KeyError,TypeError,ValueError) as exc: raise M3Top3AdmissionError("SCORER_IDENTITY_MISMATCH",f"scorer plugin cannot be loaded: {exc}",exit_code=EXIT_AUTHORITY) from exc
        price=DuckDBParquetPriceProvider(cfg["price_paths"],cfg["price_dataset_id"],cfg["price_dataset_hash"],cfg.get("price_source_semantics","RAW_IMMUTABLE"),cfg.get("price_release"),cfg.get("price_component_manifest"))
        window_release=next(release for release in lineage["releases"] if release["domain"]=="WINDOW_REGISTRY_RELEASE")
        try:
            window_payload=json.loads(Path(window_release["artifact_path"]).read_text(encoding="utf-8"))
        except (OSError,UnicodeError,json.JSONDecodeError) as exc:
            raise M3Top3AdmissionError("OUTCOME_COMPONENT_LINEAGE_MISMATCH","window registry exact artifact is unreadable",exit_code=EXIT_INTEGRITY) from exc
        window_mapping=window_payload.get("window_end_by_snapshot_date") if isinstance(window_payload,dict) else None
        window_protocol=window_payload.get("protocol_version") if isinstance(window_payload,dict) else None
        if not isinstance(window_mapping,dict) or not isinstance(window_protocol,str) or not window_protocol:
            raise M3Top3AdmissionError("OUTCOME_COMPONENT_LINEAGE_MISMATCH","window registry schema is incomplete",exit_code=EXIT_INTEGRITY)
        if (cfg.get("window_end_by_snapshot_date") is not None and cfg.get("window_end_by_snapshot_date")!=window_mapping) or (cfg.get("window_protocol_version") is not None and cfg.get("window_protocol_version")!=window_protocol):
            raise M3Top3AdmissionError("OUTCOME_COMPONENT_LINEAGE_MISMATCH","config window values differ from exact registry bytes",exit_code=EXIT_INTEGRITY)
        windows=ExplicitWindowResolver(window_mapping,window_protocol)
        window_identity={key:window_release[key] for key in ("release_id","artifact_sha256","release_revision")}
        runner=ValidationRunner(scorer,RankingEngine(cfg.get("tie_break_policy","UNRESOLVED_CONTROL")),OutcomeBuilder(price,windows,cfg.get("validation_protocol_version","m3top3-outcome-working-v0.1")),execution_mode=mode,scorer_config_bytes=scorer_config_bytes,diagnostic_scorer_identity=admitted_scorer,execution_lineage=lineage,window_release_identity=window_identity)
        root=Path(args.snapshot_root); snapshot_dirs=[]
        if root.exists():
            for candidate in sorted(root.iterdir()):
                if not candidate.is_dir() or candidate.name.startswith(".") or not (candidate/"manifest.json").exists(): continue
                try: date.fromisoformat(candidate.name)
                except ValueError: continue
                snapshot_dirs.append(candidate)
        require_execution_units(len(snapshot_dirs),"backtest snapshot root")
        out=Path(args.output); ledger=PredictionLedger(out/"prediction-ledger.jsonl"); results=[]; blocked=[]; failed_integrity=[]; failed_authority=[]
        for snapshot in snapshot_dirs:
            try: results.append(runner.run_snapshot(snapshot,out/"runs",ledger))
            except M3Top3AdmissionError as exc:
                target=failed_integrity if exc.exit_code==EXIT_INTEGRITY else failed_authority if exc.exit_code==EXIT_AUTHORITY else blocked
                target.append({"snapshot":snapshot.name,"code":exc.code})
        verify_execution_accounting(len(snapshot_dirs),admitted=len(results),blocked=len(blocked),failed_integrity=len(failed_integrity),failed_authority=len(failed_authority))
    except M3Top3AdmissionError as exc:
        print(json.dumps({"status":"FAILED_ADMISSION","code":exc.code,"exit":exc.exit_code},ensure_ascii=False,indent=2)); return exc.exit_code
    except (OSError,KeyError,ValueError,TypeError,json.JSONDecodeError) as exc:
        print(json.dumps({"status":"FAILED_INTEGRITY","code":"BLOCKED_INPUT_INTEGRITY","error":str(exc)},ensure_ascii=False,indent=2)); return EXIT_INTEGRITY
    summary={"requested":len(snapshot_dirs),"admitted":len(results),"blocked":len(blocked),"failed_integrity":len(failed_integrity),"failed_authority":len(failed_authority),"blocked_items":blocked,"integrity_items":failed_integrity,"authority_items":failed_authority}
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    if failed_authority:return EXIT_AUTHORITY
    if failed_integrity:return EXIT_INTEGRITY
    if blocked:return EXIT_BLOCKED
    return 0


if __name__=="__main__": raise SystemExit(main())
