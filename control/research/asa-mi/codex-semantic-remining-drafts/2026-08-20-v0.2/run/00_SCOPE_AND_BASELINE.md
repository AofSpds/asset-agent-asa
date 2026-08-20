# Scope and baseline

```
TASK = AAA_ASA_MI_GENUINE_SEMANTIC_REMINING_EXTRACTION_QA_v0.2
AUTHORING_STATE = WORK_DRAFT
START_TIME = 2026-08-20T07:00:15+09:00
TASK_BRANCH = codex/asa-mi-semantic-remining-20260820-v02
BASE_BRANCH = codex/asa-mi-source-mining-20260820-v01
BASE_SHA = aa99e57baf351c35c270b6318767b32e7c51f589
V01_FINAL_CONTENT_COMMIT = da866eb8e296a5c26b6860d98ac0e236926584d3
PRIMARY_MAIN_SHA_OBSERVED_AT_START = 5f54a2f829b6ff42517e8159f3a1299a79e6fcdb
AUTHORIZED_WRITE_ROOT = control/research/asa-mi/codex-semantic-remining-drafts/2026-08-20-v0.2/
RAW_PRIMARY_SOURCE_VERIFICATION = NOT_PERFORMED
NORMATIVE_AUTHORITY = NONE
VALIDATION_CLAIM = NONE
MERGE_AUTHORIZED = FALSE
FREEZE_AUTHORIZED = FALSE
PRODUCTION_AUTHORIZED = FALSE
OWNER_ACCEPTANCE = NOT_REQUESTED
```

The v0.1 draft is a read-only index, extraction candidate set, and QA target. It is not semantic ground truth and does not prove independent rereading or saturation. The v0.2 source set is the 18 repository-visible ASA-MI records listed in `01_SOURCE_INVENTORY.md`; v0.1 artifacts are separately reviewed as layer D.

## Provenance layers

| Layer | Meaning | Treatment |
|---|---|---|
| A | Raw primary sources | Seven reported sources remain unavailable; no raw verification claim |
| B | Historical normalized source records | Secondary normalized evidence, never upgraded to raw verified |
| C | Live ASA-MI research records | Current repository research, never retro-attributed to historical sources |
| D | v0.1 Codex extraction | Read-only QA target and search aid |
| E | v0.2 Codex inference | Explicitly separated, non-owner, unconfirmed candidates |

## Semantic constraints

- `CURRENT_HYPOTHESIS != FINAL_TRUTH`.
- `REPLACE(H1,H2) != DELETE(H1)` and `SUPERSEDED != DELETED`.
- `CURRENT != TRUE`, `INACTIVE != FALSE`, and `OLD != FALSE`.
- `AGREEMENT_COUNT != INDEPENDENT_EVIDENCE`.
- `ACCESSIBLE_DATA != AUTOMATICALLY_MEMORY`.
- `MEMORY_OF_AUTHORITY != AUTHORITY`.
- `PROCESS_DISCONTINUITY != AUTOMATIC_PERSONA_TERMINATION`.
- `IDENTITY ?= MEMORY` remains a current, important, unconfirmed working hypothesis and must retain its strongest counterpositions.

## Isolation receipt

The branch was created as a new Git worktree from the exact v0.1 head. No rebase or merge was performed. All authored files for this run are confined to the authorized write root. Git-status and tree-diff checks are repeated in the final integrity audit.
