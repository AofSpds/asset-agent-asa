# M3TOP3 R-WP2/3 Bounded Remediation Discovery

- Scope: `R-WP2-01 Universe & Exposure Closure` + `R-WP3-01 Data Admission Closure`
- Execution role: PMO-directed evidence discovery only
- IVA execution participation: `NONE`
- Mutation: source workbook and project sources were read-only; no source evidence was invented or backfilled
- Primary working artifact: `U127_Data_Expansion_Working_v0.8_2026-08-15.xlsx`
- Primary artifact SHA-256: `44501584c9dc6224637e9193219c1e8c87507af77dc15dc3944a3d04af524cda`
- Source self-classification: `PRE_RESEARCH_SNAPSHOT` / `HISTORICAL_STATUS_ONLY` / `DO_NOT_USE_AS_CURRENT_AUTHORITY=TRUE`

## 1. Closure verdict

| Gate | Verdict | What is closed now | What remains blocked |
|---|---|---|---|
| G2 — Universe & Exposure Closure | `BLOCKED_WITH_WORKING_SUBGATES_CLOSED` | U127 working membership 127/127; U46=46 + U81=81; exact duplicates=0; company_id binding 127/127; W1–W8 cutoff/entry/last-day registry; current artifact outcome-exposure classification | U127 is `FREEZE_CANDIDATE`; overall identity READY=0/127; row-level outcome-blind inclusion provenance absent; person/model outcome-access history absent; therefore sealed holdout and unbiased population claims prohibited |
| G3 — Data Admission Closure | `BLOCKED_WITH_NARROW_SUBGATES_CLOSED` | Thin PIT slot existence 1016/1016; 2025 named byte identity; CA stock-count signal adjudication 24/24; CA record/source-locator evidence; working 979-row price reconstruction preserved as preliminary | Historical denominator incomplete; 2024/2026 current named bytes absent; standalone current interface manifest absent; CA completeness axes B/C open; U81 F1 READY=0; Thin PIT evidence/content completion=0/1016 |

No Official Golden, Full Replay, official winner release, performance claim, or model state advancement is authorized by these results.

## 2. G2 exact findings

### 2.1 Working membership — closeable only as a working set

- Membership rows: `127/127 PASS`
- Composition: `U46=46`, `U81=81`
- Exact duplicate supplied names: `0`
- Exact duplicate KRX codes: `0`
- company_id binding: `127/127 READY`
- overall identity: `127/127 PARTIAL`, `0/127 READY`
- entity resolution: `5 READY`, `122 PARTIAL`
- exceptional identifiers requiring explicit handling: two historical alias annotations; one non-all-numeric KRX identifier, `세미티에스 0017J0`

This closes `WORKING_MEMBERSHIP_ENUMERATION`, not `OUTER_UNIVERSE_PROVENANCE` or `U127_FROZEN/CURRENT`.

### 2.2 Provenance boundary

`Semi_Universe_v1.0` establishes the prior U46 and the historical rule that a company must have been listed, tradable, and within semiconductor business scope at the relevant time. The v0.8 workbook adds the U81 working rows and seed axes. It does not carry a row-level genesis ledger proving:

- who selected every U81 member;
- the selection rule and candidate population at selection time;
- the selection timestamp;
- whether winner/outcome knowledge was concealed;
- rejected candidates under the same rule.

Therefore every row in `01_U127_WORKING_MEMBERSHIP_PROVENANCE_GAPS.csv` is marked `NOT_PROVEN_ROW_LEVEL_OUTCOME_BLIND`, while preserving its exact working membership and current completion statuses.

### 2.3 Window and exposure role

The eight window definitions are fully enumerable. However, the same workbook directly contains:

- `Baseline_Windows!F2:I9`: winner, winner MFE, Top10 cut, Top20 cut;
- `Price_Full_Rank_Reval!A2:Q980`: 979 outcome-ranked company-window rows;
- `Price_Reval_Summary!A2:I9`: outcome summaries;
- `Baseline_Registry!A2:D6`: preliminary historical baseline references.

Thus W1–W8 are outcome-exposed in the current artifact. No sheet or field records who or which model accessed which outcome, and when. Artifact exposure can be closed as `KNOWN_EXPOSED`; historical person/model exposure cannot be reconstructed from this artifact and remains `ACCESS_LEDGER_ABSENT`. Until independent evidence proves otherwise, all eight windows are `DEVELOPMENT_OR_DESCRIPTIVE_ONLY` and cannot be called sealed holdout.

## 3. G3 exact findings

### 3.1 Historical denominator

| Axis | Ready/deterministic | Partial/open | Exact scope |
|---|---:|---:|---:|
| Historical business priority | 465 protocol-certified | 16 PARTIAL + 535 NEEDS_RESEARCH | 1,016 company-window cells |
| Complete BP histories | 57 companies | 70 companies incomplete | 127 companies |
| Listing/tradability | 547 READY | 469 PARTIAL | 1,016 company-window cells |
| Combined historical eligibility | 502 deterministic = 465 ELIGIBLE + 37 INELIGIBLE | 514 UNRESOLVED | 1,016 company-window cells |

Combined historical-eligibility unresolved counts are exactly `W1=62`, `W2=63`, `W3=64`, `W4=66`, `W5=66`, `W6=65`, `W7=66`, `W8=62` (`514` total). The separate listing/tradability PARTIAL counts are `W1–W7=59` each and `W8=56` (`469` total); they must not be substituted for the combined denominator. The exact company, window, workbook row, and status-cell coordinate for every open BP/listing/combined decision is in `03_DENOMINATOR_CLOSURE_QUEUE.csv`.

The workbook's narrower `BP_RESIDUAL_RESEARCH_QUEUE_COUNT=3` refers only to the named residual track (`씨엠티엑스`, `삼양엔씨켐`, `엘케이켐`). It must not be misread as the total denominator gap; raw table status counts show 551 non-READY BP cells across 70 companies.

### 3.2 Price bytes and derived ranks

| Component | Workbook expected SHA-256 | Current named input | Decision |
|---|---|---|---|
| marcap-2024.parquet | `b0c38943e67637d5faf88429880092cf0f46a394be39860dd3bcd0b04231bccb` | absent | `BLOCKED` |
| marcap-2025.parquet | `2bfd93c217eb74263bc5020b23fa6debb6b02531c11eaccc2826639bc191559e` | present; 25,153,419 bytes; hash match | `PASS_CURRENT_BYTE_IDENTITY` |
| marcap-2026.parquet | `5da710a2fc56f8fe9b1f5126295cc30c3b15c0ee35d28ba808a505ec4a2243c1` | absent | `BLOCKED` |

The old `SEMI-PRICE-LEDGER_IMPORT-MANIFEST_v1.0.csv` is present, but it is not the exact standalone interface manifest whose expected hash is recorded by the v0.8 workbook. The workbook itself also contains a status conflict: `Integrity_Summary` says raw ledgers attached in that turn=`0/BLOCKER`, while `Price_Manifest` later claims all three component bytes attached and verified. Current execution-surface availability governs admission: only the named 2025 bytes can presently be rehashed.

`Price_Full_Rank_Reval` contains 979 rows matching the working eligible counts by window, but every row is labeled `PRELIMINARY_PRICE_REVALIDATION_CA_PROTOCOL_CORRECTED / NOT_OFFICIAL_ELIGIBILITY`. The immutable full-rank CSV payload is not located. This output is not admissible as official ground truth.

### 3.3 Corporate actions

- CA audit signals: `24/24 PASS`
- action records: `11`; all have passing evidence-audit status
- source-locator partials: `0`
- regression checks: `2/2 PASS`
- completeness axis A, stock-count discontinuity: `CLOSED`
- completeness axis B, exhaustive material OHLC discontinuity cross-check: `OPEN`
- completeness axis C, exhaustive known-KRX comparable-price/unit-change omission sweep: `OPEN`
- W6 and W8 Top10/Top20 differences under the corrected CA protocol are audit differences, not permission to tune toward the preliminary baseline.

CA record-level evidence can be accepted; `CA_COMPLETENESS_GATE` cannot.

### 3.4 Thin PIT and annotation admission

- Slots: `1016/1016 INITIALIZED`
- completion: `0 COMPLETE`, `1016 INCOMPLETE`
- evidence: `1016 NOT_RESEARCHED`
- publication_at: `1016 NULL`
- freshness: `1016 UNKNOWN`
- valuation, earnings, forward expectations, guidance, PO, backlog, qualification, repeat order, adoption, fab CAPEX, and material reference fields: `1016 NEEDS_RESEARCH` each
- F1 per company-window: `520 PARTIAL`, `496 NEEDS_RESEARCH`, `0 READY`
- U81 F1 company state: `0 READY`, `19 PARTIAL`, `62 NEEDS_RESEARCH`
- existing U46 source index: `37/46 Official fields NOT_VERIFIED`; company master preserves `46/46 VERIFIED structural seed / PARTIAL identity enrichment`, with DART corp id and listing date `NOT_FOUND` for all 46 in v0.1

The build manifest applies the registered source order and PIT rules without creating evidence. Interpretive fields require outcome-concealed source bundles, independent coding, preserved pre-adjudication outputs, and a sidecar lineage/access record. `NOT_FOUND`, `NOT_COLLECTED`, and `NOT_APPLICABLE` must remain distinct and must never be converted to zero or a negative business fact.

## 4. Immediate bounded queues

1. Supply and rehash exact named 2024 and 2026 price bytes plus the exact standalone interface manifest.
2. Close 551 BP, 469 listing/tradability, and 514 combined eligibility open cells using the exact queue; do not backfill across unsupported time windows.
3. Close CA completeness axes B and C against the frozen three-year byte set.
4. Complete U81 F1 and remaining identity evidence before Thin PIT feature collection.
5. Build outcome-concealed source bundles and annotation/access sidecars; then collect the 1,016 Thin PIT rows under fail-closed admission.

## 5. Evidence files produced

- `01_U127_WORKING_MEMBERSHIP_PROVENANCE_GAPS.csv` — 127 exact working members and row-level completion/provenance gaps
- `02_W1_W8_WINDOW_EXPOSURE_ROLE_MANIFEST.csv` — eight exact windows and allowed evidence role
- `03_DENOMINATOR_CLOSURE_QUEUE.csv` — 1,534 open decision records plus header: 551 BP, 469 listing, 514 combined eligibility
- `04_PRICE_CA_CURRENT_BYTE_ADMISSION_QUEUE.csv` — price-byte, interface, rank, and CA admission queue
- `05_THIN_PIT_SOURCE_ANNOTATION_BUILD_MANIFEST.csv` — field-level source, lineage, blinding, missingness, and release requirements

## 6. Source-rule anchors

- `Semi_Universe_v1.0`: historical eligibility requires listing, tradability, and semiconductor business scope at the relevant snapshot.
- `Semi_Data_Route_v1.1`: fixed source tiers; same-provider PIT consensus; provider mixing prohibited; NOT_FOUND is retrieval failure, not a negative fact.
- `SEMI-PIT-LEDGER_v1.0`: append-only logical key; evidence publication time and entry availability; raw event and model decision separated.
- `SEMI-PRICE-LEDGER_IMPORT-MANIFEST_v1.0.csv`: KRX-derived yearly parquet; evidence-backed adjustment factors only.
- `SEMI-PRICE-LEDGER_v1.0_SCHEMA.csv`: daily OHLC, stocks, trading status, CA flag/factor/type/source/confidence, and universe-eligibility interface fields.
