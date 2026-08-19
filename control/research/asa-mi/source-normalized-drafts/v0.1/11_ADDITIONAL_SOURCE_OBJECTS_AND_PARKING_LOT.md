# ASA-MI Additional Source Objects & Parking Lot v0.1

```text
ARTIFACT_CLASS = SOURCE_NORMALIZED_OBJECT_SET + PARKING_LOT
PURPOSE = PRESERVE SOURCE CONTENT NOT YET CENTRAL IN OTHER NORMALIZED FILES
SOURCE_DERIVED_ONLY = TRUE
CURRENT_BEST_SELECTION = NONE
TAGGING_STATE = DRAFT
```

This file deliberately captures source-derived concepts that are easy to lose because they sit between philosophy, architecture, product intent, and control. They are preserved even if later tagging concludes that some are superseded, overbroad, or outside ASA-MI scope.

---

# A. Historical memory/state firewalls from ASA-MI source packet

### SN-MI-HIST-PC-001

```text
CLASS = SOURCE_CLAIM / HISTORICAL_ANALYTICAL_FIREWALL
SOURCE = SRC-MI0
STATEMENT = MEMORY != CURRENT STATE
IMPORTANT = Later live brainstorming may challenge/refine this; do not rewrite historical source.
```

### SN-MI-HIST-PC-002

```text
CLASS = AUTHORITY_FIREWALL
SOURCE = SRC-MI0
STATEMENT = MEMORY != REQUIREMENT
```

### SN-MI-HIST-PC-003

```text
CLASS = AUTHORITY_FIREWALL
SOURCE = SRC-MI0
STATEMENT = MEMORY != DESIGN CONTRACT
```

### SN-MI-HIST-PC-004

```text
CLASS = AUTHORITY_FIREWALL
SOURCE = SRC-MI0
STATEMENT = MEMORY != OWNER DECISION RECEIPT
```

### SN-MI-HIST-PC-005

```text
CLASS = AUTHORITY_FIREWALL
SOURCE = SRC-MI0
STATEMENT = MEMORY != VALIDATION EVIDENCE
```

### SN-MI-HIST-PC-006

```text
CLASS = AUTHORITY_FIREWALL
SOURCE = SRC-MI0
STATEMENT = MEMORY != ACTIVE BASELINE POINTER
```

### SN-MI-HIST-PC-007

```text
CLASS = AUTHORITY_FIREWALL
SOURCE = SRC-MI0
STATEMENT = IDENTITY RECOVERY != AUTHORITY RECOVERY
```

These objects are especially important for tomorrow's tagging because some later live brainstorming intentionally broadens the concept of Memory. Historical firewalls about Requirement/Authority/Validation may survive even if `MEMORY != CURRENT STATE` is later refined.

---

# B. Memory visibility / scope / applicability

### SN-MI-M-009

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

### SN-MI-PC-015

```text
CLASS = PRINCIPLE_CANDIDATE
SOURCE = SRC-MI0
STATEMENT = MEMORY_VISIBILITY != MEMORY_APPLICABILITY
```

### SN-MI-PC-016

```text
CLASS = PRINCIPLE_CANDIDATE
SOURCE = SRC-MI0
STATEMENT = A memory visible for context does not automatically become a rule, requirement, hold, constraint, or authority in another scope.
```

---

# C. Memory evaluation should not collapse into one score

### SN-MI-PC-017

```text
CLASS = PRINCIPLE_CANDIDATE
SOURCE = SRC-MI0
STATEMENT = Memory evaluation should not collapse into one undifferentiated importance score.
```

### SN-MI-M-010

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

### SN-MI-OQ-008

```text
CLASS = OPEN_QUESTION
SOURCE = SRC-MI0
QUESTION = Which memory-evaluation dimensions are truly independent versus derivable from others?
```

---

# D. Owner burden / autonomous memory administration

### SN-MI-DI-002

```text
CLASS = DESIGN_INTENT_IN_SOURCE
SOURCE = SRC-MI0
STATEMENT = Owner should not manually administer memory IDs, TTLs, retention classes, digests, paths, levels, promotion rules, or every individual save/delete decision.
```

### SN-MI-DI-003

```text
CLASS = DESIGN_INTENT_IN_SOURCE
SOURCE = SRC-MI0
STATEMENT = Normal memory administration should largely be automated/LLM-managed.
```

### SN-MI-PC-018

```text
CLASS = PRINCIPLE_CANDIDATE
SOURCE = SRC-MI0
FORM = AUTONOMOUS_MEMORY_MANAGEMENT != AUTONOMOUS_AUTHORITY
```

### SN-MI-PC-019

```text
CLASS = PRINCIPLE_CANDIDATE
SOURCE = SRC-MI0
FORM = AUTONOMOUS_MEMORY_MANAGEMENT != UNREVIEWABLE_IDENTITY_MUTATION
```

### SN-MI-OQ-009

```text
CLASS = OPEN_QUESTION
SOURCE = SRC-MI0
QUESTION = How can memory administration remain low-burden while high-impact Persona mutation remains inspectable/recoverable?
```

---

# E. Cold-start recovery dimensions

### SN-MI-M-011

```text
CLASS = MODEL_CANDIDATE / EVALUATION_DIMENSION_SET
SOURCE = SRC-MI0
COLD_START_RECOVERY_DIMENSIONS = [
  IDENTITY_CONTINUITY,
  INTENT_CONTINUITY,
  COGNITIVE_CONTINUITY,
  EXECUTION_CONTINUITY,
  AUTHORITY_CONTINUITY
]
RULE = dimensions must not be automatically collapsed
```

### SN-MI-OQ-010

```text
CLASS = OPEN_QUESTION
SOURCE = SRC-MI0
QUESTION = What is the minimum state required for cold-start Persona reconstruction when reliable chat/session memory is zero?
```

### SN-MI-M-012

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

---

# F. Persona topology / plurality

### SN-MI-H-014

```text
CLASS = WORKING_HYPOTHESIS
SOURCE = SRC-MI1 / adversarial packet source context
STATEMENT = Personas may originate from a common Person-side cognitive root while accumulating Persona-specific experience, memory, specialization, heuristics, and relational history.
```

### SN-MI-PC-020

```text
CLASS = PRINCIPLE_CANDIDATE
SOURCE = SRC-MI1 / adversarial packet source context
STATEMENT = Persona topology is not predefined as a fixed tree.
```

### SN-MI-H-015

```text
CLASS = WORKING_HYPOTHESIS
SOURCE = SRC-MI1 / adversarial packet source context
STATEMENT = Different users may maintain one Persona, many Personas, branching Personas, or other relational forms.
```

### SN-MI-RISK-007

```text
CLASS = RISK_CLAIM
SOURCE = adversarial source context
STATEMENT = Open-ended Persona differentiation may create complexity, fragmented agency, inconsistent state, authority confusion, maintenance burden, or dependency.
```

---

# G. Change / Growth distinction

### SN-MI-PC-021

```text
CLASS = PRINCIPLE_CANDIDATE
SOURCE = SRC-MI1 / adversarial packet source context
FORM = EVOLUTION = CHANGE_OVER_TIME
```

### SN-MI-PC-022

```text
CLASS = PRINCIPLE_CANDIDATE
SOURCE = SRC-MI1 / adversarial packet source context
FORM = GROWTH = desirable subset of change under an applicable evaluation criterion
```

### SN-MI-PC-023

```text
CLASS = PRINCIPLE_CANDIDATE
SOURCE = SRC-MI1 / adversarial packet source context
FORM = MORE_EXPERIENCE != AUTOMATIC_GROWTH
```

Potential non-growth changes named in source:

```text
memory poisoning
drift
corruption
rigidity
harmful bias
unnecessary complexity
unhealthy dependence
```

---

# H. Persona self-description / self-model vs observed behavior

### SN-MI-RISK-008

```text
CLASS = RISK_CLAIM
SOURCE = SRC-MI1 deep-search synthesis
STATEMENT = Persona self-description may diverge from observed behavior; self-model should not be treated as ground truth merely because the Persona asserts it.
```

### SN-MI-M-013

```text
CLASS = MODEL_CANDIDATE / EVALUATION_COMPARISON
SOURCE = SRC-MI1
COMPARE = [PERSONA_SELF_DESCRIPTION, OBSERVED_BEHAVIOR, SUPPORTING_MEMORY_EVIDENCE, OWNER_AUDIT_INTERPRETATION]
```

### SN-MI-OQ-011

```text
CLASS = OPEN_QUESTION
SOURCE = SRC-MI1
QUESTION = How should Persona self-model be represented and tested against behavior/evidence without treating external evaluators as unquestionable truth?
```

---

# I. Experience products may diverge by representation

### SN-MI-H-016

```text
CLASS = WORKING_HYPOTHESIS
SOURCE = SRC-MI1
STATEMENT = Experience may produce multiple memory/state products rather than one biography-like text representation.
PRODUCT_CANDIDATES = [episodic history, semantic knowledge, procedural skill, preference/heuristic, relationship understanding, personality-like disposition]
```

### SN-MI-PC-024

```text
CLASS = PRINCIPLE_CANDIDATE
SOURCE = SRC-MI1
STATEMENT = Persona Memory should not be assumed to be all-natural-language biography.
```

### SN-MI-OQ-012

```text
CLASS = OPEN_QUESTION
SOURCE = SRC-MI1
QUESTION = Which learned products should remain linked to episodes versus materialize as reusable function/skill/state?
```

---

# J. Edge / cloud disclosure and projection

### SN-MI-H-017

```text
CLASS = WORKING_HYPOTHESIS
SOURCE = SRC-MI1
STATEMENT = External cloud compute may receive only task-relevant projected context rather than direct access to the entire long-term Persona memory vault.
```

### SN-MI-PC-025

```text
CLASS = PRINCIPLE_CANDIDATE
SOURCE = SRC-MI1
STATEMENT = Influence from external compute does not itself equal governance over durable Persona state.
```

### SN-MI-OQ-013

```text
CLASS = OPEN_QUESTION
SOURCE = SRC-MI1
QUESTION = Which user-side projection/redaction functions are needed to minimize unnecessary memory disclosure while preserving useful external reasoning?
```

---

# K. Product-side Audit Persona terminology

### SN-MI-TERM-001

```text
CLASS = TERMINOLOGY_GUARD
SOURCE = SRC-MI1 / adversarial packet source context
STATEMENT = Product-side Audit Persona/function != AAA-VALIDATION-AUDITOR
```

### SN-MI-RISK-009

```text
CLASS = RISK_CLAIM
SOURCE = SRC-MI1 / RED sources
STATEMENT = A product-side Audit Persona sharing model/provider/common-memory/root assumptions does not gain independence merely from its label or role prompt.
```

---

# L. Source-derived architecture/research route boundaries

### SN-MI-PC-026

```text
CLASS = AUTHORITY_FIREWALL
SOURCE = SRC-MI0
STATEMENT = ASA-MI research proposition != authorized AAA Requirement
```

### SN-MI-PC-027

```text
CLASS = AUTHORITY_FIREWALL
SOURCE = SRC-MI0
STATEMENT = Whitepaper source insight may create a proposition/requirement candidate but does not automatically create authorized Requirement or Design Contract.
```

### SN-MI-PC-028

```text
CLASS = PRINCIPLE_CANDIDATE
SOURCE = SRC-MI0
STATEMENT = Memory/Identity research should not become an unrelated project-global hold.
FORM = LOCAL_BLOCKER != PROJECT_GLOBAL_HOLD
```

---

# M. Parking-lot statements requiring tomorrow's classification rather than loss

These source-derived statements are intentionally retained without forcing exact class assignment tonight.

```text
PL-001 = 'Memory lifetime > model lifetime' — design intent vs hypothesis vs requirement candidate?
PL-002 = 'Persona may be deeply integrated yet remain externally defined' — relational-status principle vs product semantics?
PL-003 = 'User-defined meaning != user-defined reality' — Whitepaper principle potentially relevant to memory/self-model.
PL-004 = 'Long use != capture' — provider/retention principle candidate.
PL-005 = 'Persona can become valuable without provider owning the relationship asset' — commercial/design intent candidate.
PL-006 = 'One high-quality adaptive agent may outperform multi-Persona architecture' — counter-hypothesis preserved from adversarial source.
PL-007 = 'Long-term memory may be more dangerous than helpful' — counter-hypothesis preserved from adversarial source.
PL-008 = 'Local sovereignty may be mostly illusory if high-quality cognition remains centralized' — counter-hypothesis preserved from adversarial source.
PL-009 = 'Audit + governance may create false security' — counter-hypothesis preserved from adversarial source.
PL-010 = 'PCS-SHAI may reproduce cognitive concentration it seeks to prevent' — founding counter-hypothesis/falsification candidate.
```

The next tagging session can either promote these into typed objects or leave them in the parking lot with a reason.
