# Integrity audit

## Result

```text
INTEGRITY_AUDIT_STATE = PASS
RESEARCH_VALIDATION_STATE = NOT_PERFORMED
INTEGRITY_PASS != RESEARCH_VALIDATION_PASS
AUDIT_TIME = 2026-08-20T11:13:35+09:00
```

This audit verifies registry structure, traceability mechanics, coverage, isolation, and declared state. It does not claim that a hypothesis is true, that every interpretation is semantically correct, that raw-source intent is verified, or that the Owner accepted any result.

## Executed checks

| Check | Observed result | State |
|---|---|---|
| JSONL parsing | 19 files / 1,296 nonblank records parsed; zero errors | PASS |
| v0.1 object QA coverage | 487 records / 487 unique predecessor IDs | PASS |
| QA disposition total | 313 + 1 + 128 + 2 + 3 + 10 + 30 = 487 | PASS |
| Correction identity | 128 unique correction IDs, predecessor IDs, and successor IDs | PASS |
| Correction preservation | every record contains predecessor and successor; v0.1 is retained | PASS |
| Correction layer copies | 80 historical-normalized + 48 live = 128 | PASS |
| New endpoint identity | 820 base/new/successor/split/inference endpoint IDs; zero duplicate IDs | PASS |
| New relation identity | 162 unique IDs and 162 unique from/type/to triples | PASS |
| Relation endpoint resolution | all 162 new relations and all 53 corrected v0.1 relation endpoints resolve | PASS |
| Relation certainty separation | candidate certainty and endpoint status are stored separately | PASS |
| Historical/live matrix | 62 unique endpoint pairs; no `RESOLVED` classification | PASS |
| Source locators | 122 unique repository-addressable correction/recovery locator files resolve | PASS |
| Pass ledger parsing | 99 receipts; unique pass IDs | PASS |
| Receipt source lists | every receipt has a nonempty explicit `source_files_opened`; array count equals `source_file_count` | PASS |
| Receipt time order | start timestamps are monotonic; zero regressions | PASS |
| Required semantic passes | 10 full sweeps, 16 specialist passes, 8 red-team passes | PASS |
| Saturation receipts | final `SATURATION_01`–`03` exist after prerequisites and report zero/zero/zero | PASS |
| Layer separation | B corrections/recoveries, C corrections/recoveries, D QA, and E inference use separate registries | PASS |
| Inference targets | 27 counterhypotheses, 28 experiments, 22 failure modes, 14 models, 27 edge cases | PASS |
| Experiment schema | all 28 records preserve target, counterhypothesis, controls, manipulation, observables, expected discrimination, and failure-to-discriminate fields | PASS |
| A–O experimental coverage | recorded and re-audited in experiment QA and specialist outputs | PASS |
| Write isolation | Git status shows only the authorized v0.2 root | PASS |
| v0.1 preservation | no v0.1 path differs from base `aa99e57...` | PASS |
| Branch identity | `codex/asa-mi-semantic-remining-20260820-v02` | PASS |
| Branch lineage | merge base with `aa99e57...` is exactly `aa99e57...` | PASS |
| Main preservation | local `main` remains `5f54a2f829b6ff42517e8159f3a1299a79e6fcdb` | PASS |
| Merge/rebase state | no merge or rebase performed; exact base ancestry retained | PASS |
| Raw-source claim | seven missing packets remain `NOT_PERFORMED` | PASS |
| Authority claims | no validation, freeze, Owner acceptance, merge readiness, or production claim | PASS |

## Semantic-QA caution

The audit intentionally distinguishes “file/ID/endpoint/coverage mechanics pass” from “meaning is proven correct.” Semantic review occurred through the full sweeps, specialist passes, red-team passes, object-by-object QA, relation audits, source-card audits, source-field audits, and residual rereads. That work can identify and correct extraction errors; it cannot convert normalized historical records into raw-verified evidence or research hypotheses into facts.

## Anti-fake-pass findings retained

- The pass ledger no longer contains a duplicate `SATURATION_01`; the earlier zero pass is named `SATURATION_01_PRE_RESET_ZERO` and explicitly invalidated by later material discovery.
- Eight early receipts that summarized collections as “three registries,” “six red-team artifacts,” or similar were expanded to their actual filenames; receipt array counts now match reported counts.
- Ten provisional parking-lot corrections caused by a compact-index omission were removed after canonical source-object reread disproved them.
- Duplicate relation triples and historical/live endpoint pairs were removed rather than counted.
- `POSSIBLE_SEMANTIC_EQUIVALENCE` edges preserve endpoints and provenance; they do not assert semantic identity.

## Publication recheck required

After the content commit, the publication step must re-run JSONL parsing, endpoint resolution, `git diff --check`, authorized-path status, base ancestry, and working-tree cleanliness. The exact post-commit HEAD and Draft PR URL are external publication receipts and will be recorded in the return packet and PR body.
