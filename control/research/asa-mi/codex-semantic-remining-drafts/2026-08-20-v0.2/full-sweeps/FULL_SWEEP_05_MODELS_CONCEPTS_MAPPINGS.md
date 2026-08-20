# FULL_SWEEP_05 — Models, concepts, and mappings

## Receipt

```text
PASS_ID = FULL_SWEEP_05
PURPOSE = Recover competing models and mappings, including models that reuse the same vocabulary with different causal commitments.
START_TIME = 2026-08-20T07:18:45+09:00
END_TIME = 2026-08-20T07:19:24+09:00
ACTIVE_REVIEW_SECONDS = 39
SOURCE_FILES_OPENED = all 18 repository-visible ASA-MI source files
SOURCE_FILE_COUNT = 18
SOURCE_BYTES_CONSIDERED = 198964
SOURCE_SET_SHA256 = a0a4aea24d5a7432a4286d1eac21cb1720b5d5aed463ccc6a861ab402374dd23
RAW_PRIMARY_SOURCE_VERIFICATION = NOT_PERFORMED
```

## Model families recovered from source text

### Identity bearer models

1. **Strong Memory identity** — the deliberately strong `Identity ?= Memory` falsification target.
2. **Current-state construction** — a present instantiated state constructs continuity by recognizing remembered history as its own.
3. **Memory-centered emergence** — durable memory plus organization, lineage, experience, standpoint, and dispositions produces substantive identity.
4. **Necessary-not-sufficient Memory** — Memory is required but cannot alone determine Persona identity.
5. **Continuity support** — Memory supports continuity without constituting identity.
6. **Multi-component emergence** — relations, lineage, commitments, dispositions, self-model, and governance state remain independently constitutive.
7. **Multi-dimensional continuity** — abandon one boolean and evaluate independently varying continuity dimensions.
8. **Versioned process** — model Persona as a succession/process relation rather than a persisting bearer.

These are not lexical variants. They disagree about what bears identity, what is causally necessary, and whether identity is even a single-valued predicate.

### Memory representation models

9. **Data/record model** — episodic, semantic, relational, and procedural stored products.
10. **Governed durable state model** — Memory includes organized state, provenance, lineage, and lifecycle semantics.
11. **Functional mapping model** — `M : Context -> Value`, with constancy/variability derived over a declared boundary.
12. **Reference/relational model** — a Persona-memory relation can bind an external object without localizing its target content.
13. **Procedure/binding model** — acquired function, function binding, or reusable result may be procedural Memory.
14. **Disposition model** — learned preference, heuristic, risk stance, or relationship interpretation may be a non-biographical Memory product.
15. **Self-model model** — a representation of the Persona may be Memory, derived state, or optional view.
16. **Reconstruction-policy model** — retrieval/compiler policy may itself be identity-bearing Memory, or a distinct co-determinant.

### Current-state models

17. **Persisted rich status** — current Persona-relevant state is materialized as a canonical snapshot.
18. **Minimal bootstrap status** — persist only what is needed to find/reconstruct the rest.
19. **Derived status** — compute Current Status from Memory, Self, Time, and Context.
20. **Hybrid status** — small persisted status plus derived view, references, and cache.
21. **Current operator** — `CURRENT(M)=M(CURRENT_CONTEXT)` makes currentness a relation/evaluation rather than an intrinsic stored type.
22. **Lazy Persona instance** — an instance contains access, operators, environment bindings, and active context without materializing all Memory.

### Reconstruction and portability models

23. **Memory-dominant reconstruction** — governed durable state dominates; runtime is mostly replaceable compute.
24. **Joint causal stack** — behavior depends on state × retrieval × context compilation × model prior × runtime configuration.
25. **Hidden reconstruction owner** — selection/compression policy materially owns what Persona is instantiated.
26. **Behavioral envelope** — continuity is a distribution relative to baseline intra-Persona variance, not exact output equality.
27. **Degraded continuity** — capability can fall sharply while core relational, constraint, retrieval, recording, and export continuity survives.

### History, provenance, and mutation models

28. **Layered history model** — event, evidence, episode, interpretation, derived lesson, and current effect remain distinct.
29. **Canonical-source/derived-index model** — durable history/state is canonical; graphs, vectors, summaries, and embeddings are rebuildable views.
30. **Semantic-index challenge** — derived artifacts may contain irrecoverable judgments and therefore be partly canonical.
31. **Forward/reverse lifecycle model** — candidate→working→durable→consolidated→core and active→dormant→superseded/conflicting→archived→forgotten.
32. **Dependency-invalidation model** — corrections/deletions propagate over derivation relations to address ghost influence.
33. **Three-plane authority model** — evidence, Persona semantic state, and Authority are distinct planes with separately governed transitions.
34. **Trajectory drift model** — aggregate source concentration, promotion, dissent, risk, and migration-resistance changes over time.

### Plurality and relationship models

35. **Shared evidence / separate interpretation** — common origin without common conclusion.
36. **Shared interpretation model** — common meanings/heuristics propagate, with convergence risk.
37. **Fission lineage model** — multiple legitimate successors share pre-fission history and then diverge.
38. **Merge reconciliation model** — preserve conflict/provenance and form a reconciled current interpretation.
39. **Merge successor-C model** — merge creates a new successor, not restoration of an earlier unified Persona.
40. **Relational-value model** — retention arises from familiarity/usefulness/relationship, distinct from structural capture.

## Mapping audit

The corpus maps mature CS abstractions to Persona questions, but mapping direction matters:

- `state/object/version/serialization` map to persistence and reinstantiation, not automatically to human identity.
- `self/this/receiver` maps to a context-resolved reference, not automatically to conscious selfhood.
- `cache/materialized view` maps to Current Status alternatives, not proof that status is non-constitutive.
- `reference/locator/binding` maps to Reference Memory, but target identity and snapshot semantics remain unresolved.
- `event sourcing/provenance/dependency graph` maps to history and ghost-influence management, but does not decide privacy or lived meaning.
- `permission/capability` supports Authority separation, while de facto semantic influence remains outside a purely formal permission model.
- `RDF/PROV/SHACL/JSON-LD/SBVR/AIDA/nanopublications` are representation priors, not adopted ontology or source validation.

## Relations newly exposed by this pass

1. Functional Memory `TENSION_WITH` the multi-component causal stack if “Memory” absorbs compiler/runtime.
2. Current-state construction `DEPENDS_ON` an ownership/appropriation relation over remembered history.
3. Multi-dimensional continuity `ALTERNATIVE_TO` one-bit same-Persona evaluation, not necessarily `CONTRADICTS` it.
4. Derived-status model `WEAKENS` the necessity of a canonical rich Current Status but does not refute constitutive present state.
5. Semantic-index challenge `WEAKENS` rebuildable-index claims.
6. History-layer model `CONSTRAINS` deletion and correction claims by requiring layer-specific targets.
7. Dependency-invalidation model `MOTIVATED_BY` ghost influence; it does not prove that influence removal is complete.
8. Behavioral-envelope model `CONSTRAINS` all provider-swap interpretations.
9. Degraded-continuity model `COEXISTS_WITH` large capability loss.
10. Shared-evidence/separate-interpretation `ALTERNATIVE_TO` both full sharing and full isolation.
11. Fission-lineage model `COEXISTS_WITH` multiple legitimate successors and `CONSTRAINS` implicit authority inheritance.
12. Merge successor-C `ALTERNATIVE_TO` reconciliation, not a validated replacement.

## Extraction-QA implications

- A single `MODEL` class conceals whether a record is causal decomposition, ontology candidate, evaluation frame, lifecycle vocabulary, data representation, or governance recommendation.
- Several v0.1 objects with `STATEMENT = CLASS = ...` or `OBJECT_ID = ...` retain the class but lose the model's content entirely.
- Model lists must not be split into one object per dimension when the source asserts the list as a comparative model.
- Conversely, statements with independent truth conditions—such as portability, behavioral compatibility, and provider independence—must not be merged into one “portability” claim.

## Materiality judgment

No new source-derived object is counted. The material work is the recovery of 40 distinguishable model variants and 12 relation candidates whose semantics cannot be inferred from shared class labels.
