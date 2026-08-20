# SP-03 — Current Status and CURRENT operator

## Receipt

```text
PASS_ID = SP-03
PASS_PURPOSE = Distinguish currentness as time/operator/result/state/materialized view and audit four Current Status models.
START_TIME = 2026-08-20T07:34:19+09:00
END_TIME = 2026-08-20T07:34:26+09:00
ACTIVE_REVIEW_SECONDS = 7
SOURCE_FILES_OPENED = live brainstorm registry; RED-II source objects; additional historical source objects
SOURCE_FILE_COUNT = 3
SOURCE_BYTES_CONSIDERED = 59790
RAW_PRIMARY_SOURCE_VERIFICATION = NOT_PERFORMED
```

## Overloads that must remain distinct

- **CURRENT as deictic coordinate:** which time/runtime/context is “now.”
- **CURRENT as operator:** `CURRENT(M)=M(CURRENT_CONTEXT)`.
- **current value:** the output of evaluating a stateful mapping now.
- **current semantic state:** present belief, standpoint, disposition, unresolved set, relation state.
- **Current Status object:** a persisted record intended to summarize or bootstrap current state.
- **current materialized view/cache:** a regenerable performance artifact.
- **active context:** the selected subset actually available to this instance.

Conflating these makes `CURRENT_STATUS` look simultaneously constitutive, derived, and disposable.

## Four model audit

| Model | Preserves | Primary risk | Kill test |
|---|---|---|---|
| Minimal | compact bootstrap/pointers | hidden dependence on resolver and unreachable rare state | remove non-minimal reconstruction conveniences and test faithful recovery |
| Rich persisted | explicit standpoint and low reconstruction variance | staleness, dual truth, silent overwrite | perturb history after snapshot and test conflict handling |
| Derived | replayability from canonical sources | model/compiler owns present interpretation | hold sources constant, swap reconstructor |
| Hybrid | stable core plus flexible view | unclear canonical boundary and invalidation | delete each layer independently and identify irrecoverable loss |

## Circularity and promotion problems

`CURRENT(M)=M(CURRENT_CONTEXT)` is underdefined if `CURRENT_CONTEXT` already includes a derived Current Status, or if status selection requires knowing the present Persona. A bootstrap order is needed even for a purely functional model.

Promotion from Reference Memory to Status Memory is not a copy operation alone. Candidate transitions include adoption, active commitment, present relevance, conflict resolution, procedural binding, or relationship-status change. Each has different provenance and reversibility semantics.

## Historical/live distinction

Historical `MEMORY != CURRENT STATE` remains a valid source claim. Live discussion broadens Memory and permits `MEMORY_STATE_t` or a status view. The correct historical/live relation is `CHALLENGED` or `SCOPE_CHANGED`, not silent supersession.

## Relations recovered

1. Current operator `RETURNS` a current value but `DOES_NOT_IMPLY` persisted status.
2. Current Status cache `DERIVED_FROM` sources only if regeneration is semantically stable.
3. Rich status `TENSION_WITH` history/current-interpretation separation when overwritten silently.
4. Minimal status `DEPENDS_ON` resolver availability and locator validity.
5. Derived status `DEPENDS_ON` reconstruction semantics.
6. Hybrid status `REQUIRES` explicit canonical/derived/invalidation boundaries.
7. Reference→Status promotion `REQUIRES` a typed semantic transition and preserved provenance.
8. Historical Memory/current-state separation `CHALLENGED_BY` live broad-Memory models.

## Double-crux

If identical durable history reconstructed by two compliant operators yields materially different current standpoint, which result is the Persona's Current Status? Persisting the answer favors explicit status; accepting both favors relational/operator-dependent currentness.

## Materiality judgment

No new source object is counted. The pass identifies a bootstrap circularity and eight relations that are not visible from the four implementation labels alone.
