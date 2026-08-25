#!/usr/bin/env python3
"""One bounded structural/reproducibility check for G3 Axis-B artifacts.

This is a worker-side mechanical check, not an independent validator act and
not a global/full regression.  It checks exact custody and output hashes,
deterministic gzip headers, full-row conservation/order/disposition counts,
and the exact inequality on the emitted signal subset.  It does not rederive
all comparisons and must be executed only once for this run.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import gzip
import hashlib
import json
import resource
import subprocess
import time
from collections import Counter
from pathlib import Path
from typing import Any


LEDGER_NAME = "G3_AXIS_B_FULL_ROW_DISPOSITION_LEDGER_v0.1.csv.gz"
SIGNALS_NAME = "G3_AXIS_B_MATERIAL_SIGNAL_ROWS_v0.1.csv.gz"
QUARANTINE_NAME = "G3_AXIS_B_QUARANTINE_ROWS_v0.1.csv.gz"
SUMMARY_NAME = "G3_AXIS_B_DERIVATION_SUMMARY_v0.1.json"
MANIFEST_NAME = "G3_AXIS_B_SOURCE_AND_OUTPUT_MANIFEST_v0.1.json"
CHECK_NAME = "G3_AXIS_B_TARGETED_STRUCTURAL_REPRO_CHECK_v0.1.json"
CHECKSUMS_NAME = "G3_AXIS_B_SHA256SUMS_v0.1.txt"
PINNED_COMMIT = "5e8e4e57f3fcb129a6ff20751f643f67d3592c82"
EXPECTED_ROWS = {2024: 687_708, 2025: 696_524, 2026: 437_787}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def git_value(repo: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(repo), *args], text=True, stderr=subprocess.STDOUT
    ).strip()


def gzip_mtime(path: Path) -> int:
    with path.open("rb") as handle:
        header = handle.read(10)
    if len(header) != 10 or header[:2] != b"\x1f\x8b":
        raise AssertionError(f"not gzip: {path.name}")
    return int.from_bytes(header[4:8], "little")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_true(value: str) -> bool:
    return value.lower() == "true"


def stream_ledger(path: Path, summary: dict[str, Any]) -> dict[str, Any]:
    expected_dispositions = summary["results"]["row_disposition_counts"]
    seen = {year: bytearray(rows) for year, rows in EXPECTED_ROWS.items()}
    disposition_counts: Counter[str] = Counter()
    seam_counts: Counter[str] = Counter()
    rows = 0
    previous_key: tuple[str, str, int, int] | None = None
    duplicate_source_identity = 0
    order_violations = 0
    with gzip.open(path, "rt", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {
            "source_year",
            "source_row_index_zero_based",
            "date",
            "code",
            "axis_b_signal",
            "year_seam",
            "seam_transition",
            "disposition",
        }
        if not required.issubset(reader.fieldnames or []):
            raise AssertionError("ledger schema missing required fields")
        for row in reader:
            rows += 1
            year = int(row["source_year"])
            source_index = int(row["source_row_index_zero_based"])
            if year not in seen or source_index < 0 or source_index >= len(seen[year]):
                raise AssertionError(f"source identity outside domain at ledger row {rows}")
            if seen[year][source_index]:
                duplicate_source_identity += 1
            seen[year][source_index] = 1
            disposition_counts[row["disposition"]] += 1
            if parse_true(row["year_seam"]):
                seam_counts[row["seam_transition"]] += 1
            key = (row["code"], row["date"], year, source_index)
            if previous_key is not None and key < previous_key:
                order_violations += 1
            previous_key = key

    missing_source_identity = {
        str(year): len(bits) - sum(bits) for year, bits in seen.items()
    }
    if rows != summary["population"]["rows"]:
        raise AssertionError(f"ledger rows {rows} != summary population")
    if dict(sorted(disposition_counts.items())) != expected_dispositions:
        raise AssertionError("ledger disposition counts != summary")
    if any(missing_source_identity.values()) or duplicate_source_identity:
        raise AssertionError("ledger source-row conservation failed")
    if order_violations:
        raise AssertionError("ledger deterministic row order failed")
    return {
        "rows": rows,
        "disposition_counts": dict(sorted(disposition_counts.items())),
        "source_identity_missing": missing_source_identity,
        "source_identity_duplicates": duplicate_source_identity,
        "order_violations": order_violations,
        "seam_rows": dict(sorted(seam_counts.items())),
    }


def stream_signals(path: Path, expected_rows: int) -> dict[str, Any]:
    rows = 0
    exact_predicate_failures = 0
    linkage_failures = 0
    disposition_failures = 0
    exact_boundary_rows = 0
    directions: Counter[str] = Counter()
    seam_signals: Counter[str] = Counter()
    with gzip.open(path, "rt", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            rows += 1
            open_price = int(row["open"])
            previous_close = int(row["previous_observed_close"])
            signed_gap = int(row["signed_gap_price"])
            absolute_gap = int(row["absolute_gap_price"])
            denominator = int(row["gap_denominator_previous_close"])
            if (
                previous_close <= 0
                or open_price <= 0
                or signed_gap != open_price - previous_close
                or absolute_gap != abs(signed_gap)
                or denominator != previous_close
                or 5 * absolute_gap < previous_close
                or row["threshold_numerator"] != "1"
                or row["threshold_denominator"] != "5"
                or not parse_true(row["axis_b_signal"])
            ):
                exact_predicate_failures += 1
            if not row["previous_observed_date"] or not row["calendar_day_gap"]:
                linkage_failures += 1
            if row["disposition"] != "MATERIAL_SIGNAL_PENDING_AXIS_C":
                disposition_failures += 1
            if 5 * absolute_gap == previous_close:
                exact_boundary_rows += 1
            directions[row["direction"]] += 1
            if parse_true(row["year_seam"]):
                seam_signals[row["seam_transition"]] += 1
    if rows != expected_rows:
        raise AssertionError(f"signal rows {rows} != {expected_rows}")
    if exact_predicate_failures or linkage_failures or disposition_failures:
        raise AssertionError("signal subset structural/exact predicate check failed")
    return {
        "rows": rows,
        "exact_predicate_failures": exact_predicate_failures,
        "linkage_failures": linkage_failures,
        "disposition_failures": disposition_failures,
        "exact_boundary_rows": exact_boundary_rows,
        "directions": {name: directions.get(name, 0) for name in ("DOWN", "FLAT", "UP")},
        "seam_signals": dict(sorted(seam_signals.items())),
    }


def stream_quarantine(path: Path, expected_rows: int) -> dict[str, Any]:
    rows = 0
    disposition_counts: Counter[str] = Counter()
    unexpected = 0
    allowed = {
        "DATA_INTEGRITY_BLOCKER",
        "NOT_EVALUABLE_KEY_DOMAIN",
        "NOT_EVALUABLE_PRICE_DOMAIN",
    }
    with gzip.open(path, "rt", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            rows += 1
            disposition_counts[row["disposition"]] += 1
            if row["disposition"] not in allowed:
                unexpected += 1
    if rows != expected_rows or unexpected:
        raise AssertionError("quarantine subset structural check failed")
    return {
        "rows": rows,
        "disposition_counts": dict(sorted(disposition_counts.items())),
        "unexpected_rows": unexpected,
    }


def run(artifact_dir: Path, source_root: Path) -> None:
    start = time.perf_counter()
    start_usage = resource.getrusage(resource.RUSAGE_SELF)
    summary = load_json(artifact_dir / SUMMARY_NAME)
    manifest = load_json(artifact_dir / MANIFEST_NAME)
    checks: list[str] = []

    if git_value(source_root, "rev-parse", "HEAD") != PINNED_COMMIT:
        raise AssertionError("pinned source commit mismatch")
    for source in manifest["source_files"]:
        path = source_root / source["path"]
        if path.stat().st_size != source["bytes"]:
            raise AssertionError(f"source size mismatch {source['path']}")
        if sha256_file(path) != source["sha256"]:
            raise AssertionError(f"source sha256 mismatch {source['path']}")
        if git_value(source_root, "rev-parse", f"HEAD:{source['path']}") != source["git_blob"]:
            raise AssertionError(f"source Git blob mismatch {source['path']}")
    checks.append("PINNED_SOURCE_COMMIT_SIZE_SHA256_GIT_BLOB_EXACT")

    for name, expected in manifest["outputs"].items():
        path = artifact_dir / name
        if path.stat().st_size != expected["bytes"] or sha256_file(path) != expected["sha256"]:
            raise AssertionError(f"manifest output mismatch: {name}")
    checks.append("MANIFEST_OUTPUT_SIZE_SHA256_EXACT")

    gzip_names = [LEDGER_NAME, SIGNALS_NAME, QUARANTINE_NAME]
    gzip_mtimes = {name: gzip_mtime(artifact_dir / name) for name in gzip_names}
    if any(gzip_mtimes.values()):
        raise AssertionError("nonzero gzip mtime")
    if any((artifact_dir / name).stat().st_size >= 100_000_000 for name in gzip_names):
        raise AssertionError("single gzip object reaches 100MB GitHub limit")
    checks.append("DETERMINISTIC_GZIP_MTIME_ZERO_AND_EACH_OBJECT_LT_100MB")

    ledger = stream_ledger(artifact_dir / LEDGER_NAME, summary)
    checks.append("FULL_ROW_CONSERVATION_ORDER_AND_DISPOSITION_COUNTS")
    signals = stream_signals(
        artifact_dir / SIGNALS_NAME, summary["results"]["material_signal_rows"]
    )
    checks.append("EMITTED_SIGNAL_SUBSET_EXACT_INEQUALITY_AND_LINKAGE")
    expected_quarantine = (
        summary["data_quality"]["rows_blocked_by_current_or_previous_duplicate_key"]
        + summary["data_quality"]["not_evaluable_key_domain_rows"]
        + summary["data_quality"]["not_evaluable_price_domain_rows"]
    )
    quarantine = stream_quarantine(artifact_dir / QUARANTINE_NAME, expected_quarantine)
    checks.append("QUARANTINE_SUBSET_COUNT_AND_ALLOWED_DISPOSITIONS")

    if signals["exact_boundary_rows"] != summary["results"]["exact_20_percent_boundary_rows"]:
        raise AssertionError("exact boundary count mismatch")
    if signals["directions"] != summary["results"]["signal_directions"]:
        raise AssertionError("signal direction count mismatch")
    if summary["data_quality"]["duplicate_date_code_rows"] != 0:
        raise AssertionError("unexpected duplicate Date+Code blocker")
    if summary["data_quality"]["unresolved_rows"] != 0 or summary["data_quality"]["silent_drops"] != 0:
        raise AssertionError("unresolved or silent-drop count nonzero")
    checks.append("SUMMARY_CONSERVATION_BOUNDARY_DIRECTION_AND_ZERO_UNRESOLVED")

    elapsed = time.perf_counter() - start
    end_usage = resource.getrusage(resource.RUSAGE_SELF)
    now = dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).isoformat(timespec="seconds")
    receipt = {
        "artifact_id": "AAA-M3TOP3-G3-AXIS-B-TARGETED-STRUCTURAL-REPRO-CHECK-v0.1",
        "issued_at_kst": now,
        "execution_class": "ONE_WORKER_TARGETED_STRUCTURAL_REPRO_CHECK",
        "validator_act": False,
        "global_validation": False,
        "full_regression": False,
        "rederives_full_signal_classification": False,
        "status": "WORKER_TARGETED_CHECK_OK",
        "checks": checks,
        "ledger": ledger,
        "signals": signals,
        "quarantine": quarantine,
        "gzip_mtime": gzip_mtimes,
        "timing": {
            "wall_seconds": round(elapsed, 6),
            "cpu_user_seconds": round(end_usage.ru_utime - start_usage.ru_utime, 6),
            "cpu_system_seconds": round(end_usage.ru_stime - start_usage.ru_stime, 6),
            "cru": "NOT_INSTRUMENTED",
        },
        "claim_ceiling": "MECHANICAL_WORKER_CHECK_ONLY_NO_VALIDATION_PASS_NO_GATE_EFFECT",
    }
    (artifact_dir / CHECK_NAME).write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    checksum_targets = sorted(
        path
        for path in artifact_dir.iterdir()
        if path.is_file()
        and path.name != CHECKSUMS_NAME
        and path.suffix != ".pyc"
    )
    lines = [f"{sha256_file(path)}  {path.name}" for path in checksum_targets]
    (artifact_dir / CHECKSUMS_NAME).write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-dir", type=Path, required=True)
    parser.add_argument("--source-root", type=Path, required=True)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run(args.artifact_dir.resolve(), args.source_root.resolve())
