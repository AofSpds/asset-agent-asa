from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any, Mapping


def canonical_json_bytes(value: Any) -> bytes:
    """Return stable UTF-8 JSON bytes for hashing and identity checks."""
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def content_sha256(value: Any) -> str:
    return sha256_hex(canonical_json_bytes(value))


@dataclass(frozen=True)
class ExactBaseIdentity:
    repository: str
    commit_sha: str

    def __post_init__(self) -> None:
        if len(self.commit_sha) != 40 or any(c not in "0123456789abcdef" for c in self.commit_sha):
            raise ValueError("commit_sha must be a lowercase 40-character Git SHA")


def assert_exact_base(expected: ExactBaseIdentity, observed: ExactBaseIdentity) -> None:
    if expected != observed:
        raise RuntimeError(
            f"STALE_BASE: expected {expected.repository}@{expected.commit_sha}, "
            f"observed {observed.repository}@{observed.commit_sha}"
        )


def immutable_identity(record: Mapping[str, Any], identity_fields: tuple[str, ...]) -> str:
    missing = [field for field in identity_fields if field not in record]
    if missing:
        raise KeyError(f"missing identity fields: {', '.join(missing)}")
    material = {field: record[field] for field in identity_fields}
    return content_sha256(material)
