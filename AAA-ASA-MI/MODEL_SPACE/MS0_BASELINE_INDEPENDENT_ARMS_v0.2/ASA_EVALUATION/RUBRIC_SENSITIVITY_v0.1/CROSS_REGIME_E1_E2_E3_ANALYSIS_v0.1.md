# Cross-Regime E1/E2/E3 Rubric Sensitivity Analysis v0.1

PROJECT = AAA
PRODUCT = ASSET AGENT ASA
WORKSTREAM = AAA-ASA-MI
AUTHOR = AAA-ASA / ASA-MI
AUTHORING_STATE = ADVISORY_ANALYSIS
PAIRED_VALIDATION_STATE = NOT_PERFORMED
INDEPENDENT_VALIDATION_STATE = NOT_PERFORMED
OWNER_ACCEPTANCE_STATE = NOT_REQUESTED
CANONICALITY = NONE
MODEL_POOL_0_CLAIM = NONE

## Exact evaluation target

EVALUATION_POOL_ID = AAA_ASA_MI_BASELINE_6_FINALISTS_EVAL_SNAPSHOT_v0.1

Candidates remain separate exact targets:
- ARM-A D4 LPCW
- ARM-A D1 AHCK
- ARM-B D2 TRCC
- ARM-B D1 CCP
- ARM-C D3 CCRA
- ARM-C D1 WLRF

No merge, admission, or canonicalization is implied by this analysis.

## Regime definitions

- E1 = MINIMAL_COMMITMENT_ROBUSTNESS
- E2 = NATIVE_CONSEQUENCE_GENERATIVITY
- E3 = NON_GLOBALITY_CONTEXT_PLURALISM

All three used the same six-candidate snapshot and a 70% common core plus a 30% regime-specific lens.

## Observed rankings

### E1
1. AHCK = 90.0
2. WLRF = 87.5
3. LPCW = 86.5
4. CCP = 85.0
5. TRCC = 84.5
6. CCRA = 82.5

E1 explicitly treated WLRF/LPCW as an effective tie band and CCP/TRCC as another effective tie band.

### E2
1. TRCC = 95.8
2. WLRF = 93.6
3. AHCK = 91.4
4. CCRA = 89.0
5. LPCW = 84.3
6. CCP = 83.3

### E3
1. CCRA = 96.0
2. CCP = 95.5
3. LPCW = 95.0
4. AHCK = 87.5
5. TRCC = 86.5
6. WLRF = 81.0

## Primary finding

RUBRIC_SELECTION_PRESSURE = STRONG

The same frozen candidate pool produces three different TOP-1 candidates under three intentionally different but only partially shifted evaluation regimes:

- E1 -> AHCK
- E2 -> TRCC
- E3 -> CCRA

No candidate wins more than one of E1/E2/E3.

This establishes that evaluation design materially affects candidate selection. It does NOT establish that the earlier baseline convergence was caused primarily by the rubric, because the candidate-generation ARMs themselves shared a common execution packet, problem framing, and pressure vocabulary.

## Top-3 overlap

Using strict score order for descriptive comparison:

- E1 TOP3 = {AHCK, WLRF, LPCW}
- E2 TOP3 = {TRCC, WLRF, AHCK}
- E3 TOP3 = {CCRA, CCP, LPCW}

Top-3 Jaccard overlap:
- E1 vs E2 = 0.50
- E1 vs E3 = 0.20
- E2 vs E3 = 0.00

The zero E2/E3 TOP3 overlap is the strongest current evidence that the generativity and context-pluralism lenses apply materially different selection pressure.

## Descriptive rank correlation

Using E1 effective-tie average ranks and ordinary E2/E3 ranks, descriptive Spearman correlations are approximately:

- E1 vs E2 = +0.15
- E1 vs E3 = -0.56
- E2 vs E3 = -0.77

N = 6 is too small for these values to be treated as inferential statistics. They are descriptive diagnostics only.

## Semantic-family interpretation

### E2 strongly selects witnessed/generative rewrite

E2 TOP2:
- TRCC
- WLRF

Both provide typed/structured local transformation, explicit preservation/non-persistence, causal witness history, conflict/concurrency, and replay. E2 therefore selects the F2 witnessed/generative-change family rather than one isolated ARM-specific name.

### E3 strongly selects contextual/local-to-global constitution

E3 TOP3:
- CCRA
- CCP
- LPCW

All three are independently generated variants of the contextual/non-global compatibility family. E3 therefore selects the F1 contextual-constitution family as a block.

### E1 selects a generalist rather than either specialized family winner

AHCK is E1 TOP1 while remaining E2 rank 3 and E3 rank 4. Its total-score range across E1/E2/E3 is only 3.9 points, much smaller than the specialized candidates:

- AHCK range = 3.9
- LPCW range = 10.7
- TRCC range = 11.3
- CCP range = 12.2
- WLRF range = 12.6
- CCRA range = 13.5

CURRENT_INTERPRETATION = AHCK behaves like a relatively rubric-stable generalist, while rewrite and contextual candidates behave like stronger specialists whose ranking moves sharply with the evaluation lens.

This is not a superiority claim.

## Pareto observation

Across the three regime totals, none of the six candidates is strictly dominated by another candidate on all E1/E2/E3 scores.

THREE_REGIME_PARETO_FRONTIER = ALL_SIX_CANDIDATES

This is a strong argument against premature elimination at this stage and supports temporary model-pool management rather than forced single-winner selection.

## Common-core halo / interpretation confound

The common-core score itself was independently rescored in each regime, so this experiment measures:

REGIME_EFFECT = WEIGHT/LENS EFFECT + EVALUATOR_INTERPRETATION/HALO EFFECT

It is not a pure mathematical reweighting experiment.

Observed common-core range across E1/E2/E3:
- LPCW = 4.3 / 70
- CCP = 3.2 / 70
- CCRA = 2.5 / 70
- AHCK = 2.0 / 70
- WLRF = 2.0 / 70
- TRCC = 1.5 / 70

However, a post-hoc diagnostic using each candidate's mean E1/E2/E3 common-core score and reattaching each regime-specific 30-point score preserves the headline regime winners:

- E1 fixed-core diagnostic -> AHCK remains #1
- E2 fixed-core diagnostic -> TRCC remains #1
- E3 fixed-core diagnostic -> CCRA remains #1

The E1 CCP/TRCC internal order changes, but E1 had already classified them as an effective tie band. Therefore the headline rubric-sensitivity result is not explained only by common-core halo drift.

IMPORTANT: this fixed-core diagnostic is post-hoc ASA analysis and must NOT be injected into future isolated evaluators before their runs.

## Updated interpretation of the earlier two-job attractor

The baseline cross-ARM result suggested a strong two-job attractor:

A. CONTEXTUAL_CONSTITUTION / NON_GLOBAL_COMPATIBILITY
B. GENERATIVE_CHANGE / CAUSAL_REPLAY

E1/E2/E3 now refine that interpretation:

- E2 confirms B as a genuine selection attractor under generativity.
- E3 confirms A as a genuine selection attractor under non-global/context plurality.
- E1 surfaces AHCK as a third robust-generalist position that neither specialist lens selects first.

Therefore the evidence currently supports a THREE-POSITION RESEARCH FRONTIER rather than a final two-kernel architecture:

1. CONTEXTUAL / GLUING / NON-GLOBAL SPECIALISTS
2. WITNESSED REWRITE / CAUSAL CHANGE SPECIALISTS
3. ADMISSIBLE-HISTORY / CONSTRAINT GENERALIST

This does not mean three kernels are required. It means the evaluation experiment has not justified collapsing these positions yet.

## What can and cannot be concluded

SUPPORTED:
- Evaluation criteria materially alter rankings.
- E2 and E3 apply strongly different selection pressure.
- Semantic families, not just individual names, respond coherently to matching lenses.
- AHCK is comparatively rank-stable across these three lenses.
- No candidate is three-regime Pareto-dominated.

NOT_SUPPORTED:
- RUBRIC_INDUCED_CONVERGENCE is the sole or primary cause of baseline convergence.
- Any candidate is canonical.
- The two-job architecture is false.
- AHCK is the final general solution.
- E2 or E3 specialist winners are superior outside their regime.

## Recommended continuation

Continue E4-E9 using the same exact six-candidate snapshot and preserve evaluator isolation.

Do NOT change the common-core protocol mid-series merely because E1-E3 revealed common-core halo drift; doing so would make E4-E9 non-comparable to E1-E3.

Instead, after all nine regimes complete:

1. preserve every raw regime ranking;
2. compute candidate-level and semantic-family-level convergence;
3. compute TOP1 frequency, TOP3 overlap, rank correlations, and Pareto survival;
4. perform a post-hoc fixed-common-core sensitivity analysis using a frozen aggregation rule;
5. distinguish regime-specific specialists from cross-regime generalists;
6. only then decide whether the pool should be normalized into MODEL_POOL_0.

FORMAL_VALIDATION_CLAIM = NONE
MODEL_ADMISSION_CLAIM = NONE
CANONICALITY_CLAIM = NONE
