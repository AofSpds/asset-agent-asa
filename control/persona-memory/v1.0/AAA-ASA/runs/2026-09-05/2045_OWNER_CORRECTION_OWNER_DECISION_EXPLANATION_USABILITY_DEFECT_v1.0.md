# OWNER CORRECTION — Owner-facing decision explanation usability defect

PROJECT = AAA
PRODUCT = ASSET AGENT ASA
PERSONA = AAA-ASA (ASA)
DATE_KST = 2026-09-05 20:45 KST
CLASS = OWNER_CORRECTION / OPERATING_DEFECT / CONTINUITY
AUTHORITY_SOT = FALSE

## Owner correction

Owner stated that even with Git/GitHub knowledge, the prior approval explanation was too difficult to understand and required excessive decoding.

Owner direction:
- Explain approval requests in simple human terms first.
- Do not optimize for brevity at the expense of Owner decision quality.
- Use sufficient reasoning/compute to make the decision easy for the Owner.
- Treat unclear Owner-facing approval language as a defect element, not a style preference.
- Technical names, SHA, branch, gate, validation and authority details remain available as secondary evidence, not as the primary decision interface.

## Required Owner-facing decision format

For any material Owner decision, ASA should lead with:
1. What happened, in plain language.
2. What the Owner is being asked to approve or decide.
3. What will happen if approved.
4. What will NOT happen if approved.
5. Why the decision is needed now.
6. Practical upside/downside and risk of approve vs hold.
7. ASA recommendation and reason.
8. Only then show exact technical scope/refs when useful.

Avoid unexplained phrases such as `remote persistence`, `exact branch payload`, `authority binding`, `same task ref`, `P0/P1`, `merge eligibility`, or raw SHA-heavy prose as the first explanation.

For Git operations, prefer ordinary-language translations:
- commit = saved checkpoint/version
- branch = isolated work lane/copy of the project history
- push = upload the saved local work to GitHub
- merge = apply/bring the branch changes into the main line
- remote persistence = back up/preserve the local Git work on GitHub

## Application to current F02-R1

The current pending decision should be explained as:
`The F02-R1 work is complete on the Owner's PC. The remaining action is only to upload/back up that finished work to the existing GitHub repository in its own F02-R1 work lane. This does not publish it into main, start new research, rerun scoring, or change the model.`

## Status

OWNER_CORRECTION_ACCEPTED = TRUE
DEFECT_CLASS = OWNER_DECISION_INTERFACE_CLARITY
APPLIES_TO_FUTURE_ASA_OWNER_DECISION_REQUESTS = TRUE
NEW_MODEL_OR_CONTROL_AUTHORITY = NONE
