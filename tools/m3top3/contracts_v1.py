from __future__ import annotations

from datetime import date
from typing import Any, Iterable

from .core import parse_date, parse_datetime, sha256_hex
from .pit_guard import PITGuard

MODEL_VERSION = "M3TOP3-v1.0"
FEATURE_SCHEMA_VERSION = "M3TOP3-FEATURE-SCHEMA_v1.0_WORKING"
SCORER_VERSION = "M3TOP3-GATED-LINEAR_v1.0_WORKING"
WEIGHT_VERSION = "M3TOP3-WEIGHT-VERSION_v1.0_WORKING"
MODEL_INPUT_SCHEMA_VERSION = "MIS-v1.0"
SCORER_IO_VERSION = "SIO-v1.0"
WINDOW_MAPPING_VERSION = "WM-v1.1"

MISSING_STATES = {
    "AVAILABLE", "MISSING", "UNKNOWN", "REVIEW_REQUIRED", "NOT_FOUND",
    "NA_FOR_OVERLAP", "NA_FOR_HARD_GATE_OVERLAP",
}
ELIGIBILITY_STATES = {"ELIGIBLE", "INELIGIBLE", "REVIEW_REQUIRED", "UNKNOWN"}

REQUIRED_IDENTITY_FIELDS = (
    "snapshot_id", "snapshot_date", "snapshot_cutoff_at",
    "snapshot_content_hash_or_revision", "window_anchor_date",
    "window_mapping_version", "company_id", "krx_code", "universe_release_id",
    "eligibility_state", "model_version", "feature_schema_version",
    "scorer_version", "weight_version", "model_input_schema_version",
    "input_release_or_hash", "code_or_executable_identity",
)

EXTRA_FORBIDDEN_NAMES = {
    "actual_u127_mfe", "actual_u127_mae", "actual_future_return",
    "actual_future_rank", "top3_historical_performance",
    "critical_miss_historical_result", "preliminary_winner",
    "official_winner", "future_mfe", "future_mae", "future_return",
    "future_rank", "future_high", "future_close",
}


class ContractError(ValueError):
    pass


def _walk_keys(value: Any, path: str = ""):
    if isinstance(value, dict):
        for k, v in value.items():
            p = f"{path}.{k}" if path else str(k)
            yield str(k), p
            yield from _walk_keys(v, p)
    elif isinstance(value, list):
        for i, v in enumerate(value):
            yield from _walk_keys(v, f"{path}[{i}]")


def assert_no_outcome_fields(record: dict[str, Any]) -> None:
    hits = []
    for key, path in _walk_keys(record):
        if key.lower() in EXTRA_FORBIDDEN_NAMES:
            hits.append(path)
    if hits:
        raise ContractError(f"prohibited outcome-derived model inputs: {hits}")


def validate_mis_record(record: dict[str, Any]) -> None:
    missing = [f for f in REQUIRED_IDENTITY_FIELDS if f not in record]
    if missing:
        raise ContractError(f"MIS-v1.0 missing required fields: {missing}")

    if record["model_version"] != MODEL_VERSION:
        raise ContractError("model_version mismatch")
    if record["feature_schema_version"] != FEATURE_SCHEMA_VERSION:
        raise ContractError("feature_schema_version mismatch")
    if record["scorer_version"] != SCORER_VERSION:
        raise ContractError("scorer_version mismatch")
    if record["weight_version"] != WEIGHT_VERSION:
        raise ContractError("weight_version mismatch")
    if record["model_input_schema_version"] != MODEL_INPUT_SCHEMA_VERSION:
        raise ContractError("model_input_schema_version mismatch")
    if record["window_mapping_version"] != WINDOW_MAPPING_VERSION:
        raise ContractError("window_mapping_version mismatch")
    if record["eligibility_state"] not in ELIGIBILITY_STATES:
        raise ContractError(f"invalid eligibility_state={record['eligibility_state']!r}")

    parse_date(record["snapshot_date"])
    parse_date(record["window_anchor_date"])
    parse_datetime(record["snapshot_cutoff_at"])

    if parse_date(record["snapshot_date"]) > parse_date(record["window_anchor_date"]):
        raise ContractError("snapshot_date cannot be after window_anchor_date")

    assert_no_outcome_fields(record)
    PITGuard().assert_model_inputs([record], record["snapshot_cutoff_at"])


def validate_snapshot_batch(records: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = list(records)
    if not rows:
        raise ContractError("empty snapshot batch")
    for row in rows:
        validate_mis_record(row)

    batch_keys = (
        "snapshot_id", "snapshot_date", "snapshot_cutoff_at",
        "snapshot_content_hash_or_revision", "window_anchor_date",
        "window_mapping_version", "universe_release_id", "model_version",
        "feature_schema_version", "scorer_version", "weight_version",
        "model_input_schema_version", "input_release_or_hash",
        "code_or_executable_identity",
    )
    first = rows[0]
    for field in batch_keys:
        expected = first[field]
        if any(r[field] != expected for r in rows[1:]):
            raise ContractError(f"snapshot batch mixed identity for {field}")

    ids = [r["company_id"] for r in rows]
    if len(ids) != len(set(ids)):
        raise ContractError("duplicate company_id in one snapshot batch")
    return rows


def input_batch_hash(records: Iterable[dict[str, Any]]) -> str:
    rows = sorted(list(records), key=lambda r: r["company_id"])
    return sha256_hex(rows)
