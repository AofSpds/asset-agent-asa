# ME-2 Blind Brief Manifest v0.1

## Brief Receipts

| Candidate | SHA-256 | Bytes | Common sections | Deterministic token scan |
|---|---:|---:|---:|---|
| C01 | e61540aa2dee41d4579039c60cddadaa6d70298ac371137b0615a4ef8100b276 | 7,397 | 11 | PASS |
| C02 | 6658374c8d308574c0800a71c58193bd0d9f081b12bd3ad92d57eb5ca680b751 | 6,975 | 11 | PASS |
| C03 | 7888bc7fa3e3a61b4a718c576cc0c6dbb1b5459338227a350e060a5539392475 | 7,505 | 11 | PASS |
| C04 | 8435265cc6944508fb2843246fb4d2f1c5f476ac4ab323dde8a71dc7c54267e2 | 6,465 | 11 | PASS |
| C05 | b4a98bf954fb16e25cd81fe925474ee80dd702576a7c7baabb4b9eff458608d2 | 6,586 | 11 | PASS |
| C06 | 9ef9f44f00f368082bc8439766c813d7d7f28a54a174ad05b3d31433d95d117c | 6,836 | 11 | PASS |
| C07 | e23c0919c82dc5fecb91b9c40be34fb898f207273dbc3a6f954405bbc7c7c8ee | 6,830 | 11 | PASS |
| C08 | 7eeeae8c223ac71305eab78c21b668ffda285e8a1c08ce24d00b601f98be304d | 7,024 | 11 | PASS |

## QA States

- FORMAT_UNIFORMITY: PASS
- SECTION_COUNT: PASS_8_OF_8
- FORBIDDEN_ORIGIN_TOKEN_SCAN: PASS
- TRACK_OR_RESULT_CUE_SCAN: PASS
- KNOWN_DUPLICATED_ASSUMPTION_LABEL_DEFECTS: REPAIRED
- RESIDUAL_RESEARCH_BASIS_CUE: REMOVED
- SUBSTANTIVE_PRESERVATION_SELF_CHECK: PASS_WITH_INDEPENDENT_RECHECK
- REPAIR_ROUND_1: APPLIED_C02_C03 / RECHECK_PASS
- MODEL_ASSISTED_BLIND_QA: PASS_8_OF_8
- BLIND_QA_STATE: PASS

## Deterministic Scan Scope

The scan covers only public blind briefs. It rejects source-position identifiers, prior-track terms, evaluator/result labels, old alias-key markers, freeze-note metadata, the known duplicated assumption labels, and the known research-basis phrase. Theory-internal concepts such as evidence provenance, evidential status, or fixed protocol versions are not treated as origin metadata.

## Preservation Limitation

The briefs are normalized syntheses rather than byte-preserving redactions. Preservation was checked structurally against each permitted source for problem framing, assumptions, representation, mechanisms, six common stress cases, consequences, objections, alternatives, falsifiers, implementation, and conclusion-changing evidence. Independent semantic review initially found two omissions, the scene builder applied only the four prescribed insertions, and the independent worker rechecked the repaired briefs. Final semantic QA is PASS 8/8.
