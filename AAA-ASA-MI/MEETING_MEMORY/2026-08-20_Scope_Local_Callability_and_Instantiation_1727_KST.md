# AAA-ASA-MI Meeting Memory

## Title
Scope-local Callability / Instantiation / Rendering Analogy Clarification

## Date / Time
2026-08-20 17:27 KST

## Status
WORKING_RESEARCH_CONTEXT / BRAINSTORM / RELATIONAL_CONSTITUTION / INIT_CURRENTIZATION_PREPARATION

## Purpose
Preserve Owner's simplification of the earlier `future reachability / operational absence` hypothesis into a cheaper bounded-scope representation, and clarify the rendering analogy so it is useful without silently equating rendering exclusion with physical memory absence.

This record is NOT a Requirement, Design Contract, Frozen Artifact, Final Ontology, Validation Receipt, Independent Validation PASS, or Final Truth.

---

## 1. Owner Simplification — Do Not Prove All Future Possibilities

Owner proposed avoiding the expensive requirement to prove that an element can never interact again under every imaginable future.

Instead, define the result relative to the current bounded scope / current model state.

Working intuition:

> In the STATUS of this scope, the object/member is not callable.

Because bare `STATUS` is overloaded elsewhere in ASA-MI, a more explicit technical term should be researched for this dimension, e.g. `CALLABILITY`, `MATERIALIZATION_ELIGIBILITY`, `IN_SCOPE_REACHABILITY`, or a scoped relation-result field.

Core idea:

`NOT CALLABLE IN CURRENT SCOPE`

is cheaper and more implementable than:

`PROVEN IMPOSSIBLE TO INTERACT FOR ALL FUTURE STATES`.

This turns the problem from metaphysical/global nonexistence proof into bounded operational evaluation.

---

## 2. Candidate Distinction — Existence vs Scope-local Instantiation

Potential layered interpretation:

1. a reference / primitive / source object may exist in the broader substrate;
2. the current scope may judge it not callable / not relevant / not materialization-eligible;
3. therefore it is not instantiated/materialized into the current operational instance;
4. another scope or successor state may materialize it later if callability/relevance changes.

This preserves P0 mutability and avoids deleting history or substrate merely because the object is not part of the current materialization.

Working distinction:

`NOT MATERIALIZED IN SCOPE != GLOBAL NONEXISTENCE`

and

`CURRENTLY MATERIALIZED != PERMANENT ESSENCE`.

---

## 3. Rendering Analogy — Useful but Must Be Technically Scoped

Owner proposed a rendering analogy:

- a rendered object corresponds to an instantiated/materialized object in the active view;
- an object unrelated to the current camera/view corresponds to an object that is not instantiated/materialized in that active view.

The analogy is useful at the abstraction layer:

`SCENE / SUBSTRATE`
→ view/scope relevance evaluation
→ culling / selection
→ active rendered/materialized set.

Technical caution:

In real graphics systems, an object that is culled from rendering is NOT necessarily absent from CPU/GPU memory. Frustum/occlusion culling can simply skip draw/processing work while scene records or geometry remain resident. More advanced streaming systems may also avoid or evict memory residency for non-needed assets, but this is a separate optimization dimension.

Therefore ASA-MI should distinguish at least conceptually:

- `SUBSTRATE_EXISTS / REFERENCEABLE`
- `IN_SCOPE_CALLABLE / MATERIALIZATION_ELIGIBLE`
- `MATERIALIZED / ACTIVE`
- `RUNTIME_RESIDENT / LOADED`

Do not collapse these into one state merely because the rendering metaphor is intuitive.

---

## 4. Important Consequence for RELATIONAL CONSTITUTION

This suggests a cheaper operational interpretation of relational existence:

> An element need not be globally declared nonexistent when relations disappear. The current scope can simply evaluate it as non-callable / non-participating and exclude it from the current materialized instance.

This makes Relation-first modeling more implementable because the system need only decide:

`Should this element participate in this bounded materialization now?`

rather than:

`Can this element ever interact again in all possible future worlds?`

---

## 5. Candidate Function / Rule Shape

Very loose conceptual sketch only:

`CALLABILITY(scope, ref/member, relations, time, environment, ...) -> result`

then:

`MATERIALIZE(scope) -> { elements/relations whose current callability/eligibility permits participation }`

The representation could be function, rule, tree traversal, graph reachability, cached membership, event projection, or another cheaper mechanism.

Function representation is NOT mandated.

---

## 6. Potential State Vocabulary — Not Adopted

Possible operational outcomes to research:

- `CALLABLE_NOW`
- `NOT_CALLABLE_IN_SCOPE`
- `UNKNOWN_IN_SCOPE`
- `DEFERRED / LATENT`
- `MATERIALIZED`
- `NOT_MATERIALIZED`

These are only brainstorming candidates. Do not reintroduce ambiguous bare `STATUS` as a canonical field without qualification.

---

## 7. INIT Implementation Implication

A low-cost INIT could avoid global reachability proofs and instead:

1. define a bounded materialization scope;
2. evaluate current callability/relevance using available relations/rules;
3. instantiate/materialize only the eligible subset;
4. keep non-materialized references/history outside the active instance;
5. rematerialize a successor instance when relations/scope/rules materially change.

This is consistent with:

- P0 liveness/currentization;
- relational constitution;
- instance-as-materialized-view;
- succession rather than continuity;
- semantic relationality without universal expensive graph requirements.

---

## 8. Main Adversarial Questions

Codex should attack:

- Is `callability` a sufficiently general abstraction, or merely a runtime convenience?
- Who/what defines the current scope?
- Does `not callable` mean no relation, no permitted action, no dependency, or merely no active reference?
- Can important latent/historical relations be accidentally pruned?
- Is explicit materialization cheaper than a stable entity/event-sourced projection?
- How should scope-local callability interact with security/authority boundaries?
- Does this model create excessive rematerialization when the scope changes frequently?

---

## 9. Five-Line Summary

현재 상태: Owner가 global future-noninteraction proof 대신 bounded scope에서 `호출 가능/불가능`을 평가하고 그 결과로 현재 Instance materialization 여부를 결정하는 더 싼 후보를 제시했다.
핵심 판단: `NOT CALLABLE IN CURRENT SCOPE`는 `GLOBAL NONEXISTENCE`와 다르며, 현재 materialization에서 제외하는 것으로 충분할 수 있다.
진행 작업: rendering/culling 비유를 유지하되 `not rendered`와 `not memory-resident`를 기술적으로 분리하고 substrate/reference, scope-callability, materialization, runtime residency 층을 구분했다.
다음 단계: callability가 Relation family의 한 결과인지, Boundary operator인지, materialization eligibility인지 Codex 대항군에서 비교하고 INIT의 가장 싼 구현을 찾는다.
사용자 행동: 이 bounded-scope 접근을 현행 강한 구현 후보로 보존하되 bare STATUS 용어는 피하고 callability/materialization 개념명을 후속 검토한다. 작성시각: 2026-08-20 17:27 KST
