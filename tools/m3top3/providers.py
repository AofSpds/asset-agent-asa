from __future__ import annotations

import csv
import importlib
import json
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any, Protocol, Sequence

from .core import parse_date, parse_datetime


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
    def __init__(self, path: str | Path, source_version: str):
        self.path = Path(path); self.source_version = source_version; self._rows = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if line.strip(): self._rows.append(json.loads(line))

    def records_at(self, company_id: str, cutoff_at: datetime) -> Sequence[dict[str, Any]]:
        out=[]
        for r in self._rows:
            if str(r.get("company_id")) != company_id: continue
            pub=r.get("publication_at")
            if pub is not None and parse_datetime(pub) > cutoff_at: continue
            valid_from=r.get("valid_from") or r.get("effective_at")
            if valid_from and parse_datetime(valid_from) > cutoff_at: continue
            valid_to=r.get("valid_to")
            if valid_to and parse_datetime(valid_to) <= cutoff_at: continue
            out.append(dict(r))
        return out


class InMemoryFeatureProvider:
    def __init__(self, rows: Sequence[dict[str, Any]], source_version: str = "TEST-FEATURES"):
        self._rows=[dict(r) for r in rows]; self.source_version=source_version
    def records_at(self, company_id: str, cutoff_at: datetime) -> Sequence[dict[str, Any]]:
        return [dict(r) for r in self._rows if str(r.get("company_id")) == company_id and not (r.get("publication_at") and parse_datetime(r["publication_at"]) > cutoff_at)]


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
    amount: Decimal | None = None
    changes: Decimal | None = None
    changes_ratio: Decimal | None = None


class PriceProvider(Protocol):
    dataset_id: str
    dataset_hash: str
    semantics: str
    def trading_dates(self, start: date, end: date) -> list[date]: ...
    def row(self, code: str, trading_date: date) -> PriceRow | None: ...
    def rows(self, code: str, start: date, end: date) -> list[PriceRow]: ...


class CsvPriceProvider:
    def __init__(self, path: str | Path, dataset_id: str = "TEST-PRICE", dataset_hash: str = "TEST", semantics: str = "RAW_IMMUTABLE"):
        self.path=Path(path); self.dataset_id=dataset_id; self.dataset_hash=dataset_hash; self.semantics=semantics; rows=[]
        with self.path.open("r", encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                rows.append(PriceRow(
                    parse_date(r["date"]),
                    str(r["code"]).zfill(6),
                    Decimal(str(r["open"])),
                    Decimal(str(r["high"])),
                    Decimal(str(r["low"])),
                    Decimal(str(r["close"])),
                    volume=int(r["volume"]) if r.get("volume") else None,
                    marcap=Decimal(str(r["marcap"])) if r.get("marcap") else None,
                    stocks=int(r["stocks"]) if r.get("stocks") else None,
                    corporate_action_flag=(r.get("corporate_action_flag", "").lower() == "true") if r.get("corporate_action_flag") else None,
                    adjustment_factor=Decimal(str(r["adjustment_factor"])) if r.get("adjustment_factor") else None,
                    amount=Decimal(str(r["amount"])) if r.get("amount") else None,
                    changes=Decimal(str(r["changes"])) if r.get("changes") else None,
                    changes_ratio=Decimal(str(r["changes_ratio"])) if r.get("changes_ratio") else None,
                ))
        self._rows=rows; self._by_key={(r.code,r.date):r for r in rows}; self._dates=sorted({r.date for r in rows})
    def trading_dates(self,start:date,end:date)->list[date]: return [d for d in self._dates if start<=d<=end]
    def row(self,code:str,trading_date:date)->PriceRow|None: return self._by_key.get((str(code).zfill(6),trading_date))
    def rows(self,code:str,start:date,end:date)->list[PriceRow]:
        code=str(code).zfill(6); return [r for r in self._rows if r.code==code and start<=r.date<=end]


class DuckDBParquetPriceProvider:
    """Optional production adapter for RAW marcap or PRICE-CANONICAL parquet."""
    def __init__(self, paths: Sequence[str | Path], dataset_id: str, dataset_hash: str, semantics: str = "RAW_IMMUTABLE"):
        try: duckdb=importlib.import_module("duckdb")
        except ImportError as exc: raise RuntimeError("DuckDBParquetPriceProvider requires the optional 'duckdb' package") from exc
        self._duckdb=duckdb; self.paths=[str(Path(p)) for p in paths]; self.dataset_id=dataset_id; self.dataset_hash=dataset_hash; self.semantics=semantics; self._con=duckdb.connect()
        list_sql="["+",".join(repr(p) for p in self.paths)+"]"; self._source_sql=f"read_parquet({list_sql}, union_by_name=true)"
        cols={r[0].lower():r[0] for r in self._con.execute(f"DESCRIBE SELECT * FROM {self._source_sql}").fetchall()}; required={"date","code","open","high","low","close"}; missing=required-set(cols)
        if missing: raise ValueError(f"price parquet missing required columns: {sorted(missing)}")
        self._cols=cols
    def _c(self,lower:str)->str: return '"'+self._cols[lower].replace('"','""')+'"'
    def _optional(self, lower: str) -> str:
        return self._c(lower) if lower in self._cols else "NULL"
    def _price_select(self) -> str:
        return ", ".join((
            f"CAST({self._c('date')} AS DATE)",
            f"CAST({self._c('code')} AS VARCHAR)",
            self._c("open"), self._c("high"), self._c("low"), self._c("close"),
            self._optional("volume"), self._optional("marcap"), self._optional("stocks"),
            self._optional("corporate_action_flag"), self._optional("adjustment_factor"),
            self._optional("amount"), self._optional("changes"), self._optional("changesratio"),
        ))
    @staticmethod
    def _optional_integral(value, field: str) -> int | None:
        if value is None:
            return None
        if isinstance(value, bool):
            raise ValueError(f"{field} must be an integral numeric value, not bool")
        parsed = Decimal(str(value))
        if not parsed.is_finite() or parsed != parsed.to_integral_value():
            raise ValueError(f"{field} must be an integral numeric value")
        return int(parsed)
    @staticmethod
    def _price_row(row) -> PriceRow:
        return PriceRow(
            row[0], str(row[1]).zfill(6),
            *(Decimal(str(x)) for x in row[2:6]),
            volume=DuckDBParquetPriceProvider._optional_integral(row[6], "Volume"),
            marcap=None if row[7] is None else Decimal(str(row[7])),
            stocks=DuckDBParquetPriceProvider._optional_integral(row[8], "Stocks"),
            corporate_action_flag=None if row[9] is None else bool(row[9]),
            adjustment_factor=None if row[10] is None else Decimal(str(row[10])),
            amount=None if row[11] is None else Decimal(str(row[11])),
            changes=None if row[12] is None else Decimal(str(row[12])),
            changes_ratio=None if row[13] is None else Decimal(str(row[13])),
        )
    def trading_dates(self,start:date,end:date)->list[date]:
        q=f"SELECT DISTINCT CAST({self._c('date')} AS DATE) d FROM {self._source_sql} WHERE CAST({self._c('date')} AS DATE) BETWEEN ? AND ? ORDER BY d"; return [r[0] for r in self._con.execute(q,[start,end]).fetchall()]
    def row(self,code:str,trading_date:date)->PriceRow|None:
        q=f"SELECT {self._price_select()} FROM {self._source_sql} WHERE LPAD(CAST({self._c('code')} AS VARCHAR),6,'0')=? AND CAST({self._c('date')} AS DATE)=? LIMIT 2"; rows=self._con.execute(q,[str(code).zfill(6),trading_date]).fetchall()
        if len(rows) > 1: raise ValueError(f"duplicate price rows for {str(code).zfill(6)} on {trading_date.isoformat()}")
        return None if not rows else self._price_row(rows[0])
    def rows(self,code:str,start:date,end:date)->list[PriceRow]:
        q=f"SELECT {self._price_select()} FROM {self._source_sql} WHERE LPAD(CAST({self._c('code')} AS VARCHAR),6,'0')=? AND CAST({self._c('date')} AS DATE) BETWEEN ? AND ? ORDER BY 1"; out=[]
        for row in self._con.execute(q,[str(code).zfill(6),start,end]).fetchall(): out.append(self._price_row(row))
        return out
