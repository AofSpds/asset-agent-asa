---
title: "Track B B2 — Robust Resumption Envelope"
state: "NON_NORMATIVE"
track: "B"
position: "B2"
pre_reveal_status: "PRE_REVEAL_FREEZE / IMMUTABLE"
pre_reveal_boundary: "AAA-ASA-MI Neutral 8-Position Pilot Contract v0.1 only"
post_reveal_status: "DELTA_AUDIT / NON_NORMATIVE"
post_reveal_boundary: "Artifacts 02–05 only"
post_reveal_basis:
  - "02_RESEARCH_FOUNDATION_MAP.md"
  - "03_OWNER_INTENT_INTERPRETATION_MATRIX.md"
  - "04_CONCEPT_AND_ASSUMPTION_MAP.md"
  - "05_SOURCE_INTEGRITY_AND_CURRENT_SIX_AUDIT.md"
audit_date: "2026-08-21"
---

# Track B B2 — Robust Resumption Envelope

# PRE_REVEAL_FREEZE

Scope declaration: I used only the neutral pilot contract. I had no exposure to the current research basis, project theory, terminology, or other agents’ work. Both positions below are independently formulated. All content is frozen pre-reveal; fields 1, 2, 3, 5, 6, and 7 are specifically frozen under the Track B rule.

## B2 — Robust Resumption Envelope

### 1. Problem interpretation — FROZEN

The practical target is not historical sameness but reliable renewal of a human-facing role. A persona persists to the extent that a successor can honor protected commitments, respond within an expected range, disclose and justify changes, and remain accountable across relevant future situations.

Historical descent remains a separate claim. An unrelated implementation may be a better operational continuation than an exact descendant that violates the persona’s central commitments.

### 2. Explicit assumptions — FROZEN

- Practical continuity can be evaluated through future-facing commitments and counterfactual interaction tests.
- The relevant use domain, protected commitments, tolerances, and amendment procedure can be declared.
- No finite test proves unrestricted equivalence; every conclusion is domain-bound.
- Incomplete evidence should define a set of possible histories or configurations, not one guessed history.
- Contradictory evidence may require multiple alternative sets rather than forced averaging.
- More than one successor may qualify simultaneously.
- Behavioral and commitment equivalence does not imply genealogical identity.
- Changes are acceptable only when an identified amendment rule or accountable explanation permits them.
- Human reviewers can identify at least some commitments that must not be traded away.
- Resource-bounded evaluation may remain unresolved.

### 3. Model specification — FROZEN

At each review boundary, the persona is represented by a review capsule:

\[
R_i=(E_i,\Omega_i,M_i,Q_i,\Theta_i,A_i)
\]

- \(E_i\): versioned observations and applicable interpretive rules;
- \(\Omega_i\): the set of histories/configurations consistent with \(E_i\);
- \(M_i\): scoped commitments, permissions, prohibitions, priorities, and sources;
- \(Q_i\): counterfactual interaction probes;
- \(\Theta_i\): tolerances and comparison rules;
- \(A_i\): permitted amendment and explanation procedures.

Capsules may have partial precedence and may branch.

For a candidate successor \(z\), the model evaluates commitment satisfaction, predicted behavior over \(Q_i\), retention of required knowledge or accountability, and explanation of deliberate changes. Because evidence is incomplete, it computes lower and upper suitability bounds over admissible predecessor histories and candidate configurations.

- strong continuation: the lower bound passes and no protected commitment is violated;
- possible continuation: only the upper bound passes;
- failed continuation: even the upper bound fails;
- unresolved: the budget or representation is insufficient.

Genealogical descent and external authority are reported separately.

Merging branches means combining their constraints. If the conjunction has no solution, the model returns a minimal conflicting constraint set and preserves alternative envelopes. It does not manufacture a compromise state.

### 4. How assumptions appear in the model

- Underdetermination appears as \(\Omega_i\), a set rather than a single latent state.
- Human-facing continuity appears as \(M_i\), \(Q_i\), and \(\Theta_i\).
- Scoped conclusions appear in every certificate’s declared probe domain and tolerances.
- Accountable change appears in \(A_i\).
- Multiple successors appear as independent certificates rather than a uniqueness constraint.
- Contradiction appears as separated feasible sets and minimal conflict explanations.
- The descent/continuation distinction appears as separate outputs.
- Budget limits appear as unresolved bounds, never as failure.

### 5. Native consequences — FROZEN

- An exact copy can fail operational continuity by breaking a protected commitment.
- A separately implemented system can qualify operationally without proving descent.
- Several candidates can qualify at the same time.
- Continuity can be non-transitive when domains or tolerances differ.
- Provenance affects operational continuity only when it changes accountability, a protected commitment, or expected future conduct.
- New evidence narrows the feasible set and may strengthen or weaken the robust lower bound.
- Pairwise feasible interpretations do not imply a globally feasible interpretation.
- Threshold-relative events are conclusions about a probe, not intrinsic historical joints.
- No certificate licenses claims beyond its declared domain.

#### C1 — Meaning revision without overwrite

The \(t_1\) capsule records the actual R1 evaluation: A and B sufficed, so `READY under R1` was issued. Under R2, feasible histories include possibilities where the unrecorded C held and possibilities where it did not. The R2 result is therefore unresolved. The \(t_1\) decision and R1 context remain fixed; the model may not relabel the old result as either `READY under R2` or `NOT READY under R2`.

#### C2 — Interrupted branches and partial merge

X produces a narrower, well-supported feasible set. Y produces a wider set because of corruption. If the accept/reject records are available, their conjunction is infeasible unless a declared reconciliation rule distinguishes their scopes. Otherwise the merge remains partitioned into X-consistent and Y-consistent alternatives. A candidate is strongly resumable only if it preserves protected commitments across all remaining relevant possibilities; otherwise it is possible or unresolved. Runtime labels prove no identity, descent, completeness, or authority.

#### C3 — Continuous change under different sampling

Each sampling plan constrains a set of continuous paths. Invariant claims are those true for every compatible path under every sampling plan covered by the certificate, such as an endpoint change or a minimum crossing implied by alternating observations and continuity. Exact detected crossing counts depend on density, threshold, noise, and interpolation. The model reports a feasible range of crossings and tags every threshold conclusion with those choices.

#### C4 — Dependency and schema change

The historical `owner` interpretation remains in its original capsule. Under the new schema, an exact translation produces one principal set, a one-to-many translation produces several feasible sets, and an unavailable translation leaves the corresponding variable unconstrained. Downstream claims are strong only when true in every feasible translation; otherwise their suitability bounds widen or the result becomes unresolved.

#### C5 — Local agreement without a global account

Each local feasible set and pairwise intersection remains valid. An empty three-way intersection means no global account exists under the chosen translators. Alternatives are maximal feasible subsets or explicitly relaxed translator assumptions. A minimal conflicting constraint set identifies which translator or overlap assumption prevents globalization.

#### C6 — Copy, divergence, and consolidation

Both successors may qualify simultaneously as operational continuations of the checkpoint on a declared domain. Divergence can cause one, both, or neither to retain that qualification. Memory exchange and consolidation may improve current commitment coverage or behavioral compatibility, but do not establish genealogical sameness. The strongest licensed claims may therefore be shared feasible precursor and present role-equivalence; unique identity and exclusive succession remain unproven.

### 6. Failure and falsification conditions — FROZEN

The position fails formally if:

- labels or irrelevant presentation order change its bounds;
- missing information is treated as a violated commitment;
- a sampling refinement changes an allegedly refinement-invariant conclusion;
- infeasible branch constraints are silently averaged;
- a changed translator reverses a result without appearing in the conflict explanation;
- timeout is returned as failure.

It would be materially weakened if protected commitments cannot be elicited with enough stability to predict later resumption success, or if probe performance does not generalize beyond the probes.

I would abandon it as the primary continuity account if, across a preregistered set of matched cases, its certificates do not predict human resumption and trust judgments better than snapshot resemblance or identifier continuity, and adaptive expansion of the probe set does not improve out-of-sample prediction.

It must return `OUT_OF_DOMAIN` for phenomena that cannot be represented as finite evidence constraints, commitments, probes, or accountable amendments. Frequent relevant out-of-domain cases require a new representational family.

### 7. Limitations — FROZEN

- Probe suites can be gamed and are vulnerable to Goodhart effects.
- Choosing protected commitments is normative and may reflect reviewer power.
- Unobserved situations can reveal discontinuities that the envelope missed.
- Feasible-history sets may grow too large for exact computation.
- Similar behavior does not establish shared experience, origin, authorship, or moral identity.
- Thresholds and domain boundaries can make borderline outcomes unstable.
- Non-transitivity complicates long chains of resumptions.
- A persuasive explanation can mimic accountable change without being sincere.
- Human expectations can themselves conflict or change.

### 8. Self-critique

This is a functional and normative account, not a theory of literal identity. By allowing independently built successors, it may erase morally important authorship or causal history. Its apparent precision depends heavily on who selected the commitments, probes, and tolerances. A sophisticated system could optimize for the review envelope while failing in untested contexts.

### 9. Alternative explanations considered

- Causal genealogy: relevant to descent and responsibility but not sufficient for competent resumption.
- Shared memory: useful as a commitment or probe, but copyable.
- Stable identifiers: useful for administration, not substantive evidence.
- Narrative recognition by a user: important but vulnerable to framing and inconsistency.
- Cryptographic continuity: authenticates a chain but not preserved commitments.
- Pure predictive similarity: omits promises, permissions, explanations, and authority.
- A hidden essential self: not adopted because the contract supplies no independent observable test for it.

### 10. Theory contribution

The contribution is a scoped, interval-valued resumption certificate over feasible histories and future interactions. It distinguishes operational continuation from descent, treats underdetermination as a first-class object, and makes accountable revision part of continuity rather than an exception to it.

### 11. Testable and implementable contact

An implementation can use versioned constraint documents, a SAT/SMT or bounded model solver for feasible histories, a sandboxed probe runner, commitment checkers, robust lower/upper scoring, and minimal-unsatisfiable-core extraction. Every certificate includes the domain, tolerances, unresolved variables, amendments, and resource budget.

**Preregistered native test B2-T:** Compare:

- Candidate A: verified exact descent from K but a deliberate violation of a protected commitment on held-out probes.
- Candidate B: no proven descent, but preservation of every protected commitment, behavior within declared tolerances, and accountable explanations for changes.

The model predicts that B receives the stronger operational-resumption certificate, while A alone receives the stronger descent claim. Relabeling candidates, removing stable IDs, or permuting presentation order must not alter that split.

A second test supplies pairwise-feasible but jointly infeasible translators. The solver must reject a global envelope and return a conflict core containing the changed assumption.

**Meaningful failure condition:** If the model ranks A above B operationally, or if blinded human resumption judgments reliably favor A after both the breach and lack of descent are disclosed—and the certificate performs no better than an ID/snapshot baseline across the preregistered suite—the central position is falsified as a primary practical account.

Under budget exhaustion, bounds remain open and the result is `UNRESOLVED_WITHIN_BUDGET`.

### 12. What would change the conclusion

The position would gain support if commitment-preserving, behaviorally compatible candidates are reliably accepted as resumptions despite implementation or lineage changes, and if its lower-bound certificates predict failures on held-out interactions.

I would revise it if provenance has an independent, dominant effect after behavior, commitments, disclosures, and authority are controlled. I would also revise it if no stable protected commitments or useful probe domain can be elicited, if adversarial systems routinely pass probes while failing real interaction, or if a measurable intrinsic continuity property explains outcomes that the envelope systematically misses.

## END PRE_REVEAL_FREEZE

The preceding twelve-field position is immutable. The following material records only what changed in assessment after exposure to artifacts 02–05.

# POST-REVEAL DELTA AUDIT

## Audit method

Two distinctions are preserved:

1. **Disposition:** `UNCHANGED`, `CHANGED`, or `REJECTED` describes what the reveal does to the frozen position. `CHANGED` is an audit conclusion and does not edit the frozen text.
2. **Origin relation:** `INDEPENDENTLY_REDISCOVERED` means the frozen position overlaps a proposition or mechanism visible in 02–05; `GENUINELY_NEW_RELATIVE_TO_02_05` means no explicit counterpart was found in those four artifacts. This is not a claim of novelty relative to unavailable sources or the wider literature.

Overlap is not validation. The reveal artifacts do not execute B2 or test B2-T.

## Field-by-field delta

| Frozen field | Disposition | Relation to 02–05 | Reveal basis and reason |
|---|---|---|---|
| 1. Problem interpretation | `CHANGED IN PROGRAM SCOPE; UNCHANGED AS B2’S INTERNAL VIEW` | `INDEPENDENTLY_REDISCOVERED` in part | 03 and 04 explicitly preserve both human-facing continuance and structural succession without equating them. 02’s purpose also keeps identity, memory, authority, history, and relational participation under human governance. Therefore “the practical target is not historical sameness” can remain B2’s operational lens but cannot stand as the complete program target. |
| 2. Explicit assumptions | `UNCHANGED AS HYPOTHESES` | Mixed | Admissible histories, alternative sets, non-closure, domain-relative views, multiple successors, and ID insufficiency overlap 02–05. The assumptions that protected commitments can be stably elicited and that probes predict resumption remain untested; 05 reports no candidate-level human familiarity/control evidence. |
| 3. Model specification | `UNCHANGED AS A CANDIDATE MODULE` | Mixed: independently rediscovered machinery plus a new assembly | B2’s feasible-history set overlaps the AHCK scope reported in 05. Constraint intersection, local alternatives, and conflict cores overlap LPCW/CCP/CCRA. The exact review capsule, commitment/probe/tolerance/amendment tuple, and robust suitability bounds do not appear in 02–05. |
| 4. Assumption-to-model contact | `UNCHANGED` | Mixed | Versioned evidence, possible histories, scoped interpretation, and separated descent align with 02–04. The explicit use of commitment books, counterfactual probes, amendment procedures, and lower/upper certificates is B2-specific relative to the reveal basis. |
| 5. Native consequences and C1–C6 | `CHANGED ONLY IN EXTRAPOLATION` | Substantially `INDEPENDENTLY_REDISCOVERED` | Historical versioning, ID removal, fork/merge, non-global compatibility, partial translation, and threshold sensitivity all appear in 02–05. The claim that provenance matters only through operational effects remains admissible inside B2’s explicitly operational certificate, but the reveal rejects extending it to overall Persona continuity because legacy, lineage, authority, and historical integrity remain independent program concerns. |
| 6. Failure/falsification conditions | `UNCHANGED` | Mixed | Relabeling, refinement, translator mutation, anti-fixture gaming, and non-closure pressures overlap 02–04. B2’s human matched-case abandonment test, adaptive probe condition, and explicit `OUT_OF_DOMAIN` rule are not supplied in 02–05. |
| 7. Limitations | `UNCHANGED AND MATERIALLY STRENGTHENED` | `INDEPENDENTLY_REDISCOVERED` | 02 warns of answer encoding, evaluator sensitivity, post-hoc reinterpretation, and hidden assumptions. 04 separates familiarity from sovereignty. 05 shows no human-control evidence and incomplete continuous-change testing. These directly reinforce B2’s Goodhart, power, coverage, and scope limitations. |
| 8. Self-critique | `UNCHANGED` | `INDEPENDENTLY_REDISCOVERED` in concern | The reveal basis warns against collapsing human familiarity, sovereignty, lineage, and identity into one operational score. This confirms B2’s own concern that functional success may erase origin, authorship, or causal history. |
| 9. Alternatives considered | `UNCHANGED` | `INDEPENDENTLY_REDISCOVERED` | The four artifacts keep causal lineage, memory, relation, process, persistent-whole, constraint, contextual, interface, predictive, and portfolio accounts live. B2 cannot eliminate them through probe success alone. |
| 10. Theory contribution | `CHANGED FROM POSSIBLE PRIMARY ACCOUNT TO PURPOSE-RELATIVE CONTRIBUTION` | `GENUINELY_NEW_RELATIVE_TO_02_05` in exact form | The interval-valued operational certificate is distinct relative to 02–05, but 02’s theory-ecology possibility and 03’s dual continuance/succession view make a scoped-module interpretation better supported than a complete theory interpretation. |
| 11. Testable/implementable contact | `UNCHANGED` | Mixed | Constraint solving and conflict-core extraction overlap current candidate mechanisms. The A-versus-B descent/commitment matched experiment and human predictive comparison address a gap that 05 explicitly leaves open; no revealed result executes them. |
| 12. What would change the conclusion | `UNCHANGED` | `INDEPENDENTLY_REDISCOVERED` as discipline | 02–05 provide neither controlled human resumption judgments nor evidence that provenance becomes irrelevant under matching. Consequently the reveal itself neither confirms nor falsifies B2-T. |

## Unchanged

- The review capsule, feasible-history envelope, scoped commitments, probe domains, tolerances, and amendment procedures remain intact.
- Operational continuation remains explicitly distinct from genealogical descent and external authority.
- More than one successor may receive a scoped operational certificate.
- Historical evaluations remain versioned and may not be overwritten by later rules.
- Missing, contradictory, corrupt, and computationally unresolved evidence remain distinct.
- Pairwise feasibility does not imply global feasibility.
- Threshold and sampling choices remain explicit dependencies.
- B2’s native and abandonment tests remain frozen and unexecuted.

## Changed

The frozen text is not edited, but two post-reveal conclusions change:

1. **Program scope:** B2 is no longer treated as a plausible complete statement of “the practical target.” It is retained as an operational-continuance module or purpose-relative candidate inside a larger account that must also preserve lineage, historical integrity, authority, and human governance.
2. **Evidential status:** the assumptions that reviewers can declare stable protected commitments and that probe certificates predict real resumption are explicitly `NOT_DEMONSTRATED`. Artifact 05 identifies human familiarity/control/sovereignty as an open gap and reports no candidate-level evidence.

No formula, assumption, consequence, failure trigger, or test in the frozen block is retroactively modified.

## Rejected

One unqualified extrapolation is rejected:

- The opening phrase “the practical target is not historical sameness” must not be read as the program-wide conclusion. Artifacts 02–04 keep historical integrity, legacy, lineage, identity, memory, authority, continuance, and succession simultaneously in scope.

The following stronger readings are also rejected, but they were not required by the frozen model:

- operational equivalence proves identity;
- successful probes transfer authority;
- provenance is globally dispensable;
- B2 states Owner intent;
- human familiarity alone establishes sovereignty;
- an independently implemented successor is automatically the unique Persona successor.

The scoped B2 claim—that an unrelated implementation may outperform a descendant on a declared operational certificate—remains a live, falsifiable hypothesis.

## Independently rediscovered

B2 independently reproduced the following before reveal:

- current meaning can be usable and successor-revisable without historical overwrite;
- incomplete evidence should retain alternative admissible histories;
- unknown, undefined, disputed, alternative, impossible, and not-proven results should not collapse;
- continuity and succession are distinct;
- IDs and snapshots do not establish identity;
- multiple successor relations are possible after copy, fission, or merge;
- contextual/local compatibility may fail globally;
- translation may be partial or multivalued;
- continuous paths should not be reduced to sampling-created decisive events;
- domain and perspective choices must remain visible;
- human-facing continuity can involve narrative, commitment, and behavioral properties;
- a portfolio or theory ecology may be more appropriate than a universal kernel;
- fixture design, hidden thresholds, and answer encoding can make apparent success non-native.

The strongest structural overlaps are with the admissible-history family summarized for AHCK, the contextual constraint/gluing mechanisms summarized for LPCW/CCP/CCRA, and the continuance/succession distinction in 03–04.

## Genuinely new relative to artifacts 02–05

The following exact mechanisms, consequences, or tests were not found in the four reveal artifacts:

- the review capsule `R_i=(E_i,\Omega_i,M_i,Q_i,\Theta_i,A_i)` as one operational unit;
- robust lower and upper resumption-suitability bounds over predecessor and successor possibilities;
- the four certificate outcomes strong, possible, failed, and resource/representation-unresolved;
- explicit protected-commitment, probe, tolerance, and accountable-amendment coupling;
- the consequence that scoped continuity can be non-transitive when domains or tolerances differ;
- the sharp matched experiment contrasting a verified descendant that breaches a protected commitment with a non-descendant that preserves it;
- the requirement that an operational certificate outperform ID/snapshot baselines on human resumption judgments;
- the explicit adaptive-probe failure condition;
- the reviewer-power critique attached to choosing protected commitments;
- the `OUT_OF_DOMAIN` rule for cases outside finite evidence/commitment/probe representation.

These are “new” only relative to 02–05. Missing candidate-generation packets and absent ARM-B/ARM-C sources prevent claims about the broader project archive or external literature.

## Basis and source caveats

- Artifact 02 is source-derived with explicit interpretation and is `NON_NORMATIVE`. Its purpose statements and current assumptions do not validate B2.
- Artifact 03 distinguishes normalized-record Owner statements from research interpretation and says raw primary verification remains incomplete.
- The long-lived Persona lineage/substrate reading is explicitly a research interpretation, while memory sufficiency, liveness, exact human-familiarity weighting, and canonical program naming remain open.
- Artifact 04 is a working map, not an ontology. Its candidate families cannot be treated as mandatory architecture.
- Artifact 05 reports uneven provenance: ARM-A is strongest, ARM-B is corrupt/partial, ARM-C source selection is not proven, and exact evaluation replay is unavailable.
- Current-six absence of a B2-like human probe result is not evidence that existing candidates cannot provide one.
- No revealed artifact supplies controlled human judgments, stable commitment elicitation, adversarial probe generalization, or comparative evidence for B2-T.
- Similarity to admissible-history or contextual candidates may reflect shared problem pressure rather than derivation or superiority.
- Novelty findings are bounded to the four permitted artifacts and do not cover missing archives, other agents’ work, or the wider literature.

## Reasons for the delta result

The reveal strongly supports the relevance of B2’s machinery: admissible histories, scoped contexts, partial translation, non-global compatibility, versioned meaning, and multiple succession are all active research pressures. It also makes clear that the overall human-compatible Persona purpose retains historical integrity, lineage, authority, memory, and sovereignty as independent concerns. B2 already separates descent and authority from its certificate, so its model survives; what changes is the permissible breadth of the claim made for that certificate.

Because 05 identifies the exact human-facing evidence B2 needs as absent, conceptual convergence cannot upgrade B2’s empirical standing. The correct delta is scope restriction plus retained testing pressure, not optimization of the frozen model.

## Crisp reveal verdict

`REVEAL_VERDICT_B2 = RETAIN_WITH_PROGRAM_SCOPE_CHANGE_AS_NON_NORMATIVE_OPERATIONAL_CONTINUANCE_CANDIDATE`

`DELTA_PROFILE = SUBSTANTIAL_INDEPENDENT_REDISCOVERY + GENUINELY_NEW_CERTIFICATE_AND_TEST + ONE_REJECTED_PROGRAM_WIDE_EXTRAPOLATION + NO_VALIDATION`

B2 survives reveal as a distinct, falsifiable account of operational resumption, not as a complete account of Persona persistence. Its review capsule, robust bounds, and matched human test remain novel relative to 02–05, while its feasible-history and contextual machinery independently converges with the revealed basis.
