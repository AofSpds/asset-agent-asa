# R-WP4-02 Control Validation Receipt v0.1

## 1. Control header

| Field | Locked value |
|---|---|
| Receipt ID | `R-WP4-02-CTLV-RECEIPT-v0.1` |
| Validator persona | `AAA-CONTROL-VALIDATOR (CTLV)` |
| Paired author | `AAA-CONTROL-ARCHITECT` |
| Repository | `AofSpds/asset-agent-asa` |
| Branch locator | `aaa-m3top3-p0-runtime-failclosed-remediation-20260823` |
| Exact base | `167c1b05e25df658b322cf428c72ce3a4f476544` |
| Exact candidate | `4fffdfb03fdd4ae6bf6656d2034abd3ef701ae4f` |
| Candidate tree | `56dec4ec870a596627e250f4b89f95009c43f8cd` |
| Candidate parent | `91f0238e557153367bef4334e79cfc9ab1ac0209` — rejected/superseded |
| Local runtime mirror | `/workspace/scratch/577256efb437/remediation/runtime_checkout` |
| Validation time | `2026-08-23 03:03:53 KST (+0900)` |
| Implementation edits by CTLV | `NONE` |
| Git writes by CTLV | `NONE` |
| IVA execution participation | `NONE` |
| Final CTLV verdict | `PASS_WITH_EVIDENCE_QUALIFICATION` |

## 2. Executive verdict

CTLV independently admits exact candidate `4fffdfb03fdd4ae6bf6656d2034abd3ef701ae4f` as a bounded, diagnostic **fail-closed infrastructure candidate** for R-WP4-02.

The candidate closes the reviewed control defects for immutable/create-only publication, classified failure exits, admission-before-output, artifact and semantic verification, retrieval reconciliation, price lineage, multi-component price identity, and global Official/PRICE_CANONICAL claim locks. The final 100-round concurrent identical-write probe produced no raw exception and no invalid final snapshot.

This is not model validation and does not authorize Official Golden, Full Replay, Freeze, Promotion, Release, or Production.

## 3. Exact Git lineage and byte evidence

| Check | Independent observation | Result |
|---|---|---|
| Branch HEAD | GitHub branch resolved to exact `4fffdfb03fdd4ae6bf6656d2034abd3ef701ae4f` | `PASS` |
| Tree identity | GitHub commit tree is exact `56dec4ec870a596627e250f4b89f95009c43f8cd` | `PASS` |
| Base ancestry | Compare status `ahead`; merge base exact `167c1b05...`; ahead `7`, behind `0` | `PASS` |
| Candidate surface | Base-to-candidate compare contains `56` changed files | `PASS` |
| Git/local byte comparison | Local/source mapping Git blob hashes: `56/56 MATCH`, `0` missing, `0` mismatch | `PASS` |
| Denominator correction | Git blob `4c7849b7105fe043ed3bed045302aff56dda52c2`; SHA-256 `02bde437c04b1cc3d314b30e9bdd41bdb9a9164d0d2df4468728bdab8089eb62`; `325454` bytes | `PASS` |
| Final snapshot blob | `tools/m3top3/snapshot.py` = Git blob `b3f6af803f96798ce572badeaeedf03b03929017` | `PASS` |
| Final immutability test blob | `test_known_failures_immutability.py` = Git blob `d1616f865283c8cd97ade1d32744eb5a74d447a3` | `PASS` |
| Final mutation harness blob | `run_targeted_mutation_checks.py` = Git blob `2491543578e9a6832bdc7aa4a397f33f265adcc4` | `PASS` |

The branch is unprotected and the commit is unsigned. This is recorded as a non-blocking repository-control residual because this receipt is keyed to the immutable commit and tree, not to the mutable branch name. A later merge/release must re-bind to an exact SHA and must not rely on the branch locator alone.

## 4. Independent execution evidence

| Evidence | Command / probe | Observation | Result |
|---|---|---|---|
| Full test suite | `python -m unittest discover -v -s tools/m3top3/tests -p 'test*.py'` | `120/120` passed; `0` failure/error/skip; exit `0` | `PASS` |
| Compile-all | `python -m compileall -q tools/m3top3` | exit `0` | `PASS` |
| Py-compile | `python -m py_compile tools/m3top3/*.py tools/m3top3/tests/*.py` | exit `0` | `PASS` |
| Mutation controls | `python ../r_wp4_failclosed_impl/run_targeted_mutation_checks.py .` | `33/33 KILLED_RED`; `0` survivor/error; `source_mutated=false` | `PASS` |
| Critical focused suite | Eight concurrency, manifest-last, price-lineage, component-manifest and global-lock tests | `8/8` passed | `PASS` |
| Concurrent identical writes | Independent two-writer probe, `100` isolated rounds | `71` rounds = one success plus classified `IMMUTABLE_SNAPSHOT_COLLISION/3`; `29` rounds = two safe success/reuse completions; raw exceptions `0`; invalid final snapshots `0` | `PASS` |

The requested historical suite and mutation minimums were superseded by the larger final frozen surface. CTLV executed the complete `120`-test suite and all `33` registered mutation controls rather than stopping at the earlier `97`/`18` counts.

## 5. Control findings

| Control objective | CTLV finding | Result |
|---|---|---|
| Snapshot create-only publication | Canonical directory is claimed with exclusive `mkdir`; files are published using no-replace hardlinks; `manifest.json` is published last. A pre-existing empty canonical target retains its inode and bytes. | `PASS` |
| Staging race classification | A deterministic staging-directory race is normalized to `IMMUTABLE_SNAPSHOT_COLLISION`, integrity exit `3`; no raw `FileExistsError` escaped in the 100-round probe. | `PASS` |
| Incomplete publication quarantine | Injected manifest-link failure leaves no canonical manifest, so the incomplete target is non-enumerable and non-admissible; no prior target is overwritten. | `PASS` |
| Result create-only write | Result artifacts use candidate bytes plus no-replace hardlink; identical bytes reuse, conflicting same identity blocks with `NONDETERMINISTIC_RERUN/3`. | `PASS` |
| Append-only ledger | Exclusive file lock, live on-disk reread, duplicate identity comparison, append-only bytes, flush and fsync are enforced. | `PASS` |
| Admission before result write | Snapshot and live price admission complete before scorer/output. Prediction-ledger admission occurs before result artifact publication, so a ledger collision cannot leave a new result artifact. | `PASS` |
| Classified exits | Blocked, integrity, and authority failures retain exit `2`, `3`, and `4`; CLIs return non-zero for blocked/corrupt/unauthorized states. | `PASS` |
| Manifest/file/readback verification | Manifest control identity, actual JSONL bytes, declared row counts, retrieval aggregate and complete semantic aggregate are recomputed before scoring/reuse. | `PASS` |
| Retrieval audit reconciliation | PIT/model/audit identities are one-to-one; deterministic receipt IDs, cutoff/company keys, counts, exclusions, source hashes and independent reconstruction are verified. | `PASS` |
| PIT price dataset binding | Each PIT row must contain exactly one `SOURCE_DATASET` reference matching manifest/model `price_dataset_id` and exact `price_dataset_hash`; self-consistent forged drift is blocked. | `PASS` |
| Snapshot-to-outcome price binding | Snapshot manifest price dataset ID/hash/semantics must equal the live outcome provider lineage before scoring/outcomes. | `PASS` |
| Component manifest binding | Live component paths and bytes are rehashed; multi-component dataset identity and versioned component manifest must match exactly before query/use. | `PASS` |
| Official global claim lock | `OFFICIAL_EXECUTION_ENABLED=False`; self-authored model identity/receipt cannot enable Official execution. | `PASS` |
| PRICE_CANONICAL global claim lock | `PRICE_CANONICAL_VALIDATION_ENABLED=False`; self-asserted canonical/CA receipts cannot create Validation authority. | `PASS` |
| S0 preservation | Governance artifacts retain `S0_PRE_OUTCOME_BASELINE_CANDIDATE`; no model validity, predictive-power, Freeze, Golden or Replay transition is asserted. | `PASS` |
| IVA separation | Known-Failure Lock, G0 receipts and remediation receipts bind `IVA_EXECUTION_PARTICIPATION=NONE`; CTLV is the internal control validator, not IVA. | `PASS` |

## 6. Rejected-candidate closure trail

| Candidate | CTLV/ENGV control finding | Disposition |
|---|---|---|
| `e7e68ad6244a36fac2e679a26eaef191810df411` | Self-consistent PIT `dataset_refs` could drift from manifest/model/outcome price lineage. | `REJECTED / SUPERSEDED` |
| `0fbb7128c0f15481187ddc3a151d8c760d6c2aed` | POSIX directory rename could replace a concurrently created empty canonical target. | `REJECTED / SUPERSEDED` |
| `91f0238e557153367bef4334e79cfc9ab1ac0209` | Concurrent identical writes could leak raw `FileExistsError` from deterministic staging `mkdir`, producing unclassified exit `1`. | `REJECTED / SUPERSEDED` |
| `4fffdfb03fdd4ae6bf6656d2034abd3ef701ae4f` | Exclusive target/no-replace publication, exact price binding, and classified staging race all passed final independent validation. | `CTLV PASS_WITH_EVIDENCE_QUALIFICATION` |

No CTLV PASS is transferable to any rejected parent or to a later descendant. Any byte change requires a new exact-SHA validation receipt.

## 7. Retrospective base-evidence qualification

The post-hoc base receipt
`05_POST_HOC_RETROSPECTIVE_EXACT_BASE_RED_RECEIPT_v0.2.json`
has SHA-256 `2718e061ea85b5ca43053c055bef5b4915d00dd49afa03e3a0e6bd7bcc949cb3` and records all `33` logical IDs:

- `27` = `RED_OBSERVED`
- `5` = `CONTROL_ABSENT_SOURCE_OBSERVED`
- `1` = `BASE_SAFE_OBSERVED`

However, the retrospective `/tmp` base materialization contained one additional trailing LF per materialized base file. The observations are semantically equivalent and reproducible, but that materialization is not byte-exact to the Git base. It was also executed after implementation.

Therefore its admissible label is:

`POST_HOC_SEMANTIC_EQUIVALENT_BASE_OBSERVATION / NOT_BYTE_EXACT / NOT_CHRONOLOGICAL_TDD`

This qualification does not negate the final candidate's independently passing regression and mutation closure. It does prohibit representing the receipt as exact-byte historical RED proof or chronological test-first evidence.

## 8. Claim ceiling and preserved locks

| Claim/state | Status after this receipt |
|---|---|
| Bounded diagnostic fail-closed infrastructure | `ADMISSIBLE AT EXACT 4fffdfb...` |
| Model state | `S0_PRE_OUTCOME_BASELINE_CANDIDATE` |
| Predictive power / alpha | `NOT_VALIDATED` |
| Exact executable v1 recovery | `NOT ESTABLISHED BY THIS RECEIPT` |
| Official Golden | `BLOCKED` |
| Official Full Replay | `BLOCKED` |
| PRICE_CANONICAL Validation | `BLOCKED` |
| Freeze / Promotion / Release / Production | `NOT AUTHORIZED` |
| IVA execution role | `NONE` |

## 9. Final CTLV statement

`CONTROL_VALIDATION_PASS / R-WP4-02_FAIL_CLOSED_INFRASTRUCTURE_ADMISSIBLE / EXACT_SHA_ONLY / EVIDENCE_QUALIFIED`

CTLV finds no remaining blocker within the bounded R-WP4-02 control scope at exact commit `4fffdfb03fdd4ae6bf6656d2034abd3ef701ae4f`. PMO may integrate this receipt as one required internal validation input. Any higher state transition or Official execution remains governed by separate unmet evidence and Owner-reserved gates.
