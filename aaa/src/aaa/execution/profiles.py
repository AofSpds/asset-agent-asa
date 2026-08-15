from __future__ import annotations

from aaa.execution.contracts import ExecutionContractError, ExecutionProfile


VALIDATION_EXACT_GIT_V0_1 = ExecutionProfile(
    execution_profile_id="AAA_VALIDATION_EXACT_GIT_V0_1",
    version="v0.1",
    allowed_personas=("SEMI-VALIDATION-AUDITOR",),
    required_capability="INDEPENDENT_VALIDATION",
    minimum_permission_level=1,
    timeout_seconds=1800,
    network_policy="DENY",
    filesystem_policy="READ_ONLY_EXACT_CHECKOUT",
    commands=(("python", "-m", "unittest", "discover", "-s", "aaa/tests", "-p", "test_*.py", "-v"),),
    environment_allowlist=("PYTHONPATH", "PATH", "HOME", "TMPDIR", "TEMP", "TMP"),
    metadata={
        "canonical_write": False,
        "llm_required": False,
        "purpose": "deterministic exact-target validation worker profile",
    },
)

_PROFILE_REGISTRY = {
    VALIDATION_EXACT_GIT_V0_1.execution_profile_id: VALIDATION_EXACT_GIT_V0_1,
}


def get_execution_profile(execution_profile_id: str) -> ExecutionProfile:
    try:
        profile = _PROFILE_REGISTRY[execution_profile_id]
    except KeyError as exc:
        raise ExecutionContractError("EXECUTION_PROFILE_NOT_ALLOWLISTED") from exc
    profile.validate()
    return profile


def list_execution_profiles() -> list[dict[str, object]]:
    return [
        {**profile.canonical_payload(), "profile_sha256": profile.profile_sha256}
        for profile in sorted(_PROFILE_REGISTRY.values(), key=lambda item: item.execution_profile_id)
    ]
