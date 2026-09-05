# F05-R1 P4 D1 bounded correction report

- Run: `AAA-M3TOP3-F05-R1-20260905-231028-CODEX-01`
- Recorded: `2026-09-06T00:51:00+09:00`
- Classification: `ROUTINE_IMPLEMENTATION_CONTROL_DEFECT_WITHIN_APPROVED_SCOPE`
- Owner decision required: `false`
- Score execution count: `0`

## Predecessor disposition

The immutable D0 pre-score target `bc327dddfcc2d826a9ef7c4169b2e8c87f4957f8` / tree `ae502559ccb3dc3ad76c835f5049f993f6da2d01` remains rejected on `CTLV-D0-001 / N12`. Its validation-record commit is `6dc37f81640cc4aa833d6aaab136cd6c3a02ef98` / tree `7fc2b71167cb862398af91496d8f29ac9c726cbd`. No D0 PASS evidence transfers to D1.

## Correction

The D1 gate now fails closed before engine construction unless all four independent receipts use the exact schema, D1 revision, role-specific L1/L2 level, pinned validator identity, strict receipt-ID pattern, exact author-separation assertion, empty findings, no-PASS-transfer assertion, target commit/tree/bundle, and input-byte bindings. Aggregate descriptors must be in canonical CTLV/MODV/ENGV/IVA order and their paths must equal the exact repository-relative receipt paths read by the score CLI.

The score CLI also rechecks captured HEAD, clean-tree state, every bound input/report/receipt byte, and every validated target blob after the pure score helper returns and before create-once persistence. A helper-time commit or worktree change cannot persist output.

The JSON receipts are Git- and byte-bound declarations, not cryptographic signatures of a human or service principal. D1 therefore pins their declared role identities and relies on repository custody plus independently written journals; it does not claim external principal authentication.

## Changed implementation

- `tools/m3top3/f05_r1_score_outputs.py`
- `tools/m3top3/cli_score_f05_r1_outputs.py`
- `tools/m3top3/tests/test_f05_r1_score_outputs.py`
- `tools/m3top3/tests/test_cli_score_f05_r1_outputs.py`

No model feature, scorer, configuration, F05 weight, downstream transform, eligibility rule, cutoff, denominator, source byte, CA adjudication, or input byte changed.

## Verification

- Focused score-gate and CLI suite: 14/14 PASS.
- Full affected-plus-regression suite: 118/118 PASS, zero failures/errors/skips, DuckDB case included.
- Adversarial closure: consistent D0 whole-set rehash rejected; false/nonexistent receipt descriptor path rejected before helper; helper-time committed runtime drift rejected before persistence.
- `py_compile`: PASS.
- `git diff --check`: PASS.
- Final F05 input: 57 rows, SHA-256 `8e5c2991eb1c14bede88300a5fd1d648ce263d3e7a3d6a83b31af9b1e3d873f7`.
- Merged F02+F05 input hash: `78d540e5e0385104ba21a744e28897762f4d15af25f571de1cc57136882b2500`.
- Production score calls and output files: 0.

These are author/supporting checks. D1 scoring remains prohibited until fresh CTLV L1, MODV L1, ENGV L1, and IVA L2 receipts all PASS against the exact successor commit/tree.
