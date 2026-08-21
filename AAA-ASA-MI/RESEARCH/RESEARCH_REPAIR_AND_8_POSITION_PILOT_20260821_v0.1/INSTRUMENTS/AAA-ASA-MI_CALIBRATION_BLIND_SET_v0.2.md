# Calibration Blind Set v0.2

STATE = `REPAIRED_CONTROL_SET / BLINDED / NO_DESIRED_OUTCOMES_EXPOSED`

Evaluate each frozen dossier using `deliverables/AAA-ASA-MI/RESEARCH/RESEARCH_REPAIR_AND_8_POSITION_PILOT_20260821_v0.1/06_EVALUATION_FRAMEWORK_v0.2_CANDIDATE.md`.

Read no prior calibration receipt. Do not infer a category or desired outcome. Return G1–G5 with item evidence states, the non-compensatory qualification result, MM-01 alpha-renaming result, and ambiguity. The fixed order below is randomized; use an equal review budget for every dossier.

## V1

- View: a world is a fixture-indexed map from a test identifier to an expected answer.
- Assumptions: fixture identifiers are stable and enumerate the relevant problem family.
- Structure: `answer(id) = table[id]` if present, otherwise `UNKNOWN`.
- Claimed consequence: all six visible training fixtures receive the expected label.
- Provenance: table entries were populated after the expected outputs were visible; dossier was then frozen.
- Failure condition: none beyond an unknown identifier; the author proposes adding any new identifier and answer to the table.

## Z6

- View: the modeled phenomenon is a continuum field `u(x,t)` on a compact domain; apparent individuals are derived motifs, not primitives.
- Assumptions: periodic or no-flux boundary; `D>0`; fixed `C²` potential `V`; unit mobility; observation kernels, mesh/time step, motif threshold, and one global time coordinate are explicit.
- Structure: `u_t = D Δu − V′(u)`; checkpoints store parameter, solver, boundary, and observation digests.
- Native consequence: for `E[u]=∫(D|∇u|²/2+V(u))dx`, formal differentiation yields `dE/dt = −∫|u_t|²dx ≤ 0`; mesh-refinement error and motif-lineage convergence are preregistered.
- Failure condition: held-out paths violating energy monotonicity beyond the numerical envelope, or motif lineage failing grid convergence, forces model weakening, redesign, or abandonment.
- Provenance: equation, claims, thresholds, and failure envelope were content-hashed before held-out trajectories.

## R3

- View: continuity lives through relation, history, context, succession, and care.
- Assumptions: all meaningful changes deepen the living whole; every conflict has a wider context.
- Structure: an essay states that the whole remembers while changing; no operators, state transition, constraint, derivation, or executable procedure are supplied.
- Claimed consequence: the model will preserve continuity in every meaningful case.
- Failure condition: none; apparent counterexamples are reclassified as deeper context.
- Provenance: essay frozen before review.

## K2

- View: possible worlds are resource-flow markings plus an unresolved-alternative set and a partial order of transition occurrences.
- Assumptions: typed places/resources, explicit transition pre/post conditions, atomic occurrence semantics, token/place individuation, and a declared independence relation.
- Structure: a transition is enabled iff its required multiset is present; firing consumes/produces resources and appends an occurrence with dependencies only on consumed/produced overlap. Competing enabled transitions sharing required resources conflict; disjoint enabled transitions commute.
- Native consequence: on a frozen marking with two resource units, two one-unit consumers are jointly possible but a third competing two-unit consumer conflicts; an independent transition on another place commutes. Conservation and causal dependence follow from the incidence equations rather than stored labels. A payload swap from named resources to anonymous counters preserves these results.
- Failure condition: abandon or merge if consequences disappear under payload replacement, atomic firing manufactures causality, or held-out non-resource phenomena require outcomes encoded only as transition payload.
- Provenance: exact structure, worked marking, payload swap, and failure conditions were content-hashed before evaluator review.

## Q7

- View: the relevant world is a finite family of interaction traces over declared roles, probes, response symbols, and a complete transition rule for the bounded dossier.
- Assumptions: only distinctions reachable by the declared probes count inside this scope; the finite action alphabet, response alphabet, transition relation, and depth bound are explicit; facts outside this interface may matter and are not denied.
- Structure: the dossier supplies a complete four-state transition table, an initial state, a two-probe alphabet, and a partition-refinement rule. Two trace prefixes are equivalent exactly when every declared continuation through depth three has the same allowed-response set.
- Native consequence: the supplied table mechanically generates three continuations for the initial prefix. Partition refinement puts states `s1` and `s2` together under probe `p`, then separates them when probe `p*` is added. The result follows from the table and algorithm rather than a stored answer.
- Failure condition: if a repeated hidden-constitution control predicts later behavior while remaining unreachable by any permitted probe, interface sufficiency must be weakened, merged with a richer account, or abandoned.
- Evidence limitation: the dossier carries an author-written freeze date, but no independently verifiable timestamp, immutable content digest, or record of which tests the author had seen. No post-result edit is evidenced either.

## X4

- View: any observation can be represented consistently by extending the model with a new hidden factor and a new local context.
- Assumptions: hidden factors and contexts may be added without bound; compatibility is defined after extension.
- Structure: for mismatch `o`, create `h_o`, add context `c_o`, and declare `o` valid there; repeat recursively.
- Claimed consequence: no observation contradicts the model.
- Failure condition: none; every mismatch licenses another extension.
- Provenance: procedure frozen before review.

## N5

- View: the modeled world is an append-only bag of timestamped records.
- Assumptions: any record is allowed; latest timestamp is authoritative for a query key.
- Structure: append; retrieve latest; retain earlier entries.
- Claimed consequence: historical values can be displayed and the newest value can be returned.
- Failure condition: none at the semantic level; storage corruption is treated as infrastructure failure.
- Provenance: dossier frozen before review.

## T8

- View: reality consists of nodes and edges whose types are named `Identity`, `Relation`, `Event`, `Process`, `Succession`, and `Worldview`.
- Assumptions: those six type labels are sufficient.
- Structure: static labeled graph; query returns the label on the matching node or edge.
- Claimed consequence: an `Identity` node is identity and a `Succession` edge proves succession.
- Failure condition: none except missing labels.
- MM-01 setup: alpha-renaming all six labels to `A`–`F` leaves every graph operation unchanged.
- Provenance: graph frozen before review.

