"""Create-once canonical JSONL materializer for bounded F05-R1 inputs.

The command verifies the exact cohort and Parquet bytes supplied by the caller,
uses the deterministic upstream builder, and writes no scores or rankings.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from datetime import date
from pathlib import Path
from typing import Any, Sequence

from .f05_r1_market import (
    CONSUMED_SOURCE_FIELDS,
    EXPECTED_PRICE_DATASET_ID,
    EXPECTED_PRICE_PARQUET_SHA256,
    EXPECTED_SOURCE_SEMANTICS,
    EXPECTED_W1_COHORT_ARTIFACT_SHA256,
    W1_CUTOFF_DATE,
    W1_SESSION_DATES,
    F05SourceBinding,
    build_w1_f05_inputs,
)
from .providers import DuckDBParquetPriceProvider


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _expected_sha256(value: str, label: str) -> str:
    normalized = value.lower()
    if re.fullmatch(r"[0-9a-f]{64}", normalized) is None:
        raise ValueError(f"{label} must be a 64-character SHA-256")
    return normalized


def _strict_json_bytes(data: bytes, context: str) -> Any:
    def pairs(values):
        result = {}
        for key, value in values:
            if key in result:
                raise ValueError(f"{context} contains duplicate JSON key: {key}")
            result[key] = value
        return result

    def reject_float(value):
        raise ValueError(f"{context} contains binary-float JSON number: {value}")

    def reject_constant(value):
        raise ValueError(f"{context} contains non-finite JSON constant: {value}")

    try:
        return json.loads(
            data.decode("utf-8"),
            object_pairs_hook=pairs,
            parse_float=reject_float,
            parse_constant=reject_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"{context} is not strict UTF-8 JSON") from exc


def _canonical_json_line(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def _load_bound_cohort(path: Path, expected_sha256: str) -> list[dict[str, Any]]:
    if not path.is_file():
        raise FileNotFoundError(f"cohort JSON does not exist: {path}")
    data = path.read_bytes()
    actual = hashlib.sha256(data).hexdigest()
    if actual != _expected_sha256(expected_sha256, "cohort_sha256"):
        raise ValueError(f"cohort JSON SHA-256 mismatch: expected {expected_sha256}, got {actual}")
    parsed = _strict_json_bytes(data, "cohort JSON")
    if isinstance(parsed, dict):
        members = parsed.get("include_companies")
        binding = parsed.get("w1_binding")
        if not isinstance(binding, dict) or binding.get("snapshot_cutoff_at") != "2024-08-09T23:59:59+09:00":
            raise ValueError("cohort JSON W1 cutoff binding is missing or changed")
    else:
        members = parsed
    if not isinstance(members, list) or not all(isinstance(item, dict) for item in members):
        raise ValueError("cohort JSON must be a member list or contain include_companies")
    return members


def _load_bound_mapping(path: Path, expected_sha256: str, context: str) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"{context} does not exist: {path}")
    data = path.read_bytes()
    actual = hashlib.sha256(data).hexdigest()
    expected = _expected_sha256(expected_sha256, f"{context}_sha256")
    if actual != expected:
        raise ValueError(f"{context} SHA-256 mismatch: expected {expected}, got {actual}")
    parsed = _strict_json_bytes(data, context)
    if not isinstance(parsed, dict):
        raise ValueError(f"{context} must be a JSON object")
    return parsed


def materialize(args: argparse.Namespace) -> dict[str, Any]:
    cohort_path = Path(args.cohort)
    parquet_path = Path(args.parquet)
    output_path = Path(args.output)
    if output_path.exists():
        raise FileExistsError(f"create-once output already exists: {output_path}")
    cohort_sha256 = _expected_sha256(args.cohort_sha256, "cohort_sha256")
    parquet_sha256 = _expected_sha256(args.parquet_sha256, "parquet_sha256")
    if args.dataset_id != EXPECTED_PRICE_DATASET_ID:
        raise ValueError("dataset_id does not match the approved F05-R1 dataset")
    if cohort_sha256 != EXPECTED_W1_COHORT_ARTIFACT_SHA256:
        raise ValueError("cohort_sha256 does not match the frozen R0 cohort artifact")
    if parquet_sha256 != EXPECTED_PRICE_PARQUET_SHA256:
        raise ValueError("parquet_sha256 does not match the approved F05-R1 byte binding")
    if args.source_semantics != EXPECTED_SOURCE_SEMANTICS:
        raise ValueError("source_semantics does not match the approved F05-R1 semantics")
    if not parquet_path.is_file():
        raise FileNotFoundError(f"Parquet does not exist: {parquet_path}")
    actual_parquet_sha256 = _sha256_file(parquet_path)
    if actual_parquet_sha256 != parquet_sha256:
        raise ValueError(
            f"Parquet SHA-256 mismatch: expected {parquet_sha256}, got {actual_parquet_sha256}"
        )
    lookback_start = date.fromisoformat(args.lookback_start)
    if lookback_start != W1_SESSION_DATES[0]:
        raise ValueError("lookback_start must equal the governed W1 first observation date")
    members = _load_bound_cohort(cohort_path, cohort_sha256)
    ca_manifest_path = Path(args.ca_manifest)
    ca_custody_path = Path(args.ca_custody)
    ca_manifest_sha256 = _expected_sha256(args.ca_manifest_sha256, "ca_manifest_sha256")
    ca_custody_sha256 = _expected_sha256(args.ca_custody_sha256, "ca_custody_sha256")
    ca_manifest = _load_bound_mapping(
        ca_manifest_path, ca_manifest_sha256, "CA evidence manifest"
    )
    ca_custody = _load_bound_mapping(
        ca_custody_path, ca_custody_sha256, "CA source custody"
    )
    provider = DuckDBParquetPriceProvider(
        [parquet_path],
        dataset_id=args.dataset_id,
        dataset_hash=parquet_sha256,
        semantics=args.source_semantics,
    )
    required_columns = {field.lower() for field in CONSUMED_SOURCE_FIELDS}
    if not required_columns.issubset(set(provider._cols)):
        missing = sorted(required_columns - set(provider._cols))
        raise ValueError(f"Parquet is missing F05-R1 consumed fields: {missing}")
    if tuple(provider.trading_dates(W1_SESSION_DATES[0], W1_CUTOFF_DATE)) != W1_SESSION_DATES:
        raise ValueError("Parquet trading dates do not match the governed W1 session grid")
    rows_by_code = {
        str(member["krx_code"]): provider.rows(
            str(member["krx_code"]), lookback_start, W1_CUTOFF_DATE
        )
        for member in members
    }
    lineage = (
        f"COHORT_ARTIFACT_SHA256:{cohort_sha256}",
        f"PRICE_DATASET_ID:{args.dataset_id}",
        f"PRICE_PARQUET_SHA256:{parquet_sha256}",
        f"PRICE_SOURCE_SEMANTICS:{args.source_semantics}",
        f"CA_MANIFEST_ARTIFACT_SHA256:{ca_manifest_sha256}",
        f"CA_CUSTODY_ARTIFACT_SHA256:{ca_custody_sha256}",
        *tuple(args.source_lineage_ref or ()),
    )
    records = build_w1_f05_inputs(
        members,
        rows_by_code,
        source_binding=F05SourceBinding(
            dataset_id=args.dataset_id,
            parquet_sha256=parquet_sha256,
            source_semantics=args.source_semantics,
        ),
        ca_evidence_manifest=ca_manifest,
        ca_source_custody=ca_custody,
        ca_custody_root=ca_custody_path.parent,
        source_lineage_refs=lineage,
    )
    records.sort(key=lambda item: item["company_id"])
    payload = b"".join(_canonical_json_line(record) for record in records)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation prevents a validated input object from being silently
    # overwritten by a later invocation.
    with output_path.open("xb") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    return {
        "artifact_kind": "F05_R1_W1_UPSTREAM_INPUT_JSONL",
        "contains_scores": False,
        "row_count": len(records),
        "output_path": str(output_path),
        "byte_size": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "cohort_sha256": cohort_sha256,
        "parquet_sha256": parquet_sha256,
        "ca_manifest_sha256": ca_manifest_sha256,
        "ca_custody_sha256": ca_custody_sha256,
        "cutoff_date": W1_CUTOFF_DATE.isoformat(),
    }


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--cohort", required=True, help="Exact W1 cohort JSON")
    result.add_argument("--cohort-sha256", required=True)
    result.add_argument("--parquet", required=True, help="Bound 2024 price Parquet")
    result.add_argument("--parquet-sha256", required=True)
    result.add_argument("--dataset-id", required=True)
    result.add_argument("--source-semantics", required=True)
    result.add_argument("--ca-manifest", required=True, help="Exact official CA evidence manifest")
    result.add_argument("--ca-manifest-sha256", required=True)
    result.add_argument("--ca-custody", required=True, help="Exact official CA response-byte custody JSON")
    result.add_argument("--ca-custody-sha256", required=True)
    result.add_argument("--source-lineage-ref", action="append", default=[])
    result.add_argument("--lookback-start", default="2024-05-16")
    result.add_argument("--output", required=True, help="New canonical JSONL path")
    return result


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    receipt = materialize(args)
    print(_canonical_json_line(receipt).decode("utf-8"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
