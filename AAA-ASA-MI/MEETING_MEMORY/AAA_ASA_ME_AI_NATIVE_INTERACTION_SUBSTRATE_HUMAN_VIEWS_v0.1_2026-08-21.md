# AAA-ASA-ME AI-Native Interaction Substrate / Human Materialized Views v0.1

DATE = 2026-08-21 KST
PROJECT = AAA
PRODUCT = ASSET AGENT ASA
WORKSTREAM = AAA-ASA-ME
STATE = NON_NORMATIVE_RESEARCH_MEMORY / OWNER_EXPLICIT_HIGH_INTEREST_HYPOTHESIS / NOT_VALIDATED / NOT_SELECTED

## Owner signal

The Owner noted that expressing data, bindings, objects, and systems purely through functions/processes/interactions may be difficult for humans to author and inspect, but AAA has ASA as an AI partner. Therefore human cognitive ergonomics need not be the sole reason to preserve Object/Class-centered canonical representation.

## Current hypothesis

A plausible architecture is:

1. Canonical or lower-level substrate optimized for structural fidelity, potentially interaction/morphism/process/rule/composition-first rather than Object-first.
2. ASA operates as compiler/interpreter/reasoner over that substrate.
3. Human-facing representations are materialized views: Object, Class, API, Persona, Relation, Event, graph, table, narrative, etc., selected for the current task and perspective.
4. Human usability and auditability remain requirements, but they need not dictate the ontology of the underlying model.
5. The human-facing object view must never silently become a second semantic source of truth.

## Key distinction

AI_MAINTAINABILITY != HUMAN_DIRECT_AUTHORABILITY

A representation may be difficult for humans to manipulate directly but still be viable if ASA can reliably:
- compose/decompose;
- explain provenance;
- project task-specific views;
- verify equivalence/preservation;
- expose uncertainty and unsupported cases;
- provide reversible transforms between substrate and human view.

## Major risk

Do not use AI complexity-handling as permission for an unconstrained or opaque substrate. The substrate must still support deterministic identity/provenance where required, validation, replay/debugging, capability boundaries, and stable semantic digests.

## Research implication

Compare at least two engineering hypotheses:

A. HUMAN-FIRST CANONICAL MODEL
Object/Class/API-like constructs remain canonical because they maximize inspectability.

B. AI-NATIVE INTERACTION CANONICAL MODEL
Interaction/process/morphism/rule composition is canonical; Object/Class/API are generated materialized views for humans and integrations.

A hybrid is also open: compact typed interaction substrate plus governed human views.

No architecture is selected.
