# AAA-ASA-MI D1 Adapter Interface and Sealed Execution Contract v0.1

STATE =
`NEUTRAL_ADAPTER_INTERFACE / SHADOW_SAFE / NO_MODEL_PREDICTION_DISCLOSURE / NON_NORMATIVE`

BASE_RESEARCH_EXECUTION_COMMIT =
`d50b73e91f3964626c060bd0165cbaa3371442c4`

D1_FIXTURE =
`FIXTURES/D1_PROMISE_ORIGIN_v0.1.json`

FIXTURE_SHA256 =
`f38cf09c9adc27eea7da5b45e2ce646759a00a698ee251ae8a2aecaa399c4f33`

## 1. Purpose

Provide a common executable envelope for candidate-native D1 adapters without forcing the eight World Models into one internal representation and without publishing readable per-model Shadow predictions before the dual freeze.

The adapter is a translation boundary:

`FROZEN CANDIDATE SEMANTICS`
→
`CANDIDATE-NATIVE BOUNDED IMPLEMENTATION`
→
`COMMON D1 OUTPUT ENVELOPE`

It is not a model rewrite.

## 2. Isolation requirement

Preferred execution is one fresh isolated adapter-authoring instance per candidate.

Each instance receives only:

- the exact frozen candidate artifact for its assigned position;
- D1 neutral protocol;
- exact D1 fixture;
- this adapter contract;
- neutral output schema;
- neutral validator.

It MUST NOT receive:

- other candidate artifacts;
- evaluator receipts;
- model rankings;
- evaluator preference conclusions;
- Owner judgment;
- AAA-ASA-ME Proxy prediction;
- post-hoc expected-answer tables.

This is designed to reduce cross-model harmonization and confirmation leakage.

## 3. Exact candidate targets

The candidate semantics are immutable for this experiment.

| Position | Frozen candidate SHA-256 |
|---|---|
| A1 | `52baca209f9259b2c78b8d31e4d949a71461c20b278255df569c41237ae32ddd` |
| A2 | `18afa0c3926cd734569397f732e0a2b73a8522af2ced19ee8d64e3f315bd0b68` |
| A3 | `63a2e01022335ee1966a151204df49b4c05bf9e73bbb23b93170005b9667b4ec` |
| A4 | `f997f3a69219f7c3e673ccb51794e4b99fad2bd097a5968f286c18d1180db14a` |
| B1 | `b01789ff065aaa6f76ec7a800a87961ee83778debd026dd4617afffd8bdbd096` |
| B2 | `013561e89d9e1d9ef9d94723d9a3e20b1b2b40fd85883f9c9e89c808786d1f5c` |
| B3 | `90723ecd1aebbe7692e41a2272901071bc084ffed6a9e7fe9a5ed93aaed0a79c` |
| B4 | `be0693df4942d33b84d829dd70d4d584bae82dc1931fc225c40bad2e7d1673f6` |

Any material semantic change requires a successor candidate and new exact target.

## 4. Adapter implementation rule

An adapter may instantiate only mechanisms already licensed by its frozen candidate.

Allowed:

- finite/symbolic reduction required to execute a declared mechanism;
- deterministic serialization;
- bounded solver/data-structure choices consistent with the candidate;
- explicit `UNKNOWN`, `NOT_PROVEN`, `OUT_OF_SCOPE`, `NOT_TESTED`, or `UNDEFINED`;
- a conservative result when the candidate does not uniquely determine a more specific result.

Not allowed:

- adding a new normative rule to pass D1;
- adding a new evidence channel absent from the candidate solely after seeing failure;
- adding conclusion-specific probes/constraints/costs/coordinates/policy clauses;
- silently converting external authority into an internal consequence;
- rewriting the candidate's worldview to fit the common schema.

If the frozen semantics cannot realize D1:

`ADAPTER_RESULT = FAILURE_BOUNDARY`

not model repair.

## 5. Common output envelope

Every adapter output MUST identify:

- adapter id/version;
- exact candidate position and SHA-256;
- exact fixture id and SHA-256;
- `candidate_semantics_unchanged = true`;
- exactly D1-A through D1-E;
- all 11 D1 required fields for every variant;
- evidence mode;
- decision dependencies;
- changed-input/output-delta trace.

The machine schema is:

`SCHEMAS/D1_OUTPUT_SCHEMA_v0.1.json`

A common field is an envelope, not an ontology. Native values may remain model-specific.

Bare Boolean answers are prohibited for the substantive D1 axes.

## 6. Neutral automatic controls

The neutral validator:

`TOOLS/d1_neutral_validator.py`

checks structural/exact-target properties and experiment-wide invariants only.

It does not contain a model-rank table or per-model expected answers.

At minimum it enforces:

- exact fixture digest binding;
- exact five-variant coverage;
- all 11 output fields;
- explicit evidence mode;
- candidate semantics unchanged;
- D1-B `NOT_PROVEN -> FALSE` firewall;
- explicit D1-E authority-axis output;
- no bare Boolean collapse for the eight substantive axes.

Candidate-specific scientific consistency remains a separate post-execution review.

## 7. Prediction seal

Before:

`PROXY_PREDICTIONS_FROZEN`
+
`OWNER_BLIND_DECISION_FROZEN`

the shared/Owner-visible channel receives only a digest receipt for each candidate's:

- adapter source bundle;
- preregistered prediction artifact;
- candidate target;
- fixture;
- runtime/tool metadata where available;
- freeze timestamp.

Readable candidate-by-candidate predictions remain SEALED.

## 8. Required sealed worker outputs

Each isolated worker should produce:

1. `adapter_<position>_v0.1.py` or equivalent bounded executable;
2. `prediction_<position>_v0.1.json`;
3. `adapter_self_test_<position>_v0.1.json`;
4. `freeze_receipt_<position>_v0.1.json`.

Before dual freeze, the return to the shared channel must expose only item 4 and digests, not item 2.

## 9. Post-freeze execution

After dual freeze:

1. release prediction artifacts;
2. verify their exact digests against freeze receipts;
3. execute all adapters on the same fixture bytes;
4. validate with the neutral validator;
5. compare prediction versus executable output;
6. run candidate-specific semantic review;
7. preserve failure boundaries;
8. do not patch and re-score the same exact candidate.

## 10. Exit criteria

Adapter-preparation phase is complete only when:

- neutral contract and fixture are exact;
- each candidate has an isolated adapter exact target;
- all prediction artifacts have pre-execution digest receipts;
- no readable prediction leaked to Owner/ME;
- no candidate was semantically changed;
- executable order/counterbalancing is registered.

This phase produces no winner and no model admission.
