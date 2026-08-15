from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "aaa" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aaa.ops.run_registry import list_runs


class RunRegistryP09CompatibilityTests(unittest.TestCase):
    def test_validation_run_id_result_identity_is_physically_verified(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            work_order_id = "WO-VALIDATION-TEST"
            run_id = "RUN-VALIDATION-TEST"
            exact_target = "a" * 40

            workorders = root / "control" / "workorders"
            workorders.mkdir(parents=True)
            (workorders / "validation.yaml").write_text(
                f"work_order_id: {work_order_id}\nstatus: TEST\n",
                encoding="utf-8",
            )

            result_payload = {
                "result_id": "RESULT-VALIDATION-TEST",
                "validation_run_id": run_id,
                "work_order_id": work_order_id,
                "verdict": "FAIL",
                "repository": "AofSpds/asset-agent-asa",
                "exact_validation_target": exact_target,
            }
            result_bytes = (json.dumps(result_payload, indent=2) + "\n").encode("utf-8")
            results = root / "control" / "aaa" / "results"
            results.mkdir(parents=True)
            result_path = results / "RESULT-VALIDATION-TEST.json"
            result_path.write_bytes(result_bytes)

            run_payload = {
                "run_id": run_id,
                "process_id": "P09-INDEPENDENT-VALIDATION",
                "work_order_id": work_order_id,
                "responsible_persona": "SEMI-VALIDATION-AUDITOR",
                "executor_role": "PREVALIDATION_CHECK",
                "state": "COMPLETED_FAIL",
                "repository": "AofSpds/asset-agent-asa",
                "exact_base_commit": exact_target,
                "branch": "aaa-test",
                "started_at": "2026-08-16T06:10:00+09:00",
                "last_heartbeat_at": None,
                "stale_after_seconds": 7200,
                "canonical_output": False,
                "terminal_result": {
                    "result_id": "RESULT-VALIDATION-TEST",
                    "result_sha256": hashlib.sha256(result_bytes).hexdigest(),
                    "completed_at": "2026-08-16T06:14:00+09:00",
                    "persistent_locator": "control/aaa/results/RESULT-VALIDATION-TEST.json",
                    "verdict": "FAIL",
                },
            }
            runs = root / "control" / "aaa" / "runs"
            runs.mkdir(parents=True)
            (runs / "run.json").write_text(json.dumps(run_payload), encoding="utf-8")

            rows = list_runs(root, datetime(2026, 8, 16, 0, 0, tzinfo=timezone.utc))
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["run_id"], run_id)
            self.assertEqual(rows[0]["effective_state"], "COMPLETED_FAIL")
            self.assertEqual(rows[0]["terminal_result"]["verdict"], "FAIL")


if __name__ == "__main__":
    unittest.main()
