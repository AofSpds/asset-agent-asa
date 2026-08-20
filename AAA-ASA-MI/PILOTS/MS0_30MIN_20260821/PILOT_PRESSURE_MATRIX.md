# MS0 30-Minute Pilot — Lightweight Common Pressure Matrix

STATE = PILOT_ROUTING_ONLY / NON_NORMATIVE / NOT_FULL_MS0_MAIN_ROUND / NO_PASS_FAIL_CLAIM

ROUTING_STATES = VIABLE / VIABLE_WITH_CONCERNS / BLOCKED / NOT_PROVEN

ASSESSMENT_LIMIT = Each result is a bounded seed-level observation. No implementation, formal proof, benchmark, or external literature verification was performed.

## Common Matrix

Legend: `S` = apparent strength, `C` = concern but plausible extension, `W` = material weakness/not yet shown. These marks support the routing state only and are not validation scores.

| ID | P-G1 Coherence | P-G2 Change/history | P-G3 Non-closure | P-G4 Bounded toy | P-G5 Assumptions visible | P-G6 Lock-in risk | P-G7 Falsifiability | P-G8 Low-level generality | PILOT ROUTING |
|---|---|---|---|---|---|---|---|---|---|
| C01 | S | S | S | S | S | C: truth/proof vocabulary | C: dynamics discriminator needed | S | VIABLE_WITH_CONCERNS |
| C02 | S | S | C: absence vs unknown | S | S | C: event identity/granularity | S | S | VIABLE_WITH_CONCERNS |
| C03 | S | C: traces external to core | C: lifted observation domain | S | S | C: observer/bisimulation choice | S | S | VIABLE_WITH_CONCERNS |
| C04 | S | S | S | S | S | C: constraint language/bounds | S | S | VIABLE |
| C05 | S | C: temporal indexing required | S | C: finite contexts only | S | C: context topology | S | S | VIABLE_WITH_CONCERNS |
| C06 | S | S | C: probability is not dispute | S | S | C: priors/factorization | S | S | VIABLE_WITH_CONCERNS |
| C07 | S | C: concurrency replay | C: local unknown semantics | S | S | C: address/protocol identity | S | S | VIABLE_WITH_CONCERNS |
| C08 | S | W: not intrinsic | W: enrichment required | S | S | C: type/composition ontology | W: bare form too permissive | S | NOT_PROVEN |

LOCK_IN_INTERPRETATION = P-G6 asks whether hidden lock-in is acceptably exposed, not whether a candidate has no commitments. Every non-trivial candidate has commitments.

## Candidate Findings

### C01 — Paraconsistent Provenance Calculus

- PRESSURE_OBSERVATION = A finite four-valued assertion ledger can be implemented quickly and keeps support/refutation/provenance inspectable across revisions. Contradiction does not force closure. The decisive missing test is whether non-propositional change can be represented without schema inflation.
- POSITIVE_PILOT_FINDING = Unusually clean separation of claim, evidence, provenance, conflict, and current derivation; historical interpretations can coexist without rewriting their inputs.
- NEGATIVE_PILOT_FINDING = Risks substituting an epistemic/claim model for a World Model and turning processes or constitution into predicate bookkeeping.
- ROUTING_STATE = VIABLE_WITH_CONCERNS
- REVISION_OR_ABANDON_TRIGGER = Abandon or hybridize if the common toy worlds require pervasive opaque predicates or cannot distinguish world change from changes in belief.

### C02 — Causal Event Reconstruction Algebra

- PRESSURE_OBSERVATION = A small event DAG plus two projection versions directly demonstrates replay, branching history, and currentization. However, event boundaries and missing-event semantics must be declared rather than smuggled in.
- POSITIVE_PILOT_FINDING = Best immediate history/replay surface; makes semantic changes testable as competing projections over preserved records.
- NEGATIVE_PILOT_FINDING = Can freeze Event as de facto ontology and make relation/continuity semantics projection-specific; the absence of an event is not automatically UNKNOWN or ABSENT.
- ROUTING_STATE = VIABLE_WITH_CONCERNS
- REVISION_OR_ABANDON_TRIGGER = Weaken if the same phenomenon requires incompatible event individuations across views that cannot be reconciled without rewriting the log.

### C03 — Coinductive Behavioral World

- PRESSURE_OBSERVATION = A finite labeled transition system and bisimulation test are bounded and coherent. Trace retention and non-closure statuses are not supplied by bare coalgebra but can be explicit observation outputs without changing the core.
- POSITIVE_PILOT_FINDING = Makes ongoing behavior and observer-relevant equivalence primary, avoiding an assumption of stable inner essence and enabling executable identity challenges.
- NEGATIVE_PILOT_FINDING = A chosen observation interface can erase memory, dissent, provenance, and constitutive internal differences while declaring systems equivalent.
- ROUTING_STATE = VIABLE_WITH_CONCERNS
- REVISION_OR_ABANDON_TRIGGER = Reject a proposed observation algebra if two cases the research treats as materially different become bisimilar for accidental reasons.

### C04 — Revisable Constraint / Possible-World Ensemble

- PRESSURE_OBSERVATION = A bounded solver model can preserve multiple admissible worlds, named incompatible assumption sets, constraint deltas, and historical solver inputs. It constrains outcomes and produces countermodels, satisfying the seed-level falsifiability test.
- POSITIVE_PILOT_FINDING = Strongest low-commitment mechanism for keeping ontology underdetermined while still deriving consequences and counterexamples; UNKNOWN can remain a set of live possibilities.
- NEGATIVE_PILOT_FINDING = Domain bounds and constraint language may encode the ontology invisibly, while realistic temporal or recursive models can become intractable.
- ROUTING_STATE = VIABLE
- REVISION_OR_ABANDON_TRIGGER = Downgrade if modest toy worlds require unbounded quantification, solver-specific encodings, or constraints so weak that every structure remains admissible.

### C05 — Contextual Sheaf of Local Worlds

- PRESSURE_OBSERVATION = Finite contexts, local assignments, restriction maps, and failed gluing are toy-implementable. Temporal history requires indexing versions or contexts; the context cover is an exposed but expensive assumption.
- POSITIVE_PILOT_FINDING = Most distinctive treatment of perspective, scope, scale, and disagreement: local validity need not imply a fabricated globally consistent world, and obstruction itself becomes evidence.
- NEGATIVE_PILOT_FINDING = Context topology and restriction maps may pre-decide what can agree; sophistication risks obscuring simple errors behind mathematical language.
- ROUTING_STATE = VIABLE_WITH_CONCERNS
- REVISION_OR_ABANDON_TRIGGER = Abandon if gluing failures track arbitrary context design rather than stable, interpretable domain disagreements.

### C06 — Probabilistic Generative State-Space

- PRESSURE_OBSERVATION = A small hidden-state model supports update, prediction, smoothing, and alternate posterior histories. Explicit sentinel/status layers are still required because dispute and undefinedness are not probability values.
- POSITIVE_PILOT_FINDING = Only candidate in the field with native quantitative treatment of noisy observation, uncertain latent cause, prediction, and retrospective inference.
- NEGATIVE_PILOT_FINDING = Priors, variable selection, factorization, and forced numeric belief can create false precision and conflate uncertainty with conflict or missing semantics.
- ROUTING_STATE = VIABLE_WITH_CONCERNS
- REVISION_OR_ABANDON_TRIGGER = Reject probability for a state class when calibration is impossible or when distinct UNKNOWN/DISPUTED/UNDEFINED cases collapse into the same posterior.

### C07 — Operationally Closed Actor Ecology

- PRESSURE_OBSERVATION = A small deterministic actor simulator can expose local transitions, message traces, dynamic composition, and absence of a global clock. Reproducible concurrency and observer-independent history remain concerns.
- POSITIVE_PILOT_FINDING = Directly executable model of autonomy-with-coupling, distributed emergence, local change, and reorganization without requiring one total world state.
- NEGATIVE_PILOT_FINDING = Actor addresses and message boundaries silently resemble pre-given entities/relations; global evidence capture can reintroduce the central observer the model avoids.
- ROUTING_STATE = VIABLE_WITH_CONCERNS
- REVISION_OR_ABANDON_TRIGGER = Downgrade if meaningful aggregate identity/boundary can be obtained only from a privileged omniscient log or hand-coded observer.

### C08 — Compositional Transformation Category

- PRESSURE_OBSERVATION = A free typed category and diagram-equivalence checker are bounded and coherent, but bare composition does not provide historical reconstruction, uncertainty/conflict, or a strong falsification surface. Adding all three may merely wrap another candidate.
- POSITIVE_PILOT_FINDING = Offers unusually strong compositional compression and may reveal invariants that survive changes of scale or implementation.
- NEGATIVE_PILOT_FINDING = At seed level it is too underdetermined and risks becoming elegant notation over hidden semantics supplied elsewhere.
- ROUTING_STATE = NOT_PROVEN
- REVISION_OR_ABANDON_TRIGGER = Revive only with a minimal, non-decorative enrichment whose history and non-closure behavior can be tested against the same toy worlds.

## Pilot-Only Representatives

PILOT_POSITIVE_REP = C05 — Contextual Sheaf of Local Worlds

PILOT_POSITIVE_REP_REASON = It opens the most unusual useful research surface in this field: locally valid descriptions, explicit translations, and meaningful failure of global consistency provide a precise counterweight to premature single-world closure. This is upside-only routing; its context-topology and complexity risks remain fully preserved.

PILOT_ROBUSTNESS_REP = C04 — Revisable Constraint / Possible-World Ensemble

PILOT_ROBUSTNESS_REP_REASON = It remains non-trivial and falsifiable while requiring the fewest seed-level semantic commitments: a bounded solver can preserve multiple admissible structures, named assumptions, historical constraint versions, and countermodels without choosing a single ontology. Its constraint-language and scaling risks remain material.

DISTINCT_REPRESENTATIVES = TRUE

PILOT_AUTHORITY_WARNING = These representatives are ephemeral observations from a short, non-executable pressure pass. They are not MS0 finalists and must not seed future ranking or preference without renewed comparison.

## Cross-Candidate Observations

- MOST_INTERESTING_POSITIVE_DISCOVERY = Non-closure can be computationally productive rather than merely a status flag: C04 turns it into alternative satisfying worlds, while C05 turns non-gluing into explicit evidence.
- MOST_IMPORTANT_NEGATIVE_DISCOVERY = Every family relocates ontology rather than eliminating it: predicates, event individuation, observation algebras, constraint languages, context covers, priors, actor addresses, or composition types are all potential hidden freeze points.
- COMMON_MISSING_EVIDENCE = No candidate faced shared executable scenarios, mutation histories, query contracts, or cost measurements; therefore routing beyond seed-level plausibility is not proven.
