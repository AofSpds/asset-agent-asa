# SP-12 — Provenance, origin, evidence, and authority

## Receipt

```text
PASS_ID = SP-12
PASS_PURPOSE = Re-read origin and provenance claims and separate evidential confidence, source identity, endorsement, and decision authority.
START_TIME = 2026-08-20T07:43:59+09:00
END_TIME = 2026-08-20T07:44:10+09:00
ACTIVE_REVIEW_SECONDS = 11
SOURCE_FILES_OPENED = planning guidance; Whitepaper objects; MI planner; RED-I; RED-III; additional-source objects
SOURCE_FILE_COUNT = 6
SOURCE_BYTES_CONSIDERED = 70353
RAW_PRIMARY_SOURCE_VERIFICATION = NOT_PERFORMED
```

## Provenance dimensions

The direct source reread supports at least six dimensions that v0.1 vocabulary can otherwise conflate:

1. originating actor or evidence source;
2. transformation/derivation chain;
3. independent corroboration and evidential confidence;
4. current endorsement, including a later explicit Owner act;
5. decision or execution Authority;
6. chain/custody integrity and availability of the underlying evidence.

Repetition and summarization cannot change the first dimension. Independent corroboration may rationally increase confidence without upgrading origin. Later Owner endorsement is a new provenance event, not a retroactive rewrite that makes the external origin “Owner-authored.” Truth, trust, relevance, endorsement, and Authority therefore need separate fields.

## Relations recovered

1. Origin `COEXISTS_WITH` derivation history.
2. Independent corroboration `MAY_STRENGTHEN` evidential confidence without changing origin.
3. Owner endorsement `CREATES` a new endorsement event rather than replacing origin.
4. Evidential confidence `DOES_NOT_IMPLY` execution Authority.
5. Source authority `DOES_NOT_IMPLY` truth.
6. Low-authority origin `DOES_NOT_IMPLY` false content.
7. Repeated consolidation `MAY_WEAKEN` provenance legibility.
8. Persona interpretation `SHOULD_RETAIN` supporting and conflicting evidence links.

## Failure boundary

“Non-launderable origin” is necessary but insufficient. A system may keep an origin label intact while placing an inferred claim into a high-salience Current Status slot, thereby producing de facto Owner-preference behavior. The audit must therefore trace both label lineage and downstream placement/use.

## Materiality judgment

No new source object is counted. The pass recovers the need for a distinct endorsement-event dimension and prevents confidence updates from being mistaken for origin or Authority upgrades.
