# Owner Review Bundle — Protocol–Object 이중 모델 재탐지

PERSISTENT_PATH = AAA-ASA-MI/RESEARCH/PROTOCOL_OBJECT_DUAL_MODEL_REDETECTION_20260821_v0.1/08_OWNER_REVIEW_BUNDLE_KO.md  
PERSISTENT_REF = research/asa-mi-protocol-object-redetection-20260821-v0-1  
DIGEST_RECEIPT = RECEIPTS/ARTIFACT_RECEIPTS.md  


상태: `POST-TEXT-BIND / NON_NORMATIVE / NOT_VALIDATED / MODEL_FREEZE_CLAIM_NONE`

## 먼저 고정할 해석

> **N01–N12 모두 런타임 실행 증거는 `NOT_PROVEN`이다.**
>
> 아래의 “지원”은 동결 문서에 메커니즘이 있다는 **아키텍처 수준의 접촉**만 뜻한다. 실제 설치, 실행, 출력, 지연, 재현, 원자성, 리셋, 최종 상태 보존은 입증되지 않았다.

- 후보는 동결되어 있다. 의미 변경은 원문 수정이 아니라 새 exact identity와 lineage를 가진 successor여야 한다.
- `READ`, `VIEW_MATERIALIZATION`, `RUNTIME_STATE_MUTATION`, `MODEL_SEMANTIC_MUTATION`은 구분해서 본다.
- Protocol-local 결과를 보편적 진리나 공통 ontology로 승격하지 않는다.
- 순위, 승자, 통합 점수는 만들지 않는다.
- 질문은 “어느 Protocol이 철학적으로 옳은가”가 아니라, 라우팅·불변량·복수성·변경 경계를 어디에 둘 것인가이다.

## 12개 구조 한눈에 보기

| 후보 | 생성 seed | 중심 구조 |
|---|---|---|
| N01 | Relation-first | 증거형 typed hypergraph + sandbox adapter |
| N02 | Relation-first | capability relational fabric + 조건부 CRDT |
| N03 | Event/process-first | immutable event log + temporal projection |
| N04 | Event/process-first | actor/message + commitment + ProtocolInstance |
| N05 | Relation–Event 공구성 | witnessed square + finite Protocol IR |
| N06 | Relation–Event 공구성 | causal event structure + incidence + branch |
| N07 | Protocol-native | stable evidence kernel + typed Protocol VM |
| N08 | Protocol-native | proof-carrying contract + partial lattice |
| N09 | 대안 형식 | membrane-local rewriting + critical pair |
| N10 | 대안 형식 | hybrid viability/control + symbolic guard |
| N11 | Wildcard | polycentric institutional blackboard |
| N12 | Wildcard | typed patch ledger + contextual optics |

---

## N01 — Evidentiary Typed Hypergraph

- **지원 폭:** 관계·증거·출처 재구성, contextual view, 분쟁/복수 view, 제한된 workflow·simulation·control·composite를 typed adapter로 수용한다.
- **이질 Protocol 생존성:** **조건부.** 같은 immutable hypergraph identity는 유지되지만, 새 Protocol은 manifest·type·effect·adapter 검증을 통과해야 한다. event-primary·연속·암묵적/체화 Protocol은 왜곡 또는 거절 가능성이 크다.
- **충돌:** 같은 비교 범위의 찬성/반대 근거를 `CONFLICT`로 보존한다. 다른 범위의 결과는 `MULTIPLE_VALID_VIEWS`; router 순서나 다수결은 기본 해결자가 아니다.
- **불변 / 가변:** exact target, provenance closure, source/view 분리, conflict·scope 보존, 접근 비증폭은 불변. context, Persona, 선택·표현, runtime overlay·cursor는 가변. 의미·규칙·권한 변경은 successor다.
- **Persona / worldview:** 둘을 별도 versioned input으로 두고 병렬 실행한다. 전환 시 원천에서 다시 materialize하고 손실·누락을 기록한다.
- **유연성의 성격:** **구조적 제약이 있는 유연성.** 명시적 signature·capability·effect·provenance·resource bound가 없으면 실행하지 않는다. “무엇이든 adapter”는 아니다.
- **상태 발생:** 정보·완결성이 부족하면 `UNKNOWN`; 같은 범위의 양립 불가 근거면 `CONFLICT`; 닫힌 증명 의무를 끝냈으나 성립하지 않으면 `NOT_PROVEN`; type/권한/adapter/semantic primitive가 없으면 `OUT_OF_SCOPE`.
- **가장 강한 한계:** relation-first 분해가 사건의 발생·순서·수행성을 약화할 수 있고, 서로 먼 Protocol 사이에는 손실을 기록할 뿐 의미 보존을 보장하지 못한다.
- **실행 근거:** `NOT_PROVEN`.

## N02 — Capability Relational Fabric

- **지원 폭:** versioned relation/facet, capability-bounded query·materialization·mutation, 다중값/분기 공존, 조건부 CRDT merge, explicit bridge를 지원한다.
- **이질 Protocol 생존성:** **조건부.** Protocol별 namespace와 exact snapshot은 유지되지만, 의미 연결은 versioned bridge와 증명된 merge algebra가 있어야 한다. 없으면 병렬 보존만 한다.
- **충돌:** 값·identity·order·authority·schema·time 등 typed `ConflictRecord`로 경쟁 항을 보존한다. CRDT 수렴은 algebra 법칙이 입증된 부분에만 주장한다.
- **불변 / 가변:** exact binding, capability confinement, append/lineage, materialization purity, plurality가 불변. 선언된 runtime input과 승인된 relation/object delta만 가변. type·routing·merge·status 의미 변경은 successor다.
- **Persona / worldview:** Persona는 capability·salience·disclosure·preference가 있는 context ref다. worldview는 Protocol·bridge·assumption 묶음이며, 충실한 전환이 불명확하면 통합하지 않는다.
- **유연성의 성격:** **보수적 구조 유연성.** capability와 merge law 없이 임의 수렴·last-write-wins·이름 유사성에 의한 호환을 허용하지 않는다.
- **상태 발생:** 필요한 값 부재는 `UNKNOWN`; 동일 규칙을 함께 만족할 수 없는 typed contender는 `CONFLICT`; adapter/merge/compatibility 증거 부족은 `NOT_PROVEN`; domain·operation·capability 밖이면 `OUT_OF_SCOPE`.
- **가장 강한 한계:** 관계 주소성과 capability를 우선해 과정 정체성·연속 dynamics를 덜 자연스럽게 다루며, ProtocolInstance의 합법적 parameter revision/history가 충분히 구체적이지 않다.
- **실행 근거:** `NOT_PROVEN`.

## N03 — Event-Sourced Temporal World

- **지원 폭:** event-sourced workflow, temporal state machine, replay, correction/compensation, commitment-like process, contextual projection, bridge 기반 이질 Protocol을 다룬다.
- **이질 Protocol 생존성:** **조건부.** immutable event history와 Protocol-local namespace는 살아남지만, relation-only 또는 continuous semantics가 eventization에서 손상되면 거절한다.
- **충돌:** 같은 proposition/context/interval의 양립 불가 claim은 `CONFLICT`; 서로 다른 Persona·context 결과는 `MULTIPLE_VALID_VIEWS`. 선택 policy는 새 scoped result일 뿐 원천을 삭제하지 않는다.
- **불변 / 가변:** append-only event, exact cut, bitemporal/causal provenance, pure projection, namespace isolation이 불변. frozen transition 아래의 runtime event append는 가변. schema·rule·router·bridge 의미는 successor다.
- **Persona / worldview:** Persona별 evidence·salience·Protocol preference를 exact cut에 묶어 재생한다. 전환은 이전 결론을 번역하지 않고 같은 cut에서 재-materialize한다.
- **유연성의 성격:** **descriptor·sandbox 범위의 구조 유연성.** 안정 ID, typed envelope, replay/effect contract가 없는 Protocol은 quarantine/거절한다.
- **상태 발생:** cut/context/evidence 부족은 `UNKNOWN`; 공통 frame의 양립 불가 claim은 `CONFLICT`; 요구된 warrant가 미충족이면 `NOT_PROVEN`; evaluator/class/adapter가 없으면 `OUT_OF_SCOPE`.
- **가장 강한 한계:** event primacy가 풍부한 정적 관계·연속 과정·retroactive reinterpretation을 잘게 쪼갤 수 있다. 별도 mutable ProtocolInstance parameter/history 부재도 합법적 runtime Protocol 변경을 막는다.
- **실행 근거:** `NOT_PROVEN`.

## N04 — Commitment Actor Ecology

- **지원 폭:** actor/message workflow, role·commitment, causal transition, concurrent ProtocolInstance, context projection, stateful runtime 전환에 직접 맞는다.
- **이질 Protocol 생존성:** **조건부.** generic envelope로 보존할 수 있지만 실행에는 schema와 transition evaluator/adapter가 필요하다. relation-only slice·continuous control은 비원생적이다.
- **충돌:** payload·role·causal order·interpretation의 `ConflictSet`을 남긴다. 다른 context/worldview의 유효 결과는 `MULTIPLE_VALID_VIEWS`; 전역 우선순위는 없다.
- **불변 / 가변:** actor ownership, immutable events, causal honesty, exact target, source/runtime/view 분리가 불변. ProtocolInstance의 state revision·timer·frontier는 frozen evaluator 아래 가변. definition/role/causal rule은 successor다.
- **Persona / worldview:** versioned projection contract로 vocabulary·salience·redaction만 바꾸며, switch manifest가 identity·frontier·evidence·status 손실을 공개한다.
- **유연성의 성격:** **메시지·상태기계로 경계된 유연성.** evaluator 없는 unseen Protocol은 저장·검사만 가능하고 임의 실행하지 않는다.
- **상태 발생:** evaluator·정보 부재는 `UNKNOWN`; 같은 frame의 incompatible claims는 `CONFLICT`; proof/evaluator replay가 성립하지 않으면 `NOT_PROVEN`; 모델이 다루지 않는 질문/프로필이면 `OUT_OF_SCOPE`.
- **가장 강한 한계:** 의미를 담는 adapter가 없으면 generic envelope는 containment에 머문다. 다중 Object 원자성·연속 dynamics·closed relation slice도 약하다.
- **실행 근거:** `NOT_PROVEN`.

## N05 — Witnessed Relation/Event Incidence

- **지원 폭:** query, workflow, interpreter, bounded simulator, transaction, migration, external-observer를 finite IR과 witnessed relation/event square로 다룬다.
- **이질 Protocol 생존성:** **조건부.** relation과 event를 모두 주소 가능한 경계로 유지하지만, 새 Protocol이 finite IR·typed port·effect·bound로 compile되어야 한다.
- **충돌:** comparable한 같은-scope claim만 `CONFLICT`; 다른 context는 `PLURAL_VALID`. resolution도 별도 Protocol이며 후보와 counterexample을 삭제하지 않는다.
- **불변 / 가변:** square boundary, exact pins, witness/provenance, event continuity, effect separation, view non-authority가 불변. runtime event/state revision은 선언된 rule 아래 가변. semantics와 witness policy 변경은 successor다.
- **Persona / worldview:** Persona별 claim을 한 `ViewSet` 안에 따로 보존하고, switch마다 fidelity/loss report를 만든다. Persona는 권한이나 truth를 생성하지 않는다.
- **유연성의 성격:** **형식적·유한 제약의 유연성.** opaque/native/self-modifying/unbounded Protocol은 실행하지 않는다.
- **상태 발생:** 필요한 관측 부재는 `UNKNOWN`; verified counterexample 또는 같은-scope incompatibility는 `CONFLICT`; witness/proof 의무 미충족은 `NOT_PROVEN`; opcode·predicate·resource·mapping 미지원은 `OUT_OF_SCOPE`.
- **가장 강한 한계:** witnessed square가 의미 불일치를 해결하기보다 witness policy 안으로 옮길 수 있다. 별도 persistent ProtocolInstance parameter history와 mixed-request 전체 원자성도 불완전하다.
- **실행 근거:** `NOT_PROVEN`.

## N06 — Causal-Incidence Co-Constitution

- **지원 폭:** finite relation/event hybrid, causal configuration, explicit counterfactual branch, finite possibility view, contextual materialization, bridge 기반 unseen Protocol을 다룬다.
- **이질 Protocol 생존성:** **조건부.** PIR에 매핑되는 부분만 실행하고, 나머지는 stable opaque construct로 보존한다. `PARTIAL`은 mutation 권한을 주지 않는다.
- **충돌:** causal conflict와 incidence conflict를 분리해 유지한다. 여러 compatible branch는 `MULTIPLE_VALID`; bridge끼리 다르면 `CONFLICT`; 기본 합의는 없다.
- **불변 / 가변:** causal closure, conflict exclusion/heredity, incidence integrity, branch separation, no-view-as-truth가 불변. authorized committed event와 bounded branch/session은 가변. rule·type·Protocol meaning은 successor다.
- **Persona / worldview:** 여러 Persona를 side-by-side로 두는 것이 안전 기본값이다. switch는 preserved/translated/hidden/unmapped/authority change를 receipt로 남긴다.
- **유연성의 성격:** **PIR·support envelope 안의 구조 유연성.** unmapped construct의 의미를 추정하지 않고 operation별 `SUPPORTED/PARTIAL/OUT_OF_SCOPE`를 낸다.
- **상태 발생:** Object/context evidence 부족은 `UNKNOWN`; supported claim/branch의 양립 불가는 `CONFLICT`; bounded branch/proof가 끝나지 않으면 `NOT_PROVEN`; rule/effect/translation이 미지원이면 `OUT_OF_SCOPE`.
- **가장 강한 한계:** dense/continuous causality를 명시적으로 제외하며, stable mutable ProtocolInstance와 revision history가 없어 합법적 runtime parameter patch와 stateful latch가 약하다.
- **실행 근거:** `NOT_PROVEN`.

## N07 — Evidence-Kernel Protocol VM

- **지원 폭:** bounded query·matcher·finite state machine·workflow·composition·relation/event subscription·contextual view·runtime Protocol state를 typed bytecode로 폭넓게 표현한다.
- **이질 Protocol 생존성:** **조건부지만 구조적으로 넓다.** domain 이름이 아니라 opcode/type/effect/capability/budget로 admission한다. 미지원 payload는 보존할 수 있어도 실행 권한은 얻지 못한다.
- **충돌:** context-keyed `StatusAssertion`과 plural outputs를 병렬 보존한다. 하나의 답이 필요하면 explicit aggregation Protocol이 필요하다. whole effect journal을 사전 검증해 local transaction 안의 mixed illegal request를 전부 거절할 수 있다.
- **불변 / 가변:** evidence/revision immutability, exact pinning, context completeness, Persona isolation, admission closure가 불변. ProtocolInstance runtime revision·cursor·state는 typed transition으로 가변. bytecode/schema/effect meaning은 successor다.
- **Persona / worldview:** Persona를 evidence scope·권한·runtime sharing mode가 있는 first-class revision으로 둔다. partition/seal/switch receipt가 A→B→A와 state carryover를 통제한다.
- **유연성의 성격:** **강한 구조적 유연성.** closed typed VM, finite budget, captured nondeterminism, whole-journal validation이 경계를 만든다. arbitrary native code나 “무엇이든 실행”은 명시적으로 제외한다.
- **상태 발생:** 필요한 evidence/context가 없으면 `UNKNOWN`; 병렬 status가 공통 namespace에서 양립 불가하면 `CONFLICT`; proof·adapter·runtime 성질이 입증되지 않으면 `NOT_PROVEN`; opcode/type/capability/authority 밖이면 `OUT_OF_SCOPE` 또는 typed refusal.
- **가장 강한 한계:** closed VM은 tacit·embodied·opaque·unbounded semantics를 제외한다. 구조적 범위가 넓어도 domain legitimacy·truth·연속 ODE solver·완전한 counterfactual semantics는 커널 밖이다.
- **실행 근거:** `NOT_PROVEN`.

## N08 — Proof-Carrying Contract Lattice

- **지원 폭:** typed state machine, role/channel contract, relation/event subscription, higher-order bounded Protocol, proof/refinement/compatibility, runtime instance와 switch contract를 다룬다.
- **이질 Protocol 생존성:** **조건부.** stable substrate에 보존하고 contact·contract·frame·checker가 맞는 capability만 실행한다. comparison lattice는 전역이 아니라 frame별 partial lattice다.
- **충돌:** 같은 frame의 incompatible obligations는 `CONFLICT`; 여러 incomparable optimum은 `MULTIPLE_VALID`; meet/join을 억지로 만들지 않는다. Object-side authority/invariant gate가 action proposal 실행을 별도로 막는다.
- **불변 / 가변:** semantic ID immutability, proof specificity, context/frame retention, evidence retention, authority gate 독립성이 불변. ProtocolInstance runtime revision·declared parameter는 가변. role/event/contract meaning은 새 semantic ID다.
- **Persona / worldview:** Object-rooted Persona 여러 개를 동시에 유지하고, fusion/split은 semantic successor로 본다. switch는 state·event·obligation·context mapping과 loss를 증명/기록한다.
- **유연성의 성격:** **증명·계약으로 제한된 유연성.** parsing, proof, compatibility, authority는 독립 gate다. 모르는 Protocol이 parse되었다는 이유만으로 mutation 권한을 주지 않는다.
- **상태 발생:** fact/evidence 부족은 `UNKNOWN`; 같은 frame의 incompatible positions는 `CONFLICT`; checker/dependency/obligation 미충족은 `NOT_PROVEN`; contract/context/role/observation 밖이면 `OUT_OF_SCOPE`이며 host capability 부족은 별도 `UNSUPPORTED`다.
- **가장 강한 한계:** 호환성은 checker·axiom·frame·observation algebra에 크게 의존해 국소적이고 비용이 높다. mixed batch의 applied prefix를 허용하므로 전체-request 원자적 거절은 자동 보장되지 않는다.
- **실행 근거:** `NOT_PROVEN`.

## N09 — Membrane Rewrite World

- **지원 폭:** finite rewriting, nested locality, rule/event/relation response, bounded branching, multi-interpreter Protocol, critical-pair 분석, view/switch를 지원한다.
- **이질 Protocol 생존성:** **조건부.** 새 언어를 named interpreter로 parse/lower할 수 있는 규칙만 실행한다. 나머지는 membrane 안에서 opaque READ 또는 quarantine으로 보존한다.
- **충돌:** 겹치는 read/write footprint에서 critical pair를 만들고 branch·defer·reject·policy-resolve한다. bounded join 결과를 전역 confluence로 과장하지 않는다.
- **불변 / 가변:** membrane locality, exact version, fresh successor, rule provenance, capability/mode separation, plural alternatives가 불변. 명시된 runtime rule은 versioned state를 바꿀 수 있다. rule/interpreter/meaning 변경은 semantic successor다.
- **Persona / worldview:** 여러 Persona의 grant와 proposal을 분리하고, switch checkpoint에 protocol/runtime/event cursor/alternatives를 고정한다. round trip은 component별 fidelity만 주장한다.
- **유연성의 성격:** **interpreter·lowering·budget로 제한된 구조 유연성.** familiar syntax 유추나 숨은 callback으로 미지원 의미를 채우지 않는다.
- **상태 발생:** derivation/자료 부재 또는 budget exhaustion은 `UNKNOWN`; critical pair가 양립 불가하면 `CONFLICT/contested`; bounded join·replay·fidelity가 성립하지 않으면 `NOT_PROVEN`; interpreter/import/effect가 없으면 `OUT_OF_SCOPE` 또는 quarantine.
- **가장 강한 한계:** membrane과 rewrite rule은 표현 틀일 뿐, 새로운 Protocol별 lowering이 없으면 의미 실행이 일어나지 않는다. 순서·연속 dynamics·stateful latch 같은 의미는 별도 규칙이 필요하다.
- **실행 근거:** `NOT_PROVEN`.

## N10 — Guarded Viability Field

- **지원 폭:** continuous/discrete hybrid state, viability/control proposal, symbolic authority guard, event/request lanes, pure contextual views, adapter-mediated Protocol switch에 특화되어 있다.
- **이질 Protocol 생존성:** **조건부.** verified adapter, conservative capability, 또는 observation-only admission이 필요하다. exact bytes/provenance는 보존할 수 있지만 semantics를 자동 실행하지 않는다.
- **충돌:** 여러 guard가 priority 없이 approve하면 `CONFLICT`이고 mutation하지 않는다. continuous confidence·utility·margin은 authority가 아니며 opposing situated judgments를 보존한다.
- **불변 / 가변:** no mutation without symbolic approval, provenance non-amplification, view/source 분리, exact lineage가 불변. mode·continuous state·declared `theta_R`는 가변. schema·guard·authority·status·`theta_S`는 successor다.
- **Persona / worldview:** principal–Persona–context–operation 교차점에서 capability를 확인하고 concurrent Persona proposal을 분리한다. switch는 observable/tolerance/horizon과 residue를 공개한다.
- **유연성의 성격:** **control/guard contract에 묶인 구조 유연성.** score나 similarity가 authority·semantic compatibility를 만들지 않는다.
- **상태 발생:** admissible value 부재는 `UNKNOWN`; 양립 불가 claim/guard는 `CONFLICT`; proof policy·solver certificate가 부족하면 `NOT_PROVEN`; predicate/adapter/authority semantics가 없으면 `OUT_OF_SCOPE`.
- **가장 강한 한계:** hybrid control에는 강한 접점을 제시하지만 provenance DAG·commitment·modal·novel pattern·causal intervention 같은 이질 의미는 adapter에 의존한다. 그 adapter와 held-out 실행은 없다.
- **실행 근거:** `NOT_PROVEN`.

## N11 — Polycentric Institutional Blackboard

- **지원 폭:** institutional rule, governance, authority, assessment/dissent, commitment, normative/operational effect, sandbox evaluator와 directional bridge를 다룬다.
- **이질 Protocol 생존성:** **조건부.** 각 Protocol의 local vocabulary/status를 그대로 두고 blackboard에서 공존시킨다. adapter가 없으면 manifest와 output은 `opaque`로 보존할 뿐 해석·실행하지 않는다.
- **충돌:** rival Assessment와 Dissent를 삭제하지 않는다. authority grant가 충돌하면 `authority_disputed`로 operational/constitutional commit을 막는다. decision Protocol은 Context의 제한된 matter에만 효력이 있다.
- **불변 / 가변:** pinned run, append-only correction, plurality, power intersection, bridge loss, predecessor history가 불변. Context activation·institutional Effect·Protocol lifecycle은 명시된 grant로 가변. meaning 변경은 successor다.
- **Persona / worldview:** Persona는 institutional standpoint이며 한 사람이 여러 Persona를, 여러 사람이 office Persona를 가질 수 있다. worldview description도 claim이므로 경쟁 기술과 함께 남는다.
- **유연성의 성격:** **다원적이지만 경계가 있는 유연성.** schema/resource/receipt/effect mediation의 작은 host kernel이 있고, Protocol이 authority를 스스로 확장할 수 없다.
- **상태 발생:** common `UNKNOWN`에 해당하는 경우는 `undetermined`; incompatible assessment/authority는 `contested/authority_disputed`; evaluator·replay·compatibility 의무 미확립은 `NOT_PROVEN`에 해당한다. adapter/bridge/context/authority 범위 밖은 `opaque/declined/OUT_OF_SCOPE`에 해당한다. local status가 primary라 공통 상태 mapping 자체가 손실 경계다.
- **가장 강한 한계:** 제도적 복수성과 책임 기록에는 강하지만 domain semantics를 스스로 제공하지 않는다. common mutation taxonomy와 N11의 institutional effect classes 사이 mapping, 그리고 mutable ProtocolInstance parameter/history가 미해결이다.
- **실행 근거:** `NOT_PROVEN`.

## N12 — Patch–Lens Ecology

- **지원 폭:** contextual read/view, typed path update, plural patch plan, round-trip/loss law, relation/event invalidation, Persona-specific view/write permission에 특화되어 있다.
- **이질 Protocol 생존성:** **조건부.** closed wire vocabulary의 manifest·optic·normalizer·effect를 검증하거나 named adapter를 사용한다. 미지원 schema/optic/effect는 typed refusal이다.
- **충돌:** overlapping patch precondition은 `PATCH_PRECONDITION_CONFLICT`; 여러 유효 plan은 `ALTERNATIVE_PLANS/MULTIPLE_VALID`로 유지하고 selector 없이는 commit하지 않는다. domain action conflict에는 별도 comparator가 필요하다.
- **불변 / 가변:** exact snapshot, typed path, before digest, mode separation, context binding, loss disclosure, lineage가 불변. runtime namespace/ledger는 runtime schema 안에서 가변. semantic patch는 새 snapshot·revision·lineage를 만든다.
- **Persona / worldview:** Persona별 readable/writable path와 mode를 계약으로 제한한다. 전환 시 hidden source를 삭제하지 않고 A→B→A 안정 path digest를 비교한다.
- **유연성의 성격:** **typed patch/optic 법칙으로 제한된 유연성.** family name이나 화면 유사성으로 adapter를 합성하지 않으며, 불명확한 write-back은 거절한다.
- **상태 발생:** context/source 값 부재는 `UNKNOWN`; claim 또는 patch precondition 양립 불가는 `CONFLICT`; law·proof·target 식별이 미확립이면 `NOT_PROVEN`; context/manifest/optic/effect 밖이면 `OUT_OF_SCOPE` 또는 typed refusal.
- **가장 강한 한계:** view↔source 변환에는 구체적이지만 causal/modal/commitment/hybrid/pattern/action-conflict 의미는 Protocol별 manifest·normalizer가 없으면 실행하지 못한다. stateful latch도 closed kernel에 없다.
- **실행 근거:** `NOT_PROVEN`.

---

## 검토 시 유지할 마지막 경계

- 종이 구조의 표현 가능성과 실제 실행 적합성을 분리한다.
- `NOT_PROVEN`을 실패·거짓·거절과 동일시하지 않는다.
- plural view 보존을 “아무 말이나 허용”과 동일시하지 않는다. 각 view에는 exact Protocol, context, Persona/worldview, evidence, provenance, effect boundary가 붙어야 한다.
- 어떤 선택도 동결 후보 원문을 소급 수정하지 않는다. 의미 변경은 successor 제안으로만 다룬다.

## Owner가 먼저 결정하면 분별력이 큰 질문

1. **라우팅 권한:** 별도 최소 router가 모든 eligible Protocol을 보존하고 이유와 함께 거절해야 하는가, 아니면 Protocol/Object 상호작용 안에서 activation이 생겨나도 되는가? 어느 경우에도 반드시 지켜야 할 routing invariant는 무엇인가?
2. **공통 불변량의 크기:** exact identity·provenance·effect separation·loss disclosure만 전 Protocol 공통으로 둘 것인가, 아니면 event order·authority·status·identity continuity까지 공통화할 것인가? 공통화할 수 없는 Protocol은 거절할 것인가, 격리 공존시킬 것인가?
3. **행동 충돌과 복수성:** 서로 반대되는 action proposal이 함께 유효할 때 기본 동작은 “둘 다 보존하고 실행 중지”인가? Context-scoped arbiter가 하나를 선택할 수 있다면, 누가 그 arbiter를 지정하고 dissent와 미선택안을 얼마나 오래 보존해야 하는가?
4. **합법적 runtime 변경의 판별:** 결과를 바꾸는 parameter patch라도 schema가 mutable로 선언되어 있으면 같은 ProtocolInstance의 새 runtime revision으로 볼 것인가? 어느 조건부터 새 semantic identity와 successor lineage를 강제할 것인가?
5. **Persona 간 정보 이동:** Persona/worldview는 완전 격리, shared-read-only, 또는 explicit bridge 중 무엇을 기본으로 할 것인가? 한 Persona의 결론·권한·runtime memory가 다른 Persona에 넘어갈 수 있는 최소 receipt와 authority 조건은 무엇인가?
6. **혼합 요청의 원자성:** harmless activation/view 설정과 금지된 semantic rewrite가 한 요청에 섞이면 전체를 사전검증해 전부 거절할 것인가, 허용된 prefix를 적용하고 항목별 receipt를 남길 것인가? 이 규칙은 외부 effect와 compensation에도 동일해야 하는가?
