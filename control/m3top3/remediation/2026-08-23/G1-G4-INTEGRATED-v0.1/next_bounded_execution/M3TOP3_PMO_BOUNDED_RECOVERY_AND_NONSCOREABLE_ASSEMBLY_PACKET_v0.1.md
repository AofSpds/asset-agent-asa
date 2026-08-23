# M3Top3 PMO Bounded Recovery & Non-scoreable Assembly Packet v0.1

`PACKET_ID = M3TOP3-PMO-BOUNDED-RECOVERY-NONSCOREABLE-ASSEMBLY-20260823-01`

| Control | Value |
|---|---|
| Authority | `APPROVE_AND_CLOSE + PMO_DIRECT_DISPATCH=YES` |
| Execution Commander | `AAA-PMO-ORCHESTRATOR` |
| Owner action required now | `FALSE` |
| IVA execution participation | `NONE` |
| Model state | `S0_PRE_OUTCOME_BASELINE_CANDIDATE` |
| Allowed purpose | G1–G3 exact-byte recovery, denominator procedure validation, non-scoreable assembly controls |
| Prohibited outputs | scoring, ranking, Top-K, returns, outcome performance, Official Golden, Official Replay, Failure Atlas, Challenger evaluation |

## 1. Packet sequence

1. T0 — Freeze inputs and bind hashes.
2. BR-01 and PR-01 — Run exact baseline-package and price-component recovery in parallel.
3. EL-01 — Freeze the 514-cell queue, prioritize it mechanically, and issue a deterministic 32-cell procedure sample.
4. DA-01 — Assemble W4×3 fail-closed, non-scoreable pilot records.
5. T5 — PMO records only G1/G2/G3 evidence deltas. No Gate PASS or model-state transition is created.

## 2. T0 — Frozen inputs

| Input | SHA-256 |
|---|---|
| G1 baseline identity matrix | `528d0abd41991abbbe377508c6305f73368eb588193c90746ae3c029493709d0` |
| G2 universe/exposure matrix | `90104878d4bf6da92bc13f67180c3461c6fff71688f08b9c1b0b349238c1e51b` |
| G3 data/annotation matrix | `7ad599f41313c8148cf205b6b80d71885b33b69414fdb32bff10490ec32821dc` |
| U127 working membership gaps | `752138a1897cdacfcbb4762ac0caf5888007e49ac4605f88152576e544eeaa33` |
| Historical denominator queue | `02bde437c04b1cc3d314b30e9bdd41bdb9a9164d0d2df4468728bdab8089eb62` |
| Price/CA admission queue | `b7d07a1c3438c30bced3161ea5d287d53f34431c7ab3f5e040a761ea06548412` |
| Thin PIT build manifest | `5b78b6f0ea8cbdc2684e37724e3f0323ae8c50f1ae6dc1547e444d3e9c0eb7a1` |
| 2025 raw Parquet | `2bfd93c217eb74263bc5020b23fa6debb6b02531c11eaccc2826639bc191559e` |
| Price schema | `67c8633579c3b624ffa2254bdf4173f205b1617b64ed960b9b1e200bc1e01c25` |

Any mismatch stops the affected lane before processing.

## 3. BR-01 — Exact baseline research-package recovery

### Expected identities

| Artifact | Expected path | Bytes | SHA-256 |
|---|---|---:|---|
| v0.1 ZIP | `control/research/working-candidates/m3top3-gr-research-package/v0.1/AAA_M3TOP3_GR_RESEARCH_PACKAGE_v0.1_WORKING.zip` | 35,775 | `3aaee7c1de2bd6f97e5ffd808fba980bf73fea1b604fb3c3b79e2be005180002` |
| v0.2 ZIP | `control/research/working-candidates/m3top3-gr-research-package/v0.2/AAA_M3TOP3_GR_RESEARCH_PACKAGE_v0.2_WORKING.zip` | 40,210 | `5bbe75a4c9966abcb9f10d2f1e84df983977c1cf76d69e7bda6dfe4f24e60836` |

Registration authorization anchor: commit `0940227893c9439a2f196586067c5ec2e3f31959`.

### Actions

- Query only approved repository, recovery root, and known source-custodian locators.
- Preserve locator, actor, time, query and result in a custody ledger.
- Place any received byte stream in quarantine under its original name.
- Verify byte size and SHA-256 before reading ZIP contents.
- Only exact matches become `RECOVERED_EXACT_CANDIDATE`.
- After exact match, inventory the central directory and internal manifest read-only.

### Terminal states

Each ZIP must end as one of:

- `EXACT_MATCH_RECOVERED`
- `CUSTODIAN_ATTESTED_UNAVAILABLE`
- `MISMATCH_QUARANTINED`

Current state is `NOT_FOUND_ON_SEARCHED_SURFACES`; this is not yet custodian-attested unavailability.

### Stop rules

- Stop and quarantine on any path/name/size/hash/version mismatch.
- Never recreate, rezip, normalize or substitute semantic equivalents as original bytes.
- Never promote a working scorer/config to official v1.
- If a custodian attests unavailability, raise the reserved Owner choice; PMO does not choose archival S0 versus `v1r-semantic-reconstruction`.

## 4. PR-01 — 2024/2026 price bytes and standalone manifest recovery

| Artifact | Expected bytes | Expected SHA-256 |
|---|---:|---|
| `marcap-2024.parquet` | 24,572,111 | `b0c38943e67637d5faf88429880092cf0f46a394be39860dd3bcd0b04231bccb` |
| `marcap-2026.parquet` | 16,198,533 | `5da710a2fc56f8fe9b1f5126295cc30c3b15c0ee35d28ba808a505ec4a2243c1` |
| `SEMI-PRICE-MARCAP-KRX-2024-2026_v1.interface-manifest.json` | exact artifact required | `56d36d51e9f7b8870aa75cc41ee241603f6cf7446cb2386187c6ebcbb88b73c4` |

### Actions

- Recover only from authorized custody/storage locators and record provenance for every transfer.
- Quarantine first; verify name, bytes and hash before metadata inspection.
- Exact matches may enter an immutable component-candidate register.
- Only after all three artifacts match may PMO issue `PRICE_COMPONENT_BYTES_RECOVERED`.
- Read-only metadata/schema/calendar coverage may follow; canonical transformation, CA adjustment and return calculation remain prohibited.

### Claim ceiling

Even exact recovery does not create `PRICE_CANONICAL`. CA completeness B/C, the canonical 20-column row, Trading Status, provider and eligibility fields must still close.

### Owner trigger

New cost, account, contract, credential, provider or source-definition authority is required. Until then, PMO continues bounded recovery without Owner action.

## 5. EL-01 — 514-cell eligibility priority and procedure sample

### Frozen population

- Combined unresolved cells: 514 across 67 companies.
- Window counts: W1 62, W2 63, W3 64, W4 66, W5 66, W6 65, W7 66, W8 62.
- Open decision records: 1,534 = business-priority 551 + listing/tradability 469 + combined eligibility 514.

### Priority order

1. **Mechanical short-circuit** — resolve listing/tradability first for `UNRESOLVED/UNRESOLVED` cells using cutoff-safe KRX/KIND or admitted daily-ledger evidence. Deterministic FALSE closes the combined cell as ineligible without unnecessary business-scope research.
2. **Business-scope closure** — research the existing tradability-TRUE cells and any newly TRUE cells with cutoff-safe primary-business evidence.
3. **Ambiguity lane** — aliases, mergers, splits, listing boundaries and missing evidence require explicit adjudication. `UNRECOVERABLE` and `UNRESOLVED` remain valid outcomes.
4. **Reuse control** — company evidence may span multiple windows only when validity dates and absence of intervening change are proven.

### 32-cell process-validation sample

- S1: eight `business-scope unresolved / tradability TRUE` cells, one per window where available.
- S2: eight `unresolved / unresolved` cells, one per window.
- S3: eight listing-boundary cases, one per window where the actual queue supports the stratum.
- S4: one company's W1–W8 longitudinal set.
- Deterministic order: ascending `SHA256("M3TOP3-ELIGIBILITY-PILOT-v0.1|window|KRX_code|stratum")`.
- Winner, rank, return and later-success fields are excluded from the sampling frame.
- W4×삼양엔씨켐 is a fixed negative control outside the statistical sample if not naturally selected.

The sample validates the procedure; it must never be extrapolated as a 514-cell completion estimate.

### Stop rules

- No outcome-aware human/LLM eligibility coding.
- No post-cutoff evidence or present-day business backfill.
- No silent deletion or forced inclusion of unresolved cells.
- Any required eligibility-semantic change is an Owner trigger.

## 6. DA-01 — W4×3 non-scoreable assembly pilot

### Fixed scope

| Company | Code | Control case | Current eligibility |
|---|---|---|---|
| 케이씨텍 | `281820` | normal eligible price path | `ELIGIBLE` |
| 미래산업 | `025560` | CA + zero-OHL stress path | `ELIGIBLE` |
| 삼양엔씨켐 | `482630` | unresolved-denominator negative control | `UNRESOLVED` |

W4 cutoff=`2025-05-09`, entry=`2025-05-12`, last trading day=`2025-08-08`.

### Mandatory record fields

- `bundle_id = W4|company_id|revision`
- raw source locator and byte hash
- retrieval timestamp and actor
- timezone-aware publication time and cutoff comparison
- identity binding and eligibility state
- price-component hash and boundary-date coverage
- zero-OHL and CA-signal state
- retrieval/access sidecar and concealment receipt
- `SCORE_ADMISSION=false`
- `RANK_ADMISSION=false`
- `OUTCOME_ADMISSION=false`

No outcome role or return calculation is assigned. Source bundles must exclude future prices, winners, ranks, returns and current-success state. Because exact F01–F09 identity is absent, the pilot records only neutral facts/evidence and lineage; it creates no official feature label.

### Terminal states

Each company ends as `ASSEMBLED_CANDIDATE` or reasoned `FAIL_CLOSED`. Missing source hash, publication time, identity or concealment evidence must fail closed. 삼양엔씨켐 remains full-row preserved and unscored while eligibility is unresolved.

## 7. Packet exit and Owner triggers

### Exit

- BR-01 and PR-01 expected artifacts each have an evidence-backed terminal state.
- EL-01 sample and full-queue priority plan are frozen; no outcome data entered selection.
- DA-01 has 3/3 terminal receipts and zero prohibited outputs.
- PMO issues a G1/G2/G3 delta checkpoint only. No gate or model promotion is implied.

### Reserved Owner triggers

1. Exact baseline custodian attests unavailability or recovered bytes mismatch.
2. Price recovery requires a new paid provider, contract, account, credential or source definition.
3. Universe or eligibility semantics must change.
4. Historical consensus access or blinded annotation at scale requires resources/budget.
5. Scoring, Golden, Replay, S0 transition, Freeze, Promotion, Release, Merge or Production is proposed.

`DEFAULT_IF_NO_OWNER_ACTION = CONTINUE_WITHIN_APPROVED_BOUNDED_SCOPE`
