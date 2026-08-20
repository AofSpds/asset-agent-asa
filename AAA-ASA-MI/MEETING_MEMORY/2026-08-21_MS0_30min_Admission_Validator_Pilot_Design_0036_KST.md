# MS0 — 30-Minute Model Proposal Admission + Validator Pilot Design

TIME = 2026-08-21 00:36 KST
STATE = WORKING_RESEARCH_MEMORY / PILOT_DESIGN / NON_NORMATIVE

PROJECT = AAA
WORKSTREAM = AAA-ASA-MI
WORLD_MODEL_NAME = 한알
MILESTONE = MS0 — ONTOGENESIS

## 0. Trigger

The first 30-minute pilot generated eight polished model-family seeds in 7m54s. The Owner identified two process failures:

1. MODEL_IDEA was being promoted too quickly toward candidate-like status.
2. The same execution worker generated and routed its own model proposals.

The Owner directed that model proposal admission use explicit qualification criteria and a separate validator.

## 1. Pilot objective

This second pilot tests the funnel and admission architecture, not the final model tournament.

Target process:

IDEA_POOL
→ MODEL_PROPOSAL AUTHORING
→ EXACT TARGET COMMIT
→ FRESH AAA-MODEL-DESIGN-VALIDATOR REVIEW
→ ADMISSION ROUTING

No author may self-promote a proposal to SERIOUS_MODEL_CANDIDATE.

## 2. Pilot execution topology

Recommended 30 focused minutes:

- 10–12 min AUTHORING INSTANCE
  - generate a broad idea pool,
  - select up to 4 materially different ideas for proposal elaboration,
  - complete A1–A12 evidence where possible,
  - create one bounded micro-probe per proposal,
  - commit exact proposal bundle,
  - produce a validator handoff packet,
  - STOP; no self-validation.

- 15–17 min FRESH VALIDATOR INSTANCE
  - persona lock = AAA-MODEL-DESIGN-VALIDATOR,
  - review exact committed proposal bundle,
  - apply V1–V12 independently,
  - issue one routing result per proposal,
  - no proposal rewriting in the same validation act.

- 3 min CLOSURE
  - process review,
  - meeting memory,
  - Git persistence,
  - return packet.

If a fresh independent validator worker cannot be created inside the execution environment, the authoring instance must STOP after producing exactly one validator handoff packet for a new Codex instance. Self-validation is prohibited.

## 3. Depth-over-count correction

This pilot does NOT attempt to create 8 serious candidates.

Targets:
- IDEA_POOL_TARGET = 10–16
- MODEL_PROPOSAL_TARGET = up to 4
- SERIOUS_MODEL_CANDIDATE_COUNT = validator-determined, possibly 0

A proposal may be submitted to validation only if the author can provide reviewable evidence for the Admission Gate. If time expires, incomplete ideas remain MODEL_IDEA or MODEL_PROPOSAL_NOT_READY rather than being padded into admission-ready artifacts.

## 4. Admission standard

The existing A1–A12 Model Proposal Admission Gate applies:

A1 WORLD_MODEL_THESIS
A2 MATERIAL_DISTINCTNESS
A3 COMMITMENT_SURFACE_EXPLICITNESS
A4 CHANGE_HISTORY_SEMANTICS
A5 NON_CLOSURE_SEMANTICS
A6 BOUNDED_OPERATIONALIZATION
A7 COMMON_QUERY_CONTACT
A8 FALSIFICATION_ABANDONMENT_CONDITION
A9 ASSUMPTION_REGISTER
A10 REVISION_SUCCESSOR_PATH
A11 NON_TRIVIALITY
A12 LOW_LEVEL_GENERALITY

Admission rule:

ADMIT_SERIOUS_CANDIDATE requires evidence-supported satisfaction of ALL mandatory gates.

Any mandatory gate that is materially NOT_PROVEN prevents admission in that act.

## 5. Validator ownership

Validator persona = AAA-MODEL-DESIGN-VALIDATOR.

Validator reviews exact immutable proposal targets using V1–V12 and may route:

ADMIT_SERIOUS_CANDIDATE
DEVELOP_FURTHER
MERGE_WITH_EXISTING_PROPOSAL
KEEP_AS_COUNTERIDEA
REJECT_CURRENT_ROUND
REVIEW_REQUIRED

The validator must not materially rewrite a proposal and approve that rewrite in the same act.

Material revision:
AUTHOR REWORK
→ NEW EXACT TARGET
→ FRESH VALIDATION

## 6. Anti-bias controls

- Pilot C01–C08 rankings remain quarantined historical observations.
- C04/C05 representative status from Pilot 1 must not be used as prior ranking evidence.
- The proposer may reuse known model families only if independently re-elaborated; no grandfathered candidate status.
- The validator should not see private author reasoning; only reviewable artifacts and evidence.
- Proposal polish, mathematical sophistication, named formalism familiarity, or author self-confidence are not admission evidence.

## 7. Early-completion correction

The previous pilot interpreted the 30-minute budget as a maximum and completed once output fields were filled.

This pilot therefore defines MINIMUM WORK UNITS rather than minimum wall-clock consumption.

Author cannot declare authoring complete until either:
- up to 4 proposals each have full required evidence + micro-probe, OR
- the author explicitly records which proposals are NOT_READY and why.

Validator cannot declare validation complete until every submitted exact proposal has an individual V1–V12 review or is explicitly VALIDATION_INCOMPLETE due to time.

No aggregate matrix may substitute for per-proposal evidence.

Time should not be wasted to fill the clock, but completion requires evidentiary depth rather than template completion.

## 8. Success criteria

Pilot success does NOT require any proposal to be admitted.

Success means:
- the funnel distinguishes idea from proposal from candidate,
- self-validation is prevented,
- exact-target validation is demonstrated,
- the validator rejects/develops/admits based on evidence rather than elegance,
- the process reveals realistic proposal-development and admission cost,
- Full MS0 can be updated based on measured bottlenecks.

## 9. Authority state

NON_NORMATIVE
NO_FINAL_MODEL_SELECTION
NO_INDEPENDENT_VALIDATION_CLAIM
NO_OWNER_ACCEPTANCE

This is a process pilot design for MS0 research.

작성시각: 2026-08-21 00:36 KST
