from __future__ import annotations

import copy
import csv
import hashlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.m3top3.contracts_v1 import input_batch_hash
from tools.m3top3.f05_r1_market import F05_FEATURE_ID
from tools.m3top3.f05_r1_score_outputs import (
    AGGREGATE_VALIDATION_SCHEMA_VERSION,
    CLAIM_STATUS,
    EXPECTED_CONFIG_SHA256,
    EXPECTED_F02_INPUT_BATCH_SHA256,
    EXPECTED_INDEPENDENCE_ASSERTION,
    EXPECTED_TARGET_AUTHOR_IDENTITY,
    EXPECTED_VALIDATION_LEVEL_BY_ROLE,
    F02_FIXED_COMPANY_IDS,
    FIVE_FILENAME,
    INDEPENDENT_VALIDATION_RECEIPT_SCHEMA_VERSION,
    RANKING_FILENAME,
    REQUIRED_VALIDATOR_ROLES,
    SCORE_FILENAME,
    F05ScoreOutputError,
    _canonical_json_line,
    build_f05_r1_outputs,
    persist_f05_r1_outputs,
)
from tools.m3top3.tests.test_f05_r1_market import build_bound_inputs, cohort_and_prices


REPO = Path(__file__).resolve().parents[3]
F02_INPUT_PATH = (
    REPO / "control/m3top3/f02-r1-multi-company-input-repair/v1.0/runs/"
    "AAA-M3TOP3-F02-R1-20260905-171755-CODEX-01/score-and-seal/"
    "STRICT_MODEL_INPUT_BATCH.json"
)
CONFIG_PATH = REPO / "tools/m3top3/configs/m3top3_v1.0.json"


class TestF05R1ScoreOutputs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cohort, prices = cohort_and_prices()
        f05_rows = sorted(build_bound_inputs(cohort, prices), key=lambda row: row["company_id"])
        cls.f05_bytes = b"".join(_canonical_json_line(row) for row in f05_rows)
        cls.f02_bytes = F02_INPUT_PATH.read_bytes()
        cls.config_bytes = CONFIG_PATH.read_bytes()
        cls.f05_rows = f05_rows
        cls.f02_rows = json.loads(cls.f02_bytes)
        merged = copy.deepcopy(cls.f02_rows)
        f05_by_id = {row["company_id"]: row for row in f05_rows}
        for row in merged:
            row["feature_raw_inputs"][F05_FEATURE_ID] = copy.deepcopy(
                f05_by_id[row["company_id"]]["feature_raw_input"]
            )
        cls.merged_input_hash = input_batch_hash(merged)
        cls.input_bindings = {
            "f05_input_jsonl_sha256": hashlib.sha256(cls.f05_bytes).hexdigest(),
            "f02_model_input_batch_sha256": hashlib.sha256(cls.f02_bytes).hexdigest(),
            "config_sha256": hashlib.sha256(cls.config_bytes).hexdigest(),
        }
        cls.target_commit = "a" * 40
        cls.target_tree = "b" * 40
        cls.target_bundle = (
            f"AAA-M3TOP3-F05-R1-D1-{cls.target_commit}-{cls.target_tree}"
        )
        cls.run_id = "AAA-M3TOP3-F05-R1-SYNTHETIC-GATE-TEST"
        cls.target_revision = "D1"
        cls.receipt_paths = {
            role: (
                f"validation/{role}_{EXPECTED_VALIDATION_LEVEL_BY_ROLE[role]}_"
                "D1_RECEIPT.json"
            )
            for role in REQUIRED_VALIDATOR_ROLES
        }

    def gate_bytes(self, **report_changes):
        receipts = {}
        descriptors = []
        for role in REQUIRED_VALIDATOR_ROLES:
            receipt_id = (
                f"AAA-M3TOP3-F05-R1-D1-{role}-"
                f"{EXPECTED_VALIDATION_LEVEL_BY_ROLE[role]}-20260906-010000-01"
            )
            validator_identity = f"root/f05_r1_{role.lower()}_d1"
            value = {
                "schema_version": INDEPENDENT_VALIDATION_RECEIPT_SCHEMA_VERSION,
                "receipt_id": receipt_id,
                "run_id": self.run_id,
                "target_revision": self.target_revision,
                "validator_role": role,
                "validation_level": EXPECTED_VALIDATION_LEVEL_BY_ROLE[role],
                "validator_identity": validator_identity,
                "author_identity": EXPECTED_TARGET_AUTHOR_IDENTITY,
                "independence_assertion": EXPECTED_INDEPENDENCE_ASSERTION,
                "supporting_not_self_pass": False,
                "role_verdicts": {role: "PASS"},
                "target_author": False,
                "target_edited": False,
                "no_pass_transfer": True,
                "verdict": "PASS",
                "findings": [],
                "target_commit": self.target_commit,
                "target_tree": self.target_tree,
                "target_bundle_identity": self.target_bundle,
                "target_input_hash": self.merged_input_hash,
                "input_bindings": self.input_bindings,
            }
            raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
            receipts[role] = raw
            descriptors.append({
                "role": role,
                "validation_level": EXPECTED_VALIDATION_LEVEL_BY_ROLE[role],
                "receipt_id": receipt_id,
                "validator_identity": validator_identity,
                "path": self.receipt_paths[role],
                "sha256": hashlib.sha256(raw).hexdigest(),
            })
        report = {
            "schema_version": AGGREGATE_VALIDATION_SCHEMA_VERSION,
            "run_id": self.run_id,
            "target_revision": self.target_revision,
            "status": "PASS",
            "scoring_permitted": True,
            "target_author": False,
            "blocking_findings": [],
            "target_commit": self.target_commit,
            "target_tree": self.target_tree,
            "target_bundle_identity": self.target_bundle,
            "target_input_hash": self.merged_input_hash,
            "input_bindings": self.input_bindings,
            "role_verdicts": {role: "PASS" for role in REQUIRED_VALIDATOR_ROLES},
            "validation_receipts": descriptors,
        }
        report.update(report_changes)
        report_bytes = json.dumps(report, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return report_bytes, receipts

    @staticmethod
    def _encode(value):
        return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")

    def mutate_receipt_gate(self, role, field, value, *, missing=False):
        report_bytes, receipts = self.gate_bytes()
        report = json.loads(report_bytes)
        receipt = json.loads(receipts[role])
        if missing:
            receipt.pop(field)
        else:
            receipt[field] = value
        receipts[role] = self._encode(receipt)
        descriptor = next(item for item in report["validation_receipts"] if item["role"] == role)
        descriptor["sha256"] = hashlib.sha256(receipts[role]).hexdigest()
        descriptor_field = {
            "receipt_id": "receipt_id",
            "validation_level": "validation_level",
            "validator_identity": "validator_identity",
        }.get(field)
        if descriptor_field is not None and not missing and isinstance(value, str):
            descriptor[descriptor_field] = value
        return self._encode(report), receipts

    def rehash_gate(self, report, receipt_documents):
        receipt_bytes = {}
        for role in REQUIRED_VALIDATOR_ROLES:
            receipt = receipt_documents[role]
            raw = self._encode(receipt)
            receipt_bytes[role] = raw
            descriptor = next(
                item for item in report["validation_receipts"] if item["role"] == role
            )
            descriptor["validation_level"] = receipt["validation_level"]
            descriptor["receipt_id"] = receipt["receipt_id"]
            descriptor["validator_identity"] = receipt["validator_identity"]
            descriptor["sha256"] = hashlib.sha256(raw).hexdigest()
        return self._encode(report), receipt_bytes

    def build(self):
        report, receipts = self.gate_bytes()
        return build_f05_r1_outputs(
            f05_input_jsonl=self.f05_bytes,
            f02_input_batch_json=self.f02_bytes,
            config_json=self.config_bytes,
            aggregate_validation_json=report,
            validation_receipt_json_by_role=receipts,
            validation_receipt_path_by_role=self.receipt_paths,
        )

    def test_exact_gate_calls_unchanged_engine_and_renders_three_provisional_artifacts(self):
        self.assertEqual(hashlib.sha256(self.f02_bytes).hexdigest(), EXPECTED_F02_INPUT_BATCH_SHA256)
        self.assertEqual(hashlib.sha256(self.config_bytes).hexdigest(), EXPECTED_CONFIG_SHA256)
        first = self.build()
        second = self.build()
        self.assertEqual(first.score_jsonl, second.score_jsonl)
        self.assertEqual(first.provisional_ranking_csv, second.provisional_ranking_csv)
        self.assertEqual(first.f02_f05_exact_five_csv, second.f02_f05_exact_five_csv)
        self.assertEqual(
            first.sha256_by_filename(),
            {
                SCORE_FILENAME: "a5f1fd264b8eff8d75e3ad61b0ecee77729c7661e58d96a7bc0f38b20a2504fe",
                RANKING_FILENAME: "13bf13c9d716dfd4ae3c33cbf054576732650ae70ac7ac74dfe9a2ff88d2dd09",
                FIVE_FILENAME: "664ff158382610007d83cd6b0585a20c636434edbc975217084f7b94f7c15797",
            },
        )

        score_rows = [json.loads(line) for line in first.score_jsonl.splitlines()]
        ranking = list(csv.DictReader(io.StringIO(first.provisional_ranking_csv.decode("utf-8"))))
        five = list(csv.DictReader(io.StringIO(first.f02_f05_exact_five_csv.decode("utf-8"))))
        self.assertEqual(len(score_rows), 57)
        self.assertEqual(len(ranking), 57)
        self.assertEqual(len(five), 5)
        self.assertEqual({row["company_id"] for row in five}, F02_FIXED_COMPANY_IDS)
        self.assertEqual(sorted(int(row["f05_only_provisional_rank"]) for row in ranking), list(range(1, 58)))
        self.assertEqual(sorted(int(row["combined_provisional_rank"]) for row in five), list(range(1, 6)))
        self.assertEqual(
            sum(row["combined_provisional_rank"] is None for row in score_rows), 52
        )
        self.assertEqual(sum(row["feature_coverage_ratio"] == "0.3" for row in score_rows), 5)
        self.assertEqual(sum(row["feature_coverage_ratio"] == "0.2" for row in score_rows), 52)
        self.assertTrue(all(row["claim_status"] == CLAIM_STATUS for row in score_rows))
        self.assertTrue(all(row["top3_flag"] is False and row["top10_flag"] is False for row in score_rows))
        self.assertNotIn("official", "\n".join(first.score_jsonl.decode("utf-8").splitlines()).lower().replace("no_official", ""))

        with tempfile.TemporaryDirectory(prefix="f05-score-output-") as temp:
            output_dir = Path(temp) / "score-output"
            hashes = persist_f05_r1_outputs(first, output_dir)
            self.assertEqual(set(hashes), {SCORE_FILENAME, RANKING_FILENAME, FIVE_FILENAME})
            self.assertEqual(set(path.name for path in output_dir.iterdir()), set(hashes))
            with self.assertRaises(FileExistsError):
                persist_f05_r1_outputs(first, output_dir)

    def test_failed_gate_cannot_construct_or_call_engine(self):
        report, receipts = self.gate_bytes(status="FAIL", scoring_permitted=False)
        with patch("tools.m3top3.f05_r1_score_outputs.M3Top3V1Engine") as engine:
            with self.assertRaisesRegex(F05ScoreOutputError, "not permitted"):
                build_f05_r1_outputs(
                    f05_input_jsonl=self.f05_bytes,
                    f02_input_batch_json=self.f02_bytes,
                    config_json=self.config_bytes,
                    aggregate_validation_json=report,
                    validation_receipt_json_by_role=receipts,
                    validation_receipt_path_by_role=self.receipt_paths,
                )
            engine.assert_not_called()

    def test_author_receipt_and_receipt_hash_drift_fail_closed(self):
        report, receipts = self.gate_bytes()
        value = json.loads(receipts["CTLV"])
        value["target_author"] = True
        receipts["CTLV"] = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
        with self.assertRaises(F05ScoreOutputError):
            build_f05_r1_outputs(
                f05_input_jsonl=self.f05_bytes,
                f02_input_batch_json=self.f02_bytes,
                config_json=self.config_bytes,
                aggregate_validation_json=report,
                validation_receipt_json_by_role=receipts,
                validation_receipt_path_by_role=self.receipt_paths,
            )

    def test_formal_receipt_fields_fail_closed_before_engine_call(self):
        other_receipt_id = "AAA-M3TOP3-F05-R1-D1-MODV-L1-20260906-010000-01"
        other_validator_identity = "root/f05_r1_modv_d1"
        cases = (
            ("schema_version_missing", "schema_version", None, True),
            ("schema_version_mutated", "schema_version", "UNREVIEWED", False),
            ("run_id_missing", "run_id", None, True),
            ("run_id_mutated", "run_id", "OTHER-RUN", False),
            ("target_revision_missing", "target_revision", None, True),
            ("target_revision_mutated", "target_revision", "D0", False),
            ("receipt_id_missing", "receipt_id", None, True),
            ("receipt_id_empty", "receipt_id", "", False),
            ("receipt_id_duplicate", "receipt_id", other_receipt_id, False),
            ("validator_role_missing", "validator_role", None, True),
            ("validator_role_substituted", "validator_role", "MODV", False),
            ("validation_level_missing", "validation_level", None, True),
            ("validation_level_mutated", "validation_level", "L2", False),
            ("validator_identity_missing", "validator_identity", None, True),
            ("validator_identity_empty", "validator_identity", "", False),
            (
                "validator_identity_duplicate",
                "validator_identity",
                other_validator_identity,
                False,
            ),
            (
                "validator_identity_is_author",
                "validator_identity",
                EXPECTED_TARGET_AUTHOR_IDENTITY,
                False,
            ),
            ("author_identity_missing", "author_identity", None, True),
            ("author_identity_mutated", "author_identity", "root/other_author", False),
            ("independence_assertion_missing", "independence_assertion", None, True),
            ("independence_assertion_mutated", "independence_assertion", "INDEPENDENT", False),
            ("supporting_not_self_pass_missing", "supporting_not_self_pass", None, True),
            ("supporting_not_self_pass_true", "supporting_not_self_pass", True, False),
            ("target_author_missing", "target_author", None, True),
            ("target_author_true", "target_author", True, False),
            ("target_edited_missing", "target_edited", None, True),
            ("target_edited_true", "target_edited", True, False),
            ("no_pass_transfer_missing", "no_pass_transfer", None, True),
            ("no_pass_transfer_false", "no_pass_transfer", False, False),
            ("verdict_missing", "verdict", None, True),
            ("verdict_mutated", "verdict", "FAIL", False),
            ("findings_missing", "findings", None, True),
            ("findings_nonempty", "findings", [{"finding_id": "N12"}], False),
            ("role_verdicts_missing", "role_verdicts", None, True),
            ("role_verdicts_substituted", "role_verdicts", {"MODV": "PASS"}, False),
            (
                "role_verdicts_extra_role",
                "role_verdicts",
                {"CTLV": "PASS", "MODV": "PASS"},
                False,
            ),
            ("target_commit_missing", "target_commit", None, True),
            ("target_commit_mutated", "target_commit", "c" * 40, False),
            ("target_tree_missing", "target_tree", None, True),
            ("target_tree_mutated", "target_tree", "d" * 40, False),
            ("target_bundle_missing", "target_bundle_identity", None, True),
            ("target_bundle_mutated", "target_bundle_identity", "OTHER-BUNDLE", False),
            ("target_input_hash_missing", "target_input_hash", None, True),
            ("target_input_hash_mutated", "target_input_hash", "e" * 64, False),
            ("input_bindings_missing", "input_bindings", None, True),
            (
                "input_bindings_mutated",
                "input_bindings",
                {**self.input_bindings, "f05_input_jsonl_sha256": "f" * 64},
                False,
            ),
        )
        for name, field, value, missing in cases:
            with self.subTest(case=name):
                report, receipts = self.mutate_receipt_gate(
                    "CTLV", field, value, missing=missing
                )
                with patch("tools.m3top3.f05_r1_score_outputs.M3Top3V1Engine") as engine:
                    with self.assertRaises(F05ScoreOutputError):
                        build_f05_r1_outputs(
                            f05_input_jsonl=self.f05_bytes,
                            f02_input_batch_json=self.f02_bytes,
                            config_json=self.config_bytes,
                            aggregate_validation_json=report,
                            validation_receipt_json_by_role=receipts,
                            validation_receipt_path_by_role=self.receipt_paths,
                        )
                    engine.assert_not_called()

    def test_aggregate_identity_and_exact_descriptors_fail_before_engine_call(self):
        report_mutations = []
        for field, values in (
            ("schema_version", (None, "UNREVIEWED")),
            ("run_id", (None, "OTHER-RUN")),
            ("target_revision", (None, "D0")),
        ):
            for index, value in enumerate(values):
                def mutate(report, field=field, value=value):
                    if value is None:
                        report.pop(field)
                    else:
                        report[field] = value
                report_mutations.append((f"{field}_{index}", mutate))

        def remove_descriptor(report):
            report["validation_receipts"].pop()

        def reorder_descriptors(report):
            report["validation_receipts"][0], report["validation_receipts"][1] = (
                report["validation_receipts"][1],
                report["validation_receipts"][0],
            )

        def missing_descriptor_field(report):
            report["validation_receipts"][0].pop("receipt_id")

        def extra_descriptor_field(report):
            report["validation_receipts"][0]["unbound"] = True

        def mutate_descriptor_field(report):
            report["validation_receipts"][0]["validation_level"] = "L2"

        def duplicate_descriptor_path(report):
            report["validation_receipts"][1]["path"] = report["validation_receipts"][0]["path"]

        def falsify_descriptor_path(report):
            report["validation_receipts"][0]["path"] = "validation/FALSIFIED.json"

        report_mutations.extend(
            (
                ("descriptor_missing", remove_descriptor),
                ("descriptor_order", reorder_descriptors),
                ("descriptor_field_missing", missing_descriptor_field),
                ("descriptor_field_extra", extra_descriptor_field),
                ("descriptor_field_mutated", mutate_descriptor_field),
                ("descriptor_path_duplicate", duplicate_descriptor_path),
                ("descriptor_path_falsified", falsify_descriptor_path),
            )
        )
        for name, mutate in report_mutations:
            with self.subTest(case=name):
                report_bytes, receipts = self.gate_bytes()
                report = json.loads(report_bytes)
                mutate(report)
                with patch("tools.m3top3.f05_r1_score_outputs.M3Top3V1Engine") as engine:
                    with self.assertRaises(F05ScoreOutputError):
                        build_f05_r1_outputs(
                            f05_input_jsonl=self.f05_bytes,
                            f02_input_batch_json=self.f02_bytes,
                            config_json=self.config_bytes,
                            aggregate_validation_json=self._encode(report),
                            validation_receipt_json_by_role=receipts,
                            validation_receipt_path_by_role=self.receipt_paths,
                        )
                    engine.assert_not_called()

    def test_whole_set_rehash_cannot_rewrite_d1_or_validator_provenance(self):
        report_bytes, receipt_bytes = self.gate_bytes()
        baseline_report = json.loads(report_bytes)
        baseline_receipts = {
            role: json.loads(raw) for role, raw in receipt_bytes.items()
        }

        d0_report = copy.deepcopy(baseline_report)
        d0_receipts = copy.deepcopy(baseline_receipts)
        d0_bundle = f"AAA-M3TOP3-F05-R1-D0-{self.target_commit}-{self.target_tree}"
        d0_paths = {}
        d0_report["target_revision"] = "D0"
        d0_report["target_bundle_identity"] = d0_bundle
        for role in REQUIRED_VALIDATOR_ROLES:
            level = EXPECTED_VALIDATION_LEVEL_BY_ROLE[role]
            d0_paths[role] = f"validation/{role}_{level}_D0_RECEIPT.json"
            d0_receipts[role]["target_revision"] = "D0"
            d0_receipts[role]["target_bundle_identity"] = d0_bundle
            d0_receipts[role]["validator_identity"] = f"root/f05_r1_{role.lower()}_d0"
            d0_receipts[role]["receipt_id"] = (
                f"AAA-M3TOP3-F05-R1-D0-{role}-{level}-20260906-010000-01"
            )
            descriptor = next(
                item for item in d0_report["validation_receipts"] if item["role"] == role
            )
            descriptor["path"] = d0_paths[role]
        d0_report_bytes, d0_receipt_bytes = self.rehash_gate(d0_report, d0_receipts)

        arbitrary_report = copy.deepcopy(baseline_report)
        arbitrary_receipts = copy.deepcopy(baseline_receipts)
        for role in REQUIRED_VALIDATOR_ROLES:
            arbitrary_receipts[role]["validator_identity"] = f"arbitrary/{role.lower()}"
            arbitrary_receipts[role]["receipt_id"] = f"ARBITRARY-{role}-RECEIPT"
        arbitrary_report_bytes, arbitrary_receipt_bytes = self.rehash_gate(
            arbitrary_report, arbitrary_receipts
        )

        bundle_report = copy.deepcopy(baseline_report)
        bundle_receipts = copy.deepcopy(baseline_receipts)
        bundle_report["target_bundle_identity"] = "ARBITRARY-REHASHED-D1-BUNDLE"
        for role in REQUIRED_VALIDATOR_ROLES:
            bundle_receipts[role][
                "target_bundle_identity"
            ] = "ARBITRARY-REHASHED-D1-BUNDLE"
        bundle_report_bytes, bundle_receipt_bytes = self.rehash_gate(
            bundle_report, bundle_receipts
        )

        cases = (
            ("whole_set_d0_rewrite", d0_report_bytes, d0_receipt_bytes, d0_paths),
            (
                "whole_set_arbitrary_provenance",
                arbitrary_report_bytes,
                arbitrary_receipt_bytes,
                self.receipt_paths,
            ),
            (
                "whole_set_arbitrary_target_bundle",
                bundle_report_bytes,
                bundle_receipt_bytes,
                self.receipt_paths,
            ),
        )
        for name, report, receipts, paths in cases:
            with self.subTest(case=name):
                with patch("tools.m3top3.f05_r1_score_outputs.M3Top3V1Engine") as engine:
                    with self.assertRaises(F05ScoreOutputError):
                        build_f05_r1_outputs(
                            f05_input_jsonl=self.f05_bytes,
                            f02_input_batch_json=self.f02_bytes,
                            config_json=self.config_bytes,
                            aggregate_validation_json=report,
                            validation_receipt_json_by_role=receipts,
                            validation_receipt_path_by_role=paths,
                        )
                    engine.assert_not_called()

    def test_noncanonical_or_ungoverned_f05_input_fails_before_scoring(self):
        noncanonical = self.f05_bytes.replace(b'"availability_state":"AVAILABLE"', b'"availability_state": "AVAILABLE"', 1)
        report, receipts = self.gate_bytes()
        with patch("tools.m3top3.f05_r1_score_outputs.M3Top3V1Engine") as engine:
            with self.assertRaisesRegex(F05ScoreOutputError, "not canonical"):
                build_f05_r1_outputs(
                    f05_input_jsonl=noncanonical,
                    f02_input_batch_json=self.f02_bytes,
                    config_json=self.config_bytes,
                    aggregate_validation_json=report,
                    validation_receipt_json_by_role=receipts,
                    validation_receipt_path_by_role=self.receipt_paths,
                )
            engine.assert_not_called()


if __name__ == "__main__":
    unittest.main()
