# AAA-ASA-ME Owner Function/Mechanism Mutation Clarification v0.1

DATE = 2026-08-21 KST
PROJECT = AAA
PRODUCT = ASSET AGENT ASA
WORKSTREAM = AAA-ASA-ME
STATE = NON_NORMATIVE_RESEARCH_MEMORY / OWNER_EXPLICIT / HIGH_INTEREST / NOT_VALIDATED / NOT_OWNER_ACCEPTANCE

## 1. Owner explicit clarification

The Owner clarified that the intended change is not merely a state change or output variation under a fixed transition rule.

The key intuition is:

`A => B`

where the arrow/mapping itself is treated as the function/mechanism. The important mutation is:

`f_t : A -> B`

becoming

`f_(t+1) : A -> B'` or more generally a different mapping/domain/codomain/causal mechanism.

In the Owner's computer-science analogy, a website is, for its users, effectively the set of externally available web APIs/behaviors. PUT/DELETE may change stored state and therefore later outputs under the same API contract, but a deeper change occurs when the internal chain/composition of functions changes, causing the same external condition/request to map differently. In that deeper case, the mapping mechanism itself changed.

## 2. Required distinction

Do not collapse the following:

1. STATE MUTATION: `x_t -> x_(t+1)` under fixed `f`.
2. PARAMETER MUTATION: `f_theta -> f_theta'` where rule family remains fixed but parameters change.
3. MECHANISM/FUNCTION MUTATION: `f_t -> f_(t+1)` where the mapping law itself changes.
4. INTERFACE MUTATION: the set/type of admissible interactions changes.
5. TOPOLOGY/RELATION MUTATION: who/what can interact with whom/what changes.

The Owner's current emphasis is specifically #3 and its interaction with #4/#5.

## 3. Causal interpretation

A plain mathematical function changing does not by itself prove causal change. But if `f` is explicitly the causal/structural/transition mechanism, then `f_t -> f_(t+1)` is a change in the causal mechanism. In that case the same antecedent/intervention can produce a different consequent because the mechanism has changed.

A minimal formal sketch is:

`y_t = f_t(x_t)`

`f_(t+1) = M(f_t, interaction_t, context_t, history_t)`

`y_(t+1) = f_(t+1)(x_(t+1))`

where `M` is currently OPEN and must not become an unexamined fixed meta-rule that merely moves rigidity one level up.

## 4. World-model implication

The current interaction-first hypothesis should therefore not be limited to:

`interaction changes state`

or

`interaction changes interface`.

A stronger candidate is:

`interaction can change the mapping/causal mechanism that determines future interactions and outcomes`.

This makes the world model a co-evolution of states, relations/interfaces, and causal/transition mechanisms.

## 5. Prior-art relevance

Relevant existing research families include:

- nonstationary/time-varying causal models where causal strengths, local mechanisms, or graph structure may change over time;
- adaptive dynamical networks where system dynamics and network structure co-evolve;
- self-modifying systems where transition functions/rules themselves may change;
- higher-order/meta-dynamical formulations where a rule updates another rule.

These are partial precedents, not exact equivalence to the Owner's worldview.

## 6. Current research questions

- Can mechanism mutation be endogenous to interaction rather than selected from a pre-enumerated regime table?
- Can `f -> f'` be constrained/falsifiable without an infinite meta-rule regress?
- When is a change merely state/parameter drift, and when is it semantic/mechanism mutation requiring successor-model identity?
- Can multiple scales expose different functions while preserving lineage between them?
- Can relation/context select, compose, or transform mappings without forcing a single universal ontology?

## 7. Status

This is an Owner-explicit conceptual clarification and should update the interpretation of earlier `MUTATE`, `FUNCTION`, `PROTOCOL`, and `INTERACTION` discussions. It is not a canonical architecture decision.
