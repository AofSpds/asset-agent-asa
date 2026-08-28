# AAA-PMO-ORCHESTRATOR Persistent Persona Memory

PERSONA_ID = AAA-PMO-ORCHESTRATOR
PERSONA_CLASS = PROGRAM_EXECUTION_ORCHESTRATION
PAIR = AAA-PMO-VALIDATOR

## CURRENT_RUNTIME_MEMO
- STATE = CHANNEL_SUCCESSION_REQUIRED_AFTER_CONTEXT_LIMIT
- NOTE = Prior PMO visible conversation reached context-length limit on 2026-08-26. Treat as channel/runtime-capacity stop, not program failure. Successor PMO must recover from Git and resume from latest open unit without restarting sealed work.

## OWNER_INTENT_AND_DIRECTIVES
- PMO is the execution commander; ASA is supervisory control. Owner is not a manual relay between execution personas/channels.
- Persistent Git artifacts/issues/run journals are the continuity bus; do not require Owner to repaste durable context.
- All Personas inherit the universal Progress/Time/Compute behavior code. Future WBS steps must state time, and long executions should expose evidence-based progress/ETA and compute/resource accounting where measurable.
- OWNER UI CONTINUITY REQUIREMENT (2026-08-29): the visible PMO conversation channel must remain alive and usable for Owner interaction during an execution act. Worker/runtime termination is not permission to leave the Owner-facing conversation in an apparently-running or unusable state. If execution becomes BLOCKED/TERMINATED or needs external Owner action, explicitly report STOPPED/BLOCKED in the live conversation, persist the exact checkpoint, release workers, and keep the conversation available for the Owner to provide the remediation/result and resume instructions. Future execution/succession packets must bind this requirement explicitly.

## CURRENT_TASK_AND_STATE
- TASK = M3TOP3 WORK Ultra WP0-WP9 continuation + queued semantic-neutral EOPT before Full W1-W8 scale-out.
- STATE = PROGRAM_IN_PROGRESS / PMO_VISIBLE_CHANNEL_ENDED_BY_CONTEXT_LIMIT / SUCCESSOR_REQUIRED
- DURABLE_PARENT_QUEUE = GitHub Issue #49
- G1_SOURCE_CUSTODY = GitHub Issue #52
- G1_G4_INTEGRATED_CHECKPOINT = NOT_CLOSED (last durable observed state)
- EOPT_G0 = OPEN / NOT_PROVEN / 1 OF 6 PASS (last durable observed state)
- EOPT_MEASUREMENT_STARTED = NO
- EOPT_MUTATION_STARTED = NO
- FULL_W1_W8_SCALE_OUT = NOT_AUTHORIZED

## OPEN_BLOCKERS
- G1 exact v0.1/v0.2 research-package ZIP bytes remain NOT_FOUND; custodian exhaustion NOT_PROVEN; source-custody coordination active on #52.
- G2: 34 documentary cells, 514 combined eligibility cells, W1-W8 date provenance remain open.
- G3: standalone predecessor manifest identity, CA B/C, governed calendar, PIT eligibility/tradability, annotation remain open. Exact upstream 2024/2025/2026 marcap Parquet bytes were recovered/pinned in latest durable #49 state.
- Integrated G1-G4 checkpoint remains open; EOPT-G0 cannot close until actual preconditions pass.
- Runtime blocker: prior PMO conversation context limit reached. New PMO channel/bootstrap required.

## IMPORTANT_DECISIONS_TO_REMEMBER
- Do not restart WP0-WP9 because the visible conversation ended.
- Do not rerun sealed G4 solely for channel succession. G4 last durable state: SATISFIED_WITH_FINDING.
- Successor must read latest Issue #49 and #52 comments and reconcile any newer durable state before executing.
- If any local-only/unpushed work exists after the last durable Git checkpoint, preserve/reconcile it if accessible; do not assume it survived.
- EOPT measurement/mutation and Full W1-W8 scale-out remain blocked until governed gates actually pass.
- Persona Memory is continuity only and never supersedes governed current state.
- Do not conflate runtime termination with conversation termination. Owner-facing conversation liveness is a required control surface: STOP/BLOCK status must be explicit, but the conversation should stay available unless a genuine product/context limit forces channel succession.

## REQUIRED_NORMATIVE_REFS
- Project Instructions current pointer
- Active Organization routing state
- Active Shared Contract
- Universal `COMMON/AAA_EXECUTION_PROGRESS_TIME_COMPUTE_BEHAVIOR_CODE_v1.0.md`
- GitHub Issue #49 current state/comments
- GitHub Issue #52 current state/comments
- `PMO_CHANNEL_SUCCESSION_CHECKPOINT_2026-08-26_0016_KST.md`

## LATEST_CHECKPOINTS
- `control/persona-memory/v1.0/AAA-PMO-ORCHESTRATOR/PMO_CHANNEL_SUCCESSION_CHECKPOINT_2026-08-26_0016_KST.md`
- checkpoint commit: `78ea075ee35466be6b54df3355e3986b8107e52c`
- last durable #49 recovery packet manifest observed: `c6992f2219fe182f8ecf1a9d7aaaccb3339c35faf5cf35db6c4eef1f4fecdbf3`

## NEXT_ROUTE
1. Open new PMO channel.
2. Git bootstrap → universal common loadout → PMO MEMORY/WORKLOG → succession checkpoint.
3. Re-read Issue #49/#52 latest state and reconcile exact branch/worktree/artifact heads.
4. Resume from latest open G1/G2/G3/integrated-checkpoint unit; do not restart sealed work.
5. Re-establish progress telemetry in successor runtime.
6. Keep the Owner-facing conversation live through execution; on BLOCKED/TERMINATED, report status explicitly, checkpoint/release workers, and wait for Owner remediation in the same conversation whenever technically possible.

## DO_NOT_FORGET
- PMO는 domain semantic supersession authority가 아니다.
- Persona Memory는 program progress SoT를 대체하지 않는다.
- Channel != Persona. A channel can end while the PMO Persona/program continues through Git-backed succession.
- Runtime != conversation. A worker/runtime may terminate while the conversation must remain live as the Owner control surface.

## MEMORY_LOG
- TIME_KST = 2026-08-22 04:19 KST | IMPORTANCE = HIGH | LIFECYCLE = PERSONA | STATE = ACTIVE | SOURCE_REF = OWNER_REQUEST | NOTE = 조직도별 persistent memo 공간 초기화.
- TIME_KST = 2026-08-26 00:16 KST | IMPORTANCE = P0_CONTINUITY | LIFECYCLE = RUNTIME | STATE = ACTIVE | SOURCE_REF = OWNER_REPORT + GIT_ISSUE_49_52 | NOTE = Prior PMO visible channel reached context limit. Successor checkpoint created; resume from Git without program restart.
- TIME_KST = 2026-08-29 00:59 KST | IMPORTANCE = P0_OWNER_CONTROL_SURFACE | LIFECYCLE = PERSONA | STATE = ACTIVE | SOURCE_REF = OWNER_CORRECTION | NOTE = Owner requires PMO conversation channel to remain alive/usable even when execution runtime stops or blocks. Future execution/succession packets must explicitly bind: explicit STOPPED/BLOCKED owner report, durable checkpoint, worker release, same-channel remediation/resume whenever technically possible; only genuine product/context limits justify channel succession.
