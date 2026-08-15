from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "aaa" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aaa.core.identity import ExactBaseIdentity
from aaa.gateway.provider import FakeProvider, OfflineProvider
from aaa.gateway.router import ProviderGateway
from aaa.nl.intent import (
    CandidateWorkIntent,
    InvalidWorkIntent,
    ReasoningUnavailable,
    confirm_to_work_order_draft,
    interpret_work_intent,
)


GOOD_INTENT = {
    "title": "Inspect asset status",
    "objective": "Read deterministic asset state and summarize discrepancies",
    "executor_role": "RESEARCH",
    "permission_level": 0,
    "material_scope": ["control/aaa/**"],
    "input_bindings": [{"asset_id": "A1", "sha256": "a" * 64}],
    "acceptance": ["status returned", "no canonical mutation"],
    "required_validation": ["deterministic identity check"],
    "scientific_firewall": ["no future outcome use"],
}


class IntentProvider(FakeProvider):
    provider_id = "intent-test"

    def __init__(self, intent=None) -> None:
        self.intent = dict(GOOD_INTENT if intent is None else intent)

    def structured_output(self, request):
        return {"intent": dict(self.intent)}


class NaturalLanguageIntentV05Tests(unittest.TestCase):
    def test_language_output_is_candidate_only(self) -> None:
        candidate = interpret_work_intent(ProviderGateway([IntentProvider()]), "자산 상태를 확인해줘")
        self.assertIsInstance(candidate, CandidateWorkIntent)
        assert isinstance(candidate, CandidateWorkIntent)
        self.assertFalse(candidate.canonical_output)
        self.assertTrue(candidate.requires_deterministic_confirmation)
        self.assertEqual(candidate.permission_level, 0)
        self.assertRegex(candidate.candidate_sha256, r"^[0-9a-f]{64}$")

    def test_all_providers_offline_does_not_block_control_plane(self) -> None:
        result = interpret_work_intent(ProviderGateway([OfflineProvider()]), "상태 설명")
        self.assertIsInstance(result, ReasoningUnavailable)
        assert isinstance(result, ReasoningUnavailable)
        self.assertEqual(result.status, "WAITING_FOR_REASONING")
        self.assertTrue(result.control_plane_operational)
        self.assertFalse(result.canonical_output)

    def test_authority_fields_from_model_are_rejected(self) -> None:
        bad = dict(GOOD_INTENT)
        bad["production_release"] = True
        with self.assertRaisesRegex(InvalidWorkIntent, "FORBIDDEN_AUTHORITY_FIELDS"):
            interpret_work_intent(ProviderGateway([IntentProvider(bad)]), "릴리즈 해줘")

    def test_permission_above_l2_is_rejected(self) -> None:
        bad = dict(GOOD_INTENT)
        bad["permission_level"] = 5
        with self.assertRaisesRegex(InvalidWorkIntent, "PERMISSION_LEVEL_OUT_OF_RANGE"):
            interpret_work_intent(ProviderGateway([IntentProvider(bad)]), "작업")

    def test_candidate_change_is_detected_before_work_order_draft(self) -> None:
        candidate = interpret_work_intent(ProviderGateway([IntentProvider()]), "작업")
        assert isinstance(candidate, CandidateWorkIntent)
        with self.assertRaisesRegex(InvalidWorkIntent, "STALE_OR_CHANGED_CANDIDATE"):
            confirm_to_work_order_draft(
                candidate,
                expected_candidate_sha256="0" * 64,
                exact_base_identity=ExactBaseIdentity("AofSpds/asset-agent-asa", "1" * 40),
                work_order_id="WO-1",
                work_order_version="v0.1",
                created_at="2026-08-16T04:00:00+09:00",
            )

    def test_confirmed_draft_is_noncanonical_and_hash_bound(self) -> None:
        candidate = interpret_work_intent(ProviderGateway([IntentProvider()]), "작업")
        assert isinstance(candidate, CandidateWorkIntent)
        kwargs = dict(
            expected_candidate_sha256=candidate.candidate_sha256,
            exact_base_identity=ExactBaseIdentity("AofSpds/asset-agent-asa", "1" * 40),
            work_order_id="WO-1",
            work_order_version="v0.1",
            created_at="2026-08-16T04:00:00+09:00",
        )
        first = confirm_to_work_order_draft(candidate, **kwargs)
        second = confirm_to_work_order_draft(candidate, **kwargs)
        self.assertEqual(first, second)
        self.assertFalse(first.canonical_output)
        self.assertTrue(first.requires_authority_acceptance)
        self.assertRegex(first.payload["work_order_sha256"], r"^[0-9a-f]{64}$")
        self.assertEqual(first.payload["permission_level"], 0)
        self.assertEqual(first.payload["output_contract"], "AAA_RESULT_MANIFEST")
        self.assertIn("CANONICAL_WRITE", first.payload["forbidden_actions"])
        self.assertEqual(first.payload["input_bindings"][-1]["candidate_sha256"], candidate.candidate_sha256)
        self.assertRegex(first.draft_sha256, r"^[0-9a-f]{64}$")

    def test_empty_input_fails_before_provider_call(self) -> None:
        with self.assertRaisesRegex(InvalidWorkIntent, "EMPTY_USER_TEXT"):
            interpret_work_intent(ProviderGateway([IntentProvider()]), "   ")


if __name__ == "__main__":
    unittest.main()
