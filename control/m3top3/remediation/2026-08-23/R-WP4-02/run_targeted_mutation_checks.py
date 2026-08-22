from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Mutation:
    mutation_id: str
    path: str
    old: str
    new: str
    paired_test: str


MUTATIONS = [
    Mutation("MUT-PIT-MISSING-KEY", "tools/m3top3/pit_guard.py", 'violations.append(GuardViolation("MISSING_PUBLICATION_AT", "historical feature/evidence row requires publication_at", "publication_at"))', 'pass  # MUTATION: missing-key guard removed', "tools.m3top3.tests.test_known_failures_pit.KnownFailurePITTests.test_kf_pit_001_missing_publication_key"),
    Mutation("MUT-PIT-NULL", "tools/m3top3/pit_guard.py", 'violations.append(GuardViolation("MISSING_PUBLICATION_AT", f"missing publication datetime at {path}", path))', 'pass  # MUTATION: null-publication guard removed', "tools.m3top3.tests.test_known_failures_pit.KnownFailurePITTests.test_kf_pit_001_null_publication"),
    Mutation("MUT-PIT-NAIVE", "tools/m3top3/pit_guard.py", 'violations.append(GuardViolation("INVALID_PUBLICATION_DATETIME", f"invalid timezone-aware publication datetime at {path}", path))', 'pass  # MUTATION: timezone guard removed', "tools.m3top3.tests.test_known_failures_pit.KnownFailurePITTests.test_kf_pit_002_naive_publication_string"),
    Mutation("MUT-PIT-AVAILABLE", "tools/m3top3/pit_guard.py", 'if lk == "available_before_entry" and value is False:', 'if False and lk == "available_before_entry" and value is False:', "tools.m3top3.tests.test_known_failures_pit.KnownFailurePITTests.test_kf_pit_003_not_available_before_entry"),
    Mutation("MUT-PIT-CURRENT", "tools/m3top3/pit_guard.py", 'if lk == "current_only" and value is True:', 'if False and lk == "current_only" and value is True:', "tools.m3top3.tests.test_known_failures_pit.KnownFailurePITTests.test_kf_pit_004_current_only"),
    Mutation("MUT-PIT-CONSUMED-PUB", "tools/m3top3/pit_guard.py", 'if parse_datetime(value) > cutoff:\n                            violations.append(GuardViolation("PIT_PUBLICATION_AFTER_CUTOFF"', 'if False:\n                            violations.append(GuardViolation("PIT_PUBLICATION_AFTER_CUTOFF"', "tools.m3top3.tests.test_known_failures_pit.KnownFailurePITTests.test_kf_pit_005_consumed_future_row_blocks"),
    Mutation("MUT-PIT-CONSUMED-EFFECTIVE", "tools/m3top3/pit_guard.py", 'if parse_datetime(value) > cutoff:\n                        violations.append(GuardViolation("PIT_EFFECTIVE_AFTER_CUTOFF"', 'if False:\n                        violations.append(GuardViolation("PIT_EFFECTIVE_AFTER_CUTOFF"', "tools.m3top3.tests.test_known_failures_pit.KnownFailurePITTests.test_kf_pit_006_consumed_effective_after_cutoff_blocks"),
    Mutation("MUT-SNAPSHOT-STATUS", "tools/m3top3/admission.py", 'if status != "SNAPSHOT_READY":', 'if False and status != "SNAPSHOT_READY":', "tools.m3top3.tests.test_known_failures_snapshot.KnownFailureSnapshotTests.test_kf_snp_002_partial_manifest_blocked_before_scorer"),
    Mutation("MUT-SNAPSHOT-BLOCKERS", "tools/m3top3/admission.py", 'if status == "SNAPSHOT_READY" and blockers:', 'if False and status == "SNAPSHOT_READY" and blockers:', "tools.m3top3.tests.test_known_failures_snapshot.KnownFailureSnapshotTests.test_kf_snp_004_ready_with_blocker_is_contradiction"),
    Mutation("MUT-MODEL-HASH", "tools/m3top3/admission.py", 'if manifest.get("model_input_file_sha256") != actual_model_hash:', 'if False and manifest.get("model_input_file_sha256") != actual_model_hash:', "tools.m3top3.tests.test_known_failures_integrity.KnownFailureIntegrityTests.test_kf_int_002_model_input_valid_json_mutation"),
    Mutation("MUT-RETRIEVAL-AUDIT-HASH", "tools/m3top3/admission.py", 'if manifest.get("retrieval_audit_file_sha256") != actual_audit_hash:', 'if False and manifest.get("retrieval_audit_file_sha256") != actual_audit_hash:', "tools.m3top3.tests.test_known_failures_integrity.KnownFailureIntegrityTests.test_retrieval_audit_valid_json_mutation_is_detected"),
    Mutation("MUT-RETRIEVAL-AUDIT-RECONCILIATION", "tools/m3top3/admission.py", 'if source_matching_rows != selected_rows + excluded_rows:', 'if False:', "tools.m3top3.tests.test_known_failures_integrity.KnownFailureIntegrityTests.test_self_consistent_forged_retrieval_counts_are_rejected"),
    Mutation("MUT-PRICE-HASH", "tools/m3top3/admission.py", 'if (\n        not actual_hash', 'if False and (\n        not actual_hash', "tools.m3top3.tests.test_known_failures_price.KnownFailurePriceTests.test_post_construction_price_byte_mutation_is_rejected_before_read"),
    Mutation("MUT-OHLC", "tools/m3top3/providers.py", 'if any(value <= 0 for value in prices) or row.high < max(row.open,row.close) or row.low > min(row.open,row.close) or row.low > row.high:', 'if False:', "tools.m3top3.tests.test_known_failures_price.KnownFailurePriceTests.test_kf_prc_004_high_below_open_or_close"),
    Mutation("MUT-RESULT-IMMUTABLE", "tools/m3top3/ledger.py", 'if prior != payload:\n                raise M3Top3AdmissionError(\n                    "NONDETERMINISTIC_RERUN"', 'if False:\n                raise M3Top3AdmissionError(\n                    "NONDETERMINISTIC_RERUN"', "tools.m3top3.tests.test_known_failures_immutability.KnownFailureImmutabilityTests.test_kf_imm_003_same_run_id_different_result_is_rejected"),
    Mutation("MUT-CLI-BLOCKED", "tools/m3top3/cli_run_backtest.py", 'if blocked or len(results)!=len(snapshot_dirs): return EXIT_BLOCKED', 'if False: return EXIT_BLOCKED', "tools.m3top3.tests.test_known_failures_cli.KnownFailureCLITests.test_kf_cli_001_blocked_tie_returns_two_and_no_output"),
    Mutation("MUT-OFFICIAL-GLOBAL-KILL", "tools/m3top3/admission.py", 'if not OFFICIAL_EXECUTION_ENABLED:', 'if False:', "tools.m3top3.tests.test_known_failures_model_admission.KnownFailureModelAdmissionTests.test_kf_mod_002_diagnostic_scorer_denied_in_official_mode"),
    Mutation("MUT-PRICE-COMPONENT-MANIFEST", "tools/m3top3/admission.py", 'if len(components)<=1:', 'if True:', "tools.m3top3.tests.test_known_failures_price.KnownFailurePriceTests.test_multi_component_price_requires_versioned_byte_manifest"),
    Mutation("MUT-PRICE-SEMANTICS-ALLOWLIST", "tools/m3top3/admission.py", 'if semantics not in ALLOWED_PRICE_SEMANTICS:', 'if False and semantics not in ALLOWED_PRICE_SEMANTICS:', "tools.m3top3.tests.test_known_failures_price.KnownFailurePriceTests.test_unrecognized_price_semantics_is_fail_closed_at_construction"),
    Mutation("MUT-SNAPSHOT-DIRECTORY-IDENTITY", "tools/m3top3/admission.py", 'if not canonical_directory and not internal_staging_directory:', 'if False and not canonical_directory and not internal_staging_directory:', "tools.m3top3.tests.test_known_failures_integrity.KnownFailureIntegrityTests.test_hidden_staging_directory_is_not_externally_admissible"),
    Mutation("MUT-PIT-MODEL-LINEAGE", "tools/m3top3/admission.py", 'if pit_keys != model_keys:', 'if False and pit_keys != model_keys:', "tools.m3top3.tests.test_known_failures_integrity.KnownFailureIntegrityTests.test_self_consistent_model_pit_identity_forgery_is_rejected"),
    Mutation("MUT-RETRIEVAL-INDEPENDENT-RECONSTRUCTION", "tools/m3top3/snapshot.py", 'if raw_features!=expected_features or retrieval_receipt!=expected_receipt:', 'if False and (raw_features!=expected_features or retrieval_receipt!=expected_receipt):', "tools.m3top3.tests.test_known_failures_snapshot.KnownFailureSnapshotTests.test_exact_provider_instance_method_forgery_is_independently_reconstructed"),
    Mutation("MUT-SNAPSHOT-PREPUBLISH-VERIFY", "tools/m3top3/snapshot.py", 'verify_snapshot_artifacts(staging,allow_staging=True)', 'pass  # MUTATION: pre-publish semantic verification removed', "tools.m3top3.tests.test_known_failures_snapshot.KnownFailureSnapshotTests.test_duplicate_company_slice_is_verified_before_publish"),
    Mutation("MUT-RESULT-EXCLUSIVE-CREATE", "tools/m3top3/ledger.py", 'os.link(candidate,self.path)', 'os.replace(candidate,self.path)', "tools.m3top3.tests.test_known_failures_immutability.KnownFailureImmutabilityTests.test_concurrent_different_payloads_cannot_both_append_or_overwrite"),
    Mutation("MUT-LEDGER-LIVE-RECHECK", "tools/m3top3/ledger.py", 'live=self._read_existing(); states=[]; additions=[]', 'live=dict(self._existing); states=[]; additions=[]', "tools.m3top3.tests.test_known_failures_immutability.KnownFailureImmutabilityTests.test_two_ledger_instances_cannot_append_conflicting_same_identity"),
    Mutation("MUT-LEDGER-BEFORE-RESULT", "tools/m3top3/backtest.py", 'prediction_ledger.append_many(prediction_records)', 'pass  # MUTATION: ledger admission skipped before result write', "tools.m3top3.tests.test_known_failures_immutability.KnownFailureImmutabilityTests.test_ledger_admission_failure_precedes_result_artifact_write"),
    Mutation("MUT-STAGING-ENUMERATION", "tools/m3top3/cli_run_backtest.py", 'if not candidate.is_dir() or candidate.name.startswith(".") or not (candidate/"manifest.json").exists():\n                continue\n            try: date.fromisoformat(candidate.name)\n            except ValueError: continue', 'if not candidate.is_dir() or not (candidate/"manifest.json").exists():\n                continue\n            try: date.fromisoformat(candidate.name)\n            except ValueError: pass', "tools.m3top3.tests.test_known_failures_cli.KnownFailureCLITests.test_hidden_staging_snapshot_directory_is_not_enumerated"),
    Mutation("MUT-PRICE-LINEAGE", "tools/m3top3/backtest.py", 'if actual_price_lineage!=expected_price_lineage:', 'if False and actual_price_lineage!=expected_price_lineage:', "tools.m3top3.tests.test_known_failures_integrity.KnownFailureIntegrityTests.test_snapshot_and_outcome_price_lineage_mismatch_is_rejected"),
    Mutation("MUT-PARQUET-PREQUERY-ADMISSION", "tools/m3top3/providers.py", 'verify_price_component_manifest(self,component_manifest)\n        verify_price_release(self,admission_config)\n        self._con=duckdb.connect()', 'verify_price_component_manifest(self,component_manifest)\n        self._con=duckdb.connect()\n        verify_price_release(self,admission_config)', "tools.m3top3.tests.test_known_failures_price.KnownFailurePriceTests.test_parquet_hash_mismatch_blocks_before_connect_or_query"),
    Mutation("MUT-PIT-PRICE-DATASET-BINDING", "tools/m3top3/admission.py", 'if len(price_refs)!=1 or price_refs[0].get("content_hash")!=manifest.get("price_dataset_hash"):', 'if False and (len(price_refs)!=1 or price_refs[0].get("content_hash")!=manifest.get("price_dataset_hash")):', "tools.m3top3.tests.test_known_failures_integrity.KnownFailureIntegrityTests.test_self_consistent_manifest_model_price_drift_from_pit_is_rejected"),
    Mutation("MUT-SNAPSHOT-TARGET-EXCLUSIVE", "tools/m3top3/snapshot.py", 'd.mkdir(exist_ok=False)', 'd.mkdir(exist_ok=True)', "tools.m3top3.tests.test_known_failures_immutability.KnownFailureImmutabilityTests.test_empty_concurrent_snapshot_target_is_not_replaced"),
    Mutation("MUT-SNAPSHOT-MANIFEST-LAST", "tools/m3top3/snapshot.py", 'publish_order=("pit_snapshot.jsonl","model_input.jsonl","retrieval_audit.jsonl","manifest.json")', 'publish_order=("manifest.json","pit_snapshot.jsonl","model_input.jsonl","retrieval_audit.jsonl")', "tools.m3top3.tests.test_known_failures_immutability.KnownFailureImmutabilityTests.test_snapshot_manifest_is_published_last"),
]


def run(source_root: Path) -> dict:
    results = []
    for mutation in MUTATIONS:
        with tempfile.TemporaryDirectory(prefix="m3top3-mutation-") as tmp:
            temp_root = Path(tmp)
            shutil.copytree(source_root / "tools", temp_root / "tools")
            target = temp_root / mutation.path
            original = target.read_text(encoding="utf-8")
            count = original.count(mutation.old)
            if count != 1:
                results.append({"mutation_id": mutation.mutation_id, "status": "HARNESS_ERROR", "replacement_count": count})
                continue
            target.write_text(original.replace(mutation.old, mutation.new, 1), encoding="utf-8")
            env = dict(os.environ)
            env["PYTHONPATH"] = str(temp_root)
            completed = subprocess.run(
                [sys.executable, "-m", "unittest", mutation.paired_test, "-v"],
                cwd=temp_root,
                env=env,
                capture_output=True,
                text=True,
                timeout=30,
            )
            output = completed.stdout + completed.stderr
            killed = completed.returncode != 0 and "FAILED (failures=1)" in output and "errors=" not in output
            results.append({
                "mutation_id": mutation.mutation_id,
                "paired_test": mutation.paired_test,
                "status": "KILLED_RED" if killed else "SURVIVED_OR_ERROR",
                "return_code": completed.returncode,
                "test_summary": next((line for line in output.splitlines() if line.startswith("FAILED")), None),
            })
    killed_count = sum(item["status"] == "KILLED_RED" for item in results)
    return {
        "source_root": str(source_root),
        "source_mutated": False,
        "requested_mutations": len(MUTATIONS),
        "killed_red": killed_count,
        "survived_or_error": len(MUTATIONS) - killed_count,
        "status": "PASS" if killed_count == len(MUTATIONS) else "FAIL",
        "results": results,
    }


if __name__ == "__main__":
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / "runtime_checkout"
    receipt = run(root)
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    raise SystemExit(0 if receipt["status"] == "PASS" else 1)
