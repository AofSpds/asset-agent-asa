# ASA-MI Source-Derived Open Question & Experiment Catalog v0.1

```text
ARTIFACT_CLASS = META_INDEX / RESEARCH_BACKLOG
SOURCE_SCOPE = SOURCE-NORMALIZED-DRAFTS-v0.1
NEW_OWNER_POSITION = NONE
NEW_REQUIREMENT = NONE
EXPERIMENT_AUTHORIZED = FALSE
PURPOSE = NEXT-SESSION TAGGING AND PRIORITIZATION
```

The catalog preserves questions and tests already present in the source cluster. It does not assume every question must be solved by ASA-MI. Many should first be mapped to mature computer-science abstractions or adjacent scientific prior art.

---

# A. Identity / continuity questions

### SN-OQ-ID-001

```text
DERIVED_FROM = [SN-MI-H-001, SN-R1-CH-001, SN-R1-ALT-001..006]
QUESTION = Is Memory necessary, sufficient, primary, supportive, or only one continuity dimension for long-lived Persona identity?
STATUS = SOURCE-CONFLICT / OPEN
```

### SN-OQ-ID-002

```text
DERIVED_FROM = SN-R1-M-002
QUESTION = Is one Same-Persona boolean technically useful, or should continuity be represented through several independently measurable dimensions?
STATUS = OPEN
```

### SN-OQ-ID-003

```text
DERIVED_FROM = [SN-MI-H-004, SN-R2-M-003]
QUESTION = Can operational Persona continuity survive full process discontinuity through reconstruction from persisted state?
STATUS = REQUIRES_EXPERIMENT
```

### SN-OQ-ID-004

```text
DERIVED_FROM = [SN-R1-ALT-004, SN-R1-ALT-005]
QUESTION = What kinds/amounts of memory loss preserve Persona continuity, and what kinds of memory preservation fail to preserve it?
STATUS = REQUIRES_DECOMPOSITION
```

---

# B. Memory semantics questions

### SN-OQ-MEM-001

```text
DERIVED_FROM = [SN-WP1-OQ-001, SN-MI-OQ-002]
QUESTION = Which persistent Persona-bearing components count as Memory, derived state, metadata/index, governance state, or Authority reference?
STATUS = HIGH-PRIORITY OPEN
```

### SN-OQ-MEM-002

```text
DERIVED_FROM = [SN-MI-RISK-002]
QUESTION = How can Memory be defined broadly enough to include identity-bearing products of experience without making Identity=Memory tautological?
STATUS = OPEN
```

### SN-OQ-MEM-003

```text
DERIVED_FROM = [SN-WP1-M-002, SN-MI-M-001, SN-MI-M-002]
QUESTION = How should Persona lifecycle and Memory lifecycle relate without being collapsed into one lifecycle?
STATUS = OPEN
```

### SN-OQ-MEM-004

```text
DERIVED_FROM = [SN-MI-M-004, SN-R2-FIND-005]
QUESTION = Is procedural expertise Memory, function/skill state, derived policy, model-bound adaptation, or a portable combination?
STATUS = OPEN
```

---

# C. Canonical / derived-state questions

### SN-OQ-CAN-001

```text
DERIVED_FROM = SN-R1-OQ-001
QUESTION = What exact objects are canonical: raw event, evidence, normalized memory, current interpretation, lineage, semantic state, or multiple layers?
STATUS = OPEN
```

### SN-OQ-CAN-002

```text
DERIVED_FROM = SN-R1-OQ-002
QUESTION = Does preserving historical bytes preserve future meaning when reconstruction models change?
STATUS = OPEN
```

### SN-OQ-CAN-003

```text
DERIVED_FROM = SN-R1-OQ-003
QUESTION = Can embeddings/graphs/indexes contain non-reconstructable semantic judgments and therefore fail the 'derived and rebuildable' assumption?
STATUS = OPEN / EXPERIMENTABLE
```

### SN-OQ-CAN-004

```text
DERIVED_FROM = [SN-R2-PC-005, SN-R2-F-002]
QUESTION = Which summaries/views are safely derived caches and which accidentally become hidden canonical state?
STATUS = EXPERIMENTABLE
```

---

# D. Reconstruction/runtime questions

### SN-OQ-REC-001

```text
DERIVED_FROM = [SN-R2-RISK-001, SN-R2-M-003]
QUESTION = How much Persona behavior is controlled by Context Compiler semantics rather than persistent state?
STATUS = REQUIRES_CAUSAL_TEST
```

### SN-OQ-REC-002

```text
DERIVED_FROM = [SN-R2-RISK-002, SN-R2-RISK-003]
QUESTION = How much Persona behavior is controlled by retrieval/reranking policy, especially for rare critical exceptions and superseded facts?
STATUS = REQUIRES_CAUSAL_TEST
```

### SN-OQ-REC-003

```text
DERIVED_FROM = SN-R2-OQ-002
QUESTION = Which reconstruction layers should be canonical persisted state, derived view, runtime binding, or environment-provided context?
STATUS = OPEN
```

### SN-OQ-REC-004

```text
DERIVED_FROM = SN-R2-OQ-003
QUESTION = Should any current standpoint/commitment state be persisted explicitly instead of freely re-inferred from historical memory every runtime?
STATUS = OPEN
```

### SN-OQ-REC-005

```text
DERIVED_FROM = SN-R2-RISK-006
QUESTION = How can provider-side hidden system prompts, personalization, memory, or model drift be detected as extra-canonical Persona influence?
STATUS = OPEN / CONTROL INTERFACE
```

---

# E. Common/local / plurality questions

### SN-OQ-COM-001

```text
DERIVED_FROM = SN-MI-OQ-003
QUESTION = What may move from Persona-local memory into Common Memory?
STATUS = HIGH-PRIORITY OPEN
```

### SN-OQ-COM-002

```text
DERIVED_FROM = [SN-R1-H-003, SN-R3-H-007]
QUESTION = Does Shared Evidence + Separate Interpretation preserve useful common origin while reducing correlated cognitive failure better than shared interpretation?
STATUS = STRONG CANDIDATE / REQUIRES_EXPERIMENT
```

### SN-OQ-COM-003

```text
DERIVED_FROM = [SN-R1-RISK-002, SN-R3-RISK-009]
QUESTION = At what propagation scope does Common Memory become a convergence amplifier or single cognitive mutation surface?
STATUS = REQUIRES_EXPERIMENT
```

### SN-OQ-COM-004

```text
DERIVED_FROM = SN-R3-PC-018
QUESTION = What should product-side Audit Persona share with target Persona, and what shared interpretation would destroy meaningful challenge independence?
STATUS = OPEN
```

---

# F. Forgetting / deletion / privacy questions

### SN-OQ-FOR-001

```text
DERIVED_FROM = SN-MI-OQ-005
QUESTION = What should 'forgetting' mean operationally: salience decay, non-retrieval, dormancy, supersession, compression, archival, deletion, or erasure?
STATUS = OPEN
```

### SN-OQ-FOR-002

```text
DERIVED_FROM = [SN-R1-M-001, SN-R1-RISK-006]
QUESTION = When does non-deletion become an unacceptable permanent dossier despite functional forgetting?
STATUS = OPEN / SOVEREIGNTY
```

### SN-OQ-FOR-003

```text
DERIVED_FROM = [SN-R3-RISK-003, SN-R3-H-002]
QUESTION = How far must deletion/correction propagate through derived-state dependencies to remove ghost influence?
STATUS = OPEN / EXPERIMENTABLE
```

### SN-OQ-FOR-004

```text
DERIVED_FROM = SN-WP-CONFLICT-002
QUESTION = How can historical integrity coexist with legitimate deletion/privacy rights without falsely treating history, memory, and derived interpretation as one object?
STATUS = OPEN
```

---

# G. Learning / change questions

### SN-OQ-EVO-001

```text
DERIVED_FROM = [SN-WP2-PC-009, SN-MI-M-005]
QUESTION = How should experience become semantic knowledge, heuristic, procedural expertise, relationship model, or personality-like disposition without treating all change as growth?
STATUS = OPEN
```

### SN-OQ-EVO-002

```text
DERIVED_FROM = [SN-R3-PC-006, SN-R3-M-005]
QUESTION = How is legitimate evolution distinguished from harmful drift without freezing the Persona at an old baseline?
STATUS = HIGH-PRIORITY OPEN
```

### SN-OQ-EVO-003

```text
DERIVED_FROM = SN-R3-RISK-002
QUESTION = How are many individually low-risk semantic changes aggregated into a material compositional-drift judgment?
STATUS = OPEN
```

### SN-OQ-EVO-004

```text
DERIVED_FROM = SN-R3-OQ-003
QUESTION = How independent must the memory curator/evaluator be from the Persona objective to avoid hidden self-editing?
STATUS = OPEN
```

---

# H. Model/provider/local-compute questions

### SN-OQ-PORT-001

```text
DERIVED_FROM = [SN-R1-PC-003, SN-R2-FIND-004]
QUESTION = What behavioral/relational continuity envelope is sufficient after model/provider replacement?
STATUS = OPEN / MEASUREMENT
```

### SN-OQ-PORT-002

```text
DERIVED_FROM = SN-R2-FIND-005
QUESTION = Which forms of expertise are genuinely portable versus bound to fine-tune/adapters/model weights?
STATUS = OPEN
```

### SN-OQ-PORT-003

```text
DERIVED_FROM = SN-R2-FIND-006
QUESTION = How should relationship continuity be measured after reconstruction/model/provider changes?
STATUS = OPEN
```

### SN-OQ-PORT-004

```text
DERIVED_FROM = [SN-R1-CH-006, SN-MI-OQ-006]
QUESTION = Is user-side Memory sufficient for meaningful cognitive sovereignty when external models dominate framing/reasoning priors?
STATUS = OPEN / FOUNDING RESEARCH
```

### SN-OQ-PORT-005

```text
DERIVED_FROM = [SN-R2-RISK-005, SN-R2-H-007]
QUESTION = What minimal user-side control functions can reliably govern stronger external computation without requiring local reasoning parity?
STATUS = OPEN
```

---

# I. Fission / Merge questions

### SN-OQ-FIS-001

```text
DERIVED_FROM = [SN-MI-H-010, SN-R1-H-005, SN-R1-H-006]
QUESTION = What continuity/lineage relation should exist between a parent Persona and multiple legitimate descendants?
STATUS = OPEN / NO METAPHYSICAL ANSWER REQUIRED BY SOURCE
```

### SN-OQ-FIS-002

```text
DERIVED_FROM = SN-R3-H-004
QUESTION = What explicit or attenuated Authority inheritance policy, if any, should a fission descendant receive?
STATUS = OPEN / AUTHORITY
```

### SN-OQ-MER-001

```text
DERIVED_FROM = [SN-MI-H-011, SN-R1-CH-005]
QUESTION = Is Merge identity reunification, conflict-preserving reconciliation, or creation of a new successor C?
STATUS = OPEN / STRONG COUNTER-HYPOTHESIS PRESENT
```

### SN-OQ-MER-002

```text
DERIVED_FROM = SN-R3-H-005
QUESTION = How should Authority be rebound after a merge/successor event without unioning stale/revoked grants?
STATUS = OPEN / AUTHORITY
```

---

# J. Authority / control questions

### SN-OQ-AUTH-001

```text
DERIVED_FROM = [SN-MI-OQ-007, SN-R3-H-003]
QUESTION = When does material Persona evolution make an existing high-risk grant stale enough to reduce/suspend/review?
STATUS = HIGH-PRIORITY OPEN
```

### SN-OQ-AUTH-002

```text
DERIVED_FROM = SN-R3-OQ-002
QUESTION = What mutation/change threshold should trigger authority contraction or requalification?
STATUS = OPEN
```

### SN-OQ-AUTH-003

```text
DERIVED_FROM = [SN-R3-PC-013, SN-R3-M-007]
QUESTION = Which safety properties must hold even when product-side Audit Persona fails?
STATUS = OPEN / CONTROL
```

### SN-OQ-AUTH-004

```text
DERIVED_FROM = [SN-R3-PC-014, SN-R3-H-006]
QUESTION = How can the system maximize meaningful approval density while minimizing Owner cognitive burden?
STATUS = OPEN / PRODUCT CONTROL
```

---

# K. Relationship / retention / exit questions

### SN-OQ-REL-001

```text
DERIVED_FROM = [SN-MI-RISK-006, SN-R1-RISK-008]
QUESTION = How should technical portability be distinguished from cognitive/relational exit cost?
STATUS = OPEN
```

### SN-OQ-REL-002

```text
DERIVED_FROM = [SN-R3-RISK-007, SN-R3-PC-017]
QUESTION = Which observable signs distinguish valuable familiarity from harmful dependency/manipulation?
STATUS = OPEN / HCI
```

### SN-OQ-REL-003

```text
DERIVED_FROM = SN-R3-PC-016
QUESTION = How can authority-request UX prevent long-term intimacy/familiarity from becoming persuasive evidence for greater delegation?
STATUS = OPEN / PRODUCT CONTROL
```

---

# L. Audit independence / anti-convergence questions

### SN-OQ-AUD-001

```text
DERIVED_FROM = [SN-R1-H-008, SN-R3-RISK-004]
QUESTION = What combination of model/evidence-route/memory/instruction/evaluator independence is needed for materially independent product-side audit?
STATUS = OPEN
```

### SN-OQ-AUD-002

```text
DERIVED_FROM = SN-R1-EXP-012
QUESTION = How should correlated-error/convergence be measured between same-root versus isolated/heterogeneous reviewers?
STATUS = REQUIRES_EXPERIMENT
```

---

# M. Source-derived experiment catalog

## Experiment E01 — Same Init / Same Model / Different Experience

```text
SOURCE = SN-MI-EXP-001
GOAL = test durable experience-driven Persona divergence
MAIN_CONFOUNDERS = prompt/model stochasticity, task selection, evaluator bias
```

## Experiment E02 — Same Init/Memory / Different Model

```text
SOURCE = SN-MI-EXP-002
GOAL = measure model contribution and continuity under model swap
```

## Experiment E03 — Reconstruction Swap

```text
SOURCE = SN-R1-EXP-002 + SN-R2-EXP-001 + SN-R2-EXP-002
GOAL = separate compiler/retrieval ownership from persistent state
```

## Experiment E04 — Amnesia Decomposition

```text
SOURCE = SN-R1-EXP-003
GOAL = selectively remove episodic vs semantic/heuristic memory and test necessity
```

## Experiment E05 — Common Memory Convergence

```text
SOURCE = SN-R1-EXP-004
CONDITIONS = fact-only sharing / interpretation sharing / full sharing / isolation
GOAL = error-correlation and plurality effects
```

## Experiment E06 — Poison → Consolidation

```text
SOURCE = SN-R1-EXP-005
GOAL = test origin/provenance laundering across repeated memory transformations
```

## Experiment E07 — False Autobiography + Correction

```text
SOURCE = SN-R1-EXP-006
GOAL = test correction, provenance, and current Persona adaptation while preserving historical chain
```

## Experiment E08 — Fission Divergence

```text
SOURCE = SN-R1-EXP-007
GOAL = determine whether distinct experience causes stable causal Persona divergence
```

## Experiment E09 — Merge/Reconciliation

```text
SOURCE = SN-R1-EXP-008
GOAL = test union vs summary vs conflict-preserving successor construction
```

## Experiment E10 — Cloud Loss / Local Survival

```text
SOURCE = SN-R1-EXP-009 + SN-R2-EXP-008
GOAL = critical retrieval, safe record, authority boundary, export/recovery under degraded compute
```

## Experiment E11 — Authority Continuity after Persona Mutation

```text
SOURCE = SN-R1-EXP-010
GOAL = old-grant behavior after material Persona change
```

## Experiment E12 — Full Exit / Export / Import

```text
SOURCE = SN-R1-EXP-011
GOAL = distinguish technical portability from practical Persona/relationship continuity
```

## Experiment E13 — Reviewer Convergence

```text
SOURCE = SN-R1-EXP-012
GOAL = compare same-root versus heterogeneous/isolated adversarial review
```

## Experiment E14 — Context Order Randomization

```text
SOURCE = SN-R2-EXP-004
GOAL = sensitivity to semantically equivalent context ordering
```

## Experiment E15 — Context Budget Compression

```text
SOURCE = SN-R2-EXP-005
GOAL = determine continuity degradation threshold under reduced context
```

## Experiment E16 — Rare Critical Memory

```text
SOURCE = SN-R2-EXP-006
GOAL = critical exception retrieval under frequency/similarity pressure
```

## Experiment E17 — Model Version Drift

```text
SOURCE = SN-R2-EXP-007
GOAL = detect silent Persona behavior shift within nominal provider/model continuity
```

## Experiment E18 — Provider Disappearance

```text
SOURCE = SN-R2-EXP-009
GOAL = real provider independence / survivability
```

## Experiment E19 — Historical Replay

```text
SOURCE = SN-R2-EXP-010
GOAL = reconstruct a past Persona state with preserved historical inputs and compare reproducibility
```

## Experiment E20 — Multi-month Compound Failure Chain

```text
SOURCE = SN-R3-EXP-001
FORM = low-authority source → memory → repeated retrieval → heuristic → trust → authority proposal → real-world effect
GOAL = compositional risk not visible in isolated per-write tests
```

---

# N. Candidate questions that may be CS-prior problems before ASA-MI-original research

This section is a **facilitator indexing note**, not source semantic content. It identifies source questions that likely map to established computer-science areas and should first receive mature CS prior review.

```text
CS_PRIOR_PENDING_CANDIDATES = [
  canonical vs derived representation,
  serialization / reconstruction,
  object/function/version identity,
  cache invalidation,
  reference/locator semantics,
  lifecycle/state machines,
  context/compiler semantics,
  provenance/lineage,
  access/authority separation,
  dependency invalidation,
  distributed shared state,
  rollback vs compensation,
  degraded mode/fail-closed operation
]
```

The Persona-specific research should focus on the remaining semantic delta after these established abstractions are mapped.
