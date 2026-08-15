from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from tools.m3top3.features_v1_narrow_patch import FeatureEngineV1NarrowPatch
from tools.m3top3.official_runtime_v1 import score_official_snapshot_records
from tools.m3top3.release_vdi_v1 import MANDATORY_AXES, validate_official_coverage_release
from tools.m3top3.scorer_v1 import M3Top3V1Engine
from tools.m3top3.shared_interface_guards_v1 import SharedInterfaceGuardError
from tools.m3top3.shared_interface_guards_v1_1 import (
    BOUND_SHARED_ASSETS,
    FEATURE_INPUT_REGISTRY_RELEASE_ID,
    FEATURE_INPUT_REGISTRY_SHA256,
    REFRESH_REGISTRY_RELEASE_ID,
    REFRESH_REGISTRY_SHA256,
    FeatureInputRegistry,
    certification_content_hash,
    typed_governance_object_hash,
    validate_consumed_value_provenance_v1_1,
    validate_f08_freshness_provenance_v1_1,
    verify_shared_asset_bindings,
    whole_block_payload_hash,
)
from tools.m3top3.tests.test_model_v1 import record

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
CONFIG = json.loads((HERE.parent / "configs" / "m3top3_v1.0.json").read_text(encoding="utf-8"))
FW = CONFIG["feature_weights"]


def _add_f02_derivation_metadata(r: dict) -> None:
    f02 = r["feature_raw_inputs"].get("F02_NUMERIC_BUSINESS_INFLECTION") or {}
    for metric, spec in (f02.get("metric_changes") or {}).items():
        if not isinstance(spec, dict):
            continue
        spec.setdefault("derivation_id", f"SYN-{metric}-DERIVATION")
        spec.setdefault("derivation_version", "v1")


def _certify_record(r: dict):
    _add_f02_derivation_metadata(r)
    registry = FeatureInputRegistry.load(REPO_ROOT)
    evidence_resolver: dict[str, dict] = {}
    certification_resolver: dict[str, str] = {}
    for fid, block in r["feature_raw_inputs"].items():
        if not isinstance(block, dict):
            continue
        scope = registry.resolve_feature_paths(fid, block)
        evidence_ref = f"IMMUTABLE-EVIDENCE:{r['company_id']}:{fid}"
        evidence_resolver[evidence_ref] = {"status": "RESOLVED"}
        cert_id = f"CERT:{r['company_id']}:{fid}"
        cert = {
            "certification_id": cert_id,
            "certification_version": "v1",
            "feature_id": fid,
            "applicable_model_version": "M3TOP3-v1.0",
            "applicable_feature_schema_version": "M3TOP3-FEATURE-SCHEMA_v1.0_WORKING",
            "feature_block_hash": whole_block_payload_hash(block),
            "authoritative_scope_contract_id": FEATURE_INPUT_REGISTRY_RELEASE_ID,
            "authoritative_scope_contract_hash": FEATURE_INPUT_REGISTRY_SHA256,
            "certified_scope": list(scope),
            "supported_cutoff_at": "2026-08-14T20:00:00+09:00",
            "immutable_evidence_refs": [evidence_ref],
            "persistent_locator": f"synthetic://{cert_id}",
        }
        cert_hash = certification_content_hash(cert)
        cert["certification_content_hash"] = cert_hash
        certification_resolver[cert_id] = cert_hash
        block["whole_block_certification"] = cert
    gate = r.get("hard_risk_gate") or {}
    if gate.get("state") and gate.get("state") != "NONE":
        ref = f"IMMUTABLE-GATE:{r['company_id']}"
        evidence_resolver[ref] = {"status": "RESOLVED"}
        gate["pit_provenance"] = {
            "immutable_evidence_ref": ref,
            "publication_at": "2026-08-14T19:00:00+09:00",
        }
    return evidence_resolver, certification_resolver


def _typed_refresh_rule(target: str, penalty: float = 30.0, *, registry_sha: str = REFRESH_REGISTRY_SHA256, scope=None):
    rule = {
        "refresh_rule_id": "SYN-NUMERIC-FRESHNESS-RULE-v1",
        "registry_release_id": REFRESH_REGISTRY_RELEASE_ID,
        "registry_sha256": registry_sha,
        "applicable_scope": [target] if scope is None else scope,
        "applicable_source_or_evidence_class": "SYN_PRIMARY",
        "freshness_determination_method": "SYNTHETIC_PREDECLARED_RULE",
        "stale_state_method": "SYNTHETIC_FIXED_STATE",
        "effective_model_version": "M3TOP3-v1.0",
        "rule_status": "ACTIVE",
        "penalty_value": penalty,
    }
    rule["governance_object_sha256"] = typed_governance_object_hash(rule)
    return rule


def _add_positive_freshness(r: dict, *, penalty: float = 30.0, support_time: str = "2026-08-14T18:00:00+09:00"):
    f08 = r["feature_raw_inputs"]["F08_EVIDENCE_RELIABILITY"]
    target = next(iter(f08["feature_evidence"]))
    support_ref = f"FRESH-EVIDENCE:{r['company_id']}:{target}"
    f08["feature_evidence"][target].update(
        {
            "freshness_penalty": penalty,
            "refresh_rule_id": "SYN-NUMERIC-FRESHNESS-RULE-v1",
            "source_or_evidence_class": "SYN_PRIMARY",
            "supported_cutoff_ref": support_ref,
            "supported_cutoff_at": support_time,
            "evaluated_for_snapshot_cutoff_at": "2026-08-14T23:00:00+09:00",
            "evaluation_run_at": "2026-08-16T01:30:00+09:00",
        }
    )
    return target, support_ref


def _release_validation(rows):
    scorer = M3Top3V1Engine(CONFIG, "SHARED-WIRING-TEST")
    result = scorer.score_snapshot(rows)
    pass_map = {r["company_id"]: True for r in rows if r["eligibility_state"] == "ELIGIBLE"}
    return result, validate_official_coverage_release(
        result,
        validation_dataset_release_id="SYN-VDI-v1",
        denominator_policy_version="SYN-DENOM-v1",
        pit_validation_passed=pass_map,
        freshness_validation_passed=pass_map,
    )


class TestSharedAssetBindings(unittest.TestCase):
    def test_00_all_six_shared_assets_rehash_and_git_blob_pass(self):
        report = verify_shared_asset_bindings(REPO_ROOT)
        self.assertEqual(len(report), 6)
        self.assertEqual(set(report), {a.path for a in BOUND_SHARED_ASSETS})
        self.assertTrue(all(v["status"] == "PASS" for v in report.values()))


class TestPitConsumedScopeWiring(unittest.TestCase):
    def test_01_self_declared_consumed_fields_cannot_omit_actual_consumed_path(self):
        r = record(1)
        r["feature_raw_inputs"] = {
            "F01_COMMERCIAL_CONVERSION_MOMENTUM": {
                "commercial_state": "QUALIFICATION_ACCEPTANCE_OR_FIRST_VOLUME_ORDER",
                "latest_positive_transition_at": "2026-08-01T09:00:00+09:00",
                "consumed_fields": ["latest_positive_transition_at"],
                "consumed_value_provenance": {
                    "latest_positive_transition_at": {
                        "immutable_evidence_ref": "E1",
                        "publication_at": "2026-08-01T09:00:00+09:00",
                    }
                },
            }
        }
        with self.assertRaises(SharedInterfaceGuardError):
            validate_consumed_value_provenance_v1_1(r, evidence_resolver={"E1": {}}, repo_root=REPO_ROOT)

    def test_02_no_bound_authoritative_registry_fails(self):
        r = record(1)
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises((SharedInterfaceGuardError, FileNotFoundError)):
                validate_consumed_value_provenance_v1_1(r, evidence_resolver={}, repo_root=td)

    def test_03_whole_block_certificate_hash_mismatch_fails(self):
        r = record(1)
        evidence, certs = _certify_record(r)
        f01 = r["feature_raw_inputs"]["F01_COMMERCIAL_CONVERSION_MOMENTUM"]
        f01["whole_block_certification"]["feature_block_hash"] = "bad"
        with self.assertRaises(SharedInterfaceGuardError):
            validate_consumed_value_provenance_v1_1(r, evidence_resolver=evidence, certification_resolver=certs, repo_root=REPO_ROOT)

    def test_04_scope_contract_hash_mismatch_fails(self):
        r = record(1)
        evidence, certs = _certify_record(r)
        f01 = r["feature_raw_inputs"]["F01_COMMERCIAL_CONVERSION_MOMENTUM"]
        f01["whole_block_certification"]["authoritative_scope_contract_hash"] = "bad"
        with self.assertRaises(SharedInterfaceGuardError):
            validate_consumed_value_provenance_v1_1(r, evidence_resolver=evidence, certification_resolver=certs, repo_root=REPO_ROOT)

    def test_05_certificate_subset_scope_fails(self):
        r = record(1)
        evidence, certs = _certify_record(r)
        f01 = r["feature_raw_inputs"]["F01_COMMERCIAL_CONVERSION_MOMENTUM"]
        f01["whole_block_certification"]["certified_scope"] = []
        with self.assertRaises(SharedInterfaceGuardError):
            validate_consumed_value_provenance_v1_1(r, evidence_resolver=evidence, certification_resolver=certs, repo_root=REPO_ROOT)

    def test_06_unresolved_immutable_evidence_reference_fails(self):
        r = record(1)
        evidence, certs = _certify_record(r)
        fid = "F01_COMMERCIAL_CONVERSION_MOMENTUM"
        r["feature_raw_inputs"][fid]["whole_block_certification"]["immutable_evidence_refs"] = ["MISSING-REF"]
        cert = r["feature_raw_inputs"][fid]["whole_block_certification"]
        cert["certification_content_hash"] = certification_content_hash(cert)
        certs[cert["certification_id"]] = cert["certification_content_hash"]
        with self.assertRaises(SharedInterfaceGuardError):
            validate_consumed_value_provenance_v1_1(r, evidence_resolver=evidence, certification_resolver=certs, repo_root=REPO_ROOT)

    def test_07_derived_aggregate_operator_without_upstream_lineage_fails(self):
        r = record(1)
        r["feature_raw_inputs"] = {
            "F02_NUMERIC_BUSINESS_INFLECTION": {
                "metric_changes": {
                    "revenue": {
                        "value": 0.2,
                        "operator_id": "UPSTREAM-OP-v1",
                        "derivation_id": "REV-CHANGE",
                        "derivation_version": "v1",
                    }
                },
                "consumed_value_provenance": {
                    "metric_changes.revenue.value": {
                        "immutable_evidence_ref": "E-AGG",
                        "publication_at": "2026-08-14T10:00:00+09:00",
                        "operator_id": "UPSTREAM-OP-v1",
                        "derivation_id": "REV-CHANGE",
                        "derivation_version": "v1",
                    }
                },
            }
        }
        with self.assertRaises(SharedInterfaceGuardError):
            validate_consumed_value_provenance_v1_1(r, evidence_resolver={"E-AGG": {}}, repo_root=REPO_ROOT)

    def test_08_valid_whole_block_certification_passes(self):
        r = record(1)
        evidence, certs = _certify_record(r)
        resolved = validate_consumed_value_provenance_v1_1(r, evidence_resolver=evidence, certification_resolver=certs, repo_root=REPO_ROOT)
        self.assertEqual(set(resolved), set(r["feature_raw_inputs"]))


class TestF08FreshnessWiring(unittest.TestCase):
    def test_09_arbitrary_refresh_rule_string_without_resolution_fails(self):
        r = record(1)
        target, support_ref = _add_positive_freshness(r, penalty=10)
        with self.assertRaises(SharedInterfaceGuardError):
            validate_f08_freshness_provenance_v1_1(r, typed_refresh_rules={}, evidence_resolver={support_ref: {}}, repo_root=REPO_ROOT)

    def test_10_wrong_refresh_registry_sha_fails(self):
        r = record(1)
        target, support_ref = _add_positive_freshness(r, penalty=10)
        rule = _typed_refresh_rule(target, penalty=10, registry_sha="bad")
        with self.assertRaises(SharedInterfaceGuardError):
            validate_f08_freshness_provenance_v1_1(r, typed_refresh_rules={rule["refresh_rule_id"]: rule}, evidence_resolver={support_ref: {}}, repo_root=REPO_ROOT)

    def test_11_refresh_rule_scope_mismatch_fails(self):
        r = record(1)
        target, support_ref = _add_positive_freshness(r, penalty=10)
        rule = _typed_refresh_rule(target, penalty=10, scope=["OTHER-FEATURE"])
        with self.assertRaises(SharedInterfaceGuardError):
            validate_f08_freshness_provenance_v1_1(r, typed_refresh_rules={rule["refresh_rule_id"]: rule}, evidence_resolver={support_ref: {}}, repo_root=REPO_ROOT)

    def test_12_historical_support_after_snapshot_fails(self):
        r = record(1)
        target, support_ref = _add_positive_freshness(r, penalty=10, support_time="2026-08-15T00:00:00+09:00")
        rule = _typed_refresh_rule(target, penalty=10)
        with self.assertRaises(SharedInterfaceGuardError):
            validate_f08_freshness_provenance_v1_1(r, typed_refresh_rules={rule["refresh_rule_id"]: rule}, evidence_resolver={support_ref: {}}, repo_root=REPO_ROOT)

    def test_13_late_evaluation_runtime_with_valid_historical_asof_passes(self):
        r = record(1)
        target, support_ref = _add_positive_freshness(r, penalty=10)
        rule = _typed_refresh_rule(target, penalty=10)
        validate_f08_freshness_provenance_v1_1(r, typed_refresh_rules={rule["refresh_rule_id"]: rule}, evidence_resolver={support_ref: {}}, repo_root=REPO_ROOT)

    def test_14_governed_penalty_over_20_passes_guard_and_arithmetic_caps_20(self):
        r = record(1)
        target, support_ref = _add_positive_freshness(r, penalty=30)
        rule = _typed_refresh_rule(target, penalty=30)
        validate_f08_freshness_provenance_v1_1(r, typed_refresh_rules={rule["refresh_rule_id"]: rule}, evidence_resolver={support_ref: {}}, repo_root=REPO_ROOT)
        fmap = FeatureEngineV1NarrowPatch(FW).compute_snapshot([r])[r["company_id"]]["features"]
        self.assertEqual(fmap["F08_EVIDENCE_RELIABILITY"]["trace"]["feature_evidence"][target]["freshness_penalty"], "20")


class TestCoverageReleaseWiring(unittest.TestCase):
    def test_15_only_one_axis_available_not_official_rankable(self):
        r = record(1)
        r["feature_raw_inputs"] = {"F05_MARKET_POSITIONING_BALANCE": r["feature_raw_inputs"]["F05_MARKET_POSITIONING_BALANCE"]}
        _, vdi = _release_validation([r])
        self.assertEqual(vdi["release_rankability_status"], "BLOCKED_INCOMPLETE_POLICY_COVERAGE")
        self.assertFalse(vdi["per_company"][0]["all_mandatory_axes_calculable"])

    def test_16_reliability_axis_absent_not_official_rankable(self):
        r = record(1)
        r["feature_raw_inputs"].pop("F08_EVIDENCE_RELIABILITY")
        r["feature_raw_inputs"].pop("F09_EXECUTION_THESIS_SAFETY")
        _, vdi = _release_validation([r])
        self.assertEqual(vdi["release_rankability_status"], "BLOCKED_INCOMPLETE_POLICY_COVERAGE")

    def test_17_all_five_axes_some_governed_missing_features_provisional_allowed(self):
        r = record(1)
        for fid in ("F02_NUMERIC_BUSINESS_INFLECTION", "F04_EVENT_SURPRISE_VS_PRIOR_EXPECTATION", "F07_BETA_TRANSMISSION_ALIGNMENT", "F08_EVIDENCE_RELIABILITY"):
            r["feature_raw_inputs"].pop(fid)
        result, vdi = _release_validation([r])
        output = result["outputs"][0]
        self.assertEqual(output["score_status"], "PROVISIONAL_MISSING_FEATURES")
        self.assertEqual(vdi["release_rankability_status"], "OFFICIAL_RANKABLE")
        self.assertTrue(vdi["per_company"][0]["provisional_ranking_allowed"])

    def test_18_any_review_required_feature_blocks_official_rankability(self):
        r = record(1)
        r["feature_raw_inputs"]["F02_NUMERIC_BUSINESS_INFLECTION"] = {
            "availability_state": "REVIEW_REQUIRED",
            "missing_reason": "synthetic unresolved adjudication",
        }
        _, vdi = _release_validation([r])
        self.assertEqual(vdi["release_rankability_status"], "BLOCKED_INCOMPLETE_POLICY_COVERAGE")
        self.assertTrue(vdi["per_company"][0]["review_required_present"])

    def test_19_na_for_overlap_allowed_if_all_five_axes_survive(self):
        r = record(1)
        shared = "SAME-ECONOMIC-FACT"
        r["feature_raw_inputs"]["F01_COMMERCIAL_CONVERSION_MOMENTUM"]["event_group_ids"] = [shared]
        r["feature_raw_inputs"]["F02_NUMERIC_BUSINESS_INFLECTION"]["event_group_ids"] = [shared]
        result, vdi = _release_validation([r])
        self.assertEqual(result["outputs"][0]["feature_trace"]["F02_NUMERIC_BUSINESS_INFLECTION"]["availability_state"], "NA_FOR_OVERLAP")
        self.assertEqual(vdi["release_rankability_status"], "OFFICIAL_RANKABLE")

    def test_20_company_coverage_one_does_not_claim_feature_completeness(self):
        rows = [record(1), record(2)]
        for r in rows:
            for fid in ("F02_NUMERIC_BUSINESS_INFLECTION", "F04_EVENT_SURPRISE_VS_PRIOR_EXPECTATION", "F07_BETA_TRANSMISSION_ALIGNMENT", "F08_EVIDENCE_RELIABILITY"):
                r["feature_raw_inputs"].pop(fid)
        _, vdi = _release_validation(rows)
        self.assertEqual(vdi["company_rankability_coverage"], "1")
        self.assertTrue(vdi["feature_completeness_is_not_company_coverage"])
        self.assertTrue(any(float(c["feature_coverage_ratio"]) < 1.0 for c in vdi["per_company"]))
        self.assertEqual(set(vdi["mandatory_axes"]), set(MANDATORY_AXES))


class TestOfficialRuntimeIntegration(unittest.TestCase):
    def test_21_official_runtime_binds_shared_assets_pit_coverage_and_f02_note(self):
        rows = [record(1), record(2)]
        evidence: dict[str, dict] = {}
        certs: dict[str, str] = {}
        for r in rows:
            e, c = _certify_record(r)
            evidence.update(e)
            certs.update(c)
        out = score_official_snapshot_records(
            rows,
            code_identity="SHARED-WIRING-INTEGRATION-TEST",
            validation_dataset_release_id="SYN-VDI-v1",
            denominator_policy_version="SYN-DENOM-v1",
            evidence_resolver=evidence,
            certification_resolver=certs,
            typed_refresh_rules={},
            repo_root=REPO_ROOT,
        )
        self.assertEqual(out["vdi_release_validation"]["release_rankability_status"], "OFFICIAL_RANKABLE")
        self.assertEqual(len(out["shared_asset_binding"]), 6)
        self.assertEqual(out["f02_compatibility_note_binding"]["status"], "PASS")
        self.assertFalse(out["actual_replay_authorized"])
        self.assertFalse(out["model_freeze_authorized"])


if __name__ == "__main__":
    unittest.main()
