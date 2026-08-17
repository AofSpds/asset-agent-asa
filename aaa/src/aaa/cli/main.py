from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

from aaa.api.read_only import build_status, list_validation_gates, list_work_orders, verify_asset
from aaa.api.server import serve
from aaa.execution.psql_backend import PsqlExecutionBackend
from aaa.ops.operational_service import OperationalReadService
from aaa.state.discrepancy import build_discrepancy_report


def _emit(value: Any, as_json: bool) -> None:
    if as_json: print(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2)); return
    if isinstance(value, dict):
        for key, item in value.items(): print(f"{key}: {json.dumps(item, ensure_ascii=False, sort_keys=True) if isinstance(item, (dict, list)) else item}")
        return
    if isinstance(value, list):
        for item in value: print(json.dumps(item, ensure_ascii=False, sort_keys=True) if isinstance(item, dict) else item)
        return
    print(value)


def _operational_service(repo_root: Path) -> OperationalReadService:
    database = os.environ.get("AAA_POSTGRES_DB")
    execution_reader = PsqlExecutionBackend(database=database) if database else None
    return OperationalReadService(repo_root, execution_reader=execution_reader)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="aaa", description="Asset Agent ASA deterministic control interface")
    parser.add_argument("--repo-root", default=".")
    sub = parser.add_subparsers(dest="command", required=True)
    status = sub.add_parser("status"); status.add_argument("--json", action="store_true", dest="as_json")
    work = sub.add_parser("work"); work_sub = work.add_subparsers(dest="work_command", required=True); work_list = work_sub.add_parser("list"); work_list.add_argument("--json", action="store_true", dest="as_json")
    runs = sub.add_parser("runs"); runs.add_argument("--json", action="store_true", dest="as_json")
    personas = sub.add_parser("personas"); personas.add_argument("--json", action="store_true", dest="as_json")
    workers = sub.add_parser("workers", help="inspect connected T19 worker projection"); workers.add_argument("--json", action="store_true", dest="as_json")
    tasks = sub.add_parser("tasks", help="inspect connected T19 execution task projection"); tasks.add_argument("--json", action="store_true", dest="as_json")
    asset = sub.add_parser("asset"); asset_sub = asset.add_subparsers(dest="asset_command", required=True); asset_verify = asset_sub.add_parser("verify"); asset_verify.add_argument("path"); asset_verify.add_argument("--json", action="store_true", dest="as_json")
    gate = sub.add_parser("gate"); gate_sub = gate.add_subparsers(dest="gate_command", required=True); gate_list = gate_sub.add_parser("list"); gate_list.add_argument("--json", action="store_true", dest="as_json")
    state = sub.add_parser("state"); state_sub = state.add_subparsers(dest="state_command", required=True); state_compare = state_sub.add_parser("compare"); state_compare.add_argument("--json", action="store_true", dest="as_json")
    serve_parser = sub.add_parser("serve"); serve_parser.add_argument("--host", default="127.0.0.1"); serve_parser.add_argument("--port", type=int, default=8765)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser(); args = parser.parse_args(argv); repo_root = Path(args.repo_root); operational = _operational_service(repo_root)
    if args.command == "status": _emit(build_status(repo_root), args.as_json); return 0
    if args.command == "work" and args.work_command == "list": _emit(list_work_orders(repo_root), args.as_json); return 0
    if args.command == "runs": _emit(operational.runs(), args.as_json); return 0
    if args.command == "personas": _emit(operational.personas(), args.as_json); return 0
    if args.command == "workers": _emit(operational.workers(), args.as_json); return 0
    if args.command == "tasks": _emit(operational.tasks(), args.as_json); return 0
    if args.command == "asset" and args.asset_command == "verify": _emit(verify_asset(repo_root, args.path), args.as_json); return 0
    if args.command == "gate" and args.gate_command == "list": _emit(list_validation_gates(repo_root), args.as_json); return 0
    if args.command == "state" and args.state_command == "compare": _emit(build_discrepancy_report(repo_root), args.as_json); return 0
    if args.command == "serve": serve(repo_root, host=args.host, port=args.port); return 0
    parser.error("unsupported command"); return 2
