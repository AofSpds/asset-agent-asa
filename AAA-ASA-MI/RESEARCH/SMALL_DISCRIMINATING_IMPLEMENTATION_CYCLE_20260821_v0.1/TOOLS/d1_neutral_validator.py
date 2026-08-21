#!/usr/bin/env python3
"""Neutral structural validator for AAA-ASA-MI D1 adapter outputs.

This validator is deliberately model-agnostic. It does not decide which model is
scientifically correct and it does not contain a per-model expected-answer table.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

REQUIRED_VARIANTS = ("D1-A", "D1-B", "D1-C", "D1-D", "D1-E")
REQUIRED_FIELDS = (
    "BEHAVIOR_RELATION",
    "MEMORY_CONTENT_RELATION",
    "PROMISE_ORIGIN_STATUS",
    "DESCENT_STATUS",
    "COMMITMENT_OR_OBLIGATION_STATUS",
    "CONTINUATION_STATUS",
    "AUTHORITY_STATUS",
    "SAME_PERSONA_STATUS",
    "UNKNOWN_NOT_PROVEN_OUT_OF_SCOPE",
    "DECISION_DEPENDENCIES",
    "CHANGED_INPUT_CAUSING_OUTPUT_DELTA",
)
EVIDENCE_MODES = {
    "FORMAL_DERIVATION",
    "EXECUTABLE_REPLAY",
    "REVIEWER_INFERENCE",
    "SOURCE_CLAIM",
    "HUMAN_JUDGMENT",
    "NOT_TESTED",
}
D1B_FORBIDDEN_NEGATIVE_TOKENS = {
    "FALSE",
    "DID_NOT_PROMISE",
    "PROMISE_DID_NOT_OCCUR",
    "NO_PROMISE_OCCURRED",
    "NOT_AUTHORED",
}


class ValidationError(ValueError):
    pass


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_json(path: Path) -> tuple[Any, bytes]:
    raw = path.read_bytes()
    return json.loads(raw.decode("utf-8")), raw


def _walk_scalars(value: Any):
    if isinstance(value, dict):
        for v in value.values():
            yield from _walk_scalars(v)
    elif isinstance(value, list):
        for v in value:
            yield from _walk_scalars(v)
    else:
        yield value


def _contains_forbidden_negative(value: Any) -> bool:
    for scalar in _walk_scalars(value):
        if isinstance(scalar, str) and scalar.upper().strip() in D1B_FORBIDDEN_NEGATIVE_TOKENS:
            return True
        if scalar is False:
            return True
    return False


def validate(fixture_path: Path, output_path: Path) -> dict[str, Any]:
    fixture, fixture_raw = load_json(fixture_path)
    out, _ = load_json(output_path)

    if fixture.get("fixture_id") != "AAA-ASA-MI-D1-PROMISE-ORIGIN-v0.1":
        raise ValidationError("unexpected fixture_id")
    fixture_digest = sha256_bytes(fixture_raw)

    if out.get("fixture_id") != fixture["fixture_id"]:
        raise ValidationError("adapter output fixture_id mismatch")
    if out.get("fixture_sha256") != fixture_digest:
        raise ValidationError("adapter output fixture_sha256 mismatch")
    if out.get("candidate_semantics_unchanged") is not True:
        raise ValidationError("candidate_semantics_unchanged must be true")

    position = out.get("candidate_position")
    if position not in {f"A{i}" for i in range(1, 5)} | {f"B{i}" for i in range(1, 5)}:
        raise ValidationError("candidate_position must be A1-A4 or B1-B4")
    candidate_digest = out.get("candidate_exact_sha256", "")
    if not isinstance(candidate_digest, str) or len(candidate_digest) != 64:
        raise ValidationError("candidate_exact_sha256 must be a 64-char hex digest")
    try:
        int(candidate_digest, 16)
    except ValueError as exc:
        raise ValidationError("candidate_exact_sha256 is not hex") from exc

    results = out.get("variant_results")
    if not isinstance(results, list):
        raise ValidationError("variant_results must be a list")
    by_id = {}
    for result in results:
        if not isinstance(result, dict):
            raise ValidationError("each variant result must be an object")
        vid = result.get("variant_id")
        if vid in by_id:
            raise ValidationError(f"duplicate variant_id {vid}")
        by_id[vid] = result
        missing = [f for f in REQUIRED_FIELDS if f not in result]
        if missing:
            raise ValidationError(f"{vid}: missing required fields: {missing}")
        mode = result.get("EVIDENCE_MODE")
        if mode not in EVIDENCE_MODES:
            raise ValidationError(f"{vid}: invalid EVIDENCE_MODE {mode!r}")
        for field in REQUIRED_FIELDS[:8]:
            if isinstance(result[field], bool):
                raise ValidationError(f"{vid}:{field} must be typed/native output, not bare boolean")

    if set(by_id) != set(REQUIRED_VARIANTS):
        raise ValidationError(
            f"variant set mismatch: expected {REQUIRED_VARIANTS}, got {tuple(sorted(by_id))}"
        )

    # D1-B is an experiment-wide firewall, not a per-model preference:
    # loss of promise evidence must not be converted into a negative historical fact.
    if _contains_forbidden_negative(by_id["D1-B"]["PROMISE_ORIGIN_STATUS"]):
        raise ValidationError("D1-B violates NOT_PROVEN -> FALSE firewall")

    # D1-E must produce an authority-axis result rather than omit or collapse the axis.
    if by_id["D1-E"]["AUTHORITY_STATUS"] in (None, "", [], {}):
        raise ValidationError("D1-E AUTHORITY_STATUS must be explicit")

    return {
        "validator_state": "PASS_NEUTRAL_STRUCTURAL_CONTROLS",
        "fixture_id": fixture["fixture_id"],
        "fixture_sha256": fixture_digest,
        "adapter_id": out.get("adapter_id"),
        "candidate_position": position,
        "checked_variants": list(REQUIRED_VARIANTS),
        "model_rank_claim": "NONE",
        "validation_claim": "NONE",
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--fixture", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    args = p.parse_args()
    try:
        receipt = validate(args.fixture, args.output)
    except (OSError, json.JSONDecodeError, ValidationError) as exc:
        print(json.dumps({"validator_state": "FAIL", "reason": str(exc)}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
