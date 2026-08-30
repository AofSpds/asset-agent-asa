#!/usr/bin/env python3
"""Single-attempt, read-only G10 Finance forensic audit.

This program deliberately has no Finance/provider client and no S3 mutation
primitive. Its AWS command allow-list is limited to caller identity, exact
version enumeration, and exact-version reads.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import re
import subprocess
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections.abc import Callable, Iterable, Mapping, Sequence
from typing import Any


REPOSITORY = "AofSpds/asset-agent-asa"
BRANCH = "aaa-pmo-public-data-g2-g3-source-admission-v1-20260828"
ACTOR = "AofSpds"
ACCOUNT_ID = "956315449338"
REGION = "ap-northeast-2"
BUCKET = "semi-data-plane-aofspds-20260815"
BASE_RECEIPT_COMMIT = "5a76699a9324e049704863e74be38195cccc70f0"
BASE_RECEIPT_TREE = "e60b19ee76b8eb109888d8918af2d89d20664d9a"
PREP_MESSAGE = "Prepare G10 read-only issuer and S3 forensic audit v1.0"
ACTIVATION_MESSAGE = "Arm G10 read-only issuer and S3 forensic audit once v1.0"
OWNER_COMMENT_ID = 5466200427
OWNER_COMMENT_CREATED_UPDATED_UTC = "2026-08-30T02:18:42Z"
OWNER_COMMENT_BODY_SHA256 = (
    "918d1712759079046ce1bb3d41e41a1a64b3c5ae296b66d34b2b4a38fee42356"
)
OWNER_COMMENT_URL = (
    "https://github.com/AofSpds/asset-agent-asa/issues/49#issuecomment-5466200427"
)
TERMINAL_RECEIPT_PATH = (
    "control/m3top3/public-data-source-admission/v1.0/"
    "M3TOP3_FINANCE_CA_PAGE100_G10_LIVE_TERMINAL_RECEIPT_v1.0.json"
)
TERMINAL_RECEIPT_SHA256 = (
    "e68cf58a15640e553e4c5b114877ac385c009cbc5d9812fe745d82df0e43b4af"
)
TERMINAL_RECEIPT_BLOB = "4e2ee7a5629d15e96f42fb5868683f222e8067bc"
TERMINAL_RECEIPT_BYTES = 17618
PREDECESSOR_CHECKPOINT_PATH = (
    "control/m3top3/public-data-source-admission/v1.0/"
    "M3TOP3_FINANCE_CA_ACQUISITION_CHECKPOINT_v1.0.json"
)
PREDECESSOR_CHECKPOINT_SHA256 = (
    "9a18edaf66b9f03b2202dbef11c0f86472340695c0c245f0a8ca958e3cfce55d"
)
PREDECESSOR_CHECKPOINT_BLOB = "eeda311c19724fb8c13ab20e3bdc1469853da8ad"
PREDECESSOR_CHECKPOINT_BYTES = 37979
SOURCE_ADMISSION_PATH = "tools/m3top3/source_admission.py"
SOURCE_ADMISSION_SHA256 = (
    "574b2f45474b39fd0cf64f28a946bd115ddb3b782595c3ddd78d15c801d111dd"
)
SOURCE_ADMISSION_BLOB = "2aba27f2ca27dddabcdf1f6c963f28d63d26402f"
SOURCE_ADMISSION_BYTES = 47130
REV0_IDENTITY_MAP_SHA256 = (
    "0cecaae9f8ecf9736b08218ef9d830fa896eeed79b73418eebf5503ae277ba60"
)
REV27_CHECKPOINT_TOKEN_SHA256 = (
    "dcccd95f006b04732474640503b10e0d950542e6e3a4bab8a1ea2707644d643f"
)
AUTHORITY_PATH = (
    "control/m3top3/public-data-source-admission/v1.0/"
    "M3TOP3_FINANCE_CA_PAGE100_G10_FORENSIC_AUTHORITY_v1.0.json"
)
ACTIVATION_PATH = (
    "control/m3top3/public-data-source-admission/v1.0/"
    "M3TOP3_FINANCE_CA_PAGE100_G10_FORENSIC_ACTIVATION_v1.0.json"
)
ACTIVATION_TEMPLATE_PATH = ACTIVATION_PATH + ".template"
MANIFEST_PATH = (
    "control/m3top3/public-data-source-admission/v1.0/"
    "M3TOP3_FINANCE_CA_PAGE100_G10_FORENSIC_MANIFEST_v1.0.json"
)
WORKFLOW_PATH = ".github/workflows/m3top3-finance-page100-g10-readonly-forensic-v1.yml"
RUNNER_PATH = "tools/m3top3/finance_page100_g10_forensic.py"
PREP_FILES = frozenset(
    {WORKFLOW_PATH, RUNNER_PATH, AUTHORITY_PATH, ACTIVATION_TEMPLATE_PATH, MANIFEST_PATH}
)

RAW_PREFIX = (
    "raw/public-data-api/M3TOP3-FINANCE-STOCK-RIGHTS-v1/_pilot_generation/"
    "runtime_lock_id=PMO-FINANCE-PAGE100-G10-20260830044522/"
    "pilot_run_id=FINANCE-PAGE100-PILOT-G10-20260830044522/"
)
CONTROL_PREFIX = (
    "raw/public-data-api/M3TOP3-FINANCE-STOCK-RIGHTS-v1/_pilot_control/"
    "runtime_lock_id=PMO-FINANCE-PAGE100-G10-20260830044522/"
    "pilot_run_id=FINANCE-PAGE100-PILOT-G10-20260830044522/"
)
CHECKPOINT_KEY = CONTROL_PREFIX + "checkpoint.json"
CLAIM_PREFIX = (
    "raw/public-data-api/M3TOP3-FINANCE-STOCK-RIGHTS-v1/"
    "_writer_claims/quota_day_kst=2026-08-30/"
)
CLAIM_KEY = CLAIM_PREFIX + "execution-claim.json"

ALLOWED_AWS_CALLS = frozenset(
    {
        ("sts", "get-caller-identity"),
        ("s3api", "list-object-versions"),
        ("s3api", "get-object"),
    }
)
BANNED_EVIDENCE_PATTERNS = (
    re.compile(r"(?i)(service[_-]?key|authorization)\s*[:=]"),
    re.compile(r"(?i)(x-amz-(credential|signature|security-token))"),
    re.compile(r"(?i)(api\.data\.go\.kr|apis\.data\.go\.kr)"),
    re.compile(r"(?i)(aws_access_key_id|aws_secret_access_key|aws_session_token)"),
    re.compile(r"(?i)([?&](serviceKey|service_key|key)=)"),
)


class ForensicAuditError(RuntimeError):
    """Fail-closed forensic contract failure."""


def require(condition: bool, code: str) -> None:
    if not condition:
        raise ForensicAuditError(code)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob_sha_bytes(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def canonical_json_payload(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def canonical_json_bytes(value: Any) -> bytes:
    return canonical_json_payload(value) + b"\n"


def load_canonical_json(path: pathlib.Path) -> dict[str, Any]:
    raw = path.read_bytes()
    require(raw.endswith(b"\n") and not raw.endswith(b"\n\n"), "JSON_NEWLINE_INVALID")
    try:
        value = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ForensicAuditError("JSON_PARSE_INVALID") from exc
    require(isinstance(value, dict), "JSON_ROOT_NOT_OBJECT")
    require(raw == canonical_json_bytes(value), "JSON_NOT_CANONICAL")
    return value


def write_canonical_json(path: pathlib.Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_json_bytes(dict(value)))


def issuer_identity_digest(item: Mapping[str, Any]) -> str:
    """Exact G10 identity algorithm, including canonical JSON's terminal LF."""
    identity = {
        "issuCmpyKsdCustNo": str(item.get("issuCmpyKsdCustNo") or ""),
        "crno": str(item.get("crno") or ""),
        "stckIssuCmpyNm": str(item.get("stckIssuCmpyNm") or ""),
    }
    return sha256_bytes(canonical_json_bytes(identity))


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _xml_to_value(element: ET.Element) -> Any:
    children = list(element)
    if not children:
        return (element.text or "").strip()
    grouped: dict[str, Any] = {}
    for child in children:
        tag = _local_name(child.tag)
        value = _xml_to_value(child)
        if tag in grouped:
            if not isinstance(grouped[tag], list):
                grouped[tag] = [grouped[tag]]
            grouped[tag].append(value)
        else:
            grouped[tag] = value
    return grouped


def _parse_entity_value(body: bytes) -> Any:
    payload = body.lstrip(b"\xef\xbb\xbf\x00\t\r\n ")
    if payload.startswith((b"{", b"[")):
        def no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
            result: dict[str, Any] = {}
            for key, value in pairs:
                require(key not in result, "JSON_DUPLICATE_KEY")
                result[key] = value
            return result
        try:
            return json.loads(payload.decode("utf-8"), object_pairs_hook=no_duplicates)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ForensicAuditError("ENTITY_JSON_PARSE_INVALID") from exc
    if payload.startswith(b"<"):
        upper = payload.upper()
        require(b"<!DOCTYPE" not in upper and b"<!ENTITY" not in upper, "XML_DTD_PROHIBITED")
        try:
            root = ET.fromstring(payload)
        except ET.ParseError as exc:
            raise ForensicAuditError("XML_PARSE_INVALID") from exc
        return {_local_name(root.tag): _xml_to_value(root)}
    raise ForensicAuditError("ENTITY_NOT_JSON_OR_XML")


def _find_first(value: Any, names: tuple[str, ...]) -> Any:
    if isinstance(value, dict):
        for name in names:
            if name in value and not isinstance(value[name], (dict, list)):
                return value[name]
        for child in value.values():
            found = _find_first(child, names)
            if found is not None:
                return found
    elif isinstance(value, list):
        for child in value:
            found = _find_first(child, names)
            if found is not None:
                return found
    return None


def _find_items(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, dict):
        if "item" in value:
            item = value["item"]
            if item in (None, ""):
                return []
            if isinstance(item, dict):
                return [item]
            require(
                isinstance(item, list) and all(isinstance(row, dict) for row in item),
                "ITEM_SHAPE_INVALID",
            )
            return list(item)
        for child in value.values():
            items = _find_items(child)
            if items:
                return items
    elif isinstance(value, list):
        for child in value:
            items = _find_items(child)
            if items:
                return items
    return []


def _strict_uint(text: str | None, code: str, *, positive: bool = False) -> int:
    require(isinstance(text, str) and bool(re.fullmatch(r"[0-9]+", text)), code)
    value = int(text)
    require(value >= (1 if positive else 0), code)
    return value


def parse_finance_entity(
    body: bytes,
    expected_bas_dt: str,
    expected_page_no: int,
    expected_page_size: int,
) -> dict[str, Any]:
    """Meaning-equivalent replay of frozen parse_entity_bytes/finance_entity_to_page."""
    require(isinstance(body, bytes) and 0 < len(body) <= 100_000, "RAW_ENTITY_SIZE_INVALID")
    parsed = _parse_entity_value(body)
    result_code = _find_first(parsed, ("resultCode",))
    require(result_code == "00", "FINANCE_RESULT_CODE_NOT_00")
    page_no = _strict_uint(str(_find_first(parsed, ("pageNo",))), "PAGE_NO_INVALID", positive=True)
    page_size = _strict_uint(str(_find_first(parsed, ("numOfRows",))), "PAGE_SIZE_INVALID", positive=True)
    total_count = _strict_uint(str(_find_first(parsed, ("totalCount", "totalCnt"))), "TOTAL_COUNT_INVALID")
    require(page_no == expected_page_no, "PAGE_NO_MISMATCH")
    require(page_size == expected_page_size, "PAGE_SIZE_MISMATCH")
    items = _find_items(parsed)
    for row in items:
        require(str(_find_first(row, ("basDt",)) or "") == expected_bas_dt, "ITEM_BASE_DATE_MISMATCH")
    require(len(items) <= expected_page_size, "ITEM_COUNT_EXCEEDS_PAGE_SIZE")
    require(
        not (expected_page_no * expected_page_size < total_count)
        or len(items) == expected_page_size,
        "UNDERFILLED_INTERMEDIATE_PAGE",
    )
    return {
        "basDt": expected_bas_dt,
        "page_no": page_no,
        "page_size": page_size,
        "total_count": total_count,
        "items": items,
    }


def classify_conflicts(
    items_or_pages: Sequence[Mapping[str, Any]],
    inherited_identity_map: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Replay G10 observation order without changing the frozen identity map."""
    identities = dict(inherited_identity_map or {})
    for custody, digest in identities.items():
        require(bool(custody) and bool(re.fullmatch(r"[0-9a-f]{64}", digest)), "INHERITED_IDENTITY_INVALID")
    pages: list[dict[str, Any]] = []
    if items_or_pages and "items" in items_or_pages[0]:
        for page in items_or_pages:
            pages.append(
                {
                    "basDt": str(page.get("basDt") or "UNKNOWN"),
                    "page_no": int(page.get("page_no") or 0),
                    "items": list(page.get("items") or []),
                }
            )
        require(
            [page["page_no"] for page in pages] == list(range(1, len(pages) + 1)),
            "PAGE_ORDER_NOT_EXACT_ASCENDING",
        )
        require(len({page["basDt"] for page in pages}) == 1, "PAGE_BASE_DATE_DRIFT")
    else:
        pages = [{"basDt": "UNKNOWN", "page_no": 0, "items": list(items_or_pages)}]
    checked = matches = missing = 0
    conflicts: list[dict[str, Any]] = []
    accepted_specimens: dict[tuple[str, str], dict[str, str]] = {}
    for page in pages:
        for item_index, raw_item in enumerate(page["items"], 1):
            item = dict(raw_item)
            custody = str(item.get("issuCmpyKsdCustNo") or "")
            if not custody:
                missing += 1
                continue
            observed = {
                "issuCmpyKsdCustNo": custody,
                "crno": str(item.get("crno") or ""),
                "stckIssuCmpyNm": str(item.get("stckIssuCmpyNm") or ""),
            }
            digest = issuer_identity_digest(observed)
            checked += 1
            expected = identities.get(custody)
            if expected is not None and expected != digest:
                conflicts.append(
                    {
                        "basDt": page["basDt"],
                        "page_no": page["page_no"],
                        "item_index": item_index,
                        "observed_identity": observed,
                        "observed_identity_sha256": digest,
                        "frozen_identity_sha256": expected,
                        "accepted_current_specimen": accepted_specimens.get(
                            (custody, expected), "NOT_OBSERVED_IN_FOUR_G10_RAW_ENTITIES"
                        ),
                        "classification": "FROZEN_G10_IDENTITY_DIGEST_MISMATCH",
                    }
                )
            else:
                identities[custody] = digest
                matches += 1
                accepted_specimens.setdefault((custody, digest), observed)
    return {
        "rows_checked": checked,
        "match_rows": matches,
        "conflicts": len(conflicts),
        "missing_rows": missing,
        "conflict_specimens": conflicts,
        "final_identity_hashes": dict(sorted(identities.items())),
    }


def paginate_version_pages(
    fetch_page: Callable[[str | None, str | None], Mapping[str, Any]],
    prefix: str,
) -> dict[str, list[dict[str, Any]]]:
    """Pure fail-closed ListObjectVersions paginator."""
    versions: list[dict[str, Any]] = []
    deletes: list[dict[str, Any]] = []
    seen_entries: set[tuple[str, str, str]] = set()
    key_marker: str | None = None
    version_marker: str | None = None
    seen_markers: set[tuple[str | None, str | None]] = set()
    for _ in range(100):
        marker = (key_marker, version_marker)
        require(marker not in seen_markers, "VERSION_PAGINATION_CYCLE")
        seen_markers.add(marker)
        page = dict(fetch_page(key_marker, version_marker))
        require(not page.get("CommonPrefixes"), "VERSION_COMMON_PREFIXES_PROHIBITED")
        for kind, target in (("Versions", versions), ("DeleteMarkers", deletes)):
            rows = page.get(kind, [])
            require(isinstance(rows, list), "VERSION_PAGE_ROWS_INVALID")
            for row in rows:
                require(isinstance(row, dict), "VERSION_PAGE_ROW_INVALID")
                key = row.get("Key")
                require(isinstance(key, str) and key.startswith(prefix), "VERSION_KEY_OUTSIDE_PREFIX")
                entry = (kind, key, str(row.get("VersionId") or ""))
                require(bool(entry[2]) and entry not in seen_entries, "VERSION_ENTRY_DUPLICATE_OR_ID_MISSING")
                seen_entries.add(entry)
                target.append(dict(row))
        truncated = page.get("IsTruncated", False)
        require(type(truncated) is bool, "VERSION_TRUNCATION_FLAG_INVALID")
        if not truncated:
            return {"versions": versions, "delete_markers": deletes}
        next_key = page.get("NextKeyMarker")
        next_version = page.get("NextVersionIdMarker")
        require(isinstance(next_key, str) and bool(next_key), "NEXT_KEY_MARKER_MISSING")
        require(isinstance(next_version, str) and bool(next_version), "NEXT_VERSION_MARKER_MISSING")
        key_marker, version_marker = next_key, next_version
    raise ForensicAuditError("VERSION_PAGINATION_PAGE_CAP_EXCEEDED")


def _read_json_file(path: pathlib.Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_bytes())
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ForensicAuditError("INPUT_JSON_INVALID") from exc
    require(isinstance(value, dict), "INPUT_JSON_ROOT_INVALID")
    return value


def validate_static_contract(
    authority: Mapping[str, Any],
    activation: Mapping[str, Any],
    receipt: Mapping[str, Any],
    predecessor_checkpoint: Mapping[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> None:
    require(authority.get("artifact") == "M3TOP3_FINANCE_CA_PAGE100_G10_FORENSIC_AUTHORITY_v1.0", "AUTHORITY_ARTIFACT_MISMATCH")
    require(authority.get("state") == "OWNER_AUTHORIZED_READ_ONLY_SINGLE_ATTEMPT", "AUTHORITY_STATE_MISMATCH")
    require(authority.get("repository") == REPOSITORY and authority.get("branch") == BRANCH, "AUTHORITY_REPO_BRANCH_MISMATCH")
    owner = authority.get("owner_authorization", {})
    require(owner.get("issue_comment_id") == OWNER_COMMENT_ID, "OWNER_COMMENT_ID_MISMATCH")
    require(owner.get("created_updated_at_utc") == OWNER_COMMENT_CREATED_UPDATED_UTC, "OWNER_COMMENT_TIME_MISMATCH")
    require(owner.get("body_sha256") == OWNER_COMMENT_BODY_SHA256, "OWNER_COMMENT_BODY_HASH_MISMATCH")
    require(owner.get("url") == OWNER_COMMENT_URL, "OWNER_COMMENT_URL_MISMATCH")
    base = authority.get("base_terminal_receipt", {})
    require(base.get("commit_sha") == BASE_RECEIPT_COMMIT and base.get("tree_sha") == BASE_RECEIPT_TREE, "BASE_RECEIPT_COMMIT_TREE_MISMATCH")
    require(base.get("path") == TERMINAL_RECEIPT_PATH and base.get("sha256") == TERMINAL_RECEIPT_SHA256 and base.get("git_blob_sha") == TERMINAL_RECEIPT_BLOB and base.get("bytes") == TERMINAL_RECEIPT_BYTES, "BASE_RECEIPT_FILE_MISMATCH")
    source_binding = authority.get("frozen_source_admission", {})
    require(
        source_binding
        == {
            "path": SOURCE_ADMISSION_PATH,
            "sha256": SOURCE_ADMISSION_SHA256,
            "git_blob_sha": SOURCE_ADMISSION_BLOB,
            "bytes": SOURCE_ADMISSION_BYTES,
        },
        "FROZEN_SOURCE_ADMISSION_BINDING_MISMATCH",
    )
    runner_binding = authority.get("frozen_g10_runner", {})
    require(
        runner_binding.get("path") == "tools/m3top3/finance_page100_pilot.py"
        and runner_binding.get("sha256") == "537880a005e9b18432dfea045fb9d794146ee19f48d239bc73b0e326afda21e5"
        and runner_binding.get("git_blob_sha") == "1f11fd3b7f6f884b7b524ac3553c2d30518d0ee5",
        "FROZEN_G10_RUNNER_BINDING_MISMATCH",
    )
    predecessor_binding = authority.get("frozen_predecessor_checkpoint", {})
    require(
        predecessor_binding.get("path") == PREDECESSOR_CHECKPOINT_PATH
        and predecessor_binding.get("sha256") == PREDECESSOR_CHECKPOINT_SHA256
        and predecessor_binding.get("git_blob_sha") == PREDECESSOR_CHECKPOINT_BLOB
        and predecessor_binding.get("bytes") == PREDECESSOR_CHECKPOINT_BYTES
        and predecessor_binding.get("identity_hash_count") == 12,
        "FROZEN_PREDECESSOR_BINDING_MISMATCH",
    )
    aws = authority.get("aws_read_only_scope", {})
    require(aws.get("account_id") == ACCOUNT_ID and aws.get("region") == REGION and aws.get("bucket") == BUCKET, "AWS_SCOPE_MISMATCH")
    require(aws.get("raw_prefix") == RAW_PREFIX and aws.get("control_prefix") == CONTROL_PREFIX and aws.get("claim_prefix") == CLAIM_PREFIX, "AWS_PREFIX_MISMATCH")
    require(aws.get("claim_list_exact_prefix") == CLAIM_KEY, "AWS_CLAIM_LIST_PREFIX_MISMATCH")
    require(aws.get("checkpoint_key") == CHECKPOINT_KEY and aws.get("execution_claim_key") == CLAIM_KEY, "AWS_KEY_MISMATCH")
    effects = authority.get("authorized_effects", {})
    expected_zero = {
        "finance_provider_api_calls": 0,
        "quota_reservations": 0,
        "s3_put_object_calls": 0,
        "s3_delete_object_calls": 0,
        "remote_custody_mutations": 0,
        "normalization_records": 0,
        "promotion_actions": 0,
    }
    require(effects == expected_zero, "AUTHORITY_EFFECTS_NOT_EXACT_ZERO")
    require(authority.get("semantic_change_authorized") is False, "SEMANTIC_CHANGE_AUTHORIZED")
    require(authority.get("validation_floor_reduction_authorized") is False, "VALIDATION_REDUCTION_AUTHORIZED")
    require(authority.get("production_authorized") is False, "PRODUCTION_AUTHORIZED")
    allowed_actions = set(aws.get("allowed_aws_api_actions", []))
    require(allowed_actions == {"s3:ListBucketVersions", "s3:GetObjectVersion"}, "AWS_ACTION_ALLOWLIST_MISMATCH")
    require(not any(any(word in action for word in ("Put", "Delete", "Copy", "Restore")) for action in allowed_actions), "WRITE_ACTION_PRESENT")

    require(activation.get("artifact") == "M3TOP3_FINANCE_CA_PAGE100_G10_FORENSIC_ACTIVATION_v1.0", "ACTIVATION_ARTIFACT_MISMATCH")
    require(activation.get("state") == "ARMED_ONCE_READ_ONLY", "ACTIVATION_STATE_MISMATCH")
    require(activation.get("repository") == REPOSITORY and activation.get("branch") == BRANCH and activation.get("owner_actor") == ACTOR, "ACTIVATION_IDENTITY_MISMATCH")
    require(activation.get("activation_commit_message") == ACTIVATION_MESSAGE, "ACTIVATION_MESSAGE_MISMATCH")
    require(bool(re.fullmatch(r"[0-9a-f]{40}", str(activation.get("preparation_head_sha", "")))), "PREPARATION_HEAD_INVALID")
    require(bool(re.fullmatch(r"[0-9a-f]{40}", str(activation.get("preparation_tree_sha", "")))), "PREPARATION_TREE_INVALID")
    require(activation.get("owner_authorization") == owner, "ACTIVATION_OWNER_BINDING_MISMATCH")
    require(activation.get("authorized_effects") == expected_zero, "ACTIVATION_EFFECTS_NOT_ZERO")
    require(activation.get("base_terminal_receipt_commit") == BASE_RECEIPT_COMMIT, "ACTIVATION_BASE_MISMATCH")
    require(activation.get("single_attempt_only") is True and activation.get("g10_rerun") is False and activation.get("g11_generation") is False, "ACTIVATION_ATTEMPT_SCOPE_MISMATCH")

    require(receipt.get("artifact") == "M3TOP3_FINANCE_CA_PAGE100_G10_LIVE_TERMINAL_RECEIPT_v1.0", "TERMINAL_RECEIPT_ARTIFACT_MISMATCH")
    require(receipt.get("repository") == REPOSITORY and receipt.get("branch") == BRANCH, "TERMINAL_RECEIPT_REPO_BRANCH_MISMATCH")
    require(receipt.get("workflow", {}).get("run_id") == 33273146915 and receipt.get("workflow", {}).get("run_attempt") == 1, "G10_RUN_IDENTITY_MISMATCH")
    require(receipt.get("failure", {}).get("exact_code") == "IssuerIdentityConflictError", "G10_FAILURE_CODE_MISMATCH")
    successor = receipt.get("issuer_identity", {}).get("successor", {})
    require(successor == {"conflicts": 2, "match_rows": 38, "missing_rows": 0, "rows_checked": 40}, "G10_IDENTITY_COUNTER_MISMATCH")
    raw_objects = receipt.get("remote_effects", {}).get("raw_custody", {}).get("objects", [])
    require(isinstance(raw_objects, list) and len(raw_objects) == 4, "G10_RAW_OBJECT_COUNT_MISMATCH")
    require([row.get("page_no") for row in raw_objects] == [1, 2, 3, 4], "G10_RAW_PAGE_ORDER_MISMATCH")
    for row in raw_objects:
        key = row.get("s3_object_key")
        require(isinstance(key, str) and key.startswith(RAW_PREFIX), "G10_RAW_KEY_OUTSIDE_PREFIX")
        require(bool(re.fullmatch(r"[A-Za-z0-9._-]+", str(row.get("version_id", "")))), "G10_RAW_VERSION_INVALID")
        require(row.get("sha256") == row.get("remote_readback_sha256") and row.get("bytes") == row.get("remote_readback_bytes"), "G10_RAW_READBACK_MISMATCH")
    claim = receipt.get("remote_effects", {}).get("execution_claim", {})
    require(claim.get("object_key") == CLAIM_KEY and bool(claim.get("version_id")), "G10_CLAIM_BINDING_MISMATCH")
    checkpoint = receipt.get("remote_effects", {}).get("checkpoint_custody", {})
    require(checkpoint.get("object_key") == CHECKPOINT_KEY and checkpoint.get("checkpoint_revision") == 27, "G10_CHECKPOINT_BINDING_MISMATCH")

    if predecessor_checkpoint is not None:
        telemetry = predecessor_checkpoint
        identity_map = telemetry.get("issuer_identity_hashes", {})
        require(isinstance(identity_map, dict) and len(identity_map) == 12, "PREDECESSOR_IDENTITY_MAP_MISMATCH")
        require(telemetry.get("issuer_identity_rows_checked") == 76 and telemetry.get("issuer_identity_match_rows") == 76 and telemetry.get("issuer_identity_conflicts") == 0 and telemetry.get("issuer_identity_missing_rows") == 0, "PREDECESSOR_IDENTITY_COUNTER_MISMATCH")
    if manifest is not None:
        require(manifest.get("artifact") == "M3TOP3_FINANCE_CA_PAGE100_G10_FORENSIC_MANIFEST_v1.0", "MANIFEST_ARTIFACT_MISMATCH")
        require(manifest.get("base_terminal_receipt_commit") == BASE_RECEIPT_COMMIT, "MANIFEST_BASE_MISMATCH")
        require(set(manifest.get("preparation_files", {})) == PREP_FILES - {MANIFEST_PATH}, "MANIFEST_FILE_SET_MISMATCH")
        prep_root = pathlib.Path(__file__).resolve().parents[2]
        for relative, binding in manifest["preparation_files"].items():
            require(isinstance(binding, dict), "MANIFEST_FILE_BINDING_INVALID")
            data = (prep_root / relative).read_bytes()
            require(
                binding
                == {
                    "bytes": len(data),
                    "git_blob_sha": git_blob_sha_bytes(data),
                    "sha256": sha256_bytes(data),
                },
                "MANIFEST_FILE_BYTES_MISMATCH_" + relative,
            )


def _git_output(*args: str, binary: bool = False) -> bytes | str:
    result = subprocess.run(
        ["git", *args], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    return result.stdout if binary else result.stdout.decode("utf-8").strip()


def _raw_commit_message(commit: str) -> bytes:
    raw = _git_output("cat-file", "commit", commit, binary=True)
    assert isinstance(raw, bytes)
    headers, sep, message = raw.partition(b"\n\n")
    require(bool(headers) and sep == b"\n\n", "GIT_COMMIT_OBJECT_INVALID")
    return message


def _single_parent(commit: str) -> str:
    line = str(_git_output("rev-list", "--parents", "-n", "1", commit)).split()
    require(len(line) == 2 and line[0] == commit, "GIT_COMMIT_PARENT_COUNT_INVALID")
    return line[1]


def _exact_diff_names(before: str, after: str) -> dict[str, str]:
    lines = str(_git_output("diff", "--name-status", "--no-renames", before, after)).splitlines()
    result: dict[str, str] = {}
    for line in lines:
        status, tab, path = line.partition("\t")
        require(tab == "\t" and status in {"A", "M"} and path not in result, "GIT_DIFF_INVALID")
        result[path] = status
    return result


def validate_git_activation(activation: Mapping[str, Any]) -> dict[str, str]:
    expected_env = {
        "GITHUB_REPOSITORY": REPOSITORY,
        "GITHUB_REF": "refs/heads/" + BRANCH,
        "GITHUB_EVENT_NAME": "push",
        "GITHUB_ACTOR": ACTOR,
        "GITHUB_TRIGGERING_ACTOR": ACTOR,
        "GITHUB_RUN_ATTEMPT": "1",
        "EVENT_FORCED": "false",
        "EVENT_HEAD_MESSAGE": ACTIVATION_MESSAGE,
    }
    for key, value in expected_env.items():
        require(os.environ.get(key) == value, "EVENT_ENV_" + key + "_MISMATCH")
    head = str(_git_output("rev-parse", "HEAD"))
    before = os.environ.get("EVENT_BEFORE", "")
    after = os.environ.get("EVENT_AFTER", "")
    require(head == after == os.environ.get("GITHUB_SHA"), "EVENT_HEAD_MISMATCH")
    require(before == activation.get("preparation_head_sha"), "EVENT_BEFORE_PREPARATION_MISMATCH")
    require(_single_parent(head) == before, "ACTIVATION_PARENT_MISMATCH")
    require(_raw_commit_message(head) == ACTIVATION_MESSAGE.encode(), "ACTIVATION_RAW_MESSAGE_MISMATCH")
    require(_exact_diff_names(before, head) == {ACTIVATION_PATH: "A"}, "ACTIVATION_DIFF_NOT_ONE_FILE")
    prep_tree = str(_git_output("rev-parse", before + "^{tree}"))
    require(prep_tree == activation.get("preparation_tree_sha"), "PREPARATION_TREE_MISMATCH")
    require(_single_parent(before) == BASE_RECEIPT_COMMIT, "PREPARATION_PARENT_MISMATCH")
    require(str(_git_output("rev-parse", BASE_RECEIPT_COMMIT + "^{tree}")) == BASE_RECEIPT_TREE, "BASE_RECEIPT_TREE_MISMATCH")
    require(_raw_commit_message(before) == PREP_MESSAGE.encode(), "PREPARATION_RAW_MESSAGE_MISMATCH")
    require(_exact_diff_names(BASE_RECEIPT_COMMIT, before) == {path: "A" for path in PREP_FILES}, "PREPARATION_DIFF_NOT_EXACT_FIVE_FILES")
    return {"activation_head_sha": head, "activation_tree_sha": str(_git_output("rev-parse", "HEAD^{tree}")), "preparation_head_sha": before, "preparation_tree_sha": prep_tree}


def verify_owner_comment(token: str) -> None:
    require(bool(token), "GITHUB_TOKEN_MISSING")
    url = f"https://api.github.com/repos/{REPOSITORY}/issues/comments/{OWNER_COMMENT_ID}"
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": "Bearer " + token,
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "g10-readonly-forensic-audit",
        },
    )

    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req: Any, fp: Any, code: int, msg: str, headers: Any, newurl: str) -> None:
            return None

    try:
        with urllib.request.build_opener(NoRedirect).open(request, timeout=20) as response:
            require(response.status == 200, "OWNER_COMMENT_HTTP_STATUS_INVALID")
            data = json.loads(response.read())
    except (urllib.error.URLError, json.JSONDecodeError) as exc:
        raise ForensicAuditError("OWNER_COMMENT_FETCH_FAILED") from exc
    require(data.get("id") == OWNER_COMMENT_ID, "OWNER_COMMENT_REMOTE_ID_MISMATCH")
    require(data.get("user", {}).get("login") == ACTOR, "OWNER_COMMENT_REMOTE_AUTHOR_MISMATCH")
    require(data.get("html_url") == OWNER_COMMENT_URL, "OWNER_COMMENT_REMOTE_URL_MISMATCH")
    require(data.get("created_at") == OWNER_COMMENT_CREATED_UPDATED_UTC and data.get("updated_at") == OWNER_COMMENT_CREATED_UPDATED_UTC, "OWNER_COMMENT_REMOTE_TIME_MISMATCH")
    body = str(data.get("body") or "").encode("utf-8")
    require(sha256_bytes(body) == OWNER_COMMENT_BODY_SHA256, "OWNER_COMMENT_REMOTE_BODY_MISMATCH")


def _github_json(token: str, api_path_and_query: str) -> dict[str, Any]:
    require(bool(token), "GITHUB_TOKEN_MISSING")
    require(api_path_and_query.startswith("/repos/AofSpds/asset-agent-asa/"), "GITHUB_API_PATH_NOT_EXACT_REPOSITORY")
    request = urllib.request.Request(
        "https://api.github.com" + api_path_and_query,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": "Bearer " + token,
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "g10-readonly-forensic-audit",
        },
    )

    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req: Any, fp: Any, code: int, msg: str, headers: Any, newurl: str) -> None:
            return None

    try:
        with urllib.request.build_opener(NoRedirect).open(request, timeout=20) as response:
            require(response.status == 200, "GITHUB_API_STATUS_INVALID")
            value = json.loads(response.read())
    except (urllib.error.URLError, json.JSONDecodeError) as exc:
        raise ForensicAuditError("GITHUB_API_READ_FAILED") from exc
    require(isinstance(value, dict), "GITHUB_API_ROOT_INVALID")
    return value


def verify_remote_execution_gate(
    token: str,
    activation: Mapping[str, Any],
    phase: str,
) -> dict[str, Any]:
    require(phase in {"before-aws", "before-artifact"}, "REMOTE_GATE_PHASE_INVALID")
    activation_head = os.environ.get("GITHUB_SHA", "")
    preparation_head = str(activation.get("preparation_head_sha") or "")
    current_run_id = int(os.environ.get("GITHUB_RUN_ID", "0"))
    require(bool(re.fullmatch(r"[0-9a-f]{40}", activation_head)), "REMOTE_GATE_ACTIVATION_HEAD_INVALID")
    require(bool(re.fullmatch(r"[0-9a-f]{40}", preparation_head)), "REMOTE_GATE_PREPARATION_HEAD_INVALID")
    ref = _github_json(
        token,
        "/repos/AofSpds/asset-agent-asa/git/ref/heads/"
        + urllib.parse.quote(BRANCH, safe=""),
    )
    require(ref.get("object", {}).get("sha") == activation_head, "REMOTE_BRANCH_HEAD_MOVED")
    workflow_id = urllib.parse.quote(WORKFLOW_PATH, safe="")
    common = (
        f"/repos/AofSpds/asset-agent-asa/actions/workflows/{workflow_id}/runs"
        f"?branch={urllib.parse.quote(BRANCH, safe='')}&event=push&per_page=100&head_sha="
    )
    prep_runs = _github_json(token, common + preparation_head)
    require(prep_runs.get("total_count") == 0 and prep_runs.get("workflow_runs") == [], "PREPARATION_PUSH_MUST_HAVE_ZERO_RUNS")
    activation_runs = _github_json(token, common + activation_head)
    runs = activation_runs.get("workflow_runs")
    require(isinstance(runs, list) and activation_runs.get("total_count") == 1 and len(runs) == 1, "ACTIVATION_MUST_HAVE_EXACTLY_ONE_RUN")
    require(runs[0].get("id") == current_run_id and runs[0].get("run_attempt") == 1, "CURRENT_RUN_ID_ATTEMPT_MISMATCH")
    current = _github_json(
        token,
        f"/repos/AofSpds/asset-agent-asa/actions/runs/{current_run_id}",
    )
    require(current.get("head_sha") == activation_head and current.get("event") == "push", "CURRENT_RUN_HEAD_EVENT_MISMATCH")
    require(current.get("run_attempt") == 1 and current.get("actor", {}).get("login") == ACTOR and current.get("triggering_actor", {}).get("login") == ACTOR, "CURRENT_RUN_ACTOR_ATTEMPT_MISMATCH")
    require(current.get("head_commit", {}).get("message") == ACTIVATION_MESSAGE, "CURRENT_RUN_MESSAGE_MISMATCH")
    active_ids: set[int] = set()
    for status in ("requested", "queued", "in_progress", "waiting", "pending"):
        response = _github_json(
            token,
            f"/repos/AofSpds/asset-agent-asa/actions/workflows/{workflow_id}/runs"
            f"?branch={urllib.parse.quote(BRANCH, safe='')}&status={status}&per_page=100",
        )
        rows = response.get("workflow_runs", [])
        require(isinstance(rows, list), "ACTIVE_RUN_LIST_INVALID")
        active_ids.update(int(row["id"]) for row in rows)
    require(active_ids == {current_run_id}, "DUPLICATE_OR_FOREIGN_ACTIVE_FORENSIC_RUN")
    return {"phase": phase, "branch_head_sha": activation_head, "current_run_id": current_run_id}


class AwsReadOnlyS3:
    def __init__(self, bucket: str) -> None:
        require(bucket == BUCKET, "AWS_BUCKET_INVALID")
        self.bucket = bucket
        self.call_counts: dict[str, int] = {}

    def aws_json(self, *args: str) -> dict[str, Any]:
        require(len(args) >= 2 and (args[0], args[1]) in ALLOWED_AWS_CALLS, "AWS_COMMAND_NOT_READ_ONLY_ALLOWLISTED")
        name = args[0] + ":" + args[1]
        self.call_counts[name] = self.call_counts.get(name, 0) + 1
        result = subprocess.run(
            ["aws", *args, "--output", "json"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env={**os.environ, "AWS_PAGER": "", "AWS_MAX_ATTEMPTS": "1", "AWS_RETRY_MODE": "standard"},
        )
        try:
            value = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            raise ForensicAuditError("AWS_JSON_OUTPUT_INVALID") from exc
        require(isinstance(value, dict), "AWS_JSON_ROOT_INVALID")
        return value

    def list_versions(self, prefix: str) -> dict[str, list[dict[str, Any]]]:
        require(prefix in {RAW_PREFIX, CONTROL_PREFIX, CLAIM_KEY}, "LIST_PREFIX_NOT_EXACT_ALLOWED")

        def fetch(key_marker: str | None, version_marker: str | None) -> Mapping[str, Any]:
            args = [
                "s3api", "list-object-versions", "--bucket", self.bucket,
                "--prefix", prefix, "--expected-bucket-owner", ACCOUNT_ID,
                "--max-keys", "1000", "--no-paginate",
            ]
            if key_marker is not None:
                args.extend(["--key-marker", key_marker, "--version-id-marker", str(version_marker)])
            return self.aws_json(*args)

        return paginate_version_pages(fetch, prefix)

    def read_exact_version(
        self,
        key: str,
        version_id: str,
        destination: pathlib.Path,
        *,
        expected_content_type: str,
        expected_metadata_keys: frozenset[str],
    ) -> tuple[bytes, dict[str, Any]]:
        require(
            key.startswith(RAW_PREFIX) or key == CHECKPOINT_KEY or key == CLAIM_KEY,
            "GET_KEY_NOT_EXACT_ALLOWED",
        )
        meta = self.aws_json(
            "s3api", "get-object", "--bucket", self.bucket, "--key", key,
            "--version-id", version_id, "--expected-bucket-owner", ACCOUNT_ID,
            "--no-paginate", str(destination),
        )
        body = destination.read_bytes()
        require(meta.get("VersionId") == version_id, "READBACK_VERSION_MISMATCH")
        require(meta.get("ContentLength") == len(body), "READBACK_LENGTH_MISMATCH")
        require(meta.get("ServerSideEncryption") == "AES256", "READBACK_ENCRYPTION_MISMATCH")
        require(meta.get("ContentType") == expected_content_type, "READBACK_CONTENT_TYPE_MISMATCH")
        user_metadata = meta.get("Metadata", {})
        require(
            isinstance(user_metadata, dict)
            and set(user_metadata) == expected_metadata_keys
            and user_metadata.get("sha256") == sha256_bytes(body),
            "READBACK_METADATA_EXACT_SET_OR_SHA256_MISMATCH",
        )
        return body, meta


def _inventory_projection(inventory: Mapping[str, Sequence[Mapping[str, Any]]]) -> dict[str, Any]:
    def project(row: Mapping[str, Any], marker: bool) -> dict[str, Any]:
        out = {
            "key": row.get("Key"),
            "version_id": row.get("VersionId"),
            "is_latest": row.get("IsLatest"),
            "last_modified": row.get("LastModified"),
        }
        if not marker:
            out.update({"bytes": row.get("Size"), "etag": row.get("ETag")})
        return out
    return {
        "versions": sorted((project(row, False) for row in inventory["versions"]), key=lambda row: (str(row["key"]), str(row["version_id"]))),
        "delete_markers": sorted((project(row, True) for row in inventory["delete_markers"]), key=lambda row: (str(row["key"]), str(row["version_id"]))),
    }


def _validate_inventory_row(row: Mapping[str, Any]) -> None:
    require(isinstance(row.get("Key"), str) and isinstance(row.get("VersionId"), str), "INVENTORY_IDENTITY_INVALID")
    require(type(row.get("IsLatest")) is bool, "INVENTORY_LATEST_INVALID")
    require(isinstance(row.get("LastModified"), str), "INVENTORY_TIME_INVALID")
    require(type(row.get("Size")) is int and row.get("Size") >= 0, "INVENTORY_SIZE_INVALID")
    require(isinstance(row.get("ETag"), str), "INVENTORY_ETAG_INVALID")


def validate_checkpoint_history(
    records: Sequence[Mapping[str, Any]],
    *,
    require_exact_g10_vectors: bool = False,
) -> dict[str, Any]:
    require(len(records) == 28, "CHECKPOINT_HISTORY_COUNT_INVALID")
    by_revision: dict[int, Mapping[str, Any]] = {}
    version_ids: set[str] = set()
    latest_revisions: list[int] = []
    immutable_keys = (
        "runtime_lock_id", "pilot_run_id", "execution_token_sha256",
        "owner_cap_spec_sha256", "activation_base_head_commit",
    )
    monotonic_keys = (
        "network_attempts_started_conservative", "provider_api_network_attempts",
        "quota_reservations", "remote_raw_custody_writes",
        "response_entities_received", "issuer_identity_rows_checked",
        "issuer_identity_match_rows", "issuer_identity_conflicts",
        "issuer_identity_missing_rows",
    )
    immutable_reference: dict[str, Any] | None = None
    for record in records:
        checkpoint = record.get("checkpoint")
        require(isinstance(checkpoint, dict), "CHECKPOINT_RECORD_BODY_INVALID")
        revision = checkpoint.get("checkpoint_revision")
        require(type(revision) is int and 0 <= revision <= 27 and revision not in by_revision, "CHECKPOINT_REVISION_INVALID_OR_DUPLICATE")
        by_revision[revision] = checkpoint
        version_id = record.get("version_id")
        require(isinstance(version_id, str) and version_id not in version_ids, "CHECKPOINT_VERSION_ID_DUPLICATE")
        version_ids.add(version_id)
        if record.get("is_latest") is True:
            latest_revisions.append(revision)
        current_immutable = {key: checkpoint.get(key) for key in immutable_keys}
        if immutable_reference is None:
            immutable_reference = current_immutable
        require(current_immutable == immutable_reference, "CHECKPOINT_IMMUTABLE_BINDING_DRIFT")
        require(checkpoint.get("normalization_records_created") == 0, "CHECKPOINT_NORMALIZATION_NONZERO")
        require(checkpoint.get("promotion_actions") == 0, "CHECKPOINT_PROMOTION_NONZERO")
        require(checkpoint.get("validation_claim") == "NONE", "CHECKPOINT_VALIDATION_CLAIM_DRIFT")
        require(checkpoint.get("gate_effect") == "NONE", "CHECKPOINT_GATE_EFFECT_DRIFT")
    require(set(by_revision) == set(range(28)), "CHECKPOINT_REVISION_SET_NOT_ZERO_THROUGH_27")
    previous_checkpoint: Mapping[str, Any] | None = None
    for revision in range(28):
        checkpoint = by_revision[revision]
        if previous_checkpoint is not None:
            for key in monotonic_keys:
                before = previous_checkpoint.get(key)
                after = checkpoint.get(key)
                require(type(before) is int and type(after) is int and after >= before, "CHECKPOINT_COUNTER_NOT_MONOTONIC_" + key)
            previous_raw = previous_checkpoint.get("raw_index", [])
            current_raw = checkpoint.get("raw_index", [])
            require(isinstance(previous_raw, list) and isinstance(current_raw, list) and current_raw[: len(previous_raw)] == previous_raw, "CHECKPOINT_RAW_INDEX_NOT_PREFIX_PRESERVING")
        previous_checkpoint = checkpoint
    exact_vectors = {
        "network_attempts_started_conservative": [0, 0, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4],
        "quota_reservations": [0, 0, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4],
        "provider_api_network_attempts": [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4],
        "remote_raw_custody_writes": [0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4],
        "response_entities_received": [0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4],
        "date_echo_match_rows": [0, 0, 0, 0, 0, 10, 10, 10, 10, 10, 10, 10, 20, 20, 20, 20, 20, 20, 30, 30, 30, 30, 30, 30, 40, 40, 40, 40],
        "issuer_identity_rows_checked": [0, 0, 0, 0, 0, 0, 0, 0, 10, 10, 10, 10, 10, 10, 20, 20, 20, 20, 20, 20, 30, 30, 30, 30, 30, 30, 40, 40],
        "issuer_identity_match_rows": [0, 0, 0, 0, 0, 0, 0, 0, 10, 10, 10, 10, 10, 10, 20, 20, 20, 20, 20, 20, 30, 30, 30, 30, 30, 30, 38, 38],
        "issuer_identity_conflicts": [0] * 26 + [2, 2],
        "issuer_identity_missing_rows": [0] * 28,
    }
    if require_exact_g10_vectors:
        for key, expected in exact_vectors.items():
            observed = [by_revision[revision].get(key) for revision in range(28)]
            require(observed == expected, "CHECKPOINT_EXACT_VECTOR_MISMATCH_" + key)
        require(
            [by_revision[revision].get("state") for revision in range(28)]
            == ["IN_PROGRESS"] * 27 + ["BLOCKED"],
            "CHECKPOINT_STATE_VECTOR_MISMATCH",
        )
    require(latest_revisions == [27], "CHECKPOINT_LATEST_NOT_EXACT_REV27")
    final = by_revision[27]
    require(final.get("state") == "BLOCKED" and final.get("last_error_class") == "IssuerIdentityConflictError", "CHECKPOINT_FINAL_TERMINAL_STATE_INVALID")
    return {"by_revision": by_revision, "immutable_bindings": immutable_reference}


def checkpoint_token_sha256(record: Mapping[str, Any]) -> str:
    token = json.dumps(
        {
            "etag": str(record.get("etag") or ""),
            "sse": "AES256",
            "version_id": str(record.get("version_id") or ""),
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    require(bool(record.get("etag")) and bool(record.get("version_id")), "CHECKPOINT_TOKEN_INPUT_INVALID")
    return sha256_bytes(token.encode("utf-8"))


def run_audit(
    authority: Mapping[str, Any],
    activation: Mapping[str, Any],
    receipt: Mapping[str, Any],
    predecessor: Mapping[str, Any],
    git_lineage: Mapping[str, str],
    output_dir: pathlib.Path,
) -> dict[str, Any]:
    client = AwsReadOnlyS3(BUCKET)
    caller = client.aws_json("sts", "get-caller-identity", "--no-cli-pager")
    require(caller.get("Account") == ACCOUNT_ID, "AWS_ACCOUNT_MISMATCH")

    inventories = {
        "raw": client.list_versions(RAW_PREFIX),
        "control": client.list_versions(CONTROL_PREFIX),
        "claim": client.list_versions(CLAIM_KEY),
    }
    for inventory in inventories.values():
        require(not inventory["delete_markers"], "DELETE_MARKER_OBSERVED")
        for row in inventory["versions"]:
            _validate_inventory_row(row)

    expected_raw = receipt["remote_effects"]["raw_custody"]["objects"]
    raw_pairs = {(row["Key"], row["VersionId"]) for row in inventories["raw"]["versions"]}
    expected_raw_pairs = {(row["s3_object_key"], row["version_id"]) for row in expected_raw}
    require(raw_pairs == expected_raw_pairs and len(inventories["raw"]["versions"]) == 4, "RAW_VERSION_HISTORY_NOT_EXACT_FOUR")
    require(all(row["IsLatest"] is True for row in inventories["raw"]["versions"]), "RAW_VERSION_NOT_LATEST")
    claim_binding = receipt["remote_effects"]["execution_claim"]
    require(
        {(row["Key"], row["VersionId"]) for row in inventories["claim"]["versions"]}
        == {(CLAIM_KEY, claim_binding["version_id"])},
        "CLAIM_VERSION_HISTORY_NOT_EXACT_ONE",
    )
    require(inventories["claim"]["versions"][0]["IsLatest"] is True, "CLAIM_VERSION_NOT_LATEST")
    require(
        len(inventories["control"]["versions"]) == 28
        and {row["Key"] for row in inventories["control"]["versions"]} == {CHECKPOINT_KEY},
        "CONTROL_VERSION_HISTORY_NOT_EXACT_CHECKPOINT_28",
    )

    pages: list[dict[str, Any]] = []
    raw_metadata_by_page: dict[int, dict[str, str]] = {}
    checkpoint_records: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="g10-forensic-") as tmp_name:
        tmp = pathlib.Path(tmp_name)
        for raw in expected_raw:
            destination = tmp / f"raw-page-{raw['page_no']}.entity"
            body, head = client.read_exact_version(
                raw["s3_object_key"], raw["version_id"], destination,
                expected_content_type="application/octet-stream",
                expected_metadata_keys=frozenset(
                    {
                        "sha256", "http-status", "acquired-at-utc", "request-id",
                        "bas-dt", "page-no", "attempt", "runtime-lock-id",
                        "pilot-run-id", "quota-day-kst", "provider-call-started-at-utc",
                        "socket-opened-at-utc", "response-received-at-utc",
                        "reservation-checkpoint-revision",
                        "reservation-checkpoint-token-sha256",
                        "provider-call-checkpoint-revision",
                        "provider-call-checkpoint-token-sha256",
                        "execution-claim-version-id",
                        "execution-claim-content-sha256",
                    }
                ),
            )
            digest = sha256_bytes(body)
            require(digest == raw["sha256"] and len(body) == raw["bytes"], "RAW_BODY_BINDING_MISMATCH")
            require(head.get("ETag") == raw["etag"], "RAW_ETAG_MISMATCH")
            listed = [
                row for row in inventories["raw"]["versions"]
                if row["Key"] == raw["s3_object_key"] and row["VersionId"] == raw["version_id"]
            ]
            require(len(listed) == 1 and listed[0]["Size"] == len(body) and listed[0]["ETag"] == head.get("ETag"), "RAW_LIST_GET_METADATA_MISMATCH")
            page = parse_finance_entity(body, str(raw["basDt"]), int(raw["page_no"]), 10)
            page["source_object"] = {
                "key": raw["s3_object_key"], "version_id": raw["version_id"],
                "sha256": digest, "bytes": len(body), "etag": head.get("ETag"),
                "server_side_encryption": head.get("ServerSideEncryption"),
            }
            raw_metadata_by_page[int(raw["page_no"])] = dict(head["Metadata"])
            pages.append(page)
        pages.sort(key=lambda page: int(page["page_no"]))

        for index, row in enumerate(inventories["control"]["versions"]):
            destination = tmp / f"checkpoint-{index}.json"
            body, head = client.read_exact_version(
                CHECKPOINT_KEY, row["VersionId"], destination,
                expected_content_type="application/json",
                expected_metadata_keys=frozenset({"sha256"}),
            )
            try:
                checkpoint = json.loads(body)
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise ForensicAuditError("REMOTE_CHECKPOINT_JSON_INVALID") from exc
            require(isinstance(checkpoint, dict), "REMOTE_CHECKPOINT_ROOT_INVALID")
            require(body == canonical_json_bytes(checkpoint), "REMOTE_CHECKPOINT_NOT_CANONICAL_JSON_LF")
            require(row["Size"] == len(body) and row["ETag"] == head.get("ETag"), "CHECKPOINT_LIST_GET_METADATA_MISMATCH")
            revision = checkpoint.get("checkpoint_revision")
            require(type(revision) is int and 0 <= revision <= 27, "REMOTE_CHECKPOINT_REVISION_INVALID")
            require(checkpoint.get("runtime_lock_id") == "PMO-FINANCE-PAGE100-G10-20260830044522" and checkpoint.get("pilot_run_id") == "FINANCE-PAGE100-PILOT-G10-20260830044522", "REMOTE_CHECKPOINT_RUNTIME_MISMATCH")
            checkpoint_records.append(
                {
                    "revision": revision,
                    "version_id": row["VersionId"],
                    "sha256": sha256_bytes(body),
                    "bytes": len(body),
                    "etag": head.get("ETag"),
                    "is_latest": row["IsLatest"],
                    "last_modified": row["LastModified"],
                    "checkpoint": checkpoint,
                }
            )
        claim_body, claim_head = client.read_exact_version(
            CLAIM_KEY, claim_binding["version_id"], tmp / "execution-claim.json",
            expected_content_type="application/json",
            expected_metadata_keys=frozenset({"sha256"}),
        )

    history = validate_checkpoint_history(
        checkpoint_records,
        require_exact_g10_vectors=True,
    )
    checkpoint_records.sort(key=lambda row: int(row["revision"]))
    records_by_revision = {int(row["revision"]): row for row in checkpoint_records}
    final_record = checkpoint_records[-1]
    final_checkpoint = final_record["checkpoint"]
    checkpoint_receipt = receipt["remote_effects"]["checkpoint_custody"]
    require(final_record["sha256"] == checkpoint_receipt["final_artifact_sha256"] and final_record["bytes"] == checkpoint_receipt["final_artifact_bytes"] and final_checkpoint["state"] == "BLOCKED", "FINAL_CHECKPOINT_RECEIPT_MISMATCH")
    require(final_checkpoint["provider_api_network_attempts"] == 4 and final_checkpoint["quota_reservations"] == 4 and final_checkpoint["remote_raw_custody_writes"] == 4, "FINAL_CHECKPOINT_EFFECT_COUNTER_MISMATCH")
    require(final_checkpoint["issuer_identity_rows_checked"] == 40 and final_checkpoint["issuer_identity_match_rows"] == 38 and final_checkpoint["issuer_identity_conflicts"] == 2 and final_checkpoint["issuer_identity_missing_rows"] == 0, "FINAL_CHECKPOINT_IDENTITY_COUNTER_MISMATCH")
    require(checkpoint_token_sha256(final_record) == REV27_CHECKPOINT_TOKEN_SHA256, "FINAL_CHECKPOINT_TOKEN_HASH_MISMATCH")
    expected_token_revision_pairs = [(2, 3), (9, 10), (15, 16), (21, 22)]
    final_raw_index = final_checkpoint.get("raw_index", [])
    require(isinstance(final_raw_index, list) and len(final_raw_index) == 4, "FINAL_RAW_INDEX_COUNT_MISMATCH")
    final_attempts = final_checkpoint.get("attempts", [])
    require(isinstance(final_attempts, list) and len(final_attempts) == 4, "FINAL_ATTEMPT_COUNT_MISMATCH")
    for raw_row, (reservation_revision, provider_revision) in zip(final_raw_index, expected_token_revision_pairs, strict=True):
        require(raw_row.get("reservation_checkpoint_revision") == reservation_revision and raw_row.get("provider_call_checkpoint_revision") == provider_revision, "RAW_INDEX_CHECKPOINT_REVISION_PAIR_MISMATCH")
        require(raw_row.get("reservation_checkpoint_token_sha256") == checkpoint_token_sha256(records_by_revision[reservation_revision]), "RAW_INDEX_RESERVATION_TOKEN_MISMATCH")
        require(raw_row.get("provider_call_checkpoint_token_sha256") == checkpoint_token_sha256(records_by_revision[provider_revision]), "RAW_INDEX_PROVIDER_TOKEN_MISMATCH")
        page_no = int(raw_row.get("page_no", 0))
        metadata = raw_metadata_by_page.get(page_no)
        require(
            metadata
            == {
                "sha256": str(raw_row["entity_sha256"]),
                "http-status": str(raw_row["http_status"]),
                "acquired-at-utc": str(raw_row["acquired_at_utc"]),
                "request-id": str(raw_row["request_id"]),
                "bas-dt": str(raw_row["basDt"]),
                "page-no": str(raw_row["page_no"]),
                "attempt": str(raw_row["attempt"]),
                "runtime-lock-id": str(raw_row["runtime_lock_id"]),
                "pilot-run-id": str(raw_row["pilot_run_id"]),
                "quota-day-kst": str(raw_row["quota_day_kst"]),
                "provider-call-started-at-utc": str(raw_row["provider_call_started_at_utc"]),
                "socket-opened-at-utc": str(raw_row["socket_opened_at_utc"]),
                "response-received-at-utc": str(raw_row["response_received_at_utc"]),
                "reservation-checkpoint-revision": str(raw_row["reservation_checkpoint_revision"]),
                "reservation-checkpoint-token-sha256": str(raw_row["reservation_checkpoint_token_sha256"]),
                "provider-call-checkpoint-revision": str(raw_row["provider_call_checkpoint_revision"]),
                "provider-call-checkpoint-token-sha256": str(raw_row["provider_call_checkpoint_token_sha256"]),
                "execution-claim-version-id": str(raw_row["execution_claim_version_id"]),
                "execution-claim-content-sha256": str(raw_row["execution_claim_content_sha256"]),
            },
            "RAW_METADATA_FINAL_CHECKPOINT_LINEAGE_MISMATCH",
        )
        matching_attempts = [
            row for row in final_attempts
            if row.get("basDt") == raw_row.get("basDt")
            and row.get("page_no") == raw_row.get("page_no")
            and row.get("attempt") == raw_row.get("attempt")
        ]
        require(len(matching_attempts) == 1, "RAW_INDEX_ATTEMPT_CARDINALITY_MISMATCH")
        attempt = matching_attempts[0]
        for attempt_key, raw_key in (
            ("object_key", "s3_object_key"),
            ("entity_sha256", "entity_sha256"),
            ("entity_bytes", "entity_bytes"),
            ("s3_version_id", "s3_version_id"),
            ("s3_etag", "s3_etag"),
            ("reservation_checkpoint_revision", "reservation_checkpoint_revision"),
            ("reservation_checkpoint_token_sha256", "reservation_checkpoint_token_sha256"),
            ("provider_call_checkpoint_revision", "provider_call_checkpoint_revision"),
            ("provider_call_checkpoint_token_sha256", "provider_call_checkpoint_token_sha256"),
            ("execution_claim_version_id", "execution_claim_version_id"),
            ("execution_claim_content_sha256", "execution_claim_content_sha256"),
        ):
            require(attempt.get(attempt_key) == raw_row.get(raw_key), "RAW_INDEX_ATTEMPT_LINEAGE_MISMATCH_" + attempt_key)
    require(sha256_bytes(claim_body) == claim_binding["content_sha256"] and claim_head.get("ETag") == claim_binding["etag"], "CLAIM_BODY_BINDING_MISMATCH")
    claim_list_row = inventories["claim"]["versions"][0]
    require(claim_list_row["Size"] == len(claim_body) and claim_list_row["ETag"] == claim_head.get("ETag"), "CLAIM_LIST_GET_METADATA_MISMATCH")
    try:
        claim_json = json.loads(claim_body)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ForensicAuditError("CLAIM_JSON_INVALID") from exc
    require(isinstance(claim_json, dict) and claim_body == canonical_json_bytes(claim_json), "CLAIM_NOT_CANONICAL_JSON_LF")
    expected_claim = {
        "artifact": "M3TOP3_FINANCE_PAGE100_EXECUTION_CLAIM_v1.0",
        "state": "SINGLE_WRITER_CLAIMED",
        "runtime_lock_id": final_checkpoint["runtime_lock_id"],
        "pilot_run_id": final_checkpoint["pilot_run_id"],
        "writer_id": claim_binding["writer_id"],
        "github_run_id": 33273146915,
        "github_run_attempt": 1,
        "activation_base_head_commit": final_checkpoint["activation_base_head_commit"],
        "owner_cap_spec_sha256": final_checkpoint["owner_cap_spec_sha256"],
        "execution_token_sha256": final_checkpoint["execution_token_sha256"],
        "predecessor_workflow_run_id": final_checkpoint["inherited_predecessor"]["workflow_run_id"],
        "predecessor_rerun": False,
    }
    require(claim_json == expected_claim, "CLAIM_EXACT_SCHEMA_OR_BINDING_MISMATCH")

    inherited = history["by_revision"][0]["issuer_identity_hashes"]
    require(inherited == predecessor["issuer_identity_hashes"], "REV0_PREDECESSOR_IDENTITY_BASELINE_MISMATCH")
    require(len(inherited) == 12 and sha256_bytes(canonical_json_bytes(inherited)) == REV0_IDENTITY_MAP_SHA256, "REV0_IDENTITY_BASELINE_HASH_MISMATCH")
    classification = classify_conflicts(pages, inherited)
    require(classification["rows_checked"] == 40 and classification["match_rows"] == 38 and classification["conflicts"] == 2 and classification["missing_rows"] == 0, "REPLAY_IDENTITY_COUNTER_MISMATCH")
    require(classification["final_identity_hashes"] == final_checkpoint["issuer_identity_hashes"], "REPLAY_FINAL_IDENTITY_MAP_MISMATCH")
    require(all(row["basDt"] == "20240131" and row["page_no"] == 4 for row in classification["conflict_specimens"]), "CONFLICT_LOCATION_MISMATCH")
    page_vectors = [classify_conflicts(pages[:index], inherited) for index in range(1, 5)]
    require(
        [page["page_no"] for page in pages] == [1, 2, 3, 4]
        and [page["page_size"] for page in pages] == [10, 10, 10, 10]
        and [page["total_count"] for page in pages] == [275, 275, 275, 275]
        and [len(page["items"]) for page in pages] == [10, 10, 10, 10],
        "RAW_PAGE_AGGREGATE_VECTOR_MISMATCH",
    )
    require(
        [row["rows_checked"] for row in page_vectors] == [10, 20, 30, 40]
        and [row["match_rows"] for row in page_vectors] == [10, 20, 30, 38]
        and [row["conflicts"] for row in page_vectors] == [0, 0, 0, 2]
        and [row["missing_rows"] for row in page_vectors] == [0, 0, 0, 0],
        "CONFLICT_PAGE_VECTOR_MISMATCH",
    )

    checkpoint_projection = []
    for record in checkpoint_records:
        checkpoint = record["checkpoint"]
        identity_map = checkpoint.get("issuer_identity_hashes", {})
        checkpoint_projection.append(
            {
                "revision": record["revision"], "version_id": record["version_id"],
                "sha256": record["sha256"], "bytes": record["bytes"],
                "etag": record["etag"], "is_latest": record["is_latest"],
                "last_modified": record["last_modified"], "state": checkpoint.get("state"),
                "last_error_class": checkpoint.get("last_error_class"),
                "network_attempts_started_conservative": checkpoint.get("network_attempts_started_conservative"),
                "provider_api_network_attempts": checkpoint.get("provider_api_network_attempts"),
                "quota_reservations": checkpoint.get("quota_reservations"),
                "remote_raw_custody_writes": checkpoint.get("remote_raw_custody_writes"),
                "response_entities_received": checkpoint.get("response_entities_received"),
                "issuer_identity_rows_checked": checkpoint.get("issuer_identity_rows_checked"),
                "issuer_identity_match_rows": checkpoint.get("issuer_identity_match_rows"),
                "issuer_identity_conflicts": checkpoint.get("issuer_identity_conflicts"),
                "issuer_identity_missing_rows": checkpoint.get("issuer_identity_missing_rows"),
                "identity_map_count": len(identity_map),
                "identity_map_sha256": sha256_bytes(canonical_json_bytes(identity_map)),
                "raw_index_count": len(checkpoint.get("raw_index", [])),
                "checkpoint_token_sha256": checkpoint_token_sha256(record),
            }
        )

    sanitized_conflicts = []
    for global_ordinal, conflict in enumerate(classification["conflict_specimens"], 1):
        observed = conflict["observed_identity"]
        accepted = conflict["accepted_current_specimen"]
        field_equality = (
            {
                key + "_equal": accepted.get(key) == observed.get(key)
                for key in ("issuCmpyKsdCustNo", "crno", "stckIssuCmpyNm")
            }
            if isinstance(accepted, dict)
            else {
                "issuCmpyKsdCustNo_equal": "UNKNOWN_NOT_READ_UNDER_APPROVED_SCOPE",
                "crno_equal": "UNKNOWN_NOT_READ_UNDER_APPROVED_SCOPE",
                "stckIssuCmpyNm_equal": "UNKNOWN_NOT_READ_UNDER_APPROVED_SCOPE",
            }
        )
        sanitized_conflicts.append(
            {
                "basDt": conflict["basDt"], "page_no": conflict["page_no"],
                "page_item_ordinal": conflict["item_index"],
                "conflict_ordinal": global_ordinal,
                "global_row_ordinal": (int(conflict["page_no"]) - 1) * 10 + int(conflict["item_index"]),
                "custody_key_sha256": sha256_bytes(observed["issuCmpyKsdCustNo"].encode("utf-8")),
                "frozen_identity_sha256": conflict["frozen_identity_sha256"],
                "observed_identity_sha256": conflict["observed_identity_sha256"],
                "field_equality_flags": field_equality,
                "cause": "UNKNOWN_NOT_DECIDED_BY_READ_ONLY_FORENSIC_SCOPE",
                "prior_raw_tuple": "UNKNOWN_NOT_READ_UNDER_APPROVED_SCOPE",
            }
        )
    sanitized_replay = {
        "rows_checked": classification["rows_checked"],
        "match_rows": classification["match_rows"],
        "conflict_rows": classification["conflicts"],
        "missing_rows": classification["missing_rows"],
        "distinct_conflict_custody_key_digests": len({row["custody_key_sha256"] for row in sanitized_conflicts}),
        "page_vectors": [
            {"page_no": index, "rows_checked": row["rows_checked"], "match_rows": row["match_rows"], "conflict_rows": row["conflicts"], "missing_rows": row["missing_rows"]}
            for index, row in enumerate(page_vectors, 1)
        ],
        "conflict_rows_exact": sanitized_conflicts,
        "final_identity_map_count": len(classification["final_identity_hashes"]),
        "final_identity_map_sha256": sha256_bytes(canonical_json_bytes(classification["final_identity_hashes"])),
    }

    evidence = {
        "artifact": "M3TOP3_FINANCE_CA_PAGE100_G10_READ_ONLY_FORENSIC_EVIDENCE_v1.0",
        "state": "COMPLETE_EXACT_READ_ONLY_FORENSIC_EVIDENCE",
        "repository": REPOSITORY,
        "branch": BRANCH,
        "git_lineage": dict(git_lineage),
        "owner_authorization": authority["owner_authorization"],
        "g10_terminal_receipt": {
            "commit_sha": BASE_RECEIPT_COMMIT, "tree_sha": BASE_RECEIPT_TREE,
            "path": TERMINAL_RECEIPT_PATH, "sha256": TERMINAL_RECEIPT_SHA256,
            "git_blob_sha": TERMINAL_RECEIPT_BLOB, "bytes": TERMINAL_RECEIPT_BYTES,
        },
        "aws_read_only_session": {
            "account_id": ACCOUNT_ID, "region": REGION, "bucket": BUCKET,
            "caller_arn_sha256": sha256_bytes(str(caller.get("Arn") or "").encode()),
            "allowed_prefixes": [RAW_PREFIX, CONTROL_PREFIX, CLAIM_KEY],
            "aws_cli_read_call_counts": dict(sorted(client.call_counts.items())),
        },
        "version_histories": {
            "raw": _inventory_projection(inventories["raw"]),
            "control": _inventory_projection(inventories["control"]),
            "execution_claim": _inventory_projection(inventories["claim"]),
            "all_delete_marker_counts": {name: len(value["delete_markers"]) for name, value in inventories.items()},
        },
        "checkpoint_versions": checkpoint_projection,
        "issuer_identity_replay": sanitized_replay,
        "effect_classification": {
            "finance_provider_api_calls": 0, "quota_reservations": 0,
            "s3_put_object_calls": 0, "s3_delete_object_calls": 0,
            "remote_custody_mutations": 0, "aws_read_only_session_established": 1,
            "raw_exact_version_gets": 4, "checkpoint_exact_version_gets": 28,
            "execution_claim_exact_version_gets": 1,
            "normalization_records": 0, "promotion_actions": 0,
        },
        "claim_ceiling": {
            "model_semantic_change": False, "pit_semantic_change": False,
            "evidence_semantic_change": False, "validation_claim": "NONE",
            "gate_effect": "NONE", "production_authority": False,
        },
        "sanitization": {
            "raw_bodies_persisted": False, "provider_secret_values_persisted": False,
            "aws_credentials_persisted": False, "authenticated_urls_persisted": False,
            "clear_issuer_identity_fields_persisted": False,
            "conflict_identity_material": "HASH_ONLY",
        },
    }
    evidence_bytes = canonical_json_bytes(evidence)
    evidence_text = evidence_bytes.decode("utf-8")
    require(not any(pattern.search(evidence_text) for pattern in BANNED_EVIDENCE_PATTERNS), "EVIDENCE_SANITIZATION_SCAN_FAILED")
    evidence_path = output_dir / "g10-readonly-forensic-evidence.json"
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    evidence_path.write_bytes(evidence_bytes)
    evidence_sha = sha256_bytes(evidence_bytes)

    receipt_out = {
        "artifact": "M3TOP3_FINANCE_CA_PAGE100_G10_READ_ONLY_FORENSIC_RUN_RECEIPT_v1.0",
        "state": "TERMINAL_SUCCESS_READ_ONLY_EXACT_HISTORY_AND_CONFLICT_SPECIMENS_PROVEN",
        "repository": REPOSITORY, "branch": BRANCH,
        "workflow": {
            "run_id": int(os.environ.get("GITHUB_RUN_ID", "0")),
            "run_attempt": int(os.environ.get("GITHUB_RUN_ATTEMPT", "0")),
            "job": os.environ.get("GITHUB_JOB", "UNKNOWN"),
            "head_sha": git_lineage["activation_head_sha"],
        },
        "owner_authorization": authority["owner_authorization"],
        "evidence": {"filename": evidence_path.name, "sha256": evidence_sha, "bytes": len(evidence_bytes)},
        "findings": {
            "raw_versions": 4, "checkpoint_versions": 28, "existing_s3_put_versions_exact": 33,
            "checkpoint_revisions": "0..27", "execution_claim_versions": 1,
            "delete_markers": 0, "issuer_identity_conflicts": 2,
            "conflict_rows_exactly_identified_hash_only": True,
        },
        "effects": evidence["effect_classification"],
        "claim_ceiling": evidence["claim_ceiling"],
        "prohibitions_preserved": {
            "g10_rerun": True, "g11_generation": True, "finance_provider_calls": True,
            "quota_reservations": True, "s3_mutations": True,
            "semantic_change": True, "normalization_promotion_release_production": True,
        },
        "next_decision": "OWNER_REVIEW_EXACT_CONFLICT_SPECIMENS_NO_AUTOMATIC_SEMANTIC_CHANGE",
    }
    receipt_bytes = canonical_json_bytes(receipt_out)
    require(not any(pattern.search(receipt_bytes.decode("utf-8")) for pattern in BANNED_EVIDENCE_PATTERNS), "RECEIPT_SANITIZATION_SCAN_FAILED")
    receipt_path = output_dir / "g10-readonly-forensic-run-receipt.json"
    receipt_path.write_bytes(receipt_bytes)
    sanitization = {
        "artifact": "M3TOP3_FINANCE_CA_PAGE100_G10_READ_ONLY_FORENSIC_SANITIZATION_RECEIPT_v1.0",
        "state": "PASS",
        "files": {
            evidence_path.name: {"sha256": evidence_sha, "bytes": len(evidence_bytes)},
            receipt_path.name: {"sha256": sha256_bytes(receipt_bytes), "bytes": len(receipt_bytes)},
        },
        "raw_bodies_in_actions_artifact": 0,
        "secret_values_in_actions_artifact": 0,
        "authenticated_urls_in_actions_artifact": 0,
    }
    write_canonical_json(output_dir / "sanitization-receipt.json", sanitization)
    return receipt_out


def _load_all(args: argparse.Namespace) -> tuple[dict[str, Any], ...]:
    authority_path = pathlib.Path(args.authority)
    activation_path = pathlib.Path(args.activation)
    receipt_path = pathlib.Path(args.receipt)
    predecessor_path = pathlib.Path(args.predecessor_checkpoint)
    manifest_path = pathlib.Path(args.manifest)
    require(sha256_bytes(receipt_path.read_bytes()) == TERMINAL_RECEIPT_SHA256 and len(receipt_path.read_bytes()) == TERMINAL_RECEIPT_BYTES, "TERMINAL_RECEIPT_LOCAL_BYTES_MISMATCH")
    require(sha256_bytes(predecessor_path.read_bytes()) == PREDECESSOR_CHECKPOINT_SHA256 and len(predecessor_path.read_bytes()) == PREDECESSOR_CHECKPOINT_BYTES, "PREDECESSOR_CHECKPOINT_LOCAL_BYTES_MISMATCH")
    source_path = pathlib.Path(SOURCE_ADMISSION_PATH)
    require(source_path.is_file(), "SOURCE_ADMISSION_FILE_MISSING")
    source_bytes = source_path.read_bytes()
    require(len(source_bytes) == SOURCE_ADMISSION_BYTES and sha256_bytes(source_bytes) == SOURCE_ADMISSION_SHA256, "SOURCE_ADMISSION_LOCAL_BYTES_MISMATCH")
    return (
        load_canonical_json(authority_path), load_canonical_json(activation_path),
        load_canonical_json(receipt_path), load_canonical_json(predecessor_path),
        load_canonical_json(manifest_path),
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("preflight", "audit"):
        sub = subparsers.add_parser(command)
        sub.add_argument("--authority", required=True)
        sub.add_argument("--activation", required=True)
        sub.add_argument("--receipt", required=True)
        sub.add_argument("--predecessor-checkpoint", required=True)
        sub.add_argument("--manifest", required=True)
        if command == "preflight":
            sub.add_argument("--verify-owner-comment", action="store_true")
        else:
            sub.add_argument("--output-dir", required=True)
    remote = subparsers.add_parser("remote-gate")
    remote.add_argument("--activation", required=True)
    remote.add_argument("--phase", required=True, choices=("before-aws", "before-artifact"))
    args = parser.parse_args(argv)
    if args.command == "remote-gate":
        activation = load_canonical_json(pathlib.Path(args.activation))
        require(activation.get("artifact") == "M3TOP3_FINANCE_CA_PAGE100_G10_FORENSIC_ACTIVATION_v1.0", "REMOTE_GATE_ACTIVATION_ARTIFACT_MISMATCH")
        result = verify_remote_execution_gate(
            os.environ.get("GITHUB_TOKEN", ""), activation, args.phase
        )
        print(json.dumps(result, sort_keys=True, separators=(",", ":")))
        return 0
    authority, activation, receipt, predecessor, manifest = _load_all(args)
    validate_static_contract(authority, activation, receipt, predecessor, manifest)
    git_lineage = validate_git_activation(activation)
    if args.command == "preflight":
        if args.verify_owner_comment:
            verify_owner_comment(os.environ.get("GITHUB_TOKEN", ""))
        print(json.dumps({"state": "PASS", **git_lineage}, sort_keys=True, separators=(",", ":")))
        return 0
    run_audit(authority, activation, receipt, predecessor, git_lineage, pathlib.Path(args.output_dir))
    print("G10_READ_ONLY_FORENSIC_AUDIT_COMPLETE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
