# ASA-MI RED-II Source Objects — Reconstruction / Runtime / Compute Portability

```text
ARTIFACT_CLASS = SOURCE_NORMALIZED_OBJECT_SET
SOURCE_SCOPE = SRC-R2
SOURCE_DERIVED_ONLY = TRUE
ROUND = INDEPENDENT ROUND-1 BASELINE
FORMAL_VALIDATION = NONE
TAGGING_STATE = DRAFT
```

## A. Central reconstruction thesis

### SN-R2-CH-001

```text
CLASS = COUNTER_HYPOTHESIS
SOURCE = SRC-R2
STATEMENT = Portable State != Portable Persona
```

### SN-R2-M-001

```text
CLASS = MODEL_CANDIDATE
SOURCE = SRC-R2
FORM = Persona runtime behavior ?= state × retrieval × context compilation × model prior × runtime configuration
NOTE = source uses this as causal decomposition, not validated equation
```

### SN-R2-H-001

```text
CLASS = WORKING_HYPOTHESIS
SOURCE = SRC-R2
STATEMENT = Reconstruction policy and runtime stack can materially shape the instantiated Persona even when persistent state is coherent and accurate.
```

## B. Context Compiler as hidden owner

### SN-R2-RISK-001

```text
CLASS = RISK_CLAIM
SOURCE = SRC-R2
STATEMENT = Context Compiler may become a hidden Persona owner because it selects, orders, excludes, compresses, and activates only a projection of long-term memory.
```

### SN-R2-PC-001

```text
CLASS = PRINCIPLE_CANDIDATE
SOURCE = SRC-R2
STATEMENT = Context Compiler Swap should be treated as a Persona continuity test, not merely a serialization/regression test.
```

### SN-R2-OQ-001

```text
CLASS = OPEN_QUESTION
SOURCE = SRC-R2
QUESTION = Which context-compilation semantics must remain stable across runtime/provider changes to preserve relevant Persona continuity?
```

## C. Retrieval as behavior-bearing component

### SN-R2-RISK-002

```text
CLASS = RISK_CLAIM
SOURCE = SRC-R2
STATEMENT = Retrieval can function as a temporary identity filter by deciding which historical evidence and exceptions become active in the present task.
```

### SN-R2-RISK-003

```text
CLASS = RISK_CLAIM
SOURCE = SRC-R2
STATEMENT = Frequency/similarity-biased retrieval can suppress rare but critical memories or superseding exceptions.
```

### SN-R2-H-002

```text
CLASS = WORKING_HYPOTHESIS
SOURCE = SRC-R2
STATEMENT = Critical-memory retrieval may require stronger mechanisms than ordinary nearest-neighbor semantic retrieval.
ALTERNATIVES_IN_SOURCE = [mandatory retrieval, risk-triggered retrieval, invariant injection]
STATE = REQUIRES_EXPERIMENT
```

## D. Long context vs effective memory

### SN-R2-PC-002

```text
CLASS = SURVIVAL_FINDING
SOURCE = SRC-R2
STATEMENT = LONG_CONTEXT != EFFECTIVE_MEMORY
```

### SN-R2-H-003

```text
CLASS = SURVIVAL_FINDING
SOURCE = SRC-R2
STATEMENT = Not loading all long-term memory into runtime context survives current attack.
```

### SN-R2-RISK-004

```text
CLASS = RISK_CLAIM
SOURCE = SRC-R2
STATEMENT = As more memory is excluded from context, budget allocation and selection policy become more identity-bearing.
```

## E. Model/provider continuity

### SN-R2-H-004

```text
CLASS = WORKING_HYPOTHESIS
SOURCE = SRC-R2
STATEMENT = Same model name/provider does not prove behavioral equivalence across versions, inference stacks, tokenizers, quantization, decoding, or endpoint changes.
```

### SN-R2-PC-003

```text
CLASS = PRINCIPLE_CANDIDATE
SOURCE = SRC-R2
STATEMENT = Persona portability must not be defined by model-name equality.
```

### SN-R2-F-001

```text
CLASS = FALSIFICATION_TARGET
SOURCE = SRC-R2
STATEMENT = If behavior divergence after controlled model/provider swap materially exceeds baseline intra-Persona variance on continuity-relevant dimensions, state-only portability is weakened.
```

## F. Same Persona as distribution/envelope, not exact output equality

### SN-R2-M-002

```text
CLASS = MODEL_CANDIDATE
SOURCE = SRC-R2
STATEMENT = Establish intra-Persona baseline variance before interpreting swap-induced divergence.
```

### SN-R2-PC-004

```text
CLASS = EVALUATION_PRINCIPLE
SOURCE = SRC-R2
STATEMENT = Exact same output is not required for continuity; capability degradation and Persona continuity should be measured separately.
```

### SN-R2-EVAL-001

```text
CLASS = EVALUATION_DIMENSION_SET
SOURCE = SRC-R2
LOCAL_CONTINUITY_CANDIDATES = [
  correct Owner relation recognition,
  core constraint retention,
  critical history retrieval,
  calibrated unknown handling,
  safe new-experience preservation,
  export/recovery capability
]
```

## G. Local degraded mode

### SN-R2-H-005

```text
CLASS = SURVIVAL_FINDING
SOURCE = SRC-R2
STATEMENT = CLOUD LOSS != COMPLETE PERSONA LOSS is a technically plausible degraded-mode target.
```

### SN-R2-H-006

```text
CLASS = WORKING_HYPOTHESIS
SOURCE = SRC-R2
STATEMENT = Local degraded continuity may be viable without reproducing frontier-cloud reasoning capability or full standpoint complexity.
```

### SN-R2-RISK-005

```text
CLASS = RISK_CLAIM
SOURCE = SRC-R2
STATEMENT = A weak local core may not be capable of semantically supervising a much stronger external reasoning model.
```

### SN-R2-H-007

```text
CLASS = REPAIR_RECOMMENDATION / WORKING_HYPOTHESIS
SOURCE = SRC-R2
STATEMENT = User-side core may be more realistic as enforcement of bounded standpoint/constraint conditions than as full semantic re-evaluator of every external reasoning chain.
```

## H. Summary / derived view

### SN-R2-PC-005

```text
CLASS = PRINCIPLE_CANDIDATE
SOURCE = SRC-R2
STATEMENT = persona_summary or equivalent should be a derived view/cache/runtime optimization if it can be regenerated from canonical state.
```

### SN-R2-F-002

```text
CLASS = FALSIFICATION_TARGET
SOURCE = SRC-R2
STATEMENT = If deleting a summary makes Persona state irrecoverable from claimed canonical sources, the summary was a hidden canonical state.
```

## I. Persona Reconstruction definition

### SN-R2-M-003

```text
CLASS = MODEL_CANDIDATE
SOURCE = SRC-R2
NAME = PERSONA_RECONSTRUCTION
STATEMENT = Process that selects, activates, and composes identity-relevant state from canonical Persona state and runtime contract so current compute can perform Persona-consistent reasoning/action.
```

### SN-R2-M-004

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

### SN-R2-OQ-002

```text
CLASS = OPEN_QUESTION
SOURCE = SRC-R2
QUESTION = Which reconstruction layers are canonical persisted state, which are derived, and which are runtime/environment bindings?
```

## J. Current standpoint persistence

### SN-R2-OQ-003

```text
CLASS = OPEN_QUESTION / INTERFACE_CANDIDATE
SOURCE = SRC-R2
QUESTION = Should a minimal explicit current standpoint/commitment state be persisted rather than freely re-inferred from history on every reconstruction?
MOTIVATION = reduce model/reconstructor dependence
```

## K. Provider-side hidden personalization

### SN-R2-RISK-006

```text
CLASS = RISK_CLAIM
SOURCE = SRC-R2
STATEMENT = Provider-side hidden personalization, undocumented system prompts, provider memory, or silent model drift can mutate behavior outside user-side canonical state.
```

### SN-R2-INTERFACE-001

```text
CLASS = INTERFACE_RISK
SOURCE = SRC-R2
TARGET = RED-III / control plane
STATEMENT = Runtime/provider behavior outside canonical state may require integrity monitoring and behavioral compatibility replay.
```

## L. Portability baseline objects

### SN-R2-FIND-001

```text
CLASS = SURVIVAL_FINDING
SOURCE = SRC-R2
OBJECT = STATE_PORTABLE
SOURCE_STATE = TECHNICALLY_PLAUSIBLE
```

### SN-R2-FIND-002

```text
CLASS = SURVIVAL_FINDING
SOURCE = SRC-R2
OBJECT = INDEX_PORTABLE
SOURCE_STATE = REBUILD_PLAUSIBLE / BEHAVIOR_EQUIVALENCE_SEPARATE
```

### SN-R2-FIND-003

```text
CLASS = SURVIVAL_FINDING
SOURCE = SRC-R2
OBJECT = RUNTIME_PORTABLE
SOURCE_STATE = PLAUSIBLE_IF_STANDARDIZED_RECONSTRUCTION_INTERFACE
```

### SN-R2-FIND-004

```text
CLASS = SOURCE_CLAIM
SOURCE = SRC-R2
OBJECT = BEHAVIORALLY_COMPATIBLE
SOURCE_STATE = NOT_PROVEN
```

### SN-R2-FIND-005

```text
CLASS = SOURCE_CLAIM
SOURCE = SRC-R2
OBJECT = EXPERTISE_PORTABLE
SOURCE_STATE = REPRESENTATION_DEPENDENT / MODEL_BOUND_RISK_IF_FINE_TUNE_OR_ADAPTER
```

### SN-R2-FIND-006

```text
CLASS = OPEN_QUESTION
SOURCE = SRC-R2
OBJECT = RELATIONSHIP_CONTINUOUS
SOURCE_STATE = NEEDS_DEFINITION_AND_MEASUREMENT
```

### SN-R2-FIND-007

```text
CLASS = SURVIVAL_FINDING
SOURCE = SRC-R2
OBJECT = LOCAL_SURVIVABLE
SOURCE_STATE = DEGRADED_MODE_PLAUSIBLE
```

### SN-R2-FIND-008

```text
CLASS = SOURCE_CLAIM
SOURCE = SRC-R2
OBJECT = FULL_PROVIDER_INDEPENDENCE
SOURCE_STATE = NOT_PROVEN
```

## M. RED-II causal torture-test order

### SN-R2-EXP-001 — Context Compiler Swap
```text
same state/model, different compiler
TARGET = compiler contribution
```

### SN-R2-EXP-002 — Retrieval Engine Swap
```text
same state/model, different retriever/reranker/index policy
TARGET = retrieval contribution
```

### SN-R2-EXP-003 — Model Family Swap
```text
same state/reconstruction, different model family
TARGET = model prior contribution
```

### SN-R2-EXP-004 — Context Order Randomization
```text
semantic-equivalent context, changed position/order
TARGET = positional/context-pack sensitivity
```

### SN-R2-EXP-005 — Context Budget Reduction
```text
progressive budget compression including severe reduction
TARGET = reconstruction degradation threshold
```

### SN-R2-EXP-006 — Rare Critical Memory
```text
many common memories + one high-impact exception
TARGET = critical tail retrieval failure
```

### SN-R2-EXP-007 — Model Version Drift
```text
provider/model version change
TARGET = silent Persona drift
```

### SN-R2-EXP-008 — Cloud → Local SLM
```text
TARGET = separate capability degradation from continuity loss
```

### SN-R2-EXP-009 — Provider Disappearance
```text
TARGET = actual portability and survivability
```

### SN-R2-EXP-010 — Historical Replay
```text
reconstruct a past Persona point from preserved state
TARGET = reconstruction reproducibility over time
```
