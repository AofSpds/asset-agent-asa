# FC1-G2 Read-only Reconciliation

```text
PROJECT = AAA / ASSET AGENT ASA
PERSONA = AAA-PMO-ORCHESTRATOR delegated bounded worker
LANE = FC1-G2
MODE = READ_ONLY
GIT_OR_ISSUE_MUTATION = NONE
VALIDATOR_EXECUTION = NONE
SEALED_RECEIPT_RERUN = NONE
```

## 1. Result

`G2 = OPEN / PARTIAL / NO NEW ELIGIBILITY OR PROVENANCE CLOSURE`

The durable G2 counts reproduce exactly, but the exact documentary ledger has a
necessary three-number distinction:

- `34` = excluded unresolved documentary cells (`DRRV-F04` scope);
- `35` = those 34 plus the separate direct-subset technical row `PX-004-L`;
- `99` = all protocol rows, all still explicitly non-admitted to any eligibility
  or tradability decision; 64 are actor-attested route observations only.

No attached project-source byte changed relative to the recovered predecessor
workspace. Therefore the current attachments add no documentary, eligibility,
or W1-W8 provenance evidence.

## 2. Exact evidence surfaces

| Surface | Rows / role | SHA-256 |
|---|---:|---|
| `remediation/r_wp23_data_closure/01_U127_WORKING_MEMBERSHIP_PROVENANCE_GAPS.csv` | 127 membership rows | `752138a1897cdacfcbb4762ac0caf5888007e49ac4605f88152576e544eeaa33` |
| `remediation/r_wp23_data_closure/02_W1_W8_WINDOW_EXPOSURE_ROLE_MANIFEST.csv` | 8 outcome-bearing local-role rows | `f346e1227cf3828bde82117af951027e4387bb729f779e227ae6cb07f481bbd7` |
| `remediation/r_wp23_data_closure/03_DENOMINATOR_CLOSURE_QUEUE.csv` | 1,534 open axis records | `02bde437c04b1cc3d314b30e9bdd41bdb9a9164d0d2df4468728bdab8089eb62` |
| `g2_32p1.../inputs/ELIGIBILITY_PROCESS_VALIDATION_SAMPLE_MANIFEST_v0.1.csv` | frozen 32+1 sample | `bd1dcef5e446591b25ee902c46e010618a3aef30f9ca58865ab01daceb89715b` |
| `g2_32p1.../FROZEN_RETRIEVAL_PROTOCOL_v0.1.md` | documentary-only protocol | `c87c7d2d996621b9fdea07b03f48398b30a616800b86c8418bd51e068ed643b2` |
| `g2_32p1_direct_reretrieval_v02.../PROTOCOL_COMPLETENESS_REGISTER_v0.2.csv` | 99 protocol rows | `0f440224e7be2da3d881ad59a2a214ef7b294c0c829efa4aa20c4c8dab72816c` |
| `g2_release_candidate.../U127_WORKING_MEMBERSHIP_RELEASE_CANDIDATE_v0.1.csv` | 127 candidate members | `6a7c40b2a8bd52353a944f108dd556bf1dc05a520926aebb6d1bca4ae3b48f7c` |
| `g2_release_candidate.../W1_W8_WINDOW_REGISTRY_RELEASE_CANDIDATE_v0.1.csv` | 8 outcome-free tuples | `96d63cc98a01b6332cf9486440e7f3fdaa0ec5a2d605f21bc14a4025b46e69fe` |
| Owner v1.2 recommendation DOCX | policy authority; tuples not enumerated | `a7d87f07d5d442ac01b0fbaa9ebc2f5c6bbd52bf25d67b4ba319e66e86f9fdbc` |
| Owner v1.2 masterplan DOCX | execution authority; tuples not enumerated | `819e2c12bd149129e5054350c355b9132842d44841e09a1da2dbd1050888c7dd` |

Sealed manifests reused without revalidation:

- v0.2 candidate: `c0d3f66e8a19a3fde7749b8a637bdafc6375625c0beee3e38d2d0f69f248b872`;
- v0.2 independent validation: `7431c5669911e78b82eabe80d5460fc63f4a7c71cde3a2939eb361774a93b083`;
- G2 custody follow-up: `41939a69ab4b8e6b8664473d81095c186255dd2bfba4bbb626e6b48735a38d25`;
- v0.2 binding addendum: `a0bd6040acafc8a0e513821c381fe0ebbf2d7346955c7b22f75f70b35fffd312`;
- G1/G2 follow-up validation: `ca1ac0333fe9d8538ffc59132d07667c3464befa95e3ff2f75ceeb909390bbb0`.

Latest Issue #53 state is open; latest comment `5413047250` records successor
lease `PMO-SUCCESSOR-20260826-0034-KST`, `FC1-G2` queued, 34/514/date
provenance open, and no duplicate worker or validator.

## 3. Documentary cells

Exact 99-row partition:

| Partition | Count | Current meaning |
|---|---:|---|
| actor-attested `RECOVERED` direct rows | 64 | no raw bytes, header, content hash, or exact access clock; not independent documentary proof |
| direct technical unresolved | 1 | `PX-004-L`, `UNRECOVERABLE_TECHNICAL` |
| excluded `UNKNOWN` | 13 | 12 entry-tradability + 1 business-scope |
| excluded `UNRECOVERABLE` | 21 | 21 inherited fail-closed entry-tradability rows |

The advertised 34-cell lane is therefore exactly:

- 33 entry-tradability cells;
- 1 business-scope cell;
- 13 `UNKNOWN` + 21 `UNRECOVERABLE`;
- 21 inherited fail-closed;
- 33 unique company-window pairs across 20 companies.

All 34 map to the exact 514 combined queue, but to only 33 company-window
pairs because `PX-033-T` and `PX-033-B` share 삼양엔씨켐/W4. Of the 33 pairs:

- 24 are `UNRESOLVED/UNRESOLVED` and also occur in the listing/tradability queue;
- 9 are `UNRESOLVED/TRUE` in the denominator ledger;
- none may be subtracted from 514 merely because a documentary row is later
  captured; the sample protocol explicitly authorizes retrieval only and zero
  eligibility investigations/decisions.

## 4. Combined historical eligibility

The exact 1,534-row queue partitions into:

| Axis | Open rows |
|---|---:|
| Historical business priority | 551 |
| Listing / tradability | 469 |
| Combined historical eligibility | 514 |

Existing deterministic combined cells are preserved: `502 = 465 ELIGIBLE +
37 INELIGIBLE`. The remaining 514 are:

- by window: W1 `62`, W2 `63`, W3 `64`, W4 `66`, W5 `66`, W6 `65`,
  W7 `66`, W8 `62`;
- component state: `469 UNRESOLVED/UNRESOLVED + 45 UNRESOLVED/TRUE`;
- underlying BP: `500 NEEDS_RESEARCH + 14 PARTIAL`;
- BP evidence: `497 NOT_RESEARCHED + 3 SEARCHED_NO_CUTOFF_SAFE_EVIDENCE +
  13 PRIMARY_SOURCE + 1 OFFICIAL_FILING_EXISTENCE/SECONDARY_DETAIL`;
- scope: 67 companies, 513 U81 cells and one U46 cell (씨엠티엑스/W7);
- open-window distribution: 59 companies x 8, 4 x 7, 2 x 5, 1 x 3, 1 x 1.

No one of the 514 can be closed from arithmetic alone: business priority is
unresolved in all 514. Once a governed BP decision exists, combined-status
calculation is deterministic. The 45 `/TRUE` rows then close directly from BP;
the BP-true subset of the remaining 469 still requires admitted listing and
actual entry-day tradability evidence.

A parallel non-validator G3-D read-only projection materially narrows the latter
dependency without closing it. Artifact
`agent_g3_pit_annotation/G3_D_ENTRY_TRADABILITY_SUMMARY.json` (SHA-256
`14906157e5071aec2d2e333ffd1f6a31d5c90092f4577494e90f7fc780dce289`)
reproduces all `1,016/1,016` workbook Entry-Open/tradable flags from the exact
recovered 2024/2025/2026 bytes: `979 TRUE + 37 FALSE`, mismatches `0`; the old
and range-complete 2026 objects agree `254/254` for W7/W8 Entry Open. Thus the
469 `/UNRESOLVED` rows already have a mechanically positive Entry-Open fact.
Their remaining price-side closure still depends on G3 CA B/C, governed
calendar, and exact release admission/lineage, while G2 still needs independent
`listed_at_entry` provenance. This projection does not alter the frozen 32+1
no-price protocol and does not reduce 514.

The 14 `PARTIAL` BP rows are the lowest-effort semantic candidates, but they are
not mechanical passes: their own queue requirement is
`REVALIDATE_OR_COMPLETE_CUTOFF_SAFE_PRIMARY_BUSINESS_EVIDENCE`.

## 5. W1-W8 date provenance

Local candidate tuples are exactly:

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

They are locally concordant 8/8 with the predecessor role manifest. Neither
exact Owner v1.2 DOCX enumerates them, and the predecessor manifest is
outcome-bearing and lacks tuple-level upstream authority bindings. A raw-price
calendar consistency check can be mechanical, but cannot itself establish who
authorized these eight window definitions.

Required closure remains an outcome-free
`W1_W8_DATE_PROVENANCE_BINDING_v1.0` with one row/window and exact upstream
authority, artifact/document ID and hash, record/cell locator, effective
version, authorized custodian attestation, and targeted validation receipt.

## 6. Current project-source delta

All 16 current `project_sources` bytes are SHA-256-identical to the recovered
predecessor workspace. Relevant unchanged contracts are:

- `Semi_Universe_v1.0` (`eef313bc...`): historical inclusion requires listed,
  tradable, and in semiconductor business scope at the relevant time;
- `Semi_Data_Route_v1.1` (`508f98e8...`): cutoff/source-tier discipline and
  `NOT_FOUND` must not become a negative fact;
- `SEMI-PIT-LEDGER_v1.0` (`acde50e7...`): historical eligibility requires
  listing plus actual Entry-day tradability, with publication/availability
  lineage.

Therefore there is no newly attached source-based gate delta.

## 7. Fastest safe route

1. Mark G2-A reconciliation `DONE_WITH_SOURCE_CUSTODY_BLOCKER`; do not repeat
   the completed local/Git search or sealed v0.2 validation.
2. Preserve the operational queue as `34 excluded + PX-004-L technical`, not
   simply 34 total. Do not promote the 64 actor attestations.
3. Use an outcome-clean external custody sidecar for exact official URLs with
   opaque body/header capture, access clocks and hashes. The 34 excluded rows
   require a separately authorized exact-route manifest; `PX-004-L` gets at
   most the governed single exact-URL retry.
4. For the 514 denominator, adjudicate BP first. Start with the 14 partial rows,
   then batch by 67 company histories while recording explicit validity
   intervals. Never reuse a document across windows without a proven interval.
5. If BP is false, short-circuit tradability. If BP is true, resolve only the
   necessary listing cells. Reuse the exact 1,016-row Entry-Open projection only
   after G3 CA/calendar/release-lineage admission; do not repeat that mechanical
   scan. The frozen 32+1 documentary protocol itself forbids price/return
   evidence and cannot be repurposed.
6. Recompute combined status mechanically only after source/adjudication fields
   are complete, then create the eight-row date-provenance binding.
7. Produce one consolidated exact-hash G2 candidate and one targeted validator
   only after the current Owner validator hold is released.

## 8. EWU, ETA, and claim ceiling

Recommended earned-EWU ceiling now: `7 / 25` for FC1-G2, limited to the fully
reconciled G2-A subunit and its bounded blocker disposition. Award `0` to G2-B,
G2-C, G2-D and G2-V. This follows the same progress treatment as a completed
identity reconciliation that ends in a proved external-byte blocker.

The packet's G2 P50 `2.5h` / P90 `5h` can still describe reconciliation and
candidate mechanics only. It is not supportable as an actual G2 gate-closure
forecast while clean source custody, 514 BP decisions, conditional tradability
decisions, tuple authority and validator release are absent. External wait must
be reported separately; actual G2 closure ETA is currently unmeasurable.

Gate effect: `NO G2 GATE ADVANCE`; a bounded queue/blocker reconciliation only.

Claim ceiling:

`STATUS_ARITHMETIC_AND_LINEAGE_RECONCILIATION_ONLY / NO_NEW_DOCUMENTARY_PROOF /
NO_ELIGIBILITY_OR_TRADABILITY_DECISION / NO_DENOMINATOR_RELEASE /
NO_W1_W8_AUTHORITY_RELEASE / NO_G2_PASS / NO_INTEGRATED_PASS / NO_EOPT_G0_PASS`.
