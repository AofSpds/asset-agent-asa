# First Scorecard Input-Custody Attestation

- PMO run: `AAA-M3TOP3-FIRST-SCORECARD-20260905-093656-CODEX-01`
- custody inspection: `2026-09-05T09:45:24.5646533+09:00` to `2026-09-05T10:07:36.7283351+09:00`
- role: PMO-delegated read-only input custodian; no file, Git, network, provider or credential mutation
- scope: exact files and Git objects needed by this approved first replay only

## Exact local price components

| Year | Absolute locator | Bytes | SHA-256 | Rows / dates / bounds |
|---|---|---:|---|---|
| 2024 | `C:\Users\ms1pk\Downloads\marcap-2024.parquet` | 24,572,111 | `b0c38943e67637d5faf88429880092cf0f46a394be39860dd3bcd0b04231bccb` | 687,708 / 244 / 2024-01-02..2024-12-30 |
| 2025 | `C:\Users\ms1pk\Downloads\marcap-2025.parquet` | 25,153,419 | `2bfd93c217eb74263bc5020b23fa6debb6b02531c11eaccc2826639bc191559e` | 696,524 / 242 / 2025-01-02..2025-12-30 |
| 2026 | `C:\Users\ms1pk\Downloads\marcap-2026.parquet` | 16,198,533 | `5da710a2fc56f8fe9b1f5126295cc30c3b15c0ee35d28ba808a505ec4a2243c1` | 434,915 / 151 / 2026-01-02..2026-08-13 |

The three-component dataset identity is
`419893f0dc8c08019a746182135630cc5f94d6e7ebc2874d5bd23cb54c0a72f7`. Across 1,819,147 rows,
the common 18-column schema was observed with zero null Date/Code values, zero malformed code values and zero
duplicate `(Date, Code)` keys. These are raw immutable replay inputs, not a price-canonical release.

## Replay calendar and W1–W8

The 637 exact observed price dates reconcile with weekdays minus the bound official KRX closures over each
observed range: `244/244`, `242/242`, `151/151`, with zero missing or unexpected dates and zero closure/date
overlap. Closure bindings are:

- 2024: Git blob `98c93ecb5dafe38723ee06fb07cbd80c7c8a2a4d`, SHA-256 `d5961ae5998036cc1710fe28e22d324db0233b570dd5c417b088fba1408f857f`
- 2025: Git blob `583c4c6dc374408bca2c8a8eadbd9ee168468210`, SHA-256 `c90dcd0f9fd59498f239bbed32f63a300d64f25f9e03020f26a15c40cf017fa8`
- 2026: Git blob `92c3815e6b8b5383620ec916716e777b51fdd142`, SHA-256 `89ccce131de8d0c4baa6a30d62b7d2e8e3bdc872c71a21d7d81d4b667330d384`

The W1–W8 registry is commit `e59ed048d6da76edcad82c9a58b0d083c6452471`, binding blob
`033817e6335865e411d2bb4b5837434167091458`, embedded CSV SHA-256
`96d63cc98a01b6332cf9486440e7f3fdaa0ec5a2d605f21bc14a4025b46e69fe`. All eight declared entries are the
first replay date after snapshot; all eight ends and derived exits exist globally. This supports the approved
replay-only calendar, not a production calendar or outcome-free window authority claim.

## Population, annotation and CA limits

The G3-E source queue is commit `69a1e7b`, Git blob
`4b3cfbfa9969abe2bd6dff5fdbfeb2db9d31cdae`, compressed SHA-256
`8b3671d662457aef8c1a5595b33a85a27e08aaee56238e7218f1df0b4df78353`, 1,016 unique
company-window rows. Its exact outer partition is 465 eligible, 37 proven ineligible by tradability and 514
unresolved. It remains `QUEUE_ONLY_NOT_ADMITTED`; feature annotation sidecars are absent.

The bounded working CA record contains two source-verified events. `KRX:033170` is unresolved in all eight
windows and is outside the 465 included rows. `KRX:183300/W8` intersects an included row, but the July split
and suspension leave no observable Aug-11 exit in the bound Aug-13 price file; if it is ever model-selected,
the outcome must be excluded as unresolved material CA. No adjustment factor is inferred. Because this run
produces zero scored selections, no future price value or outcome calculation is consumed.

## Golden package custody

The request attachment is 71,412 bytes, SHA-256
`9a93ca585282809a751f7ad5f29d68c86040bc73ee20ee1cb8a2349072787b36`. The recovered ZIP is 40,210 bytes,
SHA-256 `5bbe75a4c9966abcb9f10d2f1e84df983977c1cf76d69e7bda6dfe4f24e60836`; all 10 unique entries decompress
and pass CRC, and all 9 internal component size/hash references match. This proves transport integrity only.
Independent arithmetic binds GF08/GF12/GF13/GF14. GF09 remains an explicit control-input gap because gate,
contract-form eligibility and fixture authorization are absent; it is not defaulted.
