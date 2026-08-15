from __future__ import annotations

from pathlib import Path
import sys
import unittest

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC = REPO_ROOT / "aaa" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aaa.ops.operational_service import (
    OperationalAuthorityMode,
    OperationalBackendUnavailable,
    OperationalReadService,
)
from aaa.ops.run_registry import list_runs, persona_overview


class StaticProjection:
    def __init__(self, runs, personas=()):
        self._runs = tuple(runs)
        self._personas = tuple(personas)

    def list_runs(self):
        return self._runs

    def persona_overview(self):
        return self._personas


class ExplodingProjection:
    def list_runs(self):
        raise ConnectionError("postgres unavailable")

    def persona_overview(self):
        raise ConnectionError("postgres unavailable")


class T18CommonReadPathTests(unittest.TestCase):
    def test_json_authority_mode_preserves_existing_run_and_persona_projection(self):
        service = OperationalReadService(REPO_ROOT)
        self.assertEqual(service.runs(), list_runs(REPO_ROOT))
        self.assertEqual(service.personas(), persona_overview(REPO_ROOT))

    def test_postgres_authority_without_backend_fails_closed_no_json_fallback(self):
        service = OperationalReadService(
            REPO_ROOT,
            mode=OperationalAuthorityMode.POSTGRES_AUTHORITATIVE,
        )
        with self.assertRaisesRegex(
            OperationalBackendUnavailable,
            "POSTGRES_OPERATIONAL_BACKEND_UNAVAILABLE",
        ):
            service.runs()
        with self.assertRaisesRegex(
            OperationalBackendUnavailable,
            "POSTGRES_OPERATIONAL_BACKEND_UNAVAILABLE",
        ):
            service.personas()

    def test_postgres_authority_backend_failure_does_not_fallback_to_json(self):
        service = OperationalReadService(
            REPO_ROOT,
            mode=OperationalAuthorityMode.POSTGRES_AUTHORITATIVE,
            postgres_reader=ExplodingProjection(),
        )
        with self.assertRaisesRegex(
            OperationalBackendUnavailable,
            "POSTGRES_OPERATIONAL_READ_FAILED",
        ):
            service.runs()
        with self.assertRaisesRegex(
            OperationalBackendUnavailable,
            "POSTGRES_PERSONA_PROJECTION_FAILED",
        ):
            service.personas()

    def test_shadow_database_must_match_before_json_is_served(self):
        authority = list_runs(REPO_ROOT)
        shadow = [dict(row) for row in authority]
        service = OperationalReadService(
            REPO_ROOT,
            shadow_reader=StaticProjection(shadow),
        )
        self.assertEqual(service.runs(), authority)

        shadow[0]["state"] = "RUNNING_CONFIRMED"
        mismatch = OperationalReadService(
            REPO_ROOT,
            shadow_reader=StaticProjection(shadow),
        )
        with self.assertRaisesRegex(Exception, "SHADOW_RUN_REGISTRY_MISMATCH"):
            mismatch.runs()

    def test_cli_and_http_use_common_operational_service_not_direct_registry(self):
        cli = (REPO_ROOT / "aaa" / "src" / "aaa" / "cli" / "main.py").read_text(encoding="utf-8")
        server = (REPO_ROOT / "aaa" / "src" / "aaa" / "api" / "server.py").read_text(encoding="utf-8")
        self.assertIn("from aaa.ops.operational_service import OperationalReadService", cli)
        self.assertIn("from aaa.ops.operational_service import OperationalReadService", server)
        self.assertNotIn("from aaa.ops.run_registry import list_runs", cli)
        self.assertNotIn("from aaa.ops.run_registry import list_runs", server)
        self.assertNotIn("psycopg", cli.lower())
        self.assertNotIn("psycopg", server.lower())


if __name__ == "__main__":
    unittest.main()
