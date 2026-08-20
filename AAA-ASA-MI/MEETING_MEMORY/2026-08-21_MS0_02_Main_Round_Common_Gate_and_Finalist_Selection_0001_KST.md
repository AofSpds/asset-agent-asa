# MS0-02 — Main Round Common Gate + Finalist Selection

TIME = 2026-08-21 00:01 KST
STATE = WORKING_RESEARCH_MEMORY / MS0_STAGE_DESIGN / NON_NORMATIVE

PROJECT CONTEXT =
- World Model naming candidate: 한알
- MS0 working milestone name: ONTOGENESIS
- Narrative codename: FIAT LUX / 빛이 있으라
- First implementation artifact naming candidate: 별
- 별 = first implementation artifact only; NOT yet Instance/Event/Relation/etc.
- Candidate tournament target = 8 serious model candidates
- Candidate tournament minimum = 6 serious model candidates if 8 genuinely distinct candidates cannot be produced

NOT:
- Requirement
- Design Contract
- Canonical ontology
- Final model selection
- Validation receipt
- Owner acceptance

## 0. Successor correction / current tournament structure

This note CURRENTIZES the earlier MS0-02/MS0-03 tournament design without rewriting prior historical notes.

Current intended flow:

1. MS0-01 produces TARGET 8 / MINIMUM 6 serious, non-strawman model candidates.
2. ALL serious candidates enter the SAME MS0-02 Main Round Common Pressure Test.
3. Only candidates that satisfy the Main Round Common Gate enter the MAIN_ROUND_PASS_SET.
4. ONLY the MAIN_ROUND_PASS_SET receives the independent Positive Filter and Negative Filter finalist evaluation.
5. Two DISTINCT finalists are selected where viable:
   - POSITIVE_FINALIST = greatest demonstrated upside among main-round passers.
   - ROBUSTNESS_FINALIST = smallest demonstrated downside among main-round passers.
6. MS0-03 independently constructs both finalists as Reference Candidates before comparison.

Do NOT select finalists before common-gate survival has been demonstrated.

## 1. Main Round principle

The Main Round does NOT ask:
- Which candidate is most exciting?
- Which candidate is safest?
- Which candidate resembles current vocabulary most closely?

It asks only:

`IS THIS MODEL COHERENT, NON-TRIVIAL, RESEARCH-USEFUL, AND IMPLEMENTABLE ENOUGH TO DESERVE DEEPER COMPARISON?`

The gate must be neutral between expressive/high-upside models and conservative/low-downside models.

Vocabulary fit is not a pass criterion.

Relation / Event / Instance / Process / Boundary / Memory / Materialization / Succession / Scope / Scale / Perspective / Authority remain candidate vocabulary only.

## 2. Common Gate dimensions

Every candidate receives the SAME gate questions.

Per gate state:
- PASS
- PARTIAL_WITH_EXPLICIT_LIMIT
- FAIL
- NOT_APPLICABLE_WITH_JUSTIFICATION

No numeric total score is required for Main Round survival.

### G1 — INTERNAL COHERENCE [CORE]

The candidate must provide:
- a clear model thesis,
- explicit primary/derived concepts or equivalent structure,
- internally consistent update/change rules,
- declared assumptions.

FAIL if:
- identical conditions produce contradictory semantics without conflict representation,
- critical behavior depends on mutually incompatible assumptions,
- the model cannot explain its own primitive/derived distinction or equivalent.

### G2 — CHANGE + HISTORICAL RECONSTRUCTABILITY [CORE]

The candidate must support some coherent way to represent change while preserving the ability to reconstruct prior model states/claims/records.

It need not use `Event`, `Instance`, or `Succession`.

PASS requires:
- prior state/representation remains recoverable,
- currentization does not silently rewrite historical inputs,
- later semantics do not automatically erase earlier semantic state.

### G3 — NON-CLOSURE / UNCERTAINTY / CONFLICT [CORE]

The candidate must preserve meaningful non-closure or provide a clearly justified equivalent mechanism.

At minimum it must not silently force:
- UNKNOWN -> FALSE,
- UNDEFINED -> INVALID,
- DISPUTED -> one side selected without evidence.

Exact vocabulary is optional.

### G4 — BOUNDED IMPLEMENTABILITY [CORE]

A small research prototype must be reasonably implementable without first building large infrastructure.

PASS requires:
- a bounded toy implementation can be described,
- critical computational operations are identifiable,
- no new DB/SaaS/agent framework/ontology platform is required merely to make the model testable.

High complexity is allowed if bounded experimentation remains possible.

### G5 — EXPLICIT ASSUMPTION + REVISION SURFACE [CORE]

The candidate must expose assumptions rather than hiding them inside implementation choices.

PASS requires:
- assumptions are identifiable,
- expensive-to-reverse assumptions are visible,
- current semantics can in principle be revised/currentized,
- historical meaning is not retroactively rewritten merely because the model changes.

### G6 — NON-TRIVIAL CONSTRAINT / FALSIFIABILITY [SUPPORTING]

The candidate must constrain something.

FAIL tendency:
- the model can represent every possible outcome with equal ease and therefore predicts/excludes nothing,
- all contradictions become perspective differences without testable conditions,
- the model is only an empty container/schema.

PARTIAL is acceptable if falsification surface is still being developed.

### G7 — LOW-LEVEL WORLD-MODEL GENERALITY [SUPPORTING]

The candidate should plausibly operate below Persona/ASA-specific semantics.

Check that it is not accidentally hard-coded around:
- Persona identity,
- investment workflows,
- current AAA authority structures,
- current naming metaphors.

Persona/ASA use may be an example, not the ontology.

### G8 — VIEW / SCALE / STRUCTURAL-CHANGE COMPATIBILITY [SUPPORTING]

The candidate should either:
- support multiple useful representations across scope/scale/perspective/composition,
- OR explicitly demonstrate why those concepts are unnecessary and how equivalent phenomena are represented.

The gate does NOT require `Scope`, `Scale`, `Perspective`, or `Boundary` as primitives.

## 3. Main Round pass rule

A candidate enters MAIN_ROUND_PASS_SET only if:

MANDATORY:
- G1 = PASS
- G2 = PASS
- G3 = PASS or PARTIAL_WITH_EXPLICIT_LIMIT where the limit is non-fatal and extensible
- G4 = PASS
- G5 = PASS

AND:
- no FATAL BLOCKER is present,
- at least TWO of G6/G7/G8 are PASS,
- any remaining G6/G7/G8 state is not FAIL due to a fundamental contradiction.

This is deliberately not a weighted average.

A candidate cannot compensate for a failed CORE gate by having extraordinary strengths elsewhere.

## 4. Fatal blockers

Any one of the following normally blocks Main Round passage unless explicitly reclassified after review:

FATAL-01
Historical reconstruction is impossible without rewriting prior records using future/current semantics.

FATAL-02
Unknown/conflict necessarily collapses to false/absent/invalid with no coherent extension path.

FATAL-03
No bounded prototype can test the candidate without first constructing major infrastructure.

FATAL-04
A hidden, irreversible semantic assumption is required for basic coherence and cannot be isolated.

FATAL-05
The model is effectively unfalsifiable / unconstrained: every result can be explained after the fact.

FATAL-06
The model only works by treating currently OPEN candidate vocabulary as unquestionable truth while hiding that commitment.

FATAL-07
The model is actually Persona/ASA/domain architecture disguised as a low-level world model.

FATAL-08
Naming metaphors (`한알`, `별`, `ONTOGENESIS`, `FIAT LUX`, etc.) are used as formal semantic evidence.

A fatal blocker is a research finding, not a claim that the model is globally false.

## 5. Main Round required artifacts

For EVERY candidate:

### 5.1 MAIN_ROUND_CARD

Fields:
- CANDIDATE_ID
- MODEL_FAMILY
- MODEL_THESIS
- DECLARED_ASSUMPTIONS
- G1..G8 RESULT
- FATAL_BLOCKERS
- PRESSURE_TEST_OBSERVATIONS
- SURPRISING_STRENGTHS
- SURPRISING_FAILURES
- MAIN_ROUND_VERDICT
- REASON_FOR_VERDICT
- KEEP_AS_COUNTERMODEL = TRUE/FALSE

### 5.2 MAIN_ROUND_MATRIX

One matrix comparing all TARGET 8 / MINIMUM 6 candidates using G1..G8 and fatal blockers.

### 5.3 ELIMINATION_LEDGER

Every non-passing candidate must remain recorded with:
- why it did not pass,
- what valuable idea should be preserved,
- what future change could justify revival.

`NOT PASSED != FALSE MODEL`.

## 6. Positive / Negative finalist filters

ONLY MAIN_ROUND_PASS_SET enters finalist selection.

Both filters evaluate EVERY main-round passer.

The filters remain independent.

### POSITIVE FILTER — upside

Evaluate evidence for:
- explanatory reach,
- representational power,
- useful conceptual compression,
- ability to unify without erasing important distinctions,
- ability to expose new research questions,
- extensibility,
- ability to generate useful implementation experiments,
- reuse/adaptation of strong prior modeling traditions,
- human-familiar + structural projection potential where relevant,
- surprising simplification or new capability.

Output:
`POSITIVE_PROFILE`

Do not subtract negative findings during this evaluation.

### NEGATIVE FILTER — downside

Evaluate evidence for:
- hidden assumptions,
- semantic distortion,
- ontology lock-in,
- irreversibility,
- complexity explosion,
- recursive/combinatorial risk,
- replay/history fragility,
- view/scale relativism risk,
- implementation burden,
- migration/evolution cost,
- hidden identity/global-clock/binary-truth/schema assumptions,
- God Object / universal primitive risk.

Output:
`NEGATIVE_PROFILE`

Do not discount a weakness merely because the candidate has high upside.

## 7. Finalist selection rule

After BOTH profiles are complete for every main-round passer:

### POSITIVE_FINALIST
Select the DISTINCT candidate with the strongest demonstrated positive profile.

Question:
`Which viable model opens the largest useful world-model/research space?`

### ROBUSTNESS_FINALIST
Select the DISTINCT candidate with the smallest demonstrated negative profile while remaining substantively useful.

Question:
`Which viable model introduces the least dangerous commitment/failure surface?`

Do NOT combine the profiles into one score.

## 8. Same-candidate case

If one candidate is best on BOTH axes:

1. record that it dominates both axes,
2. assign it to the axis where its dominance is clearest,
3. search MAIN_ROUND_PASS_SET for the strongest DISTINCT finalist on the other axis,
4. require the alternate finalist to have genuinely credible evidence on that axis.

If no distinct qualified alternate exists:
- do NOT fabricate one,
- set `DISTINCT_SECOND_FINALIST = REVIEW_REQUIRED`,
- preserve the dominance finding for Owner review.

## 9. Candidate-count contingency

TARGET_CANDIDATES = 8
MINIMUM_SERIOUS_CANDIDATES = 6

If fewer than 6 genuinely different non-strawman candidates can be produced:
- record `DIVERGENCE_INSUFFICIENT`,
- explain why the model space appears constrained,
- do not fabricate filler candidates.

If 8+ serious candidates naturally emerge, more than 8 may be briefly inventoried, but the main round should normally be bounded to the 8 most materially distinct candidates for comparability and research budget.

## 10. Meeting Memory design

Required memories:

1. `MS0-02_MAIN_ROUND_MEETING_MEMORY`
   - expectations,
   - common attacks,
   - candidate-by-candidate failures/surprises,
   - pass/fail reasons,
   - eliminated-but-valuable ideas.

2. `MS0-02_FINALIST_FILTER_MEETING_MEMORY`
   - Positive profiles,
   - Negative profiles,
   - why each finalist leads its own axis,
   - same-candidate/tie handling,
   - unresolved issues.

Do not require or expose private chain-of-thought.
Record reviewable observations, decisions, alternatives, evidence and assumptions.

## 11. Exit condition

MS0-02 is complete when:

- TARGET 8 / MINIMUM 6 serious candidates have received the same common gate where available,
- MAIN_ROUND_PASS_SET is explicit,
- eliminated candidates remain in the Elimination Ledger,
- every passer has independent Positive and Negative profiles,
- one Positive Finalist and one Robustness Finalist are selected where two distinct qualified models exist,
- unresolved finalist ambiguity is explicitly REVIEW_REQUIRED rather than hidden,
- both finalist packets are ready for MS0-03 independent Reference Candidate construction.

## 12. Handoff to MS0-03

MS0-03 receives:
- MAIN_ROUND_PASS_SET,
- Main Round Matrix,
- Elimination Ledger,
- Positive profiles,
- Negative profiles,
- POSITIVE_FINALIST,
- ROBUSTNESS_FINALIST,
- Assumption/Failure registers,
- both MS0-02 Meeting Memories.

MS0-03 must NOT hybridize the finalists before independently elaborating them.

작성시각: 2026-08-21 00:01 KST
