from __future__ import annotations

from dataclasses import dataclass
import hashlib


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@dataclass(frozen=True)
class ContentIdentity:
    sha256: str
    byte_size: int

    @classmethod
    def from_bytes(cls, data: bytes) -> "ContentIdentity":
        return cls(sha256=sha256_bytes(data), byte_size=len(data))


@dataclass(frozen=True)
class StagingObject:
    run_id: str
    key: str
    identity: ContentIdentity


def build_run_scoped_key(run_id: str, relative_key: str) -> str:
    if not run_id or "/" in run_id:
        raise ValueError("run_id must be a non-empty path-safe identifier")
    relative = relative_key.strip("/")
    if not relative or ".." in relative.split("/"):
        raise ValueError("relative_key must remain inside the run-scoped staging namespace")
    return f"staging/{run_id}/{relative}"


def assert_same_key_identity(existing: ContentIdentity, incoming: ContentIdentity) -> None:
    if existing != incoming:
        raise RuntimeError("SAME_KEY_DIFFERENT_HASH_HARD_FAIL")


def release_complete(primary_ok: bool, secondary_ok: bool) -> bool:
    """Primary success with secondary failure is never a complete release."""
    return primary_ok and secondary_ok
