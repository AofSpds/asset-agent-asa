from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

from aaa.core.identity import content_sha256
from aaa.state.discrepancy import build_discrepancy_report


KNOWN_CONTINUITY_COLLISION = "AAA-FINDING-CONTINUITY-EVENT-ID-COLLISION_v0.1_WORKING"
VALID_COMPARISON_STATUS = {"MATCH", "MISMATCH", "STALE", "UNKNOWN"}


class InvalidShadowCycle(RuntimeError):
    pass


def _valid_sha(value: str, length: int) -> bool:
    return len(value) == length and all(c in "0123456789abcdef" for c in value)


@dataclass(frozen=True)
class ShadowObservation:
    sequence: int
    observed_at: str
    current_state_path: str
    current_state_sha256: str
    event_ledger_path: str
    event_ledger_sha256: str
    discrepancy_report_sha256: str
    shadow_implementation_commit: str
    shadow_contract_sha256: str
    comparison_status: str
    external_blockers: tuple[str, ...] = ()
    canonical_output: bool = False

    def __post_init__(self) -> None:
        if self.sequence < 1:
            raise InvalidShadowCycle("SEQUENCE_MUST_START_AT_ONE")
        if not self.observed_at or not self.current_state_path or not self.event_ledger_path:
            raise InvalidShadowCycle("OBSERVATION_IDENTITY_FIELDS_REQUIRED")
        for value in (self.current_state_sha256, self.event_ledger_sha256, self.discrepancy_report_sha256, self.shadow_contract_sha256):
            if not _valid_sha(value, 64):
                raise InvalidShadowCycle("INVALID_SHA256")
        if not _valid_sha(self.shadow_implementation_commit, 40):
            raise InvalidShadowCycle("INVALID_IMPLEMENTATION_COMMIT")
        if self.comparison_status not in VALID_COMPARISON_STATUS:
            raise InvalidShadowCycle(f"INVALID_COMPARISON_STATUS:{self.comparison_status}")
        if any(not blocker for blocker in self.external_blockers):
            raise InvalidShadowCycle("EMPTY_EXTERNAL_BLOCKER")
        if self.canonical_output:
            raise InvalidShadowCycle("SHADOW_OUTPUT_MUST_BE_NONCANONICAL")

    @property
    def observation_sha256(self) -> str:
        return content_sha256(asdict(self))


@dataclass(frozen=True)
class ShadowCycleReport:
    cycle_id: str
    observation_count: int
    consecutive_match_count: int
    latest_comparison_status: str
    status: str
    active_external_blockers: tuple[str, ...]
    historical_blockers_seen: tuple[str, ...]
    current_state_sha256: str
    shadow_implementation_commit: str
    shadow_contract_sha256: str
    latest_observation_sha256: str
    binding_drift_seen: bool
    canonical_output: bool = False
    cutover_authorized: bool = False
    historical_repair_performed: bool = False
    ready_for_independent_validation_candidate: bool = False

    @property
    def report_sha256(self) -> str:
        return content_sha256(asdict(self))


def observe_repo(
    repo_root: Path,
    *,
    sequence: int,
    observed_at: str,
    shadow_implementation_commit: str,
    shadow_contract_sha256: str,
    external_blockers: Iterable[str] = (KNOWN_CONTINUITY_COLLISION,),
) -> ShadowObservation:
    report = build_discrepancy_report(repo_root)
    return ShadowObservation(
        sequence=sequence,
        observed_at=observed_at,
        current_state_path=str(report["current_state"]["path"]),
        current_state_sha256=str(report["current_state"]["sha256"]),
        event_ledger_path=str(report["event_ledger"]["path"]),
        event_ledger_sha256=str(report["event_ledger"]["sha256"]),
        discrepancy_report_sha256=str(report["report_sha256"]),
        shadow_implementation_commit=shadow_implementation_commit,
        shadow_contract_sha256=shadow_contract_sha256,
        comparison_status=str(report["status"]),
        external_blockers=tuple(sorted(set(external_blockers))),
    )


def append_observation(
    history: tuple[ShadowObservation, ...],
    observation: ShadowObservation,
) -> tuple[ShadowObservation, ...]:
    if history:
        if observation.observation_sha256 == history[-1].observation_sha256:
            return history
        expected = history[-1].sequence + 1
    else:
        expected = 1
    if observation.sequence != expected:
        raise InvalidShadowCycle(f"NONCONTIGUOUS_SEQUENCE:expected={expected}:actual={observation.sequence}")
    if any(row.observation_sha256 == observation.observation_sha256 for row in history):
        raise InvalidShadowCycle("DUPLICATE_OBSERVATION_OUT_OF_ORDER")
    return history + (observation,)


def summarize_shadow_cycle(
    history: tuple[ShadowObservation, ...],
    *,
    required_consecutive_matches: int = 3,
) -> ShadowCycleReport:
    if not history:
        raise InvalidShadowCycle("NO_SHADOW_OBSERVATIONS")
    if required_consecutive_matches < 1:
        raise InvalidShadowCycle("INVALID_REQUIRED_MATCH_COUNT")
    for expected, observation in enumerate(history, start=1):
        if observation.sequence != expected:
            raise InvalidShadowCycle("HISTORY_SEQUENCE_INVALID")

    latest = history[-1]
    consecutive = 0
    for observation in reversed(history):
        if observation.comparison_status != "MATCH":
            break
        if observation.shadow_implementation_commit != latest.shadow_implementation_commit:
            break
        if observation.shadow_contract_sha256 != latest.shadow_contract_sha256:
            break
        consecutive += 1

    active_blockers = tuple(sorted(set(latest.external_blockers)))
    historical_blockers = tuple(sorted({blocker for observation in history for blocker in observation.external_blockers}))
    binding_drift_seen = any(
        observation.shadow_implementation_commit != latest.shadow_implementation_commit
        or observation.shadow_contract_sha256 != latest.shadow_contract_sha256
        for observation in history[:-1]
    )

    if latest.comparison_status in {"MISMATCH", "STALE"}:
        status = "NOT_READY_DIVERGENCE"
    elif latest.comparison_status == "UNKNOWN":
        status = "NOT_READY_UNKNOWN"
    elif active_blockers:
        status = "BLOCKED_EXTERNAL_CONTINUITY_OR_CONTROL_GATE"
    elif consecutive < required_consecutive_matches:
        status = "OBSERVING_MORE_MATCH_CYCLES"
    else:
        status = "READY_FOR_INDEPENDENT_VALIDATION_CANDIDATE"

    cycle_material = {
        "observations": [row.observation_sha256 for row in history],
        "required_consecutive_matches": required_consecutive_matches,
    }
    cycle_id = content_sha256(cycle_material)
    return ShadowCycleReport(
        cycle_id=cycle_id,
        observation_count=len(history),
        consecutive_match_count=consecutive,
        latest_comparison_status=latest.comparison_status,
        status=status,
        active_external_blockers=active_blockers,
        historical_blockers_seen=historical_blockers,
        current_state_sha256=latest.current_state_sha256,
        shadow_implementation_commit=latest.shadow_implementation_commit,
        shadow_contract_sha256=latest.shadow_contract_sha256,
        latest_observation_sha256=latest.observation_sha256,
        binding_drift_seen=binding_drift_seen,
        ready_for_independent_validation_candidate=status == "READY_FOR_INDEPENDENT_VALIDATION_CANDIDATE",
    )
