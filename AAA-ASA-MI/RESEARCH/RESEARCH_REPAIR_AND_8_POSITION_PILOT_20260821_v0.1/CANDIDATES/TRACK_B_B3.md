PRE_REVEAL_INPUT_BOUNDARY=neutral contract only
POST_REVEAL_BASIS=02–05
NON_NORMATIVE

# PRE_REVEAL_FREEZE

Source boundary: neutral pilot contract only. The complete positions below are frozen before exposure to any current research basis. In particular, each position’s fields 1, 2, 3, 5, 6, and 7 are the frozen Track B core.

## B3 — Belief-Tube Viability

### 1. Problem interpretation

A persistent persona is best treated as an uncertain, temporally extended pattern of capacities, preferences, commitments, and human relationships—not as a stored object. Meaningful resumption asks whether a candidate can be connected to prior operation by an admissible trajectory while remaining within an explicitly chosen human-compatible viability envelope.

This can support graded claims of possible continuity, robust continuity, and shared descent. It does not by itself prove numerical sameness or authority.

### 2. Explicit assumptions

1. Operationally relevant persona characteristics can be represented by a finite, revisable state \(z\).
2. Change over an interval can be bounded by a set-valued dynamic law; exact prediction is unnecessary.
3. Observations are partial, noisy, schema-relative, and may use only local ordering rather than global time.
4. Human-compatible operation can be described by a versioned viability envelope \(V_P\) under policy \(P\).
5. Missing evidence enlarges uncertainty; it is not negative evidence.
6. Historical observations and historical interpretations can be retained separately from later evaluators.
7. Shared descent, functional continuity, sameness, and authority are different claims.
8. Branches may produce several equally admissible trajectory families.
9. Schema translators may be exact, set-valued, or undefined.
10. Approximate computation must be sound: budget exhaustion yields `UNKNOWN`, never `FALSE`.

### 3. Model specification

For each locally ordered run \(r\), let \(z_r(s)\) range over relevant persona configurations. Observations carry value, uncertainty, source, local position, schema, and interpretation-rule version.

The compatible belief tube is:

\[
\mathcal T_r =
\{z(\cdot):
z(s_i)\in H_{\sigma_i}^{-1}(o_i),
\quad \dot z\in F_\nu(z,u,w)\}.
\]

Here \(H_{\sigma_i}\) is the schema-specific observation map and \(F_\nu\) is a versioned differential inclusion or set-valued update law. No single exact path is presumed.

A resumption from checkpoint \(K\) is:

- **possibly continuous** when at least one compatible path connects \(K\) to the candidate while remaining in \(V_P\);
- **robustly continuous** when the candidate uncertainty set lies inside the robustly reachable viability region;
- **unsupported** when sound reachability proves no admissible path;
- **unknown** when evidence or computation cannot decide.

Several solution families may share the same restriction up to \(K\), then diverge. Consolidation conditions these families on exchanged information; it does not splice their lived intervals into one trajectory.

Rule-relative interpretation is a separate evaluator \(E_R(o)\). Translators \(M_{\sigma\rightarrow\sigma'}\) return a singleton, a set of alternatives, or `UNDEFINED`.

Authority is supplied by a separate attestation system. It is never inferred from state proximity, common origin, or copied memory.

### 4. How assumptions appear in the model

- State representability appears in \(z\) and its published coordinate dictionary.
- Bounded change appears in \(F_\nu\), including declared regularity and disturbance bounds.
- Partial observation appears in inverse images under \(H_\sigma\), producing sets rather than point states.
- Human judgment appears explicitly in the policy-indexed envelope \(V_P\).
- Open-world reasoning appears as widening tubes and unresolved coordinates.
- Historical preservation appears through immutable observations plus multiple \(E_R\) evaluations.
- Non-unique succession appears as separate compatible solution families.
- Translation uncertainty is propagated through set-valued \(M\).
- Claim separation appears in distinct outputs for viability, descent, sameness, and authority.
- Computation limits appear through certified inner/outer approximations and `UNKNOWN`.

### 5. Native consequences

1. With noncontracting uncertainty and no new evidence, a longer interruption cannot strengthen robust continuity.
2. Consistent new observations shrink the compatible path set; they cannot create a path previously proved impossible under the same model.
3. Legitimate change can preserve continuity if its rate and route remain viable; snapshot similarity is neither necessary nor sufficient.
4. Exact threshold-crossing counts are not licensed without sampling and regularity assumptions.
5. Translation ambiguity propagates downstream and cannot spontaneously become certainty.
6. A copied checkpoint can generate multiple equally strong descendants.
7. Memory exchange can increase informational overlap without producing identity fusion.
8. Pairwise-compatible local descriptions need not admit a joint description.
9. Re-evaluation under a new rule adds a new result without changing the old one.
10. Label renaming, stable-ID removal, and irrelevant presentation order do not alter conclusions unsupported by those features.

### 6. Failure/falsification conditions

B3 is materially weakened if:

- continuity judgments change under invertible state-coordinate changes;
- declared refinement-invariant conclusions reverse under benign sampling refinement while regularity assumptions hold;
- ordinary persona changes routinely violate every non-vacuous dynamic bound;
- unacceptable resumptions fall robustly inside \(V_P\), or accepted resumptions are consistently unreachable;
- the state vocabulary must expand into a case-by-case catalogue to match stable human judgments;
- useful answers remain computationally indeterminate under realistic budgets.

Abandon B3 as the primary account if a preregistered blinded suite repeatedly produces candidates indistinguishable in every declared state coordinate and counterfactual probe, yet independent reviewers reliably distinguish their admissibility for reasons that cannot be represented without making the viability envelope a case list.

### 7. Limitations

- State coordinates, metrics, and viability envelopes contain value judgments.
- Abrupt reinterpretation may not fit a continuous approximation.
- High-dimensional reachability may be expensive or conservative.
- Strategic deception is only handled to the extent captured by observation-quality assumptions.
- Long gaps can yield tubes too broad to support useful conclusions.
- The model cannot establish metaphysical sameness.
- Authority and legitimacy require external human or institutional evidence.
- Distinct communities may adopt incompatible viability envelopes.

### 8. Self-critique

The geometric vocabulary may disguise contested human judgments as technical boundaries. Path existence can be too permissive: a mathematically possible route is not necessarily a meaningful continuation. Conversely, a conservative envelope may punish legitimate growth. State compression may omit narrative or relational facts that matter most, while an overcomplete state defeats tractability.

### 9. Alternative explanations considered

- **Stable identifier or snapshot:** computationally simple, but neither establishes meaningful descent nor tolerates regeneration and divergence.
- **Pure provenance ledger:** stronger for historical audit, weaker for continuous functional change and undersampling.
- **Predictive/compression similarity:** useful for behavioral resemblance, but a successful imitator may compress the same record without being its continuation.
- **Proof- or policy-based succession:** better for legitimacy and authority, but can authorize a functionally hollow successor.
- **Narrative coherence:** human-readable, but difficult to test without an explicit operational semantics.

### 10. Theory contribution

B3 contributes a continuous, set-valued account of persistence that separates four questions often conflated:

1. Is there a compatible route from the prior operation?
2. Does that route remain human-compatible?
3. Does evidence establish shared descent?
4. Is the candidate authorized?

It also makes sampling dependence, uncertainty growth, schema translation, and non-global reconciliation native rather than exceptional.

### 11. Testable/implementable contact

A prototype needs:

- interval- or set-valued observations;
- local ordering and optional time-alignment bounds;
- versioned observation maps and dynamic laws;
- a reachability/viability solver;
- set-valued schema translators;
- an immutable evaluation ledger;
- separate descent and authority attestations;
- four outcomes: `POSSIBLE`, `ROBUST`, `UNSUPPORTED`, `UNKNOWN`.

#### Common problems

**C1 — Meaning revision**

At \(t1\), retain `READY under R1`, supported by A and B. Under R2, A and B remain observed while C is unresolved, so current readiness is `UNKNOWN`, not `NOT READY`. Do not overwrite the R1 evaluation, its rule, A/B, or the historical absence of C.

**C2 — Interrupted branches**

X and Y share the K-compatible cross-section. X’s complete record supports a narrow reconstruction including acceptance of \(d\) and note \(x\). Y supports only its intact observations; corrupted intervals expand into a reachable set. If rejection of \(d\) or note \(y\) survives verification, it remains a distinct conflicting mode; otherwise it is unresolved. X may be robustly resumable while Y is only possibly resumable. Runtime IDs contribute nothing. Shared descent may be supported, but unique sameness and authority are not.

**C3 — Different sampling**

Common sample values, endpoint relations, and any property true of every compatible continuous path are invariant. Exact crossing count, short excursions, dwell time, and even whether a crossing is decisive depend on sampling, threshold, hysteresis, and regularity bounds. The model retains a set of compatible functions and returns a crossing-count or occupancy range instead of manufacturing point events.

**C4 — Dependency/schema change**

The historical `owner` observation remains reconstructible in its old schema. Exact translations give singleton current interpretations; one-to-many cases give alternative `principals[]` sets; unavailable translations return `UNDEFINED`, not an empty set. Downstream calculations operate over all alternatives or remain unknown.

**C5 — No global account**

Each report retains its local feasible set and each pair may retain a valid coupling. Because the three couplings have no common joint realization, no all-scope account is justified. Maximal two-scope accounts or alternative translator choices may be reported separately. The responsible assumptions are the selected translators, coordinate alignments, and composition rules.

**C6 — Copy and consolidation**

Both successors may have equally strong shared-descent and possible-continuity claims from the checkpoint. Divergence yields distinct trajectory families. Later memory exchange narrows some informational differences but does not merge their histories or prove sameness. Neither unique identity nor authority follows from common origin, copied content, or consolidation.

#### Native test preregistration

Construct label-free paired cases with the same underlying path family but different presentation order, sampling density, and successor labels. B3 predicts:

- alpha-renaming and irrelevant reordering leave outputs unchanged;
- stable-ID removal affects only explicitly ID-dependent evidence;
- sampling refinement changes crossing bounds but not a declared viability invariant;
- changing a translator identifies that translator as the cause of any conclusion reversal;
- an outside-family case returns `OUT_OF_FAMILY`;
- budget exhaustion returns `UNKNOWN`, not rejection.

A failure of these metamorphic properties falsifies the implementation. Repeated state-complete, counterfactually indistinguishable cases with stable but unrepresentable human distinctions triggers abandonment under field 6.

### 12. What would change the conclusion

Case conclusions may change through new observations, corrected uncertainty bounds, a new schema translation, a changed viability policy, or an independent authority attestation. Each change must identify the affected assumption.

The theoretical conclusion would change if discontinuous symbolic or institutional factors dominate trajectory evidence, if no stable viability envelope can be agreed, or if the preregistered abandonment condition is met. In that case, B3 should become a subordinate diagnostic rather than the primary continuity model.

# POST_REVEAL_DELTA_AUDIT

The B3/B4 pre-reveal freeze remains immutable. The comparisons below change only the external assessment of each position.

Scope caveat: “new” means absent from the four authorized revealed artifacts, not globally or program-wide new. “Independently rediscovered” means independent of the unrevealed basis; several overlaps were nevertheless cued by C1–C6 in the neutral contract.

## B3 — Belief-Tube Viability

### Remains unchanged

- The core interpretation remains: continuity is an uncertain, temporally extended viability question, not proof supplied by an ID, snapshot, or memory copy.
- The distinctions among possible continuity, robust continuity, descent, sameness, and authority remain intact.
- Local ordering, partial observation, semantic versioning, set-valued translation, open-world uncertainty, and sound `UNKNOWN` under budget remain unchanged.
- The continuous/set-valued vocabulary remains justified. The revealed foundation explicitly keeps continuous/viability families live and does not require object, event, relation, graph, global state, or global time.
- The frozen native consequences, failure conditions, and limitations require no repair.

Reason: nothing in the revealed basis falsifies B3’s declared assumptions. The basis instead treats the relevant ontology and identity questions as open.

### Changes

No frozen scientific claim changes. Three comparative assessments change:

1. **Novelty narrows.** Continuous/viability is already an explicitly recognized candidate family. B3 is therefore an independent concrete realization of a known research direction, not discovery of the broad family.
2. **Overlap becomes visible.** Its compatible trajectory families and multi-outcome queries partly resemble the current audit’s account of AHCK admissible histories; its local-to-global coupling test resembles LPCW/CCP obstruction work. B3 remains materially different through differential/set-valued dynamics, viability, sampling semantics, and robust reachability.
3. **Evaluation priority changes.** Boundary/coordinate substitution, answer-encoding, human control, and sovereignty tests become higher-priority follow-ups. This is an evaluation change, not a model rewrite.

### Rejects

B3 continues to reject or decline the following as mandatory conclusions:

- `Identity = Memory` sufficiency;
- stable ID, snapshot equality, or copied content as proof of sameness;
- automatic authority transfer through descent or functional similarity;
- mandatory relation-first, event-first, graph, or global-time ontology;
- exact threshold-crossing events without sampling/regularity support;
- the inference that pairwise compatibility establishes a global account.

These are not conflicts with established Owner truth. The revealed basis classifies memory identity as open, relation-first as a strong but revisable lean, and global state/time as optional.

### Independently rediscovered

Relative to the unrevealed basis, B3 independently reproduced or operationalized:

- historical record plus then-applicable semantic version, with currentization as a separate partial operation;
- non-collapse of unknown, undefined, alternative, impossible, and not-proven;
- the continuance/succession distinction without automatic sameness;
- local parameters rather than presumed global time;
- pairwise local compatibility without global composition;
- sampling and threshold choice as possible hidden ontology;
- copy/divergence/merge conclusions that preserve descent without identity;
- human-side judgment through a versioned viability policy;
- the danger that variables, metrics, or envelopes encode the desired answer.

The C1–C6 contract directly prompted several of these problem classes. The independent contribution is mainly B3’s unified continuous formal treatment and consequences, not discovery of the cases themselves.

### Genuinely new contribution

Relative to the four revealed artifacts, B3 adds:

- a belief-tube/differential-inclusion specification rather than a general reference to “continuous/viability”;
- distinct existential and robust continuity criteria;
- the native interruption result that an evidence-free gap under noncontracting uncertainty cannot strengthen robustness;
- sound inner/outer reachability with budget exhaustion separated from impossibility;
- a formal account in which information consolidation conditions beliefs but does not fuse trajectory histories;
- a state-sufficiency abandonment test based on counterfactually indistinguishable candidates receiving stable, non-encodable human judgments.

The broad family is not new; this particular computational and falsificatory package is.

### Basis conflict or source caveat

1. **State-centric tension with relational constitution.** The current basis has a strong relation-constitutive lean. B3 includes relationships as state dimensions but does not make relation constitution fundamental. This is a live theoretical disagreement, not a violation, because the lean is explicitly non-final and non-mandatory.
2. **P0 tension.** A finite state vocabulary and viability envelope could harden into an essence. B3’s revisable coordinates and policy versioning mitigate this, but representation-substitution tests are necessary.
3. **Answer-encoding risk.** The revealed foundation specifically warns that variables, constraints, boundaries, schemas, and sampling can predetermine results. B3’s \(z\), \(F\), and \(V_P\) are all exposed to that risk.
4. **Human-purpose gap.** Human governance is represented, but human familiarity, actual control, and cognitive sovereignty are not demonstrated.
5. **No current empirical validation.** The audit says continuous change is not natively tested by the current six. That establishes a coverage gap, not support for B3’s truth.
6. **Comparative provenance is inadequate.** ARM-B is corrupt/partial, ARM-C source provenance is absent, exact candidate inputs are missing, and exact evaluator rerun is unavailable. No superiority, convergence lineage, or evaluator-calibrated result can be inferred.
7. **No Owner endorsement.** The intent matrix is based partly on normalized records with raw-primary verification incomplete. Its purpose statements do not select B3.

### B3 verdict

The reveal corroborated B3’s **research relevance**, its compatibility with the live ontology-neutral program, and the importance of the exact gaps it targets. It did not validate B3’s dynamics, viability envelope, human compatibility, comparative superiority, global novelty, or Owner acceptance.

## Crisp overall verdict

| Question | B3 | B4 |
|---|---|---|
| Frozen core changed? | No | No |
| Responsive to documented live questions? | Yes | Yes |
| Broad family already present? | Yes: continuous/viability | Partly: proof, policy, and non-closure components |
| Architecture-specific contribution still new to these artifacts? | Yes | Yes |
| Empirically validated by reveal? | No | No |
| Owner-endorsed? | No | No |
| Proven superior to current six? | No | No |
| Main revealed challenge | Hidden ontology/answer encoding in state and viability choices | Proof-ledger sufficiency and lack of native continuous/world dynamics |

The reveal validated **fit to the research problem**, not **truth of either model**. It showed that both freezes independently land on documented distinctions and risks. It did not validate adequacy, human compatibility, sovereignty, production readiness, global novelty, comparative rank, or any identity claim.
