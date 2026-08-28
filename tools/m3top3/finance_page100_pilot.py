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
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Protocol, Sequence

from . import finance_live_pilot as legacy
from . import source_admission as sa


RUNTIME_LOCK_ID = "PMO-FINANCE-PAGE100-20260829041623"
PILOT_RUN_ID = "FINANCE-PAGE100-PILOT-20260829041623"
ACTIVATION_BASE_HEAD_COMMIT = "31d1bc2a23b97c34adb851ab73394145994ddb6e"
EXECUTION_TOKEN_SHA256 = "763c3e1a57f270efcec8ca9be1ee2565a131bf0e4501343e68670fd7f5d32d0d"

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
    quota_day_kst: str = "2026-08-29"
    finance_ordinal_base: int = 9
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

    def find_existing_by_prefix(self, object_prefix: str) -> SealedEntity | None: ...

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
        ):
            raise sa.CheckpointConflictError("page-100 raw custody join invalid")
        raw_by_attempt[identity] = raw
        status = str(raw.get("http_status"))
        status_counts[status] = status_counts.get(status, 0) + 1
        result_code = str(raw.get("provider_result_code"))
        observed_result_counts[result_code] = (
            observed_result_counts.get(result_code, 0) + 1
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

    claim = _execution_claim(bindings, writer_id)
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
        checkpoint = _initial_checkpoint(bindings, seed, evidence, clock=clock)
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
                sealed = custody.find_existing_by_prefix(
                    latest["raw_object_prefix"]
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
                attempt["provider_call_started"] = True
                attempt["provider_call_started_at_utc"] = _iso_utc(clock)
                if bas_dt == "20240131" and page_no == 1:
                    checkpoint["page_1_revalidation"]["fresh_calls_started"] += 1
                checkpoint["provider_api_network_attempts"] += 1
                save()
                params = sa.finance_request_params(
                    bas_dt, page_no, REQUEST_PAGE_SIZE
                )
                try:
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
                }
                sealed = custody.seal_and_readback(
                    object_key, response.body, metadata
                )
                persist_sealed(attempt, sealed, reconciled=False)
                latest = attempt

            assert latest is not None and sealed is not None
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

    def acquire_execution_claim(
        self, claim: Mapping[str, Any]
    ) -> ExecutionClaimEvidence:
        """Create once; a 412 always blocks, even for byte-identical payloads."""
        payload = sa.canonical_json_bytes(dict(claim))
        with tempfile.NamedTemporaryFile(
            prefix="m3top3-page100-claim-", delete=False
        ) as handle:
            target = Path(handle.name)
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            result = self._invoke(
                self._base("put-object") + [
                    "--key", self.claim_key,
                    "--body", str(target),
                    "--content-type", "application/json",
                    "--server-side-encryption", "AES256",
                    "--if-none-match", "*",
                ]
            )
            assert result is not None
            created_version = str(result.get("VersionId", ""))
            if not created_version:
                raise RemoteCustodyError(
                    "execution claim create missing VersionId"
                )
            readback = self._get(self.claim_key, version_id=created_version)
            if readback is None or readback[0] != payload:
                raise RemoteCustodyError("execution claim readback mismatch")
            meta = readback[1]
            version_id = str(meta.get("VersionId", ""))
            etag = str(meta.get("ETag", ""))
            sse = str(meta.get("ServerSideEncryption", ""))
            if version_id != created_version or not etag or sse != "AES256":
                raise RemoteCustodyError(
                    "execution claim readback evidence missing"
                )
            return ExecutionClaimEvidence(
                object_key=self.claim_key,
                content_sha256=_sha256(payload),
                version_id=version_id,
                etag=etag,
                server_side_encryption=sse,
                write_precondition="IF_NONE_MATCH_STAR",
                writer_id=str(claim.get("writer_id", "")),
            )
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
            "quota-day-kst": self.bindings.quota_day_kst,
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
        self, object_key: str, version_id: str | None = None
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
        try:
            bas_dt = str(user["bas-dt"])
            page_no = int(user["page-no"])
        except (KeyError, TypeError, ValueError):
            raise RemoteCustodyError("successor raw request metadata invalid") from None
        required = {
            "sha256", "http-status", "acquired-at-utc", "request-id",
            "bas-dt", "page-no", "attempt", "runtime-lock-id",
            "pilot-run-id", "quota-day-kst",
        }
        if (
            set(user) != required
            or quota_day != self.bindings.quota_day_kst
            or bas_dt not in PRIMARY_DATES[1:]
            or not 1 <= page_no <= MAX_PAGES_PER_DATE
            or request_id != deterministic_request_id(bas_dt, page_no)
            or str(user.get("request-id", "")) != request_id
            or str(user.get("attempt", "")) != attempt_text
            or str(user.get("runtime-lock-id", "")) != RUNTIME_LOCK_ID
            or str(user.get("pilot-run-id", "")) != PILOT_RUN_ID
            or str(user.get("quota-day-kst", "")) != quota_day
            or key_digest != sealed.entity_sha256
            or (version_id is not None and sealed.version_id != version_id)
        ):
            raise RemoteCustodyError("successor raw lineage metadata mismatch")
        return sealed

    def read_existing(
        self, object_key: str, version_id: str | None = None
    ) -> SealedEntity | None:
        return self._read_current(object_key, version_id)

    def find_existing_by_prefix(self, object_prefix: str) -> SealedEntity | None:
        required = (
            RAW_KEY_PREFIX + "_pilot_generation/"
            + f"runtime_lock_id={RUNTIME_LOCK_ID}/"
            + f"pilot_run_id={PILOT_RUN_ID}/"
        )
        if not object_prefix.startswith(required):
            raise RemoteCustodyError("successor reconciliation prefix escaped")
        result = self._invoke(
            self._base("list-objects-v2")
            + ["--prefix", object_prefix, "--max-keys", "2"]
        )
        assert result is not None
        contents = result.get("Contents", [])
        keys = [
            row.get("Key") for row in contents if isinstance(row, Mapping)
        ] if isinstance(contents, list) else []
        if (
            not isinstance(contents, list)
            or len(keys) != len(contents)
            or result.get("IsTruncated") is True
            or len(keys) > 1
            or any(
                not isinstance(key, str)
                or re.fullmatch(
                    re.escape(object_prefix) + r"sha256=[0-9a-f]{64}\.entity",
                    key,
                ) is None
                for key in keys
            )
        ):
            raise RemoteCustodyError("successor reconciliation listing invalid")
        return self._read_current(keys[0]) if keys else None

    def seal_and_readback(
        self, object_key: str, body: bytes, metadata: Mapping[str, str]
    ) -> SealedEntity:
        digest = _sha256(body)
        required = {
            "sha256", "http-status", "acquired-at-utc", "request-id",
            "bas-dt", "page-no", "attempt", "runtime-lock-id",
            "pilot-run-id", "quota-day-kst",
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
        ):
            raise RemoteCustodyError("successor raw metadata lineage shifted")
        with tempfile.NamedTemporaryFile(
            prefix="m3top3-page100-raw-", delete=False
        ) as handle:
            target = Path(handle.name)
            handle.write(body)
            handle.flush()
            os.fsync(handle.fileno())
        try:
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
            sealed = self._read_current(object_key, version_id)
            if sealed is None or sealed.body != body:
                raise RemoteCustodyError("successor raw readback mismatch")
            return sealed
        finally:
            target.unlink(missing_ok=True)

    def put_control_artifact(
        self, name: str, body: bytes, content_type: str
    ) -> Mapping[str, str]:
        if name not in {"quota-ledger.jsonl", "raw-index.jsonl", "report.json"}:
            raise RemoteCustodyError("successor control artifact name invalid")
        key = self.checkpoint_key.rsplit("/", 1)[0] + "/" + name
        with tempfile.NamedTemporaryFile(
            prefix="m3top3-page100-control-", delete=False
        ) as handle:
            target = Path(handle.name)
            handle.write(body)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            result = self._invoke(
                self._base("put-object") + [
                    "--key", key,
                    "--body", str(target),
                    "--content-type", content_type,
                    "--server-side-encryption", "AES256",
                    "--if-none-match", "*",
                    "--metadata", f"sha256={_sha256(body)}",
                ]
            )
            assert result is not None
            version = str(result.get("VersionId", ""))
            readback = self._get(key, version_id=version)
            if (
                not version
                or readback is None
                or readback[0] != body
                or str(readback[1].get("VersionId", "")) != version
                or str(readback[1].get("ServerSideEncryption", "")) != "AES256"
            ):
                raise RemoteCustodyError("successor control readback mismatch")
            return {
                "object_key": key,
                "version_id": version,
                "etag": str(readback[1].get("ETag", "")),
                "sha256": _sha256(body),
                "server_side_encryption": "AES256",
                "write_precondition": "IF_NONE_MATCH_STAR",
            }
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
        "authority_sha256": authority_sha,
        "plan_sha256": plan_sha,
        "runner_sha256": bound.get("runner_sha256"),
        "source_admission_sha256": bound.get("source_admission_sha256"),
        "checkpoint_template_sha256": bound.get("checkpoint_seed_sha256"),
        "workflow_sha256": bound.get("workflow_sha256"),
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

    current = authority.get("current_runtime_authority")
    live = authority.get("finance_page100_pilot_authority")
    plan_gate = plan.get("execution_gate")
    custody_plan = plan.get("durable_custody_plan")
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
        or plan.get("state") != "LIVE_ARMED_EXECUTABLE"
        or not isinstance(plan_gate, Mapping)
        or plan_gate.get("state") != "OPEN"
        or any(
            plan_gate.get(key) is not True
            for key in (
                "execution_armed", "plan_executable",
                "provider_api_calls_permitted_now",
                "remote_s3_writes_permitted_now",
            )
        )
        or not isinstance(custody_plan, Mapping)
        or custody_plan.get("state") != "READY_FOR_LIVE_ARMED"
        or custody_plan.get("exact_remote_raw_prefix") != raw_uri
        or custody_plan.get("execution_claim_uri") != claim_uri
    ):
        raise BindingError("successor LIVE authority gate is not open")

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
    if deadline_text != "19800":
        raise BindingError("successor self-deadline binding mismatch")
    secret = sa.validate_decoded_secret(
        legacy.FINANCE_SECRET_ENV,
        os.environ.get(legacy.FINANCE_SECRET_ENV),
    )
    store = S3Page100ObjectStore(bindings)
    transport = legacy.UrlLibFinanceTransport(secret)
    deadline = time.monotonic() + int(deadline_text)
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

    quota_ref = store.put_control_artifact(
        "quota-ledger.jsonl", quota_bytes, "application/x-ndjson"
    )
    raw_ref = store.put_control_artifact(
        "raw-index.jsonl", raw_bytes, "application/x-ndjson"
    )
    report["durable_control_artifacts"] = {
        "quota_ledger": dict(quota_ref),
        "raw_index": dict(raw_ref),
    }
    report_bytes = sa.canonical_json_bytes(report)
    sa.assert_no_secret(report_bytes, (secret,))
    _atomic_write(args.report, report_bytes)
    report_ref = store.put_control_artifact(
        "report.json", report_bytes, "application/json"
    )
    report["durable_control_artifacts"]["report"] = dict(report_ref)
    # The S3 report cannot contain its own content digest without a cycle.  The
    # local sanitized mirror records the exact immutable S3 reference.
    _atomic_write(args.report, sa.canonical_json_bytes(report))
    if execution_error is not None:
        raise execution_error
    return exit_code


def main() -> int:
    try:
        return _main()
    except Exception as exc:
        print("FINANCE_PAGE100_PILOT_BLOCKED:" + type(exc).__name__)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
