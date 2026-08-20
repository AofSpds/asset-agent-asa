# v0.1 object extraction semantic-QA report

## Receipt

```text
PASS_ID = OBJECT-QA-ALL-487
PASS_PURPOSE = Review every v0.1 object against its repository-visible source record and provenance layer.
START_TIME = 2026-08-20T07:52:20+09:00
END_TIME = 2026-08-20T07:57:21+09:00
ACTIVE_REVIEW_SECONDS = 301
OBJECTS_REVIEWED = 487
SOURCE_DERIVED = 346
LIVE = 111
CODEX_INFERRED = 30
RAW_PRIMARY_SOURCE_VERIFICATION = NOT_PERFORMED
```

Each JSONL disposition records the fifteen requested checks: statement fidelity, metadata fallback, class, subclass, source position, current state, Owner state, source level, negative semantics, locator, split/merge, wording, historical context, semantic duplication, and raw-source limits.

## Dispositions

| QA status | Count | Meaning in this review |
|---|---:|---|
| `ACCURATE` | 313 | Primary claim and provenance fields are materially faithful to the repository-visible record. |
| `ACCURATE_WITH_MINOR_NORMALIZATION` | 1 | The RED-I verdict direction required disambiguation by its source-register summary. |
| `NEEDS_CORRECTION` | 128 | A successor record corrects statement, class strength, source-finding type, locator, source-state, and/or source-context loss. |
| `SPLIT_REQUIRED` | 2 | One experiment bundle and one over-consumed worldview section require independent successors. |
| `MERGE_CANDIDATE` | 3 | Possible semantic equivalence exists, but provenance/layer separation must remain. |
| `RAW_SOURCE_REQUIRED` | 10 | The parking-lot paraphrase is faithful to the normalized record but cannot be semantically verified against unavailable raw packets. |
| `REVIEW_REQUIRED` | 30 | v0.1 Codex inferences are coherent candidates, not source claims or Owner positions. |

## Material error families

### 1. Metadata/label used as statement — 51

The parser selected `TENSION`, `CLASS = ...`, `OBJECT_ID = ...`, or `TARGET = ...` instead of claim-bearing fields or heading context. This is the central extraction defect. Corrected successors recover component lists, model rules, experiment conditions/targets, planning recommendations, and live hypotheses.

### 2. Source class strengthened — 17

`CANDIDATE_HYPOTHESIS` was normalized to `WORKING_HYPOTHESIS`. A candidate can be active without being the workstream's working hypothesis. Successors use `CANDIDATE_HYPOTHESIS` and retain the original state.

### 3. Non-resolving locator anchors — 14

Nine synthetic meta/thesis anchors and five checkpoint anchors did not exist in their target files. The content is retained; successor locators point to the actual repository file or RED-III thesis list.

### 4. Experiment objective omitted — 22

RED-I and RED-II experiment objects captured an intervention line while dropping `TARGET`; two RED-II records captured only `TARGET` because their condition lived in the heading. Successors join condition and discrimination target. These remain source experiment ideas, not executed experiments.

### 5. Source finding reduced to a label — 8

`STATE_PORTABLE`, `INDEX_PORTABLE`, and related RED-II objects lost `SOURCE_STATE`. Successors state both the subject and its qualified status, including `NOT_PROVEN` and representation dependence.

### 6. Reference name mistaken for reference claim — 7

Prior-art objects stated only `AIDA`, `RDF_1_2`, etc. Successors retain low weight, non-adoption, and the limited similarity/projection relation. External links were not independently reverified.

### 7. Bundled records — 2 predecessors / 19 proposed successors

The live experiment bundle contains ten experiments. `CX-LIVE-WORLDVIEW-0009` consumed later Memory-boundary, challenge, preservation, and unresolved-question sections into one source record. Both are preserved and split proposals are recorded; no predecessor is deleted.

### 8. RED source finding mislabeled as evidence — 9

The v0.1 class mapper converted `SURVIVAL_FINDING` to `EVIDENCE_CLAIM`. A RED-source conclusion or plausibility status is not an executed experiment or independent evidence. Manual re-audit changes the successor class to `SOURCE_SURVIVAL_FINDING` while preserving exact source-state qualifiers. Five are newly added correction predecessors; four existing statement successors also gain the class correction.

### 9. Verdict scope required cross-file resolution — 1

`CX-SRC-SRC-R1-0001` is ambiguous in isolation, but the source register explicitly states `literal Identity = Memory -> REJECTED BY COUNTERFORCE`. The final disposition is `ACCURATE_WITH_MINOR_NORMALIZATION`: RED-I rejected the literal equation while preserving Memory as a major continuity carrier. This remains a normalized adversarial-source verdict, not raw verification, formal validation, or Owner adoption.

### 10. Named model omitted its payload — 4

`CX-SRC-SRC-MI0-0015` retained only `MEMORY_SCOPE_HIERARCHY_CANDIDATE`; its seven proposed scopes were left in embedded source text. A late whole-file residual audit corrected the earlier `ACCURATE` disposition and created a successor containing the complete candidate set.

A follow-up residual screen then reviewed 78 other long-record/short-statement candidates. It found three further metadata-name fallbacks: the multidimensional continuity model, trajectory-based drift monitoring, and accepted-envelope/declared-evolution model. The latter two use separate component-set objects for their signals/dimensions so the corrected parent model and recovered detail are not counted as paraphrases. These late corrections demonstrate why the initial QA itself was reattacked.

### 11. Explicit unconfirmed state left unstructured — 1

`CX-SRC-SRC-MI0-0001` recorded `SOURCE_POSITION_STATE=NOT_RECORDED` even though the source record says `CONFIRMATION=UNCONFIRMED`. Because this is the central `Identity ?= Memory` hypothesis, a residual negative-semantics audit promoted the issue from minor normalization to a correction successor. The statement is unchanged; the successor makes unconfirmed normalized-source status and non-Owner-acceptance explicit.

### 12. Explicit source state, motivation, examples, or meaning omitted — 10

A late field-by-field reread found ten more predecessors whose headline was plausible but incomplete. Successors `0119`–`0123` restore scope-revisable candidate status, a non-promoted authority-firewall scope note, two non-validation qualifiers on mathematical-looking decompositions, and an open measurement boundary. Successors `0124`–`0128` restore four poisoning targets, supporting-and-conflicting evidence with the qualifier “where possible,” RED-I-local P0 severity, the portability motivation for persisted Current Status, and the meaning plus five negative modes behind `EVOLUTION != GROWTH`.

### 13. Compact-index false positive rejected — 10 provisional records removed

An adversarial disposition audit initially inferred that ten raw-limited parking records lacked statements because the compact `run/object_index.jsonl` omits their full payloads. Direct reread of canonical `source-derived/objects.jsonl` disproved that inference: every predecessor contains its normalized statement. Provisional corrections `0129`–`0138` were deleted, the original QA dispositions were restored, and no count was retained. This rejection is recorded because anti-count-inflation is part of semantic QA.

### 14. v0.2 successor self-QA — 3 successor enrichments, no new predecessor count

Reopening the correction successors caught three v0.2-side losses: successor `0067` now names all ten open relation-vocabulary candidates; `0068` now records the actual non-claim rather than the metadata word `RECOMMENDED`; and `0049` makes five cold-start continuity dimensions explicit. These are quality repairs to existing successor records, not additional v0.1 correction predecessors.

## Manual all-object re-audit

A second numbered pass reopened all 487 objects beside their complete embedded records in 16 batches. Later negative-semantics, source-card, source-field, and successor audits produced the additional error families above and are recorded in the pass ledger. The initial automated dispositions are therefore not treated as self-validating.

## Duplicate audit

Lexical equality created false duplicates among the three different `TENSION` records and among multiple `CLASS = ...` fallbacks. Two genuine possible-equivalence pairs were retained:

- historical `MEMORY != AUTHORITY` across MI and RED-III;
- historical/live `DELETE_SOURCE != DELETE_INFLUENCE`.

They are link candidates, not collapse/delete instructions. Same wording across provenance layers remains separate evidence.

## Boundary of this report

This is semantic extraction QA against repository-visible normalized/live text. It does not verify the seven unavailable raw primary sources, validate any hypothesis, establish Owner acceptance, or make v0.1 canonical. `v01_object_qa.jsonl` is the complete disposition registry; `corrections.jsonl`, `splits.jsonl`, and `merge_candidates.jsonl` preserve successor actions.
