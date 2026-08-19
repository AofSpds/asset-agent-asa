# AAA-ASA-MI Brainstorm Hypothesis & Principle Registry v0.1

## Artifact state

```text
ARTIFACT_ID = AAA-ASA-MI-BRAINSTORM-HYPOTHESIS-PRINCIPLE-REGISTRY-v0.1
PROJECT = AAA
PRODUCT = ASSET AGENT ASA
WORKSTREAM = ASA-MI / Memory & Identity / Growing & Changing Persona
SCOPE = ASA-MI_ONLY
ARTIFACT_CLASS = WORKING_RESEARCH_REGISTRY
AUTHORING_STATE = WORKING_BRAINSTORM_CAPTURE
NORMATIVE_AUTHORITY = NONE
GLOBAL_APPLICABILITY = FALSE
FROZEN = FALSE
PAIRED_VALIDATION = NOT_PERFORMED
INDEPENDENT_VALIDATION = NOT_PERFORMED
OWNER_FINAL_ACCEPTANCE = FALSE
PRODUCTION_AUTHORIZED = FALSE
RECORDED_BY = AAA-ASA-MEMORY-IDENTITY-PROCESS-FACILITATOR-FISSION (ASA-MI-PF)
RECORDED_TIME = 2026-08-20T05:09:00+09:00
SOURCE_DISCUSSION_WINDOW = 2026-08-20T03:53:00+09:00..2026-08-20T05:09:00+09:00
```

This artifact captures ASA-MI brainstorming that occurred after the existing worldview and planning-guidance artifacts, including ideas that are **not** currently selected as the leading hypothesis.

It exists to preserve research state and candidate space. It is not a Requirement, Design Contract, Shared Contract, validation receipt, or production authority.

Historical references:

```text
FOUNDATIONAL_WORLDVIEW_REF = control/research/asa-mi/foundational-worldview/v0.1/AAA_ASA_MI_FOUNDATIONAL_WORLDVIEW_v0.1.md
PLANNING_GUIDANCE_REF = control/research/asa-mi/planning-guidance/v0.1/AAA_ASA_MI_PLANNING_PRINCIPLES_AND_RECOMMENDATIONS_v0.1.md
```

---

# 1. Record classes used in this registry

```text
RECORD_CLASS ∈ {
  DESIGN_INTENT,
  PRINCIPLE_CANDIDATE,
  RESEARCH_METHOD_CANDIDATE,
  PHILOSOPHICAL_PRIOR,
  CS_PRIOR_MAPPING,
  WORKING_HYPOTHESIS,
  CANDIDATE_HYPOTHESIS,
  MODEL_CANDIDATE,
  OPEN_QUESTION,
  EXPERIMENT_IDEA,
  CORRECTION,
  UNCLASSIFIED
}
```

Class boundaries are themselves revisable. `FAILURE_TO_CLASSIFY != INVALID_CONTENT`.

---

# 2. Design intent / philosophical grounding

## DI-001 — Persona is an abstraction of a person or some portion of a person

```text
OBJECT_ID = ASA-MI-DI-001
CLASS = DESIGN_INTENT
STATEMENT = "Digital Persona는 현실의 사람 전체 또는 일부 현상을 계산 가능한 형태로 추상화한 객체를 지향한다."
STATE = CURRENT_BRAINSTORM_BASIS
```

This does not assert `HUMAN = COMPUTER_OBJECT`. It asserts that the project is building a computational representation of selected human/persona phenomena.

## DI-002 — Reality-proximity is a design objective

```text
OBJECT_ID = ASA-MI-DI-002
CLASS = DESIGN_INTENT
STATEMENT = "철학·심리·현실 인간경험을 가설에 매핑하는 목적은 Persona abstraction이 현실의 사람에게서 너무 멀어지지 않게 하기 위함이다."
SHORT_FORM = REALITY_PROXIMITY_IS_DESIGN_OBJECTIVE
STATE = CURRENT_BRAINSTORM_BASIS
```

## DI-003 — Human plausibility matters, but is not sufficient

```text
OBJECT_ID = ASA-MI-DI-003
CLASS = DESIGN_INTENT
STATEMENT = "현실의 사람이 상호작용 결과를 현실감 있게 받아들일 수 있어야 한다."
NON_EQUIVALENCE = PERCEIVED_REALISM != REALITY_FIDELITY
STATE = CURRENT_BRAINSTORM_BASIS
```

Human-perceived realism is therefore a relevant evaluation dimension, not a replacement for structural or behavioral evidence.

## DI-004 — Reality is to be made more explicit and measurable where practical

```text
OBJECT_ID = ASA-MI-DI-004
CLASS = DESIGN_INTENT
STATEMENT = "ASA-MI는 현실을 상태, 값, 관계, 함수, 참조, 시간, 변화율, 변화조건 등으로 가능한 한 명시적으로 수치화/정규화하려 한다."
DOES_NOT_ASSERT = ALL_REALITY_MUST_BE_REDUCED_TO_SCALAR_NUMBERS
STATE = CURRENT_BRAINSTORM_BASIS
```

`UNKNOWN != 0`, `UNOBSERVED != ABSENT`, and unsupported numerical precision should not be invented.

---

# 3. Research / modeling principles

## P-001 — Reuse mature computer-science abstractions before inventing new primitives

```text
OBJECT_ID = ASA-MI-P-001
CLASS = RESEARCH_METHOD_CANDIDATE
FORM = USE_CS_PRIOR -> MAP_TO_PERSONA -> IDENTIFY_PERSONA_DELTA -> NEW_ABSTRACTION_ONLY_IF_NEEDED
STATE = CURRENT_RECOMMENDED_METHOD
```

Computer science has already accumulated abstractions such as object, instance, state, function, reference, relation, context, scope, lifecycle, event, binding, serialization, version, cache, permission, and transition.

ASA-MI should not redefine these without an observed explanatory failure.

## P-002 — Computer-science legacy is a prior, not reality

```text
OBJECT_ID = ASA-MI-P-002
CLASS = PRINCIPLE_CANDIDATE
CS_PRIOR != REALITY
IF CS_PRIOR_CONFLICTS_WITH_OBSERVED_REALITY:
    MODEL_REVISION_REQUIRED
STATE = CURRENT_BRAINSTORM_BASIS
```

## P-003 — Philosophy is used as reality-grounding for abstraction selection

```text
OBJECT_ID = ASA-MI-P-003
CLASS = PHILOSOPHICAL_PRIOR
FORM = HUMAN_PHENOMENA -> PHILOSOPHICAL_PSYCHOLOGICAL_PRIOR -> CS_ABSTRACTION -> PERSONA_MODEL
STATE = CURRENT_BRAINSTORM_BASIS
```

Philosophy is not treated as Ground Truth. Competing philosophical interpretations may coexist as priors and can be revised.

## P-004 — Precision is not accuracy

```text
OBJECT_ID = ASA-MI-P-004
CLASS = PRINCIPLE_CANDIDATE
PRECISION != ACCURACY
REPRESENTATION != REALITY
SCHEMA != ONTOLOGICAL_TRUTH
STATE = CURRENT_BRAINSTORM_BASIS
```

## P-005 — No absolute constant is assumed as an intrinsic type

```text
OBJECT_ID = ASA-MI-P-005
CLASS = PRINCIPLE_CANDIDATE
STATEMENT = "상수는 존재론적 절대불변값이라기보다, 선언된 Boundary 안에서 같은 값을 반환하도록 취급되는 함수적 상태다."
SHORT_FORM = CONSTANT -> SCOPED_INVARIANT
STATE = CURRENT_BRAINSTORM_BASIS
```

The more useful characteristics are `BOUNDARY`, `CHANGE_RATE`, and `TRANSITION_CONDITION`.

## P-006 — Lifecycle applies to Persona-related objects and relations

```text
OBJECT_ID = ASA-MI-P-006
CLASS = PRINCIPLE_CANDIDATE
STATEMENT = "Persona, Memory Object, relation, function binding, derived state 등에는 lifecycle을 가정할 수 있으며 deletion도 유효한 transition이 될 수 있다."
STATE = CURRENT_BRAINSTORM_BASIS
```

This is distinct from the preservation policy of ASA-MI research-history artifacts.

## P-007 — Brainstorm statements should be recorded by semantic class, not forced into Hypothesis

```text
OBJECT_ID = ASA-MI-P-007
CLASS = PRINCIPLE_CANDIDATE
STATEMENT = "브레인스토밍의 발언을 모두 가설로 강제하지 않고 Design Intent, Principle, Prior, Model, Mapping, Open Question 등 의미에 따라 기록한다."
STATE = CURRENT_RECOMMENDED_METHOD
```

---

# 4. Core Persona / Memory model hypotheses

## H-001 — Persona may be an instantiated Memory/State object

```text
OBJECT_ID = ASA-MI-H-001
CLASS = WORKING_HYPOTHESIS
FORM = PERSONA_t ?= INSTANTIATE(MEMORY_STATE_t, ENVIRONMENT_t, RUNTIME_t)
RELATED_TO = ASA-MI-H-IDENTITY-MEMORY-v0.1
STATE = ACTIVE_WORKING_HYPOTHESIS
CONFIRMATION_STATE = UNCONFIRMED
```

This does not require process continuity.

## H-002 — Fundamental Memory representation may be functional

```text
OBJECT_ID = ASA-MI-H-002
CLASS = WORKING_HYPOTHESIS
FORM = M : Context -> Value
STATEMENT = "Memory는 고정된 값 그 자체보다, 조건/범위/환경/시점 등에 따라 값을 반환하는 함수 또는 매핑으로 표현할 수 있다."
STATE = CURRENT_STRONG_CANDIDATE
CONFIRMATION_STATE = UNCONFIRMED
```

## H-003 — Constant/variable may be derived behavior rather than intrinsic type

```text
OBJECT_ID = ASA-MI-H-003
CLASS = WORKING_HYPOTHESIS
FORM = SCOPED_INVARIANT(M,B) <=> FOR_ALL(c1,c2 IN B): M(c1)=M(c2)
STATE = CURRENT_STRONG_CANDIDATE
CONFIRMATION_STATE = UNCONFIRMED
```

`CONSTANT / VARIABLE = DERIVED_PROPERTY(M, Boundary)` is preferred over intrinsic immutable typing as a current model candidate.

## H-004 — Change rate and transition condition are primary characteristics

```text
OBJECT_ID = ASA-MI-H-004
CLASS = MODEL_CANDIDATE
FORM = MEMORY_DYNAMICS(M) ?= {BOUNDARY, CHANGE_RATE, TRANSITION_CONDITION}
STATE = CURRENT_STRONG_CANDIDATE
```

`CHANGE_RATE` may later be represented numerically, categorically, probabilistically, or by another model. Fake precision is not assumed.

## H-005 — Memory may include values, references, relations, function bindings, and mapped results

```text
OBJECT_ID = ASA-MI-H-005
CLASS = CANDIDATE_HYPOTHESIS
MEMORY_VALUE_TYPES_MAY_INCLUDE = [
  VALUE,
  OBJECT,
  REFERENCE,
  RELATION,
  FUNCTION,
  FUNCTION_BINDING,
  EXECUTION_RESULT,
  STATUS,
  EVENT,
  DERIVED_VIEW
]
STATE = ACTIVE_CANDIDATE
```

This candidate intentionally broadens Memory beyond an internal database of recalled episodes.

## H-006 — Storage location does not determine Memory identity

```text
OBJECT_ID = ASA-MI-H-006
CLASS = WORKING_HYPOTHESIS
FORM = STORAGE_LOCATION != MEMORY_IDENTITY
STATE = CURRENT_STRONG_CANDIDATE
```

A Memory relation may point to local storage, Git object, database row, external URL, cloud object, API resource, other Persona object, or another locator.

## H-007 — Accessible data is not automatically Memory

```text
OBJECT_ID = ASA-MI-H-007
CLASS = CANDIDATE_HYPOTHESIS
FORM = ACCESSIBLE(X) != MEMORIZED(X)
CANDIDATE_RULE = BOUND_REFERENCE(Persona,X) -> MEMORY_RELATION(Persona,X)
STATE = ACTIVE_CANDIDATE
```

This prevents the trivial interpretation `all reachable information = memory` unless evidence supports it.

## H-008 — External reference may itself be Memory

```text
OBJECT_ID = ASA-MI-H-008
CLASS = WORKING_HYPOTHESIS
EXAMPLE = Persona --REMEMBERS_BY_REFERENCE--> External_URL
STATE = CURRENT_STRONG_CANDIDATE
```

A reference Memory may preserve locator, observed time, digest, target identity, and/or snapshot reference depending on the required fidelity.

## H-009 — Function may be a Persona member and procedural-memory candidate

```text
OBJECT_ID = ASA-MI-H-009
CLASS = CANDIDATE_HYPOTHESIS
FORM = PROCEDURAL_MEMORY ?= EXECUTABLE_FUNCTION_OR_FUNCTIONAL_BINDING
STATE = ACTIVE_CANDIDATE
CONFIRMATION_STATE = UNCONFIRMED
```

Not every runtime function is Persona Memory. A distinction remains between base/runtime capability and Persona-acquired procedural state.

## H-010 — Environment-bound function state may be Memory

```text
OBJECT_ID = ASA-MI-H-010
CLASS = WORKING_HYPOTHESIS
FORM = f_E = BIND(f,E)
CANDIDATE = FUNCTION_BINDING_STATE_t subset_of PERSONA_STATUS_OR_MEMORY
STATE = CURRENT_STRONG_CANDIDATE
```

The same abstract function may map differently under different environments.

## H-011 — Function execution result may become Memory

```text
OBJECT_ID = ASA-MI-H-011
CLASS = CANDIDATE_HYPOTHESIS
FORM = y = f_E(x); PRESERVE_FOR_REUSE(y) -> MEMORY_CANDIDATE(y)
STATE = ACTIVE_CANDIDATE
```

## H-012 — Past environment-function mappings may remain reference Memory

```text
OBJECT_ID = ASA-MI-H-012
CLASS = CANDIDATE_HYPOTHESIS
FORM = CURRENT_BINDING = BIND(f,E_now); HISTORICAL_BINDING = REFERENCE(BIND(f,E_past))
STATE = ACTIVE_CANDIDATE
```

---

# 5. SELF / CURRENT / STATUS candidates

## H-SELF-001 — Explicit self-awareness need not be continuously materialized

```text
OBJECT_ID = ASA-MI-H-SELF-001
CLASS = WORKING_HYPOTHESIS
FORM = SELF_EXISTS != SELF_IS_EXPLICITLY_REPRESENTED
STATE = CURRENT_STRONG_CANDIDATE
```

A Persona need not continuously carry the proposition `I am I` in active cognition.

## H-SELF-002 — SELF may be a context-resolved receiver/reference

```text
OBJECT_ID = ASA-MI-H-SELF-002
CLASS = CANDIDATE_HYPOTHESIS
FORM = SELF(context) -> current Persona receiver/reference
STATE = ACTIVE_CANDIDATE
```

This is a mapping to established `self/this/receiver/reference` computer-science abstractions.

## H-SELF-003 — Self-model may be an optional derived view

```text
OBJECT_ID = ASA-MI-H-SELF-003
CLASS = CANDIDATE_HYPOTHESIS
FORM = SELF_MODEL = F(SELF(context), MEMORY, RELATIONS, LINEAGE, ENVIRONMENT)
STATE = ACTIVE_CANDIDATE
```

`SELF_REFERENCE_AVAILABLE != SELF_MODEL_ALWAYS_MATERIALIZED`.

## H-CURRENT-001 — CURRENT may be an evaluation operator

```text
OBJECT_ID = ASA-MI-H-CURRENT-001
CLASS = WORKING_HYPOTHESIS
FORM = CURRENT(M) = M(CURRENT_CONTEXT)
STATE = CURRENT_STRONG_CANDIDATE
```

Current-state existence and explicit current-awareness are distinct.

## H-CURRENTSELF-001 — CURRENT_SELF may be derived rather than persisted

```text
OBJECT_ID = ASA-MI-H-CURRENTSELF-001
CLASS = CANDIDATE_HYPOTHESIS
FORM = CURRENT_SELF = SELF(CURRENT_CONTEXT) OR VIEW(MEMORY,SELF,TIME,CONTEXT)
STATE = ACTIVE_CANDIDATE
```

## H-STATUS-001 — CURRENT_STATUS may be a dynamic/materialized view rather than canonical persistent state

```text
OBJECT_ID = ASA-MI-H-STATUS-001
CLASS = CANDIDATE_HYPOTHESIS
FORM = CURRENT_STATUS_t ?= VIEW(MEMORY, SELF, TIME, CONTEXT)
STATE = ACTIVE_CANDIDATE
```

Possible implementation forms remain open:

```text
CURRENT_STATUS_STORED
CURRENT_STATUS_DERIVED
CURRENT_STATUS_CACHE
HYBRID
```

## H-STATUS-002 — Persona Instance may not materialize all Persona Memory

```text
OBJECT_ID = ASA-MI-H-STATUS-002
CLASS = CANDIDATE_HYPOTHESIS
FORM = PERSONA_INSTANCE_t ?= {MEMORY_ACCESS, OPERATORS, ENVIRONMENT_BINDINGS, ACTIVE_CONTEXT_t}
STATE = ACTIVE_CANDIDATE
```

Lazy retrieval may be sufficient for large portions of Memory.

---

# 6. Context candidates and CS-prior mapping

## CS-CTX-001 — Context prior

```text
OBJECT_ID = ASA-MI-CS-CTX-001
CLASS = CS_PRIOR_MAPPING
CS_COMMON_ABSTRACTION = "relevant state/bindings/conditions needed to execute or evaluate an operation"
ASA_MI_FORM = M(Context) -> Value
STATE = PRIOR_ADOPTED_FOR_CURRENT_DISCUSSION
FINAL_TRUTH = FALSE
```

## H-CTX-001 — Context may include coordinates, bindings, state, and conditions

```text
OBJECT_ID = ASA-MI-H-CTX-001
CLASS = CANDIDATE_HYPOTHESIS
CONTEXT ?= {
  EVALUATION_COORDINATES,
  RELEVANT_STATE,
  BINDINGS,
  CONDITIONS
}
STATE = ACTIVE_CANDIDATE
```

## Competing Context structure candidates

```text
OBJECT_ID = ASA-MI-H-CTX-STRUCT-001
CLASS = CANDIDATE_HYPOTHESIS
CANDIDATES = [
  GLOBAL_CONTEXT,
  LOCAL_CONTEXT_PER_FUNCTION,
  HYBRID_GLOBAL_CONTEXT_WITH_PER_FUNCTION_PROJECTION
]
STATE = UNRESOLVED
```

---

# 7. Lifecycle / deletion / forgetting candidates

## H-LIFE-001 — Persona and Memory objects have lifecycle

```text
OBJECT_ID = ASA-MI-H-LIFE-001
CLASS = WORKING_HYPOTHESIS
EXAMPLE_TRANSITIONS = [CREATE, ACTIVE, UPDATE, DORMANT, REACTIVATE, SUPERSEDE, ARCHIVE, DELETE]
SINGLE_FIXED_PATH_REQUIRED = FALSE
STATE = CURRENT_STRONG_CANDIDATE
```

## H-DEL-001 — Deletion is a valid lifecycle operation

```text
OBJECT_ID = ASA-MI-H-DEL-001
CLASS = WORKING_HYPOTHESIS
STATE = CURRENT_STRONG_CANDIDATE
```

Deletion semantics remain decomposed into candidates such as:

```text
DELETE_RELATION
DELETE_PERSONA_MEMORY_OBJECT
DELETE_SOURCE_CONTENT
DELETE_DERIVED_INFLUENCE
```

## H-DEL-002 — Source deletion may not erase learned influence

```text
OBJECT_ID = ASA-MI-H-DEL-002
CLASS = CANDIDATE_HYPOTHESIS
FORM = DELETE_SOURCE != DELETE_INFLUENCE
STATE = ACTIVE_CANDIDATE
```

## H-FORGET-001 — Forgetting need not equal deletion

```text
OBJECT_ID = ASA-MI-H-FORGET-001
CLASS = CANDIDATE_HYPOTHESIS
FORGET_MAY_MAP_TO = [ACCESSIBILITY_DECAY, ACTIVATION_DECAY, RELATION_WEAKENING, RETRIEVAL_FAILURE, DELETE]
STATE = UNRESOLVED
```

---

# 8. Competing CURRENT STATUS candidate sets preserved without selection

```text
OBJECT_ID = ASA-MI-H-STATUS-COMPETING-001
CLASS = CANDIDATE_HYPOTHESIS
CANDIDATES = {
  MINIMAL_STATUS: "persist only the minimum bootstrap state; retrieve the rest",
  RICH_STATUS: "persist a materialized snapshot of current Persona-relevant state",
  DERIVED_STATUS: "derive current status from Memory/Context/Reconstruction",
  HYBRID_STATUS: "small persisted status + derived view + reference memory + optional cache"
}
STATE = UNRESOLVED
```

Previously brainstormed possible Status dimensions, retained as candidates rather than requirements:

```text
CANDIDATE_DIMENSIONS = [
  IDENTITY_OR_SELF_STATE,
  LINEAGE_STATE,
  RELATION_STATE,
  CURRENT_BELIEF_OR_HYPOTHESIS_STATE,
  DISPOSITION_STATE,
  STANDPOINT_STATE,
  HEURISTIC_STATE,
  PROCEDURAL_STATE,
  FUNCTION_BINDING_STATE,
  AUTHORITY_BINDING_REFERENCE,
  GOAL_STATE,
  OPEN_OR_UNRESOLVED_STATE,
  ENVIRONMENT_BINDING,
  OPERATIONAL_MODE,
  SELF_MODEL,
  MEMORY_MAP_OR_POINTERS
]
```

Each may later be classified as `PERSISTED_MEMBER`, `DERIVED_VIEW`, `RUNTIME_BINDING`, `TRANSIENT_RESULT`, `REFERENCE_ONLY`, or `NOT_REQUIRED`.

---

# 9. Reality / human mapping and evaluation candidates

## H-MAP-001 — Human phenomena should map onto mature CS abstractions where possible

```text
OBJECT_ID = ASA-MI-H-MAP-001
CLASS = RESEARCH_METHOD_CANDIDATE
FORM = HUMAN_PHENOMENON -> BEST_AVAILABLE_CS_ABSTRACTION + PERSONA_SPECIFIC_DELTA
STATE = CURRENT_RECOMMENDED_METHOD
```

## H-MAP-002 — Abstraction loss is a research object

```text
OBJECT_ID = ASA-MI-H-MAP-002
CLASS = CANDIDATE_HYPOTHESIS
STATEMENT = "사람의 현상을 CS abstraction으로 매핑할 때 무엇이 보존되고 무엇이 손실되는지를 별도로 측정/기록해야 한다."
CANDIDATE_PROXIES = [
  RECONSTRUCTION_ERROR,
  BEHAVIORAL_ERROR,
  RELATIONAL_ERROR,
  PORTABILITY_ERROR,
  AMBIGUITY,
  INFORMATION_LOSS_PROXY
]
STATE = ACTIVE_CANDIDATE
```

## H-EVAL-001 — Perceived realism and structural fidelity are distinct

```text
OBJECT_ID = ASA-MI-H-EVAL-001
CLASS = CANDIDATE_HYPOTHESIS
FORM = PERCEIVED_REALISM != REALITY_FIDELITY
STATE = CURRENT_STRONG_CANDIDATE
```

Candidate evaluation axes:

```text
STRUCTURAL_FIDELITY
BEHAVIORAL_FIDELITY
PHENOMENOLOGICAL_PLAUSIBILITY
COMPUTATIONAL_COHERENCE
```

These axes are not yet formal metrics.

---

# 10. Candidate research questions / hypothesis backlog

The following questions remain intentionally open. Where mature CS models already exist, the default next action is `CS_PRIOR_PENDING`, not zero-base reinvention.

## Priority A — likely CS-prior-heavy

```text
ASA-MI-OQ-CTX-001 = "What is the minimum/effective Context domain per Memory function?"           STATE=CS_PRIOR_PENDING
ASA-MI-OQ-VAL-001 = "How should UNKNOWN/UNDEFINED/NULL/ABSENT/DELETED/CONFLICT differ?"           STATE=CS_PRIOR_PENDING
ASA-MI-OQ-ID-001  = "What makes two Memory functions/objects the same object across versions?"   STATE=CS_PRIOR_PENDING
ASA-MI-OQ-REF-001 = "Reference identity vs target-content identity vs snapshot identity?"         STATE=CS_PRIOR_PENDING
ASA-MI-OQ-CACHE-001 = "When is a materialized current view merely cache vs canonical state?"      STATE=CS_PRIOR_PENDING
ASA-MI-OQ-VERS-001 = "Update-in-place vs successor/version identity semantics?"                   STATE=CS_PRIOR_PENDING
ASA-MI-OQ-SER-001 = "What state is required for serialization/reinstantiation bootstrap?"         STATE=CS_PRIOR_PENDING
```

## Priority B — CS prior plus Persona-specific delta

```text
ASA-MI-OQ-CHG-001 = "What exactly is CHANGE_RATE: value derivative, transition frequency, or hazard/probability?"   STATE=OPEN
ASA-MI-OQ-TR-001  = "How are TRANSITION_CONDITIONS represented and composed?"                                  STATE=OPEN
ASA-MI-OQ-CREATE-001 = "What transforms an observation/event into Persona Memory?"                            STATE=OPEN
ASA-MI-OQ-LEARN-001 = "REMEMBER(E) vs LEARN(E): same or different operators?"                                 STATE=OPEN
ASA-MI-OQ-FORGET-001 = "Forgetting as decay, inaccessibility, weak relation, reconstruction loss, or deletion?" STATE=OPEN
ASA-MI-OQ-DERIVE-001 = "When is a derived value stored, recomputed, or treated as a separate Memory object?"    STATE=OPEN
ASA-MI-OQ-RECURSE-001 = "Can Memory return functions that modify Memory or its transition rules?"               STATE=OPEN
ASA-MI-OQ-RECON-001 = "How much Persona behavior is determined by Memory vs reconstruction operator/model/runtime?" STATE=OPEN
ASA-MI-OQ-ENV-001 = "Actual environment vs remembered environment and re-binding under provider/runtime change?" STATE=OPEN
ASA-MI-OQ-AUTH-001 = "Who may read/write/alter/delete Memory or its transition conditions?"                     STATE=OPEN
```

## Priority C — likely ASA-MI-specific research

```text
ASA-MI-OQ-IDENTITY-001 = "Is Memory necessary, sufficient, primary, or merely one substrate for Persona identity?" STATE=OPEN
ASA-MI-OQ-CONTINUITY-001 = "Can state/lineage/reconstruction relations explain Persona continuity without process continuity?" STATE=OPEN
ASA-MI-OQ-SAMEPERSONA-001 = "What measurable criteria determine 'same Persona' after reinstantiation/model substitution?" STATE=OPEN
ASA-MI-OQ-FISSION-001 = "How should shared pre-fission history map to multiple successor Selves?" STATE=OPEN
ASA-MI-OQ-MERGE-001 = "What does merging divergent Persona Memory/identity states mean, if it is coherent at all?" STATE=OPEN
ASA-MI-OQ-COMMONLOCAL-001 = "What may be shared across Personas without causing convergence?" STATE=OPEN
ASA-MI-OQ-REALISM-001 = "Which human-perceived continuity/change signals correlate with structural fidelity rather than mere imitation?" STATE=OPEN
ASA-MI-OQ-POISON-001 = "How do slow, compositional Memory changes alter Persona identity without obvious single-step corruption?" STATE=OPEN
```

---

# 11. Candidate experiments preserved from brainstorming

```text
OBJECT_ID = ASA-MI-EXP-CANDIDATES-v0.1
CLASS = EXPERIMENT_IDEA
CANDIDATES = [
  "same Memory/state + different model/runtime -> compare instantiated Persona",
  "same model/runtime + different experience history -> compare Persona divergence",
  "remove persisted SELF_MODEL -> test self reconstruction",
  "change SELF/Memory root -> measure resulting self/continuity interpretation",
  "remove or alter selected Current Status dimensions -> reinstate and measure what is lost",
  "provider/environment swap -> re-bind functions and compare Persona behavior",
  "external reference target changes while locator remains constant -> test reference-memory semantics",
  "delete source memory while preserving derived heuristics -> test ghost influence",
  "shared evidence + separate interpretation vs shared interpretation -> measure Persona convergence",
  "reconstruct same research/persona state with multiple fresh AI instances -> measure reconstruction variance"
]
STATE = CANDIDATE_ONLY
```

---

# 12. Explicit corrections / withdrawn overgeneralizations

## COR-001 — `Deletion is unnatural` withdrawn

```text
OBJECT_ID = ASA-MI-COR-001
CLASS = CORRECTION
WITHDRAWN = "Persona Memory deletion is inherently unnatural"
CURRENT = "Deletion may be a normal lifecycle operation; research-history preservation policy must not be generalized to all Persona Memory."
STATE = RECORDED
```

## COR-002 — `CURRENT_STATUS must always be persisted` withdrawn as an assumption

```text
OBJECT_ID = ASA-MI-COR-002
CLASS = CORRECTION
WITHDRAWN = "Current Status must necessarily be a permanently stored canonical object"
CURRENT = "Stored, derived, cached, and hybrid Current Status remain competing candidates."
STATE = RECORDED
```

## COR-003 — `SELF_ANCHOR must be a persisted member` is not established

```text
OBJECT_ID = ASA-MI-COR-003
CLASS = CORRECTION
WITHDRAWN_AS_ASSUMPTION = "A persistent SELF_ANCHOR member is necessarily required"
CURRENT = "SELF may be a runtime/context receiver/reference; persisted anchor, derived self-model, and hybrid alternatives remain open."
STATE = RECORDED
```

## COR-004 — Memory boundary is not assumed finite/closed

```text
OBJECT_ID = ASA-MI-COR-004
CLASS = CORRECTION
WITHDRAWN_AS_ASSUMPTION = "Persona Memory must be bounded by local internal storage"
CURRENT = "External references and bound objects may participate in Memory; exact membership semantics remain open."
STATE = RECORDED
```

---

# 13. Research lineage rule

```text
DESIGN_INTENT
-> PRINCIPLE / PRIOR
-> HYPOTHESIS
-> MODEL / MAPPING
-> IMPLEMENTATION_CANDIDATE
-> EXPERIMENT / OBSERVATION
-> HYPOTHESIS_STATE_CHANGE
```

Not every record must traverse every stage.

The purpose is to preserve enough lineage that a successor can answer not only `what is the current model?` but also `why was this model considered?`, `which alternatives existed?`, and `what would cause it to change?`.

---

# 14. Registry semantics

```text
CURRENT_STRONG_CANDIDATE != CONFIRMED
ACTIVE_CANDIDATE != SELECTED
CURRENT_RECOMMENDED_METHOD != NORMATIVE_REQUIREMENT
CS_PRIOR_PENDING != ASA_MI_QUESTION_REQUIRING_ZERO_BASE_REINVENTION
SUPERSEDED != DELETED
RESEARCH_RECORD_PRESERVATION != PERSONA_MEMORY_IMMUTABILITY
```

Material future changes should be recorded as new registry objects or a successor registry version rather than silently rewriting historical thinking.
