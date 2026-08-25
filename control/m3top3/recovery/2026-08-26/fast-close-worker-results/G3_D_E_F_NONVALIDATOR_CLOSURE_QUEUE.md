# M3Top3 G3-D/E/F Non-Validator Closure Queue

```text
OBSERVED_AT_KST = 2026-08-26T01:08:18+09:00
EXECUTION_ROLE = FC1-G3 NON-VALIDATOR WORKER
VALIDATOR_HOLD = TRUE
IVA_EXECUTION_PARTICIPATION = NONE
SOURCE_MUTATION = NONE
GIT_OR_ISSUE_MUTATION = NONE
GATE_EFFECT = NONE
```

## 1. Disposition

G3-D has a reproducible **price-side Entry Open projection** over all 1,016
company-window rows.  The forward range-complete 2024/2025/2026 source bytes
produce exactly the same `valid_entry_open` and `tradable_at_entry` states as
the historical workbook: `979 TRUE`, `37 FALSE`, `0 mismatch`.

This does not close historical eligibility.  The 514 unresolved combined rows
all have unresolved business priority.  Of them, 469 also have unresolved
listing provenance even though their price-side Entry Open is positive.  The
remaining 45 have price/listing-side `tradable_eligible=TRUE` but unresolved
business priority.  G3-D can therefore eliminate **no** G2 evidence row by
itself; it supplies a mechanical join input only after G3-B corporate-action,
G3-C governed-calendar, price-release, and exact-lineage admission.

G3-E is not a small annotation clean-up.  Thin PIT has `0/1,016 COMPLETE`,
`1,016/1,016 NOT_RESEARCHED`, `1,016/1,016 publication_at=NULL`, and no
annotation/access sidecar.  Seventeen content/reference columns are
`NEEDS_RESEARCH` for every row (`17,272` field-slots).  The current source
documents define routing and schema but are dated 2026-08-14 and cannot be
backfilled as historical W1-W8 evidence.

G3-F can assemble a fail-closed lineage **envelope** mechanically, but cannot
complete the eight-domain exact release binding because Universe, denominator,
feature/annotation, CA, calendar, window-provenance, and exact scorer-release
dependencies are not all closed.

## 2. Exact source bindings

| Artifact | Bytes | SHA-256 | Current role |
|---|---:|---|---|
| `U127_Data_Expansion_Working_v0.8_2026-08-15.xlsx` | 563,995 | `44501584c9dc6224637e9193219c1e8c87507af77dc15dc3944a3d04af524cda` | Historical/outcome-exposed working source; not current release authority |
| `03_DENOMINATOR_CLOSURE_QUEUE.csv` | 325,454 | `02bde437c04b1cc3d314b30e9bdd41bdb9a9164d0d2df4468728bdab8089eb62` | 1,534 open decision records |
| `05_THIN_PIT_SOURCE_ANNOTATION_BUILD_MANIFEST.csv` | 7,245 | `5b78b6f0ea8cbdc2684e37724e3f0323ae8c50f1ae6dc1547e444d3e9c0eb7a1` | Build requirements; not feature/annotation release |
| `U127_WORKING_MEMBERSHIP_RELEASE_CANDIDATE_v0.1.csv` | 14,667 | `6a7c40b2a8bd52353a944f108dd556bf1dc05a520926aebb6d1bca4ae3b48f7c` | 127-row candidate; sealed candidate receipt only |
| `W1_W8_WINDOW_REGISTRY_RELEASE_CANDIDATE_v0.1.csv` | 414 | `96d63cc98a01b6332cf9486440e7f3fdaa0ec5a2d605f21bc14a4025b46e69fe` | Eight exact candidate date tuples; upstream date provenance qualified |
| `SEMI-DATA-ROUTE v1.1` | 49,660 | `508f98e88c150ceb751db2227727db529eb04da467c53a6eed5278ca5e17aa02` | Source tiers, PIT routing, missingness rules |
| `Semi-Universe v1.0` | 42,132 | `eef313bc71bd0a5cb019f92e43e1bf38c2a63633bb847320d1cb4c8fe4ea9023` | Historical eligibility rule reference |
| `SEMI-PIT-LEDGER v1.0` | 38,985 | `acde50e7090382e95cc585227c4dd52df6b3f342258b6debfa0aabb7db94006a` | Append-only/PIT/tradability contract |
| `R_WP4_03_CANONICAL_LINEAGE_FULL_UNIVERSE_CONTRACT_v0.1.md` | 19,079 | `f6eab8c880c498c09c52aef1b1b30e37b94de7ada9e6fc00994b5b2e7df5b0b9` | Sealed G4-scope lineage contract; not rerun |

Selected current price components:

| Year | Bytes | SHA-256 | Notes |
|---|---:|---|---|
| 2024 | 24,572,111 | `b0c38943e67637d5faf88429880092cf0f46a394be39860dd3bcd0b04231bccb` | exact upstream range component |
| 2025 | 25,153,419 | `2bfd93c217eb74263bc5020b23fa6debb6b02531c11eaccc2826639bc191559e` | byte-identical to uploaded source |
| 2026 | 16,297,737 | `b6f3f8ea110326b21d23b5344e6abe159f8ea7f7a345262155b929c08886fc9d` | first observed upstream component through 2026-08-14 |

The older workbook-bound 2026 component is 16,198,533 bytes with SHA-256
`5da710a2fc56f8fe9b1f5126295cc30c3b15c0ee35d28ba808a505ec4a2243c1`
and ends on 2026-08-13.  Its W7/W8 Entry Open values are exact-equal to the
range-complete component for all `254/254` applicable rows.  That equivalence
does not substitute for a new release manifest or authorize predecessor
manifest impersonation.

## 3. G3-D — PIT eligibility and Entry tradability

### 3.1 Exact current counts

| Plane | Exact state |
|---|---|
| Thin PIT rows | 1,016 = 127 companies x 8 windows |
| Operational membership | INCLUDE 465; UNRESOLVED 551 |
| Price-side actual Entry Open/tradability | TRUE 979; FALSE 37; unresolved 0 |
| Listing-combined `tradable_eligible` | TRUE 510; FALSE 37; UNRESOLVED 469 |
| Combined historical eligibility | ELIGIBLE 465; INELIGIBLE_BY_TRADABILITY 37; UNRESOLVED 514 |
| Combined unresolved by window | W1 62; W2 63; W3 64; W4 66; W5 66; W6 65; W7 66; W8 62 |

Cross-tab of the full 1,016 rows:

| Operational membership | Tradable eligible | Historical state | Count |
|---|---|---|---:|
| INCLUDE | TRUE | ELIGIBLE | 465 |
| UNRESOLVED | FALSE | INELIGIBLE_BY_TRADABILITY | 37 |
| UNRESOLVED | TRUE | UNRESOLVED | 45 |
| UNRESOLVED | UNRESOLVED | UNRESOLVED | 469 |

Price-side Entry Open reproduction by window is exact:

| Window | TRUE | FALSE | Workbook mismatch |
|---|---:|---:|---:|
| W1 | 119 | 8 | 0 |
| W2 | 120 | 7 | 0 |
| W3 | 121 | 6 | 0 |
| W4 | 124 | 3 | 0 |
| W5 | 124 | 3 | 0 |
| W6 | 124 | 3 | 0 |
| W7 | 125 | 2 | 0 |
| W8 | 122 | 5 | 0 |

The 37 false rows comprise 34 absent Date+Code rows consistent with pre-listing
states and three W8 rows with observed `Open=0`.  Absence/zero is only a
mechanical price observation here; the workbook's listing decision is not
independently re-adjudicated.

### 3.2 Closure queue

1. Bind the eight Entry dates to the separately hashed governed calendar
   release (G3-C); do not infer the calendar from observed price dates alone.
2. Bind price-side rows to the forward current component manifest and exact
   2024/2025/2026 hashes; do not substitute the missing predecessor manifest.
3. Bind Trading_Status/CA treatment to the future G3-B release candidate.
4. Join the 469 listing-history decisions supplied by G2; positive Entry Open
   does not prove listing status.
5. Join the 551 business-priority decisions supplied by G2.  The 37 terminal
   price-side FALSE rows remain in the denominator as explicit ineligible rows.
6. Materialize per-window full `U/E/I/UNRESOLVED` row artifacts and digests;
   require `UNRESOLVED=0` for READY.
7. Publish the G3-D candidate only as authoring evidence while validator hold is
   active.

The frozen 32+1 documentary sample remains a separate no-price retrieval
protocol.  This projection neither modifies that sample nor subtracts its rows
from the 514 denominator queue.

## 4. G3-E — annotation dependency

### 4.1 Exact current gaps

| Item | Current state |
|---|---|
| Thin PIT slots | 1,016 INITIALIZED; 0 COMPLETE; 1,016 INCOMPLETE |
| Feature/reference columns marked NEEDS_RESEARCH | 17 columns x 1,016 = 17,272 field-slots |
| `evidence_status` | 1,016 NOT_RESEARCHED |
| `source_evidence_ref` | 1,016 NULL |
| `publication_at` | 1,016 NULL |
| `last_verified_observed_at` | 1,016 NULL |
| `freshness_staleness` | 1,016 UNKNOWN |
| Annotation/access sidecar | 0/1,016 present |
| F1 status | READY 0; PARTIAL 520; NEEDS_RESEARCH 496 |

### 4.2 Mandatory safe pipeline

1. Freeze an outcome-free source-bundle plan per company/window and hash its
   source tier, query, search depth, budget, and stopping rule before search.
2. Keep retrieval actor, annotator A, annotator B, and adjudicator roles
   separate; record exact access/concealment state.
3. Preserve exact source bytes or stable source object identity, `source_hash`,
   timezone-aware `publication_at`, observation period, and retrieval receipt.
4. Admit only evidence available by the frozen cutoff/entry rule.  Current
   facts or 2026 project documents must not backfill historical state.
5. Extract objective facts deterministically where possible.  For every
   interpretive/scoring-critical field, preserve two independent
   pre-adjudication outputs, disagreement, adjudication, and reliability.
6. Persist annotator/model ID, prompt/config/build/temperature/tool-result
   hashes, timestamps, source-bundle hash, and `outcome_access_flag`.
7. Preserve `NOT_FOUND`, `NOT_COLLECTED`, `NOT_APPLICABLE`, `UNKNOWN`,
   `UNRECOVERABLE`, `PIT_VINTAGE_UNVERIFIED`, `LATE`, and `CONFLICT` as distinct
   states.  Never convert them to zero or a negative business fact.
8. Apply exact-v1 `VALUE_ADMITTED / NA_ADMITTED / SNAPSHOT_BLOCKED` only after
   the exact v1 mandatory/optional input contract is recovered.  Until then,
   missing content is fail-closed, not silently renormalized by a newly invented
   rule.
9. Materialize immutable feature-source and annotation releases plus one-to-one
   retrieval receipts for full applicable U.

### 4.3 Mechanical versus non-mechanical boundary

Mechanically possible now:

- source/field queue generation;
- cutoff comparison once timezone-aware publication data exists;
- byte/hash/locator/retrieval-receipt verification;
- missingness-class validation;
- access/concealment schema and sidecar creation;
- fact extraction for explicitly objective values;
- consistency, uniqueness, and one-to-one coverage checks.

Not mechanically closeable from current artifacts:

- historical evidence retrieval itself;
- proof that a human/LLM annotator was outcome-blind;
- independent dual interpretation and adjudication;
- truth of qualification/design-win/repeat-order/fab-stage interpretations;
- exact-v1 optional-versus-mandatory admission, because G1 exact identity is
  unresolved.

## 5. G3-F — exact lineage binding

The sealed lineage contract requires these eight release domains exactly once:

| Required domain | Current candidate state | Blocking fact |
|---|---|---|
| UNIVERSE_RELEASE | 127-row exact candidate; candidate-level sealed receipts exist | final release/applicability authority and row-level genesis remain qualified |
| DENOMINATOR_ELIGIBILITY_RELEASE | absent as complete release | 514 unresolved; exact E/I partitions not materialized |
| FEATURE_SOURCE_RELEASE | absent | Thin PIT 0/1,016 complete; source bundles/receipts absent |
| PRICE_RELEASE | exact forward bytes recovered | predecessor standalone manifest absent; new forward release identity not yet bound |
| CORPORATE_ACTION_RELEASE | record-level subgates preserved | completeness B/C open |
| TRADING_CALENDAR_RELEASE | absent | observed price dates cannot self-authorize a calendar |
| WINDOW_REGISTRY_RELEASE | 8-row exact candidate, SHA-256 `96d63c...9fe` | upstream date provenance finding remains open |
| SCORER_RELEASE | absent as exact pre-outcome v1 | G1 exact ZIP/scorer/config identity unresolved |

Forward mechanical assembly must preserve:

- semantic identity = logical URI + byte hash, excluding absolute paths;
- separate live-byte identity with exact size/hash/readback;
- independently supplied Universe and denominator expectation manifests;
- no self-certification from the rows being admitted;
- exact U/E/I set and partition digests;
- one-to-one row `dataset_refs` for Universe, denominator, feature, price,
  calendar and outcome-side CA/window domains;
- timezone/date/revision/status coherence;
- an externally bound hash of the lineage bundle's own bytes;
- authoring/evidence/paired-validation/independent-validation/Owner states kept
  separate.

## 6. Time and CRU forecast without validators

These forecasts separate a **bounded pre-validation/blocker candidate** from a
true scoreable G3 release.

| Unit | P50 | P90 | CRU proxy | Deliverable under current hold |
|---|---:|---:|---:|---|
| G3-D package/readback after B/C/calendar inputs | 0.25-0.5 h | 0.75 h | 2-4 | exact mechanical Entry projection + dependency-bound candidate |
| G3-E dependency/sidecar/admission schema | 0.5-0.75 h | 1.0-1.5 h | 4-8 | fail-closed annotation queue, not completed evidence |
| G3-F blocked lineage-envelope assembly | 0.5-1.0 h | 1.5-2.0 h | 5-10 | exact blocked envelope and missing-domain matrix |
| Combined D/E/F bounded candidate | 1.25-2.25 h | 3.25-4.25 h | 11-22 | non-validator candidate only |

True G3-E completion has no credible 2.5-hour ETA on current evidence.  It
contains 1,016 company-window rows and 17,272 unresearched field-slots, requires
historical source retrieval plus independent dual coding for interpretations,
and is also blocked by exact-v1 input semantics.  A rough workload floor of
only 1 minute per company-window is already 16.9 active hours before dual
review, adjudication, source-byte custody, or rework.  Therefore:

```text
G3_D_E_F_PREVALIDATION_BLOCKER_CANDIDATE_P50 = 1.25-2.25 h
G3_D_E_F_PREVALIDATION_BLOCKER_CANDIDATE_P90 = 3.25-4.25 h
TRUE_SCOREABLE_G3_RELEASE_ETA = NOT_MEASURABLE_FROM_CURRENT_INPUTS
SEALED_G3_OR_EOPT_G0_ETA_WITH_VALIDATOR_HOLD = UNAVAILABLE
```

## 7. Claim ceiling

- No new PASS, validation receipt, G3 closure, or integrated checkpoint claim.
- No listing/business-scope truth is created by positive Entry Open.
- No price/CA/calendar canonical or predecessor-manifest substitution claim.
- No outcome-blind annotation claim; current workbook is outcome-exposed.
- No exact-v1 NA/renormalization rule is invented.
- No score, rank, Top-K, return, Golden, Replay, Freeze, Champion, promotion,
  release, production, predictive-power, or optimization-effectiveness claim.
- Existing sealed receipts remain valid only within their original exact scope
  and were not rerun.

