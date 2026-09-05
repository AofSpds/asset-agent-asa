# Strict Real Input-to-Score Trace — Pre-Review Candidate

This checkpoint proves the candidate path mechanically; it is not the final actual replay receipt. The actual
score-and-seal command remains gated on an exact candidate commit and affected-only review.

## Immutable predecessor boundary

- predecessor head: `79b46dc1f63f1cd215cc0ebc0c91b4ec09e7dc71`
- predecessor ZERO_SCOREABLE output tree: `1d73cc942a3524571ea214724c887c3964dca13f`
- predecessor executable bundle: `M3TOP3-EXECUTABLE-BUNDLE-SHA256:82266d51a64382cbd34ee68872a3cd3e3f640c6ff438e84416906f8b8a8ab9c0`
- preserved config SHA-256: `eecde22a7744cff505c624bb6f0bdb11714352a122632238ea68d9cd0fbacb98`
- old scorer, feature transforms, weights, missingness, guards, coverage runner and results: no repository-object change

The successor uses a new executable bundle identity because it adds an adapter and a two-phase CLI. That new
identity does not imply a model, scorer, feature, weight or config change.

## Leaf-to-feature trace

Raw custody and value evidence are separate. `SOURCE_MANIFEST.json` contains no value or metric payload. The
feature sidecar contains eight immutable leaves for `W1|KRX:005290|F02_NUMERIC_BUSINESS_INFLECTION`:

- four `OBSERVED` decimal leaves: revenue/current, revenue/prior, operating_profit/current, operating_profit/prior;
- four `DERIVED` transform-control leaves: each metric's `change_mode` and `operator_id`;
- zero estimated leaves.

Every observed leaf binds the official KIND HTML SHA-256 and an exact line locator. Every derived control leaf
binds its two numeric leaf IDs, the explicit `RELATIVE` method, and the frozen feature-input registry object.
The importer resolves each JSON Pointer into the constructed block before it emits sorted `consumed_fields` and
matching `consumed_value_provenance`. Audit-only state is not copied into scorer input.

## Candidate score trace

The focused integration execution retained all 57 W1 INCLUDE rows and produced:

| Item | Candidate result |
|---|---:|
| U127 outer rows | 127 |
| W1 scorer rows | 57 |
| scored rows | 1 |
| `REPLAY_DATA_INSUFFICIENT` rows | 56 |
| proven / unresolved outer exclusions | 8 / 62 |
| available / missing feature blocks | 1 / 512 |
| score coverage | `1/57 = 0.01754385964912280701754385965` |
| scored company | `KRX:005290` |
| F02 score / final score | `50` / `50.00` |
| score status | `PROVISIONAL_MISSING_FEATURES` |
| ranking status | `INCOMPLETE_COVERAGE` |

The two calculated relative changes are `0.07273094951360781366485873046` for revenue and
`0.09671897289586305278174037090` for operating profit. Because only one company has F02 inputs, each robust
cross-sectional percentile is `50`; this is a mechanically expected singleton result, not evidence of model quality.
There is no official Top3/Top10 at `1/57` coverage. The outcome cohort policy is separately named
`ALL_SCOREABLE_PRECOMMITTED_NO_SUBSTITUTION` and is sealed before any future price file is opened.

## Outcome boundary

`score-and-seal` accepts no price argument. It writes the 57-ID denominator, all 57 result identities, input and
score hashes, W1 WM-v1.1 tuple, coverage state and nonempty measurement cohort using exclusive-create, fsync and
readback verification. Only the independent `measure-outcomes` phase accepts price paths. It verifies the durable
seal first, then binds exact 2024–2026 file bytes and opens the 2024 values.

The outcome path may calculate only explicitly labeled raw-unadjusted diagnostics. MAE return remains unmeasured
because its formula is open. Corporate-action comparability, price-canonical status, official MFE rank, primary hit
and critical-miss metrics remain unverified or unmeasured unless exact evidence closes them.
