from __future__ import annotations

from typing import Any, Mapping, Sequence

from tools.m3top3.core import deterministic_id, sha256_hex
from tools.m3top3.pit_guard import PITGuard

from .contracts import (
    AssessedCandidate,
    CandidateInput,
    CandidateRecallStage,
    ConfidenceRiskAssessmentStage,
    EligibilityState,
    EvidenceState,
    RankabilityDisposition,
    RankedCandidate,
    RecallDisposition,
    RecalledCandidate,
    SetConstructionResult,
    SetConstructionStage,
    SetDecisionAction,
    SetDisposition,
    SetPolicy,
    TailRankingStage,
    WorkbenchInvariantError,
    axis_to_mapping,
    eligibility_to_mapping,
    utf8_key,
    validate_and_parse_envelope,
)


def _sorted_unique(values: Sequence[str]) -> list[str]:
    return sorted(set(values), key=utf8_key)


class IdentityCandidateRecall(CandidateRecallStage):
    """Development-only recall adapter that preserves every supplied identity."""

    def recall(
        self, candidates: Sequence[CandidateInput]
    ) -> tuple[RecalledCandidate, ...]:
        return tuple(
            RecalledCandidate(
                candidate=candidate,
                disposition=RecallDisposition.RECALLED_IDENTITY_PRESERVED,
            )
            for candidate in candidates
        )


class OpportunityTailRanker(TailRankingStage):
    """Ranks only VERIFIED opportunity values using the frozen total tie key."""

    def rank(
        self, recalled: Sequence[RecalledCandidate], policy: SetPolicy
    ) -> tuple[
        tuple[RankedCandidate, ...], Mapping[str, tuple[str, ...]]
    ]:
        rankable: list[RecalledCandidate] = []
        reasons: dict[str, tuple[str, ...]] = {}
        for item in recalled:
            candidate = item.candidate
            if (
                candidate.opportunity.evidence_state
                is policy.opportunity_state_required_for_raw_rank
            ):
                if candidate.opportunity.value is None:
                    raise WorkbenchInvariantError(
                        "VERIFIED opportunity reached ranker without a decimal value"
                    )
                rankable.append(item)
                reasons[candidate.candidate_id] = ()
            else:
                state = candidate.opportunity.evidence_state.value
                reasons[candidate.candidate_id] = (
                    f"OPPORTUNITY_STATE_{state}_NOT_VERIFIED",
                )

        ordered = sorted(
            rankable,
            key=lambda item: (
                -item.candidate.opportunity.value,  # type: ignore[operator]
                utf8_key(item.candidate.candidate_id),
                utf8_key(item.candidate.pit_snapshot_id),
            ),
        )
        ranked: list[RankedCandidate] = []
        for raw_rank, item in enumerate(ordered, 1):
            score = item.candidate.opportunity.value
            if score is None:
                raise WorkbenchInvariantError("rankable opportunity value disappeared")
            canonical_score = format(score, "f")
            ranked.append(
                RankedCandidate(
                    recalled=item,
                    raw_rank=raw_rank,
                    raw_score=score,
                    tie_group=deterministic_id(
                        "tie", {"opportunity_decimal": canonical_score}
                    ),
                    tie_break_key=(
                        format(-score, "f"),
                        item.candidate.candidate_id.encode("utf-8").hex(),
                        item.candidate.pit_snapshot_id.encode("utf-8").hex(),
                    ),
                )
            )
        return tuple(ranked), reasons


class IdentityConfidenceRiskAssessment(ConfidenceRiskAssessmentStage):
    """Preserves confidence and risk after ranking without score mutation."""

    def assess(
        self, ranked: Sequence[RankedCandidate]
    ) -> tuple[AssessedCandidate, ...]:
        return tuple(
            AssessedCandidate(
                ranked=item,
                confidence=item.recalled.candidate.confidence,
                risk=item.recalled.candidate.risk,
            )
            for item in ranked
        )


class FailClosedSetConstructor(SetConstructionStage):
    """Applies only the frozen explicit gates and records every scan decision."""

    @staticmethod
    def _gate_reasons(
        item: AssessedCandidate, policy: SetPolicy
    ) -> list[str]:
        candidate = item.ranked.recalled.candidate
        reasons: list[str] = []
        if candidate.eligibility.state is not policy.eligibility_required:
            reasons.append(
                f"ELIGIBILITY_STATE_{candidate.eligibility.state.value}_NOT_ALLOWED"
            )
            reasons.extend(candidate.eligibility.reason_codes)
        if item.confidence.evidence_state not in policy.allowed_confidence_states:
            reasons.append(
                f"CONFIDENCE_STATE_{item.confidence.evidence_state.value}_NOT_ALLOWED"
            )
            reasons.extend(item.confidence.reason_codes)
        if item.risk.evidence_state not in policy.allowed_risk_states:
            reasons.append(
                f"RISK_STATE_{item.risk.evidence_state.value}_NOT_ALLOWED"
            )
            reasons.extend(item.risk.reason_codes)
        return _sorted_unique(reasons)

    def construct(
        self, assessed: Sequence[AssessedCandidate], policy: SetPolicy
    ) -> SetConstructionResult:
        selected: list[dict[str, Any]] = []
        decisions: list[dict[str, Any]] = []
        dispositions: dict[str, dict[str, Any]] = {}
        pending_skip_ids: list[str] = []
        pending_skip_decision_indexes: list[int] = []

        for item in assessed:
            if len(selected) >= policy.set_size:
                break
            ranked = item.ranked
            candidate = ranked.recalled.candidate
            candidate_id = candidate.candidate_id
            slot = len(selected) + 1
            gate_reasons = self._gate_reasons(item, policy)
            if gate_reasons:
                decision = {
                    "decision_index": len(decisions) + 1,
                    "action": SetDecisionAction.SKIPPED.value,
                    "candidate_id": candidate_id,
                    "raw_rank": ranked.raw_rank,
                    "slot": slot,
                    "reason_codes": gate_reasons,
                    "replacement_candidate_id": None,
                }
                decisions.append(decision)
                pending_skip_ids.append(candidate_id)
                pending_skip_decision_indexes.append(len(decisions) - 1)
                dispositions[candidate_id] = {
                    "set_disposition": SetDisposition.SKIPPED.value,
                    "set_position": None,
                    "reason_codes": gate_reasons,
                }
                continue

            action = (
                SetDecisionAction.SUBSTITUTED
                if pending_skip_ids
                else SetDecisionAction.SELECTED
            )
            decision_reasons = (
                ["FILLED_SLOT_AFTER_HIGHER_RANK_SKIPS"]
                if pending_skip_ids
                else ["POLICY_GATES_PASSED"]
            )
            selected_row = {
                "set_position": slot,
                "candidate_id": candidate_id,
                "company_id": candidate.company_id,
                "security_code": candidate.security_code,
                "pit_snapshot_id": candidate.pit_snapshot_id,
                "raw_rank": ranked.raw_rank,
                "raw_score": format(ranked.raw_score, "f"),
            }
            selected.append(selected_row)
            decisions.append(
                {
                    "decision_index": len(decisions) + 1,
                    "action": action.value,
                    "candidate_id": candidate_id,
                    "raw_rank": ranked.raw_rank,
                    "slot": slot,
                    "reason_codes": decision_reasons,
                    "substitutes_for_candidate_ids": list(pending_skip_ids),
                }
            )
            for decision_index in pending_skip_decision_indexes:
                decisions[decision_index]["replacement_candidate_id"] = candidate_id
            dispositions[candidate_id] = {
                "set_disposition": SetDisposition.SELECTED.value,
                "set_position": slot,
                "reason_codes": decision_reasons,
            }
            pending_skip_ids = []
            pending_skip_decision_indexes = []

        for item in assessed:
            candidate_id = item.ranked.recalled.candidate.candidate_id
            if candidate_id not in dispositions:
                dispositions[candidate_id] = {
                    "set_disposition": SetDisposition.NOT_SCANNED_CAPACITY_REACHED.value,
                    "set_position": None,
                    "reason_codes": ["SET_CAPACITY_REACHED"],
                }

        first_unfilled_slot = len(selected) + 1
        for slot in range(first_unfilled_slot, policy.set_size + 1):
            decisions.append(
                {
                    "decision_index": len(decisions) + 1,
                    "action": SetDecisionAction.UNFILLED.value,
                    "candidate_id": None,
                    "raw_rank": None,
                    "slot": slot,
                    "reason_codes": ["NO_PASSING_CANDIDATE_AVAILABLE"],
                    "skipped_candidate_ids": (
                        list(pending_skip_ids) if slot == first_unfilled_slot else []
                    ),
                }
            )

        return SetConstructionResult(
            selected_set=tuple(selected),
            decision_log=tuple(decisions),
            dispositions=dispositions,
        )


class ForwardModelWorkbench:
    """Outcome-nonresponsive, in-memory reference workbench v0.1."""

    def __init__(
        self,
        *,
        recall: CandidateRecallStage | None = None,
        ranker: TailRankingStage | None = None,
        assessor: ConfidenceRiskAssessmentStage | None = None,
        set_constructor: SetConstructionStage | None = None,
        pit_guard: PITGuard | None = None,
    ) -> None:
        self._recall = recall or IdentityCandidateRecall()
        self._ranker = ranker or OpportunityTailRanker()
        self._assessor = assessor or IdentityConfidenceRiskAssessment()
        self._set_constructor = set_constructor or FailClosedSetConstructor()
        self._pit_guard = pit_guard or PITGuard()

    @staticmethod
    def _policy_mapping(policy: SetPolicy) -> dict[str, Any]:
        return {
            "policy_id": policy.policy_id,
            "set_size": policy.set_size,
            "eligibility_required": policy.eligibility_required.value,
            "allowed_confidence_states": [
                item.value for item in policy.allowed_confidence_states
            ],
            "allowed_risk_states": [item.value for item in policy.allowed_risk_states],
            "opportunity_state_required_for_raw_rank": (
                policy.opportunity_state_required_for_raw_rank.value
            ),
        }

    @staticmethod
    def _semantic_input(normalized_input: Mapping[str, Any]) -> dict[str, Any]:
        candidates = []
        for candidate in normalized_input["candidates"]:
            candidates.append(
                {key: value for key, value in candidate.items() if key != "metadata"}
            )
        return {
            **normalized_input,
            "candidates": candidates,
        }

    @staticmethod
    def _raw_ranking_mapping(
        ranked: Sequence[RankedCandidate],
    ) -> list[dict[str, Any]]:
        return [
            {
                "candidate_id": item.recalled.candidate.candidate_id,
                "company_id": item.recalled.candidate.company_id,
                "security_code": item.recalled.candidate.security_code,
                "pit_snapshot_id": item.recalled.candidate.pit_snapshot_id,
                "raw_rank": item.raw_rank,
                "raw_score": format(item.raw_score, "f"),
                "tie_group": item.tie_group,
                "tie_break_key": list(item.tie_break_key),
            }
            for item in ranked
        ]

    @staticmethod
    def _candidate_traces(
        *,
        candidates: Sequence[CandidateInput],
        recalled: Sequence[RecalledCandidate],
        ranked: Sequence[RankedCandidate],
        rank_reasons: Mapping[str, tuple[str, ...]],
        set_result: SetConstructionResult,
        policy: SetPolicy,
    ) -> list[dict[str, Any]]:
        recall_by_id = {
            item.candidate.candidate_id: item.disposition.value for item in recalled
        }
        ranked_by_id = {
            item.recalled.candidate.candidate_id: item for item in ranked
        }
        policy_surface = ForwardModelWorkbench._policy_mapping(policy)
        traces: list[dict[str, Any]] = []
        for candidate in sorted(candidates, key=lambda item: utf8_key(item.candidate_id)):
            candidate_id = candidate.candidate_id
            ranked_item = ranked_by_id.get(candidate_id)
            if ranked_item is None:
                rankability = RankabilityDisposition.UNRANKED.value
                set_disposition = SetDisposition.UNRANKED.value
                set_position = None
                set_reasons: Sequence[str] = ()
                raw_rank = None
            else:
                rankability = RankabilityDisposition.RANKED.value
                set_info = set_result.dispositions[candidate_id]
                set_disposition = set_info["set_disposition"]
                set_position = set_info["set_position"]
                set_reasons = set_info["reason_codes"]
                raw_rank = ranked_item.raw_rank
            reasons = _sorted_unique(
                [*rank_reasons.get(candidate_id, ()), *set_reasons]
            )
            trace = {
                "candidate_id": candidate_id,
                "company_id": candidate.company_id,
                "security_code": candidate.security_code,
                "pit_snapshot_id": candidate.pit_snapshot_id,
                "opportunity": axis_to_mapping(candidate.opportunity),
                "confidence": axis_to_mapping(candidate.confidence),
                "risk": axis_to_mapping(candidate.risk),
                "eligibility": eligibility_to_mapping(candidate.eligibility),
                "set_policy": policy_surface,
                "recall_disposition": recall_by_id[candidate_id],
                "rankability_disposition": rankability,
                "set_disposition": set_disposition,
                "raw_rank": raw_rank,
                "set_position": set_position,
                "reason_codes": reasons,
            }
            traces.append(trace)
        return traces

    @staticmethod
    def _assert_accounting(
        *,
        candidates: Sequence[CandidateInput],
        traces: Sequence[Mapping[str, Any]],
        ranked: Sequence[RankedCandidate],
        selected_set: Sequence[Mapping[str, Any]],
    ) -> dict[str, Any]:
        input_ids = sorted((item.candidate_id for item in candidates), key=utf8_key)
        trace_ids = sorted((str(item["candidate_id"]) for item in traces), key=utf8_key)
        selected_ids = {str(item["candidate_id"]) for item in selected_set}
        skipped_rows = sum(
            1
            for item in traces
            if item["set_disposition"] == SetDisposition.SKIPPED.value
        )
        identity_match = input_ids == trace_ids
        accounting = {
            "input_rows": len(candidates),
            "terminal_trace_rows": len(traces),
            "ranked_rows": len(ranked),
            "unranked_rows": len(candidates) - len(ranked),
            "selected_rows": len(selected_set),
            "skipped_rows": skipped_rows,
            "input_terminal_identity_match": identity_match,
        }
        if not identity_match:
            raise WorkbenchInvariantError("input and terminal trace identities differ")
        if accounting["input_rows"] != accounting["terminal_trace_rows"]:
            raise WorkbenchInvariantError("input and terminal trace counts differ")
        if accounting["ranked_rows"] + accounting["unranked_rows"] != accounting[
            "input_rows"
        ]:
            raise WorkbenchInvariantError("ranked/unranked accounting does not close")
        if not selected_ids.issubset(set(input_ids)):
            raise WorkbenchInvariantError("selected set contains a synthetic identity")
        for trace in traces:
            if trace["candidate_id"] not in selected_ids and not trace["reason_codes"]:
                raise WorkbenchInvariantError(
                    "a nonselected candidate has no terminal reason code"
                )
        return accounting

    def run(self, envelope: Mapping[str, Any]) -> dict[str, Any]:
        parsed = validate_and_parse_envelope(envelope, pit_guard=self._pit_guard)
        recalled = self._recall.recall(parsed.candidates)
        if tuple(item.candidate for item in recalled) != tuple(parsed.candidates):
            raise WorkbenchInvariantError(
                "candidate recall did not preserve every input row and ordering"
            )

        ranked, rank_reasons = self._ranker.rank(recalled, parsed.set_policy)
        assessed = self._assessor.assess(ranked)
        if tuple(item.ranked for item in assessed) != tuple(ranked):
            raise WorkbenchInvariantError("assessment stage changed raw ranking")
        set_result = self._set_constructor.construct(assessed, parsed.set_policy)

        raw_ranking = self._raw_ranking_mapping(ranked)
        candidate_traces = self._candidate_traces(
            candidates=parsed.candidates,
            recalled=recalled,
            ranked=ranked,
            rank_reasons=rank_reasons,
            set_result=set_result,
            policy=parsed.set_policy,
        )
        selected_set = [dict(item) for item in set_result.selected_set]
        accounting = self._assert_accounting(
            candidates=parsed.candidates,
            traces=candidate_traces,
            ranked=ranked,
            selected_set=selected_set,
        )

        normalized_input = parsed.normalized_input
        config = {
            "workbench_schema_version": parsed.workbench_schema_version,
            "fixture_class": parsed.fixture_class,
            "set_policy": self._policy_mapping(parsed.set_policy),
        }
        semantic_input = self._semantic_input(normalized_input)
        result: dict[str, Any] = {
            "workbench_schema_version": parsed.workbench_schema_version,
            "workbench_run_id": deterministic_id(
                "mwb",
                {
                    "semantic_input": semantic_input,
                    "config_digest": sha256_hex(config),
                },
            ),
            "input_digest": sha256_hex(normalized_input),
            "config_digest": sha256_hex(config),
            "fixture_class": parsed.fixture_class,
            "guard_state": "PASS",
            "candidate_traces": candidate_traces,
            "raw_ranking": raw_ranking,
            "selected_set": selected_set,
            "set_decision_log": [dict(item) for item in set_result.decision_log],
            "accounting": accounting,
        }
        result["result_digest"] = sha256_hex(result)
        return result


def run_workbench(envelope: Mapping[str, Any]) -> dict[str, Any]:
    return ForwardModelWorkbench().run(envelope)
