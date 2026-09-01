from __future__ import annotations

import copy
import hashlib
import json
import os
import re
import runpy
import subprocess
import sys
import tempfile
from argparse import Namespace
from contextlib import contextmanager
from pathlib import Path

MODULE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MODULE_DIR))
CONTROL_DIR = MODULE_DIR.parents[1] / "control/m3top3/public-data-source-admission/v1.0"

import finance_page100_g11c9_selector_successor as g11c9  # noqa: E402


class RaisesResult:
    value: BaseException | None = None


@contextmanager
def raises(exception_type: type[BaseException], match: str | None = None):
    result = RaisesResult()
    try:
        yield result
    except exception_type as exc:
        result.value = exc
        if match is not None and re.search(match, str(exc)) is None:
            raise AssertionError(f"{exc!r} does not match {match!r}") from exc
    else:
        raise AssertionError(f"expected {exception_type.__name__}")


def h(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def raw_ref() -> g11c9.SealedRawReference:
    return g11c9.SealedRawReference(
        key=(
            "raw/public-data-api/M3TOP3-FINANCE-STOCK-RIGHTS-v1/"
            "_pilot_generation/G11C9/20260901200940/page-5.json"
        ),
        version_id="exact-version-id",
        sha256=h("sealed raw page"),
    )


def row(
    ordinal: int,
    custody_hash: str | None,
    identity_hash: str | None,
    *,
    page_no: int = 5,
    page_item_ordinal: int = 1,
) -> g11c9.HashedSourceRow:
    return g11c9.HashedSourceRow(
        bas_dt=g11c9.SEED_BASE_DATE,
        page_no=page_no,
        page_item_ordinal=page_item_ordinal,
        global_row_ordinal=ordinal,
        custody_key_sha256=custody_hash,
        observed_identity_sha256=identity_hash,
    )


def seeded_state() -> g11c9.ProjectionState:
    return g11c9.ProjectionState(
        source_rows=40,
        eligible_rows=35,
        excluded_rows=5,
        missing_rows=0,
        identity_map={h("custody-a"): h("identity-a")},
        excluded_global_row_ordinals=[36, 37, 38, 39, 40],
    )


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, sort_keys=True) + "\n", encoding="utf-8")


def safe_adapter_document() -> dict:
    path = MODULE_DIR / "finance_page100_g11c9_live_adapter.py"
    return {
        "ready": True,
        "path": g11c9.LIVE_ADAPTER_REPO_PATH,
        "sha256": g11c9.sha256_file(path),
        "git_blob": g11c9.git_blob_sha1_file(path),
        "factory_symbol": g11c9.LIVE_ADAPTER_FACTORY_SYMBOL,
        "interface_version": g11c9.LIVE_ADAPTER_INTERFACE_VERSION,
    }


def predecessor_ineligible_preparation_binding() -> dict:
    return {
        "preparation_commit": g11c9.PREDECESSOR_G11C1_PREPARATION_COMMIT,
        "preparation_tree": g11c9.PREDECESSOR_G11C1_PREPARATION_TREE,
        "activation_created": False,
        "precheck_activation_created": False,
        "live_activation_created": False,
        "precheck_run_created": False,
        "live_run_created": False,
        "reuse_authorized": False,
        "terminal_receipt_path": g11c9.PREDECESSOR_G11C1_TERMINAL_RECEIPT_PATH,
        "terminal_receipt_sha256": g11c9.PREDECESSOR_G11C1_TERMINAL_RECEIPT_SHA256,
        "terminal_receipt_git_blob":
            g11c9.PREDECESSOR_G11C1_TERMINAL_RECEIPT_GIT_BLOB,
        "terminal_receipt_payload_sha256":
            g11c9.PREDECESSOR_G11C1_TERMINAL_RECEIPT_PAYLOAD_SHA256,
        "terminal_receipt_bytes": g11c9.PREDECESSOR_G11C1_TERMINAL_RECEIPT_BYTES,
    }


def consumed_g11c1_identity_lists() -> dict:
    return {
        field_name: list(values)
        for field_name, values in g11c9.PREDECESSOR_G11C1_IDENTITIES.items()
    }


def predecessor_invalidated_g11c2_binding() -> dict:
    return g11c9.predecessor_invalidated_g11c2_binding()


def predecessor_terminal_g11c3_binding() -> dict:
    return g11c9.predecessor_terminal_g11c3_binding()


def predecessor_terminal_g11c4_binding() -> dict:
    return g11c9.predecessor_terminal_g11c4_binding()


def predecessor_terminal_g11c5_binding() -> dict:
    return g11c9.predecessor_terminal_g11c5_binding()


def predecessor_terminal_g11c6_binding() -> dict:
    return g11c9.predecessor_terminal_g11c6_binding()


def predecessor_terminal_g11c7_binding() -> dict:
    authority_path = CONTROL_DIR / g11c9.AUTHORITY_FILENAME
    return json.loads(authority_path.read_text(encoding="utf-8"))[
        "predecessor_terminal_g11c7_binding"
    ]


def predecessor_invalidated_g11c8_binding() -> dict:
    authority_path = CONTROL_DIR / g11c9.AUTHORITY_FILENAME
    return json.loads(authority_path.read_text(encoding="utf-8"))[
        "predecessor_invalidated_g11c8_binding"
    ]


def consumed_predecessor_lineage() -> dict:
    result = consumed_g11c1_identity_lists()
    for field_name, values in g11c9.PREDECESSOR_G11C2_IDENTITIES.items():
        result.setdefault(field_name, []).extend(values)
    result.update({
        "g11c2_precheck_run_id": g11c9.PREDECESSOR_G11C2_PRECHECK_RUN_ID,
        "g11c2_precheck_run_attempt": g11c9.PREDECESSOR_G11C2_PRECHECK_RUN_ATTEMPT,
        "g11c2_precheck_rerun_authorized": False,
        "g11c2_live_run_exists": False,
        "g11c2_activation_reuse_authorized": False,
        "g11c2_generation_reuse_authorized": False,
    })
    for field_name, values in g11c9.PREDECESSOR_G11C3_IDENTITIES.items():
        result.setdefault(field_name, []).extend(values)
    result.update({
        "g11c3_precheck_run_id": 33472741288,
        "g11c3_precheck_run_attempt": 1,
        "g11c3_live_run_id": 33473465774,
        "g11c3_live_run_attempt": 1,
        "g11c3_credentials_issued": False,
        "g11c3_runner_started": False,
        "g11c3_activation_reuse_authorized": False,
        "g11c3_generation_reuse_authorized": False,
    })
    for field_name, values in g11c9.PREDECESSOR_G11C4_IDENTITIES.items():
        result.setdefault(field_name, []).extend(values)
    result.update({
        "g11c4_precheck_run_id": g11c9.PREDECESSOR_G11C4_PRECHECK_RUN_ID,
        "g11c4_precheck_run_attempt": g11c9.PREDECESSOR_G11C4_PRECHECK_RUN_ATTEMPT,
        "g11c4_precheck_rerun_authorized": False,
        "g11c4_credentials_issued": 0,
        "g11c4_runner_started": False,
        "g11c4_activation_reuse_authorized": False,
        "g11c4_generation_reuse_authorized": False,
    })
    for field_name, values in g11c9.PREDECESSOR_G11C5_IDENTITIES.items():
        result.setdefault(field_name, []).extend(values)
    result.update({
        "consumed_github_runs": list(g11c9.REQUIRED_NO_RERUN_RUNS),
        "consumed_g11c4_precheck_run": g11c9.PREDECESSOR_G11C4_PRECHECK_RUN_ID,
        "consumed_g11c5_precheck_run": g11c9.PREDECESSOR_G11C5_PRECHECK_RUN_ID,
        "g11c5_precheck_run_id": g11c9.PREDECESSOR_G11C5_PRECHECK_RUN_ID,
        "g11c5_precheck_job_id": g11c9.PREDECESSOR_G11C5_PRECHECK_JOB_ID,
        "g11c5_precheck_run_attempt": g11c9.PREDECESSOR_G11C5_PRECHECK_RUN_ATTEMPT,
        "g11c5_precheck_rerun_authorized": False,
        "g11c5_precheck_execution_result": "PASS",
        "g11c5_terminal_receipt_result": "FAIL_CLOSED",
        "g11c5_terminal_receipt_contract_valid": False,
        "g11c5_live_run_exists": False,
        "g11c5_credentials_issued": 3,
        "g11c5_runner_started": True,
        "g11c5_live_execution_started": False,
        "g11c5_activation_reuse_authorized": False,
        "g11c5_generation_reuse_authorized": False,
        "g11c5_runtime_lock_reuse_authorized": False,
        "g11c5_pilot_run_id_reuse_authorized": False,
        "g11c5_precheck_act_id_reuse_authorized": False,
        "g11c5_live_act_id_reuse_authorized": False,
        "g11c5_latch_event_id_reuse_authorized": False,
    })
    for field_name, values in g11c9.PREDECESSOR_G11C6_IDENTITIES.items():
        result.setdefault(field_name, []).extend(values)
    result.update({
        "consumed_g11c6_precheck_run": 33484842311,
        "g11c6_precheck_run_id": 33484842311,
        "g11c6_precheck_job_id": 99782407546,
        "g11c6_precheck_run_attempt": 1,
        "g11c6_precheck_rerun_authorized": False,
        "g11c6_precheck_execution_result": "NOT_RUN_PRE_OIDC",
        "g11c6_terminal_receipt_result": "FAIL_CLOSED",
        "g11c6_terminal_receipt_contract_valid": True,
        "g11c6_live_run_exists": False,
        "g11c6_credentials_issued": 0,
        "g11c6_runner_started": False,
        "g11c6_live_execution_started": False,
        "g11c6_activation_reuse_authorized": False,
        "g11c6_generation_reuse_authorized": False,
        "g11c6_runtime_lock_reuse_authorized": False,
        "g11c6_pilot_run_id_reuse_authorized": False,
        "g11c6_precheck_act_id_reuse_authorized": False,
        "g11c6_live_act_id_reuse_authorized": False,
        "g11c6_latch_event_id_reuse_authorized": False,
    })
    for field_name, values in g11c9.PREDECESSOR_G11C7_IDENTITIES.items():
        result.setdefault(field_name, []).extend(values)
    result.update({
        "consumed_g11c7_precheck_run": 33490803554,
        "consumed_g11c7_live_run": 33492771321,
        "g11c7_precheck_run_id": 33490803554,
        "g11c7_precheck_job_id": 99801574441,
        "g11c7_precheck_run_attempt": 1,
        "g11c7_precheck_execution_result": "PASS",
        "g11c7_live_run_id": 33492771321,
        "g11c7_live_job_id": 99807892677,
        "g11c7_live_run_attempt": 1,
        "g11c7_live_execution_result": "FAIL_CLOSED_PRE_CREDENTIAL",
        "g11c7_terminal_receipt_contract_valid": True,
        "g11c7_precheck_credentials_issued": 3,
        "g11c7_live_credentials_issued": 0,
        "g11c7_live_runner_started": False,
        "g11c7_live_execution_started": False,
        "g11c7_precheck_rerun_authorized": False,
        "g11c7_live_rerun_authorized": False,
        "g11c7_activation_reuse_authorized": False,
        "g11c7_generation_reuse_authorized": False,
        "g11c7_runtime_lock_reuse_authorized": False,
        "g11c7_pilot_run_id_reuse_authorized": False,
        "g11c7_precheck_act_id_reuse_authorized": False,
        "g11c7_live_act_id_reuse_authorized": False,
        "g11c7_latch_event_id_reuse_authorized": False,
    })
    for field_name, values in g11c9.PREDECESSOR_G11C8_IDENTITIES.items():
        result.setdefault(field_name, []).extend(values)
    result.update({
        "consumed_g11c8_precheck_run": 33498757471,
        "g11c8_precheck_run_id": 33498757471,
        "g11c8_precheck_job_id": 99826920605,
        "g11c8_precheck_run_attempt": 1,
        "g11c8_precheck_execution_result": "PASS",
        "g11c8_precheck_receipt_contract_valid": True,
        "g11c8_precheck_receipt_result": "PASS",
        "g11c8_precheck_rerun_authorized": False,
        "g11c8_live_run_exists": False,
        "g11c8_live_run_retry_authorized": False,
        "g11c8_activation_reuse_authorized": False,
        "g11c8_generation_reuse_authorized": False,
        "g11c8_runtime_lock_reuse_authorized": False,
        "g11c8_pilot_run_id_reuse_authorized": False,
        "g11c8_precheck_act_id_reuse_authorized": False,
        "g11c8_live_act_id_reuse_authorized": False,
        "g11c8_latch_event_id_reuse_authorized": False,
    })
    return result


def authority_document() -> dict:
    safe_adapter = safe_adapter_document()
    return {
        "artifact": g11c9.AUTHORITY_SCHEMA,
        "schema_version": 1,
        "generation_timestamp": g11c9.GENERATION_TIMESTAMP,
        "authority_commit": g11c9.AUTHORITY_COMMIT,
        "owner_authority_binding": {
            "commit": g11c9.OWNER_APPROVAL_COMMIT,
            "governing_forward_only_receipt_path": (
                "control/m3top3/public-data-source-admission/v1.0/"
                "M3TOP3_FINANCE_CA_PAGE100_G11_DOWNSTREAM_OWNER_DECISION_RECEIPT_v1.1.json"
            ),
            "governing_forward_only_receipt_commit": g11c9.GOVERNED_CORRECTION_HEAD,
            "governing_forward_only_receipt_git_blob": g11c9.OWNER_DECISION_V1_1_GIT_BLOB,
            "governing_forward_only_receipt_sha256": g11c9.OWNER_DECISION_V1_1_SHA256,
        },
        "predecessor_ineligible_preparation_binding":
            predecessor_ineligible_preparation_binding(),
        "predecessor_invalidated_g11c2_binding":
            predecessor_invalidated_g11c2_binding(),
        "predecessor_terminal_g11c3_binding":
            predecessor_terminal_g11c3_binding(),
        "predecessor_terminal_g11c4_binding":
            predecessor_terminal_g11c4_binding(),
        "predecessor_terminal_g11c5_binding":
            predecessor_terminal_g11c5_binding(),
        "predecessor_terminal_g11c6_binding":
            predecessor_terminal_g11c6_binding(),
        "predecessor_terminal_g11c7_binding":
            predecessor_terminal_g11c7_binding(),
        "predecessor_invalidated_g11c8_binding":
            predecessor_invalidated_g11c8_binding(),
        "fresh_identity": {
            "generation_id": g11c9.GENERATION_ID,
            "runtime_lock_id": g11c9.RUNTIME_LOCK_ID,
            "pilot_run_id": g11c9.PILOT_RUN_ID,
            "preparation_id": g11c9.PREPARATION_ID,
            "precheck_act_id": g11c9.PRECHECK_ACT_ID,
            "live_act_id": g11c9.LIVE_ACT_ID,
            "latch_event_id": g11c9.LATCH_EVENT_ID,
            "owner_cap_spec_sha256": g11c9.OWNER_CAP_SPEC_SHA256,
            "execution_token_sha256": g11c9.EXECUTION_TOKEN_SHA256,
            "identity_reuse_authorized": False,
        },
        "owner_cap_spec": g11c9.expected_owner_cap_spec(),
        "owner_cap_spec_canonicalization": "UTF8_JSON_SORT_KEYS_COMPACT_TRAILING_LF",
        "owner_cap_spec_sha256": g11c9.OWNER_CAP_SPEC_SHA256,
        "execution_token_material": g11c9.expected_execution_token_material(),
        "execution_token_material_canonicalization": "UTF8_JSON_SORT_KEYS_COMPACT_TRAILING_LF",
        "execution_token_sha256": g11c9.EXECUTION_TOKEN_SHA256,
        "authorized_route": {
            "route": (
                "RESUME_PAGE100_RAW_ACQUISITION_FROM_EXACT_G10_CHECKPOINT_"
                "AT_20240131_PAGE_5"
            ),
            "one_fresh_exact_three_sts_probe_precheck_authorized": True,
            "github_run_attempt_required": 1,
        },
        "sealed_s3_projection_binding": {
            "bas_dt": g11c9.SEED_BASE_DATE,
            "source_rows": 40,
            "eligible_rows": 35,
            "excluded_rows_at_sealed_seed": 5,
            "missing_rows": 0,
            "excluded_global_row_ordinals": [36, 37, 38, 39, 40],
            "sealed_eligible_projection_sha256": g11c9.SEALED_SEED_PROJECTION_SHA256,
            "selector_algorithm": g11c9.SELECTOR_ALGORITHM,
            "selector_custody_key_sha256": g11c9.TARGET_CUSTODY_SHA256,
            "selector_match_left_eligible": False,
            "raw_source_rows_mutated": False,
        },
        "selector_continuation_semantics": {
            "s3_exclusion_authority_scope": (
                "SEALED_FIVE_OCCURRENCES_AT_GLOBAL_ROW_ORDINALS_36_THROUGH_40_ONLY"
            ),
            "exact_selector_auto_exclusion_applies_to_future_pages": False,
            "future_same_selector_rows_raw_custodied_before_parse": True,
            "future_same_selector_rows_excluded_from_eligible_projection": False,
            "future_selector_observation_after_raw_custody": (
                "FAIL_CLOSED_PENDING_OWNER_DECISION"
            ),
            "checkpoint_advance_past_future_selector_observation": False,
            "sealed_excluded_count_without_new_owner_decision": 5,
        },
        "exact_resume_anchor": {
            "g10_checkpoint_sha256": g11c9.PREDECESSOR_CHECKPOINT_SHA256,
            "resume_bas_dt": g11c9.SEED_BASE_DATE,
            "next_page": 5,
            "reacquire_completed_date_or_first_four_current_date_pages": False,
        },
        "finance_bounds": {
            "aggregate_max_primary_page_acquisitions": 1700,
            "aggregate_max_network_attempts_total": 2000,
            "max_attempts_per_logical_page": 2,
            "g10_spent_primary_acquisitions": 4,
            "g10_spent_network_attempts": 4,
            "maximum_new_g11_primary_acquisitions": 1696,
            "maximum_new_g11_network_attempts": 1996,
        },
        "adapter_execution_order_binding": g11c9.expected_adapter_execution_order(),
        "live_pre_mutation_order": g11c9.expected_live_pre_mutation_order(),
        "entry_gate": {
            "live_adapter_gate": g11c9.LIVE_ADAPTER_GATE_READY,
            "live_session_policy_ascii_and_size_ceiling_verified": True,
        },
        "safe_executable_adapter": safe_adapter,
        "custody_boundary": {
            "g11_raw_prefix": g11c9.G11_RAW_PREFIX,
            "g11_control_prefix": g11c9.G11_CONTROL_PREFIX,
            "execution_claim_key": g11c9.EXECUTION_CLAIM_KEY,
            "predecessor_objects_immutable": True,
        },
        "no_rerun": {
            "consumed_github_runs": list(g11c9.REQUIRED_NO_RERUN_RUNS),
            **consumed_predecessor_lineage(),
        },
        "claim_ceiling": {
            "source_admission_verdict": "NOT_ADMITTED",
            "issuer_identity_resolved": False,
            "normalization": False,
            "pit": False,
            "promotion": False,
            "release": False,
            "production": False,
        },
    }


def plan_document(seed_path: Path) -> dict:
    return {
        "artifact": g11c9.PLAN_SCHEMA,
        "schema_version": 1,
        "generation_timestamp": g11c9.GENERATION_TIMESTAMP,
        "authority_commit": g11c9.AUTHORITY_COMMIT,
        "generation_id": g11c9.GENERATION_ID,
        "authority": {"owner_authority_commit": g11c9.OWNER_APPROVAL_COMMIT},
        "predecessor_ineligible_preparation_binding":
            predecessor_ineligible_preparation_binding(),
        "predecessor_invalidated_g11c2_binding":
            predecessor_invalidated_g11c2_binding(),
        "predecessor_terminal_g11c3_binding":
            predecessor_terminal_g11c3_binding(),
        "predecessor_terminal_g11c4_binding":
            predecessor_terminal_g11c4_binding(),
        "predecessor_terminal_g11c5_binding":
            predecessor_terminal_g11c5_binding(),
        "predecessor_terminal_g11c6_binding":
            predecessor_terminal_g11c6_binding(),
        "predecessor_terminal_g11c7_binding":
            predecessor_terminal_g11c7_binding(),
        "predecessor_invalidated_g11c8_binding":
            predecessor_invalidated_g11c8_binding(),
        "identity": {
            "generation_id": g11c9.GENERATION_ID,
            "runtime_lock_id": g11c9.RUNTIME_LOCK_ID,
            "pilot_run_id": g11c9.PILOT_RUN_ID,
            "preparation_id": g11c9.PREPARATION_ID,
            "precheck_act_id": g11c9.PRECHECK_ACT_ID,
            "live_act_id": g11c9.LIVE_ACT_ID,
            "latch_event_id": g11c9.LATCH_EVENT_ID,
            "owner_cap_spec_sha256": g11c9.OWNER_CAP_SPEC_SHA256,
            "execution_token_sha256": g11c9.EXECUTION_TOKEN_SHA256,
        },
        "resume_and_seed_contract": {
            "checkpoint_seed_path": (
                "control/m3top3/public-data-source-admission/v1.0/"
                + g11c9.SEED_FILENAME
            ),
            "checkpoint_seed_sha256": g11c9.sha256_file(seed_path),
            "checkpoint_seed_git_blob": g11c9.git_blob_sha1_file(seed_path),
            "predecessor_checkpoint_sha256": g11c9.PREDECESSOR_CHECKPOINT_SHA256,
            "start_bas_dt": g11c9.SEED_BASE_DATE,
            "start_page": 5,
        },
        "no_rerun": consumed_predecessor_lineage(),
        "budget_contract": {
            "aggregate_primary_acquisition_ceiling": 1700,
            "aggregate_network_attempt_ceiling": 2000,
            "g10_spent_primary_acquisitions": 4,
            "g10_spent_network_attempts": 4,
            "g11_primary_acquisition_ceiling": 1696,
            "g11_network_attempt_ceiling": 1996,
            "max_attempts_per_logical_page": 2,
            "historical_predecessor_nine_calls_recounted": False,
        },
        "ordered_phases": [
            {
                "phase": "PRECHECK",
                "allowed_effects": (
                    "EXACT_THREE_OIDC_STS_POLICY_PACKING_PROBES_ONLY_"
                    "ZERO_DOWNSTREAM_EFFECT"
                ),
                "provider_calls": 0,
                "quota_reservations": 0,
                "sts_policy_probe_count": 3,
                "aws_calls": 6,
                "sts_calls": 6,
                "sts_assume_role_attempts": 3,
                "sts_sessions_assumed": 3,
                "sts_get_caller_identity_calls": 3,
                "credentials_issued": 3,
                "s3_calls": 0,
                "s3_get_object_version_calls": 0,
                "s3_bucket_metadata_calls": 0,
                "raw_writes": 0,
                "s3_put_delete_copy": 0,
                "repository_mutations_by_workflow": 0,
                "remote_custody_mutations": 0,
            },
            {
                "phase": "LIVE_READ_ONLY_SEED_VERIFICATION_BEFORE_ANY_MUTATION",
                "actions": g11c9.expected_live_seed_verification_actions(),
                "s3_list_bucket_versions_calls": 3,
                "s3_get_object_version_calls": 5,
                "s3_head_object_calls": 0,
                "predecessor_unversioned_get_object_calls": 0,
                "g10_checkpoint_mutations": 0,
                "execution_claim_writes": 0,
                "quota_reservations": 0,
                "provider_calls": 0,
                "s3_writes": 0,
            },
            {
                "phase": "LIVE_FIRST_MUTATION_AND_CHECKPOINT_INITIALIZATION",
                "actions": [
                    "CREATE_EXACT_2026_09_01_EXECUTION_CLAIM_ONCE_WITH_IF_NONE_MATCH_STAR"
                ],
            },
            {
                "phase": "BOUNDED_LIVE_DATA_GENERATION",
                "start": "bas_dt=20240131,pageNo=5",
                "per_logical_page_order": [
                    (
                        "IF_SELECTOR_IS_OBSERVED_ON_PAGE_5_OR_LATER_AFTER_RAW_CUSTODY_"
                        "FAIL_CLOSED_PENDING_OWNER_DECISION_WITHOUT_AUTO_EXCLUSION_OR_"
                        "CHECKPOINT_ADVANCE"
                    )
                ],
            }
        ],
    }


def seed_document() -> dict:
    return {
        "artifact": g11c9.SEED_SCHEMA,
        "schema_version": 1,
        "generation_timestamp": g11c9.GENERATION_TIMESTAMP,
        "authority_commit": g11c9.AUTHORITY_COMMIT,
        "predecessor_ineligible_preparation_binding":
            predecessor_ineligible_preparation_binding(),
        "predecessor_invalidated_g11c2_binding":
            predecessor_invalidated_g11c2_binding(),
        "predecessor_terminal_g11c3_binding":
            predecessor_terminal_g11c3_binding(),
        "predecessor_terminal_g11c4_binding":
            predecessor_terminal_g11c4_binding(),
        "predecessor_terminal_g11c5_binding":
            predecessor_terminal_g11c5_binding(),
        "predecessor_terminal_g11c6_binding":
            predecessor_terminal_g11c6_binding(),
        "predecessor_terminal_g11c7_binding":
            predecessor_terminal_g11c7_binding(),
        "predecessor_invalidated_g11c8_binding":
            predecessor_invalidated_g11c8_binding(),
        "no_rerun": consumed_predecessor_lineage(),
        "bas_dt": g11c9.SEED_BASE_DATE,
        "next_page": 5,
        "predecessor": {
            "checkpoint_sha256": g11c9.PREDECESSOR_CHECKPOINT_SHA256,
            "validated_raw_pages": [1, 2, 3, 4],
        },
        "projection": {
            "selector_algorithm": g11c9.SELECTOR_ALGORITHM,
            "selector_sha256": g11c9.TARGET_CUSTODY_SHA256,
            "eligible_projection_sha256": g11c9.SEALED_SEED_PROJECTION_SHA256,
            "source_rows": 40,
            "eligible_rows": 35,
            "excluded_rows": 5,
            "missing_rows": 0,
            "excluded_global_row_ordinals": [36, 37, 38, 39, 40],
            "selector_match_left_eligible": False,
        },
        "evidence_mode": "SEALED_S2_S3_RECEIPT_REUSE",
        "deterministic_recheck_at_live": True,
    }


def test_exact_generation_selector_seed_and_budget_constants() -> None:
    assert g11c9.GENERATION_TIMESTAMP == "20260901200940"
    assert g11c9.OWNER_APPROVAL_COMMIT == "884e1fadebda480f4c38d172eab083cbdbf031b2"
    assert g11c9.AUTHORITY_COMMIT == "19a62491c5168ee4c5f8ece31eba7598f11ebbbc"
    assert g11c9.GOVERNED_CORRECTION_HEAD == "19a62491c5168ee4c5f8ece31eba7598f11ebbbc"
    assert g11c9.GOVERNED_CORRECTION_TREE == "572bf2ab23a7d761de8160e6828f8b074618391b"
    assert g11c9.ACTIVATION_BASE_HEAD_COMMIT == "39a674ac8fc2d6af25e23f533f9f3379f81e4b6c"
    assert g11c9.ACTIVATION_BASE_TREE == "9f3905bd6aa25617c5b2f93e137a9ac281c3dc7b"
    assert g11c9.PREDECESSOR_G11C1_PREPARATION_COMMIT == (
        "0ccb62cd4c0ceaa0409a56b40a899d00f531ba09"
    )
    assert g11c9.PREDECESSOR_G11C1_PREPARATION_TREE == (
        "f35d2bdd68138d527bc8603472311c0ca032988e"
    )
    assert g11c9.OWNER_CAP_SPEC_SHA256 == "c2df5290d66beebade5c17717d41fec4d26f5f78487d23902f4fdbe72d53e31e"
    assert g11c9.EXECUTION_TOKEN_SHA256 == "6db13e47d9bf12142d6ac6e29f63c8ce09f198cfeabf54553462f3e6ee56f4e2"
    assert g11c9.TARGET_CUSTODY_SHA256 == (
        "f3e7b94dbde722df47cc3bb1a5615068cea42dc1994a91ce92317f5d1fb8b3d6"
    )
    assert g11c9.SEALED_SEED_PROJECTION_SHA256 == (
        "8f6986c9a9839ad62fe856dd0c4d31b54ce1982373deffd1404671c4c9fbfd24"
    )
    assert (g11c9.INHERITED_G10_ACQUISITIONS, g11c9.G11_ACQUISITION_CEILING) == (4, 1696)
    assert (g11c9.INHERITED_G10_ATTEMPTS, g11c9.G11_ATTEMPT_CEILING) == (4, 1996)
    assert g11c9.FIRST_NEW_PAGE == 5
    assert g11c9.REQUIRED_NO_RERUN_RUNS == (
        33272691259, 33273146915, 33401871715, 33403101817,
        33414615913, 33414695818, 33465583987, 33466306591,
        33469887723, 33472741288, 33473465774, 33477019917,
        33479444941, 33484842311, 33490803554, 33492771321,
        33498757471,
    )
    assert "FINANCE-PAGE100-G11C1-20260901123521" in (
        g11c9.PREDECESSOR_G11C1_IDENTITIES["consumed_generation_ids"]
    )
    assert "FINANCE-PAGE100-G11C2-20260901130250" in (
        g11c9.PREDECESSOR_G11C2_IDENTITIES["consumed_generation_ids"]
    )
    assert predecessor_invalidated_g11c2_binding()["terminal_receipt_sha256"] == (
        "b7e03464f1f2c53a7446901b88ccb2aa481f940c272970f24cccbb5be1523df6"
    )
    assert predecessor_terminal_g11c3_binding()["credentials_issued"] is False
    assert predecessor_terminal_g11c3_binding()["runner_started"] is False
    c4_terminal = predecessor_terminal_g11c4_binding()
    assert set(c4_terminal) == {
        "generation_id", "runtime_lock_id", "pilot_run_id", "preparation_id",
        "precheck_act_id", "live_act_id", "latch_event_id",
        "terminal_receipt_append_commit", "terminal_receipt_append_tree",
        "terminal_receipt_path", "terminal_receipt_git_blob",
        "terminal_receipt_sha256", "terminal_receipt_payload_sha256",
        "terminal_receipt_bytes", "execution_head_sha", "execution_tree_sha",
        "precheck_run_id", "precheck_job_id", "run_attempt", "result",
        "terminal_state", "entry_gate", "oidc_token_requests", "aws_calls",
        "sts_calls", "sts_assume_role_attempts", "sts_assume_role_successes",
        "sts_sessions_assumed", "sts_get_caller_identity_calls",
        "credentials_issued", "probe_2_started", "probe_3_started",
        "runner_started", "s3_calls", "provider_calls", "quota_reservations",
        "remote_custody_mutations", "repository_mutations_by_workflow",
        "all_downstream_effects_zero", "live_execution_started",
        "same_run_retry_authorized", "reuse_authorized",
    }
    assert c4_terminal["entry_gate"] == (
        "FAIL_CLOSED_PRECHECK_PROBE_1_STS_AUTHORIZATION_FAILURE"
    )
    assert c4_terminal["oidc_token_requests"] == 1
    assert c4_terminal["aws_calls"] == 1
    assert c4_terminal["sts_assume_role_successes"] == 0
    assert c4_terminal["sts_sessions_assumed"] == 0
    assert c4_terminal["probe_2_started"] is False
    assert c4_terminal["probe_3_started"] is False
    assert c4_terminal["runner_started"] is False
    assert c4_terminal["all_downstream_effects_zero"] is True
    assert c4_terminal["live_execution_started"] is False
    assert c4_terminal["same_run_retry_authorized"] is False
    c5_terminal = predecessor_terminal_g11c5_binding()
    assert c5_terminal["terminal_receipt_append_commit"] == (
        "d0061e9005a74817563588990064af4260ab2bd9"
    )
    assert c5_terminal["terminal_receipt_append_tree"] == (
        "7ba82af78770b8fdcfb914ab080bd280f017918f"
    )
    assert c5_terminal["terminal_receipt_git_blob"] == (
        "a3d29884a44ca4dac88b9d47bf2447fe24aa0b08"
    )
    assert c5_terminal["terminal_receipt_sha256"] == (
        "c518d4ac79b6e7735eae9fe3a799ae7ea29dd4c357508ddd4c85e2d09711b30e"
    )
    assert c5_terminal["terminal_receipt_payload_sha256"] == (
        "332d15f75b2f7843046f0eb5d8983fdb3791cef3fa6155803828e1d74008049f"
    )
    assert c5_terminal["terminal_receipt_bytes"] == 50220
    assert c5_terminal["precheck_run_id"] == 33479444941
    assert c5_terminal["precheck_job_id"] == 99765558713
    assert c5_terminal["execution_head_sha"] == (
        "1ecfc11dfd7adb9f4de878330ff4e2b5ab786ffe"
    )
    assert c5_terminal["execution_tree_sha"] == (
        "53d13cccc42aae8f4b21adebee3ed71190ba1954"
    )
    assert c5_terminal["precheck_execution_result"] == "PASS"
    assert c5_terminal["result"] == "FAIL_CLOSED"
    assert c5_terminal["terminal_receipt_contract_valid"] is False
    assert c5_terminal["credentials_issued"] == 3
    assert "runner_started" not in c5_terminal
    c6_terminal = predecessor_terminal_g11c6_binding()
    assert c6_terminal == g11c9.PREDECESSOR_G11C6_BINDING
    assert c6_terminal["terminal_receipt_append_commit"] == (
        "56f2a2fc109da0167010dce64c3697d5051636d3"
    )
    assert c6_terminal["terminal_receipt_append_tree"] == (
        "a868ca84f516dc43f30329c267e3209f940ce2bf"
    )
    assert c6_terminal["terminal_receipt_git_blob"] == (
        "08583e511d62cde662b668fa78cfe4f1a4787572"
    )
    assert c6_terminal["terminal_receipt_sha256"] == (
        "d1d4ed8edbc670990b2eea1c13f9681f17f1a1ae0771fb062c20900346a22867"
    )
    assert c6_terminal["terminal_receipt_payload_sha256"] == (
        "50581e61f50e9526ecc945900fd545047761c7ecfe95e18ee49717c3037734ce"
    )
    assert c6_terminal["terminal_receipt_bytes"] == 44284
    assert c6_terminal["precheck_run_id"] == 33484842311
    assert c6_terminal["precheck_job_id"] == 99782407546
    assert c6_terminal["execution_head_sha"] == (
        "a08938730b95843125b18950abc27af1d48839ba"
    )
    assert c6_terminal["execution_tree_sha"] == (
        "8ac1f1d29c82c0b240559b758cabde22c4ca93d1"
    )
    assert c6_terminal["runner_started"] is False
    assert c6_terminal["credentials_issued"] == 0
    assert c6_terminal["all_effects_zero"] is True
    repo_root = Path(__file__).resolve().parents[3]
    control_root = repo_root / "control/m3top3/public-data-source-admission/v1.0"
    authority_on_disk = json.loads(
        (control_root / (
            "M3TOP3_FINANCE_CA_PAGE100_G11C9_ELIGIBLE_SUCCESSOR_"
            "AUTHORITY_v1.0.json"
        )).read_text(encoding="utf-8")
    )
    schema_on_disk = json.loads(
        (control_root / (
            "M3TOP3_FINANCE_CA_PAGE100_G11C9_FOCUSED_PRECHECK_"
            "TERMINAL_RECEIPT_SCHEMA_v1.0.json"
        )).read_text(encoding="utf-8")
    )
    generator_globals = runpy.run_path(str(control_root / (
        "M3TOP3_FINANCE_CA_PAGE100_G11C9_FOCUSED_PRECHECK_"
        "TERMINAL_RECEIPT_GENERATOR_v1.0.py"
    )))
    authority_c6 = authority_on_disk["predecessor_terminal_g11c6_binding"]
    schema_c6 = {
        key: value["const"]
        for key, value in schema_on_disk["$defs"][
            "predecessor_terminal_g11c6_binding"
        ]["properties"].items()
    }
    assert authority_c6 == g11c9.PREDECESSOR_G11C6_BINDING
    assert schema_c6 == authority_c6
    assert generator_globals["EXPECTED_G11C6_BINDING"] == authority_c6
    assert authority_c6["preparation_expected_commit_message"] == (
        "Prepare M3Top3 Finance page100 G11C6 eligible successor "
        "20260901155700 v1.0"
    )
    assert authority_c6["preparation_actual_commit_message"] == (
        "Prepare M3Top3 Finance Page100 G11C6 eligible successor "
        "20260901155700 v1.0"
    )
    assert authority_c6["preparation_message_case_sensitive_equal"] is False
    for altered_runs in (
        list(g11c9.REQUIRED_NO_RERUN_RUNS[:-1]),
        list(reversed(g11c9.REQUIRED_NO_RERUN_RUNS)),
        [*g11c9.REQUIRED_NO_RERUN_RUNS, g11c9.REQUIRED_NO_RERUN_RUNS[-1]],
    ):
        altered = authority_document()
        altered["no_rerun"]["consumed_github_runs"] = altered_runs
        with raises(g11c9.GateError, match="EXACT_BINDING_MISMATCH"):
            g11c9.validate_authority_document(altered)
    altered_binding = authority_document()
    altered_binding["predecessor_terminal_g11c6_binding"][
        "terminal_receipt_bytes"
    ] += 1
    with raises(g11c9.GateError, match="predecessor_terminal_g11c6_binding"):
        g11c9.validate_authority_document(altered_binding)
    assert list(g11c9.LIVE_PRE_MUTATION_PHASES) == [
        "RUNTIME_KST_DATE_EQUALITY_GATE",
        "FIVE_EXACT_PREDECESSOR_GET_OBJECT_VERSION_READS",
        "THREE_BOUNDED_LIST_BUCKET_VERSIONS_READS",
        "RUNTIME_KST_DATE_RECHECK",
        "EXECUTION_CLAIM_IF_NONE_MATCH_CREATE",
        "FRESH_CHECKPOINT_QUOTA_PROVIDER",
    ]


def test_hash_only_projection_is_deterministic_for_non_target_rows() -> None:
    rows = [
        row(1, h("custody-1"), h("identity-1"), page_no=1, page_item_ordinal=1),
        row(2, h("custody-2"), h("identity-2"), page_no=1, page_item_ordinal=2),
    ]
    first, result = g11c9.project_hashed_rows(rows)
    second, _ = g11c9.project_hashed_rows(rows)
    assert first.eligible_projection_sha256 == second.eligible_projection_sha256
    assert result.source_rows == result.eligible_rows == 2
    assert result.excluded_rows == result.missing_rows == 0
    assert first.source_rows == first.eligible_rows + first.excluded_rows + first.missing_rows


def test_only_sealed_seed_ordinals_36_through_40_can_be_excluded() -> None:
    state = g11c9.ProjectionState(source_rows=35, eligible_rows=35)
    result_state, result = g11c9.project_hashed_rows(
        [row(36, g11c9.TARGET_CUSTODY_SHA256, None, page_no=4, page_item_ordinal=6)],
        state,
        selector_policy=g11c9.SEED_SELECTOR_POLICY,
    )
    assert result.excluded_global_row_ordinals == (36,)
    assert result_state.excluded_rows == 1
    assert g11c9.TARGET_CUSTODY_SHA256 not in result_state.identity_map

    with raises(g11c9.GateError, match="SEALED_SELECTOR_SCOPE_VIOLATION"):
        g11c9.project_hashed_rows(
            [row(1, g11c9.TARGET_CUSTODY_SHA256, None, page_no=1)],
            selector_policy=g11c9.SEED_SELECTOR_POLICY,
        )


def test_future_selector_match_requires_raw_custody_then_stops_pending_owner() -> None:
    original = seeded_state()
    with raises(g11c9.FutureSelectorObservationError) as captured:
        g11c9.project_hashed_rows(
            [row(41, g11c9.TARGET_CUSTODY_SHA256, h("changed identity"))],
            original,
            raw_ref=raw_ref(),
            require_sealed_raw=True,
            selector_policy=g11c9.FUTURE_SELECTOR_POLICY,
        )
    assert captured.value.code == "FUTURE_SELECTOR_OBSERVED_PENDING_OWNER_DECISION"
    # Transactional core returns no advanced state on the terminal observation.
    assert original.source_rows == 40
    assert original.excluded_rows == 5


def test_future_selector_cannot_be_observed_before_raw_seal() -> None:
    with raises(g11c9.GateError, match="RAW_NOT_SEALED"):
        g11c9.project_hashed_rows(
            [row(41, g11c9.TARGET_CUSTODY_SHA256, None)],
            seeded_state(),
            require_sealed_raw=True,
        )


def test_non_target_conflict_and_missing_fields_fail_transactionally_after_raw_seal() -> None:
    original = seeded_state()
    with raises(g11c9.NonTargetIdentityConflictError):
        g11c9.project_hashed_rows(
            [row(41, h("custody-a"), h("identity-b"))],
            original,
            raw_ref=raw_ref(),
            require_sealed_raw=True,
        )
    assert original.source_rows == 40

    with raises(g11c9.MissingCustodyError):
        g11c9.project_hashed_rows(
            [row(41, None, h("identity"))],
            original,
            raw_ref=raw_ref(),
            require_sealed_raw=True,
        )
    with raises(g11c9.MissingIdentityError):
        g11c9.project_hashed_rows(
            [row(41, h("new custody"), None)],
            original,
            raw_ref=raw_ref(),
            require_sealed_raw=True,
        )
    assert original.source_rows == 40


def test_budget_exact_boundaries_and_per_page_attempt_gate() -> None:
    last = g11c9.BudgetState(g11_acquisitions=1695, g11_attempts=1995)
    terminal = last.reserve_attempt(new_unique_acquisition=True, page_attempt=2)
    assert terminal.effective_acquisitions == 1700
    assert terminal.effective_attempts == 2000
    assert terminal.remaining_acquisitions == terminal.remaining_attempts == 0
    with raises(g11c9.GateError, match="ACQUISITION_CEILING"):
        terminal.reserve_attempt(new_unique_acquisition=True, page_attempt=1)
    with raises(g11c9.GateError, match="ATTEMPTS_PER_PAGE_CEILING"):
        g11c9.BudgetState().reserve_attempt(new_unique_acquisition=True, page_attempt=3)


def test_append_only_namespace_guard_rejects_historical_keys() -> None:
    g11c9.validate_g11_object_key(
        "raw/public-data-api/source/G11C9/20260901200940/page-5.json"
    )
    with raises(g11c9.GateError, match="HISTORICAL_NAMESPACE_WRITE_FORBIDDEN"):
        g11c9.validate_g11_object_key(
            "raw/public-data-api/source/G10/G11C9/20260901200940/page-5.json"
        )


def test_active_raw_and_control_prefixes_reject_g11_through_g11c8() -> None:
    g11c9.validate_active_c9_prefixes(g11c9.G11_RAW_PREFIX, g11c9.G11_CONTROL_PREFIX)
    for historical in ("G11", "G11C1", "G11C2", "G11C3", "G11C4", "G11C5", "G11C6", "G11C7", "G11C8"):
        old_raw = g11c9.G11_RAW_PREFIX.replace("G11C9", historical)
        old_control = g11c9.G11_CONTROL_PREFIX.replace("G11C9", historical)
        with raises(g11c9.GateError, match="HISTORICAL_ACTIVE_PREFIX_FORBIDDEN"):
            g11c9.validate_active_c9_prefixes(old_raw, g11c9.G11_CONTROL_PREFIX)
        with raises(g11c9.GateError, match="HISTORICAL_ACTIVE_PREFIX_FORBIDDEN"):
            g11c9.validate_active_c9_prefixes(g11c9.G11_RAW_PREFIX, old_control)


def test_precheck_receipt_append_and_execution_roles_are_not_collapsed() -> None:
    receipt = {"execution_binding": {"head_sha": "a" * 40, "tree_sha": "b" * 40}}
    binding = {
        "receipt_append_commit": "c" * 40,
        "receipt_append_tree": "d" * 40,
        "execution_head_sha": "a" * 40,
        "execution_head_tree_sha": "b" * 40,
    }
    g11c9.validate_precheck_pass_role_binding(binding, receipt)

    collapsed = dict(binding)
    collapsed["receipt_append_commit"] = "a" * 40
    collapsed["receipt_append_tree"] = "b" * 40
    with raises(g11c9.GateError, match="PRECHECK_LINEAGE_ROLES_COLLAPSED"):
        g11c9.validate_precheck_pass_role_binding(collapsed, receipt)

    swapped = dict(binding)
    swapped["execution_head_sha"] = "c" * 40
    with raises(g11c9.GateError, match="execution_head_sha"):
        g11c9.validate_precheck_pass_role_binding(swapped, receipt)

    ambiguous = {**binding, "commit": "c" * 40, "tree": "d" * 40}
    with raises(g11c9.GateError, match="AMBIGUOUS_PRECHECK_LINEAGE_FIELDS"):
        g11c9.validate_precheck_pass_role_binding(ambiguous, receipt)


def test_sealed_adapter_dynamic_import_registers_dataclass_module_and_factory() -> None:
    adapter_path = MODULE_DIR / "finance_page100_g11c9_live_adapter.py"
    factory = g11c9.load_sealed_live_adapter_factory(
        adapter_path, g11c9.sha256_file(adapter_path)
    )
    assert callable(factory)
    assert factory.__name__ == g11c9.LIVE_ADAPTER_FACTORY_SYMBOL


def test_runtime_live_head_markers_resolve_only_from_exact_github_environment() -> None:
    head = "a" * 40
    tree = "b" * 40
    activation = {
        "activation_binding": {
            "live_activation_commit": g11c9.LIVE_HEAD_MARKER,
            "live_activation_tree": g11c9.LIVE_TREE_MARKER,
            "expected_branch_head_at_dispatch": g11c9.LIVE_HEAD_MARKER,
        }
    }
    observed = g11c9.validate_runtime_live_head_binding(
        activation,
        environment={
            "G11C9_LIVE_HEAD_SHA": head,
            "G11C9_LIVE_HEAD_TREE": tree,
            "GITHUB_SHA": head,
            "GITHUB_RUN_ID": "123456789",
            "GITHUB_RUN_ATTEMPT": "1",
        },
    )
    assert observed["head_sha"] == head
    assert observed["tree_sha"] == tree
    assert observed["github_run_id"] == 123456789

    embedded = {"activation_binding": dict(activation["activation_binding"])}
    embedded["activation_binding"]["live_activation_commit"] = head
    with raises(g11c9.GateError, match="live activation commit marker"):
        g11c9.validate_runtime_live_head_binding(
            embedded,
            environment={
                "G11C9_LIVE_HEAD_SHA": head,
                "G11C9_LIVE_HEAD_TREE": tree,
                "GITHUB_SHA": head,
                "GITHUB_RUN_ID": "123456789",
                "GITHUB_RUN_ATTEMPT": "1",
            },
        )

    with raises(g11c9.GateError, match="GITHUB_SHA"):
        g11c9.validate_runtime_live_head_binding(
            activation,
            environment={
                "G11C9_LIVE_HEAD_SHA": head,
                "G11C9_LIVE_HEAD_TREE": tree,
                "GITHUB_SHA": "c" * 40,
                "GITHUB_RUN_ID": "123456789",
                "GITHUB_RUN_ATTEMPT": "1",
            },
        )


def test_live_result_binds_actual_execution_and_single_terminal_put() -> None:
    execution = {
        "repository": g11c9.REPOSITORY,
        "branch": g11c9.BRANCH,
        "github_run_id": 123456789,
        "github_run_attempt": 1,
        "head_sha": "a" * 40,
        "tree_sha": "b" * 40,
    }

    def object_binding(name: str, *, key: str | None = None) -> dict:
        return {
            "key": key or f"raw/public-data-api/source/G11C9/{g11c9.GENERATION_TIMESTAMP}/{name}.json",
            "version_id": f"version-{name}",
            "etag": f'"etag-{name}"',
            "sha256": h(name),
            "bytes": 100,
            "content_type": "application/json",
            "server_side_encryption": "AES256",
        }

    effects = dict(g11c9.LIVE_PRE_ENTRY_EFFECTS)
    effects.update({
        "primary_acquisitions": 1,
        "network_attempts": 1,
        "provider_calls": 1,
        "quota_reservations": 1,
        "raw_writes": 1,
        "checkpoint_writes": 3,
        "execution_claim_writes": 1,
        "terminal_receipt_writes": 1,
        "terminal_receipt_put_attempts": 1,
        "s3_get_calls": 11,
        "s3_put_calls": 6,
        "s3_other_calls": 3,
        "finance_provider_api_calls": 1,
        "provider_quota_reservations": 1,
        "raw_objects_written": 1,
        "raw_index_appends": 1,
        "aws_calls": 26,
        "s3_calls": 20,
        "s3_get_attempts": 11,
        "s3_put_attempts": 6,
        "s3_other_read_calls": 3,
        "successful_put_mutations": 6,
        "unconfirmed_or_failed_put_attempts": 0,
        "remote_custody_mutations": 6,
        "effective_primary_acquisitions": 5,
        "effective_network_attempts": 5,
    })
    result = {
        "schema": "M3TOP3_FINANCE_CA_PAGE100_G11C9_LIVE_ENTRY_RESULT_v1.0",
        "verdict": "PASS",
        "entry_gate": "LIVE_ENTERED_ONCE",
        "execution_binding": execution,
        "effects": effects,
        "effect_reconciliation": {"complete": True, "ambiguous_side_effects": False},
        "execution_claim_binding": object_binding("claim", key=g11c9.EXECUTION_CLAIM_KEY),
        "checkpoint_binding": object_binding("checkpoint", key=g11c9.G11_CHECKPOINT_KEY),
        "terminal_receipt_binding": {
            "key": g11c9.G11_TERMINAL_RECEIPT_KEY,
            "attempted": True,
            "put_attempts": 1,
            "confirmed": True,
            "object": object_binding("terminal", key=g11c9.G11_TERMINAL_RECEIPT_KEY),
        },
    }
    code, normalized = g11c9._normalize_and_validate_live_result(
        result, 0, expected_execution_binding=execution
    )
    assert code == 0
    assert normalized["effects"]["sts_calls"] == 6
    assert normalized["effects"]["sts_assume_role_attempts"] == 3
    assert normalized["effects"]["sts_sessions_assumed"] == 3
    assert normalized["effects"]["sts_get_caller_identity_calls"] == 3
    assert normalized["effects"]["credentials_issued"] == 3
    assert normalized["effects"]["aws_calls"] == 6 + normalized["effects"]["s3_calls"]
    assert normalized["terminal_receipt_binding"]["confirmed"] is True

    invalid = dict(result)
    invalid["effects"] = dict(effects)
    invalid["effects"]["terminal_receipt_put_attempts"] = 0
    with raises(g11c9.GateError, match="terminal receipt attempt/write"):
        g11c9._normalize_and_validate_live_result(
            invalid, 0, expected_execution_binding=execution
        )


def test_pre_entry_live_result_preserves_three_session_effect_ledger() -> None:
    result = g11c9._pre_entry_live_failure("TEST_PRE_ENTRY_GATE")

    code, normalized = g11c9._normalize_and_validate_live_result(
        result, g11c9.EX_CONFIG
    )

    assert code == g11c9.EX_CONFIG
    assert normalized["entry_gate"] == "LIVE_NOT_ENTERED"
    assert normalized["effects"]["s3_calls"] == 0
    assert normalized["effects"]["sts_calls"] == 6
    assert normalized["effects"]["sts_assume_role_attempts"] == 3
    assert normalized["effects"]["sts_sessions_assumed"] == 3
    assert normalized["effects"]["sts_get_caller_identity_calls"] == 3
    assert normalized["effects"]["credentials_issued"] == 3
    assert normalized["effects"]["aws_calls"] == 6
    assert normalized["effects"]["remote_custody_mutations"] == 0
    assert normalized["effect_reconciliation"] == {
        "complete": True, "ambiguous_side_effects": False,
    }


def test_seed_summary_reuses_sealed_receipts_and_defers_raw_recheck_to_live() -> None:
    assert g11c9.validate_seed_document(seed_document()) == "SEALED_RECEIPT_REUSE"


def test_plan_must_bind_exact_current_seed_sha_and_blob() -> None:
    with tempfile.TemporaryDirectory() as temporary_directory:
        seed_path = Path(temporary_directory) / g11c9.SEED_FILENAME
        write_json(seed_path, seed_document())
        plan = plan_document(seed_path)
        g11c9.validate_plan_seed_material_binding(plan, seed_path)
        write_json(seed_path, {**seed_document(), "state": "mutated-after-plan-binding"})
        with raises(g11c9.GateError, match="checkpoint_seed_sha256"):
            g11c9.validate_plan_seed_material_binding(plan, seed_path)


def test_live_session_policy_ascii_and_2048_character_limit() -> None:
    with tempfile.TemporaryDirectory() as temporary_directory:
        policy_path = Path(temporary_directory) / "live-policy.json"
        policies = g11c9.expected_split_session_policies()
        for role, policy in policies.items():
            write_json(policy_path, policy)
            exact_length = g11c9.validate_live_session_policy_for_aws(policy_path, role)
            assert exact_length <= 2048

        original_ceiling = g11c9.AWS_INLINE_SESSION_POLICY_ASCII_CHARACTER_CEILING
        try:
            role = "final_list_write_session_policy"
            write_json(policy_path, policies[role])
            exact_length = g11c9.validate_live_session_policy_for_aws(policy_path, role)
            g11c9.AWS_INLINE_SESSION_POLICY_ASCII_CHARACTER_CEILING = exact_length - 1
            with raises(g11c9.GateError, match="LIVE_SESSION_POLICY_EXCEEDS"):
                g11c9.validate_live_session_policy_for_aws(policy_path, role)
        finally:
            g11c9.AWS_INLINE_SESSION_POLICY_ASCII_CHARACTER_CEILING = original_ceiling

        forbidden_version = copy.deepcopy(policies["checkpoint_read_session_policy"])
        forbidden_version["Version"] = "2012-10-17"
        write_json(policy_path, forbidden_version)
        with raises(g11c9.GateError, match="VERSION_MUST_BE_OMITTED"):
            g11c9.validate_live_session_policy_for_aws(
                policy_path, "checkpoint_read_session_policy"
            )


def test_bundle_hash_bindings_and_precheck_sts_effect_contract() -> None:
    placeholder_cap = g11c9.OWNER_CAP_SPEC_SHA256
    placeholder_token = g11c9.EXECUTION_TOKEN_SHA256
    g11c9.OWNER_CAP_SPEC_SHA256 = g11c9.sha256_bytes(
        g11c9.canonical_json_lf_bytes(g11c9.expected_owner_cap_spec())
    )
    g11c9.EXECUTION_TOKEN_SHA256 = g11c9.sha256_bytes(
        g11c9.canonical_json_lf_bytes(g11c9.expected_execution_token_material())
    )
    with tempfile.TemporaryDirectory() as temporary_directory:
        tmp_path = Path(temporary_directory)
        authority_path = tmp_path / g11c9.AUTHORITY_FILENAME
        plan_path = tmp_path / g11c9.PLAN_FILENAME
        seed_path = tmp_path / g11c9.SEED_FILENAME
        manifest_path = tmp_path / g11c9.MANIFEST_FILENAME
        policy_filenames = {
            "checkpoint_read_session_policy":
                "M3TOP3_FINANCE_CA_PAGE100_G11C9_CHECKPOINT_READ_SESSION_POLICY_v1.0.json",
            "raw_four_read_session_policy":
                "M3TOP3_FINANCE_CA_PAGE100_G11C9_RAW_FOUR_READ_SESSION_POLICY_v1.0.json",
            "final_list_write_session_policy":
                "M3TOP3_FINANCE_CA_PAGE100_G11C9_FINAL_LIST_WRITE_SESSION_POLICY_v1.0.json",
        }
        repo_root = MODULE_DIR.parents[1]
        policy_paths = {
            role: repo_root / "control/m3top3/public-data-source-admission/v1.0" / filename
            for role, filename in policy_filenames.items()
        }
        test_path = Path(__file__).resolve()
        runner_path = Path(g11c9.__file__).resolve()
        adapter_path = MODULE_DIR / "finance_page100_g11c9_live_adapter.py"

        write_json(authority_path, authority_document())
        write_json(seed_path, seed_document())
        write_json(plan_path, plan_document(seed_path))
        safe_adapter = safe_adapter_document()

        def binding(path: Path) -> dict:
            return {
                "filename": path.name,
                "sha256": g11c9.sha256_file(path),
                "git_blob": g11c9.git_blob_sha1_file(path),
            }

        manifest = {
            "artifact": g11c9.MANIFEST_SCHEMA,
            "schema_version": 1,
            "generation_timestamp": g11c9.GENERATION_TIMESTAMP,
            "generation_id": g11c9.GENERATION_ID,
            "authority_commit": g11c9.AUTHORITY_COMMIT,
            "preparation_commit_binding": "DEFERRED_TO_ACTIVATION",
            "sealed_scope_summary": {
                "owner_cap_spec_sha256": g11c9.OWNER_CAP_SPEC_SHA256,
                "execution_token_sha256": g11c9.EXECUTION_TOKEN_SHA256,
                "fixed_quota_day_kst": g11c9.QUOTA_DAY_KST,
            },
            "adapter_execution_order_binding": g11c9.expected_adapter_execution_order(),
            "files": {
                "authority": binding(authority_path),
                "plan": binding(plan_path),
                "seed": binding(seed_path),
                "runner": binding(runner_path),
                "tests": binding(test_path),
                "adapter_tests": binding(test_path),
                "live_adapter": {
                    **binding(adapter_path),
                    "path": g11c9.LIVE_ADAPTER_REPO_PATH,
                },
                **{
                    role: {
                        **binding(policy_path),
                        "path": policy_path.relative_to(repo_root).as_posix(),
                    }
                    for role, policy_path in policy_paths.items()
                },
            },
            "live_adapter_gate": g11c9.LIVE_ADAPTER_GATE_READY,
            "live_adapter": {
                "executable": True,
                "sealed": True,
                "ready": True,
                **safe_adapter,
            },
            "safe_executable_adapter": safe_adapter,
        }
        write_json(manifest_path, manifest)

        result = g11c9.validate_bundle(
            authority_path=authority_path,
            plan_path=plan_path,
            seed_path=seed_path,
            manifest_path=manifest_path,
            pytest_path=test_path,
        )
        assert result["first_new_page"] == 5
        assert result["governed_correction_head"] == g11c9.GOVERNED_CORRECTION_HEAD
        assert result["live_adapter_gate"] == g11c9.LIVE_ADAPTER_GATE_READY
        assert g11c9.PRECHECK_STS_PROBE_EFFECTS["aws_calls"] == 6
        assert g11c9.PRECHECK_STS_PROBE_EFFECTS["sts_calls"] == 6
        assert g11c9.PRECHECK_STS_PROBE_EFFECTS["s3_calls"] == 0
        assert g11c9.PRECHECK_STS_PROBE_EFFECTS["provider_calls"] == 0
        assert g11c9.PRECHECK_STS_PROBE_EFFECTS["remote_custody_mutations"] == 0

        blocked = dict(manifest)
        blocked["live_adapter_gate"] = g11c9.LIVE_ADAPTER_GATE_BLOCKED
        blocked_manifest = tmp_path / ("blocked-" + g11c9.MANIFEST_FILENAME)
        write_json(blocked_manifest, blocked)
        with raises(g11c9.GateError, match="manifest.live_adapter_gate"):
            g11c9.validate_manifest_document(
                blocked,
                authority_path=authority_path,
                plan_path=plan_path,
                seed_path=seed_path,
                runner_path=runner_path,
                pytest_path=test_path,
                live_adapter_path=adapter_path,
            )
    g11c9.OWNER_CAP_SPEC_SHA256 = placeholder_cap
    g11c9.EXECUTION_TOKEN_SHA256 = placeholder_token


def test_unsealed_owner_decision_v11_binding_fails_closed() -> None:
    authority = authority_document()
    authority["owner_authority_binding"]["governing_forward_only_receipt_sha256"] = (
        "__OWNER_DECISION_V1_1_SHA256__"
    )
    with raises(g11c9.GateError, match="UNSEALED_AUTHORITY_PLACEHOLDER"):
        g11c9.validate_authority_document(authority)


def test_precheck_requires_exact_three_workflow_proven_sts_policy_probes() -> None:
    assert g11c9.validate_precheck_sts_policy_probe_count(3) == 3
    for invalid in (None, False, 0, 1, 2, 4):
        with raises(g11c9.GateError, match="STS_POLICY_PROBE|EXACT_BINDING"):
            g11c9.validate_precheck_sts_policy_probe_count(invalid)
    assert g11c9.PRECHECK_STS_PROBE_EFFECTS == {
        **g11c9.ZERO_EFFECTS,
        "aws_calls": 6,
        "sts_calls": 6,
        "sts_assume_role_attempts": 3,
        "sts_sessions_assumed": 3,
        "sts_get_caller_identity_calls": 3,
        "credentials_issued": 3,
    }
    assert [probe["role"] for probe in g11c9.OIDC_STS_POLICY_PACKING_PROBES] == [
        "CHECKPOINT_READ", "RAW_READ", "FINAL_LIST_WRITE",
    ]
    expected_observation_roles = [
        probe["role"] for probe in g11c9.OIDC_STS_POLICY_PACKING_PROBES
    ]
    assert expected_observation_roles == ["CHECKPOINT_READ", "RAW_READ", "FINAL_LIST_WRITE"]


def test_bounded_depth_33_history_geometry_and_pre_oidc_probe_order() -> None:
    repo_root = MODULE_DIR.parents[1]
    workflow_paths = [
        repo_root / ".github/workflows/m3top3-finance-page100-g11c9-eligible-successor-precheck-v1.yml",
        repo_root / ".github/workflows/m3top3-finance-page100-g11c9-eligible-successor-live-v1.yml",
    ]
    expected_roles = (
        "G11C1_PREPARATION",
        "G11C2_PREPARATION",
        "G11C2_PRECHECK_ACTIVATION",
        "G11C2_PRECHECK_RECEIPT_APPEND",
        "G11C2_TERMINAL_CHECKPOINT",
        "G11C6_TERMINAL_RECEIPT_APPEND",
        "G11C7_PREPARATION",
        "G11C7_PRECHECK_ACTIVATION",
        "G11C7_PRECHECK_RECEIPT_APPEND",
        "G11C7_LIVE_ACTIVATION",
        "G11C7_TERMINAL_RECEIPT_APPEND",
        "G11C8_PREPARATION",
        "G11C8_PRECHECK_ACTIVATION",
        "G11C8_PRECHECK_RECEIPT_APPEND",
        "G11C8_TERMINAL_INVALIDATION_APPEND",
    )
    expected_history_hashes = (
        "0ccb62cd4c0ceaa0409a56b40a899d00f531ba09",
        "f35d2bdd68138d527bc8603472311c0ca032988e",
        "203a11baf838955b69a5cc4b7509aff38dbf271b",
        "c5cc0148f3887eeb360761b0105b85a8fbc96cf2",
        "117e701f0bd3ce25d40132169ac5267d306c24c2",
        "e0f6faa56fa485f075cdc974af787352c184870a",
        "72e2465b1d09853c7baf5b4710c44778c63a3851",
        "0c75cca28985afc555a03d541b5409d22ea74eae",
        "5f400498c0890d756b3d5cbe6ede7ec6d2292450",
        "b5e5eb8c2d08feaa99e83185ee1ef0eaf8e90004",
        "56f2a2fc109da0167010dce64c3697d5051636d3",
        "a868ca84f516dc43f30329c267e3209f940ce2bf",
        "096da670e8d077c4d5c5e4ecaacf87e12a0258dc",
        "bfd792b953fff9f43d01f30588fa0258a5a9ac70",
        "72f883e0abd59d0b879b36d4c457d8f65a9031a3",
        "52000cedda77794427c60dce21f6a3d22dd93eef",
        "e0c3087bb83d184263a739da7d1400c8e1871a11",
        "acc69da07c2c755b2b303d71e5e8edbd8457bc97",
        "2b93cf1e62cb8278fe0d4025e6ded89b7983d91f",
        "16e24984370d5cdf70b58904700990185aabf612",
        "0b21f3ffde00ea7f6705811954c729e35103a8db",
        "283ccf856dd34559a1fe8848808615ab4a3ba9ce",
        "36c111e2f423fc2afe1989d2f351460b4e2a17d5",
        "bff4c6c76aa1ad31ffd280eddb8e627ae097b1e0",
        "9a018eb9167692004e4171b6556e29efcf93a1e7",
        "ec6ac1f89e8b6bcdd10cde5045bee3f349fd8968",
        "cde451f6c04ad670d62ae776bb0dbabd92e4dd86",
        "a7e61c8cb7a55e9a209cee7e221f07f2a67d10dd",
        "39a674ac8fc2d6af25e23f533f9f3379f81e4b6c",
        "9f3905bd6aa25617c5b2f93e137a9ac281c3dc7b",
    )
    for workflow_path in workflow_paths:
        source = workflow_path.read_text(encoding="utf-8")
        assert re.findall(r"fetch-depth:\s*([^\s]+)", source) == ["33"]
        assert re.findall(r"fetch-tags:\s*([^\s]+)", source) == ["false"]
        assert re.findall(r"persist-credentials:\s*([^\s]+)", source) == ["false"]
        assert "GIT_NO_LAZY_FETCH: '1'" in source
        assert "git fetch " not in source
        observed_roles = re.findall(r"^\s+(G11C[0-9]_[A-Z0-9_]+)\|", source, re.MULTILINE)
        assert observed_roles == [*expected_roles, *expected_roles]
        for role in expected_roles:
            assert source.count(role + "|") == 2
        for history_hash in expected_history_hashes:
            assert history_hash in source
        availability_end = source.index("done <<EOF", source.index("git cat-file -e \"${commit}^{commit}\""))
        ancestry_start = source.index("git merge-base --is-ancestor \"$commit\"")
        first_credentials = source.index("aws-actions/configure-aws-credentials")
        assert availability_end < ancestry_start < first_credentials
        assert source.index('test "$(git rev-parse "${commit}^{tree}")" = "$tree"') < ancestry_start
    precheck_source = workflow_paths[0].read_text(encoding="utf-8")
    live_source = workflow_paths[1].read_text(encoding="utf-8")
    assert "for ref in HEAD HEAD^ HEAD^^" in precheck_source
    assert "for ref in HEAD HEAD^ HEAD^^ HEAD^^^ HEAD^^^^" in live_source
    assert 'test "$EXPECTED_PREPARATION_PARENT_COMMIT" = "$G11C8_TERMINAL_CHECKPOINT_COMMIT"' in live_source
    assert (30 + 1, 32 + 1) == (31, 33)
    for unsafe_depth in (0, 10, 27, 29, 31, 32, 34):
        assert unsafe_depth != 33
        for workflow_path in workflow_paths:
            mutated = workflow_path.read_text(encoding="utf-8").replace(
                "fetch-depth: 33", f"fetch-depth: {unsafe_depth}", 1
            )
            assert re.findall(r"fetch-depth:\s*([^\s]+)", mutated) != ["33"]
    source = precheck_source
    missing = source.replace(
        next(line for line in source.splitlines() if "G11C2_TERMINAL_CHECKPOINT|" in line),
        "",
        1,
    )
    assert missing.count("G11C2_TERMINAL_CHECKPOINT|") != 2
    duplicate_line = next(
        line for line in source.splitlines() if "G11C7_PREPARATION|" in line
    )
    duplicate = source.replace(duplicate_line, duplicate_line + "\n" + duplicate_line, 1)
    assert duplicate.count("G11C7_PREPARATION|") != 2
    first_role = next(line for line in source.splitlines() if "G11C1_PREPARATION|" in line)
    second_role = next(line for line in source.splitlines() if "G11C2_PREPARATION|" in line)
    reordered = source.replace(first_role, "__FIRST__", 1).replace(second_role, first_role, 1).replace("__FIRST__", second_role, 1)
    assert re.findall(r"^\s+(G11C[0-9]_[A-Z0-9_]+)\|", reordered, re.MULTILINE)[:2] != list(expected_roles[:2])
    wrong_tree = source.replace(
        "f35d2bdd68138d527bc8603472311c0ca032988e", "0" * 40, 1
    )
    assert expected_history_hashes[1] not in wrong_tree
    late = source.replace('git cat-file -e "${commit}^{commit}"', "# moved-too-late", 1)
    late += '\n        git cat-file -e "${commit}^{commit}"\n'
    assert late.index('git cat-file -e "${commit}^{commit}"') > late.index("aws-actions/configure-aws-credentials")


def test_g11c7_and_g11c8_terminal_bindings_and_identity_mutations_fail_closed() -> None:
    authority = authority_document()
    g11c9.validate_authority_document(authority)
    altered_binding = copy.deepcopy(authority)
    altered_binding["predecessor_terminal_g11c7_binding"]["terminal_receipt_bytes"] += 1
    with raises(g11c9.GateError, match="g11c7_binding canonical sha256"):
        g11c9.validate_authority_document(altered_binding)
    missing_identity = copy.deepcopy(authority)
    missing_identity["no_rerun"]["consumed_generation_ids"].remove(
        "FINANCE-PAGE100-G11C7-20260901171500"
    )
    with raises(g11c9.GateError, match="G11C7_IDENTITY"):
        g11c9.validate_authority_document(missing_identity)
    altered_c8 = copy.deepcopy(authority)
    altered_c8["predecessor_invalidated_g11c8_binding"]["terminal_receipt_bytes"] += 1
    with raises(g11c9.GateError, match="g11c8_binding canonical sha256"):
        g11c9.validate_authority_document(altered_c8)
    missing_c8_identity = copy.deepcopy(authority)
    missing_c8_identity["no_rerun"]["consumed_generation_ids"].remove(
        "FINANCE-PAGE100-G11C8-20260901184500"
    )
    with raises(g11c9.GateError, match="G11C8_IDENTITY"):
        g11c9.validate_authority_document(missing_c8_identity)


def _schema_errors(
    instance: object, schema: object, root_schema: dict, path: str = "$"
) -> list[str]:
    """Validate the Draft-2020 keyword subset used by the frozen receipt schema."""
    if schema is True:
        return []
    if schema is False:
        return [f"{path}: false schema"]
    if not isinstance(schema, dict):
        return [f"{path}: invalid schema node"]
    errors: list[str] = []
    reference = schema.get("$ref")
    if isinstance(reference, str):
        assert reference.startswith("#/")
        target: object = root_schema
        for token in reference[2:].split("/"):
            token = token.replace("~1", "/").replace("~0", "~")
            assert isinstance(target, dict)
            target = target[token]
        errors.extend(_schema_errors(instance, target, root_schema, path))
    for subschema in schema.get("allOf", []):
        errors.extend(_schema_errors(instance, subschema, root_schema, path))
    condition = schema.get("if")
    if isinstance(condition, dict) and not _schema_errors(
        instance, condition, root_schema, path
    ):
        if "then" in schema:
            errors.extend(_schema_errors(instance, schema["then"], root_schema, path))
    expected_type = schema.get("type")
    if expected_type is not None:
        type_checks = {
            "object": lambda value: isinstance(value, dict),
            "array": lambda value: isinstance(value, list),
            "string": lambda value: isinstance(value, str),
            "integer": lambda value: type(value) is int,
            "number": lambda value: type(value) in (int, float),
            "boolean": lambda value: type(value) is bool,
            "null": lambda value: value is None,
        }
        allowed = [expected_type] if isinstance(expected_type, str) else expected_type
        if not any(type_checks[item](instance) for item in allowed):
            return errors + [f"{path}: type {expected_type!r} rejected"]
    def json_equal(left: object, right: object) -> bool:
        return json.dumps(left, sort_keys=True, separators=(",", ":")) == json.dumps(
            right, sort_keys=True, separators=(",", ":")
        )

    if "const" in schema and not json_equal(instance, schema["const"]):
        errors.append(f"{path}: const mismatch")
    if "enum" in schema and not any(
        json_equal(instance, member) for member in schema["enum"]
    ):
        errors.append(f"{path}: enum mismatch")
    if isinstance(instance, str) and "pattern" in schema:
        if re.search(schema["pattern"], instance) is None:
            errors.append(f"{path}: pattern mismatch")
    if type(instance) in (int, float):
        if "minimum" in schema and instance < schema["minimum"]:
            errors.append(f"{path}: below minimum")
        if "maximum" in schema and instance > schema["maximum"]:
            errors.append(f"{path}: above maximum")
    if isinstance(instance, dict):
        for key in schema.get("required", []):
            if key not in instance:
                errors.append(f"{path}.{key}: required")
        properties = schema.get("properties", {})
        for key, subschema in properties.items():
            if key in instance:
                errors.extend(
                    _schema_errors(instance[key], subschema, root_schema, f"{path}.{key}")
                )
        additional = schema.get("additionalProperties", True)
        if additional is False:
            for key in set(instance).difference(properties):
                errors.append(f"{path}.{key}: additional property")
        elif isinstance(additional, dict):
            for key in set(instance).difference(properties):
                errors.extend(
                    _schema_errors(instance[key], additional, root_schema, f"{path}.{key}")
                )
    if isinstance(instance, list):
        if len(instance) < schema.get("minItems", 0):
            errors.append(f"{path}: too few items")
        if "maxItems" in schema and len(instance) > schema["maxItems"]:
            errors.append(f"{path}: too many items")
        if schema.get("uniqueItems") is True:
            encoded = [json.dumps(item, sort_keys=True) for item in instance]
            if len(encoded) != len(set(encoded)):
                errors.append(f"{path}: duplicate items")
        prefix_items = schema.get("prefixItems", [])
        for index, subschema in enumerate(prefix_items):
            if index < len(instance):
                errors.extend(
                    _schema_errors(
                        instance[index], subschema, root_schema, f"{path}[{index}]"
                    )
                )
        items = schema.get("items")
        if items is not None:
            for index in range(len(prefix_items), len(instance)):
                errors.extend(
                    _schema_errors(instance[index], items, root_schema, f"{path}[{index}]")
                )
    return errors


def _schema_keyword_inventory(schema: object) -> set[str]:
    keywords: set[str] = set()

    def visit(node: object) -> None:
        if isinstance(node, bool):
            return
        assert isinstance(node, dict)
        for key, value in node.items():
            keywords.add(key)
            if key in ("$defs", "properties"):
                assert isinstance(value, dict)
                for subschema in value.values():
                    visit(subschema)
            elif key in ("allOf", "prefixItems"):
                assert isinstance(value, list)
                for subschema in value:
                    visit(subschema)
            elif key in ("if", "then", "items", "additionalProperties") and isinstance(
                value, (dict, bool)
            ):
                visit(value)

    visit(schema)
    return keywords


def _g11c9_generator_candidate(generator: dict) -> dict:
    c8_receipt_path = CONTROL_DIR / (
        "M3TOP3_FINANCE_CA_PAGE100_G11C8_ELIGIBLE_SUCCESSOR_"
        "PRECHECK_TERMINAL_RECEIPT_33498757471_v1.0.json"
    )
    c8_receipt = json.loads(c8_receipt_path.read_text(encoding="utf-8"))
    authority = json.loads(
        (CONTROL_DIR / g11c9.AUTHORITY_FILENAME).read_text(encoding="utf-8")
    )
    copied_keys = (
        "authority_binding",
        "predecessor_terminal_g11c4_binding",
        "predecessor_terminal_g11c5_binding",
        "predecessor_terminal_g11c6_binding",
        "predecessor_terminal_g11c7_binding",
        "policy_material_bindings",
        "execution_binding",
        "fresh_identity_binding",
        "activation_binding",
        "route_contract",
        "observed_effects",
        "read_only_observations",
        "runner_result",
        "claims",
    )
    candidate = {key: copy.deepcopy(c8_receipt[key]) for key in copied_keys}
    candidate["generated_at_utc"] = "2026-09-01T11:09:40Z"
    candidate["predecessor_invalidated_g11c8_binding"] = copy.deepcopy(
        authority["predecessor_invalidated_g11c8_binding"]
    )
    authority_binding = candidate["authority_binding"]
    authority_binding.update({
        "activation_base_head_commit": generator["EXPECTED_AUTHORITY_BASE_COMMIT"],
        "activation_base_tree": generator["EXPECTED_AUTHORITY_BASE_TREE"],
        "owner_cap_spec_sha256": g11c9.OWNER_CAP_SPEC_SHA256,
        "execution_token_sha256": g11c9.EXECUTION_TOKEN_SHA256,
        "authority_git_blob": "b" * 40,
    })
    material_paths = {
        "authority_path": "control/m3top3/public-data-source-admission/v1.0/" + g11c9.AUTHORITY_FILENAME,
        "plan_path": "control/m3top3/public-data-source-admission/v1.0/" + g11c9.PLAN_FILENAME,
        "seed_path": "control/m3top3/public-data-source-admission/v1.0/" + g11c9.SEED_FILENAME,
        "manifest_path": "control/m3top3/public-data-source-admission/v1.0/" + g11c9.MANIFEST_FILENAME,
        "workflow_path": ".github/workflows/m3top3-finance-page100-g11c9-eligible-successor-precheck-v1.yml",
        "runner_path": "tools/m3top3/finance_page100_g11c9_selector_successor.py",
        "tests_path": "tools/m3top3/tests/test_finance_page100_g11c9_selector_successor.py",
    }
    authority_binding.update(material_paths)
    for key, value in list(authority_binding.items()):
        if isinstance(value, str) and ("G11C8" in value or "g11c8" in value):
            del authority_binding[key]
    for key in (
        "authority_sha256", "plan_sha256", "seed_sha256", "manifest_sha256",
        "workflow_sha256", "runner_sha256", "tests_sha256",
    ):
        authority_binding[key] = hashlib.sha256(key.encode("ascii")).hexdigest()
    for item, expected in zip(
        candidate["policy_material_bindings"], generator["EXPECTED_POLICY_MATERIALS"]
    ):
        ordinal, role, filename, _probe_role = expected
        policy_path = CONTROL_DIR / filename
        item.update({
            "probe_ordinal": ordinal,
            "role": role,
            "path": "control/m3top3/public-data-source-admission/v1.0/" + filename,
            "git_blob": g11c9.git_blob_sha1_file(policy_path),
            "sha256": g11c9.sha256_file(policy_path),
            "bytes": policy_path.stat().st_size,
        })
    execution = candidate["execution_binding"]
    execution.update({
        "run_id": "9990001",
        "job_id": "9990002",
        "head_sha": "c" * 40,
        "tree_sha": "d" * 40,
        "artifact_sha256": "e" * 64,
        "workflow_ref": generator["EXPECTED_WORKFLOW_REF"],
    })
    identity = candidate["fresh_identity_binding"]
    identity.update({
        "generation_id": g11c9.GENERATION_ID,
        "runtime_lock_id": g11c9.RUNTIME_LOCK_ID,
        "pilot_run_id": g11c9.PILOT_RUN_ID,
        "preparation_id": g11c9.PREPARATION_ID,
        "precheck_act_id": g11c9.PRECHECK_ACT_ID,
        "live_act_id": g11c9.LIVE_ACT_ID,
        "latch_event_id": g11c9.LATCH_EVENT_ID,
        "owner_cap_spec_sha256": g11c9.OWNER_CAP_SPEC_SHA256,
        "execution_token_sha256": g11c9.EXECUTION_TOKEN_SHA256,
    })
    activation = candidate["activation_binding"]
    activation.update({
        "act_id": g11c9.PRECHECK_ACT_ID,
        "latch_event_id": g11c9.LATCH_EVENT_ID,
        "activation_path": generator["EXPECTED_ACTIVATION_PATH"],
        "commit_message": generator["EXPECTED_ACTIVATION_MESSAGE"],
        "activation_sha256": "f" * 64,
        "preparation_commit": "1" * 40,
        "preparation_tree": "2" * 40,
        "activation_commit": execution["head_sha"],
        "activation_tree": execution["tree_sha"],
    })
    route = candidate["route_contract"]
    route["maximum_new_g11c9_network_attempts"] = route.pop(
        "maximum_new_g11c8_network_attempts"
    )
    route["maximum_new_g11c9_primary_acquisitions"] = route.pop(
        "maximum_new_g11c8_primary_acquisitions"
    )
    candidate["checks"] = {key: True for key in generator["REQUIRED_CHECKS"]}
    runner_result = candidate["runner_result"]
    runner_result["result_sha256"] = execution["artifact_sha256"]
    assert tuple(generator["REQUIRED_NO_RERUN_RUNS"]) == g11c9.REQUIRED_NO_RERUN_RUNS
    assert g11c9.ACTIVE_PREFIX_REJECTION_REGRESSIONS == (
        "G11", "G11C1", "G11C2", "G11C3", "G11C4", "G11C5", "G11C6",
        "G11C7", "G11C8",
    )
    runner_result["observations"]["required_no_rerun_runs"] = list(
        g11c9.REQUIRED_NO_RERUN_RUNS
    )
    runner_result["observations"]["active_prefix_rejection_regressions"] = list(
        g11c9.ACTIVE_PREFIX_REJECTION_REGRESSIONS
    )
    candidate["runner_result"] = {
        key: runner_result[key]
        for key in (
            "verdict", "entry_gate", "live_adapter_gate", "workflow_conclusion",
            "result_sha256", "sts_policy_probe_count", "observations", "effects",
        )
    }
    material_schema = json.loads(
        (CONTROL_DIR / (
            "M3TOP3_FINANCE_CA_PAGE100_G11C9_FOCUSED_PRECHECK_"
            "TERMINAL_RECEIPT_SCHEMA_v1.0.json"
        )).read_text(encoding="utf-8")
    )["$defs"]["material_bindings"]
    candidate["authority_binding"] = {
        key: authority_binding[key] for key in material_schema["required"]
    }
    stale_material_paths: list[str] = []

    def find_stale_material_paths(value: object, path: str = "$") -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                find_stale_material_paths(child, f"{path}.{key}")
        elif isinstance(value, list):
            for index, child in enumerate(value):
                find_stale_material_paths(child, f"{path}[{index}]")
        elif isinstance(value, str) and ("G11C8_" in value or "g11c8_" in value):
            if not path.startswith("$.predecessor_invalidated_g11c8_binding"):
                stale_material_paths.append(path)

    find_stale_material_paths(candidate)
    assert stale_material_paths == []
    return candidate


def _actual_live_receipt_jq_gates(workflow_source: str) -> list[tuple[str, str]]:
    command_pattern = re.compile(
        r'''(?ms)^\s*jq -e\s*'''
        r'''(?P<opts>(?:\\\n\s+--arg(?:json)?\s+\w+\s+"\$\w+"\s*)*)'''
        r''''(?P<filter>.*?)'\s+"\$(?P<target>\w+)" >/dev/null$'''
    )
    return [
        (match.group("opts"), match.group("filter"))
        for match in command_pattern.finditer(workflow_source)
        if match.group("target") == "precheck_receipt_path"
    ]


def test_actual_generator_schema_and_all_live_receipt_jq_gates_ordered17() -> None:
    repo_root = MODULE_DIR.parents[1]
    generator_path = CONTROL_DIR / (
        "M3TOP3_FINANCE_CA_PAGE100_G11C9_FOCUSED_PRECHECK_"
        "TERMINAL_RECEIPT_GENERATOR_v1.0.py"
    )
    schema_path = CONTROL_DIR / (
        "M3TOP3_FINANCE_CA_PAGE100_G11C9_FOCUSED_PRECHECK_"
        "TERMINAL_RECEIPT_SCHEMA_v1.0.json"
    )
    workflow_path = repo_root / (
        ".github/workflows/m3top3-finance-page100-g11c9-eligible-successor-live-v1.yml"
    )
    generator = runpy.run_path(str(generator_path))
    candidate = _g11c9_generator_candidate(generator)
    passed, failures = generator["_validate_candidate"](candidate)
    assert passed is True and failures == []
    with tempfile.TemporaryDirectory() as temporary_directory:
        temporary = Path(temporary_directory)
        input_path = temporary / "candidate.json"
        receipt_path = temporary / "receipt.json"
        write_json(input_path, candidate)
        generated = subprocess.run(
            [sys.executable, str(generator_path), "--input", str(input_path),
             "--output", str(receipt_path)],
            cwd=repo_root, text=True, capture_output=True, check=False,
        )
        assert generated.returncode == 0, generated.stderr
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        assert receipt == generator["build_receipt"](candidate)
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        assert _schema_keyword_inventory(schema) <= {
            "$defs", "$id", "$ref", "$schema", "additionalProperties", "allOf",
            "const", "description", "enum", "if", "items", "maximum", "maxItems",
            "minimum", "minItems", "pattern", "prefixItems", "properties", "required",
            "then", "title", "type", "uniqueItems",
            "x-live-activation-precheck-pass-binding-contract",
        }
        assert _schema_errors(receipt, schema, schema) == []
        assert set(receipt) == set(schema["properties"])
        assert set(receipt) == set(schema["required"])
        assert receipt["authority_binding"] == receipt["material_bindings"]
        assert set(receipt["authority_binding"]) == set(
            schema["$defs"]["material_bindings"]["required"]
        )
        payload_document = copy.deepcopy(receipt)
        payload_document.pop("receipt_integrity")
        payload_sha256 = hashlib.sha256(
            json.dumps(
                payload_document, ensure_ascii=False, sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()
        assert payload_sha256 == receipt["receipt_integrity"]["payload_sha256"]
        check_names = schema["$defs"]["check_names"]
        all_checks_pass = schema["$defs"]["all_checks_pass"]["allOf"][1]
        required_checks = set(generator["REQUIRED_CHECKS"])
        assert required_checks == set(check_names["required"])
        assert required_checks == set(check_names["properties"])
        assert required_checks == set(all_checks_pass["properties"])
        assert all(
            all_checks_pass["properties"][name] == {"const": True}
            for name in required_checks
        )
        for check_name in required_checks:
            check_mutation = copy.deepcopy(receipt)
            check_mutation["checks"][check_name] = False
            assert _schema_errors(check_mutation, schema, schema)
        bool_as_int = copy.deepcopy(receipt)
        bool_as_int["checks"][next(iter(required_checks))] = 1
        assert _schema_errors(bool_as_int, schema, schema)
        int_as_bool = copy.deepcopy(receipt)
        int_as_bool["github_run_attempt"] = True
        assert _schema_errors(int_as_bool, schema, schema)

        workflow_source = workflow_path.read_text(encoding="utf-8")
        gates = _actual_live_receipt_jq_gates(workflow_source)
        assert len(gates) == 4
        marker_ids = (
            "ORDERED_NO_RERUN",
            "EXECUTION_IDENTITY",
            "PASS_EFFECTS_CLAIMS",
            "POLICY_MATERIALS",
        )
        marked_gates: list[tuple[str, str]] = []
        for marker_id in marker_ids:
            begin = f"# G11C9_RECEIPT_JQ_GATE_{marker_id}_BEGIN"
            end = f"# G11C9_RECEIPT_JQ_GATE_{marker_id}_END"
            assert workflow_source.count(begin) == 1
            assert workflow_source.count(end) == 1
            begin_index = workflow_source.index(begin) + len(begin)
            end_index = workflow_source.index(end)
            assert begin_index < end_index
            marked = _actual_live_receipt_jq_gates(
                workflow_source[begin_index:end_index]
            )
            assert len(marked) == 1
            marked_gates.extend(marked)
        assert marked_gates == gates
        assert len(re.findall(
            r'''(?m)^\s*'\s+"\$precheck_receipt_path" >/dev/null$''',
            workflow_source,
        )) == len(gates)
        assert all(
            ".no_rerun.consumed_github_runs == [33272691259,33273146915,"
            in jq_filter for _opts, jq_filter in gates
        )
        gate_markers = (
            "consumed_g11c8_precheck_run",
            ".artifact == (",
            "live_adapter_gate.runner_reported_readiness",
            ".policy_material_bindings == [",
        )
        assert all(
            sum(marker in jq_filter for marker in gate_markers) == 1
            for _opts, jq_filter in gates
        )
        assert all(
            sum(marker in jq_filter for _opts, jq_filter in gates) == 1
            for marker in gate_markers
        )
        env_match = workflow_source.split("jobs:", 1)[0]
        workflow_env = {
            key: value.strip().strip("'\"")
            for key, value in re.findall(
                r"(?m)^  ([A-Z][A-Z0-9_]+):\s*(.+?)\s*$", env_match
            )
        }
        subprocess_env = dict(os.environ)
        subprocess_env.update(workflow_env)
        authority_binding = candidate["authority_binding"]
        policy_by_role = {
            item["role"]: item for item in candidate["policy_material_bindings"]
        }
        shell_values: dict[str, object] = {
            "precheck_activation_commit": candidate["execution_binding"]["head_sha"],
            "precheck_activation_tree": candidate["execution_binding"]["tree_sha"],
            "precheck_activation_sha": candidate["activation_binding"]["activation_sha256"],
            "receipt_run_id": candidate["execution_binding"]["run_id"],
            "receipt_job_id": candidate["execution_binding"]["job_id"],
            "preparation_commit": candidate["activation_binding"]["preparation_commit"],
            "preparation_tree": candidate["activation_binding"]["preparation_tree"],
            "owner_decision_sha": authority_binding["owner_decision_sha256"],
            "authority_sha": authority_binding["authority_sha256"],
            "plan_sha": authority_binding["plan_sha256"],
            "seed_sha": authority_binding["seed_sha256"],
            "manifest_sha": authority_binding["manifest_sha256"],
            "precheck_workflow_sha": authority_binding["workflow_sha256"],
            "runner_sha": authority_binding["runner_sha256"],
            "test_sha": authority_binding["tests_sha256"],
        }
        for prefix, role in (
            ("checkpoint_read_policy", "checkpoint_read_session_policy"),
            ("raw_four_read_policy", "raw_four_read_session_policy"),
            ("final_list_write_policy", "final_list_write_session_policy"),
        ):
            material = policy_by_role[role]
            shell_values[prefix + "_sha"] = material["sha256"]
            shell_values[prefix + "_blob"] = material["git_blob"]
            shell_values[prefix + "_bytes"] = material["bytes"]

        option_pattern = re.compile(
            r'--arg(?P<json>json)?\s+(?P<name>\w+)\s+"\$(?P<variable>\w+)"'
        )

        def run_gate(opts: str, jq_filter: str, document_path: Path) -> int:
            command = ["jq", "-e"]
            for option in option_pattern.finditer(opts):
                variable = option.group("variable")
                value = shell_values.get(variable, workflow_env.get(variable))
                assert value is not None, variable
                command.extend([
                    "--argjson" if option.group("json") else "--arg",
                    option.group("name"),
                    str(value),
                ])
            command.extend([jq_filter, str(document_path)])
            return subprocess.run(
                command, cwd=repo_root, env=subprocess_env,
                text=True, capture_output=True, check=False,
            ).returncode

        assert [run_gate(*gate, receipt_path) for gate in gates] == [0, 0, 0, 0]
        ordered17 = list(g11c9.REQUIRED_NO_RERUN_RUNS)
        mutations = {
            "missing": None,
            "reordered": [ordered17[1], ordered17[0], *ordered17[2:]],
            "wrong_type": [str(run_id) for run_id in ordered17],
            "duplicate": [*ordered17[:-1], ordered17[-2]],
            "wrong_run": [*ordered17[:-1], 33498757472],
        }
        for name, mutated_runs in mutations.items():
            mutated = copy.deepcopy(receipt)
            if mutated_runs is None:
                del mutated["no_rerun"]["consumed_github_runs"]
            else:
                mutated["no_rerun"]["consumed_github_runs"] = mutated_runs
            mutated_path = temporary / f"receipt-{name}.json"
            write_json(mutated_path, mutated)
            assert _schema_errors(mutated, schema, schema)
            assert all(run_gate(*gate, mutated_path) != 0 for gate in gates)


def _run_direct() -> int:
    tests = [
        value for name, value in sorted(globals().items())
        if name.startswith("test_") and callable(value)
    ]
    for test in tests:
        test()
    print(f"{len(tests)} focused tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(_run_direct())
