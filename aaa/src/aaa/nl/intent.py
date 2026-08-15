from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from typing import Any, Mapping

from aaa.core.identity import ExactBaseIdentity, canonical_json_bytes, content_sha256
from aaa.gateway.router import AllProvidersUnavailable, GatewayResult, ProviderGateway


FORBIDDEN_INTENT_KEYS = {
    "canonical_write",
    "ground_truth_promotion",
    "shared_contract_change",
    "model_freeze",
    "production_release",
    "independent_validation_pass",
    "replay_authorized",
}

ALLOWED_EXECUTOR_ROLES = {
    "RESEARCH",
    "ENGINEERING",
    "PREVALIDATION_CHECK",
}

MANDATORY_FORBIDDEN_ACTIONS = (
    "CANONICAL_WRITE",
    "GROUND_TRUTH_PROMOTION",
    "SHARED_CONTRACT_CHANGE",
    "MODEL_FREEZE",
    "PRODUCTION_RELEASE",
    "INDEPENDENT_VALIDATION_SELF_CERTIFICATION",
)


class InvalidWorkIntent(RuntimeError):
    pass


def _canonical_json_text(value: Any) -> str:
    return canonical_json_bytes(value).decode("utf-8")


@dataclass(frozen=True)
class CandidateWorkIntent:
    source_provider_id: str
    source_request_sha256: str
    source_response_sha256: str
    user_text_sha256: str
    title: str
    objective: str
    executor_role: str
    permission_level: int
    material_scope: tuple[str, ...]
    input_bindings_json: tuple[str, ...]
    acceptance: tuple[str, ...]
    required_validation: tuple[str, ...]
    scientific_firewall: tuple[str, ...]
    canonical_output: bool = False
    requires_deterministic_confirmation: bool = True

    def __post_init__(self) -> None:
        if not self.title or not self.objective or not self.executor_role:
            raise InvalidWorkIntent("TITLE_OBJECTIVE_EXECUTOR_REQUIRED")
        if self.executor_role not in ALLOWED_EXECUTOR_ROLES:
            raise InvalidWorkIntent(f"EXECUTOR_ROLE_NOT_ALLOWED:{self.executor_role}")
        if self.permission_level < 0 or self.permission_level > 2:
            raise InvalidWorkIntent("PERMISSION_LEVEL_OUT_OF_RANGE")
        if not self.material_scope:
            raise InvalidWorkIntent("MATERIAL_SCOPE_REQUIRED")
        if any(not scope or scope.startswith("/") or ".." in scope.split("/") for scope in self.material_scope):
            raise InvalidWorkIntent("UNSAFE_MATERIAL_SCOPE")
        if not self.acceptance or not self.required_validation or not self.scientific_firewall:
            raise InvalidWorkIntent("CONTROL_FIELDS_REQUIRED")
        for encoded in self.input_bindings_json:
            decoded = json.loads(encoded)
            if not isinstance(decoded, dict):
                raise InvalidWorkIntent("INVALID_INPUT_BINDING_ENCODING")
        if self.canonical_output:
            raise InvalidWorkIntent("LANGUAGE_OUTPUT_MUST_BE_NONCANONICAL")
        if not self.requires_deterministic_confirmation:
            raise InvalidWorkIntent("DETERMINISTIC_CONFIRMATION_REQUIRED")

    @property
    def input_bindings(self) -> tuple[Mapping[str, Any], ...]:
        return tuple(json.loads(encoded) for encoded in self.input_bindings_json)

    @property
    def candidate_sha256(self) -> str:
        return content_sha256(asdict(self))


@dataclass(frozen=True)
class WorkOrderDraft:
    payload_json: str
    candidate_sha256: str
    canonical_output: bool = False
    requires_authority_acceptance: bool = True

    def __post_init__(self) -> None:
        payload = json.loads(self.payload_json)
        if not isinstance(payload, dict):
            raise InvalidWorkIntent("INVALID_WORK_ORDER_DRAFT_PAYLOAD")
        if self.canonical_output:
            raise InvalidWorkIntent("WORK_ORDER_DRAFT_MUST_BE_NONCANONICAL")
        if not self.requires_authority_acceptance:
            raise InvalidWorkIntent("WORK_ORDER_DRAFT_REQUIRES_AUTHORITY_ACCEPTANCE")

    @property
    def payload(self) -> Mapping[str, Any]:
        return json.loads(self.payload_json)

    @property
    def draft_sha256(self) -> str:
        return content_sha256({
            "payload_json": self.payload_json,
            "candidate_sha256": self.candidate_sha256,
            "canonical_output": self.canonical_output,
            "requires_authority_acceptance": self.requires_authority_acceptance,
        })


@dataclass(frozen=True)
class ReasoningUnavailable:
    status: str
    detail: str
    control_plane_operational: bool = True
    canonical_output: bool = False


def _strings(value: Any, field: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not value or any(not isinstance(item, str) or not item for item in value):
        raise InvalidWorkIntent(f"INVALID_{field.upper()}")
    return tuple(value)


def _bindings(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list) or any(not isinstance(item, dict) for item in value):
        raise InvalidWorkIntent("INVALID_INPUT_BINDINGS")
    return tuple(_canonical_json_text(item) for item in value)


def _candidate_from_gateway(result: GatewayResult, user_text: str) -> CandidateWorkIntent:
    response = dict(result.response)
    intent = response.get("intent")
    if not isinstance(intent, dict):
        raise InvalidWorkIntent("MISSING_INTENT_OBJECT")
    prohibited = FORBIDDEN_INTENT_KEYS.intersection(intent)
    if prohibited:
        raise InvalidWorkIntent(f"FORBIDDEN_AUTHORITY_FIELDS:{','.join(sorted(prohibited))}")
    try:
        permission_level = int(intent.get("permission_level", -1))
    except (TypeError, ValueError) as exc:
        raise InvalidWorkIntent("INVALID_PERMISSION_LEVEL") from exc
    return CandidateWorkIntent(
        source_provider_id=result.provider_id,
        source_request_sha256=result.request_sha256,
        source_response_sha256=result.response_sha256,
        user_text_sha256=content_sha256({"user_text": user_text}),
        title=str(intent.get("title") or ""),
        objective=str(intent.get("objective") or ""),
        executor_role=str(intent.get("executor_role") or ""),
        permission_level=permission_level,
        material_scope=_strings(intent.get("material_scope"), "material_scope"),
        input_bindings_json=_bindings(intent.get("input_bindings")),
        acceptance=_strings(intent.get("acceptance"), "acceptance"),
        required_validation=_strings(intent.get("required_validation"), "required_validation"),
        scientific_firewall=_strings(intent.get("scientific_firewall"), "scientific_firewall"),
    )


def interpret_work_intent(gateway: ProviderGateway, user_text: str) -> CandidateWorkIntent | ReasoningUnavailable:
    if not user_text.strip():
        raise InvalidWorkIntent("EMPTY_USER_TEXT")
    request = {
        "task": "AAA_WORK_INTENT_EXTRACTION",
        "user_text": user_text,
        "constraints": {
            "canonical_output": False,
            "permission_level_max": 2,
            "allowed_executor_roles": sorted(ALLOWED_EXECUTOR_ROLES),
            "authority_fields_forbidden": sorted(FORBIDDEN_INTENT_KEYS),
            "required_fields": [
                "title",
                "objective",
                "executor_role",
                "permission_level",
                "material_scope",
                "input_bindings",
                "acceptance",
                "required_validation",
                "scientific_firewall",
            ],
        },
    }
    try:
        result = gateway.structured_output(request)
    except AllProvidersUnavailable as exc:
        return ReasoningUnavailable("WAITING_FOR_REASONING", str(exc))
    return _candidate_from_gateway(result, user_text)


def confirm_to_work_order_draft(
    candidate: CandidateWorkIntent,
    *,
    expected_candidate_sha256: str,
    exact_base_identity: ExactBaseIdentity,
    work_order_id: str,
    work_order_version: str,
    created_at: str,
) -> WorkOrderDraft:
    if candidate.candidate_sha256 != expected_candidate_sha256:
        raise InvalidWorkIntent("STALE_OR_CHANGED_CANDIDATE")
    if not work_order_id or not work_order_version or not created_at:
        raise InvalidWorkIntent("WORK_ORDER_ID_VERSION_CREATED_AT_REQUIRED")

    input_bindings = [dict(item) for item in candidate.input_bindings]
    input_bindings.append({
        "binding_type": "AAA_NL_CANDIDATE",
        "candidate_sha256": candidate.candidate_sha256,
        "source_provider_id": candidate.source_provider_id,
        "source_response_sha256": candidate.source_response_sha256,
    })
    material_without_hash: dict[str, Any] = {
        "work_order_id": work_order_id,
        "work_order_version": work_order_version,
        "title": candidate.title,
        "objective": candidate.objective,
        "executor_role": candidate.executor_role,
        "permission_level": candidate.permission_level,
        "exact_base_identity": asdict(exact_base_identity),
        "input_bindings": input_bindings,
        "material_scope": list(candidate.material_scope),
        "output_contract": "AAA_RESULT_MANIFEST",
        "forbidden_actions": list(MANDATORY_FORBIDDEN_ACTIONS),
        "acceptance": list(candidate.acceptance),
        "required_validation": list(candidate.required_validation),
        "scientific_firewall": list(candidate.scientific_firewall),
        "created_at": created_at,
    }
    work_order_sha256 = content_sha256(material_without_hash)
    payload = {"work_order_sha256": work_order_sha256, **material_without_hash}
    return WorkOrderDraft(payload_json=_canonical_json_text(payload), candidate_sha256=candidate.candidate_sha256)
