# SP-08 — Reconstruction, retriever, and context compiler

## Receipt

```text
PASS_ID = SP-08
PASS_PURPOSE = Decompose reconstruction ownership into retrieval, compilation, model interpretation, runtime, and environment contributions.
START_TIME = 2026-08-20T07:38:53+09:00
END_TIME = 2026-08-20T07:39:05+09:00
ACTIVE_REVIEW_SECONDS = 12
SOURCE_FILES_OPENED = MI planner; RED-I; RED-II
SOURCE_FILE_COUNT = 3
SOURCE_BYTES_CONSIDERED = 37008
RAW_PRIMARY_SOURCE_VERIFICATION = NOT_PERFORMED
```

## Causal stack

1. **Canonical/source state** supplies possible evidence and current-state records.
2. **Index/candidate generator** determines what can be retrieved.
3. **Retriever/reranker** scores and excludes candidates.
4. **Context compiler** selects, orders, compresses, labels, and combines selected content with the runtime contract.
5. **Model prior** interprets ambiguity, resolves conflicts, and generates reasoning/action.
6. **Runtime/config/tools/environment** constrain capabilities, bindings, hidden prompts, and observable action.

The source formula is a causal decomposition, not a validated multiplicative equation.

## Hidden-ownership mechanisms

- Excluding rare counterevidence without altering storage.
- Promoting a summary to practical canonical status through repeated priority.
- Compressing conflicts into false consensus.
- Reordering equivalent content so different facts dominate attention.
- Injecting provider-side personalization outside user-state lineage.
- Changing tools/environment so the same procedural binding behaves differently.

## Reconstruction receipt candidate (Codex inference)

A causal audit would need at least candidate-set identity, retrieval/reranking policy version, excluded critical items, compression derivation, context order/budget, runtime contract, model/runtime identifiers, hidden-state limitations, and environment/tool bindings. This is a research instrumentation candidate, not an authorized design.

## Relations recovered

1. Canonical-state integrity `DOES_NOT_IMPLY` reconstructed-state fidelity.
2. Retriever `CONSTRAINS` which history can influence the current instance.
3. Compiler `TRANSFORMS` retrieved material and may add semantic judgments.
4. Model prior `INTERPRETS` compiled context and may resolve ambiguity differently.
5. Runtime binding `CONSTRAINS` procedural expression independently of stored procedure.
6. Summary-as-cache claim `FALSIFIED_IF` deletion makes claimed canonical state unrecoverable.
7. Broad Memory `POSSIBLY_ABSORBS` reconstruction policy, weakening the independence claim.
8. Reconstruction variance `REQUIRES` baseline intra-Persona variance before continuity judgment.

## Double-crux

If changing only the retriever produces a stable Persona-relevant behavioral shift, is the retriever part of Memory, part of Persona, or an external causal dependency? The empirical result alone cannot decide the membership vocabulary; it does refute storage-only sufficiency.

## Materiality judgment

No new source object is counted. The pass preserves six causal stages and instruments the hidden-owner claim without promoting a design.
