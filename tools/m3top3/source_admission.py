#!/usr/bin/env python3
"""Fail-closed primitives for the M3Top3 public-data source canaries.

This module is additive and deliberately does not touch production providers,
model semantics, PIT semantics, or active manifests.  It supports only source
preflight/canary evidence and injected-fixture Finance pilot readiness until the
durable raw-data plane and endpoint identity gates are closed.
"""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import re
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Protocol
from xml.etree import ElementTree


KST = timezone(timedelta(hours=9))
MAX_ATTEMPTS = 3
SECRET_NAMES = (
    "DATA_GO_KR_FINANCE_STOCK_RIGHTS_SERVICE_KEY",
    "DATA_GO_KR_KSD_CORP_SERVICE_KEY",
)
KSD_SOURCE_ID = "M3TOP3-KSD-CORP-DATA-GO-KR-v1"
KSD_BASE_URL = "https://apis.data.go.kr/B552481/CorpSvc"
KSD_ALTERNATE_CANDIDATE = "https://api.seibro.or.kr/openapi/service/CorpSvc"
FINANCE_SOURCE_ID = "M3TOP3-FINANCE-STOCK-RIGHTS-v1"
FINANCE_URL = (
    "https://apis.data.go.kr/1160100/GetStocRighScheService_V2/"
    "getRighExerReasSche_V2"
)
FINANCE_OPERATION = "getRighExerReasSche_V2"
QUOTA_CAPS = {"KSD": 80, "FINANCE": 8000}
SAFE_HEADERS = {"content-type", "content-length", "date", "etag", "last-modified"}
KSD_MARKET_NAME_FIELDS = ("listNm", "caltotMartTpcdNm", "lstgScrsItmsKcdNm", "scrsItmsKcdNm", "mrktNm", "marketNm")
_PERCENT_TRIPLET = re.compile(r"%[0-9A-Fa-f]{2}")
_ASCII_YYYYMMDD = re.compile(r"[0-9]{8}")
_ASCII_SHA256 = re.compile(r"[0-9a-f]{64}")
_ASCII_UNSIGNED_INTEGER = re.compile(r"[0-9]+")


class AdmissionError(RuntimeError):
    """Sanitized, non-secret-bearing source-admission failure."""


class CredentialContractError(AdmissionError):
    pass


class QuotaBoundaryError(AdmissionError):
    pass


class SourceProtocolError(AdmissionError):
    pass


class SourceTransportError(AdmissionError):
    pass


class CheckpointConflictError(AdmissionError):
    pass


def canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def validate_decoded_secret(name: str, value: str | None) -> str:
    """Accept only a present decoded-form key; never transform or reveal it."""
    if not value:
        raise CredentialContractError(f"missing required secret: {name}")
    if value != value.strip() or any(ch.isspace() for ch in value):
        raise CredentialContractError(f"invalid decoded secret format: {name}")
    if _PERCENT_TRIPLET.search(value):
        raise CredentialContractError(f"invalid decoded secret format: {name}")
    return value


def encoded_query(endpoint: str, params: Mapping[str, Any], secret: str) -> str:
    """Build one authenticated URL from a decoded key exactly once."""
    clean = {str(k): str(v) for k, v in params.items() if k != "serviceKey"}
    clean["serviceKey"] = secret
    return endpoint + "?" + urllib.parse.urlencode(clean, doseq=False)


def secret_variants(secret: str) -> tuple[bytes, ...]:
    variants = {
        secret.encode("utf-8"),
        urllib.parse.quote(secret, safe="").encode("ascii"),
        urllib.parse.quote_plus(secret, safe="").encode("ascii"),
    }
    return tuple(sorted(variants))


def assert_no_secret(data: bytes, secrets: tuple[str, ...]) -> None:
    if any(variant and variant in data for secret in secrets for variant in secret_variants(secret)):
        raise CredentialContractError("secret-bearing response or output rejected")


def _xml_to_value(element: ElementTree.Element) -> Any:
    children = list(element)
    if not children:
        return (element.text or "").strip()
    grouped: dict[str, Any] = {}
    for child in children:
        tag = child.tag.rsplit("}", 1)[-1]
        value = _xml_to_value(child)
        if tag in grouped:
            if not isinstance(grouped[tag], list):
                grouped[tag] = [grouped[tag]]
            grouped[tag].append(value)
        else:
            grouped[tag] = value
    return grouped


def parse_entity_bytes(data: bytes) -> Any:
    """Parse JSON or non-DOCTYPE XML from exact stored entity bytes."""
    payload = data.lstrip(b"\xef\xbb\xbf\x00\t\r\n ")
    if payload.startswith((b"{", b"[")):
        def no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
            result: dict[str, Any] = {}
            for key, value in pairs:
                if key in result:
                    raise SourceProtocolError("duplicate JSON key")
                result[key] = value
            return result

        try:
            return json.loads(payload.decode("utf-8"), object_pairs_hook=no_duplicates)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise SourceProtocolError("malformed JSON response") from None
    if payload.startswith(b"<"):
        if b"<!DOCTYPE" in payload.upper() or b"<!ENTITY" in payload.upper():
            raise SourceProtocolError("unsafe XML response")
        try:
            root = ElementTree.fromstring(payload)
        except ElementTree.ParseError:
            raise SourceProtocolError("malformed XML response") from None
        return {root.tag.rsplit("}", 1)[-1]: _xml_to_value(root)}
    raise SourceProtocolError("unexpected non-JSON/XML response")


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
            if isinstance(item, list) and all(isinstance(row, dict) for row in item):
                return item
            raise SourceProtocolError("invalid provider item shape")
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


def classify_provider(provider: str, parsed: Any) -> dict[str, Any]:
    code = str(_find_first(parsed, ("resultCode", "returnReasonCode", "code")) or "")
    message = str(_find_first(parsed, ("resultMsg", "returnAuthMsg", "message")) or "")
    total_raw = _find_first(parsed, ("totalCount", "totalCnt"))
    try:
        total = int(total_raw) if total_raw not in (None, "") else None
    except (TypeError, ValueError):
        raise SourceProtocolError("invalid totalCount") from None
    items = _find_items(parsed)
    normalized_code = code.lstrip("0") or "0"
    if provider == "FINANCE":
        if normalized_code != "0":
            raise SourceProtocolError("Finance provider resultCode failure")
        if total is None:
            raise SourceProtocolError("Finance response missing totalCount")
        state = "VALID_EMPTY" if total == 0 else "SUCCESS"
    elif provider == "KSD":
        if normalized_code == "3":
            state = "NODATA"
        elif normalized_code == "11":
            raise SourceProtocolError("KSD schema/request failure")
        elif normalized_code == "0":
            state = "SUCCESS" if items else "VALID_EMPTY"
        else:
            raise SourceProtocolError("KSD unknown provider resultCode")
    else:
        raise SourceProtocolError("unknown provider")
    return {"provider": provider, "state": state, "result_code": code, "message": message, "total_count": total, "items": items}


def _parse_iso_date_bound(value: str, field: str) -> date:
    if not isinstance(value, str):
        raise SourceProtocolError(f"invalid Finance {field}")
    try:
        parsed = date.fromisoformat(value)
    except ValueError:
        raise SourceProtocolError(f"invalid Finance {field}") from None
    if parsed.isoformat() != value:
        raise SourceProtocolError(f"invalid Finance {field}")
    return parsed


def _parse_finance_bas_dt(value: str) -> date:
    if not isinstance(value, str) or _ASCII_YYYYMMDD.fullmatch(value) is None:
        raise SourceProtocolError("invalid Finance basDt")
    try:
        parsed = datetime.strptime(value, "%Y%m%d").date()
    except ValueError:
        raise SourceProtocolError("invalid Finance basDt") from None
    if parsed.strftime("%Y%m%d") != value:
        raise SourceProtocolError("invalid Finance basDt")
    return parsed


def validate_finance_pilot_dates(
    dates: tuple[str, ...],
    *,
    start_date: str,
    end_date: str,
) -> tuple[str, ...]:
    """Validate one exact, caller-frozen Finance date plan without expanding it."""
    if not isinstance(dates, tuple) or not dates:
        raise SourceProtocolError("Finance pilot date plan must be a non-empty tuple")
    lower = _parse_iso_date_bound(start_date, "start date")
    upper = _parse_iso_date_bound(end_date, "end date")
    if lower > upper:
        raise SourceProtocolError("invalid Finance target date bounds")
    parsed_dates = [_parse_finance_bas_dt(value) for value in dates]
    if len(set(dates)) != len(dates):
        raise SourceProtocolError("duplicate Finance pilot date")
    if parsed_dates != sorted(parsed_dates):
        raise SourceProtocolError("Finance pilot dates must be strictly increasing")
    if any(value < lower or value > upper for value in parsed_dates):
        raise SourceProtocolError("Finance pilot date outside target bounds")
    return dates


def finance_request_params(bas_dt: str, page_no: int, requested_page_size: int) -> dict[str, str]:
    """Build the secret-free, type-stable Finance query identity material."""
    _parse_finance_bas_dt(bas_dt)
    for value, name in ((page_no, "page number"), (requested_page_size, "page size")):
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise SourceProtocolError(f"invalid Finance requested {name}")
    return {
        "basDt": bas_dt,
        "issuCmpyKsdCustNo": "",
        "numOfRows": str(requested_page_size),
        "pageNo": str(page_no),
        "resultType": "json",
        "stckIssuCmpyNm": "",
    }


def _strict_unsigned_wire_integer(value: Any, field: str, *, positive: bool = False) -> int:
    if isinstance(value, bool):
        raise SourceProtocolError(f"invalid Finance {field}")
    if isinstance(value, int):
        result = value
    elif isinstance(value, str) and _ASCII_UNSIGNED_INTEGER.fullmatch(value) is not None:
        result = int(value)
    else:
        raise SourceProtocolError(f"invalid Finance {field}")
    if result < (1 if positive else 0):
        raise SourceProtocolError(f"invalid Finance {field}")
    return result


def finance_entity_to_page(
    body: bytes,
    *,
    expected_bas_dt: str,
    expected_page_no: int,
) -> dict[str, Any]:
    """Normalize one already-custodied Finance entity into pagination input."""
    _parse_finance_bas_dt(expected_bas_dt)
    if isinstance(expected_page_no, bool) or not isinstance(expected_page_no, int) or expected_page_no <= 0:
        raise SourceProtocolError("invalid Finance expected page number")
    parsed = parse_entity_bytes(body)
    result_code = _find_first(parsed, ("resultCode",))
    if result_code in (None, ""):
        raise SourceProtocolError("Finance response missing resultCode")
    if not isinstance(result_code, str) or result_code != "00":
        raise SourceProtocolError("Finance provider resultCode failure")
    classified = classify_provider("FINANCE", parsed)
    page_no = _strict_unsigned_wire_integer(_find_first(parsed, ("pageNo",)), "pageNo", positive=True)
    page_size = _strict_unsigned_wire_integer(_find_first(parsed, ("numOfRows",)), "numOfRows", positive=True)
    total_count = _strict_unsigned_wire_integer(_find_first(parsed, ("totalCount", "totalCnt")), "totalCount")
    if page_no != expected_page_no:
        raise SourceProtocolError("Finance echoed page number mismatch")
    if total_count != classified["total_count"]:
        raise SourceProtocolError("Finance totalCount normalization mismatch")
    items = classified["items"]
    for item in items:
        observed_bas_dt = _find_first(item, ("basDt",))
        if str(observed_bas_dt or "") != expected_bas_dt:
            raise SourceProtocolError("Finance item basDt mismatch")
    return {
        "page_no": page_no,
        "page_size": page_size,
        "total_count": total_count,
        "items": items,
    }


def pagination_page_1_identity(page: Mapping[str, Any]) -> str:
    """Return the single public identity used for fresh and resumed page 1."""
    return hashlib.sha256(canonical_json_bytes({
        "page_no": page.get("page_no"),
        "page_size": page.get("page_size"),
        "total_count": page.get("total_count"),
        "items": page.get("items"),
    })).hexdigest()


def _validate_pagination_page(
    page: Mapping[str, Any],
    *,
    expected_page_no: int,
    first_total: Any,
    first_size: Any,
    seen_pages: set[bytes],
    item_count: int,
) -> int:
    """Validate one page before any later page can consume quota."""
    page_no = page.get("page_no")
    total_count = page.get("total_count")
    page_size = page.get("page_size")
    if type(page_no) is not int or page_no != expected_page_no:
        raise SourceProtocolError("pagination echoed page number mismatch")
    if type(total_count) is not int or total_count < 0:
        raise SourceProtocolError("invalid pagination totalCount")
    if type(page_size) is not int or page_size <= 0:
        raise SourceProtocolError("invalid pagination page size")
    if total_count != first_total or page_size != first_size:
        raise SourceProtocolError("pagination snapshot shifted")
    items = page.get("items")
    if not isinstance(items, list):
        raise SourceProtocolError("invalid pagination items")
    fingerprint = canonical_json_bytes(items)
    if items and fingerprint in seen_pages:
        raise SourceProtocolError("repeated whole page")
    if len(items) > first_size:
        raise SourceProtocolError("returned page exceeds page size")
    next_item_count = item_count + len(items)
    if next_item_count > first_total:
        raise SourceProtocolError("pagination item count exceeds totalCount")
    if not items and next_item_count < first_total:
        raise SourceProtocolError("empty intermediate page")
    seen_pages.add(fingerprint)
    return next_item_count


def validate_pagination_snapshot(pages: list[Mapping[str, Any]]) -> dict[str, Any]:
    """Validate one complete, immutable pagination snapshot without network I/O."""
    if not pages:
        raise SourceProtocolError("pagination snapshot has no pages")
    first_total = pages[0].get("total_count")
    first_size = pages[0].get("page_size")
    seen_pages: set[bytes] = set()
    item_count = 0
    for ordinal, page in enumerate(pages, start=1):
        item_count = _validate_pagination_page(
            page,
            expected_page_no=ordinal,
            first_total=first_total,
            first_size=first_size,
            seen_pages=seen_pages,
            item_count=item_count,
        )
    if item_count != first_total:
        raise SourceProtocolError("pagination item count does not equal totalCount")
    identity = pagination_page_1_identity(pages[0])
    return {"state": "DATE_COMPLETE", "page_count": len(pages), "item_count": item_count, "page_1_identity": identity}


def assert_resume_page_1(snapshot: Mapping[str, Any], page_1: Mapping[str, Any]) -> None:
    """Fail closed when resumed page 1 no longer matches the frozen snapshot."""
    current = pagination_page_1_identity(page_1)
    if current != snapshot.get("page_1_identity"):
        raise SourceProtocolError("resume page 1 identity or total shifted")


def collect_bounded_pagination_snapshot(
    fetch_page: Callable[[int], Mapping[str, Any]],
    *,
    max_pages: int,
    resume_snapshot: Mapping[str, Any] | None = None,
    on_page_validated: Callable[[int, Mapping[str, Any], int], None] | None = None,
) -> dict[str, Any]:
    """Collect one bounded page set and close it through the invariant validator.

    ``fetch_page`` is dependency-injected so offline tests can prove the complete
    collection path without making provider requests.  A resumed collection
    always re-reads page 1 and binds it to the prior snapshot before any later
    page is fetched.  The first returned page size is the pagination authority;
    ``max_pages`` is a caller-frozen safety ceiling, not a provider hint.
    """
    if isinstance(max_pages, bool) or not isinstance(max_pages, int) or max_pages <= 0:
        raise SourceProtocolError("invalid bounded pagination page limit")
    if resume_snapshot is not None and not isinstance(resume_snapshot, Mapping):
        raise SourceProtocolError("invalid resume snapshot")

    first_page = fetch_page(1)
    if not isinstance(first_page, Mapping):
        raise SourceProtocolError("invalid pagination page record")
    first_page = dict(first_page)
    if resume_snapshot is not None:
        assert_resume_page_1(resume_snapshot, first_page)

    total_count = first_page.get("total_count")
    page_size = first_page.get("page_size")
    if type(total_count) is not int or total_count < 0:
        raise SourceProtocolError("invalid pagination totalCount")
    if type(page_size) is not int or page_size <= 0:
        raise SourceProtocolError("invalid pagination page size")
    seen_pages: set[bytes] = set()
    item_count = _validate_pagination_page(
        first_page,
        expected_page_no=1,
        first_total=total_count,
        first_size=page_size,
        seen_pages=seen_pages,
        item_count=0,
    )
    if on_page_validated is not None:
        on_page_validated(1, first_page, item_count)
    expected_pages = max(1, (total_count + page_size - 1) // page_size)
    if expected_pages > max_pages:
        raise QuotaBoundaryError("bounded pagination page limit exceeded")

    pages: list[Mapping[str, Any]] = [first_page]
    for page_no in range(2, expected_pages + 1):
        page = fetch_page(page_no)
        if not isinstance(page, Mapping):
            raise SourceProtocolError("invalid pagination page record")
        page = dict(page)
        item_count = _validate_pagination_page(
            page,
            expected_page_no=page_no,
            first_total=total_count,
            first_size=page_size,
            seen_pages=seen_pages,
            item_count=item_count,
        )
        pages.append(page)
        if on_page_validated is not None:
            on_page_validated(page_no, page, item_count)

    snapshot = validate_pagination_snapshot(pages)
    return {
        "state": snapshot["state"],
        "pages": pages,
        "snapshot": snapshot,
        "resumed": resume_snapshot is not None,
    }


@dataclass(frozen=True)
class QuotaReservation:
    provider: str
    quota_day_kst: str
    ordinal: int
    operation: str


class QuotaLedger:
    """Single-process write-ahead quota ledger; every reserved attempt is spent."""

    def __init__(self, path: Path, now: Callable[[], datetime] | None = None) -> None:
        self.path = path
        self.now = now or (lambda: datetime.now(timezone.utc))
        self._lock = threading.Lock()

    def _day(self) -> str:
        return self.now().astimezone(KST).date().isoformat()

    def _count(self, provider: str, day: str) -> int:
        if not self.path.exists():
            return 0
        count = 0
        for line in self.path.read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            if row.get("event") == "QUOTA_SLOT_RESERVED" and row.get("provider") == provider and row.get("quota_day_kst") == day:
                count += 1
        return count

    def reserve(self, provider: str, operation: str, request_id: str) -> QuotaReservation:
        with self._lock:
            day = self._day()
            used = self._count(provider, day)
            cap = QUOTA_CAPS[provider]
            if used >= cap:
                raise QuotaBoundaryError(f"{provider} conservative quota boundary reached")
            row = {
                "event": "QUOTA_SLOT_RESERVED",
                "provider": provider,
                "quota_day_kst": day,
                "ordinal": used + 1,
                "operation": operation,
                "request_id": request_id,
                "reserved_at_utc": self.now().astimezone(timezone.utc).isoformat(),
                "known_external_attempts_minimum": 0,
                "unknown_external_attempts": True,
            }
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(canonical_json_bytes(row).decode("utf-8"))
                handle.flush()
                os.fsync(handle.fileno())
            return QuotaReservation(provider, day, used + 1, operation)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req: Any, fp: Any, code: int, msg: str, headers: Any, newurl: str) -> None:
        return None


def canonical_request_id(source_id: str, endpoint: str, operation: str, params: Mapping[str, Any]) -> str:
    material = {"source_id": source_id, "endpoint": endpoint, "operation": operation, "params": {k: params[k] for k in sorted(params)}}
    return hashlib.sha256(canonical_json_bytes(material)).hexdigest()


def fetch_entity(
    *,
    provider: str,
    source_id: str,
    endpoint: str,
    operation: str,
    params: Mapping[str, Any],
    secret: str,
    ledger: QuotaLedger,
    timeout_seconds: float = 20.0,
    opener: Any | None = None,
    sleep_fn: Callable[[float], None] = time.sleep,
) -> tuple[bytes, dict[str, Any]]:
    request_id = canonical_request_id(source_id, endpoint, operation, params)
    client = opener or urllib.request.build_opener(NoRedirect())
    last_kind = "transport"
    for attempt in range(1, MAX_ATTEMPTS + 1):
        reservation = ledger.reserve(provider, operation, request_id)
        url = encoded_query(endpoint, params, secret)
        request = urllib.request.Request(url, headers={"Accept": "application/json, application/xml;q=0.9", "User-Agent": "AAA-M3Top3-Source-Canary/1.0"})
        try:
            response = client.open(request, timeout=timeout_seconds)
            status = int(getattr(response, "status", response.getcode()))
            body = response.read()
            headers = {str(k).lower(): str(v) for k, v in response.headers.items() if str(k).lower() in SAFE_HEADERS}
            if status != 200:
                raise SourceTransportError(f"HTTP status {status}")
            assert_no_secret(body, (secret,))
            receipt = {
                "request_id": request_id,
                "provider": provider,
                "source_id": source_id,
                "endpoint": endpoint,
                "operation": operation,
                "params": {k: params[k] for k in sorted(params)},
                "attempt": attempt,
                "quota_day_kst": reservation.quota_day_kst,
                "quota_ordinal": reservation.ordinal,
                "http_status": status,
                "safe_headers": headers,
                "raw_entity_bytes_definition": "HTTP entity body after transport content-decoding and before charset/JSON/XML decoding",
                "entity_bytes": len(body),
                "entity_sha256": hashlib.sha256(body).hexdigest(),
            }
            return body, receipt
        except urllib.error.HTTPError as exc:
            status = int(exc.code)
            last_kind = f"http_{status}"
            if status not in ({429} | set(range(500, 600))) or attempt == MAX_ATTEMPTS:
                raise SourceTransportError(f"source request failed: {last_kind}") from None
            jitter = int(hashlib.sha256(f"{request_id}|{attempt}".encode()).hexdigest()[:4], 16) % 1000 / 1000.0
            sleep_fn(min(2 ** (attempt - 1), 4) + jitter)
        except (urllib.error.URLError, TimeoutError, OSError):
            last_kind = "transient_transport"
            if attempt == MAX_ATTEMPTS:
                raise SourceTransportError(f"source request failed: {last_kind}") from None
            jitter = int(hashlib.sha256(f"{request_id}|{attempt}".encode()).hexdigest()[:4], 16) % 1000 / 1000.0
            sleep_fn(min(2 ** (attempt - 1), 4) + jitter)
    raise SourceTransportError(f"source request failed: {last_kind}")


def write_sealed_entity(root: Path, body: bytes, receipt: Mapping[str, Any], secrets: tuple[str, ...]) -> Path:
    assert_no_secret(body, secrets)
    digest = hashlib.sha256(body).hexdigest()
    path = root / "staging-not-durable" / str(receipt["provider"]).lower() / str(receipt["quota_day_kst"]) / f"{digest}.entity"
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("xb") as handle:
            handle.write(body)
            handle.flush()
            os.fsync(handle.fileno())
    except FileExistsError:
        if path.read_bytes() != body:
            raise AdmissionError("raw custody digest collision")
    return path


@dataclass(frozen=True)
class FinancePilotSpec:
    """Frozen, offline-only Finance pilot inputs; dates are never auto-expanded."""

    ordered_dates: tuple[str, ...]
    target_start_date: str
    target_end_date: str
    requested_page_size: int
    max_pages_per_date: int
    max_page_acquisitions: int
    authority_binding_sha256: str
    source_id: str = FINANCE_SOURCE_ID
    operation: str = FINANCE_OPERATION


@dataclass(frozen=True)
class AcquiredRawEntity:
    """One injected raw fixture entity; this type carries no credential material."""

    body: bytes
    http_status: int
    acquired_at_utc: str
    provider_api_network_attempts: int = 0


@dataclass(frozen=True)
class CustodyWriteResult:
    storage_locator: str
    entity_bytes: int
    entity_sha256: str
    readback_bytes: int
    readback_sha256: str
    canonical: bool = False


class RawCustodySink(Protocol):
    def seal_and_verify(self, body: bytes, draft: Mapping[str, Any]) -> CustodyWriteResult:
        ...


class CheckpointStore(Protocol):
    def load(self) -> tuple[Mapping[str, Any] | None, str | None]:
        ...

    def compare_and_swap(self, value: Mapping[str, Any], expected_sha256: str | None) -> str:
        ...


class JsonCheckpointStore:
    """Canonical JSON checkpoint with process-safe CAS and atomic replacement."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self._lock = threading.Lock()

    def _load_locked(self) -> tuple[dict[str, Any] | None, str | None]:
        if not self.path.exists():
            return None, None
        raw = self.path.read_bytes()
        parsed = parse_entity_bytes(raw)
        if not isinstance(parsed, dict) or canonical_json_bytes(parsed) != raw:
            raise SourceProtocolError("non-canonical Finance checkpoint")
        return parsed, hashlib.sha256(raw).hexdigest()

    def load(self) -> tuple[Mapping[str, Any] | None, str | None]:
        with self._lock:
            return self._load_locked()

    def compare_and_swap(self, value: Mapping[str, Any], expected_sha256: str | None) -> str:
        if not isinstance(value, Mapping):
            raise SourceProtocolError("invalid Finance checkpoint")
        payload = canonical_json_bytes(dict(value))
        digest = hashlib.sha256(payload).hexdigest()
        with self._lock:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            lock_path = self.path.with_name(f".{self.path.name}.lock")
            lock_fd = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o600)
            try:
                fcntl.flock(lock_fd, fcntl.LOCK_EX)
                _, current_sha256 = self._load_locked()
                if current_sha256 != expected_sha256:
                    raise CheckpointConflictError("Finance checkpoint compare-and-swap conflict")
                temp_path = self.path.with_name(
                    f".{self.path.name}.{os.getpid()}.{threading.get_ident()}.{time.time_ns()}.tmp"
                )
                try:
                    with temp_path.open("xb") as handle:
                        handle.write(payload)
                        handle.flush()
                        os.fsync(handle.fileno())
                    os.replace(temp_path, self.path)
                    directory_fd = os.open(self.path.parent, os.O_RDONLY)
                    try:
                        os.fsync(directory_fd)
                    finally:
                        os.close(directory_fd)
                finally:
                    temp_path.unlink(missing_ok=True)
            finally:
                fcntl.flock(lock_fd, fcntl.LOCK_UN)
                os.close(lock_fd)
        return digest


def _finance_plan_identity(spec: FinancePilotSpec) -> str:
    material = {
        "source_id": spec.source_id,
        "operation": spec.operation,
        "ordered_dates": list(spec.ordered_dates),
        "requested_page_size": spec.requested_page_size,
        "max_pages_per_date": spec.max_pages_per_date,
        "max_page_acquisitions": spec.max_page_acquisitions,
    }
    return hashlib.sha256(canonical_json_bytes(material)).hexdigest()


def _validate_finance_pilot_spec(spec: FinancePilotSpec) -> str:
    if not isinstance(spec, FinancePilotSpec):
        raise SourceProtocolError("invalid Finance pilot specification")
    if spec.source_id != FINANCE_SOURCE_ID or spec.operation != FINANCE_OPERATION:
        raise SourceProtocolError("Finance pilot source identity mismatch")
    validate_finance_pilot_dates(
        spec.ordered_dates,
        start_date=spec.target_start_date,
        end_date=spec.target_end_date,
    )
    for value, field in (
        (spec.requested_page_size, "requested page size"),
        (spec.max_pages_per_date, "page ceiling"),
        (spec.max_page_acquisitions, "acquisition ceiling"),
    ):
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise SourceProtocolError(f"invalid Finance pilot {field}")
    if not isinstance(spec.authority_binding_sha256, str) or _ASCII_SHA256.fullmatch(spec.authority_binding_sha256) is None:
        raise SourceProtocolError("invalid Finance pilot authority binding")
    return _finance_plan_identity(spec)


def _checkpoint_timestamp(clock: Callable[[], datetime]) -> str:
    value = clock()
    if not isinstance(value, datetime) or value.tzinfo is None:
        raise SourceProtocolError("Finance checkpoint clock must be timezone-aware")
    return value.astimezone(timezone.utc).isoformat()


def _initial_finance_checkpoint(spec: FinancePilotSpec, plan_identity: str, timestamp: str) -> dict[str, Any]:
    return {
        "artifact": "M3TOP3_FINANCE_CA_ACQUISITION_CHECKPOINT_v1.0",
        "schema_version": 1,
        "authority_binding_sha256": spec.authority_binding_sha256,
        "source_id": spec.source_id,
        "operation": spec.operation,
        "ordered_date_plan_sha256": plan_identity,
        "ordered_dates": list(spec.ordered_dates),
        "requested_page_size": spec.requested_page_size,
        "max_pages_per_date": spec.max_pages_per_date,
        "max_page_acquisitions": spec.max_page_acquisitions,
        "page_acquisitions": 0,
        "next_date_index": 0,
        "completed_dates": [],
        "date_results": [],
        "current_date": None,
        "last_error": None,
        "provider_api_network_attempts": 0,
        "remote_raw_custody_writes": 0,
        "bulk_acquisition_authorized": False,
        "validation_claim": "NONE",
        "gate_effect": "NONE",
        "updated_at_utc": timestamp,
    }


def _assert_finance_checkpoint_binding(
    checkpoint: Mapping[str, Any],
    spec: FinancePilotSpec,
    plan_identity: str,
) -> None:
    expected = {
        "artifact": "M3TOP3_FINANCE_CA_ACQUISITION_CHECKPOINT_v1.0",
        "schema_version": 1,
        "authority_binding_sha256": spec.authority_binding_sha256,
        "source_id": spec.source_id,
        "operation": spec.operation,
        "ordered_date_plan_sha256": plan_identity,
        "ordered_dates": list(spec.ordered_dates),
        "requested_page_size": spec.requested_page_size,
        "max_pages_per_date": spec.max_pages_per_date,
        "max_page_acquisitions": spec.max_page_acquisitions,
        "provider_api_network_attempts": 0,
        "remote_raw_custody_writes": 0,
        "bulk_acquisition_authorized": False,
        "validation_claim": "NONE",
        "gate_effect": "NONE",
    }
    for field, expected_value in expected.items():
        if checkpoint.get(field) != expected_value:
            raise CheckpointConflictError(f"Finance checkpoint binding mismatch: {field}")
    completed = checkpoint.get("completed_dates")
    next_index = checkpoint.get("next_date_index")
    results = checkpoint.get("date_results")
    acquisitions = checkpoint.get("page_acquisitions")
    if not isinstance(completed, list) or completed != list(spec.ordered_dates[:len(completed)]):
        raise CheckpointConflictError("Finance checkpoint completed dates are not an ordered prefix")
    if type(next_index) is not int or next_index != len(completed):
        raise CheckpointConflictError("Finance checkpoint next date index mismatch")
    if not isinstance(results, list) or len(results) != len(completed):
        raise CheckpointConflictError("Finance checkpoint result prefix mismatch")
    if type(acquisitions) is not int or acquisitions < 0 or acquisitions > spec.max_page_acquisitions:
        raise CheckpointConflictError("Finance checkpoint acquisition count mismatch")
    current = checkpoint.get("current_date")
    if current is not None:
        if not isinstance(current, Mapping) or next_index >= len(spec.ordered_dates):
            raise CheckpointConflictError("invalid Finance current-date checkpoint")
        if current.get("basDt") != spec.ordered_dates[next_index]:
            raise CheckpointConflictError("Finance current-date checkpoint is not next in plan")


def _validate_acquired_raw_entity(entity: AcquiredRawEntity) -> None:
    if not isinstance(entity, AcquiredRawEntity) or not isinstance(entity.body, bytes):
        raise SourceProtocolError("invalid injected Finance raw entity")
    if type(entity.http_status) is not int or entity.http_status != 200:
        raise SourceProtocolError("invalid injected Finance HTTP status")
    if entity.provider_api_network_attempts != 0:
        raise SourceProtocolError("offline Finance pilot rejected provider network activity")
    try:
        observed = datetime.fromisoformat(entity.acquired_at_utc.replace("Z", "+00:00"))
    except (AttributeError, ValueError):
        raise SourceProtocolError("invalid Finance acquisition timestamp") from None
    if observed.tzinfo is None or observed.utcoffset() != timedelta(0):
        raise SourceProtocolError("Finance acquisition timestamp must be UTC")


def _validate_offline_custody_result(result: CustodyWriteResult, body: bytes) -> None:
    digest = hashlib.sha256(body).hexdigest()
    if not isinstance(result, CustodyWriteResult) or result.canonical:
        raise SourceProtocolError("offline Finance custody cannot be canonical")
    if not isinstance(result.storage_locator, str) or not result.storage_locator:
        raise SourceProtocolError("invalid offline Finance custody locator")
    if (
        result.entity_bytes != len(body)
        or result.readback_bytes != len(body)
        or result.entity_sha256 != digest
        or result.readback_sha256 != digest
    ):
        raise SourceProtocolError("offline Finance custody readback mismatch")


def run_finance_historical_pilot(
    spec: FinancePilotSpec,
    *,
    reserve_attempt: Callable[[str, str, str], QuotaReservation],
    acquire_raw_once: Callable[[Mapping[str, str], QuotaReservation], AcquiredRawEntity],
    leak_scan: Callable[[bytes], None],
    custody_sink: RawCustodySink,
    custody_index_append: Callable[[Mapping[str, Any]], None],
    checkpoint_store: CheckpointStore,
    clock: Callable[[], datetime],
) -> dict[str, Any]:
    """Run a secret-free, no-network Finance pilot over injected raw fixtures."""
    plan_identity = _validate_finance_pilot_spec(spec)
    loaded, checkpoint_sha256 = checkpoint_store.load()
    if loaded is None:
        checkpoint = _initial_finance_checkpoint(spec, plan_identity, _checkpoint_timestamp(clock))
        checkpoint_sha256 = checkpoint_store.compare_and_swap(checkpoint, None)
    else:
        if not isinstance(loaded, Mapping):
            raise SourceProtocolError("invalid Finance checkpoint record")
        checkpoint = json.loads(canonical_json_bytes(dict(loaded)).decode("utf-8"))
    _assert_finance_checkpoint_binding(checkpoint, spec, plan_identity)

    while checkpoint["next_date_index"] < len(spec.ordered_dates):
        bas_dt = spec.ordered_dates[checkpoint["next_date_index"]]
        prior_current = checkpoint.get("current_date")
        prior_page_1_identity = None
        prior_custody_refs: list[dict[str, Any]] = []
        if isinstance(prior_current, Mapping) and prior_current.get("basDt") == bas_dt:
            prior_page_1_identity = prior_current.get("page_1_identity")
            prior_refs = prior_current.get("custody_refs", [])
            if isinstance(prior_refs, list) and all(isinstance(row, dict) for row in prior_refs):
                prior_custody_refs = list(prior_refs)
        checkpoint["current_date"] = {
            "basDt": bas_dt,
            "state": "IN_PROGRESS",
            "page_1_identity": prior_page_1_identity,
            "first_total_count": None,
            "first_returned_page_size": None,
            "expected_pages": None,
            "validated_pages": [],
            "custody_refs": prior_custody_refs,
        }
        checkpoint["last_error"] = None
        checkpoint["updated_at_utc"] = _checkpoint_timestamp(clock)
        checkpoint_sha256 = checkpoint_store.compare_and_swap(checkpoint, checkpoint_sha256)

        page_refs: dict[int, dict[str, Any]] = {}

        def save_checkpoint() -> None:
            nonlocal checkpoint_sha256
            checkpoint["updated_at_utc"] = _checkpoint_timestamp(clock)
            checkpoint_sha256 = checkpoint_store.compare_and_swap(checkpoint, checkpoint_sha256)

        def fetch_page(page_no: int) -> Mapping[str, Any]:
            if checkpoint["page_acquisitions"] >= spec.max_page_acquisitions:
                raise QuotaBoundaryError("Finance pilot acquisition ceiling reached")
            params = finance_request_params(bas_dt, page_no, spec.requested_page_size)
            request_id = canonical_request_id(spec.source_id, FINANCE_URL, spec.operation, params)
            reservation = reserve_attempt("FINANCE", spec.operation, request_id)
            if not isinstance(reservation, QuotaReservation):
                raise SourceProtocolError("invalid Finance quota reservation")
            if (
                reservation.provider != "FINANCE"
                or reservation.operation != spec.operation
                or type(reservation.ordinal) is not int
                or reservation.ordinal <= 0
            ):
                raise SourceProtocolError("Finance quota reservation mismatch")
            try:
                quota_day = date.fromisoformat(reservation.quota_day_kst)
            except (TypeError, ValueError):
                raise SourceProtocolError("invalid Finance quota day") from None
            if quota_day.isoformat() != reservation.quota_day_kst:
                raise SourceProtocolError("invalid Finance quota day")

            acquired = acquire_raw_once(params, reservation)
            _validate_acquired_raw_entity(acquired)
            leak_scan(acquired.body)
            digest = hashlib.sha256(acquired.body).hexdigest()
            draft = {
                "source_id": spec.source_id,
                "operation": spec.operation,
                "safe_params": dict(params),
                "request_id": request_id,
                "attempt": 1,
                "quota_day_kst": reservation.quota_day_kst,
                "http_status": acquired.http_status,
                "entity_bytes": len(acquired.body),
                "entity_sha256": digest,
                "acquired_at_utc": acquired.acquired_at_utc,
            }
            custody = custody_sink.seal_and_verify(acquired.body, draft)
            _validate_offline_custody_result(custody, acquired.body)
            raw_record = {**draft, "storage_locator": custody.storage_locator}
            prohibited = {
                "servicekey", "credential_value", "credential_hash", "credential_prefix",
                "authenticated_url", "request_headers", "location",
            }
            if any(str(key).lower() in prohibited for key in raw_record):
                raise CredentialContractError("prohibited field in Finance raw custody record")
            custody_index_append(raw_record)
            reference = {
                "page_no": page_no,
                "request_id": request_id,
                "attempt": 1,
                "quota_day_kst": reservation.quota_day_kst,
                "quota_ordinal": reservation.ordinal,
                "entity_bytes": len(acquired.body),
                "entity_sha256": digest,
                "storage_locator": custody.storage_locator,
                "canonical": False,
            }
            if reference not in checkpoint["current_date"]["custody_refs"]:
                checkpoint["current_date"]["custody_refs"].append(reference)
            checkpoint["current_date"]["state"] = "RAW_SEALED"
            checkpoint["page_acquisitions"] += 1
            save_checkpoint()
            page = finance_entity_to_page(
                acquired.body,
                expected_bas_dt=bas_dt,
                expected_page_no=page_no,
            )
            page_refs[page_no] = reference
            return page

        def on_page_validated(page_no: int, page: Mapping[str, Any], cumulative_item_count: int) -> None:
            reference = page_refs.get(page_no)
            if reference is None:
                raise SourceProtocolError("Finance validated page missing custody reference")
            current = checkpoint["current_date"]
            current["state"] = "PAGE_VALIDATED"
            current["validated_pages"].append({
                **reference,
                "cumulative_item_count": cumulative_item_count,
            })
            if page_no == 1:
                current["page_1_identity"] = pagination_page_1_identity(page)
                current["first_total_count"] = page["total_count"]
                current["first_returned_page_size"] = page["page_size"]
                current["expected_pages"] = max(
                    1,
                    (page["total_count"] + page["page_size"] - 1) // page["page_size"],
                )
            save_checkpoint()

        resume_snapshot = None
        if prior_page_1_identity is not None:
            if not isinstance(prior_page_1_identity, str) or _ASCII_SHA256.fullmatch(prior_page_1_identity) is None:
                raise CheckpointConflictError("invalid Finance resume page-1 identity")
            resume_snapshot = {"page_1_identity": prior_page_1_identity}
        try:
            collected = collect_bounded_pagination_snapshot(
                fetch_page,
                max_pages=spec.max_pages_per_date,
                resume_snapshot=resume_snapshot,
                on_page_validated=on_page_validated,
            )
        except Exception as exc:
            if checkpoint.get("current_date") is not None:
                checkpoint["current_date"]["state"] = "BLOCKED"
                checkpoint["last_error"] = type(exc).__name__
                try:
                    save_checkpoint()
                except CheckpointConflictError:
                    raise
            raise

        date_result = {
            "basDt": bas_dt,
            "state": "DATE_COMPLETE",
            "snapshot": collected["snapshot"],
            "custody_refs": list(checkpoint["current_date"]["custody_refs"]),
            "valid_empty": collected["snapshot"]["item_count"] == 0,
        }
        checkpoint["completed_dates"].append(bas_dt)
        checkpoint["date_results"].append(date_result)
        checkpoint["next_date_index"] += 1
        checkpoint["current_date"] = None
        checkpoint["last_error"] = None
        save_checkpoint()

    all_empty = all(result["valid_empty"] for result in checkpoint["date_results"])
    return {
        "state": "STOP_NO_PROMOTION" if all_empty else "OFFLINE_FIXTURE_COMPLETE_NO_PROMOTION",
        "source_id": spec.source_id,
        "operation": spec.operation,
        "ordered_date_plan_sha256": plan_identity,
        "completed_dates": list(checkpoint["completed_dates"]),
        "date_results": list(checkpoint["date_results"]),
        "page_acquisitions": checkpoint["page_acquisitions"],
        "checkpoint_sha256": checkpoint_sha256,
        "provider_api_network_attempts": 0,
        "remote_raw_custody_writes": 0,
        "bulk_acquisition_authorized": False,
        "validation_claim": "NONE",
        "gate_effect": "NONE",
    }


def preflight_environment() -> dict[str, str]:
    for name in SECRET_NAMES:
        validate_decoded_secret(name, os.environ.get(name))
    return {name: "PRESENT_DECODED_FORM_VALIDATED" for name in SECRET_NAMES}


def _main() -> int:
    parser = argparse.ArgumentParser(description="M3Top3 public-data source canary primitives")
    parser.add_argument("command", choices=("preflight",))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.command == "preflight":
        result = {"state": "PREFLIGHT_PASS", "credentials": preflight_environment(), "secret_values_persisted": False}
        payload = canonical_json_bytes(result)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_bytes(payload)
        else:
            print(payload.decode("utf-8"), end="")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(_main())
    except AdmissionError as exc:
        print(f"SOURCE_ADMISSION_BLOCKED: {exc}")
        raise SystemExit(2)
