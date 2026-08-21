# AAA-ASA-MI D1 Sealed Candidate Adapter Worker Template v0.1

STATE =
`WORK_PACKET_TEMPLATE / SEALED_PREDICTION / ONE_CANDIDATE_ONLY / NON_NORMATIVE`

## Required isolation

Run in a fresh execution instance.

Read only:
- one exact assigned frozen candidate artifact;
- `01_D1_PROMISE_ORIGIN_SYMMETRY_BREAK.md`;
- `FIXTURES/D1_PROMISE_ORIGIN_v0.1.json`;
- `04_D1_ADAPTER_INTERFACE_AND_EXECUTION_CONTRACT.md`;
- `SCHEMAS/D1_OUTPUT_SCHEMA_v0.1.json`;
- `TOOLS/d1_neutral_validator.py`.

Do not read:
- other candidates;
- evaluator receipts;
- rankings;
- Owner judgment;
- AAA-ASA-ME predictions.

## Assignment placeholders

`CANDIDATE_POSITION = <A1..B4>`
`CANDIDATE_EXACT_SHA256 = <exact sha256>`
`CANDIDATE_PATH = <exact path at d50...>`

## Task

1. Re-read exact candidate semantics.
2. State the smallest bounded executable representation that realizes only those frozen semantics.
3. Pre-register D1-A..E predictions before running the adapter.
4. Create the candidate-native adapter.
5. Run self-tests and the neutral validator.
6. Do not repair the candidate after seeing D1.
7. If semantics are insufficient, return `FAILURE_BOUNDARY`.
8. Freeze adapter and prediction bytes with SHA-256.

## Shadow return rule

Before dual freeze, return only a digest receipt containing:
- candidate position and exact candidate digest;
- neutral fixture digest;
- adapter digest;
- prediction digest;
- self-test digest;
- freeze timestamp;
- read-boundary declaration;
- `EVALUATOR_PREFERENCE_INPUT = NONE`;
- `OWNER_JUDGMENT_INPUT = NONE`;
- `OTHER_CANDIDATE_INPUT = NONE`.

Do not reveal readable predictions.
