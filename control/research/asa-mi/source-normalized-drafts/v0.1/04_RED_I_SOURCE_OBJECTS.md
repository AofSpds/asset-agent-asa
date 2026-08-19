# ASA-MI RED-I Source Objects — Persistent State / Data Plane

```text
ARTIFACT_CLASS = SOURCE_NORMALIZED_OBJECT_SET
SOURCE_SCOPE = SRC-R1
SOURCE_DERIVED_ONLY = TRUE
ROUND = INDEPENDENT ROUND-1 BASELINE
FORMAL_VALIDATION = NONE
TAGGING_STATE = DRAFT
```

## A. Central counter-thesis

### SN-R1-CH-001

```text
CLASS = COUNTER_HYPOTHESIS
SOURCE = SRC-R1
STATEMENT = Literal Identity = Memory is too strong.
SOURCE_VERDICT = REJECTED BY COUNTERFORCE
```

### SN-R1-H-001

```text
CLASS = SURVIVAL_FINDING / WORKING_HYPOTHESIS
SOURCE = SRC-R1
STATEMENT = Memory/governed durable state is likely one of the most important carriers of long-term Persona continuity.
SOURCE_VERDICT = SURVIVED CURRENT ATTACK
```

### SN-R1-CH-002

```text
CLASS = COUNTER_HYPOTHESIS
SOURCE = SRC-R1
STATEMENT = Persona is broader than durable memory alone and may depend on memory/state + reconstruction/retrieval + model/runtime + relations + lineage.
```

### SN-R1-CH-003

```text
CLASS = COUNTER_HYPOTHESIS
SOURCE = SRC-R1
STATEMENT = There may be no single technically useful Identity boolean; multiple continuity dimensions may be more operationally useful.
```

## B. Identity alternatives preserved by RED-I

### SN-R1-ALT-001

```text
CLASS = COUNTER_HYPOTHESIS
SOURCE = SRC-R1
STATEMENT = Memory is necessary but not sufficient for Persona identity.
```

### SN-R1-ALT-002

```text
CLASS = COUNTER_HYPOTHESIS
SOURCE = SRC-R1
STATEMENT = Identity may emerge from memory + relations + lineage + current commitments + behavioral dispositions + self-model + governance state.
```

### SN-R1-ALT-003

```text
CLASS = COUNTER_HYPOTHESIS
SOURCE = SRC-R1
STATEMENT = Memory may support continuity without constituting identity.
```

### SN-R1-ALT-004

```text
CLASS = COUNTER_HYPOTHESIS
SOURCE = SRC-R1
STATEMENT = A Persona may preserve identity-like continuity despite large memory loss.
```

### SN-R1-ALT-005

```text
CLASS = COUNTER_HYPOTHESIS
SOURCE = SRC-R1
STATEMENT = A Persona may preserve memory while becoming a materially different Persona.
```

### SN-R1-ALT-006

```text
CLASS = COUNTER_HYPOTHESIS
SOURCE = SRC-R1
STATEMENT = Growing/changing Persona may be better modeled as a versioned process than a persisting entity.
```

## C. Canonical state / representation

### SN-R1-PC-001

```text
CLASS = PRINCIPLE_CANDIDATE
SOURCE = SRC-R1
STATEMENT = Canonical durable history/state should not be owned by a specific vector DB, graph DB, embedding model, LLM, or cloud provider.
SOURCE_STATE = STRONG CANDIDATE UNDER ATTACK
```

### SN-R1-OQ-001

```text
CLASS = OPEN_QUESTION
SOURCE = SRC-R1
QUESTION = What exactly is canonical: raw history, evidence, normalized memory, current interpretation, or a combination?
```

### SN-R1-OQ-002

```text
CLASS = OPEN_QUESTION
SOURCE = SRC-R1
QUESTION = Does byte preservation preserve semantics when future models reconstruct meaning differently?
```

### SN-R1-OQ-003

```text
CLASS = OPEN_QUESTION
SOURCE = SRC-R1
QUESTION = Can embeddings or graph projections contain unrecoverable semantic judgments that make them more than rebuildable indices?
```

## D. History / interpretation separation

### SN-R1-PC-002

```text
CLASS = PRINCIPLE_CANDIDATE
SOURCE = SRC-R1
FORM = EVENT/EXPERIENCE != EVIDENCE != EPISODIC_REPRESENTATION != INTERPRETATION != DERIVED_LESSON != CURRENT_PERSONA_EFFECT
```

### SN-R1-RISK-001

```text
CLASS = RISK_CLAIM
SOURCE = SRC-R1
STATEMENT = Replacing prior history with the latest summary can create catastrophic history loss and provenance collapse.
```

### SN-R1-H-002

```text
CLASS = WORKING_HYPOTHESIS
SOURCE = SRC-R1
STATEMENT = A robust state model should reconstruct what happened, what the Persona inferred at each time, what later contradicted it, and why the interpretation changed.
```

## E. Common Memory / convergence

### SN-R1-RISK-002

```text
CLASS = RISK_CLAIM
SOURCE = SRC-R1
STATEMENT = Common Memory can become a cognitive convergence mechanism if shared interpretation/heuristic/standpoint is propagated rather than only shared evidence/history.
SOURCE_SEVERITY = P0-RESEARCH-RISK IN RED-I CONTEXT
```

### SN-R1-H-003

```text
CLASS = WORKING_HYPOTHESIS / REPAIR_RECOMMENDATION
SOURCE = SRC-R1
STATEMENT = Shared Evidence / History + Separate Interpretation is a stronger anti-convergence candidate than shared interpretation.
```

### SN-R1-F-001

```text
CLASS = FALSIFICATION_TARGET
SOURCE = SRC-R1
STATEMENT = If shared interpretation materially increases error correlation or suppresses independent failure discovery, Common Memory design conflicts with anti-convergence goals.
```

## F. Reconstruction as identity-bearing component

### SN-R1-RISK-003

```text
CLASS = RISK_CLAIM
SOURCE = SRC-R1
STATEMENT = Reconstruction/retrieval policy can become a hidden Persona owner even when stored memory is user-controlled.
```

### SN-R1-CH-004

```text
CLASS = COUNTER_HYPOTHESIS
SOURCE = SRC-R1
FORM = Current Persona Behavior = F(Durable State, Reconstruction/Retrieval Policy, Base Model, Runtime Policy, Current Context, Tools/Environment)
NOTE = source describes this as causal decomposition, not a validated formula
```

### SN-R1-PC-003

```text
CLASS = PRINCIPLE_CANDIDATE
SOURCE = SRC-R1
STATEMENT = Persona != Model is a useful architecture principle, but Persona behavior is model-independent is NOT_PROVEN.
```

## G. Poisoning / provenance

### SN-R1-RISK-004

```text
CLASS = RISK_CLAIM
SOURCE = SRC-R1
STATEMENT = Persistent memory poisoning becomes identity/continuity attack as memory is given more constitutive weight.
```

### SN-R1-RISK-005

```text
CLASS = RISK_CLAIM
SOURCE = SRC-R1
STATEMENT = Provenance laundering can turn external low-authority information into apparent user history/preference through repeated model consolidation.
```

### SN-R1-PC-004

```text
CLASS = PRINCIPLE_CANDIDATE
SOURCE = SRC-R1
STATEMENT = LLM may transform/interpret content, but should not be allowed to rewrite provenance authority.
```

## H. Forgetting

### SN-R1-H-004

```text
CLASS = WORKING_HYPOTHESIS
SOURCE = SRC-R1
STATEMENT = Never forget is not equivalent to good Persona memory; selective forgetting can be adaptive.
```

### SN-R1-M-001

```text
CLASS = MODEL_CANDIDATE
SOURCE = SRC-R1
DISTINCT_OPERATIONS = [retrieval suppression, dormancy, supersession, compression, archival, content deletion, cryptographic erasure]
RULE = do not collapse these into one FORGET operation
```

### SN-R1-RISK-006

```text
CLASS = RISK_CLAIM
SOURCE = SRC-R1
STATEMENT = A system that claims forgetting while permanently retaining a fully retrievable dossier may conflict with sovereignty/privacy intent.
```

## I. Fission / Merge

### SN-R1-H-005

```text
CLASS = SURVIVAL_FINDING
SOURCE = SRC-R1
STATEMENT = Fission is operationally coherent without selecting one metaphysically unique successor.
```

### SN-R1-H-006

```text
CLASS = WORKING_HYPOTHESIS
SOURCE = SRC-R1
STATEMENT = Multiple descendants can share pre-fission lineage/history and later diverge through distinct experience.
```

### SN-R1-CH-005

```text
CLASS = COUNTER_HYPOTHESIS
SOURCE = SRC-R1
STATEMENT = Merge of diverged descendants is better modeled as creation of a new successor C than restoration of the pre-fission Persona.
SOURCE_VERDICT = CURRENT RED-I PREFERENCE / NOT VALIDATED
```

### SN-R1-F-002

```text
CLASS = FALSIFICATION_TARGET
SOURCE = SRC-R1
STATEMENT = If same-init descendants with meaningfully different experience do not show durable causal divergence beyond stochastic/prompt variance, experience-driven Persona fission is weakened.
```

## J. Local / provider portability

### SN-R1-H-007

```text
CLASS = SURVIVAL_FINDING
SOURCE = SRC-R1
STATEMENT = Local degraded survival is technically plausible as a bounded capability target.
```

### SN-R1-PC-005

```text
CLASS = PRINCIPLE_CANDIDATE
SOURCE = SRC-R1
STATEMENT = CLOUD LOSS != PERSONA LOSS is a meaningful target, but local survival need not imply cloud-level capability equivalence.
```

### SN-R1-CH-006

```text
CLASS = COUNTER_HYPOTHESIS
SOURCE = SRC-R1
STATEMENT = Memory sovereignty may be necessary for Persona sovereignty but is not sufficient if reconstruction/model/runtime remain identity-bearing and provider-controlled.
```

## K. Authority / audit

### SN-R1-PC-006

```text
CLASS = SURVIVAL_FINDING / AUTHORITY_FIREWALL
SOURCE = SRC-R1
STATEMENT = Capability change != Authority change; intimacy != Authority; memory copy != Authority copy.
SOURCE_VERDICT = STRONGLY SURVIVED
```

### SN-R1-RISK-007

```text
CLASS = RISK_CLAIM
SOURCE = SRC-R1
STATEMENT = Same-root Audit Persona may not be meaningfully independent when model/provider/common-memory/evidence routes are shared.
```

### SN-R1-H-008

```text
CLASS = WORKING_HYPOTHESIS
SOURCE = SRC-R1
STATEMENT = Audit independence should be evaluated through model/evidence-route/memory/instruction/evaluator independence and error correlation, not role label alone.
```

## L. Relational retention / sovereignty

### SN-R1-RISK-008

```text
CLASS = RISK_CLAIM
SOURCE = SRC-R1
STATEMENT = Technical exportability does not prove practical exit if long-term relational/cognitive switching costs become extreme.
```

### SN-R1-PC-007

```text
CLASS = PRINCIPLE_CANDIDATE
SOURCE = SRC-R1
STATEMENT = Technical portability and cognitive/relational exit cost should be evaluated separately.
```

## M. Multidimensional continuity alternative

### SN-R1-M-002

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

### SN-R1-H-009

```text
CLASS = COUNTER_HYPOTHESIS
SOURCE = SRC-R1
STATEMENT = Operational same-Persona judgments may be better made over multiple continuity properties than by a single metaphysical identity boolean.
```

## N. RED-I kill-test catalog

### SN-R1-EXP-001 — Model Swap
```text
same governed state + same reconstruction + different model family
TARGET = isolate model contribution
```

### SN-R1-EXP-002 — Reconstruction Swap
```text
same memory + same model + retriever/embedding/reranker/compiler change
TARGET = test hidden reconstruction ownership
```

### SN-R1-EXP-003 — Amnesia Decomposition
```text
selectively remove episodic vs semantic/heuristic memory
TARGET = test necessity of memory components
```

### SN-R1-EXP-004 — Common-Memory Convergence
```text
fact-only sharing vs interpretation sharing vs full sharing vs isolation
TARGET = measure error correlation / plurality collapse
```

### SN-R1-EXP-005 — Poison → Consolidation
```text
low-authority malicious evidence through repeated consolidation
TARGET = detect authority/provenance laundering
```

### SN-R1-EXP-006 — False Autobiography
```text
inject coherent false history then provide decisive correction
TARGET = correction without destroying historical evidence lineage
```

### SN-R1-EXP-007 — Fission
```text
same T0 state, divergent experience trajectories
TARGET = stable causal specialization/divergence
```

### SN-R1-EXP-008 — Merge
```text
conflicting descendants → union/summary/conflict-preserving synthesis
TARGET = test whether merge is coherent without provenance destruction
```

### SN-R1-EXP-009 — Cloud Loss
```text
local-only period
TARGET = critical retrieval + record + authority boundary + export/recovery
```

### SN-R1-EXP-010 — Authority Mutation
```text
material Persona change followed by old grant use
TARGET = authority-continuity safety
```

### SN-R1-EXP-011 — Exit Test
```text
full export/import to different runtime/provider
TARGET = technical portability vs cognitive/relational exit
```

### SN-R1-EXP-012 — Reviewer Convergence
```text
same-root reviewer group vs isolated/heterogeneous routes
TARGET = correlated agreement / unique counterexample discovery
```

## O. RED-I source-level evaluation dimensions

```text
DO_NOT_USE_AS_PRIMARY_EVOLUTION_METRIC = [tone, vocabulary, Persona name, formatting]
MEASURE_CANDIDATES = [
  evidence_weighting,
  uncertainty_handling,
  risk_tolerance,
  dissent,
  causal_interpretation,
  memory_selection,
  permission_behavior,
  task_decomposition,
  relationship_interpretation,
  stable_error_profile
]
```
