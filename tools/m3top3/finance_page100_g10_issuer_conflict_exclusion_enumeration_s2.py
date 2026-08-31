#!/usr/bin/env python3
"""Fresh bounded S2 issuer-group exclusion enumeration.

PRECHECK is offline.  LIVE consumes the pinned credential action's single STS
identity validation and can execute only the four literal, version-qualified
S3 reads sealed below.  The clear entity bodies exist only in process memory
and a mode-0600 temporary directory before they are passed to the already
reviewed pure projection function.  This module never calls a Finance provider,
lists S3, writes custody, runs G10/G11, or durably persists issuer values.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import pathlib
import re
import stat
import subprocess
import sys
import tempfile
from collections.abc import Callable, Mapping, Sequence
from typing import Any

try:
    from . import (
        finance_page100_g10_issuer_conflict_exclusion_enumeration_precheck
        as pure,
    )
except ImportError:  # Direct execution in GitHub Actions.
    import finance_page100_g10_issuer_conflict_exclusion_enumeration_precheck as pure


REPOSITORY = "AofSpds/asset-agent-asa"
BRANCH = "aaa-pmo-public-data-g2-g3-source-admission-v1-20260828"
ACTOR = "AofSpds"
ACCOUNT_ID = "956315449338"
REGION = "ap-northeast-2"
BUCKET = "semi-data-plane-aofspds-20260815"
ROLE_NAME = "M3Top3GitHubOIDCRawWriter"

GENERATION_STAMP = "20260831134500"
GENERATION_ID = "G10-ISSUER-GROUP-EXCLUSION-ENUMERATION-S2-" + GENERATION_STAMP
RUNTIME_LOCK_ID = "PMO-G10-ISSUER-GROUP-EXCLUSION-ENUMERATION-S2-" + GENERATION_STAMP
PRECHECK_ACT_ID = (
    "G10-ISSUER-GROUP-EXCLUSION-ENUMERATION-S2-PRECHECK-" + GENERATION_STAMP
)
LIVE_ACT_ID = "G10-ISSUER-GROUP-EXCLUSION-ENUMERATION-S2-LIVE-" + GENERATION_STAMP

PREDECESSOR_TERMINAL_COMMIT = "83d14411f7b0dc18a3cd6e8f58b0e0659eea98e9"
PREDECESSOR_TERMINAL_TREE = "035d7ba146a4b679e362ceeb9d73242b49089e0b"
PREDECESSOR_TERMINAL_PATH = (
    "control/m3top3/public-data-source-admission/v1.0/"
    "M3TOP3_FINANCE_CA_PAGE100_G10_ISSUER_CONFLICT_EXCLUSION_REMEDIATION_"
    "ENUMERATION_S1_LIVE_TERMINAL_RECEIPT_33397813927_v1.0.json"
)
PREDECESSOR_TERMINAL_BYTES = 5555
PREDECESSOR_TERMINAL_SHA256 = (
    "f204fb27f607a235e69c7e53b1752b55ad9b89e9ce421901c1daebc735b5fb46"
)
PREDECESSOR_TERMINAL_BLOB = "09afa0c51fdba04c7c1b0cdfc372123010c73110"

POLICY_KEY_PREFIX = (
    "raw/public-data-api/"
    "M3TOP3-FINANCE-STOCK-RIGHTS-v1/_pilot_generation/"
    "runtime_lock_id=PMO-FINANCE-PAGE100-G10-20260830044522/"
    "pilot_run_id=FINANCE-PAGE100-PILOT-G10-20260830044522/"
    "getRighExerReasSche_V2/quota_day_kst=2026-08-30"
)
POLICY_RESOURCE_PATTERN = (
    f"arn:aws:s3:::{BUCKET}/{POLICY_KEY_PREFIX}/"
    "request_id=*/attempt=1/sha256=*.entity"
)
EXPECTED_POLICY_BYTES = 601

CONTROL_ROOT = "control/m3top3/public-data-source-admission/v1.0"
AUTHORITY_PATH = (
    f"{CONTROL_ROOT}/M3TOP3_FINANCE_CA_PAGE100_G10_ISSUER_CONFLICT_EXCLUSION_"
    "REMEDIATION_ENUMERATION_S2_AUTHORITY_v1.0.json"
)
MANIFEST_PATH = (
    f"{CONTROL_ROOT}/M3TOP3_FINANCE_CA_PAGE100_G10_ISSUER_CONFLICT_EXCLUSION_"
    "REMEDIATION_ENUMERATION_S2_MANIFEST_v1.0.json"
)
POLICY_PATH = (
    f"{CONTROL_ROOT}/M3TOP3_FINANCE_CA_PAGE100_G10_ISSUER_CONFLICT_EXCLUSION_"
    "REMEDIATION_ENUMERATION_S2_LIVE_SESSION_POLICY_v1.0.json"
)
PRECHECK_ACTIVATION_PATH = (
    f"{CONTROL_ROOT}/M3TOP3_FINANCE_CA_PAGE100_G10_ISSUER_CONFLICT_EXCLUSION_"
    "REMEDIATION_ENUMERATION_S2_PRECHECK_ACTIVATION_v1.0.json"
)
LIVE_ACTIVATION_PATH = (
    f"{CONTROL_ROOT}/M3TOP3_FINANCE_CA_PAGE100_G10_ISSUER_CONFLICT_EXCLUSION_"
    "REMEDIATION_ENUMERATION_S2_LIVE_ACTIVATION_v1.0.json"
)
PRECHECK_PASS_PATH = (
    f"{CONTROL_ROOT}/M3TOP3_FINANCE_CA_PAGE100_G10_ISSUER_CONFLICT_EXCLUSION_"
    "REMEDIATION_ENUMERATION_S2_PRECHECK_PASS_RECEIPT_v1.0.json"
)
PRECHECK_TEMPLATE_PATH = PRECHECK_ACTIVATION_PATH + ".template"
LIVE_TEMPLATE_PATH = LIVE_ACTIVATION_PATH + ".template"
PRECHECK_WORKFLOW_PATH = (
    ".github/workflows/m3top3-finance-page100-g10-issuer-conflict-exclusion-"
    "remediation-enumeration-s2-precheck-v1.yml"
)
LIVE_WORKFLOW_PATH = (
    ".github/workflows/m3top3-finance-page100-g10-issuer-conflict-exclusion-"
    "remediation-enumeration-s2-live-v1.yml"
)
RUNNER_PATH = (
    "tools/m3top3/"
    "finance_page100_g10_issuer_conflict_exclusion_enumeration_s2.py"
)
TEST_PATH = (
    "tools/m3top3/tests/"
    "test_finance_page100_g10_issuer_conflict_exclusion_enumeration_s2.py"
)

PREPARATION_MESSAGE = (
    "Prepare G10 issuer-group exclusion enumeration S2 20260831134500 v1.0"
)
PRECHECK_MESSAGE = (
    "Arm G10 issuer-group exclusion enumeration S2 PRECHECK 20260831134500 v1.0"
)
LIVE_MESSAGE = (
    "Arm G10 issuer-group exclusion enumeration S2 LIVE 20260831134500 v1.0"
)

AUTHORITY_ARTIFACT = (
    "M3TOP3_FINANCE_CA_PAGE100_G10_ISSUER_CONFLICT_EXCLUSION_REMEDIATION_"
    "ENUMERATION_S2_AUTHORITY_v1.0"
)
MANIFEST_ARTIFACT = (
    "M3TOP3_FINANCE_CA_PAGE100_G10_ISSUER_CONFLICT_EXCLUSION_REMEDIATION_"
    "ENUMERATION_S2_MANIFEST_v1.0"
)
PRECHECK_ACTIVATION_ARTIFACT = (
    "M3TOP3_FINANCE_CA_PAGE100_G10_ISSUER_CONFLICT_EXCLUSION_REMEDIATION_"
    "ENUMERATION_S2_PRECHECK_ACTIVATION_v1.0"
)
LIVE_ACTIVATION_ARTIFACT = (
    "M3TOP3_FINANCE_CA_PAGE100_G10_ISSUER_CONFLICT_EXCLUSION_REMEDIATION_"
    "ENUMERATION_S2_LIVE_ACTIVATION_v1.0"
)
PRECHECK_PASS_ARTIFACT = (
    "M3TOP3_FINANCE_CA_PAGE100_G10_ISSUER_CONFLICT_EXCLUSION_REMEDIATION_"
    "ENUMERATION_S2_PRECHECK_PASS_RECEIPT_v1.0"
)

EXPECTED_RAW_VERSIONS = tuple(dict(row) for row in pure.EXPECTED_EXACT_RAW_VERSIONS)
EXPECTED_TOTAL_BYTES = 18_730
EXPECTED_GET_CALLS = 4
EXPECTED_CONTENT_TYPE = "application/octet-stream"
EXPECTED_RAW_METADATA_KEYS = frozenset(
    {
        "sha256",
        "http-status",
        "acquired-at-utc",
        "request-id",
        "bas-dt",
        "page-no",
        "attempt",
        "runtime-lock-id",
        "pilot-run-id",
        "quota-day-kst",
        "provider-call-started-at-utc",
        "socket-opened-at-utc",
        "response-received-at-utc",
        "reservation-checkpoint-revision",
        "reservation-checkpoint-token-sha256",
        "provider-call-checkpoint-revision",
        "provider-call-checkpoint-token-sha256",
        "execution-claim-version-id",
        "execution-claim-content-sha256",
    }
)
HASH_RE = re.compile(r"[0-9a-f]{64}")
COMMIT_RE = re.compile(r"[0-9a-f]{40}")
UTC_RE = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z")

PREPARATION_BOUND_FILES = frozenset(
    {
        AUTHORITY_PATH,
        POLICY_PATH,
        PRECHECK_TEMPLATE_PATH,
        LIVE_TEMPLATE_PATH,
        PRECHECK_WORKFLOW_PATH,
        LIVE_WORKFLOW_PATH,
        RUNNER_PATH,
        TEST_PATH,
    }
)

ZERO_PROHIBITED_EFFECTS = {
    "company_master_or_universe_mutations": 0,
    "finance_provider_api_calls": 0,
    "g10_or_g11_runs": 0,
    "github_actions_artifacts_uploaded": 0,
    "normalization_pit_promotion_release_production_actions": 0,
    "provider_quota_reservations": 0,
    "remote_custody_mutations": 0,
    "repository_mutations": 0,
    "s3_copy_object_calls": 0,
    "s3_delete_object_calls": 0,
    "s3_get_bucket_location_calls": 0,
    "s3_get_bucket_versioning_calls": 0,
    "s3_get_object_calls_without_version": 0,
    "s3_head_object_calls": 0,
    "s3_list_object_versions_calls": 0,
    "s3_list_objects_calls": 0,
    "s3_put_object_calls": 0,
}

EXPECTED_PRECHECK_EFFECTS = {
    **ZERO_PROHIBITED_EFFECTS,
    "aws_or_s3_calls": 0,
    "oidc_assume_role_with_web_identity_calls": 0,
    "raw_bytes": 0,
    "remote_mutations": 0,
    "s3_get_object_version_calls": 0,
    "sts_get_caller_identity_calls": 0,
}

EXPECTED_CALL_CEILING = {
    "finance_provider_api_calls": 0,
    "g10_or_g11_runs": 0,
    "oidc_assume_role_with_web_identity_calls": 1,
    "provider_quota_reservations": 0,
    "raw_bytes": EXPECTED_TOTAL_BYTES,
    "s3_copy_object_calls": 0,
    "s3_delete_object_calls": 0,
    "s3_get_bucket_location_calls": 0,
    "s3_get_bucket_versioning_calls": 0,
    "s3_get_object_calls_without_version": 0,
    "s3_get_object_version_calls": EXPECTED_GET_CALLS,
    "s3_head_object_calls": 0,
    "s3_list_object_versions_calls": 0,
    "s3_list_objects_calls": 0,
    "s3_put_object_calls": 0,
    "sts_get_caller_identity_calls": 1,
}

CLEAR_IDENTITY_KEYS = frozenset(
    {
        "issuCmpyKsdCustNo",
        "issuCmpyNm",
        "stckIssuCmpyNm",
        "issucoCustno",
        "issucoNm",
        "corpNm",
        "crno",
        "isinCd",
        "itmsNm",
        "shortIsin",
    }
)


class S2EnumerationError(RuntimeError):
    """A stable fail-closed code; messages never include source values."""


def require(condition: bool, code: str) -> None:
    if not condition:
        raise S2EnumerationError(code)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def git_blob_sha_bytes(value: bytes) -> str:
    header = f"blob {len(value)}\0".encode("ascii")
    return hashlib.sha1(header + value).hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def load_canonical_json(path: pathlib.Path) -> dict[str, Any]:
    require(path.is_file() and not path.is_symlink(), "JSON_FILE_NOT_REGULAR")
    raw = path.read_bytes()
    try:
        value = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise S2EnumerationError("JSON_PARSE_INVALID") from exc
    require(isinstance(value, dict), "JSON_ROOT_NOT_OBJECT")
    require(raw == canonical_json_bytes(value), "JSON_NOT_CANONICAL_LF")
    return value


def file_binding(path: pathlib.Path) -> dict[str, Any]:
    raw = path.read_bytes()
    return {
        "bytes": len(raw),
        "git_blob_sha": git_blob_sha_bytes(raw),
        "sha256": sha256_bytes(raw),
    }


def _strict_uint(value: Any, code: str, expected: int | None = None) -> int:
    require(type(value) is int and value >= 0, code)
    if expected is not None:
        require(value == expected, code)
    return value


def _real_utc_timestamp(value: Any, code: str) -> dt.datetime:
    require(isinstance(value, str) and bool(UTC_RE.fullmatch(value)), code)
    try:
        parsed = dt.datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=dt.timezone.utc
        )
    except ValueError as exc:
        raise S2EnumerationError(code) from exc
    return parsed


def _contains_clear_identity_key(value: Any) -> bool:
    if isinstance(value, Mapping):
        if any(str(key) in CLEAR_IDENTITY_KEYS for key in value):
            return True
        return any(_contains_clear_identity_key(child) for child in value.values())
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return any(_contains_clear_identity_key(child) for child in value)
    return False


def _binding_matches(root: pathlib.Path, binding: Mapping[str, Any]) -> bool:
    required = {"bytes", "git_blob_sha", "path", "sha256"}
    if not required.issubset(set(binding)) or not isinstance(binding.get("path"), str):
        return False
    path = root / str(binding["path"])
    if not path.is_file() or path.is_symlink():
        return False
    expected = {key: binding[key] for key in ("bytes", "git_blob_sha", "sha256")}
    return file_binding(path) == expected


def validate_predecessor_terminal(root: pathlib.Path) -> dict[str, Any]:
    path = root / PREDECESSOR_TERMINAL_PATH
    require(
        file_binding(path)
        == {
            "bytes": PREDECESSOR_TERMINAL_BYTES,
            "git_blob_sha": PREDECESSOR_TERMINAL_BLOB,
            "sha256": PREDECESSOR_TERMINAL_SHA256,
        },
        "PREDECESSOR_TERMINAL_FILE_BINDING_MISMATCH",
    )
    receipt = load_canonical_json(path)
    require(
        receipt.get("state")
        == "TERMINAL_CONTROL_FAILURE_SINGLE_LIVE_ATTEMPT_CONSUMED_FRESH_SUCCESSOR_AUTHORIZED",
        "PREDECESSOR_TERMINAL_STATE_INVALID",
    )
    checkpoint = receipt.get("terminal_checkpoint")
    classification = (
        checkpoint.get("classification") if isinstance(checkpoint, Mapping) else None
    )
    require(
        isinstance(checkpoint, Mapping)
        and checkpoint.get("exact_code")
        == "STS_PACKED_POLICY_TOO_LARGE_171_PERCENT_BEFORE_CREDENTIAL_ISSUANCE"
        and checkpoint.get("failure_phase") == "AWS_OIDC_SESSION_ESTABLISHMENT"
        and checkpoint.get("credentials_issued") is False
        and checkpoint.get("exact_enumeration_completed") is False
        and checkpoint.get("raw_body_or_clear_issuer_value_observed") is False
        and checkpoint.get("retry_or_rerun_authorized") is False
        and checkpoint.get("step_number") == 6
        and isinstance(classification, Mapping)
        and all(
            classification.get(key) is True
            for key in (
                "automatic_successor_eligible",
                "control_only_failure",
                "custody_neutral",
                "quota_neutral",
                "semantic_neutral",
            )
        )
        and classification.get("data_plane_read_effect_present") is False
        and classification.get("nonzero_auth_attempt_effect_present") is True,
        "PREDECESSOR_DEFECT_CLASSIFICATION_INVALID",
    )
    require(
        receipt.get("effect_classification")
        == {
            "aws_or_s3_calls": 1,
            "aws_read_only_session_established": 0,
            "company_master_or_universe_mutations": 0,
            "credentials_issued": 0,
            "finance_provider_api_calls": 0,
            "g10_or_g11_runs": 0,
            "github_actions_artifacts_uploaded": 0,
            "normalization_pit_promotion_release_production_actions": 0,
            "oidc_token_request_attempts": 1,
            "provider_quota_reservations": 0,
            "raw_bytes": 0,
            "remote_custody_mutations": 0,
            "remote_mutations": 0,
            "repository_mutations_by_workflow": 0,
            "runner_aws_cli_calls": 0,
            "s3_copy_object_calls": 0,
            "s3_delete_object_calls": 0,
            "s3_get_bucket_location_calls": 0,
            "s3_get_bucket_versioning_calls": 0,
            "s3_get_object_calls_without_version": 0,
            "s3_get_object_version_calls": 0,
            "s3_head_object_calls": 0,
            "s3_list_object_versions_calls": 0,
            "s3_list_objects_calls": 0,
            "s3_put_object_calls": 0,
            "sts_assume_role_with_web_identity_attempts": 1,
            "sts_get_caller_identity_calls": 0,
        },
        "PREDECESSOR_EFFECTS_NOT_EXACT",
    )
    disposition = receipt.get("disposition")
    require(
        isinstance(disposition, Mapping)
        and disposition.get("automatic_fresh_successor_authorized") is True
        and disposition.get("owner_action_required_before_fresh_successor") is False
        and disposition.get("same_activation_reuse_authorized") is False
        and disposition.get("same_run_retry_authorized") is False,
        "PREDECESSOR_DISPOSITION_INVALID",
    )
    standing = receipt.get("owner_standing_direction")
    require(
        isinstance(standing, Mapping)
        and standing.get("issue_number") == 49
        and standing.get("comment_id") == 5464265547
        and standing.get("automatic_control_successor_authorized") is True
        and standing.get("semantics")
        == "SEMANTIC_NEUTRAL_QUOTA_NEUTRAL_CUSTODY_NEUTRAL_CONTROL_CORRECTION",
        "OWNER_STANDING_DIRECTION_BINDING_INVALID",
    )
    workflow = receipt.get("workflow")
    require(
        isinstance(workflow, Mapping)
        and workflow.get("actor") == ACTOR
        and workflow.get("triggering_actor") == ACTOR
        and workflow.get("event") == "push"
        and workflow.get("head_sha") == "0d1e7734809e303d8b48b7a9d45091af23e32c97"
        and workflow.get("run_id") == 33397813927
        and workflow.get("run_attempt") == 1
        and workflow.get("job_id") == 99506464647
        and workflow.get("conclusion") == "failure"
        and workflow.get("artifacts") == 0
        and workflow.get("workflow_path")
        == ".github/workflows/m3top3-finance-page100-g10-issuer-conflict-"
        "exclusion-remediation-enumeration-s1-live-v1.yml",
        "PREDECESSOR_WORKFLOW_BINDING_INVALID",
    )
    require(not _contains_clear_identity_key(receipt), "CLEAR_IDENTITY_KEY_IN_PREDECESSOR")
    return receipt


def expected_policy() -> dict[str, Any]:
    version_ids = [str(row["version_id"]) for row in EXPECTED_RAW_VERSIONS]
    return {
        "Statement": [
            {
                "Action": "s3:GetObjectVersion",
                "Condition": {"StringEquals": {"s3:VersionId": version_ids}},
                "Effect": "Allow",
                "Resource": POLICY_RESOURCE_PATTERN,
            }
        ],
        "Version": "2012-10-17",
    }


def validate_policy(policy: Mapping[str, Any]) -> None:
    require(dict(policy) == expected_policy(), "LIVE_SESSION_POLICY_NOT_EXACT")
    encoded = canonical_json_bytes(policy)
    require(len(encoded) == EXPECTED_POLICY_BYTES, "LIVE_SESSION_POLICY_SIZE_NOT_EXACT")
    key_pattern = re.compile(
        re.escape(POLICY_KEY_PREFIX)
        + r"/request_id=[0-9a-f]{64}/attempt=1/sha256=[0-9a-f]{64}\.entity"
    )
    require(
        len(EXPECTED_RAW_VERSIONS) == EXPECTED_GET_CALLS
        and len({row["version_id"] for row in EXPECTED_RAW_VERSIONS})
        == EXPECTED_GET_CALLS
        and all(
            bool(key_pattern.fullmatch(str(row["s3_object_key"])))
            and str(row["s3_object_key"]).endswith(
                f"/sha256={row['sha256']}.entity"
            )
            for row in EXPECTED_RAW_VERSIONS
        ),
        "SEALED_RAW_VECTOR_NOT_COVERED_BY_COMPACT_POLICY_PATTERN",
    )


def _validate_effect_ceilings(authority: Mapping[str, Any]) -> None:
    scope = authority.get("exact_read_scope")
    require(isinstance(scope, Mapping), "EXACT_READ_SCOPE_MISSING")
    require(
        scope.get("account_id") == ACCOUNT_ID
        and scope.get("region") == REGION
        and scope.get("bucket") == BUCKET
        and scope.get("role_arn")
        == f"arn:aws:iam::{ACCOUNT_ID}:role/{ROLE_NAME}"
        and scope.get("total_raw_bytes") == EXPECTED_TOTAL_BYTES,
        "AWS_IDENTITY_SCOPE_INVALID",
    )
    require(
        scope.get("exact_raw_versions") == list(EXPECTED_RAW_VERSIONS),
        "EXACT_RAW_VERSION_VECTOR_MISMATCH",
    )
    policy_control = scope.get("session_policy_control")
    require(
        isinstance(policy_control, Mapping)
        and policy_control
        == {
            "canonical_bytes": EXPECTED_POLICY_BYTES,
            "exact_pair_enforcement": "SEALED_RUNNER_ORDERED_FOUR_KEY_VERSION_PAIRS",
            "iam_pair_binding_semantics": "RESOURCE_PATTERN_X_EXACT_VERSION_ALLOWLIST",
            "managed_session_policies": [],
            "predecessor_packed_policy_size_percent": 171,
            "resource_pattern": POLICY_RESOURCE_PATTERN,
            "session_tags": [],
            "version_id_allowlist": [
                str(row["version_id"]) for row in EXPECTED_RAW_VERSIONS
            ],
        },
        "SESSION_POLICY_CONTROL_NOT_EXACT",
    )
    ceilings = scope.get("call_ceiling")
    require(isinstance(ceilings, Mapping), "CALL_CEILING_MISSING")
    require(dict(ceilings) == EXPECTED_CALL_CEILING, "CALL_CEILING_NOT_EXACT")
    authorized = authority.get("authorized_effects")
    require(isinstance(authorized, Mapping), "AUTHORIZED_EFFECTS_MISSING")
    require(
        authorized.get("precheck")
        == {
            "aws_or_s3_calls": 0,
            "finance_provider_api_calls": 0,
            "g10_or_g11_runs": 0,
            "github_actions_artifacts_uploaded": 0,
            "normalization_pit_promotion_release_production": 0,
            "provider_quota_reservations": 0,
            "remote_mutations": 0,
            "sts_calls": 0,
        }
        and authorized.get("live")
        == {
            "finance_provider_api_calls": 0,
            "g10_or_g11_runs": 0,
            "github_actions_artifacts_uploaded": 0,
            "normalization_pit_promotion_release_production": 0,
            "oidc_assume_role_with_web_identity_calls": 1,
            "provider_quota_reservations": 0,
            "raw_bytes_read": EXPECTED_TOTAL_BYTES,
            "remote_custody_mutations": 0,
            "repository_mutations": 0,
            "s3_get_object_version_calls": EXPECTED_GET_CALLS,
            "s3_mutation_calls": 0,
            "sts_get_caller_identity_calls": 1,
        },
        "AUTHORIZED_EFFECTS_NOT_EXACT",
    )


def validate_authority(root: pathlib.Path, authority: Mapping[str, Any]) -> None:
    require(
        authority.get("artifact") == AUTHORITY_ARTIFACT
        and authority.get("state")
        == "OWNER_STANDING_AUTHORIZED_FRESH_BOUNDED_READ_ONLY_ENUMERATION_SUCCESSOR_S2"
        and authority.get("repository") == REPOSITORY
        and authority.get("branch") == BRANCH,
        "AUTHORITY_IDENTITY_INVALID",
    )
    predecessor = authority.get("predecessor_terminal_binding")
    require(
        predecessor
        == {
            "bytes": PREDECESSOR_TERMINAL_BYTES,
            "commit_sha": PREDECESSOR_TERMINAL_COMMIT,
            "git_blob_sha": PREDECESSOR_TERMINAL_BLOB,
            "path": PREDECESSOR_TERMINAL_PATH,
            "sha256": PREDECESSOR_TERMINAL_SHA256,
            "tree_sha": PREDECESSOR_TERMINAL_TREE,
        },
        "AUTHORITY_PREDECESSOR_BINDING_INVALID",
    )
    validate_predecessor_terminal(root)
    successor = authority.get("successor_identity")
    require(
        isinstance(successor, Mapping)
        and successor.get("generation_id") == GENERATION_ID
        and successor.get("runtime_lock_id") == RUNTIME_LOCK_ID
        and successor.get("precheck_act_id") == PRECHECK_ACT_ID
        and successor.get("live_act_id") == LIVE_ACT_ID
        and successor.get("prior_s1_precheck_or_pass_reused") is False
        and successor.get("prior_s1_authority_or_session_reused") is False
        and successor.get("prior_s1_activation_or_latch_reused") is False,
        "FRESH_SUCCESSOR_IDENTITY_INVALID",
    )
    selector = authority.get("selector")
    require(
        isinstance(selector, Mapping)
        and selector.get("algorithm") == "SHA256_OF_UTF8_ISSUCMPY_KSD_CUSTNO"
        and selector.get("custody_key_sha256") == pure.TARGET_CUSTODY_KEY_SHA256
        and selector.get("frozen_identity_sha256") == pure.FROZEN_IDENTITY_SHA256
        and selector.get("observed_identity_sha256") == pure.OBSERVED_IDENTITY_SHA256
        and selector.get("scope")
        == "CURRENT_FROZEN_FINANCE_PAGE100_G10_40_ROW_SLICE_ONLY",
        "SELECTOR_BINDING_INVALID",
    )
    baseline = authority.get("baseline_identity_projection")
    require(
        isinstance(baseline, Mapping)
        and baseline.get("count") == 12
        and baseline.get("projection_sha256")
        == pure.EXPECTED_BASELINE_PROJECTION_SHA256
        and isinstance(baseline.get("identity_hashes_by_custody_sha256"), Mapping)
        and len(baseline["identity_hashes_by_custody_sha256"]) == 12,
        "BASELINE_PROJECTION_BINDING_INVALID",
    )
    require(
        sha256_bytes(
            canonical_json_bytes(
                dict(sorted(baseline["identity_hashes_by_custody_sha256"].items()))
            )
        )
        == pure.EXPECTED_BASELINE_PROJECTION_SHA256,
        "BASELINE_PROJECTION_DIGEST_MISMATCH",
    )
    _validate_effect_ceilings(authority)
    claim = authority.get("claim_ceiling")
    require(
        isinstance(claim, Mapping)
        and claim.get("issuer_identity_resolution") is False
        and claim.get("normalization_pit_promotion_release_production") is False
        and claim.get("gate_effect") == "NONE",
        "CLAIM_CEILING_INVALID",
    )
    prohibitions = authority.get("prohibitions")
    require(
        isinstance(prohibitions, Mapping)
        and all(value is True for value in prohibitions.values()),
        "PROHIBITION_SET_INVALID",
    )
    builder = authority.get("execution_bindings", {}).get("pure_projection_builder")
    require(
        isinstance(builder, Mapping)
        and builder.get("path") == pure.RUNNER_PATH
        and builder.get("function") == "build_hash_only_exclusion_projection"
        and set(builder)
        == {"bytes", "function", "git_blob_sha", "path", "sha256"}
        and file_binding(root / str(builder["path"]))
        == {key: builder[key] for key in ("bytes", "git_blob_sha", "sha256")},
        "PURE_PROJECTION_BUILDER_BINDING_INVALID",
    )
    live_policy = authority.get("execution_bindings", {}).get("live_session_policy")
    require(
        isinstance(live_policy, Mapping)
        and live_policy.get("path") == POLICY_PATH
        and set(live_policy) == {"bytes", "git_blob_sha", "path", "sha256"}
        and _binding_matches(root, live_policy),
        "LIVE_SESSION_POLICY_BINDING_INVALID",
    )
    require(not _contains_clear_identity_key(authority), "CLEAR_IDENTITY_KEY_IN_AUTHORITY")


def validate_manifest(
    root: pathlib.Path,
    manifest: Mapping[str, Any],
) -> None:
    require(
        manifest.get("artifact") == MANIFEST_ARTIFACT
        and manifest.get("state") == "IMMUTABLE_S2_PREPARATION_MANIFEST"
        and manifest.get("preparation_commit_message") == PREPARATION_MESSAGE
        and manifest.get("preparation_parent_head_sha") == PREDECESSOR_TERMINAL_COMMIT
        and manifest.get("preparation_parent_tree_sha") == PREDECESSOR_TERMINAL_TREE,
        "MANIFEST_IDENTITY_OR_PARENT_INVALID",
    )
    files = manifest.get("preparation_files")
    require(
        isinstance(files, Mapping) and set(files) == set(PREPARATION_BOUND_FILES),
        "MANIFEST_FILE_SET_INVALID",
    )
    for relative, binding in files.items():
        require(
            isinstance(binding, Mapping)
            and set(binding) == {"bytes", "git_blob_sha", "sha256"},
            "MANIFEST_FILE_BINDING_SCHEMA_INVALID",
        )
        require(
            file_binding(root / relative) == dict(binding),
            "MANIFEST_FILE_BINDING_MISMATCH",
        )


def validate_event_lineage(
    mode: str,
    activation: Mapping[str, Any],
    expected_preparation_commit: str,
) -> None:
    required = {
        "EVENT_ACTOR",
        "EVENT_TRIGGERING_ACTOR",
        "EVENT_REPOSITORY",
        "EVENT_REF",
        "EVENT_BEFORE",
        "EVENT_AFTER",
        "EVENT_FORCED",
        "EVENT_HEAD_MESSAGE",
        "EVENT_RUN_ATTEMPT",
    }
    require(all(name in os.environ for name in required), "EVENT_LINEAGE_ENV_MISSING")
    expected_message = PRECHECK_MESSAGE if mode == "PRECHECK" else LIVE_MESSAGE
    expected_before = expected_preparation_commit
    if mode == "LIVE":
        binding = activation.get("precheck_pass_binding")
        require(isinstance(binding, Mapping), "LIVE_PRECHECK_PASS_BINDING_MISSING")
        expected_before = str(binding.get("commit_sha") or "")
    require(
        os.environ["EVENT_ACTOR"] == ACTOR
        and os.environ["EVENT_TRIGGERING_ACTOR"] == ACTOR
        and os.environ["EVENT_REPOSITORY"] == REPOSITORY
        and os.environ["EVENT_REF"] == f"refs/heads/{BRANCH}"
        and os.environ["EVENT_BEFORE"] == expected_before
        and bool(COMMIT_RE.fullmatch(os.environ["EVENT_AFTER"]))
        and os.environ["EVENT_FORCED"] == "false"
        and os.environ["EVENT_HEAD_MESSAGE"] == expected_message
        and os.environ["EVENT_RUN_ATTEMPT"] == "1",
        "EVENT_LINEAGE_MISMATCH",
    )


def validate_activation(
    mode: str,
    activation: Mapping[str, Any],
    authority_bytes: bytes,
    manifest_bytes: bytes,
    policy_bytes: bytes,
    expected_preparation_commit: str,
    expected_preparation_tree: str,
    *,
    now: dt.datetime | None = None,
) -> None:
    require(bool(COMMIT_RE.fullmatch(expected_preparation_commit)), "PREP_COMMIT_INVALID")
    require(bool(COMMIT_RE.fullmatch(expected_preparation_tree)), "PREP_TREE_INVALID")
    artifact = (
        PRECHECK_ACTIVATION_ARTIFACT if mode == "PRECHECK" else LIVE_ACTIVATION_ARTIFACT
    )
    state = (
        "ARMED_FRESH_ZERO_EXTERNAL_EFFECT_S2_PRECHECK_ONCE"
        if mode == "PRECHECK"
        else "ARMED_FRESH_EXACT_FOUR_VERSION_READ_ONLY_ENUMERATION_ONCE"
    )
    message = PRECHECK_MESSAGE if mode == "PRECHECK" else LIVE_MESSAGE
    act_id = PRECHECK_ACT_ID if mode == "PRECHECK" else LIVE_ACT_ID
    expected_keys = {
        "activated_at_utc",
        "activation_id",
        "armed",
        "artifact",
        "authority_sha256",
        "branch",
        "expected_commit_message",
        "fresh_runtime_and_latch",
        "manifest_sha256",
        "policy_sha256",
        "preparation_commit_sha",
        "preparation_parent",
        "preparation_tree_sha",
        "repository",
        "state",
    }
    if mode == "LIVE":
        expected_keys.add("precheck_pass_binding")
    require(
        set(activation) == expected_keys
        and activation.get("artifact") == artifact
        and activation.get("state") == state
        and activation.get("armed") is True
        and activation.get("repository") == REPOSITORY
        and activation.get("branch") == BRANCH
        and activation.get("expected_commit_message") == message
        and isinstance(activation.get("activation_id"), str),
        "ACTIVATION_IDENTITY_INVALID",
    )
    activated = _real_utc_timestamp(
        activation.get("activated_at_utc"), "ACTIVATION_TIMESTAMP_INVALID"
    )
    clock = now or dt.datetime.now(dt.timezone.utc)
    require(
        -dt.timedelta(minutes=5) <= clock - activated <= dt.timedelta(hours=24),
        "ACTIVATION_NOT_FRESH",
    )
    require(
        activation.get("preparation_commit_sha") == expected_preparation_commit
        and activation.get("preparation_tree_sha") == expected_preparation_tree
        and activation.get("authority_sha256") == sha256_bytes(authority_bytes)
        and activation.get("manifest_sha256") == sha256_bytes(manifest_bytes)
        and activation.get("policy_sha256") == sha256_bytes(policy_bytes),
        "ACTIVATION_IMMUTABLE_BINDING_MISMATCH",
    )
    timestamp_compact = activated.strftime("%Y%m%d%H%M%S")
    expected_activation_prefix = (
        "G10-ISSUER-GROUP-EXCLUSION-ENUMERATION-S2-PRECHECK-ACTIVATION-"
        if mode == "PRECHECK"
        else "G10-ISSUER-GROUP-EXCLUSION-ENUMERATION-S2-LIVE-ACTIVATION-"
    )
    require(
        activation["activation_id"] == expected_activation_prefix + timestamp_compact,
        "ACTIVATION_ID_TIMESTAMP_LINK_INVALID",
    )
    require(
        activation.get("preparation_parent")
        == {
            "terminal_commit_sha": PREDECESSOR_TERMINAL_COMMIT,
            "terminal_tree_sha": PREDECESSOR_TERMINAL_TREE,
        },
        "ACTIVATION_PREPARATION_PARENT_INVALID",
    )
    fresh = activation.get("fresh_runtime_and_latch")
    common_fresh = {
        "generation_id": GENERATION_ID,
        "precheck_attempt_ordinal": 1,
        "prior_s1_precheck_or_pass_reused": False,
        "prior_s1_authority_or_session_reused": False,
        "prior_s1_activation_or_latch_reused": False,
        "runtime_lock_id": RUNTIME_LOCK_ID,
    }
    if mode == "PRECHECK":
        require(
            isinstance(fresh, Mapping)
            and type(fresh.get("precheck_attempt_ordinal")) is int
            and dict(fresh) == common_fresh,
            "ACTIVATION_FRESH_RUNTIME_INVALID",
        )
    else:
        expected_live_fresh = {**common_fresh, "live_attempt_ordinal": 1}
        require(
            isinstance(fresh, Mapping)
            and type(fresh.get("precheck_attempt_ordinal")) is int
            and type(fresh.get("live_attempt_ordinal")) is int
            and dict(fresh) == expected_live_fresh,
            "ACTIVATION_FRESH_RUNTIME_INVALID",
        )
    require(not _contains_clear_identity_key(activation), "CLEAR_IDENTITY_KEY_IN_ACTIVATION")


def validate_precheck_pass(
    root: pathlib.Path,
    receipt: Mapping[str, Any],
    activation: Mapping[str, Any],
    authority_bytes: bytes,
    manifest_bytes: bytes,
    policy_bytes: bytes,
    expected_preparation_commit: str,
    expected_preparation_tree: str,
) -> None:
    binding = activation.get("precheck_pass_binding")
    require(isinstance(binding, Mapping), "PRECHECK_PASS_BINDING_MISSING")
    require(
        set(binding)
        == {"bytes", "commit_sha", "git_blob_sha", "path", "sha256", "tree_sha"}
        and binding.get("path") == PRECHECK_PASS_PATH
        and bool(COMMIT_RE.fullmatch(str(binding.get("commit_sha") or "")))
        and bool(COMMIT_RE.fullmatch(str(binding.get("tree_sha") or "")))
        and _binding_matches(root, binding),
        "PRECHECK_PASS_FILE_BINDING_INVALID",
    )
    require(
        set(receipt)
        == {
            "activation_binding",
            "artifact",
            "branch",
            "effects",
            "exact_enumeration_started",
            "generation_id",
            "preparation",
            "repository",
            "state",
            "workflow",
        },
        "PRECHECK_PASS_RECEIPT_SCHEMA_INVALID",
    )
    precheck_binding = receipt.get("activation_binding")
    require(
        isinstance(precheck_binding, Mapping)
        and set(precheck_binding)
        == {"bytes", "commit_sha", "git_blob_sha", "path", "sha256", "tree_sha"}
        and precheck_binding.get("path") == PRECHECK_ACTIVATION_PATH
        and bool(COMMIT_RE.fullmatch(str(precheck_binding.get("commit_sha") or "")))
        and bool(COMMIT_RE.fullmatch(str(precheck_binding.get("tree_sha") or "")))
        and _binding_matches(root, precheck_binding),
        "PRECHECK_ACTIVATION_RECEIPT_BINDING_INVALID",
    )
    precheck_activation = load_canonical_json(root / PRECHECK_ACTIVATION_PATH)
    validate_activation(
        "PRECHECK",
        precheck_activation,
        authority_bytes,
        manifest_bytes,
        policy_bytes,
        expected_preparation_commit,
        expected_preparation_tree,
    )
    require(
        receipt.get("artifact") == PRECHECK_PASS_ARTIFACT
        and receipt.get("state") == "PASS_FRESH_BOUNDED_S2_PRECHECK_LIVE_NOT_STARTED"
        and receipt.get("repository") == REPOSITORY
        and receipt.get("branch") == BRANCH
        and receipt.get("generation_id") == GENERATION_ID
        and receipt.get("preparation")
        == {
            "head_sha": expected_preparation_commit,
            "tree_sha": expected_preparation_tree,
        },
        "PRECHECK_PASS_RECEIPT_IDENTITY_INVALID",
    )
    effects = receipt.get("effects")
    require(
        isinstance(effects, Mapping)
        and dict(effects) == EXPECTED_PRECHECK_EFFECTS
        and receipt.get("exact_enumeration_started") is False,
        "PRECHECK_PASS_EFFECTS_NOT_ZERO",
    )
    workflow = receipt.get("workflow")
    require(
        isinstance(workflow, Mapping)
        and set(workflow)
        == {
            "actor",
            "completed_at_utc",
            "conclusion",
            "event",
            "head_sha",
            "job_id",
            "path",
            "run_attempt",
            "run_id",
            "triggering_actor",
            "url",
        }
        and workflow.get("actor") == ACTOR
        and workflow.get("conclusion") == "success"
        and workflow.get("event") == "push"
        and workflow.get("head_sha") == precheck_binding.get("commit_sha")
        and workflow.get("path") == PRECHECK_WORKFLOW_PATH
        and workflow.get("run_attempt") == 1
        and type(workflow.get("run_id")) is int
        and workflow["run_id"] > 0
        and type(workflow.get("job_id")) is int
        and workflow["job_id"] > 0
        and workflow.get("triggering_actor") == ACTOR
        and workflow.get("url")
        == f"https://github.com/{REPOSITORY}/actions/runs/{workflow['run_id']}",
        "PRECHECK_PASS_WORKFLOW_INVALID",
    )
    completed = _real_utc_timestamp(
        workflow.get("completed_at_utc"), "PRECHECK_PASS_COMPLETED_AT_INVALID"
    )
    clock = dt.datetime.now(dt.timezone.utc)
    require(
        -dt.timedelta(minutes=5) <= clock - completed <= dt.timedelta(hours=24),
        "PRECHECK_PASS_NOT_FRESH",
    )
    require(not _contains_clear_identity_key(receipt), "CLEAR_IDENTITY_KEY_IN_PRECHECK_PASS")


RunCallable = Callable[..., subprocess.CompletedProcess[bytes]]


class ExactAwsCli:
    """Four ordered reads after the pinned action's account validation."""

    def __init__(
        self,
        run: RunCallable = subprocess.run,
        *,
        configured_account_id: str | None = None,
    ) -> None:
        self._run = run
        self.configured_account_id = configured_account_id
        self.identity_validated = False
        self.call_counts = {"s3api:get-object": 0}
        self.attempted_pairs: list[tuple[str, str]] = []

    @staticmethod
    def _environment() -> dict[str, str]:
        return {
            **os.environ,
            "AWS_DEFAULT_REGION": REGION,
            "AWS_EC2_METADATA_DISABLED": "true",
            "AWS_MAX_ATTEMPTS": "1",
            "AWS_PAGER": "",
            "AWS_REGION": REGION,
            "AWS_RETRY_MODE": "standard",
        }

    def _invoke(self, name: str, args: Sequence[str]) -> dict[str, Any]:
        require(name in self.call_counts, "AWS_OPERATION_NOT_ALLOWLISTED")
        require(self.call_counts[name] < EXPECTED_GET_CALLS, "AWS_CALL_BUDGET_EXCEEDED")
        self.call_counts[name] += 1
        result = self._run(
            ["aws", *args],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=self._environment(),
            shell=False,
        )
        require(result.returncode == 0, "AWS_CLI_CALL_FAILED")
        try:
            value = json.loads(result.stdout)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise S2EnumerationError("AWS_JSON_INVALID") from exc
        require(isinstance(value, dict), "AWS_JSON_ROOT_INVALID")
        return value

    def validate_configured_identity(self) -> None:
        require(
            self.call_counts == {"s3api:get-object": 0}
            and self.configured_account_id == ACCOUNT_ID,
            "CONFIGURED_AWS_ACCOUNT_ID_INVALID",
        )
        self.identity_validated = True

    def read_exact(self, ordinal: int, destination: pathlib.Path) -> bytes:
        require(1 <= ordinal <= EXPECTED_GET_CALLS, "RAW_READ_ORDINAL_INVALID")
        require(self.identity_validated, "ACTION_IDENTITY_NOT_VALIDATED")
        require(
            self.call_counts["s3api:get-object"] == ordinal - 1,
            "RAW_READ_NOT_SEQUENTIAL",
        )
        binding = EXPECTED_RAW_VERSIONS[ordinal - 1]
        pair = (str(binding["s3_object_key"]), str(binding["version_id"]))
        require(pair not in self.attempted_pairs, "RAW_PAIR_REUSED")
        self.attempted_pairs.append(pair)
        metadata = self._invoke(
            "s3api:get-object",
            (
                "s3api",
                "get-object",
                "--bucket",
                BUCKET,
                "--key",
                pair[0],
                "--version-id",
                pair[1],
                "--expected-bucket-owner",
                ACCOUNT_ID,
                "--output",
                "json",
                "--no-cli-pager",
                str(destination),
            ),
        )
        require(destination.is_file() and not destination.is_symlink(), "RAW_TEMP_FILE_INVALID")
        require(stat.S_IMODE(destination.stat().st_mode) == 0o600, "RAW_TEMP_MODE_INVALID")
        body = destination.read_bytes()
        require(
            len(body) == binding["bytes"]
            and sha256_bytes(body) == binding["sha256"],
            "RAW_BODY_BINDING_MISMATCH",
        )
        require(
            metadata.get("VersionId") == binding["version_id"]
            and type(metadata.get("ContentLength")) is int
            and metadata.get("ContentLength") == binding["bytes"]
            and metadata.get("ServerSideEncryption") == "AES256"
            and metadata.get("ContentType") == EXPECTED_CONTENT_TYPE,
            "RAW_METADATA_BINDING_MISMATCH",
        )
        user_metadata = metadata.get("Metadata")
        require(
            isinstance(user_metadata, Mapping)
            and set(user_metadata) == EXPECTED_RAW_METADATA_KEYS
            and user_metadata.get("sha256") == binding["sha256"],
            "RAW_USER_METADATA_EXACT_SET_OR_SHA256_MISMATCH",
        )
        return body

    def read_all(self) -> list[bytes]:
        self.validate_configured_identity()
        bodies: list[bytes] = []
        total = 0
        with tempfile.TemporaryDirectory(prefix="g10-exclusion-s2-") as temp_name:
            temp = pathlib.Path(temp_name)
            for ordinal in range(1, EXPECTED_GET_CALLS + 1):
                destination = temp / f"page-{ordinal}.entity"
                descriptor = os.open(
                    destination,
                    os.O_WRONLY | os.O_CREAT | os.O_EXCL,
                    0o600,
                )
                os.close(descriptor)
                body = self.read_exact(ordinal, destination)
                total += len(body)
                require(total <= EXPECTED_TOTAL_BYTES, "RAW_TOTAL_BYTES_CEILING_EXCEEDED")
                bodies.append(body)
        require(
            self.call_counts == {"s3api:get-object": 4}
            and len(self.attempted_pairs) == 4
            and total == EXPECTED_TOTAL_BYTES,
            "LIVE_FINAL_CALL_OR_BYTE_COUNT_INVALID",
        )
        return bodies


def build_live_output(
    projection: Mapping[str, Any],
    reader: ExactAwsCli,
) -> dict[str, Any]:
    partition = projection.get("partition_accounting")
    target_rows = projection.get("target_occurrences")
    eligible = projection.get("eligible_projection")
    require(
        isinstance(partition, Mapping)
        and isinstance(target_rows, list)
        and isinstance(eligible, Mapping),
        "PURE_PROJECTION_SHAPE_INVALID",
    )
    ordinals = [row.get("global_row_ordinal") for row in target_rows]
    page_ordinals = [
        {
            "global_row_ordinal": row.get("global_row_ordinal"),
            "page_item_ordinal": row.get("page_item_ordinal"),
            "page_no": row.get("page_no"),
        }
        for row in target_rows
    ]
    require(
        all(type(value) is int and value > 0 for value in ordinals)
        and len(ordinals) == len(set(ordinals))
        and partition.get("excluded_total_occurrences") == len(ordinals)
        and len(ordinals) >= 3,
        "TARGET_ORDINAL_ACCOUNTING_INVALID",
    )
    result = {
        "artifact": (
            "M3TOP3_FINANCE_CA_PAGE100_G10_ISSUER_GROUP_EXCLUSION_"
            "ENUMERATION_S2_HASH_ONLY_RESULT_v1.0"
        ),
        "basDt": pure.EXPECTED_BASE_DATE,
        "claim_ceiling": {
            "company_master_or_universe_mutated": False,
            "gate_effect": "NONE",
            "issuer_identity_selected": False,
            "normalization_pit_promotion_release_production": False,
        },
        "effects": {
            **ZERO_PROHIBITED_EFFECTS,
            "oidc_assume_role_with_web_identity_calls": 1,
            "raw_bytes": EXPECTED_TOTAL_BYTES,
            "s3_get_object_version_calls": reader.call_counts["s3api:get-object"],
            "sts_get_caller_identity_calls": 1,
        },
        "eligible_projection": {
            "row_count": eligible.get("row_count"),
            "sha256": eligible.get("sha256"),
        },
        "partition_accounting": dict(partition),
        "read_binding": {
            "object_count": EXPECTED_GET_CALLS,
            "ordered_page_numbers": [1, 2, 3, 4],
            "raw_bytes": EXPECTED_TOTAL_BYTES,
            "raw_manifest_sha256": sha256_bytes(
                canonical_json_bytes(list(EXPECTED_RAW_VERSIONS))
            ),
        },
        "state": "PASS_HASH_ONLY_ENUMERATION_COMPLETE_NO_FILTER_MUTATION",
        "target_global_row_ordinals": ordinals,
        "target_page_ordinals": page_ordinals,
        "target_occurrence_count": len(ordinals),
    }
    require(
        isinstance(result["eligible_projection"]["sha256"], str)
        and bool(HASH_RE.fullmatch(result["eligible_projection"]["sha256"])),
        "ELIGIBLE_PROJECTION_DIGEST_INVALID",
    )
    require(not _contains_clear_identity_key(result), "CLEAR_IDENTITY_KEY_IN_OUTPUT")
    return result


def validate_bundle(
    root: pathlib.Path,
    authority_path: str,
    manifest_path: str,
    policy_path: str,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], bytes, bytes, bytes]:
    authority_file = root / authority_path
    manifest_file = root / manifest_path
    policy_file = root / policy_path
    authority = load_canonical_json(authority_file)
    manifest = load_canonical_json(manifest_file)
    policy = load_canonical_json(policy_file)
    validate_authority(root, authority)
    validate_manifest(root, manifest)
    validate_policy(policy)
    return (
        authority,
        manifest,
        policy,
        authority_file.read_bytes(),
        manifest_file.read_bytes(),
        policy_file.read_bytes(),
    )


def command_precheck(args: argparse.Namespace) -> int:
    root = pathlib.Path(args.root).resolve()
    authority, manifest, policy, authority_bytes, manifest_bytes, policy_bytes = (
        validate_bundle(root, args.authority, args.manifest, args.policy)
    )
    del authority, manifest, policy
    activation = load_canonical_json(root / args.activation)
    validate_activation(
        "PRECHECK",
        activation,
        authority_bytes,
        manifest_bytes,
        policy_bytes,
        args.expected_preparation_commit,
        args.expected_preparation_tree,
    )
    validate_event_lineage(
        "PRECHECK", activation, args.expected_preparation_commit
    )
    output = {
        "artifact": (
            "M3TOP3_FINANCE_CA_PAGE100_G10_ISSUER_GROUP_EXCLUSION_"
            "ENUMERATION_S2_PRECHECK_RESULT_v1.0"
        ),
        "effects": dict(EXPECTED_PRECHECK_EFFECTS),
        "generation_id": GENERATION_ID,
        "state": "PASS_OFFLINE_PRECHECK_ZERO_DATA_READ",
    }
    sys.stdout.buffer.write(canonical_json_bytes(output))
    return 0


def _validated_live_inputs(
    args: argparse.Namespace,
) -> tuple[dict[str, Any], dict[str, Any]]:
    root = pathlib.Path(args.root).resolve()
    authority, manifest, policy, authority_bytes, manifest_bytes, policy_bytes = (
        validate_bundle(root, args.authority, args.manifest, args.policy)
    )
    del manifest, policy
    activation = load_canonical_json(root / args.activation)
    validate_activation(
        "LIVE",
        activation,
        authority_bytes,
        manifest_bytes,
        policy_bytes,
        args.expected_preparation_commit,
        args.expected_preparation_tree,
    )
    validate_event_lineage("LIVE", activation, args.expected_preparation_commit)
    pass_receipt = load_canonical_json(root / args.precheck_pass)
    validate_precheck_pass(
        root,
        pass_receipt,
        activation,
        authority_bytes,
        manifest_bytes,
        policy_bytes,
        args.expected_preparation_commit,
        args.expected_preparation_tree,
    )
    return authority, activation


def command_live_preflight(args: argparse.Namespace) -> int:
    _validated_live_inputs(args)
    output = {
        "artifact": (
            "M3TOP3_FINANCE_CA_PAGE100_G10_ISSUER_GROUP_EXCLUSION_"
            "ENUMERATION_S2_LIVE_PREFLIGHT_RESULT_v1.0"
        ),
        "effects": dict(EXPECTED_PRECHECK_EFFECTS),
        "generation_id": GENERATION_ID,
        "state": "PASS_LIVE_PREFLIGHT_ZERO_EXTERNAL_EFFECT",
    }
    sys.stdout.buffer.write(canonical_json_bytes(output))
    return 0


def command_live(args: argparse.Namespace, *, run: RunCallable = subprocess.run) -> int:
    authority, _ = _validated_live_inputs(args)
    reader = ExactAwsCli(
        run,
        configured_account_id=os.environ.get("CONFIGURED_AWS_ACCOUNT_ID"),
    )
    bodies = reader.read_all()
    baseline = authority["baseline_identity_projection"]
    projection = pure.build_hash_only_exclusion_projection(
        bodies,
        exact_raw_versions=list(EXPECTED_RAW_VERSIONS),
        inherited_identity_hashes_by_custody_sha256=(
            baseline["identity_hashes_by_custody_sha256"]
        ),
        target_custody_key_sha256=pure.TARGET_CUSTODY_KEY_SHA256,
        frozen_identity_sha256=pure.FROZEN_IDENTITY_SHA256,
        observed_identity_sha256=pure.OBSERVED_IDENTITY_SHA256,
        expected_bas_dt=pure.EXPECTED_BASE_DATE,
        known_conflict_global_ordinals=pure.KNOWN_CONFLICT_GLOBAL_ORDINALS,
    )
    output = build_live_output(projection, reader)
    sys.stdout.buffer.write(canonical_json_bytes(output))
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    sub = result.add_subparsers(dest="command", required=True)
    for name in ("precheck", "live-preflight", "live"):
        command = sub.add_parser(name)
        command.add_argument("--root", default=".")
        command.add_argument("--authority", default=AUTHORITY_PATH)
        command.add_argument("--manifest", default=MANIFEST_PATH)
        command.add_argument("--policy", default=POLICY_PATH)
        command.add_argument("--expected-preparation-commit", required=True)
        command.add_argument("--expected-preparation-tree", required=True)
        if name == "precheck":
            command.add_argument("--activation", default=PRECHECK_ACTIVATION_PATH)
            command.set_defaults(func=command_precheck)
        else:
            command.add_argument("--activation", default=LIVE_ACTIVATION_PATH)
            command.add_argument("--precheck-pass", default=PRECHECK_PASS_PATH)
            command.set_defaults(
                func=command_live_preflight if name == "live-preflight" else command_live
            )
    return result


def main() -> int:
    args = parser().parse_args()
    try:
        return int(args.func(args))
    except (S2EnumerationError, pure.ExclusionPrecheckError) as exc:
        failure = {
            "artifact": "M3TOP3_FINANCE_CA_PAGE100_G10_ISSUER_GROUP_EXCLUSION_ENUMERATION_S2_FAILURE_v1.0",
            "code": str(exc),
            "state": "FAIL_CLOSED",
        }
        sys.stderr.buffer.write(canonical_json_bytes(failure))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
