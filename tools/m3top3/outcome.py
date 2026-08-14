from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Protocol

from .core import deterministic_id
from .providers import PriceProvider


class WindowResolver(Protocol):
    protocol_version: str
    def window_end(self, snapshot_date: date) -> date: ...


class ExplicitWindowResolver:
    def __init__(self, mapping: dict[str, str], protocol_version: str = "explicit-window-v0.1"):
        self.mapping={date.fromisoformat(k):date.fromisoformat(v) for k,v in mapping.items()}; self.protocol_version=protocol_version
    def window_end(self,snapshot_date:date)->date:
        if snapshot_date not in self.mapping: raise KeyError(f"no authoritative window end configured for {snapshot_date}")
        return self.mapping[snapshot_date]


@dataclass(frozen=True)
class OutcomeRecord:
    validation_id:str; model_score_id:str; price_dataset_id:str; validation_protocol_version:str
    entry:Decimal|None; exit:Decimal|None; return_ratio:Decimal|None; mfe:Decimal|None; mae:Decimal|None
    horizon_close:Decimal|None; horizon_close_return:Decimal|None; entry_date:date|None; exit_date:date|None; window_end:date
    ca_status:str; outcome_comparability_status:str; outcome_validity:str; status:str


class OutcomeBuilder:
    """Future outcome builder. Never feeds future fields to model input."""
    def __init__(self,price:PriceProvider,windows:WindowResolver,validation_protocol_version:str="m3top3-outcome-working-v0.1"):
        self.price=price; self.windows=windows; self.validation_protocol_version=validation_protocol_version

    def build(self,model_score_id:str,code:str,snapshot_date:date)->OutcomeRecord:
        window_end=self.windows.window_end(snapshot_date)
        candidates=self.price.trading_dates(snapshot_date,window_end)
        future=self.price.trading_dates(window_end,date(window_end.year+1,window_end.month,min(window_end.day,28)))
        entry_dates=[d for d in candidates if d>snapshot_date]; exit_dates=[d for d in future if d>window_end]
        entry_date=entry_dates[0] if entry_dates else None; exit_date=exit_dates[0] if exit_dates else None
        if entry_date is None: return self._pending(model_score_id,window_end,"NO_ENTRY_PRICE")
        entry_row=self.price.row(code,entry_date)
        if entry_row is None: return self._pending(model_score_id,window_end,"NO_ENTRY_PRICE")
        held=self.price.rows(code,entry_date,window_end)
        if not held: return self._pending(model_score_id,window_end,"NO_HOLDING_ROWS")
        mfe=max(r.high for r in held); mae=min(r.low for r in held); horizon_close=held[-1].close; hret=(horizon_close/entry_row.open)-Decimal("1")
        if exit_date is None:
            return OutcomeRecord(deterministic_id("valpending",{"score":model_score_id,"window_end":window_end.isoformat(),"reason":"NO_EXIT"}),model_score_id,self.price.dataset_id,self.validation_protocol_version,entry_row.open,None,None,mfe,mae,horizon_close,hret,entry_date,None,window_end,"CA_PENDING" if self.price.semantics=="RAW_IMMUTABLE" else "EVIDENCE_ADJUSTED_OR_NONE","CA_PENDING" if self.price.semantics=="RAW_IMMUTABLE" else "PRICE_CANONICAL","PENDING_EXIT","PRELIMINARY")
        exit_row=self.price.row(code,exit_date)
        if exit_row is None: return self._pending(model_score_id,window_end,"NO_EXIT_PRICE")
        ret=(exit_row.open/entry_row.open)-Decimal("1"); validity="VALID" if self.price.semantics=="PRICE_CANONICAL" else "CA_PENDING"
        return OutcomeRecord(deterministic_id("val",{"score":model_score_id,"price":self.price.dataset_id,"protocol":self.validation_protocol_version,"entry":entry_date.isoformat(),"exit":exit_date.isoformat()}),model_score_id,self.price.dataset_id,self.validation_protocol_version,entry_row.open,exit_row.open,ret,mfe,mae,horizon_close,hret,entry_date,exit_date,window_end,"UNADJUSTED_RAW" if self.price.semantics=="RAW_IMMUTABLE" else "EVIDENCE_ADJUSTED_OR_NONE","CA_PENDING" if self.price.semantics=="RAW_IMMUTABLE" else "PRICE_CANONICAL",validity,"PRELIMINARY" if self.price.semantics=="RAW_IMMUTABLE" else "VALIDATION")

    def _pending(self,model_score_id:str,window_end:date,reason:str)->OutcomeRecord:
        return OutcomeRecord(deterministic_id("valpending",{"score":model_score_id,"window_end":window_end.isoformat(),"reason":reason}),model_score_id,self.price.dataset_id,self.validation_protocol_version,None,None,None,None,None,None,None,None,None,window_end,"CA_PENDING" if self.price.semantics=="RAW_IMMUTABLE" else "UNKNOWN","CA_PENDING",reason,"PRELIMINARY")
