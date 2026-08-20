# MS0-01 — Divergence / Model-Family Exploration

TIME = 2026-08-20 23:41 KST
STATE = WORKING_RESEARCH_MEMORY / MS0_DESIGN / NON_NORMATIVE

## 0. Context

Working world-model name candidate: `한알`

Working milestone:
- `MS0 — ONTOGENESIS`
- narrative codename: `FIAT LUX / 빛이 있으라`

Working first implementation-artifact name: `별`

`별` currently means only `FIRST IMPLEMENTATION ARTIFACT`.
It MUST NOT be assumed to mean Instance, Event, Relation, Boundary, or any other ontology primitive.

## 1. Stage position

MS0-00 restores the research state and identifies what is Owner-explicit, hypothesis, counter-hypothesis, ancestor concept, OPEN, or retired/lower-weight.

MS0-01 begins deliberate divergence.

The purpose is NOT to choose the model.
The purpose is to widen the serious computational design space before convergence pressure begins.

## 2. Stage objective

Explore multiple serious computational/modeling families capable of expressing the currently harvested worldview and research questions without assuming that the current candidate vocabulary is the final ontology.

The stage should identify:
- what each model family represents naturally,
- what it represents only awkwardly,
- what existing ASA-MI concepts it would collapse, split, reinterpret, or discard,
- what ontology it would silently impose,
- what assumptions would be expensive to reverse,
- which unresolved questions each model family makes newly visible.

## 3. Required research posture

Do NOT start by implementing the current vocabulary as classes.

Current terms such as:
- Relation
- Event
- Instance
- Process
- Memory
- Standpoint
- Boundary
- Materialization
- Succession
- Scope / Scale

are CANDIDATE RESEARCH VOCABULARY only.

INVENTORY INCLUSION != MODEL INCLUSION.

MS0-01 may propose that a term:
- remains first-class,
- becomes derived,
- becomes a view/projection,
- is split into multiple concepts,
- is merged with another concept,
- is implementation-only,
- is unnecessary in one model family,
- or should remain OPEN.

Any such proposal remains a CODEX_MODELING_PROPOSAL unless later reviewed.

## 4. Model families to investigate

The stage must investigate several serious alternatives rather than one favored architecture.

Potential families include, but are not limited to:
- temporal relational/state models,
- event-sourced + materialized-view models,
- typed graph / hypergraph models,
- relational algebra / Datalog-style fact and derivation models,
- process / actor / interaction models,
- state-transition / labeled-transition systems,
- process algebra / Petri-net-like approaches when materially useful,
- functional/reactive models,
- hybrid models.

These are prompts for exploration, not mandatory finalists.

Do not introduce exotic formalism merely for sophistication.
Prefer established prior art when it is sufficient.

## 5. Minimum candidate count

Produce at least FOUR non-strawman model families.

Each must be presented as if it could plausibly win.

Do not create intentionally weak alternatives to justify a preferred design.

A fifth or sixth candidate may be added when it exposes a materially distinct semantic tradeoff.

## 6. Comparison axes

At minimum compare candidates on:
- ability to represent change without rewriting history,
- time / history treatment,
- uncertainty / unknown / dispute handling,
- compositionality,
- multi-scale representation,
- perspective/context dependence,
- support for changing current meaning,
- deterministic replay potential,
- ability to distinguish source facts from derived interpretation,
- ability to support future Persona modeling without making Persona the root ontology,
- implementation complexity,
- inspectability / explainability,
- accidental ontology lock-in risk,
- reversibility of design choices,
- suitability for a small first implementation artifact (`별`).

Do NOT assume that Boundary, Instance, Event, or Relation must appear as comparison axes in every model in the same form.
Instead record how each model family interprets or replaces the research problems those terms were originally trying to express.

## 7. Required outputs

### 7.1 MODEL_FAMILY_CARDS

For each candidate:
- candidate name
- known prior art / intellectual ancestry
- core representational idea
- what becomes primitive
- what becomes derived
- treatment of time/change
- treatment of uncertainty
- strongest fit with current research
- strongest semantic distortion
- implementation burden
- reversible assumptions
- hard-to-reverse assumptions
- key attack

### 7.2 CROSS_MODEL_COMPARISON_MATRIX

One matrix comparing the candidates against common research questions.

SCORE != TRUTH.
Qualitative explanation is primary.

### 7.3 SEMANTIC_COLLAPSE_MAP

Record where a model family would collapse distinctions currently kept separate.

Examples of collapse questions:
- Event vs Relation
- current state vs materialized view
- history vs memory
- existence vs accessibility
- entity vs process
- model state vs epistemic state

The examples are not mandatory distinctions.
They are research questions.

### 7.4 NEW_QUESTIONS_REGISTER

Every candidate should generate new questions.
Preserve them rather than forcing answers.

### 7.5 SURVIVING_CANDIDATES

At end of MS0-01, identify a small set of candidates worth deeper pressure testing.

This is NOT final selection.

## 8. Stage meeting memory

Create one stage meeting-memory artifact recording:
- inputs actually read,
- candidates considered,
- discarded alternatives and why,
- surprising findings,
- concepts that proved redundant in some models,
- concepts that became more important in some models,
- assumptions accidentally introduced and then removed,
- disagreements inside the analysis,
- unresolved questions,
- what changed in current understanding,
- handoff requirements for MS0-02.

Do not record private chain-of-thought.
Record reproducible research decisions, alternatives, evidence, observations, and reasons.

## 9. Prohibitions

MS0-01 MUST NOT:
- choose the final Hanal model,
- implement Persona INIT,
- define `별` as a specific ontology category,
- infer formal semantics from the names `한알`, `별`, `ONTOGENESIS`, or `FIAT LUX`,
- promote implementation convenience into reality claims,
- rewrite historical Meeting Memory,
- declare a validation PASS,
- turn CODEX proposal into Owner decision.

## 10. Exit condition

MS0-01 is complete when:

1. at least four credible competing model families have been explored,
2. their semantic tradeoffs are explicit,
3. at least two or three candidates remain credible for deeper pressure testing,
4. no surviving candidate depends on hidden conversion of OPEN questions into facts,
5. the next stage can test concrete semantic pressure points rather than debating vocabulary abstractly.

A valid result may conclude that none of the initially considered families is sufficient and that a hybrid or new combination must be investigated.

## 11. Approximate research budget

Suggested budget: 60–90 minutes equivalent effort.

Time is secondary to the Exit Condition.
Do not spend time merely to fill the budget.

## 12. Owner review intent

Owner expects to review the accumulated stage meeting records during the next working period.
The records should therefore make the path of the research inspectable without requiring the Owner to reconstruct the entire conversation manually.
