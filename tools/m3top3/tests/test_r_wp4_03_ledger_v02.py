from __future__ import annotations

import hashlib
import json
import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from tools.m3top3.admission import M3Top3AdmissionError
from tools.m3top3.core import canonical_json_bytes
from tools.m3top3.ledger import FullRunArtifactStore, PredictionLedger, publication_transaction


def _result(run: str, lineage: str, companies: tuple[str, ...] = ("C1", "C2")) -> dict:
    ranked = []
    for rank, company in enumerate(companies, 1):
        ranked.append(
            {
                "model_score_id": f"score-{run}-{company}",
                "pit_snapshot_id": f"pit-{run}-{company}",
                "company_id": company,
                "security_code": f"{rank:06d}",
                "model_version": "diagnostic-v1",
                "raw_score": str(100 - rank),
                "rank": rank,
                "selected_top3": rank <= 3,
                "denominator_member_id": f"denom-{run}-{company}",
            }
        )
    return {
        "validation_run_id": run,
        "lineage_hash": lineage,
        "ranked_count": len(ranked),
        "outcome_count": len(ranked),
        "scorer_outputs": [
            {"model_score_id": row["model_score_id"], "company_id": row["company_id"]}
            for row in ranked
        ],
        "ranked": ranked,
        "outcomes": [
            {"model_score_id": row["model_score_id"], "company_id": row["company_id"]}
            for row in ranked
        ],
    }


def _prediction_rows(result: dict) -> list[dict]:
    return [
        PredictionLedger.build_record(
            row,
            "2026-08-23T00:00:00+09:00",
            f"input-{row['company_id']}",
            lineage_hash=result["lineage_hash"],
        )
        for row in result["ranked"]
    ]


class FullRunArtifactStoreV02Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _store(self, run: str) -> FullRunArtifactStore:
        return FullRunArtifactStore(self.root / "runs" / f"{run}.json")

    def _assert_incomplete(self, action) -> None:
        with self.assertRaises(M3Top3AdmissionError) as caught:
            action()
        self.assertEqual(
            (caught.exception.code, caught.exception.exit_code),
            ("INCOMPLETE_RESULT_PUBLICATION", 3),
        )

    def test_complete_no_ledger_commit_is_exactly_reusable(self) -> None:
        result = _result("R1", "L1")
        store = self._store("R1")
        self.assertEqual(store.preflight(result), "APPENDABLE")
        self.assertEqual(store.publish(result), "APPENDED")
        self.assertEqual(self._store("R1").preflight(result), "REUSED")
        manifest = json.loads(store.manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["schema_version"], "m3top3-full-run-commit-v2")
        self.assertEqual(manifest["prediction_batch_count"], 0)
        self.assertNotIn("ledger_sha256", manifest)

    def test_exact_partial_artifact_without_manifest_is_never_resumed(self) -> None:
        result = _result("R1", "L1")
        store = self._store("R1")
        payloads = store._payloads(result)
        partial_path, partial_payload = next(iter(payloads.items()))
        partial_path.parent.mkdir(parents=True)
        partial_path.write_bytes(partial_payload)
        before = {path: path.read_bytes() for path in payloads if path.exists()}
        self._assert_incomplete(lambda: store.preflight(result))
        self.assertEqual(before, {path: path.read_bytes() for path in payloads if path.exists()})
        self.assertFalse(store.manifest_path.exists())

    def test_manifest_without_complete_artifact_set_is_rejected(self) -> None:
        result = _result("R1", "L1")
        store = self._store("R1")
        store.manifest_path.parent.mkdir(parents=True)
        store.manifest_path.write_text("{}\n", encoding="utf-8")
        self._assert_incomplete(lambda: store.preflight(result))

    def test_committed_set_cannot_disappear_then_be_recreated_after_preflight(self) -> None:
        result = _result("R1", "L1")
        original = self._store("R1")
        original.preflight(result)
        original.publish(result)
        admitted = self._store("R1")
        self.assertEqual(admitted.preflight(result), "REUSED")
        for path in (*admitted._artifact_paths, admitted.manifest_path):
            path.unlink()
        self._assert_incomplete(lambda: admitted.publish(result))
        self.assertFalse(any(path.exists() for path in (*admitted._artifact_paths, admitted.manifest_path)))

    def test_malformed_or_noncanonical_commit_manifest_is_not_a_commit(self) -> None:
        result = _result("R1", "L1")
        store = self._store("R1")
        store.preflight(result)
        store.publish(result)
        manifest = json.loads(store.manifest_path.read_text(encoding="utf-8"))
        store.manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        self._assert_incomplete(lambda: self._store("R1").preflight(result))

    def test_ledger_publication_requires_matching_pre_mutation_preflight(self) -> None:
        result = _result("R1", "L1")
        ledger = PredictionLedger(self.root / "prediction.jsonl")
        ledger.append_many(_prediction_rows(result))
        self._assert_incomplete(lambda: self._store("R1").publish(result, ledger.path))
        self.assertFalse((self.root / "runs").exists())

    def test_partial_artifact_preflight_fails_before_ledger_mutation(self) -> None:
        result = _result("R1", "L1")
        store = self._store("R1")
        store.path.parent.mkdir(parents=True)
        store.path.write_bytes(store._payloads(result)[store.path])
        ledger = PredictionLedger(self.root / "prediction.jsonl")
        self._assert_incomplete(lambda: store.preflight(result, ledger.path))
        self.assertFalse(ledger.path.exists())

    def test_two_runs_share_ledger_then_first_run_reuses(self) -> None:
        ledger = PredictionLedger(self.root / "prediction.jsonl")
        result1 = _result("R1", "L1")
        store1 = self._store("R1")
        self.assertEqual(store1.preflight(result1, ledger.path), "APPENDABLE")
        ledger.append_many(_prediction_rows(result1))
        self.assertEqual(store1.publish(result1, ledger.path), "APPENDED")
        first_ledger_hash = hashlib.sha256(ledger.path.read_bytes()).hexdigest()

        result2 = _result("R2", "L2", ("C3", "C4", "C5"))
        store2 = self._store("R2")
        self.assertEqual(store2.preflight(result2, ledger.path), "APPENDABLE")
        ledger.append_many(_prediction_rows(result2))
        self.assertEqual(store2.publish(result2, ledger.path), "APPENDED")
        self.assertNotEqual(first_ledger_hash, hashlib.sha256(ledger.path.read_bytes()).hexdigest())

        reused = self._store("R1")
        self.assertEqual(reused.preflight(result1, ledger.path), "REUSED")
        self.assertEqual(reused.publish(result1, ledger.path), "REUSED")
        self.assertEqual(self._store("R1").publish(result1, ledger.path), "REUSED")
        manifest1 = json.loads(reused.manifest_path.read_text(encoding="utf-8"))
        manifest2 = json.loads(store2.manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest1["prediction_batch_count"], 2)
        self.assertEqual(manifest2["prediction_batch_count"], 3)
        self.assertTrue(set(manifest1["prediction_batch_identity_set"]).isdisjoint(manifest2["prediction_batch_identity_set"]))
        self.assertNotIn("ledger_sha256", manifest1)

    def test_committed_run_rejects_missing_live_prediction_member(self) -> None:
        result = _result("R1", "L1")
        ledger = PredictionLedger(self.root / "prediction.jsonl")
        store = self._store("R1")
        store.preflight(result, ledger.path)
        rows = _prediction_rows(result)
        ledger.append_many(rows)
        store.publish(result, ledger.path)
        ledger.path.write_bytes(canonical_json_bytes(rows[0]) + b"\n")
        self._assert_incomplete(lambda: self._store("R1").preflight(result, ledger.path))

    def test_committed_run_rejects_changed_live_prediction_payload(self) -> None:
        result = _result("R1", "L1")
        ledger = PredictionLedger(self.root / "prediction.jsonl")
        store = self._store("R1")
        store.preflight(result, ledger.path)
        rows = _prediction_rows(result)
        ledger.append_many(rows)
        store.publish(result, ledger.path)
        rows[0]["score"] = "tampered"
        ledger.path.write_bytes(b"".join(canonical_json_bytes(row) + b"\n" for row in rows))
        with self.assertRaises(M3Top3AdmissionError) as caught:
            self._store("R1").preflight(result, ledger.path)
        self.assertEqual(
            (caught.exception.code, caught.exception.exit_code),
            ("NONDETERMINISTIC_RERUN", 3),
        )

    def test_commit_manifest_is_admitted_last(self) -> None:
        calls: list[Path] = []

        class RecordingStore(FullRunArtifactStore):
            @staticmethod
            def _admit_bytes(path: Path, payload: bytes) -> str:
                calls.append(path)
                return FullRunArtifactStore._admit_bytes(path, payload)

        result = _result("R1", "L1")
        store = RecordingStore(self.root / "runs" / "R1.json")
        store.preflight(result)
        store.publish(result)
        self.assertEqual(calls[-1], store.manifest_path)
        self.assertEqual(len(calls), 5)

    def test_shared_ledger_identity_serializes_different_run_transactions(self) -> None:
        first_entered = threading.Event()
        release_first = threading.Event()
        second_attempted = threading.Event()
        second_entered = threading.Event()

        def first() -> None:
            with publication_transaction("run:R1", "ledger:shared"):
                first_entered.set()
                self.assertTrue(release_first.wait(2))

        def second() -> None:
            self.assertTrue(first_entered.wait(2))
            second_attempted.set()
            with publication_transaction("run:R2", "ledger:shared"):
                second_entered.set()

        with ThreadPoolExecutor(max_workers=2) as pool:
            first_future = pool.submit(first)
            second_future = pool.submit(second)
            self.assertTrue(second_attempted.wait(2))
            self.assertFalse(second_entered.wait(0.05))
            release_first.set()
            first_future.result(timeout=2)
            second_future.result(timeout=2)
        self.assertTrue(second_entered.is_set())


if __name__ == "__main__":
    unittest.main()
