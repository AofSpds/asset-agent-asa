from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PromotionContext:
    control_acceptance: bool = False
    required_validation_pass: bool = False
    owner_release_approval: bool = False
    deterministic_promotion_job: bool = False


def authorize_canonical_promotion(context: PromotionContext) -> None:
    """Fail closed unless every authoritative promotion gate is explicitly satisfied."""
    gates = {
        "CONTROL_ACCEPTANCE": context.control_acceptance,
        "REQUIRED_VALIDATION_PASS": context.required_validation_pass,
        "OWNER_RELEASE_APPROVAL": context.owner_release_approval,
        "DETERMINISTIC_PROMOTION_JOB": context.deterministic_promotion_job,
    }
    failed = [name for name, passed in gates.items() if not passed]
    if failed:
        raise PermissionError("CANONICAL_PROMOTION_BLOCKED: " + ",".join(failed))
