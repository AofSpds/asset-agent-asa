from __future__ import annotations

from datetime import date, datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "aaa" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aaa.core.balanced_v1 import (
    BALANCED_V1,
    LEGACY_AAA_RUN_V0_X,
    CompatibilityWithPredecessor,
    DeclaredCompatibleSet,
    GovernedTimeEvidence,
    IdentityEnvelope,
    ReaderPolicy,
    SchemaFamilyVersion,
    SchemaRef,
    SchemaStatus,
    TimeAuthorityKind,
    TimePrecision,
    TimeSemantic,
    project_legacy_run_semantics,
    require_balanced_v1_marker,
    validate_pit_admissibility,
)


class BalancedV1E1Tests(unittest.TestCase):
    def test_identity_envelope_is_typed_and_collision_safe(self) -> None:
        run_ref = IdentityEnvelope("SEMICONDUCTOR_RESEARCH", "LOGICAL_RUN", "ID-001")
        event_ref = IdentityEnvelope("SEMICONDUCTOR_RESEARCH", "ECONOMIC_EVENT", "ID-001")
        self.assertNotEqual(run_ref.canonical_key, event_ref.canonical_key)

    def test_identity_envelope_rejects_blank_dimensions(self) -> None:
        with self.assertRaises(ValueError):
            IdentityEnvelope("SEMICONDUCTOR_RESEARCH", "", "ID-001")

    def test_date_precision_cannot_smuggle_intraday_datetime(self) -> None:
        with self.assertRaises(ValueError):
            GovernedTimeEvidence(
                semantic=TimeSemantic.PUBLIC_EVIDENCE_AVAILABLE_TIME,
                precision=TimePrecision.DATE,
                value=datetime(2026, 8, 16, 9, 30, tzinfo=timezone.utc),
                authority_kind=TimeAuthorityKind.SOURCE_EVIDENCE,
                authority_identity="SOURCE-1",
                evidence_or_clock_reference="EVIDENCE-1",
            )

    def test_datetime_precision_requires_timezone(self) -> None:
        with self.assertRaises(ValueError):
            GovernedTimeEvidence(
                semantic=TimeSemantic.RECORDED_TIME,
                precision=TimePrecision.DATETIME_TZ,
                value=datetime(2026, 8, 16, 9, 30),
                authority_kind=TimeAuthorityKind.GOVERNED_OPERATIONAL_STORE_CLOCK,
                authority_identity="PG-TRANSACTION-CLOCK",
                evidence_or_clock_reference="TX-1",
            )

    def test_date_precision_preserves_date_only(self) -> None:
        evidence = GovernedTimeEvidence(
            semantic=TimeSemantic.PUBLIC_EVIDENCE_AVAILABLE_TIME,
            precision=TimePrecision.DATE,
            value=date(2026, 8, 16),
            authority_kind=TimeAuthorityKind.IMMUTABLE_CERTIFICATION,
            authority_identity="PIT-CERTIFIER",
            evidence_or_clock_reference="CERT-1",
        )
        self.assertEqual(evidence.value, date(2026, 8, 16))

    def test_pit_admissibility_accepts_publication_before_cutoff(self) -> None:
        cutoff = datetime(2026, 8, 16, 9, 0, tzinfo=timezone.utc)
        published = datetime(2026, 8, 16, 8, 59, tzinfo=timezone.utc)
        self.assertTrue(validate_pit_admissibility(snapshot_cutoff_at=cutoff, publication_at=published))

    def test_pit_admissibility_accepts_supported_cutoff_mode(self) -> None:
        cutoff = datetime(2026, 8, 16, 9, 0, tzinfo=timezone.utc)
        supported = datetime(2026, 8, 16, 8, 30, tzinfo=timezone.utc)
        self.assertTrue(validate_pit_admissibility(snapshot_cutoff_at=cutoff, supported_cutoff_at=supported))

    def test_pit_admissibility_rejects_only_later_evidence(self) -> None:
        cutoff = datetime(2026, 8, 16, 9, 0, tzinfo=timezone.utc)
        later = datetime(2026, 8, 16, 9, 1, tzinfo=timezone.utc)
        self.assertFalse(validate_pit_admissibility(snapshot_cutoff_at=cutoff, publication_at=later))

    def test_pit_admissibility_requires_governed_availability_evidence(self) -> None:
        with self.assertRaises(ValueError):
            validate_pit_admissibility(snapshot_cutoff_at=datetime(2026, 8, 16, 9, 0, tzinfo=timezone.utc))

    def test_schema_version_rejects_floating_latest(self) -> None:
        with self.assertRaises(ValueError):
            SchemaRef("MODEL_INPUT_SCHEMA", "latest")

    def test_non_initial_schema_requires_exact_predecessor(self) -> None:
        with self.assertRaises(ValueError):
            SchemaFamilyVersion(
                ref=SchemaRef("MODEL_INPUT_SCHEMA", "MIS-v1.1"),
                schema_status=SchemaStatus.WORKING,
                compatibility_with_predecessor=CompatibilityWithPredecessor.NON_BREAKING_ADDITIVE,
                reader_policy=ReaderPolicy.DECLARED_COMPATIBLE_SET,
                spec_sha256="a" * 64,
            )

    def test_declared_compatible_set_is_directional(self) -> None:
        v1 = SchemaRef("MODEL_INPUT_SCHEMA", "MIS-v1.0")
        v11 = SchemaRef("MODEL_INPUT_SCHEMA", "MIS-v1.1")
        compatible = DeclaredCompatibleSet("SET-1", v11, (v1, v11), "b" * 64)
        self.assertTrue(compatible.permits(v1))
        reverse = DeclaredCompatibleSet("SET-2", v1, (v1,), "c" * 64)
        self.assertFalse(reverse.permits(v11))

    def test_legacy_projection_labels_but_does_not_invent_attempt(self) -> None:
        original = {"run_id": "RUN-T19-HISTORICAL", "state": "COMPLETED_PASS"}
        projected = project_legacy_run_semantics(original)
        self.assertEqual(projected["semantic_generation"], LEGACY_AAA_RUN_V0_X)
        self.assertNotIn("run_attempt_id", projected)
        self.assertNotIn("semantic_generation", original)

    def test_legacy_projection_rejects_synthetic_attempt(self) -> None:
        with self.assertRaises(ValueError):
            project_legacy_run_semantics({"run_id": "RUN-X", "run_attempt_id": "ATTEMPT-X"})

    def test_successor_record_requires_explicit_marker(self) -> None:
        require_balanced_v1_marker({"semantic_generation": BALANCED_V1})
        with self.assertRaises(ValueError):
            require_balanced_v1_marker({"run_id": "RUN-LEGACY"})

    def test_successor_contract_schemas_are_valid_json_and_do_not_mutate_legacy_schema(self) -> None:
        contracts = ROOT / "aaa" / "contracts"
        for name in (
            "identity_envelope_v1.schema.json",
            "time_evidence_v1.schema.json",
            "schema_family_version_v1.schema.json",
            "declared_compatible_set_v1.schema.json",
        ):
            payload = json.loads((contracts / name).read_text(encoding="utf-8"))
            self.assertEqual(payload["$schema"], "https://json-schema.org/draft/2020-12/schema")
        legacy = json.loads((contracts / "run_registry_entry.schema.json").read_text(encoding="utf-8"))
        self.assertNotIn("run_attempt_id", json.dumps(legacy))

    def test_migration_manifest_preserves_0001_0005_and_registers_0006(self) -> None:
        manifest = json.loads((ROOT / "aaa" / "db" / "MIGRATIONS.json").read_text(encoding="utf-8"))
        expected_legacy = {
            "0001": "66e5609fea1104f4aba4d0566989bf3a6c8d2b6e0b75cb274a79f7bdb48d68c2",
            "0002": "dfd47bb167e4bbcef2de9cb45bec811c0acfbcc5f03bde1a49fc24990b7d16dc",
            "0003": "5d14f97a9b2d469885984c92fe3d725e213ec892616eee19a7708338b226374b",
            "0004": "23edc2c1dd3475498b5e39f5c1323affb6168ca1f7e220ccc26aa642240906ea",
            "0005": "6ea318dba31f94392d6828cf64d2a9701c11e88142a13f53c9dcbb88fc29807a",
        }
        observed = {item["version"]: item for item in manifest["migrations"]}
        for version, digest in expected_legacy.items():
            self.assertEqual(observed[version]["sha256"], digest)
        migration = ROOT / observed["0006"]["path"]
        self.assertEqual(hashlib.sha256(migration.read_bytes()).hexdigest(), observed["0006"]["sha256"])
        self.assertFalse(manifest["balanced_v1"]["postgresql_authoritative"])


if __name__ == "__main__":
    unittest.main()
