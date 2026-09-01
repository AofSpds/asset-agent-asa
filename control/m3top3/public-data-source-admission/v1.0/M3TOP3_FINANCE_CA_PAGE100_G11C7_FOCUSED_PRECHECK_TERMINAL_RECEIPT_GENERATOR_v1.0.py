#!/usr/bin/env python3
"""Build a fail-closed G11C7 focused PRECHECK terminal receipt.

The generator records observations; it does not perform network, provider, quota,
AWS, S3, GitHub, or repository mutations itself.  A PASS receipt establishes only
that exactly three bounded OIDC STS policy-packing probes succeeded, with three
temporary credential sessions and zero downstream data/custody/repository
mutation.  It can never grant LIVE authority or activate LIVE execution.

Usage:
    python M3TOP3_FINANCE_CA_PAGE100_G11C7_FOCUSED_PRECHECK_TERMINAL_RECEIPT_GENERATOR_v1.0.py \
      --input precheck-observations.json --output precheck-terminal-receipt.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "1.0"
GENERATION_TIMESTAMP = "20260901171500"
TASK_BRANCH = "aaa-pmo-public-data-g2-g3-source-admission-v1-20260828"
EXPECTED_ACTIVATION_PATH = (
    "control/m3top3/public-data-source-admission/v1.0/"
    "M3TOP3_FINANCE_CA_PAGE100_G11C7_ELIGIBLE_SUCCESSOR_PRECHECK_ACTIVATION_v1.0.json"
)
EXPECTED_ACTIVATION_MESSAGE = (
    "Arm M3Top3 Finance Page100 G11C7 focused PRECHECK 20260901171500 v1.0"
)
EXPECTED_WORKFLOW_REF = (
    "AofSpds/asset-agent-asa/.github/workflows/"
    "m3top3-finance-page100-g11c7-eligible-successor-precheck-v1.yml@"
    "refs/heads/aaa-pmo-public-data-g2-g3-source-admission-v1-20260828"
)
EXPECTED_OWNER_DECISION_PATH = (
    "control/m3top3/public-data-source-admission/v1.0/"
    "M3TOP3_FINANCE_CA_PAGE100_G11_DOWNSTREAM_OWNER_DECISION_RECEIPT_v1.1.json"
)
EXPECTED_OWNER_DECISION_SHA256 = (
    "9efa622791a036c870ff4cded87bc4123cfae8089382c90a9ee2e804955ec6dd"
)
EXPECTED_AUTHORITY_BASE_COMMIT = "56f2a2fc109da0167010dce64c3697d5051636d3"
EXPECTED_AUTHORITY_BASE_TREE = "a868ca84f516dc43f30329c267e3209f940ce2bf"
EXPECTED_PREDECESSOR_FAILURE_PATH = (
    "control/m3top3/public-data-source-admission/v1.0/"
    "M3TOP3_FINANCE_CA_PAGE100_G11_ELIGIBLE_SUCCESSOR_LIVE_TERMINAL_RECEIPT_33466306591_v1.0.json"
)
EXPECTED_PREDECESSOR_FAILURE_GIT_BLOB = "00bd90fa57062e438bcddfdcc36be9a5694ef3d9"
EXPECTED_PREDECESSOR_FAILURE_SHA256 = (
    "0577dbbacefa40e60e402dcfb37dd0a85c621952ac29314b56a8481d5e2087d6"
)
EXPECTED_PREDECESSOR_FAILURE_PAYLOAD_SHA256 = (
    "bb9d490db07755ddb1da399c4a454abf08679abaeeaae99db5ff58895dec18df"
)
EXPECTED_G11C1_PREPARATION_COMMIT = "0ccb62cd4c0ceaa0409a56b40a899d00f531ba09"
EXPECTED_G11C1_PREPARATION_TREE = "f35d2bdd68138d527bc8603472311c0ca032988e"
EXPECTED_G11C1_TERMINAL_RECEIPT_PATH = (
    "control/m3top3/public-data-source-admission/v1.0/"
    "M3TOP3_FINANCE_CA_PAGE100_G11C1_PREPARATION_AUDIT_TERMINAL_RECEIPT_"
    "20260901130250_v1.0.json"
)
EXPECTED_G11C1_TERMINAL_RECEIPT_SHA256 = (
    "737a2dbd844e2fccf4e53fae88ba34cb68a994138a666dbf221e64fd8acd03c1"
)
EXPECTED_G11C1_TERMINAL_RECEIPT_GIT_BLOB = (
    "8dbde6505e5cb0b130cd96e8495cd7f2d63703f7"
)
EXPECTED_G11C1_TERMINAL_RECEIPT_PAYLOAD_SHA256 = (
    "a41f3fa41413ed89a30a84867624b3ea52de5813903da033dd48ac023fdc15df"
)
EXPECTED_G11C1_TERMINAL_RECEIPT_BYTES = 11695
EXPECTED_G11C2_PREPARATION_COMMIT = "203a11baf838955b69a5cc4b7509aff38dbf271b"
EXPECTED_G11C2_PREPARATION_TREE = "c5cc0148f3887eeb360761b0105b85a8fbc96cf2"
EXPECTED_G11C2_PRECHECK_RUN_ID = 33469887723
EXPECTED_G11C2_INVALIDATION_RECEIPT_PATH = (
    "control/m3top3/public-data-source-admission/v1.0/"
    "M3TOP3_FINANCE_CA_PAGE100_G11C2_PRE_LIVE_FROZEN_CONTRACT_AUDIT_"
    "TERMINAL_RECEIPT_20260901130250_v1.0.json"
)
EXPECTED_G11C2_INVALIDATION_RECEIPT_SHA256 = (
    "b7e03464f1f2c53a7446901b88ccb2aa481f940c272970f24cccbb5be1523df6"
)
EXPECTED_G11C2_INVALIDATION_RECEIPT_GIT_BLOB = (
    "46dc2cf1c7f422786f4365b94782cb8982a6bdb2"
)
EXPECTED_G11C2_INVALIDATION_RECEIPT_PAYLOAD_SHA256 = (
    "d94c512c53a2b83c4d8aae0fc54b0558d9d79f00ca699b684189d9831c5f990a"
)
EXPECTED_G11C2_INVALIDATION_RECEIPT_BYTES = 16182
EXPECTED_G11C4_TERMINAL_RECEIPT_PATH = (
    "control/m3top3/public-data-source-admission/v1.0/"
    "M3TOP3_FINANCE_CA_PAGE100_G11C4_ELIGIBLE_SUCCESSOR_PRECHECK_TERMINAL_"
    "RECEIPT_33477019917_v1.0.json"
)
EXPECTED_G11C4_TERMINAL_RECEIPT_APPEND_COMMIT = (
    "6e4660cfbb1730dcaeaa2908c9e1a38de012a920"
)
EXPECTED_G11C4_TERMINAL_RECEIPT_APPEND_TREE = (
    "3e4a53a6df8ac7fa4f500c51a951ae9c900476d8"
)
EXPECTED_G11C4_TERMINAL_RECEIPT_GIT_BLOB = (
    "7839bde0f67cea9762dd30d2c063add07b36aca9"
)
EXPECTED_G11C4_TERMINAL_RECEIPT_SHA256 = (
    "427fd336552939115a7e4a4ada49dedf74b0dbc5340bc691d1e9c457fcb301ab"
)
EXPECTED_G11C4_TERMINAL_RECEIPT_PAYLOAD_SHA256 = (
    "88d6816dbb9ca4f2f1ae91aa82c32bcbcdd5ed119420ff2aa5819a7cb3d847eb"
)
EXPECTED_G11C4_TERMINAL_RECEIPT_BYTES = 25645
EXPECTED_G11C4_PRECHECK_RUN_ID = 33477019917
EXPECTED_G11C4_PRECHECK_JOB_ID = 99758300336
EXPECTED_G11C4_EXECUTION_HEAD_SHA = "4015867bedf55784584f901bc3afb5e0ca62dc95"
EXPECTED_G11C4_EXECUTION_TREE_SHA = "9df8503c01a90ed45d76346f43507cd20fee9365"
EXPECTED_G11C4_TERMINAL_STATE = (
    "TERMINAL_FAIL_CLOSED_FOCUSED_G11C4_PRECHECK_PROBE_1_CHECKPOINT_READ_"
    "STS_ASSUME_ROLE_WITH_WEB_IDENTITY_NOT_AUTHORIZED_ONE_STS_ATTEMPT_"
    "ZERO_CREDENTIALS_ZERO_DOWNSTREAM_EFFECT_NO_RERUN_LIVE_CLOSED"
)
EXPECTED_G11C4_FAILURE_ENTRY_GATE = (
    "FAIL_CLOSED_PRECHECK_PROBE_1_STS_AUTHORIZATION_FAILURE"
)
EXPECTED_G11C5_TERMINAL_RECEIPT_PATH = (
    "control/m3top3/public-data-source-admission/v1.0/"
    "M3TOP3_FINANCE_CA_PAGE100_G11C5_ELIGIBLE_SUCCESSOR_PRECHECK_TERMINAL_"
    "RECEIPT_33479444941_v1.0.json"
)
EXPECTED_G11C5_TERMINAL_RECEIPT_APPEND_COMMIT = (
    "d0061e9005a74817563588990064af4260ab2bd9"
)
EXPECTED_G11C5_TERMINAL_RECEIPT_APPEND_TREE = (
    "7ba82af78770b8fdcfb914ab080bd280f017918f"
)
EXPECTED_G11C5_TERMINAL_RECEIPT_GIT_BLOB = (
    "a3d29884a44ca4dac88b9d47bf2447fe24aa0b08"
)
EXPECTED_G11C5_TERMINAL_RECEIPT_SHA256 = (
    "c518d4ac79b6e7735eae9fe3a799ae7ea29dd4c357508ddd4c85e2d09711b30e"
)
EXPECTED_G11C5_TERMINAL_RECEIPT_PAYLOAD_SHA256 = (
    "332d15f75b2f7843046f0eb5d8983fdb3791cef3fa6155803828e1d74008049f"
)
EXPECTED_G11C5_TERMINAL_RECEIPT_BYTES = 50220
EXPECTED_G11C5_PREPARATION_COMMIT = "b73db818d27c80e4ef1b4c5c7b0506691be33920"
EXPECTED_G11C5_PREPARATION_TREE = "ffab50ec73ab0f29674d82f2d72110a8923a766f"
EXPECTED_G11C5_PRECHECK_ACTIVATION_COMMIT = (
    "1ecfc11dfd7adb9f4de878330ff4e2b5ab786ffe"
)
EXPECTED_G11C5_PRECHECK_ACTIVATION_TREE = (
    "53d13cccc42aae8f4b21adebee3ed71190ba1954"
)
EXPECTED_G11C5_PRECHECK_RUN_ID = 33479444941
EXPECTED_G11C5_PRECHECK_JOB_ID = 99765558713
EXPECTED_G11C5_EXECUTION_HEAD_SHA = "1ecfc11dfd7adb9f4de878330ff4e2b5ab786ffe"
EXPECTED_G11C5_EXECUTION_TREE_SHA = "53d13cccc42aae8f4b21adebee3ed71190ba1954"
EXPECTED_G11C5_TERMINAL_STATE = (
    "TERMINAL_FAIL_CLOSED_G11C5_PRECHECK_EXECUTION_PASS_RECEIPT_SCHEMA_"
    "GENERATOR_NO_RERUN_CONTRACT_MISMATCH_C4_RUN_33477019917_OMITTED_BY_"
    "FROZEN_SCHEMA_LIVE_CLOSED_CURRENT_GENERATION_NO_RERUN"
)
EXPECTED_G11C6_BINDING: dict[str, Any] = {'generation_id': 'FINANCE-PAGE100-G11C6-20260901155700',
 'runtime_lock_id': 'PMO-FINANCE-PAGE100-G11C6-20260901155700',
 'pilot_run_id': 'FINANCE-PAGE100-PILOT-G11C6-20260901155700',
 'preparation_id': 'FINANCE-PAGE100-G11C6-PREPARATION-20260901155700',
 'precheck_act_id': 'FINANCE-PAGE100-PRECHECK-ACT-G11C6-20260901155700',
 'live_act_id': 'FINANCE-PAGE100-LIVE-ACT-G11C6-20260901155700',
 'latch_event_id': 'FINANCE-PAGE100-LATCH-G11C6-20260901155700',
 'preparation_commit': '1a7588c3c5cc25d378f8edcad4f89c04cf1ba773',
 'preparation_tree': '5e4fe175e926401b3814c6509958d2d39e782434',
 'preparation_parent_commit': 'd0061e9005a74817563588990064af4260ab2bd9',
 'preparation_parent_tree': '7ba82af78770b8fdcfb914ab080bd280f017918f',
 'preparation_expected_commit_message': 'Prepare M3Top3 Finance page100 G11C6 eligible successor '
                                        '20260901155700 v1.0',
 'preparation_actual_commit_message': 'Prepare M3Top3 Finance Page100 G11C6 eligible successor '
                                      '20260901155700 v1.0',
 'preparation_message_case_sensitive_equal': False,
 'precheck_activation_commit': 'a08938730b95843125b18950abc27af1d48839ba',
 'precheck_activation_tree': '8ac1f1d29c82c0b240559b758cabde22c4ca93d1',
 'precheck_activation_path': 'control/m3top3/public-data-source-admission/v1.0/M3TOP3_FINANCE_CA_PAGE100_G11C6_ELIGIBLE_SUCCESSOR_PRECHECK_ACTIVATION_v1.0.json',
 'precheck_activation_git_blob': '85ecbc94a5dc125ef979d7a9925dcd50a73f871a',
 'precheck_activation_sha256': '3a845af5bffee4dcbea399e7635d402bf2403494f84dc7899a2a2f031a018282',
 'precheck_activation_bytes': 50757,
 'terminal_receipt_append_commit': '56f2a2fc109da0167010dce64c3697d5051636d3',
 'terminal_receipt_append_tree': 'a868ca84f516dc43f30329c267e3209f940ce2bf',
 'terminal_receipt_path': 'control/m3top3/public-data-source-admission/v1.0/M3TOP3_FINANCE_CA_PAGE100_G11C6_ELIGIBLE_SUCCESSOR_PRECHECK_TERMINAL_RECEIPT_33484842311_v1.0.json',
 'terminal_receipt_git_blob': '08583e511d62cde662b668fa78cfe4f1a4787572',
 'terminal_receipt_sha256': 'd1d4ed8edbc670990b2eea1c13f9681f17f1a1ae0771fb062c20900346a22867',
 'terminal_receipt_payload_sha256': '50581e61f50e9526ecc945900fd545047761c7ecfe95e18ee49717c3037734ce',
 'terminal_receipt_bytes': 44284,
 'execution_head_sha': 'a08938730b95843125b18950abc27af1d48839ba',
 'execution_tree_sha': '8ac1f1d29c82c0b240559b758cabde22c4ca93d1',
 'precheck_run_id': 33484842311,
 'precheck_job_id': 99782407546,
 'run_attempt': 1,
 'workflow_conclusion': 'failure',
 'result': 'FAIL_CLOSED',
 'terminal_state': 'TERMINAL_FAIL_CLOSED_G11C6_PRECHECK_PRE_OIDC_PREPARATION_COMMIT_MESSAGE_CASE_MISMATCH_EXPECTED_page100_ACTUAL_Page100_ZERO_EXTERNAL_EFFECT_NO_RERUN_LIVE_CLOSED',
 'entry_gate': 'FAIL_CLOSED_PRE_OIDC_PREPARATION_COMMIT_MESSAGE_CASE_MISMATCH',
 'defect_code': 'PREPARATION_COMMIT_MESSAGE_CASE_MISMATCH',
 'defect_class': 'SEMANTIC_QUOTA_CUSTODY_NEUTRAL_ZERO_EXTERNAL_EFFECT_CONTROL_DEFECT',
 'runner_started': False,
 'oidc_token_requests': 0,
 'aws_calls': 0,
 'sts_calls': 0,
 'sts_assume_role_attempts': 0,
 'sts_assume_role_successes': 0,
 'sts_sessions_assumed': 0,
 'sts_get_caller_identity_calls': 0,
 'credentials_issued': 0,
 's3_calls': 0,
 'provider_calls': 0,
 'provider_network_attempts': 0,
 'quota_reservations': 0,
 'remote_custody_mutations': 0,
 'repository_mutations_by_workflow': 0,
 'github_actions_artifacts_uploaded': 0,
 'effects_reconciled': True,
 'ambiguous_side_effects': False,
 'all_effects_zero': True,
 'all_downstream_effects_zero': True,
 'live_execution_started': False,
 'same_run_retry_authorized': False,
 'reuse_authorized': False}
BASE_DATE = "20240131"
ELIGIBLE_PROJECTION_SHA256 = (
    "8f6986c9a9839ad62fe856dd0c4d31b54ce1982373deffd1404671c4c9fbfd24"
)
S3_TERMINAL_RECEIPT_COMMIT = "dfc1428aff461bbca8e2d2504acb144463349052"
S3_TERMINAL_RECEIPT_BLOB = "a6589d2e48ad95703a564e393eed9a071f8bdf75"
S3_SELECTOR_CUSTODY_SHA256 = (
    "f3e7b94dbde722df47cc3bb1a5615068cea42dc1994a91ce92317f5d1fb8b3d6"
)
LIVE_PRE_MUTATION_ORDER = (
    "RUNTIME_KST_DATE_EQUALITY_GATE",
    "FIVE_EXACT_PREDECESSOR_GET_OBJECT_VERSION_READS",
    "THREE_BOUNDED_LIST_BUCKET_VERSIONS_READS",
    "RUNTIME_KST_DATE_RECHECK",
    "EXECUTION_CLAIM_IF_NONE_MATCH_CREATE",
    "FRESH_CHECKPOINT_QUOTA_PROVIDER",
)

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
GIT_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
RUN_ID_RE = re.compile(r"^[0-9]+$")
PLACEHOLDER_RE = re.compile(r"^__[A-Z0-9_]+__$")

REQUIRED_CHECKS = (
    "exact_downstream_authority_present_and_in_scope",
    "route_semantics_and_effect_contract_exactly_bound",
    "task_branch_head_and_tree_exact",
    "s3_terminal_receipt_and_no_rerun_state_verified",
    "sealed_35_row_projection_verified",
    "predecessor_checkpoint_and_raw_version_bindings_verified",
    "fresh_generation_runtime_act_identities_verified",
    "fresh_precheck_activation_and_latch_verified",
    "consumed_identity_or_latch_reuse_absent",
    "s2_s3_g10_rerun_absent",
    "single_writer_concurrency_group_exactly_bound",
    "github_workflow_identity_and_run_attempt_verified",
    "owner_decision_oa_f01_verified",
    "precheck_and_live_session_policies_exactly_bound",
    "live_session_policy_ascii_and_size_ceiling_verified",
    "fresh_successor_prefixes_are_new_by_governed_lineage",
    "finance_date_page_network_quota_bounds_unchanged",
    "aggregate_remaining_effect_ceiling_verified",
    "future_selector_raw_custody_then_fail_closed_policy_verified",
    "live_pre_mutation_order_verified",
    "focused_deterministic_tests_pass",
    "runner_live_adapter_readiness_recorded",
    "source_admission_not_claimed",
    "forbidden_semantic_and_release_authorities_absent",
    "observed_effects_complete_and_reconciled",
    "predecessor_g11c4_terminal_failure_exactly_bound_and_no_rerun",
    "predecessor_g11c5_terminal_control_failure_exactly_bound_and_no_rerun",
    "predecessor_g11c6_terminal_control_failure_exactly_bound_and_no_rerun",
    "three_policy_material_bindings_exactly_bound",
    "three_oidc_sts_policy_packing_probes_succeeded",
    "three_probe_credentials_issued_only",
    "zero_s3_provider_quota_custody_repository_mutation",
)

EXACT_PROBE_EFFECTS = {
    "aws_calls": 6,
    "sts_calls": 6,
    "sts_assume_role_attempts": 3,
    "sts_sessions_assumed": 3,
    "sts_get_caller_identity_calls": 3,
    "credentials_issued": 3,
}

ZERO_MUTATION_EFFECTS = (
    "provider_calls",
    "finance_provider_api_calls",
    "provider_network_attempts",
    "quota_reservations",
    "provider_quota_reservations",
    "s3_calls",
    "s3_get_calls",
    "s3_get_object_calls",
    "s3_get_object_version_calls",
    "s3_list_calls",
    "s3_list_bucket_versions_calls",
    "s3_put_calls",
    "s3_copy_calls",
    "s3_delete_calls",
    "s3_tagging_mutation_calls",
    "s3_put_delete_copy",
    "remote_custody_mutations",
    "raw_objects_written",
    "raw_writes",
    "checkpoint_writes",
    "execution_claim_writes",
    "terminal_receipt_s3_writes",
    "quota_ledger_appends",
    "raw_index_appends",
    "company_master_mutations",
    "universe_mutations",
    "github_repository_mutations_by_workflow",
    "repository_mutations_by_workflow",
    "repository_writes",
    "github_actions_artifacts_uploaded",
    "g10_runs",
    "g11_live_runs",
    "normalization_actions",
    "pit_actions",
    "promotion_actions",
    "release_actions",
    "production_actions",
)

RUNNER_ZERO_EFFECTS = (
    "provider_calls",
    "quota_reservations",
    "s3_calls",
    "repository_writes",
    "remote_custody_mutations",
    "g10_runs",
    "g11_live_runs",
    "normalization_actions",
    "pit_actions",
    "promotion_actions",
    "release_actions",
    "production_actions",
)

EXPECTED_POLICY_MATERIALS = (
    (
        1,
        "checkpoint_read_session_policy",
        "M3TOP3_FINANCE_CA_PAGE100_G11C7_CHECKPOINT_READ_SESSION_POLICY_v1.0.json",
        "CHECKPOINT_READ",
    ),
    (
        2,
        "raw_four_read_session_policy",
        "M3TOP3_FINANCE_CA_PAGE100_G11C7_RAW_FOUR_READ_SESSION_POLICY_v1.0.json",
        "RAW_READ",
    ),
    (
        3,
        "final_list_write_session_policy",
        "M3TOP3_FINANCE_CA_PAGE100_G11C7_FINAL_LIST_WRITE_SESSION_POLICY_v1.0.json",
        "FINAL_LIST_WRITE",
    ),
)

FORBIDDEN_CLAIMS = (
    "source_admission_pass",
    "issuer_identity_resolved",
    "normalization_authorized",
    "pit_authorized",
    "promotion_authorized",
    "release_authorized",
    "production_authorized",
    "model_semantic_change_authorized",
    "evidence_meaning_change_authorized",
    "validation_floor_reduction_authorized",
    "live_authorized_by_precheck",
)


class ReceiptError(ValueError):
    """Candidate observations cannot support a governed receipt."""


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def _require_mapping(parent: dict[str, Any], key: str) -> dict[str, Any]:
    value = parent.get(key)
    if not isinstance(value, dict):
        raise ReceiptError(f"{key} must be an object")
    return value


def _require_string(parent: dict[str, Any], key: str) -> str:
    value = parent.get(key)
    if not isinstance(value, str) or not value:
        raise ReceiptError(f"{key} must be a non-empty string")
    if PLACEHOLDER_RE.fullmatch(value):
        raise ReceiptError(f"{key} still contains unresolved placeholder {value}")
    return value


def _require_sha256(parent: dict[str, Any], key: str) -> str:
    value = _require_string(parent, key)
    if not SHA256_RE.fullmatch(value):
        raise ReceiptError(f"{key} must be a lowercase 64-hex SHA-256")
    return value


def _require_git_sha(parent: dict[str, Any], key: str) -> str:
    value = _require_string(parent, key)
    if not GIT_SHA_RE.fullmatch(value):
        raise ReceiptError(f"{key} must be a lowercase 40-hex Git object id")
    return value


def _require_run_id(parent: dict[str, Any], key: str) -> str:
    value = _require_string(parent, key)
    if not RUN_ID_RE.fullmatch(value):
        raise ReceiptError(f"{key} must contain decimal digits only")
    return value


def _require_nonnegative_int(parent: dict[str, Any], key: str) -> int:
    value = parent.get(key)
    if type(value) is not int or value < 0:
        raise ReceiptError(f"{key} must be a non-negative integer")
    return value


def _validate_effects(
    effects: dict[str, Any], prefix: str, failures: list[str]
) -> None:
    for effect, expected in EXACT_PROBE_EFFECTS.items():
        if _require_nonnegative_int(effects, effect) != expected:
            failures.append(f"{prefix}.{effect}_must_equal_{expected}")
    for effect in ZERO_MUTATION_EFFECTS:
        if _require_nonnegative_int(effects, effect) != 0:
            failures.append(f"{prefix}.{effect}_must_equal_0")
    if effects.get("effects_reconciled") is not True:
        failures.append(f"{prefix}.effects_reconciled_must_be_true")
    if effects.get("ambiguous_side_effects") is not False:
        failures.append(f"{prefix}.ambiguous_side_effects_must_be_false")


def _validate_runner_effects(
    effects: dict[str, Any], failures: list[str]
) -> None:
    for effect, expected in EXACT_PROBE_EFFECTS.items():
        if _require_nonnegative_int(effects, effect) != expected:
            failures.append(f"runner_result.effects.{effect}_must_equal_{expected}")
    for effect in RUNNER_ZERO_EFFECTS:
        if _require_nonnegative_int(effects, effect) != 0:
            failures.append(f"runner_result.effects.{effect}_must_equal_0")


def _validate_policy_materials(
    value: Any, failures: list[str]
) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise ReceiptError("policy_material_bindings must be an array")
    if len(value) != 3:
        failures.append("policy_material_bindings_must_contain_exactly_3_entries")
    bindings: list[dict[str, Any]] = []
    base = "control/m3top3/public-data-source-admission/v1.0/"
    for index, expected in enumerate(EXPECTED_POLICY_MATERIALS):
        if index >= len(value) or not isinstance(value[index], dict):
            failures.append(f"policy_material_bindings[{index}]_missing_or_not_object")
            continue
        item = value[index]
        bindings.append(item)
        ordinal, role, filename, _probe_role = expected
        if item.get("probe_ordinal") != ordinal:
            failures.append(f"policy_material_bindings[{index}].probe_ordinal_mismatch")
        if item.get("role") != role:
            failures.append(f"policy_material_bindings[{index}].role_mismatch")
        if item.get("path") != base + filename:
            failures.append(f"policy_material_bindings[{index}].path_mismatch")
        _require_git_sha(item, "git_blob")
        _require_sha256(item, "sha256")
        if _require_nonnegative_int(item, "bytes") <= 0:
            failures.append(f"policy_material_bindings[{index}].bytes_must_be_positive")
    for key in ("role", "path", "git_blob", "sha256"):
        values = [item.get(key) for item in bindings]
        if len(values) != len(set(values)):
            failures.append(f"policy_material_bindings.{key}_values_must_be_unique")
    return bindings


def _validate_probe_observations(value: Any, failures: list[str]) -> None:
    if not isinstance(value, list):
        raise ReceiptError(
            "runner_result.observations.oidc_sts_policy_packing_probes must be an array"
        )
    if len(value) != 3:
        failures.append(
            "runner_result.observations.oidc_sts_policy_packing_probes_must_have_3_entries"
        )
    for index, expected in enumerate(EXPECTED_POLICY_MATERIALS):
        if index >= len(value) or not isinstance(value[index], dict):
            failures.append(f"runner_result.observations.probe[{index}]_missing_or_not_object")
            continue
        probe = value[index]
        ordinal, policy_role, _filename, role = expected
        exact = {
            "probe_ordinal": ordinal,
            "role": role,
            "policy_role": policy_role,
            "outcome": "SUCCESS",
            "sts_attempts": 1,
            "sts_successes": 1,
            "credentials_issued": 1,
        }
        for key, expected_value in exact.items():
            if probe.get(key) != expected_value:
                failures.append(
                    f"runner_result.observations.probe[{index}].{key}_mismatch"
                )


def _validate_candidate(candidate: dict[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []

    generated_at_utc = _require_string(candidate, "generated_at_utc")
    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]+)?Z", generated_at_utc):
        failures.append("generated_at_utc_must_be_canonical_utc")

    authority = _require_mapping(candidate, "authority_binding")
    for key in (
        "owner_decision_path",
        "authority_path",
        "plan_path",
        "seed_path",
        "manifest_path",
        "workflow_path",
        "runner_path",
        "tests_path",
        "predecessor_failure_receipt_path",
        "predecessor_g11c1_terminal_receipt_path",
        "predecessor_g11c2_invalidation_receipt_path",
    ):
        _require_string(authority, key)
    for key in (
        "owner_decision_sha256",
        "authority_sha256",
        "plan_sha256",
        "seed_sha256",
        "manifest_sha256",
        "workflow_sha256",
        "runner_sha256",
        "tests_sha256",
        "predecessor_failure_receipt_sha256",
        "predecessor_failure_payload_sha256",
        "predecessor_g11c1_terminal_receipt_sha256",
        "predecessor_g11c1_terminal_receipt_payload_sha256",
        "predecessor_g11c2_invalidation_receipt_sha256",
        "predecessor_g11c2_invalidation_receipt_payload_sha256",
        "owner_cap_spec_sha256",
        "execution_token_sha256",
    ):
        _require_sha256(authority, key)
    for key in (
        "authority_git_blob",
        "activation_base_head_commit",
        "activation_base_tree",
        "predecessor_failure_receipt_git_blob",
        "predecessor_g11c1_preparation_commit",
        "predecessor_g11c1_preparation_tree",
        "predecessor_g11c1_terminal_receipt_git_blob",
        "predecessor_g11c2_preparation_commit",
        "predecessor_g11c2_preparation_tree",
        "predecessor_g11c2_invalidation_receipt_git_blob",
    ):
        _require_git_sha(authority, key)
    if authority.get("owner_decision_path") != EXPECTED_OWNER_DECISION_PATH:
        failures.append("authority_binding.owner_decision_path_mismatch")
    if authority.get("owner_decision_sha256") != EXPECTED_OWNER_DECISION_SHA256:
        failures.append("authority_binding.owner_decision_sha256_mismatch")
    exact_authority_values = {
        "activation_base_head_commit": EXPECTED_AUTHORITY_BASE_COMMIT,
        "activation_base_tree": EXPECTED_AUTHORITY_BASE_TREE,
        "predecessor_failure_receipt_path": EXPECTED_PREDECESSOR_FAILURE_PATH,
        "predecessor_failure_receipt_git_blob": EXPECTED_PREDECESSOR_FAILURE_GIT_BLOB,
        "predecessor_failure_receipt_sha256": EXPECTED_PREDECESSOR_FAILURE_SHA256,
        "predecessor_failure_payload_sha256": EXPECTED_PREDECESSOR_FAILURE_PAYLOAD_SHA256,
        "predecessor_failure_run_id": 33466306591,
        "predecessor_failure_job_id": 99726777914,
        "predecessor_failure_bytes": 7688,
        "predecessor_g11c1_preparation_commit": EXPECTED_G11C1_PREPARATION_COMMIT,
        "predecessor_g11c1_preparation_tree": EXPECTED_G11C1_PREPARATION_TREE,
        "predecessor_g11c1_terminal_receipt_path": EXPECTED_G11C1_TERMINAL_RECEIPT_PATH,
        "predecessor_g11c1_terminal_receipt_git_blob": EXPECTED_G11C1_TERMINAL_RECEIPT_GIT_BLOB,
        "predecessor_g11c1_terminal_receipt_sha256": EXPECTED_G11C1_TERMINAL_RECEIPT_SHA256,
        "predecessor_g11c1_terminal_receipt_payload_sha256":
            EXPECTED_G11C1_TERMINAL_RECEIPT_PAYLOAD_SHA256,
        "predecessor_g11c1_terminal_receipt_bytes":
            EXPECTED_G11C1_TERMINAL_RECEIPT_BYTES,
        "predecessor_g11c2_preparation_commit": EXPECTED_G11C2_PREPARATION_COMMIT,
        "predecessor_g11c2_preparation_tree": EXPECTED_G11C2_PREPARATION_TREE,
        "predecessor_g11c2_precheck_run_id": EXPECTED_G11C2_PRECHECK_RUN_ID,
        "predecessor_g11c2_invalidation_receipt_path":
            EXPECTED_G11C2_INVALIDATION_RECEIPT_PATH,
        "predecessor_g11c2_invalidation_receipt_git_blob":
            EXPECTED_G11C2_INVALIDATION_RECEIPT_GIT_BLOB,
        "predecessor_g11c2_invalidation_receipt_sha256":
            EXPECTED_G11C2_INVALIDATION_RECEIPT_SHA256,
        "predecessor_g11c2_invalidation_receipt_payload_sha256":
            EXPECTED_G11C2_INVALIDATION_RECEIPT_PAYLOAD_SHA256,
        "predecessor_g11c2_invalidation_receipt_bytes":
            EXPECTED_G11C2_INVALIDATION_RECEIPT_BYTES,
        "standing_authority_issue": 49,
        "standing_authority_comment_id": 5464265547,
    }
    for key, expected in exact_authority_values.items():
        if authority.get(key) != expected:
            failures.append(f"authority_binding.{key}_mismatch")
    expected_material_paths = {
        "authority_path": "control/m3top3/public-data-source-admission/v1.0/M3TOP3_FINANCE_CA_PAGE100_G11C7_ELIGIBLE_SUCCESSOR_AUTHORITY_v1.0.json",
        "plan_path": "control/m3top3/public-data-source-admission/v1.0/M3TOP3_FINANCE_CA_PAGE100_G11C7_ELIGIBLE_SUCCESSOR_PLAN_v1.0.json",
        "seed_path": "control/m3top3/public-data-source-admission/v1.0/M3TOP3_FINANCE_CA_PAGE100_G11C7_ELIGIBLE_SUCCESSOR_CHECKPOINT_SEED_v1.0.json",
        "manifest_path": "control/m3top3/public-data-source-admission/v1.0/M3TOP3_FINANCE_CA_PAGE100_G11C7_ELIGIBLE_SUCCESSOR_MANIFEST_v1.0.json",
        "workflow_path": ".github/workflows/m3top3-finance-page100-g11c7-eligible-successor-precheck-v1.yml",
        "runner_path": "tools/m3top3/finance_page100_g11c7_selector_successor.py",
        "tests_path": "tools/m3top3/tests/test_finance_page100_g11c7_selector_successor.py",
    }
    for key, expected in expected_material_paths.items():
        if authority.get(key) != expected:
            failures.append(f"authority_binding.{key}_mismatch")

    predecessor_g11c4 = _require_mapping(
        candidate, "predecessor_terminal_g11c4_binding"
    )
    for key in (
        "generation_id",
        "runtime_lock_id",
        "pilot_run_id",
        "preparation_id",
        "precheck_act_id",
        "live_act_id",
        "latch_event_id",
        "terminal_receipt_path",
        "result",
        "terminal_state",
        "entry_gate",
    ):
        _require_string(predecessor_g11c4, key)
    for key in ("terminal_receipt_sha256", "terminal_receipt_payload_sha256"):
        _require_sha256(predecessor_g11c4, key)
    for key in (
        "terminal_receipt_git_blob",
        "execution_head_sha",
        "execution_tree_sha",
    ):
        _require_git_sha(predecessor_g11c4, key)
    exact_predecessor_g11c4 = {
        "generation_id": "FINANCE-PAGE100-G11C4-20260901143300",
        "runtime_lock_id": "PMO-FINANCE-PAGE100-G11C4-20260901143300",
        "pilot_run_id": "FINANCE-PAGE100-PILOT-G11C4-20260901143300",
        "preparation_id": "FINANCE-PAGE100-G11C4-PREPARATION-20260901143300",
        "precheck_act_id": "FINANCE-PAGE100-PRECHECK-ACT-G11C4-20260901143300",
        "live_act_id": "FINANCE-PAGE100-LIVE-ACT-G11C4-20260901143300",
        "latch_event_id": "FINANCE-PAGE100-LATCH-G11C4-20260901143300",
        "terminal_receipt_append_commit": EXPECTED_G11C4_TERMINAL_RECEIPT_APPEND_COMMIT,
        "terminal_receipt_append_tree": EXPECTED_G11C4_TERMINAL_RECEIPT_APPEND_TREE,
        "terminal_receipt_path": EXPECTED_G11C4_TERMINAL_RECEIPT_PATH,
        "terminal_receipt_git_blob": EXPECTED_G11C4_TERMINAL_RECEIPT_GIT_BLOB,
        "terminal_receipt_sha256": EXPECTED_G11C4_TERMINAL_RECEIPT_SHA256,
        "terminal_receipt_payload_sha256": EXPECTED_G11C4_TERMINAL_RECEIPT_PAYLOAD_SHA256,
        "terminal_receipt_bytes": EXPECTED_G11C4_TERMINAL_RECEIPT_BYTES,
        "execution_head_sha": EXPECTED_G11C4_EXECUTION_HEAD_SHA,
        "execution_tree_sha": EXPECTED_G11C4_EXECUTION_TREE_SHA,
        "precheck_run_id": EXPECTED_G11C4_PRECHECK_RUN_ID,
        "precheck_job_id": EXPECTED_G11C4_PRECHECK_JOB_ID,
        "run_attempt": 1,
        "result": "FAIL_CLOSED",
        "terminal_state": EXPECTED_G11C4_TERMINAL_STATE,
        "entry_gate": EXPECTED_G11C4_FAILURE_ENTRY_GATE,
        "oidc_token_requests": 1,
        "aws_calls": 1,
        "sts_calls": 1,
        "sts_assume_role_attempts": 1,
        "sts_assume_role_successes": 0,
        "sts_sessions_assumed": 0,
        "sts_get_caller_identity_calls": 0,
        "credentials_issued": 0,
        "probe_2_started": False,
        "probe_3_started": False,
        "runner_started": False,
        "s3_calls": 0,
        "provider_calls": 0,
        "quota_reservations": 0,
        "remote_custody_mutations": 0,
        "repository_mutations_by_workflow": 0,
        "all_downstream_effects_zero": True,
        "live_execution_started": False,
        "same_run_retry_authorized": False,
        "reuse_authorized": False,
    }
    for key, expected in exact_predecessor_g11c4.items():
        if predecessor_g11c4.get(key) != expected:
            failures.append(f"predecessor_terminal_g11c4_binding.{key}_mismatch")

    predecessor_g11c5 = _require_mapping(
        candidate, "predecessor_terminal_g11c5_binding"
    )
    exact_predecessor_g11c5 = {
        "generation_id": "FINANCE-PAGE100-G11C5-20260901152200",
        "runtime_lock_id": "PMO-FINANCE-PAGE100-G11C5-20260901152200",
        "pilot_run_id": "FINANCE-PAGE100-PILOT-G11C5-20260901152200",
        "preparation_id": "FINANCE-PAGE100-G11C5-PREPARATION-20260901152200",
        "precheck_act_id": "FINANCE-PAGE100-PRECHECK-ACT-G11C5-20260901152200",
        "live_act_id": "FINANCE-PAGE100-LIVE-ACT-G11C5-20260901152200",
        "latch_event_id": "FINANCE-PAGE100-LATCH-G11C5-20260901152200",
        "preparation_commit": EXPECTED_G11C5_PREPARATION_COMMIT,
        "preparation_tree": EXPECTED_G11C5_PREPARATION_TREE,
        "precheck_activation_commit": EXPECTED_G11C5_PRECHECK_ACTIVATION_COMMIT,
        "precheck_activation_tree": EXPECTED_G11C5_PRECHECK_ACTIVATION_TREE,
        "terminal_receipt_append_commit": EXPECTED_G11C5_TERMINAL_RECEIPT_APPEND_COMMIT,
        "terminal_receipt_append_tree": EXPECTED_G11C5_TERMINAL_RECEIPT_APPEND_TREE,
        "terminal_receipt_path": EXPECTED_G11C5_TERMINAL_RECEIPT_PATH,
        "terminal_receipt_git_blob": EXPECTED_G11C5_TERMINAL_RECEIPT_GIT_BLOB,
        "terminal_receipt_sha256": EXPECTED_G11C5_TERMINAL_RECEIPT_SHA256,
        "terminal_receipt_payload_sha256": EXPECTED_G11C5_TERMINAL_RECEIPT_PAYLOAD_SHA256,
        "terminal_receipt_bytes": EXPECTED_G11C5_TERMINAL_RECEIPT_BYTES,
        "execution_head_sha": EXPECTED_G11C5_EXECUTION_HEAD_SHA,
        "execution_tree_sha": EXPECTED_G11C5_EXECUTION_TREE_SHA,
        "precheck_run_id": EXPECTED_G11C5_PRECHECK_RUN_ID,
        "precheck_job_id": EXPECTED_G11C5_PRECHECK_JOB_ID,
        "run_attempt": 1,
        "precheck_execution_result": "PASS",
        "result": "FAIL_CLOSED",
        "terminal_state": EXPECTED_G11C5_TERMINAL_STATE,
        "terminal_receipt_contract_valid": False,
        "defect": (
            "FROZEN_SCHEMA_REQUIRED_NO_RERUN_CONST_OMITS_CONSUMED_"
            "G11C4_PRECHECK_RUN_33477019917"
        ),
        "oidc_token_requests": 3,
        "aws_calls": 6,
        "sts_calls": 6,
        "sts_assume_role_attempts": 3,
        "sts_sessions_assumed": 3,
        "sts_get_caller_identity_calls": 3,
        "credentials_issued": 3,
        "s3_calls": 0,
        "provider_calls": 0,
        "quota_reservations": 0,
        "remote_custody_mutations": 0,
        "repository_mutations_by_workflow": 0,
        "effects_reconciled": True,
        "ambiguous_side_effects": False,
        "all_downstream_effects_zero": True,
        "live_execution_started": False,
        "same_run_retry_authorized": False,
        "reuse_authorized": False,
    }
    for key, expected in exact_predecessor_g11c5.items():
        if predecessor_g11c5.get(key) != expected:
            failures.append(f"predecessor_terminal_g11c5_binding.{key}_mismatch")


    predecessor_g11c6 = _require_mapping(
        candidate, "predecessor_terminal_g11c6_binding"
    )
    if dict(predecessor_g11c6) != EXPECTED_G11C6_BINDING:
        failures.append("predecessor_terminal_g11c6_binding.exact_binding_mismatch")

    _validate_policy_materials(candidate.get("policy_material_bindings"), failures)

    execution = _require_mapping(candidate, "execution_binding")
    _require_run_id(execution, "run_id")
    _require_run_id(execution, "job_id")
    _require_git_sha(execution, "head_sha")
    _require_git_sha(execution, "tree_sha")
    _require_sha256(execution, "artifact_sha256")
    _require_string(execution, "workflow_ref")
    _require_string(execution, "actor")
    _require_string(execution, "event_name")
    if execution.get("run_attempt") != 1:
        failures.append("execution_binding.run_attempt_must_equal_1")
    if execution.get("forced") is not False:
        failures.append("execution_binding.forced_must_be_false")
    if execution.get("workflow_ref") != EXPECTED_WORKFLOW_REF:
        failures.append("execution_binding.workflow_ref_mismatch")
    if execution.get("actor") != "AofSpds":
        failures.append("execution_binding.actor_must_equal_AofSpds")
    if execution.get("event_name") != "push":
        failures.append("execution_binding.event_name_must_equal_push")

    identities = _require_mapping(candidate, "fresh_identity_binding")
    identity_values: list[str] = []
    for key in (
        "generation_id",
        "runtime_lock_id",
        "pilot_run_id",
        "preparation_id",
        "precheck_act_id",
        "live_act_id",
        "latch_event_id",
    ):
        identity_values.append(_require_string(identities, key))
    if len(set(identity_values)) != len(identity_values):
        failures.append("fresh_identity_values_must_be_distinct")
    exact_identities = {
        "generation_id": "FINANCE-PAGE100-G11C7-20260901171500",
        "runtime_lock_id": "PMO-FINANCE-PAGE100-G11C7-20260901171500",
        "pilot_run_id": "FINANCE-PAGE100-PILOT-G11C7-20260901171500",
        "preparation_id": "FINANCE-PAGE100-G11C7-PREPARATION-20260901171500",
        "precheck_act_id": "FINANCE-PAGE100-PRECHECK-ACT-G11C7-20260901171500",
        "live_act_id": "FINANCE-PAGE100-LIVE-ACT-G11C7-20260901171500",
        "latch_event_id": "FINANCE-PAGE100-LATCH-G11C7-20260901171500",
    }
    for key, expected in exact_identities.items():
        if identities.get(key) != expected:
            failures.append(f"fresh_identity_binding.{key}_mismatch")
    for key in ("owner_cap_spec_sha256", "execution_token_sha256"):
        _require_sha256(identities, key)
        if identities.get(key) != authority.get(key):
            failures.append(f"fresh_identity_binding.{key}_must_match_authority")

    activation = _require_mapping(candidate, "activation_binding")
    for key in ("activation_path", "commit_message"):
        _require_string(activation, key)
    _require_sha256(activation, "activation_sha256")
    _require_git_sha(activation, "preparation_commit")
    _require_git_sha(activation, "preparation_tree")
    if activation.get("act_id") != identities.get("precheck_act_id"):
        failures.append("activation_binding.act_id_mismatch")
    if activation.get("latch_event_id") != identities.get("latch_event_id"):
        failures.append("activation_binding.latch_event_id_mismatch")
    if activation.get("activation_path") != EXPECTED_ACTIVATION_PATH:
        failures.append("activation_binding.activation_path_mismatch")
    if activation.get("commit_message") != EXPECTED_ACTIVATION_MESSAGE:
        failures.append("activation_binding.commit_message_mismatch")

    route = _require_mapping(candidate, "route_contract")
    route_kind = _require_string(route, "route_kind")
    if route_kind != "RESUME_FINANCE_PAGE100_FROM_EXACT_G10_CHECKPOINT":
        failures.append("route_contract.route_kind_must_match_owner_selected_route")
    _require_string(route, "selector_policy")
    _require_string(route, "entry_cursor")
    if route.get("base_date") != BASE_DATE:
        failures.append("route_contract.base_date_mismatch")
    if route.get("eligible_rows") != 35:
        failures.append("route_contract.eligible_rows_must_equal_35")
    if route.get("excluded_rows") != 5:
        failures.append("route_contract.excluded_rows_must_equal_5")
    if route.get("projection_sha256") != ELIGIBLE_PROJECTION_SHA256:
        failures.append("route_contract.projection_sha256_mismatch")
    if route.get("selector_policy") != (
        "RAW_CUSTODY_THEN_FAIL_CLOSED_PENDING_OWNER_DECISION_ON_FUTURE_SELECTOR_NO_AUTO_EXCLUSION_NO_CHECKPOINT_ADVANCE"
    ):
        failures.append("route_contract.selector_policy_must_match_OA_F01")
    if route.get("sealed_excluded_count") != 5:
        failures.append("route_contract.sealed_excluded_count_must_equal_5")
    if route.get("future_selector_auto_exclusion") is not False:
        failures.append("route_contract.future_selector_auto_exclusion_must_be_false")
    if route.get("checkpoint_advance_past_future_selector") is not False:
        failures.append("route_contract.checkpoint_advance_past_future_selector_must_be_false")
    exact_route_values = {
        "primary_date_count": 17,
        "request_page_size": 10,
        "max_pages_per_date": 100,
        "max_attempts_per_logical_page": 2,
        "aggregate_max_primary_page_acquisitions": 1700,
        "inherited_g10_primary_acquisitions": 4,
        "maximum_new_g11c7_primary_acquisitions": 1696,
        "aggregate_max_network_attempts_total": 2000,
        "inherited_g10_network_attempts": 4,
        "maximum_new_g11c7_network_attempts": 1996,
    }
    for key, expected in exact_route_values.items():
        if route.get(key) != expected:
            failures.append(f"route_contract.{key}_must_equal_{expected}")
    if route.get("ordered_primary_dates_sha256") != (
        "920b118d7d7abaa10f69e93169698ed380db7162ac3c5024756a07702a7065f6"
    ):
        failures.append("route_contract.ordered_primary_dates_sha256_mismatch")

    checks = _require_mapping(candidate, "checks")
    for check in REQUIRED_CHECKS:
        if checks.get(check) is not True:
            failures.append(f"checks.{check}_must_be_true")

    effects = _require_mapping(candidate, "observed_effects")
    _validate_effects(effects, "observed_effects", failures)

    observations = _require_mapping(candidate, "read_only_observations")
    for key in (
        "github_read_calls",
        "aws_read_calls",
        "s3_read_calls",
    ):
        value = observations.get(key)
        if type(value) is not int or value < 0:
            raise ReceiptError(f"read_only_observations.{key} must be a non-negative integer")
    if observations.get("aws_read_calls") != 3:
        failures.append(
            "read_only_observations.aws_read_calls_must_equal_3_GetCallerIdentity"
        )
    if observations.get("s3_read_calls") != 0:
        failures.append("read_only_observations.s3_read_calls_must_equal_0")

    runner_result = _require_mapping(candidate, "runner_result")
    if runner_result.get("verdict") != "PASS":
        failures.append("runner_result.verdict_must_equal_PASS")
    if runner_result.get("entry_gate") != "FOCUSED_PRECHECK_PASS":
        failures.append("runner_result.entry_gate_must_equal_FOCUSED_PRECHECK_PASS")
    adapter_readiness = runner_result.get("live_adapter_gate")
    if adapter_readiness not in {
        "READY",
        "BLOCKED_MISSING_EXECUTABLE_CUSTODY_ADAPTERS",
    }:
        failures.append("runner_result.live_adapter_gate_unknown")
    if adapter_readiness != "READY":
        failures.append("runner_result.live_adapter_gate_must_be_READY_for_precheck_PASS")
    if runner_result.get("workflow_conclusion") != "success":
        failures.append("runner_result.workflow_conclusion_must_equal_success")
    if runner_result.get("sts_policy_probe_count") != 3:
        failures.append("runner_result.sts_policy_probe_count_must_equal_3")
    _require_sha256(runner_result, "result_sha256")
    if runner_result.get("result_sha256") != execution.get("artifact_sha256"):
        failures.append("runner_result.result_sha256_must_match_execution_artifact_sha256")
    runner_observations = _require_mapping(runner_result, "observations")
    if runner_observations.get("future_selector_policy") != (
        "RAW_CUSTODY_THEN_FAIL_CLOSED_PENDING_OWNER_DECISION"
    ):
        failures.append("runner_result.observations.future_selector_policy_mismatch")
    if runner_observations.get("sealed_exclusion_scope") != [36, 37, 38, 39, 40]:
        failures.append("runner_result.observations.sealed_exclusion_scope_mismatch")
    if runner_observations.get("sts_policy_probe_count_verified") != 3:
        failures.append(
            "runner_result.observations.sts_policy_probe_count_verified_must_equal_3"
        )
    if runner_observations.get("sts_policy_probe_count") != 3:
        failures.append(
            "runner_result.observations.sts_policy_probe_count_must_equal_3"
        )
    if runner_observations.get("sts_policy_probe_roles") != [
        "CHECKPOINT_READ",
        "RAW_READ",
        "FINAL_LIST_WRITE",
    ]:
        failures.append("runner_result.observations.sts_policy_probe_roles_mismatch")
    _validate_probe_observations(
        runner_observations.get("oidc_sts_policy_packing_probes"), failures
    )
    required_no_rerun_runs = [
        33272691259,
        33273146915,
        33401871715,
        33403101817,
        33414615913,
        33414695818,
        33465583987,
        33466306591,
        33469887723,
        33472741288,
        33473465774,
        33477019917,
        33479444941,
        33484842311,
    ]
    observed_no_rerun_runs = runner_observations.get("required_no_rerun_runs")
    if observed_no_rerun_runs != required_no_rerun_runs:
        failures.append("runner_result.observations.required_no_rerun_runs_mismatch")
    if runner_observations.get(
        "live_session_policy_ascii_and_size_ceiling_verified"
    ) is not True:
        failures.append(
            "runner_result.observations."
            "live_session_policy_ascii_and_size_ceiling_verified_must_be_true"
        )
    if runner_observations.get("live_pre_mutation_order") != list(LIVE_PRE_MUTATION_ORDER):
        failures.append("runner_result.observations.live_pre_mutation_order_mismatch")
    runner_effects = _require_mapping(runner_result, "effects")
    _validate_runner_effects(runner_effects, failures)
    for key in (*EXACT_PROBE_EFFECTS, *RUNNER_ZERO_EFFECTS):
        if runner_effects.get(key) != effects.get(key):
            failures.append(f"runner_result.effects.{key}_must_match_observed_effects")

    claims = _require_mapping(candidate, "claims")
    for claim in FORBIDDEN_CLAIMS:
        if claims.get(claim) is not False:
            failures.append(f"claims.{claim}_must_be_false")

    return not failures, failures


def build_receipt(candidate: dict[str, Any]) -> dict[str, Any]:
    passed, failures = _validate_candidate(candidate)
    adapter_readiness = candidate["runner_result"]["live_adapter_gate"]
    terminal_state = (
        "TERMINAL_PASS_FOCUSED_G11C7_PRECHECK_EXACT_3_OIDC_STS_POLICY_PACKING_PROBES_SUCCESS_ZERO_DOWNSTREAM_MUTATION_LIVE_NOT_AUTHORIZED"
        if passed
        else "TERMINAL_FAIL_CLOSED_FOCUSED_G11C7_PRECHECK_LIVE_NOT_AUTHORIZED"
    )

    receipt: dict[str, Any] = {
        "artifact": f"M3TOP3_FINANCE_CA_PAGE100_G11C7_ELIGIBLE_SUCCESSOR_PRECHECK_TERMINAL_RECEIPT_{candidate['execution_binding']['run_id']}_v1.0",
        "artifact_kind": "FRESH_G11C7_ELIGIBLE_SUCCESSOR_FOCUSED_PRECHECK_TERMINAL_RECEIPT",
        "schema_version": 1,
        "repository": "AofSpds/asset-agent-asa",
        "branch": TASK_BRANCH,
        "commit": candidate["execution_binding"]["head_sha"],
        "tree": candidate["execution_binding"]["tree_sha"],
        "github_run_id": candidate["execution_binding"]["run_id"],
        "github_job_id": candidate["execution_binding"]["job_id"],
        "github_run_attempt": candidate["execution_binding"]["run_attempt"],
        "generation_id": candidate["fresh_identity_binding"]["generation_id"],
        "runtime_lock_id": candidate["fresh_identity_binding"]["runtime_lock_id"],
        "pilot_run_id": candidate["fresh_identity_binding"]["pilot_run_id"],
        "act_id": candidate["fresh_identity_binding"]["precheck_act_id"],
        "result": "PASS" if passed else "FAIL_CLOSED",
        "terminal_state": terminal_state,
        "artifact_identity": {
            "artifact_id": f"M3TOP3_FINANCE_CA_PAGE100_G11C7_ELIGIBLE_SUCCESSOR_PRECHECK_TERMINAL_RECEIPT_{candidate['execution_binding']['run_id']}_v1.0",
            "schema_version": SCHEMA_VERSION,
            "receipt_type": "FOCUSED_PRECHECK_TERMINAL_RECEIPT",
            "generation_timestamp": GENERATION_TIMESTAMP,
            "generated_at_utc": candidate["generated_at_utc"],
        },
        "project_context": {
            "project": "AAA",
            "product": "ASSET AGENT ASA",
            "persona": "AAA-PMO-ORCHESTRATOR",
            "task_branch": TASK_BRANCH,
            "validation_claim": "FOCUSED_G11C7_PRECHECK_POLICY_PACKING_PROBES_ONLY",
        },
        "lineage": {
            "s2": {
                "run_id": "33403101817",
                "terminal": True,
                "rerun_authorized": False,
            },
            "s2_precheck_run_id": "33401871715",
            "s3_precheck": {
                "run_id": "33414615913",
                "job_id": "99562174243",
                "terminal": True,
                "rerun_authorized": False,
            },
            "s3_apply": {
                "run_id": "33414695818",
                "job_id": "99562427077",
                "terminal": True,
                "rerun_authorized": False,
            },
            "s3_terminal_receipt_commit": S3_TERMINAL_RECEIPT_COMMIT,
            "s3_terminal_receipt_blob": S3_TERMINAL_RECEIPT_BLOB,
            "g10_terminal": True,
            "g10_precheck_run_id": "33272691259",
            "g10_live_run_id": "33273146915",
            "g10_rerun_authorized": False,
            "g11_precheck_run_id": "33465583987",
            "g11_live_run_id": "33466306591",
            "g11_terminal": True,
            "g11_rerun_authorized": False,
            "g11c2_precheck_run_id": "33469887723",
            "g11c2_precheck_terminal": True,
            "g11c2_live_run_exists": False,
            "g11c2_reuse_authorized": False,
            "g11c3_precheck_run_id": "33472741288",
            "g11c3_live_run_id": "33473465774",
            "g11c3_terminal": True,
            "g11c3_reuse_authorized": False,
            "g11c4_precheck_run_id": "33477019917",
            "g11c4_precheck_job_id": "99758300336",
            "g11c4_precheck_run_attempt": 1,
            "g11c4_terminal": True,
            "g11c4_live_run_exists": False,
            "g11c4_reuse_authorized": False,
            "g11c5_precheck_run_id": "33479444941",
            "g11c5_precheck_job_id": "99765558713",
            "g11c5_precheck_run_attempt": 1,
            "g11c5_precheck_execution_result": "PASS",
            "g11c5_terminal_receipt_result": "FAIL_CLOSED",
            "g11c5_terminal_receipt_contract_valid": False,
            "g11c5_terminal": True,
            "g11c5_live_run_exists": False,
            "g11c5_reuse_authorized": False,
            "g11c6_precheck_run_id": "33484842311",
            "g11c6_precheck_job_id": "99782407546",
            "g11c6_precheck_run_attempt": 1,
            "g11c6_precheck_execution_result": "NOT_RUN_PRE_OIDC",
            "g11c6_terminal_receipt_result": "FAIL_CLOSED",
            "g11c6_terminal_receipt_contract_valid": True,
            "g11c6_terminal": True,
            "g11c6_live_run_exists": False,
            "g11c6_credentials_issued": 0,
            "g11c6_runner_started": False,
            "g11c6_live_execution_started": False,
            "g11c6_reuse_authorized": False,
            "same_activation_reuse_authorized": False,
            "same_run_retry_authorized": False,
        },
        "projection_binding": {
            "base_date": BASE_DATE,
            "source_rows": 40,
            "eligible_rows": 35,
            "excluded_rows": 5,
            "missing_rows": 0,
            "excluded_global_row_ordinals": [36, 37, 38, 39, 40],
            "known_conflict_global_row_ordinals": [37, 39],
            "prior_matching_global_row_ordinals": [36, 38, 40],
            "selector_match_left_eligible": False,
            "eligible_projection_sha256": ELIGIBLE_PROJECTION_SHA256,
            "selector_custody_sha256": S3_SELECTOR_CUSTODY_SHA256,
            "source_rows_mutated": False,
            "source_admission_verdict": "NOT_ADMITTED",
            "issuer_identity_resolved": False,
        },
        "authority_binding": candidate["authority_binding"],
        "material_bindings": candidate["authority_binding"],
        "predecessor_terminal_g11c4_binding": candidate[
            "predecessor_terminal_g11c4_binding"
        ],
        "predecessor_terminal_g11c5_binding": candidate[
            "predecessor_terminal_g11c5_binding"
        ],
        "predecessor_terminal_g11c6_binding": candidate[
            "predecessor_terminal_g11c6_binding"
        ],
        "policy_material_bindings": candidate["policy_material_bindings"],
        "execution_binding": candidate["execution_binding"],
        "fresh_identity_binding": candidate["fresh_identity_binding"],
        "activation_binding": candidate["activation_binding"],
        "route_contract": candidate["route_contract"],
        "checks": candidate["checks"],
        "observed_effects": candidate["observed_effects"],
        "read_only_observations": candidate["read_only_observations"],
        "runner_result": candidate["runner_result"],
        "claims": candidate["claims"],
        "effect_reconciliation": {
            "provider_calls": candidate["observed_effects"]["finance_provider_api_calls"],
            "quota_reservations": candidate["observed_effects"]["provider_quota_reservations"],
            "raw_writes": candidate["observed_effects"]["raw_objects_written"],
            "s3_put_delete_copy": (
                candidate["observed_effects"]["s3_put_calls"]
                + candidate["observed_effects"]["s3_delete_calls"]
                + candidate["observed_effects"]["s3_copy_calls"]
            ),
            "repository_mutations_by_workflow": candidate["observed_effects"]["github_repository_mutations_by_workflow"],
            "remote_custody_mutations": candidate["observed_effects"]["remote_custody_mutations"],
            "aws_calls": candidate["observed_effects"]["aws_calls"],
            "sts_calls": candidate["observed_effects"]["sts_calls"],
            "sts_assume_role_attempts": candidate["observed_effects"]["sts_assume_role_attempts"],
            "sts_sessions_assumed": candidate["observed_effects"]["sts_sessions_assumed"],
            "sts_get_caller_identity_calls": candidate["observed_effects"]["sts_get_caller_identity_calls"],
            "credentials_issued": candidate["observed_effects"]["credentials_issued"],
            "s3_calls": candidate["observed_effects"]["s3_calls"],
            "all_mutation_effects_zero": all(
                candidate["observed_effects"][key] == 0 for key in ZERO_MUTATION_EFFECTS
            ),
            "effects_reconciled": candidate["observed_effects"]["effects_reconciled"],
            "ambiguous_side_effects": candidate["observed_effects"]["ambiguous_side_effects"],
        },
        "claim_ceiling": {
            "validation_claim": (
                "FOCUSED_G11C7_PRECHECK_POLICY_PACKING_PROBES_ONLY"
                if passed else "NONE"
            ),
            "oidc_sts_policy_packing_probe_sessions": 3 if passed else 0,
            "temporary_credentials_issued_for_probe_sessions": 3 if passed else 0,
            "live_authorized": False,
            "source_admission_verdict": "NOT_ADMITTED",
            "g2_pass": False,
            "g3_pass": False,
            "issuer_identity_resolved": False,
            "normalization": False,
            "pit": False,
            "promotion": False,
            "release": False,
            "production": False,
        },
        "no_rerun": {
            "consumed_g10_precheck_run": "33272691259",
            "consumed_g10_live_run": "33273146915",
            "consumed_s2_precheck_run": "33401871715",
            "consumed_s2_live_run": "33403101817",
            "consumed_s3_precheck_run": "33414615913",
            "consumed_s3_apply_run": "33414695818",
            "consumed_g11_precheck_run": "33465583987",
            "consumed_g11_live_run": "33466306591",
            "consumed_g11c2_precheck_run": "33469887723",
            "consumed_g11c3_precheck_run": "33472741288",
            "consumed_g11c3_live_run": "33473465774",
            "consumed_g11c4_precheck_run": "33477019917",
            "consumed_g11c5_precheck_run": "33479444941",
            "consumed_g11c6_precheck_run": "33484842311",
            "g11c6_precheck_run_id": "33484842311",
            "g11c6_precheck_job_id": "99782407546",
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
            "consumed_g11_generation_id": "FINANCE-PAGE100-G11-20260901110618",
            "consumed_g11_runtime_lock_id": "PMO-FINANCE-PAGE100-G11-20260901110618",
            "consumed_g11_pilot_run_id": "FINANCE-PAGE100-PILOT-G11-20260901110618",
            "consumed_g11_precheck_act_id": "FINANCE-PAGE100-PRECHECK-ACT-G11-20260901110618",
            "consumed_g11_live_act_id": "FINANCE-PAGE100-LIVE-ACT-G11-20260901110618",
            "consumed_g11_latch_event_id": "FINANCE-PAGE100-LATCH-G11-20260901110618",
            "consumed_generation_ids": [
                "FINANCE-PAGE100-G11-20260901110618",
                "FINANCE-PAGE100-G11C1-20260901123521",
                "FINANCE-PAGE100-G11C2-20260901130250",
                "FINANCE-PAGE100-G11C3-20260901134119",
                "FINANCE-PAGE100-G11C4-20260901143300",
                "FINANCE-PAGE100-G11C5-20260901152200",
                "FINANCE-PAGE100-G11C6-20260901155700",
            ],
            "consumed_runtime_lock_ids": [
                "PMO-FINANCE-PAGE100-G11-20260901110618",
                "PMO-FINANCE-PAGE100-G11C1-20260901123521",
                "PMO-FINANCE-PAGE100-G11C2-20260901130250",
                "PMO-FINANCE-PAGE100-G11C3-20260901134119",
                "PMO-FINANCE-PAGE100-G11C4-20260901143300",
                "PMO-FINANCE-PAGE100-G11C5-20260901152200",
                "PMO-FINANCE-PAGE100-G11C6-20260901155700",
            ],
            "consumed_pilot_run_ids": [
                "FINANCE-PAGE100-PILOT-G11-20260901110618",
                "FINANCE-PAGE100-PILOT-G11C1-20260901123521",
                "FINANCE-PAGE100-PILOT-G11C2-20260901130250",
                "FINANCE-PAGE100-PILOT-G11C3-20260901134119",
                "FINANCE-PAGE100-PILOT-G11C4-20260901143300",
                "FINANCE-PAGE100-PILOT-G11C5-20260901152200",
                "FINANCE-PAGE100-PILOT-G11C6-20260901155700",
            ],
            "consumed_preparation_ids": [
                "FINANCE-PAGE100-G11C1-PREPARATION-20260901123521",
                "FINANCE-PAGE100-G11C2-PREPARATION-20260901130250",
                "FINANCE-PAGE100-G11C3-PREPARATION-20260901134119",
                "FINANCE-PAGE100-G11C4-PREPARATION-20260901143300",
                "FINANCE-PAGE100-G11C5-PREPARATION-20260901152200",
                "FINANCE-PAGE100-G11C6-PREPARATION-20260901155700",
            ],
            "consumed_precheck_act_ids": [
                "FINANCE-PAGE100-PRECHECK-ACT-G11-20260901110618",
                "FINANCE-PAGE100-PRECHECK-ACT-G11C1-20260901123521",
                "FINANCE-PAGE100-PRECHECK-ACT-G11C2-20260901130250",
                "FINANCE-PAGE100-PRECHECK-ACT-G11C3-20260901134119",
                "FINANCE-PAGE100-PRECHECK-ACT-G11C4-20260901143300",
                "FINANCE-PAGE100-PRECHECK-ACT-G11C5-20260901152200",
                "FINANCE-PAGE100-PRECHECK-ACT-G11C6-20260901155700",
            ],
            "consumed_live_act_ids": [
                "FINANCE-PAGE100-LIVE-ACT-G11-20260901110618",
                "FINANCE-PAGE100-LIVE-ACT-G11C1-20260901123521",
                "FINANCE-PAGE100-LIVE-ACT-G11C2-20260901130250",
                "FINANCE-PAGE100-LIVE-ACT-G11C3-20260901134119",
                "FINANCE-PAGE100-LIVE-ACT-G11C4-20260901143300",
                "FINANCE-PAGE100-LIVE-ACT-G11C5-20260901152200",
                "FINANCE-PAGE100-LIVE-ACT-G11C6-20260901155700",
            ],
            "consumed_latch_event_ids": [
                "FINANCE-PAGE100-LATCH-G11-20260901110618",
                "FINANCE-PAGE100-LATCH-G11C1-20260901123521",
                "FINANCE-PAGE100-LATCH-G11C2-20260901130250",
                "FINANCE-PAGE100-LATCH-G11C3-20260901134119",
                "FINANCE-PAGE100-LATCH-G11C4-20260901143300",
                "FINANCE-PAGE100-LATCH-G11C5-20260901152200",
                "FINANCE-PAGE100-LATCH-G11C6-20260901155700",
            ],
            "current_run_retry_authorized": False,
            "same_activation_reuse_authorized": False,
            "same_latch_reuse_authorized": False,
        },
        "live_adapter_gate": {
            "runner_reported_readiness": adapter_readiness,
            "state": (
                "CLOSED_AWAITING_SEPARATE_FRESH_LIVE_ACTIVATION"
                if passed and adapter_readiness == "READY"
                else (
                    "CLOSED_ADAPTER_NOT_EXECUTABLE"
                    if passed
                    else "CLOSED_PRECHECK_FAILED"
                )
            ),
            "precheck_pass_is_necessary_not_sufficient": True,
            "precheck_receipt_alone_authorizes_live": False,
            "live_activation_observed": False,
            "live_provider_adapter_enabled": False,
            "live_s3_write_adapter_enabled": False,
            "required_live_act_id": candidate["fresh_identity_binding"]["live_act_id"],
            "required_latch_event_id": candidate["fresh_identity_binding"]["latch_event_id"],
        },
        "terminal": {
            "result": "PASS" if passed else "FAIL_CLOSED",
            "terminal_state": terminal_state,
            "precheck_complete": True,
            "failed_invariants": failures,
            "live_authorized": False,
            "live_execution_started": False,
            "separate_live_authority_required": True,
            "separate_live_activation_and_latch_required": True,
            "live_entry_disposition": (
                "ELIGIBLE_FOR_SEPARATE_LIVE_ACTIVATION_EVALUATION"
                if passed and adapter_readiness == "READY"
                else "NOT_ELIGIBLE_FOR_LIVE"
            ),
            "receipt_authorizes_provider_calls": False,
            "receipt_authorizes_quota_reservations": False,
            "receipt_authorizes_s3_mutations": False,
            "receipt_authorizes_repository_mutations": False,
            "receipt_authorizes_normalization_pit_promotion_release_production": False,
            "rerun_authorized": False,
        },
    }
    receipt["receipt_integrity"] = {
        "canonicalization": "UTF8_JSON_SORT_KEYS_COMPACT_EXCLUDING_RECEIPT_INTEGRITY",
        "payload_sha256": hashlib.sha256(_canonical_bytes(receipt)).hexdigest(),
    }
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    try:
        candidate = json.loads(args.input.read_text(encoding="utf-8"))
        if not isinstance(candidate, dict):
            raise ReceiptError("input root must be an object")
        receipt = build_receipt(candidate)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    except (OSError, json.JSONDecodeError, ReceiptError) as exc:
        print(f"receipt generation failed: {exc}", file=sys.stderr)
        return 2

    print(
        json.dumps(
            {
                "output": str(args.output),
                "result": receipt["terminal"]["result"],
                "terminal_state": receipt["terminal"]["terminal_state"],
                "live_authorized": False,
                "payload_sha256": receipt["receipt_integrity"]["payload_sha256"],
            },
            sort_keys=True,
        )
    )
    return 0 if receipt["terminal"]["result"] == "PASS" else 3


if __name__ == "__main__":
    raise SystemExit(main())
