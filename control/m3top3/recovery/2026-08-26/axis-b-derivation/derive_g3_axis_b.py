#!/usr/bin/env python3
"""Deterministic G3 Axis-B Open/previous-Close signal derivation.

Scope is intentionally narrow:
* exact pinned FinanceData/marcap 2024/2025/2026 Parquet bytes;
* every row, stitched across year seams by exact Code;
* current Open versus immediately previous observed same-Code Close;
* inclusive absolute gap >= 20%, implemented as integer arithmetic;
* signal only: no corporate-action, factor, adjustment, eligibility, status,
  calendar, annotation, score, or ranking inference.

Requires Python 3.12 and pyarrow==17.0.0.  Source price values must be finite
integral doubles; the program fails closed rather than round a value.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import gzip
import hashlib
import json
import os
import platform
import resource
import subprocess
import tempfile
import time
from collections import Counter
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.csv as pacsv
import pyarrow.parquet as pq


PINNED_COMMIT = "5e8e4e57f3fcb129a6ff20751f643f67d3592c82"
PYARROW_VERSION = "17.0.0"
THRESHOLD_NUMERATOR = 1
THRESHOLD_DENOMINATOR = 5
# Bounded pre-final rework, with no loop: one initial attempt failed on an
# unsupported Arrow duration-to-int cast (4.073222 s); the first completed
# materialization (35.227627 s) was superseded after the governed protocol
# precedence review found that 116 first-observation rows with Open<=0 must be
# price-domain quarantines under section 4.1 step 6.
PRECOMPUTE_REWORK_SECONDS = 79.268674
SOURCES: tuple[dict[str, Any], ...] = (
    {
        "year": 2024,
        "path": "data/marcap-2024.parquet",
        "git_blob": "b69c5222d015c81f19f90f581faabe4dd1a919b4",
        "bytes": 24_572_111,
        "sha256": "b0c38943e67637d5faf88429880092cf0f46a394be39860dd3bcd0b04231bccb",
        "rows": 687_708,
    },
    {
        "year": 2025,
        "path": "data/marcap-2025.parquet",
        "git_blob": "e817f0729b787fe03904982a37b1d84d26d70206",
        "bytes": 25_153_419,
        "sha256": "2bfd93c217eb74263bc5020b23fa6debb6b02531c11eaccc2826639bc191559e",
        "rows": 696_524,
    },
    {
        "year": 2026,
        "path": "data/marcap-2026.parquet",
        "git_blob": "3921c090c0c9336e2ab8d068a4546aec26595665",
        "bytes": 16_297_737,
        "sha256": "b6f3f8ea110326b21d23b5344e6abe159f8ea7f7a345262155b929c08886fc9d",
        "rows": 437_787,
    },
)

LEDGER_NAME = "G3_AXIS_B_FULL_ROW_DISPOSITION_LEDGER_v0.1.csv.gz"
SIGNALS_NAME = "G3_AXIS_B_MATERIAL_SIGNAL_ROWS_v0.1.csv.gz"
QUARANTINE_NAME = "G3_AXIS_B_QUARANTINE_ROWS_v0.1.csv.gz"
SUMMARY_NAME = "G3_AXIS_B_DERIVATION_SUMMARY_v0.1.json"
TELEMETRY_NAME = "G3_AXIS_B_RUN_TELEMETRY_v0.1.json"
REPORT_NAME = "G3_AXIS_B_DERIVATION_REPORT_2026-08-26.md"
MANIFEST_NAME = "G3_AXIS_B_SOURCE_AND_OUTPUT_MANIFEST_v0.1.json"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def json_write(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def utc_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def iso_kst(value: dt.datetime) -> str:
    return value.astimezone(dt.timezone(dt.timedelta(hours=9))).isoformat(timespec="seconds")


def git_value(repo: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(repo), *args], text=True, stderr=subprocess.STDOUT
    ).strip()


def verify_sources(source_root: Path) -> list[dict[str, Any]]:
    if pa.__version__ != PYARROW_VERSION:
        raise RuntimeError(
            f"pyarrow version mismatch: expected {PYARROW_VERSION}, observed {pa.__version__}"
        )
    observed_commit = git_value(source_root, "rev-parse", "HEAD")
    if observed_commit != PINNED_COMMIT:
        raise RuntimeError(f"source commit mismatch: {observed_commit}")

    evidence: list[dict[str, Any]] = []
    for spec in SOURCES:
        path = source_root / spec["path"]
        observed = {
            **spec,
            "observed_bytes": path.stat().st_size,
            "observed_sha256": sha256_file(path),
            "observed_git_blob": git_value(source_root, "rev-parse", f"HEAD:{spec['path']}"),
        }
        for key, observed_key in (
            ("bytes", "observed_bytes"),
            ("sha256", "observed_sha256"),
            ("git_blob", "observed_git_blob"),
        ):
            if observed[observed_key] != spec[key]:
                raise RuntimeError(
                    f"source {spec['year']} {key} mismatch: {observed[observed_key]}"
                )
        evidence.append(observed)
    return evidence


def all_true(mask: pa.Array | pa.ChunkedArray) -> bool:
    result = pc.all(pc.fill_null(mask, False)).as_py()
    return bool(result)


def bool_np(mask: pa.Array | pa.ChunkedArray):
    return pc.fill_null(mask, False).to_numpy(zero_copy_only=False)


def shifted(array: pa.Array, scalar: pa.Scalar) -> pa.Array:
    if len(array) == 0:
        return array
    return pa.concat_arrays([pa.array([scalar.as_py()], type=array.type), array.slice(0, len(array) - 1)])


def null_shifted(array: pa.Array) -> pa.Array:
    if len(array) == 0:
        return array
    return pa.concat_arrays([pa.nulls(1, type=array.type), array.slice(0, len(array) - 1)])


def deterministic_gzip(raw_path: Path, gzip_path: Path) -> None:
    with raw_path.open("rb") as src, gzip_path.open("wb") as dst_raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=dst_raw, mtime=0, compresslevel=9) as dst:
            for block in iter(lambda: src.read(8 * 1024 * 1024), b""):
                dst.write(block)


def write_csv_gz(table: pa.Table, path: Path) -> None:
    options = pacsv.WriteOptions(include_header=True, batch_size=65_536, delimiter=",")
    with tempfile.NamedTemporaryFile(
        prefix=path.name + ".", suffix=".raw", dir=path.parent, delete=False
    ) as tmp:
        raw_path = Path(tmp.name)
    try:
        pacsv.write_csv(table, raw_path, write_options=options)
        deterministic_gzip(raw_path, path)
    finally:
        raw_path.unlink(missing_ok=True)


def scalar_string_mask(mask: pa.Array, yes: str, no: str | pa.Array) -> pa.Array:
    return pc.if_else(mask, pa.scalar(yes), no if isinstance(no, pa.Array) else pa.scalar(no))


def derive(source_root: Path, output_dir: Path) -> dict[str, Any]:
    start_utc = utc_now()
    start_perf = time.perf_counter()
    start_usage = resource.getrusage(resource.RUSAGE_SELF)
    output_dir.mkdir(parents=True, exist_ok=True)

    source_evidence = verify_sources(source_root)

    normalized_tables: list[pa.Table] = []
    per_source: dict[str, dict[str, Any]] = {}
    for spec in SOURCES:
        source_path = source_root / spec["path"]
        raw = pq.read_table(source_path, columns=["Date", "Code", "Open", "Close"])
        if raw.num_rows != spec["rows"]:
            raise RuntimeError(
                f"source {spec['year']} row mismatch: {raw.num_rows} != {spec['rows']}"
            )
        required = {"Date", "Code", "Open", "Close"}
        if set(raw.column_names) != required:
            raise RuntimeError(f"source {spec['year']} schema mismatch: {raw.column_names}")
        table = pa.table(
            {
                "Date": pc.cast(raw["Date"], pa.timestamp("ns"), safe=True),
                "Code": pc.cast(raw["Code"], pa.string(), safe=True),
                "Open": pc.cast(raw["Open"], pa.float64(), safe=True),
                "Close": pc.cast(raw["Close"], pa.float64(), safe=True),
                "SourceYear": pa.array([spec["year"]] * raw.num_rows, type=pa.int16()),
                "SourceRowIndex": pa.array(range(raw.num_rows), type=pa.int64()),
            }
        )
        normalized_tables.append(table)
        per_source[str(spec["year"])] = {
            "rows": raw.num_rows,
            "min_date": pc.min(table["Date"]).as_py().date().isoformat(),
            "max_date": pc.max(table["Date"]).as_py().date().isoformat(),
            "distinct_codes": pc.count_distinct(table["Code"]).as_py(),
            "distinct_dates": pc.count_distinct(table["Date"]).as_py(),
            "date_arrow_type_original": str(raw["Date"].type),
        }

    source_table = pa.concat_tables(normalized_tables, promote_options="none")
    total_rows = source_table.num_rows
    expected_total = sum(int(x["rows"]) for x in SOURCES)
    if total_rows != expected_total:
        raise RuntimeError(f"combined row mismatch: {total_rows} != {expected_total}")

    indices = pc.sort_indices(
        source_table,
        sort_keys=[
            ("Code", "ascending"),
            ("Date", "ascending"),
            ("SourceYear", "ascending"),
            ("SourceRowIndex", "ascending"),
        ],
        null_placement="at_end",
    )
    table = pc.take(source_table, indices).combine_chunks()

    date = table["Date"].chunk(0)
    code = table["Code"].chunk(0)
    open_price = table["Open"].chunk(0)
    close_price = table["Close"].chunk(0)
    source_year = table["SourceYear"].chunk(0)
    source_row = table["SourceRowIndex"].chunk(0)
    n = len(date)

    finite_open = pc.fill_null(pc.is_finite(open_price), False)
    finite_close = pc.fill_null(pc.is_finite(close_price), False)
    integral_open = pc.if_else(finite_open, pc.equal(open_price, pc.floor(open_price)), True)
    integral_close = pc.if_else(finite_close, pc.equal(close_price, pc.floor(close_price)), True)
    if not all_true(integral_open) or not all_true(integral_close):
        raise RuntimeError("non-integral finite Open/Close observed; refusing implicit rounding")

    open_int = pc.cast(open_price, pa.int64(), safe=True)
    close_int = pc.cast(close_price, pa.int64(), safe=True)
    prev_code = null_shifted(code)
    prev_date = null_shifted(date)
    prev_close = null_shifted(close_int)
    prev_source_year = null_shifted(source_year)

    same_code = pc.fill_null(pc.equal(code, prev_code), False)
    equal_prev_date = pc.fill_null(pc.equal(date, prev_date), False)
    dup_with_prev = pc.and_(same_code, equal_prev_date)
    if n:
        dup_with_next = pa.concat_arrays([dup_with_prev.slice(1), pa.array([False])])
    else:
        dup_with_next = dup_with_prev
    duplicate_key_row = pc.or_(dup_with_prev, dup_with_next)
    previous_duplicate_key = shifted(duplicate_key_row, pa.scalar(False))

    valid_code = pc.and_(pc.is_valid(code), pc.greater(pc.utf8_length(code), 0))
    valid_date = pc.is_valid(date)
    valid_open = pc.and_(pc.is_valid(open_int), finite_open)
    valid_close = pc.and_(pc.is_valid(close_int), finite_close)
    valid_prev_close = pc.and_(pc.is_valid(prev_close), shifted(finite_close, pa.scalar(False)))
    positive_open = pc.and_(valid_open, pc.greater(open_int, 0))
    positive_prev_close = pc.and_(valid_prev_close, pc.greater(prev_close, 0))

    key_domain_ok = pc.and_(valid_code, valid_date)
    duplicate_block = pc.or_(duplicate_key_row, previous_duplicate_key)
    first_observation = pc.and_(key_domain_ok, pc.invert(same_code))
    evaluable = pc.and_kleene(
        pc.and_kleene(pc.and_kleene(key_domain_ok, same_code), pc.invert(duplicate_block)),
        pc.and_kleene(positive_open, positive_prev_close),
    )
    evaluable = pc.fill_null(evaluable, False)

    signed_gap_all = pc.subtract(open_int, prev_close)
    absolute_gap_all = pc.abs(signed_gap_all)
    exact_left_all = pc.multiply(absolute_gap_all, THRESHOLD_DENOMINATOR)
    signal_all = pc.and_(evaluable, pc.greater_equal(exact_left_all, prev_close))
    exact_boundary_all = pc.and_(evaluable, pc.equal(exact_left_all, prev_close))
    nonsignal_all = pc.and_(evaluable, pc.invert(signal_all))

    missing_key_block = pc.invert(key_domain_ok)
    # Governed protocol section 4.1 step 6 takes precedence over the ordinary
    # first-observation terminal: Open<=0/missing/nonfinite is price-domain
    # quarantine even when no previous same-Code row exists.  PreviousClose is
    # applicable only when a previous same-Code observation exists.
    invalid_current_open = pc.invert(pc.fill_null(positive_open, False))
    invalid_previous_close = pc.and_(
        same_code, pc.invert(pc.fill_null(positive_prev_close, False))
    )
    not_evaluable_price = pc.fill_null(
        pc.and_(
            pc.and_(pc.fill_null(key_domain_ok, False), pc.invert(duplicate_block)),
            pc.or_(invalid_current_open, invalid_previous_close),
        ),
        False,
    )

    disposition: pa.Array = pa.array(
        ["NO_MATERIAL_SIGNAL_AXIS_B_TERMINAL"] * n, type=pa.string()
    )
    disposition = scalar_string_mask(signal_all, "MATERIAL_SIGNAL_PENDING_AXIS_C", disposition)
    disposition = scalar_string_mask(
        first_observation, "FIRST_OBSERVATION_NO_COMPARISON", disposition
    )
    disposition = scalar_string_mask(
        not_evaluable_price, "NOT_EVALUABLE_PRICE_DOMAIN", disposition
    )
    disposition = scalar_string_mask(
        missing_key_block, "NOT_EVALUABLE_KEY_DOMAIN", disposition
    )
    disposition = scalar_string_mask(
        duplicate_block, "DATA_INTEGRITY_BLOCKER", disposition
    )

    prev_date_output = pc.if_else(same_code, prev_date, pa.nulls(n, type=pa.timestamp("ns")))
    prev_close_output = pc.if_else(same_code, prev_close, pa.nulls(n, type=pa.int64()))
    signed_gap_output = pc.if_else(evaluable, signed_gap_all, pa.nulls(n, type=pa.int64()))
    absolute_gap_output = pc.if_else(evaluable, absolute_gap_all, pa.nulls(n, type=pa.int64()))
    denominator_output = pc.if_else(evaluable, prev_close, pa.nulls(n, type=pa.int64()))
    signal_output = pc.if_else(evaluable, signal_all, pa.nulls(n, type=pa.bool_()))

    direction: pa.Array = pa.array([None] * n, type=pa.string())
    direction = pc.if_else(
        pc.and_(evaluable, pc.equal(signed_gap_all, 0)), pa.scalar("FLAT"), direction
    )
    direction = pc.if_else(
        pc.and_(evaluable, pc.less(signed_gap_all, 0)), pa.scalar("DOWN"), direction
    )
    direction = pc.if_else(
        pc.and_(evaluable, pc.greater(signed_gap_all, 0)), pa.scalar("UP"), direction
    )

    date32 = pc.cast(date, pa.date32())
    prev_date32 = pc.cast(prev_date, pa.date32())
    calendar_gap_all = pc.subtract(
        pc.cast(date32, pa.int32()), pc.cast(prev_date32, pa.int32())
    )
    calendar_gap = pc.if_else(
        same_code, calendar_gap_all, pa.nulls(n, type=pa.int32())
    )
    year_seam = pc.and_(same_code, pc.not_equal(source_year, prev_source_year))
    seam_transition: pa.Array = pa.array([None] * n, type=pa.string())
    for previous, current in ((2024, 2025), (2024, 2026), (2025, 2026)):
        mask = pc.and_(
            same_code,
            pc.and_(pc.equal(prev_source_year, previous), pc.equal(source_year, current)),
        )
        seam_transition = pc.if_else(mask, pa.scalar(f"{previous}->{current}"), seam_transition)

    current_close_source_usable = pc.and_(valid_close, pc.greater(close_int, 0))

    ledger = pa.table(
        {
            "source_year": source_year,
            "source_row_index_zero_based": source_row,
            "date": pc.strftime(date, format="%Y-%m-%d"),
            "code": code,
            "open": open_int,
            "close": close_int,
            "current_close_source_usable": current_close_source_usable,
            "previous_observed_date": pc.strftime(prev_date_output, format="%Y-%m-%d"),
            "previous_observed_close": prev_close_output,
            "calendar_day_gap": calendar_gap,
            "signed_gap_price": signed_gap_output,
            "absolute_gap_price": absolute_gap_output,
            "gap_denominator_previous_close": denominator_output,
            "threshold_numerator": pa.array([THRESHOLD_NUMERATOR] * n, type=pa.int8()),
            "threshold_denominator": pa.array([THRESHOLD_DENOMINATOR] * n, type=pa.int8()),
            "direction": direction,
            "axis_b_signal": signal_output,
            "exact_threshold_boundary": pc.if_else(
                evaluable, exact_boundary_all, pa.nulls(n, type=pa.bool_())
            ),
            "year_seam": year_seam,
            "seam_transition": seam_transition,
            "disposition": disposition,
        }
    )

    signal_table = ledger.filter(signal_all)
    quarantine_mask = pc.or_(
        pc.equal(disposition, "DATA_INTEGRITY_BLOCKER"),
        pc.or_(
            pc.equal(disposition, "NOT_EVALUABLE_KEY_DOMAIN"),
            pc.equal(disposition, "NOT_EVALUABLE_PRICE_DOMAIN"),
        ),
    )
    quarantine_table = ledger.filter(quarantine_mask)

    write_csv_gz(ledger, output_dir / LEDGER_NAME)
    write_csv_gz(signal_table, output_dir / SIGNALS_NAME)
    write_csv_gz(quarantine_table, output_dir / QUARANTINE_NAME)

    disposition_counts = Counter(disposition.to_pylist())
    seam_counts: dict[str, dict[str, int]] = {}
    for transition in ("2024->2025", "2024->2026", "2025->2026"):
        mask = pc.equal(seam_transition, transition)
        seam_counts[transition] = {
            "rows": int(pc.sum(pc.cast(pc.fill_null(mask, False), pa.int64())).as_py()),
            "evaluable": int(
                pc.sum(pc.cast(pc.and_(pc.fill_null(mask, False), evaluable), pa.int64())).as_py()
            ),
            "signals": int(
                pc.sum(pc.cast(pc.and_(pc.fill_null(mask, False), signal_all), pa.int64())).as_py()
            ),
            "quarantined": int(
                pc.sum(pc.cast(pc.and_(pc.fill_null(mask, False), quarantine_mask), pa.int64())).as_py()
            ),
        }

    def count(mask: pa.Array | pa.ChunkedArray) -> int:
        return int(pc.sum(pc.cast(pc.fill_null(mask, False), pa.int64())).as_py())

    summary: dict[str, Any] = {
        "artifact_id": "AAA-M3TOP3-G3-AXIS-B-DERIVATION-SUMMARY-v0.1",
        "artifact_role": "NON_VALIDATOR_BOUNDED_MECHANICAL_SIGNAL_DERIVATION",
        "owner_decision": "OD-G3-B-01=YES",
        "claim_ceiling": "SIGNAL_ONLY_NO_CA_OR_ADJUSTMENT_INFERENCE_NO_GATE_PASS",
        "protocol": {
            "population": "EVERY_ROW_OF_EXACT_PINNED_2024_2025_2026_COMPONENTS",
            "group": "EXACT_CODE",
            "order": ["DATE_ASC", "SOURCE_YEAR_ASC_TIE_BREAK", "SOURCE_ROW_INDEX_ASC_TIE_BREAK"],
            "comparison": "CURRENT_OPEN_VS_IMMEDIATELY_PREVIOUS_OBSERVED_SAME_CODE_CLOSE",
            "year_boundaries": "STITCHED",
            "threshold": {"numerator": 1, "denominator": 5, "inclusive": True},
            "classification_equation": "5*abs(Open-PreviousClose)>=PreviousClose",
            "rounding": "NONE",
            "input_price_domain": "FINITE_INTEGRAL_PARQUET_DOUBLE_VERIFIED_BEFORE_CAST",
            "code_change_mapping": "NONE_NEW_CODE_STARTS_FIRST_OBSERVATION",
        },
        "source_commit": PINNED_COMMIT,
        "source_files": source_evidence,
        "population": {
            "rows": total_rows,
            "distinct_codes": int(pc.count_distinct(code).as_py()),
            "distinct_dates": int(pc.count_distinct(date).as_py()),
            "per_source": per_source,
        },
        "results": {
            "row_disposition_counts": dict(sorted(disposition_counts.items())),
            "evaluable_rows": count(evaluable),
            "material_signal_rows": count(signal_all),
            "non_signal_evaluable_rows": count(nonsignal_all),
            "exact_20_percent_boundary_rows": count(exact_boundary_all),
            "first_observation_rows": count(first_observation),
            "year_seam_rows": count(year_seam),
            "year_seams": seam_counts,
            "signal_directions": {
                "UP": count(pc.and_(signal_all, pc.greater(signed_gap_all, 0))),
                "DOWN": count(pc.and_(signal_all, pc.less(signed_gap_all, 0))),
                "FLAT": count(pc.and_(signal_all, pc.equal(signed_gap_all, 0))),
            },
        },
        "data_quality": {
            "duplicate_date_code_rows": count(duplicate_key_row),
            "rows_blocked_by_current_or_previous_duplicate_key": count(duplicate_block),
            "missing_or_blank_code_rows": count(pc.invert(valid_code)),
            "missing_date_rows": count(pc.invert(valid_date)),
            "missing_or_nonfinite_open_rows": count(pc.invert(valid_open)),
            "missing_or_nonfinite_close_rows": count(pc.invert(valid_close)),
            "nonpositive_open_rows": count(pc.and_(valid_open, pc.less_equal(open_int, 0))),
            "nonpositive_close_source_rows": count(
                pc.and_(valid_close, pc.less_equal(close_int, 0))
            ),
            "comparison_rows_with_nonpositive_previous_close": count(
                pc.and_(same_code, pc.and_(valid_prev_close, pc.less_equal(prev_close, 0)))
            ),
            "not_evaluable_key_domain_rows": count(missing_key_block),
            "not_evaluable_price_domain_rows": count(not_evaluable_price),
            "unresolved_rows": 0,
            "silent_drops": 0,
            "all_finite_open_close_integral": True,
        },
        "open_dependencies": {
            "axis_c_reconciliation_for_every_material_signal": "PENDING_EXACT_INDEPENDENT_KRX_CA_UNIVERSE",
            "corporate_action_inference": "NOT_PERFORMED",
            "adjustment_factor_inference": "NOT_PERFORMED",
            "g3_gate": "NOT_CLOSED",
        },
        "deterministic_outputs": [LEDGER_NAME, SIGNALS_NAME, QUARANTINE_NAME],
    }
    if sum(disposition_counts.values()) != total_rows:
        raise RuntimeError("disposition conservation failed")
    if count(signal_all) + count(nonsignal_all) != count(evaluable):
        raise RuntimeError("evaluable signal/non-signal conservation failed")
    json_write(output_dir / SUMMARY_NAME, summary)

    end_utc = utc_now()
    end_usage = resource.getrusage(resource.RUSAGE_SELF)
    elapsed = time.perf_counter() - start_perf
    telemetry = {
        "artifact_id": "AAA-M3TOP3-G3-AXIS-B-RUN-TELEMETRY-v0.1",
        "start_timestamp_kst": iso_kst(start_utc),
        "end_timestamp_kst": iso_kst(end_utc),
        "total_wall_seconds": round(elapsed, 6),
        "active_compute_wall_seconds": round(elapsed, 6),
        "source_recovery_wall_seconds_prior_observed": 27.537,
        "queue_wait_seconds": 0,
        "dependency_wait_seconds": 0,
        "rework_seconds": PRECOMPUTE_REWORK_SECONDS,
        "cpu_user_seconds": round(end_usage.ru_utime - start_usage.ru_utime, 6),
        "cpu_system_seconds": round(end_usage.ru_stime - start_usage.ru_stime, 6),
        "max_rss_kib": end_usage.ru_maxrss,
        "cru": "NOT_INSTRUMENTED",
        "python": platform.python_version(),
        "pyarrow": pa.__version__,
        "retry_count": 3,
        "retry_characterization": [
            "ONE_FORWARD_CODE_FIX_AFTER_UNSUPPORTED_ARROW_DURATION_CAST",
            "ONE_FORWARD_DISPOSITION_PRECEDENCE_FIX_OPEN_LE_ZERO_OVER_FIRST_OBSERVATION",
            "ONE_NULL_SAFE_BOOLEAN_MASK_FIX_AFTER_ARROW_NULL_PROPAGATION",
            "NO_LOOP"
        ],
        "validator_count": 0,
        "global_validation": False,
        "full_regression": False,
    }
    json_write(output_dir / TELEMETRY_NAME, telemetry)

    report = f"""# G3 Axis-B bounded derivation report

```text
EXECUTION_CLASS = NON_VALIDATOR_BOUNDED_MECHANICAL_DERIVATION
OWNER_DECISION = OD-G3-B-01 = YES
SOURCE_COMMIT = {PINNED_COMMIT}
POPULATION_ROWS = {total_rows:,}
MATERIAL_SIGNAL_ROWS = {count(signal_all):,}
G3_GATE = NOT_CLOSED
VALIDATION_CLAIM = NONE
```

## Result

Every row in the three exact pinned FinanceData/marcap components received one
Axis-B disposition after exact-Code chronological stitching. The comparison is
current `Open` against the immediately previous observed same-Code `Close`.
Classification used integer arithmetic
`5 * abs(Open - PreviousClose) >= PreviousClose`; no value was rounded.

| Measure | Count |
|---|---:|
| Population | {total_rows:,} |
| Evaluable comparisons | {count(evaluable):,} |
| Material signals (`>=20%`, inclusive) | {count(signal_all):,} |
| Exact 20% boundary signals | {count(exact_boundary_all):,} |
| Evaluable non-signals | {count(nonsignal_all):,} |
| First same-Code observations | {count(first_observation):,} |
| Duplicate Date+Code rows | {count(duplicate_key_row):,} |
| Price-domain quarantines | {count(not_evaluable_price):,} |
| Unresolved / silently dropped | 0 / 0 |

## Year seams

| Transition | Rows | Evaluable | Signals | Quarantined |
|---|---:|---:|---:|---:|
| 2024→2025 | {seam_counts['2024->2025']['rows']:,} | {seam_counts['2024->2025']['evaluable']:,} | {seam_counts['2024->2025']['signals']:,} | {seam_counts['2024->2025']['quarantined']:,} |
| 2024→2026 | {seam_counts['2024->2026']['rows']:,} | {seam_counts['2024->2026']['evaluable']:,} | {seam_counts['2024->2026']['signals']:,} | {seam_counts['2024->2026']['quarantined']:,} |
| 2025→2026 | {seam_counts['2025->2026']['rows']:,} | {seam_counts['2025->2026']['evaluable']:,} | {seam_counts['2025->2026']['signals']:,} | {seam_counts['2025->2026']['quarantined']:,} |

Long date gaps and seams remain mechanical observations only. They do not
imply a corporate action, suspension, relisting, adjustment, or status.

## Custody and boundaries

All three input sizes, SHA-256 values, Git blob IDs, and the detached HEAD were
verified before computation. The 2024/2025/2026 input hashes are respectively
`{SOURCES[0]['sha256']}`, `{SOURCES[1]['sha256']}`, and
`{SOURCES[2]['sha256']}`.

Material signals remain `MATERIAL_SIGNAL_PENDING_AXIS_C`. This derivation does
not infer corporate actions or factors, does not modify price data, and does
not close G3 or the integrated checkpoint. Axis-C exact independent KRX event
bytes are still required.

## Timing / resource accounting

| Item | Observed |
|---|---:|
| Source sparse recovery + exact hash check | 27.537 s |
| Derivation wall time | {elapsed:.3f} s |
| CPU user / system | {telemetry['cpu_user_seconds']:.3f} / {telemetry['cpu_system_seconds']:.3f} s |
| Peak RSS | {telemetry['max_rss_kib']:,} KiB |
| CRU | NOT_INSTRUMENTED |
| Retry / rework | 3 / {PRECOMPUTE_REWORK_SECONDS:.3f} s |
| Validator / global validation | 0 / FALSE |
"""
    (output_dir / REPORT_NAME).write_text(report, encoding="utf-8")

    output_files = [
        LEDGER_NAME,
        SIGNALS_NAME,
        QUARANTINE_NAME,
        SUMMARY_NAME,
        TELEMETRY_NAME,
        REPORT_NAME,
        Path(__file__).name,
    ]
    manifest = {
        "artifact_id": "AAA-M3TOP3-G3-AXIS-B-SOURCE-AND-OUTPUT-MANIFEST-v0.1",
        "source_commit": PINNED_COMMIT,
        "source_files": source_evidence,
        "outputs": {
            name: {
                "bytes": (output_dir / name).stat().st_size,
                "sha256": sha256_file(output_dir / name),
            }
            for name in output_files
        },
        "determinism": {
            "gzip_mtime": 0,
            "row_order": "CODE_DATE_SOURCE_YEAR_SOURCE_ROW_INDEX",
            "csv_lineterminator": "LF",
            "pyarrow": PYARROW_VERSION,
            "runtime_telemetry_and_report_are_run_specific": True,
        },
        "validation_claim": "NONE",
    }
    json_write(output_dir / MANIFEST_NAME, manifest)
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    derive(args.source_root.resolve(), args.output_dir.resolve())
