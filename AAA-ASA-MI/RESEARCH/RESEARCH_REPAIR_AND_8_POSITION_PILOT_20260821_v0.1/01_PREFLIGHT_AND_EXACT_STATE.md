# AAA-ASA-MI Preflight and Exact Research State v0.1

STATE = SOURCE_DERIVED / NON_NORMATIVE / NO_VALIDATION_CLAIM

## Repository identity

- Repository: `AofSpds/asset-agent-asa`
- Default/current research branch used: `main`
- Exact HEAD: `50c4a1d92e743e7e1862b61d848f12e046d49bdd`
- HEAD message: `AAA-ASA-MI: add worldview primer navigation artifact v0.1`
- HEAD time: `2026-08-21T03:30:58Z`
- Head tree: `666031d1618ddd86e9a89afa55790b06dc12edaa`
- The packet's orientation landmark equals current HEAD; equality was verified rather than assumed.

Five branch names containing `asa-mi` were found. Compared with `main`, the inspected research branches were diverged and 169 commits behind; their ahead-only material is explicitly marked WORK_DRAFT/non-normative. No branch evidence established a newer active research baseline, so `main` is retained.

## Current AAA-ASA-MI inventory at HEAD

| Area | File count | State |
|---|---:|---|
| `CODEX_WORK_PACKETS` | 1 | Present |
| `MEETING_MEMORY` | 70 | Present; normalized records, not raw transcripts |
| `MODEL_SPACE` | 26 | Present but source completeness differs by ARM |
| `PILOTS` | 17 | Present |
| `WORLDVIEW_PRIMER` | 1 | Navigation-only/non-normative |
| **Total** | **115** | Git-tree enumerated |

Exact repository-relative locations for navigation, purpose records, ARM sources/archives/probes, evaluation analyses/return archives, and each current-six candidate's best-supported source/evaluation route are recorded in `EXACT_ARTIFACT_PATH_INVENTORY_v0.1.md`. Missing source packets and pool bodies are explicitly recorded there as having no repository path.

## Exact current-six identifiers

Evaluation pool label: `AAA_ASA_MI_BASELINE_6_FINALISTS_EVAL_SNAPSHOT_v0.1`

1. `E1-C01_ARM-A_D4_LPCW` — ARM-A D4 Local-Patch Compatibility World
2. `E1-C02_ARM-A_D1_AHCK` — ARM-A D1 Admissible-History Constraint Kernel
3. `E1-C03_ARM-B_D2_TRCC` — ARM-B D2 Typed Rewriting Causal Complex
4. `E1-C04_ARM-B_D1_CCP` — ARM-B D1 Contextual Constraint Patches
5. `E1-C05_ARM-C_D3_CCRA` — ARM-C D3 Contextual Constraint-Rewrite Atlas
6. `E1-C06_ARM-C_D1_WLRF` — ARM-C D1 Witnessed Local Rewrite Fabric

The six identities are PROVEN by the current evaluation analyses. The exact bytes of the claimed six-candidate input snapshot are NOT_PROVEN because no snapshot body matching the recorded pool label/hash is present.

## Evaluation artifacts present

- Three ARM independent advisory evaluations.
- Cross-ARM semantic convergence analysis.
- Baseline synthesis v0.2.
- Losslessly decodable E1, E2, E3 evaluator return packets and archive manifest.
- E1–E3 cross-regime analysis.
- E4–E6 result summary and E1–E6 interim analysis.
- Recorded pool-content hash: `8c6f2bc562da088e659475832bed28bb8d52b5f18404a448df3347cdbbe8e708`.

E1–E3 output packets are verifiable against the archive manifest's original sizes and SHA-256 values. E4–E6 raw evaluator packets are absent; only summaries remain. E7–E9 were planned but not executed/persisted in this state.

## Research-purpose artifacts

- The Primer is navigation only and cannot be semantic source of truth.
- Meeting Memory contains normalized purpose/intent/research records.
- The referenced foundational-worldview artifact and original PCS-SHAI/raw chat sources are not present at this HEAD.
- A historical, diverged source-mining draft reports seven raw originals unavailable and explicitly says raw primary verification was not performed. It is auxiliary provenance evidence, not an active baseline.

## Blocking contradictions

1. `SOURCE_INGEST_STATUS.md` says each ARM has a full `SOURCE_ARCHIVE`; HEAD contains a decodable full ARM-A archive, a malformed ARM-B archive, and no ARM-C source archive. Status = CONFLICT.
2. ARM-B's three authoritative blob sizes total 30,647 Base64 characters, which is not divisible by four despite ending in padding; lossless decode fails with gzip CRC/length errors. Status = NOT_PROVEN/CORRUPT.
3. ARM-C retains only executable micro-probe source plus downstream reviews; full proposal/return packet lineage is absent. Status = PARTIAL.
4. The current-six pool label and hash are repeated, but the exact pool body is absent. Evaluator outputs cannot prove what exact candidate text each evaluator received. Status = NOT_PROVEN.
5. Meeting Memory calls several statements Owner-confirmed, but raw transcripts/primary whitepapers are absent. Exact wording beyond preserved direct snippets is secondary-source only.

## Preflight gate result

PILOT_GENERATION_MAY_PROCEED = YES, using a newly frozen, exact pilot contract and newly frozen positions.

CURRENT_SIX_COMPARATIVE_RECONSTRUCTION = LIMITED. Existing summaries and executable probes may support bounded claims, but missing source cannot be repaired by inference.

The required research-basis item × candidate fields are completed in `CURRENT_SIX_BASIS_ITEM_MATRIX_v0.1.md` using separate `WAS_IN_INPUT`, `WAS_EXPLICITLY_ADDRESSED`, and `MODEL_CAN_EXPRESS` values.
