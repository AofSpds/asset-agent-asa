# G3 Axis B/C + calendar minimal governed protocol candidate

```text
PROJECT = AAA / ASSET AGENT ASA
PERSONA_SCOPE = AAA-PMO-ORCHESTRATOR DELEGATED NON-VALIDATOR WORKER
WORK_UNIT = FC1-G3 / G3-B CA AXES B/C + G3-C GOVERNED CALENDAR
ISSUED_AT_KST = 2026-08-26T01:29:17+09:00
STATUS = READY_FOR_OWNER_SEMANTIC_DECISIONS_AND_SOURCE_CUSTODY
VALIDATOR_HOLD = TRUE
VALIDATOR_OR_REVIEWER_USED = FALSE
GLOBAL_VALIDATION_OR_FULL_REGRESSION = NOT_RUN
VALIDATION_LOOP = NOT_RUN
MECHANICAL_AXIS_B_OR_C_SCAN = NOT_RUN
GIT_OR_ISSUE_MUTATION = NONE
GATE_PASS_CREATED = FALSE
```

## 1. Bounded disposition

This packet closes the **protocol-definition pass**, not G3. It derives the
narrowest deterministic rules already supported by governed text and isolates
four semantic/authority decisions that PMO must not guess.

The ready route is:

1. Owner answers the four defaulted decisions in section 6.
2. A custodian supplies exact independent KRX corporate-action and calendar
   artifacts with byte identity and authority receipts.
3. A worker materializes the adopted protocol and executes only the two bounded
   scans plus calendar reconciliation.

Until then, Axis B, Axis C, and governed calendar remain open. This packet
creates no new PASS, receipt, release, or validation credit.

## 2. Exact evidence surface

| Artifact | Exact identity / locator | Material fact used |
|---|---|---|
| Prior bounded assessment | SHA-256 `d0d355d3727e6cb0d8fdcad34aefe835c0ce0edc7eed8df6287a8e47cd066808` | B threshold/formula, C independent universe, and calendar authority were open |
| Working workbook | 563,995 bytes; SHA-256 `44501584c9dc6224637e9193219c1e8c87507af77dc15dc3944a3d04af524cda`; `Protocol_Registry!A42:D44`, `Execution_Coverage!A79:H79`, `CA_Audit_Signals!A1:S25`, `Corporate_Actions!A1:R12` | Existing field pair is current Open / prior observed Close; Axis A uses a 20% stock-count signal; 11 evidenced CA rows exist; B/C remain open |
| Price/CA admission queue | SHA-256 `b7d07a1c3438c30bced3161ea5d287d53f34431c7ab3f5e040a761ea06548412` | Axis B covers all three exact components; Axis C must be exhaustive |
| Price import manifest | SHA-256 `ca8f117a83cd3da800a2a2b5e0ebdca3c89ff658ff3fd21b5083e4aae9ab98ce`, rows 8–10 | Discontinuity is a signal only; adjustment factor must be evidence-backed; status flags are preserved |
| Data route | SHA-256 `508f98e88c150ceb751db2227727db529eb04da467c53a6eed5278ca5e17aa02` | One KRX-derived ledger; provider mixing prohibited; Snapshot/Entry/Exit mechanics |
| PIT ledger | SHA-256 `acde50e7090382e95cc585227c4dd52df6b3f342258b6debfa0aabb7db94006a` | Daily source state and snapshot decision are separate; Entry-day tradability is explicit |
| Canonical lineage contract | SHA-256 `f6eab8c880c498c09c52aef1b1b30e37b94de7ada9e6fc00994b5b2e7df5b0b9` | CA/calendar/window releases need exact artifact, digest, state, date, and authority identity; self-certification prohibited |
| Acceptance/stop contract | SHA-256 `f001a1187af6d5906d4b449b90b105f9554ade78303612830de4ab857ba67690` | Runtime cannot infer missing CA completeness |

Exact Axis-B population:

| Year | Rows | Dates | Range | Bytes | SHA-256 |
|---|---:|---:|---|---:|---|
| 2024 | 687,708 | 244 | 2024-01-02–2024-12-30 | 24,572,111 | `b0c38943e67637d5faf88429880092cf0f46a394be39860dd3bcd0b04231bccb` |
| 2025 | 696,524 | 242 | 2025-01-02–2025-12-30 | 25,153,419 | `2bfd93c217eb74263bc5020b23fa6debb6b02531c11eaccc2826639bc191559e` |
| 2026 through 08-14 | 437,787 | 152 | 2026-01-02–2026-08-14 | 16,297,737 | `b6f3f8ea110326b21d23b5344e6abe159f8ea7f7a345262155b929c08886fc9d` |

Total: `1,822,019` rows. The 638 year-partitioned distinct price dates are a
diagnostic source-date index only.

## 3. Rules already inferable without an Owner decision

### Axis B

- Population is every row of the three exact components.
- Existing audit semantics identify the candidate comparison pair as current
  `Open` and the immediately prior observed `Close` for the same security code.
- Processing must stitch year boundaries before comparison.
- A discontinuity is an audit signal only. It cannot create a CA type, factor,
  adjustment, suspension, trading status, or row deletion.
- Adjustment requires explicit event evidence. Provider mixing is prohibited.
- Every source row must be retained with an evaluability/terminal disposition;
  unresolved rows cannot be silently dropped.

### Axis C

- Preserve the 24-row Axis-A signal audit and the 11 existing evidenced CA
  rows within their exact original scope.
- Omission exhaustion requires a source universe independent of the workbook's
  CA rows and Axis-A/B signals.
- Event identity, publication/effective date, type, factor when supported,
  evidence reference, and correction lineage must be explicit.
- Price or stock-count discontinuity cannot self-certify an independent event
  universe.

### Calendar and windows

- Snapshot is date `T` EOD.
- Entry is the first governed trading date strictly after Snapshot.
- Holding dates run from Entry through window end inclusive.
- Exit is the first governed trading date strictly after window end.
- Price-date union can diagnose coverage but cannot authorize the calendar.
- Calendar membership can verify dates and next-date mechanics; it cannot
  establish why the W1–W8 snapshots were chosen. Window authority stays a
  separate release/binding.

## 4. Ready-to-adopt minimal protocol candidate

### 4.1 Axis B — material Open/previous-Close signal

Proposed exact test, pending `OD-G3-B-01`:

\[
g_t = \left|\frac{Open_t-PreviousClose_t}{PreviousClose_t}\right|,
\qquad signal_t = (g_t \ge 0.20)
\]

Implement without floating-point rounding:

```text
abs(Open_t - PreviousClose_t) * 10000 >= 2000 * PreviousClose_t
```

The 20% value is **not** presently an OHLC authority rule. It is the narrowest
default because 20% is the only explicit materiality constant on the existing
CA audit surface (Axis-A stock-count signal). Reusing it for Axis B is a
conservative signal-screen proposal and requires Owner ratification. The
inclusive boundary maximizes deterministic capture at the exact threshold.

Deterministic processing:

1. Group by exact security code; sort ascending by date across all three years.
2. For each row, use the immediately prior observed same-code row's Close.
3. Record signed and absolute change, direction, prior date, and calendar-day
   gap. Do not infer semantics from a long gap.
4. First same-code observation: `FIRST_OBSERVATION_NO_COMPARISON`.
5. Duplicate same-code/same-date rows: `DATA_INTEGRITY_BLOCKER`; never choose a
   winner silently.
6. Missing/non-numeric price or `Open <= 0` or `PreviousClose <= 0`:
   `NOT_EVALUABLE_PRICE_DOMAIN`; retain and route to technical OHLC
   classification, with no CA/status inference.
7. Code change/relisting continuity is used only with explicit official mapping;
   otherwise the new code starts as a first observation.
8. Every material signal reconciles against Axis C. A complete independent
   universe may support `NO_KRX_EVENT_MATCH_SIGNAL_ONLY_NO_ADJUSTMENT`; the
   price signal itself cannot.

Axis-B closure requires exactly one terminal disposition for all 1,822,019
rows, zero integrity blockers, zero unresolved rows, and terminal Axis-C
reconciliation for every material signal.

### 4.2 Axis C — independent KRX event universe

Required input is one independently frozen `KRX_CA_EVENT_UNIVERSE`, not derived
from current CA rows or price/stock-count signals, carrying:

- exact bytes, SHA-256, source locator, query/export parameters, acquired time,
  publication cutoff, effective-date/security scope, row count, and
  custodian/authority receipt;
- effective-date coverage `2024-01-01` through `2026-08-14`;
- the union of security codes in the three exact components, with explicit
  official old/new-code continuity when applicable; and
- source event ID, issue identity, publication time, exact official effective
  or basis date, source event type, comparable-price impact, supported factor,
  correction/supersession reference, and evidence reference.

Proposed in-scope event taxonomy, pending `OD-G3-C-01`:

1. stock split;
2. reverse split/consolidation;
3. bonus/free issue;
4. capital reduction with unit or basis impact;
5. rights/ex-rights event with official basis-price impact;
6. merger/stock exchange with unit or basis impact;
7. spin-off/demerger with unit or basis impact;
8. other official KRX event explicitly carrying comparable-price or unit
   impact; and
9. correction, cancellation, or supersession of any class above.

Observe but never auto-adjust: paid-in share issuance, CB/BW conversion,
merger share issuance without unit/basis change, name change, cash dividend,
and listing/suspension events without comparable-price impact. Event class alone
never authorizes adjustment.

Matching and edge rules:

- primary match is security code plus exact official effective/basis date;
- fuzzy-date matching is prohibited;
- an effective interval is usable only when the source explicitly supplies it;
- multi-security events expand into deterministic security legs while
  preserving the parent event ID;
- identical duplicate event IDs may collapse; conflicting duplicates remain
  unresolved;
- an explicit latest non-cancelled correction by the frozen publication cutoff
  supersedes the prior record while preserving lineage; and
- factor comes only from explicit official evidence or the already governed
  bonus-issue formula `post-rights-date price × (1 + new shares per old share)`.

Axis-C exhaustion requires 100% terminal disposition of the byte-bound source
universe, 100% terminal reconciliation of existing CA rows and Axis-A/B
signals, zero live duplicate identities, zero missing required fields, zero
unresolved events, and exact manifest count/digest reconciliation.

### 4.3 Governed trading calendar

Required normative input is exact official KRX equity regular-session calendar
bytes—or an explicitly Owner-designated authority equivalent—with exact hash,
source locator, acquisition time, date/market scope, row count, and authority
receipt. It must cover `2024-01-01` through at least `2026-08-14` and every
market represented by the exact component securities.

Canonical grain is `market_id + trade_date` unless the authority source proves
one common KRX equity calendar. A half-day counts only when the authority source
marks an in-scope equity session open; an exceptional closure is absent. No
market-common calendar is inferred from price presence.

Deterministic derivation:

- Snapshot and window end come from the separate governed window registry and
  must be calendar members.
- `Entry = min(trade_date > snapshot)`.
- holding dates are governed dates from Entry through window end inclusive.
- `Exit = min(trade_date > window_end)`.
- missing security price on an open date is a price coverage/tradability issue,
  not a calendar closure.

Diagnostic comparison to the price-date union:

- official-only date → price-source coverage finding, never automatic calendar
  removal;
- price-only date → calendar/source conflict requiring explicit adjudication;
- release requires zero unresolved conflicts and exact artifact/manifest/
  authority binding.

### 4.4 W1–W8 authority boundary

Current candidate identity: 414 bytes, SHA-256
`96d63cc98a01b6332cf9486440e7f3fdaa0ec5a2d605f21bc14a4025b46e69fe`.
Local values agree 8/8, but upstream tuple provenance remains open.

| W | Snapshot | Entry | Window end |
|---|---|---|---|
| W1 | 2024-08-09 | 2024-08-12 | 2024-11-08 |
| W2 | 2024-11-08 | 2024-11-11 | 2025-02-10 |
| W3 | 2025-02-10 | 2025-02-11 | 2025-05-09 |
| W4 | 2025-05-09 | 2025-05-12 | 2025-08-08 |
| W5 | 2025-08-08 | 2025-08-11 | 2025-11-10 |
| W6 | 2025-11-10 | 2025-11-11 | 2026-02-10 |
| W7 | 2026-02-10 | 2026-02-11 | 2026-05-08 |
| W8 | 2026-05-08 | 2026-05-11 | 2026-08-10 |

The calendar may verify membership and next-date mechanics. It cannot create
tuple authority or clean-holdout/OOS status. If Owner ratifies this exact hash,
PMO must materialize a separate outcome-free authority binding; ratification
does not itself create a release.

## 5. What genuinely still requires Owner authority

| Decision | Why it cannot be inferred |
|---|---|
| Axis-B 20% inclusive threshold | Existing 20% constant governs stock-count signals, not OHLC materiality |
| Axis-C taxonomy/scope/exhaustion adoption | Current text names the sweep but does not freeze its event set or acceptance rule |
| Calendar authority class | Raw price dates cannot self-certify official exchange-open status |
| W1–W8 exact tuple authority | Existing Owner documents govern role/exposure but do not enumerate the eight date tuples |

Exact KRX CA/calendar bytes are source-custody dependencies, not facts that an
Owner decision can manufacture.

## 6. Exact defaulted Owner decision packet

Owner may reply with four lines:

```text
OD-G3-B-01 = YES
OD-G3-C-01 = YES
OD-G3-CAL-01 = YES
OD-G3-WIN-01 = YES
```

Meanings:

- `OD-G3-B-01 = YES`: adopt absolute current-Open versus immediately-prior-
  observed-Close change `>= 20%`, inclusive, exact/no-rounding, signal-only.
  `NO` must provide `threshold_bps` and `inclusive|exclusive`.
- `OD-G3-C-01 = YES`: adopt section 4.2 scope, taxonomy, exact-date matching,
  correction lineage, and zero-unresolved exhaustion. `NO` must state exact
  taxonomy/scope/match/exhaustion deltas.
- `OD-G3-CAL-01 = YES`: official KRX equity regular-session artifact, or an
  explicitly Owner-designated authority equivalent, is normative; price dates
  remain diagnostic-only. `NO` must name the alternative authority and market/
  session scope.
- `OD-G3-WIN-01 = YES`: ratify the exact 8-row candidate hash solely as an
  outcome-exposed development/descriptive registry and authorize an outcome-free
  authority binding. `NO` must provide replacement tuples or exact upstream
  source/locators.

All four defaults are recommended for the fastest bounded route. `YES` does not
waive missing source bytes, receipt requirements, validation, or claim ceilings.

## 7. Timing with validator excluded

| Worker-only unit | Preconditions | P50 | P90 |
|---|---|---:|---:|
| Adopt decisions + materialize protocol bindings | four Owner answers | 0.25 h | 0.75 h |
| Axis B scan/candidate | `OD-G3-B-01` | 0.75 h | 1.5 h |
| Axis C reconciliation/candidate | `OD-G3-C-01` + exact independent event bytes | 1.0 h | 2.5 h |
| Calendar candidate/reconciliation | `OD-G3-CAL-01` + exact calendar bytes | 0.5 h | 1.0 h |
| Combined bounded worker candidate | all decisions and bytes | **2.25 h** | **5.0 h** |

Conditional compute: `25–40 CRU`. External custodian/source wait and validator
time are excluded. Worker-active timing confidence is medium; current wall-clock
ETA remains not measurable because source wait is unbounded.

## 8. Risk and claim ceiling

Primary risks:

- 20% is not yet governed for OHLC and may create false positives/negatives;
  signal-only handling plus independent Axis C limits semantic harm.
- price-date union could self-certify the calendar; the protocol forbids it.
- code changes and corrections can create silent duplication; only explicit
  official mapping/supersession is accepted.
- Owner ratification could be mistaken for validation/release; all adopted
  rules still require exact artifacts and the later minimum necessary exact-
  delta validation outside this worker scope.

```text
G3_B_AXIS_B = OPEN / OWNER_THRESHOLD_DECISION_PENDING
G3_B_AXIS_C = OPEN / OWNER_PROTOCOL_DECISION_AND_EXACT_KRX_SOURCE_PENDING
G3_C_CALENDAR = OPEN / OWNER_AUTHORITY_DECISION_AND_EXACT_SOURCE_PENDING
W1_W8_AUTHORITY = PROVENANCE_OPEN / OWNER_BINDING_DECISION_PENDING
G3_GATE_EFFECT = NONE
VALIDATION_CLOSURE_DELTA = 0
```

No claim is made for Axis-B/C exhaustion, CA completeness, corporate-action
release, governed calendar release, W1–W8 authority release, clean holdout/OOS,
PIT eligibility/tradability, Price Canonical, G3/integrated closure, EOPT-G0,
A/A, Golden, Replay, Freeze, Promotion, Release, or Production.

Machine-readable companion:
`G3_B_C_CALENDAR_MINIMAL_GOVERNED_PROTOCOL_CANDIDATE_2026-08-26.json`.
