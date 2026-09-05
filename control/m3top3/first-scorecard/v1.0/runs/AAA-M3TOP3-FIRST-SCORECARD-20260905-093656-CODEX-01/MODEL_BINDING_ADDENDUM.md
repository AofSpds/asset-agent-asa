# M3Top3 First Scorecard — Forward Model/Runner Binding Addendum

- PMO run: `AAA-M3TOP3-FIRST-SCORECARD-20260905-093656-CODEX-01`
- implementation commit: `bced851e8d1bb7f10c6441752aabbe66550fb91f`
- implementation tree: `c9c8e8619c17b36666c8902f71bfd894b12faf34`
- executable bundle identity: `M3TOP3-EXECUTABLE-BUNDLE-SHA256:897ee61120a1645120b69841c3cdb1b6d4713137d0c255a74328770a69d3c94b`
- status: `FORWARD_CURRENTIZED_COVERAGE_LIMITED_REPLAY_CANDIDATE_NOT_RELEASE`
- recorded at: `2026-09-05T10:26:05.5312303+09:00`

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
| `contracts_v1.py` | `5528f6e81a36ea8558ea909fc59074684a3dd73c414c723be386712dac77f4aa` |
| `features_v1.py` | `14bca2fecb4ec46cebc432a619af3388b8e8bab69ff7164dff5b52aed75dc981` |
| `features_v1_narrow_patch.py` | `b5059969e406e6bfaf2269346d9fd9756a50824c9fe068d8a97cdd20d3b82596` |
| `scorer_v1.py` | `0bb0fbd1628992b2d49d6f7e06b3cbad1fe470f5bab7f175a89b4691a4d96126` |
| `shared_interface_guards_v1.py` | `746ae5570a4542b9e67536f77f043bc2ba7e5b54b1e5f599a7fbf6c01c6aee56` |
| `window_mapping_v11.py` | `6f73ec50cf6ac2f8f2c2da5edda40771704ea02b49fc73f9c275830d97d4cc70` |
| `m3top3_v1.0.json` | `eecde22a7744cff505c624bb6f0bdb11714352a122632238ea68d9cd0fbacb98` |
| `coverage_limited_replay_v1.py` | `ea4659064fe5cb24aacc2f5cd1f7d7fe7608725b2a0e5e3022c13b9bee1d6e83` |

## Reuse and claim boundary

The prior G4 target (`6bea55409588209529dc4c94d03694875a2c7c69`, tree
`5bebddb0fb2ffbc1c85828b54f5bbf44f0a5c687`) is reused only as evidence for mechanisms that are
unchanged in its original scope. It does not validate this adapter, the F06 successor, current population
binding, or a historical replay result. Workbench C1 (`94eaebd04ceb3f7d1652ea7b79e89db7f98f8205`) remains a
separate outcome-nonresponsive scaffold and is not substituted for this scorer.

This binding authorizes one affected-only review and a coverage-limited retrospective execution. It is not a
model freeze, release, promotion, production, clean holdout/OOS, or outcome-based tuning decision.
