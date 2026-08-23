from __future__ import annotations

"""R-WP4-03 v0.4.1-successor exact-anchor mutation harness.

The first 33 mutation IDs preserve the accepted R-WP4-02 control intents.
The next 17 preserve the frozen v0.1 exact-50 R-WP4-03 design.  The final
four are the explicit v0.2 design delta for controls that landed after that
design was frozen.  The final three are the non-retroactive v0.4 SEM-001
semantic-preservation delta.  This is a 57-case successor registry, not a
retroactive rewrite of either the predecessor exact-50 or v0.2 exact-54
contracts.
Every mutation runs in a fresh copy of ``tools`` and is accepted only when its
paired semantic regression fails by assertion (never by import/runtime error).
The harness may live outside the candidate: its probe modules are overlaid only
into each disposable mutation sandbox.  The governed source root is never
modified.
"""

import argparse
import csv
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Mutation:
    mutation_id: str
    generation: str
    control_family: str
    path: str
    old: str
    new: str
    paired_tests: tuple[str, ...]
    matrix_ids: tuple[str, ...] = ()


def _m(
    mutation_id: str,
    generation: str,
    family: str,
    path: str,
    old: str,
    new: str,
    test: str | tuple[str, ...],
    matrix: str | tuple[str, ...] = (),
) -> Mutation:
    return Mutation(
        mutation_id,
        generation,
        family,
        path,
        old,
        new,
        (test,) if isinstance(test, str) else test,
        (matrix,) if isinstance(matrix, str) else matrix,
    )


PROBE = "tools.m3top3.tests.run_r_wp4_03_mutation_checks.MutationSemanticProbeTests"


MUTATIONS: tuple[Mutation, ...] = (
    _m("MUT-PIT-MISSING-KEY", "R-WP4-02-PRESERVED", "PIT publication key", "tools/m3top3/pit_guard.py", 'violations.append(GuardViolation("MISSING_PUBLICATION_AT", "historical feature/evidence row requires publication_at", "publication_at"))', "pass  # MUTATION: missing-key guard removed", "tools.m3top3.tests.test_known_failures_pit.KnownFailurePITTests.test_kf_pit_001_missing_publication_key"),
    _m("MUT-PIT-NULL", "R-WP4-02-PRESERVED", "PIT null publication", "tools/m3top3/pit_guard.py", 'violations.append(GuardViolation("MISSING_PUBLICATION_AT", f"missing publication datetime at {path}", path))', "pass  # MUTATION: null-publication guard removed", "tools.m3top3.tests.test_known_failures_pit.KnownFailurePITTests.test_kf_pit_001_null_publication"),
    _m("MUT-PIT-NAIVE", "R-WP4-02-PRESERVED", "PIT timezone", "tools/m3top3/pit_guard.py", 'violations.append(GuardViolation("INVALID_PUBLICATION_DATETIME", f"invalid timezone-aware publication datetime at {path}", path))', "pass  # MUTATION: timezone guard removed", "tools.m3top3.tests.test_known_failures_pit.KnownFailurePITTests.test_kf_pit_002_naive_publication_string"),
    _m("MUT-PIT-AVAILABLE", "R-WP4-02-PRESERVED", "PIT availability", "tools/m3top3/pit_guard.py", 'if lk == "available_before_entry" and value is False:', 'if False and lk == "available_before_entry" and value is False:', "tools.m3top3.tests.test_known_failures_pit.KnownFailurePITTests.test_kf_pit_003_not_available_before_entry"),
    _m("MUT-PIT-CURRENT", "R-WP4-02-PRESERVED", "PIT current-only", "tools/m3top3/pit_guard.py", 'if lk == "current_only" and value is True:', 'if False and lk == "current_only" and value is True:', "tools.m3top3.tests.test_known_failures_pit.KnownFailurePITTests.test_kf_pit_004_current_only"),
    _m("MUT-PIT-CONSUMED-PUB", "R-WP4-02-PRESERVED", "PIT consumed publication", "tools/m3top3/pit_guard.py", 'if parse_datetime(value) > cutoff:\n                            violations.append(GuardViolation("PIT_PUBLICATION_AFTER_CUTOFF"', 'if False:\n                            violations.append(GuardViolation("PIT_PUBLICATION_AFTER_CUTOFF"', "tools.m3top3.tests.test_known_failures_pit.KnownFailurePITTests.test_kf_pit_005_consumed_future_row_blocks"),
    _m("MUT-PIT-CONSUMED-EFFECTIVE", "R-WP4-02-PRESERVED", "PIT consumed effective date", "tools/m3top3/pit_guard.py", 'if parse_datetime(value) > cutoff:\n                        violations.append(GuardViolation("PIT_EFFECTIVE_AFTER_CUTOFF"', 'if False:\n                        violations.append(GuardViolation("PIT_EFFECTIVE_AFTER_CUTOFF"', "tools.m3top3.tests.test_known_failures_pit.KnownFailurePITTests.test_kf_pit_006_consumed_effective_after_cutoff_blocks"),
    _m("MUT-SNAPSHOT-STATUS", "R-WP4-02-PRESERVED", "Snapshot READY status", "tools/m3top3/admission.py", 'if status != "SNAPSHOT_READY":', 'if False and status != "SNAPSHOT_READY":', "tools.m3top3.tests.test_known_failures_snapshot.KnownFailureSnapshotTests.test_kf_snp_002_partial_manifest_blocked_before_scorer"),
    _m("MUT-SNAPSHOT-BLOCKERS", "R-WP4-02-PRESERVED", "Snapshot blocker contradiction", "tools/m3top3/admission.py", 'if status == "SNAPSHOT_READY" and blockers:', 'if False and status == "SNAPSHOT_READY" and blockers:', "tools.m3top3.tests.test_known_failures_snapshot.KnownFailureSnapshotTests.test_kf_snp_004_ready_with_blocker_is_contradiction"),
    _m("MUT-MODEL-HASH", "R-WP4-02-PRESERVED", "Model input byte hash", "tools/m3top3/admission.py", 'if manifest.get("model_input_file_sha256") != actual_model_hash:', 'if False and manifest.get("model_input_file_sha256") != actual_model_hash:', "tools.m3top3.tests.test_known_failures_integrity.KnownFailureIntegrityTests.test_kf_int_002_model_input_valid_json_mutation"),
    _m("MUT-RETRIEVAL-AUDIT-HASH", "R-WP4-02-PRESERVED", "Retrieval audit byte hash", "tools/m3top3/admission.py", 'if manifest.get("retrieval_audit_file_sha256") != actual_audit_hash:', 'if False and manifest.get("retrieval_audit_file_sha256") != actual_audit_hash:', "tools.m3top3.tests.test_known_failures_integrity.KnownFailureIntegrityTests.test_retrieval_audit_valid_json_mutation_is_detected"),
    _m("MUT-RETRIEVAL-AUDIT-RECONCILIATION", "R-WP4-02-PRESERVED", "Retrieval count reconciliation", "tools/m3top3/admission.py", 'if source_matching_rows != selected_rows + excluded_rows:', 'if False:', "tools.m3top3.tests.test_r_wp4_03_mutation_isolation.RWP403MutationIsolationTests.test_retrieval_count_reconciliation_guard"),
    _m("MUT-PRICE-HASH", "R-WP4-02-PRESERVED", "Price live-byte hash", "tools/m3top3/admission.py", 'if (\n        not actual_hash', 'if False and (\n        not actual_hash', "tools.m3top3.tests.test_known_failures_price.KnownFailurePriceTests.test_post_construction_price_byte_mutation_is_rejected_before_read"),
    _m("MUT-OHLC", "R-WP4-02-PRESERVED", "OHLC integrity", "tools/m3top3/providers.py", 'if any(value <= 0 for value in prices) or row.high < max(row.open,row.close) or row.low > min(row.open,row.close) or row.low > row.high:', 'if False:', "tools.m3top3.tests.test_known_failures_price.KnownFailurePriceTests.test_kf_prc_004_high_below_open_or_close"),
    _m("MUT-RESULT-IMMUTABLE", "R-WP4-02-PRESERVED", "Result byte immutability", "tools/m3top3/ledger.py", '            if prior != payload:', '            if False:', "tools.m3top3.tests.test_r_wp4_03_mutation_isolation.RWP403MutationIsolationTests.test_immutable_json_artifact_store_rejects_different_payload"),
    _m("MUT-CLI-BLOCKED", "R-WP4-02-PRESERVED", "CLI blocked exit", "tools/m3top3/cli_run_backtest.py", 'if blocked:return EXIT_BLOCKED', 'if False and blocked:return EXIT_BLOCKED', "tools.m3top3.tests.test_known_failures_cli.KnownFailureCLITests.test_kf_cli_001_blocked_tie_returns_two_and_no_output"),
    _m("MUT-OFFICIAL-GLOBAL-KILL", "R-WP4-02-PRESERVED", "Official global kill", "tools/m3top3/admission.py", 'if not OFFICIAL_EXECUTION_ENABLED:', 'if False:', "tools.m3top3.tests.test_known_failures_model_admission.KnownFailureModelAdmissionTests.test_kf_mod_002_diagnostic_scorer_denied_in_official_mode"),
    _m("MUT-PRICE-COMPONENT-MANIFEST", "R-WP4-02-PRESERVED", "Price component manifest", "tools/m3top3/admission.py", 'if len(paths)<=1:\n        return', 'if True:\n        return', f"{PROBE}.test_multi_component_manifest_required"),
    _m("MUT-PRICE-SEMANTICS-ALLOWLIST", "R-WP4-02-PRESERVED", "Price semantics allowlist", "tools/m3top3/admission.py", 'if semantics not in ALLOWED_PRICE_SEMANTICS:', 'if False and semantics not in ALLOWED_PRICE_SEMANTICS:', "tools.m3top3.tests.test_known_failures_price.KnownFailurePriceTests.test_unrecognized_price_semantics_is_fail_closed_at_construction"),
    _m("MUT-SNAPSHOT-DIRECTORY-IDENTITY", "R-WP4-02-PRESERVED", "Snapshot directory identity", "tools/m3top3/admission.py", 'if not canonical_directory and not internal_staging_directory:', 'if False and not canonical_directory and not internal_staging_directory:', "tools.m3top3.tests.test_known_failures_integrity.KnownFailureIntegrityTests.test_hidden_staging_directory_is_not_externally_admissible"),
    _m("MUT-PIT-MODEL-LINEAGE", "R-WP4-02-PRESERVED", "PIT/model identity join", "tools/m3top3/admission.py", 'if pit_keys != model_keys:', 'if False and pit_keys != model_keys:', "tools.m3top3.tests.test_known_failures_integrity.KnownFailureIntegrityTests.test_self_consistent_model_pit_identity_forgery_is_rejected"),
    _m("MUT-RETRIEVAL-INDEPENDENT-RECONSTRUCTION", "R-WP4-02-PRESERVED", "Retrieval independent reconstruction", "tools/m3top3/snapshot.py", 'if raw_features!=expected_features or retrieval_receipt!=expected_receipt:', 'if False and (raw_features!=expected_features or retrieval_receipt!=expected_receipt):', "tools.m3top3.tests.test_known_failures_snapshot.KnownFailureSnapshotTests.test_exact_provider_instance_method_forgery_is_independently_reconstructed"),
    _m("MUT-SNAPSHOT-PREPUBLISH-VERIFY", "R-WP4-02-PRESERVED", "Snapshot prepublish verification", "tools/m3top3/snapshot.py", 'verify_snapshot_artifacts(staging,allow_staging=True)', 'pass  # MUTATION: pre-publish semantic verification removed', "tools.m3top3.tests.test_known_failures_snapshot.KnownFailureSnapshotTests.test_duplicate_company_slice_is_verified_before_publish"),
    _m("MUT-RESULT-EXCLUSIVE-CREATE", "R-WP4-02-PRESERVED", "Result exclusive create", "tools/m3top3/ledger.py", '        try:\n            os.link(candidate,self.path)\n        except FileExistsError:\n            prior=self.path.read_bytes()', '        try:\n            os.replace(candidate,self.path)\n        except FileExistsError:\n            prior=self.path.read_bytes()', "tools.m3top3.tests.test_known_failures_immutability.KnownFailureImmutabilityTests.test_concurrent_different_payloads_cannot_both_append_or_overwrite"),
    _m("MUT-LEDGER-LIVE-RECHECK", "R-WP4-02-PRESERVED", "Ledger locked live recheck", "tools/m3top3/ledger.py", 'live=self._read_existing(); states=[]; additions=[]', 'live=dict(self._existing); states=[]; additions=[]', "tools.m3top3.tests.test_known_failures_immutability.KnownFailureImmutabilityTests.test_two_ledger_instances_cannot_append_conflicting_same_identity"),
    _m("MUT-LEDGER-BEFORE-RESULT", "R-WP4-02-PRESERVED", "Ledger admission before result", "tools/m3top3/backtest.py", '                prediction_ledger.append_many(prediction_records)\n            artifact_state=store.publish(result,ledger_path)', '            artifact_state=store.publish(result,ledger_path)\n            if prediction_ledger is not None:\n                prediction_ledger.append_many(prediction_records)', "tools.m3top3.tests.test_r_wp4_03_mutation_isolation.RWP403MutationIsolationTests.test_prediction_ledger_append_precedes_result_publish"),
    _m("MUT-STAGING-ENUMERATION", "R-WP4-02-PRESERVED", "CLI staging exclusion", "tools/m3top3/cli_run_backtest.py", 'if not candidate.is_dir() or candidate.name.startswith(".") or not (candidate/"manifest.json").exists(): continue\n                try: date.fromisoformat(candidate.name)\n                except ValueError: continue', 'if not candidate.is_dir() or not (candidate/"manifest.json").exists(): continue\n                try: date.fromisoformat(candidate.name)\n                except ValueError: pass', "tools.m3top3.tests.test_known_failures_cli.KnownFailureCLITests.test_hidden_staging_snapshot_directory_is_not_enumerated"),
    _m("MUT-PRICE-LINEAGE", "R-WP4-02-PRESERVED", "Snapshot/outcome price lineage", "tools/m3top3/backtest.py", 'if {field:manifest.get(field) for field in expected_price}!=expected_price: raise M3Top3AdmissionError("PRICE_LINEAGE_MISMATCH","snapshot and outcome-provider price identities differ",exit_code=EXIT_INTEGRITY)', 'if False: raise M3Top3AdmissionError("PRICE_LINEAGE_MISMATCH","snapshot and outcome-provider price identities differ",exit_code=EXIT_INTEGRITY)', "tools.m3top3.tests.test_known_failures_integrity.KnownFailureIntegrityTests.test_snapshot_and_outcome_price_lineage_mismatch_is_rejected"),
    _m("MUT-PARQUET-PREQUERY-ADMISSION", "R-WP4-02-PRESERVED", "Parquet prequery admission", "tools/m3top3/providers.py", 'verify_price_component_manifest(self,component_manifest)\n        verify_price_release(self,admission_config)\n        self._con=duckdb.connect()', 'verify_price_component_manifest(self,component_manifest)\n        self._con=duckdb.connect()\n        verify_price_release(self,admission_config)', "tools.m3top3.tests.test_known_failures_price.KnownFailurePriceTests.test_parquet_hash_mismatch_blocks_before_connect_or_query"),
    _m("MUT-PIT-PRICE-DATASET-BINDING", "R-WP4-02-PRESERVED", "PIT price dataset binding", "tools/m3top3/admission.py", '    "FEATURE_SOURCE_RELEASE",\n    "PRICE_RELEASE",\n    "TRADING_CALENDAR_RELEASE",', '    "FEATURE_SOURCE_RELEASE",\n    "TRADING_CALENDAR_RELEASE",', f"{PROBE}.test_pit_price_ref_identity_binding"),
    _m("MUT-SNAPSHOT-TARGET-EXCLUSIVE", "R-WP4-02-PRESERVED", "Snapshot target create-only", "tools/m3top3/snapshot.py", 'd.mkdir(exist_ok=False)', 'd.mkdir(exist_ok=True)', "tools.m3top3.tests.test_known_failures_immutability.KnownFailureImmutabilityTests.test_empty_concurrent_snapshot_target_is_not_replaced"),
    _m("MUT-SNAPSHOT-MANIFEST-LAST", "R-WP4-02-PRESERVED", "Snapshot manifest-last", "tools/m3top3/snapshot.py", 'publish_order=("pit_snapshot.jsonl","model_input.jsonl","retrieval_audit.jsonl","manifest.json")', 'publish_order=("manifest.json","pit_snapshot.jsonl","model_input.jsonl","retrieval_audit.jsonl")', "tools.m3top3.tests.test_known_failures_immutability.KnownFailureImmutabilityTests.test_snapshot_manifest_is_published_last"),
    _m("MUT-STAGING-RACE-CLASSIFICATION", "R-WP4-02-PRESERVED", "Snapshot race classification", "tools/m3top3/snapshot.py", 'raise M3Top3AdmissionError("IMMUTABLE_SNAPSHOT_COLLISION","snapshot staging identity appeared during create-only admission",{"path":str(staging)},3) from exc', 'raise exc  # MUTATION: raw staging race leaks as unclassified', "tools.m3top3.tests.test_known_failures_immutability.KnownFailureImmutabilityTests.test_staging_mkdir_race_is_classified_integrity_collision"),

    _m("MUT-R03-OFFICIAL-GOLDEN-REPLAY-LOCK", "R-WP4-03-NEW", "Official/Golden/Replay claim locks", "tools/m3top3/admission.py", 'if config.get("official_golden") is True or config.get("full_replay") is True:', 'if False:', f"{PROBE}.test_claim_locks", ("CLM-003", "CLM-004", "CLM-005")),
    _m("MUT-R03-UNIVERSE-LIVE-INDEPENDENT-MANIFEST", "R-WP4-03-NEW", "Universe live independent manifest", "tools/m3top3/admission.py", 'if live_manifest_hash != manifest_hash or live_manifest != getattr(provider, "_lineage_manifest", None):', 'if False:', "tools.m3top3.tests.test_known_failures_lineage_universe.KnownFailureCanonicalLineageAndUniverseTests.test_jsonl_manifest_live_byte_drift_is_rejected", ("UNI-001", "UNI-014", "LIN-004", "LIN-010")),
    _m("MUT-R03-PATH-INDEPENDENT-COMPONENT-DIGEST", "R-WP4-03-NEW", "Path-independent component digest", "tools/m3top3/admission.py", '"semantic_role": component.get("semantic_role"),\n        }', '"semantic_role": component.get("semantic_role"),\n            "path": component.get("path"),\n        }', f"{PROBE}.test_component_digest_is_path_independent", ("LIN-007", "LIN-009")),
    _m("MUT-R03-UNIVERSE-DENOMINATOR-SET", "R-WP4-03-NEW", "Universe/denominator exact-set equality", "tools/m3top3/admission.py", '    if actual_ids != release_ids:', '    if False:', f"{PROBE}.test_universe_runtime_slice_exact", ("UNI-006", "UNI-007", "UNI-008")),
    _m("MUT-R03-PARTITION-DIGESTS", "R-WP4-03-NEW", "Eligible/ineligible/partition digests", "tools/m3top3/admission.py", '    if manifest.get("eligible_record_ids")!=eligible_record_ids or manifest.get("ineligible_record_ids")!=ineligible_record_ids or manifest.get("eligible_set_digest")!=canonical_e or manifest.get("ineligible_set_digest")!=canonical_i or manifest.get("denominator_partition_digest")!=partition_digest:', '    if False:', "tools.m3top3.tests.test_r_wp4_03_mutation_isolation.RWP403MutationIsolationTests.test_partition_digest_guard_at_snapshot_level", ("UNI-010", "UNI-011")),
    _m("MUT-R03-DATASET-REF-ONE-TO-ONE", "R-WP4-03-NEW", "Row-level dataset refs one-to-one", "tools/m3top3/admission.py", '    "PRICE_RELEASE",\n    "TRADING_CALENDAR_RELEASE",\n)\nOUTCOME_DATASET_DOMAINS = (', '    "PRICE_RELEASE",\n)\nOUTCOME_DATASET_DOMAINS = (', f"{PROBE}.test_dataset_refs_one_to_one", ("REF-001", "REF-002", "REF-003", "REF-004", "REF-005", "REF-006", "REF-007", "REF-008")),
    _m("MUT-R03-STATUS-DATE-REVISION-COHERENCE", "R-WP4-03-NEW", "Status/date/revision coherence", "tools/m3top3/admission.py", '        if pit_row.get("snapshot_revision")!=manifest.get("snapshot_revision") or model_row.get("snapshot_revision",0)!=manifest.get("snapshot_revision"):', '        if False:', f"{PROBE}.test_revision_tuple_coherence", ("LIN-008", "UNI-009", "UNI-012", "SNP-004", "SNP-005B")),
    _m("MUT-R03-FULL-U-SNAPSHOT-SETS", "R-WP4-03-NEW", "Full applicable U snapshot sets", "tools/m3top3/admission.py", '    actual_members=set(pit_member_ids)|set(model_member_ids); expected_members=set(denominator_member_ids)\n    missing=sorted(expected_members-actual_members); extra=sorted(actual_members-expected_members)\n    if missing:\n        code="TERMINAL_INELIGIBLE_IDENTITY_MISSING" if set(missing).issubset(ineligible_member_ids) else "SNAPSHOT_UNIVERSE_MEMBER_MISSING"\n        raise M3Top3AdmissionError(code,"snapshot PIT/model sets omit applicable Universe members",{"missing":missing},EXIT_INTEGRITY)\n    if extra:\n        raise M3Top3AdmissionError("SNAPSHOT_UNIVERSE_MEMBER_EXTRA","snapshot PIT/model sets contain outside-Universe members",{"extra":extra},EXIT_INTEGRITY)\n    if sorted(pit_member_ids)!=denominator_member_ids or sorted(model_member_ids)!=denominator_member_ids:\n        raise M3Top3AdmissionError("SNAPSHOT_UNIVERSE_MEMBER_MISSING","PIT/model Universe sets do not reconcile",exit_code=EXIT_INTEGRITY)\n    if sorted(actual_eligible_ids)!=eligible_member_ids:\n        raise M3Top3AdmissionError("ELIGIBLE_SET_DIGEST_MISMATCH","snapshot eligible set differs from denominator E",exit_code=EXIT_INTEGRITY)', '    actual_members=set(pit_member_ids)|set(model_member_ids); expected_members=set(actual_members)\n    missing=[]; extra=[]', "tools.m3top3.tests.test_known_failures_lineage_universe.KnownFailureCanonicalLineageAndUniverseTests.test_self_consistent_subset_of_snapshot_rows_is_rejected", ("SNP-001", "SNP-002", "SNP-002B", "SNP-003")),
    _m("MUT-R03-EXACT-DIAGNOSTIC-SCORER", "R-WP4-03-NEW", "Exact diagnostic scorer identity", "tools/m3top3/admission.py", 'if sha256_hex(config_bytes) != receipt.get("config_sha256") or len(config_bytes) != receipt.get("config_byte_size"):', 'if False:', f"{PROBE}.test_diagnostic_scorer_config_exact", ("SCR-001", "SCR-002", "SCR-003")),
    _m("MUT-R03-RUN-LINEAGE-IDENTITY", "R-WP4-03-NEW", "Validation-run lineage identity", "tools/m3top3/backtest.py", '    if result.get("validation_run_id")!=expected:', '    if False:', f"{PROBE}.test_validation_run_id_binding", "SCR-005"),
    _m("MUT-R03-FULL-U-SCORER-OUTPUT", "R-WP4-03-NEW", "Full scorer-output U completeness", "tools/m3top3/backtest.py", 'if missing: raise M3Top3AdmissionError("FULL_SCORER_OUTPUT_SET_MEMBER_MISSING","scorer-output identity set omits U members",{"missing":missing},EXIT_INTEGRITY)', 'if False: raise M3Top3AdmissionError("FULL_SCORER_OUTPUT_SET_MEMBER_MISSING","scorer-output identity set omits U members",{"missing":missing},EXIT_INTEGRITY)', f"{PROBE}.test_scoring_full_u_missing_member", ("RNK-001", "RNK-002", "RNK-003", "RNK-004")),
    _m("MUT-R03-RANK-SET-SEQUENCE-TOP3", "R-WP4-03-NEW", "Full rank set/sequence/Top3", "tools/m3top3/backtest.py", 'if [row.get("rank") for row in ranked]!=list(range(1,len(ranked)+1)):', 'if False:', "tools.m3top3.tests.test_r_wp4_03_matrix.RWP403MatrixTests.test_matrix_rnk_006", ("RNK-005", "RNK-006", "RNK-007")),
    _m("MUT-R03-FULL-OUTCOME-SET", "R-WP4-03-NEW", "Full outcome-set persistence", "tools/m3top3/backtest.py", '"full_universe_outcomes":outcomes', '"full_universe_outcomes":selected_outcomes', f"{PROBE}.test_full_outcome_set_persistence", ("OUT-001", "OUT-002", "OUT-003", "OUT-004", "OUT-005")),
    _m("MUT-R03-METRIC-DENOMINATOR", "R-WP4-03-NEW", "Metric denominator integrity", "tools/m3top3/backtest.py", 'def summarize_full_eligible_universe(self,outcomes:list[dict[str,Any]],eligible_count:int)->dict[str,Any]:\n        if len(outcomes)!=eligible_count:', 'def summarize_full_eligible_universe(self,outcomes:list[dict[str,Any]],eligible_count:int)->dict[str,Any]:\n        eligible_count=len(outcomes)  # MUTATION: collapse denominator to observed rows\n        if len(outcomes)!=eligible_count:', f"{PROBE}.test_metric_denominator_integrity", ("OUT-006", "OUT-007")),
    _m("MUT-R03-FULL-LEDGER-COMPLETENESS", "R-WP4-03-NEW", "Full ranking/ledger completeness", "tools/m3top3/ledger.py", 'or result.get("ranked_count")!=len(ranked)\n            or result.get("outcome_count")!=len(outcomes)', 'or False  # MUTATION: full ranked count guard removed\n            or result.get("outcome_count")!=len(outcomes)', f"{PROBE}.test_full_ledger_ranked_count", ("RNK-008", "OUT-001", "IMM-002")),
    _m("MUT-R03-ZERO-WORK-ACCOUNTING", "R-WP4-03-NEW", "Zero-work/nonzero-exit accounting", "tools/m3top3/admission.py", '    if not isinstance(count,int) or isinstance(count,bool) or count<=0:', '    if False:', "tools.m3top3.tests.test_known_failures_cli.KnownFailureCLITests.test_backtest_zero_snapshot_directories_is_blocked_not_success", ("UNI-013", "CLI-001", "CLI-002", "CLI-003")),
    _m("MUT-R03-FULL-RESULT-IMMUTABLE-MANIFEST-LAST", "R-WP4-03-NEW", "Full-result immutable manifest-last", "tools/m3top3/ledger.py", 'state="REUSED"\n        for path,payload in payloads.items():\n            if self._admit_bytes(path,payload)=="APPENDED": state="APPENDED"\n        # The separate commit marker is always the last governed write.\n        if self._admit_bytes(self.manifest_path,canonical_json_bytes(manifest)+b"\\n")=="APPENDED": state="APPENDED"', 'state="REUSED"\n        if self._admit_bytes(self.manifest_path,canonical_json_bytes(manifest)+b"\\n")=="APPENDED": state="APPENDED"\n        for path,payload in payloads.items():\n            if self._admit_bytes(path,payload)=="APPENDED": state="APPENDED"', "tools.m3top3.tests.test_r_wp4_03_ledger_v02.FullRunArtifactStoreV02Tests.test_commit_manifest_is_admitted_last", ("IMM-001", "IMM-003", "IMM-004", "IMM-005")),
    _m("MUT-R03-EXTRA-LINEAGE-COMPONENT", "R-WP4-03-NEW", "Manifest-only extra lineage component", "tools/m3top3/admission.py", '        if declared_ids-live_ids:', '        if False:', "tools.m3top3.tests.test_r_wp4_03_matrix.RWP403MatrixTests.test_matrix_lin_006", "LIN-006"),
    _m("MUT-R03-ELIGIBILITY-RELEASE-COMPLETE", "R-WP4-03-NEW", "Terminal eligibility release admission", "tools/m3top3/admission.py", '            if row.status not in ADMITTED_RELEASE_STATUSES or row.eligibility_status=="UNRESOLVED":', '            if False:', "tools.m3top3.tests.test_r_wp4_03_matrix.RWP403MatrixTests.test_matrix_uni_009", "UNI-009"),
    _m("MUT-R03-OUTCOME-COMPONENT-LINEAGE", "R-WP4-03-NEW", "Independent outcome component lineage", "tools/m3top3/backtest.py", '            if self.window_release_identity!={key:window_ref.get(key) for key in ("release_id","artifact_sha256","release_revision")}:', '            if False:', "tools.m3top3.tests.test_r_wp4_03_matrix.RWP403MatrixTests.test_matrix_ref_007", "REF-007"),
    _m("MUT-R03-IMMUTABLE-RELEASE-COLLISION", "R-WP4-03-NEW", "Persistent release identity immutability", "tools/m3top3/ledger.py", '        if self.path.exists():\n            if self.path.read_bytes()!=envelope:\n                raise M3Top3AdmissionError("IMMUTABLE_RELEASE_COLLISION","same release identity is already bound to different bytes",{"path":str(self.path),"release_identity":release_identity},EXIT_INTEGRITY)', '        if self.path.exists():\n            if False:\n                raise M3Top3AdmissionError("IMMUTABLE_RELEASE_COLLISION","same release identity is already bound to different bytes",{"path":str(self.path),"release_identity":release_identity},EXIT_INTEGRITY)', "tools.m3top3.tests.test_r_wp4_03_matrix.RWP403MatrixTests.test_matrix_imm_001", "IMM-001"),
    _m("MUT-R03-TOP3-OUTCOME-VIEW", "R-WP4-03-V04-SEM001", "Legacy Top3 outcome view", "tools/m3top3/backtest.py", '"outcomes":selected_outcomes,"selected_top3_outcomes":selected_outcomes', '"outcomes":outcomes,"selected_top3_outcomes":selected_outcomes', f"{PROBE}.test_sem001_top3_outcome_view"),
    _m("MUT-R03-TOP3-METRIC-POPULATION", "R-WP4-03-V04-SEM001", "Legacy Top3 metric population", "tools/m3top3/backtest.py", 'selected_top3_metrics=self.metrics.summarize(selected_outcomes)', 'selected_top3_metrics=self.metrics.summarize(outcomes)  # MUTATION: redefine legacy metrics on full E', f"{PROBE}.test_sem001_top3_metric_population"),
    _m("MUT-R03-RESULT-VIEW-VERSION-IDENTITY", "R-WP4-03-V04-SEM001", "Result/view version run identity", "tools/m3top3/backtest.py", '"window_protocol_version":getattr(self.outcome_builder.windows,"protocol_version",None),"validation_protocol_version":self.outcome_builder.validation_protocol_version,"result_contract_version":RESULT_CONTRACT_VERSION,"selected_top3_metrics_view_version":SELECTED_TOP3_METRICS_VIEW_VERSION', '"window_protocol_version":getattr(self.outcome_builder.windows,"protocol_version",None),"validation_protocol_version":self.outcome_builder.validation_protocol_version,"selected_top3_metrics_view_version":SELECTED_TOP3_METRICS_VIEW_VERSION', f"{PROBE}.test_sem001_result_view_version_identity"),
)


def _source_manifest(root: Path) -> dict[str, dict[str, Any]]:
    manifest: dict[str, dict[str, Any]] = {}
    for path in sorted((root / "tools").rglob("*")):
        if not path.is_file() or path.suffix in {".pyc", ".pyo"} or "__pycache__" in path.parts:
            continue
        payload = path.read_bytes()
        manifest[path.relative_to(root).as_posix()] = {
            "sha256": hashlib.sha256(payload).hexdigest(),
            "byte_size": len(payload),
        }
    return manifest


def _manifest_digest(manifest: dict[str, dict[str, Any]]) -> str:
    payload = json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _sha256_file(path: Path | None) -> str | None:
    if path is None or not path.exists():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_identity(root: Path) -> dict[str, Any]:
    values: dict[str, Any] = {"available": False, "commit": None, "tree": None, "dirty": None}
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True, timeout=5, check=True
        ).stdout.strip()
        tree = subprocess.run(
            ["git", "rev-parse", "HEAD^{tree}"], cwd=root, capture_output=True, text=True, timeout=5, check=True
        ).stdout.strip()
        status = subprocess.run(
            ["git", "status", "--porcelain"], cwd=root, capture_output=True, text=True, timeout=5, check=True
        ).stdout
    except (OSError, subprocess.SubprocessError):
        return values
    return {"available": True, "commit": commit, "tree": tree, "dirty": bool(status.strip())}


def _validate_freeze_receipt(
    source_root: Path,
    freeze_receipt: Path | None,
    expected_freeze_sha256: str | None,
) -> dict[str, Any]:
    if freeze_receipt is None:
        return {
            "bound": False,
            "reason": "no candidate-freeze receipt supplied; result is WIP-only",
            "freeze_receipt_path": None,
            "freeze_receipt_sha256": None,
            "runtime_manifest_sha256": None,
            "runtime_file_count": None,
        }
    payload = freeze_receipt.read_bytes()
    actual_receipt_sha256 = hashlib.sha256(payload).hexdigest()
    if expected_freeze_sha256 is not None and actual_receipt_sha256 != expected_freeze_sha256:
        raise RuntimeError("candidate-freeze receipt bytes differ from the explicitly configured SHA-256")
    try:
        receipt = json.loads(payload.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise RuntimeError("candidate-freeze receipt is unreadable or malformed") from exc
    if receipt.get("schema_version")=="r-wp4-03-freeze-manifest-v1":
        required={
            "successor_candidate_version":"v0.4",
            "source_tree_scope":"tools/m3top3",
            "source_tree_algorithm":"sha256-canonical-json-relative-path-size-sha256-v1",
            "pyc_excluded":True,
            "iva_participation":"NONE",
            "prior_v0_3_disposition":"REOPENED_NO_GO_FOR_SEM001",
        }
        if any(receipt.get(key)!=value for key,value in required.items()):
            raise RuntimeError("v0.4 canonical freeze manifest governance fields are not exact")
        if Path(str(receipt.get("candidate_root"))).resolve()!=source_root.resolve():
            raise RuntimeError("candidate-freeze source root differs from the mutation source root")
        declared=receipt.get("files")
        if not isinstance(declared,list) or not declared:
            raise RuntimeError("v0.4 canonical freeze manifest has no exact source inventory")
        live=[]
        for path in sorted((source_root / "tools" / "m3top3").rglob("*")):
            if not path.is_file() or path.suffix in {".pyc",".pyo"} or "__pycache__" in path.parts:
                continue
            live.append({
                "relative_path":path.relative_to(source_root).as_posix(),
                "sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
                "size":path.stat().st_size,
            })
        if declared!=live:
            raise RuntimeError("v0.4 canonical freeze inventory differs from live candidate bytes")
        tree_sha256=hashlib.sha256(
            json.dumps(live,sort_keys=True,separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        if tree_sha256!=receipt.get("source_tree_sha256"):
            raise RuntimeError("v0.4 canonical freeze source-tree digest mismatch")
        return {
            "bound":True,
            "freeze_receipt_path":str(freeze_receipt.resolve()),
            "freeze_receipt_sha256":actual_receipt_sha256,
            "configured_freeze_receipt_sha256":expected_freeze_sha256,
            "freeze_schema_version":receipt["schema_version"],
            "freeze_state":"RUNTIME_CANDIDATE_V0_4_FROZEN",
            "runtime_manifest_sha256":tree_sha256,
            "runtime_file_count":len(live),
            "runtime_files":{row["relative_path"]:row["sha256"] for row in live},
            "accepted_runtime_commit":receipt.get("accepted_runtime_commit"),
            "evidence_parent_commit":receipt.get("evidence_parent_commit"),
            "iva_execution_participation":receipt.get("iva_participation"),
        }
    runtime_files = receipt.get("runtime_files") if isinstance(receipt, dict) else None
    if (
        receipt.get("schema_version") not in {
            "m3top3-r-wp4-03-runtime-candidate-freeze-v0.4",
            "m3top3-r-wp4-03-runtime-candidate-freeze-v1",
        }
        or receipt.get("state") != "RUNTIME_CANDIDATE_FROZEN_TEST_EVIDENCE_INTEGRATION_OPEN"
        or not isinstance(runtime_files, dict)
        or not runtime_files
    ):
        raise RuntimeError("candidate-freeze receipt schema/state/runtime inventory is not admissible")
    if Path(str(receipt.get("source_root"))).resolve() != source_root.resolve():
        raise RuntimeError("candidate-freeze source root differs from the mutation source root")
    actual_runtime_files: dict[str, str] = {}
    for relative, expected_hash in sorted(runtime_files.items()):
        if not isinstance(relative, str) or not relative.startswith("tools/m3top3/") or "/tests/" in relative:
            raise RuntimeError("candidate-freeze runtime inventory contains a non-runtime path")
        path = source_root / relative
        if not path.is_file():
            raise RuntimeError(f"candidate-freeze runtime file is missing: {relative}")
        actual_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        actual_runtime_files[relative] = actual_hash
        if actual_hash != expected_hash:
            raise RuntimeError(f"candidate-freeze runtime file hash mismatch: {relative}")
    digest_bytes = "".join(
        f"{digest}  {relative}\n" for relative, digest in sorted(actual_runtime_files.items())
    ).encode("utf-8")
    actual_manifest_sha256 = hashlib.sha256(digest_bytes).hexdigest()
    if actual_manifest_sha256 != receipt.get("runtime_manifest_sha256"):
        raise RuntimeError("candidate-freeze runtime manifest digest does not match its exact file inventory")
    return {
        "bound": True,
        "freeze_receipt_path": str(freeze_receipt.resolve()),
        "freeze_receipt_sha256": actual_receipt_sha256,
        "configured_freeze_receipt_sha256": expected_freeze_sha256,
        "freeze_schema_version": receipt["schema_version"],
        "freeze_state": receipt["state"],
        "frozen_at": receipt.get("frozen_at"),
        "runtime_manifest_sha256": actual_manifest_sha256,
        "runtime_file_count": len(actual_runtime_files),
        "runtime_files": actual_runtime_files,
        "iva_execution_participation": receipt.get("iva_execution_participation"),
    }


def _validate_external_registries(registry: Path | None, matrix: Path | None) -> dict[str, Any]:
    result: dict[str, Any] = {
        "registry_order_match": None,
        "registry_ordinal_sequence_match": None,
        "registry_unique_id_count": None,
        "matrix_unique_id_count": None,
    }
    if registry is not None:
        with registry.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        ids = [row.get("mutation_id") for row in rows]
        ordinals = [row.get("ordinal") for row in rows]
        expected = [mutation.mutation_id for mutation in MUTATIONS]
        if ids != expected or len(set(ids)) != len(MUTATIONS):
            raise RuntimeError("external v0.4.1 successor mutation registry does not exactly match the 57-case harness order")
        if ordinals != [str(index) for index in range(1, len(MUTATIONS) + 1)]:
            raise RuntimeError("external v0.4.1 successor mutation registry ordinals are not the exact 1..57 sequence")
        result["registry_order_match"] = True
        result["registry_ordinal_sequence_match"] = True
        result["registry_unique_id_count"] = len(set(ids))
    if matrix is not None:
        with matrix.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        ids = [row.get("test_id") for row in rows]
        if len(ids) != 75 or len(set(ids)) != 75:
            raise RuntimeError("negative regression matrix must contain exactly 75 unique test IDs")
        result["matrix_unique_id_count"] = 75
    return result


def _run_mutation(source_root: Path, mutation: Mutation, timeout: int) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="m3top3-r03-mutation-") as tmp:
        temp_root = Path(tmp)
        shutil.copytree(source_root / "tools", temp_root / "tools")
        for copied in (temp_root / "tools").rglob("*"):
            copied.chmod(copied.stat().st_mode | (0o700 if copied.is_dir() else 0o600))
        harness_dir=Path(__file__).resolve().parent
        sandbox_test_dir=temp_root / "tools" / "m3top3" / "tests"
        for filename in (
            "run_r_wp4_03_mutation_checks.py",
            "r_wp4_03_matrix_harness.py",
            "r_wp4_03_matrix_cases.py",
        ):
            shutil.copy2(harness_dir / filename,sandbox_test_dir / filename)
        target = temp_root / mutation.path
        original = target.read_text(encoding="utf-8")
        replacement_count = original.count(mutation.old)
        target_hash_before = hashlib.sha256(original.encode("utf-8")).hexdigest()
        if replacement_count != 1:
            return {
                "mutation_id": mutation.mutation_id,
                "status": "HARNESS_ERROR",
                "replacement_count": replacement_count,
                "target_path": mutation.path,
                "target_sha256_before": target_hash_before,
                "paired_tests": list(mutation.paired_tests),
                "matrix_ids": list(mutation.matrix_ids),
                "reason": "exact old anchor must occur once",
            }
        target.write_text(original.replace(mutation.old, mutation.new, 1), encoding="utf-8")
        target_hash_after = hashlib.sha256(target.read_bytes()).hexdigest()
        env = dict(os.environ)
        env["PYTHONPATH"] = str(temp_root)
        module_name = ".".join(Path(mutation.path).with_suffix("").parts)
        import_probe = subprocess.run(
            [
                sys.executable,
                "-c",
                (
                    "import importlib,json;"
                    f"m=importlib.import_module({module_name!r});"
                    "h=importlib.import_module('tools.m3top3.tests.run_r_wp4_03_mutation_checks');"
                    "print(json.dumps({'target':m.__file__,'harness':h.__file__},sort_keys=True))"
                ),
            ],
            cwd=temp_root,
            env=env,
            capture_output=True,
            text=True,
            timeout=min(timeout, 15),
        )
        try:
            imported_paths = json.loads(import_probe.stdout)
        except (json.JSONDecodeError, TypeError):
            imported_paths = None
        expected_prefix = str(temp_root.resolve()) + os.sep
        if (
            import_probe.returncode != 0
            or not isinstance(imported_paths, dict)
            or any(not str(value).startswith(expected_prefix) for value in imported_paths.values())
        ):
            return {
                "mutation_id": mutation.mutation_id,
                "status": "HARNESS_ERROR",
                "replacement_count": replacement_count,
                "target_path": mutation.path,
                "target_sha256_before": target_hash_before,
                "target_sha256_after": target_hash_after,
                "paired_tests": list(mutation.paired_tests),
                "matrix_ids": list(mutation.matrix_ids),
                "reason": "mutated target/harness import did not resolve inside the isolated copy",
                "import_probe_return_code": import_probe.returncode,
                "import_probe_stderr": import_probe.stderr,
            }
        command = [sys.executable, "-m", "unittest", *mutation.paired_tests, "-v"]
        try:
            completed = subprocess.run(
                command,
                cwd=temp_root,
                env=env,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired as exc:
            output = (exc.stdout or "") + (exc.stderr or "")
            return {
                "mutation_id": mutation.mutation_id,
                "status": "TIMEOUT",
                "replacement_count": replacement_count,
                "target_path": mutation.path,
                "target_sha256_before": target_hash_before,
                "target_sha256_after": target_hash_after,
                "paired_tests": list(mutation.paired_tests),
                "matrix_ids": list(mutation.matrix_ids),
                "command": command,
                "transcript_sha256": hashlib.sha256(output.encode("utf-8")).hexdigest(),
            }
        output = completed.stdout + completed.stderr
        ran = re.search(r"Ran (\d+) test", output)
        failure = re.search(r"FAILED \(failures=(\d+)\)", output)
        has_error = "errors=" in output or "FAILED (errors=" in output
        has_skip = "skipped=" in output
        killed = (
            completed.returncode != 0
            and ran is not None
            and int(ran.group(1)) == len(mutation.paired_tests)
            and failure is not None
            and int(failure.group(1)) >= 1
            and not has_error
            and not has_skip
        )
        status = "KILLED_RED" if killed else "SURVIVED_OR_ERROR"
        return {
            "mutation_id": mutation.mutation_id,
            "generation": mutation.generation,
            "control_family": mutation.control_family,
            "status": status,
            "replacement_count": replacement_count,
            "target_path": mutation.path,
            "target_sha256_before": target_hash_before,
            "target_sha256_after": target_hash_after,
            "paired_tests": list(mutation.paired_tests),
            "matrix_ids": list(mutation.matrix_ids),
            "command": command,
            "return_code": completed.returncode,
            "tests_collected": int(ran.group(1)) if ran else None,
            "failure_class": "ASSERTION_FAILURE" if killed else "NOT_A_QUALIFYING_ASSERTION_FAILURE",
            "test_summary": next((line for line in output.splitlines() if line.startswith("FAILED")), None),
            "transcript_sha256": hashlib.sha256(output.encode("utf-8")).hexdigest(),
            "transcript_tail": output.splitlines()[-20:],
            "import_root": str(temp_root),
            "imported_module_paths": imported_paths,
        }


def run(
    source_root: Path,
    registry: Path | None,
    matrix: Path | None,
    timeout: int,
    freeze_receipt: Path | None = None,
    expected_freeze_sha256: str | None = None,
) -> dict[str, Any]:
    if len(MUTATIONS) != 57 or len({item.mutation_id for item in MUTATIONS}) != 57:
        raise RuntimeError("v0.4 successor mutation catalog must contain exactly 57 unique IDs")
    if [item.generation for item in MUTATIONS].count("R-WP4-02-PRESERVED") != 33:
        raise RuntimeError("mutation catalog must preserve exactly 33 predecessor controls")
    if [item.generation for item in MUTATIONS].count("R-WP4-03-NEW") != 21:
        raise RuntimeError("v0.4 successor mutation catalog must preserve exactly 21 pre-SEM-001 R-WP4-03 controls")
    if [item.generation for item in MUTATIONS].count("R-WP4-03-V04-SEM001") != 3:
        raise RuntimeError("v0.4 successor mutation catalog must contain exactly three SEM-001 controls")
    source_root = source_root.resolve()
    freeze_binding = _validate_freeze_receipt(source_root, freeze_receipt, expected_freeze_sha256)
    external_registry_checks = _validate_external_registries(registry, matrix)
    before = _source_manifest(source_root)
    results = [_run_mutation(source_root, mutation, timeout) for mutation in MUTATIONS]
    after = _source_manifest(source_root)
    counts = {
        name: sum(item["status"] == name for item in results)
        for name in ("KILLED_RED", "SURVIVED_OR_ERROR", "HARNESS_ERROR", "TIMEOUT")
    }
    source_mutated = before != after
    accepted = (
        counts["KILLED_RED"] == len(MUTATIONS)
        and sum(counts[name] for name in counts if name != "KILLED_RED") == 0
        and not source_mutated
        and freeze_binding["bound"]
    )
    return {
        "schema_version": "m3top3-r-wp4-03-mutation-receipt-v3",
        "claim_scope": "INTERNAL_ENGINEERING_NOT_IVA",
        "authority_state": "AUTHORITATIVE_CANDIDATE_BOUND" if freeze_binding["bound"] else "WIP_UNBOUND",
        "candidate_freeze_binding": freeze_binding,
        "registry_contract": "R_WP4_03_MUTATION_REGISTRY_v0.4.1_SUCCESSOR",
        "predecessor_design_contract": {
            "registry_version": "v0.1",
            "exact_total": 50,
            "legacy_preserved": 33,
            "r_wp4_03_new": 17,
            "retroactively_modified": False,
        },
        "successor_design_delta": {
            "added_count": 7,
            "reason": "four v0.2 control seams plus three v0.4 SEM-001 semantic-preservation controls",
            "added_controls": [
                {"matrix_id": "LIN-006", "stable_code": "EXTRA_LINEAGE_COMPONENT"},
                {"matrix_id": "UNI-009", "stable_code": "ELIGIBILITY_RELEASE_NOT_COMPLETE"},
                {"matrix_id": "REF-007", "stable_code": "OUTCOME_COMPONENT_LINEAGE_MISMATCH"},
                {"matrix_id": "IMM-001", "stable_code": "IMMUTABLE_RELEASE_COLLISION"},
                {"mutation_id": "MUT-R03-TOP3-OUTCOME-VIEW", "control": "LEGACY_TOP3_OUTCOME_VIEW"},
                {"mutation_id": "MUT-R03-TOP3-METRIC-POPULATION", "control": "LEGACY_TOP3_METRIC_POPULATION"},
                {"mutation_id": "MUT-R03-RESULT-VIEW-VERSION-IDENTITY", "control": "RESULT_VIEW_VERSION_IDENTITY"},
            ],
        },
        "source_root": str(source_root),
        "source_manifest_before_sha256": _manifest_digest(before),
        "source_manifest_after_sha256": _manifest_digest(after),
        "source_manifest_file_count": len(before),
        "source_manifest": before,
        "source_mutated": source_mutated,
        "candidate_git": _git_identity(source_root),
        "harness_path": str(Path(__file__).resolve()),
        "harness_sha256": _sha256_file(Path(__file__).resolve()),
        "registry_path": str(registry.resolve()) if registry else None,
        "registry_sha256": _sha256_file(registry),
        "matrix_path": str(matrix.resolve()) if matrix else None,
        "matrix_sha256": _sha256_file(matrix),
        "requested_mutations": len(MUTATIONS),
        "legacy_mutations": 33,
        "new_mutations": 24,
        "killed_red": counts["KILLED_RED"],
        "survived_or_error": counts["SURVIVED_OR_ERROR"],
        "harness_error": counts["HARNESS_ERROR"],
        "timeout": counts["TIMEOUT"],
        "skipped": 0,
        "external_registry_checks": external_registry_checks,
        "status": "PASS" if accepted else "FAIL",
        "results": results,
    }


class MutationSemanticProbeTests(unittest.TestCase):
    """Narrow semantic probes used only by registered mutation cases."""

    def _assert_code(self, code: str, action, exit_code: int) -> None:
        from tools.m3top3.admission import M3Top3AdmissionError

        with self.assertRaises(M3Top3AdmissionError) as caught:
            action()
        self.assertEqual((caught.exception.code, caught.exception.exit_code), (code, exit_code))

    @staticmethod
    def _read_rows(path: Path) -> list[dict[str, Any]]:
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

    @staticmethod
    def _pit_semantic(row: dict[str, Any]) -> dict[str, Any]:
        fields = (
            "company_id", "snapshot_cutoff_at", "snapshot_schema_version", "snapshot_revision",
            "f1_f2_effective_refs", "f3_observation_refs", "evidence_refs", "dataset_refs",
            "universe_lineage_manifest_hash", "universe_authority_status", "universe_release_id",
            "universe_release_version", "universe_release_revision", "universe_release_hash",
            "universe_release_status", "denominator_release_id", "denominator_release_version",
            "denominator_release_revision", "denominator_release_hash", "denominator_release_status",
            "denominator_member_id", "eligibility_record_id", "eligibility_status",
            "tradability_state_ref", "retrieval_receipt_id", "retrieval_source_hash",
        )
        return {field: row.get(field) for field in fields}

    def _rewrite_snapshot(
        self,
        snapshot_dir: Path,
        pit_rows: list[dict[str, Any]],
        model_rows: list[dict[str, Any]],
        audit_rows: list[dict[str, Any]],
        manifest: dict[str, Any],
        *,
        rebind_receipts: bool = False,
        rebind_pits: bool = False,
    ) -> None:
        from tools.m3top3.admission import _snapshot_manifest_identity_payload
        from tools.m3top3.core import aggregate_hash, canonical_json_bytes, deterministic_id, sha256_hex

        if rebind_receipts:
            by_key: dict[tuple[str, str], dict[str, Any]] = {}
            for receipt in audit_rows:
                payload = {key: value for key, value in receipt.items() if key != "retrieval_receipt_id"}
                receipt["retrieval_receipt_id"] = deterministic_id("retrieval", payload)
                by_key[(receipt["company_id"], receipt["cutoff_at"])] = receipt
            for pit, model in zip(pit_rows, model_rows):
                receipt = by_key[(pit["company_id"], pit["snapshot_cutoff_at"])]
                for row in (pit, model):
                    row["retrieval_receipt_id"] = receipt["retrieval_receipt_id"]
                    row["retrieval_source_hash"] = receipt["source_hash"]
            rebind_pits = True
        if rebind_pits:
            models = {(row["company_id"], row["snapshot_cutoff_at"]): row for row in model_rows}
            for pit in pit_rows:
                pit["pit_snapshot_id"] = deterministic_id("pit", self._pit_semantic(pit))
                pit["capture_run_id"] = deterministic_id(
                    "capture", {"pit_snapshot_id": pit["pit_snapshot_id"], "generator_version": pit["generator_version"]}
                )
                models[(pit["company_id"], pit["snapshot_cutoff_at"])]["pit_snapshot_id"] = pit["pit_snapshot_id"]
        payloads: dict[str, bytes] = {
            "pit_snapshot.jsonl": b"".join(canonical_json_bytes(row) + b"\n" for row in pit_rows),
            "model_input.jsonl": b"".join(canonical_json_bytes(row) + b"\n" for row in model_rows),
            "retrieval_audit.jsonl": b"".join(canonical_json_bytes(row) + b"\n" for row in audit_rows),
        }
        for name, payload in payloads.items():
            (snapshot_dir / name).write_bytes(payload)
        manifest.update(
            {
                "pit_file_sha256": sha256_hex(payloads["pit_snapshot.jsonl"]),
                "model_input_file_sha256": sha256_hex(payloads["model_input.jsonl"]),
                "retrieval_audit_file_sha256": sha256_hex(payloads["retrieval_audit.jsonl"]),
                "pit_row_count": len(pit_rows),
                "model_input_row_count": len(model_rows),
                "retrieval_audit_row_count": len(audit_rows),
                "retrieval_audit_content_hash": aggregate_hash([sha256_hex(row) for row in audit_rows]),
                "retrieval_receipt_ids": sorted(row["retrieval_receipt_id"] for row in audit_rows),
                "retrieval_source_hashes": sorted({row["source_hash"] for row in audit_rows}),
                "snapshot_content_hash": aggregate_hash(
                    [sha256_hex(row) for row in pit_rows]
                    + [sha256_hex(row) for row in model_rows]
                    + [sha256_hex(row) for row in audit_rows]
                ),
            }
        )
        manifest["snapshot_manifest_identity_hash"] = sha256_hex(_snapshot_manifest_identity_payload(manifest))
        (snapshot_dir / "manifest.json").write_bytes(canonical_json_bytes(manifest) + b"\n")

    def _materialized_snapshot(self, root: Path):
        from tools.m3top3.tests._known_failure_helpers import materialize_ready_snapshot

        snapshot_dir, _, _, _ = materialize_ready_snapshot(root)
        return (
            snapshot_dir,
            self._read_rows(snapshot_dir / "pit_snapshot.jsonl"),
            self._read_rows(snapshot_dir / "model_input.jsonl"),
            self._read_rows(snapshot_dir / "retrieval_audit.jsonl"),
            json.loads((snapshot_dir / "manifest.json").read_text(encoding="utf-8")),
        )

    def test_retrieval_count_reconciliation(self) -> None:
        from tools.m3top3.admission import verify_snapshot_artifacts

        with tempfile.TemporaryDirectory() as tmp:
            snapshot, pit, model, audit, manifest = self._materialized_snapshot(Path(tmp))
            audit[0]["source_matching_rows"] += 1
            self._rewrite_snapshot(snapshot, pit, model, audit, manifest, rebind_receipts=True)
            self._assert_code("RETRIEVAL_AUDIT_SEMANTIC_MISMATCH", lambda: verify_snapshot_artifacts(snapshot), 3)

    def test_immutable_json_result_collision(self) -> None:
        from tools.m3top3.ledger import ImmutableJsonArtifactStore

        with tempfile.TemporaryDirectory() as tmp:
            store = ImmutableJsonArtifactStore(Path(tmp) / "run.json")
            self.assertEqual(store.admit({"run": "SAME", "payload": "A"}), "APPENDED")
            self._assert_code("NONDETERMINISTIC_RERUN", lambda: store.admit({"run": "SAME", "payload": "B"}), 3)

    def test_multi_component_manifest_required(self) -> None:
        from tools.m3top3.admission import verify_price_component_manifest

        provider = type("Provider", (), {"paths": ["a.parquet", "b.parquet"]})()
        self._assert_code("PRICE_COMPONENT_MANIFEST_REQUIRED", lambda: verify_price_component_manifest(provider, None), 3)

    def test_claim_locks(self) -> None:
        from tools.m3top3.admission import admit_claim_locks

        for key in ("official_golden", "full_replay"):
            self._assert_code("OFFICIAL_REPLAY_GLOBALLY_BLOCKED", lambda key=key: admit_claim_locks({key: True}), 4)

    def test_component_digest_is_path_independent(self) -> None:
        from tools.m3top3.admission import canonical_component_set_digest
        from tools.m3top3.core import hash_file

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = root / "first.bin"
            second = root / "relocated" / "second.bin"
            first.write_bytes(b"same exact bytes")
            second.parent.mkdir()
            second.write_bytes(first.read_bytes())
            base = {
                "component_id": "C1", "logical_name": "portable.bin", "byte_size": first.stat().st_size,
                "artifact_sha256": hash_file(first), "semantic_role": "TEST",
            }
            self.assertEqual(
                canonical_component_set_digest([{**base, "path": str(first)}]),
                canonical_component_set_digest([{**base, "path": str(second)}]),
            )

    def test_universe_runtime_slice_exact(self) -> None:
        from datetime import date
        from tools.m3top3.admission import verify_universe_release
        from tools.m3top3.providers import StaticUniverseProvider, UniverseState

        c1 = UniverseState("C1", "000001", date(2020, 1, 1), None, True, True, "U1")
        c2 = UniverseState("C2", "000002", date(2020, 1, 1), None, True, True, "U2")
        provider = StaticUniverseProvider([c1, c2], denominator_states=[c1])
        self._assert_code(
            "UNIVERSE_RELEASE_RUNTIME_SLICE_MISMATCH",
            lambda: verify_universe_release(provider, date(2025, 1, 2), [c1]),
            3,
        )

    def test_partition_digest_reconciliation(self) -> None:
        from tools.m3top3.admission import _snapshot_manifest_identity_payload, verify_snapshot_artifacts
        from tools.m3top3.core import canonical_json_bytes, sha256_hex

        with tempfile.TemporaryDirectory() as tmp:
            snapshot, _, _, _, manifest = self._materialized_snapshot(Path(tmp))
            manifest["eligible_set_digest"] = "f" * 64
            manifest["snapshot_manifest_identity_hash"] = sha256_hex(_snapshot_manifest_identity_payload(manifest))
            (snapshot / "manifest.json").write_bytes(canonical_json_bytes(manifest) + b"\n")
            self._assert_code("ELIGIBLE_SET_DIGEST_MISMATCH", lambda: verify_snapshot_artifacts(snapshot), 3)

    def test_dataset_refs_one_to_one(self) -> None:
        from tools.m3top3 import admission
        from tools.m3top3.admission import verify_snapshot_artifacts

        with tempfile.TemporaryDirectory() as tmp:
            governed_domains = admission.MODEL_INPUT_DATASET_DOMAINS
            if "TRADING_CALENDAR_RELEASE" not in governed_domains:
                admission.MODEL_INPUT_DATASET_DOMAINS = governed_domains + ("TRADING_CALENDAR_RELEASE",)
            try:
                snapshot, pit, model, audit, manifest = self._materialized_snapshot(Path(tmp))
            finally:
                admission.MODEL_INPUT_DATASET_DOMAINS = governed_domains
            for row in (*pit, *model):
                row["dataset_refs"] = [ref for ref in row["dataset_refs"] if ref["domain"] != "TRADING_CALENDAR_RELEASE"]
            self._rewrite_snapshot(snapshot, pit, model, audit, manifest, rebind_pits=True)
            self._assert_code("DATASET_REF_DOMAIN_MISSING", lambda: verify_snapshot_artifacts(snapshot), 3)

    def test_pit_price_ref_identity_binding(self) -> None:
        from tools.m3top3 import admission
        from tools.m3top3.admission import verify_snapshot_artifacts

        with tempfile.TemporaryDirectory() as tmp:
            governed_domains = admission.MODEL_INPUT_DATASET_DOMAINS
            if "PRICE_RELEASE" not in governed_domains:
                admission.MODEL_INPUT_DATASET_DOMAINS = governed_domains + ("PRICE_RELEASE",)
            try:
                snapshot, pit, model, audit, manifest = self._materialized_snapshot(Path(tmp))
            finally:
                admission.MODEL_INPUT_DATASET_DOMAINS = governed_domains
            for row in (*pit, *model):
                row["dataset_refs"] = [ref for ref in row["dataset_refs"] if ref["domain"] != "PRICE_RELEASE"]
            self._rewrite_snapshot(snapshot, pit, model, audit, manifest, rebind_pits=True)
            self._assert_code("DATASET_REF_DOMAIN_MISSING", lambda: verify_snapshot_artifacts(snapshot), 3)

    def test_revision_tuple_coherence(self) -> None:
        from tools.m3top3.admission import verify_snapshot_artifacts

        with tempfile.TemporaryDirectory() as tmp:
            snapshot, pit, model, audit, manifest = self._materialized_snapshot(Path(tmp))
            pit[0]["snapshot_revision"] = 1
            model[0]["snapshot_revision"] = 1
            self._rewrite_snapshot(snapshot, pit, model, audit, manifest, rebind_pits=True)
            self._assert_code("SNAPSHOT_REVISION_MISMATCH", lambda: verify_snapshot_artifacts(snapshot), 3)

    def test_diagnostic_scorer_config_exact(self) -> None:
        from tools.m3top3.admission import DIAGNOSTIC_LINEAGE_STATE, preflight_diagnostic_scorer
        from tools.m3top3.core import hash_file, sha256_hex

        artifact = Path(__file__).resolve()
        config = b'{"fixture":"exact"}'
        receipt = {
            "state": DIAGNOSTIC_LINEAGE_STATE,
            "scorer_plugin": "fixture:Scorer",
            "scorer_artifact_path": str(artifact),
            "scorer_artifact_sha256": hash_file(artifact),
            "scorer_artifact_byte_size": artifact.stat().st_size,
            "config_sha256": sha256_hex(config),
            "config_byte_size": len(config),
            "model_id": "M", "model_version": "V", "model_schema_version": "S", "feature_set_version": "F",
        }
        self._assert_code("SCORER_IDENTITY_MISMATCH", lambda: preflight_diagnostic_scorer(receipt, config + b" "), 4)

    def test_scoring_full_u_missing_member(self) -> None:
        from tools.m3top3.backtest import _verify_scoring_coverage
        from tools.m3top3.model_interface import ScoreResult

        inputs = [
            {"pit_snapshot_id": "P1", "company_id": "C1", "security_code": "000001", "entry_eligible": "TRUE"},
            {"pit_snapshot_id": "P2", "company_id": "C2", "security_code": "000002", "entry_eligible": "FALSE"},
        ]
        scores = [ScoreResult("S1", "P1", "C1", "000001", "V", Decimal("1"), "DIAGNOSTIC", [])]
        scorer = type("Scorer", (), {"model_version": "V"})()
        self._assert_code("FULL_SCORER_OUTPUT_SET_MEMBER_MISSING", lambda: _verify_scoring_coverage(inputs, scores, scorer), 3)

    def test_rank_sequence_integrity(self) -> None:
        from tools.m3top3.backtest import _verify_ranking_coverage

        inputs = [
            {"pit_snapshot_id": "P1", "company_id": "C1", "security_code": "000001", "entry_eligible": "TRUE", "denominator_member_id": "D1", "eligibility_record_id": "E1"},
            {"pit_snapshot_id": "P2", "company_id": "C2", "security_code": "000002", "entry_eligible": "TRUE", "denominator_member_id": "D2", "eligibility_record_id": "E2"},
        ]
        ranked = [
            {"pit_snapshot_id": "P1", "company_id": "C1", "security_code": "000001", "model_score_id": "S1", "rank": 1, "selected_top3": True, "denominator_member_id": "D1", "eligibility_record_id": "E1", "eligibility_at_snapshot": "TRUE"},
            {"pit_snapshot_id": "P2", "company_id": "C2", "security_code": "000002", "model_score_id": "S2", "rank": 3, "selected_top3": False, "denominator_member_id": "D2", "eligibility_record_id": "E2", "eligibility_at_snapshot": "TRUE"},
        ]
        self._assert_code("RANK_SEQUENCE_INTEGRITY_FAILURE", lambda: _verify_ranking_coverage(ranked, inputs, {"eligible_row_count": 2}), 3)

    def test_validation_run_id_binding(self) -> None:
        from tools.m3top3.backtest import (
            FULL_UNIVERSE_VIEW_VERSION,
            RESULT_CONTRACT_VERSION,
            RUN_IDENTITY_FIELDS,
            SELECTED_TOP3_METRICS_VIEW_VERSION,
            verify_validation_run_identity,
        )

        payload = {field: f"value:{field}" for field in RUN_IDENTITY_FIELDS}
        payload.update(
            {
                "result_contract_version": RESULT_CONTRACT_VERSION,
                "selected_top3_metrics_view_version": SELECTED_TOP3_METRICS_VIEW_VERSION,
                "full_universe_view_version": FULL_UNIVERSE_VIEW_VERSION,
                "result_revision": 0,
            }
        )
        self._assert_code(
            "RUN_ID_LINEAGE_MISMATCH",
            lambda: verify_validation_run_identity(
                {
                    "validation_run_identity_payload": payload,
                    "validation_run_id": "forged-validation-run-id",
                }
            ),
            3,
        )

    def test_metric_denominator_integrity(self) -> None:
        from tools.m3top3.backtest import MetricsEngine

        self._assert_code("METRIC_DENOMINATOR_INTEGRITY_FAILURE", lambda: MetricsEngine().summarize([], 1), 3)

    def test_full_outcome_set_persistence(self) -> None:
        from tools.m3top3.admission import M3Top3AdmissionError
        from tools.m3top3.ledger import PredictionLedger
        from tools.m3top3.tests._known_failure_helpers import (
            diagnostic_runner,
            materialize_external_fixture,
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture = materialize_external_fixture(
                root,
                eligibility_status_by_company={"C4": "ELIGIBLE"},
            )
            runner, _ = diagnostic_runner(
                fixture["price"],
                fixture["dates"],
                fixture["scorer"],
                execution_lineage=fixture["lineage"],
            )
            try:
                result = runner.run_snapshot(
                    fixture["snapshot_dir"],
                    root / "full-result",
                    PredictionLedger(root / "full-ledger.jsonl"),
                )
            except M3Top3AdmissionError as exc:
                self.fail(f"full outcome persistence guard rejected its own valid baseline: {exc.code}/{exc.exit_code}")
            self.assertEqual(result["full_universe_outcome_count"], 4)
            self.assertEqual(len(result["full_universe_outcomes"]), 4)
            self.assertEqual(len(result["outcomes"]), 3)
            self.assertEqual(
                result["outcomes"],
                [row for row in result["full_universe_outcomes"] if row["selected_top3"]],
            )

    def test_full_ledger_ranked_count(self) -> None:
        from tools.m3top3.ledger import FullRunArtifactStore, PredictionLedger
        from tools.m3top3.tests.test_r_wp4_03_ledger_v02 import _result

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = _result("R1", "L1")
            result["ranked_count"] = 1
            store = FullRunArtifactStore(root / "runs" / "R1.json")
            self._assert_code("INCOMPLETE_RESULT_PUBLICATION", lambda: store._payloads(result), 3)

    def test_extra_lineage_component_guard(self) -> None:
        from tools.m3top3.admission import admit_execution_lineage_bundle, canonical_component_set_digest
        from tools.m3top3.core import hash_file
        from tools.m3top3.tests.r_wp4_03_matrix_harness import _lineage_bundle, _rewrite_bundle, _write_json

        with tempfile.TemporaryDirectory() as tmp:
            path, bundle = _lineage_bundle(Path(tmp))
            release = bundle["releases"][0]
            manifest_path = Path(release["manifest_path"])
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            extra_path = manifest_path.with_name("manifest-only-live-component.bin")
            extra_path.write_bytes(b"independently registered live bytes\n")
            manifest["components"].append(
                {
                    "component_id": f"{release['release_id']}:manifest-only",
                    "logical_name": extra_path.name,
                    "path": str(extra_path),
                    "byte_size": extra_path.stat().st_size,
                    "artifact_sha256": hash_file(extra_path),
                    "semantic_role": release["semantic_role"],
                }
            )
            manifest["component_set_digest"] = canonical_component_set_digest(manifest["components"])
            _write_json(manifest_path, manifest)
            release["manifest_sha256"] = hash_file(manifest_path)
            self._assert_code(
                "EXTRA_LINEAGE_COMPONENT",
                lambda: admit_execution_lineage_bundle(path, _rewrite_bundle(path, bundle)),
                3,
            )

    def test_eligibility_release_complete_guard(self) -> None:
        from tools.m3top3.admission import verify_universe_release
        from tools.m3top3.core import hash_file
        from tools.m3top3.providers import JsonlUniverseProvider, UniverseState
        from tools.m3top3.tests.r_wp4_03_matrix_harness import (
            _external_universe,
            _jsonl,
            _rebind_external_manifest,
            _write_jsonl,
            business_dates,
        )

        with tempfile.TemporaryDirectory() as tmp:
            snapshot_date = business_dates()[0]
            states = [
                UniverseState("C1", "005930", snapshot_date.replace(year=2020), None, True, True, "U1", "DIAGNOSTIC_VERIFIED"),
                UniverseState("C2", "000660", snapshot_date.replace(year=2020), None, True, True, "U2", "DIAGNOSTIC_VERIFIED"),
            ]
            universe, denominator, manifest, _ = _external_universe(Path(tmp), states, [snapshot_date])
            rows = _jsonl(denominator)
            rows[0]["eligibility_status"] = "UNRESOLVED"
            _write_jsonl(denominator, rows)
            _rebind_external_manifest(universe, denominator, manifest)
            provider = JsonlUniverseProvider(
                universe,
                "U-MATRIX-EXTERNAL",
                "DIAGNOSTIC",
                denominator_path=denominator,
                lineage_manifest_path=manifest,
                lineage_manifest_hash=hash_file(manifest),
            )
            self._assert_code(
                "ELIGIBILITY_RELEASE_NOT_COMPLETE",
                lambda: verify_universe_release(provider, snapshot_date, provider.states_at(snapshot_date)),
                2,
            )

    def test_outcome_component_lineage_guard(self) -> None:
        from tools.m3top3.backtest import ValidationRunner
        from tools.m3top3.ledger import PredictionLedger
        from tools.m3top3.model_interface import RankingEngine
        from tools.m3top3.outcome import ExplicitWindowResolver, OutcomeBuilder
        from tools.m3top3.tests._known_failure_helpers import (
            CountingScorer,
            diagnostic_scorer_admission,
            materialize_ready_snapshot,
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            snapshot_dir, dates, price, _ = materialize_ready_snapshot(root)
            manifest = json.loads((snapshot_dir / "manifest.json").read_text(encoding="utf-8"))
            ref_map = {ref["domain"]: dict(ref) for ref in manifest["lineage_releases"]}
            ref_map["CORPORATE_ACTION_RELEASE"]["artifact_sha256"] = "f" * 64
            refs = [
                ref_map[domain]
                for domain in (
                    "PRICE_RELEASE",
                    "CORPORATE_ACTION_RELEASE",
                    "TRADING_CALENDAR_RELEASE",
                    "WINDOW_REGISTRY_RELEASE",
                )
            ]
            scorer = CountingScorer()
            config, receipt = diagnostic_scorer_admission(scorer)
            windows = ExplicitWindowResolver({dates[0].isoformat(): dates[5].isoformat()}, "test-window-v1")
            runner = ValidationRunner(
                scorer,
                RankingEngine("COMPANY_ID_ASC_DIAGNOSTIC"),
                OutcomeBuilder(price, windows, dataset_refs=refs),
                execution_mode="DIAGNOSTIC",
                scorer_config_bytes=config,
                diagnostic_scorer_identity=receipt,
            )
            self._assert_code(
                "OUTCOME_COMPONENT_LINEAGE_MISMATCH",
                lambda: runner.run_snapshot(
                    snapshot_dir,
                    root / "output",
                    PredictionLedger(root / "prediction-ledger.jsonl"),
                ),
                3,
            )

    def _sem001_four_member_result(self) -> dict[str, Any]:
        from datetime import date

        from tools.m3top3.ledger import PredictionLedger
        from tools.m3top3.providers import InMemoryFeatureProvider,StaticUniverseProvider,UniverseState
        from tools.m3top3.snapshot import SnapshotBuildConfig,SnapshotBuilder,SnapshotStore
        from tools.m3top3.tests._known_failure_helpers import business_dates,diagnostic_runner,price_provider

        temporary=tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root=Path(temporary.name)
        dates=business_dates(count=30)
        codes=("005930","000660","035420","051910")
        companies=("C1","C2","C3","C4")
        exit_open={"005930":110,"000660":120,"035420":130,"051910":10}
        hold_high={"005930":120,"000660":130,"035420":140,"051910":110}
        price_rows=[]
        for code in codes:
            for index,trading_date in enumerate(dates):
                open_value=exit_open[code] if index==6 else 100
                price_rows.append({
                    "date":trading_date.isoformat(),"code":code,"open":open_value,
                    "high":max(open_value,hold_high[code]),"low":min(open_value,90),
                    "close":open_value,"volume":1000+index,
                })
        price=price_provider(root,price_rows)
        states=[
            UniverseState(company,code,date(2020,1,1),None,True,True,f"U{index}")
            for index,(company,code) in enumerate(zip(companies,codes),1)
        ]
        features=InMemoryFeatureProvider([
            {
                "company_id":company,"feature_id":"diagnostic_score","value":str(10-index),
                "publication_at":"2025-01-02T10:00:00+09:00",
            }
            for index,company in enumerate(companies)
        ])
        builder=SnapshotBuilder(
            StaticUniverseProvider(states,"U-SEM001-MUTATION","DIAGNOSTIC"),
            features,
            price,
            SnapshotBuildConfig(),
        )
        built=builder.build(dates[0])
        snapshot_root=root / "sem001-snapshots"
        SnapshotStore(snapshot_root).write(built,{"generator_version":"sem001-mutation-v0.4"})
        snapshot_dir=snapshot_root / dates[0].isoformat()
        runner,_=diagnostic_runner(price,dates)
        try:
            return runner.run_snapshot(
                snapshot_dir,
                root / "sem001-result",
                PredictionLedger(root / "sem001-ledger.jsonl"),
            )
        except BaseException as exc:
            self.fail(f"valid SEM-001 four-member execution failed closed: {type(exc).__name__}: {exc}")

    def test_sem001_top3_outcome_view(self) -> None:
        result=self._sem001_four_member_result()
        self.assertEqual(result["outcome_count"],3)
        self.assertEqual(result["selected_top3_outcome_count"],3)
        self.assertEqual(result["full_universe_outcome_count"],4)
        self.assertEqual(result["outcomes"],result["selected_top3_outcomes"])
        self.assertEqual([row["rank"] for row in result["outcomes"]],[1,2,3])

    def test_sem001_top3_metric_population(self) -> None:
        result=self._sem001_four_member_result()
        self.assertEqual(result["metrics"],result["selected_top3_metrics"])
        self.assertEqual(result["metrics"]["mean_return"],"0.2")
        self.assertEqual(result["metrics"]["win_rate"],"1")
        self.assertEqual(result["metrics"]["valid_return_count"],3)
        self.assertEqual(result["full_universe_outcome_count"],4)

    def test_sem001_result_view_version_identity(self) -> None:
        from tools.m3top3.core import deterministic_id

        result=self._sem001_four_member_result()
        payload=result["validation_run_identity_payload"]
        for field in (
            "result_contract_version",
            "selected_top3_metrics_view_version",
            "full_universe_view_version",
        ):
            self.assertEqual(payload.get(field),result.get(field),field)
        self.assertEqual(result["validation_run_id"],deterministic_id("validationrun",payload))

    def test_immutable_release_collision_guard(self) -> None:
        from tools.m3top3.ledger import ImmutableReleaseStore

        with tempfile.TemporaryDirectory() as tmp:
            store = ImmutableReleaseStore(Path(tmp) / "release-identity.json")
            self.assertEqual(store.admit("PRICE-R1", b"one"), "APPENDED")
            self._assert_code(
                "IMMUTABLE_RELEASE_COLLISION",
                lambda: store.admit("PRICE-R1", b"two"),
                3,
            )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the exact 57-case R-WP4-03 v0.4.1 successor mutation suite")
    parser.add_argument("--source-root", required=True)
    parser.add_argument("--registry")
    parser.add_argument("--matrix")
    parser.add_argument("--freeze-receipt")
    parser.add_argument("--freeze-receipt-sha256")
    parser.add_argument("--json-out")
    parser.add_argument("--timeout", type=int, default=45)
    args = parser.parse_args(argv)
    receipt = run(
        Path(args.source_root),
        Path(args.registry) if args.registry else None,
        Path(args.matrix) if args.matrix else None,
        args.timeout,
        Path(args.freeze_receipt) if args.freeze_receipt else None,
        args.freeze_receipt_sha256,
    )
    payload = json.dumps(receipt, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    if args.json_out:
        output = Path(args.json_out)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0 if receipt["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
