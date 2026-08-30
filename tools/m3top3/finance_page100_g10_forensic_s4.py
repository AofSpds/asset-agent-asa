#!/usr/bin/env python3
"""Fresh G10 read-only forensic S4 projection-fix successor wrapper.

The original G10 core remains immutable.  This wrapper imports a separately
frozen S4 core whose only semantic delta is the governed nested delete-marker
namespace correction from ``claim`` to ``execution_claim``.  It adds fresh
PRECHECK/AUDIT lineage and the same bounded, exact-version, read-only controls.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import pathlib
import re
import subprocess
import tempfile
import urllib.parse
import zipfile
from collections.abc import Iterable, Mapping, Sequence
from typing import Any

try:
    from . import finance_page100_g10_forensic_s4_core as frozen
except ImportError:  # Direct script execution in GitHub Actions.
    import finance_page100_g10_forensic_s4_core as frozen


REPOSITORY = "AofSpds/asset-agent-asa"
BRANCH = "aaa-pmo-public-data-g2-g3-source-admission-v1-20260828"
ACTOR = "AofSpds"
ACCOUNT_ID = "956315449338"
REGION = "ap-northeast-2"
BUCKET = "semi-data-plane-aofspds-20260815"

GENERATION_STAMP = "20260830183123"
GENERATION_ID = "G10-READONLY-FORENSIC-S4-" + GENERATION_STAMP
RUNTIME_LOCK_ID = "PMO-G10-READONLY-FORENSIC-S4-" + GENERATION_STAMP
PREPARATION_ID = "G10-READONLY-FORENSIC-S4-PREPARATION-" + GENERATION_STAMP
PRECHECK_ACT_ID = "G10-READONLY-FORENSIC-S4-PRECHECK-" + GENERATION_STAMP
AUDIT_ACT_ID = "G10-READONLY-FORENSIC-S4-AUDIT-" + GENERATION_STAMP
ACTIVATION_ID = "G10-READONLY-FORENSIC-S4-ACTIVATION-" + GENERATION_STAMP

CURRENT_TERMINAL_HEAD = "bc5f7e21de0de53ad695cde7873536684248b75d"
CURRENT_TERMINAL_TREE = "3cac5ccb1da8eeaf8cf3415fda432b85bc28f148"
FAILED_RUN_ID = 33300797071
FAILED_JOB_ID = 99228439128
FAILED_RUN_ATTEMPT = 1
FAILED_ACTIVATION_HEAD = "05fb66022db971889562454da7817b7d5cf52da4"
FAILED_EXACT_CODE = "AUDIT_VERSION_HISTORY_INVALID"
FAILED_RECEIPT_PATH = (
    "control/m3top3/public-data-source-admission/v1.0/"
    "M3TOP3_FINANCE_CA_PAGE100_G10_FORENSIC_S3_AUDIT_TERMINAL_RECEIPT_"
    "33300797071_v1.0.json"
)
FAILED_RECEIPT_BYTES = 7596
FAILED_RECEIPT_BLOB = "dd3b330302548c442cb73232ac0bf6ba76dc2b87"
FAILED_RECEIPT_SHA256 = (
    "49d8ec795539781b211e9ab08abded3d65b7649f57bdb17914bdbfe6a2eb00db"
)
FAILED_RECEIPT_COMMIT = CURRENT_TERMINAL_HEAD
FAILED_RECEIPT_TREE = CURRENT_TERMINAL_TREE

OWNER_PACKET_TIME_KST = "2026-08-30T18:13:00+09:00"
OWNER_PACKET_BYTES = 12236
OWNER_PACKET_SHA256 = (
    "d4caf01eade6e538b6663a997ad5d558bebb290bcdfedce27975ece547f48795"
)
SOURCE_SCOPE_COMMENT_ID = 5466200427
SOURCE_SCOPE_COMMENT_SHA256 = (
    "918d1712759079046ce1bb3d41e41a1a64b3c5ae296b66d34b2b4a38fee42356"
)

PREP_MESSAGE = "Prepare G10 read-only forensic S4 20260830183123 v1.0"
PRECHECK_MESSAGE = "Arm G10 read-only forensic S4 PRECHECK 20260830183123 v1.0"
AUDIT_MESSAGE = "Arm G10 read-only forensic S4 AUDIT 20260830183123 v1.0"

ROOT = pathlib.Path(__file__).resolve().parents[2]
BASE_DIR = "control/m3top3/public-data-source-admission/v1.0"
PRECHECK_WORKFLOW_PATH = (
    ".github/workflows/"
    "m3top3-finance-page100-g10-readonly-forensic-s4-precheck-v1.yml"
)
AUDIT_WORKFLOW_PATH = (
    ".github/workflows/"
    "m3top3-finance-page100-g10-readonly-forensic-s4-audit-v1.yml"
)
RUNNER_PATH = "tools/m3top3/finance_page100_g10_forensic_s4.py"
CORRECTED_CORE_PATH = "tools/m3top3/finance_page100_g10_forensic_s4_core.py"
PREDECESSOR_CORE_PATH = "tools/m3top3/finance_page100_g10_forensic.py"
TEST_PATH = "tools/m3top3/tests/test_finance_page100_g10_forensic_s4.py"
AUTHORITY_PATH = (
    BASE_DIR + "/M3TOP3_FINANCE_CA_PAGE100_G10_FORENSIC_S4_AUTHORITY_v1.0.json"
)
MANIFEST_PATH = (
    BASE_DIR + "/M3TOP3_FINANCE_CA_PAGE100_G10_FORENSIC_S4_MANIFEST_v1.0.json"
)
PRECHECK_POLICY_PATH = (
    BASE_DIR
    + "/M3TOP3_FINANCE_CA_PAGE100_G10_FORENSIC_S4_PRECHECK_SESSION_POLICY_v1.0.json"
)
AUDIT_POLICY_PATH = (
    BASE_DIR
    + "/M3TOP3_FINANCE_CA_PAGE100_G10_FORENSIC_S4_AUDIT_SESSION_POLICY_v1.0.json"
)
PRECHECK_TEMPLATE_PATH = (
    BASE_DIR
    + "/M3TOP3_FINANCE_CA_PAGE100_G10_FORENSIC_S4_PRECHECK_ACTIVATION_v1.0.json.template"
)
AUDIT_TEMPLATE_PATH = (
    BASE_DIR
    + "/M3TOP3_FINANCE_CA_PAGE100_G10_FORENSIC_S4_AUDIT_ACTIVATION_v1.0.json.template"
)
PRECHECK_ACTIVATION_PATH = (
    BASE_DIR
    + "/M3TOP3_FINANCE_CA_PAGE100_G10_FORENSIC_S4_PRECHECK_ACTIVATION_v1.0.json"
)
AUDIT_ACTIVATION_PATH = (
    BASE_DIR
    + "/M3TOP3_FINANCE_CA_PAGE100_G10_FORENSIC_S4_AUDIT_ACTIVATION_v1.0.json"
)
PRECHECK_PASS_RECEIPT_PATH = (
    BASE_DIR
    + "/M3TOP3_FINANCE_CA_PAGE100_G10_FORENSIC_S4_PRECHECK_PASS_RECEIPT_v1.0.json"
)
PREP_FILES = frozenset(
    {
        PRECHECK_WORKFLOW_PATH,
        AUDIT_WORKFLOW_PATH,
        RUNNER_PATH,
        CORRECTED_CORE_PATH,
        TEST_PATH,
        AUTHORITY_PATH,
        PRECHECK_POLICY_PATH,
        AUDIT_POLICY_PATH,
        PRECHECK_TEMPLATE_PATH,
        AUDIT_TEMPLATE_PATH,
        MANIFEST_PATH,
    }
)

OLD_AUTHORITY_PATH = (
    BASE_DIR + "/M3TOP3_FINANCE_CA_PAGE100_G10_FORENSIC_AUTHORITY_v1.0.json"
)
OLD_ACTIVATION_PATH = (
    BASE_DIR + "/M3TOP3_FINANCE_CA_PAGE100_G10_FORENSIC_ACTIVATION_v1.0.json"
)
OLD_MANIFEST_PATH = (
    BASE_DIR + "/M3TOP3_FINANCE_CA_PAGE100_G10_FORENSIC_MANIFEST_v1.0.json"
)
G10_RECEIPT_PATH = frozen.TERMINAL_RECEIPT_PATH
PREDECESSOR_PATH = frozen.PREDECESSOR_CHECKPOINT_PATH
EXACT_RAW_VERSIONS = (
    {
        "bytes": 4642,
        "page_no": 1,
        "s3_object_key": frozen.RAW_PREFIX
        + "getRighExerReasSche_V2/quota_day_kst=2026-08-30/"
        + "request_id=2336abe1c81d4c86f90fef6575e204d0455367d4d5e8ed6cce103a752f0330da/"
        + "attempt=1/sha256=2e97f391bcf833db568de2c8638c5ff6d297ea07be21efc3fca6d05cd266c309.entity",
        "sha256": "2e97f391bcf833db568de2c8638c5ff6d297ea07be21efc3fca6d05cd266c309",
        "version_id": "VdsI_D_jNujHIb9ff8loyRWtuAW737RI",
    },
    {
        "bytes": 4697,
        "page_no": 2,
        "s3_object_key": frozen.RAW_PREFIX
        + "getRighExerReasSche_V2/quota_day_kst=2026-08-30/"
        + "request_id=dea3a2edfa78a4ebe2f912d2a8d8fa90456e960ad4cdbb832e501c91dd71d41c/"
        + "attempt=1/sha256=385cf9c3d3ba69c623ada225e8dd76fff8ce615658f7c37113f0cd326594fbb9.entity",
        "sha256": "385cf9c3d3ba69c623ada225e8dd76fff8ce615658f7c37113f0cd326594fbb9",
        "version_id": "30whtf2xTpWQYXPmr.Kt5RBnK1Y_YDI4",
    },
    {
        "bytes": 4570,
        "page_no": 3,
        "s3_object_key": frozen.RAW_PREFIX
        + "getRighExerReasSche_V2/quota_day_kst=2026-08-30/"
        + "request_id=eb594842fb4aa2c9a131efbb7b64f4bb72f3678315fa352224132355bd0be1de/"
        + "attempt=1/sha256=ef7ef262d0cc39c703b98bc8321c75d5c715bd58b6a0677d8897de9e43e49ce9.entity",
        "sha256": "ef7ef262d0cc39c703b98bc8321c75d5c715bd58b6a0677d8897de9e43e49ce9",
        "version_id": "1dHYBfs4hg1tM7S6TckyUngOmfwWKZc2",
    },
    {
        "bytes": 4821,
        "page_no": 4,
        "s3_object_key": frozen.RAW_PREFIX
        + "getRighExerReasSche_V2/quota_day_kst=2026-08-30/"
        + "request_id=75494b2b71aeb1dcfd52e2cba2198e933fef2ad271c900328085da375dd9989c/"
        + "attempt=1/sha256=8ab2eec3af93ef2a26097a65d8f0964471160e222245a6e2ae3b79adac69afe1.entity",
        "sha256": "8ab2eec3af93ef2a26097a65d8f0964471160e222245a6e2ae3b79adac69afe1",
        "version_id": "iBxAq9V.V7eA_doOM39JcVt_gtzAHskI",
    },
)

EVENT_KEYS = (
    "EVENT_ACTOR",
    "EVENT_TRIGGERING_ACTOR",
    "EVENT_REPOSITORY",
    "EVENT_REF",
    "EVENT_BEFORE",
    "EVENT_AFTER",
    "EVENT_FORCED",
    "EVENT_HEAD_MESSAGE",
    "EVENT_RUN_ATTEMPT",
)
PRECHECK_OUTPUT_NAMES = frozenset(
    {
        "precheck-receipt.json",
        "activation-readback.json",
        "aws-readonly-session-receipt.json",
        "exact-secret-scan.json",
        "sanitization-receipt.json",
        "terminal-summary.json",
    }
)
AUDIT_OUTPUT_NAMES = frozenset(
    {
        "precheck-receipt.json",
        "activation-readback.json",
        "aws-readonly-session-receipt.json",
        "raw-version-manifest.json",
        "checkpoint-version-history.json",
        "execution-claim-version-history.json",
        "issuer-conflict-reproduction.json",
        "exact-secret-scan.json",
        "sanitization-receipt.json",
        "terminal-summary.json",
    }
)
ZERO_EFFECTS = {
    "finance_provider_api_calls": 0,
    "quota_reservations": 0,
    "s3_put_object_calls": 0,
    "s3_delete_object_calls": 0,
    "remote_custody_mutations": 0,
    "normalization_records": 0,
    "promotion_actions": 0,
}
AUTHORIZED_READ_REPEAT = {
    "max_fresh_successor_audit_attempts_after_approval": 2,
    "this_successor_audit_attempt_ordinal": 1,
    "per_audit_maximums": {
        "sts_get_caller_identity_calls": 1,
        "s3_list_object_versions_calls": 3,
        "s3_get_object_version_calls": 33,
        "raw_object_version_reads": 4,
        "checkpoint_object_version_reads": 28,
        "execution_claim_object_version_reads": 1,
        "finance_provider_api_calls": 0,
        "quota_reservations": 0,
        "s3_put_object_calls": 0,
        "s3_delete_object_calls": 0,
        "remote_custody_mutations": 0,
    },
}
PRECHECK_POLICY_ACTIONS = {
    "s3:GetBucketLocation",
    "s3:GetBucketVersioning",
}
AUDIT_POLICY_ACTIONS = {
    "s3:ListBucketVersions",
    "s3:GetObjectVersion",
}
AUDIT_POLICY_CHARACTERS = 1357
AUDIT_POLICY_BYTES = 1358
AUDIT_POLICY_SHA256 = (
    "e5e3ff62bfec4490d5589491aec9ad4a0febde384c27e4be7a623ce5052e96db"
)
AUDIT_POLICY_GIT_BLOB_SHA = "19c4454358bc73e835b8eb70084c80edc20dd694"
EXACT_CLAIM_VERSION_ID = "27scTNMVYtc.VuIP2xEo.qqPKN3WQiPf"
PREDECESSOR_CORE_BYTES = 72718
PREDECESSOR_CORE_SHA256 = (
    "d05c2081bdaf4a79b07ca1b990c1c88ba8ca07b9fb2ecfee4882ddaf157f21a5"
)
PREDECESSOR_CORE_GIT_BLOB_SHA = "8320e75871c06618e8d67ccdcb9bd56168c0b416"
CORRECTED_CORE_BYTES = 72815
CORRECTED_CORE_SHA256 = (
    "84aa27b79f65c25384411055c5597f2d13012bc4677f3bb05a7fa5e4d5d496e1"
)
CORRECTED_CORE_GIT_BLOB_SHA = "4b20d83f056c56e36b273ad0b5680cef22f0dd19"
OBSOLETE_PROJECTION_LINE = (
    b'            "all_delete_marker_counts": {name: len(value["delete_markers"]) '
    b'for name, value in inventories.items()},\n'
)
CORRECTED_PROJECTION_LINE = (
    b'            "all_delete_marker_counts": {"raw": len(inventories["raw"]'
    b'["delete_markers"]), "control": len(inventories["control"]'
    b'["delete_markers"]), "execution_claim": len(inventories["claim"]'
    b'["delete_markers"])},\n'
)
VERSION_HISTORY_KEYS = frozenset(
    {"raw", "control", "execution_claim", "all_delete_marker_counts"}
)
DELETE_MARKER_COUNT_KEYS = frozenset({"raw", "control", "execution_claim"})
BANNED_ACTION_FRAGMENTS = (
    "Put",
    "Delete",
    "Copy",
    "Restore",
    "CreateMultipart",
    "UploadPart",
    "CompleteMultipart",
    "AbortMultipart",
)
BANNED_TEXT_PATTERNS = (
    re.compile(r"(?i)[\"']authorization[\"']\s*:"),
    re.compile(r"(?im)^authorization\s*:"),
    re.compile(r"(?i)[\"']?authorization[\"']?\s*:\s*[\"']?bearer\b"),
    re.compile(r"(?i)x-amz-(credential|signature|security-token)"),
    re.compile(
        r"(?i)[\"']?aws_(access_key_id|secret_access_key|session_token)[\"']?\s*[:=]"
    ),
    re.compile(
        r"(?i)[\"']?(service[_-]?key|api[_-]?key)[\"']?\s*[:=]"
    ),
    re.compile(
        r"(?i)[?&](signature|access_token|auth_token|token|service[_-]?key|api[_-]?key)="
    ),
    re.compile(
        r"(?i)[\"']?actions_id_token_request_token[\"']?\s*[:=]"
    ),
    re.compile(r"(?i)raw_secret_sentinel"),
    re.compile(
        r"(?i)[\"'](issuCmpyKsdCustNo|crno|stckIssuCmpyNm)[\"']\s*:"
    ),
    re.compile(r"(?i)<(issuCmpyKsdCustNo|crno|stckIssuCmpyNm)>"),
    re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    re.compile(r"\bgh(?:p|o|u|s|r)_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b"),
    re.compile(r"(?i)https?://[^/\s:@]+:[^/\s@]+@"),
)


class S4ForensicError(RuntimeError):
    """Fail-closed S4 control error."""


def require(condition: bool, code: str) -> None:
    if not condition:
        raise S4ForensicError(code)


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(
        b"blob " + str(len(data)).encode("ascii") + b"\0" + data
    ).hexdigest()


def load_canonical_json(path: pathlib.Path) -> dict[str, Any]:
    raw = path.read_bytes()
    require(raw.endswith(b"\n") and not raw.endswith(b"\n\n"), "JSON_NEWLINE_INVALID")
    try:
        value = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise S4ForensicError("JSON_PARSE_INVALID") from exc
    require(isinstance(value, dict), "JSON_ROOT_NOT_OBJECT")
    require(raw == canonical_json_bytes(value), "JSON_NOT_CANONICAL")
    return value


def parse_canonical_json_bytes(raw: bytes, code: str) -> dict[str, Any]:
    require(raw.endswith(b"\n") and not raw.endswith(b"\n\n"), code + "_NEWLINE")
    try:
        value = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise S4ForensicError(code + "_PARSE") from exc
    require(isinstance(value, dict), code + "_ROOT")
    require(raw == canonical_json_bytes(value), code + "_CANONICAL")
    return value


def write_canonical_json(path: pathlib.Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_json_bytes(dict(value)))


def file_binding(relative: str) -> dict[str, Any]:
    data = (ROOT / relative).read_bytes()
    return {
        "bytes": len(data),
        "git_blob_sha": git_blob_sha(data),
        "sha256": sha256_bytes(data),
    }


def validate_corrected_core_delta() -> None:
    predecessor = (ROOT / PREDECESSOR_CORE_PATH).read_bytes()
    corrected = (ROOT / CORRECTED_CORE_PATH).read_bytes()
    require(
        len(predecessor) == PREDECESSOR_CORE_BYTES
        and sha256_bytes(predecessor) == PREDECESSOR_CORE_SHA256
        and git_blob_sha(predecessor) == PREDECESSOR_CORE_GIT_BLOB_SHA,
        "S4_PREDECESSOR_CORE_BINDING_INVALID",
    )
    require(
        len(corrected) == CORRECTED_CORE_BYTES
        and sha256_bytes(corrected) == CORRECTED_CORE_SHA256
        and git_blob_sha(corrected) == CORRECTED_CORE_GIT_BLOB_SHA,
        "S4_CORRECTED_CORE_BINDING_INVALID",
    )
    require(
        predecessor.count(OBSOLETE_PROJECTION_LINE) == 1
        and CORRECTED_PROJECTION_LINE not in predecessor
        and corrected == predecessor.replace(
            OBSOLETE_PROJECTION_LINE, CORRECTED_PROJECTION_LINE, 1
        ),
        "S4_CORE_DELTA_NOT_EXACT_NAMESPACE_CORRECTION",
    )


def _single_parent(commit: str) -> str:
    line = str(frozen._git_output("rev-list", "--parents", "-n", "1", commit)).split()
    require(len(line) == 2 and line[0] == commit, "GIT_COMMIT_PARENT_COUNT_INVALID")
    return line[1]


def _raw_message(commit: str) -> bytes:
    return frozen._raw_commit_message(commit)


def _diff_names(before: str, after: str) -> dict[str, str]:
    return frozen._exact_diff_names(before, after)


def _message_for(mode: str) -> str:
    require(mode in {"PRECHECK", "AUDIT"}, "MODE_INVALID")
    return PRECHECK_MESSAGE if mode == "PRECHECK" else AUDIT_MESSAGE


def _activation_path(mode: str) -> str:
    require(mode in {"PRECHECK", "AUDIT"}, "MODE_INVALID")
    return PRECHECK_ACTIVATION_PATH if mode == "PRECHECK" else AUDIT_ACTIVATION_PATH


def _attempt_latch(mode: str) -> dict[str, Any]:
    require(mode in {"PRECHECK", "AUDIT"}, "MODE_INVALID")
    return {
        "max_fresh_successor_audit_attempts_after_approval": 2,
        "precheck_consumes_audit_attempt": False,
        "consumed_audit_attempts_before_activation": 0,
        "this_audit_attempt_ordinal": None if mode == "PRECHECK" else 1,
    }


def _owner_binding() -> dict[str, Any]:
    return {
        "author": ACTOR,
        "body_bytes": OWNER_PACKET_BYTES,
        "body_sha256": OWNER_PACKET_SHA256,
        "issued_at_kst": OWNER_PACKET_TIME_KST,
        "semantics": "G10_READ_ONLY_FORENSIC_PROJECTION_FIX_FRESH_SUCCESSOR_EXACT_REPEAT_READ_AUTHORITY",
        "source": "CURRENT_PMO_CHANNEL_OWNER_PACKET",
    }


def _workflow_path(mode: str) -> str:
    require(mode in {"PRECHECK", "AUDIT"}, "MODE_INVALID")
    return PRECHECK_WORKFLOW_PATH if mode == "PRECHECK" else AUDIT_WORKFLOW_PATH


def _policy_path(mode: str) -> str:
    require(mode in {"PRECHECK", "AUDIT"}, "MODE_INVALID")
    return PRECHECK_POLICY_PATH if mode == "PRECHECK" else AUDIT_POLICY_PATH


def validate_policy(policy: Mapping[str, Any], mode: str) -> None:
    require(policy.get("Version") == "2012-10-17", "POLICY_VERSION_INVALID")
    statements = policy.get("Statement")
    expected_statement_count = 1 if mode == "PRECHECK" else 2
    require(
        isinstance(statements, list) and len(statements) == expected_statement_count,
        "POLICY_STATEMENTS_INVALID",
    )
    actions: set[str] = set()
    for row in statements:
        require(isinstance(row, dict) and row.get("Effect") == "Allow", "POLICY_EFFECT_INVALID")
        raw = row.get("Action")
        values = raw if isinstance(raw, list) else [raw]
        require(all(isinstance(item, str) for item in values), "POLICY_ACTION_INVALID")
        actions.update(values)
    expected_actions = (
        PRECHECK_POLICY_ACTIONS if mode == "PRECHECK" else AUDIT_POLICY_ACTIONS
    )
    require(actions == expected_actions, "POLICY_ACTION_SET_INVALID")
    require(
        not any(
            fragment in action
            for action in actions
            for fragment in BANNED_ACTION_FRAGMENTS
        ),
        "POLICY_WRITE_ACTION_PRESENT",
    )
    require(not any("*" in action for action in actions), "POLICY_WILDCARD_ACTION_PRESENT")
    bucket = "arn:aws:s3:::" + BUCKET
    if mode == "PRECHECK":
        require(
            statements[0].get("Resource") == bucket,
            "POLICY_BUCKET_METADATA_RESOURCE_INVALID",
        )
        require("Condition" not in statements[0], "POLICY_PRECHECK_CONDITION_INVALID")
        return
    require(statements[0].get("Resource") == bucket, "POLICY_LIST_RESOURCE_INVALID")
    prefixes = (
        statements[0]
        .get("Condition", {})
        .get("StringEquals", {})
        .get("s3:prefix")
    )
    require(
        prefixes == [frozen.RAW_PREFIX, frozen.CONTROL_PREFIX, frozen.CLAIM_KEY],
        "POLICY_LIST_PREFIXES_INVALID",
    )
    require(
        statements[1].get("Resource")
        == [
            bucket + "/" + frozen.RAW_PREFIX + "*",
            bucket + "/" + frozen.CHECKPOINT_KEY,
            bucket + "/" + frozen.CLAIM_KEY,
        ]
        and "Condition" not in statements[1],
        "POLICY_GET_RESOURCE_SCOPE_INVALID",
    )
    data = canonical_json_bytes(dict(policy))
    require(
        len(data) == AUDIT_POLICY_BYTES
        and len(data) - 1 == AUDIT_POLICY_CHARACTERS
        and sha256_bytes(data) == AUDIT_POLICY_SHA256
        and git_blob_sha(data) == AUDIT_POLICY_GIT_BLOB_SHA,
        "POLICY_COMPACT_EXACT_BINDING_INVALID",
    )


def validate_frozen_base() -> tuple[dict[str, Any], ...]:
    authority = load_canonical_json(ROOT / OLD_AUTHORITY_PATH)
    activation = load_canonical_json(ROOT / OLD_ACTIVATION_PATH)
    receipt = load_canonical_json(ROOT / G10_RECEIPT_PATH)
    predecessor = load_canonical_json(ROOT / PREDECESSOR_PATH)
    manifest = load_canonical_json(ROOT / OLD_MANIFEST_PATH)
    frozen.validate_static_contract(
        authority, activation, receipt, predecessor, manifest
    )
    return authority, activation, receipt, predecessor, manifest


def validate_s4_contract(
    authority: Mapping[str, Any],
    activation: Mapping[str, Any],
    manifest: Mapping[str, Any],
    policy: Mapping[str, Any],
    mode: str,
) -> None:
    require(
        authority.get("artifact")
        == "M3TOP3_FINANCE_CA_PAGE100_G10_FORENSIC_S4_AUTHORITY_v1.0",
        "S4_AUTHORITY_ARTIFACT_INVALID",
    )
    require(
        authority.get("state")
        == "OWNER_AUTHORIZED_G10_READ_ONLY_FORENSIC_PROJECTION_FIX_SUCCESSOR",
        "S4_AUTHORITY_STATE_INVALID",
    )
    require(
        authority.get("repository") == REPOSITORY
        and authority.get("branch") == BRANCH,
        "S4_AUTHORITY_REPO_BRANCH_INVALID",
    )
    require(
        authority.get("project") == "AAA"
        and authority.get("product") == "ASSET AGENT ASA"
        and authority.get("current_persona_lock")
        == "AAA-PMO-ORCHESTRATOR (PMO)",
        "S4_AUTHORITY_PERSONA_INVALID",
    )
    require(
        authority.get("current_owner_authorization") == _owner_binding(),
        "S4_OWNER_BINDING_INVALID",
    )
    source_scope = authority.get("source_scope_authorization", {})
    require(
        source_scope.get("issue_comment_id") == SOURCE_SCOPE_COMMENT_ID
        and source_scope.get("body_sha256") == SOURCE_SCOPE_COMMENT_SHA256,
        "S4_SOURCE_SCOPE_BINDING_INVALID",
    )
    successor = authority.get("successor_identity")
    require(
        successor
        == {
            "activation_id": ACTIVATION_ID,
            "audit_act_id": AUDIT_ACT_ID,
            "generation_id": GENERATION_ID,
            "preparation_id": PREPARATION_ID,
            "precheck_act_id": PRECHECK_ACT_ID,
            "runtime_lock_id": RUNTIME_LOCK_ID,
        },
        "S4_SUCCESSOR_IDENTITY_INVALID",
    )
    predecessor = authority.get("predecessor_forensic_terminal", {})
    require(
        predecessor
        == {
            "activation_head_sha": FAILED_ACTIVATION_HEAD,
            "exact_code": FAILED_EXACT_CODE,
            "exact_control_defect": "DELETE_MARKER_PROJECTION_NAMESPACE_KEY_MISMATCH_CLAIM_VS_EXECUTION_CLAIM",
            "failure_phase": "POST_FROZEN_CORE_VERSION_HISTORY_PROJECTION_VALIDATION",
            "job_id": FAILED_JOB_ID,
            "receipt": {
                "bytes": FAILED_RECEIPT_BYTES,
                "commit_sha": FAILED_RECEIPT_COMMIT,
                "git_blob_sha": FAILED_RECEIPT_BLOB,
                "path": FAILED_RECEIPT_PATH,
                "sha256": FAILED_RECEIPT_SHA256,
                "tree_sha": FAILED_RECEIPT_TREE,
            },
            "run_attempt": FAILED_RUN_ATTEMPT,
            "run_id": FAILED_RUN_ID,
            "terminal_head_sha": CURRENT_TERMINAL_HEAD,
            "terminal_tree_sha": CURRENT_TERMINAL_TREE,
        },
        "S4_PREDECESSOR_TERMINAL_INVALID",
    )
    require(authority.get("authorized_effects") == ZERO_EFFECTS, "S4_EFFECTS_NOT_ZERO")
    require(
        authority.get("authorized_effects_semantics")
        == "NON_READ_PROVIDER_QUOTA_MUTATION_AND_DOWNSTREAM_EFFECTS_ONLY",
        "S4_EFFECT_SEMANTICS_INVALID",
    )
    require(
        authority.get("authorized_read_repeat") == AUTHORIZED_READ_REPEAT,
        "S4_READ_REPEAT_AUTHORITY_INVALID",
    )
    require(
        authority.get("projection_namespace_contract")
        == {
            "all_delete_marker_count_keys": sorted(DELETE_MARKER_COUNT_KEYS),
            "obsolete_claim_key_absent": True,
            "version_history_keys": sorted(VERSION_HISTORY_KEYS),
        },
        "S4_PROJECTION_NAMESPACE_CONTRACT_INVALID",
    )
    require(
        authority.get("control_loop_stop_rule")
        == {
            "exact_predecessor_defect_fingerprint": {
                "exact_code": FAILED_EXACT_CODE,
                "exact_control_defect": "DELETE_MARKER_PROJECTION_NAMESPACE_KEY_MISMATCH_CLAIM_VS_EXECUTION_CLAIM",
                "failure_phase": "POST_FROZEN_CORE_VERSION_HISTORY_PROJECTION_VALIDATION",
            },
            "on_same_fingerprint_recurrence": "CONTROL_LOOP_DETECTED",
            "owner_action_required": True,
            "remaining_attempt_budget_does_not_override_stop": True,
        },
        "S4_CONTROL_LOOP_STOP_RULE_INVALID",
    )
    require(authority.get("g10_live_rerun_authorized") is False, "S4_G10_RERUN_ENABLED")
    require(authority.get("g11_authorized") is False, "S4_G11_ENABLED")
    require(authority.get("semantic_change_authorized") is False, "S4_SEMANTIC_CHANGE_ENABLED")
    require(authority.get("normalization_promotion_release_production_authorized") is False, "S4_RELEASE_SURFACE_ENABLED")
    aws = authority.get("aws_read_only_scope", {})
    require(
        aws.get("account_id") == ACCOUNT_ID
        and aws.get("region") == REGION
        and aws.get("bucket") == BUCKET,
        "S4_AWS_SCOPE_INVALID",
    )
    require(
        set(aws.get("precheck_allowed_s3_actions", []))
        == PRECHECK_POLICY_ACTIONS
        and set(aws.get("audit_allowed_s3_actions", []))
        == AUDIT_POLICY_ACTIONS
        and aws.get("oidc_sts_operations")
        == ["sts:AssumeRoleWithWebIdentity", "sts:GetCallerIdentity"],
        "S4_AWS_ACTIONS_INVALID",
    )
    require(
        aws.get("raw_prefix") == frozen.RAW_PREFIX
        and aws.get("control_prefix") == frozen.CONTROL_PREFIX
        and aws.get("execution_claim_key") == frozen.CLAIM_KEY,
        "S4_AWS_PREFIX_INVALID",
    )
    require(
        aws.get("audit_session_controls")
        == {
            "checkpoint_exact_listed_pairs": 28,
            "execution_claim_exact_key_version_pairs": 1,
            "inline_session_policy_canonical_characters": AUDIT_POLICY_CHARACTERS,
            "managed_session_policies": [],
            "no_other_key_or_pair": True,
            "raw_exact_key_version_pairs": 4,
            "session_tags": [],
        },
        "S4_AWS_SESSION_CONTROLS_INVALID",
    )
    require(
        authority.get("fresh_successor_guard")
        == {
            "fresh_s4_precheck_required": True,
            "prior_s3_activation_reused": False,
            "prior_s3_precheck_artifact_reused": False,
            "prior_s3_run_retried_or_reused": False,
            "predecessor_audit_read_effects_repeated_only_under_current_packet": True,
        },
        "S4_FRESH_SUCCESSOR_GUARD_INVALID",
    )

    failed_bytes = (ROOT / FAILED_RECEIPT_PATH).read_bytes()
    require(
        len(failed_bytes) == FAILED_RECEIPT_BYTES
        and sha256_bytes(failed_bytes) == FAILED_RECEIPT_SHA256
        and git_blob_sha(failed_bytes) == FAILED_RECEIPT_BLOB,
        "S4_FAILED_RECEIPT_BYTES_INVALID",
    )
    failed = json.loads(failed_bytes)
    require(
        failed.get("terminal_checkpoint", {}).get("exact_code") == FAILED_EXACT_CODE
        and failed.get("workflow", {}).get("run_id") == FAILED_RUN_ID
        and failed.get("workflow", {}).get("job_id") == FAILED_JOB_ID
        and failed.get("artifact")
        == "M3TOP3_FINANCE_CA_PAGE100_G10_FORENSIC_S3_AUDIT_TERMINAL_RECEIPT_v1.0"
        and failed.get("terminal_checkpoint", {}).get("exact_control_defect")
        == "DELETE_MARKER_PROJECTION_NAMESPACE_KEY_MISMATCH_CLAIM_VS_EXECUTION_CLAIM",
        "S4_FAILED_RECEIPT_CONTENT_INVALID",
    )

    validate_policy(policy, mode)
    policy_data = (ROOT / _policy_path(mode)).read_bytes()
    require(
        policy_data == canonical_json_bytes(policy),
        "S4_POLICY_BYTES_INVALID",
    )
    workflow_data = (ROOT / _workflow_path(mode)).read_bytes()
    require(
        b"inline-session-policy: >-\n            " + policy_data in workflow_data,
        "S4_WORKFLOW_POLICY_BYTES_MISMATCH",
    )
    require(
        workflow_data.count(b"role-skip-session-tagging: true") == 1
        and b"managed-session-policies:" not in workflow_data
        and b"role-session-tags:" not in workflow_data
        and b"session-tags:" not in workflow_data,
        "S4_WORKFLOW_MANAGED_POLICY_OR_SESSION_TAG_INVALID",
    )
    bindings = authority.get("execution_bindings")
    require(isinstance(bindings, dict), "S4_EXECUTION_BINDINGS_INVALID")
    for key, relative in (
        ("precheck_workflow", PRECHECK_WORKFLOW_PATH),
        ("audit_workflow", AUDIT_WORKFLOW_PATH),
        ("runner", RUNNER_PATH),
        ("corrected_core", CORRECTED_CORE_PATH),
        ("precheck_policy", PRECHECK_POLICY_PATH),
        ("audit_policy", AUDIT_POLICY_PATH),
        ("focused_tests", TEST_PATH),
    ):
        require(
            bindings.get(key) == {"path": relative, **file_binding(relative)},
            "S4_EXECUTION_BINDING_INVALID_" + key,
        )

    require(
        manifest.get("artifact")
        == "M3TOP3_FINANCE_CA_PAGE100_G10_FORENSIC_S4_MANIFEST_v1.0",
        "S4_MANIFEST_ARTIFACT_INVALID",
    )
    require(
        manifest.get("preparation_parent_head_sha") == CURRENT_TERMINAL_HEAD
        and manifest.get("preparation_parent_tree_sha") == CURRENT_TERMINAL_TREE,
        "S4_MANIFEST_PARENT_INVALID",
    )
    require(
        manifest.get("preparation_commit_message") == PREP_MESSAGE
        and manifest.get("preparation_id") == PREPARATION_ID
        and manifest.get("state") == "IMMUTABLE_S4_PREPARATION_MANIFEST",
        "S4_MANIFEST_IDENTITY_INVALID",
    )
    manifest_files = manifest.get("preparation_files")
    require(
        isinstance(manifest_files, dict)
        and set(manifest_files) == PREP_FILES - {MANIFEST_PATH},
        "S4_MANIFEST_FILE_SET_INVALID",
    )
    for relative, binding in manifest_files.items():
        require(binding == file_binding(relative), "S4_MANIFEST_BINDING_INVALID_" + relative)

    require(
        activation.get("artifact")
        == (
            "M3TOP3_FINANCE_CA_PAGE100_G10_FORENSIC_S4_PRECHECK_ACTIVATION_v1.0"
            if mode == "PRECHECK"
            else "M3TOP3_FINANCE_CA_PAGE100_G10_FORENSIC_S4_AUDIT_ACTIVATION_v1.0"
        ),
        "S4_ACTIVATION_ARTIFACT_INVALID",
    )
    require(activation.get("mode") == mode, "S4_ACTIVATION_MODE_INVALID")
    require(
        activation.get("state")
        == ("ARMED_FRESH_PRECHECK_ONCE" if mode == "PRECHECK" else "ARMED_FRESH_AUDIT_ONCE"),
        "S4_ACTIVATION_STATE_INVALID",
    )
    require(
        activation.get("repository") == REPOSITORY
        and activation.get("branch") == BRANCH
        and activation.get("owner_actor") == ACTOR
        and activation.get("current_persona_lock")
        == "AAA-PMO-ORCHESTRATOR (PMO)",
        "S4_ACTIVATION_REPO_BRANCH_INVALID",
    )
    require(
        activation.get("activation_commit_message") == _message_for(mode),
        "S4_ACTIVATION_MESSAGE_INVALID",
    )
    require(
        activation.get("current_owner_authorization") == _owner_binding(),
        "S4_ACTIVATION_OWNER_INVALID",
    )
    require(activation.get("successor_identity") == successor, "S4_ACTIVATION_IDENTITY_INVALID")
    require(
        activation.get("current_terminal_head_sha") == CURRENT_TERMINAL_HEAD
        and activation.get("current_terminal_tree_sha") == CURRENT_TERMINAL_TREE,
        "S4_ACTIVATION_TERMINAL_BASE_INVALID",
    )
    require(activation.get("authorized_effects") == ZERO_EFFECTS, "S4_ACTIVATION_EFFECTS_INVALID")
    require(
        activation.get("authorized_read_repeat") == AUTHORIZED_READ_REPEAT,
        "S4_ACTIVATION_READ_REPEAT_INVALID",
    )
    require(
        activation.get("audit_attempt_latch") == _attempt_latch(mode),
        "S4_ACTIVATION_AUDIT_ATTEMPT_LATCH_INVALID",
    )
    require(activation.get("g10_live_rerun") is False and activation.get("g11_generation") is False, "S4_ACTIVATION_SCOPE_INVALID")
    require(
        activation.get("consumed_predecessor")
        == {
            "activation_head_sha": FAILED_ACTIVATION_HEAD,
            "exact_code": FAILED_EXACT_CODE,
            "exact_control_defect": "DELETE_MARKER_PROJECTION_NAMESPACE_KEY_MISMATCH_CLAIM_VS_EXECUTION_CLAIM",
            "failure_phase": "POST_FROZEN_CORE_VERSION_HISTORY_PROJECTION_VALIDATION",
            "job_id": FAILED_JOB_ID,
            "run_attempt": FAILED_RUN_ATTEMPT,
            "run_id": FAILED_RUN_ID,
            "terminal_receipt_sha256": FAILED_RECEIPT_SHA256,
        },
        "S4_ACTIVATION_CONSUMED_PREDECESSOR_INVALID",
    )
    require(
        activation.get("execution_bindings") == bindings,
        "S4_ACTIVATION_EXECUTION_BINDINGS_INVALID",
    )
    for key in ("preparation_head_sha", "preparation_tree_sha"):
        require(
            bool(re.fullmatch(r"[0-9a-f]{40}", str(activation.get(key, "")))),
            "S4_ACTIVATION_PREPARATION_ID_INVALID",
        )
    if mode == "PRECHECK":
        require("precheck_evidence" not in activation, "S4_PRECHECK_SELF_EVIDENCE_PRESENT")
    else:
        proof = activation.get("precheck_evidence")
        require(isinstance(proof, dict), "S4_AUDIT_PRECHECK_EVIDENCE_MISSING")
        require(
            bool(re.fullmatch(r"[0-9a-f]{40}", str(proof.get("activation_head_sha", ""))))
            and bool(re.fullmatch(r"[0-9a-f]{40}", str(proof.get("activation_tree_sha", "")))),
            "S4_AUDIT_PRECHECK_GIT_ID_INVALID",
        )
        require(
            type(proof.get("run_id")) is int
            and proof.get("run_id") > 0
            and type(proof.get("job_id")) is int
            and proof.get("job_id") > 0
            and type(proof.get("artifact_id")) is int
            and proof.get("artifact_id") > 0,
            "S4_AUDIT_PRECHECK_RUNTIME_ID_INVALID",
        )
        require(
            proof.get("conclusion") == "success"
            and proof.get("run_attempt") == 1
            and proof.get("artifact_digest", "").startswith("sha256:")
            and bool(re.fullmatch(r"[0-9a-f]{64}", proof["artifact_digest"][7:])),
            "S4_AUDIT_PRECHECK_RESULT_INVALID",
        )
        require(
            proof.get("artifact_name")
            == f"m3top3-g10-readonly-forensic-s4-precheck-{proof['run_id']}-1",
            "S4_AUDIT_PRECHECK_ARTIFACT_NAME_INVALID",
        )
        require(
            type(proof.get("artifact_size_in_bytes")) is int
            and proof.get("artifact_size_in_bytes") > 0,
            "S4_AUDIT_PRECHECK_ARTIFACT_SIZE_INVALID",
        )
        pass_binding = proof.get("pass_receipt")
        require(isinstance(pass_binding, dict), "S4_PRECHECK_PASS_BINDING_MISSING")
        require(
            pass_binding.get("path") == PRECHECK_PASS_RECEIPT_PATH
            and pass_binding.get("commit_message")
            == f"Seal G10 read-only forensic S4 PRECHECK PASS {proof['run_id']} v1.0"
            and bool(
                re.fullmatch(
                    r"[0-9a-f]{40}", str(pass_binding.get("commit_head_sha", ""))
                )
            )
            and bool(
                re.fullmatch(
                    r"[0-9a-f]{40}", str(pass_binding.get("commit_tree_sha", ""))
                )
            ),
            "S4_PRECHECK_PASS_GIT_BINDING_INVALID",
        )
        pass_data = (ROOT / PRECHECK_PASS_RECEIPT_PATH).read_bytes()
        require(
            pass_binding.get("bytes") == len(pass_data)
            and pass_binding.get("sha256") == sha256_bytes(pass_data)
            and pass_binding.get("git_blob_sha") == git_blob_sha(pass_data),
            "S4_PRECHECK_PASS_FILE_BINDING_INVALID",
        )
        pass_receipt = load_canonical_json(ROOT / PRECHECK_PASS_RECEIPT_PATH)
        require(
            pass_receipt.get("artifact")
            == "M3TOP3_FINANCE_CA_PAGE100_G10_FORENSIC_S4_PRECHECK_PASS_RECEIPT_v1.0"
            and pass_receipt.get("state") == "TERMINAL_PRECHECK_PASS_ZERO_EFFECT"
            and pass_receipt.get("generation_id") == GENERATION_ID
            and pass_receipt.get("precheck_evidence")
            == {key: value for key, value in proof.items() if key != "pass_receipt"},
            "S4_PRECHECK_PASS_CONTENT_INVALID",
        )

    g10_receipt = load_canonical_json(ROOT / G10_RECEIPT_PATH)
    expected_raw_versions = [
        {
            "bytes": row["bytes"],
            "page_no": row["page_no"],
            "s3_object_key": row["s3_object_key"],
            "sha256": row["sha256"],
            "version_id": row["version_id"],
        }
        for row in g10_receipt["remote_effects"]["raw_custody"]["objects"]
    ]
    require(
        expected_raw_versions == list(EXACT_RAW_VERSIONS)
        and authority.get("exact_g10_raw_versions") == expected_raw_versions,
        "S4_EXACT_RAW_VERSION_BINDINGS_INVALID",
    )
    claim = g10_receipt["remote_effects"]["execution_claim"]
    require(
        authority.get("exact_history_expectations")
        == {
            "checkpoint_key": frozen.CHECKPOINT_KEY,
            "checkpoint_versions": 28,
            "checkpoint_revisions": "0..27",
            "checkpoint_version_ids_predeclared": False,
            "checkpoint_version_ids_sealed_in_success_artifact": True,
            "checkpoint_validation": "EXACT_KEY_COUNT_REVISIONS_CANONICAL_CONTENT_METADATA_FROZEN_VECTORS_FINAL_TOKEN",
            "delete_markers": 0,
            "execution_claim_key": frozen.CLAIM_KEY,
            "execution_claim_version_id": claim["version_id"],
            "execution_claim_versions": 1,
            "raw_versions": 4,
        },
        "S4_EXACT_HISTORY_EXPECTATIONS_INVALID",
    )
    predecessor_core_binding = {
        "bytes": PREDECESSOR_CORE_BYTES,
        "git_blob_sha": PREDECESSOR_CORE_GIT_BLOB_SHA,
        "path": PREDECESSOR_CORE_PATH,
        "sha256": PREDECESSOR_CORE_SHA256,
    }
    corrected_core_binding = {
        "bytes": CORRECTED_CORE_BYTES,
        "git_blob_sha": CORRECTED_CORE_GIT_BLOB_SHA,
        "path": CORRECTED_CORE_PATH,
        "sha256": CORRECTED_CORE_SHA256,
    }
    require(
        authority.get("predecessor_frozen_core") == predecessor_core_binding
        and authority.get("corrected_forensic_core") == corrected_core_binding
        and bindings.get("corrected_core")
        == {"path": CORRECTED_CORE_PATH, **file_binding(CORRECTED_CORE_PATH)},
        "S4_FROZEN_ALGORITHM_BINDING_INVALID",
    )
    validate_corrected_core_delta()

    validate_frozen_base()


def validate_git_activation(activation: Mapping[str, Any], mode: str) -> dict[str, str]:
    expected = {
        "EVENT_ACTOR": ACTOR,
        "EVENT_TRIGGERING_ACTOR": ACTOR,
        "EVENT_REPOSITORY": REPOSITORY,
        "EVENT_REF": "refs/heads/" + BRANCH,
        "EVENT_FORCED": "false",
        "EVENT_HEAD_MESSAGE": _message_for(mode),
        "EVENT_RUN_ATTEMPT": "1",
    }
    for key, value in expected.items():
        require(os.environ.get(key) == value, "EVENT_ENV_" + key + "_MISMATCH")
    require(
        os.environ.get("GITHUB_ACTOR") == os.environ.get("EVENT_ACTOR")
        and os.environ.get("GITHUB_TRIGGERING_ACTOR")
        == os.environ.get("EVENT_TRIGGERING_ACTOR")
        and os.environ.get("GITHUB_REPOSITORY") == os.environ.get("EVENT_REPOSITORY")
        and os.environ.get("GITHUB_REF") == os.environ.get("EVENT_REF")
        and os.environ.get("GITHUB_RUN_ATTEMPT") == os.environ.get("EVENT_RUN_ATTEMPT")
        and os.environ.get("GITHUB_EVENT_NAME") == "push",
        "EVENT_ALIAS_OR_GITHUB_ENV_MISMATCH",
    )
    head = str(frozen._git_output("rev-parse", "HEAD"))
    before = os.environ.get("EVENT_BEFORE", "")
    after = os.environ.get("EVENT_AFTER", "")
    require(head == after == os.environ.get("GITHUB_SHA"), "EVENT_HEAD_MISMATCH")
    require(_single_parent(head) == before, "ACTIVATION_PARENT_MISMATCH")
    require(_raw_message(head) == _message_for(mode).encode(), "ACTIVATION_RAW_MESSAGE_MISMATCH")
    require(_diff_names(before, head) == {_activation_path(mode): "A"}, "ACTIVATION_DIFF_NOT_EXACT_ONE_FILE")

    preparation = str(activation.get("preparation_head_sha"))
    prep_tree = str(activation.get("preparation_tree_sha"))
    require(
        str(frozen._git_output("rev-parse", preparation + "^{tree}")) == prep_tree,
        "PREPARATION_TREE_MISMATCH",
    )
    require(_single_parent(preparation) == CURRENT_TERMINAL_HEAD, "PREPARATION_PARENT_MISMATCH")
    require(
        str(frozen._git_output("rev-parse", CURRENT_TERMINAL_HEAD + "^{tree}"))
        == CURRENT_TERMINAL_TREE,
        "CURRENT_TERMINAL_TREE_MISMATCH",
    )
    require(_raw_message(preparation) == PREP_MESSAGE.encode(), "PREPARATION_RAW_MESSAGE_MISMATCH")
    require(
        _diff_names(CURRENT_TERMINAL_HEAD, preparation)
        == {path: "A" for path in PREP_FILES},
        "PREPARATION_DIFF_NOT_EXACT_S4_FILES",
    )
    if mode == "PRECHECK":
        require(before == preparation, "PRECHECK_PARENT_NOT_PREPARATION")
    else:
        proof = activation["precheck_evidence"]
        precheck_head = str(proof["activation_head_sha"])
        pass_binding = proof["pass_receipt"]
        pass_head = str(pass_binding["commit_head_sha"])
        require(before == pass_head, "AUDIT_PARENT_NOT_PRECHECK_PASS_RECEIPT")
        require(
            _single_parent(pass_head) == precheck_head,
            "PRECHECK_PASS_PARENT_NOT_PRECHECK_ACTIVATION",
        )
        require(
            _raw_message(pass_head)
            == str(pass_binding["commit_message"]).encode(),
            "PRECHECK_PASS_COMMIT_MESSAGE_INVALID",
        )
        require(
            _diff_names(precheck_head, pass_head)
            == {PRECHECK_PASS_RECEIPT_PATH: "A"},
            "PRECHECK_PASS_DIFF_INVALID",
        )
        require(
            str(frozen._git_output("rev-parse", pass_head + "^{tree}"))
            == pass_binding["commit_tree_sha"],
            "PRECHECK_PASS_TREE_INVALID",
        )
        require(_single_parent(precheck_head) == preparation, "PRECHECK_ACTIVATION_PARENT_INVALID")
        require(_raw_message(precheck_head) == PRECHECK_MESSAGE.encode(), "PRECHECK_ACTIVATION_MESSAGE_INVALID")
        require(
            _diff_names(preparation, precheck_head)
            == {PRECHECK_ACTIVATION_PATH: "A"},
            "PRECHECK_ACTIVATION_DIFF_INVALID",
        )
        require(
            str(frozen._git_output("rev-parse", precheck_head + "^{tree}"))
            == proof["activation_tree_sha"],
            "PRECHECK_ACTIVATION_TREE_INVALID",
        )
    return {
        "activation_head_sha": head,
        "activation_tree_sha": str(frozen._git_output("rev-parse", "HEAD^{tree}")),
        "event_after": after,
        "event_before": before,
        "preparation_head_sha": preparation,
        "preparation_tree_sha": prep_tree,
    }


def _workflow_runs(token: str, head_sha: str, mode: str) -> list[dict[str, Any]]:
    workflow_id = urllib.parse.quote(_workflow_path(mode), safe="")
    query = (
        f"/repos/{REPOSITORY}/actions/workflows/{workflow_id}/runs"
        f"?branch={urllib.parse.quote(BRANCH, safe='')}&event=push&per_page=100"
        f"&head_sha={head_sha}"
    )
    value = frozen._github_json(token, query)
    rows = value.get("workflow_runs")
    require(
        isinstance(rows, list) and value.get("total_count") == len(rows),
        "WORKFLOW_RUN_LIST_INVALID",
    )
    return rows


def verify_precheck_remote(token: str, activation: Mapping[str, Any]) -> dict[str, Any]:
    proof = activation.get("precheck_evidence")
    require(isinstance(proof, dict), "PRECHECK_PROOF_MISSING")
    runs = _workflow_runs(token, str(proof["activation_head_sha"]), "PRECHECK")
    require(len(runs) == 1, "PRECHECK_RUN_CARDINALITY_INVALID")
    run = runs[0]
    require(
        run.get("id") == proof["run_id"]
        and run.get("run_attempt") == 1
        and run.get("status") == "completed"
        and run.get("conclusion") == "success"
        and run.get("head_sha") == proof["activation_head_sha"],
        "PRECHECK_RUN_REMOTE_RESULT_INVALID",
    )
    require(
        str(run.get("path", "")).split("@", 1)[0] == PRECHECK_WORKFLOW_PATH,
        "PRECHECK_RUN_WORKFLOW_PATH_INVALID",
    )
    jobs = frozen._github_json(
        token, f"/repos/{REPOSITORY}/actions/runs/{proof['run_id']}/jobs?per_page=100"
    )
    job_rows = jobs.get("jobs")
    require(
        isinstance(job_rows, list)
        and jobs.get("total_count") == 1
        and len(job_rows) == 1,
        "PRECHECK_JOB_CARDINALITY_INVALID",
    )
    job = job_rows[0]
    require(
        job.get("id") == proof["job_id"]
        and job.get("name") == "precheck"
        and job.get("status") == "completed"
        and job.get("conclusion") == "success"
        and job.get("head_sha") == proof["activation_head_sha"],
        "PRECHECK_JOB_REMOTE_RESULT_INVALID",
    )
    artifacts = frozen._github_json(
        token, f"/repos/{REPOSITORY}/actions/runs/{proof['run_id']}/artifacts"
    )
    rows = artifacts.get("artifacts")
    require(
        isinstance(rows, list)
        and artifacts.get("total_count") == 1
        and len(rows) == 1,
        "PRECHECK_ARTIFACT_CARDINALITY_INVALID",
    )
    artifact = rows[0]
    require(
        artifact.get("id") == proof["artifact_id"]
        and artifact.get("name") == proof["artifact_name"]
        and artifact.get("size_in_bytes") == proof["artifact_size_in_bytes"]
        and artifact.get("digest") == proof["artifact_digest"]
        and artifact.get("expired") is False,
        "PRECHECK_ARTIFACT_REMOTE_BINDING_INVALID",
    )
    return {
        "run_id": run["id"],
        "run_attempt": run["run_attempt"],
        "conclusion": run["conclusion"],
        "job_id": job["id"],
        "job_name": job["name"],
        "job_conclusion": job["conclusion"],
        "artifact_id": artifact["id"],
        "artifact_name": artifact["name"],
        "artifact_digest": artifact["digest"],
        "artifact_size_in_bytes": artifact["size_in_bytes"],
    }


def verify_remote_gate(
    token: str, activation: Mapping[str, Any], mode: str, phase: str
) -> dict[str, Any]:
    require(phase in {"before-aws", "before-artifact"}, "REMOTE_GATE_PHASE_INVALID")
    activation_head = os.environ.get("GITHUB_SHA", "")
    current_run_id = int(os.environ.get("GITHUB_RUN_ID", "0"))
    require(
        bool(re.fullmatch(r"[0-9a-f]{40}", activation_head)),
        "REMOTE_ACTIVATION_HEAD_INVALID",
    )
    ref = frozen._github_json(
        token,
        "/repos/AofSpds/asset-agent-asa/git/ref/heads/"
        + urllib.parse.quote(BRANCH, safe=""),
    )
    require(ref.get("object", {}).get("sha") == activation_head, "REMOTE_BRANCH_HEAD_MOVED")
    runs = _workflow_runs(token, activation_head, mode)
    require(len(runs) == 1, "CURRENT_ACTIVATION_RUN_CARDINALITY_INVALID")
    require(
        runs[0].get("id") == current_run_id
        and runs[0].get("run_attempt") == 1,
        "CURRENT_RUN_ID_ATTEMPT_INVALID",
    )
    current = frozen._github_json(
        token, f"/repos/{REPOSITORY}/actions/runs/{current_run_id}"
    )
    require(
        current.get("head_sha") == activation_head
        and current.get("event") == "push"
        and current.get("run_attempt") == 1
        and current.get("actor", {}).get("login") == ACTOR
        and current.get("triggering_actor", {}).get("login") == ACTOR
        and current.get("head_commit", {}).get("message") == _message_for(mode),
        "CURRENT_RUN_REMOTE_IDENTITY_INVALID",
    )
    active_ids: set[int] = set()
    for status in ("requested", "queued", "in_progress", "waiting", "pending"):
        rows = frozen._github_json(
            token,
            f"/repos/{REPOSITORY}/actions/runs"
            f"?branch={urllib.parse.quote(BRANCH, safe='')}&status={status}&per_page=100",
        ).get("workflow_runs", [])
        require(isinstance(rows, list), "ACTIVE_RUN_ROWS_INVALID")
        active_ids.update(int(row["id"]) for row in rows)
    require(active_ids == {current_run_id}, "DUPLICATE_OR_FOREIGN_ACTIVE_S4_RUN")
    preparation_runs = _workflow_runs(
        token, str(activation["preparation_head_sha"]), mode
    )
    require(preparation_runs == [], "PREPARATION_PUSH_TRIGGERED_S4_WORKFLOW")
    result = {
        "phase": phase,
        "mode": mode,
        "branch_head_sha": activation_head,
        "current_run_id": current_run_id,
    }
    if mode == "AUDIT":
        result["precheck"] = verify_precheck_remote(token, activation)
    return result


def _aws_json(service: str, operation: str, *args: str) -> dict[str, Any]:
    allowed = {
        ("sts", "get-caller-identity"),
        ("s3api", "get-bucket-location"),
        ("s3api", "get-bucket-versioning"),
    }
    require((service, operation) in allowed, "PRECHECK_AWS_CALL_NOT_ALLOWED")
    result = subprocess.run(
        ["aws", service, operation, *args, "--output", "json"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={
            **os.environ,
            "AWS_PAGER": "",
            "AWS_MAX_ATTEMPTS": "1",
            "AWS_RETRY_MODE": "standard",
        },
    )
    try:
        value = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise S4ForensicError("PRECHECK_AWS_JSON_INVALID") from exc
    require(isinstance(value, dict), "PRECHECK_AWS_JSON_ROOT_INVALID")
    return value


def _sensitive_values() -> list[bytes]:
    names = (
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY",
        "AWS_SESSION_TOKEN",
        "ACTIONS_ID_TOKEN_REQUEST_TOKEN",
        "GITHUB_TOKEN",
        "GH_TOKEN",
    )
    return [
        value.encode("utf-8")
        for name in names
        if len(value := os.environ.get(name, "")) >= 8
    ]


def _scan_bytes(data: bytes, sensitive: Sequence[bytes]) -> None:
    text = data.decode("utf-8")
    require(
        not any(pattern.search(text) for pattern in BANNED_TEXT_PATTERNS),
        "OUTPUT_SANITIZATION_PATTERN_FAILED",
    )
    require(
        not any(secret in data for secret in sensitive),
        "OUTPUT_SANITIZATION_SECRET_VALUE_FAILED",
    )


def _finalize_output(
    output_dir: pathlib.Path,
    expected_names: set[str],
    sensitive: Sequence[bytes],
) -> None:
    entries = list(output_dir.iterdir())
    require(
        all(
            path.is_file()
            and not path.is_symlink()
            and not path.name.startswith(".")
            for path in entries
        ),
        "OUTPUT_NONREGULAR_HIDDEN_OR_SYMLINK_ENTRY",
    )
    current = {path.name for path in entries}
    require(
        current == expected_names - {"exact-secret-scan.json", "sanitization-receipt.json"},
        "OUTPUT_PRE_SCAN_FILE_SET_INVALID",
    )
    pre_scan = {}
    for path in sorted(output_dir.iterdir()):
        data = path.read_bytes()
        _scan_bytes(data, sensitive)
        pre_scan[path.name] = {
            "bytes": len(data),
            "sha256": sha256_bytes(data),
        }
    scan = {
        "artifact": "M3TOP3_FINANCE_CA_PAGE100_G10_FORENSIC_S4_EXACT_SECRET_SCAN_v1.0",
        "state": "PASS",
        "target_file_names": sorted(expected_names),
        "files_scanned": pre_scan,
        "self_and_sanitization_scanned_after_receipt_creation": True,
        "pattern_classes": [
            "AUTHORIZATION_BEARER",
            "SIGNED_OR_AUTHENTICATED_URL",
            "AWS_CREDENTIAL_LABEL",
            "SERVICE_OR_API_KEY_QUERY",
            "OIDC_TOKEN_LABEL",
            "RAW_SENTINEL_LITERAL",
            "AWS_ACCESS_KEY_IDENTIFIER",
            "GITHUB_TOKEN_PREFIX",
            "JWT_SHAPE",
            "URL_USERINFO",
            "EXACT_RUNTIME_SECRET_VALUES",
        ],
        "secret_values_persisted": 0,
    }
    write_canonical_json(output_dir / "exact-secret-scan.json", scan)
    scan_data = (output_dir / "exact-secret-scan.json").read_bytes()
    _scan_bytes(scan_data, sensitive)
    files = {
        path.name: {
            "bytes": len(path.read_bytes()),
            "sha256": sha256_bytes(path.read_bytes()),
        }
        for path in sorted(output_dir.iterdir())
    }
    sanitization = {
        "artifact": "M3TOP3_FINANCE_CA_PAGE100_G10_FORENSIC_S4_SANITIZATION_RECEIPT_v1.0",
        "state": "PASS",
        "files": files,
        "raw_bodies_persisted": 0,
        "raw_issuer_values_persisted": 0,
        "credentials_or_tokens_persisted": 0,
        "authenticated_urls_persisted": 0,
        "provider_secret_values_persisted": 0,
        "self_hash_excluded_to_avoid_self_reference": True,
    }
    write_canonical_json(output_dir / "sanitization-receipt.json", sanitization)
    final = {path.name for path in output_dir.iterdir() if path.is_file()}
    require(final == expected_names, "OUTPUT_FINAL_FILE_SET_INVALID")
    for path in output_dir.iterdir():
        require(
            path.is_file() and not path.is_symlink() and not path.name.startswith("."),
            "OUTPUT_FINAL_NONREGULAR_HIDDEN_OR_SYMLINK_ENTRY",
        )
        _scan_bytes(path.read_bytes(), sensitive)


def _prepare_output_dir(path: pathlib.Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    require(
        path.is_dir() and not path.is_symlink() and not any(path.iterdir()),
        "OUTPUT_DIR_INVALID_OR_NOT_EMPTY",
    )


def run_precheck_aws(
    authority: Mapping[str, Any],
    activation: Mapping[str, Any],
    git_lineage: Mapping[str, str],
    output_dir: pathlib.Path,
) -> None:
    _prepare_output_dir(output_dir)
    caller = _aws_json("sts", "get-caller-identity", "--no-cli-pager")
    location = _aws_json(
        "s3api",
        "get-bucket-location",
        "--bucket",
        BUCKET,
        "--expected-bucket-owner",
        ACCOUNT_ID,
        "--no-cli-pager",
    )
    versioning = _aws_json(
        "s3api",
        "get-bucket-versioning",
        "--bucket",
        BUCKET,
        "--expected-bucket-owner",
        ACCOUNT_ID,
        "--no-cli-pager",
    )
    require(caller.get("Account") == ACCOUNT_ID, "PRECHECK_AWS_ACCOUNT_INVALID")
    expected_session_arn = (
        f"arn:aws:sts::{ACCOUNT_ID}:assumed-role/M3Top3GitHubOIDCRawWriter/"
        f"g10-readonly-forensic-s4-precheck-{os.environ.get('GITHUB_RUN_ID', '')}"
    )
    require(caller.get("Arn") == expected_session_arn, "PRECHECK_AWS_ROLE_SESSION_INVALID")
    require(location.get("LocationConstraint") == REGION, "PRECHECK_AWS_REGION_INVALID")
    require(versioning.get("Status") == "Enabled", "PRECHECK_BUCKET_VERSIONING_NOT_ENABLED")
    policy_binding = authority["execution_bindings"]["precheck_policy"]
    activation_readback = {
        "artifact": "M3TOP3_FINANCE_CA_PAGE100_G10_FORENSIC_S4_ACTIVATION_READBACK_v1.0",
        "state": "PASS",
        "mode": "PRECHECK",
        "generation_id": GENERATION_ID,
        "git_lineage": dict(git_lineage),
        "event_binding_keys": list(EVENT_KEYS),
        "predecessor_run_reused": False,
        "predecessor_activation_reused": False,
    }
    precheck_receipt = {
        "artifact": "M3TOP3_FINANCE_CA_PAGE100_G10_FORENSIC_S4_PRECHECK_RECEIPT_v1.0",
        "state": "PASS_ZERO_EFFECT_READ_ONLY_PRECHECK",
        "generation_id": GENERATION_ID,
        "runtime_lock_id": RUNTIME_LOCK_ID,
        "precheck_act_id": PRECHECK_ACT_ID,
        "audit_attempt_latch": dict(activation["audit_attempt_latch"]),
        "workflow": {
            "run_id": int(os.environ.get("GITHUB_RUN_ID", "0")),
            "run_attempt": int(os.environ.get("GITHUB_RUN_ATTEMPT", "0")),
            "job": os.environ.get("GITHUB_JOB", "UNKNOWN"),
            "head_sha": git_lineage["activation_head_sha"],
        },
        "current_owner_authorization": authority["current_owner_authorization"],
        "oidc_trust_binding": authority["aws_read_only_scope"]["oidc_trust_binding"],
        "account_id": ACCOUNT_ID,
        "region": REGION,
        "bucket": BUCKET,
        "assumed_role_arn_sha256": sha256_bytes(
            str(caller.get("Arn") or "").encode("utf-8")
        ),
        "session_policy": policy_binding,
        "authorized_effects": ZERO_EFFECTS,
        "observed_effects": {
            **ZERO_EFFECTS,
            "s3_data_reads": 0,
            "s3_bucket_metadata_reads": 2,
            "sts_identity_reads": 1,
        },
    }
    aws_receipt = {
        "artifact": "M3TOP3_FINANCE_CA_PAGE100_G10_FORENSIC_S4_AWS_READONLY_SESSION_RECEIPT_v1.0",
        "state": "PASS",
        "account_id": ACCOUNT_ID,
        "region": REGION,
        "bucket": BUCKET,
        "bucket_versioning": "Enabled",
        "caller_arn_sha256": sha256_bytes(
            str(caller.get("Arn") or "").encode("utf-8")
        ),
        "session_policy": policy_binding,
        "aws_cli_calls": {
            "sts:get-caller-identity": 1,
            "s3api:get-bucket-location": 1,
            "s3api:get-bucket-versioning": 1,
        },
        "s3_list_bucket_versions": 0,
        "s3_get_object_version": 0,
        "s3_put_object": 0,
        "s3_delete_object": 0,
    }
    terminal = {
        "artifact": "M3TOP3_FINANCE_CA_PAGE100_G10_FORENSIC_S4_PRECHECK_TERMINAL_SUMMARY_v1.0",
        "state": "PRECHECK_PASS_AUDIT_NOT_STARTED",
        "generation_id": GENERATION_ID,
        "audit_attempt_latch": dict(activation["audit_attempt_latch"]),
        "precheck_pass": True,
        "audit_started": False,
        "provider_calls": 0,
        "quota_reservations": 0,
        "s3_data_reads": 0,
        "s3_mutations": 0,
        "remote_custody_mutations": 0,
        "next": "FRESH_SEPARATE_AUDIT_ACTIVATION_AFTER_EXACT_RUN_ARTIFACT_READBACK",
    }
    write_canonical_json(output_dir / "precheck-receipt.json", precheck_receipt)
    write_canonical_json(output_dir / "activation-readback.json", activation_readback)
    write_canonical_json(output_dir / "aws-readonly-session-receipt.json", aws_receipt)
    write_canonical_json(output_dir / "terminal-summary.json", terminal)
    _finalize_output(
        output_dir,
        set(PRECHECK_OUTPUT_NAMES),
        _sensitive_values(),
    )


class BoundedCorrectedAwsReadOnlyS3(frozen.AwsReadOnlyS3):
    """Constrain the frozen evidence engine to the exact one-page read budget."""

    CALL_CAPS = {
        "sts:get-caller-identity": 1,
        "s3api:list-object-versions": 3,
        "s3api:get-object": 33,
    }
    last_instance: "BoundedCorrectedAwsReadOnlyS3 | None" = None

    def __init__(self, bucket: str) -> None:
        super().__init__(bucket)
        self._listed_prefixes: set[str] = set()
        self._listed_pairs: set[tuple[str, str]] = set()
        self._read_pairs: set[tuple[str, str]] = set()
        self.readbacks: list[dict[str, Any]] = []
        type(self).last_instance = self

    def aws_json(self, *args: str) -> dict[str, Any]:
        require(len(args) >= 2, "AUDIT_AWS_COMMAND_TOO_SHORT")
        name = args[0] + ":" + args[1]
        require(name in self.CALL_CAPS, "AUDIT_AWS_COMMAND_NOT_ALLOWED")
        require(
            self.call_counts.get(name, 0) < self.CALL_CAPS[name],
            "AUDIT_AWS_CALL_BUDGET_EXCEEDED_" + name,
        )
        result = super().aws_json(*args)
        if name == "sts:get-caller-identity":
            expected_arn = (
                f"arn:aws:sts::{ACCOUNT_ID}:assumed-role/M3Top3GitHubOIDCRawWriter/"
                f"g10-readonly-forensic-s4-audit-{os.environ.get('GITHUB_RUN_ID', '')}"
            )
            require(
                result.get("Account") == ACCOUNT_ID
                and result.get("Arn") == expected_arn,
                "AUDIT_AWS_ROLE_SESSION_INVALID",
            )
        return result

    def list_versions(self, prefix: str) -> dict[str, list[dict[str, Any]]]:
        require(
            prefix in {frozen.RAW_PREFIX, frozen.CONTROL_PREFIX, frozen.CLAIM_KEY},
            "AUDIT_LIST_PREFIX_NOT_ALLOWED",
        )
        require(prefix not in self._listed_prefixes, "AUDIT_LIST_PREFIX_REUSED")
        self._listed_prefixes.add(prefix)
        page = self.aws_json(
            "s3api",
            "list-object-versions",
            "--bucket",
            self.bucket,
            "--prefix",
            prefix,
            "--expected-bucket-owner",
            ACCOUNT_ID,
            "--max-keys",
            "1000",
            "--no-paginate",
        )
        require(page.get("IsTruncated", False) is False, "AUDIT_HISTORY_TRUNCATED")
        inventory = frozen.paginate_version_pages(
            lambda key_marker, version_marker: (
                page
                if key_marker is None and version_marker is None
                else (_ for _ in ()).throw(S4ForensicError("AUDIT_SECOND_LIST_PAGE_PROHIBITED"))
            ),
            prefix,
        )
        require(not inventory["delete_markers"], "AUDIT_DELETE_MARKER_PROHIBITED")
        pairs = {
            (str(row["Key"]), str(row["VersionId"]))
            for row in inventory["versions"]
        }
        require(
            len(pairs) == len(inventory["versions"]),
            "AUDIT_LIST_PAIR_DUPLICATE",
        )
        if prefix == frozen.RAW_PREFIX:
            require(
                pairs
                == {
                    (str(row["s3_object_key"]), str(row["version_id"]))
                    for row in EXACT_RAW_VERSIONS
                },
                "AUDIT_RAW_LIST_PAIR_SET_INVALID",
            )
        elif prefix == frozen.CONTROL_PREFIX:
            require(
                len(pairs) == 28
                and {key for key, _ in pairs} == {frozen.CHECKPOINT_KEY},
                "AUDIT_CHECKPOINT_LIST_PAIR_SET_INVALID",
            )
        else:
            require(
                pairs == {(frozen.CLAIM_KEY, EXACT_CLAIM_VERSION_ID)},
                "AUDIT_CLAIM_LIST_PAIR_SET_INVALID",
            )
        self._listed_pairs.update(pairs)
        return inventory

    def read_exact_version(
        self,
        key: str,
        version_id: str,
        destination: pathlib.Path,
        *,
        expected_content_type: str,
        expected_metadata_keys: frozenset[str],
    ) -> tuple[bytes, dict[str, Any]]:
        pair = (key, version_id)
        raw_pairs = {
            (str(row["s3_object_key"]), str(row["version_id"]))
            for row in EXACT_RAW_VERSIONS
        }
        require(pair in self._listed_pairs, "AUDIT_GET_PAIR_NOT_IN_EXACT_INVENTORY")
        require(
            pair in raw_pairs
            or pair == (frozen.CLAIM_KEY, EXACT_CLAIM_VERSION_ID)
            or (key == frozen.CHECKPOINT_KEY and pair in self._listed_pairs),
            "AUDIT_GET_PAIR_OUTSIDE_EXACT_ALLOWED_SET",
        )
        require(pair not in self._read_pairs, "AUDIT_GET_PAIR_REUSED")
        self._read_pairs.add(pair)
        body, metadata = super().read_exact_version(
            key,
            version_id,
            destination,
            expected_content_type=expected_content_type,
            expected_metadata_keys=expected_metadata_keys,
        )
        require(
            metadata.get("ServerSideEncryption") == "AES256",
            "AUDIT_READBACK_SSE_INVALID",
        )
        self.readbacks.append(
            {
                "bytes": len(body),
                "content_type": metadata.get("ContentType"),
                "etag": metadata.get("ETag"),
                "key": key,
                "server_side_encryption": "AES256",
                "sha256": sha256_bytes(body),
                "version_id": version_id,
            }
        )
        return body, metadata


def verify_precheck_archive(
    authority: Mapping[str, Any],
    activation: Mapping[str, Any],
    archive_path: pathlib.Path,
) -> tuple[dict[str, Any], bytes]:
    proof = activation.get("precheck_evidence")
    require(isinstance(proof, dict), "PRECHECK_ARCHIVE_PROOF_MISSING")
    require(
        archive_path.is_file() and not archive_path.is_symlink(),
        "PRECHECK_ARCHIVE_NOT_REGULAR_FILE",
    )
    archive = archive_path.read_bytes()
    require(
        len(archive) == proof["artifact_size_in_bytes"]
        and "sha256:" + sha256_bytes(archive) == proof["artifact_digest"],
        "PRECHECK_ARCHIVE_DIGEST_OR_SIZE_INVALID",
    )
    try:
        with zipfile.ZipFile(io.BytesIO(archive), "r") as bundle:
            infos = bundle.infolist()
            require(
                {info.filename for info in infos} == set(PRECHECK_OUTPUT_NAMES)
                and len(infos) == len(PRECHECK_OUTPUT_NAMES),
                "PRECHECK_ARCHIVE_FILE_SET_INVALID",
            )
            require(
                all(
                    not info.is_dir()
                    and "/" not in info.filename
                    and "\\" not in info.filename
                    and not info.filename.startswith(".")
                    and info.file_size <= 1_000_000
                    and not (info.flag_bits & 0x1)
                    for info in infos
                ),
                "PRECHECK_ARCHIVE_ENTRY_INVALID",
            )
            files = {info.filename: bundle.read(info) for info in infos}
    except (zipfile.BadZipFile, RuntimeError) as exc:
        raise S4ForensicError("PRECHECK_ARCHIVE_ZIP_INVALID") from exc
    for data in files.values():
        _scan_bytes(data, _sensitive_values())
    parsed = {
        name: parse_canonical_json_bytes(data, "PRECHECK_ARCHIVE_JSON")
        for name, data in files.items()
    }
    receipt = parsed["precheck-receipt.json"]
    expected_role_arn = (
        f"arn:aws:sts::{ACCOUNT_ID}:assumed-role/M3Top3GitHubOIDCRawWriter/"
        f"g10-readonly-forensic-s4-precheck-{proof['run_id']}"
    )
    expected_role_hash = sha256_bytes(expected_role_arn.encode("utf-8"))
    require(
        receipt.get("artifact")
        == "M3TOP3_FINANCE_CA_PAGE100_G10_FORENSIC_S4_PRECHECK_RECEIPT_v1.0"
        and receipt.get("state") == "PASS_ZERO_EFFECT_READ_ONLY_PRECHECK"
        and receipt.get("generation_id") == GENERATION_ID
        and receipt.get("runtime_lock_id") == RUNTIME_LOCK_ID
        and receipt.get("precheck_act_id") == PRECHECK_ACT_ID
        and receipt.get("audit_attempt_latch") == _attempt_latch("PRECHECK")
        and receipt.get("workflow", {}).get("run_id") == proof["run_id"]
        and receipt.get("workflow", {}).get("run_attempt") == 1
        and receipt.get("workflow", {}).get("head_sha")
        == proof["activation_head_sha"]
        and receipt.get("current_owner_authorization")
        == authority["current_owner_authorization"]
        and receipt.get("oidc_trust_binding")
        == authority["aws_read_only_scope"]["oidc_trust_binding"]
        and receipt.get("account_id") == ACCOUNT_ID
        and receipt.get("region") == REGION
        and receipt.get("bucket") == BUCKET
        and receipt.get("assumed_role_arn_sha256") == expected_role_hash
        and receipt.get("session_policy")
        == authority["execution_bindings"]["precheck_policy"],
        "PRECHECK_ARCHIVE_RECEIPT_CONTENT_INVALID",
    )
    require(
        receipt.get("observed_effects")
        == {
            **ZERO_EFFECTS,
            "s3_data_reads": 0,
            "s3_bucket_metadata_reads": 2,
            "sts_identity_reads": 1,
        },
        "PRECHECK_ARCHIVE_EFFECTS_INVALID",
    )
    require(
        parsed["activation-readback.json"]
        == {
            "artifact": "M3TOP3_FINANCE_CA_PAGE100_G10_FORENSIC_S4_ACTIVATION_READBACK_v1.0",
            "event_binding_keys": list(EVENT_KEYS),
            "generation_id": GENERATION_ID,
            "git_lineage": parsed["activation-readback.json"].get("git_lineage"),
            "mode": "PRECHECK",
            "predecessor_activation_reused": False,
            "predecessor_run_reused": False,
            "state": "PASS",
        }
        and parsed["activation-readback.json"].get("git_lineage", {}).get(
            "activation_head_sha"
        )
        == proof["activation_head_sha"]
        and parsed["terminal-summary.json"].get("state")
        == "PRECHECK_PASS_AUDIT_NOT_STARTED",
        "PRECHECK_ARCHIVE_LINEAGE_OR_TERMINAL_INVALID",
    )
    require(
        parsed["terminal-summary.json"].get("audit_attempt_latch")
        == _attempt_latch("PRECHECK"),
        "PRECHECK_ARCHIVE_ATTEMPT_LATCH_INVALID",
    )
    aws_receipt = parsed["aws-readonly-session-receipt.json"]
    require(
        aws_receipt
        == {
            "account_id": ACCOUNT_ID,
            "artifact": "M3TOP3_FINANCE_CA_PAGE100_G10_FORENSIC_S4_AWS_READONLY_SESSION_RECEIPT_v1.0",
            "aws_cli_calls": {
                "s3api:get-bucket-location": 1,
                "s3api:get-bucket-versioning": 1,
                "sts:get-caller-identity": 1,
            },
            "bucket": BUCKET,
            "bucket_versioning": "Enabled",
            "caller_arn_sha256": expected_role_hash,
            "s3_delete_object": 0,
            "s3_get_object_version": 0,
            "s3_list_bucket_versions": 0,
            "s3_put_object": 0,
            "session_policy": authority["execution_bindings"]["precheck_policy"],
            "state": "PASS",
            "region": REGION,
        },
        "PRECHECK_ARCHIVE_AWS_RECEIPT_INVALID",
    )
    scan = parsed["exact-secret-scan.json"]
    require(
        scan.get("state") == "PASS"
        and scan.get("target_file_names") == sorted(PRECHECK_OUTPUT_NAMES),
        "PRECHECK_ARCHIVE_SECRET_SCAN_INVALID",
    )
    sanitization = parsed["sanitization-receipt.json"]
    expected_bindings = {
        name: {"bytes": len(data), "sha256": sha256_bytes(data)}
        for name, data in files.items()
        if name != "sanitization-receipt.json"
    }
    require(
        sanitization.get("state") == "PASS"
        and sanitization.get("files") == expected_bindings,
        "PRECHECK_ARCHIVE_SANITIZATION_BINDINGS_INVALID",
    )
    pass_receipt = load_canonical_json(ROOT / PRECHECK_PASS_RECEIPT_PATH)
    require(
        pass_receipt.get("precheck_receipt_file")
        == {
            "bytes": len(files["precheck-receipt.json"]),
            "filename": "precheck-receipt.json",
            "sha256": sha256_bytes(files["precheck-receipt.json"]),
        },
        "PRECHECK_ARCHIVE_GIT_RECEIPT_BINDING_INVALID",
    )
    return (
        {
            "artifact_digest": proof["artifact_digest"],
            "artifact_id": proof["artifact_id"],
            "artifact_name": proof["artifact_name"],
            "artifact_size_in_bytes": proof["artifact_size_in_bytes"],
            "job_id": proof["job_id"],
            "run_attempt": proof["run_attempt"],
            "run_id": proof["run_id"],
        },
        files["precheck-receipt.json"],
    )


def _sorted_readbacks(rows: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        (dict(row) for row in rows),
        key=lambda row: (str(row.get("key", "")), str(row.get("version_id", ""))),
    )


def validate_version_history_projection(
    histories: Mapping[str, Any], *, require_zero_delete_markers: bool
) -> dict[str, int]:
    """Validate the governed namespace and counts used by the production path."""
    require(set(histories) == VERSION_HISTORY_KEYS, "AUDIT_VERSION_HISTORY_KEY_SET_INVALID")
    counts = histories.get("all_delete_marker_counts")
    if isinstance(counts, dict) and set(counts) == {"raw", "control", "claim"}:
        raise S4ForensicError("CONTROL_LOOP_DETECTED")
    require(
        isinstance(counts, dict) and set(counts) == DELETE_MARKER_COUNT_KEYS,
        "AUDIT_DELETE_MARKER_COUNT_KEY_SET_INVALID",
    )
    require("claim" not in histories and "claim" not in counts, "AUDIT_OBSOLETE_CLAIM_KEY_PRESENT")
    for name in DELETE_MARKER_COUNT_KEYS:
        inventory = histories.get(name)
        require(isinstance(inventory, dict), "AUDIT_VERSION_HISTORY_INVENTORY_INVALID")
        markers = inventory.get("delete_markers")
        require(isinstance(markers, list), "AUDIT_DELETE_MARKER_LIST_INVALID")
        require(
            type(counts[name]) is int
            and counts[name] >= 0
            and counts[name] == len(markers),
            "AUDIT_DELETE_MARKER_COUNT_INVALID",
        )
    if require_zero_delete_markers:
        require(
            counts == {"control": 0, "execution_claim": 0, "raw": 0},
            "AUDIT_DELETE_MARKER_PRESENT",
        )
    return {name: int(counts[name]) for name in sorted(DELETE_MARKER_COUNT_KEYS)}


def emit_complete_audit_artifact(
    authority: Mapping[str, Any],
    activation: Mapping[str, Any],
    git_lineage: Mapping[str, str],
    output_dir: pathlib.Path,
    precheck_binding: Mapping[str, Any],
    precheck_receipt_bytes: bytes,
    frozen_evidence: Mapping[str, Any],
    corrected_core_run_receipt: Mapping[str, Any],
    raw_readbacks: Sequence[Mapping[str, Any]],
    checkpoint_readbacks: Sequence[Mapping[str, Any]],
    claim_readbacks: Sequence[Mapping[str, Any]],
) -> None:
    """Serialize the complete production audit artifact from validated evidence."""
    precheck_receipt = parse_canonical_json_bytes(
        precheck_receipt_bytes, "AUDIT_PRECHECK_RECEIPT"
    )
    require(
        precheck_receipt.get("artifact")
        == "M3TOP3_FINANCE_CA_PAGE100_G10_FORENSIC_S4_PRECHECK_RECEIPT_v1.0"
        and precheck_receipt.get("state") == "PASS_ZERO_EFFECT_READ_ONLY_PRECHECK"
        and precheck_receipt.get("generation_id") == GENERATION_ID
        and precheck_receipt.get("runtime_lock_id") == RUNTIME_LOCK_ID
        and precheck_receipt.get("precheck_act_id") == PRECHECK_ACT_ID
        and precheck_receipt.get("audit_attempt_latch") == _attempt_latch("PRECHECK")
        and precheck_receipt.get("current_owner_authorization")
        == authority["current_owner_authorization"],
        "AUDIT_PRECHECK_RECEIPT_BINDING_INVALID",
    )
    histories = frozen_evidence["version_histories"]
    core_evidence_bytes = canonical_json_bytes(dict(frozen_evidence))
    core_run_receipt_bytes = canonical_json_bytes(dict(corrected_core_run_receipt))
    core_evidence_binding = {
        "bytes": len(core_evidence_bytes),
        "filename": "g10-readonly-forensic-evidence.json",
        "sha256": sha256_bytes(core_evidence_bytes),
    }
    require(
        corrected_core_run_receipt.get("evidence") == core_evidence_binding,
        "AUDIT_CORE_EVIDENCE_BINDING_INVALID",
    )
    corrected_core_output_bindings = {
        "evidence": core_evidence_binding,
        "run_receipt": {
            "bytes": len(core_run_receipt_bytes),
            "filename": "g10-readonly-forensic-run-receipt.json",
            "sha256": sha256_bytes(core_run_receipt_bytes),
        },
    }
    delete_marker_counts = validate_version_history_projection(
        histories, require_zero_delete_markers=True
    )
    effects = frozen_evidence["effect_classification"]
    replay = frozen_evidence["issuer_identity_replay"]
    require(
        frozen_evidence["aws_read_only_session"]["aws_cli_read_call_counts"]
        == {
            "s3api:get-object": 33,
            "s3api:list-object-versions": 3,
            "sts:get-caller-identity": 1,
        },
        "AUDIT_EXACT_AWS_READ_CALL_BUDGET_INVALID",
    )
    require(
        len(histories["raw"]["versions"]) == 4
        and len(histories["control"]["versions"]) == 28
        and len(histories["execution_claim"]["versions"]) == 1,
        "AUDIT_VERSION_HISTORY_INVALID",
    )
    require(
        len(raw_readbacks) == 4
        and len(checkpoint_readbacks) == 28
        and len(claim_readbacks) == 1,
        "AUDIT_READBACK_PARTITION_INVALID",
    )
    require(
        replay.get("rows_checked") == 40
        and replay.get("match_rows") == 38
        and replay.get("conflict_rows") == 2
        and replay.get("missing_rows") == 0,
        "AUDIT_CONFLICT_REPRODUCTION_INVALID",
    )
    require(
        effects.get("finance_provider_api_calls") == 0
        and effects.get("quota_reservations") == 0
        and effects.get("s3_put_object_calls") == 0
        and effects.get("s3_delete_object_calls") == 0
        and effects.get("remote_custody_mutations") == 0,
        "AUDIT_ZERO_EFFECT_CONTRACT_FAILED",
    )
    require(
        activation.get("audit_attempt_latch") == _attempt_latch("AUDIT"),
        "AUDIT_ATTEMPT_NOT_EXACTLY_LATCHED",
    )
    run_id = int(os.environ.get("GITHUB_RUN_ID", "0"))
    run_attempt = int(os.environ.get("GITHUB_RUN_ATTEMPT", "0"))
    job_name = os.environ.get("GITHUB_JOB", "UNKNOWN")
    require(
        run_id > 0 and run_attempt == 1 and job_name == "audit",
        "AUDIT_RUNTIME_IDENTITY_INVALID",
    )
    (output_dir / "precheck-receipt.json").write_bytes(precheck_receipt_bytes)
    write_canonical_json(
        output_dir / "activation-readback.json",
        {
            "artifact": "M3TOP3_FINANCE_CA_PAGE100_G10_FORENSIC_S4_ACTIVATION_READBACK_v1.0",
            "state": "PASS",
            "mode": "AUDIT",
            "generation_id": GENERATION_ID,
            "git_lineage": dict(git_lineage),
            "event_binding_keys": list(EVENT_KEYS),
            "precheck_artifact_binding": dict(precheck_binding),
            "predecessor_run_reused": False,
            "predecessor_activation_reused": False,
            "audit_attempt_latch": dict(activation["audit_attempt_latch"]),
        },
    )
    write_canonical_json(
        output_dir / "aws-readonly-session-receipt.json",
        {
            "artifact": "M3TOP3_FINANCE_CA_PAGE100_G10_FORENSIC_S4_AWS_READONLY_SESSION_RECEIPT_v1.0",
            "state": "PASS",
            "account_id": ACCOUNT_ID,
            "region": REGION,
            "bucket": BUCKET,
            "caller_arn_sha256": frozen_evidence["aws_read_only_session"][
                "caller_arn_sha256"
            ],
            "oidc_trust_binding": authority["aws_read_only_scope"][
                "oidc_trust_binding"
            ],
            "session_policy": authority["execution_bindings"]["audit_policy"],
            "aws_cli_read_call_counts": frozen_evidence["aws_read_only_session"][
                "aws_cli_read_call_counts"
            ],
            "exact_version_readbacks_sse_aes256": 33,
            "s3_mutation_calls": 0,
            "provider_calls": 0,
            "quota_reservations": 0,
        },
    )
    write_canonical_json(
        output_dir / "raw-version-manifest.json",
        {
            "artifact": "M3TOP3_FINANCE_CA_PAGE100_G10_FORENSIC_S4_RAW_VERSION_MANIFEST_v1.0",
            "state": "EXACT_FOUR_VERSIONS_READ",
            "versions": histories["raw"]["versions"],
            "delete_markers": histories["raw"]["delete_markers"],
            "readbacks": [dict(row) for row in raw_readbacks],
            "exact_version_get_count": effects["raw_exact_version_gets"],
        },
    )
    write_canonical_json(
        output_dir / "checkpoint-version-history.json",
        {
            "artifact": "M3TOP3_FINANCE_CA_PAGE100_G10_FORENSIC_S4_CHECKPOINT_VERSION_HISTORY_v1.0",
            "state": "EXACT_REVISIONS_ZERO_THROUGH_27_READ",
            "inventory": histories["control"],
            "checkpoint_versions": frozen_evidence["checkpoint_versions"],
            "readbacks": [dict(row) for row in checkpoint_readbacks],
            "exact_version_get_count": effects["checkpoint_exact_version_gets"],
            "all_28_version_ids_sealed": True,
        },
    )
    write_canonical_json(
        output_dir / "execution-claim-version-history.json",
        {
            "artifact": "M3TOP3_FINANCE_CA_PAGE100_G10_FORENSIC_S4_EXECUTION_CLAIM_VERSION_HISTORY_v1.0",
            "state": "EXACT_ONE_VERSION_READ",
            "inventory": histories["execution_claim"],
            "readbacks": [dict(row) for row in claim_readbacks],
            "exact_version_get_count": effects["execution_claim_exact_version_gets"],
        },
    )
    write_canonical_json(
        output_dir / "issuer-conflict-reproduction.json",
        {
            "artifact": "M3TOP3_FINANCE_CA_PAGE100_G10_FORENSIC_S4_ISSUER_CONFLICT_REPRODUCTION_v1.0",
            "state": "EXACT_CONFLICT_REPRODUCED",
            "corrected_forensic_core": authority["corrected_forensic_core"],
            "corrected_core_output_bindings": corrected_core_output_bindings,
            "result": replay,
            "raw_issuer_values_persisted": False,
            "issuer_resolution_performed": False,
        },
    )
    write_canonical_json(
        output_dir / "terminal-summary.json",
        {
            "artifact": "M3TOP3_FINANCE_CA_PAGE100_G10_FORENSIC_S4_TERMINAL_SUMMARY_v1.0",
            "state": "TERMINAL_SUCCESS_READ_ONLY_FORENSIC_OBJECTIVE_COMPLETE",
            "generation_id": GENERATION_ID,
            "runtime_lock_id": RUNTIME_LOCK_ID,
            "audit_act_id": AUDIT_ACT_ID,
            "audit_attempt_latch": dict(activation["audit_attempt_latch"]),
            "workflow": {
                "run_id": run_id,
                "run_attempt": run_attempt,
                "job": job_name,
                "head_sha": git_lineage["activation_head_sha"],
            },
            "findings": {
                "checkpoint_revisions": "0..27",
                "checkpoint_versions": 28,
                "checkpoint_version_ids_sealed": 28,
                "obsolete_claim_key_absent": True,
                "conflict_rows_exactly_identified_hash_only": True,
                "delete_marker_counts": delete_marker_counts,
                "execution_claim_versions": 1,
                "historical_existing_versions_read": 33,
                "issuer_identity_conflicts": 2,
                "raw_versions": 4,
                "version_history_keys": sorted(VERSION_HISTORY_KEYS),
            },
            "effects": effects,
            "read_effect_counts": frozen_evidence["aws_read_only_session"][
                "aws_cli_read_call_counts"
            ],
            "write_effect_counts": {
                "finance_provider_api_calls": 0,
                "quota_reservations": 0,
                "remote_custody_mutations": 0,
                "s3_delete_object_calls": 0,
                "s3_put_object_calls": 0,
            },
            "claim_ceiling": frozen_evidence["claim_ceiling"],
            "current_owner_authorization": authority["current_owner_authorization"],
            "corrected_forensic_core": authority["corrected_forensic_core"],
            "corrected_core_output_bindings": corrected_core_output_bindings,
            "owner_action_required": True,
            "next": "OWNER_REVIEW_NO_AUTOMATIC_ISSUER_RESOLUTION_G10_G11_PIT_NORMALIZATION_PROMOTION_RELEASE",
        },
    )
    _finalize_output(output_dir, set(AUDIT_OUTPUT_NAMES), _sensitive_values())


def run_audit_projection(
    authority: Mapping[str, Any],
    activation: Mapping[str, Any],
    git_lineage: Mapping[str, str],
    output_dir: pathlib.Path,
    precheck_binding: Mapping[str, Any],
    precheck_receipt_bytes: bytes,
) -> None:
    _prepare_output_dir(output_dir)
    old_authority, old_activation, receipt, predecessor, _ = validate_frozen_base()
    with tempfile.TemporaryDirectory(prefix="g10-s4-corrected-core-") as temp_name:
        temp = pathlib.Path(temp_name)
        BoundedCorrectedAwsReadOnlyS3.last_instance = None
        previous_client = frozen.AwsReadOnlyS3
        frozen.AwsReadOnlyS3 = BoundedCorrectedAwsReadOnlyS3
        try:
            frozen_receipt = frozen.run_audit(
                old_authority,
                old_activation,
                receipt,
                predecessor,
                git_lineage,
                temp,
            )
        finally:
            frozen.AwsReadOnlyS3 = previous_client
        audit_client = BoundedCorrectedAwsReadOnlyS3.last_instance
        frozen_evidence = load_canonical_json(
            temp / "g10-readonly-forensic-evidence.json"
        )
        frozen_run_receipt = load_canonical_json(
            temp / "g10-readonly-forensic-run-receipt.json"
        )
        frozen_sanitization = load_canonical_json(temp / "sanitization-receipt.json")
        frozen_evidence_bytes = canonical_json_bytes(frozen_evidence)
        frozen_run_receipt_bytes = canonical_json_bytes(frozen_run_receipt)
    require(frozen_receipt == frozen_run_receipt, "AUDIT_CORE_RETURN_RECEIPT_MISMATCH")
    require(
        frozen_run_receipt.get("evidence")
        == {
            "bytes": len(frozen_evidence_bytes),
            "filename": "g10-readonly-forensic-evidence.json",
            "sha256": sha256_bytes(frozen_evidence_bytes),
        },
        "AUDIT_CORE_EVIDENCE_BINDING_INVALID",
    )
    require(
        frozen_sanitization.get("state") == "PASS"
        and frozen_sanitization.get("files")
        == {
            "g10-readonly-forensic-evidence.json": {
                "bytes": len(frozen_evidence_bytes),
                "sha256": sha256_bytes(frozen_evidence_bytes),
            },
            "g10-readonly-forensic-run-receipt.json": {
                "bytes": len(frozen_run_receipt_bytes),
                "sha256": sha256_bytes(frozen_run_receipt_bytes),
            },
        },
        "AUDIT_CORE_SANITIZATION_BINDING_INVALID",
    )
    require(
        audit_client is not None
        and len(audit_client.readbacks) == 33
        and audit_client._listed_prefixes
        == {frozen.RAW_PREFIX, frozen.CONTROL_PREFIX, frozen.CLAIM_KEY}
        and audit_client._read_pairs == audit_client._listed_pairs
        and len(audit_client._listed_pairs) == 33
        and all(
            row["server_side_encryption"] == "AES256"
            for row in audit_client.readbacks
        ),
        "AUDIT_EXACT_SSE_READBACK_COUNT_INVALID",
    )
    raw_readbacks = _sorted_readbacks(
        row
        for row in audit_client.readbacks
        if row["key"].startswith(frozen.RAW_PREFIX)
    )
    checkpoint_readbacks = _sorted_readbacks(
        row for row in audit_client.readbacks if row["key"] == frozen.CHECKPOINT_KEY
    )
    claim_readbacks = _sorted_readbacks(
        row for row in audit_client.readbacks if row["key"] == frozen.CLAIM_KEY
    )
    expected_raw_by_pair = {
        (row["s3_object_key"], row["version_id"]): row
        for row in EXACT_RAW_VERSIONS
    }
    require(
        {(row["key"], row["version_id"]) for row in raw_readbacks}
        == set(expected_raw_by_pair),
        "AUDIT_RAW_READBACK_PAIR_SET_INVALID",
    )
    raw_readbacks = _sorted_readbacks(
        {
            **row,
            "page_no": expected_raw_by_pair[(row["key"], row["version_id"])][
                "page_no"
            ],
        }
        for row in raw_readbacks
    )
    revision_by_version = {
        row["version_id"]: row["revision"]
        for row in frozen_evidence["checkpoint_versions"]
    }
    require(
        {row["version_id"] for row in checkpoint_readbacks}
        == set(revision_by_version),
        "AUDIT_CHECKPOINT_READBACK_VERSION_SET_INVALID",
    )
    checkpoint_readbacks = _sorted_readbacks(
        {**row, "revision": revision_by_version[row["version_id"]]}
        for row in checkpoint_readbacks
    )
    require(
        len(raw_readbacks) == 4
        and len(checkpoint_readbacks) == 28
        and len(claim_readbacks) == 1,
        "AUDIT_SSE_READBACK_PARTITION_INVALID",
    )
    require(
        frozen_evidence["aws_read_only_session"]["aws_cli_read_call_counts"]
        == {
            "s3api:get-object": 33,
            "s3api:list-object-versions": 3,
            "sts:get-caller-identity": 1,
        },
        "AUDIT_EXACT_AWS_READ_CALL_BUDGET_INVALID",
    )
    effects = frozen_evidence["effect_classification"]
    require(
        effects["finance_provider_api_calls"] == 0
        and effects["quota_reservations"] == 0
        and effects["s3_put_object_calls"] == 0
        and effects["s3_delete_object_calls"] == 0
        and effects["remote_custody_mutations"] == 0,
        "AUDIT_ZERO_EFFECT_CONTRACT_FAILED",
    )
    replay = frozen_evidence["issuer_identity_replay"]
    require(
        replay["rows_checked"] == 40
        and replay["match_rows"] == 38
        and replay["conflict_rows"] == 2
        and replay["missing_rows"] == 0,
        "AUDIT_CONFLICT_REPRODUCTION_INVALID",
    )
    histories = frozen_evidence["version_histories"]
    delete_marker_counts = validate_version_history_projection(
        histories, require_zero_delete_markers=True
    )
    require(
        len(histories["raw"]["versions"]) == 4
        and len(histories["control"]["versions"]) == 28
        and len(histories["execution_claim"]["versions"]) == 1
        and delete_marker_counts
        == {"control": 0, "execution_claim": 0, "raw": 0},
        "AUDIT_VERSION_HISTORY_INVALID",
    )

    emit_complete_audit_artifact(
        authority,
        activation,
        git_lineage,
        output_dir,
        precheck_binding,
        precheck_receipt_bytes,
        frozen_evidence,
        frozen_run_receipt,
        raw_readbacks,
        checkpoint_readbacks,
        claim_readbacks,
    )


def _load_s4(
    authority_path: str,
    activation_path: str,
    manifest_path: str,
    policy_path: str,
    mode: str,
) -> tuple[dict[str, Any], ...]:
    authority = load_canonical_json(pathlib.Path(authority_path))
    activation = load_canonical_json(pathlib.Path(activation_path))
    manifest = load_canonical_json(pathlib.Path(manifest_path))
    policy = load_canonical_json(pathlib.Path(policy_path))
    validate_s4_contract(authority, activation, manifest, policy, mode)
    return authority, activation, manifest, policy


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    preflight = subparsers.add_parser("preflight")
    preflight.add_argument("--mode", choices=("PRECHECK", "AUDIT"), required=True)
    preflight.add_argument("--authority", required=True)
    preflight.add_argument("--activation", required=True)
    preflight.add_argument("--manifest", required=True)
    preflight.add_argument("--policy", required=True)
    preflight.add_argument("--verify-precheck", action="store_true")

    remote = subparsers.add_parser("remote-gate")
    remote.add_argument("--mode", choices=("PRECHECK", "AUDIT"), required=True)
    remote.add_argument("--activation", required=True)
    remote.add_argument("--phase", choices=("before-aws", "before-artifact"), required=True)

    aws = subparsers.add_parser("precheck-aws")
    aws.add_argument("--authority", required=True)
    aws.add_argument("--activation", required=True)
    aws.add_argument("--manifest", required=True)
    aws.add_argument("--policy", required=True)
    aws.add_argument("--output-dir", required=True)

    artifact = subparsers.add_parser("verify-precheck-archive")
    artifact.add_argument("--authority", required=True)
    artifact.add_argument("--activation", required=True)
    artifact.add_argument("--manifest", required=True)
    artifact.add_argument("--policy", required=True)
    artifact.add_argument("--precheck-archive", required=True)

    audit = subparsers.add_parser("audit")
    audit.add_argument("--authority", required=True)
    audit.add_argument("--activation", required=True)
    audit.add_argument("--manifest", required=True)
    audit.add_argument("--policy", required=True)
    audit.add_argument("--output-dir", required=True)
    audit.add_argument("--precheck-archive", required=True)

    args = parser.parse_args(argv)
    if args.command == "remote-gate":
        activation = load_canonical_json(pathlib.Path(args.activation))
        result = verify_remote_gate(
            os.environ.get("GITHUB_TOKEN", ""),
            activation,
            args.mode,
            args.phase,
        )
        print(json.dumps(result, sort_keys=True, separators=(",", ":")))
        return 0

    mode = (
        "PRECHECK"
        if args.command == "precheck-aws"
        else "AUDIT"
        if args.command in {"audit", "verify-precheck-archive"}
        else args.mode
    )
    authority, activation, _, _ = _load_s4(
        args.authority,
        args.activation,
        args.manifest,
        args.policy,
        mode,
    )
    if args.command == "verify-precheck-archive":
        proof, _ = verify_precheck_archive(
            authority, activation, pathlib.Path(args.precheck_archive)
        )
        print(
            json.dumps(
                {"state": "PASS", "mode": "AUDIT", **proof},
                sort_keys=True,
                separators=(",", ":"),
            )
        )
        return 0
    git_lineage = validate_git_activation(activation, mode)

    if args.command == "preflight":
        if args.verify_precheck:
            require(mode == "AUDIT", "PRECHECK_PROOF_ONLY_FOR_AUDIT")
            verify_precheck_remote(os.environ.get("GITHUB_TOKEN", ""), activation)
        print(
            json.dumps(
                {"state": "PASS", "mode": mode, **git_lineage},
                sort_keys=True,
                separators=(",", ":"),
            )
        )
        return 0

    if args.command == "precheck-aws":
        run_precheck_aws(
            authority,
            activation,
            git_lineage,
            pathlib.Path(args.output_dir),
        )
        print("G10_READ_ONLY_FORENSIC_S4_PRECHECK_COMPLETE")
        return 0

    precheck_binding, precheck_receipt_bytes = verify_precheck_archive(
        authority, activation, pathlib.Path(args.precheck_archive)
    )
    run_audit_projection(
        authority,
        activation,
        git_lineage,
        pathlib.Path(args.output_dir),
        precheck_binding,
        precheck_receipt_bytes,
    )
    print("G10_READ_ONLY_FORENSIC_S4_AUDIT_COMPLETE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
