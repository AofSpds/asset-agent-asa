# M3Top3 First Scorecard — Forward Model/Runner Binding Addendum

- PMO run: `AAA-M3TOP3-FIRST-SCORECARD-20260905-093656-CODEX-01`
- implementation commit: `f9f58f542b177a525dbf9f74d45bcf9f8b11dfac`
- implementation tree: `08427965b3c1254a3b65a6d48fe969fd97d132b6`
- executable bundle identity: `M3TOP3-EXECUTABLE-BUNDLE-SHA256:82266d51a64382cbd34ee68872a3cd3e3f640c6ff438e84416906f8b8a8ab9c0`
- status: `FORWARD_CURRENTIZED_COVERAGE_LIMITED_REPLAY_CANDIDATE_NOT_RELEASE`
- recorded at: `2026-09-05T10:34:38.7466194+09:00`

## Binding decision

The unchanged v1 model components were restored byte-for-byte at the Git-object layer from candidate commit
`5f9491b6861a11097a929156eaa8bb7cc3c8c749`. Fifteen checked source components exactly match their
candidate Git blobs, including scorer `2a797ea705eeb1aef330754fb08ff2182297c139`, config
`043bf24bc8c838a8060360e86614cf5bfefc9145`, feature schema
`2550f781c2a901c0faada95dfc4a788503ec669b`, weight contract
`76974860c75f5e164b49639208f8950595c71981`, shared guards
`ce5b3b3ad0f09bcbea2aee24abd591974154ea91`, and window implementation
`4fa61dc8d0e7e3b6e2414a8eb41d5960e27a92a1`.

The older narrow-patch identity `9ead14baed320dd922e64df278401212ea4aab45` is not executed. Independent prior
adjudication at `48c25a97f72ab6ea2faff0b09e386802ecca751c` found that rotated milestone IDs could
bypass F06 deduplication. This run forward-currentizes only that bounded defect:

- corrected F06 implementation blob: `b9017f5db0fb637c8a449d5ee3cb1c4a05481076`
- corrected test blob: `3031e70fb9b3a7d13c511c82a4099f51e5e55870`
- correction: namespaced `milestone_id` / `event_group_id` / `evidence_group_id` connected-component
  deduplication, including transitive collisions and conservative anonymous-row handling
- unchanged: feature weights, axis weights, scorer aggregation, gate multipliers, ranking and tie rules

The restored baseline-lock document remains an unmodified historical source object
(`9cdbda6180661d8bc9214ae32cde5246ef6a23aa`). Its embedded older executable/test references are not
silently treated as the current runner binding; this addendum is the forward run-specific binding.

## Executed component byte identities

| Component | SHA-256 |
|---|---|
| `__init__.py` | `54b143b394a19dadb286305f267571b62423ad35b92115becc3d025a0dd1a0b3` |
| `cli_run_coverage_limited_replay.py` | `b44864bfbca0fc874621d000fbf373cadeddc5f8446493af66d8939cd6bcae23` |
| `contracts_v1.py` | `5528f6e81a36ea8558ea909fc59074684a3dd73c414c723be386712dac77f4aa` |
| `core.py` | `9d4ecbe324f4f1eece034e3ccc6aabd4968dce1f185ea58de8eb780da03746ec` |
| `features_v1.py` | `14bca2fecb4ec46cebc432a619af3388b8e8bab69ff7164dff5b52aed75dc981` |
| `features_v1_narrow_patch.py` | `b5059969e406e6bfaf2269346d9fd9756a50824c9fe068d8a97cdd20d3b82596` |
| `pit_guard.py` | `7df44af85ecad959c81b629ec63b1cf9d6d57b1c155f715f49a8c5d445afc957` |
| `runtime_v1.py` | `bfc7a9f1dc7dea20ac1fefb3c3cc8530811674045de691369f46abdda21f55ab` |
| `scorer_v1.py` | `0bb0fbd1628992b2d49d6f7e06b3cbad1fe470f5bab7f175a89b4691a4d96126` |
| `shared_interface_guards_v1.py` | `746ae5570a4542b9e67536f77f043bc2ba7e5b54b1e5f599a7fbf6c01c6aee56` |
| `window_mapping_v11.py` | `6f73ec50cf6ac2f8f2c2da5edda40771704ea02b49fc73f9c275830d97d4cc70` |
| `m3top3_v1.0.json` | `eecde22a7744cff505c624bb6f0bdb11714352a122632238ea68d9cd0fbacb98` |
| `coverage_limited_replay_v1.py` | `ea4659064fe5cb24aacc2f5cd1f7d7fe7608725b2a0e5e3022c13b9bee1d6e83` |

The first independent affected-only review found that the earlier eight-component aggregate omitted four
executed dependencies. Commit `f9f58f542b177a525dbf9f74d45bcf9f8b11dfac` closes the local dependency set to
13 files, includes the CLI bytes in the same aggregate, and fails before binding when tracked or untracked
worktree changes exist. This is a reproducibility-only correction; it changes no model or data semantics.

## Reuse and claim boundary

The prior G4 target (`6bea55409588209529dc4c94d03694875a2c7c69`, tree
`5bebddb0fb2ffbc1c85828b54f5bbf44f0a5c687`) is reused only as evidence for mechanisms that are
unchanged in its original scope. It does not validate this adapter, the F06 successor, current population
binding, or a historical replay result. Workbench C1 (`94eaebd04ceb3f7d1652ea7b79e89db7f98f8205`) remains a
separate outcome-nonresponsive scaffold and is not substituted for this scorer.

This binding authorizes one affected-only review and a coverage-limited retrospective execution. It is not a
model freeze, release, promotion, production, clean holdout/OOS, or outcome-based tuning decision.
