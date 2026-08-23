from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from tools.m3top3.admission import (
    M3Top3AdmissionError,
    _verify_full_universe_coverage,
    _verify_retrieval_audit_semantics,
    verify_price_component_manifest,
)
from tools.m3top3.backtest import RUN_IDENTITY_FIELDS, verify_validation_run_identity
from tools.m3top3.core import deterministic_id
from tools.m3top3.ledger import ImmutableJsonArtifactStore, PredictionLedger
from tools.m3top3.tests._known_failure_helpers import (
    diagnostic_runner,
    materialize_external_fixture,
)


class RWP403MutationIsolationTests(unittest.TestCase):
    """One production guard per mutation, with assertion-only red outcomes."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    @staticmethod
    def _jsonl_rows(path: Path) -> list[dict]:
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]

    @staticmethod
    def _pit_identity_payload(row: dict) -> dict:
        fields = (
            "company_id",
            "snapshot_cutoff_at",
            "snapshot_schema_version",
            "snapshot_revision",
            "f1_f2_effective_refs",
            "f3_observation_refs",
            "evidence_refs",
            "dataset_refs",
            "universe_lineage_manifest_hash",
            "universe_authority_status",
            "universe_release_id",
            "universe_release_revision",
            "universe_release_hash",
            "universe_release_status",
            "denominator_release_id",
            "denominator_release_revision",
            "denominator_release_hash",
            "denominator_release_status",
            "denominator_member_id",
            "eligibility_record_id",
            "eligibility_status",
            "tradability_state_ref",
            "retrieval_receipt_id",
            "retrieval_source_hash",
        )
        return {field: row.get(field) for field in fields}

    def test_retrieval_count_reconciliation_guard(self) -> None:
        fixture = materialize_external_fixture(self.root)
        snapshot = fixture["snapshot_dir"]
        manifest = json.loads((snapshot / "manifest.json").read_text(encoding="utf-8"))
        pit_rows = self._jsonl_rows(snapshot / "pit_snapshot.jsonl")
        model_rows = self._jsonl_rows(snapshot / "model_input.jsonl")
        audit_rows = self._jsonl_rows(snapshot / "retrieval_audit.jsonl")

        receipt = audit_rows[0]
        receipt["source_matching_rows"] = receipt["selected_rows"] + receipt["excluded_rows"] + 1
        receipt_identity_fields = {
            "company_id",
            "cutoff_at",
            "source_version",
            "source_status",
            "source_hash",
            "source_matching_rows",
            "selected_rows",
            "excluded_rows",
            "exclusions",
            "cutoff_frozen_bundle",
        }
        receipt["retrieval_receipt_id"] = deterministic_id(
            "retrieval",
            {field: receipt[field] for field in receipt_identity_fields},
        )

        pit_row = next(row for row in pit_rows if row["company_id"] == receipt["company_id"])
        model_row = next(row for row in model_rows if row["company_id"] == receipt["company_id"])
        pit_row["retrieval_receipt_id"] = receipt["retrieval_receipt_id"]
        pit_row["retrieval_source_hash"] = receipt["source_hash"]
        pit_row["pit_snapshot_id"] = deterministic_id("pit", self._pit_identity_payload(pit_row))
        pit_row["capture_run_id"] = deterministic_id(
            "capture",
            {
                "pit_snapshot_id": pit_row["pit_snapshot_id"],
                "generator_version": pit_row["generator_version"],
            },
        )
        model_row["retrieval_receipt_id"] = receipt["retrieval_receipt_id"]
        model_row["retrieval_source_hash"] = receipt["source_hash"]
        model_row["pit_snapshot_id"] = pit_row["pit_snapshot_id"]
        receipt["pit_snapshot_id"] = pit_row["pit_snapshot_id"]
        manifest["retrieval_receipt_ids"] = sorted(
            row["retrieval_receipt_id"] for row in audit_rows
        )

        with self.assertRaises(M3Top3AdmissionError) as caught:
            _verify_retrieval_audit_semantics(
                snapshot,
                manifest,
                pit_rows,
                model_rows,
                audit_rows,
            )
        self.assertEqual(
            (caught.exception.code, caught.exception.exit_code),
            ("RETRIEVAL_AUDIT_SEMANTIC_MISMATCH", 3),
        )
        self.assertIn("counts do not reconcile", str(caught.exception))

    def test_immutable_json_artifact_store_rejects_different_payload(self) -> None:
        path = self.root / "immutable" / "run.json"
        store = ImmutableJsonArtifactStore(path)
        first = {"validation_run_id": "SAME", "payload": "A"}
        second = {"validation_run_id": "SAME", "payload": "B"}
        self.assertEqual(store.admit(first), "APPENDED")
        before = path.read_bytes()

        with self.assertRaises(M3Top3AdmissionError) as caught:
            store.admit(second)
        self.assertEqual(
            (caught.exception.code, caught.exception.exit_code),
            ("NONDETERMINISTIC_RERUN", 3),
        )
        self.assertEqual(path.read_bytes(), before)

    def test_price_component_manifest_guard_in_isolation(self) -> None:
        first = self.root / "price-a.parquet"
        second = self.root / "price-b.parquet"
        first.write_bytes(b"price-a")
        second.write_bytes(b"price-b")
        provider = SimpleNamespace(
            paths=[first, second],
            dataset_id="P-MULTI",
            dataset_hash="0" * 64,
        )

        with self.assertRaises(M3Top3AdmissionError) as caught:
            verify_price_component_manifest(provider, None)
        self.assertEqual(
            (caught.exception.code, caught.exception.exit_code),
            ("PRICE_COMPONENT_MANIFEST_REQUIRED", 3),
        )

    def test_prediction_ledger_append_precedes_result_publish(self) -> None:
        fixture = materialize_external_fixture(self.root)
        runner, _ = diagnostic_runner(
            fixture["price"],
            fixture["dates"],
            fixture["scorer"],
            execution_lineage=fixture["lineage"],
        )

        class RejectOnlyAtAppend:
            def __init__(self) -> None:
                self.preflight_calls = 0
                self.append_calls = 0

            def preflight_many(self, rows):
                self.preflight_calls += 1
                return ["APPENDABLE"] * len(rows)

            def append_many(self, rows):
                self.append_calls += 1
                raise M3Top3AdmissionError(
                    "NONDETERMINISTIC_RERUN",
                    "isolated post-preflight ledger collision",
                    exit_code=3,
                )

        ledger = RejectOnlyAtAppend()
        output = self.root / "ledger-append-before-result"
        with self.assertRaises(M3Top3AdmissionError) as caught:
            runner.run_snapshot(fixture["snapshot_dir"], output, ledger)
        self.assertEqual(
            (caught.exception.code, caught.exception.exit_code),
            ("NONDETERMINISTIC_RERUN", 3),
        )
        self.assertEqual((ledger.preflight_calls, ledger.append_calls), (1, 1))
        self.assertFalse(output.exists())

    def test_partition_digest_guard_at_snapshot_level(self) -> None:
        fixture = materialize_external_fixture(self.root)
        snapshot = fixture["snapshot_dir"]
        manifest = json.loads((snapshot / "manifest.json").read_text(encoding="utf-8"))
        pit_rows = self._jsonl_rows(snapshot / "pit_snapshot.jsonl")
        model_rows = self._jsonl_rows(snapshot / "model_input.jsonl")
        audit_rows = self._jsonl_rows(snapshot / "retrieval_audit.jsonl")

        for field, forged in (
            ("eligible_set_digest", "0" * 64),
            ("ineligible_set_digest", "1" * 64),
            ("denominator_partition_digest", "2" * 64),
        ):
            with self.subTest(field=field):
                candidate = copy.deepcopy(manifest)
                candidate[field] = forged
                with self.assertRaises(M3Top3AdmissionError) as caught:
                    _verify_full_universe_coverage(
                        candidate,
                        pit_rows,
                        model_rows,
                        audit_rows,
                    )
                self.assertEqual(
                    (caught.exception.code, caught.exception.exit_code),
                    ("ELIGIBLE_SET_DIGEST_MISMATCH", 3),
                )

    def test_validation_run_identity_completeness_guard(self) -> None:
        payload = {field: f"value:{field}" for field in RUN_IDENTITY_FIELDS}
        payload["result_revision"] = 0
        payload.pop("scorer_identity_hash")
        result = {
            "validation_run_identity_payload": payload,
            "validation_run_id": deterministic_id("validationrun", payload),
        }

        with self.assertRaises(M3Top3AdmissionError) as caught:
            verify_validation_run_identity(result)
        self.assertEqual(
            (caught.exception.code, caught.exception.exit_code),
            ("RUN_ID_LINEAGE_MISMATCH", 3),
        )

    def test_full_ledger_completeness_mutation_is_assertion_failure(self) -> None:
        fixture = materialize_external_fixture(
            self.root,
            eligibility_status_by_company={"C4": "ELIGIBLE"},
        )
        runner, _ = diagnostic_runner(
            fixture["price"],
            fixture["dates"],
            fixture["scorer"],
            execution_lineage=fixture["lineage"],
        )
        output = self.root / "full-ledger-result"
        ledger_path = self.root / "full-ledger.jsonl"

        try:
            result = runner.run_snapshot(
                fixture["snapshot_dir"],
                output,
                PredictionLedger(ledger_path),
            )
        except M3Top3AdmissionError as exc:
            self.fail(
                "full-E ledger publication unexpectedly raised a governed error: "
                f"{exc.code}/{exc.exit_code}"
            )

        self.assertEqual(result["ranked_count"], result["eligible_count"])
        self.assertEqual(result["ranked_count"], 4)
        self.assertEqual(len(ledger_path.read_text(encoding="utf-8").splitlines()), 4)


if __name__ == "__main__":
    unittest.main()
