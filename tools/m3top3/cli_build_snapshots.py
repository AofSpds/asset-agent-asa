from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

from .admission import EXIT_AUTHORITY, EXIT_BLOCKED, EXIT_INTEGRITY, M3Top3AdmissionError, admit_claim_locks, admit_execution_lineage_bundle, require_execution_units, verify_execution_accounting
from .providers import DuckDBParquetPriceProvider, JsonlFeatureProvider, JsonlUniverseProvider
from .snapshot import BatchSnapshotGenerator, SnapshotBuildConfig, SnapshotBuilder, SnapshotStore


def main(argv:list[str]|None=None) -> int:
    p=argparse.ArgumentParser(description="Build deterministic M3Top3 PIT snapshots")
    p.add_argument("--config",required=True); p.add_argument("--start",required=True); p.add_argument("--end",required=True); p.add_argument("--output",required=True); p.add_argument("--retries",type=int,default=1)
    args=p.parse_args(argv)
    try:
        cfg=json.loads(Path(args.config).read_text(encoding="utf-8")); admit_claim_locks(cfg)
        lineage=admit_execution_lineage_bundle(cfg.get("execution_lineage_bundle"),cfg.get("execution_lineage_bundle_sha256"))
        if cfg.get("execution_mode","DIAGNOSTIC") != "DIAGNOSTIC":
            raise M3Top3AdmissionError("PLACEHOLDER_CONFIG_NOT_ADMISSIBLE","unsupported execution_mode",exit_code=EXIT_AUTHORITY)
        start=date.fromisoformat(args.start); end=date.fromisoformat(args.end)
        if start>end: raise M3Top3AdmissionError("NO_EXECUTION_UNITS","snapshot interval is empty or reversed",exit_code=EXIT_BLOCKED)
        universe=JsonlUniverseProvider(
            cfg["universe_jsonl"],
            cfg["universe_release_id"],
            cfg["universe_authority_status"],
            release_hash=cfg.get("universe_release_hash"),
            release_status=cfg.get("universe_release_status"),
            denominator_path=cfg.get("denominator_jsonl"),
            denominator_release_id=cfg.get("denominator_release_id"),
            denominator_release_hash=cfg.get("denominator_release_hash"),
            denominator_status=cfg.get("denominator_release_status"),
            lineage_manifest_path=cfg.get("universe_lineage_manifest"),
            lineage_manifest_hash=cfg.get("universe_lineage_manifest_hash"),
            universe_expectation_manifest_path=cfg.get("universe_expectation_manifest"),
            universe_expectation_manifest_hash=cfg.get("universe_expectation_manifest_hash"),
            denominator_expectation_manifest_path=cfg.get("denominator_expectation_manifest"),
            denominator_expectation_manifest_hash=cfg.get("denominator_expectation_manifest_hash"),
        ); features=JsonlFeatureProvider(cfg["features_jsonl"],cfg["feature_source_version"],source_status=cfg.get("feature_source_status","DIAGNOSTIC_VERIFIED")); price=DuckDBParquetPriceProvider(cfg["price_paths"],cfg["price_dataset_id"],cfg["price_dataset_hash"],cfg.get("price_source_semantics","RAW_IMMUTABLE"),cfg.get("price_release"),cfg.get("price_component_manifest"))
        build_cfg=SnapshotBuildConfig(snapshot_schema_version=cfg.get("snapshot_schema_version","v0.1"),model_input_schema_version=cfg.get("model_input_schema_version","m3top3-input-v0.1-working"),generator_version=cfg.get("generator_version","m3top3-infra-v0.1"),timezone=cfg.get("timezone","Asia/Seoul"),cutoff_local_time=cfg.get("cutoff_local_time","23:59:59"),price_source_semantics=cfg.get("price_source_semantics","RAW_IMMUTABLE"),reconstruction_version=cfg.get("reconstruction_version","RECONSTRUCTION_v0.1_WORKING"))
        runner=BatchSnapshotGenerator(SnapshotBuilder(universe,features,price,build_cfg,execution_lineage=lineage),SnapshotStore(args.output),retries=args.retries)
        meta={"generator_version":build_cfg.generator_version,"generator_git_commit":cfg.get("generator_git_commit"),"universe_release_id":universe.release_id,"universe_authority_status":universe.authority_status,"feature_source_version":features.source_version,"feature_source_hash":features.source_hash,"feature_source_status":features.source_status,"price_dataset_id":price.dataset_id,"price_dataset_hash":price.dataset_hash,"price_source_semantics":price.semantics,"price_release_status":price.release_status,"reconstruction_version":build_cfg.reconstruction_version}
        result=runner.run(start,end,meta)
        require_execution_units(result.requested,"snapshot price/calendar interval")
        verify_execution_accounting(result.requested,admitted=result.generated+result.reused,blocked=result.blocked,failed_integrity=result.failed_integrity,failed_authority=result.failed_authority,failed_internal=max(0,result.failed-result.failed_integrity-result.failed_authority))
    except M3Top3AdmissionError as exc:
        print(json.dumps({"status":"FAILED_ADMISSION","code":exc.code,"exit":exc.exit_code},ensure_ascii=False,indent=2)); return exc.exit_code
    except (OSError,KeyError,ValueError,TypeError,json.JSONDecodeError) as exc:
        print(json.dumps({"status":"FAILED_INTEGRITY","code":"BLOCKED_INPUT_INTEGRITY","error":str(exc)},ensure_ascii=False,indent=2)); return EXIT_INTEGRITY
    summary={"requested":result.requested,"admitted":result.generated+result.reused,"generated":result.generated,"reused":result.reused,"blocked":result.blocked,"failed_integrity":result.failed_integrity,"failed_authority":result.failed_authority,"failed":result.failed,"blocked_dates":result.blocked_dates,"failed_dates":result.failed_dates,"accounting_pass":result.accounting_pass}
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    if result.failed_authority: return EXIT_AUTHORITY
    if result.failed_integrity: return EXIT_INTEGRITY
    if not result.accounting_pass: return EXIT_BLOCKED
    if result.failed: return 1
    return 2 if result.blocked else 0


if __name__=="__main__": raise SystemExit(main())
