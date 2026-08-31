#!/usr/bin/env python3
"""Zero-external-effect PRECHECK for hash-only G10 issuer-group exclusion.

This module has no network, AWS, provider, quota, or persistence capability.
It validates the preparation bundle and supplies a pure in-memory projection
function for focused tests. Reading the four sealed raw object versions is a
separate, future authority boundary.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import pathlib
import re
import xml.etree.ElementTree as ET
from collections.abc import Mapping, Sequence
from typing import Any


REPOSITORY = "AofSpds/asset-agent-asa"
BRANCH = "aaa-pmo-public-data-g2-g3-source-admission-v1-20260828"
PREPARATION_PARENT_HEAD_SHA = "85b6467adc52c08bb469083473a34d784afbc019"
PREPARATION_PARENT_TREE_SHA = "526d3a9787ce60e6f0e16830ad0909056fcbc05d"
PREPARATION_MESSAGE = (
    "Prepare G10 issuer-group exclusion enumeration PRECHECK v1.0"
)
ACTIVATION_MESSAGE = (
    "Arm G10 issuer-group exclusion enumeration PRECHECK once v1.0"
)

CONTROL_ROOT = "control/m3top3/public-data-source-admission/v1.0"
AUTHORITY_PATH = (
    f"{CONTROL_ROOT}/M3TOP3_FINANCE_CA_PAGE100_G10_ISSUER_CONFLICT_"
    "EXCLUSION_REMEDIATION_ENUMERATION_PRECHECK_AUTHORITY_v1.0.json"
)
MANIFEST_PATH = (
    f"{CONTROL_ROOT}/M3TOP3_FINANCE_CA_PAGE100_G10_ISSUER_CONFLICT_"
    "EXCLUSION_REMEDIATION_ENUMERATION_PRECHECK_MANIFEST_v1.0.json"
)
ACTIVATION_PATH = (
    f"{CONTROL_ROOT}/M3TOP3_FINANCE_CA_PAGE100_G10_ISSUER_CONFLICT_"
    "EXCLUSION_REMEDIATION_ENUMERATION_PRECHECK_ACTIVATION_v1.0.json"
)
ACTIVATION_TEMPLATE_PATH = ACTIVATION_PATH + ".template"
DECISION_RECEIPT_PATH = (
    f"{CONTROL_ROOT}/M3TOP3_FINANCE_CA_PAGE100_G10_ISSUER_CONFLICT_"
    "OWNER_DECISION_RECEIPT_v1.1.json"
)
RUNNER_PATH = (
    "tools/m3top3/"
    "finance_page100_g10_issuer_conflict_exclusion_enumeration_precheck.py"
)
TEST_PATH = (
    "tools/m3top3/tests/"
    "test_finance_page100_g10_issuer_conflict_exclusion_enumeration_precheck.py"
)
WORKFLOW_PATH = (
    ".github/workflows/m3top3-finance-page100-g10-issuer-conflict-"
    "exclusion-remediation-enumeration-precheck-v1.yml"
)

TARGET_CUSTODY_KEY_SHA256 = (
    "f3e7b94dbde722df47cc3bb1a5615068cea42dc1994a91ce92317f5d1fb8b3d6"
)
FROZEN_IDENTITY_SHA256 = (
    "d95a27a7c79ae4bda4c8170db30f2d4bc395faff904b55dbcbaeb10e3f6f9c21"
)
OBSERVED_IDENTITY_SHA256 = (
    "d1d37a0df09e0aa73c1dd350b4a8be2b62172dfcca27bf8dede4a925bdeacb03"
)
KNOWN_CONFLICT_GLOBAL_ORDINALS = (37, 39)
EXPECTED_BASE_DATE = "20240131"
EXPECTED_SOURCE_ROWS = 40
EXPECTED_SOURCE_MATCH_ROWS = 38
EXPECTED_SOURCE_CONFLICT_ROWS = 2
EXPECTED_SOURCE_MISSING_ROWS = 0
EXPECTED_TOTAL_COUNT = 275
EXPECTED_BASELINE_PROJECTION_SHA256 = (
    "426a3a34725b32455035825c2674605d220d5ad05dde7d19862caaad1933a9b8"
)

EXPECTED_SEALED_SOURCE_BINDINGS = {
    "acquisition_predecessor_checkpoint": {
        "bytes": 37979,
        "git_blob_sha": "eeda311c19724fb8c13ab20e3bdc1469853da8ad",
        "path": (
            f"{CONTROL_ROOT}/M3TOP3_FINANCE_CA_ACQUISITION_CHECKPOINT_v1.0.json"
        ),
        "sha256": (
            "9a18edaf66b9f03b2202dbef11c0f86472340695c0c245f0a8ca958e3cfce55d"
        ),
    },
    "forensic_s4_authority": {
        "bytes": 12136,
        "git_blob_sha": "7514407afd57a4927590211e66bcd125c795d04d",
        "path": f"{CONTROL_ROOT}/M3TOP3_FINANCE_CA_PAGE100_G10_FORENSIC_S4_AUTHORITY_v1.0.json",
        "sha256": (
            "bc463ad35cecdee14d0c13410ffb7c858aec46f93e9334ed74cf4e75a25541ec"
        ),
    },
    "forensic_s4_terminal": {
        "bytes": 35681,
        "git_blob_sha": "134eff09eed3ee85db21db4c3f2ff0626a04c31d",
        "path": (
            f"{CONTROL_ROOT}/M3TOP3_FINANCE_CA_PAGE100_G10_FORENSIC_S4_"
            "AUDIT_TERMINAL_RECEIPT_33305734866_v1.0.json"
        ),
        "sha256": (
            "6ebd945c1551b0247fd9b9a6177871acc42fc1edc279c7cd0b5c543c5c61b869"
        ),
    },
    "issuer_conflict_reproduction": {
        "bytes": 2587,
        "git_blob_sha": "b140afc108b3003c7f29d00ed6cfde9df6de35d3",
        "path": (
            f"{CONTROL_ROOT}/evidence/g10-readonly-forensic-s4-audit-33305734866/"
            "issuer-conflict-reproduction.json"
        ),
        "sha256": (
            "a40f0d94ef543d0c24643a1075913d43b97f49d04ed879d9b6a832417916755f"
        ),
    },
    "raw_version_manifest": {
        "bytes": 5157,
        "git_blob_sha": "db096f0f7509d5a27f86d55e9cff8e87462b8d6a",
        "path": (
            f"{CONTROL_ROOT}/evidence/g10-readonly-forensic-s4-audit-33305734866/"
            "raw-version-manifest.json"
        ),
        "sha256": (
            "01087a6faddc536e6a97ebfbb0ec8b78f47133a9cac7a8f55da31d9e174d206e"
        ),
    },
}

EXPECTED_EXACT_RAW_VERSIONS = (
    {
        "bytes": 4642,
        "page_no": 1,
        "s3_object_key": (
            "raw/public-data-api/M3TOP3-FINANCE-STOCK-RIGHTS-v1/_pilot_generation/"
            "runtime_lock_id=PMO-FINANCE-PAGE100-G10-20260830044522/"
            "pilot_run_id=FINANCE-PAGE100-PILOT-G10-20260830044522/"
            "getRighExerReasSche_V2/quota_day_kst=2026-08-30/"
            "request_id=2336abe1c81d4c86f90fef6575e204d0455367d4d5e8ed6cce103a752f0330da/"
            "attempt=1/sha256=2e97f391bcf833db568de2c8638c5ff6d297ea07be21efc3fca6d05cd266c309.entity"
        ),
        "sha256": "2e97f391bcf833db568de2c8638c5ff6d297ea07be21efc3fca6d05cd266c309",
        "version_id": "VdsI_D_jNujHIb9ff8loyRWtuAW737RI",
    },
    {
        "bytes": 4697,
        "page_no": 2,
        "s3_object_key": (
            "raw/public-data-api/M3TOP3-FINANCE-STOCK-RIGHTS-v1/_pilot_generation/"
            "runtime_lock_id=PMO-FINANCE-PAGE100-G10-20260830044522/"
            "pilot_run_id=FINANCE-PAGE100-PILOT-G10-20260830044522/"
            "getRighExerReasSche_V2/quota_day_kst=2026-08-30/"
            "request_id=dea3a2edfa78a4ebe2f912d2a8d8fa90456e960ad4cdbb832e501c91dd71d41c/"
            "attempt=1/sha256=385cf9c3d3ba69c623ada225e8dd76fff8ce615658f7c37113f0cd326594fbb9.entity"
        ),
        "sha256": "385cf9c3d3ba69c623ada225e8dd76fff8ce615658f7c37113f0cd326594fbb9",
        "version_id": "30whtf2xTpWQYXPmr.Kt5RBnK1Y_YDI4",
    },
    {
        "bytes": 4570,
        "page_no": 3,
        "s3_object_key": (
            "raw/public-data-api/M3TOP3-FINANCE-STOCK-RIGHTS-v1/_pilot_generation/"
            "runtime_lock_id=PMO-FINANCE-PAGE100-G10-20260830044522/"
            "pilot_run_id=FINANCE-PAGE100-PILOT-G10-20260830044522/"
            "getRighExerReasSche_V2/quota_day_kst=2026-08-30/"
            "request_id=eb594842fb4aa2c9a131efbb7b64f4bb72f3678315fa352224132355bd0be1de/"
            "attempt=1/sha256=ef7ef262d0cc39c703b98bc8321c75d5c715bd58b6a0677d8897de9e43e49ce9.entity"
        ),
        "sha256": "ef7ef262d0cc39c703b98bc8321c75d5c715bd58b6a0677d8897de9e43e49ce9",
        "version_id": "1dHYBfs4hg1tM7S6TckyUngOmfwWKZc2",
    },
    {
        "bytes": 4821,
        "page_no": 4,
        "s3_object_key": (
            "raw/public-data-api/M3TOP3-FINANCE-STOCK-RIGHTS-v1/_pilot_generation/"
            "runtime_lock_id=PMO-FINANCE-PAGE100-G10-20260830044522/"
            "pilot_run_id=FINANCE-PAGE100-PILOT-G10-20260830044522/"
            "getRighExerReasSche_V2/quota_day_kst=2026-08-30/"
            "request_id=75494b2b71aeb1dcfd52e2cba2198e933fef2ad271c900328085da375dd9989c/"
            "attempt=1/sha256=8ab2eec3af93ef2a26097a65d8f0964471160e222245a6e2ae3b79adac69afe1.entity"
        ),
        "sha256": "8ab2eec3af93ef2a26097a65d8f0964471160e222245a6e2ae3b79adac69afe1",
        "version_id": "iBxAq9V.V7eA_doOM39JcVt_gtzAHskI",
    },
)

ACTIVATION_ARTIFACT = (
    "M3TOP3_FINANCE_CA_PAGE100_G10_ISSUER_CONFLICT_EXCLUSION_REMEDIATION_"
    "ENUMERATION_PRECHECK_ACTIVATION_v1.0"
)
ACTIVATION_STATE = "ARMED_ZERO_EXTERNAL_EFFECT_PRECHECK_ONCE"

HASH_RE = re.compile(r"[0-9a-f]{64}")
GIT_SHA_RE = re.compile(r"[0-9a-f]{40}")
ACTIVATION_ID_RE = re.compile(
    r"G10-ISSUER-GROUP-EXCLUSION-ENUMERATION-PRECHECK-ACTIVATION-[0-9]{14}"
)
RUNTIME_LOCK_RE = re.compile(
    r"PMO-G10-ISSUER-GROUP-EXCLUSION-ENUMERATION-PRECHECK-[0-9]{14}"
)
UTC_TIMESTAMP_RE = re.compile(
    r"20[0-9]{2}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z"
)
CLEAR_IDENTITY_KEYS = frozenset(
    {"issuCmpyKsdCustNo", "crno", "stckIssuCmpyNm"}
)


class ExclusionPrecheckError(RuntimeError):
    """Fail-closed preparation or pure-projection error."""


def require(condition: bool, code: str) -> None:
    if not condition:
        raise ExclusionPrecheckError(code)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob_sha_bytes(data: bytes) -> str:
    header = b"blob " + str(len(data)).encode("ascii") + b"\0"
    return hashlib.sha1(header + data).hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        + b"\n"
    )


def load_canonical_json(path: pathlib.Path) -> dict[str, Any]:
    raw = path.read_bytes()
    require(raw.endswith(b"\n") and not raw.endswith(b"\n\n"), "JSON_NEWLINE_INVALID")
    try:
        value = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ExclusionPrecheckError("JSON_PARSE_INVALID") from exc
    require(isinstance(value, dict), "JSON_ROOT_NOT_OBJECT")
    require(raw == canonical_json_bytes(value), "JSON_NOT_CANONICAL")
    return value


def issuer_identity_digest(item: Mapping[str, Any]) -> str:
    identity = {
        "crno": str(item.get("crno") or ""),
        "issuCmpyKsdCustNo": str(item.get("issuCmpyKsdCustNo") or ""),
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
        key = _local_name(child.tag)
        value = _xml_to_value(child)
        if key in grouped:
            if not isinstance(grouped[key], list):
                grouped[key] = [grouped[key]]
            grouped[key].append(value)
        else:
            grouped[key] = value
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
            raise ExclusionPrecheckError("ENTITY_JSON_PARSE_INVALID") from exc
    if payload.startswith(b"<"):
        upper = payload.upper()
        require(b"<!DOCTYPE" not in upper and b"<!ENTITY" not in upper, "XML_DTD_PROHIBITED")
        try:
            root = ET.fromstring(payload)
        except ET.ParseError as exc:
            raise ExclusionPrecheckError("XML_PARSE_INVALID") from exc
        return {_local_name(root.tag): _xml_to_value(root)}
    raise ExclusionPrecheckError("ENTITY_NOT_JSON_OR_XML")


def _find_first(value: Any, names: tuple[str, ...]) -> Any:
    if isinstance(value, Mapping):
        for name in names:
            if name in value and not isinstance(value[name], (Mapping, list)):
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
    if isinstance(value, Mapping):
        if "item" in value:
            item = value["item"]
            if item in (None, ""):
                return []
            if isinstance(item, Mapping):
                return [dict(item)]
            require(
                isinstance(item, list) and all(isinstance(row, Mapping) for row in item),
                "ITEM_SHAPE_INVALID",
            )
            return [dict(row) for row in item]
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


def _strict_uint(value: Any, code: str, *, positive: bool = False) -> int:
    text = str(value) if value is not None else ""
    require(bool(re.fullmatch(r"[0-9]+", text)), code)
    parsed = int(text)
    require(parsed >= (1 if positive else 0), code)
    return parsed


def parse_finance_entity(
    body: bytes,
    expected_bas_dt: str,
    expected_page_no: int,
    expected_page_size: int = 10,
    expected_total_count: int = EXPECTED_TOTAL_COUNT,
) -> dict[str, Any]:
    require(isinstance(body, bytes) and 0 < len(body) <= 100_000, "RAW_ENTITY_SIZE_INVALID")
    parsed = _parse_entity_value(body)
    require(_find_first(parsed, ("resultCode",)) == "00", "FINANCE_RESULT_CODE_NOT_00")
    page_no = _strict_uint(_find_first(parsed, ("pageNo",)), "PAGE_NO_INVALID", positive=True)
    page_size = _strict_uint(_find_first(parsed, ("numOfRows",)), "PAGE_SIZE_INVALID", positive=True)
    total_count = _strict_uint(_find_first(parsed, ("totalCount", "totalCnt")), "TOTAL_COUNT_INVALID")
    require(page_no == expected_page_no, "PAGE_NO_MISMATCH")
    require(page_size == expected_page_size, "PAGE_SIZE_MISMATCH")
    require(total_count == expected_total_count, "TOTAL_COUNT_MISMATCH")
    items = _find_items(parsed)
    require(len(items) == expected_page_size, "PAGE_ITEM_COUNT_INVALID")
    for item in items:
        require(
            _find_first(item, ("basDt",)) == expected_bas_dt,
            "ITEM_BASE_DATE_MISMATCH",
        )
    return {
        "basDt": expected_bas_dt,
        "items": items,
        "page_no": page_no,
        "page_size": page_size,
        "total_count": total_count,
    }


def _validate_hash(value: str, code: str) -> None:
    require(isinstance(value, str) and bool(HASH_RE.fullmatch(value)), code)


def _require_exact_integer_mapping(
    value: Any,
    expected: Mapping[str, int],
    code: str,
) -> None:
    require(
        isinstance(value, Mapping)
        and set(value) == set(expected)
        and all(
            type(value.get(key)) is int and value.get(key) == expected_value
            for key, expected_value in expected.items()
        ),
        code,
    )


def _parse_real_utc_timestamp(value: Any, code: str) -> dt.datetime:
    require(
        isinstance(value, str) and bool(UTC_TIMESTAMP_RE.fullmatch(value)),
        code,
    )
    try:
        parsed = dt.datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError as exc:
        raise ExclusionPrecheckError(code) from exc
    return parsed.replace(tzinfo=dt.timezone.utc)


def _walk_for_clear_keys(value: Any) -> bool:
    if isinstance(value, Mapping):
        if any(key in CLEAR_IDENTITY_KEYS for key in value):
            return True
        return any(_walk_for_clear_keys(child) for child in value.values())
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return any(_walk_for_clear_keys(child) for child in value)
    return False


def _build_hash_only_exclusion_projection_from_verified_pages(
    pages: Sequence[Mapping[str, Any]],
    *,
    inherited_identity_hashes_by_custody_sha256: Mapping[str, str],
    target_custody_key_sha256: str,
    frozen_identity_sha256: str,
    observed_identity_sha256: str,
    expected_bas_dt: str = EXPECTED_BASE_DATE,
    known_conflict_global_ordinals: Sequence[int] = KNOWN_CONFLICT_GLOBAL_ORDINALS,
    sealed_source_match_rows: int = EXPECTED_SOURCE_MATCH_ROWS,
    sealed_source_conflict_rows: int = EXPECTED_SOURCE_CONFLICT_ROWS,
    sealed_source_missing_rows: int = EXPECTED_SOURCE_MISSING_ROWS,
) -> dict[str, Any]:
    """Build a sanitized company-wide exclusion projection from in-memory pages.

    This is an internal pure core for the authority-bound public entry point and
    synthetic unit tests; execution code must call build_hash_only_exclusion_projection.
    Clear source values are used only while hashing. They are never returned.
    Every source row is classified sequentially before the selector is applied.
    The selector then removes every occurrence, including prior matching rows.
    """

    _validate_hash(target_custody_key_sha256, "TARGET_DIGEST_INVALID")
    _validate_hash(frozen_identity_sha256, "FROZEN_IDENTITY_DIGEST_INVALID")
    _validate_hash(observed_identity_sha256, "OBSERVED_IDENTITY_DIGEST_INVALID")
    require(frozen_identity_sha256 != observed_identity_sha256, "CANDIDATE_DIGESTS_EQUAL")
    require(len(pages) == 4, "FOUR_PAGES_REQUIRED")
    require(
        [int(page.get("page_no") or 0) for page in pages] == [1, 2, 3, 4],
        "PAGE_ORDER_INVALID",
    )
    require(
        all(str(page.get("basDt") or "") == expected_bas_dt for page in pages),
        "PAGE_BASE_DATE_MISMATCH",
    )
    require(
        sealed_source_match_rows == 38
        and sealed_source_conflict_rows == 2
        and sealed_source_missing_rows == 0,
        "SEALED_SOURCE_COUNTER_BINDING_MISMATCH",
    )

    require(
        isinstance(inherited_identity_hashes_by_custody_sha256, Mapping)
        and len(inherited_identity_hashes_by_custody_sha256) == 12
        and all(
            isinstance(key, str)
            and isinstance(value, str)
            and bool(HASH_RE.fullmatch(key))
            and bool(HASH_RE.fullmatch(value))
            for key, value in inherited_identity_hashes_by_custody_sha256.items()
        ),
        "BASELINE_IDENTITY_MAP_INVALID",
    )
    require(
        sha256_bytes(
            canonical_json_bytes(
                dict(sorted(inherited_identity_hashes_by_custody_sha256.items()))
            )
        )
        == EXPECTED_BASELINE_PROJECTION_SHA256,
        "BASELINE_AUTHORITY_BINDING_MISMATCH",
    )
    identities = dict(inherited_identity_hashes_by_custody_sha256)
    target_rows: list[dict[str, Any]] = []
    eligible_hash_projection: list[dict[str, Any]] = []
    custody_preimage_by_digest: dict[str, str] = {}
    global_ordinal = 0
    source_match_rows = 0
    source_conflict_rows = 0

    for page in pages:
        items = page.get("items")
        require(isinstance(items, list) and len(items) == 10, "PAGE_ITEM_COUNT_INVALID")
        for page_item_ordinal, raw_item in enumerate(items, 1):
            require(isinstance(raw_item, Mapping), "ITEM_SHAPE_INVALID")
            global_ordinal += 1
            custody_value = raw_item.get("issuCmpyKsdCustNo")
            require(type(custody_value) is str, "CUSTODY_TYPE_INVALID")
            custody = custody_value
            require(
                bool(custody)
                and custody == custody.strip()
                and bool(re.fullmatch(r"[0-9]+", custody)),
                "CUSTODY_FORMAT_INVALID",
            )
            custody_digest = sha256_bytes(custody.encode("utf-8"))
            prior_preimage = custody_preimage_by_digest.setdefault(custody_digest, custody)
            require(prior_preimage == custody, "CUSTODY_DIGEST_ALIAS_OR_COLLISION")
            identity_digest = issuer_identity_digest(raw_item)
            expected_identity_digest = identities.get(custody_digest)
            if expected_identity_digest is not None and expected_identity_digest != identity_digest:
                source_classification = "CONFLICT"
                source_conflict_rows += 1
            else:
                source_classification = "MATCH"
                source_match_rows += 1
                identities[custody_digest] = identity_digest
            descriptor = {
                "basDt": expected_bas_dt,
                "custody_key_sha256": custody_digest,
                "global_row_ordinal": global_ordinal,
                "observed_identity_sha256": identity_digest,
                "page_item_ordinal": page_item_ordinal,
                "page_no": int(page["page_no"]),
            }
            if custody_digest == target_custody_key_sha256:
                if identity_digest == frozen_identity_sha256:
                    identity_class = "FROZEN"
                elif identity_digest == observed_identity_sha256:
                    identity_class = "OBSERVED"
                else:
                    raise ExclusionPrecheckError("THIRD_TARGET_IDENTITY")
                target_rows.append(
                    {
                        **descriptor,
                        "disposition": "EXCLUDED_OWNER_AUTHORIZED_ISSUER_GROUP",
                        "identity_class": identity_class,
                        "source_classification": source_classification,
                    }
                )
            else:
                require(source_classification == "MATCH", "NON_TARGET_CONFLICT_REMAINS")
                eligible_hash_projection.append(descriptor)

    require(global_ordinal == EXPECTED_SOURCE_ROWS, "SOURCE_ROW_COUNT_INVALID")
    require(target_rows, "TARGET_CUSTODY_NOT_OBSERVED")
    require(
        source_match_rows == sealed_source_match_rows
        and source_conflict_rows == sealed_source_conflict_rows,
        "SOURCE_REPLAY_PARITY_MISMATCH",
    )

    frozen_rows = [row for row in target_rows if row["identity_class"] == "FROZEN"]
    observed_rows = [row for row in target_rows if row["identity_class"] == "OBSERVED"]
    observed_ordinals = tuple(row["global_row_ordinal"] for row in observed_rows)
    require(len(frozen_rows) >= 1, "PRIOR_MATCHING_TARGET_OCCURRENCE_NOT_FOUND")
    require(len(observed_rows) == 2, "KNOWN_CONFLICT_COUNT_MISMATCH")
    require(
        all(row["source_classification"] == "MATCH" for row in frozen_rows),
        "FROZEN_TARGET_NOT_SOURCE_MATCH",
    )
    require(
        all(row["source_classification"] == "CONFLICT" for row in observed_rows),
        "OBSERVED_TARGET_NOT_SOURCE_CONFLICT",
    )
    require(
        observed_ordinals == tuple(known_conflict_global_ordinals),
        "KNOWN_CONFLICT_ORDINALS_MISMATCH",
    )
    require(len(target_rows) >= 3, "SEALED_G10_SELECTOR_OCCURRENCES_LESS_THAN_3")

    excluded_source_match = len(frozen_rows)
    excluded_source_conflict = len(observed_rows)
    excluded_total = len(target_rows)
    eligible_match_rows = sealed_source_match_rows - excluded_source_match
    require(eligible_match_rows >= 0, "ELIGIBLE_COUNT_NEGATIVE")
    require(
        excluded_total == excluded_source_match + excluded_source_conflict,
        "EXCLUDED_PARTITION_MISMATCH",
    )
    require(
        eligible_match_rows + excluded_total + sealed_source_missing_rows
        == EXPECTED_SOURCE_ROWS,
        "ACCOUNTING_SUM_MISMATCH",
    )
    require(
        len(eligible_hash_projection) == eligible_match_rows,
        "ELIGIBLE_PROJECTION_COUNT_MISMATCH",
    )
    require(
        all(
            row["custody_key_sha256"] != target_custody_key_sha256
            for row in eligible_hash_projection
        ),
        "TARGET_LEFT_ELIGIBLE",
    )

    result = {
        "artifact": "M3TOP3_FINANCE_CA_PAGE100_G10_ISSUER_GROUP_HASH_ONLY_EXCLUSION_PROJECTION_v1.0",
        "basDt": expected_bas_dt,
        "clear_issuer_values_persisted": False,
        "company_master_or_universe_mutated": False,
        "eligible_projection": {
            "row_count": eligible_match_rows,
            "sha256": sha256_bytes(canonical_json_bytes(eligible_hash_projection)),
            "target_selector_occurrences": 0,
        },
        "issuer_identity_selected": False,
        "partition_accounting": {
            "eligible_match_rows": eligible_match_rows,
            "excluded_conflict_occurrences": excluded_source_conflict,
            "excluded_prior_matching_occurrences": excluded_source_match,
            "excluded_total_occurrences": excluded_total,
            "missing_rows": sealed_source_missing_rows,
            "source_rows": EXPECTED_SOURCE_ROWS,
        },
        "sealed_source_pre_exclusion": {
            "conflict_rows": source_conflict_rows,
            "match_rows": source_match_rows,
            "missing_rows": sealed_source_missing_rows,
            "rows": EXPECTED_SOURCE_ROWS,
        },
        "final_hash_only_identity_map": {
            "count": len(identities),
            "sha256": sha256_bytes(canonical_json_bytes(dict(sorted(identities.items())))),
        },
        "selector": {
            "algorithm": "SHA256_OF_UTF8_ISSUCMPY_KSD_CUSTNO",
            "custody_key_sha256": target_custody_key_sha256,
            "scope": "CURRENT_FROZEN_FINANCE_PAGE100_G10_40_ROW_SLICE_ONLY",
        },
        "target_occurrences": target_rows,
    }
    require(not _walk_for_clear_keys(result), "CLEAR_IDENTITY_KEY_IN_OUTPUT")
    return result


def build_hash_only_exclusion_projection(
    entity_bodies: Sequence[bytes],
    *,
    exact_raw_versions: Sequence[Mapping[str, Any]],
    inherited_identity_hashes_by_custody_sha256: Mapping[str, str],
    target_custody_key_sha256: str,
    frozen_identity_sha256: str,
    observed_identity_sha256: str,
    expected_bas_dt: str = EXPECTED_BASE_DATE,
    known_conflict_global_ordinals: Sequence[int] = KNOWN_CONFLICT_GLOBAL_ORDINALS,
) -> dict[str, Any]:
    """Replay only the four exact authority-bound raw object versions."""

    require(
        list(exact_raw_versions) == list(EXPECTED_EXACT_RAW_VERSIONS)
        and all(
            isinstance(row, Mapping)
            and set(row) == {
                "bytes",
                "page_no",
                "s3_object_key",
                "sha256",
                "version_id",
            }
            and type(row.get("bytes")) is int
            and type(row.get("page_no")) is int
            and all(
                isinstance(row.get(key), str)
                for key in ("s3_object_key", "sha256", "version_id")
            )
            for row in exact_raw_versions
        ),
        "RAW_VERSION_AUTHORITY_BINDING_MISMATCH",
    )
    require(
        target_custody_key_sha256 == TARGET_CUSTODY_KEY_SHA256
        and frozen_identity_sha256 == FROZEN_IDENTITY_SHA256
        and observed_identity_sha256 == OBSERVED_IDENTITY_SHA256
        and expected_bas_dt == EXPECTED_BASE_DATE
        and tuple(known_conflict_global_ordinals) == KNOWN_CONFLICT_GLOBAL_ORDINALS,
        "SELECTOR_OR_PROVENANCE_AUTHORITY_BINDING_MISMATCH",
    )
    require(len(entity_bodies) == 4, "FOUR_ENTITY_BODIES_REQUIRED")
    require(len(exact_raw_versions) == 4, "FOUR_RAW_BINDINGS_REQUIRED")
    require(
        [int(row.get("page_no") or 0) for row in exact_raw_versions] == [1, 2, 3, 4],
        "RAW_BINDING_PAGE_VECTOR_INVALID",
    )
    pages: list[dict[str, Any]] = []
    for page_no, (body, binding) in enumerate(zip(entity_bodies, exact_raw_versions), 1):
        require(type(body) is bytes, "RAW_ENTITY_TYPE_INVALID")
        require(
            isinstance(binding, Mapping)
            and type(binding.get("bytes")) is int
            and binding.get("bytes", 0) > 0
            and isinstance(binding.get("sha256"), str)
            and bool(HASH_RE.fullmatch(binding["sha256"])),
            "RAW_BINDING_INVALID",
        )
        require(
            len(body) == binding.get("bytes")
            and sha256_bytes(body) == binding.get("sha256"),
            "RAW_BODY_BINDING_MISMATCH",
        )
        pages.append(
            parse_finance_entity(
                body,
                expected_bas_dt,
                page_no,
                expected_page_size=10,
                expected_total_count=EXPECTED_TOTAL_COUNT,
            )
        )
    return _build_hash_only_exclusion_projection_from_verified_pages(
        pages,
        inherited_identity_hashes_by_custody_sha256=(
            inherited_identity_hashes_by_custody_sha256
        ),
        target_custody_key_sha256=target_custody_key_sha256,
        frozen_identity_sha256=frozen_identity_sha256,
        observed_identity_sha256=observed_identity_sha256,
        expected_bas_dt=expected_bas_dt,
        known_conflict_global_ordinals=known_conflict_global_ordinals,
    )


def _binding_for(path: pathlib.Path) -> dict[str, Any]:
    raw = path.read_bytes()
    return {
        "bytes": len(raw),
        "git_blob_sha": git_blob_sha_bytes(raw),
        "sha256": sha256_bytes(raw),
    }


def validate_preparation_bundle(
    root: pathlib.Path,
    authority: Mapping[str, Any],
    manifest: Mapping[str, Any],
    *,
    allow_missing_predecessor_checkpoint_for_local_test: bool = False,
) -> None:
    require(
        authority.get("artifact")
        == (
            "M3TOP3_FINANCE_CA_PAGE100_G10_ISSUER_CONFLICT_EXCLUSION_"
            "REMEDIATION_ENUMERATION_PRECHECK_AUTHORITY_v1.0"
        )
        and authority.get("project") == "AAA"
        and authority.get("repository") == REPOSITORY
        and authority.get("branch") == BRANCH
        and authority.get("state") == "PRECHECK_ONLY_ZERO_EXTERNAL_EFFECT",
        "AUTHORITY_IDENTITY_OR_STATE_INVALID",
    )
    decision = authority.get("decision_receipt_binding", {})
    require(
        decision
        == {
            "bytes": 11612,
            "commit_sha": PREPARATION_PARENT_HEAD_SHA,
            "git_blob_sha": "45efc3a45db3691b20a01e04810b8ca6ae16e94a",
            "path": DECISION_RECEIPT_PATH,
            "sha256": "b6cc5db024d12f3f0a796797d796e19ee14d4729c74fb84729237a40c04618df",
            "tree_sha": PREPARATION_PARENT_TREE_SHA,
        },
        "DECISION_RECEIPT_LITERAL_BINDING_MISMATCH",
    )
    require(
        _binding_for(root / DECISION_RECEIPT_PATH)
        == {key: decision[key] for key in ("bytes", "git_blob_sha", "sha256")},
        "DECISION_RECEIPT_FILE_BINDING_MISMATCH",
    )
    require(
        authority.get("selector")
        == {
            "algorithm": "SHA256_OF_UTF8_ISSUCMPY_KSD_CUSTNO",
            "custody_key_sha256": TARGET_CUSTODY_KEY_SHA256,
            "frozen_identity_sha256": FROZEN_IDENTITY_SHA256,
            "observed_identity_sha256": OBSERVED_IDENTITY_SHA256,
            "scope": "CURRENT_FROZEN_FINANCE_PAGE100_G10_40_ROW_SLICE_ONLY",
        },
        "AUTHORITY_SELECTOR_MISMATCH",
    )
    require(
        authority.get("known_conflict_provenance")
        == {
            "basDt": EXPECTED_BASE_DATE,
            "global_row_ordinals": list(KNOWN_CONFLICT_GLOBAL_ORDINALS),
            "logical_group_id": "G10-S4-33305734866-LG01",
            "occurrence_ids": [
                "G10-S4-33305734866-C01",
                "G10-S4-33305734866-C02",
            ],
        },
        "KNOWN_CONFLICT_PROVENANCE_MISMATCH",
    )
    require(
        authority.get("authority_basis")
        == {
            "actual_exact_version_enumeration_authorized": False,
            "decision": (
                "OWNER_EXCLUDE_EXACT_HASHED_ISSUER_GROUP_FROM_CURRENT_FROZEN_"
                "G10_PILOT_ELIGIBILITY"
            ),
            "decision_source": "CURRENT_PMO_CHANNEL_OWNER_DIRECTION",
            "interpreted_scope": "PREPARE_AND_RUN_ZERO_EXTERNAL_EFFECT_PRECHECK_ONLY",
        },
        "AUTHORITY_BASIS_INVALID",
    )
    require(
        authority.get("claim_ceiling")
        == {
            "exact_selector_occurrence_count": "NOT_ENUMERATED_AT_PRECHECK",
            "gate_effect": "NONE",
            "issuer_identity_resolution": False,
            "normalization_pit_promotion_release_production": False,
            "validation_claim": "PRECHECK_ONLY_ZERO_EXTERNAL_EFFECT",
        },
        "CLAIM_CEILING_INVALID",
    )
    require(
        authority.get("precheck_contract")
        == {
            "activation_file_created_by_preparation": False,
            "all_40_rows_replayed_before_selector": True,
            "clear_issuer_values_allowed_in_code_logs_artifacts_or_git": False,
            "company_wide_selector_semantics_required": True,
            "exact_enumeration_performed": False,
            "exact_raw_entity_binding_required_before_parse": True,
            "inherited_hash_only_identity_baseline_required": True,
            "known_minimum_target_occurrences": 3,
            "non_target_conflict_tolerance": 0,
            "offline_focused_tests_only": True,
            "preparation_and_activation_are_separate_commits": True,
            "source_pre_exclusion_counts": {
                "conflict_rows": EXPECTED_SOURCE_CONFLICT_ROWS,
                "match_rows": EXPECTED_SOURCE_MATCH_ROWS,
                "missing_rows": EXPECTED_SOURCE_MISSING_ROWS,
                "rows": EXPECTED_SOURCE_ROWS,
            },
        },
        "PRECHECK_CONTRACT_INVALID",
    )
    precheck_contract = authority["precheck_contract"]
    require(
        type(precheck_contract["known_minimum_target_occurrences"]) is int
        and type(precheck_contract["non_target_conflict_tolerance"]) is int,
        "PRECHECK_CONTRACT_INTEGER_TYPE_INVALID",
    )
    _require_exact_integer_mapping(
        precheck_contract["source_pre_exclusion_counts"],
        {
            "conflict_rows": EXPECTED_SOURCE_CONFLICT_ROWS,
            "match_rows": EXPECTED_SOURCE_MATCH_ROWS,
            "missing_rows": EXPECTED_SOURCE_MISSING_ROWS,
            "rows": EXPECTED_SOURCE_ROWS,
        },
        "PRECHECK_SOURCE_COUNTER_TYPE_INVALID",
    )
    baseline = authority.get("baseline_identity_projection", {})
    baseline_map = baseline.get("identity_hashes_by_custody_sha256", {})
    require(
        isinstance(baseline_map, Mapping)
        and baseline.get("algorithm")
        == (
            "SORTED_MAP_SHA256_UTF8_CUSTODY_TO_FROZEN_IDENTITY_SHA256_"
            "CANONICAL_JSON_LF"
        )
        and baseline.get("count") == 12
        and baseline.get("clear_custody_values_persisted") is False
        and baseline.get("source")
        == "HASH_ONLY_DERIVATION_FROM_SEALED_PREDECESSOR_CHECKPOINT"
        and baseline.get("projection_sha256")
        == EXPECTED_BASELINE_PROJECTION_SHA256
        and len(baseline_map) == 12
        and all(
            isinstance(key, str)
            and isinstance(value, str)
            and bool(HASH_RE.fullmatch(key))
            and bool(HASH_RE.fullmatch(value))
            for key, value in baseline_map.items()
        )
        and sha256_bytes(canonical_json_bytes(dict(baseline_map)))
        == EXPECTED_BASELINE_PROJECTION_SHA256,
        "BASELINE_HASH_ONLY_PROJECTION_INVALID",
    )
    effects = authority.get("effect_ceiling", {})
    _require_exact_integer_mapping(
        effects,
        {
            "aws_or_s3_calls": 0,
            "company_master_or_universe_mutations": 0,
            "finance_provider_api_calls": 0,
            "g10_or_g11_runs": 0,
            "github_api_or_remote_gate_calls": 0,
            "issuer_identity_selections": 0,
            "normalization_pit_promotion_release_production_actions": 0,
            "provider_quota_reservations": 0,
            "remote_custody_mutations": 0,
            "sts_calls": 0,
        },
        "PRECHECK_EFFECT_CEILING_INVALID",
    )
    require(
        authority.get("stop_conditions")
        == [
            "ACTIVATION_FILE_PRESENT_IN_PREPARATION_COMMIT",
            "ANY_EXTERNAL_NETWORK_AWS_S3_STS_PROVIDER_OR_QUOTA_EFFECT",
            "ANY_G10_OR_G11_EXECUTION",
            "ANY_IDENTITY_SELECTION_CLEAR_ISSUER_PERSISTENCE_OR_MASTER_UNIVERSE_MUTATION",
            "ANY_NORMALIZATION_PIT_PROMOTION_RELEASE_OR_PRODUCTION",
            "COUNT_CLAIM_BEFORE_EXACT_ENUMERATION",
            "PRIOR_S4_AUTHORITY_SESSION_RUNTIME_OR_LATCH_REUSE",
            "SOURCE_DECISION_SELECTOR_OR_MANIFEST_BINDING_MISMATCH",
        ],
        "STOP_CONDITION_SET_INVALID",
    )
    future = authority.get("future_exact_version_read_plan", {})
    require(future.get("authorized_by_this_precheck") is False, "FUTURE_READ_IMPLICITLY_AUTHORIZED")
    require(future.get("separate_owner_authority_required") is True, "FUTURE_READ_AUTHORITY_BOUNDARY_MISSING")
    require(
        type(future.get("exact_get_object_version_call_ceiling_if_separately_authorized"))
        is int
        and future.get("exact_get_object_version_call_ceiling_if_separately_authorized")
        == 4
        and type(future.get("exact_raw_bytes_ceiling_if_separately_authorized"))
        is int
        and future.get("exact_raw_bytes_ceiling_if_separately_authorized") == 18730,
        "FUTURE_READ_CEILING_INVALID",
    )
    _require_exact_integer_mapping(
        {
            key: future.get(key)
            for key in (
                "finance_provider_api_calls",
                "list_object_or_list_object_versions_calls",
                "provider_quota_reservations",
                "s3_delete_copy_or_put_calls",
            )
        },
        {
            "finance_provider_api_calls": 0,
            "list_object_or_list_object_versions_calls": 0,
            "provider_quota_reservations": 0,
            "s3_delete_copy_or_put_calls": 0,
        },
        "FUTURE_READ_SIDE_EFFECT_CEILING_INVALID",
    )
    sealed = authority.get("sealed_source_bindings", {})
    require(
        sealed == EXPECTED_SEALED_SOURCE_BINDINGS,
        "SEALED_SOURCE_BINDING_SET_INVALID",
    )
    for name, binding in sealed.items():
        path = root / str(binding.get("path") or "")
        if name == "acquisition_predecessor_checkpoint" and not path.exists():
            require(
                allow_missing_predecessor_checkpoint_for_local_test,
                "PREDECESSOR_CHECKPOINT_FILE_MISSING",
            )
            continue
        require(path.is_file(), "SEALED_SOURCE_FILE_MISSING")
        require(
            _binding_for(path)
            == {key: binding[key] for key in ("bytes", "git_blob_sha", "sha256")},
            "SEALED_SOURCE_FILE_BINDING_MISMATCH",
        )
    s4_authority = load_canonical_json(
        root / sealed["forensic_s4_authority"]["path"]
    )
    corrected_s4_core = s4_authority.get("corrected_forensic_core")
    require(
        corrected_s4_core
        == {
            "bytes": 72815,
            "git_blob_sha": "4b20d83f056c56e36b273ad0b5680cef22f0dd19",
            "path": "tools/m3top3/finance_page100_g10_forensic_s4_core.py",
            "sha256": (
                "84aa27b79f65c25384411055c5597f2d13012bc4677f3bb05a7fa5e4d5d496e1"
            ),
        }
        and _binding_for(root / corrected_s4_core["path"])
        == {
            key: corrected_s4_core[key]
            for key in ("bytes", "git_blob_sha", "sha256")
        },
        "CORRECTED_S4_CLASSIFICATION_CORE_BINDING_MISMATCH",
    )
    exact_versions = future.get("exact_raw_versions_if_separately_authorized")
    require(
        exact_versions == s4_authority.get("exact_g10_raw_versions")
        and exact_versions == list(EXPECTED_EXACT_RAW_VERSIONS)
        and isinstance(exact_versions, list)
        and all(
            type(row.get("page_no")) is int
            and type(row.get("bytes")) is int
            for row in exact_versions
        ),
        "FUTURE_EXACT_VERSION_VECTOR_MISMATCH",
    )
    require(
        manifest.get("artifact")
        == (
            "M3TOP3_FINANCE_CA_PAGE100_G10_ISSUER_CONFLICT_EXCLUSION_"
            "REMEDIATION_ENUMERATION_PRECHECK_MANIFEST_v1.0"
        )
        and manifest.get("state")
        == "IMMUTABLE_ZERO_EXTERNAL_EFFECT_PRECHECK_PREPARATION_MANIFEST"
        and manifest.get("preparation_id")
        == "G10-ISSUER-GROUP-EXCLUSION-ENUMERATION-PRECHECK-PREPARATION-20260831"
        and manifest.get("preparation_commit_message") == PREPARATION_MESSAGE
        and manifest.get("preparation_parent_head_sha") == PREPARATION_PARENT_HEAD_SHA
        and manifest.get("preparation_parent_tree_sha") == PREPARATION_PARENT_TREE_SHA,
        "MANIFEST_IDENTITY_OR_PARENT_BINDING_MISMATCH",
    )
    files = manifest.get("preparation_files")
    require(isinstance(files, Mapping) and len(files) == 5, "MANIFEST_FILE_SET_INVALID")
    expected_paths = {
        AUTHORITY_PATH,
        ACTIVATION_TEMPLATE_PATH,
        RUNNER_PATH,
        TEST_PATH,
        WORKFLOW_PATH,
    }
    require(set(files) == expected_paths, "MANIFEST_PATH_SET_INVALID")
    for relative, expected in files.items():
        require(_binding_for(root / relative) == expected, "MANIFEST_FILE_BINDING_MISMATCH")


def validate_activation(
    activation: Mapping[str, Any],
    authority: Mapping[str, Any],
    manifest: Mapping[str, Any],
    *,
    expected_preparation_commit_sha: str,
    expected_preparation_tree_sha: str,
    validation_time_utc: dt.datetime | None = None,
) -> None:
    require(
        set(activation)
        == {
            "activation_id",
            "activated_at_utc",
            "armed",
            "artifact",
            "authority_sha256",
            "branch",
            "expected_commit_message",
            "external_effects_authorized",
            "fresh_runtime_and_latch",
            "manifest_sha256",
            "preparation_commit_sha",
            "preparation_parent",
            "preparation_tree_sha",
            "repository",
            "state",
        },
        "ACTIVATION_SCHEMA_INVALID",
    )
    require(activation.get("artifact") == ACTIVATION_ARTIFACT, "ACTIVATION_ARTIFACT_INVALID")
    require(activation.get("state") == ACTIVATION_STATE, "ACTIVATION_STATE_INVALID")
    require(activation.get("armed") is True, "ACTIVATION_NOT_ARMED")
    require(
        isinstance(activation.get("activation_id"), str)
        and bool(ACTIVATION_ID_RE.fullmatch(activation["activation_id"])),
        "ACTIVATION_ID_INVALID",
    )
    activation_timestamp = _parse_real_utc_timestamp(
        activation.get("activated_at_utc"), "ACTIVATION_TIMESTAMP_INVALID"
    )
    validation_clock = validation_time_utc or dt.datetime.now(dt.timezone.utc)
    require(
        isinstance(validation_clock, dt.datetime)
        and validation_clock.tzinfo is not None
        and validation_clock.utcoffset() == dt.timedelta(0),
        "ACTIVATION_VALIDATION_CLOCK_INVALID",
    )
    activation_age = validation_clock - activation_timestamp
    require(
        -dt.timedelta(minutes=5) <= activation_age <= dt.timedelta(hours=24),
        "ACTIVATION_TIMESTAMP_NOT_FRESH",
    )
    activation_timestamp_compact = re.sub(
        r"[-:TZ]", "", str(activation["activated_at_utc"])
    )
    require(
        activation["activation_id"].endswith(activation_timestamp_compact),
        "ACTIVATION_ID_TIMESTAMP_MISMATCH",
    )
    require(activation.get("repository") == REPOSITORY, "ACTIVATION_REPOSITORY_MISMATCH")
    require(activation.get("branch") == BRANCH, "ACTIVATION_BRANCH_MISMATCH")
    require(activation.get("expected_commit_message") == ACTIVATION_MESSAGE, "ACTIVATION_MESSAGE_MISMATCH")
    require(
        activation.get("preparation_parent")
        == {
            "decision_commit_sha": PREPARATION_PARENT_HEAD_SHA,
            "decision_tree_sha": PREPARATION_PARENT_TREE_SHA,
        },
        "ACTIVATION_DECISION_BINDING_MISMATCH",
    )
    require(
        isinstance(expected_preparation_commit_sha, str)
        and bool(GIT_SHA_RE.fullmatch(expected_preparation_commit_sha))
        and activation.get("preparation_commit_sha") == expected_preparation_commit_sha,
        "ACTIVATION_PREPARATION_COMMIT_MISMATCH",
    )
    require(
        isinstance(expected_preparation_tree_sha, str)
        and bool(GIT_SHA_RE.fullmatch(expected_preparation_tree_sha))
        and activation.get("preparation_tree_sha") == expected_preparation_tree_sha,
        "ACTIVATION_PREPARATION_TREE_MISMATCH",
    )
    require(
        activation.get("authority_sha256")
        == sha256_bytes(canonical_json_bytes(dict(authority))),
        "ACTIVATION_AUTHORITY_BINDING_MISMATCH",
    )
    require(
        activation.get("manifest_sha256")
        == sha256_bytes(canonical_json_bytes(dict(manifest))),
        "ACTIVATION_MANIFEST_BINDING_MISMATCH",
    )
    _require_exact_integer_mapping(
        activation.get("external_effects_authorized"),
        {
            "aws_or_s3_calls": 0,
            "finance_provider_api_calls": 0,
            "g10_or_g11_runs": 0,
            "normalization_pit_promotion_release_production": 0,
            "provider_quota_reservations": 0,
            "remote_mutations": 0,
        },
        "ACTIVATION_EFFECT_CEILING_INVALID",
    )
    fresh = activation.get("fresh_runtime_and_latch")
    require(
        isinstance(fresh, Mapping)
        and set(fresh)
        == {
            "precheck_attempt_ordinal",
            "prior_s4_authority_or_session_reused",
            "prior_s4_latch_reused",
            "runtime_lock_id",
        }
        and type(fresh.get("precheck_attempt_ordinal")) is int
        and fresh.get("precheck_attempt_ordinal") == 1
        and fresh.get("prior_s4_authority_or_session_reused") is False
        and fresh.get("prior_s4_latch_reused") is False
        and isinstance(fresh.get("runtime_lock_id"), str)
        and bool(RUNTIME_LOCK_RE.fullmatch(fresh["runtime_lock_id"])),
        "ACTIVATION_FRESH_RUNTIME_OR_LATCH_INVALID",
    )
    require(
        fresh["runtime_lock_id"].endswith(activation_timestamp_compact),
        "ACTIVATION_RUNTIME_TIMESTAMP_MISMATCH",
    )


def command_precheck(args: argparse.Namespace) -> int:
    root = pathlib.Path(args.root).resolve()
    authority = load_canonical_json(root / args.authority)
    manifest = load_canonical_json(root / args.manifest)
    activation = load_canonical_json(root / args.activation)
    validate_preparation_bundle(root, authority, manifest)
    validate_activation(
        activation,
        authority,
        manifest,
        expected_preparation_commit_sha=args.expected_preparation_commit,
        expected_preparation_tree_sha=args.expected_preparation_tree,
    )
    print(
        json.dumps(
            {
                "exact_enumeration_started": False,
                "external_effects": 0,
                "state": "TERMINAL_PRECHECK_PASS_ZERO_EXTERNAL_EFFECT_ENUMERATION_NOT_STARTED",
            },
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    sub = result.add_subparsers(dest="command", required=True)
    precheck = sub.add_parser("precheck")
    precheck.add_argument("--root", default=".")
    precheck.add_argument("--authority", default=AUTHORITY_PATH)
    precheck.add_argument("--manifest", default=MANIFEST_PATH)
    precheck.add_argument("--activation", default=ACTIVATION_PATH)
    precheck.add_argument("--expected-preparation-commit", required=True)
    precheck.add_argument("--expected-preparation-tree", required=True)
    precheck.set_defaults(func=command_precheck)
    return result


def main() -> int:
    args = parser().parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
