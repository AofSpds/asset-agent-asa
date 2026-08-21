# AAA-ASA-ME Owner Interaction-Ruleset and Interface Primitive Clarification v0.1

DATE = 2026-08-21 KST
PROJECT = AAA
PRODUCT = ASSET AGENT ASA
WORKSTREAM = AAA-ASA-ME
STATE = NON_NORMATIVE_RESEARCH_MEMORY / OWNER_EXPLICIT / NOT_VALIDATED / NOT_OWNER_ACCEPTANCE

## Owner-explicit worldview clarification

The Owner clarified that the intended primitive is not a metaphysically self-contained Object but an organized set of interactions / interaction rules.

Key statements:
- API is an interface: from an external participant's operational perspective, a web system is encountered as a set of callable interactions, rules, mappings, and effects.
- Calling API/interface 'abstraction' does not make interaction dispensable. The abstraction may expose an irreducible interaction surface while hiding implementation.
- `A => B`: the `=>` mapping/function is central. Domain and codomain may themselves contain functions; higher-order mappings and chained function composition are allowed.
- A system can therefore be represented as an ensemble of mappings / interaction rules, including mappings from functions/rule-sets to other functions/rule-sets.
- State change differs from mechanism change. If the internal chain of functions changes, the same external input may yield a different result because the mapping law itself changed.
- Object-oriented implementation still exposes usable behavior through interfaces/methods/contracts; this motivates investigation of whether Object is representational convenience while interaction is computationally unavoidable.
- A person should not automatically be modeled as a single primitive object. The Owner views a person as a higher-level organization/set of many interacting elements. The same applies to communities and other systems.
- The Owner used neural interaction as an intuition: a brain/person is not a single indivisible computing atom, but an organized biological network. Neuroscientifically, this should not be reduced to neurons only; glia, body, and broader biological interactions may also matter.
- The Owner hypothesizes that treating the person as a singular self-contained object can create modeling error, partly because human conscious self-experience encourages reification of a unified self. This is a philosophical/modeling hypothesis, not an established neuroscientific fact.

## Current computational hypothesis

INTERACTION / INTERACTION-RULE SET is a stronger primitive candidate than OBJECT.

A useful operational hierarchy is:

`interaction rules / mappings`
→ `organized recurring interaction pattern`
→ `system-like stable bundle`
→ `object/person/community as a materialized view at some scale/context`

A system may expose an interface that is itself a bundle of interaction contracts. The external interface can remain stable while internal function chains change, or the interface itself can change.

For stateful systems, pure `A -> B` is often insufficient. A better form is:

`(state_t, input_t) -> (state_t+1, output_t)`

For mechanism mutation:

`F_t -> F_t+1`

and for higher-order mechanism change:

`M(F_t, interaction_t) -> F_t+1`

The fixed-meta-rule regress (`what changes M?`) remains OPEN and must not be hidden by another unexamined primitive.

## Important terminology control

- API = Application Programming Interface, literally an interface.
- An API is not necessarily a pure mathematical function; state, side effects, concurrency, nondeterminism, failures, and external dependencies may require transition relations/process semantics.
- `mapping/function`, `causal mechanism`, `interaction rule`, and `interface contract` overlap in some models but are NOT automatically identical.

## Research consequence

Future prior-art search should prioritize theories where:
1. systems are behavior/interface/interaction-defined rather than object-intrinsic;
2. interactions compose recursively;
3. interaction rules/functions themselves can change;
4. higher-level systems emerge from interacting lower-level components;
5. no privileged indivisible object boundary is required;
6. meta-rule rigidity and regress are explicit test targets.
