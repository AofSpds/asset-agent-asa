#!/usr/bin/env python3
"""Freeze a deterministic, outcome-blind eligibility process sample.

This script reads only the combined historical-eligibility rows from the
governed denominator closure queue.  It does not investigate eligibility,
change any eligibility state, or use winner/outcome/rank/return fields.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Callable, Iterable


ARTIFACT_ID = "M3TOP3-ELIGIBILITY-PROCESS-VALIDATION-SAMPLE-v0.1"
SEED = "M3TOP3-ELIGIBILITY-PILOT-v0.1"
EXPECTED_INPUT_SHA256 = (
    "02bde437c04b1cc3d314b30e9bdd41bdb9a9164d0d2df4468728bdab8089eb62"
)
EXPECTED_COMBINED_ROWS = 514
WINDOWS = tuple(f"W{i}" for i in range(1, 9))
CONTROL_KEY = ("W4", "482630")
CONTROL_NAME = "삼양엔씨켐"
PROHIBITED_FIELD_TOKENS = (
    "outcome",
    "winner",
    "rank",
    "return",
    "mfe",
    "mae",
    "top3",
    "top10",
    "top20",
)

OUTPUT_FIELDS = (
    "record_id",
    "record_role",
    "sample_inclusion",
    "sample_order",
    "stratum",
    "stratum_label",
    "selection_method",
    "window",
    "company_no",
    "canonical_name",
    "KRX_code",
    "queue_axis",
    "current_status",
    "component_state",
    "evidence_status",
    "closure_evidence_required",
    "source_sheet",
    "source_cell_ref",
    "source_workbook_row",
    "selection_hash_sha256",
    "eligibility_change_authorized",
    "eligibility_investigation_authorized",
    "scoring_authorized",
)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def selection_hash(row: dict[str, str], stratum: str) -> str:
    payload = f"{SEED}|{row['window']}|{row['KRX_code']}|{stratum}"
    return sha256_bytes(payload.encode("utf-8"))


def key(row: dict[str, str]) -> tuple[str, str]:
    return row["window"], row["KRX_code"]


def read_combined_rows(path: Path) -> tuple[list[dict[str, str]], str]:
    payload = path.read_bytes()
    digest = sha256_bytes(payload)
    if digest != EXPECTED_INPUT_SHA256:
        raise ValueError(
            f"input hash mismatch: expected {EXPECTED_INPUT_SHA256}, got {digest}"
        )

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = tuple(reader.fieldnames or ())
        lowered = tuple(name.lower() for name in fieldnames)
        prohibited = sorted(
            {
                token
                for name in lowered
                for token in PROHIBITED_FIELD_TOKENS
                if token in name
            }
        )
        if prohibited:
            raise ValueError(f"prohibited input field token(s): {prohibited}")
        rows = [
            dict(row)
            for row in reader
            if row["axis"] == "COMBINED_HISTORICAL_ELIGIBILITY"
        ]

    if len(rows) != EXPECTED_COMBINED_ROWS:
        raise ValueError(
            f"combined-row count mismatch: expected {EXPECTED_COMBINED_ROWS}, got {len(rows)}"
        )
    if set(row["window"] for row in rows) != set(WINDOWS):
        raise ValueError("combined queue does not contain exactly W1-W8")
    if any(row["current_status"] != "UNRESOLVED" for row in rows):
        raise ValueError("combined queue contains a non-UNRESOLVED current_status")
    if len({key(row) for row in rows}) != len(rows):
        raise ValueError("duplicate company-window key in combined queue")
    if CONTROL_KEY not in {key(row) for row in rows}:
        raise ValueError("fixed negative-control row not found")
    control_row = next(row for row in rows if key(row) == CONTROL_KEY)
    if control_row["canonical_name"] != CONTROL_NAME:
        raise ValueError("fixed negative-control identity mismatch")
    prohibited_output_fields = sorted(
        {
            field
            for field in OUTPUT_FIELDS
            if any(token in field.lower() for token in PROHIBITED_FIELD_TOKENS)
        }
    )
    if prohibited_output_fields:
        raise ValueError(f"prohibited output field(s): {prohibited_output_fields}")
    return rows, digest


def select_one_per_window(
    rows: Iterable[dict[str, str]],
    stratum: str,
    predicate: Callable[[dict[str, str]], bool],
    excluded: set[tuple[str, str]],
) -> list[dict[str, str]]:
    selected: list[dict[str, str]] = []
    for window in WINDOWS:
        candidates = [
            row
            for row in rows
            if row["window"] == window and predicate(row) and key(row) not in excluded
        ]
        if not candidates:
            raise ValueError(f"no candidate for {stratum} / {window}")
        chosen = min(candidates, key=lambda row: selection_hash(row, stratum))
        selected.append(chosen)
        excluded.add(key(chosen))
    return selected


def select_complete_company(
    rows: Iterable[dict[str, str]],
    excluded: set[tuple[str, str]],
) -> tuple[str, list[dict[str, str]], int]:
    by_company: dict[str, dict[str, dict[str, str]]] = defaultdict(dict)
    for row in rows:
        by_company[row["KRX_code"]][row["window"]] = row

    candidates: list[tuple[str, str, dict[str, dict[str, str]]]] = []
    for code, window_map in by_company.items():
        if set(window_map) != set(WINDOWS):
            continue
        if any((window, code) in excluded for window in WINDOWS):
            continue
        anchor = window_map["W1"]
        anchor_hash = selection_hash(anchor, "S4_ALL_WINDOWS")
        candidates.append((anchor_hash, code, window_map))

    if not candidates:
        raise ValueError("no complete W1-W8 company available for S4")
    _, code, window_map = min(candidates, key=lambda item: item[0])
    selected = [window_map[window] for window in WINDOWS]
    for row in selected:
        excluded.add(key(row))
    return code, selected, len(candidates)


def output_record(
    row: dict[str, str],
    *,
    record_role: str,
    included: bool,
    sample_order: int | None,
    stratum: str,
    stratum_label: str,
    selection_method: str,
) -> dict[str, object]:
    record_id = (
        f"EPV-{stratum.replace('_', '-')}-{row['window']}-{row['KRX_code']}"
    )
    return {
        "record_id": record_id,
        "record_role": record_role,
        "sample_inclusion": "TRUE" if included else "FALSE",
        "sample_order": sample_order if sample_order is not None else "",
        "stratum": stratum,
        "stratum_label": stratum_label,
        "selection_method": selection_method,
        "window": row["window"],
        "company_no": row["company_no"],
        "canonical_name": row["canonical_name"],
        "KRX_code": row["KRX_code"],
        "queue_axis": row["axis"],
        "current_status": row["current_status"],
        "component_state": row["membership_or_tradability"],
        "evidence_status": row["evidence_or_price_status"],
        "closure_evidence_required": row["closure_evidence_required"],
        "source_sheet": row["sheet"],
        "source_cell_ref": row["cell_ref"],
        "source_workbook_row": row["workbook_row"],
        "selection_hash_sha256": selection_hash(row, stratum),
        "eligibility_change_authorized": "FALSE",
        "eligibility_investigation_authorized": "FALSE",
        "scoring_authorized": "FALSE",
    }


def freeze_sample(rows: list[dict[str, str]]) -> tuple[list[dict[str, object]], dict]:
    by_key = {key(row): row for row in rows}
    excluded = {CONTROL_KEY}

    s4_code, s4_rows, s4_candidate_company_count = select_complete_company(rows, excluded)
    s1_rows = select_one_per_window(
        rows,
        "S1_TRUE",
        lambda row: row["membership_or_tradability"].endswith("/TRUE"),
        excluded,
    )
    s2_rows = select_one_per_window(
        rows,
        "S2_UNRESOLVED",
        lambda row: row["membership_or_tradability"].endswith("/UNRESOLVED"),
        excluded,
    )
    s3_rows = select_one_per_window(
        rows,
        "S3_LISTING_BOUNDARY_PROXY",
        lambda row: row["membership_or_tradability"].endswith("/UNRESOLVED"),
        excluded,
    )

    strata = (
        (
            "S1_TRUE",
            "known TRUE listing/tradability component; combined status remains UNRESOLVED",
            "one per window by ascending specified SHA-256",
            s1_rows,
        ),
        (
            "S2_UNRESOLVED",
            "UNRESOLVED listing/tradability component",
            "one per window by ascending specified SHA-256 after S4/control exclusions",
            s2_rows,
        ),
        (
            "S3_LISTING_BOUNDARY_PROXY",
            "distinct listing-history-pending process-boundary replicate",
            "one per window from UNRESOLVED listing component by ascending specified SHA-256 after S2 exclusions",
            s3_rows,
        ),
        (
            "S4_ALL_WINDOWS",
            "one company represented across W1-W8",
            "complete-company candidates ordered by the specified S4 W1 anchor hash",
            s4_rows,
        ),
    )

    records: list[dict[str, object]] = []
    sample_order = 1
    for stratum, label, method, selected_rows in strata:
        for row in selected_rows:
            records.append(
                output_record(
                    row,
                    record_role="PROCESS_SAMPLE",
                    included=True,
                    sample_order=sample_order,
                    stratum=stratum,
                    stratum_label=label,
                    selection_method=method,
                )
            )
            sample_order += 1

    control = output_record(
        by_key[CONTROL_KEY],
        record_role="FIXED_NEGATIVE_CONTROL",
        included=False,
        sample_order=None,
        stratum="FIXED_NEGATIVE_CONTROL",
        stratum_label="삼양엔씨켐 W4 unresolved denominator control; kept outside sample",
        selection_method="fixed by PMO packet; no random selection",
    )
    records.append(control)

    sample_records = [row for row in records if row["sample_inclusion"] == "TRUE"]
    if len(sample_records) != 32:
        raise ValueError(f"sample size is {len(sample_records)}, expected 32")
    if len({(row["window"], row["KRX_code"]) for row in sample_records}) != 32:
        raise ValueError("process sample contains duplicate company-window cells")
    if any(
        (row["window"], row["KRX_code"]) == CONTROL_KEY for row in sample_records
    ):
        raise ValueError("fixed negative control leaked into 32-cell sample")
    if Counter(row["stratum"] for row in sample_records) != {
        "S1_TRUE": 8,
        "S2_UNRESOLVED": 8,
        "S3_LISTING_BOUNDARY_PROXY": 8,
        "S4_ALL_WINDOWS": 8,
    }:
        raise ValueError("stratum count mismatch")
    if len({row["KRX_code"] for row in sample_records if row["stratum"] == "S4_ALL_WINDOWS"}) != 1:
        raise ValueError("S4 is not a single company")
    if {row["window"] for row in sample_records if row["stratum"] == "S4_ALL_WINDOWS"} != set(WINDOWS):
        raise ValueError("S4 does not span exactly W1-W8")

    diagnostics = {
        "combined_queue_rows": len(rows),
        "combined_queue_by_window": dict(
            sorted(Counter(row["window"] for row in rows).items())
        ),
        "component_state_distribution": dict(
            sorted(Counter(row["membership_or_tradability"] for row in rows).items())
        ),
        "s4_complete_company_candidates": s4_candidate_company_count,
        "s4_selected_company_code": s4_code,
        "s4_selected_company_name": s4_rows[0]["canonical_name"],
    }
    return records, diagnostics


def write_csv(path: Path, records: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=OUTPUT_FIELDS,
            extrasaction="raise",
            quoting=csv.QUOTE_ALL,
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(records)


def write_json(
    path: Path,
    records: list[dict[str, object]],
    diagnostics: dict,
    input_path: Path,
    input_sha256: str,
) -> None:
    sample_records = [row for row in records if row["sample_inclusion"] == "TRUE"]
    controls = [row for row in records if row["sample_inclusion"] == "FALSE"]
    payload = {
        "artifact_id": ARTIFACT_ID,
        "artifact_date": "2026-08-23",
        "status": "FROZEN_PROCESS_VALIDATION_SAMPLE",
        "authority_boundary": {
            "PMO_bounded_execution": True,
            "IVA_execution_participation": "NONE",
            "eligibility_investigation": "NOT_PERFORMED",
            "eligibility_change": "NOT_AUTHORIZED",
            "model_evaluation": "NOT_AUTHORIZED",
        },
        "source": {
            "path": input_path.as_posix(),
            "sha256": input_sha256,
            "filtered_axis": "COMBINED_HISTORICAL_ELIGIBILITY",
            "row_count": EXPECTED_COMBINED_ROWS,
        },
        "selection_contract": {
            "seed": SEED,
            "row_hash_expression": "SHA256('M3TOP3-ELIGIBILITY-PILOT-v0.1|window|KRX_code|stratum')",
            "ordering": "ascending hexadecimal SHA-256 within each eligible window/stratum pool",
            "collision_rule": "exclude fixed control, then exclude company-window cells selected by earlier strata",
            "stratum_sequence": [
                "S4_ALL_WINDOWS",
                "S1_TRUE",
                "S2_UNRESOLVED",
                "S3_LISTING_BOUNDARY_PROXY",
            ],
            "s4_company_rule": "choose the complete W1-W8 company with the smallest specified S4 hash on its W1 anchor row",
            "prohibited_field_tokens": list(PROHIBITED_FIELD_TOKENS),
        },
        "design_adjustment": {
            "requested_S3": "listing-boundary 8",
            "implemented_S3": "S3_LISTING_BOUNDARY_PROXY 8",
            "reason": (
                "The 514-row combined queue has no listing-date or distance-to-entry field. "
                "It contains 469 rows with an UNRESOLVED listing/tradability component and "
                "45 rows with a TRUE component. S3 therefore freezes a second, disjoint "
                "one-per-window listing-history-pending process sample. It is not evidence "
                "that any selected cell is temporally near a listing date."
            ),
            "claim_limit": "No temporal listing-boundary fact is inferred or changed.",
        },
        "diagnostics": diagnostics,
        "counts": {
            "process_sample": len(sample_records),
            "fixed_negative_controls_outside_sample": len(controls),
            "records_in_manifest": len(records),
            "by_stratum": dict(sorted(Counter(row["stratum"] for row in sample_records).items())),
            "sample_by_window": dict(sorted(Counter(row["window"] for row in sample_records).items())),
        },
        "sample_records": sample_records,
        "fixed_negative_controls": controls,
    }
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("remediation/r_wp23_data_closure/03_DENOMINATOR_CLOSURE_QUEUE.csv"),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("remediation/g2_eligibility_process_sample"),
    )
    args = parser.parse_args()

    rows, input_sha256 = read_combined_rows(args.input)
    records, diagnostics = freeze_sample(rows)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = args.output_dir / "ELIGIBILITY_PROCESS_VALIDATION_SAMPLE_MANIFEST_v0.1.csv"
    json_path = args.output_dir / "ELIGIBILITY_PROCESS_VALIDATION_SAMPLE_MANIFEST_v0.1.json"
    write_csv(csv_path, records)
    write_json(json_path, records, diagnostics, args.input, input_sha256)

    print(
        json.dumps(
            {
                "artifact_id": ARTIFACT_ID,
                "csv": csv_path.as_posix(),
                "csv_sha256": sha256_bytes(csv_path.read_bytes()),
                "json": json_path.as_posix(),
                "json_sha256": sha256_bytes(json_path.read_bytes()),
                "process_sample_rows": 32,
                "fixed_controls_outside_sample": 1,
                "selected_s4_company": diagnostics["s4_selected_company_name"],
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
