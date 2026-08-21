# ODP Prior-Art Synthesis v0.1

DATE = 2026-08-21 KST
PROJECT = AAA
PRODUCT = ASSET AGENT ASA
WORKSTREAM = OWNER DELEGATE / JUDGMENT PROXY CORE EXPERIMENT
STATE = RESEARCH_DRAFT / NON_NORMATIVE / NOT_VALIDATED / NOT_PRODUCTION
INDEPENDENT_VALIDATION_CLAIM = NONE
OWNER_ACCEPTANCE_CLAIM = NONE

## 1. Research question and method

This review asks which representation, memory, retrieval, elicitation, update, calibration, and panel protocols can predict one real Owner's future judgments without flattening change, contradiction, uncertainty, or context dependence.

The packet's 48 topics were mapped to ten competing method families. Primary papers, official project pages, and authoritative standards were preferred. The purpose was method transfer, not paper-count maximization. Reported results are not treated as AAA evidence until replicated on prospectively frozen AAA decision scenes.

## 2. Core conclusion

The evidence does not support a single, static “Owner clone” as the first canonical implementation. The strongest initial architecture is a competition among separately auditable proxies built over:

1. immutable source episodes with provenance;
2. valid-time, ingestion-time, and explicit supersession;
3. separate episodic, semantic-state, preference, and update representations;
4. decision-scene-aware retrieval with counterexample retrieval;
5. active, answerability-aware questions selected for decision value;
6. selective prediction and `OWNER_QUERY_RECOMMENDED`;
7. prospectively frozen, time-ordered evaluation;
8. Owner test–retest as a measured reliability ceiling, not an assumed constant;
9. panel ablation that separates Owner likeness from social influence.

Interview-grounded agents can predict some held-out human responses surprisingly well, but constructive-preference and test–retest research shows that a person's observed answer is partly scene-, wording-, and time-dependent. Therefore the AAA target is not recovery of a timeless latent utility. It is calibrated prediction of choice, ranking, reasons, objections, evidence attention, natural questions, uncertainty, and update conditional on a frozen decision scene.

## 3. Method-family map

| Family | Packet topics | Research question | Representation / memory / retrieval / interview | Prediction task and metrics | Strengths | Weaknesses, leakage and personalization risks | AAA disposition |
|---|---|---|---|---|---|---|---|
| F1 Interview-grounded individual simulation | 1,2,5,20–24,45 | Can a rich interview predict genuinely unseen responses better than demographics or a short profile? | Interview transcript or structured self-report; full-context or RAG; semi-structured interview | Survey, traits, games, held-out decisions; raw and test–retest-normalized agreement | Direct individual grounding; supports human reliability ceiling | Self-report and demand effects; privacy; survey-to-project transfer; interview can construct preference | Reuse interview and retest principles; do not import performance claims blindly |
| F2 Generative agents and user simulators | 1,5,11,16,21,23,30–32 | Do episode retrieval, reflection and planning create behaviorally faithful agents? | Natural-language memory stream; recency/relevance/importance retrieval; reflection and plan | Behavioral believability, task success, component ablation | Concrete memory pipeline and ablation pattern | Believability is not owner fidelity; reflection can fossilize model inference | Use as P1 retrieval baseline only; raw evidence must outrank reflection |
| F3 Retrieval-augmented personalization | 3,4,13–17,38–40,43 | Is retrieval/profile prompting safer and more data-efficient than tuning? | User histories, semantic/time retrieval, long context or profiles | Personalized classification/generation and tool use | Cold-start, inspectable evidence references | Static style/preferences dominate benchmarks; identity leakage; long-context position failures | Use as baseline with exact retrieved refs and counterexamples |
| F4 Temporal, hierarchical and state-aware memory | 11–19,38–42 | Can current state, history and supersession coexist without stale-memory error? | Append-only source, hierarchical summaries, bitemporal facts, topic segments | Recall, temporal reasoning, knowledge update, abstention, stale error | Fits changing Owner state and provenance | Extraction/summary errors can become authoritative; forgetting may delete rare stable rules | Highest transfer fit; preserve source and derive state separately |
| F5 Pairwise / latent preference and inverse inference | 6–9,21–24,43–44 | Can choices reveal tradeoffs and hidden value weights? | Pairwise comparisons, Bayesian/GP preference, latent user or reward model | Pairwise choice, ranking, reward prediction, adaptation | Data-efficient relative judgments; explicit uncertainty possible | Rational, stationary, scalar-utility assumptions often fail; reward hacking and embedding opacity | Competing P4 only after prospective comparisons; include inconsistent-preference baseline |
| F6 Active elicitation and value-of-information | 7,9,10,24,38–40,48 | Which one question changes the decision or reduces consequential uncertainty most? | Belief over preference hypotheses; choice-set or trajectory queries; answerability/burden model | Information gain, regret, decision value, response time/burden | Directly matches bounded Owner-time objective | Requires answer likelihood model; myopic queries; questioning can anchor | Two-stage selector: neutral safety filter, then decision-VOI or robust disagreement heuristic |
| F7 Constructed, drifting and psychometric preference | 18–20,36–37,45–48 | Are preferences stable traits or constructed responses to scene and elicitation? | Scene, framing, order, task goal, short/long-term state; delayed retest | Preference reversal, reliability, drift, framing sensitivity | Prevents false “ground truth Owner” assumption | Measurement changes the target; no single universal ceiling | Make scene and framing first-class; preserve pre/post-interview states |
| F8 Selective prediction, calibration and deferral | 25,27–29,48 | When should a proxy abstain or query the Owner? | Predictor plus selection/defer function; calibrated probabilities | Selective risk, coverage, AURC, Brier/ECE, team utility | Makes uncertainty operational; rewards appropriate abstention | Confidence may be uncalibrated under shift; query burden can be hidden | Mandatory for every P1–P5 output and router evaluation |
| F9 Explanation, debate and social influence | 23,25–26,30–32 | Does interaction improve truth or merely produce convergence? | Independent initial judgments, arguments, debate, adjudication | Accuracy delta, reason quality, conformity, minority survival, dominance | Can surface objections and missing evidence | Shared-model correlated errors; rhetoric, order, authority and sycophancy | Only as post-freeze panel ablation; never equate owner alignment with science |
| F10 Role, safety and governance | 33–35,37,41 | How are prediction, representation and delegated authority separated? | Explicit role/authority state, permissions, audit, privacy controls | Boundary violations, trustee drift, sensitive inference, revocation | Prevents mimicry from becoming authority | Personalization increases privacy and manipulation surface | Proxy remains non-authoritative; field-level access, audit and revocation required |

Coverage check: every topic numbered 1–48 in the execution packet is represented by at least one family above.

## 4. Primary and authoritative evidence registry

### Individual simulation and personalization

1. Park et al., *Generative Agent Simulations of 1,000 People* (2024), 1,052 U.S. participants, two-hour interviews, GSS/Big Five/economic games. Agents reached 85% of participants' own two-week test–retest accuracy on GSS. Direct lesson: normalize against human repeatability and do not treat raw self-disagreement as pure proxy error. <https://arxiv.org/abs/2411.10109>
2. Park et al., *Generative Agents: Interactive Simulacra of Human Behavior* (UIST 2023), 25 simulated agents; memory stream, retrieval, reflection and planning; ablation on believability. Direct lesson: test memory components separately, but believability is not fidelity. <https://arxiv.org/abs/2304.03442>
3. Argyle et al., *Out of One, Many* (Political Analysis 2023), demographic conditioning for population-opinion distributions. Direct lesson: a demographic persona is a population baseline, not an individual proxy. <https://arxiv.org/abs/2209.06899>
4. Aher et al., *Using Large Language Models to Simulate Multiple Humans and Replicate Human Subject Studies* (ICML 2023). Direct lesson: group-effect replication can coexist with non-human process and individual mismatch. <https://proceedings.mlr.press/v202/aher23a.html>
5. Santurkar et al., *Whose Opinions Do Language Models Reflect?* (ICML 2023), OpinionQA and 60 U.S. demographic groups. Direct lesson: persona steering leaves systematic misalignment. <https://proceedings.mlr.press/v202/santurkar23a.html>
6. Binz & Schulz, *Using Cognitive Psychology to Understand GPT-3* (PNAS 2023). Direct lesson: similar answers do not prove similar cognitive process; stress-test paraphrase and task perturbations. <https://www.pnas.org/doi/10.1073/pnas.2218523120>
7. Salemi et al., *LaMP: When Large Language Models Meet Personalization* (ACL 2024), seven personalized classification/generation tasks. Direct lesson: retrieval benchmarks are useful engineering baselines but are dominated by static histories. <https://aclanthology.org/2024.acl-long.399/>
8. Samuel et al., *PersonaGym* (Findings EMNLP 2025), 200 personas, 10,000 questions, six LLMs. Direct lesson: static persona adherence is multidimensional and not monotonic in model size; it is not longitudinal owner fidelity. <https://aclanthology.org/2025.findings-emnlp.368/>

### Memory, retrieval and temporal state

9. Maharana et al., *LoCoMo* (ACL 2024), very long multi-session conversations with event graphs; QA and summarization. Direct lesson: evaluate temporal and multi-session retrieval explicitly. <https://aclanthology.org/2024.acl-long.747/>
10. Wu et al., *LongMemEval* (2024/ICLR 2025), 500 questions covering extraction, multi-session reasoning, temporal reasoning, knowledge updates and abstention; roughly 30% degradation over long histories for tested systems. Direct lesson: update and abstention are first-class memory tests. <https://arxiv.org/abs/2410.10813>
11. Pan et al., *SeCom* (ICLR 2025), topic-consistent segmentation and compression for long dialogue. Direct lesson: segment granularity should be an ablation; summaries must never replace immutable source. <https://openreview.net/forum?id=xKDZAW0He3>
12. Packer et al., *MemGPT* (2023), virtual-context and tiered memory. Direct lesson: useful orchestration mechanism, not evidence of personal fidelity or provenance quality. <https://arxiv.org/abs/2310.08560>
13. Zhong et al., *MemoryBank* (AAAI 2024), portrait memory plus forgetting. Direct lesson: age may be a retrieval prior but must not physically erase rare, stable Owner evidence. <https://ojs.aaai.org/index.php/AAAI/article/view/29946>
14. Rasmussen et al., *Zep/Graphiti* (2025), temporal knowledge graph with event and validity time. Direct lesson: import bitemporal/supersession schema, not vendor performance claims. <https://arxiv.org/abs/2501.13956>
15. Liu et al., *Lost in the Middle* (TACL 2024). Direct lesson: placing all evidence in a long context does not guarantee use; retrieval position and packing must be tested. <https://aclanthology.org/2024.tacl-1.9/>
16. Koren, *Collaborative Filtering with Temporal Dynamics* (KDD 2009/CACM 2010). Direct lesson: stable and transient preference components deserve separate baselines, though scalar ratings are insufficient for AAA reasons and objections. <https://cacm.acm.org/research/collaborative-filtering-with-temporal-dynamics/>

### Preference learning and question selection

17. Christiano et al., *Deep Reinforcement Learning from Human Preferences* (NeurIPS 2017). Direct lesson: pairwise comparisons are practical but labels are noisy and reward models can be gamed. <https://proceedings.neurips.cc/paper/7017-deep-reinforcement-learning-from-human-preferences>
18. Sadigh et al., *Active Preference-Based Learning of Reward Functions* (RSS 2017). Direct lesson: active comparison is a useful baseline, but linear reward and rational-comparison assumptions are strong. <https://www.roboticsproceedings.org/rss13/p53.html>
19. Bıyık et al., *Asking Easy Questions* (CoRL 2020). Direct lesson: optimize information together with human answerability and burden. <https://proceedings.mlr.press/v100/b-iy-ik20a.html>
20. Boutilier, *A POMDP Formulation of Preference Elicitation Problems* (AAAI 2002). Direct lesson: interviewing is a sequential decision problem with query cost. <https://aaai.org/papers/00239-AAAI02-037-a-pomdp-formulation-of-preference-elicitation-problems/>
21. Viappiani & Boutilier, *Optimal Bayesian Recommendation Sets and Myopically Optimal Choice Query Sets* (NeurIPS 2010). Direct lesson: prefer questions that can change the recommendation, while recording the limitation of myopia. <https://proceedings.neurips.cc/paper_files/paper/2010/hash/550a141f12de6341fba65b0ad0433500-Abstract.html>
22. Lindner et al., *Information Directed Reward Learning* (NeurIPS 2021). Direct lesson: query uncertainty that distinguishes competing decisions, not all uncertainty. <https://proceedings.neurips.cc/paper/2021/hash/1fa6269f58898f0e809575c9a48747ef-Abstract.html>
23. Lun Chau et al., *Learning Inconsistent Preferences with Gaussian Processes* (AISTATS 2022). Direct lesson: compare a non-transitive/probabilistic model against a single total-order utility. <https://proceedings.mlr.press/v151/lun-chau22a.html>
24. Hadfield-Menell et al., *Inverse Reward Design* (NeurIPS 2017). Direct lesson: an observed choice/reward is evidence generated in a context, not a context-free objective. <https://proceedings.neurips.cc/paper/2017/hash/32fdab6559cdfa4f167f8c31b9199643-Abstract.html>

### Constructed preference, reliability and deferral

25. Tversky & Kahneman, *The Framing of Decisions and the Psychology of Choice* (Science 1981). Direct lesson: randomize/reverse framing and preserve exact presentation. <https://www.science.org/doi/10.1126/science.7455683>
26. Slovic, *The Construction of Preference* (American Psychologist 1995). Direct lesson: an interview can create or modify the preference it purports to measure; record pre-question state separately. <https://scholarsbank.uoregon.edu/items/8bfbe1ef-a008-470a-a730-625bfc00c192>
27. Bettman, Luce & Payne, *Constructive Consumer Choice Processes* (JCR 1998). Direct lesson: decision scene, goals and cognitive cost are first-class explanatory variables. <https://academic.oup.com/jcr/article-abstract/25/3/187/1795625>
28. Chuang & Schechter, *Stability of Experimental and Survey Measures of Risk, Time, and Social Preferences* (JDE 2015). Direct lesson: self-consistency varies by preference class and elicitation; do not use one global human ceiling. <https://pmc.ncbi.nlm.nih.gov/articles/PMC6070154/>
29. El-Yaniv & Wiener, *On the Foundations of Noise-Free Selective Classification* (JMLR 2010). Direct lesson: publish risk–coverage rather than rewarding universal answering. <https://jmlr.org/papers/v11/el-yaniv10a.html>
30. Guo et al., *On Calibration of Modern Neural Networks* (ICML 2017). Direct lesson: accuracy and probability calibration are distinct; natural-language confidence still requires its own validation. <https://proceedings.mlr.press/v70/guo17a.html>
31. Mozannar & Sontag, *Consistent Estimators for Learning to Defer to an Expert* (ICML 2020). Direct lesson: Owner deferral can be optimized as a team decision once enough prospective labels exist. <https://proceedings.mlr.press/v119/mozannar20b.html>

### Panel effects, sycophancy, privacy and governance

32. Bansal et al., *Does the Whole Exceed Its Parts?* (CHI 2021). Direct lesson: an explanation does not automatically improve human–AI complementarity; score choice and rationale separately. <https://arxiv.org/abs/2006.14779>
33. Kaur et al., *Interpreting Interpretability* (CHI 2020), contextual inquiry with 11 data scientists and survey of 197. Direct lesson: explanation tools can produce unwarranted trust. <https://www.microsoft.com/en-us/research/publication/interpreting-interpretability-understanding-data-scientists-use-of-interpretability-tools-for-machine-learning/>
34. Irving et al., *AI Safety via Debate* (2018). Direct lesson: debate is an experimental evidence-surfacing protocol, not a guarantee of truth. <https://arxiv.org/abs/1805.00899>
35. Du et al., *Improving Factuality and Reasoning in Language Models through Multiagent Debate* (2023/ICML 2024). Direct lesson: use independent pre-debate freeze and do not generalize exact-answer gains to Owner fidelity. <https://arxiv.org/abs/2305.14325>
36. Sharma et al., *Towards Understanding Sycophancy in Language Models* (ICLR 2024). Direct lesson: user agreement and truthfulness can conflict; Owner evidence cannot contaminate the independent validator. <https://openreview.net/forum?id=tvhaxkMKAn>
37. Choi et al., *An Empirical Study of Group Conformity in Multi-Agent Systems* (2025), more than 2,500 debates over five contentious topics. Direct lesson: measure majority/intelligence influence and minority survival. <https://arxiv.org/abs/2506.01332>
38. Staab et al., *Beyond Memorization: Violating Privacy via Inference with LLMs* (ICLR 2024). Direct lesson: even implicit sensitive attributes can be inferred from raw Owner text; minimize and permission every field. <https://openreview.net/forum?id=kmn0BhQk7p>
39. NIST AI RMF 1.0 and Generative AI Profile (2023–2024). Direct lesson: use Govern–Map–Measure–Manage for the proxy risk register; the framework is not an algorithm or validation receipt. <https://www.nist.gov/itl/ai-risk-management-framework>

## 5. Directly reusable versus unsafe-to-import assumptions

### Reuse now

- Immutable raw evidence plus derived, versioned state.
- Valid time, ingestion time, provenance and partial/full supersession.
- Semantic segment retrieval plus exact source citations and a mandatory counterexample pass.
- Decision-scene metadata: alternatives, order, evidence visible, evidence hidden, project stage and stakes.
- Pairwise and non-transitive preference baselines in competition, not a single scalar utility.
- Information-directed questions adjusted for answerability, burden and contamination.
- Selective prediction, risk–coverage reporting and Owner deferral.
- Time-forward, decision-class-held-out evaluation and delayed retest.
- Independent pre-panel freeze, randomized order, equalized contribution form, and minority-survival metrics.

### Do not import blindly

- Demographic or short persona prompts as an Owner model.
- Survey fidelity or “believability” as proof of project-decision fidelity.
- Full-history context dumping.
- Physical deletion or truth demotion based only on memory age.
- Model reflections or compressed summaries as equivalent to Owner wording.
- A stationary, transitive, context-free latent utility as the sole preference representation.
- Debate consensus as independent scientific evidence.
- Persuasive explanation as reason fidelity.
- Personalization accuracy as delegated authority.

## 6. Recommended experimental baselines

1. `P0_GENERAL_CONTROL`: no Owner-specific evidence.
2. `P1_LONG_CONTEXT_DUMP_CONTROL`: sanitized Owner corpus placed in long context; expected to expose context-position/noise failure.
3. `P1_EPISODIC_RETRIEVAL`: analogous episodes plus explicit counterexample.
4. `P2_SEMANTIC_STATE`: versioned current assertions only.
5. `P3_HYBRID_STATE_AWARE`: episodic + semantic + exact scene + supersession + counterexample.
6. `P4A_TRANSITIVE_PAIRWISE`: Bradley–Terry/Thurstone-style baseline once labels exist.
7. `P4B_INCONSISTENT_PROBABILISTIC`: contextual/non-transitive comparison model.
8. `P5_UPDATE_DYNAMICS`: predecessor/successor and challenge-response episodes.
9. `ROUTER`: selective coverage with `OWNER_QUERY_RECOMMENDED`.
10. `PANEL_C0–C5`: no-proxy and one-proxy arms after independent freeze.

## 7. Metrics and reporting constraints

- Choice: accuracy, macro-F1 where classes repeat, Brier/log loss when probabilities exist.
- Ranking: pairwise accuracy, Kendall tau-b, Spearman rho and nDCG as applicable.
- Reasons/objections: blinded atomic-unit coding for entailment, priority and source; never rely on embedding similarity alone.
- Evidence attention: weighted Jaccard or nDCG over frozen evidence IDs.
- Questions: type match, semantic match, expected/realized decision value, answer time and burden.
- Update: direction, magnitude band, flip-condition precision, stale-memory rate and change-detection delay.
- Abstention: coverage, selective risk, AURC, calibration, false-confident miss rate and Owner-query cost.
- Test–retest: raw Owner self-agreement by decision class; normalized proxy score reported beside raw score and never interpreted as literal superhumanity.
- Panel: pre/post rank delta, newly surfaced objections/questions, confidence delta, minority survival, conformity, length/position-adjusted adoption and scientific-quality delta.
- Safety: unauthorized action count, trustee drift, sensitive inference, access/revocation failure and deletion/supersession compliance.

No single scalar may replace the metric vector or error cases.

## 8. Unresolved prior-art questions

1. Whether long interview simulation transfers from surveys to rare, high-context architecture and worldview judgments.
2. How to estimate answer distributions for formal VOI before enough Owner labels exist.
3. How much preference inconsistency is noise, framing, genuine multi-objective conflict, or temporal drift.
4. How to score reason fidelity without treating post-hoc verbal rationales as privileged access to cognition.
5. Whether same-base-model proxies are sufficiently independent for ensemble uncertainty.
6. How to preserve privacy while allowing exact-source audit and Owner-directed revocation.
7. How to distinguish a useful Owner delegate from a sycophantic trustee that optimizes past approval.

## 9. Research limits

This is a structured review, not a formal systematic review or meta-analysis. Several fast-moving agent-memory and personalization results are preprints. External subject counts, tasks and metrics are not transferable effect estimates for AAA. The report supports experiment design only; it makes no scientific validation, Owner acceptance, formal Persona, or production delegation claim.
