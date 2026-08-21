# AAA-ASA-MI Small Discriminating Implementation Cycle Manifest v0.1

STATE =
`SOURCE_REBASELINE_APPLIED / D1_PROTOCOL_AND_ADAPTER_INTERFACE_FROZEN_CANDIDATE / D2_SCOPED / SHADOW_SEAL_ACTIVE / NON_NORMATIVE`

REPOSITORY =
`AofSpds/asset-agent-asa`

BASE_RESEARCH_EXECUTION_COMMIT =
`d50b73e91f3964626c060bd0165cbaa3371442c4`

SUCCESSOR_RESEARCH_BRANCH =
`research/asa-mi-discriminating-cycle-20260821-v0-1`

ACTIVE_BASELINE_CHANGE =
`NONE`

MAIN_REF_CHANGE =
`NONE`

CANONICAL_MODEL =
`NONE`

MODEL_FREEZE =
`NONE`

VALIDATION_CLAIM =
`NONE`

## Research basis treatment

Historical current-six is retained as provenance-bounded historical control.

The exact A1–A4/B1–B4 artifacts at the base research execution commit are treated only as prospective experimental references for this cycle.

This does not promote them to canonical models.

Unknown/corrupt historical source remains unknown/corrupt.

## Current bounded program

1. `D1 Promise-Origin Symmetry Break` — neutral protocol + adapter interface frozen candidate.
2. `D2 Path / Jump / Translator Discriminator` — scoped next discriminator.
3. Shadow information-control contract for AAA-ASA-MI ↔ AAA-ASA-ME.
4. One-candidate-per-worker sealed adapter-authoring pattern.
5. No full 8-position rerun.
6. No 48-position expansion.

## Artifact digests

| Relative path | SHA-256 |
|---|---|
| `01_D1_PROMISE_ORIGIN_SYMMETRY_BREAK.md` | `f63d9d9fc2119e61a18ffb8fbe020ee5065427e2c448f120c2cdef10b65af480` |
| `02_D2_PATH_JUMP_TRANSLATOR_SCOPING.md` | `18cb135338f57910dfcf8b152a8400a097473fc6158e2d27a2b17e03af4bef34` |
| `03_SHADOW_INFORMATION_CONTROL.md` | `92996e1f1a252ca9b27fea06169c2eeb5e16f073f2cd07fc63c55785880e9112` |
| `04_D1_ADAPTER_INTERFACE_AND_EXECUTION_CONTRACT.md` | `fccb1e75cb5321f839d42baf7ddadb2c579f1bc5ca8da13e4fc6cc7a71b0047f` |
| `FIXTURES/D1_PROMISE_ORIGIN_v0.1.json` | `f38cf09c9adc27eea7da5b45e2ce646759a00a698ee251ae8a2aecaa399c4f33` |
| `SCHEMAS/D1_OUTPUT_SCHEMA_v0.1.json` | `44feb46f94a38ac0ef41092b0f5cf2c37d0318c53383e45e85f6cce68e573356` |
| `TOOLS/d1_neutral_validator.py` | `c0e3404ad2d52d34731af2a4fc644576bb576e60e0b77245f41afac63bc3d537` |
| `TESTS/test_d1_neutral_validator.py` | `1a0435b4e30a3bc795396cebd96cd99824943059f191ad11882e487caa04ba52` |
| `WORK_PACKETS/AAA_ASA_MI_D1_SEALED_ADAPTER_WORKER_TEMPLATE_v0.1.md` | `a3aafeeb44a79fc58ccf964572c5c376e2847e3eace0ba16d6df0a82f4cf5bb9` |

## Scientific intent

D1 targets:
`origin / provenance / obligation / continuation / authority`

D2 targets:
`path / dynamics / discontinuity / translation / sampling`

The experiments are deliberately orthogonal enough to expose different worldview boundaries.

## Neutral harness state

The D1 common envelope is deliberately model-agnostic.

It contains no readable model-by-model expected-answer table and no ranking.

Author-side isolated regression smoke for the neutral validator:

`5 PASS / 0 FAIL`

This is an author self-test only.

It is NOT:
- candidate execution;
- model scientific validation;
- paired validation;
- independent validation.

## Information-control note

No readable per-model prediction matrix is stored in this Owner-visible branch before the Shadow dual freeze.

The neutral protocol, fixture, schema, validator, and worker template are persistent and OPEN.

Candidate-specific adapter/prediction content remains SEALED by procedure and should be frozen in separate isolated one-candidate workers with digest receipts.

## Next exact action

Instantiate eight isolated D1 adapter workers, one per frozen A1–A4/B1–B4 candidate.

Each worker must:
- read only its candidate + neutral D1 materials;
- preregister prediction before execution;
- implement only frozen candidate semantics;
- return only digest/freeze receipt before dual Shadow freeze;
- preserve `FAILURE_BOUNDARY` instead of patching a candidate after failure.

Material adapter failure requires:
`FAILURE_BOUNDARY`
or, only as a separate future artifact,
`SUCCESSOR_MODEL_PROPOSAL`

It does not authorize patching the candidate and scoring the patched version as the same exact target.
