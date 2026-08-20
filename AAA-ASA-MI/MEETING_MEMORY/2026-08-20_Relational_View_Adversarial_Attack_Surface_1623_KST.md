# AAA-ASA-MI Meeting Memory

## Title
Relational View / Materialized Instance — Adversarial Attack Surface

## Date / Time
2026-08-20 16:23 KST

## Status
WORKING_RESEARCH_CONTEXT / ADVERSARIAL_BRAINSTORM / INIT_CURRENTIZATION

## Purpose

Preserve adversarial questions against the current strong candidate `INSTANCE-AS-RELATIONAL-VIEW HYPOTHESIS` and related Boundary / Materialization / Self-as-relational-consensus ideas.

This record is NOT a Requirement, Design Contract, Frozen Artifact, Final Ontology, Validation Receipt, or Final Truth.

Current strong lean is deliberately treated as attackable. INIT implementation suitability remains the primary selection criterion.

---

## 1. Current Strong Candidate Under Attack

`INSTANCE-AS-RELATIONAL-VIEW HYPOTHESIS`

Working idea:

A concrete INSTANCE need not be treated as a permanently identical substance that persists while only attributes change. It may instead be an exact discrete object materialized from current relational/process/primitive configuration under a particular time, environment, purpose, hypothesis set, and boundary/composition rule.

Different materializations are different instances.

`I_1 != I_2`

They may have succession relations rather than continuity/equality.

The current candidate is especially attractive because merge, absorption, fission, branching, overlapping membership, and changing self/boundary semantics can be represented without requiring one metaphysically continuous identity.

---

## 2. Adversarial Principle

Do not ask only whether the relational-view model is internally coherent.

Compare it against simpler and competing baselines.

Strong comparison question:

> Does relational-view materialization provide enough additional explanatory and implementation value to justify its semantic and computational complexity compared with simpler entity-first, event-sourced, component-based, temporal, process, or hybrid models?

`CURRENT LEAN != IMPLEMENTATION COMMITMENT`

---

## 3. Formal Attack — Relations May Presuppose Relata

In conventional mathematics, a relation is defined over a domain/codomain or carrier set. A binary relation is commonly modeled as a subset of a Cartesian product.

Therefore a strong challenge is:

> Can RELATION genuinely be prior to entities, or does a formal relation already require something relation-like to connect?

Possible outcomes:

- Relation-first survives only as modeling priority, not ontological priority.
- Nodes/carriers remain opaque primitives while intrinsic essence is intentionally left undefined.
- Higher-order structural positions may substitute for rich entity definitions.
- Strong relation-only ontology may be rejected while relation-first modeling remains useful.

---

## 4. Substrate Attack — A Materialized View Is a View of What?

Database materialized views require a base substrate.

If instances are views, ASA-MI must answer what the view is materialized from.

Candidates:

- primitive values;
- events;
- claims/evidence;
- processes;
- relations;
- exact references;
- historical records;
- combinations.

If every substrate element is itself only another materialized view, infinite regress or hidden base assumptions may appear.

Important distinction:

`IMPLEMENTATION PRIMITIVE != METAPHYSICAL ATOM`

An implementation may stop decomposing at a primitive without claiming reality itself is atomistic.

---

## 5. Boundary Attack — Relation Alone May Be Insufficient

Owner currently suspects Boundary may itself be a type of relation.

Adversarial refinement:

A boundary may require at least three separable concepts:

- boundary relation: how an element relates to an instance with respect to inside/outside/interface/shared/etc.;
- boundary rule/operator: how relations/conditions are evaluated to select members for the current materialization;
- materialized boundary: the exact members and crossing relations included in a particular exact instance.

If these are collapsed, semantic circularity and implementation ambiguity increase.

---

## 6. Circularity / Fixed-Point Attack

If instance composition depends on relations and boundary:

`INSTANCE = F(RELATIONS, BOUNDARY, ...)`

but relations/boundary themselves depend on the instance:

`RELATION = G(INSTANCE_A, INSTANCE_B, ...)`

`BOUNDARY = H(INSTANCE, RELATIONS, ...)`

then one-way evaluation may not be sufficient.

Risks:

- non-termination;
- multiple valid fixed points;
- oscillating membership;
- order-dependent evaluation;
- hidden arbitrary tie-break rules;
- unreplayable materialization.

Alternatives to compare:

- well-founded dependency rules;
- monotonic fixed-point semantics;
- constraint solving;
- graph closure;
- rule engines;
- event-sourced materialization;
- hybrid designs.

---

## 7. Purpose / Observer Capture Attack

If materialization depends on purpose, context, or observer:

`INSTANCE = Materialize(Relations, Purpose, Context, ...)`

then a malicious or poorly selected purpose may materially reshape the object being modeled.

Questions:

- Is the instance a property of the modeled reality or of the query/task?
- Can two purposes produce incompatible instances from the same substrate?
- Does task objective become an unacknowledged ontology constructor?
- Can an external provider manipulate the boundary by changing the prompt/objective?

Possible safeguard:

Purpose/context must become explicit provenance rather than hidden execution context.

---

## 8. Cost / Relation Explosion Attack

Naively recomputing a relational instance from a large dynamic network may be expensive.

Risks:

- dense graph traversal;
- higher-order relations;
- relation-between-relation expansion;
- invalidation fan-out;
- many purpose-specific materializations;
- many overlapping boundaries;
- repeated fixed-point evaluation;
- large lineage storage.

Potential implementation candidates:

- materialized current instances;
- dependency tracking;
- incremental view maintenance;
- event-triggered refresh instead of clock-tick refresh;
- bounded scopes;
- selective rematerialization;
- caching with explicit invalidation.

The hypothesis should be benchmarked, not defended rhetorically.

---

## 9. Staleness / Refresh Semantics Attack

A database materialized view can become stale when base data changes.

Likewise a relational instance may no longer correspond to the latest relational substrate.

Open questions:

- immediate rematerialization?
- lazy/on-read?
- event-triggered?
- explicit versioned stale state?
- eventual convergence?

Important candidate rule:

Old exact materializations should not be silently overwritten. A new exact instance may be created and linked by SUCCESSION where appropriate.

---

## 10. Referential Stability Attack

If each materialization creates a new instance, external systems still need stable references.

Need to distinguish candidates such as:

- exact instance reference;
- lineage reference;
- conceptual/model reference;
- current-pointer/reference.

A stable lineage ref must not be confused with proof of metaphysical identity.

Without this separation, APIs, authority grants, memory references, and audit records may become unstable or ambiguous.

---

## 11. Merge / Fission Representation Is Easy; Semantics Are Not

Relational lineage can easily DRAW merge and fission:

`A -> C <- B`

`A -> B`

`A -> C`

But representation does not solve semantic inheritance.

Questions:

- which memories transfer?
- which obligations transfer?
- which relations persist?
- conflicting members?
- duplicated resources?
- authority?
- external references?
- legal/accounting identity?
- lineage weighting or contribution?

Critical existing direction:

`SUCCESSION != AUTHORITY INHERITANCE`

Merge/fission should probably produce explicit receipts/policies rather than infer all inheritance from lineage.

---

## 12. Intrinsic Constraint Attack

Strong relation-first thinking may accidentally underweight properties that are local/intrinsic enough to matter regardless of current network.

Examples may include:

- cryptographic key material;
- physical capacity;
- local process state;
- immutable historical evidence;
- primitive numerical values;
- hardware/environment constraints.

Potential conclusion:

Relation-first may need to coexist with primitives/local state rather than replace them.

---

## 13. Missing Relation Attack

`NO EDGE FOUND != NO RELATION`

A relation-first system is especially vulnerable to treating retrieval failure as ontological absence.

Need separation among:

- verified relation;
- inferred relation;
- disputed relation;
- unknown relation;
- explicitly absent relation;
- stale relation.

Otherwise relation-first modeling amplifies data incompleteness into false object boundaries.

---

## 14. Binary Graph Attack

Not all relationships are binary edges.

Potential requirements include:

- n-ary relations;
- context-indexed relations;
- time-indexed relations;
- relation-to-relation relations;
- events that bind multiple participants;
- asymmetric claims and mutual recognition.

Therefore `RELATION-FIRST != SIMPLE PROPERTY GRAPH`.

A Graph DB implementation must not be inferred from the philosophical/modeling hypothesis.

---

## 15. Temporal Granularity Attack

If each time point produces a new instance, what counts as a new point?

Clock-based materialization can cause instance explosion.

Potential alternatives:

- event-triggered materialization;
- semantic-change-triggered materialization;
- threshold-based materialization;
- explicit owner/system checkpoints;
- demand-driven/on-query materialization.

This is a major INIT cost and lineage-size issue.

---

## 16. Self-as-Relational-Consensus Falsifiability Attack

Current Owner working worldview:

Self is not a permanent identity substance; consciousness/self may be modeled as a bundle of connected processes whose self-referential relational organization treats an aggregate as “me.”

Adversarial concern:

If “consensus” is defined broadly enough to explain every self-like phenomenon, the hypothesis becomes unfalsifiable.

Need to distinguish:

- philosophical interpretive hypothesis;
- measurable operational hypothesis;
- implementation requirement.

Potential adversarial question:

> What observation or experiment would cause ASA-MI to weaken or reject the `SELF-AS-RELATIONAL-CONSENSUS` hypothesis?

It should not become INIT requirement merely because it elegantly fits Owner worldview.

---

## 17. Security / Authority Boundary Attack

A relational, context-dependent self boundary must not automatically control hard authorization boundaries.

Keep separate:

`SELF MEMBERSHIP != AUTHORITY`

`RELATIONAL INCLUSION != SECRET ACCESS`

`SUCCESSION != GRANT SUCCESSION`

Authorization may require deterministic hard enforcement even if self/model boundaries remain dynamic and relational.

---

## 18. Perturbation Stability Attack

If a tiny relation change causes massive instance re-materialization, the model may be too brittle for practical use.

Research questions:

- sensitivity to small input changes;
- boundary churn rate;
- materialization fan-out;
- relation noise tolerance;
- stable core vs rapidly changing fringe.

A model can reject ontological continuity while still needing engineering stability.

---

## 19. Cross-View Reconciliation Attack

Different purposes or models may materialize different instances from overlapping substrate.

Do not silently force one canonical answer.

Need research on relations between views themselves:

- overlaps;
- conflicts;
- projection/subsumption;
- shared lineage;
- mutually inconsistent boundaries;
- different scales/resolutions.

The system may need to preserve multiple materializations simultaneously.

---

## 20. Strong Alternative Baselines for Codex Committee

The relational-view hypothesis should be compared against at least the following implementation families rather than reviewed in isolation:

### Baseline A — Entity-first + Event Sourcing
Stable technical entity references with append-only events and derived current state.

Strength: simple identity/reference semantics, strong replay.
Attack on relational view: perhaps merge/fission can be handled with explicit events without redefining instance ontology.

### Baseline B — Entity Component System (ECS)
Entities as lightweight references; composition comes from changing sets of components; systems/functions operate over components.

Strength: composition-friendly and implementation-proven.
Attack: function-member and member-set intuitions may already be achievable without treating the whole instance as relational view.

### Baseline C — Temporal/Bitemporal Model + Lineage
Keep exact time-scoped facts/states plus predecessor/successor lineage.

Strength: history/PIT/replay are explicit.
Attack: relational materialization may be unnecessary for most use cases.

### Baseline D — Event/Process Ontology
Treat events/process transitions as primary and materialize entities only as convenient aggregates.

Strength: merge/fission/change naturally represented.
Attack: process-first may outperform relation-first for liveness/evolution.

### Baseline E — Event-Sourced Relational Substrate + Materialized Instance Views
Keep primitives/events/relations as base substrate and derive versioned instances as views.

Strength: directly captures the current Owner intuition while containing recomputation through event sourcing/materialization.
Risk: highest conceptual/engineering complexity among simple candidates.

---

## 21. Suggested Codex Committee Attack Questions

1. Does `INSTANCE-AS-RELATIONAL-VIEW` solve a concrete problem that simpler entity-first + event sourcing cannot solve cleanly?
2. What is the minimal non-view substrate required to prevent infinite regress?
3. Can Boundary be modeled without circular self-definition?
4. Under what constraints is instance materialization deterministic/replayable?
5. If stochasticity exists, what exactly must be frozen for historical reconstruction?
6. How large can dependency/invalidation fan-out become in realistic workloads?
7. How are exact-instance refs separated from lineage refs and current pointers?
8. Can merge/fission semantics be specified without accidental authority inheritance?
9. How is relation missingness separated from relation absence?
10. Does relational-view remain useful when relations are n-ary/contextual/temporal rather than simple graph edges?
11. What falsifies `SELF-AS-RELATIONAL-CONSENSUS`?
12. Give concrete cases where entity-first, ECS, process-first, or temporal models are simpler and equally expressive.
13. Give a minimal prototype and measure materialization cost, replay cost, invalidation cost, and semantic clarity.
14. Identify the smallest surviving core if the strong relational-view hypothesis fails.

---

## 22. INIT Decision Discipline

The current strong relational hypothesis should enter INIT only to the extent justified by implementation suitability.

Candidate gate:

- expressive advantage is demonstrated for actual target scenarios;
- merge/fission/boundary semantics are materially clearer than baseline;
- exact materialization and lineage are replayable/auditable;
- computational cost is bounded enough for INIT;
- hard authority/security boundaries remain separable;
- failure modes are containable;
- simpler alternatives were actually compared.

If these do not hold, retain the philosophical/modeling hypothesis as research context and choose a simpler INIT implementation.

---

## Five-Line Summary

현재 상태: `INSTANCE-AS-RELATIONAL-VIEW`는 Owner가 강하게 기울어진 현행화 후보지만 INIT 구현 채택 전 대항군 공격이 필요한 상태다.
핵심 판단: 가장 강한 반론은 relation의 relata 선행 문제, materialized view의 base substrate 문제, boundary/instance 순환성, 비용·staleness·reference 안정성, merge/fission의 의미 계승 문제다.
진행 작업: Entity-first+Event Sourcing, ECS, Temporal/Lineage, Process-first, Event-sourced relational materialization을 경쟁 baseline으로 정의하고 공격 질문을 수집했다.
다음 단계: Codex 대항군 위원회가 강한 가설을 그대로 공격하고 최소 prototype/benchmark를 통해 표현력·재현성·비용·명료성을 비교하도록 Task Design에 반영한다.
사용자 행동: 현재는 강한 가설을 약화해 숨기지 말고 공격 가능한 형태로 유지하되, 대항군 결과가 더 단순한 대안을 지지하면 INIT 구현은 그쪽으로 현행화한다. 작성시각: 2026-08-20 16:23 KST
