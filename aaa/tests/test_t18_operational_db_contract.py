from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC = REPO_ROOT / "aaa" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aaa.ops.operational_state import (
    JsonRunRegistryReader,
    ShadowOperationalStateReader,
    ShadowReconciliationError,
    inventory_json_run_registry,
    reconcile_run_rows,
)


class StaticReader:
    def __init__(self, rows):
        self.rows = tuple(rows)

    def list_runs(self):
        return self.rows


class T18OperationalDatabaseContractTests(unittest.TestCase):
    def test_migration_declares_postgresql_authority_boundaries(self):
        sql = (REPO_ROOT / "aaa" / "db" / "migrations" / "0001_operational_execution_plane.sql").read_text(
            encoding="utf-8"
        )
        required = (
            "CREATE TABLE IF NOT EXISTS aaa_ops.work_order_refs",
            "CREATE TABLE IF NOT EXISTS aaa_ops.runs",
            "CREATE TABLE IF NOT EXISTS aaa_ops.run_events",
            "CREATE TABLE IF NOT EXISTS aaa_ops.results",
            "CREATE TABLE IF NOT EXISTS aaa_ops.experiments",
            "CREATE TABLE IF NOT EXISTS aaa_ops.experiment_runs",
            "CREATE TABLE IF NOT EXISTS aaa_ops.snapshot_refs",
            "DEFERRABLE INITIALLY DEFERRED",
            "RUN_EVENTS_APPEND_ONLY",
            "RESULT_MUST_BE_BOUND_IN_SAME_TRANSACTION",
            "TERMINAL_STATE_VERDICT_MISMATCH",
            "STALE_OR_INVALID_LEASE",
            "transaction_timestamp()",
            "CREATE OR REPLACE VIEW aaa_ops.run_projection",
        )
        for token in required:
            self.assertIn(token, sql)

        forbidden = ("redis", "kafka", "kubernetes", "sqlite")
        lowered = sql.lower()
        for token in forbidden:
            self.assertNotIn(token, lowered)

    def test_source_identity_is_successor_migration_not_0001_rewrite(self):
        sql = (REPO_ROOT / "aaa" / "db" / "migrations" / "0002_json_registry_source_identity.sql").read_text(
            encoding="utf-8"
        )
        for token in (
            "source_json_path",
            "source_json_sha256",
            "source_json_byte_size",
            "canonical_output",
            "runs_source_json_path_unique",
        ):
            self.assertIn(token, sql)

    def test_0003_encodes_exact_retry_and_atomic_completion(self):
        sql = (REPO_ROOT / "aaa" / "db" / "migrations" / "0003_idempotent_events_atomic_completion.sql").read_text(
            encoding="utf-8"
        )
        for token in (
            "aaa_ops.append_run_event_idempotent",
            "pg_advisory_xact_lock",
            "IDEMPOTENCY_KEY_REUSE_MISMATCH",
            "aaa_ops.complete_run_atomic",
            "STALE_OR_INVALID_LEASE",
            "INVALID_RUN_TIME_EVIDENCE",
            "COMPLETED_WITH_FINDINGS",
        ):
            self.assertIn(token, sql)

    def test_migration_manifest_binds_all_exact_sql_bytes_and_preserves_p09_targets(self):
        manifest_path = REPO_ROOT / "aaa" / "db" / "MIGRATIONS.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        versions = [item["version"] for item in manifest["migrations"]]
        self.assertEqual(versions[:3], ["0001", "0002", "0003"])
        self.assertEqual(len(versions), len(set(versions)))
        for migration in manifest["migrations"]:
            sql_bytes = (REPO_ROOT / migration["path"]).read_bytes()
            self.assertEqual(hashlib.sha256(sql_bytes).hexdigest(), migration["sha256"])
        self.assertEqual(
            manifest["authority"],
            "NON_AUTHORITATIVE_SHADOW_UNTIL_EXPLICIT_OWNER_CUTOVER",
        )
        self.assertEqual(
            manifest["p09_non_interference"]["failed_target"],
            "80378610f9ac9e688c52417f0416e01c057400a7",
        )
        self.assertEqual(
            manifest["p09_non_interference"]["rerun_target"],
            "30fdb278c218b24e44d66eb5f47935a196dc4f8c",
        )
        self.assertFalse(manifest["sqlite_certifying"])
        self.assertFalse(manifest["redis_required"])
        self.assertFalse(manifest["kafka_required"])
        self.assertFalse(manifest["kubernetes_required"])

    def test_json_inventory_is_byte_exact_and_sorted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            runs = root / "control" / "aaa" / "runs"
            runs.mkdir(parents=True)
            payload_b = b'{"run_id":"RUN-B","state":"BLOCKED"}\n'
            payload_a = b'{"run_id":"RUN-A","state":"READY_NOT_DISPATCHED"}\n'
            (runs / "z.json").write_bytes(payload_b)
            (runs / "a.json").write_bytes(payload_a)

            inventory = inventory_json_run_registry(root)
            self.assertEqual([item.path for item in inventory], [
                "control/aaa/runs/a.json",
                "control/aaa/runs/z.json",
            ])
            self.assertEqual(inventory[0].byte_size, len(payload_a))
            self.assertEqual(inventory[0].sha256, hashlib.sha256(payload_a).hexdigest())
            self.assertEqual(inventory[1].sha256, hashlib.sha256(payload_b).hexdigest())

    def test_duplicate_run_identity_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            runs = root / "control" / "aaa" / "runs"
            runs.mkdir(parents=True)
            (runs / "a.json").write_text('{"run_id":"RUN-1"}', encoding="utf-8")
            (runs / "b.json").write_text('{"run_id":"RUN-1"}', encoding="utf-8")
            with self.assertRaisesRegex(ShadowReconciliationError, "DUPLICATE_RUN_ID"):
                inventory_json_run_registry(root)

    def test_shadow_reader_returns_json_only_on_exact_projection_match(self):
        authority = [{
            "run_id": "RUN-1",
            "process_id": "P18",
            "work_order_id": "WO-1",
            "responsible_persona": "SEMI-CONTROL-ARCHITECT",
            "executor_role": "ENGINEERING_IMPLEMENTATION",
            "state": "DISPATCHED_AWAITING_ACK",
            "repository": "AofSpds/asset-agent-asa",
            "exact_base_commit": "a" * 40,
            "branch": "aaa-t18-operational-db-v0.1",
            "started_at": "2026-08-16T06:00:00+09:00",
            "last_heartbeat_at": "2026-08-16T06:10:00+09:00",
            "stale_after_seconds": 7200,
            "canonical_output": False,
        }]
        shadow = [{
            **authority[0],
            "exact_target_commit": authority[0]["exact_base_commit"],
            "branch_context": authority[0]["branch"],
            "started_at": "2026-08-15T21:00:00+00:00",
            "last_heartbeat_at": "2026-08-15T21:10:00Z",
        }]
        reader = ShadowOperationalStateReader(StaticReader(authority), StaticReader(shadow))
        rows = reader.list_runs()
        self.assertEqual(rows, tuple(authority))

    def test_shadow_mismatch_never_auto_selects_a_winner(self):
        authority = [{
            "run_id": "RUN-1",
            "state": "DISPATCHED_AWAITING_ACK",
            "exact_base_commit": "a" * 40,
            "branch": "aaa-t18-operational-db-v0.1",
        }]
        shadow = [{
            "run_id": "RUN-1",
            "state": "RUNNING_CONFIRMED",
            "exact_target_commit": "a" * 40,
            "branch_context": "aaa-t18-operational-db-v0.1",
        }]
        report = reconcile_run_rows(authority, shadow)
        self.assertEqual(report.status, "MISMATCH")
        self.assertEqual(report.mismatched_run_ids, ("RUN-1",))
        with self.assertRaisesRegex(ShadowReconciliationError, "SHADOW_RUN_REGISTRY_MISMATCH"):
            ShadowOperationalStateReader(StaticReader(authority), StaticReader(shadow)).list_runs()

    def test_duplicate_shadow_rows_fail_closed_instead_of_last_write_wins(self):
        authority = [{"run_id": "RUN-1", "state": "BLOCKED"}]
        shadow = [
            {"run_id": "RUN-1", "state": "BLOCKED"},
            {"run_id": "RUN-1", "state": "BLOCKED"},
        ]
        with self.assertRaisesRegex(ShadowReconciliationError, "DUPLICATE_RUN_ID_FOR_RECONCILIATION"):
            reconcile_run_rows(authority, shadow)

    def test_repository_json_registry_can_be_inventoried_without_mutation(self):
        reader = JsonRunRegistryReader(REPO_ROOT)
        rows = reader.list_runs()
        self.assertGreaterEqual(len(rows), 1)
        inventory = inventory_json_run_registry(REPO_ROOT)
        self.assertEqual(len(rows), len(inventory))
        self.assertEqual(
            {row["run_id"] for row in rows},
            {item.run_id for item in inventory},
        )
        for row in rows:
            self.assertRegex(str(row["_source_sha256"]), r"^[0-9a-f]{64}$")
            self.assertGreater(int(row["_source_byte_size"]), 0)

    def test_import_and_reconcile_tools_are_standard_library_and_fail_closed(self):
        importer = (REPO_ROOT / "aaa" / "db" / "tools" / "json_registry_to_sql.py").read_text(encoding="utf-8")
        reconciler = (REPO_ROOT / "aaa" / "db" / "tools" / "reconcile_shadow_export.py").read_text(encoding="utf-8")
        self.assertIn("load_run_registry", importer)
        self.assertIn("RESULT_SHA256_MISMATCH", importer)
        self.assertIn("source_json_sha256", reconciler)
        self.assertIn("T18_JSON_POSTGRES_RECONCILIATION_MISMATCH", reconciler)
        for forbidden in ("psycopg", "sqlalchemy", "redis", "kafka"):
            self.assertNotIn(forbidden, importer.lower())
            self.assertNotIn(forbidden, reconciler.lower())


if __name__ == "__main__":
    unittest.main()
