# F02_R1_COMPLETION_REPORT

PROJECT = AAA · PRODUCT = ASSET AGENT ASA  
RUN_ID = AAA-M3TOP3-F02-R1-20260905-171755-CODEX-01  
REPORT_CUTOFF_KST = 2026-09-05T19:37:43.2411131+09:00  
REMOTE_PERSISTENCE_ADDENDUM_KST = 2026-09-05T21:26:16.1024172+09:00
TERMINAL = COMPLETE_MULTI_COMPANY_PROVISIONAL

F02-only 관측 5개사의 잠정 비교 경로가 완성됐다. 다른 feature는 여전히 비어 있다. 이번 결과는 공식 Top3/Top10, U127 최적선택, 모델 성능 PASS 또는 투자 추천이 아니다.

| 회사 | 사용 분기 | 공개일 | 매출 YoY | OP YoY | F02 | coverage | 잠정순위 | 제한사항 |
|---|---|---|---:|---:|---:|---:|---:|---|
| 025560 미래산업 | 2024Q1 / 2023Q1 | 2024-05-14 | 7.8719% | 560.5811%* | 87.5 | 10% | 1 (동점) | Q1 대안·전기 적자/재작성; F02-only |
| 031980 피에스케이홀딩스 | 2024Q1 / 2023Q1 | 2024-05-16 | 155.4397% | 341.0654% | 87.5 | 10% | 2 (동점) | Q1 대안; F02-only |
| 005290 동진쎄미켐 | 2024Q2 / 2023Q2 | 2024-08-02 | 7.2731% | 9.6719% | 50 | 10% | 3 | 기존 cache·잠정 Q2; F02-only |
| 036200 유니셈 | 2024Q1 / 2023Q1 | 2024-05-10 | 6.6339% | 5.2218% | 25 | 10% | 4 | Q1 대안; F02-only |
| 003160 디아이 | 2024Q1 / 2023Q1 | 2024-05-16 | -11.4347% | -312.1464% | 0 | 10% | 5 | Q1 대안·당기 적자; F02-only |

표의 YoY는 기존 RELATIVE 식 `(current-prior)/abs(prior)`를 백분율로 표시한 값이며 표시만 소수 4자리로 반올림했다. 실제 입력·계산은 원문 정수와 Decimal 정밀도를 유지한다. *025560 OP는 음수 전기 절댓값 대비 개선율이며 통상적인 양수 기저 성장률이 아니다. 전기 OP는 같은 공개 원문의 중단영업 반영 재작성 비교값이다.

두 87.5점 회사는 경제적 우열이 구분된 것이 아니라 동점이다. 기존 회사 ID 오름차순 규칙이 025560, 031980 순서를 정했다. coverage 열은 각 회사의 feature-weight coverage 10%이며, 회사 분모 coverage 5/57와 다르다. 005290의 새 50점은 두 지표 percentile이 각각 50인 실제 계산 결과이지 과거 50점에 강제 고정한 값이 아니다. 003160의 0은 실제 관측 비교점수이며 NA/미입력을 0으로 채운 결과가 아니다.

## 원격 persistence 후속 addendum

원래 완료보고 cutoff에는 원격 전송 권한이 없어 local-only로 정확히 종료했다. Owner 후속 메시지는 그때 요청한 exact payload와 destination—원문·저널 포함 현재 F02-R1 payload, 기존 `https://github.com/AofSpds/asset-agent-asa.git`, 동일 task branch—에 대한 승인으로 적용했다. 최초 성공 push는 `7ebbd2e6a64b46ee1d8c703ab8a9942f30c8dc42`이며 main/authority refs는 변경되지 않았다. 이 후속 전송은 source 재검색, score rerun, PR, merge 또는 release가 아니다.

## 1. 완료와 미완료의 구분

- VALIDATION_COMPLETE = TRUE: CTLV/MODV/ENGV/PMOV/IVA가 exact P3 대상에 PASS; blocking 0. P5 사후 독립 readback 25 checks PASS.
- RESEARCH_OBJECTIVE_MET = TRUE: 신규 4개 + cache 대조군 1개 = 실제 비교가능 5개사. 최소 신규 2개/전체 3개 목표 충족.
- PERSISTENCE_COMPLETE = TRUE_FOR_LOCAL_AND_REMOTE_TASK_BRANCH. 입력/검증/score/seal은 local payload commit `33b4690bb52b2fb1d593beee3b2549a7da70e699`에, 원격에 처음 전송된 완료보고 payload는 `7ebbd2e6a64b46ee1d8c703ab8a9942f30c8dc42`에 보존됐다. 이 addendum을 포함한 최종 closing commit/tree/remote HEAD는 본문 자기참조를 피하기 위해 terminal 반환에 별도 제시한다.
- REMOTE_PERSISTENCE = INITIAL_PUSH_VERIFIED; FINAL_ADDENDUM_REF_RETURNED_IN_TERMINAL. 원래 push는 명시적 payload/destination 승인 부족으로 auto-review에서 실행 전에 차단됐지만, Owner가 후속 `진행하세요.`로 기존 origin·동일 task branch 전송을 명시 승인했다. 2026-09-05T21:25:14.7295968+09:00에 승인 적용을 시작했고 2026-09-05T21:26:16.1024172+09:00까지 원격 `7ebbd2e6a64b46ee1d8c703ab8a9942f30c8dc42`을 readback했다. 우회·새 credential·main 변경 없음.
- NO_PR = 요청되지 않았고 merge/main/release 권한이 없다. Main 반영, release, production, W2–W8 또는 outcome 실행은 하지 않았다.

기존 Strict 1/57 (1.7544%)에서 5/57 (8.7719%)로 4개 증가했다. 적격 57개 전체를 입력 배치에 유지하고 52개는 REPLAY_DATA_INSUFFICIENT로 남겼다. 127 = 5 scored + 52 insufficient + 8 EXCLUDE_PROVEN + 62 EXCLUDE_UNRESOLVED. 경제적 eligibility와 증거확신도, feature scoreability는 별개다. 이번 고정 5개사 밖은 NOT_ASSESSED_IN_THIS_BATCH이며 전체 자료 부재나 부적격으로 재분류하지 않았다.

9 features × 57개 = 513 blocks 중 AVAILABLE 5개, NOT_FOUND 508개. 40 consumed leaves는 관측 수치 20 + 파생 control 20이며 추정치 0이다. 파생 control 20개는 change_mode/operator_id이고 관측 원문 수치가 아니다. 10개 상대변화는 원문 pair에서 산출했다. 결측은 null/NOT_FOUND이며 score 입력을 채우기 위해 보간·대용하지 않았다.

## 2. Owner 승인과 재시작 복구

- 원 승인: `3bb8c2368f64d93e5e748fd35497946b1cecd198`, 승인 blob `f82095850a1d98c16ef5eb33ad91888344655fb4`.
- 승인 packet commit `2f773328e50ab0d6e7f640845251d16ba167b26f`, blob `8c410fe2aa6cedf1910d01f8bf4529ccb5cd29fb`, SHA-256 `65c1d9a62109ba9cc657a8416606ac8ac1d39b5edbf60a9e579859f921bdd01b`. 첨부 초안의 미승인 문구가 아니라 후속 Owner 승인 및 NO-RERUN 지시를 적용했다.
- 시작: 2026-09-05T17:17:55.1469424+09:00. 같은 run root와 task branch를 유지했다. 원 packet의 새 root 조항을 재시작 이유로 다시 적용하지 않았다.
- 복구 첫 확인: Git branch/HEAD/working tree, 기존 root, CHECKPOINTS/PROCESS_ACTION_LEDGER/source matrix. 마지막 실질 완료 단계는 P1이었다.
- 13개 기존 관리파일을 모두 유지했고 신규 원문 4건과 cache 원문 1건의 hash가 일치했다. durable source evidence 손실은 검출되지 않았다. 실패한 이전 multi-file patch는 원자적으로 미적용됐고 이후 matrix 수정만 적용된 상태였다. 저장되지 않은 UI/메모리 내용을 모두 복구했다고 주장하지 않는다.
- 17:45:31.4742731에 source evidence가 완료돼 있었다. 복구 reconciliation을 18:14:40.3012516에 기록하고 남은 P2–P6만 수행했다. 완료된 source action 재수행 0; 새 provider/credential/budget 0. UI continuity 자체가 복원됐다고 주장하지 않는다.

## 3. 실제 수치·단위·기간

| 회사 | 원문 단위 | 매출 current / prior | OP current / prior | 공개일 / period-end→cutoff 경과 |
|---|---|---:|---:|---:|
| 003160 | KRW | 34732575950 / 39216899579 | -1836830457 / 865831578 | 85 / 131일 |
| 025560 | KRW | 5162565692 / 4785829491 | 2040268633 / -442977057 | 87 / 131일 |
| 031980 | KRW | 38094447594 / 14913281644 | 15420952017 / 3496296368 | 85 / 131일 |
| 036200 | KRW | 55186952755 / 51753687853 | 4559702713 / 4333422148 | 91 / 131일 |
| 005290 | KRW_MILLION | 355414 / 331317 | 49972 / 45565 | 7 / 40일 |

각 회사 내부는 같은 연결 기준·지표·3개월 길이·전년 동분기 비교다. 신규 네 회사는 2024Q1/2023Q1, 대조군은 2024Q2/2023Q2다. 2024-08-09T23:59:59+09:00 cutoff를 유지하며 날짜만 확인되는 공시는 closed-day upper bound를 사용한다. intraday 공개시각을 발명하지 않았다. 분기 누계 차감·환산·단위 변환·freshness penalty는 실행하지 않았다. 원문 native pair 단위가 상대변화식에서 상쇄되므로 원/KRW_MILLION을 회사 간 명목금액으로 직접 비교하지 않는다.

025560 전기 OP는 같은 2024Q1 보고서의 계속영업 비교값 -442,977,057이다. 원문 note line 23818 및 TD line 23874/23875/23876의 -448,371,497 + 5,394,440 = -442,977,057 연결을 보존했다. 나중에 공개된 정정·성과를 끌어오지 않았다. 원문 분기보고서 자체를 감사확정 자료라고 확대하지 않았다.

### 003160 — (주)디아이

- Source ID: `SRC-KRX-KIND-003160-20240516-20240516003155`; [KIND 원문](https://kind.krx.co.kr/external/2024/05/16/001334/20240516003155/11013.htm).
- 원문 경로: `control/m3top3/f02-r1-multi-company-input-repair/v1.0/runs/AAA-M3TOP3-F02-R1-20260905-171755-CODEX-01/sources/KRX-003160/KRX_003160_20240516_Q1_REPORT_11013.htm`; 1,404,585 bytes.
- SHA-256: `2ab621a3862041c57040524aaa3c084c81304685015cbc2be7e6b57ba5fa3fe3`; Git blob: `b99d90f62b47c52389356318ccb328395dcf1130`.
- 표 시작 line 6543; 매출 row 3, OP row 8; current/prior one-based cell 2/4. Exact cover/header/context 및 모든 숫자 셀은 INPUT_MAPPING_R1의 parsed_cell_bindings와 검증 영수증에 결합.
- 기간: 2024-01-01–2024-03-31 / 2023-01-01–2023-03-31, 3개월, 연결. 공개일은 2024-05-16; 취득시각을 공개시각으로 대체하지 않음.
- 공시 성격: `FILED_QUARTERLY_REPORT` / `OFFICIAL_FILED_QUARTERLY_STATEMENT_NO_AUDIT_ATTESTATION`.
- Q2: [2024-08-14 후보](https://kind.krx.co.kr/external/2024/08/14/002471/20240814007837/11012.htm)는 cutoff 이후라 미채택. `SRA-003160-0010` 및 명시된 기존 receipt를 재사용. cutoff 이전 사용 가능한 Q2 전체 부재는 NOT_PROVEN; bounded set의 최신 확인 Q1만 채택.

### 025560 — 미래산업 주식회사

- Source ID: `SRC-KRX-KIND-025560-20240514-20240514003275`; [KIND 원문](https://kind.krx.co.kr/external/2024/05/14/001496/20240514003275/11013.htm).
- 원문 경로: `control/m3top3/f02-r1-multi-company-input-repair/v1.0/runs/AAA-M3TOP3-F02-R1-20260905-171755-CODEX-01/sources/KRX-025560/KRX_025560_20240514_Q1_REPORT_11013.htm`; 1,325,372 bytes.
- SHA-256: `a547f8b383ecb85f39d5826ab08bf6641c6716a85ba12ddc90efb5c9f303537f`; Git blob: `44a8179c1a003db97cc4e1bc733208edcc0b1df4`.
- 표 시작 line 4011; 매출 row 3, OP row 7; current/prior one-based cell 2/4. Exact cover/header/context 및 모든 숫자 셀은 INPUT_MAPPING_R1의 parsed_cell_bindings와 검증 영수증에 결합.
- 기간: 2024-01-01–2024-03-31 / 2023-01-01–2023-03-31, 3개월, 연결. 공개일은 2024-05-14; 취득시각을 공개시각으로 대체하지 않음.
- 공시 성격: `FILED_QUARTERLY_REPORT` / `OFFICIAL_FILED_QUARTERLY_STATEMENT_NO_AUDIT_ATTESTATION`.
- Q2: [2024-08-14 후보](https://kind.krx.co.kr/external/2024/08/14/001390/20240814004272/11012.htm)는 cutoff 이후라 미채택. `SRA-025560-0002` 및 명시된 기존 receipt를 재사용. cutoff 이전 사용 가능한 Q2 전체 부재는 NOT_PROVEN; bounded set의 최신 확인 Q1만 채택.

### 031980 — 피에스케이홀딩스 주식회사

- Source ID: `SRC-KRX-KIND-031980-20240516-20240516001477`; [KIND 원문](https://kind.krx.co.kr/external/2024/05/16/000652/20240516001477/11013.htm).
- 원문 경로: `control/m3top3/f02-r1-multi-company-input-repair/v1.0/runs/AAA-M3TOP3-F02-R1-20260905-171755-CODEX-01/sources/KRX-031980/KRX_031980_20240516_Q1_REPORT_11013.htm`; 961,791 bytes.
- SHA-256: `8323d301baa3f62a872f2dec7f846d98d0effc0e9e06f7ea6dca5c7c78a598a9`; Git blob: `89a0ebd92b90207ba8e0f5e947f5350c92714039`.
- 표 시작 line 4250; 매출 row 3, OP row 7; current/prior one-based cell 2/4. Exact cover/header/context 및 모든 숫자 셀은 INPUT_MAPPING_R1의 parsed_cell_bindings와 검증 영수증에 결합.
- 기간: 2024-01-01–2024-03-31 / 2023-01-01–2023-03-31, 3개월, 연결. 공개일은 2024-05-16; 취득시각을 공개시각으로 대체하지 않음.
- 공시 성격: `FILED_QUARTERLY_REPORT` / `OFFICIAL_FILED_QUARTERLY_STATEMENT_NO_AUDIT_ATTESTATION`.
- Q2: [2024-08-14 후보](https://kind.krx.co.kr/external/2024/08/14/003322/20240814010557/11012.htm)는 cutoff 이후라 미채택. `SRB-031980-0009` 및 명시된 기존 receipt를 재사용. cutoff 이전 사용 가능한 Q2 전체 부재는 NOT_PROVEN; bounded set의 최신 확인 Q1만 채택.

### 036200 — 유니셈 주식회사

- Source ID: `SRC-KRX-KIND-036200-20240510-20240510001413`; [KIND 원문](https://kind.krx.co.kr/external/2024/05/10/000637/20240510001413/11013.htm).
- 원문 경로: `control/m3top3/f02-r1-multi-company-input-repair/v1.0/runs/AAA-M3TOP3-F02-R1-20260905-171755-CODEX-01/sources/KRX-036200/KRX_036200_20240510_Q1_REPORT_11013.htm`; 1,083,117 bytes.
- SHA-256: `63152e6f1ba5c1b063c6466b54c3d7b7382d948de0aa36f19f8a208a3cb58ab2`; Git blob: `0e451a3feb018cc4d38bd53915d535a44674e267`.
- 표 시작 line 4408; 매출 row 3, OP row 7; current/prior one-based cell 2/4. Exact cover/header/context 및 모든 숫자 셀은 INPUT_MAPPING_R1의 parsed_cell_bindings와 검증 영수증에 결합.
- 기간: 2024-01-01–2024-03-31 / 2023-01-01–2023-03-31, 3개월, 연결. 공개일은 2024-05-10; 취득시각을 공개시각으로 대체하지 않음.
- 공시 성격: `FILED_QUARTERLY_REPORT` / `OFFICIAL_FILED_QUARTERLY_STATEMENT_NO_AUDIT_ATTESTATION`.
- Q2: [2024-08-14 후보](https://kind.krx.co.kr/external/2024/08/14/003029/20240814009619/11012.htm)는 cutoff 이후라 미채택. `SRB-036200-0009` 및 명시된 기존 receipt를 재사용. cutoff 이전 사용 가능한 Q2 전체 부재는 NOT_PROVEN; bounded set의 최신 확인 Q1만 채택.

### 005290 — (주)동진쎄미켐

- Source ID: `SRC-KRX-KIND-005290-20240802-70956`; [KIND 원문](https://kind.krx.co.kr/external/2024/08/02/000210/20240730000320/70956.htm).
- 원문 경로: `control/m3top3/real-input-replay/v1.0/runs/AAA-M3TOP3-REAL-INPUT-STRICT-PRAGMATIC-20260905-114150-CODEX-01/sources/W1/KRX-005290/KRX_005290_20240802_PROVISIONAL_EARNINGS_70956.htm`; 16,221 bytes.
- SHA-256: `5c361107cbd2dc35b236b5358595e036ecb1dd9dc8b06471bca7bf9e550c7db7`; Git blob: `82be77ca6edb47695ca52ccf0ac2b1c69605129f`.
- 표 시작 line 18; 매출 row 5, OP row 7; current/prior one-based cell 3/6. Exact cover/header/context 및 모든 숫자 셀은 INPUT_MAPPING_R1의 parsed_cell_bindings와 검증 영수증에 결합.
- 기간: 2024-04-01–2024-06-30 / 2023-04-01–2023-06-30, 3개월, 연결. 공개일은 2024-08-02; 취득시각을 공개시각으로 대체하지 않음.
- 공시 성격: `PROVISIONAL_EARNINGS_FAIR_DISCLOSURE` / `PROVISIONAL_NOT_FINAL_AUDITOR_REVIEW_NOT_YET_ISSUED`.
- Q2 cache만 재사용, 새 공시·CA 수집 0. 다른 Q2 최신성 조사 없음.

## 4. D1·contract·model·control disposition

P2는 기존 의미와 새 입력 profile의 경계를 분리해 CONDITIONALLY_COMPATIBLE_EXPLORATORY로 분류했다. D1의 Q1/Q2 최신 확인 규칙은 공식 KIND의 bounded source set 안에서만 적용한다. 공개된 실제 최신자료 전체나 Q2 미공시를 증명하는 규칙으로 바꾸지 않았다. 중앙 policy 원본의 PENDING_P2는 동결시점 상태로 남아 있고 후속 `P2_DISPOSITION_AND_IMPLEMENTATION_SCOPE.json` 및 exact P4 보고서가 실제 gate 해소를 기록한다.

Source/issuer/date/quarter/basis/unit/sign/cover/header/table/cell/version을 결합한 전용 adapter 1개와 정확한 5-source mapping을 사용했다. 서로 다른 issuer/숫자 셀 이식, hash 불일치, 미래 공시·field, 잘못된 기간/연결/단위, duplicate/partial leaves, prior=0, 경로 우회는 거부하도록 검증됐다. 문자열 내 유사 숫자 포함 여부만으로 승인하지 않는다.

- 모델 M3TOP3-v1.0, F01–F09 산식/weights/scorer/config/eligibility/window/price/outcome 함수를 보존.
- Config SHA-256: `eecde22a7744cff505c624bb6f0bdb11714352a122632238ea68d9cd0fbacb98`.
- Consumed registry exact blob: `5faa4d5739bf9ecb0c11d16f6d7d697ff3983977`. 실패한 historical composite locator를 정상 resolve했다고 주장하지 않고 exact blob을 재사용.
- Input profile: `F02_R1_EXPLORATORY_V1`; model version과 구별.
- Executable bundle: `M3TOP3-REAL-INPUT-EXECUTABLE-BUNDLE-SHA256:fe555c17a4ec8244e99755d193f63a67ff10574964b4025b9086cd70cd7321c7` (31 components; 과거 bundle과 별개).
- Mapping SHA-256: `1d30e0c244aca29093a5fa42b54abd8312a7e0c8c838326e12aae059b28fe30f`.
- Runtime SOURCE_MANIFEST SHA-256: `b3bf4af1a27811b72073595af07a61eb0edfbd326fda349d3f0e98cb3f2b6900`.
- FEATURE_SIDECAR SHA-256: `bb1619b7d037919c576d9c688789814a9474da76635d39edd6e37a2b00f727cc`.
- 통합 P4 보고서 SHA-256: `886e012c0053cbe1efe309278ef55c5290a653ac7f1902cfef6da65732368956`.

## 5. 검증과 사후 점수 대조

P3 작성자 점검과 P4 독립 PASS를 구분한다. P4의 5개 role acts는 3명의 non-author reviewer가 수행했다: CTLV, MODV/ENGV/PMOV의 별도 bootstrap acts, 별도 IVA L2. 5명의 서로 다른 사람/worker가 검토했다고 주장하지 않는다. root PMO는 작성·통합자로서 독립 PASS를 자체 발행하지 않았다.

| 역할 | exact target 판정 | 핵심 실제 증거 |
|---|---|---|
| CTLV | PASS | 5원문/20셀 별도 stdlib 추출, 8 focused tests PASS |
| MODV | PASS | 원래 legacy 13 tests PASS (0.302초), 7 focused tests, model 13 components 보존 |
| ENGV | PASS | fresh affected 31 tests PASS (104.878초), 14 gate mutation 거부, outcome 함수 8개 AST 보존 |
| PMOV | PASS | 승인·분모·33 actions·13관리파일·32대상/34초기변경경로 및 진척 증거 |
| IVA | PASS | independent bounded L2, 6 focused tests 및 10 gate cases; 사후 25 checks PASS |

서로 중복되는 focused test를 고유 검사 수로 합산하지 않았다. fresh affected 31 + unchanged legacy 13 = 44 distinct suite methods. 과거 71/71을 새 source 검증으로 전용하지 않았고 full PC1 rerun도 하지 않았다.

P4 frozen target 이후 operative correction 0, blocking findings 0. IVA 3 + PMOV 2의 nonblocking observation은 3주제(30분 checkpoint 지연, rework/단계시간 미측정, HTTP/read-scope/CRU 미측정)로 중복된다. 지적을 없애기 위한 반복 수정 루프 없이 최종 보고에 반영했다. P3의 SHA 전사 오타, exact header/cell 강화 및 affected 3-test 8.944초 재검증, 변경 integration 파일 LF 정규화는 사전 수정으로 따로 기록했다. P5 root readback에서 canonical payload hash와 raw formatted-file hash를 비교했던 점검문만 바로잡았으며 code/input/output 변경이나 재채점은 없었다.

R1 score-and-seal 실행 1회: 2026-09-05T19:26:31.699448+09:00–2026-09-05T19:26:42.579538+09:00, 10.88009초, 실행 HEAD `48eef6f3105112f637d8783395bcbad883d5af96`. 10개 Decimal 상대변화 → 지표별 cohort percentile → 두 percentile median → 결측 가중치 재정규화 → 기존 동점 규칙의 실제 trace가 일치한다. raw scorer의 top3_flag는 내부 잠정 표식이며 selection ledger의 official_selection_flag는 127개 모두 FALSE, official_rank는 모두 null이다.

- Seal ID: `m3selection_cda20d73e7ee7d917aa6dc97439051b6`.
- Seal content SHA-256: `cda20d73e7ee7d917aa6dc97439051b60a1d0c0fd4c620a43da87261b5a6fb5f`.
- Canonical input / score / ledger payload SHA-256은 `P5_POST_SCORE_READBACK.json`에, 서로 다른 raw-file SHA-256도 별도 필드에 보존.
- Seal은 57개 include 결과, 5개 precommitted cohort, exact input/bundle/report/receipt hash를 결합한다. cohort flag는 미래 outcome 실행승인이 아니다.
- 실행 manifest: future price path 없음, price value read 0, outcome_execution_authorized FALSE. 이 단일 act의 미접근과 과거 actor 노출을 구분.

## 6. Claim ceiling과 역사적 제한

`EXPLORATORY_AFTER_W1_OUTCOME_EXPOSURE`를 보존한다. prior_actor_w1_outcome_exposure TRUE, blind_process_claim FALSE다. 원 source ledger SRA-003160-0004/0005에는 2025 보고서 검색 hit의 배제 및 value-fingerprint query가 기록돼 있다. 이는 2024 기간의 순수 blind source search였다는 주장과 양립하지 않는 역사적 편차다. 채택 raw bytes는 검증된 2024 보고서이며 복구 이후 가격/outcome 탐색이나 값 우열을 보고 D1을 바꾼 행위는 하지 않았다. 이 제한을 삭제하거나 새 검색으로 덮지 않았다.

혼합 Q1/Q2, 공개일 노후도 차이, 전기 적자 분모, 잠정 Q2, F02-only, 작은 관측 집합, 52개 미입력 및 기존 노출 때문에 공식 순위·전시장 최적성·성능/OOS/holdout/모델개발 100%/release를 주장하지 않는다. 이 보고서는 좁은 기능 목표 달성 증거다.

## 7. Planned vs actual과 비용

원 계획 P50 125분 / 보수적 240분, LOW confidence를 변경하지 않았다. 보고 cutoff까지 wall 139.802분 (약 2시간 19.8분); final Git 봉인·readback 시간은 terminal 반환시각으로 추가 확인한다. 125분 계획은 초과했고 로컬 기능·보고 closure는 19:43 KST경, 4시간 checkpoint 21:17:55 KST 전에 끝났다. 후속 원격 전송 승인 대기는 그 이후까지 이어졌으며 기능 작업 미완료나 active execution으로 계산하지 않는다. 계획 초과로 validation gate를 생략하지 않았다.

첫 locator는 시작 후 10분39.646초로 약 15분 목표 충족. 30분 checkpoint는 17:47:55.1469424까지 저장되지 않았고 18:14:40.3012516에 26분45.154초 늦게 기록했다. 첫 executable input은 18:35:50.3101487, 시작 후 77분55.163초였다. source 완료와 executable input 성공을 같은 사건으로 부르지 않는다.

Source actions 33/48 (003160 10, 025560 5, 031980 9, 036200 9; cache 005290 0), source files 4/8, new bytes 4,774,865/20,000,000. 19 query + 4 result open + 8 source fetch + 2 fetch retry = 33 charged unique actions; 총 37 ledger records 중 control 4는 분리했다. retry flag 6은 action 종류 분해와 다른 계수다. source-human assistance 0, browser interaction 0; Owner의 runtime 복구 지시는 인간의 운영 지시이며 source 수동 선택은 아니다.

HTTP 총량 NOT_INSTRUMENTED (2 direct successful requests만 정확히 관측, 2 sandbox 시도 zero, 29 action의 내부 요청량 미측정). source action 33을 HTTP 33회로 둔갑시키지 않았다. 원격 Git readback은 source action이 아니며 sandbox network 실패 1회 후 허용된 read-only escalation으로 확인했다. 첫 push는 안전 검토에서 실행 전 차단돼 당시 전송 0이었다. 후속 Owner 승인 후 같은 task branch로 1차 전송이 성공했고 원격 commit이 일치했다. 이 보고 addendum의 최종 증분 push 결과는 terminal refs로 확정한다.

ACTIVE/WAIT/REWORK/CRU/token/재시작 지속시간은 NOT_INSTRUMENTED. 알려진 8.944초 affected recheck가 있으므로 누적 재작업 0이나 실측 비용절감율은 주장하지 않는다. 자세한 단계별 timing evidence/forecast 변화는 `PROGRESS_FORECAST_CALIBRATION_REPORT.md` 참조.

## 8. Exact Git·보존·readback

- Branch: `task/aaa/m3top3-f02-r1-multi-company-input-repair-20260905`.
- Worktree: `C:\Users\ms1pk\dev\asset-agent-asa\asset-agent-asa\r1`.
- Baseline PC1 commit `6b219f9f3a37dd89b26fc1d6ecec6b8eb890fa9f`, tree `c3dbfeac38c1490843ab7400960b63af5d941118`.
- Recovery commit `ca7bcfbc443768411c2ba2e182a45e1c92636c97`.
- P2 commit `8b1b9b17db211e529a7f21867ceb9c51724286be`.
- P3 operative/final validation target `cdfebb54ced5d75b402fb8605ee6ee5e4578bbdd`, tree `79d12edb12d15ad96a56b9656950f2d40e3f85a6`.
- P4 evidence commit `48eef6f3105112f637d8783395bcbad883d5af96`, tree `9ef55c25ec0654c8dcc0a26e2d525ec2093a2cae`.
- Final score/input payload commit `33b4690bb52b2fb1d593beee3b2549a7da70e699`, tree `5b2e5eff5cbd724d7cf1613520051bdc61bcb9c8`; clean readback before closure documents.
- Report-containing final closing commit/tree are returned exactly after committing this document; no self-referential fabricated hash is embedded here. `P6_PERSISTENCE_READBACK.json` identifies the already-observed payload checkpoint and full closing change set. This distinction is not a claim that the P5 parent is the report-containing final HEAD.

At 19:30:27 KST live remote readback, active locator `5b2dd5c5ea5bf96eb22163a0598d6879fffada9e`, organization `d7c490c373f2df356f31e4459c345328616b4eb3`, shared contract `4d70f6ae32604bcef3f4a8027074163d5e5c80cd`, remote main `950bc98b0702cd5564e3d7b24a6624d9818dfbb9` were unchanged from P0. Local main `fdd6a79c3611018b0f83c190e1f3de8a848fc58a` is separate existing work and was neither adopted nor changed. No new task remote ref was present at that readback; the first attempted push was rejected before execution. After explicit Owner follow-up authorization, the task ref was created and read back at `7ebbd2e6a64b46ee1d8c703ab8a9942f30c8dc42` by 2026-09-05T21:26:16.1024172+09:00.

Preserved old PC1 tree `0ea887bd547998678861baea5600045eb0b2e297`; old real-input output tree `d28a10eb6472452057fac383d5f63f07a5d6e455`; predecessor first-scorecard tree `1d73cc942a3524571ea214724c887c3964dca13f`. Thirteen model components match both predecessor Git blobs and recorded runtime hashes on their respective byte surfaces. Exact P4 32 target files remain unchanged.

Changed files are restricted to the four approved engineering paths, this versioned run root (including raw custody/receipts/reports), and PMO root journal. Root repository `.gitattributes` is preserved; only run-local `sources/.gitattributes` was added to preserve raw bytes. Full 52-path closing set is enumerated in `P6_PERSISTENCE_READBACK.json`; final tool readback checks it against actual Git diff. No unrelated deletion/overwrite.

## 9. 다음 행동

현재 승인 범위의 source/input/validation/점수·seal 및 task-branch 원격 보존은 종료한다. 추가 조사·다른 feature·다음 window·outcome/release·PR/main merge를 자동 시작하지 않는다. 새 provider/credential은 사용하지 않았다. 이 addendum을 포함한 최종 remote ref는 terminal 반환에서 확인한다.
