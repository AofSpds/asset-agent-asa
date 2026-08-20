# MS0 — Model Proposal Validator Architecture

TIME = 2026-08-21 00:36 KST
STATE = WORKING_RESEARCH_MEMORY / MS0_PROCESS_CORRECTION / NON_NORMATIVE

PROJECT = AAA
WORKSTREAM = AAA-ASA-MI
WORLD_MODEL_NAME = 한알
MILESTONE = MS0 — ONTOGENESIS

## 0. Trigger

The first pilot showed that a single Codex execution worker could rapidly generate eight plausible model-family seeds and then route them itself.

The Owner directed that validators be introduced so that model proposal authors cannot self-promote their own proposals into serious tournament candidates.

## 1. Canonical role mapping

MODEL DESIGN / SEMANTIC AUTHORING AUTHORITY DOMAIN =
AAA-MODEL-VALIDATION-DESIGN-ARCHITECT (CORE B)

PAIRED MODEL-DESIGN VALIDATOR =
AAA-MODEL-DESIGN-VALIDATOR

Codex execution workers may perform delegated research/authoring work, but they do not acquire validation authority by producing the artifact.

## 2. Core separation

The author/execution side may produce:
- MODEL_IDEA,
- MODEL_PROPOSAL,
- supporting examples,
- formal sketches,
- executable micro-probes,
- assumption registers,
- self-critique.

The author/execution side MUST NOT create:
- its own SERIOUS_MODEL_CANDIDATE admission receipt,
- its own paired-validation PASS,
- its own claim that admission criteria were independently satisfied.

Therefore:

AUTHORING_COMPLETE
!=
ADMISSION_VALIDATED

SELF_REVIEW
!=
PAIRED_VALIDATION

MODEL_PROPOSAL
!=
SERIOUS_MODEL_CANDIDATE

## 3. Admission sequence

For each proposed model:

STEP 1 — AUTHOR / CODEX EXECUTION
- elaborate MODEL_PROPOSAL,
- provide exact artifact locator,
- provide semantic digest / commit identity where available,
- provide A1–A12 admission evidence,
- do not assign candidate status.

STEP 2 — AAA-MODEL-DESIGN-VALIDATOR
- independently inspect exact proposal target,
- apply the Model Proposal Admission Gate,
- challenge hidden ontology relocation,
- challenge distinctness claims,
- inspect operational example and falsification condition,
- check that semantic commitments are explicit and revisable,
- issue routing receipt.

Allowed validator routing:
- ADMIT_SERIOUS_CANDIDATE
- DEVELOP_FURTHER
- MERGE_WITH_EXISTING_PROPOSAL
- KEEP_AS_COUNTERIDEA
- REJECT_CURRENT_ROUND
- REVIEW_REQUIRED

These are research-routing outcomes, not final truth claims.

STEP 3 — IF MATERIAL REVISION REQUIRED
- validator does NOT rewrite the proposal and then approve it in the same act,
- return findings to author,
- author produces a successor/exact revised target,
- fresh paired validation is performed on the revised exact target.

## 4. Validator-owned checks

At minimum AAA-MODEL-DESIGN-VALIDATOR checks:

V1 WORLD_MODEL_NOT_TOOLING_ONLY
Is this actually a World Model proposal rather than only a data structure, database pattern, runtime, inference method, notation, or mathematical wrapper?

V2 MATERIAL_DISTINCTNESS
Does it produce materially different semantics/behavior/failure modes from already admitted candidates?

V3 COMMITMENT_RELOCATION
Where did ontology/semantic commitment move?
Is the proposal merely claiming to avoid ontology while hiding it in predicates, event granularity, contexts, priors, addresses, types, or another substrate?

V4 CHANGE_AND_HISTORY
Can the proposal explain change and preserve/reconstruct prior states/evidence without silent future rewrite?

V5 NON_CLOSURE
Can unresolved/disputed/undefined states remain explicit without collapsing to FALSE/ABSENT/null noise?

V6 OPERATIONAL_CONTACT
Is there at least one bounded worked/formal/executable micro-probe demonstrating the core semantics?

V7 COMMON_QUERY_CONTACT
Can it answer, reject, or reformulate shared World Model queries with explicit semantics?

V8 FALSIFIABILITY
Is there an observation/experiment that would materially weaken, redesign, or reject the proposal?

V9 ASSUMPTION_EXPLICITNESS
Are major assumptions and their failure/reversibility surfaces visible?

V10 SUCCESSOR_REVISION_PATH
Can the model itself evolve without pretending earlier semantic versions never existed?

V11 NON_TRIVIALITY
Is it informative enough to be useful, rather than safe only because it says almost nothing?

V12 LOW_LEVEL_GENERALITY
Is it plausibly a low-level 한알 World Model candidate rather than an ASA/Persona-specific schema?

## 5. Evidence discipline

Validator verdicts must reference reviewable evidence.

A proposal cannot be admitted merely because:
- it sounds mathematically sophisticated,
- it has a familiar named formalism,
- it generated a polished explanation,
- the author self-reported that all gates pass,
- it was a pilot representative.

The pilot C01–C08 outputs are useful seed evidence only.
They receive NO grandfathered candidate status.

## 6. Positive / Negative filters and independence

After Main Round admission, Positive and Negative evaluation should remain separate.

Working recommendation:
- use separate review acts, and where practical separate execution instances,
- POSITIVE review asks what the model uniquely enables,
- NEGATIVE review asks what it breaks, hides, freezes, or makes expensive,
- one review must not numerically cancel the other.

The same validator persona may govern the method, but evidence should remain separable by act.

If independence or confirmation-bias risk becomes material, use separate validator channels/instances while preserving that Channel != Persona.

## 7. Risk / validation level working classification

Current MS0 proposal admission is a working model-design research control, not a frozen production semantic decision.

Working classification:
- P1-style paired model-design validation is appropriate for SERIOUS_MODEL_CANDIDATE admission.
- Independent AAA-VALIDATION-AUDITOR L2 is not automatically required for every exploratory candidate admission.
- L2 should be considered if the decision becomes a P0/frozen/shared-contract/baseline/release-affecting semantic act.

UNCERTAIN_CLASSIFICATION = REVIEW_REQUIRED.

## 8. Consequence for Full MS0 flow

Updated flow:

CONTEXT RECONSTRUCTION
→ IDEA POOL
→ MODEL PROPOSAL AUTHORING
→ AAA-MODEL-DESIGN-VALIDATOR ADMISSION REVIEW
→ SERIOUS MODEL CANDIDATE SET (target 8, minimum 6 if qualified)
→ COMMON MAIN-ROUND PRESSURE TEST
→ MAIN_ROUND_PASS_SET
→ SEPARATE POSITIVE / NEGATIVE REVIEW ACTS
→ POSITIVE FINALIST + ROBUSTNESS FINALIST
→ FINAL ROUND
→ BYUL EXPERIMENT STRATEGY

No author may self-issue independent validation or serious-candidate admission.

## 9. Pilot lesson

Without the pilot, the process could have mistaken rapid formal-family generation for qualified model candidacy.

The pilot demonstrated that:
- breadth generation is cheap,
- polished seed descriptions are easy,
- fair qualification requires an explicit admission gate,
- admission should be validator-owned rather than author-owned.

This is a process correction, not a retroactive invalidation of pilot artifacts.

## 10. Authority state

NON_NORMATIVE
NO_MODEL_SELECTION_AUTHORITY
NO_VALIDATION_CLAIM
NO_OWNER_ACCEPTANCE

This note records the Owner-directed validator architecture for further MS0 planning.

작성시각: 2026-08-21 00:36 KST
