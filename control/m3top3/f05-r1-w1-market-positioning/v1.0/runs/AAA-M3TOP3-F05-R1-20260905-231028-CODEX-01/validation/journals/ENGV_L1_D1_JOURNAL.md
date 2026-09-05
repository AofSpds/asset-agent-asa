# ENGV L1 D1 independent validation journal

- Receipt: `AAA-M3TOP3-F05-R1-D1-ENGV-L1-20260906-012411-01`
- Run: `AAA-M3TOP3-F05-R1-20260905-231028-CODEX-01`
- Canonical validator identity: `root/f05_r1_engv_d1`
- Physical execution actor: `root/f05_r1_engv_d1_fresh`
- Target author: `root/f05_r1_author`
- Verdict: `PASS`
- Findings: none

## Independence and lane custody

The physical actor `root/f05_r1_engv_d1_fresh` was mapped to the clean canonical ENGV role lane `root/f05_r1_engv_d1` after an earlier contaminated lane was discarded without a verdict. This validation was performed independently of the target author and other validators. No peer D1 receipt, journal, conclusion, or verdict was read. No D0 PASS transferred. The target was not edited, no production score command was executed, no score output was created, and no commit was made.

## Frozen target

- Revision: `D1`
- Commit: `2700dda2fee8b4f8b6cfab9c075f8b860ffc94f9`
- Tree: `c98194af223562e440d66c47b57f6696110ced47`
- Bundle: `AAA-M3TOP3-F05-R1-D1-2700dda2fee8b4f8b6cfab9c075f8b860ffc94f9-c98194af223562e440d66c47b57f6696110ced47`
- Target input hash: `78d540e5e0385104ba21a744e28897762f4d15af25f571de1cc57136882b2500`

The current checkout HEAD was a later descendant, `57a5b9b37936af1ca9b08f17d4b39d3de26d35a0`. It was not substituted for the frozen target. Validation used the exact target commit/tree and separately proved that scoring custody rejects HEAD, worktree, bound-byte, and validated-target drift.

## Authority and exact binding recovery

The Owner-approved policy and execution request were recovered directly from their pinned Git objects:

- Policy commit/blob: `709ded3f4440142c05a97dcc03b286ad49fa149b` / `ab65b65182fddaf31c1b7e0d7e1f0341f4bbdf9e`
- Request commit/blob: `ab1a9a52cbee1825a2ff725a8b997307f7f5e16e` / `370c86569717aa1b93ecc748a06766d0400946e0`

All 34 entries in `P4_D1_EXACT_TARGET.json` were checked independently. Results were 34/34 matching byte lengths, 34/34 matching worktree SHA-256 values, and 34/34 matching Git blobs at the frozen target commit. There were zero mismatches.

Exact input bindings also matched:

| Input | SHA-256 |
| --- | --- |
| F05 canonical JSONL | `8e5c2991eb1c14bede88300a5fd1d648ce263d3e7a3d6a83b31af9b1e3d873f7` |
| Frozen F02 model-input batch | `13667596d8e76f10d319f4129a7cba3b890d2575b3cebf33b78a143740bbbf9e` |
| Preserved model configuration | `eecde22a7744cff505c624bb6f0bdb11714352a122632238ea68d9cd0fbacb98` |
| Reconstructed merged F02+F05 input | `78d540e5e0385104ba21a744e28897762f4d15af25f571de1cc57136882b2500` |

The bound raw Parquet was 24,572,111 bytes with SHA-256 `b0c38943e67637d5faf88429880092cf0f46a394be39860dd3bcd0b04231bccb`. The exact cohort artifact was 10,698 bytes with SHA-256 `8ac8ba439b3decb2690e04ec8fa7d40e40c37dd1ab0329bf3d24bf8253eba6a1`.

## Engineering review outcome

The adapter change is semantic-neutral: `PriceRow` adds optional `amount`, `changes`, and `changes_ratio` fields after all legacy fields; existing positional construction remains compatible; CSV parsing remains compatible; DuckDB exposes existing columns by name and preserves old minimal schemas using `NULL`; Volume and Stocks conversion rejects booleans, fractional values, and non-finite values.

The builder remains score-free and fail-closed. It binds the exact dataset, Parquet SHA-256, source semantics, consumed fields, 61-session grid, cutoff, 57-member cohort, official CA evidence/custody, and exact GST/Exicon rows. It compounds `ChangesRatio / 100` across exactly 20 and 60 intervals, computes recent-20 over immediately-prior-20 turnover, fixes Decimal context and reduction order, and refuses partial denominators, wrong identities, missing values, duplicate/misaligned dates, post-cutoff rows, dividend substitution, and adjustment factors.

The score-output helper is pure with respect to the filesystem and cannot construct the engine until the exact D1 target, bundle, input bytes, role/level/identity/receipt-ID rules, author separation, independence assertion, no-transfer assertion, empty findings, canonical role order, and exact descriptor paths all pass. The CLI separately enforces repository-root containment, no link hopping, clean Git, target ancestry/tree/blob custody, bound bytes, create-once output state, and a complete post-helper recheck before persistence.

Ten model/scorer/config/eligibility/PIT runtime blobs were identical between the D1 parent and D1 target, including `features_v1.py`, `features_v1_narrow_patch.py`, `scorer_v1.py`, `m3top3_v1.0.json`, `contracts_v1.py`, `coverage_limited_replay_v1.py`, `pit_guard.py`, `real_input_replay_v1.py`, `shared_interface_guards_v1.py`, and `window_mapping_v11.py`. The four changed D1 code/test files compiled in memory, and the exact D1 diff passed `git diff --check`.

## Positive matrix

| Case | Result | Evidence |
| --- | --- | --- |
| P01 | PASS | Additive `PriceRow` and CSV old-call compatibility; new fields remain optional and typed. |
| P02 | PASS | DuckDB exposes the existing Parquet fields, preserves an old minimal schema, and rejects non-integral count values. |
| P03 | PASS | Ordinary issuer uses exact 21/61 observations for 20/60 intervals. |
| P04 | PASS | GST 2024-06-26 reference-price change and 2024-07-24 share-count boundary are exact. |
| P05 | PASS | Exicon 2024-06-03 reference-price change and 2024-07-31 share-count boundary are exact. |
| P06 | PASS | Turnover acceleration is exact recent-20 mean divided by prior-20 mean minus one. |
| P07 | PASS | Exact 57-member equal-weight benchmark, aliases, materialized inputs, and unchanged engine compatibility hold. |

## Negative matrix

| Case | Result | Rejection proved |
| --- | --- | --- |
| N01 | PASS | Naive raw-close return across a CA boundary. |
| N02 | PASS | Wrong issuer/date/source field/source binding. |
| N03 | PASS | Post-cutoff/future row or shifted cutoff. |
| N04 | PASS | 56-member denominator, wrong 57-member cohort, missing/extra member. |
| N05 | PASS | Missing, zero, nonpositive, fractional, boolean, or non-finite required market values. |
| N06 | PASS | Duplicate or cross-company-misaligned session endpoints. |
| N07 | PASS | Cash-dividend total-return substitution. |
| N08 | PASS | Invented or precomputed CA adjustment factor. |
| N09 | PASS | F05 weight, feature, scorer, config, eligibility, or PIT drift. |
| N10 | PASS | Wrong D1 revision, schema, role, level, identity, receipt ID, assertions, findings, or author separation. |
| N11 | PASS | Noncanonical role order, descriptor mismatch, false path, nonexistent path, or receipt path escape. |
| N12 | PASS | Consistently rehashed D0 target/provenance set attempting to masquerade as D1. |
| N13 | PASS | Pre/post-helper HEAD, dirty worktree, bound-byte, target-tree/blob, output-path, or create-once drift. |

## Executed verification

- Focused D1 score-gate and CLI suite: 14/14 PASS, zero failures/errors/skips.
- Exact affected-plus-regression suite with the isolated DuckDB runtime: 118/118 PASS, zero failures/errors/skips; DuckDB integration included.
- Additional synthetic post-helper probes: 3/3 PASS for untracked worktree drift, bound-evidence byte drift, and committed validated-target drift; persistence call count 0 and output-directory creation count 0.
- Actual CA custody validation: four exact event groups across `KRX:083450` and `KRX:092870`; manifest semantic SHA-256 `b947cce6c75a7a9fb1f09aab6cd2d7042ed4823098cd814f62d7adc5ce88318f`; custody semantic SHA-256 `e38dcedfabbe6743bda7358c0387fa6624bdedfc4da2ff6840d1bf2351cce1d5`.
- Actual F05 input validation: 267,149 bytes; 57 rows; 57 unique company IDs; 57 unique KRX codes; ascending IDs; 57 `AVAILABLE`; one common 20d benchmark and one common 60d benchmark.
- Reconstructed merged model-input batch: 57 rows and exact hash `78d540e5e0385104ba21a744e28897762f4d15af25f571de1cc57136882b2500`.
- Production score CLI calls: 0. Score outputs created: 0.

## Verdict

`PASS` for ENGV L1 D1. The frozen target meets the approved engineering controls with no finding and no semantic, model, scorer, configuration, eligibility, denominator, provider, or PIT drift.
