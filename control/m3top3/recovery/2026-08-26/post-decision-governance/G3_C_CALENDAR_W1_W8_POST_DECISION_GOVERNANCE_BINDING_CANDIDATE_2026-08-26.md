# G3 Axis C / calendar / W1–W8 post-decision governance binding candidate

```text
PROJECT = AAA / ASSET AGENT ASA
PERSONA_SCOPE = AAA-PMO-ORCHESTRATOR DELEGATED NON-VALIDATOR WORKER
WORK_UNIT = FC1-G3 / POST-DECISION GOVERNANCE BINDINGS
ISSUED_AT_KST = 2026-08-26T02:05:03+09:00
STATUS = RULE_BINDINGS_MATERIALIZED / SOURCE_DEPENDENCIES_OPEN
OWNER_DECISIONS = OD-G3-C-01 YES / OD-G3-CAL-01 YES / OD-G3-WIN-01 YES
AXIS_B_COMPUTE = NOT_RUN
VALIDATOR_OR_REVIEWER_USED = FALSE
GLOBAL_OR_FULL_VALIDATION = NOT_RUN
VALIDATION_LOOP = NOT_RUN
GIT_OR_ISSUE_MUTATION = NONE
GATE_EFFECT = NONE
VALIDATION_CLOSURE_DELTA = 0
```

## 1. Bounded result

The three approved Owner decisions now govern the **rule layer**:

1. Axis C uses the frozen KRX corporate-action taxonomy, exact-date matching,
   correction lineage, and zero-unresolved exhaustion semantics.
2. The normative calendar authority class is exact official KRX equity
   regular-session evidence, or an explicitly Owner-designated equivalent;
   observed price dates remain diagnostic only.
3. The exact W1–W8 candidate at SHA-256
   `96d63cc98a01b6332cf9486440e7f3fdaa0ec5a2d605f21bc14a4025b46e69fe`
   is ratified only as an outcome-exposed development/descriptive registry.

This artifact binds those meanings without pretending that the missing source
objects exist. It is not an Axis-C release, calendar release, outcome-free
window authority, validation receipt, or gate PASS.

## 2. Authority-state matrix after the Owner decisions

| Domain | Rule state now | Exact source/evidence state | Execution state | Release/admission state |
|---|---|---|---|---|
| Axis C corporate actions | `GOVERNED / FROZEN_BY_OD-G3-C-01` | Independent KRX CA bytes, export/query identity, and custodian receipt `MISSING` | `SOURCE_BLOCKED` | `NOT_ADMITTED` |
| Trading calendar | `GOVERNED / FROZEN_BY_OD-G3-CAL-01` | Exact normative KRX calendar bytes and authority receipt `MISSING` | `SOURCE_BLOCKED` | `NOT_ADMITTED` |
| W1–W8 registry | Exact 8-row identity `OWNER_RATIFIED_FOR_OUTCOME_EXPOSED_DEVELOPMENT_ONLY` | Outcome-free selection/binding evidence and upstream tuple provenance `NOT_PROVEN` | Development/descriptive use only | `NO_CLEAN_HOLDOUT / NO_OOS / NO_RELEASE` |

The decisions eliminate semantic ambiguity. They do not eliminate evidence
dependencies.

## 3. Exact governing anchors

| Anchor | SHA-256 | Scope used here |
|---|---|---|
| G3 minimal governed protocol MD | `6872cd98c78490fe226474b5c45c1ca13b2a20f1c5db45a08adeaa7099caed42` | Human-readable Axis C, calendar, and W1–W8 semantics |
| G3 minimal governed protocol JSON | `42c60cdafbc1b504a3113512c5a2ac9ad8e728a18e5173853fec3ad2ba923250` | Machine-readable rule definitions |
| FAST-CLOSE Owner decision packet MD | `a6fd50cd491025615edf31b6a3e539534c953b2aded1a5418cd5d50650215b1d` | Exact questions, recommended effects, and claim boundary |
| FAST-CLOSE Owner decision packet JSON | `3bb8667cbd43c79c1b99925ec339fd0598c8185a2488bf8b36c5625ac0a98f6d` | Machine-readable decision meanings |
| W1–W8 registry candidate | `96d63cc98a01b6332cf9486440e7f3fdaa0ec5a2d605f21bc14a4025b46e69fe`; 414 bytes | Exact tuple identity ratified for outcome-exposed development/descriptive use only |

Decision observation: after PMO presented the explicit four-line decision
request, the Owner instructed the PMO to proceed. The parent PMO supplied this
worker with `OD-G3-C-01`, `OD-G3-CAL-01`, and `OD-G3-WIN-01` as approved.
Durable Git/Issue recording of that runtime approval is PMO packaging work; its
absence from this worker directory does not authorize this worker to invent a
receipt or mutate Git.

## 4. Axis C governed binding

### 4.1 Frozen semantic contract

`OD-G3-C-01 = YES` freezes the following for the current exact-v1 route:

- Independent source role: `KRX_CA_EVENT_UNIVERSE`, not derived from current CA
  rows, Axis-A stock-count signals, Axis-B price signals, or the workbook.
- Effective-date scope: `2024-01-01` through `2026-08-14`.
- Security scope: union of codes in the three exact price components, with code
  continuity only when an explicit official old/new mapping exists.
- Primary match: security code plus exact official effective/basis date. Fuzzy
  date matching is prohibited.
- Corrections: the latest explicit non-cancelled record by the frozen
  publication cutoff supersedes the earlier record while preserving lineage.
- Adjustment factors: only explicit official factors or the already governed
  bonus-issue formula are usable; event type alone never authorizes adjustment.
- Exhaustion: 100% terminal source disposition and reconciliation, zero live
  duplicate identities, zero missing required fields, zero unresolved events,
  and exact manifest count/digest reconciliation.

Frozen in-scope taxonomy:

1. stock split;
2. reverse split or consolidation;
3. bonus or free issue;
4. capital reduction with unit or basis impact;
5. rights or ex-rights event with official basis-price impact;
6. merger or stock exchange with unit or basis impact;
7. spin-off or demerger with unit or basis impact;
8. other official KRX event explicitly carrying comparable-price or unit
   impact; and
9. correction, cancellation, or supersession of an in-scope event.

Observed but never auto-adjusted absent explicit comparable-price/unit evidence:
paid-in issuance, CB/BW conversion, merger issuance without unit/basis change,
name change, cash dividend, and listing/suspension status.

### 4.2 Still-missing exact input

The following must arrive together as one independently frozen source package:

- exact source bytes and SHA-256;
- source locator and query/export parameters;
- acquired-at time and frozen publication cutoff;
- effective-date and security scope;
- source row count;
- event IDs, issue/security identity, publication time, official effective or
  basis date, type, impact/factor fields, correction lineage, and evidence refs;
- custodian or authority receipt.

Current state is `NOT_FOUND / NOT_PROVIDED`. Therefore no Axis-C mechanical
reconciliation, exhaustion claim, completeness claim, or release admission is
authorized.

### 4.3 Exact resume trigger

```text
TRIGGER = EXACT_INDEPENDENT_KRX_CA_EVENT_UNIVERSE_BYTES_AND_CUSTODIAN_RECEIPT_ARRIVE
ACTION = HASH_AND_SCOPE_BIND_THEN_EXECUTE_ONLY_AXIS_C_NORMALIZATION_RECONCILIATION_AND_EXHAUSTION_CANDIDATE
FAIL_CLOSED_IF = BYTE_IDENTITY_SCOPE_PUBLICATION_CUTOFF_OR_RECEIPT_IS_MISSING_OR_MISMATCHED
DO_NOT = SUBSTITUTE_PRICE_SIGNALS_OR_RESCAN_UNRELATED_LANES
```

Conditional worker time after admissible input: P50 `1.0 h`, P90 `2.5 h`.
External source wait is unmeasurable and excluded.

## 5. Governed calendar binding

### 5.1 Frozen semantic contract

`OD-G3-CAL-01 = YES` freezes:

- normative source: exact official KRX equity regular-session calendar bytes,
  or an explicitly Owner-designated authority equivalent;
- scope: `2024-01-01` through at least `2026-08-14`, covering every market in
  the three exact price components;
- canonical grain: `market_id + trade_date`, unless the authority proves one
  common KRX equity calendar;
- a half-day is in scope only when the authority identifies an open regular
  equity session; an exceptional closure is excluded;
- price-date union is diagnostic only and can never self-certify calendar
  membership or authority; and
- a missing security price row on an official open date is a coverage or
  tradability issue, not evidence that the market was closed.

Once exact calendar evidence exists, the deterministic mechanics are:

```text
Snapshot = exact date from the separately governed W1-W8 registry
Entry = first governed trade date strictly after Snapshot
Holding dates = governed dates from Entry through window end inclusive
Exit = first governed trade date strictly after window end
```

### 5.2 Still-missing exact input

Required but absent: exact calendar bytes, SHA-256, source locator, acquisition
time, market/date/session scope, source row count, and authority receipt. The
638 observed price dates remain a diagnostic index only. No calendar release or
window/calendar reconciliation is admitted now.

### 5.3 Exact resume trigger

```text
TRIGGER = EXACT_NORMATIVE_KRX_EQUITY_REGULAR_SESSION_BYTES_AND_AUTHORITY_RECEIPT_ARRIVE
ACTION = HASH_AND_SCOPE_BIND_THEN_BUILD_ONLY_THE_GOVERNED_CALENDAR_AND_W1_W8_DATE_MECHANICS_RECONCILIATION_CANDIDATE
FAIL_CLOSED_IF = AUTHORITY_SCOPE_MARKET_SESSION_IDENTITY_OR_BYTE_DIGEST_IS_MISSING_OR_MISMATCHED
DO_NOT = PROMOTE_PRICE_DATES_OR_REBUILD_UNRELATED_PRICE_CA_ANNOTATION_LANES
```

Conditional worker time after admissible input: P50 `0.5 h`, P90 `1.0 h`.
External source wait is unmeasurable and excluded.

## 6. W1–W8 development-only authority binding

### 6.1 Exact ratified identity

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

Exact candidate identity: `414` bytes, SHA-256
`96d63cc98a01b6332cf9486440e7f3fdaa0ec5a2d605f21bc14a4025b46e69fe`.

### 6.2 Binding effect and hard boundary

The exact tuples are now governed only for **outcome-exposed development and
descriptive use**. Any artifact consuming them must carry at least:

```text
WINDOW_AUTHORITY_CLASS = OWNER_RATIFIED_OUTCOME_EXPOSED_DEVELOPMENT_ONLY
WINDOW_REGISTRY_SHA256 = 96d63cc98a01b6332cf9486440e7f3fdaa0ec5a2d605f21bc14a4025b46e69fe
CLEAN_HOLDOUT = FALSE
OOS = FALSE
RELEASE_ADMITTED = FALSE
OUTCOME_FREE_BINDING_EVIDENCE = NOT_PROVEN
UPSTREAM_TUPLE_PROVENANCE = OPEN
```

Calendar evidence may later prove membership and next-date mechanics. It cannot
prove why these eight windows were selected, that selection preceded outcome
observation, or that the windows are clean holdout/OOS.

### 6.3 Still-missing outcome-free evidence and resume trigger

An outcome-free authority binding requires independently time-stamped evidence
showing the selection rule and tuple commitment before the relevant outcomes
were available, or a newly governed future window registry committed before
outcomes. Exact upstream tuple provenance may close provenance but does not by
itself establish outcome-free status unless its timing and selection lineage do
so.

```text
TRIGGER = EXACT_PRE_OUTCOME_SELECTION_RULE_AND_COMMITMENT_EVIDENCE_OR_A_NEW_PROSPECTIVE_WINDOW_REGISTRY_ARRIVES
ACTION = BIND_ONLY_THE_EVIDENCED_WINDOW_AUTHORITY_CLASS_AND_PRESERVE_THE_DEVELOPMENT_REGISTRY_LINEAGE
FAIL_CLOSED_IF = TIMESTAMP_SELECTION_RULE_OR_TUPLE_IDENTITY_CANNOT_BE_PROVEN
DO_NOT = RETROACTIVELY_LABEL_THE_CURRENT_EIGHT_ROWS_CLEAN_HOLDOUT_OR_OOS
```

## 7. Resume routing and no-duplicate boundary

| Trigger observed | Resume only | Remains held |
|---|---|---|
| Exact KRX CA package + receipt | Axis-C source binding and bounded reconciliation candidate | Calendar, window outcome-free authority, validation |
| Exact KRX calendar package + receipt | Calendar source binding and W1–W8 date-mechanics candidate | Axis C, window selection authority, validation |
| Exact pre-outcome/future window evidence | Corresponding window authority binding only | Unrelated G3 lanes and validation |
| More than one exact input arrives | The affected lanes may run independently or in a bounded combined worker pass | Global/full suite and validation loop |

Before any resumed lane executes, compare the exact trigger artifact identity to
this binding and confirm no concurrent worker owns the same lane. A near match,
recreated artifact, or local concordance does not satisfy a trigger.

## 8. Validation and claim ceiling

- No validator, reviewer, global validation, full regression, or revalidation
  loop was used for this binding artifact.
- Owner decisions do not trigger validation.
- Source arrival triggers the affected bounded worker lane only, not validation.
- The existing validator HOLD remains intact.
- Sealed G4 evidence remains preserved within its exact original scope and is
  not rerun.

No claim is made for Axis-C source exhaustion or completeness, CA release,
governed calendar release, outcome-free W1–W8 authority, clean holdout/OOS,
Price Canonical, PIT eligibility/tradability, G3 or integrated G1–G4 PASS,
EOPT-G0, A/A, predictive power, Golden, Replay, Freeze, Champion, Promotion,
Release, Production, or optimization effectiveness.

```text
AXIS_C_RULES = GOVERNED
AXIS_C_RELEASE = SOURCE_BLOCKED / NOT_ADMITTED
CALENDAR_RULES = GOVERNED
CALENDAR_RELEASE = SOURCE_BLOCKED / NOT_ADMITTED
W1_W8_DEVELOPMENT_AUTHORITY = OWNER_RATIFIED_OUTCOME_EXPOSED_ONLY
W1_W8_OUTCOME_FREE_AUTHORITY = NOT_PROVEN
G3_GATE = OPEN / PARTIAL
INTEGRATED_G1_G4 = NOT_CLOSED
EOPT_G0 = OPEN / NOT_PROVEN / 1_OF_6_PASS
GATE_EFFECT = NONE
```

Machine-readable companion:
`G3_C_CALENDAR_W1_W8_POST_DECISION_GOVERNANCE_BINDING_CANDIDATE_2026-08-26.json`.
