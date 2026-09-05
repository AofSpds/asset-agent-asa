# F05-R1 affected validation report

## Result

`D1 PASS — BOUNDED W1 SCORE GATE OPEN`

Fresh independent CTLV L1, MODV L1, ENGV L1, and IVA L2 validation all passed the exact D1 target with zero findings. The validated target is commit `2700dda2fee8b4f8b6cfab9c075f8b860ffc94f9`, tree `c98194af223562e440d66c47b57f6696110ced47`, with 34 bound target files and unchanged merged input hash `78d540e5e0385104ba21a744e28897762f4d15af25f571de1cc57136882b2500`.

This PASS opens only the Owner-authorized create-once W1 F05 provisional score stage. It is not an official Top3/Top10, model-performance PASS, release approval, or investment recommendation.

## Independent evidence

- CTLV L1: 34/34 target files, 57/57 source reconstruction, 11/11 official CA bodies, 22/22 adversarial gate cases, and 118/118 regression tests passed.
- MODV L1: 8,607 raw rows independently read; 171 return/turnover values, exact-57 benchmark, GST/Exicon CA arithmetic, and 39 affected checks passed.
- ENGV L1: 34/34 target bindings, 14/14 focused tests, 118/118 full tests with DuckDB and zero skips, plus 3/3 helper-time drift probes passed.
- IVA L2: 43,810 independent assertions passed, including 3,477 market rows, 171 slice hashes, independent return/turnover/benchmark reconstruction, and 31 N12 mutation cases.

All P01-P07 positive cases passed. All N01-N13 negative cases were rejected as required. D0 PASS evidence was not transferred.

## Independence reconciliation

The first ENGV lane discovered another validator's D1 case-disposition lines before freezing its own findings. It correctly issued no receipt, journal, or verdict and was discarded. A fresh-context ENGV actor independently reran the engineering scope without reading peer D1 evidence and issued the sole ENGV PASS. The exact reconciliation is recorded in `P4_D1_VALIDATOR_INDEPENDENCE_RECONCILIATION.json`.

Validator identities are exact Git- and byte-bound role declarations under repository custody. No external cryptographic authentication of human or service principals is claimed.

## Score boundary

- P4 status: PASS.
- Blocking findings: 0.
- Production score calls before this closure: 0.
- Permitted next act: one create-once production score execution using the exact committed aggregate and four exact receipt files.
- W2-W8, outcomes, main, merge, release, production deployment, new provider, credential, and budget remain prohibited.
