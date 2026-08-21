# AAA Owner Delegate Proxy — Multi-Variant Participation & Elicitation Experiment v0.1

DATE = 2026-08-21 KST
PROJECT = AAA
PRODUCT = ASSET AGENT ASA
STATE = PERSISTED_ISOLATED_MEMO_BRANCH / NON_NORMATIVE / CORE_DEVELOPMENT_EXPERIMENT_PROPOSAL
BRANCH = asa-mi-owner-memo-20260821-1449

## 0. Owner proposal captured

OWNER_EXPLICIT_1:
- Compare identical model-evaluation results with and without an Owner-delegate persona participating.

OWNER_EXPLICIT_2:
- Maintain multiple alternative Owner-delegate personas based on different methodologies; compare how each behaves on the same evaluation.
- Derive interview questions representing situations/questions the real Owner would likely encounter in the same decision scene, then compare proxy behavior against actual Owner responses.

OWNER_EXPLICIT_3:
- The accumulated data should provide evidence not only about Owner decision prediction, but also about how Owner memory should be collected, structured, retrieved, and how interviews should be designed.
- The Owner explicitly permits deviation from the proposed method if a better research design exists.

## 1. ASA synthesis: do not build one clone first

Recommended architecture is not ONE OWNER CLONE.

Build a `PROXY ECOLOGY` consisting of methodologically distinct candidate Owner Judgment Proxies plus an explicit control condition.

Keep two experimental planes separate:

A. PROXY FIDELITY PLANE
- proxies predict Owner judgment in SHADOW mode;
- proxy outputs cannot influence the evaluation panel or Owner;
- purpose: measure how well each proxy models the Owner.

B. PANEL INTERVENTION PLANE
- compare the same frozen evaluation packet under conditions where no proxy, one proxy, or a proxy ensemble participates;
- purpose: estimate the causal effect of Owner-proxy participation on model-evaluation outcomes.

Do not infer proxy fidelity from panel impact. A proxy can strongly change a panel while poorly predicting Owner judgment, or closely predict Owner while having little panel influence.

## 2. Initial proxy variants

Keep the base LLM/model family constant initially where practical so that the memory/representation methodology is the principal experimental difference. Cross-model replication comes later.

P0 = CONTROL / GENERAL EVALUATOR
- no Owner-specific data.

P1 = EPISODIC CASE PROXY
- retrieves analogous historical Owner Decision Episodes and explicit statements.

P2 = SEMANTIC JUDGMENT-STATE PROXY
- uses a distilled current Owner Judgment State: stable patterns, conditional patterns, conflicts, superseded beliefs, uncertainty.

P3 = HYBRID STATE-AWARE PROXY
- episodic + semantic memory;
- current decision scene;
- explicit counterexample retrieval;
- temporal/current-state relevance.

P4 = PREFERENCE-MODEL PROXY
- pairwise preference / latent utility or probabilistic preference model derived from past decisions and interviews.

P5 = UPDATE-DYNAMICS PROXY
- attempts to predict not only current choice but how Owner judgment changes after objections, new evidence, or reframing.

P6 = ROUTED / MIXTURE PROXY (later)
- context router or model averaging over validated proxies by decision class and confidence.
- do not create until P1-P5 prospective evidence exists.

## 3. Experimental conditions for identical model evaluation

Use a frozen `EVALUATION_SCENE_PACKET` containing exact candidate artifacts, evidence available at time t, test results, and allowed context.

### SHADOW ARM
All proxy variants independently evaluate the same packet and freeze outputs.
No proxy output is visible to panel members or Owner.
Purpose = Owner-fidelity measurement.

### PANEL CONTROL ARM C0
Fresh evaluator panel, no Owner proxy participation.

### PANEL TREATMENT ARMS
C1 = fresh evaluator panel + P1
C2 = fresh evaluator panel + P2
C3 = fresh evaluator panel + P3
C4 = fresh evaluator panel + P4
C5 = fresh evaluator panel + P5 where applicable
C6 = fresh evaluator panel + validated diverse proxy ensemble (later)

Important:
- use fresh isolated panel instances for each arm;
- randomize candidate order and proxy speaking order;
- do not re-use a panel after it has seen another condition;
- preserve initial independent judgments before deliberation;
- replicate conditions because LLM panels are stochastic;
- record minority opinions and confidence, not only final consensus.

Measure both outcome and process deltas relative to C0.

## 4. Panel-impact measurements

For each treatment vs C0:
- winner / preferred-model delta;
- ranking delta;
- qualification decision delta;
- scientific-profile delta;
- disagreement diversity delta;
- convergence / herding delta;
- objection coverage delta;
- novel-question discovery delta;
- confidence/calibration delta;
- theory-contribution recovery delta;
- whether proxy participation suppresses legitimate minority views.

This tests whether an Owner-like participant contributes useful decision diversity or merely creates anchoring/authority pressure.

## 5. Owner comparison and interview protocol

After proxies are frozen, obtain the actual Owner judgment on the SAME decision scene without revealing proxy identities, outputs, panel results, rankings, or Track labels.

Owner response fields should include:
- choice / ranking;
- compelling reasons;
- strongest objection;
- uncertainty;
- missing information;
- question(s) the Owner would naturally ask;
- what evidence would change the decision.

### INTERVIEW PROBE GENERATION
Generate follow-up questions from:
1. disagreement among proxy variants;
2. high proxy uncertainty;
3. disagreement between proxy and Owner after initial reveal stage;
4. conflicting historical Owner episodes;
5. conditions where one memory representation succeeds and another fails.

Do not simply ask more questions. Select questions expected to reduce uncertainty or distinguish competing Owner-model hypotheses.

Preserve `QUESTION_GENERATION_REASON` and which proxy hypotheses the question discriminates.

## 6. Core data unit

`OWNER_DECISION_EXPERIMENT_EPISODE`

Fields should include at minimum:
- EPISODE_ID
- TIME
- DECISION_CLASS
- EVALUATION_SCENE_PACKET_DIGEST
- PROJECT_STATE_REF
- AVAILABLE_EVIDENCE_AT_T
- ALTERNATIVES
- PROXY_VARIANT_VERSION
- PROXY_MEMORY_INPUT_DIGEST
- PROXY_RETRIEVAL_SET
- PROXY_INITIAL_JUDGMENT
- PROXY_REASONS
- PROXY_OBJECTIONS
- PROXY_UNCERTAINTY
- PROXY_CHANGE_CONDITIONS
- PANEL_ARM
- PANEL_INITIAL_JUDGMENTS
- PANEL_FINAL_JUDGMENT
- OWNER_INITIAL_JUDGMENT
- OWNER_REASONS
- OWNER_OBJECTIONS
- OWNER_UNCERTAINTY
- OWNER_QUESTIONS
- OWNER_CHANGE_CONDITIONS
- POST_CHALLENGE_OWNER_JUDGMENT
- POST_CHALLENGE_PROXY_JUDGMENT
- AGREEMENT_METRICS
- ERROR_CLASSIFICATION
- INTERVIEW_PROBES_GENERATED
- MEMORY_ACQUISITION_DELTA
- SUCCESSOR_PROXY_VERSION

## 7. Error taxonomy

Do not record only correct/incorrect.

Candidate error classes:
- RETRIEVAL_FAILURE
- MISSING_OWNER_MEMORY
- STALE_MEMORY
- CONTEXT_MISMATCH
- WRONG_DECISION_CLASS_ANALOGY
- PREFERENCE_INFERENCE_FAILURE
- REASONING_FAILURE
- OWNER_STATE_DRIFT
- UNCERTAINTY_MISCALIBRATION
- PRESENTATION / FRAMING SENSITIVITY
- RIGHT_CHOICE_WRONG_REASON
- PROXY_HERDING_EFFECT
- OWNER_SELF_INCONSISTENCY / TEST_RETEST_VARIANCE
- UNKNOWN

## 8. Evaluation layers

### Proxy fidelity
- choice agreement
- ranking correlation
- reason overlap / semantic alignment
- objection alignment
- evidence-attention alignment
- uncertainty calibration
- question-generation similarity
- update symmetry after new evidence
- selective prediction accuracy at different abstention/coverage levels

### Proxy contribution to panel
- incremental decision quality where externally evaluable
- coverage of Owner-relevant objections/questions
- diversity gain or loss
- susceptibility to majority pressure
- effect on final evaluator stability

### Memory/interview-system quality
- prediction-error reduction per newly stored memory item
- prediction-error reduction per interview minute/question
- retrieval hit utility
- stale-memory harm rate
- active-question information gain
- number of Owner interventions avoided without loss of fidelity (future, bounded use only)

## 9. Memory and interview policy learner

The higher-value long-run target is not merely the best proxy persona.

Create two derived experimental components:

`OWNER_MEMORY_ACQUISITION_POLICY`
- which events/statements/decisions should be persisted;
- at what granularity;
- which contradictions and supersessions must be preserved;
- which contexts make a memory reusable;
- when a memory should be treated as stale or conditional.

`OWNER_INTERVIEW_POLICY`
- when to interview;
- what decision boundary to probe;
- which pairwise/counterfactual question maximally distinguishes current proxy hypotheses;
- when further questioning adds little information and should stop.

Evaluate these policies prospectively by whether they improve future held-out Owner-prediction performance.

## 10. Recommended improvement over a single winner-take-all proxy

Do not select one permanent Owner clone too early.

Human judgment is context-dependent and revisable; different proxy representations may dominate in different decision classes.

Keep a longitudinal `PROXY PERFORMANCE REGISTRY` by:
- decision class;
- time period;
- evidence regime;
- proxy version;
- confidence/abstention bin.

Later consider a routed mixture/ensemble only if held-out evidence demonstrates predictable domain-specific strengths.

## 11. Scientific controls

- prospective temporal holdout is mandatory;
- no Proxy answer visible to Owner before Owner freeze;
- no Owner answer visible to Proxy before Proxy freeze;
- no panel result visible during Owner blind judgment;
- preserve exact decision-scene evidence to prevent hindsight leakage;
- periodically measure Owner test-retest consistency as a human ceiling/reference;
- use negative controls such as generic-persona, recent-chat-only, static-profile, and random-memory retrieval baselines;
- separate procedural independence from epistemic/model-family independence;
- after memory-method isolation, replicate across different base model families.

## 12. Authority separation

OWNER_DELEGATE_PROXY is a predictive/representational experiment.
It is not:
- Human Project Owner;
- AAA-RESEARCH-VALIDATOR;
- AAA-VALIDATION-AUDITOR;
- Owner Acceptance authority;
- Freeze/Release authority.

Future bounded delegation, if any, requires separate authority design and strong prospective evidence.

## 13. External research directions supporting this design

Prior-art clusters to review formally:
- generative-agent simulation from deep qualitative interviews;
- episodic/semantic long-term personalized memory;
- dynamic preference memory update;
- learnable memory acquisition and memory compression;
- user-level personalized preference alignment;
- active/preferential Bayesian preference elicitation;
- paired human/digital-twin decision and reason symmetry;
- multi-agent debate diversity, confidence, and herding/majority pressure;
- personalization safety and memory-induced bias.

## 14. Recommended staged program

ODP-E0 = historical corpus audit and proxy-baseline construction.
ODP-E1 = retrospective replay only for debugging, NOT validation.
ODP-E2 = prospective SHADOW predictions on real Owner decisions.
ODP-E3 = multi-proxy Owner-fidelity comparison.
ODP-E4 = panel ablation: no proxy vs each proxy vs ensemble.
ODP-E5 = active interview and memory-acquisition optimization.
ODP-E6 = cross-model-family replication.
ODP-E7 = decision-class router / mixture proxy if justified.
ODP-E8 = bounded delegation research only after prospective calibration.

## 15. Non-claims

This proposal does not claim that a reliable Owner delegate already exists, that a single proxy architecture will dominate, that AI panel agreement is truth, that external research proves this exact AAA use case, or that proxy fidelity grants authority.
