# TRACK_A_A1 — Versioned Constraint-History Calculus

POSITION_ID = `TRACK_A_A1`

ORIENTATION = `FORMALIZATION / COMPUTATIONAL CONTACT`

MODEL_NAME = `VCHC — Versioned Constraint-History Calculus`

STATE = `FROZEN_CANDIDATE_POSITION / NON_NORMATIVE / NO_VALIDATION_OR_ADMISSION_CLAIM`

RESEARCH_BASIS_ROOT = `deliverables/AAA-ASA-MI/RESEARCH/RESEARCH_REPAIR_AND_8_POSITION_PILOT_20260821_v0.1/`

NEUTRAL_CONTRACT = `working/AAA-ASA-MI_NEUTRAL_PILOT_CONTRACT_v0.1.md`

## Provenance firewall

### SOURCE_DERIVED_BASIS

- The purpose is a computational structure for meaningful Persona resumption through interruption and change; identifiers, current snapshots, and stored text are not continuity proof (`working/AAA-ASA-MI_NEUTRAL_PILOT_CONTRACT_v0.1.md:5-11`).
- P0 permits an operational current meaning without finalizing it; historical versions remain inspectable (`02_RESEARCH_FOUNDATION_MAP.md:39-48`).
- Unknown, undefined, disputed, alternative, impossible, and not-proven must not collapse (`02_RESEARCH_FOUNDATION_MAP.md:39-48`).
- A candidate must operationalize its own view and derive a native consequence; project vocabulary is not mandatory (`03_OWNER_INTENT_INTERPRETATION_MATRIX.md:21-24`; `04_CONCEPT_AND_ASSUMPTION_MAP.md:19-22`).
- The exact raw Owner/whitepaper sources and portions of prior ARM provenance are absent. This position does not repair missing evidence by inference (`01_PREFLIGHT_AND_EXACT_STATE.md:53-72`).

### UNSOURCED_PRIOR_MODEL_PROPOSAL

Everything below that defines `VCHC`, its formal objects, operators, theorems, continuity profiles, and implementation is an independently proposed model hypothesis. It is not Owner intent, an established ASA-MI primitive set, or a claim that the baseline two-job attractor is correct. The closest prior family is possible-history/constraint semantics; novelty is not claimed.

## 1. Problem interpretation

The hard problem is not storing a latest Persona state. It is licensing only those claims that survive incomplete evidence, branching, schema change, and reinterpretation while retaining a mechanically reviewable account of why they are licensed.

VCHC treats a modeled world as a **nonempty family of typed, version-scoped possible histories**, not as one authoritative snapshot. A history is admissible only when it satisfies frozen generative and consistency constraints. Identity and continuity are not primitives: a query may derive a scoped predecessor/continuity claim from witnesses, or preserve several alternatives.

This is one unified possible-history semantics. It does not assume that contextual constitution and causal change must be two separate kernels.

## 2. Explicit assumptions

`A1.1 FINITE_OR_SYMBOLIC_SCOPE` — Each query has a finite horizon or a sound symbolic representation of its possible histories.

`A1.2 VERSION_LOCAL_SEMANTICS` — Every record and rule is interpreted under an explicit semantic version. No successor version mutates a predecessor version.

`A1.3 CONSTRAINTED_GENERATION` — A possible history is admitted by typed generative/consistency constraints, not by arbitrary record append.

`A1.4 PARTIAL_TRANSLATION` — Cross-version translation may return an exact image, alternatives, a typed hole, or an incompatibility. Total translation is not assumed.

`A1.5 OPEN_WORLD_EVIDENCE` — Missing or corrupt evidence enlarges the admissible-history family unless an independent rule excludes the missing alternatives; it does not become false.

`A1.6 PROFILE_RELATIVE_CONTINUITY` — Any continuity/succession judgment is relative to a declared profile `κ` of required witnesses. No universal identity scalar or automatic authority inheritance is assumed.

`A1.7 CONSTRAINT_LANGUAGE_COMMITMENT` — Type choices, variables, factorization, constraints, translations, and `κ` are exposed ontology/selection commitments and may determine results.

## 3. Model specification

Define a VCHC model

`M = (V, Σ, K, E, T, Q)` where:

- `V` is a DAG of semantic versions.
- `Σ_v` is the typed vocabulary available at version `v`.
- `K_v` is a frozen set of rules constraining valid history fragments and extensions under `Σ_v`.
- `E_v` is immutable, provenance-bearing evidence represented under `v`; corruption and absence are explicit.
- `T_vw : Σ_v ⇀ P(Σ_w ∪ {HOLE, INCOMPATIBLE})` is a partial, possibly one-to-many translation relation.
- `Ω_v(E)` is the set of all histories satisfying `K_v` and the usable portion of `E`.
- `Q` evaluates propositions over `Ω_v(E)` and returns a result plus a derivation/countermodel certificate.

Query results:

- `FORCED(q)` iff every admissible history satisfies `q`.
- `IMPOSSIBLE(q)` iff no admissible history satisfies `q`.
- `ALTERNATIVE(q)` iff admissible histories support both `q` and `¬q`.
- `UNDEFINED(q)` iff `q` cannot be typed in the chosen semantic version.
- `DISPUTED(q)` iff separately supported context families disagree and no licensed merge exists.
- `NOT_PROVEN(q)` iff the requested evidentiary or provenance witness is missing even when a semantic alternative set cannot be fully reconstructed.

Historical/current query split:

- `THEN(v, q)` evaluates against frozen `(Σ_v, K_v, E_v)`.
- `NOW(w, q, v)` evaluates only the licensed translations of `E_v` through `T_vw`; holes remain holes.
- A translation receipt lists exact images, alternatives, holes, and incompatibilities.

Branch/merge:

- A checkpoint induces a shared prefix constraint.
- Branches add independent constraint/evidence deltas.
- Merge is a fiber product of branch history families over the common prefix plus an explicit merge policy. If no compatible product exists, conflict is returned; if corruption leaves several products, all remain admissible.

Continuity:

- `CONT_κ(x,y)` is derivable only when every witness required by the declared profile `κ` is present in an admissible history linking `x` and `y`.
- Different profiles may license descent, commitment-continuity, behavioral-continuity, or no relation. None entails numerical identity or authority unless those are separately specified and witnessed.

## 4. How assumptions appear in the model

| Assumption | Structural contact |
|---|---|
| A1.1 | Query horizon and solver backend are frozen in the run manifest. Exhaustion returns `UNKNOWN_BUDGET`, never false. |
| A1.2 | `V`, immutable `(Σ_v,K_v,E_v)`, and separate `THEN/NOW` operators. |
| A1.3 | `K_v` admits/excludes histories; arbitrary logs do not become possible worlds automatically. |
| A1.4 | `T_vw` is a relation with exact/alternative/hole/incompatible outcomes and receipts. |
| A1.5 | Evidence removal expands `Ω`; corruption is a constraint weakening, not a negative fact. |
| A1.6 | `CONT_κ` requires an explicit profile and proof certificate. |
| A1.7 | Signatures, rules, translators, merge policy, and continuity profile are versioned inputs in the assumption register. |

## 5. Native consequences and preregistration

### Derived consequences

`NC-A1-1 EVIDENCE-WEAKENING` — With `K_v` fixed, removing evidence changes `Ω_v(E)` to a superset. Therefore evidence loss cannot create a new `FORCED(q)` result; it can only preserve it or weaken it to `ALTERNATIVE/NOT_PROVEN/UNKNOWN_BUDGET`.

`NC-A1-2 NO CREATION THROUGH A HOLE` — If a source field has no image under `T_vw`, its target value is not derivable merely from translation. A target result requires an independent `K_w` derivation.

`NC-A1-3 MERGE NON-INVENTION` — A merge cannot license a branch fact absent from compatible branch histories unless an explicit merge rule derives it and supplies a witness.

`NC-A1-4 LABEL INVARIANCE` — Type-preserving alpha-renaming leaves the admissible-history isomorphism class and all query statuses unchanged.

### Prospective native-test registration

`PRIMARY_NAT-A1` — In C2, corrupting Y must enlarge or leave unchanged the Y-compatible history family. It must not create a unique merged Persona, identity, authority, or new forced branch fact. The result must survive H1/H3 relabeling.

`PAYLOAD_SWAP` — Replace READY/A/B/C and Persona vocabulary with isomorphic unrelated labels. `NC-A1-1..4` must still hold.

`ASSUMPTION_MUTATION` — Make `T_vw` silently total by defaulting every hole. The first lost consequence must be `NC-A1-2`; C1/C4 become answer-encoding risks. This mutation is predicted to invalidate the model's historical-integrity claim.

`UNIQUE_WEAK_REGIME` — A genuinely continuous system whose decisive property is not expressible by finite/symbolic history constraints may defeat A1.1. VCHC must report `OUT_OF_SCOPE/UNKNOWN_BUDGET`, not manufacture threshold events.

## 6. Failure/falsification conditions

The position is materially weakened or abandoned as a general World Model if any of the following is evidenced prospectively:

1. **Monotonicity violation:** with `K_v` unchanged, removal/corruption of evidence creates a new forced conclusion. That falsifies the advertised semantics or its implementation.
2. **Answer encoding:** unseen isomorphic payload swaps require adding conclusion-specific constraints to recover advertised results. Then VCHC is a fixture-specific rule container, not a native model.
3. **Constraint-language capture:** held-out cases repeatedly reverse conclusions solely under equally plausible type/factorization choices, with no principled selection rule. VCHC must be reduced to an audit layer or merged with another model.
4. **Continuous failure:** a late continuous-change case has refinement-invariant consequences that VCHC cannot reproduce without a post-hoc event threshold or a complete external simulator. Then the finite-history foundation is abandoned for that domain.
5. **Intractable openness:** realistic bounded cases cannot be solved or soundly approximated within the preregistered budget, and compression changes query status. Timeout remains `UNKNOWN_BUDGET`, but repeated failure defeats practical foundational use.

## 7. Limitations

- The constraint language can relocate ontology rather than remove it.
- `Ω` may grow exponentially under incomplete evidence and branching.
- The model is stronger at reconstruction and explicit uncertainty than at continuous embodied dynamics or spontaneous novelty.
- A continuity profile can encode desired answers if not independently justified.
- Human familiarity, governance legitimacy, and subjective experience are not derived by formal admissibility alone.
- The model does not prove that the world itself is a possible-history family.

## 8. Self-critique

VCHC may be an unusually disciplined semantic audit/reconstruction engine rather than a complete world model. Its most attractive results—non-overwrite, no invention through holes, merge non-invention—partly arise because the model was designed around the contract's failure cases. G3 must therefore be tested on unseen isomorphic and non-isomorphic domains. It also risks restating “only infer what constraints license” unless its solver produces useful exclusions or invariants not manually encoded.

## 9. Alternative explanations considered

- **Persistent object + event sourcing:** simpler operationally, but risks treating object identity as given.
- **Witnessed rewrite/causal fabric:** stronger for native ontogenesis and causal precedence; VCHC may underdescribe actual production.
- **Continuous viability/process field:** stronger for C3 and embodiment; weaker for semantic version translation unless augmented.
- **Operational/affordance semantics:** characterizes continuity by possible interactions rather than history; may better capture capability but discard provenance distinctions.
- **Model ecology:** several specialized kernels may outperform one VCHC. VCHC does not claim universal sufficiency.

## 10. Theory contribution

The candidate contributes a precise separation among:

1. immutable then-semantics,
2. partial current translation,
3. evidence loss as possibility expansion,
4. explicit continuity profiles rather than identity,
5. merge as constrained product rather than state union.

Its useful negative claim is that historical integrity plus current reinterpretation does not require a persistent identical object; it requires versioned semantics, explicit translation holes, and proof-carrying query results.

## 11. Testable/implementable contact

Finite pilot implementation:

1. Encode `Σ_v`, `K_v`, evidence, and translators as typed JSON plus SMT constraints.
2. Enumerate or symbolically solve `Ω_v(E)`.
3. For query `q`, check satisfiability of `K∧E∧q` and `K∧E∧¬q` to classify forced/impossible/alternative.
4. Emit model/countermodel, translation, and continuity certificates.
5. Run branch merge by solving both deltas over the shared checkpoint and explicit merge rules.

```text
query(v, E, q):
  if not typeable(q, Σ[v]): return UNDEFINED
  pos = SAT(K[v] + E + q)
  neg = SAT(K[v] + E + not(q))
  return classify(pos, neg, provenance(E))
```

Replay targets: all C1–C6, H1–H7, and an unseen payload-swapped seed. Exact spec, solver version, seed, budget, and hashes must be frozen before evaluation.

## 12. What would change the conclusion

- Strong held-out performance with low constraint sensitivity would increase confidence that VCHC is a useful low-level candidate.
- Frequent factorization/type-induced reversals would narrow it to a reconstruction layer.
- A continuous or interaction-first candidate that derives the same history/revision protections more cheaply would favor merger or replacement.
- Evidence that human-recognized Persona continuity systematically depends on features not representable as constraints/history would reject its generality.
- Evidence that one stable carrier is necessary for security or governance would add a carrier assumption; it would not be silently inferred from continuity.

## Concise C1–C6 responses

### C1

`THEN(R1)` returns `READY` with its A/B proof. Under R2, A and B translate but C is a `HOLE`; both READY and not-READY histories remain unless R2 independently fixes C. Historical READY is not overwritten and current READY is not proven.

### C2

K supplies a shared-prefix constraint; X supplies a complete delta; corrupt Y weakens its delta and expands alternatives. The merge is the set of compatible fiber products. Decision conflict remains disputed; no unique identity or authority follows from runtime IDs or memory union.

### C3

Samples constrain an underlying signal family. One-versus-three crossings is threshold/sampling-relative. Only properties true in every signal consistent with both evidence and the declared regularity constraints are forced; otherwise crossing count remains alternative. No decisive event is inserted by default.

### C4

The old `owner` record remains reconstructible under its old schema. Exact translations produce one principal, one-to-many translations preserve all licensed sets, and unavailable mappings yield holes. Downstream claims depending on a hole are not proven and receive a dependency receipt.

### C5

Each local theory remains nonempty. Pairwise translation does not imply a global model: if the translator cycle has no compatible assignment, the global product is empty and no larger account is licensed. Alternative global accounts are all retained when several products exist.

### C6

The shared checkpoint proves common descent only if its witness is available. Divergence produces two history families; memory consolidation adds explicit cross-branch evidence but does not prove sameness. `CONT_κ` may license selected descent/continuity profiles; identity and authority remain not proven.
