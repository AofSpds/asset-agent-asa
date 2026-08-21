# AAA Owner Delegate Proxy ODP-0 Work Packet + Owner Interview Protocol v0.1

DATE = 2026-08-21 KST
PROJECT = AAA
PRODUCT = ASSET AGENT ASA
WORKSTREAM = OWNER DELEGATE / JUDGMENT PROXY CORE EXPERIMENT
STATE = PERSISTED_ISOLATED_MEMO_BRANCH / NON_NORMATIVE / CORE_DEVELOPMENT_EXPERIMENT_PACKET
BRANCH = asa-mi-owner-memo-20260821-1449

## Purpose
Prepare a single executable research packet that launches, in parallel, (A) external prior-art synthesis and (B) historical Owner decision-audit, then converges into a multi-proxy design, an adaptive Owner-interview protocol, and a first shadow-evaluation opportunity using the current model-selection cycle if leakage controls can be satisfied.

## Critical clarification
The current model-selection cycle may be used as a first high-value natural experiment only if the exact candidate materials, candidate rankings, evaluator outputs, and final synthesis remain hidden from any proxy-construction process before proxy predictions are frozen.

If leakage cannot be ruled out, classify this cycle as `QUASI_PROSPECTIVE / CALIBRATION_ONLY`, not clean held-out validation.

## Workstreams

### ODP-0A — External Prior-Art Synthesis
Research at minimum:
- generative agents / digital twins / human behavior simulation
- personalized LLMs / user simulators
- longitudinal user modeling
- preference learning / preference elicitation
- active preference learning / Bayesian query selection / value of information
- episodic vs semantic memory architectures
- state-aware retrieval and memory anchoring
- preference drift / temporal instability / test-retest reliability
- choice vs reason symmetry / rationale fidelity
- multi-agent debate / panel influence / social influence / conformity
- calibration / abstention / selective prediction / coverage-vs-accuracy
- delegate vs trustee decision support
- memory acquisition / what-to-memorize / adaptive memory update
- safety risks: sycophancy, overfitting, stale memory, framing sensitivity, demand characteristics

Outputs:
1. literature map
2. methods that appear reusable
3. methods that should not be imported blindly
4. known failure modes
5. recommended experimental baselines
6. candidate metrics
7. exact citations/links/DOIs
8. unresolved questions

### ODP-0B — Historical Owner Decision Audit
Use existing AAA Git-backed Owner-originated records only.
Do not infer missing facts.

Extract a representative sample of decision episodes spanning:
- worldview/model choices
- architecture choices
- implementation-cost tradeoffs
- research-method decisions
- corrections of ASA/AI interpretation
- hypothesis acceptance/rejection
- cases where Owner changed view after new evidence
- cases with explicit uncertainty
- cases where human-familiarity / implementation / explanatory power conflicted

For each episode capture, where evidence exists:
- exact timestamp / artifact ref / commit or locator
- decision scene
- alternatives known at the time
- evidence available at the time
- Owner decision
- Owner ranking if any
- explicit reason(s)
- explicit objection(s)
- uncertainty
- change condition / what would reverse the decision
- later successor decision
- whether prior state was superseded
- evidence-state for every field: PROVEN / PARTIAL / NOT_PROVEN / CONFLICT / UNKNOWN

Outputs:
1. Decision Episode corpus draft
2. missing-data map
3. high-value decision classes
4. candidate persuasion/preference hypotheses labeled `MODEL_INFERRED`, never Owner fact
5. candidate retrieval keys
6. candidate interview gaps

## Barrier 0 — Reconciliation
Do not design the canonical proxy before comparing ODP-0A and ODP-0B.

Questions:
- Which external methods fit the actual AAA data?
- Which methods assume data AAA does not have?
- What historical fields are consistently missing?
- Which missing fields are worth collecting prospectively?
- What should remain raw evidence vs derived Owner judgment state?
- What can be tested with the current model-selection cycle without leakage?

## ODP-1 — Multi-Proxy Ecology
At minimum implement/design these methodological variants using the same base model first where possible:
- P0 GENERAL CONTROL: no Owner data
- P1 EPISODIC: analogous past decision episodes only
- P2 SEMANTIC-STATE: derived current Owner judgment state only
- P3 HYBRID STATE-AWARE: episodic + semantic + current decision scene + explicit counterexample retrieval
- P4 PREFERENCE MODEL: pairwise / latent preference or utility representation
- P5 UPDATE-DYNAMICS: emphasize how Owner changes judgment after counterevidence

All proxies must expose:
- selected evidence refs
- predicted choice/ranking
- reasons
- objections
- uncertainty
- questions they would ask
- evidence that would change their judgment
- abstain / OWNER_QUERY_RECOMMENDED state

No proxy may claim Owner authority.

## ODP-2 — Panel Participation Ablation
For the same exact model-evaluation scene compare:
- C0: evaluation panel without Owner Proxy
- C1..Cn: panel with one proxy variant
- optional later C-ENS: calibrated proxy ensemble/router

Requirements:
- fresh evaluator instances per arm
- candidate order randomized where practical
- evaluator initial judgment frozen before proxy intervention
- proxy contribution introduced only after initial judgment freeze
- final judgment frozen after intervention

Measure separately:
- panel decision delta
- ranking delta
- new objection/questions introduced
- uncertainty delta
- minority-view preservation/loss
- conformity / persuasive dominance risk
- scientific-evaluation quality
- Owner-representation value

`OWNER_REPRESENTATION_VALUE != SCIENTIFIC_VALIDATION_VALUE`.

## ODP-3 — Shadow Owner Prediction
For every proxy variant:
1. freeze decision scene
2. produce proxy prediction independently
3. freeze exact proxy output + model/config + retrieved memories
4. do not reveal predictions to Owner
5. obtain Owner judgment
6. freeze Owner judgment
7. reveal and compare

Metrics:
- Choice Symmetry
- Ranking Symmetry
- Reason Symmetry
- Objection Symmetry
- Evidence-Attention Symmetry
- Question Symmetry
- Uncertainty Symmetry
- Update Symmetry
- abstention calibration
- coverage-vs-accuracy
- right-choice/wrong-reason frequency

Also measure Owner test-retest consistency on a small delayed blind subset where feasible.

## ODP-4 — Adaptive Owner Interview Protocol
Goal is not `MORE QUESTIONS`, but `MORE INFORMATION PER OWNER MINUTE`.

### Interview source types
A. PRE-RESULT PURPOSE INTERVIEW
- what outcome would be useful
- what remains uncertain
- what result would be untrustworthy
- what should remain open

B. PROXY-DISAGREEMENT INTERVIEW
Triggered when P1..P5 diverge materially.
Ask one bounded question that best discriminates between competing Owner models.

C. TRADEOFF-BOUNDARY INTERVIEW
Use pairwise contrasts to locate decision boundaries, e.g. explanatory power vs implementation cost, novelty vs familiarity, structural generality vs bounded practicality.

D. COUNTERFACTUAL INTERVIEW
Ask what minimal changed fact/evidence would flip the judgment.

E. CHALLENGE INTERVIEW
Present the strongest objection to a currently preferred candidate and observe update behavior.

F. RETEST INTERVIEW
Later, without reminding the prior answer, repeat a small subset to estimate Owner self-consistency and drift.

### Interview contamination controls
- one bounded question at a time
- general/neutral language first
- do not tell Owner which proxy generated the question
- do not reveal proxy predictions before Owner answers
- do not reveal AI evaluator rank/Track before blind Owner judgment
- preserve exact Owner wording
- separate OWNER_EXPLICIT from MODEL_INFERRED
- do not convert answers directly into frozen ontology

### Interview-question selection rule
Prefer questions that maximize expected discrimination / uncertainty reduction across proxy variants.
Candidate selection signals:
- proxy disagreement
- high proxy confidence but historical counterexamples exist
- high expected impact on future decision classes
- repeated prediction error category
- missing memory suspected
- suspected Owner drift

### Interview output schema
For each question:
- QUESTION_ID
- trigger
- competing proxy hypotheses
- pre-question uncertainty
- exact question text
- exact Owner response
- interpretation candidates kept separate
- which proxy hypotheses gained/lost support
- whether memory should be added/updated/superseded
- expected future utility

## Current Model-Selection Cycle — First Opportunity
Treat the current ASA-MI model-selection cycle as a candidate first prospective scene because:
- Owner expectations have been recorded before final result review
- multiple candidate worldview models are being evaluated
- blind/replicated evaluation is reportedly in progress
- Owner has not yet performed final candidate review

But do NOT call it clean prospective evidence unless these checks PASS:
- proxy-design corpus excludes candidate outcomes/rankings/final reports
- current candidate documents were not used to tune proxy methods
- exact decision scene can be reconstructed at the moment before Owner review
- Owner has not seen the candidate rankings/evaluator conclusions before blind judgment
- contamination ledger is explicit

If any fail: classify as `QUASI_PROSPECTIVE / METHOD_CALIBRATION` and reserve the next decision episode as the first clean held-out case.

Recommended sequence for this cycle:
1. finish current Work without altering it
2. verify exact artifacts/results
3. before showing Owner ranks, create neutral blind candidate briefs
4. freeze P0..P5 proxy judgments independently
5. conduct Owner blind interview using adaptive protocol
6. compare proxy vs Owner
7. only then reveal AI evaluator results/Track labels
8. run meta-interview on disagreements
9. separately run panel-ablation replay; do not contaminate the original result

## Data-Learning Loop
Every episode must feed three separate learning targets:
1. PROXY MODEL — predict Owner judgment
2. MEMORY ACQUISITION POLICY — decide what information is worth retaining
3. INTERVIEW POLICY — decide what question most reduces uncertainty

Do not optimize only for final-choice accuracy.

## Authority / Governance
- OWNER DELEGATE PROXY is experimental and non-authoritative.
- It cannot issue Owner Acceptance, Freeze/Release, Independent Validation PASS, or replace required Owner decisions.
- AAA-RESEARCH-VALIDATOR remains independent and must not be tuned to Owner preference.
- Any future bounded delegation requires separate evidence, risk classification, authority design, and Owner approval.

## Required final result
Return exactly one `[RETURN PACKET]` containing:
- prior-art synthesis
- historical decision audit summary
- Decision Episode schema v0.1
- Proxy Ecology design v0.1
- Adaptive Owner Interview protocol v0.1
- current model-selection leakage assessment
- whether current cycle qualifies as CLEAN_PROSPECTIVE / QUASI_PROSPECTIVE / NOT_USABLE
- first shadow-test plan
- first panel-ablation plan
- research risks and failure modes
- next-step recommendation
- exact Git writes/commits/paths
- no scientific/validation PASS claims beyond executed evidence

## Five-line summary
현재 상태: Owner Delegate Proxy를 다중 Proxy 경쟁·Shadow 예측·Panel Ablation·Adaptive Interview·Memory Acquisition을 결합한 AAA 코어 실험으로 실행 준비한다.
핵심 판단: 현재 모델 선정은 매우 좋은 첫 기회지만 candidate/result leakage를 통제하지 못하면 clean held-out이 아니라 quasi-prospective calibration으로만 사용해야 한다.
진행 작업: 외부 선행연구와 기존 Owner Decision Audit을 병렬 수행한 뒤 Multi-Proxy와 정보이득 기반 Owner 인터뷰를 설계하도록 Work 패킷을 구성했다.
다음 단계: 현재 Work 완료를 기다리면서 ODP-0A/0B를 병렬 수행하고, 결과 공개 전 Proxy 예측과 Owner blind interview를 freeze할 수 있는지 확인한다.
사용자 행동: 이 패킷을 다음 Work 실행에 사용하고, 결과가 나오기 전에는 후보 순위·평가결론을 Owner에게 노출하지 않는 것이 가장 중요하다. 작성시각: 2026-08-21 15:46 KST
