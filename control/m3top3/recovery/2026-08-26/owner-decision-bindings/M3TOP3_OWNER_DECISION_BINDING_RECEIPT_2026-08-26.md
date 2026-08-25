# M3Top3 Owner decision binding receipt

```text
PROJECT = AAA / ASSET AGENT ASA
PERSONA = AAA-PMO-ORCHESTRATOR (PMO)
RECEIPT_CLASS = NON_VALIDATOR / OWNER_SEMANTIC_DECISION_BINDING
CREATED_AT_KST = 2026-08-26T02:04:18+09:00
OWNER_REPLY_TIMESTAMP = NOT_INSTRUMENTED
DECISION_EFFECT = BOUND
VALIDATION_TRIGGERED = FALSE
SOURCE_EVIDENCE_CREATED = FALSE
GATE_EFFECT = NONE
PASS_EFFECT = NONE
```

## 1. Conversation-sequencing basis

1. The committed Owner decision packet presented exactly four recommended `YES`
   decisions and stated that the Owner could reply `4개 모두 YES`.
2. The PMO then repeated those four decision lines and requested their approval.
3. The Owner's immediately following message was `진행하세요.` and supplied no
   contrary value, qualification, or alternative decision.
4. Within that exact conversational scope, `진행하세요.` is bound as approval of
   all four immediately preceding recommended decisions. This receipt does not
   generalize the utterance beyond those four decision IDs.

```text
OD-G3-B-01 = YES
OD-G3-C-01 = YES
OD-G3-CAL-01 = YES
OD-G3-WIN-01 = YES
```

## 2. Exact bound semantics

| Decision | Exact bound semantics | Authorized next action |
|---|---|---|
| `OD-G3-B-01 = YES` | Current Open versus the immediately prior observed Close for the same instrument; absolute change `>=20%`, inclusive, exact and without rounding; signal-only, with no CA or adjustment inference | Run only the bounded Axis-B candidate scan over 1,822,019 rows |
| `OD-G3-C-01 = YES` | `LISTED_KRX_CA_TAXONOMY_EXACT_DATE_MATCH_CORRECTION_LINEAGE_ZERO_UNRESOLVED_EXHAUSTION` | Freeze the protocol; wait for exact independent KRX CA bytes, then run only Axis-C reconciliation |
| `OD-G3-CAL-01 = YES` | `EXACT_OFFICIAL_KRX_EQUITY_REGULAR_SESSION_ARTIFACT_OR_EXPLICIT_EQUIVALENT_IS_NORMATIVE_PRICE_DATE_UNION_DIAGNOSTIC_ONLY` | Wait for exact calendar bytes, then run only calendar/window reconciliation |
| `OD-G3-WIN-01 = YES` | Ratify the eight-row candidate with SHA-256 `96d63cc98a01b6332cf9486440e7f3fdaa0ec5a2d605f21bc14a4025b46e69fe` as an outcome-exposed development registry only, and authorize a separate authority-binding candidate | Materialize the Owner-authority binding candidate only; do not create retroactive clean-holdout, OOS, or window-release status |

`OD-MAJOR-REBASE-01` remains `NO`; it was not part of the approval request.

## 3. Claim and execution ceiling

- The four decisions bind rules only. They create no missing source bytes,
  historical facts, annotations, custodian evidence, validation receipt, or gate
  evidence.
- They do not satisfy G1, G2, G3, the integrated G1-G4 checkpoint, or EOPT-G0.
- They create no PASS, A/A, predictive-power, Golden, Replay, Freeze, Champion,
  Promotion, Release, Production, or optimization-effectiveness claim.
- Sealed G4 evidence remains preserved only in its original scope.
- Validator hold remains active. No validator, global/full validation, regression,
  revalidation loop, or automatic retry is authorized by this receipt.
- Axis-C and calendar execution remain source-blocked. Source arrival authorizes
  only the affected exact lane; it does not authorize a full-suite rerun.
- G3-E's existing fail-closed queue is reused; this receipt supplies none of its
  17,272 missing historical annotation values.

## 4. Integrity anchors

```text
PARENT_PACKET_MD_SHA256 = a6fd50cd491025615edf31b6a3e539534c953b2aded1a5418cd5d50650215b1d
PARENT_PACKET_JSON_SHA256 = 3bb8667cbd43c79c1b99925ec339fd0598c8185a2488bf8b36c5625ac0a98f6d
CANONICAL_DECISION_SET_SHA256 = 79ca7f7723a11dad407b777b49719b7ebaf529d4c1fdd174ca4507cefb1ffe2d
CONVERSATION_BASIS_SHA256 = e102bc2e8aba191567b693593c2ac6586fcf82cb1caa069482cad7f26ed150f3
```

The canonical decision-set hash is calculated from the following UTF-8 text with
a final newline:

```text
OD-G3-B-01=YES
OD-G3-C-01=YES
OD-G3-CAL-01=YES
OD-G3-WIN-01=YES
```

