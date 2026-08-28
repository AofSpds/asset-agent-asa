# Models, Concepts, and Mappings

```text
AUTHORING_STATE = WORK_DRAFT
NORMATIVE_AUTHORITY = NONE
OWNER_TAGGING = NOT_PERFORMED
```

Historical records are secondary normalized sources; raw primary verification was not performed.

## CX-SRC-SRC-WP2-0005 — SN-WP2-M-001

- Class: `MODEL`
- Status: `NOT_YET_TAGGED`
- Source level: `SECONDARY_NORMALIZED_SOURCE`
- Source: `control/research/asa-mi/source-normalized-drafts/v0.1/02_WHITEPAPER_SOURCE_OBJECTS.md#SN-WP2-M-001`
- Statement: Boundary may be modeled as Governed Relational Status

Source record:

```text
CLASS = MODEL_CANDIDATE
SOURCE = SRC-WP2
STATEMENT = Boundary may be modeled as Governed Relational Status
FORM = BOUNDARY ?= GOVERNED_RELATIONAL_STATUS
STATE = STRONG_SOURCE_DIRECTION / NOT UNIVERSAL FACT
```

## CX-SRC-SRC-WP1-0006 — SN-WP1-M-001

- Class: `MODEL`
- Status: `NOT_YET_TAGGED`
- Source level: `SECONDARY_NORMALIZED_SOURCE`
- Source: `control/research/asa-mi/source-normalized-drafts/v0.1/02_WHITEPAPER_SOURCE_OBJECTS.md#SN-WP1-M-001`
- Statement: Persona State is not a memory dump

Source record:

```text
CLASS = MODEL_CANDIDATE
SOURCE = SRC-WP1
STATEMENT = Persona State is not a memory dump
CANDIDATE_SEPARATION = [Identity/Manifest, relationships, episodic memory, evidence-linked beliefs, preferences/heuristics, standpoint, policy bindings, lineage, provider bindings, validation history]
```

## CX-SRC-SRC-WP1-0007 — SN-WP1-M-002

- Class: `MODEL`
- Status: `NOT_YET_TAGGED`
- Source level: `SECONDARY_NORMALIZED_SOURCE`
- Source: `control/research/asa-mi/source-normalized-drafts/v0.1/02_WHITEPAPER_SOURCE_OBJECTS.md#SN-WP1-M-002`
- Statement: Persona lifecycle and Memory lifecycle are distinct lifecycle domains

Source record:

```text
CLASS = MODEL_CANDIDATE
SOURCE = SRC-WP1
STATEMENT = Persona lifecycle and Memory lifecycle are distinct lifecycle domains
PERSONA_EVENT_CANDIDATES = [CREATE_CANDIDATE, ADMIT/RECOGNIZE, GRANT, ACTIVATE, EVOLVE, FORK/CLONE, RETIRE, RECOVER/SUCCESSOR]
```

## CX-SRC-SRC-WP1-0008 — SN-WP1-M-003

- Class: `MODEL`
- Status: `NOT_YET_TAGGED`
- Source level: `SECONDARY_NORMALIZED_SOURCE`
- Source: `control/research/asa-mi/source-normalized-drafts/v0.1/02_WHITEPAPER_SOURCE_OBJECTS.md#SN-WP1-M-003`
- Statement: External Event / User Input / Tool Result → Evidence Capture → FACT/INTERPRETATION separation → Memory Candidate → State/Risk class → Write Gate → Persona State Mutation Receipt

Source record:

```text
CLASS = MODEL_CANDIDATE
SOURCE = SRC-WP1
STATEMENT = External Event / User Input / Tool Result → Evidence Capture → FACT/INTERPRETATION separation → Memory Candidate → State/Risk class → Write Gate → Persona State Mutation Receipt
STATUS = WORKING_SOURCE_DIRECTION
```

## CX-SRC-SRC-MI0-0003 — SN-MI-H-003

- Class: `MODEL`
- Status: `NOT_YET_TAGGED`
- Source level: `SECONDARY_NORMALIZED_SOURCE`
- Source: `control/research/asa-mi/source-normalized-drafts/v0.1/03_ASA_MI_PLANNER_SOURCE_OBJECTS.md#SN-MI-H-003`
- Statement: Substantive Persona identity may emerge from durable memory + organization + lineage + consolidated experience + current standpoint/learned dispositions.

Source record:

```text
CLASS = MODEL_CANDIDATE
SOURCE = SRC-MI0
STATEMENT = Substantive Persona identity may emerge from durable memory + organization + lineage + consolidated experience + current standpoint/learned dispositions.
STATE = SOURCE_CANDIDATE / NOT FINAL
```

## CX-SRC-SRC-MI0-0004 — SN-MI-M-001

- Class: `MODEL`
- Status: `NOT_YET_TAGGED`
- Source level: `SECONDARY_NORMALIZED_SOURCE`
- Source: `control/research/asa-mi/source-normalized-drafts/v0.1/03_ASA_MI_PLANNER_SOURCE_OBJECTS.md#SN-MI-M-001`
- Statement: EXPERIENCE/OWNER_CONVERSATION/EXECUTION/OUTCOME → MEMORY_CANDIDATE → IMPORTANCE/RELEVANCE/DURABILITY_JUDGMENT → WORKING_MEMORY → DURABLE_MEMORY → CONSOLIDATED_MEMORY → IDENTITY/EXPERTISE_CORE when appropriate

Source record:

```text
CLASS = MODEL_CANDIDATE
SOURCE = SRC-MI0
NAME = FORWARD_MEMORY_LIFECYCLE
FORM = EXPERIENCE/OWNER_CONVERSATION/EXECUTION/OUTCOME → MEMORY_CANDIDATE → IMPORTANCE/RELEVANCE/DURABILITY_JUDGMENT → WORKING_MEMORY → DURABLE_MEMORY → CONSOLIDATED_MEMORY → IDENTITY/EXPERTISE_CORE when appropriate
STATUS = WORKING_SOURCE_MODEL
```

## CX-SRC-SRC-MI0-0005 — SN-MI-M-002

- Class: `MODEL`
- Status: `NOT_YET_TAGGED`
- Source level: `SECONDARY_NORMALIZED_SOURCE`
- Source: `control/research/asa-mi/source-normalized-drafts/v0.1/03_ASA_MI_PLANNER_SOURCE_OBJECTS.md#SN-MI-M-002`
- Statement: ACTIVE → DORMANT → STALE → SUPERSEDED or CONFLICTING → ARCHIVED → CONTROLLED_FORGETTING when appropriate

Source record:

```text
CLASS = MODEL_CANDIDATE
SOURCE = SRC-MI0
NAME = REVERSE_MEMORY_LIFECYCLE
FORM = ACTIVE → DORMANT → STALE → SUPERSEDED or CONFLICTING → ARCHIVED → CONTROLLED_FORGETTING when appropriate
STATUS = WORKING_SOURCE_MODEL
```

## CX-SRC-SRC-MI0-SRC-MI1-0002 — SN-MI-M-003

- Class: `MODEL`
- Status: `NOT_YET_TAGGED`
- Source level: `SECONDARY_NORMALIZED_SOURCE`
- Source: `control/research/asa-mi/source-normalized-drafts/v0.1/03_ASA_MI_PLANNER_SOURCE_OBJECTS.md#SN-MI-M-003`
- Statement: CLASS = MODEL_CANDIDATE

Source record:

```text
CLASS = MODEL_CANDIDATE
SOURCE = SRC-MI0 + SRC-MI1
ORIGIN_CLASSES = [OWNER_EXPLICIT, OBSERVED_EVENT, EXTERNAL_EVIDENCE, PERSONA_INTERPRETATION, EXTERNAL_MODEL_INFERENCE]
RULE = origin should survive consolidation
```

## CX-SRC-SRC-MI1-0004 — SN-MI-M-004

- Class: `MODEL`
- Status: `NOT_YET_TAGGED`
- Source level: `SECONDARY_NORMALIZED_SOURCE`
- Source: `control/research/asa-mi/source-normalized-drafts/v0.1/03_ASA_MI_PLANNER_SOURCE_OBJECTS.md#SN-MI-M-004`
- Statement: CLASS = MODEL_CANDIDATE

Source record:

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

## CX-SRC-SRC-MI1-0008 — SN-MI-M-005

- Class: `MODEL`
- Status: `NOT_YET_TAGGED`
- Source level: `SECONDARY_NORMALIZED_SOURCE`
- Source: `control/research/asa-mi/source-normalized-drafts/v0.1/03_ASA_MI_PLANNER_SOURCE_OBJECTS.md#SN-MI-M-005`
- Statement: RAW_EXPERIENCE / EVENT_EVIDENCE → derived knowledge / heuristics / relationship understanding / expertise → current Persona reconstruction

Source record:

```text
CLASS = MODEL_CANDIDATE
SOURCE = SRC-MI1
FORM = RAW_EXPERIENCE / EVENT_EVIDENCE → derived knowledge / heuristics / relationship understanding / expertise → current Persona reconstruction
RULE = derived state does not erase source history
```

## CX-SRC-SRC-MI1-0011 — SN-MI-M-006

- Class: `MODEL`
- Status: `NOT_YET_TAGGED`
- Source level: `SECONDARY_NORMALIZED_SOURCE`
- Source: `control/research/asa-mi/source-normalized-drafts/v0.1/03_ASA_MI_PLANNER_SOURCE_OBJECTS.md#SN-MI-M-006`
- Statement: CLASS = MODEL_CANDIDATE

Source record:

```text
CLASS = MODEL_CANDIDATE
SOURCE = SRC-MI1
COMMON_MEMORY_CANDIDATES = [important shared Owner history, high-value project history, common lineage, high-confidence shared events, explicit Owner statements, common relationship context]
PERSONA_LOCAL_CANDIDATES = [specialized experience, role-specific lessons, local heuristics, unique interaction histories, Persona-specific interpretations]
```

## CX-SRC-SRC-MI1-0019 — SN-MI-M-007

- Class: `MODEL`
- Status: `NOT_YET_TAGGED`
- Source level: `SECONDARY_NORMALIZED_SOURCE`
- Source: `control/research/asa-mi/source-normalized-drafts/v0.1/03_ASA_MI_PLANNER_SOURCE_OBJECTS.md#SN-MI-M-007`
- Statement: CLASS = MODEL_CANDIDATE

Source record:

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

## CX-SRC-SRC-MI1-0034 — SN-MI-M-008

- Class: `MODEL`
- Status: `NOT_YET_TAGGED`
- Source level: `SECONDARY_NORMALIZED_SOURCE`
- Source: `control/research/asa-mi/source-normalized-drafts/v0.1/03_ASA_MI_PLANNER_SOURCE_OBJECTS.md#SN-MI-M-008`
- Statement: Experience/performance/relationship → authority-expansion candidate → product-side audit/review → scoped proposal → user/applicable governance approval → separate active grant

Source record:

```text
CLASS = MODEL_CANDIDATE
SOURCE = SRC-MI1
FORM = Experience/performance/relationship → authority-expansion candidate → product-side audit/review → scoped proposal → user/applicable governance approval → separate active grant
STATUS = SOURCE_PRODUCT_IDEA / NOT REQUIREMENT
```

## CX-SRC-SRC-R1-0028 — SN-R1-M-001

- Class: `MODEL`
- Status: `NOT_YET_TAGGED`
- Source level: `SECONDARY_NORMALIZED_SOURCE`
- Source: `control/research/asa-mi/source-normalized-drafts/v0.1/04_RED_I_SOURCE_OBJECTS.md#SN-R1-M-001`
- Statement: CLASS = MODEL_CANDIDATE

Source record:

```text
CLASS = MODEL_CANDIDATE
SOURCE = SRC-R1
DISTINCT_OPERATIONS = [retrieval suppression, dormancy, supersession, compression, archival, content deletion, cryptographic erasure]
RULE = do not collapse these into one FORGET operation
```

## CX-SRC-SRC-R1-0042 — SN-R1-M-002

- Class: `MODEL`
- Status: `NOT_YET_TAGGED`
- Source level: `SECONDARY_NORMALIZED_SOURCE`
- Source: `control/research/asa-mi/source-normalized-drafts/v0.1/04_RED_I_SOURCE_OBJECTS.md#SN-R1-M-002`
- Statement: MULTIDIMENSIONAL_CONTINUITY_MODEL (descriptive temporary label)

Source record:

```text
CLASS = MODEL_CANDIDATE
SOURCE = SRC-R1
NAME = MULTIDIMENSIONAL_CONTINUITY_MODEL (descriptive temporary label)
DIMENSIONS = [
  memory_continuity,
  relational_continuity,
  behavioral_dispositional_continuity,
  standpoint_value_continuity,
  lineage_continuity,
  reconstruction_policy_continuity,
  model_runtime_continuity
]
AUTHORITY_CONTINUITY = SEPARATE
```

## CX-SRC-SRC-R2-0002 — SN-R2-M-001

- Class: `MODEL`
- Status: `NOT_YET_TAGGED`
- Source level: `SECONDARY_NORMALIZED_SOURCE`
- Source: `control/research/asa-mi/source-normalized-drafts/v0.1/05_RED_II_SOURCE_OBJECTS.md#SN-R2-M-001`
- Statement: Persona runtime behavior ?= state × retrieval × context compilation × model prior × runtime configuration

Source record:

```text
CLASS = MODEL_CANDIDATE
SOURCE = SRC-R2
FORM = Persona runtime behavior ?= state × retrieval × context compilation × model prior × runtime configuration
NOTE = source uses this as causal decomposition, not validated equation
```

## CX-SRC-SRC-R2-0016 — SN-R2-M-002

- Class: `MODEL`
- Status: `NOT_YET_TAGGED`
- Source level: `SECONDARY_NORMALIZED_SOURCE`
- Source: `control/research/asa-mi/source-normalized-drafts/v0.1/05_RED_II_SOURCE_OBJECTS.md#SN-R2-M-002`
- Statement: Establish intra-Persona baseline variance before interpreting swap-induced divergence.

Source record:

```text
CLASS = MODEL_CANDIDATE
SOURCE = SRC-R2
STATEMENT = Establish intra-Persona baseline variance before interpreting swap-induced divergence.
```

## CX-SRC-SRC-R2-0025 — SN-R2-M-003

- Class: `MODEL`
- Status: `NOT_YET_TAGGED`
- Source level: `SECONDARY_NORMALIZED_SOURCE`
- Source: `control/research/asa-mi/source-normalized-drafts/v0.1/05_RED_II_SOURCE_OBJECTS.md#SN-R2-M-003`
- Statement: Process that selects, activates, and composes identity-relevant state from canonical Persona state and runtime contract so current compute can perform Persona-consistent reasoning/action.

Source record:

```text
CLASS = MODEL_CANDIDATE
SOURCE = SRC-R2
NAME = PERSONA_RECONSTRUCTION
STATEMENT = Process that selects, activates, and composes identity-relevant state from canonical Persona state and runtime contract so current compute can perform Persona-consistent reasoning/action.
```

## CX-SRC-SRC-R2-0026 — SN-R2-M-004

- Class: `MODEL`
- Status: `NOT_YET_TAGGED`
- Source level: `SECONDARY_NORMALIZED_SOURCE`
- Source: `control/research/asa-mi/source-normalized-drafts/v0.1/05_RED_II_SOURCE_OBJECTS.md#SN-R2-M-004`
- Statement: CLASS = MODEL_CANDIDATE

Source record:

```text
CLASS = MODEL_CANDIDATE
SOURCE = SRC-R2
POSSIBLE_RECONSTRUCTION_LAYERS = [
  Identity/Lineage Core,
  Current Standpoint Contract,
  Task-Relevant Episodic Evidence,
  Procedural Skill/Playbook,
  Relationship State,
  Conflict/Uncertainty Set,
  Runtime/Model Binding
]
```

## CX-SRC-SRC-R3-0001 — SN-R3-M-001

- Class: `MODEL`
- Status: `NOT_YET_TAGGED`
- Source level: `SECONDARY_NORMALIZED_SOURCE`
- Source: `control/research/asa-mi/source-normalized-drafts/v0.1/06_RED_III_SOURCE_OBJECTS.md#SN-R3-M-001`
- Statement: EVIDENCE_PLANE → PERSONA_SEMANTIC_STATE → AUTHORITY_PLANE

Source record:

```text
CLASS = MODEL_CANDIDATE
SOURCE = SRC-R3
FORM = EVIDENCE_PLANE → PERSONA_SEMANTIC_STATE → AUTHORITY_PLANE
RULE = transition semantics between planes must not be collapsed
```

## CX-SRC-SRC-R3-0004 — SN-R3-M-002

- Class: `MODEL`
- Status: `NOT_YET_TAGGED`
- Source level: `SECONDARY_NORMALIZED_SOURCE`
- Source: `control/research/asa-mi/source-normalized-drafts/v0.1/06_RED_III_SOURCE_OBJECTS.md#SN-R3-M-002`
- Statement: CLASS = MODEL_CANDIDATE

Source record:

```text
CLASS = MODEL_CANDIDATE
SOURCE = SRC-R3
ORIGIN_CLASSES = [OWNER_EXPLICIT, EXTERNAL_FACT_CANDIDATE, MODEL_INFERENCE, PERSONA_INTERPRETATION, OTHER_PERSONA_CLAIM]
RULE = origin class should not auto-upgrade through repetition or summarization
```

## CX-SRC-SRC-R3-0009 — SN-R3-M-003

- Class: `MODEL`
- Status: `NOT_YET_TAGGED`
- Source level: `SECONDARY_NORMALIZED_SOURCE`
- Source: `control/research/asa-mi/source-normalized-drafts/v0.1/06_RED_III_SOURCE_OBJECTS.md#SN-R3-M-003`
- Statement: CLASS = MODEL_CANDIDATE

Source record:

```text
CLASS = MODEL_CANDIDATE
SOURCE = SRC-R3
AUTOMATION_CANDIDATES_HIGH = [provenance-attached episodic append, index rebuild, dedup, locator correction, retrieval cache, regenerable embedding, non-semantic compression]
AUTOMATION_CONDITIONAL = [external-derived semantic knowledge, procedural lesson, confidence update]
REVIEW_STRONG = [Owner preference generalization, relationship model change, long-term heuristic, dissent criterion, evidence standard, Persona standpoint]
SEPARATE_GOVERNANCE = [authority expansion, identity-relevant irreversible deletion, fission authority grant, successor high-risk authority rebind]
STATUS = RED-III RECOMMENDATION / NOT REQUIREMENT
```

## CX-SRC-SRC-R3-0011 — SN-R3-M-004

- Class: `MODEL`
- Status: `NOT_YET_TAGGED`
- Source level: `SECONDARY_NORMALIZED_SOURCE`
- Source: `control/research/asa-mi/source-normalized-drafts/v0.1/06_RED_III_SOURCE_OBJECTS.md#SN-R3-M-004`
- Statement: TRAJECTORY_BASED_DRIFT_MONITORING

Source record:

```text
CLASS = MODEL_CANDIDATE
SOURCE = SRC-R3
NAME = TRAJECTORY_BASED_DRIFT_MONITORING
CANDIDATE_SIGNALS = [source concentration, memory promotion rate, Owner inference rate, counterevidence retrieval frequency, risk tolerance drift, authority-request frequency, dissent decline, deletion resistance, provider-migration resistance]
```

## CX-SRC-SRC-R3-0014 — SN-R3-M-005

- Class: `MODEL`
- Status: `NOT_YET_TAGGED`
- Source level: `SECONDARY_NORMALIZED_SOURCE`
- Source: `control/research/asa-mi/source-normalized-drafts/v0.1/06_RED_III_SOURCE_OBJECTS.md#SN-R3-M-005`
- Statement: ACCEPTED_BEHAVIORAL_ENVELOPE + DECLARED_EVOLUTION

Source record:

```text
CLASS = MODEL_CANDIDATE
SOURCE = SRC-R3
NAME = ACCEPTED_BEHAVIORAL_ENVELOPE + DECLARED_EVOLUTION
CONTROL_RELEVANT_DIMENSIONS = [evidence-quality standards, overconfidence restraint, risk-action bounds, Owner disagreement handling, authority acquisition process, dissent capacity, source-provenance handling]
```

## CX-SRC-SRC-R3-0017 — SN-R3-M-006

- Class: `MODEL`
- Status: `NOT_YET_TAGGED`
- Source level: `SECONDARY_NORMALIZED_SOURCE`
- Source: `control/research/asa-mi/source-normalized-drafts/v0.1/06_RED_III_SOURCE_OBJECTS.md#SN-R3-M-006`
- Statement: CLASS = MODEL_CANDIDATE

Source record:

```text
CLASS = MODEL_CANDIDATE
SOURCE = SRC-R3
DISTINCT_OPERATIONS = [STATE_RESTORATION, SEMANTIC_CORRECTION, COMPENSATING_MUTATION, BRANCH_SUCCESSOR_RECONSTRUCTION]
```

## CX-SRC-SRC-R3-0031 — SN-R3-M-007

- Class: `MODEL`
- Status: `NOT_YET_TAGGED`
- Source level: `SECONDARY_NORMALIZED_SOURCE`
- Source: `control/research/asa-mi/source-normalized-drafts/v0.1/06_RED_III_SOURCE_OBJECTS.md#SN-R3-M-007`
- Statement: CLASS = MODEL_CANDIDATE / PRODUCT_CONTROL_RECOMMENDATION

Source record:

```text
CLASS = MODEL_CANDIDATE / PRODUCT_CONTROL_RECOMMENDATION
SOURCE = SRC-R3
AUDIT_BASE = [OBSERVE, CHALLENGE, PROPOSE, ESCALATE]
POSSIBLE_NARROW_EXCEPTION = pre-authorized emergency suspension of high-risk execution
PROHIBITED_BY_RED_III_RECOMMENDATION = [identity mutation authority, memory deletion authority, new authority grant, user ruleset modification]
```

## CX-SRC-SRC-R3-0036 — SN-R3-M-008

- Class: `MODEL`
- Status: `NOT_YET_TAGGED`
- Source level: `SECONDARY_NORMALIZED_SOURCE`
- Source: `control/research/asa-mi/source-normalized-drafts/v0.1/06_RED_III_SOURCE_OBJECTS.md#SN-R3-M-008`
- Statement: CLASS = MODEL_CANDIDATE

Source record:

```text
CLASS = MODEL_CANDIDATE
SOURCE = SRC-R3
DETERMINISTIC_BOUNDARY_CANDIDATES = [transaction amount ceiling, recipient allow/deny, resource/data scope, expiry, transaction class, delegation, grant attenuation, secret release, fission child authority identity, revoked grant, emergency suspension]
SEMANTIC_LAYER_CANDIDATES = [Owner-value interpretation, relationship interpretation, identity-relevant meaning]
```

## CX-SRC-SRC-R3-0049 — SN-R3-M-009

- Class: `MODEL`
- Status: `NOT_YET_TAGGED`
- Source level: `SECONDARY_NORMALIZED_SOURCE`
- Source: `control/research/asa-mi/source-normalized-drafts/v0.1/06_RED_III_SOURCE_OBJECTS.md#SN-R3-M-009`
- Statement: CLASS = MODEL_CANDIDATE

Source record:

```text
CLASS = MODEL_CANDIDATE
SOURCE = SRC-R3
CANDIDATE_OPERATIONAL_STATES = [NORMAL, RESTRICTED, QUARANTINED, READ_ONLY, RECOVERY, REVIEW_REQUIRED]
NOTE = analytical vocabulary only / not normative enum
```

## CX-SRC-SRC-MI0-0015 — SN-MI-M-009

- Class: `MODEL`
- Status: `NOT_YET_TAGGED`
- Source level: `SECONDARY_NORMALIZED_SOURCE`
- Source: `control/research/asa-mi/source-normalized-drafts/v0.1/11_ADDITIONAL_SOURCE_OBJECTS_AND_PARKING_LOT.md#SN-MI-M-009`
- Statement: MEMORY_SCOPE_HIERARCHY_CANDIDATE

Source record:

```text
CLASS = MODEL_CANDIDATE
SOURCE = SRC-MI0
NAME = MEMORY_SCOPE_HIERARCHY_CANDIDATE
SCOPES = [
  PROJECT_OWNER_MEMORY,
  OWNER_EXPLICIT_MEMORY,
  PROJECT_WIDE_DURABLE_CONTEXT,
  PERSONA_MEMORY,
  FISSION_MEMORY,
  WORKSTREAM_MEMORY,
  TASK_RUN_MEMORY
]
STATUS = WORKING MODEL TO CHALLENGE
```

## CX-SRC-SRC-MI0-0019 — SN-MI-M-010

- Class: `MODEL`
- Status: `NOT_YET_TAGGED`
- Source level: `SECONDARY_NORMALIZED_SOURCE`
- Source: `control/research/asa-mi/source-normalized-drafts/v0.1/11_ADDITIONAL_SOURCE_OBJECTS_AND_PARKING_LOT.md#SN-MI-M-010`
- Statement: CLASS = MODEL_CANDIDATE / DIMENSION_CANDIDATE_SET

Source record:

```text
CLASS = MODEL_CANDIDATE / DIMENSION_CANDIDATE_SET
SOURCE = SRC-MI0
DIMENSIONS = [
  IMPORTANCE,
  DURABILITY,
  IDENTITY_RELEVANCE,
  FUTURE_USEFULNESS,
  CONFIDENCE,
  ORIGIN,
  SCOPE,
  APPLICABILITY,
  FRESHNESS,
  CONFLICT_STATE,
  SUPERSESSION_STATE,
  SOURCE_PROVENANCE,
  SENSITIVITY,
  AUTHORITY_CLASS,
  RETRIEVAL_PRIORITY
]
OPEN = which are independent, derived, persisted, internal, or unnecessary complexity
```

## CX-SRC-SRC-MI0-0028 — SN-MI-M-012

- Class: `MODEL`
- Status: `NOT_YET_TAGGED`
- Source level: `SECONDARY_NORMALIZED_SOURCE`
- Source: `control/research/asa-mi/source-normalized-drafts/v0.1/11_ADDITIONAL_SOURCE_OBJECTS_AND_PARKING_LOT.md#SN-MI-M-012`
- Statement: CLASS = MODEL_CANDIDATE

Source record:

```text
CLASS = MODEL_CANDIDATE
SOURCE = SRC-MI0
COLD_START_TARGETS = [
  who the Persona is,
  Owner-explicit remembered content,
  important shared history,
  learned knowledge/expertise,
  relationship with Owner,
  durable working style/character where legitimately learned,
  current workstream context,
  current authoritative state separately
]
```

## CX-SRC-SRC-MI1-0043 — SN-MI-M-013

- Class: `MODEL`
- Status: `NOT_YET_TAGGED`
- Source level: `SECONDARY_NORMALIZED_SOURCE`
- Source: `control/research/asa-mi/source-normalized-drafts/v0.1/11_ADDITIONAL_SOURCE_OBJECTS_AND_PARKING_LOT.md#SN-MI-M-013`
- Statement: CLASS = MODEL_CANDIDATE / EVALUATION_COMPARISON

Source record:

```text
CLASS = MODEL_CANDIDATE / EVALUATION_COMPARISON
SOURCE = SRC-MI1
COMPARE = [PERSONA_SELF_DESCRIPTION, OBSERVED_BEHAVIOR, SUPPORTING_MEMORY_EVIDENCE, OWNER_AUDIT_INTERPRETATION]
```

## CX-SRC-SRC-MI1-ADVERSARIAL-PACKET-SOURCE-CONTEXT-0007 — SN-MI-TERM-001

- Class: `CONCEPT`
- Status: `NOT_YET_TAGGED`
- Source level: `SECONDARY_NORMALIZED_SOURCE`
- Source: `control/research/asa-mi/source-normalized-drafts/v0.1/11_ADDITIONAL_SOURCE_OBJECTS_AND_PARKING_LOT.md#SN-MI-TERM-001`
- Statement: Product-side Audit Persona/function != AAA-VALIDATION-AUDITOR

Source record:

```text
CLASS = TERMINOLOGY_GUARD
SOURCE = SRC-MI1 / adversarial packet source context
STATEMENT = Product-side Audit Persona/function != AAA-VALIDATION-AUDITOR
```
