from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterable

from .core import aggregate_hash, canonical_json_bytes, deterministic_id, hash_file, sha256_hex


EXIT_BLOCKED = 2
EXIT_INTEGRITY = 3
EXIT_AUTHORITY = 4
OFFICIAL_EXECUTION_ENABLED = False
PRICE_CANONICAL_VALIDATION_ENABLED = False
ALLOWED_PRICE_SEMANTICS = frozenset({"RAW_IMMUTABLE", "PRICE_CANONICAL"})


class M3Top3AdmissionError(RuntimeError):
    """A classified, fail-closed admission failure.

    ``code`` and ``exit_code`` are part of the runtime contract.  Callers must
    not downgrade a classified failure to a successful or generic exit.
    """

    def __init__(
        self,
        code: str,
        message: str,
        details: dict[str, Any] | None = None,
        exit_code: int = EXIT_BLOCKED,
    ):
        self.code = code
        self.details = details or {}
        self.exit_code = exit_code
        super().__init__(f"{code}: {message}")


@dataclass(frozen=True)
class VerifiedSnapshot:
    manifest: dict[str, Any]
    pit_rows: list[dict[str, Any]]
    model_inputs: list[dict[str, Any]]
    retrieval_audits: list[dict[str, Any]]


def _read_manifest(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise M3Top3AdmissionError(
            "BLOCKED_INPUT_INTEGRITY",
            f"manifest is unreadable: {path}",
            {"path": str(path), "cause": type(exc).__name__},
            EXIT_INTEGRITY,
        ) from exc
    if not isinstance(value, dict):
        raise M3Top3AdmissionError(
            "BLOCKED_INPUT_INTEGRITY",
            "manifest must be a JSON object",
            {"path": str(path)},
            EXIT_INTEGRITY,
        )
    return value


def _read_jsonl(path: Path) -> tuple[bytes, list[dict[str, Any]]]:
    try:
        payload = path.read_bytes()
        text = payload.decode("utf-8")
    except (OSError, UnicodeError) as exc:
        raise M3Top3AdmissionError(
            "BLOCKED_INPUT_INTEGRITY",
            f"JSONL input is unreadable: {path}",
            {"path": str(path), "cause": type(exc).__name__},
            EXIT_INTEGRITY,
        ) from exc
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise M3Top3AdmissionError(
                "BLOCKED_INPUT_INTEGRITY",
                f"malformed JSONL at {path}:{line_number}",
                {"path": str(path), "line": line_number},
                EXIT_INTEGRITY,
            ) from exc
        if not isinstance(row, dict):
            raise M3Top3AdmissionError(
                "BLOCKED_INPUT_INTEGRITY",
                f"JSONL row must be an object at {path}:{line_number}",
                {"path": str(path), "line": line_number},
                EXIT_INTEGRITY,
            )
        rows.append(row)
    return payload, rows


def _retrieval_semantic_failure(message: str, details: dict[str, Any] | None = None) -> None:
    raise M3Top3AdmissionError(
        "RETRIEVAL_AUDIT_SEMANTIC_MISMATCH",
        message,
        details,
        EXIT_INTEGRITY,
    )


def _verify_retrieval_audit_semantics(
    snapshot_dir: Path,
    manifest: dict[str, Any],
    pit_rows: list[dict[str, Any]],
    model_inputs: list[dict[str, Any]],
    retrieval_audits: list[dict[str, Any]],
    allow_staging: bool = False,
) -> None:
    """Revalidate retrieval receipts independently of declared hashes.

    Hash binding detects byte drift.  This check prevents a self-consistent
    rewrite of the audit bytes and every declared aggregate from turning an
    invalid receipt into an admissible snapshot.
    """

    expected_count = len(pit_rows)
    if len(model_inputs) != expected_count or len(retrieval_audits) != expected_count:
        _retrieval_semantic_failure(
            "READY snapshot requires exactly one PIT row, model input, and retrieval receipt per company slice",
            {
                "pit_rows": len(pit_rows),
                "model_inputs": len(model_inputs),
                "retrieval_audits": len(retrieval_audits),
            },
        )

    manifest_cutoff = manifest.get("snapshot_cutoff_at")
    manifest_date = manifest.get("snapshot_date")
    if not isinstance(manifest_cutoff, str) or not manifest_cutoff:
        _retrieval_semantic_failure("manifest snapshot_cutoff_at must be a non-empty string")
    if not isinstance(manifest_date, str) or not manifest_date:
        _retrieval_semantic_failure("manifest snapshot_date must be a non-empty string")
    try:
        parsed_date = date.fromisoformat(manifest_date)
        parsed_cutoff = datetime.fromisoformat(manifest_cutoff)
    except (TypeError, ValueError) as exc:
        _retrieval_semantic_failure("manifest snapshot date/cutoff is invalid", {"cause": type(exc).__name__})
    if parsed_cutoff.tzinfo is None or parsed_cutoff.utcoffset() is None:
        _retrieval_semantic_failure("manifest snapshot cutoff must be timezone-aware")
    if parsed_cutoff.date() != parsed_date:
        _retrieval_semantic_failure(
            "manifest snapshot date and cutoff calendar date differ",
            {"snapshot_date": manifest_date, "snapshot_cutoff_at": manifest_cutoff},
        )
    canonical_directory = snapshot_dir.name == manifest_date
    internal_staging_directory = (
        allow_staging
        and snapshot_dir.name.startswith(f".{manifest_date}.")
        and snapshot_dir.name.endswith(".staging")
    )
    if not canonical_directory and not internal_staging_directory:
        _retrieval_semantic_failure(
            "snapshot directory identity differs from manifest snapshot_date",
            {"directory": snapshot_dir.name, "snapshot_date": manifest_date},
        )

    def row_keys(rows: list[dict[str, Any]], artifact: str) -> set[tuple[str, str, str, str]]:
        keys: list[tuple[str, str, str, str]] = []
        for index, row in enumerate(rows):
            company_id = row.get("company_id")
            cutoff_at = row.get("snapshot_cutoff_at")
            snapshot_date = row.get("snapshot_date")
            pit_snapshot_id = row.get("pit_snapshot_id")
            if (
                not isinstance(company_id, str)
                or not company_id
                or not isinstance(cutoff_at, str)
                or cutoff_at != manifest_cutoff
                or snapshot_date != manifest_date
                or not isinstance(pit_snapshot_id, str)
                or not pit_snapshot_id
            ):
                _retrieval_semantic_failure(
                    f"{artifact} company/date/cutoff/PIT identity is invalid",
                    {
                        "artifact": artifact,
                        "row_index": index,
                        "company_id": company_id,
                        "snapshot_date": snapshot_date,
                        "cutoff_at": cutoff_at,
                        "pit_snapshot_id": pit_snapshot_id,
                    },
                )
            keys.append((company_id, snapshot_date, cutoff_at, pit_snapshot_id))
        if len(set(keys)) != len(keys):
            _retrieval_semantic_failure(f"{artifact} contains a duplicate company/date/cutoff/PIT slice", {"artifact": artifact})
        return set(keys)

    pit_keys = row_keys(pit_rows, "pit_snapshot.jsonl")
    model_keys = row_keys(model_inputs, "model_input.jsonl")
    if pit_keys != model_keys:
        _retrieval_semantic_failure(
            "PIT and model-input company/date/cutoff/PIT identities differ",
            {"pit_keys": sorted(pit_keys), "model_keys": sorted(model_keys)},
        )

    pit_by_company: dict[tuple[str, str], dict[str, Any]] = {}
    model_by_company: dict[tuple[str, str], dict[str, Any]] = {}
    for index, row in enumerate(pit_rows):
        identity_payload = {
            "company_id": row.get("company_id"),
            "snapshot_cutoff_at": row.get("snapshot_cutoff_at"),
            "snapshot_schema_version": row.get("snapshot_schema_version"),
            "snapshot_revision": row.get("snapshot_revision"),
            "f1_f2_effective_refs": row.get("f1_f2_effective_refs"),
            "f3_observation_refs": row.get("f3_observation_refs"),
            "evidence_refs": row.get("evidence_refs"),
            "dataset_refs": row.get("dataset_refs"),
            "universe_release_id": row.get("universe_release_id"),
            "tradability_state_ref": row.get("tradability_state_ref"),
            "retrieval_receipt_id": row.get("retrieval_receipt_id"),
            "retrieval_source_hash": row.get("retrieval_source_hash"),
        }
        if row.get("pit_snapshot_id") != deterministic_id("pit", identity_payload):
            _retrieval_semantic_failure("PIT snapshot ID is not deterministic for its semantic payload", {"row_index": index})
        generator_version = row.get("generator_version")
        if not isinstance(generator_version, str) or not generator_version:
            _retrieval_semantic_failure("PIT row generator_version must be a non-empty string", {"row_index": index})
        expected_capture = deterministic_id(
            "capture",
            {"pit_snapshot_id": row.get("pit_snapshot_id"), "generator_version": generator_version},
        )
        if row.get("capture_run_id") != expected_capture:
            _retrieval_semantic_failure("capture_run_id is not deterministic for PIT/generator identity", {"row_index": index})
        pit_by_company[(row["company_id"], row["snapshot_cutoff_at"])] = row
    for row in model_inputs:
        model_by_company[(row["company_id"], row["snapshot_cutoff_at"])] = row

    required = {
        "retrieval_receipt_id",
        "company_id",
        "cutoff_at",
        "source_version",
        "source_hash",
        "source_matching_rows",
        "selected_rows",
        "excluded_rows",
        "exclusions",
        "cutoff_frozen_bundle",
    }
    audit_keys: list[tuple[str, str]] = []
    audit_by_company: dict[tuple[str, str], dict[str, Any]] = {}
    for index, receipt in enumerate(retrieval_audits):
        missing = sorted(required - set(receipt))
        if missing:
            _retrieval_semantic_failure("retrieval receipt is missing required fields", {"row_index": index, "missing": missing})
        company_id = receipt.get("company_id")
        cutoff_at = receipt.get("cutoff_at")
        source_version = receipt.get("source_version")
        source_hash = receipt.get("source_hash")
        receipt_id = receipt.get("retrieval_receipt_id")
        exclusions = receipt.get("exclusions")
        if not all(isinstance(value, str) and value for value in (company_id, cutoff_at, source_version, source_hash, receipt_id)):
            _retrieval_semantic_failure("retrieval receipt identity/source fields must be non-empty strings", {"row_index": index})
        if cutoff_at != manifest_cutoff:
            _retrieval_semantic_failure(
                "retrieval receipt cutoff differs from the snapshot cutoff",
                {"row_index": index, "receipt_cutoff": cutoff_at, "manifest_cutoff": manifest_cutoff},
            )
        if len(source_hash) != 64 or any(character not in "0123456789abcdef" for character in source_hash.lower()):
            _retrieval_semantic_failure("retrieval receipt source_hash must be a SHA256 hex digest", {"row_index": index})
        counts = [receipt.get(name) for name in ("source_matching_rows", "selected_rows", "excluded_rows")]
        if any(not isinstance(value, int) or isinstance(value, bool) or value < 0 for value in counts):
            _retrieval_semantic_failure("retrieval receipt counts must be non-negative integers", {"row_index": index, "counts": counts})
        source_matching_rows, selected_rows, excluded_rows = counts
        if source_matching_rows != selected_rows + excluded_rows:
            _retrieval_semantic_failure(
                "retrieval receipt counts do not reconcile",
                {
                    "row_index": index,
                    "source_matching_rows": source_matching_rows,
                    "selected_rows": selected_rows,
                    "excluded_rows": excluded_rows,
                },
            )
        if not isinstance(exclusions, list) or excluded_rows != len(exclusions):
            _retrieval_semantic_failure(
                "retrieval receipt excluded_rows differs from exclusions length",
                {"row_index": index, "excluded_rows": excluded_rows},
            )
        if not isinstance(receipt.get("cutoff_frozen_bundle"), bool):
            _retrieval_semantic_failure("retrieval receipt cutoff_frozen_bundle must be boolean", {"row_index": index})
        for exclusion_index, exclusion in enumerate(exclusions):
            if not isinstance(exclusion, dict) or not isinstance(exclusion.get("row_id"), str) or not exclusion.get("row_id"):
                _retrieval_semantic_failure("retrieval exclusion requires a non-empty row_id", {"row_index": index, "exclusion_index": exclusion_index})
            codes = exclusion.get("codes")
            if not isinstance(codes, list) or not codes or any(not isinstance(code, str) or not code for code in codes):
                _retrieval_semantic_failure("retrieval exclusion requires non-empty string codes", {"row_index": index, "exclusion_index": exclusion_index})
        payload = {key: value for key, value in receipt.items() if key != "retrieval_receipt_id"}
        if receipt_id != deterministic_id("retrieval", payload):
            _retrieval_semantic_failure("retrieval receipt ID is not deterministic for its payload", {"row_index": index})
        audit_keys.append((company_id, cutoff_at))
        audit_by_company[(company_id, cutoff_at)] = receipt

    pit_company_keys = {(company_id, cutoff_at) for company_id, _, cutoff_at, _ in pit_keys}
    if len(set(audit_keys)) != len(audit_keys) or set(audit_keys) != pit_company_keys:
        _retrieval_semantic_failure(
            "retrieval receipt company/cutoff identities are not one-to-one with PIT/model rows",
            {"receipt_keys": sorted(set(audit_keys)), "pit_keys": sorted(pit_company_keys)},
        )
    for key in sorted(pit_company_keys):
        pit_row = pit_by_company[key]
        model_row = model_by_company[key]
        receipt = audit_by_company[key]
        for row, artifact in ((pit_row, "pit_snapshot.jsonl"), (model_row, "model_input.jsonl")):
            if row.get("retrieval_receipt_id") != receipt["retrieval_receipt_id"] or row.get("retrieval_source_hash") != receipt["source_hash"]:
                _retrieval_semantic_failure(
                    f"{artifact} retrieval lineage differs from the audit receipt",
                    {"company_id": key[0]},
                )
        if model_row.get("price_dataset_id") != manifest.get("price_dataset_id") or model_row.get("price_source_semantics") != manifest.get("price_source_semantics"):
            _retrieval_semantic_failure("model-input price lineage differs from manifest", {"company_id": key[0]})
        dataset_refs=pit_row.get("dataset_refs")
        price_refs=[] if not isinstance(dataset_refs,list) else [
            ref for ref in dataset_refs
            if isinstance(ref,dict)
            and ref.get("domain")=="SOURCE_DATASET"
            and ref.get("source_id")==manifest.get("price_dataset_id")
        ]
        if len(price_refs)!=1 or price_refs[0].get("content_hash")!=manifest.get("price_dataset_hash"):
            _retrieval_semantic_failure(
                "PIT price dataset reference is not exactly bound to manifest/model price identity",
                {"company_id":key[0],"matching_ref_count":len(price_refs)},
            )
        if pit_row.get("generator_version") != manifest.get("generator_version"):
            _retrieval_semantic_failure("PIT generator version differs from manifest", {"company_id": key[0]})
        if pit_row.get("universe_release_id") != manifest.get("universe_release_id"):
            _retrieval_semantic_failure("PIT universe release differs from manifest", {"company_id": key[0]})
        if receipt.get("source_version") != manifest.get("feature_source_version"):
            _retrieval_semantic_failure("retrieval source version differs from manifest", {"company_id": key[0]})
        if model_row.get("reconstruction_version") != manifest.get("reconstruction_version"):
            _retrieval_semantic_failure("model reconstruction version differs from manifest", {"company_id": key[0]})

    expected_receipt_ids = sorted(receipt["retrieval_receipt_id"] for receipt in retrieval_audits)
    expected_source_hashes = sorted({receipt["source_hash"] for receipt in retrieval_audits})
    if manifest.get("retrieval_receipt_ids") != expected_receipt_ids or manifest.get("retrieval_source_hashes") != expected_source_hashes:
        _retrieval_semantic_failure("manifest retrieval lineage does not match audit rows")


def _snapshot_manifest_identity_payload(manifest: dict[str, Any]) -> dict[str, Any]:
    fields = (
        "snapshot_date",
        "snapshot_cutoff_at",
        "snapshot_content_hash",
        "snapshot_status",
        "blockers",
        "pit_row_count",
        "model_input_row_count",
        "retrieval_audit_row_count",
        "pit_file_sha256",
        "model_input_file_sha256",
        "retrieval_audit_file_sha256",
        "retrieval_audit_content_hash",
        "retrieval_receipt_ids",
        "retrieval_source_hashes",
        "generator_version",
        "universe_release_id",
        "feature_source_version",
        "price_dataset_id",
        "price_dataset_hash",
        "price_source_semantics",
        "reconstruction_version",
    )
    return {field: manifest.get(field) for field in fields}


def verify_snapshot_artifacts(snapshot_dir: str | Path, *, allow_staging: bool = False) -> VerifiedSnapshot:
    """Verify state, actual bytes, row counts, and semantic aggregate.

    Verification occurs before a scorer or output path may be touched.
    """

    snapshot_dir = Path(snapshot_dir)
    manifest = _read_manifest(snapshot_dir / "manifest.json")
    expected_manifest_identity = sha256_hex(_snapshot_manifest_identity_payload(manifest))
    if manifest.get("snapshot_manifest_identity_hash") != expected_manifest_identity:
        raise M3Top3AdmissionError(
            "SNAPSHOT_MANIFEST_IDENTITY_MISMATCH",
            "manifest control identity differs from its declared hash",
            {"expected": expected_manifest_identity, "declared": manifest.get("snapshot_manifest_identity_hash")},
            EXIT_INTEGRITY,
        )
    status = manifest.get("snapshot_status")
    blockers = manifest.get("blockers")
    if not isinstance(blockers, list):
        raise M3Top3AdmissionError(
            "BLOCKED_MANIFEST_STATE_CONTRADICTION",
            "manifest blockers must be a list",
            {"snapshot_status": status},
            EXIT_BLOCKED,
        )
    if status == "SNAPSHOT_READY" and blockers:
        raise M3Top3AdmissionError(
            "BLOCKED_MANIFEST_STATE_CONTRADICTION",
            "READY snapshot has non-empty blockers",
            {"blockers": blockers},
            EXIT_BLOCKED,
        )
    if status != "SNAPSHOT_READY":
        raise M3Top3AdmissionError(
            "BLOCKED_SNAPSHOT_NOT_READY",
            f"snapshot status is {status!r}",
            {"snapshot_status": status, "blockers": blockers},
            EXIT_BLOCKED,
        )

    pit_path = snapshot_dir / "pit_snapshot.jsonl"
    model_path = snapshot_dir / "model_input.jsonl"
    audit_path = snapshot_dir / "retrieval_audit.jsonl"
    pit_bytes, pit_rows = _read_jsonl(pit_path)
    model_bytes, model_inputs = _read_jsonl(model_path)
    audit_bytes, retrieval_audits = _read_jsonl(audit_path)

    actual_pit_hash = sha256_hex(pit_bytes)
    if manifest.get("pit_file_sha256") != actual_pit_hash:
        raise M3Top3AdmissionError(
            "PIT_FILE_HASH_MISMATCH",
            "stored PIT bytes do not match the manifest",
            {"expected": manifest.get("pit_file_sha256"), "actual": actual_pit_hash},
            EXIT_INTEGRITY,
        )
    actual_model_hash = sha256_hex(model_bytes)
    if manifest.get("model_input_file_sha256") != actual_model_hash:
        raise M3Top3AdmissionError(
            "MODEL_INPUT_FILE_HASH_MISMATCH",
            "stored model-input bytes do not match the manifest",
            {"expected": manifest.get("model_input_file_sha256"), "actual": actual_model_hash},
            EXIT_INTEGRITY,
        )
    actual_audit_hash = sha256_hex(audit_bytes)
    if manifest.get("retrieval_audit_file_sha256") != actual_audit_hash:
        raise M3Top3AdmissionError(
            "RETRIEVAL_AUDIT_FILE_HASH_MISMATCH",
            "stored retrieval-audit bytes do not match the manifest",
            {"expected": manifest.get("retrieval_audit_file_sha256"), "actual": actual_audit_hash},
            EXIT_INTEGRITY,
        )

    if manifest.get("pit_row_count") != len(pit_rows):
        raise M3Top3AdmissionError(
            "ROW_COUNT_MISMATCH",
            "PIT row count differs from the manifest",
            {"declared": manifest.get("pit_row_count"), "actual": len(pit_rows), "artifact": "pit_snapshot.jsonl"},
            EXIT_INTEGRITY,
        )
    if manifest.get("model_input_row_count") != len(model_inputs):
        raise M3Top3AdmissionError(
            "ROW_COUNT_MISMATCH",
            "model-input row count differs from the manifest",
            {"declared": manifest.get("model_input_row_count"), "actual": len(model_inputs), "artifact": "model_input.jsonl"},
            EXIT_INTEGRITY,
        )
    if manifest.get("retrieval_audit_row_count") != len(retrieval_audits):
        raise M3Top3AdmissionError(
            "ROW_COUNT_MISMATCH",
            "retrieval-audit row count differs from the manifest",
            {"declared": manifest.get("retrieval_audit_row_count"), "actual": len(retrieval_audits), "artifact": "retrieval_audit.jsonl"},
            EXIT_INTEGRITY,
        )

    audit_content_hash=aggregate_hash([sha256_hex(row) for row in retrieval_audits])
    if manifest.get("retrieval_audit_content_hash") != audit_content_hash:
        raise M3Top3AdmissionError(
            "RETRIEVAL_AUDIT_CONTENT_HASH_MISMATCH",
            "recalculated retrieval-audit aggregate differs from the manifest",
            {"expected": manifest.get("retrieval_audit_content_hash"), "actual": audit_content_hash},
            EXIT_INTEGRITY,
        )

    aggregate = aggregate_hash(
        [sha256_hex(row) for row in pit_rows]
        + [sha256_hex(row) for row in model_inputs]
        + [sha256_hex(row) for row in retrieval_audits]
    )
    if manifest.get("snapshot_content_hash") != aggregate:
        raise M3Top3AdmissionError(
            "SNAPSHOT_CONTENT_HASH_MISMATCH",
            "recalculated semantic aggregate differs from the manifest",
            {"expected": manifest.get("snapshot_content_hash"), "actual": aggregate},
            EXIT_INTEGRITY,
        )
    _verify_retrieval_audit_semantics(snapshot_dir, manifest, pit_rows, model_inputs, retrieval_audits, allow_staging)
    return VerifiedSnapshot(manifest, pit_rows, model_inputs, retrieval_audits)


def _placeholder_values(value: Any) -> Iterable[str]:
    if isinstance(value, dict):
        for key, nested in value.items():
            yield str(key)
            yield from _placeholder_values(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from _placeholder_values(nested)
    elif value is None:
        yield "NONE"
    elif isinstance(value, str):
        yield value


def verify_official_scorer(
    scorer: Any,
    config_bytes: bytes,
    receipt: dict[str, Any] | None,
) -> None:
    """Admit an exact scorer/config identity for official-mode execution."""

    if not OFFICIAL_EXECUTION_ENABLED:
        raise M3Top3AdmissionError(
            "OFFICIAL_MODE_GLOBALLY_BLOCKED",
            "no active governed authority registry or cryptographic trust root admits official execution",
            exit_code=EXIT_AUTHORITY,
        )

    if getattr(scorer, "model_id", None) == "DIAGNOSTIC_FIXTURE" or scorer.__class__.__name__.lower().startswith("diagnostic"):
        raise M3Top3AdmissionError(
            "OFFICIAL_SCORER_ADMISSION_DENIED",
            "diagnostic/test scorers cannot enter official mode",
            exit_code=EXIT_AUTHORITY,
        )
    try:
        config = json.loads(config_bytes.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise M3Top3AdmissionError(
            "PLACEHOLDER_CONFIG_NOT_ADMISSIBLE",
            "official scorer config is not canonical JSON",
            exit_code=EXIT_AUTHORITY,
        ) from exc
    placeholders = ("WORKING", "UNRESOLVED", "EXAMPLE", "PLACEHOLDER")
    if any(any(token in item.upper() for token in placeholders) for item in _placeholder_values(config)):
        raise M3Top3AdmissionError(
            "PLACEHOLDER_CONFIG_NOT_ADMISSIBLE",
            "working/example/unresolved values are not admissible in official mode",
            exit_code=EXIT_AUTHORITY,
        )
    required = {
        "model_id",
        "model_version",
        "model_schema_version",
        "feature_set_version",
        "scorer_artifact_sha256",
        "config_sha256",
        "baseline_identity",
        "authority_receipt",
    }
    if not isinstance(receipt, dict) or required - set(receipt) or any(not receipt.get(k) for k in required):
        raise M3Top3AdmissionError(
            "OFFICIAL_SCORER_ADMISSION_DENIED",
            "complete frozen scorer identity and authority receipt are required",
            {"missing": sorted(required - set(receipt or {}))},
            EXIT_AUTHORITY,
        )
    actual_config_hash = sha256_hex(config_bytes)
    if receipt["config_sha256"] != actual_config_hash or getattr(scorer, "config_hash", None) != actual_config_hash:
        raise M3Top3AdmissionError(
            "SCORER_CONFIG_HASH_MISMATCH",
            "scorer/config identity differs from actual canonical config bytes",
            {"actual": actual_config_hash},
            EXIT_AUTHORITY,
        )
    for attr in ("model_id", "model_version", "model_schema_version", "feature_set_version"):
        if getattr(scorer, attr, None) != receipt[attr]:
            raise M3Top3AdmissionError(
                "OFFICIAL_SCORER_ADMISSION_DENIED",
                f"scorer {attr} differs from the release receipt",
                {"field": attr},
                EXIT_AUTHORITY,
            )
    artifact_path = getattr(scorer, "artifact_path", None)
    if artifact_path is None or hash_file(Path(artifact_path)) != receipt["scorer_artifact_sha256"]:
        raise M3Top3AdmissionError(
            "OFFICIAL_SCORER_ADMISSION_DENIED",
            "scorer artifact bytes do not match the release receipt",
            exit_code=EXIT_AUTHORITY,
        )


def verify_price_release(provider: Any, admission_config: dict[str, Any] | None = None) -> None:
    """Re-verify provider byte identity and canonical/CA release admission."""

    semantics = getattr(provider, "semantics", None)
    if semantics not in ALLOWED_PRICE_SEMANTICS:
        raise M3Top3AdmissionError(
            "UNSUPPORTED_PRICE_SEMANTICS",
            "price semantics must match the governed allowlist exactly",
            {"semantics": semantics, "allowed": sorted(ALLOWED_PRICE_SEMANTICS)},
            EXIT_AUTHORITY,
        )
    raw_paths = getattr(provider, "paths", None)
    if raw_paths is None:
        single_path = getattr(provider, "path", None)
        raw_paths = [single_path] if single_path is not None else []
    paths = [Path(path).resolve() for path in raw_paths]
    if not paths:
        raise M3Top3AdmissionError(
            "PRICE_COMPONENT_PATHS_UNAVAILABLE",
            "price provider must expose exact component paths for live byte verification",
            exit_code=EXIT_INTEGRITY,
        )
    try:
        live_component_hashes = {str(path): hash_file(path) for path in paths}
    except OSError as exc:
        raise M3Top3AdmissionError(
            "PRICE_COMPONENT_HASH_MISMATCH",
            "price component bytes are unavailable during live verification",
            {"cause": type(exc).__name__},
            EXIT_INTEGRITY,
        ) from exc
    cached_components = {str(Path(path).resolve()): digest for path, digest in getattr(provider, "component_hashes", {}).items()}
    actual_hash = (
        next(iter(live_component_hashes.values()))
        if len(live_component_hashes) == 1
        else price_dataset_identity_hash(getattr(provider, "dataset_id", ""), live_component_hashes)
    )
    if (
        not actual_hash
        or getattr(provider, "dataset_hash", None) != actual_hash
        or getattr(provider, "actual_dataset_hash", None) != actual_hash
        or cached_components != live_component_hashes
    ):
        raise M3Top3AdmissionError(
            "PRICE_COMPONENT_HASH_MISMATCH",
            "configured price hash differs from actual component bytes",
            {
                "declared": getattr(provider, "dataset_hash", None),
                "cached": getattr(provider, "actual_dataset_hash", None),
                "actual": actual_hash,
            },
            EXIT_INTEGRITY,
        )
    if len(live_component_hashes) > 1:
        manifest = getattr(provider, "component_manifest", None)
        required = {"manifest_version", "hash_algorithm", "dataset_id", "dataset_hash", "components"}
        expected_components = [{"path": path, "sha256": digest} for path, digest in sorted(live_component_hashes.items())]
        if (
            not isinstance(manifest, dict)
            or required - set(manifest)
            or manifest.get("manifest_version") != "m3top3-price-components-v1"
            or manifest.get("hash_algorithm") != "SHA256"
            or manifest.get("dataset_id") != getattr(provider, "dataset_id", None)
            or manifest.get("dataset_hash") != actual_hash
            or manifest.get("components") != expected_components
        ):
            raise M3Top3AdmissionError(
                "PRICE_COMPONENT_MANIFEST_MISMATCH",
                "live component paths/hashes or dataset identity differ from the versioned manifest",
                {"expected_components": expected_components},
                EXIT_INTEGRITY,
            )
    if semantics != "PRICE_CANONICAL":
        return
    if not PRICE_CANONICAL_VALIDATION_ENABLED:
        raise M3Top3AdmissionError(
            "PRICE_CANONICAL_GLOBALLY_BLOCKED",
            "self-asserted canonical receipts cannot create VALIDATION authority",
            exit_code=EXIT_AUTHORITY,
        )


def price_dataset_identity_hash(dataset_id: str, component_hashes: dict[str, str]) -> str:
    components=[{"path":path,"sha256":digest} for path,digest in sorted(component_hashes.items())]
    return sha256_hex({"manifest_version":"m3top3-price-components-v1","dataset_id":dataset_id,"components":components})


def verify_price_component_manifest(provider: Any, manifest: dict[str, Any] | None) -> None:
    components=getattr(provider,"component_hashes",{})
    if len(components)<=1:
        return
    if not isinstance(manifest,dict):
        raise M3Top3AdmissionError("PRICE_COMPONENT_MANIFEST_REQUIRED","multi-component price input requires a versioned byte manifest",exit_code=EXIT_INTEGRITY)
    required={"manifest_version","hash_algorithm","dataset_id","dataset_hash","components"}
    if required-set(manifest) or manifest.get("manifest_version")!="m3top3-price-components-v1" or manifest.get("hash_algorithm")!="SHA256":
        raise M3Top3AdmissionError("PRICE_COMPONENT_MANIFEST_MISMATCH","price component manifest schema/version is invalid",exit_code=EXIT_INTEGRITY)
    expected=[{"path":path,"sha256":digest} for path,digest in sorted(components.items())]
    declared=manifest.get("components")
    if manifest.get("dataset_id")!=getattr(provider,"dataset_id",None) or manifest.get("dataset_hash")!=getattr(provider,"actual_dataset_hash",None) or declared!=expected:
        raise M3Top3AdmissionError("PRICE_COMPONENT_MANIFEST_MISMATCH","component paths/hashes or dataset identity do not match actual bytes",{"expected_components":expected},EXIT_INTEGRITY)
