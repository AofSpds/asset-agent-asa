from __future__ import annotations

from http.client import HTTPConnection
import json
from pathlib import Path
import sys
import threading
import unittest

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "aaa" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aaa.api.server import build_server


class StateCompareHTTPTests(unittest.TestCase):
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

    def request(self, method: str) -> tuple[int, object]:
        connection = HTTPConnection("127.0.0.1", self.port, timeout=3)
        connection.request(method, "/api/aaa/state/compare")
        response = connection.getresponse()
        raw = response.read()
        payload = json.loads(raw.decode("utf-8")) if raw else None
        status = response.status
        connection.close()
        return status, payload

    def test_get_state_compare_returns_match_without_llm(self) -> None:
        status, payload = self.request("GET")
        self.assertEqual(status, 200)
        self.assertEqual(payload["status"], "MATCH")
        self.assertEqual(payload["canonical_authority"], "EXISTING_SEMI_CONTROL_PLANE")
        self.assertEqual(payload["event_ledger"]["latest_event_id"], "EVT-VALIDATION-0005")

    def test_state_compare_mutation_is_denied(self) -> None:
        status, payload = self.request("POST")
        self.assertEqual(status, 405)
        self.assertEqual(payload["error"], "READ_ONLY_API_MUTATION_PROHIBITED")


if __name__ == "__main__":
    unittest.main()
