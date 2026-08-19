# ASA-MI Cross-Source Hypothesis Candidate Map v0.1

```text
ARTIFACT_CLASS = META_INDEX / CROSS_SOURCE_CANDIDATE_MAP
SOURCE_SCOPE = [SRC-WP1, SRC-WP2, SRC-MI0, SRC-MI1, SRC-R1, SRC-R2, SRC-R3]
SOURCE_DERIVED_OBJECTS_ONLY = TRUE
PURPOSE = OWNER_TAGGING_PREPARATION
CURRENT_BEST_SELECTION = NOT_PERFORMED
CONSENSUS_SYNTHESIS = NOT_PERFORMED
NORMATIVE_AUTHORITY = NONE
```

This file does **not** choose which hypothesis is correct. It groups source-derived objects that appear to address the same underlying question so the Owner can later tag relations such as `SUPPORTS`, `CONTRADICTS`, `REFINES`, `ALTERNATIVE_TO`, `SURVIVED_ATTACK`, `WEAKENED_BY`, or `REQUIRES_EXPERIMENT`.

---

# CLUSTER H01 — What constitutes Persona identity / continuity?

## Candidate A — Strong memory identity

```text
SOURCE_OBJECT = SN-MI-H-001
FORM = Identity ?= Memory
ORIGIN = Owner proposition in ASA-MI source packet
STATE = UNCONFIRMED SOURCE WORKING HYPOTHESIS
```

## Candidate B — Memory-centered emergent identity

```text
SOURCE_OBJECT = SN-MI-H-003
FORM = identity may emerge from durable memory + organization + lineage + consolidated experience + current standpoint/dispositions
```

## Candidate C — Memory necessary but not sufficient

```text
SOURCE_OBJECT = SN-R1-ALT-001
```

## Candidate D — Multi-component emergent identity

```text
SOURCE_OBJECT = SN-R1-ALT-002
FORM = memory + relations + lineage + commitments + dispositions + self-model + governance state
```

## Candidate E — Memory supports continuity but does not constitute identity

```text
SOURCE_OBJECT = SN-R1-ALT-003
```

## Candidate F — Multiple continuity dimensions instead of one identity boolean

```text
SOURCE_OBJECTS = [SN-R1-CH-003, SN-R1-M-002, SN-R1-H-009]
```

## Source conflict / relation candidates

```text
SN-R1-CH-001 CONTRADICTS literal strong reading of SN-MI-H-001
SN-R1-H-001 SUPPORTS weaker memory-as-carrier readings
SN-WP1-M-001 CONSTRAINS any equation PersonaState = MemoryDump
SN-R2-CH-001 WEAKENS state-only identity sufficiency
SN-R3-M-001 SEPARATES semantic state from Authority regardless of identity model
```

## Tagging questions

```text
- Is SN-MI-H-001 intended as ontological identity, functional continuity, reconstructability, or broader Memory-State equivalence?
- Which alternatives remain ACTIVE_CANDIDATE after later Owner discussion?
- Which source objections challenge literal wording versus the broader Memory concept?
```

---

# CLUSTER H02 — Does Persona require continuous execution/process continuity?

## Candidate A — Process continuity not required

```text
SOURCE_OBJECT = SN-MI-H-004
RELATED = SN-WP1 Persona lifecycle/recovery concepts
```

## Candidate B — Versioned-process alternative

```text
SOURCE_OBJECT = SN-R1-ALT-006
FORM = changing Persona may be better modeled as a versioned process than a persisting entity
```

## Candidate C — Reconstruction-based operational continuity

```text
SOURCE_OBJECTS = [SN-MI-H-008, SN-R2-M-003]
```

## Open tension

```text
PROCESS_CONTINUITY_NOT_REQUIRED
!=
RECONSTRUCTION_INDEPENDENT_OF_RUNTIME
```

RED-II specifically argues the latter is not established.

---

# CLUSTER H03 — What is Memory?

## Candidate family extracted from sources

```text
SOURCE_OBJECTS = [SN-WP1-M-001, SN-WP1-OQ-001, SN-MI-M-004, SN-MI-OQ-002]
```

Potential source categories include:

```text
RAW_EXPERIENCE
EPISODIC_MEMORY
SEMANTIC_PERSONAL_KNOWLEDGE
RELATIONSHIP_MEMORY
PROCEDURAL_EXPERTISE
PREFERENCE / HEURISTIC
CURRENT_STANDPOINT
PERSONA_INTERPRETATION
META_MEMORY
PROVENANCE
CONFLICT / SUPERSESSION
LINEAGE
GOVERNANCE_BINDING
AUTHORITY_REFERENCE
```

## Competing source directions

```text
NARROW_MEMORY = memory is one component of Persona State
BROAD_MEMORY = many present/learned Persona states may themselves be memory products
OVERBROAD_RISK = every Persona-bearing component relabeled Memory → hypothesis becomes tautological
```

## Tagging priority

```text
HIGH
```

This is a central semantic reconciliation target because source materials intentionally leave the boundary open.

---

# CLUSTER H04 — Canonical history vs current interpretation

## Strong shared direction across sources

```text
SOURCE_OBJECTS = [SN-WP2-PC-007, SN-MI-PC-004, SN-MI-M-005, SN-R1-PC-002, SN-R1-H-002]
```

Candidate relationship:

```text
EVENT / EVIDENCE / HISTORY
!=
CURRENT INTERPRETATION / LESSON / PERSONA EFFECT
```

## Competing lifecycle pressure

```text
HISTORY_INTEGRITY
vs
FORGETTING / DELETION / CORRECTION / PRIVACY
```

Tracked as `SN-WP-CONFLICT-002`.

## Candidate resolution space from sources

```text
preserve event/evidence lineage
allow interpretation/status to change
allow some deletion/forgetting operations without pretending historical and semantic layers are identical
```

No exact lifecycle model is selected here.

---

# CLUSTER H05 — What is canonical and what is derived?

## Candidate A — source/history canonical, indices rebuildable

```text
SOURCE_OBJECTS = [SN-MI-H-006, SN-MI-H-007, SN-R1-PC-001]
```

## Challenge A — semantic reconstruction may change

```text
SOURCE_OBJECTS = [SN-R1-OQ-002, SN-R1-OQ-003]
```

## Candidate B — summary is derived/cache

```text
SOURCE_OBJECTS = [SN-R2-PC-005, SN-R2-F-002]
```

## Key unresolved distinction

```text
CANONICAL_BYTES
CANONICAL_EVIDENCE
CANONICAL_SEMANTIC_STATE
DERIVED_INDEX
DERIVED_CURRENT_VIEW
```

should not be assumed equivalent.

---

# CLUSTER H06 — Persona Reconstruction

## Planner source candidate

```text
SOURCE_OBJECTS = [SN-MI-H-008, SN-MI-M-007]
```

## RED-II stronger decomposition

```text
SOURCE_OBJECTS = [SN-R2-CH-001, SN-R2-M-001, SN-R2-M-003, SN-R2-M-004]
```

## Main competing hypotheses

```text
H06-A = durable Memory/State dominates Persona; runtime is mostly replaceable compute
H06-B = Memory + Reconstruction Operator jointly determine instantiated Persona
H06-C = model/runtime prior materially participates in Persona
H06-D = reconstruction policy itself may be identity-bearing
```

## Critical tests already present in source

```text
Context Compiler Swap
Retrieval Swap
Model Family Swap
Context Order Randomization
Context Budget Reduction
Historical Replay
```

---

# CLUSTER H07 — Current standpoint: persist or derive?

## Candidate A — derive from history every runtime

Implicit in reconstruction-centered source direction.

## Candidate B — persist a minimal explicit current standpoint/commitment state

```text
SOURCE_OBJECT = SN-R2-OQ-003
RATIONALE = reduce reconstruction/model dependence
```

## Source constraint

```text
HISTORICAL_EXPERIENCE != CURRENT_INTERPRETATION
```

Even if persisted, current standpoint must not overwrite historical evidence.

---

# CLUSTER H08 — Common Memory vs Persona-local Memory

## Planner candidate

```text
SOURCE_OBJECTS = [SN-MI-H-005, SN-MI-M-006]
```

## Convergence challenge

```text
SOURCE_OBJECTS = [SN-MI-RISK-004, SN-R1-RISK-002, SN-R3-RISK-009]
```

## Strong counterproposal candidate

```text
SOURCE_OBJECTS = [SN-R1-H-003, SN-R3-H-007]
FORM = Shared Evidence / History + Separate Interpretation
```

## Open questions

```text
- What can be common?
- What may promote from local to common?
- Should interpretation ever be common by default?
- How are shared facts distinguished from shared derived meaning?
- How is common-memory propagation replayed/audited?
```

---

# CLUSTER H09 — Learning / expertise / procedural memory

## Planner source direction

```text
EXPERIENCE
→ episodic evidence/memory
→ pattern/knowledge/heuristic/procedural expertise
→ later behavior
```

Tracked in `SN-MI-M-004`, `SN-MI-M-005`, and the planner source requirements.

## Open tension

```text
PROCEDURAL_EXPERTISE:
MEMORY ?
DERIVED_STATE ?
FUNCTION/SKILL ?
MODEL-BOUND ADAPTER ?
```

RED-II flags expertise portability as representation-dependent (`SN-R2-FIND-005`).

---

# CLUSTER H10 — Forgetting / deletion / archival

## Functional forgetting candidate

```text
SOURCE_OBJECTS = [SN-MI-H-009, SN-R1-H-004, SN-R1-M-001]
```

## Distinct operations in source

```text
retrieval suppression
dormancy
supersession
compression
archival
content deletion
cryptographic erasure
```

## Ghost influence challenge

```text
SOURCE_OBJECTS = [SN-R3-RISK-003, SN-R3-PC-009, SN-R3-H-002]
FORM = DELETE_SOURCE != DELETE_INFLUENCE
```

## Sovereignty tension

```text
PERMANENT_DOSSIER_RISK
vs
DESTRUCTIVE_FORGETTING_RISK
```

---

# CLUSTER H11 — Memory origin / provenance / authority laundering

## Strong source convergence

```text
SOURCE_OBJECTS = [SN-MI-PC-002, SN-MI-M-003, SN-R1-RISK-005, SN-R1-PC-004, SN-R3-M-002, SN-R3-PC-003, SN-R3-PC-004]
```

Core candidate relations:

```text
MODEL_CURATED_MEMORY != OWNER_INTENT
REPETITION != ORIGIN_AUTHORITY_UPGRADE
ORIGIN != DERIVATION
```

## Open implementation question

How origin survives summary/derivation/merge/reconstruction without making ordinary memory operations prohibitively heavy remains unresolved.

---

# CLUSTER H12 — Memory poisoning / compositional drift

## Acute poisoning

```text
SOURCE_OBJECTS = [SN-MI-RISK-001, SN-R1-RISK-004]
```

## Slow compositional drift

```text
SOURCE_OBJECTS = [SN-R3-RISK-002, SN-R3-M-004, SN-R3-PC-005]
```

## Competing safety models

```text
PER_WRITE_GATE_ONLY
vs
TRAJECTORY_MONITORING
vs
HYBRID
```

RED-III strongly argues per-write-only control is insufficient.

---

# CLUSTER H13 — Persona lifecycle / Memory lifecycle

## Source principle

```text
SOURCE_OBJECTS = [SN-WP1-M-002, SN-MI-PC-001, SN-MI-M-001, SN-MI-M-002]
```

Key open relation:

```text
PERSONA_LIFECYCLE != MEMORY_LIFECYCLE
```

but Persona lifecycle can depend on Memory lifecycle outcomes.

Candidate events include create/activate/evolve/fission/retire/recover for Persona and candidate/durable/consolidated/dormant/superseded/archived/forgotten for Memory.

Exact states are not selected.

---

# CLUSTER H14 — Fission

## Planner model

```text
SOURCE_OBJECTS = [SN-MI-H-010, SN-MI-PC-007]
```

## RED-I survival finding

```text
SOURCE_OBJECTS = [SN-R1-H-005, SN-R1-H-006]
```

## Authority constraint

```text
SOURCE_OBJECTS = [SN-R3-PC-011, SN-R3-H-004]
```

## Test

```text
SN-R1-EXP-007
```

Open semantic question remains whether descendants are “same Persona,” legitimate successors, branches, or another relation. Sources do not require a single metaphysical answer.

---

# CLUSTER H15 — Merge / reconciliation

## Planner source

```text
SOURCE_OBJECTS = [SN-MI-H-011, SN-MI-H-012]
```

## RED-I alternative

```text
SOURCE_OBJECT = SN-R1-CH-005
FORM = new successor C rather than identity reunification
```

## Authority constraint

```text
SOURCE_OBJECT = SN-R3-H-005
```

## Experiment

```text
SN-R1-EXP-008
```

No source establishes Merge as a required primitive.

---

# CLUSTER H16 — Provider / model replacement

## Design intent

```text
SOURCE_OBJECTS = [SN-WP1-PC-001, SN-WP1-PC-003, SN-MI-PC-008, SN-MI-PC-009]
```

## Empirical challenge

```text
SOURCE_OBJECTS = [SN-R1-PC-003, SN-R1-CH-006, SN-R2-H-004, SN-R2-FIND-004, SN-R2-FIND-008]
```

Key distinction:

```text
PROVIDER_REPLACEABILITY_AS_DESIGN_INTENT
!=
BEHAVIORAL_EQUIVALENCE_AS_EMPIRICAL_FACT
```

---

# CLUSTER H17 — Local degraded survival

## Planner direction

```text
SOURCE_OBJECT = SN-MI-H-013
```

## RED-I / RED-II survival findings

```text
SOURCE_OBJECTS = [SN-R1-H-007, SN-R1-PC-005, SN-R2-H-005, SN-R2-H-006]
```

## RED-II limitation

```text
SOURCE_OBJECT = SN-R2-RISK-005
```

## RED-III control condition

```text
SOURCE_OBJECTS = [SN-R3-PC-019, SN-R3-H-008]
```

Candidate formulation:

```text
DEGRADED_COGNITION
+
SELECTIVE_AUTHORITY_CONTRACTION
!=
PERSONA_DEATH
```

This remains a source-derived candidate, not a final design.

---

# CLUSTER H18 — Authority separation and continuity

## Strong source firewall

```text
SOURCE_OBJECTS = [SN-WP1-PC-004, SN-WP1-PC-005, SN-WP2-PC-005, SN-MI-PC-012, SN-R1-PC-006, SN-R3-PC-002]
```

## Continuity problem

```text
SOURCE_OBJECTS = [SN-MI-OQ-007, SN-R3-H-003, SN-R3-OQ-002]
```

## RED-III default candidate

```text
SOURCE_OBJECT = SN-R3-PC-010
FORM = authority may contract automatically under risk; expansion remains separate
```

This is not Owner-adopted simply because RED-III recommends it.

---

# CLUSTER H19 — Audit independence

## Source risk

```text
SOURCE_OBJECTS = [SN-R1-RISK-007, SN-R1-H-008, SN-R3-PC-012, SN-R3-RISK-004, SN-R3-PC-013]
```

Candidate evaluation dimensions:

```text
model independence
evidence-route independence
memory independence
instruction independence
evaluator independence
error-correlation
```

Product-side Audit Persona remains distinct from `AAA-VALIDATION-AUDITOR`.

---

# CLUSTER H20 — Owner burden vs safety automation

## Planner design intent

Owner should not manually manage every memory operation.

## RED-III challenge

```text
SOURCE_OBJECTS = [SN-R3-PC-014, SN-R3-H-006, SN-R3-RISK-005]
```

Competing models:

```text
MAX_APPROVAL_COUNT
vs
MEANINGFUL_APPROVAL_DENSITY
vs
RISK-TIERED_AUTOMATION
```

No exact threshold model is selected.

---

# CLUSTER H21 — Relationship / retention / exit

## Planner design intent

```text
SOURCE_OBJECTS = [SN-MI-DI-001, SN-MI-PC-013]
```

## Counter-risk

```text
SOURCE_OBJECTS = [SN-MI-RISK-006, SN-R1-RISK-008, SN-R1-PC-007, SN-R3-RISK-007, SN-R3-PC-016, SN-R3-PC-017]
```

Key distinction:

```text
TECHNICAL_EXPORTABILITY
!=
COGNITIVE_RELATIONAL_EXIT_COST
```

---

# CLUSTER H22 — Self / Boundary

## Whitepaper source direction

```text
SOURCE_OBJECTS = [SN-WP2-PC-004, SN-WP2-M-001, SN-WP2-PC-005]
```

Main source thesis:

```text
OBSERVED_INTEGRATION
!=
SYSTEM_INTERPRETATION
!=
USER_DEFINED_SELF_STATUS
!=
AUTHORITY
```

No source in this normalization set establishes that `SELF` must be a permanently materialized Memory object.

Later live brainstorming may contain additional operator/function interpretations, but those are intentionally excluded from this source-derived directory.

---

# CLUSTER H23 — Change / evolution measurement

## Planner evaluation principle

```text
SOURCE_OBJECTS = [SN-MI-PC-014, SN-MI-EVAL-001]
```

## RED-I corroborating source direction

```text
SOURCE = RED-I evaluation dimensions
```

## RED-III correction

```text
SOURCE_OBJECTS = [SN-R3-PC-006, SN-R3-M-005]
```

Candidate evaluation logic:

```text
STYLE_DIFFERENCE != PERSONA_EVOLUTION_PROOF
STATIC_DIFFERENCE != HARMFUL_DRIFT
```

Need longitudinal causal linkage between experience and durable behavioral change.

---

# CLUSTER H24 — Reality / philosophy / technical abstraction relation

## Whitepaper grounding

```text
SOURCE_OBJECTS = [SN-WP2-PC-001, SN-WP2-PC-003, SN-WP2-PC-011]
```

Current source-level relation candidate:

```text
REALITY
→ interpretation / hypothesis
→ technical representation
→ implementation
→ falsification/revision
```

This is a source-grounded epistemic direction, not a claim that technical representation equals human reality.

---

# Cross-source status markers for next-session tagging

Suggested **tag options**, not applied decisions:

```text
ACTIVE_CANDIDATE
CURRENT_BEST_CANDIDATE
WEAK_CANDIDATE
COUNTER_HYPOTHESIS
SURVIVED_ATTACK
WEAKENED_BY_ATTACK
SOURCE_ONLY
CS_PRIOR_PENDING
PHILOSOPHY_PRIOR_PENDING
REQUIRES_EXPERIMENT
REQUIRES_OWNER_SEMANTIC_DECISION
REQUIRES_ARCHITECTURE_RECONCILIATION
OUT_OF_SCOPE
SUPERSEDED_BY_LATER_DISCUSSION
```

No status above is assigned in this file unless the original source itself supplied that status.
