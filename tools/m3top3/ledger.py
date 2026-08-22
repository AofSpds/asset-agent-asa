from __future__ import annotations

import json
import fcntl
import os
import uuid
from pathlib import Path
from typing import Any

from .admission import EXIT_INTEGRITY, M3Top3AdmissionError
from .core import atomic_write_text, canonical_json_bytes, deterministic_id


class AppendOnlyLedger:
    def __init__(self, path: str | Path, id_field: str):
        self.path = Path(path)
        self.id_field = id_field
        self._existing: dict[str, bytes] = self._read_existing()

    @property
    def _lock_path(self)->Path:
        return self.path.with_name(f".{self.path.name}.lock")

    def _read_existing(self)->dict[str,bytes]:
        existing:dict[str,bytes]={}
        if not self.path.exists(): return existing
        try:
            for line_number,line in enumerate(self.path.read_text(encoding="utf-8").splitlines(),1):
                if not line.strip(): continue
                row=json.loads(line)
                if not isinstance(row,dict) or self.id_field not in row:
                    raise TypeError("ledger row is not an object with the required identity")
                rid=str(row[self.id_field]); payload=canonical_json_bytes(row); prior=existing.get(rid)
                if prior is not None and prior!=payload:
                    raise ValueError("ledger contains a conflicting duplicate identity")
                existing[rid]=payload
        except (OSError,UnicodeError,json.JSONDecodeError,KeyError,TypeError,ValueError) as exc:
            raise M3Top3AdmissionError("BLOCKED_INPUT_INTEGRITY","ledger bytes are unreadable, malformed, or conflicting",{"path":str(self.path),"line":locals().get("line_number"),"cause":type(exc).__name__},EXIT_INTEGRITY) from exc
        return existing

    def append(self, row: dict[str, Any]) -> str:
        return self.append_many([row])[0]

    def append_many(self,rows:list[dict[str,Any]])->list[str]:
        prepared=[(str(row[self.id_field]),canonical_json_bytes(row)) for row in rows]
        if len({rid for rid,_ in prepared})!=len(prepared):
            raise M3Top3AdmissionError("NONDETERMINISTIC_RERUN","append batch contains a duplicate immutable identity",{"id_field":self.id_field},EXIT_INTEGRITY)
        if not prepared: return []
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._lock_path.open("a+b") as lock:
            fcntl.flock(lock.fileno(),fcntl.LOCK_EX)
            live=self._read_existing(); states=[]; additions=[]
            for rid,payload in prepared:
                prior=live.get(rid)
                if prior is not None and prior!=payload:
                    raise M3Top3AdmissionError("NONDETERMINISTIC_RERUN",f"immutable ledger collision for {self.id_field}={rid}",{"path":str(self.path),"id_field":self.id_field,"identity":rid},EXIT_INTEGRITY)
                states.append("REUSED" if prior is not None else "APPENDED")
                if prior is None: additions.append((rid,payload))
            if additions:
                with self.path.open("ab") as handle:
                    handle.write(b"".join(payload+b"\n" for _,payload in additions)); handle.flush(); os.fsync(handle.fileno())
                live.update(additions)
            self._existing=live
            return states

    def check(self, row: dict[str, Any]) -> str:
        rid = str(row[self.id_field])
        payload = canonical_json_bytes(row)
        self.path.parent.mkdir(parents=True,exist_ok=True)
        with self._lock_path.open("a+b") as lock:
            fcntl.flock(lock.fileno(),fcntl.LOCK_SH)
            self._existing=self._read_existing()
        prior = self._existing.get(rid)
        if prior is None:
            return "APPENDABLE"
        if prior != payload:
            raise M3Top3AdmissionError("NONDETERMINISTIC_RERUN",f"immutable ledger collision for {self.id_field}={rid}",{"path":str(self.path),"id_field":self.id_field,"identity":rid},EXIT_INTEGRITY)
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
        candidate=self.path.with_name(f".{self.path.name}.{uuid.uuid4().hex}.candidate")
        atomic_write_text(candidate,payload.decode("utf-8"))
        try:
            os.link(candidate,self.path)
        except FileExistsError:
            prior=self.path.read_bytes()
            if prior!=payload:
                raise M3Top3AdmissionError(
                    "NONDETERMINISTIC_RERUN",
                    "concurrent run identity has different result bytes",
                    {"path":str(self.path)},
                    EXIT_INTEGRITY,
                )
            return "REUSED"
        finally:
            try: candidate.unlink()
            except FileNotFoundError: pass
        return "APPENDED"
