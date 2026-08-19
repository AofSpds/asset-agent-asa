# ASA-MI Source-Normalized Draft — Next-Session Tagging Backlog

```text
ARTIFACT_CLASS = META_WORKSHEET
SOURCE_SEMANTICS = NO_NEW_SOURCE_CLAIMS
PURPOSE = OWNER + ASA-MI-PF TAGGING SESSION
TAGGING_PERFORMED = FALSE
OWNER_DECISION = NONE
```

This worksheet is intentionally separate from source-object content. It proposes **questions and tag slots**, not answers.

---

# 1. Object status tags — candidate vocabulary

Use only where useful. The vocabulary is open.

```text
SOURCE_ONLY
CURRENTLY_RELEVANT
ACTIVE_CANDIDATE
CURRENT_BEST_CANDIDATE
ALTERNATIVE_CANDIDATE
COUNTER_HYPOTHESIS
WEAKENED
SURVIVED_ATTACK
REQUIRES_EXPERIMENT
CS_PRIOR_PENDING
PHILOSOPHICAL_PRIOR_PENDING
REQUIRES_OWNER_SEMANTIC_DECISION
REQUIRES_ARCHITECTURE_RECONCILIATION
REQUIRES_CONTROL_RECONCILIATION
OUT_OF_SCOPE
SUPERSEDED_BY_LATER_DISCUSSION
UNRESOLVED
NOT_PROVEN
```

Do not assign `CURRENT_BEST_CANDIDATE` merely because several sources agree.

```text
COUNT(AGREEMENT) != EVIDENCE_WEIGHT
```

---

# 2. Relation tags — candidate vocabulary

```text
SUPPORTS
CONTRADICTS
REFINES
ALTERNATIVE_TO
DEPENDS_ON
DERIVED_FROM
WEAKENS
SURVIVED_ATTACK_FROM
REQUIRES_EXPERIMENT
APPLIES_UNDER
OUT_OF_SCOPE_FOR
COEXISTS_WITH
TENSION_WITH
SUPERSEDED_BY
HISTORICAL_PREDECESSOR_OF
IMPLEMENTATION_OF
EVALUATES
FALSIFIES_IF_OBSERVED
```

Relation tags should be directional where direction matters.

---

# 3. Per-object tagging card

For each selected object:

```text
OBJECT_ID =
SOURCE_STATUS =
CURRENT_RESEARCH_RELEVANCE =
CURRENT_TAG =
RELATES_TO =
RELATION =
OWNER_SEMANTIC_NOTE =
EVIDENCE_STATE =
EXPERIMENT_LINK =
CS_PRIOR_REF =
PHILOSOPHICAL_PRIOR_REF =
LATER_LIVE_BRAINSTORM_LINK =
KEEP_SOURCE_WORDING = TRUE/FALSE
NORMALIZATION_CORRECTION_NEEDED = TRUE/FALSE
```

`NORMALIZATION_CORRECTION_NEEDED` means the draft extraction misrepresented the source. It is not a semantic disagreement with the source.

---

# 4. Suggested first-pass tagging order

The order is chosen to reduce cascading rework. It is a facilitator suggestion, not a semantic conclusion.

## T1 — Identity / Memory cluster

```text
TARGET = H01
WHY_FIRST = central proposition; many downstream concepts depend on what reading of 'Memory' and 'Identity' is being discussed
```

Objects to review:

```text
SN-MI-H-001
SN-MI-H-003
SN-R1-CH-001
SN-R1-H-001
SN-R1-ALT-001..006
SN-R1-M-002
```

Questions:

```text
Which readings remain active?
Which are merely historical source formulations?
Which were already refined by later live dialogue?
Which should remain deliberately strong falsification targets even if not current-best?
```

## T2 — Memory semantics / scope cluster

Objects:

```text
SN-WP1-M-001
SN-WP1-OQ-001
SN-MI-M-004
SN-MI-OQ-002
SN-MI-RISK-002
```

Question:

```text
What is the current intended breadth of Memory, without forcing a final ontology?
```

## T3 — History / current interpretation

Objects:

```text
SN-WP2-PC-007
SN-MI-PC-004
SN-MI-M-005
SN-R1-PC-002
SN-R1-H-002
SN-WP-CONFLICT-002
```

Question:

```text
What historical facts/evidence/records are preservation-first, and which semantic layers remain mutable/deletable?
```

## T4 — Reconstruction / hidden ownership

Objects:

```text
SN-MI-H-008
SN-MI-M-007
SN-R1-RISK-003
SN-R1-CH-004
SN-R2-CH-001
SN-R2-M-001
SN-R2-M-003
SN-R2-RISK-001
SN-R2-RISK-002
```

Question:

```text
What should count as part of Persona versus environment/runtime/reconstructor?
```

## T5 — Common/local memory / anti-convergence

Objects:

```text
SN-MI-H-005
SN-MI-M-006
SN-MI-RISK-004
SN-R1-RISK-002
SN-R1-H-003
SN-R3-RISK-009
SN-R3-H-007
```

Question:

```text
Which shared layers preserve common origin without sharing conclusion/interpretation?
```

## T6 — Forget/delete/influence

Objects:

```text
SN-MI-H-009
SN-MI-PC-006
SN-R1-M-001
SN-R1-RISK-006
SN-R3-RISK-003
SN-R3-PC-009
SN-R3-H-002
```

Question:

```text
How many distinct lifecycle operations are currently useful to preserve as candidates?
```

## T7 — Provider/local/portability

Objects:

```text
SN-WP1-PC-001
SN-WP1-PC-003
SN-MI-PC-008..011
SN-MI-H-013
SN-R1-PC-003
SN-R1-CH-006
SN-R2-FIND-001..008
SN-R2-RISK-005
```

Question:

```text
Which statements are design intent, which are empirical hypotheses, and which are already contradicted by dependence findings?
```

## T8 — Authority/control

Objects:

```text
SN-WP1-PC-004..005
SN-WP2-PC-005
SN-MI-PC-012
SN-MI-OQ-007
SN-R1-PC-006
SN-R3-PC-002
SN-R3-PC-010..015
SN-R3-H-003..006
```

Question:

```text
Which are existing project governance principles, product-research candidates, or RED-only recommendations?
```

## T9 — Fission / Merge

Objects:

```text
SN-MI-H-010..012
SN-MI-PC-007
SN-R1-H-005..006
SN-R1-CH-005
SN-R3-H-004..005
```

Question:

```text
Which semantics are retained as candidates, and which should be explicitly deferred?
```

## T10 — Human realism / relationship / exit

Objects:

```text
SN-MI-DI-001
SN-MI-PC-013
SN-MI-RISK-006
SN-R1-RISK-008
SN-R1-PC-007
SN-R3-RISK-007
SN-R3-PC-016..017
```

Question:

```text
Which are product intents, HCI hypotheses, ethical risks, or measurable evaluation dimensions?
```

---

# 5. Cross-link to live brainstorming — intentionally deferred

The source-normalized draft must remain isolated until the Owner explicitly performs the link/tagging act.

Potential later link classes:

```text
SOURCE_OBJECT
--HISTORICAL_PREDECESSOR_OF-->
LIVE_BRAINSTORM_OBJECT

SOURCE_OBJECT
--SUPPORTS-->
CURRENT_WORKING_HYPOTHESIS

SOURCE_OBJECT
--CONTRADICTS-->
CURRENT_WORKING_HYPOTHESIS

SOURCE_OBJECT
--SUPERSEDED_BY_LATER_DISCUSSION-->
LIVE_OBJECT
```

Do not infer these links merely because wording looks similar.

---

# 6. Special later-discussion areas likely to need reconciliation

This list is a facilitator indexing note based on known separation needs, not a pre-applied tag.

```text
SELF as stored state vs runtime/context selector
CURRENT as stored status vs evaluation operator
Memory primitive M(Context) → Value
constant as scoped invariant / change-rate & transition-condition model
external URL/function binding as Memory candidates
Persona as instantiated Memory/State object
CS abstraction legacy as default prior
philosophy as reality-grounding for human→Persona abstraction
```

These concepts came from later live brainstorming and therefore are **not inserted into source-derived objects here**. They should be linked tomorrow only where the Owner confirms lineage/relationship.

---

# 7. Tagging-session success condition

The session succeeds if it produces clearer relations without forcing premature semantic closure.

```text
SUCCESS != ALL_OBJECTS_HAVE_ONE_FINAL_STATUS
SUCCESS = IMPORTANT_SOURCE_OBJECTS_HAVE_TRACEABLE_RELATION_TO_CURRENT_RESEARCH_STATE
```

Historical alternatives should remain visible even when they are no longer current-best.
