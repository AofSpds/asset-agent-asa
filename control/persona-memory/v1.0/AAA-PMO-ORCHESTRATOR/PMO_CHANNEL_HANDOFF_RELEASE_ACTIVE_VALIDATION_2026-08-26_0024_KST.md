# PMO Channel Handoff — Release Active Validation / Resume Later

PROJECT = AAA
PRODUCT = ASSET AGENT ASA
PERSONA = AAA-PMO-ORCHESTRATOR (PMO)
DIRECTIVE_CLASS = OWNER_CHANNEL_SUCCESSION_RUNTIME_CONTROL
RECORDED_AT = 2026-08-26 00:24 KST
AUTHORITY_SOT = FALSE

## OWNER DIRECTIVE

The prior PMO visible channel reached its conversation/context limit. Before successor PMO execution begins, release/terminate all validation, reviewer, subagent, worker, measurement, and other in-flight compute associated with the prior PMO runtime instance.

This is a runtime/resource handoff rule. It does NOT invalidate or reopen completed validation evidence.

## REQUIRED DISPOSITION

1. PRIOR_PMO_RUNTIME = RETIRED_FOR_CONTEXT_LIMIT.
2. ALL_ACTIVE_VALIDATION_WORKERS = RELEASE_OR_TERMINATE.
3. ALL_ACTIVE_SUBAGENTS_AND_BACKGROUND_WORKERS = RELEASE_OR_TERMINATE unless independently governed outside the prior PMO runtime and explicitly proven still required.
4. NO_NEW_VALIDATION_OR_EXECUTION_DISPATCH until successor PMO completes read-only reconciliation.
5. Preserve every already sealed validation receipt, evidence artifact, issue comment, commit/tree/hash, and gate transition exactly as durable history.
6. Do NOT mark completed validation as failed, superseded, or undone merely because its runtime process is released.
7. Do NOT rerun sealed G4 or other sealed validation solely because the old channel ended.
8. Any partial/in-flight validation result that was not durably sealed before retirement is treated as UNSEALED_PARTIAL_EVIDENCE; preserve if recoverable, but it creates no PASS claim.
9. Successor PMO may reacquire validators/reviewers and resume only the still-open validation units after Git/branch/worktree/issue reconciliation.
10. Before material continuation, successor PMO must establish one exclusive execution lease and confirm no old PMO worker/validator lease remains active.

## HANDOFF MODEL

`OLD PMO CHANNEL/WORKERS STOPPED -> DURABLE GIT STATE PRESERVED -> NEW PMO READ-ONLY RECONCILIATION -> EXCLUSIVE LEASE -> RESUME OPEN WORK ONLY`

## CURRENT DURABLE CLAIM CEILING

Use latest governed/durable evidence after reconciliation. Last observed continuity state remains:
- G4 exact runtime mechanism: SATISFIED_WITH_FINDING.
- G1/G2/G3 and integrated checkpoint: open/not closed unless newer durable evidence proves otherwise.
- EOPT measurement/mutation: not authorized until actual gates pass.
- Full W1-W8 scale-out: not authorized until actual gates pass.

## OWNER ACTION

No Owner manual relay of old conversation context is required. New PMO must recover from Git. The only runtime-side action outside Git is to ensure the old visible PMO execution/Stop indicator and any visible in-flight workers are actually stopped before successor compute is started.
