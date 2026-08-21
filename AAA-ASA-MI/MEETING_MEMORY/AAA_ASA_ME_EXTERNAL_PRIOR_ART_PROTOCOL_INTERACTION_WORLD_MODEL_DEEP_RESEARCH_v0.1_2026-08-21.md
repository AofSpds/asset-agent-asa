# AAA-ASA-ME External Prior-Art Deep Research — Protocol / Interaction / World Model v0.1

DATE = 2026-08-21 KST
PROJECT = AAA
PRODUCT = ASSET AGENT ASA
WORKSTREAM = AAA-ASA-ME
STATE = NON_NORMATIVE_EXTERNAL_RESEARCH / NOT_VALIDATED / NOT_OWNER_ACCEPTANCE

## Research question

Has there been prior research materially similar to the Owner's emerging requirement:

- diversity and flexibility first;
- world/object representation centered on Relation/Event/Interaction rather than fixed identity;
- Protocol as a model of interaction / Relation / Event, not merely a static ruleset;
- a model that can support heterogeneous and unforeseen protocols when possible;
- explicit capability boundaries when a protocol cannot be supported;
- optional runtime adaptation and, when structurally necessary, successor-model mutation;
- no requirement that one universal model support every possible interaction.

## Preliminary conclusion

No single established research program located in this search appears to combine the complete requirement as one canonical "world model" architecture.

However, several mature lineages each cover a major part of the requirement. The closest synthesis candidates are:

1. interaction-oriented / commitment-based multiagent protocols;
2. coordination models such as Reo;
3. process calculi, especially pi-calculus, and Actor/open-system models;
4. interactive computation / open systems;
5. reflective systems and metaobject protocols / models@runtime;
6. Dynamic Epistemic Logic action/event models;
7. enactivism / participatory sense-making / structural coupling;
8. object- and relation-centric world models / graph interaction networks;
9. object-centric event/process models;
10. runtime variability / self-adaptive systems.

The current Owner requirement looks less like a rediscovery of one old theory and more like a cross-domain synthesis that joins an interaction-centric substrate, declarative protocol semantics, explicit limits, and controlled model evolution.

## Strongest precedents

### A. Flexible / commitment-based multiagent protocols

A particularly close precedent is the commitment-protocol research line associated with Munindar P. Singh and collaborators.

Traditional message-sequence protocols were criticized as too rigid for autonomous agents. Commitment protocols model interactions in terms of social commitments (relations between parties) and actions/events that create, discharge, modify, or otherwise affect those commitments. In this line, protocol states need not be enumerated a priori and transitions can be computed at runtime, enabling flexible execution.

Important evidence:
- Venkatraman (1999), Specifying and Verifying Compliance in Commitment Protocols.
- Mallya (2005), Modeling and Enacting Business Processes via Commitment Protocols Among Agents.
- Yolum/Singh and subsequent work on flexible enactment and commitment concession.
- GoCo (2018), expressive commitment protocols with autonomy and uncertainty.
- Langshaw (IJCAI 2024), declarative protocols combining flexibility with an information model and explicit action conflicts.
- Orpheus (AAAI 2025), a programming model for agents organized around communication protocols.
- Interaction-Oriented Programming tooling (2025).

Relevance:
VERY HIGH for `Protocol ~= interaction semantics over relations/events`.

Gap:
These works do not generally provide a broad ontological/world model whose own representation can evolve across arbitrary semantic protocol families.

### B. FIPA agent interaction protocols

FIPA's 1997 Agent Communication Language is notable for several ideas close to explicit capability boundaries:

- agents need not implement every standard protocol;
- an agent should return `not-understood` when it does not recognize or cannot process a message;
- agents may use nonstandard communicative acts/protocols;
- protocols are not exhaustive;
- multiple conversations under different protocols can occur concurrently;
- the FIPA text explicitly warns that fixed protocols can be restrictive and that anticipating every possible response is unrealistic.

Relevance:
HIGH for `not every model must support every protocol`, explicit unsupported behavior, and plural protocol participation.

Gap:
FIPA still treats protocols primarily as communication patterns layered over autonomous agents, not as a general world-model interaction ontology.

### C. Reo / coordination models

Reo (Arbab, 2004 onward) is an exogenous coordination model in which connectors coordinate interactions among otherwise separate components. Connectors are compositionally built from channels and can have context-dependent behavior. The channel set can be open-ended.

Relevance:
VERY HIGH for separating `what components are` from `how interactions among them are coordinated`, while giving interaction a first-class formal semantics.

Gap:
The internal semantic/world representation of each component is intentionally external; Reo is a coordination formalism, not a full world model.

### D. pi-calculus and mobile process calculi

Milner, Parrow, and Walker's pi-calculus models communicating systems whose linkage structure can change through communication itself. Communication can therefore alter the relation topology among processes.

Relevance:
VERY HIGH for `interaction/event can mutate relations/topology` and for process/event-first candidate architectures.

Gap:
It is intentionally austere about rich semantic content, perspective, ontology, uncertainty, and model self-evolution.

### E. Interactive computation / open systems

Wegner and Goldin's interactive-computation program argues that open interactive systems cannot be adequately understood as closed input-output algorithms whose complete future behavior is prespecified. Interface constraints provide partial descriptions of systems whose full interactive behavior is inherently not known in advance.

Relevance:
VERY HIGH for the Owner's requirement that universal support is not expected, that partial capability descriptions are legitimate, and that interaction with an open environment is primary.

Gap:
This is a computation paradigm, not by itself a detailed Relation/Event/Protocol world-model implementation.

### F. Metaobject protocols / reflection / models@runtime

Kiczales, des Rivieres, and Bobrow's Metaobject Protocol work makes aspects of a language/object system explicitly inspectable and customizable at a meta-level. Later open-interpreter and self-adaptive systems research allows runtime structure/behavior/state to be exposed and modified. Models@runtime and dynamic software product lines similarly treat variability and runtime reconfiguration as first-class.

Relevance:
VERY HIGH for controlled adaptation/mutation and for making the rules governing object behavior themselves modeled/manipulable.

Gap:
Most of this work concerns software architecture/language semantics rather than a general cognitive or ontological world model. Runtime reconfiguration is not equivalent to semantic successor-model mutation.

### G. Dynamic Epistemic Logic (DEL)

DEL models world/epistemic states and separate action/event models. A product-update operation applies an event/action model to a prior model to produce a new model. Event models can encode different agents' perspectives on the same action, and newer work extends model-changing capabilities.

Relevance:
HIGH for the architecture pattern `MODEL x EVENT_MODEL -> UPDATED_MODEL`, perspective-specific event semantics, and explicit model transformation.

Gap:
Standard DEL focuses mainly on knowledge/belief dynamics and is not a general interaction/world ontology.

### H. Enactivism / participatory sense-making

De Jaegher and Di Paolo (2007) argue that an interaction process can acquire a degree of autonomy and that meaning is generated and transformed in the interplay between interaction dynamics and participating individuals. Structural-coupling work emphasizes reciprocal co-determination of agent and environment over time.

Relevance:
VERY HIGH conceptually for `interaction itself can be a first-class process that changes participants and meaning` and for object/protocol non-separability.

Gap:
It is not yet an executable formal architecture at the level required by AAA; significant computational formalization is still required.

### I. Object-/relation-centric world models and graph interaction networks

Battaglia et al. (2016) Interaction Networks and subsequent graph-network work model objects and relations explicitly and predict dynamics through interaction. More recent object-centric world-model work (Cosmos 2024, Dyn-O 2025) targets compositional generalization and structured dynamics.

Relevance:
HIGH for Object/Relation substrate, compositionality, and unseen structural combinations.

Gap:
Protocols are not normally first-class semantic objects, and model mutation/capability boundaries are not the central research target.

### J. Object-centric event/process models

Object-Centric Process Mining and OCEL 2.0 model events as involving multiple objects and also represent object-object relationships and changing object attributes over time.

Relevance:
MEDIUM-HIGH for a concrete `Object + Event + Relation` data substrate and against the assumption that each event belongs to one single fixed case/object.

Gap:
It is primarily descriptive/process-mining infrastructure, not a general adaptive world model or protocol ecology.

## Current synthesis hypothesis

The closest external research ancestry is not one field but the intersection:

`OPEN / INTERACTIVE COMPUTATION`
+
`PROCESS CALCULUS / ACTOR / COORDINATION`
+
`DECLARATIVE FLEXIBLE MULTIAGENT PROTOCOLS`
+
`EVENT-MODEL-DRIVEN STATE TRANSFORMATION`
+
`REFLECTION / MODELS@RUNTIME`
+
`RELATIONAL / OBJECT-CENTRIC WORLD MODELS`
+
`ENACTIVE STRUCTURAL COUPLING`

This combination materially resembles the Owner's present design space, but no prior-art source in this search was found that already packages all of these as the same canonical world-model architecture.

## Important scientific caution

Do not claim novelty from this search alone.

A defensible current statement is:

`NO_SINGLE_EXACT_PRECEDENT_FOUND_IN_CURRENT_SEARCH`
/
`MULTIPLE_STRONG_PARTIAL_PRECEDENTS_FOUND`
/
`NOVELTY_NOT_ESTABLISHED`

A real novelty claim would require a systematic literature review with explicit databases, query strings, inclusion/exclusion criteria, citation chasing, and independent review.

## Suggested research directions for model regeneration

Do not use prior art as a single synthesis that forces convergence. Instead seed isolated candidate workers from different lineages:

- commitment/social-state protocols;
- Reo/coordination connectors;
- pi-calculus/process algebra;
- Actor/open-system interaction;
- DEL event-model update;
- metaobject/reflection/models@runtime;
- enactivism/structural coupling;
- graph/object-centric world models;
- object-centric event/process models;
- categorical/compositional open systems;
- wildcards.

Then evaluate whether a candidate can represent new interaction semantics without either silently changing its ontology or claiming universal expressiveness.

## External sources harvested

- Milner, Parrow, Walker, A Calculus of Mobile Processes I, Information and Computation 100(1), 1992.
- Wegner, Models and Paradigms of Interaction, Brown CS TR CS-95-21, 1995.
- Wegner & Goldin, Mathematical Models of Interactive Computing, Brown CS TR CS-99-13, 1999.
- Agha, Actors: A Model of Concurrent Computation in Distributed Systems, MIT Press, 1986.
- Kiczales, des Rivieres, Bobrow, The Art of the Metaobject Protocol, MIT Press, 1991.
- Arbab, Reo: a channel-based coordination model for component composition, MSCS, 2004.
- Mousavi, Sirjani, Arbab, Formal Semantics and Analysis of Component Connectors in Reo, 2006.
- FIPA Agent Communication Language / interaction protocol specifications, 1997 onward.
- Venkatraman, Specifying and Verifying Compliance in Commitment Protocols, 1999.
- Mallya, Modeling and Enacting Business Processes via Commitment Protocols Among Agents, 2005.
- Meneguzzi et al., GoCo: planning expressive commitment protocols, 2018.
- Singh, Christie, Chopra, Langshaw, IJCAI 2024.
- Baldoni et al., Orpheus, AAAI 2025.
- De Jaegher & Di Paolo, Participatory Sense-Making, 2007.
- Dynamic Epistemic Logic / Baltag-Moss-Solecki action-model product update tradition.
- Battaglia et al., Interaction Networks, NeurIPS 2016.
- Sanchez-Gonzalez et al., Graph Networks as Learnable Physics Engines, ICML 2018.
- Sehgal et al., Neurosymbolic Grounding for Compositional World Models, ICLR 2024.
- Wang et al., Dyn-O, NeurIPS 2025.
- van der Aalst / Berti, Object-Centric Process Mining and OCEL 2.0 lineage.
- Runtime-model / self-adaptive-system / dynamic software-product-line literature.

현재 상태: 외부 선행연구를 심층 탐색한 결과 현재 Owner 요구 전체와 동일한 단일 canonical world-model 계열은 확인하지 못했으나 강한 부분 선행계보를 다수 확인했다.
핵심 판단: 가장 가까운 축은 flexible commitment protocols, Reo coordination, pi-calculus/open interaction, DEL event-model update, reflection/runtime models, enactivism, relation/object-centric world models의 교차점이다.
진행 작업: 각 선행계보의 대응 요구와 한계를 분리 기록했으며 `NO_SINGLE_EXACT_PRECEDENT_FOUND / MULTIPLE_STRONG_PARTIAL_PRECEDENTS_FOUND / NOVELTY_NOT_ESTABLISHED`로 보수적으로 분류한다.
다음 단계: 모델 재생성 시 선행연구를 한 번에 합성하지 말고 서로 다른 계열로 isolated divergence seed한 뒤 unseen interaction/protocol stress로 비교한다.
사용자 행동: 외부 레거시 설명에서는 특히 commitment-protocol, Reo, pi-calculus, interactive-computation, DEL, MOP/enactivism을 우선 검토하면 된다. 작성시각: 2026-08-21 20:00 KST
