# M3Top3 G1–G4 PMO Integrated Checkpoint v0.1

`CHECKPOINT_ID = M3TOP3-G1-G4-INTEGRATED-CHECKPOINT-20260823-01`

| Field | Current value |
|---|---|
| Program | `M3TOP3_P0_VALIDATION_REBASE` |
| Execution Commander | `AAA-PMO-ORCHESTRATOR` |
| Owner authority | `APPROVE_AND_CLOSE + PMO_DIRECT_DISPATCH=YES` |
| Owner action required now | **`FALSE`** |
| IVA execution participation | **`NONE`** |
| Model state | `S0_PRE_OUTCOME_BASELINE_CANDIDATE` |
| Model validity / predictive power | `NOT_ESTABLISHED / NOT_ESTABLISHED` |
| Official Golden / Full Replay | `BLOCKED / BLOCKED` |
| Freeze / Promotion / Release / Merge / Production | `BLOCKED` or `NOT_AUTHORIZED` |
| Updated | 2026-08-23 21:20 KST |

## 1. PMO conclusion

The program is not stopped. The first evidence-production cycle has completed five material milestones: exact v1.2 plan currentization, baseline-identity audit, Universe/exposure audit, data/annotation-readiness audit, and the v0.4 runtime-mechanism correction with internal engineering acceptance.

However, evidence production and formal gate closure are different. Under the exact v1.2 gate map, only G0 is presently satisfied with a finding. G1 and G2 remain actively in progress, G3 is dependency-blocked, and G4 has a mechanism-closed candidate but not every formal validation/audit receipt named by the controlling plan. G5–G9 remain blocked and have not been executed.

This checkpoint therefore authorizes continued bounded recovery and non-scoreable preparation only. It does not authorize model scoring, ranking, Top-K production, outcome performance, Official Golden, Full Replay, Failure Atlas, Challenger evaluation, or Prospective Shadow.

## 2. Exact governing baseline

| Artifact | SHA-256 | Result |
|---|---|---|
| `M3Top3_Owner_Governed_PMO_WORK_ULTRA_Execution_Masterplan_v1.2_2026-08-22.docx` | `819e2c12bd149129e5054350c355b9132842d44841e09a1da2dbd1050888c7dd` | Exact dispatch match |
| `M3Top3_Final_Review_Synthesis_and_Governed_Recommendation_v1.2_2026-08-22.docx` | `a7d87f07d5d442ac01b0fbaa9ebc2f5c6bbd52bf25d67b4ba319e66e86f9fdbc` | Exact dispatch match |
| Owner direct-dispatch packet | `16688e3cc089f9d60524b3ea6ff7f34fa6ad59c0aa66bfc7b1940c54914d82cf` | Execution authority current |
| G0 currentization receipt | `dcc34e29945f44a8e3943573acf23e9e82b0f387c90353b627610c9c4193d434` | G0 exact pair closed |

The controlling gate map is:

`G0 Bootstrap → G1 Exact Identity → G2 Universe/Eligibility/Window/Exposure → G3 Historical PIT/Data/Annotation → G4 Runtime → G5 Golden → G6 Replay → G7 Failure Atlas → G8 Challengers → G9 Prospective Shadow`.

The older v0.4 checkpoint's merged gate labels are `SUPERSEDED_FOR_GATE_MAPPING_ONLY`. The evidence is retained as runtime provenance but does not control this projection.

## 3. Gate state

| Gate | State | What is complete | What still blocks closure |
|---|---|---|---|
| G0 | `SATISFIED_WITH_FINDING` | Exact plan pair, Owner receipt, PMO dispatch boundary, IVA separation | PMOV/domain audit remains a separate surface and is not impersonated by PMO |
| G1 | `IN_PROGRESS` | Exact-evidence audit complete; exact-byte/source-custodian recovery continues | Official scorer/config/environment/oracle/release, timestamp, access/change chain, expected research ZIPs |
| G2 | `IN_PROGRESS` | U46/U127 currentized; U127/W1–W8 policy corrected; 32-cell deterministic eligibility process sample frozen | Membership genesis, authoritative release, 514-cell evidence decisions, clean historical holdout |
| G3 | `DEPENDENCY_BLOCKED` | 2025 bytes audited; W4×3 non-scoreable mechanical pilot completed with 3/3 fail-closed | 2024/2026 bytes, standalone manifest, CA/calendar/status, PIT/annotation lineage, F03/F04 vintage, exact feature contract |
| G4 | `IN_PROGRESS` | v0.4 diagnostic runtime mechanism and internal engineering-control evidence complete | Formal ENGV+CTLV validation and PMOV audit/claim review remain separate plan surfaces |
| G5 | `DEPENDENCY_BLOCKED` | No Official Golden executed | G1–G4 and independent release/oracle requirements |
| G6 | `DEPENDENCY_BLOCKED` | No Full Replay executed | G1–G5 |
| G7 | `DEPENDENCY_BLOCKED` | No Failure Atlas executed | G6 |
| G8 | `DEPENDENCY_BLOCKED` | No Challenger build/evaluation executed | G7 and preregistration |
| G9 | `DEPENDENCY_BLOCKED` | No Prospective Shadow executed | G8 and future cohort materialization |

### Progress interpretation

- Evidence milestones completed: **5**.
- Formally satisfied gates: **1 of 10** (`G0`, with finding).
- This is not a 10% time estimate. Substantial G1–G4 evidence has been produced, but the program deliberately does not convert audits or engineering tests into a release gate.
- The long elapsed time came from finding and correcting semantic/runtime issues before using historical outcome data. That prevented an invalid Official Replay from being mistaken for model evidence.

## 4. G1 — Baseline identity

### Decision

`ORIGINAL_V1_IDENTITY = UNPROVEN`

`S0 → S1 = NOT_ELIGIBLE`

The current evidence does not prove that the original v1 package is exact, outcome-blind, or continuously linked to later engineering. It also does not prove the opposite. Later working infrastructure and the test-only `DiagnosticFixtureScorer` cannot be promoted to original-v1 identity.

### Recovery currentization

A new bounded search covered the current `/workspace`, the named repository, the AofSpds organization code-search surface, and the prior recorded blob-readback paths. It found none of the two expected research ZIPs. This remains a bounded `NOT_FOUND`, not proof of global nonexistence or custodian unavailability.

Expected ZIPs:

| Artifact | Expected bytes | Expected SHA-256 | Current state |
|---|---:|---|---|
| v0.1 research ZIP | 35,775 | `3aaee7c1de2bd6f97e5ffd808fba980bf73fea1b604fb3c3b79e2be005180002` | `NOT_FOUND_ON_SEARCHED_SURFACES` |
| v0.2 research ZIP | 40,210 | `5bbe75a4c9966abcb9f10d2f1e84df983977c1cf76d69e7bda6dfe4f24e60836` | `NOT_FOUND_ON_SEARCHED_SURFACES` |

No exact byte may be recreated, normalized, rezipped, or semantically substituted and then called original v1.

## 5. G2 — Universe, eligibility and exposure

### Closed facts

- U46 is exactly enumerated as 46 records across the three current registers.
- U127 working membership is 127 unique rows: U46=46 and U81=81.
- U127 row-level outcome-blind selection provenance is 0/127.
- Exact v1.2 keeps U127 as the **current-phase working/canonical validation universe**, with membership stable during this phase to prevent denominator drift.
- U127 membership-genesis outcome-conditioning remains an audit item. The evidence proves neither outcome-blind selection nor intentional winner-driven selection.
- Therefore U127 must not be automatically relabeled as either a Challenge Universe or a Population Universe. Unbiased-population and generalized-discovery claims remain prohibited.
- W1–W8 may be used for the exact pre-outcome v1's first honest historical evaluation after G1–G5 close. They are not a clean holdout or OOS-superiority surface.
- After the first replay and Failure Atlas expose results, W1–W8 may be used for Challengers only as an `EXPOSED HISTORICAL DEVELOPMENT / DIAGNOSTIC / COMPARATIVE SET`.
- No other clean historical holdout was found; successor true OOS defaults to prospective-only evidence.

The prior Lane B/Data-audit statements that automatically classified U127 as `Challenge-only` and W1–W8 as `development-only` are superseded on this policy point by the Owner-approved exact v1.2 plan. Their underlying enumeration, exposure and missing-provenance facts remain valid.

### Open release work

- An outcome-blind Population Universe is not proven.
- No authoritative U127 applicability/release manifest is available.
- Entity-resolution readiness is 5/127; identity remains partial for 127/127.
- Combined historical eligibility is 465 eligible, 37 ineligible, and **514 unresolved** across eight windows.

A deterministic 32-cell procedure-validation sample has now been frozen without any winner, rank, return or later-success field. It contains eight cells per S1–S4 stratum and four per window; 램테크놀러지 (`171010`) provides the W1–W8 longitudinal stratum. 삼양엔씨켐 W4 is preserved outside the sample as a fixed negative control. This is a workflow sample only: eligibility investigation and state changes remain zero.

## 6. G3 — Data and annotation

### Reproduced 2025 facts

| Metric | Result |
|---|---:|
| Rows / distinct codes / distinct dates | 696,524 / 2,985 / 242 |
| Date range | 2025-01-02–2025-12-30 |
| Duplicate `(Date, Code)` | 0 |
| U127 present | 125/127 |
| U127 with all 242 dates | 120 |
| Zero Open=High=Low, all market / U127 | 31,692 / 29 |

The exact 2025 bytes are only a raw-component candidate. The raw 18-column file lacks eight governed fields from the 20-column reference, including corporate-action, adjustment, trading-status, provider and eligibility fields.

### Blocking facts

- Exact 2024 and 2026 Parquet bytes are not found.
- The standalone three-component interface manifest is not found; the supplied legacy CSV is a different artifact.
- CA completeness axes B/C, independent calendar release, Trading Status and zero-OHL treatment remain open.
- Thin PIT is complete for **0/1,016** rows; timezone-aware `publication_at` is 0/1,016.
- Hashed source bundles, access sidecars, independent dual coding, pre-adjudication outputs and LLM/annotator lineage are absent.
- F03/F04 have no auditable historical-vintage consensus source.
- Exact executable F01–F09 identity is not recovered.

Only a W4×3 non-scoreable data-assembly pilot may be prepared/executed under a separate fail-closed packet. It must produce no score, rank, Top-K, return, Golden or Replay result.

That bounded mechanical pilot has now run. All three companies have 64 raw rows from the cutoff through the last trading day and all three named boundary dates. 케이씨텍 and 삼양엔씨켐 have no zero-OHL row in the interval; 미래산업 has 17. Because source bundles, publication timing, access/concealment lineage and governed CA/Trading Status fields remain absent—and 삼양엔씨켐 remains eligibility-unresolved—all three admissions correctly ended `FAIL_CLOSED`. No score, rank, return or outcome field was produced.

## 7. G4 — Runtime

`R-WP4-03_DIAGNOSTIC_RUNTIME_MECHANISM = CLOSED_AT_V0.4_CANDIDATE`

| Evidence | Result |
|---|---:|
| Frozen candidate | 31/31; source-tree SHA-256 `37b10c54baee9aba7f33f1b59d524e0a24e4e1e1561483a030527a2bff566c73` |
| Runtime parent / evidence parent | `ea52bde2ed65c46f3e797f640b60dd9741aa8fe1` / `3d75dab93d31b20f2f4d42de38cbc6aae96a6ccd` |
| Implementation / evidence commits | `6bea55409588209529dc4c94d03694875a2c7c69` / `1d6822736d97f8ddc76ae03e43d7cd594294b086` |
| Compile / unit-regression | 28/28 / 261/261 PASS |
| SEM-001 / negative matrix | 10/10 / 75/75 PASS |
| Mutation / concurrency | 57/57 killed-red / 400/400 PASS |
| Internal acceptance | `PASS_INTERNAL_ENGINEERING_CONTROL` |

The correction restores governed legacy Top3 meaning while storing full eligible-universe outcomes separately. It closes the diagnostic mechanism at the candidate implementation SHA. It does not validate the model or data. Because the exact plan names ENG+CTL execution, ENGV+CTLV validation and PMOV audit of the PMO claim, this PMO checkpoint does not relabel the internal acceptance receipt as complete formal G4 closure.

Two lineage findings remain open without invalidating the current candidate: the freeze manifest's `accepted_runtime_commit=ea52...` is a validated parent, not the v0.4 implementation commit `6bea...`; and the preserved mutation-v1 failed receipt points to a historical harness hash no longer materialized at the same path. The mutation-v2 current PASS receipt matches the current harness. Original receipts remain immutable and are not rewritten.

## 8. Next bounded execution

PMO will continue without a new Owner decision through the following packet:

1. Exact source-custodian recovery for the two baseline ZIPs, bound to expected path, byte size and SHA-256.
2. Exact recovery for `marcap-2024.parquet`, `marcap-2026.parquet` and the standalone component manifest.
3. Route the frozen 32-cell eligibility sample to a separately governed, outcome-blind evidence-recovery procedure; no eligibility change is yet authorized by the sample receipt.
4. Build source-bundle, publication-time, concealment and access-sidecar templates before any W4×3 re-admission attempt.
5. Route the prepared formal G4 request on the immutable v0.4 candidate to ENGV and CTLV, with a separate PMOV claim audit; IVA remains outside execution.

### Owner trigger only when reached

- A custodian confirms exact baseline bytes are unavailable or bytes mismatch.
- New paid provider, contract, account or credential authority is needed.
- A historical-vintage consensus provider and budget must be selected.
- Blinded dual-annotation resources are requested after pilot controls are demonstrated.
- Universe/holdout/prospective boundaries or any model semantics would change.
- S0 transition, Golden, Replay, Freeze, Promotion, Release, Merge or Production is proposed.

Until one of those triggers is reached, `OWNER_ACTION_REQUIRED=FALSE` and PMO continues within the approved bounded scope.

## 9. Evidence anchors

| Evidence | SHA-256 |
|---|---|
| Baseline identity audit | `685bcb34b5da889425bcb6a623e78be5a36dd4beb10aa6dfb714a25f3df8f14b` |
| Baseline identity matrix | `528d0abd41991abbbe377508c6305f73368eb588193c90746ae3c029493709d0` |
| Universe/exposure audit | `fa25ff019572981948d823595da6d1b89ade1c3a86e3a32984f995d7b546a328` |
| Universe/exposure matrix | `90104878d4bf6da92bc13f67180c3461c6fff71688f08b9c1b0b349238c1e51b` |
| Data/annotation audit | `f948a7c8beab1d55f24146815c69b91f5a9e5b28118171c5311c00ab2016743a` |
| Data/annotation matrix | `7ad599f41313c8148cf205b6b80d71885b33b69414fdb32bff10490ec32821dc` |
| 2025 audit receipt | `093a326b27453cb389fb206d73db8a577c7754672fa6c1ab81568f6bce6e4ac5` |
| v0.4 runtime checkpoint | `08c6de4bf24ab1a3547b06e76c1435fb43b2acb4600460526c3b896e357eac55` |
| v0.4 internal validation receipt | `c814ad850d4602f1884fcdfe30e7c0d528206306107af4f009e2174dcc056d11` |
| Source-custody recovery probe | `01883efe8b347d24ca4d52dc39be15ec7abec9771f2a6f1b619392c5ab73e8fc` |
| U127/W1–W8 policy disposition | `6e80363bd8446fa7a42b54f03a668b214a14547e6a87aef981b8c42f2293d647` |
| Eligibility process sample CSV / JSON | `bd1dcef5e446591b25ee902c46e010618a3aef30f9ca58865ab01daceb89715b` / `02f6da31f4b608a6c2f41d7d6dc93faed55b23f54e14c31857458cb1751a662a` |
| Eligibility process sample receipt | `5e56fd23c5d9b6d6776e0604380fa0327ef407d4c53551980e9b5f48efbba7fd` |
| W4×3 pilot contract / mechanical receipt | `17b9736e335f786142e2a08eaa43ee37939842f45c48288e059e57d3f4ee2587` / `86ddbaba9ee05d949671c02afccd830c0abc7f589ef23e973192f3dc99f2e663` |
| W4×3 pilot human receipt | `302caad469d48b2905675d3f05d561dd9cdd12a3a373f45045fd1c5e4f1bcf1d` |
| G4 formal validation request | `9afb57f21166beadf21d0ce22d285e1033659322a2d483454f437b2682e9a097` |

The machine-readable controlling projection is `M3TOP3_G1_G4_MASTER_STATUS_v0.1.json`.
