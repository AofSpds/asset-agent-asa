# Calibration v0.1 Replicated Receipts

STATE = `PRESERVED_NEGATIVE_RESULT / NO_GLOBAL_SCORE`

## CAL-E1

Read boundary: blind set v0.1 and evaluation framework 06 only. No file 07, prior receipt, research basis, or desired outcome was read.

| Alias | G1 | G2 | G3 | G4 | G5 | Result |
|---|---|---|---|---|---|---|
| A7 | PE | PE | FE | FE | FE | NOT_QUALIFIED |
| C4 | PE | PE | PE | PE | PE | QUALIFIED |
| F2 | FE | FE | FE | FE | PE | NOT_QUALIFIED |
| J9 | PE | PE | PE | PE | PE | QUALIFIED |
| L1 | PE | PA | FE | PE | PE | NOT_QUALIFIED |
| P6 | PE | PE | FE | FE | PE | NOT_QUALIFIED |
| S3 | PE | PE | FE | FE | PE | NOT_QUALIFIED |
| W8 | PA | FE | FE | FE | PE | NOT_QUALIFIED |

CAL-E1 reason for L1: its continuation list is explicitly hand-enumerated, no rules can regenerate it, and therefore the claimed separation is an evidenced non-native result rather than merely absent replay. C4's energy law was limited to a formal identity needing sufficient regularity. J9 was limited to a worked/formal example rather than executed replay.

## CAL-E2

Read boundary: blind set v0.1 and evaluation framework 06 only. No file 07, receipt/result, research basis, or other agent output was read. Gate judgments were frozen before MM-01.

| Alias | G1 | G2 | G3 | G4 | G5 | Result |
|---|---|---|---|---|---|---|
| A7 | PE | FE | FE | FE | FE | NOT_QUALIFIED |
| C4 | PE | PE | PE | PE | PE | QUALIFIED |
| F2 | FE | FE | FE | FE | PE | NOT_QUALIFIED |
| J9 | PE | PE | PE | PE | PE | QUALIFIED |
| L1 | PE | PA | NP | PE | PE | INDETERMINATE |
| P6 | PE | PE | FE | FE | PE | NOT_QUALIFIED |
| S3 | PE | PE | FE | FE | PE | NOT_QUALIFIED |
| W8 | FE | FE | FE | FE | PE | NOT_QUALIFIED |

CAL-E2 reason for L1: absent replay is not automatically demonstrated inability, so G3 remained `NOT_PROVEN`; it explicitly preserved CAL-E1's stricter reading as a live ambiguity. A7's G2 and W8's G1 were stricter than CAL-E1, without changing their qualifications.

## MM-01 and replication decision

Both evaluators found all eight qualification results invariant under consistent alpha-renaming. Renaming strengthened the diagnosis that W8's semantics came from labels. It did not improve unfamiliar C4/J9 or any negative control.

Seven qualification anchors replicated. The required borderline anchor did not replicate. Under the preregistered exact-anchor rule:

`V0.1_REPLICATION = FAIL_MATERIAL_BORDERLINE_CONTROL`.

`PILOT_COMPARISON = STOPPED_PENDING_V0.2_REPAIR`.

`PE=PASS_EVIDENCED`, `FE=FAIL_EVIDENCED`, `PA=PARTIAL`, `NP=NOT_PROVEN`.

