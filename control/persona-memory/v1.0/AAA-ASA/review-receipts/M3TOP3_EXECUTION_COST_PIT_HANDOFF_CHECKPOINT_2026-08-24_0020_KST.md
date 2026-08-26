# M3Top3 Execution / Cost / PIT Handoff Checkpoint

PROJECT = AAA
PRODUCT = ASSET AGENT ASA
PERSONA = AAA-ASA (ASA)
CHECKPOINT_CLASS = PERSONA_CONTINUITY / OWNER_CORRECTION / EXECUTION_OBSERVATION
AUTHORITY_SOT = FALSE
TIME_KST = 2026-08-24 00:20 KST

## 1. CURRENT EXECUTION INTERPRETATION
- The currently running PMO program is the approved M3Top3 WP0-WP9 execution WBS, not a WP4-only task.
- Current momentary focus is still the safe-runtime / lineage / G1-G4 integration area plus bounded historical recovery/eligibility pilot work.
- Latest Owner-shared execution screen shows:
  - Owner approval / IVA boundary / exact v1.2 baseline line fixed: COMPLETE.
  - v0.4 fail-closed runtime correction + internal engineering evidence + Git evidence fixed: COMPLETE.
  - G1 baseline identity, G2 universe/exposure, G3 data/annotation audit: COMPLETE.
  - Current: exact v1.2 precedence cleanup + G1-G4 integrated checkpoint publication.
  - Next: bounded recovery/eligibility sample, W4x3 non-scoreable pilot, evidence hash/JSON/reproducibility QC and gate-delta report.
  - Subagents shown: 21 completed, 1 active at the time of the screenshot.
  - 514 eligibility procedural samples were referenced; a W4x3 representative pilot was executed, with expected FAIL_CLOSED behavior where exact evidence IDs were unavailable.
- Do NOT infer that the whole two-year historical PIT replay is already running. The current activity is still audit/safety/pilot work before full scale-out.

## 2. FULL PROGRAM SCOPE CLARIFICATION
- Owner corrected prior assistant wording: the current PMO execution WBS itself DOES include the later Historical PIT/Data recovery, Freeze/Golden, First Honest Replay, Failure Atlas, Challengers, and Forward Shadow setup.
- Therefore: `current run != full two-year PIT currently executing`, but `current WBS includes the later W1-W8 historical PIT/replay work`.
- WP9 prospective 3M/6M evidence cannot be completed instantly because future time must pass; the program can set up and begin shadow tracking.

## 3. W1-W8 INTERPRETATION
- W1-W8 are eight non-overlapping ~3-month historical evaluation windows across roughly two years.
- Each window has a PIT snapshot/cutoff, then ~3M outcome observation.
- U127 x 8 implies up to about 1,016 company-window rows, but these are not 1,016 iid independent experiments; independent regime evidence is closer to eight windows.
- The intended historical work is NOT daily PIT for every trading day across two years.
- After W1-W8 are exposed, they remain valuable development/diagnostic/comparative data for successor Challengers but are no longer clean holdout/OOS evidence.

## 4. OWNER COST CONCERN / TUNING DIRECTION
- Owner reports the current run has already exceeded 50 hours and approximately half of a USD 200 Pro allowance/token budget appears consumed.
- Owner expects the current run may reach about 100 hours and explicitly considers cost/performance tuning important.
- Owner direction/working preference:
  1. Do not interrupt the current safety-building run merely to tune it.
  2. Finish and seal the current safe code/runtime evidence first.
  3. Immediately after closure, perform semantic-neutral cost/performance tuning before full PIT scale-out.
  4. Then run a stratified calibration pilot, budgeted up to about 10 days but preferably stop earlier when estimates converge.
  5. Use the pilot to forecast full W1-W8 token/wall-clock cost before committing to full-scale recovery/replay.
- Candidate telemetry for the tuning/pilot checkpoint: token per company-window, wall-clock per company-window, retrieval count, cache-hit rate, source-reuse rate, validator-token share, deterministic-code share, retry rate, blocked/unverified rate, p50/p90/p95, and easy/medium/hard case stratification.
- Suggested pilot design discussed: include all W1-W8 with a stratified sample of companies/cases rather than only one window; roughly 64-96 company-window observations can be enough for cost calibration if workload diversity is represented.
- Pilot stopping rule should be estimate convergence rather than blindly using all 10 days; e.g. total-token and wall-clock forecast changes <~10% over repeated checkpoints, with hard-tail p95 stable and all W1-W8 represented.

## 5. PIT DATA ARCHITECTURE UNDERSTANDING / OWNER DIRECTION
- Owner recognized that the long-term value comes from preserving model-neutral historical facts/evidence separately from feature interpretation and model weights.
- Preferred conceptual layering:
  1. Raw Source / Evidence / Fact layer: source identity, publication timestamp, factual content, price/financial/tradability/corporate-action evidence; append-only/immutable-by-release as much as possible.
  2. PIT normalization/admission layer: company/date normalization, cutoff availability, PIT_VERIFIED / UNVERIFIED / LATE / CONFLICT, eligibility/tradability, NOT_FOUND/PARTIAL/STALE, etc.
  3. Annotation / Feature interpretation layer: qualification, design-win, installed base, PO, backlog, shipment, customer CAPEX, utilization, stage, Conversion Visibility, Recognition, Expectations Gap, etc.; versioned and separable from raw fact.
  4. Model layer: F01-F09 mapping, transforms, weights, score, rank, Top3; freely versioned through Challengers after v1 replay.
  5. Outcome layer: 3M MFE, return, MAE, time-to-peak, giveback, etc.; separated from feature/PIT input.
- Owner's latest clarification question was whether the current collection is mainly the immutable layer. Correct continuation answer: `Yes, primarily the durable raw evidence/fact + provenance/PIT-admission substrate is what should be treated as the reusable invariant asset, but the current WP3 work also creates versioned normalization/annotation metadata; it is not raw-source-only. The important rule is to keep fact/evidence separate from interpretation/weights so future models can reprocess the same corpus.`
- If later model tuning reveals a missing explanatory variable, collect only the additional historical evidence needed for that candidate feature and append a new data/evidence release rather than overwriting the original corpus.

## 6. MODEL RESEARCH PURPOSE
- The purpose of the full historical replay is not merely to print Top3. It is to preserve the full U127 rank and feature/score/outcome behavior so the model can be analyzed and improved.
- Frozen v1 must be replayed honestly before outcome-informed tuning.
- After replay: Full Rank + Top3/Top10 + Critical Miss/deep-tail + outcome metrics -> Failure Atlas -> 2-3 material Challengers -> comparison -> future Shadow evidence.
- A new feature or data field may be added later if Failure Atlas indicates it is needed; the corpus should support incremental enrichment.
- Raw facts should not embed model weights. Interpretation, feature mappings, transforms, and weights are versioned above the corpus.

## 7. CURRENT PROGRESS ESTIMATION DISCIPLINE
- Do not inflate progress merely because wall-clock time passed.
- Prior executing-agent explicit estimate was overall P0 rebase ~35-40% and R-WP4 ~70%; later Owner-shared screenshot showed additional G1/G2/G3 completion and G4 integration/pilot activity.
- Advisory estimate after that screenshot was roughly overall concentrated WP0-WP8 program ~40-50% (center ~45%), with safe-runtime/base-build substantially further along. Treat this only as an observational estimate, not a governed gate claim.
- For the next channel, prefer new execution-screen evidence or exact Git checkpoints over stale percentage estimates.

## 8. SUCCESSOR FIRST CONTINUATION
1. Bootstrap AAA Project Instructions and resolve `AAA-ASA (ASA)` unless Owner explicitly selects another Persona.
2. Load common PROJECT_MEMORY, AAA-ASA MEMORY, WORKLOG, then this exact checkpoint.
3. Do not ask Owner to restate the above context.
4. If Owner continues the pending PIT question, answer that current collection is primarily building the durable invariant evidence/fact substrate but also performs versioned PIT normalization/admission/annotation; model weighting/tuning remains a separate layer.
5. If Owner shares a newer execution screenshot, compare it against the latest known G1-G4/pilot state and update progress without interrupting the running work.
6. Preserve the Owner cost-tuning requirement as a post-current-run checkpoint before full historical scale-out.

## 9. REFERENCES TO KEEP IN VIEW
- Current approved operational decomposition: `M3Top3_PMO_Initial_Execution_Workplan_v1.0_2026-08-22` (conversation/upload artifact; Git exact authority should be recovered through current governed refs).
- Exact validated v1.2 plan remains the baseline; do not silently modify validated bytes/semantics without appropriate revalidation.
- Existing Owner-reviewed scientific constraints: v1 first honest replay before tuning; U127 current-phase canonical working universe; W1-W8 historical windows; 3M MFE Rank primary Opportunity GT; investability separate; Round-1 material Challengers 2-3.

END_CHECKPOINT
