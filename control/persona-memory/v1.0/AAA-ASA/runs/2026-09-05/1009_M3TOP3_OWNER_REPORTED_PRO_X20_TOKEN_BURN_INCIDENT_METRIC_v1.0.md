# M3Top3 Owner-Reported Pro X20 Token Burn Incident Metric v1.0

PROJECT = AAA
PRODUCT = ASSET AGENT ASA
PERSONA = AAA-ASA (ASA)
DATE_KST = 2026-09-05 10:09 KST
RECORD_CLASS = OWNER_REPORTED_RESOURCE_BURN_METRIC / CONTINUITY / INCIDENT_EVIDENCE
AUTHORITY_SOT = FALSE

## Owner report

Owner reports that over roughly the last fifteen days, M3Top3/AAA work appears to have consumed approximately two full `Pro X20` 100% token allowances.

OWNER_TEXT = "프로 X20 기준 토큰 100% 를 두번은 쓴것 같아요 보름만에"

## Interpretation boundary

- This is an Owner-reported usage estimate, not platform-native token telemetry.
- Exact token count, monetary value, and attribution by gate/run are NOT_INSTRUMENTED unless separately recovered from product/account telemetry.
- Do not convert this estimate into an exact token count.
- Use it as a material resource-burn severity indicator for the G1/G2/G3 delay/governance incident and HLOM global-improvement review.

## Operating consequence

The incident review must treat resource burn as a first-class impact alongside elapsed wall-clock and decision latency. Long-running blocker loops must expose compute/token consumption when available, and stale no-evidence work must trigger route-change/Owner escalation rather than continue consuming premium compute without decision-relevant progress.

CURRENT_FIRST_SCORECARD_ROUTE = OWNER_AUTHORIZED_FAST_REPLAY_REBASELINE
OWNER_ACTION_REQUIRED = FALSE
NEXT = preserve this metric in the final incident/after-action accounting; do not interrupt the active first-scorecard PMO execution solely to retrofit exact historical token telemetry.
