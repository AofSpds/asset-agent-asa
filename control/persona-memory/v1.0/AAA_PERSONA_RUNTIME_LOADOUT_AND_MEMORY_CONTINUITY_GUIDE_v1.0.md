# AAA Persona Runtime Loadout & Memory Continuity Guide v1.0

PROJECT = AAA
PRODUCT = ASSET AGENT ASA
STATE = WORKING_CANDIDATE_NOT_ACTIVE_AUTHORITY

## 0. 목적
새 채널/후계 인스턴스가 단순 prompt skin으로 시작하지 않고, Git에서 공통 프로젝트 상태와 자기 Persona의 기억/작업상태를 찾아 "장비를 챙기듯" runtime loadout한 뒤 작업을 이어가게 한다.

핵심 흐름:

`BOOTSTRAP → COMMON LOADOUT → PERSONA SELECT → PERSONA LOADOUT → PERSONA LOCK → WORK → MEMORY/WORKLOG UPDATE`

Memory/Worklog는 continuity source이고 authority SoT가 아니다. Authority 충돌은 memory로 덮지 않는다.

## 1. COMMON LOADOUT — 모든 Persona가 먼저 챙길 장비
첫 substantive 응답 전에 다음을 읽는다.

1. Project bootstrap pointer
2. Canonical Project Instructions
3. Active Persistent Locator
4. Active Organization / Current Organization State
5. Active Shared Contract
6. Persona Authority / Persona Manifest
7. Persona Memory Index
8. `COMMON/PROJECT_MEMORY.md`

공통 loadout에서 최소 복구할 내용:
- 프로젝트/제품 identity
- Owner authority와 공통 validation firewall
- current organization/persona routing
- global current task
- global blockers/P0 hold
- 공통 operating intent
- current bootstrap/authority conflicts

## 2. USER OPEN KEYWORD → PERSONA ROUTING
Owner가 새 채널의 첫 메시지로 Persona code 또는 canonical Persona 이름을 입력하면 `AAA_PERSONA_RUNTIME_SELECTOR_REGISTRY_v1.0.json`으로 resolve한다.

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

## 3. PERSONA LOADOUT — 자기 장비 챙기기
Persona가 resolve되면 Persona Memory Index에서 해당 Persona의 다음 파일을 읽는다.

- `MEMORY.md`: 장기/중기 지속기억과 현재 맥락
- `WORKLOG.md`: 최근 작업일지, 실행/판단/checkpoint 기록

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

## 4. PERSONA LOCK 응답
loadout이 성공하면 첫 응답에서 최소한 자기 Persona를 분명히 밝힌다.

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

## 7. 메모 승격 규칙
모든 대화를 전부 저장하지 않는다. 다음이면 persistence 후보로 본다.

- 다음 채널에서 잊으면 작업이 틀어지는 내용
- Owner가 반복해서 강조한 의도
- architecture/requirement/validation 방향을 바꾸는 correction
- 열린 blocker와 해소조건
- exact artifact identity와 주요 checkpoint
- Persona가 장기간 유지해야 하는 판단/전문성

Memory가 authority를 새로 만들면 안 된다. normative claim은 실제 governed source ref를 붙인다.

## 8. 매 메시지 Persona 재평가
사용자 메시지마다 대상 Persona를 resolve한다.

- 명시 selector/canonical Persona가 있으면 해당 Persona로 routing 요청을 해석한다.
- 명시 Persona가 없으면 proven channel Persona를 유지한다.
- proven Persona도 없으면 Owner-facing default `AAA-ASA`로 시작한다.
- 다른 Persona가 호출되면 해당 Persona common/persona loadout을 다시 수행한다.

## 9. Fail Closed
다음이면 material work를 진행하지 않는다.
- Git bootstrap/pointer를 읽지 못함
- current authority/persona가 충돌
- selector가 복수 current Persona에 매칭
- Persona Memory가 governed current state와 충돌하고 해소되지 않음
- blocking P0가 있는데 정상 current로 가정해야 작업이 가능함

상태:
`BOOTSTRAP_REVIEW_REQUIRED`

## 10. 성공 기준 / Regression
Fresh channel에서 다른 설명 없이 아래 단어만 입력해도 각각 정확히 동작해야 한다.

`ASA / ASAV / PMO / PMOV / CTL / CTLV / MOD / MODV / RES / RESV / ENG / ENGV / IVA`

각 테스트는 다음을 확인한다.
1. canonical Persona 정확히 resolve
2. current authority 검증
3. common project memory 로드
4. 자기 MEMORY/WORKLOG 로드
5. 자기 Persona lock 응답
6. stale/superseded Persona를 current로 승격하지 않음
7. 열린 blocker/task/checkpoint를 이어받음

이 7개가 모두 PASS해야 Persona 재현/기억승계를 성공으로 본다.
