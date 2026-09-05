# M3Top3 First Scorecard — First Actual Return

- RUN_ID: `AAA-M3TOP3-FIRST-SCORECARD-20260905-093656-CODEX-01`
- actual_start_at: `2026-09-05T09:36:56.1322777+09:00`
- first_return_at: `2026-09-05T10:00:02.5892220+09:00`
- first_return_target: `2026-09-05T10:06:56.1322777+09:00`
- branch: `task/aaa/m3top3-first-scorecard-20260905`
- worktree: `C:\Users\ms1pk\dev\asset-agent-asa\asset-agent-asa\scorecard`
- execution_environment: `Codex desktop / local / JWDEV / Windows NT 10.0.26200.0 / CPython 3.12.14`
- duplicate_check: `NO_DUPLICATE_EXECUTOR_OBSERVED_WITHIN_CHECKED_SURFACES`
- claim_ceiling: `COVERAGE_LIMITED_RETROSPECTIVE_REPLAY / NOT_CLEAN_OOS / NOT_COMPLETE_UNIVERSE / NOT_PRODUCTION`

## Exact execution binding

| Layer | Selected exact identity | Current disposition |
|---|---|---|
| Model source set | candidate commit `5f9491b6861a11097a929156eaa8bb7cc3c8c749` | selected component source; the old branch as a whole is not restored |
| Scorer | `tools/m3top3/scorer_v1.py`; Git blob `2a797ea705eeb1aef330754fb08ff2182297c139` | selected intent; imports the narrow patch below |
| Config | `tools/m3top3/configs/m3top3_v1.0.json`; Git blob `043bf24bc8c838a8060360e86614cf5bfefc9145`; content SHA-256 `eecde22a7744cff505c624bb6f0bdb11714352a122632238ea68d9cd0fbacb98` | selected, no tuning |
| Feature schema | `control/core_b/M3TOP3-FEATURE-SCHEMA_v1.0_WORKING.yaml`; Git blob `2550f781c2a901c0faada95dfc4a788503ec669b` | selected semantics |
| Weights | `control/core_b/M3TOP3-WEIGHT-VERSION_v1.0_WORKING.yaml`; Git blob `76974860c75f5e164b49639208f8950595c71981` | selected, no outcome adjustment |
| Model/scorer contracts | model `a5bc212aa07166db46b38070f54737cb47a7f090`; scorer `18ecdefbb7f8fddaa3d7189494fab9c00547d59e` | selected semantics |
| MIS / shared guards | `contracts_v1.py` blob `161c3817cf0e0f0827a294b7fde150ab6b6cbcda`; `shared_interface_guards_v1.py` blob `ce5b3b3ad0f09bcbea2aee24abd591974154ea91` | selected validation boundary |
| Window mapping | `window_mapping_v11.py` blob `4fa61dc8d0e7e3b6e2414a8eb41d5960e27a92a1`; `WM-v1.1` | selected semantics |
| Library runner | `runtime_v1.py` blob `3988ddee8a6437790873398cf59ee82ed6534931` | library-only; accepts one snapshot batch, not W1–W8 replay |
| Feature narrow patch | `features_v1_narrow_patch.py` blob `9ead14baed320dd922e64df278401212ea4aab45` | `BLOCKING_FINDING`: known P0 F06 identity-rotation bypass; requires bounded semantics-preserving successor fix and affected-only review |
| Existing tests | `test_model_v1.py` blob `7087735d662cb798e0e9d3ab6877424026a8527f`; `test_narrow_fixes_v1.py` blob `baf6faa6b1b4b94c8f3029b952e9dbad279a558d` | reusable only for their original scope; add adversarial F06/adapter tests |
| Baseline record | `M3TOP3-NO-TUNE-BASELINE-LOCK_v1.2_WORKING.yaml`; blob `9cdbda6180661d8bc9214ae32cde5246ef6a23aa` | intent binding reused; its embedded scorer/test identities are stale and will be currentized forward-only |
| G4 target | commit `6bea55409588209529dc4c94d03694875a2c7c69`, tree `5bebddb0fb2ffbc1c85828b54f5bbf44f0a5c687` | prior PASS reusable only for unchanged generic runtime mechanisms; not substituted for v1 batch scorer/adapter |
| Workbench C1 | commit `94eaebd04ceb3f7d1652ea7b79e89db7f98f8205`, tree `6ae36ce30a1aba84351a453a60320396143a8a3b` | separate outcome-nonresponsive workbench; not selected as scorer |
| Replay adapter / CLI | not present in the selected source | `MISSING_ADAPTER`; build bounded MIS batch, result-ledger, denominator and scorecard writer without changing model/PIT meaning |

Fastest in-scope route: materialize only the selected components, apply the bounded conservative F06 identity fix, add the W1–W8 batch/result adapter, independently check the changed surfaces once, then run. No further policy approval is required.

## W1–W8 availability before feature/result assembly

The exact window tuple authority is commit `e59ed048d6da76edcad82c9a58b0d083c6452471`, Git blob `033817e6335865e411d2bb4b5837434167091458`; its embedded 414-byte registry has SHA-256 `96d63cc98a01b6332cf9486440e7f3fdaa0ec5a2d605f21bc14a4025b46e69fe`.

Eligibility reconstruction sources are commit `6f9ed94e7323e20abf3b19637ecb807e342430f2`: U127 membership blob `f16f0caa0d57063e8d26d0a66a6e3f8e869b183f` and denominator queue blob `4c7849b7105fe043ed3bed045302aff56dda52c2`.

| Window | cutoff / entry / last day | U127 | INCLUDE eligibility | EXCLUDE_PROVEN | EXCLUDE_UNRESOLVED | score-capable | result-capable | pending row classification |
|---|---|---:|---:|---:|---:|---|---|---:|
| W1 | 2024-08-09 / 2024-08-12 / 2024-11-08 | 127 | 57 | 8 | 62 | `NOT_YET_COMPUTED` | `NOT_YET_COMPUTED` | 57 |
| W2 | 2024-11-08 / 2024-11-11 / 2025-02-10 | 127 | 57 | 7 | 63 | `NOT_YET_COMPUTED` | `NOT_YET_COMPUTED` | 57 |
| W3 | 2025-02-10 / 2025-02-11 / 2025-05-09 | 127 | 57 | 6 | 64 | `NOT_YET_COMPUTED` | `NOT_YET_COMPUTED` | 57 |
| W4 | 2025-05-09 / 2025-05-12 / 2025-08-08 | 127 | 58 | 3 | 66 | `NOT_YET_COMPUTED` | `NOT_YET_COMPUTED` | 58 |
| W5 | 2025-08-08 / 2025-08-11 / 2025-11-10 | 127 | 58 | 3 | 66 | `NOT_YET_COMPUTED` | `NOT_YET_COMPUTED` | 58 |
| W6 | 2025-11-10 / 2025-11-11 / 2026-02-10 | 127 | 59 | 3 | 65 | `NOT_YET_COMPUTED` | `NOT_YET_COMPUTED` | 59 |
| W7 | 2026-02-10 / 2026-02-11 / 2026-05-08 | 127 | 59 | 2 | 66 | `NOT_YET_COMPUTED` | `NOT_YET_COMPUTED` | 59 |
| W8 | 2026-05-08 / 2026-05-11 / 2026-08-10 | 127 | 60 | 5 | 62 | `NOT_YET_COMPUTED` | `NOT_YET_COMPUTED` | 60 |
| **Total** | — | **1,016** | **465** | **37** | **514** | **NA** | **NA** | **465** |

`NOT_YET_COMPUTED` is not zero. The Git-present annotation queue contains 1,016 keys but zero admitted model-input rows and no row-level `feature_raw_inputs`; the result side lacks the row-level current manifest/outcome join. The 465 pending rows will now be joined only to available cutoff-safe inputs. Rows with no governed Opportunity axis will become explicit `REPLAY_DATA_INSUFFICIENT`, not fabricated zero/false values.

## Input custody available now

- Embedded Golden v0.2 ZIP restored without re-zipping: 40,210 bytes, SHA-256 `5bbe75a4c9966abcb9f10d2f1e84df983977c1cf76d69e7bda6dfe4f24e60836`, 10/10 entries, CRC clean.
- Local `marcap-2024.parquet`: 24,572,111 bytes, SHA-256 `b0c38943e67637d5faf88429880092cf0f46a394be39860dd3bcd0b04231bccb`.
- Local `marcap-2025.parquet`: 25,153,419 bytes, SHA-256 `2bfd93c217eb74263bc5020b23fa6debb6b02531c11eaccc2826639bc191559e`.
- Local `marcap-2026.parquet`: 16,198,533 bytes, SHA-256 `5da710a2fc56f8fe9b1f5126295cc30c3b15c0ee35d28ba808a505ec4a2243c1`.
- Parquet reader: isolated `pyarrow==17.0.0` / `numpy==2.5.2`; dependency use is read-only and not part of model identity.

The local 2026 component is the packet-listed revision, not the later upstream 16,297,737-byte revision mentioned historically. It covers the approved W8 end date; its exact observed date range will be measured before binding. No provider, AWS/S3, Finance or credential lane is opened.
