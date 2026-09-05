from __future__ import annotations

import base64
import copy
import csv
import hashlib
import json
import os
import platform
import sys
from collections import Counter
from datetime import timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Iterable

from .contracts_v1 import assert_no_outcome_fields, validate_snapshot_batch
from .core import canonical_json_bytes, parse_date, parse_datetime, sha256_hex
from .coverage_limited_replay_v1 import (
    EXPECTED_COUNTS,
    FEATURE_IDS,
    MISSING_FEATURE_REASON,
    POPULATION_GIT_BLOB,
    POPULATION_PATH,
    POPULATION_REVISION,
    POPULATION_ROW_COUNT,
    POPULATION_SHA256,
    build_window_mis,
    validate_population,
)
from .runtime_v1 import build_engine
from .shared_interface_guards_v1 import (
    validate_consumed_value_provenance,
    validate_f08_freshness_provenance,
)


RUNNER_VERSION = "M3TOP3-REAL-INPUT-STRICT-PRAGMATIC-REPLAY-v1.0"
SOURCE_MANIFEST_SCHEMA = "M3TOP3-REAL-SOURCE-MANIFEST-v1.0"
FEATURE_LEAF_SCHEMA = "M3TOP3-REAL-FEATURE-LEAF-v1.0"
F02 = "F02_NUMERIC_BUSINESS_INFLECTION"
F02_ADMISSION_METHOD = "F02_KRX_PROVISIONAL_CORE_OPERATING_METRICS_v1"
F02_OPERATOR_ID = "M3TOP3_F02_RELATIVE_FROM_OBSERVED_PAIR_v1"
FEATURE_INPUT_REGISTRY_REF = (
    "79b46dc1f63f1cd215cc0ebc0c91b4ec09e7dc71:"
    "control/shared/M3TOP3-FEATURE-INPUT-REGISTRY_v1.0_WORKING.yaml@"
    "5faa4d5739bf9ecb0c11d16f6d7d697ff3983977"
)
PREDECESSOR_EXECUTABLE_BUNDLE_IDENTITY = (
    "M3TOP3-EXECUTABLE-BUNDLE-SHA256:"
    "82266d51a64382cbd34ee68872a3cd3e3f640c6ff438e84416906f8b8a8ab9c0"
)
W1_MAPPING = {
    "window_id": "W1",
    "window_anchor_date": "2024-08-10",
    "snapshot_cutoff_at": "2024-08-09T23:59:59+09:00",
    "entry_trade_date": "2024-08-12",
    "nominal_window_end": "2024-11-10",
    "evaluation_last_trade_date": "2024-11-08",
    "horizon_close_date": "2024-11-08",
    "exit_trade_date": "2024-11-11",
}

W1_KRX_CLOSURES = (
    "2024-08-15",
    "2024-09-16",
    "2024-09-17",
    "2024-09-18",
    "2024-10-01",
    "2024-10-03",
    "2024-10-09",
)


def _build_expected_w1_holding_dates() -> tuple[str, ...]:
    start = parse_date(W1_MAPPING["entry_trade_date"])
    end = parse_date(W1_MAPPING["evaluation_last_trade_date"])
    closures = {parse_date(value) for value in W1_KRX_CLOSURES}
    result: list[str] = []
    current = start
    while current <= end:
        if current.weekday() < 5 and current not in closures:
            result.append(current.isoformat())
        current += timedelta(days=1)
    return tuple(result)


EXPECTED_W1_HOLDING_DATES = _build_expected_w1_holding_dates()
W1_REPLAY_CALENDAR_BINDING = {
    "identity": "REPLAY_ONLY_PRICE_DATE_X_OFFICIAL_KRX_CLOSURE_BINDING-v1",
    "window_registry_revision": "e59ed048d6da76edcad82c9a58b0d083c6452471",
    "window_registry_blob": "033817e6335865e411d2bb4b5837434167091458",
    "window_registry_csv_sha256": "96d63cc98a01b6332cf9486440e7f3fdaa0ec5a2d605f21bc14a4025b46e69fe",
    "closure_2024_git_blob": "98c93ecb5dafe38723ee06fb07cbd80c7c8a2a4d",
    "closure_2024_sha256": "d5961ae5998036cc1710fe28e22d324db0233b570dd5c417b088fba1408f857f",
    "expected_holding_dates": list(EXPECTED_W1_HOLDING_DATES),
    "expected_holding_date_count": len(EXPECTED_W1_HOLDING_DATES),
    "expected_holding_dates_sha256": sha256_hex(list(EXPECTED_W1_HOLDING_DATES)),
    "rule": "INCLUSIVE_ENTRY_TO_EVALUATION_LAST_WEEKDAYS_MINUS_BOUND_KRX_CLOSURES",
    "authority_ceiling": "APPROVED_REPLAY_ONLY_NOT_PRODUCTION_CALENDAR_RELEASE",
}

OUTCOME_RUNTIME_POLICY = {
    "policy_id": "M3TOP3-W1-OUTCOME-PARQUET-RUNTIME-v1",
    "python": {
        "implementation": "CPython",
        "version": "3.12.14",
        "executable_name": "python.exe",
        "byte_size": 107_312,
        "sha256": "ebdb7ddc892a73a9ece422fda408d0bbc2d232904cedeaae359066ef2db37317",
    },
    "parquet_reader": {
        "distribution": "pyarrow",
        "version": "25.0.1",
        "dist_info_directory": "pyarrow-25.0.1.dist-info",
        "record_byte_size": 78_570,
        "record_sha256": "1eddf4fb72b1b071868dc02d6fc8242125d98c6557ae6af8f783b1c84ef6a797",
        "unhashed_existing_allowlist": ["pyarrow-25.0.1.dist-info/RECORD"],
        "require_dont_write_bytecode": True,
        "require_pycache_prefix": None,
        "verification_rule": (
            "LOCATE_WITHOUT_IMPORT_THEN_VERIFY_RECORD_AND_EVERY_HASHED_ENTRY_AND_REJECT_"
            "NONALLOWLIST_UNHASHED_EXISTING_BYTES_BEFORE_IMPORT_AND_PRICE_ACCESS"
        ),
    },
}

MANIFEST_KEYS = {
    "schema_version",
    "manifest_id",
    "run_id",
    "created_at",
    "purpose",
    "population_binding",
    "windows",
    "sources",
}
POPULATION_BINDING_KEYS = {"revision", "path", "git_blob", "compressed_sha256", "row_count"}
WINDOW_KEYS = {"window_id", "window_anchor_date", "snapshot_cutoff_at", "entry_date", "include_count"}
SOURCE_KEYS = {
    "source_id",
    "company_id",
    "krx_code",
    "source_type",
    "source_tier",
    "title",
    "publisher",
    "publication_at",
    "publication_date",
    "publication_precision",
    "publication_interval",
    "canonical_locator",
    "raw_storage_ref",
    "raw_artifact",
    "acquired_at",
    "acquisition",
    "status",
    "source_limitations",
    "outcome_custody",
    "admission",
}
LEAF_KEYS = {
    "schema_version",
    "record_id",
    "run_id",
    "source_manifest_id",
    "source_manifest_sha256",
    "population_row_key",
    "window_id",
    "snapshot_cutoff_at",
    "company_id",
    "krx_code",
    "feature_id",
    "input_path",
    "value",
    "value_type",
    "unit_or_category",
    "availability_state",
    "evidence_kind",
    "temporal_status",
    "publication_at_or_interval",
    "effective_period",
    "produced_at",
    "source_refs",
    "transform_or_estimation_method_id",
    "input_lineage_refs",
    "contains_estimated_input",
    "missing_reason",
    "admission",
}


def _leaf_spec(metric: str, field: str, *, line: int | None = None) -> dict[str, Any]:
    observed = field in {"current", "prior"}
    return {
        "metric": metric,
        "field": field,
        "evidence_kind": "OBSERVED" if observed else "DERIVED",
        "value_type": "DECIMAL" if observed else ("ENUM" if field == "change_mode" else "IDENTIFIER"),
        "unit": "KRW_MILLION" if observed else ("UNITLESS_ENUM" if field == "change_mode" else "METHOD_ID"),
        "period": (
            "2024Q2" if field == "current" else "2023Q2" if field == "prior" else "2024Q2_VS_2023Q2"
        ),
        "basis": "QUARTER" if observed else "QUARTER_COMPARISON",
        "line": line,
    }


F02_LEAF_SPECS = {
    "/metric_pairs/operating_profit/current": _leaf_spec("operating_profit", "current", line=59),
    "/metric_pairs/operating_profit/prior": _leaf_spec("operating_profit", "prior", line=62),
    "/metric_pairs/operating_profit/change_mode": _leaf_spec("operating_profit", "change_mode"),
    "/metric_pairs/operating_profit/operator_id": _leaf_spec("operating_profit", "operator_id"),
    "/metric_pairs/revenue/current": _leaf_spec("revenue", "current", line=42),
    "/metric_pairs/revenue/prior": _leaf_spec("revenue", "prior", line=45),
    "/metric_pairs/revenue/change_mode": _leaf_spec("revenue", "change_mode"),
    "/metric_pairs/revenue/operator_id": _leaf_spec("revenue", "operator_id"),
}


class RealInputReplayError(ValueError):
    pass


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _git_blob_oid(payload: bytes) -> str:
    return hashlib.sha1(f"blob {len(payload)}\0".encode("ascii") + payload).hexdigest()


def _reject_json_constant(value: str) -> None:
    raise RealInputReplayError(f"non-finite JSON constant is forbidden: {value}")


def _reject_json_float(value: str) -> None:
    raise RealInputReplayError(f"JSON floating-point numbers are forbidden: {value}")


def _object_without_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise RealInputReplayError(f"duplicate JSON key is forbidden: {key}")
        result[key] = value
    return result


def _strict_json_loads(payload: str, context: str) -> Any:
    try:
        return json.loads(
            payload,
            object_pairs_hook=_object_without_duplicate_keys,
            parse_constant=_reject_json_constant,
            parse_float=_reject_json_float,
        )
    except (json.JSONDecodeError, RealInputReplayError) as exc:
        if isinstance(exc, RealInputReplayError):
            raise
        raise RealInputReplayError(f"{context}: invalid JSON") from exc


def _assert_exact_keys(value: dict[str, Any], expected: set[str], context: str) -> None:
    if not isinstance(value, dict) or set(value) != expected:
        present = set(value) if isinstance(value, dict) else set()
        raise RealInputReplayError(
            f"{context}: exact keys required; missing={sorted(expected - present)}, extra={sorted(present - expected)}"
        )


def _canonical_decimal(value: Any, context: str) -> Decimal:
    if not isinstance(value, str) or not value or value.strip() != value:
        raise RealInputReplayError(f"{context}: canonical decimal string required")
    try:
        result = Decimal(value)
    except InvalidOperation as exc:
        raise RealInputReplayError(f"{context}: canonical decimal string required") from exc
    if not result.is_finite() or format(result, "f") != value:
        raise RealInputReplayError(f"{context}: non-canonical or non-finite decimal")
    return result


def load_source_manifest(path: str | Path) -> tuple[dict[str, Any], str]:
    source_path = Path(path)
    try:
        payload = source_path.read_bytes()
        text = payload.decode("utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise RealInputReplayError("source manifest is not readable UTF-8") from exc
    result = _strict_json_loads(text, "source manifest")
    if not isinstance(result, dict):
        raise RealInputReplayError("source manifest must be a JSON object")
    return result, hashlib.sha256(payload).hexdigest()


def load_feature_sidecar(path: str | Path) -> tuple[list[dict[str, Any]], str]:
    sidecar_path = Path(path)
    try:
        payload = sidecar_path.read_bytes()
        text = payload.decode("utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise RealInputReplayError("feature sidecar is not readable UTF-8") from exc
    result = [
        _strict_json_loads(line, f"feature sidecar line {index}")
        for index, line in enumerate(text.splitlines(), start=1)
        if line.strip()
    ]
    if not result or any(not isinstance(record, dict) for record in result):
        raise RealInputReplayError("feature sidecar requires at least one object record")
    return result, hashlib.sha256(payload).hexdigest()


def validate_source_manifest(
    manifest: dict[str, Any],
    *,
    manifest_content_sha256: str,
    repo: str | Path,
    expected_run_id: str,
) -> dict[str, dict[str, Any]]:
    _assert_exact_keys(manifest, MANIFEST_KEYS, "source manifest")
    if manifest["schema_version"] != SOURCE_MANIFEST_SCHEMA or manifest["run_id"] != expected_run_id:
        raise RealInputReplayError("source manifest schema/run mismatch")
    if manifest["purpose"] != "MODEL_INPUT_ONLY" or not str(manifest["manifest_id"]):
        raise RealInputReplayError("source manifest purpose/identity mismatch")
    parse_datetime(manifest["created_at"])
    if len(manifest_content_sha256) != 64 or any(ch not in "0123456789abcdef" for ch in manifest_content_sha256):
        raise RealInputReplayError("source manifest content SHA-256 is malformed")

    binding = manifest["population_binding"]
    _assert_exact_keys(binding, POPULATION_BINDING_KEYS, "population_binding")
    expected_binding = {
        "revision": POPULATION_REVISION,
        "path": POPULATION_PATH,
        "git_blob": POPULATION_GIT_BLOB,
        "compressed_sha256": POPULATION_SHA256,
        "row_count": POPULATION_ROW_COUNT,
    }
    if binding != expected_binding:
        raise RealInputReplayError("source manifest population binding mismatch")
    if manifest["windows"] != [
        {
            "window_id": "W1",
            "window_anchor_date": W1_MAPPING["window_anchor_date"],
            "snapshot_cutoff_at": W1_MAPPING["snapshot_cutoff_at"],
            "entry_date": W1_MAPPING["entry_trade_date"],
            "include_count": EXPECTED_COUNTS["W1"]["ELIGIBLE"],
        }
    ]:
        raise RealInputReplayError("source manifest W1 binding mismatch")
    _assert_exact_keys(manifest["windows"][0], WINDOW_KEYS, "windows[0]")

    if not isinstance(manifest["sources"], list) or not manifest["sources"]:
        raise RealInputReplayError("source manifest requires at least one source")
    repo_path = Path(repo).resolve()
    source_root = (
        repo_path
        / "control/m3top3/real-input-replay/v1.0/runs"
        / expected_run_id
        / "sources"
    ).resolve()
    by_id: dict[str, dict[str, Any]] = {}
    for index, source in enumerate(manifest["sources"]):
        context = f"sources[{index}]"
        _assert_exact_keys(source, SOURCE_KEYS, context)
        source_id = str(source["source_id"])
        if not source_id or source_id in by_id:
            raise RealInputReplayError(f"{context}: source_id missing or duplicated")
        if source["company_id"] != f"KRX:{source['krx_code']}" or len(source["krx_code"]) != 6:
            raise RealInputReplayError(f"{context}: exact company/code binding required")
        if source["source_type"] != "FILING" or source["publisher"] != "KOREA_EXCHANGE_KIND_OFFICIAL":
            raise RealInputReplayError(f"{context}: unsupported source authority/type")
        if source["publication_at"] is not None or source["publication_precision"] != "DATE_ONLY":
            raise RealInputReplayError(f"{context}: date-only source precision must not be promoted")
        publication_date = parse_date(source["publication_date"])
        interval = source["publication_interval"]
        _assert_exact_keys(interval, {"earliest_at", "latest_at", "bound_method_id"}, f"{context}.interval")
        expected_prefix = publication_date.isoformat()
        if interval != {
            "earliest_at": f"{expected_prefix}T00:00:00+09:00",
            "latest_at": f"{expected_prefix}T23:59:59+09:00",
            "bound_method_id": "DATE_ONLY_KST_CLOSED_DAY_v1",
        }:
            raise RealInputReplayError(f"{context}: date-only interval was not conservatively derived")
        if parse_datetime(interval["latest_at"]) > parse_datetime(W1_MAPPING["snapshot_cutoff_at"]):
            raise RealInputReplayError(f"{context}: source is post-cutoff")
        if not str(source["canonical_locator"]).startswith("https://kind.krx.co.kr/"):
            raise RealInputReplayError(f"{context}: official KIND HTTPS locator required")

        relative = Path(str(source["raw_storage_ref"]))
        candidate = (repo_path / relative).resolve()
        try:
            candidate.relative_to(source_root)
        except ValueError as exc:
            raise RealInputReplayError(f"{context}: raw source path escapes the exact run sources root") from exc
        if not candidate.is_file():
            raise RealInputReplayError(f"{context}: raw source file is missing")
        raw_artifact = source["raw_artifact"]
        _assert_exact_keys(raw_artifact, {"byte_size", "sha256", "git_blob", "media_type", "charset"}, f"{context}.raw")
        raw_bytes = candidate.read_bytes()
        if (
            raw_artifact["byte_size"] != len(raw_bytes)
            or raw_artifact["sha256"] != hashlib.sha256(raw_bytes).hexdigest()
            or raw_artifact["git_blob"] != _git_blob_oid(raw_bytes)
            or raw_artifact["media_type"] != "text/html"
            or raw_artifact["charset"] != "UTF-8"
        ):
            raise RealInputReplayError(f"{context}: raw artifact identity mismatch")
        try:
            source_text = raw_bytes.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise RealInputReplayError(f"{context}: raw source charset mismatch") from exc
        if any(anchor not in source_text for anchor in (source["title"], "(주)동진쎄미켐", "2024.08.02", "잠정")):
            raise RealInputReplayError(f"{context}: company/title/date/provisional anchors absent")

        parse_datetime(source["acquired_at"])
        _assert_exact_keys(source["acquisition"], {"actor_id", "method", "request_ref"}, f"{context}.acquisition")
        if source["acquisition"]["method"] != "HTTPS_GET" or source["status"] != "PRESERVED_RAW":
            raise RealInputReplayError(f"{context}: custody state mismatch")
        if not isinstance(source["source_limitations"], list) or not source["source_limitations"]:
            raise RealInputReplayError(f"{context}: source limitations must be retained")
        custody = source["outcome_custody"]
        _assert_exact_keys(custody, {"state", "outcome_surface_accessed", "receipt_ref"}, f"{context}.custody")
        if custody["outcome_surface_accessed"] is not False:
            raise RealInputReplayError(f"{context}: source admitted after outcome-custody breach")
        admission = source["admission"]
        _assert_exact_keys(admission, {"state", "temporal_status", "cutoff_at", "reason_code", "evaluated_at"}, f"{context}.admission")
        if (
            admission["state"] != "ADMITTED_STRICT"
            or admission["temporal_status"] != "CUTOFF_SAFE"
            or admission["cutoff_at"] != W1_MAPPING["snapshot_cutoff_at"]
        ):
            raise RealInputReplayError(f"{context}: source is not Strict-admitted")
        parse_datetime(admission["evaluated_at"])
        by_id[source_id] = {**source, "_raw_path": candidate, "_raw_text_lines": source_text.splitlines()}
    return by_id


def _record_id(company_id: str, metric: str, field: str) -> str:
    code = company_id.split(":", 1)[1]
    return f"LEAF-W1-{code}-F02-{metric.replace('_', '-').upper()}-{field.replace('_', '-').upper()}"


def _source_evidence_ref(source: dict[str, Any], locator: str) -> str:
    return f"SHA256:{source['raw_artifact']['sha256']}#{source['source_id']}#{locator}"


def validate_feature_leaves(
    records: Iterable[dict[str, Any]],
    *,
    manifest: dict[str, Any],
    manifest_content_sha256: str,
    sources: dict[str, dict[str, Any]],
    population_rows: Iterable[dict[str, Any]],
    expected_run_id: str,
) -> list[dict[str, Any]]:
    population = {
        (row["window_id"], row["company_id"]): row for row in validate_population(population_rows)
    }
    materialized = list(records)
    record_ids: set[str] = set()
    leaf_keys: set[tuple[str, str, str, str]] = set()
    by_id: dict[str, dict[str, Any]] = {}
    for index, record in enumerate(materialized):
        context = f"leaf[{index}]"
        _assert_exact_keys(record, LEAF_KEYS, context)
        assert_no_outcome_fields(record)
        if record["schema_version"] != FEATURE_LEAF_SCHEMA or record["run_id"] != expected_run_id:
            raise RealInputReplayError(f"{context}: schema/run mismatch")
        if (
            record["source_manifest_id"] != manifest["manifest_id"]
            or record["source_manifest_sha256"] != manifest_content_sha256
        ):
            raise RealInputReplayError(f"{context}: source manifest identity mismatch")
        key = (record["window_id"], record["company_id"], record["feature_id"], record["input_path"])
        if key in leaf_keys or record["record_id"] in record_ids:
            raise RealInputReplayError(f"{context}: duplicate leaf key or record_id")
        leaf_keys.add(key)
        record_ids.add(record["record_id"])
        by_id[record["record_id"]] = record
        if record["window_id"] != "W1" or record["feature_id"] != F02:
            raise RealInputReplayError(f"{context}: bounded Strict route admits W1 F02 only")
        if record["snapshot_cutoff_at"] != W1_MAPPING["snapshot_cutoff_at"]:
            raise RealInputReplayError(f"{context}: cutoff mismatch")
        if (
            record["company_id"] != f"KRX:{record['krx_code']}"
            or len(record["krx_code"]) != 6
            or not record["krx_code"].isalnum()
            or record["krx_code"] != record["krx_code"].upper()
        ):
            raise RealInputReplayError(f"{context}: exact six-character code binding required")
        population_row = population.get(("W1", record["company_id"]))
        if (
            population_row is None
            or population_row["row_key"] != record["population_row_key"]
            or population_row["historical_eligibility_status"] != "ELIGIBLE"
        ):
            raise RealInputReplayError(f"{context}: target is not the frozen W1 INCLUDE row")
        spec = F02_LEAF_SPECS.get(record["input_path"])
        if spec is None:
            raise RealInputReplayError(f"{context}: input path is not allowlisted")
        if record["record_id"] != _record_id(record["company_id"], spec["metric"], spec["field"]):
            raise RealInputReplayError(f"{context}: record_id/path mismatch")
        if (
            record["availability_state"] != "AVAILABLE"
            or record["missing_reason"] is not None
            or record["temporal_status"] != "CUTOFF_SAFE"
            or record["contains_estimated_input"] is not False
            or record["evidence_kind"] not in {"OBSERVED", "DERIVED"}
            or record["evidence_kind"] != spec["evidence_kind"]
        ):
            raise RealInputReplayError(f"{context}: invalid Strict leaf state")
        if record["value_type"] != spec["value_type"] or record["unit_or_category"] != spec["unit"]:
            raise RealInputReplayError(f"{context}: value type/unit mismatch")
        effective = record["effective_period"]
        _assert_exact_keys(effective, {"label", "basis", "scope"}, f"{context}.period")
        if effective != {"label": spec["period"], "basis": spec["basis"], "scope": "CONSOLIDATED"}:
            raise RealInputReplayError(f"{context}: period/scope mismatch")
        timing = record["publication_at_or_interval"]
        _assert_exact_keys(
            timing,
            {"precision", "publication_at", "publication_date", "latest_possible_at", "bound_method_id"},
            f"{context}.timing",
        )
        parse_datetime(record["produced_at"])
        admission = record["admission"]
        _assert_exact_keys(admission, {"state", "reason_code", "decided_at"}, f"{context}.admission")
        if admission["state"] != "ADMITTED":
            raise RealInputReplayError(f"{context}: leaf is not admitted")
        parse_datetime(admission["decided_at"])

        if spec["evidence_kind"] == "OBSERVED":
            value = _canonical_decimal(record["value"], f"{context}.value")
            if spec["field"] == "prior" and value == 0:
                raise RealInputReplayError(f"{context}: RELATIVE prior cannot be zero")
            if record["transform_or_estimation_method_id"] is not None or record["input_lineage_refs"]:
                raise RealInputReplayError(f"{context}: observed leaf carries transform lineage")
            if not isinstance(record["source_refs"], list) or len(record["source_refs"]) != 1:
                raise RealInputReplayError(f"{context}: observed leaf requires one exact source ref")
            source_ref = record["source_refs"][0]
            _assert_exact_keys(source_ref, {"source_id", "source_content_sha256", "locator"}, f"{context}.source_ref")
            source = sources.get(source_ref["source_id"])
            if source is None or source["company_id"] != record["company_id"]:
                raise RealInputReplayError(f"{context}: source ref does not resolve to this company")
            expected_locator = f"html:line-{spec['line']}"
            if (
                source_ref["source_content_sha256"] != source["raw_artifact"]["sha256"]
                or source_ref["locator"] != expected_locator
            ):
                raise RealInputReplayError(f"{context}: source content/locator mismatch")
            line = source["_raw_text_lines"][spec["line"] - 1]
            if f"{int(value):,}" not in line:
                raise RealInputReplayError(f"{context}: observed value is absent at exact locator")
        else:
            if record["source_refs"] != [] or record["transform_or_estimation_method_id"] != F02_OPERATOR_ID:
                raise RealInputReplayError(f"{context}: derived control provenance mismatch")
            if spec["field"] == "change_mode" and record["value"] != "RELATIVE":
                raise RealInputReplayError(f"{context}: change_mode mismatch")
            if spec["field"] == "operator_id" and record["value"] != F02_OPERATOR_ID:
                raise RealInputReplayError(f"{context}: operator_id mismatch")
        source_for_timing = next(
            (source for source in sources.values() if source["company_id"] == record["company_id"]),
            None,
        )
        if source_for_timing is None or timing != {
            "precision": "DATE_ONLY",
            "publication_at": None,
            "publication_date": source_for_timing["publication_date"],
            "latest_possible_at": source_for_timing["publication_interval"]["latest_at"],
            "bound_method_id": "DATE_ONLY_KST_CLOSED_DAY_v1",
        }:
            raise RealInputReplayError(f"{context}: source timing lineage mismatch")
        if parse_datetime(timing["latest_possible_at"]) > parse_datetime(record["snapshot_cutoff_at"]):
            raise RealInputReplayError(f"{context}: post-cutoff leaf")

    grouped: dict[tuple[str, str, str], set[str]] = {}
    for record in materialized:
        grouped.setdefault((record["window_id"], record["company_id"], record["feature_id"]), set()).add(record["input_path"])
    if any(paths != set(F02_LEAF_SPECS) for paths in grouped.values()):
        raise RealInputReplayError("each admitted F02 block requires all eight governed leaves")
    for record in materialized:
        spec = F02_LEAF_SPECS[record["input_path"]]
        if spec["evidence_kind"] != "DERIVED":
            continue
        expected_lineage = sorted(
            [
                _record_id(record["company_id"], spec["metric"], "current"),
                _record_id(record["company_id"], spec["metric"], "prior"),
            ]
        )
        if sorted(record["input_lineage_refs"]) != expected_lineage or any(ref not in by_id for ref in expected_lineage):
            raise RealInputReplayError(f"{record['record_id']}: derived lineage is incomplete")
    return sorted(materialized, key=lambda row: (row["window_id"], row["company_id"], row["feature_id"], row["input_path"]))


def _pointer_to_dotted(pointer: str) -> str:
    return ".".join(part for part in pointer.split("/") if part)


def _set_pointer(target: dict[str, Any], pointer: str, value: Any) -> None:
    parts = [part for part in pointer.split("/") if part]
    if not parts:
        raise RealInputReplayError("empty input pointer")
    cursor = target
    for part in parts[:-1]:
        child = cursor.setdefault(part, {})
        if not isinstance(child, dict):
            raise RealInputReplayError(f"pointer collision at {pointer}")
        cursor = child
    cursor[parts[-1]] = value


def _resolve_pointer(target: dict[str, Any], pointer: str) -> Any:
    cursor: Any = target
    for part in (part for part in pointer.split("/") if part):
        if not isinstance(cursor, dict) or part not in cursor:
            raise RealInputReplayError(f"unresolved consumed pointer {pointer}")
        cursor = cursor[part]
    return cursor


def build_strict_w1_mis(
    population_rows: Iterable[dict[str, Any]],
    *,
    pmo_run_id: str,
    manifest: dict[str, Any],
    manifest_content_sha256: str,
    leaf_records: Iterable[dict[str, Any]],
    repo: str | Path,
    code_identity: str,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if not code_identity or code_identity == PREDECESSOR_EXECUTABLE_BUNDLE_IDENTITY:
        raise RealInputReplayError("successor adapter requires a new executable bundle identity")
    population = validate_population(population_rows)
    sources = validate_source_manifest(
        manifest,
        manifest_content_sha256=manifest_content_sha256,
        repo=repo,
        expected_run_id=pmo_run_id,
    )
    leaves = validate_feature_leaves(
        leaf_records,
        manifest=manifest,
        manifest_content_sha256=manifest_content_sha256,
        sources=sources,
        population_rows=population,
        expected_run_id=pmo_run_id,
    )
    rows = build_window_mis("W1", population, pmo_run_id=pmo_run_id, code_identity=code_identity)
    semantic_sidecar_sha256 = sha256_hex(leaves)
    composite_input_sha256 = sha256_hex(
        {
            "population_sha256": POPULATION_SHA256,
            "source_manifest_content_sha256": manifest_content_sha256,
            "semantic_feature_leaf_sha256": semantic_sidecar_sha256,
            "window_id": "W1",
        }
    )
    for row in rows:
        row["window_anchor_date"] = W1_MAPPING["window_anchor_date"]
        row["input_release_or_hash"] = f"SHA256:{composite_input_sha256}"

    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for leaf in leaves:
        grouped.setdefault((leaf["window_id"], leaf["company_id"]), []).append(leaf)
    row_by_key = {("W1", row["company_id"]): row for row in rows}
    for key, block_leaves in sorted(grouped.items()):
        block: dict[str, Any] = {"availability_state": "AVAILABLE", "metric_pairs": {}}
        provenance: dict[str, dict[str, Any]] = {}
        source_lineage_refs: set[str] = set()
        for leaf in block_leaves:
            _set_pointer(block, leaf["input_path"], leaf["value"])
            dotted = _pointer_to_dotted(leaf["input_path"])
            if leaf["evidence_kind"] == "OBSERVED":
                source_ref = leaf["source_refs"][0]
                source = sources[source_ref["source_id"]]
                evidence_ref = _source_evidence_ref(source, source_ref["locator"])
                source_lineage_refs.add(evidence_ref)
            else:
                evidence_ref = (
                    f"ADMISSION_METHOD:{F02_ADMISSION_METHOD}|OPERATOR:{F02_OPERATOR_ID}|"
                    f"REGISTRY:{FEATURE_INPUT_REGISTRY_REF}|LINEAGE:{','.join(sorted(leaf['input_lineage_refs']))}"
                )
            provenance[dotted] = {
                "evidence_ref": evidence_ref,
                "supported_cutoff_at": leaf["publication_at_or_interval"]["latest_possible_at"],
            }
        consumed_fields = sorted(provenance)
        block["source_lineage_refs"] = sorted(source_lineage_refs)
        block["consumed_fields"] = consumed_fields
        block["consumed_value_provenance"] = provenance
        for leaf in block_leaves:
            if _resolve_pointer(block, leaf["input_path"]) != leaf["value"]:
                raise RealInputReplayError(f"{leaf['record_id']}: pointer/value resolution mismatch")
        row_by_key[key]["feature_raw_inputs"][F02] = block

    validate_strict_w1_mis(rows, code_identity=code_identity)
    return rows, {
        "source_manifest_content_sha256": manifest_content_sha256,
        "semantic_feature_leaf_sha256": semantic_sidecar_sha256,
        "composite_input_sha256": composite_input_sha256,
        "source_count": len(sources),
        "sidecar_leaf_count": len(leaves),
        "observed_numeric_leaf_count": sum(leaf["evidence_kind"] == "OBSERVED" for leaf in leaves),
        "derived_control_leaf_count": sum(leaf["evidence_kind"] == "DERIVED" for leaf in leaves),
        "derived_relative_change_count": len(grouped) * 2,
        "estimated_leaf_count": 0,
        "admitted_feature_block_count": len(grouped),
    }


def validate_strict_w1_mis(records: Iterable[dict[str, Any]], *, code_identity: str) -> list[dict[str, Any]]:
    rows = validate_snapshot_batch(records)
    if len(rows) != EXPECTED_COUNTS["W1"]["ELIGIBLE"]:
        raise RealInputReplayError("W1 scorer batch must retain all 57 INCLUDE rows")
    available_count = 0
    for row in rows:
        if row["code_or_executable_identity"] != code_identity:
            raise RealInputReplayError("successor executable identity mismatch")
        if row["window_anchor_date"] != W1_MAPPING["window_anchor_date"]:
            raise RealInputReplayError("WM-v1.1 window anchor mismatch")
        blocks = row.get("feature_raw_inputs")
        if not isinstance(blocks, dict) or set(blocks) != set(FEATURE_IDS):
            raise RealInputReplayError(f"{row['company_id']}: exact F01-F09 blocks required")
        for feature_id, block in blocks.items():
            if block.get("availability_state") == "NOT_FOUND":
                if set(block) != {"availability_state", "missing_reason", "missing_evidence_ref"}:
                    raise RealInputReplayError(f"{row['company_id']}/{feature_id}: malformed missing block")
                if block["missing_reason"] != MISSING_FEATURE_REASON:
                    raise RealInputReplayError(f"{row['company_id']}/{feature_id}: missing reason mismatch")
                continue
            available_count += 1
            if feature_id != F02 or set(block) != {
                "availability_state",
                "metric_pairs",
                "source_lineage_refs",
                "consumed_fields",
                "consumed_value_provenance",
            }:
                raise RealInputReplayError(f"{row['company_id']}/{feature_id}: unapproved model-input block")
            if block["availability_state"] != "AVAILABLE" or set(block["metric_pairs"]) != {"operating_profit", "revenue"}:
                raise RealInputReplayError(f"{row['company_id']}/{feature_id}: incomplete F02 block")
            for metric, pair in block["metric_pairs"].items():
                if set(pair) != {"current", "prior", "change_mode", "operator_id"}:
                    raise RealInputReplayError(f"{row['company_id']}/{feature_id}/{metric}: incomplete pair")
                _canonical_decimal(pair["current"], f"{metric}.current")
                if _canonical_decimal(pair["prior"], f"{metric}.prior") == 0:
                    raise RealInputReplayError(f"{metric}: RELATIVE prior cannot be zero")
                if pair["change_mode"] != "RELATIVE" or pair["operator_id"] != F02_OPERATOR_ID:
                    raise RealInputReplayError(f"{metric}: operator mismatch")
            expected_consumed = sorted(
                _pointer_to_dotted(path) for path in F02_LEAF_SPECS
            )
            if block["consumed_fields"] != expected_consumed or set(block["consumed_value_provenance"]) != set(expected_consumed):
                raise RealInputReplayError(f"{row['company_id']}/{feature_id}: consumed provenance mismatch")
            for path in F02_LEAF_SPECS:
                _resolve_pointer(block, path)
        assert_no_outcome_fields(row)
        validate_consumed_value_provenance(row)
        validate_f08_freshness_provenance(row)
    if available_count == 0:
        raise RealInputReplayError("Strict successor cannot execute an empty sidecar")
    return rows


def execute_strict_w1_model_stage(
    population_rows: Iterable[dict[str, Any]],
    *,
    pmo_run_id: str,
    manifest: dict[str, Any],
    manifest_content_sha256: str,
    leaf_records: Iterable[dict[str, Any]],
    repo: str | Path,
    config_path: str | Path,
    code_identity: str,
) -> dict[str, Any]:
    population = validate_population(population_rows)
    mis, input_custody = build_strict_w1_mis(
        population,
        pmo_run_id=pmo_run_id,
        manifest=manifest,
        manifest_content_sha256=manifest_content_sha256,
        leaf_records=leaf_records,
        repo=repo,
        code_identity=code_identity,
    )
    engine = build_engine(code_identity=code_identity, config_path=config_path)
    scored = engine.score_snapshot(mis)
    if scored["eligible_count"] != EXPECTED_COUNTS["W1"]["ELIGIBLE"]:
        raise RealInputReplayError("scorer did not receive the complete W1 INCLUDE batch")
    if scored["rankable_count"] <= 0:
        raise RealInputReplayError("real-input objective failed: scorer still produced zero scores")

    source_by_company = {
        row["company_id"]: row for row in population if row["window_id"] == "W1"
    }
    output_by_company = {row["company_id"]: row for row in scored["outputs"]}
    expected_output_ids = {
        row["company_id"]
        for row in source_by_company.values()
        if row["historical_eligibility_status"] == "ELIGIBLE"
    }
    if set(output_by_company) != expected_output_ids:
        raise RealInputReplayError("scorer output does not match the frozen 57-row INCLUDE set")

    partitions: Counter[str] = Counter()
    feature_states: Counter[str] = Counter()
    ledger: list[dict[str, Any]] = []
    for company_id in sorted(source_by_company):
        source = source_by_company[company_id]
        source_state = source["historical_eligibility_status"]
        output = output_by_company.get(company_id)
        if output is None:
            partition = (
                "EXCLUDE_PROVEN"
                if source_state == "INELIGIBLE_BY_TRADABILITY"
                else "EXCLUDE_UNRESOLVED"
            )
            partitions[partition] += 1
            ledger.append(
                {
                    "pmo_run_id": pmo_run_id,
                    "window_id": "W1",
                    "row_key": source["row_key"],
                    "company_id": company_id,
                    "krx_code": source["krx_code"],
                    "source_eligibility_state": source_state,
                    "outer_partition": partition,
                    "score_status": "NOT_SENT_TO_SCORER_OUTER_EXCLUSION",
                    "feature_coverage_ratio": None,
                    "final_score": None,
                    "scorer_partial_exact_rank": None,
                    "official_rank": None,
                    "model_score_id": None,
                    "official_selection_flag": False,
                    "outcome_measurement_cohort_flag": False,
                    "result_measurement_state": "NOT_APPLICABLE_OUTER_EXCLUSION",
                }
            )
            continue

        for feature in output.get("feature_trace", {}).values():
            feature_states[str(feature.get("availability_state"))] += 1
        is_scored = output["final_score"] is not None
        partition = "INCLUDE_SCORED" if is_scored else "REPLAY_DATA_INSUFFICIENT"
        partitions[partition] += 1
        model_score_id = None
        if is_scored:
            model_score_id = "m3score_" + sha256_hex(
                {
                    "engine_run_id": output["run_id"],
                    "snapshot_id": output["snapshot_id"],
                    "company_id": output["company_id"],
                    "scored_payload": output,
                }
            )
        ledger.append(
            {
                "pmo_run_id": pmo_run_id,
                "window_id": "W1",
                "row_key": source["row_key"],
                "company_id": company_id,
                "krx_code": source["krx_code"],
                "source_eligibility_state": source_state,
                "outer_partition": partition,
                "score_status": output["score_status"],
                "feature_coverage_ratio": output["feature_coverage_ratio"],
                "final_score": output["final_score"],
                "scorer_partial_exact_rank": output["exact_rank"],
                "official_rank": None,
                "model_score_id": model_score_id,
                "official_selection_flag": False,
                "outcome_measurement_cohort_flag": is_scored,
                "result_measurement_state": (
                    "PENDING_OUTCOME_AFTER_DURABLE_SEAL"
                    if is_scored
                    else "NOT_MEASURED_MODEL_SCORE_UNAVAILABLE"
                ),
            }
        )

    expected_partitions = {
        "INCLUDE_SCORED": scored["rankable_count"],
        "REPLAY_DATA_INSUFFICIENT": EXPECTED_COUNTS["W1"]["ELIGIBLE"] - scored["rankable_count"],
        "EXCLUDE_PROVEN": EXPECTED_COUNTS["W1"]["INELIGIBLE_BY_TRADABILITY"],
        "EXCLUDE_UNRESOLVED": EXPECTED_COUNTS["W1"]["UNRESOLVED"],
    }
    observed_partitions = {name: partitions[name] for name in expected_partitions}
    if observed_partitions != expected_partitions:
        raise RealInputReplayError(
            f"W1 outer partition mismatch: {observed_partitions} != {expected_partitions}"
        )
    scored_rows = sorted(
        (row for row in scored["outputs"] if row["final_score"] is not None),
        key=lambda row: int(row["exact_rank"]),
    )
    return {
        "pmo_run_id": pmo_run_id,
        "mode": "STRICT",
        "runner_version": RUNNER_VERSION,
        "claim_class": "COVERAGE_LIMITED_REAL_INPUT_STRICT_REPLAY",
        "model_stage_state": "COMPLETED_NONEMPTY_STRICT_SCORE",
        "stage_sequence": [
            "POPULATION_BOUND",
            "SOURCE_CUSTODY_VERIFIED",
            "STRICT_FEATURE_LEAVES_ADMITTED",
            "CONSUMED_POINTERS_AND_PROVENANCE_VERIFIED",
            "W1_COMPLETE_INCLUDE_BATCH_SCORED",
        ],
        "successor_executable_bundle_identity": code_identity,
        "preserved_predecessor_bundle_identity": PREDECESSOR_EXECUTABLE_BUNDLE_IDENTITY,
        "config_hash": engine.config_hash,
        "source_population": {
            "revision": POPULATION_REVISION,
            "path": POPULATION_PATH,
            "git_blob": POPULATION_GIT_BLOB,
            "compressed_sha256": POPULATION_SHA256,
            "row_count": POPULATION_ROW_COUNT,
            "authority": "QUEUE_ONLY_WITH_EXPLICIT_SUCCESSOR_LEAF_OVERLAY",
        },
        "input_custody": input_custody,
        "strict_value_classification": {
            "observed_numeric_leaf_count": input_custody["observed_numeric_leaf_count"],
            "derived_control_leaf_count": input_custody["derived_control_leaf_count"],
            "calculated_relative_change_count": input_custody["derived_relative_change_count"],
            "estimated_leaf_count": 0,
            "unverified_or_missing_feature_block_count": (
                EXPECTED_COUNTS["W1"]["ELIGIBLE"] * len(FEATURE_IDS)
                - input_custody["admitted_feature_block_count"]
            ),
        },
        "window": {
            **W1_MAPPING,
            "u127_count": 127,
            "replay_include_eligibility_count": EXPECTED_COUNTS["W1"]["ELIGIBLE"],
            "exclude_proven_count": EXPECTED_COUNTS["W1"]["INELIGIBLE_BY_TRADABILITY"],
            "exclude_unresolved_count": EXPECTED_COUNTS["W1"]["UNRESOLVED"],
            "scoreable_count": scored["rankable_count"],
            "replay_data_insufficient_count": expected_partitions["REPLAY_DATA_INSUFFICIENT"],
            "scorer_include_batch_count": scored["eligible_count"],
            "scorer_coverage": scored["scorable_eligible_coverage"],
            "ranking_status": scored["ranking_status"],
            "outer_partitions": observed_partitions,
            "feature_availability_states": dict(sorted(feature_states.items())),
            "coverage_limited_order": [
                {
                    "company_id": row["company_id"],
                    "partial_rank": row["exact_rank"],
                    "final_score": row["final_score"],
                    "score_status": row["score_status"],
                    "warning_flags": row["warning_flags"],
                }
                for row in scored_rows
            ],
            "official_top3_state": "NOT_AVAILABLE_INCOMPLETE_57_ROW_SCORE_COVERAGE",
            "outcome_measurement_cohort_policy": "ALL_SCOREABLE_PRECOMMITTED_NO_SUBSTITUTION",
        },
        "model_input_batch": mis,
        "scorer_output": scored,
        "selection_ledger": ledger,
        "outcome_firewall": {
            "future_price_values_loaded_before_model_selection": False,
            "future_outcome_fields_present_in_model_inputs": False,
            "price_stage_may_begin_after": "DURABLE_SELECTION_SEAL_COMMIT_AND_READBACK",
        },
        "claim_ceiling": [
            "NO_OFFICIAL_TOP3_OR_TOP10_CLAIM",
            "NO_COMPLETE_W1_INPUT_COVERAGE_CLAIM",
            "NO_CLEAN_HOLDOUT_OR_OOS_CLAIM",
            "NO_MODEL_QUALITY_OR_PRODUCTION_READINESS_CLAIM",
        ],
    }


def _seal_payload(model_stage: dict[str, Any]) -> dict[str, Any]:
    include_results = [
        {
            "company_id": row["company_id"],
            "krx_code": row["krx_code"],
            "outer_partition": row["outer_partition"],
            "score_status": row["score_status"],
            "feature_coverage_ratio": row["feature_coverage_ratio"],
            "final_score": row["final_score"],
            "scorer_partial_exact_rank": row["scorer_partial_exact_rank"],
            "model_score_id": row["model_score_id"],
            "outcome_measurement_cohort_flag": row["outcome_measurement_cohort_flag"],
        }
        for row in model_stage["selection_ledger"]
        if row["source_eligibility_state"] == "ELIGIBLE"
    ]
    measurement_cohort = [
        {
            "company_id": row["company_id"],
            "krx_code": row["krx_code"],
            "model_score_id": row["model_score_id"],
            "final_score": row["final_score"],
            "scorer_partial_exact_rank": row["scorer_partial_exact_rank"],
        }
        for row in include_results
        if row["outcome_measurement_cohort_flag"]
    ]
    return {
        "pmo_run_id": model_stage["pmo_run_id"],
        "mode": model_stage["mode"],
        "successor_executable_bundle_identity": model_stage["successor_executable_bundle_identity"],
        "preserved_predecessor_bundle_identity": model_stage["preserved_predecessor_bundle_identity"],
        "config_hash": model_stage["config_hash"],
        "source_manifest_content_sha256": model_stage["input_custody"]["source_manifest_content_sha256"],
        "semantic_feature_leaf_sha256": model_stage["input_custody"]["semantic_feature_leaf_sha256"],
        "composite_input_sha256": model_stage["input_custody"]["composite_input_sha256"],
        "model_input_batch_hash": model_stage["scorer_output"]["input_hash"],
        "scorer_output_hash": sha256_hex(model_stage["scorer_output"]),
        "selection_ledger_hash": sha256_hex(model_stage["selection_ledger"]),
        "engine_run_id": model_stage["scorer_output"]["run_id"],
        "window_mapping": model_stage["window"],
        "replay_calendar_binding": copy.deepcopy(W1_REPLAY_CALENDAR_BINDING),
        "outcome_runtime_policy": copy.deepcopy(OUTCOME_RUNTIME_POLICY),
        "outer_127_accounting": model_stage["window"]["outer_partitions"],
        "ranking_status": model_stage["window"]["ranking_status"],
        "rankable_count": model_stage["window"]["scoreable_count"],
        "coverage": model_stage["window"]["scorer_coverage"],
        "rank_tie_policy": "FULL_PRECISION_SCORE_DESC_COMPANY_ID_ASC",
        "official_top3_state": "NOT_AVAILABLE_INCOMPLETE_57_ROW_SCORE_COVERAGE",
        "include_57_results": include_results,
        "outcome_measurement_cohort_policy": "ALL_SCOREABLE_PRECOMMITTED_NO_SUBSTITUTION",
        "outcome_measurement_cohort": measurement_cohort,
        "selected_company_substitution_policy": "FORBIDDEN",
    }


def create_selection_seal(model_stage: dict[str, Any], *, sealed_at_kst: str) -> dict[str, Any]:
    if model_stage.get("model_stage_state") != "COMPLETED_NONEMPTY_STRICT_SCORE":
        raise RealInputReplayError("nonempty completed model stage required before sealing")
    parse_datetime(sealed_at_kst)
    payload = _seal_payload(model_stage)
    if len(payload["include_57_results"]) != 57 or not payload["outcome_measurement_cohort"]:
        raise RealInputReplayError("selection seal requires the full W1 denominator and nonempty measurement cohort")
    digest = sha256_hex(payload)
    return {
        "schema_version": "M3TOP3-DURABLE-SELECTION-SEAL-v1.0",
        "sealed_at_kst": sealed_at_kst,
        "seal_content_sha256": digest,
        "seal_id": f"m3selection_{digest[:32]}",
        "sealed_payload": payload,
        "future_price_values_opened_at_seal": False,
    }


def validate_selection_seal(seal: dict[str, Any]) -> dict[str, Any]:
    _assert_exact_keys(
        seal,
        {
            "schema_version",
            "sealed_at_kst",
            "seal_content_sha256",
            "seal_id",
            "sealed_payload",
            "future_price_values_opened_at_seal",
        },
        "selection seal",
    )
    if seal["schema_version"] != "M3TOP3-DURABLE-SELECTION-SEAL-v1.0":
        raise RealInputReplayError("selection seal schema mismatch")
    parse_datetime(seal["sealed_at_kst"])
    expected = sha256_hex(seal["sealed_payload"])
    if seal["seal_content_sha256"] != expected or seal["seal_id"] != f"m3selection_{expected[:32]}":
        raise RealInputReplayError("selection seal content identity mismatch")
    if seal["future_price_values_opened_at_seal"] is not False:
        raise RealInputReplayError("selection seal does not assert an unopened outcome boundary")
    payload = seal["sealed_payload"]
    mapping = payload.get("window_mapping", {})
    if (
        payload.get("mode") != "STRICT"
        or len(payload.get("include_57_results", [])) != 57
        or not payload.get("outcome_measurement_cohort")
        or payload.get("outcome_measurement_cohort_policy")
        != "ALL_SCOREABLE_PRECOMMITTED_NO_SUBSTITUTION"
        or payload.get("selected_company_substitution_policy") != "FORBIDDEN"
        or any(mapping.get(key) != value for key, value in W1_MAPPING.items())
        or payload.get("replay_calendar_binding") != W1_REPLAY_CALENDAR_BINDING
        or payload.get("outcome_runtime_policy") != OUTCOME_RUNTIME_POLICY
        or not str(payload.get("successor_executable_bundle_identity", "")).startswith(
            "M3TOP3-REAL-INPUT-EXECUTABLE-BUNDLE-SHA256:"
        )
        or payload.get("successor_executable_bundle_identity") == PREDECESSOR_EXECUTABLE_BUNDLE_IDENTITY
    ):
        raise RealInputReplayError("selection seal semantic invariant mismatch")
    return seal


def commit_selection_seal(path: str | Path, seal: dict[str, Any]) -> dict[str, Any]:
    validate_selection_seal(seal)
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = canonical_json_bytes(seal) + b"\n"
    try:
        descriptor = os.open(
            target,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0),
            0o644,
        )
    except FileExistsError:
        if target.read_bytes() != payload:
            raise RealInputReplayError("existing selection seal differs; overwrite is forbidden")
    else:
        try:
            offset = 0
            while offset < len(payload):
                offset += os.write(descriptor, payload[offset:])
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
    readback = read_selection_seal(target)
    if target.read_bytes() != payload or canonical_json_bytes(readback) + b"\n" != payload:
        raise RealInputReplayError("selection seal durable readback mismatch")
    return readback


def read_selection_seal(path: str | Path) -> dict[str, Any]:
    try:
        payload = Path(path).read_bytes()
        seal = _strict_json_loads(payload.decode("utf-8"), "selection seal")
    except (OSError, UnicodeDecodeError) as exc:
        raise RealInputReplayError("selection seal is not readable UTF-8") from exc
    if not isinstance(seal, dict):
        raise RealInputReplayError("selection seal must be a JSON object")
    return validate_selection_seal(seal)


def _read_durable_selection_seal_receipt(path: str | Path) -> dict[str, Any]:
    target = Path(path).resolve()
    try:
        raw = target.read_bytes()
        seal = _strict_json_loads(raw.decode("utf-8"), "durable selection seal")
    except (OSError, UnicodeDecodeError) as exc:
        raise RealInputReplayError("durable selection seal is not readable UTF-8") from exc
    if not isinstance(seal, dict):
        raise RealInputReplayError("durable selection seal must be a JSON object")
    validated = validate_selection_seal(seal)
    if raw != canonical_json_bytes(validated) + b"\n":
        raise RealInputReplayError("durable selection seal is not the exact canonical committed byte form")
    return {
        "receipt_type": "DURABLE_SELECTION_SEAL_CANONICAL_READBACK",
        "selection_seal": validated,
        "selection_seal_id": validated["seal_id"],
        "path": str(target),
        "byte_size": len(raw),
        "file_sha256": hashlib.sha256(raw).hexdigest(),
    }


PRICE_COMPONENT_BINDINGS = {
    "2024": {
        "name": "marcap-2024.parquet",
        "byte_size": 24_572_111,
        "sha256": "b0c38943e67637d5faf88429880092cf0f46a394be39860dd3bcd0b04231bccb",
    },
    "2025": {
        "name": "marcap-2025.parquet",
        "byte_size": 25_153_419,
        "sha256": "2bfd93c217eb74263bc5020b23fa6debb6b02531c11eaccc2826639bc191559e",
    },
    "2026": {
        "name": "marcap-2026.parquet",
        "byte_size": 16_198_533,
        "sha256": "5da710a2fc56f8fe9b1f5126295cc30c3b15c0ee35d28ba808a505ec4a2243c1",
    },
}
PRICE_DATASET_IDENTITY_SHA256 = "419893f0dc8c08019a746182135630cc5f94d6e7ebc2874d5bd23cb54c0a72f7"


def _verify_distribution_record_entries(
    distribution_root: Path,
    record_bytes: bytes,
    *,
    unhashed_existing_allowlist: set[str],
) -> dict[str, int]:
    verified_entries = 0
    allowed_unhashed_existing = 0
    declared_unhashed_absent = 0
    seen_allowlist: set[str] = set()
    try:
        rows = csv.reader(record_bytes.decode("utf-8").splitlines())
        for index, row in enumerate(rows, start=1):
            if len(row) != 3:
                raise RealInputReplayError(f"PyArrow RECORD row {index}: exact three fields required")
            relative, recorded_hash, recorded_size = row
            candidate = (distribution_root / Path(relative)).resolve()
            try:
                candidate.relative_to(distribution_root)
            except ValueError as exc:
                raise RealInputReplayError(f"PyArrow RECORD row {index}: path escapes distribution root") from exc
            if not recorded_hash and not recorded_size:
                if relative in unhashed_existing_allowlist:
                    if not candidate.is_file():
                        raise RealInputReplayError(f"PyArrow RECORD row {index}: allowlisted file is missing")
                    seen_allowlist.add(relative)
                    allowed_unhashed_existing += 1
                elif candidate.exists():
                    raise RealInputReplayError(
                        f"PyArrow RECORD row {index}: unhashed executable/cache bytes are present"
                    )
                else:
                    declared_unhashed_absent += 1
                continue
            if not recorded_hash.startswith("sha256=") or not recorded_size.isdigit():
                raise RealInputReplayError(f"PyArrow RECORD row {index}: unsupported identity format")
            try:
                data = candidate.read_bytes()
            except OSError as exc:
                raise RealInputReplayError(f"PyArrow RECORD row {index}: bound file unreadable") from exc
            encoded = base64.urlsafe_b64encode(hashlib.sha256(data).digest()).rstrip(b"=").decode("ascii")
            if len(data) != int(recorded_size) or recorded_hash != f"sha256={encoded}":
                raise RealInputReplayError(f"PyArrow RECORD row {index}: installed file identity mismatch")
            verified_entries += 1
    except UnicodeDecodeError as exc:
        raise RealInputReplayError("PyArrow RECORD is not UTF-8") from exc
    if seen_allowlist != unhashed_existing_allowlist:
        raise RealInputReplayError("PyArrow RECORD unhashed allowlist is not represented exactly")
    if verified_entries <= 0:
        raise RealInputReplayError("PyArrow RECORD verified no installed files")
    return {
        "record_hashed_entries_verified": verified_entries,
        "record_unhashed_existing_allowlisted": allowed_unhashed_existing,
        "record_unhashed_declared_absent": declared_unhashed_absent,
    }


def _verify_outcome_runtime_before_price_access(policy: dict[str, Any]) -> dict[str, Any]:
    if policy != OUTCOME_RUNTIME_POLICY:
        raise RealInputReplayError("sealed outcome runtime policy is not the reviewed exact policy")
    expected_python = policy["python"]
    executable = Path(sys.executable).resolve()
    executable_identity = {
        "byte_size": executable.stat().st_size,
        "sha256": _file_sha256(executable),
    }
    if (
        platform.python_implementation() != expected_python["implementation"]
        or platform.python_version() != expected_python["version"]
        or executable.name.lower() != expected_python["executable_name"]
        or executable_identity
        != {"byte_size": expected_python["byte_size"], "sha256": expected_python["sha256"]}
    ):
        raise RealInputReplayError("Python runtime does not match the sealed outcome runtime policy")

    expected_reader = policy["parquet_reader"]
    if (
        sys.dont_write_bytecode is not expected_reader["require_dont_write_bytecode"]
        or sys.pycache_prefix is not expected_reader["require_pycache_prefix"]
    ):
        raise RealInputReplayError("outcome process must disable bytecode writes and use no external cache prefix")
    if any(name == "pyarrow" or name.startswith("pyarrow.") for name in sys.modules):
        raise RealInputReplayError("PyArrow was imported before exact distribution verification")

    candidate_roots: set[Path] = set()
    for raw_root in sys.path:
        try:
            root = Path(raw_root or os.getcwd()).resolve()
        except (OSError, TypeError):
            continue
        module_init = root / "pyarrow" / "__init__.py"
        record = root / expected_reader["dist_info_directory"] / "RECORD"
        if module_init.is_file() and record.is_file():
            candidate_roots.add(root)
    if len(candidate_roots) != 1:
        raise RealInputReplayError(
            f"exactly one unimported bound PyArrow distribution required; found {len(candidate_roots)}"
        )
    distribution_root = next(iter(candidate_roots))
    expected_module_file = (distribution_root / "pyarrow" / "__init__.py").resolve()
    dist_info = distribution_root / expected_reader["dist_info_directory"]
    record_path = dist_info / "RECORD"
    record_bytes = record_path.read_bytes()
    if {
        "byte_size": len(record_bytes),
        "sha256": hashlib.sha256(record_bytes).hexdigest(),
    } != {
        "byte_size": expected_reader["record_byte_size"],
        "sha256": expected_reader["record_sha256"],
    }:
        raise RealInputReplayError("PyArrow distribution RECORD identity mismatch")
    record_verification = _verify_distribution_record_entries(
        distribution_root,
        record_bytes,
        unhashed_existing_allowlist=set(expected_reader["unhashed_existing_allowlist"]),
    )
    try:
        import pyarrow  # type: ignore[import-not-found]
    except ImportError as exc:
        raise RealInputReplayError("PYARROW_RUNTIME_UNAVAILABLE_AFTER_EXACT_FILE_VERIFICATION") from exc
    if (
        getattr(pyarrow, "__version__", None) != expected_reader["version"]
        or not pyarrow.__file__
        or Path(pyarrow.__file__).resolve() != expected_module_file
    ):
        raise RealInputReplayError("PyArrow import does not resolve to the preverified exact distribution")
    module_file = Path(pyarrow.__file__).resolve()
    return {
        "binding_state": "SEALED_RUNTIME_AND_ALL_EXECUTABLE_DISTRIBUTION_BYTES_VERIFIED_BEFORE_IMPORT_AND_PRICE_ACCESS",
        "runtime_policy_sha256": sha256_hex(policy),
        "python": {
            "executable": str(executable),
            "version": sys.version,
            **executable_identity,
        },
        "parquet_reader": {
            "distribution": expected_reader["distribution"],
            "version": pyarrow.__version__,
            "module_file": str(module_file),
            "distribution_root": str(distribution_root),
            "record_path": str(record_path),
            "record_byte_size": len(record_bytes),
            "record_sha256": hashlib.sha256(record_bytes).hexdigest(),
            **record_verification,
        },
    }


def _bind_price_components_after_seal(paths: dict[str, Path]) -> tuple[dict[str, Any], bytes]:
    if set(paths) != set(PRICE_COMPONENT_BINDINGS):
        raise RealInputReplayError("exact 2024-2026 price component paths required")
    components = []
    captured_2024: bytes | None = None
    for year in sorted(PRICE_COMPONENT_BINDINGS):
        expected = PRICE_COMPONENT_BINDINGS[year]
        path = paths[year]
        if not path.is_file():
            raise RealInputReplayError(f"{year} bound price component is missing")
        if year == "2024":
            captured_2024 = path.read_bytes()
            observed = {
                "byte_size": len(captured_2024),
                "sha256": hashlib.sha256(captured_2024).hexdigest(),
            }
        else:
            observed = {"byte_size": path.stat().st_size, "sha256": _file_sha256(path)}
        if observed != {"byte_size": expected["byte_size"], "sha256": expected["sha256"]}:
            raise RealInputReplayError(f"{year} price component identity mismatch")
        components.append({"year": year, "path": str(path), **observed, "name": expected["name"]})
    if captured_2024 is None:
        raise RealInputReplayError("2024 price component was not captured")
    return (
        {
            "binding_state": "EXACT_COMPONENT_BYTES_VERIFIED_AFTER_DURABLE_SELECTION_SEAL",
            "dataset_identity_sha256": PRICE_DATASET_IDENTITY_SHA256,
            "source_semantics": "RAW_IMMUTABLE_NOT_PRICE_CANONICAL",
            "decoded_component_year": "2024",
            "decoded_component_transport": "IN_MEMORY_EXACT_HASHED_BYTE_BUFFER_NO_PATH_REOPEN",
            "components": components,
        },
        captured_2024,
    )


def _normalize_marcap_rows_after_seal(payload: bytes) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    try:
        import pyarrow  # type: ignore[import-not-found]
        import pyarrow.parquet as parquet  # type: ignore[import-not-found]
    except ImportError as exc:
        raise RealInputReplayError(
            "PYARROW_RUNTIME_UNAVAILABLE_AFTER_PRECHECK"
        ) from exc
    try:
        table = parquet.read_table(
            pyarrow.BufferReader(payload),
            columns=["Date", "Code", "Open", "High", "Low", "Close"],
        )
    except Exception as exc:
        raise RealInputReplayError("bound 2024 price component could not be read with the expected schema") from exc
    normalized: list[dict[str, Any]] = []
    for index, row in enumerate(table.to_pylist()):
        code = row["Code"]
        if not isinstance(code, str) or len(code) != 6 or not code.isalnum() or code != code.upper():
            raise RealInputReplayError(f"marcap row {index}: exact six-character Code required")
        day = row["Date"]
        if hasattr(day, "date") and not isinstance(day, str):
            day = day.date() if hasattr(day, "hour") else day
        normalized.append(
            {
                "date": parse_date(day).isoformat(),
                "krx_code": code,
                "open": row["Open"],
                "high": row["High"],
                "low": row["Low"],
                "close": row["Close"],
            }
        )
    return normalized, {
        "package": "pyarrow",
        "version": pyarrow.__version__,
        "read_columns": ["Date", "Code", "Open", "High", "Low", "Close"],
        "source_row_count": table.num_rows,
        "source_schema": str(table.schema),
        "decoded_buffer_byte_size": len(payload),
        "decoded_buffer_sha256": hashlib.sha256(payload).hexdigest(),
    }


def _positive_price(value: Any, context: str) -> Decimal:
    if isinstance(value, bool):
        raise RealInputReplayError(f"{context}: boolean is not a price")
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise RealInputReplayError(f"{context}: finite positive price required") from exc
    if not result.is_finite() or result <= 0:
        raise RealInputReplayError(f"{context}: finite positive price required")
    return result


def _valid_ohlc(row: dict[str, Any], context: str) -> dict[str, Decimal]:
    opened = _positive_price(row["open"], f"{context}/open")
    high = _positive_price(row["high"], f"{context}/high")
    low = _positive_price(row["low"], f"{context}/low")
    close = _positive_price(row["close"], f"{context}/close")
    if high < max(opened, close, low) or low > min(opened, close, high):
        raise RealInputReplayError(f"{context}: invalid OHLC ordering")
    return {"open": opened, "high": high, "low": low, "close": close}


def _calculate_w1_raw_outcomes_from_normalized_rows(
    verified_seal: dict[str, Any],
    price_rows: Iterable[dict[str, Any]],
    *,
    price_binding: dict[str, Any],
    durable_readback_receipt: dict[str, Any] | None,
) -> dict[str, Any]:
    """Shared arithmetic; only the private receipt-bearing path may emit firewall proof."""
    seal = validate_selection_seal(verified_seal)
    payload = seal["sealed_payload"]
    include_results = payload["include_57_results"]
    comparison = {row["company_id"]: row["krx_code"] for row in include_results}
    if len(comparison) != 57 or len(set(comparison.values())) != 57:
        raise RealInputReplayError("sealed W1 INCLUDE denominator is not exactly 57 unique companies/codes")
    measurement_ids = {row["company_id"] for row in payload["outcome_measurement_cohort"]}
    if not measurement_ids.issubset(comparison):
        raise RealInputReplayError("measurement cohort escapes sealed INCLUDE denominator")

    mapping = payload["window_mapping"]
    entry_date = parse_date(mapping["entry_trade_date"])
    evaluation_last = parse_date(mapping["evaluation_last_trade_date"])
    exit_date = parse_date(mapping["exit_trade_date"])
    expected_dates = set(payload["replay_calendar_binding"]["expected_holding_dates"])
    observed_market_dates: set[str] = set()
    observed_dates_through_exit: set[str] = set()
    by_key: dict[tuple[str, str], dict[str, Any]] = {}
    comparison_codes = set(comparison.values())
    for index, row in enumerate(price_rows):
        if not isinstance(row, dict) or set(row) != {"date", "krx_code", "open", "high", "low", "close"}:
            raise RealInputReplayError(f"price row {index}: exact normalized OHLC fields required")
        code = row["krx_code"]
        if not isinstance(code, str) or len(code) != 6 or not code.isalnum() or code != code.upper():
            raise RealInputReplayError(f"price row {index}: malformed KRX code")
        day = parse_date(row["date"])
        day_text = day.isoformat()
        if entry_date <= day <= evaluation_last:
            observed_market_dates.add(day_text)
        if entry_date <= day <= exit_date:
            observed_dates_through_exit.add(day_text)
        if code not in comparison_codes or day < entry_date or day > exit_date:
            continue
        key = (code, day_text)
        if key in by_key:
            raise RealInputReplayError(f"duplicate selected-denominator price key: {key}")
        by_key[key] = {**row, "date": day_text}
    if observed_market_dates != expected_dates or exit_date.isoformat() not in observed_dates_through_exit:
        missing = sorted(expected_dates - observed_market_dates)
        unexpected = sorted(observed_market_dates - expected_dates)
        raise RealInputReplayError(
            "price dataset does not expose the exact bound W1 market date spine: "
            f"missing={missing}, unexpected={unexpected}, exit_present={exit_date.isoformat() in observed_dates_through_exit}"
        )

    outcomes: list[dict[str, Any]] = []
    complete_rows: list[dict[str, Any]] = []
    for company_id, code in sorted(comparison.items()):
        unresolved_dates: list[dict[str, str]] = []
        valid_holding: list[dict[str, Any]] = []
        for day in sorted(expected_dates):
            row = by_key.get((code, day))
            if row is None:
                unresolved_dates.append({"date": day, "reason": "ABSENT_ROW_SUSPENSION_OR_MISSING_UNRESOLVED"})
                continue
            try:
                values = _valid_ohlc(row, f"{company_id}/{day}")
            except RealInputReplayError as exc:
                unresolved_dates.append({"date": day, "reason": "INVALID_RAW_OHLC:" + str(exc)})
                continue
            valid_holding.append({"date": day, **values})

        entry_row = next((row for row in valid_holding if row["date"] == entry_date.isoformat()), None)
        end_row = next((row for row in valid_holding if row["date"] == evaluation_last.isoformat()), None)
        exit_raw = by_key.get((code, exit_date.isoformat()))
        try:
            exit_values = _valid_ohlc(exit_raw, f"{company_id}/{exit_date.isoformat()}") if exit_raw else None
        except RealInputReplayError as exc:
            exit_values = None
            unresolved_dates.append({"date": exit_date.isoformat(), "reason": "INVALID_EXIT_OHLC:" + str(exc)})
        if exit_raw is None:
            unresolved_dates.append({"date": exit_date.isoformat(), "reason": "EXIT_ROW_MISSING_NO_SUBSTITUTION"})

        if entry_row is None or end_row is None or exit_values is None or not valid_holding:
            outcomes.append(
                {
                    "company_id": company_id,
                    "krx_code": code,
                    "measurement_state": "NOT_MEASURED_REQUIRED_ENDPOINT_OR_PATH_INVALID",
                    "unresolved_dates": unresolved_dates,
                    "corporate_action_state": "UNVERIFIED_NOT_ASSUMED_NONE",
                    "w1_include57_raw_unadjusted_mfe_return_rank": None,
                }
            )
            continue

        entry_open = entry_row["open"]
        peak_high = max(row["high"] for row in valid_holding)
        minimum_low = min(row["low"] for row in valid_holding)
        exit_open = exit_values["open"]
        outcome = {
            "company_id": company_id,
            "krx_code": code,
            "measurement_state": (
                "PRELIMINARY_RAW_PRICE_MEASURED_CA_UNVERIFIED"
                if not unresolved_dates
                else "PRELIMINARY_RAW_PRICE_PARTIAL_PATH_UNRESOLVED_DATES"
            ),
            "corporate_action_state": "UNVERIFIED_NOT_ASSUMED_NONE",
            "entry_trade_date": entry_date.isoformat(),
            "entry_open_observed_raw": str(entry_open),
            "mfe_peak_high_observed_raw": str(peak_high),
            "raw_unadjusted_mfe_return_calculated": str(peak_high / entry_open - Decimal("1")),
            "minimum_valid_low_observed_raw": str(minimum_low),
            "mae_return": None,
            "mae_return_state": "UNMEASURED_OPEN_CONTRACT_FORMULA",
            "horizon_close_date": evaluation_last.isoformat(),
            "horizon_close_observed_raw": str(end_row["close"]),
            "raw_unadjusted_horizon_close_return_calculated": str(end_row["close"] / entry_open - Decimal("1")),
            "exit_trade_date": exit_date.isoformat(),
            "exit_open_observed_raw": str(exit_open),
            "raw_unadjusted_exit_open_return_calculated": str(exit_open / entry_open - Decimal("1")),
            "raw_unadjusted_peak_to_exit_giveback_calculated": str((peak_high - exit_open) / entry_open),
            "expected_holding_date_count": len(expected_dates),
            "valid_holding_date_count": len(valid_holding),
            "unresolved_dates": unresolved_dates,
            "w1_include57_raw_unadjusted_mfe_return_rank": None,
            "actual_mfe_exact_rank": None,
            "actual_mfe_exact_rank_state": "UNMEASURED_PRICE_CANONICAL_AND_CA_COMPARABILITY_NOT_VERIFIED",
        }
        outcomes.append(outcome)
        if not unresolved_dates:
            complete_rows.append(outcome)

    complete_raw_denominator = len(complete_rows) == 57
    if complete_raw_denominator:
        ranked = sorted(
            complete_rows,
            key=lambda row: (-Decimal(row["raw_unadjusted_mfe_return_calculated"]), row["company_id"]),
        )
        for rank, row in enumerate(ranked, start=1):
            row["w1_include57_raw_unadjusted_mfe_return_rank"] = rank
            row["w1_include57_raw_rank_state"] = "PRELIMINARY_COMPLETE_RAW_DENOMINATOR_CA_UNVERIFIED"
    else:
        for row in outcomes:
            row["w1_include57_raw_rank_state"] = "NOT_MEASURABLE_INCOMPLETE_RAW_DENOMINATOR"

    selected_outcomes = [row for row in outcomes if row["company_id"] in measurement_ids]
    if len(selected_outcomes) != len(measurement_ids):
        raise RealInputReplayError("sealed measurement cohort lost a company; substitution is forbidden")
    selected_item_measured_count = sum(
        row["measurement_state"].startswith("PRELIMINARY_RAW_PRICE_") for row in selected_outcomes
    )
    result = {
        "pmo_run_id": payload["pmo_run_id"],
        "outcome_stage_state": (
            "PRELIMINARY_RAW_PRICE_MEASURED_CA_UNVERIFIED"
            if selected_item_measured_count
            else "NOT_MEASURED_SELECTED_PRICE_PATH_INVALID_OR_MISSING"
        ),
        "execution_proof_state": (
            "DURABLE_SELECTION_SEAL_AND_EXACT_PRICE_BUFFER_VERIFIED"
            if durable_readback_receipt is not None
            else "IN_MEMORY_ARITHMETIC_ONLY_NO_DURABLE_FIREWALL_PROOF"
        ),
        "stage_sequence": (
            [
                "MODEL_SCORED",
                "SELECTION_SEALED_DURABLE_READBACK_VERIFIED",
                "OUTCOME_EXECUTABLE_AND_RUNTIME_VERIFIED",
                "PRICE_COMPONENT_BYTES_BOUND",
                "PRICE_VALUES_READ_FROM_EXACT_HASHED_BUFFER",
                "RAW_OUTCOMES_CALCULATED",
            ]
            if durable_readback_receipt is not None
            else [
                "MODEL_SCORED",
                "SELECTION_SEAL_CONTENT_VALIDATED_IN_MEMORY_ONLY",
                "PRELOADED_TEST_ROWS_USED",
                "RAW_OUTCOME_ARITHMETIC_CALCULATED_WITHOUT_EXECUTION_PROOF",
            ]
        ),
        "selection_seal_id": seal["seal_id"],
        "durable_selection_seal_readback_receipt": durable_readback_receipt,
        "price_input_binding": price_binding,
        "window_mapping": payload["window_mapping"],
        "sealed_measurement_cohort_count": len(measurement_ids),
        "selected_item_raw_measured_count": selected_item_measured_count,
        "selected_contract_exact_outcome_count": 0,
        "comparison_include_count": 57,
        "comparison_complete_raw_path_count": len(complete_rows),
        "complete_raw_rank_denominator": complete_raw_denominator,
        "selected_outcome_ledger": selected_outcomes,
        "comparison_outcome_ledger": outcomes,
        "metric_states": {
            "MFE_peak_and_raw_unadjusted_return": "CALCULATED_PRELIMINARY_CA_UNVERIFIED",
            "W1_INCLUDE57_raw_unadjusted_MFE_rank": (
                "CALCULATED_PRELIMINARY_CA_UNVERIFIED"
                if complete_raw_denominator
                else "NOT_MEASURABLE_INCOMPLETE_RAW_DENOMINATOR"
            ),
            "official_MFE_exact_rank": "UNMEASURED_PRICE_CANONICAL_AND_CA_COMPARABILITY_NOT_VERIFIED",
            "MAE_path_minimum_low": "OBSERVED_RAW",
            "MAE_return": "UNMEASURED_OPEN_CONTRACT_FORMULA",
            "horizon_close_return": "CALCULATED_RAW_DIAGNOSTIC_CA_UNVERIFIED",
            "exit_open_return": "CALCULATED_RAW_CA_UNVERIFIED_NOT_TOTAL_RETURN",
            "primary_top3_hit": "NOT_APPLICABLE_NO_OFFICIAL_TOP3_AND_NO_OFFICIAL_MFE_RANK",
            "critical_miss": "NOT_APPLICABLE_NO_OFFICIAL_TOP3_AND_NO_OFFICIAL_MFE_RANK",
        },
        "value_classification": {
            "observed": "RAW_OHLC_FROM_EXACT_BOUND_PRICE_COMPONENT",
            "calculated": "FULL_PRECISION_RATIOS_FROM_RAW_OHLC_AND_BOUND_WM_v1.1_DATES",
            "estimated": "NONE",
            "unverified": "CORPORATE_ACTION_COMPARABILITY_PRICE_CANONICAL_AND_OFFICIAL_RANK",
        },
        "outcome_firewall": {
            "selection_seal_readback_verified_before_price_component_access": durable_readback_receipt is not None,
            "measurement_cohort_policy": payload["outcome_measurement_cohort_policy"],
            "selected_company_substitution": False,
            "outcome_used_to_change_model_input_score_or_cohort": False,
        },
        "claim_ceiling": [
            "RAW_UNADJUSTED_PRICE_DIAGNOSTIC_ONLY",
            "NO_TOTAL_RETURN_OR_CA_COMPLETE_CLAIM",
            "NO_OFFICIAL_MFE_RANK_OR_PRIMARY_VALIDATION_METRIC_CLAIM",
            "NO_MODEL_QUALITY_OR_PRODUCTION_READINESS_CLAIM",
        ],
    }
    if durable_readback_receipt is None:
        result["claim_ceiling"].append("NO_OPERATIONAL_OUTCOME_CLAIM_FROM_IN_MEMORY_TEST_HELPER")
    result["outcome_semantic_sha256"] = sha256_hex(result)
    return result


def calculate_w1_raw_outcomes_from_normalized_rows_for_test(
    verified_seal: dict[str, Any],
    price_rows: Iterable[dict[str, Any]],
    *,
    price_binding: dict[str, Any],
) -> dict[str, Any]:
    """Arithmetic-fixture helper; deliberately cannot attest durable seal or price-file ordering."""
    return _calculate_w1_raw_outcomes_from_normalized_rows(
        verified_seal,
        price_rows,
        price_binding=price_binding,
        durable_readback_receipt=None,
    )


def execute_w1_outcomes_from_seal(
    *,
    selection_seal_path: str | Path,
    expected_selection_seal_id: str,
    current_executable_bundle_identity: str,
    price_2024_path: str | Path,
    price_2025_path: str | Path,
    price_2026_path: str | Path,
) -> dict[str, Any]:
    # The first filesystem read is the durable selection seal. Price paths are not
    # stat'ed, hashed, imported or opened until this readback passes.
    durable_receipt = _read_durable_selection_seal_receipt(selection_seal_path)
    verified_seal = durable_receipt["selection_seal"]
    if durable_receipt["selection_seal_id"] != expected_selection_seal_id:
        raise RealInputReplayError("selection seal changed after preflight readback")
    sealed_identity = verified_seal["sealed_payload"]["successor_executable_bundle_identity"]
    if current_executable_bundle_identity != sealed_identity:
        raise RealInputReplayError("current outcome executable bundle does not match the sealed model executable")
    runtime_receipt = _verify_outcome_runtime_before_price_access(
        verified_seal["sealed_payload"]["outcome_runtime_policy"]
    )
    paths = {
        "2024": Path(price_2024_path).resolve(),
        "2025": Path(price_2025_path).resolve(),
        "2026": Path(price_2026_path).resolve(),
    }
    price_binding, captured_2024 = _bind_price_components_after_seal(paths)
    normalized_rows, reader_decode = _normalize_marcap_rows_after_seal(captured_2024)
    price_binding["parquet_reader_runtime"] = {**runtime_receipt, "decode": reader_decode}
    return _calculate_w1_raw_outcomes_from_normalized_rows(
        verified_seal,
        normalized_rows,
        price_binding=price_binding,
        durable_readback_receipt={
            key: value for key, value in durable_receipt.items() if key != "selection_seal"
        },
    )
