from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Iterable

from aaa.core.identity import content_sha256
from aaa.storage.identity import ContentIdentity, release_complete


BLOCKING_SEVERITIES = {"BLOCK"}


@dataclass(frozen=True)
class ArtifactRecoveryObservation:
    artifact_id: str
    expected: ContentIdentity
    observed_primary: ContentIdentity | None
    observed_secondary: ContentIdentity | None
    primary_available: bool
    secondary_available: bool


@dataclass(frozen=True)
class RunRecoveryObservation:
    run_id: str
    status: str
    journal_integrity_ok: bool
    result_identity_present: bool


@dataclass(frozen=True)
class StateRecoveryObservation:
    expected_state_sha256: str
    observed_state_sha256: str
    expected_base_commit: str
    observed_base_commit: str


@dataclass(frozen=True)
class RecoverySnapshot:
    artifacts: tuple[ArtifactRecoveryObservation, ...]
    runs: tuple[RunRecoveryObservation, ...]
    state: StateRecoveryObservation
    llm_provider_available: bool
    deterministic_core_available: bool
    canonical_write_requested: bool = False


@dataclass(frozen=True)
class RecoveryFinding:
    code: str
    severity: str
    subject: str
    detail: str


@dataclass(frozen=True)
class RecoveryReport:
    status: str
    safe_to_resume_noncanonical_work: bool
    canonical_mutation_allowed: bool
    findings: tuple[RecoveryFinding, ...]
    report_sha256: str


def _artifact_findings(obs: ArtifactRecoveryObservation) -> Iterable[RecoveryFinding]:
    if not obs.primary_available:
        yield RecoveryFinding("PRIMARY_ARTIFACT_MISSING", "BLOCK", obs.artifact_id, "Primary bytes are unavailable")
    elif obs.observed_primary != obs.expected:
        yield RecoveryFinding("PRIMARY_ARTIFACT_IDENTITY_MISMATCH", "BLOCK", obs.artifact_id, "Primary SHA256/byte-size differs from expected identity")

    if not obs.secondary_available:
        yield RecoveryFinding("SECONDARY_ARTIFACT_MISSING", "BLOCK", obs.artifact_id, "Secondary replica is unavailable; release is incomplete")
    elif obs.observed_secondary != obs.expected:
        yield RecoveryFinding("SECONDARY_ARTIFACT_IDENTITY_MISMATCH", "BLOCK", obs.artifact_id, "Secondary SHA256/byte-size differs from expected identity")

    if obs.primary_available and obs.secondary_available:
        primary_ok = obs.observed_primary == obs.expected
        secondary_ok = obs.observed_secondary == obs.expected
        if not release_complete(primary_ok, secondary_ok):
            yield RecoveryFinding("RELEASE_NOT_COMPLETE", "BLOCK", obs.artifact_id, "Both persisted copies are required to match before release completion")


def _run_findings(obs: RunRecoveryObservation) -> Iterable[RecoveryFinding]:
    if not obs.journal_integrity_ok:
        yield RecoveryFinding("RUN_JOURNAL_INTEGRITY_FAILURE", "BLOCK", obs.run_id, "Run history cannot be trusted until journal integrity is restored")
        return
    if obs.status == "RUNNING":
        yield RecoveryFinding("INTERRUPTED_RUN_REQUIRES_RECONCILIATION", "BLOCK", obs.run_id, "A process restart must not silently convert RUNNING into success")
    elif obs.status == "SUCCEEDED" and not obs.result_identity_present:
        yield RecoveryFinding("SUCCEEDED_RUN_MISSING_RESULT_IDENTITY", "BLOCK", obs.run_id, "Successful run lacks immutable result identity")
    elif obs.status not in {"CREATED", "RUNNING", "SUCCEEDED", "FAILED", "BLOCKED", "CANCELLED"}:
        yield RecoveryFinding("UNKNOWN_RUN_STATUS", "BLOCK", obs.run_id, f"Unknown run status: {obs.status}")


def audit_recovery(snapshot: RecoverySnapshot) -> RecoveryReport:
    findings: list[RecoveryFinding] = []

    if snapshot.canonical_write_requested:
        findings.append(RecoveryFinding("RECOVERY_CANONICAL_WRITE_PROHIBITED", "BLOCK", "CONTROL_PLANE", "Recovery inspection is read-only and cannot authorize canonical mutation"))

    if snapshot.state.expected_state_sha256 != snapshot.state.observed_state_sha256:
        findings.append(RecoveryFinding("STALE_OR_DIVERGED_CURRENT_STATE", "BLOCK", "CURRENT_STATE", "Observed Current State identity differs from the expected bound identity"))
    if snapshot.state.expected_base_commit != snapshot.state.observed_base_commit:
        findings.append(RecoveryFinding("STALE_BASE_COMMIT", "BLOCK", "BASE_COMMIT", "Observed repository base differs from the expected exact base"))

    for artifact in snapshot.artifacts:
        findings.extend(_artifact_findings(artifact))
    for run in snapshot.runs:
        findings.extend(_run_findings(run))

    if not snapshot.deterministic_core_available:
        findings.append(RecoveryFinding("DETERMINISTIC_CORE_UNAVAILABLE", "BLOCK", "AAA", "Control-plane recovery cannot proceed without the deterministic core"))
    elif not snapshot.llm_provider_available:
        findings.append(RecoveryFinding("LLM_OFF_CONTROL_PLANE_SURVIVES", "INFO", "AAA", "No LLM provider is available, but deterministic recovery remains operational"))

    blocked = any(f.severity in BLOCKING_SEVERITIES for f in findings)
    material = {
        "snapshot": asdict(snapshot),
        "findings": [asdict(f) for f in findings],
        "status": "BLOCKED" if blocked else "PASS",
        "safe_to_resume_noncanonical_work": not blocked,
        "canonical_mutation_allowed": False,
    }
    return RecoveryReport(
        status="BLOCKED" if blocked else "PASS",
        safe_to_resume_noncanonical_work=not blocked,
        canonical_mutation_allowed=False,
        findings=tuple(findings),
        report_sha256=content_sha256(material),
    )
