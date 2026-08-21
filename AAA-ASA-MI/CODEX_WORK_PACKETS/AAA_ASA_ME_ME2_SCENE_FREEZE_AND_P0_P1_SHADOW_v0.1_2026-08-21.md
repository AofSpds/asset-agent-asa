# [AAA-ASA-ME → WORK]
# [ME-2 SCENE FREEZE + P0/P1 FRESH SANITIZED SHADOW]
# [ONE HANDOFF = ONE COMPLETE PACKET]

PROJECT = AAA
PRODUCT = ASSET AGENT ASA
PARENT_PERSONA = AAA-ASA
WORKSTREAM = AAA-ASA-ME
CHANNEL_IS_SEPARATE_FORMAL_AUTHORITY_PERSONA = FALSE
TASK = AAA_ASA_ME_ME2_SCENE_FREEZE_AND_P0_P1_SHADOW_v0.1
REQUEST_TYPE = NON_NORMATIVE RESEARCH EXECUTION / METHOD_CALIBRATION
OWNER_DELEGATION_AUTHORIZED = FALSE
OWNER_ACCEPTANCE_PROXY_AUTHORIZED = FALSE
INDEPENDENT_VALIDATION_CLAIM = NONE
PRODUCTION_AUTHORIZED = FALSE

===============================================================================
0. PURPOSE
===============================================================================

Execute the next ASA-ME experiment after ODP-0 intake.

The immediate objective is NOT to build a canonical Owner clone and NOT to run P0-P5 all at once.

Use the ODP-recommended execution order:

DECISION SCENE FREEZE + RECEIPTS
→ P0 GENERAL CONTROL
→ P1 EPISODIC PROXY + RULE-BASED ABSTENTION
→ FREEZE P0/P1 OUTPUTS
→ RETURN A BLIND OWNER-REVIEW BUNDLE

P2/P3/P4/P5 are explicitly deferred to later successors.

CURRENT_CYCLE_CLASSIFICATION = QUASI_PROSPECTIVE
USE_RESTRICTION = METHOD_CALIBRATION_ONLY
CLEAN_PROSPECTIVE_CLAIM = NOT_AUTHORIZED

===============================================================================
1. EXACT INPUT REFS
===============================================================================

REPOSITORY = AofSpds/asset-agent-asa

ASA-ME PREPARATION BRANCH =
asa-mi-owner-memo-20260821-1449

At execution start:
- resolve and record the exact current HEAD of the preparation branch;
- do not assume the packet-authoring HEAD remains current;
- record tree SHA and packet blob SHA.

ODP-0 RESULT BRANCH =
research/asa-mi-owner-delegate-odp0-20260821-v01

ODP-0 RESULT HEAD =
04612ff674d54c0739aca26e8f9e3206daea5b91

ODP ARTIFACTS =
1. AAA-ASA-MI/OWNER_DELEGATE_PROXY_ODP0/ODP_PRIOR_ART_SYNTHESIS_v0.1.md
   Git blob = da9cc5c9fa2c869a67f4369e52f0ab4263a5298a
   SHA256 = 7873c56e27b1437eacdc8750674b100c82ae4d474e3ec4d3ef5768dd26abe309

2. AAA-ASA-MI/OWNER_DELEGATE_PROXY_ODP0/OWNER_HISTORICAL_DECISION_EPISODE_CORPUS_DRAFT_v0.1.md
   Git blob = e143217d2dd2f24727fe820be8d4155b1d532f08
   SHA256 = 20ff3c761008dea8b5efb81e7cca38d9e4c11fa2f64ccb9cc90279a3dcda20d1

3. AAA-ASA-MI/OWNER_DELEGATE_PROXY_ODP0/ODP_METHOD_DATA_FIT_AND_EXPERIMENT_DESIGN_v0.1.md
   Git blob = 12bce7c9c1009eb8a41b7579344f9a1b9155ad84
   SHA256 = 3b15ffd1cecaae66845f66865764401b87de1bdb1a768b63a3f791b95b9eb8b5

MI RESEARCH EXACT COMMIT =
d50b73e91f3964626c060bd0165cbaa3371442c4

MI RESEARCH ROOT =
AAA-ASA-MI/RESEARCH/RESEARCH_REPAIR_AND_8_POSITION_PILOT_20260821_v0.1/

MI MANIFEST =
00_README_AND_MANIFEST.md
Git blob observed by ASA-ME = 61d2bfd5a7710ec6357c32fde57b8b48a2e318f8

EXISTING BLIND INPUTS AND SHA256 =
- BLIND_INPUTS/R03.md = f4914a0ddd069ef18bc66fe9e3b27dc54e62b16dc93651759b02d1ddeca7d256
- BLIND_INPUTS/R05.md = 5708ce54e7187cd16201f1984f52216945235658d66c9ba1ee281ffecc76964c
- BLIND_INPUTS/R08.md = b181dfc6b7051d01a8c25c816e6c97c234a0d337e7dc885733702283e86a4626
- BLIND_INPUTS/R11.md = 159b6d311c88278e5062ecea09f5e08789b8a80fec1fe69583c273a25b26c2b0
- BLIND_INPUTS/R14.md = 0835812677f28485035cc40201f10004eebfc231ef6a3482e558b06afb4712fe
- BLIND_INPUTS/R17.md = 5b5e8d47b2f56b2a3ac644edb3b74a73d3b8e3c56b1d443098f5a5d883920536
- BLIND_INPUTS/R19.md = 8015e146dd0922fd7d8a15ac62d8e9551d409793966318d297196a729542b4cb
- BLIND_INPUTS/R21.md = a5b6d0533859e8a3fcd08bb7313ab4f775e0d1e30cabd3496dc64d51af12ce51

KNOWN BLIND-INPUT QA DEFECTS =
- R19 retained cue phrases such as “prevailing research basis”, “ASA-MI”, and “current research”.
- mechanical acronym replacement produced malformed labels `R17-R17` and `R14-R14`.
- existing blind transformation was post-hoc and did not have a prospectively signed transform manifest.

Therefore:
EXISTING_BLIND_INPUTS = SOURCE_SURFACES_ONLY
EXISTING_BLIND_INPUTS != FINAL_OWNER_BLIND_BRIEF_BUNDLE

===============================================================================
2. HARD INFORMATION BOUNDARY
===============================================================================

This execution MUST NOT read the content of any current evaluator/result/preference artifact before P0/P1 and Owner initial judgment are frozen.

BLOCK CONTENT ACCESS TO AT MINIMUM:
- 09_INDEPENDENT_EVALUATION_AND_THEORY_EXTRACTION.md
- 10_OWNER_SYNTHESIS_AND_DECISION.md
- AAA_ASA_MI_CONSOLIDATED_RESEARCH_REPORT_v0.1.md
- RECEIPTS/PILOT_EVAL_PEV1_RECEIPT.md
- RECEIPTS/PILOT_EVAL_PEV2_RECEIPT.md
- RECEIPTS/PAIRED_THEORY_EXTRACTION.md
- RECEIPTS/PILOT_ALIAS_KEY_v0.1.md
- any file containing current evaluator rank, score, preference conclusion, champion/winner label, or Track↔blind alias mapping
- any post-cutoff Owner statement revealing current candidate preference

Do not open CANDIDATES/TRACK_A_* or CANDIDATES/TRACK_B_* content unless the re-neutralization from existing BLIND_INPUTS is proven substantively inadequate.

If candidate source bodies must be opened, the scene-builder context becomes further contaminated and MUST NOT be reused as a proxy prediction context.

FILE/PATH METADATA EXPOSURE != CONTENT ACCESS.
Record metadata exposure separately.

===============================================================================
3. ME-2A — CONTAMINATION RECONSTRUCTION
===============================================================================

Start from the existing ASA-ME contamination ledger if present:
AAA-ASA-MI/MEETING_MEMORY/AAA_ASA_ME_LIVE_SHADOW_CONTAMINATION_LEDGER_v0.1_2026-08-21.md

Append/successor, never silently overwrite history.

Required fields per exposure:
- exposure_id
- time
- actor/context
- source ref
- exact content class
- whether candidate identity was exposed
- whether evaluator rank/score/preference was exposed
- whether Owner blind answer was exposed
- whether substantive candidate content was exposed
- impact on held-out status
- remediation/containment

The final classification for this cycle remains fail-closed:
QUASI_PROSPECTIVE / METHOD_CALIBRATION_ONLY

Do NOT spend effort trying to upgrade it to CLEAN unless decisive evidence appears naturally.
The purpose of this Work is to make the calibration scientifically useful, not to rescue a clean label.

===============================================================================
4. ME-2B — BUILD A NEW NEUTRAL OWNER DECISION SCENE
===============================================================================

Use ONLY the eight existing BLIND_INPUTS as the primary substantive source surfaces.

Create a NEW neutral brief set with aliases:
C01 ... C08

Alias assignment requirements:
- generate a random permutation programmatically;
- record seed/source of randomness and permutation hash;
- do not expose the alias mapping in the user-facing return packet;
- do not read the old PILOT_ALIAS_KEY to construct the new alias mapping;
- maintain only Cxx ↔ Rxx in a sealed codebook for later post-freeze reconciliation.

For each brief:
- equal top-level template and heading structure;
- preserve substantive theory/model differences;
- remove old Rxx labels from the body;
- remove Track/original-position metadata;
- remove evaluator/result/status language;
- remove known R19 research-basis cues;
- repair malformed R17-R17 / R14-R14 aliases without changing substantive meaning;
- remove authorship/provenance clues not needed for Owner judgment;
- do not summarize away important objections, assumptions, mechanisms, implementation implications, or falsifiers.

The neutral brief template should contain at minimum:
1. Core claim / worldview
2. What exists or is treated as primary
3. Identity / relation / event / state treatment
4. Change / time / succession treatment
5. Persona / memory implications
6. Human-familiarity implications
7. Implementation implications
8. Main strengths
9. Main failure modes / objections
10. What evidence would weaken or overturn it
11. Important unresolved questions

Do not make every brief equally persuasive by flattening actual differences.
NEUTRALIZATION != HOMOGENIZATION.

===============================================================================
5. BLIND QA GATE
===============================================================================

Before any Proxy prediction, run deterministic and model-assisted QA.

Deterministic forbidden-token scan across all C01-C08 briefs for at least:
TRACK_A
TRACK_B
A1
A2
A3
A4
B1
B2
B3
B4
R03
R05
R08
R11
R14
R17
R19
R21
ASA-MI
PEV
G1
G2
G3
G4
G5
PASS
PARTIAL
INDETERMINATE
champion
winner
rank
score
prevailing research basis
current research

Model-assisted blind QA must answer only:
- Can any brief infer its original Track/position from residual metadata/style artifacts?
- Does any brief contain evaluator outcome/preference information?
- Did neutralization materially alter substantive content?
- Are templates comparable enough to reduce superficial presentation bias?

Blind QA may NOT rank or evaluate the candidates.

If QA fails, repair and rehash before prediction.

===============================================================================
6. FREEZE / RECEIPTS
===============================================================================

Create a new isolated result branch/worktree. Do not write to main.
Suggested branch:
research/asa-me-shadow-scene-p0-p1-20260821-v01

Persist at minimum:

A. DECISION_SCENE_MANIFEST_v0.1.md
- source commit
- exact eight source paths and SHA256
- neutralization recipe/version
- exact C01-C08 brief paths and SHA256
- scene cutoff
- method-calibration classification
- contamination refs
- no evaluator-result-access assertion with evidence state

B. BLIND_BRIEF_MANIFEST_v0.1.md
- Cxx paths/hashes/byte sizes
- common template version
- deterministic QA result
- model-assisted QA result

C. ALIAS_CODEBOOK_PRIVATE_v0.1.json
- Cxx ↔ Rxx only
- DO NOT include Track/original candidate mapping
- mark SEALED_UNTIL_OWNER_INITIAL_JUDGMENT_FREEZE

D. CORPUS_ALLOWLIST_P0_v0.1.md
P0 may read only:
- frozen neutral decision scene and briefs
- generic task/output schema
- no Owner history

E. CORPUS_ALLOWLIST_P1_v0.1.md
P1 may read only:
- everything allowed to P0
- ODP historical Decision Episode corpus at exact frozen ref
- only historical Owner evidence strictly before the decision-scene cutoff
- no current candidate evaluator/result data
- no post-cutoff Owner preference data

F. CORPUS_BLOCKLIST_v0.1.md
Include all blocked evaluator/result/alias artifacts and post-cutoff Owner preference evidence.

G. SCENE_FREEZE_RECEIPT_v0.1.md
- Git commit/tree
- file hashes
- freeze time
- branch
- execution environment
- contamination classification

===============================================================================
7. P0 + P1 EXECUTION
===============================================================================

CRITICAL INDEPENDENCE RULE:
The scene-builder context used to create/QA the neutral briefs MUST NOT itself produce P0/P1 predictions.

Use genuinely fresh sanitized prediction instances/workers if available.

If fresh-context independence cannot be positively demonstrated:
- do not fabricate Proxy results;
- stop after scene freeze;
- return `PROXY_FRESH_INSTANCE_INDEPENDENCE = NOT_PROVEN`;
- preserve the scene bundle for a separate fresh run.

P0_GENERAL_CONTROL:
- no Owner-specific data.
- output predicted Owner choice/ranking/reasons/objections/evidence attention/questions/uncertainty/change conditions.
- use rule-based abstention where the scene is insufficient.

P1_EPISODIC_PROXY:
- retrieve analogous historical Decision Episodes by decision class, tradeoff axes, stage, and temporal validity.
- include at least one counterexample episode where available.
- respect supersession.
- raw source evidence outranks derived interpretation.
- abstain if analogy is weak/conflicted/stale or decisive context is missing.

Both must use the same base model/version and same frozen C01-C08 scene where technically possible.

Do not let P0 and P1 see one another’s outputs.
Do not let either see evaluator results.
Do not let either see Owner answers for this scene.

===============================================================================
8. PROXY OUTPUT CONTRACT
===============================================================================

Persist separate immutable outputs:
PROXY_OUTPUT_P0_v0.1
PROXY_OUTPUT_P1_v0.1

Required fields:
- proxy_id/version
- base model/version/config
- exact scene manifest hash
- exact allowlist/blocklist hashes
- retrieved memory refs (P1 only)
- counterexample refs (P1 only)
- predicted_choice = Cxx | ABSTAIN
- predicted_ranking
- predicted_reasons
- predicted_objections
- predicted_important_evidence
- predicted_owner_questions
- predicted_uncertainty
- predicted_change_conditions
- confidence = calibrated value OR explicit UNCALIBRATED_BAND
- abstain_state = ANSWER | ABSTAIN | OWNER_QUERY_RECOMMENDED
- output SHA256
- freeze time
- contamination notes

No proxy output may claim Owner authority.

===============================================================================
9. OWNER BLIND REVIEW BUNDLE
===============================================================================

After BOTH Proxy outputs are frozen, produce a user-facing blind-review packet containing:
- only C01-C08 neutral briefs;
- a randomized presentation order frozen in advance;
- no Cxx↔Rxx mapping;
- no Proxy predictions;
- no evaluator rank/score/conclusion;
- no Track labels;
- concise Owner response form.

Owner response form must capture BEFORE any challenge/reveal:
1. initial choice
2. ranking or pairwise preference where possible
3. top reasons
4. strongest objection
5. evidence most attended to
6. uncertainty
7. natural question
8. minimal fact/evidence that would change the judgment

Do not ask additional elicitation questions until this initial Owner judgment is frozen.

===============================================================================
10. REQUIRED RETURN PACKET
===============================================================================

At completion output EXACTLY ONE `[RETURN PACKET]` and nothing after it.

It must contain:

PROJECT = AAA
PRODUCT = ASSET AGENT ASA
WORKSTREAM = AAA-ASA-ME
TASK = AAA_ASA_ME_ME2_SCENE_FREEZE_AND_P0_P1_SHADOW_v0.1

EXECUTION_VERDICT
EXACT_INPUT_REFS
EXACT_RESULT_BRANCH
EXACT_COMMITS
CONTAMINATION_LEDGER_STATUS
CURRENT_CYCLE_CLASSIFICATION
DECISION_SCENE_FREEZE_STATE
BLIND_QA_STATE
C01_C08_BRIEF_HASHES
ALIAS_CODEBOOK_STATE
P0_CONTEXT_INDEPENDENCE
P1_CONTEXT_INDEPENDENCE
P0_OUTPUT_FREEZE_STATE
P1_OUTPUT_FREEZE_STATE
PROXY_OUTPUT_HASHES
OWNER_BLIND_REVIEW_BUNDLE_PATH
OWNER_BLIND_REVIEW_READY = TRUE/FALSE
BLOCKING_ISSUES
KNOWN_LIMITATIONS
EXACT_GIT_WRITES
NEXT_RECOMMENDATION

Do not expose:
- Cxx↔Rxx mapping
- any old Track mapping
- current evaluator rank/score/preference result
- P0/P1 predicted Owner choice in the user-facing packet before Owner judgment

If Proxy outputs were successfully frozen, report only that their sealed outputs exist and their hashes/locators; keep prediction content sealed.

===============================================================================
11. FAIL-CLOSED CONDITIONS
===============================================================================

FAIL/CALIBRATION_HALT if:
- evaluator result content is opened before freeze;
- Owner current candidate preference is discovered before Proxy freeze;
- neutral briefs materially distort candidate semantics;
- alias codebook leaks into Proxy or Owner context;
- P0/P1 prediction context is not fresh/sanitized and independence cannot be proven;
- any Proxy output is modified after freeze without successor version/hash;

Do not rewrite historical frozen artifacts.
Do not promote method-calibration evidence to Independent Validation PASS.

===============================================================================
12. ROADMAP CONTINUATION
===============================================================================

If successful:
ME-0A = COMPLETE
ME-0B = COMPLETE
ME-1 = P0/P1 EXECUTABLE BASELINES COMPLETE; P2-P5 DEFERRED
ME-2 = QUASI_PROSPECTIVE SCENE FROZEN
ME-3A = P0/P1 PREDICTIONS FROZEN
ME-4A = OWNER INITIAL BLIND JUDGMENT NEXT
ME-5A = P0/P1 ↔ OWNER COMPARISON AFTER OWNER FREEZE
ME-6 = PANEL ABLATION LATER
ME-7 = MEMORY/INTERVIEW LEARNING CONTINUOUS

현재 상태: ODP-0 intake 완료 후 현재 8-position을 clean validation이 아닌 quasi-prospective method-calibration 장면으로 전환하는 다음 실행 패킷이다.
핵심 판단: ODP 권고에 따라 P0-P5를 한꺼번에 돌리지 않고 exact scene/receipt → P0/P1 → freeze → Owner blind review 순으로 진행한다.
진행 작업: 기존 blind input의 known leakage defect를 교정해 C01-C08 neutral brief를 새로 freeze하고, evaluator 결과를 봉인한 채 fresh P0/P1 baseline을 실행한다.
다음 단계: P0/P1 output이 봉인되면 Owner에게 동일한 C01-C08 blind bundle만 제시해 초기 판단을 freeze한다.
사용자 행동: 이 패킷을 새 Work 실행에 그대로 넣고, 완료 시 단일 `[RETURN PACKET]`만 이 ASA-ME 채널로 가져온다. 작성시각: 2026-08-21 16:36 KST
