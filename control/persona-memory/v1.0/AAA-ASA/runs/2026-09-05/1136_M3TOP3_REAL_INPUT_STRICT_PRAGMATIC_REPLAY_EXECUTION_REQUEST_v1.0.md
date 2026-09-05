# M3Top3 실자료 연결·4상태 식별·Strict/Pragmatic Replay 실행 요청서

## 0. 먼저 할 일과 이번 완료 기준

**분류표를 완성하는 일이 아니라, 실제 자료가 모델 점수와 사후 성과로 이어지는 경로를 만든다.**
관측/계산/추정/미확인 식별은 입력을 만드는 과정에서 함께 수행한다. 모든 빈칸을 먼저 조사하지 않는다.

| 항목 | 지시 |
|---|---|
| PROJECT / PRODUCT | AAA / ASSET AGENT ASA |
| PACKET_ID | AAA-M3TOP3-REAL-INPUT-STRICT-PRAGMATIC-REPLAY-EXECUTION-v1.0-20260905 |
| FROM / TARGET | AAA-ASA (ASA) → AAA-PMO-ORCHESTRATOR (PMO) |
| 실행 표면 | 기존 Codex PMO 실행 대화. PMOV 검증 대화가 아님 |
| 우선 목표 | 실제 관측·계산 입력으로 NON-EMPTY STRICT REPLAY |
| 다음 목표 | 가능한 경우 명시적 추정 시나리오와 민감도 비교, 필요한 공백만 선택 보완 |
| 작성 상태 | EXECUTION_REQUEST_PREPARED; 문서 작성은 실행 착수·검증 PASS가 아님 |
| 보존 | 기존 v1 scorer/weights/feature 의미, 이전 0-scoreable 결과, U127 및 제외 기록 |
| 금지 | 전수복구 회귀, 숫자 조작, 추정의 사실 위장, 결과맞춤 입력, 자동 승격·배포 |

Owner 지시: “좋습니다. 실행 요청서 쭉 만들어 봅시다.”
직전 방향: “비어 있는 부분을 모델 평가를 통해 필요한 부분만 보완… 어느 정도는 추정… 완벽할 수 없는 기획”.
이 요청서는 그 방향을 구현 작업과 반환 기준으로 구체화한 것이다. 새 추정방법·가중치·의미 변경을 포괄 승인받았다고 확대해석하지 않는다.

**기존에 승인된 Strict 실자료 연결은 계속한다. 추정방법의 채택이 별도 결정을 요구하면 그 부분만 분리하고 Strict를 붙잡지 않는다.**

## 1. 승계와 권한

Repository: `AofSpds/asset-agent-asa`
Bootstrap: `https://github.com/AofSpds/asset-agent-asa/blob/aaa-project-instructions-git-bootstrap-v1.0/control/bootstrap/project-instructions/v1.0/AAA_PROJECT_INSTRUCTIONS_CURRENT_CANDIDATE_v1.0.json`

실행자는 bootstrap → current Organization/Shared Contract/Persona → COMMON memory/behavior → PMO MEMORY/WORKLOG → 최신 승인·작업 refs 순서로 읽는다. 현재 공통 권한·검증 기준을 이 문서로 낮추지 않는다. 이미 명시적으로 변경된 과거 전수복구 요구는 최신 결정에 따라 해석한다. 전체 저장소 재조사나 bootstrap 재설계를 선행 작업으로 추가하지 않는다.

권한 근거와 원문은 §12에 있다.
- S01: G1 처리 및 G2/G3 6개+추가 10개 승인. 가용 입력·명시적 누락·제외를 사용하는 제한적 평가 경로.
- S02: 그 승인에 따른 PMO 실행 지시. 새 비용/provider/custody, 모델 의미 변경, 배포 권한은 없음.
- S03: 평가 후 필요한 데이터만 보완하고 제한적 추정을 검토하라는 Owner 방향. 특정 추정법의 무조건 채택은 아님.
- S04~S06: 이전 실행의 종료 결과와 실제 코드 제한. 재실행할 과제가 아니라 승계할 사실.

같은 successor 작업이 이미 실행 중이면 중복 시작하지 않는다. PMO가 실제 RUN_ID/시각/환경/branch/worktree/확인한 중복 범위를 기록한다. Git 기록이 조용하다는 이유만으로 모든 외부 프로세스가 종료됐다고 주장하지 않는다.

확인된 predecessor branch는 `task/aaa/m3top3-first-scorecard-20260905`, HEAD는 `79b46dc1f63f1cd215cc0ebc0c91b4ec09e7dc71`이다. 이를 보존하고, 관련 최신 delta 확인 후 별도 successor branch/worktree를 사용한다. 제안 branch: `task/aaa/m3top3-real-input-replay-20260905`. main/Finance/기존 결과는 변경하지 않는다.

## 2. 출발점: 무엇이 끝났고 무엇이 비어 있는가

이 절은 Git/보고서 확인 사실이다. 이후 절의 실행 설계와 구분한다.

- 이전 RUN: `AAA-M3TOP3-FIRST-SCORECARD-20260905-093656-CODEX-01`.
- 실행 코드 HEAD: `fdde257f2330d36236b551a303e8149184c18eba`.
- 보고·산출물 보존 HEAD: `79b46dc1f63f1cd215cc0ebc0c91b4ec09e7dc71`.
- 외부 모집단 1,016 company-window = eligibility INCLUDE 465 + EXCLUDE_PROVEN 37 + EXCLUDE_UNRESOLVED 514.
- INCLUDE 465행의 F01~F09 4,185블록은 모두 NOT_FOUND. 실제 점수·성과는 0건이며 성능 0점이 아니다.
- 당시 47/47 검사는 당시 exact 대상과 제한된 경로에 대한 결과다. 이번 새 경로에 PASS를 자동 이전하지 않는다.
- GF09는 CONTROL_GAP_NOT_EXACTLY_BOUND로 남았다. 전체 Golden PASS라고 부르지 않는다.

현재 adapter는 각 행에 `_missing_feature_inputs`를 넣고, 검사가 NOT_FOUND 외 상태를 거부하며, rankable_count가 0이 아니면 오류를 낸다. CLI도 feature sidecar 인자가 없고 `finalize_without_scored_rows`를 호출한다. 따라서 파일만 옆에 놓는 것으로는 실자료가 사용되지 않는다. [S05]

기존 scorer는 Opportunity axis가 하나 이상 계산되면 누락 가중치를 재정규화해 점수를 낼 수 있다. 일부 eligible 행이 미점수여도 점수 가능한 행의 순위를 반환하되 `INCOMPLETE_COVERAGE` 경고를 남긴다. 그 경고를 지우거나 전체 U127 순위로 확대하지 않는다. [S07]

## 3. 범위: 한 번 연결하고, 같은 규칙으로 확장

### 3.1 파일럿 및 확장 순서

1. 기본 파일럿은 **W1의 기존 INCLUDE 57행**이다. 성과가 좋아 보이는 기간/회사로 바꾸지 않는다.
2. 연결 시험용 소수 행은 W1 INCLUDE를 company_id 정렬 후 앞의 최대 5개로 고정한다. 이는 엔지니어링 시험이며 그 자체로 모델 성능을 평가하지 않는다.
3. 실제 입력 한 건의 흐름을 증명하면 W1 57행을 하나의 비교 배치로 처리한다. 없는 값은 그대로 둔다.
4. 이미 보유한 자료와 동일 변환만으로 가능한 W2~W8은 같은 실행 안에서 확장할 수 있다. 새 대규모 수집은 확대하지 않는다.
5. W1에서 경로가 막히면 이유를 특정한다. 다른 Window의 기존 입력이 기계적으로 준비돼 있다면 사전 고정한 시간순으로 진행하고 W1의 실패도 보고한다. 성과 기반 Window 선택은 금지한다.

| Window | 외부 U127 | 기존 INCLUDE | 검증된 제외 | 미확인 제외 |
|---|---:|---:|---:|---:|
| W1 | 127 | 57 | 8 | 62 |
| W2 | 127 | 57 | 7 | 63 |
| W3 | 127 | 57 | 6 | 64 |
| W4 | 127 | 58 | 3 | 66 |
| W5 | 127 | 58 | 3 | 66 |
| W6 | 127 | 59 | 3 | 65 |
| W7 | 127 | 59 | 2 | 66 |
| W8 | 127 | 60 | 5 | 62 |

465는 회사 수가 아니라 company-window 행 수다. 분모를 465로만 표시하지 말고 외부 1,016과 Window별 127도 함께 표시한다. 새 eligibility 정책 없이 514행을 추정으로 자동 복귀시키지 않는다.

### 3.2 범위 밖

옛 ZIP/manifest 수색, 514 eligibility 전수조사, 17,272슬롯 전수충전, 전체시장 CA 전수확인, 완료된 G4 전체 suite, Workbench 재개발, EOPT, Finance 재개, main merge, release/promotion/production은 하지 않는다.

## 4. 입력 식별: 4상태와 시간 적합성을 분리

**값 단위로 식별한다. 기업 전체를 “관측 기업/추정 기업”으로 단순 분류하지 않는다.**

| evidence_kind | 의미 | STRICT | PRAGMATIC |
|---|---|---|---|
| OBSERVED | 원문에서 직접 확인되는 수치·상태 | 시간·형식 적합 시 사용 | 동일 |
| DERIVED | 관측 입력과 명시적 계산식으로 재현되는 값 | 시간·형식 적합 시 사용 | 동일 |
| ESTIMATED | 근거와 방법·범위를 가진 추정값 | 사용하지 않음 | 채택된 추정 정책 범위에서만 사용 |
| MISSING | 사용 가능한 값이 아직 없음 | 기존 missingness | 기존 missingness |

위 상태는 `evidence_kind`다. 기존 scorer의 `availability_state=AVAILABLE/NOT_FOUND/...`를 이 이름으로 무단 교체하지 않는다. sidecar가 두 체계를 명시적으로 연결한다.

별도 `temporal_status`:
- `CUTOFF_SAFE`: 소비하는 모든 근거가 snapshot cutoff 이전 사용 가능함을 뒷받침.
- `TIME_UNVERIFIED`: 공개 시점/유효기간이 불명확. PIT 입력으로 채택하지 않음.
- `POST_CUTOFF`: 당시 이후 자료. Strict/Pragmatic PIT 입력에서 제외.

현재 추출·계산한 시각은 `produced_at`에 기록한다. 당시 공개 시각인 `publication_at`으로 바꿔 적지 않는다. 발생일·회계기간·공개일·수집일을 구별한다. 날짜만 있는 근거는 불확실 구간을 보존하고, 확인된 가장 늦은 가능시각까지 cutoff 이전일 때만 채택한다.

추정에 미래 자료가 섞이면 ESTIMATED_PIT가 아니다. 사후 복원 연구가 필요하면 별도 retrospective reconstruction 실험으로 제안하되 이번 PIT 경로에 넣지 않는다. 전후 자료 중 “후” 자료가 cutoff 이후라면 사용할 수 없다.

추정값으로 계산한 값은 DERIVED라는 이유로 관측급이 되지 않는다. `contains_estimated_input=true`를 전파한다. 혼합 feature는 leaf별 상태를 남기고, 순위 계산의 다른 회사 입력 영향도 배치 identity로 추적한다.

### 최소 sidecar 필드

`window_id, company_id, feature_id, input_path, value, unit_or_category, evidence_kind, temporal_status, publication_at_or_interval, effective_period, produced_at, source_refs, source_content_hash, transform_or_estimation_method_id, input_lineage_refs, missing_reason`.

추정은 `assumptions, lower/base/upper 또는 허용 범주, uncertainty_basis`를 추가한다. MEDIUM 같은 주관적 신뢰표시는 확률 보정 결과가 아니며 그 자체로 채택 근거가 되지 않는다.

MISSING 사유는 최소 다음을 구별한다: `NOT_COLLECTED`, `RAW_PRESENT_NOT_TRANSFORMED`, `TIME_UNVERIFIED`, `SOURCE_CONFLICT`, `METHOD_UNBOUND`, `SOURCE_UNAVAILABLE`, `NOT_APPLICABLE`. 조사하지 않은 것을 “찾았으나 없음” 또는 실제 부정 사실로 바꾸지 않는다.

## 5. F01~F09: 실제 소비 필드부터 좁게 연결

아래는 기존 구현을 읽어 만든 작업 우선순위다. 정확한 feature 계약·config가 최종 의미 기준이다. [S07~S09]

| Feature | 실행 지시 |
|---|---|
| F02 실적 변화 | 우선 연결 후보. 기존 공식 원문에 현재·비교기간 값이 있으면 metric_pairs로 연결. change_mode를 명시하고 metric_changes는 value+operator_id 객체를 사용한다. 비교기간/연결·별도/단위가 다른 숫자를 섞지 않는다. prior=0에 임의 epsilon을 넣거나 변환식을 바꾸지 않는다. |
| F05 시장 positioning | 기존 가격 활용 후보이나 “가격이 있으니 자동 완성”은 아님. 20/60일 total_return, 각각의 universe equal-weight return, turnover_acceleration의 정확한 의미·계산식·lookback을 확인한다. raw close 비율을 total return으로 위장하지 않는다. 정의/기업행동 처리가 안 된 부분은 missing 또는 별도 proxy 제안으로 둔다. |
| F03 기대 변화 | 실제 vintage가 있는 revision 또는 기존 계약이 허용하는 official_guidance_change만 사용한다. 현재 consensus를 과거 값으로, 정보 없음을 UNCHANGED로 바꾸지 않는다. |
| F01/F06/F07 | cutoff-safe 상업화·예정 milestone·전달단계 근거를 기존 범주에 매핑한다. 최근 서술을 과거 fact로 복사하지 않는다. F07은 기존 activation_alignment 범주를 쓰며 임의의 0.4/0.6/0.8 점수를 직접 주입하지 않는다. |
| F04 surprise | 독립적인 사전 기대 근거가 없으면 missing. 실제 결과에서 “당시 기대”를 역산하지 않는다. |
| F08/F09 | 증거 품질/당시 위험 근거를 반영한다. 추정값에 VERIFIED_HIGH를 붙이거나 조사 미완료를 안전으로 바꾸지 않는다. 이 두 축만으로 Opportunity 입력을 대신하지 않는다. |

F06 `retrieval_complete`, F09 `assessment_complete`, F04 `independent_pre_event_baseline`, milestone `verified`를 점수를 만들기 위해 임의 TRUE로 바꾸지 않는다.

기존 scorer의 hard_risk_gate NONE은 “추가 gate를 적용하지 않음”으로 기록하며 “위험 없음이 증명됨”으로 해석하지 않는다. 알려진 위험은 숨기지 않는다. 적용 근거/정책이 부족하면 해당 영향만 명시하고 임의 감점/안전 판정을 만들지 않는다.

**F02 또는 이미 근거가 연결된 Opportunity feature 하나를 먼저 끝까지 연결한다.** F05의 정의가 덜 닫혔다고 전체 실자료 연결을 기다리게 하지 않는다. 어느 축도 계약상 연결할 수 없을 때만 필요한 최소 source/방법 결정을 즉시 반환한다.

## 6. 구현 요구: all-missing 전용 경로를 넘어서기

### 6.1 실자료 입력 경로

feature sidecar와 source manifest를 받는 새 CLI/adapter 경로를 추가한다. 예시 인자명은 `--feature-sidecar`, `--source-manifest`, `--mode strict|pragmatic`, `--window`; 이름 자체는 구현 선택이다. 최종 보고에 실제 명령을 기록한다.

- source → 추출/계산값 → sidecar → feature_raw_inputs → feature trace → final_score의 lineage를 연결한다.
- 실제 값이 있는데도 `_missing_feature_inputs`로 덮어쓰지 않는다.
- 모든 feature를 NOT_FOUND로만 제한하던 검사를, 상태별 허용 필드·근거·시간 검사로 대체한다.
- rankable_count=0만 허용하던 단언은 실제 분모·점수·제외 회계 검사로 교체한다.
- 기존 all-missing 경로는 음성 테스트로 유지한다. 새 구현이 실제 값을 받아 점수를 낼 수 있음을 양성 테스트로 입증한다.
- 같은 source의 중복 사용·단위·company/window join·중복 row·비유한 수치를 검사한다. 새 가중치나 점수식을 넣지 않는다.
- 기존 consumed-value provenance 검사를 보존하고 leaf별 근거를 연결한다. ESTIMATED라는 라벨로 그 검사를 우회하지 않는다. [S10]

### 6.2 시간축과 가격 입력

동일 연간 Parquet에 snapshot 이전 가격과 이후 outcome이 함께 있을 수 있다. model 단계에는 cutoff 이하로 잘린 별도 입력만 노출한다. 원파일 식별을 위한 해시 확인과 미래 경제적 값을 모델에 공급하는 행위를 혼동하지 않는다.

lookback의 가격/거래량/단위 적합성을 확인하고, outcome 데이터는 predictions/input/추정정책을 고정한 후 별도 단계에서 사용한다. 미래 분할/수익률을 보고 과거 모델 입력이나 포함 여부를 유리하게 바꾸지 않는다.

### 6.3 배치와 비어 있지 않은 결과

F02/F03/F05에는 횡단면 계산이 있다. 회사별 단독 percentile 점수를 합쳐 전체 순위로 만들지 않는다. 각 Window의 INCLUDE 배치를 유지하고, 없는 행은 누락으로 보고한다. 기본 실행에서 점수 가능한 행만 재배치해 정규화 기준을 몰래 바꾸지 않는다.

non-empty는 `final_score is not None`이다. 유효한 수치 0도 점수다. “non-zero score”를 목표로 만들지 않는다. 합성값으로 양성 단위테스트를 통과한 것과 실자료 연결 성공을 구별한다.

### 6.4 outcome 계산 경로

점수·선택이 있는 경우 실제 outcome join을 실행한다. 기존 계약의 MFE/MAE/기간 수익률·순위·적중 정의를 읽어 적용한다. 정의가 확인되지 않은 metric은 새로 발명하지 말고 미측정 처리한다.

모델 선택은 outcome 확인 전에 고정한다. 선택 종목의 outcome이 측정 불가하면 선택기록과 사유를 남기고 다음 종목으로 대체하지 않는다. 실제 필요한 종목/기간의 CA·거래정지·가격 비교가능성만 처리한다. 확인되지 않은 raw 수익률을 조정·total return과 같은 이름으로 출력하지 않는다.

## 7. Strict → Pragmatic → 필요한 공백만 보완

### A. STRICT: 이번 핵심 실행

OBSERVED/DERIVED이면서 CUTOFF_SAFE인 입력을 기존 v1에 공급한다. 현재 계약대로 NA를 유지한다. 실제 입력값 수, 실제 점수 수, 실제 측정 outcome 수를 각각 출력한다.

최소 한 건의 실자료 점수는 연결 성공일 뿐 모델 성능 검증이 아니다. 작은 배치에서 Top3/Top10 적중률이 자동으로 높아질 수 있으므로 후보 수≤K인 hit@K는 판별력이 없는 수치로 표시한다.

### B. PRAGMATIC: 별도 추정 정책을 가진 조건부 실험

먼저 근거가 있는 소수 입력만 추정 후보로 제시한다. 기존 정책으로 채택 가능한 경우에만 실행하고, 새 imputation/feature 의미가 필요한 경우에는 exact field·방법·범위·영향·권고를 한 Owner decision card로 묶는다. 승인 대기를 Strict의 중단 이유로 삼지 않는다.

정책에는 대상 필드, 사용하는 cutoff-safe 근거, 수치/범주 산출 규칙, 불확실 범위, 사용 불가 조건, 버전을 기록한다. 모델의 최종 점수를 직접 찍어 넣지 않는다. LLM의 기억·회사 이름만으로 과거 사실이나 공개일을 채우지 않는다.

추정 정책은 outcome을 보기 전에 고정한다. 같은 비교 대상에서 STRICT와 PRAGMATIC 입력을 따로 저장하고 어떤 값이 바뀌었는지 남긴다. 추정정책을 아직 채택하지 못하면 `PRAGMATIC_DEFERRED_POLICY_NOT_BOUND`로 반환한다. 이는 Strict 결과 실패를 의미하지 않는다.

### C. 민감도와 선택 보완

허용된 수치의 low/base/high 또는 범주 대안을 사용한다. 범위는 근거로 정하고 좋은 성적이 나오는 구간을 선택하지 않는다. 관련 추정값들의 종속성을 무시한 불가능 조합을 만들지 않는다.

보고: Top3/Top10 구성 변화, 각 종목 순위 범위, 새로 점수화된 행, 추정 의존도. Strict/Pragmatic의 점수화 대상이 다르면 공통 대상 비교와 추가 커버리지 효과를 구분하고, 횡단면 정규화 기준도 함께 밝힌다.

순위 안정성은 예측 정확성의 증명이 아니다. 추정의 질과 누락군 편향을 별도로 한계에 남긴다. 70~80% 같은 임의 완성률을 새 gate로 만들지 않는다.

추가 조사 우선순위는 점수화 해소, 순위 경계 민감도, 근거 확보 가능성, 조사비용으로 정한다. 자동 전수수집으로 돌아가지 않는다. 첫 배치의 보완은 우선순위 상위 최대 5개 source object 또는 동일 source로 해결되는 묶음 1회로 제한한다. 새 입력 없이는 동일 빈 배치를 다시 실행하지 않는다.

outcome을 본 뒤 결과를 참고하여 보완한 후속 실행은 exploratory로 표시한다. 과거 결과를 덮거나 untouched baseline 검증이라고 부르지 않는다.

## 8. 작업 순서·시간·연산량

아래 시간은 **이번 요청서의 LOW-confidence 계획값**이며 소스 확보가 확인된 완료 약속이 아니다. 실행자가 최초 30분 관측으로 재예측한다. 이전 all-missing 실행 61분을 실자료 수집 속도의 벤치마크로 쓰지 않는다.

| 단계 | 실제 산출물 | 계획 P50 | 계획 범위 | 기본 EWU |
|---|---|---:|---:|---:|
| R0 승계·시작 | 실제 RUN/branch/권한·중복 확인 | 10분 | 5~15분 | 5 |
| R1 소비필드·가용성 | F01~F09 필드/분류 규칙, 첫 source와 작업 병목 | 20분 | 15~30분 | 10 |
| R2 입력·실행기 연결 | sidecar importer, non-empty/outcome 경로 | 60분 | 30~120분 | 25 |
| R3 실제 입력 파일럿 | 고정된 소수 행 → W1 배치 입력·근거 | 60분 | 30~120분 | 20 |
| R4 변경분 리뷰 | exact 대상 한 캠페인 및 필요한 제한 수정 | 40분 | 20~75분 | 15 |
| R5 Strict 실행 | 실제 점수·선택·가능한 성과 | 20분 | 10~45분 | 15 |
| R6 보존·보고 | 최종 결과/한계/핵심 공백·실행 명령 | 15분 | 10~30분 | 10 |

R2/R3는 입출력 계약이 맞춰진 후 병렬 가능. 단계 범위를 합친 값을 정확한 전체 ETA로 제시하지 않는다. **초기 Strict 파일럿은 수 시간 규모의 계획이며, 첫 30분 후 실제 범위로 재예측한다.**

추정 실험은 방법이 이미 채택 가능할 때 별도 20~60분 계획 슬롯으로 처리하며 기본 Strict EWU/종료를 붙잡지 않는다. 범위를 실제 추가하면 별도 EWU를 선언하고 전체 분모를 조용히 바꾸지 않는다.

- 최초 30분: 실제 source 한 건 또는 정확한 미확보 지점, 입력형식, 파일럿 집합, 다음 연결 작업을 반환. 분류표의 행 수만 진척으로 삼지 않는다.
- 실자료가 있는 상태에서 60분 동안 input→score 연결이 없으면 source/변환/admission/adapter 중 어느 지점인지 즉시 보고한다. 이는 자동 중단 시한이 아니라 무진척 보고 기준이다.
- 같은 source 경로에서 새 근거 없는 실패 2회 후에는 같은 검색을 반복하지 않는다. 다른 승인된 경로, NA, 국소 제외 또는 Owner 결정을 사용한다.
- 기본 동시 작성 worker는 최대 2개, PMO가 조립. 검증자는 리뷰 때 독립 문맥으로만 투입한다. 이름만 바꿔 같은 agent의 자기검토를 독립검증으로 부르지 않는다.
- Git read·외부 source 요청·재시도·실행·테스트·review 횟수와 시간을 기록. token/CRU를 계측할 수 없으면 NOT_INSTRUMENTED; 0이나 추정 토큰 수로 채우지 않는다.
- 외부 수집은 기존 권한과 provider 한도 이내. 이 파일럿은 source document 최대 24개/네트워크 시도 최대 40회 중 기존 한도와 더 작은 값을 사용한다. 이는 새 provider·유료·credential 권한이 아니다. 기존 권한이 없으면 그 획득만 결정 요청하고 가능한 로컬 작업은 계속한다.

## 9. 리뷰: 변경한 경로를 실제로 검사

PMO는 구현을 끝내 exact candidate를 고정한 뒤 PMOV가 필요한 MODV/ENGV 및 source/PIT 영향에 따른 CTLV 역할을 독립적으로 배정하도록 한다. 별도 visible validator 채널을 Owner에게 요구하지 않는다. 필요한 고위험 검증 기준은 유지하되 코드 전체·과거 전체 suite를 이유 없이 다시 돌리지 않는다. 새 평가경로 승인 여부가 불명확하면 그 부분만 review-required로 남긴다.

한 캠페인: 독립 첫 검토 → finding 통합 → 범위 내 수정 1회 → affected-only 재확인. 잔여 blocking finding은 정확한 영향과 우회안을 반환하고 무한 수정·검증 루프로 바꾸지 않는다. 리뷰가 non-empty 입력·outcome 경로를 실제로 포함했는지 명시한다.

필수 확인:
1. real source→실제 소비 필드→유효한 점수의 lineage. 합성 양성 테스트와 실자료 증거를 별도 보존.
2. OBSERVED/DERIVED/ESTIMATED/MISSING 및 시간 적합성. 추정 전파, 미래 정보/가짜 timestamp 차단.
3. F02 operator/단위/기간, F05 필수 입력/total-return 구별, F06 identity 수정 보존.
4. 0만 허용하던 adapter 제한 제거와 비어 있지 않은 경로. all-missing 동작도 보존.
5. window 배치 정규화, 기존 v1 scorer/weight/config 불변, 양/음/0/null의 구분.
6. source/input/policy/code/config/환경 identity와 결과 재현. 독립 산술 또는 기존 oracle로 확인하고 scorer 출력을 정답으로 복사하지 않음.
7. 실제 outcome fixture/조인 및 CA 미확인 시 미측정·무대체. 실제 성과가 아직 없으면 테스트 PASS를 그 대용으로 삼지 않음.
8. 분모·제외·점수화·추정 의존도·performance claim 표시. GF09 미결을 전체 Golden PASS로 바꾸지 않음.

## 10. 반환물: 숫자가 들어 있는 결과와 재실행 가능한 입력

새 run 경로 아래 원본·source refs·sidecar·정책·명령·code/config hash·review·결과를 보존한다. 여러 파일은 필요할 수 있지만 Owner에게는 **FINAL_REPORT.md 하나를 읽는 입구**로 제공한다.

최소 결과 표:
`Window / outer U127 / eligibility INCLUDE / proven exclusion / unresolved exclusion / observed inputs / derived inputs / estimated inputs / missing inputs / strict scoreable / pragmatic scoreable / selected / outcome measurable / reason`.

별도 주의:
- OBSERVED 등 입력 개수와 점수 가능한 회사×기간 개수를 혼동하지 않는다.
- 원자료 있음, 시간 적합, 모델 입력 연결됨, 실제 소비됨을 구분한다.
- Top3/Top10은 계산 가능 범위로만 표시. 실제 원래 U127 순위를 계산하지 않았으면 NA.
- 성과가 가능한 경우 기존 정의의 metric을 사용하고 같은 평가가능 집합의 기존 단순 benchmark도 가능 범위에서 병기한다. 정의되지 않은 benchmark는 이번에 새로 발명하지 않는다.
- 실측 throughput/시간/비용, 소스 한도 사용량, 보완 가치가 큰 공백 최대 5개를 표시한다.

### 종료 상태를 구별한다

`COMPLETE_STRICT_MEASURED`: 실자료 입력·비어 있지 않은 점수·Window 배치와 측정 가능한 성과·요구 리뷰/보존 완료. 모델 우수성 인증은 아님.

`PARTIAL_NONEMPTY_SCORE_ONLY`: 실자료 점수는 있으나 outcome 또는 비교가 미측정. 점수 연결 완료와 성과 미완료를 분리.

`PARTIAL_DATA_OR_METHOD_BLOCKED`: 어떤 최소 source/방법/연결이 없어 몇 행이 막혔는지 및 가장 빠른 결정을 제시.

`ZERO_SCOREABLE_DIAGNOSTIC_ONLY`: 기존처럼 전부 비어 있으면 진단만 완료. **FIRST_MEASURED_PERFORMANCE_OBJECTIVE=NOT_ACHIEVED**이며 본 요청의 목표 달성/100% 성공으로 표시하지 않는다.

Pragmatic은 별도 `EXECUTED / NO_DEFENSIBLE_ESTIMATE / POLICY_DECISION_REQUIRED / NOT_NEEDED_FOR_THIS_BATCH`를 기록한다. 추정을 못 했다는 이유로 Strict 산출물을 보류하지 않는다.

**존재하지 않는 자료를 만들어 성공시키라는 지시가 아니다. 동일한 빈 입력을 재실행해 성공으로 종결하지 말라는 지시다.**

## 11. 즉시 Owner 결정이 필요한 경계

현재 승인 안의 source 연결·누락·회계·정의된 계산은 반복 승인을 요청하지 않는다. 다음은 정확한 한 카드로 올린다.
- 새 imputation 또는 모델/feature/가중치/의미 변경이 필요한 추정방법.
- PIT를 사후 복원으로 바꾸는 변경, 실제 공개시각 없는 값을 역사 fact로 채택하는 요청.
- 새 유료 provider/예산/credential/외부 custody 또는 기존 호출한도 확대.
- validation floor 완화, release/promotion/production/merge.
- 현재 실행에 필요한 exact 권한 충돌 또는 중복 writer를 안전하게 해소할 수 없는 경우.

카드: 무엇이 막혔나 / 영향을 받는 행·필드 / 기존 범위 내 대안 / 새 결정안 / claim·시간·비용 차이 / 권고. 알려지지 않은 시간을 정밀 ETA로 만들지 않는다. 국소 문제가 아닌 전체 정지가 필요한 경우만 그 이유를 제시한다.

## 12. 정확한 source refs — 새 검색 대신 이 경로부터

S01 `cd4d02a92de496a38ee682145afc2336e4160f7c`:
`control/persona-memory/v1.0/AAA-ASA/runs/2026-09-05/0923_M3TOP3_FAST_REPLAY_REBASELINE_OWNER_APPROVAL_v1.0.md`

S02 `37d7107c2d9a6141edf91ec94bdd9dd13d9177a0`:
`control/persona-memory/v1.0/AAA-ASA/runs/2026-09-05/0925_M3TOP3_FAST_REPLAY_REBASELINE_PMO_DIRECT_DISPATCH_v1.0.md`
Issue #52/#53/#54 최신 방향: comment `5548033695` / `5548034767` / `5548036059`.

S03 `b3d28479c09aef91d3c9f4bd349b4b4f832e9581`:
`control/persona-memory/v1.0/AAA-ASA/runs/2026-09-05/1109_M3TOP3_OWNER_DIRECTION_ITERATIVE_MISSING_DATA_AND_ESTIMATION_POLICY_v1.0.md`

S04 `27b0867e61ec27e9b7d6a10d36cad19c908ffb91`:
`control/persona-memory/v1.0/AAA-ASA/runs/2026-09-05/1049_FIRST_SCORECARD_ZERO_SCOREABLE_REPORT_ADMISSION_AND_NONEMPTY_PATH_OBSERVATION.md`

S05 `fdde257f2330d36236b551a303e8149184c18eba`:
`tools/m3top3/coverage_limited_replay_v1.py` — blob `80fb0dac86b919596bd5c82314e619dd2c8b12b9`.
`tools/m3top3/cli_run_coverage_limited_replay.py` — blob `5be5536def2724d4db7f4c0f7eee1a5046c80bb3`.

S06 `79b46dc1f63f1cd215cc0ebc0c91b4ec09e7dc71`의 run root:
`control/m3top3/first-scorecard/v1.0/runs/AAA-M3TOP3-FIRST-SCORECARD-20260905-093656-CODEX-01/`
Read: `FIRST_RETURN_BINDING_AND_WINDOW_AVAILABILITY.md`, `INPUT_CUSTODY_ATTESTATION.md`, `AFFECTED_ONLY_REVIEW_RECEIPT.md`, `replay-output/REPLAY_RUN_MANIFEST.json`와 해당 run의 최종 보고.

S07 같은 `79b46dc1...`의 `tools/m3top3/scorer_v1.py` — blob `2a797ea705eeb1aef330754fb08ff2182297c139`.
S08 같은 ref의 `tools/m3top3/features_v1.py` — 원형 feature 계산; narrow patch와 함께 읽을 것.
S09 같은 ref의 `tools/m3top3/features_v1_narrow_patch.py` — blob `b9017f5db0fb637c8a449d5ee3cb1c4a05481076`.
S10 같은 ref의 `tools/m3top3/shared_interface_guards_v1.py` — blob `ce5b3b3ad0f09bcbea2aee24abd591974154ea91`.

현재 config: `tools/m3top3/configs/m3top3_v1.0.json`.
SHA-256: `eecde22a7744cff505c624bb6f0bdb11714352a122632238ea68d9cd0fbacb98`.
이전 executable bundle: `82266d51a64382cbd34ee68872a3cd3e3f640c6ff438e84416906f8b8a8ab9c0`. 새 adapter는 새 bundle identity로 기록하며 이전 PASS를 자동 승계하지 않는다.

Population queue blob: `4b3cfbfa9969abe2bd6dff5fdbfeb2db9d31cdae`.
compressed SHA-256: `8b3671d662457aef8c1a5595b33a85a27e08aaee56238e7218f1df0b4df78353`.
Window registry: commit `e59ed048d6da76edcad82c9a58b0d083c6452471`, blob `033817e6335865e411d2bb4b5837434167091458`; CSV SHA-256 `96d63cc98a01b6332cf9486440e7f3fdaa0ec5a2d605f21bc14a4025b46e69fe`.

기존 가격 입력 — S06의 attestations 기준이며 이번 runtime이 직접 readback한다:
- 2024: 24,572,111 bytes; SHA-256 `b0c38943e67637d5faf88429880092cf0f46a394be39860dd3bcd0b04231bccb`.
- 2025: 25,153,419 bytes; SHA-256 `2bfd93c217eb74263bc5020b23fa6debb6b02531c11eaccc2826639bc191559e`.
- 2026: 16,198,533 bytes; SHA-256 `5da710a2fc56f8fe9b1f5126295cc30c3b15c0ee35d28ba808a505ec4a2243c1`; 2026-08-13까지의 revision.
- 세 파일 dataset identity: `419893f0dc8c08019a746182135630cc5f94d6e7ebc2874d5bd23cb54c0a72f7`.
- 이전 local locator는 `C:\Users\ms1pk\Downloads\marcap-YYYY.parquet`. 현재 존재를 보장하는 경로가 아니므로 확인 후 사용한다. 다른 revision은 조용히 바꿔 넣지 않고 새 binding/영향을 기록한다.

v0.2 ZIP은 S06 run root의 `evidence/input-package/AAA_M3TOP3_GR_RESEARCH_PACKAGE_v0.2_WORKING.zip`에 보존됐다. Git blob `65489076e49e0a5dd6fadc53b216ec8c98254954`, 40,210 bytes, SHA-256 `5bbe75a4c9966abcb9f10d2f1e84df983977c1cf76d69e7bda6dfe4f24e60836`. 과거 Owner 재업로드를 다시 선행조건으로 만들지 않는다.

## 13. 최종 실행자 지시

이 파일을 받은 PMO는 이미 승인된 Strict 범위에서 실제 작업을 시작한다. 이 문서를 다시 긴 기획서로 변환하는 것으로 끝내지 않는다. 새 의미·추정정책의 결정만 분리하고, 실제 실자료 연결을 우선한다. Owner는 여러 역할 사이의 수동 전달자가 아니다.

최종 반환은 핵심 결과·재현 refs·남은 판단만 담은 RETURN PACKET 하나로 하고, 첫 성과 미달을 숨기지 않는다. 결과·입력은 Git 등 승인된 영구 저장소에 보존한다. 로컬 임시 파일만 남았으면 완료로 간주하지 말고 그 사실과 안전한 전달 방법을 즉시 밝힌다.

현재 상태 = 후속 실행 요청서 작성 완료; 이전 결과는 ZERO_SCOREABLE이며 새 실행은 미착수.
핵심 판단 = 4상태 식별은 실제 입력 연결의 일부이며, 모델 점수·성과 산출이 본 목표.
진행 작업 = 승인된 Strict 경로부터 구현·실자료 연결·변경분 리뷰·평가; 추정은 별도 정책 경계.
다음 단계 = 첫 실자료 trace → W1 배치 → 가능한 Strict 성과 → 조건부 Pragmatic/민감도 → 필요한 공백만 보완.
사용자 행동 = 이 파일 하나를 기존 Codex PMO 실행 대화에 전달. 기존 승인 밖 결정이 생길 때만 국소 확인. · 작성시각: 2026-09-05 11:36 KST
