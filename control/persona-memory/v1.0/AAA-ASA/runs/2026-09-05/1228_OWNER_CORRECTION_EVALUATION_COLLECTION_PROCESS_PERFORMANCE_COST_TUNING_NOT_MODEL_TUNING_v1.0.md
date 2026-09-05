# Owner Correction — Evaluation/Collection Process Performance-Cost Tuning, Not Model Tuning

PROJECT = AAA
PRODUCT = ASSET AGENT ASA
CURRENT_PERSONA_LOCK = AAA-ASA (ASA)
DATE_KST = 2026-09-05 12:28 KST
RECORD_CLASS = OWNER_CORRECTION / CONTINUITY
AUTHORITY_SOT = FALSE

## Owner correction

Owner clarified that the intended tuning target is **not M3Top3 model tuning**. The target is the **performance and cost efficiency of the evaluation / evidence collection / PIT reconstruction / feature materialization / validation process itself**.

Owner text:
> 아 아뇨 모델 튜닝이 아니라 평가/수집 프로세스의 성능/비용 튜닝입니다.

This supersedes any ASA wording that framed the requested telemetry primarily as model-tuning evidence.

## Operational implication

The active real-input Replay should be used as an empirical calibration run for the research/evaluation pipeline. Preserve the model semantics, scorer, weights, and outcome firewall; instrument the process around them.

Minimum process telemetry to collect where measurable:

1. SOURCE RETRIEVAL
- source/provider route
- request/search/fetch count
- successful source-hit count
- duplicate/cache reuse count
- bytes read/downloaded
- latency and retry/backoff
- failure/no-evidence reason

2. EXTRACTION / PIT MATERIALIZATION
- raw facts inspected/extracted
- OBSERVED / DERIVED / ESTIMATED / MISSING counts
- cutoff-safe admitted values
- TIME_UNVERIFIED / POST_CUTOFF / conflict rejects
- transform success/failure counts
- elapsed active time by feature/source route

3. ADMISSION / FEATURE YIELD
- admitted feature blocks by F01-F09
- rows newly made scoreable
- scoreable-coverage uplift per work unit
- feature/source route responsible for uplift

4. VALIDATION / REWORK
- tests/reviews executed
- findings/reopens
- correction/revalidation time
- repeated validation avoided/reused where authorized

5. COST / THROUGHPUT
- wall time, active time, wait/block time, rework time
- worker concurrency
- token/CRU/cost proxy only when instrumented; otherwise NOT_INSTRUMENTED
- admitted PIT values per minute
- scoreable rows gained per minute
- source attempts per admitted value
- source documents per scoreable row
- token/CRU per admitted value or scoreable row when measurable
- EWU/CRU efficiency when measurable

6. VALUE-OF-INFORMATION / ROUTE EFFICIENCY
- marginal scoreability/coverage gained by each feature/source route
- time/cost spent for that gain
- route-switch trigger after bounded no-evidence attempts
- no-evidence-loop and duplicate-work counts

## Required derived efficiency metrics

At minimum, if denominators exist:
- RETRIEVAL_HIT_RATE = useful source hits / retrieval attempts
- PIT_ADMISSION_YIELD = cutoff-safe admitted values / candidate extracted values
- SCOREABILITY_YIELD = newly scoreable company-window rows / work batch
- COVERAGE_GAIN_PER_ACTIVE_HOUR
- ADMITTED_VALUES_PER_ACTIVE_HOUR
- SCOREABLE_ROWS_PER_ACTIVE_HOUR
- RETRY_RATE
- REWORK_RATIO = rework time / elapsed or active time, with denominator stated
- WAIT_RATIO = wait/block time / elapsed time, with denominator stated
- COST_PER_ADMITTED_VALUE and COST_PER_SCOREABLE_ROW only when cost/token/CRU is instrumented

## Tuning objective

Use these measurements to improve **how the project researches, fetches, transforms, admits, validates, caches, parallelizes, and stops work**. Do not use this correction to change model weights/features or optimize historical model outcomes.

The desired loop is:

PROCESS RUN -> MEASURE TIME/COST/YIELD -> IDENTIFY EXPENSIVE LOW-YIELD STEPS -> CHANGE COLLECTION/EVALUATION ROUTE -> NEXT RUN CALIBRATION

Examples of allowed process tuning questions:
- Is F05 price-derived materialization much cheaper per scoreable row than historical consensus retrieval?
- Which source route has the highest cutoff-safe admission yield?
- Where do retries/backoff consume time without evidence gain?
- What can be cached/reused across W1-W8 without violating PIT?
- Which steps parallelize safely and which create coordination/review overhead?
- When should a missing-data search stop and switch to MISSING/ESTIMATED/alternative route?

## Relation to current execution request

The current request already requires counts/timing for Git reads, external source requests, retries, execution, tests and review, and requires token/CRU to remain NOT_INSTRUMENTED if unavailable. This correction strengthens that generic telemetry into a process-performance/cost calibration objective.

Do not interrupt an already-running Strict Replay merely to retrofit unavailable historical telemetry. Apply the richer ledger prospectively from the next measurable step/checkpoint.

MODEL_TUNING_AUTHORIZED = FALSE
PROCESS_PERFORMANCE_COST_TUNING = OWNER_INTENT_CONFIRMED
OWNER_ACTION_REQUIRED = FALSE
