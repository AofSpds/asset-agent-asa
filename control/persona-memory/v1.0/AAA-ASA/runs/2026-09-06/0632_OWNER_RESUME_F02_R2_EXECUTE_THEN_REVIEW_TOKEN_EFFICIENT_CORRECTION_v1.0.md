# OWNER RESUME — F02-R2 Execute-Then-Review / Token-Efficient Correction

PROJECT = AAA
PRODUCT = ASSET AGENT ASA
PERSONA = AAA-ASA (ASA)
DATE_KST = 2026-09-06 06:32 KST
CLASS = OWNER_DIRECTION / EXECUTION_SEQUENCE_CORRECTION / TOKEN_EFFICIENCY_CONTROL
AUTHORITY_SOT = FALSE

OWNER_DECISION = RESUME
OWNER_TEXT = "네 재개 하세요. 이대로 50여개 회사를 진행하면 토큰 올인나요 ㅋㅋ"

## 0. 사람말 요약

Owner는 F02-R2 재개를 승인한다. 다만 이전 F05-R1에서 기능 계산 전 다중 사전검증과 계산 후 재검증이 겹쳐 wall time과 LLM/validation overhead가 과도하게 커진 점을 correction으로 반영한다.

F02-R2는 기존 Owner Item 22의 `CONTINUE_EXECUTION + RECORD_FINDING + POST_EXECUTION_REVIEW` 원칙으로 복귀한다. 최소 안전 precheck만 통과하면 52개 census/추출/잠정 F02 생성까지 먼저 실행하고, 그 candidate bundle을 고정한 뒤 통합 사후검증한다.

검증 수준을 약화시키는 것이 아니라 검증 시점과 단위를 바꾼다: 반복적인 회사별/역할별 원문 재독 대신 전수 자동 invariant + 예외/고위험 대상 affected independent review를 사용한다.

## 1. Superseded sequencing only

The prior execution request `0614_M3TOP3_F02_R2_OWNER_AUTHORIZED_PMO_EXECUTION_REQUEST_v1.0.md` remains authoritative for target, source family, ceilings, semantics, PIT, no-rerun, no-main/merge/release boundaries, except the following sequencing is superseded:

OLD = source/extraction -> independent validation gate -> score/materialization -> further review
NEW = minimal safety precheck -> census/extraction -> provisional candidate materialization -> one consolidated post-execution validation -> affected-only correction/revalidation -> closure

No model/F02/F05 semantic change is created by this correction.

## 2. Minimal pre-execution gate only

Before material work, check only:
1. exact target = remaining W1 52 companies;
2. cutoff = 2024-08-09T23:59:59+09:00;
3. allowed source family = existing official KRX KIND family only;
4. isolated task branch/worktree; no main/predecessor mutation;
5. no future/outcome/provider/budget expansion.

Do not perform full CTLV/MODV/ENGV/IVA pre-score validation merely to open the execution gate.

STOP at precheck only for wrong target/cutoff/source/branch or an Owner-reserved boundary. Ordinary parser/layout/control findings are recorded and execution continues where unaffected.

## 3. Execution-first candidate pipeline

A. 52-company deterministic census first.
B. Batch acquisition/extraction using the proven F02-R1 path.
C. Straight-through automatic lane for matched layouts.
D. Time-boxed exception lane for irregular issuers; do not hold the full cohort for one issuer.
E. Materialize provisional expanded F02 candidate once from admissible extracted evidence.
F. Bind existing F05-R1 result bytes by exact hash/ref without rerun.
G. Freeze candidate bundle before independent review.

If an issuer remains unresolved within bounded time/actions, preserve PARTIAL/NOT_FOUND and continue. Do not weaken evidence standards to force coverage.

## 4. Token-efficient operating rules

TOKEN_COST_EXACT = NOT_INSTRUMENTED; no fabricated token count or savings claim.

Operational controls:
- Fetch/save each official raw source once where possible; reuse frozen local bytes and hashes.
- Do not repeatedly inject full multi-hundred-KB/MB HTML documents into LLM contexts.
- Parse/index locally/deterministically first; pass exact table/header/cell slices plus source identity to LLM/validator when sufficient.
- Company-level normal cases produce compact JSONL/CSV evidence rows, not long narrative reports.
- LLM deep review is reserved for ambiguous layouts, conflicting tables, cutoff/basis ambiguity, or post-validation exceptions.
- Validators do not independently rediscover all 52 sources. They inspect the frozen candidate, deterministic invariant results, sampled/exception evidence, and exact affected slices.
- No validator-of-validator narrative loop.
- No repeated full-bundle readback unless an exact integrity or semantic conflict requires it.
- Git writer remains single PMO root; parallel read-only acquisition/extraction lanes may be used if available.

## 5. Post-execution validation design

After provisional candidate freeze:

### Automatic full-cohort invariants
Run deterministic checks across every admitted company:
- issuer/code/source identity;
- publication date <= cutoff;
- quarter/period length and current/prior comparability;
- same statement basis within issuer pair;
- revenue/operating-profit row and unit/sign parse;
- missing is not zero;
- no future/backfilled source;
- no predecessor F02/F05 mutation;
- deterministic score transform and coverage accounting.

### Independent review
Use the current required independence floor, but concentrate it on:
- parser/adapter behavior as a system;
- exception/high-risk issuer set;
- deterministic sample of straight-through rows sufficient to detect systemic layout errors;
- any automatic invariant failure.

Do not require each independent role to reread every normal issuer from scratch.

### Findings
DEFAULT = CONTINUE_EXECUTION + RECORD_FINDING + POST_EXECUTION_REVIEW.
If a finding affects a subset, correct/revalidate only the affected parser class/company set.
Do not restart 52-company extraction or full validation.

## 6. Timebox / anti-runaway rule

TARGET_P50_WALL = approximately 2 hours
TARGET_CONSERVATIVE_WALL = approximately 3 to 3.5 hours
These are planning targets, not guaranteed percentiles.

At about 2h: prioritize freezing the best admissible provisional candidate instead of perfecting low-yield exceptions.
At about 3h: unresolved issuer exceptions should normally close as PARTIAL/NOT_FOUND and move to consolidated review/closure unless a systemic defect affects broad coverage.

Do not extend toward the prior 5h/12h plan merely to chase marginal issuer coverage.

Track separately when measurable:
- SOURCE/CENSUS time
- EXTRACTION time
- EXCEPTION time
- VALIDATION time
- report/persistence time
- LLM/validator invocation count or equivalent observable call count
- number of issuers requiring deep exception review
- affected revalidation count

Unknown telemetry remains NOT_INSTRUMENTED.

## 7. Owner interaction

REPEAT_OWNER_APPROVAL_WITHIN_EXACT_APPROVED_SCOPE = FALSE

Do not ask Owner routine questions for source layout, parser fixes, exception triage, checkpoint continuation, or affected revalidation.
Escalate only if proceeding requires a new semantic rule, weaker evidence standard, provider/budget/credential expansion, scope/ceiling expansion, PIT/model/eligibility change, W2-W8/outcome access, or main/merge/release/production action.

## 8. Current resume checkpoint

At Owner stop/readback, remote execution branch `task/aaa/m3top3-f02-r2-broad-coverage-20260906` still pointed to F05-R1 terminal commit `8f3253e5f4372903b5ebe5f4e1bf6e08bd288239`; no remote F02-R2 material commit had been observed. Local unpushed state, if any, must be inspected and reused rather than discarded or rerun.

RESUME_DISPOSITION = AUTHORIZED_UNDER_THIS_CORRECTED_SEQUENCE
