# AAA-ASA-ME Prior Art Deep Dive — Reo / Coordination Model v0.1

DATE = 2026-08-21 KST
PROJECT = AAA
PRODUCT = ASSET AGENT ASA
WORKSTREAM = AAA-ASA-ME
STATE = NON_NORMATIVE_RESEARCH / EXTERNAL_PRIOR_ART / NOT_VALIDATED / NOT_OWNER_ACCEPTANCE

## 1. Research target

Second prior-art lineage after commitment-based interaction protocols:

`Reo / exogenous coordination / interaction-first connector semantics`

Owner preference signal from previous step:
- Commitment-based interaction protocol lineage currently has the strongest positive subjective response among reviewed external precedents.
- This is preference evidence, NOT canonical model selection.
- `PROTOCOL == RELATION/EVENT` remains OPEN.

## 2. Core Reo idea

Farhad Arbab's Reo is a channel-based exogenous coordination model in which autonomous components are treated largely as black boxes and their interactions are coordinated by first-class connectors built compositionally from primitive channels.

High-level interpretation:

`COMPONENTS / OBJECTS`
+
`EXTERNAL CONNECTOR / COORDINATION STRUCTURE`
→
`COMPOSITE INTERACTION BEHAVIOR`

In Reo, the interaction/connector layer is deliberately separated from component internals.

Arbab later characterized Reo as a constructive model that treats interaction as a first-class concept, even the sole first-class concept in that modeling perspective.

## 3. Connector semantics

A Reo connector is not merely a wire. It imposes a coordination pattern involving combinations of:
- data flow;
- synchronization;
- mutual exclusion;
- state;
- context-dependent behavior.

Complex connectors are composed from simpler channels and nodes.

Operational semantics can be expressed using Constraint Automata, supporting equivalence/refinement/containment checks and formal verification of coordination mechanisms.

## 4. Flexibility / composition

Reo's flexibility comes from composition of reusable interaction primitives rather than from allowing arbitrary unconstrained behavior.

Important prior-art directions include:
- user-defined channel types;
- compositional connector construction;
- multiple communication semantics;
- compatibility analysis between choreography and connectors;
- declarative specification and executable compilation.

Later Cho-Reo-graphies work explicitly allows different communication semantics, determined by user-defined connectors, to be freely mixed subject to compatibility analysis.

## 5. Dynamic reconfiguration

Reo research includes dynamic reconfiguration of connectors.

Connectors can be structurally reconfigured at runtime, including during pending I/O interactions.

Graph-transformation / high-level replacement systems have been used to formalize connector reconfiguration.

Later work distinguishes structural and behavioral perspectives and studies behavior-preserving reconfiguration.

This is relevant to AAA-MI's MUTATE direction, but with an important boundary:
- Reo primarily mutates/reconfigures coordination structure.
- It does NOT automatically imply mutation of a general world-model ontology or semantic substrate.

## 6. Relation to Owner requirement

Strong matches:

1. `INTERACTION FIRST-CLASS`
   - Interaction is modeled explicitly rather than hidden inside object implementation.

2. `OBJECT INTERNALS != COORDINATION SEMANTICS`
   - A component may remain autonomous while an external interaction structure coordinates it.

3. `COMPOSITION`
   - Complex protocols/interaction semantics can emerge from composition of smaller primitives.

4. `HETEROGENEOUS INTERACTION SEMANTICS`
   - User-defined channels/connectors and mixed communication semantics provide a strong precedent for supporting diverse protocols.

5. `DYNAMIC RECONFIGURATION`
   - Coordination structure can change at runtime and can be analyzed formally.

6. `EXPLICIT SEMANTICS / VERIFIABILITY`
   - Constraint Automata provide operational semantics and formal verification surfaces.

## 7. Major mismatches / limitations

Reo is NOT a general world model.

Key limitations for current AAA-MI goals:

- Components are largely black-boxed; Reo intentionally focuses on connectors rather than the intrinsic semantics/identity/history of objects.
- Relation semantics are primarily coordination/dataflow relations, not arbitrary social, causal, semantic, epistemic, identity, or historical relations.
- Protocol meaning is largely external connector behavior; it does not natively model rich normative meaning comparable to commitment-based protocols.
- Dynamic reconfiguration usually changes connector topology/behavior inside the coordination formalism, not the semantic ontology of the world model itself.
- Exogenous coordination may become too external/controlling if AAA wants protocols to arise from, participate in, or co-constitute the same world substrate.

## 8. Comparison with Commitment-based interaction protocols

### Commitment lineage

Focus:
`SEMANTIC RELATION STATE + EVENTS THAT CHANGE IT`

Strengths:
- rich public/social meaning;
- relation lifecycle;
- event-driven state change;
- autonomy without fixed action sequences;
- local projection / observability;
- explicit normative interpretation.

Weakness:
- commitment ontology is narrow and social/normative;
- weaker as a general coordination substrate.

### Reo lineage

Focus:
`INTERACTION STRUCTURE / CONNECTOR SEMANTICS`

Strengths:
- interaction itself becomes first-class;
- strong compositionality;
- heterogeneous coordination semantics;
- formal executability and verification;
- dynamic connector reconfiguration.

Weakness:
- meaning of objects/relations is thin;
- can become mechanically external to the world/object model;
- less natural for rich Persona/worldview semantics.

## 9. Current research interpretation

A high-value successor hypothesis is NOT to choose Commitment OR Reo immediately.

Potential design space:

A. `SEMANTIC RELATION LAYER` inspired by commitment-style explicit relation state
+
`INTERACTION / COORDINATION FABRIC` inspired by Reo-like first-class connectors

B. A deeper unified successor in which both semantic relation-state and coordination topology are materializations of a common Relation/Event/Process substrate.

C. Keep them independent as competing models if unification creates unnecessary complexity.

All remain OPEN.

## 10. Why Commitment may currently feel closer — MODEL_INFERRED ONLY

Possible explanation, not Owner-confirmed:
- Commitment approaches attach explicit meaning to relations and events, while Reo is deliberately more structural/mechanical.
- AAA-MI seeks Persona/worldview semantics, not only coordination mechanics.
- Therefore the first lineage may feel closer because interaction has semantic consequences for entities/relations rather than merely controlling dataflow.

This inference requires Owner confirmation before promotion.

## 11. Reusable design lessons

Candidates should be tested for:
- interaction as first-class structure;
- protocol composition from reusable primitives;
- new user-defined interaction types;
- compatibility checks rather than forced support;
- formal operational semantics;
- dynamic reconfiguration with invariant preservation;
- explicit separation between local component semantics and interaction semantics where useful;
- ability to reject unsupported interaction without semantic distortion.

## 12. External source anchors

- Arbab, 2004, `Reo: A channel-based coordination model for component composition`, Mathematical Structures in Computer Science.
- Arbab, 2006, `Coordination for Component Composition`, Electronic Notes in Theoretical Computer Science.
- Baier, Sirjani, Arbab, Rutten, 2006, `Modeling component connectors in Reo by constraint automata`, Science of Computer Programming.
- Krause, Maraikar, Lazovik, Arbab, 2011, `Modeling dynamic reconfigurations in Reo using high-level replacement systems`.
- Dokter & Arbab, 2018, `Treo: Textual Syntax for Reo Connectors`.
- Arbab et al., 2018, `Connectors meet Choreographies`.

현재 상태: 두 번째 외부 선행계열인 Reo/exogenous coordination을 interaction-first 관점에서 검토했다.
핵심 판단: Reo는 `interaction을 first-class로 모델링 + compositional connector semantics + dynamic reconfiguration`에서 매우 강하지만 general world semantics 자체는 약하다.
진행 작업: Commitment 계열의 semantic relation strength와 Reo 계열의 compositional interaction strength를 분리해 successor design space로 보존한다.
다음 단계: Reo를 현재 요구에 직접 채택하지 않고 interaction-fabric seed로 유지한 뒤 다음 prior-art lineage와 비교한다.
사용자 행동: Commitment 계열과 Reo의 차이 중 어떤 쪽이 더 자연스러운지 관찰하되 지금은 canonical 선택하지 않는다. 작성시각: 2026-08-21 20:10 KST
