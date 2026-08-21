# AAA-ASA-ME Prior-Art Deep Dive — Interaction Nets / Interaction Combinators v0.1

DATE = 2026-08-21 KST
PROJECT = AAA
PRODUCT = ASSET AGENT ASA
WORKSTREAM = AAA-ASA-ME
STATE = NON_NORMATIVE_RESEARCH_MEMORY / PRIOR_ART_DEEP_DIVE / NOT_VALIDATED / NOT_OWNER_ACCEPTANCE

## 1. Source family

Primary prior art:
- Yves Lafont, "Interaction Nets", POPL 1990.
- Yves Lafont, "Interaction Combinators", Information and Computation 137(1), 1997.
- Later implementation/calculus work by Ian Mackie, Maribel Fernández, Hassan/Mackie/Sato, et al.

## 2. Core mechanics

An Interaction Net is an undirected graph of agents. Each agent has exactly one distinguished principal port and zero or more auxiliary ports.

Two agents connected principal-port to principal-port form an ACTIVE PAIR.

Computation is local graph rewriting:

`ACTIVE_PAIR -> REPLACEMENT_NET`

subject to preserving the external interface/free ports.

A standard Interaction Net system has at most one rewrite rule for each pair of agent types. This gives binary, local interaction and the strong-confluence / one-step diamond property: independent reductions can occur in either order and still reconverge.

This creates natural local parallelism and distributed execution.

## 3. Interaction Combinators

Lafont's 1997 Interaction Combinators reduce the computational basis to three symbols (`gamma`, `delta`, `epsilon`) and six interaction rules while retaining universality as a distributed computation model.

Research significance for AAA:
- very small local primitive set can generate arbitrarily rich global computation;
- interaction is the operational primitive;
- network topology is rewritten by interaction;
- a large centralized world-state transition function is not required.

## 4. Strong fit with current Owner intuition

OWNER_CURRENT_INTUITION:
`The model may only need to implement interaction well; rich semantics need not all be primitive inside the model.`

Interaction Nets are highly relevant because:
- the system state is a network, not a monolithic object record;
- computation occurs only through local interactions;
- local interactions rewrite the global network structure;
- many independent interactions may proceed concurrently;
- rich global behavior can emerge from sparse local machinery.

This is a stronger minimal-interaction hypothesis than Reo:
- Reo: interaction/coordination is first-class between components.
- Interaction Nets: computation itself is interaction-driven graph rewriting.

## 5. Critical mismatch / rigidity risk

Pure Interaction Nets are not automatically flexible in the Owner's sense.

Once the signature and rewrite rules are fixed, the runtime is intentionally highly constrained:
- only principal-port active pairs interact;
- interaction is binary;
- at most one rule exists for each active-pair type in the standard formalism;
- strong confluence tends to suppress alternative reduction outcomes (assuming normalization).

Therefore Interaction Nets may remove OBJECT-ONTOLOGY rigidity while moving rigidity into the INTERACTION-RULE layer.

Key AAA research question:
`Does flexibility come from an interaction substrate, or does the substrate merely relocate fixed semantics into a static rule table?`

## 6. Candidate role for AAA world-model research

Do NOT treat Interaction Nets as a ready-made complete world model.

High-value candidate interpretations:

A. `RUNTIME INTERACTION SUBSTRATE`
- world/persona state materialized as a graph/network;
- events occur as local interactions/rewrite;
- protocols may constrain/select/compose rewrite semantics.

B. `MINIMAL INTERACTION WORLD HYPOTHESIS`
- Object/Relation/Event/Protocol may be higher-order materializations over a more primitive interaction/rewrite substrate.

C. `SUCCESSOR-MUTABLE RULE ECOLOGY`
- ordinary runtime = local rewrite under current rules;
- unsupported interaction = explicit capability boundary;
- material need for new rule semantics = successor-model mutation rather than silent in-place repair.

## 7. Protocol placement remains OPEN

Do NOT identify Protocol with Relation/Event or with the rewrite rule set yet.

Competing possibilities:
- Protocol = rule set / interaction law;
- Protocol = a compositional structure that selects or scopes interaction rules;
- Protocol = executable network/subgraph;
- Protocol = interpretation/materialization over interaction traces;
- Protocol = a distinct model interacting with the interaction substrate.

## 8. Key performance implications

If Interaction-Net-derived candidates are generated, test at least:
- unseen interaction support;
- rule-set extensibility without ontology collapse;
- explicit UNSUPPORTED / OUT_OF_SCOPE behavior;
- whether semantic diversity can coexist despite confluence pressure;
- ability to preserve multiple local perspectives;
- dynamic rule/protocol composition;
- distinction between network-state rewrite and model-semantic mutation;
- whether plurality is represented or accidentally normalized into a single normal form.

## 9. Current research tag

TAG = HIGH_RELEVANCE_MINIMAL_INTERACTION_PRIOR_ART
WORLDVIEW_FIT = HIGH_POTENTIAL
ARCHITECTURAL_FIT = HIGH_POTENTIAL
MAIN_RISK = INTERACTION_RULE_RIGIDITY / CONFLUENCE_VS_PLURALITY
SELECTION_STATE = NOT_SELECTED
OWNER_ACCEPTANCE = NONE

현재 상태: Interaction Nets/Interaction Combinators의 핵심 구조와 AAA 요구의 적합성을 심층 검토했다.
핵심 판단: `computation = local interaction + graph rewrite`라는 최소 상호작용 가설은 매우 유력하지만 고정 rule set이 새로운 경직성으로 이동할 위험이 있다.
진행 작업: Reo와 분리하여 Interaction Nets를 runtime interaction substrate / minimal interaction world hypothesis 후보로 태깅하고 confluence-vs-plurality 위험을 명시했다.
다음 단계: unseen interaction, rule extensibility, protocol placement, plurality preservation, successor mutation boundary를 microprobe 대상으로 설계한다.
사용자 행동: Interaction Nets는 정답으로 확정하지 말고 강한 seed로 유지하며 `상호작용만 잘 구현하면 충분한가`를 독립 경쟁가설로 계속 검증한다. 작성시각: 2026-08-21 20:30 KST
