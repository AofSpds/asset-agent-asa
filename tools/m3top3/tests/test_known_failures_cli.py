from __future__ import annotations

import io
import json
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from tools.m3top3.admission import EXIT_INTEGRITY, M3Top3AdmissionError
from tools.m3top3.cli_build_snapshots import main as snapshot_main
from tools.m3top3.cli_run_backtest import main as backtest_main
from tools.m3top3.core import hash_file
from tools.m3top3.model_interface import DiagnosticFixtureScorer
from tools.m3top3.tests._known_failure_helpers import CountingScorer, materialize_ready_snapshot, price_provider, standard_price_rows


class KnownFailureCLITests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def _run_quiet(self, fn, argv):
        stream = io.StringIO()
        with redirect_stdout(stream):
            status = fn(argv)
        return status, json.loads(stream.getvalue())

    def _backtest_config(self, path, snapshot_date, window_end, **updates):
        config = {
            "execution_mode": "DIAGNOSTIC",
            "scorer_plugin": "fixture:Scorer",
            "tie_break_policy": "COMPANY_ID_ASC_DIAGNOSTIC",
            "price_paths": ["unused.parquet"],
            "price_dataset_id": "P",
            "price_dataset_hash": "unused",
            "price_source_semantics": "RAW_IMMUTABLE",
            "window_end_by_snapshot_date": {snapshot_date: window_end},
            "window_protocol_version": "test-v1",
            "validation_protocol_version": "test-v1",
        }
        config.update(updates)
        path.write_text(json.dumps(config), encoding="utf-8")

    def test_kf_cli_001_blocked_tie_returns_two_and_no_output(self):
        snapshot_dir, dates, price, _ = materialize_ready_snapshot(self.root)
        config = self.root / "backtest.json"
        self._backtest_config(config, dates[0].isoformat(), dates[5].isoformat())

        class BlockedRunner:
            def __init__(self, *args, **kwargs): pass
            def run_snapshot(self, *args, **kwargs):
                return {"status": "BLOCKED_TIE_POLICY_UNRESOLVED", "snapshot_date": dates[0].isoformat()}

        output = self.root / "output"
        with patch("tools.m3top3.cli_run_backtest.load_scorer", return_value=CountingScorer()), patch("tools.m3top3.cli_run_backtest.DuckDBParquetPriceProvider", return_value=price), patch("tools.m3top3.cli_run_backtest.ValidationRunner", BlockedRunner):
            status, summary = self._run_quiet(backtest_main, ["--config", str(config), "--snapshot-root", str(snapshot_dir.parent), "--output", str(output)])
        self.assertEqual(status, 2)
        self.assertEqual(summary["blocked"], 1)
        self.assertFalse(output.exists())

    def test_kf_cli_002_partial_snapshot_returns_two_not_generated(self):
        dates = [standard_price_rows()[0]["date"]]
        price = price_provider(self.root, standard_price_rows()[:2])
        universe = self.root / "universe.jsonl"
        universe.write_text(json.dumps({"company_id":"C1","security_code":"005930","valid_from":"2020-01-01","valid_to":None,"operational_member":True,"tradable_eligible":None,"universe_record_id":"U1"}) + "\n", encoding="utf-8")
        features = self.root / "features.jsonl"; features.write_text("", encoding="utf-8")
        config = self.root / "snapshot.json"
        config.write_text(json.dumps({"execution_mode":"DIAGNOSTIC","universe_jsonl":str(universe),"universe_release_id":"U","universe_authority_status":"DIAGNOSTIC","features_jsonl":str(features),"feature_source_version":"F","price_paths":["unused"],"price_dataset_id":"P","price_dataset_hash":price.dataset_hash,"price_source_semantics":"RAW_IMMUTABLE"}), encoding="utf-8")
        output = self.root / "snap-output"
        with patch("tools.m3top3.cli_build_snapshots.DuckDBParquetPriceProvider", return_value=price):
            status, summary = self._run_quiet(snapshot_main, ["--config",str(config),"--start",dates[0],"--end",dates[0],"--output",str(output)])
        self.assertEqual(status, 2)
        self.assertEqual(summary["blocked"], 1)
        self.assertEqual(summary["generated"], 0)
        self.assertFalse(output.exists())

    def test_kf_cli_003_corrupt_snapshot_returns_three_and_no_output(self):
        snapshot_dir, dates, price, _ = materialize_ready_snapshot(self.root)
        (snapshot_dir / "model_input.jsonl").write_text("{bad\n", encoding="utf-8")
        config = self.root / "backtest.json"
        self._backtest_config(config, dates[0].isoformat(), dates[5].isoformat())
        output = self.root / "output"
        with patch("tools.m3top3.cli_run_backtest.load_scorer", return_value=CountingScorer()), patch("tools.m3top3.cli_run_backtest.DuckDBParquetPriceProvider", return_value=price):
            status, summary = self._run_quiet(backtest_main, ["--config", str(config), "--snapshot-root", str(snapshot_dir.parent), "--output", str(output)])
        self.assertEqual(status, 3)
        self.assertEqual(summary["failed_integrity"], 1)
        self.assertFalse(output.exists())

    def test_snapshot_cli_preflight_integrity_returns_three_without_output(self):
        config = self.root / "snapshot.json"
        config.write_text(json.dumps({"execution_mode":"DIAGNOSTIC","universe_jsonl":"unused","universe_release_id":"U","universe_authority_status":"DIAGNOSTIC"}), encoding="utf-8")
        output = self.root / "output"
        error = M3Top3AdmissionError("PRICE_COMPONENT_HASH_MISMATCH", "bad", exit_code=EXIT_INTEGRITY)
        with patch("tools.m3top3.cli_build_snapshots.JsonlUniverseProvider", side_effect=error):
            status, summary = self._run_quiet(snapshot_main, ["--config",str(config),"--start","2025-01-02","--end","2025-01-02","--output",str(output)])
        self.assertEqual(status, 3)
        self.assertEqual(summary["code"], "PRICE_COMPONENT_HASH_MISMATCH")
        self.assertFalse(output.exists())

    def test_official_diagnostic_scorer_returns_four_without_output(self):
        config_bytes = b'{"model":"M3TOP3","version":"v1"}'
        scorer_config = self.root / "scorer.json"; scorer_config.write_bytes(config_bytes)
        config = self.root / "official.json"
        config.write_text(json.dumps({"execution_mode":"OFFICIAL","scorer_plugin":"fixture:Scorer","scorer_config_path":str(scorer_config),"official_model_receipt":{}}), encoding="utf-8")
        output = self.root / "output"
        with patch("tools.m3top3.cli_run_backtest.load_scorer", return_value=DiagnosticFixtureScorer()):
            status, summary = self._run_quiet(backtest_main, ["--config",str(config),"--snapshot-root",str(self.root/"snapshots"),"--output",str(output)])
        self.assertEqual(status, 4)
        self.assertEqual(summary["code"], "OFFICIAL_MODE_GLOBALLY_BLOCKED")
        self.assertFalse(output.exists())

    def test_snapshot_cli_official_mode_globally_blocked_without_output(self):
        config=self.root/"snapshot-official.json"
        config.write_text(json.dumps({"execution_mode":"OFFICIAL"}),encoding="utf-8")
        output=self.root/"official-output"
        status,summary=self._run_quiet(snapshot_main,["--config",str(config),"--start","2025-01-02","--end","2025-01-02","--output",str(output)])
        self.assertEqual(status,4)
        self.assertEqual(summary["code"],"OFFICIAL_MODE_GLOBALLY_BLOCKED")
        self.assertFalse(output.exists())

    def test_malformed_feature_jsonl_is_integrity_exit_three(self):
        universe=self.root/"universe.jsonl"
        universe.write_text(json.dumps({"company_id":"C1","security_code":"005930","valid_from":"2020-01-01","valid_to":None,"operational_member":True,"tradable_eligible":True,"universe_record_id":"U1"})+"\n",encoding="utf-8")
        features=self.root/"features.jsonl"; features.write_text("{malformed\n",encoding="utf-8")
        config=self.root/"snapshot-malformed-feature.json"
        config.write_text(json.dumps({"execution_mode":"DIAGNOSTIC","universe_jsonl":str(universe),"universe_release_id":"U","universe_authority_status":"DIAGNOSTIC","features_jsonl":str(features),"feature_source_version":"F","price_paths":["unused"],"price_dataset_id":"P","price_dataset_hash":"unused"}),encoding="utf-8")
        output=self.root/"malformed-output"
        status,summary=self._run_quiet(snapshot_main,["--config",str(config),"--start","2025-01-02","--end","2025-01-02","--output",str(output)])
        self.assertEqual(status,3)
        self.assertEqual(summary["code"],"BLOCKED_INPUT_INTEGRITY")
        self.assertFalse(output.exists())

    def test_hidden_staging_snapshot_directory_is_not_enumerated(self):
        snapshot_dir,dates,price,_=materialize_ready_snapshot(self.root)
        staging=snapshot_dir.parent/f".{snapshot_dir.name}.deadbeef.staging"
        shutil.copytree(snapshot_dir,staging)
        config=self.root/"backtest-staging.json"
        self._backtest_config(config,dates[0].isoformat(),dates[5].isoformat())
        output=self.root/"staging-output"
        with patch("tools.m3top3.cli_run_backtest.load_scorer",return_value=CountingScorer()),patch("tools.m3top3.cli_run_backtest.DuckDBParquetPriceProvider",return_value=price):
            status,summary=self._run_quiet(backtest_main,["--config",str(config),"--snapshot-root",str(snapshot_dir.parent),"--output",str(output)])
        self.assertEqual(status,0)
        self.assertEqual(summary["requested"],1)
        self.assertEqual(summary["admitted"],1)


if __name__ == "__main__":
    unittest.main()
