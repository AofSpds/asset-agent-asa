# MS0 30-Minute Pilot — Candidate Seeds

STATE = PILOT_DIVERGENCE / NON_NORMATIVE / NO_FUTURE_PRIOR / NO_VALIDATION_CLAIM

CANDIDATES_REQUESTED = 8

CANDIDATES_GENERATED = 8

DISTINCTNESS_NOTE = The field spans eight computational/formal families. C01/C04/C05 all handle incomplete knowledge, but respectively make proof status, solution space, and local-context compatibility primary; they are retained because their update, query, and failure semantics materially differ. No family has more than two immediate variants.

## C01 — Paraconsistent Provenance Calculus

- CANDIDATE_ID = C01
- WORKING_LABEL = Paraconsistent Provenance Calculus
- ONE_SENTENCE_THESIS = Model the world-facing record as provenance-bearing assertions in a contradiction-tolerant logic where support and refutation can coexist without explosion.
- COMPUTATIONAL_OR_FORMAL_SHAPE = Four-valued/paraconsistent logic plus append-only assertion/retraction/supersession ledger and derivation graph.
- WHAT_IT_TREATS_AS_PRIMARY_IF_ANY = Typed assertions, their provenance, and inference rules; a singular complete world state is not required.
- CURRENT_CONCEPTS_DEMOTED_REMOVED_OR_REINTERPRETED = Instance, Event, Relation, Boundary, and Memory become optional predicates or derived views rather than fixed primitives.
- STRONGEST_APPARENT_UPSIDE = UNKNOWN, DISPUTED, competing interpretations, and historical meaning can be represented explicitly with inspectable derivations.
- STRONGEST_APPARENT_DOWNSIDE = It can model knowledge about the world better than the world itself and may hide dynamics behind ever-growing assertion machinery.
- WHY_MATERIALLY_DISTINCT = Its semantics are proof-theoretic and contradiction-tolerant, unlike state transition, probabilistic, distributed, or compositional models.
- MAJOR_ASSUMPTION = Useful world-model behavior can be mediated through assertion status and provenance without requiring a privileged underlying state.
- OPEN_QUESTION = Can continuous change, individuation, and constitutive coupling be expressed without turning every phenomenon into an artificial claim?

## C02 — Causal Event Reconstruction Algebra

- CANDIDATE_ID = C02
- WORKING_LABEL = Causal Event Reconstruction Algebra
- ONE_SENTENCE_THESIS = Treat immutable, partially ordered occurrences as the substrate and compute all current structures as explicitly versioned folds/materializations over selected causal histories.
- COMPUTATIONAL_OR_FORMAL_SHAPE = Append-only event DAG, causal/temporal partial order, deterministic or declared-nondeterministic fold functions, versioned projections.
- WHAT_IT_TREATS_AS_PRIMARY_IF_ANY = Occurrences and precedence/causal dependencies.
- CURRENT_CONCEPTS_DEMOTED_REMOVED_OR_REINTERPRETED = Relation, Instance, Boundary, Memory, and current state become projections; Succession becomes an event-pattern rather than necessary primitive.
- STRONGEST_APPARENT_UPSIDE = Historical reconstruction, branching, replay, and semantic-currentization experiments are direct and auditable.
- STRONGEST_APPARENT_DOWNSIDE = Event identity/granularity is already an ontology choice, and current-state queries may accumulate projection complexity.
- WHY_MATERIALLY_DISTINCT = It is history-generative: structure is computed from a causal log rather than asserted, solved, inferred probabilistically, or produced by local actors.
- MAJOR_ASSUMPTION = Relevant change can be captured as stable occurrence records with enough ordering and interpretation metadata.
- OPEN_QUESTION = What precedes event individuation when participant, boundary, and observation semantics are themselves unsettled?

## C03 — Coinductive Behavioral World

- CANDIDATE_ID = C03
- WORKING_LABEL = Coinductive Behavioral World
- ONE_SENTENCE_THESIS = Define modeled things by the observations and transitions they can continue to produce, with identity approximated by behavioral equivalence rather than stored essence.
- COMPUTATIONAL_OR_FORMAL_SHAPE = Coalgebra/labeled transition system, observation functions, guarded transitions, traces, bisimulation or simulation relations.
- WHAT_IT_TREATS_AS_PRIMARY_IF_ANY = Ongoing observable behavior and possible next transitions.
- CURRENT_CONCEPTS_DEMOTED_REMOVED_OR_REINTERPRETED = Instance becomes a behavior state/observation point; identity becomes equivalence; Process is central without requiring Process as a named domain primitive.
- STRONGEST_APPARENT_UPSIDE = Naturally represents ongoing becoming, interaction, and multiple implementations with equivalent externally relevant behavior.
- STRONGEST_APPARENT_DOWNSIDE = Internal history, provenance, disputed interpretation, and meaningful hidden structure are easy to erase under coarse behavioral equivalence.
- WHY_MATERIALLY_DISTINCT = It is coinductive and future-behavior oriented rather than fact-, event-, context-, probability-, or composition-first.
- MAJOR_ASSUMPTION = A declared observation interface is sufficient to discriminate what matters in the modeled world.
- OPEN_QUESTION = Who chooses the observation algebra, and can its revision preserve earlier identity judgments without circularity?

## C04 — Revisable Constraint / Possible-World Ensemble

- CANDIDATE_ID = C04
- WORKING_LABEL = Revisable Constraint / Possible-World Ensemble
- ONE_SENTENCE_THESIS = Represent current knowledge as revisable constraints whose satisfying models are the currently possible worlds, leaving identity and structure underdetermined until forced.
- COMPUTATIONAL_OR_FORMAL_SHAPE = Constraint store using SAT/SMT/Datalog-style finite domains, constraint deltas, named assumption sets, model enumeration or symbolic solution regions.
- WHAT_IT_TREATS_AS_PRIMARY_IF_ANY = Constraints and the set of admissible solutions, not a single privileged state.
- CURRENT_CONCEPTS_DEMOTED_REMOVED_OR_REINTERPRETED = UNKNOWN becomes multiplicity of solutions; disputed states become incompatible named constraint sets; conventional entities/relations are variables and constraints.
- STRONGEST_APPARENT_UPSIDE = Delays ontology closure while still constraining possibilities and generating counterexamples to assumptions.
- STRONGEST_APPARENT_DOWNSIDE = Expressivity can cause combinatorial blow-up, and modeling choices may reappear invisibly in the constraint language/domain bounds.
- WHY_MATERIALLY_DISTINCT = It is model-theoretic and solution-set based; update changes admissible worlds rather than directly mutating objects or replaying occurrences.
- MAJOR_ASSUMPTION = Important semantics can be stated as checkable constraints over a bounded domain without unacceptable loss.
- OPEN_QUESTION = How should historical, processual, and continuous phenomena be bounded without predetermining the result?

## C05 — Contextual Sheaf of Local Worlds

- CANDIDATE_ID = C05
- WORKING_LABEL = Contextual Sheaf of Local Worlds
- ONE_SENTENCE_THESIS = Model locally coherent descriptions over explicit contexts and treat global worldhood as a gluing question whose failure is meaningful rather than automatically repaired.
- COMPUTATIONAL_OR_FORMAL_SHAPE = Finite context poset/cover, local sections, restriction maps, compatibility checks, optional sheaf/presheaf gluing and obstruction reports.
- WHAT_IT_TREATS_AS_PRIMARY_IF_ANY = Context-indexed local descriptions and translation/restriction between overlapping contexts.
- CURRENT_CONCEPTS_DEMOTED_REMOVED_OR_REINTERPRETED = Perspective, Scope, and Scale need not be entity attributes; they become indices/maps, while global identity/relation may exist only when compatible gluing succeeds.
- STRONGEST_APPARENT_UPSIDE = Precisely preserves local truth, perspective, multi-scale representation, and irreducible disagreement without forcing a false global state.
- STRONGEST_APPARENT_DOWNSIDE = Context-cover design is a strong hidden commitment; mathematical and implementation complexity can outrun the pilot's practical needs.
- WHY_MATERIALLY_DISTINCT = Local-to-global compatibility—not assertions, events, transitions, probability, or actors—is the governing semantic operation.
- MAJOR_ASSUMPTION = Relevant contexts and their overlaps can be made explicit enough for restriction/gluing to carry meaning.
- OPEN_QUESTION = Are non-gluing obstructions useful domain evidence or artifacts of a badly chosen context topology?

## C06 — Probabilistic Generative State-Space

- CANDIDATE_ID = C06
- WORKING_LABEL = Probabilistic Generative State-Space
- ONE_SENTENCE_THESIS = Treat world evolution and observation as a generative process over latent states, preserving uncertainty as distributions and alternative posterior histories.
- COMPUTATIONAL_OR_FORMAL_SHAPE = Dynamic Bayesian network/probabilistic program, latent-state transition kernel, observation model, posterior inference and smoothing.
- WHAT_IT_TREATS_AS_PRIMARY_IF_ANY = Random variables, generative dependencies, and probability distributions.
- CURRENT_CONCEPTS_DEMOTED_REMOVED_OR_REINTERPRETED = Instance/Relation/Event become latent or observed variables; Perspective becomes an observation model; UNKNOWN becomes uncertainty only where probability is justified.
- STRONGEST_APPARENT_UPSIDE = Supports noisy evidence, uncertain causality, prediction, retrospective inference, and explicit comparison of competing hypotheses.
- STRONGEST_APPARENT_DOWNSIDE = Probability can falsely quantify ignorance or disagreement; priors and factorization encode strong ontology and causal commitments.
- WHY_MATERIALLY_DISTINCT = It provides quantitative generative/inferential semantics absent from the logical, algebraic, contextual, and distributed candidates.
- MAJOR_ASSUMPTION = Uncertainty relevant to the World Model is sufficiently probabilistic and the generative factorization is defensible.
- OPEN_QUESTION = Which non-probabilistic states—undefined, disputed, prohibited—must remain outside the probability layer?

## C07 — Operationally Closed Actor Ecology

- CANDIDATE_ID = C07
- WORKING_LABEL = Operationally Closed Actor Ecology
- ONE_SENTENCE_THESIS = Model the world as locally stateful message-processing cells whose maintained interaction protocols generate higher-order organization, boundaries, and histories.
- COMPUTATIONAL_OR_FORMAL_SHAPE = Actor/message-passing system with local transition functions, mailboxes, protocol traces, dynamic actor creation/retirement, and observer-defined aggregate projections.
- WHAT_IT_TREATS_AS_PRIMARY_IF_ANY = Local operations and messages; global state is not primary.
- CURRENT_CONCEPTS_DEMOTED_REMOVED_OR_REINTERPRETED = Boundary and membership emerge from sustained protocol closure/coupling; Relation becomes message/protocol regularity; Instance becomes an addressable local process or aggregate projection.
- STRONGEST_APPARENT_UPSIDE = Makes autonomy-with-coupling, emergence, concurrency, and fission/merge-like reorganization executable without a global clock.
- STRONGEST_APPARENT_DOWNSIDE = Actor address, mailbox, protocol, and local-state choices can silently impose identity and boundary; replay of concurrency is difficult.
- WHY_MATERIALLY_DISTINCT = It is operational and distributed: world structure arises from local computation and communication rather than a centralized semantic representation.
- MAJOR_ASSUMPTION = Local message-passing closure is an adequate substrate for the phenomena of interest.
- OPEN_QUESTION = Can semantic disagreement and historical reconstruction be preserved without installing a privileged external observer/log?

## C08 — Compositional Transformation Category

- CANDIDATE_ID = C08
- WORKING_LABEL = Compositional Transformation Category
- ONE_SENTENCE_THESIS = Treat composable transformations and their laws as primary, using interfaces only as the domains/codomains required for composition rather than assuming enduring objects.
- COMPUTATIONAL_OR_FORMAL_SHAPE = Typed category/free category or symmetric monoidal category, morphism composition, string diagrams, equations and optional enriched annotations.
- WHAT_IT_TREATS_AS_PRIMARY_IF_ANY = Transformations, composability, and invariant laws.
- CURRENT_CONCEPTS_DEMOTED_REMOVED_OR_REINTERPRETED = Objects/Instances are interfaces; Relations and Events may be morphisms of different types; boundaries are typing/composition constraints.
- STRONGEST_APPARENT_UPSIDE = Strong modularity and multi-scale compositional reasoning; the same laws can describe atomic and aggregated transformations.
- STRONGEST_APPARENT_DOWNSIDE = Bare categorical structure says little about history, uncertainty, observation, or empirical discrimination without substantial enrichment.
- WHY_MATERIALLY_DISTINCT = Its semantics arise from universal composition laws and equivalence of diagrams, not state storage, inference, local contexts, or runtime actors.
- MAJOR_ASSUMPTION = The most important world regularities are preserved under explicit composition and can be expressed by tractable equations.
- OPEN_QUESTION = What minimal enrichment supplies history and non-closure without turning the category into a decorative wrapper around another model?
