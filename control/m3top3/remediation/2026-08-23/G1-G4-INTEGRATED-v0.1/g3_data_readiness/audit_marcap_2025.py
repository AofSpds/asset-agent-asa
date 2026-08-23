#!/usr/bin/env python3
"""Read-only, deterministic coverage audit for the supplied 2025 marcap bytes.

The program does not write files.  It emits one JSON object to stdout and exits
non-zero if an explicitly supplied input hash does not match.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import sys
from collections import Counter, defaultdict
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require_hash(path: Path, expected: str | None) -> str:
    observed = sha256(path)
    if expected and observed.lower() != expected.lower():
        raise SystemExit(
            f"HASH_MISMATCH: {path}: expected={expected.lower()} observed={observed}"
        )
    return observed


def date_text(value: object) -> str:
    if hasattr(value, "date"):
        value = value.date()  # type: ignore[union-attr]
    if hasattr(value, "isoformat"):
        return value.isoformat()  # type: ignore[union-attr]
    return str(value)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--parquet", required=True, type=Path)
    parser.add_argument("--u127-csv", required=True, type=Path)
    parser.add_argument("--schema-csv", required=True, type=Path)
    parser.add_argument("--expected-parquet-sha256")
    parser.add_argument("--expected-u127-sha256")
    parser.add_argument("--expected-schema-sha256")
    args = parser.parse_args()

    try:
        import numpy
        import pyarrow
        import pyarrow.parquet as pq
    except ImportError as exc:
        raise SystemExit(
            "DEPENDENCY_MISSING: install pyarrow==17.0.0 into an isolated "
            "temporary directory and expose it through PYTHONPATH"
        ) from exc

    parquet_hash = require_hash(args.parquet, args.expected_parquet_sha256)
    u127_hash = require_hash(args.u127_csv, args.expected_u127_sha256)
    schema_hash = require_hash(args.schema_csv, args.expected_schema_sha256)

    with args.u127_csv.open("r", encoding="utf-8-sig", newline="") as stream:
        membership = list(csv.DictReader(stream))
    u127_names = {row["KRX_code"].strip(): row["canonical_name"] for row in membership}
    u127_codes = set(u127_names)

    with args.schema_csv.open("r", encoding="utf-8-sig", newline="") as stream:
        canonical_fields = next(csv.reader(stream))

    parquet_file = pq.ParquetFile(args.parquet)
    raw_fields = parquet_file.schema_arrow.names
    table = pq.read_table(args.parquet, columns=["Date", "Code", "Open", "High", "Low"])
    columns = table.to_pydict()

    dates: set[str] = set()
    codes: set[str] = set()
    pairs: set[tuple[str, str]] = set()
    u127_dates: dict[str, set[str]] = defaultdict(set)
    zero_ohl_by_code: Counter[str] = Counter()
    zero_ohl_total = 0

    for raw_date, raw_code, open_, high, low in zip(
        columns["Date"],
        columns["Code"],
        columns["Open"],
        columns["High"],
        columns["Low"],
        strict=True,
    ):
        date = date_text(raw_date)
        code = str(raw_code)
        dates.add(date)
        codes.add(code)
        pairs.add((date, code))
        if code in u127_codes:
            u127_dates[code].add(date)
        if open_ == 0 and high == 0 and low == 0:
            zero_ohl_total += 1
            if code in u127_codes:
                zero_ohl_by_code[code] += 1

    present_u127 = u127_codes & codes
    full_u127 = sorted(code for code in present_u127 if len(u127_dates[code]) == len(dates))
    partial_u127 = {
        code: len(u127_dates[code])
        for code in sorted(present_u127)
        if 0 < len(u127_dates[code]) < len(dates)
    }
    u127_zero = {
        code: {"name": u127_names[code], "rows": zero_ohl_by_code[code]}
        for code in sorted(zero_ohl_by_code)
    }

    result = {
        "audit_mode": "READ_ONLY_STDOUT_ONLY",
        "toolchain": {
            "python": platform.python_version(),
            "numpy": numpy.__version__,
            "pyarrow": pyarrow.__version__,
        },
        "inputs": {
            "parquet": {
                "path": str(args.parquet),
                "bytes": args.parquet.stat().st_size,
                "sha256": parquet_hash,
            },
            "u127_csv": {
                "path": str(args.u127_csv),
                "bytes": args.u127_csv.stat().st_size,
                "sha256": u127_hash,
                "rows": len(membership),
            },
            "canonical_schema_csv": {
                "path": str(args.schema_csv),
                "bytes": args.schema_csv.stat().st_size,
                "sha256": schema_hash,
                "columns": len(canonical_fields),
            },
        },
        "parquet": {
            "rows": parquet_file.metadata.num_rows,
            "row_groups": parquet_file.metadata.num_row_groups,
            "columns": parquet_file.metadata.num_columns,
            "raw_fields": raw_fields,
            "distinct_codes": len(codes),
            "distinct_dates": len(dates),
            "date_min": min(dates),
            "date_max": max(dates),
            "duplicate_date_code_rows": parquet_file.metadata.num_rows - len(pairs),
        },
        "u127_coverage": {
            "membership_codes": len(u127_codes),
            "present_any_date": len(present_u127),
            "absent_codes": sorted(u127_codes - codes),
            "full_date_codes": len(full_u127),
            "partial_date_codes": partial_u127,
        },
        "zero_open_high_low": {
            "all_market_rows": zero_ohl_total,
            "u127_rows": sum(zero_ohl_by_code.values()),
            "u127_by_code": u127_zero,
        },
        "canonical_schema_comparison": {
            "canonical_columns": len(canonical_fields),
            "raw_columns": len(raw_fields),
            "intersection_columns": len(set(canonical_fields) & set(raw_fields)),
            "canonical_fields_missing_from_raw": [
                field for field in canonical_fields if field not in raw_fields
            ],
            "extra_raw_fields": [field for field in raw_fields if field not in canonical_fields],
        },
    }
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
