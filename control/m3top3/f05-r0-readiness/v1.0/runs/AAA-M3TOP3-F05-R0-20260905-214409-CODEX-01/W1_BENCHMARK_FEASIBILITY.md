# W1 57-company benchmark feasibility

- Run ID: `AAA-M3TOP3-F05-R0-20260905-214409-CODEX-01`
- Disposition: `DECISION_REQUIRED`
- Exact starting denominator: 57 W1 `INCLUDE` companies
- Current-universe substitution: prohibited and not performed
- 46-company SEMI-universe substitution: prohibited and not performed
- `EXCLUDE_PROVEN` added: 0
- `EXCLUDE_UNRESOLVED` added: 0

## Availability versus governed calculability

| Measure | Result | Meaning |
|---|---:|---|
| Exact W1 starting members | 57 | Bound historical same-snapshot denominator. |
| Raw pre-cutoff price rows | 8,607 | 57 companies × 151 common market dates through 2024-08-09. |
| At least 21 distinct positive-close observations | 57/57 | Availability diagnostic only. |
| At least 61 distinct positive-close observations | 57/57 | Availability diagnostic only. |
| Volume / Amount / Stocks value-ready in the common 61-date window | 57/57 each | Raw-column readiness only; the runtime adapter gap remains. |
| Missing common market-date rows / duplicate Date+Code groups | 0 / 0 | No observed raw-row denominator loss in the tested window. |
| Heuristic-discontinuity-clear, without proving CA absence | 55/57 | No configured heuristic trigger in the tested window; this is not `NO_CA`. |
| `CA_OR_PRICE_DISCONTINUITY_REVIEW_REQUIRED_HEURISTIC_ONLY` | 2/57 | GST and 엑시콘; three bounded heuristic boundaries. |
| Raw-input-ready companies | 57/57 | The bound bytes are broadly usable for later construction after decisions. |
| Safely F05-calculable now under exact governed upstream semantics | 0/57 | D1-D6 are all partial; this is a semantic gate, not a missing-data count. |

## Denominator analysis

The denominator must start from the exact historical W1 population object: `INCLUDE 57 / EXCLUDE_PROVEN 8 / EXCLUDE_UNRESOLVED 62`. All 57 members have identical raw market-date coverage over the common 61-date diagnostic window, so this particular raw extract does not force a missing-row divisor decision.

That empirical completeness does not create a governed rule. D3 and D6 do not specify equal-weight aggregation, synchronization, or the divisor behavior if a member is missing, suspended, or pending CA review. Two members are in that last category. Removing them would silently change 57 to 55; keeping or adjusting them without a governed comparable-price basis would also invent semantics. Neither action is allowed in F05-R0.

## Bounded CA/discontinuity impact

- GST (`KRX:083450`): raw Close changed 43,300 to 21,600 from 2024-06-25 to 2024-06-26 (`-50.115473%`), while Stocks was unchanged; Stocks then changed 9,317,745 to 18,618,260 from 2024-07-23 to 2024-07-24 (`+99.815084%`). The two boundaries may not be linked without evidence.
- 엑시콘 (`KRX:092870`): Stocks changed 10,848,797 to 13,050,797 from 2024-07-30 to 2024-07-31 (`+20.297181%`), while Close changed only `+2.858744%`.
- The raw source has no corporate-action flag or adjustment-factor field. No applicable governed pre-cutoff CA receipt or factor was recovered.

The other 55 members are classified `NO_HEURISTIC_TRIGGER_IN_TESTED_WINDOW__CA_ABSENCE_NOT_PROVEN`, not `NO_CA`.

## Conclusion

`RAW_MEMBER_AVAILABILITY = 57/57`

`GOVERNED_BENCHMARK_CONSTRUCTION = DECISION_REQUIRED`

No return or benchmark number was calculated. A narrow decision must first close D1-D6 and adjudicate the two CA-review companies; F05-R1 then requires separate authorization.
