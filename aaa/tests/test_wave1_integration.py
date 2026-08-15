from __future__ import annotations

from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "aaa" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aaa.agents.runtime import AgentRunContext, PermissionDenied, PermissionLevel, authorize_action
from aaa.api.read_only import build_status, list_validation_gates, verify_asset
from aaa.cli.main import main as cli_main
from aaa.core.identity import ExactBaseIdentity, assert_exact_base, canonical_json_bytes, content_sha256
from aaa.gateway.provider import FakeProvider, OfflineProvider
from aaa.security.promotion import PromotionContext, authorize_canonical_promotion
from aaa.state.reducer import assert_idempotent_rebuild, reduce_events
from aaa.storage.identity import ContentIdentity, assert_same_key_identity, build_run_scoped_key, release_complete


class Wave1IntegrationTests(unittest.TestCase):
    def test_deterministic_identity_and_stale_base(self):
        self.assertEqual(canonical_json_bytes({"b": 2, "a": 1}), b'{"a":1,"b":2}')
        self.assertEqual(content_sha256({"a": 1, "b": 2}), content_sha256({"b": 2, "a": 1}))
        base = ExactBaseIdentity("AofSpds/asset-agent-asa", "a" * 40)
        assert_exact_base(base, base)
        with self.assertRaisesRegex(RuntimeError, "STALE_BASE"):
            assert_exact_base(base, ExactBaseIdentity("AofSpds/asset-agent-asa", "b" * 40))

    def test_shadow_reducer_is_deterministic_and_rejects_duplicate(self):
        events = [
            {"event_id": "E1", "object": "asset:1", "value": 1},
            {"event_id": "E2", "object": "asset:2", "value": 2},
        ]
        state = reduce_events(events)
        self.assertEqual(state.events_applied, 2)
        self.assertEqual(state.last_event_id, "E2")
        assert_idempotent_rebuild(events)
        with self.assertRaisesRegex(RuntimeError, "DUPLICATE_EVENT"):
            reduce_events([events[0], events[0]])

    def test_llm_off_and_provider_swap_contract(self):
        offline = OfflineProvider()
        self.assertEqual(offline.health().status, "OFFLINE")
        self.assertFalse(offline.capabilities().invoke)
        with self.assertRaisesRegex(RuntimeError, "LLM_PROVIDER_OFFLINE"):
            offline.invoke({"prompt": "x"})
        fake = FakeProvider()
        request = {"prompt": "x", "n": 1}
        self.assertEqual(fake.invoke(request), {"provider_id": "fake", "echo": request})
        self.assertEqual(list(fake.stream(request)), [fake.invoke(request)])

    def test_agent_permission_boundary(self):
        read_only = AgentRunContext("RUN-1", "RESEARCH", PermissionLevel.READ_ONLY, "a" * 40)
        with self.assertRaisesRegex(PermissionDenied, "INSUFFICIENT_PERMISSION"):
            authorize_action(read_only, "TOOL_CALL", PermissionLevel.TOOL_EXECUTION)
        writer_without_branch = AgentRunContext("RUN-2", "ENGINEERING", PermissionLevel.ISOLATED_BRANCH_WRITE, "a" * 40)
        with self.assertRaisesRegex(PermissionDenied, "ISOLATED_BRANCH_REQUIRED"):
            authorize_action(writer_without_branch, "WRITE_FILE", PermissionLevel.ISOLATED_BRANCH_WRITE)
        writer = AgentRunContext("RUN-3", "ENGINEERING", PermissionLevel.ISOLATED_BRANCH_WRITE, "a" * 40, "aaa-run-3")
        authorize_action(writer, "WRITE_FILE", PermissionLevel.ISOLATED_BRANCH_WRITE)
        with self.assertRaisesRegex(PermissionDenied, "FORBIDDEN_AUTHORITY_ACTION"):
            authorize_action(writer, "CANONICAL_WRITE", PermissionLevel.READ_ONLY)

    def test_storage_and_promotion_fail_closed(self):
        left = ContentIdentity.from_bytes(b"abc")
        right = ContentIdentity.from_bytes(b"abc")
        self.assertEqual(left, right)
        self.assertEqual(build_run_scoped_key("RUN-1", "/outputs/result.json"), "staging/RUN-1/outputs/result.json")
        with self.assertRaises(ValueError):
            build_run_scoped_key("RUN-1", "../escape")
        with self.assertRaisesRegex(RuntimeError, "SAME_KEY_DIFFERENT_HASH_HARD_FAIL"):
            assert_same_key_identity(left, ContentIdentity.from_bytes(b"different"))
        self.assertFalse(release_complete(True, False))
        self.assertTrue(release_complete(True, True))
        with self.assertRaisesRegex(PermissionError, "CANONICAL_PROMOTION_BLOCKED"):
            authorize_canonical_promotion(PromotionContext())
        authorize_canonical_promotion(PromotionContext(True, True, True, True))

    def test_read_only_status_and_cli_without_llm(self):
        status = build_status(ROOT)
        self.assertEqual(status["project"], "Asset Agent ASA")
        self.assertEqual(status["repository"], "AofSpds/asset-agent-asa")
        self.assertFalse(status["llm_required_for_control_plane"])
        self.assertEqual(status["canonical_authority"], "EXISTING_SEMI_CONTROL_PLANE")
        self.assertTrue(status["current_state"]["version"])
        self.assertTrue(status["current_state"]["identity"]["sha256"])
        gates = list_validation_gates(ROOT)
        self.assertIn("LLM_OFF_PASS", gates)
        asset = verify_asset(ROOT, "control/aaa/v0.1/AAA-BUILD-CONTRACT_v0.1_WORKING.yaml")
        self.assertTrue(asset["verified"])
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            rc = cli_main(["--repo-root", str(ROOT), "status", "--json"])
        self.assertEqual(rc, 0)
        payload = json.loads(buffer.getvalue())
        self.assertEqual(payload["short_name"], "AAA")


if __name__ == "__main__":
    unittest.main()
