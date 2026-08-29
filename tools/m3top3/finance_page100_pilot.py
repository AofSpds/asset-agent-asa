#!/usr/bin/env python3
"""Successor-only Finance page-100 pilot.

This module intentionally leaves ``finance_live_pilot.py`` untouched.  It
imports the predecessor's durable evidence read-only, starts a new checkpoint
and raw-object namespace, and never treats predecessor attempts as new quota
spend.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import tempfile
import time
import subprocess
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Protocol, Sequence

from . import finance_live_pilot as legacy
from . import source_admission as sa


RUNTIME_LOCK_ID = "PMO-FINANCE-PAGE100-G6-20260829221500"
PILOT_RUN_ID = "FINANCE-PAGE100-PILOT-G6-20260829221500"
ACTIVATION_BASE_HEAD_COMMIT = "ee7cd5f6f48c9f13ad43071b8c7c3648c9bdd1d0"
EXECUTION_TOKEN_SHA256 = "3ecb5ad567e05208d76e892164d91d4a408d9ca50ab775c43c0ea294905c3c1d"
GENERATION_ID = "FINANCE-PAGE100-G6-20260829221500"
PRECHECK_ACT_ID = "FINANCE-PAGE100-PRECHECK-ACT-G6-20260829221500"
LATCH_EVENT_ID = "FINANCE-PAGE100-LATCH-G6-20260829221500"
FAILED_PRECHECK_WORKFLOW_RUN_ID = 33253477005
FAILED_PRECHECK_WORKFLOW_JOB_ID = 99103056660
FAILED_PRECHECK_HEAD_SHA = "ee7cd5f6f48c9f13ad43071b8c7c3648c9bdd1d0"
FAILED_PRECHECK_RERUN_AUTHORIZED = False
LIVE_ACT_ID = "FINANCE-PAGE100-LIVE-ACT-G6-20260829221500"
G4_PRECHECK_WORKFLOW_RUN_ID = 33225643741
G4_PRECHECK_HEAD_SHA = "784e9eea008b5eea57132e2e341a3c63982951cc"
MAX_SESSION_RECEIPT_SHA256 = "40a4385a25cb773bd0547669bd1fc7b0560e328f062545f8b4bcea2c7916c342"
LIVE_NOT_AFTER_UTC = datetime.fromisoformat("2026-08-30T14:30:00+00:00")

PRIMARY_DATES = legacy.PRIMARY_DATES
REQUEST_PAGE_SIZE = 10
MAX_PAGES_PER_DATE = 100
MAX_PRIMARY_PAGE_SLOTS = 1700
MAX_NETWORK_ATTEMPTS_TOTAL = 2000
MAX_ATTEMPTS_PER_PAGE = 2
MAX_FRESH_PREDECESSOR_PAGE1_REVALIDATIONS = 1

PREDECESSOR_RUNTIME_LOCK_ID = "PMO-API-SRC-ADMIT-20260828192737"
PREDECESSOR_PILOT_RUN_ID = "FINANCE-LIVE-PILOT-20260828192737"
PREDECESSOR_WORKFLOW_RUN_ID = 33195472310
PREDECESSOR_CHECKPOINT_SHA256 = (
    "9a18edaf66b9f03b2202dbef11c0f86472340695c0c245f0a8ca958e3cfce55d"
)
PREDECESSOR_REPORT_SHA256 = (
    "78c4e659f02b0a206129474219db681b50756e58f2492dbe4c1a689733fa6b2a"
)
PREDECESSOR_PAGE1_SHA256 = (
    "2e97f391bcf833db568de2c8638c5ff6d297ea07be21efc3fca6d05cd266c309"
)
PREDECESSOR_PAGE1_VERSION_ID = "avNHRa6z6kooy0MEG0rB3H2Ify2dWSjq"
PREDECESSOR_PAGE1_BYTES = 4642
PREDECESSOR_PAGE1_KEY = (
    "raw/public-data-api/M3TOP3-FINANCE-STOCK-RIGHTS-v1/"
    "getRighExerReasSche_V2/quota_day_kst=2026-08-29/"
    "request_id=2336abe1c81d4c86f90fef6575e204d0455367d4d5e8ed6cce103a752f0330da/"
    "attempt=1/sha256=" + PREDECESSOR_PAGE1_SHA256 + ".entity"
)

RAW_PREFIX = legacy.RAW_PREFIX
RAW_KEY_PREFIX = "raw/public-data-api/M3TOP3-FINANCE-STOCK-RIGHTS-v1/"
_SHA256_RE = re.compile(r"[0-9a-f]{64}")
_SAFE_ID_RE = re.compile(r"[A-Z0-9][A-Z0-9-]{7,127}")


class Page100PilotError(sa.AdmissionError):
    """Sanitized successor-pilot failure."""


class BindingError(Page100PilotError):
    pass


class HistoricalEvidenceError(Page100PilotError):
    pass


class RemoteCustodyError(Page100PilotError):
    pass


class PageCeilingError(sa.QuotaBoundaryError):
    def __init__(self, telemetry: Mapping[str, Any]):
        super().__init__("Finance pagination page ceiling exceeded")
        self.telemetry = dict(telemetry)


class IssuerIdentityConflictError(sa.SourceProtocolError):
    """A Finance issuer key mapped to more than one stable identity."""


class SelfDeadlineExceededError(sa.QuotaBoundaryError):
    """The runner stopped early enough to persist terminal evidence."""


TransportResponse = legacy.TransportResponse
SealedEntity = legacy.SealedEntity
ExecutionClaimEvidence = legacy.ExecutionClaimEvidence
NoEntityTransportError = legacy.NoEntityTransportError


@dataclass(frozen=True)
class SuccessorSealedEntity(legacy.SealedEntity):
    response_received_at_utc: str


def _with_response_timing(
    sealed: SealedEntity, response_received_at_utc: str
) -> SuccessorSealedEntity:
    return SuccessorSealedEntity(
        body=sealed.body,
        object_key=sealed.object_key,
        storage_locator=sealed.storage_locator,
        entity_sha256=sealed.entity_sha256,
        entity_bytes=sealed.entity_bytes,
        readback_sha256=sealed.readback_sha256,
        readback_bytes=sealed.readback_bytes,
        version_id=sealed.version_id,
        etag=sealed.etag,
        server_side_encryption=sealed.server_side_encryption,
        write_precondition=sealed.write_precondition,
        http_status=sealed.http_status,
        acquired_at_utc=sealed.acquired_at_utc,
        response_received_at_utc=response_received_at_utc,
    )


@dataclass(frozen=True)
class HistoricalPageOneBinding:
    object_key: str = PREDECESSOR_PAGE1_KEY
    version_id: str = PREDECESSOR_PAGE1_VERSION_ID
    entity_sha256: str = PREDECESSOR_PAGE1_SHA256
    entity_bytes: int = PREDECESSOR_PAGE1_BYTES
    server_side_encryption: str = "AES256"


@dataclass(frozen=True)
class PredecessorBinding:
    runtime_lock_id: str = PREDECESSOR_RUNTIME_LOCK_ID
    pilot_run_id: str = PREDECESSOR_PILOT_RUN_ID
    workflow_run_id: int = PREDECESSOR_WORKFLOW_RUN_ID
    checkpoint_sha256: str = PREDECESSOR_CHECKPOINT_SHA256
    report_sha256: str = PREDECESSOR_REPORT_SHA256
    raw_index_sha256: str = "c78f29fa90e7648df1ef1513df539d021b26aeac19e6b5cc3e701c90d5fcc9ad"
    quota_ledger_sha256: str = "b04e0d5434dff371ece950b568b545076a1833db078a5e40f85ebf704a436c49"
    page_one: HistoricalPageOneBinding = HistoricalPageOneBinding()


@dataclass(frozen=True)
class SuccessorBindings:
    runtime_lock_id: str = RUNTIME_LOCK_ID
    pilot_run_id: str = PILOT_RUN_ID
    quota_day_kst: str = "2026-08-30"
    finance_ordinal_base: int = 0
    github_run_id: int = 1
    github_run_attempt: int = 1
    predecessor: PredecessorBinding = PredecessorBinding()


@dataclass(frozen=True)
class Page100Spec:
    ordered_dates: tuple[str, ...] = PRIMARY_DATES
    request_page_size: int = REQUEST_PAGE_SIZE
    max_pages_per_date: int = MAX_PAGES_PER_DATE
    max_primary_page_slots: int = MAX_PRIMARY_PAGE_SLOTS
    max_network_attempts_total: int = MAX_NETWORK_ATTEMPTS_TOTAL
    max_attempts_per_page: int = MAX_ATTEMPTS_PER_PAGE


@dataclass(frozen=True)
class PredecessorBundle:
    checkpoint_bytes: bytes
    raw_index_bytes: bytes
    quota_ledger_bytes: bytes
    report_bytes: bytes | None = None


@dataclass(frozen=True)
class HistoricalSeed:
    completed_result: Mapping[str, Any]
    page_one: Mapping[str, Any]
    page_one_identity: str
    page_one_reference: Mapping[str, Any]
    inherited_attempts: tuple[Mapping[str, Any], ...]
    inherited_raw_index: tuple[Mapping[str, Any], ...]
    predecessor_checkpoint_sha256: str
    historical_page_cap_telemetry: Mapping[str, Any]
    telemetry: Mapping[str, Any]


class FinanceTransport(Protocol):
    def fetch_once(self, params: Mapping[str, str]) -> TransportResponse: ...


class Page100CustodyStore(Protocol):
    def read_historical(
        self, binding: HistoricalPageOneBinding
    ) -> SealedEntity | None: ...

    def read_existing(
        self, object_key: str, version_id: str | None = None
    ) -> SealedEntity | None: ...

    def find_existing_by_prefix(
        self, object_prefix: str, expected_lineage: Mapping[str, Any]
    ) -> SealedEntity | None: ...

    def seal_and_readback(
        self, object_key: str, body: bytes, metadata: Mapping[str, str]
    ) -> SealedEntity: ...


class DurableCheckpointStore(Protocol):
    def load(self) -> tuple[Mapping[str, Any] | None, str | None]: ...

    def compare_and_swap(
        self, value: Mapping[str, Any], expected_token: str | None
    ) -> str: ...


class ExecutionClaimStore(Protocol):
    def acquire_execution_claim(
        self, claim: Mapping[str, Any]
    ) -> ExecutionClaimEvidence: ...


def owner_cap_material() -> dict[str, Any]:
    return {
        "activation_base_head_commit": ACTIVATION_BASE_HEAD_COMMIT,
        "runtime_lock_id": RUNTIME_LOCK_ID,
        "pilot_run_id": PILOT_RUN_ID,
        "dates": list(PRIMARY_DATES),
        "request_page_size": REQUEST_PAGE_SIZE,
        "max_pages_per_date": MAX_PAGES_PER_DATE,
        "max_primary_page_acquisitions": MAX_PRIMARY_PAGE_SLOTS,
        "max_network_attempts_total": MAX_NETWORK_ATTEMPTS_TOTAL,
        "max_attempts_per_page": MAX_ATTEMPTS_PER_PAGE,
        "reused_completed_dates": ["20240102"],
        "reused_partial_pages": [{"basDt": "20240131", "page_no": 1}],
        "max_fresh_predecessor_page_1_revalidations": 1,
        "predecessor_workflow_run_id": PREDECESSOR_WORKFLOW_RUN_ID,
        "predecessor_rerun_authorized": False,
    }


OWNER_CAP_SPEC_SHA256 = hashlib.sha256(
    sa.canonical_json_bytes(owner_cap_material())
).hexdigest()


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _strict_json(data: bytes, label: str) -> dict[str, Any]:
    def pairs(values: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in values:
            if key in result:
                raise ValueError
            result[key] = value
        return result

    try:
        value = json.loads(data, object_pairs_hook=pairs)
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError):
        raise HistoricalEvidenceError(f"invalid predecessor {label}") from None
    if not isinstance(value, dict):
        raise HistoricalEvidenceError(f"invalid predecessor {label}")
    return value


def _jsonl_rows(data: bytes, label: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in data.splitlines():
        if line:
            rows.append(_strict_json(line, label))
    return rows


def _validate_spec(spec: Page100Spec) -> None:
    if spec != Page100Spec():
        raise BindingError("page-100 owner-cap binding mismatch")
    sa.validate_finance_pilot_dates(
        spec.ordered_dates, start_date="2024-01-01", end_date="2026-08-14"
    )


def _validate_bindings(bindings: SuccessorBindings) -> None:
    if (
        bindings.runtime_lock_id != RUNTIME_LOCK_ID
        or bindings.pilot_run_id != PILOT_RUN_ID
        or _SAFE_ID_RE.fullmatch(bindings.runtime_lock_id) is None
        or _SAFE_ID_RE.fullmatch(bindings.pilot_run_id) is None
        or bindings.predecessor.runtime_lock_id == bindings.runtime_lock_id
        or bindings.predecessor.pilot_run_id == bindings.pilot_run_id
        or bindings.github_run_id == bindings.predecessor.workflow_run_id
        or bindings.github_run_id < 1
        or bindings.github_run_attempt < 1
    ):
        raise BindingError("successor/predecessor execution identity mismatch")
    try:
        datetime.strptime(bindings.quota_day_kst, "%Y-%m-%d")
    except ValueError:
        raise BindingError("invalid successor quota day") from None
    expected_base = (
        9 if bindings.quota_day_kst == "2026-08-29" else 0
    )
    if bindings.finance_ordinal_base != expected_base:
        raise BindingError("successor Finance ordinal base mismatch")


def deterministic_request_id(bas_dt: str, page_no: int) -> str:
    params = sa.finance_request_params(bas_dt, page_no, REQUEST_PAGE_SIZE)
    return sa.canonical_request_id(
        sa.FINANCE_SOURCE_ID, sa.FINANCE_URL, sa.FINANCE_OPERATION, params
    )


def deterministic_raw_object_prefix(
    bindings: SuccessorBindings, bas_dt: str, page_no: int, attempt: int
) -> str:
    _validate_bindings(bindings)
    if not 1 <= page_no <= MAX_PAGES_PER_DATE:
        raise sa.QuotaBoundaryError("Finance page outside page-100 ceiling")
    if not 1 <= attempt <= MAX_ATTEMPTS_PER_PAGE:
        raise sa.QuotaBoundaryError("Finance attempt outside page ceiling")
    return (
        RAW_KEY_PREFIX
        + "_pilot_generation/"
        + f"runtime_lock_id={bindings.runtime_lock_id}/"
        + f"pilot_run_id={bindings.pilot_run_id}/"
        + f"{sa.FINANCE_OPERATION}/"
        + f"quota_day_kst={bindings.quota_day_kst}/"
        + f"request_id={deterministic_request_id(bas_dt, page_no)}/"
        + f"attempt={attempt}/"
    )


def canonical_raw_object_key(prefix: str, entity_sha256: str) -> str:
    if _SHA256_RE.fullmatch(entity_sha256) is None:
        raise RemoteCustodyError("invalid Finance entity digest")
    required_namespace = (
        RAW_KEY_PREFIX + "_pilot_generation/"
        + f"runtime_lock_id={RUNTIME_LOCK_ID}/pilot_run_id={PILOT_RUN_ID}/"
    )
    if not prefix.startswith(required_namespace):
        raise RemoteCustodyError("raw key lacks successor pilot namespace")
    return f"{prefix}sha256={entity_sha256}.entity"


def checkpoint_object_key(bindings: SuccessorBindings) -> str:
    _validate_bindings(bindings)
    return (
        RAW_KEY_PREFIX + "_pilot_control/"
        + f"runtime_lock_id={bindings.runtime_lock_id}/"
        + f"pilot_run_id={bindings.pilot_run_id}/checkpoint.json"
    )


def execution_claim_object_key(bindings: SuccessorBindings) -> str:
    _validate_bindings(bindings)
    return (
        RAW_KEY_PREFIX + "_writer_claims/"
        + f"quota_day_kst={bindings.quota_day_kst}/execution-claim.json"
    )


def pre_current_pilot_bytes(data: bytes, current_pilot_run_id: str) -> bytes:
    """Preserve every predecessor byte; remove only current-pilot tail rows."""
    preserved: list[bytes] = []
    current_started = False
    for raw_line in data.splitlines(keepends=True):
        line = raw_line.rstrip(b"\r\n")
        if not line:
            if not current_started:
                preserved.append(raw_line)
            continue
        row = _strict_json(line, "JSONL mirror")
        if row.get("pilot_run_id") == current_pilot_run_id:
            current_started = True
        elif current_started:
            raise BindingError("non-current row follows current-pilot mirror tail")
        else:
            preserved.append(raw_line)
    return b"".join(preserved)


def append_current_rows(
    existing: bytes, current_pilot_run_id: str, rows: Sequence[Mapping[str, Any]]
) -> bytes:
    prefix = pre_current_pilot_bytes(existing, current_pilot_run_id)
    return prefix + b"".join(sa.canonical_json_bytes(dict(row)) for row in rows)


def _page_cap_telemetry(
    bas_dt: str, total_count: int, *, historical_evidence: bool
) -> dict[str, Any]:
    expected_pages = max(1, math.ceil(total_count / REQUEST_PAGE_SIZE))
    return {
        "basDt": bas_dt,
        "total_count": total_count,
        "request_page_size": REQUEST_PAGE_SIZE,
        "expected_pages": expected_pages,
        "max_pages_per_date": MAX_PAGES_PER_DATE,
        "blocked_before_page_2": True,
        "historical_evidence": historical_evidence,
    }


def _provider_result_code(body: bytes) -> str:
    """Return an observed provider code; UNKNOWN means the entity was unreadable."""
    try:
        parsed = sa.parse_entity_bytes(body)
    except Exception:
        return "UNKNOWN"

    def find(value: Any) -> Any:
        if isinstance(value, Mapping):
            if "resultCode" in value:
                return value["resultCode"]
            for child in value.values():
                found = find(child)
                if found is not None:
                    return found
        elif isinstance(value, list):
            for child in value:
                found = find(child)
                if found is not None:
                    return found
        return None

    observed = find(parsed)
    if observed is None or observed == "":
        return "MISSING"
    return str(observed)


def _date_echo_observation(body: bytes, expected_bas_dt: str) -> tuple[int, int] | None:
    """Observe item date echoes without turning an unreadable entity into zeroes."""
    try:
        classified = sa.classify_provider("FINANCE", sa.parse_entity_bytes(body))
    except Exception:
        return None
    items = classified.get("items")
    if not isinstance(items, list):
        return None
    matches = 0
    mismatches = 0
    for item in items:
        if not isinstance(item, Mapping):
            mismatches += 1
        elif str(item.get("basDt") or "") == expected_bas_dt:
            matches += 1
        else:
            mismatches += 1
    return matches, mismatches


def _matching_predecessor_rows(
    rows: Sequence[Mapping[str, Any]], bas_dt: str, page_no: int
) -> list[Mapping[str, Any]]:
    return [
        row for row in rows
        if row.get("basDt") == bas_dt and row.get("page_no") == page_no
    ]


def load_historical_seed(
    bindings: SuccessorBindings,
    bundle: PredecessorBundle,
    custody: Page100CustodyStore,
    *,
    secrets: tuple[str, ...] = (),
) -> HistoricalSeed:
    """Validate and import only the Owner-authorized predecessor evidence."""
    _validate_bindings(bindings)
    predecessor = bindings.predecessor
    observed_hashes = {
        "checkpoint": _sha256(bundle.checkpoint_bytes),
        "raw index": _sha256(bundle.raw_index_bytes),
        "quota ledger": _sha256(bundle.quota_ledger_bytes),
    }
    expected_hashes = {
        "checkpoint": predecessor.checkpoint_sha256,
        "raw index": predecessor.raw_index_sha256,
        "quota ledger": predecessor.quota_ledger_sha256,
    }
    for label, expected in expected_hashes.items():
        if _SHA256_RE.fullmatch(expected) is None or observed_hashes[label] != expected:
            raise HistoricalEvidenceError(
                f"predecessor {label} exact hash mismatch"
            )

    checkpoint = _strict_json(bundle.checkpoint_bytes, "checkpoint")
    terminal_report: Mapping[str, Any] | None = None
    if bundle.report_bytes is not None:
        if _sha256(bundle.report_bytes) != predecessor.report_sha256:
            raise HistoricalEvidenceError(
                "predecessor report exact hash mismatch"
            )
        terminal_report = _strict_json(bundle.report_bytes, "report")
        report_date_echo = terminal_report.get("date_echo", {})
        if (
            terminal_report.get("state") != "STOP_NO_PROMOTION_PILOT_BLOCKED"
            or terminal_report.get("runtime_lock_id")
            != predecessor.runtime_lock_id
            or terminal_report.get("pilot_run_id") != predecessor.pilot_run_id
            or not isinstance(report_date_echo, Mapping)
            or type(report_date_echo.get("mismatch_rows")) is not int
            or report_date_echo.get("mismatch_rows", -1) < 0
        ):
            raise HistoricalEvidenceError(
                "predecessor terminal report telemetry mismatch"
            )
    attempts = checkpoint.get("attempts")
    raw_index = checkpoint.get("raw_index")
    results = checkpoint.get("date_results")
    if (
        checkpoint.get("runtime_lock_id") != predecessor.runtime_lock_id
        or checkpoint.get("pilot_run_id") != predecessor.pilot_run_id
        or checkpoint.get("state") != "BLOCKED"
        or checkpoint.get("last_error_class") != "QuotaBoundaryError"
        or checkpoint.get("completed_dates") != ["20240102"]
        or checkpoint.get("next_date_index") != 1
        or not isinstance(attempts, list)
        or not isinstance(raw_index, list)
        or not isinstance(results, list)
        or len(attempts) != 9
        or len(raw_index) != 9
        or len(results) != 1
    ):
        raise HistoricalEvidenceError("predecessor checkpoint terminal shape mismatch")

    completed_result = results[0]
    if (
        completed_result.get("basDt") != "20240102"
        or completed_result.get("state") != "DATE_COMPLETE"
        or completed_result.get("page_count") != 8
        or completed_result.get("item_count") != 76
        or completed_result.get("total_count") != 76
        or completed_result.get("valid_empty") is not False
    ):
        raise HistoricalEvidenceError("20240102 completed evidence mismatch")
    completed_attempts = [
        row for row in attempts if row.get("basDt") == "20240102"
    ]
    if (
        [row.get("page_no") for row in completed_attempts]
        != list(range(1, 9))
        or any(row.get("state") != "PARSED_200" for row in completed_attempts)
    ):
        raise HistoricalEvidenceError("20240102 page coverage evidence mismatch")

    page_one_attempts = _matching_predecessor_rows(attempts, "20240131", 1)
    page_one_raw = _matching_predecessor_rows(raw_index, "20240131", 1)
    page_one_binding = predecessor.page_one
    if len(page_one_attempts) != 1 or len(page_one_raw) != 1:
        raise HistoricalEvidenceError("20240131 predecessor page-1 evidence missing")
    attempt = page_one_attempts[0]
    reference = page_one_raw[0]
    if (
        attempt.get("attempt") != 1
        or attempt.get("state") != "PARSED_200"
        or attempt.get("github_run_id") != predecessor.workflow_run_id
        or reference.get("attempt") != 1
        or reference.get("s3_object_key") != page_one_binding.object_key
        or reference.get("s3_version_id") != page_one_binding.version_id
        or reference.get("entity_sha256") != page_one_binding.entity_sha256
        or reference.get("entity_bytes") != page_one_binding.entity_bytes
        or reference.get("server_side_encryption")
        != page_one_binding.server_side_encryption
        or reference.get("http_status") != 200
    ):
        raise HistoricalEvidenceError("20240131 page-1 exact reference mismatch")

    mirror_rows = _jsonl_rows(bundle.raw_index_bytes, "raw index")
    mirror_matches = [
        row for row in mirror_rows
        if row.get("s3_object_key") == page_one_binding.object_key
        and row.get("s3_version_id") == page_one_binding.version_id
        and row.get("entity_sha256") == page_one_binding.entity_sha256
    ]
    if len(mirror_matches) != 1:
        raise HistoricalEvidenceError("predecessor raw-index mirror mismatch")

    sealed = custody.read_historical(page_one_binding)
    if (
        sealed is None
        or sealed.object_key != page_one_binding.object_key
        or sealed.version_id != page_one_binding.version_id
        or sealed.entity_sha256 != page_one_binding.entity_sha256
        or sealed.readback_sha256 != page_one_binding.entity_sha256
        or sealed.entity_bytes != page_one_binding.entity_bytes
        or sealed.readback_bytes != page_one_binding.entity_bytes
        or sealed.server_side_encryption != page_one_binding.server_side_encryption
        or sealed.http_status != 200
        or not sealed.etag
        or _sha256(sealed.body) != page_one_binding.entity_sha256
        or len(sealed.body) != page_one_binding.entity_bytes
    ):
        raise HistoricalEvidenceError(
            "predecessor page-1 VersionId/digest/bytes/SSE readback mismatch"
        )
    sa.assert_no_secret(sealed.body, secrets)
    page_one = sa.finance_entity_to_page(
        sealed.body, expected_bas_dt="20240131", expected_page_no=1
    )
    if page_one["page_size"] != REQUEST_PAGE_SIZE:
        raise HistoricalEvidenceError("predecessor page-1 size mismatch")
    telemetry = _page_cap_telemetry(
        "20240131", page_one["total_count"], historical_evidence=True
    )

    inherited_telemetry = {
        key: checkpoint.get(key)
        for key in (
            "event_code_counts",
            "event_code_name_counts",
            "date_echo_match_rows",
            "issuer_identity_rows_checked",
            "issuer_identity_match_rows",
            "issuer_identity_conflicts",
            "issuer_identity_missing_rows",
            "issuer_identity_hashes",
            "seen_item_sha256",
            "exact_duplicate_items",
        )
    }
    inherited_telemetry["date_echo_mismatch_rows"] = (
        terminal_report["date_echo"]["mismatch_rows"]
        if terminal_report is not None
        else "UNKNOWN_NOT_INSTRUMENTED_PREDECESSOR"
    )
    return HistoricalSeed(
        completed_result=dict(completed_result),
        page_one=dict(page_one),
        page_one_identity=sa.pagination_page_1_identity(page_one),
        page_one_reference=dict(reference),
        inherited_attempts=tuple(dict(row) for row in attempts),
        inherited_raw_index=tuple(dict(row) for row in raw_index),
        predecessor_checkpoint_sha256=predecessor.checkpoint_sha256,
        historical_page_cap_telemetry=telemetry,
        telemetry=inherited_telemetry,
    )


def _iso_utc(clock: Callable[[], datetime]) -> str:
    value = clock()
    if not isinstance(value, datetime) or value.tzinfo is None:
        raise BindingError("successor clock must be timezone-aware")
    return value.astimezone(timezone.utc).isoformat()


def _assert_quota_day(
    bindings: SuccessorBindings, clock: Callable[[], datetime]
) -> None:
    value = clock()
    if not isinstance(value, datetime) or value.tzinfo is None:
        raise BindingError("successor clock must be timezone-aware")
    observed = value.astimezone(sa.KST).date().isoformat()
    if observed != bindings.quota_day_kst:
        raise sa.QuotaBoundaryError("successor pilot crossed frozen KST quota day")


def _assert_not_after(
    not_after_utc: datetime | None, clock: Callable[[], datetime]
) -> None:
    if not_after_utc is None:
        return
    if not isinstance(not_after_utc, datetime) or not_after_utc.tzinfo is None:
        raise BindingError("successor absolute not-after must be timezone-aware")
    observed = clock()
    if not isinstance(observed, datetime) or observed.tzinfo is None:
        raise BindingError("successor clock must be timezone-aware")
    if observed.astimezone(timezone.utc) >= not_after_utc.astimezone(timezone.utc):
        raise SelfDeadlineExceededError("successor absolute not-after reached")


def _parse_aware_utc(value: Any) -> datetime:
    if not isinstance(value, str) or not value:
        raise ValueError("timestamp missing")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamp must be timezone-aware")
    return parsed.astimezone(timezone.utc)


def _valid_response_timing(
    marker_at_utc: Any,
    socket_opened_at_utc: Any,
    response_received_at_utc: Any,
    quota_day_kst: Any,
    *,
    crossed: Any,
) -> bool:
    try:
        marker = _parse_aware_utc(marker_at_utc)
        socket_opened = _parse_aware_utc(socket_opened_at_utc)
        response_received = _parse_aware_utc(response_received_at_utc)
    except (TypeError, ValueError):
        return False
    if (
        not isinstance(quota_day_kst, str)
        or (crossed is not None and type(crossed) is not bool)
    ):
        return False
    response_crossed = (
        response_received.astimezone(sa.KST).date().isoformat()
        != quota_day_kst
    )
    return (
        marker <= socket_opened <= response_received
        and marker.astimezone(sa.KST).date().isoformat() == quota_day_kst
        and socket_opened.astimezone(sa.KST).date().isoformat() == quota_day_kst
        and socket_opened < LIVE_NOT_AFTER_UTC
        and (crossed is None or crossed is response_crossed)
    )


def _execution_claim(
    bindings: SuccessorBindings, writer_id: str
) -> dict[str, Any]:
    expected_writer = (
        f"github-run:{bindings.github_run_id}:attempt:{bindings.github_run_attempt}"
    )
    if writer_id != expected_writer:
        raise BindingError("successor writer identity mismatch")
    return {
        "artifact": "M3TOP3_FINANCE_PAGE100_EXECUTION_CLAIM_v1.0",
        "state": "SINGLE_WRITER_CLAIMED",
        "runtime_lock_id": bindings.runtime_lock_id,
        "pilot_run_id": bindings.pilot_run_id,
        "writer_id": writer_id,
        "github_run_id": bindings.github_run_id,
        "github_run_attempt": bindings.github_run_attempt,
        "activation_base_head_commit": ACTIVATION_BASE_HEAD_COMMIT,
        "owner_cap_spec_sha256": OWNER_CAP_SPEC_SHA256,
        "execution_token_sha256": EXECUTION_TOKEN_SHA256,
        "predecessor_workflow_run_id": bindings.predecessor.workflow_run_id,
        "predecessor_rerun": False,
    }


def _claim_record(
    evidence: ExecutionClaimEvidence,
    bindings: SuccessorBindings | None = None,
) -> dict[str, Any]:
    record = {
        "object_key": evidence.object_key,
        "content_sha256": evidence.content_sha256,
        "version_id": evidence.version_id,
        "etag": evidence.etag,
        "server_side_encryption": evidence.server_side_encryption,
        "write_precondition": evidence.write_precondition,
        "writer_id": evidence.writer_id,
    }
    if bindings is not None:
        record.update({
            "github_run_id": bindings.github_run_id,
            "github_run_attempt": bindings.github_run_attempt,
        })
    return record


def _initial_checkpoint(
    bindings: SuccessorBindings,
    seed: HistoricalSeed,
    claim_evidence: ExecutionClaimEvidence,
    *,
    clock: Callable[[], datetime],
) -> dict[str, Any]:
    inherited = {
        "state": "IMPORTED_EXACT_READ_ONLY",
        "runtime_lock_id": bindings.predecessor.runtime_lock_id,
        "pilot_run_id": bindings.predecessor.pilot_run_id,
        "workflow_run_id": bindings.predecessor.workflow_run_id,
        "workflow_run_attempt": 1,
        "checkpoint_sha256": seed.predecessor_checkpoint_sha256,
        "completed_dates_reused": ["20240102"],
        "completed_page_count_reused": 8,
        "completed_item_count_reused": 76,
        "raw_object_count_reused": 9,
        "raw_entity_bytes_reused": 40423,
        "partial_page_reused": {
            "basDt": "20240131",
            "page_no": 1,
            "page_1_identity": seed.page_one_identity,
            "total_count": seed.page_one["total_count"],
            "expected_pages": max(
                1, math.ceil(seed.page_one["total_count"] / REQUEST_PAGE_SIZE)
            ),
            "raw_reference": dict(seed.page_one_reference),
        },
        "provider_result_code_counts": "UNKNOWN_NOT_INSTRUMENTED_PREDECESSOR",
        "event_code_counts": dict(seed.telemetry.get("event_code_counts") or {}),
        "event_code_name_counts": dict(
            seed.telemetry.get("event_code_name_counts") or {}
        ),
        "date_echo_match_rows": int(
            seed.telemetry.get("date_echo_match_rows") or 0
        ),
        "date_echo_mismatch_rows": seed.telemetry.get(
            "date_echo_mismatch_rows",
            "UNKNOWN_NOT_INSTRUMENTED_PREDECESSOR",
        ),
        "issuer_identity_rows_checked": int(
            seed.telemetry.get("issuer_identity_rows_checked") or 0
        ),
        "issuer_identity_match_rows": int(
            seed.telemetry.get("issuer_identity_match_rows") or 0
        ),
        "issuer_identity_conflicts": int(
            seed.telemetry.get("issuer_identity_conflicts") or 0
        ),
        "issuer_identity_missing_rows": int(
            seed.telemetry.get("issuer_identity_missing_rows") or 0
        ),
        "exact_duplicate_items": int(
            seed.telemetry.get("exact_duplicate_items") or 0
        ),
        "attempts": [dict(row) for row in seed.inherited_attempts],
        "raw_index": [dict(row) for row in seed.inherited_raw_index],
        "network_attempts_recounted": 0,
        "raw_entities_rewritten": 0,
        "predecessor_rerun": False,
    }
    telemetry = seed.telemetry
    return {
        "artifact": "M3TOP3_FINANCE_CA_PAGE100_CHECKPOINT_v1.0",
        "schema_version": 1,
        "checkpoint_revision": 0,
        "state": "IN_PROGRESS",
        "runtime_lock_id": bindings.runtime_lock_id,
        "pilot_run_id": bindings.pilot_run_id,
        "activation_base_head_commit": ACTIVATION_BASE_HEAD_COMMIT,
        "owner_cap_spec_sha256": OWNER_CAP_SPEC_SHA256,
        "execution_token_sha256": EXECUTION_TOKEN_SHA256,
        "execution_claim": _claim_record(claim_evidence, bindings),
        "ordered_dates": list(PRIMARY_DATES),
        "request_page_size": REQUEST_PAGE_SIZE,
        "max_pages_per_date": MAX_PAGES_PER_DATE,
        "max_primary_page_slots": MAX_PRIMARY_PAGE_SLOTS,
        "max_network_attempts_total": MAX_NETWORK_ATTEMPTS_TOTAL,
        "max_attempts_per_page": MAX_ATTEMPTS_PER_PAGE,
        "quota_day_kst": bindings.quota_day_kst,
        "finance_ordinal_base": bindings.finance_ordinal_base,
        "next_date_index": 1,
        "completed_dates": ["20240102"],
        "date_results": [dict(seed.completed_result)],
        "current_date": None,
        "inherited_predecessor": inherited,
        "page_1_revalidation": {
            "basDt": "20240131",
            "required_by_successor_resume_contract": True,
            "authorized": True,
            "max_fresh_calls": MAX_FRESH_PREDECESSOR_PAGE1_REVALIDATIONS,
            "fresh_calls_started": 0,
            "state": "PENDING",
            "historical_raw_sha256": bindings.predecessor.page_one.entity_sha256,
            "historical_semantic_identity": seed.page_one_identity,
            "historical_total_count": seed.page_one["total_count"],
            "fresh_raw_sha256": None,
            "fresh_semantic_identity": None,
            "fresh_total_count": None,
            "raw_digest_match": None,
            "page_identity_match": None,
            "total_count_match": None,
            "all_invariants_pass": None,
            "continue_from_page_2_condition": (
                "TOTAL_COUNT_PAGE_IDENTITY_RAW_DIGEST_AND_ALL_"
                "PAGINATION_INVARIANTS_PASS"
            ),
        },
        "attempts": [],
        "raw_index": [],
        "unique_page_slots": [],
        "quota_reservations": 0,
        "provider_api_network_attempts": 0,
        "network_attempts_started_conservative": 0,
        "remote_raw_custody_writes": 0,
        "response_entities_received": 0,
        "no_entity_attempts": 0,
        "raw_entity_bytes": 0,
        "http_status_counts": {},
        "provider_result_code_counts": {},
        "event_code_counts": {},
        "event_code_name_counts": {},
        "date_echo_match_rows": 0,
        "date_echo_mismatch_rows": 0,
        "date_echo_uninstrumented_entities": 0,
        "issuer_identity_rows_checked": 0,
        "issuer_identity_match_rows": 0,
        "issuer_identity_conflicts": 0,
        "issuer_identity_missing_rows": 0,
        "issuer_identity_hashes": dict(
            telemetry.get("issuer_identity_hashes") or {}
        ),
        "seen_item_sha256": list(telemetry.get("seen_item_sha256") or []),
        "exact_duplicate_items": 0,
        "historical_page_cap_telemetry": dict(
            seed.historical_page_cap_telemetry
        ),
        "page_cap_telemetry": None,
        "pagination_drift_events": 0,
        "pagination_drift_records": [],
        "last_error_class": None,
        "normalization_records_created": 0,
        "promotion_actions": 0,
        "automatic_promotion_performed": False,
        "validation_claim": "NONE",
        "gate_effect": "NONE",
        "updated_at_utc": _iso_utc(clock),
    }


def _assert_checkpoint(
    checkpoint: Mapping[str, Any], bindings: SuccessorBindings
) -> None:
    expected_writer = (
        f"github-run:{bindings.github_run_id}:attempt:{bindings.github_run_attempt}"
    )
    expected = {
        "artifact": "M3TOP3_FINANCE_CA_PAGE100_CHECKPOINT_v1.0",
        "schema_version": 1,
        "runtime_lock_id": bindings.runtime_lock_id,
        "pilot_run_id": bindings.pilot_run_id,
        "activation_base_head_commit": ACTIVATION_BASE_HEAD_COMMIT,
        "owner_cap_spec_sha256": OWNER_CAP_SPEC_SHA256,
        "execution_token_sha256": EXECUTION_TOKEN_SHA256,
        "ordered_dates": list(PRIMARY_DATES),
        "request_page_size": REQUEST_PAGE_SIZE,
        "max_pages_per_date": MAX_PAGES_PER_DATE,
        "max_primary_page_slots": MAX_PRIMARY_PAGE_SLOTS,
        "max_network_attempts_total": MAX_NETWORK_ATTEMPTS_TOTAL,
        "max_attempts_per_page": MAX_ATTEMPTS_PER_PAGE,
        "quota_day_kst": bindings.quota_day_kst,
        "finance_ordinal_base": bindings.finance_ordinal_base,
        "normalization_records_created": 0,
        "promotion_actions": 0,
        "automatic_promotion_performed": False,
        "validation_claim": "NONE",
        "gate_effect": "NONE",
    }
    if any(checkpoint.get(key) != value for key, value in expected.items()):
        raise sa.CheckpointConflictError("page-100 checkpoint binding mismatch")
    claim = checkpoint.get("execution_claim")
    if (
        not isinstance(claim, Mapping)
        or claim.get("object_key") != execution_claim_object_key(bindings)
        or claim.get("writer_id") != expected_writer
        or claim.get("content_sha256")
        != _sha256(sa.canonical_json_bytes(_execution_claim(bindings, expected_writer)))
        or not claim.get("version_id")
        or not claim.get("etag")
        or claim.get("server_side_encryption") != "AES256"
        or claim.get("write_precondition") != "IF_NONE_MATCH_STAR"
    ):
        raise sa.CheckpointConflictError("page-100 execution claim binding mismatch")
    if checkpoint.get("state") not in {"IN_PROGRESS", "BLOCKED", "COMPLETE"}:
        raise sa.CheckpointConflictError("page-100 checkpoint state invalid")
    completed = checkpoint.get("completed_dates")
    next_index = checkpoint.get("next_date_index")
    if (
        not isinstance(completed, list)
        or completed != list(PRIMARY_DATES[: len(completed)])
        or next_index != len(completed)
    ):
        raise sa.CheckpointConflictError("page-100 completed prefix invalid")
    inherited = checkpoint.get("inherited_predecessor")
    if (
        not isinstance(inherited, Mapping)
        or inherited.get("checkpoint_sha256")
        != bindings.predecessor.checkpoint_sha256
        or inherited.get("completed_dates_reused") != ["20240102"]
        or inherited.get("network_attempts_recounted") != 0
        or inherited.get("raw_entities_rewritten") != 0
        or inherited.get("predecessor_rerun") is not False
    ):
        raise sa.CheckpointConflictError("inherited evidence binding invalid")
    attempts = checkpoint.get("attempts")
    raw_index = checkpoint.get("raw_index")
    slots = checkpoint.get("unique_page_slots")
    if not all(isinstance(value, list) for value in (attempts, raw_index, slots)):
        raise sa.CheckpointConflictError("page-100 collection shape invalid")
    if (
        checkpoint.get("quota_reservations") != len(attempts)
        or checkpoint.get("provider_api_network_attempts") != sum(
            row.get("provider_call_started") is True for row in attempts
        )
        or checkpoint.get("network_attempts_started_conservative") != len(attempts)
        or checkpoint.get("remote_raw_custody_writes") != len(raw_index)
        or checkpoint.get("response_entities_received") != len(raw_index)
        or len(attempts) > MAX_NETWORK_ATTEMPTS_TOTAL
        or len(slots) > MAX_PRIMARY_PAGE_SLOTS
    ):
        raise sa.CheckpointConflictError("page-100 counter mismatch")
    per_slot: dict[str, list[int]] = {}
    observed_slots: list[str] = []
    for row in attempts:
        if not isinstance(row, Mapping):
            raise sa.CheckpointConflictError("page-100 attempt invalid")
        bas_dt = row.get("basDt")
        page_no = row.get("page_no")
        attempt_no = row.get("attempt")
        slot = f"{bas_dt}:{page_no}"
        if (
            bas_dt not in PRIMARY_DATES[1:]
            or type(page_no) is not int
            or not 1 <= page_no <= MAX_PAGES_PER_DATE
            or type(attempt_no) is not int
            or not 1 <= attempt_no <= MAX_ATTEMPTS_PER_PAGE
            or row.get("quota_day_kst") != bindings.quota_day_kst
            or row.get("github_run_id") != bindings.github_run_id
            or row.get("run_attempt") != bindings.github_run_attempt
            or f"pilot_run_id={bindings.pilot_run_id}/"
            not in str(row.get("raw_object_prefix"))
            or (row.get("provider_call_started") is True and (
                not isinstance(row.get("provider_call_started_at_utc"), str)
                or type(row.get("reservation_checkpoint_revision")) is not int
                or row.get("reservation_checkpoint_revision", 0) <= 0
                or _SHA256_RE.fullmatch(str(row.get("reservation_checkpoint_token_sha256", ""))) is None
                or not isinstance(row.get("execution_claim_version_id"), str)
                or not row.get("execution_claim_version_id")
                or _SHA256_RE.fullmatch(str(row.get("execution_claim_content_sha256", ""))) is None
            ))
            or (("provider_call_checkpoint_revision" in row
                 or "provider_call_checkpoint_token_sha256" in row) and (
                type(row.get("provider_call_checkpoint_revision")) is not int
                or row.get("provider_call_checkpoint_revision", 0) <= 0
                or _SHA256_RE.fullmatch(str(row.get("provider_call_checkpoint_token_sha256", ""))) is None
            ))
            or (row.get("provider_call_started") is not True and (
                "provider_call_checkpoint_revision" in row
                or "provider_call_checkpoint_token_sha256" in row
            ))
            or (row.get("provider_call_started") is True
                and row.get("state") != "RESERVED_WRITE_AHEAD"
                and (
                    "provider_call_checkpoint_revision" not in row
                    or "provider_call_checkpoint_token_sha256" not in row
                ))
            or ("response_received_at_utc" in row and (
                not isinstance(row.get("response_received_at_utc"), str)
                or not row.get("response_received_at_utc")
                or type(row.get("response_crossed_quota_day")) is not bool
                or not _valid_response_timing(
                    row.get("provider_call_started_at_utc"),
                    row.get("socket_opened_at_utc"),
                    row.get("response_received_at_utc"),
                    bindings.quota_day_kst,
                    crossed=row.get("response_crossed_quota_day"),
                )
            ))
            or (row.get("response_entity_received") is True and (
                not isinstance(row.get("socket_opened_at_utc"), str)
                or not isinstance(row.get("response_received_at_utc"), str)
            ))
        ):
            raise sa.CheckpointConflictError("page-100 attempt lineage invalid")
        if slot not in observed_slots:
            observed_slots.append(slot)
        per_slot.setdefault(slot, []).append(attempt_no)
    if slots != observed_slots or any(
        values != list(range(1, len(values) + 1))
        for values in per_slot.values()
    ):
        raise sa.CheckpointConflictError("page-100 attempt sequence invalid")
    raw_by_attempt: dict[tuple[str, int, int], Mapping[str, Any]] = {}
    status_counts: dict[str, int] = {}
    observed_result_counts: dict[str, int] = {}
    for raw in raw_index:
        if not isinstance(raw, Mapping):
            raise sa.CheckpointConflictError("page-100 raw index row invalid")
        identity = (raw.get("basDt"), raw.get("page_no"), raw.get("attempt"))
        matches = [
            row for row in attempts
            if (row.get("basDt"), row.get("page_no"), row.get("attempt"))
            == identity
        ]
        digest = raw.get("entity_sha256")
        if (
            identity in raw_by_attempt
            or len(matches) != 1
            or raw.get("runtime_lock_id") != bindings.runtime_lock_id
            or raw.get("pilot_run_id") != bindings.pilot_run_id
            or raw.get("s3_object_prefix") != matches[0].get("raw_object_prefix")
            or raw.get("s3_object_key") != matches[0].get("object_key")
            or raw.get("s3_version_id") != matches[0].get("s3_version_id")
            or raw.get("s3_etag") != matches[0].get("s3_etag")
            or raw.get("http_status") != matches[0].get("http_status")
            or raw.get("entity_bytes") != matches[0].get("entity_bytes")
            or raw.get("entity_sha256") != matches[0].get("entity_sha256")
            or not isinstance(digest, str)
            or _SHA256_RE.fullmatch(digest) is None
            or raw.get("s3_object_key")
            != canonical_raw_object_key(str(raw.get("s3_object_prefix")), digest)
            or raw.get("remote_readback_sha256") != digest
            or raw.get("remote_readback_bytes") != raw.get("entity_bytes")
            or raw.get("server_side_encryption") != "AES256"
            or raw.get("write_precondition") != "IF_NONE_MATCH_STAR"
            or matches[0].get("provider_call_started") is not True
            or raw.get("provider_call_started_at_utc") != matches[0].get("provider_call_started_at_utc")
            or raw.get("socket_opened_at_utc") != matches[0].get("socket_opened_at_utc")
            or raw.get("response_received_at_utc") != matches[0].get("response_received_at_utc")
            or raw.get("response_crossed_quota_day") != matches[0].get("response_crossed_quota_day")
            or raw.get("reservation_checkpoint_revision") != matches[0].get("reservation_checkpoint_revision")
            or raw.get("reservation_checkpoint_token_sha256") != matches[0].get("reservation_checkpoint_token_sha256")
            or raw.get("provider_call_checkpoint_revision") != matches[0].get("provider_call_checkpoint_revision")
            or raw.get("provider_call_checkpoint_token_sha256") != matches[0].get("provider_call_checkpoint_token_sha256")
            or raw.get("execution_claim_version_id") != matches[0].get("execution_claim_version_id")
            or raw.get("execution_claim_content_sha256") != matches[0].get("execution_claim_content_sha256")
        ):
            raise sa.CheckpointConflictError("page-100 raw custody join invalid")
        raw_by_attempt[identity] = raw
        status = str(raw.get("http_status"))
        status_counts[status] = status_counts.get(status, 0) + 1
        result_code = str(raw.get("provider_result_code"))
        observed_result_counts[result_code] = (
            observed_result_counts.get(result_code, 0) + 1
        )
    for attempt_row in attempts:
        attempt_identity = (
            attempt_row.get("basDt"), attempt_row.get("page_no"),
            attempt_row.get("attempt"),
        )
        if (
            attempt_row.get("response_crossed_quota_day") is True
            and attempt_identity not in raw_by_attempt
        ):
            raise sa.CheckpointConflictError(
                "quota-day rollover response lacks raw custody"
            )
    if (
        checkpoint.get("raw_entity_bytes")
        != sum(int(row.get("entity_bytes", -1)) for row in raw_index)
        or checkpoint.get("http_status_counts") != status_counts
        or checkpoint.get("provider_result_code_counts")
        != observed_result_counts
    ):
        raise sa.CheckpointConflictError("page-100 raw aggregate invalid")
    revalidation = checkpoint.get("page_1_revalidation")
    page_one_rows = _matching_predecessor_rows(attempts, "20240131", 1)
    page_one_calls = sum(
        row.get("provider_call_started") is True for row in page_one_rows
    )
    if (
        not isinstance(revalidation, Mapping)
        or revalidation.get("required_by_successor_resume_contract") is not True
        or revalidation.get("authorized") is not True
        or revalidation.get("max_fresh_calls") != 1
        or revalidation.get("fresh_calls_started") != page_one_calls
        or page_one_calls > 1
    ):
        raise sa.CheckpointConflictError("page-1 revalidation cap invalid")
    if revalidation.get("state") not in {
        "PENDING", "COMPLETE_MATCH", "BLOCKED_THREE_WAY_SHIFT"
    }:
        raise sa.CheckpointConflictError("page-1 revalidation state invalid")
    partial = inherited.get("partial_page_reused", {})
    if (
        revalidation.get("historical_raw_sha256")
        != bindings.predecessor.page_one.entity_sha256
        or revalidation.get("historical_semantic_identity")
        != partial.get("page_1_identity")
        or revalidation.get("historical_total_count")
        != partial.get("total_count")
    ):
        raise sa.CheckpointConflictError("historical page-1 invariant shifted")
    if page_one_calls == 1:
        page_one_attempt = page_one_rows[0]
        if (
            revalidation.get("fresh_raw_sha256")
            not in {None, page_one_attempt.get("entity_sha256")}
        ):
            raise sa.CheckpointConflictError("fresh page-1 digest binding invalid")
    if revalidation.get("state") == "COMPLETE_MATCH" and not (
        revalidation.get("raw_digest_match") is True
        and revalidation.get("page_identity_match") is True
        and revalidation.get("total_count_match") is True
        and revalidation.get("all_invariants_pass") is True
    ):
        raise sa.CheckpointConflictError("page-1 revalidation evidence invalid")
    current = checkpoint.get("current_date")
    if current is not None:
        if (
            not isinstance(current, Mapping)
            or next_index >= len(PRIMARY_DATES)
            or current.get("basDt") != PRIMARY_DATES[next_index]
            or not isinstance(current.get("validated_pages"), list)
        ):
            raise sa.CheckpointConflictError("page-100 current date invalid")
        validated = current["validated_pages"]
        if validated:
            total = current.get("total_count")
            expected_pages = current.get("expected_pages")
            if (
                type(total) is not int
                or total < 0
                or current.get("page_size") != REQUEST_PAGE_SIZE
                or expected_pages != max(1, math.ceil(total / REQUEST_PAGE_SIZE))
                or not 1 <= expected_pages <= MAX_PAGES_PER_DATE
                or [row.get("page_no") for row in validated]
                != list(range(1, len(validated) + 1))
            ):
                raise sa.CheckpointConflictError("page-100 current cap invalid")
            if current.get("basDt") == "20240131" and (
                revalidation.get("state") != "COMPLETE_MATCH"
            ):
                raise sa.CheckpointConflictError(
                    "20240131 progress bypassed three-way revalidation"
                )
    historical_cap = checkpoint.get("historical_page_cap_telemetry")
    expected_historical_cap = _page_cap_telemetry(
        "20240131", int(partial.get("total_count", -1)),
        historical_evidence=True,
    )
    if historical_cap != expected_historical_cap:
        raise sa.CheckpointConflictError("historical page-cap telemetry shifted")
    results = checkpoint.get("date_results")
    if (
        not isinstance(results, list)
        or len(results) != len(completed)
        or [row.get("basDt") for row in results] != completed
    ):
        raise sa.CheckpointConflictError("page-100 date result prefix invalid")
    for result in results:
        total = result.get("total_count")
        page_count = result.get("page_count")
        if (
            result.get("state") != "DATE_COMPLETE"
            or type(total) is not int
            or total < 0
            or result.get("item_count") != total
            or page_count != max(1, math.ceil(total / REQUEST_PAGE_SIZE))
            or not 1 <= page_count <= MAX_PAGES_PER_DATE
        ):
            raise sa.CheckpointConflictError("page-100 date result cap invalid")
    result_counts = checkpoint.get("provider_result_code_counts")
    drift_records = checkpoint.get("pagination_drift_records")
    if (
        not isinstance(result_counts, Mapping)
        or any(
            not isinstance(key, str) or type(value) is not int or value < 0
            for key, value in result_counts.items()
        )
        or sum(result_counts.values()) != len(raw_index)
        or not isinstance(drift_records, list)
        or checkpoint.get("pagination_drift_events") != len(drift_records)
        or type(checkpoint.get("date_echo_mismatch_rows")) is not int
        or checkpoint.get("date_echo_mismatch_rows", -1) < 0
        or type(checkpoint.get("date_echo_uninstrumented_entities")) is not int
        or checkpoint.get("date_echo_uninstrumented_entities", -1) < 0
    ):
        raise sa.CheckpointConflictError("page-100 telemetry counters invalid")
    successor_complete_items = sum(
        int(row.get("item_count", 0)) for row in results[1:]
    )
    if checkpoint.get("state") == "COMPLETE" and (
        checkpoint.get("provider_result_code_counts")
        != ({"00": len(raw_index)} if raw_index else {})
        or checkpoint.get("date_echo_match_rows") != successor_complete_items
        or checkpoint.get("date_echo_mismatch_rows") != 0
        or checkpoint.get("date_echo_uninstrumented_entities") != 0
        or checkpoint.get("pagination_drift_events") != 0
        or checkpoint.get("issuer_identity_conflicts") != 0
        or sum(checkpoint.get("event_code_counts", {}).values())
        != successor_complete_items
        or checkpoint.get("issuer_identity_rows_checked", 0)
        + checkpoint.get("issuer_identity_missing_rows", 0)
        != successor_complete_items
    ):
        raise sa.CheckpointConflictError("complete page-100 telemetry invalid")
    if checkpoint.get("state") == "COMPLETE" and (
        completed != list(PRIMARY_DATES) or checkpoint.get("current_date") is not None
    ):
        raise sa.CheckpointConflictError("complete page-100 checkpoint incomplete")


def _observe_items(
    checkpoint: dict[str, Any], items: Sequence[Mapping[str, Any]]
) -> int:
    conflicts_before = int(checkpoint["issuer_identity_conflicts"])
    seen = set(checkpoint["seen_item_sha256"])
    identities: dict[str, str] = checkpoint["issuer_identity_hashes"]
    for source_item in items:
        item = dict(source_item)
        item_sha = _sha256(sa.canonical_json_bytes(item))
        if item_sha in seen:
            checkpoint["exact_duplicate_items"] += 1
        else:
            seen.add(item_sha)
        code = str(item.get("rgtExertRcd") or "<EMPTY>")
        name = str(item.get("rgtExertRcdNm") or "<EMPTY>")
        checkpoint["event_code_counts"][code] = (
            checkpoint["event_code_counts"].get(code, 0) + 1
        )
        pair = json.dumps(
            {"code": code, "name": name},
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        checkpoint["event_code_name_counts"][pair] = (
            checkpoint["event_code_name_counts"].get(pair, 0) + 1
        )
        custody_no = str(item.get("issuCmpyKsdCustNo") or "")
        if not custody_no:
            checkpoint["issuer_identity_missing_rows"] += 1
            continue
        identity = _sha256(sa.canonical_json_bytes({
            "issuCmpyKsdCustNo": custody_no,
            "crno": str(item.get("crno") or ""),
            "stckIssuCmpyNm": str(item.get("stckIssuCmpyNm") or ""),
        }))
        checkpoint["issuer_identity_rows_checked"] += 1
        if custody_no in identities and identities[custody_no] != identity:
            checkpoint["issuer_identity_conflicts"] += 1
        else:
            identities[custody_no] = identity
            checkpoint["issuer_identity_match_rows"] += 1
    checkpoint["seen_item_sha256"] = sorted(seen)
    return int(checkpoint["issuer_identity_conflicts"]) - conflicts_before


def _distribution_summary(values: Sequence[int]) -> dict[str, int | str]:
    if not values:
        return {
            "min": "UNKNOWN_NOT_OBSERVED",
            "p50": "UNKNOWN_NOT_OBSERVED",
            "p90": "UNKNOWN_NOT_OBSERVED",
            "max": "UNKNOWN_NOT_OBSERVED",
        }
    ordered = sorted(values)

    def percentile(numerator: int, denominator: int) -> int:
        index = max(0, math.ceil(len(ordered) * numerator / denominator) - 1)
        return ordered[index]

    return {
        "min": ordered[0],
        "p50": percentile(50, 100),
        "p90": percentile(90, 100),
        "max": ordered[-1],
    }


def _build_report(
    checkpoint: Mapping[str, Any], checkpoint_token: str | None = None
) -> dict[str, Any]:
    completed = len(checkpoint.get("completed_dates", []))
    results = list(checkpoint.get("date_results", []))
    total_items = sum(int(row.get("item_count", 0)) for row in results)
    data_dates = sum(int(row.get("item_count", 0)) > 0 for row in results)
    inherited = checkpoint.get("inherited_predecessor", {})
    inherited_conflicts = int(inherited.get("issuer_identity_conflicts", 0))
    new_conflicts = int(checkpoint.get("issuer_identity_conflicts", 0))
    conflict_total = inherited_conflicts + new_conflicts
    complete_exact = (
        checkpoint.get("state") == "COMPLETE"
        and completed == len(PRIMARY_DATES)
    )
    if not complete_exact:
        decision = "STOP_NO_PROMOTION_PILOT_BLOCKED"
    elif data_dates == 0:
        decision = "STOP_NO_PROMOTION_ZERO_DENSITY"
    elif conflict_total:
        decision = "HOLD_NO_PROMOTION_QUARANTINED"
    else:
        decision = "RECOMMEND_SEPARATE_BOUNDED_RAW_HISTORICAL_AUTHORITY"

    inherited_codes = dict(inherited.get("event_code_counts", {}))
    current_codes = dict(checkpoint.get("event_code_counts", {}))
    aggregate_codes = dict(inherited_codes)
    for code, count in current_codes.items():
        aggregate_codes[code] = aggregate_codes.get(code, 0) + count
    raw_index = list(checkpoint.get("raw_index", []))
    sse_counts: dict[str, int] = {}
    for row in raw_index:
        key = str(row.get("server_side_encryption") or "UNKNOWN")
        sse_counts[key] = sse_counts.get(key, 0) + 1
    successor_attempts = int(checkpoint.get("provider_api_network_attempts", 0))
    successor_slots = len(checkpoint.get("unique_page_slots", []))
    successor_retries = sum(
        row.get("provider_call_started") is True and int(row.get("attempt", 0)) > 1
        for row in checkpoint.get("attempts", [])
    )
    total_page_acquisitions = 8 + successor_slots
    inherited_http = {"200": 9}
    aggregate_http = dict(inherited_http)
    for status, count in checkpoint.get("http_status_counts", {}).items():
        aggregate_http[status] = aggregate_http.get(status, 0) + count
    return {
        "artifact": "M3TOP3_FINANCE_CA_PAGE100_PILOT_REPORT_v1.0",
        "artifact_class": "FINANCE_ONLY_BOUNDED_PAGE100_PILOT_RESULT",
        "state": decision,
        "runtime_lock_id": RUNTIME_LOCK_ID,
        "pilot_run_id": PILOT_RUN_ID,
        "owner_cap_spec_sha256": OWNER_CAP_SPEC_SHA256,
        "result": {
            "checkpoint_state": checkpoint.get("state"),
            "completed_date_count": completed,
            "blocked_date_count": len(PRIMARY_DATES) - completed,
            "primary_date_count": len(PRIMARY_DATES),
            "all_primary_dates_completed": complete_exact,
            "total_items": total_items,
            "dates_with_rows": data_dates,
            "valid_empty_dates": completed - data_dates,
            "page_count_by_date": {
                row["basDt"]: row["page_count"] for row in results
            },
            "rows_per_date": _distribution_summary([
                int(row["item_count"]) for row in results
            ]),
            "pages_per_date": _distribution_summary([
                int(row["page_count"]) for row in results
            ]),
            "total_rows": total_items,
            "total_page_acquisitions": total_page_acquisitions,
            "total_network_attempts": 9 + successor_attempts,
            "total_retries": successor_retries,
            "raw_bytes_total": 40423
            + int(checkpoint.get("raw_entity_bytes", 0)),
            "s3_raw_object_count": 9 + len(raw_index),
        },
        "completed_date_count": completed,
        "blocked_date_count": len(PRIMARY_DATES) - completed,
        "primary_date_count": len(PRIMARY_DATES),
        "total_items": total_items,
        "total_rows": total_items,
        "total_page_acquisitions": total_page_acquisitions,
        "total_network_attempts": 9 + successor_attempts,
        "total_retries": successor_retries,
        "raw_bytes_total": 40423 + int(checkpoint.get("raw_entity_bytes", 0)),
        "s3_raw_object_count": 9 + len(raw_index),
        "rows_per_date": _distribution_summary([
            int(row["item_count"]) for row in results
        ]),
        "pages_per_date": _distribution_summary([
            int(row["page_count"]) for row in results
        ]),
        "dates_with_rows": data_dates,
        "distributions": {
            "event_code_counts_inherited": inherited_codes,
            "event_code_counts_successor": current_codes,
            "event_code_counts_aggregate": aggregate_codes,
            "event_code_name_pairs_successor": dict(
                checkpoint.get("event_code_name_counts", {})
            ),
            "provider_result_code_counts_successor": dict(
                checkpoint.get("provider_result_code_counts", {})
            ),
            "provider_result_code_counts_inherited": inherited.get(
                "provider_result_code_counts",
                "UNKNOWN_NOT_INSTRUMENTED_PREDECESSOR",
            ),
            "http_status_counts_inherited": inherited_http,
            "http_status_counts_successor": dict(
                checkpoint.get("http_status_counts", {})
            ),
            "http_status_counts_aggregate": aggregate_http,
            "provider_result_code_counts_aggregate": (
                "UNKNOWN_NOT_INSTRUMENTED_PREDECESSOR"
            ),
        },
        "date_echo": {
            "inherited_match_rows": inherited.get("date_echo_match_rows", 0),
            "inherited_mismatch_rows": inherited.get(
                "date_echo_mismatch_rows",
                "UNKNOWN_NOT_INSTRUMENTED_PREDECESSOR",
            ),
            "successor_match_rows": checkpoint.get("date_echo_match_rows", 0),
            "successor_mismatch_rows": checkpoint.get(
                "date_echo_mismatch_rows", 0
            ),
            "aggregate_mismatch_rows": (
                "UNKNOWN_NOT_INSTRUMENTED_PREDECESSOR"
                if not isinstance(inherited.get("date_echo_mismatch_rows"), int)
                else int(inherited.get("date_echo_mismatch_rows", 0))
                + int(checkpoint.get("date_echo_mismatch_rows", 0))
            ),
            "uninstrumented_successor_entities": checkpoint.get(
                "date_echo_uninstrumented_entities", 0
            ),
        },
        "issuer_identity": {
            "inherited_match_rows": inherited.get(
                "issuer_identity_match_rows", 0
            ),
            "inherited_missing_rows": inherited.get(
                "issuer_identity_missing_rows", 0
            ),
            "inherited_conflicts": inherited_conflicts,
            "successor_rows_checked": checkpoint.get(
                "issuer_identity_rows_checked", 0
            ),
            "successor_match_rows": checkpoint.get(
                "issuer_identity_match_rows", 0
            ),
            "successor_missing_rows": checkpoint.get(
                "issuer_identity_missing_rows", 0
            ),
            "successor_conflicts": new_conflicts,
            "aggregate_match_rows": int(
                inherited.get("issuer_identity_match_rows", 0)
            ) + int(checkpoint.get("issuer_identity_match_rows", 0)),
            "aggregate_missing_rows": int(
                inherited.get("issuer_identity_missing_rows", 0)
            ) + int(checkpoint.get("issuer_identity_missing_rows", 0)),
            "aggregate_conflicts": conflict_total,
        },
        "duplicates": {
            "inherited_exact_duplicate_items": inherited.get(
                "exact_duplicate_items", 0
            ),
            "successor_exact_duplicate_items": checkpoint.get(
                "exact_duplicate_items", 0
            ),
        },
        "pagination_drift": {
            "event_count": checkpoint.get("pagination_drift_events", 0),
            "events": list(checkpoint.get("pagination_drift_records", [])),
        },
        "page_1_revalidation": dict(
            checkpoint.get("page_1_revalidation", {})
        ),
        "historical_page_cap_telemetry": checkpoint.get(
            "historical_page_cap_telemetry"
        ),
        "page_cap_telemetry": checkpoint.get("page_cap_telemetry"),
        "quota": {
            "quota_day_kst": checkpoint.get("quota_day_kst"),
            "pre_pilot_finance_ordinal": checkpoint.get(
                "finance_ordinal_base"
            ),
            "successor_reservations": checkpoint.get("quota_reservations", 0),
            "provider_finance_last_ordinal": int(
                checkpoint.get("finance_ordinal_base", 0)
            ) + int(checkpoint.get("quota_reservations", 0)),
            "provider_api_network_attempts": checkpoint.get(
                "provider_api_network_attempts", 0
            ),
            "network_attempts_started_conservative": checkpoint.get(
                "network_attempts_started_conservative", 0
            ),
            "response_entities_received": checkpoint.get(
                "response_entities_received", 0
            ),
            "no_entity_attempts": checkpoint.get("no_entity_attempts", 0),
            "unique_primary_page_slots": len(
                checkpoint.get("unique_page_slots", [])
            ),
            "caps": {
                "pages_per_date": MAX_PAGES_PER_DATE,
                "primary_page_slots": MAX_PRIMARY_PAGE_SLOTS,
                "network_attempts": MAX_NETWORK_ATTEMPTS_TOTAL,
                "attempts_per_page": MAX_ATTEMPTS_PER_PAGE,
            },
            "remaining_governed_margin": {
                "known_successor_attempt_margin": (
                    MAX_NETWORK_ATTEMPTS_TOTAL
                    - int(checkpoint.get("quota_reservations", 0))
                ),
                "external_attempts": "UNKNOWN_NOT_INSTRUMENTED",
                "effective_provider_margin": (
                    "UNKNOWN_NOT_INSTRUMENTED_EXTERNAL_ATTEMPTS"
                ),
            },
        },
        "s3_custody": {
            "bucket": "semi-data-plane-aofspds-20260815",
            "successor_raw_prefix": (
                RAW_KEY_PREFIX + "_pilot_generation/"
                + f"runtime_lock_id={RUNTIME_LOCK_ID}/"
                + f"pilot_run_id={PILOT_RUN_ID}/"
            ),
            "checkpoint_object_key": (
                RAW_KEY_PREFIX + "_pilot_control/"
                + f"runtime_lock_id={RUNTIME_LOCK_ID}/"
                + f"pilot_run_id={PILOT_RUN_ID}/checkpoint.json"
            ),
            "writer_claim_object_key": checkpoint.get(
                "execution_claim", {}
            ).get("object_key"),
            "inherited_read_only_objects": inherited.get(
                "raw_object_count_reused", 9
            ),
            "inherited_read_only_bytes": inherited.get(
                "raw_entity_bytes_reused", 40423
            ),
            "successor_objects": len(raw_index),
            "successor_entity_bytes": checkpoint.get("raw_entity_bytes", 0),
            "verification": {
                "sha256": {
                    "inherited_verified_objects": 9,
                    "successor_verified_objects": sum(
                        row.get("entity_sha256")
                        == row.get("remote_readback_sha256")
                        for row in raw_index
                    ),
                    "aggregate_verified_objects": 9 + sum(
                        row.get("entity_sha256")
                        == row.get("remote_readback_sha256")
                        for row in raw_index
                    ),
                },
                "bytes": {
                    "inherited_verified_objects": 9,
                    "successor_verified_objects": sum(
                        row.get("entity_bytes")
                        == row.get("remote_readback_bytes")
                        for row in raw_index
                    ),
                    "aggregate_verified_objects": 9 + sum(
                        row.get("entity_bytes")
                        == row.get("remote_readback_bytes")
                        for row in raw_index
                    ),
                },
                "version_id": {
                    "inherited_verified_objects": 9,
                    "successor_verified_objects": sum(
                        bool(row.get("s3_version_id")) for row in raw_index
                    ),
                    "aggregate_verified_objects": 9 + sum(
                        bool(row.get("s3_version_id")) for row in raw_index
                    ),
                },
                "encryption_readback": {
                    "inherited_aes256_objects": 9,
                    "successor_aes256_objects": sum(
                        row.get("server_side_encryption") == "AES256"
                        for row in raw_index
                    ),
                    "aggregate_aes256_objects": 9 + sum(
                        row.get("server_side_encryption") == "AES256"
                        for row in raw_index
                    ),
                },
            },
            "version_id_bound_objects": sum(
                bool(row.get("s3_version_id")) for row in raw_index
            ),
            "readback_digest_bound_objects": sum(
                row.get("entity_sha256") == row.get("remote_readback_sha256")
                for row in raw_index
            ),
            "server_side_encryption_counts": sse_counts,
            "http_status_counts": dict(
                checkpoint.get("http_status_counts", {})
            ),
        },
        "raw_index": raw_index,
        "checkpoint_token_sha256": (
            _sha256(checkpoint_token.encode()) if checkpoint_token else None
        ),
        "reused_completed_dates": ["20240102"],
        "reused_raw_entities": 9,
        "new_raw_entities": len(raw_index),
        "new_raw_entity_bytes": checkpoint.get("raw_entity_bytes", 0),
        "new_network_attempts": checkpoint.get("quota_reservations", 0),
        "predecessor_network_attempts_recounted": 0,
        "predecessor_raw_entities_rewritten": 0,
        "predecessor_rerun": False,
        "page_1_fresh_revalidations": checkpoint.get(
            "page_1_revalidation", {}
        ).get("fresh_calls_started", 0),
        "last_error_class": checkpoint.get("last_error_class"),
        "unknown_metric_policy": (
            "UNKNOWN_OR_NOT_INSTRUMENTED_MUST_NOT_BE_REPRESENTED_AS_ZERO"
        ),
        "normalization_records_created": 0,
        "automatic_promotion_performed": False,
        "validation_claim": "NONE",
        "gate_effect": "NONE",
    }


def _attempts_for(
    checkpoint: Mapping[str, Any], bas_dt: str, page_no: int
) -> list[dict[str, Any]]:
    return [
        row for row in checkpoint["attempts"]
        if row.get("basDt") == bas_dt and row.get("page_no") == page_no
    ]


def _current_raw_record(
    bindings: SuccessorBindings,
    attempt: Mapping[str, Any],
    sealed: SealedEntity,
    *,
    reconciled: bool,
) -> dict[str, Any]:
    return {
        "runtime_lock_id": bindings.runtime_lock_id,
        "pilot_run_id": bindings.pilot_run_id,
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
        "provider_result_code": _provider_result_code(sealed.body),
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
        "provider_call_started_at_utc": attempt["provider_call_started_at_utc"],
        "socket_opened_at_utc": attempt["socket_opened_at_utc"],
        "response_received_at_utc": attempt["response_received_at_utc"],
        "response_crossed_quota_day": attempt["response_crossed_quota_day"],
        "reservation_checkpoint_revision": attempt["reservation_checkpoint_revision"],
        "reservation_checkpoint_token_sha256": attempt["reservation_checkpoint_token_sha256"],
        "provider_call_checkpoint_revision": attempt["provider_call_checkpoint_revision"],
        "provider_call_checkpoint_token_sha256": attempt["provider_call_checkpoint_token_sha256"],
        "execution_claim_version_id": attempt["execution_claim_version_id"],
        "execution_claim_content_sha256": attempt["execution_claim_content_sha256"],
        "reconciled_after_custody_before_checkpoint_gap": reconciled,
        "canonical": True,
        "historical_reuse": False,
        "normalization_effect": "NONE",
        "promotion_effect": "NONE",
    }


def _assert_checkpoint_entity_readback(
    attempt: Mapping[str, Any], sealed: SealedEntity
) -> None:
    """Bind resumed remote bytes to every custody field stored in checkpoint."""
    expected_key = attempt.get("object_key")
    if (
        sealed.object_key != expected_key
        or sealed.version_id != attempt.get("s3_version_id")
        or sealed.entity_sha256 != attempt.get("entity_sha256")
        or sealed.readback_sha256 != attempt.get("entity_sha256")
        or _sha256(sealed.body) != attempt.get("entity_sha256")
        or sealed.entity_bytes != attempt.get("entity_bytes")
        or sealed.readback_bytes != attempt.get("entity_bytes")
        or len(sealed.body) != attempt.get("entity_bytes")
        or sealed.http_status != attempt.get("http_status")
        or sealed.server_side_encryption != "AES256"
        or sealed.write_precondition != "IF_NONE_MATCH_STAR"
        or not sealed.etag
        or sealed.etag != attempt.get("s3_etag")
        or sealed.acquired_at_utc != attempt.get("socket_opened_at_utc")
        or getattr(sealed, "response_received_at_utc", None)
           != attempt.get("response_received_at_utc")
        or not _valid_response_timing(
            attempt.get("provider_call_started_at_utc"),
            attempt.get("socket_opened_at_utc"),
            attempt.get("response_received_at_utc"),
            attempt.get("quota_day_kst"),
            crossed=attempt.get("response_crossed_quota_day"),
        )
        or sealed.storage_locator
        != f"s3://semi-data-plane-aofspds-20260815/{expected_key}"
    ):
        raise RemoteCustodyError("successor checkpoint raw entity readback shifted")


def run_page100_pilot(
    spec: Page100Spec,
    bindings: SuccessorBindings,
    predecessor_bundle: PredecessorBundle,
    *,
    transport: FinanceTransport,
    custody: Page100CustodyStore,
    claim_store: ExecutionClaimStore,
    checkpoint_store: DurableCheckpointStore,
    writer_id: str,
    secrets: tuple[str, ...],
    clock: Callable[[], datetime] = lambda: datetime.now(timezone.utc),
    not_after_utc: datetime | None = None,
    deadline_monotonic: float | None = None,
    monotonic_fn: Callable[[], float] = time.monotonic,
    sleep_fn: Callable[[float], None] = time.sleep,
) -> dict[str, Any]:
    """Run the new pilot without rerunning or rewriting predecessor work."""
    _validate_spec(spec)
    _validate_bindings(bindings)
    _assert_quota_day(bindings, clock)
    seed = load_historical_seed(
        bindings, predecessor_bundle, custody, secrets=secrets
    )
    _assert_quota_day(bindings, clock)
    _assert_not_after(not_after_utc, clock)

    claim = _execution_claim(bindings, writer_id)
    _assert_not_after(not_after_utc, clock)
    evidence = claim_store.acquire_execution_claim(claim)
    expected_claim_hash = _sha256(sa.canonical_json_bytes(claim))
    if (
        not isinstance(evidence, ExecutionClaimEvidence)
        or evidence.object_key != execution_claim_object_key(bindings)
        or evidence.content_sha256 != expected_claim_hash
        or evidence.writer_id != writer_id
        or not evidence.version_id
        or not evidence.etag
        or evidence.server_side_encryption != "AES256"
        or evidence.write_precondition != "IF_NONE_MATCH_STAR"
    ):
        raise sa.CheckpointConflictError(
            "successor quota-day-global writer claim mismatch"
        )

    loaded, token = checkpoint_store.load()
    if loaded is None:
        _assert_not_after(not_after_utc, clock)
        checkpoint = _initial_checkpoint(bindings, seed, evidence, clock=clock)
        _assert_not_after(not_after_utc, clock)
        token = checkpoint_store.compare_and_swap(checkpoint, None)
    else:
        checkpoint = json.loads(json.dumps(loaded))
    if checkpoint.get("execution_claim") != _claim_record(evidence, bindings):
        raise sa.CheckpointConflictError(
            "successor checkpoint claim evidence shifted"
        )
    _assert_checkpoint(checkpoint, bindings)
    if checkpoint["state"] == "COMPLETE":
        return _build_report(checkpoint, token)
    if checkpoint["state"] == "BLOCKED":
        raise Page100PilotError("durable successor checkpoint is blocked")

    def save() -> None:
        nonlocal token
        checkpoint["checkpoint_revision"] += 1
        checkpoint["updated_at_utc"] = _iso_utc(clock)
        _assert_checkpoint(checkpoint, bindings)
        sa.assert_no_secret(sa.canonical_json_bytes(checkpoint), secrets)
        token = checkpoint_store.compare_and_swap(checkpoint, token)

    def record_pagination_drift(
        kind: str, bas_dt: str, page_no: int, **details: Any
    ) -> None:
        checkpoint["pagination_drift_events"] += 1
        checkpoint["pagination_drift_records"].append({
            "kind": kind,
            "basDt": bas_dt,
            "page_no": page_no,
            **details,
        })
        save()

    def assert_self_deadline() -> None:
        _assert_not_after(not_after_utc, clock)
        if (
            deadline_monotonic is not None
            and monotonic_fn() >= deadline_monotonic
        ):
            raise SelfDeadlineExceededError(
                "Finance successor self-deadline reached"
            )

    def reserve(
        bas_dt: str, page_no: int, *, attempt_limit: int
    ) -> dict[str, Any]:
        assert_self_deadline()
        _assert_quota_day(bindings, clock)
        prior = _attempts_for(checkpoint, bas_dt, page_no)
        if len(prior) >= attempt_limit:
            raise sa.QuotaBoundaryError("Finance page attempt ceiling reached")
        if checkpoint["quota_reservations"] >= MAX_NETWORK_ATTEMPTS_TOTAL:
            raise sa.QuotaBoundaryError("Finance page-100 attempt ceiling reached")
        slot = f"{bas_dt}:{page_no}"
        if slot not in checkpoint["unique_page_slots"]:
            if len(checkpoint["unique_page_slots"]) >= MAX_PRIMARY_PAGE_SLOTS:
                raise sa.QuotaBoundaryError("Finance page-100 slot ceiling reached")
            checkpoint["unique_page_slots"].append(slot)
        attempt_no = len(prior) + 1
        record = {
            "basDt": bas_dt,
            "page_no": page_no,
            "attempt": attempt_no,
            "request_id": deterministic_request_id(bas_dt, page_no),
            "quota_day_kst": bindings.quota_day_kst,
            "raw_object_prefix": deterministic_raw_object_prefix(
                bindings, bas_dt, page_no, attempt_no
            ),
            "provider_quota_ordinal": (
                bindings.finance_ordinal_base
                + checkpoint["quota_reservations"] + 1
            ),
            "github_run_id": bindings.github_run_id,
            "run_attempt": bindings.github_run_attempt,
            "state": "RESERVED_WRITE_AHEAD",
            "reserved_at_utc": _iso_utc(clock),
            "response_entity_received": False,
            "provider_call_started": False,
        }
        checkpoint["attempts"].append(record)
        checkpoint["quota_reservations"] += 1
        checkpoint["network_attempts_started_conservative"] += 1
        save()
        return record

    def persist_sealed(
        attempt: dict[str, Any], sealed: SealedEntity, *, reconciled: bool
    ) -> None:
        expected_key = canonical_raw_object_key(
            attempt["raw_object_prefix"], sealed.entity_sha256
        )
        if not attempt.get("socket_opened_at_utc"):
            attempt["socket_opened_at_utc"] = sealed.acquired_at_utc
        if not attempt.get("response_received_at_utc"):
            response_received = getattr(sealed, "response_received_at_utc", None)
            if not isinstance(response_received, str) or not response_received:
                raise RemoteCustodyError("successor recovered response timing missing")
            attempt["response_received_at_utc"] = response_received
            attempt["response_crossed_quota_day"] = (
                _parse_aware_utc(response_received).astimezone(sa.KST).date().isoformat()
                != bindings.quota_day_kst
            )
        if not _valid_response_timing(
            attempt.get("provider_call_started_at_utc"),
            attempt.get("socket_opened_at_utc"),
            attempt.get("response_received_at_utc"),
            bindings.quota_day_kst,
            crossed=attempt.get("response_crossed_quota_day"),
        ):
            raise RemoteCustodyError("successor response timing invariant mismatch")
        if (
            sealed.object_key != expected_key
            or sealed.entity_sha256 != sealed.readback_sha256
            or sealed.entity_sha256 != _sha256(sealed.body)
            or sealed.entity_bytes != sealed.readback_bytes
            or sealed.entity_bytes != len(sealed.body)
            or sealed.server_side_encryption != "AES256"
            or sealed.write_precondition != "IF_NONE_MATCH_STAR"
            or not sealed.version_id
            or not sealed.etag
            or sealed.storage_locator
            != f"s3://semi-data-plane-aofspds-20260815/{expected_key}"
            or attempt.get("provider_call_started") is not True
            or not attempt.get("provider_call_started_at_utc")
            or type(attempt.get("reservation_checkpoint_revision")) is not int
            or _SHA256_RE.fullmatch(str(attempt.get("reservation_checkpoint_token_sha256", ""))) is None
            or type(attempt.get("provider_call_checkpoint_revision")) is not int
            or _SHA256_RE.fullmatch(str(attempt.get("provider_call_checkpoint_token_sha256", ""))) is None
            or attempt.get("execution_claim_version_id") != evidence.version_id
            or attempt.get("execution_claim_content_sha256") != evidence.content_sha256
            or sealed.acquired_at_utc != attempt.get("socket_opened_at_utc")
            or getattr(sealed, "response_received_at_utc", attempt.get("response_received_at_utc"))
               != attempt.get("response_received_at_utc")
            or not attempt.get("response_received_at_utc")
            or type(attempt.get("response_crossed_quota_day")) is not bool
        ):
            raise RemoteCustodyError("successor raw custody invariant mismatch")
        attempt.update({
            "state": "RAW_SEALED_BEFORE_PARSE",
            "response_entity_received": True,
            "http_status": sealed.http_status,
            "entity_sha256": sealed.entity_sha256,
            "entity_bytes": sealed.entity_bytes,
            "object_key": sealed.object_key,
            "s3_version_id": sealed.version_id,
            "s3_etag": sealed.etag,
        })
        if not any(
            row.get("s3_object_key") == sealed.object_key
            for row in checkpoint["raw_index"]
        ):
            raw_record = _current_raw_record(
                bindings, attempt, sealed, reconciled=reconciled
            )
            checkpoint["raw_index"].append(raw_record)
            checkpoint["raw_entity_bytes"] += sealed.entity_bytes
            checkpoint["remote_raw_custody_writes"] += 1
            checkpoint["response_entities_received"] += 1
            status = str(sealed.http_status)
            checkpoint["http_status_counts"][status] = (
                checkpoint["http_status_counts"].get(status, 0) + 1
            )
            result_code = raw_record["provider_result_code"]
            checkpoint["provider_result_code_counts"][result_code] = (
                checkpoint["provider_result_code_counts"].get(result_code, 0)
                + 1
            )
        save()

    def acquire_page(
        bas_dt: str, page_no: int, *, attempt_limit: int
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        while True:
            prior = _attempts_for(checkpoint, bas_dt, page_no)
            latest = prior[-1] if prior else None
            sealed: SealedEntity | None = None
            if latest and latest["state"] in {
                "PARSE_OR_PROTOCOL_BLOCKED_AFTER_CUSTODY",
                "NONRETRYABLE_HTTP_ENTITY_CUSTODIED",
            }:
                raise sa.SourceProtocolError(
                    "terminal Finance entity already custodied"
                )
            if latest and latest["state"] == "RESERVED_WRITE_AHEAD":
                if latest.get("provider_call_started") is not True:
                    latest["state"] = "RESERVATION_SPENT_WITHOUT_DURABLE_CALL_START"
                    checkpoint["no_entity_attempts"] += 1
                    save()
                    if len(prior) >= attempt_limit:
                        raise NoEntityTransportError("Finance reservation lacks durable call start")
                    continue
                durable_call_revision = checkpoint["checkpoint_revision"]
                durable_call_token_sha256 = _sha256(str(token).encode("utf-8"))
                if (
                    ("provider_call_checkpoint_revision" in latest
                     and latest.get("provider_call_checkpoint_revision") != durable_call_revision)
                    or ("provider_call_checkpoint_token_sha256" in latest
                        and latest.get("provider_call_checkpoint_token_sha256")
                            != durable_call_token_sha256)
                ):
                    raise sa.CheckpointConflictError(
                        "durable provider-call marker checkpoint shifted"
                    )
                latest["provider_call_checkpoint_revision"] = durable_call_revision
                latest["provider_call_checkpoint_token_sha256"] = durable_call_token_sha256
                sealed = custody.find_existing_by_prefix(
                    latest["raw_object_prefix"], latest
                )
                if sealed is None:
                    latest["state"] = "RESERVATION_SPENT_NO_REMOTE_ENTITY_ON_RESUME"
                    checkpoint["no_entity_attempts"] += 1
                    save()
                    if len(prior) >= attempt_limit:
                        raise NoEntityTransportError(
                            "Finance reservation exhausted without entity"
                        )
                    continue
                persist_sealed(latest, sealed, reconciled=True)
            elif latest and latest["state"] in {
                "RAW_SEALED_BEFORE_PARSE", "PARSED_200",
                "RETRYABLE_HTTP_ENTITY_CUSTODIED",
            }:
                if (
                    latest["state"] == "RETRYABLE_HTTP_ENTITY_CUSTODIED"
                    and len(prior) >= attempt_limit
                ):
                    raise sa.SourceTransportError(
                        "Finance retryable entity exhausted attempts"
                    )
                if latest["state"] != "RETRYABLE_HTTP_ENTITY_CUSTODIED":
                    sealed = custody.read_existing(
                        latest["object_key"], latest["s3_version_id"]
                    )
                    if sealed is None:
                        raise RemoteCustodyError(
                            "successor checkpoint raw entity missing"
                        )
                    _assert_checkpoint_entity_readback(latest, sealed)
                    sa.assert_no_secret(sealed.body, secrets)

            if sealed is None:
                attempt = reserve(
                    bas_dt, page_no, attempt_limit=attempt_limit
                )
                # Close the durable reservation / KST-midnight TOCTOU window.
                # A failed recheck leaves the reservation spent and starts no call.
                _assert_quota_day(bindings, clock)
                assert_self_deadline()
                call_started_at = _iso_utc(clock)
                if not_after_utc is not None and datetime.fromisoformat(call_started_at).astimezone(timezone.utc) >= not_after_utc.astimezone(timezone.utc):
                    raise SelfDeadlineExceededError("Finance call start crossed absolute not-after")
                attempt["provider_call_started"] = True
                attempt["provider_call_started_at_utc"] = call_started_at
                attempt["reservation_checkpoint_revision"] = checkpoint["checkpoint_revision"]
                attempt["reservation_checkpoint_token_sha256"] = _sha256(str(token).encode("utf-8"))
                attempt["execution_claim_version_id"] = evidence.version_id
                attempt["execution_claim_content_sha256"] = evidence.content_sha256
                if bas_dt == "20240131" and page_no == 1:
                    checkpoint["page_1_revalidation"]["fresh_calls_started"] += 1
                checkpoint["provider_api_network_attempts"] += 1
                save()
                attempt["provider_call_checkpoint_revision"] = checkpoint["checkpoint_revision"]
                attempt["provider_call_checkpoint_token_sha256"] = _sha256(str(token).encode("utf-8"))
                params = sa.finance_request_params(
                    bas_dt, page_no, REQUEST_PAGE_SIZE
                )
                try:
                    _assert_quota_day(bindings, clock)
                    assert_self_deadline()
                    response = transport.fetch_once(params)
                except NoEntityTransportError:
                    attempt["state"] = "NO_RESPONSE_ENTITY_RESERVATION_SPENT"
                    checkpoint["no_entity_attempts"] += 1
                    save()
                    if len(_attempts_for(checkpoint, bas_dt, page_no)) >= attempt_limit:
                        raise
                    sleep_fn(0.0)
                    continue
                if not isinstance(response, TransportResponse):
                    raise Page100PilotError("invalid Finance transport response")
                marker_time = attempt.get("provider_call_started_at_utc")
                if not _valid_response_timing(
                    marker_time, response.acquired_at_utc,
                    response.acquired_at_utc, bindings.quota_day_kst,
                    crossed=False,
                ):
                    raise sa.QuotaBoundaryError("Finance socket opened outside the frozen acquisition window")
                response_received_at = _iso_utc(clock)
                response_received_time = datetime.fromisoformat(response_received_at).astimezone(timezone.utc)
                response_crossed = (
                    response_received_time.astimezone(sa.KST).date().isoformat()
                    != bindings.quota_day_kst
                )
                if not _valid_response_timing(
                    marker_time, response.acquired_at_utc,
                    response_received_at, bindings.quota_day_kst,
                    crossed=response_crossed,
                ):
                    raise Page100PilotError("Finance response timing lineage invalid")
                attempt["socket_opened_at_utc"] = response.acquired_at_utc
                attempt["response_received_at_utc"] = response_received_at
                attempt["response_crossed_quota_day"] = response_crossed
                sa.assert_no_secret(response.body, secrets)
                digest = _sha256(response.body)
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
                    "runtime-lock-id": bindings.runtime_lock_id,
                    "pilot-run-id": bindings.pilot_run_id,
                    "quota-day-kst": bindings.quota_day_kst,
                    "provider-call-started-at-utc": attempt["provider_call_started_at_utc"],
                    "socket-opened-at-utc": attempt["socket_opened_at_utc"],
                    "response-received-at-utc": attempt["response_received_at_utc"],
                    "reservation-checkpoint-revision": str(attempt["reservation_checkpoint_revision"]),
                    "reservation-checkpoint-token-sha256": attempt["reservation_checkpoint_token_sha256"],
                    "provider-call-checkpoint-revision": str(attempt["provider_call_checkpoint_revision"]),
                    "provider-call-checkpoint-token-sha256": attempt["provider_call_checkpoint_token_sha256"],
                    "execution-claim-version-id": attempt["execution_claim_version_id"],
                    "execution-claim-content-sha256": attempt["execution_claim_content_sha256"],
                }
                sealed = custody.seal_and_readback(
                    object_key, response.body, metadata
                )
                persist_sealed(attempt, sealed, reconciled=False)
                latest = attempt

            assert latest is not None and sealed is not None
            if latest.get("response_crossed_quota_day") is True:
                raise sa.QuotaBoundaryError(
                    "Finance response crossed frozen KST quota day after raw custody"
                )
            if sealed.http_status == 429 or 500 <= sealed.http_status <= 599:
                latest["state"] = "RETRYABLE_HTTP_ENTITY_CUSTODIED"
                save()
                if len(_attempts_for(checkpoint, bas_dt, page_no)) >= attempt_limit:
                    raise sa.SourceTransportError(
                        "Finance retryable entity exhausted attempts"
                    )
                sleep_fn(0.0)
                continue
            if sealed.http_status != 200:
                latest["state"] = "NONRETRYABLE_HTTP_ENTITY_CUSTODIED"
                save()
                raise sa.SourceTransportError(
                    "Finance non-success entity custodied"
                )
            if not latest.get("date_echo_telemetry_recorded"):
                echo = _date_echo_observation(sealed.body, bas_dt)
                latest["date_echo_telemetry_recorded"] = True
                if echo is None:
                    latest["date_echo_observation"] = "UNKNOWN_UNINSTRUMENTED"
                    checkpoint["date_echo_uninstrumented_entities"] += 1
                else:
                    matches, mismatches = echo
                    latest["date_echo_observation"] = {
                        "match_rows": matches,
                        "mismatch_rows": mismatches,
                    }
                    checkpoint["date_echo_match_rows"] += matches
                    checkpoint["date_echo_mismatch_rows"] += mismatches
                save()
                if echo is not None and echo[1] > 0:
                    latest["state"] = "PARSE_OR_PROTOCOL_BLOCKED_AFTER_CUSTODY"
                    record_pagination_drift(
                        "DATE_ECHO_MISMATCH",
                        bas_dt,
                        page_no,
                        mismatch_rows=echo[1],
                    )
                    raise sa.SourceProtocolError("Finance item basDt mismatch")
            try:
                page = sa.finance_entity_to_page(
                    sealed.body,
                    expected_bas_dt=bas_dt,
                    expected_page_no=page_no,
                )
            except Exception:
                latest["state"] = "PARSE_OR_PROTOCOL_BLOCKED_AFTER_CUSTODY"
                record_pagination_drift(
                    "ENTITY_PROTOCOL_REJECTION", bas_dt, page_no
                )
                raise
            if page["page_size"] != REQUEST_PAGE_SIZE:
                latest["state"] = "PARSE_OR_PROTOCOL_BLOCKED_AFTER_CUSTODY"
                record_pagination_drift(
                    "PAGE_SIZE_SHIFT",
                    bas_dt,
                    page_no,
                    expected=REQUEST_PAGE_SIZE,
                    observed=page["page_size"],
                )
                raise sa.SourceProtocolError("Finance returned page size shifted")
            latest["state"] = "PARSED_200"
            save()
            return page, latest

    def initialize_page_one(
        current: dict[str, Any], page: Mapping[str, Any], attempt: Mapping[str, Any]
    ) -> None:
        total = int(page["total_count"])
        telemetry = _page_cap_telemetry(
            current["basDt"], total, historical_evidence=False
        )
        if telemetry["expected_pages"] > MAX_PAGES_PER_DATE:
            checkpoint["page_cap_telemetry"] = telemetry
            save()
            raise PageCeilingError(telemetry)
        items = list(page["items"])
        if len(items) > REQUEST_PAGE_SIZE or len(items) > total:
            raise sa.SourceProtocolError("Finance page-1 item count invalid")
        if not items and len(items) < total:
            raise sa.SourceProtocolError("Finance empty intermediate page")
        if telemetry["expected_pages"] > 1 and len(items) != REQUEST_PAGE_SIZE:
            record_pagination_drift(
                "UNDERFILLED_INTERMEDIATE_PAGE", current["basDt"], 1,
                expected_item_count=REQUEST_PAGE_SIZE,
                observed_item_count=len(items),
            )
            raise sa.SourceProtocolError("Finance underfilled intermediate page")
        fingerprint = _sha256(sa.canonical_json_bytes(items))
        current.update({
            "page_1_identity": sa.pagination_page_1_identity(page),
            "total_count": total,
            "page_size": REQUEST_PAGE_SIZE,
            "expected_pages": telemetry["expected_pages"],
            "page_fingerprints": [fingerprint] if items else [],
            "cumulative_item_count": len(items),
        })
        current["validated_pages"].append({
            "page_no": 1,
            "item_count": len(items),
            "cumulative_item_count": len(items),
            "page_fingerprint_sha256": fingerprint,
            "entity_sha256": attempt["entity_sha256"],
            "s3_version_id": attempt["s3_version_id"],
        })
        new_conflicts = _observe_items(checkpoint, items)
        save()
        if new_conflicts:
            raise IssuerIdentityConflictError(
                "Finance issuer identity conflict observed"
            )

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
                }
                checkpoint["current_date"] = current
                save()
            elif current.get("basDt") != bas_dt:
                raise sa.CheckpointConflictError(
                    "successor current date is not ordered next"
                )

            if not current["validated_pages"]:
                is_predecessor_page = bas_dt == "20240131"
                page_one, attempt = acquire_page(
                    bas_dt,
                    1,
                    attempt_limit=(
                        MAX_FRESH_PREDECESSOR_PAGE1_REVALIDATIONS
                        if is_predecessor_page else MAX_ATTEMPTS_PER_PAGE
                    ),
                )
                if is_predecessor_page:
                    fresh_identity = sa.pagination_page_1_identity(page_one)
                    revalidation = checkpoint["page_1_revalidation"]
                    revalidation.update({
                        "fresh_raw_sha256": attempt["entity_sha256"],
                        "fresh_semantic_identity": fresh_identity,
                        "fresh_total_count": page_one["total_count"],
                        "raw_digest_match": (
                            attempt["entity_sha256"]
                            == revalidation["historical_raw_sha256"]
                        ),
                        "page_identity_match": (
                            fresh_identity
                            == revalidation["historical_semantic_identity"]
                        ),
                        "total_count_match": (
                            page_one["total_count"]
                            == revalidation["historical_total_count"]
                        ),
                    })
                    revalidation["all_invariants_pass"] = all(
                        revalidation[name]
                        for name in (
                            "raw_digest_match",
                            "page_identity_match",
                            "total_count_match",
                        )
                    )
                    if not revalidation["all_invariants_pass"]:
                        revalidation["state"] = "BLOCKED_THREE_WAY_SHIFT"
                        record_pagination_drift(
                            "PREDECESSOR_PAGE_1_THREE_WAY_SHIFT",
                            bas_dt,
                            1,
                            raw_digest_match=revalidation["raw_digest_match"],
                            page_identity_match=revalidation["page_identity_match"],
                            total_count_match=revalidation["total_count_match"],
                        )
                        raise sa.SourceProtocolError(
                            "Finance predecessor page-1 three-way invariant shifted"
                        )
                    revalidation["state"] = "COMPLETE_MATCH"
                    save()
                initialize_page_one(current, page_one, attempt)

            next_page = len(current["validated_pages"]) + 1
            while next_page <= current["expected_pages"]:
                page, attempt = acquire_page(
                    bas_dt, next_page, attempt_limit=MAX_ATTEMPTS_PER_PAGE
                )
                if (
                    page["total_count"] != current["total_count"]
                    or page["page_size"] != current["page_size"]
                ):
                    record_pagination_drift(
                        "PAGINATION_SNAPSHOT_SHIFT",
                        bas_dt,
                        next_page,
                        expected_total_count=current["total_count"],
                        observed_total_count=page["total_count"],
                        expected_page_size=current["page_size"],
                        observed_page_size=page["page_size"],
                    )
                    raise sa.SourceProtocolError(
                        "Finance pagination snapshot shifted"
                    )
                items = list(page["items"])
                fingerprint = _sha256(sa.canonical_json_bytes(items))
                if items and fingerprint in current["page_fingerprints"]:
                    record_pagination_drift(
                        "REPEATED_WHOLE_PAGE", bas_dt, next_page
                    )
                    raise sa.SourceProtocolError("Finance repeated whole page")
                cumulative = current["cumulative_item_count"] + len(items)
                if len(items) > REQUEST_PAGE_SIZE or cumulative > current["total_count"]:
                    record_pagination_drift(
                        "PAGINATION_COUNT_EXCEEDED", bas_dt, next_page
                    )
                    raise sa.SourceProtocolError("Finance pagination count exceeded")
                if not items and cumulative < current["total_count"]:
                    record_pagination_drift(
                        "EMPTY_INTERMEDIATE_PAGE", bas_dt, next_page
                    )
                    raise sa.SourceProtocolError("Finance empty intermediate page")
                if (
                    next_page < current["expected_pages"]
                    and len(items) != REQUEST_PAGE_SIZE
                ):
                    record_pagination_drift(
                        "UNDERFILLED_INTERMEDIATE_PAGE", bas_dt, next_page,
                        expected_item_count=REQUEST_PAGE_SIZE,
                        observed_item_count=len(items),
                    )
                    raise sa.SourceProtocolError(
                        "Finance underfilled intermediate page"
                    )
                if items:
                    current["page_fingerprints"].append(fingerprint)
                current["cumulative_item_count"] = cumulative
                current["validated_pages"].append({
                    "page_no": next_page,
                    "item_count": len(items),
                    "cumulative_item_count": cumulative,
                    "page_fingerprint_sha256": fingerprint,
                    "entity_sha256": attempt["entity_sha256"],
                    "s3_version_id": attempt["s3_version_id"],
                })
                new_conflicts = _observe_items(checkpoint, items)
                save()
                if new_conflicts:
                    raise IssuerIdentityConflictError(
                        "Finance issuer identity conflict observed"
                    )
                next_page += 1

            if current["cumulative_item_count"] != current["total_count"]:
                record_pagination_drift(
                    "PAGINATION_TOTAL_DID_NOT_CLOSE",
                    bas_dt,
                    len(current["validated_pages"]),
                )
                raise sa.SourceProtocolError("Finance pagination total did not close")
            checkpoint["date_results"].append({
                "basDt": bas_dt,
                "state": "DATE_COMPLETE",
                "page_count": len(current["validated_pages"]),
                "item_count": current["cumulative_item_count"],
                "total_count": current["total_count"],
                "page_1_identity": current["page_1_identity"],
                "resume_page_1_revalidations": (
                    1 if bas_dt == "20240131" else 0
                ),
                "valid_empty": current["total_count"] == 0,
            })
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
        raise
    except Exception as exc:
        checkpoint["state"] = "BLOCKED"
        checkpoint["last_error_class"] = type(exc).__name__
        save()
        raise


class BoundedUrlLibFinanceTransport:
    """One socket attempt with an immediately-adjacent acquisition guard."""

    MAX_ENTITY_BYTES = 2_000_000

    def __init__(
        self,
        secret: str,
        *,
        quota_day_kst: str,
        not_after_utc: datetime,
        deadline_monotonic: float,
        timeout_seconds: float = 20.0,
        opener: Any | None = None,
        clock: Callable[[], datetime] = lambda: datetime.now(timezone.utc),
        monotonic_fn: Callable[[], float] = time.monotonic,
    ) -> None:
        self.secret = sa.validate_decoded_secret(
            legacy.FINANCE_SECRET_ENV, secret
        )
        if (
            quota_day_kst != "2026-08-30"
            or not isinstance(not_after_utc, datetime)
            or not_after_utc.tzinfo is None
            or not_after_utc.astimezone(timezone.utc) != LIVE_NOT_AFTER_UTC
            or type(deadline_monotonic) not in {int, float}
            or not math.isfinite(float(deadline_monotonic))
            or type(timeout_seconds) not in {int, float}
            or not math.isfinite(float(timeout_seconds))
            or not 0 < float(timeout_seconds) <= 20.0
        ):
            raise BindingError("invalid bounded Finance transport configuration")
        self.quota_day_kst = quota_day_kst
        self.not_after_utc = not_after_utc.astimezone(timezone.utc)
        self.deadline_monotonic = float(deadline_monotonic)
        self.timeout_seconds = float(timeout_seconds)
        self.opener = opener or urllib.request.build_opener(sa.NoRedirect())
        self.clock = clock
        self.monotonic_fn = monotonic_fn

    def _socket_open_stamp(self) -> str:
        if self.monotonic_fn() >= self.deadline_monotonic:
            raise SelfDeadlineExceededError(
                "Finance socket open crossed monotonic self-deadline"
            )
        observed = self.clock()
        if not isinstance(observed, datetime) or observed.tzinfo is None:
            raise BindingError("Finance transport clock must be timezone-aware")
        observed_utc = observed.astimezone(timezone.utc)
        if observed_utc >= self.not_after_utc:
            raise SelfDeadlineExceededError(
                "Finance socket open crossed absolute not-after"
            )
        if observed_utc.astimezone(sa.KST).date().isoformat() != self.quota_day_kst:
            raise sa.QuotaBoundaryError(
                "Finance socket open crossed frozen KST quota day"
            )
        return observed_utc.isoformat()

    def _remaining_body_timeout(self) -> float:
        remaining = self.deadline_monotonic - self.monotonic_fn()
        if remaining <= 0.001:
            raise NoEntityTransportError(
                "Finance response body crossed monotonic self-deadline"
            )
        return min(self.timeout_seconds, remaining)

    @staticmethod
    def _set_stream_timeout(stream: Any, timeout_seconds: float) -> None:
        queue = [stream]
        seen: set[int] = set()
        for _ in range(16):
            if not queue:
                break
            current = queue.pop(0)
            if current is None or id(current) in seen:
                continue
            seen.add(id(current))
            setter = getattr(current, "settimeout", None)
            if callable(setter):
                setter(timeout_seconds)
                return
            for name in ("fp", "raw", "_sock"):
                child = getattr(current, name, None)
                if child is not None:
                    queue.append(child)

    def _read_bounded_entity(self, stream: Any) -> bytes:
        chunks: list[bytes] = []
        observed = 0
        while True:
            remaining_timeout = self._remaining_body_timeout()
            self._set_stream_timeout(stream, remaining_timeout)
            remaining_bytes = self.MAX_ENTITY_BYTES + 1 - observed
            if remaining_bytes <= 0:
                raise Page100PilotError(
                    "Finance response entity exceeded the bounded byte ceiling"
                )
            read_size = min(65_536, remaining_bytes)
            read_one = getattr(stream, "read1", None)
            reader = read_one if callable(read_one) else stream.read
            chunk = reader(read_size)
            if not isinstance(chunk, bytes):
                raise NoEntityTransportError(
                    "Finance response body reader returned a non-byte entity"
                )
            if not chunk:
                return b"".join(chunks)
            chunks.append(chunk)
            observed += len(chunk)
            if observed > self.MAX_ENTITY_BYTES:
                raise Page100PilotError(
                    "Finance response entity exceeded the bounded byte ceiling"
                )

    def fetch_once(self, params: Mapping[str, str]) -> TransportResponse:
        url = sa.encoded_query(sa.FINANCE_URL, params, self.secret)
        request = urllib.request.Request(
            url,
            headers={
                "Accept": "application/json",
                "Accept-Encoding": "identity",
                "User-Agent": "AAA-M3Top3-Finance-Page100-G6/1.0",
            },
        )
        socket_opened_at = self._socket_open_stamp()
        try:
            response = self.opener.open(request, timeout=self.timeout_seconds)
            status = int(getattr(response, "status", response.getcode()))
            body = self._read_bounded_entity(response)
            headers = {
                str(key).lower(): str(value)
                for key, value in response.headers.items()
                if str(key).lower() in legacy.SAFE_RESPONSE_HEADERS
            }
        except urllib.error.HTTPError as exc:
            status = int(exc.code)
            body = self._read_bounded_entity(exc)
            headers = {
                str(key).lower(): str(value)
                for key, value in exc.headers.items()
                if str(key).lower() in legacy.SAFE_RESPONSE_HEADERS
            }
        except (urllib.error.URLError, TimeoutError, OSError):
            raise NoEntityTransportError(
                "Finance transport ended without response entity"
            ) from None
        return TransportResponse(
            body=body,
            http_status=status,
            safe_headers=headers,
            acquired_at_utc=socket_opened_at,
        )


class S3Page100ObjectStore(legacy.S3CliObjectStore):
    """Exact successor namespace plus version-bound predecessor readback."""

    def __init__(
        self,
        bindings: SuccessorBindings,
        **kwargs: Any,
    ) -> None:
        _validate_bindings(bindings)
        super().__init__(**kwargs)
        self.bindings = bindings
        self.checkpoint_key = checkpoint_object_key(bindings)
        self.claim_key = execution_claim_object_key(bindings)

    def compare_and_swap(
        self, value: Mapping[str, Any], expected_token: str | None
    ) -> str:
        """Version-aware CAS with exact-payload recovery after uncertain writes."""
        if not isinstance(value, Mapping):
            raise RemoteCustodyError("invalid checkpoint value")
        payload = sa.canonical_json_bytes(dict(value))

        def token_from(
            readback: tuple[bytes, dict[str, Any]] | None,
            *, require_payload: bool,
        ) -> tuple[bytes, str] | None:
            if readback is None:
                return None
            body, meta = readback
            etag = str(meta.get("ETag", ""))
            version_id = str(meta.get("VersionId", ""))
            sse = str(meta.get("ServerSideEncryption", ""))
            user = meta.get("Metadata", {})
            if (
                not etag
                or not version_id
                or sse != "AES256"
                or str(meta.get("ContentType", "")) != "application/json"
                or not isinstance(user, Mapping)
                or {str(k): str(v) for k, v in user.items()}
                   != {"sha256": _sha256(body)}
            ):
                raise RemoteCustodyError("checkpoint CAS evidence incomplete")
            if require_payload and body != payload:
                raise sa.CheckpointConflictError("checkpoint CAS exact payload mismatch")
            return body, self._checkpoint_token(etag, version_id, sse)

        current = token_from(self._get(self.checkpoint_key), require_payload=False)
        if current is not None and current[0] == payload:
            return current[1]
        if expected_token is None:
            if current is not None:
                raise sa.CheckpointConflictError("checkpoint create found existing value")
            condition = ["--if-none-match", "*"]
        else:
            expected_etag = self._checkpoint_etag(expected_token)
            if current is None or current[1] != expected_token:
                raise sa.CheckpointConflictError("checkpoint version-aware CAS token shifted")
            condition = ["--if-match", expected_etag]

        with tempfile.NamedTemporaryFile(prefix="m3top3-page100-cas-", delete=False) as handle:
            target = Path(handle.name)
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            try:
                result = self._invoke(
                    self._base("put-object") + [
                        "--key", self.checkpoint_key,
                        "--body", str(target),
                        "--content-type", "application/json",
                        "--server-side-encryption", "AES256",
                        "--metadata", f"sha256={_sha256(payload)}",
                    ] + condition
                )
                assert result is not None
                result_version = str(result.get("VersionId", ""))
                if not result_version:
                    raise RemoteCustodyError("checkpoint CAS missing VersionId")
                recovered = token_from(
                    self._get(self.checkpoint_key, version_id=result_version),
                    require_payload=True,
                )
                if recovered is None:
                    raise RemoteCustodyError("checkpoint CAS readback missing")
                latest = token_from(self._get(self.checkpoint_key), require_payload=True)
                if latest is None or latest[1] != recovered[1]:
                    raise sa.CheckpointConflictError("checkpoint CAS result is not latest")
                return recovered[1]
            except Exception as write_error:
                try:
                    recovered = token_from(
                        self._get(self.checkpoint_key), require_payload=True
                    )
                except Exception:
                    raise write_error
                if recovered is None or recovered[1] == expected_token:
                    raise write_error
                return recovered[1]
        finally:
            target.unlink(missing_ok=True)

    def checkpoint_reference(
        self, checkpoint: Mapping[str, Any], token: str | None
    ) -> Mapping[str, Any]:
        if token is None:
            raise RemoteCustodyError("terminal checkpoint token missing")
        try:
            parts = json.loads(token)
        except (TypeError, json.JSONDecodeError):
            raise RemoteCustodyError("terminal checkpoint token invalid") from None
        if (
            not isinstance(parts, dict)
            or set(parts) != {"etag", "version_id", "sse"}
            or parts.get("sse") != "AES256"
            or not all(isinstance(parts.get(key), str) and parts.get(key) for key in parts)
        ):
            raise RemoteCustodyError("terminal checkpoint token incomplete")
        payload = sa.canonical_json_bytes(dict(checkpoint))
        readback = self._get(self.checkpoint_key, version_id=parts["version_id"])
        if readback is None:
            raise RemoteCustodyError("terminal checkpoint version missing")
        body, meta = readback
        user = meta.get("Metadata", {})
        if (
            body != payload
            or str(meta.get("VersionId", "")) != parts["version_id"]
            or str(meta.get("ETag", "")) != parts["etag"]
            or str(meta.get("ServerSideEncryption", "")) != "AES256"
            or str(meta.get("ContentType", "")) != "application/json"
            or not isinstance(user, Mapping)
            or {str(k): str(v) for k, v in user.items()}
               != {"sha256": _sha256(payload)}
            or checkpoint.get("state") != "COMPLETE"
            or type(checkpoint.get("checkpoint_revision")) is not int
        ):
            raise RemoteCustodyError("terminal checkpoint exact version mismatch")
        latest = self._get(self.checkpoint_key)
        if latest is None or str(latest[1].get("VersionId", "")) != parts["version_id"]:
            raise RemoteCustodyError("terminal checkpoint version is not latest")
        return {
            "object_key": self.checkpoint_key,
            "version_id": parts["version_id"],
            "etag": parts["etag"],
            "sha256": _sha256(payload),
            "server_side_encryption": "AES256",
            "checkpoint_revision": checkpoint["checkpoint_revision"],
            "state": "COMPLETE",
        }

    def _sealed(
        self,
        body: bytes,
        object_key: str,
        metadata: Mapping[str, Any],
        *,
        write_precondition: str,
    ) -> SealedEntity:
        user_metadata = metadata.get("Metadata")
        if not isinstance(user_metadata, Mapping):
            raise RemoteCustodyError("raw entity metadata missing")
        digest = _sha256(body)
        if str(user_metadata.get("sha256", "")) != digest:
            raise RemoteCustodyError("raw entity metadata digest mismatch")
        try:
            status = int(user_metadata["http-status"])
        except (KeyError, TypeError, ValueError):
            raise RemoteCustodyError("raw entity status metadata invalid") from None
        version_id = str(metadata.get("VersionId", ""))
        etag = str(metadata.get("ETag", ""))
        sse = str(metadata.get("ServerSideEncryption", ""))
        if not version_id or not etag or sse != "AES256":
            raise RemoteCustodyError("raw entity version/SSE/ETag evidence missing")
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
            write_precondition=write_precondition,
            http_status=status,
            acquired_at_utc=str(user_metadata.get("acquired-at-utc", "")),
        )

    def _assert_single_version(self, object_key: str, version_id: str) -> None:
        payload = self._invoke(
            self._base("list-object-versions")
            + ["--prefix", object_key, "--max-keys", "2"]
        )
        assert payload is not None
        versions = payload.get("Versions", [])
        markers = payload.get("DeleteMarkers", [])
        if (
            payload.get("IsTruncated") is True
            or not isinstance(versions, list)
            or not isinstance(markers, list)
            or markers
            or len(versions) != 1
            or versions[0].get("Key") != object_key
            or versions[0].get("VersionId") != version_id
            or versions[0].get("IsLatest") is not True
        ):
            raise RemoteCustodyError("create-once S3 version history mismatch")

    def acquire_execution_claim(
        self, claim: Mapping[str, Any]
    ) -> ExecutionClaimEvidence:
        """Create once, or accept only the exact same run/attempt payload."""
        payload = sa.canonical_json_bytes(dict(claim))
        digest = _sha256(payload)

        def evidence_from(readback: tuple[bytes, dict[str, Any]] | None) -> ExecutionClaimEvidence | None:
            if readback is None:
                return None
            body, meta = readback
            version_id = str(meta.get("VersionId", ""))
            etag = str(meta.get("ETag", ""))
            sse = str(meta.get("ServerSideEncryption", ""))
            user = meta.get("Metadata", {})
            if (
                body != payload
                or not version_id
                or not etag
                or sse != "AES256"
                or str(meta.get("ContentType", "")) != "application/json"
                or not isinstance(user, Mapping)
                or {str(key): str(value) for key, value in user.items()}
                   != {"sha256": digest}
            ):
                raise sa.CheckpointConflictError("execution claim belongs to another writer")
            self._assert_single_version(self.claim_key, version_id)
            return ExecutionClaimEvidence(
                object_key=self.claim_key,
                content_sha256=digest,
                version_id=version_id,
                etag=etag,
                server_side_encryption=sse,
                write_precondition="IF_NONE_MATCH_STAR",
                writer_id=str(claim.get("writer_id", "")),
            )

        existing = evidence_from(self._get(self.claim_key))
        if existing is not None:
            return existing
        with tempfile.NamedTemporaryFile(prefix="m3top3-page100-claim-", delete=False) as handle:
            target = Path(handle.name)
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            try:
                result = self._invoke(
                    self._base("put-object") + [
                        "--key", self.claim_key,
                        "--body", str(target),
                        "--content-type", "application/json",
                        "--server-side-encryption", "AES256",
                        "--if-none-match", "*",
                        "--metadata", f"sha256={digest}",
                    ]
                )
                assert result is not None
                created_version = str(result.get("VersionId", ""))
                if not created_version:
                    raise RemoteCustodyError("execution claim create missing VersionId")
                recovered = evidence_from(
                    self._get(self.claim_key, version_id=created_version)
                )
                if recovered is None or recovered.version_id != created_version:
                    raise RemoteCustodyError("execution claim readback mismatch")
                return recovered
            except Exception as write_error:
                try:
                    recovered = evidence_from(self._get(self.claim_key))
                except Exception:
                    raise write_error
                if recovered is None:
                    raise write_error
                return recovered
        finally:
            target.unlink(missing_ok=True)

    def read_historical(
        self, binding: HistoricalPageOneBinding
    ) -> SealedEntity | None:
        if binding != self.bindings.predecessor.page_one:
            raise HistoricalEvidenceError("historical page-1 binding shifted")
        result = self._get(binding.object_key, version_id=binding.version_id)
        if result is None:
            return None
        body, metadata = result
        sealed = self._sealed(
            body,
            binding.object_key,
            metadata,
            write_precondition="IF_NONE_MATCH_STAR",
        )
        user = metadata.get("Metadata", {})
        expected = {
            "runtime-lock-id": PREDECESSOR_RUNTIME_LOCK_ID,
            "pilot-run-id": PREDECESSOR_PILOT_RUN_ID,
            "quota-day-kst": "2026-08-29",
            "bas-dt": "20240131",
            "page-no": "1",
            "attempt": "1",
            "request-id": deterministic_request_id("20240131", 1),
        }
        if (
            any(str(user.get(key, "")) != value for key, value in expected.items())
            or sealed.version_id != binding.version_id
            or sealed.entity_sha256 != binding.entity_sha256
            or sealed.entity_bytes != binding.entity_bytes
            or sealed.server_side_encryption != binding.server_side_encryption
            or sealed.http_status != 200
        ):
            raise HistoricalEvidenceError(
                "historical page-1 remote lineage shifted"
            )
        return sealed

    def _read_current(
        self,
        object_key: str,
        version_id: str | None = None,
        expected_lineage: Mapping[str, Any] | None = None,
    ) -> SealedEntity | None:
        namespace = (
            RAW_KEY_PREFIX + "_pilot_generation/"
            + f"runtime_lock_id={RUNTIME_LOCK_ID}/"
            + f"pilot_run_id={PILOT_RUN_ID}/"
        )
        pattern = re.compile(
            re.escape(namespace + sa.FINANCE_OPERATION)
            + r"/quota_day_kst=([^/]+)/request_id=([0-9a-f]{64})/"
            + r"attempt=([12])/sha256=([0-9a-f]{64})\.entity"
        )
        matched = pattern.fullmatch(object_key)
        if matched is None:
            raise RemoteCustodyError("successor raw lineage key invalid")
        result = self._get(object_key, version_id=version_id)
        if result is None:
            return None
        body, metadata = result
        sealed = self._sealed(
            body, object_key, metadata, write_precondition="IF_NONE_MATCH_STAR"
        )
        quota_day, request_id, attempt_text, key_digest = matched.groups()
        user = metadata.get("Metadata", {})
        if not isinstance(user, Mapping):
            raise RemoteCustodyError("successor raw metadata missing")
        user = {str(key): str(value) for key, value in user.items()}
        try:
            bas_dt = str(user["bas-dt"])
            page_no = int(user["page-no"])
        except (KeyError, TypeError, ValueError):
            raise RemoteCustodyError("successor raw request metadata invalid") from None
        required = {
            "sha256", "http-status", "acquired-at-utc", "request-id",
            "bas-dt", "page-no", "attempt", "runtime-lock-id",
            "pilot-run-id", "quota-day-kst", "provider-call-started-at-utc",
            "socket-opened-at-utc", "response-received-at-utc",
            "reservation-checkpoint-revision", "reservation-checkpoint-token-sha256",
            "provider-call-checkpoint-revision", "provider-call-checkpoint-token-sha256",
            "execution-claim-version-id", "execution-claim-content-sha256",
        }
        expected_claim_hash = _sha256(sa.canonical_json_bytes(_execution_claim(
            self.bindings,
            f"github-run:{self.bindings.github_run_id}:attempt:{self.bindings.github_run_attempt}",
        )))
        if (
            set(user) != required
            or quota_day != self.bindings.quota_day_kst
            or bas_dt not in PRIMARY_DATES[1:]
            or not 1 <= page_no <= MAX_PAGES_PER_DATE
            or request_id != deterministic_request_id(bas_dt, page_no)
            or user.get("request-id") != request_id
            or user.get("attempt") != attempt_text
            or user.get("runtime-lock-id") != RUNTIME_LOCK_ID
            or user.get("pilot-run-id") != PILOT_RUN_ID
            or user.get("quota-day-kst") != quota_day
            or user.get("execution-claim-content-sha256") != expected_claim_hash
            or _SHA256_RE.fullmatch(user.get("reservation-checkpoint-token-sha256", "")) is None
            or _SHA256_RE.fullmatch(user.get("provider-call-checkpoint-token-sha256", "")) is None
            or not user.get("execution-claim-version-id")
            or not user.get("provider-call-started-at-utc")
            or not user.get("socket-opened-at-utc")
            or not user.get("response-received-at-utc")
            or user.get("acquired-at-utc") != user.get("socket-opened-at-utc")
            or not _valid_response_timing(
                user.get("provider-call-started-at-utc"),
                user.get("socket-opened-at-utc"),
                user.get("response-received-at-utc"),
                quota_day,
                crossed=None,
            )
            or not user.get("reservation-checkpoint-revision", "").isdigit()
            or not user.get("provider-call-checkpoint-revision", "").isdigit()
            or key_digest != sealed.entity_sha256
            or (version_id is not None and sealed.version_id != version_id)
        ):
            raise RemoteCustodyError("successor raw lineage metadata mismatch")
        if expected_lineage is not None:
            try:
                exact = {
                    "request-id": str(expected_lineage["request_id"]),
                    "bas-dt": str(expected_lineage["basDt"]),
                    "page-no": str(expected_lineage["page_no"]),
                    "attempt": str(expected_lineage["attempt"]),
                    "runtime-lock-id": self.bindings.runtime_lock_id,
                    "pilot-run-id": self.bindings.pilot_run_id,
                    "quota-day-kst": self.bindings.quota_day_kst,
                    "provider-call-started-at-utc": str(expected_lineage["provider_call_started_at_utc"]),
                    "reservation-checkpoint-revision": str(expected_lineage["reservation_checkpoint_revision"]),
                    "reservation-checkpoint-token-sha256": str(expected_lineage["reservation_checkpoint_token_sha256"]),
                    "provider-call-checkpoint-revision": str(expected_lineage["provider_call_checkpoint_revision"]),
                    "provider-call-checkpoint-token-sha256": str(expected_lineage["provider_call_checkpoint_token_sha256"]),
                    "execution-claim-version-id": str(expected_lineage["execution_claim_version_id"]),
                    "execution-claim-content-sha256": str(expected_lineage["execution_claim_content_sha256"]),
                }
                expected_prefix = str(expected_lineage["raw_object_prefix"])
            except (KeyError, TypeError, ValueError):
                raise RemoteCustodyError("successor reconciliation lineage incomplete") from None
            if (
                expected_lineage.get("provider_call_started") is not True
                or not object_key.startswith(expected_prefix)
                or any(user.get(key) != value for key, value in exact.items())
            ):
                raise RemoteCustodyError("successor reconciliation lineage mismatch")
        return _with_response_timing(
            sealed, user["response-received-at-utc"]
        )

    def read_existing(
        self, object_key: str, version_id: str | None = None
    ) -> SealedEntity | None:
        return self._read_current(object_key, version_id)

    def find_existing_by_prefix(
        self, object_prefix: str, expected_lineage: Mapping[str, Any]
    ) -> SealedEntity | None:
        required = (
            RAW_KEY_PREFIX + "_pilot_generation/"
            + f"runtime_lock_id={RUNTIME_LOCK_ID}/"
            + f"pilot_run_id={PILOT_RUN_ID}/"
        )
        if not object_prefix.startswith(required):
            raise RemoteCustodyError("successor reconciliation prefix escaped")
        result = self._invoke(
            self._base("list-object-versions")
            + ["--prefix", object_prefix, "--max-keys", "2"]
        )
        assert result is not None
        versions = result.get("Versions", [])
        markers = result.get("DeleteMarkers", [])
        if not isinstance(versions, list) or not isinstance(markers, list):
            raise RemoteCustodyError("successor reconciliation history invalid")
        if not versions and not markers and result.get("IsTruncated") is not True:
            return None
        if (
            result.get("IsTruncated") is True
            or markers
            or len(versions) != 1
            or versions[0].get("IsLatest") is not True
            or not isinstance(versions[0].get("Key"), str)
            or re.fullmatch(
                re.escape(object_prefix) + r"sha256=[0-9a-f]{64}\.entity",
                versions[0]["Key"],
            ) is None
            or not isinstance(versions[0].get("VersionId"), str)
            or not versions[0].get("VersionId")
        ):
            raise RemoteCustodyError("successor reconciliation history is not create-once")
        key = versions[0]["Key"]
        version_id = versions[0]["VersionId"]
        sealed = self._read_current(
            key, version_id=version_id, expected_lineage=expected_lineage
        )
        if sealed is None:
            raise RemoteCustodyError("successor reconciliation version missing")
        self._assert_single_version(key, version_id)
        return sealed

    def seal_and_readback(
        self, object_key: str, body: bytes, metadata: Mapping[str, str]
    ) -> SealedEntity:
        digest = _sha256(body)
        required = {
            "sha256", "http-status", "acquired-at-utc", "request-id",
            "bas-dt", "page-no", "attempt", "runtime-lock-id",
            "pilot-run-id", "quota-day-kst", "provider-call-started-at-utc",
            "socket-opened-at-utc", "response-received-at-utc",
            "reservation-checkpoint-revision", "reservation-checkpoint-token-sha256",
            "provider-call-checkpoint-revision", "provider-call-checkpoint-token-sha256",
            "execution-claim-version-id", "execution-claim-content-sha256",
        }
        safe = {str(key): str(value) for key, value in metadata.items()}
        if set(safe) != required or safe.get("sha256") != digest:
            raise RemoteCustodyError("successor raw metadata incomplete")
        expected_prefix = deterministic_raw_object_prefix(
            self.bindings,
            safe["bas-dt"],
            int(safe["page-no"]),
            int(safe["attempt"]),
        )
        if (
            object_key != canonical_raw_object_key(expected_prefix, digest)
            or safe["request-id"]
            != deterministic_request_id(safe["bas-dt"], int(safe["page-no"]))
            or safe["runtime-lock-id"] != RUNTIME_LOCK_ID
            or safe["pilot-run-id"] != PILOT_RUN_ID
            or safe["quota-day-kst"] != self.bindings.quota_day_kst
            or _SHA256_RE.fullmatch(safe["reservation-checkpoint-token-sha256"]) is None
            or _SHA256_RE.fullmatch(safe["provider-call-checkpoint-token-sha256"]) is None
            or _SHA256_RE.fullmatch(safe["execution-claim-content-sha256"]) is None
            or not safe["execution-claim-version-id"]
            or not safe["provider-call-started-at-utc"]
            or not safe["socket-opened-at-utc"]
            or not safe["response-received-at-utc"]
            or safe["acquired-at-utc"] != safe["socket-opened-at-utc"]
            or not _valid_response_timing(
                safe["provider-call-started-at-utc"],
                safe["socket-opened-at-utc"],
                safe["response-received-at-utc"],
                self.bindings.quota_day_kst,
                crossed=None,
            )
            or not safe["reservation-checkpoint-revision"].isdigit()
            or not safe["provider-call-checkpoint-revision"].isdigit()
        ):
            raise RemoteCustodyError("successor raw metadata lineage shifted")

        def exact_read(version_id: str | None = None) -> SealedEntity | None:
            readback = self._get(object_key, version_id=version_id)
            if readback is None:
                return None
            observed_body, observed_meta = readback
            observed_user = observed_meta.get("Metadata", {})
            if (
                observed_body != body
                or not isinstance(observed_user, Mapping)
                or {str(key): str(value) for key, value in observed_user.items()} != safe
                or str(observed_meta.get("ContentType", "")) != "application/octet-stream"
            ):
                raise sa.CheckpointConflictError("successor raw object belongs to different lineage")
            sealed = self._sealed(
                observed_body, object_key, observed_meta,
                write_precondition="IF_NONE_MATCH_STAR",
            )
            self._assert_single_version(object_key, sealed.version_id)
            return _with_response_timing(
                sealed, safe["response-received-at-utc"]
            )

        existing = exact_read()
        if existing is not None:
            return existing
        with tempfile.NamedTemporaryFile(prefix="m3top3-page100-raw-", delete=False) as handle:
            target = Path(handle.name)
            handle.write(body)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            last_write_error: Exception | None = None
            for write_attempt in range(1, 4):
                try:
                    existing = exact_read()
                    if existing is not None:
                        return existing
                    result = self._invoke(
                        self._base("put-object") + [
                            "--key", object_key,
                            "--body", str(target),
                            "--content-type", "application/octet-stream",
                            "--server-side-encryption", "AES256",
                            "--if-none-match", "*",
                            "--metadata",
                            ",".join(f"{key}={safe[key]}" for key in sorted(safe)),
                        ]
                    )
                    assert result is not None
                    version_id = str(result.get("VersionId", ""))
                    if not version_id:
                        raise RemoteCustodyError("successor raw write missing VersionId")
                    recovered = exact_read(version_id)
                    if recovered is None or recovered.version_id != version_id:
                        raise RemoteCustodyError("successor raw readback mismatch")
                    return recovered
                except Exception as write_error:
                    try:
                        recovered = exact_read()
                    except Exception:
                        recovered = None
                    if recovered is not None:
                        return recovered
                    last_write_error = write_error
                    if write_attempt < 3:
                        time.sleep(float(write_attempt))
            assert last_write_error is not None
            raise last_write_error
        finally:
            target.unlink(missing_ok=True)

    def put_control_artifact(
        self, name: str, body: bytes, content_type: str
    ) -> Mapping[str, str]:
        if name not in {"quota-ledger.jsonl", "raw-index.jsonl", "report.json", "terminal-manifest.json"}:
            raise RemoteCustodyError("successor control artifact name invalid")
        key = self.checkpoint_key.rsplit("/", 1)[0] + "/" + name
        digest = _sha256(body)

        def exact_ref(version_id: str | None = None) -> Mapping[str, str] | None:
            readback = self._get(key, version_id=version_id)
            if readback is None:
                return None
            observed_body, meta = readback
            user = meta.get("Metadata", {})
            observed_version = str(meta.get("VersionId", ""))
            etag = str(meta.get("ETag", ""))
            if (
                observed_body != body
                or not observed_version
                or (version_id is not None and observed_version != version_id)
                or not etag
                or str(meta.get("ServerSideEncryption", "")) != "AES256"
                or str(meta.get("ContentType", "")) != content_type
                or not isinstance(user, Mapping)
                or {str(k): str(v) for k, v in user.items()} != {"sha256": digest}
            ):
                raise sa.CheckpointConflictError("successor control artifact differs")
            self._assert_single_version(key, observed_version)
            return {
                "object_key": key,
                "version_id": observed_version,
                "etag": etag,
                "sha256": digest,
                "server_side_encryption": "AES256",
                "write_precondition": "IF_NONE_MATCH_STAR",
            }

        existing = exact_ref()
        if existing is not None:
            return existing
        with tempfile.NamedTemporaryFile(prefix="m3top3-page100-control-", delete=False) as handle:
            target = Path(handle.name)
            handle.write(body)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            try:
                result = self._invoke(
                    self._base("put-object") + [
                        "--key", key,
                        "--body", str(target),
                        "--content-type", content_type,
                        "--server-side-encryption", "AES256",
                        "--if-none-match", "*",
                        "--metadata", f"sha256={digest}",
                    ]
                )
                assert result is not None
                version = str(result.get("VersionId", ""))
                if not version:
                    raise RemoteCustodyError("successor control write missing VersionId")
                recovered = exact_ref(version)
                if recovered is None:
                    raise RemoteCustodyError("successor control readback missing")
                return recovered
            except Exception as write_error:
                try:
                    recovered = exact_ref()
                except Exception:
                    raise write_error
                if recovered is None:
                    raise write_error
                return recovered
        finally:
            target.unlink(missing_ok=True)


def _reject_duplicate_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, child in pairs:
        if key in value:
            raise ValueError("duplicate JSON key")
        value[key] = child
    return value


def _load_control_json(path: Path) -> tuple[dict[str, Any], bytes, str]:
    try:
        raw = path.read_bytes()
        value = json.loads(raw, object_pairs_hook=_reject_duplicate_pairs)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError):
        raise BindingError(f"invalid successor control file: {path.name}") from None
    if not isinstance(value, dict):
        raise BindingError(f"invalid successor control object: {path.name}")
    return value, raw, _sha256(raw)


def _require_hash(value: Any, label: str) -> str:
    if not isinstance(value, str) or _SHA256_RE.fullmatch(value) is None:
        raise BindingError(f"invalid successor hash binding: {label}")
    return value


def _require_path_hash(
    bindings: Mapping[str, Any], path_key: str, hash_key: str, expected: str
) -> Path:
    if bindings.get(path_key) != expected:
        raise BindingError(f"successor path binding mismatch: {path_key}")
    path = Path(expected)
    expected_hash = _require_hash(bindings.get(hash_key), hash_key)
    try:
        actual_hash = _sha256(path.read_bytes())
    except OSError:
        raise BindingError(f"successor bound file missing: {path.name}") from None
    if actual_hash != expected_hash:
        raise BindingError(f"successor file hash mismatch: {path.name}")
    return path


def _validate_cli_materials(
    *,
    authority_path: Path,
    plan_path: Path,
    latch_path: Path,
    quota_ledger_path: Path,
    raw_index_path: Path,
    environment: Mapping[str, str] | None = None,
) -> tuple[Page100Spec, SuccessorBindings, PredecessorBundle, bytes, bytes]:
    """Revalidate LIVE material before secret, AWS, or provider use."""
    authority, _, authority_sha = _load_control_json(authority_path)
    plan, _, plan_sha = _load_control_json(plan_path)
    latch, _, _ = _load_control_json(latch_path)
    env = os.environ if environment is None else environment

    expected_repository = "AofSpds/asset-agent-asa"
    expected_branch = "aaa-pmo-public-data-g2-g3-source-admission-v1-20260828"
    expected_ref = "refs/heads/" + expected_branch
    identity = {
        key: env.get(key)
        for key in (
            "GITHUB_REPOSITORY", "GITHUB_REF", "GITHUB_SHA", "GITHUB_ACTOR",
            "GITHUB_TRIGGERING_ACTOR", "GITHUB_RUN_ID", "GITHUB_RUN_ATTEMPT",
        )
    }
    if (
        identity["GITHUB_REPOSITORY"] != expected_repository
        or identity["GITHUB_REF"] != expected_ref
        or identity["GITHUB_ACTOR"] != "AofSpds"
        or identity["GITHUB_TRIGGERING_ACTOR"] != "AofSpds"
        or not isinstance(identity["GITHUB_SHA"], str)
        or re.fullmatch(r"[0-9a-f]{40}", identity["GITHUB_SHA"]) is None
        or not isinstance(identity["GITHUB_RUN_ID"], str)
        or re.fullmatch(r"[1-9][0-9]*", identity["GITHUB_RUN_ID"]) is None
        or identity["GITHUB_RUN_ATTEMPT"] != "1"
    ):
        raise BindingError("successor GitHub execution identity mismatch")

    if (
        latch.get("state") != "ARMED"
        or latch.get("mode") != "LIVE_ARMED"
        or latch.get("repository") != expected_repository
        or latch.get("branch") != expected_branch
        or latch.get("owner_actor") != "AofSpds"
        or latch.get("runtime_lock_id") != RUNTIME_LOCK_ID
        or latch.get("pilot_run_id") != PILOT_RUN_ID
        or latch.get("execution_token_sha256") != EXECUTION_TOKEN_SHA256
        or latch.get("owner_cap_spec_sha256") != OWNER_CAP_SPEC_SHA256
        or latch.get("generation_id") != GENERATION_ID
        or latch.get("precheck_act_id") != PRECHECK_ACT_ID
        or latch.get("latch_event_id") != LATCH_EVENT_ID
        or latch.get("failed_generation_terminal", {}).get("workflow_run_id")
           != FAILED_PRECHECK_WORKFLOW_RUN_ID
        or latch.get("failed_generation_terminal", {}).get("do_not_rerun") is not True
        or latch.get("g4_precheck_terminal", {}).get("workflow_run_id")
           != G4_PRECHECK_WORKFLOW_RUN_ID
        or latch.get("g4_precheck_terminal", {}).get("head_sha")
           != G4_PRECHECK_HEAD_SHA
        or latch.get("g4_precheck_terminal", {}).get("do_not_rerun") is not True
        or latch.get("g4_precheck_terminal", {}).get("do_not_reuse_latch") is not True
        or latch.get("fresh_precheck_binding", {}).get("head_sha") == G4_PRECHECK_HEAD_SHA
        or latch.get("live_act_id") != LIVE_ACT_ID
    ):
        raise BindingError("successor LIVE latch binding mismatch")

    bound = latch.get("authority_bindings")
    if not isinstance(bound, Mapping) or bound.get("bindings_finalized") is not True:
        raise BindingError("successor authority bindings are not finalized")
    exact_paths = {
        "authority_path": str(authority_path),
        "plan_path": str(plan_path),
        "checkpoint_seed_path": (
            "control/m3top3/public-data-source-admission/v1.0/"
            "M3TOP3_FINANCE_CA_PAGE100_CHECKPOINT_SEED_v1.0.json"
        ),
        "baseline_quota_ledger_path": (
            "control/m3top3/public-data-source-admission/v1.0/"
            "M3TOP3_PUBLIC_DATA_API_QUOTA_LEDGER_v1.0.jsonl"
        ),
        "baseline_raw_index_path": (
            "control/m3top3/public-data-source-admission/v1.0/"
            "M3TOP3_FINANCE_CA_RAW_CUSTODY_INDEX_v1.0.jsonl"
        ),
        "predecessor_checkpoint_path": (
            "control/m3top3/public-data-source-admission/v1.0/"
            "M3TOP3_FINANCE_CA_ACQUISITION_CHECKPOINT_v1.0.json"
        ),
        "predecessor_report_path": (
            "control/m3top3/public-data-source-admission/v1.0/"
            "M3TOP3_FINANCE_CA_LIVE_PILOT_REPORT_v1.0.json"
        ),
        "predecessor_run_receipt_path": (
            "control/m3top3/public-data-source-admission/v1.0/"
            "M3TOP3_FINANCE_CA_LIVE_PILOT_RUN_RECEIPT_33195472310_v1.0.json"
        ),
        "runner_path": "tools/m3top3/finance_page100_pilot.py",
        "source_admission_path": "tools/m3top3/source_admission.py",
        "workflow_path": (
            ".github/workflows/"
            "m3top3-finance-page100-bounded-pilot-v1.yml"
        ),
        "remediation_receipt_path": "control/m3top3/public-data-source-admission/v1.0/M3TOP3_AWS_S3_RAW_WRITER_LISTBUCKETVERSIONS_REMEDIATION_RECEIPT_v1.0.json",
        "effective_writer_policy_path": "control/m3top3/public-data-source-admission/v1.0/aws-oidc/M3TOP3_AWS_S3_RAW_WRITER_POLICY_v1.0.json",
        "max_session_receipt_path": "control/m3top3/public-data-source-admission/v1.0/M3TOP3_AWS_IAM_ROLE_MAX_SESSION_DURATION_REMEDIATION_RECEIPT_v1.0.json",
    }
    hash_keys = {
        "authority_path": "authority_sha256",
        "plan_path": "plan_sha256",
        "checkpoint_seed_path": "checkpoint_seed_sha256",
        "baseline_quota_ledger_path": "baseline_quota_ledger_sha256",
        "baseline_raw_index_path": "baseline_raw_index_sha256",
        "predecessor_checkpoint_path": "predecessor_checkpoint_sha256",
        "predecessor_report_path": "predecessor_report_sha256",
        "predecessor_run_receipt_path": "predecessor_run_receipt_sha256",
        "runner_path": "runner_sha256",
        "source_admission_path": "source_admission_sha256",
        "workflow_path": "workflow_sha256",
        "remediation_receipt_path": "remediation_receipt_sha256",
        "effective_writer_policy_path": "effective_writer_policy_sha256",
        "max_session_receipt_path": "max_session_receipt_sha256",
    }
    bound_paths: dict[str, Path] = {}
    for path_key, expected in exact_paths.items():
        bound_paths[path_key] = _require_path_hash(
            bound, path_key, hash_keys[path_key], expected
        )
    if bound.get("authority_sha256") != authority_sha:
        raise BindingError("successor authority content hash mismatch")
    if bound.get("plan_sha256") != plan_sha:
        raise BindingError("successor plan content hash mismatch")

    max_session = json.loads(bound_paths["max_session_receipt_path"].read_text(encoding="utf-8"))
    checkpoint_seed = json.loads(bound_paths["checkpoint_seed_path"].read_text(encoding="utf-8"))
    if (
        bound.get("max_session_receipt_sha256") != MAX_SESSION_RECEIPT_SHA256
        or max_session.get("state") != "PASS__MAX_SESSION_DURATION_3600_TO_21600__READBACK_PROVEN"
        or max_session.get("change", {}).get("from_max_session_duration_seconds") != 3600
        or max_session.get("change", {}).get("to_max_session_duration_seconds") != 21600
        or max_session.get("change", {}).get("only_changed_field") != "Role.MaxSessionDuration"
        or max_session.get("aws_cli_execution", {}).get("update_role_attempts") != 1
        or max_session.get("aws_cli_execution", {}).get("update_role_retry") != "PROHIBITED"
        or max_session.get("aws_cli_execution", {}).get("update_role_rc") != 0
        or max_session.get("post_state", {}).get("max_session_duration_seconds") != 21600
        or max_session.get("non_target_invariants", {}).get("collateral_check") != "PASS__ONLY_MAX_SESSION_DURATION_CHANGED"
        or max_session.get("rollback", {}).get("dormant_rollback_executed") is not False
        or max_session.get("validation_claim") != "NONE"
        or checkpoint_seed.get("planned_quota_day_kst") != SuccessorBindings().quota_day_kst
        or checkpoint_seed.get("runtime_lock_id") != RUNTIME_LOCK_ID
        or checkpoint_seed.get("pilot_run_id") != PILOT_RUN_ID
        or checkpoint_seed.get("provider_api_network_attempts") != 0
        or checkpoint_seed.get("quota_reservations") != 0
        or checkpoint_seed.get("remote_raw_custody_writes") != 0
    ):
        raise BindingError("successor MaxSession or checkpoint-seed semantic mismatch")

    material = latch.get("execution_material")
    material_hash = _require_hash(
        latch.get("execution_material_sha256"), "execution_material_sha256"
    )
    if not isinstance(material, Mapping) or _sha256(
        sa.canonical_json_bytes(dict(material))
    ) != material_hash:
        raise BindingError("successor execution material hash mismatch")
    required_material = {
        "runtime_lock_id": RUNTIME_LOCK_ID,
        "pilot_run_id": PILOT_RUN_ID,
        "execution_token_sha256": EXECUTION_TOKEN_SHA256,
        "owner_cap_spec_sha256": OWNER_CAP_SPEC_SHA256,
        "generation_id": GENERATION_ID,
        "precheck_act_id": PRECHECK_ACT_ID,
        "live_act_id": LIVE_ACT_ID,
        "latch_event_id": LATCH_EVENT_ID,
        "authority_sha256": authority_sha,
        "plan_sha256": plan_sha,
        "runner_sha256": bound.get("runner_sha256"),
        "source_admission_sha256": bound.get("source_admission_sha256"),
        "checkpoint_template_sha256": bound.get("checkpoint_seed_sha256"),
        "workflow_sha256": bound.get("workflow_sha256"),
        "remediation_receipt_sha256": bound.get("remediation_receipt_sha256"),
        "effective_writer_policy_sha256": bound.get("effective_writer_policy_sha256"),
        "max_session_receipt_sha256": bound.get("max_session_receipt_sha256"),
        "effective_writer_policy_canonical_sha256": "d2d1936ff420d2e97ededf64f376f544dacf838f125e4e8d6f3f4562efef774c",
        "baseline_quota_ledger_sha256": bound.get(
            "baseline_quota_ledger_sha256"
        ),
        "baseline_raw_index_sha256": bound.get("baseline_raw_index_sha256"),
        "predecessor_checkpoint_sha256": bound.get(
            "predecessor_checkpoint_sha256"
        ),
        "predecessor_report_sha256": bound.get("predecessor_report_sha256"),
        "predecessor_run_receipt_sha256": bound.get(
            "predecessor_run_receipt_sha256"
        ),
    }
    if any(material.get(key) != value for key, value in required_material.items()):
        raise BindingError("successor execution material binding mismatch")

    authority_profiles = authority.get("mode_profiles")
    plan_profiles = plan.get("mode_profiles")
    if (
        authority.get("active_profile_selector") != "LATCH_MODE"
        or plan.get("active_profile_selector") != "LATCH_MODE"
        or not isinstance(authority_profiles, Mapping)
        or not isinstance(plan_profiles, Mapping)
        or set(authority_profiles) != {"PRECHECK_ARMED", "LIVE_ARMED"}
        or set(plan_profiles) != {"PRECHECK_ARMED", "LIVE_ARMED"}
    ):
        raise BindingError("successor immutable mode profiles missing")
    auth_profile = authority_profiles.get("LIVE_ARMED")
    plan_profile = plan_profiles.get("LIVE_ARMED")
    current = auth_profile.get("current_runtime_authority") if isinstance(auth_profile, Mapping) else None
    live = auth_profile.get("finance_page100_pilot_authority") if isinstance(auth_profile, Mapping) else None
    plan_gate = plan_profile.get("execution_gate") if isinstance(plan_profile, Mapping) else None
    custody_plan = plan.get("durable_custody_plan")
    activation = latch.get("activation_modes", {}).get("LIVE_ARMED", {})
    raw_uri = (
        "s3://semi-data-plane-aofspds-20260815/" + RAW_KEY_PREFIX
        + "_pilot_generation/"
        + f"runtime_lock_id={RUNTIME_LOCK_ID}/pilot_run_id={PILOT_RUN_ID}/"
    )
    claim_uri = (
        "s3://semi-data-plane-aofspds-20260815/"
        + execution_claim_object_key(
            SuccessorBindings(
                github_run_id=int(identity["GITHUB_RUN_ID"]),
                github_run_attempt=1,
            )
        )
    )
    if (
        not isinstance(current, Mapping)
        or current.get("provider_api_network_calls_entry_gate") != "OPEN"
        or current.get("provider_api_network_calls_authorized") is not True
        or current.get("quota_reservation_authorized") is not True
        or current.get("live_multi_page_provider_run_authorized") is not True
        or current.get("remote_raw_custody_write_authorized") is not True
        or current.get("remote_raw_custody_prefix") != raw_uri
        or not isinstance(live, Mapping)
        or live.get("authority_state") != "GRANTED_ENTRY_GATE_OPEN"
        or live.get("live_entry_gate", {}).get("state") != "OPEN"
        or live.get("remote_raw_custody_prefix") != raw_uri
        or live.get("execution_claim_uri") != claim_uri
        or not isinstance(plan_profile, Mapping)
        or plan_profile.get("state") != "LIVE_ARMED_EXECUTABLE"
        or plan_profile.get("durable_custody_state") != "READY_FOR_LIVE_ARMED"
        or not isinstance(plan_gate, Mapping)
        or plan_gate.get("state") != "OPEN"
        or any(plan_gate.get(key) is not True for key in (
            "execution_armed", "plan_executable",
            "provider_api_calls_permitted_now", "quota_reservations_permitted_now",
            "remote_s3_writes_permitted_now",
        ))
        or any(activation.get(key) is not True for key in (
            "provider_api_calls_authorized", "quota_reservations_authorized",
            "remote_raw_custody_writes_authorized",
        ))
        or activation.get("act_id") != LIVE_ACT_ID
        or latch.get("provider_api_calls_authorized") is not True
        or latch.get("quota_reservations_authorized") is not True
        or latch.get("remote_raw_custody_writes_authorized") is not True
        or not isinstance(custody_plan, Mapping)
        or custody_plan.get("state") != "DERIVED_FROM_LATCH_MODE"
        or custody_plan.get("exact_remote_raw_prefix") != raw_uri
        or custody_plan.get("execution_claim_uri") != claim_uri
    ):
        raise BindingError("successor LIVE authority profile is not open")

    finance = latch.get("finance_spec")
    if not isinstance(finance, Mapping):
        raise BindingError("successor Finance specification missing")
    exact_finance = {
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
    }
    if any(finance.get(key) != value for key, value in exact_finance.items()):
        raise BindingError("successor Finance owner caps shifted")
    for key in (
        "s2_ksd_blocker_waiver", "bulk_acquisition_authorized",
        "production_authorized", "model_semantic_change_authorized",
        "pit_semantic_change_authorized",
    ):
        if latch.get(key) is not False:
            raise BindingError("successor authorization ceiling shifted")
    if latch.get("validation_claim") != "NONE" or latch.get("gate_effect") != "NONE":
        raise BindingError("successor claim ceiling shifted")

    baseline_quota = pre_current_pilot_bytes(
        quota_ledger_path.read_bytes(), PILOT_RUN_ID
    )
    baseline_raw = pre_current_pilot_bytes(raw_index_path.read_bytes(), PILOT_RUN_ID)
    if _sha256(baseline_quota) != bound.get("baseline_quota_ledger_sha256"):
        raise BindingError("governed predecessor quota prefix hash mismatch")
    if _sha256(baseline_raw) != bound.get("baseline_raw_index_sha256"):
        raise BindingError("governed predecessor raw-index prefix hash mismatch")
    predecessor_checkpoint = bound_paths["predecessor_checkpoint_path"].read_bytes()
    bundle = PredecessorBundle(
        checkpoint_bytes=predecessor_checkpoint,
        raw_index_bytes=baseline_raw,
        quota_ledger_bytes=baseline_quota,
        report_bytes=bound_paths["predecessor_report_path"].read_bytes(),
    )
    bindings_value = SuccessorBindings(
        github_run_id=int(identity["GITHUB_RUN_ID"]),
        github_run_attempt=1,
    )
    return Page100Spec(), bindings_value, bundle, baseline_quota, baseline_raw


def _quota_rows_from_checkpoint(
    checkpoint: Mapping[str, Any]
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for attempt in checkpoint.get("attempts", []):
        rows.append({
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
            "provider_call_started": attempt.get("provider_call_started", False),
            "outcome": attempt["state"],
            "automatic_retry": attempt["attempt"] > 1,
            "known_external_attempts_minimum": 0,
            "unknown_external_attempts": True,
        })
    return rows


def _atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(f".{path.name}.{os.getpid()}.{time.time_ns()}.tmp")
    try:
        with temp.open("xb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)


def _main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Finance-only page-100 bounded successor pilot"
    )
    parser.add_argument("--authority", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--latch", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--quota-ledger", type=Path, required=True)
    parser.add_argument("--raw-index", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args(argv)

    spec, bindings, bundle, baseline_quota, baseline_raw = _validate_cli_materials(
        authority_path=args.authority,
        plan_path=args.plan,
        latch_path=args.latch,
        quota_ledger_path=args.quota_ledger,
        raw_index_path=args.raw_index,
    )
    deadline_text = os.environ.get("FINANCE_SELF_DEADLINE_SECONDS", "")
    if deadline_text != "18000":
        raise BindingError("successor self-deadline binding mismatch")
    not_after_text = os.environ.get("FINANCE_LIVE_NOT_AFTER_UTC", "")
    if not_after_text != "2026-08-30T14:30:00Z":
        raise BindingError("successor absolute not-after binding mismatch")
    not_after = datetime.fromisoformat(not_after_text.replace("Z", "+00:00"))
    remaining = (not_after - datetime.now(timezone.utc)).total_seconds()
    if remaining <= 0:
        raise SelfDeadlineExceededError("successor absolute not-after reached")
    secret = sa.validate_decoded_secret(
        legacy.FINANCE_SECRET_ENV,
        os.environ.get(legacy.FINANCE_SECRET_ENV),
    )
    acquisition_seconds = min(int(deadline_text), int(remaining) - 1200)
    if acquisition_seconds <= 0:
        raise SelfDeadlineExceededError("successor shutdown reserve unavailable")
    deadline = time.monotonic() + acquisition_seconds
    shutdown_deadline = deadline + 1200.0
    def bounded_s3_command_runner(
        command: Sequence[str],
    ) -> subprocess.CompletedProcess[str]:
        remaining_shutdown = shutdown_deadline - time.monotonic()
        if remaining_shutdown <= 0.25:
            raise RemoteCustodyError("successor shutdown S3 budget exhausted")
        return subprocess.run(
            list(command), check=False, capture_output=True, text=True,
            timeout=min(20.0, remaining_shutdown),
        )
    store = S3Page100ObjectStore(
        bindings, command_runner=bounded_s3_command_runner
    )
    transport = BoundedUrlLibFinanceTransport(
        secret,
        quota_day_kst=bindings.quota_day_kst,
        not_after_utc=not_after,
        deadline_monotonic=deadline,
    )
    writer_id = (
        f"github-run:{bindings.github_run_id}:attempt:{bindings.github_run_attempt}"
    )
    exit_code = 0
    report: dict[str, Any] | None = None
    execution_error: Exception | None = None
    try:
        report = run_page100_pilot(
            spec,
            bindings,
            bundle,
            transport=transport,
            custody=store,
            claim_store=store,
            checkpoint_store=store,
            writer_id=writer_id,
            secrets=(secret,),
            not_after_utc=not_after,
            deadline_monotonic=deadline,
        )
    except Exception as exc:
        execution_error = exc
        exit_code = 2

    checkpoint, checkpoint_token = store.load()
    if checkpoint is None:
        if execution_error is not None:
            raise execution_error
        raise RemoteCustodyError("successor durable checkpoint missing")
    if report is None:
        report = _build_report(checkpoint, checkpoint_token)

    quota_bytes = baseline_quota + b"".join(
        sa.canonical_json_bytes(row)
        for row in _quota_rows_from_checkpoint(checkpoint)
    )
    raw_bytes = baseline_raw + b"".join(
        sa.canonical_json_bytes(row) for row in checkpoint.get("raw_index", [])
    )
    checkpoint_bytes = sa.canonical_json_bytes(dict(checkpoint))
    report_bytes = sa.canonical_json_bytes(report)
    for payload in (checkpoint_bytes, quota_bytes, raw_bytes, report_bytes):
        sa.assert_no_secret(payload, (secret,))
    _atomic_write(args.checkpoint, checkpoint_bytes)
    _atomic_write(args.quota_ledger, quota_bytes)
    _atomic_write(args.raw_index, raw_bytes)
    _atomic_write(args.report, report_bytes)
    if execution_error is not None:
        raise execution_error
    _assert_checkpoint(checkpoint, bindings)
    if checkpoint.get("state") != "COMPLETE":
        raise RemoteCustodyError("successor terminal checkpoint is not COMPLETE")

    # Same-process, exact-body terminal recovery only.  This is not a workflow
    # rerun and cannot issue provider calls, reserve quota, or write raw data.
    # The shared shutdown deadline was fixed before acquisition.  Raw custody,
    # checkpointing, and terminal publication cannot receive a fresh budget.
    base_report = json.loads(json.dumps(report))
    finalization_deadline = shutdown_deadline
    last_finalization_error: Exception | None = None
    for finalization_attempt in range(1, 4):
        try:
            if time.monotonic() >= finalization_deadline:
                raise RemoteCustodyError(
                    "successor terminal finalization budget exhausted"
                )
            checkpoint_ref = store.checkpoint_reference(
                checkpoint, checkpoint_token
            )
            quota_ref = store.put_control_artifact(
                "quota-ledger.jsonl", quota_bytes, "application/x-ndjson"
            )
            raw_ref = store.put_control_artifact(
                "raw-index.jsonl", raw_bytes, "application/x-ndjson"
            )
            durable_report = json.loads(json.dumps(base_report))
            durable_report["durable_control_artifacts"] = {
                "checkpoint": dict(checkpoint_ref),
                "quota_ledger": dict(quota_ref),
                "raw_index": dict(raw_ref),
            }
            durable_report_bytes = sa.canonical_json_bytes(durable_report)
            sa.assert_no_secret(durable_report_bytes, (secret,))
            report_ref = store.put_control_artifact(
                "report.json", durable_report_bytes, "application/json"
            )
            terminal_manifest = {
                "artifact": "M3TOP3_FINANCE_CA_PAGE100_TERMINAL_MANIFEST_v1.0",
                "state": "COMPLETE_TERMINAL_READBACK_PROVEN",
                "runtime_lock_id": RUNTIME_LOCK_ID,
                "pilot_run_id": PILOT_RUN_ID,
                "checkpoint_token_sha256": _sha256(
                    str(checkpoint_token).encode("utf-8")
                ),
                "checkpoint": dict(checkpoint_ref),
                "quota_ledger": dict(quota_ref),
                "raw_index": dict(raw_ref),
                "report": dict(report_ref),
                "automatic_promotion_performed": False,
                "validation_claim": "NONE",
            }
            manifest_ref = store.put_control_artifact(
                "terminal-manifest.json",
                sa.canonical_json_bytes(terminal_manifest),
                "application/json",
            )
            report = durable_report
            report["durable_control_artifacts"]["report"] = dict(report_ref)
            report["durable_control_artifacts"]["terminal_manifest"] = dict(
                manifest_ref
            )
            _atomic_write(args.report, sa.canonical_json_bytes(report))
            last_finalization_error = None
            break
        except Exception as exc:
            last_finalization_error = exc
            if finalization_attempt < 3:
                retry_delay = float(finalization_attempt)
                if time.monotonic() + retry_delay >= finalization_deadline:
                    last_finalization_error = RemoteCustodyError(
                        "successor terminal finalization budget exhausted"
                    )
                    break
                time.sleep(retry_delay)
    if last_finalization_error is not None:
        raise last_finalization_error
    return exit_code


def main() -> int:
    try:
        return _main()
    except Exception as exc:
        print("FINANCE_PAGE100_PILOT_BLOCKED:" + type(exc).__name__)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
