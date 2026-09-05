# M3Top3 Process Calibration Run PC1 — Fully Instrumented W1 Exploratory Source Batch Execution Request

PROJECT = AAA
PRODUCT = ASSET AGENT ASA
FROM_PERSONA = AAA-ASA (ASA)
TARGET_PERSONA = AAA-PMO-ORCHESTRATOR (PMO)
PACKET_ID = AAA-M3TOP3-PROCESS-CALIBRATION-PC1-W1-SOURCE-BATCH-v1.0-20260905
DATE_KST = 2026-09-05 14:20 KST

## 0. Purpose

This successor run is NOT a model-tuning run. Its primary purpose is to measure and improve the performance/cost of the evaluation pipeline itself:

source discovery → source acquisition → PIT/provenance admission → feature materialization → scoring → sealing/outcome → affected validation.

The previous real-input run proved the path can produce a real score and raw outcome, but it also showed that the expensive part is not final scoring. This run therefore becomes the first fully instrumented process-calibration benchmark.

Do not restart G1/G2/G3 exhaustive closure. Do not retune M3Top3-v1 weights/features/scorer. Do not reopen old ZIP recovery, 514-row exhaustive eligibility closure, 17,272-slot blanket annotation, full-market CA, or unchanged full validation suites.

## 1. Predecessor accepted state

Predecessor run:
`AAA-M3TOP3-REAL-INPUT-STRICT-PRAGMATIC-20260905-114150-CODEX-01`

Preserved report branch:
`task/aaa/m3top3-real-input-replay-20260905`

Preserved report HEAD:
`a7b173cf28dc287e1e619e723e938b9bc2c3fd9e`

Reviewed code candidate:
`c15cbfa9bbedcb3b388b9d101b269ced2fc83bc5`

Score/seal preservation commit:
`0dfef7b81566e6ec018994d5597f3f8f923944d1`

Executable bundle:
`M3TOP3-REAL-INPUT-EXECUTABLE-BUNDLE-SHA256:4d828c0308bf892718832e9cb02d87ee7716b9b62c28d643b69b424b5f2b6a4a`

Predecessor terminal state:
`PARTIAL_NONEMPTY_SCORE_ONLY`

Empirical predecessor measurements:
- wall start→outcome end ≈ 2h 12m 46.43s
- source discovery/open/fetch attempts = 18
- admitted official source documents = 1
- successful Strict scoreable rows added = 1
- final score-and-seal command ≈ 1.86s
- final outcome command ≈ 8.14s
- test-case executions across implementation/fix/recheck = 585
- runtime package install attempts = 2, including one sandbox-network denial
- token/CRU and active/wait split = NOT_INSTRUMENTED

Interpretation boundary:
- one admitted document from 18 heterogeneous discovery/open/fetch attempts gives only a crude admission-per-attempt proxy (~5.6%), not a statistically stable route yield.
- the final score/outcome commands themselves were seconds, so end-to-end latency is dominated by acquisition/implementation/review overhead rather than final scoring compute.
- 585 test executions are an observed process-cost signal, not proof that all were unnecessary. The next run must separate mandatory fresh input review from code-validation work that can be reused when executable bytes are unchanged.

## 2. Scope and scientific status

This run uses W1 only and is explicitly:
`EXPLORATORY_PROCESS_CALIBRATION_AFTER_W1_OUTCOME_EXPOSURE`

Any new W1 backfill must NOT be presented as untouched confirmatory v1 evidence.

Primary process objective:
measure which source/feature routes produce cutoff-safe admitted values and new scoreable rows per unit time/attempt/rework.

Secondary execution objective:
increase W1 Strict scoreable rows using only defensible OBSERVED/DERIVED PIT inputs under the existing model semantics.

No Pragmatic estimated input is authorized by this packet.
No model semantic change is authorized.
No PIT semantic change is authorized.
No release/promotion/production effect is authorized.

## 3. Frozen source batch

Do not broaden the W1 batch beyond these five work items in PC1:

1. `KRX:003160` — W1 cutoff-safe F02 official-source candidate.
2. `KRX:025560` — W1 cutoff-safe F02 official-source candidate.
3. `KRX:031980` — W1 cutoff-safe F02 official-source candidate.
4. `KRX:036200` — W1 cutoff-safe F02 official-source candidate.
5. `KRX:005290` — exact W1 corporate-action/comparable-price evidence only, for assessing raw→contract-exact outcome-upgrade cost.

For items 1–4:
- do not assume the filing exists;
- do not assume period/unit/consolidation basis;
- if not cutoff-safe or not comparable, leave MISSING/NA;
- no value invention or substitute-company reuse.

For item 5:
- it does not add a scoreable row;
- it is retained as a separate CA/outcome-route cost calibration lane;
- if contract-exact comparability cannot be established within the bounded route, preserve raw diagnostic only and stop that lane.

## 4. Code and validation freeze

Default rule:
reuse the exact predecessor executable bundle byte-for-byte.

If the executable bundle remains unchanged:
- do NOT rerun the predecessor 71/71 code campaign merely because new source/sidecar data were added;
- do NOT repeat the 585 historical test-case executions;
- perform fresh checks only on new source bytes, sidecar schema, PIT/provenance admission, deterministic input hash, score/seal identity, outcome comparability, and any data-dependent guard affected by the new material.

If code mutation becomes unavoidable:
- stop that mutation lane before applying it;
- classify the defect and exact affected surface;
- either use a semantics-neutral bounded correction under existing authority or escalate if model/PIT semantics would change;
- only the changed code surface receives affected validation.

Reusing prior code validation does NOT validate new source data. New data/lineage always require fresh admission checks.

## 5. Mandatory instrumentation artifacts

Create from run start, not retroactively:

1. `PROCESS_EFFICIENCY_LEDGER.jsonl`
2. `PROCESS_METRIC_DEFINITIONS.json`
3. `PROCESS_CHECKPOINTS.jsonl`
4. `PROCESS_ROUTE_SUMMARY.json`
5. `PROCESS_COST_CALIBRATION_AND_TUNING_REPORT.md`

Ledger event minimum fields:
`run_id, checkpoint_id, stage, route_id, source_domain, feature_id, window_id, company_id, attempt_no, started_at, ended_at, wall_ms, active_ms_if_measurable, wait_ms_if_measurable, outcome, cache_state, bytes_if_measurable, source_hash_if_available, pit_candidate_delta, pit_admitted_delta, admitted_value_delta, scoreable_row_delta, retry_reason, duplicate_reason, blocker_or_route_switch_reason`.

Never encode unavailable telemetry as zero. Use `NOT_INSTRUMENTED`.

## 6. Mandatory checkpoints

### P0 — BASELINE FREEZE
Before material work:
- RUN_ID / branch / worktree / exact predecessor / executable bundle
- frozen five-item worklist
- planned route order
- planned P50/P90 by stage
- worker count and concurrency
- initial scoreable baseline = W1 1/57
- metric definitions and counters = zeroed only where true counters, not missing telemetry

### P1 — FIRST 30 MINUTES
Return:
- route attempts
- useful hits / duplicate hits / unusable hits
- PIT candidates / admitted values
- first newly admitted source or exact failing stage
- scoreable row delta
- elapsed wall
- active/wait if measurable
- cache reuse observed
- no-evidence repeats

### P2 — FIRST NEW INPUT→SCORE SUCCESS
For the first newly scoreable row after baseline:
- discovery time
- fetch/open time
- parse/transform time
- PIT/provenance admission time
- sidecar materialization time
- scoring/seal time
- validation time
- attempts consumed
- admitted values created
- `marginal active minutes / scoreable row` if active time is measurable

### P3 — FIVE-ITEM BATCH TERMINAL
Per item and per route:
- attempted / found / duplicate / unusable / cutoff-failed / admitted
- bytes and hashes if measurable
- retries
- cache hits
- PIT admission yield
- transformation yield
- scoreable row gain
- CA outcome-upgrade result for item 5
- elapsed/active/wait/rework
- explicit terminal reason for every unresolved item

### P4 — VALIDATION CLOSE
Record:
- exactly which fresh checks ran
- prior validation reused and its exact byte identity
- new data/lineage checks
- findings by severity
- rework/recheck count
- validation active time
- code-test executions in this run
- avoided duplicate full-suite reruns

### P5 — POST-RUN CALIBRATION
Produce:
- plan vs actual
- source route ranking by useful yield
- feature route ranking by scoreability gain
- retry/duplicate/cache statistics
- admission yield
- scoreable rows per wall/active hour
- validation/rework ratio
- high-cost/low-yield lanes
- low-cost/high-yield lanes
- recommended parser/cache/concurrency/source-order changes
- exact changes to apply to the next Window run
- expected savings range and confidence, based only on measured evidence

## 7. Process metrics

At minimum compute when denominators exist:

`RETRIEVAL_HIT_RATE = useful_source_hits / retrieval_attempts`

`PIT_ADMISSION_YIELD = pit_admitted_values / pit_candidate_values`

`TRANSFORM_SUCCESS_RATE = transformed_usable_values / admitted_source_values`

`SCOREABILITY_GAIN = new_scoreable_rows - baseline_scoreable_rows`

`SCOREABLE_ROWS_PER_WALL_HOUR`

`SCOREABLE_ROWS_PER_ACTIVE_HOUR` if active time is instrumented

`COVERAGE_GAIN_PER_WALL_HOUR`

`RETRY_RATE`

`CACHE_HIT_RATE` where caching exists

`DUPLICATE_FETCH_RATE`

`VALIDATION_REWORK_RATIO`

`NO_EVIDENCE_REPEAT_COUNT`

`ROUTE_SWITCH_COUNT`

`TOKEN_OR_CRU_PER_SCOREABLE_ROW` only if platform telemetry exposes the numerator; otherwise NOT_INSTRUMENTED.

Do not optimize for document count alone. The primary efficiency unit is decision-relevant evaluation progress.

## 8. Route-control rules

- same route + same failure + no new evidence twice → no third identical retry; switch/NA/terminalize.
- exact duplicate URL/content hash → do not refetch unless a justified freshness check requires it.
- cache parsed official source bytes and normalized extraction keyed by content hash + parser version.
- use one parser implementation for same-format KIND/KRX disclosures; do not hand-build a new parser per company.
- source-route discovery and parsing may run in parallel only where they do not race on shared output.
- default bounded authoring workers: max 2 plus PMO assembly.
- no new provider, paid data, credentials, custody expansion, or broader network quota without Owner decision.

## 9. Exit conditions

PC1 is COMPLETE when:
1. all five work items have terminal dispositions;
2. instrumentation artifacts P0–P5 are complete;
3. any new Strict scoreable rows and CA/outcome upgrade are preserved without overstated claims;
4. process tuning report gives concrete next-run changes.

PC1 may finish with zero new scoreable rows if every source route is truthfully terminalized. That is a process-calibration result, not model-performance completion.

Do not expand beyond five items merely to improve the apparent yield.

## 10. Next-run rule after PC1

After PC1, ASA/PMO shall use `PROCESS_COST_CALIBRATION_AND_TUNING_REPORT.md` to design the next Window run.

Preferred next benchmark:
- a precommitted W2 Strict source batch;
- selection rule frozen before any W2 future outcome access;
- tuned parser/cache/concurrency/source ordering applied;
- compare PC1 vs W2 on wall time, attempts, admission yield, scoreability gain, validation overhead, and cost proxies.

The purpose is to prove that the evaluation process itself is becoming faster/cheaper while preserving evidence quality.

OWNER_ACTION_REQUIRED = FALSE within the bounded existing source/provider/semantic scope.
MODEL_SEMANTIC_CHANGE_AUTHORIZED = FALSE.
PIT_SEMANTIC_CHANGE_AUTHORIZED = FALSE.
PRODUCTION_RELEASE_AUTHORIZED = FALSE.
