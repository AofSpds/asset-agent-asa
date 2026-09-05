# OWNER APPROVAL — M3Top3 F02-R2 Broad Coverage

PROJECT = AAA
PRODUCT = ASSET AGENT ASA
PERSONA = AAA-ASA (ASA)
DATE_KST = 2026-09-06 06:12 KST
CLASS = OWNER_DECISION / BOUNDED_RESEARCH_EXECUTION_AUTHORIZATION
AUTHORITY_SOT = FALSE

OWNER_DECISION = APPROVE
OWNER_TEXT = "승인합니다."

## 0. 사람말 요약

F02는 회사의 실제 매출·영업이익이 전년 동분기보다 좋아지고 있는지를 보는 M3Top3의 실적개선 항목이다. F02-R1에서 W1 57개사 중 5개사의 실제 공시 입력경로가 검증됐고, F05-R1에서는 57/57개사의 시장반응 F05 계산이 완료됐다. 이번 승인으로 남은 52개사의 F02를 가능한 최대 범위까지 넓혀, 더 많은 회사에서 "실적 개선 + 시장반응"을 동시에 비교하는 F02-R2 broad-coverage 실행을 허가한다.

## 1. 승인 범위

TARGET_WINDOW = W1
SNAPSHOT_CUTOFF = 2024-08-09T23:59:59+09:00
EXACT_COHORT = existing W1 INCLUDE 57
ALREADY_F02_SCOREABLE = 003160,025560,031980,036200,005290
NEW_TARGET_SET = exact W1 INCLUDE 57 minus the above 5 = 52 companies

OBJECTIVE = maximize cutoff-safe F02 coverage across the remaining 52 using the already-proven F02 semantics and official source family; do not force 52/52 if evidence is unavailable.

### Preserved F02 semantics
- model/version/scorer/weights unchanged;
- bounded F02 profile remains realized revenue + operating profit versus prior comparable same quarter;
- same quarter length and same financial-statement basis within each company;
- Q2 preferred only when a cutoff-safe admissible official Q2 source exists; otherwise Q1 fallback under the same previously approved D1 logic;
- no future statement/restatement backfill;
- no silent zero/neutral fill;
- NOT_FOUND remains retrieval/evidence state, not negative business fact;
- no PC1, F02-R1, or F05-R1 rerun.

### Allowed official source family
KRX KIND official filings/disclosures already used in F02-R1 only, including:
- filed quarterly/semiannual financial disclosure where the required 3-month comparable values are explicitly available;
- official provisional earnings/fair-disclosure source where already admissible under the R1 profile;
- no new provider, paid source, credential, budget, or unofficial substitution.

## 2. Execution design authorized

Use a census-first, batch-first pipeline rather than 52-company manual serial search.

P0 — exact target binding
- reproduce exact 52-company target set from W1 INCLUDE 57 minus the 5 existing F02 companies;
- bind exact F02-R1 and F05-R1 predecessor refs; no mutation of predecessor branches.

P1 — official-source census
- enumerate cutoff-safe Q2 candidates first, then Q1 fallback candidates only as needed;
- record candidate/publication/date/basis/source identity before raw acquisition;
- one shared deterministic census/indexing strategy preferred over repeated free-form search.

P2 — batch extraction/generalization
- reuse and generalize the proven R1 source adapter only as needed;
- extract exact revenue and operating-profit current/prior cells with issuer/date/period/basis/unit/table/header/cell lineage;
- semantic-neutral parser/generalization fixes allowed inside isolated task branch with affected revalidation.

P3 — straight-through automatic lane
- process all companies whose official source structure matches validated patterns;
- no Owner questions for routine parser/layout variants.

P4 — bounded exception lane
- only unresolved/irregular companies enter exception review;
- preserve NOT_FOUND/PARTIAL when the cap is reached or admissible evidence cannot be established;
- do not lower evidence standards merely to increase coverage.

P5 — validation
- affected independent validation on exact extracted sources/cells, period/basis, cutoff safety, missingness, denominator preservation, and model/scorer immutability;
- author cannot self-issue independent PASS;
- routine defects: checkpoint -> classify -> bounded correction -> affected revalidation -> continue, without repeat Owner approval.

P6 — create-once F02 materialization and combined view
- calculate F02 once on the validated expanded cohort;
- retain F05-R1 57/57 bytes and results without rerun;
- produce common-coverage F02+F05 view only for companies with both features and show coverage explicitly;
- do not present mixed-coverage rows as an official 57-company Top3.

P7 — report/seal/persistence
- exact source/input/validation/result/report hashes and task-branch remote persistence;
- main unchanged; no PR/merge/release/production.

## 3. Bounded ceilings

MAX_NEW_TARGET_COMPANIES = 52
MAX_SOURCE_ACTIONS_TOTAL = 520
MAX_SOURCE_ACTIONS_PER_NEW_ISSUER = 12
MAX_NEW_RAW_SOURCE_FILES = 104
MAX_NEW_RAW_SOURCE_BYTES = 160000000
MAX_RETRIES_PER_EXACT_SOURCE_OBJECT = 2

These are ceilings, not quotas. Stop early when sufficient exact evidence is obtained. Do not spend remaining quota merely because it exists.

## 4. Planned time / progress behavior

P50_WALL = 5 hours
P90_WALL = 12 hours
CONFIDENCE = LOW

EWU = 100
- target/census closure 15
- parser/generalization readiness 20
- straight-through extraction 25
- bounded exception handling 15
- independent validation 15
- score/report/persistence 10

Progress must distinguish actual completed evidence from reading/searching effort. If long-running, persist checkpoints and ETA changes; no passive spinner.

## 5. Explicitly not authorized

- F02 formula/weight/scorer/model-config change;
- F05 formula/85-point saturation change;
- F01/F03/F04/F06/F07/F08/F09 expansion;
- current-universe substitution or W1 denominator mutation;
- standalone-vs-consolidated basis substitution not already admissible under preserved R1 semantics;
- future/post-cutoff financial values or outcome/MFE/MAE access for feature construction;
- W2-W8 expansion;
- new provider, credential, paid source, or budget;
- main mutation, PR merge, release, or production.

## 6. Stop / Owner decision boundary

STOP and return one plain-language decision item only if:
- the preserved R1 F02 semantics are insufficient for a material class of companies and a new semantic rule is required;
- evidence standards or statement-basis rules must be weakened or changed;
- a new provider/credential/budget is required;
- source-action/byte/company ceilings must be expanded;
- model/PIT/eligibility/weight/scorer semantics would change;
- W2-W8/outcome/main/merge/release/production is needed.

Do NOT stop for ordinary source-layout/parser/control defects inside the approved scope.

## 7. Claim ceiling

This approval may establish expanded W1 F02 functional coverage and a provisional common-coverage F02+F05 view. It may not establish official Top3/Top10, model-performance PASS, holdout/OOS performance, release readiness, or investment recommendation.

REPEAT_OWNER_APPROVAL_WITHIN_EXACT_APPROVED_SCOPE = FALSE
