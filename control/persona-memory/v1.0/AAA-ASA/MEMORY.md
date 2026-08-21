# AAA-ASA Persistent Persona Memory

PERSONA_ID = AAA-ASA
PERSONA_CLASS = OWNER_FACING_ADVISORY_ORCHESTRATION
PAIR = AAA-ADVISORY-VALIDATOR

## CURRENT_RUNTIME_MEMO
- STATE = ACTIVE_WORKING_MEMO
- NOTE = 새 채널/후계 인스턴스에서 Owner-facing 현재 맥락을 복구하기 위한 메모 공간.
- CURRENT_OWNER_REQUIREMENT = 장문의 AAA Project Instructions를 Git canonical source로 이동하고 Project Instructions에는 최소 bootstrap reference만 남기는 방향. 각 Persona는 독립 persistent memo 공간을 가지며 Persona injection/recovery에 필요한 현재 정보를 그때그때 정리한다.

## OWNER_INTENT_AND_DIRECTIVES
- 2026-08-22: 상세 AAA 공통지침을 Git에 두고 Project Instructions가 이를 참조하도록 전환 요청.
- 2026-08-22: Persona 주입에 필요한 내용을 수시로 정리할 메모 체계 요청.
- 2026-08-22: 조직도별 Persona마다 Git persistent memo 공간 생성 요청.

## CURRENT_TASK_AND_STATE
- TASK = AAA_PROJECT_INSTRUCTIONS_GIT_BOOTSTRAP_AND_PERSONA_MEMORY_v1.0
- STATE = CANDIDATE_MATERIALIZED_IN_GIT_NOT_ACTIVE
- BRANCH = aaa-project-instructions-git-bootstrap-v1.0
- DRAFT_PR = 46

## OPEN_BLOCKERS
- 실제 ChatGPT Project Instructions를 Git bootstrap stub로 교체하는 product-level 설정 변경은 아직 수행되지 않음.
- Git candidate는 현재 active project-wide authority가 아니며 필요한 governance/validation/cutover가 별도임.
- Active Organization의 Core B persona pair coherence incident는 별도 P0 remediation으로 열린 상태이며 bootstrap candidate가 이를 자동 치유한다고 간주하지 않음.

## IMPORTANT_DECISIONS_TO_REMEMBER
- Persona Memory는 continuity layer이며 Authority/Validation/Model/Shared Contract semantic SoT가 아니다.
- Memory와 governed current state가 충돌하면 memory를 신뢰하지 않고 BOOTSTRAP_REVIEW_REQUIRED.
- Historical persona text는 보존하되 current routing은 canonical current state로 resolve한다.

## REQUIRED_NORMATIVE_REFS
- control/bootstrap/project-instructions/v1.0/AAA_PROJECT_INSTRUCTIONS_CURRENT_CANDIDATE_v1.0.json
- control/bootstrap/project-instructions/v1.0/AAA_PROJECT_INSTRUCTIONS_CANONICAL_v1.0.md
- control/persona-memory/v1.0/AAA_PERSONA_MEMORY_INDEX_v1.0.json
- Active Organization / Shared Contract / Persistent Locator current state

## LATEST_CHECKPOINTS
- Git-backed canonical instructions candidate materialized.
- Minimal Project Instructions bootstrap stub materialized.
- 13 Persona memo spaces + memory index + runtime injection memo template materialized.
- Draft PR #46 opened against main.

## NEXT_ROUTE
- Validate/bootstrap design and authority coherence before activation.
- After governed activation readiness, replace long product Project Instructions with minimal bootstrap stub and run fresh-channel E2E bootstrap regression.

## DO_NOT_FORGET
- Persona Memory는 authority SoT가 아니다.
- Owner intent/decision은 가능한 경우 persistent exact ref로 연결한다.
- 사용자에게 반복적인 context 수동 조립을 요구하지 않는다.

## MEMORY_LOG
- TIME_KST = 2026-08-22 04:19 KST | IMPORTANCE = HIGH | LIFECYCLE = PERSONA | STATE = ACTIVE | SOURCE_REF = OWNER_REQUEST | NOTE = 조직도별 persistent memo 공간 초기화.
- TIME_KST = 2026-08-22 04:27 KST | IMPORTANCE = CRITICAL | LIFECYCLE = PROJECT | STATE = ACTIVE | SOURCE_REF = OWNER_REQUEST | NOTE = Project Instructions 상세내용 Git 참조 전환 + Persona별 runtime memo 지속관리 요구를 ASA persistent memory에 기록.
