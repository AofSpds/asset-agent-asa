# F05_R1_COMPLETION_REPORT

PROJECT = AAA · PRODUCT = ASSET AGENT ASA
RUN_ID = AAA-M3TOP3-F05-R1-20260905-231028-CODEX-01
REPORT_CUTOFF_KST = 2026-09-06T03:28:09+09:00
TERMINAL = COMPLETE_F05_R1_W1_PROVISIONAL

F05는 좋은 변화가 시장가격에 반영되기 시작했는지, 그리고 반영 속도가 이미 과열 구간에 들어갔는지를 보는 시장반응 항목이다. 이번 R1은 2024-08-09 W1 cutoff 이전의 20·60 거래구간 가격반응과 거래회전 가속도를, 당시 INCLUDE 57개사의 동일 분모 안에서 비교했다.

실제 계산 가능 수는 **57/57개사**다. 두 수익률 benchmark 모두 57개 전부를 사용했으며 분모 축소, 현행 종목군 대체, 결측 보간은 없었다.

기업행위(CA) 때문에 제외되거나 막힌 회사는 **0개**다. GST와 엑시콘의 W1 경계는 공식 발행사·KRX 근거로 닫혔다. 조정계수를 추정하지 않았고, CA 경계를 단순 raw-close 비율로 넘지 않았으며, 현금배당 재투자 총수익률로 바꾸지 않았다.

## 잠정 F05 상위 결과

| 잠정순위 | 회사 | 종목코드 | F05 |
|---:|---|---:|---:|
| 1 | 유진테크 | 084370 | 85.0000 |
| 2 | 월덱스 | 101160 | 85.0000 |
| 3 | 원익머트리얼즈 | 104830 | 85.0000 |
| 4 | 파크시스템스 | 140860 | 85.0000 |
| 5 | 와이씨 | 232140 | 85.0000 |
| 6 | 원익IPS | 240810 | 85.0000 |
| 7 | RF머트리얼즈 | 327260 | 79.6429 |

앞의 여섯 회사는 모두 같은 85점이다. 1–6이라는 번호는 고정된 `company_id` 오름차순 동점 규칙으로 재현성을 확보한 것이며 경제적 우열을 뜻하지 않는다. 회사명은 Owner가 읽기 쉽도록 기존 W1 cohort binding에서 사후 표시한 값으로, 점수 입력에는 사용되지 않았다.

이 결과가 말할 수 있는 것은 **고정 W1·고정 57개사 안에서 F05 기능 계산이 작동했고 잠정 횡단면 순위를 재현했다**는 것뿐이다. 공식 Top3/Top10, M3Top3 성과 PASS, holdout/OOS 성과, release 준비, 투자추천을 뜻하지 않는다. W1 outcome, W2–W8, PR, main 변경, merge, release, production은 실행하지 않았다.

## 별도 F02 + F05 잠정 보기

기존 F02가 계산 가능했던 다섯 회사만 별도 결합 보기에 포함했다. 다른 52개사는 이번 bundle에서 F05만 있으므로 아래 1–5 순위를 전체 57개사의 공식 순위로 읽으면 안 된다.

| 잠정순위 | 회사 | F02 | F05 | 잠정 결합점수 |
|---:|---|---:|---:|---:|
| 1 | 미래산업 (025560) | 87.5 | 61.6071 | 75.9921 |
| 2 | PSK홀딩스 (031980) | 87.5 | 39.1071 | 65.9921 |
| 3 | 동진쎄미켐 (005290) | 50 | 65.7143 | 56.9841 |
| 4 | 유니셈 (036200) | 25 | 20.5357 | 23.0159 |
| 5 | 디아이 (003160) | 0 | 41.0714 | 18.2540 |

결합식은 기존 의미를 유지한 `(25×F02 + 20×F05) / 45`다. 다섯 행의 feature coverage는 0.3이고 나머지 52개 F05-only 행은 0.2다. 이 보기는 F02의 `EXPLORATORY_AFTER_W1_OUTCOME_EXPOSURE` 제한을 그대로 상속하므로 blind-process 또는 성과 검증으로 확대할 수 없다.

## 1. 입력·계산 의미

- Cutoff: `2024-08-09T23:59:59+09:00`; post-cutoff 가격이나 outcome을 열지 않았다.
- 고정 population: W1 INCLUDE 57개사만 사용했다. `EXCLUDE_PROVEN` 8개와 `EXCLUDE_UNRESOLVED` 62개는 benchmark에 포함하지 않았다.
- 원자료: 57×61 = 3,477행, 회사별 3개 metric = 171개 slice. 가격 parquet SHA-256은 `b0c38943e67637d5faf88429880092cf0f46a394be39860dd3bcd0b04231bccb`다.
- 20d/60d: 각각 20/60 일간 수익률 interval, 21/61 거래일 관측이다. `ChangesRatio / 100`을 일별 수익률로 해석해 `∏(1+r)-1`로 복리 계산했다.
- Benchmark: horizon별 admissible 57개 수익률의 단순 동일가중 평균이다. 양 horizon 모두 정확히 57/57이다.
- Turnover: 일별 `Volume / Stocks`; 최근 20거래일 평균을 직전 20거래일 평균으로 나눈 뒤 1을 뺐다.
- F05: weight 20과 기존 recognition velocity `0.50/0.30/0.20`, saturation, scorer/config 의미를 유지했다. 선택 valuation/diffusion 입력을 새로 만들거나 취득하지 않았다.
- 최종 F05 input은 267,149 bytes, SHA-256 `8e5c2991eb1c14bede88300a5fd1d648ce263d3e7a3d6a83b31af9b1e3d873f7`; F02+F05 merged input hash는 `78d540e5e0385104ba21a744e28897762f4d15af25f571de1cc57136882b2500`이다.

## 2. GST·엑시콘 CA 판정

- GST: 2024-06-26 권리락과 2024-07-24 추가상장 경계를 공식 근거에 결합했다. KRX 기준가격 21,700원과 상장 후 총주식수 18,618,260주를 증거로 보존했다.
- 엑시콘: 2024-06-03 권리락과 2024-07-31 추가상장 경계를 공식 근거에 결합했다. KRX 기준가격 19,470원과 상장 후 총주식수 13,050,797주를 증거로 보존했다.
- 공식 CA evidence manifest SHA-256은 `3fa931f83edb8d5bf3baf493d770cedc1ffa2f4f56ce8aae7a1171ded45fa50b`, byte-custody SHA-256은 `84a53966ca5233b699a8b5448ccd13ceede683dc555304945df76c7ba62d7eb7`다.

## 3. 구현·검증 disposition

모델·weight·downstream transform·PIT·eligibility는 바꾸지 않고, 기존 parquet의 필수 field를 semantic-neutral 방식으로 노출하는 전용 builder와 fail-closed score envelope만 추가했다. 새 provider, paid source, credential, budget은 사용하지 않았다.

D0 검증에서 formal receipt identity/path/custody gate 부족 `CTLV-D0-001`이 발견돼 D0는 score 대상으로 폐기됐다. 이는 Owner 정책 변경이 아닌 승인 범위 내 구현통제 결함이었다. 정확한 D1 correction을 적용하고 D0 PASS를 전용하지 않은 채 CTLV L1, MODV L1, ENGV L1, IVA L2를 모두 새로 실행했다.

D1 exact target `2700dda2fee8b4f8b6cfab9c075f8b860ffc94f9` / tree `c98194af223562e440d66c47b57f6696110ced47`에 대해 네 역할 모두 PASS, finding 0이다. 34/34 target file, 57/57 source reconstruction, 11/11 CA custody, 118/118 전체 test zero-skip, 8,607 raw-row reads, 171 metric 일치, IVA 43,810 assertions가 확인됐다. 초기 ENGV lane 하나는 verdict 전에 peer evidence 노출을 발견해 폐기했고, fresh-context ENGV만 PASS를 발행했다. 그 reconciliation SHA-256은 `a6900bde24aeaddf7d0cd4a2c12d972bdad2e7444d586c6401d411135a2cbfbd`다.

통합 affected validation report는 13,924 bytes, SHA-256 `ef2fd2c6f53286b332e839cea08a286809f504bf21014da1ade884098adf77e8`, status `PASS`, `scoring_permitted=true`다.

## 4. 1회성 점수 실행과 사후 대조

네 역할의 D1 PASS가 커밋된 clean HEAD `e4a3aacfb1c6b59063cf1968f96e82763833c120`에서 production score CLI를 create-once로 정확히 한 번 실행했다. Engine run ID는 `m3run_d76f0878dc3ced762337fe37b591b3cd`; 재실행은 0회다.

| 산출물 | 행 | Bytes | SHA-256 |
|---|---:|---:|---|
| `F05_R1_W1_SCORES.jsonl` | 57 | 56,858 | `37c5a27505fb4786f7ee4d4cb5f51d8c5ba5ad39542226ac6f0361ac4f7d744d` |
| `F05_R1_W1_PROVISIONAL_RANKING.csv` | 57 | 8,969 | `7cfd2d09fa802ce93092826da4746fb25509ab5358655e6b58532f3190aa5360` |
| `F02_F05_PROVISIONAL_MULTI_FEATURE_VIEW.csv` | 5 | 1,055 | `5746b865e22bf8896f89d460c02e73d8a0c85e3e975f711b09a6877153125f61` |

Root readback 21/21에 이어 fresh IVA L2가 score payload commit `e273b052c8ef663ae0f151c5747e9112b4cd811d` / tree `e272648ee236b4d5866dd09e818749486386771a`를 독립 재검증했다. Production module을 import하거나 score engine을 부르지 않고 Decimal 산식을 재구성해 57개 F05 점수·rank와 다섯 결합행을 전부 일치시켰다. Validator assertions 868개와 별도 grouped invariant 29/29가 PASS했고 finding은 0이다. IVA receipt SHA-256은 `a3771e516da22de778eadfd16dde567f0a194e1870091766304b9e2e8f9a8a3e`다.

## 5. Bundle·seal

- Bundle ID: `f05r1bundle_7c700db5b89ae06e85ed5c8ba718ce68`; canonical payload SHA-256 `7c700db5b89ae06e85ed5c8ba718ce68b39c9cabc1915c4d554aedf5cf7f7bec`.
- Bundle manifest raw SHA-256: `af6644c80078e3adf12a4cf5a32a579aff21f363f6c079168bf660ed95bcf046`; Git blob `0552dcf18a828a2912cb3f2f117a46619caa265f`.
- Provisional result seal ID: `f05r1seal_c4473f7ba95384195397e8c514545705`; canonical sealed-payload SHA-256 `c4473f7ba95384195397e8c514545705960932cc83d1fae1f1d51da4f6512e0a`.
- Seal raw SHA-256: `55ef59f1f565e2a36dbef840eb95a8ef9335c53fbf1c236e0ea459b85bed2e43`; Git blob `db6675b64bd15258acdfaf53f2fc13b8f585f3d0`.
- 이것은 provisional result 무결성 seal이며 selection seal이 아니다. `top3_flag`와 `top10_flag`는 57행 모두 false다.

## 6. 승인·Git·보존

- Owner policy: commit `709ded3f4440142c05a97dcc03b286ad49fa149b`, tree `e081e1a980fbace8e4909ce132bf5d03aaacffef`, blob `ab65b65182fddaf31c1b7e0d7e1f0341f4bbdf9e`, SHA-256 `2bd9ae341904c562a25513286b6546c737df92bfa3a6ca82434c71de396fbacb`.
- Execution request: commit `ab1a9a52cbee1825a2ff725a8b997307f7f5e16e`, tree `a8e4f0e8f8e1955e687f575cb1db2d559bb23cdc`, blob `370c86569717aa1b93ecc748a06766d0400946e0`, SHA-256 `452b64ac36d37860f72da6367e62fef1c175af3d56b4379651c232e2ab988a53`.
- No-redundant-question direction: commit `6db4a549d5e1a8e18ffe1226ad70e4bf090ba696`, tree `b6b499920cfe79e434658294b0ec2d9239d5cdaa`, blob `23f7d89ccd7c3ce1a2c36aeab1162011b75afc14`, SHA-256 `cf10e7ccac34b433c8379f175a9b724ec39ad1a083c1937f0b437683c3e7eb38`.
- Branch: `task/aaa/m3top3-f05-r1-w1-market-positioning-20260905`; worktree: `C:\Users\ms1pk\dev\asset-agent-asa\asset-agent-asa\f05-r1`.
- Composition: commit `5fb34b229868d66b6f8a02d9686445c6c4b9398d`, tree `44771b00d126fa4f73767c90a156a70559a23945`.
- Validation closure: commit `e4a3aacfb1c6b59063cf1968f96e82763833c120`, tree `3b51b2d1d0517945c2004b0918634746a2e4fb2a`.
- Score payload: commit `e273b052c8ef663ae0f151c5747e9112b4cd811d`, tree `e272648ee236b4d5866dd09e818749486386771a`.
- Post-score IVA payload: commit `9de0bcedb5287b47d2a09082d7ffc1d41c5e9867`, tree `174f8512c0669443b8ac2f9b57dac3390963205f`.
- 이 보고서가 들어 있는 closing commit은 자기참조 해시를 문서 안에 만들지 않는다. 정확한 closing/persistence/final local·remote commit과 tree는 `F05_R1_PERSISTENCE_READBACK.json` 및 terminal 반환에 제시한다.

기존 F02-R1 input·과거 PC1/score/seal, W1 cutoff, model weight/features/scorer, eligibility 분모는 보존했다. 변경은 F05-R1 전용 implementation/test, 이 versioned run root, PMO journal, raw-custody line-ending 규칙으로 제한했다. 임시 검증 runtime은 exact task path만 제거했고 score·input·증거 byte는 삭제하지 않았다.

## 7. 계획 대비와 종료 경계

계획은 P50 2시간20분, P90 5시간, LOW confidence였다. 23:10:28 시작부터 이 보고 cutoff까지 wall은 약 4시간17분41초로 P50을 넘었으나 P90 안이다. D0 correction과 fresh four-role D1 revalidation, 상세 post-score 독립 재계산을 생략하지 않았다. active/wait/rework/CRU/token/cost는 계측하지 않았으므로 추정 절감률을 주장하지 않는다.

현재 승인된 F05-R1 W1 기능 결과만 닫는다. 추가 feature 조사, W2–W8, outcome/MFE tuning, 공식 선택, PR/main/merge/release/production은 자동 시작하지 않는다. Owner가 새로 결정할 항목은 없다.
