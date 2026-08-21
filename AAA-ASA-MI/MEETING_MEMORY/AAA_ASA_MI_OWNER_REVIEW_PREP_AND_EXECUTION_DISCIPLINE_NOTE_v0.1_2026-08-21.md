# AAA-ASA-MI Owner Review Prep & Execution Discipline Note v0.1

DATE = 2026-08-21 KST
PROJECT = AAA
PRODUCT = ASSET AGENT ASA
WORKSTREAM = AAA-ASA-MI
STATE = PERSISTED_ISOLATED_MEMO_BRANCH / NOT_YET_MERGED_TO_MAIN
PURPOSE = Preserve recent Owner directions and review-process corrections without interfering with the currently running Work execution.

## 1. Owner directions to preserve

1. Confirmation-bias control is mandatory.
   - Do not make the current ASA-MI vocabulary, assumptions, or internal framing the default truth.
   - Prefer general, neutral research language first; project-specific terminology may be mapped secondarily.
   - Distinguish evidence, hypothesis, interpretation, open question, and unsupported inference.

2. A review must not stop at describing the current state.
   - If a review identifies deficiencies, convert them into an explicit reinforcement plan.
   - The plan should state what must be corrected, in what order, and what evidence will show the correction worked.

3. Work should proceed step-by-step for Owner interaction.
   - Do not make the Owner answer many review questions at once.
   - Ask one bounded review question at a time when Owner input is actually needed.
   - Routine research execution should proceed autonomously within scope.

4. Important discussion should be written down promptly.
   - Chat context is not a durable project source of truth.
   - Persist important state, decisions, and execution/review rules in Git-backed project artifacts.

5. Quality-first execution remains preferred.
   - Additional compute/time is desirable when it increases research quality, alternative-hypothesis coverage, source checking, calibration quality, replication, or evaluator independence.
   - Longer runtime is not itself a goal.

## 2. Current reinforcement direction

The current reinforcement cycle has been structured around the following sequence:

1. Research basis / problem structure clarification
2. Owner intent vs research interpretation provenance separation
3. Concept and assumption mapping without treating the map as a fixed ontology
4. Current Six exact scope / coverage audit with evidence-state separation
5. Evaluation framework correction
6. Calibration controls and negative controls
7. Small Track A / Track B pilot with Track B pre-reveal freeze
8. Replicated evaluation and disagreement analysis
9. Model competition plus separate theory-contribution extraction
10. Post-result decision routing before any larger-cohort authorization

This sequence is a research plan, not a frozen scientific conclusion.

## 3. Post-result review order

When the current Work execution completes, review in this order:

A. EXECUTION INTEGRITY
- exact repository/head/targets
- artifacts actually created
- persistence evidence
- no unsupported reconstruction of missing source evidence

B. METHOD INTEGRITY
- calibration result
- negative-control detection
- Track B pre-reveal integrity
- evaluator independence and disagreement
- no ontology/vocabulary mimic reward

C. RESEARCH FINDINGS
- what became weaker
- what gained evidence
- what appeared independently
- what remains unknown
- useful theory contributions from both strong and weak whole-model candidates

D. NEXT DECISION
- method repair
- research-basis repair
- targeted replication
- second pilot
- larger-cohort review
- Owner decision if purpose/P0/material semantics are implicated

Do not select the next path merely because the result is interesting or agrees with current expectations.

## 4. Owner pre-review preparation

Before reading the final research result, the Owner may record a short pre-review note covering, one question at a time:

- What discovery would make this research cycle clearly worthwhile?
- What result would weaken an important current assumption?
- What would make the result scientifically untrustworthy even if it looks attractive?
- Which purpose must remain preserved even if the explanatory model changes substantially?
- Which questions should remain deliberately open?

No Owner answer to these questions is recorded yet in this artifact. Do not infer or fill them.

## 5. Concurrency / persistence note

A main Work execution is currently in progress. To avoid colliding with its repository writes, this memo is intentionally persisted on an isolated Git branch rather than written directly to main.

ISOLATED_BRANCH = asa-mi-owner-memo-20260821-1449
MAIN_MERGE_STATE = NOT_YET_MERGED

After the running Work finishes, reconcile this memo against any newer main artifacts and then merge/register it through the normal project persistence flow if still applicable.

## 6. Non-claims

This note does NOT:
- approve or freeze a worldview/model,
- authorize the 48-position cohort,
- claim Independent Validation PASS,
- reinterpret any explicit Owner statement beyond the directions above,
- treat the current reinforcement plan as permanent.

## 7. Owner-reported live Work progress snapshot — 2026-08-21 14:55 KST

SOURCE_TYPE = OWNER-PROVIDED WORK-UI SCREENSHOT
VERIFICATION_STATE = UI_OBSERVATION_ONLY / FINAL_ARTIFACTS_NOT_YET_REVIEWED

Observed items from the screenshot:

- Track B pre-reveal step shown as completed.
- Calibration v0.1 reportedly matched 7 controls, but a borderline case produced divergent judgment; this was recorded as a pre-registered failure rather than hidden.
- Evaluation framework/calibration was revised to v0.2 by adding a more operational boundary and a common classifier.
- Two blind evaluators reportedly reproduced the same final classifications under v0.2:
  - 2 structurally positive cases passed,
  - 1 genuine borderline case remained uncertain,
  - 5 negative cases failed.
- Removing terminology did not reportedly improve outcomes, which is relevant to vocabulary/ontology-bias checking.
- Independent comparison of the eight candidates has started.
- Candidate files/hashes were reportedly frozen before the final held-out set/key was used.
- Two independent evaluators are reviewing blinded documents without Track labels.
- Theory extraction is shown as completed and is being kept separate from evaluation scores.

Interpretation discipline:
- These are progress observations, not accepted scientific findings.
- Final claims require artifact/commit/evidence review after Work completion.
- Calibration v0.1's borderline divergence should remain visible in later method review even if v0.2 succeeds.

## 8. Live execution roadmap and parallel Owner/ASA preparation

### Main Work roadmap

| Phase | Purpose | Expected effort | Live status as of 14:55 KST |
|---|---|---:|---|
| 0. Exact state/source check | Fix exact inputs, repository state, source gaps | 5–10 min | Appears completed earlier |
| 1. Research basis reinforcement | Separate purpose/problem/assumptions/provenance | 15–25 min | Appears substantially progressed/completed |
| 2. Current Six scope audit | Distinguish demonstrated, untested, unknown | 10–20 min | Appears substantially progressed |
| 3. Evaluation framework correction | Separate qualification, model fidelity, expressiveness, purpose fit, theory contribution | 10–20 min | v0.2 correction shown completed |
| 4. Calibration + test suite | Test evaluator against positive/negative/borderline/mimic/overfit cases | 10–20 min | v0.1 failure recorded; v0.2 repeated blind classification shown completed |
| 4R. Calibration repair if needed | Repair evaluator after calibration failure | +15–30 min | One repair cycle appears already executed |
| 5. 8-position research pilot | Generate/freeze diverse A/B candidates | 20–40 min | Candidate freeze appears completed; independent comparison started |
| 6. Replicated evaluation + theory extraction | Measure evaluator disagreement and recover theory separately | 20–35 min | In progress; theory extraction shown completed, blind evaluation ongoing |
| 7. Synthesis + persistence | Separate source/result/interpretation and route next decision | 10–20 min | Not yet evidenced complete |

Current coarse estimate from screenshot only:
- Main research generation/freeze appears mostly complete.
- Remaining critical work is replicated/blind evaluation, disagreement analysis, final synthesis, and persistence verification.
- Do not assign a precise percent-complete until final task graph/artifacts are available.

### Owner/ASA parallel preparation roadmap

| Step | Purpose | Expected effort | Status |
|---|---|---:|---|
| O1. Reconstruct protocol's pre-registered expectations | Prevent post-result goal shifting | 5 min | Completed |
| O2. Record Owner's own pre-result expectations | Separate Owner intuition from protocol criteria | 10–15 min | Completed for current cycle; preserve as subjective expectation, not scientific threshold |
| O3. Record falsification / distrust conditions | Define what would weaken current assumptions or invalidate attractive results | 10 min | Not started |
| O4. Freeze method-verdict rules | Predefine METHOD_REPAIR / SUPPORTED_WITH_LIMITATIONS / SUPPORTED_FOR_NEXT_STAGE | 10 min | Drafted conceptually, not yet Owner-reviewed |
| O5. Result Intake Gate | Check execution integrity before reading exciting conclusions | ASA-prepared | Conceptually prepared |
| O6. Independent validation / replication routing | Launch exact-target review immediately after result | ASA-prepared | Skeleton pending exact result identifiers |

### Post-result roadmap

R1. Result Intake — 5–10 min
Purpose: verify exact execution, targets, persistence, and evidence boundaries.

R2. ASA Method Review — 15–30 min
Purpose: evaluate calibration, blind integrity, evaluator independence, controls, leakage/bias, and disagreement.

R3. Research Findings Review — 20–40 min
Purpose: identify weakened assumptions, strengthened evidence, independent discoveries, new alternatives, and useful negative results.

R4. AAA-RESEARCH-VALIDATOR L1 — separate execution
Purpose: independent paired-domain validation of the exact research result; author cannot self-PASS.

R5. Targeted Replication / Red-Team — conditional, parallelizable
Purpose: test high-value or unstable findings on independent evaluators/problems without broad rerun by default.

R6. Owner Decision — conditional
Purpose: choose method repair, basis repair, second pilot, larger-cohort review, or reconsideration of a material assumption. No automatic 48-position authorization.

## 9. Owner pre-result note — 2026-08-21 14:59 KST

OWNER_EXPLICIT_STATEMENT:
- The review criteria currently feel somewhat ambiguous.
- The current execution is taking noticeably longer than the earlier roughly five-minute class of runs.

INTERPRETATION_RESTRICTION:
- Do not infer that longer runtime implies higher quality.
- Do not infer that ambiguity means the method is invalid.
- Treat criterion ambiguity itself as an item to examine in method review and post-result calibration analysis.

REVIEW CONSEQUENCE:
- Owner pre-review should not force artificial precision where the research target is not yet mature enough to support it.
- Prefer a small number of hard methodological minimums plus explicit UNCERTAIN/OPEN states over pretending to have sharp scientific thresholds prematurely.

## 10. Owner pre-result expectation — 2026-08-21 15:06 KST

OWNER_EXPLICIT_STATEMENT:
- "일단 현재의 가설 세계관을 잘 반영한 다양한 모델과 현재의 가설 세계관을 잘 반영하지 못했지만 그래도 상당히 좋은 대안 세계관 모델이 나왔으면 해요"

OWNER_INTENT_CAPTURED_WITHOUT_EXPANSION:
1. The Owner hopes to see multiple genuinely diverse models that nevertheless represent the current working worldview well.
2. The Owner also hopes to see substantially good alternative-worldview models even when they do not represent the current working worldview well.

INTERPRETATION_RESTRICTIONS:
- Do not treat similarity to the current worldview as a universal model-quality criterion.
- Do not treat low similarity to the current worldview as a defect for an alternative-worldview candidate.
- Do not infer that either family is expected to defeat the other.
- Do not count wording/style variation as model diversity without structural or explanatory differences.
- Do not infer that the current working worldview is true merely because multiple Track-A-like candidates converge on it.

ASA_RESEARCH_INTERPRETATION_FOR_LATER_REVIEW_ONLY:
- The expectation creates two distinct desirable surfaces:
  A. CURRENT-WORLDVIEW FIDELITY WITH INTERNAL MODEL DIVERSITY.
  B. ALTERNATIVE-WORLDVIEW QUALITY WITH LOW DEPENDENCE ON CURRENT-WORLDVIEW SIMILARITY.
- Later review should therefore ask separately:
  - Did the current-worldview-informed side produce structurally diverse implementations/explanations rather than one repeated attractor?
  - Did the purpose/problem-first side produce any strong alternative explanatory structures that remain good on their own terms?
  - Was either side rewarded merely for vocabulary similarity or familiarity?
- This is an Owner expectation, not an acceptance threshold and not a frozen evaluation rule.

## 11. Owner minimum personal hope for this pilot — 2026-08-21 15:09 KST

OWNER_EXPLICIT_STATEMENT:
- "뭔가 일단 마음에 드는 거 하나라도 나왔으면 해요"

OWNER_INTENT_CAPTURED_WITHOUT_EXPANSION:
- For this pilot, the Owner would personally like at least one candidate/model to emerge that is genuinely compelling to the Owner.

INTERPRETATION_RESTRICTIONS:
- Do not define "마음에 드는" on the Owner's behalf before the result is seen.
- Do not infer that this candidate must come from the current-worldview-informed group or the alternative-worldview group.
- Do not treat Owner personal appeal as scientific validation, methodological PASS, canonical adoption, or freeze authority.
- Do not infer that absence of a personally compelling candidate automatically means the methodology failed.
- Conversely, do not allow one attractive candidate to override calibration failure, provenance problems, evaluator instability, or other method-integrity failures.

ASA_RESEARCH_INTERPRETATION_FOR_LATER_REVIEW_ONLY:
- This provides a subjective minimum aspiration distinct from the protocol's scientific success conditions: at least one candidate should ideally generate enough explanatory, structural, or design interest that the Owner wants to examine it further.
- Whether such interest ultimately survives method review, independent validation, and replication remains a separate question.

## 12. Owner concern: model persuasiveness and AI-to-AI epistemic closure — 2026-08-21 15:09 KST

OWNER_EXPLICIT_STATEMENT:
- "세계관 모델이 설득력이 있어야 하는데 사실 확신이 없어요 지금 이게 ai 끼리 토론하는거죠?"

OWNER_INTENT_CAPTURED_WITHOUT_EXPANSION:
1. A worldview/model should ultimately be persuasive or convincing enough to the Owner/human reviewer, not merely internally preferred by AI evaluators.
2. The Owner is uncertain whether the present process may amount to AI systems evaluating or debating outputs produced by other AI systems.

INTERPRETATION_RESTRICTIONS:
- Do not infer that human persuasiveness is equivalent to scientific truth or methodological validity.
- Do not infer that AI-to-AI evaluation is automatically invalid.
- Do not claim epistemic independence merely because agents/evaluators are procedurally separated or blinded.
- If the same or closely related base model/configuration generated and evaluated candidates, treat shared-prior/model-family correlation as a material methodological limitation unless independent evidence shows otherwise.

POST-RESULT METHOD-REVIEW REQUIREMENTS:
- Identify whether candidate authors and evaluators used the same underlying model family/configuration or meaningfully independent ones.
- Distinguish procedural independence (blindness, separate context, separate roles) from epistemic/model independence.
- Inspect whether evaluator agreement may reflect shared model priors rather than genuine external discrimination.
- Add a separate HUMAN PERSUASIVENESS / OWNER COMPREHENSIBILITY review surface after scientific/method integrity review, not as a substitute for it.
- Prefer direct Owner review of at least the strongest current-worldview candidate(s), strongest alternative-worldview candidate(s), and any candidate whose AI-evaluator score is high but whose human explanatory case is weak or opaque.
