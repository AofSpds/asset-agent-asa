from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable, Mapping

from .release_vdi_v1 import validate_official_coverage_release
from .runtime_v1 import build_engine
from .shared_interface_guards_v1_1 import (
    F02_COMPATIBILITY_NOTE_PATH,
    REPO_ROOT,
    validate_consumed_value_provenance_v1_1,
    validate_f08_freshness_provenance_v1_1,
    verify_shared_asset_bindings,
)

OFFICIAL_RUNTIME_VERSION = "M3TOP3-v1-OFFICIAL-RUNTIME-SHARED-WIRING-v1.0_WORKING"


class OfficialReleaseRuntimeError(ValueError):
    pass


def score_official_snapshot_records(
    records: Iterable[dict[str, Any]],
    *,
    code_identity: str,
    validation_dataset_release_id: str,
    denominator_policy_version: str,
    evidence_resolver: Mapping[str, Any],
    certification_resolver: Mapping[str, str] | None = None,
    typed_refresh_rules: Mapping[str, Mapping[str, Any]] | None = None,
    repo_root: str | Path = REPO_ROOT,
    config_path: str | Path | None = None,
) -> dict[str, Any]:
    rows = list(records)
    if not rows:
        raise OfficialReleaseRuntimeError("official scoring requires at least one record")

    shared_assets = verify_shared_asset_bindings(repo_root)
    pit_pass: dict[str, bool] = {}
    freshness_pass: dict[str, bool] = {}
    resolved_scopes: dict[str, Any] = {}

    for row in rows:
        cid = str(row["company_id"])
        resolved_scopes[cid] = validate_consumed_value_provenance_v1_1(
            row,
            evidence_resolver=evidence_resolver,
            certification_resolver=certification_resolver,
            repo_root=repo_root,
        )
        pit_pass[cid] = True
        validate_f08_freshness_provenance_v1_1(
            row,
            typed_refresh_rules=typed_refresh_rules,
            evidence_resolver=evidence_resolver,
            repo_root=repo_root,
        )
        freshness_pass[cid] = True

    if config_path is None:
        engine = build_engine(code_identity=code_identity)
    else:
        engine = build_engine(code_identity=code_identity, config_path=config_path)
    score_result = engine.score_snapshot(rows)
    vdi = validate_official_coverage_release(
        score_result,
        validation_dataset_release_id=validation_dataset_release_id,
        denominator_policy_version=denominator_policy_version,
        pit_validation_passed=pit_pass,
        freshness_validation_passed=freshness_pass,
    )

    return {
        "official_runtime_version": OFFICIAL_RUNTIME_VERSION,
        "shared_asset_binding": shared_assets,
        "resolved_authoritative_scopes": resolved_scopes,
        "score_result": score_result,
        "vdi_release_validation": vdi,
        "f02_compatibility_note_binding": {
            "path": F02_COMPATIBILITY_NOTE_PATH,
            "status": shared_assets[F02_COMPATIBILITY_NOTE_PATH]["status"],
            "sha256": shared_assets[F02_COMPATIBILITY_NOTE_PATH]["sha256"],
        },
        "actual_replay_authorized": False,
        "model_freeze_authorized": False,
    }
