# Owner Directive — Progress Bar Execution Design

PROJECT = AAA
PRODUCT = ASSET AGENT ASA
PERSONA = AAA-ASA (ASA)
RECEIPT_CLASS = OWNER_DIRECTIVE_CONTINUITY_NOT_AUTHORITY_SOT
TIME_KST = 2026-08-25 13:16 KST

## OWNER DIRECTIVE
다음 작업부터 실행 설계에 실제 진행률을 표현할 수 있는 Progress Bar / Progress Telemetry를 포함한다.

## REQUIRED DESIGN PRINCIPLES
1. 실행 시작 전에 전체 scope와 progress denominator를 freeze한다.
2. 전체 프로그램 진행률과 현재 phase/gate 진행률을 분리한다.
3. WBS/WP/Gate별 measurable work units, weights, terminal states를 사전에 정의한다.
4. 진행률은 추정 문구가 아니라 machine-readable progress state에서 계산한다.
5. 각 subtask는 NOT_STARTED / IN_PROGRESS / BLOCKED / VALIDATING / DONE / SUPERSEDED 중 하나의 상태를 가진다.
6. DONE은 required evidence/receipt closure를 만족한 경우에만 인정한다.
7. scope 추가/삭제 시 기존 퍼센트를 조용히 바꾸지 않고 REBASE 이벤트와 old/new denominator를 기록한다.
8. Progress UI/report는 최소한 OVERALL %, CURRENT_PHASE %, done/total units, current gate, blockers, elapsed time, ETA range(if measurable), last progress event를 표시한다.
9. 장기 실행에서는 wall-clock 및 가능하면 token/cost telemetry도 같이 기록한다.
10. ETA는 충분한 실측 throughput이 없으면 UNKNOWN으로 표시하고 임의 추정하지 않는다.
11. progress state는 append-only event log + current projection 형태로 저장한다.
12. 검증/재검증 때문에 작업이 재개방되면 REOPENED event를 기록하고 progress confidence를 별도로 낮춘다. 가짜 monotonic progress를 만들지 않는다.

## RECOMMENDED ARTIFACTS
- EXECUTION_PROGRESS_PLAN_v1.0.md
- EXECUTION_PROGRESS_WEIGHTS_v1.0.json
- EXECUTION_PROGRESS_EVENTS.jsonl
- EXECUTION_PROGRESS_CURRENT.json
- EXECUTION_PROGRESS_DASHBOARD.md

## RECOMMENDED TOP-LINE DISPLAY
OVERALL        [██████░░░░] 62%
CURRENT PHASE  [████████░░] 81%
WP/GATE        WP3 / G3 — VALIDATING
UNITS          147 / 212 closed
BLOCKED        3
ELAPSED        41h 22m
ETA            18–27h (confidence: MEDIUM) or UNKNOWN
LAST EVENT     <timestamp> <event>

## CALCULATION RULE
Prefer evidence-closed weighted work units. Initial weights may be plan-derived; after an authorized measurement/calibration phase, future plans may use measured workload/cost weights. Never derive overall progress by simple visual checklist counting when work-package sizes materially differ.

## NEXT-EXECUTION REQUIREMENT
PMO execution plans prepared after this directive should include this progress-control layer from the start. This receipt does not mutate or interrupt the currently running M3Top3 execution.
