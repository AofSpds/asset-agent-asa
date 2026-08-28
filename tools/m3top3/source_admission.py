#!/usr/bin/env python3
"""Fail-closed primitives for the M3Top3 public-data source canaries.

This module is additive and deliberately does not touch production providers,
model semantics, PIT semantics, or active manifests.  It supports only source
preflight/canary evidence until the durable raw-data plane and endpoint identity
gates are closed.
"""

from __future__ import annotations

import argparse
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
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Mapping
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
QUOTA_CAPS = {"KSD": 80, "FINANCE": 8000}
SAFE_HEADERS = {"content-type", "content-length", "date", "etag", "last-modified"}
KSD_MARKET_NAME_FIELDS = ("listNm", "caltotMartTpcdNm", "lstgScrsItmsKcdNm", "scrsItmsKcdNm", "mrktNm", "marketNm")
_PERCENT_TRIPLET = re.compile(r"%[0-9A-Fa-f]{2}")


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
    identity = hashlib.sha256(canonical_json_bytes({
        "page_no": 1,
        "page_size": first_size,
        "total_count": first_total,
        "items": pages[0].get("items"),
    })).hexdigest()
    return {"state": "DATE_COMPLETE", "page_count": len(pages), "item_count": item_count, "page_1_identity": identity}


def assert_resume_page_1(snapshot: Mapping[str, Any], page_1: Mapping[str, Any]) -> None:
    """Fail closed when resumed page 1 no longer matches the frozen snapshot."""
    current = hashlib.sha256(canonical_json_bytes({
        "page_no": page_1.get("page_no"),
        "page_size": page_1.get("page_size"),
        "total_count": page_1.get("total_count"),
        "items": page_1.get("items"),
    })).hexdigest()
    if current != snapshot.get("page_1_identity"):
        raise SourceProtocolError("resume page 1 identity or total shifted")


def collect_bounded_pagination_snapshot(
    fetch_page: Callable[[int], Mapping[str, Any]],
    *,
    max_pages: int,
    resume_snapshot: Mapping[str, Any] | None = None,
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
