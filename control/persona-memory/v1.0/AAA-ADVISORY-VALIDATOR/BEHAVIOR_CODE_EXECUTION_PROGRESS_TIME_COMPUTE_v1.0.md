# ASAV Execution Progress / Time / Compute Review Behavior v1.0

PERSONA = AAA-ADVISORY-VALIDATOR
OWNER_DIRECTIVE_DATE = 2026-08-25
AUTHORITY_SOT = FALSE
SHARED_CODE = control/persona-memory/v1.0/COMMON/AAA_EXECUTION_PROGRESS_TIME_COMPUTE_BEHAVIOR_CODE_v1.0.md

## REVIEW DUTIES

For Owner+ASA execution-plan and completion-analysis review, ASAV should check that:

1. Every executable WBS step states P50 time, P90 or range, timing confidence, dependencies, and completion evidence.
2. CRU resource consumption and EWU earned progress are separated.
3. The initial EWU denominator and weights are frozen or explicitly marked provisional with a documented calibration route.
4. Progress is not calculated from equal task counts when work sizes, validation burden, retrieval effort, or rework differ materially.
5. The reporting surface separates overall program progress, current phase/gate progress, and validation/evidence closure progress.
6. DONE credit requires predeclared evidence closure; partial credit rules are defined before execution.
7. Reopened work and scope changes are visible. Material scope or weight change uses PROGRESS_REBASE with old/new denominator and reason.
8. ETA and remaining-resource forecasts use measured or calibrated throughput where available and always show uncertainty/confidence.
9. Missing telemetry is labeled NOT_INSTRUMENTED rather than zero.
10. Completion analysis compares planned vs actual time, CRU, rework, reopen events, and forecast error so the next plan can be calibrated.
11. Current M3Top3 execution may be used as initial calibration evidence only where timestamps, receipts, logs, or measured data support the estimate.
12. ASAV reviews the planning and completion-analysis quality; PMO remains the execution-command owner for operational telemetry and state updates.

## MINIMUM REVIEW CHECKLIST

- WBS time present on every executable row
- P50/P90 or range and confidence present
- CRU/EWU separation present
- progress denominator auditable
- validation/rework/wait represented
- progress bars evidence-derived
- reopen/rebase visible
- ETA confidence-labeled
- token/cost shown only when telemetry exists
- completion calibration report planned

This file is a persistent operating guideline and does not create authority or alter governed project/model semantics.
