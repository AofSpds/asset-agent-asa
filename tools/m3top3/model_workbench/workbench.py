from __future__ import annotations

from decimal import Decimal
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


def _descending_decimal_text(value: Decimal) -> str:
    """Serialize the additive inverse exactly without Decimal arithmetic."""

    canonical = format(value, "f")
    if value.is_zero():
        return "0"
    if canonical.startswith("-"):
        return canonical[1:]
    return f"-{canonical}"


def _opportunity_value(item: RecalledCandidate) -> Decimal:
    value = item.candidate.opportunity.value
    if value is None:
        raise WorkbenchInvariantError(
            "VERIFIED opportunity reached ranker without a decimal value"
        )
    return value


def _snapshot_stage_value(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _snapshot_stage_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_snapshot_stage_value(item) for item in value]
    return value


def _snapshot_stage_rows(value: Any, surface: str) -> tuple[dict[str, Any], ...]:
    if not isinstance(value, (list, tuple)):
        raise WorkbenchInvariantError(f"{surface} must be a list or tuple of mappings")
    rows: list[dict[str, Any]] = []
    for index, row in enumerate(value):
        if not isinstance(row, Mapping):
            raise WorkbenchInvariantError(f"{surface}[{index}] must be a mapping")
        snapshot = _snapshot_stage_value(row)
        if not isinstance(snapshot, dict):
            raise WorkbenchInvariantError(f"{surface}[{index}] snapshot failed")
        rows.append(snapshot)
    return tuple(rows)


def _validated_string_list(value: Any, surface: str) -> list[str]:
    if not isinstance(value, list):
        raise WorkbenchInvariantError(f"{surface} must be a list")
    if any(not isinstance(item, str) or not item for item in value):
        raise WorkbenchInvariantError(f"{surface} must contain nonempty strings")
    if len(set(value)) != len(value):
        raise WorkbenchInvariantError(f"{surface} must not contain duplicates")
    return value


def _validated_reason_codes(value: Any, surface: str) -> list[str]:
    reasons = _validated_string_list(value, surface)
    if not reasons:
        raise WorkbenchInvariantError(f"{surface} must not be empty")
    if reasons != sorted(reasons, key=utf8_key):
        raise WorkbenchInvariantError(f"{surface} must be in canonical order")
    return reasons


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
    """Ranks only Opportunity-owned VERIFIED values with the frozen tie rule."""

    def rank(
        self, recalled: Sequence[RecalledCandidate]
    ) -> tuple[
        tuple[RankedCandidate, ...], Mapping[str, tuple[str, ...]]
    ]:
        rankable: list[RecalledCandidate] = []
        reasons: dict[str, tuple[str, ...]] = {}
        for item in recalled:
            candidate = item.candidate
            if candidate.opportunity.evidence_state is EvidenceState.VERIFIED:
                _opportunity_value(item)
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
                utf8_key(item.candidate.candidate_id),
                utf8_key(item.candidate.pit_snapshot_id),
            ),
        )
        ordered.sort(key=_opportunity_value, reverse=True)
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
                        _descending_decimal_text(score),
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
        self._pit_guard_extension = pit_guard

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
    def _snapshot_and_validate_set_result(
        *,
        set_result: SetConstructionResult,
        ranked: Sequence[RankedCandidate],
        policy: SetPolicy,
    ) -> SetConstructionResult:
        if not isinstance(set_result, SetConstructionResult):
            raise WorkbenchInvariantError(
                "set construction stage must return SetConstructionResult"
            )

        selected = _snapshot_stage_rows(set_result.selected_set, "selected_set")
        decisions = _snapshot_stage_rows(set_result.decision_log, "decision_log")
        if not isinstance(set_result.dispositions, Mapping):
            raise WorkbenchInvariantError("dispositions must be a mapping")
        dispositions = _snapshot_stage_value(set_result.dispositions)
        if not isinstance(dispositions, dict):
            raise WorkbenchInvariantError("dispositions snapshot failed")

        canonical_ids = [
            item.recalled.candidate.candidate_id for item in ranked
        ]
        canonical_ranks = [item.raw_rank for item in ranked]
        if len(set(canonical_ids)) != len(canonical_ids):
            raise WorkbenchInvariantError("canonical ranking contains duplicate identities")
        if canonical_ranks != list(range(1, len(ranked) + 1)):
            raise WorkbenchInvariantError("canonical ranking ranks are not contiguous")
        canonical_by_id = {
            item.recalled.candidate.candidate_id: item for item in ranked
        }

        selected_keys = {
            "set_position",
            "candidate_id",
            "company_id",
            "security_code",
            "pit_snapshot_id",
            "raw_rank",
            "raw_score",
        }
        if len(selected) > policy.set_size:
            raise WorkbenchInvariantError("selected_set exceeds configured set_size")
        selected_ids: list[str] = []
        selected_ranks: list[int] = []
        for index, row in enumerate(selected, 1):
            surface = f"selected_set[{index - 1}]"
            if not selected_keys.issubset(row):
                raise WorkbenchInvariantError(f"{surface} has an invalid shape")
            candidate_id = row["candidate_id"]
            if not isinstance(candidate_id, str) or candidate_id not in canonical_by_id:
                raise WorkbenchInvariantError(
                    f"{surface} identity is not in the canonical ranking"
                )
            if candidate_id in selected_ids:
                raise WorkbenchInvariantError("selected_set contains a duplicate identity")
            if type(row["set_position"]) is not int or row["set_position"] != index:
                raise WorkbenchInvariantError(
                    "selected_set positions must be unique and contiguous"
                )
            ranked_item = canonical_by_id[candidate_id]
            candidate = ranked_item.recalled.candidate
            expected = {
                "set_position": index,
                "candidate_id": candidate_id,
                "company_id": candidate.company_id,
                "security_code": candidate.security_code,
                "pit_snapshot_id": candidate.pit_snapshot_id,
                "raw_rank": ranked_item.raw_rank,
                "raw_score": format(ranked_item.raw_score, "f"),
            }
            if type(row["raw_rank"]) is not int or any(
                row[key] != expected[key] for key in selected_keys
            ):
                raise WorkbenchInvariantError(
                    f"{surface} does not match its canonical ranked row"
                )
            selected_ids.append(candidate_id)
            selected_ranks.append(ranked_item.raw_rank)
        if selected_ranks != sorted(selected_ranks):
            raise WorkbenchInvariantError(
                "selected_set does not preserve canonical rank order"
            )

        action_values = {item.value for item in SetDecisionAction}
        candidate_decisions: list[dict[str, Any]] = []
        unfilled_decisions: list[dict[str, Any]] = []
        decision_candidate_ids: set[str] = set()
        saw_unfilled = False
        for index, row in enumerate(decisions, 1):
            surface = f"decision_log[{index - 1}]"
            action = row.get("action")
            if not isinstance(action, str) or action not in action_values:
                raise WorkbenchInvariantError(f"{surface} has an invalid action")
            common_keys = {
                "decision_index",
                "action",
                "candidate_id",
                "raw_rank",
                "slot",
                "reason_codes",
            }
            action_key = (
                "replacement_candidate_id"
                if action == SetDecisionAction.SKIPPED.value
                else "skipped_candidate_ids"
                if action == SetDecisionAction.UNFILLED.value
                else "substitutes_for_candidate_ids"
            )
            if not (common_keys | {action_key}).issubset(row):
                raise WorkbenchInvariantError(f"{surface} has an invalid shape")
            if type(row["decision_index"]) is not int or row["decision_index"] != index:
                raise WorkbenchInvariantError(
                    "decision indexes must be unique and contiguous"
                )
            if (
                type(row["slot"]) is not int
                or row["slot"] < 1
                or row["slot"] > policy.set_size
            ):
                raise WorkbenchInvariantError(f"{surface} has an invalid slot")
            _validated_reason_codes(row["reason_codes"], f"{surface}.reason_codes")

            if action == SetDecisionAction.UNFILLED.value:
                saw_unfilled = True
                if row["candidate_id"] is not None or row["raw_rank"] is not None:
                    raise WorkbenchInvariantError(
                        "UNFILLED decisions must have null candidate_id and raw_rank"
                    )
                _validated_string_list(
                    row["skipped_candidate_ids"],
                    f"{surface}.skipped_candidate_ids",
                )
                unfilled_decisions.append(row)
                continue

            if saw_unfilled:
                raise WorkbenchInvariantError(
                    "candidate decisions must not follow an UNFILLED decision"
                )
            candidate_id = row["candidate_id"]
            if not isinstance(candidate_id, str) or candidate_id not in canonical_by_id:
                raise WorkbenchInvariantError(
                    f"{surface} identity is not in the canonical ranking"
                )
            if candidate_id in decision_candidate_ids:
                raise WorkbenchInvariantError(
                    "decision_log contains a duplicate candidate identity"
                )
            ranked_item = canonical_by_id[candidate_id]
            if type(row["raw_rank"]) is not int or row["raw_rank"] != ranked_item.raw_rank:
                raise WorkbenchInvariantError(
                    f"{surface} raw_rank does not match the canonical ranking"
                )
            if action == SetDecisionAction.SKIPPED.value:
                replacement = row["replacement_candidate_id"]
                if replacement is not None and (
                    not isinstance(replacement, str)
                    or replacement not in canonical_by_id
                ):
                    raise WorkbenchInvariantError(
                        f"{surface} has an invalid replacement identity"
                    )
            else:
                _validated_string_list(
                    row["substitutes_for_candidate_ids"],
                    f"{surface}.substitutes_for_candidate_ids",
                )
            decision_candidate_ids.add(candidate_id)
            candidate_decisions.append(row)

        if [row["raw_rank"] for row in candidate_decisions] != list(
            range(1, len(candidate_decisions) + 1)
        ):
            raise WorkbenchInvariantError(
                "decision_log must scan a contiguous canonical-rank prefix"
            )

        pending_skips: list[dict[str, Any]] = []
        selected_projection: list[tuple[str, int, int]] = []
        selected_count = 0
        for row in candidate_decisions:
            expected_slot = selected_count + 1
            if row["slot"] != expected_slot:
                raise WorkbenchInvariantError(
                    "decision slot contradicts sequential set construction"
                )
            if row["action"] == SetDecisionAction.SKIPPED.value:
                pending_skips.append(row)
                continue
            if selected_count >= policy.set_size:
                raise WorkbenchInvariantError(
                    "decision_log selects beyond configured set_size"
                )
            expected_action = (
                SetDecisionAction.SUBSTITUTED.value
                if pending_skips
                else SetDecisionAction.SELECTED.value
            )
            if row["action"] != expected_action:
                raise WorkbenchInvariantError(
                    "selected decision action contradicts pending skips"
                )
            pending_ids = [item["candidate_id"] for item in pending_skips]
            if row["substitutes_for_candidate_ids"] != pending_ids:
                raise WorkbenchInvariantError(
                    "substitution projection contradicts preceding skips"
                )
            for skipped in pending_skips:
                if skipped["replacement_candidate_id"] != row["candidate_id"]:
                    raise WorkbenchInvariantError(
                        "skip replacement identity contradicts selected decision"
                    )
            selected_projection.append(
                (row["candidate_id"], row["slot"], row["raw_rank"])
            )
            selected_count += 1
            pending_skips = []

        for skipped in pending_skips:
            if skipped["replacement_candidate_id"] is not None:
                raise WorkbenchInvariantError(
                    "unreplaced skip must have a null replacement identity"
                )

        selected_rows_projection = [
            (row["candidate_id"], row["set_position"], row["raw_rank"])
            for row in selected
        ]
        if selected_rows_projection != selected_projection:
            raise WorkbenchInvariantError(
                "selected_set contradicts SELECTED/SUBSTITUTED decision projection"
            )
        if selected_count < policy.set_size and len(candidate_decisions) != len(ranked):
            raise WorkbenchInvariantError(
                "an underfilled set must account for every canonical ranked row"
            )

        expected_unfilled_slots = list(
            range(selected_count + 1, policy.set_size + 1)
        )
        if [row["slot"] for row in unfilled_decisions] != expected_unfilled_slots:
            raise WorkbenchInvariantError(
                "UNFILLED decisions do not cover every remaining set slot"
            )
        pending_ids = [item["candidate_id"] for item in pending_skips]
        for index, row in enumerate(unfilled_decisions):
            expected_skips = pending_ids if index == 0 else []
            if row["skipped_candidate_ids"] != expected_skips:
                raise WorkbenchInvariantError(
                    "UNFILLED skipped-candidate projection is inconsistent"
                )
            if row["reason_codes"] != ["NO_PASSING_CANDIDATE_AVAILABLE"]:
                raise WorkbenchInvariantError(
                    "UNFILLED decision has noncanonical reason codes"
                )
        covered_slots = [row["set_position"] for row in selected] + [
            row["slot"] for row in unfilled_decisions
        ]
        if covered_slots != list(range(1, policy.set_size + 1)):
            raise WorkbenchInvariantError(
                "selected and UNFILLED rows do not cover configured set slots"
            )

        if set(dispositions) != set(canonical_by_id):
            raise WorkbenchInvariantError(
                "dispositions must cover exactly the canonical ranked identities"
            )
        decisions_by_id = {
            row["candidate_id"]: row for row in candidate_decisions
        }
        disposition_keys = {"set_disposition", "set_position", "reason_codes"}
        for candidate_id in canonical_ids:
            info = dispositions[candidate_id]
            surface = f"dispositions[{candidate_id!r}]"
            if not isinstance(info, Mapping) or not disposition_keys.issubset(info):
                raise WorkbenchInvariantError(f"{surface} has an invalid shape")
            reasons = _validated_reason_codes(
                info["reason_codes"], f"{surface}.reason_codes"
            )
            decision = decisions_by_id.get(candidate_id)
            if decision is None:
                if selected_count != policy.set_size:
                    raise WorkbenchInvariantError(
                        "only capacity-reached identities may lack a decision"
                    )
                expected_disposition = SetDisposition.NOT_SCANNED_CAPACITY_REACHED.value
                expected_position = None
                expected_reasons = ["SET_CAPACITY_REACHED"]
            elif decision["action"] == SetDecisionAction.SKIPPED.value:
                expected_disposition = SetDisposition.SKIPPED.value
                expected_position = None
                expected_reasons = decision["reason_codes"]
            else:
                expected_disposition = SetDisposition.SELECTED.value
                expected_position = decision["slot"]
                expected_reasons = decision["reason_codes"]
            if (
                info["set_disposition"] != expected_disposition
                or info["set_position"] != expected_position
                or reasons != expected_reasons
                or (
                    expected_position is not None
                    and type(info["set_position"]) is not int
                )
            ):
                raise WorkbenchInvariantError(
                    f"{surface} contradicts the decision projection"
                )

        return SetConstructionResult(
            selected_set=selected,
            decision_log=decisions,
            dispositions=dispositions,
        )

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
        parsed = validate_and_parse_envelope(
            envelope, pit_guard=self._pit_guard_extension
        )
        recalled = self._recall.recall(parsed.candidates)
        if tuple(item.candidate for item in recalled) != tuple(parsed.candidates):
            raise WorkbenchInvariantError(
                "candidate recall did not preserve every input row and ordering"
            )

        ranked, rank_reasons = self._ranker.rank(recalled)
        assessed = self._assessor.assess(ranked)
        if tuple(item.ranked for item in assessed) != tuple(ranked):
            raise WorkbenchInvariantError("assessment stage changed raw ranking")
        set_result = self._set_constructor.construct(assessed, parsed.set_policy)
        set_result = self._snapshot_and_validate_set_result(
            set_result=set_result,
            ranked=ranked,
            policy=parsed.set_policy,
        )

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
