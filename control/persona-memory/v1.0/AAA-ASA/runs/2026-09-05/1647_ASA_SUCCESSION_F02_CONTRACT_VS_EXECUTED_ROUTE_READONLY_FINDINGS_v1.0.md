# ASA succession — F02 contract versus executed route: bounded read-only findings

PROJECT = AAA
PRODUCT = ASSET AGENT ASA
CURRENT_PERSONA_LOCK = AAA-ASA (ASA)
DATE_KST = 2026-09-05 16:47 KST
JOURNAL_CLASS = APPEND_ONLY_PERSONA_CONTINUITY_AND_ADVISORY_READOUT
AUTHORITY_SOT = FALSE
INDEPENDENT_VALIDATION_PERFORMED = FALSE
NEW_PMO_EXECUTION_DISPATCHED = FALSE
MODEL_OR_PIT_SEMANTIC_CHANGE_AUTHORIZED = FALSE
RELEASE_PROMOTION_PRODUCTION_AUTHORIZED = FALSE

## 1. Scope and recovery

Owner invoked ASA and supplied the PC1/F02 channel-succession packet. Recovered the current Git bootstrap, selector, active Organization and Shared Contract, current Persona-name projections, common memory and execution behavior, ASA MEMORY/WORKLOG and the complete detailed handoff. Current Persona is AAA-ASA, not PMO. Historical August MEMORY/WORKLOG blockers are not restored over the September terminal records.

Detailed handoff: commit 858cee68bb6b0e18e3374f03ee0d653a5502a75f, blob b4c147ae9f592d8b5834e5b1058bb83e912c604d, path control/persona-memory/v1.0/AAA-ASA/runs/2026-09-05/1630_ASA_CHANNEL_SUCCESSION_PC1_TERMINAL_F02_AVAILABILITY_TOP3_OBJECTIVE_v1.0.md.

Preserve original-purpose correction at 0ceec3817532cc78e526fef0c9deb5af0a479d1a and Owner G2 direction in Issue #53 comment 5548034767. M3Top3 was already a conditional Top3 opportunity ranker; this is not a new objective. No exhaustive unresolved-row completion or old ZIP search is introduced.

## 2. Current terminal state directly read

PC1 branch task/aaa/m3top3-process-calibration-pc1-20260905 still resolves to 6b219f9f3a37dd89b26fc1d6ecec6b8eb890fa9f at this readback.
Run root: control/m3top3/process-calibration/v1.0/runs/AAA-M3TOP3-PROCESS-CALIBRATION-PC1-20260905-143739-CODEX-01/.
Terminal: COMPLETE_BOUNDED_ZERO_GAIN_PARTIAL_TELEMETRY.
W1 outer 127 / INCLUDE 57 / proven exclusion 8 / unresolved exclusion 62; Strict scoreable remains 1/57. Official Top3/Top10 and model-performance validation remain unperformed.
Four F02 routes supplied zero candidates, so parsing, admission, materialization and new scoring were not attempted. Their observed terminal failure is source acquisition, not a scorer rejection or proof of universal source absence.
PC1 report and route records were read, not independently rerun or revalidated.

## 3. F02 definition versus narrower executable admission

Inspected exact reviewed code revision c15cbfa9bbedcb3b388b9d101b269ced2fc83bc5.

Definition: control/core_b/M3TOP3-FEATURE-SCHEMA_v1.0_WORKING.yaml, blob 2550f781c2a901c0faada95dfc4a788503ec669b, F02 section.
It describes realized improvement in revenue, operating profit/margin, backlog or beta-relevant utilization; latest values versus an appropriate prior comparable period; publication before cutoff; robust cross-sectional metric percentiles and their median; no valid metric means NA. This section does not prescribe the title 영업(잠정), the single quarter 2024Q2, one issuer, or one HTML line layout. Embedded historical authoring/freeze states are not new current-state claims.

Consumed-path registry: blob 5faa4d5739bf9ecb0c11d16f6d7d697ff3983977, M3TOP3-FEATURE-INPUT-REGISTRY_v1.0_WORKING. Recovered by exact blob after the embedded commit/path read returned 404; the object was not lost. It permits metric_changes / metric_pairs / mixed_governed with explicit transformation and PIT/lineage requirements.

Actual adapter: tools/m3top3/real_input_replay_v1.py, blob 8d07b6ff2196e794aa2588e7923b366ad9eaa526.
- _leaf_spec fixes current=2024Q2, prior=2023Q2, observed basis=QUARTER, unit=KRW_MILLION.
- validate_feature_leaves fixes scope=CONSOLIDATED and requires all eight leaves: current, prior, change_mode and operator_id for both revenue and operating_profit.
- change_mode must be RELATIVE; prior cannot be zero; the fixed operator id is M3TOP3_F02_RELATIVE_FROM_OBSERVED_PAIR_v1.
- source authority is KIND official FILING with HTTPS KIND locator, HTML/UTF-8 exact raw custody and conservative date-only cutoff handling.
- validate_source_manifest requires literal raw-text anchors (주)동진쎄미켐, 2024.08.02 and 잠정 in addition to the supplied title.
- observed-value locators are fixed to HTML physical lines 42/45 for revenue and 59/62 for operating profit.

The reviewed scorer patch tools/m3top3/features_v1_narrow_patch.py (blob b9017f5db0fb637c8a449d5ee3cb1c4a05481076) uses explicit change modes; RELATIVE=(current-prior)/abs(prior), followed by metric-wise percentiles. No economic growth threshold was reached or tested on the four companies in PC1.

Advisory conclusion: the current real-input adapter is an issuer/date/layout-specific admission implementation, not a general multi-issuer F02 ingestion path. The PMO run journal already records this limitation at P0. Keeping those bytes unchanged does not make another issuer's otherwise valid source admissible. This is an independently visible code limitation, but it is NOT the observed cause of four rejected parser submissions: PC1 acquired no source candidate and never invoked that stage.

## 4. Executed discovery conditions and company dispositions

F02_DISCOVERY_RECEIPT.json blob 0ff2bc443e94f0e6241e33677eaac6e0093be4a8 and PROCESS_EFFICIENCY_LEDGER.jsonl blob b0f41ffc4a9df3092f55813c1e4616a1345e6927 were read at PC1 terminal revision.

- 003160: company-title probe 영업(잠정) returned zero; all-disclosure query for 2024-01-01 through 2024-08-09 recorded latest displayed filing 2024-07-02. No admitted source. No post-cutoff corroborating filing is recorded for this company in the receipt.
- 025560: same title probe zero; latest displayed cutoff-safe filing 2024-07-26. Receipt records a half-year report filed 2024-08-14, classified after-cutoff and not fetched into run storage.
- 031980: same title probe zero; latest displayed cutoff-safe filing 2024-07-05. Receipt records a half-year report filed 2024-08-14, classified after-cutoff and not fetched into run storage.
- 036200: issuer autocomplete failed at least twice; exact total uninstrumented; switched to global title search. Receipt records a half-year report filed 2024-08-14. This is an access/identity-route failure plus unsuccessful alternate discovery, not simply a financial-data absence claim.

Global title query used 영업(잠정) over 2024-01-01 through 2024-08-09. Forty pages were observed; pages 1-33 were treated as relevant recent-quarter results, while pages 34-40 in the May/June Q1 cycle were labeled overscan. This documents a recent-Q2-focused route, not exhaustive consideration of all prior disclosed comparable periods.

All-disclosure query summaries name only latest displayed dates; they do not prove that every earlier quarter/annual report was opened and checked for F02. Do not reconstruct unlogged browser actions. The handoff records Owner-assisted manual selection of 003160; the inspected corresponding discovery ledger entries do not separately attribute that assistance. Full automation is not claimed.

## 5. What is and is not established

Established: (1) the executed source route was narrower than the general F02 description; (2) the unchanged adapter has hard-coded issuer/date/period/layout constraints; (3) PC1 produced zero new comparable company inputs; (4) three observed half-year filings were later than the fixed cutoff, and one issuer lookup had access/identity trouble.

Not established: F02 is intrinsically invalid; early-disclosure bias is quantitatively proven; earlier usable sources exist for all four; earlier-quarter substitution necessarily solves the problem; the four companies failed model-economic criteria; any new Top3 performance evidence exists.

A latest pre-cutoff disclosed comparable period is not excluded merely by the wording of the F02 definition. But a production-ready choice of period, allowed staleness, same-basis comparison, and cross-company comparability has not been bound by this readout. The present adapter also rejects period substitutions. No silent change to those policies is permitted.

## 6. Successor design direction — not dispatch or approval

Do not reopen PC1 or repeat its unchanged search in W2. The next request should bind a small multi-company batch without future-winner selection and separate:
1. Existing-semantics mechanical correction: issuer/date/table mapping and verified source-line anchors become source-specific rather than copied from 005290, while all identity, raw custody, publication and consumed-value provenance checks remain enforced. Use existing bounded correction authority where applicable; fresh affected checks, not automatic full-suite repetition.
2. Period/source interpretation: identify the latest pre-cutoff realized reporting basis and appropriate comparable period per the existing definition; explicitly assess stale or heterogeneous periods. Any material new missingness, freshness, metric-selection, quarter-selection, estimation or PIT policy is a narrow governed decision item, not a parser-only edit.
3. Source-to-score acceptance: demonstrate actual comparable input materialization before expecting ranking expansion. Report provisional within-observed-cohort ranks and missing rivals; do not market three available issuers as the best three of U127.
4. Action-start/action-end logging and no third identical failure without new evidence from the first real action. No new provider, paid data, credentials or call ceiling assumed. No CA fetch without a downstream receipt-consumption path.

This journal only persists ASA's bounded read-only comparison and successor design considerations. No model/data/execution artifact, authority pointer, main branch, PMO task branch, old score or PC1 report was changed. No new PMO execution, external source acquisition, scorer execution, code test or independent validation was performed by this ASA readout.

## Exact supporting refs

- PC1 report blob 00358fef8faca320f189298a83150807e492a706.
- PC1 route summary blob 78e08781e8f3123a7949438a67b458e5bb507b25.
- PC1 PMO journal blob cb59a0f8d781061719a6ec5e413df752b5bda74a at control/persona-memory/v1.0/AAA-PMO-ORCHESTRATOR/runs/2026-09-05/143739_m3top3_process_calibration_pc1_pmo_root.md.
- ASA PC1 receipt commit 063a40bcb5b69d7a5f23d17c98cd0b3c5dbce62e, blob 170dedea53aaf299bf4b205a5e08d29389b07566.
- PC1 request commit 795484f2b61aca9500bfc9c19039fb6d83e8430b, blob 7939c9de970a1b896f7efb7489aa1d880109eb6d; bounded nonsemantic correction and affected-validation rule in section 4.

NEXT_ROUTE = Draft bounded successor input-adapter/source-selection execution request; preserve original Top3 objective, all historical results, cutoff and authority boundaries.
OWNER_ACTION_REQUIRED_FOR_THIS_READOUT = FALSE
FOLLOWUP_EXECUTION_ETA = NOT_ESTIMATED_REQUEST_NOT_DISPATCHED
