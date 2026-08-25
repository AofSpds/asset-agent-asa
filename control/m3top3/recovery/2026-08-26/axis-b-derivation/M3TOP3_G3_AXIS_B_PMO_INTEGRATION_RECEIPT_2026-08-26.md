# M3Top3 G3 Axis-B PMO integration receipt

```text
PERSONA = AAA-PMO-ORCHESTRATOR (PMO)
ISSUED_AT = 2026-08-26 02:18 KST
EXECUTION_CLASS = PMO_SINGLE_INTEGRATION_READBACK
OWNER_DECISION = OD-G3-B-01 = YES
SOURCE_COMMIT = 5e8e4e57f3fcb129a6ff20751f643f67d3592c82
INTEGRATION_READBACK = OK
VALIDATOR_ACTS = 0
GLOBAL_VALIDATION = FALSE
FULL_REGRESSION = FALSE
VALIDATION_LOOP = FALSE
VALIDATION_CLAIM = NONE
G3_GATE = NOT_CLOSED
EWU_DELTA = 0
```

## Exact result

The bounded non-validator derivation assigned one terminal Axis-B disposition
to every row of the exact pinned 2024, 2025, and 2026 FinanceData/marcap
components. It compared each current `Open` with the immediately preceding
observed same-Code `Close` and used the inclusive integer predicate
`5 * abs(Open - PreviousClose) >= PreviousClose`, without rounding.

| Measure | Exact count |
|---|---:|
| Source rows | 1,822,019 |
| Evaluable comparisons | 1,734,775 |
| `MATERIAL_SIGNAL_PENDING_AXIS_C` | 2,406 |
| `NO_MATERIAL_SIGNAL_AXIS_B_TERMINAL` | 1,732,369 |
| `NOT_EVALUABLE_PRICE_DOMAIN` | 84,272 |
| `FIRST_OBSERVATION_NO_COMPARISON` terminal | 2,972 |
| Raw first same-Code observations | 3,088 |
| Raw first observations with `Open <= 0` | 116 |
| Exact 20% boundary signals | 14 |
| Duplicate / missing key / unresolved / silent drop | 0 / 0 / 0 / 0 |

The 116-row overlap is intentional and governed: the price-domain rule takes
precedence over the ordinary first-observation terminal. Consequently,
`3,088 - 116 = 2,972` rows retain the first-observation terminal, while all
84,272 nonpositive-Open rows are quarantined. Terminal disposition conservation
is exact: `2,972 + 2,406 + 84,272 + 1,732,369 = 1,822,019`.

Signals are `UP=1,792`, `DOWN=614`, `FLAT=0`. Year-seam signals are four for
2024→2025 and six for 2025→2026. These are mechanical signal observations,
not corporate-action, factor, adjustment, eligibility, or release inferences.

## Source custody

| Year | Bytes | SHA-256 | Git blob |
|---:|---:|---|---|
| 2024 | 24,572,111 | `b0c38943e67637d5faf88429880092cf0f46a394be39860dd3bcd0b04231bccb` | `b69c5222d015c81f19f90f581faabe4dd1a919b4` |
| 2025 | 25,153,419 | `2bfd93c217eb74263bc5020b23fa6debb6b02531c11eaccc2826639bc191559e` | `e817f0729b787fe03904982a37b1d84d26d70206` |
| 2026 | 16,297,737 | `b6f3f8ea110326b21d23b5344e6abe159f8ea7f7a345262155b929c08886fc9d` | `3921c090c0c9336e2ab8d068a4546aec26595665` |

The source Parquet files are referenced by exact identity and are not copied
into this recovery package.

## Output custody

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `G3_AXIS_B_FULL_ROW_DISPOSITION_LEDGER_v0.1.csv.gz` | 38,684,591 | `98c0deef0c558f2f1d7016d688fd07ea0ea32eadb1866a8ed245dd18260e8baf` |
| `G3_AXIS_B_MATERIAL_SIGNAL_ROWS_v0.1.csv.gz` | 67,700 | `822e3a0eb935e05979956ec69680d0a44a0b2489112b116bafc2cf2fcfc03e56` |
| `G3_AXIS_B_QUARANTINE_ROWS_v0.1.csv.gz` | 934,247 | `c3d4e61321c54ec125ddfaed8acf74402b8ab8ec37997ca4ddaec4d1e70c18af` |
| `G3_AXIS_B_DERIVATION_SUMMARY_v0.1.json` | 5,232 | `783d9046d67c051396f32a71b48adeca0d42e5a2afe4826eb6b47cd771c2276e` |
| `G3_AXIS_B_SOURCE_AND_OUTPUT_MANIFEST_v0.1.json` | 2,939 | `9e70fc524c76a98a1241637dff31061eef5e983b889ed6c7a9332896c065a8da` |
| `G3_AXIS_B_RUN_TELEMETRY_v0.1.json` | 928 | `ed0ce04073a1710184aa949b9afa73f0f8c156a6c361f8a085cc0768d0159b4a` |
| `G3_AXIS_B_TARGETED_STRUCTURAL_REPRO_CHECK_v0.1.json` | 2,153 | `55a92d5d0efb0b86eb8ffe44a8d1f8e9e1d05f30bdae47024c7f4f6b6b5c8b6a` |
| `G3_AXIS_B_DERIVATION_REPORT_2026-08-26.md` | 2,389 | `19c5bd14a4c3f8d5a7fac1edc62963e64c1fd901037fa91c5af19bf5883eaabe` |
| `derive_g3_axis_b.py` | 27,801 | `fabcbd21a7251527907c6376398fff820461ff87b88d71eafb775ab5e5887505` |
| `check_g3_axis_b_artifacts.py` | 13,307 | `c7782afd8f602fd43c63d75e88eaa6ba5f9a6e6ae3263a6058ae9fcd47d7a47e` |
| `requirements-axis-b.txt` | 16 | `eeffd7ffbb3b90428e909ab87f9d26f46a69f61f8af45000c1177d2fbe12c35a` |
| `G3_AXIS_B_SHA256SUMS_v0.1.txt` | 1,144 | `9b5bb9ff29b37691e6f5098652383f14b529585ca3bd7a93eec52bc853f11b5b` |

The single worker-side targeted structural/reproducibility check reported
`WORKER_TARGETED_CHECK_OK`. This is bounded mechanical evidence only; it is
not an independent validator receipt and creates no PASS or gate effect.

## Time and compute

| Item | Observed |
|---|---:|
| Source recovery and exact identity check | 27.537 s |
| Final derivation | 38.899703 s |
| Single targeted worker check | 8.606136 s |
| Main-path observed wall | 75.042839 s |
| Pre-final rework | 79.268674 s |
| Total observed work including rework | 154.311513 s |
| Final derivation CPU user / system | 36.269745 / 2.601303 s |
| Peak RSS | 881,240 KiB |
| CRU | `NOT_INSTRUMENTED` |

Rework comprises three bounded forward fixes and no loop: Arrow duration cast,
the 116-row disposition-precedence correction, and null-safe Boolean masking.
No automatic repeat remained after the final materialization and one targeted
check.

## Gate and next trigger

The active frozen WBS assigns seven EWU to combined Axis-B/Axis-C closure and
does not predeclare an Axis-B-only partial weight. Therefore this derivation
earns zero EWU by itself: overall Fast-Close remains 21/100 and G3 remains
4/25. The 2,406 signals require exact independent KRX Axis-C event bytes and a
terminal Axis-C reconciliation before G3-B can close.

G4 remains sealed `SATISFIED_WITH_FINDING`; the integrated G1-G4 checkpoint is
`NOT_CLOSED`; EOPT-G0 remains `OPEN / NOT_PROVEN / 1 OF 6`; validator hold
remains active.
