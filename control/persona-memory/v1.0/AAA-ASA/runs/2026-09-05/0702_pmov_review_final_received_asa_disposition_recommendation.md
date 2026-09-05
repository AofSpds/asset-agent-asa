# ASA continuity — PMOV final review receipt and disposition recommendation

PROJECT = AAA
PERSONA = AAA-ASA (ASA)
MEMORY_CLASS = APPEND_ONLY_PERSONA_RUN_JOURNAL
AUTHORITY_SOT = FALSE
RECORDED_AT_KST = 2026-09-05 07:02
SOURCE_CLASS = OWNER_PROVIDED_PMO_VALIDATION_REPORT_TEXT
ASA_VALIDATION_PERFORMED = NONE
OWNER_DECISION_CREATED = FALSE

## Exact campaign received
REPORT_ID = AAA_M3TOP3_MODEL_WORKBENCH_PMOV_REVIEW_CAMPAIGN_REPORT_v1.1_20260905
CAMPAIGN_ID = AAA-MWB-96db4afb-FIRST-REVIEW-20260905
FROZEN_TARGET = 96db4afb5686175ad61eea127d6965102653bffc
FROZEN_TARGET_TREE = 442ba156a49dd5a7dc62f7d518058226bf29d76b
CAMPAIGN_STATUS = REVIEW_COMPLETED_WITH_BLOCKING_FINDINGS

PMOV = PASS_WITH_LIMITATIONS / 0 blocking / 2 nonblocking limitations
MODV = FAIL / 3 blocking findings
ENGV = FAIL / 2 blocking findings
IVA_L2 = NOT_PERFORMED
MODEL_PERFORMANCE_VALIDATION = NOT_PERFORMED
OWNER_ACCEPTANCE = NOT_PERFORMED
FINANCE = HOLD

## Blocking findings received
- MODV-FP-001: Tail Ranking public boundary consumes SetPolicy; claimed Opportunity-only separation is false at interface level.
- MODV-FP-002: replaceable set-construction stage can rewrite selected-set raw_rank without postcondition rejection.
- MODV-FP-003: mandatory PIT firewall can be weakened by injected no-op guard and can miss accepted non-dict Mapping values.
- ENGV-MWB-01: ambient Decimal precision can reverse valid high-precision ranking and change result digest for identical canonical input/run identity.
- ENGV-MWB-02: nested non-dict Mapping can hide an existing PIT-forbidden field and still produce guard_state=PASS.

Crosswalk shows MODV-FP-003 Mapping traversal and ENGV-MWB-02 corroborate the same firewall surface, so five findings map to four practical correction axes.

## Nonblocking limitations preserved
- PMOV-NB-01: original Owner approval-packet bytes unavailable; declared digest not independently recomputed.
- PMOV-NB-02: historical author participation/test/timing/external-effect assertions remain AUTHOR_REPORTED_ONLY.

## ASA recommendation — advisory only
RECOMMENDED_OWNER_DISPOSITION = CORRECTION_REQUIRED
RECOMMENDED_CORRECTION_MODEL = ONE_BOUNDED_CORRECTION_BATCH
RECOMMENDED_REVALIDATION = ONE_AFFECTED_ONLY_REVALIDATION
SECOND_CORRECTION_CYCLE = REQUIRES_NEW_OWNER_REPLAN
IVA_FOR_THIS_SYNTHETIC_WORKBENCH_CORRECTION = NOT_RECOMMENDED_UNLESS_SCOPE_ESCALATES_TO_P0_OR_ACTIVE/PIT/GT/RELEASE_SURFACE

Proposed correction axes:
1. Remove SetPolicy from TailRanking semantic dependency; rankability must be Opportunity-owned or separately typed, not SetPolicy-owned.
2. Add strict downstream postconditions tying selected_set raw_rank/identity to canonical raw_ranking and decision log; reject duplicate or contradictory selections.
3. Make canonical PIT firewall non-replaceable; any extension is additive only. Normalize/reject accepted Mapping shapes before PIT traversal so all accepted public inputs are recursively covered without modifying active PIT semantics unless separately authorized.
4. Eliminate ambient Decimal-context dependence from sort/tie serialization and add high-precision cross-context regression tests.

Expected affected candidate paths are primarily F02 architecture/preregistration, F04 contracts.py, F05 workbench.py, F08 test_workbench.py. Exact affected set must be fixed by the correction plan before mutation. F01 Finance report must remain untouched. Existing active-v1, PIT/GT/universe, Finance, main, release, and production surfaces remain preserved.

The correction act should produce a new exact commit/tree. Affected-only revalidation should use PMOV for target/diff/control preservation, MODV for semantic closure of MODV-FP-001/002/003, and ENGV for ENGV-MWB-01/02 plus regression evidence. No automatic correction, revalidation, merge, activation, Finance resume, or second cycle is authorized by this journal.
