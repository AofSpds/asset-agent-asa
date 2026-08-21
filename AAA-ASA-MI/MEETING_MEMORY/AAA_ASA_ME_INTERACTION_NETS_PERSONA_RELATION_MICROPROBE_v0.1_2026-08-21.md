# AAA-ASA-ME Interaction Nets Persona/Relation Microprobe v0.1

DATE = 2026-08-21 KST
PROJECT = AAA
PRODUCT = ASSET AGENT ASA
WORKSTREAM = AAA-ASA-ME
STATE = NON_NORMATIVE_RESEARCH / MICROPROBE / NOT_VALIDATED / NOT_SELECTED

## 1. Goal

Test whether an Interaction-Nets-style substrate can model Persona interaction, relation formation, event-like change, and explicit capability boundaries while keeping primitive ontology minimal.

This is NOT a claim that Interaction Nets are the final world model.

## 2. Microprobe setup

Two personas A and B begin with minimal local states and no predeclared high-level social relation.

Instead of defining a rich ontology such as FRIEND / TRUST / AUTHORITY / CONTINUITY up front, the substrate contains:

- participant nodes or state-carrying agents;
- ports/interfaces through which interactions may become active;
- local interaction/rewrite rules;
- persistent graph structure or trace sufficient to preserve interaction history where required.

High-level meanings may be materialized later by a protocol/view rather than always being primitive substrate labels.

## 3. Scenario

### S0 — independent state

A and B exist without a high-level relation primitive.

### S1 — first encounter

A and B enter an active interaction.
A local rewrite changes only the participating neighborhood.
Possible outputs:

- A successor local state A1;
- B successor local state B1;
- a persistent structural link/trace K1 representing that an interaction occurred;
- provenance that K1 resulted from the exact interaction rule and input state.

The substrate itself need not immediately call K1 "trust", "friendship", or another semantic category.

### S2 — repeated interaction

A1 and B1 interact again in the context of K1.
A local rewrite may:

- strengthen, weaken, branch, replace, or delete K1;
- produce A2/B2;
- produce additional interaction trace K2;
- preserve earlier state/history rather than silently overwrite it.

A later protocol or perspective may interpret the accumulated motif/history as a relation of some type.
Different protocols may materialize different scoped meanings from the same underlying interaction history.

### S3 — disagreement of interpretation

Protocol P1 materializes the A-B history as `COOPERATIVE_RELATION`.
Protocol P2, using different purpose/evidence criteria, materializes it as `UNPROVEN_RELATION` or another scoped view.

The substrate preserves the shared interaction history while the protocol-local results remain non-universal.

### S4 — unseen interaction

A new interaction X occurs for which the frozen interaction rule set has no semantics.

Required model behavior candidates:

- `UNSUPPORTED`;
- `OUT_OF_SCOPE`;
- `UNKNOWN`;
- `REQUIRES_SUCCESSOR_MUTATION`.

The system must NOT silently improvise a new semantic rule and still claim to be the same frozen exact model.

### S5 — successor mutation

If interaction X is scientifically important and cannot be represented without semantic distortion:

- freeze the old exact model;
- propose a successor rule system/model;
- preserve lineage;
- re-test old interactions for regression/preservation;
- validate the new exact target separately.

## 4. What this probe demonstrates if successful

A successful probe would show that:

1. high-level Relation labels do not have to be primitive;
2. participant state and graph structure can both change through local interaction;
3. repeated interaction can create stable motifs/history that later support semantic materialization;
4. multiple protocols can interpret the same substrate differently without rewriting the substrate;
5. inability to support an unseen interaction can be explicit rather than hidden;
6. semantic mutation can be separated from ordinary runtime rewriting.

## 5. Critical failure modes

### F1 — hidden relation ontology
If every rewrite rule hard-codes FRIEND/TRUST/AUTHORITY/etc., rigidity was merely moved from objects to the rule table.

### F2 — rule-table explosion
If each interaction type requires a unique explicit pairwise rule, heterogeneous real-world interaction may become intractable.

### F3 — identity smuggling
If persistent persona identity must be hard-coded externally for the net to work, the model has not explained continuity/identity; it has imported it.

### F4 — semantic emptiness
If the substrate supports arbitrary rewrites but cannot support meaningful/provenance-preserving interpretation, it is computationally expressive but not a useful world model.

### F5 — confluence collapse
Classical Interaction Nets value strong confluence. If the AAA world model must preserve multiple legitimate non-convergent histories/views, classical confluence may be too restrictive.

### F6 — mutation escape hatch
If every unsupported interaction triggers mutation, the model becomes unfalsifiable and unconstrained.

## 6. Two competing variants exposed by the probe

### V1 — SEMANTIC-HEAVY INTERACTION NET
Relation/Event semantics are partially explicit in node/rule types.

Advantages:
- easier interpretation;
- stronger local semantics;
- easier verification.

Risks:
- premature ontology;
- lower flexibility;
- rule explosion.

### V2 — MINIMAL INTERACTION SUBSTRATE
Substrate stores minimal interaction/state/topology/history; higher-level Relation/Event/Persona meanings are materialized by protocol/perspective.

Advantages:
- low rigidity;
- protocol plurality;
- better fit to the Owner's current interaction-first intuition.

Risks:
- semantic emptiness;
- hidden complexity moved into protocol/materialization layer;
- weak predictive constraints if too unconstrained.

Neither is selected.

## 7. Current research implication

The highest-value next executable test is NOT "Can Interaction Nets represent computation?" — that is already known.

The discriminating question is:

`Can a small interaction substrate preserve enough structure, history, uncertainty, and provenance that multiple high-level meanings can be materialized without requiring a large fixed ontology or an unbounded rule set?`

A second discriminating question is:

`When a genuinely new interaction appears, can the model distinguish ordinary runtime rewrite from a case requiring a successor semantic model?`

## 8. Owner signal

OWNER_EXPLICIT / CURRENT-MESSAGE SIGNAL:

- The Owner expressed strong positive interest in Interaction Nets and prior adjacent models.
- The Owner's current intuition is that the model may only need to implement interaction, with richer meanings potentially emerging or being materialized elsewhere.

This is a high-interest research direction, NOT Owner Acceptance or canonical model selection.

현재 상태: Interaction Nets를 Persona/Relation 형성에 직접 적용하는 최소 microprobe를 설계했다.
핵심 판단: 가장 유망한 포인트는 `local interaction -> participant/topology rewrite -> later semantic materialization`이며, 가장 큰 위험은 ontology rigidity가 interaction rule table로 이동하는 것이다.
진행 작업: semantic-heavy variant와 minimal-interaction-substrate variant를 분리하고 unsupported interaction / successor mutation 경계를 포함했다.
다음 단계: 작은 executable prototype에서 동일 interaction history를 두 protocol이 다르게 materialize하고 unseen interaction에서 명시적 UNSUPPORTED를 반환하는지 시험한다.
사용자 행동: Interaction Nets를 강한 후보로 유지하되 아직 relation/event/persona primitive를 제거한다고 확정하지 않는다. 작성시각: 2026-08-21 20:34 KST
