from __future__ import annotations

from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from aaa.api.operating_structure import build_operating_structure
from aaa.api.read_only import build_status, list_validation_gates, list_work_orders, verify_asset
from aaa.execution.psql_backend import PsqlExecutionBackend
from aaa.ops.operational_service import OperationalReadService
from aaa.state.discrepancy import build_discrepancy_report

_ALLOWED_ORIGINS = {"http://127.0.0.1:5173", "http://localhost:5173"}

def _operational_service(repo_root: Path) -> OperationalReadService:
    database = os.environ.get("AAA_POSTGRES_DB")
    execution_reader = PsqlExecutionBackend(database=database) if database else None
    return OperationalReadService(repo_root, execution_reader=execution_reader)

class AAAReadOnlyHandler(BaseHTTPRequestHandler):
    repo_root = Path(".")
    def _allowed_origin(self) -> str | None:
        origin = self.headers.get("Origin"); return origin if origin in _ALLOWED_ORIGINS else None
    def _json(self, payload: object, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8"); self.send_response(status.value); self.send_header("Content-Type", "application/json; charset=utf-8"); self.send_header("Content-Length", str(len(body))); self.send_header("Cache-Control", "no-store")
        allowed_origin = self._allowed_origin()
        if allowed_origin: self.send_header("Access-Control-Allow-Origin", allowed_origin); self.send_header("Vary", "Origin")
        self.end_headers(); self.wfile.write(body)
    def do_OPTIONS(self) -> None:
        self.send_response(HTTPStatus.NO_CONTENT.value); allowed_origin = self._allowed_origin()
        if allowed_origin: self.send_header("Access-Control-Allow-Origin", allowed_origin); self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS"); self.send_header("Access-Control-Allow-Headers", "Content-Type"); self.send_header("Vary", "Origin")
        self.end_headers()
    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        try:
            operational = _operational_service(self.repo_root)
            if parsed.path == "/api/aaa/health": self._json({"status": "OK", "mode": "READ_ONLY", "llm_required": False}); return
            if parsed.path == "/api/aaa/status": self._json(build_status(self.repo_root)); return
            if parsed.path == "/api/aaa/operating-structure": self._json(build_operating_structure(self.repo_root)); return
            if parsed.path == "/api/aaa/state/compare": self._json(build_discrepancy_report(self.repo_root)); return
            if parsed.path == "/api/aaa/work": self._json({"items": list_work_orders(self.repo_root)}); return
            if parsed.path == "/api/aaa/runs": self._json({"items": operational.runs()}); return
            if parsed.path == "/api/aaa/personas": self._json({"items": operational.personas()}); return
            if parsed.path == "/api/aaa/workers": self._json({"items": operational.workers(), "postgres_projection_connected": bool(os.environ.get("AAA_POSTGRES_DB"))}); return
            if parsed.path == "/api/aaa/tasks": self._json({"items": operational.tasks(), "postgres_projection_connected": bool(os.environ.get("AAA_POSTGRES_DB"))}); return
            if parsed.path == "/api/aaa/gates": self._json({"items": list_validation_gates(self.repo_root)}); return
            if parsed.path == "/api/aaa/asset/verify":
                query = parse_qs(parsed.query); relative_path = (query.get("path") or [""])[0]
                if not relative_path: self._json({"error": "MISSING_PATH"}, HTTPStatus.BAD_REQUEST); return
                self._json(verify_asset(self.repo_root, relative_path)); return
            self._json({"error": "NOT_FOUND"}, HTTPStatus.NOT_FOUND)
        except (FileNotFoundError, ValueError) as exc: self._json({"error": type(exc).__name__, "detail": str(exc)}, HTTPStatus.BAD_REQUEST)
        except Exception as exc: self._json({"error": "READ_ONLY_API_FAILURE", "detail": str(exc)}, HTTPStatus.INTERNAL_SERVER_ERROR)
    def do_POST(self) -> None: self._json({"error": "READ_ONLY_API_MUTATION_PROHIBITED"}, HTTPStatus.METHOD_NOT_ALLOWED)
    do_PUT = do_POST; do_PATCH = do_POST; do_DELETE = do_POST
    def log_message(self, format: str, *args: object) -> None: return

def build_server(repo_root: Path, host: str = "127.0.0.1", port: int = 8765) -> ThreadingHTTPServer:
    handler = type("BoundAAAReadOnlyHandler", (AAAReadOnlyHandler,), {"repo_root": repo_root.resolve()}); return ThreadingHTTPServer((host, port), handler)

def serve(repo_root: Path, host: str = "127.0.0.1", port: int = 8765) -> None:
    server = build_server(repo_root, host=host, port=port); print(f"AAA read-only API listening on http://{host}:{port}")
    try: server.serve_forever()
    finally: server.server_close()
