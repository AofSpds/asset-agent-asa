# AAA-ASA-MI Owner Judgment Proxy Experiment Concept v0.1

DATE = 2026-08-21 KST
PROJECT = AAA
PRODUCT = ASSET AGENT ASA
WORKSTREAM = AAA-ASA-MI
STATE = PERSISTED_ISOLATED_MEMO_BRANCH / NON_NORMATIVE / EXPERIMENT_CONCEPT
BRANCH = asa-mi-owner-memo-20260821-1449

## 0. Owner statements

OWNER_EXPLICIT_STATEMENT_1:
- "그 검증자를 ai 페르소나에게 지정해뒀다면 사실 저의 분신같은 느낌이면 더 좋지 않을까 해요"

OWNER_EXPLICIT_STATEMENT_2:
- "사실 프로젝트 전체에 중요한 실험입니다. 그동안의 저의 데이터로 저의 판단과 얼마나 비슷하게 만들수 있는지 충분히 외부에 있을거라고 생각해요."

OWNER_CLARIFICATION:
- The intended meaning of "충분히 외부에 있을거라고 생각해요" is that the Owner expects there to be substantial external prior research / published results relevant to modeling or predicting a person's judgments/preferences from accumulated interaction/history data.
- It does NOT mean that the Owner believes their own personal data exists externally.

## 1. Experiment hypothesis

The project may construct a non-authoritative AI evaluator/persona whose task is to predict or approximate the Owner's judgment tendencies from accumulated Owner-originated records, decisions, corrections, preferences, interviews, and review history.

Working neutral name:
`OWNER_JUDGMENT_PROXY`

This is an experimental judgment-modeling role, not the Owner, not an authority artifact, and not an Independent Validation persona.

## 2. Critical authority separation

`OWNER_JUDGMENT_PROXY != HUMAN PROJECT OWNER`

`OWNER_JUDGMENT_PROXY != AAA-RESEARCH-VALIDATOR`

`OWNER_JUDGMENT_PROXY != AAA-VALIDATION-AUDITOR`

The proxy may estimate:
- likely Owner preference,
- likely Owner objections,
- likely questions the Owner would ask,
- perceived persuasiveness / purpose fit from an Owner-like perspective,
- areas where the Owner would likely remain uncertain.

It must NOT:
- approve Freeze/Release,
- issue Owner Acceptance,
- issue Independent Validation PASS,
- silently rewrite explicit Owner statements,
- replace actual Owner review on material decisions.

## 3. Why this is a project-level experiment

The experiment tests whether accumulated historical interaction, decision, correction, and worldview data can support a stable enough computational representation of one person's judgment tendencies that an AI can predict future judgments on genuinely held-out cases.

This is relevant not only to model evaluation but also to Persona continuity, memory and identity modeling, human-compatible representation, preference stability vs revision, historical-context dependence, and the distinction between a person and a model of that person.

## 4. Required external prior-art step

Before formalizing the proxy methodology, perform an external research review covering at minimum:
- longitudinal user modeling,
- preference learning / preference elicitation,
- personalized LLMs and user simulators,
- persona / digital-twin style modeling,
- inverse preference or value inference,
- calibration and held-out prediction of human choices,
- stability / drift of human preferences over time,
- risks of overfitting, sycophancy, anchoring, and evaluator leakage.

The experiment design should reuse established methods where appropriate rather than inventing the methodology from scratch.

## 5. Experimental design requirement

Do not evaluate the proxy on examples it has already seen.

Recommended split:
A. TRAIN / CONTEXT CORPUS — historical Owner records.
B. BLIND HELD-OUT OWNER JUDGMENTS — new cases; Owner answer and proxy answer produced independently.
C. REVEAL / COMPARISON — compare only after both judgments are frozen.

Do not reduce similarity to one scalar alone. Candidate measurements may include pairwise preference agreement, top-choice agreement, ranking correlation, reject/continue/uncertain agreement, objection-category similarity, reason similarity, uncertainty calibration, and stability after counterarguments.

## 6. Non-claims

This note does not claim that such a proxy is already feasible at sufficient accuracy, does not claim that external literature has already proven this exact AAA use case, and does not authorize replacement of any formal validator or the Human Project Owner.
