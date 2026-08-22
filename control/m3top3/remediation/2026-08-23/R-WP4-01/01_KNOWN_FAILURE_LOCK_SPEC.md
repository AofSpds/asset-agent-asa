# M3TOP3 R-WP4-01 — Known-Failure Lock Specification

## 0. Control header

| Field | Value |
|---|---|
| Packet | `R-WP4-01-KNOWN-FAILURE-LOCK-20260823-0122` |
| Exact target | `AofSpds/asset-agent-asa@167c1b05e25df658b322cf428c72ce3a4f476544` |
| Branch | `aaa-pmo-m3top3-work-ultra-execution-directive-20260822` |
| Branch/HEAD match | `PASS` |
| Inspection | Read-only GitHub source inspection |
| Repository write/push | `NONE` |
| Test execution | `NOT EXECUTED` |
| IVA execution participation | `NONE` |
| Current claim ceiling | Working infrastructure only; no Official Golden, Full Replay, validation, or promotion claim |

## 1. Verdict

`SPEC_READY / IMPLEMENTATION_RED_REQUIRED / OFFICIAL_EXECUTION_BLOCKED`

The current implementation has positive-path unit coverage but does not fail closed at every P0 boundary. The lock defined here is a mandatory RED suite: each case must initially expose the current defect and later pass only after the minimal remediation patch is applied. A synthetic pass is not an Official Golden receipt.

## 2. Exact observed failure surfaces

1. **Missing or invalid evidence availability can pass, and future-row retrieval has no audit receipt.**  
   `PITGuard.validate_publication()` returns no violation for `None` (`pit_guard.py:37-44`). `validate_model_input()` checks publication fields only when non-null (`pit_guard.py:56-73`). `JsonlFeatureProvider.records_at()` accepts `publication_at=None` and deterministically excludes rows whose publication/effective time is after cutoff, but it returns only the included rows and produces no exclusion count, row locator, reason, or retrieval-receipt hash (`providers.py:69-86`). A longitudinal raw source is allowed to contain later rows; the defect is the missing retrieval audit and the absence of a separately asserted consumed-slice firewall. There is also no `available_before_entry` control.

2. **A leakage finding becomes PARTIAL data, then remains scoreable.**  
   `SnapshotBuilder._build_company()` catches `PITLeakageError`, records a blocker, and continues to construct model features (`snapshot.py:40-72`). `build()` returns `SNAPSHOT_PARTIAL` (`snapshot.py:74-82`), `BatchSnapshotGenerator.run()` writes it and counts it as generated (`snapshot.py:108-122`), and `ValidationRunner.run_snapshot()` never checks `snapshot_status` or `blockers` before scoring (`backtest.py:36-52`).

3. **Stored bytes are not re-verified.**  
   `SnapshotStore.valid_existing()` compares only the manifest's declared semantic hash with the newly built semantic hash (`snapshot.py:88-93`). It does not hash `pit_snapshot.jsonl` or `model_input.jsonl`, verify their row counts, or recalculate the snapshot aggregate. `ValidationRunner.run_snapshot()` loads the manifest and model input directly without an integrity admission step (`backtest.py:36-40`).

4. **Price identity and canonical status are caller assertions.**  
   `CsvPriceProvider` and `DuckDBParquetPriceProvider` accept `dataset_hash` and `semantics` strings without comparing actual bytes or requiring a canonical release receipt (`providers.py:120-152`). A duplicate `(code,date)` is silently last-wins in CSV via the dictionary comprehension and arbitrary-first in DuckDB via `LIMIT 1`. No OHLC invariant or CA completeness gate exists.

5. **Existing result identities are overwriteable.**  
   `SnapshotStore.write()` rewrites fixed date paths (`snapshot.py:94-98`). `ValidationRunner.run_snapshot()` rewrites `runs/<date>.json` (`backtest.py:50-52`). The append-only prediction ledger correctly detects identity collisions, but the snapshot and run artifacts do not inherit that guarantee.

6. **Blocked work reports shell success.**  
   `cli_run_backtest.main()` counts blocked results but always returns `0` (`cli_run_backtest.py:14-24`). `cli_build_snapshots.main()` returns `0` when every PARTIAL snapshot was counted as generated (`cli_build_snapshots.py:12-25`; `snapshot.py:108-122`).

7. **Official scorer/config admission is absent.**  
   `load_scorer()` dynamically imports any configured object and performs no authority, artifact, or config-hash verification (`model_interface.py:69-72`). The only in-repo scorer is explicitly diagnostic (`model_interface.py:75-87`). Example configs contain working/unresolved states, placeholder external paths, and no official scorer release receipt.

## 3. Required negative regression locks

### 3.1 PIT and availability admission

| Test ID | Given | When | Required fail-closed behavior |
|---|---|---|---|
| `KF-PIT-001` | Feature/evidence row with missing or null `publication_at` | Provider or guard admits historical input | Raise/block with `MISSING_PUBLICATION_AT`; no model input row produced |
| `KF-PIT-002` | Timezone-naive `publication_at` | Historical admission | Raise/block with `INVALID_PUBLICATION_DATETIME`; never coerce local timezone |
| `KF-PIT-003` | `available_before_entry=false` | Historical admission | Raise/block with `NOT_AVAILABLE_BEFORE_ENTRY` |
| `KF-PIT-004` | `current_only=true` | Historical admission | Raise/block with `CURRENT_ONLY_FIELD_IN_HISTORY` |
| `KF-PIT-005` | A raw longitudinal source contains rows whose publication/effective/CA-observation time is after cutoff | `records_at()` constructs the consumed slice | `RAW_SOURCE_FUTURE_ROW_EXCLUDED_WITH_AUDIT`: exclude each future row deterministically; admit eligible rows; emit a deterministic retrieval receipt with source/included/excluded counts, row locators or hashes, exclusion reason, cutoff, provider version, and receipt hash. Raw-source presence alone must not block the snapshot |
| `KF-PIT-006` | A post-cutoff publication/effective/CA-observation row reaches the consumed slice because of provider bypass, corruption, or regression | `PITGuard.assert_model_inputs()` validates the consumed slice | `CONSUMED_SLICE_FUTURE_ROW_BLOCKED`: hard-fail with `PIT_PUBLICATION_AFTER_CUTOFF`, `PIT_EFFECTIVE_AFTER_CUTOFF`, or `POST_SNAPSHOT_CA_KNOWLEDGE`; no model input, score, ledger, or result write |

`KF-PIT-005` and `KF-PIT-006` are complementary, not contradictory. The raw data plane may preserve future rows. The retrieval boundary must exclude and account for them, while the consumption boundary must treat any leaked future row as a P0 blocker.

### 3.2 Snapshot state and scoring firewall

| Test ID | Given | When | Required fail-closed behavior |
|---|---|---|---|
| `KF-SNP-001` | Raw feature contains any PIT violation | `SnapshotBuilder.build()` | No scoreable model-input artifact; state `SNAPSHOT_BLOCKED` or exception with stable code |
| `KF-SNP-002` | Manifest status `SNAPSHOT_PARTIAL` | `ValidationRunner.run_snapshot()` | Return/raise `BLOCKED_SNAPSHOT_NOT_READY` before scorer invocation; ledger/output unchanged |
| `KF-SNP-003` | Manifest status `SNAPSHOT_BLOCKED` | `ValidationRunner.run_snapshot()` | Same as above; zero scorer calls |
| `KF-SNP-004` | Non-empty manifest blockers despite claimed READY | Admission | `BLOCKED_MANIFEST_STATE_CONTRADICTION`; no scoring |

### 3.3 Stored-byte integrity

| Test ID | Given | When | Required fail-closed behavior |
|---|---|---|---|
| `KF-INT-001` | Malformed JSONL after snapshot creation | Reuse or backtest | `BLOCKED_INPUT_INTEGRITY`; no scorer call and no overwrite |
| `KF-INT-002` | Valid JSON mutation in `model_input.jsonl` | Reuse or backtest | Actual SHA mismatch detected; `valid_existing=False` or explicit immutable-integrity exception |
| `KF-INT-003` | Mutation in `pit_snapshot.jsonl` | Reuse or backtest | Actual SHA mismatch detected |
| `KF-INT-004` | Manifest row count differs from actual nonblank rows | Admission | `ROW_COUNT_MISMATCH` |
| `KF-INT-005` | File hashes match a forged manifest but recalculated semantic aggregate differs | Admission | `SNAPSHOT_CONTENT_HASH_MISMATCH` |

### 3.4 Price and CA admission

| Test ID | Given | When | Required fail-closed behavior |
|---|---|---|---|
| `KF-PRC-001` | Configured price hash differs from actual component bytes | Provider construction | `PRICE_COMPONENT_HASH_MISMATCH`; no query permitted |
| `KF-PRC-002` | `PRICE_CANONICAL` string without frozen canonical manifest and authority/CA receipts | Provider construction | `PRICE_CANONICAL_ADMISSION_DENIED` |
| `KF-PRC-003` | Duplicate `(security_code,date)` rows | Provider construction/admission | `DUPLICATE_PRICE_KEY`; never last-wins or `LIMIT 1` |
| `KF-PRC-004` | `high < max(open,close)`, `low > min(open,close)`, `low > high`, or non-positive price | Price validation | `INVALID_OHLC` with row locator |
| `KF-PRC-005` | CA flag is true but factor/evidence is missing, zero, or negative | CA admission | `CA_EVIDENCE_INCOMPLETE` or `INVALID_ADJUSTMENT_FACTOR` |
| `KF-PRC-006` | Canonical release contains any unresolved CA candidate | Official outcome admission | `PRICE_CANONICAL_CA_INCOMPLETE`; no VALIDATION status |

### 3.5 Immutable rerun and deterministic result

| Test ID | Given | When | Required fail-closed behavior |
|---|---|---|---|
| `KF-IMM-001` | Existing snapshot identity and identical verified bytes | Rerun | Reuse without modifying bytes or timestamps |
| `KF-IMM-002` | Existing date/identity with different bytes or semantic hash | Snapshot write | Immutable collision; existing files unchanged; new revision must use a new identity/path |
| `KF-IMM-003` | Same snapshot/scorer/config identity produces different ranking/result bytes | Validation rerun | `NONDETERMINISTIC_RERUN` or immutable result collision; first result unchanged |
| `KF-IMM-004` | Same run ID and identical result bytes | Validation rerun | Reuse, not overwrite |

### 3.6 CLI status and official-model admission

| Test ID | Given | When | Required fail-closed behavior |
|---|---|---|---|
| `KF-CLI-001` | Any tie-policy blocked result | Backtest CLI completes | Exit `2`; summary reports blocked and admitted counts separately |
| `KF-CLI-002` | Any PARTIAL/BLOCKED snapshot in build range | Snapshot CLI completes | Exit `2`; not counted as generated/admitted |
| `KF-CLI-003` | Hash/JSONL/price integrity failure | Either CLI | Exit `3` with stable integrity code |
| `KF-MOD-001` | Missing/unimportable scorer plugin | Official-mode admission | Exit `4`; no data read or output write |
| `KF-MOD-002` | Diagnostic fixture scorer requested in official mode | Official-mode admission | `OFFICIAL_SCORER_ADMISSION_DENIED`, exit `4` |
| `KF-MOD-003` | Missing scorer artifact hash, frozen config bytes/hash, baseline identity, or authority receipt | Official-mode admission | Block before scoring, exit `4` |
| `KF-MOD-004` | Declared `config_hash` differs from actual canonical config bytes | Official-mode admission | `SCORER_CONFIG_HASH_MISMATCH`, exit `4` |
| `KF-MOD-005` | Working/example/unresolved placeholder config used in official mode | Official-mode admission | `PLACEHOLDER_CONFIG_NOT_ADMISSIBLE`, exit `4` |

## 4. Standard exit contract

| Exit | Meaning |
|---:|---|
| `0` | Every requested unit was admitted and completed; zero blocked/integrity/admission findings |
| `2` | Controlled block: PARTIAL/BLOCKED snapshot, tie-control block, or incomplete execution accounting |
| `3` | Artifact/data integrity failure: hash, JSONL, row count, duplicate key, OHLC, or CA integrity |
| `4` | Configuration/model authority admission failure |
| `1` | Unclassified internal error only; must not mask a classified code |

## 5. Acceptance gates

The Known-Failure Lock is accepted only when all conditions hold:

1. Every matrix ID exists as an executable automated test with a deterministic fixture.
2. A pre-remediation RED receipt records that the tests expose the defect at exact HEAD or its exact implementation-equivalent descendant.
3. The remediation commit makes the same tests GREEN without weakening expected codes or assertions.
4. Full existing infrastructure tests also pass.
5. Mutation checks prove that removing each admission/integrity guard makes its paired test fail.
6. No PARTIAL/BLOCKED artifact reaches the scorer, prediction ledger, outcome engine, or run-result directory.
7. Every historical retrieval has a deterministic inclusion/exclusion receipt, and the receipt totals reconcile to the raw candidate set.
8. Removing either future-row exclusion/audit or consumed-slice hard-fail must turn its paired regression test RED.
9. No test or implementation packet assigns IVA an execution, authoring, intermediate review, or evidence-production role.

## 6. Non-claims

- This specification is not proof that any implementation patch exists.
- No test was executed in this read-only inspection packet.
- Passing these tests would establish fail-closed infrastructure behavior only, not model identity, predictive power, Official Golden, Full Replay, or production readiness.
