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

from aaa.core.balanced_v1 import IdentityEnvelope, SchemaRef
from aaa.core.execution_v1 import DependencyLockRef, LogicalRunSpec, RunAttempt, require_new_logical_run
from aaa.core.governance_v1 import (
    ActorRef,
    ActorType,
    AuthorityRef,
    Decision,
    ExactTargetDecisionReceipt,
    ExactTargetIdentity,
    ExactTargetKind,
    ExecutionProvenanceReceipt,
    MaterialInputProvenanceRef,
    OperationalEvent,
    OperationalEventFamily,
    OperationalEventRegistry,
)


class BalancedV1E3Tests(unittest.TestCase):
    def _actor(self, identity: str = "worker-1") -> ActorRef:
        return ActorRef(ActorType.WORKER, identity)

    def _authority(self, identity: str = "SEMI-CONTROL-ARCHITECT") -> AuthorityRef:
        return AuthorityRef(
            authority_role="SEMI_CONTROL_ARCHITECT",
            authority_identity=identity,
            authority_scope="BOUNDED_ENGINEERING",
            authority_source_ref="DECISION-AUTH-1",
        )

    def _spec(self, *, lock_sha: str = "1" * 64) -> LogicalRunSpec:
        return LogicalRunSpec(
            run_id="RUN-E3-001",
            project_namespace="SEMICONDUCTOR_RESEARCH",
            process_id="E3-TEST",
            work_order_ref="WO-E3-TEST",
            responsible_persona="SEMI-CONTROL-ARCHITECT",
            executor_role="BOUNDED_ENGINEERING_IMPLEMENTATION",
            repository_identity="github-repo-id:1334403184",
            exact_target_commit="a" * 40,
            execution_profile_ref="PROFILE-E3-v1",
            execution_profile_sha256="b" * 64,
            configuration_sha256="c" * 64,
            dependency_lock_refs=(DependencyLockRef("requirements.lock", lock_sha),),
            material_input_refs=(IdentityEnvelope("SEMICONDUCTOR_RESEARCH", "DATASET", "DATA-1"),),
            schema_family_version_refs=(SchemaRef("MODEL_INPUT_SCHEMA", "MIS-v1.0"),),
            created_at=datetime(2026, 8, 16, 9, 0, tzinfo=timezone.utc),
        )

    def test_actor_and_authority_are_separate_even_when_identity_matches(self) -> None:
        actor = ActorRef(ActorType.PERSONA_INSTANCE, "SEMI-CONTROL-ARCHITECT")
        authority = self._authority("SEMI-CONTROL-ARCHITECT")
        self.assertEqual(actor.actor_identity, authority.authority_identity)
        self.assertNotEqual(actor, authority)
        self.assertTrue(authority.authority_source_ref)

    def test_worker_capability_does_not_construct_authority(self) -> None:
        actor = self._actor()
        self.assertFalse(hasattr(actor, "authority_scope"))
        with self.assertRaises(ValueError):
            AuthorityRef("", actor.actor_identity, "CUTOVER", "")

    def test_floating_target_aliases_are_rejected(self) -> None:
        for alias in ("latest", "HEAD", "main", "refs/heads/aaa-integration-v0.2"):
            with self.subTest(alias=alias), self.assertRaises(ValueError):
                ExactTargetIdentity(ExactTargetKind.ARTIFACT_IDENTITY, alias)

    def test_git_commit_target_must_be_exact_sha(self) -> None:
        with self.assertRaises(ValueError):
            ExactTargetIdentity(ExactTargetKind.GIT_COMMIT, "aaa-integration-v0.2")
        ExactTargetIdentity(ExactTargetKind.GIT_COMMIT, "a" * 40)

    def test_approval_target_x_does_not_authorize_y(self) -> None:
        x = ExactTargetIdentity(ExactTargetKind.GIT_COMMIT, "a" * 40)
        y = ExactTargetIdentity(ExactTargetKind.GIT_COMMIT, "b" * 40)
        receipt = ExactTargetDecisionReceipt(
            "DEC-1", "ARCHITECTURE_EXACT_FREEZE", x, self._authority(), self._actor(),
            Decision.APPROVE, datetime.now(timezone.utc),
        )
        self.assertTrue(receipt.authorizes(x))
        self.assertFalse(receipt.authorizes(y))

    def test_revoke_and_supersede_require_prior_receipt_ref(self) -> None:
        target = ExactTargetIdentity(ExactTargetKind.CONTENT_SHA256, "a" * 64)
        with self.assertRaises(ValueError):
            ExactTargetDecisionReceipt(
                "DEC-R", "RELEASE", target, self._authority(), self._actor(),
                Decision.REVOKE, datetime.now(timezone.utc),
            )
        with self.assertRaises(ValueError):
            ExactTargetDecisionReceipt(
                "DEC-S", "RELEASE", target, self._authority(), self._actor(),
                Decision.SUPERSEDE, datetime.now(timezone.utc),
            )

    def test_dependency_lock_change_requires_new_logical_run(self) -> None:
        before = self._spec(lock_sha="1" * 64)
        after = self._spec(lock_sha="2" * 64)
        self.assertTrue(require_new_logical_run(before, after))

    def test_dependency_lock_order_is_deterministic(self) -> None:
        base = self._spec()
        second_lock = DependencyLockRef("package-lock.json", "2" * 64)
        first = LogicalRunSpec(**{**base.__dict__, "dependency_lock_refs": (base.dependency_lock_refs[0], second_lock)})
        second = LogicalRunSpec(**{**base.__dict__, "dependency_lock_refs": (second_lock, base.dependency_lock_refs[0])})
        self.assertEqual(first.exact_execution_spec_hash, second.exact_execution_spec_hash)

    def test_dirty_execution_provenance_fails_closed(self) -> None:
        with self.assertRaises(ValueError):
            ExecutionProvenanceReceipt(
                "PROV-1", "RUN-E3-001", "ATT-E3-1", "github-repo-id:1334403184",
                "a" * 40, "d" * 40, False, "PROFILE-E3-v1", "v1", "b" * 64,
                (DependencyLockRef("requirements.lock", "1" * 64),), "c" * 64,
                (MaterialInputProvenanceRef(IdentityEnvelope("SEMICONDUCTOR_RESEARCH", "DATASET", "DATA-1")),),
                "python-3.12", self._actor(), datetime.now(timezone.utc),
            )

    def test_complete_provenance_matches_bound_logical_run_and_attempt(self) -> None:
        spec = self._spec()
        attempt = RunAttempt("ATT-E3-1", spec.run_id, 1, spec.exact_execution_spec_hash)
        provenance = ExecutionProvenanceReceipt(
            "PROV-1", spec.run_id, attempt.run_attempt_id, spec.repository_identity,
            spec.exact_target_commit, "d" * 40, True, spec.execution_profile_ref, "v1",
            spec.execution_profile_sha256, spec.dependency_lock_refs, spec.configuration_sha256,
            (MaterialInputProvenanceRef(spec.material_input_refs[0], content_sha256="e" * 64),),
            "python-3.12", self._actor(), datetime.now(timezone.utc),
        )
        provenance.verify_against(spec, attempt)

    def test_provenance_dependency_lock_mismatch_fails_closed(self) -> None:
        spec = self._spec()
        attempt = RunAttempt("ATT-E3-1", spec.run_id, 1, spec.exact_execution_spec_hash)
        provenance = ExecutionProvenanceReceipt(
            "PROV-1", spec.run_id, attempt.run_attempt_id, spec.repository_identity,
            spec.exact_target_commit, "d" * 40, True, spec.execution_profile_ref, "v1",
            spec.execution_profile_sha256, (DependencyLockRef("requirements.lock", "2" * 64),),
            spec.configuration_sha256,
            (MaterialInputProvenanceRef(spec.material_input_refs[0]),),
            "python-3.12", self._actor(), datetime.now(timezone.utc),
        )
        with self.assertRaises(ValueError):
            provenance.verify_against(spec, attempt)

    def _event(self, *, event_id: str = "EVT-1", family: OperationalEventFamily = OperationalEventFamily.RUN_LIFECYCLE,
               producer: str = "worker-scope", idem: str = "idem-1", seq: int = 1, payload: str = "f" * 64,
               event_type: str = "RUN_CREATED") -> OperationalEvent:
        return OperationalEvent(
            operational_event_id=event_id,
            project_namespace="SEMICONDUCTOR_RESEARCH",
            event_family=family,
            event_type=event_type,
            event_schema_version="OP-EVT-v1",
            aggregate_ref=IdentityEnvelope("SEMICONDUCTOR_RESEARCH", "LOGICAL_RUN", "RUN-1"),
            sequence_number=seq,
            observed_at=datetime(2026, 8, 16, 9, 0, tzinfo=timezone.utc),
            actor_ref=self._actor(),
            authority_ref=self._authority(),
            producer_or_actor_scope=producer,
            idempotency_scope_key=idem,
            payload_sha256=payload,
        )

    def test_operational_event_exact_reappend_is_idempotent(self) -> None:
        registry = OperationalEventRegistry()
        event = self._event()
        self.assertTrue(registry.append(event))
        self.assertFalse(registry.append(event))

    def test_operational_event_identity_collision_different_payload_fails(self) -> None:
        registry = OperationalEventRegistry()
        registry.append(self._event())
        with self.assertRaises(ValueError):
            registry.append(self._event(payload="0" * 64))

    def test_idempotency_key_is_scoped_not_global(self) -> None:
        registry = OperationalEventRegistry()
        registry.append(self._event(event_id="EVT-1", producer="worker-a", idem="same", seq=1))
        registry.append(self._event(event_id="EVT-2", producer="worker-b", idem="same", seq=2))
        registry.append(self._event(event_id="EVT-3", family=OperationalEventFamily.RESULT, producer="worker-a", idem="same", seq=3, event_type="RESULT_WRITTEN"))
        with self.assertRaises(ValueError):
            registry.append(self._event(event_id="EVT-4", producer="worker-a", idem="same", seq=4))

    def test_aggregate_sequence_duplicate_fails_closed(self) -> None:
        registry = OperationalEventRegistry()
        registry.append(self._event(event_id="EVT-1", idem="id-1", seq=1))
        with self.assertRaises(ValueError):
            registry.append(self._event(event_id="EVT-2", idem="id-2", seq=1))

    def test_operational_event_family_cannot_be_economic_event(self) -> None:
        values = {item.value for item in OperationalEventFamily}
        self.assertNotIn("ECONOMIC_EVENT", values)

    def test_contracts_and_dependency_bound_logical_run_successor_exist(self) -> None:
        contracts = ROOT / "aaa" / "contracts"
        for name in (
            "actor_authority_refs_v1.schema.json",
            "exact_target_decision_receipt_v1.schema.json",
            "execution_provenance_receipt_v1.schema.json",
            "operational_event_v1.schema.json",
            "logical_run_v1_1.schema.json",
        ):
            payload = json.loads((contracts / name).read_text(encoding="utf-8"))
            self.assertEqual(payload["$schema"], "https://json-schema.org/draft/2020-12/schema")
        legacy_e2 = json.loads((contracts / "logical_run_v1.schema.json").read_text(encoding="utf-8"))
        self.assertNotIn("dependency_lock_refs", legacy_e2.get("required", []))
        successor = json.loads((contracts / "logical_run_v1_1.schema.json").read_text(encoding="utf-8"))
        self.assertIn("dependency_lock_refs", successor["required"])

    def test_migration_0008_is_forward_only_and_manifest_exact(self) -> None:
        manifest = json.loads((ROOT / "aaa" / "db" / "MIGRATIONS.json").read_text(encoding="utf-8"))
        observed = {item["version"]: item for item in manifest["migrations"]}
        self.assertEqual(observed["0007"]["sha256"], "d8dc393501622cfb570c6bd6759a2d2ce79e8d28ce909037856f7e5a4f52bd55")
        self.assertEqual(observed["0008"]["sha256"], "58455f35e83852330b8933444dd5d4deb8fc730e7d8e48f965e998688b096de6")
        self.assertEqual(hashlib.sha256((ROOT / observed["0008"]["path"]).read_bytes()).hexdigest(), observed["0008"]["sha256"])
        self.assertFalse(manifest["balanced_v1"]["postgresql_authoritative"])
        self.assertFalse(manifest["balanced_v1"]["live_successor_execution_authorized"])


if __name__ == "__main__":
    unittest.main()
