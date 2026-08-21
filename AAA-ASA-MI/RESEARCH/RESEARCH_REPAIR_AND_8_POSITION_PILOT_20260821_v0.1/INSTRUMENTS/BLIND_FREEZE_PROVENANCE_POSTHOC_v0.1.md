# Blind Freeze Provenance Post-Hoc Diagnostic v0.1

STATE = `POSTHOC_DIAGNOSTIC / NOT_VISIBLE_TO_PEV1_OR_PEV2 / DOES_NOT_UPGRADE_G5`

Filesystem times are source claims from one execution environment, not signed or Git-backed prospective provenance. They are recorded to explain the G5 failure and design the next run.

| Original position | Filesystem materialization time KST | Original SHA-256 |
|---|---|---|
| A1 | `2026-08-21 14:30:12.329418213 +0900` | `52baca209f9259b2c78b8d31e4d949a71461c20b278255df569c41237ae32ddd` |
| A2 | `2026-08-21 14:30:12.401418216 +0900` | `18afa0c3926cd734569397f732e0a2b73a8522af2ced19ee8d64e3f315bd0b68` |
| A3 | `2026-08-21 14:35:01.257426737 +0900` | `63a2e01022335ee1966a151204df49b4c05bf9e73bbb23b93170005b9667b4ec` |
| A4 | `2026-08-21 14:36:43.469429753 +0900` | `f997f3a69219f7c3e673ccb51794e4b99fad2bd097a5968f286c18d1180db14a` |
| B1 | `2026-08-21 14:40:31.193436471 +0900` | `b01789ff065aaa6f76ec7a800a87961ee83778debd026dd4617afffd8bdbd096` |
| B2 | `2026-08-21 14:40:31.257436472 +0900` | `013561e89d9e1d9ef9d94723d9a3e20b1b2b40fd85883f9c9e89c808786d1f5c` |
| B3 | `2026-08-21 14:36:22.685429139 +0900` | `90723ecd1aebbe7692e41a2272901071bc084ffed6a9e7fe9a5ed93aaed0a79c` |
| B4 | `2026-08-21 14:36:22.749429141 +0900` | `be0693df4942d33b84d829dd70d4d584bae82dc1931fc225c40bad2e7d1673f6` |

Final held-out v0.2 filesystem time was `2026-08-21 14:42:24.121439802 +0900`; SHA-256 `288bc9b98914279851561873ea10b6b4c95e66d419af5fbd1a23d4433a87b6c9`.

Blind copies were mechanically produced later, around `14:43:07–14:43:24 +0900`. Their hashes are in `RECEIPTS/PILOT_ALIAS_KEY_v0.1.md`. The transformation removed explicit names/metadata and post-reveal text, then replaced model acronyms. It did not have a prospectively signed transform manifest.

Static QA found two transformation defects:

- R19 retained “prevailing research basis,” “ASA-MI,” and “current research,” creating an exposure cue.
- acronym replacement produced malformed labels `R17-R17` and `R14-R14`.

Because PEV-1/PEV-2 did not receive this diagnostic and exact anonymous provenance was absent from their boundary, their G5 `PARTIAL` judgments remain authoritative for the pilot. Next-cycle blind packets must include a pre-evaluation anonymous manifest with exact original/alias hashes, signed or Git-backed time/order, transform recipe, author-visible test boundary, evaluator identity/budget, and modification log.

