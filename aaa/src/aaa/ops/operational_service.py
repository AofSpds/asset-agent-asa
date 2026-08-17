from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Mapping, Protocol, Sequence

from aaa.ops.operational_state import OperationalStateReader, ShadowReconciliationError, reconcile_run_rows
from aaa.ops.run_registry import list_runs as json_list_runs
from aaa.ops.run_registry import persona_overview as json_persona_overview


class OperationalAuthorityMode(str, Enum):
    JSON_AUTHORITATIVE_SHADOW = "JSON_AUTHORITATIVE_SHADOW"
    POSTGRES_AUTHORITATIVE = "POSTGRES_AUTHORITATIVE"


class OperationalBackendUnavailable(RuntimeError):
    pass


class OperationalProjectionReader(OperationalStateReader, Protocol):
    def persona_overview(self) -> Sequence[Mapping[str, object]]: ...


class ExecutionProjectionReader(Protocol):
    def list_workers(self) -> Sequence[Mapping[str, object]]: ...
    def list_tasks(self) -> Sequence[Mapping[str, object]]: ...


class OperationalReadService:
    """Single server-side read path for CLI/API/Owner Console.

    JSON remains authoritative for Run/Persona state until Owner cutover. T19
    worker/task state is exposed only from an explicitly connected PostgreSQL
    projection; absence of that projection returns no worker evidence and never
    infers liveness from chat or dispatch records.
    """

    def __init__(self, repo_root: Path, *, mode: OperationalAuthorityMode = OperationalAuthorityMode.JSON_AUTHORITATIVE_SHADOW, shadow_reader: OperationalStateReader | None = None, postgres_reader: OperationalProjectionReader | None = None, execution_reader: ExecutionProjectionReader | None = None):
        self._repo_root = repo_root.resolve(); self._mode = mode; self._shadow_reader = shadow_reader; self._postgres_reader = postgres_reader; self._execution_reader = execution_reader

    @property
    def mode(self) -> OperationalAuthorityMode: return self._mode

    def _require_postgres(self) -> OperationalProjectionReader:
        if self._postgres_reader is None: raise OperationalBackendUnavailable("POSTGRES_OPERATIONAL_BACKEND_UNAVAILABLE")
        return self._postgres_reader

    def runs(self) -> list[dict[str, object]]:
        if self._mode is OperationalAuthorityMode.POSTGRES_AUTHORITATIVE:
            reader = self._require_postgres()
            try: return [dict(row) for row in reader.list_runs()]
            except Exception as exc: raise OperationalBackendUnavailable("POSTGRES_OPERATIONAL_READ_FAILED") from exc
        authority_rows = json_list_runs(self._repo_root)
        if self._shadow_reader is not None:
            try: shadow_rows = self._shadow_reader.list_runs()
            except Exception as exc: raise OperationalBackendUnavailable("POSTGRES_SHADOW_READ_FAILED") from exc
            report = reconcile_run_rows(authority_rows, shadow_rows)
            if report.status != "MATCH": raise ShadowReconciliationError("SHADOW_RUN_REGISTRY_MISMATCH:" f"missing={report.missing_in_shadow}:" f"extra={report.extra_in_shadow}:" f"mismatched={report.mismatched_run_ids}")
        return authority_rows

    def personas(self) -> list[dict[str, object]]:
        if self._mode is OperationalAuthorityMode.POSTGRES_AUTHORITATIVE:
            reader = self._require_postgres()
            try: return [dict(row) for row in reader.persona_overview()]
            except Exception as exc: raise OperationalBackendUnavailable("POSTGRES_PERSONA_PROJECTION_FAILED") from exc
        self.runs(); return json_persona_overview(self._repo_root)

    def workers(self) -> list[dict[str, object]]:
        if self._execution_reader is None: return []
        try: return [dict(row) for row in self._execution_reader.list_workers()]
        except Exception as exc: raise OperationalBackendUnavailable("POSTGRES_WORKER_PROJECTION_FAILED") from exc

    def tasks(self) -> list[dict[str, object]]:
        if self._execution_reader is None: return []
        try: return [dict(row) for row in self._execution_reader.list_tasks()]
        except Exception as exc: raise OperationalBackendUnavailable("POSTGRES_TASK_PROJECTION_FAILED") from exc
