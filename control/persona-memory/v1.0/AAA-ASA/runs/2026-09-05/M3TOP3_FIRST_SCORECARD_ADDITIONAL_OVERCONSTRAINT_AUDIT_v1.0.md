# M3Top3 First-Scorecard Additional Overconstraint Audit v1.0

PROJECT = AAA
PRODUCT = ASSET AGENT ASA
PERSONA = AAA-ASA
DATE_KST = 2026-09-05
AUTHORITY_SOT = FALSE

## PURPOSE
Following Owner approval of six G2/G3 normalization policies, audit the remaining first-scorecard path for additional claim-only, provenance-only, future-reuse-only, optimization-only, or otherwise unnecessary hard blockers.

## CONFIRMED ADDITIONAL FINDINGS

1. G1 current model identity is materially more recoverable than prior blocker language implied. The v1.2 no-tune baseline lock already binds model objective, feature schema, scorer contract, weight version, validation contract, implementation repository/commit, config path/hash, source blobs, and an 18/18 synthetic contract test report. A bounded current readback/currentization is sufficient; no semantic reconstruction is presumptively required.

2. The exact v1 scorer implementation and config are present in Git history. The scorer explicitly supports missing features through available-weight renormalization. A company receives a score when at least one opportunity axis is available; official ranking coverage is based on rankable eligible companies, not completeness of every feature value. Therefore collecting all 17 historical annotation fields for all 1,016 company-window rows is not an execution necessity.

3. Historical annotation should be triaged into: available model-consumed features; explicit NA/missing features; and rows with no opportunity axis. The first two can score under existing semantics; the third may be excluded from a bounded first Replay under Owner's missing-as-missing direction, with explicit data-insufficient disposition and coverage reporting.

4. Full historical human/LLM outcome-access provenance or a sealed-clean-holdout proof is not necessary to produce a retrospective historical scorecard. If such proof is incomplete, the claim ceiling should be RETROSPECTIVE / NOT CLEAN OOS rather than blocking execution.

5. G4 exact-target runtime validation is already satisfied with nonblocking findings. Existing ENGV/CTLV/PMOV receipts include 261/261 unit, 75/75 matrix, 57/57 mutation, and 400/400 concurrency checks. The remaining Issue #51 packaging addendum affects future archived mutation-receipt reuse only and is explicitly nonblocking for the freshly executed current target. It should not block the first scorecard.

6. Full/global validation suites should not be rerun merely because G2/G3 denominator/calendar/manifest bindings are currentized. One affected-only validation of newly changed binding/data surfaces is the appropriate route unless runtime code changes.

7. EOPT optimization is an optimization lane, not a prerequisite to observe the first model scorecard. It should remain parked until after the first Replay unless measured runtime cost becomes an actual execution blocker.

8. Finance G11C9 HOLD is a separate provider/source-admission lane and must not be treated as a M3Top3 first-scorecard prerequisite.

9. The historical G2 34-cell documentary/raw-custody recovery and DRRV-F04 need not remain on the first-scorecard critical path for rows excluded by the approved unresolved-company-window rule. Evidence work is required only for included rows whose decision/feature actually depends on it.

10. Exact raw HTTP response headers/access-clock receipts are custody/audit metadata, not automatically PIT semantics. Where an authoritative stable source has an exact source/document identity, content digest, and explicit publication/effective timestamp, absence of historical access-clock/header capture should not by itself block a retrospective bounded Replay. Any relaxation must preserve the requirement that model-consumed facts be demonstrably available by cutoff.

11. G0/S0-S5 control text contains an over-coupling risk: model freeze is sometimes conditioned on dataset/price/CA readiness and replay reproducibility even though the state ladder intends semantic/code/config freeze before Golden/Replay. Model identity freeze should be separable from data readiness and performance validation; freezing the model creates no performance claim.

12. v0.2 Golden research package contains 20 fixtures. Five controlled fixtures lack independent expected model-output bindings (GF08, GF09, GF12, GF13, GF14), but these are controlled mechanical cases whose expected outputs can be independently bound from the already fixed scorer/config. This is a bounded mechanical task, not a historical-data blocker. Historical fixture dependencies can remain limited if the first scorecard is explicitly coverage-limited/retrospective.

13. The first observable scorecard should be separated from formal promotion status. A coverage-limited historical Replay can be produced with explicit exclusions/missingness and claim ceiling; S5 Champion/promotion, prospective confirmation, Forward Shadow, Release, and Production remain later gates and must not block seeing the first scorecard.

## PROPOSED SECOND NORMALIZATION DECISION SET

A. Permit a COVERAGE_LIMITED_RETROSPECTIVE_FIRST_REPLAY distinct from clean-OOS/official-promotion claims.
B. Do not require a full historical human/LLM outcome-access ledger before that first Replay; label the evidence status explicitly.
C. Apply the v1 scorer's existing missingness semantics: do not collect all 17 fields by default; collect what is available/needed, preserve NA, and exclude only company-window rows with no rankable opportunity axis/data sufficiency.
D. Park G4 Issue #51 portable archive packaging and prohibit full G4 reruns unless runtime target changes.
E. Park EOPT and Finance from the first-scorecard critical path.
F. Replace per-observation raw-header/access-clock hard requirements with authoritative source identity + digest + publication/effective time where those prove cutoff availability; keep fail-closed where cutoff availability cannot be proven.
G. Freeze current v1 model semantic/code/config identity independently from data readiness/performance validation.
H. Use the recovered v0.2 Golden package as a current mechanical test source; bind the five missing controlled expected outputs forward-only instead of recovering v0.1 or waiting on historical dependencies.
I. After rebaseline, run one affected-only validation campaign; no global/full-suite rerun absent runtime code mutation.
J. First scorecard does not require S5 Champion/promotion, prospective evidence, Forward Shadow, Release or Production.

## CLAIM CEILING
This audit proposes additional Owner decision surfaces. It does not itself change active governed gate semantics beyond the already-approved six G2/G3 policies.
