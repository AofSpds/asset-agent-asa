# F05-R1 CTLV L1 D0 independent validation journal

- Validator: `root/f05_r1_ctlv_d0` / `AAA-CONTROL-VALIDATOR (CTLV)`
- Author: `root/f05_r1_author`
- Run: `AAA-M3TOP3-F05-R1-20260905-231028-CODEX-01`
- Target commit: `bc327dddfcc2d826a9ef7c4169b2e8c87f4957f8`
- Target tree: `ae502559ccb3dc3ad76c835f5049f993f6da2d01`
- Target bundle: `AAA-M3TOP3-F05-R1-D0-bc327dddfcc2d826a9ef7c4169b2e8c87f4957f8-ae502559ccb3dc3ad76c835f5049f993f6da2d01`
- Target merged input: `78d540e5e0385104ba21a744e28897762f4d15af25f571de1cc57136882b2500`
- Issued: `2026-09-06T00:27:31+09:00`
- Verdict: `FAIL`

## Independence and method

I did not author or edit the D0 implementation, policy binding, input, CA evidence, or any shared control artifact. I read the immutable D0 commit, independently recomputed Git and SHA-256 identities, rehashed every vendored official body, queried the bound Parquet directly with DuckDB without importing the F05 builder, reconstructed all 57 companies' 20/60-session returns, turnover acceleration, exact /57 benchmarks, source-slice hashes, and merged F02/F05 input hash, and reviewed the P4 negative gates. I did not invoke the production score helper or score CLI and produced no score/rank output.

## Evidence-supported results

- Owner authority: exact policy commit/tree/blob/bytes/SHA-256 and exact execution-request commit/tree/blob/bytes/SHA-256 matched. The approved cutoff, no-denominator-shrink rule, no invented CA factor, no dividend total-return substitution, and claim ceiling were preserved.
- Population and input: exact R0 W1 INCLUDE membership was 57 unique company IDs and 57 unique KRX codes. The canonical F05 JSONL was 267,149 bytes, 57 ascending unique rows, and SHA-256 `8e5c2991eb1c14bede88300a5fd1d648ce263d3e7a3d6a83b31af9b1e3d873f7`; all 57 were explicitly `AVAILABLE`; no governed outcome key was present.
- Direct source reperformance: Parquet SHA-256 `b0c38943e67637d5faf88429880092cf0f46a394be39860dd3bcd0b04231bccb`; 3,477 admitted rows; 57 codes; 61 aligned sessions ending 2024-08-09; session-grid SHA-256 `8667d8b63eeaa5332b0c1390dec179c43c692591a7c3db4c5b1a6cf31217a911`. Every per-company return, turnover acceleration, and source-slice hash matched the materialized input. The independently reduced benchmarks matched exactly: 20-session `-0.2124153885346208337758748387981210510982875684105824670798651096`; 60-session `-0.2427557483310895727201166322683066906964043950156641786131060302`.
- CA custody: all 11 issuer/KRX bodies matched their fixed byte lengths and fixed body SHA-256 values. Direct source rows matched GST 2024-06-26 (`Close=21600`, `Changes=-100`, `ChangesRatio=-0.46`) and 2024-07-24 (`Stocks=18618260`), and Exicon 2024-06-03 (`Close=20400`, `Changes=930`, `ChangesRatio=4.78`) and 2024-07-31 (`Volume=814284`, `Stocks=13050797`). No factor was inferred.
- Model preservation: Git blobs for `features_v1.py`, `features_v1_narrow_patch.py`, `scorer_v1.py`, and the v1.0 config were respectively `35104a7384c3ee6175136e95dded7f3237d69435`, `b9017f5db0fb637c8a449d5ee3cb1c4a05481076`, `2a797ea705eeb1aef330754fb08ff2182297c139`, and `043bf24bc8c838a8060360e86614cf5bfefc9145`; no D0 diff touched them. F05 weight 20, recognition weights 0.50/0.30/0.20, and the existing saturation behavior remained bound.
- Test execution: after one environment-only ACL failure while importing DuckDB, the same 113-test command was rerun with access to the already-installed runtime and passed 113/113, exit 0, stdout SHA-256 `662cc0f45c06f573d64afcf0cc46e519254f68342389440cef167c7b415e4b16`. The independent direct-data reperformance exited 0 with stdout SHA-256 `baf8ba7834810ec374d90675c02b12db2d5317cd613a7cdd94902e26ceebbd56`.

## Blocking finding

### CTLV-D0-001 — N12 independent-receipt gate is under-specified and accepts a non-independent receipt shape

`tools/m3top3/f05_r1_score_outputs.py::_validate_gate` at D0 lines 216-231 checks each supplied object only for `target_author=false`, `target_edited=false`, target refs, input bindings, and a role-specific `role_verdicts` value. It does not require or validate `validator_role`, `validation_level`, `validator_identity`, `independence_assertion`, `supporting_not_self_pass`, or `no_pass_transfer`.

This is confirmed by the target's own passing fixtures: `tools/m3top3/tests/test_f05_r1_score_outputs.py` lines 71-80 and `tools/m3top3/tests/test_cli_score_f05_r1_outputs.py` lines 89-99 construct accepted "receipts" without any validator identity, validation level, independence assertion, or no-PASS-transfer field. Thus, a rehashed minimal JSON object that is not an independently attributable validation receipt can satisfy the current score gate when paired with a matching aggregate object.

This violates P4 negative case N12 (`reject scoring without exact-target independent PASS receipts`) and the required pre-score validation floor. The defect is bounded and correctable inside the approved scope: harden receipt-shape/role/level/identity/independence/no-transfer validation and add negative tests proving each missing or mismatched field is rejected before engine invocation. The corrected exact target requires fresh affected validation; this D0 FAIL cannot transfer.

## Case disposition

- P01-P07: `PASS` on the D0 evidence and 113-test suite.
- N01-N11: `PASS`.
- N12: `FAIL` due to `CTLV-D0-001`.
- N13: `PASS`; provisional claim constants and false Top3/Top10 flags are enforced in the output renderer, and score outputs were absent at validation time.

Overall CTLV L1 verdict: `FAIL`. No statement in this journal is an IVA L2 PASS, Owner acceptance, score authorization, release authority, or performance claim.
