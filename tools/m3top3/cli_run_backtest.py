from __future__ import annotations

import argparse
import json
from pathlib import Path

from .admission import EXIT_AUTHORITY, EXIT_BLOCKED, EXIT_INTEGRITY, M3Top3AdmissionError, verify_official_scorer
from .backtest import ValidationRunner
from .ledger import PredictionLedger
from .model_interface import RankingEngine, load_scorer
from .outcome import ExplicitWindowResolver, OutcomeBuilder
from .providers import DuckDBParquetPriceProvider


def _load_json_or_path(value):
    if isinstance(value,dict): return value
    if isinstance(value,str): return json.loads(Path(value).read_text(encoding="utf-8"))
    return None


def main(argv:list[str]|None=None) -> int:
    p=argparse.ArgumentParser(description="Run M3Top3 validation over materialized PIT snapshots")
    p.add_argument("--config",required=True); p.add_argument("--snapshot-root",required=True); p.add_argument("--output",required=True)
    args=p.parse_args(argv)
    try:
        config_path=Path(args.config); cfg=json.loads(config_path.read_text(encoding="utf-8")); mode=cfg.get("execution_mode","DIAGNOSTIC")
        if mode=="OFFICIAL": raise M3Top3AdmissionError("OFFICIAL_MODE_GLOBALLY_BLOCKED","official execution has no active governed trust root",exit_code=EXIT_AUTHORITY)
        try: scorer=load_scorer(cfg["scorer_plugin"],cfg.get("scorer_kwargs",{}))
        except (ImportError,AttributeError,KeyError,TypeError,ValueError) as exc:
            raise M3Top3AdmissionError("OFFICIAL_SCORER_ADMISSION_DENIED",f"scorer plugin cannot be loaded: {exc}",exit_code=EXIT_AUTHORITY) from exc
        scorer_config_bytes=b""; scorer_receipt=None
        if mode=="OFFICIAL":
            scorer_config_path=cfg.get("scorer_config_path")
            if not scorer_config_path: raise M3Top3AdmissionError("OFFICIAL_SCORER_ADMISSION_DENIED","official mode requires scorer_config_path",exit_code=EXIT_AUTHORITY)
            scorer_config_bytes=Path(scorer_config_path).read_bytes(); scorer_receipt=_load_json_or_path(cfg.get("official_model_receipt")); verify_official_scorer(scorer,scorer_config_bytes,scorer_receipt)
        elif mode!="DIAGNOSTIC":
            raise M3Top3AdmissionError("PLACEHOLDER_CONFIG_NOT_ADMISSIBLE","unsupported execution_mode",exit_code=EXIT_AUTHORITY)
        ranking=RankingEngine(cfg.get("tie_break_policy","UNRESOLVED_CONTROL")); price=DuckDBParquetPriceProvider(cfg["price_paths"],cfg["price_dataset_id"],cfg["price_dataset_hash"],cfg.get("price_source_semantics","RAW_IMMUTABLE"),cfg.get("price_release"),cfg.get("price_component_manifest")); windows=ExplicitWindowResolver(cfg["window_end_by_snapshot_date"],cfg.get("window_protocol_version","UNRESOLVED_CONTROL")); outcomes=OutcomeBuilder(price,windows,cfg.get("validation_protocol_version","m3top3-outcome-working-v0.1")); runner=ValidationRunner(scorer,ranking,outcomes,execution_mode=mode,scorer_config_bytes=scorer_config_bytes,official_scorer_receipt=scorer_receipt)
        root=Path(args.snapshot_root); out=Path(args.output); ledger=PredictionLedger(out/"prediction-ledger.jsonl"); results=[]; blocked=[]; failed_integrity=[]; failed_authority=[]
        snapshot_dirs=sorted(p for p in root.iterdir() if p.is_dir() and (p/"manifest.json").exists())
        for d in snapshot_dirs:
            try:
                result=runner.run_snapshot(d,out/"runs",ledger)
                if result.get("status","").startswith("BLOCKED"): blocked.append({"snapshot":d.name,"code":result["status"]})
                else: results.append(result)
            except M3Top3AdmissionError as exc:
                target=failed_integrity if exc.exit_code==EXIT_INTEGRITY else failed_authority if exc.exit_code==EXIT_AUTHORITY else blocked
                target.append({"snapshot":d.name,"code":exc.code})
    except M3Top3AdmissionError as exc:
        print(json.dumps({"status":"FAILED_ADMISSION","code":exc.code,"exit":exc.exit_code},ensure_ascii=False,indent=2)); return exc.exit_code
    except (OSError,KeyError,ValueError,TypeError,json.JSONDecodeError) as exc:
        print(json.dumps({"status":"FAILED_AUTHORITY","code":"PLACEHOLDER_CONFIG_NOT_ADMISSIBLE","error":str(exc)},ensure_ascii=False,indent=2)); return EXIT_AUTHORITY
    summary={"requested":len(snapshot_dirs),"admitted":len(results),"blocked":len(blocked),"failed_integrity":len(failed_integrity),"failed_authority":len(failed_authority),"blocked_items":blocked,"integrity_items":failed_integrity,"authority_items":failed_authority}
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    if failed_authority: return EXIT_AUTHORITY
    if failed_integrity: return EXIT_INTEGRITY
    if blocked or len(results)!=len(snapshot_dirs): return EXIT_BLOCKED
    return 0


if __name__=="__main__": raise SystemExit(main())
