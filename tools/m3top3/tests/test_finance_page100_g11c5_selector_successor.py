from __future__ import annotations

import copy
import hashlib
import json
import re
import sys
import tempfile
from argparse import Namespace
from contextlib import contextmanager
from pathlib import Path

MODULE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MODULE_DIR))

import finance_page100_g11c5_selector_successor as g11c5  # noqa: E402


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


def raw_ref() -> g11c5.SealedRawReference:
    return g11c5.SealedRawReference(
        key=(
            "raw/public-data-api/M3TOP3-FINANCE-STOCK-RIGHTS-v1/"
            "_pilot_generation/G11C5/20260901152200/page-5.json"
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
) -> g11c5.HashedSourceRow:
    return g11c5.HashedSourceRow(
        bas_dt=g11c5.SEED_BASE_DATE,
        page_no=page_no,
        page_item_ordinal=page_item_ordinal,
        global_row_ordinal=ordinal,
        custody_key_sha256=custody_hash,
        observed_identity_sha256=identity_hash,
    )


def seeded_state() -> g11c5.ProjectionState:
    return g11c5.ProjectionState(
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
    path = MODULE_DIR / "finance_page100_g11c5_live_adapter.py"
    return {
        "ready": True,
        "path": g11c5.LIVE_ADAPTER_REPO_PATH,
        "sha256": g11c5.sha256_file(path),
        "git_blob": g11c5.git_blob_sha1_file(path),
        "factory_symbol": g11c5.LIVE_ADAPTER_FACTORY_SYMBOL,
        "interface_version": g11c5.LIVE_ADAPTER_INTERFACE_VERSION,
    }


def predecessor_ineligible_preparation_binding() -> dict:
    return {
        "preparation_commit": g11c5.PREDECESSOR_G11C1_PREPARATION_COMMIT,
        "preparation_tree": g11c5.PREDECESSOR_G11C1_PREPARATION_TREE,
        "activation_created": False,
        "precheck_activation_created": False,
        "live_activation_created": False,
        "precheck_run_created": False,
        "live_run_created": False,
        "reuse_authorized": False,
        "terminal_receipt_path": g11c5.PREDECESSOR_G11C1_TERMINAL_RECEIPT_PATH,
        "terminal_receipt_sha256": g11c5.PREDECESSOR_G11C1_TERMINAL_RECEIPT_SHA256,
        "terminal_receipt_git_blob":
            g11c5.PREDECESSOR_G11C1_TERMINAL_RECEIPT_GIT_BLOB,
        "terminal_receipt_payload_sha256":
            g11c5.PREDECESSOR_G11C1_TERMINAL_RECEIPT_PAYLOAD_SHA256,
        "terminal_receipt_bytes": g11c5.PREDECESSOR_G11C1_TERMINAL_RECEIPT_BYTES,
    }


def consumed_g11c1_identity_lists() -> dict:
    return {
        field_name: list(values)
        for field_name, values in g11c5.PREDECESSOR_G11C1_IDENTITIES.items()
    }


def predecessor_invalidated_g11c2_binding() -> dict:
    return g11c5.predecessor_invalidated_g11c2_binding()


def predecessor_terminal_g11c3_binding() -> dict:
    return g11c5.predecessor_terminal_g11c3_binding()


def predecessor_terminal_g11c4_binding() -> dict:
    return g11c5.predecessor_terminal_g11c4_binding()


def consumed_predecessor_lineage() -> dict:
    result = consumed_g11c1_identity_lists()
    for field_name, values in g11c5.PREDECESSOR_G11C2_IDENTITIES.items():
        result.setdefault(field_name, []).extend(values)
    result.update({
        "g11c2_precheck_run_id": g11c5.PREDECESSOR_G11C2_PRECHECK_RUN_ID,
        "g11c2_precheck_run_attempt": g11c5.PREDECESSOR_G11C2_PRECHECK_RUN_ATTEMPT,
        "g11c2_precheck_rerun_authorized": False,
        "g11c2_live_run_exists": False,
        "g11c2_activation_reuse_authorized": False,
        "g11c2_generation_reuse_authorized": False,
    })
    for field_name, values in g11c5.PREDECESSOR_G11C3_IDENTITIES.items():
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
    for field_name, values in g11c5.PREDECESSOR_G11C4_IDENTITIES.items():
        result.setdefault(field_name, []).extend(values)
    result.update({
        "g11c4_precheck_run_id": g11c5.PREDECESSOR_G11C4_PRECHECK_RUN_ID,
        "g11c4_precheck_run_attempt": g11c5.PREDECESSOR_G11C4_PRECHECK_RUN_ATTEMPT,
        "g11c4_precheck_rerun_authorized": False,
        "g11c4_credentials_issued": 0,
        "g11c4_runner_started": False,
        "g11c4_activation_reuse_authorized": False,
        "g11c4_generation_reuse_authorized": False,
    })
    return result


def authority_document() -> dict:
    safe_adapter = safe_adapter_document()
    return {
        "artifact": g11c5.AUTHORITY_SCHEMA,
        "schema_version": 1,
        "generation_timestamp": g11c5.GENERATION_TIMESTAMP,
        "authority_commit": g11c5.AUTHORITY_COMMIT,
        "owner_authority_binding": {
            "commit": g11c5.OWNER_APPROVAL_COMMIT,
            "governing_forward_only_receipt_path": (
                "control/m3top3/public-data-source-admission/v1.0/"
                "M3TOP3_FINANCE_CA_PAGE100_G11_DOWNSTREAM_OWNER_DECISION_RECEIPT_v1.1.json"
            ),
            "governing_forward_only_receipt_commit": g11c5.GOVERNED_CORRECTION_HEAD,
            "governing_forward_only_receipt_git_blob": g11c5.OWNER_DECISION_V1_1_GIT_BLOB,
            "governing_forward_only_receipt_sha256": g11c5.OWNER_DECISION_V1_1_SHA256,
        },
        "predecessor_ineligible_preparation_binding":
            predecessor_ineligible_preparation_binding(),
        "predecessor_invalidated_g11c2_binding":
            predecessor_invalidated_g11c2_binding(),
        "predecessor_terminal_g11c3_binding":
            predecessor_terminal_g11c3_binding(),
        "predecessor_terminal_g11c4_binding":
            predecessor_terminal_g11c4_binding(),
        "fresh_identity": {
            "generation_id": g11c5.GENERATION_ID,
            "runtime_lock_id": g11c5.RUNTIME_LOCK_ID,
            "pilot_run_id": g11c5.PILOT_RUN_ID,
            "preparation_id": g11c5.PREPARATION_ID,
            "precheck_act_id": g11c5.PRECHECK_ACT_ID,
            "live_act_id": g11c5.LIVE_ACT_ID,
            "latch_event_id": g11c5.LATCH_EVENT_ID,
            "owner_cap_spec_sha256": g11c5.OWNER_CAP_SPEC_SHA256,
            "execution_token_sha256": g11c5.EXECUTION_TOKEN_SHA256,
            "identity_reuse_authorized": False,
        },
        "owner_cap_spec": g11c5.expected_owner_cap_spec(),
        "owner_cap_spec_canonicalization": "UTF8_JSON_SORT_KEYS_COMPACT_TRAILING_LF",
        "owner_cap_spec_sha256": g11c5.OWNER_CAP_SPEC_SHA256,
        "execution_token_material": g11c5.expected_execution_token_material(),
        "execution_token_material_canonicalization": "UTF8_JSON_SORT_KEYS_COMPACT_TRAILING_LF",
        "execution_token_sha256": g11c5.EXECUTION_TOKEN_SHA256,
        "authorized_route": {
            "route": (
                "RESUME_PAGE100_RAW_ACQUISITION_FROM_EXACT_G10_CHECKPOINT_"
                "AT_20240131_PAGE_5"
            ),
            "one_fresh_exact_three_sts_probe_precheck_authorized": True,
            "github_run_attempt_required": 1,
        },
        "sealed_s3_projection_binding": {
            "bas_dt": g11c5.SEED_BASE_DATE,
            "source_rows": 40,
            "eligible_rows": 35,
            "excluded_rows_at_sealed_seed": 5,
            "missing_rows": 0,
            "excluded_global_row_ordinals": [36, 37, 38, 39, 40],
            "sealed_eligible_projection_sha256": g11c5.SEALED_SEED_PROJECTION_SHA256,
            "selector_algorithm": g11c5.SELECTOR_ALGORITHM,
            "selector_custody_key_sha256": g11c5.TARGET_CUSTODY_SHA256,
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
            "g10_checkpoint_sha256": g11c5.PREDECESSOR_CHECKPOINT_SHA256,
            "resume_bas_dt": g11c5.SEED_BASE_DATE,
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
        "adapter_execution_order_binding": g11c5.expected_adapter_execution_order(),
        "live_pre_mutation_order": g11c5.expected_live_pre_mutation_order(),
        "entry_gate": {
            "live_adapter_gate": g11c5.LIVE_ADAPTER_GATE_READY,
            "live_session_policy_ascii_and_size_ceiling_verified": True,
        },
        "safe_executable_adapter": safe_adapter,
        "custody_boundary": {
            "g11_raw_prefix": g11c5.G11_RAW_PREFIX,
            "g11_control_prefix": g11c5.G11_CONTROL_PREFIX,
            "execution_claim_key": g11c5.EXECUTION_CLAIM_KEY,
            "predecessor_objects_immutable": True,
        },
        "no_rerun": {
            "consumed_github_runs": list(g11c5.REQUIRED_NO_RERUN_RUNS),
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
        "artifact": g11c5.PLAN_SCHEMA,
        "schema_version": 1,
        "generation_timestamp": g11c5.GENERATION_TIMESTAMP,
        "authority_commit": g11c5.AUTHORITY_COMMIT,
        "generation_id": g11c5.GENERATION_ID,
        "authority": {"owner_authority_commit": g11c5.OWNER_APPROVAL_COMMIT},
        "predecessor_ineligible_preparation_binding":
            predecessor_ineligible_preparation_binding(),
        "predecessor_invalidated_g11c2_binding":
            predecessor_invalidated_g11c2_binding(),
        "predecessor_terminal_g11c3_binding":
            predecessor_terminal_g11c3_binding(),
        "predecessor_terminal_g11c4_binding":
            predecessor_terminal_g11c4_binding(),
        "identity": {
            "generation_id": g11c5.GENERATION_ID,
            "runtime_lock_id": g11c5.RUNTIME_LOCK_ID,
            "pilot_run_id": g11c5.PILOT_RUN_ID,
            "preparation_id": g11c5.PREPARATION_ID,
            "precheck_act_id": g11c5.PRECHECK_ACT_ID,
            "live_act_id": g11c5.LIVE_ACT_ID,
            "latch_event_id": g11c5.LATCH_EVENT_ID,
            "owner_cap_spec_sha256": g11c5.OWNER_CAP_SPEC_SHA256,
            "execution_token_sha256": g11c5.EXECUTION_TOKEN_SHA256,
        },
        "resume_and_seed_contract": {
            "checkpoint_seed_path": (
                "control/m3top3/public-data-source-admission/v1.0/"
                + g11c5.SEED_FILENAME
            ),
            "checkpoint_seed_sha256": g11c5.sha256_file(seed_path),
            "checkpoint_seed_git_blob": g11c5.git_blob_sha1_file(seed_path),
            "predecessor_checkpoint_sha256": g11c5.PREDECESSOR_CHECKPOINT_SHA256,
            "start_bas_dt": g11c5.SEED_BASE_DATE,
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
                "actions": g11c5.expected_live_seed_verification_actions(),
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
        "artifact": g11c5.SEED_SCHEMA,
        "schema_version": 1,
        "generation_timestamp": g11c5.GENERATION_TIMESTAMP,
        "authority_commit": g11c5.AUTHORITY_COMMIT,
        "predecessor_ineligible_preparation_binding":
            predecessor_ineligible_preparation_binding(),
        "predecessor_invalidated_g11c2_binding":
            predecessor_invalidated_g11c2_binding(),
        "predecessor_terminal_g11c3_binding":
            predecessor_terminal_g11c3_binding(),
        "predecessor_terminal_g11c4_binding":
            predecessor_terminal_g11c4_binding(),
        "no_rerun": consumed_predecessor_lineage(),
        "bas_dt": g11c5.SEED_BASE_DATE,
        "next_page": 5,
        "predecessor": {
            "checkpoint_sha256": g11c5.PREDECESSOR_CHECKPOINT_SHA256,
            "validated_raw_pages": [1, 2, 3, 4],
        },
        "projection": {
            "selector_algorithm": g11c5.SELECTOR_ALGORITHM,
            "selector_sha256": g11c5.TARGET_CUSTODY_SHA256,
            "eligible_projection_sha256": g11c5.SEALED_SEED_PROJECTION_SHA256,
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
    assert g11c5.GENERATION_TIMESTAMP == "20260901152200"
    assert g11c5.OWNER_APPROVAL_COMMIT == "884e1fadebda480f4c38d172eab083cbdbf031b2"
    assert g11c5.AUTHORITY_COMMIT == "19a62491c5168ee4c5f8ece31eba7598f11ebbbc"
    assert g11c5.GOVERNED_CORRECTION_HEAD == "19a62491c5168ee4c5f8ece31eba7598f11ebbbc"
    assert g11c5.GOVERNED_CORRECTION_TREE == "572bf2ab23a7d761de8160e6828f8b074618391b"
    assert g11c5.ACTIVATION_BASE_HEAD_COMMIT == "6e4660cfbb1730dcaeaa2908c9e1a38de012a920"
    assert g11c5.ACTIVATION_BASE_TREE == "3e4a53a6df8ac7fa4f500c51a951ae9c900476d8"
    assert g11c5.PREDECESSOR_G11C1_PREPARATION_COMMIT == (
        "0ccb62cd4c0ceaa0409a56b40a899d00f531ba09"
    )
    assert g11c5.PREDECESSOR_G11C1_PREPARATION_TREE == (
        "f35d2bdd68138d527bc8603472311c0ca032988e"
    )
    assert g11c5.OWNER_CAP_SPEC_SHA256 == "f912a117a170096d752fe269913848a93614544857c854dad23a2283f5387156"
    assert g11c5.EXECUTION_TOKEN_SHA256 == "9bb9c44d64b68699d90b9764b1add085515ec43a1958a0fedcc1a62770f465de"
    assert g11c5.TARGET_CUSTODY_SHA256 == (
        "f3e7b94dbde722df47cc3bb1a5615068cea42dc1994a91ce92317f5d1fb8b3d6"
    )
    assert g11c5.SEALED_SEED_PROJECTION_SHA256 == (
        "8f6986c9a9839ad62fe856dd0c4d31b54ce1982373deffd1404671c4c9fbfd24"
    )
    assert (g11c5.INHERITED_G10_ACQUISITIONS, g11c5.G11_ACQUISITION_CEILING) == (4, 1696)
    assert (g11c5.INHERITED_G10_ATTEMPTS, g11c5.G11_ATTEMPT_CEILING) == (4, 1996)
    assert g11c5.FIRST_NEW_PAGE == 5
    assert 33272691259 in g11c5.REQUIRED_NO_RERUN_RUNS
    assert 33273146915 in g11c5.REQUIRED_NO_RERUN_RUNS
    assert 33465583987 in g11c5.REQUIRED_NO_RERUN_RUNS
    assert 33466306591 in g11c5.REQUIRED_NO_RERUN_RUNS
    assert 33469887723 in g11c5.REQUIRED_NO_RERUN_RUNS
    assert 33472741288 in g11c5.REQUIRED_NO_RERUN_RUNS
    assert 33473465774 in g11c5.REQUIRED_NO_RERUN_RUNS
    assert 33477019917 in g11c5.REQUIRED_NO_RERUN_RUNS
    assert "FINANCE-PAGE100-G11C1-20260901123521" in (
        g11c5.PREDECESSOR_G11C1_IDENTITIES["consumed_generation_ids"]
    )
    assert "FINANCE-PAGE100-G11C2-20260901130250" in (
        g11c5.PREDECESSOR_G11C2_IDENTITIES["consumed_generation_ids"]
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
    assert list(g11c5.LIVE_PRE_MUTATION_PHASES) == [
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
    first, result = g11c5.project_hashed_rows(rows)
    second, _ = g11c5.project_hashed_rows(rows)
    assert first.eligible_projection_sha256 == second.eligible_projection_sha256
    assert result.source_rows == result.eligible_rows == 2
    assert result.excluded_rows == result.missing_rows == 0
    assert first.source_rows == first.eligible_rows + first.excluded_rows + first.missing_rows


def test_only_sealed_seed_ordinals_36_through_40_can_be_excluded() -> None:
    state = g11c5.ProjectionState(source_rows=35, eligible_rows=35)
    result_state, result = g11c5.project_hashed_rows(
        [row(36, g11c5.TARGET_CUSTODY_SHA256, None, page_no=4, page_item_ordinal=6)],
        state,
        selector_policy=g11c5.SEED_SELECTOR_POLICY,
    )
    assert result.excluded_global_row_ordinals == (36,)
    assert result_state.excluded_rows == 1
    assert g11c5.TARGET_CUSTODY_SHA256 not in result_state.identity_map

    with raises(g11c5.GateError, match="SEALED_SELECTOR_SCOPE_VIOLATION"):
        g11c5.project_hashed_rows(
            [row(1, g11c5.TARGET_CUSTODY_SHA256, None, page_no=1)],
            selector_policy=g11c5.SEED_SELECTOR_POLICY,
        )


def test_future_selector_match_requires_raw_custody_then_stops_pending_owner() -> None:
    original = seeded_state()
    with raises(g11c5.FutureSelectorObservationError) as captured:
        g11c5.project_hashed_rows(
            [row(41, g11c5.TARGET_CUSTODY_SHA256, h("changed identity"))],
            original,
            raw_ref=raw_ref(),
            require_sealed_raw=True,
            selector_policy=g11c5.FUTURE_SELECTOR_POLICY,
        )
    assert captured.value.code == "FUTURE_SELECTOR_OBSERVED_PENDING_OWNER_DECISION"
    # Transactional core returns no advanced state on the terminal observation.
    assert original.source_rows == 40
    assert original.excluded_rows == 5


def test_future_selector_cannot_be_observed_before_raw_seal() -> None:
    with raises(g11c5.GateError, match="RAW_NOT_SEALED"):
        g11c5.project_hashed_rows(
            [row(41, g11c5.TARGET_CUSTODY_SHA256, None)],
            seeded_state(),
            require_sealed_raw=True,
        )


def test_non_target_conflict_and_missing_fields_fail_transactionally_after_raw_seal() -> None:
    original = seeded_state()
    with raises(g11c5.NonTargetIdentityConflictError):
        g11c5.project_hashed_rows(
            [row(41, h("custody-a"), h("identity-b"))],
            original,
            raw_ref=raw_ref(),
            require_sealed_raw=True,
        )
    assert original.source_rows == 40

    with raises(g11c5.MissingCustodyError):
        g11c5.project_hashed_rows(
            [row(41, None, h("identity"))],
            original,
            raw_ref=raw_ref(),
            require_sealed_raw=True,
        )
    with raises(g11c5.MissingIdentityError):
        g11c5.project_hashed_rows(
            [row(41, h("new custody"), None)],
            original,
            raw_ref=raw_ref(),
            require_sealed_raw=True,
        )
    assert original.source_rows == 40


def test_budget_exact_boundaries_and_per_page_attempt_gate() -> None:
    last = g11c5.BudgetState(g11_acquisitions=1695, g11_attempts=1995)
    terminal = last.reserve_attempt(new_unique_acquisition=True, page_attempt=2)
    assert terminal.effective_acquisitions == 1700
    assert terminal.effective_attempts == 2000
    assert terminal.remaining_acquisitions == terminal.remaining_attempts == 0
    with raises(g11c5.GateError, match="ACQUISITION_CEILING"):
        terminal.reserve_attempt(new_unique_acquisition=True, page_attempt=1)
    with raises(g11c5.GateError, match="ATTEMPTS_PER_PAGE_CEILING"):
        g11c5.BudgetState().reserve_attempt(new_unique_acquisition=True, page_attempt=3)


def test_append_only_namespace_guard_rejects_historical_keys() -> None:
    g11c5.validate_g11_object_key(
        "raw/public-data-api/source/G11C5/20260901152200/page-5.json"
    )
    with raises(g11c5.GateError, match="HISTORICAL_NAMESPACE_WRITE_FORBIDDEN"):
        g11c5.validate_g11_object_key(
            "raw/public-data-api/source/G10/G11C5/20260901152200/page-5.json"
        )


def test_active_raw_and_control_prefixes_reject_g11_through_g11c4() -> None:
    g11c5.validate_active_c5_prefixes(g11c5.G11_RAW_PREFIX, g11c5.G11_CONTROL_PREFIX)
    for historical in ("G11", "G11C1", "G11C2", "G11C3", "G11C4"):
        old_raw = g11c5.G11_RAW_PREFIX.replace("G11C5", historical)
        old_control = g11c5.G11_CONTROL_PREFIX.replace("G11C5", historical)
        with raises(g11c5.GateError, match="HISTORICAL_ACTIVE_PREFIX_FORBIDDEN"):
            g11c5.validate_active_c5_prefixes(old_raw, g11c5.G11_CONTROL_PREFIX)
        with raises(g11c5.GateError, match="HISTORICAL_ACTIVE_PREFIX_FORBIDDEN"):
            g11c5.validate_active_c5_prefixes(g11c5.G11_RAW_PREFIX, old_control)


def test_precheck_receipt_append_and_execution_roles_are_not_collapsed() -> None:
    receipt = {"execution_binding": {"head_sha": "a" * 40, "tree_sha": "b" * 40}}
    binding = {
        "receipt_append_commit": "c" * 40,
        "receipt_append_tree": "d" * 40,
        "execution_head_sha": "a" * 40,
        "execution_head_tree_sha": "b" * 40,
    }
    g11c5.validate_precheck_pass_role_binding(binding, receipt)

    collapsed = dict(binding)
    collapsed["receipt_append_commit"] = "a" * 40
    collapsed["receipt_append_tree"] = "b" * 40
    with raises(g11c5.GateError, match="PRECHECK_LINEAGE_ROLES_COLLAPSED"):
        g11c5.validate_precheck_pass_role_binding(collapsed, receipt)

    swapped = dict(binding)
    swapped["execution_head_sha"] = "c" * 40
    with raises(g11c5.GateError, match="execution_head_sha"):
        g11c5.validate_precheck_pass_role_binding(swapped, receipt)

    ambiguous = {**binding, "commit": "c" * 40, "tree": "d" * 40}
    with raises(g11c5.GateError, match="AMBIGUOUS_PRECHECK_LINEAGE_FIELDS"):
        g11c5.validate_precheck_pass_role_binding(ambiguous, receipt)


def test_sealed_adapter_dynamic_import_registers_dataclass_module_and_factory() -> None:
    adapter_path = MODULE_DIR / "finance_page100_g11c5_live_adapter.py"
    factory = g11c5.load_sealed_live_adapter_factory(
        adapter_path, g11c5.sha256_file(adapter_path)
    )
    assert callable(factory)
    assert factory.__name__ == g11c5.LIVE_ADAPTER_FACTORY_SYMBOL


def test_runtime_live_head_markers_resolve_only_from_exact_github_environment() -> None:
    head = "a" * 40
    tree = "b" * 40
    activation = {
        "activation_binding": {
            "live_activation_commit": g11c5.LIVE_HEAD_MARKER,
            "live_activation_tree": g11c5.LIVE_TREE_MARKER,
            "expected_branch_head_at_dispatch": g11c5.LIVE_HEAD_MARKER,
        }
    }
    observed = g11c5.validate_runtime_live_head_binding(
        activation,
        environment={
            "G11C5_LIVE_HEAD_SHA": head,
            "G11C5_LIVE_HEAD_TREE": tree,
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
    with raises(g11c5.GateError, match="live activation commit marker"):
        g11c5.validate_runtime_live_head_binding(
            embedded,
            environment={
                "G11C5_LIVE_HEAD_SHA": head,
                "G11C5_LIVE_HEAD_TREE": tree,
                "GITHUB_SHA": head,
                "GITHUB_RUN_ID": "123456789",
                "GITHUB_RUN_ATTEMPT": "1",
            },
        )

    with raises(g11c5.GateError, match="GITHUB_SHA"):
        g11c5.validate_runtime_live_head_binding(
            activation,
            environment={
                "G11C5_LIVE_HEAD_SHA": head,
                "G11C5_LIVE_HEAD_TREE": tree,
                "GITHUB_SHA": "c" * 40,
                "GITHUB_RUN_ID": "123456789",
                "GITHUB_RUN_ATTEMPT": "1",
            },
        )


def test_live_result_binds_actual_execution_and_single_terminal_put() -> None:
    execution = {
        "repository": g11c5.REPOSITORY,
        "branch": g11c5.BRANCH,
        "github_run_id": 123456789,
        "github_run_attempt": 1,
        "head_sha": "a" * 40,
        "tree_sha": "b" * 40,
    }

    def object_binding(name: str, *, key: str | None = None) -> dict:
        return {
            "key": key or f"raw/public-data-api/source/G11C5/{g11c5.GENERATION_TIMESTAMP}/{name}.json",
            "version_id": f"version-{name}",
            "etag": f'"etag-{name}"',
            "sha256": h(name),
            "bytes": 100,
            "content_type": "application/json",
            "server_side_encryption": "AES256",
        }

    effects = dict(g11c5.LIVE_PRE_ENTRY_EFFECTS)
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
        "schema": "M3TOP3_FINANCE_CA_PAGE100_G11C5_LIVE_ENTRY_RESULT_v1.0",
        "verdict": "PASS",
        "entry_gate": "LIVE_ENTERED_ONCE",
        "execution_binding": execution,
        "effects": effects,
        "effect_reconciliation": {"complete": True, "ambiguous_side_effects": False},
        "execution_claim_binding": object_binding("claim", key=g11c5.EXECUTION_CLAIM_KEY),
        "checkpoint_binding": object_binding("checkpoint", key=g11c5.G11_CHECKPOINT_KEY),
        "terminal_receipt_binding": {
            "key": g11c5.G11_TERMINAL_RECEIPT_KEY,
            "attempted": True,
            "put_attempts": 1,
            "confirmed": True,
            "object": object_binding("terminal", key=g11c5.G11_TERMINAL_RECEIPT_KEY),
        },
    }
    code, normalized = g11c5._normalize_and_validate_live_result(
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
    with raises(g11c5.GateError, match="terminal receipt attempt/write"):
        g11c5._normalize_and_validate_live_result(
            invalid, 0, expected_execution_binding=execution
        )


def test_pre_entry_live_result_preserves_three_session_effect_ledger() -> None:
    result = g11c5._pre_entry_live_failure("TEST_PRE_ENTRY_GATE")

    code, normalized = g11c5._normalize_and_validate_live_result(
        result, g11c5.EX_CONFIG
    )

    assert code == g11c5.EX_CONFIG
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
    assert g11c5.validate_seed_document(seed_document()) == "SEALED_RECEIPT_REUSE"


def test_plan_must_bind_exact_current_seed_sha_and_blob() -> None:
    with tempfile.TemporaryDirectory() as temporary_directory:
        seed_path = Path(temporary_directory) / g11c5.SEED_FILENAME
        write_json(seed_path, seed_document())
        plan = plan_document(seed_path)
        g11c5.validate_plan_seed_material_binding(plan, seed_path)
        write_json(seed_path, {**seed_document(), "state": "mutated-after-plan-binding"})
        with raises(g11c5.GateError, match="checkpoint_seed_sha256"):
            g11c5.validate_plan_seed_material_binding(plan, seed_path)


def test_live_session_policy_ascii_and_2048_character_limit() -> None:
    with tempfile.TemporaryDirectory() as temporary_directory:
        policy_path = Path(temporary_directory) / "live-policy.json"
        policies = g11c5.expected_split_session_policies()
        for role, policy in policies.items():
            write_json(policy_path, policy)
            exact_length = g11c5.validate_live_session_policy_for_aws(policy_path, role)
            assert exact_length <= 2048

        original_ceiling = g11c5.AWS_INLINE_SESSION_POLICY_ASCII_CHARACTER_CEILING
        try:
            role = "final_list_write_session_policy"
            write_json(policy_path, policies[role])
            exact_length = g11c5.validate_live_session_policy_for_aws(policy_path, role)
            g11c5.AWS_INLINE_SESSION_POLICY_ASCII_CHARACTER_CEILING = exact_length - 1
            with raises(g11c5.GateError, match="LIVE_SESSION_POLICY_EXCEEDS"):
                g11c5.validate_live_session_policy_for_aws(policy_path, role)
        finally:
            g11c5.AWS_INLINE_SESSION_POLICY_ASCII_CHARACTER_CEILING = original_ceiling

        forbidden_version = copy.deepcopy(policies["checkpoint_read_session_policy"])
        forbidden_version["Version"] = "2012-10-17"
        write_json(policy_path, forbidden_version)
        with raises(g11c5.GateError, match="VERSION_MUST_BE_OMITTED"):
            g11c5.validate_live_session_policy_for_aws(
                policy_path, "checkpoint_read_session_policy"
            )


def test_bundle_hash_bindings_and_precheck_sts_effect_contract() -> None:
    placeholder_cap = g11c5.OWNER_CAP_SPEC_SHA256
    placeholder_token = g11c5.EXECUTION_TOKEN_SHA256
    g11c5.OWNER_CAP_SPEC_SHA256 = g11c5.sha256_bytes(
        g11c5.canonical_json_lf_bytes(g11c5.expected_owner_cap_spec())
    )
    g11c5.EXECUTION_TOKEN_SHA256 = g11c5.sha256_bytes(
        g11c5.canonical_json_lf_bytes(g11c5.expected_execution_token_material())
    )
    with tempfile.TemporaryDirectory() as temporary_directory:
        tmp_path = Path(temporary_directory)
        authority_path = tmp_path / g11c5.AUTHORITY_FILENAME
        plan_path = tmp_path / g11c5.PLAN_FILENAME
        seed_path = tmp_path / g11c5.SEED_FILENAME
        manifest_path = tmp_path / g11c5.MANIFEST_FILENAME
        policy_filenames = {
            "checkpoint_read_session_policy":
                "M3TOP3_FINANCE_CA_PAGE100_G11C5_CHECKPOINT_READ_SESSION_POLICY_v1.0.json",
            "raw_four_read_session_policy":
                "M3TOP3_FINANCE_CA_PAGE100_G11C5_RAW_FOUR_READ_SESSION_POLICY_v1.0.json",
            "final_list_write_session_policy":
                "M3TOP3_FINANCE_CA_PAGE100_G11C5_FINAL_LIST_WRITE_SESSION_POLICY_v1.0.json",
        }
        repo_root = MODULE_DIR.parents[1]
        policy_paths = {
            role: repo_root / "control/m3top3/public-data-source-admission/v1.0" / filename
            for role, filename in policy_filenames.items()
        }
        test_path = Path(__file__).resolve()
        runner_path = Path(g11c5.__file__).resolve()
        adapter_path = MODULE_DIR / "finance_page100_g11c5_live_adapter.py"

        write_json(authority_path, authority_document())
        write_json(seed_path, seed_document())
        write_json(plan_path, plan_document(seed_path))
        safe_adapter = safe_adapter_document()

        def binding(path: Path) -> dict:
            return {
                "filename": path.name,
                "sha256": g11c5.sha256_file(path),
                "git_blob": g11c5.git_blob_sha1_file(path),
            }

        manifest = {
            "artifact": g11c5.MANIFEST_SCHEMA,
            "schema_version": 1,
            "generation_timestamp": g11c5.GENERATION_TIMESTAMP,
            "generation_id": g11c5.GENERATION_ID,
            "authority_commit": g11c5.AUTHORITY_COMMIT,
            "preparation_commit_binding": "DEFERRED_TO_ACTIVATION",
            "sealed_scope_summary": {
                "owner_cap_spec_sha256": g11c5.OWNER_CAP_SPEC_SHA256,
                "execution_token_sha256": g11c5.EXECUTION_TOKEN_SHA256,
                "fixed_quota_day_kst": g11c5.QUOTA_DAY_KST,
            },
            "adapter_execution_order_binding": g11c5.expected_adapter_execution_order(),
            "files": {
                "authority": binding(authority_path),
                "plan": binding(plan_path),
                "seed": binding(seed_path),
                "runner": binding(runner_path),
                "tests": binding(test_path),
                "adapter_tests": binding(test_path),
                "live_adapter": {
                    **binding(adapter_path),
                    "path": g11c5.LIVE_ADAPTER_REPO_PATH,
                },
                **{
                    role: {
                        **binding(policy_path),
                        "path": policy_path.relative_to(repo_root).as_posix(),
                    }
                    for role, policy_path in policy_paths.items()
                },
            },
            "live_adapter_gate": g11c5.LIVE_ADAPTER_GATE_READY,
            "live_adapter": {
                "executable": True,
                "sealed": True,
                "ready": True,
                **safe_adapter,
            },
            "safe_executable_adapter": safe_adapter,
        }
        write_json(manifest_path, manifest)

        result = g11c5.validate_bundle(
            authority_path=authority_path,
            plan_path=plan_path,
            seed_path=seed_path,
            manifest_path=manifest_path,
            pytest_path=test_path,
        )
        assert result["first_new_page"] == 5
        assert result["governed_correction_head"] == g11c5.GOVERNED_CORRECTION_HEAD
        assert result["live_adapter_gate"] == g11c5.LIVE_ADAPTER_GATE_READY
        assert g11c5.PRECHECK_STS_PROBE_EFFECTS["aws_calls"] == 6
        assert g11c5.PRECHECK_STS_PROBE_EFFECTS["sts_calls"] == 6
        assert g11c5.PRECHECK_STS_PROBE_EFFECTS["s3_calls"] == 0
        assert g11c5.PRECHECK_STS_PROBE_EFFECTS["provider_calls"] == 0
        assert g11c5.PRECHECK_STS_PROBE_EFFECTS["remote_custody_mutations"] == 0

        blocked = dict(manifest)
        blocked["live_adapter_gate"] = g11c5.LIVE_ADAPTER_GATE_BLOCKED
        blocked_manifest = tmp_path / ("blocked-" + g11c5.MANIFEST_FILENAME)
        write_json(blocked_manifest, blocked)
        with raises(g11c5.GateError, match="manifest.live_adapter_gate"):
            g11c5.validate_manifest_document(
                blocked,
                authority_path=authority_path,
                plan_path=plan_path,
                seed_path=seed_path,
                runner_path=runner_path,
                pytest_path=test_path,
                live_adapter_path=adapter_path,
            )
    g11c5.OWNER_CAP_SPEC_SHA256 = placeholder_cap
    g11c5.EXECUTION_TOKEN_SHA256 = placeholder_token


def test_unsealed_owner_decision_v11_binding_fails_closed() -> None:
    authority = authority_document()
    authority["owner_authority_binding"]["governing_forward_only_receipt_sha256"] = (
        "__OWNER_DECISION_V1_1_SHA256__"
    )
    with raises(g11c5.GateError, match="UNSEALED_AUTHORITY_PLACEHOLDER"):
        g11c5.validate_authority_document(authority)


def test_precheck_requires_exact_three_workflow_proven_sts_policy_probes() -> None:
    assert g11c5.validate_precheck_sts_policy_probe_count(3) == 3
    for invalid in (None, False, 0, 1, 2, 4):
        with raises(g11c5.GateError, match="STS_POLICY_PROBE|EXACT_BINDING"):
            g11c5.validate_precheck_sts_policy_probe_count(invalid)
    assert g11c5.PRECHECK_STS_PROBE_EFFECTS == {
        **g11c5.ZERO_EFFECTS,
        "aws_calls": 6,
        "sts_calls": 6,
        "sts_assume_role_attempts": 3,
        "sts_sessions_assumed": 3,
        "sts_get_caller_identity_calls": 3,
        "credentials_issued": 3,
    }
    assert [probe["role"] for probe in g11c5.OIDC_STS_POLICY_PACKING_PROBES] == [
        "CHECKPOINT_READ", "RAW_READ", "FINAL_LIST_WRITE",
    ]
    expected_observation_roles = [
        probe["role"] for probe in g11c5.OIDC_STS_POLICY_PACKING_PROBES
    ]
    assert expected_observation_roles == ["CHECKPOINT_READ", "RAW_READ", "FINAL_LIST_WRITE"]


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
