# AAA T19 Independent Validation — Manual Bridge Packet v0.1

PROJECT = Asset Agent ASA
TRACK = T19 — Execution Dispatcher / Worker Runtime
REQUEST_TYPE = INDEPENDENT_VALIDATION_EXECUTION
REQUESTING_AUTHORITY = PROJECT_OWNER
REQUESTING_CONTROL = AAA_BUILD_CONTROL
EXECUTOR_PERSONA = SEMI-VALIDATION-AUDITOR
EXECUTOR_ROLE = INDEPENDENT_VALIDATION
VALIDATION_RUN_ID = RUN-VALIDATION-AAA-T19-INDEPENDENT-20260816-001
WORK_ORDER_ID = WO-VALIDATION-AAA-T19-v0.1-INDEPENDENT-20260816
REPOSITORY = AofSpds/asset-agent-asa
BRANCH_CONTEXT = aaa-integration-v0.2
EXACT_TARGET_COMMIT = c867e3704b2744c3a826635b828ad6696e6281eb
TARGET_BINDING = control/aaa/validation/AAA-T19-EXECUTION-RUNTIME-INDEPENDENT-TARGET-BINDING_v0.1_WORKING.yaml
WORK_ORDER = control/workorders/WO-VALIDATION-AAA-T19-v0.1-INDEPENDENT-20260816.yaml

## PURPOSE
Independently and adversarially validate the exact integrated T19 Execution Dispatcher / Worker Runtime successor without relying on Engineering PASS assertions and without enabling live authoritative execution.

## AUTHORITY / INDEPENDENCE
- Repository access: READ_ONLY.
- Local temporary workspace: ALLOWED.
- Branch write / PR write / canonical write: PROHIBITED.
- Engineering PASS or CI green must not be reused as Independent Validation PASS.
- Independent Validation PASS does not authorize live execution, PostgreSQL Operational SoT, Production Release, or P10 Controlled Cutover.
- Do not modify P09 or T18 validation Runs/targets/results.
- Do not change Model / Feature / Scorer / Weight / Ranking methodology, Shared Contract, Ground Truth, PIT, or U127.

## REQUIRED START DISCIPLINE
1. Fetch the repository read-only and checkout EXACT_TARGET_COMMIT exactly.
2. Verify `git rev-parse HEAD` equals `c867e3704b2744c3a826635b828ad6696e6281eb` before running tests.
3. Do not substitute latest branch HEAD.
4. Record actual execution-start evidence in the RETURN PACKET. Do not fabricate ACK/start/heartbeat.
5. If exact checkout or prerequisite environment setup fails, fail closed and report the blocker.

## REQUIRED VALIDATION SCOPE
1. Full deterministic Python suite reproduction with exact commands and counts.
2. Owner Console locked `npm ci` and production build.
3. PostgreSQL 16 migrations `0001`–`0004`; recompute migration SHA256 values and compare to manifest.
4. Verify an unapproved Work Order cannot materialize an executable task.
5. Verify Work Order fields cannot inject arbitrary shell, command, entrypoint, or script.
6. Verify execution profile is code-owned, allowlisted, identity-bound, and SHA-bound.
7. Verify worker persona/capability/permission claim enforcement.
8. Race two eligible Workers for one task; exactly one claim winner is allowed.
9. Verify claim alone creates no ACK/start/heartbeat and never implies `RUNNING_CONFIRMED`.
10. Verify ACK alone does not imply `RUNNING_CONFIRMED`.
11. Verify start requires the current lease and records `started_at` plus first heartbeat.
12. Verify stale `lease_epoch` cannot heartbeat, append execution evidence, or terminalize.
13. Verify exact Git target mismatch blocks before ACK and before command execution.
14. Verify Worker runtime invokes only allowlisted argv with `shell=False`.
15. Verify Worker crash/interruption never implies success.
16. Verify partial Result persistence cannot create a terminal Run.
17. Verify terminal Result persistence and Run terminal transition are atomic.
18. Verify duplicate/idempotent task materialization does not create duplicate execution.
19. Verify retry semantics require a new Run identity with lineage, not reuse of terminal Run identity.
20. Verify PostgreSQL execution projection cannot override JSON operational authority during shadow.
21. Verify CLI/API/Owner Console show consistent Worker/Task/Run truth.
22. Verify absence of Worker projection does not infer liveness.
23. Verify LLM-off does not block deterministic execution Control Plane.
24. Verify `Persona != Worker != Channel != Model` boundary is preserved.
25. Verify P09 exact targets remain `80378610f9ac9e688c52417f0416e01c057400a7` and `30fdb278c218b24e44d66eb5f47935a196dc4f8c`.
26. Verify T18 Independent target remains `59c9baf3a24b1cf7542a3643c296711c37d72c3c`.
27. Verify validation produced no canonical repository/control mutation.

## ENGINEERING CLAIMS TO TREAT AS UNTRUSTED INPUTS
Engineering reports 142/142 deterministic tests PASS; PostgreSQL 16 contract smoke PASS; two-worker single-claim-winner PASS; claim-does-not-imply-running PASS; JSON Run Registry reconciliation PASS; backup/restore PASS; Owner Console locked install/build PASS. Independently reproduce relevant evidence; do not inherit these as verdict evidence without rerun.

## EXPLICIT EXCLUSIONS
- Actual live managed PostgreSQL provisioning.
- Managed PITR/RPO/RTO qualification.
- PostgreSQL Operational SoT cutover.
- Production/live T19 Worker daemon enablement.
- Retroactive ACK/start/heartbeat on existing P09 or T18 Runs.
- P09 or T18 Independent Validation verdict adjudication.
- Production Release or P10 Controlled Cutover.
- Model methodology, Shared Contract, Ground Truth, PIT, or U127 changes.

## REQUIRED VERDICT
Return exactly one of: PASS / PASS_WITH_FINDINGS / FAIL.
Also return `INDEPENDENT_VALIDATION_PASS = TRUE|FALSE` and explicitly set `LIVE_EXECUTION_AUTHORIZED = FALSE`, `POSTGRESQL_OPERATIONAL_SOT_AUTHORIZED = FALSE`, `CONTROLLED_CUTOVER_AUTHORIZED = FALSE`.

## RETURN FORMAT
At completion output exactly one fenced Markdown code block beginning with `[RETURN PACKET]` and nothing after the code block. Include all of:
- project / track / executor Persona
- validation_run_id / work_order_id
- exact_checkout_commit and verification evidence
- actual start evidence and, if maintained, heartbeat evidence
- environment and tool versions material to the tests
- every command executed
- deterministic test count/pass/fail/error
- Owner Console npm/build results
- PostgreSQL migration SHA verification
- each adversarial T19 finding/result
- concurrency single-winner evidence
- claim/ACK/start/heartbeat semantic evidence
- stale lease/fencing evidence
- exact-target pre-execution failure evidence
- crash/partial-result/atomic-terminal evidence
- authority/security/non-interference evidence
- canonical side-effect check
- exclusions preserved
- explicit blocking/nonblocking findings with IDs and severity
- explicit verdict
- independent_validation_pass boolean
- live_execution_authorized false
- postgresql_operational_sot_authorized false
- controlled_cutover_authorized false
- recommended Run terminal state
- recommended T19 gate state
- any evidence locators/log IDs needed for control adjudication

CURRENT STATUS = T19 engineering integrated; Independent Validation Run is DISPATCHED_AWAITING_ACK, not RUNNING.
KEY JUDGMENT = Exact target is fixed at c867e3704b2744c3a826635b828ad6696e6281eb and must not follow later control-only HEADs.
WORK IN PROGRESS = SEMI-VALIDATION-AUDITOR must independently reproduce and adversarially test the T19 execution-control invariants.
NEXT STEP = Execute the full read-only validation and return exactly one [RETURN PACKET] code block.
USER ACTION = None inside the validator channel other than providing this packet; do not request reconstructed context unless an actual prerequisite is unavailable.
