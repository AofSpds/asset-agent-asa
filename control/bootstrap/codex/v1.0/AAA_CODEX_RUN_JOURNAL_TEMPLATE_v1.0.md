# AAA Codex Run Journal Template v1.0

PROJECT = AAA
PRODUCT = ASSET AGENT ASA
AUTHORITY_SOT = FALSE
JOURNAL_CLASS = APPEND_ONLY_PARALLEL_RUN_RECEIPT

PERSONA_ID = <canonical persona>
PERSONA_CODE = <code>
TASK_ID = <task id>
WORKER_ID = <worker/run id>
TIME_START_KST = <YYYY-MM-DD HH:mm KST>
TIME_END_KST = <YYYY-MM-DD HH:mm KST or OPEN>
BRANCH = <task branch>
WORKTREE = <worktree path or identifier>

## OWNER_INPUT
- directive/correction/request:
- exact owner decision ref if any:

## BOOTSTRAP
- bootstrap pointer/ref:
- common project memory loaded: YES/NO
- persona memory loaded: YES/NO
- worklog/current task loaded: YES/NO
- CURRENT_PERSONA_LOCK:

## TASK_STATE
- started state:
- result state:
- blocker:
- blocker resolution:

## CHANGES
- files/artifacts changed:
- commits:
- blobs/digests/receipts:

## TESTS_AND_EVIDENCE
- tests/checks:
- evidence refs:

## DURABLE_MEMORY_CANDIDATES
- important owner intent/correction:
- durable decision:
- durable blocker/checkpoint:
- exact refs to preserve:

## NEXT
- next action:
- next route/persona:

## RULE
This run journal is evidence/continuity only. It does not grant authority or validation status and must not overwrite governed current state.
