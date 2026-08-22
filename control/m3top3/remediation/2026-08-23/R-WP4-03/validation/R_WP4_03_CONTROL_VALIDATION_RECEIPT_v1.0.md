# M3TOP3 R-WP4-03 Control Validation Receipt v1.0

## Verdict

`PASS`

`AAA-CONTROL-VALIDATOR` independently accepts the exact R-WP4-03 implementation commit `ea52bde2ed65c46f3e797f640b60dd9741aa8fe1` / tree `d068aa65b8c3bdacd062529ff9d35108812683d9` for the bounded canonical-lineage and full-eligible-universe **control mechanism only**.

IVA execution participation is `NONE`.

## Exact target and independent checks

- Branch: `aaa-m3top3-p0-canonical-lineage-full-universe-20260823`
- Parent: `495c070be37f978c8be536c0b469d2d07cf0c071`
- Remote delta: `23 paths = 17 modified + 6 added + 0 deleted`; unexpected paths `0`
- Branch at validation close: exact implementation commit, `ahead 1 / behind 0`
- Remote changed blobs: `23/23` exact; local candidate Git-blob mismatches `0`
- Frozen source: `30/30` files exact; source-tree SHA-256 `1d7b256e961b6f04ad038738fd727a41b98b18db1786a4d21cdd13f78c80d3da`
- Freeze manifest SHA-256: `0cc363f0c9eb65338747d9d8a47b35046ace881dec0bbf7db50d24ea4e004e17`
- Candidate permissions: files `0444`, directories `0555`; symlink/cache/bytecode `0`
- ENGV receipt SHA-256: `5c450df3c7f47f0184bda89562828894f9c6ffedf6266f6210d85c4de83596e3`

## Control acceptance

| Gate | Result | Control conclusion |
|---|---|---|
| A1 Scope / semantic preservation | PASS | Allowlisted delta only; model interface, outcome formula, and PIT guard accepted hashes preserved |
| A2 Independent exact-byte admission | PASS | Eight release domains, independent U/D expectations, live rehash, portable digests, scorer identity, elevated-state denial |
| A3 U/E/I partition | PASS | Exact U=E∪I set/count/digest/date/revision contract; unresolved eligibility blocks |
| A4 Row lineage / snapshot completeness | PASS | PIT/model/retrieval equal U; one-to-one refs; drift/missing/extra/duplicate rejected before scorer/publication |
| A5 Diagnostic scorer identity | PASS | Exact scorer/config/model/schema/feature identity bound into run identity |
| A6 Full preservation | PASS | Scorer outputs equal U; ranking/ledger/outcomes equal E; Top3/Top10 are projections; metric denominator reconciles |
| A7 Immutability / concurrency / accounting | PASS | Create-only, manifest-last, locked full-E ledger, deterministic collision, zero-work exit 2 |

All `14` immediate stop rules were reviewed; breaches `0`.

The in-memory exception is confined to the exact `SYNTHETIC_IN_MEMORY_DIAGNOSTIC` tag, exact fixture provider classes, `DIAGNOSTIC` authority, `RAW_IMMUTABLE`, `release_eligible=false`, and no CLI path. It does not permit live Universe/denominator self-certification.

## Independent execution and sealed evidence

- Compile: `27/27`
- Full discovery: `252/252 PASS`
- Control-focused modules: `131/131 PASS`
- Production negative matrix: `75/75 PASS`; raw exceptions/code/exit/scorer/write mismatches `0`
- Mutation: preserved `33` + new `17` = `50/50 KILLED_RED`; survivors/harness errors `0`; transcript streams independently rehashed `200/200`
- Concurrency: snapshot/full-identical/full-conflicting/ledger = `4 × 100 PASS`; raw exceptions `0`; manifest artifacts rehashed `13/13`
- Semantic revalidation: `22/22 PASS`
- Sealed evidence: `527` files, all read-only; directories read-only; symlinks `0`

## Truth limits remain blocked

- U127 outcome-blind provenance: `0/127` proven. It remains a working winner-enriched challenge Universe and cannot be called outcome-blind or population-complete.
- W1–W8 are all exposed and remain development/descriptive only.
- Historical eligibility unresolved: `514/1,016`.
- Exact named 2024/2026 price bytes and standalone interface manifest remain absent.
- CA completeness axes B/C remain open.
- Thin PIT: `0/1,016 COMPLETE`; publication timestamp null `1,016/1,016`; annotation/access sidecar absent.
- Exact executable pre-outcome v1 identity remains unrecovered.

## Authority ceiling and next route

Model state remains `S0_PRE_OUTCOME_BASELINE_CANDIDATE`. Official execution, `PRICE_CANONICAL`, Official Golden, Full Replay, Freeze, Promotion, Release, Production, and merge remain blocked.

This CTLV PASS opens only the active Core B `AAA-MODEL-VALIDATOR`. It does not open PMOV before Core B PASS and does not close R-WP4-03 by itself.
