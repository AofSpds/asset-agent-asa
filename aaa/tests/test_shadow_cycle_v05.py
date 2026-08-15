from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "aaa" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aaa.state.shadow_cycle import (
    KNOWN_CONTINUITY_COLLISION,
    InvalidShadowCycle,
    ShadowObservation,
    append_observation,
    summarize_shadow_cycle,
)


def observation(sequence: int, status: str = "MATCH", blockers=()) -> ShadowObservation:
    return ShadowObservation(
        sequence=sequence,
        observed_at=f"2026-08-16T04:{sequence:02d}:00+09:00",
        current_state_path="control/continuity/v1.0/SEMI-CURRENT-STATE_v2.10.yaml",
        current_state_sha256=(hex(sequence)[2:] * 64)[:64],
        event_ledger_path="control/continuity/v1.0/SEMI-CONTROL-EVENT-LEDGER_v3.3.jsonl",
        event_ledger_sha256="a" * 64,
        discrepancy_report_sha256="b" * 64,
        comparison_status=status,
        external_blockers=tuple(blockers),
    )


class ShadowCycleV05Tests(unittest.TestCase):
    def test_three_clean_matches_yield_validation_candidate_not_cutover(self) -> None:
        history = ()
        for i in range(1, 4):
            history = append_observation(history, observation(i))
        report = summarize_shadow_cycle(history, required_consecutive_matches=3)
        self.assertEqual(report.status, "READY_FOR_INDEPENDENT_VALIDATION_CANDIDATE")
        self.assertTrue(report.ready_for_independent_validation_candidate)
        self.assertFalse(report.cutover_authorized)
        self.assertFalse(report.canonical_output)
        self.assertFalse(report.historical_repair_performed)

    def test_known_continuity_collision_blocks_even_with_matches(self) -> None:
        history = ()
        for i in range(1, 4):
            history = append_observation(history, observation(i, blockers=(KNOWN_CONTINUITY_COLLISION,)))
        report = summarize_shadow_cycle(history)
        self.assertEqual(report.status, "BLOCKED_EXTERNAL_CONTINUITY_OR_CONTROL_GATE")
        self.assertIn(KNOWN_CONTINUITY_COLLISION, report.external_blockers)
        self.assertFalse(report.ready_for_independent_validation_candidate)

    def test_mismatch_has_priority_over_external_blocker(self) -> None:
        history = append_observation((), observation(1, blockers=(KNOWN_CONTINUITY_COLLISION,)))
        history = append_observation(history, observation(2, status="MISMATCH", blockers=(KNOWN_CONTINUITY_COLLISION,)))
        report = summarize_shadow_cycle(history)
        self.assertEqual(report.status, "NOT_READY_DIVERGENCE")

    def test_unknown_is_not_treated_as_match(self) -> None:
        report = summarize_shadow_cycle((observation(1, status="UNKNOWN"),))
        self.assertEqual(report.status, "NOT_READY_UNKNOWN")
        self.assertEqual(report.consecutive_match_count, 0)

    def test_exact_last_observation_reappend_is_idempotent(self) -> None:
        first = observation(1)
        history = append_observation((), first)
        self.assertEqual(append_observation(history, first), history)

    def test_noncontiguous_sequence_is_rejected(self) -> None:
        with self.assertRaisesRegex(InvalidShadowCycle, "NONCONTIGUOUS_SEQUENCE"):
            append_observation((observation(1),), observation(3))

    def test_cycle_report_identity_is_deterministic(self) -> None:
        history = (observation(1), observation(2))
        first = summarize_shadow_cycle(history)
        second = summarize_shadow_cycle(history)
        self.assertEqual(first, second)
        self.assertRegex(first.cycle_id, r"^[0-9a-f]{64}$")
        self.assertRegex(first.report_sha256, r"^[0-9a-f]{64}$")

    def test_shadow_output_cannot_be_constructed_as_canonical(self) -> None:
        with self.assertRaisesRegex(InvalidShadowCycle, "SHADOW_OUTPUT_MUST_BE_NONCANONICAL"):
            replace(observation(1), canonical_output=True)


if __name__ == "__main__":
    unittest.main()
