from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import hashlib
import json
import re
from typing import Mapping

from aaa.core.governance_v1 import Decision, ExactTargetDecisionReceipt, ExactTargetIdentity, ExactTargetKind


_SHA40_RE = re.compile(r"^[0-9a-f]{40}$")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def _nonempty(name: str, value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    if value.strip().lower() in {"latest", "head", "current"}:
        raise ValueError(f"{name} cannot use a floating alias")
    return value


def _sha256(name: str, value: str) -> str:
    if not _SHA256_RE.fullmatch(value):
        raise ValueError(f"{name} must be a lowercase 64-character SHA256")
    return value


def _content_identity(name: str, value: str) -> str:
    if not (_SHA256_RE.fullmatch(value) or _SHA40_RE.fullmatch(value)):
        raise ValueError(f"{name} must be an exact SHA256 or Git SHA")
    return value


def _aware(name: str, value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")
    return value


class ComponentKind(str, Enum):
    SCHEMA = "SCHEMA"
    MODEL = "MODEL"
    FEATURE_SPEC = "FEATURE_SPEC"
    MODEL_INPUT_CONTRACT = "MODEL_INPUT_CONTRACT"
    SCORER_IO = "SCORER_IO"
    EXECUTION_PROFILE = "EXECUTION_PROFILE"
    RUNTIME_SOURCE = "RUNTIME_SOURCE"
    CONFIGURATION = "CONFIGURATION"
    DATASET = "DATASET"
    SNAPSHOT = "SNAPSHOT"
    PIT_CONTRACT = "PIT_CONTRACT"
    VALIDATION_DATASET = "VALIDATION_DATASET"
    CALENDAR_WINDOW_MAPPING = "CALENDAR_WINDOW_MAPPING"
    SHARED_CONTRACT = "SHARED_CONTRACT"
    MODEL_ARTIFACT_RELEASE_MANIFEST = "MODEL_ARTIFACT_RELEASE_MANIFEST"


@dataclass(frozen=True, order=True)
class ReleaseComponentRef:
    component_kind: ComponentKind
    immutable_identity: str
    version: str
    content_hash_or_git_identity: str
    byte_size: int | None = None
    persistent_locator: str | None = None
    verified: bool = True

    def __post_init__(self) -> None:
        _nonempty("immutable_identity", self.immutable_identity)
        _nonempty("version", self.version)
        _content_identity("content_hash_or_git_identity", self.content_hash_or_git_identity)
        if self.byte_size is not None and self.byte_size < 0:
            raise ValueError("byte_size must be non-negative")
        if self.persistent_locator is not None:
            _nonempty("persistent_locator", self.persistent_locator)
        persisted = self.byte_size is not None or self.persistent_locator is not None
        if persisted and (self.byte_size is None or self.persistent_locator is None):
            raise ValueError("persisted components require both byte_size and persistent_locator")

    def canonical_payload(self) -> dict[str, object]:
        return {
            "component_kind": self.component_kind.value,
            "immutable_identity": self.immutable_identity,
            "version": self.version,
            "content_hash_or_git_identity": self.content_hash_or_git_identity,
            "byte_size": self.byte_size,
            "persistent_locator": self.persistent_locator,
        }


@dataclass(frozen=True)
class CompatibleVersionSet:
    release_set_id: str
    components: tuple[ReleaseComponentRef, ...]
    compatibility_declaration_ref: str
    exact_decision_receipt_ref: str

    def __post_init__(self) -> None:
        _nonempty("release_set_id", self.release_set_id)
        _nonempty("compatibility_declaration_ref", self.compatibility_declaration_ref)
        _nonempty("exact_decision_receipt_ref", self.exact_decision_receipt_ref)
        if not self.components:
            raise ValueError("compatible version set requires at least one component")
        keys = [(c.component_kind.value, c.immutable_identity, c.version) for c in self.components]
        if len(set(keys)) != len(keys):
            raise ValueError("duplicate component identity/version in release set")

    @property
    def component_set_sha256(self) -> str:
        payload = [
            c.canonical_payload()
            for c in sorted(
                self.components,
                key=lambda c: (c.component_kind.value, c.immutable_identity, c.version, c.content_hash_or_git_identity),
            )
        ]
        canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(canonical).hexdigest()

    @property
    def exact_target(self) -> ExactTargetIdentity:
        return ExactTargetIdentity(
            ExactTargetKind.RELEASE_SET,
            self.release_set_id,
            content_sha256=self.component_set_sha256,
        )

    def verify_release_decision(self, receipt: ExactTargetDecisionReceipt) -> None:
        if receipt.decision is not Decision.APPROVE or not receipt.authorizes(self.exact_target):
            raise ValueError("exact Decision Receipt does not authorize this immutable release set")

    @property
    def all_components_verified(self) -> bool:
        return all(component.verified for component in self.components)


class PromotionStatus(str, Enum):
    PREPARED = "PREPARED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED_VERIFIED = "COMPLETED_VERIFIED"
    FAILED_NO_PROMOTION = "FAILED_NO_PROMOTION"
    FAILED_PARTIAL_FAIL_CLOSED = "FAILED_PARTIAL_FAIL_CLOSED"


class DestinationStatus(str, Enum):
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    FAILED = "FAILED"


@dataclass(frozen=True)
class DestinationReceipt:
    destination_store: str
    destination_namespace: str
    status: DestinationStatus
    object_identity: str | None = None
    content_sha256: str | None = None
    byte_size: int | None = None

    def __post_init__(self) -> None:
        _nonempty("destination_store", self.destination_store)
        _nonempty("destination_namespace", self.destination_namespace)
        if self.object_identity is not None:
            _nonempty("object_identity", self.object_identity)
        if self.content_sha256 is not None:
            _sha256("content_sha256", self.content_sha256)
        if self.byte_size is not None and self.byte_size < 0:
            raise ValueError("byte_size must be non-negative")
        if self.status is DestinationStatus.VERIFIED:
            if self.object_identity is None or self.content_sha256 is None or self.byte_size is None:
                raise ValueError("verified destination requires exact object identity/hash/size")


@dataclass(frozen=True)
class PromotionReceipt:
    promotion_id: str
    promotion_kind: str
    release_set: CompatibleVersionSet
    decision_receipt: ExactTargetDecisionReceipt
    actor_ref: str
    authority_ref: str
    destinations: tuple[DestinationReceipt, ...]
    recorded_at: datetime

    def __post_init__(self) -> None:
        for name in ("promotion_id", "promotion_kind", "actor_ref", "authority_ref"):
            _nonempty(name, getattr(self, name))
        _aware("recorded_at", self.recorded_at)
        if not self.destinations:
            raise ValueError("promotion requires at least one destination")
        destination_keys = [(d.destination_store, d.destination_namespace) for d in self.destinations]
        if len(set(destination_keys)) != len(destination_keys):
            raise ValueError("duplicate promotion destination")
        self.release_set.verify_release_decision(self.decision_receipt)

    @property
    def status(self) -> PromotionStatus:
        verified = sum(d.status is DestinationStatus.VERIFIED for d in self.destinations)
        failed = sum(d.status is DestinationStatus.FAILED for d in self.destinations)
        pending = sum(d.status is DestinationStatus.PENDING for d in self.destinations)
        if failed:
            return PromotionStatus.FAILED_PARTIAL_FAIL_CLOSED if verified else PromotionStatus.FAILED_NO_PROMOTION
        if pending:
            return PromotionStatus.IN_PROGRESS
        if not self.release_set.all_components_verified:
            return PromotionStatus.FAILED_NO_PROMOTION
        return PromotionStatus.COMPLETED_VERIFIED

    def canonical_pointer_after(self, current_pointer: str | None) -> str | None:
        """Return a shadow/candidate pointer; production authority is deliberately external.

        The pointer changes only after all required destination receipts are verified and the
        exact release-set decision is valid. Partial or failed promotion leaves it unchanged.
        """
        if self.status is not PromotionStatus.COMPLETED_VERIFIED:
            return current_pointer
        return self.release_set.release_set_id


class RestoreStatus(str, Enum):
    PREPARED = "PREPARED"
    RESTORED_UNVERIFIED = "RESTORED_UNVERIFIED"
    RESTORED_VERIFIED = "RESTORED_VERIFIED"
    FAILED_FAIL_CLOSED = "FAILED_FAIL_CLOSED"


@dataclass(frozen=True, order=True)
class ImmutableArtifactRef:
    immutable_identity: str
    sha256: str
    byte_size: int
    persistent_locator: str

    def __post_init__(self) -> None:
        _nonempty("immutable_identity", self.immutable_identity)
        _sha256("sha256", self.sha256)
        if self.byte_size < 0:
            raise ValueError("byte_size must be non-negative")
        _nonempty("persistent_locator", self.persistent_locator)


@dataclass(frozen=True)
class RestoreManifest:
    restore_manifest_id: str
    backup_or_snapshot_identity: str
    source_store_kind: str
    target_store_kind: str
    schema_migration_version_set: tuple[str, ...]
    immutable_artifact_refs: tuple[ImmutableArtifactRef, ...]
    restore_target_identity: str
    verification_plan_ref: str
    status: RestoreStatus
    provider_metadata: Mapping[str, str] = field(default_factory=dict)
    verification_result_refs: tuple[str, ...] = field(default_factory=tuple)
    managed_pitr_rpo_rto_qualification_ref: str | None = None

    def __post_init__(self) -> None:
        for name in (
            "restore_manifest_id",
            "backup_or_snapshot_identity",
            "source_store_kind",
            "target_store_kind",
            "restore_target_identity",
            "verification_plan_ref",
        ):
            _nonempty(name, getattr(self, name))
        if not self.schema_migration_version_set:
            raise ValueError("restore requires exact schema migration version set")
        if any(v.strip().lower() == "latest" or not v.strip() for v in self.schema_migration_version_set):
            raise ValueError("restore schema migration version set must be exact")
        if len(set(self.schema_migration_version_set)) != len(self.schema_migration_version_set):
            raise ValueError("duplicate schema migration version")
        if not self.immutable_artifact_refs:
            raise ValueError("restore requires immutable artifact references")
        if len(set(self.immutable_artifact_refs)) != len(self.immutable_artifact_refs):
            raise ValueError("duplicate immutable artifact reference")
        for key, value in self.provider_metadata.items():
            _nonempty("provider_metadata key", key)
            _nonempty("provider_metadata value", value)
        for ref in self.verification_result_refs:
            _nonempty("verification_result_ref", ref)
        if self.status is RestoreStatus.RESTORED_VERIFIED and not self.verification_result_refs:
            raise ValueError("RESTORED_VERIFIED requires verification evidence")
        if self.managed_pitr_rpo_rto_qualification_ref is not None:
            _nonempty("managed_pitr_rpo_rto_qualification_ref", self.managed_pitr_rpo_rto_qualification_ref)

    @property
    def semantic_identity_sha256(self) -> str:
        """Provider metadata is deliberately excluded from semantic restore identity."""
        payload = {
            "backup_or_snapshot_identity": self.backup_or_snapshot_identity,
            "source_store_kind": self.source_store_kind,
            "target_store_kind": self.target_store_kind,
            "schema_migration_version_set": sorted(self.schema_migration_version_set),
            "immutable_artifact_refs": [
                {
                    "immutable_identity": ref.immutable_identity,
                    "sha256": ref.sha256,
                    "byte_size": ref.byte_size,
                    "persistent_locator": ref.persistent_locator,
                }
                for ref in sorted(self.immutable_artifact_refs)
            ],
            "restore_target_identity": self.restore_target_identity,
            "verification_plan_ref": self.verification_plan_ref,
        }
        canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(canonical).hexdigest()

    @property
    def recovery_verified(self) -> bool:
        return self.status is RestoreStatus.RESTORED_VERIFIED and bool(self.verification_result_refs)

    @property
    def managed_qualification_satisfied(self) -> bool:
        return self.managed_pitr_rpo_rto_qualification_ref is not None

    def may_become_operational_sot(self, cutover_decision: ExactTargetDecisionReceipt | None) -> bool:
        """Restore verification alone can never authorize Operational SoT.

        A separate exact-target Owner cutover decision must authorize the restore target.
        """
        if not self.recovery_verified or not self.managed_qualification_satisfied or cutover_decision is None:
            return False
        target = ExactTargetIdentity(ExactTargetKind.ARTIFACT_IDENTITY, self.restore_target_identity)
        return cutover_decision.decision is Decision.APPROVE and cutover_decision.authorizes(target)
