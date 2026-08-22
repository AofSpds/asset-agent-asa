# M3Top3 R-WP4-02 — Final Engineering Validation Receipt v1.0

## Control header

| Field | Value |
|---|---|
| Receipt ID | `AAA-M3TOP3-R-WP4-02-ENGV-FINAL-20260823-0304` |
| Validation authority | `AAA-ENGINEERING-VALIDATOR` |
| Work packet | `R-WP4-02_FAIL_CLOSED_RUNTIME` |
| Repository | `AofSpds/asset-agent-asa` |
| Branch | `aaa-m3top3-p0-runtime-failclosed-remediation-20260823` |
| Exact validated commit | `4fffdfb03fdd4ae6bf6656d2034abd3ef701ae4f` |
| Exact validated tree | `56dec4ec870a596627e250f4b89f95009c43f8cd` |
| Exact source base | `167c1b05e25df658b322cf428c72ce3a4f476544` |
| Branch state at validation | `IDENTICAL` to exact validated commit |
| Base relation | `AHEAD_BY_7`, `BEHIND_BY_0`, merge base equals exact source base |
| Final verdict | **`PASS_WITH_QUALIFICATION / BOUNDED_DIAGNOSTIC_RUNTIME_ONLY`** |
| IVA execution participation | **`NONE`** |
| Completed at | `2026-08-23T03:04:30+09:00` |

This receipt applies only to the exact commit and tree above. Superseded candidates `9f664a…`, `6e4677…`, `6b604ff…`, `e7e68ad…`, `0fbb712…`, and `91f0238…` are rejected and are not admissible substitutes.

## 1. Exact candidate binding

- GitHub commit metadata independently returned commit `4fffdfb03fdd4ae6bf6656d2034abd3ef701ae4f`, tree `56dec4ec870a596627e250f4b89f95009c43f8cd`, and parent `91f0238e557153367bef4334e79cfc9ab1ac0209`.
- The named branch compared identical to the exact commit.
- Local `git hash-object` values for all 24 runtime/test/config files plus the mutation and retrospective harnesses matched the corresponding GitHub blob SHAs: **26/26 match; 0 mismatch**.
- Exact binding manifest: `4fffdfb_git_blob_binding.txt`, SHA-256 `f0baf000a7d4fd2f6d058f8161c0bbc3814553b05b3b421a9018045523159028`.
- Local candidate SHA-256 manifest: `4fffdfb_candidate_sha256.txt`, SHA-256 `cfc72af2c00709dcc67604882f3e029035fd5f0b763035657f6a4a189be18cdc`.
- The mutation harness reported `source_mutated=false`; the exact Git blob binding was checked against the executed local materialization.
- PMO-integrated implementation/test receipts v0.2 (`86af1e…` / `a33a852…`) and v0.3 (`d872dbd…` / `82a569c…`) were reviewed as antecedent evidence, but they identify earlier candidates and smaller test/mutation sets. They are not identity authority for `4fffdfb…`; this exact-Git validation receipt is.

## 2. Independent execution results

| Check | Result | Evidence SHA-256 |
|---|---:|---|
| Full unittest discovery | **120/120 PASS**; failures/errors/skips `0/0/0` | `1216335b4df6fe6dddf404af63b5993e8a353ec89927fb2576a6b70690818f4e` |
| `compileall` / `py_compile` | **PASS / PASS** | `7ab0a529687b05b8aa2e70a04babd6986823c0552525b2cc6262130af1749783` |
| Targeted mutation suite | **33/33 KILLED_RED**; survived/error `0`; source mutated `false` | `c4d77105cb942e5724b636404b206bdb3da441b14a6525607d8294b152f9156d` |
| Independent retrieval-forgery probe | **4/4 REJECTED** | `55f8fd7b35762c589a5df26c83fb09b704c3f291e88a220e71d0f12b7c84daa3` |
| Independent PIT price-lineage forgery probe | **3/3 REJECTED** | `aa2be2231e65b81cb6b3d10e447a3c17a17c43ef6957ad8896d306d96b5ee012` |
| Independent snapshot concurrency probe | **100 rounds / 200 attempts; unclassified `0`; valid finals `100/100`** | `6e8c8f86486bf0005fc78547f0b7bf721687a3bdb236ad9c1abd90cbf57147ba` |

The concurrency probe produced 118 successful create/reuse returns and 82 classified `IMMUTABLE_SNAPSHOT_COLLISION` integrity exits. Every round ended with a valid, readback-verifiable canonical snapshot. No target replacement, byte overwrite, missing final manifest, or unclassified exception was observed.

## 3. Fail-closed and storage findings

### Admission before scoring or output

- PIT violations, missing/null/naive publication timestamps, future publication/effective times, and current-only rows block before scoring.
- `SNAPSHOT_PARTIAL`, `SNAPSHOT_BLOCKED`, `READY + blocker`, malformed JSONL, file-hash mismatch, row-count mismatch, semantic-aggregate mismatch, and lineage mismatch are rejected before scorer or result creation.
- Blocked paths preserve zero scorer calls, zero result writes, and zero ledger mutation where asserted.
- CLI exit contract is exercised: controlled block `2`, integrity `3`, authority `4`; Official-mode and canonical-price authority blocks occur before output.

### Retrieval audit and semantic readback

- Retrieval audit is a separate `retrieval_audit.jsonl` artifact, is not scoreable model input, and is bound by file hash, content aggregate, row count, receipt IDs, and source hashes.
- Builder admission independently reconstructs the selected slice and receipt from the exact admitted raw-source adapter. Provider subclass/instance-method forgery and internally self-consistent receipt forgery fail closed.
- Readback reconciles audit company/cutoff/source/version/count/exclusion/receipt identity 1:1 with PIT and model rows.
- PIT `dataset_refs` must contain exactly one admitted price reference whose `source_id` and `content_hash` match both model input and manifest. All three self-consistent manifest/model drift probes were rejected with integrity exit `3`.

### Price, corporate action, and component identity

- Price semantics are an exact allowlist: `RAW_IMMUTABLE` or `PRICE_CANONICAL`; unknown semantics fail closed.
- `PRICE_CANONICAL` remains globally authority-blocked. A self-authored receipt cannot enable it.
- Single- and multi-component price bytes, absolute paths, component hashes, and aggregate dataset identity are verified. Live bytes are rehashed at construction and before access; Parquet admission precedes connection/query.
- CSV and Parquet corporate-action flag/factor/evidence fields are mapped and validated; missing evidence, missing/invalid factors, duplicate keys, invalid OHLC, or byte mutation are rejected.
- Snapshot and outcome-provider price dataset ID/hash/semantics must match before scoring.

### Immutable publication and ledger ordering

- Snapshot publication uses exclusive target-directory creation, no-replace hardlinks, and manifest-last ordering. Incomplete publication lacks a manifest and is therefore non-enumerable/non-admissible.
- Deterministic staging creation races are classified as `IMMUTABLE_SNAPSHOT_COLLISION` with integrity exit `3`.
- Result artifacts use no-replace immutable publication. Identical bytes may be reused; different bytes under the same identity are rejected without changing the first artifact.
- Ledger admission is serialized, live-reread, append-only, and occurs before result artifact publication. A ledger admission failure leaves no result artifact.

## 4. ENGV-F01–F06 disposition

| Finding | Final disposition |
|---|---|
| `ENGV-F01` retrieval audit optional/unreconciled | **CLOSED** — build and readback semantic reconstruction, exact receipt binding, and independent forgery probes pass. |
| `ENGV-F02` Parquet CA integrity open | **CLOSED** — CA mapping and validation are exercised for CSV and Parquet. |
| `ENGV-F03` mandatory pre-remediation RED receipt absent | **QUALIFIED CLOSED FOR RETROSPECTIVE BEHAVIOR EVIDENCE ONLY** — 33/33 post-hoc observations exist, but no chronological pre-patch execution or byte-exact temporary materialization claim is permitted. |
| `ENGV-F04` retrieval-audit mutation absent | **CLOSED** — audit hash, reconciliation, and independent reconstruction mutations are killed. |
| `ENGV-F05` multi-component price manifest absent | **CLOSED FOR DIAGNOSTIC ADMISSION** — versioned component manifest and exact dataset identity are mandatory and mutation-tested. |
| `ENGV-F06` snapshot Official placeholder bypass | **CLOSED** — snapshot and backtest Official execution are globally hard-blocked with authority exit `4`. |

## 5. Retrospective evidence qualification

The Known-Failure Lock package is internally complete for 33 logical IDs: `27 RED_OBSERVED`, `5 CONTROL_ABSENT_SOURCE_OBSERVED`, and `1 BASE_SAFE_OBSERVED`; collection/import failure was not used as RED evidence.

However, this is **post-hoc retrospective evidence**. Independent byte comparison confirmed that each of the 14 temporary `/tmp/m3top3_exact_base_red_167c1b05` source files contains exactly one extra trailing LF relative to its Git base blob. Removing that single byte yields a 14/14 exact match. Therefore:

- the observed base behavior is reproducible and semantic-equivalent;
- the materialization is **not byte-exact**;
- the evidence is **not chronological TDD/pre-patch execution**;
- it may not be upgraded into an exact-byte or test-first claim.

Key package hashes:

| Artifact | SHA-256 |
|---|---|
| Known-Failure Lock spec | `0b6eaeaba69cf803730f067e4639e9e9b4717ab4ee417e12963308a5ef9782dc` |
| Retrospective observation matrix | `b3c446e9d8a4a44d1d1f84de00855c6d8e822257a2624bd8763c90ada2d54abe` |
| Post-hoc retrospective receipt | `2718e061ea85b5ca43053c055bef5b4915d00dd49afa03e3a0e6bd7bcc949cb3` |
| Retrospective harness | `cddde936b478168cb463df3b5e1cb51a471ec945ccf4b8aaa2e60de4a309f0fc` |

## 6. Model-semantics non-change confirmation

- `tools/m3top3/core.py` Git blob remains `e81561e737c3419013dc1bc5adff5ae258365862`, identical to the exact base.
- `tools/m3top3/model_interface.py` Git blob remains `1bc359a70a399a1eb94ef33703e2e5487afa8006`, identical to the exact base; scorer invocation, raw score production, ranking, tie behavior, and Top3 selection semantics are unchanged.
- `outcome.py` adds price-release verification before the existing calculation path; entry/exit, MFE, MAE, horizon return, and validity formulas are unchanged.
- Other changes add PIT, provenance, authority, integrity, immutable-storage, and CLI firewalls. They do not change model features, feature weights, model decision gates, score formulas, ranking formulas, selection count, or outcome formulas.

## 7. Verdict and claim ceiling

**Engineering verdict: `PASS_WITH_QUALIFICATION` for the exact bounded diagnostic-runtime remediation at commit `4fffdfb03fdd4ae6bf6656d2034abd3ef701ae4f`.**

This permits PMO and the paired governed validators to close the R-WP4-02 runtime-remediation work packet for this exact SHA. It does **not** authorize or establish:

- exact executable pre-outcome v1 recovery;
- model validity, predictive power, alpha, or Champion status;
- canonical price readiness;
- Official mode, Official Golden, or Full Replay;
- Freeze, Promotion, Release, Production, or investment use.

The preserved state is:

| Claim surface | State |
|---|---|
| Model state | `S0_PRE_OUTCOME_BASELINE_CANDIDATE` |
| Official execution | `BLOCKED` |
| `PRICE_CANONICAL` validation | `BLOCKED` |
| Official Golden | `BLOCKED` |
| Full Replay | `BLOCKED` |
| Production authority | `NONE` |
| IVA participation | `NONE` |
