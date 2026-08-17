# Asset Agent ASA contracts

These contracts are additive AAA execution-layer contracts. They do not replace the frozen SEMI schema registry.

## Invariants

- A Work Order is immutable after execution starts and is identified by `work_order_id + work_order_version + work_order_sha256`.
- Every Agent Run binds an exact repository/base commit and a permission level. MVP permission levels are limited to 0-2.
- Every Result Manifest binds its run, exact base, branch, changed files, tests, artifacts, hashes, blockers, and integration readiness.
- An implementation or engineering-validation run may not claim Independent Validation PASS.
- General agents may not perform canonical writes or authoritative adjudication.

Historical SEMI control assets remain authoritative during AAA shadow operation until a separately approved cutover.
