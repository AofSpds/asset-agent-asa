# Source card 05 — representation prior-art register

## Receipt

- PASS_ID: SOURCE-CARD-05
- START_TIME: 2026-08-20T09:19:02+09:00
- END_TIME: 2026-08-20T09:19:34+09:00
- ACTIVE_REVIEW_SECONDS: 32
- SOURCE_FILE: `control/research/asa-mi/planning-guidance/v0.1/references/AAA_ASA_MI_REPRESENTATION_PRIOR_ART_REFERENCE_REGISTER_v0.1.md`
- SOURCE_BYTES: 8877
- SOURCE_SHA256: `58ef7d0fe7b797607c65d1acc334ede51365527ad883e87adcc21ea891867cc5`

## Semantic review

All seven reference families were reread with their source type, claimed similarity, important difference, weight, and adoption state visible. The seven v0.1 label-only objects are correctly repaired: AIDA, Nanopublications, RDF, PROV-O, SHACL, SBVR, and JSON-LD remain low-weight and not adopted.

The register-level rule permits a reference to support, refine, challenge, inspire, or provide prior art, while denying automatic validation, authorization, freeze, requirement, or replacement. This is already preserved by `V02-LIVE-NEW-0002` and the explicit verification limitation `V02-SRC-NEW-0010`; it was not counted again.

Optional RDF/JSON-LD projection and SHACL field examples are implementation possibilities, not ASA-MI design decisions. The preservation rule is research-lineage policy, not evidence that any cited external assertion is correct.

## Result

No new object, correction, or relation. The raw external papers/pages were not independently reverified; this source card verifies only what the repository register says.
