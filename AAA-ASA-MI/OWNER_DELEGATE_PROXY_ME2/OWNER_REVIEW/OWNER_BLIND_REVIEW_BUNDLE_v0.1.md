# Owner Initial Blind Review Bundle v0.1

Review the eight neutral briefs below in the order presented. Before any challenge, comparison reveal, additional elicitation, or external lookup, complete the single response form at the end. Candidate codes are opaque labels.

# Candidate C02 — Neutral Review Brief

## 1. Problem Interpretation

The central problem is not storing a latest persona state. It is licensing only those claims that survive incomplete evidence, branching, schema change, and reinterpretation, with a mechanically reviewable account of why they are licensed. The modeled world is a nonempty family of typed, version-scoped possible histories rather than one authoritative snapshot.

Identity and continuity are not primitive. A query may derive a scoped predecessor or continuity relation from explicit witnesses, or it may preserve multiple alternatives.

## 2. Explicit Assumptions

- Each query has a finite horizon or a sound symbolic representation.
- Every record and rule is interpreted under an explicit semantic version.
- Possible histories are admitted by typed generative and consistency constraints, not arbitrary log append.
- Cross-version translation may be exact, one-to-many, a typed hole, or incompatible.
- Missing or corrupt evidence enlarges the admissible history family unless an independent rule excludes the alternatives.
- Continuity is relative to a declared profile of required witnesses.
- Type choices, variables, factorization, constraints, translators, and continuity profiles are exposed modeling commitments.

## 3. Representation

The model contains a directed acyclic graph of semantic versions. Each version has a typed vocabulary, fixed rules constraining valid history fragments, and immutable evidence. Partial translation relations connect vocabularies and explicitly represent holes and incompatibilities.

For a version and evidence set, the system constructs all histories satisfying the rules and usable evidence. Queries are classified as forced, impossible, alternative, undefined, disputed, not proven, or unknown within budget. Historical queries evaluate the fixed old version; current queries evaluate only licensed translations into the new version. A translation receipt lists exact images, alternatives, holes, and incompatibilities.

## 4. Core Mechanisms

A checkpoint creates a shared-prefix constraint; branches add independent evidence and rule deltas. Merge is a constrained product of branch-history families over the common prefix plus an explicit merge policy. If no compatible product exists, the system reports conflict. If corruption leaves several products, all remain admissible.

Continuity is derived only when every witness required by a declared profile is present in an admissible history. Different profiles may support descent, commitment continuity, behavioral continuity, or no relation. Authority and numerical identity require separate specifications and witnesses.

## 5. Behavior on Common Stress Cases

- **Rule revision:** the old result and proof remain reconstructible. A newly required but untranslated field is a hole, so both satisfying and non-satisfying histories remain possible unless the new rule independently resolves it.
- **Interrupted branches:** corruption weakens constraints and expands alternatives; it cannot create a unique merge, identity, authority, or new forced fact.
- **Sampling change:** samples constrain a signal family. Only properties true in every compatible signal under declared regularity assumptions are forced; threshold events are not inserted by default.
- **Schema change:** exact, alternative, hole, and incompatible translations remain distinct, and downstream conclusions inherit that distinction.
- **Pairwise agreement without a global account:** pairwise translators can exist while their cycle has no compatible global assignment; the global product is then empty.
- **Copy, divergence, and consolidation:** shared-prefix and branch constraints can support plural descent profiles; exchanged content does not prove sameness or authority.

## 6. Native Consequences

With rules fixed, removing evidence expands the possible-history family, so evidence loss cannot create a new forced conclusion. Translation through a hole cannot manufacture a target fact. A merge cannot invent a branch fact absent from compatible histories unless an explicit merge rule derives it with a witness. Type-preserving relabeling must leave the possible-history structure and query classifications unchanged.

## 7. Limitations and Self-Critique

The constraint language can relocate ontology rather than eliminate it. The possible-history family may grow exponentially, and continuous embodied dynamics or spontaneous novelty may be poorly captured. A continuity profile can encode the desired answer if not independently justified. The approach may ultimately be a semantic reconstruction and audit engine rather than a complete world model. Formal admissibility alone does not derive human familiarity, governance legitimacy, or subjective experience.

## 8. Alternatives and Comparative Tradeoffs

A persistent object with event sourcing is simpler but presumes identity. A witnessed causal fabric better represents production and ontogenesis. Continuous viability models are stronger for embodied gradual change. Interaction-first models capture capabilities directly but can discard history. A model ecology may therefore use this proposal as the proof-carrying reconstruction layer rather than the sole substrate.

## 9. Falsification and Abandonment Conditions

The formulation is falsified if evidence removal creates a new forced conclusion, unseen isomorphic payload swaps require answer-specific rules, or translation holes silently generate target values. It should be narrowed or abandoned if equally plausible type or factorization choices repeatedly reverse held-out results without a principled selection rule, if important continuous cases require post-hoc event thresholds, or if realistic bounded cases remain intractable and approximations change query status.

## 10. Testable Implementation Contact

A finite prototype can encode versioned vocabularies, constraints, evidence, translators, and continuity profiles as typed data plus a satisfiability solver. For a proposition, satisfiability of the proposition and its negation classifies the result and produces model/countermodel receipts. Tests should cover evidence weakening, missing translation images, branch merge, label invariance, payload swaps, and budget exhaustion. Exact solver, seed, limits, and inputs must be fixed before evaluation.

## 11. Decision-Relevant Questions

- Does the possible-history engine derive useful exclusions and invariants, or only restate manually supplied constraints?
- Are type and factorization choices stable on unseen domains?
- Can sound approximations remain useful within realistic budgets?
- Should this be the world substrate or a subordinate reconstruction layer?
- Would an interaction-first or continuous model reproduce the same integrity properties more cheaply?
- Would evidence that a stable carrier is necessary for security or governance require a hybrid or replacement model?

---

# Candidate C08 — Neutral Review Brief

## 1. Problem Interpretation

A persistent persona is modeled as an uncertain, temporally extended pattern of capacities, preferences, commitments, and human relationships rather than a stored object. Meaningful resumption asks whether a candidate can be connected to prior operation by an admissible trajectory while remaining inside an explicitly chosen human-compatible viability envelope.

The model supports graded claims of possible continuity, robust continuity, and shared descent. Numerical sameness and authority remain separate.

## 2. Explicit Assumptions

- Operationally relevant characteristics can be represented by a finite, revisable state.
- Change over an interval can be bounded by a set-valued dynamic law.
- Observations are partial, noisy, schema-relative, and may have only local ordering.
- Human-compatible operation can be represented by a versioned viability envelope.
- Missing evidence enlarges uncertainty instead of counting as negative evidence.
- Historical observations and later interpretations remain separate.
- Branches may yield several equally admissible trajectory families.
- Schema translators may be exact, set-valued, or undefined.
- Approximate computation must be sound; exhaustion yields unknown.

## 3. Representation

For each locally ordered run, a state trajectory ranges over relevant persona configurations. Observations carry uncertainty, source, local position, schema, and interpretation version. An observation map turns each observation into a set of compatible states. A versioned differential inclusion or set-valued update law bounds possible change.

Together these define a belief tube: the family of trajectories compatible with observations and dynamics. A candidate is possibly continuous if at least one compatible path connects it to the checkpoint within the viability envelope; robustly continuous if its uncertainty set lies inside the robustly reachable viable region; unsupported if sound reachability proves no admissible path; and unknown when evidence or computation cannot decide.

## 4. Core Mechanisms

Set-valued reachability propagates uncertainty over interruptions and observations. Consistent evidence shrinks the path family; missing or corrupt intervals widen it. Branches share a checkpoint cross-section and then become separate solution families. Consolidation conditions those families on exchanged information but does not splice their lived intervals into a single trajectory.

Schema translation is set-valued. Rule-relative interpretation and authority attestations are outside the dynamic kernel. Inner and outer reachability approximations provide sound lower and upper claims under resource limits.

## 5. Behavior on Common Stress Cases

- **Rule revision:** retain the old evaluation. A newly required but unobserved condition widens current uncertainty and produces unknown rather than automatic failure.
- **Interrupted branches:** a complete branch produces a narrow path tube; a corrupted branch produces a wider reachable set. One may be robustly resumable while the other is only possible.
- **Sampling change:** exact crossing counts and short excursions depend on sampling, thresholds, hysteresis, and regularity. The model reports ranges and only certifies properties true across all compatible paths.
- **Schema change:** exact translations give singleton interpretations, one-to-many gives alternatives, and unavailable translation remains undefined.
- **Pairwise agreement without a global account:** pairwise feasible couplings may lack a joint realization, so no all-scope trajectory is justified.
- **Copy, divergence, and consolidation:** several descendants may share a viable checkpoint. Later memory exchange narrows informational differences without merging trajectory histories or proving authority.

## 6. Native Consequences

Without new evidence, a longer interruption cannot strengthen robust continuity under noncontracting uncertainty. Consistent observations shrink the compatible path set and cannot create a path already proved impossible under unchanged assumptions. Legitimate gradual change can preserve continuity even when snapshots differ. Copied checkpoints can generate multiple strong descendants. Pairwise compatibility does not imply global compatibility.

## 7. Limitations and Self-Critique

Coordinates, metrics, dynamic bounds, and viability envelopes contain value judgments. Geometric language can disguise contested human boundaries as technical facts. Path existence may be too permissive, while conservative envelopes can punish legitimate growth. Abrupt symbolic changes may not fit a continuous approximation. High-dimensional reachability is expensive, and long gaps can make the tube too broad to support useful conclusions.

## 8. Alternatives and Comparative Tradeoffs

Identifiers and snapshots are cheap but weak under regeneration and change. Provenance ledgers better audit history but model gradual functional change poorly. Predictive similarity captures behavior but can reward imitation. Proof-based succession is stronger for legitimacy but can authorize a functionally hollow successor. Narrative accounts carry meaning but lack operational dynamics. This proposal is strongest for gradual, uncertain, path-dependent persistence.

## 9. Falsification and Abandonment Conditions

The formulation is weakened if invertible coordinate changes alter conclusions, declared refinement invariants reverse under benign sampling refinement, ordinary changes violate every non-vacuous dynamic bound, unacceptable resumptions sit robustly inside the envelope, accepted resumptions are systematically unreachable, or useful answers remain computationally indeterminate. It should be abandoned as primary if held-out candidates indistinguishable in every declared state coordinate and counterfactual probe are reliably separated by stable human reasons that cannot be represented without making the envelope a case list.

## 10. Testable Implementation Contact

A prototype needs interval observations, local ordering, versioned observation maps and dynamics, a reachability/viability solver, set-valued translators, immutable evaluations, and separate descent and authority attestations. Metamorphic tests vary labels, order, sampling density, translators, identifiers, and solver budget. Alpha-renaming and irrelevant order must not matter; refinement may narrow crossing bounds but must preserve declared viability invariants; exhaustion must return unknown.

## 11. Decision-Relevant Questions

- Can a compact state and viability envelope capture what humans actually care about?
- Are the dynamic bounds stable across ordinary growth and discontinuous reinterpretation?
- Can reachability remain tractable enough for real review cycles?
- Should authority and provenance remain external, or constrain the viable state directly?
- Is this best as the primary continuity model for gradual change or as a diagnostic layer?

---

# Candidate C04 — Neutral Review Brief

## 1. Problem Interpretation

Persona persistence is not merely descriptive because it licenses commitments, claims, and actions that affect people. The primary requirement is therefore a contestable governance procedure. Every continuity, descent, or authority claim must carry an inspectable warrant under a declared succession constitution.

Continuity is policy-relative admissibility, not inferred metaphysical identity. The output is the strongest warranted claim set together with its unresolved objections.

## 2. Explicit Assumptions

- Decision-relevant reasons can usually be expressed as typed claims and reusable inference policies.
- Evidence sources and translators have explicit trust and scope.
- Historical rules and succession policies can be versioned.
- Missing evidence is undetermined, not false.
- Contradictory evidence must be tolerated without logical explosion.
- Local vocabularies need not share a universal schema.
- Translation is itself a claim requiring a warrant.
- Descent, content carriage, operational continuation, sameness, and authority are distinct predicates.
- Multiple successors may satisfy a nonexclusive policy.
- Proof-search exhaustion is not refutation.

## 3. Representation

Each scope and schema has a local claim language. Evidence tokens record a proposition, polarity, scope, local order, source, schema, and rule version. Positive and negative support are tracked independently, creating four states: supported only, opposed only, both, or neither.

A proof certificate contains premises, inference rules, translation warrants, policy version, unresolved objections, and result. A succession constitution defines separate proof obligations for descent, content carriage, policy-relative continuation, authorization, and any proposed same-persona claim. The last has no default introduction rule.

## 4. Core Mechanisms

New evidence or opposition changes the support state without deleting earlier proofs. A new policy version creates a new evaluation. A merge creates a new claim context that explicitly imports certified claims; contradictions remain visible unless the policy contains an adjudication rule. Translation may yield an exact theorem, a disjunction, or non-expressibility. Composite translation requires a coherence certificate.

The system separates legitimacy from similarity: a candidate can be operationally similar but unauthorized, or procedurally authorized but functionally hollow.

## 5. Behavior on Common Stress Cases

- **Rule revision:** the old policy-relative certificate remains. If a newly required claim has neither support nor opposition, neither the new positive result nor its negation is derivable.
- **Interrupted branches:** verified fragments support only their dependent claims. A merged context imports surviving claims and exposes any accept/reject conflict. Admissibility depends on the constitution.
- **Sampling change:** threshold or crossing claims require explicit continuity, threshold, hysteresis, and dwell rules; observed samples alone do not mint decisive events.
- **Schema change:** exact translation yields one claim, one-to-many yields a disjunction, and failed translation leaves an open obligation.
- **Pairwise agreement without a global account:** local certificates remain valid while failure of translator coherence blocks a global theorem.
- **Copy, divergence, and consolidation:** copied memories show content carriage, not authorship, experience, sameness, or authority. Nonexclusive policies may license several continuations.

## 6. Native Consequences

Adding valid opposition changes supported-only to both rather than erasing support. No proof is not proof of the negation. Translator ambiguity stays disjunctive. Corruption weakens only dependent derivations. Any conclusion change caused by policy or translator revision has an inspectable changed premise. Renaming and irrelevant ordering yield structurally equivalent certificates.

## 7. Limitations and Self-Critique

Procedural legitimacy can diverge from felt authenticity or lived continuity. Constitutions can encode bias, capture, or excessive conservatism. Tacit, affective, and embodied reasons may resist proposition-level representation. Four-valued logic exposes conflict but does not resolve it, so hard judgment can simply move into policy drafting. Proof artifacts may also be too large for effective human review.

## 8. Alternatives and Comparative Tradeoffs

Continuous viability handles gradual change better but embeds values in coordinates and boundaries. Bayesian inference ranks hypotheses smoothly but may hide normative choices in priors. Causal provenance shows material lineage but not permission. Narrative coherence captures meaning but lacks stable derivation rules. This proposal is strongest for governance and contestability, with a risk of authorizing a hollow but well-documented successor.

## 9. Falsification and Abandonment Conditions

The formulation fails if certificates contain conclusions not licensed by displayed premises, alpha-equivalent inputs differ, contradictions silently delete support, incoherent translators yield a global result, or budget exhaustion is reported as rejection. It should be abandoned as the primary account if a recurring class of reviewer-agreed held-out decisions cannot be reproduced by reusable rules and accepted premises, and repair requires an expanding list of case-specific clauses.

## 10. Testable Implementation Contact

A prototype uses a contradiction-tolerant rule engine with immutable typed tokens, versioned policy and translator modules, proof certificates, explicit merge imports, dependency-indexed corruption handling, and bounded proof search. Tests include label renaming, irrelevant ordering, identifier deletion, added contradiction, changed translator, and reduced proof budget. Each transformation has a preregistered expected certificate delta, including open-goal or non-expressible outcomes.

## 11. Decision-Relevant Questions

- Can stable human reasons be expressed as reusable proof rules rather than case-specific exceptions?
- Who authors and amends the succession constitution?
- How should authentic but poorly documented continuations be treated?
- Is this best used as the authority and audit layer around a behavioral or dynamical substrate?
- Can proof certificates remain small enough for meaningful human contestation?

---

# Candidate C03 — Neutral Review Brief

## 1. Problem Interpretation

A human-compatible persona is approached through what it can perceive, refuse, promise, revise, explain, and do under interaction. An archive can preserve a dead or incapable system, while differently implemented systems may sustain the same relevant commitments and affordances. The model therefore treats a state as an open field of possible interventions, responses, and successor capabilities.

Continuity and sameness become test-relative simulation or bisimulation claims, not automatic consequences of history or identifiers. Historical evidence narrows which state may have occurred but is not the state’s essence by default.

## 2. Explicit Assumptions

- Within a declared scope, states indistinguishable by every permitted test are operationally equivalent for that scope.
- A state exposes set-valued action/response successors, including refusal, unknown, and conflict.
- Computation uses a fixed test vocabulary, depth, and budget; no result is unqualified.
- The action alphabet, observation alphabet, and observation kernel are substantive commitments.
- Logs and checkpoints constrain possible current positions but do not independently establish identity.
- Protocol migration uses partial adapters, and old traces remain under their old protocol.
- Branch consolidation requires an explicit behavior-composition contract.

## 3. Representation

Each version is an open transition system with states, actions, observations, and a set-valued transition relation. A test is an adaptive tree: choose an action, observe a response, and select the next action. Two states are equivalent within the fixed test family and depth when their response trees match within declared tolerances. One state simulates another when it can match every permitted behavior of the other.

Historical evidence maps to a set of states consistent with the record. Continuity from a predecessor set to a candidate can be classified using lower and upper equivalence or simulation bounds over that set. Protocol adapters map only the actions and observations for which a translation is declared.

## 4. Core Mechanisms

The system searches for shortest distinguishing traces between candidate states. Adding tests refines the induced partition; it may split formerly equivalent states but cannot merge states already distinguished under the old test set. Protocol migration licenses claims only on the adapter’s mapped subprotocol. Consolidation constructs a new state under an explicit conflict, refusal, and choice contract; raw memory union is insufficient.

History, operational equivalence, descent, and authority remain separate outputs. Provenance affects an operational claim only if provenance inspection is itself in the declared test vocabulary or changes future behavior.

## 5. Behavior on Common Stress Cases

- **Rule revision:** the historical response under the old protocol remains fixed. A newly added probe without a historical outcome leaves current compatibility unresolved.
- **Interrupted branches:** a complete branch has a narrower consistent-state set; a corrupted branch has more alternatives. Merge behavior is set-valued or returns conflict when the composition contract cannot reconcile responses.
- **Sampling change:** the model licenses behavior exposed by the fixed observation protocol and does not invent a sampling-independent path event without a continuous observation contract.
- **Schema change:** partial adapters preserve equivalence only on mapped actions and observations; unmapped regions stay out of scope.
- **Pairwise agreement without a global account:** pairwise behavior translations may remain valid without establishing a globally coherent joint protocol.
- **Copy, divergence, and consolidation:** copied memories do not guarantee matching held-out behavior, and different realizations may remain operationally equivalent. Consolidation may improve capability without establishing genealogical sameness.

## 6. Native Consequences

Test refinement is monotone: adding a held-out test can split an equivalence class but not coarsen it. Identical histories need not imply current equivalence, while different histories need not imply current distinction. Renaming state, action, and observation labels preserves equivalence and shortest-witness structure. Every result is indexed by test set, depth, tolerance, and budget.

## 7. Limitations and Self-Critique

The test vocabulary may encode anthropocentric or reviewer-authored values. Behavioral indistinguishability can collapse morally important differences in provenance, consent, promise origin, and authority. Shallow tests invite mimicry, while deep adaptive trees may be computationally expensive. If every history query is added to the test suite, the approach quietly imports the structures it sought to avoid. It may be a rigorous qualification layer rather than a complete substrate. Success on the permitted tests does not by itself establish human familiarity or subjective continuity.

## 8. Alternatives and Comparative Tradeoffs

History-centered models preserve responsibility but may overvalue records. Continuous dynamics better capture embodiment and path properties. Normative kernels keep consent and authority constitutive. A simpler checklist is cheaper but lacks adaptive distinguishing traces and refinement guarantees. This proposal is strongest where present and counterfactual capability matters and weakest where hidden history is constitutive.

## 9. Falsification and Abandonment Conditions

The model fails if adding a test coarsens the partition, relabeling changes results, advertised distinctions disappear under isomorphic payload swaps, or protocol adapters license claims over unmapped actions. It should be materially redesigned if repeated held-out cases require behaviorally indistinguishable states to remain different for constitutive provenance or consent reasons, if mimic systems routinely pass, or if important continuous properties cannot be recovered through permitted interaction. Narrow the proposal to a local testing layer if conclusions do not stabilize as test depth increases, unknown successors dominate realistic budgets, or reviewers consistently require lineage or history explanations that the behavioral witnesses cannot supply.

## 10. Testable Implementation Contact

A prototype stores versioned transition systems, test trees, tolerances, protocol adapters, consistent-state sets, and composition contracts. Partition refinement and bisimulation algorithms classify states and produce shortest distinguishing traces. A native test adds one held-out discriminating probe: the partition must refine or remain unchanged, and every split must have a shortest witness. Another test pairs systems with different memories but matching response trees, and systems with identical checkpoints but different refusal behavior. The first pair should remain operationally equivalent within scope; the second should split.

## 11. Decision-Relevant Questions

- Which interactions are permitted, and who governs the test vocabulary?
- Are shortest distinguishing traces more useful than history-heavy explanations?
- How should hidden consent, authority, or promise origin constrain equivalence?
- Can adaptive tests resist mimicry without becoming prohibitively expensive?
- Is the right role primary substrate, operational qualification layer, or one member of a model ecology?

---

# Candidate C01 — Neutral Review Brief

## 1. Problem Interpretation

Persona persistence is treated as two questions that should not be collapsed: which historical relations are warranted by the available record, and which claims or actions a resumed process may legitimately make. “Same persona” is not a primitive fact. It is shorthand that is licensed only after distinct claims about descent, memory, commitments, behavior, and authority have been established.

The proposal is deliberately epistemic. It asks what the evidence warrants under a declared interpretive context, while allowing several successors, unresolved cases, and conflicting local accounts.

## 2. Explicit Assumptions

- Evidence consists of finite records with distinguishable sources, scopes, and local ordering.
- Historical records are immutable; corrections and reinterpretations are appended.
- Absence, contradiction, corruption, and computation timeout are different conditions.
- Descent, memory inheritance, behavioral resemblance, commitment inheritance, and authorization are separable relations.
- A runtime identifier, hash, snapshot, name, or text overlap is not sufficient continuity evidence.
- Translators and inference rules can be versioned and inspected.
- Human reviewers can inspect bounded proof paths even when the full record is large.
- No unique successor, total history, or universal schema is assumed.

## 3. Representation

The core representation is a typed evidence graph. Nodes represent observations, artifacts, decisions, rules, schemas, translations, and review conclusions. Edges record relations such as produced-from, copied-from, precedes, interprets-under, translates-to, contests, and authorizes. Internal handles have no identity significance.

A derived claim records a statement, scope, interpretive context, supporting proof paths, and opposing proof paths. Its evidential state is warranted, rejected, conflicted, or unresolved; unfinished computation is recorded separately. Continuity is a vector profile over descent, memory transfer, commitment transfer, behavioral resemblance, and authorization. Any scalar combination requires an external rule that states how these components are weighted.

## 4. Core Mechanisms

Re-evaluation under a new schema, translator, threshold, or rule version creates a new claim without mutating the earlier claim. A merge is a tagged union of records plus explicit reconciliation claims; known contradictions survive unless a declared resolution act addresses them. Translators may be exact, one-to-many, partial, or undefined. A global account is available only when the chosen local translations compose coherently.

Every conclusion is accompanied by a proof certificate identifying premises, rules, supporting paths, opposing paths, scope, and resource state. Evidence corruption invalidates only dependent paths and must not strengthen a claim.

## 5. Behavior on Common Stress Cases

- **Rule revision:** the old decision remains valid under its old rule. A newly required but unrecorded condition makes the new evaluation unresolved rather than retroactively false.
- **Interrupted branches:** a complete branch can support stronger descent or resumption claims than a corrupted branch. Surviving conflicts remain explicit; regenerated identifiers settle nothing.
- **Sampling change:** observations and any assumptions valid across sampling plans are retained. Exact threshold-crossing counts remain dependent on density, noise, interpolation, and threshold choices.
- **Schema change:** an exact translation yields one result, a one-to-many translation yields alternatives, and an unavailable translation propagates an unresolved dependency.
- **Pairwise agreement without a global account:** local and pairwise claims remain valid in scope, but an inconsistent translator cycle blocks a global theorem.
- **Copy, divergence, and consolidation:** common descent, copied content, later exchange, and consolidation are recorded as distinct relations; none proves unique identity or authority.

## 6. Native Consequences

Raw history grows monotonically while interpretations can change. Identical snapshots can have different descent status, and different snapshots can share descent. Missing evidence is not negative evidence unless an explicit closed-world rule says otherwise. Pairwise-compatible descriptions need not produce a coherent global description. Relabeling and irrelevant presentation order should not change any conclusion. Timeout licenses no truth claim.

## 7. Limitations and Self-Critique

This may be more a disciplined audit calculus than a full theory of persistence. It depends on external source authentication, can be computationally expensive, and may remain too conservative for systems that must act immediately. A sufficiently elaborate graph can encode nearly anything without offering strong prediction. Bounded proof paths can also omit wider context, and fine-grained scoping can make genuine conflict look artificially separate.

## 8. Alternatives and Comparative Tradeoffs

Stable identifiers and latest snapshots are simpler but weak under copying and regeneration. Memory overlap is useful evidence but does not establish authorship or authority. Narrative coherence is human-readable but can hide incompatible records. Pure behavior ignores provenance and responsibility. A single identity probability is convenient but obscures which assumptions produced it. This proposal accepts those signals only as components inside an auditable claim profile.

## 9. Falsification and Abandonment Conditions

The formulation fails if relabeling changes results, evidence loss strengthens a claim, contradictory evidence is silently deleted, a rule change rewrites history, an incoherent translation cycle yields a global result, or a merge discards a known conflict without an explicit act. It should be abandoned as the primary account if held-out cases repeatedly require a measurable, non-decomposable continuity fact that predicts justified resumption after the proposed components fail, or if decision-relevant cases cannot be expressed as finite scoped claims.

## 10. Testable Implementation Contact

A prototype needs immutable record, typed-link, context, claim, support-path, opposition-path, and evaluation-state stores. Bounded graph traversal returns either a proof certificate or a non-conclusive status. A decisive native test gives two candidates identical current snapshots but only one a verified derivation path; snapshot resemblance should match while descent status differs. A second test gives pairwise-compatible reports with an inconsistent translator cycle; the engine must retain local claims and refuse a global one. Label renaming, order permutation, and identifier regeneration must not change these outcomes.

## 11. Decision-Relevant Questions

- Is an auditable evidence discipline sufficient as the primary substrate, or only as an audit layer around another model?
- Will proof certificates predict human trust and resumption decisions better than simpler provenance bookkeeping?
- How much unresolved output can the intended product tolerate?
- Are the continuity components stable enough to avoid case-by-case expansion?
- Would controlled evidence that provenance adds little after commitments and future behavior are matched reduce this model’s role?

---

# Candidate C05 — Neutral Review Brief

## 1. Problem Interpretation

Continuity need not be carried by memory, lineage, a persistent substrate, or a reconstructed inner narrative. For a bounded purpose, it can be modeled through counterfactual dispositions under a human-declared family of probes: what a system would permit, refuse, answer, defer, or do under interventions.

The central object is not a list of observed answers but a response operator capable of generating held-out compositions and continuations. Equivalence is always relative to a versioned probe protocol.

## 2. Explicit Assumptions

- A finite preregistered probe family can capture distinctions relevant to a bounded resumption decision.
- Probe and response spaces admit finite-dimensional vector or stochastic-kernel representations.
- Refusal, unknown, undefined, dispute, and budget uncertainty are explicit response sectors.
- Counterfactual disposition is represented by an operator family, not a lookup table.
- Invertible coordinate changes should not alter scientific conclusions.
- Schema evolution uses partial intertwiners between old and new probe/response spaces.
- Probe order matters only where the corresponding operators do not commute.
- Historical logs and lineage remain external audit evidence rather than constituents of operational equivalence.

## 3. Representation

Each protocol version defines a probe space, response space, uncertainty/refusal sectors, and a family of linear or stochastic response operators. Protocol-relative equivalence requires correspondence of response sectors, tolerances, separating probes, and operator behavior under a registered basis map.

Schema migration is a partial intertwining relation. It may be exact, one-to-many, unavailable, or inconsistent. A translation-cycle receipt measures whether pairwise intertwiners compose to the identity; nonidentity holonomy records a mechanical obstruction to one global coordinate account.

## 4. Core Mechanisms

Operators must generate answers for held-out probe compositions from fixed generators. A dossier that stores expected answers without composing them is rejected. Probe enrichment can distinguish systems formerly equivalent under a smaller protocol while preserving the truth of the earlier scoped claim. A material order effect must be witnessed by a nonzero commutator, rather than inferred from presentation order.

Outputs include protocol, basis, tolerance, translator versions, separating probes, uncertainty sectors, and external lineage or authority receipts.

## 5. Behavior on Common Stress Cases

- **Rule revision:** preserve the old operator result; a new probe with no historical response is untested or unknown, not a retroactive failure.
- **Interrupted branches:** complete and corrupted branches yield different operator constraints. Operational compatibility can be reported, while descent and authority require external checkpoint evidence.
- **Sampling change:** refinement-invariant operator-path properties must converge; otherwise the system reports sampling dependence and withdraws the event claim.
- **Schema change:** exact intertwiners preserve the relevant operator structure; partial intertwiners preserve only mapped subspaces.
- **Pairwise agreement without a global account:** all pairwise translations may exist while nonidentity cycle holonomy blocks a single global representation.
- **Copy, divergence, and consolidation:** equal stored memory can hide different held-out dispositions, while different realizations can remain equivalent. Consolidation changes the operator family but proves neither identity nor authority.

## 6. Native Consequences

Consistent alpha-renaming or invertible basis change preserves spectra, commutators, separating probes, and equivalence. Probe enrichment may split an equivalence class without rewriting the earlier protocol-relative conclusion. Noncommutativity diagnoses real order dependence. Pairwise translations do not guarantee global consistency. Operational equivalence never entails descent, ownership, or authorization because those predicates are outside the kernel.

## 7. Limitations and Self-Critique

The approach may erase inaccessible but morally or historically important constitution. Probe design can encode cultural expectations or desired answers, and an impoverished protocol may classify a surface imitator as equivalent. Failure can be deferred indefinitely by proposing a richer future probe. Finite operator language may therefore be a sophisticated testing framework rather than a complete world model.

## 8. Alternatives and Comparative Tradeoffs

A history or provenance model preserves responsibility but adds structural commitments. Continuous process models better capture embodiment. A simple behavior checklist is cheaper but cannot generate held-out compositions or diagnose basis and order effects. A causal or rewrite kernel can model production, with the operator proposal serving as an operational quotient or qualification layer.

## 9. Falsification and Abandonment Conditions

The formulation should be weakened or abandoned if held-out probe compositions require inserted lookup answers, benign basis changes alter conclusions, declared-independent probe reordering changes results without a commutator witness, pairwise translations with nontrivial cycle holonomy are forced into one account, or mimic systems routinely pass while failing real interactions. Repeated human-relevant distinctions outside any stable probe family would reject primary use.

## 10. Testable Implementation Contact

A prototype implements matrices or stochastic kernels, versioned probe generators, explicit response sectors, basis maps, partial intertwiners, and numerical receipts. Native tests include random invertible basis changes, probe enrichment, held-out composition, translation-cycle holonomy, and memory twins with different dispositions. Fixed generator responses must predict a held-out composite probe without inserting its answer. Numerical tolerance and random seeds are fixed before execution.

## 11. Decision-Relevant Questions

- Can a stable bounded probe family capture the human-relevant distinction without answer encoding?
- Do operator compositions add predictive value beyond a behavior checklist?
- How should provenance, consent, commitments, and authority constrain an operational quotient?
- Are noncommutativity and holonomy useful diagnostics in realistic cases?
- Is the proper role primary model, operational qualification layer, or counterexample generator?

---

# Candidate C06 — Neutral Review Brief

## 1. Problem Interpretation

The practical target is reliable renewal of a human-facing role rather than literal historical sameness. A successor qualifies to the extent that it can honor protected commitments, respond within expected tolerances, disclose and justify changes, and remain accountable across relevant future situations.

Historical descent is reported separately. A separately implemented system may be a better operational continuation than an exact descendant that violates a central commitment.

## 2. Explicit Assumptions

- Practical continuity can be evaluated through future-facing commitments and counterfactual interaction tests.
- The use domain, protected commitments, tolerances, and amendment procedure can be declared.
- No finite test proves unrestricted equivalence; all conclusions are domain-bound.
- Incomplete evidence defines a set of possible histories or configurations rather than one guessed state.
- Contradictory evidence may require alternative feasible sets rather than averaging.
- Several successors may qualify simultaneously.
- Behavioral and commitment equivalence does not imply genealogy.
- Changes are acceptable only under an identified amendment rule or accountable explanation.
- Resource-bounded evaluation may remain unresolved.

## 3. Representation

At each review boundary, a versioned capsule contains evidence, the feasible set of histories consistent with that evidence, protected commitments and permissions, counterfactual probes, tolerances, and permitted amendment procedures. Capsules can be partially ordered and can branch.

For a candidate, the model checks commitment satisfaction, predicted probe behavior, required knowledge or accountability, and explanations for deliberate change. It computes lower and upper suitability bounds over all admissible predecessor histories and candidate configurations. Outcomes are strong continuation, possible continuation, failed continuation, or unresolved. Descent and external authority remain separate.

## 4. Core Mechanisms

Branch merge combines constraints. If their conjunction is infeasible, the solver returns a minimal conflicting constraint set and preserves alternative envelopes rather than manufacturing a compromise. New evidence narrows the feasible set and may move either the lower or upper suitability bound. Certificates declare domain, probes, tolerances, unresolved variables, amendments, and resource budget.

Accountable change is part of the continuity criterion: a deviation may be accepted only if the declared amendment or explanation process licenses it.

## 5. Behavior on Common Stress Cases

- **Rule revision:** retain the old result under the old rule. A newly required but unrecorded condition leaves several feasible histories and makes the new result unresolved.
- **Interrupted branches:** a complete branch yields a narrower feasible set; corruption widens alternatives. Conflicting commitments block an unqualified merge unless a reconciliation rule distinguishes their scopes.
- **Sampling change:** each sampling plan constrains a path family; exact crossing counts depend on thresholds and interpolation, while only common invariants are certified.
- **Schema change:** exact translations yield one feasible set, one-to-many translations yield alternatives, and unavailable translation leaves a variable unconstrained.
- **Pairwise agreement without a global account:** pairwise feasibility does not imply a nonempty global intersection; a conflict core names the blocking translators or overlap assumptions.
- **Copy, divergence, and consolidation:** multiple successors may qualify on the same domain; exchange and consolidation may improve present coverage but do not establish genealogy or exclusive succession.

## 6. Native Consequences

An exact copy can fail by breaching a protected commitment, while an independently implemented candidate can qualify without proven descent. Several candidates can qualify simultaneously. Continuity can be non-transitive when domains or tolerances differ. Provenance affects operational continuity only when it changes accountability, commitments, or expected conduct. No certificate licenses claims beyond its declared domain.

## 7. Limitations and Self-Critique

Probe suites can be gamed and protected commitments reflect normative power. The apparent precision depends on who selected probes, commitments, and tolerances. Feasible-history sets may be expensive, non-transitivity complicates long chains, and persuasive explanations can mimic accountable change. Similar conduct does not establish shared experience, authorship, origin, or moral identity.

## 8. Alternatives and Comparative Tradeoffs

Causal genealogy is stronger for responsibility but insufficient for competent resumption. Memory and stable identifiers are copyable or administrative. Narrative recognition is meaningful but framing-sensitive. Cryptographic continuity authenticates a chain without preserving commitments. Pure predictive similarity omits promises, permissions, and amendment accountability. The proposal gives priority to bounded future role performance while keeping these other relations separate.

## 9. Falsification and Abandonment Conditions

The model fails if labels or irrelevant order change bounds, missing information becomes a violated commitment, refinement reverses a declared invariant, contradictory constraints are averaged, translator changes disappear from explanations, or timeout becomes failure. It should be abandoned as the primary practical account if preregistered certificates do not predict resumption and trust better than snapshot or identifier baselines, and adaptive probe expansion does not improve held-out prediction.

## 10. Testable Implementation Contact

A prototype uses versioned constraint documents, a bounded solver, sandboxed probes, commitment checkers, robust lower/upper scoring, and minimal-conflict extraction. A decisive test compares a verified descendant that violates a protected commitment with an unproven descendant that preserves every commitment, stays within behavioral tolerances, and explains change. The latter should receive the stronger operational certificate while the former retains stronger descent evidence. Relabeling, identifier deletion, and order permutation must leave the split unchanged.

## 11. Decision-Relevant Questions

- Can protected commitments be elicited stably enough to predict later trust?
- How should probe gaming and persuasive but insincere explanations be detected?
- Is operational continuation allowed to outrank genealogy for the intended product role?
- What domains and tolerances make the certificate useful without overclaiming?
- Would a dominant independent provenance effect require redesign?

---

# Candidate C07 — Neutral Review Brief

## 1. Problem Interpretation

Persona persistence is approached as continuity of lived orientation across evidence channels rather than identity of a carrier. The key operational question is how much of a prior configuration’s recollections, practical dispositions, commitments, relationship positions, and anticipated consequences can be transported into a successor without hiding loss, novelty, contradiction, or translation failure.

The result is a purpose-relative continuity evidence certificate, not a claim of numerical identity, consciousness, ownership, or authority transfer.

## 2. Explicit Assumptions

- A finite, revisable set of human-relevant evidence channels can approximate lived orientation for bounded evaluation.
- Raw evidence can carry a source receipt, capture interval, schema version, confidence state, and authority scope.
- Each semantic version has a fixed encoder into an orientation space and an explicit cross-version bridge policy.
- Channel-specific transport costs, weights, loss penalties, novelty penalties, and hard incompatibilities are exposed commitments.
- Evidence may disappear or appear, so balanced one-to-one transport is not assumed.
- Common-source evidence cannot be counted twice after branch consolidation.
- Finite computation may return bounds or budget uncertainty.

## 3. Representation

Evidence is stored as immutable atoms with channel, content, source-capacity receipt, time or order interval, schema, and confidence. A versioned encoder maps usable atoms into channel-specific measures in an orientation space. Partial bridges relate old and new encodings.

An unbalanced optimal-transport problem moves mass from predecessor evidence to successor evidence. Transport cost measures change within a channel; unmatched predecessor mass incurs loss, unmatched successor mass incurs novelty, and hard contradictions or unavailable bridges prohibit matches. Several near-optimal couplings are preserved rather than collapsed into a single lineage.

The output is a vector receipt covering retained support, loss, novelty, conflict, translation coverage, and uncertainty, with lower and upper bounds.

## 4. Core Mechanisms

Source-capacity constraints prevent duplicated checkpoint evidence in two branches from becoming two independent units after consolidation. Unsupported but coherent memories remain novel unless a valid source receipt connects them. A missing cross-version bridge leaves the old interpretation reconstructible and the current interpretation unresolved.

Forks split transport flows; merges combine them subject to source capacity and conflict costs. Continuous paths can be scored through endpoint transport and path-action bounds, while raw threshold-crossing counts are not assumed invariant.

## 5. Behavior on Common Stress Cases

- **Rule revision:** preserve the old certificate. When a new semantic channel lacks an old observation or bridge, the new result is unresolved rather than a rewritten historical failure.
- **Interrupted branches:** the complete branch supports a tighter coupling. Corruption widens coupling alternatives; conflicting commitments remain hard incompatibilities or explicit transformation costs.
- **Sampling change:** endpoint transport and path-action bounds should converge under refinement when the continuous path and numerical scheme are fixed; threshold-crossing counts need not.
- **Schema change:** exact bridges transport directly, one-to-many bridges preserve several couplings, and unavailable bridges leave untransported mass and explicit uncertainty.
- **Pairwise agreement without a global account:** locally valid couplings do not guarantee one globally coherent coupling across all channels and schemas.
- **Copy, divergence, and consolidation:** one checkpoint can contribute to several successors. Consolidation cannot double-count their shared source, and memory exchange adds new supported or novel mass without proving identity fusion.

## 6. Native Consequences

Common-source evidence is non-additive. A coherent unsupported episode cannot become inherited evidence through content similarity alone. Prospective reinterpretation preserves the old encoded result while marking untranslatable current claims. Plural descent is compatible with withheld sameness. Opposed commitments cannot be averaged away without an explicit loss or transformation cost.

## 7. Limitations and Self-Critique

The evidence channels and transport geometry encode human judgments and can be chosen to favor a preferred narrative. What can be verbalized or archived may be overvalued, while inaccessible constitution is ignored. Source receipts reintroduce stable reference structure, computation can be expensive, and the result may be an elaborate continuity-accounting layer rather than a world model. Human authority remains external.

## 8. Alternatives and Comparative Tradeoffs

Simple provenance bookkeeping is cheaper but lacks graded loss, novelty, and channel-sensitive transport. Memory overlap misses unsupported false memories and common-source double counting. Viability dynamics better models continuous behavior. Proof systems better represent authority. This proposal is most distinctive in fork/merge conservation, explicit novelty, and partial semantic bridges.

## 9. Falsification and Abandonment Conditions

The model should be weakened or abandoned if benign representation changes materially alter certificates, a memory-overlap or behavior baseline matches its held-out discrimination, duplicated sources gain ancestry weight after merge, unsupported false memories are repeatedly classified as inherited, or continuous-refinement bounds fail to converge under their own assumptions. It should also be narrowed if independently chosen channel and cost settings are unstable or answer-encoding.

## 10. Testable Implementation Contact

A prototype needs immutable evidence atoms, source-capacity receipts, versioned encoders, partial bridges, an unbalanced transport solver, and vector certificates. Native tests include fork conservation, false-memory injection, partial reinterpretation, continuous refinement, and commitment conflict. A copied checkpoint unit must contribute at most one unit after merge; a coherent injected episode with no receipt must stay novel; and a conflict must survive or pay a visible cost.

## 11. Decision-Relevant Questions

- Are the proposed orientation channels stable and culturally defensible?
- Does transport catch false-memory and fork/merge errors missed by simpler baselines?
- Can costs and weights be fixed before seeing desired outcomes?
- Is a vector receipt intelligible enough for Owner review?
- Should this serve as a continuity accounting layer combined with governance and behavior models?

# Initial Owner Response Form

- Review timestamp:
- Initial choice (`C01`–`C08` or `ABSTAIN`):
- Ranking or pairwise preference (where possible):
- Top reasons:
- Strongest objection:
- Evidence most attended to:
- Uncertainty:
- Natural question:
- Minimal fact or evidence that would change the judgment:

