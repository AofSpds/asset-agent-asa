from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .admission import EXIT_INTEGRITY, M3Top3AdmissionError
from .core import atomic_write_text, canonical_json_bytes, deterministic_id


class AppendOnlyLedger:
    def __init__(self, path: str | Path, id_field: str):
        self.path = Path(path)
        self.id_field = id_field
        self._existing: dict[str, bytes] = {}
        if self.path.exists():
            for line in self.path.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                row = json.loads(line)
                self._existing[str(row[self.id_field])] = canonical_json_bytes(row)

    def append(self, row: dict[str, Any]) -> str:
        state = self.check(row)
        if state == "REUSED":
            return state
        rid = str(row[self.id_field])
        payload = canonical_json_bytes(row)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(payload.decode("utf-8") + "\n")
        self._existing[rid] = payload
        return "APPENDED"

    def check(self, row: dict[str, Any]) -> str:
        rid = str(row[self.id_field])
        payload = canonical_json_bytes(row)
        prior = self._existing.get(rid)
        if prior is None:
            return "APPENDABLE"
        if prior != payload:
            raise ValueError(f"immutable ledger collision for {self.id_field}={rid}")
        return "REUSED"


class PredictionLedger(AppendOnlyLedger):
    def __init__(self, path: str | Path):
        super().__init__(path, "prediction_id")

    @staticmethod
    def build_record(ranked: dict[str, Any], predicted_at: str, input_hash: str, status: str = "EXPERIMENTAL") -> dict[str, Any]:
        identity = {
            "pit_snapshot_id": ranked["pit_snapshot_id"],
            "model_version": ranked["model_version"],
            "company_id": ranked["company_id"],
            "rank": ranked["rank"],
        }
        return {
            "prediction_id": deterministic_id("pred", identity),
            "pit_snapshot_id": ranked["pit_snapshot_id"],
            "model_score_id": ranked.get("model_score_id"),
            "model_version": ranked["model_version"],
            "company_id": ranked["company_id"],
            "security_code": ranked["security_code"],
            "rank": ranked["rank"],
            "score": ranked["raw_score"],
            "selected": ranked["selected_top3"],
            "predicted_at": predicted_at,
            "input_hash": input_hash,
            "status": status,
        }


class ImmutableJsonArtifactStore:
    """Create-once JSON result storage with deterministic byte reuse."""

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def admit(self, row: dict[str, Any]) -> str:
        payload = canonical_json_bytes(row) + b"\n"
        if self.path.exists():
            prior = self.path.read_bytes()
            if prior != payload:
                raise M3Top3AdmissionError(
                    "NONDETERMINISTIC_RERUN",
                    "existing run identity has different result bytes",
                    {"path": str(self.path)},
                    EXIT_INTEGRITY,
                )
            return "REUSED"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        atomic_write_text(self.path, payload.decode("utf-8"))
        return "APPENDED"
