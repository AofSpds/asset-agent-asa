# FULL_SWEEP_04 — Open questions and uncertainties

## Receipt

```text
PASS_ID = FULL_SWEEP_04
PURPOSE = Recover every unresolved boundary, ambiguity, and question without converting it into a premature answer.
START_TIME = 2026-08-20T07:16:02+09:00
END_TIME = 2026-08-20T07:17:29+09:00
ACTIVE_REVIEW_SECONDS = 87
SOURCE_FILES_OPENED = all 18 repository-visible ASA-MI source files
SOURCE_FILE_COUNT = 18
SOURCE_BYTES_CONSIDERED = 198964
SOURCE_SET_SHA256 = a0a4aea24d5a7432a4286d1eac21cb1720b5d5aed463ccc6a861ab402374dd23
RAW_PRIMARY_SOURCE_VERIFICATION = NOT_PERFORMED
```

This pass began again at source text. The v0.1 object registry was queried only after the reread, to test whether candidate questions were already represented.

## Recovered uncertainty map

### Identity and continuity

1. Is Memory necessary, sufficient, primary, supportive, or merely one measurable continuity dimension?
2. Does “recognizes past as its own” require actual causal lineage, accurate provenance, behavioral uptake, first-person attribution, or some combination?
3. Can a coherent but false autobiography manufacture the same operational continuity signal as a causally real history?
4. Is a single same-Persona judgment useful, or should identity judgments remain a vector over memory, lineage, relation, disposition, standpoint, reconstruction, and model/runtime continuity?
5. How much memory loss remains compatible with continuity, and which retained memories can coexist with material Persona replacement?
6. What observation would weaken `Identity ?= Memory` without merely redefining Memory to absorb the counterexample?

### Memory membership and typing

7. What makes accessible data a bound Persona-memory relation rather than ordinary reachable information?
8. Is Status Memory, an output of Memory, a cache over Memory, or a separately governed current state?
9. Which experience products remain episodes, and which become semantic knowledge, procedures, relations, heuristics, dispositions, or self-model state?
10. Is an executable function Memory, a learned capability, a runtime primitive, or Memory only when a Persona-specific binding/selection/history exists?
11. Can a function that mutates Memory or its transition rules itself be a Memory member without creating a recursive ownership problem?
12. What are the identity semantics of a reference: locator identity, target identity, content snapshot identity, binding identity, or remembered observation?
13. Which lifecycle states are conceptual Memory semantics and which are implementation-specific retrieval/storage states?

### Current, Self, and context

14. What makes two contexts equivalent for `M(Context) -> Value` when irrelevant fields differ?
15. Which Context dimensions are global, function-local, projected, latent, or supplied by runtime?
16. Does `CURRENT(M)` need a persisted temporal anchor, or is “current” wholly an evaluation relation supplied at instantiation?
17. Which Current Status dimensions are canonical, derived, cached, runtime-bound, reference-only, or unnecessary?
18. Can a Persona have a Self relation without any materialized self-model, and what behavior would discriminate those cases?
19. If self-model and observed behavior conflict, what evidentiary procedure adjudicates without treating either Persona assertion or external evaluator as ground truth?

### Canonical state and reconstruction

20. What exactly is canonical: raw event, evidence, source text, normalized record, current interpretation, semantic state, lineage, or a multi-layer package?
21. Does preservation of bytes preserve semantics when the future reconstruction model changes?
22. Which graph/index/embedding artifacts contain irrecoverable semantic choices rather than rebuildable retrieval conveniences?
23. At what point does a derived summary/cache become hidden canonical state?
24. Which reconstruction semantics must remain stable across retriever, compiler, model, and provider changes?
25. Should a minimal standpoint/commitment state be persisted to reduce reconstruction dependence, and what does that persistence freeze incorrectly?
26. How can hidden provider prompts, personalization, or silent version drift be detected as extra-canonical influence?

### Change, learning, forgetting, and deletion

27. Is `CHANGE_RATE` value derivative, transition frequency, hazard, or a family of non-comparable measures?
28. How are transition conditions composed, scoped, overridden, and versioned?
29. What distinguishes `REMEMBER(E)` from `LEARN(E)`, and can either occur without the other?
30. How is legitimate evolution separated from harmful drift without freezing an old Persona?
31. Which forgetting operation is meant in each claim: decay, inaccessibility, dormant state, supersession, compression, archival, deletion, or erasure?
32. How far must deletion/correction propagate through derived dependencies before “ghost influence removed” is a defensible claim?
33. How can history integrity and privacy deletion coexist without collapsing evidence, active memory, and current interpretation?

### Sharing, portability, authority, and human meaning

34. What may move from Persona-local to Common Memory, and can any interpretation be shared without unacceptable convergence?
35. What continuity envelope is adequate after model/provider migration, distinct from capability parity and exact output equality?
36. What user-side functions can govern stronger external computation without local reasoning parity?
37. When does Persona change invalidate a prior grant, and how can authority contract without silently treating Memory as Authority?
38. What makes an evaluator meaningfully independent when recursive evaluation eventually shares evidence, ontology, incentives, or models?
39. Which observable signals distinguish valuable familiarity from manipulation, lock-in, or harmful dependency?
40. Which human-perceived continuity signals track structural fidelity rather than fluent imitation?

## Residual questions not cleanly objectized in v0.1

The registry already contains most explicit questions above. Five cross-cutting residuals were present as implications or clauses rather than clean standalone questions:

- What makes appropriation of a remembered past as “my history” warranted rather than merely coherent?
- What equivalence relation over Context is required before functional Memory can be empirically compared?
- When does Reference Memory materially promote into current constitutive Status, and who/what performs that promotion?
- What closure criterion would justify claiming that deletion removed derived influence?
- How is evaluator independence evaluated without an infinite regress to another evaluator sharing the same conceptual frame?

These are recorded as ambiguities, not counted as new source claims. They may become Codex-inferred open-question candidates only in the separated inference stage.

## Source-layer conflicts requiring owner semantic judgment

- Historical `MEMORY != CURRENT STATE` versus the live possibility that Status is a Memory value/type.
- Whitepaper `Persona State is not a memory dump` versus live broadened functional Memory.
- Current Status as stored canonical state versus derived view/cache/hybrid.
- Strong Identity–Memory hypothesis versus memory-as-support, memory-necessary-only, multi-component, and multi-dimensional accounts.
- Reconstruction/runtime as independent Persona contributors versus mechanisms internal to a broad Memory function.
- Historical integrity versus deletion and owner sovereignty.
- Same-origin shared evidence versus anti-convergence and reviewer independence.
- Fission as multiple legitimate successors versus same-Persona language; Merge as reconciliation versus new successor C.

## QA finding

An object may accurately reproduce a question string yet still lose the question's candidate set, motivation, or falsification boundary. v0.1 QA must therefore review `SOURCE_RECORD_TEXT` and surrounding source context, not just compare `STATEMENT` to a question field.

## Materiality judgment

No new source-derived object is counted in this pass. The material result is a 40-question uncertainty map, five residual cross-cutting ambiguities, and eight explicit double-crux families. Preserving them as unresolved is more faithful than quota-driven object creation.
