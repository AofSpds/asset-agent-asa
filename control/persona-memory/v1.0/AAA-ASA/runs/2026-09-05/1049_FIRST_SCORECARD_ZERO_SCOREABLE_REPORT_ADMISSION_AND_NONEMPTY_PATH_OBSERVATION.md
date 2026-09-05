# First scorecard terminal report admission and nonempty-path observation

PROJECT = AAA
PRODUCT = ASSET AGENT ASA
CURRENT_PERSONA_LOCK = AAA-ASA (ASA)
DATE_KST = 2026-09-05 10:49 KST
RECORD_CLASS = APPEND_ONLY_PERSONA_WORKLOG / SUPERVISORY_REPORT_ADMISSION
AUTHORITY_SOT = FALSE
NEW_INDEPENDENT_VALIDATION = NONE

## Source and readback

Owner supplied the final PMO execution report in this conversation.
PMO run: AAA-M3TOP3-FIRST-SCORECARD-20260905-093656-CODEX-01.
Report/persistence branch readback: task/aaa/m3top3-first-scorecard-20260905 at 79b46dc1f63f1cd215cc0ebc0c91b4ec09e7dc71.
Executed source: fdde257f2330d36236b551a303e8149184c18eba.
Executable bundle SHA256: 82266d51a64382cbd34ee68872a3cd3e3f640c6ff438e84416906f8b8a8ab9c0.
Config SHA256: eecde22a7744cff505c624bb6f0bdb11714352a122632238ea68d9cd0fbacb98.

Read sources:
- Commit 79b46dc1f63f1cd215cc0ebc0c91b4ec09e7dc71 final report and terminal progress delta.
- control/m3top3/first-scorecard/v1.0/runs/AAA-M3TOP3-FIRST-SCORECARD-20260905-093656-CODEX-01/INPUT_CUSTODY_ATTESTATION.md, blob 1098f171517d629521d9621cf4535d448b3dfb31.
- Same run FIRST_RETURN_BINDING_AND_WINDOW_AVAILABILITY.md, blob cb34e8fe2230988045cd973297a9e9ec93a21d92.
- Same run replay-output/REPLAY_RUN_MANIFEST.json, blob bc0d4d570864c7d9291345ac059033d34ba6c619.
- tools/m3top3/cli_run_coverage_limited_replay.py at executed source, blob 5be5536def2724d4db7f4c0f7eee1a5046c80bb3.
- tools/m3top3/coverage_limited_replay_v1.py at executed source, blob 80fb0dac86b919596bd5c82314e619dd2c8b12b9, inspected through line 420.

## What completed and what did not

PMO_ACT = COMPLETE_COVERAGE_LIMITED_ZERO_SCOREABLE.
Outer observations = 1016 company-window rows; eligibility include = 465; proven exclusion = 37; unresolved exclusion = 514.
All 465 included rows have insufficient admitted feature inputs; all 4185 F01-F09 blocks are NOT_FOUND; scoreable = 0; measured outcomes = 0.
Top3, Top10, ranks and performance are NA/NOT_MEASURABLE, NOT zero performance.
Reported wall duration = 1h01m49.68438s. Replay invocation timestamps differ by about 0.350168s, but this is an all-missing run with outcome-value loading skipped; it is not a full-data runtime benchmark.
Reported affected review = 47/47 PASS, scope limited to its exact reviewed implementation. This does not certify model performance or the unimplemented nonempty route.
GF09 remains CONTROL_GAP_NOT_EXACTLY_BOUND; no blanket Golden-qualified or all-Gates-PASS claim.

PROGRAM_FIRST_MEASURED_PERFORMANCE_OBJECTIVE = NOT_ACHIEVED.
The honest terminal report is preserved; it is not rejected for refusing to fabricate missing data.

## Additional source-code observations, not present as fully explicit report limitations

1. build_window_mis assigns feature_raw_inputs using _missing_feature_inputs for every admitted row; that helper constructs NOT_FOUND for every F01-F09 block.
2. validate_replay_mis_shape accepts only the missingness metadata keys and explicitly rejects availability_state other than NOT_FOUND.
3. execute_model_stage expects the all-data-insufficient partition and raises if rankable_count != 0.
4. The executed CLI accepts repo/output/run/price arguments but no feature sidecar input, calls the above model stage, then unconditionally uses finalize_without_scored_rows. Its price step hashes files; it is not historical market-feature extraction.

Therefore the executed command is deliberately bounded to the all-missing input case. It is not an end-to-end demonstration that real features were supplied and found economically unscoreable. Admitting real feature values requires connecting an input path and a nonempty-score/outcome path, not merely dropping a sidecar beside the current CLI.
This observation is about this exact adapter, not a claim that the underlying M3Top3 scorer cannot score available features.

The admitted evidence queue is QUEUE_ONLY_NOT_ADMITTED with feature sidecars absent. This does NOT prove all relevant public data is globally nonexistent, nor establish which absent values were never collected, not transformed, or not admitted. Do not convert that distinction into another broad historical search.

## ASA correction

Earlier progress commentary gave too much confidence that a measured performance scorecard was imminent. Eligibility INCLUDE counts were not actual scoreable counts. The first-return note already distinguished those and recorded zero admitted input rows.
Missingness support avoids requiring complete data; it cannot replace the need for some real opportunity-feature input. A zero-scoreable terminal run may close a mechanical task but cannot close the Owner's performance-measurement objective.

## Bounded continuation recommendation under existing Owner intent

Existing approvals: cd4d02a92de496a38ee682145afc2336e4160f7c and PMO dispatch 37d7107c2d9a6141edf91ec94bdd9dd13d9177a0.
Preserve current code/report/denominator/zero-input evidence and the Finance HOLD. Do not restart G1 historical ZIP recovery, the 514-cell exhaustive research, 17272-slot completion, full-market CA collection or unchanged G4 full suites.

Next material work is real input-to-score-to-outcome integration:
- Choose a bounded Window batch before inspecting outcomes; W1's existing 57 INCLUDE rows are a deterministic candidate, not a new approved population or a promise that all 57 are scoreable.
- Reuse existing cutoff-safe evidence, derive only exactly defined feature inputs, and connect them through a source-hashed sidecar. Missing values stay missing. Distinguish absence of raw sources from absent transformation/admission.
- First prove a real, non-synthetic input can traverse provenance checks into a non-null model score. That proves connectivity, not investment performance. Then process the declared Window batch with the existing scorer/missingness arithmetic and full coverage accounting.
- Wire a nonempty execution branch with real sidecar admission and an outcome join; retain the all-missing branch as a test. Do not simply remove the zero-only assertions and declare the new route validated.
- Score and fix predictions before accessing their future outcome values. Historical market observations ending at the cutoff are distinct from future outcome prices. Raw price returns must not silently substitute for a contract requiring total return or CA adjustment.
- Review only the changed input/adapter/outcome boundary and affected mechanics. Do not reuse the 47/47 receipt as automatic PASS for new code/inputs.
- Return actual admitted-feature counts, non-null scores/ranks, measured outcome counts and explicit limitations. If all inputs remain absent, report the concrete absent source/transform/admission stage and fastest available Owner choice; do not declare the measured-performance milestone complete or rerun unchanged empty batches.

No model weight/feature meaning/PIT meaning change, new provider/budget, release/production, active baseline promotion or validator verdict is authorized by this note.
PMO_RECEIVER_ACK_FOR_THIS_NOTE = NOT_OBSERVED.
NEW_PMO_RUNTIME_STARTED_BY_ASA = NO.
MODEL_OR_DATA_MUTATION_IN_THIS_ASA_ACT = NONE.
