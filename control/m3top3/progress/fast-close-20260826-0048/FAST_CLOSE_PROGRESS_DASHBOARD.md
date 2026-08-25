# M3Top3 Fast-Close → Tune Dashboard

AS_OF = 2026-08-26 02:36 KST  
FAST_CLOSE [██░░░░░░░░] 21%  
EWU = 21 / 100  
CRU = not instrumented / 142 replanned (160 original); prior batches approximately 32 aggregate worker-minutes plus Axis-B 75.043 s main path and 79.269 s rework plus KRX Axis-C 134.44 s capture span and calendar 28 s material span plus PMO integration  
ELAPSED = approximately 122 minutes since successor baseline  
ACTIVE TIME = approximately 19.72 known worker main-path minutes plus Axis-C active retrieval not instrumented; PMO time not instrumented separately  
BLOCKED TIME = G1 external custody; G2 historical authority; G3 Axis-C credential/admin approval and calendar open-session authority; external waits excluded from active ETA  
REWORK = 5 events: one orchestration reconciliation, three Axis-B forward fixes, one Axis-C client-compatibility forward attempt / known lower-bound 7.321 minutes plus one not-instrumented attempt / no loop  
REOPENED UNITS = 0  
VALIDATOR = HOLD; active count 0; sealed receipts preserved  
NON-VALIDATOR WORKERS = 0; no material worker remains active  
PRE-VALIDATION CANDIDATE ETA = unmeasurable until exact external source/authority inputs resolve; conditional lane estimates exclude external wait  
MINIMUM VALIDATION = one FC2/FC3 exact-delta act only; global validation/full suite/automatic revalidation/validation loop prohibited  
SEALED EOPT-G0 ETA = unavailable until validator hold release; add P50 0.25–0.5h / P90 0.75–1h after release  
BOUNDED BLOCKER-RESOLUTION PHASE [██████████] 100%; 3/3 units complete; earned EWU unchanged because no gate evidence closed  
CURRENT LOCAL INTEGRATION PHASE [██████████] 100%; Owner packet + G3-F blocked lineage + FC2 preflight committed and exact-read back  
POST-OWNER DECISION EXECUTION [██████████] 100%; three dispatched units Git-sealed and exact-read back; this is execution telemetry, not EWU  
VALIDATION PROFILER = 0 acts / 0 validator wall minutes / `NOT_ENOUGH_DATA`; global validation and loops 0  
CRITICAL PATH = authorized exact KRX/custodian CA export plus official open-session authority, then terminal reconciliation of all 2,406 Axis-B signals  
LAST MATERIAL PROGRESS = official KRX custody evidence sealed at commit `e9bd65fea88939b8ee79c84163f864355f8ffb4f`: Axis-C access blocker plus exact 2024–2026 closure bytes 3/3 and 54 rows

## Lane progress

| Lane | Progress | State |
|---|---:|---|
| G1 | 33% (5/15 EWU) | external custodian blocker; duplicate internal searches prohibited; no new G1 search actor |
| G2 | 28% (7/25 EWU) | source pass complete; 514 BP/listing cells and 8 authority rows remain source-blocked |
| G3 | 16% (4/25 EWU) | Axis-B 100% with 2,406 signals pending Axis-C; Axis-C credential/admin-approval blocked; calendar closure bytes 3/3 recovered but open-session authority remains blocked |
| G4 | 100% | sealed `SATISFIED_WITH_FINDING`; do not rerun |
| Validation closure | 0% | Owner HOLD; later one exact-delta time-boxed act only; no global loop |

## Runtime reconciliation

- Old PMO runtime: `RETIRED`.
- Observable old workers/validators: `0/0`.
- A late but completed predecessor-PMO branch sequence through commit `5f18bfe0b5e8fe0c820951dc8d8024586ef01c51` was detected after takeover and reconciled.
- It had already adopted Fast-Close v2. No duplicate validator, search, price-recovery or gate execution was started.
- Three redundant issue comments were corrected to status-sync-only, and the stale 5/100 snapshot was marked superseded.
- Owner decision and C/calendar/window rule bindings are committed. Worker/validator count is now `0/0`. Axis-B exact inputs matched 3/3 and all 14 artifact paths were sealed at tree `07a4d0923b153866fa9176324c5d840972575643`.

## Axis-B bounded result

- Execution [██████████] 100%; frozen EWU delta `0` because G3-B is a combined Axis-B/Axis-C seven-EWU unit.
- Population/evaluable/signals: `1,822,019 / 1,734,775 / 2,406`.
- Terminals: no-signal `1,732,369`; price-domain quarantine `84,272`; first-observation `2,972`.
- Raw first observations were `3,088`; `116` rows with `Open <= 0` correctly follow the higher-priority price-domain rule.
- Duplicate/missing-key/unresolved/silent-drop: `0/0/0/0`.
- Validator/global/full/loop: `0/FALSE/FALSE/FALSE`; `VALIDATION_CLAIM=NONE`.

## Official KRX source custody

- Custody execution [██████████] 100%; two bounded non-validator passes ended; workers/validators `0/0`.
- Axis C: official `MDC04020503 / MDCHARD048` returns a 407-byte login-required page, SHA-256 `72926595...a809`; conforming CA-universe bytes and authority receipt were not obtained.
- Calendar: exact official closure bytes recovered for `2024/2025/2026`, `18/19/17` rows, total `54`.
- Calendar boundary: no open-session rows, per-row market ID, open/session-hours/half-day fields, or common-equity-market proof; `TRADING_CALENDAR_RELEASE=NOT_CREATED`.
- Custody artifact commit/tree: `e9bd65fea88939b8ee79c84163f864355f8ffb4f` / `041cf5fff3aa245a47707cce85cc756152acc072`.
- EWU/gate/validation effect: `0 / NONE / NONE`.

Integrated G1–G4 remains `NOT_CLOSED`. EOPT-G0 remains `OPEN / NOT_PROVEN / 1 OF 6 PASS`; measurement and mutation remain not started.
