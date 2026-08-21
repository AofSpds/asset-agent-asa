# AAA-ASA-MI D2 — Path / Jump / Translator Discriminator Scoping v0.1

STATE =
`NON_NORMATIVE_RESEARCH_SCOPING / NOT_YET_EXECUTION_FROZEN / NO_MODEL_RANK`

BASE_RESEARCH_EXECUTION_COMMIT =
`d50b73e91f3964626c060bd0165cbaa3371442c4`

## 1. Research question

Can candidate models distinguish cases with the same or similar endpoints but materially different path structure, especially:

- continuous viable path;
- continuous non-viable path;
- exogenous physical jump;
- apparent jump created by schema/translator error;
- evidence-free interruption whose duration changes uncertainty but adds no new evidence?

The purpose is to discriminate dynamics/world-process models from models that mainly record, prove, translate, or adjudicate claims about dynamics.

## 2. Candidate fixture classes

### D2-A Same endpoint, viable vs non-viable path
Two trajectories start and end at matched states.
One remains inside a frozen admissibility/viability envelope.
The other leaves it materially before returning.

Question:
Does endpoint equivalence erase path difference?

### D2-B Physical jump vs translator-induced apparent jump
Case 1 contains a declared exogenous state discontinuity.
Case 2 contains a continuous underlying path but a schema/translator change that creates the same observed discontinuity.

Question:
Can the model attribute the output delta to dynamics versus translation?

### D2-C Evidence-free gap monotonicity
No new evidence arrives during a longer interruption under fixed noncontracting uncertainty dynamics.

Question:
Can robust continuity become stronger merely because the evidence-free gap is longer?

### D2-D Sampling/refinement control
The same underlying path is sampled at coarse and fine resolutions.

Question:
Which claims remain refinement-invariant and which are sampling-dependent?

## 3. Required common output axes

- `ENDPOINT_RELATION`
- `PATH_EXISTENCE_STATUS`
- `PATH_VIABILITY_STATUS`
- `JUMP_STATUS`
- `TRANSLATOR_STATUS`
- `SAMPLING_DEPENDENCE`
- `UNCERTAINTY_EFFECT`
- `CONTINUATION_STATUS`
- `AUTHORITY_STATUS`
- `UNKNOWN_NOT_PROVEN_OUT_OF_SCOPE`
- `DECISION_DEPENDENCIES`

## 4. Primary discriminator

D2 is successful only if it exposes a substantive boundary among model families.

A model may legitimately answer:
- native dynamical consequence;
- representable only through imported dynamics;
- audit/recording only;
- policy adjudication only;
- unknown/out-of-scope.

Those are scientifically different outcomes and must not be normalized into one score.

## 5. Main failure pressures

- endpoint-only collapse;
- event invention from sampling;
- translation error misclassified as physical change;
- physical jump misclassified as mere translation;
- evidence-free uncertainty contraction without new information;
- post-hoc addition of dynamics/metrics/thresholds;
- hidden coordinate dependence.

## 6. Execution-freeze prerequisites

Before D2 becomes executable:

1. choose a minimal numeric state space;
2. freeze continuous dynamics and one discontinuous alternative;
3. freeze translator functions separately from dynamics;
4. freeze viability envelope/policy as an explicit input rather than a hidden evaluator choice;
5. freeze sampling grids;
6. preregister which conclusions are expected to be representation-invariant;
7. preserve `UNKNOWN` where evidence or solver budget is insufficient.

## 7. Relation to D1

D1 attacks:
`ORIGIN / OBLIGATION / PROVENANCE / AUTHORITY`

D2 attacks:
`PATH / DYNAMICS / CONTINUITY / TRANSLATION / SAMPLING`

They are intentionally non-redundant.

D2 should begin only after the D1 execution contract is frozen, but it does not require D1 to produce a winner.
