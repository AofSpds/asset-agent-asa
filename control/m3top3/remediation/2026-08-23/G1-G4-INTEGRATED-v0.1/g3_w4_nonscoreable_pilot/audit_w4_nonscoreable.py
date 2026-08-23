#!/usr/bin/env python3
"""Read-only W4 x 3 mechanical price-observation audit.

The script validates exact input hashes, reads only raw identity/date/OHLC fields,
emits JSON to stdout, and intentionally computes no return, score, rank, Top-K,
winner, MFE, MAE, or model-performance field.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import sys
from collections import defaultdict
from pathlib import Path


TARGETS = {
    "281820": {"company": "케이씨텍", "eligibility": "ELIGIBLE", "case": "NORMAL_ELIGIBLE_PRICE_PATH"},
    "025560": {"company": "미래산업", "eligibility": "ELIGIBLE", "case": "CA_ZERO_OHL_STRESS_PATH"},
    "482630": {"company": "삼양엔씨켐", "eligibility": "UNRESOLVED", "case": "DENOMINATOR_NEGATIVE_CONTROL"},
}
WINDOW = {
    "window": "W4",
    "cutoff": "2025-05-09",
    "entry": "2025-05-12",
    "last_trading_day": "2025-08-08",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require_hash(path: Path, expected: str) -> str:
    observed = sha256(path)
    if observed.lower() != expected.lower():
        raise SystemExit(f"HASH_MISMATCH: {path}: expected={expected} observed={observed}")
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
    parser.add_argument("--membership", required=True, type=Path)
    parser.add_argument("--schema", required=True, type=Path)
    parser.add_argument("--expected-parquet-sha256", required=True)
    parser.add_argument("--expected-membership-sha256", required=True)
    parser.add_argument("--expected-schema-sha256", required=True)
    args = parser.parse_args()

    try:
        import numpy
        import pyarrow
        import pyarrow.compute as pc
        import pyarrow.parquet as pq
    except ImportError as exc:
        raise SystemExit("DEPENDENCY_MISSING: isolated numpy/pyarrow required") from exc

    parquet_hash = require_hash(args.parquet, args.expected_parquet_sha256)
    membership_hash = require_hash(args.membership, args.expected_membership_sha256)
    schema_hash = require_hash(args.schema, args.expected_schema_sha256)

    with args.membership.open("r", encoding="utf-8-sig", newline="") as stream:
        membership_rows = list(csv.DictReader(stream))
    membership_by_code = {row["KRX_code"].strip(): row for row in membership_rows}
    missing_membership = sorted(set(TARGETS) - set(membership_by_code))
    if missing_membership:
        raise SystemExit(f"IDENTITY_BINDING_MISSING: {missing_membership}")

    with args.schema.open("r", encoding="utf-8-sig", newline="") as stream:
        canonical_fields = next(csv.reader(stream))

    parquet_file = pq.ParquetFile(args.parquet)
    raw_fields = parquet_file.schema_arrow.names
    required = ["Date", "Code", "Open", "High", "Low"]
    absent_required = [field for field in required if field not in raw_fields]
    if absent_required:
        raise SystemExit(f"REQUIRED_RAW_FIELD_MISSING: {absent_required}")

    table = pq.read_table(args.parquet, columns=required)
    code_mask = pc.is_in(table["Code"], value_set=pyarrow.array(sorted(TARGETS)))
    table = table.filter(code_mask)
    rows = table.to_pylist()

    per_code: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        date = date_text(row["Date"])
        code = str(row["Code"])
        if WINDOW["cutoff"] <= date <= WINDOW["last_trading_day"]:
            row = dict(row)
            row["Date"] = date
            per_code[code].append(row)

    observations = []
    for code, target in TARGETS.items():
        selected = sorted(per_code.get(code, []), key=lambda row: str(row["Date"]))
        dates = [str(row["Date"]) for row in selected]
        zero_dates = [
            str(row["Date"])
            for row in selected
            if row["Open"] == 0 and row["High"] == 0 and row["Low"] == 0
        ]
        duplicate_count = len(dates) - len(set(dates))
        observations.append(
            {
                "company": target["company"],
                "code": code,
                "company_id": membership_by_code[code]["company_id"],
                "identity_binding_status": membership_by_code[code]["company_id_binding_status"],
                "case": target["case"],
                "eligibility_state": target["eligibility"],
                "period_row_count": len(selected),
                "period_first_date": dates[0] if dates else None,
                "period_last_date": dates[-1] if dates else None,
                "boundary_presence": {
                    "cutoff": WINDOW["cutoff"] in dates,
                    "entry": WINDOW["entry"] in dates,
                    "last_trading_day": WINDOW["last_trading_day"] in dates,
                },
                "duplicate_date_rows": duplicate_count,
                "zero_open_high_low_count": len(zero_dates),
                "zero_open_high_low_dates": zero_dates,
                "governed_ca_fields_present_in_raw": False,
                "ca_observation_state": "NOT_ADMISSIBLE_FROM_RAW_SCHEMA",
                "source_bundle_state": "NOT_FOUND_PER_G3_AUDIT",
                "publication_at_state": "NULL_PER_G3_AUDIT",
                "annotation_lineage_state": "NOT_FOUND_PER_G3_AUDIT",
                "score_admission": False,
                "rank_admission": False,
                "outcome_admission": False,
                "terminal_state": "FAIL_CLOSED_PENDING_SOURCE_BUNDLE_PUBLICATION_AND_ELIGIBILITY_CONTROLS",
            }
        )

    result = {
        "audit_id": "M3TOP3-W4-X3-NONSCOREABLE-MECHANICAL-OBSERVATION-20260823-01",
        "mode": "READ_ONLY_STDOUT_ONLY",
        "iva_execution_participation": "NONE",
        "toolchain": {
            "python": platform.python_version(),
            "numpy": numpy.__version__,
            "pyarrow": pyarrow.__version__,
        },
        "window": WINDOW,
        "inputs": {
            "parquet": {"path": str(args.parquet), "sha256": parquet_hash, "bytes": args.parquet.stat().st_size},
            "membership": {"path": str(args.membership), "sha256": membership_hash, "rows": len(membership_rows)},
            "schema": {"path": str(args.schema), "sha256": schema_hash, "columns": len(canonical_fields)},
        },
        "raw_schema": {
            "columns": len(raw_fields),
            "governed_ca_fields_present": all(
                field in raw_fields
                for field in ["Corporate_Action_Flag", "Adjustment_Factor", "Corporate_Action_Type", "Action_Source"]
            ),
        },
        "observations": observations,
        "claim_boundary": {
            "score": "PROHIBITED",
            "rank": "PROHIBITED",
            "top_k": "PROHIBITED",
            "return": "PROHIBITED",
            "outcome_performance": "PROHIBITED",
            "official_golden": "PROHIBITED",
            "official_replay": "PROHIBITED",
            "price_canonical": "NOT_ESTABLISHED",
        },
        "overall_state": "MECHANICAL_OBSERVATION_COMPLETE_ASSEMBLY_ADMISSION_FAIL_CLOSED",
    }
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
