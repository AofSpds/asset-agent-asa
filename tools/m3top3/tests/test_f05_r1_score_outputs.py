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
    CLAIM_STATUS,
    EXPECTED_CONFIG_SHA256,
    EXPECTED_F02_INPUT_BATCH_SHA256,
    F02_FIXED_COMPANY_IDS,
    FIVE_FILENAME,
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
        cls.target_bundle = "M3TOP3-F05-R1-EXACT-TARGET-TEST"

    def gate_bytes(self, **report_changes):
        receipts = {}
        descriptors = []
        for role in REQUIRED_VALIDATOR_ROLES:
            value = {
                "role_verdicts": {role: "PASS"},
                "target_author": False,
                "target_edited": False,
                "target_commit": self.target_commit,
                "target_tree": self.target_tree,
                "target_bundle_identity": self.target_bundle,
                "target_input_hash": self.merged_input_hash,
                "input_bindings": self.input_bindings,
            }
            raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
            receipts[role] = raw
            descriptors.append({"role": role, "sha256": hashlib.sha256(raw).hexdigest()})
        report = {
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

    def build(self):
        report, receipts = self.gate_bytes()
        return build_f05_r1_outputs(
            f05_input_jsonl=self.f05_bytes,
            f02_input_batch_json=self.f02_bytes,
            config_json=self.config_bytes,
            aggregate_validation_json=report,
            validation_receipt_json_by_role=receipts,
        )

    def test_exact_gate_calls_unchanged_engine_and_renders_three_provisional_artifacts(self):
        self.assertEqual(hashlib.sha256(self.f02_bytes).hexdigest(), EXPECTED_F02_INPUT_BATCH_SHA256)
        self.assertEqual(hashlib.sha256(self.config_bytes).hexdigest(), EXPECTED_CONFIG_SHA256)
        first = self.build()
        second = self.build()
        self.assertEqual(first.score_jsonl, second.score_jsonl)
        self.assertEqual(first.provisional_ranking_csv, second.provisional_ranking_csv)
        self.assertEqual(first.f02_f05_exact_five_csv, second.f02_f05_exact_five_csv)

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
            )

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
                )
            engine.assert_not_called()


if __name__ == "__main__":
    unittest.main()
