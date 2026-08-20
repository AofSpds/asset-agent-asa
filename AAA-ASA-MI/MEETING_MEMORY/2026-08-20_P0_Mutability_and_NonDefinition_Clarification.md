# AAA-ASA-MI Meeting Memory Addendum

## Title
P0 Mutability and Non-Definition Clarification

## Date
2026-08-20

## Status
WORKING_RESEARCH_CONTEXT

## Purpose

Record an Owner clarification made while reviewing instruction candidates for ASA-MI task design.

This record is not a Requirement, Design Contract, Frozen Artifact, Final Ontology, or Validation Receipt.

---

## 1. Owner Clarification

The intended position is not primarily:

`WE DO NOT KNOW`

It is closer to:

`WE DO NOT FINALIZE / DEFINE THE ESSENCE AS FIXED`

The project should operate with a mutable current status rather than attempt to settle a final immutable definition.

Owner preference:

- Treat the current state as operationally usable.
- Allow that state to change.
- Do not promote the current state into a final ontological definition merely because the system needs something to operate with.
- The P0-level hypothesis concerns mutability / non-finalization.

---

## 2. Important Distinction

`UNKNOWN`

is not the same as:

`NOT_FINALIZED_BY_DESIGN`

A system may know enough to maintain an explicit current status while intentionally refusing to freeze that status into a final essence.

Candidate conceptual distinction:

- `UNKNOWN`: evidence or interpretation is insufficient.
- `CURRENT_STATUS`: an operational state exists now.
- `NOT_FINALIZED`: the current state is not promoted to an immutable final definition.
- `REVISABLE`: successor states remain allowed when context/evidence/interpretation changes.

This distinction is itself still a working representation and may evolve.

---

## 3. Implication for the Earlier `CURRENT_MODEL != REALITY` Candidate

`CURRENT_MODEL != REALITY` was an ASA synthesis and should not be treated as the Owner's primary P0 rule.

A more faithful current interpretation is:

> Maintain an explicit current status, but do not freeze it as the final definition of the phenomenon.

Therefore both of the following may be downstream expressions rather than separate top-level principles:

- `CURRENT_MODEL != FINAL_DEFINITION`
- `CURRENT_HYPOTHESIS != FINAL_DEFINITION`

Whether they should be merged, separated, or represented differently remains open.

---

## 4. Relation to the Function-Mapping Proposal

Owner previously proposed that context-sensitive properties may be better represented by a mapping result than by a fixed constant or a single mutable scalar.

Candidate form:

`CURRENT_VALUE_t = f(STATE_t, CONTEXT_t, RELATIONS_t, HISTORY_t, RUNTIME_t, ...)`

Motivation:

- The operational value can be explicit now without pretending it is an eternal essence.
- Context dependence becomes visible.
- A successor context may legitimately produce a different current value.
- The representation naturally separates `current result` from `final definition`.

Important classification clarification from Owner:

- Function mapping is **NOT an instruction**.
- Function mapping is **NOT the P0 principle itself**.
- Function mapping is a **technical / modeling hypothesis candidate linked to the P0 mutability/non-finalization hypothesis**.
- It remains subject to technical challenge, comparison, experimentation, rejection, narrowing, or replacement.
- A Codex committee technical review is requested before any adoption.

Current working tag:

`HYPOTHESIS_CANDIDATE / P0_LINKED / FUNCTION_MAPPING_REPRESENTATION / UNCONFIRMED`

It must not be promoted into a default implementation rule merely because it appears conceptually compatible with P0.

---

## 5. Technical Caution

`DO NOT FINALIZE` must not be misread as `DO NOT DEFINE ANYTHING`.

Operational systems still require explicit interfaces, schemas, state representations, invariants, and execution contracts where needed.

The open research question is which definitions are:

- operational/scoped/current,
- versus claims about an immutable essence.

The project should avoid confusing those two categories.

Function mapping is only one candidate way of representing current mutable status. Alternatives remain open, including event-sourced state, temporal/state-machine models, reactive models, probabilistic state models, rule-based models, graph/state hybrids, learned representations, and combinations thereof.

---

## 6. Current Candidate P0 Wording

Current best wording for discussion:

> `P0 MUTABILITY / NON-FINALIZATION HYPOTHESIS:`
> Maintain explicit current status and allow it to be operationally used, while withholding commitment to a permanently fixed final definition. Current status may be revised, replaced, narrowed, expanded, or reinterpreted as evidence, context, relations, runtime, or the research model changes.

This wording is NOT frozen and remains subject to successor discussion.

---

## 7. Continuation Point

Before continuing the instruction-candidate list:

1. Use the P0 formulation only as the current working status, not as a frozen doctrine.
2. Re-evaluate earlier candidates (`CURRENT_MODEL != REALITY`, `CURRENT_BEST_HYPOTHESIS != FINAL_TRUTH`) as possible derivatives rather than independent top-level instructions.
3. Keep the function-mapping proposal in the hypothesis-candidate layer, linked to P0 but distinct from it.
4. Ask the Codex committee to compare the function-mapping candidate against alternatives and attempt falsification before any design adoption.

---

## 8. Classification Correction — Function Mapping

OWNER_EXPLICIT clarification:

> `함수 방식은 지침은 아닙니다. p0에 물려 있는 가설 후보 정도 됩니다.`

Therefore the current lineage is:

`P0 MUTABILITY / NON-FINALIZATION HYPOTHESIS`

→ motivates exploration of representations that do not prematurely freeze context-sensitive phenomena

→ `FUNCTION-MAPPING REPRESENTATION HYPOTHESIS CANDIDATE`

This lineage does **not** mean logical entailment. The function-mapping candidate may be rejected while the P0 mutability hypothesis remains active.

Likewise, technical evidence against function mapping should update the function hypothesis first, not automatically falsify P0 unless that evidence also directly challenges P0.

---

## Five-Line Summary

현재 상태: P0는 가변성/비확정성에 관한 현행 연구가설이며, 운영 가능한 Current Status를 두되 최종 불변 정의로 확정하지 않는 방향으로 유지한다.
핵심 판단: 함수 mapping은 지침도 P0 자체도 아니며, P0에 연결된 별도의 기술·모델링 가설 후보이다.
진행 작업: 함수 후보를 `HYPOTHESIS_CANDIDATE / P0_LINKED / UNCONFIRMED`로 재분류하고 대안 비교·반증 대상으로 남겼다.
다음 단계: 기존 001/002 지침 후보를 P0의 파생 표현인지 재검토하고, 함수 후보는 Codex 위원회 기술 검토 대상으로 분리한다.
사용자 행동: 다음 지침 후보 검토에서는 함수 mapping을 지침 목록에서 제외한 상태로 진행한다. 작성시각: 2026-08-20 14:46 KST
