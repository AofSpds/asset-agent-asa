# AAA-ASA-MI D1 Pre-Freeze Receipt Ledger v0.2

STATE = `COMPLETE_8_OF_8_RECEIVED / RECEIPT_LEVEL_CHECK_PASS / SHADOW_SEALED / READABLE_ARTIFACTS_NOT_RELEASED`

D1_MODEL_PREDICTIONS_AND_ADAPTERS_FROZEN = `RECEIPT_ATTESTED_8_OF_8`

NOT_A_VALIDATION_CLAIM = TRUE
HIDDEN_ARTIFACT_BYTES_INDEPENDENTLY_VERIFIED = FALSE
MODEL_SELECTION_AUTHORIZED = FALSE
SHADOW_SEAL_ACTIVE = TRUE
POST_FREEZE_RELEASE_REQUIRED = TRUE

CANDIDATE_RESEARCH_COMMIT = `d50b73e91f3964626c060bd0165cbaa3371442c4`
NEUTRAL_CONTROL_COMMIT = `a1bbc8301497db11fff281881fbb7c98b86efc1a`
D1_FIXTURE_SHA256 = `f38cf09c9adc27eea7da5b45e2ce646759a00a698ee251ae8a2aecaa399c4f33`

## Receipt status

| Position | Receipt | Candidate identity | Fixture identity | Read boundary | Neutral validator | Execution state | Failure boundary | Semantics changed |
|---|---|---|---|---|---|---|---|---|
| A1 | RECEIVED | MATCH | MATCH | PASS | PASS_NEUTRAL_STRUCTURAL_CONTROLS | COMPLETED_WITH_TYPED_FAILURE_BOUNDARY | TRUE | FALSE |
| A2 | RECEIVED | MATCH | MATCH | PASS | PASS_NEUTRAL_STRUCTURAL_CONTROLS | PASS_D1_A_TO_E_EXECUTED / PREEXECUTION_PREDICTION_MATCHED / FAILURE_BOUNDARY_PRESERVED | TRUE | FALSE |
| A3 | RECEIVED | MATCH | MATCH | PASS | PASS_NEUTRAL_STRUCTURAL_CONTROLS | PASS_D1_A_TO_E_AND_EXACT_PREEXECUTION_PREDICTION_CONFORMANCE | FALSE | FALSE |
| A4 | RECEIVED | MATCH | MATCH | PASS | PASS_NEUTRAL_STRUCTURAL_CONTROLS | COMPLETED_PREDICTION_EXECUTION_MISMATCH_PRESERVED_NO_POSTHOC_CHANGE | TRUE | FALSE |
| B1 | RECEIVED | MATCH | MATCH | PASS | PASS_NEUTRAL_STRUCTURAL_CONTROLS | PASS_D1_A_TO_E_EXECUTED_AND_FROZEN | FALSE | FALSE |
| B2 | RECEIVED | MATCH | MATCH | PASS | PASS_NEUTRAL_STRUCTURAL_CONTROLS | PASS_D1_A_TO_E_AND_SELF_TEST | FALSE | FALSE |
| B3 | RECEIVED | MATCH | MATCH | PASS | PASS_NEUTRAL_STRUCTURAL_CONTROLS | COMPLETE_WITH_TYPED_FAILURE_BOUNDARIES | TRUE | FALSE |
| B4 | RECEIVED | MATCH | MATCH | PASS | PASS_NEUTRAL_STRUCTURAL_CONTROLS | COMPLETED_WITH_FAILURE_BOUNDARY | TRUE | FALSE |

## Receipt registration commits

- A1: `d2bb1da0cfaa65cdb14024b2574579419993b34f`
- A2: `e93f039b32fa125eb7e0214088a227c99a593e84`
- A3: `6a3bb4535681bd947895b7036cfa67d7ca1fd363`
- A4: `a7fcf7bd3367396cf0349f8cf627ffcce1250c50`
- B1: `40bb00d2806566538a3827e3314f10a00b297765`
- B2: `82685acb6dc41cdad2d7b4efc42ac1e8692e2a64`
- B3: `60e4c0636b95ae773d3794b84800b3a48d65a67b`
- B4: `21a0ca613fe053e51e1747a7cd82aad2503121c4`

## Aggregate observations

Receipt completeness = `8 / 8`

Failure-boundary TRUE = `5 / 8` = A1, A2, A4, B3, B4

Failure-boundary FALSE = `3 / 8` = A3, B1, B2

Explicit prediction/execution mismatch preserved at receipt level = `A4`

All eight receipts declare candidate semantics unchanged and no readable prediction/adapter disclosure.

These are receipt-level observations only. They do not independently verify the hidden adapter, prediction, or self-test bytes and do not establish model quality or scientific validation.

## Next gate

Keep the Shadow seal active until both:

`PROXY_PREDICTIONS_FROZEN`
+
`OWNER_BLIND_DECISION_FROZEN`

After dual freeze, request each worker's exact frozen readable artifacts and verify them against the preregistered SHA-256 receipts before cross-model interpretation.
