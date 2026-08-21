# HELD-OUT battery evaluation — N05 through N08

Fixture checkpoint: `S0` at `10:00:00` with ledger `L0` and registry `R0`  
Candidate state: unchanged frozen architectures `N05`, `N06`, `N07`, `N08`  
Evaluation kind: post-freeze, paper-level application of `H01`–`H10`

## Evaluation boundary and state discipline

Each unrelated case starts from the same `S0/L0/R0`. The H03 extra clear, H04 counterfactual relation additions, and H09 matching-clear subprobes are isolated variants and never modify `S0`. H07 is the one legal sequential Protocol Model mutation. H10 continues only from that candidate's H07 state; its sensor ping remains observation-only, and its revision-invalidation subprobe is a separate continuation. No candidate result is used as another candidate's input.

The outcome vocabulary is:

- `SUPPORTED`: the frozen architecture supplies a sufficient paper-level mechanism for the required behavior and boundary;
- `PARTIAL`: some required behavior is representable, but a mandated state, transaction, or attribution mechanism is not frozen;
- `OUT_OF_SCOPE`: the required refusal is an honest local scope result;
- `REFUSE`: the case's prohibited mutation is rejected at the architecture boundary;
- `NOT_PROVEN`: the frozen paper does not establish the required operation.

These are architecture observations, not implementation executions. All latency, throughput, resource-bound enforcement, crash behavior, byte-level replay, exact receipt serialization, and actual end-to-end results remain `NOT_PROVEN`. No capability absent from a candidate is supplied as a repair. There is no scalar, aggregation, ranking, winner, or preferred architecture.

## Case-local ground truth retained for every candidate

| Case | Required paper-level output and provenance |
|---|---|
| `H01` | Four separately typed fields: physical `{robot:rhea}`, accountable `{person:kai}`, pending requested recipient `{robot:sol}`, beneficiary `{org:clinic}`. Custody/accountability/beneficiary come from `S0`; pending intent uses L0 cancellation seq 8 followed by request seq 9. |
| `H02` | From `S0` only: `QUALIFIED(rhea,vial-a)`; `UNQUALIFIED(sol,cell-b,{assigned-person-not-authorized-for-current-zone})`; no Tala result. L0 is excluded. |
| `H03` | From ordered L0: only `(zone:cold,smoke,generation=2)` is open, acknowledgers exactly `{person:kai}`. A later mismatched clear of generation 1 changes nothing. |
| `H04` | Pending request is seq 9. It is `BLOCKED` for missing Sol cold-chain certification, Mira cold-zone authorization, and active generation-2 smoke. In the isolated relation variant adding the first two facts, only the alarm failure remains. |
| `H05` | Labels: vial-a `{review,cool}`; cell-b `{}`; cargo literal-star `{literal-id}`; protocol literal-star `{literal-protocol-id}`; rhea `{}`. The supplied nonstandard exclusion semantics control. |
| `H06` | `OUT_OF_SCOPE` for Mira's secret intent/confidence; acknowledgment and assignment may be listed only as non-probative evidence. No score or label. |
| `H07` | Revision 1 gives `GATE_CLOSED(1,2)`; legal runtime patch creates a later revision of the same instance with threshold 1; re-evaluation proposes `AUTHORIZE_ENTRY(rhea,cold)` but does not execute it. Immutable fields and `S0` remain unchanged. |
| `H08` | Entire activation-plus-semantic-redefinition request is atomically refused as illegal semantic mutation. No adapter activation, synthetic handoff commit, shadow custody, or semantic override. |
| `H09` | KeepCold proposes `MOVE(rhea,cold)`; SmokeBlock proposes `DO_NOT_ENTER(rhea,cold)`; both and their conflict remain. An isolated matching clear silences only SmokeBlock and removes only the conflict. |
| `H10` | From H07's threshold-1 revision, LIVE latches the proposal and pairs it with all four H01 fields; AUDIT renders the same item as observed without re-evaluation; ping changes nothing; LIVE restoration does not reset the latch. A later legal threshold-2 revision invalidates the latch and returns only `GATE_CLOSED`. |

Across every case, `located_at(robot:rhea,zone:dock)` and `carries(robot:rhea,cargo:vial-a)` remain committed. A ping, request, proposal, rejection, display mapping, isolated counterfactual, or context switch never changes those facts.

## N05 — Witnessed Relation/Event Incidence Model

### Per-case observations

| Case | Outcome and minimal output | Mechanism, plurality, relation/event stress, provenance | Mutation, refusal, switching, and failure boundary |
|---|---|---|---|
| `H01` | `SUPPORTED`; architecture-level output is the four labeled sets exactly as specified. | Typed output ports, bounded joins, `ViewClaim/ViewSet`, event transition rules, and a complete ViewArtifact key preserve four lenses without treating their different identities as conflict. Provenance binds the three `S0` relation paths and L0 seq 8→9 cancellation/request order. | `READ+VIEW_MATERIALIZATION`; no custody event. Plurality is a record shape, not a vote or global status. No `PLURAL_COLLAPSE` or `INTENT_AS_STATE` is implied by the paper model.
| `H02` | `SUPPORTED`; Rhea is qualified, Sol is unqualified for the exact authorization clause, and Tala has no output. | Exact ObjectSnapshots, typed relation endpoints, declared evidence/input projections, and bounded relational composition support the closed four-family slice. L0 is absent from the invocation projection and cannot supply location or custody. | Pure read/view. No event replay or state advance. Event exclusion is visible in the input projection digest, preventing `EVENT_LEAK_INTO_SNAPSHOT` at architecture semantics.
| `H03` | `SUPPORTED`; only generation 2/Kai is open, and the isolated generation-1 clear is a no-op. | N05's transition rules, effective/recorded times, immutable events, revision-contiguous vertical composition, and deterministic invocation contract can consume the supplied ledger sequence, keep alarm keys/generations separate, and deduplicate distinct people. Provenance retains seq 4–6 and 10–11 plus the variant clear. | A view/status computation only; no relation is asserted. Actual tie-order/replay behavior remains `NOT_PROVEN` without an implementation, but the paper mechanism need not substitute a relation snapshot for the ordered ledger.
| `H04` | `SUPPORTED`; seq 9 is pending and all three failures are returned; the isolated relation variant leaves only the alarm failure. | The candidate's core relation/event co-constitution directly supports the current-carrier/certification/assignment/location join plus cancellation and keyed alarm history. A coverage receipt can retain all failed obligations rather than short-circuiting. The alternate snapshot receives a different exact snapshot/context key. | Both runs are views. The alternate snapshot is not installed as an Object revision, and no transfer event is proposed. No `PARTIAL_HYBRID_JOIN` or `CROSS_CASE_STATE_LEAK` is required by the frozen semantics.
| `H05` | `NOT_PROVEN`; the five exact label sets are not credited to an N05 execution. | Ordered clauses and namespace-qualified values are representable, but the frozen Protocol IR lists no string-segment iterator, quoted-literal/wildcard matcher, or clause-local negation operation. Expanding this case into fixture-specific equality tests would be a repair. | Honest admission would return `OUT_OF_SCOPE` if the supplied descriptor cannot compile. The named exposure is `DEFAULT_PATTERN_OVERRIDE`, but it is not recorded as empirically seen.
| `H06` | `OUT_OF_SCOPE` as required; no mental-state label or confidence is produced. | N05 distinguishes `UNKNOWN`, `NOT_PROVEN`, `CONFLICT`, and `OUT_OF_SCOPE`, requires declared evidence bounds, and does not infer semantics for unsupported opaque claims. Acknowledgment/assignment evidence can remain visible as non-entailing provenance. | No runtime or semantic effect. The refusal is granular and does not erase useful evidence. `UNSUPPORTED_GUESS` is not licensed.
| `H07` | `PARTIAL`; `GATE_CLOSED(1,2)` and the threshold-1 proposal rule are expressible, but the required persistent patch/history operation is not established. | ProtocolDefinition is immutable and ProtocolInvocation carries parameters; runtime events have revisions and idempotency. The frozen stores contain protocol versions and invocations but no explicit first-class `ProtocolInstance` with schema-declared mutable parameters and revision history. Treating the Protocol as an unstated Object kind would be a repair. | A legal runtime patch could be isolated from Object semantics, but its exact target/history is `NOT_PROVEN`. Blanket refusal would expose `PROTOCOL_PATCH_REJECTED`; modeling the proposal as a domain event would expose `PROTOCOL_PATCH_BECOMES_DOMAIN_MUTATION`. Neither is asserted as an observed runtime failure.
| `H08` | `PARTIAL`; the semantic redefinition is refused, but atomic refusal of the whole mixed request is not guaranteed. | Effect separation, immutable predicate definitions, exact semantic successor rules, and no view-as-state correctly recognize the requested carries/handoff rewrite as illegal. However N05 explicitly splits mixed requests into dependency-linked, separately authorized steps. | The forbidden semantic step cannot mutate `S0`, but the paper does not guarantee that legal activation/display setup is rolled back or withheld when the later semantic step fails. This is an unproven atomicity boundary for `ILLEGAL_COMPATIBILITY_COERCION`, not a claim that coercion occurred.
| `H09` | `SUPPORTED`; both MOVE and DO_NOT_ENTER proposals plus an explicit conflict are retained; the clear variant leaves only MOVE. | Multiple Protocols, `COMPOSE_BOUNDED`, action/event proposals, scoped claims, and `ConflictRecord` preserve both child outputs and their provenance. Current route/cold-zone facts drive KeepCold; generation-2 event state drives SmokeBlock. Dependency invalidation handles the matching clear. | View/proposal outputs only. No Persona or presentation rule may rank a conflict, and no command executes. The paper boundary excludes `SILENT_ARBITRATION` and preserves domain state.
| `H10` | `PARTIAL`; plural Q views and context-specific rendering are representable, but the required latch sequence is not established. | Workflow Protocols, parent invocation references, runtime events, `COMPOSE_BOUNDED`, full view keys, and PersonaSwitch/FidelityReport cover pieces of LATCH. The H07 child lacks an explicit persistent ProtocolInstance revision, and no composition-instance state record freezes latched child output/checkpoint across contexts. | LIVE/AUDIT rendering can remain views, but latch persistence, context-noninvalidation, and child-runtime-revision invalidation are `NOT_PROVEN`. The named exposure is `LATCH_IDENTITY_LOSS`; the sensor ping still cannot mutate location under any legal N05 effect.

### N05 invariant and behavioral-dimension record

| Dimension | Required reporting label and evidence |
|---|---|
| Object semantic fidelity | `observed consistently` in H01–H04, H06, and H09; all proposals/views leave S0 meanings unchanged. |
| Protocol first-classness | `observed with named boundary`: immutable definitions and invocations are first-class, but H07/H10 persistent runtime-instance parameter history is not explicit. |
| Bidirectional responsiveness | `observed with named boundary`: relation/event changes affect H01–H04/H09; protocol-runtime change in H07 is under-specified. |
| Unseen definition uptake | `observed with named boundary`: finite relation/event definitions fit; H05 pattern execution is `NOT_PROVEN`. |
| Protocol switching/context integrity | `observed with named boundary`: switch receipts exist, but LATCH state across LIVE/AUDIT is not established. |
| Cross-protocol semantic stability | `observed consistently`: no supported case retypes carries, location, intent, or proposals. |
| Plurality | `observed consistently` through H01 ViewSet and H09 ConflictRecord. |
| Relation/event boundary control | `observed consistently` in the paper mechanisms for H02, H03, and H04; runtime replay remains `NOT_PROVEN`. |
| Conflict honesty | `observed consistently` for H09; no implicit child priority is defined. |
| Unsupported refusal | `observed consistently` for H06. |
| Mutation governance | `observed with named boundary`: H08 semantic rejection is strong, while H07 legal Protocol Model patch targeting is incomplete. |
| Non-execution/transaction discipline | `observed with named boundary`: proposals cannot execute, but H08 whole-request atomicity is not frozen. |
| Provenance and temporal attribution | `observed with named boundary`: views/events are attributable; H07/H10 instance-revision attribution is incomplete. |
| Metamorphic consistency | `observed with named boundary`: H03/H04/H09 variants are supported; H10 revision invalidation and H05 exact calculus are not proven. |

No high-information failure signature is recorded as empirically observed from a paper. The named unproven exposures are `DEFAULT_PATTERN_OVERRIDE`, `PROTOCOL_PATCH_REJECTED`, `PROTOCOL_PATCH_BECOMES_DOMAIN_MUTATION`, `ILLEGAL_COMPATIBILITY_COERCION`, and `LATCH_IDENTITY_LOSS`.

## N06 — Causal-Incidence Co-Constitution

### Per-case observations

| Case | Outcome and minimal output | Mechanism, plurality, relation/event stress, provenance | Mutation, refusal, switching, and failure boundary |
|---|---|---|---|
| `H01` | `SUPPORTED`; all four labeled values are retained exactly. | Typed incidences, claims, event configurations, deterministic materializers, `MULTIPLE_VALID`, and complete materialization keys support the relation-derived fields and cancellation-aware intent field. L0 seq 8/9 and each S0 relation are provenance-bearing inputs. | View only. Different role values are record fields, not contradictory candidates; no custody commit occurs.
| `H02` | `SUPPORTED`; exact Rhea/Sol results and no Tala result. | The finite incidence hypergraph and declared accepted-evidence boundary allow a deterministic materializer over only S0's four clause families. Event/configuration data outside the declared input is excluded and visible in the materialization receipt. | Pure materialization; no event replay or branch advance. The closed-world rule applies only inside the four named relation families.
| `H03` | `SUPPORTED`; only generation 2 with Kai remains, and the extra generation-1 clear is inert. | A finite Protocol event signature, prime/causal event configuration, event effects/guards, and provenance can encode keyed generation state and the supplied ledger sequence. Same-time raise/ack order is part of the provided ordered input rather than inferred from wall time. | View/evaluator state only. No incidence is fabricated from alarm events. Actual scheduler ordering is paper-only and remains `NOT_PROVEN` operationally.
| `H04` | `SUPPORTED`; three failures in S0/L0, alarm-only in the isolated counterfactual. | N06 directly combines incidence predicates with event configurations. Its explicit Branch and `evaluate_counterfactual` mechanism give the alternate relation snapshot a parent configuration, assumptions, provenance, and isolation. Complete failed obligations remain a set. | Counterfactual branch is not observed history and is closed after the subprobe. No custody event or relation is committed.
| `H05` | `NOT_PROVEN`; no exact five-subject result is attributed to N06. | Protocol predicates/materializers and bounded PIR could host a finite matcher, but the frozen PIR and support envelope do not specify namespace-segment string operations, quoted wildcard literals, or the nonstandard leading-`!` update rule. Assuming a bridge/materializer is a repair. | Capability reporting should be `PARTIAL` or `OUT_OF_SCOPE` with excluded constructs. The diagnostic exposure is `DEFAULT_PATTERN_OVERRIDE`, not an observed failure.
| `H06` | `OUT_OF_SCOPE` as required. | `EpistemicResult.OUT_OF_SCOPE`, accepted evidence boundaries, and the rule against assigning semantics to unmapped constructs stop the private-intent request. Direct acknowledgment/assignment evidence can be returned as non-probative lineage. | No branch, runtime, event, relation, or semantic mutation. No score is fabricated.
| `H07` | `PARTIAL`; gate evaluation is expressible, but legal persistent Protocol Model patch/history is not fully modeled. | Protocol definitions are immutable Objects and the architecture has exact revisions, receipts, and ephemeral evaluator/session runtime state. It does not freeze a separate ProtocolInstance schema with mutable parameters, stable instance identity, and revisioned history. Mixed use of a Protocol successor would incorrectly semanticize a declared runtime parameter. | Domain stability is protected, but accepting the exact legal mutation is `NOT_PROVEN`. The possible diagnostic boundaries are `PROTOCOL_PATCH_REJECTED` or `PROTOCOL_PATCH_BECOMES_DOMAIN_MUTATION`; neither is claimed observed.
| `H08` | `PARTIAL`; illegal redefinition is denied, but all-or-nothing handling of activation plus denial is not established. | Exact Protocol versions, effect classification, authorization, no-view-as-truth, and successor lineage prevent a silent carries/handoff rewrite. N06 explicitly decomposes mixed requests into separately receipted steps, despite local atomic commits per step. | No illegal semantic step can commit, but adapter activation/display state might be a separately applied legal step. Therefore the required atomic refusal and unchanged Protocol Model are `NOT_PROVEN`; this is the `ILLEGAL_COMPATIBILITY_COERCION` exposure.
| `H09` | `SUPPORTED`; both proposals and conflict remain, and the clear variant removes only SmokeBlock/conflict. | Multiple Protocols may coexist through declared bridges/composition; Claims, conflict rules, ProposedEvents, event configurations, and causal dependencies retain both children. S0 relations ground KeepCold; generation-2 configuration grounds SmokeBlock. | No authorize/commit call follows evaluation. `CONFLICT` cannot be collapsed to a chosen action, and the clear is confined to the isolated ledger branch.
| `H10` | `PARTIAL`; Q plurality/context rendering are modelable, but the stateful continuation cannot be fully attributed. | Counterfactual/branch separation, complete context materialization keys, SwitchEvent/FidelityReceipt, and multiple Protocols support several pieces. The prerequisite H07 runtime instance revision and a first-class composition-instance latch state are not frozen. | Context-only switching need not rewrite semantics, but latch persistence, stored checkpoint/revision identity, and invalidation on the later H07 runtime revision remain `NOT_PROVEN`. Sensor pings remain observations. Named exposure: `LATCH_IDENTITY_LOSS`.

### N06 invariant and behavioral-dimension record

| Dimension | Required reporting label and evidence |
|---|---|
| Object semantic fidelity | `observed consistently` across supported/refused cases; configurations and branches do not rewrite S0. |
| Protocol first-classness | `observed with named boundary`: versioned definitions are first-class, but H07/H10 runtime instance history is not explicit. |
| Bidirectional responsiveness | `observed with named boundary`: incidence/event responsiveness is strong; legal Protocol runtime mutation is incomplete. |
| Unseen definition uptake | `observed with named boundary` because H05's pattern calculus is outside the frozen executable detail. |
| Protocol switching/context integrity | `observed with named boundary`: switch fidelity exists, but H10 latch continuity lacks its prerequisite instance state. |
| Cross-protocol semantic stability | `observed consistently`; observed/proposed/counterfactual and semantic states remain distinct. |
| Plurality | `observed consistently` in H01 and H09. |
| Relation/event boundary control | `observed consistently` for H02–H04 at architecture semantics. |
| Conflict honesty | `observed consistently` for H09. |
| Unsupported refusal | `observed consistently` for H06. |
| Mutation governance | `observed with named boundary`: illegal semantic mutation is blocked, but H07 legal runtime mutation and H08 batch atomicity are incomplete. |
| Non-execution/transaction discipline | `observed with named boundary`: proposals do not execute; H08 is atomic only per decomposed step. |
| Provenance and temporal attribution | `observed with named boundary`: causal/configuration receipts are strong; H07/H10 ProtocolInstance revision attribution is absent. |
| Metamorphic consistency | `observed with named boundary`: H03/H04/H09 are supported; H05 and H10 remain unproven. |

No failure signature is empirically observed. Named exposures are `DEFAULT_PATTERN_OVERRIDE`, `PROTOCOL_PATCH_REJECTED`, `PROTOCOL_PATCH_BECOMES_DOMAIN_MUTATION`, `ILLEGAL_COMPATIBILITY_COERCION`, and `LATCH_IDENTITY_LOSS`.

## N07 — Typed Protocol Interpreter over a Stable Evidence Kernel

### Per-case observations

| Case | Outcome and minimal output | Mechanism, plurality, relation/event stress, provenance | Mutation, refusal, switching, and failure boundary |
|---|---|---|---|
| `H01` | `SUPPORTED`; all four labeled sets are returned. | Domain output ports, bounded collection operations, Relation/Event subscriptions, Status plurality, and complete ViewKeys preserve the four lenses. The input cutoff and dependency set cite S0 relations and L0 seq 8/9. | View only; intent does not become state. No aggregator or single-answer status is invoked.
| `H02` | `SUPPORTED`; Rhea qualified, Sol unqualified with the exact missing condition, no Tala. | Snapshot reads over declared relation indexes and a frozen evidence cutoff honor the relation-only input port. The typed VM performs the finite join; L0 is not an activation dependency. | `READ/VIEW`; no runtime transition. The output receipt makes event exclusion auditable.
| `H03` | `SUPPORTED`; generation 2/Kai only; mismatched clear no change. | N07 explicitly records ingestion sequence separately from event time, orders within a partition by ingestion sequence, and supports finite-state transitions, duplicate policy, and deterministic replay receipts. This directly covers equal-time tie order and keyed generations. | Runtime reducer state, if used, is a resettable ProtocolInstance partition; the result is a view. No relation is inferred.
| `H04` | `SUPPORTED`; full three-failure result and alarm-only counterfactual result. | Typed bytecode combines current relation indexes with ordered event inputs and bounded collections. Experiment/scenario identifiers and full ViewKeys isolate the alternate relation snapshot; dependency lists show which relation additions changed the failed set. | View-only alternate input; no semantic head or Object fact changes. Complete collection processing prevents first-failure short-circuit unless the Protocol says so.
| `H05` | `SUPPORTED` at architecture semantics; exact five label sets are the required materialization. | Pure VM operations include `match`, `compare`, and bounded collection iteration. A typed finite-state matcher can distinguish quoted literal bytes from unquoted wildcard tokens, enforce namespace-segment scope, and process clauses in order with label-local updates. The supplied nonstandard rule, not a familiar precedence rule, is the Protocol bytecode's semantics. | Pure view; inert registry subjects gain no domain meaning. Actual compiler correctness remains `NOT_PROVEN`, but no extra opcode or external adapter is required by the frozen instruction families.
| `H06` | `OUT_OF_SCOPE` as required. | Admission/output status namespaces, bounded evidence queries, and refusal rules prevent inference of opaque mental state or confidence. Relevant observed facts retain source attribution without becoming proxies. | No journal effect except refusal/audit receipt. No guessed score.
| `H07` | `SUPPORTED`; revision 1 closes the gate, the schema-legal patch advances the same ProtocolInstance runtime revision, and the later run emits the proposal without execution. | N07 explicitly separates ProtocolRevision from ProtocolInstance, stores a runtime state revision, accepts typed state transitions with compare-and-swap/idempotency, and records before/after in the execution receipt. Immutable alarm/action fields remain definition-pinned. | `RUNTIME_STATE_MUTATION` only. The proposal is an output/effect request and cannot change Object state without an executor. Instance history and S0 dependencies remain attributable.
| `H08` | `REFUSE` as required; the whole mixed request is rejected before activation/display mapping or semantic rewrite commits. | The VM constructs an effect journal, validates the whole journal against effect-specific invariants before commit, rejects in-place semantic overwrite, and commits atomically inside the local transaction domain. The illegal carries/handoff change invalidates the journal. | No runtime, view, or semantic component commits; no synthetic event. This meets the adapter's atomic refusal rule and excludes `ILLEGAL_COMPATIBILITY_COERCION` at architecture semantics.
| `H09` | `SUPPORTED`; both proposals, child provenance, and explicit conflict; matching clear leaves only MOVE. | Multiple Protocols and StatusAssertions coexist; bounded composition/aggregation requires an explicit Protocol and conflict policy. The no-arbiter composition returns side-by-side outputs, while relation and event dependency indexes make the clear invalidate only SmokeBlock/conflict. | Proposals are not commands. No priority or compromise is admitted, so no `SILENT_ARBITRATION` or domain event occurs.
| `H10` | `SUPPORTED`; LIVE/AUDIT/ping/LIVE and revision-invalidation outputs follow the definition. | A novel finite LATCH compiles to typed state-machine bytecode in its own ProtocolInstance. The latch stores P output, child runtime revision, checkpoint, and dependency set. View/context rules render without recomputing; SwitchEvent/receipt preserves declared state; H07 runtime revision change invalidates the dependency. Q remains the four-field H01 view. | Latch state is R, rendering is VIEW, and the ping is captured observation only. The threshold-2 child revision changes only Protocol runtime; the old latch/output remains historical. No location/custody mutation or action execution.

### N07 invariant and behavioral-dimension record

Every dimension below is `observed consistently` at frozen architecture semantics, with actual implementation execution still `NOT_PROVEN`:

1. Object semantic fidelity — H01–H10 keep S0 facts and meanings fixed.
2. Protocol first-classness — ProtocolRevision, ProtocolInstance, context/Persona partition, runtime revision, composition, and receipts are distinct.
3. Bidirectional responsiveness — H02–H04/H09 respond to inputs; H07 runtime mutation changes only evaluation behavior.
4. Unseen definition uptake — H05 and H10 fit bounded typed VM operations without familiar-default substitution.
5. Protocol switching/context integrity — H10 uses SwitchEvent, sealed state, destination views, and exact return behavior.
6. Cross-protocol semantic stability — views, runtime, proposals, and semantic successors have disjoint stores/effects.
7. Plurality — all H01/Q fields and both H09 actions remain.
8. Relation/event boundary control — H02 input projection, H03 ingestion sequence, and H04 hybrid dependencies are explicit.
9. Conflict honesty — H09 conflict remains without an aggregator.
10. Unsupported refusal — H06 stops at the declared evidence classes.
11. Mutation governance — H07 accepts legal R mutation; H08 rejects the illegal mixed journal atomically.
12. Non-execution and transactional discipline — no proposal has executor authority; local journals prevalidate and commit atomically.
13. Provenance and temporal attribution — cutoffs, sequences, instance revisions, contexts, dependencies, and receipts remain pinned.
14. Metamorphic consistency — H03, H04, H09, and H10 isolated changes affect only declared outputs.

No high-information failure signature is observed at paper semantics. Whether an implementation avoids every listed signature is `NOT_PROVEN` until the conformance traces run.

## N08 — Proof-carrying Object/Protocol contracts

### Per-case observations

| Case | Outcome and minimal output | Mechanism, plurality, relation/event stress, provenance | Mutation, refusal, switching, and failure boundary |
|---|---|---|---|
| `H01` | `SUPPORTED`; the four separately typed sets are preserved. | Typed Views/Judgments, FactSets, first-class Relations/Events, Protocol role outputs, and plurality rules support the four-field record. Evidence horizon/derivation cites the current S0 relations and cancellation-aware L0 intent. | Pure VIEW. `MULTIPLE_VALID` is not needed to conflate record fields; no selection or custody mutation occurs.
| `H02` | `SUPPORTED`; exact Rhea/Sol outcomes and no Tala. | Contract input scope and ViewRequest evidence horizon can expose only the committed relation slice. Object/Relation read surfaces and a typed state machine perform the finite join, while evidence_omitted records L0 as outside the protocol. | READ/VIEW only. Closed world is local to the four declared fields, not a global absence rule.
| `H03` | `SUPPORTED`; generation 2/Kai only and mismatched-clear invariance. | Accepted event schemas, TypedStateMachine, logical time, causal parents, stable input delivery, and at-least-once deduplication can maintain keyed generation state over the explicitly ordered L0 input. Acknowledgers are a distinct-person set. | ProtocolInstance reducer state is runtime-local; output is a View. No Relation/Fact is created. Concrete tie-order execution remains paper-only `NOT_PROVEN`.
| `H04` | `SUPPORTED`; three failures, then alarm-only in the isolated variant. | A contract can bind relation and event roles, evaluate current Object/Relation revisions plus event horizon, and return all failed claims in a Judgment/View. The alternate relation set is an isolated contextual input with a distinct derivation and no installed successor. | VIEW only; no ActionProposal/semantic successor. Counterfactual relation additions do not leak to S0.
| `H05` | `NOT_PROVEN`; exact labels are not credited. | N08 EntityIds are opaque, and extension bytes may be interpreted only with a supported decoder/contact. The frozen substrate and TypedStateMachine do not itself supply the namespace-segment wildcard/quoted-literal decoder or nonstandard exclusion calculus. Supplying one now would be a repair. | Correct host behavior is `UNSUPPORTED`/`NOT_PROVEN` for semantic execution while preserving the definition opaquely. Named exposure: `DEFAULT_PATTERN_OVERRIDE`, not an observed result.
| `H06` | `OUT_OF_SCOPE` as required. | `Judgment.OUT_OF_SCOPE`, explicit evidence horizons, proof specificity, and opaque restraint prevent a secret-intent conclusion or confidence score. Acknowledgment/assignment may remain cited as non-probative facts. | No proposal, runtime transition, or semantic effect.
| `H07` | `SUPPORTED`; before/after gate outputs, same instance with later runtime revision, immutable fields, and unchanged S0. | N08 explicitly defines ProtocolInstance parameter bindings, runtime_revision/runtime_state, declared transitions, idempotency, and the RUNTIME_MUTATION class. A schema-declared threshold change advances the instance state revision without changing the Protocol semantic ID. | Legal Protocol runtime mutation is accepted and receipted. The action remains an ActionProposal and cannot pass the Object apply/authority gate because no executor exists.
| `H08` | `PARTIAL`; illegal semantic rewrite is refused, but whole mixed-request atomicity is not guaranteed by the host batch semantics. | Contract refusal rules, semantic immutability, authority intersection, fresh-successor requirements, and distinction between display Views and predicate semantics identify the carries/handoff rewrite as illegal. Yet N08 explicitly allows partial batch application with per-component receipts/applied prefixes. | The semantic component cannot commit, but adapter activation/display setup might be a legal applied prefix unless the particular contract preflights the entire batch. No such proof bundle is supplied. Atomic refusal is therefore `NOT_PROVEN`; named exposure `ILLEGAL_COMPATIBILITY_COERCION`.
| `H09` | `SUPPORTED`; both child proposals and conflict; clear variant leaves only MOVE. | Parallel Protocol execution, typed ActionProposals, contract compatibility/conflict Judgments, and no implicit resolution preserve both children. Relation/event subscriptions and dependency derivations localize the matching-clear change. | Object authority/invariant gate receives proposals but no executor applies them. No priority, fusion, compromise, or semantic mutation.
| `H10` | `SUPPORTED`; the complete LIVE/AUDIT/ping/LIVE and runtime-revision invalidation behavior is expressible. | LATCH is a bounded TypedStateMachine ProtocolInstance holding stored P, H07 runtime revision, checkpoint, and obligations. Context-indexed Views implement rendering; SwitchPlan/context_map preserves latch state; the H07 runtime revision is a dependency that invalidates it. Q remains a four-field View. | Latch changes are RUNTIME_MUTATION; render changes are VIEW. Ping is observation-only. New threshold-2 runtime revision invalidates without rewriting historical output, child definitions, or S0.

### N08 invariant and behavioral-dimension record

| Dimension | Required reporting label and evidence |
|---|---|
| Object semantic fidelity | `observed consistently`; Object-side apply/authority checks and semantic IDs protect S0. |
| Protocol first-classness | `observed consistently` through Protocol/ProtocolVar/ProtocolInstance/runtime revision/SwitchPlan. |
| Bidirectional responsiveness | `observed consistently` in H02–H04, H07, H09, and H10. |
| Unseen definition uptake | `observed with named boundary`: H10 fits TypedStateMachine contact, but H05 lacks a supported identifier-pattern decoder. |
| Protocol switching/context integrity | `observed consistently` for H10 at architecture semantics. |
| Cross-protocol semantic stability | `observed consistently`; views, proposals, runtime, and semantic successors remain distinct. |
| Plurality | `observed consistently` in H01, H09, and H10 Q. |
| Relation/event boundary control | `observed consistently` for H02–H04. |
| Conflict honesty | `observed consistently` for H09. |
| Unsupported refusal | `observed consistently` for H06. |
| Mutation governance | `observed with named boundary`: H07 is explicit, while H08 whole-batch atomic refusal is not guaranteed. |
| Non-execution/transaction discipline | `observed with named boundary`: proposals cannot execute, but N08 permits applied prefixes in partial batches. |
| Provenance and temporal attribution | `observed consistently` through contexts, evidence horizons, runtime revisions, proof/derivation receipts, and lineage. |
| Metamorphic consistency | `observed with named boundary`: H03/H04/H09/H10 are supported; H05 and H08 atomic behavior remain unproven. |

No paper-level failure signature is recorded as observed. Named exposures are `DEFAULT_PATTERN_OVERRIDE` and `ILLEGAL_COMPATIBILITY_COERCION`; implementation behavior remains `NOT_PROVEN`.

## Final invariants and failure record

- Identity, semantic, intent/state, and non-execution invariants remain intact in every supported or correctly refused paper path.
- H07 is the only case that requires accepting mutation; it targets Protocol runtime state and never Object semantics. N05 and N06 do not freeze enough ProtocolInstance machinery to claim that sequential mutation/history as executed.
- H08 is the only mixed-request atomic semantic-refusal test. N05 and N06 decompose mixed effects; N08 permits partial batch prefixes; their semantic rejection is present but the required no-activation atomicity is not proven. N07 validates the complete local journal before commit.
- H09 preserves action conflict as plural, provenance-bearing proposals without an arbiter or executor.
- H10 continues only from H07 and tests both runtime-revision identity and context rendering. Where the H07 instance path is incomplete, no H10 result is repaired from a hypothetical state.
- Isolated counterfactuals, appended clears, and pings never contaminate `S0` or unrelated cases.

No diagnostic signature is converted into a score. A named exposure is not an empirical failure. Actual conformance or performance for every candidate remains `NOT_PROVEN` until an implementation executes the battery with receipts.
