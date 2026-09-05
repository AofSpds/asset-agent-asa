# M3Top3 real-input Strict/Pragmatic replay — final report

## 결론

이번 실행은 이전 `ZERO_SCOREABLE`을 덮어쓰지 않고, 실제 KRX 원문을 W1 모델 입력·점수·사후 가격까지 연결했다.

- 종료 상태: **`PARTIAL_NONEMPTY_SCORE_ONLY` with preliminary raw outcome diagnostic**
- Strict: 실제 점수 `1/57`, 실제 raw outcome 측정 `1/1` precommitted cohort
- contract-exact outcome: `0` — corporate-action comparability와 PRICE-CANONICAL 상태가 미확인이므로 승격하지 않음
- Pragmatic: `NO_DEFENSIBLE_ESTIMATE_EXECUTED / PRAGMATIC_DEFERRED_POLICY_NOT_BOUND`
- 공식 Top3/Top10, primary hit, critical miss, 모델 우수성, production readiness: 모두 주장하지 않음

따라서 실제 입력→점수→raw 성과 경로는 비어 있지 않게 작동했지만, 모델 성능 검증 완료 상태는 아니다.

## 실행 신원과 보존 경계

| 항목 | 실제 binding |
|---|---|
| RUN_ID | `AAA-M3TOP3-REAL-INPUT-STRICT-PRAGMATIC-20260905-114150-CODEX-01` |
| 실제 착수 | `2026-09-05T11:41:50.2453872+09:00` |
| branch | `task/aaa/m3top3-real-input-replay-20260905` |
| worktree | `C:\Users\ms1pk\dev\asset-agent-asa\asset-agent-asa\real-input-replay` |
| predecessor | `79b46dc1f63f1cd215cc0ebc0c91b4ec09e7dc71` |
| predecessor ZERO tree | `1d73cc942a3524571ea214724c887c3964dca13f` — 보존 확인 |
| reviewed code candidate | `c15cbfa9bbedcb3b388b9d101b269ced2fc83bc5` |
| score/seal preservation commit | `0dfef7b81566e6ec018994d5597f3f8f923944d1` |
| successor executable bundle | `M3TOP3-REAL-INPUT-EXECUTABLE-BUNDLE-SHA256:4d828c0308bf892718832e9cb02d87ee7716b9b62c28d643b69b424b5f2b6a4a` |

기존 scorer, feature transforms, weights, missingness, guards, coverage runner, config 및 이전 run 결과의 Git objects는 predecessor와 동일하다. 새 identity는 additive source/sidecar adapter와 두 단계 seal/outcome CLI만 반영한다.

## 실제 모델·설정 binding

| 구성 | 실제 값 |
|---|---|
| model | `M3TOP3-v1.0` |
| scorer | `M3TOP3-GATED-LINEAR_v1.0_WORKING` |
| weights | `M3TOP3-WEIGHT-VERSION_v1.0_WORKING` |
| feature schema / input / I/O | `M3TOP3-FEATURE-SCHEMA_v1.0_WORKING` / `MIS-v1.0` / `SIO-v1.0` |
| window mapping | `WM-v1.1`; W1 anchor `2024-08-10`, cutoff `2024-08-09T23:59:59+09:00`, entry `2024-08-12 Open`, evaluation last `2024-11-08`, exit `2024-11-11 Open` |
| config SHA-256 | `eecde22a7744cff505c624bb6f0bdb11714352a122632238ea68d9cd0fbacb98` |
| missingness | no silent zero/false/neutral fill; existing `NOT_FOUND` retained |
| hard-risk gate | `NONE` means no additional gate was applied; it does not prove no risk |
| Python | CPython `3.12.14`; executable SHA-256 `ebdb7ddc892a73a9ece422fda408d0bbc2d232904cedeaae359066ef2db37317` |
| Parquet reader | PyArrow `25.0.1`; RECORD SHA-256 `1eddf4fb72b1b071868dc02d6fc8242125d98c6557ae6af8f783b1c84ef6a797`; 761 hashed files verified, RECORD only unhashed existing allowlist, 105 bytecode entries absent |

## 실제 source → 점수

`KRX:005290`의 KRX KIND 2024 Q2 잠정 연결 실적 원문 한 건을 보존했다. 원문은 16,221 bytes, SHA-256
`5c361107cbd2dc35b236b5358595e036ecb1dd9dc8b06471bca7bf9e550c7db7`, Git blob
`82be77ca6edb47695ca52ccf0ac2b1c69605129f`이다. 날짜 정밀도는 DATE_ONLY로 유지했고, 가장 늦은 가능시각
`2024-08-02T23:59:59+09:00`도 W1 cutoff 이전이라 `CUTOFF_SAFE`로 채택했다. 잠정·미검토라는 원문 한계도 유지했다.

| 값 | 2024 Q2 | 2023 Q2 | derived relative change |
|---|---:|---:|---:|
| revenue (KRW million) | 355,414 | 331,317 | `0.07273094951360781366485873046` |
| operating profit (KRW million) | 49,972 | 45,565 | `0.09671897289586305278174037090` |

Sidecar는 관측 수치 leaf 4개, governed transform-control leaf 4개, scorer 계산 change 2개를 연결했다. 추정 leaf는 0개다.
W1 전체 57행을 같은 배치로 scorer에 공급한 결과 `KRX:005290`의 F02 score와 final score는 각각 `50`과
`50.00`이다. 상태는 `PROVISIONAL_MISSING_FEATURES`, feature coverage는 `0.1`이다. F02가 있는 회사가 하나뿐이라
cross-sectional percentile `50`은 singleton 기계적 결과이며 모델 품질 근거가 아니다.

## 실제 raw outcome

Selection seal `m3selection_5bae1c9cb07ecc0dad46262813f4198e`를 exclusive-create, fsync, canonical readback 후
Git에 먼저 고정했다. score 단계에는 가격 경로 인자가 없었고 미래 가격 read count는 0이었다. 이후 별도 process가 seal,
현재 executable bundle, 58개 W1 거래일 spine, exact price component bytes와 runtime을 검증한 뒤 2024 SHA-bound byte buffer를
직접 decode했다. 세 component dataset identity는
`419893f0dc8c08019a746182135630cc5f94d6e7ebc2874d5bd23cb54c0a72f7`이다.

W1 INCLUDE 57개 모두 58개 holding date와 exit endpoint가 존재해 raw path는 `57/57` 완전했다. 사전 고정된
`ALL_SCOREABLE_PRECOMMITTED_NO_SUBSTITUTION` cohort 한 종목의 결과는 다음과 같다.

| metric | KRX:005290 실제 raw 결과 |
|---|---:|
| entry open, 2024-08-12 | `32600.0` |
| MFE peak high | `34300.0` |
| raw unadjusted MFE return | `0.052147239263803680981595092` (약 `+5.2147%`) |
| W1 INCLUDE57 raw-unadjusted MFE rank | `55 / 57` |
| minimum valid low | `25800.0` |
| horizon close, 2024-11-08 | `26250.0` |
| raw horizon-close return | `-0.1947852760736196319018404908` (약 `-19.4785%`) |
| exit open, 2024-11-11 | `26100.0` |
| raw exit-open return | `-0.1993865030674846625766871166` (약 `-19.9387%`) |
| raw peak-to-exit giveback / entry | `0.2515337423312883435582822086` |
| unresolved holding dates | `0` |

이 값과 불리한 raw rank를 그대로 보존한다. 다만 이는 raw-unadjusted 진단이다. corporate-action comparability, dividends,
total return, PRICE-CANONICAL은 확인되지 않았고 MAE return 공식도 open item이므로 official MFE rank, hit@K, critical miss는 `NA`다.
Outcome semantic SHA-256은 `e80fe827b0f9f57d881a8ca230a948237be5392964cf10d64f12813e5716b8f6`이다.

## W1–W8 회계

`missing`은 값 수가 아니라 INCLUDE 회사×feature의 `NOT_FOUND` block 수다. W2–W8은 새 sidecar가 없으므로 이전
ZERO_SCOREABLE 상태를 보존했으며 동일 빈 입력을 다시 실행하지 않았다.

| Window | outer | INCLUDE | proven excl. | unresolved excl. | observed leaves | derived controls | estimated | missing blocks | Strict scoreable | Pragmatic | selected | outcome measurable | 이유 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| W1 | 127 | 57 | 8 | 62 | 4 | 4 (+2 calculated) | 0 | 512 | 1 | NA, not run | official 0; cohort 1 | raw 1; exact 0 | one admitted F02; coverage incomplete; CA/canonical unverified |
| W2 | 127 | 57 | 7 | 63 | 0 | 0 | 0 | 513 | 0 | NA | NA | NA | no mechanically prepared new input; preserved, not rerun |
| W3 | 127 | 57 | 6 | 64 | 0 | 0 | 0 | 513 | 0 | NA | NA | NA | same |
| W4 | 127 | 58 | 3 | 66 | 0 | 0 | 0 | 522 | 0 | NA | NA | NA | same |
| W5 | 127 | 58 | 3 | 66 | 0 | 0 | 0 | 522 | 0 | NA | NA | NA | same |
| W6 | 127 | 59 | 3 | 65 | 0 | 0 | 0 | 531 | 0 | NA | NA | NA | same |
| W7 | 127 | 59 | 2 | 66 | 0 | 0 | 0 | 531 | 0 | NA | NA | NA | same |
| W8 | 127 | 60 | 5 | 62 | 0 | 0 | 0 | 540 | 0 | NA | NA | NA | same |

전체 외부 회계는 1,016 company-window, INCLUDE 465, proven exclusion 37, unresolved exclusion 514다. INCLUDE feature
block 4,185개 중 이번 successor에서 1개가 AVAILABLE이고 4,184개는 기존 missingness로 남는다. 514 unresolved eligibility
행은 추정으로 복귀시키지 않았다.

## Pragmatic와 민감도

새 추정 정책은 채택하지 않았다. 특히 raw close ratio를 F05 total return으로 바꾸는 것은 기존 feature 의미 변경이므로
승인된 Strict 범위가 아니다. 20/60일 total return, equal-weight universe denominator, turnover acceleration, dividends,
suspension 및 CA 처리 방법이 정확히 결속되지 않은 상태에서 low/base/high 값을 만들면 숫자 조작이 된다. 따라서 sensitivity
표도 만들지 않았다. 이 판단은 Strict 결과를 막지 않았으며 별도 `PRAGMATIC_ESTIMATION_DECISION_CARD.md`에 격리돼 있다.

## 독립 리뷰와 검사

최종 reviewed candidate `c15cbfa...`에서 신규 24개와 보존 affected 47개, 총 `71/71 PASS`였다. 전체 작업 중 test case
execution은 실패·수정·독립 재확인을 포함해 585회다. 최종 independent verdict는 PASS, 잔여 P0/P1은 없다. 이는 changed
path 승인일 뿐 GF09나 전체 Golden validation을 승격하지 않는다. 자세한 chronology는 `AFFECTED_ONLY_REVIEW_RECEIPT.md`에 있다.

## 시간·사용량

- 첫 30분 반환: `2026-09-05T12:12:32.2312847+09:00`; 목표 대비 `41.9858975s` 지연
- 최종 review PASS: `2026-09-05T13:51:55.4517524+09:00`
- actual score-and-seal: `2026-09-05T13:52:37.898702+09:00`–`13:52:39.760510+09:00`
- actual outcome: `2026-09-05T13:54:28.535555+09:00`–`13:54:36.672287+09:00`
- 착수→outcome 종료: 약 `2h 12m 46.43s`
- admitted source documents: `1 / 24`; source discovery/open/fetch attempts: `18 / 40`
- isolated runtime package install attempts: `2` (sandbox network denial 1, approved retry success 1)
- token/CRU, active/wait split: `NOT_INSTRUMENTED`; 0으로 대체하지 않음

## 다음 보완 우선순위

Outcome을 본 뒤의 후속 보완은 exploratory로 표시해야 한다. 한 번의 다음 source batch는 최대 5개로 제한한다.

1. `KRX:003160` W1 cutoff-safe F02 공식 원문 후보 — 실제 존재/기간/단위는 아직 미확인.
2. `KRX:025560` 동일 후보 — 미확인.
3. `KRX:031980` 동일 후보 — 미확인.
4. `KRX:036200` 동일 후보 — 미확인.
5. `KRX:005290` W1 기간의 exact CA/comparable-price evidence — raw 진단을 contract-exact로 승격할 때만 필요.

이 목록은 값을 가정하지 않는다. 각 source가 없거나 cutoff에 맞지 않으면 `NA/제외/미측정`으로 유지한다. 전수 자료 수집,
옛 ZIP 수색, 완료된 전체 검증 재실행은 다음 단계의 선행조건이 아니다.

## 재실행 입구

정확한 argv와 환경은 `strict-score-and-seal/SCORE_AND_SEAL_RUN_MANIFEST.json` 및
`strict-outcomes/OUTCOME_RUN_MANIFEST.json`에 보존돼 있다. 핵심 순서는 다음과 같다.

1. `python -m tools.m3top3.cli_run_real_input_replay score-and-seal ...`
2. selection seal Git persistence 및 clean-worktree 확인
3. `PYTHONDONTWRITEBYTECODE=1`과 bound PyArrow root로
   `python -m tools.m3top3.cli_run_real_input_replay measure-outcomes ...`

가격 단계는 seal을 검증하기 전 price path를 stat/hash/open하지 않으며, 검증된 2024 bytes와 decode bytes가 동일하다.

현재 상태 = 실제 source→Strict score→preliminary raw outcome 연결 완료; contract-exact 성과와 공식 Top3는 미측정.
핵심 판단 = ZERO_SCOREABLE은 벗어났지만 1/57 singleton score와 raw rank 55/57은 모델 검증 완료가 아니다.
진행 작업 = 결과·review·명령·한계를 successor run에 보존.
다음 단계 = 위 5개 이하의 가치 높은 gap만 exploratory로 보완하거나, 별도 F05 추정방법 결정을 채택할 때만 Pragmatic 실행.
사용자 행동 = 현재 승인 범위 내 추가 승인 불필요; 새 추정방법/feature 의미 변경을 원할 때만 decision card를 결정.
