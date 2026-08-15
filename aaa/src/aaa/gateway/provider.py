from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Protocol


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


class ModelProvider(Protocol):
    provider_id: str

    def capabilities(self) -> ProviderCapabilities: ...
    def health(self) -> ProviderHealth: ...
    def invoke(self, request: Mapping[str, Any]) -> Mapping[str, Any]: ...
    def stream(self, request: Mapping[str, Any]) -> Iterable[Mapping[str, Any]]: ...


class OfflineProvider:
    """Explicit fail-closed provider used when all LLM providers are unavailable."""

    provider_id = "offline"

    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(False, False, False, False)

    def health(self) -> ProviderHealth:
        return ProviderHealth(self.provider_id, "OFFLINE", "No model provider configured")

    def invoke(self, request: Mapping[str, Any]) -> Mapping[str, Any]:
        raise RuntimeError("LLM_PROVIDER_OFFLINE")

    def stream(self, request: Mapping[str, Any]) -> Iterable[Mapping[str, Any]]:
        raise RuntimeError("LLM_PROVIDER_OFFLINE")


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
