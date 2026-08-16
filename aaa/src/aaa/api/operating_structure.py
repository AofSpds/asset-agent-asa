from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import re
from typing import Any

from aaa.core.identity import sha256_hex
from aaa.state.discrepancy import flatten_yaml_scalars


_CHANNEL_RE = re.compile(r"SEMI-CHANNEL-REGISTRY_v(\d+)\.(\d+)\.yaml$")
_ORG_RE = re.compile(r"SEMI-ORG-MAP_v(\d+)\.(\d+).*\.yaml$")
_CURRENT_STATE_RE = re.compile(r"SEMI-CURRENT-STATE_v(\d+)\.(\d+)\.yaml$")
_PROCESS_GATE_RE = re.compile(r"AAA-PROCESS-GATE-STATUS_v(\d+)\.(\d+)_WORKING\.yaml$")
_ROADMAP_RE = re.compile(r"AAA-v1-POST-IV-OPERATING-ROADMAP_v(\d+)\.(\d+)_OWNER-APPROVED\.json$")

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


def _latest_versioned(root: Path, pattern: re.Pattern[str]) -> Path | None:
    if not root.exists():
        return None
    candidates: list[tuple[tuple[int, int], Path]] = []
    for path in root.iterdir():
        match = pattern.fullmatch(path.name)
        if match:
            candidates.append(((int(match.group(1)), int(match.group(2))), path))
    if not candidates:
        return None
    return max(candidates, key=lambda row: row[0])[1]


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
        if raw and not raw.startswith(" ") and raw != "instances:":
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


def _identity(path: Path, root: Path) -> dict[str, Any]:
    data = path.read_bytes()
    return {
        "path": str(path.relative_to(root)),
        "sha256": sha256_hex(data),
        "byte_size": len(data),
    }


def _source(path: Path | None, root: Path, *, as_of: Any = None, status: Any = None) -> dict[str, Any]:
    if path is None or not path.is_file():
        return {
            "availability": "UNAVAILABLE",
            "path": None if path is None else str(path.relative_to(root)),
            "as_of": as_of,
            "declared_status": status,
        }
    declared = str(status or "")
    freshness = "STALE" if "STALE" in declared.upper() else "AVAILABLE"
    return {
        "availability": freshness,
        **_identity(path, root),
        "as_of": as_of,
        "declared_status": status,
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


def build_operating_structure(repo_root: Path) -> dict[str, Any]:
    root = repo_root.resolve()
    continuity = root / "control" / "continuity" / "v1.0"
    aaa_v01 = root / "control" / "aaa" / "v0.1"
    aaa_architecture = root / "control" / "aaa" / "architecture"

    channel_path = _latest_versioned(continuity, _CHANNEL_RE)
    org_path = _latest_versioned(continuity, _ORG_RE)
    current_state_path = _latest_versioned(continuity, _CURRENT_STATE_RE)
    gate_path = _latest_versioned(aaa_v01, _PROCESS_GATE_RE)
    roadmap_path = _latest_versioned(aaa_architecture, _ROADMAP_RE)

    channel_text = channel_path.read_text(encoding="utf-8") if channel_path else ""
    org_text = org_path.read_text(encoding="utf-8") if org_path else ""
    current_state_text = current_state_path.read_text(encoding="utf-8") if current_state_path else ""
    gate_text = gate_path.read_text(encoding="utf-8") if gate_path else ""

    channel_flat = flatten_yaml_scalars(channel_text) if channel_text else {}
    org_flat = flatten_yaml_scalars(org_text) if org_text else {}
    state_flat = flatten_yaml_scalars(current_state_text) if current_state_text else {}
    gate_flat = flatten_yaml_scalars(gate_text) if gate_text else {}
    roadmap = _load_json(roadmap_path)

    instances = _parse_channel_instances(channel_text)
    active_instances = [row for row in instances if str(row.get("status", "")).upper() == "ACTIVE"]

    conflicts: list[dict[str, Any]] = []
    seen_active: dict[str, str | None] = {}
    for row in active_instances:
        channel_id = str(row.get("channel_instance_id") or "")
        binding = row.get("persona_id")
        if channel_id in seen_active and seen_active[channel_id] != binding:
            conflicts.append(
                {
                    "type": "CHANNEL_BINDING_CONFLICT",
                    "channel_instance_id": channel_id,
                    "source_a": seen_active[channel_id],
                    "source_b": binding,
                }
            )
        seen_active[channel_id] = None if binding is None else str(binding)

    core_a_expected = channel_flat.get("current_structure.core_a_dedicated_active_channel")
    core_a_active = [
        row
        for row in active_instances
        if row.get("persona_id") == "SEMI-CONTROL-ARCHITECT"
    ]
    if core_a_expected is False and core_a_active:
        conflicts.append(
            {
                "type": "CORE_A_CHANNEL_CURRENT_STATE_CONFLICT",
                "source_a": "current_structure.core_a_dedicated_active_channel=false",
                "source_b": [row.get("channel_instance_id") for row in core_a_active],
            }
        )

    formal_personas: list[dict[str, Any]] = []
    for persona_id, meta in _FORMAL_PERSONA_META.items():
        registered = persona_id in org_text or persona_id in channel_text or persona_id in current_state_text
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
        formal_personas.append(
            {
                "persona_id": persona_id,
                "formal_name": persona_id,
                "korean_name": meta["korean_name"],
                "alias": meta["alias"],
                "domain": meta["domain"],
                "status": "ACTIVE" if registered else "UNKNOWN",
                "active_channel_binding_state": "ACTIVE" if bindings else ("NOT_INSTANTIATED" if registered else "UNKNOWN"),
                "active_channels": bindings,
                "manifest_or_state_ref": str(org_path.relative_to(root)) if org_path else None,
                "last_update": channel_flat.get("as_of") or state_flat.get("as_of"),
            }
        )

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

    authority_flags = {
        "json_registry_operational_authority_during_shadow": gate_flat.get(
            "operational_authority.json_registry_operational_authority_during_shadow"
        ),
        "postgresql_authoritative": gate_flat.get("operational_authority.postgresql_authoritative"),
        "bounded_shadow_execution_authorized": gate_flat.get(
            "operational_authority.bounded_shadow_execution_authorized"
        ),
        "live_execution_authorized": gate_flat.get("operational_authority.live_execution_authorized"),
        "production_canonical_promotion_authorized": gate_flat.get(
            "operational_authority.production_canonical_promotion_authorized"
        ),
        "controlled_cutover_authorized": gate_flat.get(
            "operational_authority.controlled_cutover_authorized"
        ),
        "production_release_authorized": gate_flat.get(
            "operational_authority.production_release_authorized"
        ),
    }

    current_stage = (
        gate_flat.get("next_gate.current_stage")
        or gate_flat.get("roadmap.current_stage")
        or roadmap.get("current_stage")
        or "UNKNOWN"
    )
    current_gate = (
        gate_flat.get("next_gate.current_gate")
        or gate_flat.get("roadmap.current_gate")
        or roadmap.get("current_gate")
        or "UNKNOWN"
    )
    raw_stage_state = (
        gate_flat.get("next_gate.state")
        or gate_flat.get("roadmap.current_state")
        or "UNKNOWN"
    )

    stages = roadmap.get("stages") if isinstance(roadmap.get("stages"), list) else []
    stage_rows: list[dict[str, Any]] = []
    stage0_completed = bool(gate_flat.get("roadmap.stage_0_completed"))
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
        "status": _normalize_execution_state(raw_stage_state),
        "current_stage": current_stage,
        "current_gate": current_gate,
        "current_activity": gate_flat.get("current_position.current_controlled_activity"),
        "exact_target": gate_flat.get("current_position.validated_successor_target"),
        "next_required_decision": gate_flat.get("next_gate.owner_decision_required_before_any_authority_transition"),
        "source_ref": str(gate_path.relative_to(root)) if gate_path else None,
    }

    scientific_next_validation = state_flat.get("validation_channel.next_validation")
    scientific_status = "AWAITING_VALIDATION" if scientific_next_validation else (
        "ACTIVE" if state_flat.get("model_v1.model_version") else "UNKNOWN"
    )
    science_workstream = {
        "workstream_id": "M3TOP3_SCIENTIFIC_VALIDATION",
        "display_name": "M3Top3 Scientific Validation",
        "domain_owner": "SEMI-MODEL-VALIDATION-DESIGN-ARCHITECT",
        "status": scientific_status,
        "current_activity": scientific_next_validation or state_flat.get("model_v1.independent_preflight.status"),
        "exact_target": state_flat.get("model_v1.baseline_source_commit") or state_flat.get("model_v1.source_code_commit"),
        "source_ref": str(current_state_path.relative_to(root)) if current_state_path else None,
    }

    validation_channel_active = any(
        row.get("persona_id") == "SEMI-VALIDATION-AUDITOR" for row in active_instances
    )
    validation_workstream = {
        "workstream_id": "INDEPENDENT_VALIDATION",
        "display_name": "Independent Validation",
        "domain_owner": "SEMI-VALIDATION-AUDITOR",
        "status": "ACTIVE" if validation_channel_active else "NOT_INSTANTIATED",
        "current_activity": "Gate/exit validation checkpoints",
        "latest_validated_target": gate_flat.get("current_position.validated_successor_target"),
        "latest_validation_state": gate_flat.get("current_position.independent_revalidation_state"),
        "source_ref": str(gate_path.relative_to(root)) if gate_path else None,
    }

    p09 = _run_snapshot(root, "RUN-VALIDATION-AAA-INDEPENDENT-PREFLIGHT-20260816-002")
    t18 = _run_snapshot(root, "RUN-VALIDATION-AAA-T18-INDEPENDENT-20260816-001")

    roadmap_legacy = roadmap.get("legacy_run_governance")
    if isinstance(roadmap_legacy, dict):
        dispositions = roadmap_legacy.get("current_dispositions")
        if isinstance(dispositions, dict):
            p09["current_disposition"] = dispositions.get(p09["run_id"], p09["current_disposition"])
            t18["current_disposition"] = dispositions.get(t18["run_id"], t18["current_disposition"])

    sources = {
        "organization": _source(
            org_path,
            root,
            as_of=org_flat.get("as_of"),
            status=org_flat.get("status"),
        ),
        "channel_registry": _source(
            channel_path,
            root,
            as_of=channel_flat.get("as_of"),
            status=channel_flat.get("status"),
        ),
        "current_state": _source(
            current_state_path,
            root,
            as_of=state_flat.get("as_of"),
            status=state_flat.get("status"),
        ),
        "process_gate": _source(
            gate_path,
            root,
            as_of=gate_flat.get("recorded_at"),
            status=gate_flat.get("next_gate.state") or gate_flat.get("status"),
        ),
        "roadmap": _source(
            roadmap_path,
            root,
            as_of=roadmap.get("approved_at"),
            status=roadmap.get("status"),
        ),
    }

    required_availability = [
        sources["channel_registry"]["availability"],
        sources["process_gate"]["availability"],
        sources["roadmap"]["availability"],
    ]
    if conflicts:
        projection_status = "CONFLICT"
    elif "UNAVAILABLE" in required_availability:
        projection_status = "UNAVAILABLE"
    elif "STALE" in required_availability:
        projection_status = "STALE"
    else:
        projection_status = "CURRENT"

    as_of_candidates = [
        sources[key].get("as_of")
        for key in ("channel_registry", "process_gate", "roadmap")
        if sources[key].get("as_of")
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
            "conflicts": conflicts,
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    return {
        "project": "Asset Agent ASA",
        "short_name": "AAA",
        "projection": {
            "status": projection_status,
            "current_as_of": current_as_of,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source": "Persistent Control Plane deterministic read model",
            "source_state_id": sha256_hex(projection_material),
            "conflicts": conflicts,
            "sources": sources,
        },
        "authority": {
            "authority_holder": {
                "authority_id": "PROJECT_OWNER",
                "display_name": "Project Owner / 연구책임자",
                "responsibilities": _OWNER_AUTHORITY,
                "source_ref": str(org_path.relative_to(root)) if org_path else None,
            },
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
            "roadmap_id": roadmap.get("roadmap_id"),
            "version": roadmap.get("version"),
            "status": roadmap.get("status"),
            "current_stage": current_stage,
            "current_gate": current_gate,
            "current_stage_state": _normalize_execution_state(raw_stage_state),
            "stages": stage_rows,
            "validator_modifications": roadmap.get("validator_modifications", []),
            "source_ref": str(roadmap_path.relative_to(root)) if roadmap_path else None,
        },
        "historical_runs": [p09, t18],
        "ui_contract": {
            "persona_is_not_channel": True,
            "no_execution_inference_without_evidence": True,
            "unknown_is_visible": True,
            "stale_is_visible": True,
            "conflict_is_visible": True,
            "read_only": True,
        },
    }
