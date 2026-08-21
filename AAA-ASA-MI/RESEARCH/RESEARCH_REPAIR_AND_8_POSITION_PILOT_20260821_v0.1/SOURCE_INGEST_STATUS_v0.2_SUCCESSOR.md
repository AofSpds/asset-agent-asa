# AAA-ASA-MI Source Ingest Status v0.2 Successor

STATE = `SOURCE_DERIVED / NON_DESTRUCTIVE_SUCCESSOR / MATERIAL_CONFLICTS_PRESENT`

This artifact succeeds—but does not overwrite—the earlier `SOURCE_INGEST_STATUS.md`. The earlier claim that every ARM retains a dedicated full archive is not true at exact repository HEAD `50c4a1d92e743e7e1862b61d848f12e046d49bdd`. Detailed evidence and the current-six audit are in `05_SOURCE_INTEGRITY_AND_CURRENT_SIX_AUDIT.md`.

| Unit | Source bundle | Current executable probe | Source-to-probe linkage | Status |
|---|---|---|---|---|
| ARM-A | Valid five-part archive; decoded 116,152 bytes, 887 lines, SHA-256 `e7507c0a364e9acb0ecfa2a375959c7099f428123ab1f74cd322cdb6ec423c94` | Runs and matches stored receipt | current bundle supports the replay; external original/fullness manifest absent | `PROVEN` bundle/replay; `PARTIAL` origin completeness |
| ARM-B | Stored three-part Base64 stream malformed (`30,647` non-whitespace chars; modulo four = 3); gzip CRC/length failure | Current script runs | current script hash conflicts with historical hash reported in the unique checksum-valid forensic recovery candidate | `CONFLICT/CORRUPT`; recovery only `PARTIAL`, never authoritative |
| ARM-C | No source archive; proposal/ledger/return packet absent | Eight toy probes run | no stored receipt, source packet, or hash binds the probe to downstream review claims | probe execution `PROVEN`; source completeness/linkage `NOT_PROVEN` |

## Exact current-six source-selection provenance

| Evaluator ID | Candidate | Evidence state |
|---|---|---|
| E1-C01 | ARM-A D4 LPCW | `PROVEN` in the valid generated ARM-A bundle |
| E1-C02 | ARM-A D1 AHCK | `PROVEN` in the valid generated ARM-A bundle |
| E1-C03 | ARM-B D2 TRCC | `PARTIAL` only through the non-authoritative recovery candidate; primary proposal/pressure source absent |
| E1-C04 | ARM-B D1 CCP | `PARTIAL` only through the non-authoritative recovery candidate; primary proposal/pressure source absent |
| E1-C05 | ARM-C D3 CCRA | source-selection provenance `NOT_PROVEN` |
| E1-C06 | ARM-C D1 WLRF | source-selection provenance `NOT_PROVEN` |

The pool ID/order and recorded pool hash exist, but the exact candidate body does not. E1–E3 output archives verify against their manifest; exact evaluator prompts/settings and E4–E6 raw packets do not. Exact evaluation replay is therefore `NOT_PROVEN`.

## Prohibited inference

- Do not insert the single character that repairs ARM-B into persistent history as though it were original evidence.
- Do not reconstruct ARM-B files 01/02/04 or ARM-C proposal/ledger/return files.
- Do not reconstruct the current-six pool body from its hash or downstream summaries.
- Do not treat current executable toy probes as proof of historical candidate bytes.
- Do not convert isolation declarations into independently verified isolation.

`SUCCESSOR_SOURCE_STATUS = MATERIAL_RESEARCH_BASIS_REPAIR_REQUIRED`.

