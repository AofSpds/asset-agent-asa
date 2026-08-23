# M3Top3 W4×3 Non-scoreable Pilot Receipt v0.1

| Field | Result |
|---|---|
| Execution role | `AAA-PMO-ORCHESTRATOR` bounded pilot |
| IVA participation | `NONE` |
| Window | W4: cutoff 2025-05-09 / entry 2025-05-12 / last 2025-08-08 |
| Raw source | exact 2025 Parquet SHA-256 `2bfd93c217eb74263bc5020b23fa6debb6b02531c11eaccc2826639bc191559e` |
| Mechanical observation | `COMPLETE` |
| Assembly admission | **`FAIL_CLOSED` for 3/3** |
| Score / rank / outcome admission | `FALSE / FALSE / FALSE` for 3/3 |
| Price Canonical | `NOT_ESTABLISHED` |

## Result

The read-only script verified the three input hashes and found all three exact W4 boundary dates for every target. It computed no score, rank, return, winner, Top-K or performance field.

| Company | Code | Rows, cutoff through last | Boundary dates | Zero-OHL rows | Eligibility | Terminal state |
|---|---|---:|---|---:|---|---|
| 케이씨텍 | `281820` | 64 | 3/3 present | 0 | `ELIGIBLE` | `FAIL_CLOSED` |
| 미래산업 | `025560` | 64 | 3/3 present | 17 | `ELIGIBLE` | `FAIL_CLOSED` |
| 삼양엔씨켐 | `482630` | 64 | 3/3 present | 0 | `UNRESOLVED` | `FAIL_CLOSED` |

For 미래산업, the 17 raw zero-Open/High/Low dates run from 2025-06-27 through 2025-07-21 on observed market rows. The pilot records this anomaly only. It does not infer suspension, corporate action, validity or correction because the raw schema lacks governed Trading Status and CA fields.

## Why all three fail closed

- Source bundles are absent under the current G3 audit.
- Timezone-aware `publication_at` is null under the current G3 audit.
- Access/concealment and annotation-lineage sidecars are absent.
- The raw 18-column component lacks governed CA and Trading Status fields.
- 삼양엔씨켐 remains eligibility `UNRESOLVED` and is preserved without scoring.

The receipt proves that the mechanical read-only path can preserve the full row and surface blockers. It does not establish dataset release, Price Canonical, model validity, Official Golden or Full Replay readiness.

## Reproducibility

- Script: `audit_w4_nonscoreable.py`
- Script SHA-256: `e577d7fa742c303acd9394fe413de03e94c3b0d143bdde35a6c34f90970fe450`
- Toolchain: Python 3.12.13, NumPy 2.5.2, PyArrow 17.0.0
- Machine receipt: `W4_X3_MECHANICAL_OBSERVATION_RECEIPT_v0.1.json`
- Contract: `W4_X3_NONSCOREABLE_PILOT_CONTRACT_v0.1.json`

`OWNER_ACTION_REQUIRED=FALSE`; PMO continues source-bundle and eligibility closure work. IVA remains outside execution.
