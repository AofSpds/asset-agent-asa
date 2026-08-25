# M3Top3 FC1-G3 / G3-F exact blocked lineage envelope v0.1

```text
ISSUED_AT_KST = 2026-08-26T01:36:07+09:00
PARENT_WBS_ID = FC1-G3/G3-F
EXECUTION_ROLE = NON_VALIDATOR_WORKER
ARTIFACT_ROLE = FAIL_CLOSED_AUTHORING_CANDIDATE_NOT_A_RELEASE
STATUS = BLOCKED_LINEAGE_ENVELOPE_ONLY
VALIDATOR_HOLD = TRUE
GLOBAL_VALIDATION_OR_REGRESSION_RUN = FALSE
VALIDATION_LOOP_RUN = FALSE
PRICE_RETRIEVAL_OR_RECOMPUTATION_RUN = FALSE
SOURCE_MUTATION = FALSE
GIT_OR_ISSUE_MUTATION = FALSE
GATE_EFFECT = NONE
```

## 1. Result

This artifact represents every domain required by the sealed lineage contract
**exactly once**. It binds exact candidate/supporting hashes where those
identities already exist and records every missing release identity or authority
as missing. Supporting evidence is never promoted into a release reference.

The envelope is mechanically useful for future delta-only completion, but it is
not executable as a scoreable release. No new PASS, receipt, release, G3 closure,
or integrated G1-G4 checkpoint closure is created.

Contract anchor:

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `R_WP4_03_CANONICAL_LINEAGE_FULL_UNIVERSE_CONTRACT_v0.1.md` | 19,079 | `f6eab8c880c498c09c52aef1b1b30e37b94de7ada9e6fc00994b5b2e7df5b0b9` |

## 2. Eight required domains — exactly once

| # | Required domain | Exact current state | Exact identity already bindable | Missing identity / authority that blocks admission |
|---:|---|---|---|---|
| 1 | `UNIVERSE_RELEASE` | `EXACT_CANDIDATE_NOT_FINAL` | U127 candidate: 14,667 bytes, SHA-256 `6a7c40b2a8bd52353a944f108dd556bf1dc05a520926aebb6d1bca4ae3b48f7c` | final release ID/revision; independent expectation manifest; row genesis/applicability authority; authority receipt |
| 2 | `DENOMINATOR_ELIGIBILITY_RELEASE` | `ABSENT_COMPLETE_RELEASE / 514 UNRESOLVED` | closure queue: 325,454 bytes, SHA-256 `02bde437c04b1cc3d314b30e9bdd41bdb9a9164d0d2df4468728bdab8089eb62`; this is not a release | terminal full-U E/I partition; independent expectation manifest; set/partition digests; final manifest/receipt |
| 3 | `FEATURE_SOURCE_RELEASE` | `ABSENT_RELEASE / FAIL_CLOSED_QUEUE_ONLY` | queue SHA-256 `e5f9d9ff2a10bb47ab92826646b53c6754a84f4942c866cdd510a8828b338b7f`; registry `3ee7db8f...8612`; schema `cea40640...e836` | historical source bytes; feature `publication_at`; cutoff-safe receipts; access/concealment and annotation lineage; exact-v1 admission; final manifest/receipt |
| 4 | `PRICE_RELEASE` | `EXACT_FORWARD_COMPONENT_BYTES / RELEASE IDENTITY NOT BOUND` | exact 2024/2025/2026 component hashes listed below | admitted release ID/version/revision; release-manifest hash; stable component-set digest; authority receipt; governed forward cutover or predecessor bytes |
| 5 | `CORPORATE_ACTION_RELEASE` | `PROTOCOL CANDIDATE ONLY / B-C OPEN` | protocol candidate: 20,374 bytes, SHA-256 `42c60cdafbc1b504a3113512c5a2ac9ad8e728a18e5173853fec3ad2ba923250` | governed Axis-B threshold; independent KRX event artifact; Axis-C taxonomy/scope/exhaustion; zero-unresolved release; manifest/receipt |
| 6 | `TRADING_CALENDAR_RELEASE` | `ABSENT GOVERNED RELEASE` | protocol candidate SHA-256 `42c60cda...3250`; raw price-date counts are diagnostic only | official KRX regular-session bytes or designated equivalent; derivation profile; independent expectation manifest; zero source conflicts; manifest/receipt |
| 7 | `WINDOW_REGISTRY_RELEASE` | `EXACT 8-ROW CANDIDATE / DATE PROVENANCE OPEN` | 414 bytes, SHA-256 `96d63cc98a01b6332cf9486440e7f3fdaa0ec5a2d605f21bc14a4025b46e69fe` | upstream tuple artifact/hash/locators; outcome-free authority binding; holdout/OOS authority; final release/receipt |
| 8 | `SCORER_RELEASE` | `ABSENT EXACT PRE-OUTCOME V1 / G1 BLOCKED` | none | exact scorer and config bytes/hashes; model/feature/build identity; exact pre-outcome-v1 manifest; authority receipt |

The machine-readable JSON preserves the required release-reference fields for
each domain. Unknown or missing values are `null` or explicit blocked states;
they are never represented as zero.

## 3. Exact price custody and manifest boundary

No price bytes were retrieved, decoded, rescanned, or recomputed for this
envelope. It reuses the completed recovery evidence only.

| Component | Upstream Git blob | Bytes | SHA-256 |
|---|---|---:|---|
| `data/marcap-2024.parquet` | `b69c5222d015c81f19f90f581faabe4dd1a919b4` | 24,572,111 | `b0c38943e67637d5faf88429880092cf0f46a394be39860dd3bcd0b04231bccb` |
| `data/marcap-2025.parquet` | `e817f0729b787fe03904982a37b1d84d26d70206` | 25,153,419 | `2bfd93c217eb74263bc5020b23fa6debb6b02531c11eaccc2826639bc191559e` |
| `data/marcap-2026.parquet` through 2026-08-14 | `3921c090c0c9336e2ab8d068a4546aec26595665` | 16,297,737 | `b6f3f8ea110326b21d23b5344e6abe159f8ea7f7a345262155b929c08886fc9d` |

The controlling upstream commit is
`5e8e4e57f3fcb129a6ff20751f643f67d3592c82`. The completed forward recovery
evidence is 5,209 bytes with SHA-256
`4bbcd2b6e580fffeda32483048c1a43c6cdd16d736c59c6bda1609a8e14ecbdd`.
It declares a new forward recovery manifest, but does not supply all mandatory
fields of an admitted `PRICE_RELEASE` reference.

The predecessor workbook declares expected standalone-manifest SHA-256
`56d36d51e9f7b8870aa75cc41ee241603f6cf7446cb2386187c6ebcbb88b73c4`
and simultaneously records `NOT_RECOMPUTED_NO_MANIFEST_FILE`. The manifest
bytes remain `NOT_FOUND`; byte identity remains `NOT_PROVEN`. The 763-byte
legacy import manifest at SHA-256
`ca8f117a83cd3da800a2a2b5e0ebdca3c89ff658ff3fd21b5083e4aae9ab98ce`
is `MISMATCH_NOT_SUBSTITUTED`.

## 4. D/E and G2 blocker bindings

G3-D supplies only a price-side mechanical join input:

- 1,016 company-window rows;
- Entry Open/tradability `979 TRUE / 37 FALSE / 0 mismatch`;
- historical state `465 ELIGIBLE / 37 INELIGIBLE_BY_TRADABILITY / 514 UNRESOLVED`;
- exact summary SHA-256
  `14906157e5071aec2d2e333ffd1f6a31d5c90092f4577494e90f7fc780dce289`.

G2 still has `514` business-priority unresolved rows, of which `469` also lack
listing provenance. Its blocker-decision JSON is 11,322 bytes with SHA-256
`e248f9f2a05f98809e3266995f5f0badf431da3b42aea538a0a72f27156ce87b`.
Positive Entry Open does not resolve either fact.

G3-E contributes a safe queue, not historical feature evidence:

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| field registry | 16,035 | `3ee7db8fe7ad265e9909821b608829d05c02edf88bfa8937d3c5f91f74278612` |
| ingest schema | 22,683 | `cea40640ba9258116d82ce957cf9f3cb1d3b6b79373f95cdcec1a5d72265e836` |
| 1,016-row ingest queue | 6,080,457 | `e5f9d9ff2a10bb47ab92826646b53c6754a84f4942c866cdd510a8828b338b7f` |

All `17,272` feature slots remain fail-closed. Admitted annotation values,
feature-level publication times, and source receipts are all zero in count
because they are absent—not because unknowns were coerced into zero-valued
features.

## 5. Bundle-level blockers

The following remain missing across the envelope:

1. all eight admitted release references with complete IDs, manifests,
   component-set identities, dates/revisions, and authority receipts;
2. independently supplied Universe and denominator expectation manifests;
3. exact `U/E/I` sets and partition digests;
4. one-to-one row-level `dataset_refs` for every applicable row type;
5. timezone/date/revision/status/window coherence across released artifacts;
6. exact scorer artifact/config identity; and
7. an external binding of the final lineage-envelope bytes.

The JSON deliberately does not self-embed its own hash. Its exact SHA-256 must
be bound externally after the single targeted structural readback.

## 6. Structural-check boundary

Exactly one targeted local single-pass structural check is authorized after the
MD and JSON are authored. Its scope is limited to:

- JSON parsing;
- eight domain records, exact allowlist, uniqueness, and ordinal order;
- all eight `release_admitted=false` under this blocked envelope;
- top-level blocked/no-gate/no-release invariants; and
- output byte sizes and SHA-256 identities.

It is not a validator act, global validation, full regression, price scan,
release test, or validation loop. There is no automatic retry.

## 7. EWU, time, compute, and gate effect

```text
FROZEN_BASELINE_UNIT = FC1-G3/G3-F
FROZEN_BASELINE_WEIGHT = 4 EWU
EARNED_EWU_DELTA_RECORDED_BY_WORKER = 0
RECOMMENDATION_ONLY = PMO may award at most +1 EWU for bounded authoring evidence
CREDIT_ASSUMED = FALSE
GATE_CLOSURE_CREDIT = 0
GATE_EFFECT = NONE

PLANNED_WORKER_P50 = 0.25-0.50 h
PLANNED_WORKER_P90 = 0.75-1.00 h
TIMING_CONFIDENCE = MEDIUM
CRU_PROXY = 2-4
EXTERNAL_WAIT_INCLUDED = FALSE
VALIDATOR_TIME_INCLUDED = FALSE
TRUE_SCOREABLE_G3_RELEASE_ETA = NOT_MEASURABLE_FROM_CURRENT_INPUTS
```

## 8. Claim ceiling

- No new PASS or validation receipt.
- No G3 or integrated-checkpoint closure.
- No eligibility, annotation, CA, calendar, scorer, or denominator truth claim.
- No predecessor-manifest substitution or forward cutover authorization.
- No score, rank, Top-K, return, Golden, Replay, Freeze, Champion, EOPT-G0,
  promotion, release, production, predictive-power, or optimization claim.
- Existing sealed receipts remain intact only within their original exact scope
  and were not rerun.
