# AAA-ASA-ME Owner Model–Protocol Interaction and Model Regeneration Proposal v0.1

DATE = 2026-08-21 KST
PROJECT = AAA
PRODUCT = ASSET AGENT ASA
WORKSTREAM = AAA-ASA-ME
STATE = NON_NORMATIVE_RESEARCH_MEMORY / OWNER_EXPLICIT_PROPOSAL / NOT_VALIDATED / NOT_OWNER_ACCEPTANCE

## 1. Trigger

During Owner interview review, the Owner identified a deeper mismatch between the current candidate-generation/evaluation framing and the intended world-model concept.

The Owner proposed that if the currently detected candidates were generated under a framing that treats protocols themselves as world models, the model set may need to be regenerated rather than merely re-ranked.

This is a proposal/high-priority hypothesis, not yet a frozen Owner decision.

## 2. Owner-explicit statements

OWNER_EXPLICIT_PROPOSAL:

- Model and protocol should be treated as interacting rather than as separate one-way layers.
- The desired model should be able to support heterogeneous protocol sets rather than embodying one protocol as its essence.
- A more appropriate candidate question is: `Can your model support this protocol? If yes, how does it operate under it?`
- Candidate evaluation should ask whether a model can express/respond to a protocol without semantic distortion, ad-hoc patching, or collapse of plurality.
- If the current model set was detected using protocol-as-model questions, rerunning model generation may be warranted.

## 3. Current architecture hypothesis

MODEL_INFERRED / HIGH-WEIGHT CANDIDATE:

`MODEL <-> PROTOCOL_SET`

not merely:

`MODEL -> FIXED_PROTOCOL -> OUTPUT`

The interaction should permit at least:

- protocol activation conditioned on context/purpose/perspective;
- protocol-specific projections over the same underlying relational/event state;
- protocol-induced queries or constraints feeding back into model state/representation;
- multiple protocols remaining simultaneously admissible where appropriate;
- explicit UNKNOWN / CONFLICT / MULTIPLE_VALID_VIEWS when no unique resolution is licensed;
- no forced convergence solely for convenience.

The Owner has not yet selected Relation vs Event as the unique primary foreground object.

## 4. Candidate-generation implication

The previous candidate-generation objective may be underspecified if it asks each candidate to BE the adjudication mechanism.

A revised candidate-generation task should instead seek models that can:

1. represent a sufficiently expressive underlying reality/state;
2. expose interfaces/hooks through which heterogeneous protocols can operate;
3. preserve protocol-local semantics and provenance;
4. support protocol disagreement without collapsing one protocol into another;
5. adapt when protocol sets change;
6. preserve meaningful invariants where required;
7. support heterogeneous personalities/worldviews;
8. remain testable under protocol-switch and cross-protocol stress cases.

## 5. Better discriminating question form

LOW-VALUE:
- Is protocol X the correct world model?
- Which protocol should define continuity?

HIGHER-VALUE:
- Can this candidate model natively support Protocol X?
- What model state/relations/events does Protocol X read?
- What outputs does Protocol X produce without changing the candidate semantics?
- What happens when Protocol X and Protocol Y both apply and disagree?
- Can the model switch/compose protocols without ad-hoc ontology expansion?
- What information must remain invariant across protocol changes?
- When does the model correctly return UNKNOWN / CONFLICT / MULTIPLE VALID VIEWS?
- What protocol classes are impossible or unnatural for this model, and why?

## 6. Research decision point

REVIEW_REQUIRED:

Determine whether to:

A. reinterpret the existing C01-C08 candidates under a new `MODEL_SUPPORTS_PROTOCOLS` test battery first;

B. regenerate a new candidate cohort from a corrected `MODEL <-> PROTOCOL_SET` brief;

C. do both: first stress-test existing candidates, then generate a successor cohort using observed failure boundaries.

Owner wording suggests B or C may be appropriate, but no final selection is frozen yet.

## 7. Evaluation implication

Future performance should distinguish:

- protocol support breadth;
- semantic fidelity under protocol activation;
- context-sensitive routing;
- cross-protocol conflict handling;
- protocol-switch stability;
- interaction feedback between protocol and model;
- preservation of uncertainty/plurality;
- heterogeneous personality/worldview support;
- failure-boundary honesty;
- cost/complexity of supporting additional protocols.

No single scalar score is authorized.

현재 상태: 기존 후보가 protocol-as-model framing에서 검출되었을 가능성이 있어 후보 생성 목표 자체의 재검토가 필요하다는 Owner 제안이 발생했다.
핵심 판단: 원하는 구조는 고정 프로토콜을 내장한 단일 모델보다 `MODEL <-> PROTOCOL_SET` 상호작용 구조에 가깝다.
진행 작업: 기존 후보를 새 protocol-support 기준으로 재해석할지, 후보를 새로 생성할지, 둘 다 할지 결정해야 한다.
다음 단계: 기존 C01-C08에 대한 protocol-support stress test와 corrected candidate-generation brief를 비교 설계한다.
사용자 행동: 다음 논의에서 A/B/C 중 어느 연구 경로가 더 적절한지 결정하면 된다. 작성시각: 2026-08-21 19:33 KST
