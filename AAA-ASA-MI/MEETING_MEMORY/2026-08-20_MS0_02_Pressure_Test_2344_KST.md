# MS0-02 — Pressure Test

TIME = 2026-08-20 23:44 KST
STATE = WORKING_RESEARCH_MEMORY / MS0_STAGE_DESIGN / NON_NORMATIVE

PROJECT CONTEXT =
- World Model naming candidate: 한알
- MS0 working milestone name: ONTOGENESIS
- MS0 narrative codename: FIAT LUX / 빛이 있으라
- First implementation artifact naming candidate: 별
- 별 current meaning: first implementation artifact only; NOT necessarily Instance/Event/Relation/etc.

NOT:
- Requirement
- Design Contract
- Canonical ontology
- Model selection decision
- Validation receipt
- Owner acceptance

## 0. Purpose

MS0-02 is the adversarial pressure-test stage applied to the serious model families that survive MS0-01 Divergence.

The purpose is NOT to select the most elegant model by preference.

The purpose is to expose where each candidate:
- preserves the current research worldview,
- silently collapses distinctions,
- requires arbitrary assumptions,
- becomes computationally expensive,
- becomes unfalsifiable,
- or cannot represent important uncertainty/change/history behavior.

A candidate may fail.
A useful failure is a valid research result.

## 1. Entry condition

MS0-02 starts only after MS0-01 has produced:
- >= 4 serious model-family candidates explored,
- 2–3 surviving candidates worth deeper testing,
- Cross-Model Matrix,
- Semantic Collapse Map,
- New Questions Register,
- MS0-01 Stage Meeting Memory.

If MS0-01 cannot produce at least two non-strawman surviving candidates, MS0-02 should first record that divergence failed or the concept space is already unusually constrained.

## 2. Pressure-test principle

Do NOT test only whether a candidate can encode current vocabulary.

Test whether it can preserve the research behavior we care about while allowing current vocabulary itself to be revised, merged, decomposed, or discarded.

Candidate vocabulary previously discussed includes Relation, Event, Instance, Process, Boundary, Memory, Standpoint, Materialization, Succession, Scope, Scale, Perspective, Authority, etc.

These are NOT mandatory primitives.

The pressure test must therefore distinguish:

VOCABULARY FIT
!=
SEMANTIC FIT
!=
COMPUTATIONAL FIT

## 3. Mandatory attack families

Each surviving candidate must be tested against at least the following attack families.

### A. CHANGE WITHOUT RETROACTIVE REWRITE

Can current interpretation/model state change while historical records remain intact?

Test:
- current meaning changes,
- predecessor state/history remains reconstructable,
- no silent semantic backwrite.

Failure modes:
- current state requires rewriting historical facts,
- old interpretation disappears,
- replay becomes dependent on future semantics.

### B. UNKNOWN / UNDEFINED / DISPUTED

Can the model preserve epistemic non-closure without treating uncertainty as false or null noise?

Test at minimum:
- UNKNOWN != FALSE/ABSENT,
- UNDEFINED != INVALID,
- DISPUTED can preserve conflicting claims,
- later resolution does not erase prior uncertainty/dispute history.

### C. MULTIPLE POSSIBLE PRIMITIVE CHOICES

Can the candidate avoid requiring the current research vocabulary as ontology?

Attack:
- remove or demote Boundary,
- remove or demote Instance,
- collapse Event into derived transition,
- collapse Relation into derived structure,
- replace one candidate concept with a view/projection.

Observe whether the model remains coherent.

### D. STRUCTURE / CHANGE SEPARATION

Can the model distinguish persistent/structural aspects from transitions/processes if such a distinction is useful?

Also test the opposite:
Can the candidate remain coherent if those distinctions are not fundamental?

Do NOT assume Event != Relation or Event = Relation.

### E. SCOPE / SCALE / PERSPECTIVE

Can the model support different useful materializations/interpretations across Scope, Scale, or Perspective without making every statement trivially relative?

Attack questions:
- What remains invariant across views?
- What is view-local?
- How is contradiction represented?
- Can two views disagree without one being silently overwritten?
- Does adding Perspective make the model unfalsifiable?

### F. COMPOSITION / DECOMPOSITION

Can a modeled whole be represented as composed, decomposed, regrouped, or re-bounded without requiring one final scale?

Do not assume current Boundary semantics.

Test:
- one structure -> several substructures,
- several structures -> one higher-level materialization,
- overlapping composition where candidate supports it.

Observe what identity/continuity claims the model implicitly introduces.

### G. SUCCESSION / CHANGE OF MODELED OBJECT

Without assuming a final Instance ontology, test whether the candidate can represent predecessor/successor-like change.

Questions:
- Can historical states remain distinguishable?
- Can branch/fission be represented?
- Can merge/recomposition be represented?
- Does the model accidentally require one metaphysically privileged successor?

### H. AUTHORITY SEPARATION

If Authority-like behavior is represented, verify that:
- structural copying does not automatically copy authority,
- succession does not automatically transfer authority,
- capability/membership/identity do not silently collapse into authority.

Authority may ultimately belong above the low-level model; that possibility must also be tested rather than assumed away.

### I. HUMAN-FAMILIAR VS STRUCTURAL REPRESENTATION

Can the candidate support a human-friendly description that may say something like “the same Persona changed” while preserving a more exact structural history underneath?

The human-facing projection must not silently mutate or falsify the structural record.

This test does NOT require Persona implementation during MS0.

### J. IMPLEMENTATION PRESSURE

Estimate/experiment with computational consequences:
- replay cost,
- query complexity,
- recursion risk,
- combinatorial relation growth,
- materialization cost,
- partial-order/time complexity,
- incremental update feasibility,
- storage/history growth,
- model evolution/migration difficulty.

Philosophical explanatory power != practical implementation suitability.

## 4. Explicit anti-pattern attacks

Each candidate should be actively checked for:
- God Object emergence,
- everything-becomes-Relation,
- everything-becomes-Event,
- everything-becomes-State,
- everything-becomes-View,
- hidden OOP identity assumptions,
- hidden graph ontology assumptions,
- hidden global-clock assumptions,
- hidden binary truth assumptions,
- hidden immutable-schema assumptions,
- semantic decisions introduced only for coding convenience,
- over-generalization that makes the model unfalsifiable,
- excessive abstraction that makes `별` impossible to implement simply.

## 5. Minimal executable probes

MS0-02 MAY implement tiny executable probes when code is the cheapest way to expose ambiguity or failure.

Examples:
- reconstruct current state from history,
- preserve unresolved/conflicting claims,
- branch and merge a state/lineage-like object,
- change Scope/Perspective and compare outputs,
- alter interpretation rules without rewriting historical inputs,
- measure query/materialization complexity on toy data.

These probes are disposable research instruments.

They are NOT the first implementation artifact `별` unless the Owner later promotes one.

## 6. Required per-candidate output

For each surviving model candidate create a Pressure Test Card:

MODEL_CANDIDATE_ID
MODEL_FAMILY
TESTS_ATTEMPTED
TESTS_PASSED
TESTS_FAILED
AMBIGUITIES_EXPOSED
SEMANTIC_COLLAPSES
MODEL_ASSUMPTIONS_REQUIRED
COMPUTATIONAL_RISKS
REVERSIBILITY_OF_ASSUMPTIONS
WORLDVIEW_PRESERVATION_STRENGTHS
WORLDVIEW_DISTORTIONS
NEW_QUESTIONS
RECOMMENDED_STATUS

Recommended status vocabulary may include:
- SURVIVES
- SURVIVES_WITH_ASSUMPTIONS
- NEEDS_REDESIGN
- KEEP_AS_COUNTERMODEL
- DROP_FROM_CURRENT_ROUND
- REVIEW_REQUIRED

These statuses are research routing states, NOT truth claims or validation states.

## 7. Cross-candidate output

Required:

### 7.1 PRESSURE_TEST_MATRIX
Compare all candidates against identical attack families.

### 7.2 ASSUMPTION_COST_REGISTER
List assumptions each model requires, with:
- semantic cost,
- implementation cost,
- reversibility,
- affected current hypotheses,
- whether Owner review may be needed.

### 7.3 FAILURE_ATLAS
Preserve failures by category instead of hiding them in prose.

Examples:
- representation failure,
- semantic ambiguity,
- performance risk,
- ontology lock-in,
- irreversibility risk,
- human-familiar projection mismatch.

### 7.4 SURVIVOR_SET
Do NOT force a single winner.

Expected output may be:
- one leader + one strong countermodel,
- two complementary survivors,
- no survivor,
- hybridization opportunity.

## 8. Meeting Memory requirement

Create one MS0-02 Stage Meeting Memory.

It must include:
- expectations entering the stage,
- exact attack families used,
- surprising failures,
- surprising strengths,
- candidate ranking/weight changes,
- what assumptions were introduced,
- what was NOT resolved,
- what changed in the researchers' current understanding,
- what MS0-03 must inherit.

Do not expose or require private chain-of-thought.
Record reviewable decisions, observations, alternatives and evidence only.

## 9. Exit condition

MS0-02 is complete when:

1. every surviving MS0-01 candidate has faced the same core attack families,
2. failures and required assumptions are explicitly visible,
3. at least one of the following is true:
   - a leader emerges,
   - two or more complementary survivors remain,
   - no candidate survives and the failure reason is clear,
   - a justified hybrid candidate is proposed,
4. the next stage can proceed without hiding unresolved semantic decisions.

The purpose is NOT to finalize 한알.

The purpose is to reduce the model space through evidence-bearing pressure.

## 10. Suggested research budget

Suggested budget: approximately 60–120 minutes depending on number and depth of surviving candidates.

Exit condition has priority over elapsed time.

## 11. Handoff to MS0-03

MS0-03 should receive:
- Survivor Set,
- Pressure Test Matrix,
- Assumption Cost Register,
- Failure Atlas,
- Stage Meeting Memory,
- unresolved questions.

MS0-03 should then attempt CONVERGENCE / SYNTHESIS without erasing the strongest countermodel.

## 12. Current status

This is stage planning only.
No model candidate has been executed or selected by this note.

작성시각: 2026-08-20 23:44 KST
