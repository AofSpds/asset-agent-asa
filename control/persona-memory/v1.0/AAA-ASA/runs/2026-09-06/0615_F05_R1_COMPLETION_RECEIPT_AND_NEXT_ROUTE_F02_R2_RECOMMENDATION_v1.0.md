# ASA RECEIPT — F05-R1 completion and next-route recommendation

PROJECT = AAA
PRODUCT = ASSET AGENT ASA
PERSONA = AAA-ASA (ASA)
DATE_KST = 2026-09-06 06:15 KST
CLASS = OWNER_FACING_ADVISORY_RECEIPT / NEXT_ROUTE_PREPARATION
AUTHORITY_SOT = FALSE

## 0. 사람말 요약

F05-R1은 W1 57개사 전부에 대해 시장반응(F05)을 실제 계산하는 데 성공했고, 전용 Git task branch에 결과·검증·seal·persistence 증거까지 보존됐다. 이는 공식 Top3나 모델 성능 PASS가 아니라, W1에서 F05 기능 경로가 57/57로 작동했다는 기능적·잠정 결과다.

다음 추천은 F05를 다시 손보는 것이 아니라 F02를 5개사에서 더 넓은 W1 cohort로 확장하는 `F02-R2 broad coverage`다. 이유는 F05가 이미 57/57 공통축을 제공하는 반면 F02는 5/57만 채워져 있어 현재 57개사 전체를 F02+F05 기준으로 공정하게 비교할 수 없기 때문이다.

## 1. F05-R1 observed closure

RUN_ID = AAA-M3TOP3-F05-R1-20260905-231028-CODEX-01
TERMINAL_REPORTED = COMPLETE_F05_R1_W1_PROVISIONAL
TASK_BRANCH = task/aaa/m3top3-f05-r1-w1-market-positioning-20260905
CURRENT_REMOTE_HEAD_OBSERVED_BY_ASA = 8f3253e5f4372903b5ebe5f4e1bf6e08bd288239
CURRENT_REMOTE_HEAD_MESSAGE = M3Top3: close F05-R1 persistence readback
REMOTE_MAIN_OBSERVED = 950bc98b0702cd5564e3d7b24a6624d9818dfbb9
MAIN_MUTATION_OBSERVED = FALSE

PMO completion report states:
- F05 calculable 57/57;
- benchmark denominator 57/57 for 20d and 60d;
- CA exclusions 0;
- GST/엑시콘 CA boundaries evidence-closed;
- F05 scoring once;
- D1 four-role validation PASS zero findings;
- fresh post-score IVA PASS;
- no W2-W8/outcome/main/merge/release/production.

ASA independently confirmed the task branch exists, completion report exists, persistence receipt exists, final receipt-child commit exists, and remote main remains unchanged. ASA does not elevate this readback into a new independent reproduction of every raw economic value or validator assertion.

## 2. Important interpretation — six names tied at 85

Observed provisional F05 top has six companies at exactly 85.
This is consistent with current v1 F05 implementation and is not by itself a ranking or sorting defect.

Current formula:
- V = 0.50*Pctl(20d relative return) + 0.30*Pctl(60d relative return) + 0.20*Pctl(turnover acceleration)
- base saturation penalty = max(0, V-85)
- optional valuation/diffusion penalties apply only when those optional inputs exist
- F05 = V - penalty, clipped

Therefore when optional valuation/diffusion inputs are absent, any V >= 85 collapses to F05=85. This creates an intentional saturation plateau in v1. Preserve it for current baseline. Do not tune v1 after observing W1 result. Log as a later Failure Atlas / v2 challenger observation.

## 3. F02+F05 combined view consistency

The report's five-company provisional combined formula `(25*F02 + 20*F05)/45` is consistent with the current scorer's AXIS-level aggregation, not a misuse of F02 feature weight.

- F02 feature weight = 10 and contributes to feature coverage ratio.
- F01+F02 belong to Business_Momentum axis, whose axis weight = 25.
- With only F02 available on that axis, the Business_Momentum axis score equals F02 and receives axis weight 25.
- F05 is the sole Market_Positioning feature and its axis weight = 20.
- Thus for rows with only these two populated axes the scorer uses (25*Business_Momentum + 20*Market_Positioning)/(25+20).

Feature coverage ratio 0.30 (= F02 0.10 + F05 0.20) and available-axis renormalization 45 (=25+20) describe different layers and are not contradictory.

## 4. Next-route comparison

### Recommended: F02-R2 broad coverage
Purpose: expand realized-business inflection from current 5/57 toward the maximum cutoff-safe W1 coverage using the already-proven F02 real-input path.

Why now:
1. F05 already gives a common market-positioning axis to all 57.
2. F02 is the only other feature with a real source/input path already proven on actual issuers.
3. Expanding F02 improves apples-to-apples multi-axis comparison across the cohort without introducing a new provider or a new feature semantic family.
4. F01/F03/F04/F06/F07 generally require more event/consensus/milestone/customer-fab evidence and more semantic adjudication.
5. F08 becomes more informative after more primary model features are populated; F09 has only 5% feature weight.

### Do NOT do next
- do not retune F05 because six names tie at 85;
- do not use W1 outcome to break the tie;
- do not declare the six 85-point names an official Top6/Top3;
- do not expand W2-W8 yet merely to obtain more apparent validation evidence;
- do not compare five F02+F05 rows directly against 52 F05-only rows as if coverage were equal.

## 5. Proposed F02-R2 preparation scope

Preparation-only next design should quantify before execution:
- exact remaining W1 F02 target set = 52 currently unpopulated INCLUDE companies;
- reuse eligibility of F02-R1 adapter/mapping logic;
- official KIND cutoff-safe quarterly/provisional source acquisition route;
- expected Q2-vs-Q1 fallback distribution before cutoff;
- source-action and byte ceilings calibrated from F02-R1 actual cost;
- batchable/automatable locator strategy to avoid repeating manual company-by-company discovery cost;
- no model/scorer/PIT/eligibility semantics change;
- no outcome access;
- no new provider/credential/budget unless separately approved.

## 6. Current recommendation

ASA_RECOMMENDATION = PREPARE_F02_R2_BROAD_COVERAGE_NEXT
EXECUTION_AUTHORIZED_BY_THIS_RECEIPT = FALSE
WHY = highest current expected gain in cohort-wide comparable information using an already proven actual-source path, while preserving F05 v1 behavior and avoiding outcome-driven tuning.

OWNER_DECISION_INTERFACE_FOR_NEXT_MATERIAL_EXECUTION:
Explain F02-R2 in plain language, expected reachable company count/cost, what approval would do, what it would not do, and ASA recommendation. Do not require the Owner to decode task names or Git terminology.
