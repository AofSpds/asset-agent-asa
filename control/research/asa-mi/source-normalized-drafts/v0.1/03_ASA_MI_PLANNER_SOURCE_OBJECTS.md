# ASA-MI Planner / Deep-Search Source Objects

```text
ARTIFACT_CLASS = SOURCE_NORMALIZED_OBJECT_SET
SOURCE_SCOPE = SRC-MI0 + SRC-MI1
SOURCE_DERIVED_ONLY = TRUE
FORMAL_VALIDATION = NONE
TAGGING_STATE = DRAFT
```

## A. Founding proposition cluster

### SN-MI-H-001

```text
CLASS = OWNER_PROPOSITION_IN_SOURCE / WORKING_HYPOTHESIS
SOURCE = SRC-MI0
STATEMENT = Identity ?= Memory
SOURCE_WORDING = "정체성은 기억입니다."
CONFIRMATION = UNCONFIRMED
DOES_NOT_ASSERT = SCIENTIFICALLY_PROVEN_HUMAN_ONTOLOGY
```

### SN-MI-H-002

```text
CLASS = WORKING_HYPOTHESIS
SOURCE = SRC-MI0
STATEMENT = Stable ID, runtime, and prompt may locate/execute/initialize a Persona without constituting substantive Persona identity.
```

### SN-MI-H-003

```text
CLASS = MODEL_CANDIDATE
SOURCE = SRC-MI0
STATEMENT = Substantive Persona identity may emerge from durable memory + organization + lineage + consolidated experience + current standpoint/learned dispositions.
STATE = SOURCE_CANDIDATE / NOT FINAL
```

### SN-MI-H-004

```text
CLASS = WORKING_HYPOTHESIS
SOURCE = SRC-MI1
STATEMENT = Persona does not require continuous runtime consciousness/process continuity.
IMPLIED_TEST = terminate runtime and reconstruct from governed persisted state
```

## B. Memory lifecycle cluster

### SN-MI-M-001

```text
CLASS = MODEL_CANDIDATE
SOURCE = SRC-MI0
NAME = FORWARD_MEMORY_LIFECYCLE
FORM = EXPERIENCE/OWNER_CONVERSATION/EXECUTION/OUTCOME → MEMORY_CANDIDATE → IMPORTANCE/RELEVANCE/DURABILITY_JUDGMENT → WORKING_MEMORY → DURABLE_MEMORY → CONSOLIDATED_MEMORY → IDENTITY/EXPERTISE_CORE when appropriate
STATUS = WORKING_SOURCE_MODEL
```

### SN-MI-M-002

```text
CLASS = MODEL_CANDIDATE
SOURCE = SRC-MI0
NAME = REVERSE_MEMORY_LIFECYCLE
FORM = ACTIVE → DORMANT → STALE → SUPERSEDED or CONFLICTING → ARCHIVED → CONTROLLED_FORGETTING when appropriate
STATUS = WORKING_SOURCE_MODEL
```

### SN-MI-PC-001

```text
CLASS = PRINCIPLE_CANDIDATE
SOURCE = SRC-MI0
STATEMENT = Memory requires lifecycle.
```

### SN-MI-OQ-001

```text
CLASS = OPEN_QUESTION
SOURCE = SRC-MI0 + SRC-MI1
QUESTION = Which lifecycle states are intrinsic memory semantics versus implementation-specific storage/retrieval states?
```

## C. Memory origin and provenance

### SN-MI-PC-002

```text
CLASS = AUTHORITY_FIREWALL
SOURCE = SRC-MI0
STATEMENT = MODEL_CURATED_MEMORY != OWNER_INTENT
```

### SN-MI-M-003

```text
CLASS = MODEL_CANDIDATE
SOURCE = SRC-MI0 + SRC-MI1
ORIGIN_CLASSES = [OWNER_EXPLICIT, OBSERVED_EVENT, EXTERNAL_EVIDENCE, PERSONA_INTERPRETATION, EXTERNAL_MODEL_INFERENCE]
RULE = origin should survive consolidation
```

### SN-MI-PC-003

```text
CLASS = PRINCIPLE_CANDIDATE
SOURCE = SRC-MI1
STATEMENT = Derived Persona State should remain evidence-linked.
EXAMPLE = current belief/preference/heuristic should be traceable to supporting and conflicting historical evidence where possible
```

### SN-MI-RISK-001

```text
CLASS = RISK_CLAIM
SOURCE = SRC-MI1
STATEMENT = Repeated summarization/consolidation can corrupt or launder provenance and meaning.
```

## D. Memory is not a single undifferentiated type

### SN-MI-M-004

```text
CLASS = MODEL_CANDIDATE
SOURCE = SRC-MI1
CANDIDATE_COMPONENTS = [
  RAW_EXPERIENCE,
  EPISODIC_MEMORY,
  SEMANTIC_PERSONAL_KNOWLEDGE,
  RELATIONSHIP_MEMORY,
  PROCEDURAL_EXPERTISE,
  PREFERENCES_HEURISTICS,
  CURRENT_STANDPOINT,
  PERSONA_INTERPRETATIONS,
  META_MEMORY,
  PROVENANCE,
  CONFLICT_SUPERSESSION_RELATIONS
]
RULE = do not assume all components are truly Memory
```

### SN-MI-OQ-002

```text
CLASS = OPEN_QUESTION
SOURCE = SRC-MI1
QUESTION = Which components are memory, derived state, index/metadata, identity-bearing state, or reconstructable views?
```

### SN-MI-RISK-002

```text
CLASS = RISK_CLAIM
SOURCE = SRC-MI1
STATEMENT = If every persistent Persona-bearing component is renamed Memory, Identity = Memory becomes tautological and unfalsifiable.
```

## E. Raw history vs current interpretation

### SN-MI-PC-004

```text
CLASS = PRINCIPLE_CANDIDATE
SOURCE = SRC-MI1
STATEMENT = Historical experience should remain distinguishable from current interpretation.
```

### SN-MI-M-005

```text
CLASS = MODEL_CANDIDATE
SOURCE = SRC-MI1
FORM = RAW_EXPERIENCE / EVENT_EVIDENCE → derived knowledge / heuristics / relationship understanding / expertise → current Persona reconstruction
RULE = derived state does not erase source history
```

### SN-MI-RISK-003

```text
CLASS = RISK_CLAIM
SOURCE = SRC-MI1
STATEMENT = A static persona_summary repeatedly overwritten by an LLM may create semantic drift or catastrophic history distortion.
```

## F. Common vs Persona-local memory

### SN-MI-H-005

```text
CLASS = WORKING_HYPOTHESIS / MODEL_CANDIDATE
SOURCE = SRC-MI1
FORM = COMMON_MEMORY + PERSONA_LOCAL_MEMORY + EPHEMERAL_WORKING_CONTEXT
```

### SN-MI-M-006

```text
CLASS = MODEL_CANDIDATE
SOURCE = SRC-MI1
COMMON_MEMORY_CANDIDATES = [important shared Owner history, high-value project history, common lineage, high-confidence shared events, explicit Owner statements, common relationship context]
PERSONA_LOCAL_CANDIDATES = [specialized experience, role-specific lessons, local heuristics, unique interaction histories, Persona-specific interpretations]
```

### SN-MI-RISK-004

```text
CLASS = RISK_CLAIM
SOURCE = SRC-MI1
STATEMENT = Persona-local interpretation promoted into Common Memory can propagate a mistaken cognitive mutation across Personas.
```

### SN-MI-OQ-003

```text
CLASS = OPEN_QUESTION
SOURCE = SRC-MI1
QUESTION = What may move from Persona-local memory into Common Memory, and under what evidentiary/semantic conditions?
```

## G. Representation and index layer

### SN-MI-PC-005

```text
CLASS = PRINCIPLE_CANDIDATE
SOURCE = SRC-MI1
STATEMENT = Tag/vector/graph/embedding should not be equated with Persona identity or canonical memory merely because they support retrieval.
```

### SN-MI-H-006

```text
CLASS = WORKING_HYPOTHESIS
SOURCE = SRC-MI1
STATEMENT = Canonical durable memory/history should outlive current vector DB, graph DB, embedding model, LLM, and provider.
```

### SN-MI-H-007

```text
CLASS = WORKING_HYPOTHESIS
SOURCE = SRC-MI1
STATEMENT = Derived indices should ideally be rebuildable from more durable source representations.
```

### SN-MI-OQ-004

```text
CLASS = OPEN_QUESTION
SOURCE = SRC-MI1
QUESTION = Can graph/vector/index artifacts contain irrecoverable semantic judgments such that rebuilding changes Persona meaning?
```

## H. Reconstruction

### SN-MI-H-008

```text
CLASS = WORKING_HYPOTHESIS
SOURCE = SRC-MI1
STATEMENT = The central technical problem may be Persona Reconstruction rather than Memory Storage.
```

### SN-MI-M-007

```text
CLASS = MODEL_CANDIDATE
SOURCE = SRC-MI1
CURRENT_INSTANCE_INPUT_CANDIDATES = [
  compact shared autobiographical core,
  Persona-local memory,
  current derived standpoint,
  current expertise,
  recent events,
  task-relevant old episodes,
  unresolved conflicts,
  important relationship state,
  applicable governance,
  current authority references
]
RULE = not all historical memory should be loaded into every runtime context
```

### SN-MI-RISK-005

```text
CLASS = RISK_CLAIM
SOURCE = SRC-MI1
STATEMENT = Reconstruction policy itself may become a hidden model-dependent Persona owner.
```

## I. Forgetting / deletion

### SN-MI-H-009

```text
CLASS = WORKING_HYPOTHESIS
SOURCE = SRC-MI1
STATEMENT = Biological-style forgetting is not required; functional forgetting may be implemented through lower retrieval salience, dormancy, supersession, archival, task-specific non-retrieval, or selective compression.
```

### SN-MI-PC-006

```text
CLASS = PRINCIPLE_CANDIDATE
SOURCE = SRC-MI1
STATEMENT = Content deletion may be a separate privacy/security operation from functional forgetting.
```

### SN-MI-OQ-005

```text
CLASS = OPEN_QUESTION
SOURCE = SRC-MI1
QUESTION = Which forms of forgetting preserve useful identity/history and which create harmful permanent dossiers or destructive information loss?
```

## J. Fission / Merge

### SN-MI-H-010

```text
CLASS = WORKING_HYPOTHESIS
SOURCE = SRC-MI1
STATEMENT = Fission can be modeled as shared origin + inherited common/relevant memory + lineage → divergent experiences → divergent memory/personality/expertise.
```

### SN-MI-PC-007

```text
CLASS = AUTHORITY_FIREWALL
SOURCE = SRC-MI1
STATEMENT = COPY(Persona Memory/State) != COPY(Authority)
```

### SN-MI-H-011

```text
CLASS = WORKING_HYPOTHESIS
SOURCE = SRC-MI1
STATEMENT = Merge is not union, overwrite, or a single synthesized summary; it may require contradiction coexistence, provenance, conflict representation, reconciliation, and a new current interpretation.
```

### SN-MI-H-012

```text
CLASS = WORKING_HYPOTHESIS
SOURCE = SRC-MI1
STATEMENT = Fission appears easier than Merge; Merge may be deferred.
```

## K. Provider/local compute / user-side standpoint

### SN-MI-PC-008

```text
CLASS = DESIGN_INTENT_IN_SOURCE
SOURCE = SRC-MI1
STATEMENT = CLOUD LOSS != PERSONA LOSS
```

### SN-MI-H-013

```text
CLASS = WORKING_HYPOTHESIS
SOURCE = SRC-MI1
STATEMENT = A local degraded mode may preserve core memory access, compact reconstruction, authority boundaries, new-experience recording, export/recovery, and external-compute routing without cloud parity.
```

### SN-MI-PC-009

```text
CLASS = DESIGN_INTENT_IN_SOURCE
SOURCE = SRC-MI1
STATEMENT = MEMORY LIFETIME > MODEL LIFETIME
```

### SN-MI-PC-010

```text
CLASS = DESIGN_INTENT_IN_SOURCE
SOURCE = SRC-MI1
STATEMENT = External compute may be used aggressively while long-lived standpoint remains user-side governed.
```

### SN-MI-PC-011

```text
CLASS = PRINCIPLE_CANDIDATE
SOURCE = SRC-MI1
FORM = External Model Output != Persona Memory != Persona Belief != Owner Intent != Authority
RELATED = INFLUENCE != GOVERNANCE
```

### SN-MI-OQ-006

```text
CLASS = OPEN_QUESTION
SOURCE = SRC-MI1
QUESTION = Can user-side memory/standpoint remain meaningfully sovereign if dominant reasoning priors and framing are supplied by centralized external models?
```

## L. Authority separation

### SN-MI-PC-012

```text
CLASS = AUTHORITY_FIREWALL
SOURCE = SRC-MI0 + SRC-MI1
STATEMENT = MEMORY != AUTHORITY
RELATED = [CAPABILITY_CHANGE != AUTHORITY_CHANGE, GROWTH != AUTHORITY, INTIMACY != AUTHORITY, SELF_MEMBERSHIP != AUTHORITY]
```

### SN-MI-M-008

```text
CLASS = MODEL_CANDIDATE
SOURCE = SRC-MI1
FORM = Experience/performance/relationship → authority-expansion candidate → product-side audit/review → scoped proposal → user/applicable governance approval → separate active grant
STATUS = SOURCE_PRODUCT_IDEA / NOT REQUIREMENT
```

### SN-MI-OQ-007

```text
CLASS = OPEN_QUESTION
SOURCE = SRC-MI1
QUESTION = When should existing authority expire or be re-reviewed after material Persona change?
```

## M. Product retention / relational value

### SN-MI-DI-001

```text
CLASS = DESIGN_INTENT_IN_SOURCE
SOURCE = SRC-MI1
STATEMENT = Retention should ideally arise from familiarity, relationship, usefulness, stability, friendliness, and controlled authority rather than technical hostage mechanisms.
```

### SN-MI-PC-013

```text
CLASS = PRINCIPLE_CANDIDATE
SOURCE = SRC-MI1
STATEMENT = VALUE_BASED_RETENTION != STRUCTURAL_CAPTURE
```

### SN-MI-RISK-006

```text
CLASS = RISK_CLAIM
SOURCE = SRC-MI1
STATEMENT = Emotional intimacy can itself create coercive or cognitive switching costs even if technical portability is perfect.
```

## N. Experiments / evaluation

### SN-MI-EXP-001

```text
CLASS = EXPERIMENT_CANDIDATE
SOURCE = SRC-MI1
FORM = SAME_INIT + SAME_MODEL + DIFFERENT_EXPERIENCE → measure durable Persona divergence
```

### SN-MI-EXP-002

```text
CLASS = EXPERIMENT_CANDIDATE
SOURCE = SRC-MI1
FORM = SAME_INIT + SAME_MEMORY + DIFFERENT_MODEL → measure continuity under model change
```

### SN-MI-PC-014

```text
CLASS = EVALUATION_PRINCIPLE
SOURCE = SRC-MI1
STATEMENT = Different tone/vocabulary/name/format is insufficient evidence of Persona evolution.
```

### SN-MI-EVAL-001

```text
CLASS = EVALUATION_DIMENSION_SET
SOURCE = SRC-MI1
DIMENSIONS = [evidence weighting, uncertainty treatment, risk tolerance, recall selection, causal interpretation, spontaneous self-history use, procedural expertise, dissent behavior, error patterns, permission behavior, task decomposition, relationship interpretation, stable decision tendencies]
```

## O. Candidate research requirements from the source

The source itself explicitly treated these as research requirements/proposals, not approved AAA Requirements.

```text
RAW_EXPERIENCE_PRESERVATION
RUNTIME_RECONSTRUCTION
COMMON_LOCAL_SEPARATION
EVIDENCE_LINKED_DERIVED_STATE
REBUILDABLE_INDICES
CURRENT_VALIDITY
ORIGIN_PRESERVATION
MEMORY_AUTHORITY_SEPARATION
LOCAL_DEGRADED_MODE
PROVIDER_SWAP_TESTING
FISSION_WITH_LINEAGE_AND_NO_AUTHORITY_COPY
MERGE_AS_RECONCILIATION
POISONING_AND_OVERINFERENCE_TESTING
TRAJECTORY_CHANGE_EVALUATION
RETENTION_VS_MANIPULATION_SEPARATION
```

These remain source-level candidates until later tagging/reconciliation.
