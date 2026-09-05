# M3Top3 다음 프로세스 준비안 — F05 Readiness First

PROJECT = AAA
PRODUCT = ASSET AGENT ASA
PERSONA = AAA-ASA (ASA)
DATE_KST = 2026-09-05 20:55 KST
CLASS = OWNER_FACING_NEXT_PROCESS_PREPARATION / ADVISORY / NOT_EXECUTION_AUTHORIZATION
AUTHORITY_SOT = FALSE
NEW_RESEARCH_EXECUTION_AUTHORIZED = FALSE

## 0. Owner용 한 문장

F02-R1은 여러 회사의 실제 실적 숫자를 모델에 넣는 길을 뚫었다. 다음에는 회사별 공시를 계속 하나씩 늘리기 전에, 이미 확보한 가격자료를 활용할 수 있다면 모델에서 더 큰 비중(20%)을 차지하는 F05를 W1 여러 회사에 한꺼번에 채우는 것이 Top3 판별력을 더 싸고 빠르게 늘릴 가능성이 높다. 단, 가격자료가 기업행위로 왜곡되지 않았는지와 `turnover acceleration` 계산정의가 이미 고정되어 있는지를 먼저 짧게 확인한다.

## 1. F05가 무엇인가 — 사람말

F05 = Market Positioning Balance.
쉽게 말하면 `회사의 변화가 시장에서 이제 막 인정받기 시작했는가, 아니면 이미 주가에 너무 많이 반영됐는가`를 보는 항목이다.

기존 v1 모델의 정확한 비중:
- F02 Numeric Business Inflection = 10%
- F05 Market Positioning Balance = 20%

F05가 보는 필수 축:
- 최근 20거래일의 회사 수익률이 당시 적격기업 전체보다 얼마나 강했는가
- 최근 60거래일의 회사 수익률이 당시 적격기업 전체보다 얼마나 강했는가
- 거래활성도/거래량이 가속되고 있는가

선택사항:
- valuation percentile
- news/report diffusion percentile

선택사항이 없다고 임의로 채우지 않는다. 기존 정의상 optional saturation penalty만 빠진다.

## 2. 왜 F02를 바로 57개로 늘리지 않고 F05를 먼저 보나

### 후보 A — F02 계속 확대
장점:
- 이번 R1에서 실제 다회사 입력 경로가 작동함.
- 실적 숫자라는 의미가 명확함.

단점:
- 회사별 공식 공시를 찾아 원문/기간/표/셀을 연결해야 함.
- 신규 4개사에만 약 2시간 20분 wall이 들었음.
- F02 자체의 모델 비중은 10%.
- 52개사를 같은 방식으로 넓히면 source acquisition이 다시 주비용이 될 가능성이 큼.

### 후보 B — F05 broad coverage
장점:
- 모델 비중 20%로 F02의 두 배.
- 20d/60d 가격·거래량은 회사별 공시보다 deterministic batch 계산에 적합.
- 이미 프로젝트에 2024~2026 KRX-derived 가격자료와 price-control 자산이 존재하므로 재사용 가능성이 큼.
- 잘 준비돼 있다면 W1 57개사를 한 번에 비교할 수 있어 Top3 판별정보 증가량이 큼.

위험/미확정:
- Corporate Action 조정이 끝나지 않은 가격으로 20d/60d 수익률을 계산하면 분할·증자 등의 가격단절을 momentum으로 오인할 수 있음.
- `turnover_or_volume_acceleration`의 모델 의미는 schema에 존재하지만, 실제 upstream 계산식이 exact하게 이미 고정되어 있는지는 이번 준비단계에서 확인이 필요함.
- 당시 적격 57개사의 universe-equal-weight return 계산 시 denominator와 거래정지/누락을 정확히 처리해야 함.

### 후보 C — F01/F03/F04/F06/F07/F09
대부분 event/consensus/qualification/guidance/risk evidence가 필요해 외부자료 탐색과 의미판정 비용이 더 크다. F03은 same-provider PIT consensus가 핵심이라 provider/data readiness가 별도 문제다. F04는 독립 pre-event baseline이 필요해 더 희소할 수 있다. F06/F07은 milestone/fab/customer evidence가 필요하다. F08은 다른 feature evidence가 생긴 뒤 의미가 커진다.

ASA recommendation = F05 readiness check first.

## 3. 다음 프로세스 Stage 0 — 이미 승인된 F02-R1 백업 마감

목적: 이미 끝난 F02-R1 결과를 바꾸지 않고 GitHub에 안전하게 보관.

Owner 승인 완료:
- repository = AofSpds/asset-agent-asa
- branch = task/aaa/m3top3-f02-r1-multi-company-input-repair-20260905
- exact local final result -> same remote task branch only

해야 할 일:
1. 로컬 final report-containing commit/tree 확인
2. 동일 task branch로 push
3. remote HEAD readback
4. LOCAL HEAD = REMOTE HEAD 확인
5. main unchanged 확인

하지 않을 일:
- 재검색 / 재채점 / 새 검증 / main merge / 다음 연구 실행

Stage 0은 다음 연구단계가 아니라 backup closure다.

## 4. 다음 연구 프로세스 Stage 1 — F05-R0 READINESS CHECK

목적: F05를 계산하는 것이 아니라, 지금 가진 자료로 안전하게 계산할 수 있는지를 확인한다.

### Check 1 — 가격자료 범위
W1 snapshot 2024-08-09 이전에 각 W1 INCLUDE 회사에 대해 최소 60거래일 lookback에 필요한 price/volume row가 존재하는지 확인.

출력:
- 57개 중 price 20d 가능 회사 수
- 60d 가능 회사 수
- volume/turnover 계산 가능 회사 수
- 거래정지/누락/비정상 row 목록

### Check 2 — Corporate Action 왜곡
20d/60d 구간에서 split/reverse split/capital change 등 가격단절 가능성이 있는 회사가 어느 정도인지 확인.

원칙:
- raw price discontinuity를 자동 momentum으로 사용 금지
- evidence-backed adjustment가 없는데 임의 factor 생성 금지
- CA가 열린 회사는 정확한 disposition 없이 F05에 넣지 않음

### Check 3 — Universe benchmark
당시 W1 INCLUDE 57개를 정확한 denominator로 사용해 equal-weight 20d/60d return을 만들 수 있는지 확인.

원칙:
- 현재 Universe나 46개 SEMI-UNIVERSE를 W1 57개 대신 사용하지 않음
- EXCLUDE_PROVEN / EXCLUDE_UNRESOLVED를 임의 포함하지 않음
- 누락 row가 있으면 denominator impact를 보고함

### Check 4 — turnover acceleration 정의
Schema는 `turnover_or_volume_acceleration`을 요구하고 executable은 `turnover_acceleration`을 소비한다.

반드시 확인:
- 기존 contract/upstream artifact에 exact 계산식이 이미 있는가
- 없다면 새 식을 임의로 만들지 않음
- 정의가 없으면 `DECISION_REQUIRED`로 반환하고 후보 식을 별도 제안

### Check 5 — Leakage firewall
모든 사용 관측값의 마지막 날짜 <= 2024-08-09.
2024-08-12 이후의 entry/outcome/future price는 F05 입력에 접근하지 않음.

### Stage 1 terminal
- READY_FOR_F05_R1 = price/CA/turnover/denominator 모두 기존 의미로 계산 가능
- PARTIAL_DECISION_REQUIRED = 일부만 준비되고 turnover/CA 등 좁은 결정 필요
- HOLD_DATA_NOT_READY = 가격/CA 자체가 아직 F05를 안전하게 만들 수준이 아님

Stage 1은 read-only feasibility/readiness act로 설계한다. 모델 점수·가중치·PIT 의미는 변경하지 않는다.

## 5. Stage 1이 PASS일 경우에만 준비할 Stage 2 — F05-R1 W1 BROAD MATERIALIZATION

아직 실행 승인 아님.

목표:
- W1 INCLUDE cohort의 가능한 최대 범위에서 F05 입력을 deterministic batch로 materialize
- 같은 snapshot에서 20d/60d universe-relative return과 turnover acceleration을 계산
- F05 score와 coverage 증가를 산출
- 기존 F02 5개사에는 F02+F05 두 feature가 모두 있을 수 있으므로 provisional multi-feature comparison을 별도 표시

중요:
- 공식 Top3는 아님. v1 config는 official Top-K에 complete governed coverage를 요구함.
- 누락회사는 그대로 NOT_FOUND/REVIEW_REQUIRED.
- availability가 적은 subset percentile을 전체 57개 percentile인 것처럼 표현 금지.
- 가격/CA 의미를 바꾸기 위해 score를 맞추지 않음.

## 6. 계획시간 / 진행계측

### Stage 0 F02-R1 remote backup closure
P50 = 10~20분
P90 = 45분
Confidence = MEDIUM
Owner wait/network issue separate.

### Stage 1 F05-R0 readiness
P50 = 35분
P90 = 90분
Confidence = LOW-MEDIUM
외부 web source retrieval을 기본 포함하지 않는 read-only/internal-first check.

EWU planned for Stage 1 = 100
- exact price/release identity + lookback coverage: 25
- CA distortion/readiness: 25
- W1 denominator/equal-weight feasibility: 20
- turnover definition exactness: 20
- leakage/firewall + terminal recommendation: 10

No EWU earned for merely reading files; evidence must close each declared check.
CRU/TOKEN = NOT_CALIBRATED; missing telemetry remains NOT_INSTRUMENTED.

### Stage 2 F05-R1, if later approved
ETA = NOT YET FROZEN.
Stage 1 measured row coverage and data-readiness results must calibrate the execution plan first.

## 7. Owner decision interface for the next request

When Stage 1 preparation/review is returned to Owner, do not ask `Approve F05-R1?` without explanation.
Required Owner-facing order:
1. F05가 무엇인지 한 문단 설명
2. 왜 지금 F05인지
3. 현재 가진 자료로 몇 개사를 계산할 수 있는지
4. 무엇이 위험/미확정인지
5. 승인하면 무엇을 하는지
6. 승인해도 무엇을 하지 않는지
7. ASA recommendation
8. technical exact refs at the end

Owner cognitive load is treated as a project quality/control metric. Technical accuracy cannot be used as justification for an incomprehensible decision request.

## 8. Current disposition

CURRENT_STATE = next process prepared, not launched.
RECOMMENDED_NEXT = close F02-R1 remote backup, then run bounded F05-R0 readiness check before any broad F05 scoring.
WHY = highest apparent Top3-information gain per acquisition cost among currently visible feature candidates, while preserving model semantics and using internalized data first.
OWNER_ACTION_REQUIRED_NOW = NONE for preparation. New research execution authorization will be requested only after the next-process proposal is explained in plain language.
