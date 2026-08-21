# AAA Persona Persistent Memory v1.0

## Purpose

이 영역은 AAA 각 Persona가 새 채널/후계 인스턴스에서 맥락을 복구할 때 사용할 **지속 메모 공간**이다.

- Persona Memory는 Authority / Shared Contract / Frozen artifact / Validation receipt를 대체하지 않는다.
- Persona Memory는 second semantic SoT가 아니다.
- Current authority, role, routing, validation state가 충돌하면 반드시 Active Organization / Shared Contract / validated authority/current-state를 다시 resolve한다.
- 메모는 사용자/Owner의 의도, 현재 작업, 중요한 판단, 미해결 blocker, 다음 route, 재현에 필요한 reference를 잊지 않기 위한 운용 레이어다.
- 과거 메모를 지우지 말고, 잘못되거나 stale한 내용은 `SUPERSEDED` 또는 `STALE`로 표시한다.

## Per-Persona Memory File

각 Persona는 자기 디렉터리의 `MEMORY.md`를 사용한다.

권장 섹션:

- `PERSONA_ID`
- `CURRENT_RUNTIME_MEMO`
- `OWNER_INTENT_AND_DIRECTIVES`
- `CURRENT_TASK_AND_STATE`
- `OPEN_BLOCKERS`
- `IMPORTANT_DECISIONS_TO_REMEMBER`
- `REQUIRED_NORMATIVE_REFS`
- `LATEST_CHECKPOINTS`
- `NEXT_ROUTE`
- `DO_NOT_FORGET`
- `MEMORY_LOG`

## Memory Entry Contract

각 중요 메모는 가능한 경우 다음 필드를 가진다.

- `TIME_KST`
- `IMPORTANCE = CRITICAL | HIGH | NORMAL | LOW`
- `LIFECYCLE = PROJECT | PERSONA | TASK | TEMPORARY`
- `STATE = ACTIVE | SUPERSEDED | STALE | CLOSED`
- `SOURCE_REF`
- `NOTE`
- `REVIEW_OR_EXPIRY`

## Bootstrap Rule

새 채널/후계 인스턴스는 Project Instructions bootstrap 후 자기 Persona의 `MEMORY.md`를 읽고, 그 안의 reference를 Current State/Authority와 대조한다.

`MEMORY != AUTHORITY`.

메모와 governed current state가 충돌하면 메모를 그대로 따르지 말고 `BOOTSTRAP_REVIEW_REQUIRED`로 처리한다.
