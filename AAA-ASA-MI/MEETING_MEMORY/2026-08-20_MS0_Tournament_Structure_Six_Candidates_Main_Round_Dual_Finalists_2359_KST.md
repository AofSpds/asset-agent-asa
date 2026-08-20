# MS0 Tournament Structure — Six Candidates / Main Round / Dual Finalists

TIME = 2026-08-20 23:59 KST
STATE = WORKING_RESEARCH_MEMORY / MS0_STAGE_DESIGN_CORRECTION / NON_NORMATIVE

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

## 0. Owner correction

The prior two-champion structure is refined.

Do NOT choose Positive Champion / Robustness Champion directly from the initial candidate pool.

Owner wants the following tournament structure:

1. Start with SIX serious model candidates.
2. Run the SAME main-round pressure test on all six.
3. Determine which candidates PASS the common main-round viability gate.
4. ONLY among those main-round passers:
   - select ONE candidate with the greatest demonstrated positive/upside profile,
   - select ONE DISTINCT candidate with the smallest demonstrated negative/downside profile.
5. These two candidates advance to the FINAL ROUND.

In shorthand:

SIX INITIAL CANDIDATES
-> COMMON PRESSURE TEST / MAIN ROUND
-> MAIN-ROUND PASS SET
-> POSITIVE-SELECTION FILTER + NEGATIVE-SELECTION FILTER
-> TWO DISTINCT FINALISTS

## 1. Six-candidate initial field

TARGET_INITIAL_CANDIDATE_COUNT = 6

The six candidates must be:
- serious,
- non-strawman,
- meaningfully distinct,
- plausible representations of the current research space.

Do not create artificial candidates merely to fill six slots.
If fewer than six genuinely distinct candidates can be constructed after reasonable search, record that explicitly for Owner review rather than fabricating weak entries.

However, SIX is the intended target because the Owner prefers enough diversity before pressure-test selection.

## 2. Main round = common viability test

All six candidates face the same core Pressure Test families.

The main round is NOT yet the Positive-vs-Robustness contest.

Its job is to answer:

`Is this candidate sufficiently coherent, useful, and implementable to deserve deeper comparison?`

A candidate may fail the main round because of, for example:
- fatal internal contradiction,
- inability to represent meaningful change/history or an adequate alternative,
- uncontrolled ontology lock-in,
- inability to preserve critical uncertainty/non-closure where required,
- implementation burden so extreme that bounded experimental implementation is not credible,
- triviality / empty-box safety,
- semantic collapse that destroys the research question it is supposed to model.

The exact gate must remain model-neutral and must not require current vocabulary such as Relation/Event/Instance/Boundary as mandatory primitives.

## 3. Main-round pass set

Define:

MAIN_ROUND_PASS_SET = all candidates that pass the common viability gate.

No fixed number of passers is required.

Possible outcomes:
- 6/6 pass,
- 5/6 pass,
- 4/6 pass,
- 3/6 pass,
- 2/6 pass,
- fewer than 2 pass -> REVIEW_REQUIRED before creating a two-model final.

Do not pre-trim to 2–3 candidates before applying the positive/negative selection logic.

## 4. Finalist selection occurs ONLY inside the pass set

### FINALIST P — Positive Champion

Select from MAIN_ROUND_PASS_SET the candidate with the strongest demonstrated positive profile.

Positive dimensions may include:
- explanatory power,
- representational power,
- ability to preserve important worldview possibilities,
- ability to generate useful new research questions,
- elegant compression without destructive simplification,
- extensibility,
- computational leverage,
- first-implementation learning value,
- ability to support future Persona/ASA work without prematurely defining it.

This is NOT a popularity or elegance contest.
The positive finding must be demonstrated by analysis/probes.

### FINALIST R — Robustness Champion

Select from MAIN_ROUND_PASS_SET the candidate with the smallest demonstrated downside / failure surface.

Negative dimensions may include:
- hidden assumptions,
- ontology lock-in,
- semantic distortion,
- irreversibility,
- complexity explosion,
- replay/history fragility,
- implementation brittleness,
- migration cost,
- unfalsifiability,
- accidental commitment to speculative current vocabulary.

The Robustness Champion must still be useful; it already passed the common main-round viability gate.

## 5. Distinct-finalist rule

Owner intends TWO different models to reach the final round.

Therefore:

FINALIST_P != FINALIST_R

If the same candidate ranks first on both axes:
1. determine which axis it dominates more clearly,
2. assign it to that finalist role,
3. choose the strongest DISTINCT candidate for the other role from MAIN_ROUND_PASS_SET.

The second candidate must genuinely qualify under that axis.
Do not manufacture a weak finalist merely for symmetry.

If no second distinct main-round passer can credibly fill the other role:
FINAL_PAIR_STATE = REVIEW_REQUIRED
and escalate the situation for Owner review.

## 6. Positive and negative filters do not decide main-round eligibility by themselves

Important separation:

COMMON_VIABILITY_GATE
!=
POSITIVE_CHAMPION_SELECTION
!=
ROBUSTNESS_CHAMPION_SELECTION

The common viability gate determines who may enter the finalist selection pool.

The positive and negative filters then rank/compare only those qualified candidates for two different finalist roles.

This prevents:
- a spectacular but fundamentally broken model from reaching the final merely because its upside is huge,
- a nearly empty model from reaching the final merely because it has almost no downside.

## 7. No averaging

Do NOT compute a single combined score such as:

POSITIVE_SCORE - NEGATIVE_SCORE

or any weighted average that collapses the two profiles.

Preserve each candidate as a two-axis profile.

A candidate can legitimately be:
- HIGH POSITIVE / HIGH NEGATIVE,
- HIGH POSITIVE / LOW NEGATIVE,
- MEDIUM POSITIVE / VERY LOW NEGATIVE,
- etc.

The final selection intentionally preserves different optimization objectives.

## 8. Revised stage interpretation

Working stage flow becomes:

MS0-00 — Context Reconstruction
->
MS0-01 — Six-Candidate Divergence / Candidate Construction
->
MS0-02 — Main-Round Common Pressure Test across all six
->
MAIN_ROUND_PASS_SET
->
Dual Selection inside pass set:
  Positive Champion + Robustness Champion
->
MS0-03 — FINAL ROUND / Dual Reference Candidate Deepening
->
Later decision on `별` implementation strategy

The previously written MS0-03 Dual Reference Candidate document remains historical working memory.
This note currentizes the selection path leading into MS0-03.
Do NOT rewrite the prior historical note as if this structure had already been specified.

## 9. Required records

MS0 execution should preserve at least:
- six initial Candidate Cards,
- common Main-Round Pressure Test Matrix,
- Main-Round Pass/Fail ledger with reasons,
- full Positive Filter findings for every main-round passer,
- full Negative Filter findings for every main-round passer,
- Positive Champion selection rationale,
- Robustness Champion selection rationale,
- distinct-finalist check,
- eliminated-candidate preservation register,
- Stage Meeting Memory.

Rejected/eliminated candidate != false model.
It means only that it did not advance in this MS0 tournament under the current test design.

## 10. Current status

TARGET_INITIAL_CANDIDATES = 6
FINAL_TARGET = 2 DISTINCT MODELS
FINALIST_P = highest positive/upside among main-round passers
FINALIST_R = lowest negative/downside among main-round passers
MODEL_SEMANTICS = OPEN
OWNER_FINAL_MODEL_DECISION = NOT_PERFORMED

작성시각: 2026-08-20 23:59 KST
