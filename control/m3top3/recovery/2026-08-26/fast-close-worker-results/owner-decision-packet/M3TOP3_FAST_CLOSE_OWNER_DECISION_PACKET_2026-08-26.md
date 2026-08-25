# M3Top3 FAST-CLOSE Owner decision packet

```text
PROJECT = AAA / ASSET AGENT ASA
PERSONA = AAA-PMO-ORCHESTRATOR (PMO)
PACKET_CLASS = NON_VALIDATOR / OWNER_SEMANTIC_DECISION
ISSUED_AT_KST = 2026-08-26T01:35:59+09:00
FAST_CLOSE_PROGRESS = [██░░░░░░░░] 21% (21/100 EWU)
VALIDATOR_HOLD = TRUE
GLOBAL_VALIDATION = PROHIBITED
VALIDATION_LOOP = PROHIBITED
GIT_OR_ISSUE_MUTATION = NONE
GATE_EFFECT = NONE
```

## A. Owner가 지금 결정할 수 있는 네 항목

가장 빠른 권고 응답은 아래 네 줄이다.

```text
OD-G3-B-01 = YES
OD-G3-C-01 = YES
OD-G3-CAL-01 = YES
OD-G3-WIN-01 = YES
```

| ID | `YES`로 고정되는 내용 | `YES` 직후 실행 | `NO`일 때 필요한 답 / 영향 |
|---|---|---|---|
| `OD-G3-B-01` | 현재 Open과 동일 종목 직전 관측 Close의 절대 변화가 `>=20%`이면 Axis-B 신호. 반올림 없음, 신호만 생성하며 CA·조정은 추론하지 않음 | 1,822,019행 bounded Axis-B scan 후보 생성; P50 0.75h / P90 1.5h | 대체 `threshold_bps`와 inclusive/exclusive 경계가 없으면 Axis B HOLD |
| `OD-G3-C-01` | 열거된 KRX CA taxonomy, exact-date match, correction lineage, zero-unresolved exhaustion 규칙 | 프로토콜을 고정하고 exact independent KRX CA bytes 도착 시 reconciliation; P50 1.0h / P90 2.5h | taxonomy/scope/match/exhaustion의 정확한 변경값이 없으면 Axis C HOLD |
| `OD-G3-CAL-01` | exact official KRX equity regular-session artifact(또는 명시된 동등 권위)를 normative calendar로 사용; price-date union은 진단 전용 | exact calendar bytes 도착 시 calendar/window reconciliation; P50 0.5h / P90 1.0h | 대체 권위 source와 market/session 범위가 없으면 calendar HOLD |
| `OD-G3-WIN-01` | SHA-256 `96d63cc98a01b6332cf9486440e7f3fdaa0ec5a2d605f21bc14a4025b46e69fe`의 W1-W8 8행을 outcome-exposed development registry로만 ratify하고 별도 authority binding 작성을 허가 | Owner-authority binding 후보 작성; clean holdout/OOS 또는 release 주장은 생성하지 않음 | 대체 8개 tuple 또는 exact upstream source/locator가 없으면 date authority HOLD |

네 답은 **규칙만 고정**한다. 누락된 source bytes, 역사적 사실, receipt,
annotation 또는 gate PASS를 만들지 않으며 validation도 시작하지 않는다.

## B. Owner 결정으로 만들어낼 수 없는 source/custodian 입력

| 입력 | 현재 exact 상태 | 입력 도착 시 다음 실행 |
|---|---|---|
| G1 exact v0.1/v0.2 research-package ZIP bytes | `NOT_FOUND`; custodian exhaustion `NOT_PROVEN` | exact byte/hash/readback 후 scorer/config/input semantics 추출. exhaustion 증명만 도착하면 irrecoverability를 봉인할 뿐 G1 PASS는 아님 |
| G2 documentary raw evidence | 광고된 34 excluded cells open; 별도 technical `PX-004-L`까지 세면 unresolved protocol row는 35 | exact bytes/header/hash/access clock을 해당 cell에만 bind; 기존 sealed documentary receipt는 재실행하지 않음 |
| G2 historical business-priority evidence | combined-open 514 모두 BP unresolved (`500 NEEDS_RESEARCH + 14 PARTIAL`) | cutoff-safe company validity interval로 확장 후 514 cell 재계산 |
| G2 authoritative listing history | listing/tradability open 469; positive Entry Open은 listing authority가 아님 | BP-TRUE subset에만 listing/relisting/delisting와 Entry state를 join |
| W1-W8 upstream tuple provenance | local 8/8 concordance만 존재; upstream authority 없음 | exact source/locator가 오면 tuple authority bind. 위 `WIN=YES`는 development-use authority만 만들며 retroactive clean holdout은 만들지 않음 |
| G3 predecessor standalone manifest | expected SHA-256 `56d36d51e9f7b8870aa75cc41ee241603f6cf7446cb2386187c6ebcbb88b73c4` declaration만 회수; exact bytes `NOT_FOUND` | exact bytes가 오면 predecessor identity bind; forward manifest로 impersonation 금지 |
| Independent KRX CA event universe | exact export/query bytes와 custodian receipt 없음 | `C=YES` 규칙으로 Axis-C exhaustion candidate 생성 |
| Normative KRX calendar | exact official bytes와 authority receipt 없음 | `CAL=YES` 규칙으로 governed calendar candidate 생성 |
| G3-E historical annotation evidence | 1,016 rows × 17 fields = 17,272 slots; locally recoverable content `0`, admitted rows `0` | cutoff-safe source bundles를 queue에 ingest하고 dual coding/adjudication. true completion ETA는 현재 측정 불가 |

모든 G2 missing input이 들어온 뒤 worker-only G2 후보 조립은 P50
1.5–2.5h / P90 4–5h이다. 네 G3 결정과 KRX CA/calendar bytes가 모두
들어온 뒤 B/C/calendar 후보 조립은 P50 2.25h / P90 5h이다. 외부
custodian wait와 annotation 본 수집은 이 시간에 포함되지 않는다.

## C. 선택적 major scope-rebase escape hatch — 비권고 / 고위험

기본값:

```text
OD-MAJOR-REBASE-01 = NO
```

`YES`는 누락 증거를 통과시키는 예외가 아니다. 기존 exact-v1 역사적
127×8 closure 목표를 중단하고, 현재 회수 가능한 bytes로 **새 버전의
outcome-exposed development baseline**을 설계하는 별도 program rebase다.

`YES`의 즉시 효과:

1. 현재 G1/G2/G3 FAST-CLOSE route를 `REBASE_DESIGN_HOLD`로 전환한다.
2. 새 Universe/기간/annotation 범위/denominator/window 계약과 기존
   receipt의 재사용 가능 범위를 별도 명세한다.
3. 기존 exact-v1 gate나 clean holdout/OOS를 PASS로 간주하지 않는다.
4. 새 exact target이 실제 생성될 때만 최소 exact-delta validation을
   요청할 수 있다.

주요 위험은 old/new benchmark 비교 단절, outcome exposure, annotation 또는
모델 의미 변경, 기존 receipt의 범위 불일치다. 따라서 source recovery가
현실적으로 불가능하다는 증거와 Owner의 명시적 scope 선택 없이는 실행하지
않는다.

## D. 정확한 효과·claim ceiling·validation 경계

- 네 `YES`가 모두 오면 PMO는 protocol binding과 Axis-B scan을 즉시 시작한다.
  Axis-C와 calendar는 source bytes가 올 때까지 기다린다.
- source가 하나만 오면 해당 exact lane만 실행한다. 다른 lane이나 전체 suite를
  재실행하지 않는다.
- G3-E queue/schema 1,016행은 재사용한다. 17,272-slot global re-scan이나
  validation loop는 금지한다.
- 현재 validation closure delta는 `0`; G4의 봉인된 finding/receipt만 원래
  범위에서 유지한다.
- 향후 exact G1/G2/G3 closure candidate와 sealed G4가 한 pinned base에 모이고
  Owner가 validator HOLD를 해제한 경우에만 `FC2+FC3` exact-delta validation
  1회를 허용한다: P50 15–30m, P90 45–60m, hard stop 60m, 자동 재시도 없음,
  exact fix 후 실패 check만 최대 1회 재실행.
- 어떤 답도 G1/G2/G3 또는 integrated G1-G4 PASS, EOPT-G0 PASS, A/A,
  predictive power, Golden, Replay, Freeze, Champion, Promotion, Release,
  Production 또는 optimization-effectiveness 주장을 만들지 않는다.

