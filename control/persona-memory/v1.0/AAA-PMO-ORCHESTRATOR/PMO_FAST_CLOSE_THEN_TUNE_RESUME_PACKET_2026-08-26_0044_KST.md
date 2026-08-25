# PMO Fast-Close Then Tune Resume Packet

PROJECT = AAA
PRODUCT = ASSET AGENT ASA
TARGET_PERSONA = AAA-PMO-ORCHESTRATOR (PMO)
PACKET_CLASS = CHANNEL_SUCCESSION / FAST_CLOSE / RISK_PROPORTIONAL_VALIDATION / TUNE_NEXT
RECORDED_AT = 2026-08-26 00:44 KST
OWNER_PRIORITY = FINISH_CURRENT_OPEN_WORK_AS_FAST_AS_SAFELY_POSSIBLE_THEN_ENTER_TUNING
PROGRAM_RESTART_REQUIRED = FALSE

## 0. Owner directive

The previous PMO visible channel ended by context limit. Retire that runtime and release all active workers/validators tied to it. Preserve sealed receipts/evidence. The successor PMO must finish the still-open G1/G2/G3 + integrated checkpoint work using the shortest safe path, then evaluate EOPT-G0 immediately and enter the governed tuning/measurement route as soon as gates permit.

Do not spend additional hours re-proving already sealed work, repeating identical deterministic checks, or expanding validation beyond the risk actually introduced by the open unit.

## 1. Clean takeover before compute

Before material redispatch:
- confirm old PMO runtime retired;
- confirm old workers/validators are not still executing, or treat their state as UNKNOWN and do not duplicate their exact job until reconciled;
- read latest GitHub Issue #49 and #52 comments;
- reconcile branch/worktree/artifact heads and preserve any newly durable results;
- acquire one exclusive successor execution lease.

Channel succession is not rework. Do not restart WP0-WP9.

## 2. Current durable baseline

Last durable state to reconcile, not blindly assume:
- G1: IN_PROGRESS / NOT_SATISFIED; exact v0.1/v0.2 ZIP bytes NOT_FOUND; custodian exhaustion NOT_PROVEN; #52 active.
- G2: partial progress; 34 documentary cells, 514 combined eligibility cells, W1-W8 date provenance and remaining closure evidence open.
- G3: exact upstream 2024/2025/2026 marcap Parquet bytes recovered/pinned; predecessor standalone manifest, CA B/C, governed calendar, PIT eligibility/tradability, annotation and remaining closure evidence open.
- G4: SATISFIED_WITH_FINDING; sealed. Do not rerun solely due to succession.
- G1-G4 integrated checkpoint: NOT_CLOSED.
- EOPT-G0: OPEN / NOT_PROVEN / 1 OF 6 PASS.
- EOPT measurement/mutation: NOT_STARTED.
- Full W1-W8 scale-out: NOT_AUTHORIZED.

Git governed current state wins if newer.

## 3. FAST_CLOSE execution policy

SUCCESSOR_PMO_EXECUTION_POLICY = TUNED_RISK_PROPORTIONAL_FAST_CLOSE

Mandatory rules:
1. Run G1, G2 and G3 as three isolated parallel lanes where dependencies permit.
2. Do not attach standing validators to every substep. Validators are acquired only when a lane has a closure candidate or a specific high-risk finding requires independent review.
3. Reuse sealed deterministic receipts when exact target/input/test-definition applicability is unchanged.
4. Use delta validation for local/non-semantic documentary or packaging changes.
5. Full regression, mutation, concurrency and multi-validator replay are reserved for changes that actually touch high-risk runtime semantics or for a required integrated gate boundary.
6. Nonblocking findings are recorded and execution continues unless the finding prevents trustworthy closure or requires an Owner-reserved decision.
7. Every search/recovery activity has a bounded stop rule. Repeating the same search surface without new evidence is prohibited.
8. Do not relax PIT, evidence, eligibility/tradability, fail-closed, immutable-lineage, model-semantics or claim ceilings merely to go faster.
9. Missing evidence is fail-closed or escalated, never fabricated.

## 4. Fast-close WBS and time budget

These are planning priors for the successor PMO, not guarantees. Reforecast after the first measured segment. All times are successor wall-clock targets and assume safe parallel work.

| WBS | Work | P50 | P90 / range | Initial EWU | Initial CRU | Validation rule |
|---|---|---:|---:|---:|---:|---|
| FC0 | Bootstrap + old-runtime/duplicate reconciliation + exclusive lease | 0.5 h | 1.0 h | 5 | 5 | read-only consistency only |
| FC1-G1 | Bounded exact-byte recovery/exhaustion determination | 1.0 h | 2.0 h | 15 | 20 | evidence/hash check only if candidate found; no endless re-search |
| FC1-G2 | Close remaining documentary/eligibility/date-provenance package | 2.5 h | 5.0 h | 25 | 45 | targeted/delta validation; independent review only at closure |
| FC1-G3 | Close remaining manifest/CA/calendar/PIT/annotation package | 2.5 h | 5.0 h | 25 | 45 | targeted/delta validation; stronger check only for PIT/CA semantics |
| FC2 | Integrated G1-G4 reconciliation + final hash/JSON/repro/gate-delta/base-pin/writer-clear closure | 1.0 h | 2.0 h | 20 | 30 | one integrated gate validation, reuse sealed G4 evidence |
| FC3 | EOPT-G0 evidence matrix evaluation | 0.25 h | 0.5 h | 5 | 5 | deterministic gate evaluation |
| FC4 | If EOPT-G0 PASS: freeze measurement inputs/environment/oracle and start pinned-original A/A | 0.5 h setup | 1.0 h setup | 5 | 10 | governed EOPT protocol |

Initial total = 100 EWU / 160 CRU before empirical reforecast.

Expected fast-close critical-path target if no external G1 blocker remains:
- P50: approximately 4-6 hours from clean takeover to EOPT-G0 decision.
- P90 planning envelope: approximately 8-12 hours.

This estimate excludes an unbounded external source-custody wait. If G1 requires an unavailable external custodian response, PMO must expose it immediately as the critical blocker rather than hiding it inside ETA.

## 5. G1 bounded-stop rule

G1 must not consume another long search cycle repeating already-exhausted local/Git surfaces.

Within FC1-G1:
- reconcile #52 and any newly available named custodian/archive/attachment/backup locator;
- search each genuinely new addressable surface once with exact filename/size/hash criteria;
- if exact candidate found: quarantine -> size/hash verify -> isolated inspection -> exact receipt;
- if no new addressable surface exists and custodian exhaustion can be evidenced, publish an exhaustion packet immediately;
- if exhaustion cannot be proven because an external custodian is unresolved, mark `G1_EXTERNAL_CUSTODY_BLOCKER` and continue G2/G3 in parallel. Do not invent G1 closure.

If an Owner-reserved decision becomes the only remaining path, prepare one concise decision packet immediately instead of spending more compute on redundant search.

## 6. G2 fast lane

Prioritize closure evidence, not exploratory expansion.

Order:
1. reconcile the 34 documentary cells and existing v0.2 lineage;
2. close/resolve the 514 combined eligibility cells using already-governed inputs and deterministic processing where possible;
3. close W1-W8 date provenance;
4. hash and publish one consolidated G2 closure candidate;
5. perform one targeted independent validation of the closure candidate.

Do not spawn separate validators for every mechanical subset. Use deterministic code for arithmetic/schema/status completeness; reserve LLM/validator review for exceptions/conflicts/semantic judgments.

## 7. G3 fast lane

Exploit the already recovered exact upstream 2024/2025/2026 price bytes. Do not re-recover them.

Order:
1. reconcile/reconstruct the required standalone manifest identity only from admissible evidence; otherwise explicitly qualify it;
2. close CA B/C and governed calendar through the minimum authoritative source set;
3. close PIT eligibility/tradability and annotation dependencies needed for the integrated checkpoint;
4. bind all outputs to exact upstream byte/hash lineage;
5. run one targeted independent G3 validation at closure.

Do not rerun broad price ingestion/recovery unless exact identity mismatch is detected.

## 8. Integrated closure

Once G1/G2/G3 reach closure candidates:
- bind current G1/G2/G3 artifacts to already sealed G4 exact-target evidence;
- close final hash/JSON/reproducibility QC;
- publish integrated gate-delta;
- pin unified EOPT original-base commit/tree/runtime/config/input/environment;
- establish writer-clear receipt;
- run one integrated claim/gate reconciliation.

Avoid per-lane full-suite revalidation followed by another identical integrated full-suite validation. Validation must be non-duplicative.

## 9. Transition immediately to tuning

If and only if EOPT-G0 actually passes:
1. freeze measurement protocol/workload/environment/cache-state/equivalence oracle;
2. run pinned-original A/A baseline;
3. measure bottleneck contributions and cost per attempted company-window;
4. publish/hash `M3TOP3_EOPT_MEASURED_TUNING_EXECUTION_PLAN_v1.0`;
5. evaluate EOPT-G1;
6. only after EOPT-G1 PASS create isolated optimization branch/worktree and begin semantic-neutral mutation;
7. run isolated/cumulative A/B and required validation;
8. activate only proven candidates.

PMO process/validation orchestration tuning in this packet is effective immediately. M3Top3 runtime/code mutation remains governed by EOPT-G0/G1.

## 10. Progress reporting

At minimum publish/update:
- OVERALL FAST_CLOSE progress = earned EWU / 100 initial EWU, with explicit REBASE if denominator changes;
- G1/G2/G3 lane progress;
- validation/evidence closure progress;
- elapsed wall-clock;
- active / wait / rework time where measurable;
- CRU consumed / forecast;
- ETA P50/P90 and confidence;
- current critical blocker;
- last material progress event.

Owner-facing display example:
`FAST_CLOSE [██████░░░░] 62% | 62/100 EWU | 94/160 CRU | elapsed 3.1h | ETA 2-5h | blocker: G1 external custody`

## 11. Claim ceiling

This FAST_CLOSE packet does not waive validation or authorize false closure. It only removes duplicated/low-value verification and enforces bounded search and risk-proportional validation.

No new predictive-power, Golden, Replay, Freeze, Promotion, Release, Production, optimization-effectiveness or model-semantic claim is created by this packet.

## 12. Successor PMO first report

The new PMO must report:
- CURRENT_PERSONA_LOCK
- old runtime retired / duplicate execution status
- exclusive execution lease status
- latest reconciled G1/G2/G3/G4/EOPT state
- FC0 status
- FAST_CLOSE initial/rebased EWU and CRU denominator
- first critical-path ETA
- exact first three parallel dispatches
- any Owner-only blocker, if one truly remains
