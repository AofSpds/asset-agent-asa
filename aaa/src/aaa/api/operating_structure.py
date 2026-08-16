from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from typing import Any

_CHANNEL_RE = re.compile(r"SEMI-CHANNEL-REGISTRY_v(\d+)\.(\d+)\.yaml$")
_ORG_RE = re.compile(r"SEMI-ORG-MAP_v(\d+)\.(\d+).*\.yaml$")
_CURRENT_STATE_RE = re.compile(r"SEMI-CURRENT-STATE_v(\d+)\.(\d+)\.yaml$")
_PROCESS_GATE_RE = re.compile(r"AAA-PROCESS-GATE-STATUS_v(\d+)\.(\d+)_WORKING\.yaml$")
_ROADMAP_RE = re.compile(r"AAA-v1-POST-IV-OPERATING-ROADMAP_v(\d+)\.(\d+)_OWNER-APPROVED\.json$")

_REQUIRED_SOURCES = ("organization", "channel_registry", "current_state", "process_gate", "roadmap")
_DISQUALIFYING_STATUS_TOKENS = (
    "UNPROVEN",
    "UNAPPROVED",
    "DRAFT",
    "PROPOSED",
    "REJECTED",
    "OBSOLETE",
    "SUPERSEDED",
    "INVALID",
)

_FORMAL_PERSONA_META: dict[str, dict[str, str | None]] = {
    "SEMI-CONTROL-ARCHITECT": {
        "korean_name": "문서·통제 아키텍트",
        "alias": "CORE A",
        "domain": "Data / Ground Truth / PIT / Artifact / Control / Continuity",
    },
    "SEMI-MODEL-VALIDATION-DESIGN-ARCHITECT": {
        "korean_name": "모델 검증·설계 아키텍트",
        "alias": "CORE B",
        "domain": "Model / Feature / Scorer / Weight / Ranking / Validation Methodology",
    },
    "SEMI-RESEARCH-ORCHESTRATOR": {
        "korean_name": "리서치팀",
        "alias": None,
        "domain": "Research / Evidence Acquisition / Evidence Structuring / Research Execution",
    },
    "SEMI-VALIDATION-AUDITOR": {
        "korean_name": "독립 검증·감사팀",
        "alias": None,
        "domain": "Independent Validation / Audit / Adversarial Review",
    },
}

_OWNER_AUTHORITY = [
    "project objectives",
    "priority",
    "major architecture direction",
    "final Freeze",
    "authority transition",
    "Controlled Cutover",
    "Production Release",
]


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _scalar(raw: str) -> Any:
    value = raw.strip()
    if not value:
        return None
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    lowered = value.lower()
    if lowered in {"null", "none", "~"}:
        return None
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    try:
        return int(value)
    except ValueError:
        return value


def _flatten_yaml_scalars(text: str) -> dict[str, Any]:
    result: dict[str, Any] = {}
    stack: list[tuple[int, str]] = []
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        stripped = raw.strip()
        if stripped.startswith("- ") or ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        while stack and indent <= stack[-1][0]:
            stack.pop()
        path = ".".join([item[1] for item in stack] + [key])
        if value.strip():
            result[path] = _scalar(value)
        else:
            stack.append((indent, key))
    return result


def _parse_channel_instances(text: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    in_instances = False
    current: dict[str, Any] | None = None
    for raw in text.splitlines():
        if raw == "instances:":
            in_instances = True
            continue
        if not in_instances:
            continue
        if raw and not raw.startswith(" "):
            break
        if raw.startswith("  - "):
            if current:
                rows.append(current)
            current = {}
            item = raw[4:].strip()
            if ":" in item:
                key, value = item.split(":", 1)
                current[key.strip()] = _scalar(value)
            continue
        if current is None or not raw.startswith("    ") or raw.startswith("      "):
            continue
        stripped = raw.strip()
        if ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        if value.strip():
            current[key.strip()] = _scalar(value)
    if current:
        rows.append(current)
    return rows


def _read_candidate(path: Path, kind: str) -> tuple[dict[str, Any], dict[str, Any]]:
    if kind == "roadmap":
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            return {}, {}
        return payload, payload
    text = path.read_text(encoding="utf-8")
    flat = _flatten_yaml_scalars(text)
    return flat, {"text": text}


def _declared_status(kind: str, parsed: dict[str, Any]) -> Any:
    if kind == "process_gate":
        return parsed.get("status") or parsed.get("next_gate.state") or parsed.get("roadmap.current_state")
    return parsed.get("status")


def _status_is_governed(kind: str, status: Any) -> bool:
    if status is None:
        return False
    normalized = str(status).upper()
    if "STALE" in normalized:
        return True
    if any(token in normalized for token in _DISQUALIFYING_STATUS_TOKENS):
        return False
    if kind == "roadmap":
        return normalized.startswith("OWNER_APPROVED")
    if kind == "organization":
        return (
            "OWNER_ACCEPTED" in normalized
            or "RECONCILED" in normalized
            or normalized.startswith("ACTIVE")
        )
    if kind in {"channel_registry", "current_state"}:
        return normalized.startswith("WORKING") or "RECONCILED" in normalized or normalized.startswith("ACTIVE")
    if kind == "process_gate":
        return (
            normalized.startswith("WORKING")
            or normalized in {
                "READY_NOT_DISPATCHED",
                "DISPATCHED_AWAITING_ACK",
                "RUNNING_CONFIRMED",
                "BLOCKED",
                "COMPLETED_PASS",
                "COMPLETED_FAIL",
                "COMPLETED_WITH_FINDINGS",
            }
        )
    return False


def _supersedes_value(kind: str, parsed: dict[str, Any]) -> Any:
    return parsed.get("supersedes")


def _select_governed_latest(
    root: Path,
    directory: Path,
    pattern: re.Pattern[str],
    kind: str,
) -> tuple[Path | None, dict[str, Any]]:
    if not directory.exists():
        return None, {"requirement": "REQUIRED", "selection": "NO_DIRECTORY", "skipped": []}
    candidates: list[tuple[tuple[int, int], Path]] = []
    for path in directory.iterdir():
        match = pattern.fullmatch(path.name)
        if match:
            candidates.append(((int(match.group(1)), int(match.group(2))), path))
    if not candidates:
        return None, {"requirement": "REQUIRED", "selection": "NO_CANDIDATE", "skipped": []}

    skipped: list[dict[str, Any]] = []
    for version, path in sorted(candidates, key=lambda row: row[0], reverse=True):
        try:
            parsed, _ = _read_candidate(path, kind)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            skipped.append({"path": str(path.relative_to(root)), "version": list(version), "reason": f"PARSE_ERROR:{type(exc).__name__}"})
            continue
        status = _declared_status(kind, parsed)
        if not _status_is_governed(kind, status):
            skipped.append({
                "path": str(path.relative_to(root)),
                "version": list(version),
                "declared_status": status,
                "reason": "UNSUPPORTED_OR_UNPROVEN_GOVERNED_STATUS",
            })
            continue
        supersedes = _supersedes_value(kind, parsed)
        if supersedes:
            predecessor = root / str(supersedes)
            if not predecessor.is_file():
                skipped.append({
                    "path": str(path.relative_to(root)),
                    "version": list(version),
                    "declared_status": status,
                    "supersedes": supersedes,
                    "reason": "BROKEN_SUPERSEDES_LINEAGE",
                })
                continue
        return path, {
            "requirement": "REQUIRED",
            "selection": "GOVERNED_CURRENT",
            "selected_version": list(version),
            "declared_status": status,
            "supersedes": supersedes,
            "skipped": skipped,
        }

    return None, {
        "requirement": "REQUIRED",
        "selection": "NO_GOVERNED_CURRENT_CANDIDATE",
        "skipped": skipped,
    }


def _identity(path: Path, root: Path) -> dict[str, Any]:
    data = path.read_bytes()
    return {
        "path": str(path.relative_to(root)),
        "sha256": _sha256(data),
        "byte_size": len(data),
    }


def _source(
    path: Path | None,
    root: Path,
    selection: dict[str, Any],
    *,
    as_of: Any = None,
    status: Any = None,
) -> dict[str, Any]:
    if path is None or not path.is_file():
        return {
            "requirement": "REQUIRED",
            "availability": "UNAVAILABLE",
            "path": None if path is None else str(path.relative_to(root)),
            "as_of": as_of,
            "declared_status": status,
            "selection": selection,
        }
    declared = str(status or "")
    availability = "STALE" if "STALE" in declared.upper() else "AVAILABLE"
    return {
        "requirement": "REQUIRED",
        "availability": availability,
        **_identity(path, root),
        "as_of": as_of,
        "declared_status": status,
        "selection": selection,
    }


def _normalize_channel_state(raw: Any) -> str:
    value = str(raw or "UNKNOWN").upper()
    if value == "ACTIVE":
        return "ACTIVE"
    if value in {"CLOSED", "ARCHIVED", "RECOVERY_ONLY"}:
        return "INACTIVE"
    if value in {"PLANNED", "ROTATING"}:
        return "AWAITING_DISPATCH"
    if value == "BLOCKED":
        return "BLOCKED"
    return "UNKNOWN"


def _normalize_execution_state(raw: Any) -> str:
    value = str(raw or "UNKNOWN").upper()
    if value in {"READY_NOT_DISPATCHED", "DISPATCHED_AWAITING_ACK"}:
        return "AWAITING_DISPATCH"
    if value == "RUNNING_CONFIRMED":
        return "RUNNING"
    if value.startswith("COMPLETED"):
        return "COMPLETED"
    if value == "BLOCKED":
        return "BLOCKED"
    if value in {"STALE_UNKNOWN", "UNKNOWN", "UNAVAILABLE"}:
        return "UNKNOWN"
    return "ACTIVE" if value == "ACTIVE" else "UNKNOWN"


def _load_json(path: Path | None) -> dict[str, Any]:
    if path is None or not path.is_file():
        return {}
    raw = json.loads(path.read_text(encoding="utf-8"))
    return raw if isinstance(raw, dict) else {}


def _run_snapshot(root: Path, run_id: str) -> dict[str, Any]:
    path = root / "control" / "aaa" / "runs" / f"{run_id}.json"
    if not path.is_file():
        return {
            "run_id": run_id,
            "historical_state": "UNKNOWN",
            "current_disposition": "NOT_REGISTERED",
            "source": {"availability": "UNAVAILABLE", "path": str(path.relative_to(root))},
        }
    payload = _load_json(path)
    return {
        "run_id": run_id,
        "historical_state": payload.get("state", "UNKNOWN"),
        "started_at": payload.get("started_at"),
        "last_heartbeat_at": payload.get("last_heartbeat_at"),
        "terminal_result": payload.get("terminal_result"),
        "current_disposition": "NOT_REGISTERED",
        "source": _identity(path, root),
    }


def _science_projection(state_flat: dict[str, Any], source_availability: str) -> dict[str, Any]:
    baseline = state_flat.get("model_v1.baseline_source_commit")
    if source_availability != "AVAILABLE":
        return {
            "status": "STALE" if source_availability == "STALE" else "UNKNOWN",
            "current_activity": None,
            "exact_target": None,
            "current_target_state": "UNKNOWN",
            "current_validation_verdict": None,
            "last_control_fix_target": None,
            "historical_baseline_target": baseline,
            "schema_binding": "UNAVAILABLE_CURRENT_STATE",
        }

    version = str(state_flat.get("version") or "")
    v2_current_status = state_flat.get("independent_delta_preflight.current_status")
    if v2_current_status is not None or version.startswith("v2."):
        raw_status = v2_current_status
        last_control_fix = state_flat.get("model_v1.control_fix_successor.source_commit")
        verdict = (
            state_flat.get("model_v1.control_fix_successor.independent_delta_verdict")
            or state_flat.get("model_v1.independent_delta_adjudication.verdict")
        )
        normalized_status = str(raw_status or "UNKNOWN").upper()
        waiting_new = (
            "WAITING_NEW" in normalized_status
            or "NEW_SUCCESSOR_REQUIRED" in normalized_status
            or "SUCCESSOR_REQUIRED" in normalized_status
        )
        if raw_status is None:
            exact_target = None
            current_target_state = "UNKNOWN"
        else:
            exact_target = None if waiting_new else last_control_fix
            current_target_state = (
                "NOT_REGISTERED" if waiting_new
                else ("BOUND" if exact_target else "UNKNOWN")
            )
        display_status = (
            "AWAITING_VALIDATION"
            if raw_status and ("WAITING" in normalized_status or "RERUN" in normalized_status)
            else ("ACTIVE" if raw_status else "UNKNOWN")
        )
        return {
            "status": display_status,
            "current_activity": raw_status,
            "exact_target": exact_target,
            "current_target_state": current_target_state,
            "current_validation_verdict": verdict,
            "last_control_fix_target": last_control_fix,
            "historical_baseline_target": baseline,
            "schema_binding": "SEMI-CURRENT-STATE_V2_EXPLICIT",
        }

    next_validation = state_flat.get("validation_channel.next_validation")
    current_activity = next_validation or state_flat.get("model_v1.independent_preflight.status")
    exact_target = state_flat.get("model_v1.source_code_commit")
    return {
        "status": "AWAITING_VALIDATION" if next_validation else ("ACTIVE" if current_activity else "UNKNOWN"),
        "current_activity": current_activity,
        "exact_target": exact_target,
        "current_target_state": "BOUND" if exact_target else "UNKNOWN",
        "current_validation_verdict": None,
        "last_control_fix_target": None,
        "historical_baseline_target": baseline,
        "schema_binding": "LEGACY_EXPLICIT_NO_BASELINE_FALLBACK",
    }


def build_operating_structure(repo_root: Path) -> dict[str, Any]:
    root = repo_root.resolve()
    continuity = root / "control" / "continuity" / "v1.0"
    aaa_v01 = root / "control" / "aaa" / "v0.1"
    aaa_architecture = root / "control" / "aaa" / "architecture"

    org_path, org_sel = _select_governed_latest(root, continuity, _ORG_RE, "organization")
    channel_path, channel_sel = _select_governed_latest(root, continuity, _CHANNEL_RE, "channel_registry")
    current_state_path, state_sel = _select_governed_latest(root, continuity, _CURRENT_STATE_RE, "current_state")
    gate_path, gate_sel = _select_governed_latest(root, aaa_v01, _PROCESS_GATE_RE, "process_gate")
    roadmap_path, roadmap_sel = _select_governed_latest(root, aaa_architecture, _ROADMAP_RE, "roadmap")

    org_text = org_path.read_text(encoding="utf-8") if org_path else ""
    channel_text = channel_path.read_text(encoding="utf-8") if channel_path else ""
    current_state_text = current_state_path.read_text(encoding="utf-8") if current_state_path else ""
    gate_text = gate_path.read_text(encoding="utf-8") if gate_path else ""

    org_flat = _flatten_yaml_scalars(org_text) if org_text else {}
    channel_flat = _flatten_yaml_scalars(channel_text) if channel_text else {}
    state_flat = _flatten_yaml_scalars(current_state_text) if current_state_text else {}
    gate_flat = _flatten_yaml_scalars(gate_text) if gate_text else {}
    roadmap = _load_json(roadmap_path)

    sources = {
        "organization": _source(org_path, root, org_sel, as_of=org_flat.get("as_of"), status=org_flat.get("status")),
        "channel_registry": _source(channel_path, root, channel_sel, as_of=channel_flat.get("as_of"), status=channel_flat.get("status")),
        "current_state": _source(current_state_path, root, state_sel, as_of=state_flat.get("as_of"), status=state_flat.get("status")),
        "process_gate": _source(
            gate_path,
            root,
            gate_sel,
            as_of=gate_flat.get("recorded_at"),
            status=gate_flat.get("status") or gate_flat.get("next_gate.state") or gate_flat.get("roadmap.current_state"),
        ),
        "roadmap": _source(roadmap_path, root, roadmap_sel, as_of=roadmap.get("approved_at"), status=roadmap.get("status")),
    }

    instances = _parse_channel_instances(channel_text) if sources["channel_registry"]["availability"] == "AVAILABLE" else []
    active_instances = [row for row in instances if str(row.get("status", "")).upper() == "ACTIVE"]

    conflicts: list[dict[str, Any]] = []
    seen_active: dict[str, str | None] = {}
    for row in active_instances:
        channel_id = str(row.get("channel_instance_id") or "")
        binding = row.get("persona_id")
        normalized_binding = None if binding is None else str(binding)
        if channel_id in seen_active and seen_active[channel_id] != normalized_binding:
            conflicts.append({
                "type": "CHANNEL_BINDING_CONFLICT",
                "channel_instance_id": channel_id,
                "source_a": seen_active[channel_id],
                "source_b": normalized_binding,
            })
        seen_active[channel_id] = normalized_binding

    core_a_expected = channel_flat.get("current_structure.core_a_dedicated_active_channel")
    core_a_active = [row for row in active_instances if row.get("persona_id") == "SEMI-CONTROL-ARCHITECT"]
    if core_a_expected is False and core_a_active:
        conflicts.append({
            "type": "CORE_A_CHANNEL_CURRENT_STATE_CONFLICT",
            "source_a": "current_structure.core_a_dedicated_active_channel=false",
            "source_b": [row.get("channel_instance_id") for row in core_a_active],
        })

    organization_health = sources["organization"]["availability"]
    formal_personas: list[dict[str, Any]] = []
    for persona_id, meta in _FORMAL_PERSONA_META.items():
        registered = persona_id in org_text if organization_health == "AVAILABLE" else False
        bindings = [
            {
                "channel_instance_id": row.get("channel_instance_id"),
                "display_name": row.get("display_name"),
                "channel_type": row.get("channel_type", "PERSONA_CHANNEL"),
                "status": row.get("status"),
            }
            for row in active_instances
            if row.get("persona_id") == persona_id
        ]
        if organization_health == "STALE":
            persona_status = "STALE"
            binding_state = "UNKNOWN"
        elif organization_health != "AVAILABLE":
            persona_status = "UNKNOWN"
            binding_state = "UNKNOWN"
        else:
            persona_status = "ACTIVE" if registered else "UNKNOWN"
            binding_state = "ACTIVE" if registered and bindings else ("NOT_INSTANTIATED" if registered else "UNKNOWN")
        formal_personas.append({
            "persona_id": persona_id,
            "formal_name": persona_id,
            "korean_name": meta["korean_name"],
            "alias": meta["alias"],
            "domain": meta["domain"],
            "status": persona_status,
            "active_channel_binding_state": binding_state,
            "active_channels": bindings if registered else [],
            "manifest_or_state_ref": str(org_path.relative_to(root)) if org_path and registered else None,
            "last_update": org_flat.get("as_of") if registered else None,
        })

    channels: list[dict[str, Any]] = []
    inactive_channels: list[dict[str, Any]] = []
    for row in instances:
        normalized = {
            "channel_instance_id": row.get("channel_instance_id"),
            "display_name": row.get("display_name") or row.get("channel_instance_id"),
            "channel_type": row.get("channel_type", "PERSONA_CHANNEL"),
            "persona_binding": row.get("persona_id"),
            "status": _normalize_channel_state(row.get("status")),
            "raw_status": row.get("status", "UNKNOWN"),
            "role": row.get("role"),
            "authority_relation": row.get("authority_relation"),
            "current_workstream": row.get("current_workstream"),
            "source_ref": str(channel_path.relative_to(root)) if channel_path else None,
        }
        if normalized["status"] == "ACTIVE":
            channels.append(normalized)
        else:
            inactive_channels.append(normalized)

    gate_available = sources["process_gate"]["availability"] == "AVAILABLE"
    roadmap_available = sources["roadmap"]["availability"] == "AVAILABLE"
    authority_flags = {
        "json_registry_operational_authority_during_shadow": gate_flat.get("operational_authority.json_registry_operational_authority_during_shadow") if gate_available else None,
        "postgresql_authoritative": gate_flat.get("operational_authority.postgresql_authoritative") if gate_available else None,
        "bounded_shadow_execution_authorized": gate_flat.get("operational_authority.bounded_shadow_execution_authorized") if gate_available else None,
        "live_execution_authorized": gate_flat.get("operational_authority.live_execution_authorized") if gate_available else None,
        "postgresql_operational_sot_authorized": gate_flat.get("operational_authority.postgresql_operational_sot_authorized") if gate_available else None,
        "production_canonical_promotion_authorized": gate_flat.get("operational_authority.production_canonical_promotion_authorized") if gate_available else None,
        "controlled_cutover_authorized": gate_flat.get("operational_authority.controlled_cutover_authorized") if gate_available else None,
        "production_release_authorized": gate_flat.get("operational_authority.production_release_authorized") if gate_available else None,
    }

    current_stage = (
        gate_flat.get("next_gate.current_stage")
        or gate_flat.get("roadmap.current_stage")
        or (roadmap.get("current_stage") if roadmap_available else None)
        or "UNKNOWN"
    ) if gate_available else "UNKNOWN"
    current_gate = (
        gate_flat.get("next_gate.current_gate")
        or gate_flat.get("roadmap.current_gate")
        or (roadmap.get("current_gate") if roadmap_available else None)
        or "UNKNOWN"
    ) if gate_available else "UNKNOWN"
    raw_stage_state = (
        gate_flat.get("next_gate.state")
        or gate_flat.get("roadmap.current_state")
        or "UNKNOWN"
    ) if gate_available else "UNKNOWN"

    stages = roadmap.get("stages") if roadmap_available and isinstance(roadmap.get("stages"), list) else []
    stage_rows: list[dict[str, Any]] = []
    stage0_completed = bool(gate_flat.get("roadmap.stage_0_completed")) if gate_available else False
    for stage in stages:
        if not isinstance(stage, dict):
            continue
        stage_id = str(stage.get("id") or "UNKNOWN")
        if stage_id == current_stage:
            stage_state = _normalize_execution_state(raw_stage_state)
        elif stage_id == "STAGE_0" and stage0_completed:
            stage_state = "COMPLETED"
        else:
            stage_state = "INACTIVE"
        stage_rows.append({**stage, "display_state": stage_state})

    aaa_workstream = {
        "workstream_id": "AAA_OPERATIONALIZATION",
        "display_name": "AAA Operationalization",
        "domain_owner": "PROJECT_OWNER / governed implementation channels",
        "status": _normalize_execution_state(raw_stage_state) if gate_available else "UNKNOWN",
        "current_stage": current_stage,
        "current_gate": current_gate,
        "current_activity": gate_flat.get("current_position.current_controlled_activity") if gate_available else None,
        "exact_target": gate_flat.get("current_position.validated_successor_target") if gate_available else None,
        "next_required_decision": gate_flat.get("next_gate.owner_decision_required_before_any_authority_transition") if gate_available else None,
        "source_ref": str(gate_path.relative_to(root)) if gate_path else None,
    }

    science = _science_projection(state_flat, sources["current_state"]["availability"])
    science_workstream = {
        "workstream_id": "M3TOP3_SCIENTIFIC_VALIDATION",
        "display_name": "M3Top3 Scientific Validation",
        "domain_owner": "SEMI-MODEL-VALIDATION-DESIGN-ARCHITECT",
        **science,
        "source_ref": str(current_state_path.relative_to(root)) if current_state_path else None,
    }

    validation_channel_active = any(row.get("persona_id") == "SEMI-VALIDATION-AUDITOR" for row in active_instances)
    validation_healthy = (
        sources["channel_registry"]["availability"] == "AVAILABLE"
        and sources["process_gate"]["availability"] == "AVAILABLE"
    )
    validation_workstream = {
        "workstream_id": "INDEPENDENT_VALIDATION",
        "display_name": "Independent Validation",
        "domain_owner": "SEMI-VALIDATION-AUDITOR",
        "status": ("ACTIVE" if validation_channel_active else "NOT_INSTANTIATED") if validation_healthy else "UNKNOWN",
        "current_activity": "Gate/exit validation checkpoints" if validation_healthy else None,
        "latest_validated_target": gate_flat.get("current_position.validated_successor_target") if validation_healthy else None,
        "latest_validation_state": gate_flat.get("current_position.independent_revalidation_state") if validation_healthy else None,
        "source_ref": str(gate_path.relative_to(root)) if gate_path and validation_healthy else None,
    }

    p09 = _run_snapshot(root, "RUN-VALIDATION-AAA-INDEPENDENT-PREFLIGHT-20260816-002")
    t18 = _run_snapshot(root, "RUN-VALIDATION-AAA-T18-INDEPENDENT-20260816-001")
    roadmap_legacy = roadmap.get("legacy_run_governance") if roadmap_available else None
    if isinstance(roadmap_legacy, dict):
        dispositions = roadmap_legacy.get("current_dispositions")
        if isinstance(dispositions, dict):
            p09["current_disposition"] = dispositions.get(p09["run_id"], p09["current_disposition"])
            t18["current_disposition"] = dispositions.get(t18["run_id"], t18["current_disposition"])

    required_availability = [sources[name]["availability"] for name in _REQUIRED_SOURCES]
    if conflicts:
        projection_status = "CONFLICT"
    elif "UNAVAILABLE" in required_availability:
        projection_status = "UNAVAILABLE"
    elif "STALE" in required_availability:
        projection_status = "STALE"
    else:
        projection_status = "CURRENT"

    as_of_candidates = [
        sources[name].get("as_of")
        for name in _REQUIRED_SOURCES
        if sources[name].get("as_of")
    ]
    current_as_of = max((str(value) for value in as_of_candidates), default=None)

    projection_material = json.dumps(
        {
            "sources": sources,
            "current_stage": current_stage,
            "current_gate": current_gate,
            "active_channels": [
                (row.get("channel_instance_id"), row.get("persona_binding"), row.get("status"))
                for row in channels
            ],
            "authority": authority_flags,
            "science": science,
            "conflicts": conflicts,
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    authority_holder = {
        "authority_id": "PROJECT_OWNER" if organization_health == "AVAILABLE" else "UNKNOWN",
        "display_name": "Project Owner / 연구책임자" if organization_health == "AVAILABLE" else "UNKNOWN",
        "responsibilities": _OWNER_AUTHORITY if organization_health == "AVAILABLE" else [],
        "source_ref": str(org_path.relative_to(root)) if org_path and organization_health == "AVAILABLE" else None,
        "provenance_state": organization_health,
    }

    return {
        "project": "Asset Agent ASA",
        "short_name": "AAA",
        "projection": {
            "status": projection_status,
            "current_as_of": current_as_of,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source": "Persistent Control Plane deterministic read model",
            "source_state_id": _sha256(projection_material),
            "required_sources": list(_REQUIRED_SOURCES),
            "conflicts": conflicts,
            "sources": sources,
        },
        "authority": {
            "authority_holder": authority_holder,
            "operational_flags": authority_flags,
        },
        "formal_personas": formal_personas,
        "active_channels": channels,
        "inactive_channels": inactive_channels,
        "relationships": {
            "edge_types": [
                "AUTHORITY_APPROVAL",
                "PERSONA_RESPONSIBILITY",
                "CHANNEL_PERSONA_BINDING",
                "EXECUTION_WORKSTREAM",
                "VALIDATION_AUDIT",
                "ADVISORY",
            ]
        },
        "workstreams": [aaa_workstream, science_workstream, validation_workstream],
        "roadmap": {
            "roadmap_id": roadmap.get("roadmap_id") if roadmap_available else None,
            "version": roadmap.get("version") if roadmap_available else None,
            "status": roadmap.get("status") if roadmap_available else None,
            "current_stage": current_stage,
            "current_gate": current_gate,
            "current_stage_state": _normalize_execution_state(raw_stage_state) if gate_available else "UNKNOWN",
            "stages": stage_rows,
            "validator_modifications": roadmap.get("validator_modifications", []) if roadmap_available else [],
            "acceptance_contracts": roadmap.get("acceptance_contracts", {}) if roadmap_available else {},
            "source_ref": str(roadmap_path.relative_to(root)) if roadmap_path else None,
        },
        "historical_runs": [p09, t18],
        "ui_contract": {
            "persona_is_not_channel": True,
            "no_execution_inference_without_evidence": True,
            "required_source_health_is_fail_closed": True,
            "unknown_is_visible": True,
            "stale_is_visible": True,
            "conflict_is_visible": True,
            "read_only": True,
        },
    }
