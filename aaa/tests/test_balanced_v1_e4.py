from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "aaa" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aaa.core.governance_v1 import (
    ActorRef,
    ActorType,
    AuthorityRef,
    Decision,
    ExactTargetDecisionReceipt,
    ExactTargetIdentity,
    ExactTargetKind,
)
from aaa.core.release_v1 import (
    CompatibleVersionSet,
    ComponentKind,
    DestinationReceipt,
    DestinationStatus,
    ImmutableArtifactRef,
    PromotionReceipt,
    PromotionStatus,
    ReleaseComponentRef,
    RestoreManifest,
    RestoreStatus,
)


class BalancedV1E4Tests(unittest.TestCase):
    def _actor(self) -> ActorRef:
        return ActorRef(ActorType.PERSONA_INSTANCE, "SEMI-CONTROL-ARCHITECT")

    def _authority(self, scope: str = "RELEASE") -> AuthorityRef:
        return AuthorityRef("PROJECT_OWNER", "PROJECT_OWNER", scope, "OWNER-AUTHORITY-MATRIX")

    def _components(self, *, model_hash: str = "a" * 64, verified: bool = True) -> tuple[ReleaseComponentRef, ...]:
        return (
            ReleaseComponentRef(ComponentKind.MODEL, "MODEL-1", "v1.0", model_hash, verified=verified),
            ReleaseComponentRef(
                ComponentKind.SHARED_CONTRACT,
                "SEMI-SHARED-CONTRACT-STATE",
                "v0.7_WORKING",
                "b" * 40,
                byte_size=4096,
                persistent_locator="git:control/continuity/v1.0/SEMI-SHARED-CONTRACT-STATE_v0.7_WORKING.yaml",
                verified=verified,
            ),
        )

    def _release_set(self, *, release_id: str = "RELEASE-SET-1", components=None) -> CompatibleVersionSet:
        return CompatibleVersionSet(
            release_id,
            tuple(components or self._components()),
            "COMPAT-DECL-1",
            "DEC-RELEASE-1",
        )

    def _decision(self, release_set: CompatibleVersionSet) -> ExactTargetDecisionReceipt:
        return ExactTargetDecisionReceipt(
            release_set.exact_decision_receipt_ref,
            "RELEASE",
            release_set.exact_target,
            self._authority("RELEASE"),
            self._actor(),
            Decision.APPROVE,
            datetime.now(timezone.utc),
        )

    def test_floating_component_identity_or_version_rejected(self) -> None:
        with self.assertRaises(ValueError):
            ReleaseComponentRef(ComponentKind.MODEL, "MODEL-1", "latest", "a" * 64)
        with self.assertRaises(ValueError):
            ReleaseComponentRef(ComponentKind.MODEL, "latest", "v1.0", "a" * 64)

    def test_component_set_hash_is_order_independent(self) -> None:
        components = self._components()
        first = self._release_set(components=components)
        second = self._release_set(components=tuple(reversed(components)))
        self.assertEqual(first.component_set_sha256, second.component_set_sha256)

    def test_material_component_change_changes_release_set_hash(self) -> None:
        before = self._release_set()
        after = self._release_set(components=self._components(model_hash="c" * 64))
        self.assertNotEqual(before.component_set_sha256, after.component_set_sha256)

    def test_exact_decision_must_authorize_same_release_set_identity_and_hash(self) -> None:
        release_set = self._release_set()
        release_set.verify_release_decision(self._decision(release_set))
        other = self._release_set(release_id="RELEASE-SET-2")
        with self.assertRaises(ValueError):
            release_set.verify_release_decision(self._decision(other))

    def test_unverified_component_cannot_complete_promotion(self) -> None:
        release_set = self._release_set(components=self._components(verified=False))
        receipt = PromotionReceipt(
            "PROMO-1", "SHADOW_PROMOTION", release_set, self._decision(release_set),
            "ACTOR", "AUTHORITY",
            (DestinationReceipt("S3", "shadow", DestinationStatus.VERIFIED, "OBJ-1", "d" * 64, 100),),
            datetime.now(timezone.utc),
        )
        self.assertEqual(receipt.status, PromotionStatus.FAILED_NO_PROMOTION)
        self.assertEqual(receipt.canonical_pointer_after("OLD-SET"), "OLD-SET")

    def test_partial_multi_store_failure_keeps_pointer_unchanged(self) -> None:
        release_set = self._release_set()
        receipt = PromotionReceipt(
            "PROMO-2", "SHADOW_PROMOTION", release_set, self._decision(release_set),
            "ACTOR", "AUTHORITY",
            (
                DestinationReceipt("S3", "shadow", DestinationStatus.VERIFIED, "OBJ-1", "d" * 64, 100),
                DestinationReceipt("GIT", "shadow", DestinationStatus.FAILED),
            ),
            datetime.now(timezone.utc),
        )
        self.assertEqual(receipt.status, PromotionStatus.FAILED_PARTIAL_FAIL_CLOSED)
        self.assertEqual(receipt.canonical_pointer_after("OLD-SET"), "OLD-SET")

    def test_verified_all_destinations_updates_only_candidate_pointer(self) -> None:
        release_set = self._release_set()
        receipt = PromotionReceipt(
            "PROMO-3", "SHADOW_PROMOTION", release_set, self._decision(release_set),
            "ACTOR", "AUTHORITY",
            (
                DestinationReceipt("S3", "shadow", DestinationStatus.VERIFIED, "OBJ-1", "d" * 64, 100),
                DestinationReceipt("GIT", "shadow", DestinationStatus.VERIFIED, "OBJ-2", "e" * 64, 200),
            ),
            datetime.now(timezone.utc),
        )
        self.assertEqual(receipt.status, PromotionStatus.COMPLETED_VERIFIED)
        self.assertEqual(receipt.canonical_pointer_after("OLD-SET"), release_set.release_set_id)

    def _restore(self, *, status=RestoreStatus.PREPARED, provider=None, verification=(), qualification=None) -> RestoreManifest:
        return RestoreManifest(
            "RESTORE-1",
            "BACKUP-1",
            "POSTGRESQL_BACKUP",
            "POSTGRESQL",
            ("0001", "0002", "0003", "0004", "0005", "0006", "0007", "0008", "0009"),
            (ImmutableArtifactRef("ARTIFACT-1", "f" * 64, 1234, "s3://immutable/artifact-1"),),
            "PG-RESTORE-TARGET-1",
            "VERIFY-PLAN-1",
            status,
            provider_metadata=provider or {},
            verification_result_refs=tuple(verification),
            managed_pitr_rpo_rto_qualification_ref=qualification,
        )

    def test_provider_metadata_does_not_change_restore_semantic_identity(self) -> None:
        aws = self._restore(provider={"provider": "aws", "region": "ap-northeast-2"})
        local = self._restore(provider={"provider": "local-docker"})
        self.assertEqual(aws.semantic_identity_sha256, local.semantic_identity_sha256)

    def test_restore_verified_requires_verification_evidence(self) -> None:
        with self.assertRaises(ValueError):
            self._restore(status=RestoreStatus.RESTORED_VERIFIED)

    def test_local_restore_verification_does_not_satisfy_managed_qualification(self) -> None:
        restore = self._restore(status=RestoreStatus.RESTORED_VERIFIED, verification=("VERIFY-RESULT-1",))
        self.assertTrue(restore.recovery_verified)
        self.assertFalse(restore.managed_qualification_satisfied)
        target = ExactTargetIdentity(ExactTargetKind.ARTIFACT_IDENTITY, restore.restore_target_identity)
        cutover = ExactTargetDecisionReceipt(
            "DEC-CUTOVER", "POSTGRESQL_OPERATIONAL_SOT_CUTOVER", target,
            self._authority("POSTGRESQL_OPERATIONAL_SOT_CUTOVER"), self._actor(),
            Decision.APPROVE, datetime.now(timezone.utc),
        )
        self.assertFalse(restore.may_become_operational_sot(cutover))

    def test_verified_restore_still_requires_separate_exact_cutover_decision(self) -> None:
        restore = self._restore(
            status=RestoreStatus.RESTORED_VERIFIED,
            verification=("VERIFY-RESULT-1",),
            qualification="MANAGED-PITR-QUAL-1",
        )
        self.assertFalse(restore.may_become_operational_sot(None))
        wrong = ExactTargetDecisionReceipt(
            "DEC-WRONG", "POSTGRESQL_OPERATIONAL_SOT_CUTOVER",
            ExactTargetIdentity(ExactTargetKind.ARTIFACT_IDENTITY, "OTHER-TARGET"),
            self._authority("POSTGRESQL_OPERATIONAL_SOT_CUTOVER"), self._actor(),
            Decision.APPROVE, datetime.now(timezone.utc),
        )
        self.assertFalse(restore.may_become_operational_sot(wrong))

    def test_restore_schema_version_set_rejects_latest(self) -> None:
        with self.assertRaises(ValueError):
            RestoreManifest(
                "RESTORE-X", "BACKUP-X", "POSTGRESQL_BACKUP", "POSTGRESQL",
                ("0001", "latest"),
                (ImmutableArtifactRef("A", "a" * 64, 1, "s3://a"),),
                "TARGET-X", "VERIFY-X", RestoreStatus.PREPARED,
            )

    def test_e4_contract_files_and_migration_manifest(self) -> None:
        contracts = ROOT / "aaa" / "contracts"
        for name in (
            "compatible_version_set_release_manifest_v1.schema.json",
            "promotion_receipt_v1.schema.json",
            "restore_manifest_v1.schema.json",
        ):
            payload = json.loads((contracts / name).read_text(encoding="utf-8"))
            self.assertEqual(payload["$schema"], "https://json-schema.org/draft/2020-12/schema")
        manifest = json.loads((ROOT / "aaa" / "db" / "MIGRATIONS.json").read_text(encoding="utf-8"))
        observed = {item["version"]: item for item in manifest["migrations"]}
        self.assertEqual(observed["0009"]["sha256"], "86c4827a834e62d4319ba2a1c3c238320f095f3e2bbb199ff42f5c90e1e22ec2")
        self.assertEqual(hashlib.sha256((ROOT / observed["0009"]["path"]).read_bytes()).hexdigest(), observed["0009"]["sha256"])
        self.assertFalse(manifest["balanced_v1"]["postgresql_authoritative"])
        self.assertTrue(manifest["balanced_v1"]["json_registry_operational_authority_during_shadow"])
        self.assertFalse(manifest["balanced_v1"]["production_canonical_promotion_authorized"])


if __name__ == "__main__":
    unittest.main()
