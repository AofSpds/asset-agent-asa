# M3Top3 F05-R1 — Owner-authorized PMO execution request

PROJECT = AAA
PRODUCT = ASSET AGENT ASA
FROM_PERSONA = AAA-ASA (ASA)
TARGET_PERSONA = AAA-PMO-ORCHESTRATOR (PMO)
DATE_KST = 2026-09-05 22:56 KST
CLASS = OWNER_AUTHORIZED_BOUNDED_EXECUTION_REQUEST
AUTHORITY_SOT = FALSE

OWNER_POLICY_APPROVAL_COMMIT = 709ded3f4440142c05a97dcc03b286ad49fa149b
OWNER_POLICY_APPROVAL_PATH = control/persona-memory/v1.0/AAA-ASA/runs/2026-09-05/2254_OWNER_APPROVAL_F05_MARKET_RECOGNITION_POLICY_AND_CONDITIONAL_R1_EXECUTION_v1.0.md

F05_R0_BRANCH = task/aaa/m3top3-f05-r0-readiness-20260905
F05_R0_REMOTE_HEAD = 87a5025f7e126eb66f8864ae8b106f6c5c65aba4
F05_R0_TERMINAL = PARTIAL_DECISION_REQUIRED

EXECUTION_AUTHORIZED = TRUE_WITH_PRECHECK
MODEL_WEIGHT_CHANGE_AUTHORIZED = FALSE
DOWNSTREAM_F05_SCORER_CHANGE_AUTHORIZED = FALSE
PIT_CHANGE_AUTHORIZED = FALSE
ELIGIBILITY_CHANGE_AUTHORIZED = FALSE
W2_W8_EXPANSION_AUTHORIZED = FALSE
OUTCOME_EXECUTION_AUTHORIZED = FALSE
MAIN_MERGE_RELEASE_PRODUCTION_AUTHORIZED = FALSE
NEW_PROVIDER_CREDENTIAL_BUDGET_AUTHORIZED = FALSE

## 0. 사람말 목적

F05는 "좋은 변화가 시장에 반영되기 시작했는지, 이미 너무 과열됐는지"를 보는 시장반응 항목이다.
R0에서 57개사 원자료는 모두 준비된 것이 확인됐다. 이번 R1은 Owner가 승인한 계산정책을 exact contract/code/input으로 결합하고, GST·엑시콘 기업행위 경계를 공식근거로 닫은 뒤, 검증이 통과하면 W1 57개사의 실제 F05를 계산하는 작업이다.

## 1. Mandatory start

1. Bootstrap current AAA authority/persona state.
2. Recover exact Owner approval commit/path above.
3. Read F05-R0 report and D1-D6 recovery artifacts from R0 branch.
4. Create fresh isolated task branch/worktree and fresh run ID.
5. Do not mutate or rerun F05-R0.
6. Bind a single writer PMO root journal and unique validator journals.

Recommended branch name:
`task/aaa/m3top3-f05-r1-w1-market-positioning-20260905`

## 2. Approved semantic profile to bind exactly

### D1/D2 — 20d/60d market-price return
- trading-session horizons, not calendar days;
- end at W1 cutoff 2024-08-09;
- 20 and 60 daily return intervals respectively;
- use KRX corporate-action-reference-aware daily market-price change semantics from the bound source;
- do not cross a CA boundary using naive raw-close ratio;
- cash-dividend reinvestment is not part of F05;
- no invented adjustment factor.

Implementation must make explicit:
- exact source field(s), units, scaling, missing-value rule;
- exact compounding/arithmetic;
- endpoint/inclusivity;
- source lineage for each company/horizon.

### D4 — turnover acceleration
- daily turnover = Volume / Stocks;
- acceleration = recent-20-session mean turnover / immediately-prior-20-session mean turnover - 1;
- no silent fill for zero/missing/suspended/CA boundary.

### D3/D6 — equal-weight benchmark
- exact W1 INCLUDE 57 only;
- simple equal-weight mean of admissible company returns for each horizon;
- generate benchmark only if 57/57 are admissible for the horizon in this W1 run;
- no silent denominator shrink;
- EXCLUDE_PROVEN and EXCLUDE_UNRESOLVED excluded.

### CA
- official evidence only;
- GST and 엑시콘 exact W1 boundaries must be adjudicated before scoring;
- heuristic trigger is not CA truth;
- no post-cutoff outcome-aware rewriting.

## 3. Precheck gates before any F05 score

P0 authority/identity gate:
- exact Owner approval readable;
- R0 refs readable;
- main observed but not adopted as mutable target;
- isolated branch/worktree verified.

P1 model/control binding gate:
- MOD binds approved semantics without changing downstream F05 transform/weight;
- CTL binds source fields, CA evidence, PIT cutoff, lineage, denominator rule;
- if binding requires any semantic deviation, STOP with one plain-language decision item.

P2 engineering gate:
- expose already-present required raw fields through adapter only as needed;
- semantic-neutral field exposure only;
- exact source schema and units validated;
- no provider/source expansion.

P3 CA gate:
- GST and 엑시콘 official issuer/KRX evidence read and bound;
- exact affected dates/events and reference-price/share-count implications recorded;
- if evidence conflicts or does not support approved market-price-return construction, STOP.

P4 affected validation gate:
minimum negative cases:
- naive raw-close use across CA boundary rejected;
- wrong issuer/date/source field rejected;
- future/post-cutoff price rejected;
- denominator 56/57 rejected;
- missing or zero Stocks/Volume handling rejected;
- duplicate/misaligned trading-session endpoints rejected;
- cash-dividend total-return substitution rejected;
- invented CA factor rejected;
- F05 weight/scorer mutation rejected.

Required positive cases:
- ordinary non-CA issuer 20d/60d return;
- GST CA-boundary case;
- 엑시콘 share-count/CA-boundary case;
- turnover acceleration exact arithmetic;
- 57-member equal-weight benchmark identity.

Required independent validation floor must follow current risk classification; author cannot self-issue independent PASS.

## 4. Conditional auto-continue to F05 computation

IF P0-P4 PASS with no semantic deviation:
- continue without repeat Owner approval to the bounded W1 F05 calculation.

Compute for exact W1 INCLUDE 57:
- trailing_20d_market_price_return
- universe_20d_equal_weight_return
- trailing_60d_market_price_return
- universe_60d_equal_weight_return
- turnover_acceleration
- existing F05 downstream transform only
- F05 score
- F05-only provisional rank

Optional valuation/diffusion inputs:
- do not invent or newly acquire them in this run;
- absent optional components simply do not add optional saturation penalty under existing semantics.

## 5. F02 + F05 view

For the existing five F02-scoreable companies only, produce a separate provisional multi-feature view showing:
- F02
- F05
- available model-weight coverage
- provisional combined score under unchanged scorer semantics
- explicit limitation that 52 other companies may have only F05.

Do not label this official Top3/Top10.

## 6. Required outputs

1. `F05_R1_POLICY_BINDING.json`
2. `F05_R1_CA_ADJUDICATION_REPORT.md`
3. `F05_R1_SOURCE_FIELD_BINDING.json`
4. `F05_R1_ADAPTER_CHANGE_REPORT.md` if code change occurs
5. `F05_R1_AFFECTED_VALIDATION_REPORT.md/json`
6. `F05_R1_W1_INPUTS.jsonl`
7. `F05_R1_W1_SCORES.jsonl`
8. `F05_R1_W1_PROVISIONAL_RANKING.csv`
9. `F02_F05_PROVISIONAL_MULTI_FEATURE_VIEW.csv`
10. `F05_R1_PROCESS_ACTION_LEDGER.jsonl`
11. `F05_R1_CHECKPOINTS.jsonl`
12. `F05_R1_COMPLETION_REPORT.md`
13. exact bundle/seal/persistence/readback artifacts

Completion report must start in Owner-friendly order:
- what F05 is;
- how many of 57 were actually calculable;
- any CA exclusions/blockers;
- top provisional F05 names/scores;
- what the result does and does not mean;
- only then technical refs.

## 7. Stop boundaries

STOP / OWNER ACTION REQUIRED if:
- approved policy must change;
- 57/57 benchmark condition fails;
- GST/엑시콘 cannot be evidence-closed;
- new provider/paid source/credential/budget required;
- CA factor must be inferred;
- adapter change is semantic rather than field exposure;
- validation floor must be reduced;
- W2-W8/outcome/main/merge/release/production is needed.

Routine implementation/control defects inside the approved scope:
terminal checkpoint -> exact impact classification -> bounded correction -> affected revalidation -> continue. No repeat Owner approval.

## 8. Claim ceiling

This run may establish a bounded W1 F05 functional result and provisional cross-sectional ranking.
It may NOT establish official Top3/Top10, M3Top3 performance PASS, holdout/OOS performance, release readiness, or investment recommendation.

NEXT_TERMINAL = COMPLETE_F05_R1_W1_PROVISIONAL | COMPLETE_PARTIAL_F05_R1 | BLOCKED_EXACT_DECISION_REQUIRED
