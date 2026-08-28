# New-endpoint de-duplication and layer audit

## Receipt

```text
PASS_ID = NEW-ENDPOINT-DEDUP-01
START_TIME = 2026-08-20T09:39:35+09:00
END_TIME = 2026-08-20T09:40:18+09:00
ACTIVE_REVIEW_SECONDS = 43
SOURCE_DERIVED_ENDPOINTS = 25
LIVE_ENDPOINTS = 32
```

All 57 newly recovered endpoints were reread statement-by-statement and compared across and within provenance layers. No endpoint is a count-inflating paraphrase. Two pairs are close enough to record only as `POSSIBLE_SEMANTIC_EQUIVALENCE`: reclassification/non-invalidation and non-materialized SELF/self-model. They remain separate because one member is a historical normalized recovery and the other is a live research record, and their scopes differ.

Two further cross-layer relations survived: live unknown-versus-zero semantics refine the broader historical uncertainty-state rule, while historical causal/longitudinal evaluation constraints coexist with the live four-axis candidate evaluation model. None of these relations transfers source status, truth, or Owner authority.
