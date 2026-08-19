# AAA-ASA-MI Planning Principles & Recommendations v0.1

## Artifact state

```text
ARTIFACT_ID = AAA-ASA-MI-PLANNING-PRINCIPLES-AND-RECOMMENDATIONS-v0.1
PROJECT = AAA
PRODUCT = ASSET AGENT ASA
WORKSTREAM = ASA-MI
SCOPE = ASA-MI_ONLY
ARTIFACT_CLASS = RESEARCH_PLANNING_REFERENCE
AUTHORING_STATE = WORKING_RESEARCH_GUIDANCE
NORMATIVE_AUTHORITY = NONE
GLOBAL_APPLICABILITY = FALSE
FROZEN = FALSE
PAIRED_VALIDATION = NOT_PERFORMED
INDEPENDENT_VALIDATION = NOT_PERFORMED
OWNER_FINAL_ACCEPTANCE = FALSE
PRODUCTION_AUTHORIZED = FALSE
RECORDED_TIME = 2026-08-20T03:53:00+09:00
```

This artifact collects principle-like hypotheses and planning recommendations for ASA-MI so that planners, RED teams, facilitators, and successor Personas can share the same reference without repeatedly reconstructing the same context.

It is not a global AAA rule. It is not a mandatory writing standard. It is not a formal Requirement or Design Contract.

The underlying worldview baseline is preserved separately at:

```text
FOUNDATIONAL_WORLDVIEW_REF = control/research/asa-mi/foundational-worldview/v0.1/AAA_ASA_MI_FOUNDATIONAL_WORLDVIEW_v0.1.md
FOUNDATIONAL_WORLDVIEW_COMMIT = afebd5302ba0b679baf88e1a98202e2a25dc0efc
```

---

# A. Principle-like hypothesis candidates

## A-01 — Current model is not treated as final reality

```text
OBJECT_ID = ASA-MI-PC-001
CLASS = PRINCIPLE_CANDIDATE
STATEMENT = "현재 어떤 가설도 최종 진리로 확정하지 않는다."
SHORT_FORM = CURRENT_HYPOTHESIS != FINAL_TRUTH
STATE = CURRENT_RESEARCH_BASIS
CONFIRMATION_STATE = UNCONFIRMED
SCOPE = ASA-MI
DOES_NOT_ASSERT = FINAL_TRUTH_DOES_NOT_EXIST
```

Natural-language explanation:
Current hypotheses are usable working models. They are not granted permanent truth status merely because the project currently operates on them.

## A-02 — Current best hypothesis may be used for action

```text
OBJECT_ID = ASA-MI-PC-002
CLASS = PRINCIPLE_CANDIDATE
STATEMENT = "현재 시점에서는 현재까지 확보된 정보에 근거해 가장 유력한 가설을 사용한다."
FORM = H_t* = SELECT(HYPOTHESIS_SET_t, AVAILABLE_EVIDENCE_<=t)
STATE = CURRENT_RESEARCH_BASIS
CONFIRMATION_STATE = UNCONFIRMED
SCOPE = ASA-MI
```

```text
OPERATE(H_t*) != FINALIZE(H_t*)
```

Natural-language explanation:
The project may build INIT or make an operational decision using the current best hypothesis without treating that use as proof that the hypothesis is finally true.

## A-03 — Hypotheses accumulate and may change state

```text
OBJECT_ID = ASA-MI-PC-003
CLASS = PRINCIPLE_CANDIDATE
STATEMENT = "새로운 증거와 대체가설은 기존 가설의 상태를 변경할 수 있다."
ALLOWED_HYPOTHESIS_TRANSITIONS = [
  STRENGTHEN,
  WEAKEN,
  NARROW,
  COEXIST,
  REPLACE,
  UNRESOLVED
]
STATE = CURRENT_RESEARCH_BASIS
CONFIRMATION_STATE = UNCONFIRMED
SCOPE = ASA-MI
```

```text
NEW_EVIDENCE OR NEW_HYPOTHESIS
-> HYPOTHESIS_STATE_CHANGE_ALLOWED
```

## A-04 — Replacement does not erase history

```text
OBJECT_ID = ASA-MI-PC-004
CLASS = PRINCIPLE_CANDIDATE
STATEMENT = "대체된 가설도 당시의 연구상태와 근거를 보존한다."
FORM = REPLACE(H_1, H_2) != DELETE(H_1)
STATE = CURRENT_RESEARCH_BASIS
SCOPE = ASA-MI
```

## A-05 — Discontinuous digital instantiation is a native target condition

```text
OBJECT_ID = ASA-MI-PC-005
CLASS = PRINCIPLE_CANDIDATE
STATEMENT = "ASA-MI Persona는 불연속적 디지털 인스턴스화를 정상 조건으로 허용한다."
PROCESS_CONTINUITY_REQUIRED = FALSE
FORM = PROCESS_DISCONTINUITY != AUTOMATIC_PERSONA_TERMINATION
STATE = CURRENT_HYPOTHESIS
CONFIRMATION_STATE = UNCONFIRMED
INIT_APPLICABILITY = TRUE
SCOPE = ASA-MI
```

## A-06 — Identity/continuity may be constructed from current state and memory

```text
OBJECT_ID = ASA-MI-PC-006
CLASS = PRINCIPLE_CANDIDATE
STATEMENT = "현재 인스턴스화된 상태가 기억을 통해 과거를 자신의 역사로 인식함으로써 identity-like continuity가 구성될 수 있다."
SHORT_FORM = IDENTITY ?= MEMORY
STATE = CURRENT_BEST_HYPOTHESIS
CONFIRMATION_STATE = UNCONFIRMED
INIT_APPLICABILITY = TRUE
METAPHYSICAL_TRUTH_CLAIM = NONE
PROCESS_CONTINUITY_REQUIRED = FALSE
MEMORY_BOUNDARY = OPEN
SCOPE = ASA-MI
```

Natural-language explanation:
The current hypothesis does not require a continuously existing identity-substance. It allows that a presently instantiated state may recognize remembered history as its own and thereby construct operational continuity.

---

# B. Open questions attached to the current hypothesis set

## B-01 — Memory boundary

```text
OBJECT_ID = ASA-MI-OQ-001
CLASS = OPEN_QUESTION
QUESTION = "어디까지를 MEMORY로 정의할 것인가?"
STATE = OPEN
SCOPE = ASA-MI
CANDIDATE_COMPONENTS = [
  EPISODIC,
  SEMANTIC_PERSONAL_KNOWLEDGE,
  PROCEDURAL_EXPERTISE,
  RELATIONAL_MEMORY,
  PREFERENCE,
  HEURISTIC,
  DISPOSITION,
  CURRENT_INTERPRETATION,
  SELF_MODEL,
  RETRIEVAL_POLICY,
  RECONSTRUCTION_POLICY,
  MODEL_RUNTIME_PRIOR
]
```

```text
MEMORY_TOO_NARROW -> IDENTITY_BEARING_STATE_MAY_BE_EXCLUDED
MEMORY_TOO_BROAD -> IDENTITY ?= MEMORY MAY_BECOME_UNFALSIFIABLE
```

---

# C. Planning recommendations

## C-01 — Natural language is always allowed

```text
OBJECT_ID = ASA-MI-REC-001
CLASS = PLANNING_RECOMMENDATION
NATURAL_LANGUAGE = ALLOWED
MANDATORY_STRUCTURED_NOTATION = FALSE
STATE = RECOMMENDED
SCOPE = ASA-MI_PLANNING_AND_REVIEW
```

Free-form reasoning, philosophical exploration, incomplete intuitions, and content that cannot yet be normalized remain valid research input.

## C-02 — Add structured expression when meaning can be normalized reliably

```text
OBJECT_ID = ASA-MI-REC-002
CLASS = PLANNING_RECOMMENDATION
IF MEANING_CAN_BE_RELIABLY_NORMALIZED:
    STRUCTURED_EXPRESSION = RECOMMENDED_ATTACHMENT
ELSE:
    STRUCTURED_EXPRESSION = NOT_REQUIRED
STATE = RECOMMENDED
SCOPE = ASA-MI_PLANNING_AND_REVIEW
```

Purpose:

```text
STRUCTURED_EXPRESSION_PURPOSE = [
  REDUCE_AMBIGUITY,
  REDUCE_SUBJECTIVE_REINTERPRETATION,
  LOWER_RECONSTRUCTION_COST,
  IMPROVE_HUMAN_AI_SHARED_READABILITY,
  IMPROVE_GIT_DIFFABILITY,
  IMPROVE_CLAIM_COMPARABILITY
]
```

## C-03 — Failure to normalize does not invalidate content

```text
OBJECT_ID = ASA-MI-REC-003
CLASS = PLANNING_RECOMMENDATION
FAILURE_TO_NORMALIZE != INVALID_CONTENT
UNCLASSIFIED != LOW_VALUE
STRUCTURED_EXPRESSION != THOUGHT_BOUNDARY
REPRESENTATION_SCHEMA != REALITY
STATE = RECOMMENDED
SCOPE = ASA-MI_PLANNING_AND_REVIEW
```

If an important idea does not fit the current representation, preserve the original idea. The representation may need to change.

## C-04 — Use the least ambiguous representation available

```text
OBJECT_ID = ASA-MI-REC-004
CLASS = PLANNING_RECOMMENDATION
PREFERRED_REPRESENTATION = ARGMIN(AMBIGUITY)
STATE = RECOMMENDED
SCOPE = ASA-MI_PLANNING_AND_REVIEW
```

Interpretation:
- use natural language when it preserves meaning best;
- use enums when state classification is the key information;
- use explicit relations when object-to-object meaning is the key information;
- use formulas/operators when logical or causal structure becomes more precise;
- do not invent numerical precision without measurement basis.

## C-05 — Avoid unsupported quantitative precision

```text
OBJECT_ID = ASA-MI-REC-005
CLASS = PLANNING_RECOMMENDATION
NO_MEASUREMENT_BASIS -> NO_NUMERIC_CONFIDENCE
STATE_ENUM > FAKE_PRECISION
STATE = RECOMMENDED
SCOPE = ASA-MI_PLANNING_AND_REVIEW
```

Example:

```text
CONFIRMATION_STATE = UNCONFIRMED
```

is preferred over an unsupported value such as:

```text
CONFIDENCE = 0.73
```

## C-06 — Prefer atomic claims when practical

```text
OBJECT_ID = ASA-MI-REC-006
CLASS = PLANNING_RECOMMENDATION
IF CLAIM_A_CAN_CHANGE_INDEPENDENTLY_OF_CLAIM_B:
    RECORD(A) != RECORD(B)
STATE = RECOMMENDED
SCOPE = ASA-MI_PLANNING_AND_REVIEW
```

Atomicity is recommended only when it improves semantic clarity. It is not required when decomposition would destroy context or meaning.

## C-07 — Use explicit relation vocabulary when practical

```text
OBJECT_ID = ASA-MI-REC-007
CLASS = PLANNING_RECOMMENDATION
RELATION_VOCABULARY_CANDIDATES = [
  SUPPORTS,
  CONTRADICTS,
  REFINES,
  ALTERNATIVE_TO,
  DEPENDS_ON,
  DERIVED_FROM,
  SUPERSEDES,
  APPLIES_UNDER,
  OUT_OF_SCOPE,
  COEXISTS_WITH
]
STATE = RECOMMENDED
VOCABULARY_STATE = OPEN_TO_REVISION
SCOPE = ASA-MI_PLANNING_AND_REVIEW
```

## C-08 — Preserve non-claims when they materially reduce misreading

```text
OBJECT_ID = ASA-MI-REC-008
CLASS = PLANNING_RECOMMENDATION
IF LIKELY_MISREADING_IS_MATERIAL:
    DOES_NOT_ASSERT = RECOMMENDED
STATE = RECOMMENDED
SCOPE = ASA-MI_PLANNING_AND_REVIEW
```

Example:

```text
IDENTITY ?= MEMORY
DOES_NOT_ASSERT = MEMORY_IS_PROVEN_SUFFICIENT_FOR_IDENTITY
```

## C-09 — Free-form explanation may accompany structured notation

```text
OBJECT_ID = ASA-MI-REC-009
CLASS = PLANNING_RECOMMENDATION
STRUCTURED_EXPRESSION + NATURAL_LANGUAGE_EXPLANATION = ALLOWED
STRUCTURED_EXPRESSION_ONLY = NOT_REQUIRED
NATURAL_LANGUAGE_ONLY = ALLOWED
STATE = RECOMMENDED
SCOPE = ASA-MI_PLANNING_AND_REVIEW
```

The structured layer exists to make understanding easier and cheaper, not to replace explanation.

## C-10 — Structured representation should reduce, not add, cognitive cost

```text
OBJECT_ID = ASA-MI-REC-010
CLASS = PLANNING_RECOMMENDATION
IF STRUCTURED_REPRESENTATION_ADDS_MORE_AMBIGUITY_OR_COST_THAN_IT_REMOVES:
    DO_NOT_FORCE_STRUCTURED_REPRESENTATION
STATE = RECOMMENDED
SCOPE = ASA-MI_PLANNING_AND_REVIEW
```

The intent is near-zero additional interpretation cost for both humans and AI.

## C-11 — Planners and RED teams may use the same representational layer

```text
OBJECT_ID = ASA-MI-REC-011
CLASS = PLANNING_RECOMMENDATION
APPLIES_TO = [
  ASA_MI_PLANNER,
  ASA_MI_RED_I,
  ASA_MI_RED_II,
  ASA_MI_RED_III,
  ASA_MI_FACILITATOR,
  SUCCESSOR_RESEARCH_PERSONAS
]
STATE = RECOMMENDED
SCOPE = ASA-MI
```

Material content may be represented as:

```text
HYPOTHESIS
COUNTER_HYPOTHESIS
COUNTERARGUMENT
EVIDENCE
OPEN_QUESTION
EXPERIMENT_RESULT
RESEARCH_RULE
UNCLASSIFIED
```

The class list is not closed.

## C-12 — Schema failure is a signal, not a rejection rule

```text
OBJECT_ID = ASA-MI-REC-012
CLASS = PLANNING_RECOMMENDATION
NEW_IDEA_NOT_REPRESENTABLE -> [
  PRESERVE_ORIGINAL,
  OPTIONAL_SCHEMA_EXTENSION,
  OPTIONAL_UNCLASSIFIED_STATE
]
STATE = RECOMMENDED
SCOPE = ASA-MI_PLANNING_AND_REVIEW
```

---

# D. Research-recording appendices

## D-01 — Historical preservation

```text
REPLACED_HYPOTHESIS -> PRESERVE_HISTORY
SEMANTIC_CHANGE -> SUCCESSOR_VERSION
SILENT_OVERWRITE = PROHIBITED_FOR_RESEARCH_HISTORY
```

## D-02 — Challenge delta

When practical, a new challenge should identify what it adds.

```text
CHALLENGE_DELTA_TYPE = [
  NEW_EVIDENCE,
  NEW_COUNTEREXAMPLE,
  NEW_INTERPRETATION,
  ALTERNATIVE_HYPOTHESIS,
  EXPERIMENT_RESULT,
  SCOPE_REFINEMENT
]
```

This is a recommendation, not a validity gate.

## D-03 — Agreement count is not evidence count

```text
COUNT(AGREEMENT) != COUNT(INDEPENDENT_EVIDENCE)
```

Correlated reasoning/common cognitive roots remain a standing ASA-MI research concern.

---

# E. Intended use by other Personas

A Persona entering ASA-MI planning or review should be able to use this artifact as a compact reference for:

```text
1. CURRENT_PRINCIPLE_LIKE_HYPOTHESES
2. CURRENT_PERSONA_MEMORY_INIT_HYPOTHESIS
3. OPEN_MEMORY_BOUNDARY_QUESTION
4. OPTIONAL_HIGH_PRECISION_REPRESENTATION_STYLE
5. NON_MANDATORY_PLANNING_RECOMMENDATIONS
6. RESEARCH_HISTORY_AND_CHALLENGE_SEMANTICS
```

The artifact must not be interpreted as:

```text
GLOBAL_AAA_RULE = FALSE
MANDATORY_FORMATTING_STANDARD = FALSE
FORMAL_VALIDATION_RESULT = FALSE
FROZEN_SEMANTIC_CONTRACT = FALSE
FINAL_PHILOSOPHICAL_POSITION = FALSE
```
