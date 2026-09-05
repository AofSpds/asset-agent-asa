# F05-R1 MODV L1 D0 independent validation journal

- Run: `AAA-M3TOP3-F05-R1-20260905-231028-CODEX-01`
- Role / level: `MODV / L1`
- Validator: `codex:/root/f05_r1_modv_d0`
- Author: `root/f05_r1_author`
- Issued: `2026-09-06T00:26:59+09:00`
- Verdict: **PASS**

## Independence and immutable target

I did not author or edit the implementation, policy, source bindings, F05 input, F02 input, configuration, or any score artifact. I wrote only this journal and the paired MODV receipt. I did not read another validator's journal before freezing these findings, and I did not transfer any prior PASS.

The validated target is exactly:

- D0 commit: `bc327dddfcc2d826a9ef7c4169b2e8c87f4957f8`
- D0 tree: `ae502559ccb3dc3ad76c835f5049f993f6da2d01`
- Bundle identity: `AAA-M3TOP3-F05-R1-D0-bc327dddfcc2d826a9ef7c4169b2e8c87f4957f8-ae502559ccb3dc3ad76c835f5049f993f6da2d01`
- F05 input SHA-256: `8e5c2991eb1c14bede88300a5fd1d648ce263d3e7a3d6a83b31af9b1e3d873f7`
- F02 persisted input SHA-256: `13667596d8e76f10d319f4129a7cba3b890d2575b3cebf33b78a143740bbbf9e`
- Frozen configuration SHA-256: `eecde22a7744cff505c624bb6f0bdb11714352a122632238ea68d9cd0fbacb98`
- Independently reconstructed merged-input hash: `78d540e5e0385104ba21a744e28897762f4d15af25f571de1cc57136882b2500`

The checkout was at the exact D0 commit and tree before validation. The three score-output paths were absent. No production score helper or score CLI was invoked.

## Independent mathematical reperformance

I used Python standard-library `Decimal` plus DuckDB only; the independent recomputation did not import the repository's F05 builder, feature engine, scorer, or score-output helper. It read the hash-bound `marcap-2024.parquet` source and the frozen F05 JSONL directly.

Results:

| Check | Result |
|---|---|
| Exact W1 cohort | PASS — 57 unique `company_id` / KRX code pairs; cohort identity `c72593633c88cb6913c703da626b95d6111c7b0fa5783ccef6d373b2adf8c546` |
| Common session grid | PASS — 61 sessions, 2024-05-16 through 2024-08-09; grid hash `8667d8b63eeaa5332b0c1390dec179c43c692591a7c3db4c5b1a6cf31217a911` |
| Source observations | PASS — 3,477 = 57 × 61 |
| 20-session return | PASS — 57/57 exact matches from 21 observations and the ending 20 `ChangesRatio / 100` factors |
| 60-session return | PASS — 57/57 exact matches from 61 observations and the ending 60 `ChangesRatio / 100` factors |
| Daily field consistency | PASS — maximum absolute reconstructed ratio difference was `0.00500` percentage point, within the bound `0.011` tolerance |
| Turnover acceleration | PASS — 57/57 exact matches for `mean(last 20 Volume/Stocks) / mean(immediately prior 20 Volume/Stocks) - 1` |
| Equal-weight benchmarks | PASS — both horizons matched on all 57 rows using a fixed `/57` denominator, canonical company order, precision 64, and half-even rounding |
| Missingness / shrink | PASS — all 57 rows are `AVAILABLE`; there is no denominator shrink or silent fill |
| Decimal determinism | PASS — the builder binds precision 64, half-even rounding, and canonical reduction order; mutation of global Decimal context is covered by a passing affected test |

The historical scorer key names containing `total_return` are byte-identical aliases of the canonical `market_price_return` values. They do not add dividends or a total-return series.

## Corporate-action semantics

Official custody contained 11 files; every file's actual byte count and SHA-256 matched the custody record. The custody JSON and CA manifest matched hashes `84a53966ca5233b699a8b5448ccd13ceede683dc555304945df76c7ba62d7eb7` and `3fa931f83edb8d5bf3baf493d770cedc1ffa2f4f56ce8aae7a1171ded45fa50b`.

- GST (`KRX:083450`): the official KRX ex-right evidence states base price KRW 21,700 effective 2024-06-26; the source row is Close 21,600, Changes -100, ChangesRatio -0.46. The 2024-07-24 listing evidence states 9,300,515 new shares and 18,618,260 post-listing shares, matching `Stocks` on that date.
- Exicon (`KRX:092870`): the official KRX ex-right evidence states base price KRW 19,470 effective 2024-06-03; the source row is Close 20,400, Changes +930, ChangesRatio +4.78. The listing evidence states 2,202,000 new shares, 13,050,797 post-listing shares, and 2024-07-31 listing; the source row has Volume 814,284 and Stocks 13,050,797.

The independently compounded 60-session return differs from a naive raw-close ratio by `0.3435597977617711092922586086` for GST and `0.03438359607142644089784412897` for Exicon. The frozen input matches the `ChangesRatio` compound result, not the raw-close ratio. The KRX rule evidence expressly states that corporate actions require a separately adjusted base price. No dividend cash flow or inferred/materialized adjustment factor is present.

## Downstream model and axis semantics

The frozen model artifacts are unchanged from the approved composition target:

- `features_v1.py` Git blob `35104a7384c3ee6175136e95dded7f3237d69435`
- `features_v1_narrow_patch.py` Git blob `b9017f5db0fb637c8a449d5ee3cb1c4a05481076`
- `scorer_v1.py` Git blob `2a797ea705eeb1aef330754fb08ff2182297c139`
- config Git blob `043bf24bc8c838a8060360e86614cf5bfefc9145`

Static review and affected tests confirm:

- F05 feature weight remains 20.
- Recognition velocity remains `0.50 × relative-20d percentile + 0.30 × relative-60d percentile + 0.20 × turnover-acceleration percentile`.
- Saturation remains `max(0, velocity - 85)`, optional valuation/diffusion additions only if supplied, and total cap 30. The frozen 57-row input supplies neither optional field.
- Robust percentile behavior remains 5%/95% winsorization, average-rank ties, and deterministic `company_id` tie order.
- The five preserved F02 scores are exactly 0, 50, 87.5, 87.5, and 25 for the bound five identities. With only Business Momentum/F02 and Market Positioning/F05 axes available, the unchanged scorer algebra is `(25 × F02 + 20 × F05) / 45`. Feature coverage is 0.30 for those five and 0.20 for the other 52; the output claim is expressly provisional and exploratory.

## PIT and claim firewall

The input cutoff is exactly 2024-08-09. A recursive forbidden-key scan of the F05 input and independently merged F02+F05 input found zero outcome fields. A direct text scan found no future/outcome/winner/MFE/MAE/entry tokens or post-cutoff August dates. The configuration remains `outcome_tuned: false` and keeps its scientific-firewall list. The score-output helper's claim label is `F02_F05_PROVISIONAL_EXPLORATORY_NO_OFFICIAL_TOP_K`; it hard-disables top-3/top-10 flags in bounded outputs.

## Test and command record

1. Git identity/readback: target commit and tree matched exactly; D0 diff check passed.
2. Model immutability: composition-to-D0 diff for the four frozen model/config files was empty, and all four Git blobs matched approved values.
3. Official evidence readback: KRX/issuer bodies contained the exact GST/Exicon base-price, effective-date, share-count, and listing-date facts; all custody body hashes matched.
4. First independent recomputation attempt: stopped only because the validator script imposed an unapproved diagnostic threshold `compound-vs-naive absolute difference > 0.1` on Exicon. The observed nonzero difference was `0.03438359607142644089784412897`. This was a validator-harness assumption, not a target failure; no artifact was changed.
5. Corrected independent recomputation: PASS after replacing that arbitrary magnitude condition with the semantically relevant condition that compounded and naive values are unequal. All governed equality checks were unchanged and passed.
6. Affected suite: `python -B -X utf8 -m unittest tools.m3top3.tests.test_f05_r1_market -v` — 32 tests run, 32 passed, 0 failed, 0 errors, 0 skipped.
7. Score-output absence/static guard review: all three score outputs were absent; formula and provisional-claim guards were present. No score helper/CLI invocation occurred.
8. Leakage scan: no prohibited token or post-cutoff date hit in `F05_R1_W1_INPUTS.jsonl`.

## Findings and verdict

No MODV blocking or non-blocking finding remains. The exact D0 target passes MODV L1 for the approved F05-R1 mathematical/model scope. This PASS is target-specific, permits no claim beyond the bounded provisional ceiling, and must not transfer to any corrected commit/tree or changed input bytes.
