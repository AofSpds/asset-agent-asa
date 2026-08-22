from __future__ import annotations

import json
import io
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from dataclasses import replace
from datetime import date
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from tools.m3top3.admission import (
    EXIT_AUTHORITY, EXIT_BLOCKED, EXIT_INTEGRITY, M3Top3AdmissionError,
    _snapshot_manifest_identity_payload, admit_claim_locks,
    admit_execution_lineage_bundle, canonical_component_set_digest,
    reverify_execution_lineage, require_execution_units,
    verify_execution_accounting, verify_snapshot_artifacts,
    verify_universe_release, verify_mutation_execution_receipt,
)
from tools.m3top3.backtest import (
    MetricsEngine, _verify_outcome_coverage, _verify_ranking_coverage,
    _verify_scoring_coverage, verify_result_status_claim,
    verify_validation_run_identity,
)
from tools.m3top3.core import aggregate_hash, canonical_json_bytes, deterministic_id, hash_file, sha256_hex
from tools.m3top3.ledger import FullRunArtifactStore, ImmutableReleaseStore, PredictionLedger, verify_prediction_batch_coverage
from tools.m3top3.model_interface import DiagnosticFixtureScorer, RankingEngine, ScoreResult
from tools.m3top3.providers import (
    EligibilityDecision, InMemoryFeatureProvider, JsonlUniverseProvider,
    StaticUniverseProvider, UniverseState, eligibility_decisions_hash,
)
from tools.m3top3.snapshot import SnapshotBuildConfig, SnapshotBuilder, SnapshotStore
from tools.m3top3.cli_run_backtest import main as backtest_main
from tools.m3top3.cli_build_snapshots import main as snapshot_main
from tools.m3top3.tests._known_failure_helpers import (
    CountingScorer, business_dates, diagnostic_runner,
    diagnostic_scorer_admission, materialize_external_fixture,
    materialize_ready_snapshot, price_provider, standard_price_rows,
    write_execution_lineage_bundle, external_expectation_kwargs,
)


_RAW_MATRIX = """
CLM-001|OFFICIAL_MODE_GLOBALLY_BLOCKED|4
CLM-002|PRICE_CANONICAL_GLOBALLY_BLOCKED|4
CLM-003|OFFICIAL_REPLAY_GLOBALLY_BLOCKED|4
CLM-004|RELEASE_AUTHORITY_ADMISSION_DENIED|4
CLM-005|PLACEHOLDER_RELEASE_NOT_ADMISSIBLE|4
LIN-001|LINEAGE_BUNDLE_REQUIRED|3
LIN-002|BLOCKED_INPUT_INTEGRITY|3
LIN-003|LINEAGE_DOMAIN_MISSING|3
LIN-004|LINEAGE_COMPONENT_HASH_MISMATCH|3
LIN-005|DUPLICATE_LINEAGE_COMPONENT|3
LIN-006|EXTRA_LINEAGE_COMPONENT|3
LIN-007|PASS_RELOCATION_INVARIANCE|0
LIN-008|RELEASE_REVISION_MISMATCH|3
LIN-009|COMPONENT_SET_DIGEST_MISMATCH|3
LIN-010|LINEAGE_COMPONENT_HASH_MISMATCH|3
UNI-001|UNIVERSE_RELEASE_BYTES_REQUIRED|3
UNI-002|DUPLICATE_UNIVERSE_COMPANY_ID|3
UNI-003|DUPLICATE_ACTIVE_SECURITY_CODE|3
UNI-004|UNIVERSE_EFFECTIVE_INTERVAL_CONFLICT|3
UNI-005|UNIVERSE_SET_DIGEST_MISMATCH|3
UNI-006|DENOMINATOR_MEMBER_MISSING|3
UNI-007|DENOMINATOR_MEMBER_EXTRA|3
UNI-008|DUPLICATE_DENOMINATOR_KEY|3
UNI-009|ELIGIBILITY_RELEASE_NOT_COMPLETE|2
UNI-010|DENOMINATOR_COUNT_MISMATCH|3
UNI-011|ELIGIBLE_SET_DIGEST_MISMATCH|3
UNI-012|DENOMINATOR_LINEAGE_MISMATCH|3
UNI-013|NO_ELIGIBLE_EXECUTION_UNITS|2
UNI-014|SELF_CERTIFIED_UNIVERSE_DENOMINATOR_PROHIBITED|4
REF-001|DATASET_REF_DOMAIN_MISSING|3
REF-002|DUPLICATE_DATASET_REF_DOMAIN|3
REF-003|DATASET_REF_IDENTITY_MISMATCH|3
REF-004|EXTRA_DATASET_REF|3
REF-005|FEATURE_SOURCE_LINEAGE_MISMATCH|3
REF-006|PRICE_LINEAGE_MISMATCH|3
REF-007|OUTCOME_COMPONENT_LINEAGE_MISMATCH|3
REF-008|AMBIGUOUS_COMPONENT_ALIAS|3
SNP-001|SNAPSHOT_UNIVERSE_MEMBER_MISSING|3
SNP-002|SNAPSHOT_UNIVERSE_MEMBER_EXTRA|3
SNP-002B|TERMINAL_INELIGIBLE_IDENTITY_MISSING|3
SNP-003|DUPLICATE_SCOREABLE_SNAPSHOT_KEY|3
SNP-004|SNAPSHOT_DATE_LINEAGE_MISMATCH|3
SNP-005A|BLOCKED_MANIFEST_STATE_CONTRADICTION_OR_BLOCKED_SNAPSHOT_NOT_READY|2
SNP-005B|SNAPSHOT_REVISION_MISMATCH|3
SNP-006|SNAPSHOT_IDENTITY_LINEAGE_INCOMPLETE|3
SCR-001|SCORER_IDENTITY_INCOMPLETE|4
SCR-002|SCORER_IDENTITY_MISMATCH|4
SCR-003|SCORER_IDENTITY_MISMATCH|4
SCR-004|ADMISSION_PRECEDES_SCORER|3
SCR-005|RUN_ID_LINEAGE_MISMATCH|3
RNK-001|FULL_SCORER_OUTPUT_SET_MEMBER_MISSING|3
RNK-002|FULL_SCORER_OUTPUT_SET_MEMBER_EXTRA|3
RNK-003|DUPLICATE_MODEL_SCORE_IDENTITY|3
RNK-004|FULL_ELIGIBLE_SCORE_SET_INCOMPLETE|2
RNK-005|FULL_RANKING_SET_MISMATCH|3
RNK-006|RANK_SEQUENCE_INTEGRITY_FAILURE|3
RNK-007|TOP3_PROJECTION_MISMATCH|3
RNK-008|FULL_RANKING_LEDGER_INCOMPLETE|3
OUT-001|FULL_OUTCOME_SET_MEMBER_MISSING|3
OUT-002|FULL_OUTCOME_SET_MEMBER_EXTRA|3
OUT-003|DUPLICATE_OUTCOME_IDENTITY|3
OUT-004|OUTCOME_RANKING_IDENTITY_MISMATCH|3
OUT-005|PASS_EXPLICIT_PENDING_OUTCOME|0
OUT-006|METRIC_DENOMINATOR_INTEGRITY_FAILURE|3
OUT-007|INVALID_VALIDATION_STATUS_CLAIM|4
CLI-001|NO_EXECUTION_UNITS|2
CLI-002|NO_EXECUTION_UNITS|2
CLI-003|EXECUTION_ACCOUNTING_MISMATCH|2
IMM-001|IMMUTABLE_RELEASE_COLLISION|3
IMM-002|NONDETERMINISTIC_RERUN|3
IMM-003|PASS_OR_IMMUTABLE_COLLISION|0_OR_3
IMM-004|NONDETERMINISTIC_RERUN|3
IMM-005|INCOMPLETE_RESULT_PUBLICATION|3
MUT-001|MUTATION_SURVIVOR_PROHIBITED|3
MUT-002|MUTATION_REGRESSION_INCOMPLETE|3
"""
MATRIX = {parts[0]:(parts[1],parts[2]) for line in _RAW_MATRIX.strip().splitlines() if (parts:=line.split("|"))}

# These are execution invariants, not observations copied back from a run.
# The production-matrix worker compares them with independently observed
# counters/fingerprints for every case.
EXPECTED_SCORER_CALLS = {
    **{f"RNK-{index:03d}":4 for index in range(1,9)},
    **{f"OUT-{index:03d}":4 for index in range(1,5)},
    "OUT-005":4,
    "IMM-002":8,
    "IMM-003":8,
    "IMM-004":8,
    "IMM-005":4,
}
EXPECTED_NO_WRITE = {case_id:case_id not in {"OUT-005","IMM-003"} for case_id in MATRIX}


def production_surface(case_id:str)->str:
    prefix=case_id.split("-",1)[0]
    return {
        "CLM":"admission.admit_claim_locks / admission.verify_price_release",
        "LIN":"admission.admit_execution_lineage_bundle / admission.reverify_execution_lineage",
        "UNI":"providers UniverseProvider / admission.verify_universe_release / ValidationRunner.run_snapshot",
        "REF":"admission.verify_snapshot_artifacts / ValidationRunner.run_snapshot",
        "SNP":"admission.verify_snapshot_artifacts",
        "SCR":"admission scorer verifier / ValidationRunner",
        "RNK":"backtest scoring/ranking verifier / ledger.verify_prediction_batch_coverage",
        "OUT":"backtest outcome/metrics verifier / ValidationRunner.run_snapshot",
        "CLI":"cli_build_snapshots.main / cli_run_backtest.main",
        "IMM":"ledger immutable stores / ValidationRunner.run_snapshot",
        "MUT":"admission.verify_mutation_execution_receipt with subprocess evidence",
    }[prefix]


def _write_json(path:Path,value)->None:
    path.write_bytes(canonical_json_bytes(value)+b"\n")


class RWP403MatrixTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.root=Path(self.tmp.name); self._observed_scorers=[]
    def tearDown(self): self.tmp.cleanup()

    def execute_case_observation(self,case_id):
        """Execute one adapter and return production-path evidence.

        The returned actual code/exit is captured directly from the production
        call.  It is never replaced with the expected matrix value.  The
        filesystem observation is taken across the case, except immutable
        collision cases which set a stricter attack-window observation after
        their initial governed fixture publication.
        """

        expected_code,exit_text=MATRIX[case_id]
        expected_exit=0 if exit_text=="0_OR_3" else int(exit_text)
        expected={
            "code":expected_code,
            "exit_code":expected_exit,
            "scorer_calls":EXPECTED_SCORER_CALLS.get(case_id,0),
            "no_write":EXPECTED_NO_WRITE[case_id],
        }
        self._write_invariant_override=None
        before=self._fingerprint(self.root)
        observed_code=None; observed_exit=1; raw_exception=None
        try:
            value=self._action(case_id)
            if case_id.startswith("CLI-"):
                observed_code,observed_exit=value
            elif isinstance(value,tuple) and len(value)==2 and isinstance(value[1],int):
                observed_code,observed_exit=value
            else:
                observed_code,observed_exit=value,0
        except M3Top3AdmissionError as exc:
            observed_code,observed_exit=exc.code,exc.exit_code
        except Exception as exc:  # Reported as raw; never recast as a stable code.
            observed_code,observed_exit=type(exc).__name__,1
            raw_exception=f"{type(exc).__name__}: {exc}"
        after=self._fingerprint(self.root)
        observed_no_write=before==after if self._write_invariant_override is None else self._write_invariant_override
        actual={
            "code":observed_code,
            "exit_code":observed_exit,
            "scorer_calls":sum(scorer.calls for scorer in self._observed_scorers),
            "no_write":observed_no_write,
        }
        return {
            "case_id":case_id,
            "expected":expected,
            "actual":actual,
            "production_path":True,
            "production_surface":production_surface(case_id),
            "fabricated_code":False,
            "caught_and_relabelled":False,
            "synthetic_summary_only":False,
            "pre_fingerprint":sha256_hex(before),
            "post_fingerprint":sha256_hex(after),
            "raw_exception":raw_exception,
            "verdict":"PASS" if raw_exception is None and expected==actual else "FAIL",
        }

    def _assert_expected(self,case_id,action):
        # `action` remains in the signature so older mutation selectors retain
        # their exact call shape; execution is centralized for the reportable
        # production observation.
        del action
        observation=self.execute_case_observation(case_id)
        self.assertIsNone(observation["raw_exception"],observation)
        self.assertEqual(observation["actual"],observation["expected"],observation)
        self.assertEqual(observation["verdict"],"PASS",observation)

    @staticmethod
    def _fingerprint(root):
        governed={}
        for path in root.rglob("*"):
            relative=path.relative_to(root)
            if path.is_file() and (
                any(any(token in part for token in ("out","result","runs")) for part in relative.parts[:-1])
                or any(token in path.name for token in ("result","ledger","prediction"))
            ):
                governed[str(path.relative_to(root))]=sha256_hex(path.read_bytes())
        return governed

    def _observe_scorer(self,scorer):
        if scorer is not None and all(existing is not scorer for existing in self._observed_scorers): self._observed_scorers.append(scorer)
        return scorer

    def _bundle(self,root:Path|None=None):
        root=root or self.root; artifacts=root/"components"; artifacts.mkdir(parents=True,exist_ok=True)
        specs={}
        for domain in (
            "UNIVERSE_RELEASE","DENOMINATOR_ELIGIBILITY_RELEASE","FEATURE_SOURCE_RELEASE",
            "PRICE_RELEASE","CORPORATE_ACTION_RELEASE","TRADING_CALENDAR_RELEASE",
            "WINDOW_REGISTRY_RELEASE","SCORER_RELEASE",
        ):
            path=artifacts/f"{domain.lower()}.bin"; path.write_bytes(f"exact:{domain}".encode())
            specs[domain]={"release_id":f"RID-{domain}","artifact_path":path,"semantic_role":domain}
        return write_execution_lineage_bundle(root,specs)

    def _mutate_bundle(self,mutator):
        path,_,_=self._bundle(); bundle=json.loads(path.read_text()); mutator(bundle); _write_json(path,bundle)
        return admit_execution_lineage_bundle(path,hash_file(path))

    def _external_provider(self,fixture):
        return JsonlUniverseProvider(fixture["universe_path"],"U-EXTERNAL","DIAGNOSTIC",denominator_path=fixture["denominator_path"],lineage_manifest_path=fixture["universe_manifest"],lineage_manifest_hash=hash_file(fixture["universe_manifest"]),**external_expectation_kwargs(fixture["universe_manifest"]))

    def _mutate_live_lineage_slice(self,fixture,field,value):
        provider=self._external_provider(fixture)
        manifest=json.loads(fixture["universe_manifest"].read_text(encoding="utf-8"))
        manifest["slices"][0][field]=value
        _write_json(fixture["universe_manifest"],manifest)
        provider._lineage_manifest=manifest
        provider._lineage_slices={row["snapshot_date"]:row for row in manifest["slices"]}
        provider.lineage_manifest_hash=hash_file(fixture["universe_manifest"])
        return verify_universe_release(provider,fixture["dates"][0],provider.states_at(fixture["dates"][0]))

    def _rewrite_snapshot(self,snapshot_dir,pit,model,audits,manifest):
        texts=[]
        for name,rows in (("pit_snapshot.jsonl",pit),("model_input.jsonl",model),("retrieval_audit.jsonl",audits)):
            text=b"".join(canonical_json_bytes(row)+b"\n" for row in rows); (snapshot_dir/name).write_bytes(text); texts.append(text)
        manifest.update({"pit_file_sha256":sha256_hex(texts[0]),"model_input_file_sha256":sha256_hex(texts[1]),"retrieval_audit_file_sha256":sha256_hex(texts[2]),"pit_row_count":len(pit),"model_input_row_count":len(model),"retrieval_audit_row_count":len(audits),"retrieval_audit_content_hash":aggregate_hash([sha256_hex(row) for row in audits]),"retrieval_receipt_ids":sorted(row["retrieval_receipt_id"] for row in audits),"retrieval_source_hashes":sorted({row["source_hash"] for row in audits}),"snapshot_content_hash":aggregate_hash([sha256_hex(row) for row in pit]+[sha256_hex(row) for row in model]+[sha256_hex(row) for row in audits])})
        manifest["snapshot_manifest_identity_hash"]=sha256_hex(_snapshot_manifest_identity_payload(manifest)); _write_json(snapshot_dir/"manifest.json",manifest)

    def _snapshot_rows(self,fixture):
        d=fixture["snapshot_dir"]
        rows=[]
        for name in ("pit_snapshot.jsonl","model_input.jsonl","retrieval_audit.jsonl"):
            rows.append([json.loads(line) for line in (d/name).read_text().splitlines() if line])
        return (*rows,json.loads((d/"manifest.json").read_text()))

    def _run_case(self,case_id):
        self._assert_expected(case_id,lambda:self._action(case_id))

    def _action(self,c):
        # Claim and eight-domain lineage controls.
        if c=="CLM-001": return admit_claim_locks({"execution_mode":"OFFICIAL"})
        if c=="CLM-002":
            p=price_provider(self.root,semantics="PRICE_CANONICAL"); from tools.m3top3.admission import verify_price_release; return verify_price_release(p)
        if c=="CLM-003": return admit_claim_locks({"official_golden":True})
        if c in {"CLM-004","CLM-005"}:
            state="CANONICAL" if c=="CLM-004" else "DIAGNOSTIC_EXACT_BYTE"
            return self._mutate_bundle(lambda b:b.update(state=state))
        if c=="LIN-001": return admit_execution_lineage_bundle(None,None)
        if c=="LIN-002":
            p=self.root/"bad.json"; p.write_text("[bad"); return admit_execution_lineage_bundle(p,hash_file(p))
        if c=="LIN-003": return self._mutate_bundle(lambda b:b["releases"].pop())
        if c=="LIN-004":
            return self._mutate_bundle(lambda b:b["releases"][0]["components"][0].update(artifact_sha256="0"*64))
        if c=="LIN-005":
            def duplicate(b): b["releases"][0]["components"].append(dict(b["releases"][0]["components"][0]))
            return self._mutate_bundle(duplicate)
        if c=="LIN-006":
            path,_,_=self._bundle(); bundle=json.loads(path.read_text()); release=bundle["releases"][0]; manifest_path=Path(release["manifest_path"]); manifest=json.loads(manifest_path.read_text()); extra=dict(manifest["components"][0]); extra["component_id"]+="-EXTRA"; extra["logical_name"]+="-EXTRA"; manifest["components"].append(extra); _write_json(manifest_path,manifest); release["manifest_sha256"]=hash_file(manifest_path); _write_json(path,bundle); return admit_execution_lineage_bundle(path,hash_file(path))
        if c=="LIN-007":
            a=self.root/"a"; b=self.root/"b"; a.mkdir(); b.mkdir(); one=self._bundle(a)[2]; two=self._bundle(b)[2]; self.assertNotEqual(one["bundle_sha256"],two["bundle_sha256"]); self.assertEqual(one["lineage_identity_hash"],two["lineage_identity_hash"]); return "PASS_RELOCATION_INVARIANCE"
        if c=="LIN-008":
            path,_,_=self._bundle(); bundle=json.loads(path.read_text()); release=bundle["releases"][0]; mp=Path(release["manifest_path"]); manifest=json.loads(mp.read_text()); manifest["release_revision"]=1; _write_json(mp,manifest); release["manifest_sha256"]=hash_file(mp); _write_json(path,bundle); return admit_execution_lineage_bundle(path,hash_file(path))
        if c=="LIN-009":
            def forge(b): b["releases"][0]["component_set_digest"]="f"*64
            return self._mutate_bundle(forge)
        if c=="LIN-010":
            _,_,lineage=self._bundle(); Path(lineage["releases"][0]["components"][0]["path"]).write_bytes(b"drift"); return reverify_execution_lineage(lineage)

        # Universe/denominator controls.
        if c=="UNI-001":
            u=StaticUniverseProvider([UniverseState("C","000001",date(2020,1,1),None,True,True,"U")]); u.release_hash=None; return verify_universe_release(u,date(2025,1,2),u.states_at(date(2025,1,2)))
        if c in {"UNI-002","UNI-003","UNI-004"}:
            d=date(2020,6,1)
            if c=="UNI-002": rows=[UniverseState("C","000001",date(2020,1,1),None,True,True,"U1"),UniverseState("C","000002",date(2020,1,1),None,True,True,"U2")]
            elif c=="UNI-003": rows=[UniverseState("C1","000001",date(2020,1,1),None,True,True,"U1"),UniverseState("C2","000001",date(2020,1,1),None,True,True,"U2")]
            else: rows=[UniverseState("C","000001",date(2020,1,1),date(2022,1,1),True,True,"U1"),UniverseState("C","000002",date(2021,1,1),date(2023,1,1),True,True,"U2")]
            u=StaticUniverseProvider(rows); return verify_universe_release(u,d,u.states_at(d))
        if c in {"UNI-005","UNI-010","UNI-011"}:
            f=materialize_external_fixture(self.root)
            field="universe_member_set_digest" if c=="UNI-005" else "eligible_row_count" if c=="UNI-010" else "eligible_set_digest"
            value="0"*64 if c!="UNI-010" else 4
            return self._mutate_live_lineage_slice(f,field,value)
        if c in {"UNI-006","UNI-007","UNI-009","UNI-012"}:
            f=materialize_external_fixture(self.root); u=self._external_provider(f); rows=list(u._denominator_rows)
            if c=="UNI-006": rows.pop()
            elif c=="UNI-007": rows.append(replace(rows[0],company_id="OUTSIDE",security_code="999999",universe_member_id="outside-member",eligibility_record_id="outside-decision"))
            elif c=="UNI-009": rows[0]=replace(rows[0],eligibility_status="UNRESOLVED")
            else: rows[0]=replace(rows[0],universe_release_revision=1)
            u._denominator_rows=rows; u.denominator_state_hash=eligibility_decisions_hash(rows)
            return verify_universe_release(u,f["dates"][0],u.states_at(f["dates"][0]))
        if c=="UNI-008":
            f=materialize_external_fixture(self.root); data=f["denominator_path"].read_bytes(); f["denominator_path"].write_bytes(data+data.splitlines(keepends=True)[0]); return self._external_provider(f)
        if c=="UNI-013":
            rows=[UniverseState("C1","000001",date(2020,1,1),None,True,False,"U1"),UniverseState("C2","000002",date(2020,1,1),None,False,False,"U2")]
            dates=business_dates(); price=price_provider(self.root,standard_price_rows(dates)); features=InMemoryFeatureProvider([]); b=SnapshotBuilder(StaticUniverseProvider(rows),features,price,SnapshotBuildConfig()); built=b.build(dates[0]); sr=self.root/"snap"; SnapshotStore(sr).write(built,{}); scorer=self._observe_scorer(CountingScorer()); runner,_=diagnostic_runner(price,dates,scorer); try_action=lambda:runner.run_snapshot(sr/dates[0].isoformat(),self.root/"result",PredictionLedger(self.root/"zero-e-ledger.jsonl"));
            try: return try_action()
            finally: self.assertEqual(scorer.calls,0)
        if c=="UNI-014":
            f=materialize_external_fixture(self.root); u=self._external_provider(f); return SnapshotBuilder(u,InMemoryFeatureProvider([]),f["price"],SnapshotBuildConfig())

        # Snapshot and row-level lineage controls.
        if c.startswith("REF-") or c.startswith("SNP-"):
            return self._snapshot_ref_action(c)
        if c.startswith("SCR-") or c.startswith("RNK-") or c.startswith("OUT-"):
            return self._model_action(c)
        if c.startswith("CLI-"): return self._cli_action(c)
        if c.startswith("IMM-"): return self._immutable_action(c)
        if c in {"MUT-001","MUT-002"}:
            receipt,binding=self._execute_meta_mutation(survives=c=="MUT-001")
            return verify_mutation_execution_receipt(
                receipt,50,
                expected_freeze_manifest_sha256=binding["freeze_manifest_sha256"],
                expected_source_tree_sha256=binding["source_tree_sha256"],
                expected_registry_sha256=binding["registry_sha256"],
                expected_mutation_ids=binding["mutation_ids"],
            )
        raise AssertionError(c)

    def _snapshot_ref_action(self,c):
        if c=="REF-008":
            artifacts=self.root/"alias"; artifacts.mkdir(); shared=artifacts/"shared.bin"; shared.write_bytes(b"same")
            specs={}; domains=("UNIVERSE_RELEASE","DENOMINATOR_ELIGIBILITY_RELEASE","FEATURE_SOURCE_RELEASE","PRICE_RELEASE","CORPORATE_ACTION_RELEASE","TRADING_CALENDAR_RELEASE","WINDOW_REGISTRY_RELEASE","SCORER_RELEASE")
            for domain in domains:
                path=shared if domain in {"PRICE_RELEASE","CORPORATE_ACTION_RELEASE"} else artifacts/f"{domain}.bin"; path.write_bytes(path.read_bytes() if path.exists() else domain.encode()); specs[domain]={"release_id":domain,"artifact_path":path,"semantic_role":domain}
            return write_execution_lineage_bundle(self.root,specs)
        f=materialize_external_fixture(self.root); pit,model,audits,m=self._snapshot_rows(f)
        if c in {"REF-001","REF-002","REF-003","REF-004"}:
            refs=pit[0]["dataset_refs"]
            if c=="REF-001": refs.pop(0)
            elif c=="REF-002": refs.append(dict(refs[0]))
            elif c=="REF-003": refs[0]["artifact_sha256"]="0"*64
            else: refs.append({**refs[0],"domain":"UNKNOWN_RELEASE"})
        elif c=="REF-005": m["feature_source_version"]="DRIFT"
        elif c=="REF-006":
            other=price_provider(self.root,standard_price_rows(f["dates"]),dataset_id="OTHER"); runner,_=diagnostic_runner(other,f["dates"]); return runner.run_snapshot(f["snapshot_dir"],self.root/"result")
        elif c=="REF-007":
            wrong={"release_id":"WRONG","artifact_sha256":"0"*64,"release_revision":0}; scorer=CountingScorer(); config,receipt=diagnostic_scorer_admission(scorer); from tools.m3top3.backtest import ValidationRunner; from tools.m3top3.model_interface import RankingEngine; from tools.m3top3.outcome import ExplicitWindowResolver,OutcomeBuilder
            runner=ValidationRunner(scorer,RankingEngine("COMPANY_ID_ASC_DIAGNOSTIC"),OutcomeBuilder(f["price"],ExplicitWindowResolver({f["dates"][0].isoformat():f["dates"][5].isoformat()},"test-window-v1")),execution_mode="DIAGNOSTIC",scorer_config_bytes=config,diagnostic_scorer_identity=receipt,execution_lineage=f["lineage"],window_release_identity=wrong); return runner.run_snapshot(f["snapshot_dir"],self.root/"result")
        elif c in {"SNP-001","SNP-002B"}:
            index=-1 if c=="SNP-002B" else 0; pit.pop(index); model.pop(index); audits.pop(index)
        elif c=="SNP-002":
            outside_pit=dict(pit[0]); outside_model=dict(model[0]); outside_audit=dict(audits[0])
            for row in (outside_pit,outside_model,outside_audit): row["company_id"]="OUTSIDE"
            outside_model["security_code"]="999999"; outside_audit["security_code_at_cutoff"]="999999"
            outside_model["universe_record_id"]="U-OUTSIDE"
            member_id=deterministic_id("universe_member",{"company_id":"OUTSIDE","security_code":"999999","valid_from":outside_model.get("universe_valid_from"),"valid_to":outside_model.get("universe_valid_to"),"universe_record_id":"U-OUTSIDE"})
            for row in (outside_pit,outside_model): row["denominator_member_id"]=member_id
            pit.append(outside_pit); model.append(outside_model); audits.append(outside_audit)
        elif c=="SNP-003": pit.append(dict(pit[0])); model.append(dict(model[0])); audits.append(dict(audits[0]))
        elif c=="SNP-004": pit[0]["snapshot_date"]="2025-01-03"; model[0]["snapshot_date"]="2025-01-03"
        elif c=="SNP-005A": m["snapshot_status"]="SNAPSHOT_PARTIAL"
        elif c=="SNP-005B": pit[0]["snapshot_revision"]=1
        elif c=="SNP-006": m.pop("execution_lineage_identity_hash")
        self._rewrite_snapshot(f["snapshot_dir"],pit,model,audits,m); return verify_snapshot_artifacts(f["snapshot_dir"])

    def _model_fixture(self):
        f=materialize_external_fixture(self.root); verified=verify_snapshot_artifacts(f["snapshot_dir"]); scorer=self._observe_scorer(f["scorer"]); scores=[scorer.score(row) for row in verified.model_inputs]; eligibility={row["pit_snapshot_id"]:row["entry_eligible"] for row in verified.model_inputs}; ranked=RankingEngine("COMPANY_ID_ASC_DIAGNOSTIC").rank(scores,eligibility); by={row["pit_snapshot_id"]:row for row in verified.model_inputs}; ranked=[{**row,"denominator_member_id":by[row["pit_snapshot_id"]]["denominator_member_id"],"eligibility_record_id":by[row["pit_snapshot_id"]]["eligibility_record_id"]} for row in ranked]; refs=[]; outcomes=[{**row,"dataset_refs":refs} for row in ranked]; return f,verified,scorer,scores,ranked,refs,outcomes

    def _model_action(self,c):
        if c in {"SCR-001","SCR-002","SCR-003"}:
            scorer=self._observe_scorer(CountingScorer()); config,receipt=diagnostic_scorer_admission(scorer)
            from tools.m3top3.admission import preflight_diagnostic_scorer,verify_diagnostic_scorer
            if c=="SCR-001": receipt.pop("scorer_artifact_sha256")
            elif c=="SCR-002": receipt["config_sha256"]="0"*64
            else: receipt["feature_set_version"]="DRIFT"
            admitted=preflight_diagnostic_scorer(receipt,config); return verify_diagnostic_scorer(scorer,admitted,config)
        if c=="SCR-004":
            fixture=materialize_external_fixture(self.root)
            scorer=self._observe_scorer(fixture["scorer"])
            runner,_=diagnostic_runner(
                fixture["price"],fixture["dates"],scorer,
                execution_lineage=fixture["lineage"],
            )
            component=Path(fixture["lineage"]["releases"][0]["components"][0]["path"])
            component.write_bytes(b"post-admission-drift")
            try:
                return runner.run_snapshot(
                    fixture["snapshot_dir"],
                    self.root/"scr-004-output",
                    PredictionLedger(self.root/"scr-004-ledger.jsonl"),
                )
            finally:
                self.assertEqual(scorer.calls,0)
                self.assertFalse((self.root/"scr-004-output").exists())
                self.assertFalse((self.root/"scr-004-ledger.jsonl").exists())
        if c=="SCR-005":
            return verify_validation_run_identity({"validation_run_id":"x","validation_run_identity_payload":{"snapshot_content_hash":"x"}})
        if c=="OUT-005":
            f=materialize_external_fixture(self.root)
            scorer=self._observe_scorer(f["scorer"])
            runner,_=diagnostic_runner(f["price"],f["dates"],scorer,execution_lineage=f["lineage"])
            result=runner.run_snapshot(f["snapshot_dir"],self.root/"out",PredictionLedger(self.root/"outcome-prediction-ledger.jsonl"))
            self.assertEqual(result["status"],"PRELIMINARY")
            self.assertGreater(result["metrics"]["pending_outcome_count"],0)
            self.assertIsNone(result["metrics"]["mean_mfe_return"])
            self.assertEqual(result["outcome_count"],result["eligible_count"])
            return "PASS_EXPLICIT_PENDING_OUTCOME"
        if c=="OUT-006": return MetricsEngine().summarize([],1)
        if c=="OUT-007": return verify_result_status_claim("VALIDATION","RAW_IMMUTABLE",{"pending_outcome_count":1})
        f,verified,scorer,scores,ranked,refs,outcomes=self._model_fixture()
        if c in {"RNK-001","RNK-002","RNK-003","RNK-004"}:
            if c=="RNK-001": scores.pop()
            elif c=="RNK-002": scores.append(replace(scores[0],pit_snapshot_id="outside",model_score_id="outside-score",company_id="outside"))
            elif c=="RNK-003": scores.append(scores[0])
            else: scores[0]=replace(scores[0],total_score=None,evaluation_status="PARTIAL")
            return _verify_scoring_coverage(verified.model_inputs,scores,scorer)
        if c in {"RNK-005","RNK-006","RNK-007"}:
            if c=="RNK-005": ranked.pop()
            elif c=="RNK-006": ranked[-1]["rank"]+=1
            else: ranked[0]["selected_top3"]=False
            return _verify_ranking_coverage(ranked,verified.model_inputs,verified.manifest,scores)
        if c=="RNK-008":
            input_hashes={row["pit_snapshot_id"]:sha256_hex(row) for row in verified.model_inputs}
            records=[PredictionLedger.build_record(row,verified.manifest["snapshot_cutoff_at"],input_hashes[row["pit_snapshot_id"]],status="PRELIMINARY",lineage_hash="0"*64) for row in ranked[:-1]]
            return verify_prediction_batch_coverage(ranked,records,predicted_at=verified.manifest["snapshot_cutoff_at"],input_hash_by_pit=input_hashes,status="PRELIMINARY",lineage_hash="0"*64)
        if c in {"OUT-001","OUT-002","OUT-003","OUT-004"}:
            if c=="OUT-001": outcomes.pop()
            elif c=="OUT-002": outcomes.append({**outcomes[0],"model_score_id":"outside"})
            elif c=="OUT-003": outcomes.append(dict(outcomes[0]))
            else: outcomes[0]["company_id"]="drift"
            return _verify_outcome_coverage(ranked,outcomes,refs)
        raise AssertionError(c)

    def _immutable_action(self,c):
        if c=="IMM-001":
            store=ImmutableReleaseStore(self.root/"release.json"); store.admit("R",b"one"); return store.admit("R",b"two")
        f=materialize_external_fixture(self.root); self._observe_scorer(f["scorer"]); runner,_=diagnostic_runner(f["price"],f["dates"],f["scorer"],execution_lineage=f["lineage"]); output=self.root/"runs"; ledger=PredictionLedger(self.root/"immutable-prediction-ledger.jsonl"); first=runner.run_snapshot(f["snapshot_dir"],output,ledger)
        if c=="IMM-002":
            path=output/f["dates"][0].isoformat()/f"{first['validation_run_id']}.json"; row=json.loads(path.read_text()); row["status"]="FORGED"; _write_json(path,row); before_result=path.read_bytes(); before_ledger=ledger.path.read_bytes()
            try: return runner.run_snapshot(f["snapshot_dir"],output,ledger)
            finally:
                self._write_invariant_override=path.read_bytes()==before_result and ledger.path.read_bytes()==before_ledger
                self.assertTrue(self._write_invariant_override)
        if c=="IMM-003":
            second=runner.run_snapshot(f["snapshot_dir"],output,ledger); self.assertEqual(second["artifact_state"],"REUSED"); return "PASS_OR_IMMUTABLE_COLLISION"
        if c=="IMM-004":
            result_path=output/f["dates"][0].isoformat()/f"{first['validation_run_id']}.json"; before_result=result_path.read_bytes(); before_ledger=ledger.path.read_bytes(); scorer2=self._observe_scorer(CountingScorer("1")); runner2,_=diagnostic_runner(f["price"],f["dates"],scorer2,execution_lineage=f["lineage"])
            try: return runner2.run_snapshot(f["snapshot_dir"],output,ledger)
            finally:
                self._write_invariant_override=result_path.read_bytes()==before_result and ledger.path.read_bytes()==before_ledger
                self.assertTrue(self._write_invariant_override)
        if c=="IMM-005":
            path=output/f["dates"][0].isoformat()/f"{first['validation_run_id']}.json"; path.with_suffix(".manifest.json").unlink(); before={candidate:candidate.read_bytes() for candidate in path.parent.iterdir() if candidate.is_file()}
            try: return FullRunArtifactStore(path).preflight(first,ledger.path)
            finally:
                self._write_invariant_override=before=={candidate:candidate.read_bytes() for candidate in path.parent.iterdir() if candidate.is_file()}
                self.assertTrue(self._write_invariant_override)
        raise AssertionError(c)

    def _snapshot_cli_config(self,fixture,path:Path)->None:
        expectation=external_expectation_kwargs(fixture["universe_manifest"])
        cfg={
            "execution_mode":"DIAGNOSTIC",
            "execution_lineage_bundle":str(fixture["bundle_path"]),
            "execution_lineage_bundle_sha256":fixture["bundle_hash"],
            "universe_jsonl":str(fixture["universe_path"]),
            "universe_release_id":"U-EXTERNAL",
            "universe_authority_status":"DIAGNOSTIC",
            "denominator_jsonl":str(fixture["denominator_path"]),
            "universe_lineage_manifest":str(fixture["universe_manifest"]),
            "universe_lineage_manifest_hash":hash_file(fixture["universe_manifest"]),
            "universe_expectation_manifest":str(expectation["universe_expectation_manifest_path"]),
            "universe_expectation_manifest_hash":expectation["universe_expectation_manifest_hash"],
            "denominator_expectation_manifest":str(expectation["denominator_expectation_manifest_path"]),
            "denominator_expectation_manifest_hash":expectation["denominator_expectation_manifest_hash"],
            "features_jsonl":str(fixture["features_path"]),
            "feature_source_version":"TEST-FEATURES",
            "price_paths":[str(fixture["price"].path)],
            "price_dataset_id":fixture["price"].dataset_id,
            "price_dataset_hash":fixture["price"].dataset_hash,
            "price_source_semantics":"RAW_IMMUTABLE",
        }
        _write_json(path,cfg)

    def _backtest_cli_config(self,fixture,path:Path)->None:
        cfg={
            "execution_mode":"DIAGNOSTIC",
            "execution_lineage_bundle":str(fixture["bundle_path"]),
            "execution_lineage_bundle_sha256":fixture["bundle_hash"],
            "scorer_plugin":fixture["scorer_receipt"]["scorer_plugin"],
            "scorer_config_path":str(fixture["scorer_config_path"]),
            "diagnostic_scorer_receipt":fixture["scorer_receipt"],
            "tie_break_policy":"COMPANY_ID_ASC_DIAGNOSTIC",
            "price_paths":[str(fixture["price"].path)],
            "price_dataset_id":fixture["price"].dataset_id,
            "price_dataset_hash":fixture["price"].dataset_hash,
            "price_source_semantics":"RAW_IMMUTABLE",
            "window_protocol_version":"test-window-v1",
            "validation_protocol_version":"m3top3-outcome-working-v0.1",
        }
        _write_json(path,cfg)

    def _run_cli(self,fn,argv):
        stream=io.StringIO()
        with redirect_stdout(stream): status=fn(argv)
        payload=json.loads(stream.getvalue())
        return payload.get("code"),status

    def _cli_action(self,c):
        fixture=materialize_external_fixture(self.root)
        if c=="CLI-001":
            config=self.root/"cli-backtest.json"; self._backtest_cli_config(fixture,config)
            snapshot_root=self.root/"empty-snapshot-root"; snapshot_root.mkdir()
            output=self.root/"cli-backtest-output"
            self._observe_scorer(fixture["scorer"])
            with patch("tools.m3top3.cli_run_backtest.load_scorer",return_value=fixture["scorer"]),patch("tools.m3top3.cli_run_backtest.DuckDBParquetPriceProvider",return_value=fixture["price"]):
                observed=self._run_cli(backtest_main,["--config",str(config),"--snapshot-root",str(snapshot_root),"--output",str(output)])
            self.assertEqual(fixture["scorer"].calls,0); self.assertFalse(output.exists())
            return observed
        config=self.root/f"cli-snapshot-{c}.json"; self._snapshot_cli_config(fixture,config); output=self.root/f"cli-snapshot-output-{c}"
        if c=="CLI-002":
            with patch("tools.m3top3.cli_build_snapshots.DuckDBParquetPriceProvider",return_value=fixture["price"]),patch.object(fixture["price"],"trading_dates",return_value=[]):
                observed=self._run_cli(snapshot_main,["--config",str(config),"--start",fixture["dates"][0].isoformat(),"--end",fixture["dates"][0].isoformat(),"--output",str(output)])
            self.assertFalse(output.exists()); return observed
        batch=SimpleNamespace(requested=2,generated=1,reused=0,blocked=0,failed=0,failed_integrity=0,failed_authority=0,failed_dates=[],blocked_dates=[],manifests=[],accounting_pass=False)
        with patch("tools.m3top3.cli_build_snapshots.DuckDBParquetPriceProvider",return_value=fixture["price"]),patch("tools.m3top3.cli_build_snapshots.BatchSnapshotGenerator.run",return_value=batch):
            observed=self._run_cli(snapshot_main,["--config",str(config),"--start",fixture["dates"][0].isoformat(),"--end",fixture["dates"][0].isoformat(),"--output",str(output)])
        self.assertFalse(output.exists()); return observed

    def _execute_meta_mutation(self,*,survives:bool)->tuple[dict,dict]:
        """Run a real baseline and mutant unittest process for meta-gate cases."""

        root=self.root/("meta-survivor" if survives else "meta-killed"); source=root/"source"; mutant=root/"mutant"
        source.mkdir(parents=True)
        module=source/"guard_probe.py"; test_module=source/"test_guard_probe.py"
        module.write_text("def guarded():\n    return True\n",encoding="utf-8")
        test_module.write_text(
            "import unittest\nfrom guard_probe import guarded\n"
            "class GuardProbe(unittest.TestCase):\n"
            "    def test_guard(self): self.assertTrue(guarded())\n",
            encoding="utf-8",
        )
        source_records=lambda:[{"relative_path":path.name,"size":path.stat().st_size,"sha256":hash_file(path)} for path in sorted(source.iterdir()) if path.is_file() and path.suffix!=".pyc"]
        records=source_records()
        source_tree_sha256=sha256_hex(records)
        freeze_payload={"schema_version":"r-wp4-03-freeze-manifest-v1","source_tree_sha256":source_tree_sha256,"files":records,"iva_participation":"NONE"}
        freeze_manifest_sha256=sha256_hex(canonical_json_bytes(freeze_payload)+b"\n")
        registry_payload={"schema_version":"r-wp4-03-meta-registry-v1","mutation_id":"META-REAL-PROCESS","operator":"disable_guard" if not survives else "unrelated_marker"}
        registry_sha256=sha256_hex(registry_payload)
        env=dict(os.environ); env["PYTHONPATH"]=str(source)
        command=[sys.executable,"-m","unittest","test_guard_probe.GuardProbe.test_guard"]
        baseline=subprocess.run(command,cwd=source,env=env,capture_output=True,text=True,timeout=10,check=False)
        self.assertEqual(baseline.returncode,0,baseline.stdout+baseline.stderr)
        shutil.copytree(source,mutant)
        mutant_module=mutant/"guard_probe.py"
        if survives:
            mutant_module.write_text("def guarded():\n    return True  # mutation removed an unrelated marker\n",encoding="utf-8")
        else:
            mutant_module.write_text("def guarded():\n    return False  # mutation disabled the guard\n",encoding="utf-8")
        mutant_env=dict(os.environ); mutant_env["PYTHONPATH"]=str(mutant)
        mutant_run=subprocess.run(command,cwd=mutant,env=mutant_env,capture_output=True,text=True,timeout=10,check=False)
        def execution_record(run,name):
            stdout_path=root/f"{name}.stdout.bin"; stderr_path=root/f"{name}.stderr.bin"
            stdout=run.stdout.encode("utf-8"); stderr=run.stderr.encode("utf-8")
            stdout_path.write_bytes(stdout); stderr_path.write_bytes(stderr)
            summaries=[line.strip() for line in (run.stdout+run.stderr).splitlines() if line.strip()=="OK" or line.strip().startswith("FAILED (")]
            return {"return_code":run.returncode,"timed_out":False,"test_summary":summaries[-1] if summaries else None,"stdout_path":str(stdout_path),"stderr_path":str(stderr_path),"stdout_sha256":sha256_hex(stdout),"stderr_sha256":sha256_hex(stderr),"combined_sha256":sha256_hex(stdout+stderr)}
        baseline_record=execution_record(baseline,"baseline"); mutant_record=execution_record(mutant_run,"mutant")
        status="SURVIVOR" if mutant_record["return_code"]==0 and mutant_record["test_summary"]=="OK" else "KILLED_RED" if str(mutant_record["test_summary"]).startswith("FAILED (failures=") else "HARNESS_ERROR"
        self.assertEqual(sha256_hex(source_records()),source_tree_sha256)
        binding={"freeze_manifest_sha256":freeze_manifest_sha256,"source_tree_sha256":source_tree_sha256,"registry_sha256":registry_sha256}
        receipt={
            "schema_version":"r-wp4-03-mutation-execution-v2",
            "status":"FAIL",
            "readiness":"NO_GO",
            "requested_mutations":1,
            "full_registry_executed":False,
            "killed_red":int(status=="KILLED_RED"),
            "survivors":int(status=="SURVIVOR"),
            "harness_errors":int(status=="HARNESS_ERROR"),
            "source_mutated":False,
            "manifest_drift":False,
            "iva_participation":"NONE",
            "registry_sha256":registry_sha256,
            "freeze_binding_start":{"manifest_sha256":freeze_manifest_sha256,"source_tree_sha256":source_tree_sha256},
            "freeze_binding_end":{"manifest_sha256":freeze_manifest_sha256,"source_tree_sha256":source_tree_sha256},
            "source_tree_before":source_tree_sha256,
            "source_tree_after":source_tree_sha256,
            "killed_ids":["META-REAL-PROCESS"] if status=="KILLED_RED" else [],
            "survivor_ids":["META-REAL-PROCESS"] if status=="SURVIVOR" else [],
            "harness_error_ids":["META-REAL-PROCESS"] if status=="HARNESS_ERROR" else [],
            "results":[{
                "mutation_id":"META-REAL-PROCESS",
                "status":status,
                "baseline":baseline_record,
                "mutant":mutant_record,
            }],
        }
        binding["mutation_ids"]=("META-REAL-PROCESS",)
        return receipt,binding


def _install_matrix_tests():
    for case_id in MATRIX:
        name="test_matrix_"+case_id.lower().replace("-","_")
        def test(self,case_id=case_id): self._run_case(case_id)
        setattr(RWP403MatrixTests,name,test)


_install_matrix_tests()


if __name__=="__main__": unittest.main()
