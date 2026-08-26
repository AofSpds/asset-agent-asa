# M3TOP3 W1 PIT-First EOPT Calibration Plan v1.0

```text
PROJECT = AAA
PRODUCT = ASSET AGENT ASA
CURRENT_PERSONA_LOCK = AAA-PMO-ORCHESTRATOR (PMO)
ARTIFACT = M3TOP3_W1_PIT_FIRST_EOPT_CALIBRATION_PLAN_v1.0
ISSUED_AT_KST = 2026-08-27T06:53:00+09:00
PLAN_STATE = READ_ONLY_EXECUTION_DESIGN_CANDIDATE / NOT_ACTIVATED
GATE_EFFECT = NONE
VALIDATION_CLAIM = NONE
PRODUCTION_AUTHORIZED = FALSE
MODEL_SEMANTIC_CHANGE_AUTHORIZED = FALSE
PIT_SEMANTIC_CHANGE_AUTHORIZED = FALSE
OWNER_ACTION_REQUIRED = FALSE
```

## 0. Executive disposition

Common Guard v1.1 is already durably closed at `100/100 EWU`; this plan does not reopen or repeat A0-R through A5.

The Owner direction to start runtime tuning from PIT is retained, but it does not waive EOPT-G0/G1, historical eligibility, listing/tradability, corporate-action, calendar, publication-cutoff, evidence-lineage, or fail-closed controls.

Current decision:

```text
CLEAN_FULL_W1_FEASIBLE_NOW = NO
BOUNDED_W1_CALIBRATION_DESIGN_FEASIBLE = YES
MEASUREMENT_AUTHORIZED_NOW = NO
MUTATION_AUTHORIZED_NOW = NO
```

The first executable calibration unit, once EOPT-G0 permits measurement, is a separately frozen and independently authorized bounded lineage bundle named `W1-CAL-B24`. It must exercise the pinned original production code path and preserve exact PIT semantics. It is runtime evidence only and cannot create a W1 release, model score claim, Golden/Replay claim, or performance claim.

## 1. Exact recovered W1 identity

The current development registry is byte-bound as:

```text
REGISTRY = W1_W8_WINDOW_REGISTRY_RELEASE_CANDIDATE_v0.1.csv
BYTES = 414
SHA256 = 96d63cc98a01b6332cf9486440e7f3fdaa0ec5a2d605f21bc14a4025b46e69fe
LOCAL_CONCORDANCE = 8_OF_8
AUTHORITY_CLASS = OWNER_RATIFIED_OUTCOME_EXPOSED_DEVELOPMENT_ONLY
CLEAN_HOLDOUT = FALSE
OOS = FALSE
RELEASE_ADMITTED = FALSE
OUTCOME_FREE_BINDING_EVIDENCE = NOT_PROVEN
UPSTREAM_TUPLE_PROVENANCE = OPEN
```

W1 exact tuple:

```text
WINDOW_ID = W1
SNAPSHOT_CUTOFF_DATE = 2024-08-09
ENTRY_DATE = 2024-08-12
WINDOW_END_DATE = 2024-11-08
```

W1 is therefore not calendar Q1. The tuple may be used only with the authority labels above until outcome-free upstream selection/commitment evidence is recovered or a prospective registry is committed before outcomes.

## 2. W1 population and gate state

Nominal W1 population is 127 company-window rows.

Current read-only mechanical projection:

```text
MECHANICAL_ENTRY_OPEN_TRUE = 119
MECHANICAL_ENTRY_OPEN_FALSE = 8
```

Current thin-PIT working labels:

```text
WORKING_ELIGIBLE = 57
INELIGIBLE_BY_TRADABILITY = 8
UNRESOLVED = 62
```

These labels do not close G2 source provenance. Current G2 remains blocked because supplied bytes contain no independently admitted cutoff-safe historical business-priority validity intervals, no complete authoritative listing/relisting/delisting lineage for the relevant subset, and no authoritative eight-row upstream window provenance binding.

Accordingly:

- `57` is not represented as a clean, release-admitted W1 denominator.
- `62` unresolved rows are never silently admitted or deleted.
- `8` mechanically non-tradable rows remain fail-closed.
- Full W1 execution cannot create a model or release claim until G2/G3 and the integrated checkpoint close.

## 3. Original pinned runtime identity

Current observed engineering pin:

```text
OBSERVED_EXECUTION_COMMIT = 6f9ed94e7323e20abf3b19637ecb807e342430f2
OBSERVED_EXECUTION_TREE = 255e9679b4eaa86361191a2e0d84084a6be004a5
```

Relevant exact blobs at that pin:

```text
cli_build_snapshots.py = fee45d71c89cb9282e379d3ef2a894d1906de9c9
cli_run_backtest.py = c88219b9f68cba771d977e6e1db3758fe32b86b3
snapshot.py = b7dd94fdd9727422f478e98e68ebd01ca75a675b
providers.py = a33e8caf8b5f68e34fe6252cd481554331ebc045
outcome.py = 92805a07d4e736d95f50848fc295aaa23c2762a0
backtest.py = ba28ea065308729dadd22e82c76bc509374cfec9
ledger.py = be9c1ad53de5b7f72659a4dd409bc201630e3894
```

Runtime characteristics that must remain unchanged during baseline measurement:

- `PIT-SNAPSHOT -> model_input -> MODEL-SCORE -> ranking/prediction -> VALIDATION/outcome` separation.
- `publication_at <= snapshot_cutoff_at`.
- unresolved eligibility is not READY.
- complete applicable universe `U` is represented, including terminal false rows.
- ranking/prediction/outcome covers eligible subset `E` only.
- Entry is first governed trading-day Open after Snapshot/Window Start.
- Exit is first governed trading-day Open after Window End.
- MFE/MAE use holding rows through Window End.
- fail-closed admission and claim locks remain active.

The following are not yet frozen and are mandatory EOPT-G0/G1 inputs:

```text
EXACT_RUNTIME_CONFIG_BYTES = NOT_YET_FROZEN
EXACT_EXECUTION_LINEAGE_BUNDLE = NOT_YET_FROZEN_FOR_W1_CAL
EXACT_FEATURE_JSONL_BYTES = NOT_YET_FROZEN_FOR_W1_CAL
EXACT_UNIVERSE/DENOMINATOR_BYTES = NOT_YET_FROZEN_FOR_W1_CAL
EXACT_ENVIRONMENT_MANIFEST = NOT_YET_FROZEN
EXACT_COMMAND_LINE = NOT_YET_FROZEN
NO_ACTIVE_WRITER_RECEIPT = NOT_YET_ISSUED_FOR_MEASUREMENT
```

The original runtime remains immutable/default. This plan creates no candidate implementation branch.

## 4. Full W1 feasibility decision

A clean Full W1 run requires all of the following:

1. exact W1 registry bytes and declared authority class;
2. authoritative regular-session calendar bytes and receipt;
3. authoritative Axis-C corporate-action event universe and reconciliation;
4. cutoff-safe historical business-priority and listing/tradability closure for all 127 rows;
5. exact source, feature, price, universe, denominator and lineage manifests;
6. EOPT-G0 PASS;
7. frozen workload/environment/equivalence oracle;
8. no active writer;
9. original-runtime A/A determinism.

At issue time, items 2-6 remain open. Therefore `CLEAN_FULL_W1_FEASIBLE_NOW=NO`.

## 5. Bounded calibration subset: W1-CAL-B24

### 5.1 Purpose

`W1-CAL-B24` is the smallest practical first-pass workload for component attribution and original-runtime A/A measurement. It is not a released historical W1 sample and is not a substitute for Full W1.

### 5.2 Materialization rule

The subset is not materialized in this plan because the exact row-level candidate file and lineage bundle have not yet been rebound on the measurement branch.

When EOPT-G0 permits measurement, materialize deterministically as follows:

1. Start from W1 rows carrying the pre-existing working label `ELIGIBLE` and mechanical Entry Open `TRUE`.
2. Do not treat that working label as G2 proof; set every bundle label to `CALIBRATION_ONLY_NOT_G2_RELEASE_ADMITTED`.
3. Compute `selection_key = SHA256("W1-CAL-B24|96d63cc...e69fe|" + canonical_company_id)`.
4. Sort ascending by `selection_key` and take the first 24 rows.
5. If fewer than 24 rows survive exact identity/hash binding, use all surviving rows. Never pad with unresolved rows.
6. Freeze company IDs, row identities, input hashes, selection keys, selection algorithm version and manifest digest before the first timed run.
7. Prohibit winner, rank, return, MFE, MAE, future earnings, later price path or any outcome-derived selection input.

### 5.3 Exact-path requirement

The current CLI has no company filter. Therefore B24 may be called an exact end-to-end workload only if an independently authorized bounded lineage bundle presents B24 as the complete applicable calibration universe and all normal admission/claim locks remain active.

Otherwise B24 is limited to component-attribution status. A governed Full W1 exact end-to-end A/A run remains mandatory before publishing a scoreable Full W1-W8 runtime forecast.

## 6. Baseline measurement protocol

Measurement remains prohibited until EOPT-G0 PASS.

After G0:

### 6.1 Freeze first

Freeze and hash:

- original commit/tree and exact relevant blob set;
- Python/runtime/dependency versions;
- OS/kernel, CPU model/count, memory and storage class;
- environment variable allowlist and values excluding secrets;
- exact command, working directory and output paths;
- exact W1-CAL-B24 manifest;
- all input bytes and manifests;
- cold/warm definitions;
- repetitions and noise method;
- terminal accounting and timeout policy;
- normative equivalence oracle;
- permitted non-normative differences.

### 6.2 Repetitions

Initial low-cost protocol:

```text
B24_COLD_REPETITIONS = 3
B24_WARM_REPETITIONS = 5
```

Cold means a new process with process-local caches empty. OS page-cache state must be observed and reported; it is not silently claimed cold unless explicitly controlled. Warm means identical consecutive invocations under the same frozen environment with naturally warmed source/page caches and no input mutation.

Report median, P90, hard tail, median absolute deviation and all raw observations. Do not discard outliers without a predeclared mechanical rule.

### 6.3 Full W1 confirmation

Once source gates permit Full W1:

```text
FULL_W1_COLD_REPETITIONS = 2 minimum
FULL_W1_WARM_REPETITIONS = 3 minimum
```

These counts may be increased by a versioned reforecast if variance is too high. They may not be reduced after seeing favorable results without recording the change and reason.

## 7. Mandatory telemetry

### 7.1 Progress/accounting

- overall program progress, current-stage progress, validation closure;
- EWU earned against a frozen denominator;
- CRU raw inputs and normalized CRU once calibrated;
- attempted, completed and blocked company-windows;
- active workers and validators;
- last material progress and blocker counts.

### 7.2 Time

- wall time;
- process active CPU time;
- wait time;
- blocked time;
- rework/revalidation time;
- per-company-window P50/P90/hard tail;
- stage start/end monotonic timestamps.

### 7.3 Source and compute

- retrieval calls, bytes and latency;
- source reuse and cache-hit counts;
- feature JSONL open/read/parse/hash counts and bytes;
- primary feature row-selection time;
- independent shadow-reconstruction time;
- price-release verification calls, bytes hashed and time;
- trading-calendar query calls and time;
- entry/holding/exit price extraction calls, rows and time;
- serialization bytes/time;
- hash calls/bytes/time;
- ledger append/read/fsync time;
- CPU core-time, peak RSS/GB-minute and storage I/O when exposed;
- retries/backoff and fail-closed count;
- validator wall/active/wait and revalidation count.

`NOT_INSTRUMENTED` is preserved as unknown and never converted to zero.

## 8. Bottleneck attribution map

Known hypotheses to instrument, without preselecting a winner:

1. `SnapshotBuilder._build_company` primary selection plus independent shadow reconstruction;
2. full feature JSONL reread/reparse/rehash per company/cutoff;
3. linear feature row scans;
4. repeated `verify_price_release` hashing;
5. repeated trading-calendar queries for the same window;
6. scalar entry/holding/exit price extraction;
7. serial company/window loops;
8. lineage/serialization/hash/ledger overhead;
9. validator/reporting overhead;
10. retry/backoff waste.

Optimization priority is determined only after measured active-time and hard-tail attribution.

## 9. Safe concurrency ladder

```text
LEVEL 0 = 1 worker, deterministic reference
LEVEL 1 = 2 workers
LEVEL 2 = 4 workers
LEVEL 3 = 8 workers, optional only after evidence
```

Advance only when the previous level shows:

- exact normative output equivalence;
- no nondeterministic ordering or serialization drift;
- no source throttling or retry amplification;
- no ledger/write contention;
- no peak-memory breach;
- P50 improvement without unacceptable P90/hard-tail regression.

Company-level read/compute may be parallelized. Normative final ordering and ledger mutation must remain deterministic through a single writer or deterministic merge. Eight-way execution is not presumed safe.

## 10. Exact-equivalence oracle

For identical frozen input, candidate and original must match exactly for:

- admission/fail-closed disposition and exit code;
- PIT decision;
- eligibility/tradability status;
- evidence identity, publication cutoff and provenance;
- source and component digests;
- feature facts and missingness state;
- model input values;
- score arithmetic;
- ranking, ties and Top3 membership;
- window identity and outcome row identity;
- normative serialization, row ordering, counts and manifest digests;
- reproducibility receipt.

No numeric tolerance is introduced for optimization convenience.

Permitted non-normative differences are limited to fields explicitly frozen as telemetry-only, such as monotonic timestamps, wall time, process ID, temporary path, host resource counters and cache statistics. They must not enter normative digests.

Failure disposition:

```text
CANDIDATE_ONLY_REJECT
ORIGINAL_RUNTIME_CONTINUES
NO_PARTIAL_ACTIVATION
```

## 11. EOPT mutation boundary

Strictly prohibited:

- F01-F09 semantics;
- weights, scorer arithmetic, ranking or tie policy;
- PIT cutoff/publication meaning;
- evidence admission or missingness relaxation;
- eligibility/tradability meaning;
- outcome definition;
- fail-closed weakening;
- validation-floor reduction;
- future-outcome backfill;
- Golden/Replay/Freeze/Release/Production claims.

Permitted candidate classes after EOPT-G1 include only semantic-neutral work such as parsed feature indexing, immutable source digest memoization, window-invariant calendar reuse, vectorized/batched price extraction, deterministic concurrency and redundant serialization/hash elimination where the oracle remains exact.

## 12. Promotion criteria

### 12.1 B24 to expanded calibration

Require:

- original A/A exact determinism;
- complete telemetry accounting;
- no unresolved instrumentation critical to the leading bottleneck;
- concurrency level 1 and 2 equivalence proven where attempted;
- measured bottleneck attribution stable across cold/warm runs;
- no semantic or authority deviation.

Then expand to 48 and 96 rows only as component-attribution workloads, using the same deterministic manifest rule and claim ceiling.

### 12.2 Candidate to Full W1

Require:

- EOPT-G1 PASS and mutation-dispatch receipt;
- isolated candidate branch/worktree;
- B24 isolated and cumulative A/B exact equivalence;
- fault-injection/fail-closed equivalence;
- source gates sufficient for a governed Full W1 exact E2E run;
- no active writer;
- original fallback immediately available.

### 12.3 W1 to W2

Require:

- Full W1 original A/A deterministic;
- Full W1 candidate A/B exact-equivalent;
- forecast error and throughput method frozen;
- retry, blocker and hard-tail causes classified;
- candidate benefit reproduced in both cold and warm conditions;
- zero semantic, PIT, evidence or authority deviation.

W2 uses its own exact tuple and a newly frozen manifest; W1 timing is not mechanically copied.

### 12.4 W1+W2 to W3-W8

Require:

- same candidate produces exact equivalence in both windows;
- cost/throughput and hard-tail behavior remain inside predeclared stability bands;
- no window-specific cache dependence or special-case code;
- G1/G2/G3 integrated source and eligibility gates are closed for scale-out;
- cumulative resource forecast and stall watchdog are frozen;
- original runtime fallback remains valid.

## 13. PIT progress versus model performance

Always publish separate state fields:

```text
PIT_COLLECTION_PROGRESS = attempted/completed/blocked evidence-closed rows
RUNTIME_CALIBRATION_PROGRESS = measured workloads and telemetry closure
EOPT_CANDIDATE_STATUS = NOT_STARTED / MEASURED / REJECTED / EQUIVALENT
MODEL_PERFORMANCE_STATUS = NOT_EVALUATED unless separately authorized
GOLDEN_REPLAY_STATUS = NOT_STARTED unless separately authorized
```

Runtime success, higher throughput, completed PIT collection, or an equivalent candidate does not imply predictive improvement.

## 14. WBS, time and compute controls

This plan is not activated, so it creates no new earned EWU. Upon G0 entry, freeze a separate execution baseline before work begins.

Preliminary low-confidence planning ranges, excluding external source/custodian wait:

| Stage | Scope | P50 wall | P90 wall | CRU |
|---|---|---:|---:|---|
| W1-0 | exact manifests, environment and oracle freeze | 0.5-1.0h | 2.0h | NOT_CALIBRATED |
| W1-1 | B24 original cold/warm A/A | 0.5-1.5h | 3.0h | NOT_CALIBRATED |
| W1-2 | telemetry attribution and measured plan | 0.5-1.0h | 2.0h | NOT_CALIBRATED |
| W1-3 | isolated semantic-neutral candidate after G1 | 1-3h | 6h | NOT_CALIBRATED |
| W1-4 | B24 A/B and fault cases | 0.5-1.5h | 3h | NOT_CALIBRATED |
| W1-5 | governed Full W1 original/candidate confirmation | UNKNOWN before baseline | UNKNOWN | NOT_CALIBRATED |
| W2 | W2 extension and W1+W2 stability | UNKNOWN before W1 | UNKNOWN | NOT_CALIBRATED |

Raw CPU, memory, I/O and retrieval measurements calibrate CRU. Unknown is not zero. Reforecast after the first measured segment while preserving the original forecast.

## 15. Validation and stall policy

- no global validation loop;
- no full-repository regression by default;
- exact frozen target and role-scoped checks only;
- parallel first-pass where independent;
- finding freeze and one correction batch by default;
- affected-diff recheck only after dependency closure is proven;
- sealed evidence reuse within exact applicability;
- unchanged evidence is not rerun merely because a new channel/runtime began.

During material execution, issue a progress heartbeat approximately every 10 minutes. If no material progress occurs for approximately 20 minutes: inspect once, retry a failed tool at most once, persist the checkpoint, report the exact gap and terminate. Post-compute seal/readback has an approximate 30-minute hard ceiling.

## 16. Current blockers and resume triggers

```text
G2 = historical business-priority/listing provenance + eight-row window authority
G3 = exact independent KRX CA universe + exact governed regular-session calendar
EOPT_G0 = OPEN / NOT_PROVEN / 1 OF 6
MEASUREMENT = NOT_STARTED
MUTATION = NOT_STARTED
```

Resume measurement preparation only when EOPT-G0 permits it. Resume Full W1 only when source/authority gates permit a complete exact-path run. Do not manufacture missing authority from price observations, current structural seeds or historical workbook labels.

## 17. Source bindings

- Common Guard main merge: `da0e3a4f7b921ee710785f12435a10aa750fcba6`.
- M3Top3 active recovery branch head observed: `0f3b7b0cc0864d9939c670129991fdabca14a90c`.
- W1-W8 post-decision binding candidate: `control/m3top3/recovery/2026-08-26/post-decision-governance/G3_C_CALENDAR_W1_W8_POST_DECISION_GOVERNANCE_BINDING_CANDIDATE_2026-08-26.json`.
- G2 blocker decision: `control/m3top3/recovery/2026-08-26/fast-close-worker-results/G2_B_C_D_SOURCE_PROVENANCE_BLOCKER_DECISION_2026-08-26.json`.
- Entry-tradability projection: `control/m3top3/recovery/2026-08-26/fast-close-worker-results/G3_D_ENTRY_TRADABILITY_SUMMARY.json`.
- Primary queue: GitHub Issue #49; G2 #53; G3 #54.

## 18. Claim ceiling

This plan creates no authority change, validation PASS, EOPT-G0/G1 PASS, Full W1 authorization, model/PIT semantic change, model performance claim, Golden/Replay PASS, Freeze, Champion, Release or Production authority.
