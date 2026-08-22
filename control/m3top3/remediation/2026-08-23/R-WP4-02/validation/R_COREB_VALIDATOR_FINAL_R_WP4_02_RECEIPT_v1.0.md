# M3TOP3 R-WP4-02 — Final Core B Paired-Validator Receipt

```text
RECEIPT_ID = AAA-M3TOP3-R-WP4-02-COREB-L1-20260823-0305-01
VALIDATOR = AAA-MODEL-VALIDATOR
VALIDATION_ROLE = ACTIVE_CORE_B_PAIRED_VALIDATOR_L1
AUTHORING_PERSONA = AAA-MODEL-ARCHITECT / IMPLEMENTATION_BY_SEPARATE_ENGINEERING_AUTHOR
CURRENT_PERSONA_LOCK = AAA-MODEL-VALIDATOR
IVA_EXECUTION_PARTICIPATION = NONE
INDEPENDENT_L2_STATE = NOT_PERFORMED / NOT CLAIMED
VALIDATION_TIME_KST = 2026-08-23T03:05:12+09:00
REPOSITORY = AofSpds/asset-agent-asa
BRANCH = aaa-m3top3-p0-runtime-failclosed-remediation-20260823
EXACT_HEAD = 4fffdfb03fdd4ae6bf6656d2034abd3ef701ae4f
EXACT_TREE = 56dec4ec870a596627e250f4b89f95009c43f8cd
EXACT_BASE = 167c1b05e25df658b322cf428c72ce3a4f476544
OVERALL_VERDICT = PASS_WITH_NONBLOCKING_EVIDENCE_QUALIFICATIONS
CORE_B_DISPOSITION = BOUNDED_DIAGNOSTIC_FAIL_CLOSED_RUNTIME_ACCEPTED_AT_EXACT_HEAD
MODEL_SEMANTIC_CHANGE_DETECTED = NO
MODEL_STATE = S0_PRE_OUTCOME_BASELINE_CANDIDATE
OFFICIAL_GOLDEN = BLOCKED
FULL_REPLAY = BLOCKED
FREEZE_RELEASE_PROMOTION_PRODUCTION = NOT_AUTHORIZED
OWNER_ACTION_NOW = NONE
```

## 1. Decision

Core B L1 accepts the bounded fail-closed runtime remediation **only at exact Git commit** `4fffdfb03fdd4ae6bf6656d2034abd3ef701ae4f` and tree `56dec4ec870a596627e250f4b89f95009c43f8cd`.

The accepted claim is limited to diagnostic runtime safeguards: PIT admission, retrieval lineage, price-byte/CA admission, immutable storage, classified CLI failure, and global Official/Canonical kill switches. This receipt does not establish exact v1 identity, predictive power, unbiased-universe status, sealed holdout, historical data closure, canonical price readiness, model validation, Official Golden readiness, Full Replay readiness, Freeze, Release, Promotion, or Production authority.

All earlier runtime candidates, including `9f664a29436efb52be008b0d8c168a817da95411`, `6e4677cd631fdf23f16814aa54c14a4e927fa0a6`, `6b604ff20e8a01095a46f5f9cbac647cef7eb727`, `e7e68ad6244a36fac2e679a26eaef191810df411`, `0fbb7128c0f15481187ddc3a151d8c760d6c2aed`, and `91f0238e557153367bef4334e79cfc9ab1ac0209`, are rejected or superseded and are not admissible validation targets.

## 2. Authority and independence boundary

- Governed active Core B pair: `AAA-MODEL-ARCHITECT ↔ AAA-MODEL-VALIDATOR`.
- This validator did not author or edit the implementation, tests, configs, or Git history.
- Validation was read-only except for this separate validator receipt.
- `IVA_EXECUTION_PARTICIPATION=NONE`. No task, authoring, test execution, evidence production, or intermediate review was assigned to IVA.
- This is paired domain validation (L1), not independent L2 validation and not Owner Acceptance.

## 3. Exact-target identity checks

| Check | Independent result |
|---|---|
| Remote branch readback | Branch head = `4fffdfb03fdd4ae6bf6656d2034abd3ef701ae4f` |
| Remote commit tree | `56dec4ec870a596627e250f4b89f95009c43f8cd` |
| Commit parent | `91f0238e557153367bef4334e79cfc9ab1ac0209` |
| Final-commit changed files | Exactly 3: mutation harness, `snapshot.py`, immutability tests |
| Runtime/test/config local ↔ Git blobs | `24/24 MATCH`, mismatches `0` |
| Mutation harness local ↔ Git blob | `MATCH` |
| Source mutation after mutation harness | `false`; post-run local ↔ Git blobs still `24/24 MATCH` |

Final-commit exact blob bindings:

| Artifact | Git blob | Local SHA-256 |
|---|---|---|
| `run_targeted_mutation_checks.py` | `2491543578e9a6832bdc7aa4a397f33f265adcc4` | `17793fe0180509e4590db7fd9d6717dffb893f0c57e7a0d34a2c5f7bfc7f4220` |
| `tools/m3top3/snapshot.py` | `b3f6af803f96798ce572badeaeedf03b03929017` | `8f3637a11fd820771cacdfb3d2fea3bc7f5aacf401fec998687bd96ee7d472b6` |
| `test_known_failures_immutability.py` | `d1616f865283c8cd97ade1d32744eb5a74d447a3` | `7684bfcdd65c5d66ae8de7bc93cf3d3bd12197707a2c2f1bdc6e2fa6653b7bdf` |

## 4. Independent execution results

| Verification | Result |
|---|---|
| Full unittest discovery | `120/120 PASS`; failures `0`, errors `0`, unexpected skips `0` |
| Existing infrastructure tests | `25/25 PASS` |
| Known-failure test executions | `95 PASS` across seven focused modules |
| Logical Known-Failure matrix | `33/33` unique IDs |
| `compileall` | `PASS` |
| `py_compile` | `PASS` |
| Targeted mutations | `33/33 KILLED_RED`; survived/error `0` |
| Mutation isolation | `source_mutated=false` |
| Concurrent identical snapshot writes | `100` rounds / `200` writes; success-or-reuse `119`, classified collision `81`, raw errors `0` |
| Concurrent final snapshot verification | `100/100` valid; incomplete/invalid final targets `0` |

The concurrent probe admits either identical reuse/success or `IMMUTABLE_SNAPSHOT_COLLISION` with integrity exit `3`. It rejects raw `FileExistsError` leakage. The final publish protocol is accurately described as create-only/no-replace hardlink publication with `manifest.json` last as the completeness marker; it is not described as a single atomic directory rename.

## 5. Fail-closed control disposition

| Control surface | Core B result | Evidence observed |
|---|---|---|
| PIT consumed-slice firewall | `PASS` | Missing/null/naive publication, unavailable/current-only, future publication/effective rows block with stable classifications. |
| Longitudinal raw-source semantics | `PASS` | Future raw rows are excluded with deterministic retrieval receipts; consumed future rows remain blocking. |
| Snapshot state gate | `PASS` | PARTIAL/BLOCKED/READY-with-blocker states are non-scoreable before scorer/output. |
| Actual byte/count/semantic readback | `PASS` | PIT, model-input, and retrieval-audit bytes, row counts, aggregates, and manifest identity are reverified. |
| Retrieval receipt | `PASS` | One-to-one company/cutoff binding, required fields, counts, exclusions, deterministic ID, source hash, and independent reconstruction are enforced. |
| Retrieval audit non-scoreability | `PASS` | Audit is separately persisted/hash-bound and is not a scorer feature input. |
| PIT/model/manifest price lineage | `PASS` | Every slice requires exactly one matching PIT price reference with manifest/model dataset ID and content hash; missing/duplicate/drift cases reject. |
| Price semantics | `PASS` | Exact allowlist only; unknown semantics fail closed at construction and after mutation. |
| Price bytes/component manifest | `PASS` | Live component hashes and multi-component manifest identity are verified; post-init mutations reject. |
| Parquet pre-query admission | `PASS` | Byte/semantics admission occurs before connect/query; mismatch probe records zero query admission. |
| Corporate actions | `PASS_WITH_SCOPE_LOCK` | CSV and Parquet CA factor/evidence checks execute; `PRICE_CANONICAL` remains globally disabled. |
| Official/Canonical authority | `PASS` | `OFFICIAL_EXECUTION_ENABLED=False` and `PRICE_CANONICAL_VALIDATION_ENABLED=False`; both kill switches are mutation-tested. |
| Snapshot immutability | `PASS` | Exclusive target mkdir, no-replace hardlinks, manifest-last, and staging-create race classification are enforced. |
| Result/ledger immutability | `PASS` | Exclusive result creation, live ledger reread, batch ledger-before-result, and concurrent collision controls pass. |
| CLI classification | `PASS` | Controlled block/integrity/authority exits `2/3/4` and zero-write behavior are covered. |

## 6. Model-semantic preservation

No feature-definition, weight, missingness/imputation rule, gate, ranking objective, tie policy, Top3 selection rule, primary outcome definition, or outcome formula change was detected.

- `tools/m3top3/core.py` is the same Git blob at base and head: `e81561e737c3419013dc1bc5adff5ae258365862`.
- `tools/m3top3/model_interface.py` is the same Git blob at base and head: `1bc359a70a399a1eb94ef33703e2e5487afa8006`.
- `outcome.py` changes only by importing and invoking `verify_price_release()` before the existing path. Entry, MFE, MAE, horizon-close, exit-return, and pending-state formulas remain unchanged.
- Snapshot changes add evidence, lineage, admission, and immutable-publish controls. Existing feature-value extraction, `price_close`/`market_cap` defaults, eligibility semantics, scorer invocation, ranking engine, and Top3 selection path remain intact.

Therefore the patch is an infrastructure safety remediation, not a successor model and not a recovered Official v1 scorer.

## 7. Retrospective exact-base evidence qualification

The post-hoc base probe remains usable only with the following precision:

- logical IDs observed: `33/33`;
- `27 RED_OBSERVED`, `5 CONTROL_ABSENT_SOURCE_OBSERVED`, `1 BASE_SAFE_OBSERVED`;
- collection/import errors were not used as RED evidence;
- chronology: executed after implementation, so it is not chronological TDD evidence;
- materialization: all `15/15` source files contain exactly one additional trailing LF relative to the corresponding exact Git blob; none is byte-exact, while stripping that one LF yields the exact Git blob for all `15/15`;
- disposition: semantic-equivalent/reproducible behavioral evidence, not byte-exact base materialization.

This qualification does not change the exact source base commit and does not authorize Official execution.

## 8. Evidence and packet qualifications

1. Exact executable v1 identity remains unrecovered. `R-WP1-01` continues to support `EXACT_EXECUTABLE_IDENTITY_NOT_RECOVERED` and state `S0`.
2. The observed Library no-match has no persisted immutable query receipt; it remains supportive, scope-limited evidence only.
3. U127 remains a winner-enriched working/challenge universe, not a proven unbiased population universe. W1-W8 are not a clean successor holdout.
4. Historical denominator, Thin PIT, canonical price, CA completeness, and annotation-blinding closure remain open outside this bounded runtime patch.
5. Full ranking is serialized in diagnostic results, but official full-universe outcome/evaluation and Replay remain blocked.
6. Local implementation/test receipt v0.3 is tied to rejected `e7e68ad...` (`114` tests / `29` mutations) and is superseded. It was not used as evidence for this verdict. PMO must route the implementation author to currentize the author/test receipt to `4fffdfb...` (`120` / `33`) before archival packet closure; this is non-semantic housekeeping, not an Owner decision.

## 9. Claim ceiling

| Claim/action | Disposition |
|---|---|
| Bounded diagnostic fail-closed runtime at exact `4fffdfb...` | `CORE_B_L1_ACCEPTED` |
| Exact v1 identity or pre-outcome provenance proven | `REJECTED / NOT ESTABLISHED` |
| Predictive power / alpha / model validity | `NOT ESTABLISHED` |
| U127 unbiased population or W1-W8 sealed holdout | `REJECTED` |
| Historical data/annotation/canonical-price closure | `NOT ESTABLISHED` |
| Official Golden / Full Replay | `BLOCKED` |
| Model-state advancement / Freeze / Release / Promotion / Production | `NOT AUTHORIZED` |
| Independent L2 validation | `NOT PERFORMED / NOT CLAIMED` |

## 10. Owner and PMO routing

`OWNER_ACTION_NOW=NONE` is correct. The accepted changes remain within the already approved bounded remediation and do not alter model or product semantics.

PMO may, without new Owner approval:

1. route the implementation author to currentize the implementation/test receipt to the exact accepted head, then verify its exact readback;
2. register this L1 receipt and other paired-validator receipts;
3. continue R-WP1 identity recovery and R-WP2/3 evidence closure;
4. keep all Official/Canonical/Replay kill switches active.

Owner intervention becomes required only for an exact-identity recovery disposition, a new semantic reconstruction identity, any change to feature/weight/gate/ranking/outcome/universe/holdout policy, model-state advancement, Official Golden/Full Replay authorization, Freeze, Release, Promotion, or Production authority.

## 11. Key evidence digests

| Artifact | SHA-256 |
|---|---|
| Initial Core B remediation receipt | `5c796b55d42df91232f159f5a24e5908d399f778667e0e3912ec220e8d0aaefc` |
| Corrected R-WP2/3 discovery report | `451f2ccfa2c259af654fd040815306081af54b9834af4f8d703095c4ddea7e42` |
| Corrected U127 membership gaps | `752138a1897cdacfcbb4762ac0caf5888007e49ac4605f88152576e544eeaa33` |
| Corrected price/CA queue | `b7d07a1c3438c30bced3161ea5d287d53f34431c7ab3f5e040a761ea06548412` |
| Thin PIT build manifest | `5b78b6f0ea8cbdc2684e37724e3f0323ae8c50f1ae6dc1547e444d3e9c0eb7a1` |
| Known-Failure source receipt | `267270f258dc2ced7371bdecbf3ae5cb9c936b777070293a34314cdb5a70f65c` |
| Known-Failure lock spec | `0b6eaeaba69cf803730f067e4639e9e9b4717ab4ee417e12963308a5ef9782dc` |
| Negative regression matrix | `7ceaf81b32748c3568c7596e9562516bb20de2fe0ab3e946e47029b9f60c4966` |
| Retrospective observation matrix | `b3c446e9d8a4a44d1d1f84de00855c6d8e822257a2624bd8763c90ada2d54abe` |
| Post-hoc base receipt | `2718e061ea85b5ca43053c055bef5b4915d00dd49afa03e3a0e6bd7bcc949cb3` |
| Retrospective probe | `cddde936b478168cb463df3b5e1cb51a471ec945ccf4b8aaa2e60de4a309f0fc` |
| Final mutation harness | `17793fe0180509e4590db7fd9d6717dffb893f0c57e7a0d34a2c5f7bfc7f4220` |
| Final 24-file runtime/test/config digest-list aggregate | `5675ab3e8f49548d43e6505ec0a5eba900d6ec0d6e757ba2156186193cbea116` |

## 12. Final validator statement

At exact Git head `4fffdfb03fdd4ae6bf6656d2034abd3ef701ae4f`, the bounded diagnostic runtime satisfies the R-WP4-02 fail-closed intent and preserves model semantics. Core B L1 therefore passes this exact candidate with the stated evidence qualifications. The program must remain at `S0_PRE_OUTCOME_BASELINE_CANDIDATE`; Official Golden, Full Replay, model validation, Freeze, Release, Promotion, and Production remain blocked.
