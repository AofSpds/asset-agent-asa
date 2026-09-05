# M3Top3 Fast-Replay Rebaseline — Owner Approval Binding v1.0

PROJECT = AAA
PRODUCT = ASSET AGENT ASA
PERSONA = AAA-ASA (ASA)
DATE_KST = 2026-09-05 09:23
DECISION_CLASS = OWNER_APPROVAL / REPLAY_READINESS_REBASELINE / CLAIM-EXECUTION_SEPARATION
AUTHORITY_SOT = FALSE
PURPOSE = Persist exact Owner decisions for PMO dispatch and governed current-state reconciliation. This continuity record does not itself mutate model semantics, release state, production authority, or validator verdicts.

## Owner approval sequence

Owner first approved the G1 handling direction, then approved six G2/G3 normalization policies, then explicitly approved all ten additional normalization policies.

### G1 approved handling

1. Historical v0.1/v0.2 research ZIP exact recovery is removed as a Replay hard gate.
2. v0.2 exact recovered artifact is preserved as evidence.
3. v0.1 non-recovery may remain a nonblocking historical-provenance limitation; no further open-ended ZIP search is required for first Replay.
4. Current M3Top3 v1 exact contract/code/config/weights/tests binding is checked once read-only; if coherent, G1 closes for execution.
5. If a genuinely missing current-model artifact appears, PMO/ASA must present immediate Owner routes (adopt/recreate/claim-downgrade) rather than conduct multi-day unbounded recovery.

### Six G2/G3 policies — APPROVED

1. G2: critical eligibility-unresolved company-window rows may be excluded from first Replay rather than forcing exhaustive closure.
2. G2: legal listing provenance is separated from Replay tradability; valid entry-day market data may serve as Replay-tradability evidence under the rebaseline policy.
3. G2: the already Owner-approved W1-W8 exact tuples are bound as current window authority; historical-origin search is no longer a first-Replay blocker.
4. G3: old standalone price-manifest recovery is ended as a hard gate; the exact current 2024/2025/2026 price components may be bound into a new current manifest.
5. G3: corporate-action closure is reduced from full-market completeness to the first-Replay company-window population; unresolved material CA affecting a row/window may exclude that row/window.
6. G3: exact price-date set plus official KRX closure-day evidence may be used to define the deterministic Replay calendar; historical annotation scope is pruned to G2-admitted rows and model-required inputs.

### Ten additional policies — APPROVED

1. First result may be executed as `COVERAGE_LIMITED_RETROSPECTIVE_REPLAY`; clean-OOS / complete-universe / production claims remain separate and may stay unproven.
2. Complete historical human/LLM outcome-access ledger is not required to execute the first retrospective Replay; any clean-OOS claim remains unavailable without the relevant evidence.
3. Exhaustive collection of 17 historical annotation fields for all 1,016 company-window rows is abandoned. Existing scorer missingness semantics are used.
4. If an included company-window has no available Opportunity axis and therefore cannot obtain a score, it is excluded as `REPLAY_DATA_INSUFFICIENT` with denominator/exclusion accounting preserved.
5. Historical HTTP headers/access-clock receipts are not universally required for first Replay when official source identity, content digest, and publication/effective time sufficiently establish cutoff-safe provenance. Claim ceiling must match available evidence.
6. Model freeze is separated from data-readiness completeness. The current exact v1 code/config/weights may be frozen before all historical data gaps are closed.
7. Existing G4 exact-target PASS evidence is reused; the full 261/75/57/400 validation suites are not rerun merely for this rebaseline.
8. EOPT optimization work and the separate Finance HOLD lane are removed from the first-scorecard critical path.
9. The recovered v0.2 Golden fixture package may be used; only the missing controlled expected-output bindings required for the current Golden check are filled forward-only. v0.1 recovery is not required.
10. After G1/G2/G3 rebaseline, validation is one bounded affected-only campaign on changed surfaces, then proceed to Replay if no blocking finding remains.

## Governing execution principle

`MISSING_OR_UNRESOLVED != PROJECT_STOP` by default.

For first Replay:
- preserve master/raw records;
- classify each relevant company-window as included, proven-excluded, unresolved-excluded, or data-insufficient-excluded;
- preserve explicit missingness for model inputs when scorer semantics allow it;
- never convert absence into zero/false business facts;
- never silently delete rows;
- report denominator, exclusion counts/reasons, feature coverage, and claim limitations alongside performance.

## Claim boundary

These approvals authorize a faster, coverage-limited retrospective evaluation route. They do NOT authorize:
- production or release;
- model promotion/champion status;
- semantic tuning against outcomes;
- silent hindsight backfill;
- claim that excluded/unresolved rows were proven ineligible;
- claim that the resulting Replay is complete-universe, clean holdout, or unbiased OOS evidence;
- Finance lane resume;
- EOPT mutation.

## PMO next route

1. Reconcile Issues #52/#53/#54 and any stale master-status artifacts to this Owner direction forward-only.
2. Bind the current exact M3Top3 v1 baseline from existing feature schema/scorer/config/weights/tests and validated Workbench/G4 evidence.
3. Materialize window-level Replay denominator using include/exclude/data-insufficient states; do not exhaustively research every unresolved G2 cell.
4. Build current price manifest/calendar authority equivalent from exact recovered price components and official closure evidence.
5. Intersect CA work with the admitted Replay population only.
6. Build historical model inputs using available cutoff-safe evidence and explicit missingness; exclude only rows that cannot obtain a governed score or whose critical eligibility/CA state remains unsafe.
7. Complete only the forward-only Golden expected-output bindings actually required.
8. Run one affected-only validation campaign.
9. If no blocking finding remains, run `COVERAGE_LIMITED_RETROSPECTIVE_REPLAY` and return the first scorecard with coverage/exclusion/claim-ceiling disclosure.

OWNER_ACTION_REQUIRED_WITHIN_THIS_APPROVED_SCOPE = FALSE
SECOND_APPROVAL_REQUIRED = ONLY IF semantic meaning, PIT meaning, outcome usage/tuning, provider/budget/custody authority, validation-floor reduction, release/promotion/production, or other Owner-reserved boundary changes.
