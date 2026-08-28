# RT-06 — Attack the research representation

## Receipt

```text
PASS_ID = RT-06
PASS_PURPOSE = Test whether objectization, tags, relations, and machine-checkable receipts delete ambiguity or manufacture ontology and false completion.
START_TIME = 2026-08-20T07:51:39+09:00
END_TIME = 2026-08-20T07:51:46+09:00
ACTIVE_REVIEW_SECONDS = 7
SOURCE_FILES_OPENED = planning guidance; live brainstorm registry; normalization boundary; tagging backlog; v0.1 draft manifest
SOURCE_FILE_COUNT = 5
SOURCE_BYTES_CONSIDERED = 54759
RAW_PRIMARY_SOURCE_VERIFICATION = NOT_PERFORMED
```

## Representation failure modes

1. **Narrative loss.** Atomic claims detach speaker, sequence, contrast, hesitation, and the argument that made wording meaningful.
2. **Classification priming.** Calling text a HYPOTHESIS, RISK, or SURVIVAL_FINDING frames later interpretation before the Owner decides what it was doing.
3. **Graph false precision.** A clean `CONTRADICTS` edge can hide conditional, partial, level-dependent, or terminological tension.
4. **Reification by ID.** Stable-looking identifiers make provisional extractions feel like canonical entities.
5. **Split-weight distortion.** A source decomposed into many objects can dominate retrieval/counts over a minority position preserved in one narrative paragraph.
6. **Negative-scope loss.** `DOES_NOT_ASSERT` detached from its local target may be reused as a global denial.
7. **Derivative-source multiplication.** Agreement among planner and RED outputs may reflect shared source ancestry rather than independent evidence.
8. **Machine-reconstruction bias.** LLMs may preferentially repeat concise fields and ignore prose caveats, ambiguity, and unclassified residuals.
9. **Review-burden inversion.** Hundreds of objects can cost more to interpret than the source narratives and encourage checkbox review.
10. **Receipt theater.** Parse success, pass labels, timestamps, and saturation files can simulate epistemic work—the precise v0.1 failure this run is correcting.
11. **Schema-shaped discovery.** Search finds what existing classes invite and systematically misses tone, metaphor, human meaning, and unnamed relations.
12. **Quota Goodharting.** Required counts can produce paraphrase inflation or low-materiality objects unless distinctness is semantically audited.

## Safeguards supported by the sources

- retain full source locators and surrounding context;
- allow narrative and `UNCLASSIFIED` residuals;
- represent relation certainty, scope, and rationale separately;
- distinguish extraction object, source claim, and current interpretation;
- audit split-induced weighting and shared ancestry;
- make round-trip reconstruction to source context testable;
- treat schema failure as evidence about the representation;
- never equate integrity conformance with research validation.

## Kill test

Give independent reviewers (a) source narratives only, (b) object registry only, and (c) both. Compare recovered alternatives, uncertainty calibration, causal structure, minority positions, and invented certainty. If registry-only reviewers converge more while losing material nuance, objectization is harming reconstruction even when every record parses.

## Materiality judgment

No source object is added. Twelve representation risks and a discriminating reconstruction test are retained; the representation remains an aid, not the ontology or proof of reading.
