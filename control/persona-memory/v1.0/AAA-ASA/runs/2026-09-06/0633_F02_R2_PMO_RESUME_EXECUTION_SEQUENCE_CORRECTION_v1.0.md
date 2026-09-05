# F02-R2 PMO RESUME — EXECUTE-THEN-REVIEW SEQUENCE CORRECTION

PROJECT = AAA
PRODUCT = ASSET AGENT ASA
FROM_PERSONA = AAA-ASA (ASA)
TARGET_PERSONA = AAA-PMO-ORCHESTRATOR (PMO)
DATE_KST = 2026-09-06 06:33 KST
CLASS = OWNER_AUTHORIZED_EXECUTION_SEQUENCE_CORRECTION
AUTHORITY_SOT = FALSE

OWNER_RESUME_CORRECTION_COMMIT = 47c9f4ccaeef02d896fd491decd0e813997a1c51
OWNER_RESUME_CORRECTION_PATH = control/persona-memory/v1.0/AAA-ASA/runs/2026-09-06/0632_OWNER_RESUME_F02_R2_EXECUTE_THEN_REVIEW_TOKEN_EFFICIENT_CORRECTION_v1.0.md
PRIOR_EXECUTION_REQUEST = control/persona-memory/v1.0/AAA-ASA/runs/2026-09-06/0614_M3TOP3_F02_R2_OWNER_AUTHORIZED_PMO_EXECUTION_REQUEST_v1.0.md

RESUME = AUTHORIZED
NO_RERUN = TRUE
REPEAT_OWNER_APPROVAL = FALSE

## PMO instruction

Read the 0632 Owner resume correction first. Preserve all target/source/semantic/PIT/ceiling/no-main boundaries from the 0614 execution request, but replace the old validation-before-score sequencing with:

1. MINIMAL SAFETY PRECHECK ONLY
2. 52-COMPANY CENSUS
3. BATCH SOURCE ACQUISITION / EXTRACTION
4. TIME-BOXED EXCEPTION HANDLING
5. CREATE PROVISIONAL EXPANDED F02 CANDIDATE
6. BIND EXISTING F05-R1 WITHOUT RERUN
7. FREEZE CANDIDATE BUNDLE
8. CONSOLIDATED POST-EXECUTION VALIDATION
9. AFFECTED-ONLY CORRECTION / REVALIDATION IF NEEDED
10. REPORT / SEAL / TASK-BRANCH PERSISTENCE

Do not run full multi-role independent validation merely as a prerequisite to create the provisional candidate.

Use full-cohort deterministic checks plus exception/high-risk/system-level independent review. Normal issuer raw documents should not be reread from scratch by every validator.

Token-efficiency controls from 0632 are mandatory operating guidance for this run: one-time source custody where possible, local deterministic parsing first, compact evidence rows, exact slices for LLM/validator, no validator-of-validator narrative loop, no full-bundle repeated read unless conflict requires it.

If local unpushed work was created before Owner stop, inspect and continue from it; do not discard or reacquire completed sources without evidence of corruption.

Timebox guidance:
- approximately 2h: prioritize candidate freeze over marginal exceptions;
- approximately 3h: normally close unresolved low-yield issuer exceptions as PARTIAL/NOT_FOUND and move to consolidated validation/closure;
- do not chase the superseded 5h/12h wall solely for coverage.

STOP only at the Owner-reserved boundaries already defined. Routine source/layout/parser/control defects are recorded, corrected within scope, and affected-only revalidated without Owner interruption.
