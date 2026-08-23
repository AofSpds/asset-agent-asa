# M3Top3 G1 Lane B — Universe Provenance & Historical Outcome-Exposure Audit

```text
AUDIT_ID = M3TOP3-G1-LANE-B-UNIVERSE-EXPOSURE-v0.1
AUDIT_ROLE = INTERNAL_PMO_EVIDENCE_AUDIT
AUDIT_MODE = READ_ONLY
OBSERVED_AT = 2026-08-23T20:45:05+09:00
IVA_PARTICIPATION = NONE
RUNTIME_OR_GIT_MUTATION = NONE
OFFICIAL_GOLDEN_REPLAY_EXECUTION = NONE
```

## 1. Executive verdict

| Question | Status | Determination |
|---|---|---|
| Is the registered U46 list identifiable? | `PROVEN` | `Semi_Universe_v1.0` enumerates 46 ACTIVE members: legacy TOP38 + eight additions dated 2026-08-14. The same 46 names and KRX codes appear in the same order in `SEMI-COMPANY-MASTER_v0.1` and `SEMI-SOURCE-INDEX_v1.0`. |
| Is U46 an outcome-blind Population Universe? | `UNPROVEN` | The documents do not provide the full candidate population, rejected candidates, selection timestamps, selector identity, or outcome-concealment/access receipt. |
| Is the U127 working membership identifiable? | `PROVEN` | The current working projection contains 127 unique rows: U46=46 and U81=81. All 127 have a working `company_id` binding; all 127 remain `identity_status=PARTIAL`, and only 5/127 have `entity_resolution_status=READY`. |
| Is there an authoritative U127 release/applicability manifest? | `NOT_FOUND` | No externally supplied applicability manifest, immutable U127 release receipt, authoritative membership digest, or complete authority/mapping package was located. Existing digests are explicitly non-authoritative projections from the working gap CSV. |
| Is U127 proven outcome-blind at selection? | `UNPROVEN` | Row-level outcome-blind inclusion provenance is 0/127. Selection rule, candidate population, rejection ledger, selection time, and concealment are absent. |
| Is U127 proven to have been selected because of winners? | `UNPROVEN` | The genesis/access ledger needed to establish the historical selection mechanism is absent. The audit does not infer selector intent. |
| What is U127's admissible role now? | `PROVEN` | The current artifact is outcome-exposed and is admissible only as an `OUTCOME_EXPOSED / WINNER_ENRICHED_CHALLENGE_UNIVERSE` for development, descriptive analysis, and stress testing. This is a conservative governance classification, not proof that every member was selected because it later won. |
| Is U127 established as an unbiased Population Universe? | `UNPROVEN` | Selection genesis and outcome-blind provenance are absent. Because the current artifact is outcome-exposed, the unbiased-population claim is `NOT_ADMISSIBLE` on current evidence; this does not prove that historical selection was biased. |
| Are W1–W8 exactly enumerable? | `PROVEN` | Cutoff, period, entry, last trading day, working eligible count, winner, and MFE are present for all eight windows. |
| Is any W1–W8 window a proven sealed holdout? | `CONTRADICTED` | The current workbook exposes outcomes for all eight windows, while person/model access ledgers and a sealed-holdout receipt are absent. |
| Is any clean historical holdout otherwise proven? | `NOT_FOUND` | No independent pre-exposure seal, custodian receipt, access history, or unexposed historical window registry was located. |

**Overall Lane B disposition:** `PARTIAL_EVIDENCE_CLOSED / POPULATION_UNIVERSE_BLOCKED / U127_CHALLENGE_ONLY / W1_W8_DEVELOPMENT_OR_DESCRIPTIVE_ONLY / CLEAN_HOLDOUT_NOT_PROVEN`.

## 2. Status semantics

- `PROVEN`: direct positive evidence is present in a byte-identified artifact and was cross-checked where possible.
- `CONTRADICTED`: the claim conflicts with present direct evidence.
- `UNPROVEN`: evidence required to establish the claim is absent or incomplete; the opposite is not inferred merely from absence.
- `NOT_FOUND`: the specified artifact, receipt, ledger, or record was not located on the inspected surface.

Evidence status and use admissibility are separate. An `UNPROVEN` Population claim is fail-closed as `NOT_ADMISSIBLE`; that control does not convert the unproven claim into a contradicted historical fact.

## 3. Authority and scope boundary

The Owner approval receipt authorizes bounded WP2 investigation of “U127 current release/provenance; denominator_T; W1–W8 dates; outcome access ledger; sealed holdout determination” with `OWNER_ACTION_REQUIRED=FALSE`. It does not authorize a false Population/holdout claim, model-state advancement, Official Golden, Official Replay, promotion, release, or production.

The PMO workplan requires an eventual `Universe/Eligibility/Exposure Release` containing the U127 release, deterministic denominator_T, W1–W8 specification, and exposure manifest. This audit is evidence classification only; it is not that release and does not close G2.

IVA is an external independent validation institution and did not participate in this audit, evidence production, work lane, or decision.

## 4. Population Universe — separate plane

### 4.1 What is proven

- `Semi_Universe_v1.0` is an ACTIVE Source Registration dated 2026-08-14 with `CURRENT_COUNT=46`.
- Its 46 rows are all `ACTIVE`: 38 legacy TOP38 members plus eight additions.
- It defines a historical eligibility rule: at each snapshot, a company must have been listed, tradable, and within the semiconductor equipment/materials business scope.
- U46 cross-registration is exact at the available document level:
  - `Semi_Universe_v1.0`: 46 names;
  - `SEMI-COMPANY-MASTER_v0.1`: 46 names, KRX codes, and `KRX:<code>` company IDs;
  - `SEMI-SOURCE-INDEX_v1.0`: the same 46 names and KRX codes in the same order;
  - name-set, order, and code comparison: 46/46 match; missing=0; extra=0; code differences=0.
- `SEMI-COMPANY-MASTER_v0.1` explicitly limits itself to `Universe Source = SEMI-UNIVERSE v1.0 / CURRENT_COUNT=46`; it seeds structural F1 fields but leaves DART IDs and listing dates unverified/not found.
- `SEMI-FAB-MASTER_v1.0` is a customer fab/CAPEX context ledger. It provides no candidate-population generation rule or U127 membership mapping.

### 4.2 What is not closed

No inspected source establishes an outcome-blind Population Universe release. Specifically absent are:

- a taxonomy-generated candidate population available at each selection time;
- inclusion and rejection rules applied symmetrically;
- rejected-candidate ledger;
- selector and selection timestamps;
- outcome/winner concealment receipt;
- human/LLM access history;
- exact external applicability manifest and authority receipt;
- immutable Population Universe membership bytes and authoritative set digest.

Accordingly, neither U46 nor U127 may be promoted from a registered/working candidate list to an unbiased Population Universe on current evidence.

## 5. Challenge Universe — U127 plane

### 5.1 Exact working enumeration

The working artifact `U127_Data_Expansion_Working_v0.8_2026-08-15.xlsx` is byte-identified by SHA-256 `44501584c9dc6224637e9193219c1e8c87507af77dc15dc3944a3d04af524cda` and self-classifies as `PRE_RESEARCH_SNAPSHOT / HISTORICAL_STATUS_ONLY / DO_NOT_USE_AS_CURRENT_AUTHORITY=TRUE`.

The OOXML package has no `docProps/core.xml`; its filename date and ZIP member timestamps are therefore not accepted as an origin or selection timestamp. The 17 sheets contain zero formulas and zero external links, which describes the current materialized bytes but does not reconstruct when or by whom the membership was selected.

The derived working membership gap file contains:

| Control | Exact result |
|---|---:|
| Membership rows | 127 |
| U46 group | 46 |
| U81 group | 81 |
| Unique canonical names | 127 |
| Unique KRX codes | 127 |
| Unique working company IDs | 127 |
| `company_id_binding_status=READY` | 127 |
| `identity_status=READY` | 0 |
| `identity_status=PARTIAL` | 127 |
| `entity_resolution_status=READY` | 5 |
| Row-level outcome-blind provenance proven | 0 |
| `authoritative_freeze_status=FREEZE_CANDIDATE` | 127 |

The present projection digests are useful only to identify the current working rows:

- U127 count/digest: `127 / d5ec26474d53c45079bf7dd3f36d2be17e057dee85fb763c49f57e922bc43321`
- U46 count/digest: `46 / 6a6ca96b99449f44347508b8a637bde9f813f1a6210324d19657a3c4e9251a60`
- U81 count/digest: `81 / 2ca7bee5d529dbba78a090607497d86b7a8005b69b7aa3018b927a5e2be85ebc`

These are explicitly documented as independent projections from the 127-row gap CSV, not externally supplied applicability-manifest digests and not release authority.

### 5.2 Outcome exposure and classification

The same U127 workbook contains:

- `Baseline_Windows!F2:I9`: winners, winner MFE, Top10 cut, and Top20 cut;
- `Price_Full_Rank_Reval!A2:Q980`: 979 outcome-ranked company-window rows;
- `Price_Reval_Summary!A2:I9`: outcome summaries;
- `Baseline_Registry!A2:D6`: preliminary historical baseline references;
- `Coverage_Matrix` fields that record Top10/Top20 appearances.

This proves artifact-level outcome exposure. It does not prove who accessed the outcomes or whether outcome knowledge caused each membership inclusion. Therefore:

- `U127 outcome-blind at selection` = `UNPROVEN`;
- `U127 selected because of known winners` = `UNPROVEN`;
- `U127 current artifact outcome-exposed` = `PROVEN`;
- `U127 as unbiased Population Universe` = `UNPROVEN`;
- `unbiased Population Universe use on current evidence` = `NOT_ADMISSIBLE`;
- admissible current class = `OUTCOME_EXPOSED / WINNER_ENRICHED_CHALLENGE_UNIVERSE` only.

### 5.3 Authority/manifest/mapping state

| Object | Status | Exact state |
|---|---|---|
| U46 registered list | `PROVEN` | 46-row Source Registration plus exact cross-registration in Company Master and Source Index. |
| U127 working row mapping | `PROVEN` | 127 unique working rows with company name/code/company_id; identity remains partial. |
| U127 authoritative release manifest | `NOT_FOUND` | No immutable external applicability manifest or release receipt. |
| U127 authoritative set digest | `NOT_FOUND` | Only a non-authoritative projection digest is present. |
| U127 row-level genesis/outcome-blind provenance | `UNPROVEN` | 0/127 proven; selector/rule/time/rejections/concealment absent. |
| Outcome-blind Population Universe release | `NOT_FOUND` | No separate population membership bytes, manifest, or receipt. |
| Full historical U/E/I/UNRESOLVED denominator release | `NOT_FOUND` | 514/1,016 combined eligibility cells remain unresolved; exact eligible/ineligible full partitions are not materialized. |

## 6. W1–W8 exact registry and exposure

| Window | Snapshot cutoff | Period | Entry | Last trading day | Working eligible N | Outcome exposed in workbook |
|---|---|---|---|---|---:|---|
| W1 | 2024-08-09 | 2024-08-10 to 2024-11-10 | 2024-08-12 | 2024-11-08 | 119 | 로체시스템즈 / MFE 74.22% |
| W2 | 2024-11-08 | 2024-11-10 to 2025-02-10 | 2024-11-11 | 2025-02-10 | 120 | 와이씨켐 / MFE 99.80% |
| W3 | 2025-02-10 | 2025-02-10 to 2025-05-10 | 2025-02-11 | 2025-05-09 | 121 | 마이크로컨텍솔 / MFE 103.28% |
| W4 | 2025-05-09 | 2025-05-10 to 2025-08-10 | 2025-05-12 | 2025-08-08 | 124 | 마이크로컨텍솔 / MFE 116.95% |
| W5 | 2025-08-08 | 2025-08-10 to 2025-11-10 | 2025-08-11 | 2025-11-10 | 124 | 원익홀딩스 / MFE 418.35% |
| W6 | 2025-11-10 | 2025-11-10 to 2026-02-10 | 2025-11-11 | 2026-02-10 | 124 | 코리아써키트 / MFE 239.15% |
| W7 | 2026-02-10 | 2026-02-10 to 2026-05-10 | 2026-02-11 | 2026-05-08 | 125 | 코스텍시스 / MFE 293.29% |
| W8 | 2026-05-08 | 2026-05-10 to 2026-08-10 | 2026-05-11 | 2026-08-10 | 122 | 미래산업 / MFE 270.37% |

For all eight windows:

- artifact outcome exposure = `EXPOSED_IN_CURRENT_WORKBOOK` (`PROVEN`);
- historical person access ledger = `ABSENT` (`NOT_FOUND`);
- historical model/LLM access ledger = `ABSENT` (`NOT_FOUND`);
- actual person/model identities and access times = `NOT_FOUND`;
- sealed-holdout receipt = `NOT_FOUND`;
- allowed evaluation role = `DEVELOPMENT_OR_DESCRIPTIVE_ONLY` (`PROVEN`);
- sealed-holdout claim = `CONTRADICTED`.

The audit does not guess which person or model saw an outcome. It records only that the artifact exposed the outcomes and that no access ledger was found.

## 7. Current remediation/Git-materialization check

The v0.4 runtime candidate's canonical freeze manifest binds 31 runtime files to accepted runtime commit `ea52bde2ed65c46f3e797f640b60dd9741aa8fe1` and source-tree SHA-256 `37b10c54baee9aba7f33f1b59d524e0a24e4e1e1561483a030527a2bff566c73`. That is a runtime identity, not a Universe release.

The candidate README explicitly states that the package does not promote U127 and that W1–W8 meanings are not hard-coded. Its example snapshot config remains diagnostic and non-executable as a real release: U127 JSONL/denominator/applicability paths are placeholders, the authority is `WORKING_FREEZE_CANDIDATE`, and manifest/release hashes and statuses are null. The example backtest config has `window_end_by_snapshot_date={}` and `window_protocol_version=UNRESOLVED_CONTROL`.

Therefore current runtime/Git materialization does not close U127 authority, W1–W8 release identity, or a clean holdout.

## 8. Clean-holdout disposition

```text
W1_W8_ROLE = DEVELOPMENT_OR_DESCRIPTIVE_ONLY
W1_W8_SEALED_HOLDOUT = CONTRADICTED
OTHER_HISTORICAL_SEALED_HOLDOUT = NOT_FOUND
CLEAN_HOLDOUT_AVAILABLE_NOW = NO_PROVEN_HOLDOUT
SUCCESSOR_TRUE_OOS_DEFAULT = PROSPECTIVE_ONLY
EXCEPTION = ONLY_IF_AN_INDEPENDENT_PREEXISTING_SEAL_AND_COMPLETE_ACCESS_HISTORY_ARE_LATER_PRODUCED_AND_VERIFIED
```

W1–W8 may be used only under their exposed development/descriptive role. They must not be renamed clean holdout after use in replay, failure analysis, or challenger development. A true successor OOS claim must begin with prospective shadow cohorts unless independent pre-existing sealed evidence is produced; Owner approval alone cannot manufacture missing exposure evidence.

## 9. G1 Lane B closure boundary

### Closed at evidence-classification level

- exact U46 46-row registration and 46/46 cross-registration across three source documents;
- exact U127 working enumeration: 127 = 46 + 81, with unique working identifiers;
- separation of working mapping from authoritative release authority;
- U127 current-artifact outcome exposure;
- exact W1–W8 dates, working eligible counts, winners, and MFE fields;
- absence of person/model access ledgers on the inspected surface;
- fail-closed role assignment: Population Universe blocked, U127 challenge-only, W1–W8 development/descriptive-only.

### Absolutely not closed

- an outcome-blind Population Universe;
- U127 selection genesis or row-level outcome-blind provenance;
- an independently evidenced U127 origin/selection timestamp (filename and ZIP timestamps are not provenance receipts);
- proof that U127 membership was or was not intentionally winner-driven;
- authoritative U127 applicability/release manifest, mapping receipt, or authority-bound digest;
- complete entity identity and corporate-history mapping for 127 companies;
- full historical denominator release (`514/1,016` combined eligibility cells remain unresolved);
- any human/LLM outcome-access history;
- any W1–W8 sealed-holdout claim;
- any alternative clean historical holdout;
- any prospective cohort already accrued.

## 10. Owner decision and PMO action

```text
OWNER_ACTION_REQUIRED_NOW = FALSE
OWNER_DECISION_NEEDED_NOW = NONE
BASIS = Existing Owner receipt expressly authorizes bounded WP2 and sets OWNER_ACTION_REQUIRED=FALSE; fail-closed classification is within approved scope.
PMO_ACTION = Preserve U127 as OUTCOME_EXPOSED/WINNER_ENRICHED_CHALLENGE_UNIVERSE; keep Population Universe BLOCKED; lock W1-W8 to DEVELOPMENT_OR_DESCRIPTIVE_ONLY; route true OOS to prospective evidence.
```

A new Owner decision is required only if a proposal seeks to override the approved evidence boundary, for example to use U127 as an unbiased Population Universe, call W1–W8 sealed/OOS, alter the product/evaluation scope, or waive the prospective-evidence requirement. Such a decision could authorize a changed plan but could not convert missing provenance or access history into proof.

## 11. Evidence register

| Evidence | SHA-256 | Role |
|---|---|---|
| Owner approval receipt | `9854813fc9a384e2314739cb6f58854599aefeaa8182cdc53defd0effe5ae205` | WP2 authorization; IVA none; Owner action false |
| Direct dispatch packet | `16688e3cc089f9d60524b3ea6ff7f34fa6ad59c0aa66bfc7b1940c54914d82cf` | execution authority boundary |
| PMO initial workplan | `94855875d1b4bca937be1dc0e4a6df2558bdddba32554bef060b407984e1df4b` | WP2/G2 requirements |
| Planning closure review | `f444cdea45c8d44c8bbbd70a178f2002935018935431dd5664c509aa883da45d` | planning/claim boundary |
| Semi_Universe v1.0 | `eef313bc71bd0a5cb019f92e43e1bf38c2a63633bb847320d1cb4c8fe4ea9023` | U46 registration and eligibility rule |
| SEMI-SOURCE-INDEX v1.0 | `2131ebe6724a8c2d235e7e6f06d4fdde2819ab460bd5c907e2f7ca32e02dac46` | U46 locator cross-register |
| SEMI-COMPANY-MASTER v0.1 | `03842717f3bb6815610541496b1f5dadfd44a0e277dc9364c5632cbfb5520cd6` | U46 structural seed and ID cross-register |
| SEMI-FAB-MASTER v1.0 | `528d1a59ac5b6796b95f70605675f273d80ef744da8d6460da60204d3cff4159` | contextual fab source; no Universe authority |
| U127 working workbook v0.8 | `44501584c9dc6224637e9193219c1e8c87507af77dc15dc3944a3d04af524cda` | primary working membership and exposed outcome artifact |
| U127 provenance-gap projection | `752138a1897cdacfcbb4762ac0caf5888007e49ac4605f88152576e544eeaa33` | 127-row working mapping and gaps |
| W1–W8 exposure-role manifest | `f346e1227cf3828bde82117af951027e4387bb729f779e227ae6cb07f481bbd7` | exact window/exposure classification |
| Current evidence inventory | `d41425d14c8846d3665d3d23016a456e70e1c25454eef7b78ecea720b0be00cd` | missing release/applicability evidence and projection digests |
| Admissibility matrix | `c792396220612a911a6810c5dba8eb03ac020a1d54920dbbe19d9c984cd6e9bb` | Population vs Challenge use boundary |
| v0.4 runtime freeze manifest | `e3a34016b8ca5c20582499716ddcdc807e8215e766d4f5fa6ec3eec40cd88636` | runtime candidate identity; not Universe authority |

## 12. Limitation

This is an internal PMO read-only evidence audit. It does not validate model performance, create an authority receipt, reconstruct missing historical access events, or authorize Official/Golden/Replay work. Findings remain subject to paired domain validation under the approved workplan; IVA participation remains `NONE`.
