from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from .core import aggregate_hash, canonical_json_bytes, hash_file, sha256_hex


EXIT_BLOCKED = 2
EXIT_INTEGRITY = 3
EXIT_AUTHORITY = 4


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


def verify_snapshot_artifacts(snapshot_dir: str | Path) -> VerifiedSnapshot:
    """Verify state, actual bytes, row counts, and semantic aggregate.

    Verification occurs before a scorer or output path may be touched.
    """

    snapshot_dir = Path(snapshot_dir)
    manifest = _read_manifest(snapshot_dir / "manifest.json")
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

    actual_hash = getattr(provider, "actual_dataset_hash", None)
    if not actual_hash or getattr(provider, "dataset_hash", None) != actual_hash:
        raise M3Top3AdmissionError(
            "PRICE_COMPONENT_HASH_MISMATCH",
            "configured price hash differs from actual component bytes",
            {"declared": getattr(provider, "dataset_hash", None), "actual": actual_hash},
            EXIT_INTEGRITY,
        )
    if getattr(provider, "semantics", None) != "PRICE_CANONICAL":
        return
    receipt = admission_config if admission_config is not None else getattr(provider, "canonical_release", None)
    required = ("frozen", "authority_receipt", "ca_receipt", "unresolved_ca_candidates")
    if not isinstance(receipt, dict) or any(key not in receipt for key in required):
        raise M3Top3AdmissionError(
            "PRICE_CANONICAL_ADMISSION_DENIED",
            "canonical semantics require frozen authority and CA receipts",
            exit_code=EXIT_AUTHORITY,
        )
    if receipt.get("frozen") is not True or not receipt.get("authority_receipt") or not receipt.get("ca_receipt"):
        raise M3Top3AdmissionError(
            "PRICE_CANONICAL_ADMISSION_DENIED",
            "canonical release receipt is incomplete",
            exit_code=EXIT_AUTHORITY,
        )
    if receipt.get("unresolved_ca_candidates") != 0:
        raise M3Top3AdmissionError(
            "PRICE_CANONICAL_CA_INCOMPLETE",
            "canonical release contains unresolved corporate-action candidates",
            {"unresolved_ca_candidates": receipt.get("unresolved_ca_candidates")},
            EXIT_AUTHORITY,
        )
