from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path
from typing import Any


ORACLE_VERSION = "M3TOP3-GOLDEN-SCORE-ORACLE-v1.0-INDEPENDENT-FORMULA"
AXES = {
    "Business_Momentum": (("F01", Decimal("15")), ("F02", Decimal("10"))),
    "Expectation_Surprise": (("F03", Decimal("15")), ("F04", Decimal("10"))),
    "Market_Positioning": (("F05", Decimal("20")),),
    "Forward_Runway": (("F06", Decimal("12")), ("F07", Decimal("8"))),
    "Reliability_Risk": (("F08", Decimal("5")), ("F09", Decimal("5"))),
}
AXIS_WEIGHTS = {
    "Business_Momentum": Decimal("25"),
    "Expectation_Surprise": Decimal("25"),
    "Market_Positioning": Decimal("20"),
    "Forward_Runway": Decimal("20"),
    "Reliability_Risk": Decimal("10"),
}


class GoldenOracleError(ValueError):
    pass


def _fmt(value: Decimal | None) -> str | None:
    return None if value is None else format(value.quantize(Decimal("0.01")), "f")


def independent_score(feature_scores: dict[str, Any], gate_state: str | None) -> dict[str, Any]:
    axis_scores: dict[str, Decimal | None] = {}
    for axis, components in AXES.items():
        available = [
            (weight, Decimal(str(feature_scores[feature_id])))
            for feature_id, weight in components
            if feature_scores.get(feature_id) is not None
        ]
        if not available:
            axis_scores[axis] = None
            continue
        axis_scores[axis] = sum((weight * score for weight, score in available), Decimal("0")) / sum(
            (weight for weight, _ in available), Decimal("0")
        )
    opportunity_available = any(
        axis_scores[axis] is not None
        for axis in ("Business_Momentum", "Expectation_Surprise", "Market_Positioning", "Forward_Runway")
    )
    if not opportunity_available:
        return {
            "axis_scores": {axis: _fmt(score) for axis, score in axis_scores.items()},
            "pre_gate_score": None,
            "final_score": None,
            "score_status": "INSUFFICIENT_INPUT",
        }
    available_axes = [(AXIS_WEIGHTS[axis], score) for axis, score in axis_scores.items() if score is not None]
    pre = sum((weight * score for weight, score in available_axes), Decimal("0")) / sum(
        (weight for weight, _ in available_axes), Decimal("0")
    )
    if gate_state is None:
        final = None
        status = "CONTROL_GAP_GATE_NOT_BOUND"
    elif gate_state == "NONE":
        final = pre
        status = "RANKABLE"
    else:
        raise GoldenOracleError(f"oracle fixture gate not supported: {gate_state!r}")
    return {
        "axis_scores": {axis: _fmt(score) for axis, score in axis_scores.items()},
        "pre_gate_score": _fmt(pre),
        "final_score": _fmt(final),
        "score_status": status,
    }


def _rank(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rankable = [row for row in rows if row["final_score"] is not None]
    rankable.sort(key=lambda row: (-Decimal(row["final_score"]), row["company_id"]))
    return [
        {
            **row,
            "exact_rank": rank,
            "top3": rank <= 3,
            "top10": rank <= 10,
        }
        for rank, row in enumerate(rankable, start=1)
    ]


def derive_selected_expectations(fixture_document: dict[str, Any]) -> dict[str, Any]:
    fixtures = {fixture["fixture_id"]: fixture for fixture in fixture_document["fixtures"]}
    result: dict[str, Any] = {"oracle_version": ORACLE_VERSION, "fixtures": {}}

    fx08 = fixtures["AAA-M3TOP3-GR-FX-08"]["controlled_payload"]
    fx08_rows = []
    for row in fx08.values():
        score = independent_score(row["feature_scores"], row.get("risk_gate_state"))
        fx08_rows.append({"company_id": row["company_id"], **score})
    result["fixtures"]["AAA-M3TOP3-GR-FX-08"] = {
        "state": "EXACT_BOUND",
        "rows": _rank(fx08_rows),
        "coverage": "1.00",
    }

    fx09 = fixtures["AAA-M3TOP3-GR-FX-09"]["controlled_payload"]["rows"]
    fx09_rows = []
    for row in fx09:
        score = independent_score(row["feature_scores"], None)
        fx09_rows.append({"company_id": row["company_id"], **score})
    result["fixtures"]["AAA-M3TOP3-GR-FX-09"] = {
        "state": "CONTROL_GAP_NOT_EXACTLY_BOUND",
        "rows": fx09_rows,
        "certain_snapshot_state": "INCOMPLETE_COVERAGE",
        "conditional_feature_rankability": "2/3",
        "gap": [
            "risk_gate_state missing for all rows",
            "eligibility uses non-contract field/value eligibility='TRUE'",
            "fixture absent from authorized_fixture_ids",
        ],
    }

    for fixture_id, company_id in (
        ("AAA-M3TOP3-GR-FX-12", "KRX:319660"),
        ("AAA-M3TOP3-GR-FX-13", "KRX:084370"),
    ):
        payload = fixtures[fixture_id]["controlled_payload"]
        result["fixtures"][fixture_id] = {
            "state": "EXACT_SCORE_ARITHMETIC_BOUND_RANKING_OUT_OF_SCOPE",
            "company_id": company_id,
            **independent_score(payload["feature_scores"], payload.get("risk_gate_state")),
        }

    fx14 = fixtures["AAA-M3TOP3-GR-FX-14"]["controlled_payload"]["rows"]
    fx14_rows = []
    for row in fx14:
        score = independent_score(row["feature_scores"], row.get("risk_gate_state"))
        fx14_rows.append({"company_id": row["company_id"], **score})
    result["fixtures"]["AAA-M3TOP3-GR-FX-14"] = {
        "state": "EXACT_BOUND",
        "rows": _rank(fx14_rows),
        "top3_set": [row["company_id"] for row in _rank(fx14_rows) if row["top3"]],
        "top10_diagnostic_view": [row["company_id"] for row in _rank(fx14_rows) if row["top10"]],
        "coverage": "1.00",
    }
    return result


def verify_expected_binding(fixture_path: str | Path, expected_path: str | Path) -> dict[str, Any]:
    fixture_document = json.loads(Path(fixture_path).read_text(encoding="utf-8"))
    expected = json.loads(Path(expected_path).read_text(encoding="utf-8"))
    derived = derive_selected_expectations(fixture_document)
    if expected["oracle_version"] != derived["oracle_version"]:
        raise GoldenOracleError("Golden oracle version mismatch")
    if expected["fixtures"] != derived["fixtures"]:
        raise GoldenOracleError("Golden expected binding differs from independent contract arithmetic")
    return {
        "state": "PASS_WITH_EXPLICIT_GF09_CONTROL_GAP",
        "exact_fixture_ids": [
            "AAA-M3TOP3-GR-FX-08",
            "AAA-M3TOP3-GR-FX-12",
            "AAA-M3TOP3-GR-FX-13",
            "AAA-M3TOP3-GR-FX-14",
        ],
        "control_gap_fixture_ids": ["AAA-M3TOP3-GR-FX-09"],
    }
