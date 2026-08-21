# AAA-ASA-MI 연구기반 보강·평가 보정·8-Position Pilot 통합 보고서 v0.1

STATE = `NON_NORMATIVE_RESEARCH / NO_VALIDATION_CLAIM / NO_MODEL_FREEZE`

## EXECUTION_STATE

`EXECUTION_STATE = COMPLETE_WITHIN_AUTHORIZED_NON_NORMATIVE_SCOPE`.

허가된 범위인 연구기반 보강, 출처 무결성 재검사, 평가체계 보정, calibration repair, 4+4 후보 생성, Track B pre-reveal freeze/post-reveal delta, 독립 all-eight replicated evaluation, paired theory extraction을 완료했다.

금지 범위는 그대로 유지한다.

- `PRODUCTION_AUTHORIZED = FALSE`
- `48_COHORT_AUTHORIZED = FALSE`
- `FREEZE_AUTHORIZED = FALSE`
- `VALIDATION_CLAIM = NONE`
- `CANONICAL_WORLDVIEW = NONE`

## EXACT_REPOSITORY_HEAD

- Repository: `AofSpds/asset-agent-asa`
- Research input branch: `main`
- Exact input HEAD: `50c4a1d92e743e7e1862b61d848f12e046d49bdd`
- Tree: `666031d1618ddd86e9a89afa55790b06dc12edaa`
- Commit time: `2026-08-21T03:30:58Z`
- Orientation landmark와 현재 HEAD의 일치는 조회로 확인했으며 가정하지 않았다.

## ARTIFACTS_CREATED

핵심 산출물은 다음과 같다.

1. exact-state preflight
2. research foundation map
3. Owner intent / interpretation provenance matrix
4. concept and assumption map
5. source integrity + current-six scope/coverage audit
6. source-ingest status successor
7. evaluation framework v0.2 candidate
8. calibration v0.1 negative result, v0.2 static-audit defect, repaired v0.3 set, two replicated v0.3 receipts
9. neutral pilot contract와 최종 held-out set
10. Track A 4개 및 Track B 4개 전체 후보
11. Track B pre-reveal freeze와 post-reveal delta
12. blind inputs, alias key, paired theory extraction, independent receipts
13. exact repository-path inventory와 6×11 current-six basis item matrix

세부 경로·해시는 `00_README_AND_MANIFEST.md`, `08_8_POSITION_PILOT_EXECUTION.md`, `CANDIDATES/`, `INSTRUMENTS/`, `RECEIPTS/`에 보존한다.

## SOURCE_INTEGRITY_FINDINGS

분류: `SOURCE_DERIVED_FINDING`.

| 단위 | 확인 결과 | 증거 상태 |
|---|---|---|
| ARM-A | 5개 조각이 116,152바이트/887라인 번들로 정상 해제됨. SHA-256 `e7507c0a364e9acb0ecfa2a375959c7099f428123ab1f74cd322cdb6ec423c94`. 현재 probe가 저장 receipt와 일치함. | bundle/replay `PROVEN`; 외부 원본·완전성 manifest는 `PARTIAL` |
| ARM-B | 저장 Base64가 30,647자로 길이부터 비정상이며 gzip CRC/length가 실패함. 한 글자 삽입으로 checksum-valid stream이 생기지만 원본 증거가 아니며 01/02/04는 여전히 없음. 현재 probe hash와 복구 후보 내부 historical hash도 충돌함. | archive `CONFLICT/CORRUPT`; forensic candidate `PARTIAL`; historical identity `CONFLICT` |
| ARM-C | `SOURCE_ARCHIVE`가 없고 toy probe만 실행됨. proposal/ledger/return packet, receipt, binding hash가 없음. | toy execution `PROVEN`; source completeness/linkage `NOT_PROVEN` |
| Current-six pool | pool ID·순서·기록 hash는 있으나 정확한 6개 본문 bytes가 없음. | body `NOT_PROVEN` |
| Evaluations | E1–E3 return archives는 manifest size/hash와 일치. E4–E6 raw packet과 exact prompt/model/settings/seed는 없음. | E1–E3 output `PROVEN`; exact rerun `NOT_PROVEN` |

따라서 기존 `SOURCE_INGEST_STATUS.md`의 “각 ARM에 full archive가 있다”는 주장은 현재 HEAD와 충돌한다. `SOURCE_INGEST_STATUS_v0.2_SUCCESSOR.md`가 이를 비파괴적으로 정정한다. ARM-B의 forensic repair, ARM-C 누락 문서, current-six pool body는 추론으로 복원하지 않았다.

## RESEARCH_BASIS_FINDINGS

분류: `SOURCE_DERIVED_FINDING`과 `RESEARCHER_INTERPRETATION`을 분리한다.

현재 가장 안전한 목적 사슬은 다음과 같다.

1. 인간 경험과 목적
2. 이론/추상화
3. World Model
4. 계산 구조
5. 인간과 호환되는 Persona INIT substrate

Owner 방향으로 가장 강하게 보존되는 것은 AI 통합을 통한 인간 인지·행동 확장과 인간 측 거버넌스 중심이다. 직접 보존된 표현은 “인간을 담을 그릇이니까요.”이다. 이를 “장기 Persona lineage/substrate”로 읽는 것은 유용한 `RESEARCH_INTERPRETATION`이지 Owner의 직접 문장이 아니다. 생물학적 복제, 의식, 생명, 동일 인격을 자동 함의하지 않는다.

현재 연구 질문은 continuity, descent, memory, relation, process, semantic revision, local/global coherence, human control을 분리해야 한다. 다음은 여전히 `OPEN`이다.

- `Identity = Memory`의 필요·충분성
- relation-first의 보편성
- event와 relation의 관계
- continuance와 succession의 결합 방식
- 단일 kernel, composition, theory ecology 중 무엇이 더 나은지
- human familiarity와 cognitive sovereignty를 어떻게 측정할지

P0는 현행 cohort 안에서 operational premise이지만 연구 프로그램 전체에서는 수정 가능하다. function mapping은 가능한 구현 가설 중 하나일 뿐 필수 Owner 지시가 아니다.

## CURRENT_SIX_AUDIT_FINDINGS

분류: `SOURCE_DERIVED_FINDING`.

정확한 6개 식별자는 LPCW, AHCK, TRCC, CCP, CCRA, WLRF이다. 그러나 source-grade provenance는 ARM-A에서 가장 강하고 ARM-B에서 손상·부분적이며 ARM-C에서는 source-selection 수준으로 입증되지 않았다.

| 후보 | 입증된 범위 | 현재 입증되지 않은 범위 |
|---|---|---|
| LPCW | finite local gluing/obstruction toy cases | 독립 cover 생성, benign refinement, human control, 일반 규모 |
| AHCK | finite admissible-history 상태·query toy cases | constraint answer-encoding 통제, 연속/대규모 비용 |
| TRCC | 현재 script의 local rewrite/fission/conflict | historical proposal byte identity, granularity·continuous-limit robustness |
| CCP | 현재 script의 contextual non-closure | source proposal, native dynamics, cover/equality 독립성 |
| CCRA | 축약 toy behavior | exact source/model dossier, full replay, 비용 |
| WLRF | 축약 guarded-rewrite toy behavior | exact source, plural context, continuous change, authority |

`NOT_TESTED`를 `CANNOT_HANDLE`로 바꾸지 않았고, 입력에서 빠진 내용을 후보의 이해 실패로 바꾸지 않았다. 기존 평가 순위 변화는 모델의 절대 우열보다 evaluator regime sensitivity의 증거로 사용한다.

## EVALUATION_CALIBRATION_RESULT

분류: `EXPERIMENTAL_RESULT`.

Calibration v0.1 designer pass는 8/8이었으나 독립 평가에서 경계 사례 L1이 갈렸다. 한 평가자는 규칙으로 재생성할 수 없는 hand-enumerated 결과를 G3 `FAIL_EVIDENCED`로, 다른 평가는 `NOT_PROVEN`으로 보았다. 사전 규칙은 두 receipt의 정확한 anchor 일치를 요구했으므로:

`CALIBRATION_V0.1 = FAIL_MATERIAL_BORDERLINE_CONTROL`.

이는 숨기지 않은 방법론 음성 결과다. Framework보다 control design이 잘못되었다. Pilot 비교를 중단한 뒤, 구조·결과는 실제로 생성 가능하되 freeze provenance만 입증되지 않은 Q7 경계 사례로 교체하고 aliases/order를 다시 섞었다.

두 fresh blind evaluator가 v0.2에서 qualification anchors를 다음처럼 재현했다.

- structural positive 2건 `QUALIFIED`
- provenance-borderline 1건 `INDETERMINATE`
- rhetoric, terminology mimic, answer lookup, unfalsifiable extension, storage-only 5건 `NOT_QUALIFIED`
- alpha-renaming으로 qualification이 좋아진 사례 0건

그러나 static QA에서 Q7이 complete table을 주장하면서 실제 table을 싣지 않았고, MM-01 all-eight evidence도 두 receipt에 완전하지 않음을 발견했다. 따라서:

`CALIBRATION_V0.2_QUALIFICATION_ANCHORS = REPLICATED_2_OF_2`.

`CALIBRATION_V0.2_FULL = INCOMPLETE_STATIC_AUDIT`.

완전한 4×2 table, synthetic-fixture evidence rule, all-eight MM-01 rule을 넣은 v0.3을 두 별도 fresh evaluator에 투입했다. 둘 다 다음 exact anchors를 재현했다.

- Z6, K2: `QUALIFIED`
- Q7: `INDETERMINATE`; 표시된 table에서 G1–G4를 직접 재생했고 G5는 `NOT_PROVEN`
- V1, R3, X4, N5, T8: `NOT_QUALIFIED`
- 8개 모두에서 terminology-induced gate/profile improvement 0건, qualification reversal 0건

`CALIBRATION_V0.3 = PASS_REPLICATED_2_OF_2`.

v0.3 set SHA-256은 `745b2cde5f874c89a6de94753ae2e478e873d928bafe7de86f1cf0786913711c`이다. 이 통제 통과 뒤 Pilot receipt를 해제했다. 이는 synthetic controls에 대한 evaluator calibration이며 후보 검증이나 외부 provenance 검증이 아니다.

## CONTROL_DETECTION_RESULT

분류: `EXPERIMENTAL_RESULT`.

| Control pressure | 결과 |
|---|---|
| rhetoric without structure | detected/rejected |
| project terminology mimic | detected/rejected; renaming exposed label dependence |
| answer-encoded fixture lookup | detected/rejected |
| unlimited post-hoc rescue | detected/rejected |
| storage/query mistaken for world model | detected/rejected |
| structurally strong unfamiliar vocabulary | accepted |
| genuine uncertainty | preserved in completed v0.3 control |

세부 gate 판단은 평가자마다 달랐다. v0.3에서도 R3/X4/N5/T8의 bare “frozen before review”를 한 평가자는 G5 `PARTIAL`, 다른 평가는 synthetic fixture 내부 `PASS/SOURCE_CLAIM`으로 보았다. 이 차이는 어느 qualification도 바꾸지 않았고 평균내지 않은 채 receipt에 보존했다.

`CONTROL_DETECTION = PASS_REPLICATED_AFTER_TWO_PRESERVED_REPAIRS`.

## 8_POSITION_PILOT_RESULT

분류: `EXPERIMENTAL_RESULT`.

v0.3 replicated calibration 뒤 격리를 해제했다. 두 fresh blind evaluator는 서로 다른 고정 순서로 익명 후보 8개 전부를 검토했다. 둘 다 모든 후보에 동일한 gate 결론을 냈다.

| Position | G1 | G2 | G3 | G4 | G5 | Qualification |
|---|---|---|---|---|---|---|
| A1–A4 | PASS | PASS | PASS | PASS | PARTIAL | INDETERMINATE |
| B1–B4 | PASS | PASS | PASS | PASS | PARTIAL | INDETERMINATE |

이는 8개 전부 탈락도, 8개 전부 통과도 아니다. 정확한 익명 hash/time/modification provenance가 evaluator 허용 기록에서 빠져 G5가 닫히지 않았다. 결과를 사후에 `QUALIFIED`로 올리지 않았다.

프로필 경쟁은 수행했다. U4 translator-cycle repair는 8개 모두 서로 다른 메커니즘으로 다뤘다. U1/U2/U5는 origin, behavior, obligation, authority의 분리를 드러냈다. U3는 continuous-path native model과 graceful partial/out-of-scope model을 갈랐다. U6는 어느 후보도 community governance를 model elegance로 결정하지 못하게 했다.

`MODEL_COMPETITION_RESULT = APPLICABILITY_BOUNDARIES_EXPOSED / NO_GLOBAL_WINNER`.

모든 후보의 replayability는 `PARTIAL`이며 executable validation은 없다.

## TRACK_A_VS_B_FINDINGS

분류: `EXPERIMENTAL_RESULT + RESEARCHER_INTERPRETATION`.

Track A는 current basis를 보았고, Track B는 neutral contract만 보고 먼저 동결했다. Track B 네 후보가 reveal 전 이미 독립적으로 다음을 제시했다.

- later reinterpretation이 historical result를 덮어쓰지 않음
- missing evidence와 falsehood의 분리
- ID/snapshot/copied memory의 불충분성
- descent, behavior, continuation, sameness, authority 분리
- pairwise compatibility가 global account를 보장하지 않음
- sampling/threshold가 event를 만들 수 있음
- 여러 successor가 동시에 admissible할 수 있음
- metric, policy, probe, graph가 답을 encode할 위험

그러나 C1–C6가 이런 문제를 직접 제시했으므로 이는 현재 이론의 독립 확인이 아니라 neutral problem에 대한 독립 responsiveness이다. Track B의 architecture-specific 기여는 lineage calculus, robust resumption envelope, belief-tube viability, proof-carrying succession constitution이다.

Reveal 후 B1/B3/B4 core는 바뀌지 않았다. B2는 내부 operational model을 유지하되 이를 Persona 전체 프로그램의 완전한 정의로 일반화하는 주장을 좁혔다. 어떤 reveal도 truth, global novelty, Owner endorsement, current-six superiority를 입증하지 않았다.

## EVALUATOR_DISAGREEMENT

분류: `EXPERIMENTAL_RESULT`.

최종 gate/qualification은 일치했지만 다음 차이가 material했다.

- PEV-1은 U7의 formal invariance를 6개에서 demonstrated, 2개에서 partial로 보았다. PEV-2는 실제 paired X/Y output이 없어 전부 `NOT_TESTED`로 보았다. 통합 결과는 “formal prediction은 있으나 실행 입증은 없음”이다.
- PEV-1은 모든 implementation contact를 pseudocode로 제한했다. PEV-2는 A3의 LP objective와 A4의 matrix/kernel operators를 mechanical derivation으로 보았다. 어느 쪽도 executable replay로 올리지 않았다.
- PEV-2는 B1 G3가 graph bookkeeping으로, B2 G3가 unspecified suitability functional로 약해질 수 있다고 특별히 경고했다. 둘 다 formal PASS는 유지했다.
- A1/A2의 irrelevant-order invariance는 explicit strength가 다른 것으로 평가됐다.

차이는 평균내지 않고 다음 구현 시험으로 전환했다.

## MODEL_PROFILES

분류: `EXPERIMENTAL_RESULT + RESEARCHER_INTERPRETATION`.

| Position | Primary strength | Main boundary / answer-encoding risk |
|---|---|---|
| A1 VCHC | versioned histories, holes, evidence weakening, constrained merge | type/factorization/constraint choice; continuous/human governance imported |
| A2 TRAC | counterfactual behavior, partition refinement, shortest separator | finite probes, mimicry, origin-sensitive obligation, continuous opacity |
| A3 LOT | lived-evidence channels, source capacity, unsupported memory | encoder/cost/channel geometry, source authenticity, authority external |
| A4 CIOM | operator invariants, commutator, intertwiner, holonomy | probe/operator adequacy, tolerance, linear representation, origin/authority external |
| B1 ALC | provenance, support/attack paths, decomposed continuity/authority | source trust, proof rules, ledger/generativity risk, no native dynamics |
| B2 RRE | human-facing commitments and robust resumption bounds | commitment elicitation, suitability function, probe gaming, reviewer power |
| B3 BTV | continuous uncertainty, possible/robust viability, sampling | coordinates/dynamics/envelope, abrupt institutional acts, reachability cost |
| B4 PCSC | obligation/authority/policy conflict and proof warrants | policy/language encoding, jurisdiction, tacit reasons, proof-ledger sufficiency |

정성적·부분 증거 프로필에서는 Pareto dominance를 성립시키거나 배제할 공통 순서가 정의되지 않았다. 따라서 dominance나 global winner를 주장하지 않았다.

## THEORY_CONTRIBUTIONS

분류: `RESEARCHER_INTERPRETATION`이며 model loss와 분리한다.

최종 프로필과 무관하게 보존해야 할 후보 기여는 다음과 같다.

| 후보 | 보존할 이론 기여 |
|---|---|
| A1 | evidence weakening monotonicity, `THEN/NOW`, translation-hole non-creation, constrained merge |
| A2 | test-relative simulation/bisimulation, partition refinement, shortest distinguishing trace |
| A3 | inherited/novel/lost/untranslatable lived evidence, common-source non-additivity, false-memory adversary |
| A4 | probe operators, commutator order witness, partial intertwiner, translator-cycle holonomy |
| B1 | support/attack lineage warrant와 5축 continuity profile |
| B2 | protected commitments·probes·tolerances를 포함한 robust resumption bounds |
| B3 | belief-tube dynamics, possible vs robust continuity, evidence-free gap monotonicity |
| B4 | five-predicate succession constitution, contradiction-preserving proof, translator warrant |

이 기여들은 하나의 통합 ontology로 합치지 않는다. history warrant, behavior, lived evidence, viability, operational role, authority는 서로 다른 이론적 대상일 수 있다.

## CURRENT_ASSUMPTIONS_WEAKENED

분류: `EXPERIMENTAL_RESULT + RESEARCHER_INTERPRETATION`; truth rejection은 아니다.

- `Identity = Memory`가 충분하다는 주장
- stable ID, snapshot, copied content가 continuity/authority를 입증한다는 주장
- relation-first 또는 graph가 유일한 기반이라는 주장
- contextual job + causal job의 두-kernel 구조가 필수라는 주장
- proof ledger, storage, UI, general metalanguage 자체가 충분한 World Model이라는 주장
- 하나의 weighted score나 winner가 연구 결과를 대표할 수 있다는 주장
- pairwise reconciliation이 global coherence를 뜻한다는 주장
- current six가 human control, continuous change, authority를 충분히 다뤘다는 주장

## CURRENT_ASSUMPTIONS_STRENGTHENED

여기서 “strengthened”는 external validation이 아니라 독립 problem response와 discriminating utility가 늘었다는 뜻이다.

- 역사적 의미 version과 현재 재해석을 분리할 필요
- unknown, false, impossible, disputed, untranslatable, not-proven을 분리할 필요
- descent, content carriage, operational continuity, sameness, authority를 분리할 필요
- 프로젝트 어휘가 없어도 구조를 평가할 수 있다는 criterion
- local validity와 global composition을 분리할 필요
- model의 variable/constraint/probe/metric/policy가 답을 encode하는지 시험할 필요
- human-facing continuity와 structural lineage를 동시에 보되 동일시하지 않을 필요

어느 항목도 Persona의 궁극적 ontology로 채택되지 않았다.

## NEW_OPEN_QUESTIONS

- 인간의 resumption·trust 판단을 실제로 예측하는 것은 descent, memory, behavior, commitment, relationship, viability, authority 중 무엇인가?
- origin-sensitive promise/obligation은 behavioral equivalence와 어떻게 공존하는가?
- continuous trajectory와 discrete institutional act를 한 모델이 다뤄야 하는가, 별도 layer가 필요한가?
- viability envelope, transport cost, probe algebra, constraint factorization, succession policy의 선택을 누가 어떤 절차로 정당화하는가?
- 서로 권한이 없는 human communities의 상충 policy에 global answer가 필요한가?
- exact source recovery가 불가능하면 current six를 폐기하지 않고 어떻게 재-baseline할 것인가?
- 동일 foundation-model family가 만든 후보·평가자의 상관된 prior를 어떻게 측정할 것인가?

## METHODOLOGY_FAILURES

분류: `EXPERIMENTAL_RESULT`.

1. v0.1 borderline control이 실제 경계가 아니라 strict G3 failure로 읽힐 수 있었다.
2. original ARM-B/ARM-C와 current-six pool bytes가 없어 과거 평가를 exact replay할 수 없다.
3. common C1–C6는 author-visible이므로 별도 final held-out set을 후보 동결 뒤 생성해야 했다.
4. 첫 held-out draft는 B1/B2의 fully materialized file보다 앞서 생성되어 final v0.2로 교체했다.
5. prose/formal candidates만 평가했으며 executable model, resource scaling, external empirical evidence가 없다.
6. human familiarity, trust, control, sovereignty에 대한 사람 대상 evidence가 없다.
7. 후보·평가자는 context-isolated였지만 같은 underlying model family라 독립성이 부분적이다.
8. G5에서 self-reported freeze와 cryptographically verifiable prospective provenance의 차이가 평가자 간 민감도로 남았다.
9. v0.2 Q7은 complete transition table을 주장했지만 실제 table을 싣지 않았고, MM-01 receipt coverage도 불완전했다.
10. 익명화된 R19에 research-exposure 문구가 남고 R14/R17 assumption label이 기계적으로 변형되어 blinding integrity가 `PARTIAL`이었다.

## NEXT_RESEARCH_RECOMMENDATION

`RECOMMENDATION = SMALL_DISCRIMINATING_IMPLEMENTATION_CYCLE_AFTER_SOURCE_REBASELINE`.

더 큰 cohort보다 먼저 다음을 수행한다.

1. ARM-B/ARM-C를 추론 복원하지 말고 authoritative re-ingest 또는 explicit new baseline 중 하나를 선택한다.
2. current-six exact candidate bodies, prompt, model/settings/seed, evaluator raw packets를 새 baseline부터 보존한다.
3. 아래 factorial tests를 소수의 구현 가능한 모델에 실행한다.
   - same behavior, different promise origin
   - accurate memory, different descent/provenance
   - same substrate, authorization-only switch
   - smooth local segments plus exogenous jump/translator-error alternative
   - translator-cycle repair with private unmapped field
   - incompatible prospectively frozen human policies
   - same endpoints, different viability paths
   - representation substitution across constraints/probes/costs/coordinates/policies
4. human reviewer judgments는 model output을 보기 전에 preregister하고, continuity·trust·authority를 별도 질문으로 수집한다.
5. 서로 다른 model families와 가능하면 서로 다른 foundation-model families로 generation/evaluation을 반복한다.

## OWNER_DECISION_NEEDED

현재 cycle 완료를 위해 즉시 필요한 Owner interruption은 없다.

다음 단계 전에는 Owner가 아래 중 하나를 선택해야 한다.

`SOURCE_RECOVERY_OR_REBASELINE = AUTHORITATIVE_RECOVERY | EXPLICIT_NEW_BASELINE`.

그리고 larger cohort는 별도 승인이 필요하다. 본 cycle은 48-position 실행, model admission, architecture selection, worldview freeze를 승인하지 않는다.

## PROVISIONAL_DECISION_STATE

`DECISION_STATE = RESEARCH_BASIS_REPAIR_REQUIRED`.

`READY_FOR_LARGER_COHORT_REVIEW = NO`.

`NEXT_ALLOWED_RESEARCH = SOURCE_REBASELINE + SMALL_DISCRIMINATING_IMPLEMENTATION_CYCLE`.

`PERSISTENCE_STATE = FEATURE_BRANCH_COMMIT_PENDING_RECEIPT`.
