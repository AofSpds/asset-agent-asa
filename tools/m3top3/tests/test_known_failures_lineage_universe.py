from __future__ import annotations

import json
import tempfile
import unittest
from dataclasses import replace
from datetime import date
from pathlib import Path
from unittest.mock import patch

from tools.m3top3.admission import (
    M3Top3AdmissionError,
    _snapshot_manifest_identity_payload,
    verify_snapshot_artifacts,
)
from tools.m3top3.core import aggregate_hash, hash_file, sha256_hex
from tools.m3top3.model_interface import DiagnosticFixtureScorer
from tools.m3top3.providers import InMemoryFeatureProvider, JsonlUniverseProvider, StaticUniverseProvider, UniverseState
from tools.m3top3.snapshot import SnapshotBuildConfig, SnapshotBuilder, SnapshotStore
from tools.m3top3.tests._known_failure_helpers import (
    business_dates,
    diagnostic_runner,
    external_expectation_kwargs,
    price_provider,
    standard_price_rows,
    synthetic_bound_lineage,
    write_universe_lineage_manifest,
)


class KnownFailureCanonicalLineageAndUniverseTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.dates = business_dates(count=30)
        self.price = price_provider(self.root, standard_price_rows(self.dates))
        self.states = [
            UniverseState("C1", "005930", date(2020, 1, 1), None, True, True, "U1"),
            UniverseState("C2", "000660", date(2020, 1, 1), None, True, True, "U2"),
            UniverseState("C3", "035420", date(2020, 1, 1), None, True, True, "U3"),
            UniverseState("C4", "051910", date(2020, 1, 1), None, True, True, "U4"),
        ]
        self.features = InMemoryFeatureProvider(
            [
                {
                    "company_id": state.company_id,
                    "feature_id": "diagnostic_score",
                    "value": str(10 - index),
                    "publication_at": "2025-01-02T10:00:00+09:00",
                }
                for index, state in enumerate(self.states)
            ]
        )

    def tearDown(self):
        self.tmp.cleanup()

    def assert_code(self, expected: str, action, exit_code: int | None = None):
        with self.assertRaises(M3Top3AdmissionError) as caught:
            action()
        self.assertEqual(caught.exception.code, expected)
        if exit_code is not None:
            self.assertEqual(caught.exception.exit_code, exit_code)

    def builder(self, states=None, denominator_states=None, **universe_kwargs):
        universe = StaticUniverseProvider(
            states or self.states,
            "U-DIAGNOSTIC",
            "DIAGNOSTIC",
            denominator_states=denominator_states,
            **universe_kwargs,
        )
        return SnapshotBuilder(universe, self.features, self.price, SnapshotBuildConfig())

    def write_single_company_universe(self, name="real-universe.jsonl"):
        universe_path = self.root / name
        universe_path.write_text(
            json.dumps(
                {
                    "company_id": "C1",
                    "security_code": "005930",
                    "valid_from": "2020-01-01",
                    "valid_to": None,
                    "operational_member": True,
                    "tradable_eligible": True,
                    "universe_record_id": "U1",
                    "status": "DIAGNOSTIC_VERIFIED",
                }
            )
            + "\n",
            encoding="utf-8",
        )
        return universe_path

    def materialize(self, states=None, denominator_states=None):
        builder = self.builder(states, denominator_states)
        built = builder.build(self.dates[0])
        root = self.root / f"snapshots-{len(list(self.root.glob('snapshots-*')))}"
        SnapshotStore(root).write(built, {})
        return root / self.dates[0].isoformat(), built

    def rewrite_snapshot(self, snapshot_dir: Path, pit_rows, model_rows, audit_rows, manifest):
        pit_text = "".join(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n" for row in pit_rows)
        model_text = "".join(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n" for row in model_rows)
        audit_text = "".join(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n" for row in audit_rows)
        (snapshot_dir / "pit_snapshot.jsonl").write_text(pit_text, encoding="utf-8")
        (snapshot_dir / "model_input.jsonl").write_text(model_text, encoding="utf-8")
        (snapshot_dir / "retrieval_audit.jsonl").write_text(audit_text, encoding="utf-8")
        manifest["pit_file_sha256"] = sha256_hex(pit_text)
        manifest["model_input_file_sha256"] = sha256_hex(model_text)
        manifest["retrieval_audit_file_sha256"] = sha256_hex(audit_text)
        manifest["pit_row_count"] = len(pit_rows)
        manifest["model_input_row_count"] = len(model_rows)
        manifest["retrieval_audit_row_count"] = len(audit_rows)
        manifest["retrieval_audit_content_hash"] = aggregate_hash([sha256_hex(row) for row in audit_rows])
        manifest["retrieval_receipt_ids"] = sorted(row["retrieval_receipt_id"] for row in audit_rows)
        manifest["retrieval_source_hashes"] = sorted({row["source_hash"] for row in audit_rows})
        manifest["snapshot_content_hash"] = aggregate_hash(
            [sha256_hex(row) for row in pit_rows]
            + [sha256_hex(row) for row in model_rows]
            + [sha256_hex(row) for row in audit_rows]
        )
        manifest["snapshot_manifest_identity_hash"] = sha256_hex(_snapshot_manifest_identity_payload(manifest))
        (snapshot_dir / "manifest.json").write_text(
            json.dumps(manifest, sort_keys=True, separators=(",", ":")) + "\n",
            encoding="utf-8",
        )

    def test_subset_release_is_rejected_against_exact_denominator(self):
        self.assert_code(
            "UNIVERSE_DENOMINATOR_MEMBERSHIP_MISMATCH",
            lambda: self.builder(self.states[:3], self.states).build(self.dates[0]),
            3,
        )

    def test_extra_release_member_is_rejected_against_exact_denominator(self):
        extra = UniverseState("C5", "006400", date(2020, 1, 1), None, True, True, "U5")
        self.assert_code(
            "UNIVERSE_DENOMINATOR_MEMBERSHIP_MISMATCH",
            lambda: self.builder([*self.states, extra], self.states).build(self.dates[0]),
            3,
        )

    def test_duplicate_company_identity_is_rejected(self):
        duplicate = replace(self.states[0], security_code="000001", universe_record_id="U1-DUP")
        self.assert_code(
            "DUPLICATE_UNIVERSE_COMPANY_ID",
            lambda: self.builder([*self.states, duplicate]).build(self.dates[0]),
            3,
        )

    def test_universe_release_hash_mismatch_is_rejected(self):
        self.assert_code(
            "UNIVERSE_RELEASE_HASH_MISMATCH",
            lambda: self.builder(release_hash="f" * 64).build(self.dates[0]),
            3,
        )

    def test_denominator_release_hash_mismatch_is_rejected(self):
        self.assert_code(
            "DENOMINATOR_RELEASE_HASH_MISMATCH",
            lambda: self.builder(denominator_release_hash="f" * 64).build(self.dates[0]),
            3,
        )

    def test_partial_release_or_member_status_is_not_admitted(self):
        self.assert_code(
            "UNIVERSE_RELEASE_STATUS_UNVERIFIED",
            lambda: self.builder(release_status="PARTIAL").build(self.dates[0]),
            2,
        )
        partial = [replace(self.states[0], status="PARTIAL"), *self.states[1:]]
        self.assert_code(
            "UNIVERSE_MEMBER_STATUS_UNVERIFIED",
            lambda: self.builder(partial).build(self.dates[0]),
            2,
        )

    def test_partial_feature_release_is_not_admitted(self):
        features = InMemoryFeatureProvider([], source_status="UNVERIFIED")
        builder = SnapshotBuilder(
            StaticUniverseProvider(self.states), features, self.price, SnapshotBuildConfig()
        )
        self.assert_code("FEATURE_RELEASE_STATUS_UNVERIFIED", lambda: builder.build(self.dates[0]), 2)

    def test_self_consistent_subset_of_snapshot_rows_is_rejected(self):
        snapshot_dir, _ = self.materialize()
        pit_rows = [json.loads(line) for line in (snapshot_dir / "pit_snapshot.jsonl").read_text().splitlines()]
        model_rows = [json.loads(line) for line in (snapshot_dir / "model_input.jsonl").read_text().splitlines()]
        audit_rows = [json.loads(line) for line in (snapshot_dir / "retrieval_audit.jsonl").read_text().splitlines()]
        manifest = json.loads((snapshot_dir / "manifest.json").read_text())
        self.rewrite_snapshot(snapshot_dir, pit_rows[:-1], model_rows[:-1], audit_rows[:-1], manifest)
        self.assert_code("SNAPSHOT_UNIVERSE_MEMBER_MISSING", lambda: verify_snapshot_artifacts(snapshot_dir), 3)

    def test_missing_eligible_score_blocks_before_result_or_ledger_write(self):
        snapshot_dir, _ = self.materialize()

        class MissingScore(DiagnosticFixtureScorer):
            def score(self, model_input):
                result = super().score(model_input)
                if model_input["company_id"] == "C4":
                    return replace(result, total_score=None)
                return result

        runner, _ = diagnostic_runner(self.price, self.dates, MissingScore())
        output = self.root / "missing-score"
        self.assert_code("FULL_ELIGIBLE_SCORE_SET_INCOMPLETE", lambda: runner.run_snapshot(snapshot_dir, output), 2)
        self.assertFalse(output.exists())

    def test_score_identity_drift_blocks_before_result_or_ledger_write(self):
        snapshot_dir, _ = self.materialize()

        class WrongCompany(DiagnosticFixtureScorer):
            def score(self, model_input):
                result = super().score(model_input)
                return replace(result, company_id="FORGED")

        runner, _ = diagnostic_runner(self.price, self.dates, WrongCompany())
        output = self.root / "wrong-score-identity"
        self.assert_code("SCORE_IDENTITY_MISMATCH", lambda: runner.run_snapshot(snapshot_dir, output), 3)
        self.assertFalse(output.exists())

    def test_full_rank_and_outcome_coverage_are_preserved_beyond_top3(self):
        snapshot_dir, _ = self.materialize()
        runner, _ = diagnostic_runner(self.price, self.dates)
        ledger_path = self.root / "full-ledger.jsonl"
        from tools.m3top3.ledger import PredictionLedger

        result = runner.run_snapshot(snapshot_dir, self.root / "full-result", PredictionLedger(ledger_path))
        self.assertEqual(result["ranked_count"], 4)
        self.assertEqual(result["selected_top3_count"], 3)
        self.assertEqual(result["outcome_count"], 4)
        self.assertEqual(result["selected_top3_outcome_count"], 3)
        self.assertEqual(result["full_universe_outcome_count"], 4)
        self.assertEqual(len(result["full_universe_outcomes"]), 4)
        self.assertEqual(len(ledger_path.read_text(encoding="utf-8").splitlines()), 4)

    def test_result_rejects_noncontiguous_or_subset_ranking(self):
        snapshot_dir, _ = self.materialize()
        runner, _ = diagnostic_runner(self.price, self.dates)
        original = runner.ranking.rank

        def subset(scores, eligibility):
            return original(scores, eligibility)[:-1]

        output = self.root / "subset-ranking"
        with patch.object(runner.ranking, "rank", side_effect=subset):
            self.assert_code("FULL_RANKING_SET_MISMATCH", lambda: runner.run_snapshot(snapshot_dir, output), 3)
        self.assertFalse(output.exists())

    def test_jsonl_universe_requires_independent_manifest_and_denominator(self):
        universe_path = self.write_single_company_universe()
        self.assert_code(
            "SELF_CERTIFIED_UNIVERSE_DENOMINATOR_PROHIBITED",
            lambda: JsonlUniverseProvider(universe_path, "U", "DIAGNOSTIC"),
            4,
        )

    def test_jsonl_universe_row_cannot_self_assert_verified_by_omitting_status(self):
        universe_path = self.write_single_company_universe()
        row = json.loads(universe_path.read_text(encoding="utf-8"))
        del row["status"]
        universe_path.write_text(json.dumps(row) + "\n", encoding="utf-8")
        denominator, manifest_path, manifest_hash = write_universe_lineage_manifest(
            self.root, universe_path, [self.dates[0]], "U"
        )
        self.assert_code(
            "BLOCKED_INPUT_INTEGRITY",
            lambda: JsonlUniverseProvider(
                universe_path,
                "U",
                "DIAGNOSTIC",
                denominator_path=denominator,
                lineage_manifest_path=manifest_path,
                lineage_manifest_hash=manifest_hash,
                **external_expectation_kwargs(manifest_path),
            ),
            3,
        )

    def test_jsonl_manifest_applicable_slice_mismatch_is_rejected(self):
        universe_path = self.write_single_company_universe()
        denominator, manifest_path, _ = write_universe_lineage_manifest(
            self.root, universe_path, [self.dates[0]], "U"
        )
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["slices"][0]["denominator_row_count"] = 99
        manifest_path.write_text(json.dumps(manifest, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
        provider = JsonlUniverseProvider(
            universe_path,
            "U",
            "DIAGNOSTIC",
            denominator_path=denominator,
            lineage_manifest_path=manifest_path,
            lineage_manifest_hash=hash_file(manifest_path),
            **external_expectation_kwargs(manifest_path),
        )
        builder = SnapshotBuilder(provider, self.features, self.price, SnapshotBuildConfig(),execution_lineage=synthetic_bound_lineage(provider,self.features,self.price))
        self.assert_code("DENOMINATOR_COUNT_MISMATCH", lambda: builder.build(self.dates[0]), 3)

    def test_jsonl_manifest_authority_mismatch_is_rejected(self):
        universe_path = self.write_single_company_universe()
        denominator, manifest_path, manifest_hash = write_universe_lineage_manifest(
            self.root, universe_path, [self.dates[0]], "U"
        )
        self.assert_code(
            "PLACEHOLDER_RELEASE_NOT_ADMISSIBLE",
            lambda: JsonlUniverseProvider(
                universe_path,
                "U",
                "WORKING_FREEZE_CANDIDATE",
                denominator_path=denominator,
                lineage_manifest_path=manifest_path,
                lineage_manifest_hash=manifest_hash,
                **external_expectation_kwargs(manifest_path),
            ),
            4,
        )

    def test_jsonl_denominator_cannot_alias_universe_path(self):
        universe_path = self.write_single_company_universe()
        _, manifest_path, manifest_hash = write_universe_lineage_manifest(
            self.root, universe_path, [self.dates[0]], "U"
        )
        self.assert_code(
            "UNIVERSE_LINEAGE_MANIFEST_REQUIRED",
            lambda: JsonlUniverseProvider(
                universe_path,
                "U",
                "DIAGNOSTIC",
                denominator_path=universe_path,
                lineage_manifest_path=manifest_path,
                lineage_manifest_hash=manifest_hash,
                **external_expectation_kwargs(manifest_path),
            ),
            3,
        )

    def test_jsonl_manifest_missing_applicable_slice_is_rejected(self):
        universe_path = self.write_single_company_universe()
        denominator, manifest_path, manifest_hash = write_universe_lineage_manifest(
            self.root, universe_path, [self.dates[1]], "U"
        )
        provider = JsonlUniverseProvider(
            universe_path,
            "U",
            "DIAGNOSTIC",
            denominator_path=denominator,
            lineage_manifest_path=manifest_path,
            lineage_manifest_hash=manifest_hash,
            **external_expectation_kwargs(manifest_path),
        )
        builder = SnapshotBuilder(provider, self.features, self.price, SnapshotBuildConfig(),execution_lineage=synthetic_bound_lineage(provider,self.features,self.price))
        self.assert_code("UNIVERSE_LINEAGE_SLICE_NOT_DECLARED", lambda: builder.build(self.dates[0]), 2)

    def test_jsonl_manifest_live_byte_drift_is_rejected(self):
        universe_path = self.write_single_company_universe()
        denominator, manifest_path, manifest_hash = write_universe_lineage_manifest(
            self.root, universe_path, [self.dates[0]], "U"
        )
        provider = JsonlUniverseProvider(
            universe_path,
            "U",
            "DIAGNOSTIC",
            denominator_path=denominator,
            lineage_manifest_path=manifest_path,
            lineage_manifest_hash=manifest_hash,
            **external_expectation_kwargs(manifest_path),
        )
        manifest_path.write_text(manifest_path.read_text(encoding="utf-8") + " ", encoding="utf-8")
        builder = SnapshotBuilder(provider, self.features, self.price, SnapshotBuildConfig(),execution_lineage=synthetic_bound_lineage(provider,self.features,self.price))
        self.assert_code("UNIVERSE_LINEAGE_MANIFEST_MISMATCH", lambda: builder.build(self.dates[0]), 3)

    def test_mixed_eligible_and_ineligible_keeps_u_for_scores_and_e_for_outputs(self):
        mixed = [*self.states[:3], replace(self.states[3], tradable_eligible=False)]
        snapshot_dir, built = self.materialize(mixed)
        runner, scorer = diagnostic_runner(self.price, self.dates)
        from tools.m3top3.ledger import PredictionLedger

        ledger = self.root / "mixed-ledger.jsonl"
        result = runner.run_snapshot(snapshot_dir, self.root / "mixed-output", PredictionLedger(ledger))
        self.assertEqual(len(built.model_inputs), 4)
        self.assertEqual(scorer.calls, 4)
        self.assertEqual(result["ranked_count"], 3)
        self.assertEqual(result["full_universe_outcome_count"], 3)
        self.assertEqual(len(ledger.read_text(encoding="utf-8").splitlines()), 3)


if __name__ == "__main__":
    unittest.main()
