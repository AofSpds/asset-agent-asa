# M3Top3 Owner Direction — Iterative Missing-Data Completion and Bounded Estimation Policy v1.0

PROJECT = AAA
PRODUCT = ASSET AGENT ASA
CURRENT_PERSONA_LOCK = AAA-ASA (ASA)
DATE_KST = 2026-09-05 11:09 KST
RECORD_CLASS = OWNER_DIRECTION / CONTINUITY / NON_NORMATIVE_UNTIL_BOUND_IN_EXECUTION_SPEC
AUTHORITY_SOT = FALSE

## Owner direction

Owner direction received in chat:

> 비어 있는 부분을 모델 평가를 통해 필요한 부분만 보완해 나가는 부분으로 하고 어느 정도는 추정으로 채우는것도 생각해볼만 합니다. 이건 완벽할 수 없는 기획이었어요.

Interpretation:
- Do not require exhaustive completion of every historical field before useful model evaluation.
- Use iterative evaluation to identify which missing inputs materially limit scoreability/diagnostic value, then backfill only the high-value gaps.
- Bounded estimation/inference may be considered where exact historical facts cannot reasonably be recovered.
- The project is inherently imperfect; the operating objective is decision-useful, transparently qualified evidence rather than unattainable perfect reconstruction.

## Scientific-integrity boundary

This direction does NOT by itself authorize:
- relabeling estimates/inference as observed historical facts;
- using future outcomes to fabricate or choose historical feature values for the same confirmatory v1 replay;
- silently changing v1 feature/scorer/weight semantics;
- claiming clean OOS/complete-universe/production validation from an estimated-input replay.

Recommended data-state taxonomy for the successor design:
1. OBSERVED_PIT_FACT — directly cutoff-safe observed fact with source/provenance.
2. DERIVED_PIT — deterministic derivation from cutoff-safe observed facts.
3. ESTIMATED_PIT / INFERRED_PIT — bounded estimate from cutoff-safe context, with method, confidence, and uncertainty/sensitivity disclosure.
4. MISSING — no defensible value.

Recommended evaluation surfaces:
- STRICT scorecard: OBSERVED_PIT_FACT + DERIVED_PIT only.
- PRAGMATIC scorecard: STRICT + explicitly labeled ESTIMATED/INFERRED inputs.
- SENSITIVITY envelope: show whether ranking materially changes across plausible estimate bounds.

Prioritization rule:
- Before outcome inspection for a given replay target, prioritize missing-data recovery using scoreability, current fixed model weights, feature/axis coverage, and sensitivity/value-of-information — not realized winners/returns.
- After outcomes have been inspected, further targeted backfill may continue as exploratory diagnostic work, but the resulting evidence must not be represented as a clean untouched baseline validation.

## Current implication

The next PMO design should not reopen exhaustive G2/G3 closure. It should connect real feature inputs, classify available data by the four states above, generate a nonempty strict replay where possible, and use bounded estimation only where necessary and explicitly disclosed. Missing-data work should be demand-driven by scoreability and sensitivity rather than blanket 1,016 x all-field completion.

OWNER_ACTION_REQUIRED = FALSE for documenting this direction.
NEXT = incorporate into the next PMO execution/design packet before estimated inputs are actually admitted to scoring.
