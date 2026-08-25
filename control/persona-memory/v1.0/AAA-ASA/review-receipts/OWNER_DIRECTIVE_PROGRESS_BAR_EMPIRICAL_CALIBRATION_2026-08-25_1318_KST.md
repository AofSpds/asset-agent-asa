# Owner Directive — Empirically Calibrated Progress Bar

PROJECT = AAA
PRODUCT = ASSET AGENT ASA
PERSONA = AAA-ASA
RECORDED_AT = 2026-08-25 13:18 KST
AUTHORITY_CLASS = OWNER_DIRECTIVE_CONTINUITY
AUTHORITY_SOT = FALSE

## OWNER DIRECTIVE
For the next execution design, the progress bar should be empirically calibrated from the current long-running M3Top3 execution so that reported progress is close to actual remaining work rather than a checklist or equal-WP approximation.

## REQUIRED DESIGN RESPONSE
1. Treat the current M3Top3 execution as a calibration run.
2. Reconstruct actual elapsed time and, where available, active time, validation time, blocked/wait time, rework/reopen cycles, retry/backoff, subagent fanout, and cost/token telemetry by phase/work-unit class.
3. Derive initial effort weights for the next execution from measured effort distributions rather than equal task counts.
4. Maintain separate bars for OVERALL PROGRAM, CURRENT PHASE/GATE, DATA/EXECUTION THROUGHPUT where applicable, and VALIDATION/CLOSURE.
5. Progress numerator is evidence-closed earned work; partially complete work receives only predeclared fractional credit, never subjective ad-hoc credit.
6. Reopened work deducts earned progress. Scope changes require explicit PROGRESS_REBASE with old denominator, new denominator, delta and reason.
7. Report uncertainty/confidence. Do not present false precision. Early run may show a range; narrow it as telemetry accumulates.
8. ETA and remaining cost are shown only after sufficient measured throughput exists, as ranges with confidence.
9. Preserve an immutable baseline progress plan plus append-only progress events and a current computed state/dashboard.
10. At next-run startup, recalibrate against the first measured segment and compare forecast vs actual; update only through versioned reforecast, preserving the original forecast error for future calibration.

## TARGET ACCURACY
Aim for practical forecast calibration rather than cosmetic precision. After sufficient telemetry, target remaining-effort/progress forecast error within approximately ±10–15% where workload class is comparable. If uncertainty remains larger, display the wider interval explicitly.

## MINIMUM PROGRESS SURFACES
- OVERALL weighted progress
- CURRENT PHASE/GATE progress
- evidence/validation closure progress
- elapsed wall-clock
- active vs blocked/waiting time when measurable
- last material progress event timestamp
- reopened/blocker counts
- ETA range + confidence when admissible
- token/cost burn and remaining forecast when telemetry is available

## NEXT EXECUTION ARTIFACTS
- PROGRESS_BASELINE_PLAN.json
- PROGRESS_WEIGHT_CALIBRATION.json
- PROGRESS_EVENTS.jsonl
- PROGRESS_CURRENT.json
- PROGRESS_DASHBOARD.md
- PROGRESS_FORECAST_CALIBRATION_REPORT.md after completion

## NON-INTERRUPTION
Do not interrupt or mutate the currently running M3Top3 execution merely to retrofit progress telemetry. Use its existing timestamps, receipts, logs and final completion package as calibration evidence, and apply the new progress instrumentation prospectively to the next execution.
