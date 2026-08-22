# M3TOP3 R-WP4-02 — Engineering Validation Receipt

## Control header

| Field | Value |
|---|---|
| Receipt ID | `AAA-M3TOP3-R-WP4-02-ENGV-20260823-0157-01` |
| Validator persona | `AAA-ENGINEERING-VALIDATOR` |
| Validation role | Paired engineering validator; implementation files not edited |
| Exact base | `AofSpds/asset-agent-asa@167c1b05e25df658b322cf428c72ce3a4f476544` |
| Local candidate | `/workspace/scratch/577256efb437/remediation/runtime_checkout` |
| Candidate receipt SHA-256 | MD `717e698eec9c5d2a5903aa1df8f8304de1a7fea9876b4e9af097c870f505606c`; JSON `0564ce375026ac99496a3ce385022e481d9ae8065131f39f3a12ac332876026a` |
| Mutation harness SHA-256 | `9c00a88b69293fa45958e147882f98b9cc275dbea276681c8bd78b2a3c87137a` |
| IVA execution participation | `NONE` |
| Completed at | `2026-08-23 01:57:23 KST` |
| Verdict | `FAIL / REMEDIATION_REQUIRED / REVALIDATION_REQUIRED` |

## 1. Executive verdict

The frozen local candidate is reproducibly GREEN for its present 80-test suite and kills all 15 configured mutations. It also preserves the exact base model/ranking implementation and does not change outcome formulas. These facts are necessary but not sufficient for the Known-Failure Lock.

The candidate is **not eligible for engineering PASS** because required fail-closed surfaces remain open: historical retrieval audit is optional and unreconciled, parquet corporate-action integrity is not enforced, the mandated pre-remediation RED receipt is absent, the mutation set omits the separately required retrieval-audit mutation, multi-component price admission is not bound to a versioned component manifest, and the snapshot CLI accepts `OFFICIAL` mode with working/default placeholder authority values.

No Official Golden, Full Replay, model-state advancement, Freeze, Release, Promotion, or Production claim is authorized.

## 2. Exact-byte and independent execution evidence

### 2.1 Supplied artifact identity

All 21 file digests declared in the implementation receipt matched the frozen local bytes. Digest mismatches: `0`.

### 2.2 Independent executions

| Check | Independent result | Evidence digest |
|---|---:|---|
| Full unittest discovery | `80 run / 80 pass / 0 fail / 0 error / 0 skip` | transcript SHA-256 `aa631780a0ab562a8f17844c04787a4b3274c7bcfe60d766a8cba637ebfd3ebe` |
| Existing infrastructure suite | `25 / 25 PASS` | included in full transcript |
| Logical Known-Failure IDs present by executable test name | `33 / 33` | local AST/name scan |
| Parameterized known-failure-prefixed executions | `47` | local AST/name scan; threshold `>=44` |
| `compileall` | `PASS` | independent command |
| `py_compile` | `PASS` | independent command |
| Configured mutation harness | `15 / 15 KILLED_RED` | transcript SHA-256 `e537a2c49509badd75ab146f63b82df11d23121917ca40ecc628c44e684593d2` |
| Mutation isolation | `source_mutated=false` | harness output |
| Candidate file-hash list | `PASS` | SHA-256 `1116a75e733f768b930a987af74640e01379efde95b3666a837866a4c16b928c` |

Commands independently executed:

```text
python -m unittest discover -s tools/m3top3/tests -p 'test_*.py' -v
python -m compileall -q tools/m3top3
python -m py_compile tools/m3top3/*.py
python remediation/r_wp4_failclosed_impl/run_targeted_mutation_checks.py remediation/runtime_checkout
```

## 3. Confirmed controls

- READY-state and empty-blocker verification occurs before scorer invocation.
- Stored PIT, model-input, and retrieval-audit JSONL bytes, counts, and aggregate hashes are reverified.
- Raw longitudinal future rows are excluded by the native feature providers, while a future row reaching the consumed slice is hard-blocked.
- Retrieval-audit data is stored separately from `pit_snapshot.jsonl` and `model_input.jsonl`; the native-provider audit file is hash-bound by the manifest.
- Snapshot publication uses a staged directory and refuses an existing conflicting target.
- Same result identity with different bytes is rejected, while identical bytes are reused.
- Ledger parent directories are not created on object construction, so classified pre-admission blocks leave no output directory.
- CLI exits `2/3/4` are exercised for the implemented controlled-block, integrity, and authority cases.
- Diagnostic scorer use in backtest `OFFICIAL` mode is rejected.

## 4. Material findings

### `ENGV-F01` — Retrieval audit is optional and unreconciled (`P0`, blocking)

`SnapshotBuilder._build_company()` obtains `last_retrieval_receipt` with `getattr(..., None)` and returns `None` when the provider does not expose a receipt. `build()` simply omits that audit and can still produce `SNAPSHOT_READY`. Neither build nor readback verifies:

- one receipt per historical retrieval/company;
- `source_matching_rows == selected_rows + excluded_rows`;
- `selected_rows` against the actual consumed rows;
- required receipt fields or the deterministic receipt ID.

Independent probe result:

```json
{"audit_rows":0,"blockers":[],"probe":"NO_AUDIT","status":"SNAPSHOT_READY","store_admitted":true}
{"audit_rows":1,"blockers":[],"probe":"CONTRADICTORY_AUDIT","status":"SNAPSHOT_READY","store_admitted":true}
```

This violates Known-Failure Lock acceptance item 7 and patch plan P3: missing, contradictory, or unreconciled retrieval receipts must block admission.

### `ENGV-F02` — Parquet corporate-action integrity remains open (`P0`, blocking)

`DuckDBParquetPriceProvider` discovers optional CA columns but its constructor checks only duplicate keys and OHLC. Its `row()` and `rows()` queries select only date/code/OHLC and construct `PriceRow` without CA flag, adjustment factor, or evidence ID. Therefore a parquet row with `corporate_action_flag=true` and missing/invalid factor or evidence is admitted and silently loses its CA fields.

Independent probe result:

```json
{"ca_columns_seen":["adjustment_factor","corporate_action_evidence_id","corporate_action_flag"],"constructed":true,"probe":"DUCKDB_CA_COLUMNS_IGNORED"}
```

This leaves `KF-PRC-005` open on the production parquet adapter. Current negative tests cover only the CSV adapter.

### `ENGV-F03` — Mandatory pre-remediation RED receipt is absent (`P0`, blocking evidence gap)

Known-Failure Lock acceptance item 2 and the ordered implementation sequence require the newly materialized tests to be executed against the exact base/pre-patch runtime and captured as RED before remediation. No such receipt exists in the supplied implementation packet. The regression matrix remains marked `RED_SPECIFIED_NOT_RUN`.

Mutation testing on the post-patch candidate is useful but does not replace the required base/pre-patch RED receipt.

### `ENGV-F04` — Required retrieval-audit mutation is absent (`P0`, blocking evidence gap)

The patch plan requires at least 14 mutations **including separate retrieval-audit and consumed-slice firewall mutations**. The 15 configured mutations include consumed-publication and consumed-effective guards but none removes or corrupts retrieval-audit generation, reconciliation, persistence, or hash binding. Because the runtime has no mandatory audit/reconciliation guard, no such mutation can presently be killed.

### `ENGV-F05` — Multi-component price bytes are not bound to a versioned component manifest (`P0`, blocking)

The provider computes a single aggregate from component content hashes, while `verify_price_release()` compares only `dataset_hash == actual_dataset_hash`. It does not consume the example config's `price_manifest_path`, verify an expected path-to-component-hash mapping, or bind canonical authority/CA receipts to that manifest/dataset identity.

Independent probe result:

```json
{"component_count":2,"constructed":true,"manifest_supplied":false,"probe":"MULTI_COMPONENT_NO_MANIFEST"}
```

This does not satisfy patch plan P1/P2's versioned component-manifest admission contract.

### `ENGV-F06` — Snapshot CLI permits `OFFICIAL` with working/default placeholders (`P0`, blocking)

`cli_build_snapshots.main()` accepts either `DIAGNOSTIC` or `OFFICIAL` but performs no official placeholder/authority preflight. When omitted, its defaults include `m3top3-input-v0.1-working` and `RECONSTRUCTION_v0.1_WORKING`; working universe/feature authority values are also accepted.

Independent preflight probe result:

```json
{"exit":0,"probe":"OFFICIAL_SNAPSHOT_WORKING_DEFAULTS","summary":{"accounting_pass":true,"admitted":0,"blocked":0,"failed":0,"failed_authority":0,"failed_integrity":0,"generated":0,"requested":0,"reused":0}}
```

This violates the official-mode placeholder fail-closed rule. The current `KF-MOD-005` test exercises only `verify_official_scorer()`, not the snapshot CLI.

## 5. Model-semantics review

Exact content comparison to the base commit confirmed these files are byte-identical:

- `tools/m3top3/core.py`
- `tools/m3top3/model_interface.py`
- `tools/m3top3/README.md`
- `tools/m3top3/__init__.py`

The base-to-candidate diff in `snapshot.py` preserves the pre-existing feature extraction, `price_close`/`market_cap` defaults, eligibility logic, and model-input schema fields; changes add PIT/audit/state/storage firewalls. `backtest.py` preserves scorer invocation, `RankingEngine.rank()`, Top3 selection, outcome construction, and metric formulas; changes add admission and immutable identity/storage. `outcome.py` changes only by calling `verify_price_release()` before the existing formula path.

Therefore the reviewed candidate contains **no detected feature-definition, weight, gate, ranking-objective, selection, or outcome-formula semantic change** relative to the exact base. This finding does not cure the blocking implementation/evidence gaps above.

## 6. Required remediation before revalidation

1. Make the provider contract return a typed retrieval slice/receipt; block missing receipts.
2. Validate required audit fields, deterministic receipt ID, one-receipt-per-retrieval coverage, and exact count reconciliation at build and readback.
3. Add negative tests for no receipt, contradictory counts, mismatched selected count, forged receipt ID, and audit persistence/hash-binding.
4. Add a dedicated retrieval-audit mutation and prove its paired test turns RED.
5. Load and validate CA flag/factor/evidence in the parquet constructor and query adapters; add parquet CA negative tests.
6. Require a versioned path-to-component-hash price manifest and bind its receipt to dataset/canonical/CA identity.
7. Apply placeholder/authority preflight to snapshot `OFFICIAL` mode and add an end-to-end exit-4/no-write test.
8. Execute the tests-only change against exact base `167c1b05...` and preserve the required pre-remediation RED receipt.
9. Freeze a new candidate identity, rerun the complete suite, compile checks, expanded mutations, and these independent bypass probes.

## 7. Claim ceiling and routing

| Decision surface | Status |
|---|---|
| Local candidate compilation/current suite | `GREEN` |
| R-WP4-02 engineering acceptance | `FAIL / REMEDIATION_REQUIRED` |
| Core B/model semantics change detected | `NO` |
| Official Golden | `BLOCKED` |
| Full Replay | `BLOCKED` |
| Model state advancement | `PROHIBITED` |
| Production authority | `NONE` |
| IVA participation | `NONE` |

Revalidation must target a new frozen exact byte set. This receipt is validator-authored evidence only and does not authorize implementation edits, Git push, merge, replay, validation claims, or production use.
