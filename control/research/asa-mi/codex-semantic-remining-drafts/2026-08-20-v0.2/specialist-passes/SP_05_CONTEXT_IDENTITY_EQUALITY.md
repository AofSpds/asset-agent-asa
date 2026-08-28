# SP-05 — Context, context identity, and context equality

## Receipt

```text
PASS_ID = SP-05
PASS_PURPOSE = Re-read Context definitions and distinguish structural, semantic, binding, and behavioral equality.
START_TIME = 2026-08-20T07:36:06+09:00
END_TIME = 2026-08-20T07:36:17+09:00
ACTIVE_REVIEW_SECONDS = 11
SOURCE_FILES_OPENED = live brainstorm registry; RED-II source objects; RED-I source objects
SOURCE_FILE_COUNT = 3
SOURCE_BYTES_CONSIDERED = 51441
RAW_PRIMARY_SOURCE_VERIFICATION = NOT_PERFORMED
```

## Context equality candidates

- **byte/token equality:** same serialized prompt/context.
- **content-set equality:** same propositions/evidence regardless of order.
- **binding equality:** same references resolve to the same target/version/environment.
- **semantic equality:** meaning judged equivalent despite different representation.
- **projection equality:** each function receives an equivalent relevant subset.
- **behavioral equality:** contexts induce results within a declared envelope.
- **causal equality:** the same selection, exclusion, compression, and provenance path produced them.

These relations can disagree. “Semantically equivalent context with changed order” is itself a hypothesis requiring an independent equivalence judgment.

## Structural alternatives

- Global Context makes cross-function consistency easier but increases hidden coupling and disclosure.
- Per-function local Context improves minimization but can create inconsistent Self/current/history bindings.
- Hybrid projection centralizes selection rules; that selector can become the hidden owner RED-II warns about.

## Boundary cases

1. Same text, external reference now resolves to different content.
2. Same evidence set, different order changes attention and output.
3. Same meaning, different token budget truncates rare exceptions.
4. Same bindings, different model tokenizer or system prompt changes activation.
5. Different wording, equivalent behavior on ordinary tasks but divergent safety behavior.
6. Same task-local context, different global unresolved-conflict state.
7. Same current-context label, different evaluation time or environment.

## Relations recovered

1. Context serialization equality `DOES_NOT_IMPLY` semantic equality.
2. Semantic equality `DOES_NOT_IMPLY` behavioral equality across models.
3. Binding equality `DEPENDS_ON` target identity/version, not locator alone.
4. Global Context `ALTERNATIVE_TO` local and hybrid projections.
5. Hybrid projection `DEPENDS_ON` a selection policy that may be identity-bearing.
6. Long Context `DOES_NOT_IMPLY` effective Memory.
7. Context-budget policy `STRENGTHENS` identity-bearing selection as exclusion grows.
8. Context-order experiment `DEPENDS_ON` an independently justified semantic-equivalence claim.

## Double-crux

Can two contexts be “the same” for Persona continuity if they induce materially different behavior on rare critical cases while agreeing on normal tasks? A task-relative equality notion says yes for ordinary tasks; a continuity-critical notion says no.

## Materiality judgment

No new source object is counted. Seven equality notions and eight relations prevent `same context` from acting as an uncontrolled experimental assumption.
