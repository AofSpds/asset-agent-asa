from __future__ import annotations
import hashlib, json, unittest
from pathlib import Path

from tools.m3top3.features_v1_narrow_patch import FeatureEngineV1NarrowPatch
from tools.m3top3.official_runtime_v1_1 import score_official_snapshot_records_v1_1
from tools.m3top3.shared_interface_guards_v1 import SharedInterfaceGuardError
from tools.m3top3.shared_interface_guards_v1_1 import (
    FEATURE_INPUT_REGISTRY_RELEASE_ID, FEATURE_INPUT_REGISTRY_SHA256,
    REFRESH_REGISTRY_RELEASE_ID, REFRESH_REGISTRY_SHA256, FeatureInputRegistry,
    certification_content_hash, typed_governance_object_hash,
    verify_shared_asset_bindings, whole_block_payload_hash,
)
from tools.m3top3.shared_interface_guards_v1_2 import (
    BOUND_CONTROL_FIX_ASSETS, EvidenceResolverRelease, NumericRuleResolverRelease,
    RECORD_LEVEL_POLICY_RELEASE_ID, RECORD_LEVEL_POLICY_SHA256, RecordLevelBindingPolicy,
    numeric_rule_resolver_release_hash, official_positive_f08_numeric_rules_available,
    validate_consumed_value_provenance_v1_2, validate_f08_freshness_provenance_v1_2,
    validate_record_level_consumed_scope_v1_2, verify_control_fix_asset_bindings,
)
from tools.m3top3.tests.test_model_v1 import record

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
CONFIG_PATH=HERE.parent/"configs"/"m3top3_v1.0.json"
FW=json.loads(CONFIG_PATH.read_text())["feature_weights"]

def ev(ref, cutoff="2026-08-14T18:00:00+09:00"):
    return {"evidence_ref":ref,"content_sha256":hashlib.sha256(ref.encode()).hexdigest(),
            "persistent_locator":f"synthetic://{ref}","source_lineage":[f"SYN:{ref}"],
            "supported_cutoff_at":cutoff}

def bindings(r, objs):
    p=RecordLevelBindingPolicy.load(ROOT); out={}
    for path in ("company_id","snapshot_cutoff_at","window_anchor_date"):
        out[path]={"binding_type":"EXPLICIT_CONTROL_IDENTITY_EXEMPTION",
                   "policy_release_id":RECORD_LEVEL_POLICY_RELEASE_ID,
                   "policy_sha256":RECORD_LEVEL_POLICY_SHA256,
                   "classification":p.classifications[path]}
    ref=f"ELIG:{r['company_id']}"; objs[ref]=ev(ref,"2026-08-14T08:00:00+09:00")
    out["eligibility_state"]={"binding_type":"GOVERNED_RELEASE_EVIDENCE",
        "policy_release_id":RECORD_LEVEL_POLICY_RELEASE_ID,"policy_sha256":RECORD_LEVEL_POLICY_SHA256,
        "classification":p.classifications["eligibility_state"],"value":r["eligibility_state"],
        "effective_at":"2026-08-14T08:00:00+09:00","governed_release_ref":ref}
    if r.get("hard_risk_gate"):
        g=r["hard_risk_gate"]; ref=f"GATE:{r['company_id']}"; objs[ref]=ev(ref,"2026-08-14T09:00:00+09:00")
        for path in ("hard_risk_gate.state","hard_risk_gate.event_group_id","hard_risk_gate.evidence_status","hard_risk_gate.reason"):
            key=path.split(".")[-1]
            out[path]={"binding_type":"GOVERNED_EVIDENCE","policy_release_id":RECORD_LEVEL_POLICY_RELEASE_ID,
                "policy_sha256":RECORD_LEVEL_POLICY_SHA256,"classification":p.classifications[path],
                "value":g[key],"effective_at":"2026-08-14T09:00:00+09:00","immutable_evidence_ref":ref}
        g["pit_provenance"]={"immutable_evidence_ref":ref,"publication_at":"2026-08-14T09:00:00+09:00"}
    return out

def certify(r, objs):
    reg=FeatureInputRegistry.load(ROOT); certs={}
    for fid, block in r["feature_raw_inputs"].items():
        ref=f"F:{r['company_id']}:{fid}"; objs[ref]=ev(ref); cid=f"C:{r['company_id']}:{fid}"
        c={"certification_id":cid,"certification_version":"v1","feature_id":fid,
           "applicable_model_version":"M3TOP3-v1.0",
           "applicable_feature_schema_version":"M3TOP3-FEATURE-SCHEMA_v1.0_WORKING",
           "feature_block_hash":whole_block_payload_hash(block),
           "authoritative_scope_contract_id":FEATURE_INPUT_REGISTRY_RELEASE_ID,
           "authoritative_scope_contract_hash":FEATURE_INPUT_REGISTRY_SHA256,
           "certified_scope":list(reg.resolve_feature_paths(fid,block)),
           "supported_cutoff_at":"2026-08-14T18:00:00+09:00",
           "immutable_evidence_refs":[ref],"persistent_locator":f"synthetic://{cid}"}
        h=certification_content_hash(c); c["certification_content_hash"]=h; certs[cid]=h
        block["whole_block_certification"]=c
    return certs

def add_f08(r, objs, penalty=10):
    f=r["feature_raw_inputs"]["F08_EVIDENCE_RELIABILITY"]; target=next(iter(f["feature_evidence"]))
    ref=f"FR:{r['company_id']}:{target}"; objs[ref]=ev(ref,"2026-08-14T17:00:00+09:00")
    f["feature_evidence"][target].update({"freshness_penalty":penalty,
        "refresh_rule_id":"SYN-NUMERIC-FRESHNESS-RULE-v1","source_or_evidence_class":"SYN_PRIMARY",
        "supported_cutoff_ref":ref,"supported_cutoff_at":"2026-08-14T17:00:00+09:00",
        "evaluated_for_snapshot_cutoff_at":"2026-08-14T23:00:00+09:00",
        "evaluation_run_at":"2026-08-16T02:00:00+09:00"})
    return target

def numrule(target, penalty=10):
    x={"refresh_rule_id":"SYN-NUMERIC-FRESHNESS-RULE-v1","registry_release_id":REFRESH_REGISTRY_RELEASE_ID,
       "registry_sha256":REFRESH_REGISTRY_SHA256,"applicable_scope":[target],
       "applicable_source_or_evidence_class":"SYN_PRIMARY","freshness_determination_method":"SYN",
       "stale_state_method":"SYN","effective_model_version":"M3TOP3-v1.0","rule_status":"ACTIVE",
       "penalty_value":penalty}
    x["governance_object_sha256"]=typed_governance_object_hash(x); return x

class TestAssets(unittest.TestCase):
    def test_assets_and_baseline(self):
        self.assertEqual(len(verify_control_fix_asset_bindings(ROOT)),3)
        self.assertEqual(len(verify_shared_asset_bindings(ROOT)),6)
        self.assertEqual(hashlib.sha256(CONFIG_PATH.read_bytes()).hexdigest(),
            "eecde22a7744cff505c624bb6f0bdb11714352a122632238ea68d9cd0fbacb98")
        self.assertFalse(official_positive_f08_numeric_rules_available(ROOT))

class TestCW01(unittest.TestCase):
    def test_a1_unbound_mapping_fails(self):
        with self.assertRaises(SharedInterfaceGuardError):
            validate_consumed_value_provenance_v1_2(record(1),evidence_resolver={"X":{}},
                record_level_bindings={},repo_root=ROOT) # type: ignore[arg-type]
    def test_a2_missing_hash_fails(self):
        o=ev("E");o.pop("content_sha256");r=EvidenceResolverRelease.synthetic({"E":o})
        with self.assertRaises(SharedInterfaceGuardError): r.resolve("E",cutoff_at="2026-08-14T23:59:59+09:00")
    def test_a3_missing_locator_fails(self):
        o=ev("E");o.pop("persistent_locator");r=EvidenceResolverRelease.synthetic({"E":o})
        with self.assertRaises(SharedInterfaceGuardError): r.resolve("E",cutoff_at="2026-08-14T23:59:59+09:00")
    def test_a4_missing_lineage_fails(self):
        o=ev("E");o.pop("source_lineage");r=EvidenceResolverRelease.synthetic({"E":o})
        with self.assertRaises(SharedInterfaceGuardError): r.resolve("E",cutoff_at="2026-08-14T23:59:59+09:00")
    def test_a5_resolver_hash_mismatch_fails(self):
        r=EvidenceResolverRelease("BAD","v1","synthetic://bad",{"E":ev("E")},"0"*64,True)
        with self.assertRaises(SharedInterfaceGuardError): r.validate_binding(ROOT,allow_test_resolver=True)
    def test_a6_whole_block_caller_membership_fails(self):
        r=record(1);o={};c=certify(r,o)
        with self.assertRaises(SharedInterfaceGuardError):
            validate_consumed_value_provenance_v1_2(r,evidence_resolver=o,record_level_bindings={},
                certification_resolver=c,repo_root=ROOT) # type: ignore[arg-type]
    def test_a7_f02_upstream_unbound_mapping_fails(self):
        r=record(1);r["feature_raw_inputs"]={"F02_NUMERIC_BUSINESS_INFLECTION":{"metric_changes":{"revenue":{
            "value":.2,"operator_id":"OP","derivation_id":"D","derivation_version":"v1"}}}}
        with self.assertRaises(SharedInterfaceGuardError):
            validate_consumed_value_provenance_v1_2(r,evidence_resolver={"UP":{}},
                record_level_bindings={},repo_root=ROOT) # type: ignore[arg-type]
    def test_a8_valid_synthetic_combined_passes(self):
        r=record(1);o={};b=bindings(r,o);c=certify(r,o);e=EvidenceResolverRelease.synthetic(o)
        out=validate_consumed_value_provenance_v1_2(r,evidence_resolver=e,record_level_bindings=b,
            certification_resolver=c,repo_root=ROOT,allow_test_resolver=True)
        self.assertIn("eligibility_state",out["record_level_paths"])
    def test_a9_official_runtime_rejects_test_resolver(self):
        r=record(1);o={};b=bindings(r,o);e=EvidenceResolverRelease.synthetic(o)
        with self.assertRaises(SharedInterfaceGuardError):
            score_official_snapshot_records_v1_1([r],code_identity="T",validation_dataset_release_id="V",
                denominator_policy_version="D",evidence_resolver=e,
                record_level_bindings_by_company={r["company_id"]:b},repo_root=ROOT)

class TestCW02(unittest.TestCase):
    def test_b1_caller_rule_mapping_fails(self):
        r=record(1);o={};t=add_f08(r,o);e=EvidenceResolverRelease.synthetic(o);rule=numrule(t)
        with self.assertRaises(SharedInterfaceGuardError):
            validate_f08_freshness_provenance_v1_2(r,evidence_resolver=e,
                numeric_rule_resolver={rule["refresh_rule_id"]:rule},repo_root=ROOT,
                allow_test_resolver=True) # type: ignore[arg-type]
    def test_b2_no_numeric_resolver_fails(self):
        r=record(1);o={};add_f08(r,o);e=EvidenceResolverRelease.synthetic(o)
        with self.assertRaises(SharedInterfaceGuardError):
            validate_f08_freshness_provenance_v1_2(r,evidence_resolver=e,repo_root=ROOT,
                allow_test_resolver=True)
    def test_b3_nonapproved_self_consistent_resolver_fails_official(self):
        r=record(1);o={};t=add_f08(r,o);rule=numrule(t);rules={rule["refresh_rule_id"]:rule}
        rid,ver,loc="CALLER","v1","caller://numeric"
        n=NumericRuleResolverRelease(rid,ver,loc,rules,numeric_rule_resolver_release_hash(rid,ver,loc,rules),False)
        with self.assertRaises(SharedInterfaceGuardError): n.validate_binding(ROOT)
    def test_b4_synthetic_passes_test_only_and_caps_20(self):
        r=record(1);o={};t=add_f08(r,o,30);e=EvidenceResolverRelease.synthetic(o);rule=numrule(t,30)
        n=NumericRuleResolverRelease.synthetic({rule["refresh_rule_id"]:rule})
        validate_f08_freshness_provenance_v1_2(r,evidence_resolver=e,numeric_rule_resolver=n,
            repo_root=ROOT,allow_test_resolver=True)
        with self.assertRaises(SharedInterfaceGuardError): n.validate_binding(ROOT)
        fmap=FeatureEngineV1NarrowPatch(FW).compute_snapshot([r])[r["company_id"]]["features"]
        self.assertEqual(fmap["F08_EVIDENCE_RELIABILITY"]["trace"]["feature_evidence"][t]["freshness_penalty"],"20")

class TestCW03(unittest.TestCase):
    def test_c1_missing_eligibility_binding_fails(self):
        r=record(1);o={};b=bindings(r,o);b.pop("eligibility_state");e=EvidenceResolverRelease.synthetic(o)
        with self.assertRaises(SharedInterfaceGuardError):
            validate_record_level_consumed_scope_v1_2(r,record_level_bindings=b,evidence_resolver=e,
                repo_root=ROOT,allow_test_resolver=True)
    def test_c2_missing_control_exemption_fails(self):
        r=record(1);o={};b=bindings(r,o);b.pop("company_id");e=EvidenceResolverRelease.synthetic(o)
        with self.assertRaises(SharedInterfaceGuardError):
            validate_record_level_consumed_scope_v1_2(r,record_level_bindings=b,evidence_resolver=e,
                repo_root=ROOT,allow_test_resolver=True)
    def test_c3_valid_binding_passes(self):
        r=record(1);o={};b=bindings(r,o);e=EvidenceResolverRelease.synthetic(o)
        p=validate_record_level_consumed_scope_v1_2(r,record_level_bindings=b,evidence_resolver=e,
            repo_root=ROOT,allow_test_resolver=True)
        self.assertEqual(set(p),{"company_id","eligibility_state","snapshot_cutoff_at","window_anchor_date"})
    def test_c4_hard_gate_binding_passes(self):
        r=record(4);o={};b=bindings(r,o);e=EvidenceResolverRelease.synthetic(o)
        p=validate_record_level_consumed_scope_v1_2(r,record_level_bindings=b,evidence_resolver=e,
            repo_root=ROOT,allow_test_resolver=True)
        self.assertIn("hard_risk_gate.state",p)

if __name__=="__main__": unittest.main()
