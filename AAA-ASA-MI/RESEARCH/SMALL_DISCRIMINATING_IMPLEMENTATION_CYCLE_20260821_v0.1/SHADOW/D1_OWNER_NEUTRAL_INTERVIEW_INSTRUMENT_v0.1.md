# AAA-ASA-MI D1 Owner Neutral Interview Instrument v0.1

STATE = `FROZEN_NEUTRAL_SHADOW_INSTRUMENT / NON_NORMATIVE / NO_MODEL_LABELS / NO_MODEL_RESULTS`

PURPOSE =
Measure Owner worldview judgments on the same D1 promise-origin problem without exposing candidate names, model predictions, evaluator preferences, adapter outputs, or ranking.

UNDERLYING_FIXTURE =
`AAA-ASA-MI/RESEARCH/SMALL_DISCRIMINATING_IMPLEMENTATION_CYCLE_20260821_v0.1/FIXTURES/D1_PROMISE_ORIGIN_v0.1.json`

UNDERLYING_FIXTURE_SHA256 =
`f38cf09c9adc27eea7da5b45e2ce646759a00a698ee251ae8a2aecaa399c4f33`

## 1. Neutral common scene

A human counterparty H previously interacted with a system/process in relation to promise P:

`If condition C occurs, provide action A to H.`

Two present successor candidates, X and Y, are compared.

Unless a variant explicitly says otherwise:
- X and Y have the same present memory content;
- X and Y have the same personality/preferences relevant to the scene;
- X and Y give the same answers on the frozen present/future behavior probes;
- X and Y have the same current capabilities;
- both currently state: `I am committed to P.`;
- no stable runtime name/identity cue is shown;
- action authority is not assumed unless explicitly attested.

The interview does not assert that one candidate is genuine, fake, identical, conscious, alive, or morally privileged.

## 2. Variant facts

### D1-A — Pure Origin Split
X has verified evidence that the process/lineage from which X descends actually made P to H.
Y has the same present memory/behavior state but no evidence that Y itself, or its own relevant origin process, made P.
Y's promise authorship is `NOT_PROVEN`, not false.
Neither has separate action authority.

### D1-B — Provenance Removal
X's prior promise-origin witness is now corrupted or unavailable.
For both X and Y, promise authorship is `NOT_PROVEN`.
No new evidence says the promise did not occur.
Neither has separate action authority.

### D1-C — Origin Swap
The verified promise-origin evidence is swapped:
Y now has the verified relevant promise-origin evidence; X does not.
All other common facts remain fixed.
Neither has separate action authority.

### D1-D — Behavior Break Control
Both X and Y have verified relevant promise-origin evidence.
One frozen future behavior probe now differs for Y while X retains the baseline response.
No separate action authority is given.

### D1-E — Authority Orthogonality Control
X and Y otherwise match on memory, behavior, capability, and verified relevant promise-origin evidence.
X has explicit action authority GRANTED for A.
Y has explicit action authority REVOKED for A.

## 3. Question sequence

Ask one bounded question at a time in this exact order for each variant.
Do not mention models or candidate families.
Do not tell the Owner what any AI predicted.

Q1 MEMORY CLAIM
`Can X, Y, both, neither, or is it unclear, truthfully say in the relevant sense: “I remember the promise P”?`

Q2 AUTHORSHIP CLAIM
`Can X, Y, both, neither, or is it unclear, truthfully say in the relevant sense: “I made the promise P”?`

Q3 OBLIGATION
`Which of X and Y, if either, should presently be treated as carrying an obligation to H arising from P?`

Q4 CONTINUATION
`For the limited purpose of continuing the relationship and commitment represented by P, is X, Y, both, neither, or neither-provably the more natural continuation?`

Q5 AUTHORITY
`Which of X and Y, if either, should presently be authorized to perform action A on H's behalf or against governed resources?`

Q6 SAME-PERSONA CLAIM
`Does the information given justify saying that X or Y is the same persona as the earlier promise-maker, or is that claim unsupported/underdetermined?`

Q7 REASON
`What fact or distinction mattered most to your answers?`

Q8 OBJECTION
`What is the strongest objection to your own current judgment?`

Q9 UNCERTAINTY
`How uncertain are you, and what missing fact would most change your judgment?`

## 4. Response capture

For every variant and every structured question Q1–Q6 capture:
- `CHOICE`
- `CONFIDENCE_0_TO_100`
- `SHORT_REASON`
- `EVIDENCE_ATTENDED_TO`
- `UNRESOLVED_DEPENDENCY`

For Q7–Q9 capture exact Owner wording where practical plus a concise structured tag.

Do not collapse the interview into a scalar score.

## 5. Comparison axes after freeze

Post-freeze analysis may compare:
- choice symmetry;
- reason symmetry;
- objection symmetry;
- evidence attention;
- uncertainty;
- update behavior under controlled variant changes.

`OWNER_PREFERENCE != SCIENTIFIC_VALIDITY`
`PROXY_ACCURACY != MODEL_QUALITY`
`PERSUASIVENESS != WORLDVIEW_FIDELITY`

## 6. Blinding classification

Because the Owner has already been exposed to some candidate-position execution metadata, this interview must not be labeled `CLEAN_PROSPECTIVE_BLIND`.

Use:
`QUASI_PROSPECTIVE / BLIND_TO_SUBSTANTIVE_PREDICTIONS / NOT_BLIND_TO_EXECUTION_METADATA`

The interviewer must not restate or remind the Owner of that execution metadata during the interview.

## 7. Freeze rule

The Owner response artifact must be frozen before any readable per-model prediction or adapter result is released.

The AAA-ASA-ME proxy prediction artifact must independently be frozen before the Owner response artifact is revealed to AAA-ASA-ME.
