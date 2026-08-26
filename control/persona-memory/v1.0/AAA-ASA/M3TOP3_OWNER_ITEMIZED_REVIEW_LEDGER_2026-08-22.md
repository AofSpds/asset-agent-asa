# M3Top3 Owner Itemized Review Ledger

PROJECT = AAA
PRODUCT = ASSET AGENT ASA
PERSONA = AAA-ASA
LEDGER_CLASS = NON_NORMATIVE_OWNER_REVIEW_CONTINUITY
AUTHORITY_SOT = FALSE
DATE = 2026-08-22
PURPOSE = Accumulate Owner-confirmed corrections/approvals during itemized review for one consolidated successor revision of the two M3Top3 v1.1 advisory documents after review completion.

## REVIEW DISPOSITIONS

### J02 — U127 role correction
STATE = OWNER_CORRECTION_ACCEPTED
- U127 remains `M3Top3 Canonical Validation Master Universe` with fixed 127-company membership.
- `Historical Eligible Universe_T` is derived from U127 using PIT business-scope and tradability eligibility.
- Possible outcome/winner-conditioning in U127 membership genesis is an AUDIT ITEM only.
- Do not automatically relabel U127 as a Challenge Universe.
- Do not automatically create a replacement Population Universe.

### J03 — W1-W8 post-exposure reuse
STATE = OWNER_PASS
- W1-W8 are historical evaluation windows; their Winner GT may continue to be used for challenger development/diagnostic/comparative analysis after exposure.
- After exposure they must not be relabeled as clean holdout/OOS superiority evidence.
- Prefer wording: `EXPOSED HISTORICAL DEVELOPMENT / DIAGNOSTIC / COMPARATIVE SET` for successor/challenger use.

### J04 — effective independent sample interpretation
STATE = OWNER_APPROVED
- Approximately 1,016 company-window rows are valid ranking observations but are not 1,016 iid independent experiments.
- Primary independent regime evidence is closer to the eight non-overlapping windows.
- Overlapping daily/weekly replay is for stability/turnover/warning/operational diagnostics, not iid sample inflation.

### J05 — MFE GT and investability separation
STATE = OWNER_APPROVED
- Maintain `3M MFE Rank` as Primary Opportunity-Discovery Ground Truth.
- Evaluate investability separately with Exit/Horizon Return, MAE, Time-to-Peak, Giveback, Peak Persistence, Liquidity and related path-quality metrics.
- Do not retrospectively collapse these planes into a composite GT.
- Future MFE/outcomes must remain outside historical Feature/PIT/Universe inputs.

### J06 — historical annotation hindsight control
STATE = OWNER_APPROVED
- Historical qualitative/scoring-critical annotation shall be performed with post-snapshot outcome/winner information concealed.
- Objective FACT fields should use deterministic extraction/verification rather than mandatory dual coding.
- Material subjective/scoring-critical annotations use independent dual review; material disagreement routes to adjudication.
- Preserve source bundle, snapshot cutoff, annotator/model version, prompt/rubric version, confidence, disagreement and adjudication provenance.
- Apply risk-based dual coding rather than indiscriminate dual coding of every objective field.

### J07 — missingness renormalization and coverage diagnostics
STATE = OWNER_APPROVED_WITH_MODIFICATION
- Preserve the exact original M3Top3-v1 available-component renormalization semantics; do not add a new minimum-coverage or abstention rule retroactively to v1 before first official replay.
- Mandatory v1 diagnostics shall expose Coverage Ratio, Available Feature Count, Missing Feature Bitmap, Effective Weight Vector, Evidence Coverage, and sparse-score/low-coverage flags.
- Full Replay/Failure Atlas shall stratify performance by coverage and inspect whether low-coverage high scores create Critical Miss or deep-tail false positives.
- New minimum-coverage, abstention, confidence penalty, or F08-as-confidence rules are successor/v2 hypotheses unless an exact pre-existing v1 contract proves they were already part of v1.
- Preserve `NOT_FOUND != BUSINESS_NEGATIVE` and do not turn retrieval failure into silent zero/negative scoring.

### J08 — Core B authority currentization and official-entry hold scope
STATE = OWNER_APPROVED
- Preserve the existing Owner remediation direction: current Core B pair is `AAA-MODEL-VALIDATION-DESIGN-ARCHITECT (MOD)` + `AAA-MODEL-DESIGN-VALIDATOR (MODV)` and the stale active organization projection must be superseded through governed successor currentization rather than historical rewrite.
- Before Core B authority coherence is closed, block official Core B semantic authoring through the stale/ambiguous route and block official M3Top3 model-validation / Golden / Full Replay entry or PASS claims that depend on ambiguous routing.
- Do not interpret this as a blanket stop on M3Top3 scientific preparation.
- Continue in parallel: exact v1 recovery, historical data/PIT reconstruction, U127/entity/CA/price readiness, non-semantic evidence collection, test specification, deterministic preservation/diff preparation.
- Final documents shall distinguish `OFFICIAL SEMANTIC / MODEL-VALIDATION ENTRY HOLD` from `PERMITTED PREPARATION / DATA READINESS WORK`.

### J09 — Round-1 material Challenger budget
STATE = OWNER_APPROVED
- The `2~3` limit applies to the first formal material Challenger set, not to the number of research ideas or prototypes.
- Idea/Research Pool and Prototype/Diagnostic work may be broader, subject to PIT/outcome-firewall and journaling discipline.
- Simple baselines such as momentum-only, event-only, revision-only, valuation/base and random/equal-weight controls do not consume the formal material Challenger budget.
- Round-1 material Challengers should be selected after exact v1 Full Replay + Failure Atlas and should represent distinct failure hypotheses rather than cosmetic variants.
- Formal Challenger identities/specifications must be preregistered before their outcome comparison.
- The 2~3 budget is not a permanent lifetime cap; later rounds may add new challengers through new preregistration after additional evidence.

### J10 — staged architecture status and comparison discipline
STATE = OWNER_APPROVED
- Preserve `Candidate Recall → Tail Ranking → Confidence/Risk → Set Construction` as a high-priority successor architecture hypothesis, not as a preselected preferred solution or default winner.
- Compare staged architecture against a direct full-universe ranking architecture and simpler constrained alternatives under matched evaluation conditions.
- Treat Opportunity, Confidence, Risk, Eligibility and Set Construction as separable modeling hypotheses whose value must be demonstrated rather than assumed.
- Preserve `RAW MODEL TOP3` separately from any `SET-POLICY TOP3`; portfolio/set policy gains must not be misattributed to raw ranking-model improvement.
- If an early Recall stage is used, explicitly measure winner recall and the irreversible loss introduced by early candidate exclusion.
- No architecture promotion before comparative evidence; staged architecture remains a strong research hypothesis, not a canonical successor mandate.

### J11 — current-stage statistical inference priority
STATE = OWNER_PASS
- Current-stage primary inference shall emphasize per-window raw metrics, effect sizes, worst-window/tail severity, leave-one-window-out stability, exact/permutation tests, stratified randomization where relevant, power simulation, practical non-inferiority, and regime consistency.
- SPA/MCS/PBO are not discarded; they are secondary/later tools after additional independent regimes and a complete preregistered model-trial registry make their outputs more interpretable.
- DSR is not a universal Top-K model-superiority certificate; reserve it for a separately defined tradable return series where Sharpe-type inference is actually applicable.
- Do not equate `p > 0.05` with no effect when the current sample has low power; report detectable effect/power limits.
- Statistical presentation must not hide one-window dependence or tail failures behind aggregate averages.

### J12 — Raw Model Top3 vs Set-Policy Top3 separation
STATE = OWNER_PASS
- Preserve the raw ranking output as a first-class immutable evaluation object: full Raw Rank, Raw Model Top3 and Raw Model Top10 must remain available even when a downstream set policy is applied.
- Treat Set Construction as a separate versioned policy layer that converts a ranking into an investable set under explicit concentration/liquidity/risk/eligibility constraints.
- Record Set-Policy Top3, every substitution, substitution reason, policy version, effective date, tie-breaking rule and applicable constraints separately from raw model output.
- Do not attribute Set-Policy gains or losses to the ranking model. Evaluate raw Opportunity Discovery and downstream investability/portfolio behavior on separate planes.
- Any formal Set Policy used in comparison must be outcome-blind and versioned/preregistered; retrospective policy tuning requires a successor policy version rather than rewriting prior output.
- Preserve the opportunity cost of substitutions: measure how much raw MFE-rank opportunity is sacrificed or retained when diversification/risk constraints replace a raw Top3 name.

### J13 — Forward Shadow checkpoints vs automatic promotion
STATE = OWNER_PASS
- Treat 3M and 6M as scheduled Forward-Shadow evidence checkpoints, not automatic model-promotion thresholds.
- The 3M checkpoint is the first mature prospective evidence review; assess matured cohort MFE-rank performance, Raw Top3/Top10 health, Critical Miss/deep-tail behavior, investability path, coverage/missingness, PIT integrity, operational reproducibility and ranking turnover.
- The 6M checkpoint extends the evidence review across additional matured cohorts/regime variation and inspects worst cohort, concentration dependence, leave-one-cohort-out stability, practical non-inferiority/superiority, and operational stability.
- Promotion eligibility depends on sufficient matured prospective cohorts and effective independent evidence, preregistered performance/tail-risk criteria, no unresolved material P0, independent validation, and final Owner decision.
- Calendar time alone is not sufficient evidence. If evidence is insufficient at 3M or 6M, extend Shadow rather than forcing promotion or rejection.
- Do not impose a mechanical 12M wait if sufficient governed evidence is available earlier; likewise, do not promote merely because 3M or 6M has elapsed.

### J14 — exact source/model/data/fixture/run lineage
STATE = OWNER_PASS
- Official M3Top3 validation claims must bind to exact Model Release, Dataset Releases, Golden Fixture Set, Replay Run and material evidence lineage rather than a human-readable source list alone.
- Model lineage shall identify the material semantic object through contract/version, code commit/blob/hash, config/scorer identity, feature/ranking/missingness rule versions and related release binding as applicable.
- Released validation data shall identify U127/eligibility, PIT, price, CA, trading-calendar, entity-history and other material inputs through release/path/version/commit/hash/manifest/schema/row-count receipts as applicable.
- Golden fixtures and Replay inputs/outputs require exact identities/hashes and independent expected-output oracles; do not use the same implementation to generate both expected and actual values.
- Material internal evidence artifacts require exact identity. Dynamic external sources should preserve locator, publication/retrieval timing and captured/archive/evidence receipt sufficient to reproduce what was actually observed, rather than forcing meaningless hashes on uncaptured changing pages.
- Preserve a traversable provenance chain from `CLAIM → RUN → MODEL → DATA → SOURCE/FIXTURE` so later revisions cannot silently change the evidentiary basis of an earlier result.
- Exact-identity rigor is mandatory for material validation inputs/outputs, but incidental explanatory references need not be burdened with the same artifact-control level.

### 15 — Gate-first execution ownership and supervisory control
STATE = OWNER_APPROVED_WITH_ROLE_SPLIT
- Preserve the execution doctrine as `PARALLEL PREPARATION + ORDERED EVIDENCE GATES`; preparation may run in parallel, but official downstream evidence/promotion cannot skip prerequisite gates.
- `AAA-PMO-ORCHESTRATOR (PMO)` is the execution commander for this program: it plans and sequences work packets, allocates Persona-injected Agent Threads, manages dependencies/resources/checkpoints, consolidates returns, and drives G0→G9 closure.
- `AAA-ASA (ASA)` is the supervisory-control / owner-facing governance plane: it monitors PMO execution, cross-domain coherence, authority/gate integrity, unresolved P0/P1 risks, evidence sufficiency, and escalation/Owner-decision needs.
- ASA does not replace PMO as day-to-day executor, and PMO does not self-certify governance or Owner decisions.
- This role split is organizational, not a requirement to create separate visible channels for every Persona. Default execution remains PMO-led thread-first orchestration with Git Work Packet / Run Journal / Checkpoint / Return Packet continuity; optional parallel channels remain exception-only.
- Final successor documents shall depict the control stack as `OWNER → ASA SUPERVISORY CONTROL → PMO EXECUTION COMMAND → Persona Agent Threads`, while preserving paired-validator / IVA independence at the relevant gates.

### 16 — explicit M3Top3 model-state ladder
STATE = OWNER_APPROVED_WITH_MODIFICATION
- Use an explicit model-state ladder to prevent implementation recovery, governance freeze, Golden qualification, historical replay evaluation and Champion/promotion from being conflated.
- Current pre-result v1 naming should be simplified to `M3Top3-v1 Pre-outcome Baseline Candidate` rather than prematurely using Champion/Frozen terminology.
- Recommended ladder: `S0 PRE-OUTCOME BASELINE CANDIDATE → S1 EXACT-RECOVERED BASELINE → S2 FROZEN BASELINE-OF-RECORD → S3 GOLDEN-QUALIFIED BASELINE → S4 REPLAY-EVALUATED BASELINE → S5 CHAMPION / PROMOTED MODEL`.
- `Exact-Recovered` means contract/code/config/semantics identity is recovered; it does not itself create Freeze authority.
- `Frozen` requires a governed exact-target freeze decision; `Golden-Qualified` proves implementation-contract conformance, not alpha superiority; `Replay-Evaluated` means historical evaluation completed, not automatic Champion status.
- State transitions are evidence-gated. PMO prepares the evidence/transition package, ASA supervises state-transition integrity, and the required paired validator / IVA / Owner gates remain applicable according to the governing authority level.
- The exact labels may be shortened in dashboards, but no label may imply evidence or authority that has not been obtained.

### J02 Amendment / 17 — U127 current-phase freeze vs future universe refinement
STATE = OWNER_CORRECTION_ACCEPTED / ITEM17_AMENDED
- Supersede only the permanence implied by the earlier phrase `fixed 127-company membership` in J02. It means `temporarily fixed for the current model-detection / validation phase`, not permanently immutable membership.
- Current U127 was assembled by collecting relevant listed peer/sector companies so that the current M3Top3 model can be detected, debugged and validated with sufficient breadth and discrimination.
- Until the model-detection/refinement work becomes sufficiently precise, U127 membership is held stable as the current working/canonical validation universe so denominator drift does not contaminate the present validation program.
- After the model and universe-selection logic become more precise, the validation universe may be re-examined and formally confirmed, expanded, reduced or otherwise succeeded through a new version/release. Do not silently mutate the historical U127 release or rewrite prior replay denominators.
- `Historical Eligible Universe_T` for the current U127 phase remains derived from the then-current U127 release using PIT business-scope and tradability eligibility; membership, historical eligibility and feature/data coverage remain separate concepts.
- Future universe refinement is not treated as a defect in U127 and does not automatically reclassify U127 as a Challenge Universe. U127 remains the current-phase M3Top3 validation master until a governed successor universe is defined.
- Any later successor universe must preserve lineage to U127 and allow results to be distinguished by universe release/version so performance changes are not misattributed to the model when they are caused by denominator/membership changes.

## DOCUMENT REVISION RULE
- Do not regenerate the two advisory documents after each item.
- Continue accumulating Owner dispositions here.
- After itemized review is complete, revise both M3Top3 v1.1 advisory documents once into a consolidated successor revision.
