# MS0-03 — Dual Reference Candidate Construction

TIME = 2026-08-20 23:55 KST
STATE = WORKING_RESEARCH_MEMORY / MS0_STAGE_DESIGN / NON_NORMATIVE

PROJECT CONTEXT =
- World Model naming candidate: 한알
- MS0 working milestone name: ONTOGENESIS
- MS0 narrative codename: FIAT LUX / 빛이 있으라
- First implementation artifact naming candidate: 별
- `별` current meaning: first implementation artifact only; NOT necessarily Instance/Event/Relation/etc.
- ASA is currently envisioned as a later/full Persona/Application implementation on top of 한알; the Adam analogy is narrative only.

NOT:
- Requirement
- Design Contract
- Canonical ontology
- Model selection final decision
- Validation receipt
- Owner acceptance

## 0. Purpose

MS0-03 takes the results of Divergence + Pressure Test and intentionally preserves TWO different model directions instead of collapsing them into one average winner.

The two survivor roles are:

1. POSITIVE_CHAMPION
   - the candidate with the greatest demonstrated upside,
   - strongest explanatory/representational power,
   - largest useful research surface,
   - strongest ability to make new things possible.

2. ROBUSTNESS_CHAMPION
   - the candidate with the smallest demonstrated downside,
   - fewest dangerous hidden assumptions,
   - lowest ontology lock-in / irreversibility / semantic distortion,
   - strongest practical robustness and implementation conservatism.

The two roles MUST remain distinct through MS0-03.

DO NOT hybridize them merely because combining their strengths sounds attractive.

The purpose of this stage is to make BOTH candidates concrete enough that a later implementation experiment can fairly compare them.

## 1. Entry condition

MS0-03 starts only after the prior stages provide:

- MS0-00 reconstructed research state,
- MS0-01 serious model-family set,
- MS0-02 Pressure Test results,
- Positive Filter findings,
- Negative Filter findings,
- Dual Survivor Gate result,
- Failure Atlas,
- Assumption Cost Register,
- unresolved questions.

At least two non-strawman candidates should remain.

### Same-candidate exception

If one candidate ranks first under BOTH Positive and Robustness criteria, do NOT automatically pass only one model.

Select:
- that candidate for whichever role it most clearly dominates,
- plus the strongest DISTINCT runner-up that passes the minimum cross-gate.

Reason:
MS0 intentionally preserves contrasting model hypotheses long enough to learn from implementation pressure.

If no distinct runner-up can pass minimum viability, record that as an explicit result rather than fabricating a second candidate.

## 2. Dual-track principle

Run two independent tracks:

TRACK P = POSITIVE_CHAMPION
TRACK R = ROBUSTNESS_CHAMPION

Each track must receive the SAME reconstructed research context and the SAME minimum evaluation questions.

However, each track is allowed to optimize for its own role.

TRACK P asks:
`How much of the current worldview and future research space can this model express or enable without becoming incoherent?`

TRACK R asks:
`How little semantic commitment and failure surface can this model introduce while still being useful enough to implement?`

Neither track may redefine the other track's objective.

## 3. Minimum cross-gates

A model cannot qualify merely by maximizing one axis.

### Positive Champion minimum negative gate

The Positive Champion MUST NOT have:
- a known fatal contradiction that prevents even a bounded prototype,
- an assumption whose failure destroys all historical reconstruction,
- an unrecoverable ontology commitment with no explicit justification,
- implementation complexity so high that `별` cannot reasonably be attempted as a research artifact.

High downside is allowed.
Fatal non-viability is not.

### Robustness Champion minimum positive gate

The Robustness Champion MUST provide meaningful capability beyond an empty or trivial model.

At minimum it must demonstrate:
- useful representation of change/history or equivalent behavior,
- meaningful uncertainty/non-closure handling or an explicit alternative,
- enough expressiveness to support a first implementation artifact,
- a plausible growth path toward richer future modeling.

A safe empty box does not qualify.

## 4. Required construction depth for BOTH candidates

Each candidate must be raised from a model-family description into a REFERENCE CANDIDATE.

Required outputs for each:

### 4.1 MODEL THESIS

A compact statement of:
- what the model fundamentally treats as primary,
- how the modeled world is represented,
- how change occurs,
- what is intentionally NOT assumed.

### 4.2 MINIMUM CONCEPT SET

List the minimum concepts the candidate actually needs.

Important:
Previously discussed words such as Relation, Event, Instance, Process, Boundary, Memory, Materialization, Succession, Scope, Scale, Perspective, Standpoint, Authority are candidates only.

For every concept mark one of:
- PRIMARY
- DERIVED
- VIEW / PROJECTION
- OPTIONAL EXTENSION
- NOT USED
- UNRESOLVED

No candidate receives points merely for preserving current vocabulary.

### 4.3 FORMAL / COMPUTATIONAL SHAPE

Describe enough structure that another engineer/researcher could implement a toy model without inventing the missing architecture.

May include where appropriate:
- state/fact representation,
- transition/update semantics,
- temporal/history representation,
- derivation/materialization rules,
- uncertainty/conflict representation,
- composition/decomposition handling,
- scope/view handling,
- identity/succession-like handling if used.

Do NOT force a specific technology stack yet.

### 4.4 MINIMUM QUERY SURFACE

For each candidate define a small set of example questions the model should be able to answer.

Examples only:
- What is currently represented?
- What changed?
- What was believed/represented at time T?
- What remains unknown or disputed?
- How does a different scope/scale/perspective alter the output?
- What predecessor/successor-like relation exists?

The candidate may reject or reformulate these questions if its semantics require it, but must explain why.

### 4.5 THREE OR MORE TOY SCENARIOS

Each candidate must work through the SAME small scenarios where possible.

At least:

SCENARIO A — CURRENTIZATION WITHOUT HISTORY REWRITE
A current interpretation changes while prior records remain reconstructable.

SCENARIO B — NON-CLOSURE
Something remains UNKNOWN / UNDEFINED / DISPUTED and later may or may not resolve.

SCENARIO C — STRUCTURAL CHANGE
A modeled configuration is transformed, split, merged, regrouped, or otherwise changed without presupposing a final ontology.

Optional:
SCENARIO D — MULTIPLE VIEW / SCOPE / SCALE
Same substrate/history yields different useful representation depending on a declared modeling condition.

The scenario language must be adapted to each model rather than forcing current vocabulary.

### 4.6 ASSUMPTION REGISTER

Every implementation-enabling assumption must record:
- assumption statement,
- reason needed,
- source: existing hypothesis vs CODEX proposal,
- semantic cost,
- reversibility,
- what fails if assumption is false,
- Owner review relevance.

### 4.7 OPEN SURFACE

Explicitly list what the candidate leaves unresolved.

OPEN is not a defect by default.

Evaluate whether the open surface is:
- healthy extensibility,
- missing semantics,
- deliberate non-commitment,
- or implementation blocker.

## 5. Independent meeting-memory requirement

MS0-03 must preserve the research process of BOTH tracks separately.

Required Stage memories:

1. `MS0-03_TRACK_P_POSITIVE_CHAMPION_MEETING_MEMORY`
2. `MS0-03_TRACK_R_ROBUSTNESS_CHAMPION_MEETING_MEMORY`
3. `MS0-03_DUAL_TRACK_COMPARISON_MEETING_MEMORY`

Each track memory must record:
- entering thesis,
- design choices,
- rejected alternatives,
- positive discoveries,
- negative discoveries,
- new assumptions,
- unexpected simplifications,
- unexpected complexity,
- unresolved issues,
- changes in current weighting,
- handoff state.

Do not require or expose private chain-of-thought.
Record reviewable decisions, observations, evidence and alternatives.

## 6. No contamination before independent construction

Track P and Track R should be independently elaborated FIRST.

Do not allow:
- P to import R's conservative choices merely to hide its weaknesses,
- R to import P's expressive machinery merely to raise its feature count,
- either track to become a disguised hybrid before comparison.

Only after both candidate packets are complete should cross-comparison begin.

## 7. Cross-examination

After independent construction, each candidate must challenge the other.

### P -> R questions

The Positive Champion should ask the Robustness Champion:
- What important phenomena or research questions can you NOT express?
- Are you robust because you avoid making useful commitments?
- Will extension pressure eventually force a redesign?
- What future `별` experiments become impossible or uninformative under your minimalism?

### R -> P questions

The Robustness Champion should ask the Positive Champion:
- Which expressive features are speculative rather than necessary?
- Where can complexity or ontology lock-in accumulate?
- Which assumptions are expensive to reverse?
- Could a smaller model reproduce most of your value?

Each answer should be recorded without forcing agreement.

## 8. Required final comparison

Create a DUAL_REFERENCE_CANDIDATE_TABLE with at least:

- candidate identity,
- champion role,
- model thesis,
- primary concepts,
- derived concepts,
- strongest positive finding,
- strongest negative finding,
- assumption burden,
- implementation burden,
- semantic reversibility,
- open-surface quality,
- first-implementation suitability,
- biggest unknown,
- what we would learn by building it.

Do NOT output one combined score.

## 9. Relationship to `별`

MS0-03 does NOT automatically create `별`.

At exit, each candidate must propose:

`IF_THIS_MODEL_IS_USED_FOR_BYUL:`
- smallest meaningful implementation artifact,
- what it would demonstrate,
- what it would deliberately NOT demonstrate,
- expected implementation complexity,
- most important falsification signal.

Possible later choices include:
- build one `별` using one candidate,
- build two parallel `별` variants,
- build one candidate first and preserve the other as countermodel,
- postpone implementation if neither candidate is ready.

No choice is authorized by MS0-03 itself.

## 10. Exit condition

MS0-03 is complete when:

1. a Positive Champion is concretized as a Reference Candidate,
2. a Robustness Champion is concretized as a distinct Reference Candidate where possible,
3. both satisfy their minimum cross-gates,
4. both have explicit assumptions and OPEN surfaces,
5. both have been independently constructed before cross-examination,
6. their trade-off is visible without averaging it away,
7. each has a concrete `별` implementation proposal,
8. Owner/ASA-MI can understand exactly what would be learned by implementing either one.

MS0-03 does NOT select the final 한알 model.

## 11. Suggested research budget

Suggested budget: approximately 90–150 minutes.

Possible allocation:
- 35–55 min Track P,
- 35–55 min Track R,
- 20–40 min cross-examination + comparison.

Exit condition has priority over elapsed time.

## 12. Handoff direction

The natural next stage should NOT yet assume hybridization.

Likely next questions:
- Do we need minimal executable probes of both Reference Candidates?
- Should `별` be one implementation or two comparative implementations?
- Which assumptions can be tested cheaply before implementation?
- What Owner review is needed before implementation commitment?

These should be decided in the next MS0 stage.

작성시각: 2026-08-20 23:55 KST
