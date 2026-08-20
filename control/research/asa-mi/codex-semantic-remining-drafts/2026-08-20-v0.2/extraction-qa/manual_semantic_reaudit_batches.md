# Manual semantic re-audit of all 487 v0.1 objects

This second audit reopened the v0.1 registries in numeric order and read every `STATEMENT` beside its complete embedded `SOURCE_RECORD_TEXT`. It was specifically aimed at false negatives left by the initial field-aware QA rules. It did not infer semantic truth or verify unavailable raw packets.

| Batch | Objects | Corpus region | Manual result |
|---|---:|---|---|
| MR-01 | 1–30 | Whitepaper principles/models/conflicts | Primary claims faithful; three `TENSION` fallbacks already corrected. Candidate-to-broad-type class normalization was reviewed as non-material because confirmation and source-state fields preserve candidate status. |
| MR-02 | 31–60 | Identity/Memory, provenance, common/local, reconstruction | Four class-as-statement failures already corrected; no new statement loss. |
| MR-03 | 61–90 | forgetting, fission/merge, portability, evaluation, first RED-I alternatives | New ambiguity: `SN-R1-CH-001` uses `SOURCE_VERDICT = REJECTED BY COUNTERFORCE` without an explicit verdict target. `CX-SRC-SRC-R1-0001` is downgraded to `SOURCE_CONTEXT_REQUIRED`. |
| MR-04 | 91–120 | RED-I history, convergence, poisoning, fission, local survival | New class error: `SURVIVAL_FINDING` was normalized to `EVIDENCE_CLAIM`, implying empirical support not present in the normalized source. Two objects in this batch require class successors. |
| MR-05 | 121–150 | audit, multidimensional continuity, RED-I experiments, early RED-II | Experiment-target omissions were already corrected. Two additional `SURVIVAL_FINDING` class errors identified. |
| MR-06 | 151–180 | runtime variance, reconstruction, RED-II finding table | Five additional `SURVIVAL_FINDING` class errors; four already had statement successors and receive added class correction. Label-only finding errors remain preserved, not deleted. |
| MR-07 | 181–210 | RED-II experiments and RED-III provenance/rollback/deletion | Two heading-dependent experiment conditions were already corrected; no new issue. |
| MR-08 | 211–240 | RED-III Authority/audit/common-memory and derived open-question catalog | Source claims remain unvalidated and Owner-unknown as required; no new extraction issue. |
| MR-09 | 241–270 | derived question catalog | Questions faithfully preserve unresolved status and derivation locators. |
| MR-10 | 271–300 | derived questions, historical firewalls, cold-start candidates | Historical `MEMORY != CURRENT STATE` remains distinct from later live challenges; no retroactive correction. |
| MR-11 | 301–330 | automation, topology, experience products, normalization boundaries | Main claims faithful; source-context details remain embedded. |
| MR-12 | 331–360 | RED theses, parking lot, live planning | Parking-lot candidates exist in v0.1 and were not recounted as new. Seven planning metadata fallbacks were already corrected. |
| MR-13 | 361–390 | planning recommendations, prior art, live foundations, early live hypotheses | Prior-art name-only statements already corrected; register-wide non-adoption rule remains a genuinely new source recovery. |
| MR-14 | 391–420 | procedures, Self, Status, Context, lifecycle, experiments, corrections | Candidate-to-working class strengthenings and metadata fallbacks already corrected; experiment bundle remains split-required. |
| MR-15 | 421–450 | live open questions and worldview | Worldview objects preserve section theses with explanatory source text. Their overlapping live planning records are related evidence, not independent evidence. |
| MR-16 | 451–487 | worldview merge defect, checkpoint, Codex-inferred v0.1 | `CX-LIVE-WORLDVIEW-0009` remains split-required; all 30 v0.1 Codex inferences remain `REVIEW_REQUIRED`, not source or Owner claims. |

## Material delta from initial QA

- Nine objects now require class correction from `EVIDENCE_CLAIM` to `SOURCE_SURVIVAL_FINDING`.
- Five of the nine are newly added correction predecessors; four existing statement corrections gain a class correction.
- One previously `ACCURATE` object is now `SOURCE_CONTEXT_REQUIRED` because the verdict scope is ambiguous.

Later `VERDICT-CONTEXT-RESOLUTION` reopened `01_SOURCE_REGISTER.md` beside the RED-I object set and resolved the normalized-record direction: the rejected target is literal `Identity = Memory`. The final disposition is `ACCURATE_WITH_MINOR_NORMALIZATION`; raw-primary verification remains not performed.
- No new source object was counted from these fixes.

The re-audit confirms coverage, not validation. `RAW_PRIMARY_SOURCE_VERIFICATION = NOT_PERFORMED` remains unchanged for the seven historical source packets.
