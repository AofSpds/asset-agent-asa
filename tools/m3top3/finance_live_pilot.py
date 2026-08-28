#!/usr/bin/env python3
"""Finance-only bounded live pilot with custody-first, resume-safe execution.

The module has no import-time network or AWS side effects. Live adapters are
constructed only by main after every authority and execution binding passes.
"""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import math
import os
import re
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Protocol, Sequence

from . import source_admission as sa


RUNTIME_LOCK_ID = "PMO-API-SRC-ADMIT-20260828192737"
PILOT_RUN_ID = "FINANCE-LIVE-PILOT-20260828192737"
ACTIVATION_BASE_HEAD_COMMIT = "188c39b20f91d2cbf1a05d71757e4a35bbbbb5f9"
OWNER_CAP_SPEC_SHA256 = "7b65152d8df10a6497d1656dbc5cc6d4bd253740f53a29480bb8d877b81b9f05"
EXPECTED_AUTHORITY_SHA256 = "10ec745dbcc6aa27787f4739662552aad3518f3ec31122e6a522c03cbd621b2c"
EXPECTED_EXECUTION_TOKEN_SHA256 = "9cda8bb429b3558e81e1ffcc4a232c78976c521186f13fbad5462c0312281f37"
EXPECTED_SOURCE_ADMISSION_SHA256 = "574b2f45474b39fd0cf64f28a946bd115ddb3b782595c3ddd78d15c801d111dd"
FINANCE_SECRET_ENV = "DATA_GO_KR_FINANCE_STOCK_RIGHTS_SERVICE_KEY"
GITHUB_RUN_ID_ENV = "GITHUB_RUN_ID"
AUTHORIZED_GITHUB_REPOSITORY = "AofSpds/asset-agent-asa"
AUTHORIZED_GITHUB_BRANCH = "aaa-pmo-public-data-g2-g3-source-admission-v1-20260828"
AUTHORIZED_GITHUB_REF = f"refs/heads/{AUTHORIZED_GITHUB_BRANCH}"
AUTHORIZED_GITHUB_ACTOR = "AofSpds"
AWS_ACCOUNT_ID = "956315449338"
AWS_REGION = "ap-northeast-2"
RAW_PREFIX = (
    "s3://semi-data-plane-aofspds-20260815/raw/public-data-api/"
    "M3TOP3-FINANCE-STOCK-RIGHTS-v1/"
)
PRIMARY_DATES = (
    "20240102", "20240131", "20240329", "20240628", "20240808",
    "20240809", "20240812", "20240930", "20241231", "20250115",
    "20250331", "20250630", "20251231", "20260115", "20260331",
    "20260630", "20260814",
)
REQUEST_PAGE_SIZE = 10
MAX_PAGES_PER_DATE = 10
MAX_PRIMARY_PAGE_SLOTS = 170
MAX_NETWORK_ATTEMPTS_TOTAL = 200
MAX_ATTEMPTS_PER_PAGE = 2
HISTORICAL_BASELINE_QUOTA_DAY_KST = "2026-08-28"
HISTORICAL_BASELINE_FINANCE_LAST_ORDINAL = 5
HISTORICAL_BASELINE_KSD_LAST_ORDINAL = 2
PILOT_QUOTA_DAY_KST = "2026-08-29"
PILOT_FINANCE_ORDINAL_BASE = 0
_SHA256_RE = re.compile(r"[0-9a-f]{64}")
_GIT_SHA_RE = re.compile(r"[0-9a-f]{40}")
_WRITER_ID_RE = re.compile(r"github-run:[1-9][0-9]*")
SAFE_RESPONSE_HEADERS = {
    "content-type", "content-length", "date", "etag", "last-modified", "retry-after",
}
ATTEMPT_STATES = {
    "RESERVED_WRITE_AHEAD",
    "RESERVATION_SPENT_NO_REMOTE_ENTITY_ON_RESUME",
    "RAW_SEALED_BEFORE_PARSE",
    "NO_RESPONSE_ENTITY_RESERVATION_SPENT",
    "RETRYABLE_HTTP_ENTITY_CUSTODIED",
    "NONRETRYABLE_HTTP_ENTITY_CUSTODIED",
    "PARSE_OR_PROTOCOL_BLOCKED_AFTER_CUSTODY",
    "RETURNED_PAGE_SIZE_MISMATCH",
    "PARSED_200",
}

OWNER_CAP_MATERIAL = {
    "runtime_lock_id": RUNTIME_LOCK_ID,
    "activation_base_head_commit": ACTIVATION_BASE_HEAD_COMMIT,
    "dates": list(PRIMARY_DATES),
    "request_page_size": REQUEST_PAGE_SIZE,
    "max_pages_per_date": MAX_PAGES_PER_DATE,
    "max_primary_page_acquisitions": MAX_PRIMARY_PAGE_SLOTS,
    "max_network_attempts_total": MAX_NETWORK_ATTEMPTS_TOTAL,
    "max_attempts_per_page": MAX_ATTEMPTS_PER_PAGE,
    "prefix": RAW_PREFIX,
}
if hashlib.sha256(sa.canonical_json_bytes(OWNER_CAP_MATERIAL)).hexdigest() != OWNER_CAP_SPEC_SHA256:
    raise RuntimeError("pinned Finance owner-cap material hash mismatch")


class LivePilotError(sa.AdmissionError):
    """Sanitized, non-secret-bearing live-pilot failure."""


class AuthorityBindingError(LivePilotError):
    pass


class NoEntityTransportError(LivePilotError):
    """A reserved attempt ended without a response entity."""


class RemoteCustodyError(LivePilotError):
    pass


@dataclass(frozen=True)
class LivePilotSpec:
    ordered_dates: tuple[str, ...] = PRIMARY_DATES
    request_page_size: int = REQUEST_PAGE_SIZE
    max_pages_per_date: int = MAX_PAGES_PER_DATE
    max_primary_page_slots: int = MAX_PRIMARY_PAGE_SLOTS
    max_network_attempts_total: int = MAX_NETWORK_ATTEMPTS_TOTAL
    max_attempts_per_page: int = MAX_ATTEMPTS_PER_PAGE
    runtime_lock_id: str = RUNTIME_LOCK_ID
    pilot_run_id: str = PILOT_RUN_ID
    raw_prefix: str = RAW_PREFIX
    owner_cap_spec_sha256: str = OWNER_CAP_SPEC_SHA256


@dataclass(frozen=True)
class ExecutionBindings:
    authority_sha256: str
    plan_sha256: str
    latch_execution_material_sha256: str
    runner_sha256: str
    source_admission_sha256: str
    checkpoint_template_sha256: str
    baseline_quota_ledger_sha256: str
    baseline_raw_index_sha256: str
    github_repository: str
    github_ref: str
    github_sha: str
    github_actor: str
    github_triggering_actor: str
    github_run_id: int
    github_run_attempt: int


@dataclass(frozen=True)
class TransportResponse:
    body: bytes
    http_status: int
    safe_headers: Mapping[str, str]
    acquired_at_utc: str


@dataclass(frozen=True)
class SealedEntity:
    body: bytes
    object_key: str
    storage_locator: str
    entity_sha256: str
    entity_bytes: int
    readback_sha256: str
    readback_bytes: int
    version_id: str
    etag: str
    server_side_encryption: str
    write_precondition: str
    http_status: int
    acquired_at_utc: str


@dataclass(frozen=True)
class ExecutionClaimEvidence:
    object_key: str
    content_sha256: str
    version_id: str
    etag: str
    server_side_encryption: str
    write_precondition: str
    writer_id: str


class FinanceTransport(Protocol):
    def fetch_once(self, params: Mapping[str, str]) -> TransportResponse:
        ...


class RawCustodyStore(Protocol):
    def read_existing(
        self, object_key: str, version_id: str | None = None
    ) -> SealedEntity | None:
        ...

    def seal_and_readback(
        self, object_key: str, body: bytes, metadata: Mapping[str, str]
    ) -> SealedEntity:
        ...

    def find_existing_by_prefix(self, object_prefix: str) -> SealedEntity | None:
        ...


class ExecutionClaimStore(Protocol):
    def acquire_execution_claim(
        self, claim: Mapping[str, Any]
    ) -> ExecutionClaimEvidence:
        ...


class DurableCheckpointStore(Protocol):
    """CAS token is opaque; the live S3 implementation uses an object ETag."""

    def load(self) -> tuple[Mapping[str, Any] | None, str | None]:
        ...

    def compare_and_swap(self, value: Mapping[str, Any], expected_token: str | None) -> str:
        ...


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _iso_utc(clock: Callable[[], datetime]) -> str:
    value = clock()
    if not isinstance(value, datetime) or value.tzinfo is None:
        raise LivePilotError("pilot clock must be timezone-aware")
    return value.astimezone(timezone.utc).isoformat()


def _quota_day_kst(clock: Callable[[], datetime]) -> str:
    value = clock()
    if not isinstance(value, datetime) or value.tzinfo is None:
        raise LivePilotError("pilot clock must be timezone-aware")
    observed = value.astimezone(sa.KST).date().isoformat()
    if observed != PILOT_QUOTA_DAY_KST:
        raise sa.QuotaBoundaryError("Finance pilot crossed frozen KST quota day")
    return observed


def _validate_spec(spec: LivePilotSpec) -> None:
    if not isinstance(spec, LivePilotSpec):
        raise AuthorityBindingError("invalid Finance live-pilot specification")
    expected = {
        "ordered_dates": PRIMARY_DATES,
        "request_page_size": REQUEST_PAGE_SIZE,
        "max_pages_per_date": MAX_PAGES_PER_DATE,
        "max_primary_page_slots": MAX_PRIMARY_PAGE_SLOTS,
        "max_network_attempts_total": MAX_NETWORK_ATTEMPTS_TOTAL,
        "max_attempts_per_page": MAX_ATTEMPTS_PER_PAGE,
        "runtime_lock_id": RUNTIME_LOCK_ID,
        "pilot_run_id": PILOT_RUN_ID,
        "raw_prefix": RAW_PREFIX,
        "owner_cap_spec_sha256": OWNER_CAP_SPEC_SHA256,
    }
    for field, value in expected.items():
        if getattr(spec, field) != value:
            raise AuthorityBindingError(f"Finance owner-cap binding mismatch: {field}")
    sa.validate_finance_pilot_dates(
        spec.ordered_dates, start_date="2024-01-01", end_date="2026-08-14"
    )


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _deep_values(value: Any, key: str) -> list[Any]:
    found: list[Any] = []
    if isinstance(value, Mapping):
        for name, child in value.items():
            if name == key:
                found.append(child)
            found.extend(_deep_values(child, key))
    elif isinstance(value, list):
        for child in value:
            found.extend(_deep_values(child, key))
    return found


def _require_deep_value(document: Mapping[str, Any], key: str, expected: Any) -> None:
    if expected not in _deep_values(document, key):
        raise AuthorityBindingError(f"required live-pilot binding absent: {key}")


def _reject_duplicate_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, child in pairs:
        if key in value:
            raise ValueError("duplicate JSON key")
        value[key] = child
    return value


def _load_json(path: Path) -> tuple[dict[str, Any], bytes, str]:
    try:
        raw = path.read_bytes()
        parsed = json.loads(raw, object_pairs_hook=_reject_duplicate_pairs)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError):
        raise AuthorityBindingError(f"invalid live-pilot control file: {path.name}") from None
    if not isinstance(parsed, dict):
        raise AuthorityBindingError(f"invalid live-pilot control object: {path.name}")
    return parsed, raw, hashlib.sha256(raw).hexdigest()


def validate_cli_materials(
    *,
    authority_path: Path,
    plan_path: Path,
    latch_path: Path,
    checkpoint_path: Path,
    environment: Mapping[str, str] | None = None,
) -> tuple[LivePilotSpec, ExecutionBindings]:
    """Validate every entry binding before credential, network, or S3 use."""
    authority, _, authority_sha = _load_json(authority_path)
    plan, _, plan_sha = _load_json(plan_path)
    latch, _, _ = _load_json(latch_path)
    if authority_sha != EXPECTED_AUTHORITY_SHA256:
        raise AuthorityBindingError("authority file hash mismatch")
    if latch.get("state") != "ARMED" or latch.get("mode") != "LIVE_ARMED":
        raise AuthorityBindingError("live-pilot latch is not ARMED")
    if (
        latch.get("runtime_lock_id") != RUNTIME_LOCK_ID
        or latch.get("pilot_run_id") != PILOT_RUN_ID
        or latch.get("owner_cap_spec_sha256") != OWNER_CAP_SPEC_SHA256
        or latch.get("execution_token_sha256")
        != EXPECTED_EXECUTION_TOKEN_SHA256
    ):
        raise AuthorityBindingError("live-pilot latch top-level binding mismatch")
    env = os.environ if environment is None else environment
    identity_keys = (
        "GITHUB_REPOSITORY", "GITHUB_REF", "GITHUB_SHA", "GITHUB_ACTOR",
        "GITHUB_TRIGGERING_ACTOR", "GITHUB_RUN_ID", "GITHUB_RUN_ATTEMPT",
    )
    if any(not isinstance(env.get(key), str) or not env.get(key) for key in identity_keys):
        raise AuthorityBindingError("GitHub workflow execution identity missing")
    run_id_text = str(env["GITHUB_RUN_ID"])
    run_attempt_text = str(env["GITHUB_RUN_ATTEMPT"])
    if (
        re.fullmatch(r"[1-9][0-9]*", run_id_text) is None
        or re.fullmatch(r"[1-9][0-9]*", run_attempt_text) is None
        or _GIT_SHA_RE.fullmatch(str(env["GITHUB_SHA"])) is None
        or env["GITHUB_REPOSITORY"] != AUTHORIZED_GITHUB_REPOSITORY
        or env["GITHUB_REF"] != AUTHORIZED_GITHUB_REF
        or env["GITHUB_ACTOR"] != AUTHORIZED_GITHUB_ACTOR
        or env["GITHUB_TRIGGERING_ACTOR"] != AUTHORIZED_GITHUB_ACTOR
        or latch.get("repository") != AUTHORIZED_GITHUB_REPOSITORY
        or latch.get("branch") != AUTHORIZED_GITHUB_BRANCH
        or latch.get("owner_actor") != AUTHORIZED_GITHUB_ACTOR
        or authority.get("branch") != AUTHORIZED_GITHUB_BRANCH
        or plan.get("branch") != AUTHORIZED_GITHUB_BRANCH
    ):
        raise AuthorityBindingError("GitHub workflow execution identity mismatch")
    github_run_id = int(run_id_text)
    github_run_attempt = int(run_attempt_text)

    material_raw = latch.get("execution_material")
    if not isinstance(material_raw, Mapping):
        raise AuthorityBindingError("latch execution material missing")
    material = dict(material_raw)
    exact_material_keys = {
        "runtime_lock_id", "pilot_run_id", "authority_sha256", "plan_sha256",
        "runner_sha256", "source_admission_sha256", "checkpoint_template_sha256",
        "owner_cap_spec_sha256", "execution_token_sha256",
        "pilot_quota_day_kst", "historical_baseline_quota_day_kst",
        "current_day_finance_ordinal_base", "current_day_next_finance_ordinal",
        "historical_baseline_rows_preserved",
    }
    if set(material) != exact_material_keys:
        raise AuthorityBindingError("latch execution-material key set mismatch")
    for key in (
        "authority_sha256", "plan_sha256", "runner_sha256", "source_admission_sha256",
        "checkpoint_template_sha256", "owner_cap_spec_sha256",
        "execution_token_sha256",
    ):
        if not isinstance(material[key], str) or _SHA256_RE.fullmatch(material[key]) is None:
            raise AuthorityBindingError(f"invalid latch SHA-256 binding: {key}")
    material_sha = hashlib.sha256(sa.canonical_json_bytes(material)).hexdigest()
    if material_sha != latch.get("execution_material_sha256"):
        raise AuthorityBindingError("latch execution-material hash mismatch")
    runner_sha = _sha256_file(Path(__file__))
    source_admission_sha = _sha256_file(Path(sa.__file__))
    if source_admission_sha != EXPECTED_SOURCE_ADMISSION_SHA256:
        raise AuthorityBindingError("source-admission module hash mismatch")
    token_sha = EXPECTED_EXECUTION_TOKEN_SHA256
    expected_material = {
        "runtime_lock_id": RUNTIME_LOCK_ID,
        "pilot_run_id": PILOT_RUN_ID,
        "authority_sha256": authority_sha,
        "plan_sha256": plan_sha,
        "runner_sha256": runner_sha,
        "source_admission_sha256": source_admission_sha,
        "owner_cap_spec_sha256": OWNER_CAP_SPEC_SHA256,
        "execution_token_sha256": token_sha,
        "pilot_quota_day_kst": PILOT_QUOTA_DAY_KST,
        "historical_baseline_quota_day_kst": HISTORICAL_BASELINE_QUOTA_DAY_KST,
        "current_day_finance_ordinal_base": PILOT_FINANCE_ORDINAL_BASE,
        "current_day_next_finance_ordinal": PILOT_FINANCE_ORDINAL_BASE + 1,
        "historical_baseline_rows_preserved": 7,
    }
    for key, expected in expected_material.items():
        if material.get(key) != expected:
            raise AuthorityBindingError(f"latch binding mismatch: {key}")
    checkpoint_template_sha = str(material.get("checkpoint_template_sha256", ""))
    if len(checkpoint_template_sha) != 64:
        raise AuthorityBindingError("invalid checkpoint-template hash binding")
    if checkpoint_path.exists():
        checkpoint_doc, _, checkpoint_actual_sha = _load_json(checkpoint_path)
        is_mirror = (
            checkpoint_doc.get("runtime_lock_id") == RUNTIME_LOCK_ID
            and checkpoint_doc.get("pilot_run_id") == PILOT_RUN_ID
            and checkpoint_doc.get("checkpoint_template_sha256") == checkpoint_template_sha
        )
        if checkpoint_actual_sha != checkpoint_template_sha and not is_mirror:
            raise AuthorityBindingError("checkpoint template or mirror binding mismatch")

    authority_bindings = latch.get("authority_bindings")
    if not isinstance(authority_bindings, Mapping) or authority_bindings.get("bindings_finalized") is not True:
        raise AuthorityBindingError("latch authority bindings are not finalized")
    exact_binding_values = {
        "authority_sha256": authority_sha,
        "plan_sha256": plan_sha,
        "runner_sha256": runner_sha,
        "source_admission_sha256": source_admission_sha,
        "checkpoint_seed_sha256": checkpoint_template_sha,
    }
    for key, expected in exact_binding_values.items():
        if authority_bindings.get(key) != expected:
            raise AuthorityBindingError(f"latch authority binding mismatch: {key}")
    workflow_sha = authority_bindings.get("workflow_sha256")
    if not isinstance(workflow_sha, str) or _SHA256_RE.fullmatch(workflow_sha) is None:
        raise AuthorityBindingError("latch workflow SHA-256 binding invalid")
    baseline_quota_sha = authority_bindings.get("baseline_quota_ledger_sha256")
    baseline_raw_sha = authority_bindings.get("baseline_raw_index_sha256")
    if (
        not isinstance(baseline_quota_sha, str)
        or _SHA256_RE.fullmatch(baseline_quota_sha) is None
        or not isinstance(baseline_raw_sha, str)
        or _SHA256_RE.fullmatch(baseline_raw_sha) is None
    ):
        raise AuthorityBindingError("latch governed baseline SHA-256 binding invalid")
    expected_paths = {
        "authority_path": "control/m3top3/public-data-source-admission/v1.0/M3TOP3_PUBLIC_DATA_API_SOURCE_ADMISSION_CONTRACT_v1.0.json",
        "plan_path": "control/m3top3/public-data-source-admission/v1.0/M3TOP3_PUBLIC_DATA_API_SOURCE_ADMISSION_PLAN_v1.0.json",
        "checkpoint_seed_path": "control/m3top3/public-data-source-admission/v1.0/M3TOP3_FINANCE_CA_ACQUISITION_CHECKPOINT_v1.0.json",
        "runner_path": "tools/m3top3/finance_live_pilot.py",
        "source_admission_path": "tools/m3top3/source_admission.py",
        "workflow_path": ".github/workflows/m3top3-finance-bounded-live-pilot-v1.yml",
    }
    for key, expected in expected_paths.items():
        if authority_bindings.get(key) != expected:
            raise AuthorityBindingError(f"latch path binding mismatch: {key}")

    for document in (authority, plan):
        _require_deep_value(document, "runtime_lock_id", RUNTIME_LOCK_ID)
        _require_deep_value(document, "owner_cap_spec_sha256", OWNER_CAP_SPEC_SHA256)
    _require_deep_value(
        authority, "execution_token_sha256", EXPECTED_EXECUTION_TOKEN_SHA256
    )
    _require_deep_value(plan, "pilot_run_id", PILOT_RUN_ID)
    _require_deep_value(plan, "ordered_primary_dates", list(PRIMARY_DATES))
    _require_deep_value(plan, "request_page_size", REQUEST_PAGE_SIZE)
    _require_deep_value(plan, "max_pages_per_date", MAX_PAGES_PER_DATE)
    _require_deep_value(plan, "max_primary_page_acquisitions", MAX_PRIMARY_PAGE_SLOTS)
    _require_deep_value(plan, "max_network_attempts_total", MAX_NETWORK_ATTEMPTS_TOTAL)
    _require_deep_value(
        plan, "max_attempts_per_logical_page", MAX_ATTEMPTS_PER_PAGE
    )
    _require_deep_value(plan, "exact_remote_raw_prefix", RAW_PREFIX)
    _require_deep_value(plan, "fallback_dates_authorized", False)
    _require_deep_value(plan, "bulk_acquisition_authorized", False)

    current_authority = authority.get("current_runtime_authority")
    live_authority = authority.get("finance_live_pilot_authority")
    if not isinstance(current_authority, Mapping) or not isinstance(live_authority, Mapping):
        raise AuthorityBindingError("Finance live authority blocks missing")
    required_current = {
        "provider_api_network_calls_entry_gate": "OPEN",
        "provider_api_network_calls_authorized": True,
        "quota_reservation_authorized": True,
        "live_multi_page_provider_run_authorized": True,
        "remote_raw_custody_write_authorized": True,
        "remote_raw_custody_prefix": RAW_PREFIX,
        "ksd_provider_calls_authorized": False,
        "ksd_document_search_authorized": False,
        "fallback_dates_authorized": False,
        "full_date_range_expansion_authorized": False,
        "historical_canary_2019_authorized": False,
        "bulk_acquisition_authorized": False,
        "production_authorized": False,
        "model_semantic_change_authorized": False,
        "pit_semantic_change_authorized": False,
        "normalized_release_authorized": False,
        "automatic_promotion_authorized": False,
        "validation_claim": "NONE",
        "gate_effect": "NONE",
    }
    if any(current_authority.get(key) != value for key, value in required_current.items()):
        raise AuthorityBindingError("current runtime live gate mismatch")
    live_gate = live_authority.get("live_entry_gate")
    if (
        live_authority.get("authority_state") != "GRANTED_ENTRY_GATE_OPEN"
        or not isinstance(live_gate, Mapping)
        or live_gate.get("state") != "OPEN"
    ):
        raise AuthorityBindingError("Finance authority entry gate is not OPEN")

    execution_gate = plan.get("execution_gate")
    custody_plan = plan.get("durable_custody_plan")
    if (
        plan.get("state") != "LIVE_ARMED_EXECUTABLE"
        or not isinstance(execution_gate, Mapping)
        or execution_gate.get("state") != "OPEN"
        or any(
            execution_gate.get(key) is not True
            for key in (
                "execution_armed", "plan_executable",
                "provider_api_calls_permitted_now", "remote_s3_writes_permitted_now",
            )
        )
        or not isinstance(custody_plan, Mapping)
        or custody_plan.get("state") != "READY_FOR_LIVE_ARMED"
    ):
        raise AuthorityBindingError("Finance plan execution gate is not OPEN")

    finance_spec = latch.get("finance_spec")
    remote_custody = latch.get("remote_custody")
    prohibitions = latch.get("hard_prohibitions")
    if not isinstance(finance_spec, Mapping) or not isinstance(remote_custody, Mapping) or not isinstance(prohibitions, Mapping):
        raise AuthorityBindingError("latch safety blocks missing")
    exact_finance_spec = {
        "source_id": sa.FINANCE_SOURCE_ID,
        "operation": sa.FINANCE_OPERATION,
        "ordered_primary_dates": list(PRIMARY_DATES),
        "primary_date_count": 17,
        "request_page_size": REQUEST_PAGE_SIZE,
        "max_pages_per_date": MAX_PAGES_PER_DATE,
        "max_primary_page_acquisitions": MAX_PRIMARY_PAGE_SLOTS,
        "max_network_attempts_total": MAX_NETWORK_ATTEMPTS_TOTAL,
        "max_attempts_per_page": MAX_ATTEMPTS_PER_PAGE,
        "fallback_dates_authorized": False,
        "full_date_range_expansion_authorized": False,
        "historical_2019_canary_expansion_authorized": False,
        "pilot_quota_day_kst": PILOT_QUOTA_DAY_KST,
        "historical_baseline_quota_day_kst": HISTORICAL_BASELINE_QUOTA_DAY_KST,
        "current_day_finance_ordinal_base": PILOT_FINANCE_ORDINAL_BASE,
        "current_day_next_finance_ordinal": PILOT_FINANCE_ORDINAL_BASE + 1,
        "historical_baseline_rows_preserved": 7,
    }
    if any(finance_spec.get(key) != value for key, value in exact_finance_spec.items()):
        raise AuthorityBindingError("latch Finance specification mismatch")
    if (
        remote_custody.get("authorized") is not True
        or remote_custody.get("exact_source_uri") != RAW_PREFIX
        or remote_custody.get("checkpoint_uri") != f"s3://semi-data-plane-aofspds-20260815/{checkpoint_object_key()}"
        or remote_custody.get("execution_claim_uri") != f"s3://semi-data-plane-aofspds-20260815/{execution_claim_object_key()}"
    ):
        raise AuthorityBindingError("latch remote custody binding mismatch")
    exact_prohibitions = {
        "fallback_dates": "NOT_AUTHORIZED",
        "full_date_range_expansion": "PROHIBITED",
        "historical_2019_canary_expansion": "PROHIBITED",
        "ksd_search_or_api_expansion": "PROHIBITED",
        "bulk_acquisition": "PROHIBITED",
        "normalized_release": "PROHIBITED",
        "model_semantic_change": "PROHIBITED",
        "pit_semantic_change": "PROHIBITED",
        "automatic_promotion": "PROHIBITED",
        "secret_persistence": "PROHIBITED",
        "authenticated_url_persistence": "PROHIBITED",
        "execution_token_original_persistence": "PROHIBITED",
    }
    if any(prohibitions.get(key) != value for key, value in exact_prohibitions.items()):
        raise AuthorityBindingError("latch prohibition mismatch")
    for key in (
        "s2_ksd_blocker_waiver", "production_authorized",
        "bulk_acquisition_authorized", "model_semantic_change_authorized",
        "pit_semantic_change_authorized",
    ):
        if latch.get(key) is not False:
            raise AuthorityBindingError(f"latch authorization ceiling mismatch: {key}")
    if latch.get("validation_claim") != "NONE" or latch.get("gate_effect") != "NONE":
        raise AuthorityBindingError("latch claim/gate effect mismatch")

    return LivePilotSpec(), ExecutionBindings(
        authority_sha256=authority_sha,
        plan_sha256=plan_sha,
        latch_execution_material_sha256=material_sha,
        runner_sha256=runner_sha,
        source_admission_sha256=source_admission_sha,
        checkpoint_template_sha256=checkpoint_template_sha,
        baseline_quota_ledger_sha256=baseline_quota_sha,
        baseline_raw_index_sha256=baseline_raw_sha,
        github_repository=AUTHORIZED_GITHUB_REPOSITORY,
        github_ref=AUTHORIZED_GITHUB_REF,
        github_sha=str(env["GITHUB_SHA"]),
        github_actor=AUTHORIZED_GITHUB_ACTOR,
        github_triggering_actor=AUTHORIZED_GITHUB_ACTOR,
        github_run_id=github_run_id,
        github_run_attempt=github_run_attempt,
    )


def deterministic_request_id(bas_dt: str, page_no: int) -> str:
    params = sa.finance_request_params(bas_dt, page_no, REQUEST_PAGE_SIZE)
    return sa.canonical_request_id(
        sa.FINANCE_SOURCE_ID,
        sa.FINANCE_URL,
        sa.FINANCE_OPERATION,
        params,
    )


def deterministic_raw_object_prefix(
    bas_dt: str,
    page_no: int,
    attempt: int,
    quota_day_kst: str = PILOT_QUOTA_DAY_KST,
) -> str:
    if quota_day_kst != PILOT_QUOTA_DAY_KST:
        raise sa.QuotaBoundaryError("raw lineage quota day mismatch")
    if type(attempt) is not int or attempt < 1 or attempt > MAX_ATTEMPTS_PER_PAGE:
        raise sa.QuotaBoundaryError("raw lineage attempt mismatch")
    request_id = deterministic_request_id(bas_dt, page_no)
    return (
        "raw/public-data-api/M3TOP3-FINANCE-STOCK-RIGHTS-v1/"
        f"{sa.FINANCE_OPERATION}/quota_day_kst={quota_day_kst}/"
        f"request_id={request_id}/attempt={attempt}/"
    )


def canonical_raw_object_key(object_prefix: str, entity_sha256: str) -> str:
    if _SHA256_RE.fullmatch(entity_sha256) is None:
        raise RemoteCustodyError("raw lineage entity digest invalid")
    expected_root = (
        "raw/public-data-api/M3TOP3-FINANCE-STOCK-RIGHTS-v1/"
        f"{sa.FINANCE_OPERATION}/quota_day_kst={PILOT_QUOTA_DAY_KST}/"
    )
    if not object_prefix.startswith(expected_root) or not object_prefix.endswith("/"):
        raise RemoteCustodyError("raw lineage prefix mismatch")
    return f"{object_prefix}sha256={entity_sha256}.entity"


def checkpoint_object_key() -> str:
    return (
        "raw/public-data-api/M3TOP3-FINANCE-STOCK-RIGHTS-v1/"
        f"_pilot_control/runtime_lock_id={RUNTIME_LOCK_ID}/"
        f"pilot_run_id={PILOT_RUN_ID}/checkpoint.json"
    )


def execution_claim_object_key() -> str:
    return (
        "raw/public-data-api/M3TOP3-FINANCE-STOCK-RIGHTS-v1/"
        f"_pilot_control/runtime_lock_id={RUNTIME_LOCK_ID}/"
        f"pilot_run_id={PILOT_RUN_ID}/execution-claim.json"
    )


def _split_s3_uri(uri: str) -> tuple[str, str]:
    if not uri.startswith("s3://") or uri.count("/") < 3:
        raise RemoteCustodyError("invalid S3 locator")
    bucket, _, key = uri[5:].partition("/")
    if not bucket or not key:
        raise RemoteCustodyError("invalid S3 locator")
    return bucket, key


class S3CliObjectStore:
    """AWS CLI S3 conditional-put adapter for raw entities and durable CAS."""

    def __init__(
        self,
        *,
        prefix: str = RAW_PREFIX,
        region: str = AWS_REGION,
        expected_bucket_owner: str = AWS_ACCOUNT_ID,
        command_runner: Callable[[Sequence[str]], subprocess.CompletedProcess[str]] | None = None,
    ) -> None:
        self.bucket, self.prefix_key = _split_s3_uri(prefix)
        if prefix != RAW_PREFIX:
            raise RemoteCustodyError("S3 store prefix is outside Finance authorization")
        self.region = region
        self.expected_bucket_owner = expected_bucket_owner
        self.command_runner = command_runner or self._run
        self.checkpoint_key = checkpoint_object_key()
        self.claim_key = execution_claim_object_key()

    @staticmethod
    def _run(command: Sequence[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            list(command), check=False, capture_output=True, text=True, timeout=90
        )

    def _base(self, operation: str) -> list[str]:
        return [
            "aws", "s3api", operation,
            "--bucket", self.bucket,
            "--region", self.region,
            "--expected-bucket-owner", self.expected_bucket_owner,
        ]

    def _assert_key(self, key: str) -> None:
        if not key.startswith(self.prefix_key) or ".." in key or "//" in key:
            raise RemoteCustodyError("S3 object key escaped exact Finance prefix")

    def _invoke(
        self, command: Sequence[str], *, allow_missing: bool = False
    ) -> dict[str, Any] | None:
        completed = self.command_runner(command)
        if completed.returncode != 0:
            lowered = (completed.stderr or "").lower()
            if allow_missing and any(x in lowered for x in ("nosuchkey", "not found", "404")):
                return None
            if any(x in lowered for x in ("preconditionfailed", "condition", "412")):
                raise sa.CheckpointConflictError("S3 conditional write conflict")
            raise RemoteCustodyError("AWS CLI S3 operation failed")
        try:
            value = json.loads(completed.stdout or "{}")
        except json.JSONDecodeError:
            raise RemoteCustodyError("AWS CLI returned malformed JSON") from None
        if not isinstance(value, dict):
            raise RemoteCustodyError("AWS CLI returned invalid object")
        return value

    def _get(
        self, key: str, *, version_id: str | None = None
    ) -> tuple[bytes, dict[str, Any]] | None:
        self._assert_key(key)
        with tempfile.NamedTemporaryFile(prefix="m3top3-s3-read-", delete=False) as handle:
            target = Path(handle.name)
        try:
            command = self._base("get-object") + [
                "--key", key, "--checksum-mode", "ENABLED"
            ]
            if version_id is not None:
                if not version_id:
                    raise RemoteCustodyError("empty S3 version binding")
                command += ["--version-id", version_id]
            command.append(str(target))
            metadata = self._invoke(command, allow_missing=True)
            if metadata is None:
                return None
            return target.read_bytes(), metadata
        finally:
            target.unlink(missing_ok=True)

    def load(self) -> tuple[Mapping[str, Any] | None, str | None]:
        result = self._get(self.checkpoint_key)
        if result is None:
            return None, None
        raw, metadata = result
        try:
            value = json.loads(raw)
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise RemoteCustodyError("remote checkpoint is malformed") from None
        if not isinstance(value, dict) or sa.canonical_json_bytes(value) != raw:
            raise RemoteCustodyError("remote checkpoint is not canonical JSON")
        etag = str(metadata.get("ETag", ""))
        version_id = str(metadata.get("VersionId", ""))
        sse = str(metadata.get("ServerSideEncryption", ""))
        if not etag or not version_id or sse != "AES256":
            raise RemoteCustodyError(
                "remote checkpoint missing ETag/VersionId/SSE evidence"
            )
        return value, self._checkpoint_token(etag, version_id, sse)

    @staticmethod
    def _checkpoint_token(etag: str, version_id: str, sse: str) -> str:
        return json.dumps(
            {"etag": etag, "version_id": version_id, "sse": sse},
            sort_keys=True,
            separators=(",", ":"),
        )

    @staticmethod
    def _checkpoint_etag(token: str) -> str:
        try:
            value = json.loads(token)
        except (TypeError, json.JSONDecodeError):
            raise sa.CheckpointConflictError(
                "invalid durable checkpoint CAS token"
            ) from None
        if (
            not isinstance(value, dict)
            or set(value) != {"etag", "version_id", "sse"}
            or not all(isinstance(value[key], str) and value[key] for key in value)
            or value["sse"] != "AES256"
        ):
            raise sa.CheckpointConflictError(
                "invalid durable checkpoint CAS evidence"
            )
        return value["etag"]

    def compare_and_swap(self, value: Mapping[str, Any], expected_token: str | None) -> str:
        if not isinstance(value, Mapping):
            raise RemoteCustodyError("invalid checkpoint value")
        payload = sa.canonical_json_bytes(dict(value))
        with tempfile.NamedTemporaryFile(prefix="m3top3-s3-cas-", delete=False) as handle:
            target = Path(handle.name)
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            command = self._base("put-object") + [
                "--key", self.checkpoint_key,
                "--body", str(target),
                "--content-type", "application/json",
                "--server-side-encryption", "AES256",
            ]
            command += (
                ["--if-none-match", "*"]
                if expected_token is None
                else ["--if-match", self._checkpoint_etag(expected_token)]
            )
            result = self._invoke(command)
            assert result is not None
            result_version = str(result.get("VersionId", ""))
            if not result_version:
                raise RemoteCustodyError("checkpoint CAS missing VersionId")
            readback = self._get(
                self.checkpoint_key, version_id=result_version
            )
            if readback is None or readback[0] != payload:
                raise RemoteCustodyError("remote checkpoint readback mismatch")
            etag = str(readback[1].get("ETag", result.get("ETag", "")))
            version_id = str(readback[1].get("VersionId", ""))
            sse = str(readback[1].get("ServerSideEncryption", ""))
            if not etag or version_id != result_version or sse != "AES256":
                raise RemoteCustodyError(
                    "remote checkpoint CAS readback evidence mismatch"
                )
            return self._checkpoint_token(etag, version_id, sse)
        finally:
            target.unlink(missing_ok=True)

    def acquire_execution_claim(
        self, claim: Mapping[str, Any]
    ) -> ExecutionClaimEvidence:
        if not isinstance(claim, Mapping):
            raise RemoteCustodyError("invalid execution claim")
        payload = sa.canonical_json_bytes(dict(claim))
        with tempfile.NamedTemporaryFile(prefix="m3top3-claim-", delete=False) as handle:
            target = Path(handle.name)
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            command = self._base("put-object") + [
                "--key", self.claim_key,
                "--body", str(target),
                "--content-type", "application/json",
                "--server-side-encryption", "AES256",
                "--if-none-match", "*",
            ]
            created_version: str | None = None
            try:
                result = self._invoke(command)
                assert result is not None
                created_version = str(result.get("VersionId", ""))
                if not created_version:
                    raise RemoteCustodyError(
                        "execution claim conditional create missing VersionId"
                    )
            except sa.CheckpointConflictError:
                pass
            readback = self._get(
                self.claim_key, version_id=created_version
            )
            if readback is None or readback[0] != payload:
                raise sa.CheckpointConflictError(
                    "Finance single-writer execution claim conflict"
                )
            metadata = readback[1]
            version_id = str(metadata.get("VersionId", ""))
            etag = str(metadata.get("ETag", ""))
            sse = str(metadata.get("ServerSideEncryption", ""))
            if not version_id or not etag or sse != "AES256":
                raise RemoteCustodyError("execution claim readback evidence missing")
            return ExecutionClaimEvidence(
                object_key=self.claim_key,
                content_sha256=hashlib.sha256(payload).hexdigest(),
                version_id=version_id,
                etag=etag,
                server_side_encryption=sse,
                write_precondition="IF_NONE_MATCH_STAR",
                writer_id=str(claim.get("writer_id", "")),
            )
        finally:
            target.unlink(missing_ok=True)

    def _read_raw_existing(
        self, object_key: str, *, expected_version_id: str | None = None
    ) -> SealedEntity | None:
        result = self._get(object_key, version_id=expected_version_id)
        if result is None:
            return None
        body, metadata = result
        user_metadata = metadata.get("Metadata", {})
        if not isinstance(user_metadata, Mapping):
            raise RemoteCustodyError("raw entity metadata missing")
        required_metadata = {
            "sha256", "http-status", "acquired-at-utc", "request-id", "bas-dt",
            "page-no", "attempt", "runtime-lock-id", "pilot-run-id",
            "quota-day-kst",
        }
        if set(user_metadata) != required_metadata:
            raise RemoteCustodyError("raw entity metadata key set mismatch")
        digest = hashlib.sha256(body).hexdigest()
        if str(user_metadata.get("sha256", "")) != digest:
            raise RemoteCustodyError("raw entity metadata digest mismatch")
        key_match = re.fullmatch(
            re.escape(self.prefix_key)
            + re.escape(sa.FINANCE_OPERATION)
            + r"/quota_day_kst=([^/]+)/request_id=([0-9a-f]{64})/"
            + r"attempt=([1-9][0-9]*)/sha256=([0-9a-f]{64})\.entity",
            object_key,
        )
        if key_match is None:
            raise RemoteCustodyError("raw entity canonical lineage key invalid")
        quota_day, request_id, attempt_text, key_digest = key_match.groups()
        try:
            bas_dt = str(user_metadata["bas-dt"])
            page_no = int(user_metadata["page-no"])
            attempt_no = int(user_metadata["attempt"])
        except (KeyError, TypeError, ValueError):
            raise RemoteCustodyError("raw entity request metadata invalid") from None
        expected_metadata = {
            "request-id": deterministic_request_id(bas_dt, page_no),
            "attempt": attempt_text,
            "quota-day-kst": PILOT_QUOTA_DAY_KST,
            "runtime-lock-id": RUNTIME_LOCK_ID,
            "pilot-run-id": PILOT_RUN_ID,
        }
        if (
            quota_day != PILOT_QUOTA_DAY_KST
            or bas_dt not in PRIMARY_DATES
            or not 1 <= page_no <= MAX_PAGES_PER_DATE
            or not 1 <= attempt_no <= MAX_ATTEMPTS_PER_PAGE
            or request_id != expected_metadata["request-id"]
            or key_digest != digest
            or any(str(user_metadata.get(key, "")) != value for key, value in expected_metadata.items())
            or not str(user_metadata.get("acquired-at-utc", ""))
        ):
            raise RemoteCustodyError("raw entity lineage metadata mismatch")
        try:
            acquired_at = datetime.fromisoformat(
                str(user_metadata["acquired-at-utc"])
            )
        except ValueError:
            raise RemoteCustodyError(
                "raw entity acquisition timestamp invalid"
            ) from None
        if acquired_at.tzinfo is None:
            raise RemoteCustodyError("raw entity acquisition timestamp is naive")
        version_id = str(metadata.get("VersionId", ""))
        sse = str(metadata.get("ServerSideEncryption", ""))
        etag = str(metadata.get("ETag", ""))
        if (
            not version_id
            or (expected_version_id is not None and version_id != expected_version_id)
            or sse != "AES256"
            or not etag
        ):
            raise RemoteCustodyError("raw entity version/SSE/ETag evidence missing")
        try:
            status = int(user_metadata["http-status"])
        except (KeyError, TypeError, ValueError):
            raise RemoteCustodyError("raw entity status metadata invalid") from None
        if not 100 <= status <= 599:
            raise RemoteCustodyError("raw entity HTTP status outside valid range")
        return SealedEntity(
            body=body,
            object_key=object_key,
            storage_locator=f"s3://{self.bucket}/{object_key}",
            entity_sha256=digest,
            entity_bytes=len(body),
            readback_sha256=digest,
            readback_bytes=len(body),
            version_id=version_id,
            etag=etag,
            server_side_encryption=sse,
            write_precondition="IF_NONE_MATCH_STAR",
            http_status=status,
            acquired_at_utc=str(user_metadata.get("acquired-at-utc", "")),
        )

    def read_existing(
        self, object_key: str, version_id: str | None = None
    ) -> SealedEntity | None:
        return self._read_raw_existing(
            object_key, expected_version_id=version_id
        )

    def find_existing_by_prefix(self, object_prefix: str) -> SealedEntity | None:
        self._assert_key(object_prefix)
        result = self._invoke(
            self._base("list-objects-v2")
            + ["--prefix", object_prefix, "--max-keys", "2"]
        )
        assert result is not None
        contents = result.get("Contents", [])
        if (
            not isinstance(contents, list)
            or result.get("IsTruncated") is True
        ):
            raise RemoteCustodyError("raw reconciliation listing malformed")
        keys = [
            row.get("Key") for row in contents if isinstance(row, Mapping)
        ]
        pattern = re.compile(
            re.escape(object_prefix) + r"sha256=[0-9a-f]{64}\.entity"
        )
        if (
            len(keys) != len(contents)
            or any(not isinstance(key, str) or pattern.fullmatch(key) is None for key in keys)
            or len(keys) > 1
        ):
            raise RemoteCustodyError(
                "unexpected or multiple raw entities for one reserved attempt"
            )
        return self.read_existing(keys[0]) if keys else None

    def seal_and_readback(
        self, object_key: str, body: bytes, metadata: Mapping[str, str]
    ) -> SealedEntity:
        self._assert_key(object_key)
        digest = hashlib.sha256(body).hexdigest()
        if metadata.get("sha256") != digest:
            raise RemoteCustodyError("raw custody draft digest mismatch")
        allowed = {
            "sha256", "http-status", "acquired-at-utc", "request-id", "bas-dt",
            "page-no", "attempt", "runtime-lock-id", "pilot-run-id",
            "quota-day-kst",
        }
        safe_metadata = {
            str(key): str(value) for key, value in metadata.items() if key in allowed
        }
        required_metadata = {
            "sha256", "http-status", "acquired-at-utc", "request-id", "bas-dt",
            "page-no", "attempt", "runtime-lock-id", "pilot-run-id",
            "quota-day-kst",
        }
        if set(safe_metadata) != required_metadata or set(metadata) != required_metadata:
            raise RemoteCustodyError("raw custody lineage metadata incomplete")
        expected_key = canonical_raw_object_key(
            deterministic_raw_object_prefix(
                safe_metadata["bas-dt"],
                int(safe_metadata["page-no"]),
                int(safe_metadata["attempt"]),
                safe_metadata["quota-day-kst"],
            ),
            digest,
        )
        if (
            object_key != expected_key
            or safe_metadata["request-id"]
            != deterministic_request_id(
                safe_metadata["bas-dt"], int(safe_metadata["page-no"])
            )
            or safe_metadata["runtime-lock-id"] != RUNTIME_LOCK_ID
            or safe_metadata["pilot-run-id"] != PILOT_RUN_ID
        ):
            raise RemoteCustodyError("raw custody lineage metadata mismatch")
        with tempfile.NamedTemporaryFile(prefix="m3top3-raw-", delete=False) as handle:
            target = Path(handle.name)
            handle.write(body)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            command = self._base("put-object") + [
                "--key", object_key,
                "--body", str(target),
                "--content-type", "application/octet-stream",
                "--server-side-encryption", "AES256",
                "--if-none-match", "*",
                "--metadata",
                ",".join(f"{key}={safe_metadata[key]}" for key in sorted(safe_metadata)),
            ]
            created_version: str | None = None
            try:
                result = self._invoke(command)
                assert result is not None
                created_version = str(result.get("VersionId", ""))
                if not created_version:
                    raise RemoteCustodyError(
                        "raw conditional seal missing VersionId"
                    )
            except sa.CheckpointConflictError:
                pass
            sealed = self._read_raw_existing(
                object_key, expected_version_id=created_version
            )
            if (
                sealed is None
                or sealed.body != body
                or sealed.http_status != int(safe_metadata["http-status"])
                or sealed.acquired_at_utc != safe_metadata["acquired-at-utc"]
            ):
                raise RemoteCustodyError("raw entity exclusive seal/readback mismatch")
            return sealed
        finally:
            target.unlink(missing_ok=True)


class UrlLibFinanceTransport:
    """One-attempt transport. Retry policy belongs exclusively to the runner."""

    def __init__(
        self, secret: str, *, timeout_seconds: float = 20.0, opener: Any | None = None
    ) -> None:
        self.secret = sa.validate_decoded_secret(FINANCE_SECRET_ENV, secret)
        self.timeout_seconds = timeout_seconds
        self.opener = opener or urllib.request.build_opener(sa.NoRedirect())

    def fetch_once(self, params: Mapping[str, str]) -> TransportResponse:
        url = sa.encoded_query(sa.FINANCE_URL, params, self.secret)
        request = urllib.request.Request(
            url,
            headers={
                "Accept": "application/json",
                "Accept-Encoding": "identity",
                "User-Agent": "AAA-M3Top3-Finance-Live-Pilot/1.0",
            },
        )
        acquired_at = _iso_utc(_utc_now)
        try:
            response = self.opener.open(request, timeout=self.timeout_seconds)
            status = int(getattr(response, "status", response.getcode()))
            body = response.read()
            headers = {
                str(key).lower(): str(value)
                for key, value in response.headers.items()
                if str(key).lower() in SAFE_RESPONSE_HEADERS
            }
        except urllib.error.HTTPError as exc:
            status = int(exc.code)
            body = exc.read()
            headers = {
                str(key).lower(): str(value)
                for key, value in exc.headers.items()
                if str(key).lower() in SAFE_RESPONSE_HEADERS
            }
        except (urllib.error.URLError, TimeoutError, OSError):
            raise NoEntityTransportError(
                "Finance transport ended without response entity"
            ) from None
        return TransportResponse(
            body=body,
            http_status=status,
            safe_headers=headers,
            acquired_at_utc=acquired_at,
        )


def _read_baseline_quota_ledger(path: Path) -> tuple[str, list[dict[str, Any]]]:
    try:
        raw = path.read_bytes()
    except OSError:
        raise AuthorityBindingError("baseline quota ledger missing") from None
    rows: list[dict[str, Any]] = []
    try:
        for line_with_ending in raw.splitlines(keepends=True):
            line = line_with_ending.rstrip(b"\r\n")
            if not line:
                continue
            row = json.loads(line, object_pairs_hook=_reject_duplicate_pairs)
            if not isinstance(row, dict):
                raise ValueError
            rows.append(row)
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError):
        raise AuthorityBindingError("baseline quota ledger malformed") from None
    baseline = [row for row in rows if "pilot_run_id" not in row]
    if len(baseline) != 7:
        raise AuthorityBindingError("governed baseline quota row count mismatch")
    for row in baseline:
        if (
            row.get("event") != "QUOTA_SLOT_SPENT"
            or row.get("quota_day_kst") != HISTORICAL_BASELINE_QUOTA_DAY_KST
            or row.get("provider") not in {"FINANCE", "KSD"}
        ):
            raise AuthorityBindingError("governed baseline quota binding mismatch")
    finance = [
        row for row in baseline
        if row.get("provider") == "FINANCE"
        and row.get("event") == "QUOTA_SLOT_SPENT"
    ]
    ksd = [
        row for row in baseline
        if row.get("provider") == "KSD"
        and row.get("event") == "QUOTA_SLOT_SPENT"
    ]
    if [row.get("ordinal") for row in finance] != list(
        range(1, HISTORICAL_BASELINE_FINANCE_LAST_ORDINAL + 1)
    ):
        raise AuthorityBindingError("Finance baseline quota ordinals mismatch")
    if [row.get("ordinal") for row in ksd] != list(
        range(1, HISTORICAL_BASELINE_KSD_LAST_ORDINAL + 1)
    ):
        raise AuthorityBindingError("KSD baseline quota ordinals mismatch")
    if any(row.get("operation") != sa.FINANCE_OPERATION for row in finance):
        raise AuthorityBindingError("Finance baseline quota operation mismatch")
    expected_ksd_operations = {
        1: "getIssucoCustnoByShortIsin",
        2: "getIssucoBasicInfo",
    }
    if any(
        row.get("operation") != expected_ksd_operations[row["ordinal"]]
        for row in ksd
    ):
        raise AuthorityBindingError("KSD baseline quota operation mismatch")
    # Preserve the exact governed pre-pilot bytes, including field order and
    # line endings. Pilot rows appended by an earlier mirror are excluded.
    return hashlib.sha256(
        _governed_baseline_jsonl_bytes(path)
    ).hexdigest(), baseline


def _execution_claim_material(
    bindings: ExecutionBindings, writer_id: str
) -> dict[str, Any]:
    if (
        _WRITER_ID_RE.fullmatch(writer_id) is None
        or writer_id != f"github-run:{bindings.github_run_id}"
    ):
        raise AuthorityBindingError("invalid Finance single-writer identity")
    return {
        "artifact": "M3TOP3_FINANCE_LIVE_PILOT_EXECUTION_CLAIM_v1.0",
        "schema_version": 1,
        "state": "SINGLE_WRITER_CLAIMED",
        "runtime_lock_id": RUNTIME_LOCK_ID,
        "pilot_run_id": PILOT_RUN_ID,
        "writer_id": writer_id,
        "github_repository": bindings.github_repository,
        "github_ref": bindings.github_ref,
        "github_sha": bindings.github_sha,
        "github_actor": bindings.github_actor,
        "github_triggering_actor": bindings.github_triggering_actor,
        "github_run_id": bindings.github_run_id,
        "github_run_attempt_semantics": (
            "RECORDED_PER_RESERVATION_NOT_SINGLE_WRITER_CLAIM_IDENTITY"
        ),
        "authority_sha256": bindings.authority_sha256,
        "plan_sha256": bindings.plan_sha256,
        "latch_execution_material_sha256": (
            bindings.latch_execution_material_sha256
        ),
        "runner_sha256": bindings.runner_sha256,
        "source_admission_sha256": bindings.source_admission_sha256,
        "checkpoint_template_sha256": bindings.checkpoint_template_sha256,
        "baseline_quota_ledger_sha256": bindings.baseline_quota_ledger_sha256,
        "baseline_raw_index_sha256": bindings.baseline_raw_index_sha256,
        "owner_cap_spec_sha256": OWNER_CAP_SPEC_SHA256,
        "quota_day_kst": PILOT_QUOTA_DAY_KST,
        "source_id": sa.FINANCE_SOURCE_ID,
        "remote_raw_custody_prefix": RAW_PREFIX,
    }


def _claim_evidence_record(
    evidence: ExecutionClaimEvidence,
) -> dict[str, Any]:
    return {
        "object_key": evidence.object_key,
        "content_sha256": evidence.content_sha256,
        "version_id": evidence.version_id,
        "etag": evidence.etag,
        "server_side_encryption": evidence.server_side_encryption,
        "write_precondition": evidence.write_precondition,
        "writer_id": evidence.writer_id,
    }


def _workflow_identity_record(bindings: ExecutionBindings) -> dict[str, Any]:
    return {
        "repository": bindings.github_repository,
        "ref": bindings.github_ref,
        "sha": bindings.github_sha,
        "actor": bindings.github_actor,
        "triggering_actor": bindings.github_triggering_actor,
        "run_id": bindings.github_run_id,
        "run_attempt_semantics": (
            "RECORDED_PER_RESERVATION_NOT_SINGLE_WRITER_CLAIM_IDENTITY"
        ),
    }


def _initial_checkpoint(
    spec: LivePilotSpec,
    bindings: ExecutionBindings,
    claim_evidence: ExecutionClaimEvidence,
    *,
    clock: Callable[[], datetime],
) -> dict[str, Any]:
    return {
        "artifact": "M3TOP3_FINANCE_CA_ACQUISITION_CHECKPOINT_v1.0",
        "schema_version": 2,
        "checkpoint_role": "DURABLE_FINANCE_ONLY_LIVE_PILOT_CAS",
        "checkpoint_revision": 0,
        "state": "IN_PROGRESS",
        "runtime_lock_id": spec.runtime_lock_id,
        "pilot_run_id": spec.pilot_run_id,
        "owner_cap_spec_sha256": spec.owner_cap_spec_sha256,
        "authority_sha256": bindings.authority_sha256,
        "plan_sha256": bindings.plan_sha256,
        "latch_execution_material_sha256": bindings.latch_execution_material_sha256,
        "runner_sha256": bindings.runner_sha256,
        "source_admission_sha256": bindings.source_admission_sha256,
        "checkpoint_template_sha256": bindings.checkpoint_template_sha256,
        "baseline_quota_ledger_sha256": bindings.baseline_quota_ledger_sha256,
        "baseline_raw_index_sha256": bindings.baseline_raw_index_sha256,
        "execution_claim": _claim_evidence_record(claim_evidence),
        "workflow_execution_identity": _workflow_identity_record(bindings),
        "source_id": sa.FINANCE_SOURCE_ID,
        "operation": sa.FINANCE_OPERATION,
        "ordered_dates": list(spec.ordered_dates),
        "request_page_size": spec.request_page_size,
        "max_pages_per_date": spec.max_pages_per_date,
        "max_primary_page_slots": spec.max_primary_page_slots,
        "max_network_attempts_total": spec.max_network_attempts_total,
        "max_attempts_per_page": spec.max_attempts_per_page,
        "remote_raw_custody_prefix": spec.raw_prefix,
        "quota_day_kst": PILOT_QUOTA_DAY_KST,
        "observed_github_run_attempts": [],
        "next_date_index": 0,
        "completed_dates": [],
        "date_results": [],
        "current_date": None,
        "unique_page_slots": [],
        "attempts": [],
        "raw_index": [],
        "quota_reservations": 0,
        "network_attempts_started_conservative": 0,
        "response_entities_received": 0,
        "no_entity_attempts": 0,
        "remote_raw_custody_writes_or_reconciliations": 0,
        "raw_entity_bytes": 0,
        "http_status_counts": {},
        "event_code_counts": {},
        "event_code_name_counts": {},
        "date_echo_match_rows": 0,
        "issuer_identity_rows_checked": 0,
        "issuer_identity_match_rows": 0,
        "issuer_identity_conflicts": 0,
        "issuer_identity_missing_rows": 0,
        "issuer_identity_hashes": {},
        "seen_item_sha256": [],
        "exact_duplicate_items": 0,
        "last_error_class": None,
        "normalization_records_created": 0,
        "promotion_actions": 0,
        "bulk_acquisition_authorized": False,
        "model_semantic_change_authorized": False,
        "pit_semantic_change_authorized": False,
        "validation_claim": "NONE",
        "gate_effect": "NONE",
        "updated_at_utc": _iso_utc(clock),
    }


def _assert_checkpoint_binding(
    checkpoint: Mapping[str, Any],
    spec: LivePilotSpec,
    bindings: ExecutionBindings,
    claim_evidence: ExecutionClaimEvidence,
) -> None:
    expected = {
        "artifact": "M3TOP3_FINANCE_CA_ACQUISITION_CHECKPOINT_v1.0",
        "schema_version": 2,
        "checkpoint_role": "DURABLE_FINANCE_ONLY_LIVE_PILOT_CAS",
        "runtime_lock_id": spec.runtime_lock_id,
        "pilot_run_id": spec.pilot_run_id,
        "owner_cap_spec_sha256": spec.owner_cap_spec_sha256,
        "authority_sha256": bindings.authority_sha256,
        "plan_sha256": bindings.plan_sha256,
        "latch_execution_material_sha256": bindings.latch_execution_material_sha256,
        "runner_sha256": bindings.runner_sha256,
        "source_admission_sha256": bindings.source_admission_sha256,
        "checkpoint_template_sha256": bindings.checkpoint_template_sha256,
        "baseline_quota_ledger_sha256": bindings.baseline_quota_ledger_sha256,
        "baseline_raw_index_sha256": bindings.baseline_raw_index_sha256,
        "execution_claim": _claim_evidence_record(claim_evidence),
        "workflow_execution_identity": _workflow_identity_record(bindings),
        "source_id": sa.FINANCE_SOURCE_ID,
        "operation": sa.FINANCE_OPERATION,
        "ordered_dates": list(spec.ordered_dates),
        "request_page_size": REQUEST_PAGE_SIZE,
        "max_pages_per_date": MAX_PAGES_PER_DATE,
        "max_primary_page_slots": MAX_PRIMARY_PAGE_SLOTS,
        "max_network_attempts_total": MAX_NETWORK_ATTEMPTS_TOTAL,
        "max_attempts_per_page": MAX_ATTEMPTS_PER_PAGE,
        "remote_raw_custody_prefix": RAW_PREFIX,
        "quota_day_kst": PILOT_QUOTA_DAY_KST,
        "normalization_records_created": 0,
        "promotion_actions": 0,
        "bulk_acquisition_authorized": False,
        "model_semantic_change_authorized": False,
        "pit_semantic_change_authorized": False,
        "validation_claim": "NONE",
        "gate_effect": "NONE",
    }
    for field, value in expected.items():
        if checkpoint.get(field) != value:
            raise sa.CheckpointConflictError(f"live checkpoint binding mismatch: {field}")
    completed = checkpoint.get("completed_dates")
    next_index = checkpoint.get("next_date_index")
    if not isinstance(completed, list) or completed != list(PRIMARY_DATES[: len(completed)]):
        raise sa.CheckpointConflictError("completed Finance dates are not an ordered prefix")
    if type(next_index) is not int or next_index != len(completed):
        raise sa.CheckpointConflictError("Finance next-date checkpoint mismatch")
    if checkpoint.get("quota_reservations", -1) > MAX_NETWORK_ATTEMPTS_TOTAL:
        raise sa.CheckpointConflictError("Finance quota reservation cap exceeded")
    if len(checkpoint.get("unique_page_slots", [])) > MAX_PRIMARY_PAGE_SLOTS:
        raise sa.CheckpointConflictError("Finance unique page-slot cap exceeded")
    if checkpoint.get("state") not in {"IN_PROGRESS", "BLOCKED", "COMPLETE"}:
        raise sa.CheckpointConflictError("Finance checkpoint state invalid")
    attempts = checkpoint.get("attempts")
    raw_index = checkpoint.get("raw_index")
    slots = checkpoint.get("unique_page_slots")
    results = checkpoint.get("date_results")
    if not all(isinstance(value, list) for value in (attempts, raw_index, slots, results)):
        raise sa.CheckpointConflictError("Finance checkpoint collection shape invalid")
    if len(results) != len(completed):
        raise sa.CheckpointConflictError("Finance date-result prefix mismatch")
    if [row.get("basDt") for row in results if isinstance(row, Mapping)] != completed:
        raise sa.CheckpointConflictError("Finance date-result order mismatch")
    counters = {
        "quota_reservations": len(attempts),
        "network_attempts_started_conservative": len(attempts),
        "response_entities_received": len(raw_index),
        "remote_raw_custody_writes_or_reconciliations": len(raw_index),
        "raw_entity_bytes": sum(
            row.get("entity_bytes", -1)
            for row in raw_index if isinstance(row, Mapping)
        ),
    }
    if any(checkpoint.get(key) != value for key, value in counters.items()):
        raise sa.CheckpointConflictError("Finance checkpoint counter mismatch")
    expected_ordinals = list(
        range(
            PILOT_FINANCE_ORDINAL_BASE + 1,
            PILOT_FINANCE_ORDINAL_BASE + len(attempts) + 1,
        )
    )
    if [row.get("provider_quota_ordinal") for row in attempts if isinstance(row, Mapping)] != expected_ordinals:
        raise sa.CheckpointConflictError("Finance quota ordinals are not continuous")

    observed_slots: list[str] = []
    per_slot_attempts: dict[str, list[int]] = {}
    for row in attempts:
        if not isinstance(row, Mapping):
            raise sa.CheckpointConflictError("Finance attempt record invalid")
        bas_dt = row.get("basDt")
        page_no = row.get("page_no")
        attempt_no = row.get("attempt")
        if (
            bas_dt not in PRIMARY_DATES
            or type(page_no) is not int
            or not 1 <= page_no <= MAX_PAGES_PER_DATE
            or type(attempt_no) is not int
            or row.get("state") not in ATTEMPT_STATES
            or row.get("quota_day_kst") != PILOT_QUOTA_DAY_KST
            or row.get("github_run_id") != bindings.github_run_id
            or type(row.get("run_attempt")) is not int
            or row.get("run_attempt") < 1
            or row.get("request_id") != deterministic_request_id(bas_dt, page_no)
        ):
            raise sa.CheckpointConflictError("Finance attempt lineage invalid")
        expected_prefix = deterministic_raw_object_prefix(
            bas_dt, page_no, attempt_no, PILOT_QUOTA_DAY_KST
        )
        if row.get("raw_object_prefix") != expected_prefix:
            raise sa.CheckpointConflictError("Finance raw object prefix mismatch")
        slot = f"{bas_dt}:{page_no}"
        if slot not in observed_slots:
            observed_slots.append(slot)
        per_slot_attempts.setdefault(slot, []).append(attempt_no)
    if slots != observed_slots:
        raise sa.CheckpointConflictError("Finance unique page slots mismatch")
    if any(values != list(range(1, len(values) + 1)) or len(values) > MAX_ATTEMPTS_PER_PAGE for values in per_slot_attempts.values()):
        raise sa.CheckpointConflictError("Finance per-page attempt sequence invalid")
    observed_run_attempts = list(dict.fromkeys(
        row["run_attempt"] for row in attempts
    ))
    if checkpoint.get("observed_github_run_attempts") != observed_run_attempts:
        raise sa.CheckpointConflictError(
            "Finance observed GitHub run-attempt ledger mismatch"
        )

    raw_by_attempt: dict[tuple[str, int, int], Mapping[str, Any]] = {}
    status_counts: dict[str, int] = {}
    for row in raw_index:
        if not isinstance(row, Mapping):
            raise sa.CheckpointConflictError("Finance raw index record invalid")
        identity = (row.get("basDt"), row.get("page_no"), row.get("attempt"))
        if identity in raw_by_attempt:
            raise sa.CheckpointConflictError("duplicate Finance raw attempt reference")
        raw_by_attempt[identity] = row
        matching = [
            attempt for attempt in attempts
            if (attempt.get("basDt"), attempt.get("page_no"), attempt.get("attempt")) == identity
        ]
        digest = row.get("entity_sha256")
        if (
            len(matching) != 1
            or row.get("runtime_lock_id") != RUNTIME_LOCK_ID
            or row.get("pilot_run_id") != PILOT_RUN_ID
            or row.get("source_id") != sa.FINANCE_SOURCE_ID
            or row.get("operation") != sa.FINANCE_OPERATION
            or row.get("quota_day_kst") != PILOT_QUOTA_DAY_KST
            or row.get("request_id") != matching[0].get("request_id")
            or row.get("provider_quota_ordinal") != matching[0].get("provider_quota_ordinal")
            or row.get("github_run_id") != matching[0].get("github_run_id")
            or row.get("run_attempt") != matching[0].get("run_attempt")
            or row.get("s3_object_prefix") != matching[0].get("raw_object_prefix")
            or not isinstance(digest, str)
            or _SHA256_RE.fullmatch(digest) is None
            or type(row.get("entity_bytes")) is not int
            or row.get("entity_bytes") < 0
            or row.get("s3_object_key") != canonical_raw_object_key(row["s3_object_prefix"], digest)
            or row.get("remote_readback_sha256") != digest
            or row.get("remote_readback_bytes") != row.get("entity_bytes")
            or row.get("server_side_encryption") != "AES256"
            or row.get("write_precondition") != "IF_NONE_MATCH_STAR"
            or not row.get("s3_version_id")
        ):
            raise sa.CheckpointConflictError("Finance raw custody reference mismatch")
        status_key = str(row.get("http_status"))
        status_counts[status_key] = status_counts.get(status_key, 0) + 1
    if checkpoint.get("http_status_counts") != status_counts:
        raise sa.CheckpointConflictError("Finance HTTP status counters mismatch")
    for attempt in attempts:
        identity = (attempt["basDt"], attempt["page_no"], attempt["attempt"])
        has_raw = identity in raw_by_attempt
        if bool(attempt.get("response_entity_received")) != has_raw:
            raise sa.CheckpointConflictError("Finance response/raw reference mismatch")
        raw_required_states = ATTEMPT_STATES - {
            "RESERVED_WRITE_AHEAD",
            "RESERVATION_SPENT_NO_REMOTE_ENTITY_ON_RESUME",
            "NO_RESPONSE_ENTITY_RESERVATION_SPENT",
        }
        if (attempt.get("state") in raw_required_states) != has_raw:
            raise sa.CheckpointConflictError(
                "Finance attempt state/raw implication mismatch"
            )
        if has_raw and attempt.get("object_key") != raw_by_attempt[identity].get("s3_object_key"):
            raise sa.CheckpointConflictError("Finance attempt object key mismatch")
    no_entity_states = {
        "NO_RESPONSE_ENTITY_RESERVATION_SPENT",
        "RESERVATION_SPENT_NO_REMOTE_ENTITY_ON_RESUME",
    }
    if checkpoint.get("no_entity_attempts") != sum(
        1 for attempt in attempts if attempt.get("state") in no_entity_states
    ):
        raise sa.CheckpointConflictError("Finance no-entity counter mismatch")
    current = checkpoint.get("current_date")
    if current is not None:
        if (
            not isinstance(current, Mapping)
            or next_index >= len(PRIMARY_DATES)
            or current.get("basDt") != PRIMARY_DATES[next_index]
            or current.get("state") != "IN_PROGRESS"
        ):
            raise sa.CheckpointConflictError("Finance current-date binding invalid")
        validated = current.get("validated_pages")
        if not isinstance(validated, list):
            raise sa.CheckpointConflictError("Finance validated page list invalid")
        if [row.get("page_no") for row in validated if isinstance(row, Mapping)] != list(range(1, len(validated) + 1)):
            raise sa.CheckpointConflictError("Finance validated page prefix invalid")
        if not validated:
            if any(
                current.get(key) is not None
                for key in ("total_count", "page_size", "expected_pages")
            ) or current.get("cumulative_item_count") != 0:
                raise sa.CheckpointConflictError(
                    "Finance empty current-date progress invalid"
                )
        else:
            total_count = current.get("total_count")
            expected_pages = current.get("expected_pages")
            if (
                type(total_count) is not int
                or total_count < 0
                or current.get("page_size") != REQUEST_PAGE_SIZE
                or type(expected_pages) is not int
                or not 1 <= expected_pages <= MAX_PAGES_PER_DATE
                or expected_pages
                != max(1, math.ceil(total_count / REQUEST_PAGE_SIZE))
                or len(validated) > expected_pages
            ):
                raise sa.CheckpointConflictError(
                    "Finance current pagination bounds invalid"
                )
            running_count = 0
            nonempty_fingerprints: list[str] = []
            for page_row in validated:
                if not isinstance(page_row, Mapping):
                    raise sa.CheckpointConflictError(
                        "Finance validated page record invalid"
                    )
                item_count = page_row.get("item_count")
                fingerprint = page_row.get("page_fingerprint_sha256")
                if (
                    type(item_count) is not int
                    or not 0 <= item_count <= REQUEST_PAGE_SIZE
                    or not isinstance(fingerprint, str)
                    or _SHA256_RE.fullmatch(fingerprint) is None
                ):
                    raise sa.CheckpointConflictError(
                        "Finance validated page telemetry invalid"
                    )
                running_count += item_count
                if page_row.get("cumulative_item_count") != running_count:
                    raise sa.CheckpointConflictError(
                        "Finance validated cumulative count invalid"
                    )
                if item_count:
                    nonempty_fingerprints.append(fingerprint)
                matching_parsed = [
                    attempt for attempt in attempts
                    if attempt.get("basDt") == current["basDt"]
                    and attempt.get("page_no") == page_row["page_no"]
                    and attempt.get("state") == "PARSED_200"
                    and attempt.get("entity_sha256") == page_row.get("entity_sha256")
                    and attempt.get("s3_version_id") == page_row.get("s3_version_id")
                ]
                if not matching_parsed:
                    raise sa.CheckpointConflictError(
                        "Finance validated page has no parsed raw reference"
                    )
            if (
                current.get("cumulative_item_count") != running_count
                or current.get("page_fingerprints") != nonempty_fingerprints
                or running_count > total_count
            ):
                raise sa.CheckpointConflictError(
                    "Finance current page aggregate mismatch"
                )
    allowed_attempt_dates = set(completed)
    if isinstance(current, Mapping) and isinstance(current.get("basDt"), str):
        allowed_attempt_dates.add(current["basDt"])
    if any(attempt["basDt"] not in allowed_attempt_dates for attempt in attempts):
        raise sa.CheckpointConflictError(
            "Finance attempt exists outside completed/current date prefix"
        )

    result_keys = {
        "basDt", "state", "page_count", "item_count", "total_count",
        "page_1_identity", "resume_page_1_revalidations", "valid_empty",
    }
    aggregate_items = 0
    for result in results:
        if not isinstance(result, Mapping) or set(result) != result_keys:
            raise sa.CheckpointConflictError("Finance date result shape invalid")
        bas_dt = result["basDt"]
        page_count = result["page_count"]
        item_count = result["item_count"]
        total_count = result["total_count"]
        revalidations = result["resume_page_1_revalidations"]
        if (
            result["state"] != "DATE_COMPLETE"
            or type(page_count) is not int
            or not 1 <= page_count <= MAX_PAGES_PER_DATE
            or type(item_count) is not int
            or type(total_count) is not int
            or item_count < 0
            or item_count != total_count
            or item_count > page_count * REQUEST_PAGE_SIZE
            or page_count
            != max(1, math.ceil(total_count / REQUEST_PAGE_SIZE))
            or not isinstance(result["page_1_identity"], str)
            or _SHA256_RE.fullmatch(result["page_1_identity"]) is None
            or type(revalidations) is not int
            or revalidations not in {0, 1}
            or result["valid_empty"] is not (total_count == 0)
        ):
            raise sa.CheckpointConflictError("Finance date result value invalid")
        parsed_page_numbers = {
            attempt["page_no"] for attempt in attempts
            if attempt["basDt"] == bas_dt and attempt["state"] == "PARSED_200"
        }
        all_page_numbers = {
            attempt["page_no"] for attempt in attempts
            if attempt["basDt"] == bas_dt
        }
        expected_page_numbers = set(range(1, page_count + 1))
        if (
            not expected_page_numbers.issubset(parsed_page_numbers)
            or not all_page_numbers.issubset(expected_page_numbers)
        ):
            raise sa.CheckpointConflictError(
                "Finance date result lacks exact parsed page coverage"
            )
        aggregate_items += item_count
    telemetry_items = aggregate_items + (
        int(current.get("cumulative_item_count", 0))
        if isinstance(current, Mapping) else 0
    )
    event_count_total = sum(
        value for value in checkpoint.get("event_code_counts", {}).values()
        if type(value) is int and value >= 0
    )
    event_pair_total = sum(
        value for value in checkpoint.get("event_code_name_counts", {}).values()
        if type(value) is int and value >= 0
    )
    seen_items = checkpoint.get("seen_item_sha256")
    duplicate_items = checkpoint.get("exact_duplicate_items")
    if (
        not isinstance(checkpoint.get("event_code_counts"), Mapping)
        or not isinstance(checkpoint.get("event_code_name_counts"), Mapping)
        or not isinstance(seen_items, list)
        or any(not isinstance(value, str) or _SHA256_RE.fullmatch(value) is None for value in seen_items)
        or len(seen_items) != len(set(seen_items))
        or type(duplicate_items) is not int
        or duplicate_items < 0
        or telemetry_items != checkpoint.get("date_echo_match_rows")
        or event_count_total != telemetry_items
        or event_pair_total != telemetry_items
        or len(seen_items) + duplicate_items != telemetry_items
        or checkpoint.get("issuer_identity_rows_checked", 0)
        + checkpoint.get("issuer_identity_missing_rows", 0) != telemetry_items
        or checkpoint.get("issuer_identity_match_rows", 0)
        + checkpoint.get("issuer_identity_conflicts", 0)
        != checkpoint.get("issuer_identity_rows_checked", 0)
    ):
        raise sa.CheckpointConflictError(
            "Finance completed-result telemetry aggregate mismatch"
        )
    if checkpoint.get("state") == "COMPLETE" and (
        completed != list(PRIMARY_DATES) or current is not None
    ):
        raise sa.CheckpointConflictError("complete Finance checkpoint is incomplete")


def _attempts_for(
    checkpoint: Mapping[str, Any], bas_dt: str, page_no: int
) -> list[dict[str, Any]]:
    return [
        row for row in checkpoint["attempts"]
        if row.get("basDt") == bas_dt and row.get("page_no") == page_no
    ]


def _raw_record(
    attempt: Mapping[str, Any], sealed: SealedEntity, *, reconciled: bool
) -> dict[str, Any]:
    return {
        "pilot_run_id": PILOT_RUN_ID,
        "runtime_lock_id": RUNTIME_LOCK_ID,
        "source_id": sa.FINANCE_SOURCE_ID,
        "operation": sa.FINANCE_OPERATION,
        "basDt": attempt["basDt"],
        "page_no": attempt["page_no"],
        "attempt": attempt["attempt"],
        "request_id": attempt["request_id"],
        "quota_day_kst": attempt["quota_day_kst"],
        "provider_quota_ordinal": attempt["provider_quota_ordinal"],
        "github_run_id": attempt["github_run_id"],
        "run_attempt": attempt["run_attempt"],
        "http_status": sealed.http_status,
        "entity_bytes": sealed.entity_bytes,
        "entity_sha256": sealed.entity_sha256,
        "storage_locator": sealed.storage_locator,
        "s3_object_key": sealed.object_key,
        "s3_object_prefix": attempt["raw_object_prefix"],
        "s3_version_id": sealed.version_id,
        "s3_etag": sealed.etag,
        "server_side_encryption": sealed.server_side_encryption,
        "write_precondition": sealed.write_precondition,
        "remote_readback_bytes": sealed.readback_bytes,
        "remote_readback_sha256": sealed.readback_sha256,
        "acquired_at_utc": sealed.acquired_at_utc,
        "reconciled_after_custody_before_checkpoint_gap": reconciled,
        "canonical": True,
        "credential_bearing_endpoint_material_absent": True,
        "secret_persisted": False,
        "normalization_effect": "NONE",
        "promotion_effect": "NONE",
    }


def _observe_items(checkpoint: dict[str, Any], items: list[dict[str, Any]]) -> None:
    seen = set(checkpoint["seen_item_sha256"])
    identities: dict[str, str] = checkpoint["issuer_identity_hashes"]
    for item in items:
        item_sha = hashlib.sha256(sa.canonical_json_bytes(item)).hexdigest()
        if item_sha in seen:
            checkpoint["exact_duplicate_items"] += 1
        else:
            seen.add(item_sha)
        code = str(item.get("rgtExertRcd") or "<EMPTY>")
        checkpoint["event_code_counts"][code] = (
            checkpoint["event_code_counts"].get(code, 0) + 1
        )
        name = str(item.get("rgtExertRcdNm") or "<EMPTY>")
        pair_key = json.dumps(
            {"code": code, "name": name},
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        checkpoint["event_code_name_counts"][pair_key] = (
            checkpoint["event_code_name_counts"].get(pair_key, 0) + 1
        )
        checkpoint["date_echo_match_rows"] += 1
        custody_no = str(item.get("issuCmpyKsdCustNo") or "")
        if not custody_no:
            checkpoint["issuer_identity_missing_rows"] += 1
            continue
        identity_sha = hashlib.sha256(
            sa.canonical_json_bytes(
                {
                    "issuCmpyKsdCustNo": custody_no,
                    "crno": str(item.get("crno") or ""),
                    "stckIssuCmpyNm": str(item.get("stckIssuCmpyNm") or ""),
                }
            )
        ).hexdigest()
        checkpoint["issuer_identity_rows_checked"] += 1
        previous = identities.get(custody_no)
        if previous is not None and previous != identity_sha:
            checkpoint["issuer_identity_conflicts"] += 1
        else:
            identities[custody_no] = identity_sha
            checkpoint["issuer_identity_match_rows"] += 1
    checkpoint["seen_item_sha256"] = sorted(seen)


def _build_report(
    checkpoint: Mapping[str, Any], checkpoint_token: str | None
) -> dict[str, Any]:
    results = list(checkpoint.get("date_results", []))
    total_items = sum(int(row.get("item_count", 0)) for row in results)
    data_dates = sum(1 for row in results if int(row.get("item_count", 0)) > 0)
    completed = len(checkpoint.get("completed_dates", []))
    state = str(checkpoint.get("state", "BLOCKED"))
    issuer_conflicts = int(checkpoint.get("issuer_identity_conflicts", 0))
    complete_exact = state == "COMPLETE" and completed == len(PRIMARY_DATES)
    quarantined = issuer_conflicts > 0
    if not complete_exact:
        promotion_decision = "STOP_NO_PROMOTION_PILOT_BLOCKED"
    elif data_dates == 0:
        promotion_decision = "STOP_NO_PROMOTION_ZERO_DENSITY"
    elif quarantined:
        promotion_decision = "HOLD_NO_PROMOTION_QUARANTINED"
    else:
        promotion_decision = (
            "RECOMMEND_SEPARATE_BOUNDED_RAW_HISTORICAL_AUTHORITY"
        )
    report_state = promotion_decision
    duplicate_count = int(checkpoint.get("exact_duplicate_items", 0))
    checkpoint_cas_evidence: dict[str, Any] = {
        "etag_present": bool(checkpoint_token),
        "version_id_present": False,
        "server_side_encryption": "NOT_AVAILABLE_FOR_INJECTED_STORE",
        "write_precondition": "CAS_STORE_OPAQUE_TOKEN",
    }
    if checkpoint_token:
        try:
            token_value = json.loads(checkpoint_token)
        except (TypeError, json.JSONDecodeError):
            token_value = None
        if isinstance(token_value, dict) and set(token_value) == {
            "etag", "version_id", "sse"
        }:
            checkpoint_cas_evidence = {
                "etag_present": bool(token_value["etag"]),
                "version_id_present": bool(token_value["version_id"]),
                "server_side_encryption": token_value["sse"],
                "write_precondition": "IF_NONE_MATCH_OR_IF_MATCH_ETAG",
            }
    event_pairs = []
    for pair_key, count in sorted(
        checkpoint.get("event_code_name_counts", {}).items()
    ):
        try:
            pair = json.loads(pair_key)
        except (TypeError, json.JSONDecodeError):
            pair = {"code": "<INVALID>", "name": "<INVALID>"}
        event_pairs.append(
            {"code": pair["code"], "name": pair["name"], "count": count}
        )
    return {
        "artifact": "M3TOP3_FINANCE_CA_COVERAGE_PILOT_v1.0",
        "artifact_class": "FINANCE_ONLY_BOUNDED_LIVE_PILOT_RESULT",
        "state": report_state,
        "runtime_lock_id": RUNTIME_LOCK_ID,
        "pilot_run_id": PILOT_RUN_ID,
        "owner_cap_spec_sha256": OWNER_CAP_SPEC_SHA256,
        "completed_date_count": completed,
        "primary_date_count": len(PRIMARY_DATES),
        "dates_with_rows": data_dates,
        "valid_empty_dates": completed - data_dates,
        "data_density_ratio": data_dates / len(PRIMARY_DATES),
        "data_density": {
            "numerator_dates_with_rows": data_dates,
            "denominator_primary_dates": len(PRIMARY_DATES),
            "ratio": data_dates / len(PRIMARY_DATES),
        },
        "total_items": total_items,
        "page_count_by_date": {
            row["basDt"]: row["page_count"] for row in results
        },
        "bytes": {
            "raw_response_entity_bytes": checkpoint.get("raw_entity_bytes", 0),
            "canonical_raw_entities": len(checkpoint.get("raw_index", [])),
        },
        "event_code_counts_opaque": dict(checkpoint.get("event_code_counts", {})),
        "event_code_name_pairs_opaque": event_pairs,
        "date_echo": {
            "match_rows": checkpoint.get("date_echo_match_rows", 0),
            "mismatch_rows": 0,
        },
        "issuer_identity": {
            "rows_checked": checkpoint.get("issuer_identity_rows_checked", 0),
            "match_rows": checkpoint.get("issuer_identity_match_rows", 0),
            "conflicts": issuer_conflicts,
            "missing_rows": checkpoint.get("issuer_identity_missing_rows", 0),
        },
        "external_u127_identity_match": {
            "state": "NOT_EVALUATED",
            "reason": "EXTERNAL_U127_DATA_NOT_ACQUIRED_IN_FINANCE_ONLY_PILOT",
        },
        "duplicates": {
            "exact_duplicate_items": duplicate_count,
            "ratio_numerator": duplicate_count,
            "ratio_denominator": total_items,
            "ratio": duplicate_count / total_items if total_items else 0.0,
        },
        "quota": {
            "quota_day_kst": PILOT_QUOTA_DAY_KST,
            "github_run_attempts_observed": list(
                checkpoint.get("observed_github_run_attempts", [])
            ),
            "pre_pilot_finance_ordinal": PILOT_FINANCE_ORDINAL_BASE,
            "historical_baseline_quota_day_kst": HISTORICAL_BASELINE_QUOTA_DAY_KST,
            "historical_baseline_finance_last_ordinal": HISTORICAL_BASELINE_FINANCE_LAST_ORDINAL,
            "pilot_reservations": checkpoint.get("quota_reservations", 0),
            "provider_finance_last_ordinal": PILOT_FINANCE_ORDINAL_BASE
            + int(checkpoint.get("quota_reservations", 0)),
            "network_attempts_started_conservative": checkpoint.get(
                "network_attempts_started_conservative", 0
            ),
            "response_entities_received": checkpoint.get(
                "response_entities_received", 0
            ),
            "no_entity_attempts": checkpoint.get("no_entity_attempts", 0),
            "maximum_pilot_attempts": MAX_NETWORK_ATTEMPTS_TOTAL,
        },
        "http_status_counts": dict(checkpoint.get("http_status_counts", {})),
        "raw_index": list(checkpoint.get("raw_index", [])),
        "checkpoint_token_sha256": (
            hashlib.sha256(checkpoint_token.encode("utf-8")).hexdigest()
            if checkpoint_token else None
        ),
        "checkpoint_cas_evidence": checkpoint_cas_evidence,
        "last_error_class": checkpoint.get("last_error_class"),
        "fallback_dates_used": [],
        "full_date_range_expansion": False,
        "historical_2019_canary_expansion": False,
        "normalization_records_created": 0,
        "automatic_promotion_performed": False,
        "historical_acquisition_promotion": {
            "decision": promotion_decision,
            "predicate": {
                "checkpoint_complete": complete_exact,
                "all_primary_dates_completed": completed == len(PRIMARY_DATES),
                "dates_with_rows_greater_than_zero": data_dates > 0,
                "issuer_identity_conflicts_equal_zero": issuer_conflicts == 0,
                "quarantine_triggered": quarantined,
                "recommendation_prerequisites_met": (
                    complete_exact and data_dates > 0 and not quarantined
                ),
                "separate_owner_authorization_required": True,
                "historical_acquisition_authorized": False,
            },
            "automatic_promotion_performed": False,
        },
        "bulk_acquisition_authorized": False,
        "model_semantic_change_authorized": False,
        "pit_semantic_change_authorized": False,
        "validation_claim": "NONE",
        "gate_effect": "NONE",
    }


def run_finance_live_pilot(
    spec: LivePilotSpec,
    bindings: ExecutionBindings,
    *,
    transport: FinanceTransport,
    custody: RawCustodyStore,
    claim_store: ExecutionClaimStore,
    checkpoint_store: DurableCheckpointStore,
    writer_id: str,
    secrets: tuple[str, ...],
    clock: Callable[[], datetime] = _utc_now,
    sleep_fn: Callable[[float], None] = time.sleep,
) -> dict[str, Any]:
    """Execute the frozen 17-date pilot; tests inject every side-effect adapter."""
    _validate_spec(spec)
    _quota_day_kst(clock)
    claim = _execution_claim_material(bindings, writer_id)
    claim_evidence = claim_store.acquire_execution_claim(claim)
    expected_claim_sha = hashlib.sha256(sa.canonical_json_bytes(claim)).hexdigest()
    if (
        not isinstance(claim_evidence, ExecutionClaimEvidence)
        or claim_evidence.object_key != execution_claim_object_key()
        or claim_evidence.content_sha256 != expected_claim_sha
        or not claim_evidence.version_id
        or not claim_evidence.etag
        or claim_evidence.server_side_encryption != "AES256"
        or claim_evidence.write_precondition != "IF_NONE_MATCH_STAR"
        or claim_evidence.writer_id != writer_id
    ):
        raise sa.CheckpointConflictError(
            "Finance single-writer execution claim evidence mismatch"
        )
    loaded, token = checkpoint_store.load()
    if loaded is None:
        checkpoint = _initial_checkpoint(
            spec, bindings, claim_evidence, clock=clock
        )
        token = checkpoint_store.compare_and_swap(checkpoint, None)
    else:
        checkpoint = json.loads(json.dumps(loaded))
    _assert_checkpoint_binding(checkpoint, spec, bindings, claim_evidence)
    if checkpoint["state"] == "COMPLETE":
        return _build_report(checkpoint, token)
    if checkpoint["state"] == "BLOCKED":
        raise LivePilotError("durable Finance checkpoint is blocked")

    def save() -> None:
        nonlocal token
        checkpoint["checkpoint_revision"] += 1
        checkpoint["updated_at_utc"] = _iso_utc(clock)
        sa.assert_no_secret(sa.canonical_json_bytes(checkpoint), secrets)
        token = checkpoint_store.compare_and_swap(checkpoint, token)

    def reserve(bas_dt: str, page_no: int) -> dict[str, Any]:
        quota_day_kst = _quota_day_kst(clock)
        if page_no < 1 or page_no > MAX_PAGES_PER_DATE:
            raise sa.QuotaBoundaryError("Finance page number outside pilot ceiling")
        prior = _attempts_for(checkpoint, bas_dt, page_no)
        if len(prior) >= MAX_ATTEMPTS_PER_PAGE:
            raise sa.QuotaBoundaryError("Finance per-page attempt ceiling reached")
        if checkpoint["quota_reservations"] >= MAX_NETWORK_ATTEMPTS_TOTAL:
            raise sa.QuotaBoundaryError("Finance live-pilot attempt ceiling reached")
        slot = f"{bas_dt}:{page_no}"
        if slot not in checkpoint["unique_page_slots"]:
            if len(checkpoint["unique_page_slots"]) >= MAX_PRIMARY_PAGE_SLOTS:
                raise sa.QuotaBoundaryError("Finance primary page-slot ceiling reached")
            checkpoint["unique_page_slots"].append(slot)
        attempt_no = len(prior) + 1
        request_id = deterministic_request_id(bas_dt, page_no)
        raw_object_prefix = deterministic_raw_object_prefix(
            bas_dt, page_no, attempt_no, quota_day_kst
        )
        record = {
            "basDt": bas_dt,
            "page_no": page_no,
            "attempt": attempt_no,
            "request_id": request_id,
            "quota_day_kst": quota_day_kst,
            "raw_object_prefix": raw_object_prefix,
            "provider_quota_ordinal": (
                PILOT_FINANCE_ORDINAL_BASE
                + checkpoint["quota_reservations"]
                + 1
            ),
            "github_run_id": bindings.github_run_id,
            "run_attempt": bindings.github_run_attempt,
            "state": "RESERVED_WRITE_AHEAD",
            "reserved_at_utc": _iso_utc(clock),
            "response_entity_received": False,
        }
        checkpoint["attempts"].append(record)
        if bindings.github_run_attempt not in checkpoint["observed_github_run_attempts"]:
            checkpoint["observed_github_run_attempts"].append(
                bindings.github_run_attempt
            )
        checkpoint["quota_reservations"] += 1
        # A crash after this CAS may be indistinguishable from a started request.
        checkpoint["network_attempts_started_conservative"] += 1
        save()
        return record

    def persist_sealed(
        attempt: dict[str, Any], sealed: SealedEntity, *, reconciled: bool
    ) -> None:
        canonical_key = canonical_raw_object_key(
            attempt["raw_object_prefix"], sealed.entity_sha256
        )
        if (
            sealed.object_key != canonical_key
            or sealed.entity_sha256 != sealed.readback_sha256
            or sealed.entity_bytes != sealed.readback_bytes
            or sealed.server_side_encryption != "AES256"
            or not sealed.version_id
            or not sealed.etag
            or sealed.write_precondition != "IF_NONE_MATCH_STAR"
            or sealed.storage_locator
            != f"s3://semi-data-plane-aofspds-20260815/{canonical_key}"
        ):
            raise RemoteCustodyError("Finance raw custody invariant mismatch")
        attempt["object_key"] = canonical_key
        record = _raw_record(attempt, sealed, reconciled=reconciled)
        if not any(
            row["s3_object_key"] == sealed.object_key
            for row in checkpoint["raw_index"]
        ):
            checkpoint["raw_index"].append(record)
            checkpoint["remote_raw_custody_writes_or_reconciliations"] += 1
            checkpoint["raw_entity_bytes"] += sealed.entity_bytes
            checkpoint["response_entities_received"] += 1
            status_key = str(sealed.http_status)
            checkpoint["http_status_counts"][status_key] = (
                checkpoint["http_status_counts"].get(status_key, 0) + 1
            )
        attempt.update(
            {
                "state": "RAW_SEALED_BEFORE_PARSE",
                "response_entity_received": True,
                "http_status": sealed.http_status,
                "entity_sha256": sealed.entity_sha256,
                "entity_bytes": sealed.entity_bytes,
                "s3_version_id": sealed.version_id,
                "s3_etag": sealed.etag,
                "reconciled_after_custody_before_checkpoint_gap": reconciled,
            }
        )
        save()

    def acquire_page(
        bas_dt: str, page_no: int, *, allow_parsed_reuse: bool = True
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        while True:
            prior = _attempts_for(checkpoint, bas_dt, page_no)
            latest = prior[-1] if prior else None
            sealed: SealedEntity | None = None
            if latest and latest["state"] in {
                "NONRETRYABLE_HTTP_ENTITY_CUSTODIED",
                "PARSE_OR_PROTOCOL_BLOCKED_AFTER_CUSTODY",
                "RETURNED_PAGE_SIZE_MISMATCH",
            }:
                if latest["state"] == "NONRETRYABLE_HTTP_ENTITY_CUSTODIED":
                    raise sa.SourceTransportError(
                        "Finance terminal HTTP entity was already custodied"
                    )
                raise sa.SourceProtocolError(
                    "Finance terminal protocol failure was already custodied"
                )
            if (
                latest
                and latest["state"] == "RETRYABLE_HTTP_ENTITY_CUSTODIED"
                and latest["attempt"] >= MAX_ATTEMPTS_PER_PAGE
            ):
                raise sa.SourceTransportError(
                    "Finance retryable HTTP status exhausted page attempts"
                )
            if (
                latest
                and latest["state"] in {
                    "NO_RESPONSE_ENTITY_RESERVATION_SPENT",
                    "RESERVATION_SPENT_NO_REMOTE_ENTITY_ON_RESUME",
                }
                and latest["attempt"] >= MAX_ATTEMPTS_PER_PAGE
            ):
                raise NoEntityTransportError(
                    "Finance no-entity attempts exhausted page attempts"
                )
            if latest and latest["state"] == "RESERVED_WRITE_AHEAD":
                sealed = custody.find_existing_by_prefix(
                    latest["raw_object_prefix"]
                )
                if sealed is None:
                    latest["state"] = "RESERVATION_SPENT_NO_REMOTE_ENTITY_ON_RESUME"
                    checkpoint["no_entity_attempts"] += 1
                    save()
                else:
                    sa.assert_no_secret(sealed.body, secrets)
                    persist_sealed(latest, sealed, reconciled=True)
            elif latest and latest["state"] in {
                "RAW_SEALED_BEFORE_PARSE", "PARSED_200"
            }:
                if latest["state"] != "PARSED_200" or allow_parsed_reuse:
                    sealed = custody.read_existing(
                        latest["object_key"], latest["s3_version_id"]
                    )
                    if sealed is None:
                        raise RemoteCustodyError(
                            "checkpoint references missing raw entity"
                        )
                    if (
                        sealed.entity_sha256 != latest.get("entity_sha256")
                        or sealed.version_id != latest.get("s3_version_id")
                        or sealed.http_status != latest.get("http_status")
                    ):
                        raise RemoteCustodyError(
                            "checkpoint raw entity readback shifted"
                        )
                    sa.assert_no_secret(sealed.body, secrets)

            if sealed is None:
                attempt = reserve(bas_dt, page_no)
                # Close the write-ahead-CAS/midnight TOCTOU window. The
                # reservation remains durably spent, but no provider request
                # may begin on a different KST quota day.
                _quota_day_kst(clock)
                params = sa.finance_request_params(
                    bas_dt, page_no, REQUEST_PAGE_SIZE
                )
                try:
                    response = transport.fetch_once(params)
                except NoEntityTransportError:
                    attempt["state"] = "NO_RESPONSE_ENTITY_RESERVATION_SPENT"
                    checkpoint["no_entity_attempts"] += 1
                    save()
                    if attempt["attempt"] >= MAX_ATTEMPTS_PER_PAGE:
                        raise
                    sleep_fn(0.0)
                    continue
                if (
                    not isinstance(response, TransportResponse)
                    or not isinstance(response.body, bytes)
                    or type(response.http_status) is not int
                ):
                    raise LivePilotError("Finance transport returned invalid response")
                sa.assert_no_secret(response.body, secrets)
                digest = hashlib.sha256(response.body).hexdigest()
                object_key = canonical_raw_object_key(
                    attempt["raw_object_prefix"], digest
                )
                metadata = {
                    "sha256": digest,
                    "http-status": str(response.http_status),
                    "acquired-at-utc": response.acquired_at_utc,
                    "request-id": attempt["request_id"],
                    "bas-dt": bas_dt,
                    "page-no": str(page_no),
                    "attempt": str(attempt["attempt"]),
                    "runtime-lock-id": RUNTIME_LOCK_ID,
                    "pilot-run-id": PILOT_RUN_ID,
                    "quota-day-kst": attempt["quota_day_kst"],
                }
                sealed = custody.seal_and_readback(
                    object_key, response.body, metadata
                )
                persist_sealed(attempt, sealed, reconciled=False)
                latest = attempt

            assert latest is not None and sealed is not None
            status = sealed.http_status
            if status == 429 or 500 <= status <= 599:
                latest["state"] = "RETRYABLE_HTTP_ENTITY_CUSTODIED"
                save()
                if latest["attempt"] >= MAX_ATTEMPTS_PER_PAGE:
                    raise sa.SourceTransportError(
                        "Finance retryable HTTP status exhausted page attempts"
                    )
                sleep_fn(0.0)
                continue
            if status != 200:
                latest["state"] = "NONRETRYABLE_HTTP_ENTITY_CUSTODIED"
                save()
                raise sa.SourceTransportError(
                    "Finance non-success HTTP entity custodied"
                )
            try:
                page = sa.finance_entity_to_page(
                    sealed.body,
                    expected_bas_dt=bas_dt,
                    expected_page_no=page_no,
                )
            except Exception:
                latest["state"] = "PARSE_OR_PROTOCOL_BLOCKED_AFTER_CUSTODY"
                save()
                raise
            if page["page_size"] != REQUEST_PAGE_SIZE:
                latest["state"] = "RETURNED_PAGE_SIZE_MISMATCH"
                save()
                raise sa.SourceProtocolError(
                    "Finance returned page size differs from request"
                )
            latest["state"] = "PARSED_200"
            save()
            return page, latest

    try:
        while checkpoint["next_date_index"] < len(PRIMARY_DATES):
            bas_dt = PRIMARY_DATES[checkpoint["next_date_index"]]
            current = checkpoint.get("current_date")
            if current is None:
                current = {
                    "basDt": bas_dt,
                    "state": "IN_PROGRESS",
                    "page_1_identity": None,
                    "total_count": None,
                    "page_size": None,
                    "expected_pages": None,
                    "validated_pages": [],
                    "page_fingerprints": [],
                    "cumulative_item_count": 0,
                    "resume_page_1_revalidations": 0,
                }
                checkpoint["current_date"] = current
                save()
            elif current.get("basDt") != bas_dt:
                raise sa.CheckpointConflictError(
                    "current Finance date is not ordered next"
                )

            if current["validated_pages"]:
                page_one_attempts = _attempts_for(checkpoint, bas_dt, 1)
                latest_page_one = page_one_attempts[-1] if page_one_attempts else None
                validated_page_one = current["validated_pages"][0]
                uncommitted_revalidation = bool(
                    latest_page_one
                    and latest_page_one.get("state") == "PARSED_200"
                    and (
                        latest_page_one.get("entity_sha256")
                        != validated_page_one.get("entity_sha256")
                        or latest_page_one.get("s3_version_id")
                        != validated_page_one.get("s3_version_id")
                    )
                )
                reuse_revalidation = (
                    current.get("resume_page_1_revalidations", 0) > 0
                    or uncommitted_revalidation
                )
                page_one, _ = acquire_page(
                    bas_dt, 1, allow_parsed_reuse=reuse_revalidation
                )
                if (
                    sa.pagination_page_1_identity(page_one)
                    != current["page_1_identity"]
                ):
                    raise sa.SourceProtocolError(
                        "Finance resume page-1 identity shifted"
                    )
                if current["resume_page_1_revalidations"] == 0:
                    current["resume_page_1_revalidations"] = 1
                save()
            else:
                page_one, attempt = acquire_page(bas_dt, 1)
                total = page_one["total_count"]
                expected_pages = max(1, math.ceil(total / REQUEST_PAGE_SIZE))
                if expected_pages > MAX_PAGES_PER_DATE:
                    raise sa.QuotaBoundaryError(
                        "Finance pagination page ceiling exceeded"
                    )
                fingerprint = hashlib.sha256(
                    sa.canonical_json_bytes(page_one["items"])
                ).hexdigest()
                count = len(page_one["items"])
                if count > REQUEST_PAGE_SIZE or count > total:
                    raise sa.SourceProtocolError(
                        "Finance page-1 item count invalid"
                    )
                if not page_one["items"] and count < total:
                    raise sa.SourceProtocolError(
                        "Finance empty intermediate page"
                    )
                current.update(
                    {
                        "page_1_identity": sa.pagination_page_1_identity(
                            page_one
                        ),
                        "total_count": total,
                        "page_size": REQUEST_PAGE_SIZE,
                        "expected_pages": expected_pages,
                        "page_fingerprints": (
                            [fingerprint] if page_one["items"] else []
                        ),
                        "cumulative_item_count": count,
                    }
                )
                current["validated_pages"].append(
                    {
                        "page_no": 1,
                        "item_count": count,
                        "cumulative_item_count": count,
                        "page_fingerprint_sha256": fingerprint,
                        "entity_sha256": attempt["entity_sha256"],
                        "s3_version_id": attempt["s3_version_id"],
                    }
                )
                _observe_items(checkpoint, page_one["items"])
                save()

            next_page = len(current["validated_pages"]) + 1
            while next_page <= current["expected_pages"]:
                page, attempt = acquire_page(bas_dt, next_page)
                if (
                    page["total_count"] != current["total_count"]
                    or page["page_size"] != current["page_size"]
                ):
                    raise sa.SourceProtocolError(
                        "Finance pagination snapshot shifted"
                    )
                items = page["items"]
                fingerprint = hashlib.sha256(
                    sa.canonical_json_bytes(items)
                ).hexdigest()
                if items and fingerprint in current["page_fingerprints"]:
                    raise sa.SourceProtocolError("Finance repeated whole page")
                cumulative = current["cumulative_item_count"] + len(items)
                if (
                    len(items) > REQUEST_PAGE_SIZE
                    or cumulative > current["total_count"]
                ):
                    raise sa.SourceProtocolError(
                        "Finance pagination item count exceeded"
                    )
                if not items and cumulative < current["total_count"]:
                    raise sa.SourceProtocolError(
                        "Finance empty intermediate page"
                    )
                if items:
                    current["page_fingerprints"].append(fingerprint)
                current["cumulative_item_count"] = cumulative
                current["validated_pages"].append(
                    {
                        "page_no": next_page,
                        "item_count": len(items),
                        "cumulative_item_count": cumulative,
                        "page_fingerprint_sha256": fingerprint,
                        "entity_sha256": attempt["entity_sha256"],
                        "s3_version_id": attempt["s3_version_id"],
                    }
                )
                _observe_items(checkpoint, items)
                save()
                next_page += 1

            if current["cumulative_item_count"] != current["total_count"]:
                raise sa.SourceProtocolError(
                    "Finance pagination totalCount did not close"
                )
            result = {
                "basDt": bas_dt,
                "state": "DATE_COMPLETE",
                "page_count": len(current["validated_pages"]),
                "item_count": current["cumulative_item_count"],
                "total_count": current["total_count"],
                "page_1_identity": current["page_1_identity"],
                "resume_page_1_revalidations": (
                    current["resume_page_1_revalidations"]
                ),
                "valid_empty": current["total_count"] == 0,
            }
            checkpoint["date_results"].append(result)
            checkpoint["completed_dates"].append(bas_dt)
            checkpoint["next_date_index"] += 1
            checkpoint["current_date"] = None
            save()

        checkpoint["state"] = "COMPLETE"
        checkpoint["last_error_class"] = None
        save()
        return _build_report(checkpoint, token)
    except sa.CheckpointConflictError:
        raise
    except RemoteCustodyError:
        # Remote custody/control-plane availability failures are resumable;
        # the last durable checkpoint remains authoritative and unblocked.
        raise
    except Exception as exc:
        checkpoint["state"] = "BLOCKED"
        checkpoint["last_error_class"] = type(exc).__name__
        try:
            save()
        except sa.CheckpointConflictError:
            raise
        raise


def _atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = path.with_name(f".{path.name}.lock")
    lock_fd = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o600)
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX)
        temp = path.with_name(f".{path.name}.{os.getpid()}.{time.time_ns()}.tmp")
        try:
            with temp.open("xb") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp, path)
            directory_fd = os.open(path.parent, os.O_RDONLY)
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
        finally:
            temp.unlink(missing_ok=True)
    finally:
        fcntl.flock(lock_fd, fcntl.LOCK_UN)
        os.close(lock_fd)


def _read_jsonl_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    try:
        for line in path.read_bytes().splitlines():
            if not line:
                continue
            value = json.loads(line, object_pairs_hook=_reject_duplicate_pairs)
            if not isinstance(value, dict):
                raise ValueError
            rows.append(value)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError):
        raise LivePilotError(f"invalid JSONL mirror: {path.name}") from None
    return rows


def _governed_baseline_jsonl_bytes(path: Path) -> bytes:
    try:
        raw = path.read_bytes()
        governed: list[bytes] = []
        pilot_rows_started = False
        for line_with_ending in raw.splitlines(keepends=True):
            line = line_with_ending.rstrip(b"\r\n")
            if not line:
                if not pilot_rows_started:
                    governed.append(line_with_ending)
                continue
            value = json.loads(
                line, object_pairs_hook=_reject_duplicate_pairs
            )
            if not isinstance(value, dict):
                raise ValueError
            if "pilot_run_id" in value:
                pilot_rows_started = True
            else:
                if pilot_rows_started:
                    raise ValueError(
                        "governed baseline row follows pilot mirror row"
                    )
                governed.append(line_with_ending)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError):
        raise LivePilotError(f"invalid JSONL mirror: {path.name}") from None
    return b"".join(governed)


def _governed_baseline_jsonl_sha256(path: Path) -> str:
    return hashlib.sha256(_governed_baseline_jsonl_bytes(path)).hexdigest()


def _write_jsonl(path: Path, rows: list[Mapping[str, Any]]) -> None:
    _atomic_write(
        path, b"".join(sa.canonical_json_bytes(dict(row)) for row in rows)
    )


def _quota_rows_from_checkpoint(
    baseline_rows: list[dict[str, Any]], checkpoint: Mapping[str, Any]
) -> list[Mapping[str, Any]]:
    rows: list[Mapping[str, Any]] = list(baseline_rows)
    for attempt in checkpoint.get("attempts", []):
        rows.append(
            {
                "event": "QUOTA_SLOT_SPENT",
                "provider": "FINANCE",
                "operation": sa.FINANCE_OPERATION,
                "pilot_run_id": PILOT_RUN_ID,
                "runtime_lock_id": RUNTIME_LOCK_ID,
                "run_id": attempt["github_run_id"],
                "run_attempt": attempt["run_attempt"],
                "basDt": attempt["basDt"],
                "page_no": attempt["page_no"],
                "attempt": attempt["attempt"],
                "request_id": attempt["request_id"],
                "ordinal": attempt["provider_quota_ordinal"],
                "quota_day_kst": attempt["quota_day_kst"],
                "reserved_at_utc": attempt["reserved_at_utc"],
                "response_entity_received": attempt.get(
                    "response_entity_received", False
                ),
                "outcome": attempt["state"],
                "automatic_retry": attempt["attempt"] > 1,
                "known_external_attempts_minimum": 0,
                "unknown_external_attempts": True,
            }
        )
    return rows


def _main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Finance-only bounded live pilot"
    )
    parser.add_argument("--authority", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--latch", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--quota-ledger", type=Path, required=True)
    parser.add_argument("--raw-index", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args(argv)

    spec, bindings = validate_cli_materials(
        authority_path=args.authority,
        plan_path=args.plan,
        latch_path=args.latch,
        checkpoint_path=args.checkpoint,
    )
    baseline_sha, baseline_quota_rows = _read_baseline_quota_ledger(
        args.quota_ledger
    )
    if baseline_sha != bindings.baseline_quota_ledger_sha256:
        raise AuthorityBindingError("governed baseline quota ledger hash mismatch")
    baseline_quota_bytes = _governed_baseline_jsonl_bytes(args.quota_ledger)
    baseline_raw_rows = [
        row for row in _read_jsonl_rows(args.raw_index)
        if row.get("pilot_run_id") != PILOT_RUN_ID
    ]
    baseline_raw_sha = _governed_baseline_jsonl_sha256(args.raw_index)
    if baseline_raw_sha != bindings.baseline_raw_index_sha256:
        raise AuthorityBindingError("governed baseline raw index hash mismatch")
    baseline_raw_bytes = _governed_baseline_jsonl_bytes(args.raw_index)
    secret = sa.validate_decoded_secret(
        FINANCE_SECRET_ENV, os.environ.get(FINANCE_SECRET_ENV)
    )
    writer_id = f"github-run:{bindings.github_run_id}"
    store = S3CliObjectStore()
    transport = UrlLibFinanceTransport(secret)
    try:
        report = run_finance_live_pilot(
            spec,
            bindings,
            transport=transport,
            custody=store,
            claim_store=store,
            checkpoint_store=store,
            writer_id=writer_id,
            secrets=(secret,),
        )
        exit_code = 0
    except Exception:
        checkpoint, checkpoint_token = store.load()
        if checkpoint is None:
            raise
        report = _build_report(checkpoint, checkpoint_token)
        exit_code = 2

    checkpoint, _ = store.load()
    if checkpoint is None:
        raise RemoteCustodyError(
            "remote checkpoint missing after Finance execution"
        )
    _atomic_write(args.checkpoint, sa.canonical_json_bytes(checkpoint))
    _atomic_write(
        args.raw_index,
        baseline_raw_bytes
        + b"".join(
            sa.canonical_json_bytes(row)
            for row in checkpoint.get("raw_index", [])
        ),
    )
    pilot_quota_rows = _quota_rows_from_checkpoint([], checkpoint)
    _atomic_write(
        args.quota_ledger,
        baseline_quota_bytes
        + b"".join(sa.canonical_json_bytes(row) for row in pilot_quota_rows),
    )
    _atomic_write(args.report, sa.canonical_json_bytes(report))
    return exit_code


def main() -> int:
    try:
        return _main()
    except sa.AdmissionError as exc:
        print(f"FINANCE_LIVE_PILOT_BLOCKED: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
