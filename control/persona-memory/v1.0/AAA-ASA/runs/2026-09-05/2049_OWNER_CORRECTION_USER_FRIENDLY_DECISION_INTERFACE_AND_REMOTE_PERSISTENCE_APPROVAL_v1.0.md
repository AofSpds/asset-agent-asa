# OWNER CORRECTION + APPROVAL — User-friendly decision interface / F02-R1 remote preservation

PROJECT = AAA
PRODUCT = ASSET AGENT ASA
PERSONA = AAA-ASA (ASA)
DATE_KST = 2026-09-05 20:49 KST
CLASS = OWNER_CORRECTION / OWNER_DECISION / CONTINUITY_RECEIPT
AUTHORITY_SOT = FALSE

## 1. Owner correction — decision interface quality

OWNER_DIRECTION = 철저히 유저 친화적으로 설명할 것.

Owner explicitly identifies the following as a defect class:
- requiring the Owner to reconstruct what an acronym/task means before making a decision;
- leading with Git/governance jargon instead of the business/research meaning;
- causing the Owner to spend unnecessary cognitive effort to decode an approval request;
- technically accurate but decision-hostile explanations that increase human error risk.

Operating correction for ASA and successor Owner-facing explanations:
1. Explain the object/task itself first in plain language: what it is, why it exists, and where it sits in the larger program.
2. State the current situation in ordinary language before Git/persona/authority terminology.
3. State exactly what decision is being requested.
4. Explain what will happen if approved.
5. Explain what will NOT happen if approved.
6. Explain approve/hold consequences and material risks.
7. Provide ASA recommendation and rationale when a recommendation is admissible.
8. Put branch/SHA/pointer/validation terminology after the decision explanation, as supporting detail.
9. Do not save assistant compute at the expense of Owner comprehension. Owner cognitive load and decision error risk are first-class quality metrics.
10. If the Owner must infer the meaning of the task name/acronym from prior context, treat the explanation as incomplete.

This is a UX/control correction, not a change to model/PIT/validation semantics.

## 2. F02-R1 reminder in human terms

F02 is the M3Top3 feature that asks whether a company's realized business numbers, currently revenue and operating profit in the bounded profile, are improving relative to a comparable prior period.
F02-R1 is the first repair/generalization step that made the real-input path work for multiple companies rather than only the original Dongjin Semichem example. The reported result increased W1 F02-scoreable companies from 1/57 to 5/57. It is not the full M3Top3 model, not official Top3, and not a model-performance PASS.

## 3. Owner approval — remote preservation only

OWNER_DECISION = APPROVE
OWNER_TEXT = 승인합니다. 다음 프로세스 준비하세요.

Approved action in plain language:
Copy the already-completed F02-R1 result bundle from the local PC Git state to GitHub for safe backup/recovery, without changing the research result or starting more research.

Exact approved destination:
REPOSITORY = AofSpds/asset-agent-asa
TASK_BRANCH = task/aaa/m3top3-f02-r1-multi-company-input-repair-20260905

Approved payload scope:
- final F02-R1 code changes within the previously approved bounded engineering surface;
- official source bytes already acquired for the run;
- source/input mapping and manifests;
- feature sidecar;
- process ledgers/checkpoints/progress artifacts;
- validation receipts/report;
- score/seal outputs;
- F02_R1_COMPLETION_REPORT;
- PMO run journal and final persistence/readback artifacts.

Explicitly NOT authorized by this approval:
- rerun of source discovery or scoring;
- new company/window/feature expansion;
- model weight/feature/scorer/ranking/PIT/eligibility semantic change;
- main mutation, merge, PR merge, release or production;
- new provider, credential, paid source or budget;
- force push or history rewrite.

Required closure condition:
- identify exact local report-containing final commit/tree;
- push that exact result to the same named task branch on the existing origin;
- read back remote branch HEAD;
- prove remote branch HEAD equals local final HEAD;
- report main unchanged and no additional execution.

REPEAT_OWNER_APPROVAL_REQUIRED = FALSE for this exact remote-preservation act.

## 4. Next-process preparation direction

Owner additionally directs ASA to prepare the next process.
ASA shall not automatically launch a new research batch merely because F02-R1 completed. First compare the next candidate steps by expected contribution to reliable Top3 discrimination, data readiness, acquisition cost, semantic risk, and reuse of already internalized data. Prepare an Owner-facing recommendation in plain language before any new bounded execution authorization is requested.

CURRENT_STATE = F02-R1 local functional completion reported; remote preservation approved; next-process design authorized, next research execution not yet authorized by this receipt.
