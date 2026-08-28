# SP-10 — Common Memory, local Memory, and convergence

## Receipt

```text
PASS_ID = SP-10
PASS_PURPOSE = Re-read what may be shared or local and test whether the favored shared-evidence/separate-interpretation control actually establishes independence.
START_TIME = 2026-08-20T07:40:41+09:00
END_TIME = 2026-08-20T07:42:05+09:00
ACTIVE_REVIEW_SECONDS = 84
SOURCE_FILES_OPENED = MI planner; RED-I; RED-III; open-question catalog
SOURCE_FILE_COUNT = 4
SOURCE_BYTES_CONSIDERED = 56607
RAW_PRIMARY_SOURCE_VERIFICATION = NOT_PERFORMED
```

## Layered sharing boundary

The sources mention sharing at materially different layers: raw events, evidence, references/locators, selected history, interpretations, heuristics, Current Status, ontology, and retrieval/consolidation policy. Calling all of these “Common Memory” obscures where convergence enters. A shared history can already encode interpretation through inclusion, ordering, omission, and salience even when its records are called evidence.

The live candidate “Shared Evidence + Separate Interpretation” remains a useful control candidate, not a proven solution. Separate interpretation can still be correlated when Personas share the same model family, ontology, retriever, compiler prompt, evaluator, or upstream evidence-selection route. Conversely, storage isolation does not create epistemic independence when those roots remain shared.

## Relations recovered

1. Common evidence `COEXISTS_WITH` separate interpretation.
2. Shared interpretation `STRENGTHENS` convergence risk.
3. Same evidence `DOES_NOT_IMPLY` independently produced interpretation.
4. Common history `MAY_EMBED` selection judgments.
5. Audit independence `IS_WEAKENED_BY` inherited common interpretation.
6. Storage isolation `DOES_NOT_IMPLY` epistemic independence.
7. Local-to-common promotion `REQUIRES` a typed transition with origin, derivation, dissent, and rollback.
8. Convergence risk `CAN_BE_OBSERVED_BY` correlated error and reduced unique-counterexample discovery.

## Discriminating design

Cross the sharing layer (evidence only / interpretation only / both / neither) with model-root, retrieval-route, ontology, and evaluator diversity. Measure correlated error, unique counterexamples, calibration, and propagation after one Persona receives poisoned evidence. A result cannot be attributed to “Common Memory” without locating which layer changed.

## Materiality judgment

No new source object is counted. The material correction is to treat Common/Local as a vector of sharing decisions, not one bucket boundary, and to withhold any claim that separate interpretation is genuinely independent.
