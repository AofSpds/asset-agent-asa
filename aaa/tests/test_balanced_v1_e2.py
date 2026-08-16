from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "aaa" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aaa.core.balanced_v1 import IdentityEnvelope, SchemaRef, project_legacy_run_semantics
from aaa.core.execution_v1 import (
    AttemptTerminationReceipt,
    LogicalRunFinalDispositionReceipt,
    LogicalRunSpec,
    LogicalRunStatus,
    RetryableDisposition,
    RunAttempt,
    RunAttemptState,
    TerminationClass,
    require_new_logical_run,
    validate_retry_attempt,
)


class BalancedV1E2Tests(unittest.TestCase):
    def _spec(self, *, run_id: str = "RUN-V1-001", target: str = "a" * 40, config: str = "b" * 64) -> LogicalRunSpec:
        return LogicalRunSpec(
            run_id=run_id,
            project_namespace="SEMICONDUCTOR_RESEARCH",
            process_id="TEST-PROCESS",
            work_order_ref="WO-TEST-001",
            responsible_persona="SEMI-CONTROL-ARCHITECT",
            executor_role="BOUNDED_ENGINEERING_IMPLEMENTATION",
            repository_identity="github-repo-id:1334403184",
            exact_target_commit=target,
            execution_profile_ref="PROFILE-TEST-v1",
            execution_profile_sha256="c" * 64,
            configuration_sha256=config,
            material_input_refs=(
                IdentityEnvelope("SEMICONDUCTOR_RESEARCH", "DATASET", "DATASET-A"),
                IdentityEnvelope("SEMICONDUCTOR_RESEARCH", "SNAPSHOT", "SNAP-A"),
            ),
            schema_family_version_refs=(SchemaRef("MODEL_INPUT_SCHEMA", "MIS-v1.0"),),
            created_at=datetime(2026, 8, 16, 18, 0, tzinfo=timezone.utc),
        )

    def test_execution_spec_hash_is_deterministic_and_excludes_run_id_and_created_at(self) -> None:
        first = self._spec(run_id="RUN-A")
        second = self._spec(run_id="RUN-B")
        self.assertEqual(first.exact_execution_spec_hash, second.exact_execution_spec_hash)

    def test_material_target_change_requires_new_logical_run(self) -> None:
        self.assertTrue(require_new_logical_run(self._spec(), self._spec(target="d" * 40)))

    def test_material_configuration_change_requires_new_logical_run(self) -> None:
        self.assertTrue(require_new_logical_run(self._spec(), self._spec(config="e" * 64)))

    def test_input_order_does_not_change_exact_spec_hash(self) -> None:
        first = self._spec()
        second = LogicalRunSpec(
            **{
                **first.__dict__,
                "run_id": "RUN-ORDER-2",
                "material_input_refs": tuple(reversed(first.material_input_refs)),
            }
        )
        self.assertEqual(first.exact_execution_spec_hash, second.exact_execution_spec_hash)

    def test_first_attempt_cannot_be_retry(self) -> None:
        with self.assertRaises(ValueError):
            RunAttempt(
                run_attempt_id="ATTEMPT-1",
                run_id="RUN-1",
                attempt_ordinal=1,
                exact_execution_spec_hash="a" * 64,
                retry_of_attempt_id="ATTEMPT-0",
            )

    def test_retry_attempt_requires_lineage_reason_and_authorization(self) -> None:
        with self.assertRaises(ValueError):
            RunAttempt(
                run_attempt_id="ATTEMPT-2",
                run_id="RUN-1",
                attempt_ordinal=2,
                exact_execution_spec_hash="a" * 64,
                retry_of_attempt_id="ATTEMPT-1",
            )

    def test_same_logical_run_retry_with_same_hash_is_valid(self) -> None:
        spec = self._spec()
        first = RunAttempt("ATT-1", spec.run_id, 1, spec.exact_execution_spec_hash)
        retry = RunAttempt(
            "ATT-2", spec.run_id, 2, spec.exact_execution_spec_hash,
            retry_of_attempt_id="ATT-1", retry_reason_code="INFRA_TIMEOUT",
            retry_authorization_ref="RETRY-POLICY-1",
        )
        validate_retry_attempt(first, retry, spec)

    def test_retry_with_changed_spec_fails_closed(self) -> None:
        before = self._spec()
        after = self._spec(target="d" * 40)
        first = RunAttempt("ATT-1", before.run_id, 1, before.exact_execution_spec_hash)
        retry = RunAttempt(
            "ATT-2", before.run_id, 2, before.exact_execution_spec_hash,
            retry_of_attempt_id="ATT-1", retry_reason_code="RETRY",
            retry_authorization_ref="AUTH-1",
        )
        with self.assertRaises(ValueError):
            validate_retry_attempt(first, retry, after)

    def test_acknowledged_attempt_is_not_running(self) -> None:
        attempt = RunAttempt(
            "ATT-1", "RUN-1", 1, "a" * 64,
            state=RunAttemptState.ACKNOWLEDGED,
            worker_id="worker-1", lease_epoch=1,
        )
        self.assertFalse(attempt.running_at(datetime.now(timezone.utc)))

    def test_running_confirmed_requires_start_heartbeat_and_lease(self) -> None:
        with self.assertRaises(ValueError):
            RunAttempt(
                "ATT-1", "RUN-1", 1, "a" * 64,
                state=RunAttemptState.RUNNING_CONFIRMED,
                worker_id="worker-1", lease_epoch=1,
            )

    def test_running_confirmed_checks_observation_inside_lease(self) -> None:
        now = datetime.now(timezone.utc)
        attempt = RunAttempt(
            "ATT-1", "RUN-1", 1, "a" * 64,
            state=RunAttemptState.RUNNING_CONFIRMED,
            worker_id="worker-1", lease_epoch=1,
            started_at=now - timedelta(seconds=5),
            last_heartbeat_at=now - timedelta(seconds=1),
            lease_expires_at=now + timedelta(seconds=60),
        )
        self.assertTrue(attempt.running_at(now))
        self.assertFalse(attempt.running_at(now + timedelta(seconds=61)))

    def test_terminal_attempt_requires_receipt(self) -> None:
        with self.assertRaises(ValueError):
            RunAttempt(
                "ATT-1", "RUN-1", 1, "a" * 64,
                state=RunAttemptState.TIMED_OUT,
            )

    def test_attempt_termination_receipt_is_timezone_aware(self) -> None:
        with self.assertRaises(ValueError):
            AttemptTerminationReceipt(
                "TERM-1", "RUN-1", "ATT-1", TerminationClass.TIMEOUT,
                RetryableDisposition.RETRYABLE_IF_POLICY_ALLOWS,
                "AUTHORITY", "ACTOR", datetime(2026, 8, 16, 18, 0),
            )

    def test_completed_logical_run_requires_selected_attempt(self) -> None:
        with self.assertRaises(ValueError):
            LogicalRunFinalDispositionReceipt(
                "FINAL-1", "RUN-1", LogicalRunStatus.COMPLETED_PASS,
                "AUTHORITY", "ACTOR", datetime.now(timezone.utc),
            )

    def test_cancelled_logical_run_requires_decision_ref(self) -> None:
        with self.assertRaises(ValueError):
            LogicalRunFinalDispositionReceipt(
                "FINAL-1", "RUN-1", LogicalRunStatus.CANCELLED,
                "AUTHORITY", "ACTOR", datetime.now(timezone.utc),
            )

    def test_legacy_projection_still_never_synthesizes_attempt(self) -> None:
        projected = project_legacy_run_semantics({"run_id": "RUN-T19-HISTORICAL", "state": "COMPLETED_PASS"})
        self.assertEqual(projected["semantic_generation"], "LEGACY_AAA_RUN_V0_X")
        self.assertNotIn("run_attempt_id", projected)

    def test_contract_files_exist_without_changing_legacy_run_schema(self) -> None:
        contracts = ROOT / "aaa" / "contracts"
        for name in (
            "logical_run_v1.schema.json",
            "run_attempt_v1.schema.json",
            "attempt_termination_receipt_v1.schema.json",
            "logical_run_final_disposition_receipt_v1.schema.json",
        ):
            payload = json.loads((contracts / name).read_text(encoding="utf-8"))
            self.assertEqual(payload["$schema"], "https://json-schema.org/draft/2020-12/schema")
        legacy = (contracts / "run_registry_entry.schema.json").read_text(encoding="utf-8")
        self.assertNotIn("run_attempt_id", legacy)

    def test_migration_manifest_preserves_prior_hashes_and_registers_0007(self) -> None:
        manifest = json.loads((ROOT / "aaa" / "db" / "MIGRATIONS.json").read_text(encoding="utf-8"))
        observed = {item["version"]: item for item in manifest["migrations"]}
        expected = {
            "0001": "66e5609fea1104f4aba4d0566989bf3a6c8d2b6e0b75cb274a79f7bdb48d68c2",
            "0002": "dfd47bb167e4bbcef2de9cb45bec811c0acfbcc5f03bde1a49fc24990b7d16dc",
            "0003": "5d14f97a9b2d469885984c92fe3d725e213ec892616eee19a7708338b226374b",
            "0004": "23edc2c1dd3475498b5e39f5c1323affb6168ca1f7e220ccc26aa642240906ea",
            "0005": "6ea318dba31f94392d6828cf64d2a9701c11e88142a13f53c9dcbb88fc29807a",
            "0006": "e298e32510afed3cfee0173afebe5c170405f8f6aa7f99ee89ccd4de4e199bfa",
            "0007": "d8dc393501622cfb570c6bd6759a2d2ce79e8d28ce909037856f7e5a4f52bd55",
        }
        for version, digest in expected.items():
            self.assertEqual(observed[version]["sha256"], digest)
            self.assertEqual(hashlib.sha256((ROOT / observed[version]["path"]).read_bytes()).hexdigest(), digest)
        self.assertFalse(manifest["balanced_v1"]["postgresql_authoritative"])
        self.assertFalse(manifest["balanced_v1"]["live_successor_execution_authorized"])


if __name__ == "__main__":
    unittest.main()
