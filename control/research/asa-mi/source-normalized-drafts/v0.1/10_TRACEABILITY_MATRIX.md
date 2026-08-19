# ASA-MI Source-Normalized Draft Traceability Matrix v0.1

```text
ARTIFACT_CLASS = META_INDEX / TRACEABILITY_MATRIX
SOURCE_SET = [SRC-WP1, SRC-WP2, SRC-MI0, SRC-MI1, SRC-R1, SRC-R2, SRC-R3]
OBJECT_SET_STATUS = PROVISIONAL EXTRACTION IDS
PURPOSE = TRACE SOURCE → OBJECT → CLUSTER → FUTURE TAGGING
```

## 1. Source → normalized file mapping

| Source | Normalized target | Primary content |
|---|---|---|
| SRC-WP1 | `02_WHITEPAPER_SOURCE_OBJECTS.md` | Persona/Model separation, Persona State, lifecycle, memory promotion, authority/mutation firewalls |
| SRC-WP2 | `02_WHITEPAPER_SOURCE_OBJECTS.md` | Reality-first, unknown-friendly, Self/Boundary relation, history/meaning, evolution, optionality/falsifiability |
| SRC-MI0 | `03_ASA_MI_PLANNER_SOURCE_OBJECTS.md` | Owner proposition, lifecycle, origin classes, authority separation, core research questions |
| SRC-MI1 | `03_ASA_MI_PLANNER_SOURCE_OBJECTS.md` | planner synthesis, reconstruction, common/local, forgetting, portability, fission/merge, experiments |
| SRC-R1 | `04_RED_I_SOURCE_OBJECTS.md` | state/data-plane counter-theses, identity alternatives, convergence, canonical state, kill tests |
| SRC-R2 | `05_RED_II_SOURCE_OBJECTS.md` | reconstruction/runtime causal decomposition, compiler/retrieval/model/provider portability |
| SRC-R3 | `06_RED_III_SOURCE_OBJECTS.md` | provenance authority, compositional drift, Authority continuity, Audit, ghost influence, control |

## 2. Topic → source coverage

| Topic | WP1 | WP2 | MI | R1 | R2 | R3 |
|---|---:|---:|---:|---:|---:|---:|
| Identity ?= Memory | adjacent | reality constraint | primary proposition | strong attack | runtime sufficiency attack | control consequences |
| Process discontinuity | lifecycle/recovery | plural/process openness | explicit candidate | accepts as researchable | reconstruction focus | control after reconstruction |
| Persona != Model | yes | retained | yes | survives as design principle | strongly stress-tested | provider mutation risk |
| Memory taxonomy | yes | adjacent | extensive | force separation | reconstruction layers | authority/origin layers |
| History vs interpretation | yes | strong | strong | strong | summary/cache consequence | correction/ghost influence |
| Common/local memory | limited | plurality context | primary candidate | convergence attack | runtime sharing effects | propagation/control attack |
| Reconstruction | recovery | survivability | central problem | hidden-owner risk | primary domain | reconstruction receipt/control interface |
| Forgetting/deletion | open | history/meaning tension | functional forgetting | differentiated operations | runtime retrieval effects | ghost influence/dependency |
| Fission | clone/fork | plurality | candidate | survives operationally | runtime portability | Authority inheritance control |
| Merge | limited | open plurality | candidate/defer | new-successor countermodel | runtime reconciliation open | new Authority binding candidate |
| Provider replaceability | strong | sovereignty/optional | strong intent | state not sufficient | primary stress test | hidden provider/control risk |
| Local degraded mode | survivability adjacent | optionality | strong target | plausible | plausible degraded | authority contraction |
| Authority separation | strong | strong | strong | strongly survives | separate runtime references | primary control domain |
| Audit independence | strong concern | anti-monoculture | product Audit idea | same-root attack | independent reconstruction route | same-root/control-failure attack |
| Anti-convergence | cognitive plurality | protocol falsifiability | common-memory risk | primary attack | indirect runtime correlation | shared-interpretation propagation |
| Human burden | usability | user-defined governance | low-manual-memory intent | product concern | runtime complexity | approval-density concern |
| Relational retention | user value | capture risk | explicit product intent | cognitive exit attack | portability distinction | trust/persuasion risk |

## 3. Major source claims with opposing/challenging objects

### Identity / Memory

```text
SN-MI-H-001
  CHALLENGED_BY = [SN-R1-CH-001, SN-R1-ALT-001..006, SN-R2-CH-001]
  CONSTRAINED_BY = [SN-WP1-M-001, SN-WP2-PC-003]
  CONTROL_SEPARATION = [SN-R3-PC-002]
```

### Canonical durable memory/history

```text
SN-MI-H-006 + SN-MI-H-007
  SUPPORTED_BY = SN-R1-PC-001
  CHALLENGED_BY = [SN-R1-OQ-002, SN-R1-OQ-003]
  RUNTIME_CONSEQUENCE = SN-R2-PC-005
```

### Current Persona reconstruction

```text
SN-MI-H-008
  REFINED_BY = [SN-R2-M-003, SN-R2-M-004]
  CHALLENGED_BY = [SN-R1-RISK-003, SN-R2-RISK-001, SN-R2-RISK-002]
  CONTROL_INTERFACE = SN-R2-INTERFACE-001
```

### Common Memory

```text
SN-MI-H-005 + SN-MI-M-006
  CHALLENGED_BY = [SN-MI-RISK-004, SN-R1-RISK-002, SN-R3-RISK-009]
  ALTERNATIVE_CANDIDATE = [SN-R1-H-003, SN-R3-H-007]
  TEST = SN-R1-EXP-004
```

### Functional forgetting

```text
SN-MI-H-009
  REFINED_BY = SN-R1-M-001
  SOVEREIGNTY_RISK = SN-R1-RISK-006
  GHOST_INFLUENCE_RISK = SN-R3-RISK-003
  DEPENDENCY_CANDIDATE = SN-R3-H-002
```

### Provider replacement

```text
SN-WP1-PC-003 + SN-MI-PC-008..011
  EMPIRICAL_LIMIT = [SN-R1-PC-003, SN-R2-FIND-004, SN-R2-FIND-008]
  HIDDEN_OWNER_RISK = [SN-R1-CH-006, SN-R2-RISK-006]
  TESTS = [SN-R1-EXP-001, SN-R2-EXP-003, SN-R2-EXP-007, SN-R2-EXP-009]
```

### Authority separation

```text
SN-WP1-PC-004 + SN-WP2-PC-005 + SN-MI-PC-012
  SURVIVAL_SUPPORT = SN-R1-PC-006
  REFINED_BY = [SN-R3-PC-002, SN-R3-PC-010, SN-R3-H-003]
  OPEN = [SN-MI-OQ-007, SN-R3-OQ-002]
```

### Audit Persona

```text
source product idea
  CHALLENGED_BY = [SN-R1-RISK-007, SN-R3-RISK-004]
  PRINCIPLE = [SN-R1-H-008, SN-R3-PC-012, SN-R3-PC-013]
```

## 4. Objects likely to need later link to live-brainstorm model

This is a **traceability placeholder only**; no semantic links are pre-applied.

```text
Memory semantics cluster          → later M(Context)→Value model
Current / current status cluster  → later CURRENT as evaluation operator
Self / Boundary cluster           → later SELF as context/runtime selector hypothesis
stability/lifecycle cluster       → later Boundary + Change Rate + Transition Condition formulation
reference/index cluster           → later external URL/reference-as-memory discussion
procedural expertise cluster      → later function/member/function-binding discussion
CS legacy cluster                 → later USE_CS_PRIOR → MAP_TO_PERSONA → IDENTIFY_DELTA method
philosophy/reality cluster        → later human-reality grounding / abstraction-intent principle
```

These links must be tagged in the next session rather than silently inferred now.

## 5. Objects carrying explicit source status that must not be overwritten

Examples:

```text
SN-R1-CH-001 = REJECTED BY COUNTERFORCE (source status only)
SN-R1-H-001 = SURVIVED CURRENT ATTACK (source status only)
SN-R2-FIND-004 = NOT_PROVEN
SN-R2-FIND-008 = NOT_PROVEN
SN-R3-PC-010 = RED-III default/recommendation, not Owner decision
SN-MI-H-001 = unconfirmed working proposition, not scientific fact
SN-WP2 objects = revision proposal / partial owner review, not normative AAA authority
```

A later current-research tag may differ, but the historical source status should remain available.

## 6. Traceability integrity rules

```text
NORMALIZED_OBJECT must identify SOURCE_ID.
SOURCE_STATUS must not be upgraded during normalization.
COUNTERFORCE_VERDICT != VALIDATION_VERDICT.
SOURCE_AGREEMENT != INDEPENDENT_EVIDENCE.
LATER_OWNER_TAG != RETROACTIVE_SOURCE_REWRITE.
CURRENT_RESEARCH_STATE != HISTORICAL_SOURCE_STATE.
```

## 7. Coverage gaps intentionally left for later

```text
- Full line-by-line extraction of every Whitepaper proposition is not attempted; this corpus is ASA-MI-relevant extraction.
- External papers cited inside RED outputs are not independently re-verified in this normalization pass.
- Live brainstorming after the sources is deliberately isolated and not merged.
- Exact canonical stable IDs are deferred until tagging/reconciliation.
- No formal Requirement/Design/Control object promotion occurs here.
```
