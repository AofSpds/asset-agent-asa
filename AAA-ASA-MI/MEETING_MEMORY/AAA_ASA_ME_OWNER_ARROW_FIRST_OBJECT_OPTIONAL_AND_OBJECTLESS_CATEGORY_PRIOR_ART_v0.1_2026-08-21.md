# AAA-ASA-ME Arrow-First / Object-Optional Worldview Clarification v0.1

DATE = 2026-08-21 KST
PROJECT = AAA
PRODUCT = ASSET AGENT ASA
WORKSTREAM = AAA-ASA-ME
STATE = NON_NORMATIVE_RESEARCH_MEMORY / OWNER_EXPLICIT + PRIOR_ART_NOTE / NOT_VALIDATED / NOT_OWNER_ACCEPTANCE

## Owner-explicit clarification

The Owner's current computational intuition is:

- API is an interface: externally, a software system is encountered through a set of allowed interactions/contracts.
- OOP's Object + Interface decomposition is not assumed to be ontologically fundamental. An object/class can already be interpreted as a bundle of state/history plus interaction rules/functions.
- Stateful behavior can be represented functionally as `(state_t, input_t) -> (state_t+1, output_t)`.
- If the state/class variables are carried in the domain/codomain, an OO-style object can be encoded as a transition/function bundle rather than requiring Object as a primitive.
- Higher-order functions allow functions/rule-sets themselves in domains/codomains, so mechanism mutation can be represented as `M(F_t, interaction_t) -> F_{t+1}`.
- The Owner's strong hypothesis is therefore `interaction / interaction-rule set first`, with Object/Person/Community as optional higher-level materializations of recurring organized interaction.
- Treating a human as a single primitive object may be a modeling convenience reinforced by unified self-experience; computationally/biologically a human is a higher-level organization of many interacting subsystems. This is a philosophical/modeling hypothesis, not an established neuroscientific claim.

## Important technical nuance

`A -> B` is a mathematical function only when each complete input determines a unique output. Real APIs may have state, side effects, concurrency, nondeterminism, failures, and external dependencies. These can be modeled by explicit state threading, relations, transition systems, transducers, processes, or morphisms. Therefore the broader primitive candidate is better named `arrow / interaction / process / morphism` than pure function alone until the exact formalism is selected.

## Why OOP still creates Objects and Interfaces

The separation is strongly useful for engineering:
- encapsulation and access control;
- stable names/handles to mutable state and resources;
- modularity and local reasoning;
- substitutability, contracts, and version compatibility;
- type checking/dispatch;
- lifecycle and ownership;
- change isolation across teams/components.

These practical benefits do not establish Object as a fundamental computational/world-model primitive.

## Prior-art note: objectless/category-free category theory

A directly relevant formal precedent exists: objectless (object-free) category theory can be formulated using morphisms/arrows and their composition without primitive object variables. Standard objects can be represented/recovered through identity morphisms. This is mathematically equivalent to the ordinary object+morphism formulation, so syntactic removal of objects does not erase all identity structure; formal identity remains encoded in identity arrows.

This is highly relevant to the Owner's `A => B` / arrow-first intuition:
- arrows/morphisms can be primitive;
- composition is fundamental;
- what standard language calls an object can emerge as an identity/compositional role;
- but some identity/invariance structure remains necessary for composition to be well-formed.

Research implication: compare the current Trinity Primitive hypothesis (제법무아 / 오온개공 / 연기설) against arrow-first/objectless category theory, process categories, behavioral systems, coalgebra, and dynamic interaction formalisms. The key discriminator is whether object identity can remain merely contextual/compositional while interaction rules themselves can mutate without hidden fixed meta-rule rigidity.
