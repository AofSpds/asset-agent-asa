from __future__ import annotations

import inspect
import json
import sys
import tempfile
import unittest
from dataclasses import asdict, replace
from datetime import date
from decimal import Decimal
from pathlib import Path

from tools.m3top3.admission import (
    EXIT_AUTHORITY,
    EXIT_BLOCKED,
    EXIT_INTEGRITY,
    M3Top3AdmissionError,
    _snapshot_manifest_identity_payload,
    preflight_diagnostic_scorer,
    preflight_diagnostic_scorer_origin,
    canonical_component_set_digest,
    price_dataset_identity_hash,
    reverify_execution_lineage,
    universe_member_set_digest,
    eligibility_set_digest,
    verify_diagnostic_scorer,
    verify_lineage_temporal_compatibility,
    verify_mutation_execution_receipt,
    verify_snapshot_artifacts,
)
from tools.m3top3.backtest import (
    MetricsEngine,
    _verify_built_outcome,
    _verify_ranking_coverage,
    _verify_scoring_coverage,
    verify_result_status_claim,
)
from tools.m3top3.core import aggregate_hash, canonical_json_bytes, hash_file, sha256_hex
from tools.m3top3.model_interface import DiagnosticFixtureScorer, RankingEngine, ScoreResult, load_scorer
from tools.m3top3.outcome import ExplicitWindowResolver, OutcomeBuilder
from tools.m3top3.ledger import PredictionLedger
from tools.m3top3.providers import DuckDBParquetPriceProvider, JsonlFeatureProvider, JsonlUniverseProvider, UniverseState
from tools.m3top3.snapshot import SnapshotBuildConfig, SnapshotBuilder, SnapshotStore
from tools.m3top3.tests._known_failure_helpers import (
    CountingScorer,
    diagnostic_scorer_admission,
    diagnostic_runner,
    external_expectation_kwargs,
    materialize_external_fixture,
    write_execution_lineage_bundle,
)


class RWP403V02RemediationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.root=Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def assert_code(self,code,exit_code,action):
        with self.assertRaises(M3Top3AdmissionError) as caught:
            action()
        self.assertEqual((caught.exception.code,caught.exception.exit_code),(code,exit_code))

    @staticmethod
    def _rows(path):
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]

    @staticmethod
    def _write_rows(path,rows):
        payload=b"".join(canonical_json_bytes(row)+b"\n" for row in rows)
        path.write_bytes(payload)
        return payload

    def _rewrite_snapshot(self,snapshot_dir,pit,model,audit,manifest):
        pit_bytes=self._write_rows(snapshot_dir/"pit_snapshot.jsonl",pit)
        model_bytes=self._write_rows(snapshot_dir/"model_input.jsonl",model)
        audit_bytes=self._write_rows(snapshot_dir/"retrieval_audit.jsonl",audit)
        manifest.update({
            "pit_file_sha256":sha256_hex(pit_bytes),
            "model_input_file_sha256":sha256_hex(model_bytes),
            "retrieval_audit_file_sha256":sha256_hex(audit_bytes),
            "pit_row_count":len(pit),
            "model_input_row_count":len(model),
            "retrieval_audit_row_count":len(audit),
            "retrieval_audit_content_hash":aggregate_hash([sha256_hex(row) for row in audit]),
            "retrieval_receipt_ids":sorted(row["retrieval_receipt_id"] for row in audit),
            "retrieval_source_hashes":sorted({row["source_hash"] for row in audit}),
            "snapshot_content_hash":aggregate_hash(
                [sha256_hex(row) for row in pit]
                +[sha256_hex(row) for row in model]
                +[sha256_hex(row) for row in audit]
            ),
        })
        manifest["snapshot_manifest_identity_hash"]=sha256_hex(_snapshot_manifest_identity_payload(manifest))
        (snapshot_dir/"manifest.json").write_bytes(canonical_json_bytes(manifest)+b"\n")

    def test_external_subset_rewrite_rebinds_live_u_and_denominator(self):
        fixture=materialize_external_fixture(self.root)
        snapshot=fixture["snapshot_dir"]
        pit=[row for row in self._rows(snapshot/"pit_snapshot.jsonl") if row["company_id"]!="C4"]
        model=[row for row in self._rows(snapshot/"model_input.jsonl") if row["company_id"]!="C4"]
        audit=[row for row in self._rows(snapshot/"retrieval_audit.jsonl") if row["company_id"]!="C4"]
        manifest=json.loads((snapshot/"manifest.json").read_text(encoding="utf-8"))
        members=sorted(row["denominator_member_id"] for row in model)
        eligible=sorted(row["denominator_member_id"] for row in model if row["entry_eligible"]=="TRUE")
        ineligible=sorted(row["denominator_member_id"] for row in model if row["entry_eligible"]=="FALSE")
        eligible_records=sorted(row["eligibility_record_id"] for row in model if row["entry_eligible"]=="TRUE")
        ineligible_records=sorted(row["eligibility_record_id"] for row in model if row["entry_eligible"]=="FALSE")
        canonical_u=universe_member_set_digest(model)
        canonical_e=eligibility_set_digest(model,"ELIGIBLE")
        canonical_i=eligibility_set_digest(model,"INELIGIBLE")
        manifest.update({
            "denominator_member_ids":members,"denominator_identity_hash":aggregate_hash(members),"denominator_row_count":len(members),
            "eligible_member_ids":eligible,"eligible_identity_hash":aggregate_hash(eligible),"eligible_row_count":len(eligible),
            "ineligible_member_ids":ineligible,"ineligible_identity_hash":aggregate_hash(ineligible),"ineligible_row_count":len(ineligible),
            "eligible_record_ids":eligible_records,"ineligible_record_ids":ineligible_records,
            "universe_member_set_digest":canonical_u,"eligible_set_digest":canonical_e,"ineligible_set_digest":canonical_i,
            "denominator_partition_digest":sha256_hex({"universe_member_set_digest":canonical_u,"eligible_set_digest":canonical_e,"ineligible_set_digest":canonical_i,"universe_count":len(members),"eligible_count":len(eligible),"ineligible_count":len(ineligible)}),
        })
        self._rewrite_snapshot(snapshot,pit,model,audit,manifest)
        self.assert_code("TERMINAL_INELIGIBLE_IDENTITY_MISSING",EXIT_INTEGRITY,lambda:verify_snapshot_artifacts(snapshot))

    def test_custom_live_fixture_cannot_generate_its_own_expectations(self):
        state=UniverseState("C1","005930",date(2020,1,1),None,True,True,"U1","DIAGNOSTIC_VERIFIED")
        self.assert_code(
            "SELF_CERTIFIED_UNIVERSE_DENOMINATOR_PROHIBITED",EXIT_AUTHORITY,
            lambda:materialize_external_fixture(self.root,[state]),
        )
        self.assert_code(
            "SELF_CERTIFIED_UNIVERSE_DENOMINATOR_PROHIBITED",EXIT_AUTHORITY,
            lambda:materialize_external_fixture(self.root,[state],independent_expectation_states=[state]),
        )

    def test_denominator_owns_eligibility_independently_of_legacy_u_flags(self):
        fixture=materialize_external_fixture(self.root,eligibility_status_by_company={"C4":"ELIGIBLE"})
        c4=next(row for row in fixture["built"].model_inputs if row["company_id"]=="C4")
        self.assertFalse(c4["tradable_eligible"])
        self.assertEqual((c4["eligibility_status"],c4["entry_eligible"]),("ELIGIBLE","TRUE"))

    def test_nonzero_revisions_and_nondefault_cutoff_are_preserved(self):
        fixture=materialize_external_fixture(
            self.root,universe_release_revision=7,denominator_release_revision=9,cutoff_local_time="15:30:00"
        )
        manifest=fixture["built"].lineage
        self.assertEqual((manifest["universe_release_revision"],manifest["denominator_release_revision"]),(7,9))
        self.assertTrue(manifest["snapshot_cutoff_at"].endswith("T15:30:00+09:00"))

    def test_future_release_vintage_is_temporal_integrity_failure(self):
        artifacts=self.root/"components"; artifacts.mkdir()
        specs={}
        domains=("UNIVERSE_RELEASE","DENOMINATOR_ELIGIBILITY_RELEASE","FEATURE_SOURCE_RELEASE","PRICE_RELEASE","CORPORATE_ACTION_RELEASE","TRADING_CALENDAR_RELEASE","WINDOW_REGISTRY_RELEASE","SCORER_RELEASE")
        for domain in domains:
            path=artifacts/f"{domain}.bin"; path.write_bytes(domain.encode())
            specs[domain]={"release_id":domain,"artifact_path":path,"semantic_role":domain,"as_of_date":"2026-01-01"}
        _,_,lineage=write_execution_lineage_bundle(self.root,specs)
        self.assert_code("RELEASE_TEMPORAL_MISMATCH",EXIT_INTEGRITY,lambda:verify_lineage_temporal_compatibility(lineage,date(2025,1,2)))

    def test_lazy_component_loss_is_stably_classified(self):
        fixture=materialize_external_fixture(self.root)
        scorer=fixture["scorer"]
        runner,_=diagnostic_runner(fixture["price"],fixture["dates"],scorer,execution_lineage=fixture["lineage"])
        fixture["features_path"].unlink()
        self.assert_code("LINEAGE_COMPONENT_HASH_MISMATCH",EXIT_INTEGRITY,lambda:reverify_execution_lineage(fixture["lineage"]))
        output=self.root/"lazy-output"; ledger=self.root/"lazy-ledger.jsonl"
        with self.assertRaises(M3Top3AdmissionError) as caught:
            runner.run_snapshot(fixture["snapshot_dir"],output,PredictionLedger(ledger))
        self.assertEqual((caught.exception.code,caught.exception.exit_code),("ADMISSION_PRECEDES_SCORER",EXIT_INTEGRITY))
        self.assertEqual(caught.exception.details["cause"],"LINEAGE_COMPONENT_HASH_MISMATCH")
        self.assertEqual(caught.exception.details["execution_lineage_bundle_hash"],fixture["lineage"]["bundle_sha256"])
        self.assertEqual(scorer.calls,0)
        self.assertFalse(output.exists()); self.assertFalse(ledger.exists())

    def test_scorer_source_substitution_is_rejected(self):
        fixture=materialize_external_fixture(self.root)
        config=canonical_json_bytes({"x":"bound"})
        legitimate=Path(inspect.getsourcefile(DiagnosticFixtureScorer) or inspect.getfile(DiagnosticFixtureScorer)).resolve()
        evil=self.root/"evilmod.py"
        evil.write_text(
            "class EvilScorer:\n"
            " model_id='DIAGNOSTIC_FIXTURE'\n model_version='diagnostic-v0'\n model_schema_version='v0.1'\n"
            " feature_set_version='diagnostic'\n"
            f" config_hash='{sha256_hex(config)}'\n",
            encoding="utf-8",
        )
        sys.path.insert(0,str(self.root))
        self.addCleanup(lambda:sys.path.remove(str(self.root)) if str(self.root) in sys.path else None)
        receipt={
            "state":"DIAGNOSTIC_EXACT_BYTES","scorer_plugin":"evilmod:EvilScorer",
            "scorer_artifact_path":str(legitimate),"scorer_artifact_sha256":hash_file(legitimate),"scorer_artifact_byte_size":legitimate.stat().st_size,
            "config_sha256":sha256_hex(config),"config_byte_size":len(config),
            "model_id":"DIAGNOSTIC_FIXTURE","model_version":"diagnostic-v0","model_schema_version":"v0.1","feature_set_version":"diagnostic",
        }
        admitted=preflight_diagnostic_scorer(receipt,config)
        self.assert_code("SCORER_IDENTITY_MISMATCH",EXIT_AUTHORITY,lambda:preflight_diagnostic_scorer_origin(admitted,fixture["lineage"]))
        scorer=load_scorer("evilmod:EvilScorer")
        self.assert_code("SCORER_IDENTITY_MISMATCH",EXIT_AUTHORITY,lambda:verify_diagnostic_scorer(scorer,admitted,config))

    def test_forged_scorer_identity_hash_does_not_bypass_preflight(self):
        scorer=DiagnosticFixtureScorer(); config=canonical_json_bytes({"cfg":1}); scorer.config_hash=sha256_hex(config)
        artifact=Path(inspect.getsourcefile(scorer.__class__) or inspect.getfile(scorer.__class__)).resolve()
        forged={"scorer_identity_hash":"ATTACKER","scorer_artifact_path":str(artifact),"scorer_artifact_sha256":hash_file(artifact),"config_sha256":sha256_hex(config),"model_id":scorer.model_id,"model_version":scorer.model_version,"model_schema_version":scorer.model_schema_version,"feature_set_version":scorer.feature_set_version}
        self.assert_code("SCORER_IDENTITY_INCOMPLETE",EXIT_AUTHORITY,lambda:verify_diagnostic_scorer(scorer,forged,config))

    def test_nonnumeric_and_nonfinite_eligible_scores_are_controlled_blocks(self):
        scorer=DiagnosticFixtureScorer()
        row={"pit_snapshot_id":"P1","company_id":"C1","security_code":"005930","entry_eligible":"TRUE"}
        for value in ("9",Decimal("NaN"),Decimal("Infinity"),Decimal("-Infinity")):
            score=ScoreResult("S1","P1","C1","005930",scorer.model_version,value,"DIAGNOSTIC",[])
            with self.subTest(value=str(value)):
                self.assert_code("FULL_ELIGIBLE_SCORE_SET_INCOMPLETE",EXIT_BLOCKED,lambda score=score:_verify_scoring_coverage([row],[score],scorer))

    def test_rank_rows_bind_exact_scorer_output_identity_value_and_trace(self):
        inputs=[{"pit_snapshot_id":"P1","company_id":"C1","security_code":"005930","denominator_member_id":"U1","eligibility_record_id":"E1","entry_eligible":"TRUE"}]
        score=ScoreResult("S1","P1","C1","005930","diagnostic-v0",Decimal("9"),"DIAGNOSTIC",[{"component_id":"x","contribution":"9"}])
        ranked=RankingEngine("COMPANY_ID_ASC_DIAGNOSTIC").rank([score],{"P1":"TRUE"})
        ranked=[{**ranked[0],"denominator_member_id":"U1","eligibility_record_id":"E1","model_score_id":"FORGED"}]
        self.assert_code("RANKING_IDENTITY_MISMATCH",EXIT_INTEGRITY,lambda:_verify_ranking_coverage(ranked,inputs,{"eligible_row_count":1},[score]))

    def test_publishable_run_requires_full_e_prediction_ledger(self):
        fixture=materialize_external_fixture(self.root)
        runner,scorer=diagnostic_runner(fixture["price"],fixture["dates"],fixture["scorer"],execution_lineage=fixture["lineage"])
        output=self.root/"runs"
        self.assert_code("FULL_RANKING_LEDGER_INCOMPLETE",EXIT_INTEGRITY,lambda:runner.run_snapshot(fixture["snapshot_dir"],output))
        self.assertEqual(scorer.calls,fixture["built"].lineage["denominator_row_count"])
        self.assertFalse(output.exists())

    def test_retrieval_audit_full_compound_key_drift_is_rejected(self):
        fixture=materialize_external_fixture(self.root)
        snapshot=fixture["snapshot_dir"]
        pit=self._rows(snapshot/"pit_snapshot.jsonl"); model=self._rows(snapshot/"model_input.jsonl"); audit=self._rows(snapshot/"retrieval_audit.jsonl")
        manifest=json.loads((snapshot/"manifest.json").read_text(encoding="utf-8"))
        audit[0]["universe_release_revision"]+=1
        self._rewrite_snapshot(snapshot,pit,model,audit,manifest)
        self.assert_code("RETRIEVAL_AUDIT_SEMANTIC_MISMATCH",EXIT_INTEGRITY,lambda:verify_snapshot_artifacts(snapshot))

    def test_outcome_verifier_rejects_unknown_status_and_provider_drift(self):
        fixture=materialize_external_fixture(self.root)
        builder=OutcomeBuilder(fixture["price"],ExplicitWindowResolver({fixture["dates"][0].isoformat():fixture["dates"][5].isoformat()},"test-window-v1"))
        ranking={"model_score_id":"S1","security_code":"005930"}
        built=builder.build("S1","005930",fixture["dates"][0])
        forged=replace(built,outcome_validity="FORGED_TERMINAL")
        self.assert_code("OUTCOME_RANKING_IDENTITY_MISMATCH",EXIT_INTEGRITY,lambda:_verify_built_outcome(forged,ranking,builder,fixture["dates"][0]))
        drifted=replace(built,price_dataset_id="OTHER")
        self.assert_code("OUTCOME_COMPONENT_LINEAGE_MISMATCH",EXIT_INTEGRITY,lambda:_verify_built_outcome(drifted,ranking,builder,fixture["dates"][0]))

    def test_runner_classifies_window_resolution_parse_failure_without_publication(self):
        fixture=materialize_external_fixture(self.root)
        runner,scorer=diagnostic_runner(fixture["price"],fixture["dates"],fixture["scorer"],execution_lineage=fixture["lineage"])

        class BrokenWindowResolver:
            protocol_version="test-window-v1"
            def window_end(self,snapshot_date):
                raise ValueError(f"malformed window for {snapshot_date}")

        runner.outcome_builder.windows=BrokenWindowResolver()
        output=self.root/"window-failure-output"; ledger=self.root/"window-failure-ledger.jsonl"
        self.assert_code(
            "OUTCOME_COMPONENT_LINEAGE_MISMATCH",EXIT_INTEGRITY,
            lambda:runner.run_snapshot(fixture["snapshot_dir"],output,PredictionLedger(ledger)),
        )
        self.assertEqual(scorer.calls,fixture["built"].lineage["denominator_row_count"])
        self.assertFalse(output.exists()); self.assertFalse(ledger.exists())

    def test_metrics_reject_nonfinite_values_and_unknown_result_status(self):
        row={"outcome_validity":"VALID","status":"VALIDATION","return_ratio":"NaN","entry":"1","mfe":"2"}
        self.assert_code("OUTCOME_RANKING_IDENTITY_MISMATCH",EXIT_INTEGRITY,lambda:MetricsEngine().summarize([row],1))
        self.assert_code("RESULT_STATUS_NOT_ADMITTED",EXIT_INTEGRITY,lambda:verify_result_status_claim("FORGED_TERMINAL","RAW_IMMUTABLE",{"pending_outcome_count":0}))

    def test_mutation_receipt_requires_exact_final_freeze_and_registry_binding(self):
        freeze="1"*64; tree="2"*64; registry="3"*64
        baseline_stdout=b"baseline passed\n"; baseline_stderr=b"OK\n"
        mutant_stdout=b"mutant executed\n"; mutant_stderr=b"FAILED (failures=1)\n"
        baseline_stdout_path=self.root/"baseline.stdout.bin"; baseline_stderr_path=self.root/"baseline.stderr.bin"
        mutant_stdout_path=self.root/"mutant.stdout.bin"; mutant_stderr_path=self.root/"mutant.stderr.bin"
        baseline_stdout_path.write_bytes(baseline_stdout); baseline_stderr_path.write_bytes(baseline_stderr)
        mutant_stdout_path.write_bytes(mutant_stdout); mutant_stderr_path.write_bytes(mutant_stderr)
        baseline={
            "return_code":0,"timed_out":False,"test_summary":"OK",
            "stdout_path":str(baseline_stdout_path),"stderr_path":str(baseline_stderr_path),
            "stdout_sha256":sha256_hex(baseline_stdout),"stderr_sha256":sha256_hex(baseline_stderr),
            "combined_sha256":sha256_hex(baseline_stdout+baseline_stderr),
        }
        mutant={
            "return_code":1,"timed_out":False,"test_summary":"FAILED (failures=1)",
            "stdout_path":str(mutant_stdout_path),"stderr_path":str(mutant_stderr_path),
            "stdout_sha256":sha256_hex(mutant_stdout),"stderr_sha256":sha256_hex(mutant_stderr),
            "combined_sha256":sha256_hex(mutant_stdout+mutant_stderr),
        }
        mutation_ids=tuple(f"MUT-{index:02d}" for index in range(1,51))
        results=[{"mutation_id":mutation_id,"status":"KILLED_RED","baseline":baseline,"mutant":mutant} for mutation_id in mutation_ids]
        receipt={
            "schema_version":"r-wp4-03-mutation-execution-v2",
            "status":"PASS","readiness":"GO_FOR_INDEPENDENT_VALIDATION_HANDOFF",
            "requested_mutations":50,"full_registry_executed":True,
            "killed_red":50,"survivors":0,"harness_errors":0,
            "source_mutated":False,"manifest_drift":False,"iva_participation":"NONE",
            "registry_sha256":registry,
            "freeze_binding_start":{"manifest_sha256":freeze,"source_tree_sha256":tree},
            "freeze_binding_end":{"manifest_sha256":freeze,"source_tree_sha256":tree},
            "source_tree_before":tree,"source_tree_after":tree,
            "killed_ids":list(mutation_ids),"survivor_ids":[],"harness_error_ids":[],
            "results":results,
        }
        verify_mutation_execution_receipt(receipt,50,expected_freeze_manifest_sha256=freeze,expected_source_tree_sha256=tree,expected_registry_sha256=registry,expected_mutation_ids=mutation_ids)
        forged=dict(receipt); forged["status"]="FAIL"
        self.assert_code("MUTATION_REGRESSION_INCOMPLETE",EXIT_INTEGRITY,lambda:verify_mutation_execution_receipt(forged,50,expected_freeze_manifest_sha256=freeze,expected_source_tree_sha256=tree,expected_registry_sha256=registry,expected_mutation_ids=mutation_ids))
        self.assert_code("MUTATION_REGRESSION_INCOMPLETE",EXIT_INTEGRITY,lambda:verify_mutation_execution_receipt(receipt,50,expected_freeze_manifest_sha256=freeze,expected_source_tree_sha256=tree,expected_registry_sha256="4"*64,expected_mutation_ids=mutation_ids))
        duplicate=json.loads(json.dumps(receipt))
        duplicate["results"][-1]["mutation_id"]=duplicate["results"][0]["mutation_id"]
        duplicate["killed_ids"][-1]=duplicate["killed_ids"][0]
        self.assert_code("MUTATION_REGRESSION_INCOMPLETE",EXIT_INTEGRITY,lambda:verify_mutation_execution_receipt(duplicate,50,expected_freeze_manifest_sha256=freeze,expected_source_tree_sha256=tree,expected_registry_sha256=registry,expected_mutation_ids=mutation_ids))
        errored=json.loads(json.dumps(receipt))
        errored["results"][0]["mutant"]["test_summary"]="FAILED (failures=1, errors=1)"
        self.assert_code("MUTATION_REGRESSION_INCOMPLETE",EXIT_INTEGRITY,lambda:verify_mutation_execution_receipt(errored,50,expected_freeze_manifest_sha256=freeze,expected_source_tree_sha256=tree,expected_registry_sha256=registry,expected_mutation_ids=mutation_ids))
        self.assert_code("MUTATION_REGRESSION_INCOMPLETE",EXIT_INTEGRITY,lambda:verify_mutation_execution_receipt(receipt,1,expected_freeze_manifest_sha256=freeze,expected_source_tree_sha256=tree,expected_registry_sha256=registry,expected_mutation_ids=mutation_ids))

    def test_multicomponent_price_identity_executes_end_to_end_without_sha_plane_collapse(self):
        fixture=materialize_external_fixture(self.root)
        component_a=self.root/"price-2024.parquet"; component_b=self.root/"price-2025.parquet"
        component_a.write_bytes(b"price-component-a"); component_b.write_bytes(b"price-component-b")
        paths=[component_a,component_b]
        components=[
            {"component_id":f"P-MULTI:{index}","logical_name":path.name,"semantic_role":f"PRICE_PARTITION_{index}","path":str(path.resolve()),"artifact_sha256":hash_file(path),"byte_size":path.stat().st_size}
            for index,path in enumerate(paths,1)
        ]
        dataset_hash=price_dataset_identity_hash("P-MULTI",components)
        component_manifest={"manifest_version":"m3top3-price-components-v2","hash_algorithm":"SHA256","dataset_id":"P-MULTI","dataset_hash":dataset_hash,"component_set_digest":canonical_component_set_digest(components),"components":components}
        dates=fixture["dates"]
        codes=["005930","000660","035420","051910"]
        rows={(code,d):(d,code,100+i,103+i,98+i,101+i,False,None,None) for code in codes for i,d in enumerate(dates)}

        class Result:
            def __init__(self,values): self.values=values
            def fetchall(self): return list(self.values)
            def fetchone(self): return self.values[0] if self.values else None
        class Connection:
            def execute(self,query,params=None):
                if query.startswith("DESCRIBE"):
                    return Result([(name,) for name in ("date","code","open","high","low","close","corporate_action_flag","adjustment_factor","corporate_action_evidence_id")])
                if "HAVING n>1" in query or "GREATEST" in query or "AND (" in query:
                    return Result([])
                if "SELECT DISTINCT" in query:
                    start,end=params
                    return Result([(d,) for d in dates if start<=d<=end])
                if params and " BETWEEN " in query:
                    code,start,end=params
                    return Result([rows[(code,d)] for d in dates if start<=d<=end and (code,d) in rows])
                if params:
                    code,trading_date=params
                    value=rows.get((code,trading_date))
                    return Result([value] if value else [])
                return Result([])
        class Duck:
            @staticmethod
            def connect(): return Connection()

        from unittest.mock import patch
        with patch("tools.m3top3.providers.importlib.import_module",return_value=Duck):
            price=DuckDBParquetPriceProvider(paths,"P-MULTI",dataset_hash,component_manifest=component_manifest)

        lineage_value=json.loads(fixture["universe_manifest"].read_text(encoding="utf-8"))
        u_binding=lineage_value["release"]; d_binding=lineage_value["denominator"]
        alias_roles=["CORPORATE_ACTION_RELEASE","PRICE_RELEASE","TRADING_CALENDAR_RELEASE"]
        alias_base={"physical_alias_allowed":True,"physical_alias_group_id":"PRICE_CA_CALENDAR_SHARED_BYTES","physical_alias_roles":alias_roles}
        bundle_root=self.root/"multi-bundle"; bundle_root.mkdir()
        def alias_components(prefix,role):
            return [{"component_id":f"{prefix}:{index}","logical_name":path.name,"semantic_role":role,"path":path} for index,path in enumerate(paths,1)]
        specs={
            "UNIVERSE_RELEASE":{"release_id":"U-EXTERNAL","artifact_path":fixture["universe_path"],"semantic_role":"UNIVERSE_MEMBERSHIP","components":[{"component_id":"U:ROWS","logical_name":"universe.jsonl","semantic_role":"UNIVERSE_MEMBERSHIP_ROWS","path":fixture["universe_path"]},{"component_id":"U:EXPECTATION","logical_name":"universe-expectation.json","semantic_role":"UNIVERSE_EXPECTATION_MANIFEST","path":Path(u_binding["expectation_manifest_path"])},{"component_id":"U:LINEAGE","logical_name":"universe-lineage.json","semantic_role":"UNIVERSE_LINEAGE_MANIFEST","path":fixture["universe_manifest"]}]},
            "DENOMINATOR_ELIGIBILITY_RELEASE":{"release_id":"U-EXTERNAL:DENOMINATOR","artifact_path":fixture["denominator_path"],"semantic_role":"ELIGIBILITY_DENOMINATOR","components":[{"component_id":"D:ROWS","logical_name":"denominator.jsonl","semantic_role":"DENOMINATOR_ELIGIBILITY_ROWS","path":fixture["denominator_path"]},{"component_id":"D:EXPECTATION","logical_name":"denominator-expectation.json","semantic_role":"DENOMINATOR_EXPECTATION_MANIFEST","path":Path(d_binding["expectation_manifest_path"])}]},
            "FEATURE_SOURCE_RELEASE":{"release_id":"TEST-FEATURES","artifact_path":fixture["features_path"],"semantic_role":"PIT_FEATURE_SOURCE"},
            "PRICE_RELEASE":{"release_id":"P-MULTI","artifact_path":component_a,"semantic_role":"RAW_PRICE","components":components,**alias_base},
            "CORPORATE_ACTION_RELEASE":{"release_id":"P-MULTI:CA","artifact_path":component_a,"semantic_role":"CA_EVIDENCE","components":alias_components("P-MULTI:CA","CA_EVIDENCE_PARTITION"),**alias_base},
            "TRADING_CALENDAR_RELEASE":{"release_id":"P-MULTI:CALENDAR","artifact_path":component_a,"semantic_role":"TRADING_CALENDAR","components":alias_components("P-MULTI:CAL","TRADING_CALENDAR_PARTITION"),**alias_base},
            "WINDOW_REGISTRY_RELEASE":{"release_id":"WINDOW-TEST-V1","artifact_path":fixture["window_path"],"semantic_role":"OUTCOME_WINDOW_REGISTRY"},
            "SCORER_RELEASE":{"release_id":"SCORER-DIAGNOSTIC-EXACT","artifact_path":Path(fixture["scorer_receipt"]["scorer_artifact_path"]),"semantic_role":"DIAGNOSTIC_SCORER"},
        }
        _,_,lineage=write_execution_lineage_bundle(bundle_root,specs)
        universe=JsonlUniverseProvider(
            fixture["universe_path"],"U-EXTERNAL","DIAGNOSTIC",denominator_path=fixture["denominator_path"],
            lineage_manifest_path=fixture["universe_manifest"],lineage_manifest_hash=hash_file(fixture["universe_manifest"]),
            **external_expectation_kwargs(fixture["universe_manifest"]),
        )
        features=JsonlFeatureProvider(fixture["features_path"],"TEST-FEATURES")
        built=SnapshotBuilder(universe,features,price,SnapshotBuildConfig(),execution_lineage=lineage).build(dates[0])
        snapshot_root=self.root/"multi-snapshots"; SnapshotStore(snapshot_root).write(built,{})
        runner,_=diagnostic_runner(price,dates,fixture["scorer"],execution_lineage=lineage)
        result=runner.run_snapshot(snapshot_root/dates[0].isoformat(),self.root/"multi-runs",PredictionLedger(self.root/"multi-ledger.jsonl"))
        self.assertEqual((result["universe_count"],result["ranked_count"],result["outcome_count"]),(4,3,3))
        self.assertNotEqual(next(release for release in lineage["portable_releases"] if release["domain"]=="PRICE_RELEASE")["artifact_sha256"],price.dataset_hash)


if __name__=="__main__":
    unittest.main()
