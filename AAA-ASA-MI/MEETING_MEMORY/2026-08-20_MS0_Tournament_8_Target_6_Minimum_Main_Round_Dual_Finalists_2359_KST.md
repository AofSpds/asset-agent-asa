# MS0 Tournament Currentization — 8 Target / 6 Minimum / Main Round / Dual Finalists

TIME = 2026-08-20 23:59 KST
STATE = WORKING_RESEARCH_MEMORY / MS0_STAGE_DESIGN_CURRENTIZATION / NON_NORMATIVE

PROJECT CONTEXT =
- World Model naming candidate: 한알
- MS0 working milestone name: ONTOGENESIS
- MS0 narrative codename: FIAT LUX / 빛이 있으라
- First implementation artifact naming candidate: 별
- `별` current meaning: first implementation artifact only

NOT:
- Requirement
- Design Contract
- Canonical ontology
- Final model selection
- Validation receipt
- Owner acceptance

## 0. Owner currentization

The intended MS0 tournament field is expanded.

TARGET_INITIAL_CANDIDATES = 8
MINIMUM_SERIOUS_CANDIDATES = 6

Use eight candidates when eight genuinely distinct, serious, non-strawman model families can be produced.

If eight cannot be produced without padding the field with weak or duplicative candidates, use no fewer than six serious candidates and explicitly record why the field could not reach eight.

Do NOT invent artificial candidates merely to hit a number.

## 1. Tournament flow

TARGET FLOW:

8 serious initial candidates
-> same common Main-Round Pressure Test for every candidate
-> MAIN_ROUND_PASS_SET
-> evaluate every passer independently under Positive Filter and Negative Filter
-> select TWO DISTINCT finalists from passers only:
   1. POSITIVE_FINALIST = candidate with greatest demonstrated upside / positive profile
   2. ROBUSTNESS_FINALIST = candidate with smallest demonstrated downside / negative profile
-> MS0 Final Round / Dual Reference Candidate Deepening

If only 6 or 7 serious initial candidates are available, the same flow applies.

## 2. Main round comes before champion selection

The Positive / Negative filters do NOT select candidates directly from the initial pool.

First, all initial candidates must face a common model-neutral viability gate.

A model reaches MAIN_ROUND_PASS_SET only if it is sufficiently coherent, non-trivial, and boundedly implementable to deserve deeper comparison.

The common gate must not force current vocabulary such as Relation / Event / Instance / Boundary to be primitives.

## 3. Positive and negative finalist roles

### POSITIVE_FINALIST

Among MAIN_ROUND_PASS_SET, choose the model that demonstrates the largest useful upside, such as:
- explanatory/representational power,
- new research surface,
- useful conceptual compression,
- extensibility,
- learning value from implementation,
- ability to preserve or expose important current hypotheses without unnecessary closure.

### ROBUSTNESS_FINALIST

Among MAIN_ROUND_PASS_SET, choose the model with the smallest demonstrated failure surface, such as:
- fewest hidden assumptions,
- lowest ontology lock-in,
- strongest reversibility,
- lower semantic distortion,
- lower implementation brittleness,
- lower complexity explosion risk,
- stronger history/replay integrity where applicable.

## 4. Distinct-finalist requirement

The Owner wants TWO different finalists where possible.

POSITIVE_FINALIST != ROBUSTNESS_FINALIST

If one candidate ranks first on both axes:
- assign it to the axis where its dominance is clearest,
- select the strongest distinct qualified candidate from MAIN_ROUND_PASS_SET for the other axis.

Do not fabricate a weak finalist for symmetry.
If no distinct second finalist genuinely qualifies, mark REVIEW_REQUIRED for Owner review.

## 5. No averaging

Do NOT collapse Positive and Negative profiles into one combined score.

A candidate may be:
- very high upside / high downside,
- medium-high upside / very low downside,
- high on both desirable dimensions,
- or low on both.

The two-finalist design intentionally preserves two different optimization objectives.

## 6. Record requirements

Execution should preserve:
- Candidate Card for each initial model,
- exact initial field count and why,
- common Main-Round Pressure Test results for every initial model,
- Main-Round Pass/Fail ledger with reasons,
- Positive Filter findings for every passer,
- Negative Filter findings for every passer,
- Positive Finalist selection rationale,
- Robustness Finalist selection rationale,
- distinct-finalist check,
- eliminated-candidate preservation register,
- Stage Meeting Memory.

ELIMINATED != FALSE.
It only means not advanced under the current MS0 tournament design.

## 7. Relationship to previous MS0 notes

Earlier notes that referenced four or six initial candidates remain historical working memory.

This note is the CURRENT intended candidate-count policy:

TARGET = 8
MINIMUM = 6 serious candidates
FINALISTS = 2 distinct models selected only from Main-Round passers

Do NOT rewrite prior notes to make them appear to have always used this count.

## 8. Current status

TARGET_INITIAL_CANDIDATES = 8
MINIMUM_SERIOUS_CANDIDATES = 6
COMMON_MAIN_ROUND_REQUIRED = TRUE
FINAL_TARGET = 2 DISTINCT MODELS
POSITIVE_FINALIST_SELECTION_POOL = MAIN_ROUND_PASS_SET_ONLY
ROBUSTNESS_FINALIST_SELECTION_POOL = MAIN_ROUND_PASS_SET_ONLY
MODEL_SEMANTICS = OPEN
OWNER_FINAL_MODEL_DECISION = NOT_PERFORMED

작성시각: 2026-08-20 23:59 KST
