from __future__ import annotations

from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from aaa.api.read_only import build_status, list_validation_gates, list_work_orders, verify_asset


class AAAReadOnlyHandler(BaseHTTPRequestHandler):
    repo_root = Path(".")

    def _json(self, payload: object, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
        self.send_response(status.value)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "http://127.0.0.1:5173")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
        parsed = urlparse(self.path)
        try:
            if parsed.path == "/api/aaa/health":
                self._json({"status": "OK", "mode": "READ_ONLY", "llm_required": False})
                return
            if parsed.path == "/api/aaa/status":
                self._json(build_status(self.repo_root))
                return
            if parsed.path == "/api/aaa/work":
                self._json({"items": list_work_orders(self.repo_root)})
                return
            if parsed.path == "/api/aaa/gates":
                self._json({"items": list_validation_gates(self.repo_root)})
                return
            if parsed.path == "/api/aaa/asset/verify":
                query = parse_qs(parsed.query)
                relative_path = (query.get("path") or [""])[0]
                if not relative_path:
                    self._json({"error": "MISSING_PATH"}, HTTPStatus.BAD_REQUEST)
                    return
                self._json(verify_asset(self.repo_root, relative_path))
                return
            self._json({"error": "NOT_FOUND"}, HTTPStatus.NOT_FOUND)
        except (FileNotFoundError, ValueError) as exc:
            self._json({"error": type(exc).__name__, "detail": str(exc)}, HTTPStatus.BAD_REQUEST)
        except Exception as exc:  # fail closed; do not expose mutation surface
            self._json({"error": "READ_ONLY_API_FAILURE", "detail": str(exc)}, HTTPStatus.INTERNAL_SERVER_ERROR)

    def do_POST(self) -> None:  # noqa: N802 - explicit mutation denial
        self._json({"error": "READ_ONLY_API_MUTATION_PROHIBITED"}, HTTPStatus.METHOD_NOT_ALLOWED)

    do_PUT = do_POST
    do_PATCH = do_POST
    do_DELETE = do_POST

    def log_message(self, format: str, *args: object) -> None:
        return


def serve(repo_root: Path, host: str = "127.0.0.1", port: int = 8765) -> None:
    handler = type("BoundAAAReadOnlyHandler", (AAAReadOnlyHandler,), {"repo_root": repo_root.resolve()})
    server = ThreadingHTTPServer((host, port), handler)
    print(f"AAA read-only API listening on http://{host}:{port}")
    server.serve_forever()
