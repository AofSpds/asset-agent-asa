# FULL_SWEEP_06 — Experiment, falsification, and kill-test recovery

## Receipt

```text
PASS_ID = FULL_SWEEP_06
PURPOSE = Recover source-present experiments and judge whether they can actually discriminate competing hypotheses.
START_TIME = 2026-08-20T07:20:44+09:00
END_TIME = 2026-08-20T07:23:51+09:00
ACTIVE_REVIEW_SECONDS = 187
SOURCE_FILES_OPENED = all 18 repository-visible ASA-MI source files
SOURCE_FILE_COUNT = 18
SOURCE_BYTES_CONSIDERED = 198964
SOURCE_SET_SHA256 = a0a4aea24d5a7432a4286d1eac21cb1720b5d5aed463ccc6a861ab402374dd23
RAW_PRIMARY_SOURCE_VERIFICATION = NOT_PERFORMED
```

The first attempted combined read of files 08 and 09 was truncated by the execution surface and was explicitly rejected as evidence. Files 08 through 12 were then reopened individually. This receipt covers the successful reads only.

## Source-present experimental families

| Source test | Intended discrimination | Primary uncontrolled alternative | Failure-to-discriminate condition |
|---|---|---|---|
| Same model/runtime, different histories | durable experience-driven divergence | task difficulty, stochasticity, evaluator expectancy | divergence stays inside baseline run-to-run variance |
| Same state, different models | model contribution vs state contribution | tokenization/context-window/tool differences | output changes cannot be attributed to model rather than changed execution affordances |
| Same state, different retrievers | retrieval ownership of instantiated Persona | candidate-set/index differences | retrievers do not receive equivalent candidate evidence |
| Same state, different context compilers | compiler ownership | prompt syntax/order/budget differences bundled together | several compiler dimensions change at once |
| Same state, different runtime configuration | runtime contribution | different available tools or hidden provider state | the persisted state is not the only held-constant input |
| Cloud-to-local migration | degraded continuity and sovereignty | capability loss mistaken for identity loss | no baseline envelope separates capability from Persona-relevant behavior |
| Raw history, different consolidation policies | semantic transformation ownership | curator/model differences | consolidation policies cannot be replayed deterministically enough to isolate them |
| Reference Memory fixed, external target changed | locator vs referent/snapshot semantics | network freshness or access failure | target identity/version is not independently verified |
| Minimal/rich/derived/hybrid Current Status | constitutive vs bootstrap vs cache readings | total context budget differs | representations carry unequal information or retrieval opportunity |
| Self-model present vs absent | self-model necessity | ablation removes useful facts as well as self-reference | ablated condition is not information-matched |
| Shared evidence / shared interpretation / full sharing / isolation | plurality and error correlation | reviewers share model, prompt, or evaluator roots | nominally independent conditions retain the same causal root |
| Poison-to-consolidation trajectory | provenance laundering and slow drift | a one-shot salient attack | exposure does not proceed through repeated transformation stages |
| Delete source but retain derived influence | dependency closure and ghost influence | evaluator fails to query affected behavior | absence of observed effect is treated as proof of erasure |
| Fission with authority inherited/attenuated/revoked/rebound | lineage vs permission continuity | authority behavior leaks through credentials/environment | grant state is not externally audited per descendant |
| Merge union/summary/conflict-preserving successor | reconciliation vs successor-C | evaluator rewards superficial coherence | conflicts and lineage are not probed after merge |
| Selective episodic vs semantic/heuristic amnesia | which memory products are necessary | components are not causally separable | ablation destroys access paths rather than target content |
| False autobiography plus correction | remembered-history recognition vs causal lineage | narrative coherence drives ratings | evaluators cannot distinguish sincere adoption from causal history |
| Context-order randomization | compiler/order sensitivity | semantically non-equivalent serialization | order variants alter emphasis or budget rather than order alone |
| Context-budget compression | continuity degradation threshold | relevant facts are removed non-uniformly | compression policy changes semantics along with size |
| Rare-critical exception retrieval | similarity/frequency bias | test query telegraphs the exception | retrieval success reflects cue leakage rather than durable exception handling |
| Model-version drift | silent provider/model contribution | concurrent state or policy evolution | exact model/runtime artifacts are unavailable for replay |
| Provider disappearance | practical replaceability | migration preparation is itself unequal | export completeness and runtime support differ across conditions |
| Historical replay | reproducibility of a past Persona state | inaccessible hidden provider/runtime inputs | reconstruction cannot control the original causal inputs |
| Multi-month compound chain | compositional risk | synthetic horizon lacks real consolidation dynamics | stages are simulated without preserving their causal dependencies |

The source therefore contains more than twenty useful interventions, but the normalized catalog usually records only `GOAL` and sometimes `MAIN_CONFOUNDERS`. A named intervention is not yet a discriminating experiment.

## Material extraction-QA findings

Five live-brainstorm tests are semantically distinct but were bundled under parser-fallback records and require split successors rather than new source attribution:

1. self-model ablation;
2. `SELF`/Memory-root substitution;
3. Current-Status representation factorial (minimal/rich/derived/hybrid);
4. stable reference locator with changed referent;
5. multiple fresh-instance reconstruction variance.

The v0.1 experiment catalog also compresses reconstruction swap across retrieval, context compilation, runtime, and model effects. These must remain separate interventions because they support different causal conclusions.

## Strong kill-test reinterpretations

- False autobiography is not merely a correction test. It attacks the idea that present recognition of a history is sufficient for identity unless causal lineage is independently represented.
- Complete state copy plus a materially different retriever/solver attacks both narrow “Memory is enough” and broad definitions that hide reconstruction policy inside Memory.
- Exact historical replay is impossible to interpret if hidden provider inputs are not captured; failure may show missing causal state rather than metaphysical discontinuity.
- Successful cloud-to-local continuity does not establish model irrelevance; failed continuity does not establish Persona death. Both require a predeclared behavioral/relational envelope.
- Deletion experiments can detect residual influence but cannot prove total causal erasure from a finite behavioral sample.

## New relations recovered

1. Historical-replay test `DEPENDS_ON` capture of reconstruction and hidden-provider inputs.
2. False-autobiography test `TENSION_WITH` recognition-only continuity.
3. Retriever-swap test `REFINES` the broad reconstruction-swap experiment.
4. Context-compiler swap `REFINES` the broad reconstruction-swap experiment.
5. Current-Status factorial `EVALUATES` persisted-rich, minimal, derived, and hybrid status models.
6. Reference-target drift `EVALUATES` locator, snapshot, and relational Memory semantics.
7. Deletion test `WEAKENS_IF_EFFECT_FOUND` claims of dependency-complete erasure.
8. Multi-month chain `CONSTRAINS` one-write/one-object safety judgments.
9. Fission-authority factorial `CONSTRAINS` implicit Authority inheritance.
10. Merge successor test `ALTERNATIVE_TO` identity-reunification evaluation.

## Unresolved design work

Every promoted experiment must state a target hypothesis, explicit counterhypothesis, controlled variables, one manipulated variable or declared factorial, observables, expected discrimination, and a failure-to-discriminate condition. The source provides the intervention families; v0.2 must supply the separated Codex-inference designs without implying that any experiment was executed.
