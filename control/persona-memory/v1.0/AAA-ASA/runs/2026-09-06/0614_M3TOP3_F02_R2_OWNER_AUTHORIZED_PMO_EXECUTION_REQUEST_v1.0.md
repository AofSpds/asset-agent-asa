# M3Top3 F02-R2 — Owner-authorized PMO execution request

PROJECT = AAA
PRODUCT = ASSET AGENT ASA
FROM_PERSONA = AAA-ASA (ASA)
TARGET_PERSONA = AAA-PMO-ORCHESTRATOR (PMO)
DATE_KST = 2026-09-06 06:14 KST
CLASS = OWNER_AUTHORIZED_BOUNDED_EXECUTION_REQUEST
AUTHORITY_SOT = FALSE

OWNER_APPROVAL_COMMIT = ec1843d8a7d10ce69f6b251f16234aad50778cc7
OWNER_APPROVAL_PATH = control/persona-memory/v1.0/AAA-ASA/runs/2026-09-06/0612_OWNER_APPROVAL_M3TOP3_F02_R2_BROAD_COVERAGE_v1.0.md

F02_R1_REMOTE_BRANCH = task/aaa/m3top3-f02-r1-multi-company-input-repair-20260905
F02_R1_REMOTE_HEAD_AT_LAST_ASA_READBACK = b0e4b60e6380ad12705ded8f05efce13843bbf3c
F05_R1_REMOTE_BRANCH = task/aaa/m3top3-f05-r1-w1-market-positioning-20260905
F05_R1_REMOTE_HEAD_AT_DISPATCH = 8f3253e5f4372903b5ebe5f4e1bf6e08bd288239

TASK_BRANCH_PRECREATED_FOR_EXECUTION_ISOLATION = task/aaa/m3top3-f02-r2-broad-coverage-20260906
TASK_BRANCH_BASE = F05_R1_REMOTE_BRANCH_HEAD_AT_CREATION

EXECUTION_AUTHORIZED = TRUE
MODEL_SEMANTIC_CHANGE_AUTHORIZED = FALSE
PIT_SEMANTIC_CHANGE_AUTHORIZED = FALSE
ELIGIBILITY_CHANGE_AUTHORIZED = FALSE
F05_CHANGE_AUTHORIZED = FALSE
W2_W8_AUTHORIZED = FALSE
OUTCOME_AUTHORIZED = FALSE
MAIN_PR_MERGE_RELEASE_PRODUCTION_AUTHORIZED = FALSE
NEW_PROVIDER_CREDENTIAL_BUDGET_AUTHORIZED = FALSE

## 0. 사람말 목적

F02는 회사의 실제 매출·영업이익이 전년 동분기보다 개선되는지 보는 실적개선 항목이다. 현재 W1에서 F05는 57/57이지만 F02는 5/57이다. 이번 실행은 나머지 52개 회사의 공식 KIND 공시를 census-first/batch-first 방식으로 처리해 F02를 가능한 최대 범위까지 넓히고, F02와 F05가 모두 있는 common-coverage cohort를 크게 만드는 작업이다.

목표는 52/52를 억지로 채우는 것이 아니다. cutoff-safe 공식 evidence를 확보할 수 있는 만큼만 정확히 채우고, 나머지는 NOT_FOUND/PARTIAL을 보존한다.

## 1. Mandatory bootstrap and no-rerun recovery

1. Bootstrap current AAA authority/persona state.
2. Read exact Owner approval commit/path above.
3. Read F02-R1 completion/persistence artifacts from exact remote branch; do not rerun F02-R1.
4. Read F05-R1 completion/persistence artifacts from exact remote branch; do not rerun F05-R1.
5. Verify the precreated task branch/worktree is isolated and contains no unrelated mutable work before material execution.
6. Create a fresh run ID under a versioned F02-R2 run root.
7. Single PMO writer; validators use isolated fresh contexts/journals. Do not race on shared mutable journal files.

## 2. Exact target set

W1 snapshot cutoff = 2024-08-09T23:59:59+09:00.
Exact cohort = existing W1 INCLUDE 57.
Existing F02 scoreable five = 003160, 025560, 031980, 036200, 005290.
New target set = exact W1 INCLUDE 57 minus those five = exactly 52.

Materialize `F02_R2_TARGET_SET.json` before source acquisition with:
- 52 company IDs/codes/names;
- parent W1 population identity;
- predecessor five exclusions;
- deterministic target-set hash.

Target-set mismatch => STOP before source actions.

## 3. Preserved F02 profile

Do not alter M3TOP3-v1.0, F02 formula, feature weight, axis/scorer logic, missingness, PIT, eligibility, or cutoff.

Required economic inputs under preserved R1 bounded profile:
- realized revenue;
- realized operating profit;
- current comparable quarter versus prior-year same quarter;
- 3-month comparable period;
- same financial statement basis within issuer pair;
- exact native units/signs and source cell custody.

Source recency policy:
- Q2 is preferred only if a cutoff-safe admissible official Q2 source exists within the already-used official KIND source family;
- otherwise use the bounded Q1 fallback path under the same R1 logic;
- do not claim global Q2 absence merely because the bounded census did not find one;
- do not backfill later restatements or future knowledge.

Official source family only:
- KRX KIND filed quarterly/semiannual reports where the required 3-month comparable values are explicit and admissible;
- KRX KIND official provisional earnings/fair disclosure where already admissible under the R1 profile;
- no unofficial mirror, new provider, paid source, credential, or budget.

## 4. Execution phases

### P0 — exact precheck
- authority/approval/branch/worktree/target-set/predecessor refs;
- source-action ledger starts at zero;
- freeze time/compute plan and checkpoints.

### P1 — 52-company source census
Perform a deterministic company-level census before raw-document acquisition whenever possible.
For each issuer record:
- candidate source identity;
- source type;
- publication date;
- quarter/period;
- consolidated/statement basis;
- selection reason or bounded fallback reason;
- acquisition required yes/no.

Prefer shared structured enumeration/indexing over repeated free-form search.
Do not spend actions proving an absolute absence beyond the approved bounded source set.

### P2 — parser/adapter generalization
Reuse F02-R1 proven extraction path.
Allowed modifications are semantic-neutral only:
- support additional official table/header/layout variants;
- deterministic exact-cell extraction;
- issuer/date/period/basis/unit/header/table/cell lineage;
- fail closed on ambiguous or conflicting tables.

No fuzzy numeric fingerprint alone may admit a cell.
No company-to-company value transplant.
No later-value inference.

### P3 — straight-through automatic batch lane
Process all issuers matching validated patterns without per-company Owner interaction.
Capture per-company extraction receipt and source hash.

### P4 — bounded exception lane
Only unresolved issuers enter this lane.
Use remaining approved source actions selectively.
Routine HTML/layout/parser defects are implementation defects, not Owner decisions.
Correct -> affected revalidate -> continue.
When admissible evidence still cannot be established within ceilings, preserve PARTIAL/NOT_FOUND and continue other issuers.

### P5 — exact affected validation
Required axes:
- exact issuer/source/date/quarter/basis binding;
- exact revenue/OP current/prior cells and signs/units;
- cutoff/publication safety;
- no future/backfilled restatement;
- no missing=zero substitution;
- no predecessor F02/F05 mutation;
- no target denominator mutation;
- parser mutation negatives;
- deterministic rerun of extraction transform on frozen bytes where needed without reacquiring sources.

Independent validation floor follows current risk classification. Author cannot self-certify independent PASS.
Routine failed validation inside unchanged Owner semantics can be corrected and revalidated without repeat approval.

### P6 — create-once F02 R2 materialization
After validation gate PASS:
- calculate expanded F02 once on the validated common snapshot cohort;
- do not rerun F05-R1;
- bind existing F05-R1 values by exact hash/ref;
- produce coverage matrix across all 57;
- produce F02+F05 common-coverage view only where both features are available;
- keep heterogeneous-coverage rows clearly separated from any comparable common-coverage ranking.

Do not emit official Top3/Top10.

### P7 — closure
Persist:
- target set;
- source census;
- raw custody/source manifest;
- mappings/extraction receipts;
- exception ledger;
- affected validation receipts/report;
- expanded F02 inputs/scores;
- 57-company coverage matrix;
- F02+F05 common-coverage provisional view;
- process/checkpoint/progress ledgers;
- completion report;
- exact bundle/seal/persistence readback.

Push only the exact task branch. Main stays unchanged. No PR/merge/release/production.

## 5. Ceilings

MAX_NEW_TARGET_COMPANIES = 52
MAX_SOURCE_ACTIONS_TOTAL = 520
MAX_SOURCE_ACTIONS_PER_NEW_ISSUER = 12
MAX_NEW_RAW_SOURCE_FILES = 104
MAX_NEW_RAW_SOURCE_BYTES = 160000000
MAX_RETRIES_PER_EXACT_SOURCE_OBJECT = 2

Ceilings are maximums, not quotas. Stop spending when exact evidence is sufficient. No quota-burning.

## 6. Progress/time plan

P50_WALL = 5h
P90_WALL = 12h
CONFIDENCE = LOW

EWU = 100
- P0/P1 target+census = 15
- P2 parser/generalization = 20
- P3 straight-through extraction = 25
- P4 exception lane = 15
- P5 validation = 15
- P6/P7 score+report+persistence = 10

Persist checkpoints before long validation/exception stages. Report actual progress, wait/rework, and ETA changes when measurable. Missing telemetry remains NOT_INSTRUMENTED; do not fabricate efficiency claims.

## 7. Stop boundaries

STOP / OWNER ACTION REQUIRED only if one of these becomes necessary:
- new F02 economic meaning/formula/weight/scorer rule;
- new statement-basis substitution not already admissible under preserved R1 semantics;
- weaker evidence standard;
- new provider/paid source/credential/budget;
- expansion beyond 52 target companies or action/file/byte ceilings;
- PIT/eligibility/universe/denominator semantics change;
- F05 model/saturation change;
- W2-W8 or outcome/MFE/MAE access;
- main/PR merge/release/production.

Do not stop for routine source-layout/parser/control defects inside these boundaries. No redundant Owner approval questions.

## 8. Required Owner-facing completion order

Completion report starts with:
1. F02가 무엇인지 한 문단;
2. F02 coverage가 5/57에서 몇/57로 늘었는지;
3. 몇 개가 자동 처리 / 예외 처리 / 미확정인지;
4. F02+F05 common-coverage 상위 잠정 결과;
5. 무엇을 의미하고 무엇을 의미하지 않는지;
6. 주요 실패/누락 이유;
7. only then technical refs/hashes/validation details.

## 9. Terminal states

- COMPLETE_F02_R2_BROAD_COVERAGE_PROVISIONAL
- COMPLETE_F02_R2_BOUNDED_PARTIAL_COVERAGE
- BLOCKED_EXACT_OWNER_DECISION_REQUIRED

Claim ceiling: bounded W1 expanded F02 functional coverage and provisional common-coverage F02+F05 analysis only. No official Top3, no model-performance PASS, no holdout/OOS claim, no release or investment recommendation.

REPEAT_OWNER_APPROVAL_WITHIN_EXACT_APPROVED_SCOPE = FALSE
