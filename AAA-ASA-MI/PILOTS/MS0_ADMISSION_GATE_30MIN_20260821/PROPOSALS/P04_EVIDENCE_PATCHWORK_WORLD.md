# P04 — Evidence Patchwork World

STATE = MODEL_PROPOSAL_ONLY / NOT_ADMITTED / NO_CANDIDATE_STATUS

AUTHOR_SUBMISSION_STATE = SUBMITTED_FOR_FRESH_VALIDATOR_REVIEW

SOURCE_IDEA = I02

## A1. WORLD MODEL THESIS

WHAT_IS_MODELED = Evidence-bearing local descriptions of modeled situations, their dependencies and incompatibilities, historical transformations, and the family of currently supportable materializations.

HOW_WORLD_OR_MODEL_STATE_OR_EQUIVALENT_IS_CONSTITUTED = An immutable patch declares a typed payload, applicability interval/context, dependencies, conflicts, and provenance. The world-equivalent is not the patch database itself; it is `Materializations(P, compatibility_v, selection_assumptions)`: the family of maximal or query-bounded compatible patch compositions plus explicitly unplaced patches. A materialization is always accompanied by the patch set and semantic policy that produced it.

WORLD_MODEL_CLAIM = P04 proposes that no unsupported complete state is primary: world constitution for modeling is the structured space of evidence-compatible partial constructions. This deliberately tests the boundary between epistemic ledger and World Model.

## A2. MATERIAL DISTINCTNESS

NEAREST_PROPOSAL_OR_IDEA = I04 Constraint Ensemble; among submissions, P01 Algebraic Rewrite World.

EXACT_MATERIAL_DIFFERENCE = P04 composes immutable, provenance-bearing local patches and permits incompatible materializations. It has no required global constraint theory or single configuration transition law. P01 starts with a global term and rules; I04 starts with constraints and all satisfying global assignments.

DIFFERENT_BEHAVIOR_OR_FAILURE_MODE_CAUSED_BY_DIFFERENCE = P04 can retain evidence that fits no current materialization and explain each local composition. It may fail to infer global consequences that a constraint solver derives, and patch compatibility may become pairwise/local where the real conflict is global.

## A3. COMMITMENT SURFACE

Commitment resides in patch types/payload schema, patch individuation, dependency/conflict semantics, applicability context, compatibility algorithm, maximality/query-bounding policy, and projection rules. Provenance is not neutral: decisions about what counts as a patch or conflict may relocate entity, event, relation, time, and authority assumptions.

## A4. CHANGE / HISTORY

WHAT_CAN_CHANGE = New patches may assert observations or transformations; successor policy versions may change compatibility/materialization. Existing patches are not mutated.

WHAT_HISTORY_REMAINS = Patch payloads, provenance, dependency/conflict edges, ingestion order where meaningful, and policy versions are content-addressed. A transformation patch refers to before/after conditions without requiring Event as a universal primitive.

HOW_PRIOR_STATE_OR_EVIDENCE_IS_RECONSTRUCTED = Evaluate only patches available at cutoff `T` under the policy version active then. Return all compatible materializations or a query-bounded subset plus completeness status.

HOW_CURRENT_INTERPRETATION_CAN_CHANGE_WITHOUT_RETROACTIVE_REWRITE = A new compatibility or projection policy recomputes a new materialization family while the earlier family/digest and evidence remain. Cross-version answers expose policy differences.

## A5. NON-CLOSURE

- UNKNOWN = no applicable patch determines the query and the query domain is open; not false/absent.
- UNDEFINED = the query has no interpretation under the selected patch schemas/policy.
- DISPUTED = supported patches give incompatible answers and remain in different materializations or an explicit conflict set.
- MULTIPLE_ADMISSIBLE_ALTERNATIVES = multiple compatible materializations answer differently.
- ORPHANED = a patch lacks satisfied dependencies; it is preserved but cannot currently participate.

## A6. BOUNDED OPERATIONALIZATION

### Patch-composition micro-probe

```text
p1: claim location(s1)=outside, provenance=e1, applies=t0..t2
p2: claim location(s1)=chamber, provenance=e2, applies=t1..t2
p3: transform move(s1,outside->chamber), depends={p1}, provenance=e3, at=t1
p4: claim integrity(s1)=unknown, provenance=e4, applies=t1

compatibility_v1:
  p1 and p2 conflict at overlapping time unless a transformation patch
  orders the values and satisfies its before-condition.
```

Without `p3`, materializations include `{p1,p4}` and `{p2,p4}`, with location disputed. With valid `p3`, the time-indexed composition `{p1,p3,p2,p4}` supports outside-before/chamber-after while integrity remains explicitly unknown. If `p3`'s before-condition is not supported, `p3` is orphaned and cannot silently resolve the dispute. Re-evaluating under `compatibility_v2` does not alter any patch or the recorded v1 result.

CORE_SEMANTICS_TOUCHED = local evidence composition, conflict, dependency, transformation, multiple materializations, unresolved status, and policy-versioned reinterpretation.

## A7. COMMON QUERY CONTACT

1. WHAT_IS_REPRESENTED_NOW = Return the query-bounded compatible materializations at the declared cutoff/policy, plus completeness and orphan/conflict sets.
2. WHAT_CHANGED = Return new patches and the delta in materialization membership/explanations; a new interpretation policy is reported separately from world-facing evidence.
3. WHAT_WAS_REPRESENTED_OR_CLAIMED_AT_TIME_T = Evaluate the patch cutoff and historical policy; distinguish available claims from supportable materializations.
4. WHAT_REMAINS_UNRESOLVED = Return queries with divergent materializations, unknown patches, missing dependencies, and explicit conflicts.
5. WHAT_CHANGES_UNDER_ANOTHER_CONTEXT = Filter/project by declared applicability context, recompute compatibility, and report excluded patches and policy.
6. WHAT_ASSUMPTIONS_WERE_USED = Return compatibility, selection/maximality, cutoff, context, schema, and closed/open-domain assumptions.

## A8. FALSIFICATION / ABANDONMENT

ABANDONMENT_EXPERIMENT = Apply P04 to a shared causal fission/merge scenario and a continuous-change scenario. If correct answers require a hidden global state/solver not expressible through patch composition, P04 is an evidence layer and should be merged under another World Model rather than admitted alone. If small patch sets yield intractably many materializations before representing non-trivial structure, materially weaken or reject the family.

## A9. ASSUMPTION REGISTER

| ASSUMPTION_ID | STATEMENT | SOURCE | WHY_NEEDED | WHAT_FAILS_IF_FALSE | REVERSIBILITY |
|---|---|---|---|---|---|
| P04-AS1 | Evidence-compatible partial constructions can constitute the modeled world-equivalent without a privileged complete state. | CODEX_PROPOSAL | Central world-model thesis. | P04 becomes only a ledger feeding another model. | Low. |
| P04-AS2 | Relevant evidence can be individuated into immutable typed patches. | MODEL_FAMILY_ASSUMPTION | Enables provenance and recomposition. | Patch boundaries distort continuous/holistic phenomena. | Medium-low: successor can aggregate/split with mappings. |
| P04-AS3 | Historical evidence must survive changing interpretation. | INHERITED_RESEARCH_HYPOTHESIS | Supports non-retroactive currentization. | Versioning/materialization history is unnecessary. | High. |
| P04-AS4 | Compatibility and selection assumptions can be exposed and versioned. | MODEL_FAMILY_ASSUMPTION | Prevents hidden conflict resolution. | Ontology remains buried in code. | Medium. |
| P04-AS5 | UNKNOWN must not be inferred from mere patch absence without open-domain metadata. | CODEX_PROPOSAL | Separates no evidence from known absence. | Query semantics become unsafe. | High. |

## A10. REVISION / SUCCESSOR PATH

Patch schemas and compatibility/materialization policies are immutable versioned packages with parent digests and migration maps. Old patches never receive new payload meaning in place. A successor may split patch types, change applicability, or replace compatibility; it records a successor patch or translation view and may mark `UNTRANSLATABLE`. Prior materialization families and policy digests remain reproducible.

## A11. NON-TRIVIALITY

P04 calculates compatible evidence compositions, minimal conflict sets, dependency closure, orphaned evidence, alternative materializations, and explanation/provenance for query answers. It constrains resolution: an unsupported transformation cannot reconcile incompatible claims. It discriminates an evidence update from a policy reinterpretation and makes combinatorial/materialization failure measurable.

## A12. LOW-LEVEL GENERALITY

The kernel contains patches, applicability, dependency/conflict, compatibility, provenance, and materialization. It does not contain Persona, ASA, agent memory, workflows, authority roles, or application schemas. Patches may describe physical, social, computational, or abstract modeled situations. The validator must still decide whether evidence-constitution is sufficiently world-level.

## AUTHOR SELF-CRITIQUE — ZERO VALIDATION AUTHORITY

AUTHOR_STRONGEST_CASE = P04 makes historical evidence, non-closure, alternative current constructions, and interpretation revision first-class while preventing unsupported complete-state fabrication.

AUTHOR_STRONGEST_OBJECTION = It may precisely model claims/evidence and still fail to model the world; `Materializations(...)` could be an epistemic product requiring another substrate to supply dynamics and ontology.

AUTHOR_HIDDEN_COMMITMENT_SUSPECTED = Patch boundaries, compatibility locality, time/applicability schema, maximality policy, and provenance authority.

AUTHOR_WHAT_MAY_MAKE_THIS_NOT_A_WORLD_MODEL = If every patch payload presupposes externally defined entities, change, and causal semantics, P04 is a versioned evidence integration layer.

AUTHOR_ABANDONMENT_SIGNAL = Shared scenarios need a hidden global solver/state, or patch materialization explodes before producing world-level structural leverage.
