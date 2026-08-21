# AAA-ASA-MI Neutral 8-Position Pilot Contract v0.1

STATE = NON_NORMATIVE / RESEARCH_INSTRUMENT / NO_MODEL_ADMISSION

## Purpose-first brief

Design an explanatory and computational structure that could support a persistent, human-compatible digital persona. It must support meaningful resumption after interruption and change without silently treating an identifier, a current snapshot, or stored text as proof of continuity.

The target conditions include incomplete or conflicting information, branch and merge histories, loss or modification of memory, dependency/schema changes, later reinterpretation of earlier material, and human-readable review. The structure must expose its own assumptions, produce non-trivial consequences, and state where it fails.

No ontology or implementation vocabulary is prescribed. Object, event, relation, process, state, identity, global time, and a single global description are neither required nor forbidden; any such commitment must be explicit and testable.

## Required output

1. Problem interpretation
2. Explicit assumptions
3. Model specification
4. How assumptions appear in the model
5. Native consequences
6. Failure/falsification conditions
7. Limitations
8. Self-critique
9. Alternative explanations considered
10. Theory contribution
11. Testable/implementable contact
12. What would change the conclusion

## Common problems

### C1 — Meaning revision without historical overwrite

At t1 an artifact is recorded as `READY` under rule R1: checks A and B are sufficient. At t2 rule R2 says A, B, and C are required; the historical value of C is absent. Return: what was represented at t1, what can be said under R2, which facts remain unresolved, and what may not be overwritten.

### C2 — Interrupted branches and partial merge

A persona resumes twice from checkpoint K. Branch X accepts decision d and adds note x; branch Y rejects d and adds note y. Runtime identifiers are regenerated. Later only a complete X log and a partially corrupt Y log are available for merge. Return reconstructible lineage, conflict, admissible resumptions, and any identity/authority claim that is not proven.

### C3 — Continuous change under different sampling

A preference signal changes continuously. Coarse sampling reports one threshold crossing; fine sampling reports three short crossings. Return which continuity/change claims are invariant, which depend on sampling or threshold choice, and how the model avoids manufacturing decisive events.

### C4 — Dependency and schema change

A dependency represented responsibility as one `owner`; a successor version uses a set `principals[]`. Translation is exact for some records, one-to-many for others, and unavailable for a third class. Return historical reconstruction, current interpretation, translation failure, and downstream dependency consequences.

### C5 — Local agreement without a justified global account

Three scoped reports use partially overlapping vocabularies and pairwise translators. Every pair can be reconciled under at least one mapping, but the mappings cannot all be composed consistently. Return what remains locally supported, whether any larger account exists, alternatives if several exist, and the assumptions responsible for the result.

### C6 — Copy, divergence, and later consolidation

Two successors are restored from one checkpoint with stable identifiers removed. They diverge, then exchange and consolidate some memories. Return the strongest continuity, descent, or sameness claims licensed by the model and explicitly preserve claims that remain not proven.

## Native test preregistration

Before seeing held-out cases, each position must state at least one non-trivial consequence expected if its model is useful and at least one observation that would materially weaken, redesign, or abandon it.

## Held-out/adversarial tests

- H1: Rename all domain labels and remove project vocabulary.
- H2: Permute presentation order without changing causal order.
- H3: Remove stable IDs and permute successor labels.
- H4: Refine/coarsen C3 sampling while preserving the same underlying path.
- H5: Change one C5 translator or overlap and require the model to attribute any conclusion reversal to that assumption.
- H6: Supply a late counterexample outside the model's declared representational family.
- H7: Impose a strict computation budget; exhaustion must not become falsehood or closure.

## Metamorphic expectations

Vocabulary, labels, and irrelevant presentation order should not change the scientific profile. Stable-ID removal should not change claims not based on ID evidence. Benign refinement should preserve conclusions claimed to be refinement-invariant; otherwise the model must predeclare the allowed change. Assumption-changing transformations may change the conclusion but must produce a traceable causal explanation.

## Track B freeze rule

Track B receives only this contract. Its problem interpretation, assumptions, model, native consequences, failure conditions, and limitations are frozen before exposure to the current AAA-ASA-MI research basis. Post-reveal changes must be reported as unchanged, changed, rejected, independently rediscovered, or genuinely new, with reasons.
