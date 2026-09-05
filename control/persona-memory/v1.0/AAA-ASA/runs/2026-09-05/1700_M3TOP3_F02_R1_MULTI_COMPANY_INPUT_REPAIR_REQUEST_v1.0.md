# F02-R1 — 복수회사 실제 입력 복구 제한 실행요청서

PROJECT = AAA
PRODUCT = ASSET AGENT ASA
PACKET_ID = AAA-M3TOP3-F02-R1-MULTI-COMPANY-INPUT-REPAIR-v1.0-20260905
VERSION = v1.0
DATE_KST = 2026-09-05 17:00 KST
FROM_PERSONA = AAA-ASA (ASA)
TARGET_PERSONA = AAA-PMO-ORCHESTRATOR (PMO)
CURRENT_AUTHOR_PERSONA_LOCK = AAA-ASA (ASA)
DOCUMENT_STATE = DRAFT_AWAITING_OWNER_EXECUTION_AUTHORIZATION
DOCUMENT_CLASS = BOUNDED_SUCCESSOR_EXECUTION_REQUEST / OWNER_REVIEW_DRAFT
AUTHORITY_SOT = FALSE
OWNER_DESIGN_DIRECTION = 다음 단계 가시지요.
DESIGN_AND_CONTINUITY_RECORDING = AUTHORIZED_BY_CURRENT_REQUEST
NEW_PMO_EXECUTION_AUTHORIZED = FALSE_AT_ISSUE
NEW_PMO_EXECUTION_DISPATCHED = FALSE
INPUT_SELECTION_POLICY_CHANGE = PROPOSED_NOT_ACTIVE
MODEL_WEIGHT_FEATURE_FORMULA_SCORER_CHANGE = PROHIBITED
PIT_CUTOFF_OR_OUTCOME_FIREWALL_CHANGE = PROHIBITED
RELEASE_PROMOTION_PRODUCTION = NOT_AUTHORIZED
EXECUTION_GRADE = EXTRA_HIGH_RECOMMENDED_NOT_RUNTIME_ATTESTATION
PRO_CLASS = NOT_REQUIRED_FOR_ROUTINE_BOUNDED_WORK
PARALLELISM = MAX_TWO_BOUNDED_AUTHOR_RESEARCH_WORKERS_PLUS_PMO_SINGLE_WRITER
VALIDATION_STATE = NOT_PERFORMED

이 요청서는 작성·저장만 완료한 실행안이다. 문서 수신, Git 저장, Persona 호출만으로 실행승인이 생기지 않는다. 승인 후에도 현행 authority 및 적용 검증요건을 충족한 범위에서만 실행한다.

## 0. Owner가 한눈에 볼 내용

| 구분 | 이번 제안 |
|---|---|
| 목적 | 특정 회사의 공시 한 건만 받는 입력 경로를 보정하여 여러 회사의 실제 F02 입력과 잠정 상대순위를 얻는다. |
| 대상 | PC1의 네 회사 003160 / 025560 / 031980 / 036200. 005290은 기존 원문·출력 재사용 대조군이다. |
| 유지 | W1 cutoff 2024-08-09 23:59:59 KST, 기존 127/57/8/62 분모, F01–F09 산식·가중치, 과거 실행결과. |
| 새 결정 D1 | 2024Q2만 강제하지 않고, 제한된 공식 경로에서 확인한 cutoff 이전 최신 공개 분기(Q2 우선, Q1 대안)를 전년 동분기와 비교하는 입력 선택안을 승인할지 결정한다. |
| D1의 한계 | 최신 확인자료와 실제 전체 최신자료를 구분한다. 회사별 사용 분기가 다를 수 있으며, 이는 잠정 비교의 명시적 제한이다. |
| 실행 목표 | 대조군 포함 최대 5개사. 3개 이상 실제 비교 가능 입력이 주된 기능 목표이며 성공을 보장하지 않는다. 3개 확보가 전체 최적 Top3 증명은 아니다. |
| 제안 자원 | 외부 source action 최대 48회, 신규 네 회사당 12회. 기존 승인 상한·provider 조건보다 넓으면 별도 권한이 먼저 필요하다. |
| 시간 계획 | 실행 P50 계획 2시간 5분 / 보수적 계획 4시간. 실측 분위수가 아닌 LOW-confidence 계획치, Owner·외부 대기 별도. |
| 현재 | 요청서만 작성됨. 새 수집·코드수정·재채점·독립검증은 실행하지 않음. |

## 1. 사실 기반과 해석 경계

[S1] ASA read-only findings: commit ccac37903969fb5a2efcfda9d8cc9b4329a5d4b0, blob 2549908fda9b18114d7030588cb7232f373811fc.
Path: control/persona-memory/v1.0/AAA-ASA/runs/2026-09-05/1647_ASA_SUCCESSION_F02_CONTRACT_VS_EXECUTED_ROUTE_READONLY_FINDINGS_v1.0.md

[S2] PC1 terminal: branch task/aaa/m3top3-process-calibration-pc1-20260905, commit 6b219f9f3a37dd89b26fc1d6ecec6b8eb890fa9f, tree c3dbfeac38c1490843ab7400960b63af5d941118.
Run root: control/m3top3/process-calibration/v1.0/runs/AAA-M3TOP3-PROCESS-CALIBRATION-PC1-20260905-143739-CODEX-01/
Files: PROCESS_COST_CALIBRATION_AND_TUNING_REPORT.md (blob 00358fef8faca320f189298a83150807e492a706); F02_DISCOVERY_RECEIPT.json (0ff2bc443e94f0e6241e33677eaac6e0093be4a8); PROCESS_EFFICIENCY_LEDGER.jsonl (b0f41ffc4a9df3092f55813c1e4616a1345e6927); PROCESS_ROUTE_SUMMARY.json (78e08781e8f3123a7949438a67b458e5bb507b25).

[S3] Reviewed executable commit: c15cbfa9bbedcb3b388b9d101b269ced2fc83bc5.
- tools/m3top3/real_input_replay_v1.py: blob 8d07b6ff2196e794aa2588e7923b366ad9eaa526.
- tools/m3top3/cli_run_real_input_replay.py: blob a302814565f38fda9f72832d2004cc3b16af3ebd.
- tools/m3top3/features_v1_narrow_patch.py: blob b9017f5db0fb637c8a449d5ee3cb1c4a05481076.
- control/core_b/M3TOP3-FEATURE-SCHEMA_v1.0_WORKING.yaml: blob 2550f781c2a901c0faada95dfc4a788503ec669b, F02 section.
- Consumed-path registry: exact blob 5faa4d5739bf9ecb0c11d16f6d7d697ff3983977. An embedded commit/path previously returned 404; use the exact blob, not a newly invented replacement registry.

[S4] Predecessor real-input report: a7b173cf28dc287e1e619e723e938b9bc2c3fd9e; score/seal: 0dfef7b81566e6ec018994d5597f3f8f923944d1.
Executable bundle: M3TOP3-REAL-INPUT-EXECUTABLE-BUNDLE-SHA256:4d828c0308bf892718832e9cb02d87ee7716b9b62c28d643b69b424b5f2b6a4a.
Config SHA256: eecde22a7744cff505c624bb6f0bdb11714352a122632238ea68d9cd0fbacb98.

[S5] Original Top3 objective correction: 0ceec3817532cc78e526fef0c9deb5af0a479d1a.
Path: control/persona-memory/v1.0/AAA-ASA/runs/2026-09-05/1522_OWNER_CORRECTION_M3TOP3_ORIGINAL_TOP3_EXTRACTION_OBJECTIVE_NOT_REDEFINITION_v1.0.md
G2 Owner direction: Issue #53 comment 5548034767. Exhaustive unresolved-row closure is not a first-Replay prerequisite.

[S6] PC1 request: 795484f2b61aca9500bfc9c19039fb6d83e8430b, blob 7939c9de970a1b896f7efb7489aa1d880109eb6d.
Path: control/persona-memory/v1.0/AAA-ASA/runs/2026-09-05/1420_M3TOP3_PROCESS_CALIBRATION_PC1_EXECUTION_REQUEST_v1.0.md
Its bounded correction/reuse provisions do not automatically reopen terminal PC1 or authorize this successor's new input-selection policy.

Confirmed: PC1 ended with Strict scoreable 1/57 and no new F02 source candidates. Its four companies were not rejected by the scorer. The adapter independently has issuer/date/period/layout-specific constraints. [S1–S3]
Not confirmed: all four have usable older sources; early-disclosure bias is quantified; F02 is intrinsically invalid; this plan will produce three usable companies.
All subsequent design choices, resource ceilings and forecasts are ASA proposals, not findings reported by PC1.

## 2. 승계·실행 시작 조건

BOOTSTRAP_URL = https://github.com/AofSpds/asset-agent-asa/blob/aaa-project-instructions-git-bootstrap-v1.0/control/bootstrap/project-instructions/v1.0/AAA_PROJECT_INSTRUCTIONS_CURRENT_CANDIDATE_v1.0.json

승인 후 PMO는 기존 Codex 실행 대화에서 local AGENTS.md 및 bootstrap을 읽고 current authority, COMMON memory/behavior, PMO MEMORY/WORKLOG와 최신 task journal을 복구한다. 별도의 새 PMO 채널을 기본 생성하지 않는다.

계획 작성 시 읽은 main = 950bc98b0702cd5564e3d7b24a6624d9818dfbb9. 이것은 관측 기준이지 해당 main 전체를 실행기준으로 자동 채택하라는 뜻이 아니다.
ASA continuity branch = task/aaa/asa-pmov-review-dispatch-20260905.
실행 기준 = [S2]의 exact PC1 terminal 및 [S3–S4]의 보존된 code/model/input identity.

실행자는 predecessor·authority delta와 중복 실행 여부를 확인한 뒤, 그 기준에서 새 isolated task branch/worktree와 fresh run ID를 만든다. branch가 움직였다는 이유만으로 global rerun하지 않는다. 경쟁 writer가 있으면 해당 실행을 병행 시작하지 않는다.
PC1 branch, 이전 score/seal 및 report는 수정하지 않는다. 알려진 exact blob 회수는 허용하지만 repository-wide discovery·옛 ZIP 복원으로 돌아가지 않는다.

## 3. 범위와 산출 성공조건

PRIMARY_NEW_ISSUERS = KRX:003160, KRX:025560, KRX:031980, KRX:036200
CACHED_CONTROL = KRX:005290
WINDOW = W1
CUTOFF = 2024-08-09T23:59:59+09:00
OUTER_POPULATION = 127
INCLUDE = 57
EXCLUDE_PROVEN = 8
EXCLUDE_UNRESOLVED = 62

경제적 eligibility, 증거확신도, feature scoreability를 각각 보존한다. 입력 없는 56개가 부적격이라는 주장을 하지 않는다. 이번 조사 외 회사는 NOT_ASSESSED_IN_THIS_BATCH로 표시하고 전체 부재를 주장하지 않는다.

주요 기능 목표는 실제 원문→정확한 값→출처/시점 확인→F02→잠정 상대순위의 복수회사 경로다. 검증된 새 입력 최소 2개사, 대조군 포함 최소 3개사가 목표이며 최대 5개다. 같은 기업의 문서 수·입력 leaf 수를 회사 수로 세지 않는다.

3개 미만이면 확보된 적법한 입력과 미달 이유를 반환한다. 빈 점수 실행, 없는 값 채우기, 성공할 때까지 회사 교체는 금지한다. 연구목표 미달과 실행 종료를 구분한다.

## 4. 변경 분류 — 기계적 연결과 D1 결정의 분리

### A. 회사·원문별 연결 보정 후보

회사명·공시일·HTML 줄번호를 005290 상수로 검사하지 않고, 해당 원문과 exact issuer mapping에 결합한다. 단순히 검사를 삭제하거나 입력 파일의 자기선언을 믿는 보정은 금지한다.
공식 문서의 issuer identity, 공시 식별자, 보고기간, 연결/별도, 표·행·열, 지표명, 단위, 수치 셀을 함께 확인한다. 텍스트에 숫자가 포함됐다는 부분문자열 검사만으로 채택하지 않는다.
변경된 line/table locator는 원문 hash와 parser/mapping version에 결합한다. 다른 회사·다른 기간·다른 표의 숫자 이식은 실패해야 한다.

A의 구현 변경이 source-admission/PIT/identity 보증에 미치는 영향은 별도 분류한다. 계산식 불변이라는 이유로 모든 수정을 저위험·의미중립으로 미리 판정하지 않는다.

### D1. 제안하는 입력기간·자료 선택 규칙 — 아직 미승인

POLICY_CANDIDATE_ID = AAA-M3TOP3-F02-INPUT-SELECTION-R1-v1.0

1. 수집대상은 기존 KIND 공식 공시 경로다. 영업(잠정) 제목을 필수조건으로 두지 않고 해당 회사의 분기·반기·잠정실적 공시를 확인한다. DART, 기업 IR, 유료 DB, 신규 API는 이 초안의 자동 확장 범위가 아니다.
2. 모든 사용 값과 사용 버전의 공개시점은 기존 W1 cutoff 이하여야 한다. 오늘 취득한 시각을 과거 공개시각으로 대체하지 않는다. 8월 14일 보고서를 8월 9일 입력으로 소급하지 않는다.
3. 후보기간은 실제 시작·종료일이 확인된 2024년 Q2와 Q1이다. 확인된 사용 가능 후보 중 최신 분기를 택하며 Q2가 확보되지 않으면 Q1을 검토한다. 이는 bounded source set에서 확인한 최신자료이지 전 세계 자료의 최신성을 증명하는 규칙이 아니다.
4. 회사마다 Q2 미발견/미공시 입증/접근 실패/판정 불가를 구분한다. Q2를 못 찾았다고 미공시로 확정하지 않는다. Q1 사용 시 더 최신자료의 확인 한계도 함께 남긴다.
5. 각 회사 내 비교는 같은 지표·같은 연결 기준·같은 분기 길이의 전년 동분기다. Q1은 2023Q1, Q2는 2023Q2와 비교한다. 반기 누계·연간·직전분기를 같은 분기 YoY로 섞지 않는다.
6. 이번 배치는 매출과 영업이익의 두 metric pair를 모두 사용한다. 당기·전기·change_mode·operator_id의 8개 consumed leaf를 확인한다. 이는 제한 배치의 입력 profile이며 F02 전체 정의를 두 지표로 축소하는 변경이 아니다.
7. 원화 단위 변환은 명시된 원/천원/백만원 사이의 정확한 Decimal scaling만 허용하는 안이다. 원문 값·원문 단위를 보존하고 변환값은 DERIVED 및 transform/upstream lineage로 구분한다. 반기 누계에서 분기를 빼내는 새 추정/변환, 임의 반올림, 지표 대용, 수치 추정은 포함하지 않는다.
8. 연결·별도 혼합, 회계기준·기간 불일치, prior=0은 해당 배치에서 미입력/검토 필요로 남긴다. 음수의 부호를 지우지 않으며 기존 RELATIVE 식과 prior=0 금지는 유지한다.
9. 회사별 선택기간, 공개일, period_end, 경과일, 잠정/확정 여부, 후보 선택근거·제외근거를 반드시 출력한다. 새 freshness 점수·penalty·결측치 보정은 만들지 않는다.
10. 회사 간 사용 분기가 다를 수 있다. 공통 cutoff에서의 최근 확인 실적 비교라는 잠정 profile로 명시하고, 같은 분기 실적 전체 비교라고 부르지 않는다. 이 혼합기간 정책의 계약 적합성이 확인되지 않으면 pooled scoring은 하지 않고 확보된 값과 좁은 결정항목을 반환한다.

Owner 승인만으로 검증 PASS가 생기지는 않는다. 승인 후 MOD가 기간·비교·metric 선택 의미를, CTL이 source/PIT/변환 provenance와 기존 contract 연결을 좁게 정리하고 적용 검증 경로를 확정한다. 전역 Shared Contract나 model baseline을 몰래 바꾸지 않는다. 기존 규칙으로 이미 허용된 부분과 새로 bound하는 부분을 구분한다.
D1 미승인 또는 미해결 상태에서 Q1을 Q2로 표시하거나, 기존 승인·기존 PASS를 전용하여 새 profile을 가동하지 않는다.

## 5. 검색·비용 한도와 실패 탈출

다음 수치는 새 제한 실행을 위한 제안값이며 현재 소비한 호출량이나 이미 승인된 Finance 한도가 아니다.
- 신규 네 회사 각각 source action 최대 12회, 합계 48회. query / result open / source fetch / 재시도를 모두 센다. 005290은 기존 cache만 사용하고 신규 CA/공시 수집은 하지 않는다.
- 새 원문 보존 최대 8건, 회사당 최대 2건, 총 20MB. 초과 필요 시 남은 가능한 작업을 마치고 한도 문제를 반환한다.
- 동일 route + 동일 failure + 새 근거 없음 2회 후 세 번째 동일 시도 금지. 대체 route는 새 근거와 횟수를 기록한다. 전체시장 제목검색·pagination은 이번 안에서 제외한다.
- 검색기간은 2024-01-01부터 cutoff까지. 비교값은 이 기간 내 공시 또는 이미 보존된 cutoff-safe cache에서 확인한다. 부족하면 자동 연도·provider 확장하지 않는다.
- 최초 회사에서 약 15분 안에 실제 source locator/시점/필요 수치 확보 가능성 또는 정확한 실패 원인을 먼저 반환한다. 후보가 전혀 없으면 범용 parser를 먼저 완성하지 않는다.
- 시작 후 30분 시점까지 첫 입력 연결 또는 실패 지점을 checkpoint한다. 시간만 보내며 같은 동작을 반복하지 않는다. 다음 checkpoint는 실제 입력 최초 성공, 검증 종료, 최종 종료다.

source action 수와 HTTP request 수, browser interaction 수를 다른 계수로 기록한다. 브라우저 내부 network 총량을 볼 수 없으면 NOT_INSTRUMENTED로 남기며 48회를 실제 HTTP 요청 48회라고 주장하지 않는다. provider의 실제 quota·약관·기존 authorization은 별도로 준수한다. 더 엄격한 기존 한도가 있으면 그것을 적용한다.
시작 전 action ledger를 만들고 action_id/start/end/result/reason/bytes/hash/cache/retry를 실제 행동마다 닫는다. Owner의 수동 선택·브라우저 보조는 HUMAN_ASSISTED로 기록하고 자동화 성공으로 세지 않는다.

## 6. 구현·데이터 보존 범위

아래는 승인 후 적용할 좁은 구현 경계다. 이번 ASA 작성 단계에서는 어떤 실행 파일도 변경하지 않는다.
- 기존 real_input_replay_v1.py의 source manifest·leaf admission 연결부와 cli_run_real_input_replay.py의 명시적 successor profile/bundle 결합부.
- 필요할 때만 전용 parser/adapter helper 1개와 해당 affected test 파일. 정확한 경로 및 dependency touch set은 코드수정 전 P0 기록에 고정한다.
- 별도의 versioned input-selection/mapping artifact, source manifest, feature sidecar, 진행 ledger와 최종 보고서. 기존 frozen contract 파일을 덮어쓰지 않는다.
- 새 run 산출물은 기존 real-input-replay run 규칙의 fresh run root에서 작성한다. raw 원문은 기존 허용 custody 방식으로 보존한다. 그 방식이 현재 권한으로 resolve되지 않으면 새 AWS/S3/prefix를 만들지 않고 해당 write를 중단한다.

PRESERVE_ALL_OTHERS = TRUE
특히 features_v1.py / features_v1_narrow_patch.py / scorer_v1.py / model config / eligibility population / window mapping / price / outcome 실행부는 변경 금지다. 수집과 scoring에는 미래 outcome·가격 경로를 주입하지 않는다.
새 입력 profile의 version은 model_version과 분리한다. 기존 모델은 M3TOP3-v1.0으로 보존하되 input policy와 executable bundle은 새 exact identity를 부여한다. helper·CLI·mapping·transform 의존성까지 hash에 포함하고 수정한 코드를 과거 16-component bundle과 동일하다고 주장하지 않는다.

## 7. 검증 및 재사용

과거 71/71은 원래 exact 적용범위에서만 재사용한다. 코드가 바뀌면 새로운 adapter와 실제 영향 경로에 fresh validation이 필요하다. 같은 코드라는 이유만으로 새 자료를 검증했다고 처리하지 않는다.

필수 확인:
A. 다른 issuer와 다른 HTML 구조의 실제 원문 최소 두 개를 처리하는 positive case. 합성 fixture는 테스트용일 뿐 실제 회사 입력 획득으로 세지 않는다.
B. 회사 바꿔치기, 공시일 위조, cutoff 이후 값, 정정 버전의 후행정보, 잘못된 기간/연결/단위/표 셀, duplicate leaf, hash 불일치, prior=0, 미래 outcome 필드를 거부한다.
C. 숫자는 부호·소수·단위·셀을 함께 exact 검사한다. 원문 안의 비슷한 숫자를 찾는 방식으로 검증을 통과시키지 않는다.
D. 기존 005290 singleton 입력을 같은 조건으로 재현하면 원래 substantive feature/score가 동일해야 한다. 새 run ID·시각 등 행정 metadata 차이는 사전 allowlist로 구분한다.
E. 새 비교회사가 추가되면 percentile과 기존 005290의 새 실행 점수는 달라질 수 있다. 기존 50점을 새 cohort에 고정하지 않는다. 과거 결과 자체는 수정하지 않는다.
F. model/config 보존, 새 adapter/input/bundle exact binding, old score/seal/output 보존을 actual diff와 runtime bytes로 확인한다. 원래 테스트를 고친 새 기대값만으로 정당화하지 않는다.

검증자는 현행 risk class와 authority에 따라 지정한다. P1 paired validation, P0의 L1+IVA 등 적용되는 floor를 이 요청서로 낮추지 않는다. 모든 Persona를 무조건 호출하거나 전체 repo를 재감사하지 않고 필요한 control/model/engineering slice만 exact target에 결합한다. 작성·수정한 사람이 같은 act에서 독립 PASS를 내지 않는다.
한 번의 finding 취합→제한적 correction→affected recheck를 기본 계획으로 한다. 미해결 문제가 있으면 PASS를 만들기 위해 반복 루프를 돌리지 않고 exact blocker를 반환한다.
W1 outcome 노출은 이미 존재하므로 EXPLORATORY_AFTER_W1_OUTCOME_EXPOSURE를 보존한다. 역할 분리만으로 pristine holdout/OOS를 주장하지 않으며, actor의 실제 outcome 접근 여부를 거짓 FALSE로 기록하지 않는다.

## 8. 실행 WBS와 보고 기준

| 단계 | 작업 / 증거완료 조건 | P50 계획 | 보수적 계획 | EWU |
|---|---|---:|---:|---:|
| P0 | 승인·current delta·single writer·exact baseline·계수기 고정 | 5분 | 10분 | 5 |
| P1 | 4개사 bounded source/기간 후보표와 실제 원문 또는 정확한 실패 기록 | 25분 | 45분 | 25 |
| P2 | D1 적용범위와 기존 contract 의미 차이·검증 경로 결합 | 15분 | 30분 | 15 |
| P3 | 실제 source shape에 필요한 adapter/단위/locator 연결 및 입력 검증 | 35분 | 65분 | 25 |
| P4 | affected validation·보존·negative cases·필요 paired/independent 결과 | 25분 | 50분 | 15 |
| P5 | 허용 입력의 새 점수·잠정 순위·seal 또는 근거 있는 미실행 처분 | 10분 | 20분 | 10 |
| P6 | source→score 비용·목표 달성 여부·exact final refs·readback·종료 | 10분 | 20분 | 5 |
| 합계 | LOW-confidence planning prior, 실측 percentile 아님 | 125분 | 240분 | 100 |

현재 실행 진척 = NOT_STARTED. 이 WBS의 계획 완료가 모델개발 100%를 뜻하지 않는다.
P1 원문 후보가 0건이면 P3/P5를 생략하고 미입력·목표미달을 반환한다. 생략 단계의 EWU는 얻지 않는다. 합법적인 조기 종료는 100/100 진척이나 처리속도 개선 증명이 아니다.
P2는 metadata 계약분류이며, 원문을 보지 않고 제도·정책 설계부터 무한 확대하지 않는다. 값의 우열·미래수익률을 보고 D1 선택규칙을 바꾸지 않는다.

각 단계 ACTUAL_START/END, ELAPSED_WALL, ACTIVE/WAIT/REWORK(측정 가능 시), LAST_MATERIAL_PROGRESS, NEXT_TERMINAL_EVENT를 기록한다. 원래 계획과 재예측을 함께 보존한다.
PLANNED_CRU / TOKEN_COST = NOT_CALIBRATED. 실제 노출되지 않은 telemetry는 NOT_INSTRUMENTED. source action/bytes/test-case count/elapsed는 별도 실측 대용량이며 CRU로 둔갑시키지 않는다.
시간계획 초과가 gate waiver 사유는 아니다. 4시간 시점 미완료이면 실제 남은 작업·원인·checkpoint를 보고하고, 권한·비용·진행상태에 따라 현행 stop rule로 종료/계속 여부를 명시한다. 백그라운드 실행을 확인 없이 주장하지 않는다.

## 9. 최종 반환물 — 조사 종료와 모델 진척을 구분

한 run root 안에 필요한 최소 파일만 작성한다.
1. F02_SOURCE_SELECTION_MATRIX: 5개사별 source id/hash, public time, period/basis/unit, 선택·제외 이유, 더 최신자료 확인 한계, failure class, metric/leaf 상태.
2. Input policy/bundle/manifest + SOURCE_MANIFEST + FEATURE_SIDECAR: 승인·계약·원문·변환·consumed leaf의 exact 연결. 승인되지 않은 값은 후보 자료로만 격리한다.
3. PROCESS_ACTION_LEDGER + CHECKPOINTS + AFFECTED_VALIDATION_REPORT: 시도 분모·대기·재작업·human assistance·실행 및 재사용 경계.
4. F02_R1_COMPLETION_REPORT + new score/seal when permitted: 비교가능 회사 수, 기존 1/57 대비 변화, actual claim ceiling, planned-vs-actual, next action.

완료보고 첫 표는 회사 / 사용 분기 / 공개일 / 매출 YoY / OP YoY / F02 / coverage / 잠정순위 / 제한사항 순으로 한다. NA와 unavailable은 0이 아니다. 지표값을 계산하지 않았으면 숫자를 채우지 않는다.
F02-only 점수이며 다른 feature가 여전히 비어 있음을 전면 표시한다. 같은 snapshot의 관측된 일부 집합 내 순위이지 공식 Top3/Top10, U127 최적선택, 모델 성능 PASS가 아니다. 동점 처리도 기존 규칙대로 하며 숫자 세 개를 맞추려 강제로 선정하지 않는다.

terminal은 다음 중 실제 상태로 기록한다.
- COMPLETE_MULTI_COMPANY_PROVISIONAL: 최소 3개 비교가능 입력과 필요한 검증·새 seal 완료. 기능 목표 도달만 뜻한다.
- COMPLETE_PARTIAL_BELOW_TARGET: 입력 일부 확보, 최소 복수회사 목표 미달.
- COMPLETE_NO_NEW_ADMISSIBLE_INPUT: 새 입력 0건, 원인·비용·권고 보존.
- BLOCKED_EXACT_DECISION_REQUIRED: 정책·권한·계약·환경·증거 문제와 필요한 행동을 특정함.

VALIDATION_COMPLETE / PERSISTENCE_COMPLETE / RESEARCH_OBJECTIVE_MET는 각각 별도 기록한다. final commit/tree/changed files/branch/PR 또는 NO_PR 사유/readback와 종료 상태를 포함한다. 자동 merge·main 반영·release는 이 범위가 아니다.

## 10. 금지와 중단 경계

PC1 rerun / 동일 실패 반복 / W2–W8 자동 확대 / 회사 교체·추가 / U127 또는 57 분모 변경 / G1–G3 전수복구 / 옛 ZIP 수색 / 새 CA 조사 / 미래 outcome 재조회 / 추정값 / 가중치·feature 산식 변경은 금지한다.
새 provider·유료자료·credentials·quota 확대·AWS/S3 권한·prefix 확대·validation floor 축소·release/promotion/production은 별도 Owner 경계다.
필수 authority/Persona가 실제 충돌하면 BOOTSTRAP_REVIEW_REQUIRED. 원문 한 건의 실패는 전체 프로젝트 중단 사유가 아니며 다른 승인된 회사 작업은 계속한다. 영향이 국소적이면 해당 lane만 막고 반환한다.

## 11. Owner 승인 카드 — 이번 작성 단계에서는 미승인

DECISION_CARD_ID = AAA-OWNER-F02-R1-EXECUTION-AND-INPUT-SELECTION-20260905-001
DECISION_TARGET = 위 PACKET_ID의 exact Git blob 또는 SHA256
REQUESTED_DECISION = APPROVE_OR_HOLD

승인 요청의 정확한 내용:
- 같은 네 회사의 W1 source/adapter 복구를 새 successor run으로 실행한다.
- D1의 Q2/Q1 최신 확인 공개분기·전년동분기 비교와 명시된 손실 없는 단위변환의 제한 profile을 계약에 결합하고, 필요한 검증 후 잠정 비교에 사용한다.
- 제안한 source-action/보존량 상한을 준수하며 더 넓은 provider·quota·custody를 자동 승인하지 않는다.
- 모델 가중치·산식·PIT cutoff·eligibility·과거 결과·release 상태는 유지한다.

Owner의 현재 “다음 단계 가시지요.”는 직전 안내한 요청서 설계·저장 단계의 진행으로 기록했다. 아직 보지 않은 D1 및 새 호출상한까지 포괄 승인한 것으로 확대하지 않았다.
이 카드에 대한 후속 명시 승인이 붙기 전에는 PMO에게 실행 완료/실행 중이라고 보고하거나 자동 dispatch하지 않는다. 승인 후에는 같은 범위의 일상적 단계마다 반복 승인을 요구하지 않는다.

## 12. ASA 설계 완료 기록

CURRENT_STATE = 후속 요청서 작성, 실행승인 전
DESIGN_BASIS = 기존 PC1 종료·F02 계약/실제 adapter 대조 결과와 Owner의 다음 단계 진행 지시
AUTHOR_SELF_CHECK = 범위·D1 경계·과거결과 보존·새 bundle·비교집합 효과·실패 반환조건의 문서상 대조 완료
PAIRED_OR_INDEPENDENT_VALIDATION = NOT_PERFORMED
NEW_SOURCE_ACQUISITION = NONE_BY_THIS_ASA_ACT
NEW_CODE_OR_MODEL_EXECUTION = NONE_BY_THIS_ASA_ACT
PERSISTENCE_CLASS = ASA_PERSONA_RUN_JOURNAL_AND_DESIGN_REQUEST; 중앙 MEMORY/WORKLOG 과거 본문은 이 act에서 수정하지 않음

현재 상태 = F02-R1 제한 실행요청서 초안 작성. PC1 종료와 Strict 1/57은 유지.
핵심 판단 = 단일회사 입력 제약 보정과 실제 공개기간 선택을 분리하며 D1은 아직 미승인.
진행 작업 = 같은 네 회사의 source→input→잠정순위 실행조건·검증·비용·실패반환 설계.
다음 단계 = exact 요청서의 Owner 결정 후 기존 PMO Codex 대화에서 단일 successor 실행.
사용자 행동 = D1을 포함한 이 제한 실행안의 승인 또는 보류 결정. · 작성시각: 2026-09-05 17:00 KST
