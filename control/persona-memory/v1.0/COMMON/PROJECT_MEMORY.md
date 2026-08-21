# AAA Shared Project Memory

PROJECT = AAA
PRODUCT = ASSET AGENT ASA
MEMORY_CLASS = CROSS_PERSONA_CONTINUITY
AUTHORITY_SOT = FALSE

## PURPOSE
모든 current AAA Persona가 새 채널/후계 인스턴스에서 자기 전용 MEMORY를 읽기 전에 공통으로 알아야 할 최소 지속맥락을 제공한다.
이 파일은 Authority/Shared Contract/Organization/Validation PASS를 생성하지 않는다. 충돌 시 governed current state가 우선한다.

## ALWAYS_KNOW
- Channel != Persona. 채널은 실행 인스턴스이고 Persona는 지속 조직 정체성이다.
- Git persistent governed current state가 Chat/Handoff/Memory보다 우선한다.
- RETURN/HANDOFF packet은 운반수단이며 최종 SoT가 아니다.
- Owner는 목표, 우선순위, 주요 Requirement/Design, Freeze/Release/Production의 최종 승인자다.
- 중요 P0/P1 semantic change는 exact target과 validation lineage를 요구한다.
- TEST_PASS != REQUIREMENT_PRESERVATION_PROOF.
- Persona Memory/Worklog는 continuity source이며 authority SoT가 아니다.
- 중요한 사실/결정/작업상태는 Git persistent artifact 또는 Persona Memory/Worklog에 남겨 채널 교체 시 재현한다.

## CURRENT_GLOBAL_WORK
- Git-first Project Instructions bootstrap + Persona runtime selector + persistent Persona memory/worklog continuity candidate를 구축 중이다.
- Candidate branch: `aaa-project-instructions-git-bootstrap-v1.0`.
- Detailed Project Instructions는 Git에 두고 ChatGPT Project Instructions에는 최소 bootstrap URL 지침만 남기는 방향이다.

## CURRENT_GLOBAL_BLOCKERS
- 이 bootstrap/memory 구조는 아직 `WORKING_CANDIDATE_NOT_ACTIVE_AUTHORITY`이며 governed activation/validation이 남아 있다.
- Active Organization의 Core B authority/persona coherence incident는 별도 P0 remediation이 열려 있다. bootstrap candidate가 그 충돌을 자동 해결했다고 간주하지 않는다.
- Global current authority surfaces가 충돌하면 material work를 추정으로 진행하지 말고 `BOOTSTRAP_REVIEW_REQUIRED`로 보고한다.

## OWNER_OPERATING_INTENT
- Owner가 새 채널에서 `ASA`, `CTL`, `MOD`, `RES`, `ENG`, `IVA` 등 Persona selector만 입력해도 해당 Persona가 자기 정체성과 기억을 Git에서 찾아 "장비를 챙기듯" loadout하여 이어서 일할 수 있어야 한다.
- 사용자에게 이미 Git에 있는 프로젝트 맥락이나 이전 승계패킷을 반복해서 수동 조립하게 하지 않는다.
- 모든 Persona는 공통맥락 → 자기 Persona memory → 자기 worklog/current task 순으로 복구한다.
- 중요한 새 Owner 지시, correction, blocker, 결정, checkpoint는 해당 Persona MEMORY/WORKLOG에 지속 기록한다.

## COMMON_BOOTSTRAP_ORDER
1. Git bootstrap pointer / canonical Project Instructions
2. Active Persistent Locator / Organization / Shared Contract / Persona Authority
3. 이 `COMMON/PROJECT_MEMORY.md`
4. Runtime Persona selector resolution
5. 해당 Persona `MEMORY.md`
6. 해당 Persona `WORKLOG.md`
7. Current task/blocker/checkpoint/normative refs
8. Persona lock 응답 후 작업

## MEMORY_LOG
- 2026-08-22 04:44 KST | HIGH | ACTIVE | Owner request: 모든 Persona 공통 주입 내용과 Persona별 기억승계/작업일지 loadout 구조를 마련한다.
