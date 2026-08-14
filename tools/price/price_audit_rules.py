#!/usr/bin/env python3
"""Deterministic rule primitives for PRICE-CANONICAL dry-run auditing."""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
import math
import re
from typing import Mapping, Sequence

import numpy as np

OHLC_CLASS_NORMAL = "OHLC_CLASS_NORMAL"
OHLC_CLASS_ZERO_OHL_NO_TRADE_METRICS = "OHLC_CLASS_ZERO_OHL_NO_TRADE_METRICS"
OHLC_CLASS_ZERO_OHL_WITH_TRADE_METRICS = "OHLC_CLASS_ZERO_OHL_WITH_TRADE_METRICS"
OHLC_CLASS_OTHER_INCONSISTENCY = "OHLC_CLASS_OTHER_INCONSISTENCY"

PRICE_REASON_CODES = {
    "PRICE-Q001": "MISSING_REQUIRED_DATE",
    "PRICE-Q002": "MISSING_REQUIRED_CODE",
    "PRICE-Q003": "DUPLICATE_DATE_CODE",
    "PRICE-Q004": "MISSING_REQUIRED_OHLC",
    "PRICE-Q005": "OHLC_OTHER_INCONSISTENCY",
    "PRICE-Q006": "ZERO_OHL_WITH_TRADE_METRICS_REQUIRES_ADJUDICATION",
    "PRICE-Q007": "NUMERIC_NONFINITE",
    "PRICE-Q008": "VOLUME_NONINTEGRAL",
    "PRICE-Q009": "CODE_LEXICAL_CORRUPTION",
    "PRICE-Q010": "COMPANY_ID_FOREIGN_KEY_FAILURE",
    "PRICE-Q011": "RAW_LINEAGE_UNRESOLVED",
    "PRICE-Q012": "CA_EVIDENCE_REQUIRED",
    "PRICE-Q013": "CA_EVIDENCE_UNRESOLVED",
    "PRICE-Q014": "UNSUPPORTED_NUMERIC_ROUNDING_REQUIRED",
}

CODE_RE = re.compile(r"^[0-9A-Z]{6}$")


@dataclass(frozen=True)
class NumericAudit:
    null_count: int
    nonfinite_count: int
    fractional_count: int
    exact_decimal_roundtrip_failures: int


def _null_mask(values: np.ndarray) -> np.ndarray:
    if values.dtype.kind == "f":
        return np.isnan(values)
    if values.dtype.kind in "iu":
        return np.zeros(values.shape, dtype=bool)
    return np.fromiter((x is None for x in values), dtype=bool, count=len(values))


def numeric_audit(values: np.ndarray) -> NumericAudit:
    """Audit source numerics without inventing a canonical precision/scale."""
    values = np.asarray(values)
    nulls = _null_mask(values)

    if values.dtype.kind in "iu":
        return NumericAudit(int(nulls.sum()), 0, 0, 0)

    if values.dtype.kind != "f":
        non_null = [x for x in values.tolist() if x is not None]
        nonfinite = 0
        fractional = 0
        failures = 0
        for value in non_null:
            try:
                f = float(value)
            except (TypeError, ValueError):
                nonfinite += 1
                continue
            if not math.isfinite(f):
                nonfinite += 1
                continue
            if f != math.trunc(f):
                fractional += 1
            text = str(int(f)) if f == math.trunc(f) else np.format_float_positional(f, unique=True, trim="-")
            try:
                if float(Decimal(text)) != f:
                    failures += 1
            except (InvalidOperation, ValueError, OverflowError):
                failures += 1
        return NumericAudit(int(nulls.sum()), nonfinite, fractional, failures)

    finite = np.isfinite(values) & ~nulls
    nonfinite_count = int((~np.isfinite(values) & ~nulls).sum())
    finite_values = values[finite]
    integral = finite_values == np.trunc(finite_values)
    fractional_count = int((~integral).sum())

    failures = 0
    if integral.any():
        integral_values = finite_values[integral]
        i64 = np.iinfo(np.int64)
        in_range = (integral_values >= i64.min) & (integral_values <= i64.max)
        failures += int((~in_range).sum())
        if in_range.any():
            iv = integral_values[in_range].astype(np.int64)
            failures += int((iv.astype(np.float64) != integral_values[in_range]).sum())

    if fractional_count:
        for f in np.unique(finite_values[~integral]).tolist():
            text = np.format_float_positional(float(f), unique=True, trim="-")
            try:
                if float(Decimal(text)) != float(f):
                    failures += 1
            except (InvalidOperation, ValueError, OverflowError):
                failures += 1

    return NumericAudit(int(nulls.sum()), nonfinite_count, fractional_count, failures)


def code_lexical_failures(codes: np.ndarray) -> tuple[int, int]:
    codes = np.asarray(codes, dtype=object)
    nulls = int(sum(x is None for x in codes.tolist()))
    failures = 0
    for value in codes.tolist():
        if value is None:
            continue
        if not isinstance(value, str) or CODE_RE.fullmatch(value) is None:
            failures += 1
    return nulls, failures


def classify_ohlc(open_: np.ndarray, high: np.ndarray, low: np.ndarray, close: np.ndarray,
                  volume: np.ndarray, amount: np.ndarray) -> np.ndarray:
    """Return one deterministic technical class per row, without semantic inference."""
    open_ = np.asarray(open_, dtype=np.float64)
    high = np.asarray(high, dtype=np.float64)
    low = np.asarray(low, dtype=np.float64)
    close = np.asarray(close, dtype=np.float64)
    volume = np.asarray(volume, dtype=np.float64)
    amount = np.asarray(amount, dtype=np.float64)

    out = np.full(len(close), OHLC_CLASS_OTHER_INCONSISTENCY, dtype=object)
    zero_ohl = (open_ == 0) & (high == 0) & (low == 0) & (close > 0)
    zero_trade = zero_ohl & (volume == 0) & (amount == 0)
    with_trade = zero_ohl & ((volume > 0) | (amount > 0))
    normal = ((high >= open_) & (high >= low) & (high >= close)
              & (low <= open_) & (low <= high) & (low <= close))
    out[normal] = OHLC_CLASS_NORMAL
    out[zero_trade] = OHLC_CLASS_ZERO_OHL_NO_TRADE_METRICS
    out[with_trade] = OHLC_CLASS_ZERO_OHL_WITH_TRADE_METRICS
    return out


def required_ohlc_null_rows(columns: Mapping[str, np.ndarray]) -> int:
    masks = [_null_mask(np.asarray(columns[name])) for name in ("Open", "High", "Low", "Close")]
    combined = masks[0].copy()
    for mask in masks[1:]:
        combined |= mask
    return int(combined.sum())


def duplicate_date_code_rows(date_days: np.ndarray, codes: np.ndarray) -> int:
    date_days = np.asarray(date_days, dtype=np.int64)
    codes = np.asarray(codes, dtype=object)
    keys = np.char.add(np.char.add(date_days.astype(str), "|"), codes.astype(str))
    _, counts = np.unique(keys, return_counts=True)
    return int(counts[counts > 1].sum())


def canonical_row_accounting(source: int, passed: int, pending: int, quarantine: int) -> bool:
    return int(source) == int(passed) + int(pending) + int(quarantine)


def validate_company_map(records: Sequence[Mapping[str, object]]) -> list[str]:
    errors: list[str] = []
    seen: dict[str, str] = {}
    for idx, record in enumerate(records):
        code = record.get("code")
        company_id = record.get("company_id")
        if not isinstance(code, str) or CODE_RE.fullmatch(code) is None:
            errors.append(f"row {idx}: invalid code")
            continue
        if not isinstance(company_id, str) or not company_id.strip():
            errors.append(f"row {idx}: missing company_id")
            continue
        if code in seen and seen[code] != company_id:
            errors.append(f"row {idx}: conflicting company_id for {code}")
        else:
            seen[code] = company_id
    return errors


def map_company_ids(codes: np.ndarray, mapping: Mapping[str, str]) -> np.ndarray:
    """Map only explicit code bindings; unresolved values remain NULL/None."""
    arr = np.asarray(codes, dtype=object)
    return np.fromiter((mapping.get(code) for code in arr.tolist()), dtype=object, count=len(arr))
