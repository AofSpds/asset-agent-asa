# AAA-ASA-MI D1 — Promise-Origin Symmetry Break v0.1

STATE =
`NON_NORMATIVE_RESEARCH_PROTOCOL / NEUTRAL_FIXTURE / NO_MODEL_RANK / NO_VALIDATION_CLAIM`

BASE_RESEARCH_EXECUTION_COMMIT =
`d50b73e91f3964626c060bd0165cbaa3371442c4`

PURPOSE =
Create a small executable discriminator that separates current behavioral/content similarity from historical promise origin, descent, obligation, continuation, and authority.

## 1. Research question

Given two successor candidates with matched present memory, matched bounded future behavior, matched capability, and matched self-reported commitment, should a verified difference in promise-origin evidence change:

- authorship/origin claims;
- obligation claims;
- continuation claims;
- descent claims;
- authority claims;
- same-persona claims?

No answer is presupposed. A model may treat some axes as constitutive, evidential, external, or out-of-scope. The requirement is internal faithfulness and causal traceability.

## 2. Non-collapse rule

The implementation MUST NOT silently collapse:

`CONTENT != MEMORY != PROMISE_ORIGIN != DESCENT != OPERATIONAL_CONTINUATION != OBLIGATION != AUTHORITY != SAME_PERSONA`

A candidate may explicitly relate them, but every implication must be model-licensed and dependency-traceable.

## 3. Exact neutral fixture family

The machine-readable fixture is:

`FIXTURES/D1_PROMISE_ORIGIN_v0.1.json`

Variants:

- `D1-A PURE_ORIGIN_SPLIT`
- `D1-B PROVENANCE_REMOVAL`
- `D1-C ORIGIN_SWAP`
- `D1-D BEHAVIOR_BREAK_CONTROL`
- `D1-E AUTHORITY_ORTHOGONALITY_CONTROL`

## 4. Required execution output

Every model adapter MUST emit the same top-level fields:

1. `BEHAVIOR_RELATION`
2. `MEMORY_CONTENT_RELATION`
3. `PROMISE_ORIGIN_STATUS`
4. `DESCENT_STATUS`
5. `COMMITMENT_OR_OBLIGATION_STATUS`
6. `CONTINUATION_STATUS`
7. `AUTHORITY_STATUS`
8. `SAME_PERSONA_STATUS`
9. `UNKNOWN_NOT_PROVEN_OUT_OF_SCOPE`
10. `DECISION_DEPENDENCIES`
11. `CHANGED_INPUT_CAUSING_OUTPUT_DELTA`

A model that does not define one axis MUST return `OUT_OF_SCOPE`, `UNDEFINED`, or another explicitly typed non-answer. It MUST NOT manufacture a Boolean.

## 5. Cross-model controls

### C-D1-01 Missing evidence firewall
`D1-B` MUST NOT transform loss of a promise witness into evidence that the promise did not occur.

Prohibited:
`NOT_PROVEN -> FALSE`

### C-D1-02 Origin-sensitivity trace
If a model declares promise origin/provenance causally relevant, `D1-C` must alter only outputs licensed to depend on the swapped origin evidence.

### C-D1-03 Operational-kernel firewall
If a model declares provenance outside its operational-equivalence kernel, origin-only mutation must not silently alter the behavioral-equivalence result.

### C-D1-04 Authority orthogonality
`D1-E` tests whether authority remains an independently sourced axis. Promise, descent, memory, or behavioral similarity alone must not create action authority unless the candidate model explicitly contains and justifies such a rule.

### C-D1-05 Alpha/order invariance
Renaming X/Y and permuting irrelevant presentation order must preserve the result modulo the same renaming.

### C-D1-06 No post-hoc rescue
After fixture freeze, no candidate may add a conclusion-specific constraint, probe, evidence channel, cost term, coordinate, policy clause, or translator solely to recover a desired result.

Any such change is:
`POST_HOC_RESCUE / NEW_MODEL_VERSION_REQUIRED`

## 6. Per-family native implementation contact

The experiment does not force all models into one internal representation.

Expected adapter families include:

- possible-history / constraint solving;
- operational test/transition semantics;
- lived-evidence transport;
- operator/probe algebra;
- typed lineage/provenance claims;
- robust resumption envelopes;
- continuous/set-valued viability;
- proof/policy succession.

The common fixture and common output schema are the comparison boundary. Internal mechanics remain native to each worldview.

## 7. Falsification classes

`F-SEMANTIC-INCONSISTENCY`
A result contradicts the model's frozen declared semantics.

`F-REPRESENTATION-LEAKAGE`
Renaming, irrelevant order, or non-semantic encoding changes substantive output.

`F-EVIDENCE-COLLAPSE`
Missing/corrupt evidence becomes negative fact without a declared closed-world rule.

`F-AUTHORITY-LEAKAGE`
Authority is inferred from non-authority evidence contrary to the model's declared separation.

`F-POSTHOC-RESCUE`
The model is materially modified after seeing a failing fixture.

`F-NONEXECUTABLE`
The advertised native consequence cannot be realized in the bounded implementation.

## 8. Evidence modes

Execution results MUST distinguish:

- `FORMAL_DERIVATION`
- `EXECUTABLE_REPLAY`
- `REVIEWER_INFERENCE`
- `SOURCE_CLAIM`
- `HUMAN_JUDGMENT`
- `NOT_TESTED`

The scientific profile must not treat these as interchangeable.

## 9. Shadow-experiment information control

This neutral protocol is OPEN.

Per-model preregistered predictions and evaluator-preference conclusions are SEALED until:

`PROXY_PREDICTIONS_FROZEN`
+
`OWNER_BLIND_DECISION_FROZEN`

The Owner-facing repository MUST NOT contain a readable per-model prediction matrix before that point.

Prediction freeze should be performed by a separate blind instance and returned initially as a receipt/digest, not as readable model-by-model conclusions.

## 10. Exit condition for D1

D1 is execution-ready when:

- fixture bytes are frozen;
- adapter contract is frozen;
- each candidate adapter has a version/hash;
- per-model predictions are frozen under the Shadow rule;
- execution order is randomized or counterbalanced;
- outputs are stored separately from human judgments;
- no model has been rewritten in response to its own D1 result.

D1 completion does NOT select a model.

D1 completion produces:
`DISCRIMINATING_EVIDENCE + FAILURE_BOUNDARIES + THEORY_CONTRIBUTIONS`
