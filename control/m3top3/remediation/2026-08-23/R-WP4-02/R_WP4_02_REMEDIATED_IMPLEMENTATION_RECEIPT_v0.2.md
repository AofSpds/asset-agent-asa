# M3TOP3 R-WP4-02 — Remediated Fail-Closed Implementation Receipt v0.2

## Control header

| Field | Value |
|---|---|
| Receipt ID | `AAA-M3TOP3-R-WP4-02-REMEDIATED-GREEN-20260823-0218` |
| Prepared by | `AAA-PMO-ORCHESTRATOR`, integrating the frozen implementation author outputs and PMO reruns |
| Exact base | `AofSpds/asset-agent-asa@167c1b05e25df658b322cf428c72ce3a4f476544` |
| Rejected intermediate Git candidate | `9f664a29436efb52be008b0d8c168a817da95411` — `NOT ACCEPTED` after ENGV/Core B bypass findings |
| v0.2 candidate | Frozen local bytes; exact remediation Git HEAD pending |
| Verdict | `IMPLEMENTATION_CANDIDATE_GREEN / PAIRED_REVALIDATION_PENDING` |
| IVA execution participation | `NONE` |
| Official Golden / Full Replay | `BLOCKED / BLOCKED` |
| Model state | `S0_PRE_OUTCOME_BASELINE_CANDIDATE` |

This receipt supersedes the v0.1 implementation/test receipts as the current implementation candidate. It does not erase the v0.1 engineering FAIL receipt.

## Independent execution evidence

| Check | Result |
|---|---:|
| Existing infrastructure tests | `25 / 25 PASS` |
| Full unittest discovery | `97 / 97 PASS`; failure/error/skip `0 / 0 / 0` |
| `compileall` / `py_compile` | `PASS / PASS` |
| Targeted temp-copy mutations | `18 / 18 KILLED_RED` |
| Source mutated by mutation harness | `FALSE` |
| Known-Failure logical IDs | `33 / 33` |
| Retrospective exact-base observations | `33 / 33`: `27 RED_OBSERVED`, `5 CONTROL_ABSENT_SOURCE_OBSERVED`, `1 BASE_SAFE_OBSERVED` |
| Import/collection error used as RED evidence | `FALSE` |

The exact-base observation was executed after the implementation. It is expressly labeled `POST-HOC_RETROSPECTIVE_EXACT_BASE`; it proves observed base behavior/control absence, not chronological test-first execution.

## Disposition of ENGV-F01–F06

| Finding | v0.2 disposition |
|---|---|
| ENGV-F01 retrieval audit optional/unreconciled | Closed in candidate: exactly one receipt per company/cutoff; required fields, SHA-256 source identity, counts, exclusions, deterministic receipt ID, and audit↔PIT↔model 1:1 are checked at build and readback. Self-consistent forged manifest/audit cases are negative-tested. |
| ENGV-F02 parquet CA ignored | Closed in candidate: parquet CA flag/factor/evidence are mapped and validated; invalid factor or missing evidence hard-fails. |
| ENGV-F03 exact-base RED receipt absent | Closed as a qualified evidence gap: post-hoc exact-base receipt and 33-ID observation matrix added without claiming chronological pre-patch execution. |
| ENGV-F04 retrieval-audit mutation absent | Closed in candidate: separate audit byte/hash and semantic-reconciliation mutations are present and killed. |
| ENGV-F05 multi-component manifest absent | Closed in candidate for diagnostic admission: versioned absolute path→component SHA-256 manifest and dataset identity are mandatory for multi-component price input. |
| ENGV-F06 snapshot OFFICIAL placeholder bypass | Closed in candidate: snapshot and backtest `OFFICIAL` execution are globally hard-blocked with exit `4`. |

Additional authority ceiling: `PRICE_CANONICAL` validation is globally hard-blocked. A self-authored receipt cannot create Official or Validation authority. Future enablement requires a separately governed authority-registry/trust-root change.

## Candidate file SHA-256

| File | SHA-256 |
|---|---|
| `tools/m3top3/admission.py` | `51c1d11b3b94370dc67dd72aff921f544162dd56ff68148f2e34e2a0f22c7559` |
| `tools/m3top3/backtest.py` | `94d0dd1a7cccb0a8e695703666ed9a0b3abff8354de0c29f5258204536832adb` |
| `tools/m3top3/cli_build_snapshots.py` | `37af9835eeb33f6b6d6efe69dd8232a99c379fbc3bafb22fb90591d2b5bd0be1` |
| `tools/m3top3/cli_run_backtest.py` | `d074cb7a99d4cde1c5fcfbe95ff650866d888839e6a15523b9dd50f4bad1e99b` |
| `tools/m3top3/configs/backtest.example.json` | `3936895f9bf9b565bb2ad19f69586e0a40367405ce2698726f9d3309750b4aef` |
| `tools/m3top3/configs/snapshot.example.json` | `6885746ee9a0fb9c3406d31c3d1f775bf47f6ba9bf7f1b64b3fcb4ed5c7d87c5` |
| `tools/m3top3/ledger.py` | `16bd0ccff0061f325682e45094edb54be4626e402456a389c13d943187d43769` |
| `tools/m3top3/outcome.py` | `0097cbab2373db885538d18083f554136dd347d2863b97aa3f26d728acd9331f` |
| `tools/m3top3/pit_guard.py` | `5fa17bb958b852e808757b1636c593ae8fec6e8b9bcd9ec3b26e6822a863e366` |
| `tools/m3top3/providers.py` | `77e9ec304ac396df4af3b3bd1f6b776fa68cf7076b77f79cbc6a0b9f11b4fd32` |
| `tools/m3top3/snapshot.py` | `f47fcd861e0654a2bc3f0d20c457c7cf42734348f5738ea5aad1cb8f0053e610` |
| `tools/m3top3/tests/_known_failure_helpers.py` | `92da81e87d0c35875c01a1494644faf9ee536ba19880b777c8820c066f2c2321` |
| `tools/m3top3/tests/test_infrastructure.py` | `e032f6c107f042f2b8e43dc5e01de2225c5ca48dcbd978c5d1b78f1c8b0e9416` |
| `tools/m3top3/tests/test_known_failures_cli.py` | `6cd57bcd1fcd9e009c0f8fb8b764393061946e87cac3e7db7f2b5e7ce58cda4f` |
| `tools/m3top3/tests/test_known_failures_immutability.py` | `ac68e866b11f7991ea5a8f219e226d422d056ed08dad80190b7c42589f866005` |
| `tools/m3top3/tests/test_known_failures_integrity.py` | `1da6065a905be4a85217f8f73ef763ab70fe1295167e2e48a4eca4ce72c70f55` |
| `tools/m3top3/tests/test_known_failures_model_admission.py` | `7bf31dccff324cef1450bf73b0bb72dbbae9eb909329fe14fa1930015f0af55f` |
| `tools/m3top3/tests/test_known_failures_pit.py` | `e7935170b9183d0cbf8da23690565a342ea8ddb2cc517023092069cac0a89684` |
| `tools/m3top3/tests/test_known_failures_price.py` | `c545f7b625196bf4abe062b53058c26801d342637999428b60270821026a7994` |
| `tools/m3top3/tests/test_known_failures_snapshot.py` | `934839ee0ec6945fa5d6b335a9514b485e048d41d3832b4c86f1d35a1ed75125` |
| `run_targeted_mutation_checks.py` | `3c7aa98bedc4aa5f5479fa8f370f22386669afdeb75b4a31b17b2060a9f15941` |
| `run_retrospective_exact_base_red.py` | `cddde936b478168cb463df3b5e1cb51a471ec945ccf4b8aaa2e60de4a309f0fc` |

## Preserved claim ceiling

No exact executable pre-outcome v1 identity was recovered. U127 provenance/exposure and historical PIT/data closure remain blocked. This candidate establishes only bounded diagnostic-runtime safeguards. It does not establish model validity, predictive power, Golden readiness, replay readiness, Freeze, Release, Promotion, or Production authority.
