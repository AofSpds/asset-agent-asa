# OWNER APPROVAL — F05 market-recognition policy and conditional F05-R1 execution

PROJECT = AAA
PRODUCT = ASSET AGENT ASA
PERSONA = AAA-ASA (ASA)
DATE_KST = 2026-09-05 22:54 KST
CLASS = OWNER_DECISION / MODEL_INPUT_SEMANTIC_BINDING / CONDITIONAL_BOUNDED_EXECUTION_AUTHORIZATION
AUTHORITY_SOT = FALSE

OWNER_DECISION = APPROVE
OWNER_TEXT = "승인합니다."

## 0. 사람말 요약

F05는 "좋은 변화가 시장에 얼마나 반영되기 시작했고, 이미 너무 과열되지는 않았는가"를 보는 M3Top3의 시장반응 항목이다.
F05-R0 결과, W1 적격 57개사의 가격·거래량·거래대금·상장주식수 원자료는 모두 준비됐지만 20일/60일 수익률, 비교군 평균, 거래활성도 가속, 기업행위 처리의 정확한 앞단 계산규칙이 과거 설계에서 완전히 고정되지 않은 것이 확인됐다.
Owner는 아래의 하나의 일관된 F05 계산정책을 승인한다.

## 1. 승인된 F05 정책

POLICY_ID = AAA-M3TOP3-F05-MARKET-RECOGNITION-POLICY-v1.0-20260905

### P1. F05의 경제적 의미
- F05는 배당을 포함한 투자자 총수익 자체가 아니라, 기업의 변화가 시장가격과 거래활성도에 얼마나 반영되기 시작했는지와 과열 정도를 측정한다.
- 기존 F05 downstream scorer/weight/saturation 구조는 변경하지 않는다.

### P2. 20일/60일 horizon
- 달력일이 아니라 거래일 기준을 사용한다.
- 20d component = snapshot cutoff를 끝점으로 하는 직전 20개 거래 세션의 시장가격 변화.
- 60d component = snapshot cutoff를 끝점으로 하는 직전 60개 거래 세션의 시장가격 변화.
- 구현은 필요한 관측치 수/endpoint를 명시적으로 봉인하고 off-by-one ambiguity를 허용하지 않는다.

### P3. 시장가격 수익률의 의미
- raw unadjusted close-to-close discontinuity를 기업행위 시장반응으로 오인하지 않는다.
- KRX가 기업행위 권리락/분할/증자 등에서 적용하는 기준가격/일일 등락 의미를 존중한 market-price-return을 사용한다.
- 현금배당 재투자를 포함한 textbook total-return을 F05에 추가하지 않는다.
- 구현은 bound source에서 기업행위 기준가격이 반영된 일일 변화 의미를 exact field/lineage로 결합해 compound 또는 동등한 수학적 결과를 산출해야 하며, raw close 단순비율로 CA 경계를 가로지르지 않는다.
- 임의 adjustment factor 생성 금지.

### P4. 거래활성도
- daily turnover = Volume / Stocks.
- turnover acceleration = (최근 20거래일 daily-turnover 평균 / 그 직전 20거래일 daily-turnover 평균) - 1.
- 분모 0, 결측, 거래정지, 기업행위 경계는 임의 보간하지 않고 명시적 disposition을 요구한다.

### P5. W1 benchmark
- exact W1 INCLUDE 57개사가 비교집단이다.
- 각 horizon별 eligible-universe benchmark = 57개 admissible company return의 단순 equal-weight 평균.
- 이번 W1에서는 57/57가 admissible한 경우에만 benchmark를 생성한다.
- 특정 회사가 불명확하다고 조용히 56개 이하로 denominator를 축소하지 않는다.
- EXCLUDE_PROVEN / EXCLUDE_UNRESOLVED는 benchmark에 넣지 않는다.

### P6. Corporate Action
- 공식 issuer/KRX evidence로 확인된 기업행위만 사용한다.
- heuristic trigger는 검토 신호일 뿐 CA 사실이나 adjustment factor가 아니다.
- GST와 엑시콘의 W1 경계는 공식 근거로 exact adjudication한 뒤 계산에 포함한다.
- post-cutoff 자료를 이용해 cutoff 이전 경제적 사실을 새로 발명하거나 결과를 맞추지 않는다.

### P7. PIT / leakage
- F05 입력에 사용하는 모든 경제관측은 2024-08-09 snapshot cutoff 이하에서 끝난다.
- 2024-08-12 이후 entry/outcome/future price, future rank/winner, MFE/MAE를 F05 입력선택·계산에 사용하지 않는다.

## 2. 승인된 실행 범위

F05_R1_PREPARATION = AUTHORIZED
F05_R1_EXACT_BINDING = AUTHORIZED
MOD_CTL_BINDING_AND_REQUIRED_VALIDATION = AUTHORIZED
F05_R1_BOUNDED_W1_EXECUTION = CONDITIONALLY_AUTHORIZED_AFTER_PRECHECK_PASS

Conditional auto-continue rule:
- MOD/CTL이 위 P1-P7을 exact contract/input semantics로 결합하고,
- GST/엑시콘 CA 경계를 공식 근거로 닫고,
- adapter가 기존 raw Volume/Amount/Stocks/ChangesRatio 또는 승인된 exact source fields를 semantic-neutral하게 노출하고,
- required affected validation이 PASS하며,
- no semantic deviation / no denominator shrink / no new provider / no outcome leakage가 확인되면,

PMO는 같은 승인 범위 안에서 별도 반복 Owner 승인 없이 F05-R1 W1 57개사 계산으로 자동 계속할 수 있다.

## 3. 허용되는 F05-R1 결과

- W1 INCLUDE 57개사에 대해 가능한 범위의 20d market-price return
- 60d market-price return
- exact 57-member equal-weight benchmark
- turnover acceleration
- 기존 F05 downstream transform에 따른 F05 score
- F05-only provisional relative ranking
- 기존 F02 5개사의 F02+F05 provisional multi-feature view (명확한 coverage 표시)
- exact input/adapter/bundle/validation/score/seal/report/readback

이는 official Top3/Top10 또는 model-performance PASS가 아니다.

## 4. 변경 금지 / Owner stop boundary

별도 Owner 결정 없이는 금지:
- F05 기존 feature weight 20 변경
- downstream F05 recognition velocity 0.50/0.30/0.20 변경
- saturation penalty 변경
- F01-F09 scorer/model config 변경
- W1 INCLUDE 57 denominator 축소 또는 current universe 대체
- CA factor 추정/발명
- 현금배당 total-return으로 의미 변경
- 새 provider/paid source/credential/budget
- W2-W8 확장
- outcome/MFE 기반 튜닝
- main merge/release/production

STOP_REQUIRED only if:
- 승인된 P1-P7과 다른 의미가 필요함
- GST/엑시콘 공식 CA evidence가 충돌하거나 충분히 닫히지 않음
- 57/57 benchmark 조건을 만족하지 못함
- adapter 변경이 semantic-neutral 범위를 넘음
- validation floor를 낮춰야 함
- provider/quota/custody 권한 확대가 필요함

## 5. 근거 상태

F05-R0 terminal = PARTIAL_DECISION_REQUIRED
R0 branch = task/aaa/m3top3-f05-r0-readiness-20260905
R0 remote HEAD = 87a5025f7e126eb66f8864ae8b106f6c5c65aba4
R0 final tree = 7ab484e88cf5a1aa073f0267e462b3d4e2f06ab2

R0 established:
- W1 raw market availability = 57/57
- exact 57 company cohort = closed
- D1-D6 = 0 exact / 6 partial before this Owner decision
- GST / 엑시콘 = CA/discontinuity review required before policy binding
- no F05 score/rank/seal was produced in R0

This Owner decision closes the missing semantic-policy choice; it does not itself fabricate validation PASS or CA evidence.

## 6. Next route

NEXT = PMO creates isolated F05-R1 task branch/worktree and first performs exact MOD/CTL binding + CA adjudication + adapter precheck + affected validation.
IF PASS = auto-continue to bounded W1 57-company F05 computation under this approval.
IF FAIL/CONFLICT = return one exact decision item in plain language; do not improvise.

REPEAT_OWNER_APPROVAL_WITHIN_EXACT_APPROVED_SCOPE = FALSE
