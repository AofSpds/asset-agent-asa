# SEM-001 v0.4 Acceptance Contract

## Authority and identity

- Target identity: `R-WP4-03_RUNTIME_CANDIDATE_v0.4`.
- The frozen local v0.2 candidate and its `NO_GO` receipt remain immutable predecessor evidence.
- The authoritative Git v0.3 closeout candidate is reopened as `NO_GO_FOR_SEM001` and also remains immutable. It must not be edited, relabeled, or reused as v0.4 evidence.
- Authoritative lineage transition recorded by PMO: the v0.4 patch must be a descendant of validated runtime `ea52bde2ed65c46f3e797f640b60dd9741aa8fe1` and governed branch/evidence head `3d75dab93d31b20f2f4d42de38cbc6aae96a6ccd` (tree `6980020494b3cbbda6b74b6dcad07de288f194d2`), not a commit made from the older local 4fff-based candidate tree. The final receipt must prove ancestry and bind the authoritative materialization under `remediation/r_wp4_03_git_authoritative`.
- The local `runtime_checkout` tree is retained only as the legacy Top3 semantic reference for the independent behavioral tests; it is not the authoritative v0.4 Git parent.
- Validation scope is independent internal engineering/control validation. `IVA_EXECUTION_PARTICIPATION=NONE`.
- This correction restores the already-approved Top3 semantic contract. It creates no model-semantic, Official, Golden, Full Replay, Freeze, Promotion, Release, Production, alpha, or predictive-performance authority.

## Exact result-view contract

For an admitted eligible ranking set `E` and `K = min(3, |E|)`:

| Field | Required population and meaning |
|---|---|
| `ranked` | Every member of `E`, exactly once, contiguous ranks `1..|E|` |
| `top3` | Exact projection `ranked[:K]` |
| `full_universe_outcomes` | One outcome for every member of `E`, exactly once |
| `full_universe_outcome_count` | Exactly `|E|` |
| `selected_top3_outcomes` | Exact outcome projection for `top3`, in rank order |
| `selected_top3_outcome_count` | Exactly `K` |
| `outcomes` | Backward-compatible historical Top3 outcome view; byte-semantic equality with `selected_top3_outcomes` |
| `outcome_count` | Exactly `K`, the count of `outcomes`, not `|E|` |
| `metrics` | Historical Top3 metric view computed from `outcomes` only |
| `selected_top3_metrics` | Explicit versioned Top3 metric view; semantic equality with `metrics` |
| `full_universe_metrics` | Separately named full-`E` accounting/diagnostic metric view; it must never replace or alias `metrics` |

The legacy `metrics` object retains its historical keys and formulas without requiring new embedded metadata. Population identity is expressed by the separately named views and these immutable result-level semantic identity fields:

- `result_contract_version`
- `selected_top3_metrics_view_version`
- `full_universe_view_version`

All three version values must be included in `validation_run_identity_payload`, the run lineage payload, and the committed full-run manifest. Changing any one must change `validation_run_id`. The result-contract schema may remain `m3top3-validation-result-v3`, while the governed candidate freeze/evidence identity is v0.4.

## Frozen legacy Top3 formulas

Let `T = outcomes`, the selected Top3 outcome rows.

- `valid_return_count = count(row.return_ratio is not None for row in T)`
- `mean_return = arithmetic mean of non-null return_ratio in T`, otherwise `null`
- `median_return = median of non-null return_ratio in T`, otherwise `null`
- `win_rate = count(return_ratio > 0) / valid_return_count`, otherwise `null`
- `mean_mfe_return = arithmetic mean((mfe / entry) - 1)` over rows in `T` with non-null `mfe` and `entry`, otherwise `null`

The formulas do not filter on `outcome_validity`; this preserves the validated parent behavior for diagnostic RAW/CA-pending outcomes. A pending or missing non-Top3 outcome may change the full-`E` diagnostic status but must not erase or alter otherwise computable Top3 metrics.

`full_universe_metrics` may withhold full-`E` aggregate values when any full-`E` outcome is pending, but it must still reconcile:

- `eligible_count = |E|`
- `outcome_record_count = |full_universe_outcomes|`
- `valid_outcome_count + pending_outcome_count = |E|`

## Independent fail-closed verification

Immediately before publication, the runtime verifier must independently reject with exit `3`:

1. `outcomes != selected_top3_outcomes` or either differs from the Top3 outcome projection: `TOP3_PROJECTION_MISMATCH`.
2. `outcome_count != selected_top3_outcome_count != K`: `TOP3_PROJECTION_MISMATCH`.
3. Full-`E` missing, extra, duplicate, or identity-drifted outcomes: the existing full-outcome integrity codes.
4. Any stored Top3 metric value or count that differs from an independent recomputation over `outcomes`: `METRIC_DENOMINATOR_INTEGRITY_FAILURE`.
5. `metrics != selected_top3_metrics`: `METRIC_DENOMINATOR_INTEGRITY_FAILURE`.
6. Any full-`E` accounting mismatch: `METRIC_DENOMINATOR_INTEGRITY_FAILURE`.
7. Missing or mismatched result/view versions, or a run ID not recomputed from the complete version-bound identity payload: existing canonical `RUN_ID_LINEAGE_MISMATCH` with exit `3`.
8. RAW or pending data labeled `VALIDATION`, or any Official/Golden/Replay attempt: existing authority exit `4` codes.

## Required independent regression cases

| ID | Required assertion |
|---|---|
| `SEM-001-A` | Four eligible returns `0.1, 0.2, 0.3, -0.9`: legacy `metrics.mean_return=0.2`, `win_rate=1`, while full `E` remains four rows |
| `SEM-001-B` | The fourth, non-Top3 outcome is pending: Top3 metrics remain computable and unchanged |
| `SEM-001-C` | `outcomes` and `selected_top3_outcomes` are the same exact three-row projection; `full_universe_outcomes` contains all four |
| `SEM-001-D` | Replacing `outcomes` with full `E` is rejected before publication with exit `3` |
| `SEM-001-E` | Forging a Top3 metric value is rejected before publication with exit `3` |
| `SEM-001-F` | `OutcomeBuilder.build`, `RankingEngine.rank`, and the diagnostic scorer behavior remain unchanged from the validated parent |
| `SEM-001-G` | Official/Golden/Replay and RAW-as-VALIDATION claim locks remain fail-closed |
| `SEM-001-H` | A pending Top3 member preserves legacy non-null filtering and does not import non-Top3 rows into Top3 metrics |
| `SEM-001-I` | Result/view versions are present in run identity; changing any version changes `validation_run_id`; forged identity is rejected |
| `SEM-001-J` | `selected_top3_metrics` cannot diverge from the backward-compatible `metrics` alias; any drift is rejected before publication |

The executable independent RED/GREEN artifact is `test_sem_001_v0_4_acceptance.py` in this directory. It is outside the runtime tree and must not be copied into the author implementation as self-validation evidence.

## v0.4 evidence gate

Acceptance requires all of the following bound to one new v0.4 freeze receipt:

1. New v0.4 runtime freeze identity and exact runtime manifest; no reuse of the local v0.2 or authoritative Git v0.3 freeze hash.
2. The authoritative `ea52bde...` / `3d75dab...` successor regression discovery passes in full (`261/261` at the v0.4 freeze), and all SEM-001 independent cases pass. The older local candidate's `164/164` result remains predecessor evidence only and is not sufficient v0.4 evidence.
3. Governed 75-case matrix passes without retrospective editing of the frozen matrix contract.
4. All 54 v0.2 mutations remain `KILLED_RED`.
5. A v0.4 successor mutation registry adds at least:
   - `MUT-R03-TOP3-OUTCOME-VIEW`
   - `MUT-R03-TOP3-METRIC-POPULATION`
   - `MUT-R03-RESULT-VIEW-VERSION-IDENTITY`
   and all are `KILLED_RED` by assertion failures. Expected successor total: at least `57/57`.
6. Candidate-bound manifest-last concurrency probes pass on every current authoritative publication surface: snapshot `100/100`, full-run identical `100/100`, full-run conflicting `100/100`, and ledger `100/100`, with raw/unclassified exceptions `0`. The older `ReleaseIdentityRegistry` receipts remain predecessor-only evidence; the v0.4 governed successor surface is the `m3top3-full-run-commit-v3` manifest-last store.
7. Internal engineering/control validation is rebound to the v0.4 freeze and returns `PASS`.
8. Only after item 7 may PMO create the exact Git commit/tree evidence. Generated `__pycache__` and `.pyc` files are excluded.

Any runtime modification after the v0.4 freeze invalidates the freeze and all bound execution evidence.

The frozen `R_WP4_03_CANONICAL_LINEAGE_FULL_UNIVERSE_CONTRACT_v0.1` must not be silently rewritten. A successor clarification/addendum must state `full_universe_outcome_count = ranked_count = eligible_count` and `outcome_count = selected_top3_outcome_count = K`.
