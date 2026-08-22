from __future__ import annotations

import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from tools.m3top3.admission import M3Top3AdmissionError
from tools.m3top3.snapshot import SnapshotStore
from tools.m3top3.tests._known_failure_helpers import CountingScorer, diagnostic_runner, materialize_ready_snapshot


class KnownFailureImmutabilityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.snapshot_dir, self.dates, self.price, self.built = materialize_ready_snapshot(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def _snapshot_bytes(self):
        return {p.name: p.read_bytes() for p in self.snapshot_dir.iterdir() if p.is_file()}

    def test_kf_imm_001_identical_snapshot_reuse_preserves_bytes_and_mtime(self):
        prior = self._snapshot_bytes()
        manifest = self.snapshot_dir / "manifest.json"
        prior_mtime = manifest.stat().st_mtime_ns
        result = SnapshotStore(self.snapshot_dir.parent).write(self.built, {"generator_version": "different-metadata-must-not-overwrite"})
        self.assertEqual(result["snapshot_content_hash"], self.built.snapshot_set_entry_hash)
        self.assertEqual(self._snapshot_bytes(), prior)
        self.assertEqual(manifest.stat().st_mtime_ns, prior_mtime)

    def test_kf_imm_002_snapshot_collision_preserves_prior_bytes(self):
        prior = self._snapshot_bytes()
        changed = replace(self.built, snapshot_set_entry_hash="f" * 64)
        with self.assertRaises(M3Top3AdmissionError) as caught:
            SnapshotStore(self.snapshot_dir.parent).write(changed, {"generator_version": "test"})
        self.assertEqual(caught.exception.code, "IMMUTABLE_SNAPSHOT_COLLISION")
        self.assertEqual(self._snapshot_bytes(), prior)

    def test_snapshot_incomplete_existing_directory_is_collision(self):
        other_root = self.root / "incomplete"
        target = other_root / self.built.snapshot_date.isoformat()
        target.mkdir(parents=True)
        marker = target / "marker"
        marker.write_bytes(b"prior")
        with self.assertRaises(M3Top3AdmissionError) as caught:
            SnapshotStore(other_root).write(self.built, {})
        self.assertEqual(caught.exception.code, "IMMUTABLE_SNAPSHOT_COLLISION")
        self.assertEqual(marker.read_bytes(), b"prior")

    def test_kf_imm_003_same_run_id_different_result_is_rejected(self):
        output = self.root / "results"
        runner1, _ = diagnostic_runner(self.price, self.dates, CountingScorer("9"))
        first = runner1.run_snapshot(self.snapshot_dir, output)
        result_path = output / self.dates[0].isoformat() / f"{first['validation_run_id']}.json"
        prior = result_path.read_bytes()
        runner2, _ = diagnostic_runner(self.price, self.dates, CountingScorer("8"))
        with self.assertRaises(M3Top3AdmissionError) as caught:
            runner2.run_snapshot(self.snapshot_dir, output)
        self.assertEqual(caught.exception.code, "NONDETERMINISTIC_RERUN")
        self.assertEqual(result_path.read_bytes(), prior)

    def test_kf_imm_004_same_run_id_identical_bytes_reused(self):
        output = self.root / "results"
        runner, _ = diagnostic_runner(self.price, self.dates, CountingScorer("9"))
        first = runner.run_snapshot(self.snapshot_dir, output)
        result_path = output / self.dates[0].isoformat() / f"{first['validation_run_id']}.json"
        prior = result_path.read_bytes(); prior_mtime = result_path.stat().st_mtime_ns
        second = runner.run_snapshot(self.snapshot_dir, output)
        self.assertEqual(second["artifact_state"], "REUSED")
        self.assertEqual(result_path.read_bytes(), prior)
        self.assertEqual(result_path.stat().st_mtime_ns, prior_mtime)

    def test_different_run_ids_coexist_for_same_snapshot_date(self):
        class OtherVersionScorer(CountingScorer):
            model_version = "diagnostic-v1"
        output = self.root / "results"
        runner1, _ = diagnostic_runner(self.price, self.dates, CountingScorer("9"))
        runner2, _ = diagnostic_runner(self.price, self.dates, OtherVersionScorer("9"))
        first = runner1.run_snapshot(self.snapshot_dir, output)
        second = runner2.run_snapshot(self.snapshot_dir, output)
        self.assertNotEqual(first["validation_run_id"], second["validation_run_id"])
        self.assertEqual(len(list((output / self.dates[0].isoformat()).glob("*.json"))), 2)


if __name__ == "__main__":
    unittest.main()
