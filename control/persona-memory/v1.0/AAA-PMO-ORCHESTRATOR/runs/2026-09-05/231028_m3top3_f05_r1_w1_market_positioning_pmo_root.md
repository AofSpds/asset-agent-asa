# AAA PMO root journal — M3Top3 F05-R1 W1 market positioning

- Run ID: `AAA-M3TOP3-F05-R1-20260905-231028-CODEX-01`
- Persona lock: `AAA-PMO-ORCHESTRATOR (PMO)`
- Started: 2026-09-05 23:10:28 KST
- Branch: `task/aaa/m3top3-f05-r1-w1-market-positioning-20260905`
- State: `IN_PROGRESS / P4 D1 EXACT-TARGET FREEZE`

## Authority

- Owner policy: `709ded3f4440142c05a97dcc03b286ad49fa149b`, blob `ab65b65182fddaf31c1b7e0d7e1f0341f4bbdf9e`, SHA256 `2bd9ae341904c562a25513286b6546c737df92bfa3a6ca82434c71de396fbacb`.
- Execution request: `ab1a9a52cbee1825a2ff725a8b997307f7f5e16e`, blob `370c86569717aa1b93ecc748a06766d0400946e0`, SHA256 `452b64ac36d37860f72da6367e62fef1c175af3d56b4379651c232e2ab988a53`.
- No-redundant-question direction: `6db4a549d5e1a8e18ffe1226ad70e4bf090ba696`, blob `23f7d89ccd7c3ce1a2c36aeab1162011b75afc14`, SHA256 `cf10e7ccac34b433c8379f175a9b724ec39ad1a083c1937f0b437683c3e7eb38`.
- Conditional execution is authorized only after P0-P4 close without semantic deviation.

## Exact composition

- Executable/F02 base: `b0e4b60e6380ad12705ded8f05efce13843bbf3c`, tree `01e9ed6dddc6c23af44811fb5cd072c199f02dd6`.
- R0 final: `87a5025f7e126eb66f8864ae8b106f6c5c65aba4`, tree `7ab484e88cf5a1aa073f0267e462b3d4e2f06ab2`.
- Dispatch tip: `6db4a549d5e1a8e18ffe1226ad70e4bf090ba696`, tree `b6b499920cfe79e434658294b0ec2d9239d5cdaa`.
- Task composition: `5fb34b229868d66b6f8a02d9686445c6c4b9398d`, tree `44771b00d126fa4f73767c90a156a70559a23945`.
- F05-R0 was not mutated or rerun. The task-only merge preserves exact ancestry; it creates no main merge/release/production effect.

## Current work

- P0 complete: exact authority, R0, W1 population, price objects, F02-R1, model, scorer, and config identities reconfirmed.
- P1 materialized: approved P1-P7 semantics and exact source-field contract bound with no deviation.
- P3 materialized: GST and Exicon corporate-action boundaries closed with official issuer/KRX evidence; no adjustment factor inferred.
- P2 is complete. The semantic-neutral field exposure, exact F05 builder, input CLI, and score-output envelope are implemented. D0 reopened a bounded author lane for N12 only; the D1 correction lane is now closed pending exact-target validation.
- Final score-free input is 57/57, 267,149 bytes, SHA256 `8e5c2991eb1c14bede88300a5fd1d648ce263d3e7a3d6a83b31af9b1e3d873f7`; merged F02+F05 input hash is `78d540e5e0385104ba21a744e28897762f4d15af25f571de1cc57136882b2500`.
- Two pre-target materializations were retained under `evidence/retired/` after routine implementation hardening. Neither was scored.
- Root D1 affected-plus-regression checks are 118/118 PASS with zero skips. This is supporting author evidence, not an independent P4 PASS.
- P4 scientific/engineering validation floor is frozen as CTLV L1 + MODV L1 + ENGV L1 + IVA L2 before scoring; PMOV is process-only.
- No F05 score or provisional rank exists yet. The score gate remains closed until the exact D1 target receives all four fresh independent receipts.
- No Owner stop boundary is present.

## D0 validation disposition

- D0 target `bc327dddfcc2d826a9ef7c4169b2e8c87f4957f8` / tree `ae502559ccb3dc3ad76c835f5049f993f6da2d01` is rejected for scoring.
- CTLV found `CTLV-D0-001`: the old gate did not require formal validator role, level, identity, independence, and no-transfer fields.
- MODV L1 and IVA L2 passed their independent substantive work; IVA completed 27,566 assertions. Their PASS verdicts do not transfer to D1.
- This is a bounded implementation-control correction, not an Owner policy boundary. The score gate remains closed and D1 full affected revalidation is mandatory.

## D1 bounded correction

- Canonical target author identity remains `root/f05_r1_author`; the implementation actor `root/f05_r1_d1_gate_correction` and root integration actor are explicitly bound to that non-independent author lane.
- The corrected gate pins exact D1 revision/bundle, role/level/identity/receipt-ID conventions, author separation, independence and no-transfer assertions, receipt hashes, actual CLI-read receipt paths, target bytes, and input bytes before engine construction.
- The CLI rechecks HEAD, clean worktree, every bound input/report/receipt byte, and all validated target blobs after the helper returns and before persistence.
- Three adversarial reproductions are now closed: consistent D0 whole-set rehash, aggregate receipt-path substitution, and helper-time committed runtime drift.
- Focused checks are 14/14 PASS; the full affected-plus-regression suite is 118/118 PASS with DuckDB and zero skips. `py_compile` and `git diff --check` pass.
- Score calls and score output files remain zero. Fresh D1 CTLV L1, MODV L1, ENGV L1, and IVA L2 validation is required with no D0 PASS transfer.
- The declared validator identities are Git- and byte-bound under repository custody; no external cryptographic identity authentication is claimed.
