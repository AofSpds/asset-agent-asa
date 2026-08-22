# R-WP1-01 — M3Top3 v1 Exact Identity Recovery Report

```text
REPORT_ID = AAA-M3TOP3-R-WP1-01-IDENTITY-RECOVERY-20260823-01
WORK_PACKET = R-WP1-01 Exact Identity Recovery
EXECUTION_MODE = READ_ONLY
SEMANTIC_MUTATION = PROHIBITED
OUTCOME_TUNING = PROHIBITED
IVA_EXECUTION_PARTICIPATION = NONE
CURRENT_STATE = S0_PRE_OUTCOME_BASELINE_CANDIDATE
S0_TO_S1_ELIGIBILITY = NOT_ELIGIBLE
OVERALL_VERDICT = EXACT_EXECUTABLE_IDENTITY_NOT_RECOVERED
OWNER_IDENTITY_CHOICE_NOW = NOT_YET_REQUIRED
```

## 1. 결론

지정된 Git 이력·관련 branch family·현재 로컬 공급 원본을 read-only로 재탐색했으나, **M3Top3 v1을 그대로 실행·재현할 수 있는 하나의 exact release는 복구되지 않았다.** 정확히 회수된 것은 다음 세 부류다.

1. `SEMI-EVAL-CORE`, `SEMI-DATA-ROUTE`, `SEMI-PIT-LEDGER`, `SEMI-UNIVERSE`의 현재 공급 bytes와 일부 의미 원칙
2. 2026-08-15 이후의 working engineering infrastructure·Golden preparation bytes
3. 과거 `M3TOP3 GR Research Package v0.1/v0.2`를 exact하게 등록하려던 authorization과 두 ZIP의 예상 SHA-256·byte size

그러나 두 연구 ZIP 자체, 공식 scorer/config, F01–F09 전체 contract, gate·NA·tie·rank의 하나로 결속된 원본, environment lock, v1 전용 독립 expected outputs, `MARM-v1.0` release manifest, 완전한 outcome/winner access ledger는 현재 Git과 공급 파일에서 찾지 못했다.

따라서:

- `S0 → S1_EXACT_RECOVERED_BASELINE`: **금지**
- 현행 working infrastructure 또는 최근 문서로 `v1`을 재작성: **금지**
- Official Golden / Full Replay: **금지**
- Owner의 신규 identity 선택: **아직 요청하지 않음**. 먼저 아래의 정확한 두 ZIP recovery target에 대해 마지막 source-byte 회수 절차를 실행한다.

정확한 ZIP bytes가 회수되지 않거나 Owner/source custodian이 불가를 확인하면 그때만 Owner에게 `v1r-semantic-reconstruction` 신규 identity 또는 S0 archival 유지 중 하나를 요청해야 한다.

## 2. 탐색 범위

### GitHub

- Repository: `AofSpds/asset-agent-asa`
- default branch `main`
- M3Top3 exact-ZIP branch family 4개
  - `aaa-m3top3-gr-research-zip-registration-authorization-v0.1`
  - `aaa-m3top3-gr-research-zip-registration-execution-v0.1-v0.2`
  - `aaa-m3top3-gr-research-zip-registration-execution-recovery-r1-v0.1-v0.2`
  - `aaa-m3top3-gr-research-zip-registration-execution-recovery-r2-v0.1-v0.2`
- Core B authority/reconciliation branch family 및 PMO M3Top3 branch
- pre-infrastructure base commit `a02145cabf0c057591adf4098b630fca3a6453dc`
- relevant Git trees의 recursive path inventory와 exact blob readback

네 exact-ZIP branch는 모두 commit `654f0e97f5230c61101cd434905ca11070c6e5ed`, tree `a7873ba446fc5d3b94142fefa5121549cbaf9f73`를 가리켰다. 이 tree와 `main` 모두에서 아래 두 authorized target path는 GitHub contents readback `404 NOT_FOUND`였다.

### Local supplied sources

- `project_sources/06-Semi_Eval_Core_v1.0_2026-08-14.docx`
- `project_sources/07-Semi_Data_Route_v1.1_2026-08-14.docx`
- `project_sources/08-Semi_Universe_v1.0_2026-08-14.docx`
- `project_sources/09-SEMI-PIT-LEDGER_v1.0.docx`
- `qa/wp2_sources/U127_Data_Expansion_Working_v0.8_2026-08-15.xlsx`
- 기타 공급 source/register/schema 파일은 identity 보조근거로 확인

OOXML core metadata의 created/modified 값은 모두 `2013-12-23T23:15:00Z`인 생성기 기본값이어서 pre-outcome 생성시각 증거로 사용할 수 없다. 파일명·본문의 `2026-08-14`는 semantic label이며 독립 timestamp receipt가 아니다.

## 3. Component별 판정

| Component | 판정 | 복구된 내용 | 미충족 내용 / 영향 |
|---|---|---|---|
| 전체 v1 contract | `MISSING` | legacy source bytes와 후기 identity pointer | pre-outcome exact contract path/hash/timestamp 없음 |
| 공식 scorer | `MISSING` | working plugin interface와 `DiagnosticFixtureScorer` bytes | v1 scorer class/module/config hash 없음; diagnostic scorer는 대체 불가 |
| 공식 config | `MISSING` | working example JSON 2개 | plugin은 placeholder, window는 `UNRESOLVED_CONTROL`, generator commit은 null |
| F01–F09 mapping | `SEMANTIC_RECONSTRUCTION` | 6축 가중치와 Trigger 단계 등 일부 의미 | F01–F09 정의·scale·transform·availability·axis 결속 원본 없음 |
| weight vector | `SEMANTIC_RECONSTRUCTION` | 30/25/20/15/5/5가 `SEMI-EVAL-CORE`에 존재 | F01–F09→축→total의 exact executable mapping 없음 |
| gate | `MISSING` | 후기 리뷰에 gate 문제 언급 | 0.85/0.70 포함 공식 gate 산식·순서·rounding 원본 없음 |
| NA / missingness | `SEMANTIC_RECONSTRUCTION` | `NOT_FOUND != 0/negative`, no-silent-imputation pointer | full NA 재정규화·rankability·coverage/effective-weight 구현 원본 없음 |
| tie | `MISSING` | 후기 preparation은 company_id asc를 가리킴; infra는 official tie를 `UNRESOLVED_CONTROL`로 차단 | pre-outcome tie contract와 exact expected output 없음 |
| rank / Top-K | `SEMANTIC_RECONSTRUCTION` | 후기 pointer: full-precision desc, company_id asc, Top3 primary/Top10 diagnostic | underlying bound artifact 및 v1 executable proof 없음 |
| window / outcome | `SEMANTIC_RECONSTRUCTION` | legacy 일반 규칙: T EOD→next Open, next 3M snapshot next Open, MFE/MAE; v0.8에서 W1–W8 날짜 복구 | exact pre-outcome W1–W8 registry/hash 없음; v0.8은 outcome-exposed |
| environment lock | `MISSING` | stdlib tests와 optional DuckDB 언급 | requirements/pyproject/lock/container/platform receipt 없음 |
| v1 expected outputs | `MISSING` | GF01–GF20 taxonomy와 missing ZIP에 expected-result가 있었다는 pointer | concrete fixture bytes·독립 oracle·expected bundle 없음 |
| model release manifest | `MISSING` | `MARM-v1.0` pointer | exact manifest bytes/path/hash/state 없음 |
| outcome/winner provenance | `MISSING_WITH_KNOWN_EXPOSURE_FLOOR` | v0.8 bytes가 winner/MFE/full-rank를 포함; 2026-08-22 ASA run journal이 winner-readiness를 source set으로 명시 | 누가/무엇이/언제 outcome을 열람했는지 전 기간 ledger 없음; outcome-blind 지위 입증 불가 |

## 4. Exact evidence inventory

### 4.1 Legacy semantic source bytes — exact bytes, incomplete model identity

| Artifact | SHA-256 | Bytes | 정확히 입증하는 범위 |
|---|---:|---:|---|
| `Semi_Eval_Core_v1.0_2026-08-14.docx` | `3a8c70df26dee0b3c1430846cd9934aa237fd2075f322d78d899ed8cb81acc54` | 48,851 | 6축 3M weight 30/25/20/15/5/5, Trigger C0/C1/C2a/C2b/C3, NOT_FOUND 원칙 |
| `Semi_Data_Route_v1.1_2026-08-14.docx` | `508f98e88c150ceb751db2227727db529eb04da467c53a6eed5278ca5e17aa02` | 49,660 | PIT/source routing, Entry/Exit/MFE/MAE의 일반 규칙 |
| `Semi_Universe_v1.0_2026-08-14.docx` | `eef313bc71bd0a5cb019f92e43e1bf38c2a63633bb847320d1cb4c8fe4ea9023` | 42,132 | U46 current universe와 historical eligibility 원칙 |
| `SEMI-PIT-LEDGER_v1.0.docx` | `acde50e7090382e95cc585227c4dd52df6b3f342258b6debfa0aabb7db94006a` | 38,985 | append-only logical fields와 validation field contract |

이 bytes는 정확하지만 단독으로 F01–F09 scorer를 실행할 수 없으므로 전체 v1 identity를 `EXACT_RECOVERED`로 만들지 않는다.

### 4.2 Exact research-package recovery target — target identity recovered, package bytes missing

Authorization target:

- path: `control/architecture/working-candidates/research-working-candidate-persistence/registration-authorization/v0.1/AAA_M3TOP3_GR_RESEARCH_v0.1_v0.2_EXACT_ZIP_REGISTRATION_AUTHORIZATION_v0.1.json`
- commit: `0940227893c9439a2f196586067c5ec2e3f31959`
- tree: `95faa861034589bfa0932b3d97f157317b31a94d`
- Git blob: `2085322578ba779d7dbcddc69fb352ca137fb680`
- SHA-256: `ada5267873ba9aa19a10e83f26f9490711a79f9df781bc80167b51e992d387da`
- bytes: `15,954`

Authorized package targets:

| Package | Expected exact path | Expected SHA-256 | Expected bytes | Readback |
|---|---|---:|---:|---|
| v0.1 predecessor | `control/research/working-candidates/m3top3-gr-research-package/v0.1/AAA_M3TOP3_GR_RESEARCH_PACKAGE_v0.1_WORKING.zip` | `3aaee7c1de2bd6f97e5ffd808fba980bf73fea1b604fb3c3b79e2be005180002` | 35,775 | `NOT_FOUND` |
| v0.2 successor | `control/research/working-candidates/m3top3-gr-research-package/v0.2/AAA_M3TOP3_GR_RESEARCH_PACKAGE_v0.2_WORKING.zip` | `5bbe75a4c9966abcb9f10d2f1e84df983977c1cf76d69e7bda6dfe4f24e60836` | 40,210 | `NOT_FOUND` |

Authorization 자체는 `registration_execution_authorized=false`, `registration_execution_state=NOT_EXECUTED`, `registration_readback_state=NOT_EXECUTED`였다. 후속 L1/L2 receipts는 authorization target을 PASS했을 뿐 각각 `registration_execution_authorized_by_l1=false`, `registration_execution_authorized_by_l2=false`이며 ZIP bytes나 연구 의미를 검증한 receipt가 아니다.

Connected ChatGPT Library exact-source search (PMO-provided result):

- `LIBRARY_EXACT_SOURCE_SEARCH=NO_MATCH`
- search date: `2026-08-23 KST`
- searched surface: connected ChatGPT Library
- queries: both authorized ZIP filenames as exact-title queries; broad `M3TOP3_GR_RESEARCH_PACKAGE` and `GR Research Package` queries; both expected SHA-256 values
- scope limit: this establishes no match only on the searched Library surface. It does **not** establish global nonexistence of either ZIP.

### 4.3 Working engineering artifacts — exact bytes, non-official

| Artifact | Commit / observed tree | Git blob | 판정 |
|---|---|---|---|
| `control/m3top3/v0.1/M3TOP3-INFRASTRUCTURE-SPEC_v0.1.yaml` | commit `1cd98e5612d9f734c6215cc6ecee475534859d02` | `15ff7344f3547a0dd62eb8d92179c47d1b611583` | `WORKING_ENGINEERING`; v1 semantic release 아님 |
| `control/m3top3/v0.1/M3TOP3-BACKTEST-INTERFACE_v0.1.yaml` | commit `4e66b90d7136de5cb62c767a4ecc84d45e23f6e2` | `24612eaeb21904323bfb7ec2356c2e1e8daa2040` | backtest interface contract; official v1 semantics/release 아님 |
| `control/m3top3/v0.1/M3TOP3-SNAPSHOT-MANIFEST-CONTRACT_v0.1.yaml` | commit `35bd4fb56d2469850ca4fc38e636634b65c40882` | `3b0bad79e21d84efbe12921fd26ee5e336f7f9a1` | snapshot manifest contract; exact v1 scorer/config binding 아님 |
| `tools/m3top3/model_interface.py` | commit `2615bc34747f147cbc7ed1992c1c752185638868` | `1bc359a70a399a1eb94ef33703e2e5487afa8006` | plugin/ranking interface; official scorer 없음 |
| `tools/m3top3/configs/snapshot.example.json` | commit `dad9cc0d5dd07095910fca0dd9a31c40f08f456b` | `cb13d80be4ddb20bff73130e622c731153035b58` | `RECONSTRUCTION_v0.1_WORKING`, generator commit null |
| `tools/m3top3/configs/backtest.example.json` | commit `c5040082b8c20f22309fdf49eec29e2867ea47f7` | `05d7b40a511406d2f1057a0fa92010c27c7da33f` | scorer placeholder, tie/window unresolved |
| `tools/m3top3/tests/test_infrastructure.py` | commit `c7dfc55fe96fcfc0dd198ed1b50f18036704234c` | `354717bcd2f5bcc0b768ad76a674f25bd65b78d4` | synthetic infrastructure 25 tests; v1 expected output 아님 |
| `control/core_b/M3TOP3-v1-GOLDEN-REPLAY-SCIENTIFIC-PREPARATION_v0.3_WORKING.yaml` | observed in tree `537d7da7cd2ec7559c9587a94a422954e7f58d35` | `315bffb3d0803da7b6f7da18268b8ab6b0e3ba4b` | 내부 version `v0.2_WORKING`; model/MARM/implementation/release는 pending |

Golden preparation이 이름으로 참조한 `M3TOP3-FEATURE-SCHEMA_v1.0_WORKING`, `M3TOP3-GATED-LINEAR_v1.0_WORKING`, `M3TOP3-WEIGHT-VERSION_v1.0_WORKING`, `M3TOP3-PIT-CONSUMED-PROVENANCE-CONTRACT_v1.0_WORKING`, `WM-v1.1`, `M3TOP3-VALIDATION-CONTRACT_v1.0_WORKING`, `VDI-v1.0`, `MARM-v1.0`의 exact path/hash/bytes는 관련 recursive Git tree에서 발견되지 않았다. 따라서 pointer 자체만 exact이며 target binding은 성립하지 않는다.

### 4.4 Outcome exposure floor

- U127 v0.8 exact supplied bytes: SHA-256 `44501584c9dc6224637e9193219c1e8c87507af77dc15dc3944a3d04af524cda`, 563,995 bytes.
- 이 workbook에는 W1–W8 winner, MFE, full-rank reconstruction이 포함돼 있어 artifact 자체는 outcome-exposed다.
- Git run journal `control/persona-memory/v1.0/AAA-ASA/runs/2026-08-22/0701_m3top3_deep_review_asa.md`, blob `309db6a9e019ded5b30b57464c168b3ef2d6a87d`는 source set에 `U127 expansion/winner-readiness ledgers`를 명시한다.
- 이 기록은 늦어도 2026-08-22 해당 검토가 winner-readiness 자료에 노출됐다는 lower bound다. 반대로 original model authoring 시점이 outcome 이전이었다는 증거는 아니다.

## 5. S0 → S1 판단

`S1_EXACT_RECOVERED_BASELINE`에 필요한 아래 묶음 중 핵심 항목이 미충족이다.

- exact semantic contract: 미충족
- official scorer/source code: 미충족
- official config and config hash: 미충족
- environment/dependency/platform lock: 미충족
- v1-specific independent expected outputs: 미충족
- immutable model artifact release manifest: 미충족
- pre-outcome timestamp and access provenance: 미충족

따라서 `S0_TO_S1_ELIGIBILITY = NOT_ELIGIBLE`이며 S0 유지가 강제된다.

## 6. 다음 통제 조치와 Owner surface

### PMO가 승인 범위 내 즉시 할 일

1. 정확한 두 ZIP 파일명·SHA-256·byte size로 source custodian recovery를 한 번 더 수행한다.
2. 회수 시 변환·재압축 없이 bytes/hash/size를 확인하고 격리 보관한다.
3. v0.1↔v0.2 deterministic diff로 `14_CONTROLLED_SYNTHETIC_BINDINGS`, `EXPECTED_WORK`, `EXPECTED_RESULT`, `PIT_EVIDENCE`, `CONFLICT_REGISTER`의 존재·변경 범위를 확인한다.
4. ZIP 내부의 contract/scorer/config/env/tests/manifest/access-provenance가 모두 결속되는지 별도 S0→S1 candidate review를 발행한다.

### Owner 결정이 필요한 시점

현재는 `OWNER_IDENTITY_CHOICE_NOW = NOT_YET_REQUIRED`다. 정확한 recovery target이 이미 있으므로 source-byte 회수 시도를 먼저 끝내는 것이 정보가치가 높다.

다음 중 하나가 성립하면 Owner 결정을 요청한다.

- exact v0.1/v0.2 ZIP이 source custodian에서도 없다고 확인됨
- 회수 bytes가 expected SHA-256 또는 byte size와 불일치함
- ZIP 내부에도 official scorer/config/env/release/provenance가 없음

그때의 선택지는 다음 두 개다.

1. `S0_ARCHIVAL_BASELINE_IDENTITY_UNRESOLVED`로 보존
2. 별도 신규 identity `v1r-semantic-reconstruction`을 승인하고, original v1과 동일하다고 주장하지 않음

## 7. Claim locks

- `M3Top3 v1 exact recovered`: **FALSE**
- `M3Top3 v1 pre-outcome provenance proven`: **FALSE**
- `Current working scorer = official v1 scorer`: **FALSE**
- `GF01–GF20 taxonomy = Golden expected-output bundle`: **FALSE**
- `S1 / Freeze / Official Golden / Full Replay eligible`: **FALSE**
- `IVA execution participant`: **FALSE**
