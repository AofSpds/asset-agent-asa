# AAA-ASA-ME Prior-Art Deep Dive 01 — Commitment-Based / Interaction-Oriented Multiagent Protocols v0.1

DATE = 2026-08-21 KST
PROJECT = AAA
PRODUCT = ASSET AGENT ASA
WORKSTREAM = AAA-ASA-ME
STATE = NON_NORMATIVE_RESEARCH / EXTERNAL_PRIOR_ART / NOT_VALIDATED / NOVELTY_NOT_ESTABLISHED

## Scope

This note studies commitment-based multiagent interaction protocols as external prior art relevant to the Owner's current requirements. It does NOT assume that Protocol == Relation or Protocol == Event.

## Core distinction

Commitment-protocol research generally distinguishes:

- autonomous participants/agents;
- public/social state represented by directed commitments among participants;
- events/actions that create, discharge, cancel, release, assign, delegate, detach, expire, or violate commitments;
- a protocol that defines which social states are relevant and how actions/events affect those states.

Thus a useful schematic is:

`PARTICIPANTS + WORLD/EVENT FACTS -> SOCIAL COMMITMENT STATE -> EVENT/ACTION PROGRESSION`

with the protocol giving the interaction semantics over the commitment state.

This is importantly different from `PROTOCOL == RELATION/EVENT`. Commitments are relation-like social/normative objects; events/actions progress them; the protocol is the specification of the relevant social states and their progression.

## Canonical commitment form

A common form is:

`C(debtor, creditor, antecedent, consequent)`

meaning that a debtor is committed toward a creditor such that if the antecedent holds, the consequent is to hold.

The commitment state is public/social rather than an attempt to inspect private beliefs or intentions.

## Why this research was developed

Traditional protocol approaches often prescribe action/message sequences. Yolum & Singh argued that sequence-oriented protocol specification unnecessarily limits autonomous agents. Commitment-based protocol approaches instead specify the social meaning/effects of actions so that agents retain freedom over how to proceed while remaining accountable for commitments.

This produces a key separation:

`AUTONOMY OF ACTION != ABSENCE OF SOCIAL CONSTRAINT`

Agents can choose their actions locally; compliance is judged against the resulting commitment state.

## Event relation

Events are first-class in the operational semantics. Relevant events can:

- create commitments;
- make antecedents true and detach conditional commitments;
- satisfy consequents and discharge commitments;
- make commitments expire or become violated;
- alter creditor/debtor relationships via assignment/delegation operations;
- change what each participant can verify depending on observability and social context.

Yolum & Singh formalized commitment evolution using Event Calculus. Later work also represents commitment contents directly over event expressions and studies protocol enactments as event sequences.

## Important flexibility property

The protocol does not have to prescribe one exact message/action trace. Instead, the relevant social state and action effects constrain acceptable interaction. This gives agents more execution freedom than a fixed sequence protocol.

However, this flexibility is bounded by the commitment ontology and defined action semantics. It is not an unrestricted universal world model.

## Local views and observability

Later work emphasizes that each participant maintains a local projection of the social state. Whether a protocol is verifiable depends on whether participants can observe the events needed to determine commitment progression and compliance.

This is especially relevant to AAA because:

`FACT OCCURRED != PARTICIPANT COULD OBSERVE/VERIFY FACT`

and because cross-context interactions may require explicit bridging claims/commitments.

## Protocol composition result

A notable negative result in the literature is that two protocols that are individually verifiably enactable in their own contexts do NOT automatically yield a verifiably enactable composition when their contexts are combined. Additional design/bridging structure may be required.

This is relevant to the Owner's diversity/flexibility requirement: composability cannot be assumed merely because individual protocol families work in isolation.

## Runtime generation/adaptation

Subsequent work has explored dynamically creating or verifying new commitment protocols at runtime, and generating decentralized communication protocols from commitment specifications. This is closer to adaptive protocol support, but still generally operates within the commitment formalism rather than mutating the underlying semantic universe arbitrarily.

## Fit to current AAA-ASA-ME requirement

Strongly relevant:

- interaction-first rather than object-internal mental-state semantics;
- relation-like social state;
- events/actions progressing relational state;
- flexibility through declarative interaction constraints instead of rigid sequences;
- participant autonomy;
- explicit accountability/compliance;
- local projections and observability boundaries;
- protocol composition as a nontrivial problem;
- runtime protocol generation/verification research exists.

Only partially relevant / limitations:

- commitment is fundamentally a normative/social relation, not a general-purpose Relation/Event/world substrate;
- protocol is not identical to Relation or Event;
- arbitrary new interaction ontologies are not natively supported without extending the formalism;
- multi-personality/worldview plurality is not the central target;
- semantic model mutation/successor evolution is not a native core mechanism;
- the approach does not by itself constitute a general world model.

## Current interpretation for AAA

Best use as prior art is NOT:

`AAA Protocol should simply be a commitment protocol.`

Better use:

1. Treat commitment protocols as a strong precedent for separating participant autonomy from public interaction semantics.
2. Reuse the idea that relations can have explicit lifecycles progressed by events.
3. Reuse public/social-state semantics and observability-aware local projections.
4. Preserve the negative lesson that protocol composition can fail even when components work independently.
5. Do not import the commitment ontology as the universal ontology.
6. Keep OPEN whether AAA Protocol is a relation/event/process itself, a semantics over them, or another construct.

## Prior-art anchors

- Singh, Agent Communication Languages: Rethinking the Principles, IEEE Computer, 1998.
- Yolum & Singh, Commitment Machines, technical report 2000 / Springer 2002.
- Yolum & Singh, Flexible Protocol Specification and Execution: Applying Event Calculus Planning using Commitments, AAMAS 2002.
- Yolum & Singh, Reasoning about Commitments in the Event Calculus, Annals of Mathematics and Artificial Intelligence, 2004.
- Chopra & Singh et al., formalization/composition work, including IJCAI 2015.
- Chopra & Singh, Clouseau: Generating Communication Protocols from Commitments, AAAI 2020.
- Telang, Singh & Yorke-Smith, Maintenance of Social Commitments, AAAI 2021.

현재 상태: 외부 선행연구 1번인 commitment-based interaction protocol 계열을 심층 검토했다.
핵심 판단: 이 계열은 Protocol을 Relation/Event와 동일시하지 않고, relation-like social commitment state와 이를 진행시키는 event/action semantics를 protocol이 규정한다.
진행 작업: autonomy, social-state semantics, event-driven relation lifecycle, local projection/observability, composition failure를 AAA 후보 설계에 유용한 prior-art lesson으로 분리했다.
다음 단계: Owner와 개념 적합성을 검토한 뒤 2번 Reo/coordination model 계열로 진행한다.
사용자 행동: 이 계열에서 가져갈 것과 버릴 것을 판단하면 된다. 작성시각: 2026-08-21 20:04 KST
