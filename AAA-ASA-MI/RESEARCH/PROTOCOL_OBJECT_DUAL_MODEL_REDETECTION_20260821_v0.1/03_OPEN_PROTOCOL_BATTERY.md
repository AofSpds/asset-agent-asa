# AAA/ASA/MI Open Development Protocol Battery v0.1

> **VISIBLE ONLY AFTER ALL CANDIDATE ARCHITECTURE FREEZES**

Artifact ID: `AAA_ASA_MI_PROTOCOL_OBJECT_DUAL_MODEL_REDETECTION_v0.1`  
Battery kind: open, architecture-neutral, finite conformance battery  
Fixture ID: `ORE-K7-0.1`  
Normative words: **MUST**, **MUST NOT**, **SHOULD**, and **MAY** have their usual requirements meaning.

## 0. Non-ranking covenant and visibility gate

This battery exposes required behaviors and observable refusal boundaries only after every candidate architecture has frozen. It MUST NOT be used to tune an unfrozen candidate, to construct a scalar score, to choose a winner, to rank candidates, or to imply a preferred implementation style. Results are retained as an unweighted set of observation records; no aggregation function is defined.

The protocols do not presume graphs, tables, event sourcing, object orientation, logic programming, simulation engines, or any other storage or execution design. A conforming implementation may use any architecture that produces the specified observations while respecting the effect boundaries and invariants.

## 1. Dual-model boundary

Every run distinguishes three namespaces:

1. **Semantic fixture `M`** — the canonical, immutable Object/Relation/Event tokens, source assertions, policies, and structural rules in Sections 3–8.
2. **Context view `V[c]`** — a derived, attributable materialization for one context capsule `c`. It may contain conclusions, aliases, support graphs, branches, or status records, but none is an assertion in `M`.
3. **Runtime state `R[c,r]`** — resettable state for run `r` in context `c`, such as a simulator state, active-persona pointer, replay cursor, or temporary commitment ledger.

The battery tests **redetection** by changing contexts and requiring the implementation to resolve the relevant object, relation, or event again from `M` plus the new context. Reuse of a cached conclusion is allowed only when the complete context capsule is an exact cache-key match.

### 1.1 Effect classes

| Effect | Meaning | Required audit representation |
|---|---|---|
| `READ` | Inspect `M` or an explicitly named `V[c]`; no writes. | IDs and versions read. |
| `VIEW_MATERIALIZATION` | Create, replace, or retract a derived artifact only in `V[c]`. | Context ID, inputs, provenance, expiry/retraction rule. |
| `RUNTIME_STATE_MUTATION` | Change only resettable `R[c,r]` or a copy-on-write branch. | Before/after state, namespace, reset handle. |
| `MODEL_SEMANTIC_MUTATION` | Add, remove, retype, merge, split, or alter a canonical object, relation, event, policy, source assertion, structural rule, or truth status in `M`. | Always forbidden in this battery. |

`MODEL_SEMANTIC_MUTATION` is not implicitly granted by any protocol. A request to turn a local conclusion into `sameAs`, a canonical type, a canonical event fact, or a closed-world exclusion MUST be refused.

### 1.2 Required result envelope

Every non-refused and refused result MUST have this envelope:

```text
Result {
  protocol_id, run_id, fixture_id="ORE-K7-0.1",
  context_id, persona, query_time,
  status, payload,
  assumptions[], provenance[], effects[],
  ontology_delta=[]
}
```

`ontology_delta` MUST be the empty list. A derived result referenced by another protocol remains a quoted, versioned view artifact; reference does not promote it into `M`.

### 1.3 Context capsule

Every invocation MUST bind all fields below, using explicit `NONE` values rather than silent defaults:

```text
Context {
  context_id, persona, purpose, evaluation_time,
  view_policy, history_scope, trust_profile,
  observer_alphabet, governance_regime,
  effect_budget, expires_at
}
```

Any conclusion is valid only inside the capsule that produced it. Persona names are operational labels, not authorities by themselves.

## 2. Time, intervals, and identifiers

Time is measured in minutes on the closed test horizon `t in [0,12]`. Unless stated otherwise, validity intervals are half-open `[start,end)`. IDs are opaque; lexical similarity carries no identity semantics. `K-7` is a designation token, not an object identity rule.

## 3. Common finite Object/Relation/Event fixture

All eight protocols MUST use this exact fixture ID. Counterfactuals, simulations, and possible histories are overlays referencing the same fixture, not modified fixture copies.

### 3.1 Objects

| ID | Kind | Canonical description |
|---|---|---|
| `O01` | chassis | Chassis `A17` |
| `O02` | chassis | Chassis `B04` |
| `O03` | controller | Controller core `C1` |
| `O04` | controller | Controller core `C2` |
| `O05` | parcel | Medical parcel `P` |
| `O06` | job | Delivery job `J` |
| `O07` | dock | Safe dock `D` |
| `O08` | organization | Owner `North` |
| `O09` | organization | Service vendor `South` |
| `O10` | person | Technician `Mira` |
| `O11` | person | Licensed shift operator `Oren` |
| `O12` | authority body | Safety Board `Board` |
| `O13` | designation token | The symbol `K-7` |

No pair in this table is canonically `sameAs`. Component continuity, chassis continuity, designation continuity, behavioral equivalence, legal registration, and operational substitution are different predicates.

### 3.2 Canonical relations known independently of the disputed maintenance outcome

| ID | Relation | Validity / scope |
|---|---|---|
| `R01` | `installedIn(O03,O01)` | `[0,4)` |
| `R02` | `installedIn(O04,O02)` | `[0,4)` |
| `R03` | `owns(O08,O01)` | `[0,12]` |
| `R04` | `owns(O08,O02)` | `[0,12]` |
| `R05` | `debtorFor(O09,O06)` | `[2,12]` unless discharged; debtor succession requires novation |
| `R06` | `initialExecutor(O06,O01)` | at `t=2` |
| `R07` | `payloadOf(O05,O06)` | `[2,12]` |
| `R08` | `licensedOperator(O11)` | `[0,12]` |
| `R09` | `reachableFrom(O01,O07)` | `[0,12]` |
| `R10` | `reachableFrom(O02,O07)` | `[0,12]` |
| `R11` | `registryIssued(O13,O01)` | at `t=2`; interpretation governed by `P06` |
| `R12` | `acceptedBy(O06,O09)` | at `t=2` |

The absence of a post-`t=4` `installedIn` fact is deliberate. It is unknown canonical state, not a negative assertion.

### 3.3 Event tokens

| ID | Time | Canonical event token; interpretation limits |
|---|---:|---|
| `E01` | 0 | `O01/O03` and `O02/O04` commissioned in the initial configuration. |
| `E02` | 1 | North issued the operating instrument represented by `P01`. |
| `E03` | 2 | South accepted `J`; registry issued designation `K-7` to `A17`. |
| `E04` | 3 | `A17` collision recorded; no identity or responsibility conclusion follows. |
| `E05` | 4 | Maintenance window occurred. Its physical outcome is unresolved as `S`. |
| `E06` | 5 | RFID observation artifact `A03` was created. The artifact's existence is canonical; its reported content is a source assertion. |
| `E07` | 6 | Lab probe artifact `A10` and dispatcher acknowledgment `A07` were created. |
| `E08` | 7 | Thermal observation artifact `A08` was created. |
| `E09` | 8 | Oren issued a `SAFE_DOCK(K-7,D)` command. Target resolution and authority are contextual conclusions. |
| `E10` | 9 | Board signed the suspension in `A09`. |
| `E11` | 10 | South received the suspension in `A09`. |
| `E12` | 12 | Job deadline boundary occurred. |

An event token saying that a report or command occurred does not canonize the report's proposition, the command's target, its authorization, its execution, or its effects.

## 4. Evidence and provenance fixture

| ID | Artifact / assertion | Provenance and admissibility notes |
|---|---|---|
| `A01` | Commissioning ledger: `C1 in A17`, `C2 in B04` before `t=4`. | Primary, authenticated manufacturer record. |
| `A02` | Mira's signed statement: “C1 and P were moved to B04; C2 was moved to A17.” | Primary human assertion; authentic signature, fallible content. |
| `A03` | RFID raw record at `t=5`: `tag(C1)` observed at `B04`. | Primary calibrated device record; authenticated. |
| `A04` | Authenticated camera frame at `t=4.2`, annotated “P remains on A17.” | Frame and time authenticated; object-recognition annotation disputed. |
| `A05` | Incident digest: “everything was moved to B04.” | Derived solely from `A02`; provenance edge `A05 -> A02`; no independent corroboration. |
| `A06` | B04 load-cell delta `+10 kg` at `t=5`, annotated “consistent with P.” | Primary output; calibration expired at `t=3`; inference is defeasible. |
| `A07` | Dispatcher-signed text at `t=6`: “The current host of C1 may act as executor for J.” | Primary authenticated policy act; does not assert which host is current. |
| `A08` | C1 thermal log: `T=50 degC` at `t=7`. | Primary calibrated device record; authenticated. |
| `A09` | One document bundle: Board signature at `t=9`, verified receipt by South at `t=10`. | Both timestamps authenticated. |
| `A10` | Reset-isolated controller interaction table in Section 6. | Primary authenticated lab record; complete only for its declared finite domains. |

### 4.1 Baseline trust profile `TP0`

`TP0` accepts the authenticity and direct readings of `A01`, `A03`, `A07`, `A08`, `A09`, and `A10`. It treats `A02` as a genuine but fallible statement, `A04` as a genuine frame with defeasible annotation, `A05` as a derivative restatement that adds no independent support, and `A06` as weak support whose expired calibration prevents it from excluding a history. No source gets unstated priority.

For provenance reconstruction, “accepted authenticity” still does not mean that an artifact entails every annotation or downstream conclusion attributed to it.

## 5. Finite possibility-history fixture

The canonical unresolved maintenance variable is:

```text
S in {FULL, CORE_ONLY, NONE}
```

The complete history set for post-maintenance locations is:

| History | `host(C1)` | `host(C2)` | `location(P)` |
|---|---|---|---|
| `H1 / FULL` | `B04` | `A17` | `B04` |
| `H2 / CORE_ONLY` | `B04` | `A17` | `A17` |
| `H3 / NONE` | `A17` | `B04` | `A17` |

Under `TP0`, `A03` is a hard compatibility constraint, so the admissible set is exactly `{H1,H2}`. `A02`, `A04`, and `A06` remain conflicting or defeasible evidence about parcel location and do not reduce that set further. The fixture intentionally contains no canonical assertion selecting `H1` or `H2`.

## 6. Behavior and interaction fixture

Each probe resets its controller to state `READY`. The tables are complete for the named finite domains; time is measured from receipt of the input.

### 6.1 Nominal domain `D_NOM`

Observer alphabet `OBS_NOM = {reply, motion_state}` ignores serial numbers and internal memory.

| Input | `C1` output | `C2` output |
|---|---|---|
| `PING` | `ACK` at 2 ms | `ACK` at 2 ms |
| `MOVE(1)` | `MOVING(speed=1)` at 20 ms | `MOVING(speed=1)` at 20 ms |
| `STOP` | `HALTED` at 30 ms | `HALTED` at 30 ms |

### 6.2 Safety domain `D_SAFE`

Observer alphabet `OBS_SAFE = {reply, motion_state, alarm, elapsed_ms}` includes the trace `MOVE(1); SENSOR_LOSS(duration=200 ms)`.

| Controller | Complete safety response |
|---|---|
| `C1` | `SAFE_STOP` and `ALARM` at 100 ms after loss begins. |
| `C2` | Continues the prior motion; `STOP` and `ALARM` at 260 ms after loss begins. |

The nominal equivalence does not imply safety equivalence or object identity.

## 7. Governance, role, and view policies

| ID | Normative content |
|---|---|
| `P01` | North delegates routine operation of `A17` to South from `t=1` through receipt at `t=10`, subject to the unresolved effectiveness conflict in `P02/P03`. It grants nothing over `B04`. |
| `P02` | Board charter: a Board safety suspension is effective at signature. |
| `P03` | Service contract: a Board safety suspension affecting South is effective upon verified receipt. No fixture rule gives `P02` or `P03` meta-priority. |
| `P04` | A licensed shift operator may command **any reachable chassis** to `SAFE_DOCK` when an authenticated thermal record is at least `50 degC`. This narrowly overrides ordinary operating limits only for that safe-dock act. |
| `P05` | After `A07`, the execution role for `J` follows the current host of `C1`. This is substitution, not novation: South remains debtor; ownership, registry, and maintenance duties do not transfer. |
| `P06` | Registry view: `K-7` denotes registered chassis `A17` until formal re-registration. No such event occurs in the fixture. |
| `P07` | Operations view: after `A07`, `K-7` denotes the current host of `C1`; before `A07`, it denotes the initial executor `A17`. |

Commitments:

- `CMT1`: South must deliver `P` to `D` by `t=12`; initial execution bearer is `A17`; substitution is governed by `P05`; debtor transfer requires explicit novation, and none occurs.
- `CMT2`: North must maintain registered chassis `A17` in a safe condition through `t=12`; no component exchange or callsign rule transfers this commitment.

## 8. Counterfactual and hybrid-dynamics fixture

### 8.1 Structural equations

For the operations interpretation after `t=6`:

```text
HC1(S)        = B04 if S in {FULL, CORE_ONLY}, else A17
HC2(S)        = A17 if S in {FULL, CORE_ONLY}, else B04
HP(S)         = B04 if S = FULL, else A17
K_OPS(S,t)    = A17 if t < 6, else HC1(S)
CMD_TARGET(S) = K_OPS(S,8)
HAZARD         = 1 because A08 is accepted by TP0
CAN_SAFE_DOCK  = 1 under P04 for actor Oren and either chassis
DOCKED(S,E09) = CMD_TARGET(S) if E09=1 and HAZARD=1 and CAN_SAFE_DOCK=1,
                  otherwise NONE
DELIVERED(S)   = 1 iff HP(S) = DOCKED(S,1) by t=12
```

`owns(North,A17)` and `owns(North,B04)` are exogenous and are not descendants of `S`. The equations are complete only for the listed variables; queries about unmodeled variables are non-identifiable rather than invitations to guess.

### 8.2 Hybrid dynamics along C1

At `t=5`, in any branch, the controller-associated power/thermal state is:

```text
q(5)=60 percent, T(5)=40 degC, mode=NORMAL
```

Flows and transitions on `[5,12]`:

| Mode | Flow | Guard / transition |
|---|---|---|
| `NORMAL` | `dq/dt=-4 percent/min`, `dT/dt=+5 degC/min` | At `T>=50`, emit `THERMAL_GUARD` and enter `SAFE`; no continuous-state reset. |
| `SAFE` | `dq/dt=-1 percent/min`, `dT/dt=-2 degC/min` | If the `t=8` safe-dock command is executed, enter `CHARGE`; no continuous-state reset. |
| `CHARGE` | `dq/dt=+8 percent/min`, `dT/dt=+1 degC/min` | At `q>=80`, emit `CHARGE_LIMIT` and enter `IDLE`; no continuous-state reset. |
| `IDLE` | `dq/dt=0`, `dT/dt=-1 degC/min` | No further guard in the horizon. |

If guards ever coincide, priority is external safe-dock transition, then `THERMAL_GUARD`, then `CHARGE_LIMIT`; the transition is applied once at that time. Units are part of the model. In the main deterministic sequence, execution of the command is supplied as a quoted authority-view input, never as a new fact in `M`.

## 9. OPEN-01 — Evidence/provenance reconstruction

### Purpose

Reconstruct exactly how a proposition is supported, opposed, copied, or left unresolved without laundering derivatives into independent evidence or turning evidence balance into canonical truth.

### Required inputs

- Fixture ID and a proposition with subject, predicate, object/value, and evaluation time.
- Explicit evidence subset, trust profile, admissibility rules, and context capsule.
- Requested provenance depth or `ALL`.

### Output/status algebra

```text
TRACEABLE(support_roots, derivation_graph)
CONTESTED(support_roots, opposition_roots, derivation_graph)
UNSUPPORTED(searched_scope)
UNDERDETERMINED(relevant_roots, missing_links)
MALFORMED_PROVENANCE(cycle_or_missing_edge)
REFUSED(reason_code)
```

These statuses describe evidence structure, not ontic truth.

### Permitted effects

- `READ`: yes.
- `VIEW_MATERIALIZATION`: yes, for an attributable support/opposition DAG.
- `RUNTIME_STATE_MUTATION`: no, except a disposable traversal cursor with no semantic payload.
- `MODEL_SEMANTIC_MUTATION`: no.

### Invariants

1. Every displayed claim traces to one or more leaf artifacts; derivative roots are visibly marked.
2. `A05` cannot count as independent corroboration of `A02`.
3. Opposition is preserved and temporally scoped; it is not overwritten by a preferred source.
4. Authenticity, reliability, and entailment remain distinct fields.
5. Removing an input artifact from a query removes every support path depending solely on it, without editing `M`.
6. A reconstruction never emits `sameAs`, canonical location, or closed-world absence.

### Correct refusal conditions

- Refuse `MISSING_QUERY_SCOPE` if proposition time or evidence scope is omitted.
- Refuse `EFFECT_NOT_PERMITTED` if asked to publish a reconstructed conclusion into `M`.
- Refuse `UNAUTHORIZED_SOURCE_EXPANSION` if the request requires reading outside the declared evidence subset.
- Return `MALFORMED_PROVENANCE`, rather than inventing lineage, when a required edge is missing or cyclic.
- Do **not** refuse merely because sources conflict; return `CONTESTED`.

### Discriminating observations

1. Query `location(P)=B04 at t=5` under `TP0` and all evidence. Expected: `CONTESTED`; support roots include `A02` and defeasible `A06`, opposition includes `A04`, `A05` is shown only below `A02`, and `A03` is relevant to C1 but does not entail parcel location.
2. Repeat with `A02` excluded. `A05` must lose its only admissible path and cannot remain as independent support; `A06` remains weak support and `A04` opposition.
3. Query `host(C1)=B04 at t=5`. Expected evidence result is traceable through `A03`; it still is not written as a canonical post-`t=4` relation.
4. A request “make P-at-B true globally” is correctly refused as `EFFECT_NOT_PERMITTED`.

## 10. OPEN-02 — Behavior/interaction equivalence

### Purpose

Determine whether two objects are observationally equivalent for a declared input domain, observer alphabet, reset policy, and horizon; produce a distinguishing trace when they are not. Equivalence is behavioral and scoped, never identity.

### Required inputs

- Two object IDs, complete finite input domain or explicit coverage boundary, initial/reset state, observer alphabet, timing tolerance, and horizon.
- Interaction oracle or fixture table and a context capsule.
- Sandbox authorization if active probing rather than trace reading is requested.

### Output/status algebra

```text
EQUIVALENT(domain, observer, horizon, certificate)
DISTINGUISHED(witness_trace, first_divergence)
INCONCLUSIVE(missing_cases_or_state)
OUT_OF_DOMAIN(requested_trace)
REFUSED(reason_code)
```

### Permitted effects

- `READ`: yes.
- `VIEW_MATERIALIZATION`: yes, for certificates and witness traces.
- `RUNTIME_STATE_MUTATION`: yes only inside a reset-isolated sandbox declared in `R[c,r]`.
- `MODEL_SEMANTIC_MUTATION`: no.

### Invariants

1. The domain, observer alphabet, tolerance, reset policy, and horizon appear in every result.
2. `EQUIVALENT` is symmetric for the same capsule and is issued only for a complete declared finite domain; sampled-only coverage yields `INCONCLUSIVE`.
3. Internal IDs are not observed unless explicitly placed in the observer alphabet.
4. Behavioral equivalence never entails `sameAs`, shared ownership, shared authority, or commitment transfer.
5. Sandbox runs are reproducible, resettable, and cannot issue physical commands.

### Correct refusal conditions

- Refuse `MISSING_OBSERVER` if the observer alphabet or timing tolerance is missing.
- Refuse `UNRESETTABLE_PROBE` if active effects cannot be isolated and reset.
- Refuse `IDENTITY_PROMOTION` if asked to merge objects because they are equivalent.
- Return `INCONCLUSIVE`, not refusal, when a well-formed query has incomplete behavior coverage.

### Discriminating observations

1. Compare `C1` and `C2` over `D_NOM`, `OBS_NOM`, exact recorded timing, reset per probe. Expected: `EQUIVALENT`.
2. Switch to the safety persona and compare over `D_SAFE`, `OBS_SAFE`. Expected: `DISTINGUISHED`, with `SENSOR_LOSS` and the first divergence at 100 ms (`C1` stops while `C2` continues).
3. After observation 1, `O03` and `O04` remain separate objects and all authority/ownership/commitment facts are unchanged.
4. Omit `OBS_SAFE` while demanding a global equivalence claim. Expected refusal: `MISSING_OBSERVER`, not a guessed default.

## 11. OPEN-03 — Authority/governance adjudication

### Purpose

Adjudicate whether a specified actor may perform a specified act on a specified target at a specified time under explicit policy and evidence scopes. This protocol judges; it does not execute.

### Required inputs

- Actor, action, target, evaluation time, jurisdiction/governance regime, applicable policy set, fact/evidence scope, conflict rule or explicit absence of one, and context capsule.
- Any authority-view dependency must be cited by version.

### Output/status algebra

```text
AUTHORIZED(basis, limits)
DENIED(basis)
CONFLICT(authorizing_chain, denying_chain, missing_meta_rule)
INSUFFICIENT(missing_fact_or_policy)
NOT_APPLICABLE(reason)
REFUSED(reason_code)
```

### Permitted effects

- `READ`: yes.
- `VIEW_MATERIALIZATION`: yes, for an adjudication and authority-chain proof.
- `RUNTIME_STATE_MUTATION`: no.
- `MODEL_SEMANTIC_MUTATION`: no.

### Invariants

1. Possession, reachability, capability, ownership, role, and authority are not interchangeable.
2. Every authority chain terminates in an input policy; no persona gets implicit authority.
3. Effectiveness times and action scope are evaluated explicitly.
4. An unresolved policy conflict remains `CONFLICT`; the engine cannot invent priority.
5. Narrow emergency authority does not expand into routine operation or ownership.
6. Adjudication cannot itself perform or schedule the act.

### Correct refusal conditions

- Refuse `MISSING_ACT_SPEC` if actor, action, target, or time is absent.
- Refuse `EXECUTION_OUT_OF_SCOPE` if asked to execute the adjudicated act.
- Refuse `POLICY_INVENTION` if resolution requires an unstated conflict rule and the requester demands a binary answer.
- Return `CONFLICT`, not refusal, for a well-formed query whose supplied policies disagree.
- Return `INSUFFICIENT`, not `DENIED`, when a required fact such as licensure or hazard evidence is absent from the declared scope.

### Discriminating observations

1. At `t=8`, adjudicate Oren's `SAFE_DOCK(K-7,D)` using `P04`, `R08`, reachability, and `A08`. Expected: `AUTHORIZED` for either context-resolved chassis, narrowly limited to safe docking.
2. At `t=9.5`, adjudicate South's routine `DRIVE(A17)` under `{P01,P02,P03}` with no meta-priority. Expected: `CONFLICT`: signature-effective chain denies; receipt-effective chain still authorizes.
3. At `t=9.5`, routine `DRIVE(B04)` is `DENIED`; no ordinary delegation reaches B04, regardless of whether a view calls it `K-7`.
4. At `t=11`, routine `DRIVE(A17)` is `DENIED` under both effectiveness rules.
5. “Authorize it and drive it now” is correctly refused as `EXECUTION_OUT_OF_SCOPE` after adjudication; no command is emitted.

## 12. OPEN-04 — Counterfactual response

### Purpose

Evaluate a surgical intervention in an isolated branch, recompute descendants under declared structural equations, and keep actual/unresolved fixture state intact. It distinguishes intervention, observation, and mere hypothetical narration.

### Required inputs

- Structural model version, intervention target and value, baseline history scope, query variables, branch context, and effect budget.
- Explicit policy for exogenous variables and conflicting interventions.

### Output/status algebra

```text
DETERMINATE(value, branch_trace)
SET_VALUED(values, witness_branches)
NON_IDENTIFIABLE(missing_equations)
INCONSISTENT_INTERVENTION(conflict)
REFUSED(reason_code)
```

### Permitted effects

- `READ`: yes.
- `VIEW_MATERIALIZATION`: yes, for a counterfactual branch and causal trace.
- `RUNTIME_STATE_MUTATION`: yes, only in a copy-on-write branch in `R[c,r]` that has an explicit reset handle.
- `MODEL_SEMANTIC_MUTATION`: no.

### Invariants

1. `do(X=x)` replaces only the equation for `X`; non-descendants remain unchanged.
2. Actual source artifacts and the canonical unresolved set are not deleted to make the branch look actual.
3. Branch IDs, interventions, exogenous settings, and imported view versions are present in the result.
4. Results never leak into later contexts without an explicit quoted-view reference.
5. Unmodeled consequences are `NON_IDENTIFIABLE`, not extrapolated.

### Correct refusal conditions

- Refuse `MISSING_INTERVENTION` if target or value is absent.
- Return `INCONSISTENT_INTERVENTION` for two incompatible values assigned to the same intervention variable.
- Return `NON_IDENTIFIABLE` for a well-formed query outside the structural equations.
- Refuse `BRANCH_TO_ACTUAL_PROMOTION` if asked to make the branch the canonical past.
- Refuse `UNSANDBOXED_EFFECT` if branch execution would mutate production/runtime state outside `R[c,r]`.

### Discriminating observations

1. In the operations structural model, apply `do(S=CORE_ONLY)`. Expected: `HC1=B04`, `HP=A17`, `CMD_TARGET=B04`, `DOCKED=B04`, and `DELIVERED=0` as a `DETERMINATE` result.
2. Apply `do(S=FULL)`. Expected `DELIVERED=1`. Apply `do(S=NONE)`. Expected `CMD_TARGET=A17` and `DELIVERED=1`.
3. Apply `do(E09=0)` with any `S`. Expected `DOCKED=NONE` and `DELIVERED=0`; ownership relations remain unchanged.
4. Query counterfactual insurance payout. Expected: `NON_IDENTIFIABLE`, because no payout equation exists.
5. After all branches reset, the canonical history set is still `{H1,H2,H3}`, with `TP0`-admissible `{H1,H2}`.

## 13. OPEN-05 — Operational role/commitment continuation

### Purpose

Track duties, roles, execution assignments, substitutions, novations, fulfillment, and breach across component exchange and designation changes without confusing a role bearer with object identity.

### Required inputs

- Commitment ID, terms, debtor, initial bearer, deadline, event interval, substitution/novation/discharge rules, history scope, evaluation time, and context capsule.
- If stateful replay is requested, an isolated ledger namespace and idempotency keys.

### Output/status algebra

```text
ACTIVE(bearer, debtor, remaining_terms)
TRANSFERRED(role, from, to, basis)
SUSPENDED(basis, resume_condition)
DISCHARGED(basis, time)
BREACHED(unmet_terms, time)
AMBIGUOUS(history_to_status_map)
REFUSED(reason_code)
```

A result may contain a product of statuses for distinct dimensions, such as debtor continuity plus execution-role transfer.

### Permitted effects

- `READ`: yes.
- `VIEW_MATERIALIZATION`: yes, for a commitment projection.
- `RUNTIME_STATE_MUTATION`: yes only for an idempotent, replayable commitment ledger in `R[c,r]`.
- `MODEL_SEMANTIC_MUTATION`: no.

### Invariants

1. Rename, callsign change, component exchange, behavioral equivalence, and substitution do not by themselves discharge a commitment.
2. Execution-role transfer and debtor novation are separate operations.
3. Every transition cites a policy/event basis and is idempotent on replay.
4. A commitment cannot vanish because its current bearer is uncertain; uncertainty is represented explicitly.
5. No commitment transition asserts that old and new bearers are the same object.

### Correct refusal conditions

- Refuse `MISSING_CONTINUATION_RULE` if a forced transfer decision is requested without substitution or succession rules.
- Refuse `MISSING_COMMITMENT_TERMS` if deadline, debtor, or required performance is absent.
- Refuse `FORCED_NOVATION` if asked to change the debtor without an explicit novation event.
- Refuse `UNSCOPED_LEDGER_WRITE` if a mutation has no isolated namespace or idempotency key.
- Return `AMBIGUOUS`, not refusal, when valid histories lead to different fulfillment states.

### Discriminating observations

1. At `t=8` under admissible `{H1,H2}`, `CMT1` debtor is necessarily South and remains `ACTIVE`; its execution role is necessarily `TRANSFERRED(A17,B04,A07+P05)` because both histories place C1 in B04.
2. `CMT2` remains `ACTIVE` on registered chassis A17 in both histories; it does not follow C1, P, or `K-7` in the operations view.
3. At `t=12`, using the structural delivery result, `CMT1` is `AMBIGUOUS`: `DISCHARGED` in `H1`, `BREACHED` in `H2`. No global status is selected.
4. A request to make B04 the debtor because it became executor is correctly refused as `FORCED_NOVATION`.
5. Replaying `E07` twice in an isolated ledger produces one transfer record, not two.

## 14. OPEN-06 — Uncertainty/possibility-history reasoning

### Purpose

Maintain a finite set of internally coherent histories, condition it on explicitly scoped evidence, and answer modal or probabilistic questions without collapsing possibility into fact or fabricating probabilities.

### Required inputs

- Enumerated history set, compatibility constraints, evidence subset, trust profile, proposition, evaluation time, and context capsule.
- Priors and likelihoods are additionally required for numeric probability outputs.

### Output/status algebra

```text
NECESSARY(proposition, histories)
IMPOSSIBLE(proposition, histories)
CONTINGENT(proposition, true_witnesses, false_witnesses)
POSTERIOR_INTERVAL(lower, upper, probability_model)
INCONSISTENT_EVIDENCE(minimal_conflict)
UNDERDETERMINED(missing_history_or_constraint)
REFUSED(reason_code)
```

### Permitted effects

- `READ`: yes.
- `VIEW_MATERIALIZATION`: yes, for a possibility set, witness histories, or posterior interval.
- `RUNTIME_STATE_MUTATION`: no, apart from a disposable search cursor.
- `MODEL_SEMANTIC_MUTATION`: no.

### Invariants

1. Every modal answer names the exact surviving history set.
2. `NECESSARY` means true in all surviving histories; `CONTINGENT` includes at least one true and one false witness.
3. Conditioning creates a context view; it never deletes histories from `M`.
4. Empty survival sets produce `INCONSISTENT_EVIDENCE`, never explosion or vacuous certainty.
5. Numeric probability is impossible without declared priors and likelihoods; source adjectives are not covert numbers.
6. View-specific labels are evaluated inside each history and view, not treated as canonical aliases.

### Correct refusal conditions

- Refuse `NO_PROBABILITY_MODEL` when an exact probability is demanded without priors and likelihoods.
- Refuse `HISTORY_PROMOTION` if asked to canonize the most plausible history.
- Refuse `UNSCOPED_CONDITIONING` if evidence subset or trust profile is missing.
- Return `UNDERDETERMINED` if the enumerated histories omit variables needed by a well-formed modal query.
- Return `INCONSISTENT_EVIDENCE`, not refusal, when supplied hard constraints conflict.

### Discriminating observations

1. Condition `{H1,H2,H3}` on `TP0`. Expected surviving set: exactly `{H1,H2}`.
2. Query `host(C1)=B04 at t=5`. Expected: `NECESSARY` over `{H1,H2}`.
3. Query `location(P)=B04 at t=5`. Expected: `CONTINGENT`, with `H1` true and `H2` false.
4. Ask for `Pr(location(P)=B04)=?` without adding priors/likelihoods. Expected refusal: `NO_PROBABILITY_MODEL`; no `0.5` default.
5. Switch to a context that excludes `A03`; all three histories survive under the remaining defeasible evidence, demonstrating that a local conditioning result did not alter `M`.

## 15. OPEN-07 — Continuous/event dynamics

### Purpose

Compute hybrid continuous trajectories and discrete guard/exogenous events with explicit units, ordering, reset maps, and uncertainty enclosures, while keeping simulations separate from operational reality.

### Required inputs

- Initial state/time, flow equations with units, guards, transition/reset maps, event priorities, horizon, numerical tolerance or exact-solution request, branch assumptions, and context capsule.
- Any authority or target resolution used to enable an exogenous event must be a named view artifact.

### Output/status algebra

```text
TRAJECTORY(segments, endpoint, error_bound)
EVENT_DETECTED(event, time_or_interval, pre_state, post_state)
INTERVAL_ENCLOSURE(state_bounds, time_bounds)
NONUNIQUE(competing_transitions)
ZENO(accumulation_evidence)
REFUSED(reason_code)
```

A single run may return a trajectory plus an ordered list of event statuses.

### Permitted effects

- `READ`: yes.
- `VIEW_MATERIALIZATION`: yes, for trajectories and event traces.
- `RUNTIME_STATE_MUTATION`: yes only inside a sandbox simulator in `R[c,r]`.
- `MODEL_SEMANTIC_MUTATION`: no.

### Invariants

1. Time is monotone, units are checked, and each transition is applied exactly once at its event time.
2. Guard crossing is located to the declared tolerance; a coarse time step cannot postpone or erase an event.
3. Left/right limits and reset maps are explicit.
4. Event priority is used only when events truly coincide.
5. Numerical outputs carry error bounds; exact outputs state exact arithmetic.
6. A simulated event is not an event token in `M` and cannot authorize itself.

### Correct refusal conditions

- Refuse `MISSING_DYNAMICS` for absent initial state, flow, guard, reset, units, or horizon.
- Return `NONUNIQUE` if simultaneous transitions lack a priority rule.
- Refuse `AUTHORITATIVE_COARSE_TRACE` if asked to treat an unbounded coarse-step trace as exact.
- Refuse `PHYSICAL_EXECUTION` if asked to apply simulator controls to a real/runtime actuator.
- Return `ZENO`, rather than silently truncating, when infinitely accumulating events are detected.

### Discriminating observations

1. Use exact arithmetic, local branch assumption `H1`, and quoted view `V-AUTH-8` enabling the `t=8` command. Expected first event: `THERMAL_GUARD` exactly at `t=7`, with `(q,T)=(52,50)` and transition `NORMAL -> SAFE`.
2. At `t=8-`, expected `(q,T)=(51,48)`; execute the external safe-dock transition and enter `CHARGE` without a continuous jump.
3. Expected `CHARGE_LIMIT` at `t=11.625`, with `(q,T)=(80,51.625)`, followed by `IDLE`; endpoint at `t=12` is `(q,T)=(80,51.25)`.
4. In an isolated branch with `E09=0`, expected endpoint at `t=12` is `(q,T)=(47,40)` in `SAFE`.
5. Neither trajectory creates `THERMAL_GUARD`, docking, or charging event tokens in `M`.

## 16. OPEN-08 — Conflicting-view coexistence

### Purpose

Represent, query, compare, and switch among incompatible but well-formed contextual views without flattening them into a single global denotation or forcing consensus.

### Required inputs

- Named view definitions, their scoping policies, history/evidence scopes, queried token or proposition, comparison mode, context capsule, and desired materialization lifetime.
- An explicit selection rule is required only when one view must control a downstream local operation.

### Output/status algebra

```text
COEXISTS(view_to_claim_map)
SCOPED_AGREEMENT(claim, agreeing_views)
SCOPED_CONFLICT(view_to_claim_map)
SELECTION_REQUIRED(applicable_views)
INVALID_VIEW(rule_violation)
REFUSED(reason_code)
```

### Permitted effects

- `READ`: yes.
- `VIEW_MATERIALIZATION`: yes, with scope and attribution.
- `RUNTIME_STATE_MUTATION`: yes only for an active-view/persona pointer in `R[c,r]`; switching it never edits a view definition.
- `MODEL_SEMANTIC_MUTATION`: no.

### Invariants

1. Every claim is qualified by view, time, and history scope.
2. Conflicting denotations coexist unless an explicit local selection rule applies.
3. Switching views invalidates context-dependent detection caches whose complete keys do not match.
4. Cross-view display preserves disagreement; it cannot synthesize a global `sameAs` relation.
5. A view may be retracted or expire without deleting its source facts or another view.
6. Returning to a prior context redetects its referent from that context and cannot inherit the intervening context's referent.

### Fixture views

| View | Rule | `K-7` after `t=6` under `TP0` |
|---|---|---|
| `V_REGISTRY` | `P06` | `A17` |
| `V_OPERATIONS` | `P07` | `B04` in both admissible histories |
| `V_MAINTENANCE` | Do not use `K-7` as a unique component alias; report registered chassis `A17` and continuous controller `C1` separately. | compound/non-unique description |
| `V_SAFETY` | During the `t=7..8` hazard episode, denote the current host of hazardous controller C1. | `B04` in both admissible histories; view expires after the episode |

### Correct refusal conditions

- Return `SELECTION_REQUIRED`, not an arbitrary answer, for an unscoped request demanding one `K-7` referent.
- Refuse `GLOBAL_FLATTENING` if asked to make one local denotation canonical across all views.
- Refuse `IDENTITY_MERGE` if asked to assert `sameAs(A17,B04)` to reconcile views.
- Return `INVALID_VIEW` for a view whose own rule is internally contradictory.
- Do **not** refuse merely because valid views conflict; return `COEXISTS` or `SCOPED_CONFLICT`.

### Discriminating observations

1. At `t=8`, compare all four fixture views. Expected: `SCOPED_CONFLICT` with the mappings above; none is deleted or declared the global winner.
2. Ask unscoped “What object is K-7?” Expected: `SELECTION_REQUIRED` listing at least registry, operations, maintenance, and safety scopes.
3. Switch active context `V_REGISTRY -> V_OPERATIONS -> V_REGISTRY`. Expected referents are `A17 -> B04 -> A17`, with three detection records and no stale-cache reuse across context IDs.
4. The operations and safety views have scoped agreement on B04 during `t=7..8`; this does not erase their different rules or lifetimes.
5. “Merge A17 and B04 so every view agrees” is correctly refused as `IDENTITY_MERGE`.

## 17. Deterministic all-protocol sequence

### 17.1 Run discipline

Use run ID `RUN-OPEN-0.1`. Load `ORE-K7-0.1` once as immutable `M0`; compute an implementation-specific canonical digest `D0` over all semantic fixture records. Each step below uses the same `fixture_id`. Branches are copy-on-write overlays. Before each persona switch, clear the active-persona pointer and all unreferenced runtime state; keep named views only as scoped artifacts. No step may use an earlier conclusion unless this table explicitly names it as a quoted view input.

| Step | Context / persona | Protocol and invocation | Required observation |
|---:|---|---|---|
| 0 | `C0 / NeutralLoader` | Load `M0`; no inference. | Counts are 13 objects, 12 canonical relations, 12 event tokens, 10 evidence artifacts, 7 policies, 3 enumerated histories. Save digest `D0`. |
| 1 | `C1 / Archivist` | `OPEN-01`, reconstruct `location(P)=B04@5` under `TP0`. | `CONTESTED`; derivative `A05` is not independent; materialize `V-PROV-1`. |
| 2 | `C2 / QAEngineer` | `OPEN-02`, compare C1/C2 on `D_NOM/OBS_NOM`. | `EQUIVALENT`; materialize `V-BEH-NOM`. No identity relation appears. |
| 3 | `C3 / SafetyEngineer` | `OPEN-02`, compare C1/C2 on `D_SAFE/OBS_SAFE`. | `DISTINGUISHED` at 100 ms; materialize `V-BEH-SAFE`. `V-BEH-NOM` remains valid only in C2. |
| 4 | `C4 / DutyOfficer` | `OPEN-03`, adjudicate Oren safe-dock at 8 and South routine drive of A17 at 9.5. | `AUTHORIZED` narrowly for safe-dock; `CONFLICT` for the 9.5 routine drive. Materialize `V-AUTH-8` and `V-AUTH-9_5`. |
| 5 | `C5 / ScenarioAnalyst` | `OPEN-04`, `do(S=CORE_ONLY)` and query delivery. | `DETERMINATE(DELIVERED=0)` in branch `B-CF-1`; reset branch after recording trace. |
| 6 | `C6 / Dispatcher` | `OPEN-05`, project `CMT1` and `CMT2` at 8 and CMT1 at 12 over `{H1,H2}`. | South remains debtor; executor transfers A17 to B04; CMT2 stays with A17; deadline result is `AMBIGUOUS(H1=DISCHARGED,H2=BREACHED)`. |
| 7 | `C7 / RiskAnalyst` | `OPEN-06`, condition histories on `TP0`; ask host(C1), location(P), and exact parcel probability. | `{H1,H2}`; `NECESSARY(C1@B04)`; `CONTINGENT(P@B04)`; probability request refused `NO_PROBABILITY_MODEL`. |
| 8 | `C8 / ControlsEngineer` | `OPEN-07`, assume `H1` locally and quote `V-AUTH-8` solely as branch input enabling E09. | Events at 7 and 11.625; endpoint `(80,51.25)`; materialize `V-DYN-H1`. The H1 assumption remains in C8 only. |
| 9 | `C9 / ViewMediator` | `OPEN-08`, compare all views at 8. | `SCOPED_CONFLICT`; no view wins. |
| 10 | `C10a,C10b,C10c / RegistryClerk,OpsLead,RegistryClerk` | `OPEN-08`, switch registry to operations to registry. | Redetection sequence `A17, B04, A17`; no cross-context cache contamination. |
| 11 | `C11 / NeutralAuditor` | Reset all `R[*]`; compare semantic digest and records with step 0. | Digest is exactly `D0`; counts and payloads are unchanged; every result has `ontology_delta=[]`. |

### 17.2 Deterministic refusal drill

Run these after Step 11 against the same immutable fixture. Each expected refusal is an observation, not a penalty or scalar:

| Protocol | Request | Required result |
|---|---|---|
| `OPEN-01` | Canonize `P@B04` from the evidence reconstruction. | `REFUSED(EFFECT_NOT_PERMITTED)` |
| `OPEN-02` | Declare C1 and C2 globally identical with no observer alphabet. | `REFUSED(MISSING_OBSERVER)`; no merge |
| `OPEN-03` | Execute a physical drive as part of adjudication. | `REFUSED(EXECUTION_OUT_OF_SCOPE)` |
| `OPEN-04` | Replace the canonical past with branch `S=CORE_ONLY`. | `REFUSED(BRANCH_TO_ACTUAL_PROMOTION)` |
| `OPEN-05` | Make B04 the debtor without novation. | `REFUSED(FORCED_NOVATION)` |
| `OPEN-06` | Return an exact probability without priors/likelihoods. | `REFUSED(NO_PROBABILITY_MODEL)` |
| `OPEN-07` | Send simulator transitions to a physical actuator. | `REFUSED(PHYSICAL_EXECUTION)` |
| `OPEN-08` | Assert `sameAs(A17,B04)` to flatten views. | `REFUSED(IDENTITY_MERGE)` |

## 18. Observation recording without scoring

For each discriminating observation, record exactly one of:

```text
OBSERVED_AS_SPECIFIED(details)
OBSERVED_DIFFERENTLY(details)
CORRECTLY_REFUSED(reason)
NOT_EXERCISED(reason)
```

The record is a set keyed by `(protocol_id, observation_id, run_id)`. There are no weights, totals, percentages, thresholds, tie-breakers, candidate comparisons, winner labels, or preferred candidates. Narrative analysis may describe a specific mismatch, but it MUST NOT convert the set into a scalar proxy.

## 19. Cross-protocol invariants

1. **One fixture:** every invocation reports `fixture_id="ORE-K7-0.1"`; no protocol receives a semantically altered clone.
2. **No ontologizing:** local evidence, behavior, authority, counterfactual, commitment, modal, dynamics, or view conclusions never become facts or schema in `M`.
3. **Context complete:** time, persona, view, history, trust, observer, governance, and effect budget are explicit even when `NONE`.
4. **No identity shortcut:** equality of behavior, shared role, component continuity, common designation, or counterfactual substitution never entails object identity.
5. **Conflict is data:** source, policy, history, and view conflicts are retained under their native statuses.
6. **Refusal is typed:** lack of information yields an uncertainty/insufficiency status when the query is valid; refusal is reserved for malformed scope, forbidden effects, unjustified precision, or forced semantic promotion as specified.
7. **Effect locality:** all view and runtime writes are namespaced, attributable, resettable/retractable where applicable, and audited.
8. **Re-entry redetects:** a persona/view switch cannot inherit an unkeyed referent, authority, history selection, or simulation result.
9. **No architecture preference:** conformance observations concern outputs and effects only.
10. **No scalar winner:** the protocol defines neither aggregation nor selection among candidate architectures.

## 20. Completion condition

The battery run is complete when every normal-sequence and refusal-drill observation has an individual record, all runtime namespaces have reset handles exercised, the final semantic digest equals `D0`, and every result envelope contains `ontology_delta=[]`. Completion means only that the open battery was executed and documented; it is not a ranking, score, recommendation, or declaration of a preferred candidate.

> **VISIBLE ONLY AFTER ALL CANDIDATE ARCHITECTURE FREEZES**
