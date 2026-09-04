# Owner direction — flexible exclusion for unrecoverable company/window data

PROJECT = AAA
PRODUCT = ASSET AGENT ASA
PERSONA = AAA-ASA (ASA)
MEMORY_CLASS = APPEND_ONLY_OWNER_DIRECTION_CONTINUITY
AUTHORITY_SOT = FALSE
RECORDED_AT_KST = 2026-09-05 08:27

## Owner statement
The Owner states that if some company data cannot be collected, the model/replay should be flexible enough to exclude those affected companies rather than letting a small number of missing records block the whole program.

## Scope boundary
This record preserves Owner intent only. It does not itself change G1/G2/G3 governed semantics, denominator rules, model semantics, PIT rules, or validation status.

The Owner direction is interpreted narrowly as applicable to company/window-level data unavailability after bounded evidence recovery. It does not resolve G1 original-model identity, does not authorize outcome-conditioned exclusion, and does not waive global source/custody problems that affect many securities or all windows.

## ASA proposed normalization for governed follow-up
- Keep U127 as the current-phase master validation universe for auditability.
- Derive a per-window Replay Eligible Universe from U127.
- For each company-window, distinguish:
  1. ELIGIBLE_PROVEN — listing/tradability and critical PIT/price/CA prerequisites are proven.
  2. EXCLUDE_UNRESOLVED_CRITICAL — required eligibility/critical source evidence remains unresolved after bounded recovery.
  3. EXCLUDE_PROVEN_INELIGIBLE — known not listed/not tradable/out of scope at cutoff.
  4. KEEP_WITH_FEATURE_MISSINGNESS — company is eligible but a non-critical feature is UNKNOWN/NOT_FOUND/PARTIAL; preserve explicit missingness rather than dropping the company by default.
- Exclusion decisions must be cutoff-time and outcome-blind, with reason codes and denominator readback per window.
- No permanent company removal is implied when only one or some historical windows are unresolved.
- A coverage floor/comparability rule, if desired, requires a separate governed Owner disposition; none is created here.

## Current blockers this does not automatically solve
- G1 exact original v1 package identity remains open.
- G2 historical proof/custody and eligibility cells remain open under the current rule set until a governed successor rule is adopted.
- G3 KRX corporate-action/calendar source authority gaps remain broader source-access issues and may not be reducible to a few-company exclusion.

NEXT_ROUTE = ASA proposes a bounded G2/G3 gate-policy correction packet after current Workbench C1 affected review returns, if the Owner wants to apply this direction operationally.
