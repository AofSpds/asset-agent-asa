from __future__ import annotations

from decimal import Decimal
from typing import Any, Iterable, Mapping

from .features_v1 import AXIS_BY_FEATURE, FEATURE_IDS

COVERAGE_POLICY_VERSION = "M3TOP3-COVERAGE-RELEASE-POLICY_v1.0_WORKING"
PIT_PROVENANCE_POLICY_VERSION = "M3TOP3-PIT-CONSUMED-PROVENANCE-CONTRACT_v1.0_WORKING"
FRESHNESS_POLICY_VERSION = "M3TOP3-REFRESH-RULE-REGISTRY_v1.0_WORKING"
MANDATORY_AXES = (
    "Business_Momentum",
    "Expectation_Surprise",
    "Market_Positioning",
    "Forward_Runway",
    "Reliability_Risk",
)


class ReleaseValidationError(ValueError):
    pass


def _missing_summary(feature_trace: Mapping[str, Any]) -> dict[str, int]:
    out: dict[str, int] = {}
    for fid in FEATURE_IDS:
        state = str((feature_trace.get(fid) or {}).get("availability_state") or "ABSENT")
        out[state] = out.get(state, 0) + 1
    return out


def _all_axes_available(output: Mapping[str, Any]) -> bool:
    coverage = output.get("axis_coverage") or {}
    return all(axis in coverage and (coverage[axis] or {}).get("score") is not None for axis in MANDATORY_AXES)


def _has_review_required_feature(output: Mapping[str, Any]) -> bool:
    trace = output.get("feature_trace") or {}
    return any((trace.get(fid) or {}).get("availability_state") == "REVIEW_REQUIRED" for fid in FEATURE_IDS)


def validate_official_coverage_release(
    score_result: Mapping[str, Any],
    *,
    validation_dataset_release_id: str,
    denominator_policy_version: str,
    pit_validation_passed: Mapping[str, bool] | None = None,
    freshness_validation_passed: Mapping[str, bool] | None = None,
) -> dict[str, Any]:
    outputs = list(score_result.get("outputs") or [])
    pit_ok = pit_validation_passed or {}
    fresh_ok = freshness_validation_passed or {}

    eligible = [o for o in outputs if o.get("eligibility_state") == "ELIGIBLE"]
    per_company: list[dict[str, Any]] = []
    rankable_count = 0

    for output in outputs:
        cid = str(output.get("company_id"))
        eligible_state = output.get("eligibility_state")
        all_axes = _all_axes_available(output)
        review_required = _has_review_required_feature(output)
        final_exists = output.get("final_score") is not None
        ppass = bool(pit_ok.get(cid, False)) if eligible_state == "ELIGIBLE" else False
        fpass = bool(fresh_ok.get(cid, False)) if eligible_state == "ELIGIBLE" else False
        allowed = bool(
            eligible_state == "ELIGIBLE"
            and all_axes
            and not review_required
            and final_exists
            and ppass
            and fpass
        )
        if allowed:
            rankable_count += 1
        per_company.append(
            {
                "company_id": cid,
                "eligibility_state": eligible_state,
                "score_status": output.get("score_status"),
                "feature_coverage_ratio": output.get("feature_coverage_ratio"),
                "axis_coverage": output.get("axis_coverage"),
                "missing_unknown_review_summary": _missing_summary(output.get("feature_trace") or {}),
                "all_mandatory_axes_calculable": all_axes,
                "review_required_present": review_required,
                "pit_provenance_pass": ppass,
                "freshness_governance_pass": fpass,
                "provisional_ranking_allowed": allowed,
                "provisional_ranking_policy_ref": COVERAGE_POLICY_VERSION,
            }
        )

    denominator = len(eligible)
    coverage = Decimal(rankable_count) / Decimal(denominator) if denominator else Decimal("0")
    official = coverage == Decimal("1")

    return {
        "coverage_policy_version": COVERAGE_POLICY_VERSION,
        "eligible_company_denominator": denominator,
        "rankable_eligible_company_numerator": rankable_count,
        "company_rankability_coverage": str(coverage),
        "company_rankability_policy_id": COVERAGE_POLICY_VERSION,
        "mandatory_axes": list(MANDATORY_AXES),
        "minimum_numeric_feature_coverage_ratio": None,
        "feature_completeness_is_not_company_coverage": True,
        "denominator_policy_version": denominator_policy_version,
        "validation_dataset_release_id": validation_dataset_release_id,
        "model_version": score_result.get("model_version"),
        "feature_schema_version": score_result.get("feature_schema_version"),
        "scorer_version": score_result.get("scorer_version"),
        "weight_version": score_result.get("weight_version"),
        "pit_provenance_policy_version": PIT_PROVENANCE_POLICY_VERSION,
        "freshness_provenance_policy_or_registry_version": FRESHNESS_POLICY_VERSION,
        "per_company": per_company,
        "release_rankability_status": "OFFICIAL_RANKABLE" if official else "BLOCKED_INCOMPLETE_POLICY_COVERAGE",
    }
