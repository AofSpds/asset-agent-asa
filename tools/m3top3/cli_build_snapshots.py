from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

from .admission import EXIT_AUTHORITY, EXIT_INTEGRITY, M3Top3AdmissionError
from .providers import DuckDBParquetPriceProvider, JsonlFeatureProvider, JsonlUniverseProvider
from .snapshot import BatchSnapshotGenerator, SnapshotBuildConfig, SnapshotBuilder, SnapshotStore


def main(argv:list[str]|None=None) -> int:
    p=argparse.ArgumentParser(description="Build deterministic M3Top3 PIT snapshots")
    p.add_argument("--config",required=True); p.add_argument("--start",required=True); p.add_argument("--end",required=True); p.add_argument("--output",required=True); p.add_argument("--retries",type=int,default=1)
    args=p.parse_args(argv)
    try:
        cfg=json.loads(Path(args.config).read_text(encoding="utf-8"))
        if cfg.get("execution_mode","DIAGNOSTIC") not in {"DIAGNOSTIC","OFFICIAL"}:
            raise M3Top3AdmissionError("PLACEHOLDER_CONFIG_NOT_ADMISSIBLE","unsupported execution_mode",exit_code=EXIT_AUTHORITY)
        if cfg.get("execution_mode")=="OFFICIAL":
            raise M3Top3AdmissionError("OFFICIAL_MODE_GLOBALLY_BLOCKED","official snapshot execution has no active governed trust root",exit_code=EXIT_AUTHORITY)
        universe=JsonlUniverseProvider(cfg["universe_jsonl"],cfg["universe_release_id"],cfg["universe_authority_status"]); features=JsonlFeatureProvider(cfg["features_jsonl"],cfg["feature_source_version"]); price=DuckDBParquetPriceProvider(cfg["price_paths"],cfg["price_dataset_id"],cfg["price_dataset_hash"],cfg.get("price_source_semantics","RAW_IMMUTABLE"),cfg.get("price_release"),cfg.get("price_component_manifest"))
        build_cfg=SnapshotBuildConfig(snapshot_schema_version=cfg.get("snapshot_schema_version","v0.1"),model_input_schema_version=cfg.get("model_input_schema_version","m3top3-input-v0.1-working"),generator_version=cfg.get("generator_version","m3top3-infra-v0.1"),timezone=cfg.get("timezone","Asia/Seoul"),cutoff_local_time=cfg.get("cutoff_local_time","23:59:59"),price_source_semantics=cfg.get("price_source_semantics","RAW_IMMUTABLE"),reconstruction_version=cfg.get("reconstruction_version","RECONSTRUCTION_v0.1_WORKING"))
        runner=BatchSnapshotGenerator(SnapshotBuilder(universe,features,price,build_cfg),SnapshotStore(args.output),retries=args.retries)
        meta={"generator_version":build_cfg.generator_version,"generator_git_commit":cfg.get("generator_git_commit"),"universe_release_id":universe.release_id,"universe_authority_status":universe.authority_status,"feature_source_version":features.source_version,"price_dataset_id":price.dataset_id,"price_dataset_hash":price.dataset_hash,"price_source_semantics":price.semantics,"reconstruction_version":build_cfg.reconstruction_version}
        result=runner.run(date.fromisoformat(args.start),date.fromisoformat(args.end),meta)
    except M3Top3AdmissionError as exc:
        print(json.dumps({"status":"FAILED_ADMISSION","code":exc.code,"exit":exc.exit_code},ensure_ascii=False,indent=2)); return exc.exit_code
    except (KeyError,ValueError,TypeError,json.JSONDecodeError) as exc:
        print(json.dumps({"status":"FAILED_AUTHORITY","code":"PLACEHOLDER_CONFIG_NOT_ADMISSIBLE","error":str(exc)},ensure_ascii=False,indent=2)); return EXIT_AUTHORITY
    summary={"requested":result.requested,"admitted":result.generated+result.reused,"generated":result.generated,"reused":result.reused,"blocked":result.blocked,"failed_integrity":result.failed_integrity,"failed_authority":result.failed_authority,"failed":result.failed,"blocked_dates":result.blocked_dates,"failed_dates":result.failed_dates,"accounting_pass":result.accounting_pass}
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    if result.failed_authority: return EXIT_AUTHORITY
    if result.failed_integrity: return EXIT_INTEGRITY
    if result.failed or not result.accounting_pass: return 1
    return 2 if result.blocked else 0


if __name__=="__main__": raise SystemExit(main())
