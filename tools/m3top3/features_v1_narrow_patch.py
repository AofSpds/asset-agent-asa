from __future__ import annotations

from decimal import Decimal
from typing import Any, Iterable

from .core import parse_date
from .features_v1 import (
    FEATURE_IDS,
    FeatureEngineV1,
    D,
    explicit,
    med,
    na,
    ok,
    raw,
    robust_pct,
)
from .window_mapping_v11 import add_calendar_months


FEATURE_IMPLEMENTATION_VERSION = "M3TOP3-FEATURE-ENGINE-v1.0.2-F06-IDENTITY-HARDENING_WORKING"


class FeatureInputGovernanceError(ValueError):
    """Fail-closed model-side error for ungoverned feature transformations."""


IDENTITY_FIELDS = ("milestone_id", "event_group_id", "evidence_group_id")


def _milestone_identity_keys(milestone: dict[str, Any]) -> tuple[tuple[str, str], ...]:
    """Return all governed identities without allowing cross-namespace collisions."""
    keys = []
    for field in IDENTITY_FIELDS:
        value = milestone.get(field)
        if value is not None and str(value).strip():
            keys.append((field, str(value).strip()))
    return tuple(keys)


def _identity_components(
    milestones: list[dict[str, Any]],
) -> tuple[list[list[dict[str, Any]]], list[dict[str, Any]]]:
    """Conservatively group transitively connected milestone identities.

    A row identifier cannot override a shared event/evidence identity. Anonymous
    rows stay visible but never become independent identity groups.
    """
    parents = list(range(len(milestones)))

    def find(index: int) -> int:
        while parents[index] != index:
            parents[index] = parents[parents[index]]
            index = parents[index]
        return index

    def union(left: int, right: int) -> None:
        left_root, right_root = find(left), find(right)
        if left_root != right_root:
            parents[right_root] = left_root

    first_by_key: dict[tuple[str, str], int] = {}
    identified: list[int] = []
    anonymous: list[dict[str, Any]] = []
    for index, milestone in enumerate(milestones):
        keys = _milestone_identity_keys(milestone)
        if not keys:
            anonymous.append(milestone)
            continue
        identified.append(index)
        for key in keys:
            if key in first_by_key:
                union(index, first_by_key[key])
            else:
                first_by_key[key] = index

    components_by_root: dict[int, list[dict[str, Any]]] = {}
    for index in identified:
        components_by_root.setdefault(find(index), []).append(milestones[index])
    return list(components_by_root.values()), anonymous


class FeatureEngineV1NarrowPatch(FeatureEngineV1):
    """Outcome-blind narrow remediation of F02/F06.

    All unchanged F01/F03-F05/F07-F09 semantics are inherited from FeatureEngineV1.
    """

    implementation_version = FEATURE_IMPLEMENTATION_VERSION

    def f02(self, rows: Iterable[dict[str, Any]]):
        f = FEATURE_IDS[1]
        rows = list(rows)
        metric_values: dict[str, dict[str, Decimal]] = {}
        operator_trace: dict[str, dict[str, str]] = {}
        raw_change_trace: dict[str, dict[str, Decimal]] = {}

        for r in rows:
            x = raw(r, f)
            if r["eligibility_state"] != "ELIGIBLE" or not x or explicit(x):
                continue
            cid = r["company_id"]
            operator_trace[cid] = {}
            raw_change_trace[cid] = {}

            changes = x.get("metric_changes")
            if isinstance(changes, dict):
                for metric, spec in changes.items():
                    if spec is None:
                        continue
                    if not isinstance(spec, dict):
                        raise FeatureInputGovernanceError(
                            f"F02 metric_changes[{metric!r}] requires a governed object "
                            "with value + operator_id; ungoverned scalar input is forbidden"
                        )
                    if spec.get("value") is None or not spec.get("operator_id"):
                        raise FeatureInputGovernanceError(
                            f"F02 metric_changes[{metric!r}] missing value/operator_id"
                        )
                    value = D(spec["value"])
                    metric_values.setdefault(metric, {})[cid] = value
                    operator_trace[cid][metric] = str(spec["operator_id"])
                    raw_change_trace[cid][metric] = value

            for metric, pair in (x.get("metric_pairs") or {}).items():
                if not isinstance(pair, dict) or pair.get("current") is None or pair.get("prior") is None:
                    continue
                if "change_mode" not in pair:
                    raise FeatureInputGovernanceError(
                        f"F02 metric_pairs[{metric!r}] missing explicit change_mode"
                    )
                mode = str(pair["change_mode"]).upper()
                current, prior = D(pair["current"]), D(pair["prior"])
                if mode == "ABSOLUTE":
                    value = current - prior
                elif mode == "RELATIVE":
                    if prior == 0:
                        raise FeatureInputGovernanceError(
                            f"F02 metric_pairs[{metric!r}] RELATIVE prior cannot be zero"
                        )
                    value = (current - prior) / abs(prior)
                else:
                    raise FeatureInputGovernanceError(
                        f"F02 metric_pairs[{metric!r}] unsupported change_mode={mode!r}"
                    )
                metric_values.setdefault(metric, {})[cid] = value
                operator_trace[cid][metric] = str(pair.get("operator_id") or mode)
                raw_change_trace[cid][metric] = value

        percentiles = {m: robust_pct(values) for m, values in metric_values.items()}
        out = {}
        for r in rows:
            cid = r["company_id"]
            x = raw(r, f)
            e = explicit(x)
            values = [p[cid] for p in percentiles.values() if cid in p]
            if e:
                out[cid] = na(f, x, *e)
            elif values:
                out[cid] = ok(
                    f,
                    x,
                    med(values),
                    {
                        "metric_percentiles": [str(v) for v in values],
                        "operator_bindings": operator_trace.get(cid, {}),
                        "raw_metric_changes": {
                            k: str(v) for k, v in raw_change_trace.get(cid, {}).items()
                        },
                    },
                )
            else:
                out[cid] = na(f, x, "NOT_FOUND", "no valid governed realized metric")
        return out

    def f06(self, r: dict[str, Any]):
        f = FEATURE_IDS[5]
        x = raw(r, f)
        e = explicit(x)
        if not x:
            return na(f, x)
        if e:
            return na(f, x, *e)
        if not x.get("retrieval_complete"):
            return na(f, x, "NOT_FOUND", "runway retrieval incomplete")

        anchor = parse_date(r["window_anchor_date"])
        end = add_calendar_months(anchor, 3)
        in_horizon = [
            m for m in x.get("milestones", [])
            if m.get("date") and anchor < parse_date(m["date"]) <= end
        ]
        if not in_horizon:
            return ok(f, x, 20, {"milestones_in_horizon": 0})

        components, anonymous = _identity_components(in_horizon)
        accepted = lambda m: bool(m.get("verified")) and m.get("source_tier") in {"S1", "S2", "S3"}
        verified_components = [component for component in components if any(accepted(m) for m in component)]
        verified_anonymous = [m for m in anonymous if accepted(m)]
        duplicate_count = sum(len(component) - 1 for component in components)

        # Sequential credit requires two separately governed identity components.
        # A component with internally conflicting step/date labels is not used to
        # establish the sequential predicate.
        sequential_pairs: list[tuple[str, str]] = []
        for component in verified_components:
            steps = {
                str(m.get("conversion_step")).strip()
                for m in component
                if m.get("conversion_step") is not None and str(m.get("conversion_step")).strip()
            }
            dates = {str(m.get("date")) for m in component if m.get("date") is not None}
            if len(steps) == 1 and len(dates) == 1:
                sequential_pairs.append((next(iter(steps)), next(iter(dates))))
        step_values = {step for step, _ in sequential_pairs}
        step_dates = {date for _, date in sequential_pairs}
        sequential_verified = (
            bool(x.get("sequential_conversion_steps"))
            and len(verified_components) >= 2
            and len(sequential_pairs) >= 2
            and len(step_values) >= 2
            and len(step_dates) >= 2
        )

        if len(verified_components) >= 2 and sequential_verified:
            score = 100
        elif len(verified_components) >= 2:
            score = 90
        elif verified_components or verified_anonymous:
            score = 70
        else:
            score = 40

        supplier_only = bool(in_horizon) and all(m.get("supplier_only", False) for m in in_horizon)
        if supplier_only:
            score = min(score, 70)

        return ok(
            f,
            x,
            score,
            {
                "milestones_in_horizon": len(in_horizon),
                "deduped_milestones": len(components) + len(anonymous),
                "duplicate_milestones_removed": duplicate_count,
                "verified_count": len(verified_components) + len(verified_anonymous),
                "independent_verified_count": len(verified_components),
                "anonymous_verified_count": len(verified_anonymous),
                "distinct_conversion_steps": len(step_values),
                "sequential_verified": sequential_verified,
                "supplier_only": supplier_only,
                "independence_identity_rule": (
                    "CONNECTED_COMPONENTS_OVER_NAMESPACED_"
                    "milestone_id|event_group_id|evidence_group_id;anonymous_not_independent"
                ),
            },
        )
