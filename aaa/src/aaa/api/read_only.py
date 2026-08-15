from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import re
from typing import Any

from aaa.core.identity import sha256_hex


_VERSION_RE = re.compile(r"SEMI-CURRENT-STATE_v(\d+)\.(\d+)\.yaml$")


@dataclass(frozen=True)
class FileIdentity:
    path: str
    sha256: str
    byte_size: int


def _read_bytes(path: Path) -> bytes:
    return path.read_bytes()


def file_identity(path: Path, repo_root: Path) -> FileIdentity:
    data = _read_bytes(path)
    return FileIdentity(
        path=str(path.relative_to(repo_root)),
        sha256=sha256_hex(data),
        byte_size=len(data),
    )


def _latest_current_state(repo_root: Path) -> Path:
    root = repo_root / "control" / "continuity" / "v1.0"
    candidates: list[tuple[tuple[int, int], Path]] = []
    for path in root.glob("SEMI-CURRENT-STATE_v*.yaml"):
        match = _VERSION_RE.search(path.name)
        if match:
            candidates.append(((int(match.group(1)), int(match.group(2))), path))
    if not candidates:
        raise FileNotFoundError("NO_CURRENT_STATE_FOUND")
    return max(candidates, key=lambda item: item[0])[1]


def _top_level_scalar(text: str, key: str) -> str | None:
    prefix = f"{key}:"
    for raw_line in text.splitlines():
        if raw_line.startswith(" ") or raw_line.startswith("\t"):
            continue
        if raw_line.startswith(prefix):
            return raw_line[len(prefix):].strip().strip("'\"") or None
    return None


def build_status(repo_root: Path) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    state_path = _latest_current_state(repo_root)
    state_text = state_path.read_text(encoding="utf-8")
    identity = file_identity(state_path, repo_root)
    return {
        "project": "Asset Agent ASA",
        "short_name": "AAA",
        "repository": "AofSpds/asset-agent-asa",
        "aaa_role": "SHADOW_NONAUTHORITATIVE",
        "canonical_authority": "EXISTING_SEMI_CONTROL_PLANE",
        "llm_required_for_control_plane": False,
        "current_state": {
            "version": _top_level_scalar(state_text, "version"),
            "status": _top_level_scalar(state_text, "status"),
            "identity": asdict(identity),
        },
    }


def list_work_orders(repo_root: Path) -> list[dict[str, Any]]:
    root = repo_root.resolve() / "control" / "workorders"
    if not root.exists():
        return []
    rows: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*.yaml")):
        data = path.read_bytes()
        rows.append(
            {
                "path": str(path.relative_to(repo_root.resolve())),
                "sha256": sha256_hex(data),
                "byte_size": len(data),
            }
        )
    return rows


def verify_asset(repo_root: Path, relative_path: str) -> dict[str, Any]:
    root = repo_root.resolve()
    path = (root / relative_path).resolve()
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise ValueError("ASSET_PATH_ESCAPES_REPOSITORY") from exc
    if not path.is_file():
        raise FileNotFoundError(relative_path)
    return {"verified": True, **asdict(file_identity(path, root))}


def list_validation_gates(repo_root: Path) -> list[str]:
    path = repo_root.resolve() / "control" / "aaa" / "v0.1" / "AAA-BUILD-CONTRACT_v0.1_WORKING.yaml"
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    gates: list[str] = []
    in_block = False
    for line in lines:
        if line == "validation_gates:":
            in_block = True
            continue
        if in_block:
            if line.startswith("  - "):
                gates.append(line[4:].strip())
                continue
            if line and not line.startswith(" "):
                break
    return gates
