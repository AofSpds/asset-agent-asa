# M3Top3 Fast-Replay Rebaseline — PMO Direct Dispatch v1.0

PROJECT = AAA
PRODUCT = ASSET AGENT ASA
FROM = AAA-ASA (ASA)
TO = AAA-PMO-ORCHESTRATOR (PMO)
DATE_KST = 2026-09-05 09:25
DISPATCH_CLASS = OWNER_AUTHORIZED / FAST_REPLAY_REBASELINE / NO_RERUN / COVERAGE_LIMITED_RETROSPECTIVE_REPLAY_PREPARATION
OWNER_APPROVAL_BINDING = cd4d02a92de496a38ee682145afc2336e4160f7c

## Objective

Move M3Top3 to the first usable historical scorecard without requiring complete historical provenance/data coverage where the model can safely proceed with explicit missingness or explicit row exclusion.

## Mandatory sequence

1. G1 current baseline bind
   - read-only bind current exact v1 feature schema, scorer, config, weights, contracts, tests, code identities;
   - reuse existing validated evidence where applicable;
   - historical v0.1 package recovery is nonblocking; no additional broad ZIP search;
   - if coherent, mark G1 execution-ready/closed under current Owner direction.

2. G2 denominator rebaseline
   - derive per-window first-Replay population from U127;
   - states: INCLUDE / EXCLUDE_PROVEN / EXCLUDE_UNRESOLVED;
   - use current Owner-approved W1-W8 tuples;
   - separate legal listing provenance from Replay tradability;
   - do not exhaustively close the prior 514-cell queue before execution;
   - preserve exact per-window denominator and exclusion reason counts.

3. G3 data scope rebaseline
   - build a new current price manifest from exact recovered 2024/2025/2026 components;
   - define deterministic Replay calendar from exact price-date set plus official KRX closure evidence;
   - intersect CA reconciliation with the admitted first-Replay population only;
   - collect/use cutoff-safe historical model inputs only for admitted rows;
   - use explicit model missingness semantics; do not require 17/17 fields;
   - if no Opportunity axis is available and no governed score can be produced, exclude as REPLAY_DATA_INSUFFICIENT;
   - unresolved material CA affecting a row/window may exclude that row/window.

4. Golden forward-only close
   - reuse recovered v0.2 fixture package;
   - bind only the controlled expected outputs still required for current Golden mechanics;
   - do not require v0.1 recovery.

5. Validation
   - reuse existing G4 exact-target PASS evidence; no full-suite rerun merely for rebaseline;
   - run one bounded affected-only validation campaign over rebaseline-changed surfaces;
   - no second correction/revalidation loop without a new Owner replan if a blocking finding survives.

6. First scorecard
   - if no blocking finding remains, execute `COVERAGE_LIMITED_RETROSPECTIVE_REPLAY`;
   - report performance together with window-level denominator, included/excluded counts, exclusion reasons, feature coverage/missingness, CA exclusions, and claim ceiling.

## Explicitly outside this critical path

- v0.1 historical ZIP recovery
- complete 514 eligibility-cell closure
- complete 17,272 annotation-slot population
- full-market 2,406 CA-signal closure
- old standalone price-manifest recovery
- complete historical human/LLM outcome-access ledger
- G4 full suite rerun
- Issue #51 portable mutation archive addendum
- EOPT optimization
- Finance HOLD lane
- promotion/release/production

## Scientific / semantic boundaries preserved

- no outcome-based model tuning;
- no post-cutoff backfill;
- missing/NOT_FOUND != zero/false;
- unresolved exclusion != proven ineligible;
- no silent row deletion;
- no clean-OOS / complete-universe / unbiased-population claim;
- first scorecard is retrospective and coverage-limited unless later evidence supports a stronger claim.

## Stop / Owner escalation only on

- material model-semantic change;
- PIT/evidence meaning change beyond the approved normalization;
- outcome access/tuning change;
- new provider/budget/credential/custody authority;
- validation-floor reduction beyond this affected-only authorization;
- release/promotion/production;
- a blocker for which all safe approved include/exclude/missingness routes are genuinely unavailable.

OWNER_ACTION_REQUIRED_NOW = FALSE
PRODUCTION_AUTHORIZED = FALSE
RELEASE_AUTHORIZED = FALSE
MODEL_SEMANTIC_CHANGE_AUTHORIZED = FALSE
PIT_SEMANTIC_CHANGE_AUTHORIZED = FALSE
