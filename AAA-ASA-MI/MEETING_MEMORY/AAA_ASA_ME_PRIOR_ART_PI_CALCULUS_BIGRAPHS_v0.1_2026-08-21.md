# AAA-ASA-ME Prior-Art Deep Dive — π-Calculus and Bigraphical Reactive Systems v0.1

DATE = 2026-08-21 KST
PROJECT = AAA
PRODUCT = ASSET AGENT ASA
WORKSTREAM = AAA-ASA-ME
STATE = NON_NORMATIVE_RESEARCH / PRIOR_ART_REHARVEST / NOT_VALIDATED / NOT_OWNER_ACCEPTANCE

## 1. Research target

Investigate prior art where interaction is not merely message exchange but can change the structure of relations, connectivity, locality, or the represented system itself.

This follows the Owner worldview clarification that relationality/flexibility is not only a software-design preference but a hypothesis about how reality itself operates: diverse interactions arise because structures and relations are not fully rigid or pre-fixed.

## 2. π-calculus

Robin Milner, Joachim Parrow, and David Walker introduced the π-calculus as a calculus of communicating systems with changing structure.

Key property:
- communicating agents may be arbitrarily linked;
- a communication can carry a name/link that changes who can subsequently communicate with whom;
- therefore interaction can reconfigure relational topology.

Research mapping:
`INTERACTION -> LINKAGE CHANGE -> FUTURE INTERACTION SPACE CHANGE`

This is structurally relevant to the current AAA hypothesis because relations are not merely passive metadata around fixed objects. Interaction itself can modify the network of possible future relations.

Important limitation:
- π-calculus provides an intentionally sparse formal process semantics;
- it does not by itself provide rich world/object meaning, identity, history, perspective, normativity, or protocol semantics;
- therefore it is a strong structural seed, not a complete world model.

## 3. Bigraphical Reactive Systems

Milner's later Bigraphical Reactive Systems (BRS) generalize mobile interaction around two independent structural dimensions:

1. `PLACE GRAPH` — locality / nesting / containment;
2. `LINK GRAPH` — connectivity / interaction links.

A bigraph can be equipped with reaction rules that allow the represented system to reconfigure itself.

Research mapping:
`STATE = LOCALITY STRUCTURE + CONNECTIVITY STRUCTURE`
`REACTION / INTERACTION -> RECONFIGURED STATE`

This is potentially more relevant than π-calculus for AAA because it separates two forms of relational structure while still allowing dynamic reconfiguration.

BRS can recover or uniformly represent behaviors corresponding to π-calculus, Petri nets, and mobile ambients, making it a meta-level structural formalism rather than one narrow protocol language.

## 4. Current fit assessment

### Strong fit

- interaction is first-class;
- relation/connectivity can change through interaction;
- future interaction possibilities depend on past interactions;
- structure can reconfigure rather than merely update fixed attributes;
- mobility/topology change is native, not an afterthought;
- in bigraphs, locality and connectivity are modeled separately rather than collapsed.

### Weak fit / gaps

- no rich semantics for Persona identity, memory, history, perspective, authority, meaning, uncertainty, or evidence by default;
- no direct concept of Protocol as a first-class semantic model;
- reaction rules may become a hidden rigid ontology if treated as exhaustive;
- model-semantic mutation versus runtime structural transition is not the same distinction as AAA's current successor-mutation control.

## 5. Relation to Reo and Commitment prior art

Commitment-oriented protocols:
- strongest on semantic meaning of social relations and event-driven relation lifecycle.

Reo:
- strongest on explicit, composable, reconfigurable interaction/coordination structure separated from component internals.

π-calculus:
- strongest on interaction changing connectivity/topology itself.

Bigraphs:
- strongest on representing dynamic interaction over BOTH connectivity and locality/nesting, with reaction-driven reconfiguration.

No conclusion is authorized that one should replace or subsume the others.

## 6. Current candidate hypotheses

H1 — `SEMANTIC_RELATION + EVENT_LIFECYCLE`
Seed: commitment protocols.

H2 — `FIRST_CLASS_COMPOSABLE_INTERACTION`
Seed: Reo.

H3 — `INTERACTION_CHANGES_RELATIONAL_TOPOLOGY`
Seed: π-calculus.

H4 — `LOCALITY + CONNECTIVITY + REACTION RECONFIGURATION`
Seed: Bigraphical Reactive Systems.

H5 — successor model may combine some of these properties, but synthesis must be treated as a new hypothesis rather than an assumed merge.

## 7. High-value question for AAA-MI

Can a candidate world model preserve rich Object/Persona semantics while also allowing:

- relation topology to change through interaction;
- locality/context structure to change;
- future available interactions to depend on prior interactions;
- heterogeneous interaction semantics;
- explicit capability boundaries;
- controlled successor mutation when the current semantic substrate is insufficient?

## 8. Research status

Current assessment:
`STRONG_STRUCTURAL_PRIOR_ART_SEED`

Not yet:
- canonical architecture;
- Owner Acceptance;
- validated scientific claim;
- evidence that π-calculus or bigraphs alone satisfy the AAA world-model requirement.

현재 상태: π-calculus와 Bigraphical Reactive Systems를 interaction-driven structural reconfiguration 선행연구로 검토했다.
핵심 판단: π-calculus는 interaction이 connectivity를 바꾸고, Bigraphs는 locality+connectivity 구조가 reaction으로 재구성되는 것을 native하게 표현한다.
진행 작업: Commitment/Reo/π-calculus/Bigraphs를 서로 다른 독립 seed로 분리해 보존했다.
다음 단계: rich Persona/Object semantics와 interaction-driven topology/locality reconfiguration을 함께 갖는 successor 후보 또는 인접 연구를 추가 탐색한다.
사용자 행동: Reo를 강력 후보로 유지하되 π-calculus/Bigraphs는 relation topology mutation 관점의 강한 대안 seed로 비교하면 된다. 작성시각: 2026-08-21 20:21 KST
