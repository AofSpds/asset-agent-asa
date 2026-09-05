"""Deterministic upstream market-input builder for the bounded F05-R1 W1 run.

This module does not score, rank, infer corporate actions, adjust prices, include
dividends, read outcomes, or write artifacts.  It admits only the Owner-bound
KRX daily ``ChangesRatio`` semantics and materializes the three raw inputs that
the unchanged F05 feature implementation already consumes.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import date
from decimal import ROUND_HALF_EVEN, Decimal, localcontext
from pathlib import Path, PurePosixPath
from typing import Any, Mapping, Sequence

from .providers import PriceRow

F05_FEATURE_ID = "F05_MARKET_POSITIONING_BALANCE"
EXPECTED_W1_DENOMINATOR = 57
EXPECTED_W1_COHORT_IDENTITY_SHA256 = "c72593633c88cb6913c703da626b95d6111c7b0fa5783ccef6d373b2adf8c546"
EXPECTED_W1_COHORT_ARTIFACT_SHA256 = "8ac8ba439b3decb2690e04ec8fa7d40e40c37dd1ab0329bf3d24bf8253eba6a1"
EXPECTED_PRICE_DATASET_ID = "SEMI-PRICE-MARCAP-KRX-2024-2026_v1"
EXPECTED_PRICE_PARQUET_SHA256 = "b0c38943e67637d5faf88429880092cf0f46a394be39860dd3bcd0b04231bccb"
EXPECTED_SOURCE_SEMANTICS = "RAW_IMMUTABLE_NOT_PRICE_CANONICAL"
RETURN_SEMANTICS = "KRX_CHANGES_RATIO_CA_REFERENCE_PRICE_CHANGE_NO_DIVIDEND_v1"
TURNOVER_SEMANTICS = "DAILY_VOLUME_DIVIDED_BY_LISTED_STOCKS_20_OVER_PRIOR_20_v1"
RETURN_SOURCE_FIELD = "ChangesRatio"
RETURN_SOURCE_UNIT = "PERCENT"
RETURN_SOURCE_SCALE = Decimal(100)
CONSUMED_SOURCE_FIELDS = (
    "Date", "Code", "Close", "Changes", "ChangesRatio", "Volume", "Amount", "Stocks",
)
RETURN_20_INTERVALS = 20
RETURN_60_INTERVALS = 60
REQUIRED_OBSERVATIONS = RETURN_60_INTERVALS + 1
W1_CUTOFF_DATE = date(2024, 8, 9)
W1_SESSION_DATES = tuple(date.fromisoformat(value) for value in (
    "2024-05-16", "2024-05-17", "2024-05-20", "2024-05-21", "2024-05-22",
    "2024-05-23", "2024-05-24", "2024-05-27", "2024-05-28", "2024-05-29",
    "2024-05-30", "2024-05-31", "2024-06-03", "2024-06-04", "2024-06-05",
    "2024-06-07", "2024-06-10", "2024-06-11", "2024-06-12", "2024-06-13",
    "2024-06-14", "2024-06-17", "2024-06-18", "2024-06-19", "2024-06-20",
    "2024-06-21", "2024-06-24", "2024-06-25", "2024-06-26", "2024-06-27",
    "2024-06-28", "2024-07-01", "2024-07-02", "2024-07-03", "2024-07-04",
    "2024-07-05", "2024-07-08", "2024-07-09", "2024-07-10", "2024-07-11",
    "2024-07-12", "2024-07-15", "2024-07-16", "2024-07-17", "2024-07-18",
    "2024-07-19", "2024-07-22", "2024-07-23", "2024-07-24", "2024-07-25",
    "2024-07-26", "2024-07-29", "2024-07-30", "2024-07-31", "2024-08-01",
    "2024-08-02", "2024-08-05", "2024-08-06", "2024-08-07", "2024-08-08",
    "2024-08-09",
))
EXPECTED_W1_SESSION_GRID_SHA256 = "8667d8b63eeaa5332b0c1390dec179c43c692591a7c3db4c5b1a6cf31217a911"
DECIMAL_PRECISION = 64
# Name is display metadata, not the governed identity field.  Security identity
# is bound by exact Code <-> company_id matching; no issuer-name claim is made.
IDENTITY_SOURCE_FIELD = "Code"
DISPLAY_NAME_CONSUMED = False
EXPECTED_CA_MARKET_ROWS = {
    ("083450", date(2024, 6, 26)): {
        "close": Decimal("21600"), "changes": Decimal("-100"),
        "changes_ratio": Decimal("-0.46"),
    },
    ("083450", date(2024, 7, 24)): {"stocks": Decimal("18618260")},
    ("092870", date(2024, 6, 3)): {
        "close": Decimal("20400"), "changes": Decimal("930"),
        "changes_ratio": Decimal("4.78"),
    },
    ("092870", date(2024, 7, 31)): {
        "volume": Decimal("814284"), "stocks": Decimal("13050797"),
    },
}
REQUIRED_CA_RECORDS = {
    "KRX-20240625001437": {
        "company_id": "KRX:083450",
        "published_date": "2024-06-25",
        "url": "https://kind.krx.co.kr/external/2024/06/25/000508/20240625001437/70766.htm",
        "event_group_id": "CA-KRX-083450-20240626-EX_RIGHT",
        "facts": {
            "security_code": "A083450", "base_price_krw": 21700,
            "effective_date": "2024-06-26", "reason": "bonus issue",
        },
    },
    "KRX-20240724001584": {
        "company_id": "KRX:083450",
        "published_date": "2024-07-24",
        "url": "https://kind.krx.co.kr/external/2024/07/24/000527/20240724001584/70791.htm",
        "event_group_id": "CA-KRX-083450-20240724-NEW_SHARE_LISTING",
        "facts": {
            "new_ordinary_shares": 9300515, "post_listing_total_shares": 18618260,
            "listing_date": "2024-07-24", "reason": "bonus issue",
        },
    },
    "KRX-20240531001190": {
        "company_id": "KRX:092870",
        "published_date": "2024-05-31",
        "url": "https://kind.krx.co.kr/common/disclsviewer.do?method=search&acptno=20240531001190&docno=&viewerhost=&viewport=",
        "event_group_id": "CA-KRX-092870-20240603-EX_RIGHT",
        "facts": {
            "security_code": "A092870", "base_price_krw": 19470,
            "effective_date": "2024-06-03", "reason": "rights issue",
        },
    },
    "KRX-20240726001822": {
        "company_id": "KRX:092870",
        "published_date": "2024-07-26",
        "url": "https://kind.krx.co.kr/external/2024/07/26/000831/20240726001822/70791.htm",
        "event_group_id": "CA-KRX-092870-20240731-NEW_SHARE_LISTING",
        "facts": {
            "new_ordinary_shares": 2202000, "post_listing_total_shares": 13050797,
            "listing_date": "2024-07-31", "reason": "rights issue",
        },
    },
}
REQUIRED_CA_CUSTODY_URLS = {
    "GST-ISSUER-20240611-BONUS": "https://www.gst-in.com/cn/board/board.php?bbsid=ir&idx=66&pg=3",
    "KRX-20240625001437": "https://kind.krx.co.kr/external/2024/06/25/000508/20240625001437/70766.htm",
    "KRX-20240724001584": "https://kind.krx.co.kr/external/2024/07/24/000527/20240724001584/70791.htm",
    "KRX-20240709000202": "https://kind.krx.co.kr/external/2024/07/09/000130/20240709000202/11306.htm",
    "KRX-20240531001190-VIEWER": "https://kind.krx.co.kr/common/disclsviewer.do?method=search&acptno=20240531001190&docno=&viewerhost=&viewport=",
    "KRX-20240531001190-RESOLUTION": "https://kind.krx.co.kr/common/disclsviewer.do?method=searchContents&acptNo=20240531001190&docNo=20240531002320",
    "KRX-20240531002320": "https://kind.krx.co.kr/external/2024/05/31/001190/20240531002320/70766.htm",
    "KRX-20240726001822": "https://kind.krx.co.kr/external/2024/07/26/000831/20240726001822/70791.htm",
    "KRX-BASE-PRICE-OVERVIEW": "https://global.krx.co.kr/contents/GLB/06/0602/0602020202/GLB0602020202T2.jsp",
    "KRX-EX-RIGHT-FORMULA": "https://global.krx.co.kr/contents/GLB/06/0602/0602020202/GLB0602020202T3.jsp",
    "KRX-BASE-PRICE-ADJUSTMENT-CASES": "https://global.krx.co.kr/contents/GLB/06/0602/0602010201/GLB0602010201T6.jsp",
}
EXPECTED_CA_BODY_BINDINGS = {
    "GST-ISSUER-20240611-BONUS": (16089, "5054a1f0063cb47cb8d649bf6ccda1c1475fc92c788240923642027bdfba6577"),
    "KRX-20240625001437": (3275, "16a46a0afa2664f3e902269821967fa9eaff0eb4c07bda2dd388a6487268a3c7"),
    "KRX-20240724001584": (9418, "0f1a3e786f5499054815b82d301c1079f01b083532664bc5adca3bdd806affef"),
    "KRX-20240709000202": (38322, "c7750d7dafb871ca77ca765eda8947b5ecea7bc232da9579beefbcea380d15f6"),
    "KRX-20240531001190-VIEWER": (24303, "4a0555676633a24b055b20d458c09678522831e84fce0f838075ec69642d2407"),
    "KRX-20240531001190-RESOLUTION": (968, "ef470fe4bc04b4af08aaf0c0321572ee850efcb320ec7c740bda03a72ad1a781"),
    "KRX-20240531002320": (3281, "17a99ebb63495fbb964216b4a9de167b953af63570e9d91a3d00281e1ad9e102"),
    "KRX-20240726001822": (6723, "3f3c8127aa0e04a88376ecc80e27d16fe0679c4f268bea82a47f406cdbb5008c"),
    "KRX-BASE-PRICE-OVERVIEW": (1878, "497eb707fd5bb077518b772be2922830449e7a52b6528db1b34ed39149175c4e"),
    "KRX-EX-RIGHT-FORMULA": (4362, "0ac0f7ab0837a83d662b996c0ed7da111b5b2f7d0b045b16bdf926242d407e03"),
    "KRX-BASE-PRICE-ADJUSTMENT-CASES": (10440, "89f1f30449e6b93ecd7f8d47a8604737f85dfefb3e6051a21f0ef1e24c73dd62"),
}
CA_CUSTODY_IDS_BY_COMPANY = {
    "KRX:083450": (
        "GST-ISSUER-20240611-BONUS", "KRX-20240625001437", "KRX-20240724001584",
    ),
    "KRX:092870": (
        "KRX-20240709000202", "KRX-20240531001190-VIEWER",
        "KRX-20240531001190-RESOLUTION", "KRX-20240531002320",
        "KRX-20240726001822",
    ),
}
CA_RULE_CUSTODY_IDS = (
    "KRX-BASE-PRICE-OVERVIEW", "KRX-EX-RIGHT-FORMULA",
    "KRX-BASE-PRICE-ADJUSTMENT-CASES",
)


class F05InputError(ValueError):
    """An input failed the exact F05-R1 admission contract."""


@dataclass(frozen=True)
class F05CohortMember:
    company_id: str
    krx_code: str


@dataclass(frozen=True)
class F05SourceBinding:
    dataset_id: str
    parquet_sha256: str
    source_semantics: str = EXPECTED_SOURCE_SEMANTICS
    consumed_fields: tuple[str, ...] = CONSUMED_SOURCE_FIELDS
    session_grid_sha256: str = EXPECTED_W1_SESSION_GRID_SHA256


@dataclass(frozen=True)
class F05CAValidation:
    event_group_ids_by_company: Mapping[str, tuple[str, ...]]
    source_refs_by_company: Mapping[str, tuple[str, ...]]
    semantic_sha256: str
    custody_semantic_sha256: str
    global_source_refs: tuple[str, ...]


@dataclass(frozen=True)
class F05MarketMetrics:
    company_id: str
    krx_code: str
    trailing_20d_total_return: Decimal
    trailing_60d_total_return: Decimal
    turnover_acceleration: Decimal
    observation_dates: tuple[date, ...]
    return_20_source_slice_sha256: str
    return_60_source_slice_sha256: str
    turnover_source_slice_sha256: str


def _decimal_text(value: Decimal) -> str:
    """Return a non-exponent, lossless JSON-safe decimal representation."""
    if not value.is_finite():
        raise F05InputError("non-finite derived decimal")
    rendered = format(value, "f")
    if "." in rendered:
        rendered = rendered.rstrip("0").rstrip(".")
    return "0" if rendered in {"", "-0"} else rendered


def _require_decimal(value: Any, field: str, *, positive: bool = False) -> Decimal:
    if value is None or isinstance(value, bool):
        raise F05InputError(f"{field} is missing or invalid")
    try:
        parsed = value if isinstance(value, Decimal) else Decimal(str(value))
    except Exception as exc:
        raise F05InputError(f"{field} is not an exact decimal") from exc
    if not parsed.is_finite() or (positive and parsed <= 0):
        requirement = "positive finite" if positive else "finite"
        raise F05InputError(f"{field} must be {requirement}")
    return parsed


def _require_integral_positive(value: Any, field: str) -> Decimal:
    parsed = _require_decimal(value, field, positive=True)
    if parsed != parsed.to_integral_value():
        raise F05InputError(f"{field} must be an integral positive value")
    return parsed


def _session_digest(dates: Sequence[date]) -> str:
    return hashlib.sha256("\n".join(value.isoformat() for value in dates).encode("ascii")).hexdigest()


def _source_slice_digest(rows: Sequence[PriceRow], fields: Sequence[str]) -> str:
    values = []
    for row in rows:
        by_field = {
            "Date": row.date.isoformat(),
            "Code": row.code,
            "Close": _decimal_text(_require_decimal(row.close, "Close")),
            "Changes": _decimal_text(_require_decimal(row.changes, "Changes")),
            "ChangesRatio": _decimal_text(_require_decimal(row.changes_ratio, "ChangesRatio")),
            "Volume": _decimal_text(_require_integral_positive(row.volume, "Volume")),
            "Amount": _decimal_text(_require_integral_positive(row.amount, "Amount")),
            "Stocks": _decimal_text(_require_integral_positive(row.stocks, "Stocks")),
        }
        values.append([by_field[field] for field in fields])
    payload = repr((tuple(fields), tuple(tuple(value) for value in values))).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _validate_source_binding(binding: F05SourceBinding) -> None:
    if not isinstance(binding, F05SourceBinding):
        raise F05InputError("source_binding must be an F05SourceBinding")
    if binding.dataset_id != EXPECTED_PRICE_DATASET_ID:
        raise F05InputError("unapproved F05-R1 price dataset_id")
    if binding.parquet_sha256.lower() != EXPECTED_PRICE_PARQUET_SHA256:
        raise F05InputError("unapproved F05-R1 price Parquet SHA-256")
    if binding.source_semantics != EXPECTED_SOURCE_SEMANTICS:
        raise F05InputError("unapproved F05-R1 source semantics")
    if tuple(binding.consumed_fields) != CONSUMED_SOURCE_FIELDS:
        raise F05InputError("F05-R1 consumed source field contract changed")
    if binding.session_grid_sha256 != EXPECTED_W1_SESSION_GRID_SHA256:
        raise F05InputError("F05-R1 governed W1 session grid binding changed")


def _validate_ca_source_custody(
    custody: Mapping[str, Any], custody_root: Path
) -> tuple[dict[str, tuple[str, ...]], str]:
    if not isinstance(custody, Mapping):
        raise F05InputError("CA source custody must be a mapping")
    if custody.get("status") != "EXACT_RESPONSE_BYTES_VENDORED_AND_HASHED":
        raise F05InputError("official CA source response bytes are not closed")
    for field in (
        "new_economic_provider", "credential", "paid_source", "budget_used",
        "post_cutoff_economic_input", "adjustment_factor_inferred",
    ):
        if custody.get(field) is not False:
            raise F05InputError(f"CA source custody boundary changed: {field}")
    files = custody.get("files")
    if not isinstance(files, list) or not all(isinstance(item, Mapping) for item in files):
        raise F05InputError("CA source custody files are missing or invalid")
    by_id: dict[str, Mapping[str, Any]] = {}
    refs: dict[str, tuple[str, ...]] = {}
    root = custody_root.resolve()
    for item in files:
        evidence_id = item.get("evidence_id")
        if not isinstance(evidence_id, str) or evidence_id in by_id:
            raise F05InputError("CA custody evidence IDs must be present and unique")
        by_id[evidence_id] = item
    for evidence_id, expected_url in REQUIRED_CA_CUSTODY_URLS.items():
        item = by_id.get(evidence_id)
        if item is None or item.get("url") != expected_url:
            raise F05InputError(f"required CA custody source mismatch: {evidence_id}")
        expected_bytes, expected_sha = EXPECTED_CA_BODY_BINDINGS[evidence_id]
        if item.get("bytes") != expected_bytes or item.get("sha256") != expected_sha:
            raise F05InputError(f"unapproved CA custody body binding: {evidence_id}")
        relative = item.get("path")
        if not isinstance(relative, str):
            raise F05InputError(f"CA custody path is missing: {evidence_id}")
        pure = PurePosixPath(relative)
        if pure.is_absolute() or "\\" in relative or any(part in {"", ".", ".."} for part in pure.parts):
            raise F05InputError(f"unsafe CA custody path: {evidence_id}")
        target = (root / Path(*pure.parts)).resolve()
        try:
            target.relative_to(root)
        except ValueError as exc:
            raise F05InputError(f"CA custody path escaped its root: {evidence_id}") from exc
        if not target.is_file():
            raise F05InputError(f"CA custody file is missing: {evidence_id}")
        data = target.read_bytes()
        declared_bytes = item.get("bytes")
        declared_sha = item.get("sha256")
        if (
            isinstance(declared_bytes, bool) or not isinstance(declared_bytes, int)
            or declared_bytes != len(data)
            or not isinstance(declared_sha, str)
            or re.fullmatch(r"[0-9a-f]{64}", declared_sha) is None
            or hashlib.sha256(data).hexdigest() != declared_sha
        ):
            raise F05InputError(f"CA custody byte/hash mismatch: {evidence_id}")
        refs[evidence_id] = (
            f"OFFICIAL_CA_BODY_SHA256:{declared_sha}",
            f"OFFICIAL_CA_CUSTODY_PATH:{relative}",
        )
    canonical = json.dumps(custody, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return refs, hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def validate_required_ca_evidence(
    manifest: Mapping[str, Any],
    source_custody: Mapping[str, Any],
    custody_root: Path,
) -> F05CAValidation:
    """Validate the four exact official CA boundaries required by F05-R1."""
    if not isinstance(manifest, Mapping):
        raise F05InputError("CA evidence manifest must be a mapping")
    if manifest.get("cutoff_date") != W1_CUTOFF_DATE.isoformat():
        raise F05InputError("CA evidence manifest cutoff date changed")
    if manifest.get("status") != "OFFICIAL_EVIDENCE_CLOSED":
        raise F05InputError("required official CA evidence is not closed")
    if manifest.get("adjustment_factor_inferred") is not False:
        raise F05InputError("CA manifest must prove that no adjustment factor was inferred")
    post_cutoff = manifest.get("post_cutoff_material")
    if not isinstance(post_cutoff, Mapping) or post_cutoff.get("used_in_input_or_score") is not False:
        raise F05InputError("CA manifest does not preserve the post-cutoff input firewall")
    records = manifest.get("records")
    if not isinstance(records, list) or not all(isinstance(item, Mapping) for item in records):
        raise F05InputError("CA evidence manifest records are missing or invalid")
    by_id: dict[str, Mapping[str, Any]] = {}
    for record in records:
        evidence_id = record.get("evidence_id")
        if not isinstance(evidence_id, str) or evidence_id in by_id:
            raise F05InputError("CA evidence IDs must be present and unique")
        by_id[evidence_id] = record

    rules = by_id.get("KRX-BASE-PRICE-RULES")
    expected_rule_urls = [REQUIRED_CA_CUSTODY_URLS[value] for value in CA_RULE_CUSTODY_IDS]
    if (
        rules is None or rules.get("authority") != "KRX"
        or rules.get("pit_admissible") != "CONTROL_SEMANTICS_ONLY"
        or rules.get("urls") != expected_rule_urls
    ):
        raise F05InputError("official KRX CA-reference rule binding is missing or changed")

    custody_refs, custody_semantic_sha256 = _validate_ca_source_custody(
        source_custody, custody_root
    )

    event_groups: dict[str, list[str]] = {}
    source_refs: dict[str, list[str]] = {}
    for evidence_id, expected in REQUIRED_CA_RECORDS.items():
        record = by_id.get(evidence_id)
        if record is None:
            raise F05InputError(f"required official CA evidence is missing: {evidence_id}")
        for field in ("company_id", "published_date", "url"):
            if record.get(field) != expected[field]:
                raise F05InputError(f"official CA {field} mismatch: {evidence_id}")
        if record.get("authority") != "KRX" or record.get("pit_admissible") is not True:
            raise F05InputError(f"official cutoff-safe KRX status mismatch: {evidence_id}")
        facts = record.get("facts")
        if not isinstance(facts, Mapping):
            raise F05InputError(f"official CA facts missing: {evidence_id}")
        for field, value in expected["facts"].items():
            if facts.get(field) != value:
                raise F05InputError(f"official CA fact mismatch: {evidence_id}/{field}")
        if date.fromisoformat(record["published_date"]) > W1_CUTOFF_DATE:
            raise F05InputError(f"post-cutoff CA evidence is inadmissible: {evidence_id}")
        company_id = str(expected["company_id"])
        event_groups.setdefault(company_id, []).append(str(expected["event_group_id"]))
        source_refs.setdefault(company_id, []).extend((
            f"OFFICIAL_CA_EVIDENCE_ID:{evidence_id}",
            f"OFFICIAL_CA_URL:{expected['url']}",
        ))
    for company_id, evidence_ids in CA_CUSTODY_IDS_BY_COMPANY.items():
        for evidence_id in evidence_ids:
            source_refs.setdefault(company_id, []).extend(custody_refs[evidence_id])

    canonical = json.dumps(manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    global_refs = []
    for evidence_id in CA_RULE_CUSTODY_IDS:
        global_refs.extend(custody_refs[evidence_id])
    return F05CAValidation(
        event_group_ids_by_company={
            key: tuple(sorted(value)) for key, value in event_groups.items()
        },
        source_refs_by_company={
            key: tuple(sorted(value)) for key, value in source_refs.items()
        },
        semantic_sha256=hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
        custody_semantic_sha256=custody_semantic_sha256,
        global_source_refs=tuple(sorted(global_refs)),
    )


def _normalize_member(value: F05CohortMember | Mapping[str, Any]) -> F05CohortMember:
    if isinstance(value, F05CohortMember):
        member = value
    elif isinstance(value, Mapping):
        try:
            member = F05CohortMember(str(value["company_id"]), str(value["krx_code"]))
        except KeyError as exc:
            raise F05InputError("cohort member is missing company_id or krx_code") from exc
    else:
        raise F05InputError("cohort member must be F05CohortMember or a mapping")
    if re.fullmatch(r"\d{6}", member.krx_code) is None:
        raise F05InputError(f"invalid six-digit KRX code: {member.krx_code!r}")
    if member.company_id != f"KRX:{member.krx_code}":
        raise F05InputError(
            f"company/security identity mismatch: {member.company_id!r} vs {member.krx_code!r}"
        )
    return member


def _validate_company_rows(
    member: F05CohortMember,
    rows: Sequence[PriceRow],
    cutoff_date: date,
) -> tuple[PriceRow, ...]:
    if not isinstance(cutoff_date, date):
        raise F05InputError("cutoff_date must be a date")
    if cutoff_date != W1_CUTOFF_DATE:
        raise F05InputError(
            f"F05-R1 cutoff must remain {W1_CUTOFF_DATE.isoformat()}"
        )
    if len(rows) < REQUIRED_OBSERVATIONS:
        raise F05InputError(
            f"{member.company_id} requires at least {REQUIRED_OBSERVATIONS} observations"
        )
    by_date: dict[date, PriceRow] = {}
    for row in rows:
        if not isinstance(row, PriceRow):
            raise F05InputError(f"{member.company_id} contains a non-PriceRow value")
        if not isinstance(row.date, date):
            raise F05InputError(f"{member.company_id} contains an invalid Date field")
        if row.code != member.krx_code:
            raise F05InputError(
                f"wrong issuer/security row for {member.company_id}: {row.code!r}"
            )
        if row.date > cutoff_date:
            raise F05InputError(
                f"post-cutoff market row for {member.company_id}: {row.date.isoformat()}"
            )
        if row.date in by_date:
            raise F05InputError(
                f"duplicate market date for {member.company_id}: {row.date.isoformat()}"
            )
        by_date[row.date] = row

    ordered = tuple(by_date[d] for d in sorted(by_date))
    if ordered[-1].date != cutoff_date:
        raise F05InputError(
            f"cutoff endpoint missing for {member.company_id}: expected {cutoff_date.isoformat()}"
        )
    selected = ordered[-REQUIRED_OBSERVATIONS:]
    if len(selected[-(RETURN_20_INTERVALS + 1):]) != RETURN_20_INTERVALS + 1:
        raise F05InputError("20-session endpoint alignment failed")

    for row in selected:
        prefix = f"{member.company_id}/{row.date.isoformat()}"
        _require_decimal(row.open, f"{prefix}/Open", positive=True)
        _require_decimal(row.high, f"{prefix}/High", positive=True)
        _require_decimal(row.low, f"{prefix}/Low", positive=True)
        _require_decimal(row.close, f"{prefix}/Close", positive=True)
        volume = _require_integral_positive(row.volume, f"{prefix}/Volume")
        stocks = _require_integral_positive(row.stocks, f"{prefix}/Stocks")
        ratio = _require_decimal(row.changes_ratio, f"{prefix}/ChangesRatio")
        if ratio <= Decimal("-100"):
            raise F05InputError(f"{prefix}/ChangesRatio implies a nonpositive return factor")
        amount = _require_integral_positive(row.amount, f"{prefix}/Amount")
        changes = _require_decimal(row.changes, f"{prefix}/Changes")
        reference_base = _require_decimal(row.close, f"{prefix}/Close") - changes
        if reference_base <= 0:
            raise F05InputError(f"{prefix}/Changes implies a nonpositive KRX reference base")
        reconstructed_ratio = changes / reference_base * RETURN_SOURCE_SCALE
        if abs(reconstructed_ratio - ratio) > Decimal("0.011"):
            raise F05InputError(f"{prefix}/ChangesRatio is inconsistent with Close and Changes")
        if row.adjustment_factor is not None:
            raise F05InputError(
                f"invented/precomputed adjustment factor is forbidden for F05-R1: {prefix}"
            )
        # The conversions above are intentionally evaluated even where the
        # values are not used directly below; they are admission checks.
        if volume <= 0 or stocks <= 0 or amount <= 0:  # pragma: no cover - guarded above
            raise F05InputError(f"nonpositive turnover input: {prefix}")
    dates = tuple(row.date for row in selected)
    if dates != W1_SESSION_DATES or _session_digest(dates) != EXPECTED_W1_SESSION_GRID_SHA256:
        raise F05InputError("market rows do not match the governed W1 61-session grid")
    by_selected_date = {row.date: row for row in selected}
    for (code, event_date), expected in EXPECTED_CA_MARKET_ROWS.items():
        if member.krx_code != code:
            continue
        event_row = by_selected_date[event_date]
        for field, expected_value in expected.items():
            observed = _require_decimal(getattr(event_row, field), f"{member.company_id}/{event_date}/{field}")
            if observed != expected_value:
                raise F05InputError(
                    f"official CA market-row binding mismatch: {member.company_id}/{event_date}/{field}"
                )
    return selected


def _compound_changes_ratio(rows: Sequence[PriceRow], intervals: int) -> Decimal:
    if len(rows) < intervals + 1:
        raise F05InputError(f"{intervals} return intervals require {intervals + 1} observations")
    product = Decimal(1)
    # The first row establishes the start endpoint.  Each following row's KRX
    # ChangesRatio is the CA-reference-aware daily market-price change applied.
    for row in rows[-(intervals + 1):][1:]:
        ratio = _require_decimal(row.changes_ratio, "ChangesRatio")
        factor = Decimal(1) + ratio / RETURN_SOURCE_SCALE
        if factor <= 0:
            raise F05InputError("ChangesRatio implies a nonpositive daily return factor")
        product *= factor
    return product - Decimal(1)


def compute_company_metrics(
    member: F05CohortMember | Mapping[str, Any],
    rows: Sequence[PriceRow],
    cutoff_date: date = W1_CUTOFF_DATE,
    *,
    return_semantics: str = RETURN_SEMANTICS,
) -> F05MarketMetrics:
    """Compute one company's admitted W1 market metrics without a benchmark."""
    with localcontext() as context:
        context.prec = DECIMAL_PRECISION
        context.rounding = ROUND_HALF_EVEN
        return _compute_company_metrics(member, rows, cutoff_date, return_semantics)


def _compute_company_metrics(
    member: F05CohortMember | Mapping[str, Any],
    rows: Sequence[PriceRow],
    cutoff_date: date,
    return_semantics: str,
) -> F05MarketMetrics:
    normalized = _normalize_member(member)
    if return_semantics != RETURN_SEMANTICS:
        raise F05InputError(
            "return semantics must be KRX ChangesRatio price change with no dividend or factor substitution"
        )
    selected = _validate_company_rows(normalized, rows, cutoff_date)
    turnover = [
        _require_integral_positive(row.volume, "Volume")
        / _require_integral_positive(row.stocks, "Stocks")
        for row in selected[-40:]
    ]
    prior_mean = sum(turnover[:20], Decimal(0)) / Decimal(20)
    recent_mean = sum(turnover[20:], Decimal(0)) / Decimal(20)
    if prior_mean <= 0:
        raise F05InputError("prior 20-session mean turnover must be positive")
    return F05MarketMetrics(
        company_id=normalized.company_id,
        krx_code=normalized.krx_code,
        trailing_20d_total_return=_compound_changes_ratio(selected, RETURN_20_INTERVALS),
        trailing_60d_total_return=_compound_changes_ratio(selected, RETURN_60_INTERVALS),
        turnover_acceleration=recent_mean / prior_mean - Decimal(1),
        observation_dates=tuple(row.date for row in selected),
        return_20_source_slice_sha256=_source_slice_digest(selected[-21:], CONSUMED_SOURCE_FIELDS),
        return_60_source_slice_sha256=_source_slice_digest(selected, CONSUMED_SOURCE_FIELDS),
        turnover_source_slice_sha256=_source_slice_digest(
            selected[-40:], ("Date", "Code", "Volume", "Stocks")
        ),
    )


def build_w1_f05_inputs(
    cohort: Sequence[F05CohortMember | Mapping[str, Any]],
    rows_by_code: Mapping[str, Sequence[PriceRow]],
    cutoff_date: date = W1_CUTOFF_DATE,
    *,
    source_binding: F05SourceBinding,
    ca_evidence_manifest: Mapping[str, Any],
    ca_source_custody: Mapping[str, Any],
    ca_custody_root: Path,
    return_semantics: str = RETURN_SEMANTICS,
    source_lineage_refs: Sequence[str] = (),
    source_lineage_refs_by_company: Mapping[str, Sequence[str]] | None = None,
) -> list[dict[str, Any]]:
    """Build exact-57 F05 raw inputs and identical equal-weight benchmarks.

    The function is intentionally all-or-nothing: no benchmark or partial input
    is returned unless all 57 bound companies have admissible data on the same
    61-session grid ending at the exact cutoff.
    """
    if len(cohort) != EXPECTED_W1_DENOMINATOR:
        raise F05InputError(
            f"W1 benchmark denominator must be exactly {EXPECTED_W1_DENOMINATOR}, got {len(cohort)}"
        )
    members = tuple(_normalize_member(item) for item in cohort)
    company_ids = [member.company_id for member in members]
    codes = [member.krx_code for member in members]
    if len(set(company_ids)) != EXPECTED_W1_DENOMINATOR or len(set(codes)) != EXPECTED_W1_DENOMINATOR:
        raise F05InputError("W1 cohort company IDs and KRX codes must each be unique")
    membership = "\n".join(
        f"{member.company_id}|{member.krx_code}"
        for member in sorted(members, key=lambda value: (value.company_id, value.krx_code))
    ).encode("utf-8")
    cohort_sha256 = hashlib.sha256(membership).hexdigest()
    if cohort_sha256 != EXPECTED_W1_COHORT_IDENTITY_SHA256:
        raise F05InputError("W1 cohort identity does not match the frozen R0 57-member binding")
    _validate_source_binding(source_binding)
    ca_validation = validate_required_ca_evidence(
        ca_evidence_manifest, ca_source_custody, ca_custody_root
    )
    if set(rows_by_code) != set(codes):
        missing = sorted(set(codes) - set(rows_by_code))
        extra = sorted(set(rows_by_code) - set(codes))
        raise F05InputError(f"price map does not exactly match W1 cohort; missing={missing}, extra={extra}")
    if not source_lineage_refs or not all(
        isinstance(ref, str) and ref.strip() for ref in source_lineage_refs
    ):
        raise F05InputError("source_lineage_refs must contain at least one nonempty string")
    company_refs = source_lineage_refs_by_company or {}
    if source_lineage_refs_by_company is not None and set(company_refs) != set(company_ids):
        raise F05InputError("per-company source lineage keys must exactly match the W1 cohort")
    for company_id, refs_for_company in company_refs.items():
        if not refs_for_company or not all(
            isinstance(ref, str) and ref.strip() for ref in refs_for_company
        ):
            raise F05InputError(f"invalid per-company source lineage: {company_id}")

    metrics = [
        compute_company_metrics(
            member,
            rows_by_code[member.krx_code],
            cutoff_date,
            return_semantics=return_semantics,
        )
        for member in members
    ]
    # Decimal addition rounds at the fixed precision, so bind the reduction
    # order as well as the output order.  Cohort-file presentation order must
    # never change benchmark bytes.
    metrics.sort(key=lambda item: item.company_id)
    expected_grid = metrics[0].observation_dates
    for metric in metrics[1:]:
        if metric.observation_dates != expected_grid:
            raise F05InputError(
                f"misaligned 61-session endpoints for {metric.company_id}; exact common grid required"
            )

    denominator = Decimal(EXPECTED_W1_DENOMINATOR)
    with localcontext() as context:
        context.prec = DECIMAL_PRECISION
        context.rounding = ROUND_HALF_EVEN
        benchmark_20 = sum(
            (item.trailing_20d_total_return for item in metrics), Decimal(0)
        ) / denominator
        benchmark_60 = sum(
            (item.trailing_60d_total_return for item in metrics), Decimal(0)
        ) / denominator
    refs = sorted(set(source_lineage_refs))

    output: list[dict[str, Any]] = []
    for item in metrics:
        market_return_20 = _decimal_text(item.trailing_20d_total_return)
        market_return_60 = _decimal_text(item.trailing_60d_total_return)
        market_benchmark_20 = _decimal_text(benchmark_20)
        market_benchmark_60 = _decimal_text(benchmark_60)
        window_locator = (
            f"parquet-sha256:{source_binding.parquet_sha256.lower()}#Code={item.krx_code};"
            f"Date={item.observation_dates[0].isoformat()}..{item.observation_dates[-1].isoformat()};"
            f"Fields={','.join(CONSUMED_SOURCE_FIELDS)}"
        )
        item_refs = sorted(set((
            *refs,
            *ca_validation.global_source_refs,
            *tuple(company_refs.get(item.company_id, ())),
            *tuple(ca_validation.source_refs_by_company.get(item.company_id, ())),
            window_locator,
        )))
        feature_raw_input = {
            "availability_state": "AVAILABLE",
            # Canonical audit names state the authorized economic meaning.
            "trailing_20d_market_price_return": market_return_20,
            "universe_20d_equal_weight_market_price_return": market_benchmark_20,
            "trailing_60d_market_price_return": market_return_60,
            "universe_60d_equal_weight_market_price_return": market_benchmark_60,
            # The unchanged scorer consumes these historical key names.  They
            # are exact aliases and do not introduce cash-dividend total return.
            "trailing_20d_total_return": market_return_20,
            "universe_20d_equal_weight_return": market_benchmark_20,
            "trailing_60d_total_return": market_return_60,
            "universe_60d_equal_weight_return": market_benchmark_60,
            "turnover_acceleration": _decimal_text(item.turnover_acceleration),
            "event_group_ids": list(
                ca_validation.event_group_ids_by_company.get(item.company_id, ())
            ),
            "source_lineage_refs": item_refs,
            "calculation_trace": {
                "return_semantics": RETURN_SEMANTICS,
                "return_source_field": RETURN_SOURCE_FIELD,
                "return_source_unit": RETURN_SOURCE_UNIT,
                "return_source_scale_divisor": _decimal_text(RETURN_SOURCE_SCALE),
                "turnover_semantics": TURNOVER_SEMANTICS,
                "return_20_observation_count": RETURN_20_INTERVALS + 1,
                "return_20_interval_count": RETURN_20_INTERVALS,
                "return_20_start_date": item.observation_dates[-21].isoformat(),
                "return_20_end_date": item.observation_dates[-1].isoformat(),
                "return_60_observation_count": RETURN_60_INTERVALS + 1,
                "return_60_interval_count": RETURN_60_INTERVALS,
                "return_60_start_date": item.observation_dates[0].isoformat(),
                "return_60_end_date": item.observation_dates[-1].isoformat(),
                "turnover_prior_20_start_date": item.observation_dates[-40].isoformat(),
                "turnover_prior_20_end_date": item.observation_dates[-21].isoformat(),
                "turnover_recent_20_start_date": item.observation_dates[-20].isoformat(),
                "turnover_recent_20_end_date": item.observation_dates[-1].isoformat(),
                "benchmark_member_count": EXPECTED_W1_DENOMINATOR,
                "benchmark_method": "SIMPLE_EQUAL_WEIGHT_MEAN_NO_SHRINK",
                "source_dataset_id": source_binding.dataset_id,
                "source_parquet_sha256": source_binding.parquet_sha256.lower(),
                "source_semantics": source_binding.source_semantics,
                "ca_manifest_semantic_sha256": ca_validation.semantic_sha256,
                "ca_custody_semantic_sha256": ca_validation.custody_semantic_sha256,
                "consumed_source_fields": list(CONSUMED_SOURCE_FIELDS),
                "identity_source_field": IDENTITY_SOURCE_FIELD,
                "display_name_consumed": DISPLAY_NAME_CONSUMED,
                "session_grid_sha256": EXPECTED_W1_SESSION_GRID_SHA256,
                "return_20_source_slice_sha256": item.return_20_source_slice_sha256,
                "return_60_source_slice_sha256": item.return_60_source_slice_sha256,
                "turnover_source_slice_sha256": item.turnover_source_slice_sha256,
                "legacy_scorer_key_alias": {
                    "trailing_20d_total_return": "trailing_20d_market_price_return",
                    "universe_20d_equal_weight_return": "universe_20d_equal_weight_market_price_return",
                    "trailing_60d_total_return": "trailing_60d_market_price_return",
                    "universe_60d_equal_weight_return": "universe_60d_equal_weight_market_price_return",
                },
                "cash_dividend_included": False,
                "adjustment_factor_used": False,
            },
        }
        output.append({
            "company_id": item.company_id,
            "krx_code": item.krx_code,
            "feature_id": F05_FEATURE_ID,
            "cutoff_date": cutoff_date.isoformat(),
            "cohort_identity_sha256": cohort_sha256,
            "benchmark_member_count": EXPECTED_W1_DENOMINATOR,
            "feature_raw_input": feature_raw_input,
        })
    output.sort(key=lambda row: row["company_id"])
    return output
