# AAA-ASA-ME Live Shadow Contamination Ledger v0.1

DATE = 2026-08-21 KST
PROJECT = AAA
PRODUCT = ASSET AGENT ASA
WORKSTREAM = AAA-ASA-ME
STATE = NON_NORMATIVE / LIVE_EXPERIMENT_CONTROL / APPEND-OR-SUCCESSOR_REQUIRED
BRANCH = asa-mi-owner-memo-20260821-1449

## Purpose

Record every known information exposure that could affect the current 8-position Owner Shadow classification. This ledger is experiment-control evidence, not a scientific or authority PASS.

## Classification scale

- `OPEN_ALLOWED`: allowed non-target-specific context.
- `CONTROLLED_EXPOSURE`: target-adjacent information observed; retain as contamination marker.
- `SEALED_VIOLATION`: information that reveals live evaluator preference/outcome or Owner blind answer before the relevant freeze.
- `UNKNOWN`: exposure cannot yet be reconstructed.

## Exposure records

### ME-CONTAM-0001

TIME = 2026-08-21 16:09~16:13 KST
SOURCE = channel succession packet / Git-backed preparation state
CLASS = OPEN_ALLOWED
CONTENT = AAA-ASA-ME purpose, P0–P5 proxy methodology, current cycle existence, aggregate pilot gate state, MI↔ME embargo rules, non-normative preparation lineage.
OUTCOME_INFORMATION = NONE beyond aggregate status already supplied by Owner succession packet.
EFFECT = permitted initialization context.

### ME-CONTAM-0002

TIME = 2026-08-21 approximately 16:12 KST
SOURCE = Git commit metadata for MI research HEAD `d50b73e91f3964626c060bd0165cbaa3371442c4`
CLASS = CONTROLLED_EXPOSURE
CONTENT = repository path/filename metadata exposed labels including `CANDIDATES/TRACK_A_A1.md` and `CANDIDATES/TRACK_A_A2.md` while verifying the exact MI research commit. The same metadata also confirmed that evaluated candidate bytes were frozen and a reference-only errata was added.
EVALUATOR_RANK_OR_SCORE_SEEN = FALSE
CHAMPION_LABEL_SEEN = FALSE
EVALUATOR_PREFERENCE_CONCLUSION_SEEN = FALSE
OWNER_BLIND_ANSWER_SEEN = FALSE
CANDIDATE_SUBSTANTIVE_CONTENT_SEEN = FALSE
EFFECT = track/path assignment metadata was observed even though it was not needed for Owner prediction. Treat as a contamination marker. It is not currently known to reveal preference/outcome, but it prevents pretending that initialization was exposure-free.

## Current implication

`CLEAN_PROSPECTIVE` is NOT currently proven.

Fail-closed preclassification remains:

`QUASI_PROSPECTIVE / METHOD_CALIBRATION`

This can be upgraded only if a later explicit leakage audit establishes that the observed track/path metadata is non-informative with respect to the target Owner judgment and that all other clean-held-out conditions passed. It must be downgraded if evaluator preference/outcome leakage or prior Owner candidate exposure is discovered.

## Next required audit items

- reconstruct exact Owner decision-scene cutoff;
- identify all information previously seen by Owner before blind review;
- prove whether any candidate documents/outcomes entered P0–P5 proxy-method design;
- identify neutral candidate presentation surfaces without opening evaluator result artifacts;
- continue logging any target-adjacent metadata exposure;
- do not reveal live evaluator ranks/scores/conclusions before Proxy and Owner freezes.

현재 상태: live-shadow contamination ledger를 시작했고, evaluator outcome은 보지 않았지만 MI commit metadata에서 일부 Track/path label 노출이 있었음을 명시적으로 기록했다.
핵심 판단: 이 노출만으로 held-out이 무효라고 단정할 수는 없지만 exposure-free를 주장할 수 없으므로 `QUASI_PROSPECTIVE / METHOD_CALIBRATION` 예비 분류를 유지한다.
진행 작업: exact cutoff·Owner prior exposure·proxy-design input·neutral candidate surface를 contamination audit 대상으로 남겼다.
다음 단계: ODP result intake와 ME-2 leakage finalization에서 본 ledger를 기준으로 CLEAN upgrade 또는 NOT_USABLE downgrade 여부를 판정한다.
사용자 행동: 현재 별도 조치가 필요 없으며, ODP 결과가 도착하면 원문 그대로 전달하면 된다. 작성시각: 2026-08-21 16:13 KST
