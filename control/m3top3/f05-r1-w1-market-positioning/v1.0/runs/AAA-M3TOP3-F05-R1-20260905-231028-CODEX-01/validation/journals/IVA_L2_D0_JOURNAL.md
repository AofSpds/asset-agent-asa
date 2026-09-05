# F05-R1 IVA L2 D0 independent validation journal

- Receipt: `AAA-M3TOP3-F05-R1-IVA-L2-D0-20260906-002527-01`
- Run: `AAA-M3TOP3-F05-R1-20260905-231028-CODEX-01`
- Validator: `root/f05_r1_iva_d0::IVA-L2-INDEPENDENT-20260906-002527`
- Author: `root/f05_r1_author`
- Frozen target: D0 commit `bc327dddfcc2d826a9ef7c4169b2e8c87f4957f8`, tree `ae502559ccb3dc3ad76c835f5049f993f6da2d01`
- Target bundle: `AAA-M3TOP3-F05-R1-D0-bc327dddfcc2d826a9ef7c4169b2e8c87f4957f8-ae502559ccb3dc3ad76c835f5049f993f6da2d01`
- Merged input hash: `78d540e5e0385104ba21a744e28897762f4d15af25f571de1cc57136882b2500`
- Issued: `2026-09-06T00:25:27+09:00`

## Independence boundary

I froze these findings without reading the CTLV, MODV, or ENGV journals or receipts. I did not import or call `tools.m3top3.f05_r1_market`, did not invoke the unchanged scoring engine, and did not invoke the production score-output CLI. I edited no target implementation, policy, source, input, or shared control artifact. This journal and its IVA receipt are the only files written by this validator.

The arithmetic was reconstructed in a standalone in-memory program using DuckDB against the exact bound Parquet and Python `Decimal`; the target JSONL was used only as the comparison target after the independent values and trace hashes were derived.

## Bound bytes

| Component | SHA-256 | Result |
|---|---|---|
| F05 input JSONL | `8e5c2991eb1c14bede88300a5fd1d648ce263d3e7a3d6a83b31af9b1e3d873f7` | PASS |
| persisted F02 input | `13667596d8e76f10d319f4129a7cba3b890d2575b3cebf33b78a143740bbbf9e` | PASS |
| unchanged config | `eecde22a7744cff505c624bb6f0bdb11714352a122632238ea68d9cd0fbacb98` | PASS |
| 2024 price Parquet | `b0c38943e67637d5faf88429880092cf0f46a394be39860dd3bcd0b04231bccb` | PASS |
| exact W1 cohort artifact | `8ac8ba439b3decb2690e04ec8fa7d40e40c37dd1ab0329bf3d24bf8253eba6a1` | PASS |
| CA manifest artifact | `3fa931f83edb8d5bf3baf493d770cedc1ffa2f4f56ce8aae7a1171ded45fa50b` | PASS |
| CA custody artifact | `84a53966ca5233b699a8b5448ccd13ceede683dc555304945df76c7ba62d7eb7` | PASS |
| policy binding | `54bb0bb7f57975f2911d1bdae503eabcd702e5c4e8eee37d28accea8b2368137` | PASS |
| source-field binding | `0e4a43687b8f37b65f21340a6defab1026d87053bbebede63d3337b088ffd2ef` | PASS |

The independently reconstructed, score-free F02+F05 merged input canonical hash is exactly `78d540e5e0385104ba21a744e28897762f4d15af25f571de1cc57136882b2500`.

## Independent reconstruction

The validator queried `C:\Users\ms1pk\Downloads\marcap-2024.parquet` directly with DuckDB 1.4.0. It derived all distinct source sessions at or before `2024-08-09`, selected the last 61 sessions (`2024-05-16` through `2024-08-09`), and obtained the no-terminal-newline grid SHA-256 `8667d8b63eeaa5332b0c1390dec179c43c692591a7c3db4c5b1a6cf31217a911`.

The exact cohort contained 57 unique members and independently reproduced cohort identity `c72593633c88cb6913c703da626b95d6111c7b0fa5783ccef6d373b2adf8c546`. The query returned exactly 3,477 rows (57 × 61), no duplicate code/date group, and an identical 61-session grid for every member.

Each source number was converted through its source text representation into `Decimal`. With precision 64 and `ROUND_HALF_EVEN`, the validator independently computed:

- 20-session return: product of `1 + ChangesRatio / 100` over the last 20 interval rows, minus one;
- 60-session return: the same operation over the last 60 interval rows;
- turnover acceleration: mean of the last 20 `Volume / Stocks` observations divided by the immediately prior 20-observation mean, minus one;
- benchmark: company-ID-ordered simple sum divided by exactly 57, separately for each return horizon.

All 57 values for each of the three company metrics matched the target decimal strings exactly. The independently recomputed benchmarks were:

- 20-session equal-weight return: `-0.2124153885346208337758748387981210510982875684105824670798651096`
- 60-session equal-weight return: `-0.2427557483310895727201166322683066906964043950156641786131060302`

Both benchmarks and their legacy aliases matched on every one of the 57 rows. All 171 per-company source-slice hashes (20-session return, 60-session return, and 40-session turnover) matched. Cutoff, endpoint, interval/observation count, field, scale, semantics, cohort, dataset, denominator, CA semantic hashes, no-dividend flag, no-factor flag, and lineage locators also matched for all rows. The JSONL was canonical UTF-8, company-ID ordered, ended with LF, and contained no score, rank, outcome, or future-result key.

## Corporate-action boundary readback

All 11 vendored official issuer/KRX response bodies matched their declared byte lengths and SHA-256 values. The canonical manifest semantic hash was `b947cce6c75a7a9fb1f09aab6cd2d7042ed4823098cd814f62d7adc5ce88318f`; the custody semantic hash was `e38dcedfabbe6743bda7358c0387fa6624bdedfc4da2ff6840d1bf2351cce1d5`.

Independent market-row checks passed:

- GST, `2024-06-26`: Close 21,600; Changes -100; ChangesRatio -0.46; `21,600 - 21,700 = -100` against the official KRX base price.
- GST, `2024-07-24`: Stocks changed from 9,317,745 on the prior session to 18,618,260, exactly +9,300,515 official new shares.
- Exicon, `2024-06-03`: Close 20,400; Changes +930; ChangesRatio +4.78; `20,400 - 19,470 = 930` against the official KRX base price.
- Exicon, `2024-07-31`: Stocks changed from 10,848,797 on the prior session to 13,050,797, exactly +2,202,000 official new shares; Volume was 814,284.

These checks support the bound KRX reference/base-price daily-change interpretation and reject a raw adjacent-close ratio across the corporate-action boundary. No adjustment factor or dividend return was introduced.

## F02 join and coverage, without scoring

The persisted F02 batch had the same exact 57 company identities. F02 was `AVAILABLE` for exactly `KRX:003160`, `KRX:005290`, `KRX:025560`, `KRX:031980`, and `KRX:036200`; its base F05 block was `NOT_FOUND` for all 57. A deep-copy, score-free replacement of those F05 blocks with the target F05 inputs reproduced the required merged input hash.

The unchanged config binds F02 weight 10 and F05 weight 20. Therefore the exact five have available feature weight 30 and coverage `0.30`; the remaining 52 have available feature weight 20 and coverage `0.20`. No score or rank was computed.

## Test result

The standalone run executed 27,566 assertions across target identity, byte bindings, JSONL canonicality, cohort, official CA evidence, calendar, raw source admissibility, grid completeness, every derived value, every governed trace field, every source-slice hash, lineage, PIT/score-free constraints, CA market rows, and the score-free F02 join. All assertions passed; findings are empty.

- Canonical validation stdout SHA-256: `ceac5ce39f62980dded33eb0f146c7ebe4b961d3a27116834f9877ce990d6150`
- IVA role verdict: `PASS`
- Pass transfer: forbidden; this verdict applies only to IVA L2 on the exact D0 target and bound input bytes.
