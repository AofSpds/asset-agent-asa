from __future__ import annotations

import statistics
from dataclasses import asdict
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Protocol

from .admission import (
    EXIT_AUTHORITY,
    EXIT_BLOCKED,
    EXIT_INTEGRITY,
    OUTCOME_DATASET_DOMAINS,
    M3Top3AdmissionError,
    preflight_diagnostic_scorer,
    reverify_execution_lineage,
    verify_diagnostic_scorer,
    verify_official_scorer,
    verify_price_release,
    verify_snapshot_artifacts,
)
from .core import aggregate_hash, deterministic_id, hash_file, sha256_hex
from .ledger import FullRunArtifactStore, PredictionLedger, publication_transaction, verify_prediction_batch_coverage
from .model_interface import ModelScorer, RankingEngine
from .outcome import OutcomeBuilder


class RiskMetric(Protocol):
    metric_id: str
    metric_version: str
    def evaluate(self, prediction: dict[str, Any], outcome: dict[str, Any]) -> dict[str, Any]: ...


def _jsonable(value: Any) -> Any:
    if isinstance(value, Decimal): return str(value)
    if isinstance(value, date): return value.isoformat()
    if isinstance(value, dict): return {key:_jsonable(item) for key,item in value.items()}
    if isinstance(value, list): return [_jsonable(item) for item in value]
    return value


OUTCOME_VALIDITY_ALLOWLIST=frozenset({"VALID","CA_PENDING","PENDING_EXIT","NO_ENTRY_PRICE","NO_HOLDING_ROWS","NO_EXIT_PRICE"})
PENDING_OUTCOME_VALIDITIES=frozenset({"CA_PENDING","PENDING_EXIT","NO_ENTRY_PRICE","NO_HOLDING_ROWS","NO_EXIT_PRICE"})


def _verify_built_outcome(built:Any,ranking:dict[str,Any],builder:OutcomeBuilder,snapshot_date:date)->None:
    """Verify preserved OutcomeBuilder output without changing its formulas."""

    price=builder.price; validity=getattr(built,"outcome_validity",None)
    if validity not in OUTCOME_VALIDITY_ALLOWLIST:
        raise M3Top3AdmissionError("OUTCOME_RANKING_IDENTITY_MISMATCH","outcome validity is outside the exact admitted vocabulary",{"outcome_validity":validity},EXIT_INTEGRITY)
    try:
        expected_window_end=builder.windows.window_end(snapshot_date)
    except (KeyError,TypeError,ValueError) as exc:
        raise M3Top3AdmissionError("OUTCOME_COMPONENT_LINEAGE_MISMATCH","outcome window registry cannot resolve the snapshot date",{"snapshot_date":snapshot_date.isoformat()},EXIT_INTEGRITY) from exc
    if (
        getattr(built,"model_score_id",None)!=ranking.get("model_score_id")
        or getattr(built,"price_dataset_id",None)!=getattr(price,"dataset_id",None)
        or getattr(built,"validation_protocol_version",None)!=builder.validation_protocol_version
        or getattr(built,"window_end",None)!=expected_window_end
    ):
        raise M3Top3AdmissionError("OUTCOME_COMPONENT_LINEAGE_MISMATCH","built outcome price/protocol/window identity differs from admitted runtime components",exit_code=EXIT_INTEGRITY)
    semantics=getattr(price,"semantics",None)
    if validity in {"NO_ENTRY_PRICE","NO_HOLDING_ROWS","NO_EXIT_PRICE"}:
        expected_status=("PRELIMINARY","CA_PENDING" if semantics=="RAW_IMMUTABLE" else "UNKNOWN","CA_PENDING")
        expected_validation_id=deterministic_id("valpending",{"score":built.model_score_id,"window_end":expected_window_end.isoformat(),"reason":validity})
    elif validity=="PENDING_EXIT":
        expected_status=("PRELIMINARY","CA_PENDING" if semantics=="RAW_IMMUTABLE" else "EVIDENCE_ADJUSTED_OR_NONE","CA_PENDING" if semantics=="RAW_IMMUTABLE" else "PRICE_CANONICAL")
        expected_validation_id=deterministic_id("valpending",{"score":built.model_score_id,"window_end":expected_window_end.isoformat(),"reason":"NO_EXIT"})
    else:
        expected_status=("PRELIMINARY","UNADJUSTED_RAW","CA_PENDING") if validity=="CA_PENDING" else ("VALIDATION","EVIDENCE_ADJUSTED_OR_NONE","PRICE_CANONICAL")
        if getattr(built,"entry_date",None) is None or getattr(built,"exit_date",None) is None:
            raise M3Top3AdmissionError("OUTCOME_RANKING_IDENTITY_MISMATCH","terminal outcome omits entry/exit identity",exit_code=EXIT_INTEGRITY)
        expected_validation_id=deterministic_id("val",{"score":built.model_score_id,"price":price.dataset_id,"protocol":builder.validation_protocol_version,"entry":built.entry_date.isoformat(),"exit":built.exit_date.isoformat()})
    actual_status=(getattr(built,"status",None),getattr(built,"ca_status",None),getattr(built,"outcome_comparability_status",None))
    if actual_status!=expected_status or getattr(built,"validation_id",None)!=expected_validation_id:
        raise M3Top3AdmissionError("OUTCOME_RANKING_IDENTITY_MISMATCH","outcome status/reason/validation identity is not an exact admitted combination",{"validity":validity,"status":actual_status},EXIT_INTEGRITY)
    for field in ("entry","exit","return_ratio","mfe","mae","horizon_close","horizon_close_return"):
        value=getattr(built,field,None)
        if value is not None and (not isinstance(value,(int,float,Decimal)) or isinstance(value,bool) or not Decimal(str(value)).is_finite()):
            raise M3Top3AdmissionError("OUTCOME_RANKING_IDENTITY_MISMATCH","outcome contains a non-finite or nonnumeric value",{"field":field},EXIT_INTEGRITY)


class MetricsEngine:
    def summarize(self,outcomes:list[dict[str,Any]],eligible_count:int)->dict[str,Any]:
        if len(outcomes)!=eligible_count:
            raise M3Top3AdmissionError("METRIC_DENOMINATOR_INTEGRITY_FAILURE","outcome-record count differs from eligible denominator",{"eligible_count":eligible_count,"outcome_record_count":len(outcomes)},EXIT_INTEGRITY)
        if any(row.get("outcome_validity") not in OUTCOME_VALIDITY_ALLOWLIST for row in outcomes):
            raise M3Top3AdmissionError("OUTCOME_RANKING_IDENTITY_MISMATCH","metrics input contains an outcome validity outside the exact allowlist",exit_code=EXIT_INTEGRITY)
        if any((row.get("outcome_validity")=="VALID" and row.get("status")!="VALIDATION") or (row.get("outcome_validity") in PENDING_OUTCOME_VALIDITIES and row.get("status")!="PRELIMINARY") for row in outcomes):
            raise M3Top3AdmissionError("OUTCOME_RANKING_IDENTITY_MISMATCH","metrics input contains an invalid outcome status/validity combination",exit_code=EXIT_INTEGRITY)
        valid=[row for row in outcomes if row.get("outcome_validity")=="VALID"]
        pending=[row for row in outcomes if row.get("outcome_validity") in PENDING_OUTCOME_VALIDITIES]
        if len(valid)+len(pending)!=eligible_count:
            raise M3Top3AdmissionError("METRIC_DENOMINATOR_INTEGRITY_FAILURE","valid/pending outcome counts do not reconcile",exit_code=EXIT_INTEGRITY)
        accounting={"eligible_count":eligible_count,"outcome_record_count":len(outcomes),"valid_outcome_count":len(valid),"pending_outcome_count":len(pending)}
        if pending:
            return {**accounting,"metrics_status":"WITHHELD_PENDING_OUTCOMES","mean_return":None,"median_return":None,"win_rate":None,"mean_mfe_return":None}
        try:
            returns=[Decimal(str(row["return_ratio"])) for row in valid if row.get("return_ratio") is not None]
            mfe_returns=[(Decimal(str(row["mfe"]))/Decimal(str(row["entry"]))) - Decimal("1") for row in valid if row.get("entry") is not None and row.get("mfe") is not None]
        except (InvalidOperation,ValueError,TypeError,ZeroDivisionError) as exc:
            raise M3Top3AdmissionError("OUTCOME_RANKING_IDENTITY_MISMATCH","metrics input contains malformed numeric outcome values",{"cause":type(exc).__name__},EXIT_INTEGRITY) from exc
        if any(not value.is_finite() for value in returns+mfe_returns):
            raise M3Top3AdmissionError("OUTCOME_RANKING_IDENTITY_MISMATCH","metrics input contains non-finite outcome values",exit_code=EXIT_INTEGRITY)
        return {**accounting,"metrics_status":"COMPLETE","mean_return":str(sum(returns)/Decimal(len(returns))) if returns else None,"median_return":str(statistics.median(returns)) if returns else None,"win_rate":str(Decimal(sum(value>0 for value in returns))/Decimal(len(returns))) if returns else None,"mean_mfe_return":str(sum(mfe_returns)/Decimal(len(mfe_returns))) if mfe_returns else None}


RUN_IDENTITY_FIELDS=frozenset({"snapshot_manifest_identity_hash","snapshot_content_hash","universe_member_set_digest","eligible_set_digest","denominator_partition_digest","execution_lineage_identity_hash","scorer_identity_hash","ranking_protocol_version","window_protocol_version","validation_protocol_version","result_revision"})


def verify_validation_run_identity(result:dict[str,Any])->None:
    payload=result.get("validation_run_identity_payload")
    if not isinstance(payload,dict) or set(payload)!=RUN_IDENTITY_FIELDS or any(payload.get(field) in {None,""} for field in RUN_IDENTITY_FIELDS):
        raise M3Top3AdmissionError("RUN_ID_LINEAGE_MISMATCH","validation run identity omits required exact lineage inputs",exit_code=EXIT_INTEGRITY)
    expected=deterministic_id("validationrun",payload)
    if result.get("validation_run_id")!=expected:
        raise M3Top3AdmissionError("RUN_ID_LINEAGE_MISMATCH","validation run ID differs from exact lineage payload",{"declared":result.get("validation_run_id"),"expected":expected},EXIT_INTEGRITY)


def _verify_scoring_coverage(inputs:list[dict[str,Any]],scores:list[Any],scorer:ModelScorer)->None:
    expected={row["pit_snapshot_id"]:row for row in inputs}
    if len(expected)!=len(inputs): raise M3Top3AdmissionError("DUPLICATE_MODEL_SCORE_IDENTITY","snapshot input PIT identities are duplicate",exit_code=EXIT_INTEGRITY)
    actual_pits=[getattr(score,"pit_snapshot_id",None) for score in scores]
    if len(actual_pits)!=len(set(actual_pits)):
        raise M3Top3AdmissionError("DUPLICATE_MODEL_SCORE_IDENTITY","scorer output contains duplicate PIT identity",exit_code=EXIT_INTEGRITY)
    missing=sorted(set(expected)-set(actual_pits)); extra=sorted(set(actual_pits)-set(expected))
    if missing: raise M3Top3AdmissionError("FULL_SCORER_OUTPUT_SET_MEMBER_MISSING","scorer-output identity set omits U members",{"missing":missing},EXIT_INTEGRITY)
    if extra or len(scores)!=len(inputs): raise M3Top3AdmissionError("FULL_SCORER_OUTPUT_SET_MEMBER_EXTRA","scorer-output identity set has extra U members",{"extra":extra},EXIT_INTEGRITY)
    seen_pit:set[str]=set(); seen_score:set[str]=set(); seen_company:set[str]=set()
    for index,score in enumerate(scores):
        row=expected.get(getattr(score,"pit_snapshot_id",None)); score_id=getattr(score,"model_score_id",None)
        if row is None: continue
        if score.pit_snapshot_id in seen_pit or score_id in seen_score or score.company_id in seen_company:
            raise M3Top3AdmissionError("DUPLICATE_MODEL_SCORE_IDENTITY","scorer output contains duplicate PIT/company/model-score identity",{"row_index":index},EXIT_INTEGRITY)
        if not isinstance(score_id,str) or not score_id or score.company_id!=row.get("company_id") or score.security_code!=row.get("security_code") or score.model_version!=getattr(scorer,"model_version",None):
            raise M3Top3AdmissionError("SCORE_IDENTITY_MISMATCH","score identity differs from admitted U input",{"row_index":index},EXIT_INTEGRITY)
        status=str(getattr(score,"evaluation_status",""))
        # The bounded runtime admits only the exact diagnostic scorer authority.
        # Status strings are protocol values, not free-form prose: substring
        # filtering would allow forged near-matches such as FORGED_TERMINAL.
        admitted_terminal_statuses=frozenset({"DIAGNOSTIC"})
        admitted_nonterminal_statuses=frozenset({"PARTIAL","UNVERIFIED","UNRESOLVED","BLOCKED","UNKNOWN"})
        value=getattr(score,"total_score",None)
        numeric=isinstance(value,(int,float,Decimal)) and not isinstance(value,bool)
        finite=numeric and Decimal(str(value)).is_finite()
        if row.get("entry_eligible")=="TRUE" and (not finite or status in admitted_nonterminal_statuses):
            raise M3Top3AdmissionError("FULL_ELIGIBLE_SCORE_SET_INCOMPLETE","eligible U member lacks a terminal numeric score",{"company_id":score.company_id,"status":status},EXIT_BLOCKED)
        if row.get("entry_eligible")=="FALSE" and value is not None and not finite:
            raise M3Top3AdmissionError("SCORER_OUTPUT_VALUE_NOT_ADMITTED","terminal-ineligible scorer output must be finite numeric or null",{"company_id":score.company_id},EXIT_INTEGRITY)
        if status not in admitted_terminal_statuses:
            raise M3Top3AdmissionError(
                "SCORER_OUTPUT_STATUS_NOT_ADMITTED",
                "scorer output uses a status outside the exact admitted terminal set",
                {"company_id":score.company_id,"status":status,"admitted":sorted(admitted_terminal_statuses)},
                EXIT_INTEGRITY,
            )
        seen_pit.add(score.pit_snapshot_id); seen_score.add(score_id); seen_company.add(score.company_id)


def _verify_ranking_coverage(ranked:list[dict[str,Any]],inputs:list[dict[str,Any]],manifest:dict[str,Any],scores:list[Any])->None:
    eligible={row["pit_snapshot_id"]:row for row in inputs if row.get("entry_eligible")=="TRUE"}
    ranked_pits=[row.get("pit_snapshot_id") for row in ranked]
    if set(ranked_pits)!=set(eligible) or len(ranked)!=len(eligible) or len(ranked)!=manifest.get("eligible_row_count"):
        raise M3Top3AdmissionError("FULL_RANKING_SET_MISMATCH","full ranking identity set differs from E",{"expected":len(eligible),"actual":len(ranked)},EXIT_INTEGRITY)
    if [row.get("rank") for row in ranked]!=list(range(1,len(ranked)+1)):
        raise M3Top3AdmissionError("RANK_SEQUENCE_INTEGRITY_FAILURE","ranks must be unique contiguous 1..N",exit_code=EXIT_INTEGRITY)
    seen_companies:set[str]=set(); seen_scores:set[str]=set()
    score_by_pit={score.pit_snapshot_id:score for score in scores}
    for row in ranked:
        source=eligible[row["pit_snapshot_id"]]
        if row.get("company_id") in seen_companies or row.get("model_score_id") in seen_scores or row.get("company_id")!=source.get("company_id") or row.get("security_code")!=source.get("security_code") or row.get("denominator_member_id")!=source.get("denominator_member_id") or row.get("eligibility_record_id")!=source.get("eligibility_record_id") or row.get("eligibility_at_snapshot")!="TRUE":
            raise M3Top3AdmissionError("RANKING_IDENTITY_MISMATCH","ranking identity differs from admitted E input",{"rank":row.get("rank")},EXIT_INTEGRITY)
        score=score_by_pit.get(row["pit_snapshot_id"])
        if score is None or row.get("model_score_id")!=score.model_score_id or row.get("model_version")!=score.model_version or row.get("raw_score")!=str(score.total_score) or row.get("score_component_trace")!=score.component_trace:
            raise M3Top3AdmissionError("RANKING_IDENTITY_MISMATCH","ranking score identity/value/trace differs from admitted scorer output",{"rank":row.get("rank")},EXIT_INTEGRITY)
        if row.get("selected_top3") is not (row["rank"]<=min(3,len(ranked))):
            raise M3Top3AdmissionError("TOP3_PROJECTION_MISMATCH","Top3 flag is not an exact full-ranking projection",{"rank":row["rank"]},EXIT_INTEGRITY)
        seen_companies.add(row["company_id"]); seen_scores.add(row["model_score_id"])


def _verify_outcome_coverage(ranked:list[dict[str,Any]],outcomes:list[dict[str,Any]],outcome_refs:list[dict[str,Any]])->None:
    expected={row["model_score_id"]:row for row in ranked}; actual=[row.get("model_score_id") for row in outcomes]
    missing=sorted(set(expected)-set(actual)); extra=sorted(set(actual)-set(expected))
    if missing: raise M3Top3AdmissionError("FULL_OUTCOME_SET_MEMBER_MISSING","outcome set omits ranked E members",{"missing":missing},EXIT_INTEGRITY)
    if extra: raise M3Top3AdmissionError("FULL_OUTCOME_SET_MEMBER_EXTRA","outcome set contains outside-E identities",{"extra":extra},EXIT_INTEGRITY)
    company_keys=[(row.get("model_score_id"),row.get("company_id")) for row in outcomes]
    if len(actual)!=len(set(actual)) or len(company_keys)!=len(set(company_keys)):
        raise M3Top3AdmissionError("DUPLICATE_OUTCOME_IDENTITY","outcome set has duplicate model-score/company identities",exit_code=EXIT_INTEGRITY)
    for outcome in outcomes:
        ranking=expected[outcome["model_score_id"]]
        if any(outcome.get(field)!=ranking.get(field) for field in ("company_id","security_code","pit_snapshot_id","rank","denominator_member_id","eligibility_record_id")) or outcome.get("dataset_refs")!=outcome_refs:
            raise M3Top3AdmissionError("OUTCOME_RANKING_IDENTITY_MISMATCH","outcome identity/lineage differs from ranking",exit_code=EXIT_INTEGRITY)


def verify_result_status_claim(status:str,price_semantics:str,metrics:dict[str,Any])->None:
    if status not in {"PRELIMINARY","EXPERIMENTAL","VALIDATION"}:
        raise M3Top3AdmissionError("RESULT_STATUS_NOT_ADMITTED","result status is outside the exact admitted vocabulary",{"status":status},EXIT_INTEGRITY)
    if status=="VALIDATION" and (price_semantics=="RAW_IMMUTABLE" or metrics.get("pending_outcome_count",0)>0):
        raise M3Top3AdmissionError("INVALID_VALIDATION_STATUS_CLAIM","raw/CA-pending output cannot be labeled VALIDATION",exit_code=EXIT_AUTHORITY)


class ValidationRunner:
    def __init__(self,scorer:ModelScorer,ranking:RankingEngine,outcome_builder:OutcomeBuilder,metrics:MetricsEngine|None=None,execution_mode:str="DIAGNOSTIC",scorer_config_bytes:bytes|None=None,official_scorer_receipt:dict[str,Any]|None=None,diagnostic_scorer_identity:dict[str,Any]|None=None,execution_lineage:dict[str,Any]|None=None,window_release_identity:dict[str,Any]|None=None):
        self.scorer=scorer; self.ranking=ranking; self.outcome_builder=outcome_builder; self.metrics=metrics or MetricsEngine(); self.execution_mode=execution_mode; self.execution_lineage=execution_lineage; self.window_release_identity=window_release_identity; self.scorer_config_bytes=scorer_config_bytes or b""
        if execution_mode=="OFFICIAL": self.scorer_identity=official_scorer_receipt or {}; verify_official_scorer(scorer,self.scorer_config_bytes,official_scorer_receipt)
        elif execution_mode=="DIAGNOSTIC":
            admitted=preflight_diagnostic_scorer(diagnostic_scorer_identity,self.scorer_config_bytes)
            self.scorer_identity=verify_diagnostic_scorer(scorer,admitted,self.scorer_config_bytes)
        else: raise M3Top3AdmissionError("PLACEHOLDER_CONFIG_NOT_ADMISSIBLE",f"unsupported execution mode {execution_mode!r}",exit_code=EXIT_AUTHORITY)
        if self.execution_lineage is not None and not self.execution_lineage.get("synthetic_only"):
            reverify_execution_lineage(self.execution_lineage)
            releases={release["domain"]:release for release in self.execution_lineage.get("portable_releases",[])}
            scorer_release=releases.get("SCORER_RELEASE")
            if not isinstance(scorer_release,dict) or scorer_release.get("artifact_sha256")!=self.scorer_identity.get("scorer_artifact_sha256"):
                raise M3Top3AdmissionError("SCORER_IDENTITY_MISMATCH","exact scorer artifact differs from admitted SCORER_RELEASE",exit_code=EXIT_AUTHORITY)
        verify_price_release(self.outcome_builder.price)

    def run_snapshot(self,snapshot_dir:str|Path,output_dir:str|Path,prediction_ledger:PredictionLedger|None=None)->dict[str,Any]:
        snapshot_dir=Path(snapshot_dir); output_dir=Path(output_dir)
        if self.execution_lineage is not None and not self.execution_lineage.get("synthetic_only"):
            try:
                reverify_execution_lineage(self.execution_lineage)
            except M3Top3AdmissionError as exc:
                raise M3Top3AdmissionError(
                    "ADMISSION_PRECEDES_SCORER",
                    "live execution-lineage admission failed before scorer invocation",
                    {
                        "cause":exc.code,
                        "execution_lineage_bundle_hash":self.execution_lineage.get("bundle_sha256"),
                        "execution_lineage_identity_hash":self.execution_lineage.get("lineage_identity_hash"),
                    },
                    EXIT_INTEGRITY,
                ) from exc
        verified=verify_snapshot_artifacts(snapshot_dir); manifest=verified.manifest; inputs=verified.model_inputs
        if self.execution_lineage is not None and (self.execution_lineage["bundle_sha256"]!=manifest.get("execution_lineage_bundle_hash") or self.execution_lineage["lineage_identity_hash"]!=manifest.get("execution_lineage_identity_hash")):
            raise M3Top3AdmissionError("DATASET_REF_IDENTITY_MISMATCH","runner and snapshot execution-lineage identities differ",exit_code=EXIT_INTEGRITY)
        if self.execution_lineage is not None and not self.execution_lineage.get("synthetic_only"):
            scorer_release=next((release for release in self.execution_lineage.get("portable_releases",[]) if release.get("domain")=="SCORER_RELEASE"),None)
            if not isinstance(scorer_release,dict) or scorer_release.get("artifact_sha256")!=self.scorer_identity.get("scorer_artifact_sha256"):
                raise M3Top3AdmissionError(
                    "SCORER_IDENTITY_MISMATCH",
                    "exact scorer artifact differs from the admitted SCORER_RELEASE",
                    exit_code=EXIT_AUTHORITY,
                )
        eligible_count=manifest.get("eligible_row_count")
        if eligible_count==0: raise M3Top3AdmissionError("NO_ELIGIBLE_EXECUTION_UNITS","complete denominator contains zero eligible execution units",exit_code=EXIT_BLOCKED)
        verify_price_release(self.outcome_builder.price); price=self.outcome_builder.price
        if self.execution_lineage is not None and not self.execution_lineage.get("synthetic_only"):
            release_map={release["domain"]:release for release in self.execution_lineage["portable_releases"]}
            price_ref=release_map["PRICE_RELEASE"]; ca_ref=release_map["CORPORATE_ACTION_RELEASE"]; calendar_ref=release_map["TRADING_CALENDAR_RELEASE"]; window_ref=release_map["WINDOW_REGISTRY_RELEASE"]
            if price_ref.get("release_id")!=getattr(price,"dataset_id",None):
                raise M3Top3AdmissionError("PRICE_LINEAGE_MISMATCH","outcome price provider differs from exact PRICE_RELEASE",exit_code=EXIT_INTEGRITY)
            operational={release["domain"]:release for release in self.execution_lineage.get("releases",[])}
            provider_components=getattr(price,"component_records",None)
            if isinstance(provider_components,list) and provider_components:
                consumed=sorted((row.get("artifact_sha256"),row.get("byte_size")) for row in provider_components)
            else:
                paths=getattr(price,"paths",None) or ([getattr(price,"path",None)] if getattr(price,"path",None) is not None else [])
                consumed=sorted((hash_file(Path(path)),Path(path).stat().st_size) for path in paths)
            for domain in ("PRICE_RELEASE","CORPORATE_ACTION_RELEASE","TRADING_CALENDAR_RELEASE"):
                release=operational.get(domain); registered=sorted((row.get("artifact_sha256"),row.get("byte_size")) for row in (release or {}).get("components",[]))
                if not release or registered!=consumed:
                    code="PRICE_LINEAGE_MISMATCH" if domain=="PRICE_RELEASE" else "OUTCOME_COMPONENT_LINEAGE_MISMATCH"
                    raise M3Top3AdmissionError(code,f"{domain} registered component bytes differ from consumed provider components",exit_code=EXIT_INTEGRITY)
            if getattr(price,"component_set_digest",None) is not None and price_ref.get("component_set_digest")!=price.component_set_digest:
                raise M3Top3AdmissionError("PRICE_LINEAGE_MISMATCH","PRICE_RELEASE semantic component digest differs from provider manifest",exit_code=EXIT_INTEGRITY)
            if self.window_release_identity!={key:window_ref.get(key) for key in ("release_id","artifact_sha256","release_revision")}:
                raise M3Top3AdmissionError("OUTCOME_COMPONENT_LINEAGE_MISMATCH","outcome window resolver differs from exact WINDOW_REGISTRY_RELEASE",exit_code=EXIT_INTEGRITY)
        expected_price={"price_dataset_id":getattr(price,"dataset_id",None),"price_dataset_hash":getattr(price,"dataset_hash",None),"price_source_semantics":getattr(price,"semantics",None),"price_release_status":getattr(price,"release_status",None)}
        if {field:manifest.get(field) for field in expected_price}!=expected_price: raise M3Top3AdmissionError("PRICE_LINEAGE_MISMATCH","snapshot and outcome-provider price identities differ",exit_code=EXIT_INTEGRITY)
        eligibility={row["pit_snapshot_id"]:row["entry_eligible"] for row in inputs}; scores=[self.scorer.score(row) for row in inputs]
        _verify_scoring_coverage(inputs,scores,self.scorer); by_pit={row["pit_snapshot_id"]:row for row in inputs}
        scorer_outputs=[]
        for score in scores:
            source=by_pit[score.pit_snapshot_id]
            scorer_outputs.append({**_jsonable(asdict(score)),"score_revision":0,"denominator_member_id":source["denominator_member_id"],"eligibility_record_id":source["eligibility_record_id"],"eligibility_status":source["eligibility_status"],"entry_eligible":source["entry_eligible"]})
        scorer_outputs=sorted(scorer_outputs,key=lambda row:(row["company_id"],row["security_code"]))
        ranked=self.ranking.rank(scores,eligibility)
        if ranked and ranked[0].get("status")=="BLOCKED_TIE_POLICY_UNRESOLVED": raise M3Top3AdmissionError("FULL_ELIGIBLE_SCORE_SET_INCOMPLETE","tie-policy control blocks a complete ranking",exit_code=EXIT_BLOCKED)
        ranked=[{**row,"denominator_member_id":by_pit[row["pit_snapshot_id"]]["denominator_member_id"],"eligibility_record_id":by_pit[row["pit_snapshot_id"]]["eligibility_record_id"]} for row in ranked]
        _verify_ranking_coverage(ranked,inputs,manifest,scores)
        release_map={release["domain"]:release for release in manifest["lineage_releases"]}; outcome_refs=[release_map[domain] for domain in OUTCOME_DATASET_DOMAINS]
        outcomes=[]
        for row in ranked:
            try:
                built=self.outcome_builder.build(row["model_score_id"],row["security_code"],date.fromisoformat(manifest["snapshot_date"]))
            except (KeyError,TypeError,ValueError) as exc:
                raise M3Top3AdmissionError(
                    "OUTCOME_COMPONENT_LINEAGE_MISMATCH",
                    "outcome window/component input cannot be resolved for the admitted snapshot",
                    {"snapshot_date":manifest.get("snapshot_date"),"cause":type(exc).__name__},
                    EXIT_INTEGRITY,
                ) from exc
            _verify_built_outcome(built,row,self.outcome_builder,date.fromisoformat(manifest["snapshot_date"]))
            outcomes.append({**_jsonable(asdict(built)),"pit_snapshot_id":row["pit_snapshot_id"],"company_id":row["company_id"],"security_code":row["security_code"],"denominator_member_id":row["denominator_member_id"],"eligibility_record_id":row["eligibility_record_id"],"rank":row["rank"],"selected_top3":row["selected_top3"],"dataset_refs":outcome_refs})
        _verify_outcome_coverage(ranked,outcomes,outcome_refs)
        metrics=self.metrics.summarize(outcomes,eligible_count); result_status="PRELIMINARY" if price.semantics=="RAW_IMMUTABLE" or metrics["pending_outcome_count"] else "EXPERIMENTAL"
        verify_result_status_claim(result_status,price.semantics,metrics)
        scorer_identity={key:value for key,value in self.scorer_identity.items() if key!="scorer_artifact_path"}
        lineage={"snapshot_manifest_identity_hash":manifest["snapshot_manifest_identity_hash"],"snapshot_content_hash":manifest["snapshot_content_hash"],"execution_lineage_bundle_hash":manifest["execution_lineage_bundle_hash"],"execution_lineage_identity_hash":manifest["execution_lineage_identity_hash"],"lineage_releases":manifest["lineage_releases"],"eligible_identity_hash":manifest["eligible_identity_hash"],"ineligible_identity_hash":manifest["ineligible_identity_hash"],"denominator_partition_digest":manifest["denominator_partition_digest"],"scorer_identity":scorer_identity,"validation_protocol_version":self.outcome_builder.validation_protocol_version,"result_revision":0}
        lineage_hash=sha256_hex(lineage); run_payload={"snapshot_manifest_identity_hash":manifest["snapshot_manifest_identity_hash"],"snapshot_content_hash":manifest["snapshot_content_hash"],"universe_member_set_digest":manifest["universe_member_set_digest"],"eligible_set_digest":manifest["eligible_set_digest"],"denominator_partition_digest":manifest["denominator_partition_digest"],"execution_lineage_identity_hash":manifest["execution_lineage_identity_hash"],"scorer_identity_hash":self.scorer_identity["scorer_identity_hash"],"ranking_protocol_version":getattr(self.ranking,"tie_break_policy",None),"window_protocol_version":getattr(self.outcome_builder.windows,"protocol_version",None),"validation_protocol_version":self.outcome_builder.validation_protocol_version,"result_revision":0}; run_id=deterministic_id("validationrun",run_payload)
        selected=[row for row in ranked if row["selected_top3"]]; selected_outcomes=[row for row in outcomes if row["selected_top3"]]
        result={"validation_run_id":run_id,"validation_run_identity_payload":run_payload,"result_revision":0,"status":result_status,"snapshot_date":manifest["snapshot_date"],"snapshot_content_hash":manifest["snapshot_content_hash"],"lineage":lineage,"lineage_hash":lineage_hash,"model_id":self.scorer.model_id,"model_version":self.scorer.model_version,"price_dataset_id":price.dataset_id,"price_dataset_hash":price.dataset_hash,"price_source_semantics":price.semantics,"price_release_status":price.release_status,"validation_protocol_version":self.outcome_builder.validation_protocol_version,"universe_count":len(inputs),"eligible_count":eligible_count,"scorer_output_count":len(scorer_outputs),"scorer_output_identity_hash":aggregate_hash([sha256_hex(row) for row in scorer_outputs]),"ranked_count":len(ranked),"selected_top3_count":len(selected),"outcome_count":len(outcomes),"selected_top3_outcome_count":len(selected_outcomes),"scorer_outputs":scorer_outputs,"ranked":ranked,"top10":ranked[:10],"top3":selected,"outcomes":outcomes,"selected_top3_outcomes":selected_outcomes,"full_universe_outcomes":outcomes,"full_universe_outcome_count":len(outcomes),"metrics":metrics}
        verify_validation_run_identity(result)
        if prediction_ledger is None:
            raise M3Top3AdmissionError("FULL_RANKING_LEDGER_INCOMPLETE","every publishable diagnostic run requires an immutable full-E prediction ledger",exit_code=EXIT_INTEGRITY)
        prediction_records=[]
        if prediction_ledger is not None:
            for row in ranked:
                prediction_records.append(PredictionLedger.build_record(row,manifest["snapshot_cutoff_at"],sha256_hex(by_pit[row["pit_snapshot_id"]]),status=result_status,lineage_hash=lineage_hash))
        verify_prediction_batch_coverage(
            ranked,
            prediction_records,
            predicted_at=manifest["snapshot_cutoff_at"],
            input_hash_by_pit={pit_id:sha256_hex(row) for pit_id,row in by_pit.items()},
            status=result_status,
            lineage_hash=lineage_hash,
        )
        store=FullRunArtifactStore(output_dir/manifest["snapshot_date"]/f"{run_id}.json"); ledger_identity=str(prediction_ledger.path.resolve()) if prediction_ledger is not None and hasattr(prediction_ledger,"path") else f"ledger:{id(prediction_ledger)}"
        with publication_transaction(str(store.path.resolve()),ledger_identity):
            ledger_path=prediction_ledger.path if prediction_ledger is not None and hasattr(prediction_ledger,"path") else None
            artifact_preflight=store.preflight(result,ledger_path)
            if prediction_ledger is not None:
                if not hasattr(prediction_ledger,"preflight_many"): raise M3Top3AdmissionError("FULL_RANKING_LEDGER_INCOMPLETE","prediction ledger lacks non-mutating batch preflight",exit_code=EXIT_INTEGRITY)
                states=prediction_ledger.preflight_many(prediction_records)
                if len(states)!=len(ranked): raise M3Top3AdmissionError("FULL_RANKING_LEDGER_INCOMPLETE","prediction ledger preflight does not cover E",exit_code=EXIT_INTEGRITY)
                prediction_ledger.append_many(prediction_records)
            artifact_state=store.publish(result,ledger_path)
        return {**result,"artifact_state":"REUSED" if artifact_preflight=="REUSED" and artifact_state=="REUSED" else artifact_state}
