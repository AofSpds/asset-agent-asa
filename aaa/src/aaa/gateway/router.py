from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable, Mapping, Sequence

from aaa.core.identity import content_sha256
from aaa.gateway.provider import ModelProvider, ProviderCapabilities, ProviderHealth


HEALTHY_STATUSES = {"HEALTHY"}


@dataclass(frozen=True)
class ProviderAttempt:
    provider_id: str
    health_status: str
    outcome: str
    detail: str | None = None


@dataclass(frozen=True)
class GatewayResult:
    provider_id: str
    operation: str
    request_sha256: str
    response_sha256: str
    response: Mapping[str, Any]
    attempts: tuple[ProviderAttempt, ...]
    canonical_output: bool = False


class AllProvidersUnavailable(RuntimeError):
    def __init__(self, attempts: Sequence[ProviderAttempt]) -> None:
        self.attempts = tuple(attempts)
        detail = ";".join(f"{a.provider_id}:{a.health_status}:{a.outcome}" for a in self.attempts)
        super().__init__(f"ALL_MODEL_PROVIDERS_UNAVAILABLE:{detail}")


class ProviderGateway:
    """Deterministic ordered provider router.

    Provider order is explicit configuration. Health/capability failures are
    recorded and the next provider is attempted. Model output is always marked
    noncanonical; this router has no Control authority.
    """

    def __init__(self, providers: Sequence[ModelProvider]) -> None:
        if not providers:
            raise ValueError("at least one provider is required")
        ids = [p.provider_id for p in providers]
        if any(not provider_id for provider_id in ids):
            raise ValueError("provider_id is required")
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate provider_id")
        self._providers = tuple(providers)

    @property
    def provider_order(self) -> tuple[str, ...]:
        return tuple(provider.provider_id for provider in self._providers)

    def health(self) -> tuple[ProviderHealth, ...]:
        rows: list[ProviderHealth] = []
        for provider in self._providers:
            try:
                health = provider.health()
                if health.provider_id != provider.provider_id:
                    rows.append(ProviderHealth(provider.provider_id, "INVALID", "health identity mismatch"))
                else:
                    rows.append(health)
            except Exception as exc:  # provider boundary: convert failure to health row
                rows.append(ProviderHealth(provider.provider_id, "ERROR", type(exc).__name__))
        return tuple(rows)

    def _supports(self, caps: ProviderCapabilities, operation: str) -> bool:
        return bool(getattr(caps, operation, False))

    def invoke(self, request: Mapping[str, Any]) -> GatewayResult:
        return self._execute("invoke", request)

    def structured_output(self, request: Mapping[str, Any]) -> GatewayResult:
        return self._execute("structured_output", request)

    def tool_calling(self, request: Mapping[str, Any]) -> GatewayResult:
        return self._execute("tool_calling", request)

    def _execute(self, operation: str, request: Mapping[str, Any]) -> GatewayResult:
        request_material = dict(request)
        request_sha256 = content_sha256(request_material)
        attempts: list[ProviderAttempt] = []

        for provider in self._providers:
            try:
                health = provider.health()
            except Exception as exc:
                attempts.append(ProviderAttempt(provider.provider_id, "ERROR", "HEALTH_ERROR", type(exc).__name__))
                continue
            if health.provider_id != provider.provider_id:
                attempts.append(ProviderAttempt(provider.provider_id, "INVALID", "HEALTH_IDENTITY_MISMATCH"))
                continue
            if health.status not in HEALTHY_STATUSES:
                attempts.append(ProviderAttempt(provider.provider_id, health.status, "SKIPPED_UNHEALTHY", health.detail))
                continue
            try:
                caps = provider.capabilities()
            except Exception as exc:
                attempts.append(ProviderAttempt(provider.provider_id, health.status, "CAPABILITY_ERROR", type(exc).__name__))
                continue
            if not self._supports(caps, operation):
                attempts.append(ProviderAttempt(provider.provider_id, health.status, "SKIPPED_CAPABILITY"))
                continue
            try:
                fn = getattr(provider, operation)
                response = dict(fn(request_material))
            except Exception as exc:
                attempts.append(ProviderAttempt(provider.provider_id, health.status, "INVOKE_ERROR", type(exc).__name__))
                continue
            attempts.append(ProviderAttempt(provider.provider_id, health.status, "SUCCESS"))
            return GatewayResult(
                provider_id=provider.provider_id,
                operation=operation,
                request_sha256=request_sha256,
                response_sha256=content_sha256(response),
                response=response,
                attempts=tuple(attempts),
                canonical_output=False,
            )

        raise AllProvidersUnavailable(attempts)

    def stream(self, request: Mapping[str, Any]) -> Iterable[Mapping[str, Any]]:
        """Streaming deliberately does not fail over after bytes have been yielded.

        A provider may be skipped before streaming starts. Once selected, any
        stream failure is surfaced to the caller to avoid stitching outputs from
        different providers into one ambiguous result.
        """
        attempts: list[ProviderAttempt] = []
        for provider in self._providers:
            try:
                health = provider.health()
                caps = provider.capabilities()
            except Exception as exc:
                attempts.append(ProviderAttempt(provider.provider_id, "ERROR", "PRESTREAM_ERROR", type(exc).__name__))
                continue
            if health.provider_id != provider.provider_id:
                attempts.append(ProviderAttempt(provider.provider_id, "INVALID", "HEALTH_IDENTITY_MISMATCH"))
                continue
            if health.status not in HEALTHY_STATUSES:
                attempts.append(ProviderAttempt(provider.provider_id, health.status, "SKIPPED_UNHEALTHY", health.detail))
                continue
            if not caps.stream:
                attempts.append(ProviderAttempt(provider.provider_id, health.status, "SKIPPED_CAPABILITY"))
                continue
            yield from provider.stream(dict(request))
            return
        raise AllProvidersUnavailable(attempts)


def result_manifest(result: GatewayResult) -> dict[str, Any]:
    return {
        "provider_id": result.provider_id,
        "operation": result.operation,
        "request_sha256": result.request_sha256,
        "response_sha256": result.response_sha256,
        "attempts": [asdict(row) for row in result.attempts],
        "canonical_output": False,
    }
