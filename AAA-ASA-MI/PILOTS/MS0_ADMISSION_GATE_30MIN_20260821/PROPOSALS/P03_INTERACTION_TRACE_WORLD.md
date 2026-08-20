# P03 — Interaction-Trace World

STATE = MODEL_PROPOSAL_ONLY / NOT_ADMITTED / NO_CANDIDATE_STATUS

AUTHOR_SUBMISSION_STATE = SUBMITTED_FOR_FRESH_VALIDATOR_REVIEW

SOURCE_IDEA = I11

## A1. WORLD MODEL THESIS

WHAT_IS_MODELED = What a modeled world can reveal, accept, resist, or leave open through bounded interaction histories, including incompatible observations and future possibilities.

HOW_WORLD_OR_MODEL_STATE_OR_EQUIVALENT_IS_CONSTITUTED = A semantic version defines legal move types and a prefix-closed interaction structure. A current world-equivalent is not a hidden total object snapshot; it is `(history_prefix, admissible_continuations, response_constraints, unresolved_branches)`. Two implementations are equivalent only under a declared observation/interaction equivalence. The thesis is that worldhood for the model is constituted operationally by stable counterfactual interaction possibilities, not only by stored claims or runtime messages.

WORLD_MODEL_BOUNDARY = The proposal includes an environment role and probe roles but does not require human, Persona, or intentional agents. A probe can be a sensor, query, perturbation, or structural operation.

## A2. MATERIAL DISTINCTNESS

NEAREST_PROPOSAL_OR_IDEA = I05 Coinductive Behavioral World; among submitted proposals, P01 is nearest in transition behavior.

EXACT_MATERIAL_DIFFERENCE = P03 treats legal alternating interaction histories and counterfactual continuations as constitutive. A coalgebra/P01 state-transition account starts from states and their successors; P03 may identify no observer-independent current state beyond the constraints imposed by all admissible plays.

DIFFERENT_BEHAVIOR_OR_FAILURE_MODE_CAUSED_BY_DIFFERENCE = P03 can preserve two worlds as distinct when they have the same observed prefix but different possible responses to an unperformed probe. It fails when important persistence or change has no interactionally accessible consequence; P01 can still record that hidden structure.

## A3. COMMITMENT SURFACE

Commitment resides in the move alphabet, role/turn protocol, legal-play relation, response constraints, observation equivalence, fairness assumptions, and the rule for which unperformed counterfactuals count. These choices may hide Perspective, Boundary, or agency. P03 explicitly rejects an ontology-free claim.

## A4. CHANGE / HISTORY

WHAT_CAN_CHANGE = The actual history prefix grows by legal moves; future strategy/continuation space narrows or changes after interaction. A structural intervention move may change later legal responses.

WHAT_HISTORY_REMAINS = The exact typed play prefix, evidence attached to responses, semantic version, and the pre-move continuation digest are append-only.

HOW_PRIOR_STATE_OR_EVIDENCE_IS_RECONSTRUCTED = Historical world-equivalent at move index `k` is the prefix plus the continuation structure version/digest valid then. Later moves do not rewrite what was open at `k`.

HOW_CURRENT_INTERPRETATION_CAN_CHANGE_WITHOUT_RETROACTIVE_REWRITE = A successor move alphabet or equivalence relation is versioned. It may re-project old plays but must retain the old legality/equivalence judgment and disclose any non-translatable move.

## A5. NON-CLOSURE

- UNKNOWN = two or more admissible continuations answer a probe differently, or an `unknown` response is explicitly legal; lack of a performed probe is not false.
- UNDEFINED = no legal interpretation exists for a move under the current protocol; returned with a reason.
- DISPUTED = incompatible evidence-bearing response branches remain live because the protocol supplies no justified resolution.
- MULTIPLE_ADMISSIBLE_ALTERNATIVES = the prefix tree/strategy set itself carries them; pruning requires a recorded move/evidence rule.

## A6. BOUNDED OPERATIONALIZATION

### Interaction-tree micro-probe

```text
Moves by Probe:
  inspect(location, sample)
  perturb(move, sample, chamber)

Responses by Environment:
  at(outside, evidence)
  at(chamber, evidence)
  unknown(reason)
  disputed({response,evidence}...)

Initial legal continuations:
  inspect(location,s1) -> at(outside,e1)
  inspect(location,s1) -> at(chamber,e2)
  inspect(location,s1) -> disputed({outside,e1},{chamber,e2})
```

After actual response `disputed(...)`, both evidence branches remain. A legal perturbation `move(s1,chamber)` changes the continuation structure so a later inspection must return `at(chamber,e3)` unless a declared failure response occurs. Querying the prefix before perturbation still returns the earlier disputed continuation set. Two proposed worlds with the same current response but different allowed post-perturbation responses are not interaction-equivalent.

CORE_SEMANTICS_TOUCHED = open counterfactual continuations, evidence-bearing dispute, intervention-sensitive change, historical prefix, and observational equivalence.

## A7. COMMON QUERY CONTACT

1. WHAT_IS_REPRESENTED_NOW = Reformulated as: which play prefix has occurred, and what responses/interventions remain legal from it?
2. WHAT_CHANGED = Return the latest move and the delta between pre/post admissible continuation sets, with semantic version.
3. WHAT_WAS_REPRESENTED_AT_TIME_T = Return prefix `T` and the continuation digest/structure that was declared then.
4. WHAT_REMAINS_UNRESOLVED = Return probes with divergent live continuations, explicit unknown responses, and disputed response bundles.
5. WHAT_CHANGES_UNDER_ANOTHER_CONTEXT = Reformulated as a different declared probe role/equivalence projection over the same play. Answers include the projection ID and distinctions it hides.
6. WHAT_ASSUMPTIONS_WERE_USED = Return protocol, legality, fairness, response-constraint, and equivalence versions.

## A8. FALSIFICATION / ABANDONMENT

ABANDONMENT_EXPERIMENT = Construct two shared toy worlds that have identical possible interaction traces under the full bounded probe set but must remain materially different for historical reconstruction or future structural behavior. If no additional non-ad-hoc probe distinguishes them, P03's constitution is too weak and must be merged with a substrate model. Also redesign if query answers depend primarily on an arbitrary turn-taking convention rather than modeled phenomena.

## A9. ASSUMPTION REGISTER

| ASSUMPTION_ID | STATEMENT | SOURCE | WHY_NEEDED | WHAT_FAILS_IF_FALSE | REVERSIBILITY |
|---|---|---|---|---|---|
| P03-AS1 | Stable counterfactual interaction possibilities can constitute a useful low-level world-equivalent. | CODEX_PROPOSAL | This is the central thesis. | The model becomes only an observation interface. | Low: failure changes the proposal's identity. |
| P03-AS2 | Probe roles need not imply persons or agents. | MODEL_FAMILY_ASSUMPTION | Supports low-level generality. | The model becomes agent/epistemology-specific. | Medium: replace games with neutral interaction systems. |
| P03-AS3 | Unperformed alternatives should remain open rather than false. | INHERITED_RESEARCH_HYPOTHESIS | Preserves non-closure. | Prefix-tree multiplicity is unnecessary. | High. |
| P03-AS4 | Observation equivalence can be explicit and versioned. | MODEL_FAMILY_ASSUMPTION | Needed for identity/distinctness queries. | Hidden observer ontology dominates. | Medium-low. |
| P03-AS5 | Naming and current vocabulary do not define legal moves. | OWNER_EXPLICIT | Prevents metaphor-driven semantics. | Future primitives require explicit addition. | High. |

## A10. REVISION / SUCCESSOR PATH

Protocol packages contain immutable move/role/legality/equivalence definitions and parent digests. Plays retain their package version. A successor may refine a move, split a role, or change equivalence; mappings are explicit and may be partial. Old open continuations remain inspectable under the old package. A successor cannot retroactively say an old move was illegal without recording that as a new critique/projection.

## A11. NON-TRIVIALITY

P03 calculates legal continuations, strategy compatibility, distinguishability under a probe set, unresolved counterfactual branches, and change induced by intervention. It constrains which responses may follow which histories and can falsify a proposed world when an observed response is illegal. It makes the sufficiency of an observation/probe algebra directly testable rather than implicit.

## A12. LOW-LEVEL GENERALITY

The kernel uses typed interaction, environment responses, legality, histories, and equivalence; no Persona, ASA, memory-agent, workflow, authority, or domain-specific role is required. Sensors, physical perturbations, software calls, and abstract structural queries can all instantiate probes. Nevertheless, low-level generality is a validator-critical risk because interaction may still privilege observer-accessible phenomena.

## AUTHOR SELF-CRITIQUE — ZERO VALIDATION AUTHORITY

AUTHOR_STRONGEST_CASE = P03 converts perspective and observation dependence from an afterthought into a falsifiable account of world distinguishability and change under intervention.

AUTHOR_STRONGEST_OBJECTION = It may be an epistemology or testing interface pretending to be a World Model; inaccessible but causally important structure is difficult to justify internally.

AUTHOR_HIDDEN_COMMITMENT_SUSPECTED = Role alternation, move individuation, fairness, the completeness of the probe set, and the equivalence relation.

AUTHOR_WHAT_MAY_MAKE_THIS_NOT_A_WORLD_MODEL = If all semantics concern what an observer can ask/receive and none constitute the environment beyond interaction records, the proposal belongs above another World Model.

AUTHOR_ABANDONMENT_SIGNAL = Materially different shared scenarios remain interaction-equivalent under every non-ad-hoc bounded probe, or low-level examples require intentional-agent concepts.
