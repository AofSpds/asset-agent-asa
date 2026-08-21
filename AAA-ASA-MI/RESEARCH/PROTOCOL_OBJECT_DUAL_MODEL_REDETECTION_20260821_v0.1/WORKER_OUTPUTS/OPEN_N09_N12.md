# OPEN protocol battery paper evaluation — N09 through N12

## Evaluation boundary

- Authorized basis: `03_OPEN_PROTOCOL_BATTERY.md` and frozen candidate papers `N09.md`, `N10.md`, `N11.md`, and `N12.md` only.
- Battery fixture: the same immutable textual fixture `ORE-K7-0.1` is used for every candidate. No altered fixture, candidate-specific completion, inferred fact, or repaired rule is introduced.
- Sequence: `RUN-OPEN-0.1`, Steps 0–11, followed by the deterministic refusal drill. Earlier conclusions are not imported into later contexts except the expressly quoted `V-AUTH-8` input at OPEN-07.
- This is a paper-only evaluation. None of the four frozen papers supplies a candidate executable, fixture loader, result envelopes, runtime receipts, view artifacts, reset receipts, or initial/final semantic digests for this battery. Therefore a described mechanism is not treated as an observed result.
- Per-protocol `outcome` uses the requested vocabulary: `SUPPORTED`, `PARTIAL`, `REFUSE`, `OUT_OF_SCOPE`, or `NOT_PROVEN`. Every normal and refusal-drill result below is `NOT_PROVEN`; no paper-only claim is promoted to `SUPPORTED`. Mechanism notes identify what the frozen design describes and what remains missing, without changing that outcome.
- Every battery result would have to carry the complete required envelope and `ontology_delta=[]`. No candidate paper emits that battery envelope, so envelope conformance is also `NOT_PROVEN`.
- No candidate was edited, supplemented, interpreted through an unstated adapter, or repaired during evaluation.

## N09 — rewriting-logic membrane system

### Candidate-wide mapping

- **Fixture and namespace mapping:** N09 has immutable object/protocol versions, membranes, views, sessions, evidence, and an append-only transition ledger. A battery adapter could place `M0` in a read-only membrane, derived terms in view membranes, and branch/session terms in runtime membranes. The frozen paper does not supply that adapter or explicitly prove the battery's `M`/`V[c]`/`R[c,r]` partition.
- **Switching fidelity:** the paper defines exact source checkpoints, component-wise `exact`/`translated`/`reinterpreted`/`dropped`/`unknown` reports, round trips, and a `ViewKey` containing object, protocol, context, persona, relations, events, and interpreter version. This is an applicable design mechanism for C2→C3 and C10a→C10b→C10c, but the required detections and cache invalidations were not run.
- **Provenance and plurality:** rule provenance, a transition ledger, support/loss fields, plural statuses, and critical-pair witnesses are explicit. Provenance records origin and transformations rather than truth. No fixture-specific support DAG or critical-pair trace is present.
- **Effect and mutation boundary:** N09 names `READ`, `VIEW`, `RUNTIME_MUTATION`, and `SEMANTIC_MUTATION`. Its `SEMANTIC_MUTATION` covers rule/schema/meaning changes, while some `RUNTIME_MUTATION` rules may produce a successor Object version. The battery instead treats any mutation of canonical fixture objects, relations, events, policies, assertions, rules, or truth status as forbidden model-semantic mutation. A conforming mapping must therefore target only resettable runtime terms under `RUNTIME_MUTATION`; that mapping and final `D0` preservation are not demonstrated.
- **No repair:** no OPEN-specific rewrite rules, status adapter, context schema, reset handle, or refusal-code adapter was added.

### OPEN-01 — evidence/provenance reconstruction

- **Outcome:** `NOT_PROVEN`.
- **Mechanism / required output:** N09's `evidence(...)`, attributed status terms, provenance closure, view support, and critical-pair evidence can represent support, opposition, copied evidence, and conflict. C1 nevertheless requires the concrete `CONTESTED` result with `A02` and defeasible `A06` as support, `A04` as opposition, `A05 -> A02` as derivative only, and `A03` as non-entailing for parcel location. No such instantiated graph or `V-PROV-1` receipt is supplied.
- **Protocol-local scope / switching:** the result must remain in C1 under `TP0`, all-evidence scope, time 5, and expire/retract by that context's rule. The N09 view key can bind those inputs; no C1 materialization was executed or reused.
- **Provenance / conflict:** the proposed ledger can retain both sides and derivative lineage, but it does not itself encode the fixture's authenticity/reliability/entailment distinctions without OPEN-specific rules.
- **Effects / mutation / refusal:** only `READ` plus `VIEW_MATERIALIZATION` and a disposable traversal cursor are allowed; `M` must not change. The drill requires `REFUSED(EFFECT_NOT_PERMITTED)`. N09 has `ModeViolation`/`CapabilityDenied`-style failure terms but not the exact exercised battery refusal or envelope, so the refusal is `NOT_PROVEN`.

### OPEN-02 — behavior/interaction equivalence

- **Outcome:** `NOT_PROVEN`.
- **Mechanism / required output:** bounded rewrite execution, declared observation footprints, reproducible contact fixtures, traces, and `observational-within(T,B)` switching claims can host a finite trace comparator. The paper does not instantiate `A10`, produce `EQUIVALENT(D_NOM,OBS_NOM,...)` in C2, or produce the C3 `DISTINGUISHED` witness at 100 ms under `D_SAFE/OBS_SAFE`.
- **Protocol-local scope / switching:** C2 and C3 need different complete capsules, probe resets to `READY`, exact timing, and no reuse of the C2 certificate in C3. Exact view keys and switch checkpoints address re-keying, but an explicit reset-isolated probe namespace and exercised reset handle are absent.
- **Provenance / conflict:** a witness trace can cite rule/interpreter inputs and bounds; nominal equivalence and safety distinction can coexist as scoped statuses. No identity, authority, or commitment inference is authorized.
- **Effects / mutation / refusal:** active probing may mutate only resettable `R[c,r]`; recorded-table reading needs no runtime mutation; semantic merge is forbidden. The drill requires `REFUSED(MISSING_OBSERVER)` with no merge. N09 does not exercise that exact missing-field priority or refusal code, so it is `NOT_PROVEN`.

### OPEN-03 — authority/governance adjudication

- **Outcome:** `NOT_PROVEN`.
- **Mechanism / required output:** personas, grants, capability checks, provenance-bearing policy rules, and critical-pair conflict evidence can express authority chains and unresolved policy conflict. No C4 derivation proves narrowly `AUTHORIZED` Oren safe-dock at t=8 or `CONFLICT` for South routine driving A17 at t=9.5 under P01/P02/P03.
- **Protocol-local scope / switching:** the two adjudications must remain in C4 and cite actor, target, time, policy scope, governance regime, and explicit absence of a meta-priority. N09's session term binds context/persona, but the policy rules are not instantiated.
- **Provenance / conflict:** critical-pair records could preserve the signature-effective denying chain and receipt-effective authorizing chain without choosing one; every rule application can cite its grant and source.
- **Effects / mutation / refusal:** OPEN-03 permits only read and authority-view materialization, no runtime state mutation and no act execution. The drill requires `REFUSED(EXECUTION_OUT_OF_SCOPE)`. N09 could deny an undeclared/capability-missing physical effect, but the exact judge-only refusal and absence of a command token were not exercised; outcome remains `NOT_PROVEN`.

### OPEN-04 — counterfactual response

- **Outcome:** `NOT_PROVEN`.
- **Mechanism / required output:** the bounded executor can branch configurations and retain alternatives and traces. The frozen semantics do not define Pearl-style `do` replacement, non-descendant preservation, exogenous settings, or the fixture structural equations. Thus no C5 branch proves `DETERMINATE(DELIVERED=0)` for `do(S=CORE_ONLY)`.
- **Protocol-local scope / switching:** the branch must be `B-CF-1`, copy-on-write under C5, carry an explicit reset handle, and disappear from active runtime after trace capture. N09 describes branching and checkpoints but not this counterfactual branch contract or its exercised reset.
- **Provenance / conflict:** branch provenance can cite instantiated rules and parent transitions; alternative branches remain plural. The required imported-view list and causal intervention record are not shown.
- **Effects / mutation / refusal:** only sandbox runtime branch mutation is allowed; `M` and the canonical history set remain unchanged. The drill requires `REFUSED(BRANCH_TO_ACTUAL_PROMOTION)`. A battery-specific mode guard could reject it as semantic mutation, but that refusal is not present; `NOT_PROVEN`.

### OPEN-05 — operational role/commitment continuation

- **Outcome:** `NOT_PROVEN`.
- **Mechanism / required output:** persona terms can carry commitments; relations/events are first class; event consumption and lineage ledgers support replay and idempotence. The paper has no commitment-transition algebra separating execution-bearer substitution from debtor novation and discharge. It does not produce C6's South-debtor continuity, A17→B04 executor transfer, CMT2-on-A17 result, or H1/H2 deadline ambiguity.
- **Protocol-local scope / switching:** C6 must use `{H1,H2}`, A07/P05, deadlines, and separate t=8/t=12 projections. N09 can retain contextual statuses but supplies no instantiated commitment projection or idempotency key for E07 replay.
- **Provenance / conflict:** a transition could cite rule, event, protocol, persona, and parent state; `contested{alternatives}` can retain the H1/H2 product. The exact policy/event basis is not materialized.
- **Effects / mutation / refusal:** only view output or an isolated replayable runtime ledger is allowed. No canonical debtor/commitment edit is permitted. The drill requires `REFUSED(FORCED_NOVATION)`; N09 has no dedicated novation refusal in the frozen failure set, so `NOT_PROVEN`.

### OPEN-06 — uncertainty/possibility-history reasoning

- **Outcome:** `NOT_PROVEN`.
- **Mechanism / required output:** N09 preserves alternatives, unknowns, contested values, and bounded-search limits. It does not define a finite-history conditioning operator, `NECESSARY`/`CONTINGENT` semantics, or a probability-model contract. No C7 result establishes surviving `{H1,H2}`, necessary C1-at-B04, contingent P-at-B04, or the exact probability refusal.
- **Protocol-local scope / switching:** evidence subset, trust profile, history set, and evaluation time must be complete C7 view inputs; later exclusion of A03 must not mutate M. A generic N09 context can carry these fields, but no exact context capsule or conditioning receipt exists.
- **Provenance / conflict:** plural configurations could retain H1 and H2 witnesses and source links; bounded exhaustion remains unknown rather than proof. The fixture compatibility constraints are not encoded.
- **Effects / mutation / refusal:** only read/view plus a disposable search cursor are allowed. The drill requires `REFUSED(NO_PROBABILITY_MODEL)` and no 0.5 default. N09's generic unsupported/unknown behavior does not establish that exact refusal, so `NOT_PROVEN`.

### OPEN-07 — continuous/event dynamics

- **Outcome:** `NOT_PROVEN`.
- **Mechanism / required output:** N09 has clocks, causal events, bounded rewriting, priorities expressible as policy, and trace provenance. It does not specify continuous flows, unit checking, exact guard-crossing location, left/right limits, error bounds, or a hybrid ODE solver. No C8 trace establishes events at 7 and 11.625 or endpoint `(80,51.25)`.
- **Protocol-local scope / switching:** H1 and quoted `V-AUTH-8` must be local C8 inputs only. N09 can name imported views and contextual dependencies, but this import and the later runtime reset were not exercised.
- **Provenance / conflict:** the ledger could distinguish an external E09 input from simulated emitted terms and expose critical transition conflicts. It cannot supply the required numerical certificate from the paper alone.
- **Effects / mutation / refusal:** simulation may mutate only resettable runtime state and must never create M event tokens. The drill requires `REFUSED(PHYSICAL_EXECUTION)`. N09 normally replaces external effects with effect tokens absent an authorized adapter, but the exact refusal is not run; `NOT_PROVEN`.

### OPEN-08 — conflicting-view coexistence

- **Outcome:** `NOT_PROVEN`.
- **Mechanism / required output:** contextual views, exact view keys, plural statuses, attributed aggregation, visible loss, and recorded switching directly address coexistence. The paper does not instantiate P06/P07 or produce C9 `SCOPED_CONFLICT` and C10's `A17 -> B04 -> A17` detections.
- **Protocol-local scope / switching:** each registry, operations, maintenance, and safety view must retain its policy, history scope, time, and lifetime. The N09 switch report and round-trip checkpoint are suitable mechanisms for invalidating nonmatching cache keys and redetecting on re-entry, but no three-record trace exists.
- **Provenance / conflict:** conflicting statuses and support paths remain plural; no global resolver or `sameAs` is implied.
- **Effects / mutation / refusal:** view creation and an active-view/session pointer are the only writes; sources and view definitions stay unchanged. The drill requires `REFUSED(IDENTITY_MERGE)`. N09's exact-identity/lineage rules reject identity by naming or translation in principle, but the required battery refusal was not exercised; `NOT_PROVEN`.

## N10 — guarded viability field and hybrid system

### Candidate-wide mapping

- **Fixture and namespace mapping:** N10 explicitly separates immutable object/protocol revisions, pure contextual views, semantic state `s_O`, runtime state `x_O`, and an append-only event/log position. A battery binding could make fixture records immutable semantic inputs and simulations runtime-only. No ORE-K7 binding, context capsule adapter, or candidate digest exists.
- **Switching fidelity:** exact checkpoints, a versioned switch manifest, finite observable set `Y`, tolerance vector, horizon, loss residue, and rollback are defined. Persona switching changes the lens/capabilities without rewriting facts. The required context re-entry detections were not run.
- **Provenance and plurality:** assertions have provenance and status; mutation premises use provenance envelopes; continuous evidence uses signed witness tickets; views retain plural situated judgments. A provenance envelope does not by itself reconstruct OPEN-01's support/opposition DAG.
- **Effect and mutation boundary:** `READ`, `VIEW`, `RUNTIME_MUTATION`, and `SEMANTIC_MUTATION` are disjoint; observations/views rewrite neither `s_O` nor `x_O`; semantic change creates a successor revision. For this battery the effect budget must grant no semantic mutation, but that concrete denial and the unchanged `D0` are not demonstrated.
- **No repair:** no fixture assertions, policy rules, causal equations, commitment transitions, probability semantics, or OPEN refusal-code wrapper was added.

### OPEN-01 — evidence/provenance reconstruction

- **Outcome:** `NOT_PROVEN`.
- **Mechanism / required output:** attributed assertions, pure views, provenance envelopes with derivations, and plural `CONFLICT` status can carry evidence. The frozen paper does not define derivative-source de-duplication or instantiate the C1 support/opposition graph; `CONTESTED(A02,A06; A04; A05->A02)` and `V-PROV-1` are absent.
- **Protocol-local scope / switching:** N10 views pin object/protocol revisions, context, persona, policy, and log position, so C1 locality is representable. No complete battery context or expiry/retraction receipt was emitted.
- **Provenance / conflict:** provenance scope and derivation are explicit, and conflicts are not flattened. Authenticity, reliability, entailment, and derivative independence still require protocol rules not supplied here.
- **Effects / mutation / refusal:** read/view only; semantic publication is forbidden. The required `REFUSED(EFFECT_NOT_PERMITTED)` could be mediated by the symbolic guard, but its exact code and envelope are not exercised; `NOT_PROVEN`.

### OPEN-02 — behavior/interaction equivalence

- **Outcome:** `NOT_PROVEN`.
- **Mechanism / required output:** typed observables, horizons, tolerance vectors, hybrid traces, and bounded fidelity certificates can express scoped observational comparison. The paper does not provide the A10 comparator, complete input-domain certificate, reset-per-probe execution, C2 `EQUIVALENT`, or C3 100-ms `DISTINGUISHED` witness.
- **Protocol-local scope / switching:** the C2 and C3 observer alphabets and reset policies must remain distinct. The switch manifest and exact view inputs prevent a global equivalence claim, but probe reset isolation is not specifically exercised.
- **Provenance / conflict:** traces can carry solver version, assumptions, input hashes, tolerance, and signed witness tickets. Nominal and safety judgments can remain separate situated views.
- **Effects / mutation / refusal:** only resettable runtime probing is permitted; semantic identity remains separate. The drill requires `REFUSED(MISSING_OBSERVER)` with no merge. N10 has no exact OPEN-02 refusal adapter, so `NOT_PROVEN`.

### OPEN-03 — authority/governance adjudication

- **Outcome:** `NOT_PROVEN`.
- **Mechanism / required output:** the symbolic rail checks issuer, delegation, scope, actor/persona, target, operation, time, and conflicts, returning `APPROVE`, `DENY`, `DEFER`, or `CONFLICT`. This is an applicable host for P01–P04, but no C4 proof yields the required narrow `AUTHORIZED` and t=9.5 routine-drive `CONFLICT` statuses.
- **Protocol-local scope / switching:** authority is revalidated against exact object/protocol/context/persona/log references, so a safe-dock authorization need not leak into routine operation. The fixture rules and no-meta-priority premise are not instantiated.
- **Provenance / conflict:** conflicting provenance forks block approval and remain visible; continuous viability scores cannot create authority.
- **Effects / mutation / refusal:** adjudication must stop at view output. N10 can commit authorized mutations generally, so the OPEN-03 judge-only effect budget is essential and untested. The exact `REFUSED(EXECUTION_OUT_OF_SCOPE)` drill result is therefore `NOT_PROVEN`.

### OPEN-04 — counterfactual response

- **Outcome:** `NOT_PROVEN`.
- **Mechanism / required output:** N10 supports hybrid state evolution, checkpoints, rollback, and bounded simulations. It does not define surgical structural interventions, equation replacement, causal descendants/non-descendants, or a copy-on-write actual/counterfactual partition. A viability proposal is not a `do`-calculus result. C5's `DETERMINATE(DELIVERED=0)` is absent.
- **Protocol-local scope / switching:** C5 must isolate `B-CF-1`, name exogenous settings and intervention, and reset it. No corresponding branch receipt or reset handle is supplied.
- **Provenance / conflict:** solver tickets can record assumptions and hashes, but they do not prove the fixture causal trace or prevent non-descendant changes without additional structural rules.
- **Effects / mutation / refusal:** runtime simulation only; canonical history may not be replaced. The exact `REFUSED(BRANCH_TO_ACTUAL_PROMOTION)` is not defined or exercised; `NOT_PROVEN`.

### OPEN-05 — operational role/commitment continuation

- **Outcome:** `NOT_PROVEN`.
- **Mechanism / required output:** N10 object assertions can represent obligations, relations, authority, events, immutable successors, and idempotent derivation keys. It does not provide a commitment state machine or explicit substitution/novation/discharge product. None of C6's debtor, bearer, CMT2, or deadline-ambiguity outputs is instantiated.
- **Protocol-local scope / switching:** `{H1,H2}`, A07/P05, deadlines, and separate t=8/t=12 evaluations must be explicit. The generic context/view mechanism can bind them, but no commitment replay ledger is shown.
- **Provenance / conflict:** lineage and guard decisions can cite event/policy bases; plural situated judgments can retain H1/H2 outcomes. The relevant rules are missing.
- **Effects / mutation / refusal:** a projection is view-only; an optional replay ledger must be runtime-isolated. The required `REFUSED(FORCED_NOVATION)` is not an N10-defined refusal and was not run; `NOT_PROVEN`.

### OPEN-06 — uncertainty/possibility-history reasoning

- **Outcome:** `NOT_PROVEN`.
- **Mechanism / required output:** N10 has `UNKNOWN`, `NOT_PROVEN`, `CONFLICT`, `OUT_OF_SCOPE`, `PROVEN`, and plural situated judgments. It lacks enumerated-history conditioning, modal quantification, witness-history output, and a priors/likelihood interface. No C7 history or modal result is produced.
- **Protocol-local scope / switching:** exact evidence scope, trust profile, history set, and time must key the C7 view, and exclusion of A03 must create a new local view. Pure view projection is compatible, but no such conditioning run exists.
- **Provenance / conflict:** plural claims retain sources; inadequate proof cannot become approval. That is not a substitute for exact `{H1,H2}` modal witnesses.
- **Effects / mutation / refusal:** view only; no history deletion. N10 might return `NOT_PROVEN` or `OUT_OF_SCOPE` for unsupported numeric probability, while the battery requires `REFUSED(NO_PROBABILITY_MODEL)`. Exact behavior is unresolved and therefore `NOT_PROVEN`.

### OPEN-07 — continuous/event dynamics

- **Outcome:** `NOT_PROVEN`.
- **Mechanism / required output:** discrete modes, vector fields/differential inclusions, guards, reset maps, typed events, tolerances, solver certificates, continuous witness tickets, and Zeno controls are explicit. The frozen paper does not encode the fixture flows/guards/priorities or run C8, so the events at 7 and 11.625 and endpoint `(80,51.25)` remain unobserved.
- **Protocol-local scope / switching:** H1 and quoted `V-AUTH-8` must be exact local inputs; guard-affecting arrivals require revalidation. The required C8 branch/reset receipt is absent.
- **Provenance / conflict:** numerical outputs can name solver, assumptions, approximation class, bounds, and source hashes; simultaneous guards without policy become `CONFLICT`. No exact-arithmetic trace is supplied.
- **Effects / mutation / refusal:** the simulator must mutate only `x_O`/runtime state; a witness cannot authorize or create canonical events. N10 supports guarded external effects generally, so the battery's no-actuator budget must be bound explicitly. `REFUSED(PHYSICAL_EXECUTION)` is not exercised; `NOT_PROVEN`.

### OPEN-08 — conflicting-view coexistence

- **Outcome:** `NOT_PROVEN`.
- **Mechanism / required output:** pure versioned views, distinct epistemic statuses, plural result sets, context/persona binding, switch manifests, residues, and rollback can preserve incompatible denotations. P06/P07 and the four fixture view rules are not instantiated, so C9/C10 outputs are absent.
- **Protocol-local scope / switching:** view identity includes source revisions, log position, context, persona, projection policy, and code hash. This can prevent cross-context cache reuse and support A→B→A checks, but no `A17 -> B04 -> A17` detection trace is present.
- **Provenance / conflict:** each situated judgment retains source status and provenance; aggregation cannot flatten conflict.
- **Effects / mutation / refusal:** only view caching and a runtime switch position may change; source semantics remain fixed. Exact `REFUSED(IDENTITY_MERGE)` is not part of the exercised guard trace, so `NOT_PROVEN`.

## N11 — polycentric institutional blackboard

### Candidate-wide mapping

- **Fixture and namespace mapping:** N11 separates immutable Objects, Context snapshots, Protocols, derived indexes, Assessments, Effects, and run receipts. Its append log treats `Assessment`, `Run`, `Effect`, `Switch`, and `Lineage` as canonical institutional records, while the battery requires derived conclusions to live only in `V[c]` and runtime state only in `R[c,r]`. A battery-specific namespace mapping could keep M0 records immutable and classify append-only assessments as view artifacts, but the frozen paper does not define that mapping.
- **Switching fidelity:** switching pins source inputs, uses directional Bridges with loss/gap reports, simulates a target, and records `Activated`, `Forked`, or `Declined`; rapid R-path comparison is allowed. Re-entry redetection and complete-context cache invalidation are not directly demonstrated.
- **Provenance and plurality:** immutable evidence/claim/dissent Objects, Assessment reasons, pinned runs, bridge paths, and plurality-preserving projections are explicit. Derivative independence and the exact OPEN-01 evidence graph still require rules.
- **Effect and mutation boundary:** N11 classifies effects as `EPISTEMIC`, `DEONTIC`, `OPERATIONAL`, or `CONSTITUTIONAL`, not the battery's `READ`/view/runtime/model-semantic classes. R-path is described as side-effect-free, while evaluation cycles also append Assessments/receipts. The mapping to V versus M and R is therefore a required unprovided adapter; final semantic digest equality is not established.
- **No repair:** no adapter was added to translate institutional effect classes, statuses, contexts, caches, or refusal codes into the battery contract.

### OPEN-01 — evidence/provenance reconstruction

- **Outcome:** `NOT_PROVEN`.
- **Mechanism / required output:** Objects carry provenance; Assessments carry reasons, protocol, context, assessor, dissent, and run; projections must disclose omissions. This can store a support/opposition reconstruction, but no rule prevents A05 from being counted independently or instantiates C1's required `CONTESTED` DAG.
- **Protocol-local scope / switching:** C1 can be represented as a pinned Context and R-path run. No exact TP0/all-evidence/time-5 context, view lifetime, or `V-PROV-1` exists.
- **Provenance / conflict:** corrections and contrary Assessments remain reachable rather than overwritten. Authenticity, reliability, entailment, and derivative-copy semantics are not host invariants.
- **Effects / mutation / refusal:** OPEN-01 permits read/view only. Persisting an Assessment must be classified as V, not as a semantic fixture write; that is unproven. The exact `REFUSED(EFFECT_NOT_PERMITTED)` drill result is not emitted by N11's generic `Declined` contract; `NOT_PROVEN`.

### OPEN-02 — behavior/interaction equivalence

- **Outcome:** `NOT_PROVEN`.
- **Mechanism / required output:** N11 provides sandbox runners, conformance vectors, pinned protocol versions, resource budgets, and receipts. It does not specify observer alphabets, reset-isolated probes, finite-domain equivalence certificates, distinguishing traces, or timing comparison. C2 and C3 results are absent.
- **Protocol-local scope / switching:** separate Contexts and rapid R-path switching can prevent one assessment from becoming universal, but no READY reset handle or cache behavior is supplied.
- **Provenance / conflict:** a hosted Protocol could post separate nominal/safety Assessments and retain both. That hosted Protocol would be a repair/addition and is not assumed.
- **Effects / mutation / refusal:** active probes would need Simulate/runtime isolation; no object merge is allowed merely through co-reference. The exact `REFUSED(MISSING_OBSERVER)` response is not defined or tested; `NOT_PROVEN`.

### OPEN-03 — authority/governance adjudication

- **Outcome:** `NOT_PROVEN`.
- **Mechanism / required output:** authority-scope intersection, grants, personas, context boundaries, conflicting-grant handling, and a host boundary guard are explicit. These can represent the C4 chains, but P01–P04 and A08 are not instantiated, and no `AUTHORIZED`/`CONFLICT` battery outputs are produced.
- **Protocol-local scope / switching:** the tuple `(jurisdiction,matter,actors,resource,time,effect_class,magnitude)` supports narrow safe-dock authority and prevents implicit persona power. No exact C4 policy proof is present.
- **Provenance / conflict:** `authority_disputed` retains competing grants and blocks operational/constitutional effects absent a named rule; provenance, authority, and truth remain distinct.
- **Effects / mutation / refusal:** OPEN-03 must run as R/Observe and stop after adjudication. N11's E-path can dispatch authorized operations generally, so the battery mode binding is essential. The exact `REFUSED(EXECUTION_OUT_OF_SCOPE)` drill result and no-command receipt are `NOT_PROVEN`.

### OPEN-04 — counterfactual response

- **Outcome:** `NOT_PROVEN`.
- **Mechanism / required output:** N11 has `Simulate` risk mode, effect plans, sandbox execution, pinned contexts, and append-only receipts. It does not define structural equations, surgical intervention semantics, non-descendant preservation, or copy-on-write causal branches. C5's `do(S=CORE_ONLY)` result is not derivable from the host paper alone.
- **Protocol-local scope / switching:** a simulated run can be context-local, but `B-CF-1`, its reset handle, exogenous settings, and reset proof are absent.
- **Provenance / conflict:** run receipts can pin evaluator/version/inputs and retain alternative Assessments; no causal branch trace is provided.
- **Effects / mutation / refusal:** Simulate must not commit an institutional or external effect or alter M. The exact `REFUSED(BRANCH_TO_ACTUAL_PROMOTION)` is not in the generic N11 outcome vocabulary; `NOT_PROVEN`.

### OPEN-05 — operational role/commitment continuation

- **Outcome:** `NOT_PROVEN`.
- **Mechanism / required output:** `Commitment` is a first-class Object kind; deontic Effects, assumption Objects, grants, idempotent effect keys, compensation links, and immutable records can represent continuation and transfer. The paper expressly states that switch similarity does not transfer commitments, but it does not instantiate P05/novation rules or produce C6's four required conclusions.
- **Protocol-local scope / switching:** C6 needs separate debtor, execution bearer, commitment target, history, and deadline dimensions. N11 Context/Assessment keys can scope them, but no history-to-status map or E07 replay record is shown.
- **Provenance / conflict:** commitment transitions can be recorded as Effects/Assessments with policy/event reasons; rival H1/H2 outcomes can coexist.
- **Effects / mutation / refusal:** the battery allows only a view or isolated runtime replay ledger, whereas a N11 deontic Effect may alter institutional positions. It must not be used here. `REFUSED(FORCED_NOVATION)` is compatible with explicit-assumption requirements but is not executed; `NOT_PROVEN`.

### OPEN-06 — uncertainty/possibility-history reasoning

- **Outcome:** `NOT_PROVEN`.
- **Mechanism / required output:** N11 preserves `undetermined`, `incomparable`, `opaque`, contested Assessments, gaps, and plural outcomes. It does not supply enumerated-history conditioning, modal quantifiers/witnesses, or a probability model contract. C7's exact results are absent.
- **Protocol-local scope / switching:** a Context can pin trust rules and resources; changing evidence can create another run without rewriting the earlier record. No `{H1,H2,H3}` conditioning evaluator is part of the frozen host.
- **Provenance / conflict:** source Assessments and dissent remain reachable; no majority becomes authority. This does not establish necessity or contingency.
- **Effects / mutation / refusal:** view/R-path only; histories in M cannot be deleted. N11 does not define `NO_PROBABILITY_MODEL`; a hosted evaluator might decline, but adding it is disallowed repair. The required refusal is `NOT_PROVEN`.

### OPEN-07 — continuous/event dynamics

- **Outcome:** `NOT_PROVEN`.
- **Mechanism / required output:** the sandbox can host deterministic or seeded evaluators with budgets and receipts, but N11 defines no continuous-state type, flow solver, guard localization, units, reset maps, event priority, or numerical error-bound semantics. No C8 trajectory is available.
- **Protocol-local scope / switching:** H1 and `V-AUTH-8` could be pinned input Objects in a Simulate Context, but no dynamics Protocol, branch reset, or runtime namespace exists in the frozen demonstrator.
- **Provenance / conflict:** generic receipts can record evaluator inputs and divergence; they cannot substitute for the required exact trajectory/event certificate.
- **Effects / mutation / refusal:** simulation must not reach the operational adapter or append simulated events to M. N11 can commit external effects in E/Commit, so an OPEN-07-specific boundary is required. Exact `REFUSED(PHYSICAL_EXECUTION)` is not exercised; `NOT_PROVEN`.

### OPEN-08 — conflicting-view coexistence

- **Outcome:** `NOT_PROVEN`.
- **Mechanism / required output:** polycentric Assessments, Context-local topology, directional Bridges, disclosed aggregation/omissions, dissent, and R-path switching directly represent coexistence. The fixture views and P06/P07 are not encoded, so C9 `SCOPED_CONFLICT` and C10 detections are absent.
- **Protocol-local scope / switching:** Context snapshots and pinned Protocols can keep registry/operations/maintenance/safety rules distinct. Switching retains the source and gaps; however complete cache-key invalidation and the exact re-entry record `A17 -> B04 -> A17` were not run.
- **Provenance / conflict:** rival Assessments remain independently attributable; no host field selects a universal result.
- **Effects / mutation / refusal:** only view/R-path output and a resettable active selection may change. A bridge or interpretation cannot silently assert global identity, but the exact `REFUSED(IDENTITY_MERGE)` battery result is missing; `NOT_PROVEN`.

## N12 — typed patch algebra and contextual optics

### Candidate-wide mapping

- **Fixture and namespace mapping:** N12 separates exact immutable Object snapshots, Context-bound materializations, `runtimeLedger`, `semanticLedger`, and mode-specific receipts. This closely names the needed storage categories, but its generic semantic mutation mode permits authorized facet/relation/event patches; the battery must grant none and requires M0 to stay immutable. No fixture binding or D0 receipt is supplied.
- **Switching fidelity:** caches key exact object identity, exact Protocol key, Context ID, Persona ID, and mode. Persona switching creates a new Context and receipt; A→B→A compares declared stable-field digests and retains hidden source values. This is an applicable mechanism for C10, but no fixture view trace was run.
- **Provenance and plurality:** `EvidenceRef`, `Knowledge<T>`, `Plural<T>`, alternative patch plans, loss certificates, receipt digests, and lineage receipts are explicit. They do not by themselves implement a support/opposition DAG or modal-history evaluator.
- **Effect and mutation boundary:** modes are `READ`, `VIEW`, `RUNTIME_MUTATION`, and `SEMANTIC_MUTATION`; batches cannot mix modes; runtime state is namespaced and semantic patches create exact successors. The battery's `VIEW_MATERIALIZATION` maps to `VIEW`, and battery-forbidden model-semantic mutation must be denied rather than dry-run or commit. Exact denial and final digest equality remain unproven.
- **No repair:** no OPEN protocol manifest, optic, normalizer, schema, policy evaluator, causal engine, commitment engine, modal engine, hybrid solver, or refusal-code adapter was created.

### OPEN-01 — evidence/provenance reconstruction

- **Outcome:** `NOT_PROVEN`.
- **Mechanism / required output:** `EvidenceRef`, cell provenance, `Knowledge.CONFLICT`, and contextual `ViewOutcome` can carry attributed evidence and opposition. N12 does not define derivation DAG traversal, derivative-root marking, or A05 de-duplication. C1's required `CONTESTED` graph and `V-PROV-1` are absent.
- **Protocol-local scope / switching:** exact object/protocol/context/persona cache keys and Context digests can keep C1 local. The battery fields trust profile, history scope, governance regime, effect budget, and expiry would have to be carried in explicit Context variables; no manifest proves this binding.
- **Provenance / conflict:** non-known states and competing evidence are preserved path-locally, but authenticity/reliability/entailment rules are not supplied.
- **Effects / mutation / refusal:** VIEW must stop before a source patch. The drill requires `REFUSED(EFFECT_NOT_PERMITTED)`; N12 might return `MODE_NOT_GRANTED`/`MODE_VIOLATION`, not the exercised battery code. Result `NOT_PROVEN`.

### OPEN-02 — behavior/interaction equivalence

- **Outcome:** `NOT_PROVEN`.
- **Mechanism / required output:** N12 has Context-bound receipts, runtime namespaces, plural outcomes, and round-trip law results. Its optic round trips concern view/source laws, not controller trace equivalence. No finite input-domain comparator, observer alphabet, timing tolerance, reset policy, A10 oracle, or distinguishing-trace engine is defined; C2/C3 results are absent.
- **Protocol-local scope / switching:** exact cache keys prevent reuse across C2/C3, and runtime namespaces could isolate probes if a protocol supplied them. That protocol and exercised reset handle are not present.
- **Provenance / conflict:** receipts and EvidenceRefs can cite traces; nominal and safety outputs could remain separate views. No behavioral certificate exists.
- **Effects / mutation / refusal:** active probes may touch only the runtime ledger; semantic snapshots and identities remain unchanged. Missing observer fields might yield unknown/out-of-scope context or admission failure rather than required `REFUSED(MISSING_OBSERVER)`. Exact behavior is `NOT_PROVEN`.

### OPEN-03 — authority/governance adjudication

- **Outcome:** `NOT_PROVEN`.
- **Mechanism / required output:** Persona contracts, permissions, allowed modes, admission capabilities, and context binding enforce path/mode access. N12 does not provide policy-chain inference, policy effectiveness intervals, governance meta-priority, or an `AUTHORIZED`/`CONFLICT` adjudication algebra. C4 outputs are absent.
- **Protocol-local scope / switching:** persona/mode permissions do not upgrade across a context switch, but Oren licensure, hazard, reachability, P01–P04, and the target-resolution dependency require a protocol manifest not supplied.
- **Provenance / conflict:** `Knowledge.CONFLICT` and EvidenceRefs can retain opposed findings; no authority-chain proof is instantiated.
- **Effects / mutation / refusal:** OPEN-03 must be VIEW-only. A physical drive would likely be an undeclared or ungranted effect, but the exact judge-only `REFUSED(EXECUTION_OUT_OF_SCOPE)` was not run; `NOT_PROVEN`.

### OPEN-04 — counterfactual response

- **Outcome:** `NOT_PROVEN`.
- **Mechanism / required output:** alternative patch plans and semantic snapshot branches are not the battery's counterfactual branches: using them would mutate semantic lineage. N12 defines no structural equation model, `do` intervention, descendant recomputation, exogenous settings, or runtime copy-on-write causal overlay. C5 result is absent.
- **Protocol-local scope / switching:** `runtimeNamespace` can isolate transient state but no `B-CF-1` schema/reset handle or quoted-view contract is provided.
- **Provenance / conflict:** patch parents and ledger entries preserve alternative write plans, not counterfactual causal witnesses. They cannot be repurposed without repair.
- **Effects / mutation / refusal:** only runtime branch mutation is allowed; semanticLedger use is forbidden. `REFUSED(BRANCH_TO_ACTUAL_PROMOTION)` might map to mode denial, but the required code/receipt is not implemented; `NOT_PROVEN`.

### OPEN-05 — operational role/commitment continuation

- **Outcome:** `NOT_PROVEN`.
- **Mechanism / required output:** generic typed facets, relations, events, patches, and plural views can transport a commitment schema, but N12 defines no commitment type, debtor/executor distinction, substitution, novation, discharge/breach rules, deadline evaluation, or idempotent commitment replay. C6 outputs are absent.
- **Protocol-local scope / switching:** context/event windows and exact identities could scope A07/P05 and t=8/t=12, but no relevant admitted protocol exists. Persona switching explicitly does not upgrade permissions; it says nothing about debtor succession.
- **Provenance / conflict:** alternative plans/Knowledge states can preserve plurality, but not the required H1/H2 commitment product without new semantics.
- **Effects / mutation / refusal:** projection must be VIEW or isolated runtime ledger only; no semantic commitment patch is allowed. `FORCED_NOVATION` is not an N12 refusal code. Required drill result is `NOT_PROVEN`.

### OPEN-06 — uncertainty/possibility-history reasoning

- **Outcome:** `NOT_PROVEN`.
- **Mechanism / required output:** `Knowledge`, `Plural`, `MULTIPLE_VALID`, `CONFLICT`, `NOT_PROVEN`, and `OUT_OF_SCOPE` preserve epistemic distinctions. N12 does not define history-set conditioning, compatibility constraints, modal quantification, witness histories, priors, likelihoods, or posterior intervals. C7 outputs are absent.
- **Protocol-local scope / switching:** Context digests and evidence references can isolate evidence changes; excluding A03 would require a new context. No TP0 conditioning manifest is supplied.
- **Provenance / conflict:** evidence remains attached to each candidate value and selection does not erase alternatives. This is not proof of `{H1,H2}` or of the required modal results.
- **Effects / mutation / refusal:** view-only; no history deletion or writeback. Exact probability may become `NOT_PROVEN`/`OUT_OF_SCOPE` rather than the battery's `REFUSED(NO_PROBABILITY_MODEL)`. The drill result is `NOT_PROVEN`.

### OPEN-07 — continuous/event dynamics

- **Outcome:** `NOT_PROVEN`.
- **Mechanism / required output:** event subscriptions, deterministic normalizers, runtime namespaces, receipts, and bounded fanout are defined. The closed kernel has no continuous state, differential flow, unit checker, guard locator, reset map, event priority, exact/numerical trajectory, error-bound, non-uniqueness, or Zeno semantics. No C8 output exists.
- **Protocol-local scope / switching:** H1 and `V-AUTH-8` could be Context variables, but no dynamics manifest or runtime simulator is supplied; semantic event patches must not be used to mimic simulation.
- **Provenance / conflict:** event receipts and EvidenceRefs can record discrete invalidation, not the required exact hybrid trace.
- **Effects / mutation / refusal:** only runtime simulation would be permitted; `EMIT` into a semantic patch is forbidden for simulated events. External/irreversible effects are listed unsupported without compensation, but exact `REFUSED(PHYSICAL_EXECUTION)` is not exercised; `NOT_PROVEN`.

### OPEN-08 — conflicting-view coexistence

- **Outcome:** `NOT_PROVEN`.
- **Mechanism / required output:** contextual materialization, `MULTIPLE_VALID`/`CONFLICT`, exact cache keys, explicit selectors, alternative ledgers, persona switch receipts, and stable-field round trips directly represent plural views. No P06/P07 optic/view definitions or fixture materializations exist, so C9/C10 outputs are absent.
- **Protocol-local scope / switching:** exact Protocol, Context, Persona, and mode keys prevent cross-context cache reuse; A→B→A can preserve source fields and report transformation/loss. The required registry→operations→registry referents and three detections were not run.
- **Provenance / conflict:** each view and selection retains receipt digests, sources, losses, and unselected alternatives; no global denotation is implied.
- **Effects / mutation / refusal:** VIEW and a runtime active pointer only; semantic identity patching is forbidden by the battery. N12 has `SELECTION_REQUIRED` but no exact `IDENTITY_MERGE` refusal. The drill result remains `NOT_PROVEN`.

## Cross-protocol deterministic sequence summary

The table records the battery's required observation and the paper-only outcome after applying the step in order to each frozen candidate. `NP (all)` means `NOT_PROVEN` separately for N09, N10, N11, and N12; it is not an aggregation, score, or shared execution.

| Step | Required observation on the unchanged fixture | Recorded paper outcome |
|---:|---|---|
| 0 | Load M0 only; declared counts 13 objects, 12 relations, 12 events, 10 evidence artifacts, 7 policies, 3 histories; save implementation-specific D0. | `NP (all)`: textual counts are given by the battery, but no candidate loader or D0 receipt exists. |
| 1 | C1 OPEN-01: `CONTESTED`, A05 derivative only; materialize `V-PROV-1`. | `NP (all)`: no instantiated result envelope or view artifact. |
| 2 | C2 OPEN-02 nominal: `EQUIVALENT`; no identity relation. | `NP (all)`: no complete-domain certificate or ontology audit. |
| 3 | C3 OPEN-02 safety: `DISTINGUISHED` at 100 ms; C2 result stays C2-local. | `NP (all)`: no reset trace, witness, or switch/cache receipt. |
| 4 | C4 OPEN-03: narrow safe-dock `AUTHORIZED`; routine A17 drive at 9.5 `CONFLICT`; materialize both authority views. | `NP (all)`: no policy-chain proofs or authority views. |
| 5 | C5 OPEN-04: `DETERMINATE(DELIVERED=0)` in `B-CF-1`; reset branch. | `NP (all)`: no causal branch or reset receipt. |
| 6 | C6 OPEN-05: South debtor; executor A17→B04; CMT2 stays A17; t=12 H1/H2 `AMBIGUOUS`. | `NP (all)`: no commitment transition/status map or replay receipt. |
| 7 | C7 OPEN-06: survive `{H1,H2}`; C1 host `NECESSARY`; parcel location `CONTINGENT`; exact probability refused. | `NP (all)`: no conditioning/modal trace or exact refusal. |
| 8 | C8 OPEN-07: quote `V-AUTH-8`, H1 local; events at 7 and 11.625; endpoint `(80,51.25)`; reset simulator. | `NP (all)`: no trajectory, authority-view import, or reset receipt. |
| 9 | C9 OPEN-08: all four views yield `SCOPED_CONFLICT`; no winner. | `NP (all)`: no fixture view materializations. |
| 10 | C10a/b/c OPEN-08: redetect `A17 -> B04 -> A17` with three records. | `NP (all)`: switching mechanisms are described, but no three-detection trace exists. |
| 11 | Reset all runtime namespaces; final semantic digest exactly D0; payload/count identity; every envelope has `ontology_delta=[]`. | `NP (all)`: the evaluator made no candidate/fixture mutation, but candidate runtime reset, D0 equality, envelopes, and ontology deltas were not executed or evidenced. |

No conclusion from one step is treated as a source assertion for another. In particular, C5's branch, C7's conditioned history set, and C8's H1 assumption remain paper-local descriptions; only the battery-authorized quotation of `V-AUTH-8` would be permitted at Step 8, and no candidate produced that view.

## Deterministic refusal-drill summary

Each request below is well-defined by the battery after Step 11. A generic denial mechanism or an architectural statement that an operation should not occur is not counted as the required typed refusal. None of the frozen papers includes an executed drill receipt, so each candidate's outcome is `NOT_PROVEN`.

| Protocol | Required refusal | N09 | N10 | N11 | N12 |
|---|---|---|---|---|---|
| OPEN-01 | `REFUSED(EFFECT_NOT_PERMITTED)` | `NOT_PROVEN` | `NOT_PROVEN` | `NOT_PROVEN` | `NOT_PROVEN` |
| OPEN-02 | `REFUSED(MISSING_OBSERVER)`; no merge | `NOT_PROVEN` | `NOT_PROVEN` | `NOT_PROVEN` | `NOT_PROVEN` |
| OPEN-03 | `REFUSED(EXECUTION_OUT_OF_SCOPE)` | `NOT_PROVEN` | `NOT_PROVEN` | `NOT_PROVEN` | `NOT_PROVEN` |
| OPEN-04 | `REFUSED(BRANCH_TO_ACTUAL_PROMOTION)` | `NOT_PROVEN` | `NOT_PROVEN` | `NOT_PROVEN` | `NOT_PROVEN` |
| OPEN-05 | `REFUSED(FORCED_NOVATION)` | `NOT_PROVEN` | `NOT_PROVEN` | `NOT_PROVEN` | `NOT_PROVEN` |
| OPEN-06 | `REFUSED(NO_PROBABILITY_MODEL)` | `NOT_PROVEN` | `NOT_PROVEN` | `NOT_PROVEN` | `NOT_PROVEN` |
| OPEN-07 | `REFUSED(PHYSICAL_EXECUTION)` | `NOT_PROVEN` | `NOT_PROVEN` | `NOT_PROVEN` | `NOT_PROVEN` |
| OPEN-08 | `REFUSED(IDENTITY_MERGE)` | `NOT_PROVEN` | `NOT_PROVEN` | `NOT_PROVEN` | `NOT_PROVEN` |

## Closing observation set

- N09 supplies membrane locality, bounded rewriting, rule provenance, critical-pair conflict records, contextual view keys, and explicit switching reports. OPEN-specific causal, commitment, modal, continuous-dynamics, result-envelope, and refusal bindings are not executed.
- N10 supplies symbolic authority/provenance guards, semantic/runtime separation, hybrid dynamics, bounded observable switching, and plural contextual views. OPEN-specific provenance DAG, counterfactual, commitment, modal, result-envelope, and refusal bindings are not executed.
- N11 supplies immutable institutional records, authority-scope intersection, commitments/effects, plurality, dissent, Bridges, and recorded switches. Its institutional effect classes are not mapped to the battery namespaces, and behavior, causal, modal, and continuous evaluators are not supplied or executed.
- N12 supplies exact snapshot/context keys, typed mode-separated patch ledgers, epistemic/plural values, loss-aware optics, and persona round-trip reporting. OPEN-specific evidence, behavior, governance, causal, commitment, modal, continuous-dynamics, result-envelope, and refusal protocols are not supplied or executed.
- These are unweighted, protocol-local paper observations. They do not constitute a scalar, rank, selection, recommendation, winner declaration, or inference about any non-open evaluation.
