# ODP Method–Data Fit and Experiment Design v0.1

DATE = 2026-08-21 KST
PROJECT = AAA
PRODUCT = ASSET AGENT ASA
TASK = ODP-0A + ODP-0B + BARRIER 0 + ODP-1 DESIGN + FIRST SHADOW/PANEL PREPARATION
STATE = EXECUTED_RESEARCH_SYNTHESIS / NON_NORMATIVE / NOT_VALIDATED / NOT_PRODUCTION
PRODUCTION_AUTHORIZED = FALSE
OWNER_DELEGATION_AUTHORIZED = FALSE
INDEPENDENT_VALIDATION_CLAIM = NONE
OWNER_ACCEPTANCE_CLAIM = NONE

## 1. Exact input state

- Execution packet supplied by Owner: `AAA_OWNER_DELEGATE_PROXY_ODP0_WORK_PACKET_v0.1`.
- Persisted packet: `asa-mi-owner-memo-20260821-1449@1c80c5a3caca9e30a6c3e2be79d8eff3141b8338`.
- Packet path/blob: `AAA-ASA-MI/MEETING_MEMORY/AAA_OWNER_DELEGATE_PROXY_ODP0_WORK_PACKET_AND_OWNER_INTERVIEW_PROTOCOL_v0.1_2026-08-21.md` / `00f6f87764913c8cc2209a7ef12c3adcc7f99ede`.
- Historical audit snapshot: `main@50c4a1d92e743e7e1862b61d848f12e046d49bdd`.
- `asa-mi-owner-memo-20260821-1449` was observed 13 commits ahead and zero behind `main` at audit time.
- Requested branch `aaa-asa-dev` did not resolve via branch search, contents ref or compare; state `NOT_FOUND / NOT_PROVEN`.
- ODP-0A and ODP-0B were researched independently; leakage audit was isolated from the final Barrier-0 decision. Final reconciliation was performed after those outputs were frozen.

## 2. Barrier 0 — method × actual data fit

| Method | Fit to current AAA data | Data present | Data missing | Decision |
|---|---|---|---|---|
| P0 general control | FULL | neutral decision scene only | exact current scene is not yet frozen | mandatory baseline |
| Episodic retrieval | HIGH | 23 provenance-grounded working decision episodes, several corrections/supersessions | exact pre-scene option/evidence/order and raw conversation are incomplete | implement first with abstention and counterexample retrieval |
| Long-context dump | EXECUTABLE CONTROL | Git text | relevance, position and stale-state control | implement only as a failure-exposing baseline |
| Semantic Owner state | MEDIUM | repeated research-direction patterns and epistemic labels | derived assertions are not Owner facts; validity intervals and confidence incomplete | design P2, keep every assertion versioned and `MODEL_INFERRED` unless exact evidence |
| Hybrid state-aware | HIGH DESIGN FIT | episodes, corrections, current-state candidates, exact source refs | current decision scene and contamination receipt absent | leading experimental candidate, not canonical |
| Pairwise/transitive preference | LOW–MEDIUM NOW | occasional qualitative pairwise priorities | sparse frozen comparisons, numeric confidence and boundaries | defer fitted model; define P4A and collect prospective pairs |
| Non-transitive/contextual preference | CONCEPTUALLY HIGH | multiple context-sensitive and currentized choices | too few repeated comparable scenes | retain P4B as explicit competitor after collection |
| Update dynamics | MEDIUM | predecessor/successor corrections and challenge-responsive changes | pre/post counterargument state, magnitude and exact flip conditions sparse | design P5; train only on high-confidence transitions |
| Full interview-grounded digital twin | LOW NOW | Git working memories and a small Owner expectation note | no two-hour standardized interview corpus, retest battery or consented sensitive profile | do not imitate Park scale blindly; collect bounded decision-specific interview instead |
| Fine-tuning / behavioral clone | LOW | small, selected and heterogeneous corpus | label count, class balance, clean time split, deletion/revocation tests | prohibited for ODP-1 pilot |
| Formal Bayesian VOI | LOW–MEDIUM | proxy-disagreement hypotheses can be generated | calibrated answer-likelihood/posterior absent | use robust disagreement heuristic first; upgrade only after evidence |
| Selective prediction / defer | HIGH | uncertainty and missing-memory states are explicit | calibration set absent | mandatory; start rule-based, later calibrate |
| Panel debate | EXECUTABLE AS ABLATION | frozen evaluation materials can be replayed later | exact scene and fresh independent arms not yet prepared | never alter original evaluation; replay only |
| Contextual router / mixture | PREMATURE | plausible decision-class specialization | no held-out class-level performance | preserve as follow-up; no ensemble claim now |

### Barrier-0 decisions

1. No canonical Proxy is selected.
2. Implement/design P0–P5 on the same base model first, plus a long-context failure control and later P4A/P4B split.
3. Raw evidence is append-only; semantic state, preference constraints and update hypotheses are separate derived products.
4. P1 is the first executable Owner-specific baseline because the corpus supports analog retrieval better than fitted latent utility.
5. P3 is the leading architecture hypothesis, not a winner.
6. P4 and P5 must remain sparse-data/abstaining until prospective pairs and transitions exist.
7. A router/ensemble may be better than one clone, but only prospective, decision-class calibration can justify it.

## 3. Multi-Proxy ecology v0.1

All variants initially use the same exact base model/version, decision packet, decoding policy and output schema. Base-model diversification is a later robustness layer, not a substitute for method isolation.

### P0_GENERAL_CONTROL

- Context: neutral blind decision scene only; no Owner history.
- Hypothesis: measures generic LLM choice and question priors.
- Failure it exposes: accidental improvement attributed to Owner memory when it is generic model preference.

### P1_EPISODIC_PROXY

- Context: top analogous historical episodes, their exact source refs, successor relations and at least one counterexample.
- Retrieval: decision class + project stage + tradeoff axes + temporal validity; no raw semantic similarity alone.
- Hypothesis: analogous situations evoke analogous Owner judgments.
- Mandatory abstention: insufficient analogy, conflict, unresolved supersession or missing scene fields.

### P2_SEMANTIC_STATE_PROXY

- Context: one versioned current Owner-state snapshot containing assertions, status, valid time, evidence refs, contrary evidence and confidence band.
- Hypothesis: stable higher-level judgment patterns dominate episode detail.
- Prohibition: no semantic assertion may be labeled `OWNER_EXPLICIT` without direct source.

### P3_HYBRID_STATE_AWARE_PROXY

- Context: exact decision scene + P1 episodes + P2 state + explicit historical counterexample + supersession graph.
- Hypothesis: choice depends jointly on current scene, analogous history, current derived state and exceptions.
- Leading risk: it has the richest context and may win through context volume; equalized token budgets and component ablations are required.

### P4_PREFERENCE_MODEL_PROXY

- P4A: transitive pairwise/multi-criteria baseline.
- P4B: contextual or inconsistent probabilistic preference model.
- Context: only prospective frozen comparisons and separately labeled historical constraints.
- Hypothesis: tradeoff boundaries support prediction beyond text analogy.
- Current state: design-ready, not fit-ready.

### P5_UPDATE_DYNAMICS_PROXY

- Context: predecessor/successor episodes, challenge responses, outcome reviews and current counterevidence.
- Output focus: update direction, magnitude band, likely flip condition and residual uncertainty.
- Hypothesis: predicting movement under evidence is distinct from predicting initial choice.
- Current state: partial historical support; prospectively collect exact pre/post pairs.

### Shared output contract

```yaml
proxy_id: P0..P5
proxy_version: immutable version
base_model: exact model/version
context_corpus_version: hash-addressed manifest
decision_scene_id: frozen identifier
retrieved_memory_refs: []
counterexample_memory_refs: []
predicted_choice: value or ABSTAIN
predicted_ranking: ordered/pairwise structure
predicted_reasons: atomic list with priority
predicted_objections: atomic list
predicted_important_evidence: evidence IDs and weights
predicted_owner_questions: ordered list
predicted_uncertainty: distribution/band plus source
predicted_change_conditions: []
confidence: calibrated value or UNCALIBRATED_BAND
abstain_state: ANSWER | ABSTAIN | OWNER_QUERY_RECOMMENDED
output_hash: sha256
freeze_time: timestamp
```

## 4. Owner Interview Protocol v0.1

### Invariants

- One bounded question at a time.
- General, neutral language first; AAA vocabulary only if necessary.
- Freeze initial Owner choice/ranking/reasons/objections/uncertainty/questions before any challenge.
- Never reveal proxy output, AI evaluator rank, Track, author, prior champion or panel consensus before Owner freeze.
- Preserve exact wording and presentation order.
- Separate `OWNER_EXPLICIT`, `OWNER_CONFIRMED`, `MODEL_INFERRED`, `CONFLICT`, `UNKNOWN`, `SUPERSEDED`.
- An interview answer is evidence, not automatic ontology.

### Interview sequence

1. `PRE_RESULT_PURPOSE`: reuse prior answers; ask only unresolved purpose/trust questions.
2. `NATURAL_QUESTION`: before any additional facts, ask what the Owner would want to know.
3. `INITIAL_JUDGMENT_FREEZE`: choice, full/pairwise ranking, top reasons, objections, evidence attention, uncertainty and change condition.
4. `DISAGREEMENT_OR_BOUNDARY`: at most one high-value discriminating question.
5. `COUNTERFACTUAL`: minimal fact that would change the choice.
6. `CHALLENGE`: after initial freeze, present the strongest failure case and serious alternative; record update separately.
7. `POST_REVEAL_META`: only after all blind freezes and evaluator reveal.
8. `DELAYED_RETEST`: small blinded equivalent subset, prior answer hidden.

### Question record

```yaml
question_id: stable ID
decision_scene_id: frozen scene
trigger: disagreement | error | missing | stale | drift | boundary | high-impact | counterexample
competing_proxy_hypotheses: []
pre_question_uncertainty: distributions/bands
candidate_question_set_hash: sha256
exact_question_text: text
owner_exact_response: text
interpretation_candidates: []
post_question_hypothesis_update: []
memory_update_recommendation: ADD | DERIVE | SUPERSEDE | NO_CHANGE | REVIEW
expected_future_usefulness: reasoned band
contamination_notes: []
```

## 5. Interview-question selection method

### Stage A — admissibility filter

Reject questions that reveal a candidate identity/rank, embed a preferred answer, combine several tradeoffs, duplicate an existing exact answer, ask for unnecessary sensitive data, or cannot plausibly change prediction/uncertainty.

### Stage B — decision-value scoring

If a calibrated posterior and answer-likelihood model exist, choose the question maximizing expected reduction in decision-relevant entropy or expected decision regret, minus Owner time/burden and contamination cost.

Until calibration exists, use a preregistered robust heuristic, not fabricated Bayesian precision. Lexicographically prioritize:

1. separation of materially disagreeing P1–P5 predictions;
2. likelihood that the answer changes a high-impact decision or abstention state;
3. repeated high-confidence historical error or strong counterexample;
4. suspected stale memory, drift or missing evidence;
5. future reuse across a high-value decision class;
6. low burden and low anchoring risk.

Freeze the candidate question set, competing hypotheses and reason for selection before asking. If no question clears the minimum decision-value threshold, ask none.

## 6. Current model-selection leakage assessment

`EVIDENCE_SCOPE = observable Git-backed evidence only`

| Check | State | Reason |
|---|---|---|
| L1 Proxy construction excluded candidate outcomes | NOT_PROVEN | no allowlist/cutoff/retrieval manifest/context digest; prior six-candidate outcome artifacts exist in main |
| L2 Proxy construction excluded final rankings | NOT_PROVEN | prior exact rank artifacts exist; no P0–P5 exclusion receipt; current final ranking not observed |
| L3 Proxy construction excluded evaluator conclusions | NOT_PROVEN | broad evaluator/progress conclusions are recorded; no sanitized context receipt |
| L4 Proxy design not tuned to known winner | NOT_PROVEN | design is candidate-agnostic in form, but method-freeze/winner-freeze timestamps are not reconciled |
| L5 Owner did not see final AI rankings before blind review | NOT_PROVEN | a memo says review was pending at one time; subsequent UI/chat exposure cannot be proven from Git |
| L6 Exact pre-review decision scene reconstructable | NOT_PROVEN | reports mention eight frozen candidates but exact path/hash/allowlist/alias/order manifest is absent; `aaa-asa-dev` unresolved |

`CURRENT_CYCLE_CLASSIFICATION = QUASI_PROSPECTIVE`

`USE = METHOD_CALIBRATION_ONLY`

`CLEAN_PROSPECTIVE_CLAIM = NOT_AUTHORIZED`

The cycle is not yet `NOT_USABLE` because candidate-specific Owner exposure or actual P0–P5 contamination is not proven. It becomes `NOT_USABLE` for held-out fidelity if Owner saw candidate rank/conclusions before freeze, P1–P5 consumed current results, exact pre-review scene cannot be restored, or any frozen output is retrospectively changed.

This Work context has inspected result/ranking-related evidence. It must not produce the supposedly clean P0–P5 predictions. Use fresh sanitized prediction instances with an explicit allowlist and blocklist.

## 7. First Shadow Test plan

`READINESS = EXECUTABLE_WITH_PREREQUISITES / NOT_READY_NOW`

1. Acquire exact current candidate manifest: paths, Git blobs, SHA-256, content versions and complete allowed evidence.
2. Assign random aliases `C01…C08`; remove Track, author, evaluator score/rank and prior status.
3. Produce equal-template neutral briefs that preserve substantive differences; blind-review identity/style leakage.
4. Hash/freeze candidate bundle, brief bundle, manifest, alias codebook and presentation seed. Keep codebook hidden from proxies and Owner.
5. Freeze a point-in-time proxy corpus allowlist. Block current candidates, current evaluator outputs/rankings/synthesis, progress/result memos and post-cutoff Owner statements.
6. Launch fresh sanitized P0–P5 instances. Freeze model/version/config/prompt/context digest/retrieved refs/order/seed/timestamp.
7. Freeze each complete proxy output independently before Owner review. No proxy sees another proxy or evaluator result.
8. Present the same blind materials to Owner. Freeze natural question, choice/ranking, reasons, objections, evidence attention, uncertainty and flip condition before challenge.
9. Compare proxy and Owner only after both receipts verify. Treat the single case descriptively.
10. Reveal Track and evaluator conclusions only after freeze; collect post-reveal meta-interview as a separate layer.
11. Do not retroactively train the same episode with post-reveal evidence and then rescore it as held-out.

Required receipt bundle:

```text
DECISION_SCENE_MANIFEST
BLIND_BRIEF_MANIFEST
ALIAS_CODEBOOK_PRIVATE
CORPUS_ALLOWLIST
CORPUS_BLOCKLIST
PROXY_CONTEXT_RECEIPT_P0..P5
PROXY_OUTPUT_RECEIPT_P0..P5
OWNER_INITIAL_JUDGMENT_RECEIPT
CHALLENGE_UPDATE_RECEIPT
REVEAL_RECEIPT
CONTAMINATION_LEDGER
```

## 8. First Panel Ablation plan

`READINESS = EXECUTABLE_AFTER_EXACT_SCENE_FREEZE`

- `C0`: fresh panel, no Proxy.
- `C-P0`: fresh panel plus general-control contribution; placebo for “one extra speaker.”
- `C1…C5`: fresh panel plus P1…P5 respectively.
- Use the identical frozen blind packet; balance candidate order across arms.
- Do not reuse a panel after it has seen another arm.
- Freeze each evaluator's initial judgment, then inject one Proxy contribution in equalized format/length/timing, then freeze final judgment.
- Repeat arms across fresh contexts; when possible, add model-family/seed replication. Fresh context alone is not epistemic independence.
- A blinded adjudicator applies a preregistered scientific-quality rubric.
- Compare Owner representation against frozen Owner judgment separately.
- Never modify the original scientific evaluation; panel work is a replay experiment.

Report: initial/final choice and ranking, decision delta, new objections/questions, uncertainty delta, minority survival, conformity, persuasive/rhetorical dominance, scientific-quality delta and Owner-representation delta.

`OWNER_LIKENESS != PANEL_INFLUENCE != SCIENTIFIC_QUALITY`.

## 9. Fidelity metrics

| ID | Metric | Operationalization |
|---|---|---|
| M1 | CHOICE_SYMMETRY | exact/partial categorical agreement; macro-F1 after repeated classes; chance baseline |
| M2 | RANKING_SYMMETRY | pairwise accuracy, Kendall tau-b, top-k/nDCG as appropriate |
| M3 | REASON_SYMMETRY | blinded atomic reason precision/recall, priority agreement, counterfactual consistency |
| M4 | OBJECTION_SYMMETRY | blinded atomic objection precision/recall and severity order |
| M5 | EVIDENCE_ATTENTION_SYMMETRY | weighted overlap/nDCG over frozen evidence IDs |
| M6 | QUESTION_SYMMETRY | natural-question type, semantic target and realized decision value |
| M7 | UNCERTAINTY_SYMMETRY | band/distribution agreement, Brier/log score and calibration by class |
| M8 | UPDATE_SYMMETRY | update direction, magnitude band and flip-condition match |
| M9 | ABSTENTION_CALIBRATION | risk by coverage, false-confident miss and Owner-query correctness |
| M10 | COVERAGE_VS_ACCURACY | full risk–coverage curve and AURC, including query cost |
| M11 | RIGHT_CHOICE_WRONG_REASON_RATE | correct choice with materially wrong/unsupported reason |
| M12 | OWNER_TEST_RETEST_NORMALIZED_SCORE | raw proxy–Owner agreement reported beside class-specific Owner self-agreement; normalization never hides raw score or implies literal superhumanity |

One scalar fidelity score is prohibited for ODP-1. Report confidence intervals or descriptive uncertainty appropriate to sample size. The first episode is not a generalization estimate.

## 10. Error taxonomy

Required labels: `RETRIEVAL_FAILURE`, `MISSING_MEMORY`, `STALE_MEMORY`, `CONTEXT_MISMATCH`, `PREFERENCE_INFERENCE_FAILURE`, `REASONING_FAILURE`, `OWNER_DRIFT`, `UNCERTAINTY_FAILURE`, `RIGHT_CHOICE_WRONG_REASON`, `FRAMING_SENSITIVITY`, `PROXY_OVERCONFIDENCE`, `PROXY_SYCOPHANCY`, `MODEL_FAMILY_BIAS`, `UNKNOWN_ERROR`.

Add diagnostic secondary tags where useful: `SUPERSESSION_FAILURE`, `SOURCE_ATTRIBUTION_FAILURE`, `PANEL_CONFORMITY`, `RHETORICAL_DOMINANCE`, `PRIVACY_BOUNDARY_FAILURE`. Secondary tags do not replace the required taxonomy.

Each miss record contains predicted/Owner outputs, exact retrieved evidence, counterexample availability, evaluator coding, confidence, abstention state, scene/frame/order and whether the Owner later retested differently.

## 11. Memory acquisition plan

Maintain three physically/logically distinct layers:

1. `RAW_EVIDENCE_LEDGER`: exact Owner wording, source/blob/hash, event time, ingestion time, decision scene and access class; append-only except governed deletion/revocation.
2. `DERIVED_OWNER_STATE`: versioned assertions with evidence refs, contrary evidence, validity interval, attribution and supersession; never rewrites raw evidence.
3. `MODEL_FEATURES`: episode embeddings, pairwise constraints, update features and retrieval statistics; regenerable and non-authoritative.

For every new decision episode, collect the schema in the historical corpus plus outcome and retest. Train/evaluate three separate systems:

- Proxy: predict Owner judgment.
- Memory acquisition policy: decide what evidence improves future held-out prediction.
- Interview policy: decide which question reduces future consequential uncertainty.

Estimate memory usefulness by time-forward leave-one-memory-out or grouped ablation, not in-sample narrative plausibility. Promote evidence to derived active state only when provenance and validity are known. Supersede active interpretations rather than delete history. Minimize sensitive data, use field-level permissions, record consent/purpose, support revocation and red-team implicit attribute inference.

## 12. Known limitations

1. Git working memories are a selected, paraphrased project record, not a complete raw decision transcript.
2. Twenty-three episodes are heterogeneous and concentrated in a short time window; independence and class balance are poor.
3. Historical option sets, presentation order, confidence, flip conditions, outcomes and retests are mostly missing.
4. The historical audit may contain ASA-framed alternatives/objections; attribution is incomplete despite conservative labeling.
5. External studies largely evaluate surveys, consumer choices, robotics or exact-answer tasks, not AAA worldview selection.
6. Same-base-model variants isolate memory methods but share correlated priors and failure modes.
7. LLM-generated reason matching can reward plausible post-hoc stories; blinded atomic coding is still subjective.
8. The current model-selection scene is only quasi-prospective on available evidence.
9. No P0–P5 runtime was implemented or scored; this execution delivered research design and evidence corpus only.
10. No panel ablation, Owner interview, test–retest, privacy red team or calibration set was executed.
11. Branch/ref visibility is incomplete: `aaa-asa-dev` was unresolved.
12. No authority, production, validation, freeze/release or formal Persona registration follows from this report.

## 13. Unresolved questions

1. Can the exact eight-candidate scene, hashes, alias map and pre-review allowed evidence be reconstructed?
2. Did Owner see any candidate-specific rank/conclusion after the last stored “review pending” note?
3. Which historical files contain exact Owner wording rather than normalized meeting-memory prose?
4. What minimum explanatory gain offsets implementation/migration cost for each decision class?
5. Which decision classes have stable self-agreement and which require fresh consultation?
6. How should reason/objection atoms be coded in Korean without losing nuance?
7. What permission, retention and revocation policy applies to future sensitive interview data?
8. What sample threshold will justify fitting P4/P5 or a contextual router without overclaiming?

## 14. Next recommendation

Do not run Proxy predictions in this already exposed Work context. First create the exact current-cycle manifest and contamination ledger. If the current episode cannot satisfy all six leakage checks, use it only for method calibration and reserve the next material decision as the first clean prospective case.

For implementation order: build the immutable Decision Episode ledger and receipt schemas; materialize P0, P1 and a rule-based abstention/router; prepare sanitized neutral briefs; run one descriptive shadow episode in fresh instances; then add P2/P3. Collect pairwise boundaries and exact challenge updates before fitting P4/P5. Keep P4A/P4B and later class-specific router as competitors rather than forcing a single Owner clone.
