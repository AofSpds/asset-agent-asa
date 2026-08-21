# AAA Owner Judgment Proxy — Decision Shadow Data Model v0.1

DATE = 2026-08-21 KST
PROJECT = AAA
PRODUCT = ASSET AGENT ASA
WORKSTREAM = AAA-ASA-MI / PROJECT-WIDE EXPERIMENT CANDIDATE
STATE = PERSISTED_ISOLATED_MEMO_BRANCH / NON_NORMATIVE / EXPERIMENT_DESIGN_CANDIDATE
BRANCH = asa-mi-owner-memo-20260821-1449

## 0. Owner statements motivating this experiment

OWNER_EXPLICIT_STATEMENT_1:
- "그 검증자를 ai 페르소나에게 지정해뒀다면 사실 저의 분신같은 느낌이면 더 좋지 않을까 해요"

OWNER_EXPLICIT_STATEMENT_2:
- "사실 프로젝트 전체에 중요한 실험입니다. 그동안의 저의 데이터로 저의 판단과 얼마나 비슷하게 만들수 있는지 충분히 외부에 있을거라고 생각해요."

OWNER_CLARIFICATION:
- "충분히 외부에 있을거라고 생각해요" means substantial external research should exist on predicting/modeling a person's preferences and judgments from accumulated behavioral/textual/decision history. It does NOT mean the Owner's personal data exists externally.

OWNER_EXPLICIT_STATEMENT_3:
- "그리고 그 페르소나의 결정과 그 시점에서의 저의 결정을 참고해본다면 프로젝트에 가장 중요한 데이터를 얻을수 있지 않을까 해요. 데이터를 어떻게 구성하고 어떻게 참조해야 그 사람의 결정을 대신할수 있는가"

## 1. Core experiment

Create a non-authoritative OWNER_JUDGMENT_PROXY that produces a decision before the Human Project Owner decides on the same case.

Freeze both independently, then compare.

The resulting paired record is the primary experimental datum:

`PROXY_DECISION_AT_t  <->  OWNER_DECISION_AT_t`

The goal is not only outcome agreement. It is to test whether the proxy selects similar reasons, objections, uncertainty, thresholds, and update behavior.

## 2. Authority separation

OWNER_JUDGMENT_PROXY is a predictive/research persona only.

It MUST NOT:
- issue Owner Acceptance;
- issue Freeze/Release authority;
- issue Independent Validation PASS;
- replace the Human Project Owner on P0/P1 or other material decisions without explicit separate delegation;
- be conflated with AAA-RESEARCH-VALIDATOR or AAA-VALIDATION-AUDITOR.

A high predictive score is evidence of a useful Owner model, not transfer of authority.

## 3. Primary data object — DECISION_EPISODE

Every material paired decision should be recorded as one immutable DECISION_EPISODE with a stable ID.

Recommended fields:

### Identity / timing
- DECISION_EPISODE_ID
- DECISION_TIME_WINDOW
- DOMAIN / WORKSTREAM
- DECISION_CLASS
- RISK / MATERIALITY CLASS

### Decision scene available at that time
- DECISION_PROMPT / QUESTION
- OPTIONS_OR_ACTION_SET actually available
- EXACT_INPUT_ARTIFACT_REFS
- EVIDENCE_AVAILABLE_TO_OWNER_AT_TIME
- EVIDENCE_NOT_AVAILABLE_AT_TIME where relevant
- CURRENT_PROJECT_STATE_REF
- CURRENT_OWNER_CONTEXT_REF
- CURRENT_HYPOTHESIS / PURPOSE / CONSTRAINT refs relevant to this decision
- UNKNOWN / CONFLICT items visible at decision time

### Proxy pre-decision receipt
- PROXY_MODEL / CONFIG / CONTEXT_VERSION
- PROXY_RETRIEVED_MEMORY_REFS
- PROXY_DECISION
- PROXY_RANKING / PAIRWISE PREFERENCES if applicable
- PROXY_REASON_CODES / OBJECTION_CODES
- PROXY_FREE_TEXT_RATIONALE
- PROXY_CONFIDENCE
- PROXY_UNCERTAINTY / OPEN QUESTIONS
- PROXY_WOULD_CHANGE_IF
- PROXY_SHA256 / FREEZE_TIMESTAMP

### Owner decision receipt
- OWNER_DECISION
- OWNER_RANKING / PAIRWISE PREFERENCES if applicable
- OWNER_REASON_CODES confirmed after decision
- OWNER_FREE_TEXT_RATIONALE / interview transcript reference
- OWNER_CONFIDENCE if explicitly provided
- OWNER_UNCERTAINTY / OPEN QUESTIONS
- OWNER_WOULD_CHANGE_IF if explicitly elicited
- OWNER_DECISION_SOURCE_REF
- OWNER_RECEIPT_SHA256 / FREEZE_TIMESTAMP

### Comparison layer — generated only after both are frozen
- OUTCOME_MATCH
- RANKING_SIMILARITY
- PAIRWISE_PREFERENCE_MATCH
- REASON_CODE_OVERLAP
- OBJECTION_CATEGORY_MATCH
- UNCERTAINTY_ALIGNMENT
- UPDATE_DIRECTION_MATCH after new evidence/challenge
- FALSE_CONFIDENCE flag: proxy confident when Owner disagrees
- RIGHT_CHOICE_WRONG_REASON flag
- DISAGREEMENT_ANALYSIS

## 4. Separate the decision scene from long-term Owner representation

Do not dump all Owner history into every prompt.

Maintain at least three distinct layers:

A. OWNER_LONGITUDINAL_CORPUS
- exact historical Owner statements, decisions, corrections, interviews, preference reversals, preserved chronologically with source refs.

B. OWNER_JUDGMENT_STATE_CANDIDATE
- derived/revisable model of likely preferences, priorities, distinctions, decision habits, unresolved tensions, and confidence; every derived item must point back to source episodes.

C. DECISION_SCENE_t
- only the information the Owner/proxy is allowed to use for the current decision, including the options actually exposed and the project state available at time t.

This separation is required to avoid hindsight leakage and to distinguish stable preference from context-specific judgment.

## 5. Retrieval strategy candidate

For a new decision, retrieval should be decision-centered rather than generic similarity-only retrieval.

Candidate retrieval order:
1. same decision class / domain analogues;
2. same purpose / constraint conflicts;
3. prior episodes where the Owner reversed or corrected an initial judgment;
4. episodes with similar uncertainty / evidence quality;
5. explicit Owner principles currently applicable;
6. a small sample of disconfirming / contradictory Owner episodes to prevent one-sided retrieval;
7. broader historical-context summary only after exact analogous episodes are retrieved.

Retrieved items should preserve chronology and source labels:
- OWNER_EXPLICIT
- OWNER_CONFIRMED
- OWNER_REVISED
- OWNER_REJECTED
- ASA_INFERRED
- OPEN / CONFLICT

Do not silently convert ASA inference into Owner evidence.

## 6. Point-in-time / leakage control

For retrospective evaluation at historical time t, only use records that existed before the Owner decision at t.

`TRAIN_CONTEXT_CUTOFF < OWNER_DECISION_TIME_t`

Future decisions, later explanations, later project outcomes, and later worldview corrections must not be supplied to the proxy when evaluating historical prediction.

For prospective evaluation, freeze proxy output before the Owner receives or records the final decision.

## 7. Why decision outcome alone is insufficient

A proxy can reach the same answer for different reasons. Therefore outcome agreement must not be treated as sufficient evidence of an Owner-like decision model.

Measure at least:
- what was chosen;
- what was rejected;
- why;
- uncertainty;
- which evidence mattered;
- what evidence would change the choice;
- how the judgment changes after a strong counterargument/new evidence.

## 8. Data quality hierarchy

Highest-value examples are likely to be episodes with:
1. real material decisions rather than casual preferences;
2. explicit alternatives/exposure set;
3. contemporaneous reasoning or interview evidence;
4. later challenge/reconsideration;
5. clear decision revision lineage;
6. similar future held-out cases available for testing.

Raw chat volume is not equivalent to high-quality judgment data.

## 9. Training / test design

Do not randomly split adjacent messages from the same decision across train and test.

Use episode-level and preferably time-based splits.

Recommended evaluation program:
- HISTORICAL BACKTEST: predict past decisions using only earlier history.
- PROSPECTIVE SHADOW TEST: proxy decides first on new decisions, then Owner decides independently.
- CROSS-DOMAIN HELD-OUT: test whether learned judgment principles transfer to a new AAA workstream.
- CHALLENGE UPDATE TEST: give both proxy and Owner the same new counterargument/evidence and compare update direction.

## 10. Candidate metrics

Keep separate metrics; do not collapse prematurely into one score.

- Binary/top-choice agreement
- Pairwise preference accuracy
- Rank correlation
- Reject/continue/uncertain state agreement
- Reason/objection semantic overlap
- Evidence salience overlap
- Confidence calibration
- Decision-change prediction after new evidence
- False-confident disagreement rate
- Temporal stability / drift tracking
- Human qualitative judgment: "does this feel like a plausible prediction of my reasoning?"

## 11. Owner persuasiveness signal — inferred research hypothesis, NOT Owner fact

Historical ASA-MI records suggest candidate factors that may influence Owner persuasiveness. These remain hypotheses to test through interviews and held-out decisions:

- reality/problem explanatory fit rather than terminology elegance;
- ability to make previously vague intuitions concrete and generate new consequences;
- clear distinction between semantic claim and implementation mechanism;
- strong alternatives/counter-hypotheses and visible failure modes rather than confirmation-only argument;
- implementability and bounded cost, with willingness to use simpler local representations when sufficient;
- non-premature ontological commitment and preservation of revisability/open alternatives;
- connection to human-compatible / human-legible downstream purpose;
- precise category distinctions when concepts had previously been conflated;
- surprising but retrospectively natural explanatory compression;
- evidence/model specification strong enough to constrain rhetoric without pretending model specification is truth.

These are retrieval/evaluation hypotheses only. They must be validated against Owner blind review and disagreement examples.

## 12. External-prior-art implications already identified

External research reviewed during concept formation suggests:
- preference-learning methods can infer individual decision criteria and criterion interactions from pairwise preferences;
- LLM user-simulation work emphasizes that user memory/history alone is incomplete without the actual exposure/option set and context of the decision;
- personalized LLM work warns that retrieving isolated historical snippets can lose continuity/global patterns;
- recent human-agent digital-twin work shows that matching final choices does not imply matching human reasons, motivating explicit reason-level comparison.

These findings support a Decision Episode + Longitudinal Corpus + Decision Scene + paired frozen-decision design rather than a simple persona prompt built from a static profile.

## 13. Current recommendation

The highest-value project-wide dataset is not a profile summary. It is a growing, immutable sequence of paired, point-in-time decision episodes:

`WHAT_OWNER_KNEW_t`
+ `WHAT_OPTIONS_EXISTED_t`
+ `PROXY_PREDICTION_t (FROZEN)`
+ `OWNER_DECISION_t (FROZEN)`
+ `REASONS / UNCERTAINTY / CHANGE CONDITIONS`
+ `POST-FREEZE COMPARISON`

Over time, this dataset can test which memory representation, retrieval strategy, model family, interview design, and calibration approach most closely predicts Owner judgment while preserving uncertainty and revision.

## 14. Non-claims

This design does not claim a person can be fully represented by their decision history, does not claim decision prediction equals identity, and does not authorize the proxy to exercise Owner authority.
