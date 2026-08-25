# G3-E Annotation Local Recoverability and Ingest Candidate

```text
OBSERVED_AT_KST = 2026-08-26T01:25:20+09:00
EXECUTION_ROLE = FC1-G3 NON-VALIDATOR WORKER
VALIDATOR_HOLD = TRUE
GLOBAL_VALIDATION = FALSE
VALIDATION_LOOP = FALSE
SOURCE_MUTATION = NONE
GIT_OR_ISSUE_MUTATION = NONE
GATE_EFFECT = NONE
```

## 1. Decision

No G3-E annotation content value can be deterministically recovered from the
currently accessible local inputs.

What can be recovered mechanically is the complete fail-closed ingest
envelope: all 1,016 company-window keys, the exact 17-field registry, all
17,272 unfilled field slots, W1-W8 cutoff/entry joins, and the source-routing
and admission controls.  This is an executable authoring queue, not admitted
evidence and not a G3 closure candidate.

```text
THIN_PIT_ROWS = 1,016
ROW_KEYS_RECOVERABLE = 1,016 / 1,016
ANNOTATION_FIELDS = 17
QUEUE_SLOTS_RECOVERABLE = 17,272 / 17,272
ANNOTATION_CONTENT_VALUES_RECOVERABLE = 0 / 17,272
FEATURE_PUBLICATION_AT_RECOVERABLE = 0 / 1,016
FEATURE_SOURCE_EVIDENCE_REF_RECOVERABLE = 0 / 1,016
AVAILABLE_BEFORE_CUTOFF_DETERMINABLE = 0 / 17,272
ADMITTED_ANNOTATION_ROWS = 0 / 1,016
```

## 2. Exact 17-field source-to-field assessment

| Field block | Fields / slots | Governed source route | Local-state finding | Recoverable content |
|---|---:|---|---|---:|
| Valuation | 1 / 1,016 | KRX price + PIT earnings denominator; same-provider valuation series | Price exists, but no PIT denominator or valuation-vintage object | 0 |
| Earnings | 3 / 3,048 | DART/KIND, then official IR | No one-to-one historical filing bytes, period, source hash, and publication time | 0 |
| Forward expectations | 5 / 5,080 | One consistent consensus provider and historical vintage | Provider/vintage authority and retrieval receipt absent | 0 |
| Guidance | 1 / 1,016 | Filing and official IR | No cutoff-bound primary evidence bundle | 0 |
| PO / backlog | 2 / 2,032 | Filing and official IR | No contract/period source object or publication time | 0 |
| Qualification / repeat order / design win | 3 / 3,048 | Supplier/customer official sources; controlled corroboration | Static F1 context exists, but no company-window event evidence | 0 |
| Fab CAPEX state | 1 / 1,016 | Customer filing/IR and official newsroom | Current/derived fab reports postdate W1-W8 cutoffs and are not one-to-one supplier-window evidence | 0 |
| Material references | 1 / 1,016 | S1-S3 source bundle | No exact feature source object, hash, or one-to-one row binding | 0 |
| **Total** | **17 / 17,272** |  |  | **0** |

The exact fields are:

1. `valuation_observation_status`
2. `latest_revenue`
3. `latest_OP`
4. `latest_margin`
5. `Forward_EPS`
6. `Forward_OP`
7. `EPS_OP_revision`
8. `consensus_provider`
9. `observation_at`
10. `guidance`
11. `PO_order_status`
12. `backlog_status`
13. `qualification_status`
14. `volume_repeat_order_status`
15. `design_win_customer_adoption_status`
16. `fab_capex_state_status`
17. `latest_material_earnings_guidance_refs`

Every one of these 17 source worksheet cells is `NEEDS_RESEARCH` for every one
of the 1,016 rows.  The row-level evidence controls are likewise uniformly
fail-closed: `evidence_status=NOT_RESEARCHED`, `source_evidence_ref=NULL`,
`publication_at=NULL`, `last_verified_observed_at=NULL`, and
`freshness_staleness=UNKNOWN` for all 1,016 rows.

## 3. Local sources that look similar but cannot be substituted

The workbook contains publication metadata in other domains:

| Domain column | Non-null rows | Why it does not fill G3-E |
|---|---:|---|
| `Identity_Ledger.publication_at` | 53 | Identity evidence, not dynamic feature evidence |
| `U81_F1.publication_at` | 19 | Static/partial F1 context, not a company-window F2/F3 event |
| `Historical_BP.publication_at` | 481 | Denominator/business-priority evidence only |
| `Corporate_Actions.evidence_publication_at` | 11 | Corporate-action evidence only |

These 564 non-null cross-domain cells produce **zero** annotation recoveries.
Reassigning them would break source-to-field lineage.

In particular, the following shortcuts are prohibited:

- `Qualification Barrier` → `qualification_status`;
- `Fab Exposure` → `fab_capex_state_status`;
- `Customer Structure` → `design_win_customer_adoption_status`;
- price/market cap → valuation without the PIT earnings denominator;
- a 2026-08-09 through 2026-08-14 project report → a W1-W8 historical
  `publication_at`;
- `NEEDS_RESEARCH`/absence → zero, false, or a negative business fact.

The supplied price Parquet is useful only to the separate price domain.  The
current research documents and Semi schema documents supply route/control
semantics but do not supply the exact primary or authorized-provider historical
objects required by the 17 annotation fields.  The latest candidate snapshot
cutoff is W8 `2026-05-08`; the dated 2026-08 research artifacts therefore
cannot be used as historical backfill.

## 4. Executable fail-closed ingest candidate

The candidate consists of:

1. a 17-field registry with primary/secondary route, lineage, and admission
   rules;
2. a JSON Schema for the exact queue row;
3. 1,016 JSONL rows, one per unique `window_id|company_id`;
4. 17 fail-closed field slots per row;
5. an exact recoverability summary and input/output hash manifest.

Each field slot deliberately contains:

```json
{
  "source_sheet_state": "NEEDS_RESEARCH",
  "value": null,
  "collection_state": "NOT_COLLECTED",
  "local_recovery_state": "BLOCKED_EXTERNAL_HISTORICAL_RETRIEVAL_REQUIRED",
  "source_evidence_ref": null,
  "publication_at": null,
  "available_before_cutoff": null,
  "admission_state": "BLOCKED_NO_LOCAL_CUTOFF_SAFE_EVIDENCE"
}
```

The row envelope also preserves:

```text
SOURCE_BUNDLE_PLAN_STATE = UNFROZEN
ANNOTATION_SIDECAR_STATE = ABSENT
OUTCOME_ACCESS_FLAG = NULL
ROW_INGEST_STATE = QUEUE_ONLY_NOT_ADMITTED
```

No retrieval plan budget, stopping rule, source date, evidence locator,
annotation identity, or outcome-concealment state was invented.

## 5. Targeted mechanical checks

One single-pass, local mechanical check was run over this exact candidate.  It
was not a validator act, full regression, or validation loop.

```text
INPUT_HASH_BINDINGS = 5 exact source files matched
QUEUE_ROWS_PARSED = 1,016
UNIQUE_ROW_KEYS = 1,016
WINDOW_COUNTS = W1..W8 each 127
FIELD_SLOTS_PARSED = 17,272
COMPANY_ID_TO_KRX_CODE_BINDING = 1,016 / 1,016 exact
NON_NULL_ANNOTATION_VALUES = 0
INVENTED_PUBLICATION_AT = 0
```

## 6. Output hashes

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `G3_E_ANNOTATION_INGEST_FIELD_REGISTRY_v0.1.json` | 16,035 | `3ee7db8fe7ad265e9909821b608829d05c02edf88bfa8937d3c5f91f74278612` |
| `G3_E_ANNOTATION_INGEST_SCHEMA_v0.1.json` | 22,683 | `cea40640ba9258116d82ce957cf9f3cb1d3b6b79373f95cdcec1a5d72265e836` |
| `G3_E_ANNOTATION_INGEST_QUEUE_v0.1.jsonl` | 6,080,457 | `e5f9d9ff2a10bb47ab92826646b53c6754a84f4942c866cdd510a8828b338b7f` |
| `G3_E_LOCAL_RECOVERABILITY_SUMMARY_v0.1.json` | 10,247 | `69137aeccea4170e8a714e0dcf4dc0a6f755daa60d70e026dbfacc5156a0163f` |
| `build_g3_e_candidate.py` | 22,211 | `906c3bcc796bff32089bbedef5761a3b11cd3a14d4f0335c2ab43a4337975b71` |
| `targeted_qc_g3_e_candidate.py` | 3,443 | `1d1b4275935e1308d578e05b8e70fe1e409d446fd661278f309ceda5baea7ddd` |

## 7. EWU, gate effect, and remaining time

```text
EWU_RECOMMENDATION = +1 EWU within G3-E
BASIS = exact executable blocked schema/registry/queue produced
DO_NOT_AWARD = remaining annotation-content closure EWU
GATE_EFFECT = NONE
G3_E_STATUS = IN_PROGRESS / EXTERNAL_HISTORICAL_RETRIEVAL_BLOCKED
```

The remaining local worker-only step is candidate readback/binding into the
blocked G3-F lineage envelope:

```text
P50 = 0.25-0.50 h
P90 = 0.75-1.00 h
```

True annotation completion is not measurable from the current local inputs.
Even a non-governed floor of one minute per company-window is 16.9 active
hours before source custody, dual coding, disagreement adjudication, or
rework.  That floor is not an execution ETA and is not authorization to relax
the evidence contract.

## 8. Claim ceiling

- No new PASS or validation receipt.
- No G3 or integrated checkpoint closure.
- No historical annotation truth claim.
- No `publication_at`, source reference, or outcome-blindness claim.
- No current/post-cutoff backfill.
- No scorer, Golden, Replay, EOPT, promotion, release, or production claim.
