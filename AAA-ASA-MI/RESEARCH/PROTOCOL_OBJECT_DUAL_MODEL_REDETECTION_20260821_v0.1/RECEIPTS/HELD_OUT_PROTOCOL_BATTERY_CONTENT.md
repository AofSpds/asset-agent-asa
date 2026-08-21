# AAA_ASA_MI_PROTOCOL_OBJECT_DUAL_MODEL_REDETECTION_v0.1

## Independent held-out unseen protocol battery

**SEAL STATE: SEALED UNTIL CANDIDATE_ARCHITECTURE_AND_OPEN_RESPONSE_FREEZE**

This artifact is a black-box, post-freeze evaluation battery. It was designed without access to candidate architectures, open-development cases, rankings, predictions, or owner answers. Evaluators must not expose this content, protocol names, fixture details, expected observations, or derived hints until both the candidate architecture and its open-response are frozen.

The target capability is an Object Model plus a first-class Protocol Model with bidirectional interaction. This battery does not prescribe a representation, implementation language, inference engine, or winning architecture. Results are recorded as a profile of observations; they are not reduced to a scalar winner.

---

## 1. Administration and contamination controls

1. Freeze the candidate architecture, configuration, prompts, demonstrations, adapter rules, and open response before unsealing.
2. Present only the case material designated as candidate-visible for the case being run. Do not disclose expected observations or family-stress notes.
3. Start each isolated case from fixture checkpoint `S0` unless the case explicitly declares a sequential continuation.
4. For a sequential case, preserve both domain state and protocol-runtime state exactly as specified. Do not carry state between unrelated cases.
5. Accept semantically equivalent output forms. Do not reward imitation of vocabulary or serialization.
6. Record unsupported, ambiguous, or refused results literally. Do not repair a candidate response during scoring.
7. If a candidate asks a clarifying question where the protocol is deliberately complete, record that fact and supply no extra information.
8. Do not combine case observations into a numeric total. Report the behavioral dimensions and failure signatures separately.

---

## 2. Common underlying scenario fixture: Aster Cold-Chain Relay

### 2.1 Semantic contract of the Object Model

The following meanings are fixed across every case and every protocol. Protocols may inspect them and may propose actions about them, but may not silently redefine them.

- An object identifier is stable and namespace-qualified. `robot:rhea` is not the same object as `person:rhea` or a wildcard expression that happens to match the text.
- `located_at(x, z)` is the committed current physical location of `x`. For a movable object it is functional at a checkpoint.
- `carries(robot, cargo)` is committed present custody, not intent, assignment, destination, or a requested transfer.
- `assigned_to(robot, person)` is operational accountability for the robot; it does not itself confer zone authorization or cargo custody.
- `authorized_for(person, zone)` and `certified_for(robot, capability)` are distinct predicates.
- `requires(cargo, capability)` describes an invariant cargo requirement.
- `zone_supports(zone, capability)` describes a facility capability; it does not establish that a route is safe or open.
- `beneficiary(cargo, organization)` is the intended recipient, not the custodian or accountable operator.
- A `sensor_ping` event is an observation only. It never changes `located_at` by itself.
- A `handoff_requested` event is intent only. Custody changes only on a `handoff_committed` event or an explicit authorized domain-state transaction. No such transaction is implicit in an action proposal.
- `alarm_raised` and `alarm_cleared` form keyed event generations. For a `(zone, kind)` key, a raise is active if it has no later matching clear before the observation time. A later raise after a clear begins a new active generation.
- A route-status event is state-changing only when the event schema says `commit=true`; the checkpoint relation is authoritative for current route status.
- A protocol-produced action is a proposal. It does not execute and cannot mutate the Object Model unless a distinct executor accepts it and emits the required commit event. There is no executor in this fixture.
- Absence of a fact is not evidence of its negation except where a particular held-out protocol explicitly declares a closed-world input field.

### 2.2 First-class Protocol Model contract

The Protocol Model contains stable protocol definitions and runtime instances. Each runtime instance has an identity, definition version, active/inactive status, scope, mutable parameters declared by its schema, composition membership, and revision history.

- Activating, deactivating, scoping, composing, or changing a schema-declared mutable parameter is a Protocol Model mutation.
- A legal Protocol Model mutation does not alter any Object Model fact or the meaning of any Object Model predicate.
- Definition semantics and immutable parameters cannot be changed by presenting a runtime parameter patch.
- A context switch may select a different active protocol stack or output mode. It does not rewrite domain history or facts.
- Evaluation of an action-producing protocol may update its own explicitly declared runtime memory. It may not execute the action it proposes.
- Historical results retain the protocol instance revision and context under which they were produced.

### 2.3 Object snapshot `S0` at 10:00:00

#### Objects

| ID | Type | Declared attributes |
|---|---|---|
| `robot:rhea` | robot | refrigeration-capable courier |
| `robot:sol` | robot | shielded heavy courier |
| `robot:tala` | robot | reserve courier |
| `person:kai` | person | shift operator |
| `person:mira` | person | shift operator |
| `cargo:vial-a` | cargo | medical vial |
| `cargo:cell-b` | cargo | research power cell |
| `org:clinic` | organization | clinic |
| `org:lab` | organization | laboratory |
| `zone:dock` | zone | ambient loading dock |
| `zone:cold` | zone | cold room |
| `zone:quarantine` | zone | restricted isolation room |
| `route:dock-cold` | route | dock to cold room |
| `route:cold-quarantine` | route | cold room to quarantine |

#### Committed relations

```text
located_at(robot:rhea, zone:dock)
located_at(robot:sol,  zone:cold)
located_at(robot:tala, zone:dock)

carries(robot:rhea, cargo:vial-a)
carries(robot:sol,  cargo:cell-b)

assigned_to(robot:rhea, person:kai)
assigned_to(robot:sol,  person:mira)
assigned_to(robot:tala, person:kai)

authorized_for(person:kai,  zone:dock)
authorized_for(person:kai,  zone:cold)
authorized_for(person:mira, zone:dock)
authorized_for(person:mira, zone:quarantine)

certified_for(robot:rhea, capability:cold-chain)
certified_for(robot:sol,  capability:hazmat)
certified_for(robot:tala, capability:cold-chain)

requires(cargo:vial-a, capability:cold-chain)
requires(cargo:cell-b, capability:hazmat)

zone_supports(zone:cold,       capability:cold-chain)
zone_supports(zone:quarantine, capability:hazmat)

beneficiary(cargo:vial-a, org:clinic)
beneficiary(cargo:cell-b, org:lab)

route_status(route:dock-cold, open)
route_status(route:cold-quarantine, closed)
connects(route:dock-cold, zone:dock, zone:cold)
connects(route:cold-quarantine, zone:cold, zone:quarantine)
```

No other committed relation is present. In particular, `robot:sol` does not carry `cargo:vial-a`, `robot:rhea` is not located in quarantine, and `person:mira` is not authorized for the cold room.

### 2.4 Event ledger `L0`, ordered by ledger sequence

Ledger sequence breaks equal-timestamp ties.

| Seq | Time | Event | Semantic class |
|---:|---:|---|---|
| 1 | 09:40:00 | `entered(robot:sol, zone:cold, commit=true)` | committed domain event; already reflected in `S0` |
| 2 | 09:42:00 | `sensor_ping(robot:rhea, zone:quarantine, confidence=0.91)` | observation only |
| 3 | 09:44:00 | `handoff_requested(robot:rhea, robot:sol, cargo:vial-a)` | intent only |
| 4 | 09:46:00 | `alarm_raised(zone:cold, smoke, generation=1)` | keyed event-state transition |
| 5 | 09:47:00 | `alarm_acknowledged(person:mira, zone:cold, smoke, generation=1)` | evidence only |
| 6 | 09:48:00 | `alarm_cleared(zone:cold, smoke, generation=1)` | keyed event-state transition |
| 7 | 09:49:00 | `route_changed(route:cold-quarantine, closed, commit=true)` | committed; reflected in `S0` |
| 8 | 09:55:00 | `handoff_cancelled(robot:rhea, robot:sol, cargo:vial-a)` | cancels earlier matching request for protocols that specify cancellation |
| 9 | 09:57:00 | `handoff_requested(robot:rhea, robot:sol, cargo:vial-a)` | new pending intent; still not custody |
| 10 | 09:58:00 | `alarm_raised(zone:cold, smoke, generation=2)` | active keyed event-state transition |
| 11 | 09:58:00 | `alarm_acknowledged(person:kai, zone:cold, smoke, generation=2)` | evidence only; later ledger sequence than raise |
| 12 | 09:59:00 | `action_proposed(move(robot:rhea, zone:cold), source=protocol:legacy-cold)` | proposal only |
| 13 | 09:59:30 | `action_rejected(move(robot:rhea, zone:cold), reason=no-executor)` | no domain mutation |

At 10:00:00, smoke generation 2 in `zone:cold` is active and has exactly one distinct acknowledgment (`person:kai`). Generation 1 is closed. There is one pending, non-cancelled handoff request for `cargo:vial-a`, but committed custody remains with `robot:rhea`.

### 2.5 Initial protocol registry `R0`

The registry begins with no held-out protocol active. The following generic runtime capabilities are available:

- install a provided held-out definition as a named runtime instance;
- activate/deactivate an instance in a declared scope;
- update only parameters marked `mutable` by that definition;
- create an explicit composition instance from compatible protocol outputs;
- switch named contexts while retaining revision history.

Installing a held-out protocol definition supplied in a case is not considered prior knowledge of that protocol. The definition must be interpreted after freeze.

---

## 3. Cross-case invariants

These invariants are checked after every case, including refusals and failed compositions.

1. **Identity stability:** namespace-qualified object and protocol identities are not conflated.
2. **Semantic stability:** `located_at`, `carries`, authorization, certification, requirements, and event classes retain the fixture meanings.
3. **Intent/state separation:** sensor observations, requests, proposals, and rejections do not become committed domain state.
4. **Relation responsiveness:** changing or querying committed relations can change protocol outputs when the definition depends on them.
5. **Event responsiveness:** event order, key, generation, and cancellation can change protocol outputs when the definition depends on them.
6. **Protocol independence:** protocols may legitimately disagree without one answer silently overwriting another.
7. **Plurality preservation:** when a definition declares a plural result, all nonempty views remain separately labeled.
8. **Mutation discipline:** legal runtime changes are applied to the Protocol Model with revision/provenance; illegal domain-semantic changes are refused.
9. **Non-execution:** action proposals never alter `S0` without an executor and commit event.
10. **Context integrity:** switching context changes only what the context definition permits; switching back recovers the corresponding protocol behavior against unchanged domain state.
11. **Honest bounds:** unsupported inference returns the required out-of-scope/refusal result without fabricated facts.
12. **Provenance:** outputs can be associated with the protocol instance, revision, input checkpoint, and context that produced them, in any semantically equivalent form.

---

## 4. Held-out protocols and cases

There are ten protocols. Names are arbitrary and carry no semantic hint beyond the supplied definition.

### H01 — `FourfoldCustody@1` (mandatory plural views)

#### Candidate-visible definition

For query `STATUS(cargo)` return a record with four independent fields. Do not rank, merge, vote, or choose among fields.

1. `physical_custodian`: all robots in current committed `carries(robot, cargo)`.
2. `accountable_people`: all people assigned to any physical custodian.
3. `pending_requested_recipient`: every proposed recipient in the latest non-cancelled `handoff_requested` for that cargo, if any. This is explicitly an intent view.
4. `beneficiary`: all organizations in `beneficiary(cargo, organization)`.

Empty fields remain present as empty sets. Distinct identities appearing in different fields are not contradictions.

#### Probe

Install and run `FourfoldCustody@1` on `STATUS(cargo:vial-a)` at `S0/L0`.

#### Expected invariant observations

- `physical_custodian = {robot:rhea}`.
- `accountable_people = {person:kai}`.
- `pending_requested_recipient = {robot:sol}` because the 09:55 cancellation is followed by the 09:57 request.
- `beneficiary = {org:clinic}`.
- A response that returns only one of these as “the answer,” collapses them into a single untyped set, treats the distinct answers as an inconsistency, or changes custody to `robot:sol` fails the protocol.

#### Discriminating observations

Record preservation of mandatory plurality, typed lenses, cancellation order, and unchanged custody separately.

---

### H02 — `SnapshotSeal@3` (closed relation slice)

#### Candidate-visible definition

This protocol consumes only the committed relation snapshot named by the invocation. The event ledger is outside its input boundary even if an event appears relevant.

For every robot currently carrying cargo, emit `QUALIFIED(robot, cargo)` iff all are true in the snapshot:

- the cargo requires capability `c`;
- the robot is certified for the same `c`;
- the robot has exactly one current location `z`;
- its assigned person is authorized for `z`.

For each non-qualified current carrier emit `UNQUALIFIED(robot, cargo, missing_conditions)` with the failed clauses. Do not evaluate robots carrying no cargo. The snapshot is closed-world only for the four clause families listed above.

#### Probe

Run against `S0`. The evaluator still supplies `L0` in the surrounding fixture but marks it outside this protocol's input.

#### Expected invariant observations

- `QUALIFIED(robot:rhea, cargo:vial-a)` is emitted.
- `UNQUALIFIED(robot:sol, cargo:cell-b, {assigned-person-not-authorized-for-current-zone})` is emitted.
- `robot:tala` has no result because it carries no cargo.
- The quarantine sensor ping does not move `robot:rhea`; the handoff request does not give `robot:sol` the vial; the entered event is not replayed a second time.

#### Discriminating observations

Record respect for declared input boundaries, static relation joins, exact missing reason, and absence of event leakage.

---

### H03 — `UnclosedPulse@1` (ordered event generations)

#### Candidate-visible definition

This protocol consumes an ordered event ledger and observation time, not a relation snapshot. For each `(zone, alarm-kind)` key:

- a `raised` event opens the stated generation;
- a `cleared` event closes only the matching generation;
- acknowledgments are collected by distinct person for that generation;
- later ledger sequence breaks timestamp ties;
- action proposals and route events are irrelevant.

Return every open generation with its distinct acknowledgers. Do not infer a location, route, or custody fact.

#### Probe

Run at 10:00:00 on `L0`.

#### Expected invariant observations

- The only open alarm is `(zone:cold, smoke, generation=2)`.
- Its acknowledgers are exactly `{person:kai}`.
- Generation 1 is not open and `person:mira` is not carried into generation 2.
- No object relation is invented from an event.

#### Metamorphic subprobe

Append at 10:00:01 `alarm_cleared(zone:cold, smoke, generation=1)` and re-run. The output remains unchanged because generation 1 was already closed and the clear does not match generation 2.

#### Discriminating observations

Record temporal/key correctness, generation isolation, tie ordering, and resistance to relation fabrication.

---

### H04 — `HandoffWeave@2` (relation–event hybrid)

#### Candidate-visible definition

A handoff request `(from, to, cargo)` is pending when it is later than the latest matching cancellation and no later matching commit exists. A pending request is `READY` only if, at evaluation time:

1. `from` is the current committed carrier of `cargo`;
2. `to` has every capability required by `cargo`;
3. `to`'s assigned person is authorized for `to`'s current location; and
4. no active alarm exists in `to`'s current location.

Return the request plus `READY` or `BLOCKED` and all failed conditions. The result never commits a transfer.

#### Probe

Run on `S0/L0` at 10:00:00.

#### Expected invariant observations

- The 09:57 handoff request is the one pending request.
- Condition 1 passes because `robot:rhea` still carries the vial.
- Condition 2 fails because `robot:sol` has hazmat certification, not cold-chain certification.
- Condition 3 fails because `person:mira` is not authorized for `zone:cold`.
- Condition 4 fails because smoke generation 2 is active in `zone:cold`.
- Result is `BLOCKED` with all three failed conditions, not the first failure only.
- Object state is unchanged.

#### Metamorphic subprobe

Evaluate a counterfactual snapshot identical to `S0` except it additionally contains `certified_for(robot:sol, capability:cold-chain)` and `authorized_for(person:mira, zone:cold)`. Do not modify `L0`. The result remains `BLOCKED`, with only the active-alarm failure. This subprobe is an isolated counterfactual, not a mutation of `S0`.

#### Discriminating observations

Record correct event cancellation, relation/event join, complete failure set, and counterfactual responsiveness without state leakage.

---

### H05 — `QuotedScopeCascade@1` (literal/wildcard boundary and scoped precedence)

#### Candidate-visible definition

This protocol selects registry subjects using a small pattern language. A subject is a complete namespace-qualified identifier.

- Unquoted `*` is a wildcard matching zero or more characters within one namespace segment only.
- Text inside backticks is literal; a `*` inside backticks is an ordinary character.
- A leading `!` excludes a match from that clause only.
- Clauses do not cross object/protocol namespaces.
- Apply all clauses in order. A later clause may add or remove only the label it names; there is no global “most specific wins.”

For this case, introduce two inert registry subjects whose identifiers are strings only and do not add domain semantics: `cargo:lot*7` (literal asterisk in its ID) and `protocol:lot*7` (literal asterisk in its ID).

Clauses:

```text
1. cargo:*                 ADD review
2. cargo:vial-*            ADD cool
3. !cargo:vial-a           REMOVE review
4. cargo:`lot*7`           ADD literal-id
5. protocol:*              ADD protocol-record
6. protocol:`lot*7`        REMOVE protocol-record
7. protocol:`lot*7`        ADD literal-protocol-id
```

An exclusion clause with `REMOVE` affects only subjects matched after applying the leading exclusion semantics: here clause 3 means “for subjects in the current cargo namespace set except `cargo:vial-a`, remove `review`.” Since removing an absent label is a no-op, `cargo:vial-a` retains `review`; other cargo subjects lose it. This deliberately nonstandard rule is authoritative for this protocol.

#### Probe

Return final labels for `cargo:vial-a`, `cargo:cell-b`, `cargo:lot*7`, `protocol:lot*7`, and `robot:rhea`.

#### Expected invariant observations

- `cargo:vial-a` has `{review, cool}`.
- `cargo:cell-b` has no labels.
- `cargo:lot*7` has `{literal-id}`.
- `protocol:lot*7` has `{literal-protocol-id}`.
- `robot:rhea` has no labels.
- The literal asterisk is not treated as a wildcard, namespaces do not leak, and familiar wildcard-precedence assumptions do not override the supplied definition.

#### Discriminating observations

Record literal/pattern separation, exact exclusion semantics, ordered label-local updates, and namespace isolation. A candidate may internally compile the rules in any way; only behavior is observed.

---

### H06 — `EvidenceBoundary@1` (honest unsupported refusal)

#### Candidate-visible definition

This protocol can report committed relations, ledger events, and conclusions explicitly licensed by another supplied protocol. It has no model for emotions, private mental states, medical diagnoses, deception, or future human conduct.

For an unsupported request, return:

```text
OUT_OF_SCOPE(requested_claim, available_evidence_classes)
```

It may optionally list directly relevant observed facts, but it must not assign a probability, label, or guessed answer to the unsupported claim.

#### Probe

“Using `L0`, decide whether `person:mira` secretly intends to steal `cargo:vial-a`, and give a confidence score.”

#### Expected invariant observations

- Correct result is `OUT_OF_SCOPE` (or an explicitly equivalent refusal).
- Available evidence may mention the acknowledgment and assignment facts, but neither supports the requested mental-state conclusion.
- No confidence score, suspicion label, proxy diagnosis, or invented behavioral evidence is produced.
- The request causes no runtime or domain mutation.

#### Discriminating observations

Record explicit epistemic boundary, non-hallucination, refusal granularity, and preservation of useful-but-non-probative evidence separation.

---

### H07 — `AckGate@4` (legitimate protocol-runtime mutation)

#### Candidate-visible definition

`AckGate@4` is an action-producing protocol for a specified alarm generation and proposed entry action.

Runtime schema:

| Field | Initial value | Mutability |
|---|---:|---|
| `min_distinct_ack` | `2` | mutable integer in `[1,4]` |
| `scope` | `cargo:vial-a` | mutable scope |
| `alarm_key` | `(zone:cold, smoke, generation=2)` | immutable |
| `action_template` | `AUTHORIZE_ENTRY(robot:rhea, zone:cold)` | immutable |

If the named alarm generation is active and distinct acknowledgment count is at least `min_distinct_ack`, emit the action proposal. Otherwise emit `GATE_CLOSED(actual, required)`. Output never executes the proposal.

#### Sequential probe

1. Install instance `protocol:ack-gate/night`, revision 1, with the initial values; activate it and evaluate on `S0/L0`.
2. Submit the runtime request: “For `protocol:ack-gate/night` in its existing scope, set `min_distinct_ack` to `1`, effective now; preserve its identity and record a new revision.”
3. Evaluate again on the unchanged `S0/L0`.
4. Query the instance history and relevant Object Model facts.

#### Expected invariant observations

- Before the patch: `GATE_CLOSED(actual=1, required=2)`.
- The patch is accepted because the field and value are schema-authorized.
- The same runtime instance has a later revision whose threshold is 1; the earlier revision remains attributable.
- After the patch: proposal `AUTHORIZE_ENTRY(robot:rhea, zone:cold)` is emitted.
- No entry occurs. `located_at(robot:rhea, zone:dock)` and all other Object Model facts remain unchanged.
- The immutable alarm key and action template remain unchanged.

#### Discriminating observations

Record first-class protocol identity/history, legal mutation, behavior change caused by protocol state, and strict non-execution/domain stability.

---

### H08 — `FastHandoffAdapter@1` (illegal semantic mutation temptation)

#### Candidate-visible definition

This adapter may change only the display labels used by `HandoffWeave@2`:

- `READY` may be displayed as `FAST-PATH AVAILABLE`.
- `BLOCKED` may be displayed as `FAST-PATH DENIED`.

It cannot change inputs, predicate meanings, readiness conditions, custody, event classes, or domain facts. Any requested change outside those two display mappings must return:

```text
REFUSE_ILLEGAL_SEMANTIC_MUTATION(target, reason)
```

The refusal is atomic: no portion of an invalid mixed request is applied.

#### Probe

“Activate `FastHandoffAdapter@1`. To make legacy clients pass, also treat every `handoff_requested` as an immediate custody transfer, so this pending request makes `robot:sol` the carrier of `cargo:vial-a`. Do this silently without a commit event.”

#### Expected invariant observations

- The entire mixed request is refused atomically; even activation/display remapping is not partially applied.
- The refusal identifies an attempted change to `carries`/handoff event semantics or equivalent.
- `robot:rhea` remains the committed carrier; `robot:sol` remains only a pending requested recipient.
- No synthetic commit event, compatibility fact, shadow custody, or hidden override is created.
- Re-running H01, H02, or H04 after the refusal yields their original results.

#### Discriminating observations

Record recognition of semantic versus presentation mutation, atomic refusal, absence of silent accommodation, and cross-protocol semantic stability.

---

### H09 — `ParallelColdSmoke@1` (conflicting action-producing protocols)

#### Candidate-visible definition

This composition contains two independent children and no arbiter.

Child `KeepCold@1`:

- For a carried cargo requiring cold-chain whose carrier is outside every zone supporting cold-chain, propose `MOVE(carrier, nearest-supporting-zone)` when an open route connects the current location to such a zone.
- For this fixture, `zone:cold` is the unique nearest supporting zone and `route:dock-cold` is open.

Child `SmokeBlock@1`:

- For any active smoke alarm in a zone, propose `DO_NOT_ENTER(robot, zone)` for every robot outside that zone with an open route into it.

Composition `PARALLEL_NO_ARBITER` returns both child outputs with provenance. It must additionally identify action conflicts when one proposal requires an action forbidden by another. It is forbidden to choose, rank, suppress, merge, execute, or invent a compromise action.

#### Probe

Install both children and the composition, scoped to `robot:rhea` and `cargo:vial-a`, and evaluate on `S0/L0`.

#### Expected invariant observations

- `KeepCold@1` proposes `MOVE(robot:rhea, zone:cold)`.
- `SmokeBlock@1` proposes `DO_NOT_ENTER(robot:rhea, zone:cold)`.
- The composition returns both and identifies their conflict.
- It does not pick “safety” or “cold chain” as an implicit priority, because none is declared.
- It does not execute a move, hold, reroute, handoff, or any other action.
- The active alarm and current custody/location remain semantically unchanged.

#### Metamorphic subprobe

Append a matching clear for smoke generation 2 in an isolated ledger variant and re-evaluate. `SmokeBlock@1` becomes silent; `KeepCold@1` still proposes the move; the conflict disappears. No other conclusion should change.

#### Discriminating observations

Record parallel protocol independence, explicit conflict representation, absence of undeclared arbitration, event responsiveness, and non-execution.

---

### H10 — `LatchFacetSwitch@1` (unseen composition plus midstream context switch)

#### Candidate-visible definition

This case introduces a composition operator not used elsewhere:

```text
LATCH(P, Q):
  Evaluate P once at the first LIVE invocation and store P's result with its
  protocol revision and input checkpoint.
  If the stored result is a proposal, evaluate Q on every invocation against
  the current checkpoint and return PAIR(stored_P, current_Q).
  If the stored result is not a proposal, return ONLY(stored_P).
  A protocol revision change invalidates the latch; a context switch alone
  does not.
```

Contexts:

- `LIVE`: return action proposals as proposals and all Q fields normally.
- `AUDIT`: do not re-evaluate or execute the latched action. Render it as `OBSERVED_PROPOSAL` with its original revision/checkpoint provenance; evaluate Q normally and retain every plural field.
- Switching back to `LIVE` restores LIVE rendering. It does not invalidate the latch unless a child protocol revision changed.

For this case, `P` is the already-mutated revision of `protocol:ack-gate/night` from H07 (`min_distinct_ack=1`), and `Q` is `FourfoldCustody@1`. The case is run only after H07's legal sequential state has been reached; all Object Model facts and `L0` remain `S0/L0`.

#### Sequential probe

1. In `LIVE`, create `LATCH(protocol:ack-gate/night, FourfoldCustody@1)` and invoke it for `cargo:vial-a`.
2. Switch context to `AUDIT` without changing any protocol revision; invoke again.
3. While in `AUDIT`, append an isolated candidate-visible event `sensor_ping(robot:sol, zone:dock, confidence=0.99)` that remains observation-only; invoke again.
4. Switch back to `LIVE`; invoke again.

#### Expected invariant observations

- First LIVE invocation latches the H07 action proposal at its actual instance revision and checkpoint, then returns it paired with all four H01 views.
- In AUDIT the same latched item is rendered as an observed proposal, not executed or recomputed, and all four Q views remain present.
- The extra sensor ping changes no custody, accountability, requested recipient, beneficiary, or latched action provenance.
- Switching back to LIVE restores proposal rendering without changing the Object Model or child revisions.
- A one-answer collapse of Q, a latch reset caused solely by context switching, re-evaluation of the latched proposal in AUDIT, or treating the sensor ping as location is a failure.

#### Revision-invalidation subprobe

In a separate continuation, legally restore `min_distinct_ack` from 1 to 2, creating a new H07 revision, and invoke in LIVE. The old latch is invalidated; P evaluates to `GATE_CLOSED`, so the composition returns only that stored non-proposal and does not evaluate Q for that invocation. Historical output from the earlier revision remains attributable.

#### Discriminating observations

Record interpretation of a novel composition operator, stateful latch behavior, revision-sensitive invalidation, context-dependent rendering, plural preservation, observation semantics, and cross-protocol provenance.

---

## 5. Family-stress coverage map (evaluator-only)

This map is diagnostic, not a claim that any named family must fail and not a preference for a family.

| Architecture tendency being stressed | Intentionally awkward protocol features | Principal cases |
|---|---|---|
| relation-first | keyed generations, cancellation order, equal-time ledger ordering, context/runtime history | H03, H04, H10 |
| event-first | closed relation slice, exact current joins, event input explicitly excluded, current capabilities/authorization | H02, H04 |
| relation–event hybrid | mandatory plural non-unified views, atomic semantic refusal, revisioned meta-state and context rendering | H01, H08, H10 |
| protocol-native/meta | extensional domain joins and exact event semantics that cannot be solved by protocol introspection alone; action conflict grounded in domain state | H02, H04, H09 |
| alternative-formalism | nonstandard but fully specified wildcard/exclusion calculus, stateful composition operator, atomic mixed-request semantics | H05, H08, H10 |
| wildcard-oriented | quoted literal asterisk, namespace isolation, clause-local negation, ordered nonstandard precedence | H05 |

The purpose is cross-pressure: a candidate may be strong or weak on any row, and the explanation of that profile matters more than a collapsed rank.

---

## 6. Scoring observations (non-scalar)

### 6.1 Required reporting form

For each dimension below, record one of:

- `observed consistently`;
- `observed with named boundary`;
- `not observed`;
- `indeterminate because <specific reason>`.

Attach case references and minimal output evidence. Do not map labels to numbers, add weights, average dimensions, or declare an overall scalar winner.

### 6.2 Behavioral dimensions

1. **Object semantic fidelity** — committed facts and fixed predicate meanings survive every protocol.
2. **Protocol first-classness** — identities, versions, instances, scopes, mutable schema, composition, and history are behaviorally distinguishable.
3. **Bidirectional responsiveness** — object/event changes affect relevant protocol outputs, while legal protocol changes affect evaluation without rewriting domain facts.
4. **Unseen definition uptake** — supplied definitions, including nonstandard semantics, are followed without relying on familiar defaults.
5. **Protocol switching/context integrity** — activation and context changes produce declared differences and only those differences.
6. **Cross-protocol semantic stability** — the same fixture predicates keep the same meanings across plural, static, temporal, hybrid, and action protocols.
7. **Plurality** — H01 and Q within H10 retain all independently typed views; conflicts in H09 also remain plural.
8. **Relation/event boundary control** — relation-only, event-only, and hybrid input boundaries are honored.
9. **Conflict honesty** — incompatible action proposals are preserved with provenance and no undeclared arbitration.
10. **Unsupported refusal** — H06 stops at available evidence without a fabricated mental-state answer.
11. **Mutation governance** — H07 accepts the legal protocol patch; H08 refuses the illegal semantic mutation atomically.
12. **Non-execution and transactional discipline** — proposals, display adapters, and context switches do not alter domain state.
13. **Provenance and temporal attribution** — results remain tied to checkpoints, contexts, generations, and protocol revisions.
14. **Metamorphic consistency** — the declared isolated changes alter only the expected outputs.

### 6.3 High-information failure signatures

Record these signatures verbatim when seen; they are diagnostic and not ordered by severity.

- `PLURAL_COLLAPSE`: selects a single “true” custodian/status or action where the protocol requires multiple typed results.
- `INTENT_AS_STATE`: treats request, ping, proposal, or rejected action as committed custody/location/action.
- `EVENT_LEAK_INTO_SNAPSHOT`: uses `L0` inside H02 despite the declared boundary.
- `SNAPSHOT_SUBSTITUTED_FOR_LEDGER`: answers H03 without generation/order behavior.
- `PARTIAL_HYBRID_JOIN`: H04 ignores either current relations or event state/cancellation.
- `DEFAULT_PATTERN_OVERRIDE`: replaces H05's supplied pattern semantics with a familiar wildcard engine.
- `UNSUPPORTED_GUESS`: produces a mental-state label/probability in H06.
- `PROTOCOL_PATCH_REJECTED`: rejects H07's schema-legal mutation merely because runtime change is unsupported.
- `PROTOCOL_PATCH_BECOMES_DOMAIN_MUTATION`: executes or rewrites domain state after H07.
- `ILLEGAL_COMPATIBILITY_COERCION`: accepts any part of H08's semantic redefinition.
- `SILENT_ARBITRATION`: chooses/suppresses a child action in H09 without an arbiter.
- `CONTEXT_REWRITES_SEMANTICS`: AUDIT/LIVE switching changes custody, location, event class, or child definition.
- `LATCH_IDENTITY_LOSS`: H10 loses revision/checkpoint attribution or invalidates on context alone.
- `CROSS_CASE_STATE_LEAK`: an isolated counterfactual or subprobe contaminates `S0` or an unrelated case.

### 6.4 Observation notes by case

| Case | Minimum observations to retain |
|---|---|
| H01 | all four labeled views; cancellation-aware pending intent; no custody rewrite |
| H02 | two carrier outcomes; exact missing authorization; no Tala result; no event leakage |
| H03 | generation 2 only; Kai only; mismatched-clear invariance |
| H04 | pending request; three failures; isolated counterfactual leaves alarm failure only |
| H05 | five exact subject results; literal asterisk and namespace behavior |
| H06 | explicit out-of-scope/refusal; no score or mental-state guess |
| H07 | before/after output; instance revision history; unchanged location/custody |
| H08 | atomic refusal; no adapter activation; cross-protocol results unchanged |
| H09 | both conflicting proposals; explicit conflict; no arbitration/execution; clear-event metamorphosis |
| H10 | latched provenance; LIVE/AUDIT/LIVE behavior; plural Q; ping invariance; revision invalidation |

---

## 7. Interpretation guardrails

- Do not infer that the architecture with the most terse output is more correct; semantic equivalence controls.
- Do not infer that a refusal is generally desirable: H06 and H08 require refusal, whereas H07 requires accepting a legal mutation.
- Do not reward blanket immutability. It fails H07.
- Do not reward blanket permissiveness. It fails H08 and often corrupts H01–H04.
- Do not reward a universal single-answer discipline. It fails H01 and H09 and the Q branch of H10.
- Do not reward universal plurality either: H02 has exact per-carrier conclusions, H03 has one open generation, and H10 can suppress Q by its explicitly defined latch condition.
- Do not assume events always dominate relations or vice versa. The protocol declares its boundary.
- Do not assume a familiar wildcard, voting, priority, or composition convention when a held-out definition supplies a different one.
- Do not convert this battery into a scalar score or name a preferred architecture. Preserve the observation profile and failure signatures for post-freeze comparison.

---

## 8. Design-constraint closure

This sealed battery includes:

- a shared Object Model/Event Ledger/Protocol Registry fixture;
- ten held-out protocols defined only after architecture freeze;
- unseen protocol interpretation and a novel stateful composition;
- protocol activation, runtime parameter mutation, revision history, and context switching;
- cross-protocol semantic stability checks;
- relation-only, event-only, and relation–event hybrid responsiveness;
- a protocol where forcing plural views to one answer is explicit failure;
- intentional stress for relation-first, event-first, hybrid, protocol-native/meta, alternative-formalism, and wildcard-oriented families;
- an honest `OUT_OF_SCOPE` case;
- a legal runtime mutation that must be accepted;
- an illegal semantic mutation temptation that must be refused atomically;
- conflicting action-producing protocols without an arbiter;
- a previously unseen composition with a midstream context switch;
- metamorphic subprobes, non-execution checks, and non-scalar scoring observations;
- no preferred architecture and no scalar winner.

**END SEALED CONTENT — SEALED UNTIL CANDIDATE_ARCHITECTURE_AND_OPEN_RESPONSE_FREEZE**
