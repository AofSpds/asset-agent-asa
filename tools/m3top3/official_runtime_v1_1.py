from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable, Mapping

from .release_vdi_v1 import validate_official_coverage_release
from .runtime_v1 import build_engine
from .shared_interface_guards_v1 import SharedInterfaceGuardError
from .shared_interface_guards_v1_1 import F02_COMPATIBILITY_NOTE_PATH, REPO_ROOT
from .shared_interface_guards_v1_2 import (
    EvidenceResolverRelease,
    NumericRuleResolverRelease,
    validate_consumed_value_provenance_v1_2,
    validate_f08_freshness_provenance_v1_2,
    verify_control_fix_asset_bindings,
    verify_shared_asset_bindings,
)

OFFICIAL_RUNTIME_VERSION = "M3TOP3-v1-OFFICIAL-RUNTIME-SHARED-WIRING-CONTROL-FIX-v1.1_WORKING"


class OfficialReleaseRuntimeV11Error(ValueError):
    pass


def score_official_snapshot_records_v1_1(
    records: Iterable[dict[str, Any]],
    *,
    code_identity: str,
    validation_dataset_release_id: str,
    denominator_policy_version: str,
    evidence_resolver: EvidenceResolverRelease,
    record_level_bindings_by_company: Mapping[str, Mapping[str, Mapping[str, Any]]],
    certification_resolver: Mapping[str, str] | None = None,
    numeric_rule_resolver: NumericRuleResolverRelease | None = None,
    repo_root: str | Path = REPO_ROOT,
    config_path: str | Path | None = None,
) -> dict[str, Any]:
    rows = list(records)
    if not rows:
        raise OfficialReleaseRuntimeV11Error("official scoring requires at least one record")
    if not isinstance(evidence_resolver, EvidenceResolverRelease):
        raise SharedInterfaceGuardError(
            "official runtime requires governed EvidenceResolverRelease; caller mapping is prohibited"
        )
    if evidence_resolver.test_only:
        raise SharedInterfaceGuardError("TEST_ONLY evidence resolver prohibited in official runtime")
    evidence_resolver.validate_binding(repo_root, allow_test_resolver=False)
    if numeric_rule_resolver is not None:
        if not isinstance(numeric_rule_resolver, NumericRuleResolverRelease):
            raise SharedInterfaceGuardError(
                "official runtime requires governed NumericRuleResolverRelease"
            )
        if numeric_rule_resolver.test_only:
            raise SharedInterfaceGuardError(
                "TEST_ONLY numeric-rule resolver prohibited in official runtime"
            )
        numeric_rule_resolver.validate_binding(repo_root, allow_test_resolver=False)

    shared_assets = verify_shared_asset_bindings(repo_root)
    control_fix_assets = verify_control_fix_asset_bindings(repo_root)
    pit_pass: dict[str, bool] = {}
    freshness_pass: dict[str, bool] = {}
    resolved_scopes: dict[str, Any] = {}

    for row in rows:
        cid = str(row["company_id"])
        record_bindings = record_level_bindings_by_company.get(cid)
        if not isinstance(record_bindings, Mapping):
            raise SharedInterfaceGuardError(
                f"{cid}: record-level consumed-scope binding set required"
            )
        resolved_scopes[cid] = validate_consumed_value_provenance_v1_2(
            row,
            evidence_resolver=evidence_resolver,
            record_level_bindings=record_bindings,
            certification_resolver=certification_resolver,
            repo_root=repo_root,
            allow_test_resolver=False,
        )
        pit_pass[cid] = True
        validate_f08_freshness_provenance_v1_2(
            row,
            evidence_resolver=evidence_resolver,
            numeric_rule_resolver=numeric_rule_resolver,
            repo_root=repo_root,
            allow_test_resolver=False,
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
        "control_fix_asset_binding": control_fix_assets,
        "resolved_authoritative_scopes": resolved_scopes,
        "score_result": score_result,
        "vdi_release_validation": vdi,
        "evidence_resolver_binding": {
            "release_id": evidence_resolver.release_id,
            "release_content_sha256": evidence_resolver.release_content_sha256,
            "persistent_locator": evidence_resolver.persistent_locator,
        },
        "numeric_rule_resolver_binding": (
            None
            if numeric_rule_resolver is None
            else {
                "release_id": numeric_rule_resolver.release_id,
                "release_content_sha256": numeric_rule_resolver.release_content_sha256,
                "persistent_locator": numeric_rule_resolver.persistent_locator,
            }
        ),
        "f02_compatibility_note_binding": {
            "path": F02_COMPATIBILITY_NOTE_PATH,
            "status": shared_assets[F02_COMPATIBILITY_NOTE_PATH]["status"],
            "sha256": shared_assets[F02_COMPATIBILITY_NOTE_PATH]["sha256"],
        },
        "actual_replay_authorized": False,
        "model_freeze_authorized": False,
    }


__all__ = [
    "OFFICIAL_RUNTIME_VERSION",
    "OfficialReleaseRuntimeV11Error",
    "score_official_snapshot_records_v1_1",
]
