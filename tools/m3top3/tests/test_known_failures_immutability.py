from __future__ import annotations

import tempfile
import threading
import unittest
import os
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from tools.m3top3.admission import M3Top3AdmissionError
from tools.m3top3.core import canonical_json_bytes
from tools.m3top3.ledger import AppendOnlyLedger, ImmutableJsonArtifactStore
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

    def test_empty_concurrent_snapshot_target_is_not_replaced(self):
        other_root=self.root/"empty-concurrent"
        target=other_root/self.built.snapshot_date.isoformat(); target.mkdir(parents=True)
        prior_inode=target.stat().st_ino
        with self.assertRaises(M3Top3AdmissionError) as caught:
            SnapshotStore(other_root).write(self.built,{})
        self.assertEqual(caught.exception.code,"IMMUTABLE_SNAPSHOT_COLLISION")
        self.assertEqual(target.stat().st_ino,prior_inode)
        self.assertEqual(list(target.iterdir()),[])

    def test_snapshot_manifest_is_published_last(self):
        other_root=self.root/"manifest-last"
        target=other_root/self.built.snapshot_date.isoformat(); real_link=os.link
        def fail_manifest(source,destination):
            if Path(destination).name=="manifest.json": raise OSError("injected manifest publish failure")
            return real_link(source,destination)
        with patch("tools.m3top3.snapshot.os.link",side_effect=fail_manifest):
            with self.assertRaises(M3Top3AdmissionError) as caught:
                SnapshotStore(other_root).write(self.built,{})
        self.assertEqual(caught.exception.code,"IMMUTABLE_SNAPSHOT_COLLISION")
        self.assertTrue((target/"pit_snapshot.jsonl").exists())
        self.assertTrue((target/"model_input.jsonl").exists())
        self.assertTrue((target/"retrieval_audit.jsonl").exists())
        self.assertFalse((target/"manifest.json").exists())

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

    def test_concurrent_different_payloads_cannot_both_append_or_overwrite(self):
        path=self.root/"concurrent"/"run.json"
        barrier=threading.Barrier(2)
        def attempt(row):
            barrier.wait()
            try: return ImmutableJsonArtifactStore(path).admit(row)
            except M3Top3AdmissionError as exc: return exc.code
        row_a={"run":"SAME","payload":"A"}; row_b={"run":"SAME","payload":"B"}
        with ThreadPoolExecutor(max_workers=2) as pool:
            results=list(pool.map(attempt,(row_a,row_b)))
        self.assertEqual(results.count("APPENDED"),1)
        self.assertEqual(results.count("NONDETERMINISTIC_RERUN"),1)
        self.assertIn(path.read_bytes(),(canonical_json_bytes(row_a)+b"\n",canonical_json_bytes(row_b)+b"\n"))

    def test_two_ledger_instances_cannot_append_conflicting_same_identity(self):
        path=self.root/"ledger-race"/"ledger.jsonl"
        first=AppendOnlyLedger(path,"id"); second=AppendOnlyLedger(path,"id")
        self.assertEqual(first.append({"id":"SAME","value":"A"}),"APPENDED")
        with self.assertRaises(M3Top3AdmissionError) as caught: second.append({"id":"SAME","value":"B"})
        self.assertEqual((caught.exception.code,caught.exception.exit_code),("NONDETERMINISTIC_RERUN",3))
        self.assertEqual(path.read_bytes(),canonical_json_bytes({"id":"SAME","value":"A"})+b"\n")

    def test_ledger_admission_failure_precedes_result_artifact_write(self):
        class RejectingLedger:
            def append_many(self,rows):
                raise M3Top3AdmissionError("NONDETERMINISTIC_RERUN","concurrent ledger collision",exit_code=3)
        output=self.root/"ledger-first-output"
        runner,_=diagnostic_runner(self.price,self.dates,CountingScorer("9"))
        with self.assertRaises(M3Top3AdmissionError) as caught:
            runner.run_snapshot(self.snapshot_dir,output,RejectingLedger())
        self.assertEqual((caught.exception.code,caught.exception.exit_code),("NONDETERMINISTIC_RERUN",3))
        self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
