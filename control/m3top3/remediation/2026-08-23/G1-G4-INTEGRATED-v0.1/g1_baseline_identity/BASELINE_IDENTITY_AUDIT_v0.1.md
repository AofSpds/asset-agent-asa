# M3Top3 v1 Baseline Identity / Provenance Audit v0.1

| Field | Value |
|---|---|
| Audit lane | PMO G1 Lane A — Baseline Identity |
| Audit mode | Read-only, exact-evidence review |
| Generated | 2026-08-23T20:44:59+09:00 |
| Subject | Original pre-outcome M3Top3 v1 baseline |
| Execution boundary | Internal PMO; IVA participation `NONE` |
| Runtime / Git mutation | `NONE` |
| Official / Golden / Replay execution | `NONE` |
| Overall classification | **`UNPROVEN`** |
| State consequence | `S0_PRE_OUTCOME_BASELINE_CANDIDATE`; `S0→S1 NOT ELIGIBLE` |

## 1. Executive finding

The original pre-outcome M3Top3 v1 is **not exactly recovered on the evidence available in the current workspace and accessible Git history**. The supplied materials preserve useful semantic fragments and later working-engineering pointers, but do not close the original identity chain across contract, official scorer, configuration, environment, test oracle, release manifest, timestamp receipt, outcome-access history, and subsequent change history.

Accordingly:

- `EXACT_RECOVERED` — **NO**. Mandatory original bytes and provenance links are missing.
- `SEMANTICALLY_RECONSTRUCTED` — **NO**. No separately identified and Owner-approved reconstruction release exists.
- `APPROXIMATE` — **describes later working engineering only**, not the original v1 identity.
- Original pre-outcome v1 — **`UNPROVEN`**.

This is an identity/provenance finding, not a model-performance finding. It does not establish that v1 is invalid, nor does it establish that v1 is outcome-blind. It establishes that neither claim is presently provable from the reviewed evidence.

## 2. Classification rule applied

| Classification | Minimum evidence required | Audit result |
|---|---|---|
| `EXACT_RECOVERED` | Original contract, scorer/code, config, dependency/runtime identity, tests/oracles, release manifest, content hashes, pre-outcome timestamp receipt, outcome-access/change history all linked without semantic substitution | Not met |
| `SEMANTICALLY_RECONSTRUCTED` | Explicit gap record, reconstructed semantics, separate identity such as `v1r-semantic-reconstruction`, independent review and Owner approval | Not met |
| `APPROXIMATE` | Partial or placeholder implementation that may support engineering work but cannot claim original identity | Later infra only |
| `UNPROVEN` | Evidence cannot establish exact original identity or an approved reconstruction | **Met** |

## 3. Component closure assessment

| Required component | Available evidence | Status | Audit conclusion |
|---|---|---|---|
| Semantic contract | `Semi_Eval_Core_v1.0` records six-axis 3M weights, trigger states and `NOT_FOUND != negative`; related route/ledger documents preserve additional rules | `PARTIAL` | Useful semantics, but no complete executable F01–F09/gate/tie/missingness contract or original identity receipt |
| Official scorer/code | Git contains `tools/m3top3/model_interface.py` with a `DiagnosticFixtureScorer` explicitly marked test-only | `MISSING_OFFICIAL` | Diagnostic code cannot be promoted to official v1 |
| Configuration | Example configs identify reconstruction/working state and unresolved controls | `PLACEHOLDER` | Not an original frozen config |
| Environment/dependencies | No original lockfile/container/build receipt bound to a v1 release was located | `NOT_PROVEN` | Reproduction environment unclosed |
| Tests and independent oracle | Infrastructure tests and GF01–GF20 taxonomy exist | `PARTIAL` | No concrete fixture byte bundle plus independently authored expected-output hash |
| Release manifest/package | A later authorization record names two expected research-package ZIPs and expected hashes/sizes | `NOT_EXECUTED` | Named ZIPs are absent from the inspected authorized/recovery/current trees; no registration/readback receipt |
| Content-hash chain | Current files and several Git blobs can be hashed | `PARTIAL` | Present-day hashes do not create a pre-outcome release receipt |
| Pre-outcome timestamp | Source filenames/body labels say 2026-08-14; OOXML core dates are generator defaults; accessible Git M3Top3 engineering begins 2026-08-15 KST | `NOT_PROVEN` | No independent original freeze timestamp |
| Outcome-access history | U127 workbook contains winner/MFE/full-rank fields; a 2026-08-22 ASA run journal names winner-readiness ledgers | `PARTIAL_EXPOSURE_PROVEN` | Exposure exists by the cited dates, but no complete person/LLM access ledger was located |
| Change history | Later infrastructure commits are available from 2026-08-15 KST | `PARTIAL` | Does not bridge from an original pre-outcome v1 artifact to later changes |

## 4. Claim → evidence matrix

The companion JSON is the machine-readable register. The following are the decision-critical rows.

| Claim | Artifact | Exact path / commit | Hash | Status | Authority |
|---|---|---|---|---|---|
| Six-axis weights and trigger semantics are preserved as a source fragment | `Semi_Eval_Core_v1.0_2026-08-14.docx` | `project_sources/06-Semi_Eval_Core_v1.0_2026-08-14.docx` | SHA-256 `3a8c70df26dee0b3c1430846cd9934aa237fd2075f322d78d899ed8cb81acc54` | `SUPPORTED_PARTIAL` | Source-design evidence; not executable-release authority |
| PIT/return-routing semantics are preserved as a source fragment | `Semi_Data_Route_v1.1_2026-08-14.docx` | `project_sources/07-Semi_Data_Route_v1.1_2026-08-14.docx` | SHA-256 `508f98e88c150ceb751db2227727db529eb04da467c53a6eed5278ca5e17aa02` | `SUPPORTED_PARTIAL` | Source-design evidence |
| Universe document does not close U127 origin authority | `Semi_Universe_v1.0_2026-08-14.docx` | `project_sources/08-Semi_Universe_v1.0_2026-08-14.docx` | SHA-256 `eef313bc71bd0a5cb019f92e43e1bf38c2a63633bb847320d1cb4c8fe4ea9023` | `SUPPORTED_GAP` | Source-universe evidence; covers U46/historical eligibility, not U127 genesis |
| Supplied project sources do not provide a complete executable v1 contract | Project-source set 01–16 | `project_sources/` | Individual hashes recorded in companion JSON | `NOT_PROVEN` | Audit observation within inspected source set only |
| Earliest accessible pre-infra tree has no `m3top3` path | Repository tree | repo `AofSpds/asset-agent-asa`; commit `a02145cabf0c057591adf4098b630fca3a6453dc`; tree `2b4fe09827329f96f6d71822c42b0f980b36d34c` | Git tree SHA-1 as shown | `SUPPORTED` | Git history evidence; tree scan `truncated=false` |
| Later infra declares the official frozen scorer unavailable | Infrastructure spec/audit | commits beginning `1cd98e5612d9f734c6215cc6ecee475534859d02`; paths under `control/m3top3/v0.1/` | spec blob `15ff7344f3547a0dd62eb8d92179c47d1b611583`; audit blob `37c10ebed350f4fb2221c47c148bcf3cf8d05a00` | `SUPPORTED` | Working-engineering evidence, not semantic authority |
| The accessible scorer is test-only | `model_interface.py` | commit **`2615bc34747f147cbc7d4bbf7c23eed8c2c418de`**; `tools/m3top3/model_interface.py` | Git blob `1bc359a70a399a1eb94ef33703e2e5487afa8006` | `SUPPORTED` | Code evidence; explicitly excludes official-model status |
| Example configs remain reconstruction/placeholder artifacts | Snapshot/backtest examples | commits `dad9cc0d5dd07095910fca0dd9a31c40f08f456b`, `c5040082b8c20f22309fdf49eec29e2867ea47f7` | blobs `cb13d80be4ddb20bff73130e622c731153035b58`, `05d7b40a511406d2f1057a0fa92010c27c7da33f` | `SUPPORTED` | Working config only |
| Golden preparation does not bind an official model artifact | Golden preparation YAML | `control/core_b/M3TOP3-v1-GOLDEN-REPLAY-SCIENTIFIC-PREPARATION_v0.3_WORKING.yaml` | Git blob `315bffb3d0803da7b6f7da18268b8ab6b0e3ba4b` | `SUPPORTED` | Preparation only; filename/internal-version mismatch and exact binding pending |
| Exact research-package registration never closed | Registration authorization | commit `0940227893c9439a2f196586067c5ec2e3f31959`; exact path recorded in companion JSON | content SHA-256 `ada5267873ba9aa19a10e83f26f9490711a79f9df781bc80167b51e992d387da`; Git blob `2085322578ba779d7dbcddc69fb352ca137fb680` | `SUPPORTED_NOT_EXECUTED` | Authorization record says execution/readback `NOT_EXECUTED` |
| Named exact ZIPs are absent from inspected recovery/current trees | Expected v0.1/v0.2 ZIP paths | inspected trees `a7873ba446fc5d3b94142fefa5121549cbaf9f73`, `2521bfc8ed7ea23a7ad3abebe2bd1b6aeb8becac`, `2e08038a8c8c887da4c421fb2adcc74b35e444f9` | expected SHA-256 values recorded in companion JSON | `NOT_FOUND_IN_INSPECTED_TREES` | Bounded negative finding; not a claim of global nonexistence |
| Outcome-bearing material is present in the current evidence set | U127 working workbook | `qa/wp2_sources/U127_Data_Expansion_Working_v0.8_2026-08-15.xlsx` | SHA-256 `44501584c9dc6224637e9193219c1e8c87507af77dc15dc3944a3d04af524cda` | `SUPPORTED` | Outcome-exposure evidence; workbook is freeze-candidate/preliminary |
| Complete outcome-access history is not closed | ASA run journal plus absence of a complete access ledger in reviewed scope | journal blob/path in companion JSON | Git blob `309db6a9e019ded5b30b57464c168b3ef2d6a87d` | `PARTIAL_ONLY` | Proves a latest-known exposure floor, not full prior access history |
| Owner approval authorizes plan execution, not model semantic identity | Direct dispatch packet | `upload/M3Top3_Owner_to_PMO_Direct_Dispatch_Packet_v1.0_2026-08-22(1).md` | SHA-256 `16688e3cc089f9d60524b3ea6ff7f34fa6ad59c0aa66bfc7b1940c54914d82cf` | `SUPPORTED` | Owner execution authority; no Model Freeze/Golden/Replay/Release/Production authority |
| Current v0.4 runtime safety evidence does not close G1 identity | Master status checkpoint | `remediation/r_wp4_03_v04_authority/R_WP4_03_V0_4_MASTER_STATUS_CHECKPOINT.json` | SHA-256 `710e57fdf2a829ccef4198b025fd8964ca035627e3fe74a4fe6ba10e074166bb` | `SUPPORTED_SCOPE_LIMIT` | Runtime-safety authority only |

### Exact-locator correction

The earlier `R_WP1_01_EXACT_IDENTITY_RECOVERY_REPORT_v0.1.md` reached the same overall non-recovery conclusion, but its `model_interface.py` commit locator contains a transcription error. The verified commit is:

`2615bc34747f147cbc7d4bbf7c23eed8c2c418de`

not:

`2615bc34747f147cbc7ed1992c1c752185638868`

The prior report is therefore treated as `SUPPORTED_WITH_LOCATOR_CORRECTION`, not overwritten.

## 5. Bounded chronology

| Time | Evidence event | Identity meaning |
|---|---|---|
| 2026-08-14 (document labels) | Source-design documents label versions/dates | Semantic date labels only; OOXML core timestamps are non-probative generator defaults |
| 2026-08-15 06:47:33 KST | Commit `a02145...` tree has no `m3top3` path | Accessible pre-infra lower bound |
| 2026-08-15 06:49:12–06:52:58 KST | M3Top3 infrastructure/config/test commits appear | Later working engineering; does not prove an earlier frozen v1 |
| 2026-08-17 08:54 KST | Golden preparation working artifact | Exact binding and official entry remain unauthorized |
| 2026-08-19 05:26 KST | ZIP registration authorization commit | Authorization says registration/readback not executed |
| 2026-08-22 07:01 KST | ASA run journal references winner-readiness ledgers | Latest-known documented outcome-exposure floor; not a complete access chronology |
| 2026-08-23 | Runtime-safety/remediation checkpoint | Keeps exact identity as next open gate; adds no original-v1 identity proof |

## 6. G1 blockers

`BID-01` — Original complete semantic/executable contract bytes are not bound to a release receipt.

`BID-02` — Official scorer/code identity is missing; the available deterministic scorer is explicitly test-only.

`BID-03` — Original frozen configuration, tie policy, gate semantics, missingness policy, and exact feature mapping are not closed.

`BID-04` — Original dependency/runtime/build identity is not closed.

`BID-05` — Concrete Golden fixtures and independent expected-output oracle hashes are not closed.

`BID-06` — Expected v0.1/v0.2 exact research-package ZIPs were not found in the inspected authorized/recovery/current trees; registration/readback is recorded as not executed.

`BID-07` — No independent pre-outcome timestamp receipt binds the complete package.

`BID-08` — Complete human/LLM outcome-access history is not available; outcome-bearing workbook and later exposure evidence exist.

`BID-09` — No continuous change ledger links an original frozen package to later infrastructure work.

`BID-10` — No Owner-approved, separately named semantic reconstruction exists.

## 7. Mandatory stop rules

1. If any recovered ZIP/file mismatches the authorized expected path, size, SHA-256, version, or manifest, stop and quarantine it as `IDENTITY_MISMATCH`.
2. Do not re-zip, recreate, normalize, or substitute semantically equivalent bytes and label them original v1.
3. Do not relabel working infrastructure, example configs, or `DiagnosticFixtureScorer` as the official v1 implementation.
4. Do not use later runtime v0.4 safety evidence as proof of original pre-outcome identity.
5. Do not claim `PRE_OUTCOME` or `OUTCOME_BLIND` without a complete creation/freeze receipt and bounded access provenance.
6. Do not advance `S0→S1`, Model Freeze, Official Golden, Official Replay, Promotion, Release, or Production while any mandatory identity component remains open.
7. If a semantic rule must be inferred, stop original-v1 recovery and route a new, explicitly versioned reconstruction identity.
8. IVA must not participate in this execution lane; independent validation remains separate.

## 8. Owner decision surface

**Owner decision required now: `NONE`.** The approved PMO direct-dispatch scope permits continued read-only source-byte recovery and provenance closure.

Owner intervention is required only when either trigger occurs:

- a source custodian confirms that the authorized exact package bytes are unavailable, or recovered bytes fail the expected path/size/hash/version checks; or
- PMO proposes to close G1 without exact recovery.

At that point the Owner must select one of two explicit paths:

1. retain `S0_ARCHIVAL_BASELINE_IDENTITY_UNRESOLVED`; no Official Golden/Replay claim; or
2. authorize a new identity such as `v1r-semantic-reconstruction`, with explicit semantic gap register, fresh hashes, independent review, and no claim that it is the original v1.

Any semantic substitution, `S0→S1/S2` transition, Model Freeze, Official Golden/Replay, Promotion, Release, or Production authorization remains reserved and is not created by the existing execution approval.

## 9. Audit conclusion

The available evidence supports preservation of M3Top3 v1 as a valuable **pre-outcome baseline candidate**, but it does not support exact identity. G1 remains open under classification **`UNPROVEN`**. Continue exact-byte/source-custodian recovery only; keep every official model and performance gate blocked.

