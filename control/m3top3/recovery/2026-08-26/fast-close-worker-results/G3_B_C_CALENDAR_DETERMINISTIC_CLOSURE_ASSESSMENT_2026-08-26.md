# G3-B / G3-C deterministic-closure assessment

```text
PROJECT = AAA / ASSET AGENT ASA
PERSONA_SCOPE = AAA-PMO-ORCHESTRATOR DELEGATED NON-VALIDATOR WORKER
WORK_UNIT = FC1-G3 / G3-B CA AXES B/C + G3-C GOVERNED CALENDAR
ISSUED_AT_KST = 2026-08-26T01:05:44+09:00
VALIDATOR_HOLD = TRUE
IVA_EXECUTION_PARTICIPATION = NONE
SOURCE_MODE = READ_ONLY
GIT_OR_ISSUE_MUTATION = NONE
PRICE_BYTE_RECOVERY = NOT_REPEATED
SEALED_RECEIPT_REPLAY = NOT_RUN
```

## 1. Executive disposition

`DETERMINISTIC_GATE_CLOSURE = NOT_CURRENTLY_EXECUTABLE`

The exact 2024/2025/2026 price components are present and pinned, so byte custody is not the immediate blocker. The blocker is semantic/authority incompleteness:

1. **Axis B** names an exhaustive “material OHLC discontinuity” sweep, but no governed numeric threshold, comparison formula, boundary convention, or adjudication acceptance rule was found.
2. **Axis C** names an exhaustive “known-KRX unit/comparable-price omission” sweep, but no independently frozen KRX event universe, source artifact, event taxonomy, scope, or exhaustion rule was found.
3. **Governed calendar** is required, but no calendar artifact, exact derivation profile, independently supplied expectation manifest, or authority receipt exists. Distinct dates observed in the three price components are raw file-calendar facts, not a governed trading-calendar release.

Accordingly, no Axis B/C scan was executed. Running one would require inventing the missing semantics or self-certifying the reference universe, both prohibited by the governing controls.

## 2. Exact evidence anchors

### 2.1 Working workbook

Exact workbook:

- path: `/workspace/scratch/577256efb437/qa/wp2_sources/U127_Data_Expansion_Working_v0.8_2026-08-15.xlsx`
- bytes: `563,995`
- SHA-256: `44501584c9dc6224637e9193219c1e8c87507af77dc15dc3944a3d04af524cda`

Exact cells:

- `Protocol_Registry!A42:D42` — `CA_COMPLETENESS_FINAL_SCAN`; value `IN_PROGRESS / LOCATOR_PARTIALS_CLOSED / TWO_AXES_OPEN`; note says Axis A closed, Axis B material-OHLC cross-check open, and Axis C known-KRX comparable-price/unit-change omission sweep not proven exhaustive.
- `Protocol_Registry!A43:D43` — `CA_COMPLETENESS_GATE`; `PENDING_FINAL_SCAN / BLOCKER`; “Do not promote until B and C are deterministically closed.”
- `Protocol_Registry!A44:D44` — exact unresolved items; again names B and C but supplies no threshold, formula, reference-universe identity, or acceptance rule.
- `Execution_Coverage!A79:H79` — `CA_COMPLETENESS_FINAL_SCAN = 1/3`, with B and C open.
- `CA_Audit_Signals!A1:S25` — 24 data rows, 19 unique codes, all signal labels `STOCKS_CHANGE_GE_20PCT`; 8 no-adjustment, 11 adjustment-required, 5 not-applicable.
- `Corporate_Actions!A1:R12` — 11 data rows, 10 unique codes; 11 evidence-audit statuses contain `PASS`.

The three CA-related sheets contain **zero formulas**, zero comments, and no defined names. Thus the B/C rules are not hidden in formulas, workbook comments, or named ranges.

### 2.2 Price/CA queue and source contract

- `/workspace/scratch/577256efb437/remediation/r_wp23_data_closure/04_PRICE_CA_CURRENT_BYTE_ADMISSION_QUEUE.csv:10` binds Axis B to all three frozen yearly byte components, but still only says “material OHLC discontinuity”; no materiality definition is present.
- The same file at line 11 requires an exhaustive KRX comparable-price/unit-change omission sweep, but supplies no frozen KRX event artifact or set digest.
- `/workspace/scratch/f56b716343a6/project_sources/10-SEMI-PRICE-LEDGER_IMPORT-MANIFEST_v1.0.csv:8` says a Stocks jump is an audit signal, not a definitive adjustment factor.
- The same file at line 10 says an adjustment factor must be evidence-backed and must not be inferred solely from raw OHLC discontinuity.
- `/workspace/scratch/f56b716343a6/project_sources/13-SEMI-PRICE-LEDGER_v1.0_SCHEMA.csv:1` declares the governed CA/adjustment/status interface fields but provides no data rows or scan semantics.
- `Semi_Data_Route_v1.1`, `T6R2`, requires one KRX-derived OHLC ledger and prohibits provider mixing; `T7R8` says daily refresh on a trading-day basis. Neither row defines the calendar release or Axis B/C closure rule.
- `SEMI-PIT-LEDGER_v1.0`, `T5R1`, separates daily price/CA/status source state from snapshot eligibility/tradability decisions. This prevents using raw zero-OHL or date absence as an implicit trading-status decision.

### 2.3 GitHub authority surface

Issue #54, section `G3C — CA and trading calendar`, requires:

- preserve Axis A;
- complete exhaustive Axis B and C;
- produce a governed 2024–2026 `TRADING_CALENDAR_RELEASE`;
- do not infer trading suspension or adjustment from zero-OHL alone.

The issue does not specify the missing Axis B threshold/formula, the Axis C KRX reference artifact/universe, or the calendar derivation/authority profile. Repository code-search queries for `material OHLC discontinuity threshold`, `known-KRX comparable-price omission`, `TRADING_CALENDAR_RELEASE calendar dates`, and `CA_COMPLETENESS_FINAL_SCAN` returned zero file results.

### 2.4 Runtime/release controls

- `/workspace/scratch/577256efb437/remediation/r_wp4_03_control/R_WP4_03_CANONICAL_LINEAGE_FULL_UNIVERSE_CONTRACT_v0.1.md:88-111` requires each CA/calendar release reference to carry exact artifact, manifest, component-set, state, date, and authority-receipt identity.
- The same file at lines 117-120 prohibits self-certification from the live candidate, except explicit synthetic test-only fixtures.
- The same file at lines 173-178 requires exact one-to-one row-level lineage binding for `CORPORATE_ACTION_RELEASE` and `TRADING_CALENDAR_RELEASE`.
- `/workspace/scratch/577256efb437/remediation/r_wp4_03_control/R_WP4_03_ACCEPTANCE_AND_STOP_CRITERIA_v0.1.md:188` explicitly stops runtime code from inferring missing CA completeness.
- `/workspace/scratch/577256efb437/remediation/r_wp4_03_author/tools/m3top3/admission.py:286-322` permits self-derived CA/calendar identities only for explicitly non-release-eligible synthetic fixtures. It is not an evidence-closure route.

## 3. Available mechanical facts, not closure

Exact pinned range-complete components:

| Year | Rows | Distinct file dates | Range | SHA-256 |
|---|---:|---:|---|---|
| 2024 | 687,708 | 244 | 2024-01-02–2024-12-30 | `b0c38943e67637d5faf88429880092cf0f46a394be39860dd3bcd0b04231bccb` |
| 2025 | 696,524 | 242 | 2025-01-02–2025-12-30 | `2bfd93c217eb74263bc5020b23fa6debb6b02531c11eaccc2826639bc191559e` |
| 2026 through 08-14 | 437,787 | 152 | 2026-01-02–2026-08-14 | `b6f3f8ea110326b21d23b5344e6abe159f8ea7f7a345262155b929c08886fc9d` |

Total candidate Axis-B row population under the queue's “all three components” wording is `1,822,019` rows. The 638 year-partitioned distinct source dates can support a **raw observed file-calendar candidate**. They do not by themselves establish exchange-open status, suspension meaning, W1–W8 tuple authority, or a governed calendar release.

Cross-lane constraint: the existing W1–W8 registry candidate contains eight exact tuples and agrees mechanically with the local role manifest, but upstream tuple authority provenance remains open. A G3 calendar candidate cannot cure that provenance gap without binding the exact upstream authority artifact/record locators.

## 4. Exact decision requirements

### OD-G3-B-01 — Axis B protocol semantics

Required before scanning:

1. Confirm population: all full-market rows in the three exact components, inclusive through 2026-08-14.
2. Freeze the comparison definition: e.g. which of previous close/current open, close/close, adjusted/unadjusted OHLC, or another exact relationship constitutes the discontinuity test.
3. Freeze the numeric materiality threshold, inclusive/exclusive boundary, rounding/tolerance, and direction handling.
4. Define cross-year stitching, first-observation, listing/relisting, zero/invalid price, no-trade, suspension/reopening, and duplicate-date handling.
5. Define candidate disposition taxonomy and evidence needed to classify each signal.
6. Define closure acceptance: all generated candidates adjudicated, zero unresolved, exact artifact/hash/manifest and independent authority receipt.

### OD-G3-C-01 — Axis C reference universe

Required before reconciliation:

1. Supply an independently frozen KRX event artifact/manifest with exact bytes, SHA-256, source locator, acquisition/publication cutoff, and authority receipt.
2. Define market/security scope and date interval.
3. Freeze event taxonomy, at minimum deciding inclusion/exclusion for splits, reverse splits, bonus issues, capital reductions, mergers, spin-offs, rights/ex-rights basis changes, and corrections/cancellations.
4. Define event effective-date/basis-date rules and factor derivation for each event class.
5. Define exact matching keys, duplicate/supersession handling, omission disposition, and exhaustion criterion.
6. Require full reconciliation of the independently supplied event set; the existing 11 rows cannot certify that no other event was omitted.

### OD-G3-CAL-01 — governed calendar authority

Required before release:

1. Select the normative source/derivation profile:
   - preferred authority-grade route: exact KRX official calendar/session artifact; or
   - diagnostic-only route: sorted distinct Date union from the three exact price components.
2. Define markets/sessions, inclusive range, exceptional closures/half-days, and whether a date with any market row is sufficient.
3. Freeze output schema and canonicalization/digest profile.
4. Supply an independent expectation manifest and authority receipt; a calendar derived from the same price bytes cannot self-certify an official release.
5. Bind the resulting release to W1–W8 only after the independent tuple authority/provenance gap is closed.

These choices alter data-admission semantics or authority state and therefore require Owner/governance approval; PMO should not guess them.

## 5. Timing and resource forecast with validator excluded

Current bounded assessment is complete. No validator/reviewer CRU was consumed.

| Unit | Current state | P50 active | P90 active | CRU estimate | External wait |
|---|---|---:|---:|---:|---|
| Blocker/decision packet | DONE | 0.35 h actual | n/a | ~4 | none |
| Axis B candidate after OD-G3-B-01 | BLOCKED_PENDING_RULE | 0.75 h | 1.5 h | 8–12 | excluded |
| Axis C candidate after exact KRX event artifact + OD-G3-C-01 | BLOCKED_PENDING_SOURCE_AND_RULE | 1.0 h | 2.5 h | 12–20 | source wait excluded |
| Calendar candidate/release envelope after OD-G3-CAL-01 | BLOCKED_PENDING_AUTHORITY | 0.5 h | 1.0 h | 5–8 | authority/source wait excluded |
| Combined worker-only exact candidate | conditional | 2.25 h | 5.0 h | 25–40 | excluded |

Without these decisions/source bytes, elapsed time cannot close the gates; the ETA is `BLOCKED`, not merely longer. With them supplied, the worker-only exact candidate is estimated at P50 `~2.25 h`, P90 `~5 h`. Validator hold means the candidate can be authored and mechanically checked, but validation closure remains `0%` and no gate PASS may be claimed.

## 6. Gate effect and claim ceiling

```text
G3_B_CA_AXIS_B = OPEN / SEMANTIC_THRESHOLD_AND_FORMULA_UNGOVERNED
G3_B_CA_AXIS_C = OPEN / INDEPENDENT_KRX_REFERENCE_UNIVERSE_ABSENT
G3_C_GOVERNED_CALENDAR = OPEN / DERIVATION_AND_AUTHORITY_UNGOVERNED
MECHANICAL_SCAN_EXECUTED = NO
CORPORATE_ACTION_RELEASE = NOT_CREATED
TRADING_CALENDAR_RELEASE = NOT_CREATED
PRICE_CANONICAL = BLOCKED
G3_GATE_EFFECT = NONE
INTEGRATED_G1_G4_EFFECT = NONE
EOPT_G0_EFFECT = NONE
VALIDATION_CLOSURE = 0_PERCENT_UNDER_VALIDATOR_HOLD
NEW_PASS_OR_PASS_WITH_FINDING = NONE
```

Progress accounting recommendation: G3-B and G3-C may be marked `DONE_WITH_BLOCKER / OWNER_OR_GOVERNANCE_DECISION_REQUIRED` for **work-unit discovery/decision-packet EWU only**, but must receive zero gate-closure credit. PMO should decide whether Fast-Close EWU bookkeeping awards the bounded negative-result weight.

No claim is made for CA completeness, governed calendar, PIT eligibility/tradability, annotation, Price Canonical, G3 closure, integrated closure, EOPT effectiveness, Golden, Replay, Freeze, Promotion, Release, or Production.
