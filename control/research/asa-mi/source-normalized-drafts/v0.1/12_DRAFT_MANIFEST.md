# ASA-MI Source-Normalized Draft Manifest v0.1

```text
DRAFT_SET_ID = AAA-ASA-MI-SOURCE-NORMALIZED-DRAFTS-v0.1
PROJECT = AAA
PRODUCT = ASSET AGENT ASA
WORKSTREAM = ASA-MI
PATH = control/research/asa-mi/source-normalized-drafts/v0.1/
AUTHORING_STATE = WORKING_SOURCE_NORMALIZATION_DRAFT
NORMATIVE_AUTHORITY = NONE
FROZEN = FALSE
PAIRED_VALIDATION = NOT_PERFORMED
INDEPENDENT_VALIDATION = NOT_PERFORMED
OWNER_ACCEPTANCE = NOT_PERFORMED
TAGGING_STATE = PENDING_OWNER_SESSION
LIVE_BRAINSTORM_ISOLATED = TRUE
```

## Files and creation commits

```text
00_README_SOURCE_NORMALIZATION_BOUNDARY.md
COMMIT = 88c09be030dc1176e310a0f0186b4b66282b57de
PURPOSE = isolation rules / semantics / provisional-ID policy

01_SOURCE_REGISTER.md
COMMIT = 56b84818a4af5fc3dfba584066a99ebb29e4e0a3
PURPOSE = exact source identities/statuses for WP1/WP2/MI/RED source cluster

02_WHITEPAPER_SOURCE_OBJECTS.md
COMMIT = 9ed9a2791b8893735d2ef92be39f3926148704fb
PURPOSE = normalize PCS-SHAI v0.1/v0.2 concepts relevant to ASA-MI

03_ASA_MI_PLANNER_SOURCE_OBJECTS.md
COMMIT = 66afc847d0028874c6d89e16b40d0c2c542aa000
PURPOSE = normalize ASA-MI activation/planner/deep-search propositions, models, risks, experiments

04_RED_I_SOURCE_OBJECTS.md
COMMIT = a123f3bbbd6580190dc37d7234ee6377b7e5984f
PURPOSE = normalize persistent-state/data-plane counter-hypotheses and kill tests

05_RED_II_SOURCE_OBJECTS.md
COMMIT = ed13c777f7e7fec209ad8922d18e926c26e1d45a
PURPOSE = normalize reconstruction/runtime/compute-portability findings and tests

06_RED_III_SOURCE_OBJECTS.md
COMMIT = 4300747b7a0a184201c0c14b7dd41e18cbef5029
PURPOSE = normalize integrity/authority/control findings and risk models

07_CROSS_SOURCE_HYPOTHESIS_CANDIDATE_MAP.md
COMMIT = b11d0912b4fc0ded1058c5eb05b41f6c8d8a040c
PURPOSE = group competing source candidates without selecting a winner

08_OPEN_QUESTION_AND_EXPERIMENT_CATALOG.md
COMMIT = d9539c9a671b14701927daba34c8713ae40ecfea
PURPOSE = source-derived research questions + experiment catalog + CS-prior indexing note

09_TAGGING_BACKLOG_NEXT_SESSION.md
COMMIT = c7a388b52a3254b724248f9a1f54b77d9bbec827
PURPOSE = owner tagging worksheet; no tags pre-applied

10_TRACEABILITY_MATRIX.md
COMMIT = c482826d6879616f606330fa88266f2fbe407bef
PURPOSE = source → object → cluster traceability and tension mapping

11_ADDITIONAL_SOURCE_OBJECTS_AND_PARKING_LOT.md
COMMIT = 02fdb7179f91c099f667673324d522a439d747b1
PURPOSE = preserve easily-lost source concepts, historical firewalls, scope/evaluation/cold-start/product semantics, and unclassified candidates
```

## Coverage summary

Current normalized draft explicitly covers:

```text
REALITY_FIRST / UNKNOWN_FRIENDLY
HUMAN_MODEL != HUMAN_PRESCRIPTION
PERSONA != MODEL / COMPUTE / PROVIDER
SELF / BOUNDARY / INTEGRATION / AUTHORITY separation
IDENTITY ?= MEMORY and strong alternatives
PROCESS_DISCONTINUITY / RECONSTRUCTION
PERSONA_STATE vs MEMORY boundary
MEMORY LIFECYCLE
PERSONA LIFECYCLE
RAW EXPERIENCE / EVIDENCE / INTERPRETATION separation
ORIGIN / PROVENANCE / DERIVATION
MEMORY_SCOPE / VISIBILITY / APPLICABILITY
MULTI-DIMENSION MEMORY EVALUATION
COMMON vs PERSONA-LOCAL MEMORY
ANTI-CONVERGENCE
CANONICAL vs DERIVED REPRESENTATION
VECTOR / GRAPH / EMBEDDING / SUMMARY semantics
RETRIEVAL / CONTEXT COMPILER hidden-ownership risk
MODEL / PROVIDER PORTABILITY
LOCAL DEGRADED SURVIVAL
FUNCTIONAL FORGETTING / DELETE / GHOST INFLUENCE
EXPERIENCE → EXPERTISE / HEURISTIC / DISPOSITION
FISSION / MERGE
AUTHORITY SEPARATION / CONTINUITY
AUDIT INDEPENDENCE
COMPOSITIONAL DRIFT / MEMORY POISONING
OWNER BURDEN / AUTOMATION
RELATIONAL RETENTION / EXIT COST
COLD-START RECOVERY
PERSONA EVOLUTION MEASUREMENT
SOURCE-DERIVED KILL TESTS / EXPERIMENTS
```

## Isolation from live brainstorming

The live dialogue after these sources developed additional ideas such as:

```text
M(Context) → Value
CURRENT as evaluation operator
SELF as context/runtime selector
constant as scoped invariant
Boundary + Change Rate + Transition Condition
external URL/reference as Memory candidate
function/function-binding as Memory candidate
Persona as instantiated Memory/State object
CS legacy as default abstraction prior
philosophy as human-reality grounding for Persona abstraction
```

These later concepts are intentionally **not merged into source-derived objects**. They are listed only as future cross-link targets in the tagging worksheet/traceability notes.

## Draft completeness disclaimer

```text
COMPLETE_SOURCE_REWRITE = FALSE
ASA_MI_RELEVANT_EXTRACTION = TRUE
EVERY_SINGLE_SENTENCE_EXTRACTED = FALSE
MAJOR_PROPOSITION_COVERAGE = BROAD_DRAFT
EXTERNAL_CITATION_REVERIFICATION = NOT_PERFORMED_IN_THIS_PASS
```

The corpus aims for high recall of material ASA-MI concepts rather than pretending every sentence from every source has been atomized.

## Recommended next-session operations

```text
1. Verify any extraction the Owner finds semantically questionable.
2. Tag Identity/Memory cluster first.
3. Link source objects to later live-brainstorm objects only after explicit review.
4. Mark mature CS-prior problems and remove unnecessary reinvention from ASA-MI research backlog.
5. Preserve counter-hypotheses even when a current-best candidate is chosen.
6. Add exact experimental/evidence links later; do not infer validation from source agreement.
7. Create successor draft rather than silently rewriting historical source meaning if the normalization schema materially changes.
```

## Authority statement

```text
THIS_DRAFT
!= AAA_REQUIREMENT
!= AAA_DESIGN_CONTRACT
!= AAA_SHARED_CONTRACT
!= OWNER_ACCEPTANCE
!= PAIRED_VALIDATION_PASS
!= INDEPENDENT_VALIDATION_PASS
!= FROZEN_BASELINE
!= PRODUCTION_AUTHORITY
```
