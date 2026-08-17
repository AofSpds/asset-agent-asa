from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Iterable, Mapping, Protocol


class ProviderUnavailable(RuntimeError):
    """Transient/provider-side failure for which ordered failover is allowed."""


class ProviderRequestRejected(RuntimeError):
    """Request/semantic failure that must not silently fail over to another model."""


@dataclass(frozen=True)
class ProviderCapabilities:
    invoke: bool
    stream: bool
    structured_output: bool
    tool_calling: bool


@dataclass(frozen=True)
class ProviderHealth:
    provider_id: str
    status: str
    detail: str | None = None


@dataclass(frozen=True)
class ProviderCostMetadata:
    provider_id: str
    currency: str | None = None
    input_unit_cost: str | None = None
    output_unit_cost: str | None = None
    detail: str | None = None


class ModelProvider(Protocol):
    provider_id: str

    def capabilities(self) -> ProviderCapabilities: ...
    def health(self) -> ProviderHealth: ...
    def invoke(self, request: Mapping[str, Any]) -> Mapping[str, Any]: ...
    def stream(self, request: Mapping[str, Any]) -> Iterable[Mapping[str, Any]]: ...
    def structured_output(self, request: Mapping[str, Any]) -> Mapping[str, Any]: ...
    def tool_calling(self, request: Mapping[str, Any]) -> Mapping[str, Any]: ...
    def cost_metadata(self) -> ProviderCostMetadata: ...


class OfflineProvider:
    """Explicit fail-closed provider used when all LLM providers are unavailable."""

    provider_id = "offline"

    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(False, False, False, False)

    def health(self) -> ProviderHealth:
        return ProviderHealth(self.provider_id, "OFFLINE", "No model provider configured")

    def invoke(self, request: Mapping[str, Any]) -> Mapping[str, Any]:
        raise ProviderUnavailable("LLM_PROVIDER_OFFLINE")

    def stream(self, request: Mapping[str, Any]) -> Iterable[Mapping[str, Any]]:
        raise ProviderUnavailable("LLM_PROVIDER_OFFLINE")

    def structured_output(self, request: Mapping[str, Any]) -> Mapping[str, Any]:
        raise ProviderUnavailable("LLM_PROVIDER_OFFLINE")

    def tool_calling(self, request: Mapping[str, Any]) -> Mapping[str, Any]:
        raise ProviderUnavailable("LLM_PROVIDER_OFFLINE")

    def cost_metadata(self) -> ProviderCostMetadata:
        return ProviderCostMetadata(self.provider_id, detail="offline")


class FakeProvider:
    """Deterministic provider for provider-swap and contract tests."""

    provider_id = "fake"

    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(True, True, True, True)

    def health(self) -> ProviderHealth:
        return ProviderHealth(self.provider_id, "HEALTHY")

    def invoke(self, request: Mapping[str, Any]) -> Mapping[str, Any]:
        return {"provider_id": self.provider_id, "echo": dict(request)}

    def stream(self, request: Mapping[str, Any]) -> Iterable[Mapping[str, Any]]:
        yield self.invoke(request)

    def structured_output(self, request: Mapping[str, Any]) -> Mapping[str, Any]:
        return {"provider_id": self.provider_id, "structured": dict(request)}

    def tool_calling(self, request: Mapping[str, Any]) -> Mapping[str, Any]:
        return {"provider_id": self.provider_id, "tool_call": dict(request)}

    def cost_metadata(self) -> ProviderCostMetadata:
        return ProviderCostMetadata(self.provider_id, currency="TEST", input_unit_cost="0", output_unit_cost="0")


class CallableProviderAdapter:
    """Provider-neutral adapter around injected transports.

    Network/auth/provider SDK details stay outside the deterministic gateway. The
    injected transport must classify provider-side retryable failures as
    ProviderUnavailable and request/semantic failures as ProviderRequestRejected.
    This prevents unsafe silent model switching on malformed or rejected requests.
    """

    def __init__(
        self,
        *,
        provider_id: str,
        invoke_transport: Callable[[Mapping[str, Any]], Mapping[str, Any]],
        health_transport: Callable[[], ProviderHealth],
        capabilities: ProviderCapabilities,
        stream_transport: Callable[[Mapping[str, Any]], Iterable[Mapping[str, Any]]] | None = None,
        structured_transport: Callable[[Mapping[str, Any]], Mapping[str, Any]] | None = None,
        tool_transport: Callable[[Mapping[str, Any]], Mapping[str, Any]] | None = None,
        cost: ProviderCostMetadata | None = None,
    ) -> None:
        if not provider_id:
            raise ValueError("provider_id is required")
        self.provider_id = provider_id
        self._invoke_transport = invoke_transport
        self._health_transport = health_transport
        self._capabilities = capabilities
        self._stream_transport = stream_transport
        self._structured_transport = structured_transport
        self._tool_transport = tool_transport
        self._cost = cost or ProviderCostMetadata(provider_id)
        if self._cost.provider_id != provider_id:
            raise ValueError("cost metadata provider_id mismatch")

    def capabilities(self) -> ProviderCapabilities:
        return self._capabilities

    def health(self) -> ProviderHealth:
        health = self._health_transport()
        if health.provider_id != self.provider_id:
            raise RuntimeError("PROVIDER_HEALTH_IDENTITY_MISMATCH")
        return health

    def invoke(self, request: Mapping[str, Any]) -> Mapping[str, Any]:
        if not self._capabilities.invoke:
            raise ProviderRequestRejected("PROVIDER_CAPABILITY_UNAVAILABLE:invoke")
        return dict(self._invoke_transport(dict(request)))

    def stream(self, request: Mapping[str, Any]) -> Iterable[Mapping[str, Any]]:
        if not self._capabilities.stream or self._stream_transport is None:
            raise ProviderRequestRejected("PROVIDER_CAPABILITY_UNAVAILABLE:stream")
        for item in self._stream_transport(dict(request)):
            yield dict(item)

    def structured_output(self, request: Mapping[str, Any]) -> Mapping[str, Any]:
        if not self._capabilities.structured_output or self._structured_transport is None:
            raise ProviderRequestRejected("PROVIDER_CAPABILITY_UNAVAILABLE:structured_output")
        return dict(self._structured_transport(dict(request)))

    def tool_calling(self, request: Mapping[str, Any]) -> Mapping[str, Any]:
        if not self._capabilities.tool_calling or self._tool_transport is None:
            raise ProviderRequestRejected("PROVIDER_CAPABILITY_UNAVAILABLE:tool_calling")
        return dict(self._tool_transport(dict(request)))

    def cost_metadata(self) -> ProviderCostMetadata:
        return self._cost
