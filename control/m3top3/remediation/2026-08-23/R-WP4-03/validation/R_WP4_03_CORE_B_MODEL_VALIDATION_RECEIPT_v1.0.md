# R-WP4-03 Active Core B Model Validation Receipt v1.0

## Verdict

`PASS`

- Validator: `AAA-MODEL-VALIDATOR`
- Active Core B pair: `AAA-MODEL-ARCHITECT <-> AAA-MODEL-VALIDATOR`
- Exact remote target: commit `ea52bde2ed65c46f3e797f640b60dd9741aa8fe1`, tree `d068aa65b8c3bdacd062529ff9d35108812683d9`, parent `495c070be37f978c8be536c0b469d2d07cf0c071`
- Frozen candidate: tree `1d7b256e961b6f04ad038738fd727a41b98b18db1786a4d21cdd13f78c80d3da`, manifest `0cc363f0c9eb65338747d9d8a47b35046ace881dec0bbf7db50d24ea4e004e17`
- Sequential prerequisites: ENGV `PASS` (`5c450df3...96e3`), CTLV `PASS` (`6f925429...e65cf`)
- IVA execution participation: `NONE`

## Non-semantic preservation finding

The exact protected files `core.py`, `model_interface.py`, `outcome.py`, and `pit_guard.py` are byte-identical to the accepted runtime and match their remote Git blobs. No Feature meaning, weight, missingness/NA rule, model gate, score formula, confidence/opportunity transform, rank ordering, tie policy, Top3 rule, ground-truth promotion, window/horizon rule, or outcome formula was changed.

The changed runtime paths add only exact lineage admission, complete `U/E` identity coverage, full-eligible ranking/outcome/ledger preservation, and immutable fail-closed publication. `backtest.py` now computes and stores outcome records for all eligible rows and retains `selected_top3_outcomes` as the separate Top3 view. The arithmetic return and MFE formulas are unchanged; pending-outcome metric withholding is an integrity/claim control, not a new model objective.

Outcome semantics remain:

- Entry: first trading-date Open strictly after snapshot date.
- Exit: first trading-date Open strictly after window end.
- Return: `exit_open / entry_open - 1`.
- MFE/MAE: maximum High/minimum Low from entry date through window end.
- Horizon-close return: last holding-row Close divided by entry Open, minus one.
- Time-to-peak and giveback: not implemented before or after this change.

## Independent checks

- Remote branch equals exact implementation commit: `PASS`.
- Parent delta: one commit, 23 paths (`17 modified + 6 added + 0 deleted`): `PASS`.
- Canonical manifest/live candidate: `30/30`, exact tree: `PASS`.
- Protected local/accepted-runtime/remote blob identities: `4/4 PASS`.
- Python compile: `27/27 PASS`.
- Independent full unittest discovery: `252/252 PASS`.
- Sealed semantic v1.3: `22/22 probes PASS`; matrix `75/75`; production matrix `75/75`; full suite `252/252`.

## Claim ceiling and route

The model remains `S0_PRE_OUTCOME_BASELINE_CANDIDATE`. Model validity and predictive power remain `NOT_ESTABLISHED`; Champion/alpha claims are prohibited. Official execution, `PRICE_CANONICAL`, Official Golden, Full Replay, Freeze, Promotion, Release, Production, and merge remain blocked or unauthorized.

This `PASS` opens only `AAA-PMO-VALIDATOR`. It does not close the runtime mechanism by itself and does not authorize release or merge.

Issued at: `2026-08-23 07:37:36 KST`.
