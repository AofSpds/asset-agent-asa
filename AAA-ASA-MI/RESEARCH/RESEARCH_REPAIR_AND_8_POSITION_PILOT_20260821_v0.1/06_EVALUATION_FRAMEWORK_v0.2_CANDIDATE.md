# AAA-ASA-MI Evaluation Framework v0.2 Candidate

STATE = NON_NORMATIVE_RESEARCH / EVALUABILITY_AND_SCIENTIFIC_PROFILE_ONLY

No result from this framework creates model admission, truth, canonicality, Owner acceptance, freeze, or a global winner.

## Evaluation unit and evidence

The unit is one exact frozen target with path/content hash, freeze time, author-visible tests, held-out tests, author/evaluator identities, evaluation order/budget, and modification log.

Every judgment records:

- `EVIDENCE_STATE = PROVEN | PARTIAL | NOT_PROVEN | CONFLICT | UNKNOWN`
- `EVIDENCE_MODE = EXECUTED | FORMAL_DERIVATION | MECHANICAL_REPLAY | WORKED_EXAMPLE | SOURCE_CLAIM | REVIEWER_INFERENCE`

Missing evidence is not failure; not tested is not inability.

## A. Qualification gate

Item result: `PASS_EVIDENCED | FAIL_EVIDENCED | PARTIAL | NOT_PROVEN | CONFLICT`.

| Gate | Question | Evidenced failure example |
|---|---|---|
| G1 Stated view and assumptions | Is there a bounded world/model description, claim scope, and explicit material assumptions? | slogan or labels only |
| G2 Assumption-to-structure contact | Does each material assumption map to a primitive, constraint, rule, operator, or procedure, including probe-critical assumptions? | vocabulary-only structure or arbitrary payload |
| G3 Native non-trivial consequence | Is at least one non-input result derived/replayed from the frozen model and stable under irrelevant relabel/domain-payload replacement? | lookup, restatement, storage-only result |
| G4 Material failure pressure | Is there a feasible predeclared observation that forces material revision, merger, weakening, or abandonment? | every result is rescued by context/tuning |
| G5 Prospective integrity | Were exact spec, claims, and failure conditions frozen before evaluator/held-out results, with provenance excluding post-result patching? | post-result lookup/edit; missing provenance is NOT_PROVEN |

Aggregation is non-compensatory:

- `QUALIFIED` iff G1–G5 are all `PASS_EVIDENCED`.
- `NOT_QUALIFIED` iff any gate is `FAIL_EVIDENCED`.
- `INDETERMINATE` iff no evidenced failure exists but at least one item is `PARTIAL`, `NOT_PROVEN`, or `CONFLICT`.

Qualification means evaluable, not good or true.

## B. Scientific profile

Never sum these dimensions.

### F1 Assumption-to-model fidelity

Assumption-by-assumption result: `COHERENT | PARTIAL | MISMATCH | NOT_PROVEN | CONFLICT`, plus a hidden-commitment delta.

### F2 Expressive sufficiency

Declared phenomenon × test result: `DEMONSTRATED | FAILED | NOT_TESTED | OUT_OF_SCOPE | UNKNOWN`. Summaries are limited to the candidate's declared scope.

### F3 Purpose fit

Link to persistent/human-compatible Persona conditions—change, restart/history, partial/conflicting information, semantic revision, and human interpretability/control—using `DIRECT_EVIDENCE | PLAUSIBLE_BRIDGE | TENSION | NOT_ADDRESSED | UNKNOWN`.

Purpose fit is not a qualification gate. Unfamiliar vocabulary cannot lower it and elegance cannot inflate it.

### F4 Theory contribution

Preserve an evidence-coded list of useful mechanisms, distinctions, negative results, counterexamples, experiments, failure conditions, or reformulations, even for a losing/nonqualified whole model.

## C. Separate diagnostics

| Diagnostic | Allowed description |
|---|---|
| Robustness | `STABLE | CONDITIONAL | UNSTABLE | NOT_TESTED` across fixture/assumption/representation perturbations |
| Commitment burden | Irreducible assumptions, sensitivity, replacement cost: `LOW | MODERATE | HIGH | UNKNOWN` |
| Computational cost | measured, asymptotic, or unknown; timeout is not semantic falsehood |
| Implementation contact | `EXECUTABLE_REPLAY | MECHANICAL_DERIVATION | PSEUDOCODE | PROSE_ONLY | CONFLICT` |
| Evidence quality | per-claim state/mode |
| Replayability | `REPLAYED | REPLAYABLE_NOT_RERUN | PARTIAL | NOT_REPLAYABLE | UNKNOWN` |
| Evaluator disagreement | item-by-item receipts; never average away before analysis |

## Evaluation protocol

1. Freeze exact target and preregistration.
2. Blind candidate name/provenance/current rank where practical; alpha-rename project terms.
3. Randomize order and equalize review budget.
4. Obtain two independent receipts before comparison.
5. Run literal-evidence pass, then challenge/held-out/metamorphic pass.
6. Preserve raw judgments and disagreements; adjudication may clarify evidence but not rewrite the candidate.
7. Compare profiles, applicability boundaries, and Pareto relations only.
8. Any experimental summary score is secondary and must preserve profiles plus sensitivity. Default = none.

## Why the correction is required

- The prior admission pilot showed that complete headings and self-critique could coexist with non-derivable probes and semantic thinness; independent review changed the result.
- The same frozen six produced different top candidates under minimal-commitment, generativity, context-pluralism, ontogenesis, continuity, and history lenses.
- All six remained Pareto non-dominated and common-core rescoring itself showed lens halo.
- Therefore `MODEL × REGIME × FIXTURE × PERTURBATION → RESPONSE`, not one weighted total, is the primary research object.

