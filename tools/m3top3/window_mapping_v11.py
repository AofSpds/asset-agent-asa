from __future__ import annotations

import calendar as _calendar
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Iterable, Protocol

from .core import parse_date

WINDOW_MAPPING_VERSION = "WM-v1.1"


class TradingCalendar(Protocol):
    def is_trading_day(self, day: date) -> bool: ...


@dataclass(frozen=True)
class SetTradingCalendar:
    trading_days: frozenset[date]

    @classmethod
    def from_dates(cls, days: Iterable[date | str]) -> "SetTradingCalendar":
        return cls(frozenset(parse_date(d) for d in days))

    def is_trading_day(self, day: date) -> bool:
        return day in self.trading_days


@dataclass(frozen=True)
class WeekdayCalendar:
    """Synthetic-test calendar only. Never a production KRX calendar source."""

    def is_trading_day(self, day: date) -> bool:
        return day.weekday() < 5


@dataclass(frozen=True)
class WindowMapping:
    version: str
    window_anchor_date: date
    snapshot_cutoff_date: date
    entry_trade_date: date
    nominal_window_end: date
    evaluation_last_trade_date: date
    exit_trade_date: date
    horizon_close_date: date


def add_calendar_months(day: date, months: int) -> date:
    if months < 0:
        raise ValueError("months must be non-negative for WM-v1.1")
    zero_based = (day.month - 1) + months
    year = day.year + zero_based // 12
    month = zero_based % 12 + 1
    last_day = _calendar.monthrange(year, month)[1]
    return date(year, month, min(day.day, last_day))


def _seek(calendar: TradingCalendar, start: date, step: int, strict: bool) -> date:
    if step not in (-1, 1):
        raise ValueError("step must be +/-1")
    d = start + timedelta(days=step) if strict else start
    for _ in range(370):
        if calendar.is_trading_day(d):
            return d
        d += timedelta(days=step)
    raise RuntimeError(f"no trading day resolved within 370 days of {start}")


def snapshot_cutoff_on_or_before(anchor: date, calendar: TradingCalendar) -> date:
    return _seek(calendar, anchor, -1, strict=False)


def first_trade_strictly_after(day: date, calendar: TradingCalendar) -> date:
    return _seek(calendar, day, 1, strict=True)


def last_trade_on_or_before(day: date, calendar: TradingCalendar) -> date:
    return _seek(calendar, day, -1, strict=False)


def resolve_window(anchor: date | str, calendar: TradingCalendar) -> WindowMapping:
    a = parse_date(anchor)
    nominal_end = add_calendar_months(a, 3)
    cutoff = snapshot_cutoff_on_or_before(a, calendar)
    entry = first_trade_strictly_after(a, calendar)
    evaluation_last = last_trade_on_or_before(nominal_end, calendar)
    exit_day = first_trade_strictly_after(nominal_end, calendar)
    if not (cutoff <= a < entry <= evaluation_last < exit_day):
        raise RuntimeError(
            "WM-v1.1 invariant failed: cutoff<=anchor<entry<=evaluation_last<exit"
        )
    return WindowMapping(
        version=WINDOW_MAPPING_VERSION,
        window_anchor_date=a,
        snapshot_cutoff_date=cutoff,
        entry_trade_date=entry,
        nominal_window_end=nominal_end,
        evaluation_last_trade_date=evaluation_last,
        exit_trade_date=exit_day,
        horizon_close_date=evaluation_last,
    )
