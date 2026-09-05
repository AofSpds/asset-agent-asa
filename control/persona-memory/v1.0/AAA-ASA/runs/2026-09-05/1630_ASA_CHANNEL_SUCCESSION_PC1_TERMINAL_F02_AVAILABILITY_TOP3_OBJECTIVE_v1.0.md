# AAA ASA 채널 승계 패킷 — PC1 종료 / F02 수집조건 확인 / 원래 Top3 목적 유지

PACKET_ID = AAA-ASA-CHANNEL-SUCCESSION-PC1-F02-AVAILABILITY-v1.0-20260905
PROJECT = AAA
PRODUCT = ASSET AGENT ASA
FROM_PERSONA = AAA-ASA (ASA)
TARGET_PERSONA = AAA-ASA (ASA)
CURRENT_PERSONA_LOCK = AAA-ASA (ASA)
HANDOFF_TYPE = OWNER_FACING_CHANNEL_SUCCESSION / GIT_CONTEXT_RECOVERY / NO_RERUN
AUTHORITY_SOT = FALSE
NEW_PMO_EXECUTION_DISPATCHED = FALSE
NEW_MODEL_OR_PIT_SEMANTIC_CHANGE_AUTHORIZED = FALSE
RELEASE_PROMOTION_PRODUCTION_AUTHORIZED = FALSE
DATE_KST = 2026-09-05

## 0. 이 채널이 이어받는 일

이것은 ASA 상담·관제 채널의 승계다. PMO 실행 채널을 새로 만드는 패킷이 아니다.
ASA는 Owner와 목적·우선순위·실행요청을 정리하고, PMO는 기존 Codex 실행 대화에서 작업한다.
채널 이동만으로 PMO를 재시작하거나 PC1을 다시 돌리지 않는다.

최신 대화의 핵심:
Owner는 “추가 네 회사가 전부 실패했다면 입력/필터 조건 자체가 현실에 맞지 않게 설계된 것 아닌가?”를 걱정하고 있다.
현재 답해야 할 것은 낙관적 전망이 아니라, 어떤 조건에서 무엇이 막혔는지의 구체적인 구분이다.
다음 우선 확인은 F02 계약·실제 검색조건·공시시점·다회사 입력 어댑터의 적합성이다.
이 패킷은 후속 대규모 수집이나 모델 변경을 승인하지 않는다.

## 1. 반드시 보존할 Owner 목적과 correction

M3Top3는 처음부터 주어진 시점의 시장·산업·기업 조건에서 가장 적합한 세 후보를 찾는 Top3 추출 연구였다.
범용 수익률 예측모델이나 모든 기업의 모든 과거정보를 완벽히 복원하는 프로젝트가 아니다.
이를 “새 목적”, “방향 전환”, “재정의”라고 설명하지 않는다.

기존 목적: 3M Opportunity Discovery / cross-sectional ranker.
기존 평가 중심: Top3 primary, Top10 diagnostic, Critical Miss, 3M MFE Rank.
투자가능성·하락위험·기간수익률은 별도 성과 축으로 구분한다.

Owner 원문:
“우리가 하는 일은 필터링 컨디션 모델을 만드는 거라고 볼수 있어요.
모두를 완벽하게 조정할 필요는 없고 현재 컨디션에서 가장 적합한 대상 세가지를 찾는 연구 프로젝트예요.”
이어 “원래 그랬어요 탑3 추출이라 타이틀도 박아놨는디”라고 correction했다.

추가로 보존할 방향:
- 비어 있는 자료는 평가하면서 필요한 부분만 보완한다. 전수 완성을 선행조건으로 삼지 않는다.
- 관측 / 계산 / 추정 / 미확인을 구분한다. 추정 허용의 방향과 특정 추정방법의 승인·구현은 별개다.
- Owner가 요청한 성능/비용 튜닝은 모델 가중치 튜닝이 아니라 수집·가공·PIT·평가·검증 프로세스 최적화다.
- 지연·낮은 수집 수율·우회 가능한 선택지는 조기에 설명한다. 같은 실패를 반복하며 대기하지 않는다.
- G1/G2/G3 완전성·옛 ZIP 복구·전수 기업행동 조사로 되돌아가지 않는다.
- 없는 값을 꾸며서 세 종목을 채우거나, 자료가 있는 세 회사를 전체 최적 Top3라고 주장하지 않는다.

## 2. Git bootstrap과 복구 순서

REPOSITORY = AofSpds/asset-agent-asa
BOOTSTRAP_URL =
https://github.com/AofSpds/asset-agent-asa/blob/aaa-project-instructions-git-bootstrap-v1.0/control/bootstrap/project-instructions/v1.0/AAA_PROJECT_INSTRUCTIONS_CURRENT_CANDIDATE_v1.0.json

새 채널은 GitHub connector로 bootstrap을 읽고 pointer를 따른다.
Canonical Project Instructions → active Organization / Shared Contract / Persona authority → 공통 실행규칙 → COMMON memory → ASA MEMORY → ASA WORKLOG → 최근 run journal 순으로 복구한다.
명시적으로 다른 Persona가 호출되지 않았으므로 AAA-ASA를 유지한다.

ASA continuity branch = task/aaa/asa-pmov-review-dispatch-20260905
공통 memory = control/persona-memory/v1.0/COMMON/PROJECT_MEMORY.md
공통 실행규칙 = control/persona-memory/v1.0/COMMON/AAA_EXECUTION_PROGRESS_TIME_COMPUTE_BEHAVIOR_CODE_v1.0.md
ASA memory = control/persona-memory/v1.0/AAA-ASA/MEMORY.md
ASA worklog = control/persona-memory/v1.0/AAA-ASA/WORKLOG.md
최근 기록 = control/persona-memory/v1.0/AAA-ASA/runs/2026-09-05/

MEMORY/WORKLOG에는 오래된 8월 상태가 남아 있다. 그것만 읽고 완료된 문제를 현재 blocker로 복원하지 않는다.
현재 MOD/MODV는 AAA-MODEL-ARCHITECT / AAA-MODEL-VALIDATOR다.
옛 Core-B reverse-cutover/R7 문제는 현행 Owner correction과 current projection을 따라 historical로 취급한다.
Git governed current state가 Memory/Worklog 및 이 패킷보다 우선한다.
필수 authority/Persona가 실제로 충돌하거나 읽을 수 없으면 BOOTSTRAP_REVIEW_REQUIRED로 정확한 문제를 보고한다.
단순히 current branch에 파일이 없다는 이유로 유실을 확정하지 말고 알려진 exact commit/blob를 읽는다.

## 3. 즉시 읽을 exact refs

[R1] 원래 Top3 목적 correction
commit = 0ceec3817532cc78e526fef0c9deb5af0a479d1a
path = control/persona-memory/v1.0/AAA-ASA/runs/2026-09-05/1522_OWNER_CORRECTION_M3TOP3_ORIGINAL_TOP3_EXTRACTION_OBJECTIVE_NOT_REDEFINITION_v1.0.md

[R2] PC1 실행요청서 — 실행은 이미 종료됨
commit = 795484f2b61aca9500bfc9c19039fb6d83e8430b
path = control/persona-memory/v1.0/AAA-ASA/runs/2026-09-05/1420_M3TOP3_PROCESS_CALIBRATION_PC1_EXECUTION_REQUEST_v1.0.md
blob = 7939c9de970a1b896f7efb7489aa1d880109eb6d

[R3] PC1 원격 종료 상태 — 이번 승계 준비에서 직접 확인
branch = task/aaa/m3top3-process-calibration-pc1-20260905
observed_head = 6b219f9f3a37dd89b26fc1d6ecec6b8eb890fa9f
observed_tree = c3dbfeac38c1490843ab7400960b63af5d941118
commit_message = PMO: close M3Top3 PC1 process calibration
run_root = control/m3top3/process-calibration/v1.0/runs/AAA-M3TOP3-PROCESS-CALIBRATION-PC1-20260905-143739-CODEX-01/
report = run_root + PROCESS_COST_CALIBRATION_AND_TUNING_REPORT.md
추가 확인 파일 = F02_DISCOVERY_RECEIPT.json / PROCESS_EFFICIENCY_LEDGER.jsonl / PROCESS_ROUTE_SUMMARY.json / PROCESS_CHECKPOINTS.jsonl / AFFECTED_VALIDATION_REPORT.json
PMO journal = control/persona-memory/v1.0/AAA-PMO-ORCHESTRATOR/runs/2026-09-05/143739_m3top3_process_calibration_pc1_pmo_root.md

[R4] ASA의 PC1 접수 및 미해결 쟁점
commit = 063a40bcb5b69d7a5f23d17c98cd0b3c5dbce62e
path = control/persona-memory/v1.0/AAA-ASA/runs/2026-09-05/1611_PC1_REPORT_RECEIPT_ADVISORY_PARTIAL_TELEMETRY_ZERO_GAIN_v1.0.md
blob = 170dedea53aaf299bf4b205a5e08d29389b07566
이 기록은 advisory이며 독립검증 PASS나 새 PMO 실행승인이 아니다.

[R5] 9월 5일 G2 first-Replay 완화에 대한 Owner 지시
https://api.github.com/repos/AofSpds/asset-agent-asa/issues/comments/5548034767
unresolved 전수복구는 실행 선행조건이 아니다.
INCLUDE / EXCLUDE_PROVEN / EXCLUDE_UNRESOLVED를 구분하고 분모를 보존한다.
legal listing provenance와 replay tradability를 구분하며 유효 entry-day 시장자료 사용을 허용한다.
미확인을 부적격으로 바꾸거나 사후정보로 소급 포함하지 않는다.

첨부 보고서의 보조 식별:
filename = 붙여넣은 마크다운(1)(6).md
bytes = 16322
SHA256 = 0112cad7c31677b60e8a918d21a60d8d4be0226cfe727b53b5b2f042f68b1e38
위 hash는 기존 채널 첨부파일의 식별값이다. 새 채널에 같은 /mnt/data 경로가 있다고 가정하지 않는다.
원문은 [R3] Git 경로에서 복구하며 Owner에게 이전 보고서를 다시 붙여넣게 요구하지 않는다.

## 4. 현재까지 실제로 끝난 것

### A. 최초 ZERO_SCOREABLE 실행
W1–W8의 U127 회사×기간 1,016건을 분류하고 실행했다.
INCLUDE 465 / EXCLUDE_PROVEN 37 / EXCLUDE_UNRESOLVED 514.
당시 465개 INCLUDE의 F01–F09 총 4,185 feature block 모두 미입력으로 점수는 0건이었다.
이는 모델 성능 0점이 아니라 평가 입력이 없는 실행이었다. 결과를 덮어쓰지 않는다.

### B. 최초 real-input Strict/Pragmatic 실행
RUN_ID = AAA-M3TOP3-REAL-INPUT-STRICT-PRAGMATIC-20260905-114150-CODEX-01
branch = task/aaa/m3top3-real-input-replay-20260905
report_head = a7b173cf28dc287e1e619e723e938b9bc2c3fd9e
reviewed_code = c15cbfa9bbedcb3b388b9d101b269ced2fc83bc5
score_seal_commit = 0dfef7b81566e6ec018994d5597f3f8f923944d1
executable_bundle = M3TOP3-REAL-INPUT-EXECUTABLE-BUNDLE-SHA256:4d828c0308bf892718832e9cb02d87ee7716b9b62c28d643b69b424b5f2b6a4a
config_sha256 = eecde22a7744cff505c624bb6f0bdb11714352a122632238ea68d9cd0fbacb98
model = M3TOP3-v1.0
terminal = PARTIAL_NONEMPTY_SCORE_ONLY with preliminary raw outcome diagnostic

W1: cutoff 2024-08-09T23:59:59+09:00 / entry 2024-08-12 Open / evaluation last 2024-11-08 / exit 2024-11-11 Open.
W1 outer 127 / INCLUDE 57 / proven exclusion 8 / unresolved exclusion 62.
KRX:005290의 cutoff 이전 KRX/KIND 잠정실적 한 건이 F02 입력으로 연결됐다.
F02 score 50 / final 50.00 / feature coverage 0.1 / PROVISIONAL_MISSING_FEATURES.
단 하나의 회사만 F02가 있어 percentile 50은 singleton 기계적 결과다.
57개를 비교해 그 회사를 1위로 선정한 것이 아니다.

사전 고정된 scoreable cohort 1개에서 raw outcome을 측정:
raw MFE 약 +5.2147% / INCLUDE57 내 raw MFE rank 55/57 / raw exit-open return 약 -19.9387%.
불리한 결과도 보존하되 공식 Top3 선택 성과나 모델 실패 증거로 확대하지 않는다.
공식 Top3/Top10·contract-exact outcome·primary hit·critical miss는 미측정이다.
Pragmatic = NO_DEFENSIBLE_ESTIMATE_EXECUTED / PRAGMATIC_DEFERRED_POLICY_NOT_BOUND.
W2–W8에는 새 입력을 넣지 않았고 동일 빈 입력을 다시 실행하지 않았다.

### C. PC1 프로세스 계측 실행 — 최신 종료 결과
RUN_ID = AAA-M3TOP3-PROCESS-CALIBRATION-PC1-20260905-143739-CODEX-01
start = 2026-09-05T14:37:39.3805426+09:00
end = 2026-09-05T16:00:46.9632098+09:00
elapsed = 약 1시간 23분 8초
terminal = COMPLETE_BOUNDED_ZERO_GAIN_PARTIAL_TELEMETRY

추가 조사한 F02 네 회사:
- KRX:003160: 제한된 공식 경로에서 cutoff-safe 원문 후보를 확보하지 못함.
- KRX:025560: 동일. cutoff 이후 보고서 1건 관찰.
- KRX:031980: 동일. cutoff 이후 보고서 1건 관찰.
- KRX:036200: 동일. cutoff 이후 보고서 1건 관찰.

네 회사 모두 새 입력 확보 0건. PIT admission 후보 0건.
이에 따라 parsing / transform / sidecar / 새 scoring은 실행하지 않았다.
Strict scoreable은 1/57 그대로다.
4/4 수집경로 실패는 확인됐지만 4/4 경제적 부적격·모델점수 탈락은 아니다.
57개 전체를 같은 깊이로 조사하여 56개 자료 부재를 증명한 것도 아니다.

다섯 번째 작업 KRX:005290 CA 조사:
공식 후행 보고서 2건, 총 4,915,819 bytes 확보.
W1 가격조정 불필요를 뒷받침하지만 PRICE-CANONICAL과 실행기의 CA receipt 연결은 미완료.
따라서 정식 outcome 승격은 0건. CA-only 후행자료를 과거 feature로 전용하지 않는다.

PC1의 16개 executable component는 predecessor 그대로 보존됐다고 보고됐다.
fresh affected checks 31/31 PASS, 기존 71/71 code campaign 재사용, code test 재실행 0건.
이는 새 자료·기록·동일성 범위의 검증이지 모델 유효성 PASS가 아니다.
승계 작성자는 원격 종료 commit과 보고서를 읽었으나 전체 원자료·로컬 실행을 독립 재검증하지 않았다.

## 5. 혼동 금지: 세 가지 서로 다른 문제

경제적 eligibility / 증거 확신도 / feature scoreability를 구분한다.

127 → 57: historical eligibility 및 증거확정 정책의 결과.
57 → 1: 현재까지 실제 feature 입력을 완성한 회사 수.
1 → Top3: 아직 비교 가능한 모델 선정시험이 성립하지 않음.

원래 eligibility는 당시 상장 / 진입시점 거래가능 / 반도체 장비·소재 사업범위다.
자료 부족 때문에 unresolved가 많았다는 사실과, 그 회사들이 실제로 적격이었다는 주장은 다르다.
기존 62개 unresolved를 자동 INCLUDE로 바꾸지 않는다.
옛 working count 119와 57+62=119가 같다는 산술만으로 row-level 동일성과 원인을 증명하지 않는다.

## 6. 미확정 가설 — 사실로 승격하지 말 것

Owner의 우려: “현실에서 확보하기 어려운 정보가 존재할 것이라고 가정한 희망적인 기준 아니었나?”
합리적인 점검 질문이지만 아직 원인이 확정되지 않았다.

확인할 가설:
- 특정 분기·잠정실적 제목·자료 형식으로 검색을 너무 좁혔는가?
- cutoff 이전 최신 공개 실적이 아니라 아직 공시되지 않은 분기자료를 요구했는가?
- 이전 공개기간의 비교 가능한 실적은 기존 F02 계약에서 허용되는가?
- 공식 사이트 접근·검색·식별 문제가 실제 source 부재처럼 처리됐는가?
- 현재 adapter가 005290 사례에 특화되어 다른 회사를 일반적으로 받지 못하는가?

아직 단정하지 않을 것:
- F02가 본질적으로 쓸모없다 / 네 기업이 모델조건에서 탈락했다.
- 해당 회사들의 과거 실적자료가 어디에도 없다.
- 조기 공시기업 편향이 이미 입증됐다.
- 이전 분기자료를 쓰면 반드시 해결된다.
- 가격파일만 있으면 현재 F05를 즉시 만들 수 있다.
- 62개 eligibility 전수조사나 F01–F09 전체 가용률 조사가 다음 실행의 필수 gate다.

## 7. PC1에서 이어받을 성능·비용 계측 교훈

목표는 프로세스 최적화이며 모델 튜닝이 아니다.
완전 계측을 요청했으나 실제 결과는 부분 계측이다. 이를 완전 달성으로 보고하지 않는다.

주요 실측:
- 알려진 retrieval route-unit 하한 56, 그중 atomic ledger 54. 전체 시도 수는 미계측.
- global exact-title 검색 40페이지에서 대상 0건, 7페이지는 불필요한 범위 초과.
- cache 2/6 hit. 이를 F02 입력 성공 2건으로 세지 않는다.
- 첫 30분 checkpoint 기록은 약 17분 16초 지연.
- same-route/same-failure 제한이 036200에서 충분히 집행·계수되지 않음.
- active/wait/token/CRU/retry/총 hit rate 등 미계측 값은 0으로 대체하지 않음.
- 검증기 expected-count 오류 1회 재확인, 최종 closure audit의 기록 모순 4건 수정.
- 코드 검증 재사용은 유용하지만 71개 테스트 감소를 수십 분 절감으로 환산할 근거는 없음.
- P50보다 빨리 종료한 것은 속도개선 증명이 아님. 새 입력→점수 단계가 통째로 생략됐음.

후속 실행에서는 첫 실제 행동부터 시작/종료/결과/시간을 기록한다.
동일 경로·동일 실패·새 근거 없음 2회 뒤에는 세 번째 동일 시도를 하지 않는다.
cache·locator/content hash 중복제거·실제 적용 가능한 parser/adapter를 확인한다.
최대 2개 bounded 연구/작성 worker + PMO single writer라는 기존 PC1 상한을 임의 확대하지 않는다.
정식 outcome upgrade가 목적일 때 그 결과를 반영할 경로가 없다면 같은 CA 수집을 다시 선행하지 않는다.
자료 수, 검색 수, 테스트 수와 실제 비교 가능한 회사 수·Top3 판별 진척을 분리 보고한다.

## 8. 새 ASA 채널의 첫 후속 작업

먼저 [R3]과 [R4]를 읽고, 아래의 짧은 read-only 확인을 수행한다.
새 대규모 감사·전체 규칙 재설계·전수수집을 먼저 만들지 않는다.

A. frozen F02 계약과 실행된 source-selection/adapter 조건을 대조한다.
   허용 보고기간, 비교기준, 단위, 연결/별도, 필수 입력, cutoff, 허용 source shape를 확인한다.
B. PC1 네 회사의 기존 검색기록에서 실제 query·기간·발견자료·멈춘 조건을 읽는다.
   원문 미공시 / cutoff 이후 / 검색·접근 실패 / 형식 미지원 / 비교기준 불일치를 증거대로 나눈다.
   기록이 없으면 미확인으로 남기고 당시 검색행동을 꾸며내지 않는다.
C. 바꿀 필요가 있는 것과 이미 허용된 것을 구분해 Owner에게 설명한다.
   기존 계약 안의 다른 수집경로는 실행안으로, 의미변경은 좁은 decision item으로 분리한다.
D. 그 결과를 반영한 다음 PMO 요청서를 설계한다.
   목표는 여러 회사의 비교 가능한 실제 입력과 잠정 상대순위이며, 단순 조사 종료 건수가 아니다.

PC1 보고서의 원래 다음 후보는 W2 process benchmark였지만,
F02 수집조건의 문제를 확인하지 않은 채 같은 검색을 W2에 반복하지 않는다.
W1 재조사 또는 W2 실행은 별도 successor 범위로 정리하고 완료된 PC1 자체는 다시 열지 않는다.
W2라는 이유만으로 clean holdout/OOS라고 주장하지 않는다. 과거 workbook의 outcome 노출 상태를 보존한다.

## 9. 승인·실행 경계

이 패킷으로 허용되는 것은 ASA 맥락복구와 위 read-only 확인·후속 설계다.
새 PMO 실행, 신규 provider/유료자료/credentials/호출량 확대, 가중치·feature·PIT·eligibility 의미 변경,
기존 결과 덮어쓰기, release/promotion/production은 자동 승인되지 않는다.
이미 승인된 bounded 범위의 일반 작업에 같은 승인을 반복 요구하지 않는다.
필요한 새 결정이 있으면 무엇을 바꾸며 무엇은 유지하는지 정확하게 제시한다.

NOT_FOUND를 0·부정적 사실·탈락으로 바꾸지 않는다.
미래수익률·winner를 보고 같은 과거 입력을 유리하게 채우지 않는다.
보고서 읽기·후속 계획 수립을 새 실행 완료나 독립검증 PASS로 표현하지 않는다.
PC1 종료가 확인됐으며 이 ASA 채널에서 후속 수집을 실행 중인 것은 아니다.
다른 PMO runtime이 동작 중인지 확인 없이 중복 작업을 만들지 않는다.

## 10. 새 채널 첫 답변의 초점

CURRENT_PERSONA_LOCK = AAA-ASA (ASA)를 표시하고 다음을 먼저 알기 쉽게 말한다.
“PC1은 끝났고 1/57 그대로입니다. 네 회사는 모델 탈락이 아니라 입력 확보 실패입니다.
다음에는 F02가 실제로 어떤 자료·시점을 요구했고 검색이 어디서 막혔는지부터 확인하겠습니다.”

이후 확인한 조건·실패 사유·바로 적용 가능한 우회안·Owner 결정 필요 여부를 구분한다.
‘금방 된다’, ‘이제 확장만 하면 된다’는 추정으로 안심시키지 않는다.
Owner에게 이미 Git에 있는 맥락을 다시 설명하거나 이전 파일을 재조립하게 요구하지 않는다.

현재 상태 = ASA 채널 승계; PC1 종료, Strict 1/57 유지, 후속 PMO 실행 미착수.
핵심 판단 = 추가 네 회사의 수집 실패는 확인됐지만 모델조건 탈락이나 F02 자체 결함은 아직 입증되지 않음.
진행 작업 = 종료 보고서·원래 Top3 목적·Owner 우려·exact Git refs를 승계 기록으로 보존.
다음 단계 = F02 계약과 실제 수집조건의 짧은 대조 → 현실적인 복수회사 입력 후속 요청서 설계.
사용자 행동 = 새 AAA ASA 채널에 이 패킷 하나를 전달. 추가 자료 재첨부는 불필요. · 작성시각: 2026-09-05 16:30 KST
