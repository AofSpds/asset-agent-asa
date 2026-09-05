# F05-R1 MODV L1 D1 independent validation journal

- Run: `AAA-M3TOP3-F05-R1-20260905-231028-CODEX-01`
- Validator: `root/f05_r1_modv_d1`
- Role / level: `MODV / L1`
- Target revision: `D1`
- Target commit: `2700dda2fee8b4f8b6cfab9c075f8b860ffc94f9`
- Target tree: `c98194af223562e440d66c47b57f6696110ced47`
- Bundle: `AAA-M3TOP3-F05-R1-D1-2700dda2fee8b4f8b6cfab9c075f8b860ffc94f9-c98194af223562e440d66c47b57f6696110ced47`
- Findings frozen at: `2026-09-06T01:06:38+09:00`
- Verdict: `PASS`

## Independence declaration

I did not author or edit the D1 target. I did not read another D1 validator journal or receipt before freezing my findings. I did not transfer a D0 verdict. I independently read the approved Owner policy, the approved execution request, `P4_D1_EXACT_TARGET.json`, the bound source/model/control artifacts, the exact F05 input, the persisted F02 evidence, and the raw bound price/CA evidence needed for this MODV scope.

No production score CLI was called and no production score artifact was created. This receipt is one supporting role result and does not by itself open the score gate.

## Frozen-target and source custody checks

- Git resolved the exact D1 commit and tree to the requested values.
- All 34 files declared in `P4_D1_EXACT_TARGET.json` matched both their target Git blobs and current worktree SHA-256 values: `34/34`, zero mismatch.
- `marcap-2024.parquet` read back as 24,572,111 bytes with SHA-256 `b0c38943e67637d5faf88429880092cf0f46a394be39860dd3bcd0b04231bccb`.
- All 11 vendored official issuer/KRX CA bodies matched the exact byte counts and hashes in `F05_R1_OFFICIAL_CA_SOURCE_CUSTODY.json`: `11/11`, zero mismatch.
- Frozen model blobs were unchanged: `features_v1=35104a7384c3ee6175136e95dded7f3237d69435`, `narrow_patch=b9017f5db0fb637c8a449d5ee3cb1c4a05481076`, `scorer_v1=2a797ea705eeb1aef330754fb08ff2182297c139`, and `config=043bf24bc8c838a8060360e86614cf5bfefc9145`.

## Independent actual-data reperformance

I queried 8,607 raw rows for the exact 57 codes through the 2024-08-09 cutoff, selected each company's final common 61-session window, and recalculated all metrics with independent `Decimal` arithmetic rather than calling the F05 builder.

- Every company used the same 61 dates from 2024-05-16 through 2024-08-09.
- 60-day return used 61 observations and exactly 60 `ChangesRatio / 100` daily factors, excluding the first endpoint row from compounding.
- 20-day return used the last 21 observations, 2024-07-12 through 2024-08-09, and exactly 20 daily factors.
- Turnover used `Volume / Stocks` for exactly 20 prior sessions, 2024-06-17 through 2024-07-12, and 20 recent sessions, 2024-07-15 through 2024-08-09.
- All 171 company metrics (57 each of 20-day return, 60-day return, and turnover acceleration) exactly matched `F05_R1_W1_INPUTS.jsonl`.
- The independently summed company-ID-order benchmark denominator was exactly 57. The 20-day mean was `-0.2124153885346208337758748387981210510982875684105824670798651096`; the 60-day mean was `-0.2427557483310895727201166322683066906964043950156641786131060302`. Both canonical and legacy aliases matched on all 57 rows.

## Corporate-action boundary reperformance

For GST (`KRX:083450`) on 2024-06-26, the raw source row was Close 21,600, Changes -100, and ChangesRatio -0.46 percentage points. `Close - Changes` reconstructs the official KRX base price of 21,700. The preceding raw close was 43,300, so the adjacent raw-close ratio would represent the one-for-one bonus discontinuity and was correctly rejected. The 2024-07-24 `Stocks` value was exactly 18,618,260.

For Exicon (`KRX:092870`) on 2024-06-03, the row was Close 20,400, Changes +930, and ChangesRatio +4.78 percentage points. `Close - Changes` reconstructs the official KRX base price of 19,470. The preceding raw close was 20,350, whose naive ratio is not the approved ex-right market-price return. On 2024-07-31, `Volume=814,284` and `Stocks=13,050,797`, yielding exact daily turnover `0.06239343083797870735404128959` under the new listed-share count.

No cash-dividend reinvestment, adjusted-close substitution, heuristic CA factor, or inferred adjustment factor was admitted.

## Unchanged downstream model checks

I independently implemented the frozen 5th/95th linear winsorization and average-rank percentile rule over 57 synthetic vectors, then recomputed recognition velocity as `0.50*pct20 + 0.30*pct60 + 0.20*pctTurnover` and saturation as `max(0, velocity-85)` with the existing cap. All 57 independently expected values exactly matched the inherited F05 engine. The synthetic maximum post-saturation F05 score was 85.

The frozen configuration retains F05 feature weight 20, Market Positioning axis weight 20, and Business Momentum axis weight 25. The exact-five F02 values were independently read from the persisted F02 score bytes and matched `0, 50, 87.5, 87.5, 25` for `003160, 005290, 025560, 031980, 036200`. The bounded combined-view rule remains `(25*F02 + 20*F05)/45`, with five rows at feature coverage 0.30 and combined ranks 1..5; the other 52 remain F05-only at coverage 0.20 with no combined rank. All outward claims remain provisional and explicitly suppress official Top3/Top10 flags.

## P/N matrix

All positive cases P01-P07 passed: exact observation/interval arithmetic, both official CA cases, turnover arithmetic, exact-57 benchmark identity, unchanged F05 percentile/velocity/saturation, and exact-five F02+F05 combination/coverage/rank ceiling.

All negative cases N01-N13 passed in the affected tests or exact static/byte controls: naive CA raw close, wrong identity/date/source/field, future rows, 56/57 shrink, invalid turnover values, duplicate/misaligned/off-by-one sessions, total-return substitution, inferred CA factor, model/config drift, physical-field/scale drift, alias/lineage drift, deficient validation provenance, and output/claim-ceiling drift were rejected.

## Test evidence

Command:

`python -B -X utf8 -m unittest tools.m3top3.tests.test_f05_r1_market tools.m3top3.tests.test_f05_r1_score_outputs -v`

Result: `39 tests`, `0 failures`, `0 errors`, `0 skips`, `PASS`.

## Final disposition

`MODV_L1_D1 = PASS`

There are no MODV findings and no Owner decision item. This PASS binds only the exact D1 commit/tree/input hashes above and cannot transfer to any changed target.
