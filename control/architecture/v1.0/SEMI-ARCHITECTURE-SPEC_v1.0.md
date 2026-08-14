# SEMI-ARCHITECTURE-SPEC v1.0

**Semiconductor Research Permanent Data Infrastructure & Operating Contract**

| Field | Value |
|---|---|
| DOC_ID | `SEMI-ARCHITECTURE-SPEC` |
| VERSION | `v1.0` |
| ARCHITECTURE_STATUS | `FROZEN / ACTIVE ARCHITECTURE CONTRACT` |
| FREEZE_STATUS | `COMPLETE` |
| FREEZE_DATE | `2026-08-14` |
| FREEZE_DECISION | `APPROVED` |
| SCOPE | 반도체 연구 프로젝트 장기 데이터·문서·PIT·평가 인프라 |
| AUTHORITY | Architecture / Storage / Version / Lineage / Write / Migration 최상위 Contract |
| MIGRATION_STATUS | `NOT STARTED / NOT PERFORMED` |

> **핵심 원칙**  
> Normalize for storage, denormalize for retrieval.  
> Canonical history는 보존하고, Current는 생성한다.  
> 과거의 사실·판단·점수는 현재 정보로 overwrite하지 않는다.

> **PIT / Model / Validation 핵심 원칙**  
> `PIT Snapshot = 당시 무엇을 알고 있었는가`  
> `Model Score = 그 정보를 특정 모델이 어떻게 평가했는가`  
> `Validation = 그 평가 이후 실제로 무엇이 일어났는가`  
> 모델 변경은 PIT Snapshot을 수정하거나 복제하지 않는다.

---

# 0. Normative Language

| Keyword | Meaning |
|---|---|
| **MUST** | 반드시 준수 |
| **MUST NOT** | 절대 금지 |
| **SHOULD** | 특별한 사유가 없는 한 준수. 예외는 Audit 필요 |
| **SHOULD NOT** | 특별한 사유가 없는 한 금지 |
| **MAY** | 선택적 구현 가능 |

본 문서의 MUST/MUST NOT은 Architecture Freeze 이후 모든 Migration·운영·자동화·LLM workflow에 적용한다.

## 0.1 Normative Overrides / Conflict Resolution

본 Architecture v1.0은 기존 프로젝트 Source의 **모델 의미를 변경하지 않는다.**

다만 기존 Source 사이에 운영문구·저장 위치·판정 시점에 대한 충돌 또는 모호성이 존재하는 경우, 아래 항목에 한하여 본 Architecture v1.0의 규칙이 **Normative Override**로 우선한다.

### Override A — PIT Score Evidence Cutoff

Legacy 문구 중 다음 기준:

```text
publication_datetime <= Entry cutoff
AND
available_before_entry = TRUE
```

를 PIT Score Evidence eligibility의 최종 기준으로 사용하지 않는다.

Architecture v1.0 최종 기준:

```text
publication_at <= snapshot_cutoff_at
```

즉:

```text
Score Evidence Cutoff
=
snapshot_cutoff_at
```

이다.

`available_before_entry`는 Validation / Audit / information-timing 보조정보로 유지 MAY이나, Score eligibility의 authoritative condition이 아니다.

### Override B — Snapshot Correction / Score Correction / Model Change

Architecture v1.0에서는 세 가지 변경을 서로 다른 version axis로 관리한다.

**A. PIT Snapshot Data Correction**

대상:

- 잘못된 Evidence 연결
- 잘못된 Observation
- parsing 오류
- snapshot 당시 존재했던 정보의 누락
- 잘못된 PIT state
- identifier 오류

처리:

```text
same business snapshot
snapshot_revision + 1
supersedes_ref = prior PIT-SNAPSHOT
model_version = NOT APPLICABLE
```

PIT Snapshot correction 때문에 `model_version`을 생성하거나 변경하지 않는다.

**B. Model Score Correction**

동일 PIT Snapshot과 동일 model definition을 사용했으나 다음과 같은 scoring record 오류가 발견된 경우:

- component 입력 연결 오류
- score serialization 오류
- implementation 오류
- 단순 산술 오류
- 잘못된 output mapping

처리:

```text
same pit_snapshot_record
same model_version
score_revision + 1
supersedes_ref = prior MODEL-SCORE
```

**C. Model Methodology Change**

다음과 같은 방법론 변화:

- 가중치 변경
- Trigger 해석 변경
- scoring formula 변경
- component 정의 변경
- component maximum 변경
- evaluation semantics 변경

은:

```text
new model_version
score_revision = 0
```

으로 처리한다.

**모델 변경은 기존 PIT Snapshot을 수정하거나 복제하지 않는다.**

### Override C — Universe Architecture

Legacy의 Current Universe / Historical Eligible 표현은 Architecture v1.0에서 다음 3계층으로 해석·운영한다.

```text
DISCOVERY UNIVERSE
OPERATIONAL UNIVERSE
TRADABLE ELIGIBLE
```

실제 Backtest 대상:

```text
BacktestUniverse_T
=
OperationalUniverse_T
∩
TradableEligible_T
```

반도체 소부장 사업범위상 포함 여부는 Tradability가 아니라 Operational Membership에 속한다.

### Override D — Price Universe Eligible Flag

Legacy Price schema 또는 Price dataset에:

```text
Universe_Eligible_Flag
```

가 존재하더라도, Architecture v1.0 이후 해당 필드를 Universe membership의 authoritative Canonical fact로 사용하지 않는다.

향후 Canonical 구조에서는 Universe eligibility를:

```text
Universe Membership History
+
Tradability / PIT State
```

에서 파생한다.

Legacy `Universe_Eligible_Flag` 자체는 Migration 시 삭제하거나 재해석하지 않고 원형 보존한다.

### Override E — Legacy Combined PIT / Score Schema Supersession

Legacy `SEMI-PIT-LEDGER v1.0` 및 `SEMI-DATA-ROUTE v1.1`에 존재하는 다음 구조는 Architecture v1.0에서 **명시적으로 대체(supersede)** 한다.

Legacy combined structure:

```text
PIT
=
Snapshot State
+ Evidence
+ Model Interpretation
+ Score
+ Validation
```

Legacy PIT logical key:

```text
company_id
+ snapshot_date
+ model_version
```

Legacy standard Snapshot output에 포함된:

```text
Identity
+ F1/F2/F3
+ Trigger / Conversion
+ 3M Score
+ Validation
```

의 combined schema 역시 Architecture v1.0 이후의 authoritative canonical design으로 사용하지 않는다.

Architecture v1.0의 authoritative structure는 다음이다.

```text
PIT-SNAPSHOT
      +
MODEL-DEFINITION
      ↓
MODEL-SCORE
      ↓
VALIDATION
```

각 객체의 의미는 다음과 같이 분리한다.

```text
PIT-SNAPSHOT
= 당시 무엇을 알고 있었는가

MODEL-DEFINITION
= 특정 모델이 그 정보를 평가하는 규칙은 무엇인가

MODEL-SCORE
= 해당 모델이 그 Snapshot을 어떻게 평가했는가

VALIDATION
= 그 평가 이후 실제로 무엇이 일어났는가
```

따라서 다음 Legacy 규칙은 더 이상 authoritative rule이 아니다.

```text
company_id + snapshot_date + model_version
```

를 PIT Snapshot의 logical key로 사용하는 것.

다음 역시 더 이상 authoritative PIT-SNAPSHOT schema가 아니다.

- Model-specific interpretation을 PIT의 고정 state로 저장
- Score component를 PIT row에 직접 저장
- Validation을 PIT row에 직접 저장
- `score_frozen` 하나로 Snapshot과 Score freeze를 동시에 표현

Architecture v1.0에서는:

```text
PIT-SNAPSHOT
MODEL-DEFINITION
MODEL-SCORE
VALIDATION
```

의 객체 분리를 authoritative rule로 사용한다.

### Override Scope

본 절의 Override는 저장·운영 충돌을 해소한다. 다음 기존 의미는 변경하지 않는다.

- 모델 가중치
- Trigger 정의
- β 정의
- M1~M4/S
- F0/F1/F2/F3의 원래 조사 목적
- Source Routing
- Refresh Code
- Evidence Class / Status
- Fab stage 의미
- 가격 Entry / Exit / MFE / MAE 원칙
- NOT_FOUND 처리원칙

충돌이 없는 기존 Source 정의는 그대로 유지한다.

---

# 1. AI Quick Index

| 목적 | Search Key |
|---|---|
| Normative Override | cutoff · correction · universe · price eligibility · combined PIT supersession |
| Architecture 최상위 원칙 | Source of Truth · Control Plane · Data Plane |
| Canonical / Generated View | Canonical · Current View |
| Raw / Normalized / Derived | RAW · NORMALIZED · DERIVED |
| 공통 Append-only 규칙 | valid_from · recorded_at · supersedes_ref |
| Company 구조 | COMPANY-IDENTITY · STRUCTURE-HISTORY · STATE-HISTORY |
| Fab 구조 | FAB-IDENTITY · FAB-STATE-HISTORY |
| Company↔Fab | COMPANY-FAB |
| Universe 3계층 | Discovery · Operational · Tradable |
| Source / Evidence | SOURCE · EVIDENCE · Evidence Origin |
| Event Ledger | event_id · fingerprint · idempotency |
| PIT Snapshot | PIT-SNAPSHOT · snapshot_cutoff_at · snapshot_revision |
| Model Definition | MODEL-DEFINITION · model_version · score components |
| Model Score | MODEL-SCORE · score_revision · score_frozen |
| Validation | VALIDATION · model_score_id |
| Price | Entry Open · Exit Open · MFE · MAE |
| Active Manifest | active-manifest.yaml |
| Schema Registry | schemas/ |
| Run Manifest | run_id · run_mode · run_role · prompt_hash · input_hash |
| Write Safety | STAGING · VALIDATION · COMMIT |
| Version Policy | immutable · revision · release |
| Storage | Git · Large Data · DuckDB |
| Migration | Audit PASS · Regression · Cutover |
| LLM Retrieval | Bootstrap · Current View |
| Freeze 검토 | FREEZE ACCEPTANCE CHECKLIST |

---

# 2. Purpose

`SEMI-ARCHITECTURE-SPEC`의 목적은 다음을 하나의 최상위 운영 Contract로 Freeze하는 것이다.

1. 어떤 자산이 Source of Truth인지 정의한다.
2. 어떤 데이터가 Canonical이고 어떤 데이터가 Generated View인지 정의한다.
3. Historical State와 Current State의 저장 방식을 정의한다.
4. PIT·Evidence·Universe·Price의 재현성 규칙을 정의한다.
5. Rule·Schema·Model·Data Correction의 Version 축을 분리한다.
6. LLM·사람·자동화가 Canonical을 안전하게 읽고 쓸 수 있는 경계를 정의한다.
7. 향후 Legacy Migration의 검증·승격·Cutover 조건을 정의한다.

본 문서는 **사업·기술 사실을 재평가하는 문서가 아니다.**

---

# 3. Absolute Scope Restrictions

Architecture Contract의 Freeze 자체는 실제 Migration 실행을 의미하지 않는다.

Architecture 승인만으로 다음 작업을 수행하지 않는다.

- 기존 프로젝트 Source 수정
- 기존 DOCX overwrite
- 기존 모델 가중치 수정
- Trigger 정의 수정
- β 정의 수정
- M1~M4/S 정의 수정
- PIT 과거 데이터 수정
- Universe 실제 편입/삭제
- Format Migration 실행
- Canonical 실데이터 생성
- Price Ledger 실제 변환
- 과거 Snapshot 재구축
- 기존 자료의 사실관계 재평가
- Active Canonical cutover

Migration은 Architecture 이후 별도 Gate를 따른다.

---

# 4. Top-Level Architecture Principles

## 4.1 Source of Truth

### MUST-1 — ChatGPT Project

`ChatGPT Project`는:

- Workspace
- Analysis Environment
- Bootstrap Environment
- Review Environment

로 사용한다.

`ChatGPT Project` 자체는 **영구 Canonical Source of Truth가 아니다.**

### MUST-2 — External Canonical Storage

장기 Canonical record는 외부 Canonical Storage에 저장한다.

Canonical Storage는 다음을 만족해야 한다.

- persistent
- version identifiable
- auditable
- hashable where practical
- append-only history capable
- external backup capable

### MUST-3 — Git = Control Plane

Git 계층은 **Control Plane**으로 사용한다.

주 저장 대상:

- Rules
- Schemas
- Active Manifest
- Release Manifest
- Run Manifest
- Audit definition / small audit records
- Version history
- Small structured master
- Mapping / Registry
- LLM Bootstrap document

대형 Raw binary와 대형 시계열 데이터는 기본적으로 Git Control Plane에 저장하지 않는다.

### MUST-4 — Large Data Storage = Data Plane

Large Data Storage는 **Data Plane**이다.

주 저장 대상:

- Raw source documents
- Raw binary
- large Parquet
- Price
- large PIT partitions
- Event history when large
- Evidence history when large
- Legacy binary/document archive

### MUST-5 — Rule = Versioned Immutable

한 번 release된 Rule은 수정하지 않는다.

Rule 변경 필요 시:

- 기존 Rule 보존
- 신규 version 생성
- 변경 이유 기록
- 적용 시작점 기록

을 MUST로 한다.

### MUST-6 — Canonical History = Append-only

Canonical History / Ledger는 기존 record를 현재 정보로 덮어쓰지 않는다.

수정은:

- new state
- correction revision
- cancellation event
- superseding record

중 하나로 append한다.

### MUST-7 — Current = Generated View

현재 상태는 Canonical History를 읽어 생성한다.

Current View 자체를 History의 원천으로 사용하지 않는다.

### MUST-8 — No Historical Overwrite

과거 Canonical record는 현재 정보를 이유로 overwrite하지 않는다.

### MUST-9 — Format Migration ≠ Content Revision

Format 변경과 의미 변경을 하나의 Migration에서 동시에 수행하지 않는다.

예:

`DOCX → JSONL`

과

`고객구조 LOW → HIGH 수정`

을 같은 작업으로 처리하면 안 된다.

### MUST-10 — Raw / Normalized / Derived Separation

RAW, NORMALIZED, CANONICAL HISTORY, MODEL DERIVED, VALIDATION을 물리적·논리적으로 구분한다.

---

# 5. Normative Dependencies / Semantic Preservation

본 Architecture는 기존 모델 의미를 재정의하지 않는다.

## 5.1 Model / Operation Dependencies

| Dependency | Preserved Meaning |
|---|---|
| `SEMI-EVAL-CORE v1.0` | F0/F1/F2, 3M 가중치, Trigger, β, M1~M4/S |
| `SEMI-DATA-ROUTE v1.1` | F3 observation/source routing/refresh/price validation semantics, Architecture Override 적용 |
| `SEMI-UNIVERSE v1.0` | 현재 평가대상 baseline 및 historical eligibility intent |
| `SEMI-COMPANY-MASTER v0.1` | F1 Structural seed |
| `SEMI-FAB-MASTER v1.0` | Fab identity/state baseline 및 stage enum |
| `SEMI-PIT-LEDGER v1.0` | Legacy append-only/freeze intent; combined schema/key는 Override E로 superseded |
| `SEMI-SOURCE-INDEX v1.0` | Legacy LLM retrieval routing baseline |

## 5.2 Technology / Industry Dependencies

다음 자료의 기존 의미를 수정하지 않는다.

- Samsung Semiconductor Future Technology Platform Map v1.1
- Future Semiconductor System Architecture Memory Manufacturing Map v1.0
- Korea Semiconductor Equipment CAPEX Early-Revenue Response Map v1.0
- SK Hynix CAPEX Korea Equipment Ecosystem Report v0
- Korea Semiconductor SupplyChain TOP38 Master Scorecard v2.2 Detail

## 5.3 Preserved Enums

### Trigger

- `C0`
- `C1`
- `C2a`
- `C2b`
- `C3`

의 의미는 `SEMI-EVAL-CORE`를 따른다.

### 3M Weight

- Trigger/Catalyst 30
- Forward Earnings/Order 25
- Expectations Gap/Valuation 20
- Conversion Visibility 15
- Market Recognition 5
- Evidence Integrity/Freshness 5

본 Architecture가 가중치를 변경하지 않는다.

### β Types

정확히 다음 7종을 유지한다.

1. `Equipment-fill β`
2. `Utilization β`
3. `Process-intensity β`
4. `Packaging/HBM β`
5. `Test/Product-cycle β`
6. `Metrology/System-yield β`
7. `Foundry-cycle β`

### Technology Maturity

| Code | Meaning |
|---|---|
| M4 | 상용 / 양산 |
| M3 | sample / qualification / pilot / 초기 적용 |
| M2 | 공식 roadmap / 개발 |
| M1 | 연구 / prototype |
| S | 구조적 분석 |

### Evidence Class

- `FACT`
- `INDUSTRY_ESTIMATE`
- `MODEL_ASSUMPTION`
- `SPECULATIVE_OPTION`

### Evidence Status

- `VERIFIED`
- `PARTIAL`
- `NOT_FOUND`
- `CONFLICT`
- `STALE`

`NOT_FOUND`는 사업 부재를 의미하지 않는다.

---

# 6. Canonical vs Generated View

## 6.1 Canonical

다음은 장기 재현성과 Audit을 위해 보존해야 하는 Canonical이다.

- Rules
- Schemas
- Source Registry
- Evidence
- Event History
- Company Identity
- Company Structure History
- Company State History
- Fab Identity
- Fab State History
- Company-Fab relationship history
- Universe Membership History
- PIT-SNAPSHOT
- MODEL-DEFINITION
- SCORE-COMPONENT-DEFINITION
- MODEL-SCORE
- MODEL-SCORE-COMPONENT
- VALIDATION
- Price
- Run Manifest
- Release Manifest
- Audit History

Canonical은 Source of Truth이다.

## 6.2 Generated View

다음은 Canonical에서 생성되는 View다.

- `COMPANY-CURRENT`
- `FAB-CURRENT`
- `UNIVERSE-CURRENT`
- `COMPANY-FAB-CURRENT`
- `PIT-SNAPSHOT-CURRENT`
- `MODEL-SCORE-LATEST`
- `MODEL-SCORE-FLAT`
- `VALIDATION-SUMMARY`
- LLM flat views
- `SEMI-MASTER-INDEX`
- Dashboard / report extracts

Generated View는:

- Source of Truth가 아니다.
- 필요 시 삭제 가능하다.
- Canonical에서 재생성 가능해야 한다.
- Generated View 자체의 수정으로 Canonical이 변경되면 안 된다.

## 6.3 Principle

> **Normalize for storage, denormalize for retrieval.**

Storage 구조는 일관성·Audit·History를 우선하고, LLM retrieval 구조는 빠른 읽기와 문맥 회수를 우선한다.

---

# 7. Data Layer Contract

```text
RAW
 ↓
NORMALIZED SOURCE / EVIDENCE / EVENT / OBSERVATION
 ↓
CANONICAL STATE HISTORY
 ↓
PIT-SNAPSHOT
 ├───────────────┐
 ↓               ↓
MODEL-SCORE A   MODEL-SCORE B
Model v0.1      Model v0.2
 ↓               ↓
VALIDATION      VALIDATION
```

Event는 모든 PIT input의 필수 중간단계가 아니다.

Periodic / observational data는 별도 Event 생성을 강제하지 않는다.

예:

- Price
- Consensus
- Valuation
- periodic F3 Snapshot observation
- regularly sampled market data
- dataset-derived observation

이 경우 PIT는 필요한 lineage 조건을 충족하면:

```text
SOURCE / EVIDENCE / DATASET
        ↓
   PIT-SNAPSHOT
```

경로를 직접 사용할 수 있다.

## 7.1 RAW

RAW는 수집된 원본이다.

예:

- DART 문서
- KIND 문서
- IR PDF
- Newsroom page capture
- raw CSV
- raw Parquet
- source DOCX
- API response archive

RAW는 모델 판단으로 수정하지 않는다.

## 7.2 NORMALIZED

Normalized layer는 Raw의 의미를 구조화한다.

주요 객체:

- SOURCE
- EVIDENCE
- EVENT
- OBSERVATION

Normalized는 원본을 대체하지 않는다.

## 7.3 CANONICAL HISTORY

State / membership / PIT input을 시간축에 따라 보존한다.

## 7.4 MODEL DERIVED

모델 점수·등급·해석·ranking 등이다.

FACT와 별도 계층이다.

## 7.5 VALIDATION

- Entry
- Exit
- Return
- MFE
- MAE
- Universe Excess
- time_to_peak
- giveback
- Backtest metrics

를 포함한다.

---

# 8. Common Canonical Record Contract

Canonical state/history 계열은 가능한 한 다음 공통 원칙을 사용한다.

## 8.1 Core Fields

| Field | Requirement | Meaning |
|---|---|---|
| `*_record_id` | MUST | Canonical row unique ID |
| `entity_id` | MUST | Company/Fab/etc. identifier |
| `field_or_state` | MUST where applicable | 변경 대상 |
| `value` | MUST where applicable | 구조화된 값 |
| `valid_from` | MUST where applicable | 해당 상태가 사실상 유효해진 시점 |
| `recorded_at` | MUST | 시스템에 기록된 시점 |
| `record_revision` | MUST where applicable | correction revision, initial=`0` |
| `supersedes_ref` | MUST nullable | 수정 대상 record |
| `evidence_id` | SHOULD / context-dependent | 근거 연결 |
| `schema_version` | MUST | schema identifier |

## 8.2 Timestamp Rules

모든 datetime은 timezone-aware여야 한다.

기본 timezone:

`Asia/Seoul`

UTC 저장을 사용할 경우에도 원본 timezone 또는 offset을 복원할 수 있어야 한다.

다음은 서로 다른 의미다.

- `valid_from`
- `publication_at`
- `recorded_at`
- `created_at`
- `snapshot_cutoff_at`
- `frozen_at`

서로 대체해서 사용하지 않는다.

## 8.3 valid_from

`valid_from`은 해당 state/fact가 적용되는 경제적·운영상의 시점을 의미한다.

## 8.4 recorded_at

`recorded_at`은 해당 record가 Canonical system에 기록된 시점이다.

Historical backtest의 Evidence eligibility를 `recorded_at`으로 판단하지 않는다.

Historical Score의 정보 사용 가능성은 `publication_at`과 `snapshot_cutoff_at`으로 판단한다.

## 8.5 valid_to

Canonical Historical row에 `valid_to`를 갱신하기 위해 과거 record를 UPDATE하는 방식을 기본으로 사용하지 않는다.

`valid_to`는 Generated SCD View에서 파생한다.

```text
valid_to
=
same entity + same field의
다음 유효 state.valid_from 직전
```

마지막 state:

```text
valid_to = OPEN / NULL
```

따라서:

```text
valid_from = Canonical
valid_to   = Derived
```

## 8.6 Same valid_from Collision

같은 entity / field / valid_from에 correction이 존재하면:

1. supersession chain
2. `record_revision`
3. correction status

를 이용해 effective record를 선택한다.

단순 `MAX(recorded_at)`만으로 History를 결정하지 않는다.

---

# 9. Company Architecture

```text
COMPANY-IDENTITY
       +
COMPANY-STRUCTURE-HISTORY
       +
COMPANY-STATE-HISTORY
       ↓
COMPANY-CURRENT
```

## 9.1 COMPANY-IDENTITY

목적:

기업의 안정적 식별.

최소 후보:

- `company_id`
- `krx_code`
- `canonical_name`
- `english_name`
- `market`
- `aliases`
- `dart_corp_id`
- listing identity
- canonical locator

`company_id`는 MUST immutable이다.

기업명·시장·alias처럼 장기적으로 변할 수 있는 identity attribute는 silent overwrite하지 않는다.

기업명 변경·합병·분할 등은:

- identity revision
- corporate action/event
- PIT tradability/history

와 연결한다.

## 9.2 COMPANY-STRUCTURE-HISTORY

기존 F1/R1 중심 구조정보를 보존한다.

F1이라고 해서 영구불변으로 간주하지 않는다.

다음과 같은 R1 Event 발생 시 새 state를 append한다.

- M&A
- 사업재편
- 핵심제품 변경
- 공정위치 변화
- 주요 고객구조의 구조적 변화
- β transmission 구조 변화

과거 F1 record는 수정하지 않는다.

## 9.3 COMPANY-STATE-HISTORY

기존 F2/R2 중심 상태값을 보존한다.

대표 field:

- Qualification
- Installed Base
- Vendor Share
- Design Win
- Repeat Order
- Customer Expansion
- Technology Maturity
- Capacity Ceiling
- Moat state/change
- confirmed customer/application state

상태 변화는 새 record로 append한다.

## 9.4 COMPANY-CURRENT

`COMPANY-CURRENT`는 Generated View이다.

각 field별 latest effective record를 조합하여 생성한다.

`COMPANY-CURRENT` 자체를 직접 편집하지 않는다.

---

# 10. Fab Architecture

```text
FAB-IDENTITY
     +
FAB-STATE-HISTORY
     ↓
FAB-CURRENT
```

## 10.1 FAB-IDENTITY

대표 필드:

- `fab_id`
- customer
- site
- project_or_line
- memory_or_foundry
- long-lived identity metadata

## 10.2 FAB-STATE-HISTORY

Fab stage 및 관련 상태를 append-only로 관리한다.

Fab stage enum은 다음을 유지한다.

```text
PLANNING
CONSTRUCTION
UTILITY_CLEANROOM
PROCESS_FLOW_FIXED
EQUIPMENT_ORDER
MOVE_IN
INSTALL_SETUP
QUALIFICATION
PILOT
RAMP
MASS_PRODUCTION
```

다음 사건들은 서로 다른 Event다.

```text
착공
≠ Cleanroom
≠ Equipment Order
≠ Move-in
≠ Install
≠ Qualification
≠ Pilot
≠ Ramp
≠ Mass Production
```

공식 Source가 특정 단계를 확인하지 않으면 추정하여 다음 단계로 승격하지 않는다.

## 10.3 FAB-CURRENT

Generated View이다.

Fab stage history와 기타 state history에서 생성한다.

## 10.4 No Fab Duplication by Company

Fab의 현재 stage를 각 Company record에 복제하지 않는다.

Fab 상태 변경은 `FAB-STATE-HISTORY`에서 한 번만 기록한다.

---

# 11. COMPANY-FAB Bridge

Company와 Fab의 구조적 노출을 연결한다.

## 11.1 Logical Schema

최소 후보:

- `company_fab_record_id`
- `company_id`
- `fab_id`
- `process_exposure`
- `beta_type`
- `exposure_strength`
- `evidence_id`
- `valid_from`
- `recorded_at`
- `record_revision`
- `supersedes_ref`
- `schema_version`

SHOULD:

- `evidence_class`
- `confidence`

## 11.2 Rule

Bridge는:

> 해당 회사가 해당 Fab의 어떤 공정/β 경로에 노출되는가

를 저장한다.

Bridge는 Fab의 실제 stage를 저장하지 않는다.

Stage는 `FAB-STATE-HISTORY`에서 조회한다.

---

# 12. Universe Architecture

Universe를 반드시 세 계층으로 구분한다.

## 12.1 DISCOVERY UNIVERSE

조사·Scanner용 Wide Universe.

Discovery에 포함됐다는 사실만으로 모델 평가대상이 되는 것은 아니다.

## 12.2 OPERATIONAL UNIVERSE

특정 Snapshot 당시 모델이 실제 평가 대상으로 선택한 기업 집합.

Operational membership은:

> **Selection Decision**

이다.

반도체 소부장 사업 범위상 포함할지 여부는 이 계층에서 결정한다.

## 12.3 TRADABLE ELIGIBLE

기계적 PIT 거래 가능 조건.

예:

- listing
- delisting
- suspension
- Entry-day tradability
- trading status
- corporate action constraints

Tradability는 사업범위 판단이 아니다.

## 12.4 Backtest Universe

```text
BacktestUniverse_T
=
OperationalUniverse_T
∩
TradableEligible_T
```

Discovery Universe는 직접 Backtest Universe가 아니다.

## 12.5 Universe Membership History

최소 필드:

- `universe_record_id`
- `universe_id`
- `universe_type`
- `company_id`
- `valid_from`
- `recorded_at`
- `inclusion_reason`
- `universe_rule_version`
- `evidence_id`
- `record_revision`
- `supersedes_ref`
- `schema_version`

`universe_rule_version`은 **MUST**다.

## 12.6 Universe Rule Change

과거 membership rule을 현재 기준으로 조용히 다시 분류하지 않는다.

Universe rule 변경 후 과거 Snapshot을 재평가하면:

- 신규 `universe_rule_version`
- 신규 `universe_release_id`
- 신규 `run_id`

로 기록한다.

## 12.7 Universe Release

실제 평가/백테스트 입력용 Universe set은 immutable release로 고정할 수 있어야 한다.

예:

- `universe_release_id`
- `universe_rule_version`
- member count
- generated_at
- content hash

Run Manifest는 해당 release ID와 hash를 저장한다.

---

# 13. SOURCE → EVIDENCE Lineage

Canonical lineage의 시작은 다음과 같다.

```text
SOURCE
  ↓
EVIDENCE
```

단, Evidence의 origin이 항상 외부 SOURCE인 것은 아니다.

## 13.1 SOURCE

SOURCE는 문서·공시·페이지·파일 자체다.

최소 후보:

- `source_id`
- `source_type`
- `source_tier`
- title
- publisher
- publication metadata
- canonical URI/reference
- raw storage reference
- acquired_at
- raw hash
- status

Raw Source는 모델 판단으로 수정하지 않는다.

## 13.2 EVIDENCE

EVIDENCE는 평가·상태판정·Event·PIT에서 참조 가능한 원자적 주장 또는 명시적 모델 추론 단위다.

최소 필드:

- `evidence_id`
- `source_id` nullable where `MODEL_DERIVED`
- `evidence_origin`
- `publication_at` nullable where not applicable
- `evidence_class`
- `fact`
- `source_tier` nullable where not applicable
- `confidence`
- `status`
- `extracted_at`

SHOULD:

- source locator
- page / section / paragraph reference
- publication precision
- extraction version

## 13.3 Evidence Origin

`evidence_origin`은 반드시 다음을 구분한다.

```text
SOURCE_DERIVED
MODEL_DERIVED
```

### SOURCE_DERIVED

외부 또는 등록 Source/Dataset에서 직접 추출된 Evidence.

### MODEL_DERIVED

모델·분석 프로토콜이 Source-derived 정보 또는 구조정보를 바탕으로 생성한 판단·추론.

`MODEL_DERIVED`는 외부 Source가 직접 말한 Fact로 취급하지 않는다.

## 13.4 Evidence Class

허용 의미는 기존 정의를 유지한다.

```text
FACT
INDUSTRY_ESTIMATE
MODEL_ASSUMPTION
SPECULATIVE_OPTION
```

`MODEL_ASSUMPTION`은 기본적으로:

```text
evidence_origin = MODEL_DERIVED
```

로 취급한다.

`MODEL_ASSUMPTION`을:

```text
SOURCE_DERIVED FACT
```

처럼 취급하면 안 된다.

## 13.5 Evidence Status

```text
VERIFIED
PARTIAL
NOT_FOUND
CONFLICT
STALE
```

`NOT_FOUND`는 Retrieval failure이며 0점 또는 부정 사실을 자동 의미하지 않는다.

## 13.6 Evidence Reuse

동일 Evidence는 여러 Company, Fab, Event, Technology, PIT가 참조할 수 있다.

Evidence를 entity별로 불필요하게 복제하지 않는다.

---

# 14. Event Ledger

전체 프로젝트에 하나의 **논리적 Event Ledger**를 둔다.

Event는 모든 PIT input의 강제 중간단계가 아니다.

## 14.1 Event Scope

Event는 **discrete business/state change**를 정규화하는 데 사용한다.

대표 대상:

- PO
- Qualification
- Volume Order
- Repeat Order
- Design Win
- Fab Move-in
- Ramp
- Capacity Expansion
- Guidance change
- Technology Maturity transition

다음 observational data는 Event row 생성을 강제하지 않는다.

- Daily Price
- Market Cap
- Consensus level
- Forward EPS snapshot
- Valuation
- regular utilization observation
- periodic F3 observation
- market-recognition observation

## 14.2 Entity Types

예:

```text
COMPANY
FAB
CUSTOMER
TECHNOLOGY
```

## 14.3 Event Types

기본 예:

- PO
- QUALIFICATION
- VOLUME_ORDER
- REPEAT_ORDER
- EARNINGS
- BACKLOG
- GUIDANCE
- CAPACITY_EXPANSION
- FAB_MOVE_IN
- RAMP
- DESIGN_WIN
- TECHNOLOGY_MATURITY

기존 Trigger·Fab stage의 의미를 Event type으로 재정의하지 않는다.

## 14.4 Event Core

최소 후보:

- `event_record_id`
- `event_id`
- `entity_type`
- `entity_id`
- `event_type`
- `event_effective_at`
- `recorded_at`
- `record_revision`
- `supersedes_ref`
- `event_fingerprint`
- `schema_version`

## 14.5 Event ↔ Evidence

관계는 논리적으로 N:M을 지원해야 한다.

## 14.6 Direct PIT Input Path

Event가 불필요한 관측 데이터는 PIT가 직접 참조할 수 있다.

허용 lineage 예:

```text
PRICE DATASET
    ↓
PIT-SNAPSHOT
```

```text
CONSENSUS DATASET
       ↓
SOURCE_DERIVED EVIDENCE
       ↓
PIT-SNAPSHOT
```

```text
SOURCE
  ↓
EVIDENCE
  ↓
PIT-SNAPSHOT
```

## 14.7 Event Correction / Cancellation

기존 Event를 삭제하지 않는다.

Correction 또는 cancellation은 신규 revision / 신규 event state / `supersedes_ref`로 기록한다.

## 14.8 Initial Partition Policy

초기부터 과도한 월 partition을 만들지 않는다.

실제 규모·query profile이 요구할 때 partition granularity를 높인다.

---

# 15. Event Idempotency / Duplicate Control

## 15.1 ingest_idempotency_key

같은 Source/Evidence를 같은 pipeline이 반복 ingest하여 duplicate row가 생성되는 것을 방지한다.

`ingest_idempotency_key`는 deterministic해야 한다.

## 15.2 event_fingerprint

서로 다른 Evidence가 실제 동일 경제적 사건을 설명하는지 판단한다.

## 15.3 No Double Counting

서로 다른 Source가 같은 PO를 확인했다고 여러 개의 PO로 합산하면 안 된다.

Multiple Evidence는 confidence 증가와 cross-validation 강화에 사용하며 경제적 수량을 자동 증가시키지 않는다.

## 15.4 Fingerprint Collision

`event_fingerprint` 충돌만으로 무조건 merge하지 않는다.

경제적 동일성 검증이 필요하다.

---

# 16. PIT-SNAPSHOT Architecture

`PIT-SNAPSHOT`은 **모델 독립적 Point-in-Time Information Freeze**이다.

목적:

> 특정 Snapshot cutoff 시점까지 시스템이 알 수 있었던 상태·Evidence·Observation을 재현한다.

PIT-SNAPSHOT은 모델 판단 결과를 저장하지 않는다.

## 16.1 PIT-SNAPSHOT에 포함하는 것

대표적으로 다음을 포함하거나 참조한다.

### Identity / Tradability

- company identity
- listing state
- trading state
- corporate action state
- universe state/reference

### F1 / F2 effective state

Snapshot 시점까지 유효했던:

- structural state
- qualification
- design win
- installed base
- vendor share
- technology maturity
- capacity state
- Fab-related effective state

### F3 Observations

- price
- market cap
- valuation source observation
- forward EPS observation
- forward OP observation
- revision observation
- backlog
- shipment
- utilization
- CAPEX observation
- consensus observation

### Evidence / Dataset References

- evidence IDs
- source IDs
- dataset IDs
- observation IDs
- publication timestamps
- Evidence status / origin

## 16.2 PIT-SNAPSHOT에 포함하지 않는 것

다음은 PIT-SNAPSHOT의 authoritative field가 아니다.

- `model_version`
- Trigger score
- Trigger model interpretation
- Earnings/Order score
- Expectations Gap score
- Conversion score
- Recognition score
- Evidence Integrity score
- Total Score
- model component score
- model ranking
- model confidence derived from scoring
- Validation return

모델에 종속되는 해석은 `MODEL-SCORE`에 저장한다.

## 16.3 PIT Snapshot Business Identity

Architecture v1.0의 **authoritative Business Snapshot Key**는:

```text
company_id
+ snapshot_cutoff_at
```

이다.

`snapshot_cutoff_at`은 timezone-aware timestamp다.

기본 timezone:

```text
Asia/Seoul
```

`snapshot_date`는 계속 저장하되 역할은:

```text
convenience / search / partition / reporting field
```

이다.

`snapshot_date` 자체는 PIT-SNAPSHOT의 authoritative identity가 아니다.

## 16.4 PIT Snapshot Revision Identity

Revision identity:

```text
company_id
+ snapshot_cutoff_at
+ snapshot_revision
```

Canonical immutable identifier:

```text
pit_snapshot_id
```

권장 구조:

```text
pit_snapshot_id
company_id
snapshot_cutoff_at
snapshot_date
snapshot_schema_version
snapshot_revision
supersedes_ref
capture_run_id
snapshot_frozen
snapshot_frozen_at
```

## 16.5 PIT Snapshot Version Axes

1. `snapshot_schema_version`
2. `snapshot_cutoff_at`
3. `snapshot_revision`
4. `capture_run_id`

Convenience metadata:

```text
snapshot_date
```

`model_version`은 PIT-SNAPSHOT version axis가 아니다.

## 16.6 Snapshot Correction

정보 오류 발견 시:

```text
same company_id + snapshot_cutoff_at
snapshot_revision + 1
supersedes_ref = prior snapshot revision
```

기존 revision은 삭제하지 않는다.

## 16.7 Snapshot Freeze

PIT Snapshot 자체의 freeze state:

```text
snapshot_frozen
snapshot_frozen_at
```

를 사용한다.

`PIT-SNAPSHOT`에는 `score_frozen`이 존재하지 않는다.

## 16.8 Snapshot Freeze 의미

`snapshot_frozen = TRUE`는 해당 Snapshot revision이 Canonical historical input으로 사용되었으며 destructive mutation을 금지한다는 의미다.

Correction은 새 `snapshot_revision`으로 append한다.

## 16.9 Model Independence Invariant

하나의 PIT Snapshot은 여러 model version의 MODEL-SCORE에서 참조할 수 있다.

새로운 model version을 실행한다고:

- PIT Snapshot을 복사하지 않는다.
- snapshot_revision을 증가시키지 않는다.
- Snapshot Evidence를 모델별로 복제하지 않는다.

## 16.10 Observed F3 vs Model-Derived F3 Interpretation

PIT-SNAPSHOT은 Snapshot cutoff 당시 이용 가능했던 원천 Observation 및 Evidence를 보존한다.

예:

- Price
- Market Cap
- PER/PBR/EV
- Forward EPS / OP source value
- Consensus value
- EPS revision observation
- Earnings
- Guidance
- PO
- Backlog
- Shipment
- Customer CAPEX
- Fab state
- Utilization / Wafer start
- Qualification fact
- Volume / Repeat order fact
- 거래량
- 뉴스·리포트 확산 관측
- Evidence freshness를 계산할 수 있는 publication timestamp
- source/evidence/dataset reference

다음과 같이 **특정 모델의 정의·threshold·scoring logic에 따라 결과가 달라질 수 있는 판단**은 PIT-SNAPSHOT의 authoritative state로 저장하지 않는다.

- `Trigger Stage`
- `Expectations Gap`
- `Conversion Visibility`
- `Market Recognition`
- model-specific Evidence Integrity judgment
- model-specific Catalyst interpretation
- model-specific Recognition grade
- model-specific conversion stage interpretation

이들은 `MODEL-SCORE` 또는 model-specific feature layer에 귀속한다.

## 16.11 Raw Observation vs Derived Interpretation Example

PIT-SNAPSHOT은 다음을 저장할 수 있다.

```text
Price return since prior snapshot = +18%
Trading volume percentile = 92
Analyst report count = 11
Major media mentions = observed
PO announced = TRUE
Backlog increased = observed
Forward EPS revision = +7%
```

그러나 다음은 Snapshot 자체의 사실이 아니다.

```text
Market Recognition = HIGH
Trigger Stage = C2b
Expectations Gap = POSITIVE_HIGH
Conversion Visibility = 12/15
```

## 16.12 Source-Derived Commercial State Exception

`qualification completed`, `volume order confirmed`, `shipment started`, `revenue recognized`는 Source/Evidence가 직접 뒷받침하면 PIT-SNAPSHOT에 포함 가능한 business state 또는 observation이다.

반면:

```text
qualification completed
→ therefore Trigger = C2a
```

에서 `C2a`는 model-derived interpretation이다.

즉:

```text
Commercial Fact
≠
Model Trigger Classification
```

이다.

---

# 17. MODEL-DEFINITION

모델의 scoring semantics는 versioned immutable definition으로 관리한다.

`MODEL-DEFINITION`은 모델 방법론의 Canonical definition이다.

최소 후보:

```text
model_version
model_name
model_family
scoring_protocol_version
effective_from
definition_status
component_definition_ref
trigger_definition_ref
model_rule_ref
created_at
```

기존 3M 모델의 가중치·Trigger 정의는 현재 의미 그대로 해당 model definition에 연결한다.

## 17.1 Score Component Definition

Score component의 이름·개수·최대점수를 PIT schema에 hard-code하지 않는다.

모델별 component definition은 extensible collection으로 관리한다.

현재 3M-v0.1의 component 정의:

```text
Trigger/Catalyst              max 30
Forward Earnings/Order        max 25
Expectations Gap/Valuation    max 20
Conversion Visibility         max 15
Market Recognition            max 5
Evidence Integrity/Freshness  max 5
```

의 의미는 그대로 유지한다.

다만 이 값을 PIT schema의 고정 column으로 만들지 않는다.

## 17.2 Extensible Component Definition Schema

최소 후보:

```text
component_definition_id
model_version
component_key
component_name
component_order
max_score
weight_or_rule
required
definition_ref
```

---

# 18. MODEL-SCORE Architecture

`MODEL-SCORE`는 특정 `PIT-SNAPSHOT`을 특정 `MODEL-DEFINITION`으로 평가한 결과다.

```text
PIT-SNAPSHOT
     +
MODEL-DEFINITION
     ↓
MODEL-SCORE
```

## 18.1 MODEL-SCORE Core Fields

최소:

```text
model_score_id
pit_snapshot_id
model_version
score_schema_version
score_revision
supersedes_ref
scoring_run_id
score_frozen
score_frozen_at
total_score
evaluation_status
created_at
```

## 18.2 MODEL-SCORE Logical Identity

Business Score Key:

```text
pit_snapshot_id
+ model_version
```

Canonical Score Revision Key:

```text
pit_snapshot_id
+ model_version
+ score_revision
```

동일 PIT Snapshot에 여러 model_version의 Score가 공존할 수 있다.

## 18.3 Score Revision

`score_revision`은 동일 `pit_snapshot_id + model_version` 입력에 대한 scoring record correction만 의미한다.

## 18.4 Snapshot Revision ≠ Score Revision

두 revision은 완전히 독립적이다.

```text
snapshot_revision
≠
score_revision
```

Snapshot correction이 발생하면 corrected Snapshot으로 모델을 재실행하여 새로운 lineage를 만든다.

이를 기존 Score의 단순 `score_revision`으로 처리하지 않는다.

## 18.5 Model Change

동일 PIT Snapshot을 새 methodology로 평가할 경우:

```text
same pit_snapshot_id
new model_version
score_revision = 0
```

이다.

PIT Snapshot은 변하지 않는다.

## 18.6 Score Freeze

MODEL-SCORE는:

```text
score_frozen
score_frozen_at
```

을 사용한다.

`score_frozen`은 `snapshot_frozen`과 독립적이다.

---

# 19. MODEL-SCORE-COMPONENT

개별 component score는 column-per-component 방식이 아니라 extensible child records로 저장한다.

```text
MODEL-SCORE
      ↓
MODEL-SCORE-COMPONENT[]
```

최소 후보:

```text
score_component_id
model_score_id
component_key
component_value
component_status
component_explanation_ref
evidence_refs
```

`component_key`는 해당 `model_version`의 `COMPONENT-DEFINITION`을 참조한다.

## 19.1 No PIT Score Hard-coding

다음과 같은 PIT schema 고정 필드는 사용하지 않는다.

```text
Trigger_30
Earnings_Order_25
Expectations_Gap_20
Conversion_15
Recognition_5
Evidence_Integrity_5
```

현재 모델 출력용 Generated View에서는 필요 시 펼칠 수 있으나 Flat View는 Generated View이다.

## 19.2 Total Score

`total_score`는 MODEL-SCORE level에서 model definition에 따라 저장한다.

Component 합과 Total 간 consistency는 Audit 대상이다.

---

# 20. Validation Architecture

Validation은 PIT Snapshot 자체가 아니라 **특정 Model Score / Evaluation**을 대상으로 한다.

```text
PIT-SNAPSHOT
     ↓
MODEL-SCORE
     ↓
VALIDATION
```

## 20.1 Validation Core Fields

최소 후보:

```text
validation_id
model_score_id
pit_snapshot_id
model_version
price_dataset_id
validation_protocol_version
entry
exit
return
MFE
MAE
universe_excess
time_to_peak
giveback
created_at
```

authoritative evaluation reference는:

```text
model_score_id
```

이다.

## 20.2 Same Market Outcome / Different Scores

동일 Snapshot의 실제 이후 시장 경로는 동일하더라도 여러 Model Score가 존재할 수 있다.

각 모델 평가 성능을 별도로 추적한다.

## 20.3 Validation Does Not Alter Snapshot or Score

Validation 결과가 좋거나 나쁘다는 이유로:

- PIT Snapshot 수정 금지
- Score 수정 금지
- model weight 자동 변경 금지

Model 개선은 별도의 methodology versioning 절차를 따른다.

---

# 21. PIT Score Evidence Cutoff

## 21.1 Final Score Cutoff

```text
Score Evidence cutoff
=
snapshot_cutoff_at
```

Score Evidence eligibility:

```text
publication_at <= snapshot_cutoff_at
```

이어야 한다.

## 21.2 Entry-day New Information

Snapshot 다음 날 Entry 이전에 공개된 자료는 이전 Snapshot 점수에 사용하지 않는다.

## 21.3 available_before_entry

`available_before_entry`는 보존 MAY.

그러나 Score Evidence eligibility의 기준으로 사용하지 않는다.

## 21.4 available_before_snapshot_cutoff

다음 파생/감사 field를 둘 수 있다.

`available_before_snapshot_cutoff`

## 21.5 Publication Time Precision

Evidence publication time을 임의 생성하지 않는다.

날짜만 알려진 자료가 Snapshot 당일 발표됐고 발표 시각을 확인할 수 없다면, score eligibility를 위해 임의 시각을 만들어서는 안 된다.

## 21.6 recorded_at Is Not Cutoff

Historical reconstruction에서 `recorded_at`이 늦다는 이유만으로 과거에 공개되어 있던 Source를 배제하지 않는다.

Score 정보 가용성의 핵심은 `publication_at`이다.

---

# 22. Price Architecture

Price는 시장 원천 상태와 Validation 가격을 제공한다.

Universe membership을 결정하지 않는다.

## 22.1 Provider Rule

Canonical Price는 동일 KRX-derived OHLC 원장을 유지한다.

Provider 혼합 금지.

## 22.2 Price Core

대표:

- Date
- Code
- Name
- Open
- High
- Low
- Close
- Volume
- Amount
- Marcap
- Stocks
- Market
- Corporate_Action_Flag
- Trading_Status
- Corporate_Action_Type
- Adjustment_Factor
- Action_Source
- Action_Confidence
- Raw_Provider

## 22.3 Universe Eligibility Separation

Legacy schema의 `Universe_Eligible_Flag`는 Raw/Legacy 보존 대상이다.

그러나 향후 Canonical Price의 business truth field로 사용하지 않는다.

Universe eligibility는 Universe Membership + Tradability + PIT rule에서 파생한다.

## 22.4 Entry

```text
Entry
=
Snapshot 다음 거래일 Open
```

## 22.5 Exit

```text
Exit
=
다음 3M Snapshot의 다음 거래일 Open
```

## 22.6 MFE

실제 holding period 중 High 기준 최대 유리 변동.

Exit가 Exit-day Open이라면 Exit 이후 장중 High는 holding period에 포함하지 않는다.

## 22.7 MAE

실제 holding period 중 Low 기준 최대 불리 변동.

Exit 이후 가격을 포함하지 않는다.

## 22.8 Corporate Action

주식수 급변 또는 OHLC discontinuity는 audit signal일 수 있으나 자동 adjustment factor가 아니다.

`Adjustment_Factor`는 evidence-backed인 경우에만 사용한다.

## 22.9 Trading Status

가능한 범위에서 suspension, no-trade, delisting, administrative status를 보존한다.

Historical Tradable Eligibility는 Entry-day 실제 거래 가능성과 연결한다.

## 22.10 Raw Price

Raw Price dataset은 immutable asset으로 취급한다.

변환/보정 dataset은 별도 `price_dataset_id`와 version을 가진다.

## 22.11 Existing BLOCKED Audit

`SEMI-PRICE-LEDGER_v1.0_INGEST-AUDIT_BLOCKED_2026-08-14.csv`는 삭제하지 않는다.

이는 Historical Failure Audit으로 보존한다.

---

# 23. Active Manifest

Machine-readable Active pointer를 MUST로 둔다.

권장명:

`active-manifest.yaml`

## 23.1 Purpose

현재 어떤 immutable artifact/version을 운영 기준으로 사용하는가를 선언한다.

## 23.2 Minimum Candidate Fields

- `manifest_version`
- `release_id`
- `updated_at`
- `current_architecture`
- `current_model`
- `current_core`
- `current_route`
- `current_universe_rule`
- `pit_schema`
- `price_schema`
- `source_schema`
- `evidence_schema`
- `event_schema`
- `repository_commit_sha`

## 23.3 Manifest Rule

Manifest가 가리키는 모든 artifact는 실제 존재해야 한다.

Release 전 Audit/CI는 artifact existence, version consistency, schema compatibility, hash where specified를 확인해야 한다.

## 23.4 Active Pointer Update

새 release 승격 시 Active Manifest pointer update를 마지막 단계로 수행한다.

검증 실패 시 기존 Active Manifest는 변경하지 않는다.

---

# 24. SEMI-MASTER-INDEX

`SEMI-MASTER-INDEX.md`는 LLM Bootstrap용 Generated View다.

```text
active-manifest.yaml
        ↓
SEMI-MASTER-INDEX.md
```

MASTER INDEX는 유일한 Source of Truth가 아니다.

---

# 25. Schema Registry

Schema drift를 방지하기 위한 Registry를 MUST로 둔다.

초기에는 과도한 enterprise schema platform을 도입하지 않는다.

## 25.1 Initial Logical Registry

```text
schemas/
  company.schema.yaml
  fab.schema.yaml
  company_fab.schema.yaml
  universe.schema.yaml
  source.schema.yaml
  evidence.schema.yaml
  event.schema.yaml
  pit_snapshot.schema.yaml
  model_definition.schema.yaml
  model_score.schema.yaml
  score_component.schema.yaml
  validation.schema.yaml
  price.schema.yaml
  run_manifest.schema.yaml
```

## 25.2 Minimum Schema Definition

각 Schema는 최소:

- `field`
- `type`
- `nullable`
- `enum`
- `logical_key`
- `description`
- `schema_version`

을 정의한다.

SHOULD:

- default
- constraints
- semantic reference
- deprecated flag

## 25.3 Schema Version

Schema version은 business/model version과 별개다.

두 축은 독립적으로 관리한다.

---

# 26. SEMI-RUN-MANIFEST

평가·백테스트 한 번의 실행조건을 완전히 복원할 수 있는 Run Manifest를 MUST로 둔다.

## 26.1 Minimum Candidate Fields

- `run_id`
- `run_mode`
- `run_role`
- `snapshot_date`
- `snapshot_cutoff_at`
- `model_version`
- `scoring_protocol_version`
- `prompt_spec_version`
- `prompt_hash`
- `pit_schema_version`
- `universe_release_id`
- `universe_release_hash`
- `price_dataset_id`
- `price_dataset_hash`
- `evidence_cutoff`
- `input_artifact_manifest`
- `input_hashes`
- `code_commit_sha`
- `executor_type`
- `llm_model_id`
- `created_at`

## 26.2 Run Mode

```text
LIVE_PIT
HISTORICAL_RECONSTRUCTION
REPLAY
DIAGNOSTIC
```

`LIVE_PIT`과 `HISTORICAL_RECONSTRUCTION`만 Canonical 생성 후보가 될 수 있다.

`REPLAY`와 `DIAGNOSTIC`은 Canonical PIT/Score를 자동 변경하지 않는다.

## 26.3 Run Role

```text
SNAPSHOT_CAPTURE
MODEL_SCORING
VALIDATION
```

## 26.4 Snapshot Capture Run

`run_role = SNAPSHOT_CAPTURE`

목적:

```text
Source / Dataset / Evidence / State
              ↓
          PIT-SNAPSHOT
```

Snapshot capture run에는 `model_version`이 필수가 아니다.

## 26.5 Model Scoring Run

`run_role = MODEL_SCORING`

목적:

```text
PIT-SNAPSHOT
+
MODEL-DEFINITION
      ↓
MODEL-SCORE
```

## 26.6 Validation Run

`run_role = VALIDATION`

입력은 특정 `model_score_id`다.

## 26.7 Canonicalization — Snapshot Run

동일:

```text
company_id
+ snapshot_cutoff_at
+ snapshot_revision
```

Canonical PIT Snapshot revision을 생성한 authoritative capture Run은 하나만 지정한다.

## 26.8 Canonicalization — Scoring Run

동일:

```text
pit_snapshot_id
+ model_version
+ score_revision
```

Canonical MODEL-SCORE를 생성한 authoritative scoring Run은 하나만 지정한다.

## 26.9 Replay / Diagnostic Isolation

REPLAY / DIAGNOSTIC은:

- PIT Snapshot 자동 변경 금지
- Snapshot revision 자동 생성 금지
- MODEL-SCORE 자동 correction 금지
- score_revision 자동 증가 금지

결과 차이는 Audit/Diagnostic output으로만 기록한다.

## 26.10 Reproducibility Objective

목표는 bit-identical LLM output 재생이 아니라 당시 어떤 데이터·규칙·Evidence·Universe·가격원장·Prompt Protocol로 판단했는지 완전 복원하는 것이다.

---

# 27. Write Safety / Concurrency

Canonical을 LLM이나 작업자가 직접 수정하지 않는다.

## 27.1 Write Pipeline

```text
STAGING
  ↓
SCHEMA VALIDATION
  ↓
ID / DUPLICATE VALIDATION
  ↓
PIT CUTOFF VALIDATION
  ↓
LINEAGE VALIDATION
  ↓
AUDIT
  ↓
COMMIT / MERGE
  ↓
CANONICAL
  ↓
GENERATED VIEW REFRESH
  ↓
ACTIVE POINTER UPDATE, if release
```

## 27.2 Direct Write Prohibition

LLM은 Staging candidate를 생성할 수 있다.

Canonical 반영은 검증 pipeline을 통과해야 한다.

## 27.3 Initial Concurrency Strategy

초기에는 PostgreSQL/DB lock보다 다음을 우선한다.

- single merge path
- schema validation
- idempotency
- duplicate detection
- audit
- Git commit/merge
- release pointer

## 27.4 Atomic Release

여러 artifact를 새 release로 승격할 때:

1. 모든 신규 artifact 작성
2. 모든 validation 완료
3. 모든 hash/manifest 완료
4. regression test 완료
5. commit
6. Active Manifest update

순서를 사용한다.

## 27.5 PostgreSQL

현재 도입하지 않는다.

`LATER / NOT REQUIRED FOR v1`

---

# 28. Version Policy

| Asset Type | Version Policy |
|---|---|
| Architecture | Versioned Immutable |
| Rule | Versioned Immutable |
| Model Definition | immutable by `model_version` |
| Trigger/Weight/Component methodology change | New `model_version` |
| Snapshot Schema | `snapshot_schema_version` |
| PIT-SNAPSHOT | append-only + `snapshot_revision` |
| MODEL-SCORE Schema | explicit `score_schema_version` |
| MODEL-SCORE | same Snapshot/model + `score_revision` |
| Score Components | model-definition driven extensible child records |
| Validation | references immutable `model_score_id` |
| State History | append-only |
| Data Correction | correction-domain-specific revision |
| Universe Rule | `universe_rule_version` |
| Universe Set | immutable `universe_release_id` |
| Price | raw immutable + canonical `price_dataset_id/version` |
| Event | append-only + revision/supersession |
| Evidence | immutable claim + correction/supersession if necessary |
| Run | unique `run_id + run_mode + run_role` |
| Release | unique `release_id` |
| Git | commit history / SHA |

Git commit history만으로 business version을 대체하지 않는다.

---

# 29. Storage Roles

## 29.1 ChatGPT Project

```text
Workspace
Analysis
Bootstrap
Review
```

영구 원장 아님.

## 29.2 Git Repository — Control Plane

```text
Rules
Schemas
Manifest
Run Manifest
Audit metadata
Small structured master
Source registry metadata
Version history
Generated bootstrap index
```

## 29.3 Large Data Storage — Data Plane

```text
RAW
Price
Large Parquet
PIT partitions
Large Evidence/Event
Source documents
Legacy archive
```

## 29.4 DuckDB

역할:

- Query
- Join
- Validation
- local analytics
- Parquet access
- Generated View production

DuckDB 자체는 Canonical Source of Truth가 아니다.

## 29.5 PostgreSQL

```text
STATUS = LATER
```

v1 Architecture의 필수요소가 아니다.

---

# 30. Reference Logical Layout

```text
control-plane/
  rules/
  schemas/
  manifests/
  run-manifests/
  audits/
  small-masters/
  indexes/

data-plane/
  raw/
    sources/
    price/
    legacy/

  normalized/
    source/
    evidence/
    event/

  canonical/
    company/
      identity/
      structure-history/
      state-history/

    fab/
      identity/
      state-history/

    company-fab/
    universe-history/
    pit/
    price/

  validation/
    backtests/
    metrics/

generated/
  COMPANY-CURRENT
  FAB-CURRENT
  UNIVERSE-CURRENT
  COMPANY-FAB-CURRENT
  MODEL-SCORE-FLAT
  LLM-FLAT-VIEWS
  SEMI-MASTER-INDEX
```

Physical path는 Migration 설계에서 조정 MAY.

논리적 계층 분리는 변경하면 안 된다.

---

# 31. Migration Contract

Architecture Freeze 이후 Migration은 다음 순서를 MUST로 한다.

## Gate 1 — Legacy Freeze

Migration 대상 Legacy artifact를 먼저 Freeze한다.

원본 수정 금지.

## Gate 2 — Source Inventory

- filename
- source ID
- version
- size
- hash where possible
- status

를 기록한다.

## Gate 3 — Format Conversion Only

첫 Migration은 의미변경 없이 Format Conversion을 수행한다.

내용 Revision 필요 항목은 별도 issue/correction으로 분리한다.

## Gate 4 — Source Lineage

신규 record가 어떤 Legacy source에서 생성됐는지 추적 가능해야 한다.

## Gate 5 — Record Count

Migration 전/후 record count를 검증한다.

## Gate 6 — Required Field

Schema의 required field 충족 여부를 검사한다.

## Gate 7 — Enum Preservation

다음 등 기존 enum/value 의미를 보존한다.

- Trigger
- β
- M1~M4/S
- Evidence Class
- Evidence Status
- Refresh Code
- Fab Stage

## Gate 8 — Logical Key

Logical key uniqueness와 duplicate를 검사한다.

## Gate 9 — Hash / Audit

가능한 경우 source hash, output hash, manifest hash를 기록한다.

## Gate 10 — Audit PASS

Audit PASS 전 신규 Canonical을 ACTIVE로 승격하지 않는다.

## Gate 11 — Parallel Verification

신규 Canonical과 Legacy source를 검증기간 동안 분리 유지한다.

Legacy를 즉시 삭제하지 않는다.

## Gate 12 — Regression Test

최소 representative company/fab/historical Snapshot/Universe/PIT score/price/lineage에 대해 비교한다.

## Gate 13 — Cutover

Regression Test PASS 후에만 `active-manifest`가 신규 release를 가리키도록 변경한다.

---

# 32. Format Migration vs Content Revision

## 32.1 Format Migration

예:

```text
DOCX → YAML
CSV → Parquet
Flat Master → History records
```

목표는 동일 의미의 저장형식 변경이다.

## 32.2 Content Revision

예:

- 잘못된 customer structure 수정
- 잘못된 Fab stage 수정
- 새로운 Qualification evidence 반영
- 누락된 identity 보완

이는 Format Migration과 별도 처리한다.

## 32.3 Combined Migration Prohibition

Format Migration 중 “겸사겸사 내용을 최신화”하지 않는다.

---

# 33. LLM Retrieval / Bootstrap Architecture

Architecture Migration 완료 후 권장 retrieval 흐름:

```text
1. active-manifest
        ↓
2. SEMI-MASTER-INDEX
        ↓
3. applicable Rule / Schema
        ↓
4. Generated Current Views
        ↓
5. PIT / Historical History when required
        ↓
6. SEMI-DATA-ROUTE equivalent routing
        ↓
7. External Delta Search only when required
```

Migration 전에는 기존 Source routing을 유지한다.

---

# 34. Source / Evidence / Event / PIT / Score Lineage

Canonical lineage는 **단일 강제 직렬 경로가 아니다.**

Discrete business/state event가 존재하는 경우:

```text
RAW SOURCE
    ↓
SOURCE REGISTRY
    ↓
EVIDENCE
    ↓
EVENT
    ↓
STATE / PIT INPUT
    ↓
PIT-SNAPSHOT
    ↓
MODEL-SCORE
    ↓
VALIDATION
```

Periodic observation 또는 dataset-derived PIT input인 경우:

```text
RAW / DATASET
     ↓
SOURCE / NORMALIZED DATA
     ↓
EVIDENCE / OBSERVATION
     ↓
PIT-SNAPSHOT
     ↓
MODEL-SCORE
     ↓
VALIDATION
```

## 34.1 Reverse Audit

Snapshot:

```text
PIT-SNAPSHOT
→ Evidence / Observation / State
→ Source / Dataset
→ Raw
```

Score:

```text
MODEL-SCORE
→ PIT-SNAPSHOT
→ MODEL-DEFINITION
→ Component Definition
→ Scoring Run
```

Validation:

```text
VALIDATION
→ MODEL-SCORE
→ PIT-SNAPSHOT
→ Price Dataset
→ Validation Protocol
```

---

# 35. Audit Principles

Audit은 최소 다음을 검출할 수 있어야 한다.

- duplicate record
- broken reference
- orphan evidence
- missing source
- PIT cutoff violation
- invalid enum
- invalid logical key
- duplicate Event counting
- missing run provenance
- duplicate Canonical Run
- unauthorized Replay/Diagnostic canonicalization
- missing price dataset ID
- missing universe release
- hash mismatch
- illegal direct Canonical overwrite
- PIT-SNAPSHOT에 `model_version`이 identity field로 사용되는 경우
- PIT-SNAPSHOT에 model-specific component column이 hard-coded된 경우
- invalid `snapshot_revision`
- broken Snapshot supersession chain
- invalid `score_revision`
- score component가 해당 model definition에 없는 `component_key`를 참조하는 경우
- required score component 누락
- Total score와 model definition 산식 불일치
- `snapshot_frozen`과 `score_frozen`을 혼합한 경우
- Validation이 특정 `model_score_id`를 참조하지 않는 경우
- Replay/Diagnostic가 Snapshot 또는 Score를 자동 변경하는 경우
- PIT-SNAPSHOT business key가 `company_id + snapshot_cutoff_at`이 아닌 경우
- `snapshot_date`가 authoritative identity로 사용된 경우
- 동일 `company_id + snapshot_cutoff_at + snapshot_revision`에 둘 이상의 Canonical Snapshot이 존재하는 경우
- `Trigger Stage`, `Expectations Gap`, `Conversion Visibility`, `Market Recognition`을 PIT-SNAPSHOT의 authoritative model-independent state로 저장한 경우
- Legacy combined PIT/Score schema가 신규 Canonical object로 사용된 경우

---

# 36. Invariants

### INV-01
Current View는 Canonical보다 권위가 높을 수 없다.

### INV-02
과거 Score는 현재 Evidence로 silent overwrite할 수 없다.

### INV-03
Data Correction과 Methodology Change는 같은 version 축을 사용하지 않는다.

### INV-04
Price는 Universe membership을 결정하지 않는다.

### INV-05
Fab stage는 Company별로 복제하지 않는다.

### INV-06
하나의 경제적 Event를 Source 수만큼 중복 계산하지 않는다.

### INV-07
`valid_to` 생성을 위해 과거 Canonical row를 기본 UPDATE하지 않는다.

### INV-08
`recorded_at`을 `publication_at` 대신 PIT cutoff 판단에 사용하지 않는다.

### INV-09
Generated View를 수동 수정해 Canonical을 역변경하지 않는다.

### INV-10
Audit PASS 이전 release는 ACTIVE가 될 수 없다.

### INV-11
Event는 모든 PIT input의 필수 중간단계가 아니다.

### INV-12
`MODEL_DERIVED` Evidence를 외부 Source가 직접 진술한 FACT처럼 취급할 수 없다.

### INV-13
동일 Snapshot/model/score revision의 Canonical MODEL-SCORE에는 authoritative scoring Run이 하나만 존재한다.

### INV-14
`REPLAY`와 `DIAGNOSTIC` 실행은 Canonical PIT/Score를 자동 변경할 수 없다.

### INV-15 — PIT Model Independence
`PIT-SNAPSHOT`의 logical identity에는 `model_version`이 포함되지 않는다.

### INV-16 — One Snapshot, Many Models
하나의 PIT Snapshot은 여러 model version의 MODEL-SCORE에서 참조할 수 있다.

### INV-17 — Model Change Does Not Mutate Snapshot
새 model_version 생성은 `snapshot_revision`을 변경하지 않고 새로운 PIT Snapshot을 생성하지 않는다.

### INV-18 — Separate Revisions

```text
snapshot_revision
≠
score_revision
```

### INV-19 — Separate Freeze

```text
snapshot_frozen
≠
score_frozen
```

### INV-20 — Score Schema Extensibility
PIT Snapshot schema는 특정 model version의 component name/count/max score를 hard-code하지 않는다.

### INV-21 — Validation Evaluation Binding
Validation은 반드시 특정 MODEL-SCORE 또는 동등한 immutable Evaluation ID를 참조한다.

### INV-22 — Snapshot Knowledge Principle
PIT Snapshot에는 당시 알고 있던 정보를 저장하고 특정 모델이 그 정보를 해석한 결과를 authoritative Snapshot state로 저장하지 않는다.

### INV-23 — Snapshot Cutoff Identity
PIT-SNAPSHOT의 authoritative Business Snapshot Key는:

```text
company_id
+
snapshot_cutoff_at
```

이다.

`snapshot_date`는 convenience field다.

### INV-24 — Legacy Combined PIT Superseded
Legacy의 `PIT = State + Model + Score + Validation` 구조는 Architecture v1.0의 authoritative canonical architecture가 아니다.

### INV-25 — Observation / Interpretation Separation
PIT-SNAPSHOT에는 model-independent Observation/Evidence를 저장한다.

`Trigger Stage`, `Expectations Gap`, `Conversion Visibility`, `Market Recognition` 등은 MODEL-SCORE 또는 model-specific feature layer에 귀속한다.

### INV-26 — Model Interpretation Does Not Become Historical Fact
특정 model_version이 산출한 interpretation을 PIT-SNAPSHOT의 역사적 객관 상태로 승격할 수 없다.

---

# 37. Explicit Prohibitions

Architecture Freeze 이후 다음을 MUST NOT 한다.

- Canonical history destructive update
- frozen PIT delete
- current information backfill로 historical score silent replacement
- Provider-mixed OHLC validation
- evidence 없는 price adjustment
- Price에 Universe membership을 authoritative fact로 저장
- Fab stage를 Company Master마다 복제
- 같은 Event를 Source별 독립 수주로 중복 계산
- Trigger/β/Maturity enum의 비공식 변경
- Format Migration 중 의미 Revision
- Git commit SHA만으로 model/schema version을 대체
- LLM의 direct Canonical write
- Audit 없이 Active pointer 변경
- Generated View를 Source of Truth로 승격
- NOT_FOUND를 자동 negative fact로 변환
- 모든 periodic F3 observation에 Event 생성을 강제
- `MODEL_ASSUMPTION`을 외부 Source의 직접 FACT로 취급
- PIT logical key에 `model_version` 포함
- 모델 버전별 PIT Snapshot 복제
- PIT schema에 특정 모델 component column 고정
- Snapshot correction을 `score_revision`으로 처리
- Score correction을 `snapshot_revision`으로 처리
- Snapshot freeze와 Score freeze 통합
- Model change를 이유로 Snapshot revision 증가
- Validation을 Snapshot만 참조시키고 평가대상을 식별하지 않는 구조
- `company_id + snapshot_date`를 PIT의 최종 authoritative key로 사용하는 것
- `snapshot_date`만으로 같은 날짜의 서로 다른 cutoff Snapshot을 병합하는 것
- Legacy `company_id + snapshot_date + model_version` key를 신규 PIT-SNAPSHOT에 재사용
- Legacy combined PIT/Score row를 신규 Canonical schema로 그대로 승격
- `Trigger Stage`를 model-independent PIT Fact로 저장
- `Expectations Gap`, `Conversion Visibility`, `Market Recognition`을 Source fact처럼 Snapshot에 고정

---

# 38. Architecture Freeze Change Policy

본 문서가 FROZEN / ACTIVE Architecture Contract로 승인된 이후 Architecture 자체는 편의상 반복 개편하지 않는다.

새 Architecture version 검토 조건:

1. 현 구조로 해결할 수 없는 재현성 문제
2. 저장규모의 구조적 한계
3. 현재 single-merge/concurrency 방식의 한계
4. 신규 자산군/모델로 기존 schema 확장이 불가능
5. 신규 요구사항이 기존 Canonical 원칙과 충돌
6. 규제·보안·감사 요구로 현재 구조가 불충분

다음은 Architecture version 변경 사유가 아니다.

- 파일명 취향
- 폴더 위치 개선
- LLM용 View formatting 변경
- Query 성능을 위한 단순 partition 조정
- nullable field의 비파괴적 추가
- 문서 표현 개선

---

# 39. Approval / Activation Policy

Architecture v1.0 상태:

```text
FROZEN / ACTIVE ARCHITECTURE CONTRACT
```

Architecture Freeze 승인은 Migration 실행을 의미하지 않는다.

Migration은 별도:

1. Migration Inventory / Manifest Freeze
2. Control Plane materialization
3. Legacy Freeze / hash capture
4. Schema 설계
5. Migration Plan
6. Staging Migration
7. Audit
8. Regression
9. Cutover

순으로 진행한다.

---

# 40. Revision History

| Version | Date | Status | Change |
|---|---|---|---|
| v1.0 Candidate | 2026-08-14 | SUPERSEDED BY FINAL CANDIDATE | 최초 Architecture 설계 |
| v1.0 Final Candidate | 2026-08-14 | SUPERSEDED BY PRE-FREEZE ALIGNMENT | Normative Override, Evidence Origin, Event optionality, Run canonicalization 반영 |
| v1.0 PIT/Model-Score Decoupling | 2026-08-14 | SUPERSEDED BY PRE-FREEZE ALIGNMENT | `PIT-SNAPSHOT / MODEL-DEFINITION / MODEL-SCORE / VALIDATION` 분리 |
| v1.0 Pre-Freeze Alignment | 2026-08-14 | APPROVED FOR FREEZE | Override E, model-derived F3 귀속, `company_id + snapshot_cutoff_at` PIT key 최종 정렬 |
| **v1.0** | **2026-08-14** | **FROZEN / ACTIVE ARCHITECTURE CONTRACT** | **Architecture Freeze 완료. 규칙 변경 없음. Freeze metadata 및 Acceptance 상태만 확정.** |

---

# Appendix A. Canonical Logical-Key Matrix

| Object | Logical Identity / Key |
|---|---|
| COMPANY-IDENTITY | `company_id` |
| COMPANY-STRUCTURE-HISTORY | `structure_record_id`; entity/field revision chain |
| COMPANY-STATE-HISTORY | `state_record_id`; entity/field revision chain |
| FAB-IDENTITY | `fab_id` |
| FAB-STATE-HISTORY | `fab_state_record_id` |
| COMPANY-FAB | `company_fab_record_id` |
| SOURCE | `source_id` |
| EVIDENCE | `evidence_id` |
| EVENT logical | `event_id` |
| EVENT record | `event_record_id` |
| UNIVERSE membership | `universe_record_id` |
| UNIVERSE release | `universe_release_id` |
| **PIT-SNAPSHOT business identity** | **`company_id + snapshot_cutoff_at`** |
| **PIT-SNAPSHOT revision identity** | **`company_id + snapshot_cutoff_at + snapshot_revision`** |
| PIT-SNAPSHOT immutable identity | `pit_snapshot_id` |
| MODEL-DEFINITION | `model_version` |
| SCORE-COMPONENT-DEFINITION | `model_version + component_key` |
| MODEL-SCORE business identity | `pit_snapshot_id + model_version` |
| MODEL-SCORE revision identity | `pit_snapshot_id + model_version + score_revision` |
| MODEL-SCORE immutable identity | `model_score_id` |
| MODEL-SCORE-COMPONENT | `model_score_id + component_key` |
| VALIDATION | `validation_id`; authoritative evaluation reference=`model_score_id` |
| PRICE | dataset schema-defined date/security key |
| RUN | `run_id` |
| RELEASE | `release_id` |

다음은 PIT-SNAPSHOT authoritative key로 사용하지 않는다.

```text
company_id + snapshot_date + model_version
company_id + snapshot_date
```

---

# Appendix B. Canonical / Generated Matrix

| Data | Canonical | Generated |
|---|---:|---:|
| Rule versions | YES | NO |
| Schema versions | YES | NO |
| Source Registry | YES | flat locator view 가능 |
| Evidence | YES | Evidence summary 가능 |
| Event History | YES | Event current/summary 가능 |
| Company Identity | YES | Company flat 가능 |
| Company Structure History | YES | COMPANY-CURRENT |
| Company State History | YES | COMPANY-CURRENT |
| Fab State History | YES | FAB-CURRENT |
| Company-Fab History | YES | COMPANY-FAB-CURRENT |
| Universe Membership History | YES | UNIVERSE-CURRENT |
| PIT-SNAPSHOT | YES | Snapshot convenience view |
| MODEL-DEFINITION | YES | model summary 가능 |
| MODEL-SCORE | YES | MODEL-SCORE-LATEST |
| MODEL-SCORE-COMPONENT | YES | MODEL-SCORE-FLAT |
| VALIDATION | YES | validation summary |
| Price | YES | filtered validation view |
| Run Manifest | YES | run summary |
| MASTER INDEX | NO | YES |
| LLM flat view | NO | YES |

---

# Appendix C. State Derivation Rule

Canonical Historical row에 `valid_to`를 직접 UPDATE하지 않고 Generated SCD View에서 파생한다.

---

# Appendix D. PIT Cutoff Example

```text
Snapshot Date:
2025-08-13

Snapshot Cutoff:
2025-08-13T23:59:59+09:00

Evidence A:
2025-08-13T18:00:00+09:00
→ Eligible

Evidence B:
2025-08-14T08:00:00+09:00
→ NOT eligible for 2025-08-13 Snapshot/Score input

Entry:
2025-08-14 Open
```

Evidence B가 Entry 이전에 공개됐더라도 이전 Snapshot Score에는 사용하지 않는다.

동일 PIT-SNAPSHOT은 여러 모델이 재사용할 수 있다.

---

# Appendix E. Correction Examples

## E.1 Snapshot Correction

```text
SNAP-001
company_id = X
snapshot_cutoff_at = 2025-08-13T23:59:59+09:00
snapshot_revision = 0
```

Evidence 연결 오류 발견:

```text
SNAP-002
company_id = X
snapshot_cutoff_at = 2025-08-13T23:59:59+09:00
snapshot_revision = 1
supersedes_ref = SNAP-001
```

## E.2 Score Correction

```text
SCORE-001
pit_snapshot_id = SNAP-001
model_version = 3M-v0.1
score_revision = 0
```

scoring implementation 오류:

```text
SCORE-002
pit_snapshot_id = SNAP-001
model_version = 3M-v0.1
score_revision = 1
supersedes_ref = SCORE-001
```

## E.3 Model Change

```text
SCORE-003
pit_snapshot_id = SNAP-001
model_version = 3M-v0.2
score_revision = 0
```

Snapshot은 변경되지 않는다.

---

# Appendix F. Run Canonicalization Example

```text
RUN-001
run_mode = HISTORICAL_RECONSTRUCTION
run_role = SNAPSHOT_CAPTURE
output = SNAP-001
canonical = TRUE
```

```text
RUN-002
run_mode = HISTORICAL_RECONSTRUCTION
run_role = MODEL_SCORING
input = SNAP-001
model_version = 3M-v0.1
output = SCORE-001
canonical = TRUE
```

```text
RUN-003
run_mode = HISTORICAL_RECONSTRUCTION
run_role = MODEL_SCORING
input = SNAP-001
model_version = 3M-v0.2
output = SCORE-002
canonical = TRUE
```

```text
RUN-004
run_mode = REPLAY
run_role = MODEL_SCORING
input = SNAP-001
model_version = 3M-v0.1
canonical = FALSE
```

Replay 결과는 SNAP-001 또는 기존 Canonical Score를 자동 변경하지 않는다.

---

# Appendix G. Release Safety

정상 release:

```text
STAGING
→ validate
→ audit PASS
→ regression PASS
→ commit
→ immutable release
→ active-manifest pointer update
→ generated views refresh
```

실패:

```text
STAGING
→ audit FAIL
→ NO CUTOVER
→ current active release unchanged
```

---

# FREEZE ACCEPTANCE CHECKLIST — FINAL

| Item | Final Status |
|---|---|
| Normative Override | **PASS** |
| Override E / Legacy Combined PIT Supersession | **PASS** |
| Canonical / View Separation | **PASS** |
| PIT / Score Separation | **PASS** |
| PIT Model Independence | **PASS** |
| PIT Authoritative Key = `company_id + snapshot_cutoff_at` | **PASS** |
| Snapshot Revision | **PASS** |
| Score Revision | **PASS** |
| Snapshot Freeze | **PASS** |
| Score Freeze | **PASS** |
| Multi-model Evaluation | **PASS** |
| Model Definition | **PASS** |
| Extensible Score Components | **PASS** |
| F3 Observation / Interpretation Separation | **PASS** |
| Evidence Origin | **PASS** |
| Event Optionality | **PASS** |
| Event Identity / Idempotency | **PASS** |
| Company / Fab History | **PASS** |
| valid_to Derived | **PASS** |
| Universe 3-Layer | **PASS** |
| Price Eligibility Separation | **PASS** |
| PIT Cutoff | **PASS** |
| Validation Binding | **PASS** |
| Run Mode | **PASS** |
| Run Role | **PASS** |
| Canonical Run | **PASS** |
| Replay Isolation | **PASS** |
| Active Manifest Contract | **PASS** |
| Schema Registry Contract | **PASS** |
| Run Manifest Contract | **PASS** |
| Raw / Normalized / Derived | **PASS** |
| Write Safety | **PASS** |
| Migration Gate | **PASS** |

## Freeze Decision

```text
[X] APPROVE — SEMI-ARCHITECTURE-SPEC v1.0 Architecture Contract FREEZE
[ ] REVIEW
[ ] REJECT
```

**ARCHITECTURE FREEZE: COMPLETE**

**ARCHITECTURE v1.0: FROZEN / ACTIVE ARCHITECTURE**

**ACTUAL DATA MIGRATION: NOT PERFORMED**

**CANONICAL CUTOVER: NOT PERFORMED**
