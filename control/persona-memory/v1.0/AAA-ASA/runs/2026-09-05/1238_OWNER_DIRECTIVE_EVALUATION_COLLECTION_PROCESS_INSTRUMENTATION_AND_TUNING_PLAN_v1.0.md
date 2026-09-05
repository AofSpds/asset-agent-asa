# Owner Directive — Evaluation/Collection Process Instrumentation and Tuning Plan v1.0

PROJECT = AAA
PRODUCT = ASSET AGENT ASA
CURRENT_PERSONA_LOCK = AAA-ASA (ASA)
DATE_KST = 2026-09-05 12:38 KST
RECORD_CLASS = OWNER_DIRECTION / PROCESS_OPTIMIZATION / CONTINUITY
AUTHORITY_SOT = FALSE

## Owner directive

Owner direction received in chat:

> 네 혹시 이번 작업 요청서에 제대로 설계를 안했다면 그 다음엔 철저하게 계측 체크 포인트를 넣고 튜닝 계획을 세우세요.

Interpretation:
- The target of tuning is NOT model weights/features/scorer semantics.
- The target is the evaluation / source collection / PIT admission / feature materialization / validation execution process itself: throughput, latency, retries, rework, compute/token burn, and decision-relevant yield.
- Do not interrupt an already-running current replay solely to retrofit perfect telemetry. Capture non-disruptive measurements from the next available checkpoint.
- For the next execution request, process instrumentation and a post-run tuning plan are mandatory, not optional appendix material.

## Assessment of the current request

The current REAL-INPUT / STRICT-PRAGMATIC request already includes partial instrumentation:
- planned P50/range and EWU by step;
- 30-minute first-return and 60-minute no-input-to-score reporting checkpoints;
- recording Git reads, external source requests, retries, execution, tests, review counts and time;
- worker ceiling, source-document/network-attempt ceilings;
- token/CRU = NOT_INSTRUMENTED when unavailable rather than fabricated;
- two-failure no-evidence route-switch rule.

This is adequate for basic execution telemetry, but NOT sufficient for systematic process performance/cost tuning because it does not yet require a fully linked per-route efficiency ledger, stage yield accounting, marginal scoreability gain, cache/reuse accounting, or mandatory post-run optimization decision table.

## Mandatory checkpoints for the next execution

Checkpoint P0 — BASELINE FREEZE before material work
- task/run identity, exact scope and denominator
- planned stage P50/P90, expected attempts, worker count
- initial route priority and reason
- frozen metric definitions

Checkpoint P1 — FIRST MATERIAL SOURCE / 30 MIN
- attempts by route
- useful source hits vs duplicates vs unusable
- elapsed/active/wait if measurable
- first cutoff-safe admitted value or exact failing stage
- current scoreability gain = rows newly made scoreable

Checkpoint P2 — FIRST INPUT→SCORE SUCCESS
- source acquisition time
- transformation time
- PIT/provenance admission time
- adapter/scoring time
- validation time
- number of admitted values
- scoreable rows added
- marginal active-minutes per added scoreable row

Checkpoint P3 — WINDOW BATCH COMPLETE
- per-feature F01-F09: attempted / admitted / missing / conflict / time-unverified counts
- per-source route: calls, hits, retries, cache hits, bytes if available, active/wait time
- per-stage throughput and queue depth where measurable
- rework/revalidation time
- scoreable coverage gain from baseline

Checkpoint P4 — VALIDATION CLOSE
- changed-surface tests/reviews executed
- findings by severity
- false-start/reopen count
- validation active time and rework multiplier
- duplicate or unnecessary validation detected

Checkpoint P5 — POST-RUN CALIBRATION
- planned vs actual per stage
- active/wait/rework split where measurable
- attempt and retry rates
- admission yield
- scoreability yield
- coverage gain per active hour
- cost/token/CRU per admitted value and per scoreable row where measurable
- top low-yield routes and top high-yield routes
- recommended concurrency/cache/parser/source-order changes
- exact actions to apply to the next Window/run

## Required process metrics

At minimum preserve:
- RETRIEVAL_ATTEMPTS
- USEFUL_SOURCE_HITS
- DUPLICATE_SOURCE_HITS
- RETRIEVAL_HIT_RATE
- RETRY_RATE
- CACHE_HIT_RATE when applicable
- PIT_CANDIDATE_VALUES
- PIT_ADMITTED_VALUES
- PIT_ADMISSION_YIELD
- TRANSFORM_SUCCESS_RATE
- ADMITTED_VALUES_PER_ACTIVE_HOUR
- SCOREABLE_ROWS_ADDED
- SCOREABLE_ROWS_PER_ACTIVE_HOUR
- COVERAGE_GAIN_PER_ACTIVE_HOUR
- ACTIVE_TIME / WAIT_TIME / REWORK_TIME where measurable
- VALIDATION_REWORK_RATIO
- ROUTE_SWITCH_COUNT
- NO_EVIDENCE_REPEAT_COUNT
- token / CRU / cost when platform telemetry permits; otherwise NOT_INSTRUMENTED

## Efficiency ledger

Future execution must produce a machine-readable append-only ledger, suggested name:
`PROCESS_EFFICIENCY_LEDGER.jsonl`

Each event should bind at least:
`run_id, checkpoint_id, stage, route_id, source_domain, feature_id, window_id, company_id_if_applicable, attempt_no, started_at, ended_at, active_ms_if_measurable, wait_ms_if_measurable, outcome, cache_state, bytes_if_measurable, admitted_value_delta, scoreable_row_delta, retry_reason, blocker_or_route_switch_reason`.

## Post-run tuning plan

Future execution must also produce:
`PROCESS_COST_CALIBRATION_AND_TUNING_REPORT.md`

Required sections:
1. baseline plan vs actual
2. highest-yield source/feature routes
3. lowest-yield / repeated-no-evidence routes
4. duplicate fetch / cache opportunities
5. parser/transform automation opportunities
6. concurrency observations and safe next-run ceiling
7. validation/review overhead and unnecessary reruns
8. feature-order recommendation based on scoreability gain per unit effort
9. routes to stop/defer/estimate/missing instead of continue searching
10. concrete changes for next Window, with expected time/cost reduction and confidence

## Route-tuning rule

Do not optimize only for raw collection volume. Primary process objective is decision-relevant evaluation progress.
Prefer routes that increase cutoff-safe admitted features and scoreable coverage per unit active time/compute.
If a route consumes materially increasing effort with no admitted-value or scoreability gain, trigger a route-switch review rather than continuing by inertia.

## Current-run handling

If the current Strict/Pragmatic replay is already running:
- do not restart it merely to add instrumentation;
- capture all non-disruptive observable telemetry from the next checkpoint forward;
- preserve missing fields as NOT_INSTRUMENTED;
- use this run as partial calibration evidence, clearly marking telemetry gaps;
- make the next run the first fully instrumented benchmark.

MODEL_SEMANTIC_CHANGE_AUTHORIZED = FALSE
PIT_SEMANTIC_CHANGE_AUTHORIZED = FALSE
PRODUCTION_RELEASE_AUTHORIZED = FALSE
OWNER_ACTION_REQUIRED = FALSE
NEXT = enforce these checkpoints and tuning artifacts in the next PMO execution request; retrofit current run only non-disruptively.