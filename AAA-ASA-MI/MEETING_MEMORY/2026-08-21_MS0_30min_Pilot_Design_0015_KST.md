# MS0 30-Minute Pilot Design

TIME = 2026-08-21 00:15 KST
STATE = WORKING_RESEARCH_MEMORY / PILOT_DESIGN / NON_NORMATIVE

PROJECT = AAA
WORKSTREAM = AAA-ASA-MI
WORLD_MODEL_NAME = 한알
MILESTONE = MS0 — ONTOGENESIS / FIAT LUX
FIRST_IMPLEMENTATION_ARTIFACT_NAME = 별

NOT:
- Requirement
- Design Contract
- Canonical ontology
- Model selection decision
- Validation receipt
- Owner acceptance

## Owner request

Run a short approximately 30-minute pilot before the full MS0 execution so the Owner can inspect the quality and direction before sleeping.

The pilot is intended to answer whether the planned Codex workflow is behaving usefully, not to answer the World Model question itself.

## Pilot objective

Test whether a Codex execution worker can, under a hard short budget:
1. reconstruct enough of the current AAA-ASA-MI context without collapsing OPEN questions into commitments,
2. generate 8 genuinely different model-family seeds rather than cosmetic variants,
3. apply a lightweight common viability pressure pass,
4. record BOTH positive and negative observations independently,
5. produce pilot-only provisional Positive and Robustness representatives,
6. preserve a useful meeting memory and handoff without claiming semantic authority.

## Why 30 minutes is useful

The full MS0 is expected to be long. A short pilot can expose early process failures such as:
- context reconstruction loss,
- ontology being inferred from names,
- eight candidates being superficial variants,
- over-long analysis of the first candidate,
- positive/negative filters being averaged together,
- poor meeting-memory quality,
- failure to respect OPEN / non-definition,
- inability to checkpoint and close under time pressure.

## Hard timebox

TOTAL_WALL_CLOCK_BUDGET = 30 minutes

Suggested allocation:
- 0–5 min: repository/context preflight and compact context reconstruction
- 5–17 min: generate 8 candidate seeds with distinctness checks
- 17–25 min: lightweight common pressure pass + independent positive/negative observations on all candidates
- 25–28 min: choose PILOT-ONLY provisional Positive representative and Robustness representative
- 28–30 min: mandatory closure, meeting memory, artifact inventory, commit/push attempt, RETURN PACKET

The last 2 minutes are reserved for closure even if research is incomplete.

## Pilot non-contamination rule

PILOT_RESULT != MS0_RESULT
PILOT_FINALIST != MS0_FINALIST
PILOT_RANKING != FUTURE_PRIOR

The full MS0 must not inherit pilot rankings as presumptive weights merely because they were generated first.

Pilot candidates and rankings may be reused only as research evidence with explicit provenance, not as privileged starting truth.

## Pilot candidate requirement

TARGET_CANDIDATES = 8

Each candidate seed should be short but serious and include:
- unique candidate ID,
- one-sentence thesis,
- computational/formal family or shape,
- what it treats as primary if anything,
- at least one current candidate concept it demotes/removes/reinterprets,
- strongest apparent upside,
- strongest apparent downside,
- why it is materially different from the other seeds.

Do not create eight variants of the same state/event/graph model merely to satisfy the count.

If fewer than 8 genuinely distinct candidates can be produced in time, report the exact count and why rather than fabricating weak candidates.

## Lightweight pilot common pressure pass

This is NOT the full MS0-02 Main Round.

For each candidate, quickly inspect:
- basic internal coherence,
- change/history representability,
- non-closure / unknown-state handling or explicit alternative,
- bounded toy implementability,
- visible assumptions / reversibility,
- obvious hidden ontology lock-in,
- obvious falsifiability problem,
- obvious dependence on Persona/ASA-specific semantics.

Use compact findings. Do not spend the pilot trying to prove a candidate correct.

## Dual filter behavior

For every candidate preserve two independent sections:

POSITIVE_PILOT_FINDING = what this candidate makes unusually possible or simpler.
NEGATIVE_PILOT_FINDING = what this candidate risks, distorts, hides, or makes expensive.

Do not average them into one score.

## Pilot-only representatives

Among candidates that appear minimally viable under the lightweight pass, choose:
- PILOT_POSITIVE_REP = highest observed upside
- PILOT_ROBUSTNESS_REP = lowest observed downside while remaining non-trivial

Prefer distinct candidates.
If the same candidate leads both axes, record that fact and name the strongest distinct alternate only if genuinely viable.

These labels are explicitly ephemeral and do not advance a model into the real MS0 Final Round.

## Budget governor

- hard stop at 30 minutes,
- do not spend >2 minutes deeply analyzing any one seed before all 8 seeds exist,
- after minute 20, no new conceptual rabbit holes; record OPEN and continue,
- after minute 25, no new candidates; complete comparison and closure,
- at minute 28, mandatory closure mode regardless of research state,
- sufficient evidence for a pilot observation is enough; do not chase completeness,
- if Owner sends a steer such as “적당히 해 / close now”, immediately preserve current evidence and enter closure mode.

## Write-scope safety

The pilot must not mutate existing MS0 research notes, requirements, design contracts, canonical artifacts, or unrelated files.

New pilot artifacts should live under a dedicated pilot path plus one new Meeting Memory where appropriate.

Existing files are read-only context.

## Expected pilot outputs

1. COMPACT_CONTEXT_RECONSTRUCTION
2. EIGHT_CANDIDATE_SEED_TABLE or explicit shortfall
3. LIGHTWEIGHT_PRESSURE_MATRIX
4. POSITIVE_AND_NEGATIVE_FINDINGS for all candidates
5. PILOT_POSITIVE_REP
6. PILOT_ROBUSTNESS_REP
7. OPEN_QUESTIONS / PROCESS_FAILURES
8. PILOT_MEETING_MEMORY
9. Git artifact/commit/push status
10. exactly one [RETURN PACKET]

## Success criteria

Pilot succeeds if it demonstrates the process is useful and controllable, even if no candidate is compelling.

A useful failure is also success if it clearly identifies why the full MS0 process needs adjustment.

## Next use

Owner can inspect the pilot before sleeping and choose one of:
- proceed with full MS0 unchanged,
- change the candidate generation instructions,
- change the common pressure gate,
- change the positive/negative filters,
- reduce or increase budget,
- run another pilot.

작성시각: 2026-08-21 00:15 KST
