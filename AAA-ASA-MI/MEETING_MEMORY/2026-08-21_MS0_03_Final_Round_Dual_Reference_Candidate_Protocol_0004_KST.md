# MS0-03 — Final Round Dual Reference Candidate Protocol

TIME = 2026-08-21 00:04 KST
STATE = WORKING_RESEARCH_MEMORY / MS0_STAGE_DESIGN / NON_NORMATIVE

PROJECT CONTEXT =
- World Model naming candidate: 한알
- MS0 working milestone name: ONTOGENESIS
- MS0 narrative codename: FIAT LUX / 빛이 있으라
- First implementation artifact naming candidate: 별
- 별 current meaning: first implementation artifact only; NOT necessarily Instance/Event/Relation/etc.
- Candidate tournament target: 8 serious candidates; minimum 6
- Main Round: all serious candidates face the same common viability gate
- Finalists are selected ONLY from MAIN_ROUND_PASS_SET
- Finalist roles:
  - POSITIVE_FINALIST = largest demonstrated upside among Main Round passers
  - ROBUSTNESS_FINALIST = smallest demonstrated downside among Main Round passers

NOT:
- Requirement
- Design Contract
- Canonical ontology
- Final 한알 model
- Production architecture
- Validation receipt
- Owner acceptance

## 0. Purpose

MS0-03 is the FINAL ROUND for the two distinct finalist models selected from the Main Round pass set.

The purpose is NOT to merge the two candidates.

The purpose is to:
1. independently raise each finalist from a model-family candidate into a concrete Reference Candidate,
2. expose each candidate's full internal logic, assumptions, strengths, weaknesses and OPEN surface,
3. run both candidates through the SAME toy worlds, query pack and change scenarios,
4. make their trade-off observable without averaging it away,
5. determine what should be learned next through the first implementation artifact `별`.

The two finalist roles intentionally optimize different objectives.

POSITIVE_FINALIST asks:
`What model gives the largest useful explanatory / representational / research upside while remaining viable enough to test?`

ROBUSTNESS_FINALIST asks:
`What model introduces the smallest dangerous semantic / implementation / lock-in downside while remaining useful enough to test?`

Both are legitimate finalists.

## 1. Entry condition

MS0-03 starts only after MS0-02 produces:

- MAIN_ROUND_PASS_SET,
- common pressure-test evidence for every initial candidate,
- elimination ledger,
- Positive Filter findings for every Main Round passer,
- Negative Filter findings for every Main Round passer,
- POSITIVE_FINALIST selection,
- ROBUSTNESS_FINALIST selection,
- explicit reason why each finalist earned its role,
- unresolved questions inherited from MS0-02.

The finalists must be distinct where possible.

If the same candidate leads both axes:
- preserve it as the stronger role winner,
- select the strongest distinct Main Round passer for the other role only if that distinct candidate remains genuinely viable,
- otherwise record `DISTINCT_SECOND_FINALIST_NOT_PROVEN` and require Owner review rather than manufacturing a weak opponent.

## 2. Independence-before-comparison rule

The two finalists MUST be independently elaborated before they see each other's finalized construction.

TRACK P = POSITIVE_FINALIST
TRACK R = ROBUSTNESS_FINALIST

Each receives:
- the same reconstructed research context,
- the same Owner-explicit constraints,
- the same DO-NOT-ASSUME register,
- the same Main Round evidence about itself,
- the same required output template.

Before independent construction is complete:
- Track P may NOT import conservative choices from Track R merely to hide risk,
- Track R may NOT import expressive machinery from Track P merely to raise capability,
- neither track may become a disguised hybrid.

Reason:
The research value of the final round depends on preserving two genuinely different model hypotheses.

## 3. Required Reference Candidate package — BOTH finalists

Each finalist must produce a complete REFERENCE_CANDIDATE_PACKET.

### 3.1 MODEL THESIS

State compactly:
- what the candidate treats as primary,
- how it represents a modeled world,
- how change occurs,
- how history is represented,
- how uncertainty/non-closure is represented,
- what it deliberately does NOT assume.

### 3.2 MINIMUM CONCEPT SET

For every concept actually used, classify as:
- PRIMARY
- DERIVED
- VIEW / PROJECTION
- OPTIONAL EXTENSION
- NOT USED
- UNRESOLVED

Previously discussed vocabulary such as:
Relation / Event / Instance / Process / Boundary / Memory / Materialization / Succession / Scope / Scale / Perspective / Standpoint / Authority
is candidate vocabulary only.

No finalist receives credit merely for preserving old words.

If a concept is removed, merged or demoted, record:
- why,
- what explanatory value is lost,
- what complexity is removed,
- whether the change is reversible.

### 3.3 COMPUTATIONAL SHAPE

Describe enough structure that an independent implementer could build a toy version without inventing the missing core semantics.

May include, only where appropriate:
- fact/state representation,
- transition/update rules,
- temporal/history representation,
- derivation/materialization rules,
- uncertainty/conflict representation,
- composition/decomposition representation,
- scope/view handling,
- predecessor/successor-like handling,
- identity-like handling if the model needs it.

Do NOT select a database/vendor/framework merely because it is convenient.

### 3.4 INVARIANT / NON-ASSUMPTION SURFACE

Each finalist must state:
- what it must always preserve for its own coherence,
- what it intentionally refuses to decide,
- what can change in successor model versions,
- which commitments are expensive to reverse.

### 3.5 QUERY SURFACE

Define a minimum set of questions the model can answer or can explicitly reject/reformulate.

Examples:
- What is represented now?
- What changed?
- What was represented/claimed at time T?
- What remains unknown, undefined or disputed?
- What differs under another declared scope/scale/perspective?
- What structural history led here?
- What assumptions are being used to answer this query?

The model may reject the framing of a query, but must explain its alternative semantics.

### 3.6 ASSUMPTION REGISTER

Every implementation-enabling assumption must include:
- assumption_id,
- statement,
- source = existing hypothesis / Owner-explicit / Codex proposal,
- why required,
- semantic cost,
- implementation cost,
- reversibility,
- what fails if false,
- whether Owner review is required before promotion.

### 3.7 OPEN SURFACE

Explicitly classify unresolved areas as:
- HEALTHY_EXTENSIBILITY,
- DELIBERATE_NON_COMMITMENT,
- MISSING_SEMANTICS,
- IMPLEMENTATION_BLOCKER,
- RESEARCH_QUESTION.

OPEN is not automatically a defect.

## 4. Same-world comparison protocol

After both Reference Candidate packets are independently complete, expose both finalists to the SAME comparison environment.

Do not tailor easy scenarios to one model.

### 4.1 TOY WORLD A — Currentization without history rewrite

A representation/interpretation changes over time.

Required observations:
- historical input/state remains reconstructable,
- current output can differ,
- no future semantic backwrite is required,
- the candidate can explain what exactly changed.

### 4.2 TOY WORLD B — Non-closure

At least one matter is:
UNKNOWN / UNDEFINED / DISPUTED / unresolved equivalent.

Later evidence may arrive.

Required observations:
- unresolved state is not silently collapsed to false/absent,
- conflicting claims can remain visible if the model supports them,
- later resolution does not erase earlier uncertainty history.

### 4.3 TOY WORLD C — Structural transformation

A modeled configuration is transformed in a way analogous to:
- composition,
- decomposition,
- regrouping,
- split/fission,
- merge/recomposition.

Do NOT force Instance/Event/Relation vocabulary.

Observe:
- what the model treats as persisting,
- what it treats as new,
- what it refuses to identify,
- hidden continuity/identity assumptions.

### 4.4 TOY WORLD D — Multiple declared views

Where supported, hold substrate/history fixed and change one declared modeling condition such as scope/scale/perspective.

Observe:
- what remains invariant,
- what changes,
- how disagreement between views is represented,
- whether the model becomes trivially relativistic.

### 4.5 TOY WORLD E — Vocabulary removal challenge

Remove or demote at least one previously discussed candidate concept.

Examples only:
- no Boundary primitive,
- no Instance primitive,
- no Event primitive,
- no Relation primitive.

Observe whether the model remains coherent and what is lost.

## 5. Common implementation-neutral probes

Each finalist must provide pseudocode, formal notation, executable sketch, or another bounded computational demonstration sufficient to show that its semantics are operational rather than purely rhetorical.

Required minimum probes:
- reconstruct prior state/history,
- perform one update/currentization,
- preserve one unresolved/conflicting state,
- answer at least three common queries,
- show one structural transformation.

Implementation language/technology is secondary.

The probe is NOT `별` unless later promoted.

## 6. Positive / Negative evaluation in the Final Round

The finalist role does NOT exempt a candidate from the opposite filter.

For BOTH candidates record separately:

POSITIVE_FINAL_ROUND_FINDINGS =
- strongest explanatory gain,
- strongest representational gain,
- strongest simplification,
- strongest extensibility/research gain,
- what becomes possible that was previously difficult.

NEGATIVE_FINAL_ROUND_FINDINGS =
- strongest semantic risk,
- strongest hidden assumption,
- strongest irreversibility/lock-in risk,
- strongest computational burden,
- strongest falsifiability concern,
- what future change could force redesign.

Do NOT calculate one combined score.

## 7. Cross-examination

Only after independent construction and same-world tests:

### 7.1 Positive Finalist challenges Robustness Finalist

Ask:
- What important phenomena do you fail to express?
- Are you robust partly because you avoid useful commitments?
- Which future research questions become inaccessible?
- Will extension pressure eventually recreate the complexity you removed?
- Would `별` built on you teach us enough?

### 7.2 Robustness Finalist challenges Positive Finalist

Ask:
- Which expressive mechanisms are actually necessary?
- Which are speculative conveniences?
- Where does ontology lock-in accumulate?
- Which assumptions are expensive to reverse?
- Could a smaller model reproduce most of your value?
- Would `별` built on you fail because the model is too ambitious?

Do NOT force reconciliation.

Disagreement is a research result.

## 8. Meeting Memory requirements

MS0-03 requires exactly three principal Stage Meeting Memories:

1. `MS0-03_TRACK_P_POSITIVE_FINALIST_MEETING_MEMORY`
2. `MS0-03_TRACK_R_ROBUSTNESS_FINALIST_MEETING_MEMORY`
3. `MS0-03_FINAL_ROUND_COMPARISON_MEETING_MEMORY`

Each track memory records:
- entering thesis,
- chosen minimum concepts,
- rejected alternatives,
- positive findings,
- negative findings,
- assumptions introduced,
- unexpected simplifications,
- unexpected complexity,
- unresolved issues,
- changes in current weighting,
- handoff state.

Comparison memory records:
- same-world results,
- cross-examination,
- non-overlapping strengths,
- non-overlapping weaknesses,
- shared failures,
- assumptions that dominate the comparison,
- what was learned that could not be seen in the Main Round.

Do not request or expose private chain-of-thought.
Record reviewable decisions, observations, evidence and alternatives.

## 9. Final Round output

Required:

### 9.1 DUAL_REFERENCE_CANDIDATE_TABLE

For both finalists include:
- finalist identity,
- finalist role,
- model thesis,
- primary concepts,
- derived/view concepts,
- strongest positive finding,
- strongest negative finding,
- assumption burden,
- implementation burden,
- semantic reversibility,
- open-surface quality,
- first-implementation suitability,
- biggest unknown,
- what we would learn by implementing it.

### 9.2 SHARED_FAILURE_REGISTER

Failures observed in BOTH finalists are especially important.

They may indicate:
- an underspecified ASA-MI/한알 research question,
- a bad common assumption,
- a missing model family,
- or a genuinely hard problem independent of model choice.

### 9.3 NON_OVERLAPPING_VALUE_REGISTER

Record capabilities/insights unique to each finalist.

Do NOT erase them through premature hybridization.

### 9.4 BYUL_OPTIONS

Each finalist must propose:

`IF_THIS_MODEL_IS_USED_FOR_BYUL:`
- smallest meaningful first implementation artifact,
- what it demonstrates,
- what it does NOT demonstrate,
- expected complexity,
- most important falsification signal,
- likely next experiment if it succeeds,
- likely next move if it fails.

## 10. MS0-03 Exit condition

MS0-03 is complete when:

1. both finalists are independently concretized as Reference Candidates,
2. both face the same toy worlds and common probes,
3. both receive positive and negative final-round evaluation,
4. both explicitly expose assumptions and OPEN surfaces,
5. both cross-examine the other after independent completion,
6. trade-offs remain visible without averaging,
7. shared failures and unique values are separately recorded,
8. each has a concrete `별` option,
9. Owner/ASA-MI can decide what experiment should come next without pretending a final 한알 ontology has been proven.

MS0-03 does NOT select the final 한알 model.

## 11. Natural next step after MS0-03

The next stage should be an implementation-strategy decision, not automatic coding.

Possible outcomes:
- implement one `별` using Positive Finalist,
- implement one `별` using Robustness Finalist,
- implement two comparative `별` variants,
- perform one more cheap discriminating probe before `별`,
- return to model search if both finalists expose the same blocking failure.

No option is pre-authorized by this Stage design.

## 12. Suggested research budget

Suggested budget: approximately 120–180 minutes.

Possible allocation:
- 40–60 min independent Track P construction,
- 40–60 min independent Track R construction,
- 20–30 min same-world tests,
- 20–30 min cross-examination and comparison.

Exit condition has priority over elapsed time.

## 13. Current status

This document is Stage planning only.
No finalist has been executed, selected or validated by this note.

작성시각: 2026-08-21 00:04 KST
