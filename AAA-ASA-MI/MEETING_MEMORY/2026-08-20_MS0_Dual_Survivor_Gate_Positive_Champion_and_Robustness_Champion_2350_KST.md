# MS0 Dual Survivor Gate — Positive Champion + Robustness Champion

TIME = 2026-08-20 23:50 KST
STATE = WORKING_RESEARCH_MEMORY / MS0_EVALUATION_DESIGN / NON_NORMATIVE

PROJECT CONTEXT =
- World Model naming candidate: 한알
- MS0 working milestone name: ONTOGENESIS
- MS0 narrative codename: FIAT LUX / 빛이 있으라
- First implementation artifact naming candidate: 별
- 별 current meaning: first implementation artifact only

NOT:
- Requirement
- Design Contract
- Canonical ontology
- Final model selection
- Validation receipt
- Owner acceptance

## 0. Owner correction

MS0 SHOULD NOT collapse the Positive Filter and Negative Filter into one winner.

The Owner wants two intentionally different survivors:

1. the model with the greatest positive potential / strongest advantages,
2. the model with the smallest negative surface / fewest serious weaknesses.

Both should pass forward.

This is a deliberate dual-survivor design, not a temporary tie.

## 1. Two independent selection tracks

### TRACK P — POSITIVE CHAMPION

Select the candidate that creates the greatest positive value.

Evaluate especially:
- explanatory power,
- expressive power,
- ability to preserve or illuminate current worldview hypotheses,
- useful conceptual compression,
- discovery of new modeling possibilities,
- capacity to generate useful research questions,
- elegance where it produces real leverage,
- implementation leverage,
- extensibility,
- capacity to support future `별` experiments,
- potential to reveal structures not previously visible.

The Positive Champion is NOT required to have the fewest weaknesses.

A candidate may be high-positive / high-negative and still become the Positive Champion if its downside is not immediately disqualifying.

### TRACK N — ROBUSTNESS CHAMPION

Select the candidate with the smallest serious negative surface.

Evaluate especially:
- fewest hidden semantic assumptions,
- lowest ontology lock-in,
- highest reversibility,
- lowest semantic distortion,
- bounded computational complexity,
- implementation simplicity,
- stable treatment of uncertainty/history/change,
- low migration cost,
- low God-Object risk,
- low unfalsifiability risk,
- ability to fail safely and transparently.

The Robustness Champion is NOT required to have the greatest explanatory ambition.

A model that is conservative, simple, and easy to reverse may be intentionally preserved even if it is less expressive.

## 2. Minimum cross-gates

The two tracks are independent, but neither candidate may pass purely by optimizing one axis while completely failing the other.

Therefore:

POSITIVE CHAMPION must satisfy a MINIMUM NEGATIVE GATE:
- no known fatal contradiction with the current research posture,
- no unavoidable irreversible ontology commitment without explicit review,
- no implementation path that is clearly infeasible for `별`,
- known severe risks must be explicitly bounded or testable.

ROBUSTNESS CHAMPION must satisfy a MINIMUM POSITIVE GATE:
- must be capable of expressing enough of the current research problem to be informative,
- must provide a meaningful implementation path for `별`,
- must not be merely a trivial persistence/state container that avoids all hard questions by omitting them,
- must produce non-zero research value beyond being easy to implement.

These are viability gates, not score balancing.

## 3. No averaging

Do NOT compute:

TOTAL = POSITIVE_SCORE - NEGATIVE_SCORE

or any equivalent single composite winner metric by default.

In particular:

HIGH POSITIVE + HIGH NEGATIVE
MUST NOT
be averaged into MEDIUM.

LOW NEGATIVE + MODEST POSITIVE
MUST NOT
be treated as equivalent to HIGH POSITIVE + HIGH NEGATIVE.

The two profiles represent different research assets.

## 4. Expected MS0 survivor output

At the relevant selection gate, MS0 should attempt to produce:

POSITIVE_CHAMPION = <candidate>
ROBUSTNESS_CHAMPION = <candidate>

Both proceed to the next stage.

They may be different models.

If the same model wins both tracks, do NOT automatically collapse to one survivor. Preserve the strongest distinct runner-up that occupies the other side of the tradeoff frontier when a serious alternative exists.

Reason:
MS0 benefits from maintaining a meaningful contrast into implementation pressure rather than proving one model too early.

## 5. Next-stage handling

The two selected models should initially continue separately.

Do NOT immediately hybridize them.

For each model preserve:
- its own assumptions,
- its own strengths,
- its own failure surface,
- its own conceptual vocabulary,
- its own implementation consequences.

Only after both have undergone comparable deeper tests should synthesis/hybridization be considered.

Premature hybridization can hide why each model was valuable.

## 6. `별` implication — OPEN but important

A likely future experimental pattern is:

- `별-P` = a first implementation artifact informed by the Positive Champion,
- `별-R` = a first implementation artifact informed by the Robustness Champion,

or another equivalent paired implementation strategy.

However this is NOT yet fixed.

`별` remains the naming candidate for the first implementation artifact, and whether there will be one or two `별` implementations is an OPEN design decision for later MS0 stages / Owner review.

## 7. Required reporting

For each track report independently:

### Positive Champion report
- strongest unique advantages,
- what becomes possible that other candidates do not enable,
- positive discoveries,
- major remaining downside,
- minimum-negative-gate result.

### Robustness Champion report
- avoided failure modes,
- assumptions not required,
- reversibility strengths,
- simplicity/implementation advantages,
- major capability sacrificed,
- minimum-positive-gate result.

Then produce a separate:

DUAL_SURVIVOR_COMPARISON

without declaring either globally superior.

## 8. Research interpretation

The intent is not compromise.

The intent is to preserve two different optimization philosophies:

- MAXIMIZE DISCOVERY / UPSIDE,
- MINIMIZE DISTORTION / DOWNSIDE.

Both are useful experimental baselines for the first 한알 implementations.

## 9. Current status

This is working MS0 evaluation design only.
No candidate has yet been selected.
No `별` implementation has been authorized or created by this note.

작성시각: 2026-08-20 23:50 KST
