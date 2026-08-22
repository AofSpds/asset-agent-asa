from __future__ import annotations

import json
import statistics
from dataclasses import asdict
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any, Protocol

from .admission import verify_official_scorer, verify_price_release, verify_snapshot_artifacts
from .core import deterministic_id, sha256_hex
from .ledger import ImmutableJsonArtifactStore, PredictionLedger
from .model_interface import ModelScorer, RankingEngine
from .outcome import OutcomeBuilder


class RiskMetric(Protocol):
    metric_id: str
    metric_version: str
    def evaluate(self, prediction: dict[str, Any], outcome: dict[str, Any]) -> dict[str, Any]: ...


class MetricsEngine:
    def summarize(self,outcomes:list[dict[str,Any]])->dict[str,Any]:
        returns=[Decimal(str(x["return_ratio"])) for x in outcomes if x.get("return_ratio") is not None]
        mfe_returns=[]
        for x in outcomes:
            if x.get("entry") is not None and x.get("mfe") is not None: mfe_returns.append((Decimal(str(x["mfe"]))/Decimal(str(x["entry"])))-Decimal("1"))
        return {"valid_return_count":len(returns),"mean_return":str(sum(returns)/Decimal(len(returns))) if returns else None,"median_return":str(statistics.median(returns)) if returns else None,"win_rate":str(Decimal(sum(r>0 for r in returns))/Decimal(len(returns))) if returns else None,"mean_mfe_return":str(sum(mfe_returns)/Decimal(len(mfe_returns))) if mfe_returns else None}


class ValidationRunner:
    def __init__(self,scorer:ModelScorer,ranking:RankingEngine,outcome_builder:OutcomeBuilder,metrics:MetricsEngine|None=None,execution_mode:str="DIAGNOSTIC",scorer_config_bytes:bytes|None=None,official_scorer_receipt:dict[str,Any]|None=None):
        self.scorer=scorer; self.ranking=ranking; self.outcome_builder=outcome_builder; self.metrics=metrics or MetricsEngine(); self.execution_mode=execution_mode
        verify_price_release(self.outcome_builder.price)
        if execution_mode == "OFFICIAL":
            verify_official_scorer(scorer,scorer_config_bytes or b"",official_scorer_receipt)
        elif execution_mode != "DIAGNOSTIC":
            from .admission import EXIT_AUTHORITY, M3Top3AdmissionError
            raise M3Top3AdmissionError("PLACEHOLDER_CONFIG_NOT_ADMISSIBLE",f"unsupported execution mode {execution_mode!r}",exit_code=EXIT_AUTHORITY)

    def run_snapshot(self,snapshot_dir:str|Path,output_dir:str|Path,prediction_ledger:PredictionLedger|None=None)->dict[str,Any]:
        snapshot_dir=Path(snapshot_dir); output_dir=Path(output_dir)
        verified=verify_snapshot_artifacts(snapshot_dir); manifest=verified.manifest; inputs=verified.model_inputs
        eligibility={r["pit_snapshot_id"]:r["entry_eligible"] for r in inputs}; scores=[self.scorer.score(r) for r in inputs]; ranked=self.ranking.rank(scores,eligibility)
        if ranked and ranked[0].get("status")=="BLOCKED_TIE_POLICY_UNRESOLVED": return {"status":"BLOCKED_TIE_POLICY_UNRESOLVED","snapshot_date":manifest["snapshot_date"],"ranked":ranked}
        selected=[r for r in ranked if r["selected_top3"]]; outcomes=[]; by_pit={r["pit_snapshot_id"]:r for r in inputs}
        for r in selected:
            inp=by_pit[r["pit_snapshot_id"]]
            out=self.outcome_builder.build(r["model_score_id"],r["security_code"],date.fromisoformat(manifest["snapshot_date"])); d=asdict(out)
            for k,v in list(d.items()):
                if isinstance(v,Decimal): d[k]=str(v)
                if isinstance(v,date): d[k]=v.isoformat()
            outcomes.append(d)
        run_id=deterministic_id("validationrun",{"snapshot_content_hash":manifest["snapshot_content_hash"],"model_id":self.scorer.model_id,"model_version":self.scorer.model_version,"config_hash":self.scorer.config_hash,"price_dataset_id":self.outcome_builder.price.dataset_id,"price_dataset_hash":self.outcome_builder.price.dataset_hash,"validation_protocol":self.outcome_builder.validation_protocol_version})
        result={"validation_run_id":run_id,"status":"EXPERIMENTAL" if self.outcome_builder.price.semantics!="PRICE_CANONICAL" else "VALIDATION","snapshot_date":manifest["snapshot_date"],"snapshot_content_hash":manifest["snapshot_content_hash"],"model_id":self.scorer.model_id,"model_version":self.scorer.model_version,"price_dataset_id":self.outcome_builder.price.dataset_id,"price_source_semantics":self.outcome_builder.price.semantics,"validation_protocol_version":self.outcome_builder.validation_protocol_version,"ranked_count":len(ranked),"selected_top3_count":len(selected),"outcome_count":len(outcomes),"ranked":ranked,"outcomes":outcomes,"metrics":self.metrics.summarize(outcomes)}
        prediction_records=[]
        if prediction_ledger is not None:
            for r in selected:
                inp=by_pit[r["pit_snapshot_id"]]
                record=PredictionLedger.build_record(r,manifest["snapshot_cutoff_at"],sha256_hex(inp),status="EXPERIMENTAL")
                prediction_ledger.check(record); prediction_records.append(record)
        artifact_state=ImmutableJsonArtifactStore(output_dir/manifest["snapshot_date"]/f"{run_id}.json").admit(result)
        if prediction_ledger is not None:
            for record in prediction_records: prediction_ledger.append(record)
        return {**result,"artifact_state":artifact_state}
