from __future__ import annotations

import csv
import importlib
import json
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any, Protocol, Sequence

from .admission import EXIT_INTEGRITY, M3Top3AdmissionError, verify_price_release
from .core import aggregate_hash, deterministic_id, hash_file, parse_date, parse_datetime, sha256_hex
from .pit_guard import GuardViolation, PITGuard, PITLeakageError


@dataclass(frozen=True)
class UniverseState:
    company_id: str
    security_code: str
    valid_from: date | None
    valid_to: date | None
    operational_member: bool | None
    tradable_eligible: bool | None
    universe_record_id: str
    status: str = "VERIFIED"

    def effective_on(self, d: date) -> bool:
        if self.valid_from and d < self.valid_from:
            return False
        if self.valid_to and d >= self.valid_to:
            return False
        return True


class UniverseProvider(Protocol):
    release_id: str
    authority_status: str
    def states_at(self, snapshot_date: date) -> Sequence[UniverseState]: ...


class JsonlUniverseProvider:
    def __init__(self, path: str | Path, release_id: str, authority_status: str):
        self.path = Path(path)
        self.release_id = release_id
        self.authority_status = authority_status
        rows: list[UniverseState] = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            rows.append(UniverseState(str(r["company_id"]), str(r["security_code"]), parse_date(r["valid_from"]) if r.get("valid_from") else None, parse_date(r["valid_to"]) if r.get("valid_to") else None, r.get("operational_member"), r.get("tradable_eligible"), str(r["universe_record_id"]), str(r.get("status", "VERIFIED"))))
        self._rows = rows

    def states_at(self, snapshot_date: date) -> Sequence[UniverseState]:
        return [r for r in self._rows if r.effective_on(snapshot_date)]


class StaticUniverseProvider:
    def __init__(self, states: Sequence[UniverseState], release_id: str = "TEST-U", authority_status: str = "DIAGNOSTIC"):
        self._rows = list(states); self.release_id = release_id; self.authority_status = authority_status
    def states_at(self, snapshot_date: date) -> Sequence[UniverseState]:
        return [r for r in self._rows if r.effective_on(snapshot_date)]


class PITFeatureProvider(Protocol):
    source_version: str
    def records_at(self, company_id: str, cutoff_at: datetime) -> Sequence[dict[str, Any]]: ...


class JsonlFeatureProvider:
    def __init__(self, path: str | Path, source_version: str, cutoff_frozen_bundle: bool = False):
        self.path = Path(path); self.source_version = source_version; self.cutoff_frozen_bundle=cutoff_frozen_bundle; self._rows = []; self.retrieval_receipts=[]; self.last_retrieval_receipt=None
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if line.strip(): self._rows.append(json.loads(line))
        self.source_hash=hash_file(self.path)

    def records_at(self, company_id: str, cutoff_at: datetime) -> Sequence[dict[str, Any]]:
        return _select_feature_rows(self,company_id,cutoff_at)


class InMemoryFeatureProvider:
    def __init__(self, rows: Sequence[dict[str, Any]], source_version: str = "TEST-FEATURES", cutoff_frozen_bundle: bool = False):
        self._rows=[dict(r) for r in rows]; self.source_version=source_version; self.cutoff_frozen_bundle=cutoff_frozen_bundle; self.source_hash=sha256_hex(self._rows); self.retrieval_receipts=[]; self.last_retrieval_receipt=None
    def records_at(self, company_id: str, cutoff_at: datetime) -> Sequence[dict[str, Any]]:
        return _select_feature_rows(self,company_id,cutoff_at)


_AS_OF_EXCLUSION_CODES={"PIT_PUBLICATION_AFTER_CUTOFF","PIT_EFFECTIVE_AFTER_CUTOFF","POST_SNAPSHOT_CA_KNOWLEDGE"}


def _select_feature_rows(provider: Any, company_id: str, cutoff_at: datetime) -> list[dict[str, Any]]:
    """Select an as-of slice and emit a deterministic raw-source exclusion receipt.

    Longitudinal stores may contain later rows.  Those rows are excluded and
    audited; the consumed slice is independently re-guarded.  A declared
    cutoff-frozen bundle treats any future row as an integrity violation.
    """
    guard=PITGuard(); selected=[]; exclusions=[]; matching=0
    for index,r in enumerate(provider._rows):
        if str(r.get("company_id")) != company_id: continue
        matching+=1
        violations=guard.validate_model_input(r,cutoff_at)
        hard=[v for v in violations if v.code not in _AS_OF_EXCLUSION_CODES]
        future=[v for v in violations if v.code in _AS_OF_EXCLUSION_CODES]
        if hard: raise PITLeakageError(hard+future)
        row_id=str(r.get("feature_record_id") or r.get("evidence_id") or r.get("event_record_id") or deterministic_id("feature_row",{"source_hash":provider.source_hash,"index":index,"row":r}))
        if future:
            if provider.cutoff_frozen_bundle: raise PITLeakageError(future)
            exclusions.append({"row_id":row_id,"codes":sorted({v.code for v in future})}); continue
        valid_to=r.get("valid_to")
        if valid_to:
            try: expired=parse_datetime(valid_to)<=cutoff_at
            except (ValueError,TypeError) as exc: raise PITLeakageError([GuardViolation("INVALID_EFFECTIVE_DATETIME","valid_to must be a timezone-aware datetime","valid_to")]) from exc
            if expired:
                exclusions.append({"row_id":row_id,"codes":["OUTSIDE_VALIDITY_INTERVAL"]}); continue
        selected.append(dict(r))
    guard.assert_model_inputs(selected,cutoff_at)
    receipt_payload={"company_id":company_id,"cutoff_at":cutoff_at.isoformat(),"source_version":provider.source_version,"source_hash":provider.source_hash,"source_matching_rows":matching,"selected_rows":len(selected),"excluded_rows":len(exclusions),"exclusions":exclusions,"cutoff_frozen_bundle":provider.cutoff_frozen_bundle}
    receipt={**receipt_payload,"retrieval_receipt_id":deterministic_id("retrieval",receipt_payload)}
    provider.last_retrieval_receipt=receipt; provider.retrieval_receipts.append(receipt)
    return selected


@dataclass(frozen=True)
class PriceRow:
    date: date
    code: str
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int | None = None
    marcap: Decimal | None = None
    stocks: int | None = None
    corporate_action_flag: bool | None = None
    adjustment_factor: Decimal | None = None
    corporate_action_evidence_id: str | None = None


class PriceProvider(Protocol):
    dataset_id: str
    dataset_hash: str
    semantics: str
    def trading_dates(self, start: date, end: date) -> list[date]: ...
    def row(self, code: str, trading_date: date) -> PriceRow | None: ...
    def rows(self, code: str, start: date, end: date) -> list[PriceRow]: ...


class CsvPriceProvider:
    def __init__(self, path: str | Path, dataset_id: str = "TEST-PRICE", dataset_hash: str = "TEST", semantics: str = "RAW_IMMUTABLE", admission_config: dict[str, Any] | None = None):
        self.path=Path(path); self.dataset_id=dataset_id; self.dataset_hash=dataset_hash; self.semantics=semantics; self.canonical_release=admission_config; rows=[]
        self.component_hashes={str(self.path):hash_file(self.path)}; self.actual_dataset_hash=self.component_hashes[str(self.path)]
        verify_price_release(self,admission_config)
        seen:set[tuple[str,date]]=set()
        with self.path.open("r", encoding="utf-8", newline="") as f:
            for line_number,r in enumerate(csv.DictReader(f),2):
                row=PriceRow(parse_date(r["date"]), str(r["code"]).zfill(6), Decimal(str(r["open"])), Decimal(str(r["high"])), Decimal(str(r["low"])), Decimal(str(r["close"])), int(r["volume"]) if r.get("volume") else None, Decimal(str(r["marcap"])) if r.get("marcap") else None, int(r["stocks"]) if r.get("stocks") else None, (r.get("corporate_action_flag", "").lower()=="true") if r.get("corporate_action_flag") else None, Decimal(str(r["adjustment_factor"])) if r.get("adjustment_factor") else None, str(r["corporate_action_evidence_id"]) if r.get("corporate_action_evidence_id") else None)
                key=(row.code,row.date)
                if key in seen:
                    raise M3Top3AdmissionError("DUPLICATE_PRICE_KEY",f"duplicate price key {key}",{"line":line_number,"code":row.code,"date":row.date.isoformat()},EXIT_INTEGRITY)
                seen.add(key); _validate_price_row(row,{"line":line_number,"path":str(self.path)}); rows.append(row)
        self._rows=rows; self._by_key={(r.code,r.date):r for r in rows}; self._dates=sorted({r.date for r in rows})
    def trading_dates(self,start:date,end:date)->list[date]: return [d for d in self._dates if start<=d<=end]
    def row(self,code:str,trading_date:date)->PriceRow|None: return self._by_key.get((str(code).zfill(6),trading_date))
    def rows(self,code:str,start:date,end:date)->list[PriceRow]:
        code=str(code).zfill(6); return [r for r in self._rows if r.code==code and start<=r.date<=end]


class DuckDBParquetPriceProvider:
    """Optional production adapter for RAW marcap or PRICE-CANONICAL parquet."""
    def __init__(self, paths: Sequence[str | Path], dataset_id: str, dataset_hash: str, semantics: str = "RAW_IMMUTABLE", admission_config: dict[str, Any] | None = None):
        try: duckdb=importlib.import_module("duckdb")
        except ImportError as exc: raise RuntimeError("DuckDBParquetPriceProvider requires the optional 'duckdb' package") from exc
        self._duckdb=duckdb; self.paths=[str(Path(p)) for p in paths]; self.dataset_id=dataset_id; self.dataset_hash=dataset_hash; self.semantics=semantics; self.canonical_release=admission_config; self._con=duckdb.connect()
        self.component_hashes={p:hash_file(Path(p)) for p in self.paths}; self.actual_dataset_hash=next(iter(self.component_hashes.values())) if len(self.component_hashes)==1 else aggregate_hash(self.component_hashes.values())
        verify_price_release(self,admission_config)
        list_sql="["+",".join(repr(p) for p in self.paths)+"]"; self._source_sql=f"read_parquet({list_sql}, union_by_name=true)"
        cols={r[0].lower():r[0] for r in self._con.execute(f"DESCRIBE SELECT * FROM {self._source_sql}").fetchall()}; required={"date","code","open","high","low","close"}; missing=required-set(cols)
        if missing: raise ValueError(f"price parquet missing required columns: {sorted(missing)}")
        self._cols=cols
        duplicate=self._con.execute(f"SELECT LPAD(CAST({self._c('code')} AS VARCHAR),6,'0'), CAST({self._c('date')} AS DATE), COUNT(*) n FROM {self._source_sql} GROUP BY 1,2 HAVING n>1 LIMIT 1").fetchone()
        if duplicate: raise M3Top3AdmissionError("DUPLICATE_PRICE_KEY",f"duplicate price key {(duplicate[0],duplicate[1])}",{"code":duplicate[0],"date":str(duplicate[1]),"count":duplicate[2]},EXIT_INTEGRITY)
        invalid=self._con.execute(f"SELECT CAST({self._c('date')} AS DATE), LPAD(CAST({self._c('code')} AS VARCHAR),6,'0'), {self._c('open')}, {self._c('high')}, {self._c('low')}, {self._c('close')} FROM {self._source_sql} WHERE {self._c('open')}<=0 OR {self._c('high')}<=0 OR {self._c('low')}<=0 OR {self._c('close')}<=0 OR {self._c('high')}<GREATEST({self._c('open')},{self._c('close')}) OR {self._c('low')}>LEAST({self._c('open')},{self._c('close')}) OR {self._c('low')}>{self._c('high')} LIMIT 1").fetchone()
        if invalid: raise M3Top3AdmissionError("INVALID_OHLC",f"invalid OHLC row {(invalid[1],invalid[0])}",{"code":invalid[1],"date":str(invalid[0])},EXIT_INTEGRITY)
    def _c(self,lower:str)->str: return '"'+self._cols[lower].replace('"','""')+'"'
    def trading_dates(self,start:date,end:date)->list[date]:
        q=f"SELECT DISTINCT CAST({self._c('date')} AS DATE) d FROM {self._source_sql} WHERE CAST({self._c('date')} AS DATE) BETWEEN ? AND ? ORDER BY d"; return [r[0] for r in self._con.execute(q,[start,end]).fetchall()]
    def row(self,code:str,trading_date:date)->PriceRow|None:
        q=f"SELECT CAST({self._c('date')} AS DATE), CAST({self._c('code')} AS VARCHAR), {self._c('open')}, {self._c('high')}, {self._c('low')}, {self._c('close')} FROM {self._source_sql} WHERE LPAD(CAST({self._c('code')} AS VARCHAR),6,'0')=? AND CAST({self._c('date')} AS DATE)=?"; rows=self._con.execute(q,[str(code).zfill(6),trading_date]).fetchall()
        if len(rows)>1: raise M3Top3AdmissionError("DUPLICATE_PRICE_KEY",f"duplicate price key {(code,trading_date)}",exit_code=EXIT_INTEGRITY)
        row=rows[0] if rows else None
        return None if not row else PriceRow(row[0],str(row[1]).zfill(6),*(Decimal(str(x)) for x in row[2:6]))
    def rows(self,code:str,start:date,end:date)->list[PriceRow]:
        q=f"SELECT CAST({self._c('date')} AS DATE), CAST({self._c('code')} AS VARCHAR), {self._c('open')}, {self._c('high')}, {self._c('low')}, {self._c('close')} FROM {self._source_sql} WHERE LPAD(CAST({self._c('code')} AS VARCHAR),6,'0')=? AND CAST({self._c('date')} AS DATE) BETWEEN ? AND ? ORDER BY 1"; out=[]
        for row in self._con.execute(q,[str(code).zfill(6),start,end]).fetchall(): out.append(PriceRow(row[0],str(row[1]).zfill(6),*(Decimal(str(x)) for x in row[2:6])))
        return out


def _validate_price_row(row: PriceRow, locator: dict[str, Any]) -> None:
    prices=(row.open,row.high,row.low,row.close)
    if any(value <= 0 for value in prices) or row.high < max(row.open,row.close) or row.low > min(row.open,row.close) or row.low > row.high:
        raise M3Top3AdmissionError("INVALID_OHLC",f"invalid OHLC for {row.code} on {row.date}",{**locator,"code":row.code,"date":row.date.isoformat()},EXIT_INTEGRITY)
    if row.corporate_action_flag:
        if row.adjustment_factor is None:
            raise M3Top3AdmissionError("CA_EVIDENCE_INCOMPLETE","corporate-action row is missing an adjustment factor",{**locator,"code":row.code,"date":row.date.isoformat()},EXIT_INTEGRITY)
        if row.adjustment_factor <= 0:
            raise M3Top3AdmissionError("INVALID_ADJUSTMENT_FACTOR","adjustment factor must be positive",{**locator,"code":row.code,"date":row.date.isoformat()},EXIT_INTEGRITY)
        if not row.corporate_action_evidence_id:
            raise M3Top3AdmissionError("CA_EVIDENCE_INCOMPLETE","corporate-action row is missing evidence",{**locator,"code":row.code,"date":row.date.isoformat()},EXIT_INTEGRITY)
