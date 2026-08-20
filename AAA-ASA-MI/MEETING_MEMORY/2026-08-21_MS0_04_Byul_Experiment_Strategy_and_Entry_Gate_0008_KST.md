# MS0-04 — 별 Experiment Strategy and Entry Gate

TIME = 2026-08-21 00:08 KST
STATE = WORKING_RESEARCH_MEMORY / MS0_STAGE_DESIGN / NON_NORMATIVE

PROJECT CONTEXT =
- World Model naming candidate: 한알
- MS0 working milestone name: ONTOGENESIS
- MS0 narrative codename: FIAT LUX / 빛이 있으라
- First implementation artifact naming candidate: 별
- `별` current meaning: first implementation artifact / 구현체; NOT necessarily Instance/Event/Relation/etc.
- Candidate tournament target: 8 serious candidates; minimum 6
- Main Round: common viability pressure test
- Finalists: Positive Finalist + Robustness Finalist, selected only from Main Round passers
- MS0-03: independently concretize both finalists and compare them under the same toy worlds and probes

NOT:
- Requirement
- Design Contract
- Canonical ontology
- Final 한알 model selection
- Production architecture
- 별 implementation authorization
- Validation receipt
- Owner acceptance

## 0. Purpose

MS0-04 decides WHAT IMPLEMENTATION EXPERIMENT SHOULD COME NEXT after the MS0-03 Final Round.

The purpose is NOT to declare a winner.

The purpose is to choose the next experiment that maximizes useful learning while minimizing premature semantic commitment, implementation waste and accidental ontology freeze.

A model may be worth implementing because:
- it has extraordinary upside,
- it has unusually low downside,
- it is the best discriminator against its finalist opponent,
- or implementing both reveals something neither paper comparison can show.

Conversely, even a strong finalist should NOT be implemented as `별` if a much cheaper discriminating probe can resolve the dominant uncertainty first.

Primary optimization target:

`INFORMATION_GAIN / IRREVERSIBLE_SEMANTIC_COMMITMENT`

with implementation cost and elapsed time as important but secondary constraints.

This expression is a research heuristic, NOT a literal scalar score requirement.

## 1. Entry condition

MS0-04 starts only when MS0-03 has produced:

- POSITIVE_FINALIST_REFERENCE_CANDIDATE,
- ROBUSTNESS_FINALIST_REFERENCE_CANDIDATE,
- same-world comparison results,
- Positive Final Round findings for both,
- Negative Final Round findings for both,
- SHARED_FAILURE_REGISTER,
- NON_OVERLAPPING_VALUE_REGISTER,
- ASSUMPTION_REGISTERS for both finalists,
- OPEN_SURFACES for both finalists,
- `IF_THIS_MODEL_IS_USED_FOR_BYUL` proposal for each finalist,
- Final Round comparison meeting memory.

If these are materially incomplete, MS0-04 should not invent the missing comparison evidence.

## 2. Core decision principle

The next step is chosen by LEARNING VALUE, not prestige.

Do NOT ask only:
`Which finalist is better?`

Ask:
`What experiment will most efficiently tell us which model direction is more useful, what assumptions are wrong, or what new model is needed?`

Therefore:

MODEL_RANKING
!=
IMPLEMENTATION_PRIORITY

A lower-ranked model may be the better experiment if it creates stronger discrimination.

## 3. Permitted MS0-04 outcomes

MS0-04 may choose exactly one strategy state for the next step.

### STRATEGY A — SINGLE_BYUL_POSITIVE

Implement one bounded `별` using the Positive Finalist.

Appropriate when:
- its unique upside is the dominant unresolved opportunity,
- its main risks cannot be resolved without implementation,
- Robustness Finalist adds little incremental learning for the immediate experiment,
- implementation remains bounded and reversible.

### STRATEGY B — SINGLE_BYUL_ROBUSTNESS

Implement one bounded `별` using the Robustness Finalist.

Appropriate when:
- a conservative baseline is needed first,
- the Positive Finalist's additional machinery is not yet justified,
- Robustness implementation can falsify or validate important minimum assumptions,
- the experiment can establish a clean reference baseline for later comparison.

### STRATEGY C — DUAL_BYUL_COMPARATIVE

Implement two bounded variants against the same experiment contract.

Working labels MAY be:
- 별-P = Positive Finalist implementation variant
- 별-R = Robustness Finalist implementation variant

These labels are experimental and do NOT create permanent ontology classes.

Appropriate when:
- both finalists remain genuinely viable,
- they make materially different claims,
- the differences are observable in executable behavior,
- implementation costs are bounded enough that comparison is worth more than sequential speculation.

### STRATEGY C2 — STAGED_DUAL_BYUL

Implement one finalist first as an explicit baseline, then the other only if predefined continuation criteria are met.

Appropriate when:
- dual comparison has high learning value,
- but full parallel implementation is unnecessarily expensive,
- one candidate can cheaply establish test fixtures / instrumentation / common scenario harness without semantically privileging itself.

The first implementation does NOT become canonical merely because it is built first.

### STRATEGY D — CHEAP_DISCRIMINATING_PROBE_FIRST

Do NOT build `별` yet.

Run one or more bounded probes targeted at the highest-impact unresolved assumption(s).

Appropriate when:
- one cheap test could materially reorder finalist preference,
- both finalists depend on the same unresolved assumption,
- implementation would otherwise encode an avoidable semantic guess.

### STRATEGY E — RETURN_TO_MODEL_SEARCH

Do NOT build `별` yet.

Return to divergence/model-family search.

Appropriate when:
- both finalists share the same blocking failure,
- both require the same unacceptable hidden assumption,
- both fail the same critical behavior,
- or MS0-03 reveals that the candidate family set omitted an important alternative.

This is not failure of MS0.
It is a valid research result.

## 4. Decision dimensions

Every permitted strategy must be evaluated on the SAME dimensions.

### D1. DISCRIMINATION POWER

How strongly can the experiment distinguish the two finalist hypotheses or eliminate a major assumption?

### D2. FALSIFICATION VALUE

Can the experiment produce an outcome that would materially weaken the chosen model direction?

A demo that can only succeed is not enough.

### D3. UNIQUE LEARNING VALUE

What can be learned only by this strategy and not by the cheaper alternatives?

### D4. ASSUMPTION EXPOSURE

Does the experiment make hidden/expensive assumptions observable?

### D5. SEMANTIC REVERSIBILITY

If the experiment fails, can its semantic decisions be discarded without forcing historical rewrite or broad migration?

### D6. IMPLEMENTATION BOUNDEDNESS

Can the experiment remain small enough to be a research artifact rather than becoming infrastructure construction?

### D7. COMPARABILITY

If comparing models, are the input scenarios, query contracts and evidence capture sufficiently common to make the comparison meaningful?

### D8. ONTOLOGY-FREEZE RISK

Will coding convenience accidentally transform a working hypothesis into a de facto canonical ontology?

### D9. SHARED-FAILURE RESOLUTION

Does the strategy directly attack any failure observed in both finalists?

### D10. FORWARD RELEVANCE

Does the experiment teach something useful for later richer implementation, including eventual Persona work, without making Persona/ASA the low-level model's ontology?

Future relevance is allowed.
Overfitting 한알 to ASA is not.

## 5. Strategy evaluation must preserve two-sided evidence

Apply separate strategy-level filters:

### POSITIVE_EXPERIMENT_FILTER
Record:
- information upside,
- falsification opportunity,
- simplification opportunity,
- reusable experimental infrastructure,
- new questions unlocked.

### NEGATIVE_EXPERIMENT_FILTER
Record:
- accidental semantic commitment,
- sunk-cost risk,
- implementation complexity,
- comparison contamination,
- misleading demo risk,
- assumptions that become harder to reverse after code exists.

Do NOT average these into one opaque score.

Reconcile only after both sides are visible.

## 6. Cheap discriminator rule

Before authorizing any `별` strategy, inspect the finalist Assumption Registers and Final Round comparison.

Create a `CHEAP_DISCRIMINATOR_REGISTER`.

For every high-impact unresolved difference, record:
- question,
- finalist P position,
- finalist R position,
- evidence currently available,
- cheapest discriminating probe,
- estimated information value,
- whether result could change implementation strategy,
- estimated implementation effort,
- reversibility.

Rule:

IF a materially strategy-changing question can be tested much more cheaply than building `별`,
THEN STRATEGY D should receive strong preference.

Do not build first and reason later merely because coding is available.

## 7. Common `별` experiment contract

If any `별` implementation is chosen, define an IMPLEMENTATION-NEUTRAL experiment contract before coding.

The contract should include:

### 7.1 SCOPE
- exact research question,
- exact behaviors in scope,
- exact behaviors deliberately out of scope.

### 7.2 COMMON SCENARIOS
Use a bounded subset derived from the Final Round toy worlds, such as:
- currentization without historical rewrite,
- non-closure / disputed information,
- one structural transformation,
- one declared view/scope/scale change where applicable.

### 7.3 COMMON QUERY PACK
Where semantically valid, both implementations should answer comparable questions.

If a finalist rejects a question's framing, it must expose its alternative query semantics explicitly.

### 7.4 EVIDENCE CAPTURE
Capture at minimum:
- input facts/events/records/other substrate,
- transformation/update operations,
- model outputs,
- historical reconstruction output,
- unresolved/disputed state output,
- assumptions activated,
- errors/failures,
- execution cost proxies where useful.

### 7.5 FALSIFICATION CONDITIONS
Before coding, state what evidence would count against the model.

Do not define success only after results are observed.

## 8. `별` is a research artifact, not a semantic authority

Important:

`IMPLEMENTED`
!=
`TRUE`
!=
`CANONICAL`
!=
`FROZEN`

A successful `별` shows only that a bounded implementation behaved usefully under declared assumptions and tests.

It does not prove:
- the final ontology of 한알,
- metaphysical correctness,
- life/consciousness claims,
- Persona semantics,
- production readiness.

If two `별` variants are created, neither becomes primary merely because it was implemented first or has more code.

## 9. Implementation contamination control

If STRATEGY C or C2 is chosen:

- keep core model-specific logic separate,
- share only experiment-neutral fixtures/harnesses where possible,
- do not share semantic code merely to reduce duplication,
- record any shared abstraction and verify that it does not silently privilege one model,
- preserve candidate-specific assumptions separately.

Otherwise the comparison can collapse into two adapters over one hidden ontology.

## 10. Required outputs

MS0-04 must produce:

### 10.1 IMPLEMENTATION_STRATEGY_DECISION_RECORD
Include:
- selected strategy,
- alternatives considered,
- decisive evidence,
- unresolved assumptions,
- why this strategy has the best expected learning value,
- what would cause reconsideration.

This is a research decision record, NOT a final model approval.

### 10.2 CHEAP_DISCRIMINATOR_REGISTER
As defined above.

### 10.3 BYUL_EXPERIMENT_CONTRACT
Only if a `별` implementation strategy is selected.

### 10.4 FALSIFICATION_PLAN
For every model actually implemented.

### 10.5 ASSUMPTION_FREEZE_AVOIDANCE_REGISTER
List semantic choices that implementation must NOT silently hard-code as project truth.

### 10.6 MS0-04 STAGE MEETING MEMORY
Record:
- entering finalist state,
- strategy candidates,
- positive experiment findings,
- negative experiment findings,
- cheap discriminators considered,
- selected strategy and why,
- rejected strategies and why,
- open questions,
- what MS0/`별` handoff must inherit.

Do not expose private chain-of-thought.
Preserve reviewable decisions, evidence, assumptions and alternatives.

## 11. Decision rules

Use these as directional rules, not blind automation.

### Rule A — Choose D before implementation when cheap information dominates
If a cheap discriminator can resolve a dominant uncertainty with materially less commitment, prefer D.

### Rule B — Choose C when the difference itself is the experiment
If both finalists are implementable and their disagreement is only observable through execution, prefer comparative implementation.

### Rule C — Choose C2 when comparison is valuable but parallel duplication is wasteful
Use staged dual implementation with predefined continuation criteria.

### Rule D — Choose A or B only when a single implementation preserves most relevant learning
Do not choose a single model simply because it ranked first on one axis.

### Rule E — Choose E when both finalists fail for the same deep reason
Do not patch both with the same unproven assumption just to reach coding.

## 12. Suggested decision preference under genuine uncertainty

If MS0-03 ends with two strong, materially different, bounded finalists AND there is no cheap discriminator that dominates implementation,
then the default research preference should lean toward:

`DUAL_BYUL_COMPARATIVE`
or
`STAGED_DUAL_BYUL`

because the project explicitly preserved two finalist extremes in order to learn from their contrast.

This is a working research preference, NOT Owner authorization.

## 13. MS0-04 Exit condition

MS0-04 is complete when:

1. all cheap discriminators have been considered,
2. one next-step strategy is explicitly chosen,
3. the decision is supported by MS0-03 evidence rather than model aesthetics,
4. alternative strategies and rejection reasons remain recorded,
5. implementation does not silently freeze open semantics,
6. if `별` is to be built, its experiment contract and falsification plan are ready,
7. Owner/ASA-MI can review the exact experiment before implementation begins.

## 14. Relationship to MS0 closure

MS0-04 is intended to be the last substantive experiment-strategy design stage BEFORE the first `별` implementation milestone begins.

Recommended sequence:

MS0 — ONTOGENESIS / FIAT LUX
→ model-space reconstruction / tournament / final round / experiment-strategy decision
→ MS0 closure packet
→ `별` first implementation milestone

Whether an additional tiny `MS0-05 CLOSURE / HANDOFF` bookkeeping stage is useful remains OPEN.

No extra stage should be created merely for ceremony.

## 15. Current status

This is stage planning only.

No implementation strategy has been selected yet.
No `별` implementation is authorized by this note.
No final 한알 model has been selected.

작성시각: 2026-08-21 00:08 KST
