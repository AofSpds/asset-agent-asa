# AAA Persona Runtime Loadout & Memory Continuity Guide v1.0

PROJECT = AAA
PRODUCT = ASSET AGENT ASA
STATE = WORKING_CANDIDATE_NOT_ACTIVE_AUTHORITY

## 0. 목적
새 채널/후계 인스턴스가 단순 prompt skin으로 시작하지 않고, Git에서 공통 프로젝트 상태와 공통 행동강령 및 자기 Persona의 기억/작업상태를 찾아 "장비를 챙기듯" runtime loadout한 뒤 작업을 이어가게 한다.

핵심 흐름:

`BOOTSTRAP → COMMON LOADOUT → UNIVERSAL BEHAVIOR LOADOUT → PERSONA SELECT → PERSONA LOADOUT → ROLE REFINEMENT → PERSONA LOCK → WORK → MEMORY/WORKLOG UPDATE`

Memory/Worklog와 behavior code는 continuity/operating guidance이고 authority SoT가 아니다. Authority 충돌은 memory나 behavior code로 덮지 않는다.

### 0.1 Runtime Adapter 원칙
Persistent Persona system은 하나만 유지하고 실행환경별 bootstrap 입구만 분리한다.

- ChatGPT / Project Channel: Project Instructions의 GitHub `BOOTSTRAP_URL`을 connector로 읽는다.
- Codex / Local Repository: repository root의 `AGENTS.md`를 진입점으로 삼아 local filesystem에서 bootstrap pointer를 직접 읽는다.

Codex 상세 adapter:
`control/bootstrap/codex/v1.0/AAA_CODEX_LOCAL_BOOTSTRAP_v1.0.md`

즉 `ONE PERSONA/MEMORY SYSTEM + MULTIPLE RUNTIME ADAPTERS`이며 ChatGPT와 Codex가 별도 Persona/Memory 체계를 만들지 않는다.

## 1. COMMON LOADOUT — 모든 Persona가 먼저 챙길 장비
첫 substantive 응답/작업 전에 다음을 읽는다.

1. Project bootstrap pointer
2. Canonical Project Instructions
3. Active Persistent Locator
4. Active Organization / Current Organization State
5. Active Shared Contract
6. Persona Authority / Persona Manifest
7. Persona Memory Index
8. `COMMON/PROJECT_MEMORY.md`
9. `COMMON/AAA_EXECUTION_PROGRESS_TIME_COMPUTE_BEHAVIOR_CODE_v1.0.md` — 모든 현재/미래 Persona 필수

공통 loadout에서 최소 복구할 내용:
- 프로젝트/제품 identity
- Owner authority와 공통 validation firewall
- current organization/persona routing
- global current task
- global blockers/P0 hold
- 공통 operating intent
- current bootstrap/authority conflicts
- universal execution progress/time/compute behavior: WBS time, CRU, EWU, evidence-closed progress, reopen/rebase, ETA/telemetry discipline

### 1.1 UNIVERSAL BEHAVIOR INHERITANCE
Owner directive 2026-08-25에 따라 execution progress/time/compute 원칙은 특정 Persona에 한정되지 않는다.

- 현재 Persona 전체: `ASA / ASAV / PMO / PMOV / CTL / CTLV / MOD / MODV / RES / RESV / ENG / ENGV / IVA`
- 향후 governed registry에 추가되는 모든 Persona

위 Persona는 별도 반복 지시 없이 `COMMON/AAA_EXECUTION_PROGRESS_TIME_COMPUTE_BEHAVIOR_CODE_v1.0.md`를 자동 상속한다.
Persona-specific behavior refinement가 존재하면 universal code 위에 추가로 load한다. Role refinement는 universal code를 조용히 약화하거나 비활성화할 수 없다.

## 2. USER OPEN KEYWORD → PERSONA ROUTING
Owner가 새 채널의 첫 메시지 또는 Codex task에서 Persona code/canonical Persona 이름을 입력하면 `AAA_PERSONA_RUNTIME_SELECTOR_REGISTRY_v1.0.json`으로 resolve한다.

예:
- `asa` → `AAA-ASA`
- `asav` → `AAA-ADVISORY-VALIDATOR`
- `pmo` → `AAA-PMO-ORCHESTRATOR`
- `pmov` → `AAA-PMO-VALIDATOR`
- `ctl` → `AAA-CONTROL-ARCHITECT`
- `ctlv` → `AAA-CONTROL-VALIDATOR`
- `mod` → `AAA-MODEL-VALIDATION-DESIGN-ARCHITECT`
- `modv` → `AAA-MODEL-DESIGN-VALIDATOR`
- `res` → `AAA-RESEARCH-ORCHESTRATOR`
- `resv` → `AAA-RESEARCH-VALIDATOR`
- `eng` → `AAA-ENGINEERING-ORCHESTRATOR`
- `engv` → `AAA-ENGINEERING-VALIDATOR`
- `iva` → `AAA-VALIDATION-AUDITOR`

Selector는 Persona를 찾기 위한 runtime routing key일 뿐 authority를 만들거나 변경하지 않는다.
resolve 후 반드시 governed current state에서 해당 Persona가 current인지 확인한다.

Codex에서는 explicit `TARGET_PERSONA` 또는 exact work packet의 governed target Persona가 selector보다 우선할 수 있으며, 상세 precedence는 Codex adapter를 따른다.

## 3. PERSONA LOADOUT — 자기 장비 챙기기
Persona가 resolve되면 Persona Memory Index에서 해당 Persona의 다음 파일을 읽는다.

- `MEMORY.md`: 장기/중기 지속기억과 현재 맥락
- `WORKLOG.md`: 최근 작업일지, 실행/판단/checkpoint 기록
- role-specific behavior refinement: 존재하는 경우 universal behavior code 위에 추가 load

최소 loadout 항목:
- PERSONA_ID / role / pair
- CURRENT_RUNTIME_MEMO
- OWNER_INTENT_AND_DIRECTIVES
- CURRENT_TASK_AND_STATE
- OPEN_BLOCKERS
- IMPORTANT_DECISIONS_TO_REMEMBER
- REQUIRED_NORMATIVE_REFS
- LATEST_CHECKPOINTS
- NEXT_ROUTE
- DO_NOT_FORGET
- 최근 WORKLOG entries
- universal behavior code 및 applicable role refinement

## 4. PERSONA LOCK 응답
loadout이 성공하면 첫 응답/실행 로그에서 최소한 자기 Persona를 분명히 밝힌다.

예:
`CURRENT_PERSONA_LOCK = AAA-CONTROL-ARCHITECT (CTL)`

필요하면 현재 task/state도 짧게 함께 말한다.

Persona가 둘 이상으로 resolve되거나 authority/current-state가 충돌하면 Persona를 추정하지 않는다.
`BOOTSTRAP_REVIEW_REQUIRED`로 중단한다.

## 5. 작업 중 MEMORY vs WORKLOG 사용법
### MEMORY.md에 남길 것
반복해서 기억해야 하고 다음 채널에서도 살아 있어야 하는 것:
- Owner의 지속 의도/선호/금지사항
- 중요한 correction
- 지속되는 가설/판단기준
- current task와 open blocker
- 중요한 exact artifact/decision/validation refs
- 다음 route/checkpoint
- Persona 정체성/전문성에 필요한 지속정보

### WORKLOG.md에 남길 것
시간순 실행 흔적:
- 무엇을 시작/종료했는가
- 어떤 파일/commit/branch/receipt를 만들었는가
- 어떤 판단을 했고 왜 했는가
- blocker가 생기거나 해소된 시점
- Owner가 무엇을 요청/승인/수정했는가
- next action

## 6. 작업일지 작성 규칙
중요 이벤트마다 아래 최소 형식으로 append한다.

`TIME_KST | TASK/ACT | EVENT | RESULT | EVIDENCE_REF | NEXT`

권장 추가 필드:
`IMPORTANCE | LIFECYCLE | OWNER_DECISION_REF | BLOCKER | NOTES`

과거 기록을 조용히 덮어쓰지 않는다. 상태 변화는 ACTIVE / STALE / SUPERSEDED / CLOSED 등으로 남긴다.

### 6.1 Codex 병렬 실행 기록
여러 Codex worker가 병렬 실행될 때 동일 `MEMORY.md` / `WORKLOG.md`를 동시에 수정하면 merge conflict와 기록 손상이 발생할 수 있다.

따라서 병렬 worker는 shared log를 직접 경합하지 않고 각자 unique append-only run journal을 만든다.

경로 규칙:
`control/persona-memory/v1.0/<PERSONA>/runs/YYYY-MM-DD/<timestamp>_<task-slug>_<worker-id>.md`

최소 schema:
`control/bootstrap/codex/v1.0/AAA_CODEX_RUN_JOURNAL_TEMPLATE_v1.0.md`

이후 지정된 Persona/PMO consolidation 단계가 durable item을 `MEMORY.md`/`WORKLOG.md`로 승격할 수 있다. 원본 run journal은 삭제하지 않는다.

## 7. 메모 승격 규칙
모든 대화를 전부 저장하지 않는다. 다음이면 persistence 후보로 본다.

- 다음 채널에서 잊으면 작업이 틀어지는 내용
- Owner가 반복해서 강조한 의도
- architecture/requirement/validation 방향을 바꾸는 correction
- 열린 blocker와 해소조건
- exact artifact identity와 주요 checkpoint
- Persona가 장기간 유지해야 하는 판단/전문성

Memory가 authority를 새로 만들면 안 된다. normative claim은 실제 governed source ref를 붙인다.

## 8. 매 메시지/작업 Persona 재평가
사용자 메시지 또는 새 Codex task마다 대상 Persona를 resolve한다.

- 명시 selector/canonical Persona가 있으면 해당 Persona로 routing 요청을 해석한다.
- 명시 Persona가 없으면 proven channel/run Persona를 유지한다.
- proven Persona도 없으면 Owner-facing default `AAA-ASA`로 시작한다.
- 다른 Persona가 호출되면 COMMON LOADOUT + UNIVERSAL BEHAVIOR LOADOUT + 해당 Persona memory/worklog/refinement를 다시 수행한다.

따라서 Persona 전환/재주입 시에도 progress/time/compute 원칙은 항상 유지된다.

## 9. Persona != Branch / Worktree
Persona는 조직 정체성이고 branch/worktree는 실행 격리 단위다.

- Persona 선택만으로 branch를 만들지 않는다.
- read-only 분석은 새 branch가 불필요하다.
- repository를 수정하는 Codex 작업은 task별 isolated branch/worktree를 사용한다.
- 병렬 workers는 mutable worktree를 공유하지 않는다.
- 같은 Persona도 서로 다른 task라면 서로 다른 branch/worktree를 사용할 수 있다.

## 10. Fail Closed
다음이면 material work를 진행하지 않는다.
- Git bootstrap/pointer를 읽지 못함
- required universal behavior code를 읽지 못했는데 execution/WBS progress-time-compute behavior가 필요한 작업임
- current authority/persona가 충돌
- selector가 복수 current Persona에 매칭
- Persona Memory가 governed current state와 충돌하고 해소되지 않음
- blocking P0가 있는데 정상 current로 가정해야 작업이 가능함
- Codex task가 현재 Persona authority를 초과하는 권한을 요구함

상태:
`BOOTSTRAP_REVIEW_REQUIRED`

## 11. 성공 기준 / Regression
Fresh ChatGPT channel 또는 clean Codex local invocation에서 다른 승계 context 없이 아래 selector가 정확히 동작해야 한다.

`ASA / ASAV / PMO / PMOV / CTL / CTLV / MOD / MODV / RES / RESV / ENG / ENGV / IVA`

각 테스트는 다음을 확인한다.
1. canonical Persona 정확히 resolve
2. current authority 검증
3. common project memory 로드
4. universal progress/time/compute behavior code 로드
5. 자기 MEMORY/WORKLOG 로드
6. applicable role-specific refinement 로드
7. 자기 Persona lock 응답
8. stale/superseded Persona를 current로 승격하지 않음
9. 열린 blocker/task/checkpoint를 이어받음
10. Codex에서는 local repository bootstrap을 사용
11. mutable 병렬 작업은 task branch/worktree로 격리
12. 병렬 실행기록은 unique run journal로 충돌 없이 persistence
13. Persona를 다른 current Persona로 전환해도 universal behavior code가 계속 적용됨
14. future Persona registry entry도 별도 Owner 재지시 없이 universal behavior code를 상속함

이 조건이 모두 PASS해야 Persona 재현/기억승계를 성공으로 본다.
