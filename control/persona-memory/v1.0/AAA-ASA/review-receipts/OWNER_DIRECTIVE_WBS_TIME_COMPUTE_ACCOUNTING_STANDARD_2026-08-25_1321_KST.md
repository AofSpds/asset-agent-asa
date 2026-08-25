# Owner Directive — WBS Time + Compute Accounting Standard

PROJECT = AAA
PRODUCT = ASSET AGENT ASA
PERSONA = AAA-ASA
DIRECTIVE_CLASS = OWNER_EXECUTION_DESIGN_REQUIREMENT
RECORDED_AT = 2026-08-25 13:21 KST
AUTHORITY_SOT = FALSE
PURPOSE = Persistent continuity for future execution-plan design

## OWNER DIRECTIVE

For future execution designs, every WBS step must always state time. Where possible, each step must also estimate and later measure compute/resource consumption in detail. A project-local normalized unit is acceptable. The resulting telemetry should support a progress bar that approximates real remaining effort rather than simple checklist completion.

## REQUIRED WBS TIME FIELDS

Every executable WBS row must contain, at minimum:

- planned wall-clock duration P50;
- planned wall-clock duration P90 or explicit range;
- timing confidence HIGH/MEDIUM/LOW;
- actual start timestamp;
- elapsed wall-clock;
- active execution time where measurable;
- dependency/block/wait time where measurable;
- rework/revalidation time where measurable;
- estimated remaining time;
- final actual duration at closure.

Time fields may not be omitted. If evidence is insufficient, use a broad estimate plus LOW confidence rather than silently leaving time blank. `UNKNOWN_NOT_MEASURED` is allowed only when even a bounded estimate is impossible, with reason recorded.

## COMPUTE / RESOURCE ACCOUNTING

Use two separate normalized concepts so resource burn is not confused with progress:

### 1. CRU — Compute Resource Unit

`CRU` is a calibrated normalized measure of resources consumed by a WBS step. The exact weight profile is frozen per execution plan using empirical calibration, initially informed by the current M3Top3 long-running execution and later replaced/refined by measured telemetry.

Raw telemetry should be preserved whenever available:

- LLM/agent inference calls and token counts/cost proxy where exposed;
- CPU core-time;
- memory peak and GB-minute where available;
- storage read/write bytes and I/O time;
- retrieval/API calls, bytes, latency, retries and backoff;
- test/regression/mutation/concurrency workload counts;
- validator/reviewer executions and reruns;
- serialization/hash/ledger workload;
- process count and safe concurrency.

Missing telemetry is `NOT_INSTRUMENTED`, never zero.

Each WBS row should include `PLANNED_CRU_P50`, `PLANNED_CRU_P90`, `ACTUAL_CRU_TO_DATE`, and `FORECAST_CRU_AT_COMPLETION` when measurable.

### 2. EWU — Earned Work Unit

`EWU` is the progress-credit unit. It is earned only when predeclared completion evidence closes. High CRU consumption does not itself earn progress.

Each WBS step receives an EWU weight before execution based on expected real effort, including implementation, validation, evidence closure and expected rework burden. The total frozen EWU denominator powers the progress bar.

Progress = `EARNED_EWU / CURRENT_FROZEN_TOTAL_EWU`.

A completed implementation with unfinished validation earns only the predeclared implementation portion, not the full step. Reopened work can reduce earned progress. Scope additions require explicit `PROGRESS_REBASE` showing old denominator, new denominator, reason, and added work.

## REQUIRED EXECUTION DASHBOARD

Future long-running executions should expose at least:

- OVERALL_PROGRESS percent and confidence interval/range when appropriate;
- CURRENT_PHASE_PROGRESS;
- earned EWU / total EWU;
- elapsed wall-clock;
- active / wait-block / rework time when measurable;
- ETA P50 and P90/range plus confidence;
- CRU consumed and forecast-to-complete;
- throughput such as EWU/hour and/or company-window/hour where applicable;
- open blockers;
- reopened units;
- last material progress timestamp and event;
- scope/progress rebase history;
- cost/token forecast when platform telemetry permits.

## CALIBRATION RULE

The current M3Top3 long-running execution is the first empirical calibration dataset for step-class effort weights, validation/rework multipliers and initial ETA priors. Future runs should collect native telemetry from execution start. Initial priors may be recalibrated from early-run observations, but EWU denominators/weights are not silently rewritten; material changes require explicit PROGRESS_REBASE.

Suggested step classes for calibration include:

- design/authoring;
- deterministic implementation;
- unit/regression validation;
- mutation/fault-injection;
- concurrency/atomicity validation;
- source/evidence retrieval;
- PIT reconstruction/annotation;
- independent paired validation;
- gate reconciliation/evidence sealing;
- replay/evaluation;
- failure analysis;
- challenger implementation/evaluation.

## FORECAST DISCIPLINE

- Always distinguish wall-clock from cumulative compute/resource consumption.
- Always distinguish progress earned from resource burn.
- Parallel workers may increase CRU while reducing wall-clock.
- Repeated validation and rework must be visible rather than hidden inside a step.
- ETA should be range-based until empirical throughput stabilizes.
- At completion, compare predicted vs actual duration/CRU and persist forecast error for subsequent calibration.

## NEXT-PLAN REQUIREMENT

The next PMO execution plan should include a WBS timing/resource schema and progress instrumentation before execution starts, with a frozen initial EWU denominator and CRU calibration profile or explicitly marked provisional calibration.
