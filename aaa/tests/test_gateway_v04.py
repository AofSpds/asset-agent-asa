from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "aaa" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aaa.gateway.provider import (
    CallableProviderAdapter,
    FakeProvider,
    OfflineProvider,
    ProviderCapabilities,
    ProviderCostMetadata,
    ProviderHealth,
)
from aaa.gateway.router import AllProvidersUnavailable, ProviderGateway, result_manifest


class NamedFake(FakeProvider):
    def __init__(self, provider_id: str, *, healthy: bool = True, fail: bool = False) -> None:
        self.provider_id = provider_id
        self._healthy = healthy
        self._fail = fail

    def health(self) -> ProviderHealth:
        return ProviderHealth(self.provider_id, "HEALTHY" if self._healthy else "OFFLINE")

    def invoke(self, request):
        if self._fail:
            raise RuntimeError("SIMULATED_PROVIDER_FAILURE")
        return {"provider_id": self.provider_id, "echo": dict(request)}


class GatewayV04Tests(unittest.TestCase):
    def test_first_healthy_provider_wins_deterministically(self) -> None:
        gateway = ProviderGateway([NamedFake("A"), NamedFake("B")])
        result = gateway.invoke({"prompt": "x"})
        self.assertEqual(result.provider_id, "A")
        self.assertEqual(gateway.provider_order, ("A", "B"))
        self.assertFalse(result.canonical_output)
        self.assertEqual([a.outcome for a in result.attempts], ["SUCCESS"])

    def test_provider_a_offline_falls_back_to_b(self) -> None:
        gateway = ProviderGateway([NamedFake("A", healthy=False), NamedFake("B")])
        result = gateway.invoke({"prompt": "x"})
        self.assertEqual(result.provider_id, "B")
        self.assertEqual([a.outcome for a in result.attempts], ["SKIPPED_UNHEALTHY", "SUCCESS"])

    def test_provider_a_runtime_failure_falls_back_to_b(self) -> None:
        gateway = ProviderGateway([NamedFake("A", fail=True), NamedFake("B")])
        result = gateway.invoke({"prompt": "x"})
        self.assertEqual(result.provider_id, "B")
        self.assertEqual([a.outcome for a in result.attempts], ["INVOKE_ERROR", "SUCCESS"])

    def test_all_providers_offline_fails_closed(self) -> None:
        gateway = ProviderGateway([OfflineProvider(), NamedFake("B", healthy=False)])
        with self.assertRaisesRegex(AllProvidersUnavailable, "ALL_MODEL_PROVIDERS_UNAVAILABLE") as ctx:
            gateway.invoke({"prompt": "x"})
        self.assertEqual(len(ctx.exception.attempts), 2)

    def test_request_and_response_identities_are_stable(self) -> None:
        gateway = ProviderGateway([NamedFake("A")])
        first = gateway.invoke({"b": 2, "a": 1})
        second = gateway.invoke({"a": 1, "b": 2})
        self.assertEqual(first.request_sha256, second.request_sha256)
        self.assertEqual(first.response_sha256, second.response_sha256)
        manifest = result_manifest(first)
        self.assertFalse(manifest["canonical_output"])

    def test_capability_routing_skips_unsupported_provider(self) -> None:
        unsupported = CallableProviderAdapter(
            provider_id="A",
            invoke_transport=lambda request: {"bad": True},
            health_transport=lambda: ProviderHealth("A", "HEALTHY"),
            capabilities=ProviderCapabilities(True, False, False, False),
        )
        fallback = NamedFake("B")
        result = ProviderGateway([unsupported, fallback]).structured_output({"schema": "x"})
        self.assertEqual(result.provider_id, "B")
        self.assertEqual([a.outcome for a in result.attempts], ["SKIPPED_CAPABILITY", "SUCCESS"])

    def test_callable_adapter_enforces_health_identity(self) -> None:
        adapter = CallableProviderAdapter(
            provider_id="A",
            invoke_transport=lambda request: dict(request),
            health_transport=lambda: ProviderHealth("WRONG", "HEALTHY"),
            capabilities=ProviderCapabilities(True, False, False, False),
        )
        with self.assertRaisesRegex(RuntimeError, "PROVIDER_HEALTH_IDENTITY_MISMATCH"):
            adapter.health()

    def test_callable_adapter_cost_identity_must_match(self) -> None:
        with self.assertRaisesRegex(ValueError, "cost metadata provider_id mismatch"):
            CallableProviderAdapter(
                provider_id="A",
                invoke_transport=lambda request: dict(request),
                health_transport=lambda: ProviderHealth("A", "HEALTHY"),
                capabilities=ProviderCapabilities(True, False, False, False),
                cost=ProviderCostMetadata("B"),
            )

    def test_stream_never_stitches_two_providers_after_selection(self) -> None:
        class BrokenStream(NamedFake):
            def stream(self, request):
                yield {"provider_id": self.provider_id, "part": 1}
                raise RuntimeError("STREAM_BROKE")

        gateway = ProviderGateway([BrokenStream("A"), NamedFake("B")])
        stream = gateway.stream({"prompt": "x"})
        self.assertEqual(next(stream)["provider_id"], "A")
        with self.assertRaisesRegex(RuntimeError, "STREAM_BROKE"):
            next(stream)


if __name__ == "__main__":
    unittest.main()
