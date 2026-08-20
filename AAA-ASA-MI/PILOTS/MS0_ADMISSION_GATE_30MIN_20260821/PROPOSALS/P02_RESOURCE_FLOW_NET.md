# P02 — Resource-Flow Net World

STATE = MODEL_PROPOSAL_ONLY / NOT_ADMITTED / NO_CANDIDATE_STATUS

AUTHOR_SUBMISSION_STATE = SUBMITTED_FOR_FRESH_VALIDATOR_REVIEW

SOURCE_IDEA = I09

## A1. WORLD MODEL THESIS

WHAT_IS_MODELED = The current distribution of typed resources/capacities, the conditions under which transformations are possible, concurrent change, causal dependency, and unresolved location/quantity alternatives.

HOW_WORLD_OR_MODEL_STATE_OR_EQUIVALENT_IS_CONSTITUTED = A semantic package contains a versioned typed net `N_v` and a marking `M_t`. Places express admissible conditions or resource loci; typed tokens express quantities/capabilities; transitions define enabling, consumption, production, and inhibitor/read conditions. The equivalent of world state is `(N_v, M_t, unresolved_set, occurrence_prefix)`. This is proposed as world semantics because it defines what currently obtains, what can jointly occur, and which histories are causally possible—not merely how records are stored.

## A2. MATERIAL DISTINCTNESS

NEAREST_PROPOSAL_OR_IDEA = I01 / P01 Algebraic Rewrite World.

EXACT_MATERIAL_DIFFERENCE = P02 makes resource conservation, enabling, conflict, and true concurrency native. P01 permits general sequential/nondeterministic structural rewrites and must separately encode independence or conservation.

DIFFERENT_BEHAVIOR_OR_FAILURE_MODE_CAUSED_BY_DIFFERENCE = In P02, two transitions with disjoint input conditions are concurrent and yield an occurrence partial order; competing transitions are disabled by resource conflict. P01 may interleave them and needs proof that interleavings are equivalent. Conversely, P02 fails when change cannot be decomposed into stable place/transition structure without proliferating net versions.

## A3. COMMITMENT SURFACE

Commitment resides in place meanings, token colors/types, transition boundaries, arc weights, enabling conditions, the policy for token distinguishability, and the declared semantics of net evolution. A global clock is not assumed, but atomic transition firing is. Boundaries and identities may be hidden in place partitioning and token colors; these are explicit risk surfaces, not neutral implementation details.

## A4. CHANGE / HISTORY

WHAT_CAN_CHANGE = Markings change through enabled firings. The net structure itself may change only through a versioned meta-transition that creates a successor net package.

WHAT_HISTORY_REMAINS = An occurrence net records transition instances, consumed/produced token references or aggregate quantities, causal predecessors, conflicts, evidence, and net version.

HOW_PRIOR_STATE_OR_EVIDENCE_IS_RECONSTRUCTED = A marking can be reconstructed from the initial marking plus any causally closed occurrence prefix. Independent firings do not need a fabricated total order.

HOW_CURRENT_INTERPRETATION_CAN_CHANGE_WITHOUT_RETROACTIVE_REWRITE = A successor net maps old places/colors/transitions where justified. Historical markings remain interpreted under their original net. A new projection may reinterpret them only by declaring the mapping and loss.

## A5. NON-CLOSURE

P02 uses a separate symbolic marking layer:

- `Certain(M)` for determined token counts/types.
- `Alternatives({M1..Mn}, open_tail)` for multiple admissible markings.
- `Disputed({support(Mi,evidence)})` for incompatible supported markings.
- `Undefined(query, reason)` when the net vocabulary cannot interpret a query.

Unknown location is not represented by zero tokens. Zero means known absence only when the net/package declares a closed counting domain. Firing over an alternative set produces the union of successor alternatives and retains provenance.

## A6. BOUNDED OPERATIONALIZATION

### Worked micro-probe

```text
Places: outside, chamber, consumed
Token color: sample(id)
Transitions:
  enter(s): outside[s] -> chamber[s]
  react(s): chamber[s] -> consumed[s]
  inspect_chamber: read chamber[*] -> observation(count)

M0 = outside[s1] + outside[s2]
```

`enter(s1)` and `enter(s2)` are concurrently enabled. `react(s1)` is not enabled until `enter(s1)` occurs. After only the observation `count(chamber)=1` without token identity, represent:

```text
Alternatives({
  outside[s2] + chamber[s1],
  outside[s1] + chamber[s2]
}, open_tail=false)
```

Firing `react` branches over the alternatives but preserves which causal hypothesis supports each successor. An occurrence prefix containing `enter(s1)` reconstructs the first marking without assuming when independent `enter(s2)` occurred.

CORE_SEMANTICS_TOUCHED = enabling, resource conflict, concurrency, partial-order history, alternative markings, and known-zero versus unknown distinction.

## A7. COMMON QUERY CONTACT

1. WHAT_IS_REPRESENTED_NOW = Return net version plus the current certain/alternative/disputed marking expression.
2. WHAT_CHANGED = Return newly added occurrence instances and marking delta; concurrent occurrences are returned as a partial order, not forced sequence.
3. WHAT_WAS_REPRESENTED_AT_TIME_T = Reformulate `T` as a causally closed occurrence cut or a declared external time projection; reconstruct the marking at that cut.
4. WHAT_REMAINS_UNRESOLVED = Return alternative/disputed markings, open tails, and token/count variables with supporting observations.
5. WHAT_CHANGES_UNDER_ANOTHER_CONTEXT = Apply a named projection that may aggregate token colors/places; return the projection version and whether distinctions were lost.
6. WHAT_ASSUMPTIONS_WERE_USED = Return net version, closed-domain declarations, token-identity policy, projection, and observation evidence.

## A8. FALSIFICATION / ABANDONMENT

ABANDONMENT_EXPERIMENT = Run a shared fission/merge plus contextual-redescription scenario. If representing ordinary semantic change requires frequent whole-net migration, or if preserving meaningful identity requires unique colored tokens everywhere such that the net becomes an entity graph with transitions as decoration, merge P02 into a more general transition proposal. If two independently enabled changes cannot be represented without a hidden total clock, abandon the claimed concurrency advantage.

## A9. ASSUMPTION REGISTER

| ASSUMPTION_ID | STATEMENT | SOURCE | WHY_NEEDED | WHAT_FAILS_IF_FALSE | REVERSIBILITY |
|---|---|---|---|---|---|
| P02-AS1 | Important changes can be factored into locally enabled resource transformations. | MODEL_FAMILY_ASSUMPTION | Gives the net causal/concurrency semantics. | Holistic or continuous change is distorted. | Low-medium: central to the proposal. |
| P02-AS2 | Partial-order occurrence history is preferable to a mandatory global total time. | INHERITED_RESEARCH_HYPOTHESIS | Preserves concurrency without false sequence. | Queries may require an external total-time model. | High: add an explicit time projection without rewriting occurrences. |
| P02-AS3 | Zero, unknown, and disputed markings must remain distinct. | CODEX_PROPOSAL | Prevents token absence from becoming false closure. | Symbolic marking layer may be unnecessary complexity. | High: can simplify in a successor while preserving old status. |
| P02-AS4 | Place and transition individuation can be made explicit and revisable. | MODEL_FAMILY_ASSUMPTION | Net semantics require them. | Hidden ontology becomes irreducible. | Medium: successor net/version mapping, possibly lossy. |
| P02-AS5 | Current research vocabulary is not mandated as net primitives. | OWNER_EXPLICIT | Prevents names from choosing ontology. | A later required primitive needs explicit encoding. | High. |

## A10. REVISION / SUCCESSOR PATH

Net packages are immutable and content-addressed. A successor package records parent digest, place/color/transition mappings, conservation changes, and unmapped elements. Occurrences always retain their source net version. If a mapping is partial, historical answers stay available in the old vocabulary and cross-version answers say `UNMAPPED` rather than deleting or guessing meaning.

## A11. NON-TRIVIALITY

P02 calculates enabled changes, unreachable markings, resource invariants, conflicts, concurrency, causal dependence, and alternative successor sets. Place invariants and reachability can falsify proposed histories. The model discriminates a true resource conflict from merely unordered independent change and forces explicit treatment of known absence versus unresolved count/location.

## A12. LOW-LEVEL GENERALITY

The semantic kernel is typed resources, conditions, transformations, occurrence history, and unresolved markings. It has no Persona, ASA, agent, memory-system, workflow, investment, or authority-specific primitive. A biological reaction, document state, material flow, or abstract capability could use the same kernel under different declared net packages.

## AUTHOR SELF-CRITIQUE — ZERO VALIDATION AUTHORITY

AUTHOR_STRONGEST_CASE = P02 has concrete operational leverage—conservation, enabling, concurrency, conflict, and causal reconstruction—that a generic state model does not obtain for free.

AUTHOR_STRONGEST_OBJECTION = Petri-net semantics may work only for resource-like phenomena and may become a cumbersome diagram/data structure when meanings, viewpoints, or continuous processes dominate.

AUTHOR_HIDDEN_COMMITMENT_SUSPECTED = Atomic firings, stable place boundaries, token identity policy, and a privileged decomposition of change into input/output resources.

AUTHOR_WHAT_MAY_MAKE_THIS_NOT_A_WORLD_MODEL = If every domain supplies all substantive ontology through a bespoke net and the kernel only simulates it, P02 is a process-execution formalism rather than a world constitution model.

AUTHOR_ABANDONMENT_SIGNAL = Common scenarios cause net-version explosion, unique-token graphification, or loss of the claimed partial-order/conservation advantage.
