# AAA-ASA-MI Meeting Memory

## Title
Relation Recall Stimulus and Candidate Map

## Date / Time
2026-08-20 16:51 KST

## Status
WORKING_RESEARCH_CONTEXT / BRAINSTORM / RELATION_DEEP_RECALL / INIT_CURRENTIZATION_PREPARATION

## Purpose
Preserve the Owner direction that RELATION is likely the most important hypothesis family below P0 because multiple other ASA-MI problems appear to belong to, derive from, or be expressible through relation structure.

This record is not a Requirement, Design Contract, Frozen Artifact, Final Ontology, Validation Receipt, Independent Validation PASS, or Final Truth.

All items remain mutable/currentization candidates.

---

## 1. Owner Direction

Owner explicitly states:

- RELATION is likely the most important hypothesis element below P0.
- In the current worldview, many other problems feel as though they belong inside the relation problem.
- Recall-stimulus is preferred because it may surface both previously thought ideas and ideas the Owner would likely currentize if they had known the relevant abstraction legacy.

Methodological discipline:

- Owner consistency may be used to generate candidates.
- Consistency is not evidence of truth.
- Distinguish OWNER_EXPLICIT / OWNER_RECALLED, ASA_INFERRED_FROM_PATTERN, and ASA_NEW_PROPOSAL.
- Currentization depends on explanatory value, adversarial survival, and INIT implementation suitability.

---

## 2. Relation as Family, Not Single Edge

Strong recall candidate:

> RELATION should not be prematurely reduced to a binary graph edge. It may be a family of conditional structures linking participants, roles, context, time, scale, scope, evidence, and possibly other relations.

Open dimensions:

- binary vs n-ary / hyperrelation;
- directed vs symmetric / asymmetric;
- typed vs open-ended;
- weighted/graded vs discrete;
- active vs latent/potential;
- observed vs claimed vs inferred;
- context/time/scale dependent;
- relation-to-relation / higher-order relation;
- persistent vs event-like/processual;
- constitutive vs causal vs functional vs normative vs epistemic.

No canonical relation ontology is adopted.

---

## 3. Candidate Relation Families That May Absorb Other ASA-MI Problems

Potential candidate families, not adopted taxonomy:

- CONSTITUTION / PARTICIPATION: what contributes to an instance composition;
- MEMBERSHIP: what currently participates as member and in what role;
- BOUNDARY: how internal/external/interface treatment is currently relationally determined;
- SUCCESSION: predecessor-successor lineage between distinct instances;
- MERGE / ABSORB / FISSION / DETACH / RECOMBINE: composition transformation relations;
- AUTHORITY / DELEGATION: scoped rights and permissions, explicitly separate from membership/self;
- MEMORY / PROVENANCE: what history/evidence a process or instance treats as its own or usable;
- OBSERVATION / PERSPECTIVE: who/what sees or models whom under what projection;
- CAUSAL / CONDITIONAL DEPENDENCY: what conditions the arising/change of another configuration;
- SELF-ATTRIBUTION / RECOGNITION: process bundle treating an aggregate as `self`;
- EVIDENCE / SUPPORT / CHALLENGE: relation between hypotheses and evidence/reviews;
- SCALE / AGGREGATION: lower-level materializations participating in higher-level materializations.

This candidate list is deliberately open; `everything is a relation` must remain falsifiable rather than becoming an unfalsifiable universal explanation.

---

## 4. N-ary and Role-Sensitive Relation Candidate

Binary A--B edges may be insufficient.

Some relations may only make sense as:

`R(participant_1: role_1, participant_2: role_2, ..., participant_n: role_n, context...)`

Examples include governance, transactions, multi-party agreements, composition bundles, and jointly constituted structures.

This suggests roles may belong to relation semantics rather than intrinsic participant properties.

INIT implication candidate:

- preserve ability to represent more than binary semantics;
- do not require full hypergraph infrastructure unless actual bounded bundle needs it;
- allow cheap projections (including trees/tables) when semantically sufficient.

---

## 5. Relation-to-Relation / Higher-Order Relation Candidate

A relation itself may participate in another relation.

Examples:

- one relation supersedes another;
- one authority relation constrains another;
- one evidence relation supports/challenges a relation claim;
- succession may apply to relation materializations themselves;
- boundary rules may operate over sets/patterns of relations.

Technical choices remain open:

- relation object/reference;
- reification;
- hyperedge-as-node;
- relation record with lineage;
- rule/constraint representation.

This is a major complexity risk and should be bounded in INIT.

---

## 6. Relation Materialization Candidate

If instances are discrete materialized relational views, relations may also need bounded materialization.

Candidate distinction:

- RELATION SEMANTICS / TYPE CANDIDATE;
- RELATION RECIPE / RULE;
- MATERIALIZED RELATION INSTANCE at time/context/scale;
- RELATION LINEAGE / SUCCESSION.

This would avoid pretending a relation is eternally identical through time.

However, it may cause combinatorial explosion if every relation change creates a new persisted object; benchmark required.

---

## 7. Configuration / Pattern May Be More Important Than Individual Relation

Owner's relational constitution intuition emphasizes configuration/network rather than isolated edges.

Candidate:

> The explanatory unit may be a bounded RELATION BUNDLE / CONFIGURATION / PATTERN, while individual relations are ingredients.

Consequences:

- the same members with different topology can materialize different instances;
- a relation bundle may be represented cheaply as a tree when sufficient;
- different bundles/scales may use different representation strategies;
- graph/hypergraph is not mandated by semantic relationality.

Potential adversarial question:

> Is relational configuration truly constitutive, or merely a useful compression/projection over a more primitive entity/event model?

---

## 8. Latent / Potential / Active Relation Candidate

Not every possible relation needs to participate in every current materialization.

Possible conceptual distinction:

- LATENT/POTENTIAL relation: available or possible in substrate but not active in the current bounded view;
- ACTIVE relation: participates in the current materialization;
- EXPIRED/INACTIVE relation: previously active but not current;
- UNKNOWN/UNRESOLVED relation: insufficient basis to materialize.

This may limit relation explosion.

No vocabulary is adopted yet.

---

## 9. Negative / Absent / Prohibited Relations

Potentially important but easy to overlook:

- absence of a relation may itself be informative;
- explicit prohibition may differ from mere absence;
- `NOT_RELATED`, `UNKNOWN`, and `PROHIBITED_RELATION` are not equivalent;
- evidence that a relation does not exist is different from failure to observe it.

This parallels AAA evidence discipline: absence of evidence != negative fact.

INIT may need to distinguish at least unknown from explicitly ruled-out relations if the domain requires it.

---

## 10. Perspective / Claim / Reality Separation for Relations

A major candidate separation:

- OBSERVED RELATION: behavior/data indicates a relation;
- CLAIMED RELATION: one participant or authority claims a relation;
- MODEL-INFERRED RELATION: current model infers a relation;
- MUTUALLY RECOGNIZED RELATION: participants/authorities agree;
- DISPUTED RELATION: conflicting claims remain unresolved.

This prevents observer-relative or self-declared meaning from silently becoming shared reality.

Ancestor internal legacy: PCS-SHAI distinction among observed integration, system interpretation, and user-defined status.

---

## 11. Relation and Perspective

Strong next-axis candidate:

> A relation may not be fully meaningful without specifying from whose perspective / under which model / for which purpose it is materialized.

But caution:

`PERSPECTIVE-DEPENDENT MODEL != PERSPECTIVE-CREATED REALITY`

The project must preserve distinction between:

- relational fact/evidence;
- observer/model projection;
- local meaning/interpretation.

This is a likely bridge to the OBSERVER/PERSPECTIVE/PURPOSE research axis.

---

## 12. Relation and Scale

Owner confirms current worldview:

> At each scale there may be useful materialized instances; no scale must be selected as final ontology.

Relation implication:

- relations may transform across scale;
- lower-scale relations can induce higher-scale relations;
- higher-scale relations may not reduce cleanly to one lower-scale edge set;
- scale may therefore be part of relation/materialization context.

Open question:

> Is scale itself a relation/projection, an input parameter, or merely a modeling label?

---

## 13. Process/Event-First Counter-Hypothesis

Strong adversarial alternative:

> Perhaps process/event is more primitive than relation; what ASA-MI calls relation may be a durable summary/projection of repeated interactions/events.

If true:

- store events/processes as base substrate;
- derive relations/materialized instances from them;
- relational constitution may survive only as modeling priority, not base ontology.

This is a high-value Codex comparison target.

---

## 14. Structural Realism / Process Philosophy / Category-Theoretic Style as Ancestor Candidates

Recall-stimulus only; no adoption:

- Buddhist dependent origination: conditional/dependent arising rather than isolated fixed substance;
- structural realism: structure/relations may carry more explanatory weight than intrinsic object essence;
- process philosophy: becoming/process may be more fundamental than enduring substance;
- category-theoretic style: objects can be understood through morphisms/transformations and compositional structure;
- network science / graph/hypergraph: topology/configuration as analytic object;
- relational databases/algebra: relations as first-class data structures;
- materialized views/incremental view maintenance: bounded derived objects and efficient rematerialization;
- mereology/topology: part/whole, interior/boundary/closure abstractions;
- Markov blanket: boundary as dependency-mediating structure;
- autopoiesis: organization maintaining/reproducing its own operational boundary.

Each is an ANCESTOR_CONCEPT candidate, not authority or direct implementation prescription.

---

## 15. Category-Theoretic Recall Stimulus — Composition of Relations/Transformations

Without adopting category theory, a useful stimulus is:

> Perhaps what matters is not only `what is connected to what`, but whether transformations/relations compose coherently.

Potential ASA-MI questions:

- If A relates to B and B to C, when can/should a derived A-C relation exist?
- Are some relation compositions valid while others are prohibited?
- Can succession, merge, fission, membership, authority be composed without semantic leakage?
- Does composition preserve provenance and scope?

This may matter more than graph connectivity alone.

---

## 16. Relation Algebra / Constraint Candidate

Another recall candidate:

> Relations may require composition, inversion, restriction, projection, intersection, conflict, precedence, or constraint operations.

This suggests an eventual `relation algebra` may emerge from real use.

INIT caution:

Do not design the full algebra first. Record only operations needed by actual INIT scenarios and currentize from evidence.

---

## 17. Relation Bundle as Cheap Representation Candidate

Owner explicitly notes that if a tree is cheap and sufficient, a particular network bundle can be represented by the cheaper structure.

Working principle candidate:

`SEMANTIC RELATIONALITY != EXPENSIVE UNIVERSAL GRAPH`

Representation strategy may be selected per bounded bundle based on:

- required semantics;
- query patterns;
- merge/fission needs;
- update frequency;
- replay/provenance;
- cost/latency.

Potential INIT strategy:

- canonical semantic relation contract kept small/open;
- bundle-specific projection chosen cheaply;
- materialized view persisted for current operations;
- exact recipe/input lineage preserved for replay.

---

## 18. The `Everything Is Relation` Failure Mode

Critical falsification risk:

If every phenomenon can always be relabeled as a relation, the hypothesis becomes unfalsifiable and operationally useless.

Therefore Codex should force the project to answer:

- What cannot be represented adequately as relation?
- Which primitive/local states have explanatory value independent of relational configuration?
- What observable result would favor entity/process-first over relational constitution?
- What extra capability does relational constitution provide relative to simpler baselines?

A strong surviving form may be narrower:

> Relation/configuration receives modeling priority where it materially improves explanation, merge/fission, scale, boundary, and recomposition; no universal relation-only ontology is required.

---

## 19. Candidate INIT Decision Principle

Before currentizing a relation concept into INIT, ask:

1. Does this relation concept solve or simplify an actual INIT modeling problem?
2. Is a cheaper representation sufficient?
3. Can it be bounded/materialized without whole-world recomputation?
4. Can provenance/replay be preserved?
5. Can it survive merge/fission/succession without identity hacks?
6. Is the relation semantics distinguishable from claim/inference/evidence?
7. What simpler alternative should it beat?

If the concept is philosophically attractive but non-blocking and implementation-heavy, preserve it as OPEN rather than forcing it into INIT.

---

## 20. Five-Line Summary

현재 상태: Owner는 RELATION을 P0 다음의 가장 중요한 가설축으로 보고 있으며, 많은 Boundary/Membership/Succession/Self/Scale 문제가 관계 문제 안에 속할 가능성을 느끼고 있다.
핵심 판단: RELATION은 단순 binary edge가 아니라 n-ary, role/context/time/scale-sensitive, higher-order, claim/evidence-distinguished family일 가능성을 열되 `everything is relation`의 반증불가능성을 강하게 경계한다.
진행 작업: relation family, bundle/configuration, relation materialization, latent/active relation, perspective/claim separation, scale relation, relation algebra/composition, process/event-first counter-hypothesis, 다양한 ANCESTOR_CONCEPT 후보를 회상 자극으로 정리했다.
다음 단계: Owner가 회상되는/새로 강하게 끌리는/위화감 있는 후보를 구분하면 RELATIONAL CONSTITUTION의 현행 후보를 더 정확히 만들고, 이후 MEMBER/BOUNDARY/OBSERVER 문제를 해당 relation semantics 위에서 재검토한다.
사용자 행동: 이번 후보군을 정답으로 받을 필요 없이 기억을 자극하는 부분과 강하게 현행화하고 싶은 부분만 반응하면 된다. 작성시각: 2026-08-20 16:51 KST
