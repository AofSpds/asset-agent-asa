# M3Top3 Owner Review Item 19 Receipt

PROJECT = AAA
PRODUCT = ASSET AGENT ASA
PERSONA = AAA-ASA
RECEIPT_CLASS = NON_NORMATIVE_OWNER_REVIEW_CONTINUITY
AUTHORITY_SOT = FALSE
TIME_KST = 2026-08-22 20:48 KST

ITEM = 19
TITLE = Lexicographic Evaluation Order
OWNER_DECISION = PASS

APPROVED_ORDER =
1. Safety / Validity
2. Tail Defense
3. Opportunity Discovery
4. Investability
5. Coverage / Robustness
6. Operations

APPROVED_INTERPRETATION =
- Do not collapse M3Top3 model selection into one weighted composite score.
- Material failure at a higher-priority layer cannot be offset by a better score at a lower-priority layer.
- Safety/validity failures such as PIT leakage, outcome contamination, wrong model identity, inadmissible dataset, invalid Golden conformance, irreproducible material run, or wrong eligibility denominator invalidate the affected claim/run.
- Tail-defense criteria such as Critical Miss, Worst Actual Rank, deep-tail false positive and worst-window behavior are evaluated before aggregate Opportunity improvements.
- Opportunity Discovery remains based primarily on 3M MFE Rank and Top-K quality after Safety and Tail requirements are satisfied.
- Investability remains a separate plane using path-quality/liquidity measures rather than being retrospectively merged into the opportunity GT.
- Coverage/Robustness includes coverage stratification, missingness behavior, leave-one-window-out stability, concentration/regime dependence and related robustness diagnostics.
- Operations is evaluated after scientific validity/performance; however, reproducibility defects that invalidate evidence are escalated to Safety/Validity rather than treated as mere operational inconvenience.
- Challenger promotion thresholds/allowable non-inferiority margins must be preregistered before challenger outcome comparison.

CONTROL_CONTEXT =
PMO prepares the evaluation evidence package and drives execution. ASA supervises gate integrity and evidence sufficiency. Required paired validator / IVA / Owner gates remain applicable.

DOCUMENT_REVISION_RULE =
Carry this PASS into the consolidated successor revision after the full itemized review is complete; do not regenerate the two advisory documents yet.
