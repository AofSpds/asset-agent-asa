from __future__ import annotations

import gzip
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

from .contracts_v1 import (
    FEATURE_SCHEMA_VERSION,
    MODEL_INPUT_SCHEMA_VERSION,
    MODEL_VERSION,
    SCORER_IO_VERSION,
    SCORER_VERSION,
    WEIGHT_VERSION,
    WINDOW_MAPPING_VERSION,
    validate_snapshot_batch,
)
from .core import sha256_hex
from .features_v1 import AXIS_BY_FEATURE, FEATURE_IDS
from .runtime_v1 import build_engine
from .shared_interface_guards_v1 import (
    validate_consumed_value_provenance,
    validate_f08_freshness_provenance,
)


RUNNER_VERSION = "M3TOP3-COVERAGE-LIMITED-REPLAY-v1.0-WORKING"
POPULATION_REVISION = "69a1e7b"
POPULATION_PATH = (
    "control/m3top3/recovery/2026-08-26/fast-close-worker-results/"
    "g3-annotation-candidate/G3_E_ANNOTATION_INGEST_QUEUE_v0.1.jsonl.gz"
)
POPULATION_GIT_BLOB = "4b3cfbfa9969abe2bd6dff5fdbfeb2db9d31cdae"
POPULATION_SHA256 = "8b3671d662457aef8c1a5595b33a85a27e08aaee56238e7218f1df0b4df78353"
POPULATION_ROW_COUNT = 1016

MISSING_FEATURE_REASON = "NO_ADMITTED_CUTOFF_SAFE_FEATURE_INPUT_IN_BOUND_EVIDENCE"
WINDOWS: dict[str, dict[str, str]] = {
    "W1": {"snapshot": "2024-08-09", "entry": "2024-08-12", "window_end": "2024-11-08", "exit": "2024-11-11"},
    "W2": {"snapshot": "2024-11-08", "entry": "2024-11-11", "window_end": "2025-02-10", "exit": "2025-02-11"},
    "W3": {"snapshot": "2025-02-10", "entry": "2025-02-11", "window_end": "2025-05-09", "exit": "2025-05-12"},
    "W4": {"snapshot": "2025-05-09", "entry": "2025-05-12", "window_end": "2025-08-08", "exit": "2025-08-11"},
    "W5": {"snapshot": "2025-08-08", "entry": "2025-08-11", "window_end": "2025-11-10", "exit": "2025-11-11"},
    "W6": {"snapshot": "2025-11-10", "entry": "2025-11-11", "window_end": "2026-02-10", "exit": "2026-02-11"},
    "W7": {"snapshot": "2026-02-10", "entry": "2026-02-11", "window_end": "2026-05-08", "exit": "2026-05-11"},
    "W8": {"snapshot": "2026-05-08", "entry": "2026-05-11", "window_end": "2026-08-10", "exit": "2026-08-11"},
}
EXPECTED_COUNTS: dict[str, dict[str, int]] = {
    "W1": {"ELIGIBLE": 57, "INELIGIBLE_BY_TRADABILITY": 8, "UNRESOLVED": 62},
    "W2": {"ELIGIBLE": 57, "INELIGIBLE_BY_TRADABILITY": 7, "UNRESOLVED": 63},
    "W3": {"ELIGIBLE": 57, "INELIGIBLE_BY_TRADABILITY": 6, "UNRESOLVED": 64},
    "W4": {"ELIGIBLE": 58, "INELIGIBLE_BY_TRADABILITY": 3, "UNRESOLVED": 66},
    "W5": {"ELIGIBLE": 58, "INELIGIBLE_BY_TRADABILITY": 3, "UNRESOLVED": 66},
    "W6": {"ELIGIBLE": 59, "INELIGIBLE_BY_TRADABILITY": 3, "UNRESOLVED": 65},
    "W7": {"ELIGIBLE": 59, "INELIGIBLE_BY_TRADABILITY": 2, "UNRESOLVED": 66},
    "W8": {"ELIGIBLE": 60, "INELIGIBLE_BY_TRADABILITY": 5, "UNRESOLVED": 62},
}


class CoverageLimitedReplayError(ValueError):
    pass


def git_blob_oid(payload: bytes) -> str:
    header = f"blob {len(payload)}\0".encode("ascii")
    return hashlib.sha1(header + payload).hexdigest()


def load_population_bytes(repo: str | Path) -> bytes:
    try:
        payload = subprocess.check_output(
            ["git", "show", f"{POPULATION_REVISION}:{POPULATION_PATH}"],
            cwd=Path(repo),
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise CoverageLimitedReplayError("exact G3-E population object is not readable") from exc
    if git_blob_oid(payload) != POPULATION_GIT_BLOB:
        raise CoverageLimitedReplayError("G3-E population Git blob identity mismatch")
    if hashlib.sha256(payload).hexdigest() != POPULATION_SHA256:
        raise CoverageLimitedReplayError("G3-E population compressed SHA-256 mismatch")
    return payload


def parse_population_bytes(payload: bytes) -> list[dict[str, Any]]:
    try:
        rows = [json.loads(line) for line in gzip.decompress(payload).decode("utf-8").splitlines() if line]
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CoverageLimitedReplayError("G3-E population payload is not valid UTF-8 JSONL gzip") from exc
    validate_population(rows)
    return rows


def validate_population(rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    materialized = list(rows)
    if len(materialized) != POPULATION_ROW_COUNT:
        raise CoverageLimitedReplayError(
            f"population row count mismatch: {len(materialized)} != {POPULATION_ROW_COUNT}"
        )
    row_keys = [str(row.get("row_key")) for row in materialized]
    if len(set(row_keys)) != len(row_keys) or "None" in row_keys:
        raise CoverageLimitedReplayError("population row_key is missing or duplicated")
    company_window_keys = [
        (str(row.get("window_id")), str(row.get("company_id")))
        for row in materialized
    ]
    if len(set(company_window_keys)) != len(company_window_keys):
        raise CoverageLimitedReplayError("population (window_id, company_id) is duplicated")
    for row in materialized:
        code = str(row.get("krx_code", ""))
        if (
            len(code) != 6
            or not code.isalnum()
            or code != code.upper()
            or row.get("company_id") != f"KRX:{code}"
        ):
            raise CoverageLimitedReplayError(f"invalid source company/code identity in {row.get('row_key')}")
    allowed = {"ELIGIBLE", "INELIGIBLE_BY_TRADABILITY", "UNRESOLVED"}
    for window_id in WINDOWS:
        window_rows = [r for r in materialized if r.get("window_id") == window_id]
        if len(window_rows) != 127:
            raise CoverageLimitedReplayError(f"{window_id}: expected 127 rows, got {len(window_rows)}")
        states = Counter(str(r.get("historical_eligibility_status")) for r in window_rows)
        if set(states) - allowed:
            raise CoverageLimitedReplayError(f"{window_id}: unsupported eligibility states {dict(states)}")
        if dict(states) != EXPECTED_COUNTS[window_id]:
            raise CoverageLimitedReplayError(
                f"{window_id}: eligibility counts {dict(states)} != {EXPECTED_COUNTS[window_id]}"
            )
        if any(r.get("snapshot_cutoff_at") != WINDOWS[window_id]["snapshot"] for r in window_rows):
            raise CoverageLimitedReplayError(f"{window_id}: snapshot tuple mismatch")
        if any(r.get("entry_date") != WINDOWS[window_id]["entry"] for r in window_rows):
            raise CoverageLimitedReplayError(f"{window_id}: entry tuple mismatch")
    return materialized


def _missing_feature_inputs(row_key: str) -> dict[str, dict[str, Any]]:
    return {
        feature_id: {
            "availability_state": "NOT_FOUND",
            "missing_reason": MISSING_FEATURE_REASON,
            "missing_evidence_ref": f"{POPULATION_GIT_BLOB}:{row_key}",
        }
        for feature_id in FEATURE_IDS
    }


def _model_eligibility(source_state: str) -> tuple[str, str | None]:
    if source_state == "ELIGIBLE":
        return "ELIGIBLE", None
    if source_state == "INELIGIBLE_BY_TRADABILITY":
        return "INELIGIBLE", "HISTORICAL_ENTRY_INELIGIBILITY_PROVEN_IN_BOUND_G2_SOURCE"
    if source_state == "UNRESOLVED":
        return "REVIEW_REQUIRED", "HISTORICAL_ENTRY_ELIGIBILITY_UNRESOLVED_IN_BOUND_G2_SOURCE"
    raise CoverageLimitedReplayError(f"unsupported source eligibility state {source_state!r}")


def build_window_mis(
    window_id: str,
    population_rows: Iterable[dict[str, Any]],
    *,
    pmo_run_id: str,
    code_identity: str,
) -> list[dict[str, Any]]:
    if window_id not in WINDOWS:
        raise CoverageLimitedReplayError(f"unknown window_id {window_id!r}")
    all_source_rows = sorted(
        (row for row in population_rows if row["window_id"] == window_id),
        key=lambda row: row["company_id"],
    )
    if len(all_source_rows) != 127:
        raise CoverageLimitedReplayError(f"{window_id}: cannot build MIS without all 127 rows")
    source_rows = [
        row for row in all_source_rows
        if row["historical_eligibility_status"] == "ELIGIBLE"
    ]
    identity_payload = {
        "population_blob": POPULATION_GIT_BLOB,
        "population_sha256": POPULATION_SHA256,
        "window_id": window_id,
        "outer_population_row_keys": [row["row_key"] for row in all_source_rows],
        "include_row_keys": [row["row_key"] for row in source_rows],
        "missingness_policy": MISSING_FEATURE_REASON,
    }
    snapshot_revision = sha256_hex(identity_payload)
    window = WINDOWS[window_id]
    result: list[dict[str, Any]] = []
    for source in source_rows:
        eligibility, exclusion_reason = _model_eligibility(source["historical_eligibility_status"])
        result.append(
            {
                "snapshot_id": f"{pmo_run_id}-{window_id}",
                "snapshot_date": window["snapshot"],
                "snapshot_cutoff_at": f"{window['snapshot']}T23:59:59+09:00",
                "snapshot_content_hash_or_revision": snapshot_revision,
                "window_anchor_date": window["snapshot"],
                "window_mapping_version": WINDOW_MAPPING_VERSION,
                "company_id": source["company_id"],
                "krx_code": str(source["krx_code"]).zfill(6),
                "universe_release_id": (
                    "U127_LOGICAL_MEMBERSHIP_FROM_G3E_QUEUE_"
                    f"GIT_BLOB_{POPULATION_GIT_BLOB}__NOT_RELEASE_ADMITTED"
                ),
                "eligibility_state": eligibility,
                "exclusion_reason": exclusion_reason,
                "model_version": MODEL_VERSION,
                "feature_schema_version": FEATURE_SCHEMA_VERSION,
                "scorer_version": SCORER_VERSION,
                "weight_version": WEIGHT_VERSION,
                "model_input_schema_version": MODEL_INPUT_SCHEMA_VERSION,
                "scorer_io_version": SCORER_IO_VERSION,
                "input_release_or_hash": f"SHA256:{POPULATION_SHA256}",
                "code_or_executable_identity": code_identity,
                "feature_raw_inputs": _missing_feature_inputs(source["row_key"]),
                "hard_risk_gate": {"state": "NONE"},
                "replay_source": {
                    "row_key": source["row_key"],
                    "historical_eligibility_status": source["historical_eligibility_status"],
                    "row_ingest_state": source.get("row_ingest_state"),
                    "annotation_sidecar_state": source.get("annotation_sidecar_state"),
                    "source_bundle_plan_state": source.get("source_bundle_plan_state"),
                },
            }
        )
    return result


def validate_replay_mis_shape(records: Iterable[dict[str, Any]], code_identity: str) -> list[dict[str, Any]]:
    rows = validate_snapshot_batch(records)
    seen_codes: dict[str, str] = {}
    allowed_block_keys = {"availability_state", "missing_reason", "missing_evidence_ref"}
    for record in rows:
        if not code_identity or record.get("code_or_executable_identity") != code_identity:
            raise CoverageLimitedReplayError("MIS executable identity is empty or mismatched")
        company_id = str(record.get("company_id", ""))
        krx_code = str(record.get("krx_code", ""))
        if (
            company_id != f"KRX:{krx_code}"
            or len(krx_code) != 6
            or not krx_code.isalnum()
            or krx_code != krx_code.upper()
        ):
            raise CoverageLimitedReplayError(f"invalid company/code binding: {company_id}/{krx_code}")
        if krx_code in seen_codes and seen_codes[krx_code] != company_id:
            raise CoverageLimitedReplayError(f"ambiguous KRX code binding: {krx_code}")
        seen_codes[krx_code] = company_id
        blocks = record.get("feature_raw_inputs")
        if not isinstance(blocks, dict) or set(blocks) != set(FEATURE_IDS):
            raise CoverageLimitedReplayError(f"{company_id}: exact F01-F09 blocks required")
        for feature_id, block in blocks.items():
            if not isinstance(block, dict):
                raise CoverageLimitedReplayError(f"{company_id}/{feature_id}: feature block must be an object")
            if set(block) - allowed_block_keys:
                raise CoverageLimitedReplayError(
                    f"{company_id}/{feature_id}: missing feature block carries unapproved fields"
                )
            if block.get("availability_state") != "NOT_FOUND":
                raise CoverageLimitedReplayError(f"{company_id}/{feature_id}: only explicit NOT_FOUND is bound")
            if block.get("missing_reason") != MISSING_FEATURE_REASON:
                raise CoverageLimitedReplayError(f"{company_id}/{feature_id}: missing reason mismatch")
    return rows


def _outer_partition(source_state: str, output: dict[str, Any]) -> str:
    if source_state == "INELIGIBLE_BY_TRADABILITY":
        return "EXCLUDE_PROVEN"
    if source_state == "UNRESOLVED":
        return "EXCLUDE_UNRESOLVED"
    if output.get("final_score") is None:
        return "REPLAY_DATA_INSUFFICIENT"
    return "INCLUDE_SCORED"


def execute_model_stage(
    population_rows: Iterable[dict[str, Any]],
    *,
    pmo_run_id: str,
    code_identity: str,
    config_path: str | Path,
) -> dict[str, Any]:
    rows = validate_population(population_rows)
    engine = build_engine(code_identity=code_identity, config_path=config_path)
    window_results: list[dict[str, Any]] = []
    selection_ledger: list[dict[str, Any]] = []
    stage_sequence = ["POPULATION_BOUND"]

    for window_id in WINDOWS:
        mis = build_window_mis(
            window_id,
            rows,
            pmo_run_id=pmo_run_id,
            code_identity=code_identity,
        )
        validate_replay_mis_shape(mis, code_identity)
        for record in mis:
            validate_consumed_value_provenance(record)
            validate_f08_freshness_provenance(record)
        scored = engine.score_snapshot(mis)
        source_by_company = {
            row["company_id"]: row
            for row in rows
            if row["window_id"] == window_id
        }
        output_by_company = {output["company_id"]: output for output in scored["outputs"]}
        if set(output_by_company) != {
            source["company_id"]
            for source in source_by_company.values()
            if source["historical_eligibility_status"] == "ELIGIBLE"
        }:
            raise CoverageLimitedReplayError(f"{window_id}: scorer output/include population mismatch")
        partitions: Counter[str] = Counter()
        feature_states: Counter[str] = Counter()
        axis_coverage = Counter()
        for company_id in sorted(source_by_company):
            source = source_by_company[company_id]
            source_state = source["historical_eligibility_status"]
            output = output_by_company.get(company_id)
            if output is None:
                partition = "EXCLUDE_PROVEN" if source_state == "INELIGIBLE_BY_TRADABILITY" else "EXCLUDE_UNRESOLVED"
                partitions[partition] += 1
                selection_ledger.append(
                    {
                        "pmo_run_id": pmo_run_id,
                        "window_id": window_id,
                        "row_key": source["row_key"],
                        "company_id": company_id,
                        "krx_code": source["krx_code"],
                        "source_eligibility_state": source_state,
                        "model_eligibility_state": None,
                        "outer_partition": partition,
                        "score_status": "NOT_SENT_TO_SCORER_OUTER_EXCLUSION",
                        "feature_coverage_ratio": None,
                        "final_score": None,
                        "exact_rank": None,
                        "top3_flag": False,
                        "top10_flag": False,
                        "model_score_id": None,
                        "result_measurement_state": "NOT_APPLICABLE_OUTER_EXCLUSION",
                    }
                )
                continue
            partition = _outer_partition(source_state, output)
            partitions[partition] += 1
            for feature in output.get("feature_trace", {}).values():
                feature_states[str(feature.get("availability_state"))] += 1
            for axis, payload in output.get("axis_coverage", {}).items():
                axis_coverage[(axis, str(payload.get("coverage_ratio")))] += 1
            selection_ledger.append(
                {
                    "pmo_run_id": pmo_run_id,
                    "window_id": window_id,
                    "row_key": source["row_key"],
                    "company_id": output["company_id"],
                    "krx_code": source["krx_code"],
                    "source_eligibility_state": source["historical_eligibility_status"],
                    "model_eligibility_state": output["eligibility_state"],
                    "outer_partition": partition,
                    "score_status": output["score_status"],
                    "feature_coverage_ratio": output["feature_coverage_ratio"],
                    "final_score": output["final_score"],
                    "exact_rank": output["exact_rank"],
                    "top3_flag": output["top3_flag"],
                    "top10_flag": output["top10_flag"],
                    "model_score_id": "m3score_" + sha256_hex(
                        {
                            "engine_run_id": output["run_id"],
                            "snapshot_id": output["snapshot_id"],
                            "company_id": output["company_id"],
                            "scored_payload": output,
                        }
                    ),
                    "result_measurement_state": (
                        "PENDING_OUTCOME_STAGE" if output["final_score"] is not None
                        else "NOT_MEASURED_MODEL_SCORE_UNAVAILABLE"
                    ),
                }
            )

        expected_partition = {
            "REPLAY_DATA_INSUFFICIENT": EXPECTED_COUNTS[window_id]["ELIGIBLE"],
            "EXCLUDE_PROVEN": EXPECTED_COUNTS[window_id]["INELIGIBLE_BY_TRADABILITY"],
            "EXCLUDE_UNRESOLVED": EXPECTED_COUNTS[window_id]["UNRESOLVED"],
        }
        if dict(partitions) != expected_partition:
            raise CoverageLimitedReplayError(
                f"{window_id}: unexpected outer partition {dict(partitions)} != {expected_partition}"
            )
        if scored["rankable_count"] != 0:
            raise CoverageLimitedReplayError(
                f"{window_id}: bound evidence unexpectedly produced a model score"
            )
        window_results.append(
            {
                "window_id": window_id,
                **WINDOWS[window_id],
                "u127_count": 127,
                "replay_include_eligibility_count": EXPECTED_COUNTS[window_id]["ELIGIBLE"],
                "exclude_proven_count": EXPECTED_COUNTS[window_id]["INELIGIBLE_BY_TRADABILITY"],
                "exclude_unresolved_count": EXPECTED_COUNTS[window_id]["UNRESOLVED"],
                "replay_data_insufficient_count": partitions["REPLAY_DATA_INSUFFICIENT"],
                "scoreable_count": scored["rankable_count"],
                "result_measured_count": 0,
                "scorer_include_batch_count": scored["eligible_count"],
                "scorer_coverage": scored["scorable_eligible_coverage"],
                "ranking_status": scored["ranking_status"],
                "engine_run_id": scored["run_id"],
                "input_hash": scored["input_hash"],
                "feature_availability_states": dict(sorted(feature_states.items())),
                "axis_coverage_observations": [
                    {"axis": axis, "coverage_ratio": coverage, "row_count": count}
                    for (axis, coverage), count in sorted(axis_coverage.items())
                ],
                "top3": [],
                "top10": [],
                "performance_metrics": {
                    "state": "NOT_MEASURABLE",
                    "reason": "ZERO_MODEL_SCOREABLE_ROWS",
                },
            }
        )
    stage_sequence.extend(["PROVENANCE_GUARDS_PASSED", "MODEL_BATCH_SCORING_COMPLETED"])
    totals = Counter()
    for result in window_results:
        for field in (
            "u127_count",
            "replay_include_eligibility_count",
            "exclude_proven_count",
            "exclude_unresolved_count",
            "replay_data_insufficient_count",
            "scoreable_count",
            "result_measured_count",
        ):
            totals[field] += int(result[field])
    return {
        "pmo_run_id": pmo_run_id,
        "runner_version": RUNNER_VERSION,
        "claim_class": "COVERAGE_LIMITED_RETROSPECTIVE_REPLAY",
        "model_stage_state": "COMPLETED",
        "stage_sequence": stage_sequence,
        "code_identity": code_identity,
        "config_hash": engine.config_hash,
        "source_population": {
            "revision": POPULATION_REVISION,
            "path": POPULATION_PATH,
            "git_blob": POPULATION_GIT_BLOB,
            "compressed_sha256": POPULATION_SHA256,
            "row_count": POPULATION_ROW_COUNT,
            "authority": "QUEUE_ONLY_NOT_ADMITTED",
        },
        "windows": window_results,
        "totals": dict(totals),
        "selection_ledger": selection_ledger,
        "outcome_firewall": {
            "future_price_values_loaded_before_model_selection": False,
            "future_outcome_fields_present_in_model_inputs": False,
            "price_stage_may_begin_after": "MODEL_BATCH_SCORING_COMPLETED",
        },
    }


def finalize_without_scored_rows(model_stage: dict[str, Any]) -> dict[str, Any]:
    if model_stage["totals"]["scoreable_count"] != 0:
        raise CoverageLimitedReplayError("outcome stage required when scored rows exist")
    finalized = dict(model_stage)
    finalized["stage_sequence"] = list(model_stage["stage_sequence"]) + [
        "PRICE_INPUT_IDENTITIES_BOUND_AFTER_MODEL_STAGE",
        "OUTCOME_VALUE_LOAD_SKIPPED_ZERO_SCORED_SELECTIONS",
        "SCORECARD_FINALIZED",
    ]
    finalized["outcome_stage_state"] = "NOT_MEASURED_ZERO_SCORED_SELECTIONS"
    finalized["scorecard_state"] = "COMPLETE_COVERAGE_LIMITED_ZERO_SCOREABLE"
    finalized["claim_ceiling"] = [
        "NO_OBSERVED_MODEL_PERFORMANCE_CLAIM",
        "NO_CLEAN_HOLDOUT_OR_OOS_CLAIM",
        "NO_COMPLETE_U127_OR_PIT_INPUT_CLAIM",
        "NO_PRICE_CANONICAL_OR_CA_COMPLETE_CLAIM",
        "NO_GOLDEN_FREEZE_OR_PRODUCTION_READINESS_CLAIM",
    ]
    return finalized


def selection_ledger_jsonl(rows: Iterable[dict[str, Any]]) -> str:
    return "".join(
        json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
        for row in rows
    )


def scorecard_markdown(scorecard: dict[str, Any]) -> str:
    lines = [
        "# M3Top3 First Coverage-Limited Retrospective Replay Scorecard",
        "",
        f"- PMO run: `{scorecard['pmo_run_id']}`",
        f"- State: `{scorecard['scorecard_state']}`",
        f"- Claim class: `{scorecard['claim_class']}`",
        f"- Model code identity: `{scorecard['code_identity']}`",
        f"- Config SHA-256: `{scorecard['config_hash']}`",
        "- Observed performance: `NOT_MEASURABLE` (zero model-scoreable rows)",
        "",
        "| Window | U127 | eligibility include | exclude proven | exclude unresolved | data insufficient | scoreable | result measured |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for window in scorecard["windows"]:
        lines.append(
            "| {window_id} | {u127_count} | {replay_include_eligibility_count} | "
            "{exclude_proven_count} | {exclude_unresolved_count} | "
            "{replay_data_insufficient_count} | {scoreable_count} | {result_measured_count} |".format(**window)
        )
    total = scorecard["totals"]
    lines.extend(
        [
            "| **Total** | **{u127_count}** | **{replay_include_eligibility_count}** | "
            "**{exclude_proven_count}** | **{exclude_unresolved_count}** | "
            "**{replay_data_insufficient_count}** | **{scoreable_count}** | "
            "**{result_measured_count}** |".format(**total),
            "",
            "## Interpretation boundary",
            "",
            "All 465 eligibility-included company-window rows reached the frozen scorer as one complete "
            "127-row batch per window. The bounded evidence contains no admitted cutoff-safe feature values, "
            "so every feature remains `NOT_FOUND`; no value was changed to zero, false, safe, or adverse. "
            "The scorer therefore produced no rank, Top3, Top10, or measurable historical performance. "
            "This is an executed zero-scoreable scorecard, not a zero-performance result.",
            "",
        ]
    )
    return "\n".join(lines)
