# KRX governed-calendar source-custody receipt

ARTIFACT_ID = `AAA-M3TOP3-FC1-G3C-KRX-CALENDAR-SOURCE-CUSTODY-20260826-0232`

PARENT_WBS_ID = `FC1-G3 / G3-C`

EXECUTION_ROLE = `NON_VALIDATOR_BOUNDED_SOURCE_CUSTODY`

RESULT = `PARTIAL_AUTHORITY_SOURCE_CUSTODY`

GOVERNED_CALENDAR_RELEASE = `NOT_CREATED`

VALIDATION_ACTS = `0`

## 1. Result boundary

One bounded acquisition pass obtained exact live official KRX **closure-date**
responses for 2024, 2025, and 2026. The three responses are byte-preserved,
hashed, and row-counted below.

They are not an exact official open-session calendar. The response rows identify
holidays/closures only; they do not enumerate open regular sessions, identify a
market per row, or carry session-open/session-hours/half-day fields. Therefore
these bytes cannot by themselves prove the complete `market_id + trade_date`
regular-session universe required by the frozen G3-C protocol.

No observed marcap price date was promoted. No secondary calendar was used. No
calendar release, gate PASS, validator act, global validation, or retry loop was
created.

## 2. Official source and exact request profile

Official KRX UI locator:

`https://open.krx.co.kr/contents/MKD/01/0110/01100305/MKD01100305.jsp`

The live KRX page is titled `휴장일` and exposes a year selector plus an exchange
selector with `한국거래소`, `CME`, and `EUREX`. This acquisition selected only the
KRX option.

OTP request:

`GET https://open.krx.co.kr/contents/COM/GenerateOTP.jspx`

| Parameter | Exact value |
|---|---|
| `bld` | `MKD/01/0110/01100305/mkd01100305_01` |
| `name` | `form` |
| `Referer` | official UI locator above |

Data request:

`POST https://open.krx.co.kr/contents/OPN/99/OPN99000001.jspx`

| Parameter | Exact value |
|---|---|
| `search_bas_yy` | `2024`, `2025`, or `2026` |
| `gridTp` | `KRX` |
| `pagePath` | `/contents/MKD/01/0110/01100305/MKD01100305.jsp` |
| `code` | one-time KRX OTP; not retained in the governed source package |
| `pageFirstCall` | `Y` |

One fresh official-page session and one OTP/data request were used for each
year. There was no failed acquisition and no retry.

## 3. Exact byte receipts

| Year | Acquired KST | HTTP | Bytes | Rows | Response date range | SHA-256 |
|---:|---|---:|---:|---:|---|---|
| 2024 | `2026-08-26T02:30:21+09:00` | 200 | 2,143 | 18 | `2024-01-01`–`2024-12-31` | `d5961ae5998036cc1710fe28e22d324db0233b570dd5c417b088fba1408f857f` |
| 2025 | `2026-08-26T02:30:45+09:00` | 200 | 2,270 | 19 | `2025-01-01`–`2025-12-31` | `c90dcd0f9fd59498f239bbed32f63a300d64f25f9e03020f26a15c40cf017fa8` |
| 2026 | `2026-08-26T02:30:49+09:00` | 200 | 2,049 | 17 | `2026-01-01`–`2026-12-31` | `89ccce131de8d0c4baa6a30d62b7d2e8e3bdc872c71a21d7d81d4b667330d384` |

Total official closure rows = `54`.

Exact response schema observed in all three files:

`block1[].{calnd_dd,dy_tp_cd,calnd_dd_dy,kr_dy_tp,holdy_nm}`

The KRX responses are JSON bytes served with
`content-type: text/html;charset=UTF-8`; no normalization or reserialization was
performed before hashing.

## 4. Scope findings

| Required G3-C dimension | Exact finding |
|---|---|
| Date span | Official closure responses cover full calendar years 2024–2026, therefore include the required outer span through `2026-08-14` |
| Authority host | Official KRX `open.krx.co.kr` |
| Exchange selector | `gridTp=KRX`; CME/EUREX not selected |
| Closure rows | Exact and byte-bound: 18 + 19 + 17 = 54 |
| Open-session rows | `ABSENT` |
| Per-row market identity | `ABSENT` |
| Per-row regular-session-open flag | `ABSENT` |
| Session hours / delayed opening / half-day marker | `ABSENT` |
| Explicit proof that all represented equity markets share one calendar | `NOT_PROVEN_BY_THESE_BYTES` |
| Exact regular-session calendar bytes | `NOT_OBTAINED` |

## 5. Honest authority disposition

The obtained bytes are admissible as exact official KRX closure-source custody.
They are not sufficient, without an already-governed KRX rule/authority binding,
to transform every non-weekend, non-listed-closure date into an official open
regular session or to prove a common calendar across every represented equity
market.

Accordingly:

```text
AUTHORITY_RECEIPT_CANDIDATE = PARTIAL_AUTHORITY_SOURCE_CUSTODY
EXACT_OFFICIAL_KRX_CLOSURE_BYTES = OBTAINED_3_OF_3
EXACT_OFFICIAL_KRX_OPEN_SESSION_BYTES = NOT_OBTAINED
MARKET_COMMON_CALENDAR = NOT_PROVEN
G3_C_EWU = 0_OF_4_UNCHANGED
G3_C_STATE = SOURCE_BLOCKED
```

Precise remaining trigger:

1. exact official KRX open-session bytes with market/session identity, or
2. an explicitly governed authority-equivalent binding that combines these
   exact closure bytes with official KRX rules proving the complete open-date
   construction and common equity-market scope.

Until one trigger is met, do not build or promote `TRADING_CALENDAR_RELEASE`.

## 6. Compute and stop record

- Acquisition attempts: `3` planned annual requests, `3` successful, `0` retry.
- Validator/reviewer count: `0`.
- Global/full validation: `FALSE`.
- Primary acquisition window: `2026-08-26T02:30:21+09:00` through
  `2026-08-26T02:30:49+09:00` (`28 s` between first and last material byte).
- Token/CRU: `NOT_INSTRUMENTED`.
- Stop reason: exact official closure bytes recovered, but complete regular-
  session open-date authority is not exposed by the acquired source. The
  bounded pass stops without secondary-source inference.

