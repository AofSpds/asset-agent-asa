from __future__ import annotations

from decimal import Decimal
from typing import Any

from .core import parse_datetime


GUARD_IMPLEMENTATION_VERSION = "M3TOP3-SHARED-INTERFACE-GUARDS-v0.1-PROPOSAL"


class SharedInterfaceGuardError(ValueError):
    """Model-side fail-closed hook pending dual-Core shared-interface promotion."""


def _assert_supported_provenance(
    provenance: dict[str, Any],
    cutoff_at: str,
    *,
    context: str,
) -> None:
    if not isinstance(provenance, dict):
        raise SharedInterfaceGuardError(f"{context}: provenance object required")
    evidence_ref = (
        provenance.get("immutable_evidence_ref")
        or provenance.get("evidence_ref")
        or provenance.get("source_lineage_ref")
        or provenance.get("supported_cutoff_ref")
    )
    timestamp = provenance.get("publication_at") or provenance.get("supported_cutoff_at")
    if not evidence_ref:
        raise SharedInterfaceGuardError(f"{context}: immutable evidence/support reference required")
    if not timestamp:
        raise SharedInterfaceGuardError(f"{context}: publication_at or supported_cutoff_at required")
    if parse_datetime(timestamp) > parse_datetime(cutoff_at):
        raise SharedInterfaceGuardError(f"{context}: provenance timestamp exceeds snapshot cutoff")


def validate_consumed_value_provenance(record: dict[str, Any]) -> None:
    """Candidate fail-closed hook for FND-01.

    Accepted proposal shapes per consumed feature block:
      A) immutable_supported_cutoff_ref + supported_cutoff_at + evidence_ref/source ref
      B) consumed_fields[] + consumed_value_provenance[path] for each consumed path

    This helper is intentionally not wired into MIS-v1.0 release semantics until
    CORE A + CORE B reconcile the shared interface.
    """
    cutoff = record["snapshot_cutoff_at"]
    for feature_id, block in (record.get("feature_raw_inputs") or {}).items():
        if not isinstance(block, dict):
            continue
        if block.get("availability_state") in {"MISSING", "UNKNOWN", "REVIEW_REQUIRED", "NOT_FOUND"}:
            continue

        if block.get("immutable_supported_cutoff_ref"):
            _assert_supported_provenance(
                {
                    "supported_cutoff_ref": block.get("immutable_supported_cutoff_ref"),
                    "supported_cutoff_at": block.get("supported_cutoff_at"),
                    "evidence_ref": block.get("evidence_ref") or block.get("source_lineage_ref"),
                },
                cutoff,
                context=f"{feature_id}.immutable_supported_cutoff",
            )
            continue

        consumed_fields = block.get("consumed_fields")
        provenance_map = block.get("consumed_value_provenance")
        if not consumed_fields or not isinstance(provenance_map, dict):
            raise SharedInterfaceGuardError(
                f"{feature_id}: consumed_fields + consumed_value_provenance "
                "or immutable_supported_cutoff_ref required"
            )
        for path in consumed_fields:
            if path not in provenance_map:
                raise SharedInterfaceGuardError(f"{feature_id}.{path}: missing consumed-value provenance")
            _assert_supported_provenance(
                provenance_map[path],
                cutoff,
                context=f"{feature_id}.{path}",
            )

    gate = record.get("hard_risk_gate") or {}
    if gate.get("state") and gate.get("state") != "NONE":
        _assert_supported_provenance(
            gate.get("pit_provenance") or {},
            cutoff,
            context="hard_risk_gate",
        )


def validate_f08_freshness_provenance(record: dict[str, Any]) -> None:
    """Candidate FND-04 guard; arithmetic remains in F08 and cap stays 20."""
    cutoff = record["snapshot_cutoff_at"]
    f08 = (record.get("feature_raw_inputs") or {}).get("F08_EVIDENCE_RELIABILITY") or {}
    for target, evidence in (f08.get("feature_evidence") or {}).items():
        penalty = Decimal(str(evidence.get("freshness_penalty", 0)))
        if penalty <= 0:
            continue
        governed = bool(evidence.get("refresh_rule_id"))
        governed = governed or bool(
            evidence.get("refresh_code") and evidence.get("evaluated_freshness_state")
        )
        governed = governed or bool(evidence.get("supported_cutoff_ref"))
        if not governed:
            raise SharedInterfaceGuardError(
                f"F08 {target}: freshness_penalty requires governed refresh provenance"
            )
        timestamp = evidence.get("evaluated_at") or evidence.get("supported_cutoff_at")
        if timestamp and parse_datetime(timestamp) > parse_datetime(cutoff):
            raise SharedInterfaceGuardError(
                f"F08 {target}: freshness provenance evaluated after snapshot cutoff"
            )
