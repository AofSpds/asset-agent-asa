# F05 upstream definition recovery

- Run ID: `AAA-M3TOP3-F05-R0-20260905-214409-CODEX-01`
- Reference model revision: `c15cbfa9bbedcb3b388b9d101b269ced2fc83bc5`
- Inspection class: governed-history and current-artifact readback only
- Result: `0 EXACT_GOVERNED_DEFINITION_RECOVERED / 6 PARTIAL_DEFINITION_ONLY / 0 NO_GOVERNED_DEFINITION_FOUND`
- Readiness consequence: `READY_FOR_F05_R1` is not available.

## D1-D6 classification

| ID | Required upstream definition | Classification | Recovered governed content | Exact content not recovered |
|---|---|---|---|---|
| D1 | `trailing_20d_total_return` | `PARTIAL_DEFINITION_ONLY` | Required raw input name, snapshot cutoff constraint, universe-relative subtraction, cross-sectional percentile use, and downstream weight are present. | Exact endpoints and inclusivity, observation count convention, input price basis, arithmetic and units, non-trading treatment, dividend treatment, and CA adjustment are not defined. |
| D2 | `trailing_60d_total_return` | `PARTIAL_DEFINITION_ONLY` | Required raw input name, snapshot cutoff constraint, universe-relative subtraction, cross-sectional percentile use, and downstream weight are present. | Exact endpoints and inclusivity, observation count convention, input price basis, arithmetic and units, non-trading treatment, dividend treatment, and CA adjustment are not defined. |
| D3 | `eligible_universe_equal_weight_return` | `PARTIAL_DEFINITION_ONLY` | Historical eligible membership is the same-snapshot starting population; low or missing coverage may not silently remove a member; the scorer expects a supplied eligible-universe return scalar on each company row. | The code does not enforce a shared scalar identity. Aggregation arithmetic, rebalance timing, observation synchronization, and divisor behavior for missing, suspended, or CA-review members are not defined. |
| D4 | `turnover_or_volume_acceleration` / `turnover_acceleration` | `PARTIAL_DEFINITION_ONLY` | A supplied turnover-acceleration scalar is named, transformed cross-sectionally, and receives the recognition-velocity transform's existing internal `0.20` subweight. | Base measure, numerator and denominator windows, ratio/difference/log form, and zero, gap, suspension, and CA handling are not defined. A separate validation-contract turnover field is also open, but it is corroborative ambiguity rather than authority for the F05 formula. |
| D5 | total-return, price-adjustment, dividend, and CA semantics | `PARTIAL_DEFINITION_ONLY` | Price-control artifacts require evidence-backed CA flags/factors and prohibit inferring or fabricating them; raw price is not canonical. | No governed dividend field, total-return formula, CA factor set for the W1 interval, or factor application timing is available. |
| D6 | missing/suspended W1 denominator treatment | `PARTIAL_DEFINITION_ONLY` | Official rules prohibit silent omission and preserve the historical eligibility denominator for coverage accounting. | No arithmetic rule defines NA/stale/zero treatment, suspension handling, CA-review handling, or benchmark divisor adjustment. |

The 21/61 observation checks in the coverage artifact are availability diagnostics only. They do not close D1 or D2 and do not define “20d” or “60d.” Conventional finance practice and synthetic fixtures were not promoted into model semantics.

## Governed evidence readback

| Artifact | Exact identity | Material evidence |
|---|---|---|
| `control/core_b/M3TOP3-FEATURE-SCHEMA_v1.0_WORKING.yaml` | blob `2550f781c2a901c0faada95dfc4a788503ec669b`; SHA256 `13dac24c93af5a160e37998bc7b0ee9a5b33a6cdd10132f983e72f88b84eff6f` | Lines 22-34 bind winsorization, percentile, missing, and leakage discipline; lines 177-211 name the F05 raw inputs and downstream transform. |
| `tools/m3top3/features_v1.py` | blob `35104a7384c3ee6175136e95dded7f3237d69435`; SHA256 `d7c48767a05f5fd883e8619a06a25c019be23e9b5dc464ca75014056253a2882` | Lines 130-146 consume supplied return/benchmark/turnover scalars; they do not construct the upstream series. |
| `tools/m3top3/configs/m3top3_v1.0.json` | blob `043bf24bc8c838a8060360e86614cf5bfefc9145`; 2,426 bytes; SHA256 `eecde22a7744cff505c624bb6f0bdb11714352a122632238ea68d9cd0fbacb98` | F05 weight remains 20; no outcome tuning or new formula is authorized. |
| `control/core_b/M3TOP3-MODEL-CONTRACT_v1.0_WORKING.yaml` | blob `a5bc212aa07166db46b38070f54737cb47a7f090` | Lines 17-20 establish the historical eligible population boundary. |
| `control/core_b/M3TOP3-SCORER-CONTRACT_v1.0_WORKING.yaml` | blob `18ecdefbb7f8fddaa3d7189494fab9c00547d59e` | Lines 27-31 prohibit silent omission; lines 135-142 preserve denominator-sensitive official scoring discipline. |
| `control/core_b/M3TOP3-VALIDATION-CONTRACT_v1.0_WORKING.yaml` | blob `41ef43f1c534f15ebbfc22713a971ff3c8b94b29` | Line 55 states `turnover_metric: OPEN_DESIGN_ITEM`. This is only corroborative ambiguity; it is not treated as the governed F05 upstream definition. |
| `control/persona-memory/v1.0/AAA-ASA/review-receipts/M3TOP3_OWNER_REVIEW_ITEM24_PASS_2026-08-22.md` | blob `ad27d7941dde23c58696a8f64a42d126484186d4` | Lines 15-23 bind the exact same-snapshot eligible universe and prohibit silent removal for low/missing coverage. They do not define benchmark arithmetic. |
| `control/m3top3/real-input-replay/v1.0/runs/AAA-M3TOP3-REAL-INPUT-STRICT-PRAGMATIC-20260905-114150-CODEX-01/PRAGMATIC_ESTIMATION_DECISION_CARD.md` | blob `e88f97ead1cd3f5b125838c591b0e079bee23902` | Lines 8-11 record that raw marcap does not define total-return, equal-weight, turnover, lookback, dividend, suspension, or CA semantics. |

## Runtime adapter observation

`RUNTIME_ADAPTER_GAP_CONFIRMED`

At the reviewed revision, `tools/m3top3/providers.py` (blob `ae6b185ccb2d6a4b6dede6e922cdc5f4cc324fe5`; SHA256 `8680bcbcfa4c40112741567e519b45d4c31615ad02c50679d52b8e4206ec2ab2`) defines optional Volume/Stocks fields at lines 96-108, but the DuckDB Parquet adapter at lines 133-151 requires/selects only Date, Code, and OHLC and returns Volume/Stocks as null defaults; Amount is not exposed. The bound raw Parquet contains Volume, Amount, and Stocks. Exposing those already-present fields is a bounded, semantic-neutral engineering candidate for a separately authorized stage; no code was changed here.

## Narrow decisions required before F05-R1

1. D1/D2: endpoints, inclusivity, price basis, total-return/dividend/CA semantics, and non-trading handling.
2. D3/D6: equal-weight aggregation, synchronization, and denominator treatment for missing, suspended, and CA-review members.
3. D4: base measure, windows, acceleration transform, and zero/gap handling.
4. CA: evidence-backed adjudication and any admissible factors for GST and 엑시콘.
5. Engineering authorization, after semantic decisions, to expose the required existing raw fields through the runtime adapter.

No feature weight, scorer transform, saturation rule, PIT rule, eligibility rule, code, or configuration was changed.
