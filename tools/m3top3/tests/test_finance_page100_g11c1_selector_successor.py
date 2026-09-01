from __future__ import annotations

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

import finance_page100_g11c1_selector_successor as g11c1  # noqa: E402


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


def raw_ref() -> g11c1.SealedRawReference:
    return g11c1.SealedRawReference(
        key=(
            "raw/public-data-api/M3TOP3-FINANCE-STOCK-RIGHTS-v1/"
            "_pilot_generation/G11C1/20260901123521/page-5.json"
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
) -> g11c1.HashedSourceRow:
    return g11c1.HashedSourceRow(
        bas_dt=g11c1.SEED_BASE_DATE,
        page_no=page_no,
        page_item_ordinal=page_item_ordinal,
        global_row_ordinal=ordinal,
        custody_key_sha256=custody_hash,
        observed_identity_sha256=identity_hash,
    )


def seeded_state() -> g11c1.ProjectionState:
    return g11c1.ProjectionState(
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
    path = MODULE_DIR / "finance_page100_g11c1_live_adapter.py"
    return {
        "ready": True,
        "path": g11c1.LIVE_ADAPTER_REPO_PATH,
        "sha256": g11c1.sha256_file(path),
        "git_blob": g11c1.git_blob_sha1_file(path),
        "factory_symbol": g11c1.LIVE_ADAPTER_FACTORY_SYMBOL,
        "interface_version": g11c1.LIVE_ADAPTER_INTERFACE_VERSION,
    }


def authority_document() -> dict:
    safe_adapter = safe_adapter_document()
    return {
        "artifact": g11c1.AUTHORITY_SCHEMA,
        "schema_version": 1,
        "generation_timestamp": g11c1.GENERATION_TIMESTAMP,
        "authority_commit": g11c1.AUTHORITY_COMMIT,
        "owner_authority_binding": {
            "commit": g11c1.OWNER_APPROVAL_COMMIT,
            "governing_forward_only_receipt_path": (
                "control/m3top3/public-data-source-admission/v1.0/"
                "M3TOP3_FINANCE_CA_PAGE100_G11_DOWNSTREAM_OWNER_DECISION_RECEIPT_v1.1.json"
            ),
            "governing_forward_only_receipt_commit": g11c1.GOVERNED_CORRECTION_HEAD,
            "governing_forward_only_receipt_git_blob": g11c1.OWNER_DECISION_V1_1_GIT_BLOB,
            "governing_forward_only_receipt_sha256": g11c1.OWNER_DECISION_V1_1_SHA256,
        },
        "fresh_identity": {
            "generation_id": g11c1.GENERATION_ID,
            "runtime_lock_id": g11c1.RUNTIME_LOCK_ID,
            "pilot_run_id": g11c1.PILOT_RUN_ID,
            "precheck_act_id": g11c1.PRECHECK_ACT_ID,
            "live_act_id": g11c1.LIVE_ACT_ID,
            "latch_event_id": g11c1.LATCH_EVENT_ID,
            "owner_cap_spec_sha256": g11c1.OWNER_CAP_SPEC_SHA256,
            "execution_token_sha256": g11c1.EXECUTION_TOKEN_SHA256,
            "identity_reuse_authorized": False,
        },
        "owner_cap_spec": g11c1.expected_owner_cap_spec(),
        "owner_cap_spec_canonicalization": "UTF8_JSON_SORT_KEYS_COMPACT_TRAILING_LF",
        "owner_cap_spec_sha256": g11c1.OWNER_CAP_SPEC_SHA256,
        "execution_token_material": g11c1.expected_execution_token_material(),
        "execution_token_material_canonicalization": "UTF8_JSON_SORT_KEYS_COMPACT_TRAILING_LF",
        "execution_token_sha256": g11c1.EXECUTION_TOKEN_SHA256,
        "authorized_route": {
            "route": (
                "RESUME_PAGE100_RAW_ACQUISITION_FROM_EXACT_G10_CHECKPOINT_"
                "AT_20240131_PAGE_5"
            ),
            "one_fresh_zero_effect_precheck_authorized": True,
            "github_run_attempt_required": 1,
        },
        "sealed_s3_projection_binding": {
            "bas_dt": g11c1.SEED_BASE_DATE,
            "source_rows": 40,
            "eligible_rows": 35,
            "excluded_rows_at_sealed_seed": 5,
            "missing_rows": 0,
            "excluded_global_row_ordinals": [36, 37, 38, 39, 40],
            "sealed_eligible_projection_sha256": g11c1.SEALED_SEED_PROJECTION_SHA256,
            "selector_algorithm": g11c1.SELECTOR_ALGORITHM,
            "selector_custody_key_sha256": g11c1.TARGET_CUSTODY_SHA256,
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
            "g10_checkpoint_sha256": g11c1.PREDECESSOR_CHECKPOINT_SHA256,
            "resume_bas_dt": g11c1.SEED_BASE_DATE,
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
        "adapter_execution_order_binding": g11c1.expected_adapter_execution_order(),
        "live_pre_mutation_order": g11c1.expected_live_pre_mutation_order(),
        "entry_gate": {"live_adapter_gate": g11c1.LIVE_ADAPTER_GATE_READY},
        "safe_executable_adapter": safe_adapter,
        "no_rerun": {
            "consumed_github_runs": list(g11c1.REQUIRED_NO_RERUN_RUNS),
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


def plan_document() -> dict:
    return {
        "artifact": g11c1.PLAN_SCHEMA,
        "schema_version": 1,
        "generation_timestamp": g11c1.GENERATION_TIMESTAMP,
        "authority_commit": g11c1.AUTHORITY_COMMIT,
        "generation_id": g11c1.GENERATION_ID,
        "authority": {"owner_authority_commit": g11c1.OWNER_APPROVAL_COMMIT},
        "identity": {
            "generation_id": g11c1.GENERATION_ID,
            "runtime_lock_id": g11c1.RUNTIME_LOCK_ID,
            "pilot_run_id": g11c1.PILOT_RUN_ID,
            "precheck_act_id": g11c1.PRECHECK_ACT_ID,
            "live_act_id": g11c1.LIVE_ACT_ID,
            "latch_event_id": g11c1.LATCH_EVENT_ID,
            "owner_cap_spec_sha256": g11c1.OWNER_CAP_SPEC_SHA256,
            "execution_token_sha256": g11c1.EXECUTION_TOKEN_SHA256,
        },
        "resume_and_seed_contract": {
            "predecessor_checkpoint_sha256": g11c1.PREDECESSOR_CHECKPOINT_SHA256,
            "start_bas_dt": g11c1.SEED_BASE_DATE,
            "start_page": 5,
        },
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
                    "SEALED_STATIC_GOVERNED_EVIDENCE_VALIDATION_ONLY_"
                    "ZERO_AWS_ZERO_EXTERNAL_EFFECT"
                ),
                "provider_calls": 0,
                "quota_reservations": 0,
                "aws_calls": 0,
                "sts_calls": 0,
                "s3_calls": 0,
                "s3_get_object_version_calls": 0,
                "s3_bucket_metadata_calls": 0,
                "runtime_credential_accesses": 0,
                "raw_writes": 0,
                "s3_put_delete_copy": 0,
                "repository_mutations_by_workflow": 0,
            },
            {
                "phase": "LIVE_READ_ONLY_SEED_VERIFICATION_BEFORE_ANY_MUTATION",
                "actions": g11c1.expected_live_seed_verification_actions(),
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
        "artifact": g11c1.SEED_SCHEMA,
        "schema_version": 1,
        "generation_timestamp": g11c1.GENERATION_TIMESTAMP,
        "authority_commit": g11c1.AUTHORITY_COMMIT,
        "bas_dt": g11c1.SEED_BASE_DATE,
        "next_page": 5,
        "predecessor": {
            "checkpoint_sha256": g11c1.PREDECESSOR_CHECKPOINT_SHA256,
            "validated_raw_pages": [1, 2, 3, 4],
        },
        "projection": {
            "selector_algorithm": g11c1.SELECTOR_ALGORITHM,
            "selector_sha256": g11c1.TARGET_CUSTODY_SHA256,
            "eligible_projection_sha256": g11c1.SEALED_SEED_PROJECTION_SHA256,
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
    assert g11c1.GENERATION_TIMESTAMP == "20260901123521"
    assert g11c1.OWNER_APPROVAL_COMMIT == "884e1fadebda480f4c38d172eab083cbdbf031b2"
    assert g11c1.AUTHORITY_COMMIT == "19a62491c5168ee4c5f8ece31eba7598f11ebbbc"
    assert g11c1.GOVERNED_CORRECTION_HEAD == "19a62491c5168ee4c5f8ece31eba7598f11ebbbc"
    assert g11c1.GOVERNED_CORRECTION_TREE == "572bf2ab23a7d761de8160e6828f8b074618391b"
    assert g11c1.ACTIVATION_BASE_HEAD_COMMIT == "e8b0b93714060627b2fbc124566eb6a5b32cf9d5"
    assert g11c1.ACTIVATION_BASE_TREE == "0d4465091a680c1ac9ad6c7aed3aed8f606f57ea"
    assert g11c1.OWNER_CAP_SPEC_SHA256 == (
        "5eae2419731d045b6dbaa8795a42c430d0efc42b54f897a1618b09c4573ccde2"
    )
    assert g11c1.EXECUTION_TOKEN_SHA256 == (
        "a9bd3a1bfacd0a04e9ab76b80aa4ec3f795258251fdc30b37409ca5a8c56fec6"
    )
    assert g11c1.TARGET_CUSTODY_SHA256 == (
        "f3e7b94dbde722df47cc3bb1a5615068cea42dc1994a91ce92317f5d1fb8b3d6"
    )
    assert g11c1.SEALED_SEED_PROJECTION_SHA256 == (
        "8f6986c9a9839ad62fe856dd0c4d31b54ce1982373deffd1404671c4c9fbfd24"
    )
    assert (g11c1.INHERITED_G10_ACQUISITIONS, g11c1.G11_ACQUISITION_CEILING) == (4, 1696)
    assert (g11c1.INHERITED_G10_ATTEMPTS, g11c1.G11_ATTEMPT_CEILING) == (4, 1996)
    assert g11c1.FIRST_NEW_PAGE == 5
    assert 33272691259 in g11c1.REQUIRED_NO_RERUN_RUNS
    assert 33273146915 in g11c1.REQUIRED_NO_RERUN_RUNS
    assert 33465583987 in g11c1.REQUIRED_NO_RERUN_RUNS
    assert 33466306591 in g11c1.REQUIRED_NO_RERUN_RUNS
    assert list(g11c1.LIVE_PRE_MUTATION_PHASES) == [
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
    first, result = g11c1.project_hashed_rows(rows)
    second, _ = g11c1.project_hashed_rows(rows)
    assert first.eligible_projection_sha256 == second.eligible_projection_sha256
    assert result.source_rows == result.eligible_rows == 2
    assert result.excluded_rows == result.missing_rows == 0
    assert first.source_rows == first.eligible_rows + first.excluded_rows + first.missing_rows


def test_only_sealed_seed_ordinals_36_through_40_can_be_excluded() -> None:
    state = g11c1.ProjectionState(source_rows=35, eligible_rows=35)
    result_state, result = g11c1.project_hashed_rows(
        [row(36, g11c1.TARGET_CUSTODY_SHA256, None, page_no=4, page_item_ordinal=6)],
        state,
        selector_policy=g11c1.SEED_SELECTOR_POLICY,
    )
    assert result.excluded_global_row_ordinals == (36,)
    assert result_state.excluded_rows == 1
    assert g11c1.TARGET_CUSTODY_SHA256 not in result_state.identity_map

    with raises(g11c1.GateError, match="SEALED_SELECTOR_SCOPE_VIOLATION"):
        g11c1.project_hashed_rows(
            [row(1, g11c1.TARGET_CUSTODY_SHA256, None, page_no=1)],
            selector_policy=g11c1.SEED_SELECTOR_POLICY,
        )


def test_future_selector_match_requires_raw_custody_then_stops_pending_owner() -> None:
    original = seeded_state()
    with raises(g11c1.FutureSelectorObservationError) as captured:
        g11c1.project_hashed_rows(
            [row(41, g11c1.TARGET_CUSTODY_SHA256, h("changed identity"))],
            original,
            raw_ref=raw_ref(),
            require_sealed_raw=True,
            selector_policy=g11c1.FUTURE_SELECTOR_POLICY,
        )
    assert captured.value.code == "FUTURE_SELECTOR_OBSERVED_PENDING_OWNER_DECISION"
    # Transactional core returns no advanced state on the terminal observation.
    assert original.source_rows == 40
    assert original.excluded_rows == 5


def test_future_selector_cannot_be_observed_before_raw_seal() -> None:
    with raises(g11c1.GateError, match="RAW_NOT_SEALED"):
        g11c1.project_hashed_rows(
            [row(41, g11c1.TARGET_CUSTODY_SHA256, None)],
            seeded_state(),
            require_sealed_raw=True,
        )


def test_non_target_conflict_and_missing_fields_fail_transactionally_after_raw_seal() -> None:
    original = seeded_state()
    with raises(g11c1.NonTargetIdentityConflictError):
        g11c1.project_hashed_rows(
            [row(41, h("custody-a"), h("identity-b"))],
            original,
            raw_ref=raw_ref(),
            require_sealed_raw=True,
        )
    assert original.source_rows == 40

    with raises(g11c1.MissingCustodyError):
        g11c1.project_hashed_rows(
            [row(41, None, h("identity"))],
            original,
            raw_ref=raw_ref(),
            require_sealed_raw=True,
        )
    with raises(g11c1.MissingIdentityError):
        g11c1.project_hashed_rows(
            [row(41, h("new custody"), None)],
            original,
            raw_ref=raw_ref(),
            require_sealed_raw=True,
        )
    assert original.source_rows == 40


def test_budget_exact_boundaries_and_per_page_attempt_gate() -> None:
    last = g11c1.BudgetState(g11_acquisitions=1695, g11_attempts=1995)
    terminal = last.reserve_attempt(new_unique_acquisition=True, page_attempt=2)
    assert terminal.effective_acquisitions == 1700
    assert terminal.effective_attempts == 2000
    assert terminal.remaining_acquisitions == terminal.remaining_attempts == 0
    with raises(g11c1.GateError, match="ACQUISITION_CEILING"):
        terminal.reserve_attempt(new_unique_acquisition=True, page_attempt=1)
    with raises(g11c1.GateError, match="ATTEMPTS_PER_PAGE_CEILING"):
        g11c1.BudgetState().reserve_attempt(new_unique_acquisition=True, page_attempt=3)


def test_append_only_namespace_guard_rejects_historical_keys() -> None:
    g11c1.validate_g11_object_key(
        "raw/public-data-api/source/G11C1/20260901123521/page-5.json"
    )
    with raises(g11c1.GateError, match="HISTORICAL_NAMESPACE_WRITE_FORBIDDEN"):
        g11c1.validate_g11_object_key(
            "raw/public-data-api/source/G10/G11C1/20260901123521/page-5.json"
        )


def test_sealed_adapter_dynamic_import_registers_dataclass_module_and_factory() -> None:
    adapter_path = MODULE_DIR / "finance_page100_g11c1_live_adapter.py"
    factory = g11c1.load_sealed_live_adapter_factory(
        adapter_path, g11c1.sha256_file(adapter_path)
    )
    assert callable(factory)
    assert factory.__name__ == g11c1.LIVE_ADAPTER_FACTORY_SYMBOL


def test_runtime_live_head_markers_resolve_only_from_exact_github_environment() -> None:
    head = "a" * 40
    tree = "b" * 40
    activation = {
        "activation_binding": {
            "live_activation_commit": g11c1.LIVE_HEAD_MARKER,
            "live_activation_tree": g11c1.LIVE_TREE_MARKER,
            "expected_branch_head_at_dispatch": g11c1.LIVE_HEAD_MARKER,
        }
    }
    observed = g11c1.validate_runtime_live_head_binding(
        activation,
        environment={
            "G11C1_LIVE_HEAD_SHA": head,
            "G11C1_LIVE_HEAD_TREE": tree,
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
    with raises(g11c1.GateError, match="live activation commit marker"):
        g11c1.validate_runtime_live_head_binding(
            embedded,
            environment={
                "G11C1_LIVE_HEAD_SHA": head,
                "G11C1_LIVE_HEAD_TREE": tree,
                "GITHUB_SHA": head,
                "GITHUB_RUN_ID": "123456789",
                "GITHUB_RUN_ATTEMPT": "1",
            },
        )

    with raises(g11c1.GateError, match="GITHUB_SHA"):
        g11c1.validate_runtime_live_head_binding(
            activation,
            environment={
                "G11C1_LIVE_HEAD_SHA": head,
                "G11C1_LIVE_HEAD_TREE": tree,
                "GITHUB_SHA": "c" * 40,
                "GITHUB_RUN_ID": "123456789",
                "GITHUB_RUN_ATTEMPT": "1",
            },
        )


def test_live_result_binds_actual_execution_and_single_terminal_put() -> None:
    execution = {
        "repository": g11c1.REPOSITORY,
        "branch": g11c1.BRANCH,
        "github_run_id": 123456789,
        "github_run_attempt": 1,
        "head_sha": "a" * 40,
        "tree_sha": "b" * 40,
    }

    def object_binding(name: str, *, key: str | None = None) -> dict:
        return {
            "key": key or f"raw/public-data-api/source/G11C1/{g11c1.GENERATION_TIMESTAMP}/{name}.json",
            "version_id": f"version-{name}",
            "etag": f'"etag-{name}"',
            "sha256": h(name),
            "bytes": 100,
            "content_type": "application/json",
            "server_side_encryption": "AES256",
        }

    effects = dict(g11c1.LIVE_ZERO_EFFECTS)
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
        "aws_calls": 20,
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
        "schema": "M3TOP3_FINANCE_CA_PAGE100_G11C1_LIVE_ENTRY_RESULT_v1.0",
        "verdict": "PASS",
        "entry_gate": "LIVE_ENTERED_ONCE",
        "execution_binding": execution,
        "effects": effects,
        "effect_reconciliation": {"complete": True, "ambiguous_side_effects": False},
        "execution_claim_binding": object_binding("claim", key=g11c1.EXECUTION_CLAIM_KEY),
        "checkpoint_binding": object_binding("checkpoint", key=g11c1.G11_CHECKPOINT_KEY),
        "terminal_receipt_binding": {
            "key": g11c1.G11_TERMINAL_RECEIPT_KEY,
            "attempted": True,
            "put_attempts": 1,
            "confirmed": True,
            "object": object_binding("terminal", key=g11c1.G11_TERMINAL_RECEIPT_KEY),
        },
    }
    code, normalized = g11c1._normalize_and_validate_live_result(
        result, 0, expected_execution_binding=execution
    )
    assert code == 0
    assert normalized["terminal_receipt_binding"]["confirmed"] is True

    invalid = dict(result)
    invalid["effects"] = dict(effects)
    invalid["effects"]["terminal_receipt_put_attempts"] = 0
    with raises(g11c1.GateError, match="terminal receipt attempt/write"):
        g11c1._normalize_and_validate_live_result(
            invalid, 0, expected_execution_binding=execution
        )


def test_seed_summary_reuses_sealed_receipts_and_defers_raw_recheck_to_live() -> None:
    assert g11c1.validate_seed_document(seed_document()) == "SEALED_RECEIPT_REUSE"


def test_bundle_hash_bindings_and_precheck_zero_effect_contract() -> None:
    with tempfile.TemporaryDirectory() as temporary_directory:
        tmp_path = Path(temporary_directory)
        authority_path = tmp_path / g11c1.AUTHORITY_FILENAME
        plan_path = tmp_path / g11c1.PLAN_FILENAME
        seed_path = tmp_path / g11c1.SEED_FILENAME
        manifest_path = tmp_path / g11c1.MANIFEST_FILENAME
        test_path = Path(__file__).resolve()
        runner_path = Path(g11c1.__file__).resolve()
        adapter_path = MODULE_DIR / "finance_page100_g11c1_live_adapter.py"

        write_json(authority_path, authority_document())
        write_json(plan_path, plan_document())
        write_json(seed_path, seed_document())
        safe_adapter = safe_adapter_document()

        def binding(path: Path) -> dict:
            return {
                "filename": path.name,
                "sha256": g11c1.sha256_file(path),
                "git_blob": g11c1.git_blob_sha1_file(path),
            }

        manifest = {
            "artifact": g11c1.MANIFEST_SCHEMA,
            "schema_version": 1,
            "generation_timestamp": g11c1.GENERATION_TIMESTAMP,
            "generation_id": g11c1.GENERATION_ID,
            "authority_commit": g11c1.AUTHORITY_COMMIT,
            "preparation_commit_binding": "DEFERRED_TO_ACTIVATION",
            "sealed_scope_summary": {
                "owner_cap_spec_sha256": g11c1.OWNER_CAP_SPEC_SHA256,
                "execution_token_sha256": g11c1.EXECUTION_TOKEN_SHA256,
                "fixed_quota_day_kst": g11c1.QUOTA_DAY_KST,
            },
            "adapter_execution_order_binding": g11c1.expected_adapter_execution_order(),
            "files": {
                "authority": binding(authority_path),
                "plan": binding(plan_path),
                "seed": binding(seed_path),
                "runner": binding(runner_path),
                "tests": binding(test_path),
                "adapter_tests": binding(test_path),
                "live_adapter": {
                    **binding(adapter_path),
                    "path": g11c1.LIVE_ADAPTER_REPO_PATH,
                },
            },
            "live_adapter_gate": g11c1.LIVE_ADAPTER_GATE_READY,
            "live_adapter": {
                "executable": True,
                "sealed": True,
                "ready": True,
                **safe_adapter,
            },
            "safe_executable_adapter": safe_adapter,
        }
        write_json(manifest_path, manifest)

        result = g11c1.validate_bundle(
            authority_path=authority_path,
            plan_path=plan_path,
            seed_path=seed_path,
            manifest_path=manifest_path,
            pytest_path=test_path,
        )
        assert result["first_new_page"] == 5
        assert result["governed_correction_head"] == g11c1.GOVERNED_CORRECTION_HEAD
        assert result["live_adapter_gate"] == g11c1.LIVE_ADAPTER_GATE_READY
        assert all(value == 0 for value in g11c1.ZERO_EFFECTS.values())

        blocked = dict(manifest)
        blocked["live_adapter_gate"] = g11c1.LIVE_ADAPTER_GATE_BLOCKED
        blocked_manifest = tmp_path / ("blocked-" + g11c1.MANIFEST_FILENAME)
        write_json(blocked_manifest, blocked)
        with raises(g11c1.GateError, match="manifest.live_adapter_gate"):
            g11c1.validate_manifest_document(
                blocked,
                authority_path=authority_path,
                plan_path=plan_path,
                seed_path=seed_path,
                runner_path=runner_path,
                pytest_path=test_path,
                live_adapter_path=adapter_path,
            )


def test_unsealed_owner_decision_v11_binding_fails_closed() -> None:
    authority = authority_document()
    authority["owner_authority_binding"]["governing_forward_only_receipt_sha256"] = (
        "__OWNER_DECISION_V1_1_SHA256__"
    )
    with raises(g11c1.GateError, match="UNSEALED_AUTHORITY_PLACEHOLDER"):
        g11c1.validate_authority_document(authority)


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
