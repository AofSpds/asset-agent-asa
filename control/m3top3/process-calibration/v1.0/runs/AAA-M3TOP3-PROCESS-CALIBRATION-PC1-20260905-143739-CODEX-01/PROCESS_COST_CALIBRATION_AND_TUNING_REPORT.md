# M3Top3 PC1 Process Cost Calibration and Tuning Report

RUN_ID = `AAA-M3TOP3-PROCESS-CALIBRATION-PC1-20260905-143739-CODEX-01`

SCIENTIFIC_STATUS = `EXPLORATORY_PROCESS_CALIBRATION_AFTER_W1_OUTCOME_EXPOSURE`

STATE = `COMPLETE_BOUNDED_ZERO_GAIN_PARTIAL_TELEMETRY`

TIME_START_KST = `2026-09-05T14:37:39.3805426+09:00`

TIME_END_KST = `2026-09-05T16:00:46.9632098+09:00`

## Executive result

The frozen five-item calibration batch reached a terminal state without changing the executable, model semantics, PIT rules, score/seal output, or governed outcome state. No cutoff-safe official F02 source was found for `KRX:003160`, `KRX:025560`, `KRX:031980`, or `KRX:036200` after the bounded official-source route, so the Strict scoreable population remained `1/57` and scoreability gain was zero. Two official retrospective filings for `KRX:005290` support that no W1 corporate-action price adjustment was required, but they do not close the separate `PRICE-CANONICAL` and CA receipt-binding contract gate. The predecessor state `PRELIMINARY_RAW_PRICE_MEASURED_CA_UNVERIFIED` is therefore preserved without upgrade.

This is a process-calibration result, not a negative finding about the issuers and not confirmatory v1 evidence. Missing browser-action, active/wait, token, and native CRU telemetry is reported as `NOT_INSTRUMENTED`, never as zero.

## P0 frozen baseline

- Branch/worktree: `task/aaa/m3top3-process-calibration-pc1-20260905` / `C:\Users\ms1pk\dev\asset-agent-asa\asset-agent-asa\p`.
- Execution request: 11,364 bytes, 278 lines, SHA-256 `8492e1f00ee876b8e6d940eccf50c9ff0caa11874ef9dd81ae9fddeedb658708`.
- Predecessor run/report HEAD: `AAA-M3TOP3-REAL-INPUT-STRICT-PRAGMATIC-20260905-114150-CODEX-01` / `a7b173cf28dc287e1e619e723e938b9bc2c3fd9e`.
- Reviewed code candidate: `c15cbfa9bbedcb3b388b9d101b269ced2fc83bc5`.
- Score/seal preservation commit: `0dfef7b81566e6ec018994d5597f3f8f923944d1`.
- Executable identity: `M3TOP3-REAL-INPUT-EXECUTABLE-BUNDLE-SHA256:4d828c0308bf892718832e9cb02d87ee7716b9b62c28d643b69b424b5f2b6a4a`; all 16 components match the predecessor byte-for-byte.
- Frozen W1 baseline: `1/57` Strict scoreable rows; only `KRX:005290` was scoreable, at score 50.
- Worker topology: at most two bounded read/research lanes plus PMO single-writer assembly.

The first Windows checkout materialized three executable files with CRLF bytes. The initial runtime-bundle observation and an associated byte-total error remain preserved in append-only P0 records. P0C restored the exact predecessor LF bytes, and P0C2 corrected the initial byte total from 96,491 to 96,694. Neither correction changed semantics or committed predecessor content.

## Five-item terminal disposition

| Company | Frozen lane | Terminal result | New scoreable rows | Reason |
|---|---|---:|---:|---|
| `KRX:003160` | F02 official source | Not found | 0 | No cutoff-safe official F02 source after bounded route |
| `KRX:025560` | F02 official source | Not found; one after-cutoff report observed | 0 | No cutoff-safe official F02 source after bounded route |
| `KRX:031980` | F02 official source | Not found; one after-cutoff report observed | 0 | No cutoff-safe official F02 source after bounded route |
| `KRX:036200` | F02 official source | Not found; one after-cutoff report observed | 0 | No cutoff-safe official F02 source after bounded route |
| `KRX:005290` | CA/comparable-price evidence only | No W1 adjustment required is supported; no outcome upgrade | 0 | `PRICE_CANONICAL_AND_CA_CONTRACT_GATE_NOT_CLOSED` |

For the four F02 items, zero candidates reached PIT admission, so parsing, transformation, sidecar materialization, and score/seal execution were correctly skipped. A zero-new-row result was an allowed terminal outcome under the request.

## Corporate-action and comparable-price result

The two exact official source objects total 4,915,819 bytes:

- Q3 filing: 1,676,499 bytes, SHA-256 `a3e7febc9b2c1b33511ae051bf830f09815df59335eb4f7182e7c382e4881263`.
- FY2024 annual filing: 3,239,320 bytes, SHA-256 `65cbb79d6c654c27f4916df538bbec123e59c2ced6f367f0b64401f2543f2369`.

The Q3 filing records 51,414,494 shares at 2024-09-30 and no current-period cash or stock dividend in the inspected Q3 table. The annual filing records no share-count movement during 2024 or 2023. Its year-end cash-dividend record date was 2024-12-31, after the frozen W1 exit of 2024-11-11, and it reports no stock dividend. The locally governed price buffer also holds 51,414,494 shares throughout its 244 observed 2024 rows and contains no null or zero OHLCV values. Together these facts support `NO_W1_ADJUSTMENT_REQUIRED_SUPPORTED` for the observed W1 series.

That evidence is retrospective and CA-only. The executable outcome path has no receipt input, the raw price buffer is expressly non-canonical, and the global D4/`PRICE-CANONICAL` gate remains outside this run. Consequently no model or outcome executable was run, and no status was promoted.

## Plan versus actual wall time

Wall intervals use the host KST clock. They do not represent active labor because active/wait attribution was not instrumented.

| Stage | Planned P50 / P90 | Actual wall | Result |
|---|---:|---:|---|
| P0 baseline freeze | 10m / 20m | 11m 48s through P0C | Complete; P0C2 later corrected the byte-total record |
| P1 discovery/acquisition | 25m / 45m | 28m 30s from P0C to terminal evidence | Complete with partial browser telemetry |
| P2 first new input-to-score success | 20m / 40m | N/A; terminal concurrently with P1 | No success existed; zero candidates made P2 not applicable |
| P3 five-item terminal assembly | 10m / 25m | 6m 59s after P1 terminal | Complete |
| P4 affected validation | 15m / 30m | 18m 01s after P3 | Pass, 31/31 fresh checks |
| P5 post-run calibration | 15m / 30m | 17m 50s including independent closure audit and correction | Complete; 2m 50s above stage P50 and within P90 |
| Overall | 1h 35m / 3h 10m | 1h 23m 08s | 11m 52s before P50 and 1h 46m 52s before P90 |

The first-30-minute return preserves its original measurement cutoff, 2026-09-05 15:07:39 KST, but was recorded approximately 17m 16s late. The underlying browser actions were not wrapped by an atomic attempt journal, so the checkpoint provides an observed lower bound rather than reconstructing a false exact denominator.

## Route efficiency ranking

| Rank | Route | Measured result | Calibration judgment |
|---:|---|---|---|
| 1 | Exact content-addressed local cache | 2 useful hits / 6 observed lookups; 33.33% cache-hit rate | Lowest-cost useful route; retain first |
| 2 | Company-specific all-disclosure cutoff check | 0 useful hits / 3 observed query-page units | Fast terminal exclusion; retain before global search |
| 3 | Company-specific exact-title search | 0 useful hits / 3 observed query-page units | Cheap but low-yield; retain as a bounded probe |
| 4 | Exact CA official-source fetch | 2 useful documents / 2 fetches; 4,915,819 bytes | Evidence-rich, but zero outcome upgrades because the contract gate was absent |
| 5 | Global exact-title pagination | 0 target hits / 40 page units; 7 pages were decision-irrelevant overscan | Highest measured avoidable search cost; tighten stop state |
| 6 | Bounded web corroboration | No admissible F02 source; at least four unusable/cutoff-failed observations | Total attempt denominator was not instrumented; use only after official routes |

The four F02 features tie at zero acquisition and zero scoreability yield. The CA item is not a feature-acquisition candidate by design: it yielded an exact comparability finding but `0/1` governed outcome upgrades.

## Frozen process metrics at terminal

| Metric | Terminal value |
|---|---|
| Retrieval attempts | `NOT_INSTRUMENTED_TOTAL`; known route-unit lower bound 56, of which 54 were atomically ledgered |
| Useful source hits | 4: two cache hits and two exact CA documents |
| Retrieval hit rate | `NOT_COMPUTABLE_TOTAL_ATTEMPT_UNITS_INCOMPLETE` |
| PIT admission yield | `NOT_APPLICABLE_ZERO_CANDIDATES` |
| Transform success rate | `NOT_APPLICABLE_ZERO_ADMITTED_SOURCE_VALUES` |
| Scoreability gain | 0 (`1/57` to `1/57`) |
| Scoreable rows per wall hour | 0 |
| Scoreable rows per active hour | `NOT_INSTRUMENTED` |
| Coverage gain per wall hour | 0 |
| Retry rate | `NOT_INSTRUMENTED` |
| Cache hit rate | 2/6 = 33.33% |
| Duplicate-fetch rate | `NOT_INSTRUMENTED_BROWSER_FETCH_TOTAL_INCOMPLETE` |
| Validation rework ratio | `NOT_INSTRUMENTED` |
| Same-route/no-evidence repeats | Observed at least 1; total not instrumented |
| Route switches | Observed at least 3; total not instrumented |
| Token or CRU per scoreable row | `NOT_INSTRUMENTED` |

## Validation, rework, and reuse

Fresh affected validation passed 31/31 checks. It covered artifact parsing, required ledger fields, all-five terminal arithmetic, source byte sizes and hashes, Git-blob custody, physical-line anchors, raw-outcome preservation, the 16-component executable binder, and absence of executable changes from the predecessor report HEAD.

The first validation execution contained a validator-only expected-count assertion of 10 top-level JSON/JSONL artifacts when 11 existed. It did not reveal a product or data defect; the corrected second execution passed. This produces one disclosed recheck. Code-test executions in this PC1 run were zero. Because the executable bundle was byte-identical, the prior 71/71 affected campaign was reused and 71 duplicate test-case executions were avoided; no larger avoidance claim is made.

An independent P5 closure audit then identified four record-level contradictions: a 54-unit atomic ledger lower bound had been presented without the additional two known unledgered autocomplete units; the frozen progress-weight label said “fully instrumented”; the first savings draft inferred page latency without persisted timing; and the manifest's zero duplicate count lacked its two-materialized-object scope. All four were corrected. The audit also found a generated Python cache and an expected dirty pre-commit closure candidate; the cache was removed, while final clean-state verification is performed after the self-referential artifacts are committed.

Final finding inventory before P5 closure:

- P0: 0.
- P1: 1 — browser attempt denominators were incomplete.
- P2: 3 — late first-30-minute record, seven-page global-search overscan, and the `KRX:036200` same-failure limit was not cleanly enforced or atomically counted.
- P3: 2 — CRLF materialization rework and the validator expected-count error.
- Unresolved in-scope validation blockers: 0.

## High-cost/low-yield loops

1. The global exact-title scan consumed 40 page units, found zero targets, and included seven pages beyond the decision-relevant date band. This was the clearest measured avoidable loop.
2. Web corroboration produced only unusable, false-positive, or after-cutoff observations while lacking an exact attempt denominator. It added search complexity without an admissible F02 value.
3. The CA lane fetched two official documents totaling 4,915,819 bytes and produced a meaningful comparability finding, but could not change the outcome because the necessary canonical-price and receipt-binding gates were absent before retrieval.
4. Restoring exact LF bytes and correcting the validator artifact count were one-time local rework events. Both were resolved and rechecked, but neither should recur under the next-window controls.

## Low-cost/high-yield routes

1. Content-addressed cache checks returned two useful hits from six lookups and avoided redundant custody copies.
2. Company-specific all-disclosure queries terminalized three issuers quickly; the observed query groups took approximately 4.8–5.9 seconds each.
3. Exact known CA document retrievals produced two useful official sources in two fetches. Their scientific utility was high even though their governed outcome utility was blocked.
4. Exact executable-bundle binding allowed safe reuse of the prior 71/71 validation campaign.

## Precommitted W2 tuning controls

These controls are fixed before any future W2 outcome exposure:

1. Wrap every cache lookup, query, result-page open, source fetch, parser run, and route switch in an atomic append-only ledger event before the action begins; close the same event with result, wall time, bytes, and failure class.
2. Implement an explicit per-company `(route, failure_class)` state machine. After the same route and same failure occurs twice without new evidence, prohibit a third attempt and force a logged route switch or terminal disposition.
3. Use this search order: content-hash cache; company all-disclosure query constrained through cutoff; company exact-title probe; global exact-title pagination; then bounded web corroboration. In global pagination, stop as soon as the page range falls entirely before the relevant reporting cycle.
4. Deduplicate before fetch by normalized locator and, after fetch, by content hash plus parser version. Never refetch an already-bound locator/hash pair.
5. Before W2 execution, either validate a semantics-neutral issuer-parameterized adapter against the unchanged contract or restrict the batch to source shapes already supported. Do not patch issuer-specific anchors during the window.
6. Treat CA acquisition as conditional: do not fetch retrospective CA documents unless a `PRICE-CANONICAL` input and an executable receipt-binding path already exist. If either precondition is absent, terminalize the governed upgrade lane and state what evidence remains scientifically useful.
7. Preserve raw official-source bytes under source-local `.gitattributes`; compare working bytes, Git blob bytes, byte count, and SHA-256 before citing line anchors.
8. Reuse the prior 71/71 campaign only when all executable binder components match exactly. Any executable change requires fresh affected-code tests.
9. Retain the concurrency ceiling of two bounded author/research workers plus PMO single-writer assembly.

## Expected savings for the next window

| Control | Measured basis | Expected saving | Confidence |
|---|---|---|---|
| Stop global pagination at the reporting-cycle boundary | 7 of 40 page requests were decision-irrelevant overscan | Exactly 7 requests, or 17.5% of this observed route; wall-time saving is not estimable | High for request count; wall time was not instrumented |
| Enforce no-third same-failure state | At least one recurrence was observed after the bounded rule should have controlled the lane | At least 1 request opportunity; upper bound and wall-time saving are not estimable | Low; total recurrence and wall time were not instrumented |
| Gate CA fetches before acquisition | Two documents, 4,915,819 bytes, and zero governed upgrade under the already-open gate | Two fetches and 4,915,819 bytes when the same gate is known closed | High for actions/bytes; wall-time saving not claimed |
| Reuse validation by exact binder | Current byte-identical bundle allowed reuse of 71 prior passing cases; one prior campaign reported 1.446s | Exactly 71 test-case executions; no defensible future wall-time range from one observation | High for case count; low for time |
| Atomic attempt logging | Current totals and rates were not computable | Measurement completeness, not a time-saving claim | High for denominator integrity |

These savings are calibration targets, not guaranteed throughput. Action and byte savings are exact or explicitly lower-bounded from persisted counts. No page-latency saving is claimed, and the single historical 1.446-second test runtime is not converted into an unsupported future range. W2 must report measured actuals against these targets and preserve `NOT_INSTRUMENTED` wherever the relevant numerator or denominator is absent.

## Claim boundary

This run is exploratory process calibration after W1 outcome exposure. It establishes source custody, bounded terminal dispositions, a retrospective CA finding, exact executable identity, validation reuse, and next-window operating controls. It does not change the model, feature definitions, PIT/provenance semantics, score/seal logic, price-canonical policy, governed W1 outcome, release status, promotion status, or production state. The absence of a cutoff-safe source in this bounded route is not proof that no such source exists anywhere.
