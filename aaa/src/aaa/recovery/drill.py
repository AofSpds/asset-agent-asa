from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any

from aaa.agents.journal import AgentRunJournal, JournalIntegrityError
from aaa.core.identity import content_sha256, file_identity
from aaa.recovery.audit import ArtifactRecoveryObservation
from aaa.storage.identity import ContentIdentity


@dataclass(frozen=True)
class WorkerHandle:
    pid: int
    run_dir: str
    marker_path: str
    result_path: str


@dataclass(frozen=True)
class LockInspection:
    path: str
    status: str
    pid: int | None


@dataclass(frozen=True)
class JournalInspection:
    path: str
    status: str
    event_count: int
    detail: str | None = None


@dataclass(frozen=True)
class DrillEvidence:
    drill_type: str
    status: str
    evidence: dict[str, Any]
    canonical_mutation: bool = False
    real_cloud_infrastructure_exercised: bool = False

    @property
    def sha256(self) -> str:
        return content_sha256(asdict(self))


def process_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def start_interruptible_worker(run_dir: Path, *, timeout_seconds: int = 60) -> tuple[subprocess.Popen[bytes], WorkerHandle]:
    """Start a local worker that records RUNNING then waits before writing success.

    The caller can terminate it to test that an interrupted process never creates
    a success result. This is a local engineering drill, not a cloud/S3/R2 drill.
    """
    run_dir.mkdir(parents=True, exist_ok=True)
    marker = run_dir / "worker.marker"
    result = run_dir / "worker.result.json"
    script = (
        "import json,sys,time,pathlib;"
        "marker=pathlib.Path(sys.argv[1]);result=pathlib.Path(sys.argv[2]);"
        "marker.write_text('RUNNING',encoding='utf-8');"
        "time.sleep(float(sys.argv[3]));"
        "result.write_text(json.dumps({'status':'SUCCEEDED'}),encoding='utf-8')"
    )
    proc = subprocess.Popen(
        [sys.executable, "-c", script, str(marker), str(result), str(timeout_seconds)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    deadline = time.monotonic() + 5.0
    while not marker.exists() and proc.poll() is None and time.monotonic() < deadline:
        time.sleep(0.01)
    if not marker.exists():
        proc.kill()
        proc.wait(timeout=5)
        raise RuntimeError("WORKER_DID_NOT_REACH_RUNNING_MARKER")
    return proc, WorkerHandle(proc.pid, str(run_dir), str(marker), str(result))


def interrupt_worker(proc: subprocess.Popen[bytes], handle: WorkerHandle) -> DrillEvidence:
    if proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)
    result_exists = Path(handle.result_path).exists()
    evidence = {
        "pid": handle.pid,
        "returncode": proc.returncode,
        "running_marker_exists": Path(handle.marker_path).exists(),
        "success_result_exists": result_exists,
    }
    return DrillEvidence(
        drill_type="LOCAL_PROCESS_INTERRUPTION",
        status="PASS" if not result_exists else "FAIL_SUCCESS_RESULT_EXISTED_AFTER_INTERRUPT",
        evidence=evidence,
    )


def inspect_lock(lock_path: Path) -> LockInspection:
    if not lock_path.exists():
        return LockInspection(str(lock_path), "MISSING", None)
    try:
        pid = int(lock_path.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        return LockInspection(str(lock_path), "INVALID", None)
    return LockInspection(str(lock_path), "ACTIVE" if process_alive(pid) else "STALE", pid)


def quarantine_stale_lock(lock_path: Path) -> Path:
    inspection = inspect_lock(lock_path)
    if inspection.status != "STALE":
        raise RuntimeError(f"LOCK_NOT_STALE:{inspection.status}")
    destination = lock_path.with_suffix(lock_path.suffix + ".stale")
    if destination.exists():
        raise FileExistsError(f"STALE_LOCK_QUARANTINE_EXISTS:{destination}")
    lock_path.replace(destination)
    return destination


def inspect_journal(journal_path: Path) -> JournalInspection:
    journal = AgentRunJournal(journal_path)
    try:
        events = journal.read_events()
    except (JournalIntegrityError, UnicodeDecodeError) as exc:
        return JournalInspection(str(journal_path), "BLOCKED_CORRUPT_OR_PARTIAL", 0, str(exc))
    return JournalInspection(str(journal_path), "PASS", len(events))


def observe_local_replicas(
    *,
    artifact_id: str,
    expected: ContentIdentity,
    primary_path: Path,
    secondary_path: Path,
) -> ArtifactRecoveryObservation:
    def observed(path: Path) -> ContentIdentity | None:
        if not path.is_file():
            return None
        identity = file_identity(path)
        return ContentIdentity(identity["sha256"], identity["byte_size"])

    primary = observed(primary_path)
    secondary = observed(secondary_path)
    return ArtifactRecoveryObservation(
        artifact_id=artifact_id,
        expected=expected,
        observed_primary=primary,
        observed_secondary=secondary,
        primary_available=primary is not None,
        secondary_available=secondary is not None,
    )


def evidence_manifest(*evidence: DrillEvidence) -> dict[str, Any]:
    material = {
        "scope": "LOCAL_ENGINEERING_RECOVERY_DRILL_ONLY",
        "real_cloud_infrastructure_exercised": False,
        "canonical_mutation": False,
        "items": [asdict(item) | {"sha256": item.sha256} for item in evidence],
    }
    material["manifest_sha256"] = content_sha256(material)
    return material
