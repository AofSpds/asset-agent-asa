# AAA-ASA Persistent Persona Memory

PERSONA_ID = AAA-ASA
PERSONA_CLASS = OWNER_FACING_ADVISORY_ORCHESTRATION
PAIR = AAA-ADVISORY-VALIDATOR

## CURRENT_RUNTIME_MEMO
- STATE = ACTIVE_WORKING_MEMO
- NOTE = 새 채널/후계 인스턴스에서 Owner-facing 현재 맥락을 복구하기 위한 메모 공간.
- CURRENT_OWNER_REQUIREMENT = 장문의 AAA Project Instructions를 Git canonical source로 이동하고 Project Instructions에는 최소 bootstrap reference만 남긴다. 새 채널에서 `ASA/CTL/MOD/...` 같은 selector만 입력해도 해당 Persona가 공통 프로젝트 기억 + 자기 MEMORY + 자기 WORKLOG/current task를 Git에서 "장비를 챙기듯" loadout하고 자기 Persona lock을 응답한 뒤 이어서 작업해야 한다. Codex도 동일한 Persona/Memory system을 사용하되 local repository bootstrap adapter를 사용하고, repository mutation은 task별 isolated branch/worktree로 격리한다.

## OWNER_INTENT_AND_DIRECTIVES
- 2026-08-22: 상세 AAA 공통지침을 Git에 두고 Project Instructions가 이를 참조하도록 전환 요청.
- 2026-08-22: Persona 주입에 필요한 내용을 수시로 정리할 메모 체계 요청.
- 2026-08-22: 조직도별 Persona마다 Git persistent memo 공간 생성 요청.
- 2026-08-22 04:44: 모든 Persona 공통 주입 내용을 먼저 읽고, 채널 오픈 keyword로 Persona를 resolve하고, 해당 Persona의 전용 memory/worklog/current task를 loadout하며, 중요한 내용을 작업일지에 지속 기록하도록 요청.
- 2026-08-22 05:02: Codex/local repository에서도 같은 Persona memory system을 사용하도록 local bootstrap adapter를 추가하라고 승인. Persona 선택 자체에는 branch를 만들지 않고 실제 repository mutation에만 task별 isolated branch/worktree를 사용한다.

## CURRENT_TASK_AND_STATE
- TASK = AAA_PROJECT_INSTRUCTIONS_GIT_BOOTSTRAP_AND_PERSONA_MEMORY_v1.0
- STATE = CHATGPT_AND_CODEX_RUNTIME_ADAPTER_CANDIDATE_MATERIALIZED_NOT_ACTIVE
- BRANCH = aaa-project-instructions-git-bootstrap-v1.0
- DRAFT_PR = 46
- CODEX_ENTRYPOINT = AGENTS.md
- CODEX_ADAPTER = control/bootstrap/codex/v1.0/AAA_CODEX_LOCAL_BOOTSTRAP_v1.0.md
- CODEX_PARALLEL_JOURNAL_TEMPLATE = control/bootstrap/codex/v1.0/AAA_CODEX_RUN_JOURNAL_TEMPLATE_v1.0.md

## OPEN_BLOCKERS
- Git candidate는 현재 active project-wide authority가 아니며 필요한 governance/validation/cutover가 별도임.
- Active Organization의 Core B persona pair coherence incident는 별도 P0 remediation으로 열린 상태이며 bootstrap candidate가 이를 자동 치유한다고 간주하지 않음.
- Fresh-channel regression에서 selector → canonical Persona → common memory → Persona MEMORY/WORKLOG → current task/blocker/checkpoint → persona lock 흐름의 실제 재현성을 검증해야 함.
- Codex clean-local-invocation regression에서 local pointer discovery → Persona loadout → Persona lock → task branch/worktree isolation → run journal persistence가 실제로 재현되는지 검증해야 함.

## IMPORTANT_DECISIONS_TO_REMEMBER
- Persona selector (`ASA/CTL/MOD/...`)는 runtime routing key이며 authority를 생성하지 않는다.
- 모든 Persona는 자기 memory보다 먼저 `COMMON/PROJECT_MEMORY.md`를 읽는다.
- Persona Memory는 durable continuity, WORKLOG는 chronological execution trace를 담당한다.
- ChatGPT와 Codex는 같은 Persona/Memory/Organization system을 공유한다. 실행환경별 bootstrap adapter만 분리한다.
- Persona != branch/worktree. branch/worktree는 task execution isolation이다.
- 병렬 Codex worker는 shared MEMORY/WORKLOG를 동시에 수정하지 않고 unique append-only run journal을 사용한다.
- Persona Memory/Worklog/run journal는 Authority/Validation/Model/Shared Contract semantic SoT가 아니다.
- Memory와 governed current state가 충돌하면 memory를 신뢰하지 않고 BOOTSTRAP_REVIEW_REQUIRED.
- Historical persona text는 보존하되 current routing은 canonical current state로 resolve한다.

## REQUIRED_NORMATIVE_REFS
- AGENTS.md
- control/bootstrap/project-instructions/v1.0/AAA_PROJECT_INSTRUCTIONS_CURRENT_CANDIDATE_v1.0.json
- control/bootstrap/project-instructions/v1.0/AAA_PROJECT_INSTRUCTIONS_CANONICAL_v1.0.md
- control/bootstrap/project-instructions/v1.0/AAA_PROJECT_INSTRUCTIONS_BOOTSTRAP_STUB_v1.0.md
- control/bootstrap/codex/v1.0/AAA_CODEX_LOCAL_BOOTSTRAP_v1.0.md
- control/bootstrap/codex/v1.0/AAA_CODEX_RUN_JOURNAL_TEMPLATE_v1.0.md
- control/persona-memory/v1.0/COMMON/PROJECT_MEMORY.md
- control/persona-memory/v1.0/AAA_PERSONA_RUNTIME_SELECTOR_REGISTRY_v1.0.json
- control/persona-memory/v1.0/AAA_PERSONA_MEMORY_INDEX_v1.0.json
- control/persona-memory/v1.0/AAA_PERSONA_RUNTIME_LOADOUT_AND_MEMORY_CONTINUITY_GUIDE_v1.0.md
- Active Organization / Shared Contract / Persistent Locator current state

## LATEST_CHECKPOINTS
- Git-backed canonical instructions candidate materialized.
- Minimal Project Instructions bootstrap stub materialized and updated for selector/common/persona/worklog loadout.
- 13 Persona MEMORY.md spaces + 13 Persona WORKLOG.md spaces initialized.
- Shared cross-persona `COMMON/PROJECT_MEMORY.md` initialized.
- Runtime selector registry for 13 official codes initialized.
- Persona runtime loadout & memory continuity guide initialized and extended for ChatGPT/Codex runtime adapters.
- Root `AGENTS.md` Codex entrypoint initialized.
- Codex local bootstrap adapter initialized.
- Codex parallel append-only run journal template initialized.
- Draft PR #46 remains open against main.

## NEXT_ROUTE
- Bind Codex adapter/entrypoint exact refs into bootstrap pointer candidate.
- Governed review/validation of bootstrap candidate and alias selector/runtime adapter semantics.
- Resolve active Organization/Core B P0 coherence before claiming full bootstrap current-state consistency.
- Fresh-channel regression for all selectors: ASA/ASAV/PMO/PMOV/CTL/CTLV/MOD/MODV/RES/RESV/ENG/ENGV/IVA.
- Clean Codex local regression for Persona loadout, task branch/worktree isolation, and parallel run-journal persistence.
- After governed activation readiness, replace product Project Instructions with minimal Git bootstrap stub.

## DO_NOT_FORGET
- Persona Memory는 authority SoT가 아니다.
- Owner intent/decision은 가능한 경우 persistent exact ref로 연결한다.
- 사용자에게 반복적인 context 수동 조립을 요구하지 않는다.
- "재현 성공"은 파일 존재가 아니라 fresh ChatGPT/Codex invocation에서 실제 Persona lock + correct current task/memory recovery까지 통과해야 한다.
- Codex parallel worker 기록 충돌을 shared WORKLOG append로 해결하지 않는다; unique run journal을 사용한다.

## MEMORY_LOG
- TIME_KST = 2026-08-22 04:19 KST | IMPORTANCE = HIGH | LIFECYCLE = PERSONA | STATE = ACTIVE | SOURCE_REF = OWNER_REQUEST | NOTE = 조직도별 persistent memo 공간 초기화.
- TIME_KST = 2026-08-22 04:27 KST | IMPORTANCE = CRITICAL | LIFECYCLE = PROJECT | STATE = ACTIVE | SOURCE_REF = OWNER_REQUEST | NOTE = Project Instructions 상세내용 Git 참조 전환 + Persona별 runtime memo 지속관리 요구를 ASA persistent memory에 기록.
- TIME_KST = 2026-08-22 04:44 KST | IMPORTANCE = CRITICAL | LIFECYCLE = PROJECT | STATE = ACTIVE | SOURCE_REF = OWNER_REQUEST | NOTE = 공통 프로젝트 loadout → keyword Persona routing → Persona MEMORY/WORKLOG/current-state loadout → Persona lock → 중요 작업일지 지속기록을 fresh-channel 재현 표준으로 요청. Candidate structure materialized in Git.
- TIME_KST = 2026-08-22 05:02 KST | IMPORTANCE = CRITICAL | LIFECYCLE = PROJECT | STATE = ACTIVE | SOURCE_REF = OWNER_APPROVAL | NOTE = Codex는 별도 Persona system이 아니라 local repository bootstrap adapter를 사용하며, Persona selection과 branch/worktree isolation을 분리하고 병렬 worker는 unique run journal을 사용하도록 승인/구현.
