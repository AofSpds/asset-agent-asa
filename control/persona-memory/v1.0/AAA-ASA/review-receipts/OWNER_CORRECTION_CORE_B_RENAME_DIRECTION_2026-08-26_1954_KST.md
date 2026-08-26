# OWNER CORRECTION — CORE B RENAME DIRECTION

PROJECT = AAA
PRODUCT = ASSET AGENT ASA
PERSONA = AAA-ASA
MEMORY_CLASS = OWNER_CORRECTION_CONTINUITY_NOT_AUTHORITY_SOT
DATE_KST = 2026-08-26 19:54 KST

## OWNER CORRECTION
Owner clarified: `CORE B 를 리네이밍하는거였다구요`.

The intended historical rename/successor-rebind direction is NOT:

`AAA-MODEL-ARCHITECT -> AAA-MODEL-VALIDATION-DESIGN-ARCHITECT`

Instead, existing Owner evidence records:

`AAA-MODEL-VALIDATION-DESIGN-ARCHITECT -> AAA-MODEL-ARCHITECT`

and the paired validator successor-rebind:

`AAA-MODEL-DESIGN-VALIDATOR -> AAA-MODEL-VALIDATOR`.

Exact Owner decision evidence:
- commit: `bf8bddd9b86bc233a92a56a712f685f37f01a3f7`
- path: `control/decisions/organization/v0.3/AAA_OWNER_DECISION_CORE_B_MODEL_ROLE_v1.0.json`
- source Owner text: `CORE B는 AAA-MODEL-ARCHITECT 가 맞습니다. 바꿔주세요.`
- recorded effective role: `AAA-MODEL-ARCHITECT`
- supersedes current use of: `AAA-MODEL-VALIDATION-DESIGN-ARCHITECT`

Additional organization-transition evidence records:
- `AAA-MODEL-VALIDATION-DESIGN-ARCHITECT -> AAA-MODEL-ARCHITECT / SUCCESSOR_REBIND`
- `AAA-MODEL-DESIGN-VALIDATOR -> AAA-MODEL-VALIDATOR / SUCCESSOR_REBIND`

## CURRENT CORRECTION
The current Organization v1.3 active projection already contains the short-name pair:
- `AAA-MODEL-ARCHITECT`
- `AAA-MODEL-VALIDATOR`

Current stale/conflicting surfaces include later Project Instructions / Shared Contract / selector-style projections that still resolve the long-name pair.

Therefore any Organization v1.4 candidate whose effect is to replace the active short-name pair with the long-name pair is WRONG-DIRECTION for the Owner rename intent and MUST NOT be activated solely as a rename/currentization fix.

## REQUIRED NEXT ROUTE
1. Do not approve/execute the current wrong-direction v1.4 cutover.
2. Preserve immutable historical artifacts/receipts.
3. Treat the active short-name pair as the Owner-directed rename target unless a later exact Owner decision superseding `bf8bddd...` is proven.
4. Reconcile stale current Project Instructions / Shared Contract / selector / bootstrap / runtime references to the approved short-name pair through the minimum governed corrective-maintenance route.
5. Preserve controlled legacy aliases for historical long names.
6. Do not restart broad Core-B authority redesign or validation loops for a pure already-authorized rename propagation defect.

INCIDENT_CLASSIFICATION = PARTIAL_PERSONA_RENAME_PROPAGATION / CONTROL_STATE_SYNCHRONIZATION_DEFECT
MODEL_SEMANTIC_CHANGE = NONE
AUTHORITY_CHANGE = NONE unless a later exact source proves otherwise
HISTORICAL_REWRITE = PROHIBITED
