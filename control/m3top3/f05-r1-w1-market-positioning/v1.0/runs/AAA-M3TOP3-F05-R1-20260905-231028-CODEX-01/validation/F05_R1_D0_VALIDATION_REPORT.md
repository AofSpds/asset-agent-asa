# F05-R1 D0 validation report

## Result

`D0 FAIL — SCORE GATE CLOSED`

CTLV found one blocking pre-score control defect: the gate verified receipt hashes and target bindings but did not itself require the validator role, validation level, unique identity, independence assertion, or no-transfer assertion. A minimally shaped re-hashed receipt could therefore satisfy the old gate.

This is a routine implementation defect inside the approved F05-R1 scope. It does not change the Owner-approved F05 policy, source, cutoff, denominator, corporate-action construction, model weight, or scorer. No Owner decision is required.

## Independent evidence retained

- CTLV L1: FAIL on `CTLV-D0-001 / N12`; all other inspected cases passed.
- MODV L1: role PASS, findings 0; not transferable to D1.
- IVA L2: 27,566 independent assertions PASS, findings 0; not transferable to D1.
- ENGV L1 was not launched after the blocking CTLV finding because D0 could not reach the aggregate gate.
- Score engine / production score CLI calls: 0.

## Required successor

D1 must enforce the complete independent-receipt schema before any engine call, add negative tests for every missing or mismatched formal field, freeze a new commit/tree, and obtain fresh CTLV L1, MODV L1, ENGV L1, and IVA L2 receipts. No D0 PASS evidence transfers as a formal D1 verdict.
