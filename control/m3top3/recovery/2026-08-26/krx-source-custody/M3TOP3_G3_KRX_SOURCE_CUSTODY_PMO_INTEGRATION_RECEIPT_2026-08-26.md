# M3Top3 G3 KRX source-custody PMO integration receipt

```text
PERSONA = AAA-PMO-ORCHESTRATOR (PMO)
ISSUED_AT = 2026-08-26 02:35 KST
EXECUTION_CLASS = TWO_NONVALIDATOR_BOUNDED_OFFICIAL_KRX_SOURCE_CUSTODY_PASSES
SOURCE_POLICY = OFFICIAL_KRX_PRIMARY_SOURCES_ONLY
ACTIVE_WORKERS = 0
ACTIVE_VALIDATORS = 0
VALIDATION_ACTS = 0
GLOBAL_VALIDATION = FALSE
FULL_REGRESSION = FALSE
VALIDATION_LOOP = FALSE
EWU_DELTA = 0
G3 = NOT_CLOSED
```

## Result

| Lane | Exact outcome | Gate effect |
|---|---|---|
| Axis C corporate-action universe | `SOURCE_BLOCKED_CREDENTIAL_AND_ADMIN_APPROVAL_REQUIRED` | none |
| Governed calendar source | `PARTIAL_AUTHORITY_SOURCE_CUSTODY` | none |

No unofficial provider, price-signal inference, observed-price-date promotion,
or secondary calendar was used.

## Axis C authoritative blocker

The official KRX Data Marketplace maps `기업 주요 변동사항` to menu
`MDC04020503` and locator:

`https://data.krx.co.kr/contents/MDC/HARD/hardController/MDCHARD048.cmd`

The exact final response was HTTP 200, 407 bytes, SHA-256
`72926595b930be2a12498c726a786c3e4459e512dd9ba99d582ddf0d8d53a809`,
and states `로그인 또는 회원가입이 필요합니다.`. The current official Open
API usage page requires membership/login, authentication-key application and
administrator approval, then per-service application and administrator
approval. Its captured 31-service catalog does not list a conforming
corporate-action event-universe service.

Therefore the required `KRX_CA_EVENT_UNIVERSE` bytes, rows, publication cutoff,
and authority receipt are `NOT_OBTAINED`. The next admissible trigger is an
authorized KRX export or a custodian-provided conforming universe covering
`2024-01-01..2026-08-14` and the pinned code union, with exact query metadata,
row count, fields, byte digest, publication cutoff, and receipt.

## Calendar partial authority custody

One bounded official `open.krx.co.kr` acquisition obtained exact annual KRX
closure-response bytes through the `휴장일` UI, one-time OTP, and
`OPN99000001.jspx`, selecting `gridTp=KRX`.

| Year | Bytes | Rows | SHA-256 |
|---:|---:|---:|---|
| 2024 | 2,143 | 18 | `d5961ae5998036cc1710fe28e22d324db0233b570dd5c417b088fba1408f857f` |
| 2025 | 2,270 | 19 | `c90dcd0f9fd59498f239bbed32f63a300d64f25f9e03020f26a15c40cf017fa8` |
| 2026 | 2,049 | 17 | `89ccce131de8d0c4baa6a30d62b7d2e8e3bdc872c71a21d7d81d4b667330d384` |

The 54 rows are exact official closure-source bytes. They do not enumerate
open regular sessions, identify a market per row, carry an open/session-hours/
half-day field, or prove that every represented equity market shares one
calendar. They therefore cannot create `TRADING_CALENDAR_RELEASE`.

The remaining trigger is exact official open-session bytes with market/session
identity, or an explicitly governed authority-equivalent binding these exact
closure bytes to official KRX rules that prove the complete open-date
construction and common equity-market scope.

## Telemetry and stop boundary

| Item | Observed |
|---|---:|
| Axis-C official capture span | 134.44 s |
| Axis-C direct KRX HTTP requests | 6 |
| Axis-C target-locator attempts | 2, one client-compatibility forward attempt and no loop |
| Calendar planned annual requests | 3 |
| Calendar successful annual requests | 3 |
| Calendar retries | 0 |
| Calendar first-to-last material byte span | 28 s |
| Active retrieval time | `NOT_INSTRUMENTED` |
| Queue/dependency wait | `NOT_INSTRUMENTED` |
| Token/CRU | `NOT_INSTRUMENTED` |

Both bounded passes stopped at their exact authority boundaries. No validator,
reviewer, global/full validation, or validation loop was used.

## Progress and claim ceiling

Axis-B remains complete signal-only with 2,406 signals pending Axis-C. The
frozen combined G3-B Axis-B/Axis-C unit remains `0/7 EWU`; G3 remains `4/25`;
overall Fast-Close remains `21/100`; validation closure remains `0%`.

This receipt creates no Axis-C completeness/exhaustion, corporate-action type
or factor, calendar release, clean holdout/OOS, G3/integrated PASS, EOPT-G0,
A/A, Golden, Replay, Freeze, Champion, Promotion, Release, or Production claim.
