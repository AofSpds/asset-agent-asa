# OPEN battery evaluation — N01 through N04

## Evaluation basis and outcome discipline

- Battery: AAA/ASA/MI Open Development Protocol Battery v0.1.
- Fixture: ORE-K7-0.1, used unchanged for every candidate.
- Required sequence: RUN-OPEN-0.1, Steps 0–11, followed by the deterministic refusal drill.
- Candidate inputs: the exact frozen texts N01.md, N02.md, N03.md, and N04.md only.
- The SHA-256 values below are hashes of those exact candidate files. They are not the fixture semantic digest D0.
- All four files declare FROZEN_PROPOSAL/NON_NORMATIVE/NOT_VALIDATED. None contains an implementation, an ORE-K7-0.1 adapter, an execution trace, result envelopes from RUN-OPEN-0.1, reset receipts, or a computed D0. Consequently, paper mechanisms are not reported as observed runtime conformance.
- Outcome meanings used here:
  - SUPPORTED: the required behavior was actually demonstrated by authorized implementation evidence.
  - PARTIAL: the paper supplies some relevant mechanism, but omits a battery-specific evaluator, rule, envelope field, or exact behavior needed to discharge the protocol.
  - REFUSE: the candidate rejects the normal well-formed protocol invocation. No normal invocation below is classified this way.
  - OUT_OF_SCOPE: the frozen proposal lacks or expressly conditions support on an absent adapter/semantic primitive.
  - NOT_PROVEN: the paper describes an apparently adequate architectural path, but no implementation/run proves the required observation.
- Required battery outputs are shown as the target observation, not as candidate-produced output. Every candidate runtime claim remains NOT_PROVEN unless an explicit OUT_OF_SCOPE or PARTIAL limitation is identified.
- No candidate was edited, supplemented with an adapter, assigned unstated defaults, or “repaired” during evaluation.

## N01 — Relation-first typed attributed hypergraph

Candidate frozen SHA-256: **c7745acf9ffeb865ad4200e6b037fd97160e098810f127165d2deb69c47a72d0**

Fixture/run binding: ORE-K7-0.1 / RUN-OPEN-0.1. The text provides exact model targets and content digests, but it does not load M0, report the Step 0 counts, or compute D0. Those observations are NOT_PROVEN.

### Per-protocol results

| Protocol | Outcome | Required fixture output/status | Mechanism present in the frozen text and evaluation |
|---|---|---|---|
| OPEN-01 provenance | NOT_PROVEN | CONTESTED for location(P)=B04@5: A02 and weak A06 support, A04 opposes, A05 remains derivative of A02, and A03 does not entail parcel location. V-PROV-1 must be scoped to C1. | N01 explicitly supplies a provenance subgraph, finite derivation DAGs, predecessor claims, temporal/scope fields, quarantining of missing provenance, and a paraconsistent support/opposition carrier. This is a close paper fit and would preserve A05 under A02 rather than count it independently. No battery adapter or produced DAG demonstrates the exact result. |
| OPEN-02 behavior | PARTIAL | EQUIVALENT on D_NOM/OBS_NOM; DISTINGUISHED on D_SAFE/OBS_SAFE with first divergence at 100 ms; no identity, authority, ownership, or commitment change. | ProtocolSpec input/output contracts, exact context keys, restricted adapters, reproducibility claims, and identity caution are relevant. The paper does not define the finite equivalence algorithm, observer/tolerance validation, reset-isolated probe ledger, certificate, or first-divergence construction. V-BEH-NOM and V-BEH-SAFE therefore remain prospective scoped views only. |
| OPEN-03 authority | PARTIAL | Oren SAFE_DOCK at t=8 is narrowly AUTHORIZED; South DRIVE(A17) at t=9.5 is CONFLICT under P01/P02/P03. V-AUTH-8 and V-AUTH-9_5 remain adjudication views and emit no command. | Typed relations, explicit effect permissions, scoped adjudication assertions, conflict retention, and Protocol-specific conflict policies can represent the two chains. No authority-chain evaluator, effectiveness-time rule execution, or judge-versus-execute adapter is supplied, so the fixture-specific outputs are not established. |
| OPEN-04 counterfactual | OUT_OF_SCOPE | do(S=CORE_ONLY) must yield HC1=B04, HP=A17, CMD_TARGET=B04, DOCKED=B04, DELIVERED=0 in B-CF-1; branch reset must leave M unchanged. | N01 has plural ViewCases and runtime overlays, but no surgical-intervention operator, structural-equation evaluator, descendant recomputation, exogenous policy, or copy-on-write counterfactual reset contract. Its unsupported-classes section conditions modal/counterfactual behavior on an executable policy or extension that is absent here. Adding one would repair the candidate and is not done. |
| OPEN-05 commitment | PARTIAL | At t=8 South remains debtor, executor transfers A17→B04 under A07+P05, CMT2 remains with A17; at t=12 CMT1 is AMBIGUOUS(H1=DISCHARGED,H2=BREACHED). | ProtocolSpec includes typed commitments; relation histories, exact effects, idempotency, and plural cases could carry the projection. The text supplies no commitment-state algebra separating executor substitution from debtor novation, no deadline evaluator, and no replayable commitment ledger for these terms. |
| OPEN-06 possibility histories | OUT_OF_SCOPE | TP0 survivors {H1,H2}; host(C1)=B04 NECESSARY; location(P)=B04 CONTINGENT; exact probability REFUSED(NO_PROBABILITY_MODEL). | N01 preserves plural cases and never coerces UNKNOWN/NOT_PROVEN, but it supplies no finite-history conditioning or modal/probability evaluator. The proposal expressly says modal/probabilistic behavior requires an executable policy/crosswalk; none is frozen with N01. |
| OPEN-07 hybrid dynamics | OUT_OF_SCOPE | THERMAL_GUARD at t=7 at (52,50); t=8− state (51,48); CHARGE_LIMIT at t=11.625 at (80,51.625); endpoint at t=12 (80,51.25), all in a simulator view only. | No continuous-state representation, unit checker, exact guard locator, reset-map semantics, event-priority solver, or trajectory error-bound contract is given. N01 lists unsupported continuous primitives without a registered tested extension. V-AUTH-8 cannot be converted into a solver by evaluation. |
| OPEN-08 conflicting views | NOT_PROVEN | At t=8 all four views produce SCOPED_CONFLICT; registry→operations→registry redetects A17→B04→A17; no global winner or sameAs. | N01 directly specifies plural tagged views, DisagreementMap, full context/cache keys, fresh rematerialization on switching, SwitchReceipt loss accounting, identity caution, and source preservation. These mechanisms fit the protocol on paper, but there are no three detection records or cache trace proving switching fidelity. |

Protocol-local scoping: explicitly designed through exact ModelRef/ProtocolInstance, normalized Context digest, Persona/worldview/evidence boundary, view expiry, and source references. No protocol-local result was actually materialized, so scope retention is NOT_PROVEN at runtime.

Switching fidelity: the SwitchReceipt records preserved/dropped/new/untranslatable references and a loss witness; switches rematerialize from the same source. The required A17→B04→A17 round trip is NOT_PROVEN without execution.

Provenance preservation: strongest direct fit is OPEN-01 through the provenance subgraph and derivation DAG. Runtime closure and the exact A05→A02 display remain NOT_PROVEN.

Effect classification and mutation boundary: READ, VIEW_MATERIALIZATION, RUNTIME_STATE_MUTATION, and MODEL_SEMANTIC_MUTATION are explicitly disjoint. Durable answer-changing changes are semantic; frozen targets reject in-place mutation and require a successor proposal. No Step 11 digest comparison proves enforcement.

Conflict/plurality: opposing supports, distinct scopes, DisagreementMap, MULTIPLE_VALID_VIEWS, and retained alternatives are explicit; registry order is not a default resolver.

Correct refusal: the paper aligns with refusing semantic promotion, identity merge, and undeclared effects, but it does not implement the battery’s exact refusal codes. Every refusal-drill item is therefore NOT_EXERCISED and the exact refusal observation is NOT_PROVEN.

### Refusal drill

| Protocol | Required refusal | Paper boundary | Observation record |
|---|---|---|---|
| OPEN-01 | EFFECT_NOT_PERMITTED | Direct frozen-model writes are denied or redirected to a successor proposal; exact code absent. | NOT_EXERCISED; exact refusal NOT_PROVEN |
| OPEN-02 | MISSING_OBSERVER; no merge | Missing Context/Protocol support and identity merge are guarded, but MISSING_OBSERVER is not defined. | NOT_EXERCISED; exact refusal NOT_PROVEN |
| OPEN-03 | EXECUTION_OUT_OF_SCOPE | Mixed effects are split and unauthorized effects denied; adjudication-specific execution code absent. | NOT_EXERCISED; exact refusal NOT_PROVEN |
| OPEN-04 | BRANCH_TO_ACTUAL_PROMOTION | Frozen-target mutation is blocked, but the counterfactual protocol itself is OUT_OF_SCOPE. | NOT_EXERCISED; OUT_OF_SCOPE/NOT_PROVEN |
| OPEN-05 | FORCED_NOVATION | Semantic identity/claim change is guarded, but novation semantics and code are absent. | NOT_EXERCISED; exact refusal NOT_PROVEN |
| OPEN-06 | NO_PROBABILITY_MODEL | Probabilistic protocol support is absent without an adapter/policy. | NOT_EXERCISED; OUT_OF_SCOPE/NOT_PROVEN |
| OPEN-07 | PHYSICAL_EXECUTION | Undeclared physical effects are denied; the hybrid simulator is OUT_OF_SCOPE. | NOT_EXERCISED; OUT_OF_SCOPE/NOT_PROVEN |
| OPEN-08 | IDENTITY_MERGE | Identity merge is semantic mutation and cannot be inferred from views; exact code absent. | NOT_EXERCISED; exact refusal NOT_PROVEN |

## N02 — Capability-secured relational fabric

Candidate frozen SHA-256: **4c447d7a122885453a489112e9fcca04eb23c333fc6022d568cf97a304336bba**

Fixture/run binding: ORE-K7-0.1 / RUN-OPEN-0.1. Exact ProtocolRef, snapshot binding, and digest resolution are designed, but M0 was not loaded and D0 was not computed. Step 0 is NOT_PROVEN.

### Per-protocol results

| Protocol | Outcome | Required fixture output/status | Mechanism present in the frozen text and evaluation |
|---|---|---|---|
| OPEN-01 provenance | PARTIAL | CONTESTED with A02 and A06 support, A04 opposition, A05 only as a copy of A02, and A03 non-entailing; V-PROV-1 scoped. | Facets/claims carry provenance, view manifests carry derivation traces, and lineage is retained. The exact text does not define provenance-parent DAG validation, derivative-root treatment, or separate authenticity/reliability/entailment fields, so it cannot establish the A05 non-corroboration observation as frozen. |
| OPEN-02 behavior | PARTIAL | D_NOM/OBS_NOM EQUIVALENT; D_SAFE/OBS_SAFE DISTINGUISHED at 100 ms; no identity promotion. | Exact Protocol schemas, context-bound materializers, identity caution, capability isolation, and conformance probes are usable substrate. No behavior-equivalence evaluator, reset policy, timing tolerance validation, witness trace, or reset-isolated sandbox contract appears. |
| OPEN-03 authority | PARTIAL | Oren safe-dock AUTHORIZED narrowly; South DRIVE(A17) at 9.5 CONFLICT. | Capability verification, authority conflict kind, exact policy Protocols, target scoping, and no ambient authority help represent adjudication. Capabilities are not themselves the P01–P04 governance semantics, and the text gives no authority-chain/effectiveness-time evaluator or adjudication-only output. |
| OPEN-04 counterfactual | OUT_OF_SCOPE | do(S=CORE_ONLY) produces DELIVERED=0 in an isolated branch and then resets. | N02 has branch-preserving replicated state, but no do-operator, structural causal model, descendant recomputation, copy-on-write counterfactual branch, or reset handle. A new Protocol/adapter would be required and is not added. |
| OPEN-05 commitment | PARTIAL | South debtor continuity, A17→B04 executor transfer, CMT2 on A17, and H1/H2 deadline ambiguity. | Versioned Protocol rules, causal operation log, idempotency, multi-value branches, and runtime transactions could host a commitment projection. The frozen text contains no commitment schema, substitution/novation separation, deadline semantics, or ledger projection for CMT1/CMT2. |
| OPEN-06 possibility histories | OUT_OF_SCOPE | Survivors {H1,H2}; NECESSARY host(C1)=B04; CONTINGENT parcel location; probability refusal. | Multi-value registers and MultipleValidViews preserve alternatives, but no enumerated-history conditioner, modal quantifier, hard/defeasible evidence compatibility rule, or probability-model gate is specified. |
| OPEN-07 hybrid dynamics | OUT_OF_SCOPE | Exact events at 7 and 11.625 and endpoint (80,51.25), with no M mutation. | The proposal gives generic sandboxed evaluators and runtime operations but no continuous variables, units, exact integration, guard detection, priorities, reset maps, or error bounds. Its physical-control support is conditional on separately certified bounds, absent here. |
| OPEN-08 conflicting views | NOT_PROVEN | Four-view SCOPED_CONFLICT and registry→operations→registry A17→B04→A17 redetection. | Snapshot/context/Persona-bound materialization, full dependency cache invalidation, MultipleValidViews, source-preserving bridges, and disclosure of switching loss are direct paper mechanisms. No view definitions were executed and no cache/detection trace exists. |

Protocol-local scoping: ProtocolRef namespaces, snapshot/context/persona/capability digests, expiry conditions, alternative branches, and derivation traces are explicit. Runtime retention is NOT_PROVEN.

Switching fidelity: switching creates a new view request and must disclose losses, mappings, changed status rules, and source preservation; when fidelity is not established the paper returns NOT_PROVEN/OUT_OF_SCOPE. The required round trip is unexecuted.

Provenance preservation: provenance is attached to facets, claims, operations, bridges, conflicts, and views. OPEN-01’s derivative-root invariant is not fully specified.

Effect classification and mutation boundary: the four effects are disjoint; materialization is pure; runtime deltas can instantiate only already-defined types; meaning-changing schema/routing/authorization/merge/status changes require a successor exact target. Enforcement and D0 preservation remain NOT_PROVEN.

Conflict/plurality: typed ConflictRecord, multi-value registers, retained branches, conditional CRDT convergence, and no last-writer-wins default preserve disagreement.

Correct refusal: frozen-model and capability boundaries align with several drills, but the required battery reason codes and non-effects were not exercised.

### Refusal drill

| Protocol | Required refusal | Paper boundary | Observation record |
|---|---|---|---|
| OPEN-01 | EFFECT_NOT_PERMITTED | MODEL_SEMANTIC_MUTATION returns FROZEN_MODEL rather than the battery code. | NOT_EXERCISED; exact refusal NOT_PROVEN |
| OPEN-02 | MISSING_OBSERVER; no merge | Identity is not inferred, but no observer-required validator/code exists. | NOT_EXERCISED; exact refusal NOT_PROVEN |
| OPEN-03 | EXECUTION_OUT_OF_SCOPE | Least-privilege operation kinds can deny execution, but no adjudication adapter/code exists. | NOT_EXERCISED; exact refusal NOT_PROVEN |
| OPEN-04 | BRANCH_TO_ACTUAL_PROMOTION | Frozen semantics cannot be replaced in place; counterfactual support is absent. | NOT_EXERCISED; OUT_OF_SCOPE/NOT_PROVEN |
| OPEN-05 | FORCED_NOVATION | No novation semantic rule or reason code is defined. | NOT_EXERCISED; exact refusal NOT_PROVEN |
| OPEN-06 | NO_PROBABILITY_MODEL | No probability evaluator/gate is defined. | NOT_EXERCISED; OUT_OF_SCOPE/NOT_PROVEN |
| OPEN-07 | PHYSICAL_EXECUTION | External effects require outbox/dedup and authority, but the exact refusal is absent. | NOT_EXERCISED; OUT_OF_SCOPE/NOT_PROVEN |
| OPEN-08 | IDENTITY_MERGE | Source identities are preserved and merge needs a Protocol-authorized semantic path; exact code absent. | NOT_EXERCISED; exact refusal NOT_PROVEN |

## N03 — Event-sourced temporal state machines

Candidate frozen SHA-256: **c9ee69330d10165f7cf89bd1678f0e3ca006e0c4e5e6e3cead81b7038fb65167**

Fixture/run binding: ORE-K7-0.1 / RUN-OPEN-0.1. ExactModelTarget and event cuts support immutable targeting, but no M0 eventization, counts, or D0 receipt is present. Step 0 is NOT_PROVEN.

### Per-protocol results

| Protocol | Outcome | Required fixture output/status | Mechanism present in the frozen text and evaluation |
|---|---|---|---|
| OPEN-01 provenance | PARTIAL | CONTESTED with A02/A06 support, A04 opposition, A05 derivative-only, A03 non-entailing; V-PROV-1 scoped. | Immutable evidence-bearing events, EvidenceClaim, derivation_ref, provenance closure, temporal intervals, and conflict sets preserve sources. The text does not specify derivative provenance DAG rules that prevent A05 from becoming an independent root or distinguish authenticity, reliability, and entailment as required. |
| OPEN-02 behavior | PARTIAL | Nominal EQUIVALENT; safety DISTINGUISHED at 100 ms; no object merge. | Event grammars, deterministic replay, exact cuts, sandboxed workers, context keys, and stable object identity are relevant. No equivalence/certificate algorithm, observer alphabet/tolerance contract, per-probe reset sandbox, or first-divergence algorithm is supplied. |
| OPEN-03 authority | PARTIAL | Narrow AUTHORIZED safe-dock and policy CONFLICT for routine A17 drive at 9.5; no command execution. | Protocol conflict policies, command gateway separation, capability manifests, contextual materialization, and causal records can separate judgment from command. The P01–P04 authority chains and effectiveness-time adjudicator are not frozen in N03. |
| OPEN-04 counterfactual | OUT_OF_SCOPE | do(S=CORE_ONLY) yields DELIVERED=0 in B-CF-1 and resets without altering actual history. | Event replay/rematerialization is not a surgical structural intervention. No SCM, do-operator, exogenous settings, copy-on-write branch state, or counterfactual reset handle appears. Treating a hypothetical event as actual would violate its append-only semantics. |
| OPEN-05 commitment | PARTIAL | South remains debtor; executor A17→B04; CMT2 stays on A17; CMT1 at t=12 is H1/H2 ambiguous. | Protocol state machines, immutable causal events, idempotent commands, temporal views, and sagas are useful process mechanisms. No frozen commitment vocabulary or transition rules separate substitution, novation, discharge, and breach for the fixture. |
| OPEN-06 possibility histories | OUT_OF_SCOPE | {H1,H2}; NECESSARY host; CONTINGENT parcel; exact probability refusal. | Plural view records and preserved statuses do not supply a possible-history model. No finite history-set conditioning, modal evaluator, probability interface, priors/likelihoods check, or witness-history output is defined. |
| OPEN-07 hybrid dynamics | OUT_OF_SCOPE | Exact hybrid trajectory with events at 7 and 11.625 and endpoint (80,51.25), as a simulator artifact only. | Event time distinctions and Protocol workers are insufficient for exact continuous integration. The text supplies no unit-aware flow solver, guard crossing, reset/priority semantics, or error bounds, and expressly excludes continuous processes when event sampling cannot preserve required fidelity. |
| OPEN-08 conflicting views | NOT_PROVEN | Four-view SCOPED_CONFLICT and A17→B04→A17 redetection without stale cache reuse. | ProtocolResultSpace, complete MaterializationKey, contextual claims, loss-declaring bridges, Persona rematerialization from the same cut, and a switch receipt directly cover coexistence and re-entry. No actual fixture views or detection/cache records were produced. |

Protocol-local scoping: exact model/Protocol/Persona/context/cut keys and namespace isolation explicitly keep derived views local. No result envelope with fixture_id and ontology_delta=[] exists.

Switching fidelity: Persona switching rematerializes from the same event cut and records changed fields/new views; it cannot translate prior conclusions silently. The required three-record round trip remains NOT_PROVEN.

Provenance preservation: immutable event envelopes, evidence references, causal closure, bridges, and derivation refs preserve source lineage; the A05-specific derivative rule is incomplete.

Effect classification and mutation boundary: four exclusive operation classes, pure materializers, validated runtime event appends, and successor-only semantic changes are explicit. Step 11 digest and reset enforcement are unobserved.

Conflict/plurality: tagged evidence-claim sets distinguish CONFLICT, UNKNOWN, NOT_PROVEN, OUT_OF_SCOPE, and MULTIPLE_VALID_VIEWS; underlying alternatives cannot be deleted by a view policy.

Correct refusal: the semantic/effect boundaries align at a high level, but no battery-specific reason codes or physical/non-effect receipts were executed.

### Refusal drill

| Protocol | Required refusal | Paper boundary | Observation record |
|---|---|---|---|
| OPEN-01 | EFFECT_NOT_PERMITTED | Frozen semantic writes have no endpoint, but the exact code is absent. | NOT_EXERCISED; exact refusal NOT_PROVEN |
| OPEN-02 | MISSING_OBSERVER; no merge | Missing context cannot default and object identity is target-scoped, but observer-specific validation is absent. | NOT_EXERCISED; exact refusal NOT_PROVEN |
| OPEN-03 | EXECUTION_OUT_OF_SCOPE | View materialization and command submission are separate endpoints; exact adjudication refusal absent. | NOT_EXERCISED; exact refusal NOT_PROVEN |
| OPEN-04 | BRANCH_TO_ACTUAL_PROMOTION | Predecessor history cannot be rewritten; no counterfactual evaluator/code exists. | NOT_EXERCISED; OUT_OF_SCOPE/NOT_PROVEN |
| OPEN-05 | FORCED_NOVATION | No novation rule or reason code is frozen. | NOT_EXERCISED; exact refusal NOT_PROVEN |
| OPEN-06 | NO_PROBABILITY_MODEL | No probability model interface/gate is frozen. | NOT_EXERCISED; OUT_OF_SCOPE/NOT_PROVEN |
| OPEN-07 | PHYSICAL_EXECUTION | Protocol code lacks unrestricted actuator access and effects require commands, but solver/refusal code is absent. | NOT_EXERCISED; OUT_OF_SCOPE/NOT_PROVEN |
| OPEN-08 | IDENTITY_MERGE | Plural views and stable identities forbid a silent merge; exact code absent. | NOT_EXERCISED; exact refusal NOT_PROVEN |

## N04 — Actor/process-calculus commitments and message causality

Candidate frozen SHA-256: **0adc320c14a177638baef7813049efda3f97d811373affe7a46cdf62b2c1d575**

Fixture/run binding: ORE-K7-0.1 / RUN-OPEN-0.1. Exact behavior/protocol targets and append-only events are defined, but M0 was not instantiated and D0 was not computed. Step 0 is NOT_PROVEN.

### Per-protocol results

| Protocol | Outcome | Required fixture output/status | Mechanism present in the frozen text and evaluation |
|---|---|---|---|
| OPEN-01 provenance | PARTIAL | CONTESTED with A02/A06 support, A04 opposition, A05 derivative-only, and A03 non-entailing; V-PROV-1 scoped. | Events and views carry evidence refs/frontiers, and ConflictSet preserves opposing claims. The proposal does not define support/opposition derivation DAGs, source-copy ancestry sufficient for A05, malformed-provenance handling, or authenticity/reliability/entailment separation. |
| OPEN-02 behavior | PARTIAL | D_NOM equivalence; D_SAFE distinction at 100 ms; no identity/authority promotion. | Object behavior targets, immutable message envelopes, deterministic inputs, sandboxed evaluators, and exact context keys can host interaction traces. There is no observer-scoped equivalence evaluator, reset-isolated probing model, certificate, timing tolerance rule, or first-divergence operator. |
| OPEN-03 authority | PARTIAL | Oren safe-dock narrowly AUTHORIZED; South routine A17 drive at 9.5 CONFLICT; adjudication emits no drive. | Role bindings, capabilities, authorization checks, message causality, and conflict sets support a governance Protocol. The exact P01–P04 authority chain, policy-effectiveness conflict, and adjudication-versus-execution adapter are absent. |
| OPEN-04 counterfactual | OUT_OF_SCOPE | do(S=CORE_ONLY) gives DELIVERED=0 in a resettable branch and leaves actual M unchanged. | Actor runtime revisions and projections do not constitute SCM intervention. No structural equations engine, do-operator, descendant recomputation, branch overlay, exogenous policy, or reset handle is defined. |
| OPEN-05 commitment | PARTIAL | South debtor continuity, executor A17→B04, CMT2 on A17, and H1/H2 discharge/breach ambiguity. | Protocol Instances, roles, commitment message families, causal transitions, compare-and-append, and idempotency are relevant. The text lacks fixture commitment terms, substitution versus novation rules, history-indexed deadline evaluation, and a commitment ledger. |
| OPEN-06 possibility histories | OUT_OF_SCOPE | TP0 leaves {H1,H2}; host is NECESSARY; parcel location CONTINGENT; exact probability is refused. | Labelled plural claims and statuses preserve alternatives, but there is no enumerated-history conditioner, modal/probability semantics, evidence compatibility function, witness map, or probability-model validation. |
| OPEN-07 hybrid dynamics | OUT_OF_SCOPE | Exact guard/transition times and endpoint (80,51.25), with simulator results never promoted to M. | The actor runtime has timers and causal events but no continuous state, unit-aware flows, exact integration, guard localization, reset maps, priorities, or error bounds. The unsupported section excludes hard-real-time/continuous-time/analog or physical-control guarantees without a suitable profile. No profile is supplied. |
| OPEN-08 conflicting views | NOT_PROVEN | SCOPED_CONFLICT across four views and A17→B04→A17 on registry→operations→registry switching. | Coexisting Protocol projections, exact view cache keys, Context/Persona/worldview scoping, SwitchManifest loss disclosure, preserved conflict/evidence/frontier, and no implicit identity merge directly fit the protocol. No fixture view outputs, pointer reset, or cache trace demonstrates the sequence. |

Protocol-local scoping: instance/protocol targets, context/persona/worldview targets, event frontiers, and dependency-keyed views are explicit. No runtime artifact proves retention/expiry.

Switching fidelity: SwitchManifest preserves identifiers, targets, frontier, evidence, unresolved alternatives, and status, and declares loss. Exact A17→B04→A17 redetection is NOT_PROVEN.

Provenance preservation: messages, events, transitions, projections, and conflict sets retain evidence refs and causal frontiers; OPEN-01’s leaf-level derivation requirements are only partial.

Effect classification and mutation boundary: all four effects have separate targets; actor/Protocol runtime changes compare-and-append under frozen evaluators; any definition/schema/role/causal-rule change requires a successor model. Enforcement and D0 equality are unobserved.

Conflict/plurality: ConflictSet, MULTIPLE_VALID_VIEWS, labelled claim sets, no global worldview, and no silent resolver preserve disagreement.

Correct refusal: unavailable evaluators and forbidden effects fail closed in the paper, but the battery’s exact refusal codes and zero-effect receipts were not exercised.

### Refusal drill

| Protocol | Required refusal | Paper boundary | Observation record |
|---|---|---|---|
| OPEN-01 | EFFECT_NOT_PERMITTED | Frozen semantic mutation is forbidden; exact reason code absent. | NOT_EXERCISED; exact refusal NOT_PROVEN |
| OPEN-02 | MISSING_OBSERVER; no merge | No resolver may infer identity and missing context is not guessed; observer-specific code absent. | NOT_EXERCISED; exact refusal NOT_PROVEN |
| OPEN-03 | EXECUTION_OUT_OF_SCOPE | Protocol projections and actor messages are separate, but no adjudication-specific execution refusal exists. | NOT_EXERCISED; exact refusal NOT_PROVEN |
| OPEN-04 | BRANCH_TO_ACTUAL_PROMOTION | Successor-only semantics block rewriting history; counterfactual protocol absent. | NOT_EXERCISED; OUT_OF_SCOPE/NOT_PROVEN |
| OPEN-05 | FORCED_NOVATION | No debtor-novation semantics or exact code is frozen. | NOT_EXERCISED; exact refusal NOT_PROVEN |
| OPEN-06 | NO_PROBABILITY_MODEL | No numeric probability evaluator is supplied. | NOT_EXERCISED; OUT_OF_SCOPE/NOT_PROVEN |
| OPEN-07 | PHYSICAL_EXECUTION | Undeclared actuator effects are not available and continuous/physical guarantees are unsupported. | NOT_EXERCISED; OUT_OF_SCOPE/NOT_PROVEN |
| OPEN-08 | IDENTITY_MERGE | Views cannot create global identity and semantic edits require successors; exact code absent. | NOT_EXERCISED; exact refusal NOT_PROVEN |

## Group deterministic-sequence summary

This is an unweighted observation set. It is not a score, ranking, or selection.

| Sequence portion | Same-fixture required observation | N01–N04 evaluation status |
|---|---|---|
| Step 0 | Load one immutable M0; counts 13 objects, 12 relations, 12 events, 10 artifacts, 7 policies, 3 histories; save D0. | Candidate texts define immutable/exact targets, but none supplies a load/count/digest receipt. NOT_PROVEN for every candidate. |
| Steps 1–4 | Provenance CONTESTED; nominal EQUIVALENT; safety DISTINGUISHED at 100 ms; safe-dock AUTHORIZED and routine-drive CONFLICT. | Required outputs are fixed by the battery. Candidate mechanisms range from direct provenance/view support to generic adapters, but none produces a RUN-OPEN-0.1 envelope. Paper-only or PARTIAL as recorded above. |
| Step 5 | Counterfactual CORE_ONLY gives DELIVERED=0 and the branch resets. | No candidate freezes an SCM/do evaluator and reset contract for this fixture. OUT_OF_SCOPE without candidate repair. |
| Step 6 | Debtor South persists; executor A17→B04; CMT2 stays A17; t=12 is H1/H2 AMBIGUOUS. | All four offer process/relation/runtime substrate, but no exact commitment-continuation semantics. PARTIAL. |
| Step 7 | TP0 survivors {H1,H2}; NECESSARY host, CONTINGENT parcel; probability refusal. | No candidate freezes a finite-history modal/probability evaluator. OUT_OF_SCOPE; exact refusal unexercised. |
| Step 8 | Quoted V-AUTH-8 alone enables the local H1 simulator; events 7 and 11.625; endpoint (80,51.25). | No candidate supplies the hybrid solver. No authority view was actually materialized to quote. OUT_OF_SCOPE and no cross-context conclusion was promoted. |
| Steps 9–10 | Four-view SCOPED_CONFLICT; registry→operations→registry redetection A17→B04→A17. | Each candidate explicitly preserves plural, context-keyed views and prohibits global identity flattening. Runtime switching fidelity remains NOT_PROVEN because there are no view/detection/cache records. |
| Step 11 | Reset all R namespaces; semantic digest remains D0; every result has ontology_delta=[]. | All four paper boundaries distinguish runtime/view state from frozen semantics and require successor-only semantic change. No reset receipts, exact result envelopes, ontology_delta fields, or final digest comparison exist. NOT_PROVEN. |
| Refusal drill | Eight exact typed refusals with no forbidden side effects. | The papers generally encode the underlying semantic/effect boundaries, but none executes the drill or consistently defines the battery-specific reason codes. Records are NOT_EXERCISED; exact refusal behavior is NOT_PROVEN. |

Cross-protocol sequence locality was maintained in this evaluation: no earlier required conclusion was treated as a later input except the battery-authorized prospective quote of V-AUTH-8 at Step 8, and that quote was not treated as an existing artifact because no candidate produced it. No branch, history choice, authority result, behavior result, Persona result, or view denotation was promoted into M.

The battery completion condition is not met for any of N01–N04 on the authorized evidence: there is no individual runtime observation set, no exercised reset handle set, no D0 equality receipt, and no complete Result envelopes with ontology_delta=[]. This conclusion is limited to the frozen proposal texts and does not speculate about any implementation or held-out material.
