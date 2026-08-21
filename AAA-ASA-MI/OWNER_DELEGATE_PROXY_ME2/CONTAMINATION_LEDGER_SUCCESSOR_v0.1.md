# ME-2 Contamination Ledger — Successor v0.1

## Lineage and Classification

- Predecessor: `AAA-ASA-MI/MEETING_MEMORY/AAA_ASA_ME_LIVE_SHADOW_CONTAMINATION_LEDGER_v0.1_2026-08-21.md`
- Predecessor ref: `5028fc536f2732996c98cbd1e9effa8725d584dc`
- Cycle classification: `QUASI_PROSPECTIVE / METHOD_CALIBRATION_ONLY`
- Clean prospective claim: `NOT_AUTHORIZED`
- Ledger policy: append/successor; predecessor history is not rewritten.

## Exposure Records

| exposure_id | time | actor/context | source ref | exact content class | candidate identity exposed | evaluator rank/score/preference exposed | Owner blind answer exposed | substantive candidate content exposed | impact on held-out status | remediation/containment |
|---|---|---|---|---|---|---|---|---|---|---|
| ME-CONTAM-0001 | inherited at execution start | prior ASA-ME initialization | predecessor ledger at `5028fc536f2732996c98cbd1e9effa8725d584dc` | initialization record | as recorded by predecessor | NO | NO | as recorded by predecessor | classification remains quasi-prospective | predecessor preserved; successor used |
| ME-CONTAM-0002 | inherited at execution start | prior ASA-ME metadata inspection | MI repository paths and labels | file/path metadata only | path labels only | NO | NO | NO | no upgrade or downgrade beyond quasi-prospective | metadata exposure distinguished from content access |
| ME-CONTAM-0003 | 2026-08-21 execution | root orchestrator | packet `e444d39679ea7da8fe090141bbeb1257b4127a47`; ODP/MI refs; predecessor ledger | executable packet, exact Git metadata, ODP artifact metadata, contamination history | source filenames and Cxx labels only; no private mapping content used for judgment | NO | NO | NO candidate bodies; no eight source bodies | root context is ineligible for P0/P1 because it orchestrates the scene | P0/P1 delegated to fresh `fork_turns=none` workers with isolated input roots |
| ME-CONTAM-0004 | 2026-08-21 execution | scene-builder worker | eight exact `BLIND_INPUTS` blobs at `d50b73e91f3964626c060bd0165cbaa3371442c4`; new private codebook | substantive source surfaces, neutral briefs, Cxx-to-source assignment | YES, limited to Cxx-to-source pairing; no Track mapping | NO | NO | YES | worker cannot be a held-out Proxy predictor | permanently disqualified from P0/P1; no prediction produced |
| ME-CONTAM-0005 | 2026-08-21 execution | independent blind-QA worker | eight exact private sources, eight neutral briefs, codebook solely for pairing, QA controls | semantic preservation and neutralization QA | YES, limited to Cxx-to-source pairing; no Track mapping | NO | NO | YES | worker cannot be a held-out Proxy predictor | permanently disqualified from P0/P1; QA initially failed 2 briefs, repair round rechecked PASS 8/8 |

## Explicit Non-Access Assertions Before Proxy Execution

- Old `PILOT_ALIAS_KEY`: NOT_ACCESSED
- Track mappings: NOT_ACCESSED
- Evaluator result, rank, score, or preference files/content: NOT_ACCESSED
- Champion/winner artifacts: NOT_ACCESSED
- Original `CANDIDATES` bodies: NOT_ACCESSED
- Current or post-cutoff Owner preference evidence: NOT_ACCESSED
- Any prior P0/P1 output: NOT_ACCESSED

Evidence state for these assertions is `PARTIAL`: bounded worker attestations and connector/path logs exist, but no independent forensic validator was run. No Independent Validation claim is made.

## Scene-Build Disposition

- SOURCE_BODY_EXPOSURE: YES / REQUIRED_FOR_SCENE_BUILD_AND_QA
- SOURCE_TO_NEW_ALIAS_MAPPING_EXPOSURE: YES / SCENE_BUILDER_AND_QA_ONLY
- TRACK_MAPPING_EXPOSURE: NO
- EVALUATOR_RESULT_EXPOSURE: NO
- OWNER_PREFERENCE_EXPOSURE: NO
- PROXY_OUTPUT_EXPOSURE: NO
- SCENE_BUILDER_MAY_PREDICT: NO
- BLIND_QA_WORKER_MAY_PREDICT: NO
- CONTAMINATION_LEDGER_STATUS: COMPLETE_THROUGH_SCENE_QA / PROXY_RECORDS_PENDING

## Independence Consequence

P0 and P1 must run in separate fresh sanitized workers with `fork_turns=none`, isolated allowlisted local input roots, no codebook, and no mutual output visibility. If this cannot be demonstrated, Proxy execution must stop.
