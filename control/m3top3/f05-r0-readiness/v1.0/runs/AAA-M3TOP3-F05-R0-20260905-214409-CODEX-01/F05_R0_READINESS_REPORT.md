# F05-R0 readiness report

`TERMINAL = PARTIAL_DECISION_REQUIRED`

- Project / product: AAA / ASSET AGENT ASA
- Persona: `AAA-PMO-ORCHESTRATOR (PMO)`
- Run ID: `AAA-M3TOP3-F05-R0-20260905-214409-CODEX-01`
- Snapshot cutoff: `2024-08-09T23:59:59+09:00`
- Scope: bounded read-only readiness inspection and report persistence
- F05-R1: not authorized and not executed

## Owner-facing result

The exact 57-company W1 cohort and all bound market-data bytes are readable. Every member has 151 pre-cutoff market rows and complete common 21/61-date price, Volume, Amount, and Stocks availability, so the raw data are broadly usable.

F05 still cannot be calculated safely. All six required upstream definitions are only partial: the exact 20d/60d total-return construction, equal-weight benchmark arithmetic, turnover acceleration formula, dividend/CA treatment, and missing/suspended denominator handling are not fully governed. In addition, GST and 엑시콘 have three raw price/share-count discontinuity boundaries without an admissible CA record or adjustment factor. The allowed terminal is therefore `PARTIAL_DECISION_REQUIRED`, not `READY_FOR_F05_R1` and not `HOLD_DATA_NOT_READY`.

## Readiness summary

| Check | Result | Evidence-backed conclusion |
|---|---|---|
| A — exact W1 cohort | CLOSED | Exact population object verified: 1,016 total rows; W1 127 = 57 INCLUDE / 8 EXCLUDE_PROVEN / 62 EXCLUDE_UNRESOLVED; 57 unique company IDs and KRX codes; no current-universe substitution. |
| B — pre-cutoff raw market coverage | CLOSED_FOR_AVAILABILITY_ONLY | 57/57 have 151 dates through cutoff, 21/61 diagnostics ready, Volume/Amount/Stocks ready, no duplicate keys, non-positive OHLC, missing common dates, or zero-volume rows. |
| C — CA/discontinuity readiness | NOT_CLOSED | 55/57 have no configured heuristic trigger but CA absence is not proven; GST and 엑시콘 have three heuristic-only unresolved boundaries; source-verified applicable CA events/factors = 0. |
| D — exact upstream definitions | PARTIAL | D1-D6 = 0 exact / 6 partial / 0 absent. No conventional formula was substituted. |
| E — W1 benchmark feasibility | DECISION_REQUIRED | Exact denominator starts at 57, but D3/D6 and two CA-review members prevent governed benchmark construction. No benchmark was computed. |
| F — PIT/outcome firewall | NO_PROHIBITED_ECONOMIC_VALUE_ADMITTED | All economic values end on/before cutoff; no entry/outcome price or future rank/winner label was admitted. Post-cutoff CA records were scope-only and were not used as pre-cutoff evidence or to relabel/adjust observations. |
| Runtime adapter | `RUNTIME_ADAPTER_GAP_CONFIRMED` | Raw Volume/Amount/Stocks exist, but the reviewed Parquet adapter does not expose all of them to F05. No code change was made. |

## Exact population and source binding

- Population revision: `69a1e7b7971d38bf23694ed63a914ff796386b78`
- Population path: `control/m3top3/recovery/2026-08-26/fast-close-worker-results/g3-annotation-candidate/G3_E_ANNOTATION_INGEST_QUEUE_v0.1.jsonl.gz`
- Population blob: `4b3cfbfa9969abe2bd6dff5fdbfeb2db9d31cdae`
- Population bytes / SHA256: `73,327` / `8b3671d662457aef8c1a5595b33a85a27e08aaee56238e7218f1df0b4df78353`
- Bound price dataset identity SHA256: `419893f0dc8c08019a746182135630cc5f94d6e7ebc2874d5bd23cb54c0a72f7`
- Source semantics: `RAW_IMMUTABLE_NOT_PRICE_CANONICAL`
- 2024 file: 24,572,111 bytes / `b0c38943e67637d5faf88429880092cf0f46a394be39860dd3bcd0b04231bccb`
- 2025 file: 25,153,419 bytes / `2bfd93c217eb74263bc5020b23fa6debb6b02531c11eaccc2826639bc191559e`
- 2026 file: 16,198,533 bytes / `5da710a2fc56f8fe9b1f5126295cc30c3b15c0ee35d28ba808a505ec4a2243c1`

Only 2024 pre-cutoff economic values were admitted. The 2025/2026 identities were verified by size and hash only.

## Exact raw coverage result

- Parquet 2024: 687,708 rows, 244 dates from 2024-01-02 through 2024-12-30, 18 columns.
- Predicate-filtered W1 slice: 8,607 rows = 57 companies × 151 market dates through 2024-08-09.
- Common final 21 dates: 2024-07-12 through 2024-08-09; 57/57 have 21/21 observations.
- Common final 61 dates: 2024-05-16 through 2024-08-09; 57/57 have 61/61 observations.
- Price-lookback diagnostic ready: 57/57 for both 21 and 61 observations.
- Volume, Amount, Stocks raw-value ready: 57/57 each.
- Duplicate Date+Code groups, missing common-market rows, null/non-positive OHLC rows, zero-volume rows: 0 each.
- Maximum calendar gap: 5 days, consistent with the observed market calendar; maximum missing-market-session and zero-volume run: 0.

These facts demonstrate raw availability only; they do not define total-return or turnover formulas.

## CA and discontinuity ceiling

- `SOURCE_VERIFIED_PRE_CUTOFF_CA_RECORD_RECOVERED = 0/57`
- `CA_OR_PRICE_DISCONTINUITY_REVIEW_REQUIRED_HEURISTIC_ONLY = 2/57` companies and 3 boundaries
- `NO_HEURISTIC_TRIGGER_IN_TESTED_WINDOW__CA_ABSENCE_NOT_PROVEN = 55/57`
- `W1_CA_READINESS = NOT_CLOSED`

The raw source has no `corporate_action_flag` or `adjustment_factor`. The governed CA final scan remains `WORKING_BLOCKED`, `ca_completeness_gate=BLOCKED`, and `price_D4_ready=false`; zero adjustment factors are admissible. No company is labeled `NO_CA`.

The deterministic heuristic window is 2024-05-16 through 2024-08-09. Review triggers are an absolute adjacent raw-Close change greater than 30%, an absolute adjacent Stocks change at least 5%, or at least five consecutive missing market dates or zero-volume dates. These thresholds are diagnostic, are not governed CA semantics, and do not turn a first-date zero-change sentinel into an event. The CSV's `heuristic_observation_evidence` field records raw diagnostic observations, never verified corporate-action events.

Governed CA-control readback:

- `control/schemas/v0.1/price.schema.yaml`, blob `9c29c00bf8fb1bf352bfa0144dc282e50ce96bd7`: raw price is not canonical; CA/factor fields require evidence; share discontinuity is an audit signal only.
- `control/data-plane/PRICE-CANONICAL-NORMALIZATION-AUDIT-PLAN_v0.1.yaml`, blob `5419037061b7855801bdabaed28b0d6903966c46`: forbids trading/CA/factor inference and leaves promotion unclosed.
- `control/data-plane/CA-EVENT-RECONCILIATION_v0.1.yaml`, commit `72114d829d3087dfe944671bac5665539c88b271`, blob `58b5693fe5ae3a63bdc63bccf5b495379136b497`: contains two 2026 events and zero events applicable to the W1 interval.
- `control/data-plane/CA-COMPLETENESS-FINAL-SCAN_v0.2.yaml`, commit `441cbc18a8d41b42af17865b9d4c63fc3baa8836`, blob `a6a9b9e4f431714b4ef017de8193fd5e532cadf7`: `ca_completeness_final_scan=NOT_CLOSED`, gate blocked, and `price_D4_ready=false`.

## Semantic and execution boundary

`RAW_INPUT_READY = 57/57`

`SAFE_F05_CALCULABLE_NOW = 0/57`

The second figure reflects a cohort-wide semantic gate: it does not mean 57 companies lack data. A narrow Owner/model decision is required for D1-D6, plus evidence-based CA adjudication for GST and 엑시콘. A later engineering authorization is also needed to expose the existing raw fields through the runtime adapter. F05 weights, transforms, scorer, saturation rules, eligibility, and PIT semantics remain unchanged.

No F05 inputs, score, rank, seal, validation verdict, or official Top3 output was produced. Stage 2 remains locked; F05-R1 requires a separate Owner-facing authorization.

## F02-R1 non-blocking preservation readback

The earlier F02-R1 preservation lane was not rerun. Its exact remote task branch had already been closed at commit `b0e4b60e6380ad12705ded8f05efce13843bbf3c`, tree `01e9ed6dddc6c23af44811fb5cd072c199f02dd6`; no F02 artifact was reconstructed or added to this F05 branch. It was not a scientific dependency of this result.

## Required narrow decisions

1. Define D1/D2 endpoints, inclusivity, price basis, total-return/dividend/CA treatment, and non-trading behavior.
2. Define D3/D6 equal-weight aggregation and denominator behavior for missing, suspended, and CA-review members.
3. Define D4 turnover/volume base metric, windows, transformation, and zero/gap treatment.
4. Resolve GST and 엑시콘 with admissible issuer/event/adjustment evidence, without post-cutoff rewriting.
5. Separately authorize the semantic-neutral adapter field exposure only after the meanings above are closed.

## Artifact index

- `W1_57_COHORT_BINDING.json` — exact 57 identities and population binding
- `W1_57_MARKET_DATA_COVERAGE.csv` — deterministic per-company availability diagnostics
- `W1_57_CA_DISCONTINUITY_READINESS.csv` — deterministic per-company CA/discontinuity diagnostics
- `F05_UPSTREAM_DEFINITION_RECOVERY.md` — D1-D6 evidence and classifications
- `W1_BENCHMARK_FEASIBILITY.md` — exact-denominator feasibility decision
- `F05_PIT_LEAKAGE_AUDIT.md` — cutoff and outcome firewall readback
- `F05_R0_EXECUTION_LEDGER.jsonl` — bounded action/provenance ledger
- `F05_R0_ARTIFACT_CONSISTENCY_CHECK.json` — deterministic non-verdict artifact check
- `PROGRESS_*` — frozen plan, earned progress, and forecast calibration
- PMO persona journal — authority, scope, terminal, and Git persistence checkpoint
