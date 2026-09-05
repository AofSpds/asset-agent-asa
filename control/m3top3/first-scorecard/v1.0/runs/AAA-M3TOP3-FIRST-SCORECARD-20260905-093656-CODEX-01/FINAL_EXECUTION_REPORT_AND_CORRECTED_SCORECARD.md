# M3Top3 First Coverage-Limited Retrospective Replay — Final Execution Report

## Execution identity and timing

- PMO run: `AAA-M3TOP3-FIRST-SCORECARD-20260905-093656-CODEX-01`
- actual PMO start: `2026-09-05T09:36:56.1322777+09:00`
- first actual return: `2026-09-05T10:00:02.5892220+09:00` — 23m06s after start, within the 30-minute target
- replay start/end: `2026-09-05T10:37:30.105456+09:00` / `2026-09-05T10:37:30.455624+09:00`
- post-run completion: `2026-09-05T10:38:45.8166577+09:00`
- total wall time: `01:01:49.6843800`; active/wait/CPU/token/CRU: `NOT_INSTRUMENTED`
- environment: Codex desktop local, Windows 11 `10.0.26200`, bundled CPython `3.12.14`, machine `JWDEV`
- branch/worktree: `task/aaa/m3top3-first-scorecard-20260905` / `C:\Users\ms1pk\dev\asset-agent-asa\asset-agent-asa\scorecard`
- executed Git head: `fdde257f2330d36236b551a303e8149184c18eba`
- executable bundle: `M3TOP3-EXECUTABLE-BUNDLE-SHA256:82266d51a64382cbd34ee68872a3cd3e3f640c6ff438e84416906f8b8a8ab9c0`
- config SHA-256: `eecde22a7744cff505c624bb6f0bdb11714352a122632238ea68d9cd0fbacb98`
- terminal state: `COMPLETE_COVERAGE_LIMITED_ZERO_SCOREABLE`

The exact executable argv, 13 component byte identities, stage order and local environment are preserved in
`replay-output/REPLAY_RUN_MANIFEST.json`.

## Corrected first scorecard

| Window | U127 outer population | Replay eligibility include | Exclude proven | Exclude unresolved | Replay data insufficient | Scoreable | Result measured |
|---|---:|---:|---:|---:|---:|---:|---:|
| W1 | 127 | 57 | 8 | 62 | 57 | 0 | 0 |
| W2 | 127 | 57 | 7 | 63 | 57 | 0 | 0 |
| W3 | 127 | 57 | 6 | 64 | 57 | 0 | 0 |
| W4 | 127 | 58 | 3 | 66 | 58 | 0 | 0 |
| W5 | 127 | 58 | 3 | 66 | 58 | 0 | 0 |
| W6 | 127 | 59 | 3 | 65 | 59 | 0 | 0 |
| W7 | 127 | 59 | 2 | 66 | 59 | 0 | 0 |
| W8 | 127 | 60 | 5 | 62 | 60 | 0 | 0 |
| **Total** | **1,016** | **465** | **37** | **514** | **465** | **0** | **0** |

The outer U127 population was partitioned before scoring. Each Window then entered the scorer exactly once as
one complete INCLUDE batch of 57–60 rows. Across those 465 rows, all 4,185 F01–F09 blocks remain explicit
`NOT_FOUND` with reason `NO_ADMITTED_CUTOFF_SAFE_FEATURE_INPUT_IN_BOUND_EVIDENCE`; no missing value became
zero, false, safe or adverse. All 2,325 axis observations therefore have input coverage `0`, and the scorer
correctly returned `INSUFFICIENT_INPUT` / adapter `REPLAY_DATA_INSUFFICIENT` for all 465.

Accordingly, model Top3, Top10, realized rank, primary Top3-hit metric, MFE/MAE, return and all performance
metrics are `NA / NOT_MEASURABLE`. This is an actually executed zero-scoreable scorecard, not evidence of zero
model performance. No smaller comparison set was presented as the full U127 ranking.

## Inputs, firewall and outcome disposition

The exact G3-E source queue is Git blob `4b3cfbfa9969abe2bd6dff5fdbfeb2db9d31cdae`, compressed SHA-256
`8b3671d662457aef8c1a5595b33a85a27e08aaee56238e7218f1df0b4df78353`. The replay-only W1–W8 registry
binding is blob `033817e6335865e411d2bb4b5837434167091458`, CSV SHA-256
`96d63cc98a01b6332cf9486440e7f3fdaa0ec5a2d605f21bc14a4025b46e69fe`.

All eight model batches and immutable model-result IDs were formed before the three future price files were
opened. After model scoring, the runner verified all three exact file sizes and SHA-256 values and bound price
dataset identity `419893f0dc8c08019a746182135630cc5f94d6e7ebc2874d5bd23cb54c0a72f7`. Because no model score existed,
no outcome value column was loaded and no selected result was silently replaced. Raw price remains
`RAW_IMMUTABLE_NOT_PRICE_CANONICAL`. Known `KRX:183300/W8` material-CA/suspension treatment is preserved for a
future scored selection, but it does not alter this run's zero selected outcomes.

## Golden and review disposition

The embedded ZIP is transport-exact and CRC-clean. Independent contract arithmetic exactly binds GF08,
GF12, GF13 and GF14. GF09 is explicitly left `CONTROL_GAP_NOT_EXACTLY_BOUND`: its gate, contract-form
eligibility and fixture authorization are absent, so no default or expected order was invented.

The one affected-only independent campaign initially found one P1 executable-identity omission. The same
campaign's bounded correction recheck closed it by hashing all 13 local dependencies and enforcing a clean
worktree before binding. Final review: `47/47 PASS`, P0/P1/P2 `0/0/0`, `git diff --check` PASS. The unchanged
historical 261/75/57/400 suites were not rerun. Prior G4 evidence is reused only for its original unchanged
mechanism scope; it does not certify the adapter, current inputs or replay result.

## Post-run integrity and presentation erratum

Post-run verification read back 1,016 unique `(window, company)` ledger keys, exact `465/37/514` partitions,
465 immutable model-result IDs and zero non-null scores/ranks. Output hashes are in
`REPLAY_POSTRUN_VERIFICATION.json`.

The raw auto-generated Markdown contains one presentation-only error: it says “127-row scorer batch.” The
JSON, ledger and counts are correct; the scorer batches were 57–60 INCLUDE rows, while 127 is the outer
population per Window. Raw execution output is preserved immutably, and this report is the forward-corrected
human-readable scorecard.

## Claim ceiling and fastest next data route

This result does not establish observed predictive performance, clean holdout/OOS status, complete U127/PIT
inputs, a price-canonical or CA-complete dataset, Golden freeze, release, production readiness, promotion or
permission to tune from outcomes. The only row-counted scoring blocker is the absence of admitted cutoff-safe
feature values for all 465 INCLUDE rows. The fastest truthful route to non-empty scores is a bounded,
source-hashed, cutoff-safe feature sidecar admission for chosen Window batches; exhaustive old ZIP searches,
514-cell closure, full-market CA collection and full-suite reruns remain unnecessary prerequisites.
