# M3Top3 Fast-Close → Tune Dashboard

FAST_CLOSE [█░░░░░░░░░] 14%  
EWU = 14 / 100  
CRU = 1.5 wall-time proxy / 160 planned  
ELAPSED = 14 minutes since successor baseline  
ACTIVE TIME = not separately instrumented  
BLOCKED TIME = G1 external custody wait active and excluded from active ETA  
REWORK = 0  
ETA P50 = 4–6 hours; P90 = 8–12 hours; LOW confidence  
CRITICAL PATH = G1 external custodian response/exhaustion + G3 CA B/C deterministic closure  
LAST MATERIAL PROGRESS = Fast-Close v2 adopted; FC0 closed; G3 predecessor manifest declaration reconciled without byte substitution

## Lane progress

| Lane | Progress | State |
|---|---:|---|
| G1 | 33% (5/15 EWU) | external custodian blocker; duplicate internal searches prohibited |
| G2 | 0% (0/25 EWU) | fast lane queued |
| G3 | 16% (4/25 EWU) | manifest identity reconciled; CA B/C active |
| G4 | 100% | sealed `SATISFIED_WITH_FINDING`; do not rerun |
| Validation closure | 0% | reacquire once for an exact closure candidate |

Integrated G1–G4 remains `NOT_CLOSED`. EOPT-G0 remains `OPEN / NOT_PROVEN / 1 OF 6 PASS`; measurement and mutation remain not started.
