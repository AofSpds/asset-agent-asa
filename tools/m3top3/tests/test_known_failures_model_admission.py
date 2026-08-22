from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from tools.m3top3.admission import M3Top3AdmissionError, verify_official_scorer
from tools.m3top3.cli_run_backtest import main as backtest_main
from tools.m3top3.core import hash_file, sha256_hex
from tools.m3top3.model_interface import DiagnosticFixtureScorer


class OfficialFixtureScorer:
    model_id = "M3TOP3"
    model_version = "v1-exact"
    model_schema_version = "schema-v1"
    feature_set_version = "features-v1"

    def __init__(self, artifact_path: Path, config_hash: str):
        self.artifact_path = artifact_path
        self.config_hash = config_hash


class KnownFailureModelAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.artifact = self.root / "scorer.bin"
        self.artifact.write_bytes(b"exact-scorer")
        self.config_bytes = b'{"model":"M3TOP3","version":"v1"}'
        self.scorer = OfficialFixtureScorer(self.artifact, sha256_hex(self.config_bytes))
        self.receipt = {
            "model_id": self.scorer.model_id,
            "model_version": self.scorer.model_version,
            "model_schema_version": self.scorer.model_schema_version,
            "feature_set_version": self.scorer.feature_set_version,
            "scorer_artifact_sha256": hash_file(self.artifact),
            "config_sha256": sha256_hex(self.config_bytes),
            "baseline_identity": "BASELINE-EXACT",
            "authority_receipt": "OWNER-RECEIPT",
        }

    def tearDown(self):
        self.tmp.cleanup()

    def assert_code(self, fn, code):
        with self.assertRaises(M3Top3AdmissionError) as caught:
            fn()
        self.assertEqual(caught.exception.code, code)
        self.assertEqual(caught.exception.exit_code, 4)

    def test_kf_mod_001_official_kill_switch_precedes_missing_plugin(self):
        config = self.root / "config.json"
        config.write_text(json.dumps({"execution_mode": "OFFICIAL", "scorer_plugin": "missing_package:MissingScorer"}), encoding="utf-8")
        output = self.root / "output"
        with redirect_stdout(io.StringIO()):
            status = backtest_main(["--config", str(config), "--snapshot-root", str(self.root / "snapshots"), "--output", str(output)])
        self.assertEqual(status, 4)
        self.assertFalse(output.exists())

    def test_kf_mod_002_diagnostic_scorer_denied_in_official_mode(self):
        self.assert_code(lambda: verify_official_scorer(DiagnosticFixtureScorer(), self.config_bytes, self.receipt), "OFFICIAL_MODE_GLOBALLY_BLOCKED")

    def test_kf_mod_003_missing_exact_identity_receipt(self):
        self.assert_code(lambda: verify_official_scorer(self.scorer, self.config_bytes, None), "OFFICIAL_MODE_GLOBALLY_BLOCKED")

    def test_kf_mod_004_declared_config_hash_mismatch(self):
        receipt = dict(self.receipt)
        receipt["config_sha256"] = "0" * 64
        self.assert_code(lambda: verify_official_scorer(self.scorer, self.config_bytes, receipt), "OFFICIAL_MODE_GLOBALLY_BLOCKED")

    def test_kf_mod_005_working_placeholder_config_denied(self):
        config = b'{"model":"M3TOP3","status":"WORKING"}'
        scorer = OfficialFixtureScorer(self.artifact, sha256_hex(config))
        receipt = dict(self.receipt)
        receipt["config_sha256"] = sha256_hex(config)
        self.assert_code(lambda: verify_official_scorer(scorer, config, receipt), "OFFICIAL_MODE_GLOBALLY_BLOCKED")

    def test_self_asserted_exact_official_fixture_is_still_globally_blocked(self):
        self.assert_code(lambda: verify_official_scorer(self.scorer,self.config_bytes,self.receipt),"OFFICIAL_MODE_GLOBALLY_BLOCKED")


if __name__ == "__main__":
    unittest.main()
