# M3Top3 Eligibility Process-Validation Sample Receipt v0.1

## 1. Receipt state

| Field | Value |
|---|---|
| Artifact date | `2026-08-23` |
| Execution authority | `PMO_BOUNDED_EXECUTION` |
| IVA execution participation | `NONE` |
| Source mutation | `NONE` |
| Eligibility investigation | `NOT_PERFORMED` |
| Eligibility decision/change | `NOT_AUTHORIZED / NOT_PERFORMED` |
| Model evaluation | `NOT_AUTHORIZED / NOT_PERFORMED` |
| Receipt verdict | `PASS_PROCESS_SAMPLE_FROZEN` |

This receipt freezes a deterministic queue-prioritization sample only. It does not close any eligibility cell, admit any company-window row, or advance G2/G3/model state.

## 2. Frozen source

| Source | Scope | SHA-256 |
|---|---|---|
| `remediation/r_wp23_data_closure/03_DENOMINATOR_CLOSURE_QUEUE.csv` | filter `axis=COMBINED_HISTORICAL_ELIGIBILITY`; 514 rows | `02bde437c04b1cc3d314b30e9bdd41bdb9a9164d0d2df4468728bdab8089eb62` |

Observed source distribution:

- Windows: `W1=62, W2=63, W3=64, W4=66, W5=66, W6=65, W7=66, W8=62`.
- Component states: `UNRESOLVED/TRUE=45`; `UNRESOLVED/UNRESOLVED=469`.
- Every filtered row remains `current_status=UNRESOLVED`.
- No prohibited performance-result field is present in the source header or emitted manifest schema.

## 3. Frozen selection contract

The row ordering key is exactly:

`SHA256('M3TOP3-ELIGIBILITY-PILOT-v0.1|window|KRX_code|stratum')`

Ascending hexadecimal SHA-256 determines the selected cell within each eligible window/stratum pool. The fixed negative control is excluded first. S4 is chosen before the one-per-window strata so its eight cells remain unique; the complete-company candidate with the smallest specified S4 hash on its W1 anchor is selected. Subsequent strata exclude already selected company-window cells.

| Stratum | Frozen count | Result |
|---|---:|---|
| `S1_TRUE` | 8 | One `UNRESOLVED/TRUE` cell per window |
| `S2_UNRESOLVED` | 8 | One `UNRESOLVED/UNRESOLVED` cell per window |
| `S3_LISTING_BOUNDARY_PROXY` | 8 | A second, disjoint listing-history-pending cell per window |
| `S4_ALL_WINDOWS` | 8 | `램테크놀러지 (171010)`, W1-W8 |
| Total process sample | 32 | Four cells per window; 32 unique company-window keys |
| Fixed control outside sample | 1 | `삼양엔씨켐 (482630), W4`; `sample_inclusion=FALSE` |

## 4. S3 adjustment and claim limit

The design requested eight listing-boundary cells. The 514-row combined queue contains neither a listing-date field nor a distance-to-entry field. A true temporal listing boundary therefore cannot be derived from this input without adding evidence or inference.

S3 is consequently frozen as `S3_LISTING_BOUNDARY_PROXY`: a second, disjoint one-per-window sample from rows whose listing/tradability component is unresolved. It validates the listing-history-pending workflow only. It is not evidence that a selected cell is close to a listing date, and no such fact is asserted.

## 5. Verification

| Check | Result |
|---|---:|
| Source hash binding | PASS |
| Filtered rows | `514/514` |
| Process sample size | `32/32` |
| Unique sample keys | `32/32` |
| Per-window sample cells | `4/4` for each W1-W8 |
| Per-stratum cells | `8/8` for S1-S4 |
| S4 single-company coverage | `1 company × 8 windows` PASS |
| Fixed negative control outside sample | PASS |
| Eligibility changes | `0` |
| Eligibility investigations | `0` |
| Model evaluation outputs | `0` |
| Python compile | PASS |
| Deterministic regeneration | PASS |

## 6. Artifact identities

| Artifact | SHA-256 |
|---|---|
| `select_eligibility_process_sample_v0_1.py` | `0e7195ffbc374d8c5041b65fa7e4bf39d182f53b6ff085387b606d4af6952958` |
| `ELIGIBILITY_PROCESS_VALIDATION_SAMPLE_MANIFEST_v0.1.csv` | `bd1dcef5e446591b25ee902c46e010618a3aef30f9ca58865ab01daceb89715b` |
| `ELIGIBILITY_PROCESS_VALIDATION_SAMPLE_MANIFEST_v0.1.json` | `02f6da31f4b608a6c2f41d7d6dc93faed55b23f54e14c31857458cb1751a662a` |

## 7. Next-use boundary

The frozen manifest may be used only to schedule and validate a future evidence-recovery process. Any actual source research, adjudication, eligibility-state change, admission, score, Golden, Replay, state transition, release, or production action requires its own governed work packet and receipts. IVA remains outside execution.
