# Current Operating Structure Owner Console Projection

Status: IMPLEMENTED_AWAITING_INDEPENDENT_VALIDATION  
Scope: read-only UI/read-model only; no operational authority transition.

## Data flow

Persistent Control Plane
→ deterministic `/api/aaa/operating-structure` read model
→ Owner Console `Structure` view.

The UI does not maintain a separate manual organization chart. Formal Persona identity is projected from the existing organization/current-state records, active Channel bindings are projected from the latest `SEMI-CHANNEL-REGISTRY`, and the current AAA Stage/Gate and authority flags are projected from the latest `AAA-PROCESS-GATE-STATUS`.

The owner-approved Post-IV stage order is read from:

`control/aaa/architecture/AAA-v1-POST-IV-OPERATING-ROADMAP_v1.0_OWNER-APPROVED.json`

## Refresh and failure semantics

The Owner Console loads the projection on page load and refreshes it every 15 seconds.

- missing required source → `UNAVAILABLE`
- declared stale current source → `STALE`
- contradictory current binding evidence → `CONFLICT`
- absent active Channel binding → `NOT_INSTANTIATED`
- no Run start/current heartbeat evidence → never infer `RUNNING`

P09/T18 historical lifecycle state and current disposition are exposed as separate fields.

## Authority boundary

This projection is read-only. It does not authorize Worker execution, bounded Shadow execution, PostgreSQL Operational SoT, production canonical promotion, Controlled Cutover, or Production Release.

Source owner approval recorded at: 2026-08-17T01:25:00+09:00
