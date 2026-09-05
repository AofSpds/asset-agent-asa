# OWNER APPROVAL — M3Top3 F02-R1 multi-company input repair

PROJECT = AAA
PRODUCT = ASSET AGENT ASA
PERSONA = AAA-ASA (ASA)
DATE_KST = 2026-09-05 17:10 KST
CLASS = OWNER_DECISION / EXECUTION_AUTHORIZATION_BINDING / CONTINUITY_RECEIPT
AUTHORITY_SOT = FALSE

## Owner decision

OWNER_DECISION = APPROVE
OWNER_TEXT = 승인합니다. 아울러 패킷도 방금 넘겼습니다.

The Owner approval is bound to the exact ASA-authored execution request below.

TARGET_PACKET_ID = AAA-M3TOP3-F02-R1-MULTI-COMPANY-INPUT-REPAIR-v1.0-20260905
TARGET_PACKET_COMMIT = 2f773328e50ab0d6e7f640845251d16ba167b26f
TARGET_PACKET_TREE = 570d6994ec1d1ad1b9611780a2b2d7d7ebfb1e09
TARGET_PACKET_BLOB = 8c410fe2aa6cedf1910d01f8bf4529ccb5cd29fb
TARGET_PACKET_PATH = control/persona-memory/v1.0/AAA-ASA/runs/2026-09-05/1700_M3TOP3_F02_R1_MULTI_COMPANY_INPUT_REPAIR_REQUEST_v1.0.md

## Authorized bounded execution

The approval activates the exact bounded successor execution scope described by the target packet, including its D1 input-selection policy candidate and declared resource ceilings, subject to governed authority/readback at PMO execution start.

D1_APPROVED = TRUE
D1_POLICY = Use cutoff-safe latest disclosed realized quarter under the packet rule: Q2 preferred where admissible; Q1 fallback only when Q2 is not available/admissible before the fixed W1 cutoff; compare against the matching prior-year comparable period; preserve heterogeneous-period limitation explicitly.

PRIMARY_NEW_ISSUERS = KRX:003160, KRX:025560, KRX:031980, KRX:036200
CACHED_CONTROL = KRX:005290
WINDOW = W1
CUTOFF = 2024-08-09T23:59:59+09:00
EXTERNAL_SOURCE_ACTION_CEILING = 48 total / 12 per new issuer
PARALLELISM_CEILING = max two bounded author/research workers plus PMO single-writer assembly

Authorized implementation intent includes bounded repair/generalization of issuer/date/table/source mapping where required to admit valid company-specific source shapes without retaining the 005290-specific hard-coded anchors. Exact source identity, raw custody, publication timing, PIT/provenance, deterministic lineage and affected validation remain required.

## Preserved prohibitions and boundaries

MODEL_WEIGHT_CHANGE = PROHIBITED
FEATURE_FORMULA_CHANGE = PROHIBITED
SCORER_OR_RANKING_SEMANTIC_CHANGE = PROHIBITED
PIT_CUTOFF_CHANGE = PROHIBITED
OUTCOME_FIREWALL_CHANGE = PROHIBITED
ELIGIBILITY_DENOMINATOR_REWRITE = PROHIBITED
FUTURE_OUTCOME_AWARE_INPUT_SELECTION = PROHIBITED
NEW_PROVIDER = NOT_AUTHORIZED
PAID_DATA_OR_NEW_CREDENTIAL = NOT_AUTHORIZED
RELEASE_PROMOTION_PRODUCTION = NOT_AUTHORIZED
PC1_REOPEN_OR_RERUN = PROHIBITED
OLD_RESULT_OVERWRITE = PROHIBITED

NOT_FOUND must remain retrieval/evidence state, not zero, negative business fact, or model rejection.

## Dispatch state

OWNER_REPORTS_PACKET_ALREADY_TRANSFERRED_TO_PMO = TRUE
ASA_DUPLICATE_DISPATCH = PROHIBITED
NEW_PMO_EXECUTION_DISPATCHED_BY_THIS_RECEIPT = FALSE

The Owner has already transferred the packet to the PMO execution surface. ASA therefore does not create a second execution dispatch or duplicate runtime. PMO should bootstrap current governed state, verify no competing writer, create a fresh isolated successor branch/worktree/run ID, and execute the approved packet to its terminal condition.

## Supervision state

ASA_ROLE = SUPERVISORY_CONTROL / OWNER_FACING
PMO_ROLE = EXECUTION_COMMAND
NEXT_ASA_EVENT = RECEIVE_AND_REVIEW_PMO_PROGRESS_OR_TERMINAL_RETURN
REPEAT_OWNER_APPROVAL_REQUIRED = FALSE_WITHIN_EXACT_APPROVED_SCOPE

Only a material scope expansion, new provider/credential/budget, model/PIT/eligibility semantic change, authority/validation-floor impact, destructive release/production action, or conflict unresolved from governed state requires a new Owner decision.

OWNER_ACTION_REQUIRED = FALSE
CURRENT_STATUS = OWNER_APPROVED_PACKET_ALREADY_TRANSFERRED_TO_PMO_AWAIT_EXECUTION_RETURN
