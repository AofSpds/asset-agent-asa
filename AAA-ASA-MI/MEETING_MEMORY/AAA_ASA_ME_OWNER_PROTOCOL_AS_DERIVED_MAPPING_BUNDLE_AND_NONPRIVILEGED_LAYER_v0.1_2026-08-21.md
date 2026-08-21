# AAA-ASA-ME — Owner Protocol-as-Mapping-Bundle Clarification v0.1

PROJECT = AAA
PRODUCT = ASSET AGENT ASA
CHANNEL = AAA-ASA-ME
OWNER_ALIAS = nemo
STATE = OWNER_EXPLICIT / HIGH-INTEREST_WORLDVIEW_HYPOTHESIS / NON_NORMATIVE / NOT_VALIDATED
DATE = 2026-08-21 KST

## Owner clarification

The current World Model should not privilege one protocol ontology or force a single protocol architecture. The model should be capable of supporting multiple kinds of mappings/interactions and multiple forms of protocol representation.

Owner statement, normalized:
- A protocol is often itself a set/bundle of mappings.
- A protocol may also be representable as a mapping such as A => B, depending on the kind of mapping/interaction.
- Whether something is appropriately called a protocol depends on the kind/role of the mapping; there is no requirement that Protocol be a fixed external meta-layer.
- Therefore protocol change P_t -> P_(t+1) is allowed in principle.
- The World Model should support both protocol-as-bundle and protocol-as-mapping cases rather than hard-coding one representation.

## Design implication candidate

PROTOCOL_IS_NOT_CURRENTLY_A_CANONICAL_PRIMITIVE.

Candidate interpretation:
- underlying substrate: generalized mappings / transformations / interactions / compositions / histories;
- protocol: a context-sensitive role/materialized view over one mapping or a bundle of mappings that constrains or describes interaction semantics;
- protocols themselves may participate in mappings, composition, differentiation, merge, and mutation;
- a mapping may transform another mapping or protocol bundle;
- do not introduce an immutable meta-protocol merely to explain protocol mutation without testing for meta-rule regress.

## Important correction

Earlier framing that placed an Object Model and Protocol Model as two fixed architectural modules is too design-biased for the Owner's present worldview. These can remain analytical views, not forced ontological modules.

The research question is not "which protocol layer should govern objects?" but whether a sufficiently general mapping/process substrate can represent objects, boundaries, protocols, identities, differentiation, merge, and change as role/context-sensitive materializations.

## Research consequence

A future ASA committee challenge should test whether candidate formalisms can natively represent:
- mapping bundles;
- mappings of mappings;
- mutable protocol bundles;
- protocol-as-role rather than privileged layer;
- 1->1, 1->N, N->1, N->M interaction shapes or equivalent generalized forms;
- composition/compatibility without hidden fixed Objects;
- mechanism/protocol mutation without merely moving rigidity to an unexamined higher meta-rule.

## Non-claim

This memo does not select Function, Morphism, Process, Interaction, Relation, Protocol, or any other primitive as canonical. It records the Owner's requirement that the model remain open enough to support multiple protocol/mapping forms and protocol mutation.
