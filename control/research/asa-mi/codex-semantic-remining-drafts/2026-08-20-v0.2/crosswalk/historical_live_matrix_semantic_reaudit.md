# Historical/live matrix semantic re-audit

## Receipt

```text
PASS_ID = HISTORICAL-LIVE-MATRIX-REAUDIT
START_TIME = 2026-08-20T09:47:45+09:00
END_TIME = 2026-08-20T09:49:40+09:00
ACTIVE_REVIEW_SECONDS = 115
ROWS_REVIEWED = 62
ROWS_RETAINED = 60
```

Every matrix row was reread for endpoint fidelity, comparison class, current-activity claim, duplicate comparison, and accidental `RESOLVED` semantics. Two duplicate endpoint pairs were removed rather than retained as differently worded count: historical minimal-standpoint versus live Current Status models, and historical multidimensional continuity versus live realism/fidelity.

Fifteen rows were retargeted from corrected v0.1/live predecessors to their v0.2 successors where the comparison depended on corrected wording. Two classifications/analyses were also narrowed after successor review: self-model evaluation versus self-model construction is `SCOPE_CHANGED`, not a clean refinement; multidimensional continuity and perceived-realism warnings `COEXIST` rather than one refining the other.

The retained 60 rows have unique IDs, unique endpoint pairs, permitted comparison classes, and no `RESOLVED` claim. Absence from current discussion remains distinct from rejection.
