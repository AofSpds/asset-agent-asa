# F05-R1 adapter and execution-envelope change report

- Run: `AAA-M3TOP3-F05-R1-20260905-231028-CODEX-01`
- Classification: `SEMANTIC_NEUTRAL_FIELD_EXPOSURE_PLUS_EXACT_POLICY_ADAPTER`
- Author evidence status: `SUPPORTING_EVIDENCE_NOT_FORMAL_INDEPENDENT_PASS`
- Score gate: `CLOSED_PENDING_P4_EXACT_TARGET_VALIDATION`

## Outcome

The existing Parquet already contained every required raw field. The change exposes those fields through the existing price-provider boundary, binds the Owner-approved F05 construction, and adds a fail-closed score-output envelope. It does not change the model, feature weights, downstream F05 transform, scorer, eligibility population, PIT cutoff, or outcome boundary.

## Runtime changes

- `tools/m3top3/providers.py`
  - Adds backward-compatible optional `Amount`, `Changes`, and `ChangesRatio` values to `PriceRow`.
  - Exposes the existing Parquet fields without changing the data provider or source.
  - Rejects duplicate security/date rows and non-integral Volume/Stocks values.
- `tools/m3top3/f05_r1_market.py`
  - Binds the exact 57-company cohort, 61-session grid, 2024-08-09 cutoff, price-dataset identity, official CA response-body hashes, and GST/Exicon market rows.
  - Compounds 20/60 daily market-price changes using `ChangesRatio / 100` and no dividend or invented factor.
  - Computes daily turnover as `Volume / Stocks` and acceleration as recent-20 mean divided by immediately-prior-20 mean minus one.
  - Uses a fixed Decimal context and company-ID-sorted arithmetic order before the exact /57 benchmark mean.
- `tools/m3top3/cli_build_f05_r1_inputs.py`
  - Verifies every input artifact hash and creates canonical score-free JSONL once, without overwrite.
- `tools/m3top3/f05_r1_score_outputs.py`
  - Is a separate, fail-closed output stage. D0 showed that its first receipt gate bound hashes and target bytes but did not enforce every formal independent-receipt field; D0 was rejected without scoring.
  - The bounded D1 correction now pins the exact D1 revision/bundle, role/level/validator identity/receipt-ID convention, author separation, independence/no-transfer assertions, empty findings, exact input/target bytes, and the actual CLI-read receipt paths before engine construction.
  - Produces a 57-company F05-only provisional ranking and a separate exact-five F02+F05 view. The five-company combined rank is 1..5 only; the other 52 receive no combined rank.
- `tools/m3top3/cli_score_f05_r1_outputs.py`
  - Requires a clean worktree, exact Git target ancestry/tree/blob bindings, raw input/report/receipt hashes, and an absent output directory before engine invocation.
  - D1 additionally rechecks captured HEAD, clean state, all bound bytes, and validated-target blobs after the helper returns and before create-once persistence, closing helper-time Git drift.

## Preserved implementation

- `tools/m3top3/features_v1.py`: unchanged
- `tools/m3top3/features_v1_narrow_patch.py`: unchanged
- `tools/m3top3/scorer_v1.py`: unchanged
- `tools/m3top3/configs/m3top3_v1.0.json`: unchanged; F05 weight remains 20
- exact W1 INCLUDE denominator: 57
- F02-R1 persisted input and prior score/seal artifacts: reused by exact bytes and not regenerated
- W2-W8 and all outcome execution: not invoked

## Final pre-score input

- Artifact: `F05_R1_W1_INPUTS.jsonl`
- Rows / unique company IDs / unique codes: 57 / 57 / 57
- Bytes: 267,149
- SHA256: `8e5c2991eb1c14bede88300a5fd1d648ce263d3e7a3d6a83b31af9b1e3d873f7`
- Merged F02+F05 input hash, computed without scoring: `78d540e5e0385104ba21a744e28897762f4d15af25f571de1cc57136882b2500`
- Explicit F05 availability: 57 `AVAILABLE`
- Forbidden score/rank/outcome keys: 0

Two pre-target materializations were conservatively retired after implementation hardening. They remain under `evidence/retired/`, cannot be selected by the score CLI, and are recorded in the process ledger. The second retired byte stream is identical to the final stream; re-materialization established that the later order guard caused no additional byte change for the exact bound cohort.

## Author checks and D1 correction addendum

- Original D0 supporting suite: 113/113 PASS, DuckDB case included, zero skips. It did not contain the complete formal-receipt and helper-time race adversarial cases; CTLV therefore correctly rejected D0.
- D1 focused score-gate/CLI suite: 14/14 PASS.
- D1 full affected-plus-regression suite: 118/118 PASS, DuckDB case included, zero skips.
- D1 adversarial cases explicitly reject a consistently rehashed D0/provenance set, a false aggregate receipt path, and a helper-time committed runtime drift before output persistence.
- `py_compile` and `git diff --check`: PASS.
- Production score invocation remains 0.

These checks support the D1 target freeze but do not replace fresh CTLV L1, MODV L1, ENGV L1, and IVA L2 exact-target receipts. JSON validator identities are byte-bound declarations under repository custody, not external cryptographic signatures.
