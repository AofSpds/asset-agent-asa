# AAA-ASA-ME Owner Intuition — Model May Only Need to Implement Interaction + Interaction Nets Prior Art v0.1

DATE = 2026-08-21 KST
PROJECT = AAA
PRODUCT = ASSET AGENT ASA
WORKSTREAM = AAA-ASA-ME
STATE = NON_NORMATIVE_RESEARCH_MEMORY / OWNER_EXPLICIT_INTUITION / PRIOR_ART_REHARVEST / NOT_VALIDATED / NOT_OWNER_ACCEPTANCE

## 1. Owner-explicit intuition

OWNER_EXPLICIT:

- The model may only need to implement interaction.
- This is currently an intuition, not a finalized requirement or canonical architecture.
- Rich world/object semantics might therefore be unnecessary inside the interaction model itself, provided interaction can be represented/executed flexibly and other semantics can remain external, emergent, or materialized elsewhere.
- This intuition is consistent with the Owner's previously stated priorities of flexibility, diversity, relationality, low structural rigidity, explicit limits, and possible successor mutation.

## 2. Immediate research consequence

Do not assume the target must be a monolithic world model that internally represents all object meaning, identity, memory, authority, provenance, and interaction semantics.

Keep at least these competing forms OPEN:

A. rich Object/World Model + explicit Interaction Layer;
B. minimal substrate whose main responsibility is interaction implementation;
C. interaction-first model from which object/relation/event views are materialized;
D. ecology of specialized models rather than one universal model.

## 3. Prior-art signal: Interaction Nets / Interaction Combinators

Yves Lafont's Interaction Nets (POPL 1990) and Interaction Combinators (1997) are important prior-art seeds because they treat computation itself as local interaction among agents/nodes.

Key structural ideas:

- computation is performed by local interaction/rewrite rules;
- only agents that meet through designated principal ports interact;
- interaction rewrites the local graph/net;
- many interactions can proceed independently and in parallel;
- Interaction Combinators demonstrate universality with a deliberately tiny set of symbols and interaction rules;
- the model does not require rich domain semantics inside each node; semantics can be encoded in network structure and interaction rules.

This is relevant to the Owner intuition that a model may only need to implement interaction, rather than carrying all world semantics internally.

## 4. Related prior-art signal: Interactive Computation / Interaction Machines

Peter Wegner and Dina Goldin's Interactive Computation program treats ongoing interaction with an open environment as a first-class computational phenomenon rather than a closed input->algorithm->output function.

Important implications:

- complete future behavior of an open interactive system need not be specifiable in advance;
- partial/interface constraints can be more appropriate than total closed specifications;
- behavior is characterized through ongoing observable interaction;
- persistence between interactions is itself part of the computational model;
- interaction-oriented models are explicitly intended for objects, agents, distributed systems, coordination, collaboration, and open systems.

This is especially compatible with explicit capability boundaries and the Owner's rejection of universal support as a requirement.

## 5. Current comparative interpretation

Reo:
- strongest current structural-fit signal for explicit first-class coordination/interaction, composition, and reconfiguration.

Interaction Nets:
- more minimal and radical: computation can be reduced to local interaction + structural rewrite.
- potentially closer to `interaction implementation only`, but far poorer in explicit external meaning/protocol semantics.

Interactive Computation / Interaction Machines:
- more abstract but strongly aligned with open-endedness, incomplete pre-specification, persistence, and capability-by-interface/observable behavior.

These are different seeds and must not be silently synthesized.

## 6. Open questions

Still OPEN:

- Is interaction the only primitive the target model truly needs?
- Are Object/Relation/Event merely views/materializations over interaction history?
- Is Protocol itself an interaction rule, a grammar over interaction rules, a coordination structure, or a separate model?
- How much semantic meaning must be inside the interaction substrate versus externalized to higher layers?
- Can minimal interaction primitives preserve provenance, plurality, uncertainty, identity/history, and Persona-specific meaning without recreating a rigid ontology?
- When does adding semantics destroy the desired low-rigidity property?

## 7. Research use

Tag Interaction Nets / Interaction Combinators as:
`HIGH_RELEVANCE_MINIMAL_INTERACTION_PRIOR_ART / NOT_SELECTED / NOT_CANONICAL`.

Tag Interactive Computation / Interaction Machines as:
`HIGH_RELEVANCE_OPEN_INTERACTION_PRIOR_ART / NOT_SELECTED / NOT_CANONICAL`.

Do not promote either to a canonical AAA World Model without independent comparison and microprobes.

현재 상태: Owner가 `모델은 상호작용의 구현만 가능하면 충분할 수도 있다`는 새 직관을 명시했다.
핵심 판단: 이 직관은 Reo보다 더 최소주의적인 Interaction Nets 및 open-ended Interactive Computation 계열과 직접 연결된다.
진행 작업: monolithic rich world model 가정을 풀고 minimal interaction substrate / interaction-first / ecology 형태를 경쟁가설로 유지한다.
다음 단계: Interaction Nets의 local rewrite/minimal primitive 구조와 Interaction Machines의 open-system/partial-specification 구조를 Reo와 비교한다.
사용자 행동: 이 직관은 아직 확정하지 말고 강한 research hypothesis로 유지한다. 작성시각: 2026-08-21 20:28 KST
