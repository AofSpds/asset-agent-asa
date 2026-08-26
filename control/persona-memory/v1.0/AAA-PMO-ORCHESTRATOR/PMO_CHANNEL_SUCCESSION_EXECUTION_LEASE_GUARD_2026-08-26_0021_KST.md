# PMO Channel Succession Execution Lease Guard

PROJECT = AAA
PRODUCT = ASSET AGENT ASA
PERSONA = AAA-PMO-ORCHESTRATOR (PMO)
RECORDED_AT = 2026-08-26 00:21 KST
TRIGGER = OWNER_DUPLICATE_EXECUTION_CONCERN_AFTER_CONTEXT_LIMIT_SUCCESSION
AUTHORITY_SOT = FALSE

## PURPOSE
Prevent duplicate PMO dispatch or duplicate work after a visible PMO channel reaches context limit and a successor PMO channel is opened.

## RUNTIME ROLES
- OLD_PMO_CHANNEL = RETIRED_CONTEXT_LIMIT
- CURRENT_ASA_CHANNEL = SUPERVISORY_ONLY_FOR_THIS_PROGRAM; MUST NOT duplicate PMO execution command
- SUCCESSOR_PMO_CHANNEL = MAY_RESUME_ONLY_AFTER_RECONCILIATION_AND_EXCLUSIVE_EXECUTION_LEASE

## SUCCESSOR LEASE RULE
Before any new material dispatch, the successor PMO MUST:
1. bootstrap and recover the latest durable program state;
2. read the PMO channel succession checkpoint and latest parent queue/issues;
3. inspect relevant branch/worktree heads, open PRs/issues, receipts and durable run journals;
4. detect any still-live or newly-arrived in-flight task/output from the retired channel or its agents;
5. adopt or wait for existing in-flight work rather than redrive it;
6. identify the exact latest open work units;
7. record an exclusive successor execution-lease receipt naming the units it is taking over and the evidence used to conclude no competing executor is active for those units.

Until this reconciliation is complete:
`MATERIAL_REDISPATCH = PROHIBITED`

If executor status cannot be determined:
`EXECUTION_LEASE_RECONCILIATION_REQUIRED`
and no duplicate material dispatch is allowed.

## NO-DUPLICATION RULES
- Do not restart WP0-WP9 because a conversation ended.
- Do not rerun sealed G4 solely because of channel succession.
- Do not duplicate G1/G2/G3 work if the prior run already has active or newly completed durable outputs.
- New work is permitted only for still-open units after current-state reconciliation.
- A channel succession event is not REWORK unless actual work must be repeated.
- ASA may supervise, reconcile and escalate, but does not become a second PMO executor.

## SUCCESSOR FIRST REPORT
The successor PMO should report at minimum:
- `OLD_PMO_CHANNEL=RETIRED_CONTEXT_LIMIT`
- `IN_FLIGHT_RECONCILIATION=PASS|OPEN|CONFLICT`
- `SUCCESSOR_EXECUTION_LEASE=ACQUIRED|NOT_ACQUIRED`
- exact open units adopted
- exact existing units not redriven
- latest durable refs
- any conflict requiring Owner/ASA attention

## CURRENT PROGRAM BOUNDARY
This guard does not change model semantics, gates, validation claims or program authority. Governed current Git state remains superior. This file is continuity/duplicate-prevention guidance only.
