# First 30-Minute Return — Real-Input Strict/Pragmatic Replay

- RUN_ID: `AAA-M3TOP3-REAL-INPUT-STRICT-PRAGMATIC-20260905-114150-CODEX-01`
- actual_start_at: `2026-09-05T11:41:50.2453872+09:00`
- returned_at: `2026-09-05T12:12:32.2312847+09:00`
- target_at: `2026-09-05T12:11:50.2453872+09:00`
- target_status: `MISSED_BY_PT41.9858975S`
- branch: `task/aaa/m3top3-real-input-replay-20260905`
- predecessor: `task/aaa/m3top3-first-scorecard-20260905@79b46dc1f63f1cd215cc0ebc0c91b4ec09e7dc71`
- environment: `Codex desktop / local / JWDEV / Microsoft Windows NT 10.0.26200.0 / bundled CPython 3.12.14`

## Fixed W1 engineering trace

The first five W1 INCLUDE rows in ascending `company_id` order are fixed as `KRX:003160`, `KRX:005290`,
`KRX:025560`, `KRX:031980`, and `KRX:036200`. The scorer comparison batch remains all 57 W1 INCLUDE
rows. The other 70 U127 rows remain the already-bound 8 proven tradability exclusions and 62 unresolved
exclusions; no row is silently removed.

## First admitted real source and field route

- company: `KRX:005290` (Dongjin Semichem; identity comes from the fixed W1 population binding)
- source authority: Korea Exchange KIND, official provisional consolidated earnings disclosure
- source URL: `https://kind.krx.co.kr/external/2024/08/02/000210/20240730000320/70956.htm`
- preserved source: `sources/W1/KRX-005290/KRX_005290_20240802_PROVISIONAL_EARNINGS_70956.htm`
- byte size / SHA-256: `16221` / `5c361107cbd2dc35b236b5358595e036ecb1dd9dc8b06471bca7bf9e550c7db7`
- stated information date: `2024-08-02`
- conservative supported interval: `2024-08-02T00:00:00+09:00` through `2024-08-02T23:59:59+09:00`
- W1 cutoff / temporal result: `2024-08-09T23:59:59+09:00` / `CUTOFF_SAFE`
- evidence state: `OBSERVED / PROVISIONAL_UNREVIEWED_SOURCE_LABEL_RETAINED`

The bounded Strict adapter will consume only two source-stated core operating comparisons with the unchanged
F02 `RELATIVE` transform:

| Consumed field | 2024 Q2 | 2023 Q2 | Unit | Downstream state |
|---|---:|---:|---|---|
| revenue | 355,414 | 331,317 | KRW million | observed pair, then derived relative change |
| operating profit | 49,972 | 45,565 | KRW million | observed pair, then derived relative change |

This is one observed F02 block with four observed numeric leaves and two scorer-derived relative changes. No
estimate, zero fill, inferred publication time, or unobserved value is introduced.

## Binding, bottleneck, and forecast

The unchanged model/config binding is preserved. The successor is additive: source manifest, one-key feature
sidecar, guarded overlay, and selection-sealed outcome stage. All other W1 company-feature cells remain explicit
`NOT_FOUND`. F05 is not synthesized because its governed return, universe, turnover, dividend and corporate-action
definitions are not bound.

- current bottleneck: `ADAPTER_IMPLEMENTATION_AND_TEST`, not source discovery
- earned work: `15 / 100 EWU` (`R0` and `R1` complete; `R2` in progress)
- remaining forecast: `1.5–3 hours`, low-to-medium confidence
- source documents admitted: `1`
- network attempts: `18` conservative manual count (`17` discovery/open plus `1` preserved fetch)
- tests / independent review acts: `0 / 0`
- CRU/token accounting: `NOT_INSTRUMENTED`

This is an execution checkpoint, not a completed replay claim. A non-null real model score is still required;
classification or rerunning the prior empty input does not satisfy the objective.
