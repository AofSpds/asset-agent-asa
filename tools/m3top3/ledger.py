from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .core import canonical_json_bytes, deterministic_id


class AppendOnlyLedger:
    def __init__(self, path: str | Path, id_field: str):
        self.path = Path(path)
        self.id_field = id_field
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._existing: dict[str, bytes] = {}
        if self.path.exists():
            for line in self.path.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                row = json.loads(line)
                self._existing[str(row[self.id_field])] = canonical_json_bytes(row)

    def append(self, row: dict[str, Any]) -> str:
        rid = str(row[self.id_field])
        payload = canonical_json_bytes(row)
        prior = self._existing.get(rid)
        if prior is not None:
            if prior != payload:
                raise ValueError(f"immutable ledger collision for {self.id_field}={rid}")
            return "REUSED"
        with self.path.open("a", encoding="utf-8") as f:
            f.write(payload.decode("utf-8") + "\n")
        self._existing[rid] = payload
        return "APPENDED"


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
