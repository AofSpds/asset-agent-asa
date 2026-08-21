# AAA Owner Delegate Persona Core Design Proposal v0.1

DATE = 2026-08-21 KST
PROJECT = AAA
PRODUCT = ASSET AGENT ASA
WORKSTREAM = AAA-ASA-MI
STATE = PERSISTED_ISOLATED_MEMO_BRANCH / NON_NORMATIVE / CORE_DEVELOPMENT_PROPOSAL
BRANCH = asa-mi-owner-memo-20260821-1449

## 0. Purpose
Design a computational Owner-delegate persona that predicts and explains the Human Project Owner's likely judgment from longitudinal Owner-originated evidence, while preserving strict authority separation and prospective validation.

This is a core-development proposal. It is NOT an Owner Acceptance artifact, formal validator, frozen requirement, or authority delegation.

## 1. Critical role separation
Working role name: `AAA-OWNER-DELEGATE-PROXY` (candidate name only).

The role is a DELEGATE-style judgment proxy: predict what the Owner would decide in the current state. It is not a TRUSTEE that substitutes its own view of the Owner's best interests.

`OWNER_DELEGATE_PROXY != HUMAN_PROJECT_OWNER`
`OWNER_DELEGATE_PROXY != AAA-RESEARCH-VALIDATOR`
`OWNER_DELEGATE_PROXY != AAA-VALIDATION-AUDITOR`

No Freeze/Release, Owner Acceptance, P0 semantic change, Shared Contract change, or Independent Validation authority is delegated by this proposal.

## 2. External prior-art basis
The design is informed by external work on:
- Generative Agent Simulations of 1,000 People: two-hour qualitative interviews + LLM agents, evaluated prospectively against later participant responses.
- PersonaAgent (ACL 2026): episodic + semantic personalized memory and test-time preference alignment.
- PersonalAgent / PersonalAlign (ACL 2026): lifelong preference inference and hierarchical intent memory from long-term user records.
- SAMem (ACL 2026): state-aware memory retrieval for decision making.
- Controllable Memory Usage / SteeM (ACL 2026): explicit control of memory reliance to reduce anchoring.
- Preference-Aware Memory Update (ACL 2026): separate long-term tendencies from recent preference movement.
- Modelling Human Decision Behaviour with Preference Learning: pairwise comparisons can identify criteria importance, interactions, and individual attitude.
- Construction-of-preference literature: preferences may be context-, framing-, task-, and elicitation-dependent rather than static constants.
- My Digital Twin Walks the City (DIS 2026): matching final choices does not imply matching reasons; reason symmetry must be evaluated.
- Delegate-vs-Trustee literature (EACL 2026): faithfully mirroring expressed preferences is different from substituting paternalistic 'best interest' judgment.

## 3. Proposed architecture

### Layer A — Immutable Owner Evidence Ledger
Store exact Owner-originated evidence without semantic overwrite:
- utterance/correction/decision
- timestamp and decision-state timestamp
- source/channel/artifact locator
- question/task context
- alternatives actually visible to Owner
- evidence available at that time
- explicit confidence/uncertainty if present
- later reversal/revision links

### Layer B — Decision Episodes
The primary learning unit is a decision episode rather than a static profile.

Each episode records:
- DECISION_EPISODE_ID
- DECISION_CLASS
- PROJECT_STATE_REF
- AVAILABLE_EVIDENCE_REFS
- AVAILABLE_ALTERNATIVES
- OWNER_EXPLICIT_DECISION
- OWNER_RANKING if available
- OWNER_REASON_TAGS / objections
- OWNER_UNCERTAINTY
- CHANGE_CONDITIONS / what would change the judgment
- SUCCESSOR_DECISION_REF if revised later

### Layer C — Derived Owner Judgment State
A revisable derived model, never promoted to Owner fact:
- stable preference hypotheses
- contextual preference hypotheses
- recurring decision heuristics
- anti-patterns / rejection triggers
- purpose priorities
- conflict patterns / tradeoff behavior
- uncertainty triggers
- update/reversal patterns
- confidence and evidence count per hypothesis

All fields must distinguish `OWNER_EXPLICIT`, `OWNER_CONFIRMED`, `MODEL_INFERRED`, `CONFLICT`, `UNKNOWN`, and `SUPERSEDED`.

### Layer D — State-Aware Retrieval
At decision time retrieve not merely semantically similar text but a balanced evidence set:
1. exact current Owner instructions/constraints
2. structurally similar past decisions
3. decisions with similar tradeoffs/purpose conflicts
4. explicit corrections and reversals
5. counterexamples where Owner chose differently
6. recent preference movement
7. long-run patterns

Retrieval must be conditioned on the actual current project state and evidence available at time t.

### Layer E — Judgment Engine
Input = `CURRENT_DECISION_SCENE + RETRIEVED_OWNER_EVIDENCE + DERIVED_JUDGMENT_STATE`.
Output must include:
- predicted decision / ranking
- predicted reasons
- predicted objections
- predicted uncertainty
- evidence references used
- conflicting prior evidence
- predicted change conditions
- abstain / insufficient-evidence state

### Layer F — Memory-Dependence Controller
Use multiple modes rather than always maximizing fidelity:
- HIGH_FIDELITY: closely emulate established Owner pattern
- BALANCED: use history but preserve novel reasoning
- FRESH_START: intentionally reduce historical anchoring for exploratory research

The proxy used for judgment prediction should normally use HIGH_FIDELITY; research generation should not.

## 4. Prospective Decision Shadow protocol
For every suitable material decision:
1. freeze current project state + available evidence.
2. proxy predicts Owner decision first.
3. hash/timestamp proxy output; hide it from Owner.
4. Owner decides normally.
5. freeze Owner decision.
6. compare only after both are frozen.
7. add paired episode to the benchmark corpus.

Random retrospective evaluation is insufficient; primary validation must be forward-in-time held-out prediction.

## 5. Metrics
Do not use a single similarity score.

Measure separately:
- choice agreement
- pairwise/ranking agreement
- continue/reject/uncertain agreement
- reason similarity
- objection-category similarity
- evidence-attention overlap
- uncertainty calibration
- abstention quality
- change-of-mind / update symmetry after new evidence
- robustness under wording/framing changes
- performance by decision class and novelty level

The most important advanced metric is `UPDATE_SYMMETRY`: whether proxy and Owner revise in the same direction when exposed to the same new evidence.

## 6. Baselines required
Compare the proposed proxy against:
B0 generic LLM, no Owner data
B1 static Owner profile prompt
B2 recent-k conversation memory
B3 semantic-RAG over all Owner records
B4 hierarchical episodic+semantic memory
B5 state-aware + counterexample-balanced retrieval (proposed)

Only evidence of prospective gain over these baselines should justify increased complexity.

## 7. Interview program
Use interviews as active preference-elicitation, not merely profile writing.

Recommended interviews:
- broad semi-structured Owner interview to capture purpose, worldview, tradeoffs, failure sensitivities, uncertainty style
- pairwise model comparisons
- counterfactual questions: what evidence would reverse the decision?
- contradiction probes
- deliberately neutral rewording of the same problem
- delayed repeat questions to estimate self-consistency and drift

Adaptive question selection should prioritize uncertainty reduction and disputed/incomplete judgment regions rather than asking more questions indiscriminately.

## 8. Initial Owner-persuasiveness hypotheses from existing AAA records
These are MODEL_INFERRED, not Owner facts:
- explanatory compression / reality-fit is likely persuasive
- an unexpected structure that makes multiple phenomena feel more natural is likely persuasive
- precise conceptual distinctions and category corrections are important
- philosophical depth is valued when it reaches operational/model consequences
- implementation feasibility/cost remains a first-class check
- falsifiability, adversarial survival, and explicit failure surfaces increase credibility
- current-worldview similarity alone is not sufficient
- novelty alone is not sufficient
- human familiarity / human-compatible interpretation matters
- premature ontological finalization is likely disfavored

These hypotheses must be tested, not embedded as fixed weights.

## 9. Delegate vs Trustee policy
Version 1 should be strictly `DELEGATE_PREDICTION_MODE`: predict the Owner's current judgment.
A separate future `TRUSTEE_ADVISOR_MODE` may recommend what appears best for the Owner/project, but it must never be conflated with prediction of what the Owner would actually decide.

## 10. Authority stages
Stage 0 — research simulation only.
Stage 1 — prospective shadow prediction; zero execution authority.
Stage 2 — Owner-facing advisory recommendation after strong calibration.
Stage 3 — bounded low-risk delegation candidate, only if explicitly authorized, revocable, auditable, and limited to decision classes with demonstrated prospective performance.

P0 semantics, Freeze/Release, Owner Acceptance, Shared Contract, and major architecture authority remain Human Owner controlled unless governance is explicitly changed through proper authority/validation.

## 11. Core scientific question
The main project-level question is not whether an LLM can sound like the Owner.

It is:
`WHAT DATA REPRESENTATION + MEMORY UPDATE + RETRIEVAL + INFERENCE METHOD BEST PREDICTS THE OWNER'S UNSEEN DECISIONS, REASONS, UNCERTAINTY, AND REVISION BEHAVIOR OVER TIME?`

This question directly connects the experiment to AAA-ASA-MI research on memory, continuity/succession, mutable persona state, and human-compatible computational representation.

## 12. Recommended first implementation milestone
`OWNER-DELEGATE-PROXY M0 — SHADOW PREDICTOR`

Deliverables:
- Decision Episode schema
- immutable Owner evidence ingestion
- derived Owner Judgment State with provenance
- state-aware balanced retriever
- prediction output schema
- time-based train/dev/held-out split
- 3-5 baseline implementations
- first 20 prospective shadow decisions
- reason/uncertainty/update-symmetry evaluator
- calibration report

No fine-tuning is required for M0; first establish whether structured context + retrieval is sufficient. Fine-tuning / preference optimization becomes M1 only if M0 evidence justifies it.

## 13. Non-claims
- No claim that Owner judgment can already be replicated accurately.
- No claim that retrospective similarity proves prospective fidelity.
- No claim that a proxy can replace Human Owner authority.
- No claim that the Owner has one static utility function.
- No claim that more memory always improves prediction.
- No claim that matching choices equals matching reasoning.
