# AAA Codex Local Bootstrap Adapter v1.0

PROJECT = AAA
PRODUCT = ASSET AGENT ASA
STATE = WORKING_CANDIDATE_NOT_ACTIVE_AUTHORITY
RUNTIME = CODEX_LOCAL_REPOSITORY

## PURPOSE
Codex runs inside a checked-out Git repository. It must reuse the same AAA Organization / Persona / Memory system as ChatGPT, but enter through the local filesystem instead of a remote GitHub connector.

One persistent Persona system, two runtime adapters:
- ChatGPT: remote GitHub bootstrap URL
- Codex: local repository bootstrap pointer

## 1. LOCAL ENTRY
Before material work:

1. Resolve repository root (`git rev-parse --show-toplevel` or equivalent).
2. Read, relative to that root:
   `control/bootstrap/project-instructions/v1.0/AAA_PROJECT_INSTRUCTIONS_CURRENT_CANDIDATE_v1.0.json`
3. Follow its governed pointers locally.
4. Do not substitute chat history, stale handoff text, or a remote copy for readable local governed state.

If the pointer or required exact targets are missing/unreadable, stop:
`BOOTSTRAP_REVIEW_REQUIRED`.

## 2. COMMON LOADOUT
Load in this order:

1. Canonical Project Instructions
2. Active Persistent Locator
3. Active Organization / Current Organization State
4. Active Shared Contract
5. Persona Authority / Persona Manifest
6. `control/persona-memory/v1.0/COMMON/PROJECT_MEMORY.md`
7. Persona selector registry
8. Persona memory index

## 3. PERSONA RESOLUTION
Persona selection precedence:

1. Explicit `TARGET_PERSONA=<canonical>` in the task/work packet
2. Explicit recognized Persona selector/code or canonical Persona name in the task prompt
3. Governed target Persona declared by the exact work packet
4. Proven current Persona lock for a continuing Codex run
5. Otherwise `AAA-ASA`

Recognized selectors are governed by:
`control/persona-memory/v1.0/AAA_PERSONA_RUNTIME_SELECTOR_REGISTRY_v1.0.json`

Selector resolution grants no authority. The resolved Persona must still be current in governed state.

## 4. PERSONA LOADOUT
After Persona resolution, read from the Persona Memory Index:

- `MEMORY.md`
- `WORKLOG.md`
- current task/state
- open blockers
- latest checkpoints
- required normative/exact refs
- next route

Before material work, expose/log:
`CURRENT_PERSONA_LOCK = <canonical persona> (<code>)`

If multiple current Persona/authority projections conflict, stop with `BOOTSTRAP_REVIEW_REQUIRED`.

## 5. PERSONA != BRANCH
Persona is organizational identity. Branch/worktree is execution isolation.

Rules:
- Read-only analysis: no branch creation required.
- Repository mutation: use the branch/worktree explicitly assigned by the task when present.
- If mutation is required and no isolated task branch/worktree exists, create a task-specific isolated branch/worktree before editing.
- Never create branches merely named after Personas as the Persona mechanism.
- Parallel workers must not share a mutable worktree.
- Do not switch or mutate another worker's worktree/branch.

## 6. MEMORY / WORKLOG PERSISTENCE
Important durable information includes:
- Owner directive or correction
- material decision
- blocker / blocker resolution
- checkpoint
- exact artifact/commit/blob/receipt ref
- next route
- task completion/failure result

Serial/single-writer case:
- update the Persona `MEMORY.md` for durable continuity when warranted;
- append/update the Persona `WORKLOG.md` for chronological execution state.

Parallel/multi-worker case:
- do NOT make concurrent workers race on shared `MEMORY.md` or `WORKLOG.md`;
- each worker writes an append-only unique run journal under:
  `control/persona-memory/v1.0/<PERSONA>/runs/YYYY-MM-DD/<timestamp>_<task-slug>_<worker-id>.md`
- use `control/bootstrap/codex/v1.0/AAA_CODEX_RUN_JOURNAL_TEMPLATE_v1.0.md` as the minimum schema;
- a designated consolidation step/persona may later fold durable items into `MEMORY.md` / `WORKLOG.md` without deleting the run journal.

Memory/worklogs/run journals never create Authority, Validation PASS, Shared Contract semantics, Model semantics, Freeze, Release, or Production authority.

## 7. MUTATION SAFETY
Before repository mutation:
- inspect current branch/worktree;
- preserve all files outside authorized scope;
- do not overwrite Frozen/Accepted artifacts;
- do not treat tests as requirement-preservation proof;
- do not silently rewrite current authority semantics.

After mutation:
- run task-required tests/checks;
- record exact files/refs changed;
- commit to the isolated task branch;
- push when the task explicitly requires remote persistence or the established execution packet requires it.

## 8. EXIT / CHECKPOINT
Before a Codex run finishes, record enough persistent state that a successor can answer:
- What Persona was active?
- What task ran?
- What changed?
- What evidence/tests exist?
- What remains blocked?
- What exact branch/commit/artifact refs matter?
- What should happen next?

## 9. FAIL-CLOSED CONDITIONS
Stop with `BOOTSTRAP_REVIEW_REQUIRED` if any apply:
- bootstrap pointer/target unreadable
- exact target mismatch
- current Organization / Shared Contract / Persona Authority conflict
- selector resolves to noncurrent/superseded Persona
- multiple current Persona matches
- memory/worklog conflicts with governed current state and cannot be reconciled
- task requires authority that the resolved Persona does not have

## 10. REGRESSION ACCEPTANCE
Codex local bootstrap passes only if a clean local invocation can, without pasted handoff context:

1. find the local bootstrap pointer;
2. load common project memory;
3. resolve each supported Persona selector;
4. load Persona MEMORY + WORKLOG/current state;
5. emit the correct Persona lock;
6. preserve Persona != branch semantics;
7. isolate mutable parallel work by task branch/worktree;
8. persist important run state without concurrent shared-log corruption;
9. reject stale/superseded Persona authority.
