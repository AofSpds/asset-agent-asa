# G3 Axis-B bounded derivation report

```text
EXECUTION_CLASS = NON_VALIDATOR_BOUNDED_MECHANICAL_DERIVATION
OWNER_DECISION = OD-G3-B-01 = YES
SOURCE_COMMIT = 5e8e4e57f3fcb129a6ff20751f643f67d3592c82
POPULATION_ROWS = 1,822,019
MATERIAL_SIGNAL_ROWS = 2,406
G3_GATE = NOT_CLOSED
VALIDATION_CLAIM = NONE
```

## Result

Every row in the three exact pinned FinanceData/marcap components received one
Axis-B disposition after exact-Code chronological stitching. The comparison is
current `Open` against the immediately previous observed same-Code `Close`.
Classification used integer arithmetic
`5 * abs(Open - PreviousClose) >= PreviousClose`; no value was rounded.

| Measure | Count |
|---|---:|
| Population | 1,822,019 |
| Evaluable comparisons | 1,734,775 |
| Material signals (`>=20%`, inclusive) | 2,406 |
| Exact 20% boundary signals | 14 |
| Evaluable non-signals | 1,732,369 |
| First same-Code observations | 3,088 |
| Duplicate Date+Code rows | 0 |
| Price-domain quarantines | 84,272 |
| Unresolved / silently dropped | 0 / 0 |

## Year seams

| Transition | Rows | Evaluable | Signals | Quarantined |
|---|---:|---:|---:|---:|
| 2024→2025 | 2,866 | 2,741 | 4 | 125 |
| 2024→2026 | 0 | 0 | 0 | 0 |
| 2025→2026 | 2,903 | 2,778 | 6 | 125 |

Long date gaps and seams remain mechanical observations only. They do not
imply a corporate action, suspension, relisting, adjustment, or status.

## Custody and boundaries

All three input sizes, SHA-256 values, Git blob IDs, and the detached HEAD were
verified before computation. The 2024/2025/2026 input hashes are respectively
`b0c38943e67637d5faf88429880092cf0f46a394be39860dd3bcd0b04231bccb`, `2bfd93c217eb74263bc5020b23fa6debb6b02531c11eaccc2826639bc191559e`, and
`b6f3f8ea110326b21d23b5344e6abe159f8ea7f7a345262155b929c08886fc9d`.

Material signals remain `MATERIAL_SIGNAL_PENDING_AXIS_C`. This derivation does
not infer corporate actions or factors, does not modify price data, and does
not close G3 or the integrated checkpoint. Axis-C exact independent KRX event
bytes are still required.

## Timing / resource accounting

| Item | Observed |
|---|---:|
| Source sparse recovery + exact hash check | 27.537 s |
| Derivation wall time | 38.900 s |
| CPU user / system | 36.270 / 2.601 s |
| Peak RSS | 881,240 KiB |
| CRU | NOT_INSTRUMENTED |
| Retry / rework | 3 / 79.269 s |
| Validator / global validation | 0 / FALSE |
