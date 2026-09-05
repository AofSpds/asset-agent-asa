# OWNER-AUTHORIZED M3Top3 F05-R0 READINESS — PMO EXECUTION REQUEST

PROJECT = AAA
PRODUCT = ASSET AGENT ASA
FROM_PERSONA = AAA-ASA (ASA)
TARGET_PERSONA = AAA-PMO-ORCHESTRATOR (PMO)
CURRENT_PERSONA_LOCK = AAA-ASA (ASA)
DATE_KST = 2026-09-05 21:19 KST
CLASS = OWNER_AUTHORIZATION / BOUNDED_READONLY_EXECUTION_DISPATCH / F05_READINESS
AUTHORITY_SOT = FALSE

OWNER_DECISION = APPROVE
OWNER_TEXT = "다음 단계 가시죠"

EXECUTION_AUTHORIZED = TRUE
PRODUCTION_AUTHORIZED = FALSE
MODEL_SEMANTIC_CHANGE_AUTHORIZED = FALSE
PIT_SEMANTIC_CHANGE_AUTHORIZED = FALSE
ELIGIBILITY_SEMANTIC_CHANGE_AUTHORIZED = FALSE
SCORING_OR_F05_MATERIALIZATION_AUTHORIZED = FALSE
NEW_PROVIDER_OR_CREDENTIAL_AUTHORIZED = FALSE
PAID_SOURCE_OR_BUDGET_AUTHORIZED = FALSE
MAIN_MUTATION_AUTHORIZED = FALSE
MERGE_RELEASE_PRODUCTION_AUTHORIZED = FALSE

## 0. OWNER-FACING PURPOSE

F05 is the M3Top3 market-positioning feature. It asks whether the market has begun to recognize a company's thesis while avoiding over-credit when price/attention evidence already looks saturated.

This execution does NOT calculate F05 scores. It determines whether the already-held historical KRX-derived market data and current governed model definition are sufficient to calculate F05 safely for the W1 INCLUDE cohort without inventing new model semantics.

The immediate goal is to answer five bounded questions:
1. Do the W1 INCLUDE companies have sufficient pre-cutoff price/volume history for the required lookbacks?
2. Which rows/companies may be distorted by corporate actions or trading suspensions?
3. Can the W1 57-company benchmark denominator be constructed exactly from the bound historical population?
4. Are the upstream formulas for 20d/60d return, universe equal-weight return, and turnover/volume acceleration already governed and recoverable?
5. Can all inputs be constructed using observations ending on or before the W1 snapshot cutoff without outcome leakage?

## 1. GOVERNING PREPARATION RECORD

SOURCE_PREPARATION =
control/persona-memory/v1.0/AAA-ASA/runs/2026-09-05/2055_M3TOP3_NEXT_PROCESS_PREPARATION_F05_READINESS_FIRST_v1.0.md

SOURCE_PREPARATION_BLOB = f559aeb09f8e494410826f0a406f3174db2f6c66

ASA_DISPATCH_BRANCH_AT_AUTHORIZATION = task/aaa/asa-pmov-review-dispatch-20260905
ASA_DISPATCH_BRANCH_PREWRITE_HEAD = e3595528d0b6f12550f5944c61cc434c14577572
MAIN_AT_AUTHORIZATION = 950bc98b0702cd5564e3d7b24a6624d9818dfbb9

## 2. EXACT INPUT IDENTITIES ALREADY RECONFIRMED BY ASA

The currently mounted project copies were read-only hash checked before dispatch and match the previously bound components exactly:

- marcap-2024.parquet
  - bytes = 24,572,111
  - SHA256 = b0c38943e67637d5faf88429880092cf0f46a394be39860dd3bcd0b04231bccb
- marcap-2025.parquet
  - bytes = 25,153,419
  - SHA256 = 2bfd93c217eb74263bc5020b23fa6debb6b02531c11eaccc2826639bc191559e
- marcap-2026.parquet
  - bytes = 16,198,533
  - SHA256 = 5da710a2fc56f8fe9b1f5126295cc30c3b15c0ee35d28ba808a505ec4a2243c1

BOUND_PRICE_DATASET_IDENTITY_SHA256 = 419893f0dc8c08019a746182135630cc5f94d6e7ebc2874d5bd23cb54c0a72f7
BOUND_PRICE_SOURCE_SEMANTICS = RAW_IMMUTABLE_NOT_PRICE_CANONICAL

The exact W1 population must be derived from the already-bound G3-E population object, not reconstructed from today's universe:

POPULATION_REVISION = 69a1e7b
POPULATION_PATH = control/m3top3/recovery/2026-08-26/fast-close-worker-results/g3-annotation-candidate/G3_E_ANNOTATION_INGEST_QUEUE_v0.1.jsonl.gz
POPULATION_GIT_BLOB = 4b3cfbfa9969abe2bd6dff5fdbfeb2db9d31cdae
POPULATION_SHA256 = 8b3671d662457aef8c1a5595b33a85a27e08aaee56238e7218f1df0b4df78353
POPULATION_TOTAL_ROWS = 1016
W1_OUTER_ROWS = 127
W1_INCLUDE_EXPECTED = 57
W1_EXCLUDE_PROVEN_EXPECTED = 8
W1_EXCLUDE_UNRESOLVED_EXPECTED = 62
W1_SNAPSHOT_CUTOFF_DATE = 2024-08-09
W1_SNAPSHOT_CUTOFF_AT = 2024-08-09T23:59:59+09:00

## 3. EXISTING F05 MODEL CONTRACT — DO NOT CHANGE

REFERENCE_MODEL_CODE_REVISION = c15cbfa9bbedcb3b388b9d101b269ced2fc83bc5
REFERENCE_FEATURE_SCHEMA_BLOB = 2550f781c2a901c0faada95dfc4a788503ec669b
REFERENCE_FEATURE_ENGINE = tools/m3top3/features_v1.py / existing F05 implementation
REFERENCE_CONFIG = tools/m3top3/configs/m3top3_v1.0.json
REFERENCE_CONFIG_SHA256 = eecde22a7744cff505c624bb6f0bdb11714352a122632238ea68d9cd0fbacb98
F05_WEIGHT = 20

Existing governed F05 inputs include:
- trailing_20d_total_return
- trailing_60d_total_return
- eligible_universe_equal_weight_returns
- turnover_or_volume_acceleration
- valuation_percentile_if_available [optional]
- report_or_news_diffusion_percentile_if_available [optional]

Existing scorer-side F05 transform is already bound and must remain unchanged:
- 0.50 * percentile(20d universe-relative return)
- 0.30 * percentile(60d universe-relative return)
- 0.20 * percentile(turnover acceleration)
- existing saturation penalty rules only

This task is specifically to determine whether the upstream construction of those raw F05 values is already defined and whether the data are ready.

## 4. STAGE 0 — F02-R1 REMOTE PRESERVATION NON-BLOCKING CHECK

The previously approved F02-R1 remote preservation remains unresolved at dispatch time:

EXPECTED_REMOTE_BRANCH = task/aaa/m3top3-f02-r1-multi-company-input-repair-20260905
REMOTE_REF_READBACK_AT_DISPATCH = NOT_FOUND_404

PMO shall:
1. If the exact local final F02-R1 task branch is still available in its execution environment, perform the already-approved no-rerun push/readback closure to that exact remote branch.
2. If the local branch/object is unavailable, record `F02_R1_REMOTE_PRESERVATION_BLOCKED_LOCAL_STATE_UNAVAILABLE` and do not recreate, rerun, or synthesize it.
3. This backup condition is NOT a scientific dependency of F05-R0 and must not block the bounded read-only readiness check.

No F02 discovery, scoring, validation rerun, or result reconstruction is authorized.

## 5. F05-R0 EXECUTION SCOPE

### CHECK A — EXACT W1 COHORT MATERIALIZATION

Read the exact bound G3-E object and materialize only the W1 57 `ELIGIBLE` company/code identities.

Required evidence:
- exact source object digest verification
- W1 partition count = 57/8/62
- 57 unique company_id / KRX code bindings
- no current-universe substitution

If the source object cannot be read or digest/count validation fails:
TERMINAL = HOLD_DATA_NOT_READY
STOP that dependent lane; do not reconstruct from memory.

### CHECK B — PRE-CUTOFF MARKET-DATA COVERAGE

Using only observations with Date <= 2024-08-09, measure the data availability needed by the existing F05 contract.

Do NOT assume an upstream return formula that is not governed.
For readiness accounting only, report raw availability sufficient to support candidate lookback construction:
- exact available trading-date count per company before/on cutoff
- whether at least 21 distinct trading-date price observations exist ending at/before cutoff
- whether at least 61 distinct trading-date price observations exist ending at/before cutoff
- availability of Volume
- availability of Amount if present
- availability of Stocks if present
- duplicate Date+Code keys
- null/zero/non-positive price anomalies
- zero-volume / missing-volume rows
- long trading gaps / suspension-like gaps

The 21/61 observations are a DATA-AVAILABILITY diagnostic only. They must NOT be claimed as the governed definition of 20d/60d return unless an exact upstream formula is recovered in CHECK D.

Output exact counts:
- W1_57 price-lookback-ready diagnostic count
- volume-ready count
- amount-ready count if field exists
- stocks-ready count if field exists
- exception company list with row/date evidence

### CHECK C — CORPORATE ACTION / PRICE DISCONTINUITY READINESS

The source is RAW_IMMUTABLE_NOT_PRICE_CANONICAL. Therefore raw discontinuities may not be silently interpreted as market recognition momentum.

Within the bounded W1 lookback interval only:
- inspect any existing corporate_action_flag / adjustment_factor fields if actually present;
- inspect existing governed CA receipts/ledgers already in repository/current bound inputs;
- identify large raw price/share-count discontinuities or long suspension-like gaps as `CA_OR_PRICE_DISCONTINUITY_REVIEW_REQUIRED` candidates;
- do not invent adjustment factors;
- do not use post-cutoff corporate-action knowledge to rewrite pre-cutoff observations;
- distinguish source-verified CA from heuristic discontinuity flags.

Return:
- companies with no observed bounded CA/discontinuity concern
- companies with source-verified CA concern
- companies with heuristic price/share discontinuity requiring review
- unresolved CA coverage ceiling

Do not claim `NO_CA` merely because no CA record was found.

### CHECK D — EXACT UPSTREAM DEFINITION RECOVERY

Search the governed Git history/current model artifacts for exact pre-existing definitions of ALL of the following:

D1. trailing_20d_total_return
D2. trailing_60d_total_return
D3. eligible_universe_equal_weight_return construction
D4. turnover_or_volume_acceleration / turnover_acceleration
D5. price adjustment / dividend / `total_return` semantics required by D1/D2
D6. denominator treatment when a W1 INCLUDE company lacks a required market row or is suspended

Search locations should include, as relevant:
- model feature schema / implementation config
- model architecture/design records
- prior M3Top3 execution packets and validation reports
- price-control / CA / replay-control artifacts
- tests only as evidence of executable expectations, not as semantic authority by themselves
- Persona memory/worklog only as lower-priority continuity evidence

For each D1-D6 return exactly one of:
- `EXACT_GOVERNED_DEFINITION_RECOVERED`
- `PARTIAL_DEFINITION_ONLY`
- `NO_GOVERNED_DEFINITION_FOUND`

Do not convert conventional finance practice into a governed definition.
Do not infer formulas from synthetic test fixtures.

If any required D1-D6 remains partial or absent, readiness terminal cannot be `READY_FOR_F05_R1`.

### CHECK E — W1 BENCHMARK FEASIBILITY

Assess whether the exact 57-company W1 INCLUDE cohort can serve as the same-snapshot cross-sectional benchmark under the existing contract.

Required:
- denominator starts from exact 57, not current universe and not 46-company SEMI universe
- no EXCLUDE_PROVEN or EXCLUDE_UNRESOLVED rows silently added
- missing/suspended/CA-review companies remain explicit
- report denominator impact under the recovered existing rule only
- if no existing denominator-missingness rule is found, return DECISION_REQUIRED rather than inventing one

### CHECK F — PIT / OUTCOME LEAKAGE FIREWALL

For all F05 readiness evidence and any candidate upstream formula reconstruction:
- last market observation date <= 2024-08-09
- no 2024-08-12 entry price used in F05 inputs
- no W1 outcome/evaluation price used
- no future return/high/close/rank/winner labels
- post-cutoff artifacts may be read only if strictly necessary to establish historical code/document provenance, never to supply a pre-cutoff economic value or CA fact

Return an explicit leakage audit table.

## 6. RUNTIME ADAPTER READINESS OBSERVATION

Existing `DuckDBParquetPriceProvider` at the reviewed model revision reads Date/Code/OHLC for parquet and does not currently expose Volume/Amount/Stocks in returned PriceRow objects.

PMO must classify this only as:
- `RUNTIME_ADAPTER_GAP_CONFIRMED` if exact readback agrees, or
- `NOT_CONFIRMED` if current reviewed code differs.

No code correction is authorized in F05-R0.
If raw parquet contains the needed columns but runtime adapter does not expose them, report a bounded semantic-neutral engineering candidate for later authorization.

## 7. REQUIRED OUTPUTS

Create a fresh F05-R0 task branch for report persistence only. Suggested branch:
`task/aaa/m3top3-f05-r0-readiness-20260905`

No source/model code mutation in this task.

Minimum artifacts:
1. `F05_R0_READINESS_REPORT.md`
2. `W1_57_COHORT_BINDING.json`
3. `W1_57_MARKET_DATA_COVERAGE.csv` or deterministic JSONL equivalent
4. `W1_57_CA_DISCONTINUITY_READINESS.csv` or deterministic JSONL equivalent
5. `F05_UPSTREAM_DEFINITION_RECOVERY.md`
6. `W1_BENCHMARK_FEASIBILITY.md`
7. `F05_PIT_LEAKAGE_AUDIT.md`
8. `F05_R0_EXECUTION_LEDGER.jsonl`
9. PMO persona journal/checkpoint with exact refs

Do not persist copied binary market data to Git unless already governed and explicitly allowed. Persist digests, counts, deterministic summaries, and refs instead.

## 8. REQUIRED TERMINAL CLASSIFICATION

Exactly one primary terminal state:

`READY_FOR_F05_R1`
Only if:
- exact W1 cohort is bound,
- price/volume readiness is sufficient under recovered semantics,
- CA/discontinuity disposition is sufficient,
- D1-D6 exact required definitions are recovered,
- denominator handling is governed,
- leakage audit passes.

`PARTIAL_DECISION_REQUIRED`
If data are broadly usable but one or more semantic/upstream-definition or bounded CA/denominator rules are not governed and require a narrow Owner/model decision.

`HOLD_DATA_NOT_READY`
If the exact population/market inputs cannot be read/verified or market data are materially insufficient even before semantic choices.

No `PASS` token by itself.
No Engineering PASS, semantic PASS, paired validation, independent validation, model-performance PASS, or official Top3 claim is authorized by this readiness task.

## 9. PROGRESS / TIME / COMPUTE

PLANNED_WALL_TIME = P50 35 minutes / P90 90 minutes
CONFIDENCE = LOW_MEDIUM
PLANNED_EWU = 100

EWU allocation:
- exact population + market input identity / raw coverage = 25
- CA / discontinuity readiness = 25
- W1 benchmark feasibility = 15
- upstream definition recovery D1-D6 = 25
- PIT leakage audit + terminal synthesis = 10

Progress reporting:
- checkpoint at approximately EWU 25 / 50 / 75 if the runtime supports observable progress
- terminal report at EWU 100 or earlier hard terminal
- do not fabricate active time, wait time, token, network attempt, or CRU telemetry; mark NOT_INSTRUMENTED where unavailable
- no repeated Owner approval request inside this exact bounded scope

## 10. STOP / OWNER ACTION BOUNDARIES

Continue automatically within this exact task for read-only inspection and report persistence.

STOP and return a narrow decision item if any of the following would be necessary:
- define or change the mathematical meaning of 20d/60d total return
- define or change equal-weight benchmark semantics
- define turnover/volume acceleration formula
- decide new dividend/CA adjustment semantics
- change missing-company denominator handling
- change feature weights, F05 scorer transform, saturation penalty, PIT or eligibility semantics
- add provider, credential, paid source, budget, custody scope
- broaden beyond W1 / necessary pre-cutoff lookback
- mutate main, merge, release or production

## 11. STAGE 2 LOCK

Even if terminal state is `READY_FOR_F05_R1`, DO NOT automatically materialize or score F05 in this task.

Return the readiness report to ASA.
ASA will explain to Owner in plain language:
- how many of the 57 are actually calculable,
- what data issues remain,
- what exact formulas were recovered,
- whether a narrow semantic decision is needed,
- what F05-R1 would do and would not do.

Stage 2 requires a separate Owner-facing authorization.

## 12. DISPATCH DISPOSITION

CURRENT_STATE = OWNER_AUTHORIZED_FOR_F05_R0_READINESS
REPEAT_OWNER_APPROVAL_REQUIRED = FALSE_WITHIN_THIS_EXACT_SCOPE
F02_R1_REMOTE_PRESERVATION = OPEN_NON_BLOCKING / NO_RERUN
F05_R0 = AUTHORIZED
F05_R1 = NOT_AUTHORIZED
OFFICIAL_TOP3 = NOT_AVAILABLE / NOT_CLAIMED
NEXT_RETURN = ONE_TERMINAL_PMO_F05_R0_READINESS_REPORT_TO_ASA
