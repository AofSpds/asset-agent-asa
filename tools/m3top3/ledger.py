from __future__ import annotations

import json
import fcntl
import os
import uuid
import hashlib
from contextlib import contextmanager
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

    def preflight_many(self,rows:list[dict[str,Any]])->list[str]:
        """Check a complete batch without creating a ledger or lock path."""
        prepared=[(str(row[self.id_field]),canonical_json_bytes(row)) for row in rows]
        if len({rid for rid,_ in prepared})!=len(prepared):
            raise M3Top3AdmissionError("FULL_RANKING_LEDGER_INCOMPLETE","ledger batch contains duplicate immutable identities",{"id_field":self.id_field},EXIT_INTEGRITY)
        live=self._read_existing(); states=[]
        for rid,payload in prepared:
            prior=live.get(rid)
            if prior is not None and prior!=payload:
                raise M3Top3AdmissionError("NONDETERMINISTIC_RERUN",f"immutable ledger collision for {self.id_field}={rid}",{"path":str(self.path),"identity":rid},EXIT_INTEGRITY)
            states.append("REUSED" if prior is not None else "APPENDABLE")
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
    def build_record(ranked: dict[str, Any], predicted_at: str, input_hash: str, status: str = "EXPERIMENTAL", lineage_hash: str | None = None) -> dict[str, Any]:
        identity = {
            "pit_snapshot_id": ranked["pit_snapshot_id"],
            "model_version": ranked["model_version"],
            "company_id": ranked["company_id"],
            "rank": ranked["rank"],
            "denominator_member_id": ranked.get("denominator_member_id"),
            "lineage_hash": lineage_hash,
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
            "denominator_member_id": ranked.get("denominator_member_id"),
            "predicted_at": predicted_at,
            "input_hash": input_hash,
            "lineage_hash": lineage_hash,
            "status": status,
        }


def verify_prediction_batch_coverage(
    ranked: list[dict[str, Any]],
    records: list[dict[str, Any]],
    *,
    predicted_at: str,
    input_hash_by_pit: dict[str, str],
    status: str,
    lineage_hash: str,
) -> None:
    """Admit exactly one immutable prediction row for every ranked E member.

    This is deliberately a separate non-mutating verifier so callers can
    preflight the complete E batch before either the shared ledger or the
    full-run artifact set is touched.
    """

    expected_by_score:dict[str,dict[str,Any]]={}
    for row in ranked:
        try:
            expected=PredictionLedger.build_record(
                row,
                predicted_at,
                input_hash_by_pit[row["pit_snapshot_id"]],
                status=status,
                lineage_hash=lineage_hash,
            )
        except (KeyError,TypeError,ValueError) as exc:
            raise M3Top3AdmissionError(
                "FULL_RANKING_LEDGER_INCOMPLETE",
                "ranked E row lacks the exact publication envelope needed for prediction persistence",
                {"cause":type(exc).__name__},
                EXIT_INTEGRITY,
            ) from exc
        score_id=str(row.get("model_score_id"))
        if score_id in expected_by_score:
            raise M3Top3AdmissionError(
                "FULL_RANKING_LEDGER_INCOMPLETE",
                "ranked E input contains duplicate model-score identities",
                {"model_score_id":score_id},
                EXIT_INTEGRITY,
            )
        expected_by_score[score_id]=expected
    actual_ids=[record.get("prediction_id") for record in records if isinstance(record,dict)]
    actual_score_ids=[record.get("model_score_id") for record in records if isinstance(record,dict)]
    if (
        len(records)!=len(ranked)
        or len(actual_ids)!=len(set(actual_ids))
        or len(actual_score_ids)!=len(set(actual_score_ids))
        or set(actual_score_ids)!=set(expected_by_score)
    ):
        raise M3Top3AdmissionError(
            "FULL_RANKING_LEDGER_INCOMPLETE",
            "prediction batch identity set does not equal the full ranked E set",
            {"ranked_count":len(ranked),"prediction_count":len(records)},
            EXIT_INTEGRITY,
        )
    for record in records:
        expected=expected_by_score.get(str(record.get("model_score_id")))
        if expected is None or record!=expected:
            raise M3Top3AdmissionError(
                "FULL_RANKING_LEDGER_INCOMPLETE",
                "prediction row differs from the exact full-E ranking projection",
                {"model_score_id":record.get("model_score_id")},
                EXIT_INTEGRITY,
            )


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
            if prior==payload:
                return "REUSED"
            raise M3Top3AdmissionError(
                "NONDETERMINISTIC_RERUN",
                "concurrent run identity has different result bytes",
                {"path":str(self.path)},
                EXIT_INTEGRITY,
            )
        finally:
            try: candidate.unlink()
            except FileNotFoundError: pass
        return "APPENDED"


class ImmutableReleaseStore:
    """Create-once exact release receipt keyed by a governed release identity."""
    def __init__(self,path:str|Path): self.path=Path(path)
    def admit(self,release_identity:str,payload:bytes)->str:
        envelope=canonical_json_bytes({"release_identity":release_identity,"payload_sha256":hashlib.sha256(payload).hexdigest(),"byte_size":len(payload)})+b"\n"
        if self.path.exists():
            if self.path.read_bytes()!=envelope:
                raise M3Top3AdmissionError("IMMUTABLE_RELEASE_COLLISION","same release identity is already bound to different bytes",{"path":str(self.path),"release_identity":release_identity},EXIT_INTEGRITY)
            return "REUSED"
        self.path.parent.mkdir(parents=True,exist_ok=True)
        candidate=self.path.with_name(f".{self.path.name}.{uuid.uuid4().hex}.candidate")
        atomic_write_text(candidate,envelope.decode("utf-8"))
        try: os.link(candidate,self.path)
        except FileExistsError:
            if self.path.read_bytes()!=envelope:
                raise M3Top3AdmissionError("IMMUTABLE_RELEASE_COLLISION","concurrent release identity is bound to different bytes",{"path":str(self.path),"release_identity":release_identity},EXIT_INTEGRITY)
            return "REUSED"
        finally:
            try: candidate.unlink()
            except FileNotFoundError: pass
        return "APPENDED"


@contextmanager
def publication_transaction(*identities: str):
    """Lock every governed identity in a stable order.

    A single hash of the *combination* would let two different run paths mutate
    the same shared ledger concurrently.  Per-identity locks make the ledger
    identity a common serialization boundary while retaining a separate run
    artifact boundary.  Sorted acquisition prevents lock-order deadlocks.
    """

    locks=[]
    try:
        for identity in sorted(set(identities)):
            digest=hashlib.sha256(identity.encode("utf-8")).hexdigest()
            lock_path=Path("/tmp")/f"m3top3-publication-{digest}.lock"
            lock=lock_path.open("a+b")
            fcntl.flock(lock.fileno(),fcntl.LOCK_EX)
            locks.append(lock)
        yield
    finally:
        for lock in reversed(locks):
            fcntl.flock(lock.fileno(),fcntl.LOCK_UN)
            lock.close()


class FullRunArtifactStore:
    """Create-only full-run set with a separate commit manifest published last.

    The result JSON and its three auxiliary JSONL files are *not* a published
    run until the exact v2 commit manifest exists.  A process failure that
    leaves any subset of those files behind is therefore terminal for that run
    identity: a later attempt must not silently resume the partial write.

    Prediction ledgers are shared append-only files.  Consequently their whole
    file hash is not a stable property of an earlier run.  The commit manifest
    binds only the immutable prediction batch belonging to this result: its
    expected prediction identities, exact live row hashes, and count.
    """

    COMMIT_SCHEMA_VERSION = "m3top3-full-run-commit-v2"

    def __init__(self,path:str|Path):
        self.path=Path(path)
        self._preflight_receipt:tuple[str,str|None,str]|None=None

    @property
    def manifest_path(self)->Path:
        return self.path.with_suffix(".manifest.json")

    def _payloads(self,result:dict[str,Any])->dict[Path,bytes]:
        stem=self.path.with_suffix("")
        def jsonl(rows:list[dict[str,Any]])->bytes:
            return b"".join(canonical_json_bytes(row)+b"\n" for row in rows)
        return {
            stem.with_name(stem.name+".scorer_outputs.jsonl"):jsonl(result["scorer_outputs"]),
            stem.with_name(stem.name+".ranking.jsonl"):jsonl(result["ranked"]),
            stem.with_name(stem.name+".outcomes.jsonl"):jsonl(result["outcomes"]),
            self.path:canonical_json_bytes(result)+b"\n",
        }

    @property
    def _artifact_paths(self)->tuple[Path,...]:
        stem=self.path.with_suffix("")
        return (
            stem.with_name(stem.name+".scorer_outputs.jsonl"),
            stem.with_name(stem.name+".ranking.jsonl"),
            stem.with_name(stem.name+".outcomes.jsonl"),
            self.path,
        )

    @staticmethod
    def _result_fingerprint(result:dict[str,Any])->str:
        return hashlib.sha256(canonical_json_bytes(result)).hexdigest()

    @staticmethod
    def _ledger_locator(ledger_path:Path|None)->str|None:
        return str(ledger_path.resolve()) if ledger_path is not None else None

    @staticmethod
    def _expected_prediction_rows(result:dict[str,Any])->dict[str,dict[str,Any]]:
        """Return the prediction identity set and all result-verifiable fields."""

        lineage_hash=result.get("lineage_hash")
        ranked=result.get("ranked")
        if not isinstance(lineage_hash,str) or not lineage_hash or not isinstance(ranked,list):
            raise M3Top3AdmissionError(
                "INCOMPLETE_RESULT_PUBLICATION",
                "result does not contain the lineage and full ranking needed to bind its prediction batch",
                {"validation_run_id":result.get("validation_run_id")},
                EXIT_INTEGRITY,
            )
        expected:dict[str,dict[str,Any]]={}
        for row in ranked:
            try:
                identity={
                    "pit_snapshot_id":row["pit_snapshot_id"],
                    "model_version":row["model_version"],
                    "company_id":row["company_id"],
                    "rank":row["rank"],
                    "denominator_member_id":row.get("denominator_member_id"),
                    "lineage_hash":lineage_hash,
                }
                prediction_id=deterministic_id("pred",identity)
                expected_row={
                    "prediction_id":prediction_id,
                    "pit_snapshot_id":row["pit_snapshot_id"],
                    "model_score_id":row.get("model_score_id"),
                    "model_version":row["model_version"],
                    "company_id":row["company_id"],
                    "security_code":row["security_code"],
                    "rank":row["rank"],
                    "score":row["raw_score"],
                    "selected":row["selected_top3"],
                    "denominator_member_id":row.get("denominator_member_id"),
                    "lineage_hash":lineage_hash,
                }
            except (KeyError,TypeError) as exc:
                raise M3Top3AdmissionError(
                    "INCOMPLETE_RESULT_PUBLICATION",
                    "full ranking cannot define an exact prediction batch",
                    {"validation_run_id":result.get("validation_run_id"),"cause":type(exc).__name__},
                    EXIT_INTEGRITY,
                ) from exc
            if prediction_id in expected:
                raise M3Top3AdmissionError(
                    "INCOMPLETE_RESULT_PUBLICATION",
                    "full ranking maps more than one member to the same prediction identity",
                    {"prediction_id":prediction_id},
                    EXIT_INTEGRITY,
                )
            expected[prediction_id]=expected_row
        if result.get("ranked_count")!=len(expected):
            raise M3Top3AdmissionError(
                "INCOMPLETE_RESULT_PUBLICATION",
                "ranked_count does not equal the prediction identity set",
                {"declared":result.get("ranked_count"),"actual":len(expected)},
                EXIT_INTEGRITY,
            )
        return expected

    @staticmethod
    def _read_ledger_rows(ledger_path:Path)->dict[str,tuple[dict[str,Any],bytes]]:
        rows:dict[str,tuple[dict[str,Any],bytes]]={}
        if not ledger_path.exists():
            return rows
        try:
            payload=ledger_path.read_bytes()
            if payload and not payload.endswith(b"\n"):
                raise ValueError("ledger is not newline terminated")
            for line_number,raw_line in enumerate(payload.splitlines(),1):
                if not raw_line:
                    continue
                row=json.loads(raw_line.decode("utf-8"))
                if not isinstance(row,dict) or not isinstance(row.get("prediction_id"),str):
                    raise TypeError("prediction ledger row lacks an immutable identity")
                canonical=canonical_json_bytes(row)
                if canonical!=raw_line:
                    raise ValueError("prediction ledger row is not canonical JSON")
                prediction_id=row["prediction_id"]
                prior=rows.get(prediction_id)
                if prior is not None and prior[1]!=raw_line:
                    raise ValueError("prediction ledger has a conflicting duplicate identity")
                if prior is not None:
                    raise ValueError("prediction ledger repeats an immutable identity")
                rows[prediction_id]=(row,raw_line)
        except (OSError,UnicodeError,json.JSONDecodeError,TypeError,ValueError) as exc:
            raise M3Top3AdmissionError(
                "INCOMPLETE_RESULT_PUBLICATION",
                "shared prediction ledger is unreadable or not an exact immutable row set",
                {"path":str(ledger_path),"line":locals().get("line_number"),"cause":type(exc).__name__},
                EXIT_INTEGRITY,
            ) from exc
        return rows

    def _prediction_batch(
        self,
        result:dict[str,Any],
        ledger_path:Path|None,
        *,
        require_complete:bool,
    )->dict[str,Any]:
        if ledger_path is None:
            return {
                "prediction_batch_count":0,
                "prediction_batch_identity_set":[],
                "prediction_batch_identity_digest":hashlib.sha256(canonical_json_bytes([])).hexdigest(),
                "prediction_batch_payload_digest":hashlib.sha256(canonical_json_bytes([])).hexdigest(),
            }
        expected=self._expected_prediction_rows(result)
        live=self._read_ledger_rows(ledger_path)
        selected={prediction_id:live[prediction_id] for prediction_id in expected if prediction_id in live}
        if require_complete and set(selected)!=set(expected):
            raise M3Top3AdmissionError(
                "INCOMPLETE_RESULT_PUBLICATION",
                "shared prediction ledger does not contain the exact complete run batch",
                {
                    "path":str(ledger_path),
                    "expected_count":len(expected),
                    "actual_count":len(selected),
                    "missing":sorted(set(expected)-set(selected)),
                },
                EXIT_INTEGRITY,
            )
        for prediction_id,(row,_) in selected.items():
            expected_row=expected[prediction_id]
            mismatched=[key for key,value in expected_row.items() if row.get(key)!=value]
            if mismatched:
                raise M3Top3AdmissionError(
                    "NONDETERMINISTIC_RERUN",
                    "live prediction row differs from the exact result-derived batch member",
                    {"path":str(ledger_path),"prediction_id":prediction_id,"fields":mismatched},
                    EXIT_INTEGRITY,
                )
        identities=sorted(selected)
        record_hashes=[
            {"prediction_id":prediction_id,"row_sha256":hashlib.sha256(selected[prediction_id][1]).hexdigest()}
            for prediction_id in identities
        ]
        return {
            "prediction_batch_count":len(identities),
            "prediction_batch_identity_set":identities,
            "prediction_batch_identity_digest":hashlib.sha256(canonical_json_bytes(identities)).hexdigest(),
            "prediction_batch_payload_digest":hashlib.sha256(canonical_json_bytes(record_hashes)).hexdigest(),
        }

    def _commit_manifest(
        self,
        result:dict[str,Any],
        payloads:dict[Path,bytes],
        ledger_path:Path|None,
        *,
        require_complete_batch:bool,
    )->dict[str,Any]:
        by_suffix={
            "scorer_outputs_sha256":next(payload for path,payload in payloads.items() if path.name.endswith(".scorer_outputs.jsonl")),
            "ranking_sha256":next(payload for path,payload in payloads.items() if path.name.endswith(".ranking.jsonl")),
            "outcomes_sha256":next(payload for path,payload in payloads.items() if path.name.endswith(".outcomes.jsonl")),
        }
        return {
            "schema_version":self.COMMIT_SCHEMA_VERSION,
            "status":"COMPLETE",
            "validation_run_id":result["validation_run_id"],
            "result_sha256":hashlib.sha256(payloads[self.path]).hexdigest(),
            "ranked_count":result["ranked_count"],
            "outcome_record_count":result["outcome_count"],
            **{key:hashlib.sha256(payload).hexdigest() for key,payload in by_suffix.items()},
            **self._prediction_batch(result,ledger_path,require_complete=require_complete_batch),
        }

    def _publication_state(self)->tuple[bool,bool]:
        return self.manifest_path.exists(),any(path.exists() for path in self._artifact_paths)

    def preflight(self,result:dict[str,Any],ledger_path:Path|None=None)->str:
        payloads=self._payloads(result)
        manifest_exists,artifact_exists=self._publication_state()
        if not manifest_exists:
            if artifact_exists:
                raise M3Top3AdmissionError(
                    "INCOMPLETE_RESULT_PUBLICATION",
                    "partial run artifacts exist without an exact complete commit manifest; resume is prohibited",
                    {"path":str(self.path)},
                    EXIT_INTEGRITY,
                )
            batch=self._prediction_batch(result,ledger_path,require_complete=False)
            if ledger_path is not None and batch["prediction_batch_count"]:
                raise M3Top3AdmissionError(
                    "INCOMPLETE_RESULT_PUBLICATION",
                    "prediction batch exists without its exact complete run publication; resume is prohibited",
                    {"path":str(ledger_path),"prediction_batch_count":batch["prediction_batch_count"]},
                    EXIT_INTEGRITY,
                )
            state="APPENDABLE"
        else:
            complete_artifact_set=artifact_exists and all(path.exists() for path in self._artifact_paths)
            if not complete_artifact_set:
                raise M3Top3AdmissionError(
                    "INCOMPLETE_RESULT_PUBLICATION",
                    "commit manifest exists without its exact complete artifact set",
                    {"path":str(self.manifest_path)},
                    EXIT_INTEGRITY,
                )
            for path,payload in payloads.items():
                if path.read_bytes()!=payload:
                    raise M3Top3AdmissionError(
                        "NONDETERMINISTIC_RERUN",
                        "existing committed run identity has different artifact bytes",
                        {"path":str(path)},
                        EXIT_INTEGRITY,
                    )
            try:
                manifest_bytes=self.manifest_path.read_bytes()
                manifest=json.loads(manifest_bytes.decode("utf-8"))
            except (OSError,UnicodeError,json.JSONDecodeError) as exc:
                raise M3Top3AdmissionError(
                    "INCOMPLETE_RESULT_PUBLICATION",
                    "full-run commit manifest is unreadable or malformed",
                    {"path":str(self.manifest_path),"cause":type(exc).__name__},
                    EXIT_INTEGRITY,
                ) from exc
            expected=self._commit_manifest(result,payloads,ledger_path,require_complete_batch=ledger_path is not None)
            if manifest_bytes!=canonical_json_bytes(manifest)+b"\n" or manifest!=expected:
                raise M3Top3AdmissionError(
                    "INCOMPLETE_RESULT_PUBLICATION",
                    "full-run commit manifest is not the exact v2 commit for the live artifact and prediction batch",
                    {"path":str(self.manifest_path)},
                    EXIT_INTEGRITY,
                )
            state="REUSED"
        self._preflight_receipt=(
            self._result_fingerprint(result),
            self._ledger_locator(ledger_path),
            state,
        )
        return state

    @staticmethod
    def _admit_bytes(path:Path,payload:bytes)->str:
        if path.exists():
            if path.read_bytes()!=payload:
                raise M3Top3AdmissionError("NONDETERMINISTIC_RERUN","immutable run artifact collision",{"path":str(path)},EXIT_INTEGRITY)
            return "REUSED"
        candidate=path.with_name(f".{path.name}.{uuid.uuid4().hex}.candidate")
        atomic_write_text(candidate,payload.decode("utf-8"))
        try:
            os.link(candidate,path)
        except FileExistsError:
            if path.read_bytes()!=payload:
                raise M3Top3AdmissionError("NONDETERMINISTIC_RERUN","concurrent immutable run artifact collision",{"path":str(path)},EXIT_INTEGRITY)
            return "REUSED"
        finally:
            try: candidate.unlink()
            except FileNotFoundError: pass
        return "APPENDED"

    def publish(self,result:dict[str,Any],ledger_path:Path|None=None)->str:
        payloads=self._payloads(result)
        manifest_exists,artifact_exists=self._publication_state()
        if manifest_exists or artifact_exists:
            # Reuse/repair decisions are themselves a non-mutating preflight.
            # A fully committed exact run may therefore be reused by a fresh
            # store instance; a partial set is rejected before any write.
            return "REUSED" if self.preflight(result,ledger_path)=="REUSED" else "APPENDED"
        receipt=(self._result_fingerprint(result),self._ledger_locator(ledger_path))
        if self._preflight_receipt is None or self._preflight_receipt[:2]!=receipt:
            # Direct no-ledger use remains compatible.  A ledger-backed create
            # must have been preflighted before the caller appended its batch.
            if ledger_path is not None:
                raise M3Top3AdmissionError(
                    "INCOMPLETE_RESULT_PUBLICATION",
                    "ledger-backed publication lacks a matching pre-mutation cross-artifact preflight",
                    {"path":str(self.path)},
                    EXIT_INTEGRITY,
                )
            self.preflight(result,None)
        elif self._preflight_receipt[2]=="REUSED":
            raise M3Top3AdmissionError(
                "INCOMPLETE_RESULT_PUBLICATION",
                "a previously committed run disappeared after preflight; recreation is prohibited",
                {"path":str(self.path)},
                EXIT_INTEGRITY,
            )
        # This check happens before the first artifact write.  The ledger batch
        # may have been appended after the recorded preflight, but it must now
        # be exact and complete.
        manifest=self._commit_manifest(
            result,
            payloads,
            ledger_path,
            require_complete_batch=ledger_path is not None,
        )
        self.path.parent.mkdir(parents=True,exist_ok=True)
        state="REUSED"
        for path,payload in payloads.items():
            if self._admit_bytes(path,payload)=="APPENDED": state="APPENDED"
        # The separate commit marker is always the last governed write.
        if self._admit_bytes(self.manifest_path,canonical_json_bytes(manifest)+b"\n")=="APPENDED": state="APPENDED"
        return state
