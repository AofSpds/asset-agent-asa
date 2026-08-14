# M3Top3 PIT / Backtest Infrastructure (Working v0.1)

This package is an engineering implementation layer under the frozen `SEMI-ARCHITECTURE-SPEC v1.0` and frozen schema registry. It does **not** promote U127, PRICE-CANONICAL, M3Top3 v1, or Official Winner state.

Core separation:

`PIT-SNAPSHOT -> model_input derived view -> MODEL-SCORE -> ranking/prediction -> VALIDATION/outcome`

Important implementation choices:

- PIT evidence eligibility: `publication_at <= snapshot_cutoff_at`.
- Frozen PIT-SNAPSHOT remains model-independent; `model_version` is not written into PIT rows.
- Output/future labels are rejected by `PITGuard` before scoring.
- Observed trading dates come from the selected price dataset/adapter.
- RAW price is allowed only for working/preliminary outcomes and is tagged `CA_PENDING` / `UNADJUSTED_RAW`.
- PRICE-CANONICAL is a separate adapter mode; this package does not perform canonical cutover.
- Canonical validation rule is Entry = first trading-day Open after Snapshot/Window Start; Exit = first trading-day Open after configured Window End; MFE/MAE use holding rows through Window End. `horizon_close` is a **non-canonical diagnostic extension** retained separately because M3Top3 research explicitly needs 3M close behavior.
- Window dates are injected by a `WindowResolver`; W1-W8 meanings are not hard-coded.
- Tie policy defaults to `UNRESOLVED_CONTROL`. A deterministic company-id fallback exists only as `COMPANY_ID_ASC_DIAGNOSTIC`.
- Core unit tests are standard-library-only. Production Parquet access uses the optional DuckDB adapter.

Example historical snapshot CLI:

```bash
python -m tools.m3top3.cli_build_snapshots \
  --config tools/m3top3/configs/snapshot.example.json \
  --start 2024-08-01 --end 2026-08-13 \
  --output /data/snapshots/m3top3-working-v0.1
```

The example config is intentionally non-executable until the U127 historical universe/feature JSONL exports are materialized. Large snapshot/validation bytes belong in the external Data Plane (`snapshots/`, `validation/`), never Git.
