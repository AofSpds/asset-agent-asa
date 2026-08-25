# AAA Execution Progress / Time / Compute Behavior Code v1.0

PROJECT = AAA
PRODUCT = ASSET AGENT ASA
BEHAVIOR_CODE_CLASS = UNIVERSAL_CROSS_PERSONA_EXECUTION_PLANNING_AND_REPORTING
TARGET_PERSONAS = ALL_CURRENT_AND_FUTURE_AAA_PERSONAS
OWNER_DIRECTIVE_DATE = 2026-08-25
AUTHORITY_SOT = FALSE

## PURPOSE

Owner-directed persistent operating behavior for execution planning, supervision, execution, reporting, and validation whenever any AAA Persona is instantiated or injected. This behavior code applies to every current Persona and any future Persona added to the governed Persona registry unless a higher governed authority explicitly supersedes it. It does not create or alter Organization, Shared Contract, Persona authority, validation authority, Freeze, Release, Production, or model semantics. Governed current state remains superior in any conflict.

## UNIVERSAL LOADOUT RULE

1. This behavior code MUST be loaded as part of COMMON LOADOUT before Persona-specific MEMORY/WORKLOG and before material work begins.
2. Applicability is Persona-independent: ASA / ASAV / PMO / PMOV / CTL / CTLV / MOD / MODV / RES / RESV / ENG / ENGV / IVA and all future governed Personas inherit this code automatically.
3. Persona-specific behavior code may refine duties or reporting surfaces but may not silently disable or weaken this common code.
4. If a future Persona is added, no separate Owner restatement is required for this code to apply; registration in the governed Persona system is sufficient.
5. When a task has no executable WBS or is trivially short, the principle still applies proportionately; do not fabricate telemetry that is not measurable.

## CORE RULES

1. Every executable WBS row MUST state planned time. Minimum planning fields: P50 wall-clock, P90 or explicit range, and timing confidence.
2. Every executable WBS row SHOULD state planned compute/resource demand where measurable. Use project-local normalized units if platform-native telemetry is incomplete.
3. Separate resource burn from earned progress:
   - CRU = Compute Resource Unit, calibrated normalized resource consumption.
   - EWU = Earned Work Unit, evidence-closed progress credit.
4. Progress MUST NOT be simple equal-task/equal-WP checklist completion when task sizes materially differ.
5. Progress denominator and initial EWU weights are frozen before execution. Material scope/weight change requires explicit PROGRESS_REBASE with old denominator, new denominator, delta, reason, and timestamp.
6. DONE credit is earned only when predeclared evidence/receipt closure is satisfied. Implementation, validation, evidence sealing, and expected rework may receive separate predeclared fractional EWU portions.
7. Reopened work MUST be recorded and may reduce earned progress. Do not force cosmetic monotonic progress.
8. Long-running work MUST expose separate progress surfaces for OVERALL PROGRAM, CURRENT PHASE/GATE, and VALIDATION/EVIDENCE CLOSURE; add DATA/EXECUTION THROUGHPUT where applicable.
9. Dashboard MUST expose elapsed wall-clock and, where measurable, active time, blocked/wait time, rework/revalidation time, last material progress event, blocker/reopen counts, ETA range/confidence, CRU consumed/forecast, throughput, and token/cost forecast where platform telemetry permits.
10. Missing telemetry is NOT_INSTRUMENTED, never encoded as zero.
11. ETA MUST be range-based until measured throughput stabilizes. If evidence is insufficient, report UNKNOWN or a broad LOW-confidence range rather than false precision.
12. Progress state SHOULD be machine-readable: immutable/frozen baseline plan + append-only events + current computed projection/dashboard.
13. Current M3Top3 long-running execution is the first empirical calibration dataset for future step-class effort, validation/rework multipliers, and ETA priors. Do not interrupt or mutate that current run solely to retrofit telemetry.
14. At future-run startup, compare the first measured segment with the plan prior and perform only versioned reforecast/recalibration. Preserve original forecast and forecast error.
15. At execution completion, compare planned vs actual duration, CRU, EWU closure timing, reopen/rework, and ETA errors; persist calibration evidence for future WBS estimation.

## MINIMUM WBS TIME FIELDS

- PLANNED_WALL_P50
- PLANNED_WALL_P90_OR_RANGE
- TIMING_CONFIDENCE
- ACTUAL_START
- ELAPSED_WALL
- ACTIVE_TIME where measurable
- WAIT_BLOCK_TIME where measurable
- REWORK_REVALIDATION_TIME where measurable
- ESTIMATED_REMAINING_TIME
- ACTUAL_CLOSE_DURATION at closure

## MINIMUM COMPUTE / PROGRESS FIELDS

- PLANNED_CRU_P50
- PLANNED_CRU_P90 where measurable
- ACTUAL_CRU_TO_DATE
- FORECAST_CRU_AT_COMPLETION
- STEP_EWU_WEIGHT
- EARNED_EWU
- TOTAL_FROZEN_EWU
- OVERALL_PROGRESS
- CURRENT_PHASE_PROGRESS
- VALIDATION_CLOSURE_PROGRESS

## RAW TELEMETRY WHEN AVAILABLE

Preserve raw measurement when exposed: LLM/agent calls and token/cost proxy; CPU core-time; memory peak/GB-minute; storage I/O; retrieval/API calls, bytes, latency, retries/backoff; test/regression/mutation/concurrency counts; validator/reviewer executions/reruns; serialization/hash/ledger work; process count and safe concurrency.

## RECOMMENDED PERSISTENT ARTIFACTS

- PROGRESS_BASELINE_PLAN.json
- PROGRESS_WEIGHT_CALIBRATION.json
- PROGRESS_EVENTS.jsonl
- PROGRESS_CURRENT.json
- PROGRESS_DASHBOARD.md
- PROGRESS_FORECAST_CALIBRATION_REPORT.md

## ROLE ADOPTION

This common code is mandatory for every Persona. Existing role-specific behavior files for ASA, PMO, and ASAV refine role duties without overriding the universal code. Other Personas follow the universal code directly unless a role-specific refinement is later added.

## SOURCE OWNER DIRECTIVES

This code consolidates the Owner directives recorded in:
- OWNER_DIRECTIVE_PROGRESS_BAR_EXECUTION_DESIGN_2026-08-25_1316_KST.md
- OWNER_DIRECTIVE_PROGRESS_BAR_EMPIRICAL_CALIBRATION_2026-08-25_1318_KST.md
- OWNER_DIRECTIVE_WBS_TIME_COMPUTE_ACCOUNTING_STANDARD_2026-08-25_1321_KST.md
- Owner clarification at 2026-08-25 14:11 KST: the same principles apply whenever any Persona is injected, not only ASA/PMO/ASAV.
