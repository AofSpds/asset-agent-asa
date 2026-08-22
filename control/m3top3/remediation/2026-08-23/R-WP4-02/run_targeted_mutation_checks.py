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
    Mutation("MUT-PRICE-HASH", "tools/m3top3/admission.py", 'if not actual_hash or getattr(provider, "dataset_hash", None) != actual_hash:', 'if False:', "tools.m3top3.tests.test_known_failures_price.KnownFailurePriceTests.test_kf_prc_001_configured_hash_mismatch"),
    Mutation("MUT-OHLC", "tools/m3top3/providers.py", 'if any(value <= 0 for value in prices) or row.high < max(row.open,row.close) or row.low > min(row.open,row.close) or row.low > row.high:', 'if False:', "tools.m3top3.tests.test_known_failures_price.KnownFailurePriceTests.test_kf_prc_004_high_below_open_or_close"),
    Mutation("MUT-RESULT-IMMUTABLE", "tools/m3top3/ledger.py", 'if prior != payload:\n                raise M3Top3AdmissionError(\n                    "NONDETERMINISTIC_RERUN"', 'if False:\n                raise M3Top3AdmissionError(\n                    "NONDETERMINISTIC_RERUN"', "tools.m3top3.tests.test_known_failures_immutability.KnownFailureImmutabilityTests.test_kf_imm_003_same_run_id_different_result_is_rejected"),
    Mutation("MUT-CLI-BLOCKED", "tools/m3top3/cli_run_backtest.py", 'if blocked or len(results)!=len(snapshot_dirs): return EXIT_BLOCKED', 'if False: return EXIT_BLOCKED', "tools.m3top3.tests.test_known_failures_cli.KnownFailureCLITests.test_kf_cli_001_blocked_tie_returns_two_and_no_output"),
    Mutation("MUT-OFFICIAL-GLOBAL-KILL", "tools/m3top3/admission.py", 'if not OFFICIAL_EXECUTION_ENABLED:', 'if False:', "tools.m3top3.tests.test_known_failures_model_admission.KnownFailureModelAdmissionTests.test_kf_mod_002_diagnostic_scorer_denied_in_official_mode"),
    Mutation("MUT-PRICE-COMPONENT-MANIFEST", "tools/m3top3/admission.py", 'if len(components)<=1:', 'if True:', "tools.m3top3.tests.test_known_failures_price.KnownFailurePriceTests.test_multi_component_price_requires_versioned_byte_manifest"),
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
