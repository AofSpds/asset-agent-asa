# G3 Axis C KRX source-custody blocker / authority-locator receipt candidate

## 1. Scope and disposition

```text
TASK_CLASS = NON_VALIDATOR / BOUNDED_SOURCE_CUSTODY
PARENT_WBS_ID = FC1-G3-AXIS-C
SOURCE_POLICY = OFFICIAL_KRX_PRIMARY_SOURCES_ONLY
ACQUISITION_PASS_COUNT = 1
RETRY_LOOP = FALSE
GLOBAL_VALIDATION = FALSE
REVIEWER_OR_VALIDATOR = NONE
GIT_OR_ISSUE_MUTATION = NONE
FINAL_DISPOSITION = SOURCE_BLOCKED_CREDENTIAL_AND_ADMIN_APPROVAL_REQUIRED
```

The requested independently frozen `KRX_CA_EVENT_UNIVERSE` was **not
obtained**.  The bounded pass stopped immediately after the authoritative KRX
route proved credential-gated.  No price signal, stock-count discontinuity,
workbook row, unofficial provider, or individual disclosure scrape was used as
a substitute.

## 2. Requested governed target

| Field | Required target | Result |
|---|---|---|
| Effective-date coverage | `2024-01-01` through `2026-08-14` | `NOT_OBTAINED` |
| Security scope | union of codes in the three pinned marcap components | `NOT_OBTAINED` |
| Event taxonomy | frozen Axis-C classes 1–9 | `NOT_OBTAINED` |
| Required event fields | event ID, issue identity, publication time, exact effective/basis date, event type, comparable-price impact, supported factor, correction lineage, evidence ref | `NOT_OBTAINED` |
| Exact bytes / SHA-256 | one independent frozen universe | `NOT_OBTAINED` |
| Row count / manifest reconciliation | exact | `NOT_OBTAINED` |
| Custodian or authority receipt | exact original scope | `NOT_OBTAINED` |

`UNKNOWN` and `NOT_OBTAINED` are deliberately not recorded as zero.

## 3. Exact authoritative locator and access result

The KRX Data Marketplace main page identifies **기업 주요 변동사항** at:

```text
MENU_ID = MDC04020503
LOCATOR = https://data.krx.co.kr/contents/MDC/HARD/hardController/MDCHARD048.cmd
HTTP_METHOD = GET
QUERY_PARAMETERS = NONE
CAPTURED_AT = 2026-08-26T02:27:53+09:00
HTTP_STATUS = 200
CONTENT_TYPE = text/html;charset=utf-8
RESPONSE_BYTES = 407
RESPONSE_SHA256 = 72926595b930be2a12498c726a786c3e4459e512dd9ba99d582ddf0d8d53a809
```

The exact KRX response is not event data.  Its executable page text says:
`로그인 또는 회원가입이 필요합니다.` and redirects to the official KRX
login route.  This is a credential/manual-owner boundary; attempting to bypass
it is not authorized.

The menu binding is independently visible in the captured official main-page
HTML as:

```text
gotoMenu('/contents/MDC/HARD/hardController/MDCHARD048.cmd','MDC04020503')
data-menu-name="기업 주요 변동사항"
```

## 4. Official Open API check

Official documentation:

- Service use: https://openapi.krx.co.kr/contents/OPP/INFO/OPPINFO003.jsp
- Current service catalog: https://openapi.krx.co.kr/contents/OPP/INFO/service/OPPINFO004.cmd

The official service-use page requires:

1. Data Marketplace membership and login;
2. API authentication-key application and administrator approval;
3. per-service API use application and administrator approval; and
4. service use only after approval.

The captured current catalog contains 31 listed API services.  They cover
index prices, equity/rights-security daily trading and basic issue data,
securities products, bonds, derivatives, commodities, and ESG.  It does not
list a corporate-action event-universe service.  Therefore the public catalog
does not supply a credential-free conforming fallback for this Axis-C target.

## 5. Preserved local evidence

| Local evidence file | Bytes | SHA-256 | Meaning |
|---|---:|---|---|
| `evidence/KRX_MDCHARD048_LOGIN_REQUIRED_2026-08-26.html` | 407 | `72926595b930be2a12498c726a786c3e4459e512dd9ba99d582ddf0d8d53a809` | exact KRX login-required response |
| `evidence/KRX_MDCHARD048_RESPONSE_HEADERS_2026-08-26.txt` | 341 | `6d9c6fc637c3c6e1931a013fb05317b11e486628be06cac02f7fd4714d591f50` | non-sensitive response headers, including acquisition date; cookies omitted |
| `evidence/KRX_DATA_MARKETPLACE_MAIN_2026-08-26.html` | 588,359 | `37536ca24fcd5dcb4d102ae2f0870b15b1be54fe32e0cedadcfb4c6283f2e2fe` | official menu-to-locator binding |
| `evidence/KRX_DATA_MARKETPLACE_MENU_2026-08-26.xls` | 78,848 | `de83c4b9e1aa7fb1bc03b5cc7668d5bd82e01d498fbbb8f2681f03c16a96b452` | official all-menu export; includes 기업 주요 변동사항 |
| `evidence/KRX_OPENAPI_USAGE_2026-08-26.html` | 18,972 | `83a5ef28fcdfc72075763980a6b292f4562c35d1d00c8baa43d14ec28e03a281` | official key/application/approval procedure |
| `evidence/KRX_OPENAPI_CATALOG_2026-08-26.html` | 28,569 | `d28db84d5fe9189868dbcca82018a93e35c1ccdf644d25efcc5e85a7b981626e` | current 31-service official catalog |

The 407-byte response is preserved as **blocker evidence only**.  It is not a
CA source artifact and cannot be promoted to a custodian receipt.

## 6. Bounded-pass telemetry

```text
FIRST_EXACT_RETRIEVAL_TIMESTAMP = 2026-08-26T02:27:53+09:00
CAPTURE_COMPLETION_TIMESTAMP = 2026-08-26T02:30:08+09:00
CAPTURE_SPAN_SECONDS = 134.44
DIRECT_KRX_HTTP_REQUEST_COUNT = 6
TARGET_LOCATOR_ATTEMPT_COUNT = 2
TARGET_LOCATOR_FIRST_ATTEMPT = HTTP_403_WITH_DEFAULT_CLIENT
TARGET_LOCATOR_FINAL_ATTEMPT = HTTP_200_LOGIN_REQUIRED_PAGE_WITH_BROWSER_USER_AGENT
ACTIVE_RETRIEVAL_TIME = NOT_INSTRUMENTED
QUEUE_WAIT_TIME = NOT_INSTRUMENTED
DEPENDENCY_WAIT_TIME = NOT_INSTRUMENTED
RETRY_BACKOFF_TIME = NOT_APPLICABLE
REWORK_TIME = NOT_INSTRUMENTED
REQUESTED_CA_UNIVERSE_ROW_COUNT = NOT_OBTAINED
CA_UNIVERSE_BYTES = NOT_OBTAINED
FULL_SUITE_USED = FALSE
VALIDATOR_COUNT = 0
```

The second target request was a single client-compatibility forward attempt,
not a retry loop.  It produced the final exact 407-byte authoritative access
statement; no further target request was made.

## 7. Exact blocker and next admissible trigger

```text
BLOCKER_CLASS = CREDENTIAL_OR_MANUAL_AUTHORITY
BLOCKER = OFFICIAL_KRX_MDCHARD048_REQUIRES_LOGIN_OR_MEMBERSHIP
ADDITIONAL_API_BOUNDARY = AUTH_KEY_AND_SERVICE_USE_REQUIRE_ADMIN_APPROVAL
OWNER_ACTION_IF_PURSUED = AUTHORIZED_KRX_ACCOUNT_LOGIN_OR_CUSTODIAN_EXPORT
REQUIRED_EXPORT_SCOPE = 2024-01-01..2026-08-14_AND_PINNED_CODE_UNION
REQUIRED_EXPORT_METADATA = QUERY_PARAMETERS_PUBLICATION_CUTOFF_FIELDS_ROW_COUNT_SHA256_RECEIPT
RESUME_TRIGGER = EXACT_CONFORMING_KRX_CA_EVENT_UNIVERSE_BYTES_AND_AUTHORITY_RECEIPT_ARRIVE
```

## 8. Claim ceiling

This receipt candidate establishes only that the official KRX locator exists
and is credential-gated, and that the current public Open API catalog does not
list a conforming CA-universe service.  It does **not** establish event
completeness, source exhaustion, Axis-C reconciliation, corporate-action type
or factor, code continuity, correction lineage, G3 closure, integrated gate
closure, validation readiness, or PASS.
