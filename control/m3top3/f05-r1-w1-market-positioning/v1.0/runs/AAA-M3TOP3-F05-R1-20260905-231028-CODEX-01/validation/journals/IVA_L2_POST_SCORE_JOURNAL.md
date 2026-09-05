# IVA L2 P5 post-score validation journal

- Run: `AAA-M3TOP3-F05-R1-20260905-231028-CODEX-01`
- Validator: `root/f05_r1_iva_post_score`
- Role / level: `IVA / L2`
- P5 target: commit `e273b052c8ef663ae0f151c5747e9112b4cd811d`, tree `e272648ee236b4d5866dd09e818749486386771a`
- Verdict: `PASS`
- Findings: none

## Independence and preservation

The target HEAD/tree and a clean worktree were confirmed before evidence inspection. The three score outputs were read from committed Git objects. The F05 transform, rank order, merged input hash, deterministic engine ID, and five-row F02/F05 formula were independently reconstructed with standard-library Decimal arithmetic at precision 28 and `ROUND_HALF_EVEN`; no production scorer, score CLI, or repository scoring module was invoked.

The raw verdict and empty findings were frozen before the CLI receipt was opened. `P5_POST_SCORE_READBACK.json` and the PMO P5 narrative were not read. The CLI receipt was then used only to reconcile already-frozen target, input, engine, call-count, and output bindings. No target input, implementation, score output, ledger, progress artifact, PMO journal, or existing artifact was edited. The validator made zero score-engine invocations and no commit.

## Committed byte evidence

| Artifact | Bytes | Git blob | SHA-256 |
|---|---:|---|---|
| `F05_R1_W1_SCORES.jsonl` | 56,858 | `bf541ebefeaf235a1a4f94a2b27570d142e01a91` | `37c5a27505fb4786f7ee4d4cb5f51d8c5ba5ad39542226ac6f0361ac4f7d744d` |
| `F05_R1_W1_PROVISIONAL_RANKING.csv` | 8,969 | `ce3264b44a2c781e6505c6aa5838ca9117f329bb` | `7cfd2d09fa802ce93092826da4746fb25509ab5358655e6b58532f3190aa5360` |
| `F02_F05_PROVISIONAL_MULTI_FEATURE_VIEW.csv` | 1,055 | `20edde90a93d50b38949af9cfe6ad4a6da733d4b` | `5746b865e22bf8896f89d460c02e73d8a0c85e3e975f711b09a6877153125f61` |

The committed D1 aggregate is `F05_R1_AFFECTED_VALIDATION_REPORT.json`: 13,924 bytes, blob `76934ea137b90354463e3cd4c966a80e48dfe0c3`, SHA-256 `ef2fd2c6f53286b332e839cea08a286809f504bf21014da1ade884098adf77e8`. It declares D1 `PASS`, `scoring_permitted=true`, no blocking findings, and exact CTLV/MODV/ENGV/IVA PASS role bindings.

Pre-score bindings matched committed bytes: F05 input `8e5c2991eb1c14bede88300a5fd1d648ce263d3e7a3d6a83b31af9b1e3d873f7`, F02 batch `13667596d8e76f10d319f4129a7cba3b890d2575b3cebf33b78a143740bbbf9e`, config `eecde22a7744cff505c624bb6f0bdb11714352a122632238ea68d9cd0fbacb98`, and independently reconstructed merged hash `78d540e5e0385104ba21a744e28897762f4d15af25f571de1cc57136882b2500`.

## Independent score checks

- 57 canonical score rows and 57 unique company IDs were present; F05 ranks were the exact permutation `1..57`.
- All 57 F05 scores, recognition velocities, saturation penalties, and ranks matched independent reconstruction, including exact Decimal strings.
- All 57 ranking CSV rows exactly matched the score-row identity, score, rank, coverage, claim, and flag fields row by row.
- The two F05 tie groups used deterministic company-ID ascending order: ranks 1–6 at score 85 (`084370`, `101160`, `104830`, `140860`, `232140`, `240810`) and ranks 28–29 at score 50 (`183300`, `281820`).
- Coverage was exactly five rows at `0.3` and 52 rows at `0.2`; exactly 52 rows had null F02 scores and null combined ranks.
- All top-3 and top-10 flags were false. The claim ceiling was uniformly `F02_F05_PROVISIONAL_EXPLORATORY_NO_OFFICIAL_TOP_K`. Recursive field inspection found no outcome, future, official-selection, or action fields.

The five combined rows were exactly ranked as follows, and each score matched `(25*F02_SCORE+20*F05_SCORE)/45` under Decimal arithmetic:

| Rank | Company | F02 | F05 | Combined |
|---:|---|---:|---:|---:|
| 1 | `KRX:025560` | 87.5 | 61.60714285714285714285714285 | 75.99206349206349206349206349 |
| 2 | `KRX:031980` | 87.5 | 39.10714285714285714285714285 | 65.99206349206349206349206349 |
| 3 | `KRX:005290` | 50 | 65.71428571428571428571428571 | 56.98412698412698412698412698 |
| 4 | `KRX:036200` | 25 | 20.53571428571428571428571429 | 23.01587301587301587301587302 |
| 5 | `KRX:003160` | 0 | 41.07142857142857142857142857 | 18.25396825396825396825396825 |

## Post-freeze receipt reconciliation

The committed CLI receipt is 1,745 bytes, blob `84e75afe6fb0f2d9d37a69e3088f2e73da634624`, SHA-256 `738f33d1a597453bd3cbd2e29938602aacb05061ccaa3a615d027c9ac7677bb8`. Its three artifact hashes/byte counts, D1 target, four input bindings, merged hash, claim ceiling, and engine run ID matched the frozen raw findings. The engine ID independently reconstructed as `m3run_d76f0878dc3ced762337fe37b591b3cd`. The receipt declares exactly one score-engine call; this validator made zero calls.

Assertion accounting: 841 independent raw assertions plus 27 post-freeze receipt-reconciliation assertions equals 868 validator assertions, all passing. A read-only corroborating lane separately passed 29 of 29 grouped invariants; those grouped checks are not included in the 868 total.

Final verdict: `PASS`. Findings: `[]`.
