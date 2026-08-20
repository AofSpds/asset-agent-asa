# AAA-ASA-MI Meeting Memory

## Title
EVENT / PROCESS-FIRST Deep Brainstorm

## Date / Time
2026-08-20 17:39 KST

## Status
WORKING_RESEARCH_CONTEXT / BRAINSTORM / EVENT_PROCESS_RESEARCH / INIT_CURRENTIZATION_PREPARATION

## Purpose
Preserve the decision to deepen EVENT / PROCESS-first research as a serious competitor and possible co-constitutive partner to RELATIONAL CONSTITUTION.

This record is NOT a Requirement, Design Contract, Frozen Artifact, Final Ontology, Validation Receipt, Independent Validation PASS, or Final Truth.

---

## 1. Research Motivation

RELATIONAL CONSTITUTION has become increasingly powerful in the Owner's current worldview. That makes it especially important to strengthen an opposing or orthogonal hypothesis rather than allowing Relation to become an unfalsifiable universal explanation.

Primary research question:

> Is Relation constitutive, or is Relation itself a materialized/compressed result of underlying EVENT / PROCESS history?

Possible outcomes include:
- RELATION-FIRST survives strongly;
- EVENT/PROCESS-FIRST wins;
- HYBRID wins;
- RELATION-PROCESS CO-CONSTITUTION survives;
- both reduce to another deeper substrate or formalism.

---

## 2. Candidate — EVENT as Relational Configuration Change

A strong candidate is to define EVENT not merely as a log record, but as a bounded change in relational configuration.

Conceptual sketch only:

`EVENT ~= CHANGE(RELATIONAL_CONFIGURATION)`

or

`E : C_t -> C_t'`

where `C` is some bounded current configuration.

Important caution:
- this function/transition notation is only a modeling aid;
- events need not be deterministic;
- continuous processes may not admit a unique discrete event segmentation;
- `C_t` may itself be materialized and scope-relative.

---

## 3. Candidate — State as Projection over Event History

EVENT-FIRST can model current state as a projection/materialization over prior events:

`CURRENT_STATE_t = PROJECT(EVENT_HISTORY_<=t, CURRENT_RULES, SCOPE, ...)`

This resembles event sourcing but must not be equated with event sourcing as an implementation commitment.

Research question:

> Is a Relation merely one such projection over event history?

Potential form:

`RELATION_t = MATERIALIZE(RELEVANT_EVENTS_<=t, CONTEXT_t, HYPOTHESES_t, ...)`

Example intuition:
- many interactions occur between A and B;
- a current `FRIEND` relation is a compressed/materialized interpretation of that history;
- the relation then affects what later interactions mean or permit.

---

## 4. Strong Counter-Counterargument — Materialized Relation Can Become Operationally Causal

Even if Relation originates as a projection over event history, the materialized relation may affect later behavior.

Example:
- event history produces a contract relation;
- the contract relation constrains or enables later actions;
- later actions create new events;
- those events modify or terminate the relation.

Therefore:

`EVENTS -> RELATION -> POSSIBLE/INTERPRETED NEXT EVENTS -> RELATION'`

This motivates a strong candidate:

## RELATION-PROCESS CO-CONSTITUTION

> Events/processes can create, modify, activate, deactivate, or terminate relations; current relations can in turn constrain, enable, interpret, or weight subsequent events/processes.

Neither side must be assumed metaphysically primitive.

---

## 5. Event Identity Problem

EVENT-FIRST does not eliminate ontology problems. It moves them.

To record an event, the system must answer:
- what changed?
- between which participants?
- when did the event begin/end?
- at what scale?
- under whose scope/observation?
- what distinguishes one event from another?

Therefore event records may presuppose entity/relation references.

Adversarial attack:

> If an event requires already-defined participants and relations, can EVENT truly be more fundamental than Relation or Entity?

Possible escape:
- use minimal technical anchors/carriers/references;
- materialize higher semantic event identity later;
- allow event definition itself to be scope-relative.

---

## 6. Event Boundary / Segmentation Problem

Continuous reality does not automatically arrive as discrete events.

The same physical or social history may be segmented as:
- one long process;
- many micro-events;
- one macro-event;
- different overlapping events under different purposes/scales.

Strong candidate:

> There may be no unique canonical event decomposition.

This mirrors the already Owner-confirmed multi-scale materialization hypothesis for instances.

Possible implication:

`EVENT = MATERIALIZED TEMPORAL VIEW`

rather than an unquestionable primitive fact.

---

## 7. EVENT vs PROCESS Distinction

Do not casually collapse EVENT and PROCESS.

Working research distinction:
- `EVENT`: bounded occurrence/change/materialized transition.
- `PROCESS`: temporally extended pattern/generator/ongoing sequence that may produce or comprise events.

Possible relations:
- process generates events;
- events are observations/cuts through a process;
- process itself can be materialized from event history;
- both may be alternate representations at different scales.

No canonical choice yet.

---

## 8. Partial Order vs Global Timeline

EVENT-FIRST should not assume a single total ordering of all events.

In distributed systems and many real-world settings:
- events can be concurrent;
- exact global order may be unknown or meaningless;
- only causal/observational partial order may be justified.

Research candidates:
- predecessor/successor event relation;
- happens-before style relation;
- causal dependency relation;
- same-scope ordering;
- unresolved ordering.

Important:

`TEMPORAL ORDER != CAUSALITY`

and

`OBSERVED ORDER != TRUE GLOBAL ORDER`.

---

## 9. Event Claim vs Event Fact

Scientific/data safety requires separation between:
- a world event;
- an observation of an event;
- a claim that an event occurred;
- a model-inferred event;
- a recorded/logged event.

Do not collapse these.

Potential distinction:

`EVENT_CLAIM != OBSERVED_EVENT != MODEL_INFERRED_EVENT != VERIFIED_EVENT`

Vocabulary is not final.

This is especially important when historical evidence is partial or conflicting.

---

## 10. Event as Relation Activation / Deactivation

Given the recent Working Memory / Materialization Layer discussion, an EVENT may be what changes callability/materialization.

Examples:
- meeting event activates latent friendship/work relations;
- contract-signing event materializes a contractual relation;
- termination event deactivates it;
- scope-change event may cause a different relation bundle to enter Working Memory;
- merge/fission event creates new successor instances and relation configurations.

Candidate:

> EVENT may be the operational trigger that rematerializes a bounded relational view.

---

## 11. Event Cost Advantage

EVENT-FIRST has a practical attraction:

Instead of recomputing the full relational universe continuously, append bounded changes and update only affected projections/materializations.

Potential implementation benefit:
- append-only provenance;
- deterministic replay where inputs/rules are stable;
- incremental materialization;
- auditability;
- bounded dirty-set updates.

But this is not free.

Costs/risks:
- event explosion;
- event schema evolution;
- replay cost;
- hidden events / missing historical evidence;
- non-deterministic external dependencies;
- late-arriving events;
- corrections/retractions;
- event granularity instability;
- deriving current semantic relations can become expensive.

---

## 12. Strong Alternative Models for Codex Committee

The committee should compare at least:

1. RELATION-FIRST
   - current relational configuration is constitutive.

2. EVENT/PROCESS-FIRST
   - relations are projections/compressions over events/processes.

3. ENTITY-FIRST + EVENT SOURCING
   - stable technical entities receive append-only events; projections produce current state.

4. RELATION-PROCESS CO-CONSTITUTION
   - events create relations, relations condition subsequent events.

5. HYBRID BASE SUBSTRATE
   - minimal references/primitives/events/claims + materialized relations + materialized instances.

The committee must be allowed to introduce better alternatives.

---

## 13. High-Value ANCESTOR_CONCEPT Candidates

Candidates for later deep research, not authority:
- Process Philosophy / Whitehead-style process-oriented ontology;
- Event Sourcing;
- Discrete Event Systems;
- Event Calculus;
- Temporal Logic;
- Petri Nets;
- Process Algebra;
- Distributed systems partial ordering / happens-before;
- Dynamical Systems;
- State-space / transition systems;
- Structural Causal Models, with strict caution that event succession does not imply causality;
- Category-theoretic process/morphism perspectives;
- Buddhism's dependent origination as already-open relational/conditional ancestor, without identity claims.

---

## 14. Key Falsification / Adversarial Questions

- Can EVENT-FIRST define event identity without smuggling in stable entities/relations?
- Is relation compression lossy in ways that matter operationally?
- When does a materialized Relation become causally/operationally real enough that EVENT-FIRST alone is insufficient?
- Is there a unique event boundary? If not, how is replay defined?
- Can multiple scales materialize different valid events from the same substrate?
- Does process-continuity fit P0 better than discrete event identity, or does discrete event materialization fit succession better?
- How should late evidence rewrite or supersede historical event interpretation without mutating frozen history?
- Can event-first reduce relation explosion, or merely replace it with event explosion?
- Which model is cheapest for INIT while preserving future extensibility?

---

## 15. Strong Current Candidate

A particularly promising research candidate is:

> EVENT is not merely an immutable log row and Relation is not merely a static edge. EVENT/PROCESS and RELATION may form a feedback loop: processes/events alter relational configuration; current relational configuration determines how subsequent events are interpreted, enabled, constrained, and materialized.

This is `RELATION-PROCESS CO-CONSTITUTION`, not yet Owner-adopted and not an implementation commitment.

---

## 16. Five-Line Summary

현재 상태: RELATIONAL CONSTITUTION의 강한 대항·보완축으로 EVENT/PROCESS-FIRST를 독립 심층 연구축으로 열었다.
핵심 판단: EVENT를 단순 로그가 아니라 bounded configuration change로, RELATION을 event history의 materialized projection일 수 있는 대상으로 보면 Relation-first와 Event-first의 정면 비교가 가능해진다.
진행 작업: event identity/segmentation/scale/partial-order/claim-vs-fact/activation/replay 비용 문제와 `RELATION-PROCESS CO-CONSTITUTION` 후보를 정리했다.
다음 단계: Owner 회상 반응을 받은 뒤 EVENT의 본질 후보를 더 좁히고 Codex 대항군에 Relation-first vs Event/Process-first vs Hybrid 비교를 설계한다.
사용자 행동: EVENT에 대해 이미 생각했던 직관, 새로 강하게 끌리는 후보, 또는 위화감 있는 부분을 자유롭게 표시하면 된다. 작성시각: 2026-08-20 17:39 KST
