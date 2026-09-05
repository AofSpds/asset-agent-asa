"""Fail-closed, create-once score-output stage for validated F05-R1 inputs.

The callable in this module is deliberately separate from market input
materialization.  It cannot invoke the unchanged scorer until four independent
validation receipts bind the exact target, base F02 bytes, F05 JSONL bytes,
configuration bytes, and merged model-input hash.
"""
from __future__ import annotations

import copy
import csv
import hashlib
import io
import json
import os
import re
from dataclasses import dataclass
from decimal import ROUND_HALF_EVEN, Decimal, localcontext
from pathlib import Path
from typing import Any, Mapping

from .contracts_v1 import assert_no_outcome_fields, input_batch_hash, validate_snapshot_batch
from .f05_r1_market import (
    EXPECTED_W1_COHORT_IDENTITY_SHA256,
    EXPECTED_W1_DENOMINATOR,
    F05_FEATURE_ID,
    W1_CUTOFF_DATE,
)
from .real_input_replay_v1 import validate_strict_w1_mis
from .scorer_v1 import M3Top3V1Engine

EXPECTED_F02_INPUT_BATCH_SHA256 = "13667596d8e76f10d319f4129a7cba3b890d2575b3cebf33b78a143740bbbf9e"
EXPECTED_CONFIG_SHA256 = "eecde22a7744cff505c624bb6f0bdb11714352a122632238ea68d9cd0fbacb98"
REQUIRED_VALIDATOR_ROLES = ("CTLV", "MODV", "ENGV", "IVA")
EXPECTED_VALIDATION_LEVEL_BY_ROLE = {
    "CTLV": "L1",
    "MODV": "L1",
    "ENGV": "L1",
    "IVA": "L2",
}
EXPECTED_TARGET_REVISION = "D1"
EXPECTED_VALIDATOR_IDENTITY_BY_ROLE = {
    role: f"root/f05_r1_{role.lower()}_d1" for role in REQUIRED_VALIDATOR_ROLES
}
AGGREGATE_VALIDATION_SCHEMA_VERSION = (
    "AAA-M3TOP3-F05-R1-AFFECTED-VALIDATION-REPORT-v1.0"
)
INDEPENDENT_VALIDATION_RECEIPT_SCHEMA_VERSION = (
    "AAA-M3TOP3-F05-R1-INDEPENDENT-VALIDATION-RECEIPT-v1.0"
)
EXPECTED_TARGET_AUTHOR_IDENTITY = "root/f05_r1_author"
EXPECTED_INDEPENDENCE_ASSERTION = "INDEPENDENT_OF_TARGET_AUTHOR_AND_OTHER_VALIDATORS"
RECEIPT_DESCRIPTOR_FIELDS = frozenset(
    {
        "role",
        "validation_level",
        "receipt_id",
        "validator_identity",
        "path",
        "sha256",
    }
)
F02_FIXED_COMPANY_IDS = frozenset((
    "KRX:003160", "KRX:005290", "KRX:025560", "KRX:031980", "KRX:036200",
))
EXPECTED_F02_SCORES = {
    "KRX:003160": Decimal("0"),
    "KRX:005290": Decimal("50"),
    "KRX:025560": Decimal("87.5"),
    "KRX:031980": Decimal("87.5"),
    "KRX:036200": Decimal("25"),
}
CLAIM_STATUS = "F02_F05_PROVISIONAL_EXPLORATORY_NO_OFFICIAL_TOP_K"
SCORE_FILENAME = "F05_R1_W1_SCORES.jsonl"
RANKING_FILENAME = "F05_R1_W1_PROVISIONAL_RANKING.csv"
FIVE_FILENAME = "F02_F05_PROVISIONAL_MULTI_FEATURE_VIEW.csv"


class F05ScoreOutputError(ValueError):
    """The score gate, input join, or output postcondition failed."""


@dataclass(frozen=True)
class F05ScoreArtifacts:
    score_jsonl: bytes
    provisional_ranking_csv: bytes
    f02_f05_exact_five_csv: bytes
    target_commit: str
    target_tree: str
    merged_input_hash: str
    engine_run_id: str

    def sha256_by_filename(self) -> dict[str, str]:
        return {
            SCORE_FILENAME: hashlib.sha256(self.score_jsonl).hexdigest(),
            RANKING_FILENAME: hashlib.sha256(self.provisional_ranking_csv).hexdigest(),
            FIVE_FILENAME: hashlib.sha256(self.f02_f05_exact_five_csv).hexdigest(),
        }


def _strict_json_bytes(data: bytes, context: str) -> Any:
    def pairs(values):
        result = {}
        for key, value in values:
            if key in result:
                raise F05ScoreOutputError(f"{context} contains duplicate JSON key: {key}")
            result[key] = value
        return result

    def reject_float(value):
        raise F05ScoreOutputError(f"{context} contains an unbound JSON float: {value}")

    def reject_constant(value):
        raise F05ScoreOutputError(f"{context} contains a non-finite number: {value}")

    try:
        return json.loads(
            data.decode("utf-8"),
            object_pairs_hook=pairs,
            parse_float=reject_float,
            parse_constant=reject_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise F05ScoreOutputError(f"{context} is not strict UTF-8 JSON") from exc


def _canonical_json_line(value: Any) -> bytes:
    return (
        json.dumps(
            value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
        )
        + "\n"
    ).encode("utf-8")


def _parse_canonical_jsonl(data: bytes) -> list[dict[str, Any]]:
    if not data or not data.endswith(b"\n"):
        raise F05ScoreOutputError("F05 input JSONL must be nonempty and end with LF")
    lines = data.splitlines(keepends=True)
    rows = []
    for index, line in enumerate(lines, start=1):
        if line in {b"\n", b"\r\n"}:
            raise F05ScoreOutputError("F05 input JSONL cannot contain blank lines")
        value = _strict_json_bytes(line, f"F05 input JSONL line {index}")
        if not isinstance(value, dict):
            raise F05ScoreOutputError("every F05 input JSONL line must be an object")
        if line != _canonical_json_line(value):
            raise F05ScoreOutputError(f"F05 input JSONL line {index} is not canonical")
        rows.append(value)
    return rows


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _require_sha(value: Any, context: str, length: int = 64) -> str:
    if not isinstance(value, str) or re.fullmatch(rf"[0-9a-f]{{{length}}}", value) is None:
        raise F05ScoreOutputError(f"{context} must be a lowercase {length}-hex value")
    return value


def _require_nonempty_text(value: Any, context: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise F05ScoreOutputError(f"{context} must be a nonempty trimmed string")
    return value


def _validate_f05_rows(rows: list[dict[str, Any]]) -> None:
    if len(rows) != EXPECTED_W1_DENOMINATOR:
        raise F05ScoreOutputError("F05 score input must contain exactly 57 rows")
    company_ids = [row.get("company_id") for row in rows]
    if company_ids != sorted(company_ids) or len(set(company_ids)) != EXPECTED_W1_DENOMINATOR:
        raise F05ScoreOutputError("F05 score input must be unique and company_id ascending")
    codes = [row.get("krx_code") for row in rows]
    if len(set(codes)) != EXPECTED_W1_DENOMINATOR:
        raise F05ScoreOutputError("F05 score input KRX codes must be unique")
    benchmark_20 = set()
    benchmark_60 = set()
    for row in rows:
        if (
            row.get("feature_id") != F05_FEATURE_ID
            or row.get("cutoff_date") != W1_CUTOFF_DATE.isoformat()
            or row.get("cohort_identity_sha256") != EXPECTED_W1_COHORT_IDENTITY_SHA256
            or row.get("benchmark_member_count") != EXPECTED_W1_DENOMINATOR
            or row.get("company_id") != f"KRX:{row.get('krx_code')}"
        ):
            raise F05ScoreOutputError("F05 row identity/cutoff/cohort binding mismatch")
        raw = row.get("feature_raw_input")
        if not isinstance(raw, dict) or raw.get("availability_state") != "AVAILABLE":
            raise F05ScoreOutputError("F05 feature_raw_input must be explicitly AVAILABLE")
        aliases = (
            ("trailing_20d_market_price_return", "trailing_20d_total_return"),
            ("universe_20d_equal_weight_market_price_return", "universe_20d_equal_weight_return"),
            ("trailing_60d_market_price_return", "trailing_60d_total_return"),
            ("universe_60d_equal_weight_market_price_return", "universe_60d_equal_weight_return"),
        )
        if any(raw.get(canonical) is None or raw.get(canonical) != raw.get(legacy) for canonical, legacy in aliases):
            raise F05ScoreOutputError("F05 canonical/legacy market-return aliases diverged")
        if raw.get("turnover_acceleration") is None:
            raise F05ScoreOutputError("F05 turnover acceleration is missing")
        if "valuation_percentile" in raw or "diffusion_percentile" in raw:
            raise F05ScoreOutputError("unapproved optional F05 saturation inputs are forbidden")
        if not raw.get("source_lineage_refs") or not isinstance(raw.get("calculation_trace"), dict):
            raise F05ScoreOutputError("F05 source lineage/calculation trace is missing")
        assert_no_outcome_fields(row)
        benchmark_20.add(raw["universe_20d_equal_weight_market_price_return"])
        benchmark_60.add(raw["universe_60d_equal_weight_market_price_return"])
    if len(benchmark_20) != 1 or len(benchmark_60) != 1:
        raise F05ScoreOutputError("F05 benchmark is not identical across all 57 companies")


def _validate_gate(
    report: Mapping[str, Any],
    report_sha256: str,
    receipts: Mapping[str, tuple[Mapping[str, Any], str]],
    receipt_paths: Mapping[str, str],
    input_bindings: Mapping[str, str],
    merged_input_hash: str,
) -> tuple[str, str, str]:
    if report.get("schema_version") != AGGREGATE_VALIDATION_SCHEMA_VERSION:
        raise F05ScoreOutputError("aggregate validation schema version mismatch")
    run_id = _require_nonempty_text(report.get("run_id"), "aggregate validation run_id")
    if report.get("target_revision") != EXPECTED_TARGET_REVISION:
        raise F05ScoreOutputError("aggregate validation target_revision must be exactly D1")
    target_revision = EXPECTED_TARGET_REVISION
    if report.get("status") != "PASS" or report.get("scoring_permitted") is not True:
        raise F05ScoreOutputError("aggregate validation has not permitted scoring")
    if report.get("target_author") is not False:
        raise F05ScoreOutputError("aggregate validation must declare target_author=false")
    if report.get("blocking_findings") != []:
        raise F05ScoreOutputError("aggregate validation has blocking findings")
    target_commit = _require_sha(report.get("target_commit"), "target_commit", 40)
    target_tree = _require_sha(report.get("target_tree"), "target_tree", 40)
    target_bundle = f"AAA-M3TOP3-F05-R1-D1-{target_commit}-{target_tree}"
    if report.get("target_bundle_identity") != target_bundle:
        raise F05ScoreOutputError("aggregate validation target bundle identity mismatch")
    if report.get("target_input_hash") != merged_input_hash:
        raise F05ScoreOutputError("aggregate validation target input hash mismatch")
    if report.get("input_bindings") != dict(input_bindings):
        raise F05ScoreOutputError("aggregate validation input byte bindings mismatch")
    expected_role_verdicts = {role: "PASS" for role in REQUIRED_VALIDATOR_ROLES}
    if report.get("role_verdicts") != expected_role_verdicts:
        raise F05ScoreOutputError(
            "aggregate role verdicts must be exactly CTLV/MODV/ENGV/IVA PASS"
        )
    descriptors = report.get("validation_receipts")
    if not isinstance(descriptors, list) or len(descriptors) != len(REQUIRED_VALIDATOR_ROLES):
        raise F05ScoreOutputError("aggregate validation receipt bindings are missing")
    if set(receipt_paths) != set(REQUIRED_VALIDATOR_ROLES):
        raise F05ScoreOutputError("receipt paths must be exactly CTLV/MODV/ENGV/IVA")
    exact_receipt_paths = {
        role: _require_nonempty_text(receipt_paths[role], f"{role} receipt path")
        for role in REQUIRED_VALIDATOR_ROLES
    }
    if len(set(exact_receipt_paths.values())) != len(REQUIRED_VALIDATOR_ROLES):
        raise F05ScoreOutputError("independent validation receipt paths must be unique")

    by_role: dict[str, Mapping[str, Any]] = {}
    for descriptor in descriptors:
        if not isinstance(descriptor, dict) or set(descriptor) != RECEIPT_DESCRIPTOR_FIELDS:
            raise F05ScoreOutputError("aggregate validation receipt descriptor schema mismatch")
        role = descriptor.get("role")
        if role not in REQUIRED_VALIDATOR_ROLES or role in by_role:
            raise F05ScoreOutputError("aggregate validation receipt roles must be unique")
        _require_nonempty_text(
            descriptor.get("path"), f"{role} aggregate receipt descriptor path"
        )
        _require_sha(descriptor.get("sha256"), f"{role} receipt descriptor SHA-256")
        by_role[role] = descriptor
    if [descriptor["role"] for descriptor in descriptors] != list(REQUIRED_VALIDATOR_ROLES):
        raise F05ScoreOutputError(
            "aggregate validation receipt descriptors must use canonical role order"
        )
    if set(by_role) != set(REQUIRED_VALIDATOR_ROLES) or set(receipts) != set(REQUIRED_VALIDATOR_ROLES):
        raise F05ScoreOutputError("validation receipts must be exactly CTLV/MODV/ENGV/IVA")

    receipt_ids: set[str] = set()
    validator_identities: set[str] = set()
    for role in REQUIRED_VALIDATOR_ROLES:
        receipt, receipt_sha = receipts[role]
        descriptor = by_role[role]
        receipt_id = _require_nonempty_text(receipt.get("receipt_id"), f"{role} receipt_id")
        validator_identity = _require_nonempty_text(
            receipt.get("validator_identity"), f"{role} validator_identity"
        )
        expected_level = EXPECTED_VALIDATION_LEVEL_BY_ROLE[role]
        expected_receipt_id_pattern = (
            rf"AAA-M3TOP3-F05-R1-D1-{role}-{expected_level}-"
            r"[0-9]{8}-[0-9]{6}-[0-9]{2}"
        )
        if re.fullmatch(expected_receipt_id_pattern, receipt_id) is None:
            raise F05ScoreOutputError(f"{role} receipt_id does not match the D1 role/level pattern")
        if validator_identity != EXPECTED_VALIDATOR_IDENTITY_BY_ROLE[role]:
            raise F05ScoreOutputError(f"{role} validator_identity is not the pinned D1 identity")
        if receipt_id in receipt_ids:
            raise F05ScoreOutputError("independent validation receipt_ids must be unique")
        if validator_identity in validator_identities:
            raise F05ScoreOutputError("independent validator identities must be unique")
        receipt_ids.add(receipt_id)
        validator_identities.add(validator_identity)

        if descriptor != {
            "role": role,
            "validation_level": expected_level,
            "receipt_id": receipt_id,
            "validator_identity": validator_identity,
            "path": exact_receipt_paths[role],
            "sha256": receipt_sha,
        }:
            raise F05ScoreOutputError(f"{role} aggregate receipt descriptor mismatch")
        if descriptor.get("sha256") != receipt_sha:
            raise F05ScoreOutputError(f"{role} receipt byte binding mismatch")
        if (
            receipt.get("schema_version")
            != INDEPENDENT_VALIDATION_RECEIPT_SCHEMA_VERSION
            or receipt.get("run_id") != run_id
            or receipt.get("target_revision") != target_revision
            or receipt.get("validator_role") != role
            or receipt.get("validation_level") != expected_level
            or receipt.get("author_identity") != EXPECTED_TARGET_AUTHOR_IDENTITY
            or validator_identity == EXPECTED_TARGET_AUTHOR_IDENTITY
            or receipt.get("independence_assertion") != EXPECTED_INDEPENDENCE_ASSERTION
            or receipt.get("supporting_not_self_pass") is not False
            or receipt.get("target_author") is not False
            or receipt.get("target_edited") is not False
            or receipt.get("no_pass_transfer") is not True
            or receipt.get("verdict") != "PASS"
            or receipt.get("findings") != []
            or receipt.get("target_commit") != target_commit
            or receipt.get("target_tree") != target_tree
            or receipt.get("target_bundle_identity") != target_bundle
            or receipt.get("target_input_hash") != merged_input_hash
            or receipt.get("input_bindings") != dict(input_bindings)
            or receipt.get("role_verdicts") != {role: "PASS"}
        ):
            raise F05ScoreOutputError(f"{role} receipt does not bind an independent exact-target PASS")
    # Receipt identities are exact, unique, Git/byte-bound declarations, but
    # they are not cryptographically signed.  This gate therefore validates
    # declared provenance under the repository custody boundary; it does not
    # authenticate a human or service principal outside that boundary.
    return target_commit, target_tree, target_bundle


def _csv_bytes(fieldnames: tuple[str, ...], rows: list[dict[str, Any]]) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode("utf-8")


def build_f05_r1_outputs(
    *,
    f05_input_jsonl: bytes,
    f02_input_batch_json: bytes,
    config_json: bytes,
    aggregate_validation_json: bytes,
    validation_receipt_json_by_role: Mapping[str, bytes],
    validation_receipt_path_by_role: Mapping[str, str],
) -> F05ScoreArtifacts:
    """Validate all bindings, invoke the unchanged engine once, and render bytes.

    This pure callable performs no filesystem writes.  It intentionally labels
    all rankings provisional even though the generic scorer internally assigns
    exact ranks to a fully scoreable 57-row batch.
    """
    f05_sha = _sha256(f05_input_jsonl)
    f02_sha = _sha256(f02_input_batch_json)
    config_sha = _sha256(config_json)
    if f02_sha != EXPECTED_F02_INPUT_BATCH_SHA256:
        raise F05ScoreOutputError("F02 model-input batch is not the exact persisted F02-R1 batch")
    if config_sha != EXPECTED_CONFIG_SHA256:
        raise F05ScoreOutputError("model configuration bytes changed")
    f05_rows = _parse_canonical_jsonl(f05_input_jsonl)
    _validate_f05_rows(f05_rows)
    f02_rows = _strict_json_bytes(f02_input_batch_json, "F02 model-input batch")
    config = _strict_json_bytes(config_json, "model configuration")
    report = _strict_json_bytes(aggregate_validation_json, "aggregate validation report")
    if not isinstance(f02_rows, list) or not isinstance(config, dict) or not isinstance(report, dict):
        raise F05ScoreOutputError("F02/config/validation document types are invalid")
    if config.get("feature_weights", {}).get(F05_FEATURE_ID) != 20:
        raise F05ScoreOutputError("unchanged F05 weight must remain exactly 20")
    if config.get("feature_weights", {}).get("F02_NUMERIC_BUSINESS_INFLECTION") != 10:
        raise F05ScoreOutputError("unchanged F02 weight must remain exactly 10")
    base_code_identity = f02_rows[0].get("code_or_executable_identity") if f02_rows else None
    validate_strict_w1_mis(f02_rows, code_identity=str(base_code_identity))

    f05_by_company = {row["company_id"]: row for row in f05_rows}
    if set(f05_by_company) != {row.get("company_id") for row in f02_rows}:
        raise F05ScoreOutputError("F02 and F05 57-company identities do not match exactly")
    merged = copy.deepcopy(f02_rows)
    for row in merged:
        old_f05 = row["feature_raw_inputs"].get(F05_FEATURE_ID)
        if not isinstance(old_f05, dict) or old_f05.get("availability_state") != "NOT_FOUND":
            raise F05ScoreOutputError("base F02 batch does not contain the expected missing F05 block")
        row["feature_raw_inputs"][F05_FEATURE_ID] = copy.deepcopy(
            f05_by_company[row["company_id"]]["feature_raw_input"]
        )
        assert_no_outcome_fields(row)
    validate_snapshot_batch(merged)
    merged_input_hash = input_batch_hash(merged)
    input_bindings = {
        "f05_input_jsonl_sha256": f05_sha,
        "f02_model_input_batch_sha256": f02_sha,
        "config_sha256": config_sha,
    }

    receipts = {}
    for role, raw in validation_receipt_json_by_role.items():
        parsed = _strict_json_bytes(raw, f"{role} validation receipt")
        if not isinstance(parsed, dict):
            raise F05ScoreOutputError(f"{role} validation receipt must be an object")
        receipts[role] = (parsed, _sha256(raw))
    report_sha = _sha256(aggregate_validation_json)
    target_commit, target_tree, target_bundle = _validate_gate(
        report,
        report_sha,
        receipts,
        validation_receipt_path_by_role,
        input_bindings,
        merged_input_hash,
    )

    # The unchanged scorer historically runs in Python's default Decimal
    # context.  Bind that context explicitly so external caller state cannot
    # alter score or rank bytes.
    with localcontext() as context:
        context.prec = 28
        context.rounding = ROUND_HALF_EVEN
        engine = M3Top3V1Engine(
            config,
            code_identity=f"{target_bundle}|COMMIT:{target_commit}|TREE:{target_tree}",
            config_sha256=config_sha,
        )
        scored = engine.score_snapshot(merged)

    if (
        scored.get("eligible_count") != EXPECTED_W1_DENOMINATOR
        or scored.get("rankable_count") != EXPECTED_W1_DENOMINATOR
        or scored.get("scorable_eligible_coverage") != "1"
    ):
        raise F05ScoreOutputError("unchanged scorer did not produce 57/57 score coverage")
    outputs = scored.get("outputs")
    if not isinstance(outputs, list) or len(outputs) != EXPECTED_W1_DENOMINATOR:
        raise F05ScoreOutputError("unchanged scorer output row count mismatch")

    code_by_company = {row["company_id"]: row["krx_code"] for row in merged}
    f05_score_by_company = {}
    for output in outputs:
        company_id = output["company_id"]
        f05_trace = output["feature_trace"].get(F05_FEATURE_ID)
        f02_trace = output["feature_trace"].get("F02_NUMERIC_BUSINESS_INFLECTION")
        if not isinstance(f05_trace, dict) or f05_trace.get("availability_state") != "AVAILABLE" or f05_trace.get("score") is None:
            raise F05ScoreOutputError(f"{company_id}: F05 is not AVAILABLE after scoring")
        f05_score_by_company[company_id] = Decimal(f05_trace["score"])
        has_f02 = company_id in F02_FIXED_COMPANY_IDS
        expected_coverage = Decimal("0.3") if has_f02 else Decimal("0.2")
        if Decimal(output["feature_coverage_ratio"]) != expected_coverage:
            raise F05ScoreOutputError(f"{company_id}: F02/F05 coverage semantics changed")
        if output.get("score_status") != "PROVISIONAL_MISSING_FEATURES":
            raise F05ScoreOutputError(f"{company_id}: score must remain provisional")
        if has_f02:
            if f02_trace.get("availability_state") != "AVAILABLE" or Decimal(f02_trace["score"]) != EXPECTED_F02_SCORES[company_id]:
                raise F05ScoreOutputError(f"{company_id}: preserved F02 score changed")
            expected_combined = (
                Decimal(25) * EXPECTED_F02_SCORES[company_id]
                + Decimal(20) * f05_score_by_company[company_id]
            ) / Decimal(45)
            if Decimal(output["final_score"]) != expected_combined:
                raise F05ScoreOutputError(f"{company_id}: combined F02/F05 score changed")
        elif f02_trace.get("score") is not None:
            raise F05ScoreOutputError(f"{company_id}: unexpected F02 score appeared")

    f05_order = sorted(f05_score_by_company, key=lambda cid: (-f05_score_by_company[cid], cid))
    f05_rank = {company_id: index for index, company_id in enumerate(f05_order, start=1)}
    combined_order = sorted(
        (row for row in outputs if row["company_id"] in F02_FIXED_COMPANY_IDS),
        key=lambda row: (-Decimal(row["final_score"]), row["company_id"]),
    )
    combined_rank = {row["company_id"]: index for index, row in enumerate(combined_order, start=1)}
    if sorted(f05_rank.values()) != list(range(1, 58)):
        raise F05ScoreOutputError("F05-only provisional ranks are not an exact 1..57 permutation")
    if sorted(combined_rank.values()) != list(range(1, 6)):
        raise F05ScoreOutputError("F02/F05 provisional ranks are not an exact 1..5 permutation")

    score_rows = []
    ranking_rows = []
    five_rows = []
    output_by_id = {row["company_id"]: row for row in outputs}
    for company_id in sorted(output_by_id):
        output = output_by_id[company_id]
        f05_trace = output["feature_trace"][F05_FEATURE_ID]
        f02_trace = output["feature_trace"]["F02_NUMERIC_BUSINESS_INFLECTION"]
        score_rows.append({
            "schema_version": "AAA-M3TOP3-F05-R1-W1-SCORE-ROW-v1.0",
            "claim_status": CLAIM_STATUS,
            "company_id": company_id,
            "krx_code": code_by_company[company_id],
            "f05_only_provisional_rank": f05_rank[company_id],
            "combined_provisional_rank": combined_rank.get(company_id),
            "f02_score": f02_trace.get("score"),
            "f05_score": f05_trace["score"],
            "recognition_velocity": f05_trace["trace"]["recognition_velocity"],
            "saturation_penalty": f05_trace["trace"]["saturation_penalty"],
            "pre_gate_score": output["pre_gate_score"],
            "final_score": output["final_score"],
            "feature_coverage_ratio": output["feature_coverage_ratio"],
            "score_status": output["score_status"],
            "risk_gate_state": output["risk_gate_state"],
            "risk_gate_multiplier": output["risk_gate_multiplier"],
            "top3_flag": False,
            "top10_flag": False,
            "engine_run_id": scored["run_id"],
            "merged_input_hash": merged_input_hash,
            "aggregate_validation_sha256": report_sha,
            "target_commit": target_commit,
            "target_tree": target_tree,
        })
        ranking_rows.append({
            "f05_only_provisional_rank": f05_rank[company_id],
            "company_id": company_id,
            "krx_code": code_by_company[company_id],
            "f05_score": f05_trace["score"],
            "recognition_velocity": f05_trace["trace"]["recognition_velocity"],
            "saturation_penalty": f05_trace["trace"]["saturation_penalty"],
            "available_feature_weight": "20",
            "feature_coverage_ratio": output["feature_coverage_ratio"],
            "claim_status": CLAIM_STATUS,
            "top3_flag": "false",
            "top10_flag": "false",
        })
        if company_id in F02_FIXED_COMPANY_IDS:
            five_rows.append({
                "combined_provisional_rank": combined_rank[company_id],
                "company_id": company_id,
                "krx_code": code_by_company[company_id],
                "f02_score": f02_trace["score"],
                "f05_score": f05_trace["score"],
                "available_feature_weight": "30",
                "feature_coverage_ratio": output["feature_coverage_ratio"],
                "available_axis_weight": "45",
                "provisional_combined_score": output["final_score"],
                "formula": "(25*F02_SCORE+20*F05_SCORE)/45",
                "limitation": CLAIM_STATUS,
            })
    ranking_rows.sort(key=lambda row: int(row["f05_only_provisional_rank"]))
    five_rows.sort(key=lambda row: (int(row["combined_provisional_rank"]), row["company_id"]))
    if {row["company_id"] for row in five_rows} != F02_FIXED_COMPANY_IDS or len(five_rows) != 5:
        raise F05ScoreOutputError("exact-five F02/F05 output membership changed")

    return F05ScoreArtifacts(
        score_jsonl=b"".join(_canonical_json_line(row) for row in score_rows),
        provisional_ranking_csv=_csv_bytes(tuple(ranking_rows[0]), ranking_rows),
        f02_f05_exact_five_csv=_csv_bytes(tuple(five_rows[0]), five_rows),
        target_commit=target_commit,
        target_tree=target_tree,
        merged_input_hash=merged_input_hash,
        engine_run_id=scored["run_id"],
    )


def persist_f05_r1_outputs(artifacts: F05ScoreArtifacts, output_dir: str | Path) -> dict[str, str]:
    """Create exactly the three terminal files in a previously absent directory."""
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=False)
    payloads = {
        SCORE_FILENAME: artifacts.score_jsonl,
        RANKING_FILENAME: artifacts.provisional_ranking_csv,
        FIVE_FILENAME: artifacts.f02_f05_exact_five_csv,
    }
    try:
        for name, payload in payloads.items():
            with (root / name).open("xb") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
    except Exception:
        # Never overwrite or silently retry a partial create-once attempt.
        raise
    return artifacts.sha256_by_filename()
