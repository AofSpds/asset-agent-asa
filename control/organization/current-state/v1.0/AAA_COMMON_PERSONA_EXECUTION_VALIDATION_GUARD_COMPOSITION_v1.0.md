# AAA Common Persona Execution / Validation Guard Composition v1.0

PROJECT = AAA  
PRODUCT = ASSET AGENT ASA  
CLASS = P1_GLOBAL_OPERATING_CONTROL_COMPOSITION_CONTRACT  
MODE = POINTER_CONTROLLED (`SHADOW` OR `ENFORCED`)  
STATE = D1_CORRECTED_CANDIDATE_PENDING_A4_RECHECK_NOT_ACTIVE  
AUTHORITY_SOT = FALSE

## Purpose and phase boundary

This contract defines how one project-common execution/validation guard is composed into every governed current and future AAA Persona without copying its normative rules into Persona memory. It changes no Organization, Shared Contract, Persona authority, validation floor, validation independence, model/PIT/GT semantics, Freeze, Release, or Production authority.

A1 creates design artifacts only. Bootstrap/pointer injection is A2, representative T0–T10 execution is A3, frozen role-scoped validation is A4, and PR/CAS/merge/enforced activation/readback is A5. No A1 artifact may claim active, enforced, PASS, Release, or Production state.

## Exact A1 base

- Isolated branch: `aaa-common-persona-validation-execution-guard-v1.1-r2-20260826`
- A0-R commit: `1ec8fa08dcca560cc592869ac0ed7fdce8d1ce3a`
- A0-R tree: `a617863d7108beb9ee3a68ad0963b61bd434090f`
- Upstream canonical active Persona inventory at A0-R: `control/organization/current-state/v1.0/AAA_ACTIVE_PERSONA_AND_VALIDATOR_INVENTORY_v1.0.tsv@e1bfc77b96c4a5fbf1b7bf43c8bf5f0683c64be6`
- Branch-local shadow-wiring inventory: exact blob is pinned separately by the latest D1 freeze checkpoint; it is routing evidence, not a second Persona authority SoT.
- Shared Contract current Persona projection: `control/organization/current-state/v1.0/AAA_SHARED_CONTRACT_CORE_B_PERSONA_CURRENT_PROJECTION_v1.0.json@8408ea10a98a6130703829e29c9325614a082ea5`
- Current Persona reference projection: `control/organization/current-state/v1.0/AAA_CORE_B_CURRENT_PERSONA_REFERENCES_v1.0.json@275e0da4257ea8562240979215a6c2dced290334`
- Current Persona count: `13`
- Relevant current-state directory tree: `202f6a61e924832fad8131c829905f5d5758914d`
- Common guard/pointer/composition/rollback paths at that exact tree: `ABSENT`

The exact absence evidence above is bounded to `control/organization/current-state/v1.0/`; it is not a repository-wide scan.

## Exact superior operating rule

- Pointer: `control/organization/current-state/v1.0/AAA_GLOBAL_PACKET_DISPLAY_RULE_CURRENT.json@7ae5cea1297b1b23217e4d9a3342924a724e38aa`
- Target: `control/organization/current-state/v1.0/AAA_GLOBAL_PACKET_DISPLAY_RULE_v0.4.json@dff467a971f9519ba6598f535fc47623197e4bcb`
- Target commit recorded by the pointer: `57cd7b37b7efb7ee97527e11defce7dc59e4bb5f`

The v0.4 quality priority remains `QUALITY → VALIDATION_RELIABILITY → COMPLETENESS → COMPUTE_EFFICIENCY → SPEED`. Runtime length, file length, Persona count, or worker count never justifies weaker reasoning or validation.

## Canonical composition order

1. Active Authority / Shared Contract
2. `AAA-GLOBAL-PACKET-DISPLAY-RULE-v0.4`
3. `AAA-COMMON-PERSONA-EXECUTION-VALIDATION-GUARD-v1.1`
4. Role-specific Persona runtime
5. Task-specific packet

Precedence is deterministic:

- Higher governed authority always wins.
- A task-specific high-impact gate may strengthen but never weaken the common guard or a superior gate.
- A role-specific runtime may refine duties but may not disable the common guard.
- The common guard routes execution/validation and records telemetry; it creates no authority or validation verdict.
- Any unresolved material conflict fails closed as `AAA_CURRENT_STATE_REVIEW_REQUIRED`.

## Deterministic loader

1. Resolve the active Persistent Locator and active Organization/Shared Contract.
2. Resolve the exact v0.4 current pointer and verify its target blob.
3. Resolve `AAA_COMMON_PERSONA_EXECUTION_VALIDATION_GUARD_CURRENT.json`.
4. Verify that the pointer names one exact guard path/blob and an allowed mode.
5. Resolve the pointer mode. In `SHADOW`, load the guard, compute the route, and emit telemetry without changing existing gates or verdicts.
6. In `ENFORCED`, only after every activation precondition is exact and PASS, apply G-01 through G-15 while preserving the authority, Shared Contract, validation-floor, independence, and direct-PASS firewalls.
7. Resolve the Owner-selected/current Persona through the selector registry and memory index.
8. Load only role-specific Persona memory/worklog/addenda; do not copy the common guard payload into them.
9. Apply the task-specific packet subject to the precedence rules above.
10. If any exact pointer/blob/mode check fails, stop before material execution and report the exact mismatch.

## One-pointer / no-dual-SoT rule

The normative guard exists only at:

`control/organization/current-state/v1.0/AAA_COMMON_PERSONA_EXECUTION_VALIDATION_GUARD_v1.1.json`

Bootstrap and Persona surfaces may store only the current-pointer path and exact pointer blob. They must not embed or restate G-01 through G-15. The existing universal Progress/Time/Compute behavior code remains a referenced source at:

`control/persona-memory/v1.0/COMMON/AAA_EXECUTION_PROGRESS_TIME_COMPUTE_BEHAVIOR_CODE_v1.0.md@5945078b3a291d19beffb8c3f1336b4af37da354`

This separates the common guard SoT from its injection route and avoids a second normative copy.

## Persona coverage and inheritance

All 13 current Personas in upstream canonical inventory blob `e1bfc77b96c4a5fbf1b7bf43c8bf5f0683c64be6` use the same pointer route. The latest D1 freeze checkpoint separately pins the branch-local inventory whose bootstrap fields evidence that wiring, avoiding a content-addressed cycle between guard, pointer, bootstrap, and inventory. A future Persona inherits the guard when it becomes governed current and is added to the canonical selector/memory route; no Persona-local copy or Owner restatement is required.

In A1, coverage is designed but not wired. A2 must materialize a coverage manifest and exact pointer injection. A3 must prove current and future-Persona inheritance behavior under T0.

## SHADOW semantics

SHADOW means:

- load the exact guard and observe its proposed routing;
- record progress/read/validation telemetry;
- preserve every existing validation floor and high-impact gate;
- create no direct PASS or FAIL;
- make no enforced routing decision;
- run T0–T10 before any enforced activation.

The current pointer is therefore a branch-local `SHADOW` candidate pointer. The immutable guard is pointer-controlled and supports `SHADOW` or `ENFORCED`, but the pointer remains neither the active product pointer nor evidence that enforced activation prerequisites passed.

## Activation gate

Enforced activation remains closed until all of the following are exact and PASS: active Persona inventory, all-Persona coverage, pointer composition, v0.4 preservation, no authority/floor/independence change, T0–T10, targeted frozen-candidate validator receipts, rollback demonstration, pre-merge CAS, and post-merge readback.

## Rollback interface

Operational rollback is `ENFORCED → exact prior SHADOW mode` through a forward-only, non-force, compare-and-swap atomic successor. The guard and composition artifacts remain immutable and present but become inert under SHADOW. Bootstrap continues to resolve the same single pointer path; because it exact-pins the pointer blob, its derived blob plus coverage/inventory bindings are rebound in the same forward atomic change set rather than claimed byte-unchanged.

Required rollback preconditions:

- exact enforced pointer blob and activation ref;
- exact prior SHADOW pointer/blob set pinned by the latest D1 freeze checkpoint and reconfirmed before activation;
- exact bootstrap injection blobs;
- exact guard/composition blobs;
- no unbounded or ambiguous pointer delta.

Required rollback post-readback:

- ref, commit, tree, pointer blob, guard blob, composition blob;
- bootstrap pointer path unchanged and exact derived bootstrap/coverage/inventory blobs rebound coherently;
- fresh Persona resolution;
- validation floor and authority state unchanged;
- durable rollback receipt.

A CAS mismatch enters bounded delta review. A non-return is `UNKNOWN` until one pinned readback; there is no blind retry, rewind, force update, or artifact deletion.

## A1 candidate withdrawal

Before A2 wiring or enforced activation, a forward-only branch commit may restore the A0-R tree `a617863d7108beb9ee3a68ad0963b61bd434090f`, where the common pointer is absent and bootstrap candidate blob is `228db268c93d534efa69351a11b18a2f1f74fc1e`. This is candidate withdrawal, not the operational enforced-to-shadow rollback demonstration.

## Fail-closed conditions

- unresolved active Persona registry;
- multiple common current pointers;
- v0.4 or higher-authority conflict;
- authority, validation-floor, independence, Shared Contract, Release, or Production impact;
- unproven injection or rollback route;
- unexpected Persona resolution;
- unbounded dependency closure or required repository-wide scan.

## Claim ceiling

`D1_AUTHOR_CORRECTED_POINTER_CONTROLLED_COMPOSITION_PENDING_AFFECTED_RECHECK_AND_VALIDATOR_RECHECK_NO_ENFORCED_ACTIVATION`
