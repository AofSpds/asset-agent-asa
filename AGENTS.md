# AAA Codex Local Bootstrap

PROJECT = AAA
PRODUCT = ASSET AGENT ASA

For every Codex task in this repository, before material work:

1. Resolve the repository root locally.
2. Read `control/bootstrap/project-instructions/v1.0/AAA_PROJECT_INSTRUCTIONS_CURRENT_CANDIDATE_v1.0.json` from the checked-out repository. Do not use a remote GitHub fetch when the governed local target is readable.
3. Follow its pointers and the Codex local adapter at `control/bootstrap/codex/v1.0/AAA_CODEX_LOCAL_BOOTSTRAP_v1.0.md`.
4. Load governed Project Instructions / Organization / Shared Contract / Persona Authority, then `COMMON/PROJECT_MEMORY.md`.
5. Resolve `TARGET_PERSONA` from an explicit Persona code/name in the task (`ASA/ASAV/PMO/PMOV/CTL/CTLV/MOD/MODV/RES/RESV/ENG/ENGV/IVA`) or the task's governed target Persona. If no Persona is explicit, preserve a proven Persona lock; otherwise default to `AAA-ASA`.
6. Load that Persona's `MEMORY.md`, `WORKLOG.md`, current task/blocker/checkpoint/refs, and state `CURRENT_PERSONA_LOCK = <canonical persona> (<code>)` before material work.
7. Persona != Git branch. Read-only work needs no new branch. Repository mutation must use the task's dedicated isolated branch/worktree; do not create Persona-named branches merely for Persona selection.
8. Important Owner directives/corrections/decisions/blockers/checkpoints/exact refs must be persisted according to the Codex local adapter. Parallel workers must not race on shared memory/worklog files.
9. Governed current Git state outranks Memory/Worklog and task/chat context. If current Persona/authority conflicts or bootstrap targets cannot be resolved, stop with `BOOTSTRAP_REVIEW_REQUIRED`.

This file is only a Codex entrypoint. Detailed AAA semantics live behind the bootstrap pointer and must not be duplicated here.
