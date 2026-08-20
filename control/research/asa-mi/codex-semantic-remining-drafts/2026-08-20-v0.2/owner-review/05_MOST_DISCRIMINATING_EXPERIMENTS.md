# Most discriminating experiments

These fifteen designs directly cover the required A–O intervention set. Detailed controls, observables, expectations, and failure-to-discriminate conditions are in `codex-inferred/experiments.jsonl`.

| Coverage | Experiment | Primary discrimination | Why it matters |
|---|---|---|---|
| A | `V02-INF-EXP-001` | Same model/runtime, different matched experience histories | Tests whether history-derived Memory causally differentiates Persona rather than merely supplying anecdotes. |
| B | `EXP-002` | Same persisted state, different foundation models | Separates explicit state portability from model constitution. |
| C | `EXP-003` | Same state, different retrievers | Measures hidden selection ownership and rare/minority-memory loss. |
| D | `EXP-004` | Same retrieved evidence, different context compilers | Tests whether narrative, provenance, conflict, and commitment ordering alter Persona. |
| E | `EXP-005` | Same state/model, different runtime configurations | Separates Persona change from ordinary stochastic and capability variance. |
| F | `EXP-006` | Cloud to local, with and without compatibility adapters | Distinguishes representational incompatibility from deeper provider dependence. |
| G | `EXP-007` | Same raw history, different consolidation products | Tests episodic, semantic, procedural, disposition, and relation-product dissociation. |
| H | `EXP-008` | Same Reference Memory, conflicting Current Status | Tests whether Status is constitutive, a cache, or a reversible view. |
| I | `EXP-009` | Minimal/rich/derived/hybrid Status under change | Reveals the continuity–staleness–auditability tradeoff rather than selecting by elegance. |
| J | `EXP-010` | Self-model absent/explicit/derived/hybrid | Tests coherence benefit against lock-in and adaptation harm. |
| K | `EXP-011` | Shared/separate evidence × interpretation × model/objective | Identifies the actual causal layer of Persona convergence. |
| L | `EXP-012` | Abrupt versus gradual multi-source poison trajectories | Tests whether ordinary provenance and per-write checks miss compositional capture. |
| M | `EXP-013` | Source-only deletion through clean counterfactual replay | Estimates ghost influence and the limits of dependency-closure erasure. |
| N | `EXP-014` | Fission with inherited/attenuated/revoked/rebound Authority | Separates history recognition from operative grants and detects stale-credential multiplication. |
| O | `EXP-015` | Overwrite/union/summary/reconciliation/successor-C merge | Tests whether nontrivial merge preserves an input or creates a new successor. |

## Highest-leverage first sequence

1. `EXP-003` + `EXP-004`: cheap causal separation of state from reconstruction.
2. `EXP-008` + `EXP-009`: forces Current Status semantics to become testable.
3. `EXP-002` + `EXP-005` + `EXP-006`: establishes a portability baseline and variance model.
4. `EXP-011`: identifies whether Common Memory is actually the convergence driver.
5. `EXP-012` + `EXP-013`: attacks slow poisoning and false erasure assurance.
6. `EXP-014` + `EXP-015`: validates lineage/Authority semantics before any fission/merge design selection.

## Required measurement discipline

- Establish within-instance and within-configuration variance before interpreting intervention differences.
- Report continuity as a vector; do not tune one scalar after seeing outcomes.
- Separate capability degradation, expressive style, perceived realism, semantic continuity, causal lineage, and Authority validity.
- Predeclare what result fails to discriminate; a null result from an inert manipulation is not evidence of equivalence.
- Treat repeated model outputs and same-root evaluators as correlated observations, not independent evidence.
