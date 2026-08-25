# FC1-G2 B/C/D Source-Provenance Blocker Decision

```text
PROJECT = AAA / ASSET AGENT ASA
LANE = FC1-G2
MODE = NON_VALIDATOR / BOUNDED SOURCE RECOVERY
VALIDATOR_OR_REVIEWER = NONE
GLOBAL_OR_FULL_SUITE_VALIDATION = NONE
REGRESSION_OR_VALIDATION_LOOP = NONE
GIT_OR_ISSUE_MUTATION = NONE
EXTERNAL_SEARCH_OR_RETRIEVAL = NONE
OBSERVED_AT_KST = 2026-08-26T01:26:29+09:00
```

## 1. Decision

`NO NEW ADMISSIBLE HISTORICAL BP / LISTED-AT-ENTRY / W1-W8 AUTHORITY EVIDENCE FOUND`

The assigned source bytes contain useful **current structural seeds**, exact route
locators, PIT rules and exact price bytes. They do not contain the historical
authority needed to close G2:

- no cutoff-safe business-priority validity intervals for the 514 open combined
  cells;
- no authoritative listing date or listing/relisting history (`상장일 =
  NOT_FOUND` for 46/46 Company Master rows);
- no tuple-level upstream authority binding for the eight W1-W8 date rows.

Therefore:

```text
G2-B = BLOCKED / 514 OPEN
G2-C = BLOCKED / 8 AUTHORITY ROWS OPEN
G2-D = EXACT BLOCKER ENVELOPE COMPLETE / RELEASE CANDIDATE NOT BUILDABLE
G2 GATE EFFECT = NONE
NEW ELIGIBILITY / LISTING / WINDOW DECISIONS = 0 / 0 / 0
```

This is a source/input blocker, not a validation blocker.

## 2. Exact source audit

| Source | SHA-256 | Mechanically recoverable | Why it does not close G2 |
|---|---|---|---|
| TOP38 Scorecard v2.2 | `e41b02dcb642f72b447c6c468c6d590e19aff468e6bc99413b7da5ef0cde6300` | 38 current listed semiconductor-company characterizations at 2026-08-14 | current-state investment scorecard; no W1-W8 cutoff-safe validity intervals or listing history |
| `Semi_Data_Route v1.1` | `508f98e88c150ceb751db2227727db529eb04da467c53a6eed5278ca5e17aa02` | source tiers, cutoff discipline, Entry/Exit and missingness rules | rule only; no company-window evidence rows |
| `Semi_Universe v1.0` | `eef313bc71bd0a5cb019f92e43e1bf38c2a63633bb847320d1cb4c8fe4ea9023` | 46 current ACTIVE companies; historical eligibility rule | no historical membership genealogy or company-window facts |
| `SEMI-PIT-LEDGER v1.0` | `acde50e7090382e95cc585227c4dd52df6b3f342258b6debfa0aabb7db94006a` | contract requiring listing + actual Entry-day tradability | schema/contract only; no populated rows |
| Price import manifest | `ca8f117a83cd3da800a2a2b5e0ebdca3c89ff658ff3fd21b5083e4aae9ab98ce` | declared range, provider and Entry rule | 763-byte legacy configuration; no exact component hashes/release identity |
| `SEMI-SOURCE-INDEX v1.0` | `2131ebe6724a8c2d235e7e6f06d4fdde2819ab460bd5c907e2f7ca32e02dac46` | 46 DART/KIND route locators; 9 official URLs; 37 `NOT_VERIFIED` official URLs | route seeds are not historical facts or publication/access evidence |
| `SEMI-COMPANY-MASTER v0.1` | `03842717f3bb6815610541496b1f5dadfd44a0e277dc9364c5632cbfb5520cd6` | 46 KRX identities and business structural seeds | all FACT rows are `last_verified=2026-08-14`; listing dates and DART corp IDs are `NOT_FOUND` 46/46 |
| Price schema | `67c8633579c3b624ffa2254bdf4173f205b1617b64ed960b9b1e200bc1e01c25` | 20-column intended schema | headers only |
| Prior ingest audit | `6e8d0eabbd4cafaf8f3073528a3d75c7ec15713a4efa27ba5308a176776e0728` | 46 blocked historical audit rows | every ledger row is explicitly `NOT_CREATED` in that prior state |
| `marcap-2025.parquet` | `2bfd93c217eb74263bc5020b23fa6debb6b02531c11eaccc2826639bc191559e` | exact pinned 2025 bytes, 25,153,419 bytes | price-side input; positive Open does not independently prove listing authority |

The current Company Master source audit is exact:

- company sections / Business Type rows / FACT rows: `46 / 46 / 46`;
- FACT confidence: `6 High + 40 Medium`;
- FACT `last_verified=2026-08-14`: `46/46`;
- explicit historical `publication_at/effective_from/effective_to` intervals:
  `0/46`;
- DART corp ID `NOT_FOUND`: `46/46`;
- listing date `NOT_FOUND`: `46/46`.

Every W1-W8 Entry precedes 2026-08-14. A current 2026-08-14 structural seed
cannot be backfilled into a historical cutoff without a supported validity
interval. `NOT_FOUND` also cannot become a negative business or listing fact.

## 3. Business-priority closure consequence

The existing exact denominator queue remains:

| Axis/state | Open count |
|---|---:|
| Historical business priority | 551 |
| Listing/tradability | 469 |
| Combined historical eligibility | 514 |
| Combined component state `UNRESOLVED/UNRESOLVED` | 469 |
| Combined component state `UNRESOLVED/TRUE` | 45 |
| BP `NEEDS_RESEARCH` inside combined-open | 500 |
| BP `PARTIAL` inside combined-open | 14 |

All 514 combined-open cells still have unresolved BP. The current attached
masters cover 46 current companies while the combined queue spans 67 unique
companies, and the exact row-to-master overlap is not contained in the supplied
bytes. No overlap is invented here.

Fastest safe worker route after a source sidecar exists:

1. Resolve the 14 `PARTIAL` BP rows first.
2. Express historical business facts as reusable company validity intervals,
   then expand them deterministically to the applicable windows.
3. If BP is `FALSE`, close the combined cell without further positive listing
   work.
4. If BP is `TRUE`, join only the necessary authoritative listing/Entry state.
5. Preserve source bytes/hash, publication time, effective interval, locator,
   decision authority and cutoff comparison for every admitted interval.

## 4. Listed-at-entry consequence

The reusable non-validator Entry-Open artifact remains exactly:

- `1,016` price-side company-window rows;
- `979 TRUE + 37 FALSE`;
- workbook comparison mismatches: `0`;
- listing-combined state: `510 TRUE + 37 FALSE + 469 UNRESOLVED`.

Its SHA-256 is
`14906157e5071aec2d2e333ffd1f6a31d5c90092f4577494e90f7fc780dce289`.
It must not be rerun merely for this lane.

The 37 price-side false rows remain explicit mechanical observations. Positive
Entry Open is useful tradability evidence after G3 CA/calendar/release admission,
but it does not establish authoritative `listed_at_entry`, listing/relisting
history, or the absence of an unmodeled corporate action. The 469 listing rows
therefore stay open until G2 supplies authoritative listing history; no current
website locator substitutes for it.

## 5. W1-W8 authority consequence

The candidate registry is still byte-bound at
`96d63cc98a01b6332cf9486440e7f3fdaa0ec5a2d605f21bc14a4025b46e69fe`
and locally concordant `8/8`:

| W | Snapshot cutoff | Entry | Last trading day |
|---|---|---|---|
| W1 | 2024-08-09 | 2024-08-12 | 2024-11-08 |
| W2 | 2024-11-08 | 2024-11-11 | 2025-02-10 |
| W3 | 2025-02-10 | 2025-02-11 | 2025-05-09 |
| W4 | 2025-05-09 | 2025-05-12 | 2025-08-08 |
| W5 | 2025-08-08 | 2025-08-11 | 2025-11-10 |
| W6 | 2025-11-10 | 2025-11-11 | 2026-02-10 |
| W7 | 2026-02-10 | 2026-02-11 | 2026-05-08 |
| W8 | 2026-05-08 | 2026-05-11 | 2026-08-10 |

None of the assigned project-source documents enumerates these eight tuples as
an authority record. The only `2026-08-10` strings found in the relevant
converted sources are the publication date of a technology-map document, not a
W8 last-trading-day binding.

G2-C therefore needs one outcome-free `W1_W8_DATE_PROVENANCE_BINDING` with:

- upstream authority and exact artifact/document ID;
- byte hash and row/cell locator for each tuple;
- effective version;
- authorized custodian attestation.

Observed price dates may test consistency later; they cannot self-authorize the
window definitions.

## 6. Minimum resume packet

No Owner policy decision is required merely to record the present blocker. The
worker resumes when any exact missing input becomes available:

1. cutoff-safe historical BP fact/decision validity intervals for the 514
   combined-open cells (preferably batched by 67 company histories);
2. authoritative listing/relisting/delisting dates for the BP-TRUE subset of the
   469 listing-open rows;
3. an authoritative eight-row W1-W8 date provenance binding.

Do not repeat:

- the current source-document search;
- exact 2025 hashing;
- the 1,016-row Entry-Open projection;
- sealed v0.2 documentary validation;
- any global/full-suite/regression/validation loop.

## 7. EWU and worker-only time

```text
CURRENT_G2_EWU = 7 / 25
NEW_EWU_RECOMMENDED = 0
RECOMMENDED_G2_EWU_AFTER_PACKET = 7 / 25
```

The packet closes a false route and records an exact blocker, but closes no
G2-B eligibility cell, no G2-C authority row, and no releasable G2-D artifact.
Progress should not be inflated for blocker restatement.

Current true G2 gate-closure ETA is `NOT MEASURABLE`; source/custodian wait is
external and unbounded. After all three missing inputs are admitted, the
remaining worker-only interval expansion, conditional listing join, 514-cell
recompute, eight-row bind, exact candidate assembly and local mechanical QC are:

```text
P50 = 1.5-2.5 h
P90 = 4.0-5.0 h
TIMING_CONFIDENCE = LOW
```

## 8. Claim ceiling

`NO_NEW_DOCUMENTARY_PROOF / NO_HISTORICAL_BUSINESS_PRIORITY_DECISION /
NO_LISTED_AT_ENTRY_DECISION / NO_W1_W8_AUTHORITY_RELEASE /
NO_DENOMINATOR_RELEASE / NO_G2_PASS / NO_INTEGRATED_PASS / NO_EOPT_G0_PASS`
