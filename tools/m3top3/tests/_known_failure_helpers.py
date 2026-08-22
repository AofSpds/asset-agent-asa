from __future__ import annotations

import csv
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from tools.m3top3.backtest import ValidationRunner
from tools.m3top3.core import hash_file
from tools.m3top3.model_interface import DiagnosticFixtureScorer, RankingEngine
from tools.m3top3.outcome import ExplicitWindowResolver, OutcomeBuilder
from tools.m3top3.providers import CsvPriceProvider, InMemoryFeatureProvider, StaticUniverseProvider, UniverseState
from tools.m3top3.snapshot import SnapshotBuildConfig, SnapshotBuilder, SnapshotStore


def business_dates(start: date = date(2025, 1, 2), count: int = 20) -> list[date]:
    values: list[date] = []
    cursor = start
    while len(values) < count:
        if cursor.weekday() < 5:
            values.append(cursor)
        cursor += timedelta(days=1)
    return values


def write_price_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = [
        "date", "code", "open", "high", "low", "close", "volume",
        "corporate_action_flag", "adjustment_factor", "corporate_action_evidence_id",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def standard_price_rows(dates: list[date] | None = None, code: str = "005930") -> list[dict[str, Any]]:
    dates = dates or business_dates()
    return [
        {
            "date": d.isoformat(), "code": code, "open": 100 + i,
            "high": 103 + i, "low": 98 + i, "close": 101 + i,
            "volume": 1000 + i,
        }
        for i, d in enumerate(dates)
    ]


def price_provider(root: Path, rows: list[dict[str, Any]] | None = None, **kwargs: Any) -> CsvPriceProvider:
    path = root / f"price-{len(list(root.glob('price-*.csv')))}.csv"
    write_price_csv(path, rows or standard_price_rows())
    kwargs.setdefault("dataset_hash", hash_file(path))
    return CsvPriceProvider(path, **kwargs)


def ready_builder(root: Path, feature_rows: list[dict[str, Any]] | None = None):
    dates = business_dates()
    price = price_provider(root, standard_price_rows(dates))
    universe = StaticUniverseProvider(
        [UniverseState("C1", "005930", date(2020, 1, 1), None, True, True, "U1")],
        "U-TEST", "DIAGNOSTIC",
    )
    if feature_rows is None:
        feature_rows = [{
            "company_id": "C1", "feature_id": "diagnostic_score", "value": "9",
            "publication_at": "2025-01-02T10:00:00+09:00",
        }]
    builder = SnapshotBuilder(universe, InMemoryFeatureProvider(feature_rows), price, SnapshotBuildConfig())
    return dates, price, builder


def materialize_ready_snapshot(root: Path):
    dates, price, builder = ready_builder(root)
    snapshot_root = root / "snapshots"
    built = builder.build(dates[0])
    SnapshotStore(snapshot_root).write(built, {"generator_version": "test-v1"})
    return snapshot_root / dates[0].isoformat(), dates, price, built


class CountingScorer(DiagnosticFixtureScorer):
    def __init__(self, score: str = "9"):
        self.calls = 0
        self.score_value = score

    def score(self, model_input):
        self.calls += 1
        copied = dict(model_input)
        copied["feature_values"] = dict(copied.get("feature_values", {}))
        copied["feature_values"]["diagnostic_score"] = self.score_value
        return super().score(copied)


def diagnostic_runner(price: CsvPriceProvider, dates: list[date], scorer=None, tie_policy: str = "COMPANY_ID_ASC_DIAGNOSTIC"):
    scorer = scorer or CountingScorer()
    windows = ExplicitWindowResolver({dates[0].isoformat(): dates[5].isoformat()}, "test-window-v1")
    return ValidationRunner(scorer, RankingEngine(tie_policy), OutcomeBuilder(price, windows), execution_mode="DIAGNOSTIC"), scorer
