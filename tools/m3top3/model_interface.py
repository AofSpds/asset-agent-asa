from __future__ import annotations

import importlib
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Protocol, Sequence

from .core import deterministic_id


@dataclass(frozen=True)
class ScoreResult:
    model_score_id: str
    pit_snapshot_id: str
    company_id: str
    security_code: str
    model_version: str
    total_score: Decimal | None
    evaluation_status: str
    component_trace: list[dict[str, Any]]


class ModelScorer(Protocol):
    model_id: str
    model_version: str
    model_schema_version: str
    feature_set_version: str
    config_hash: str

    def score(self, model_input: dict[str, Any]) -> ScoreResult: ...


class RankingEngine:
    def __init__(self, tie_break_policy: str = "UNRESOLVED_CONTROL"):
        self.tie_break_policy = tie_break_policy

    def rank(self, scores: Sequence[ScoreResult], eligibility: dict[str, str]) -> list[dict[str, Any]]:
        eligible = [s for s in scores if eligibility.get(s.pit_snapshot_id) == "TRUE" and s.total_score is not None]
        if self.tie_break_policy == "UNRESOLVED_CONTROL":
            seen: dict[Decimal, int] = {}
            for s in eligible:
                seen[s.total_score] = seen.get(s.total_score, 0) + 1
            if any(v > 1 for v in seen.values()):
                return [{"status": "BLOCKED_TIE_POLICY_UNRESOLVED", "pit_snapshot_id": s.pit_snapshot_id, "company_id": s.company_id} for s in eligible]
            key = lambda s: (-s.total_score, s.company_id)
        elif self.tie_break_policy == "COMPANY_ID_ASC_DIAGNOSTIC":
            key = lambda s: (-s.total_score, s.company_id)
        else:
            raise ValueError(f"unsupported tie_break_policy: {self.tie_break_policy}")
        ordered = sorted(eligible, key=key)
        out = []
        for i, s in enumerate(ordered, 1):
            out.append({
                "model_score_id": s.model_score_id,
                "pit_snapshot_id": s.pit_snapshot_id,
                "company_id": s.company_id,
                "security_code": s.security_code,
                "model_version": s.model_version,
                "raw_score": str(s.total_score),
                "rank": i,
                "selected_top3": i <= 3,
                "eligibility_at_snapshot": "TRUE",
                "score_component_trace": s.component_trace,
                "status": "EXPERIMENTAL" if self.tie_break_policy.endswith("DIAGNOSTIC") else "WORKING",
            })
        return out


def load_scorer(spec: str, kwargs: dict[str, Any] | None = None) -> ModelScorer:
    module_name, object_name = spec.split(":", 1)
    obj = getattr(importlib.import_module(module_name), object_name)
    return obj(**(kwargs or {}))


class DiagnosticFixtureScorer:
    """Test-only deterministic scorer. Never an official model implementation."""
    model_id = "DIAGNOSTIC_FIXTURE"
    model_version = "diagnostic-v0"
    model_schema_version = "v0.1"
    feature_set_version = "diagnostic"
    config_hash = "diagnostic"

    def score(self, model_input: dict[str, Any]) -> ScoreResult:
        v = model_input.get("feature_values", {}).get("diagnostic_score", "0")
        score = Decimal(str(v))
        sid = deterministic_id("score", {"pit_snapshot_id": model_input["pit_snapshot_id"], "model_version": self.model_version, "score_revision": 0, "score": str(score)})
        return ScoreResult(sid, model_input["pit_snapshot_id"], model_input["company_id"], model_input["security_code"], self.model_version, score, "DIAGNOSTIC", [{"component_id": "diagnostic_score", "contribution": str(score)}])
