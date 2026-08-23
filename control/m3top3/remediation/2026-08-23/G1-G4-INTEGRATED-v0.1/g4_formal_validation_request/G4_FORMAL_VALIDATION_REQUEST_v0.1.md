# M3Top3 G4 Formal Validation Request v0.1

`REQUEST_ID = M3TOP3-G4-FORMAL-VALIDATION-REQUEST-20260823-01`

| Field | Value |
|---|---|
| Requestor | `AAA-PMO-ORCHESTRATOR` |
| Exact gate | G4 — Fail-Closed Runtime / Determinism / Immutable Lineage |
| Gate state at request | `IN_PROGRESS` |
| Execution relation | ENG + CTL |
| Required validation relation | ENGV + CTLV |
| PMO-claim audit | PMOV, separately |
| IVA participation | `NONE` |
| Owner action | `NONE` |

## Exact target

- Candidate: `r_wp4_03_final_candidate_v0_4`
- Candidate version: `v0.4`
- Candidate files: 31
- Source-tree SHA-256: `37b10c54baee9aba7f33f1b59d524e0a24e4e1e1561483a030527a2bff566c73`
- Validated runtime parent: `ea52bde2ed65c46f3e797f640b60dd9741aa8fe1`
- Evidence parent: `3d75dab93d31b20f2f4d42de38cbc6aae96a6ccd`
- Implementation commit: `6bea55409588209529dc4c94d03694875a2c7c69`
- Evidence commit/head: `1d6822736d97f8ddc76ae03e43d7cd594294b086`
- Internal engineering-control receipt SHA-256: `c814ad850d4602f1884fcdfe30e7c0d528206306107af4f009e2174dcc056d11`

## Existing candidate evidence

| Check | Result |
|---|---:|
| Compile | 28/28 PASS |
| Unit/regression | 261/261 PASS |
| SEM-001 | 10/10 PASS |
| Production negative matrix | 75/75 PASS |
| Mutation | 57/57 killed-red; survivor/error/timeout/skip 0 |
| Concurrency | 400/400 PASS; raw exception 0 |
| Remote implementation delta | 7/7 blobs exact |

## ENGV exact questions

1. Do the 31 candidate bytes match the manifest and implementation commit?
2. Are blocker paths fail-closed with non-zero failure semantics where required?
3. Are immutable publication, append-only lineage, content-hash binding and manifest-last concurrency enforced?
4. Do tests and mutation evidence independently reproduce without using model-performance or historical-outcome claims?
5. Does the current v2 mutation PASS receipt bind the current harness exactly?

Required output: exact-target ENGV receipt with independent command log, environment identity, byte hashes, PASS/FAIL/FINDING per requirement, and no code mutation.

## CTLV exact questions

1. Does v0.4 preserve the governed legacy meaning of `outcomes`, `outcome_count` and `metrics` as selected Top3?
2. Are full eligible-universe outcomes and diagnostics stored separately without changing the legacy view?
3. Does cross-view/result-version drift fail closed?
4. Are `PARTIAL`, unresolved eligibility, absent publication time and non-admitted data prevented from becoming scoreable official inputs?
5. Does the candidate avoid claiming original-v1 identity, model validity, predictive power, Price Canonical, Golden or Replay readiness?

Required output: exact-target CTLV semantic-preservation receipt with independent expected results and no authoring/mutation.

## PMOV audit questions

1. Did PMO keep the formal G4 Gate `IN_PROGRESS` pending the paired receipts?
2. Did PMO distinguish mechanism evidence from model/data validity?
3. Were the prior v0.3 SEM-001 disposition and all open findings preserved without retroactive rewrite?
4. Did PMO keep IVA outside execution and avoid reserved Owner decisions?

Required output: separate PMOV audit of the PMO claim and decision trace. PMOV does not replace ENGV or CTLV.

## Preserved findings

- `G4-QC-01`: the freeze manifest field `accepted_runtime_commit=ea52...` names the validated parent; the v0.4 implementation commit is `6bea...`. No byte mismatch is asserted.
- `G4-QC-02`: the preserved failed mutation-v1 receipt records harness SHA `43ae...`, while the current same-path harness is `374fe...`; current mutation-v2 PASS is internally consistent. The predecessor receipt is not rewritten.

## Claim ceiling and closure rule

No requested receipt may claim model validity, predictive power, alpha, Price Canonical, Official Golden, Full Replay, Freeze, Promotion, Release, Merge or Production authority.

G4 may move from `IN_PROGRESS` only after exact-target ENGV and CTLV receipts and a PMOV audit of the PMO gate claim are available and reconciled. IVA is not an automatic G4 validator and does not participate in this work packet.
