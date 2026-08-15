from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import socket

from aaa.execution.contracts import ExecutionContractError, WorkerIdentity
from aaa.execution.profiles import VALIDATION_EXACT_GIT_V0_1, list_execution_profiles
from aaa.execution.psql_backend import PsqlExecutionBackend
from aaa.execution.worker import WorkerRuntime


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m aaa.execution", description="AAA T19 bounded engineering worker runtime")
    sub = parser.add_subparsers(dest="command", required=True)
    profiles = sub.add_parser("profiles", help="list code-owned allowlisted execution profiles")
    profiles.add_argument("--json", action="store_true", dest="as_json")
    run_once = sub.add_parser("run-once", help="claim and execute at most one bounded task")
    run_once.add_argument("--database", required=True)
    run_once.add_argument("--worker-id", required=True)
    run_once.add_argument("--worker-type", default="CI_VALIDATION_WORKER")
    run_once.add_argument("--host-identity", default=socket.gethostname())
    run_once.add_argument("--repo-root", default=".")
    run_once.add_argument("--output-dir", default=".aaa/t19/results")
    run_once.add_argument("--lease-ttl-seconds", type=int, default=300)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "profiles":
        payload = list_execution_profiles()
        if args.as_json:
            print(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2))
        else:
            for item in payload:
                print(f"{item['execution_profile_id']} {item['profile_sha256']}")
        return 0
    if os.environ.get("AAA_T19_ENGINEERING_EXECUTION_ENABLED") != "1":
        raise ExecutionContractError("T19_ENGINEERING_EXECUTION_NOT_ENABLED")
    worker = WorkerIdentity(worker_id=args.worker_id, worker_type=args.worker_type, runtime_version="v0.1", host_identity=args.host_identity, capabilities=("INDEPENDENT_VALIDATION",), authorized_personas=("SEMI-VALIDATION-AUDITOR",), permission_level=1, max_concurrency=1)
    backend = PsqlExecutionBackend(database=args.database, lease_ttl_seconds=args.lease_ttl_seconds)
    backend.register_worker(worker)
    backend.register_profile(VALIDATION_EXACT_GIT_V0_1, git_identity="AAA_T19_CODE_OWNED_PROFILE_V0_1")
    runtime = WorkerRuntime(worker=worker, backend=backend, repo_root=Path(args.repo_root), output_dir=Path(args.output_dir), lease_ttl_seconds=args.lease_ttl_seconds)
    print(json.dumps(runtime.run_once(), ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
