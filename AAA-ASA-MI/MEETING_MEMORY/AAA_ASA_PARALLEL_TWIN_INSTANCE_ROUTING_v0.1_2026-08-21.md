# AAA-ASA Parallel Twin Instance Routing v0.1

DATE = 2026-08-21 KST
PROJECT = AAA
PRODUCT = ASSET AGENT ASA
STATE = NON_NORMATIVE / EXECUTION_ROUTING_PROPOSAL / NOT_PERSONA_REGISTRATION / NOT_VALIDATION

## Owner proposal

Owner asked whether the current ASA-MI model-research stream and the Owner Delegate / Judgment Proxy stream should proceed in parallel through ASA clone/twin instances.

## Recommended structure

Use temporary ASA execution instances rather than immediately registering two new persistent organizational Personas.

- `AAA-ASA-TW-MODEL` — temporary ASA twin for model-research continuation.
  - Mission: review the completed 8-position pilot, manage `SOURCE_REBASELINE + SMALL_DISCRIMINATING_IMPLEMENTATION_CYCLE`, coordinate model-result review and next research design.
  - May read full model-research artifacts, evaluator receipts, rankings, and research synthesis.

- `AAA-ASA-TW-ODP` — temporary ASA twin for Owner Delegate Proxy core research.
  - Mission: prior-art synthesis, historical Owner decision audit, multi-proxy ecology, memory/interview design, first Shadow experiment preparation.
  - MUST NOT receive current model candidate rankings/evaluator conclusions before Proxy predictions for the first Shadow scene are frozen.

- `AAA-ASA` — primary Owner-facing integrator.
  - Mission: reconcile outputs, preserve authority boundaries, route validation, and manage Owner decisions.
  - Should not convert either twin's output into Owner authority or validation PASS.

Channel/execution instance is not a new persistent Persona by default. `Channel != Persona` remains controlling.

## Contamination barrier for first Shadow experiment

The model-research twin may know full current model results.
The ODP twin must remain blind to final candidate rankings, evaluator conclusions, Track labels, and known champion status until all Proxy predictions are frozen.

After Proxy freeze, a separate blind Owner interview should be conducted using neutral candidate briefs. For strongest contamination control, the interview conductor should not see Proxy predictions before the Owner's first judgment is frozen.

## Validation separation

Neither ASA twin is an independent validator. Formal validation remains with the applicable paired validator and, where required, AAA-VALIDATION-AUDITOR.

## Five-line summary

현재 상태: 모델연구와 Owner Delegate Proxy 연구를 두 개의 임시 AAA-ASA 분신 실행 인스턴스로 병렬화하는 구조를 제안했다.
핵심 판단: 새 상설 Persona 두 개를 즉시 등록하기보다 `AAA-ASA-TW-MODEL`과 `AAA-ASA-TW-ODP`를 임시 실행 인스턴스로 운용하고 본체 AAA-ASA가 통합하는 편이 안전하다.
진행 작업: 첫 Shadow 실험을 위해 모델연구 Twin은 전체 결과를 볼 수 있지만 ODP Twin에는 Proxy prediction 동결 전 ranking/evaluator 결론을 차단하는 contamination barrier를 둔다.
다음 단계: 두 Twin용 각각의 한 번 복사형 생성/승계 패킷을 만들고, 이후 Owner blind interview는 Proxy 답을 보지 않은 별도 interview conductor로 진행하는 방안을 준비한다.
사용자 행동: 두 병렬 Twin 구조를 승인하면 바로 `AAA-ASA-TW-MODEL`과 `AAA-ASA-TW-ODP` 생성 패킷을 각각 제공한다. 작성시각: 2026-08-21 15:58 KST
