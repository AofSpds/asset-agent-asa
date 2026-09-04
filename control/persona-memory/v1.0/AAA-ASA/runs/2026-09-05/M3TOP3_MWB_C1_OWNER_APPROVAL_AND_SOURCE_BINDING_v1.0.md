# M3Top3 Workbench C1 — Owner approval binding and ASA continuity

PROJECT = AAA
PRODUCT = ASSET AGENT ASA
RECORDER_PERSONA = AAA-ASA (ASA)
RECORD_CLASS = APPEND_ONLY_OWNER_DECISION_BINDING_AND_PERSONA_WORKLOG
AUTHORITY_SOURCE = HUMAN_OWNER_MESSAGE_IN_CURRENT_AAA_ASA_CONVERSATION
MEMORY_IS_AUTHORITY_SOT = FALSE
PREPARATION_CLOCK_READBACK_KST = 2026-09-05T07:05:20+09:00
OWNER_MESSAGE_TIMESTAMP = NOT_EXPOSED
OWNER_APPROVAL_TEXT = 승인합니다.
OWNER_DECISION_ID = AAA-MWB-C1-OWNER-AUTH-20260905-001
CORRECTION_BATCH_ID = AAA-MWB-C1-20260905
DECISION = APPROVE_CORRECTION_REQUIRED

## Exact approval object
The Owner's immediately following approval binds the preceding card titled `OWNER DECISION — M3TOP3 MODEL WORKBENCH v0.1 BOUNDED CORRECTION`, not another project or task.

REVIEWED_TARGET = 96db4afb5686175ad61eea127d6965102653bffc
REVIEWED_TREE = 442ba156a49dd5a7dc62f7d518058226bf29d76b
AUTHORIZE = ONE_BOUNDED_CORRECTION_BATCH + ONE_AFFECTED_ONLY_REVALIDATION
FINDING_SCOPE = MODV-FP-001 / MODV-FP-002 / MODV-FP-003 / ENGV-MWB-01 / ENGV-MWB-02
SECOND_CORRECTION_CYCLE = NOT_AUTHORIZED
SECOND_REVALIDATION_CYCLE = NOT_AUTHORIZED

The four approved correction axes are:
1. Separate Tail Ranking's Opportunity-owned meaning from SetPolicy.
2. Enforce raw-rank and identity postconditions across selected_set, raw_ranking and decision_log.
3. Make the mandatory PIT firewall non-replaceable and recursively cover all permitted Mapping inputs within the isolated workbench.
4. Make exact-decimal ordering and result serialization/digest independent of ambient Decimal context and add regressions.

Expected material paths:
- control/m3top3/model-workbench/v0.1/M3TOP3_FORWARD_MODEL_WORKBENCH_ARCHITECTURE_AND_PREREGISTRATION_v0.1.md
- tools/m3top3/model_workbench/contracts.py
- tools/m3top3/model_workbench/workbench.py
- tools/m3top3/model_workbench/tests/test_workbench.py

Preserve the reviewed commit/tree and original review verdicts; produce a new exact correction target. Preserve F01 Finance incident report, active v1, existing PIT/GT/Universe semantics, shared PITGuard/core dependencies, Finance HOLD and branch, main, model pointers, release and production state. Unexpected necessary material path/semantic expansion requires an explicit scope disposition, not silent author expansion.

PMO may use actual MOD/ENG author threads. Validators remain OFF until correction completion and new target freeze. PMOV then conducts the single approved affected control review with actual MODV and ENGV children; no separate user-operated domain-validator channels are required. PMO/MOD/ENG authors must not substitute for the validators. Execution capability and actual dispatch remain to be checked at their runtime, not inferred from model names.

Revalidation is authorized conditionally on a unique corrected commit/tree produced by this C1 batch, complete mapping to the five findings, allowed diff/preservation, author self-check and PMO terminal completion. This is not authorization to review arbitrary future HEADs, repeat the original full review, self-correct during validation, or create a second cycle. The corrected commit cannot be known before creation and must be resolved from the exact C1 completion carrier rather than invented.

No IVA L2, Golden Replay, Full Replay, model-performance evaluation, merge, activation, release, production, Finance resume, provider/quota/custody expansion, or new paid service is approved. A P0 scope escape is not waived by the absence of IVA in this bounded campaign.

## Received source identity and evidence boundary
REPORT_ID = AAA_M3TOP3_MODEL_WORKBENCH_PMOV_REVIEW_CAMPAIGN_REPORT_v1.1_20260905
CAMPAIGN_ID = AAA-MWB-96db4afb-FIRST-REVIEW-20260905
UPLOADED_FILE_ID = file_0000000004f481f4850ba4cfe5438f61
UPLOADED_FILENAME = 붙여넣은 텍스트 (1)(20260904-220019).txt
UPLOADED_EXACT_BYTES = 54018
UPLOADED_SHA256 = bc3cf51d7343185d2b33cab4bf144bc98f3e9af350766ef4f57234b9d857cc54
UPLOAD_DIGEST_METHOD = SHA256_OF_ORIGINAL_UPLOADED_BYTES_NO_NORMALIZATION

The upload contains the full PMOV campaign report with three role originals. It remains preserved as the received attachment. This journal contains source-derived finding summaries, not a byte-identical Git copy of that complete report. It does not claim that an earlier exported MD file has the same digest as this pasted-text upload.

Original reported verdicts are retained: PMOV PASS_WITH_LIMITATIONS (0 blocking, 2 limitations); MODV FAIL (3 blocking); ENGV FAIL (2 blocking). ASA has not rerun or independently validated the code in this approval-binding act.

Source-derived exact finding/reproduction map:
- MODV-FP-001: F02 §§2–3; contracts.py TailRankingStage.rank; workbench.py OpportunityTailRanker.rank. The exported ranker receives SetPolicy and consults opportunity_state_required_for_raw_rank. With the same parsed candidates, changing only that field from VERIFIED to PARTIAL changes the reported five ranked rows to zero. Full-envelope default validation does not prove the advertised public interface separation.
- MODV-FP-002: ForwardModelWorkbench.run and _assert_accounting. An injected set constructor delegates to the built-in implementation and then sets the two selected rows' raw_rank to 999. The engine still reports guard_state=PASS although originating ranks are 2 and 5. Findings also identify absent duplicate-selection and selected-set/decision-log consistency checks.
- MODV-FP-003: _run_existing_pit_guard and accepted metadata Mapping surface. A supplied no-op guard replaces the canonical baseline; future_close then passes. With the default guard, future_close inside MappingProxyType also passes. The canonical guard must not be made optional, and accepted nested structures must not be opaque to it.
- ENGV-MWB-01: OpportunityTailRanker.rank uses unary -Decimal in ordering and tie-key formatting. alpha=10000000000000000000000000001 and bravo=10000000000000000000000000002 are ranked differently at precision 28 versus 60; input/run identity stays the same but result digest differs. This is a report finding, not a new reproduction by ASA.
- ENGV-MWB-02: metadata['wrapped_mapping']=collections.UserDict({'future_close':1}) is accepted and returns guard_state=PASS because PITGuard descends only into dict/list while the workbench accepts general Mapping. It corroborates the Mapping path in MODV-FP-003; retain both original IDs and require closure evidence for each.

These are five original finding records, grouped into four work packages. PIT firewall is one work package with two separately required bypass closures. No original finding is deleted or downgraded.

PMOV-NB-01 (missing original build approval bytes) and PMOV-NB-02 (historical author-runtime/process claims) remain nonblocking limitations. This current approval record does not retroactively repair their provenance. Do not start a separate historical recovery campaign.

## Readback and next route
During this act the material commit/tree/parent and remote refs were reread through GitHub: main 950bc98b0702cd5564e3d7b24a6624d9818dfbb9; original workbench task head a9b1e59680af76e4d133ffce7aabc6ddeb526813. The earlier completion carrier remains caf99be5d2a41b9118a997764f7459aa6c272bf7, separate from material target 96db4afb5686175ad61eea127d6965102653bffc.

NEXT_ROUTE = OWNER_DELIVERS_ONE_PMO_CORRECTION_PACKET / PMO_BUILDS_C1 / PMOV_PERFORMS_PREAPPROVED_AFFECTED_REVIEW_AFTER_COMPLETION
CORRECTION_EXECUTION_BY_ASA = NONE
REVALIDATION_EXECUTION_BY_ASA = NONE
CANDIDATE_ACCEPTANCE = NOT_GRANTED

This append records the actual new Owner decision and supersedes only the previous recommendation's pending-approval state. It does not rewrite previous journals, change the source candidate, move main/Finance/bootstrap refs, or claim that another runtime has started. A packet will convey the same approved scope; repeated scope approval is not required, but actual routing and dispatch are separate observable actions.
