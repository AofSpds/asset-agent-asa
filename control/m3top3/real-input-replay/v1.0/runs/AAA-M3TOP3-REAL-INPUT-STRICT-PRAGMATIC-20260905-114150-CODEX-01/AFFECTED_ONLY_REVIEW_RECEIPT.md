# Affected-only review receipt

- PMO RUN_ID: `AAA-M3TOP3-REAL-INPUT-STRICT-PRAGMATIC-20260905-114150-CODEX-01`
- review mode: independent, read-only, affected-only
- price access during review: none
- predecessor: `79b46dc1f63f1cd215cc0ebc0c91b4ec09e7dc71`
- preserved ZERO_SCOREABLE tree: `1d73cc942a3524571ea214724c887c3964dca13f`

## Campaign chronology

1. `90c8c106dc43dcf596d9060a9d8da79476880780` — `FAIL/BLOCK`, 64/64 tests passed but current outcome executable was not rebound to the seal. Review: `2026-09-05T12:59:55.8336067+09:00` to `2026-09-05T13:14:21.4166261+09:00`.
2. `6adde0527e0e7c64bdb4d9be3dd685f6848752fc` — `FAIL/BLOCK`, 70/70 tests passed and five execution-boundary findings were closed, but 105 present unhashed `.pyc` files remained executable. Review: `2026-09-05T13:36:04.5531193+09:00` to `2026-09-05T13:43:22.5507223+09:00`.
3. `c15cbfa9bbedcb3b388b9d101b269ced2fc83bc5` — **PASS**, 71/71 affected tests passed; no residual P0/P1. Review: `2026-09-05T13:51:00.9457198+09:00` to `2026-09-05T13:51:55.4517524+09:00`.

Final reviewed tree: `e7fa6384169e6c111327ea7b59148e7c9cbac930`.

Final reviewed executable bundle:
`M3TOP3-REAL-INPUT-EXECUTABLE-BUNDLE-SHA256:4d828c0308bf892718832e9cb02d87ee7716b9b62c28d643b69b424b5f2b6a4a`.

## Final affected test set

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
$py='C:\Users\ms1pk\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -m unittest tools.m3top3.tests.test_real_input_replay_v1 tools.m3top3.tests.test_model_v1 tools.m3top3.tests.test_narrow_fixes_v1 tools.m3top3.tests.test_coverage_limited_replay_v1 tools.m3top3.tests.test_golden_scorecard_oracle_v1 -v
```

Result: `Ran 71 tests in 1.446s — OK` (`24/24` successor plus `47/47` preserved affected tests).

`git diff --check 6adde0527e0e7c64bdb4d9be3dd685f6848752fc..c15cbfa9bbedcb3b388b9d101b269ced2fc83bc5` passed and the reviewed worktree was clean.

The review confirms only the changed path. It does not promote GF09, certify model quality, or convert raw/CA-unverified outcomes into PRICE-CANONICAL validation.
