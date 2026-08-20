# AAA-ASA-MI Meeting Memory

## Title
Memory-Layer Representation Refinement for Scope-local Materialization

## Date / Time
2026-08-20 17:28 KST

## Status
WORKING_RESEARCH_CONTEXT / TERMINOLOGY_REFINEMENT / INIT_CURRENTIZATION_PREPARATION

## Purpose
Preserve Owner's proposal to express the rendering/materialization analogy through a memory-layer model, while preventing ambiguity between conceptual/operational memory and physical RAM/VRAM residency.

This record is NOT a Requirement, Design Contract, Frozen Artifact, Final Ontology, Validation Receipt, Independent Validation PASS, or Final Truth.

---

## 1. Owner Proposal

Owner suggested changing the representation to a `memory layer` framing.

Motivation:

- objects not relevant/callable in the current scope need not be actively instantiated/materialized;
- objects relevant to the current scope can be instantiated into an active working representation;
- the rendering analogy becomes intuitive if one thinks in terms of what is currently loaded into an active working layer versus what remains outside it.

---

## 2. Terminology Caution

Bare `MEMORY_LAYER` is potentially overloaded in ASA-MI because memory is already a major Persona/Self research concept.

Therefore the working proposal is to distinguish semantic layers explicitly rather than equating all of them with physical memory.

Candidate layers:

### PERSISTENT / LATENT MEMORY LAYER
References, history, evidence, possible relation candidates, source records, or other material that is preserved but not necessarily active in the current scope.

### ACTIVE / WORKING MEMORY LAYER
The bounded set of currently callable/materialized instances, members, and relations participating in the current scope.

### RUNTIME RESIDENCY LAYER
Actual implementation residency in RAM/VRAM/cache/process memory. This is a performance/implementation detail and is NOT identical to semantic materialization.

Potential distinction:

`PERSISTED != CURRENTLY MATERIALIZED != PHYSICALLY RESIDENT`

---

## 3. Rendering Analogy Under Memory-Layer Framing

Useful conceptual analogy:

`WORLD / STORED SUBSTRATE`
-> scope/view evaluation
-> active working/materialized memory layer
-> render/interaction/execution

A culled/non-rendered object can remain in persistent/latent memory and may even remain physically resident; it is merely excluded from the current active materialization.

Therefore:

`NOT IN ACTIVE MEMORY LAYER != DELETED`

and

`IN ACTIVE MEMORY LAYER != PERMANENTLY PART OF INSTANCE`.

---

## 4. Scope-local Callability

Owner's cheaper INIT direction remains:

> In this bounded scope, evaluate whether the candidate is callable/participating now.

If not callable, leave it outside the active working/materialized layer rather than solving all possible future interaction paths.

Possible pattern:

`Persistent/Latent Substrate`
-> `Scope-local Callability Evaluation`
-> `Active Working Memory / Materialized Instance`

A successor scope may materialize a different active set.

---

## 5. Candidate Strength

This memory-layer framing is a REPRESENTATION / IMPLEMENTATION hypothesis candidate, not a claim that reality itself is memory.

Important guardrail:

`MEMORY-LAYER IMPLEMENTATION != EVERYTHING IS MEMORY`

The earlier `Identity ?= Memory` hypothesis remains separate and must not be made unfalsifiable by expanding the word memory to cover everything.

---

## 6. INIT Value

This framing may be especially suitable for INIT because it provides a cheap operational boundary:

- preserve broad substrate/history;
- materialize only bounded current working set;
- do not require global nonexistence proofs;
- rematerialize successor instances when scope/relation composition changes;
- keep physical runtime residency as an optimization concern rather than semantic truth.

---

## 7. Five-Line Summary

현재 상태: Owner가 scope-local callability와 rendering/materialization 비유를 `memory layer` 관점으로 표현하는 후보를 제시했다.
핵심 판단: 방향은 유용하지만 bare MEMORY_LAYER는 Persona memory와 물리 RAM/VRAM을 혼동할 수 있어 `persistent/latent`, `active/working`, `runtime residency` 층을 분리하는 것이 안전하다.
진행 작업: `PERSISTED != MATERIALIZED != PHYSICALLY RESIDENT` 구분과 active working memory layer를 INIT의 bounded materialization surface로 사용하는 후보를 정리했다.
다음 단계: Codex 대항군에서 memory-layer framing이 materialized-view/callability보다 더 명료하고 싼지, 또는 단순 용어 중복인지 비교한다.
사용자 행동: 현 단계에서는 `memory layer`를 유력 표현 후보로 보존하되 `everything is memory`로 확장하지 않고 계층명을 후속 검토한다. 작성시각: 2026-08-20 17:28 KST
