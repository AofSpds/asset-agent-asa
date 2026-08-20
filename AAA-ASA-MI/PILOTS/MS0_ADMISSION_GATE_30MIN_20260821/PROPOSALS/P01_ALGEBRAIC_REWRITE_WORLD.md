# P01 — Algebraic Rewrite World

STATE = MODEL_PROPOSAL_ONLY / NOT_ADMITTED / NO_CANDIDATE_STATUS

AUTHOR_SUBMISSION_STATE = SUBMITTED_FOR_FRESH_VALIDATOR_REVIEW

SOURCE_IDEA = I01

## A1. WORLD MODEL THESIS

WHAT_IS_MODELED = Finite modeled situations, the structures present in them, explicit unresolved alternatives, and the lawful ways those situations may transform.

HOW_WORLD_OR_MODEL_STATE_OR_EQUIVALENT_IS_CONSTITUTED = At semantic version `v`, a model state is an algebraic term `W : World_v` modulo declared equations `E_v`. A rule set `R_v` defines permitted successor terms. Thus the proposal is more than a storage structure: `(<signature, equations, rules>, current term, trace)` states what configurations mean, when two configurations count as equivalent, and which changes are lawful. Predicates such as Event or Relation are optional constructors, not mandatory primitives.

WORLD_MODEL_CLAIM = Worldhood is constituted by an explicit configuration language plus transformation semantics and observational queries over reachable configurations. The proposal makes no claim that reality itself is literally a term-rewriting system.

## A2. MATERIAL DISTINCTNESS

NEAREST_PROPOSAL_OR_IDEA = I09 / P02 Resource-Flow Net.

EXACT_MATERIAL_DIFFERENCE = P01 permits arbitrary typed structural rewrite of nested configurations modulo equations. P02 permits only enabled resource-flow transitions over a declared net and marking, with native concurrency/conservation structure.

DIFFERENT_BEHAVIOR_OR_FAILURE_MODE_CAUSED_BY_DIFFERENCE = P01 can express creation, deletion, nesting change, fission, or schema-version translation directly but risks rule overlap/non-confluence. P02 detects resource impossibility and independent concurrency directly but requires net redesign for arbitrary structural change.

## A3. COMMITMENT SURFACE

Semantic commitment resides in:

- the term signature and sorts;
- equations deciding equivalence;
- rewrite-rule left/right sides and conditions;
- rule priority or nondeterminism policy;
- observation/query functions;
- the choice of what is recorded in the transition trace.

The proposal is not ontology-free. It relocates ontology into an inspectable, versioned algebra and transformation law.

## A4. CHANGE / HISTORY

WHAT_CAN_CHANGE = Any configuration fragment matched by a declared rule, including nested composition and the set of unresolved alternatives.

WHAT_HISTORY_REMAINS = An append-only trace records `(pre_term_digest, rule_id, binding, evidence_refs, post_term_digest, semantic_version)`; initial term and rule package are content-addressed.

HOW_PRIOR_STATE_OR_EVIDENCE_IS_RECONSTRUCTED = Replay uses the historical `signature_v/E_v/R_v` and initial term. Each post-term digest is checked during replay. Nondeterministic choice records the selected rule/binding without claiming alternative branches never existed.

HOW_CURRENT_INTERPRETATION_CAN_CHANGE_WITHOUT_RETROACTIVE_REWRITE = A successor interpreter may map old terms into a new signature through an explicit, versioned translation. Old traces continue to answer historical queries under old semantics; cross-version queries disclose the translation used.

## A5. NON-CLOSURE

The signature contains explicit constructors rather than using absence:

`unknown(q)` = no admitted determination for question `q`.

`undefined(q, reason)` = the current signature says the question lacks a denotation.

`disputed(q, {support_i})` = incompatible supported alternatives remain present.

`alternatives(q, {a1..an}, open_tail)` = multiple admissible values; `open_tail=true` says the list is non-exhaustive.

No generic query may coerce these constructors to `false`, `absent`, or null.

## A6. BOUNDED OPERATIONALIZATION

### Formal micro-probe

Signature fragment:

```text
World ::= world(Cells, Questions)
Cell  ::= cell(Id, Phase)
Phase ::= stable | split_pending | retired
QVal  ::= known(Value, Evidence)
        | unknown(Question)
        | disputed(Question, Supports)
```

Rules:

```text
R1 request_split:
  cell(x, stable) => cell(x, split_pending)

R2 complete_split:
  cell(x, split_pending)
  => cell(x1, stable) cell(x2, stable) cell(x, retired)
  if fresh(x1, x2) and lineage(x, [x1, x2]) is recorded

R3 observe_phase:
  unknown(phase(x)) => known(phase(x), e)

R4 conflicting_observation:
  known(q, e1) + observation(q, incompatible_value, e2)
  => disputed(q, {support(existing_value,e1), support(incompatible_value,e2)})
```

Start:

`W0 = world({cell(a,stable)}, {unknown(phase(a))})`

Trace `R1(a); R2(a→a1,a2); R3(phase(a1),stable,e7); R4(phase(a1),retired,e8)` yields a configuration containing the preserved retired predecessor, two successor cells, and an explicit dispute for `phase(a1)`. Replay at the state before `R2` reconstructs `cell(a,split_pending)` without applying the later interpretation.

CORE_SEMANTICS_TOUCHED = typed constitution, lawful structural change, branching succession record, replay, and non-explosive disagreement.

## A7. COMMON QUERY CONTACT

1. WHAT_IS_REPRESENTED_NOW = Return the current normalized term plus the signature/equation version; normalization must not erase unresolved constructors.
2. WHAT_CHANGED = Return the trace suffix with rule IDs, bindings, and pre/post digests; semantic diff is computed under the rule version used.
3. WHAT_WAS_REPRESENTED_AT_TIME_T = Replay or retrieve the content-addressed term at trace position `T` using the historical semantic version.
4. WHAT_REMAINS_UNRESOLVED = Pattern-match `unknown`, `undefined`, `disputed`, and open `alternatives` constructors and return evidence references.
5. WHAT_CHANGES_UNDER_ANOTHER_CONTEXT = This question is reformulated as `observe(term, observation_algebra_id)`. The answer includes the algebra ID; P01 does not make Context a primitive.
6. WHAT_ASSUMPTIONS_WERE_USED = Return signature, equation, rule, query, and translation version IDs plus rule conditions invoked.

## A8. FALSIFICATION / ABANDONMENT

ABANDONMENT_EXPERIMENT = Implement the micro-probe plus a common context-change scenario under two independently authored observation algebras. If routine queries require scanning opaque rule traces, or materially different states normalize as equal only because equations hide the distinction, P01 requires major redesign. If every alternative proposal can be encoded only by replacing the entire signature/rule package, its claimed semantic leverage is too generic and it should be kept as a metalanguage rather than a World Model.

## A9. ASSUMPTION REGISTER

| ASSUMPTION_ID | STATEMENT | SOURCE | WHY_NEEDED | WHAT_FAILS_IF_FALSE | REVERSIBILITY |
|---|---|---|---|---|---|
| P01-AS1 | A bounded situation can be represented as a finite typed term for pilot purposes. | MODEL_FAMILY_ASSUMPTION | Enables matching, replay, and queries. | Core operationalization becomes non-finite or requires an external substrate. | Medium: replace term carrier in a successor, retaining traces through translation. |
| P01-AS2 | Lawful change can be expressed as explicit local rewrites. | MODEL_FAMILY_ASSUMPTION | Supplies transition semantics. | Important continuous/global change becomes distorted. | Medium-low: rule semantics are central, so failure likely triggers redesign. |
| P01-AS3 | Historical semantics and current semantics must remain separately inspectable. | INHERITED_RESEARCH_HYPOTHESIS | Prevents retrospective rewrite. | Versioned replay is unnecessary overhead. | High: history fields may be demoted without erasing old records. |
| P01-AS4 | Unresolved statuses should be explicit constructors, not missing values. | CODEX_PROPOSAL | Prevents closure by host language defaults. | Constructor set may misclassify domain-specific uncertainty. | High: constructors are versioned and extensible. |
| P01-AS5 | No current research vocabulary is required as a primitive. | OWNER_EXPLICIT | Preserves semantic openness. | A mandatory primitive may later prove necessary. | High: add it in a successor signature with provenance. |

## A10. REVISION / SUCCESSOR PATH

Each semantic package has `MODEL_VERSION`, parent version(s), signature/equation/rule digests, declared breaking changes, and translation functions where meaningful. Old terms and traces remain content-addressed under their original package. A successor may split a constructor, retire a rule, or change equivalence; it must record translation loss and may declare `NO_TOTAL_TRANSLATION`. Normal evolution never overwrites an old term or relabels an old transition as if the new rule existed then.

## A11. NON-TRIVIALITY

P01 calculates reachability, enabled transformations, normal forms where they exist, trace-based historical states, explicit divergent branches, and equation-based equivalence. It constrains change to declared rules and makes confluence/critical-pair failures testable. It can discriminate whether two apparent histories lead to equivalent configurations and whether a proposed transformation is lawful under a versioned semantics.

## A12. LOW-LEVEL GENERALITY

The proposal requires only typed configurations, transformation laws, unresolved constructors, and observations. It contains no Persona, ASA, agent-memory, workflow, authority, investment, or naming-specific primitive. Cells in the probe are generic modeled structures. Persona/ASA could later be expressed only as domain terms, not as the semantic foundation.

## AUTHOR SELF-CRITIQUE — ZERO VALIDATION AUTHORITY

AUTHOR_STRONGEST_CASE = P01 provides an executable semantic kernel in which constitution, change, history, non-closure, and revision are all explicit and versioned.

AUTHOR_STRONGEST_OBJECTION = Rewriting logic may be a universal formal language that gains apparent generality by forcing every real semantic choice into an arbitrary signature and rule set.

AUTHOR_HIDDEN_COMMITMENT_SUSPECTED = Discreteness, finite term boundaries, rule-local change, and the normalizer's equivalence policy.

AUTHOR_WHAT_MAY_MAKE_THIS_NOT_A_WORLD_MODEL = If the algebra merely hosts a separately designed ontology and offers no stable cross-domain constraints, it is a modeling framework/metalanguage rather than a model of world constitution.

AUTHOR_ABANDONMENT_SIGNAL = Common scenarios repeatedly require opaque external solvers or whole-package replacement, leaving rewrite reachability with no distinctive explanatory or discriminating value.
