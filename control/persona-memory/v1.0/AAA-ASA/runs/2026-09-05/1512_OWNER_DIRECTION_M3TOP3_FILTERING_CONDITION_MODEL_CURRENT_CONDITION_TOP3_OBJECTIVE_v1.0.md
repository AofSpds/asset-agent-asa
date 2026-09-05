# Owner Direction — M3Top3 as a Condition-Filtering / Top3 Selection Research Model

PROJECT = AAA
PRODUCT = ASSET AGENT ASA
PERSONA = AAA-ASA
RECORDED_AT_KST = 2026-09-05 15:12 KST
AUTHORITY_SOT = FALSE
DIRECTIVE_CLASS = OWNER_OBJECTIVE_CLARIFICATION / CONTINUITY

## Owner clarification

M3Top3 should be understood as a research project for a filtering-condition model that identifies the three candidates most suitable for the condition at the relevant snapshot/current state.

The objective is NOT to perfectly adjust or fully reconstruct every company, every feature, every historical field, or every market condition before producing useful research output.

Core research objective:

`CONDITION AT SNAPSHOT -> CANDIDATE FILTER / MATCHING -> RELATIVE RANKING -> BEST-FIT TOP3`

## Interpretation consequences

1. The success criterion is decision-useful Top3 identification under the relevant condition, not universal perfect state reconstruction.
2. Exhaustive completion of all companies/features/eligibility evidence is not a default prerequisite if the remaining uncertainty is explicitly represented and does not destroy the ability to compare plausible candidates.
3. Eligibility filtering must be separated from evidence confidence and model scoreability:
   - HARD_ELIGIBILITY: truly outside the investable/relevant set.
   - ELIGIBILITY_CONFIDENCE: how strongly the historical eligibility state is proven.
   - SCOREABILITY: how much model input is available.
4. Missing evidence must not automatically become economic ineligibility. An unresolved evidence state should not silently remove a potentially best-fit candidate unless the bounded research protocol explicitly chooses a strict sensitivity lane and preserves the exclusion accounting.
5. Strong filtering is acceptable when it reflects the model's intended condition match; it is dangerous when the filtering is mostly an artifact of data/evidence availability.
6. Evaluation should therefore inspect both:
   - selection quality of Top3 / Top10 / critical misses under the condition; and
   - membership/filter stability when uncertain eligibility or missing inputs are varied within defensible bounds.
7. The existing M3Top3-v1 scorer/weights/features are NOT changed by this clarification. Any semantic mutation still requires a separately governed design/validation decision.
8. Current PC1 process-calibration run continues. Its telemetry should help distinguish useful condition filtering from accidental data-availability filtering and should inform the next eligibility-stability / condition-matching review.

MODEL_SEMANTIC_CHANGE_AUTHORIZED = FALSE
PIT_SEMANTIC_CHANGE_AUTHORIZED = FALSE
CURRENT_EXECUTION_INTERRUPTION_REQUIRED = FALSE
OWNER_ACTION_REQUIRED = FALSE
