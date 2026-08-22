# R-WP4-01 — Minimal Implementation Patch and Test-File Plan

## 1. Patch objective

Make every known P0 input, state, integrity, immutability, CLI, and official-scorer boundary fail closed without changing the M3Top3 feature semantics, weights, ranking objective, or outcome definition. This packet does not authorize an official scorer reconstruction or replay.

## 2. Minimal source patch set

### P1 — Central admission/error contract

**Add:** `tools/m3top3/admission.py`

Provide:

- `M3Top3AdmissionError(code, message, details=None, exit_code=...)`.
- Stable exit constants: `EXIT_BLOCKED=2`, `EXIT_INTEGRITY=3`, `EXIT_AUTHORITY=4`.
- `verify_snapshot_artifacts(snapshot_dir)`:
  - parse manifest and both JSONL files;
  - require `SNAPSHOT_READY` and empty blockers;
  - hash actual UTF-8 bytes;
  - verify declared file hashes and nonblank row counts;
  - recalculate the semantic aggregate using the same canonical algorithm as build;
  - reject contradictory state.
- `verify_price_release(provider, admission_config)`:
  - compare actual component hashes to a versioned manifest;
  - require unique key and OHLC checks;
  - require frozen canonical/CA receipt for `PRICE_CANONICAL`.
- `verify_official_scorer(scorer, config_bytes, receipt)`:
  - reject diagnostic/test scorer;
  - match model ID/version/schema/feature set, scorer artifact hash, and actual config hash;
  - reject `WORKING`, `UNRESOLVED`, `EXAMPLE`, or missing authority values in official mode.

This single new module keeps classification logic out of CLI code and prevents inconsistent exit behavior.

### P2 — PIT guard and provider fail-closed behavior

**Modify:** `tools/m3top3/pit_guard.py`

- `publication_at is None` → `MISSING_PUBLICATION_AT`.
- Timezone-naive/invalid publication → `INVALID_PUBLICATION_DATETIME`.
- `available_before_entry is False` → `NOT_AVAILABLE_BEFORE_ENTRY`.
- Validate the **consumed slice** for `publication_at`, `effective_at`, `as_of`, and `corporate_action_observed_at` with stable codes.
- Any consumed row after cutoff hard-fails as `CONSUMED_SLICE_FUTURE_ROW_BLOCKED`; this guard is independent of provider filtering and protects against bypass, corruption, and regression.
- Keep `current_only=true` and forbidden future-field checks.

**Modify:** `tools/m3top3/providers.py`

- Preserve longitudinal raw stores as valid containers of later rows. `records_at()` must select the historical slice deterministically and return a typed `RetrievalSlice(rows, audit)` (or equivalent rows + receipt interface).
- For every raw row after cutoff by publication, effective, or CA-observation time, exclude it from the consumed slice and emit `RAW_SOURCE_FUTURE_ROW_EXCLUDED_WITH_AUDIT`. The receipt must contain source/included/excluded counts, stable row locator or hash, reason, cutoff/timezone, provider/source version, and a deterministic receipt hash. Totals must reconcile exactly.
- Raw-source future rows alone do **not** block the snapshot. Missing/unreconciled audit data does block admission, and any future row that reaches the consumed slice is then hard-failed by `PITGuard`.
- Validate every price row on construction/query admission.
- Reject duplicate `(code,date)` in both CSV and DuckDB paths. Replace `LIMIT 1` with an explicit uniqueness assertion.
- Verify actual component byte hashes against a manifest before any price query.
- Do not allow `PRICE_CANONICAL` without a frozen canonical release and complete CA receipt.

### P3 — Snapshot firewall and immutable storage

**Modify:** `tools/m3top3/snapshot.py`

- Do not catch a PIT violation and continue feature materialization into a scoreable view.
- Bind each provider retrieval-receipt hash and reconciled included/excluded counts into the snapshot manifest/lineage. Reject a missing, contradictory, or unreconciled receipt.
- Classify blocked/partial dates separately in `BatchResult`; do not count them as generated/admitted.
- `SnapshotStore.valid_existing()` must call actual-byte verification.
- `SnapshotStore.write()` must use atomic writes and create-only/compare-identical semantics.
- Existing identity + different bytes → immutable collision. A changed snapshot must receive a new revision/identity/path; never overwrite.
- If a diagnostic quarantine artifact is retained, place it outside the scoreable snapshot root and mark it non-admissible.

### P4 — Backtest admission and immutable result

**Modify:** `tools/m3top3/backtest.py`

- Run `verify_snapshot_artifacts()` before constructing output directories, loading the scorer over inputs, or touching ledgers.
- Verify price/scorer admission before scoring.
- Persist full ranking through an append-only result store keyed by snapshot content hash + model/scorer artifact hash + config hash + validation protocol + price release hash.
- Same identity/same bytes → `REUSED`; same identity/different bytes → `NONDETERMINISTIC_RERUN`.
- Tie block produces a structured blocked receipt and no prediction/outcome ledger writes.

**Modify:** `tools/m3top3/ledger.py`

- Reuse the existing append-only collision logic for a new run-result ledger/artifact index.
- Do not weaken the existing prediction-ledger immutability behavior.

### P5 — CLI preflight and exit status

**Modify:** `tools/m3top3/cli_build_snapshots.py`

- Preflight configuration and price release.
- Return `2` if any requested date is partial/blocked or accounting is incomplete.
- Return `3` for integrity failures and `4` for authority/config admission failures.

**Modify:** `tools/m3top3/cli_run_backtest.py`

- Preflight official/diagnostic mode explicitly.
- Stop before iteration if scorer/config/price admission fails.
- Return `2` for any controlled blocked run or tie, `3` for integrity, `4` for scorer/config authority, `0` only if all requested runs are admitted.
- Summary must expose `requested`, `admitted`, `blocked`, `failed_integrity`, and `failed_authority` counts.

### P6 — Config schema

**Modify examples only as non-official examples:**

- `tools/m3top3/configs/snapshot.example.json`
- `tools/m3top3/configs/backtest.example.json`

Add explicit `execution_mode: DIAGNOSTIC`, manifest paths, hash algorithms, and `official_admission: false`. Do not convert examples into official configs. Official config and scorer receipts must be separate frozen artifacts created under their proper authority.

## 3. Test file changes

Keep the existing `tools/m3top3/tests/test_infrastructure.py` intact except where its positive assumptions conflict with fail-closed behavior. Specifically:

- **Shared `setUp` / `write_price_csv` fixture:** replace arbitrary `dataset_hash="abc"` with the actual fixture-byte hash and an explicit diagnostic price manifest. Split the current mixed universe into `partial_builder` (keeps C3 unresolved for eligibility semantics) and `ready_builder` (all execution-eligible) so positive persistence tests do not depend on a PARTIAL snapshot.
- **`test_07_eligibility_semantics_preserved`:** retain the TRUE/FALSE/UNRESOLVED assertion on `partial_builder`; additionally assert the resulting state is non-admissible.
- **`test_16_batch_resume_reuses`:** run on `ready_builder`; assert actual-byte verification, identical-byte reuse, no mtime/byte mutation, and add a separate corruption rejection case under KF-INT-002/003.
- **`test_22_backtest_runner_separates_outcome`:** declare `execution_mode=DIAGNOSTIC` explicitly and provide a verified diagnostic price manifest. It must not accidentally exercise official admission.
- **`test_23_scale_420_dates_and_resume`:** use the actual scale CSV hash, an explicit diagnostic manifest, a READY builder, and byte-verified reuse.
- **`test_24_failed_date_retry_works`:** use `ready_builder`; a transient exception may retry, while a classified PIT/integrity block must not be retried into success.
- **`test_25_representative_historical_regression_dates`:** use actual fixture hashes and explicit diagnostic admission; retain its non-official character.
- Retain `test_03`–`test_06` PIT/future-field positives, `test_17_prediction_ledger_immutable`, and `test_19_tie_policy_blocks_official_resolution`; extend them with stable error-code assertions rather than weakening them.

Add focused files:

| Test file | Matrix coverage |
|---|---|
| `test_known_failures_pit.py` | KF-PIT-001…006 |
| `test_known_failures_snapshot.py` | KF-SNP-001…004 |
| `test_known_failures_integrity.py` | KF-INT-001…005 |
| `test_known_failures_price.py` | KF-PRC-001…006 |
| `test_known_failures_immutability.py` | KF-IMM-001…004 |
| `test_known_failures_cli.py` | KF-CLI-001…003 and exit mapping |
| `test_known_failures_model_admission.py` | KF-MOD-001…005 |

Each test must assert:

1. the stable error/status code;
2. the shell exit where applicable;
3. zero scorer calls when admission fails;
4. zero mutation of snapshot/result/ledger files;
5. exact prior bytes remain unchanged after collision;
6. no `VALIDATION` state can arise from raw or unadmitted canonical price.
7. KF-PIT-005 admits the eligible historical slice while proving all raw future rows were excluded and reconciled in a deterministic audit receipt.
8. KF-PIT-006 injects publication/effective/CA future rows directly into the consumed slice and proves that each variant hard-fails before any downstream write.

### Acceptance counts

| Acceptance measure | Minimum |
|---|---:|
| Logical Known-Failure IDs | `33 / 33` present |
| Executed negative cases after parameter expansion | `>= 44` |
| Stable error/status-code assertions | `>= 33` |
| Classified CLI exit assertions | `>= 8` (`CLI` 3 + model/config admission 5) |
| Admission failure tests proving zero scorer calls and zero output/ledger mutation | `>= 12` |
| Immutable prior-byte preservation assertions | `4` |
| Existing infrastructure tests retained after fixture correction | `25 / 25` passing |
| Full combined suite | `>= 69` executed cases, `0` failures, `0` errors, `0` unexpected skips |
| Targeted guard mutation checks | `>= 14`, including separate retrieval-audit and consumed-slice firewall mutations; each paired test must turn RED |

The `>=44` negative executions arise from the 33 logical IDs plus required parameterization: both string/datetime timezone-naive inputs; KF-PIT-005 raw-source publication/effective/CA exclusion-audit variants; KF-PIT-006 consumed-slice publication/effective/CA hard-fail variants; duplicate-key checks in CSV and DuckDB paths; four invalid-OHLC shapes; and three invalid CA-factor/evidence shapes.

## 4. Required execution sequence

1. Add the tests and capture the RED receipt on an isolated implementation worktree.
2. Implement P1–P2; make PIT/price admission tests green.
3. Implement P3; make snapshot/integrity/immutability tests green.
4. Implement P4; make scoring firewall/result immutability tests green.
5. Implement P5–P6; make CLI/scorer-admission tests green.
6. Run the complete existing + new suite.
7. Run targeted mutation checks for each P0 guard.
8. Produce implementation and validator receipts; PMO integrates. IVA remains outside execution.

## 5. Stop conditions

- Official scorer/config bytes cannot be identified exactly.
- A canonical price release cannot provide actual component hashes and complete CA evidence.
- The implementation must change model semantics to satisfy an infrastructure test.
- A patch would overwrite an existing snapshot or result rather than create a new identity.
- A test passes only by changing the expected status/exit to a weaker condition.
