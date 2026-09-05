from __future__ import annotations

from decimal import Decimal
from typing import Any, Iterable

from .contracts_v1 import (
    FEATURE_SCHEMA_VERSION, MODEL_INPUT_SCHEMA_VERSION, MODEL_VERSION,
    SCORER_IO_VERSION, SCORER_VERSION, WEIGHT_VERSION, WINDOW_MAPPING_VERSION,
    input_batch_hash, validate_snapshot_batch,
)
from .core import deterministic_id, sha256_hex
from .features_v1 import AXIS_BY_FEATURE, FEATURE_IDS, D
from .features_v1_narrow_patch import FeatureEngineV1NarrowPatch

GATE_MULTIPLIER = {"NONE": Decimal("1.00"), "SEVERE": Decimal("0.85"), "THESIS_BREAK": Decimal("0.70")}
OPPORTUNITY_AXES = {"Business_Momentum", "Expectation_Surprise", "Market_Positioning", "Forward_Runway"}


class ScorerError(ValueError):
    pass


class M3Top3V1Engine:
    model_version = MODEL_VERSION
    feature_schema_version = FEATURE_SCHEMA_VERSION
    scorer_version = SCORER_VERSION
    weight_version = WEIGHT_VERSION
    model_input_schema_version = MODEL_INPUT_SCHEMA_VERSION
    scorer_io_version = SCORER_IO_VERSION
    window_mapping_version = WINDOW_MAPPING_VERSION

    def __init__(self, config: dict[str, Any], code_identity: str, config_sha256: str | None = None):
        self.config = config
        self.code_identity = str(code_identity)
        self.config_hash = str(config_sha256) if config_sha256 else sha256_hex(config)
        self.axis_weights = {k: D(v) for k, v in config["axis_weights"].items()}
        self.feature_weights = {k: D(v) for k, v in config["feature_weights"].items()}
        if sum(self.axis_weights.values(), Decimal("0")) != Decimal("100"):
            raise ScorerError("axis weights must sum to 100")
        if sum(self.feature_weights.values(), Decimal("0")) != Decimal("100"):
            raise ScorerError("feature weights must sum to 100")
        self.features = FeatureEngineV1NarrowPatch(self.feature_weights)

    def _gate(self, record: dict[str, Any]) -> tuple[str, Decimal, set[str], list[str], str | None]:
        gate = record.get("hard_risk_gate") or {"state": "NONE"}
        state = gate.get("state", "NONE")
        warnings: list[str] = []
        if state not in GATE_MULTIPLIER:
            warnings.append("INVALID_RISK_GATE_STATE_IGNORED")
            return "NONE", GATE_MULTIPLIER["NONE"], set(), warnings, None
        if state == "NONE":
            return state, GATE_MULTIPLIER[state], set(), warnings, None
        group, status, reason = gate.get("event_group_id"), gate.get("evidence_status"), gate.get("reason")
        high_conf = status in {"VERIFIED_HIGH", "VERIFIED_PRIMARY", "VERIFIED_CUSTOMER", "VERIFIED_PRIMARY_OR_CUSTOMER"}
        if not group or not high_conf or not reason:
            warnings.append("RISK_GATE_EVIDENCE_INSUFFICIENT_NOT_APPLIED")
            return "NONE", GATE_MULTIPLIER["NONE"], set(), warnings, None
        if state == "THESIS_BREAK" and status not in {"VERIFIED_PRIMARY", "VERIFIED_CUSTOMER", "VERIFIED_PRIMARY_OR_CUSTOMER"}:
            warnings.append("THESIS_BREAK_REQUIRES_PRIMARY_OR_CUSTOMER_EVIDENCE")
            return "NONE", GATE_MULTIPLIER["NONE"], set(), warnings, None
        return state, GATE_MULTIPLIER[state], {str(group)}, warnings, str(reason)

    def _aggregate_company(self, record, feature_payload, gate_state, gate_multiplier, gate_warnings, gate_reason, run_id):
        cid = record["company_id"]
        base = {
            "snapshot_id": record["snapshot_id"], "company_id": cid,
            "model_version": self.model_version, "feature_schema_version": self.feature_schema_version,
            "scorer_version": self.scorer_version, "weight_version": self.weight_version,
            "model_input_schema_version": self.model_input_schema_version, "scorer_io_version": self.scorer_io_version,
            "window_mapping_version": self.window_mapping_version, "eligibility_state": record["eligibility_state"],
            "exclusion_reason": None, "pre_gate_score": None, "risk_gate_state": gate_state,
            "risk_gate_multiplier": str(gate_multiplier), "risk_gate_reason": gate_reason,
            "final_score": None, "exact_rank": None, "score_status": None,
            "feature_coverage_ratio": "0", "axis_coverage": {}, "top3_flag": False, "top10_flag": False,
            "warning_flags": list(gate_warnings), "run_id": run_id,
            "feature_trace": feature_payload.get("features", {}),
            "anti_double_count_audit": feature_payload.get("anti_double_count_audit", []),
        }
        if record["eligibility_state"] != "ELIGIBLE":
            base["score_status"] = "INELIGIBLE" if record["eligibility_state"] == "INELIGIBLE" else "REVIEW_REQUIRED"
            base["exclusion_reason"] = record.get("exclusion_reason") or record["eligibility_state"]
            return base

        features = feature_payload["features"]
        available_feature_weight = Decimal("0")
        by_axis: dict[str, list[tuple[Decimal, Decimal]]] = {}
        for fid in FEATURE_IDS:
            f = features.get(fid)
            if not f or f["score"] is None:
                continue
            score, weight = D(f["score"]), self.feature_weights[fid]
            available_feature_weight += weight
            by_axis.setdefault(AXIS_BY_FEATURE[fid], []).append((weight, score))

        base["feature_coverage_ratio"] = str(available_feature_weight / Decimal("100"))
        axis_scores: dict[str, Decimal] = {}
        for axis in self.axis_weights:
            comps = by_axis.get(axis, [])
            if not comps:
                base["axis_coverage"][axis] = {"score": None, "coverage_ratio": "0"}
                continue
            available = sum((w for w, _ in comps), Decimal("0"))
            total_axis_feature_weight = sum((self.feature_weights[fid] for fid in FEATURE_IDS if AXIS_BY_FEATURE[fid] == axis), Decimal("0"))
            axis_score = sum((w * s for w, s in comps), Decimal("0")) / available
            axis_scores[axis] = axis_score
            base["axis_coverage"][axis] = {"score": str(axis_score), "available_feature_weight": str(available), "coverage_ratio": str(available / total_axis_feature_weight)}

        if not any(a in axis_scores for a in OPPORTUNITY_AXES):
            base["score_status"] = "INSUFFICIENT_INPUT"
            base["warning_flags"].append("NO_OPPORTUNITY_AXIS_AVAILABLE")
            return base

        available_axis_weight = sum((self.axis_weights[a] for a in axis_scores), Decimal("0"))
        pre = sum((self.axis_weights[a] * s for a, s in axis_scores.items()), Decimal("0")) / available_axis_weight
        final = min(Decimal("100"), max(Decimal("0"), pre * gate_multiplier))
        base["pre_gate_score"], base["final_score"] = str(pre), str(final)
        base["score_status"] = "RANKABLE" if available_feature_weight == Decimal("100") else "PROVISIONAL_MISSING_FEATURES"
        if available_feature_weight < Decimal("100"):
            base["warning_flags"].append("MISSING_FEATURES_RENORMALIZED")
        return base

    def score_snapshot(self, records: Iterable[dict[str, Any]]) -> dict[str, Any]:
        rows = validate_snapshot_batch(records)
        input_hash = input_batch_hash(rows)
        run_id = deterministic_id("m3run", {
            "snapshot_id": rows[0]["snapshot_id"],
            "snapshot_content_hash_or_revision": rows[0]["snapshot_content_hash_or_revision"],
            "model_version": self.model_version, "feature_schema_version": self.feature_schema_version,
            "scorer_version": self.scorer_version, "weight_version": self.weight_version,
            "window_mapping_version": self.window_mapping_version, "code_identity": self.code_identity,
            "config_hash": self.config_hash, "input_hash": input_hash,
        })
        gate_info = {r["company_id"]: self._gate(r) for r in rows}
        gate_groups = {cid: info[2] for cid, info in gate_info.items()}
        feature_values = self.features.compute_snapshot(rows, hard_gate_groups=gate_groups)
        outputs = []
        for r in rows:
            state, multiplier, _, warnings, reason = gate_info[r["company_id"]]
            outputs.append(self._aggregate_company(r, feature_values[r["company_id"]], state, multiplier, warnings, reason, run_id))

        rankable = [o for o in outputs if o["eligibility_state"] == "ELIGIBLE" and o["final_score"] is not None]
        eligible_count = sum(1 for o in outputs if o["eligibility_state"] == "ELIGIBLE")
        rankable_count = len(rankable)
        coverage = Decimal(rankable_count) / Decimal(eligible_count) if eligible_count else Decimal("0")
        ranking_status = "OFFICIAL_RANKABLE_CANDIDATE" if coverage == Decimal("1") else "INCOMPLETE_COVERAGE"
        rankable.sort(key=lambda o: (-D(o["final_score"]), o["company_id"]))
        for i, o in enumerate(rankable, start=1):
            o["exact_rank"], o["top3_flag"], o["top10_flag"] = i, i <= 3, i <= 10
            if ranking_status != "OFFICIAL_RANKABLE_CANDIDATE":
                o["warning_flags"].append("INCOMPLETE_ELIGIBLE_DENOMINATOR")
        return {
            "run_id": run_id, "model_version": self.model_version,
            "feature_schema_version": self.feature_schema_version, "scorer_version": self.scorer_version,
            "weight_version": self.weight_version, "window_mapping_version": self.window_mapping_version,
            "code_identity": self.code_identity, "config_hash": self.config_hash, "input_hash": input_hash,
            "snapshot_id": rows[0]["snapshot_id"], "eligible_count": eligible_count, "rankable_count": rankable_count,
            "scorable_eligible_coverage": str(coverage), "ranking_status": ranking_status,
            "outputs": sorted(outputs, key=lambda o: o["company_id"]),
        }
