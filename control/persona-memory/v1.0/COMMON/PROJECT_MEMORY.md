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
- Persona != Git branch/worktree. Persona는 조직 정체성이고 branch/worktree는 실행 격리 단위다.
- Git persistent governed current state가 Chat/Handoff/Memory보다 우선한다.
- RETURN/HANDOFF packet은 운반수단이며 최종 SoT가 아니다.
- Owner는 목표, 우선순위, 주요 Requirement/Design, Freeze/Release/Production의 최종 승인자다.
- 중요 P0/P1 semantic change는 exact target과 validation lineage를 요구한다.
- TEST_PASS != REQUIREMENT_PRESERVATION_PROOF.
- Persona Memory/Worklog는 continuity source이며 authority SoT가 아니다.
- 중요한 사실/결정/작업상태는 Git persistent artifact 또는 Persona Memory/Worklog/run journal에 남겨 채널·런타임 교체 시 재현한다.
- ChatGPT와 Codex는 별도 Persona/Memory 체계를 만들지 않는다. 같은 persistent Persona system을 사용하고 bootstrap adapter만 다르게 한다.

## CURRENT_GLOBAL_WORK
- Git-first Project Instructions bootstrap + Persona runtime selector + persistent Persona memory/worklog continuity candidate를 구축 중이다.
- Candidate branch: `aaa-project-instructions-git-bootstrap-v1.0`.
- Detailed Project Instructions는 Git에 두고 ChatGPT Project Instructions에는 최소 bootstrap URL 지침만 남기는 방향이다.
- Codex는 repository root `AGENTS.md` → local bootstrap pointer → `control/bootstrap/codex/v1.0/AAA_CODEX_LOCAL_BOOTSTRAP_v1.0.md` 경로를 사용하도록 candidate가 추가되었다.
- 병렬 Codex workers는 shared MEMORY/WORKLOG에 동시에 쓰지 않고 unique append-only run journal을 사용하도록 candidate가 추가되었다.

## CURRENT_GLOBAL_BLOCKERS
- 이 bootstrap/memory 구조는 아직 `WORKING_CANDIDATE_NOT_ACTIVE_AUTHORITY`이며 governed activation/validation이 남아 있다.
- Active Organization의 Core B authority/persona coherence incident는 별도 P0 remediation이 열려 있다. bootstrap candidate가 그 충돌을 자동 해결했다고 간주하지 않는다.
- Global current authority surfaces가 충돌하면 material work를 추정으로 진행하지 말고 `BOOTSTRAP_REVIEW_REQUIRED`로 보고한다.
- ChatGPT fresh-channel regression과 Codex clean-local-invocation regression 모두 아직 PASS가 증명되지 않았다.

## OWNER_OPERATING_INTENT
- Owner가 새 채널에서 `ASA`, `CTL`, `MOD`, `RES`, `ENG`, `IVA` 등 Persona selector만 입력해도 해당 Persona가 자기 정체성과 기억을 Git에서 찾아 "장비를 챙기듯" loadout하여 이어서 일할 수 있어야 한다.
- Codex에서도 task의 `TARGET_PERSONA`/Persona selector를 기준으로 같은 Persona 기억을 local repository에서 loadout해야 한다.
- 사용자에게 이미 Git에 있는 프로젝트 맥락이나 이전 승계패킷을 반복해서 수동 조립하게 하지 않는다.
- 모든 Persona는 공통맥락 → 자기 Persona memory → 자기 worklog/current task 순으로 복구한다.
- 중요한 새 Owner 지시, correction, blocker, 결정, checkpoint는 해당 Persona MEMORY/WORKLOG 또는 병렬 run journal에 지속 기록한다.
- Persona 호출과 Git branch 생성은 분리한다. 실제 repository mutation 때만 task별 isolated branch/worktree를 사용한다.

## TARGETED_BEHAVIOR_CODE_LOADOUT
- Owner directive dated 2026-08-25: future long-running execution design/reporting shall use empirically calibrated progress, mandatory WBS time fields, CRU compute/resource accounting, and EWU evidence-closed progress accounting.
- Shared behavior code: `control/persona-memory/v1.0/COMMON/AAA_EXECUTION_PROGRESS_TIME_COMPUTE_BEHAVIOR_CODE_v1.0.md`.
- When runtime Persona resolves to `AAA-ASA`, also load `control/persona-memory/v1.0/AAA-ASA/BEHAVIOR_CODE_EXECUTION_PROGRESS_TIME_COMPUTE_v1.0.md`.
- When runtime Persona resolves to `AAA-PMO-ORCHESTRATOR`, also load `control/persona-memory/v1.0/AAA-PMO-ORCHESTRATOR/BEHAVIOR_CODE_EXECUTION_PROGRESS_TIME_COMPUTE_v1.0.md`.
- When runtime Persona resolves to `AAA-ADVISORY-VALIDATOR`, also load `control/persona-memory/v1.0/AAA-ADVISORY-VALIDATOR/BEHAVIOR_CODE_EXECUTION_PROGRESS_TIME_COMPUTE_v1.0.md`.
- These behavior files are persistent operating guidance, not Authority SoT. Governed current state remains superior.

## COMMON_BOOTSTRAP_ORDER
1. Runtime adapter 선택: ChatGPT remote GitHub / Codex local repository
2. Git bootstrap pointer / canonical Project Instructions
3. Active Persistent Locator / Organization / Shared Contract / Persona Authority
4. 이 `COMMON/PROJECT_MEMORY.md`
5. Runtime Persona selector resolution
6. 해당 Persona `MEMORY.md`
7. 해당 Persona `WORKLOG.md`
8. If target is ASA/PMO/ASAV, load the registered role-specific execution progress/time/compute behavior code
9. Current task/blocker/checkpoint/normative refs
10. Persona lock 응답 후 작업
11. 중요 state persistence; Codex 병렬 worker는 unique append-only run journal 사용

## MEMORY_LOG
- 2026-08-22 04:44 KST | HIGH | ACTIVE | Owner request: 모든 Persona 공통 주입 내용과 Persona별 기억승계/작업일지 loadout 구조를 마련한다.
- 2026-08-22 05:02 KST | HIGH | ACTIVE | Owner approval: Codex/local repository runtime을 별도 bootstrap adapter로 추가하되 Persona system은 공유하고, mutation은 task별 branch/worktree로 격리하며 병렬 기록 충돌을 방지한다.
- 2026-08-25 14:05 KST | HIGH | ACTIVE | Owner directed the current Progress Bar + empirical calibration + mandatory WBS time + CRU/EWU compute/work accounting draft to be adopted as persistent behavior guidance for ASA, PMO, and ASAV. Shared and role-specific behavior-code paths registered above.
