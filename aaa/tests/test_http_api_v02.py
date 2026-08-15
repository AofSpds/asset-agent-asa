from __future__ import annotations

from http.client import HTTPConnection
import json
from pathlib import Path
import sys
import threading
import unittest
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "aaa" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aaa.api.server import build_server


class ReadOnlyHTTPAPITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.server = build_server(ROOT, host="127.0.0.1", port=0)
        cls.port = int(cls.server.server_address[1])
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def request(self, method: str, path: str, headers: dict[str, str] | None = None) -> tuple[int, dict[str, str], object]:
        connection = HTTPConnection("127.0.0.1", self.port, timeout=3)
        connection.request(method, path, headers=headers or {})
        response = connection.getresponse()
        raw = response.read()
        response_headers = {key: value for key, value in response.getheaders()}
        payload = json.loads(raw.decode("utf-8")) if raw else None
        status = response.status
        connection.close()
        return status, response_headers, payload

    def test_health_and_status_are_llm_independent_read_only(self) -> None:
        status, _, health = self.request("GET", "/api/aaa/health")
        self.assertEqual(status, 200)
        self.assertEqual(health, {"llm_required": False, "mode": "READ_ONLY", "status": "OK"})

        status, _, payload = self.request("GET", "/api/aaa/status")
        self.assertEqual(status, 200)
        self.assertEqual(payload["repository"], "AofSpds/asset-agent-asa")
        self.assertEqual(payload["canonical_authority"], "EXISTING_SEMI_CONTROL_PLANE")
        self.assertFalse(payload["llm_required_for_control_plane"])
        self.assertTrue(payload["current_state"]["version"])

    def test_work_and_gate_endpoints_are_read_only_views(self) -> None:
        status, _, work = self.request("GET", "/api/aaa/work")
        self.assertEqual(status, 200)
        self.assertIsInstance(work["items"], list)
        self.assertGreater(len(work["items"]), 0)

        status, _, gates = self.request("GET", "/api/aaa/gates")
        self.assertEqual(status, 200)
        self.assertIn("LLM_OFF_PASS", gates["items"])

    def test_mutation_methods_are_denied(self) -> None:
        for method in ("POST", "PUT", "PATCH", "DELETE"):
            with self.subTest(method=method):
                status, _, payload = self.request(method, "/api/aaa/status")
                self.assertEqual(status, 405)
                self.assertEqual(payload["error"], "READ_ONLY_API_MUTATION_PROHIBITED")

    def test_asset_verify_rejects_repository_escape(self) -> None:
        escaped = quote("../README.md", safe="")
        status, _, payload = self.request("GET", f"/api/aaa/asset/verify?path={escaped}")
        self.assertEqual(status, 400)
        self.assertIn("ASSET_PATH_ESCAPES_REPOSITORY", payload["detail"])

    def test_local_owner_console_cors_is_allowlisted(self) -> None:
        for origin in ("http://127.0.0.1:5173", "http://localhost:5173"):
            with self.subTest(origin=origin):
                status, headers, _ = self.request("GET", "/api/aaa/health", {"Origin": origin})
                self.assertEqual(status, 200)
                self.assertEqual(headers.get("Access-Control-Allow-Origin"), origin)

        status, headers, _ = self.request("GET", "/api/aaa/health", {"Origin": "https://example.com"})
        self.assertEqual(status, 200)
        self.assertNotIn("Access-Control-Allow-Origin", headers)


if __name__ == "__main__":
    unittest.main()
