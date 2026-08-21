PRE_REVEAL_INPUT_BOUNDARY=neutral contract only
POST_REVEAL_BASIS=02–05
NON_NORMATIVE

# PRE_REVEAL_FREEZE

Source boundary: neutral pilot contract only. The complete positions below are frozen before exposure to any current research basis. In particular, each position’s fields 1, 2, 3, 5, 6, and 7 are the frozen Track B core.

## B4 — Proof-Carrying Succession Constitution

### 1. Problem interpretation

Persona persistence is not only a descriptive question; it licenses claims, commitments, and actions affecting humans. The primary requirement is therefore a contestable governance procedure: every continuity, descent, or authority claim must carry an inspectable warrant under a declared succession constitution.

Continuity is policy-relative admissibility, not silently inferred metaphysical identity. The system’s central output is the strongest warranted claim set plus its unresolved objections.

### 2. Explicit assumptions

1. Decision-relevant reasons can usually be expressed as typed claims and inference policies.
2. Evidence sources and translators can be assigned explicit trust and scope.
3. Historical rules and succession policies can be versioned.
4. Missing evidence is undetermined rather than false.
5. Contradictory evidence must be tolerated without logical explosion.
6. Local vocabularies need not share a universal schema.
7. Translation is itself a claim requiring a warrant.
8. Descent, content carriage, operational continuation, sameness, and authority are distinct predicates.
9. Multiple successors may simultaneously satisfy a nonexclusive continuation policy.
10. Proof search exhaustion is not refutation.

### 3. Model specification

Each scope and schema has a local claim language. An evidence token records:

\[
\langle
\phi,\ \text{polarity},\ \text{scope},\ \text{local order},
\ \text{source},\ \text{schema},\ \text{rule version}
\rangle .
\]

Positive and negative support are tracked independently, yielding four statuses:

- supported only;
- opposed only;
- both supported and opposed;
- neither.

A certificate contains its premises, inference rules, translator warrants, policy version, unresolved objections, and derivation result.

A succession constitution \(\Pi\) defines separate proof obligations for:

- `descends(S,K)`;
- `carries(S,q)`;
- `continues_Π(S,K)`;
- `authorized_Π(S,a)`;
- `same_persona(S,K)`.

The final predicate has no default introduction rule. If a community wants it, it must publish a distinct criterion.

A merge creates a new claim context that explicitly imports certified claims from its sources. Contradictions remain visible. No arbitrary winner is chosen unless \(\Pi\) contains a declared priority or adjudication rule.

Translators may produce an exact theorem, a disjunction of alternatives, or a proof that the source claim is not expressible. Composite translation requires a coherence certificate.

### 4. How assumptions appear in the model

- Expressibility appears in the typed claim languages.
- Trust appears in source-specific admissibility rules.
- Revision appears as version-indexed policies and derivations.
- Open-world reasoning appears through the `neither` status.
- Contradiction tolerance appears through independent positive and negative support.
- Locality appears in scope-specific languages.
- Translation accountability appears in translator certificates.
- Claim separation appears in the five distinct predicates.
- Nonexclusive succession appears through policy cardinality rules.
- Computation limits appear as open proof goals marked `NOT_PROVED_WITHIN_BUDGET`.

### 5. Native consequences

1. At a fixed policy version, adding opposing evidence does not erase an existing positive proof; status changes from supported-only to both.
2. A new rule version creates a new evaluation rather than rewriting an old derivation.
3. No proof is not a proof of the negation.
4. Copied memories establish content carriage, not authorship, lived experience, authority, or sameness.
5. Two successors may both be valid continuations if the constitution does not require exclusivity.
6. A claim transported through an ambiguous translator remains disjunctive.
7. Pairwise translation warrants do not imply a coherent global warrant.
8. Corruption weakens only derivations that depend on the damaged material.
9. Any outcome change caused by a policy or translator revision has an inspectable changed premise.
10. Renaming and irrelevant order permutation yield structurally equivalent certificates.

### 6. Failure/falsification conditions

B4 fails if:

- the proof engine derives claims not licensed by its displayed premises and rules;
- alpha-equivalent inputs produce substantively different certificates;
- contradictory evidence silently deletes prior support or causes unrelated conclusions;
- a global conclusion is issued despite an unclosed translation-coherence obligation;
- budget exhaustion is reported as rejection;
- reviewers’ stable reasons for adjudication cannot be expressed without case-specific exceptions;
- published succession policies routinely authorize obviously hollow successors or deny well-supported ones.

Abandon B4 as the primary account if, on a preregistered held-out adjudication set, a substantial recurring class of reviewer-agreed decisions cannot be reproduced by certificates whose premises and general rules those same reviewers accept, and repair requires a growing list of individual-case clauses rather than a reusable policy.

### 7. Limitations

- A procedurally valid continuation may still feel inauthentic.
- Constitutions can encode bias, institutional capture, or excessive conservatism.
- Proof artifacts may become large and difficult for humans to review.
- Tacit, affective, or embodied reasons may resist proposition-level representation.
- Source authenticity remains dependent on an external trust infrastructure.
- Different communities may issue incompatible constitutions.
- The model does not discover metaphysical identity.
- Deferring unresolved cases to adjudication may reduce automation benefits.

### 8. Self-critique

B4 risks confusing legitimacy with life. A perfectly audited successor might preserve rules while losing the behavioral qualities humans cared about. Conversely, an authentic but poorly documented continuation may fail its proof obligations. Four-valued logic exposes conflict but does not resolve it; hard judgment may simply be relocated into policy drafting.

### 9. Alternative explanations considered

- **Viability dynamics:** models gradual change and interruption well, but embeds judgments in coordinates and boundaries.
- **Bayesian generative inference:** ranks hypotheses smoothly, but priors can hide normative choices and posterior normalization can obscure unresolved contradiction.
- **Causal provenance alone:** establishes material lineage but not permission, responsibility, or human compatibility.
- **Narrative coherence:** captures human meaning but lacks stable derivation rules.
- **Identifier or snapshot continuity:** insufficient under copying, regeneration, and divergence.

### 10. Theory contribution

B4 contributes a proof-carrying, policy-relative theory of succession with:

- independent positive and negative support;
- immutable rule-relative historical judgments;
- first-class translation warrants;
- explicit non-derivability;
- orthogonal descent, content, continuation, sameness, and authority claims;
- accountable explanation of conclusion changes.

Its key claim is that uncertainty about identity should not prevent precise answers about what is evidenced, licensed, contested, or still open.

### 11. Testable/implementable contact

A prototype can use a paraconsistent rule engine with:

- immutable typed evidence tokens;
- versioned policy and translator modules;
- proof certificates;
- explicit import rules for consolidation;
- dependency-indexed corruption handling;
- four-valued query results;
- bounded proof search with open-goal reporting.

#### Common problems

**C1 — Meaning revision**

Store a certificate for `READY@R1` from A and B. Under R2, C has neither positive nor negative support, so neither `READY@R2` nor `NOT_READY@R2` is derivable absent another rule. Preserve A, B, the R1 certificate, R1 itself, and the fact that C was unrecorded. None may be overwritten.

**C2 — Interrupted branches**

Verified restoration evidence can certify both `descends(X,K)` and `descends(Y,K)` without runtime IDs. X certifies acceptance of \(d\) and note \(x\). Y certifies only intact fragments; rejection of \(d\) and note \(y\) are supported only if their tokens or independent attestations survive. Otherwise they remain alleged or unresolved. A merged context imports the surviving claims and exposes any accept/reject conflict. Admissibility depends on \(\Pi\); uniqueness, sameness, and authority are unproved unless separate certificates exist.

**C3 — Different sampling**

The primitive claims concern observed values at declared sample windows. A crossing theorem requires an explicit continuity, bracketing, threshold, hysteresis, and possibly minimum-dwell rule. Coarse evidence may support at least one crossing while fine evidence supports three bracketed excursions. Exact physical count remains unproved if intervening behavior is unconstrained. The engine does not mint a decisive crossing merely because adjacent samples change category.

**C4 — Dependency/schema change**

The old `owner` claim remains valid in its original language. Exact translator certificates yield one current claim; one-to-many certificates yield a disjunction of `principals[]` interpretations; the third class leaves an open translation obligation. Downstream proofs inherit the singleton, disjunction, or open goal. Untranslatable never means `principals=[]`.

**C5 — No global account**

All local certificates and pairwise reconciliation certificates remain valid in their scopes. Because translator composition cannot be certified, no all-three-scope theorem is available. Maximal coherent subaccounts or alternative translator selections are returned separately. The obstruction identifies the exact translators, overlap claims, and composition rule responsible.

**C6 — Copy and consolidation**

Both successors can receive shared-descent certificates and, under a nonexclusive policy, separate continuation certificates. Divergence creates distinct claim contexts. Exchanged memories certify `carries(S,q)` with source annotations; they do not certify authorship, experience, sameness, or authority. Consolidation may license a new continuation under \(\Pi\), but it does not retroactively make the predecessors one persona.

#### Native test preregistration

Create paired inputs related by vocabulary renaming, irrelevant reordering, stable-ID deletion, added contradiction, changed translator, and fixed proof-budget reduction. B4 predicts:

- renaming and irrelevant reordering produce alpha-equivalent certificates;
- ID deletion removes only derivations that cite ID evidence;
- adding a valid contradiction changes supported-only to both without deleting the original proof;
- changing a translator produces a conclusion delta whose certificate cites that translator;
- incoherent pairwise translators block a global theorem;
- an outside-language case is marked `UNEXPRESSIBLE`;
- budget exhaustion leaves an open goal.

Any untraceable conclusion change or unsound certificate falsifies the implementation. The recurring-unexpressible-reasons condition in field 6 triggers abandonment of B4 as the primary theory.

### 12. What would change the conclusion

A case-level conclusion changes only through a new evidence token, source-trust ruling, translator warrant, policy version, or completed proof obligation. The certificate must expose the dependency responsible.

The theoretical conclusion would change if human-compatible continuity proves primarily continuous and subpropositional, if legitimate policies cannot be stabilized across reviewers, or if accepted adjudications systematically resist reusable proof rules. In that event, B4 should remain an audit and authority layer but yield the primary continuity judgment to a behavioral or dynamical model.

# POST_REVEAL_DELTA_AUDIT

The B3/B4 pre-reveal freeze remains immutable. The comparisons below change only the external assessment of each position.

Scope caveat: “new” means absent from the four authorized revealed artifacts, not globally or program-wide new. “Independently rediscovered” means independent of the unrevealed basis; several overlaps were nevertheless cued by C1–C6 in the neutral contract.

## B4 — Proof-Carrying Succession Constitution

### Remains unchanged

- The core interpretation remains: continuity claims that license action require explicit, inspectable warrants rather than silent identity inference.
- Versioned evidence, four-valued contradiction handling, open-world non-proof, local claim languages, translator warrants, and bounded proof search remain unchanged.
- The five-way separation of descent, content carriage, policy-relative continuation, sameness, and authority remains unchanged.
- Memory exchange continues to prove content carriage rather than experience, authorship, sameness, or authority.
- The frozen self-critique—that procedural legitimacy can fail to capture a living or behavioral notion of continuity—remains especially important.

Reason: the revealed basis strongly supports historical integrity, non-closure statuses, authority-state separation, human governance, and the need to distinguish continuance from succession.

### Changes

No frozen scientific claim changes. The comparative assessment changes in three ways:

1. **B4 is now assessed more cautiously as a primary world model.** The foundation explicitly says a proof ledger or metalanguage is insufficient without a non-trivial native world-level consequence. B4 has native policy and inference consequences, but whether those constitute a sufficient Persona world model is now a central qualification question.
2. **Novelty narrows.** Historical semantic versioning, paraconsistent/non-closure statuses, local vocabularies, translator coherence, and authority separation already occur in the current map.
3. **Likely architectural role shifts.** Unless its policy-relative licensing is accepted as constitutive of the target, B4 may be strongest as a governance/audit layer paired with a behavioral, relational, or dynamical account. This is an external role assessment, not a frozen-core alteration.

### Rejects

B4 continues to reject:

- memory sufficiency for sameness;
- descent or copied content as automatic authority;
- rule revision by historical overwrite;
- binary falsehood from absence or failed proof search;
- a compulsory universal language or globally coherent account;
- stable IDs as sufficient succession evidence;
- an unversioned, policy-free identity verdict;
- the assumption that pairwise translator success proves global coherence.

Its strongest substantive disagreement is with `Identity = Memory` as a sufficient rule: B4’s copy and exchange results reject that implication. The revealed basis leaves the proposition open, so this is a legitimate candidate answer rather than rejection of established intent.

### Independently rediscovered

B4 independently reproduced or operationalized:

- historical records retaining their then-applicable semantics;
- later correction qualifying rather than deleting historical lineage;
- explicit separation of research result, validation, acceptance, freeze, and authority;
- non-collapse of supported, opposed, disputed, unknown, and not-proven;
- local/contextual descriptions with explicit translation obligations;
- pairwise reconciliation without guaranteed global composition;
- continuance, succession, sameness, and authority as distinct claims;
- memory as important but insufficiently established;
- human governance over judgment and authority;
- the risk that a ledger or formal language can be fluent yet lack native consequence.

Again, C1–C6 cued several problem classes. B4 independently selected a paraconsistent constitutional treatment and made its proof consequences explicit.

### Genuinely new contribution

Relative to the four revealed artifacts, B4 adds:

- an integrated proof-carrying succession constitution rather than only versioned records or generic non-closure;
- five explicit predicates with no default introduction rule for `same_persona`;
- the fixed-policy support theorem: adding valid opposition preserves the original positive proof and changes status to `both`;
- translator validity as a first-class proof obligation carried inside every transported certificate;
- merge as explicit contextual import, preventing exchanged memories from becoming retroactive authorship;
- a metamorphic certificate test requiring alpha-equivalence under vocabulary renaming;
- an abandonment condition based on recurring, reviewer-accepted reasons that resist reusable general policies.

The components have precedents in the revealed map; their combination into a succession constitution and its native tests is new relative to these artifacts.

### Basis conflict or source caveat

1. **Proof-ledger insufficiency is a direct challenge.** The basis explicitly rejects a storage system, proof ledger, or metalanguage as sufficient without native world-level consequences. B4’s policy consequences are non-trivial, but it still must show that it contains and operationalizes a Persona worldview rather than merely adjudicating claims about one.
2. **Continuous-change weakness.** B4 handles sampling epistemically but does not natively model continuous change. The revealed map treats continuous change as a major open gap.
3. **Relational-constitution tension.** Relationships can appear as claims and policy premises, but B4 does not make relational constitution primary despite the current strong lean.
4. **Policy legitimacy can encode the answer.** A succession constitution may simply stipulate preferred outcomes. Its policy selection and revision require anti-fixture and human-governance tests.
5. **Human familiarity remains untested.** Inspectable certificates may support human control, but proof size and procedural abstraction may harm familiarity. The current audit reports no candidate-level sovereignty evidence.
6. **No validation from current-six overlap.** Similarity to AHCK’s statuses or LPCW/CCP’s coherence behavior is structural only. It neither proves B4 nor demonstrates its policy layer.
7. **Comparative provenance is inadequate.** The same ARM-B/ARM-C, missing-input, missing-candidate-byte, and evaluator-replay caveats prohibit ranking or ancestry claims.
8. **No Owner endorsement.** Human-side sovereignty supports B4’s problem choice, not its constitution, logic, or policy-relative theory of continuity. Raw-primary verification remains incomplete.

### B4 verdict

The reveal corroborated B4’s **governance relevance**, its history-preserving and non-closure distinctions, and the need to keep authority separate from continuity. It did not validate B4 as a sufficient world model. The most important revealed challenge is whether it produces native Persona consequences rather than only well-audited claims.

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
