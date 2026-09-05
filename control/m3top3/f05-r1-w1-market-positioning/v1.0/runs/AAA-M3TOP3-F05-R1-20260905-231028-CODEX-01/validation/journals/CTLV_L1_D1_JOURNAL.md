# F05-R1 D1 CTLV L1 independent validation journal

- Receipt: `AAA-M3TOP3-F05-R1-D1-CTLV-L1-20260906-010919-01`
- Validator identity: `root/f05_r1_ctlv_d1`
- Target author identity: `root/f05_r1_author`
- Frozen target: `2700dda2fee8b4f8b6cfab9c075f8b860ffc94f9`
- Frozen tree: `c98194af223562e440d66c47b57f6696110ced47`
- Bundle: `AAA-M3TOP3-F05-R1-D1-2700dda2fee8b4f8b6cfab9c075f8b860ffc94f9-c98194af223562e440d66c47b57f6696110ced47`
- Level / role: `L1 / CTLV`
- Verdict: `PASS`
- Findings: none

## Independence and method

I did not author or edit any of the 34 D1 target files. I did not read another D1 validator's journal or receipt before freezing this verdict. D0 verdicts were not transferred. The validation used the approved policy/request, the D1 exact-target manifest, Git objects, the immutable local Parquet, vendored official-response bytes, static code review, independent Decimal reconstruction, adversarial gate calls that did not invoke scoring, and the complete affected-plus-regression test suite.

No production score CLI was run. The run's `score-and-seal` output directory was absent at verdict freeze.

## Exact authority and target identity

The Owner policy Git object was independently resolved as commit `709ded3f4440142c05a97dcc03b286ad49fa149b`, tree `e081e1a980fbace8e4909ce132bf5d03aaacffef`, blob `ab65b65182fddaf31c1b7e0d7e1f0341f4bbdf9e`, 7,102 bytes, SHA-256 `2bd9ae341904c562a25513286b6546c737df92bfa3a6ca82434c71de396fbacb`. The execution request resolved as commit `ab1a9a52cbee1825a2ff725a8b997307f7f5e16e`, tree `a8e4f0e8f8e1955e687f575cb1db2d559bb23cdc`, blob `370c86569717aa1b93ecc748a06766d0400946e0`, 7,847 bytes, SHA-256 `452b64ac36d37860f72da6367e62fef1c175af3d56b4379651c232e2ab988a53`. They state `APPROVE`, `TRUE_WITH_PRECHECK`, exact P1-P7 semantics, and no repeated approval within scope.

The D1 commit resolved to the declared tree. All 34 `P4_D1_EXACT_TARGET.json` entries matched declared byte length, SHA-256, target Git blob, current HEAD Git blob, and worktree bytes; mismatch count was zero. The D1 target remained an ancestor of the validation HEAD. The F05 input, F02 input, and config recomputed to the three declared input hashes. Their merged input hash independently recomputed to `78d540e5e0385104ba21a744e28897762f4d15af25f571de1cc57136882b2500`.

## Source, denominator, PIT, and corporate actions

The bound `marcap-2024.parquet` was 24,572,111 bytes with SHA-256 `b0c38943e67637d5faf88429880092cf0f46a394be39860dd3bcd0b04231bccb`. The bound cohort file was 10,698 bytes with SHA-256 `8ac8ba439b3decb2690e04ec8fa7d40e40c37dd1ab0329bf3d24bf8253eba6a1`; it contained 57 unique INCLUDE codes and reproduced identity SHA-256 `c72593633c88cb6913c703da626b95d6111c7b0fa5783ccef6d373b2adf8c546`.

An independent DuckDB read returned exactly 3,477 rows, 57 codes, and the common 61-session grid from 2024-05-16 through 2024-08-09. Duplicate code/date rows and invalid Volume, Stocks, Amount, or ChangesRatio rows were all zero. The physical schema matched the source-field binding. The scored return field was `ChangesRatio` percentage points; `Rank` was not admitted as an input field.

All 57 companies' 20-interval and 60-interval compounded returns and recent-20/prior-20 turnover acceleration were independently reconstructed from the raw rows. Decimal-value mismatches were zero. Seventeen string representations across 14 companies differed only by removable terminal zeroes; every pair was Decimal-equal and therefore confirms, rather than contradicts, the materializer's canonical decimal formatting. The independently reduced /57 benchmarks exactly matched:

- 20d: `-0.2124153885346208337758748387981210510982875684105824670798651096`
- 60d: `-0.2427557483310895727201166322683066906964043950156641786131060302`

All 11 vendored official issuer/KRX bodies matched custody byte lengths and SHA-256 values. Direct body markers and Parquet rows confirmed GST's 2024-06-26 KRW 21,700 ex-right base and 2024-07-24 total 18,618,260 shares, and Exicon's 2024-06-03 KRW 19,470 ex-right base and 2024-07-31 total 13,050,797 shares. Their bound daily fields were respectively `-0.46` and `+4.78` percentage points. No inferred adjustment factor, cash-dividend reinvestment, post-cutoff economic input, new provider, credential, paid source, or denominator shrink was present.

## D1 N12 correction verification

Static review confirmed that the score helper now binds the exact aggregate and receipt schema, D1 revision, role-specific L1/L2 level, pinned unique validator identity, strict receipt-ID pattern, target-author separation, exact independence assertion, `no_pass_transfer`, empty findings, own-role verdict, target commit/tree/derived bundle, all three input hashes, merged hash, descriptor hash, and the exact receipt path read by the CLI. The CLI separately requires an absent output directory, a clean worktree, target ancestry/tree/blob agreement, committed evidence bytes, and repeats HEAD/clean/evidence/target checks after the pure helper and before create-once persistence.

An in-memory exact D1 gate fixture passed without scoring. Twenty-two separately rebuilt adversarial variants were then exercised; all 22 were rejected and none reached an accepted state. Mutations covered schema, D1 revision, receipt ID, role, level, validator identity, author identity, independence assertion, supporting/author/edit/no-transfer flags, verdict/findings/role verdict, commit, tree, bundle, input hash/bindings, an aggregate D0 revision, and a false descriptor path. The JSON declarations remain repository-custody assertions and do not claim external cryptographic identity authentication.

## P/N disposition

Positive cases P01-P07 pass: ordinary 21/61 observation construction, GST and Exicon official CA boundaries, exact turnover arithmetic, exact 57-member equal-weight benchmarks, preserved downstream F05 weights/saturation, and the exact-five F02 reuse/coverage constraint are all byte- and behavior-bound.

Negative cases N01-N13 pass by rejection: naive raw-close CA returns, wrong issuer/date/source, future observations, 56/57, bad turnover inputs, duplicate/misaligned/off-by-one sessions, dividend substitution, invented CA factors, model/config drift, physical-field/scaling drift, alias/lineage drift, incomplete or forged validation custody, and non-provisional output/rank claims all fail closed in the reviewed target and tests.

## Test result

The D1 full affected-plus-regression command ran 118 tests with 118 passes, zero failures, zero errors, zero skips, and the DuckDB case included. The suite covers the existing model and PIT regressions, infrastructure contracts, all F05 market/CA/source/denominator cases, the corrected formal receipt gate, descriptor paths, dirty/preexisting outputs, exact target blobs, and helper-time committed drift.

`CTLV_L1_D1 = PASS`. This receipt permits no score by itself and makes no claim about another validator's verdict.
