# AAA-PMO-ORCHESTRATOR Persistent Persona Memory

PERSONA_ID = AAA-PMO-ORCHESTRATOR
PERSONA_CLASS = PROGRAM_EXECUTION_ORCHESTRATION
PAIR = AAA-PMO-VALIDATOR

## CURRENT_RUNTIME_MEMO
- STATE = ACTIVE_PROGRAM_DESIGN_DIRECTIVE_RECORDED
- NOTE = 프로그램 계획/순서/라우팅/통합/Blocker continuity memo.
- CURRENT_PROGRAM = M3TOP3 P0 VALIDATION REBASE
- PROGRAM_CONTROL = HUMAN PROJECT OWNER
- PROGRAM_ORCHESTRATION = AAA-PMO-ORCHESTRATOR
- EXECUTION_ENVIRONMENT = WORK ULTRA MODE

## OWNER_INTENT_AND_DIRECTIVES
- 2026-08-22 17:xx KST | Owner exact direction: "작업 계획서는 PMO가 OWNER 관제하에 진행하며 WORK 울트라 모드가 실행하게 됩니다. 페르소나 조직도를 참고 각 작업의 성격을 파악해서 페르소나를 지정해주고 병렬 실행이 필요한 내용을 맡겨야 합니다. 병렬 채널 수행과 병렬 실행은 다른 내용입니다. 병렬 실행시 각 페르소나를 주입한 코드에이전트 쓰레드를 쓰도록 하는것입니다. 병렬 채널 수행은 작업의 빠른 진척도를 위해 여러 채널을 이용하는것이입니다. 현재 작업중이신 내용에 현재 내용을 추가해서 기술해주세요."
- 2026-08-22 18:05 KST | Owner exact direction: "작업 계획서 요청 또다시 추가 요청입니다.에이전트 쓰레드에 페르소나를 주입할시 작업 내용을 메모할수 있도록 해야 합니다."
- M3Top3 실행계획의 단일 프로그램 관제·순서·의존성·라우팅·통합 책임은 Owner 통제 하의 AAA-PMO-ORCHESTRATOR가 맡는다.
- WORK Ultra는 PMO가 발행한 Work Packet을 수행하는 실행환경이며, 프로그램·도메인 semantic authority·Validation PASS·Owner authority를 생성하지 않는다.
- PMO는 각 작업의 성격을 판정해 canonical Persona와 paired Validator를 지정한다.
- `PARALLEL_CHANNEL_OPERATION`과 `PARALLEL_EXECUTION`을 동일시하지 않는다.
  - PARALLEL_CHANNEL_OPERATION = 진행 가속을 위해 여러 독립 채널을 열고 각 채널에 canonical Persona와 bounded task를 부여하는 운영 방식. 각 채널은 PMO에 하나의 RETURN PACKET을 반환한다.
  - PARALLEL_EXECUTION = WORK Ultra 내부에서 canonical Persona를 주입한 여러 code-agent thread가 task-specific isolated branch/worktree와 unique append-only run journal을 사용해 동시에 실행하는 방식.
- 병렬 채널은 연구·설계·검토·검증·의사결정 준비를 분산할 수 있고, 병렬 실행은 코드·데이터·테스트·artifact 생산을 실제 동시 수행한다. 어느 쪽도 Persona authority나 validation state를 자동 생성하지 않는다.
- PMO가 두 병렬면의 dependency, input/output identity, blocker, consolidation order를 통합 관리하고 Owner에게 결정이 필요한 지점만 escalation한다.
- Persona-injected WORK Ultra thread는 작업 중 기억을 유지하고 재시작·승계할 수 있도록 thread-local memory capsule을 가져야 한다.
  - `THREAD_MEMO` = 현재 목표, Owner/PMO 지시, 가정, 결정, 작업상태, blocker, next action을 유지하는 task-local continuity memo. 동일 thread/worktree 안에서 갱신 가능하나 authority SoT가 아니다.
  - `RUN_JOURNAL` = 명령, 관찰, evidence ref, artifact hash, test, decision event, checkpoint를 시간순으로 기록하는 unique append-only execution trace.
  - `MEMORY_CANDIDATE_PACKET` = 종료 시 canonical Persona MEMORY/WORKLOG에 반영할 가치가 있는 Owner directive, correction, decision, blocker, exact ref, learned constraint를 분리해 PMO에 반환하는 후보 패킷.
- Parallel thread는 shared Persona MEMORY/WORKLOG를 직접 동시 수정하지 않는다. 각 thread의 memo/journal은 독립 경로를 사용하고, PMO가 paired validator 또는 지정 consolidator의 검토 후 durable Persona memory/worklog로 승격한다.
- Thread 재시작 시 load order는 Common Project Memory → canonical Persona MEMORY/WORKLOG → PMO Work Packet → thread-local THREAD_MEMO → RUN_JOURNAL tail → current checkpoint 순이다.

## CURRENT_TASK_AND_STATE
- TASK = M3TOP3_FINAL_P0_VALIDATION_REBASE_EXECUTION_PLAN_WITH_OWNER_CONTROL_PMO_ORCHESTRATION_WORK_ULTRA_PARALLELISM_AND_THREAD_MEMORY
- STATE = OWNER_EXECUTION_MODEL_AND_THREAD_MEMORY_CORRECTIONS_RECORDED / DOCUMENT_PLAN_REVISION_IN_PROGRESS
- CURRENT_REQUIRED_OUTPUT = M3Top3 final execution plan with Persona assignment, parallel channel plan, WORK Ultra persona-injected parallel execution plan, thread-local work memory/journal/consolidation protocol, Owner decision points, gates, and PMO control model.

## OPEN_BLOCKERS
- Core B current authority/persona coherence P0 remediation remains open; official model-validation entry stays fail-closed until successor activation/regression.
- Exact v1 identity, Population/U127/exposure, Evaluation Charter, runtime/data readiness, independent Golden, and official replay gates remain open.
- WORK Ultra execution contract, thread memory capsule schema, isolation paths, and exact task packets are execution-plan recommendations until separately materialized/validated.

## IMPORTANT_DECISIONS_TO_REMEMBER
- Owner controls the program; PMO is the program execution orchestrator; WORK Ultra is the execution substrate.
- ASA remains Owner-facing advisory/orchestration support but is not the master program execution controller for this workplan.
- PMO cannot supersede domain semantics; domain Authoring Persona and paired Validator retain their exact authority boundaries.
- Every task must have TARGET_PERSONA, paired validator, authorized scope, preserve-all-others, exact inputs, output identity, gate, blocker, return route, THREAD_MEMO path, RUN_JOURNAL path, and memory consolidation route.
- Multiple channels and multiple code-agent threads are separate concurrency mechanisms and must be planned, named, tracked, and consolidated separately.
- Persona != channel != code-agent thread != branch/worktree != thread memo.
- Parallel WORK Ultra threads must not race on shared MEMORY/WORKLOG or shared mutable worktree; each uses a unique task-local memo and append-only run journal.
- Thread memory supports continuity but does not generate Persona authority, model semantics, validation PASS, release, or production authority.
- Durable memory promotion requires explicit consolidation; raw thread scratchpad is not silently merged into canonical Persona memory.

## REQUIRED_NORMATIVE_REFS
- Project Instructions current pointer
- Active Organization routing state
- Current program checkpoint / Owner decision refs
- AAA-PMO-ORCHESTRATOR / AAA-PMO-VALIDATOR Persona pair
- Core B authority coherence remediation directive
- M3Top3 final comparative adjudication and P0 validation rebase execution-plan candidate
- Codex local bootstrap / unique append-only run journal rule

## LATEST_CHECKPOINTS
- 2026-08-22 | Owner corrected execution governance: Owner-controlled PMO program management; WORK Ultra execution; explicit separation of parallel channels vs persona-injected code-agent thread parallel execution.
- 2026-08-22 18:05 KST | Owner required Persona-injected code-agent threads to preserve their work context through task-local memo, append-only journal, and controlled durable-memory consolidation.

## NEXT_ROUTE
- Revise final M3Top3 execution-plan document with three separate sections: PMO/Owner control, parallel channel operation, WORK Ultra parallel execution.
- Add Persona-bound thread memory capsule, load/resume order, unique path rules, memory candidate packet, and PMO consolidation gate.
- Route the completed program plan to AAA-PMO-VALIDATOR for routing/integration/firewall/memory-race review.
- After Owner approval, PMO materializes bounded channel packets and WORK Ultra thread packets by Persona and Gate.

## DO_NOT_FORGET
- PMO는 domain semantic supersession authority가 아니다.
- Persona Memory는 program progress SoT를 대체하지 않는다.
- WORK Ultra execution result != Paired Validation PASS != Independent Validation PASS != Owner decision.
- Thread-local memory != canonical Persona memory; consolidation is an explicit controlled act.

## MEMORY_LOG
- TIME_KST = 2026-08-22 04:19 KST | IMPORTANCE = HIGH | LIFECYCLE = PERSONA | STATE = ACTIVE | SOURCE_REF = OWNER_REQUEST | NOTE = 조직도별 persistent memo 공간 초기화.
- TIME_KST = 2026-08-22 17:xx KST | IMPORTANCE = P0_PROGRAM | LIFECYCLE = PROGRAM | STATE = ACTIVE | SOURCE_REF = OWNER_EXACT_DIRECTION | NOTE = M3Top3 program is Owner-controlled, PMO-orchestrated, WORK Ultra-executed; parallel channel operation and persona-injected code-agent thread parallel execution are separate mechanisms.
- TIME_KST = 2026-08-22 18:05 KST | IMPORTANCE = P0_PROGRAM | LIFECYCLE = PROGRAM | STATE = ACTIVE | SOURCE_REF = OWNER_EXACT_DIRECTION | NOTE = Persona-injected WORK Ultra threads require task-local memo, append-only journal, restart loadout, and controlled durable-memory candidate consolidation.
