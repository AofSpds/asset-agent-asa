# AAA Multi-Model Operating Rule v0.1

PROJECT = AAA
PRODUCT = ASSET AGENT ASA
ARTIFACT = AAA_MULTI_MODEL_OPERATING_RULE_v0.1
STATE = OWNER_APPROVED_CANDIDATE / NOT_ACTIVE_VALIDATION_AUTHORITY_UNTIL_VALIDATED_AND_MERGED
OWNER_DIRECTION_DATE_KST = 2026-09-01
AUTHORING_PERSONA = AAA-PMO-ORCHESTRATOR

## 1. Purpose

Define a bounded operating split for ChatGPT, Claude, and Gemini inside AAA without creating model-vendor authority, majority-vote governance, or a new validation tier.

This rule is an execution-routing policy. It does not alter Shared Contract semantics, model/PIT/evidence semantics, Freeze/Release/Production authority, or the formal AAA Persona hierarchy.

## 2. Formal authority rule

Model identity != Persona authority.

- ChatGPT, Claude, and Gemini are runtime/model providers, not AAA authority objects.
- A model may act under a resolved AAA Persona only when the governed task assigns that Persona and the normal AAA bootstrap/authority chain is recovered.
- `AAA-VALIDATION-AUDITOR (IVA)` remains the formal independent-validation Persona. Claude being the preferred external runtime for IVA work does not itself create an Independent Validation PASS.
- Independent Validation PASS still requires an exact governed IVA receipt or pre-authorized deterministic import under existing AAA rules.
- No model may self-expand Owner authority, validation floor, custody scope, provider/quota scope, release authority, or production authority.

## 3. Default runtime role split

### 3.1 ChatGPT — PMO / Executor / Integrator

DEFAULT_RUNTIME_ROLE = PRIMARY_EXECUTION_ORCHESTRATION

Preferred work:
- Git-governed current-state recovery and reconciliation.
- Owner-direction translation into bounded execution plans.
- Branch/workflow/issue/control-plane orchestration.
- Exact evidence integration across task, Git, issues, workflows, and receipts.
- Remediation sequencing and successor-generation control.
- Final owner-facing synthesis of validator/scout findings against governed evidence.

Restrictions:
- ChatGPT must not grant Independent Validation PASS to its own authored or executed material.
- Self-consistency review is not IVA.
- For material P0/P1 changes, existing paired-validator / IVA / Owner boundaries remain unchanged.

### 3.2 Claude — Independent Validator / Red Team default

DEFAULT_RUNTIME_ROLE = PREFERRED_INDEPENDENT_VALIDATION_RUNTIME

Preferred work:
- Frozen-SHA independent audit.
- Authority-chain reconciliation.
- Semantic contradiction and stale-reference detection.
- Claim-ceiling enforcement.
- Unsupported-transition / false-PASS detection.
- Exact lineage, effect, prohibition, gate, and do-not-rerun verification.
- Adversarial review that separates DEFECT / RISK / IMPROVEMENT / PREFERENCE.

Restrictions:
- Default strict read-only operation.
- No file edits, commits, pushes, workflow dispatch, provider/API invocation, AWS/S3/IAM mutation, or production action during independent audit unless a separately governed task explicitly authorizes it.
- Claude findings are evidence inputs. Formal IVA state still requires the governed AAA validation act/receipt.

### 3.3 Gemini — Explorer / Alternative Analyst / Consistency Scout

DEFAULT_RUNTIME_ROLE = NON_AUTHORITATIVE_EXPLORATION_AND_SCOUTING

Preferred work:
- Broad repository scanning and recall-oriented exploration.
- Candidate finding generation.
- Repeated-pattern, stale-reference, duplication, and architecture-smell search.
- Mechanical cross-checks of SHA/lineage/bounds/effect counts.
- Alternative architecture / design-option generation.
- Bottleneck hypothesis and search-space expansion.
- Third-opinion analysis before material review.

Restrictions:
- Gemini output is `HYPOTHESIS / CANDIDATE_FINDING` by default unless separately elevated through governed validation evidence.
- Gemini must not be used as the sole final PASS/FAIL authority for material P0/P1 decisions under the current calibration.
- Gemini must not convert local consistency into global authority consistency without tracing higher authority.

## 4. Multi-model workflow

Default material-work sequence:

1. ChatGPT/PMO recovers exact current authority and executes or prepares the bounded target.
2. Freeze exact target SHA/tree and relevant evidence set.
3. Gemini may perform broad non-authoritative scout/explorer analysis and return candidate findings.
4. Claude performs independent adversarial validation on the frozen target, preferably without seeing prior model conclusions when blind testing is feasible.
5. ChatGPT/PMO reconciles Claude/Gemini outputs against exact Git evidence, deterministic invariants, Owner authority, and task-local receipts.
6. Existing AAA gate/validator/Owner rules determine the actual disposition.

For high-value audits, Gemini and Claude should use separate detached worktrees or otherwise isolated read-only snapshots of the same exact SHA.

## 5. No model voting

PROHIBITED_DECISION_RULE = MAJORITY_MODEL_VOTE

The following is invalid:
`2 of 3 models said PASS -> PASS`.

Priority remains:

`governed Owner/Project authority + exact Git/evidence + deterministic invariants/tests > model opinion`.

Model disagreement is a trigger for evidence reconciliation, not a vote.

## 6. Blind-test and contamination discipline

When comparing model capability:
- Same frozen SHA/tree.
- Same audit scope and prompt where possible.
- Separate fresh sessions for blind comparisons.
- No prior correction answer, other model conclusion, or hidden expected finding should be supplied before the blind result.
- Validator/scout workspaces remain isolated from the live execution workspace.
- Read-only tools are preferred; mutation requires a separately governed task.

## 7. Current empirical calibration evidence

CALIBRATION_TARGET_HEAD = `f243ca44938919ce19c3e4c4f53cdbfb76867eed`
CALIBRATION_TARGET_TREE = `ef24f950209fc4c198957ca218b75a4db0f446f7`
TARGET = G10 issuer-group exclusion enumeration S2 LIVE terminal checkpoint.

Observed benchmark result from the 2026-09-01 blind audit exercise:

### Claude
- Recovered the S2 terminal state on first context-recovery attempt.
- In blind adversarial audit, independently detected the stale semantic field `EXCLUDE_REFERENCED_TWO_COMPANIES_AND_CONTINUE` and reconciled it against the governing Owner Decision Receipt v1.1, which had already corrected the target to one logical issuer group.
- Maintained a materially stronger uncertainty/claim-ceiling distinction between Git integrity and independent reproduction of the underlying raw enumeration result.
- One authority-source risk was severity-overstated; therefore Claude is preferred, not infallible.

### Gemini
- Performed strong mechanical SHA/lineage/bounds/effect consistency checking.
- Missed the higher-authority semantic contradiction above and positively described the stale `two companies` wording as consistent.
- Reported `UNCERTAINTIES = None` without tracing the governing Owner Decision Receipt v1.1 in that blind pass.
- Proposed an S3-mutation-oriented next step beyond what the audited evidence alone safely authorized.

CALIBRATION_DISPOSITION =
- Claude: preferred external runtime for independent validation / Red Team.
- Gemini: retained as explorer, broad scout, mechanical consistency checker, and alternative-analysis runtime.
- ChatGPT: primary PMO/execution/integration runtime.

This calibration is empirical and reversible. It is not a permanent claim that one vendor/model is universally superior. Future benchmark evidence on materially different AAA workloads may update the routing default through a governed successor revision.

## 8. Finding taxonomy and handoff

External model findings should be normalized before integration:
- `DEFECT`: proven contradiction / invalid transition / violated invariant / incorrect claim / evidence mismatch.
- `RISK`: evidence-backed concrete failure mode or ambiguity, not merely a hypothetical concern.
- `IMPROVEMENT`: valid current state with a bounded robustness/clarity/maintainability gain.
- `PREFERENCE`: alternative style/design without demonstrated control or correctness advantage.

Material findings must bind to exact evidence wherever available.

Gemini candidate findings should normally be promoted to material findings only after exact evidence reconciliation by PMO and, where required, Claude/IVA or the applicable paired validator.

## 9. Security and side-effect defaults

- Validator and scout runtimes default to read-only.
- Do not expose project secrets or credentials merely to improve model context.
- No external model receives authority to invoke provider quota, AWS/S3/IAM mutation, release, or production actions by virtue of this rule.
- Remote-control/UI convenience features do not change the underlying permission model or AAA authority.

## 10. Activation / change control

This v0.1 records the Owner-approved routing direction and current calibration.

Before treating it as an active project-wide validation rule:
- exact candidate diff must be reviewed against existing Project Instructions and validation architecture;
- no conflict may be introduced with formal Persona authority or existing validator tiers;
- material validation-routing semantics must receive applicable validation under the current AAA framework;
- merge/currentization must be explicit.

Until then it is a persisted Owner-approved candidate and continuity artifact, not a substitute for active Project Instructions or Shared Contract.
