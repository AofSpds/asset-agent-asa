[OWNER → AAA-PMO-ORCHESTRATOR]
M3TOP3 WORKBENCH C1 — OWNER-AUTHORIZED CORRECTION
ONE CORRECTION BATCH → FREEZE → ONE AFFECTED-ONLY REVIEW

===============================================================================
0. 승인 결합 · 지금의 수신자는 PMO
===============================================================================

PROJECT = AAA
PRODUCT = ASSET AGENT ASA
REPOSITORY = AofSpds/asset-agent-asa
PACKET_ID = AAA-MWB-C1-PMO-CORRECTION-AND-AFFECTED-REVIEW-v1.0-20260905
OWNER_DECISION_ID = AAA-MWB-C1-OWNER-AUTH-20260905-001
OWNER_APPROVAL_TEXT = 승인합니다.
CORRECTION_BATCH_ID = AAA-MWB-C1-20260905
REVALIDATION_CAMPAIGN_ID = AAA-MWB-C1-AFFECTED-REVIEW-20260905
TARGET_PERSONA = AAA-PMO-ORCHESTRATOR (PMO)
FOLLOW_ON_REVIEW_OWNER = AAA-PMO-VALIDATOR (PMOV)

승인은 직전의 M3TOP3 MODEL WORKBENCH v0.1 BOUNDED CORRECTION 카드에 결합됐다.
이번 허용 범위는 아래 5개 finding에 대한 수정 1회와 affected-only 재검증 1회다.
동일 범위의 착수·단계 전환 승인을 다시 요구하지 않는다.
이것은 후보 수용, merge, 모델 활성화 또는 Finance 재개 승인이 아니다.

승인 기록 — exact Git locator:
commit = ee3b749702d9acba52e1bbe325fd27f6a4150ec4
blob = f6056dd46663fcd0aa4753e1fb719615cea43bff
path = control/persona-memory/v1.0/AAA-ASA/runs/2026-09-05/M3TOP3_MWB_C1_OWNER_APPROVAL_AND_SOURCE_BINDING_v1.0.md

위 기록은 실제 Human Owner 메시지의 결합·연속성 기록이다.
메모 파일 자체가 독립적인 상위 authority나 validation PASS를 만드는 것은 아니다.

이 패킷을 받는 기존 PMO 채널은 PMO로 유지한다.
PMOV는 뒤의 검토 책임자이지 PMO 채널의 새 Persona가 아니다.
MOD/ENG 또는 MODV/ENGV 사용자 채널을 새로 만들도록 요구하지 않는다.

===============================================================================
1. 기준선과 기존 검증 증거
===============================================================================

REVIEWED_MATERIAL_COMMIT = 96db4afb5686175ad61eea127d6965102653bffc
REVIEWED_MATERIAL_TREE = 442ba156a49dd5a7dc62f7d518058226bf29d76b
ORIGINAL_BASE_MAIN = 950bc98b0702cd5564e3d7b24a6624d9818dfbb9
ORIGINAL_BASE_TREE = dd88026ee7b706a72643d5939f1d653ddde8b987
ORIGINAL_TASK_BRANCH = task/aaa/m3top3-model-workbench-20260905
OBSERVED_ORIGINAL_TASK_HEAD = a9b1e59680af76e4d133ffce7aabc6ddeb526813
ORIGINAL_COMPLETION_CARRIER = caf99be5d2a41b9118a997764f7459aa6c272bf7
ORIGINAL_COMPLETION_BLOB = a65bc94235c1e4b65e85502cf2b836a24b0b6b73

원래 material commit 이후 Completion Report/PMO Memory/Worklog만 추가된 carrier를
material 변경으로 오판하지 않는다. 최신 HEAD로 검토 대상을 바꾸지도 않는다.

SOURCE_REVIEW_REPORT_ID = AAA_M3TOP3_MODEL_WORKBENCH_PMOV_REVIEW_CAMPAIGN_REPORT_v1.1_20260905
SOURCE_REVIEW_CAMPAIGN = AAA-MWB-96db4afb-FIRST-REVIEW-20260905
SOURCE_UPLOADED_TEXT_BYTES = 54018
SOURCE_UPLOADED_TEXT_SHA256 = bc3cf51d7343185d2b33cab4bf144bc98f3e9af350766ef4f57234b9d857cc54
SOURCE_CLASS = OWNER_PROVIDED_FINAL_PMOV_REPORT

위 digest는 제공받은 전체 TXT 바이트의 SHA-256이다. 다른 MD export의 digest라고
주장하지 않는다. 승인 기록에는 source-derived 요약과 반례가 있으며 전체 원문을
Git에 byte-exact 복사했다고 주장하지 않는다. 아래 지시는 수정에 필요한 반례와
승인 범위를 자체 포함하므로 이미 있는 문맥을 Owner에게 다시 조립시키지 않는다.

기존 판정은 보존한다:
PMOV = PASS_WITH_LIMITATIONS / blocking 0 / nonblocking limitations 2
MODV = FAIL / blocking 3
ENGV = FAIL / blocking 2

PMOV-NB-01: 과거 build 승인 packet 원본 bytes 부재.
PMOV-NB-02: 과거 author runtime 참여·시간·효과의 자기보고 한계.
두 limitation은 보존하며 별도 역사복구 작업을 열지 않는다.
이번 신규 승인 기록으로 과거 원본의 부재가 치유됐다고 주장하지 않는다.

===============================================================================
2. Bootstrap 및 착수 전 확인 — 실작업에 필요한 범위만
===============================================================================

BOOTSTRAP_URL = https://github.com/AofSpds/asset-agent-asa/blob/aaa-project-instructions-git-bootstrap-v1.0/control/bootstrap/project-instructions/v1.0/AAA_PROJECT_INSTRUCTIONS_CURRENT_CANDIDATE_v1.0.json
LOCAL_ENTRY = AGENTS.md

현행 Project Instructions / active Organization / Shared Contract /
common guard와 COMMON/PROJECT_MEMORY → 자신의 MEMORY/WORKLOG → current task 순으로
복구한다. current governed Git이 이전 handoff·memory 서술보다 우선한다.
이미 닫힌 Core-B/Common Guard 사건을 다시 실행하지 않는다.

착수 시 exact 기준선·승인 기록·기존 task 및 C1 중복 writer 여부를 확인한다.
기존 C1이 있으면 그 checkpoint를 읽어 중복 branch/작업을 만들지 않는다.
실제 미해결 authority 충돌 또는 외부효과 불명확이면 BOOTSTRAP_REVIEW_REQUIRED.
과거 memory 문구의 stale 상태가 current authority로 해소되면 기록하고 계속한다.

최초 응답: CURRENT_PERSONA_LOCK = AAA-PMO-ORCHESTRATOR (PMO)
이후 현재 단계·실제 worker·blocker·다음 산출물을 짧게 보고한다.

===============================================================================
3. 수정 허용 파일 · 보존 파일
===============================================================================

MATERIAL_CHANGE_ALLOWLIST = 아래 네 경로만

F02 = control/m3top3/model-workbench/v0.1/M3TOP3_FORWARD_MODEL_WORKBENCH_ARCHITECTURE_AND_PREREGISTRATION_v0.1.md
F04 = tools/m3top3/model_workbench/contracts.py
F05 = tools/m3top3/model_workbench/workbench.py
F08 = tools/m3top3/model_workbench/tests/test_workbench.py

변경은 R1~R4의 코드·문서 정합성·회귀테스트에 한정한다.
다른 material 파일 변경이 꼭 필요하면 이유와 영향만 보고하고 범위를 임의 확대하지 않는다.
동일 경로의 새 commit revision을 만드는 것은 허용되지만 과거 commit/history는 불변이다.
문서에 C1 변경 근거·finding 연결을 표시하고 과거 검증통과를 소급 기재하지 않는다.

반드시 보존:
- F01 Finance incident/replan report
- F03 model_workbench/__init__.py
- F06 fixtures/synthetic_candidates_v0_1.json
- F07 tests/__init__.py
- tools/m3top3/pit_guard.py, core.py 및 기존 공용 의존성
- active v1 / 기존 scorer·weight·ranking / PIT·GT·Universe·release semantics
- 원래 candidate branch, main, Finance branch, active pointers
- 기존 검증 원본과 원 판정

PIT 수정은 Workbench의 호출·입력 경계에서 수행한다.
공용 PITGuard의 규칙 자체를 수정하는 범위가 아니다.
새 model family, 학습·튜닝, 신규 dependency, 전역 harness 도입은 없다.

===============================================================================
4. 승인된 수정축과 재현 기준
===============================================================================

R1 — Opportunity / SetPolicy 경계
SOURCE_FINDING = MODV-FP-001
관련: TailRankingStage.rank / OpportunityTailRanker.rank / F02 §§2–3

원 보고 반례:
동일 parsed candidates에서 SetPolicy.opportunity_state_required_for_raw_rank만
VERIFIED에서 PARTIAL로 바꾸면 exported ranker의 ranked rows가 5에서 0이 됐다.
full-envelope의 기본값 고정만으로 public interface 분리가 증명되지 않았다.

수정 요구:
Tail Ranking이 전체 SetPolicy를 받거나 소비하지 않도록 경계를 분리한다.
rankability는 Opportunity 소유 의미 또는 별도 제한된 ranking contract로 표현한다.
Confidence/Risk/Eligibility/Set Policy의 변경이 raw opportunity 순위를 바꾸지 않아야 한다.
full-envelope뿐 아니라 exported/public ranking interface까지 회귀검사한다.
명칭만 변경하거나 fixture의 기본값만 고정하는 방식으로 닫지 않는다.

R2 — downstream raw-rank / identity 불변성
SOURCE_FINDING = MODV-FP-002
관련: ForwardModelWorkbench.run / _assert_accounting / replaceable set stage

원 보고 반례:
built-in set constructor에 위임한 뒤 selected rows의 raw_rank를 999로 변경해도
성공 결과가 나왔다. canonical raw_ranking의 원래 ranks는 2와 5였다.

수정 요구:
selected_set의 identity와 raw_rank를 canonical raw_ranking에 대조한다.
중복 selection, 잘못된 originating rank, selected_set과 decision_log의 모순을
성공 결과 생성 전에 명시적으로 거부한다. 정상 skip/substitution/unfilled는 보존한다.
고의로 잘못된 결과를 내는 작은 대체 stage로 해당 후조건을 회귀검사한다.
잘못된 downstream 출력을 조용히 덮어써 정상처럼 보고하지 않는다.

R3 — mandatory PIT firewall과 Mapping 순회
SOURCE_FINDINGS = MODV-FP-003 + ENGV-MWB-02
하나의 작업축이지만 아래 두 우회경로를 각각 닫아야 한다.

원 보고 반례:
(a) caller-supplied no-op pit_guard가 canonical guard를 대체해 future_close가 통과.
(b) 기본 guard에서도 MappingProxyType 또는
    metadata['wrapped_mapping'] = collections.UserDict({'future_close': 1})
    같은 nested non-dict Mapping이 guard_state=PASS로 통과.

수정 요구:
mandatory canonical PIT 검사는 항상 실행되고 optional extension은 추가 검사만 한다.
허용 Mapping/list를 중첩 깊이 전체에서 일관되게 검사한다. 실제 처리할 입력과
검사한 입력이 어긋나지 않도록 Workbench 경계에서 normalization/검사를 정합화한다.
금지 필드가 opaque container로 숨어 PASS하지 않게 한다.
입력 계약을 몰래 축소하거나 공용 PIT 규칙을 약화하지 않는다.
no-op injection, UserDict, MappingProxyType, dict/list의 정상·금지 사례를 검사한다.
local denylist에 future_close 한 항목만 추가하는 임시 처방으로 전체 결함을 닫지 않는다.

R4 — ambient Decimal context 독립성
SOURCE_FINDING = ENGV-MWB-01
관련: OpportunityTailRanker.rank의 unary -Decimal sort/tie-key 경로

원 보고 반례:
alpha = 10000000000000000000000000001
bravo = 10000000000000000000000000002
동일 입력에서 precision 28은 alpha 우선, precision 60은 bravo 우선으로 나왔고
input/run identity는 같지만 result digest가 달랐다.

수정 요구:
허용 exact-decimal domain의 순서·tie-key·직렬화·digest가 외부 Decimal context에
의존하지 않도록 고친다. 위 반례와 정상 tie/부호/zero를 포함한 관련 경계를 검사한다.
특정 precision 숫자만 크게 고정하거나 고정밀 입력을 몰래 잘라 문제를 숨기지 않는다.
전역 Decimal context를 영구 변경해 다른 코드의 동작에 영향을 주지 않는다.

공통:
5개 원 finding ID를 그대로 유지한다. R3로 묶는 것은 작업 묶음일 뿐 두 finding의
삭제·등급 하향이 아니다. 문서 약속이나 테스트 assertion을 약화해 PASS를 만들지 않는다.

===============================================================================
5. PMO 수정 실행 · 한 batch · 한 mutable writer
===============================================================================

PHASE_A = PMO_CORRECTION
MOD/ENG = 실제 필요 역할로 내부 dispatch 가능
MODV/ENGV/PMOV/IVA_DURING_CORRECTION = OFF

권장 순서:
1. MOD가 R1~R4 계약 보정과 4-path touch set을 정리한다.
2. ENG가 그 범위의 구현·회귀테스트를 작성한다.
3. PMO가 author self-check와 범위·보존 상태를 확인한다.
4. 수정 material target을 동결하고 Completion Report를 낸 뒤 author 작업을 종료한다.

같은 파일/worktree를 여러 worker가 동시에 수정하지 않는다.
MOD·ENG의 실제 역할, runtime ID, 채택한 출력, 종료 상태를 기록한다.
도구 없이 Persona 이름만 바꿔 말하고 전문 child 참여를 주장하지 않는다.
현재 기능 부족은 즉시 보고하되 새 harness·채널·provider를 만들지 않는다.

CORRECTION_BRANCH_SUGGESTED = task/aaa/m3top3-model-workbench-c1-20260905
BRANCH_FROM = REVIEWED_MATERIAL_COMMIT

승인된 C1 전용 isolated branch/worktree 하나를 만들거나 동일 C1 기존 것을 복구한다.
원래 검토된 96db4afb…를 직접 부모로 한 correction material commit 1개를 목표로 한다.
작업 중 필요한 commit 수보다 한 batch·한 최종 검토대상·non-force history를 우선한다.
amend/force-push로 이미 동결된 증거를 고치지 않는다.
main이나 Finance/기존 candidate branch에 변경을 합치지 않는다. PR은 필요하지 않다.

Author self-check 허용:
- 기존 targeted tests의 assertion 의미 보존 및 필요한 호출-signature 정합화
- 위 5개 finding/R1~R4에 직접 연결된 회귀테스트 추가
- 동일 targeted suite, import/syntax, deterministic synthetic comparison, diff/hash 확인
- C1 동결 전 같은 범위의 정상적인 디버깅·수정 후 재실행

금지:
전체 repository suite, Finance test/수집, 실제 시장·W1–W8 outcome,
광범위한 fuzz/benchmark, 새 validation program, 통과할 때까지 임의 scope 확대.
Author self-check의 반복과 독립 재검증 cycle은 구분하고 실제 실행 횟수를 기록한다.
기존 기본 fixture 결과는 보존 비교한다. 변경이 필요하면 R1~R4에 직접 귀속된
출력 차이·이유를 설명하고 기대 digest만 바꿔서 성공 처리하지 않는다.

===============================================================================
6. Correction freeze / Completion / 후속 검토 대상 결합
===============================================================================

MATERIAL_CORRECTION_TARGET = C1에서 실제 생성한 commit/tree
DO_NOT_INVENT_TARGET_SHA = TRUE

PMO는 다음을 포함한 보고서 하나를 작성한다:
control/m3top3/model-workbench/corrections/c1/M3TOP3_MWB_C1_PMO_COMPLETION_REPORT_v1.0.md

필수 내용:
- 승인 ID와 exact approval Git ref
- predecessor commit/tree, correction branch, 새 material commit/tree
- 실제 변경 파일·blob·SHA-256 및 허용 4-path diff
- F01/F03/F06/F07와 기존 공용 의존성 보존 결과
- 5개 finding → 수정 위치 → 회귀검사 → 남은 limitation 연결표
- 실제 MOD/ENG 참여·author self-check 결과·시간·작업자 종료 상태
- 변경 없는 기존 증거의 재사용 지도
- 후속 PMOV가 읽을 exact REVALIDATION_TARGET과 아래 §7~9 scope

새 material commit을 먼저 동결하고 보고서는 후속 carrier에 기록한다.
보고서 자기 commit SHA를 자기 본문에 넣으려는 순환 수정은 하지 않는다.
필요한 PMO MEMORY/WORKLOG delta만 별도 후속 control carrier로 추가할 수 있다.
material 4개 파일과 report/continuity carrier 차이는 분리해서 보고한다.

PMO 종료 조건:
- C1 범위의 self-check 및 preservation 결과가 사실대로 기록됨
- 새 exact target과 Completion Report가 읽기 가능
- MOD/ENG/수정 writer 종료 확인
- PMO가 검증 PASS·Owner 수용을 부여하지 않음

INDEPENDENT_REVALIDATION_DURING_PHASE_A = NOT_PERFORMED
NEXT_ROUTE = EXISTING_PMOV_REVIEW_SESSION

이 승인에는 아래 재검증 1회가 이미 포함된다. 범위가 그대로면 추가 Owner 승인은
필요하지 않다. 다만 별도 PMOV runtime의 실제 착수와 권한 존재는 다른 사실이다.
PMO는 PMOV 역할로 전환해 자기 코드를 검증하지 않는다.
실제 session 간 전달 수단이 없으면 완료보고서와 바로 전달 가능한 단일 RETURN
packet을 반환하고 종료한다. 전달했다고 꾸미거나 Owner에게 child 보고서 조립을 요구하지 않는다.

===============================================================================
7. 이미 승인된 후속 PMOV affected-only 재검증
===============================================================================

PHASE_B_OWNER = AAA-PMO-VALIDATOR (PMOV)
PHASE_B_ENTRY = C1_COMPLETION_AND_EXACT_TARGET_FREEZE
MAX_REVALIDATION_CYCLES = 1

entry 조건:
- C1 completion이 이 승인 ID를 가리키고 새 target을 하나로 특정함
- target이 원래 reviewed commit의 C1 descendant이고 실제 material delta가 허용 범위
- 새 target의 self-check·보존·작성 종료가 확인됨
- 해당 C1 재검증이 아직 완료/진행 중이지 않음

대상은 Completion Report의 exact commit/tree에서 한 번 resolve해 고정한다.
branch latest나 뒤에 추가된 carrier로 자동 이동하지 않는다.
후속 검토에서 발견된 필요 수정은 이번 correction branch에 즉시 적용하지 않는다.

PMOV는 원래 가능한 것으로 관측된 native parent–child 실행 방식을 사용한다.
실제 현재 도구/권한을 확인한 뒤 MODV 1개와 ENGV 1개를 호출한다.
모델 명칭/Astra/Ultra 자체를 도구 존재나 성공의 증거로 삼지 않는다.
작성에 참여한 PMO/MOD/ENG runtime을 검증자로 재사용하지 않는다.
child의 추가 delegation, IVA 추가, validator-of-validator는 금지한다.

순서:
PMOV affected control first-pass 동결
→ MODV·ENGV 별도 child 생성
→ 서로의 이번 상세 finding/판정을 공유하지 않은 affected 검토
→ 실제 반환·종료 확인
→ 세 원본을 보존한 보고서 하나 반환

두 child는 기존 5개 finding, 승인된 수정 내용, 새 target을 읽을 수 있다.
재검증이므로 과거 finding을 모르는 최초 blind review라고 주장하지 않는다.
반대로 이번 child 판정이 서로에게 전파돼 합의 PASS가 되는 것은 금지한다.

child 생성/대기/회수 기능이 없으면 즉시 CAPABILITY_BLOCKED.
PMOV가 MODV/ENGV까지 역할 연기하거나 검사 범위를 혼자 넓혀 진행하지 않는다.
실제 ID·격리·종료 상태를 기록하고, 없는 runtime 로그나 PASS를 만들어내지 않는다.

===============================================================================
8. 역할별 재검증 범위 · 증거 재사용
===============================================================================

PMOV:
- 승인 binding, 새 commit/tree/lineage, 허용 material diff와 preserve set
- C1 Completion Report의 source 연결·author 종료·후속 carrier 분리
- 기존 PMOV-NB-01/02 보존; 과거 authority·Finance chain 전체 재감사 금지
- 실제 재검증 dispatch/effect/종료를 별도 운영 부록으로 기록

MODV:
- MODV-FP-001/002/003의 closure와 R1~R3 관련 문서·구현 일치
- Opportunity/SetPolicy 독립성, downstream rank·identity 후조건
- no-op guard 및 non-dict Mapping 우회 방지
- 나머지 의미/claim ceiling은 변경 영향이 있는 부분만 확인
- ENGV가 맡은 전체 targeted suite를 중복 실행하지 않음

ENGV:
- ENGV-MWB-01/02와 R1~R4 수정 경로의 회귀·보존 영향
- 수정된 targeted suite 1회
  PYTHONDONTWRITEBYTECODE=1 python -B -m unittest tools.m3top3.model_workbench.tests.test_workbench
- precision 28/60 동일 입력 비교와 mandatory guard/Mapping 반례를 반드시 포함
- suite에 이미 포함돼 증거가 충분한 검사를 불필요하게 반복하지 않음
- 부족한 경우 finding에 직접 관련된 작은 합성 probe만 추가; 전체 신규 탐색 금지

재사용:
- 원래 96db4afb…의 identity와 8-file manifest/기존 first-pass 원본은 역사 증거로 유지
- F01/F03/F06/F07 및 공용 의존성은 byte equality로 기존 근거 재사용
- 변경 파일의 PASS는 과거 receipt에서 승계하지 않고 새 exact target에 대해 판정
- PMOV/ENGV가 관측한 동일 hash·검사 로그를 공유해도 근거 출처를 표시
- 다른 역할의 결론을 대신 내리거나 테스트 재사용을 독립 재실행이라 하지 않음

5개 finding마다 CLOSED / OPEN / INCONCLUSIVE와 새 근거를 각각 기록한다.
R3의 두 우회경로 중 하나만 닫혀도 전체 CLOSED로 처리하지 않는다.
새 FAIL이나 잔여 blocker는 원문에 남기고 2차 correction/revalidation을 시작하지 않는다.

===============================================================================
9. 재검증 종료·반환·다음 Owner 경계
===============================================================================

재검증은 새 frozen source와 모든 원본을 read-only로 다룬다.
허용 출력은 저장소 밖 scratch의 단일 보고서 및 필요한 로컬 검사 로그다.
검증 중 Git commit/push/수정/새 PR은 허용하지 않는다.

RETURN_FILE = AAA_M3TOP3_MWB_C1_AFFECTED_REVALIDATION_REPORT_v1.0_20260905.md
내용 = exact target, 승인/수정 근거, 5개 closure map, PMOV/MODV/ENGV 원본,
       보존·재사용·실제 검사·제한사항·worker 종료·시간·다음 결정.

PASS라도 자동 merge/activation하지 않는다.
FAIL/INCONCLUSIVE/BLOCKED면 원 판정을 유지한 채 반환한다.
SECOND_CORRECTION_BATCH = NOT_AUTHORIZED
SECOND_REVALIDATION = NOT_AUTHORIZED
IVA_L2 / MODEL_PERFORMANCE_VALIDATION = NOT_PERFORMED
FINANCE_RESUME / MERGE / RELEASE / PRODUCTION = NOT_AUTHORIZED
FINAL_RETURN = AAA-ASA / HUMAN OWNER

===============================================================================
10. 공통 STOP·일정·Owner 화면
===============================================================================

STOP = 미해결 authority/target 충돌, 중복 mutable writer, scope 밖 변경 필요,
       실제 outcome/Finance/provider/AWS 접근 필요, sandbox/credential 권한 확대,
       Owner STOP, 두 번째 수정·재검증 cycle 필요.

Finance는 d17d2229fb541c4b02f65a67f8a28a14334fd308의 HOLD를 보존한다.
FUTURE_SELECTOR_OBSERVED_PENDING_OWNER_DECISION / 20240131 page5 ordinal41,
SOURCE_ADMISSION=NOT_ADMITTED / INGESTED_ROWS=NOT_RECONSTRUCTED는 바꾸지 않는다.
G11C10·PRECHECK·LIVE·raw/cursor 변경·G4/Axis-B 재실행은 없다.

계획 추정치 — 아직 실측 확률분포가 아니며 낮은 신뢰도의 planning range:
수정: P50 45~90분 / P90 2~3시간.
affected 재검증: P50 30~60분 / P90 미산정.
실제 source 확인 후 예상과 근거를 갱신한다. 추가 대기·권한·scope는 구분해 보고한다.
시간을 채우기 위해 작업하지 않고 끝나면 즉시 반환한다.

Owner 보고는 착수/수정 완료·freeze/재검증 종료/실제 blocker에 집중한다.
테스트·해시·commit 개수를 모델 개발 성능 진척으로 바꾸지 않는다.
중단 시 자기 작업자만 정리하고 종료를 확인할 수 없으면 UNKNOWN으로 보고한다.
사용자 대화 창은 유지한다. 작업 종료와 대화 종료는 다르다.

현재 상태 = Owner가 C1 수정 1회 및 affected-only 재검증 1회를 승인함
핵심 판단 = 기존 FAIL 후보를 보존하고 4개 수정축으로 새 exact target을 작성
진행 작업 = PMO/MOD/ENG 수정·self-check; 이 단계의 Validator는 OFF
다음 단계 = PMO 완료·동결 후 별도 PMOV가 이미 승인된 MODV·ENGV 재검증 수행
사용자 행동 = 이 패킷을 기존 PMO 메인 채널에 전달; MOD/ENG/검증자 채널 추가 개설 불필요
PACKET_PREPARED_AT_KST = 2026-09-05T07:09:12+09:00
