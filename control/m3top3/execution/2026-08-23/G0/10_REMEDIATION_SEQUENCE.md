# M3Top3 G0 이후 제한형 Remediation Dispatch

```text
DISPATCH_ID = AAA-M3TOP3-G0-REMEDIATION-DISPATCH-20260823-0055-01
PARENT = AAA-M3TOP3-P0-VALIDATION-REBASE-G0-20260823-0045-01
DISPATCH_AUTHORITY = OWNER_APPROVED_PMO_DIRECT_DISPATCH
STATUS = ISSUED_AFTER_PMOV_INITIAL_AUDIT_CORRECTIONS
SCOPE = PRE-GOLDEN CORRECTNESS_AND_EVIDENCE_CLOSURE
SEMANTIC_MUTATION = PROHIBITED
OUTCOME_TUNING = PROHIBITED
OFFICIAL_RUN = PROHIBITED
IVA_PARTICIPATION = NONE
```

## 실행 원칙

- 작업은 dependency/Gate 순서로 수행하며 달력상 완료일을 Gate 통과로 대체하지 않는다.
- 기존 v1 의미를 추정해 덮어쓰지 않는다. exact 원본이 없으면 `MISSING`으로 보존한다.
- runtime 수정은 먼저 실패해야 하는 회귀테스트를 고정한 뒤 수행한다.
- U127 v0.8 및 W1–W8은 outcome-exposed development evidence로만 취급한다.
- 공식 Golden/Replay와 성능 계산은 별도 Entry Receipt 전 실행하지 않는다.
- 각 Author lane의 완료는 paired validator receipt 전까지 `AUTHOR_COMPLETE / UNVALIDATED`다.

## 순차 Dispatch

| 순서 | Packet | 실행내용 | 필수 산출물 | 종료조건 |
|---:|---|---|---|---|
| 1 | `R-WP4-01 Known-Failure Lock` | 감사 commit/blob과 P0 known-failure matrix 고정 | audit-target receipt, negative regression specification | 현재 결함이 재현 가능하고 기대 실패값이 hash-bound |
| 2A | `R-WP1-01 Exact Identity Recovery` | contract/scorer/config/env/tests/provenance 탐색 | identity manifest, exact/semantic/missing classification | S0→S1 candidate evidence 또는 exact 복구 불가 receipt |
| 2B | `R-WP2-01 Universe & Exposure Closure` | U127 genesis·inclusion rationale·access log·W1–W8 role 고정 | governed universe candidate, exposure manifest | `CURRENT/FROZEN` 전까지 candidate 유지; W1–W8 exposed 분류 고정 |
| 2C | `R-WP3-01 Data Admission Closure` | BP·listing/tradability·CA·price bytes·PIT source census | denominator ledger, CA final scan, readback hashes, readiness matrix | invented/backfilled evidence 0; 모든 cell status 명시 |
| 3 | `R-WP4-02 Fail-Closed Runtime` | PIT admission/state/CLI/readback/immutable storage 수정 | code diff, unit/property/metamorphic results | invalid/partial/corrupt/overwrite cases가 모두 hard-fail·non-zero |
| 4 | `R-WP4-03 Canonical Lineage & Full Universe` | Run Manifest→Model Score→full-rank Prediction→Outcome/Validation 저장 | revisioned schemas, append-only ledger, readback receipt | full eligible-universe MFE/Exit/MAE/time-to-peak/giveback 가능 |
| 5 | `R-WP3-02 Blinded PIT Build` | snapshot별 source bundle, outcome concealment, 독립 coding/adjudication | evidence bundle hashes, annotation receipt, coverage/effective weights | PIT vintage·annotator/model provenance 및 UNKNOWN 보존 |
| 6 | `R-WP4-04 Synthetic Golden Build` | GF01–GF20 concrete fixtures와 independent oracle 구축 | fixture/oracle/harness hashes, injection results | exact implementation target에 결속; author/validator 분리 |
| 7 | `R-GATE-01 Thin Vertical Slice` | 1 window × 소수 기업으로 end-to-end 검증 | immutable run/readback trace, failure report | 모든 logical/data/lineage Gate PASS; performance claim 금지 |
| 8 | `R-GATE-02 S0→S1 Review` | exact recovery 결과와 validator receipts 통합 | state-transition package | exact recovery일 때만 S1 eligible; reconstruction이면 별도 identity |

2A·2B·2C는 서로의 결과를 변경하지 않는 read-only discovery/build lane으로 병렬 수행할 수 있다. 3 이후 구현은 별도 격리 branch/worktree에서 수행하고, paired validator가 해당 diff와 결과를 검증한다.

## WP4 필수 Negative Tests

다음 항목은 수정 전에 실패 기대값으로 고정한다.

- missing 또는 timezone 없는 `publication_at`
- `available_before_entry=False`, `current_only`, post-cutoff evidence
- `PARTIAL/BLOCKED` snapshot scoring 시도
- corrupted JSONL 및 manifest/file hash mismatch
- false price dataset hash와 canonical semantics spoofing
- duplicate price code/date row 및 invalid OHLC/CA factor
- 동일 identity의 overwrite 및 non-deterministic rerun
- blocked/tie/integrity failure의 exit code 0
- official scorer/plugin/config 미결속 상태의 run admission

## Data critical path

우선순위는 다음과 같다.

1. U127 genesis provenance와 127-row release candidate 정리
2. listing/name history unresolved 59개사 및 BP 535 cells research
3. CA completeness B/C axis와 2024/2026 raw component readback
4. 공식 Historical Eligible denominator 생성
5. Thin PIT 1,016 slots의 실제 source/publication/feature evidence 구축
6. U81 F1 0 READY 상태 해소

## Stop / Escalation Rules

영향 범위를 즉시 격리하는 경우:

- outcome/winner 정보가 feature annotation 또는 baseline semantics에 유입됨
- exact target bytes/hash 불일치
- 기존 v1 의미·가중치·gate·NA·tie의 무단 변경
- immutable identity의 overwrite 또는 lineage 손실

오너에게 재상신하는 경우:

- exact v1 원본을 찾지 못해 신규 reconstructed identity 채택이 필요함
- S1 candidate가 완성돼 governed Freeze 승인이 필요함
- Official Golden/Replay/Promotion/Production 경계에 진입함
- scope·비용·일정의 중대한 재기준선이 필요함

그 외 blocker는 finding으로 기록하고 영향받지 않는 작업을 계속한다.
