from __future__ import annotations

import argparse
import json
from pathlib import Path

from .backtest import ValidationRunner
from .ledger import PredictionLedger
from .model_interface import RankingEngine, load_scorer
from .outcome import ExplicitWindowResolver, OutcomeBuilder
from .providers import DuckDBParquetPriceProvider


def main() -> int:
    p=argparse.ArgumentParser(description="Run M3Top3 validation over materialized PIT snapshots")
    p.add_argument("--config",required=True); p.add_argument("--snapshot-root",required=True); p.add_argument("--output",required=True)
    args=p.parse_args(); cfg=json.loads(Path(args.config).read_text(encoding="utf-8"))
    scorer=load_scorer(cfg["scorer_plugin"],cfg.get("scorer_kwargs",{})); ranking=RankingEngine(cfg.get("tie_break_policy","UNRESOLVED_CONTROL")); price=DuckDBParquetPriceProvider(cfg["price_paths"],cfg["price_dataset_id"],cfg["price_dataset_hash"],cfg.get("price_source_semantics","RAW_IMMUTABLE")); windows=ExplicitWindowResolver(cfg["window_end_by_snapshot_date"],cfg.get("window_protocol_version","UNRESOLVED_CONTROL")); outcomes=OutcomeBuilder(price,windows,cfg.get("validation_protocol_version","m3top3-outcome-working-v0.1")); runner=ValidationRunner(scorer,ranking,outcomes)
    root=Path(args.snapshot_root); out=Path(args.output); ledger=PredictionLedger(out/"prediction-ledger.jsonl"); results=[]
    for d in sorted(p for p in root.iterdir() if p.is_dir() and (p/"manifest.json").exists()): results.append(runner.run_snapshot(d,out/"runs",ledger))
    print(json.dumps({"snapshot_runs":len(results),"blocked":sum(r.get("status","").startswith("BLOCKED") for r in results)},ensure_ascii=False,indent=2)); return 0


if __name__=="__main__": raise SystemExit(main())
