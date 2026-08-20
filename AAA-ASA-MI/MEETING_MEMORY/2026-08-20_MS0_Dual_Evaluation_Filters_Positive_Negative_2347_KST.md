# MS0 Dual Evaluation Filters — Positive / Negative

TIME = 2026-08-20 23:47 KST
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
- Model selection decision
- Validation receipt
- Owner acceptance

## 0. Owner direction

Owner requests two separate evaluation filters for model candidates:

1. negative-side evaluation
2. positive-side evaluation

The purpose is to prevent a one-sided research process in which:
- adversarial review sees only defects,
- constructive review sees only attractive possibilities,
- or a single aggregate score hides important asymmetry.

## 1. Core rule

Every serious model candidate should be evaluated through TWO INDEPENDENT LENSES before reconciliation.

NEGATIVE_FILTER
!=
POSITIVE_FILTER

Do NOT collapse them into one score too early.

A major strength does not automatically cancel a fatal flaw.
A serious flaw does not automatically erase a uniquely valuable capability.

## 2. NEGATIVE FILTER

Purpose:
Expose failure, distortion, brittleness, hidden assumptions, semantic overreach, implementation traps and irreversible commitments.

Questions include:
- What does this model fail to represent cleanly?
- Which current distinctions does it silently collapse?
- What ontology does it accidentally force?
- Which assumptions are added only for coding convenience?
- Where does it become unfalsifiable?
- Where does complexity explode?
- Which decisions become expensive to reverse?
- What historical/current semantic integrity risks appear?
- What human-familiar projection may hide structural discontinuity?
- What could make `별` difficult or misleading to implement?

Typical outputs:
- FAILURE
- DISTORTION
- HIDDEN_ASSUMPTION
- LOCK_IN_RISK
- IRREVERSIBILITY
- PERFORMANCE_RISK
- UNFALSIFIABILITY_RISK
- SEMANTIC_COLLAPSE
- OPEN_BLOCKER

## 3. POSITIVE FILTER

Purpose:
Identify genuine explanatory power, compression, expressive capacity, implementation leverage, generativity and unexpected fit.

This is NOT a cheerleading pass.
It must identify concrete reasons a model is valuable.

Questions include:
- What does this model express unusually naturally?
- Which previously separate research ideas become simpler or clearer?
- Does it reduce unnecessary primitives without semantic loss?
- Does it preserve OPEN/UNKNOWN states elegantly?
- Does it support change/history/currentization naturally?
- Does it offer useful multi-scale or multi-perspective behavior?
- Does it allow simpler executable probes?
- Does it make `별` easier to implement without premature ontology lock-in?
- Does it preserve human-familiar projections while retaining structural precision?
- Does it produce new useful questions or research directions?
- Does it reuse strong existing computational theory rather than inventing unnecessary machinery?

Typical outputs:
- EXPLANATORY_STRENGTH
- EXPRESSIVE_STRENGTH
- SEMANTIC_COMPRESSION
- IMPLEMENTATION_LEVERAGE
- REVERSIBILITY_STRENGTH
- EXTENSIBILITY
- GENERATIVE_VALUE
- HUMAN_FAMILIARITY_FIT
- REUSE_ADVANTAGE
- NEW_RESEARCH_AFFORDANCE

## 4. Isolation rule

Run the two passes separately enough that one does not answer the other while evaluating.

NEGATIVE pass should not say:
"This flaw is acceptable because the model has many strengths."

POSITIVE pass should not say:
"This strength does not matter because the model has a major flaw."

First preserve both bodies of evidence.
Only then perform reconciliation.

## 5. Reconciliation rule

After both filters complete, produce a paired summary rather than a single blended score.

Per candidate:

POSITIVE_PROFILE
NEGATIVE_PROFILE
NON_COMPENSATORY_FAILURES
UNIQUE_STRENGTHS
REVERSIBILITY
OPEN_QUESTIONS
CURRENT_RESEARCH_STATUS

Optional qualitative 2D placement:

A. HIGH POSITIVE / LOW NEGATIVE
- strong implementation/research candidate

B. HIGH POSITIVE / HIGH NEGATIVE
- high-upside / high-risk candidate
- preserve for research; do not average away the risk

C. LOW POSITIVE / LOW NEGATIVE
- coherent/safe but may offer little value over simpler alternatives

D. LOW POSITIVE / HIGH NEGATIVE
- likely drop/current-round counterexample candidate

These are routing categories only, not truth or validation states.

## 6. Application across MS0

This dual-filter discipline should not be limited to MS0-02.

Apply from MS0-01 onward where useful:

MS0-01 Divergence:
- Positive: why each family deserves serious consideration
- Negative: obvious structural risks / missing capability

MS0-02 Pressure Test:
- Negative filter receives full adversarial emphasis
- Positive filter explicitly records strengths exposed under pressure

MS0-03 Convergence / Synthesis:
- preserve both profiles when selecting or hybridizing
- do not erase strongest countermodel

Later executable stages:
- evaluate both failure behavior and enabling behavior

## 7. Meeting Memory requirement

Each Stage Meeting Memory should contain separate sections:

POSITIVE_FILTER_FINDINGS
NEGATIVE_FILTER_FINDINGS

Then:

RECONCILIATION
WHAT_CHANGED_IN_CURRENT_WEIGHTING
WHAT_REMAINS_OPEN

The meeting record must preserve cases where:
- a candidate is simultaneously very promising and very dangerous,
- a candidate is technically clean but conceptually weak,
- a candidate fails one dimension while uniquely solving another.

## 8. Critical anti-bias principle

POSITIVE_EVIDENCE != CONFIRMATION
NEGATIVE_EVIDENCE != REFUTATION

Both are inputs to current weighting.
Neither is final truth.

Do not force symmetry: a candidate may genuinely have many strengths and few weaknesses, or vice versa.

Do not force a single aggregate score.

## 9. Current status

This is an MS0 evaluation-design rule candidate derived from Owner direction.
It does not select a model and does not modify model semantics.

작성시각: 2026-08-20 23:47 KST
