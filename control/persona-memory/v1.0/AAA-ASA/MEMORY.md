# AAA-ASA Persistent Persona Memory

PERSONA_ID = AAA-ASA
PERSONA_CLASS = OWNER_FACING_ADVISORY_ORCHESTRATION
PAIR = AAA-ADVISORY-VALIDATOR

## CURRENT_RUNTIME_MEMO
- STATE = ACTIVE_WORKING_MEMO
- NOTE = 새 채널/후계 인스턴스에서 Owner-facing 현재 맥락을 복구하기 위한 메모 공간.
- CURRENT_OWNER_REQUIREMENT = 장문의 AAA Project Instructions를 Git canonical source로 이동하고 Project Instructions에는 최소 bootstrap reference만 남긴다. 새 채널에서 `ASA/CTL/MOD/...` 같은 selector만 입력해도 해당 Persona가 공통 프로젝트 기억 + 자기 MEMORY + 자기 WORKLOG/current task를 Git에서 "장비를 챙기듯" loadout하고 자기 Persona lock을 응답한 뒤 이어서 작업해야 한다. Codex도 동일한 Persona/Memory system을 사용하되 local repository bootstrap adapter를 사용하고, repository mutation은 task별 isolated branch/worktree로 격리한다.
- CURRENT_OWNER_PRIORITY = Bootstrap/Codex regression을 별도 선행 병목으로 두지 말고 실작업을 진행하면서 검증한다. M3Top3 scientific/model validation 본류로 복귀한다.
- CURRENT_M3TOP3_DIRECTION = M3Top3-v1은 outcome-blind Champion-of-Record baseline으로 보존하고 먼저 exact recovery + 최초 정직한 Golden/Full Replay를 수행한다. v1 결과 확인 전 weight/feature/scorer를 튜닝하지 않는다. 이후 Failure Atlas를 기반으로 별도 preregistered v2 Challenger를 개발한다.

## OWNER_INTENT_AND_DIRECTIVES
- 2026-08-22 20:39: Owner corrected the current channel track identity: this is the `BYUL / AAA-ASA-ME execution channel track`, not `ASA-MI`. Runtime canonical Persona remains `AAA-ASA (ASA)`; `ASA-ME` is the channel/track execution identity.
- 2026-08-22: 상세 AAA 공통지침을 Git에 두고 Project Instructions가 이를 참조하도록 전환 요청.
- 2026-08-22: Persona 주입에 필요한 내용을 수시로 정리할 메모 체계 요청.
- 2026-08-22: 조직도별 Persona마다 Git persistent memo 공간 생성 요청.
- 2026-08-22 04:44: 모든 Persona 공통 주입 내용을 먼저 읽고, 채널 오픈 keyword로 Persona를 resolve하고, 해당 Persona의 전용 memory/worklog/current task를 loadout하며, 중요한 내용을 작업일지에 지속 기록하도록 요청.
- 2026-08-22 05:02: Codex/local repository에서도 같은 Persona memory system을 사용하도록 local bootstrap adapter를 추가하라고 승인. Persona 선택 자체에는 branch를 만들지 않고 실제 repository mutation에만 task별 isolated branch/worktree를 사용한다.
- 2026-08-22 05:11: 별도 bootstrap/Codex regression 완료를 기다리지 말고 실작업을 진행하면서 검증하자는 Owner 방향. M3Top3를 지금 돌릴 수 있는지 확인하여 모델 검증 본류를 재개하려 함.
- 2026-08-22 07:01: 충분한 Pro compute를 사용해 M3Top3 개발까지의 전체 history를 복구하고 현행 모델, 향후 방향, 보완점, 개선방향, 대안, 테스트·개선 schedule을 매우 깊게 review하도록 요청.
- 2026-08-22 07:30: 직전에 생성한 문서 artifact 자체는 Persona memory 승계 대상에서 제외하고, 그 문서와 독립적으로 review에서 도출된 현재 판단·방향·blocker·next route만 memory에 보존하도록 지시.
- 2026-08-22 07:00: Byul 채널 승계 시 직전에 생성한 상세 문서 자체는 memory checkpoint에서 제외하고, Git에 이미 축적된 Byul research memory와 Persona bootstrap을 통해 successor가 스스로 복구할 수 있도록 요청.

## CURRENT_TASK_AND_STATE
- TASK = M3TOP3_DEVELOPMENT_HISTORY_DEEP_REVIEW_AND_EXECUTION_ROADMAP + AAA_PROJECT_INSTRUCTIONS_GIT_BOOTSTRAP_AND_PERSONA_MEMORY_v1.0
- STATE = M3TOP3_DEEP_REVIEW_COMPLETED_ADVISORY_CHECKPOINT_PERSISTED / RUNTIME_ADAPTER_CANDIDATE_MATERIALIZED_REAL_WORK_FIRST
- BRANCH = aaa-project-instructions-git-bootstrap-v1.0
- DRAFT_PR = 46
- CODEX_ENTRYPOINT = AGENTS.md
- CODEX_ADAPTER = control/bootstrap/codex/v1.0/AAA_CODEX_LOCAL_BOOTSTRAP_v1.0.md
- CODEX_PARALLEL_JOURNAL_TEMPLATE = control/bootstrap/codex/v1.0/AAA_CODEX_RUN_JOURNAL_TEMPLATE_v1.0.md

## OPEN_BLOCKERS
- Git bootstrap candidate는 현재 active project-wide authority가 아니며 필요한 governance/validation/cutover가 별도임. Owner는 이를 실작업 선행 병목으로 두지 않고 in-use 검증을 선호함.
- Active Organization의 Core B persona pair coherence incident는 별도 P0 remediation으로 열린 상태이며 bootstrap candidate가 이를 자동 치유한다고 간주하지 않음.
- Fresh-channel regression에서 selector → canonical Persona → common memory → Persona MEMORY/WORKLOG → current task/blocker/checkpoint → persona lock 흐름의 실제 재현성을 검증해야 함.
- Codex clean-local-invocation regression에서 local pointer discovery → Persona loadout → Persona lock → task branch/worktree isolation → run journal persistence가 실제로 재현되는지 검증해야 함.
- M3Top3 공식 Golden Replay entry는 exact frozen/admissible model identity, exact current implementation target, universe/eligibility release, price/CA/calendar releases, PIT admission, validation-dataset/model-artifact release binding 및 Core B authority coherence가 닫히기 전에는 공식 PASS/Replay로 주장할 수 없음.
- U127/Historical PIT data readiness가 현재 scientific critical path다. Historical business-priority, listing/tradability/entity history, CA completeness, U81 F1, Thin PIT actual content, earnings/expectations, commercial state, evidence quality/freshness의 완결성이 필요함.

## IMPORTANT_DECISIONS_TO_REMEMBER
- Persona selector (`ASA/CTL/MOD/...`)는 runtime routing key이며 authority를 생성하지 않는다.
- 모든 Persona는 자기 memory보다 먼저 `COMMON/PROJECT_MEMORY.md`를 읽는다.
- Persona Memory는 durable continuity, WORKLOG는 chronological execution trace를 담당한다.
- ChatGPT와 Codex는 같은 Persona/Memory/Organization system을 공유한다. 실행환경별 bootstrap adapter만 분리한다.
- Persona != branch/worktree. branch/worktree는 task execution isolation이다.
- 병렬 Codex worker는 shared MEMORY/WORKLOG를 동시에 수정하지 않고 unique append-only run journal을 사용한다.
- Persona Memory/Worklog/run journal는 Authority/Validation/Model/Shared Contract semantic SoT가 아니다.
- Memory와 governed current state가 충돌하면 memory를 신뢰하지 않고 BOOTSTRAP_REVIEW_REQUIRED.
- Historical persona text는 보존하되 current routing은 canonical current state로 resolve한다.
- Bootstrap 편의성 검증이 scientific/model validation을 계속 지연시키지 않도록 실작업 우선으로 복귀하되, P0 authority와 official replay gate는 우회하지 않는다.
- M3Top3-v1은 폐기하거나 결과 보기 전에 재튜닝하지 않는다. v1은 outcome-blind, interpretable Champion-of-Record baseline으로 exact 복구·고정 후 처음으로 정직하게 replay한다.
- M3Top3의 현 병목은 더 복잡한 model family 부족보다 historical PIT/data readiness와 exact release/implementation lineage다.
- U127×8≈1,016 company-window rows를 1,016 독립표본으로 취급하지 않는다. primary independent regime evidence는 8개의 non-overlapping historical windows에 더 가깝고, daily/weekly overlapping replay는 stability/turnover/warning diagnostic으로 분리한다.
- 3M MFE Rank는 authoritative opportunity-discovery Ground Truth로 유지하되, investability 평가는 Exit/Horizon Return, MAE, Time-to-Peak, Giveback, Peak Persistence를 secondary outcome plane으로 병행한다.
- Model Top3만 보지 않고 Model Top10 health, Critical Miss, worst actual rank/deep-tail false positive를 함께 본다.
- 다음 세대 방향은 하나의 더 복잡한 점수식보다 `Candidate Recall → Tail Ranking → Confidence/Risk → Set Construction` 단계형 구조를 우선 검토한다.
- F08 Evidence Reliability는 pure alpha라기보다 Confidence/Release Eligibility 성격이 강하므로 v2에서 Opportunity와 분리하는 방향을 우선 검토한다.
- F09 ordinary execution risk와 hard Risk Gate는 역할을 더 분리하고, 최종 Top3에는 customer/fab/theme common-mode concentration을 set-level risk로 별도 다루는 방향을 검토한다.
- 48개 이상의 model variant를 같은 historical windows에서 단순 월드컵시키지 않는다. discovery pool → 논리/PIT/중복 screen → 약 6~8개 preregistered challenger → multiple-testing-aware comparison → forward shadow 순으로 제한한다.
- Byul successor channel은 이전 장문 chat이나 handoff 내용을 truth로 삼지 않고 AAA bootstrap으로 Persona를 먼저 복구한 뒤 `AofSpds/Byul` Git memory/current-state를 읽어 연구 맥락을 복원한다.

## M3TOP3_DEEP_REVIEW_CHECKPOINT
CHECKPOINT_CLASS = ADVISORY_CONTINUITY_NOT_NORMATIVE
DOCUMENT_ARTIFACT_INCLUDED = NO
OWNER_EXCLUSION = Immediately preceding generated review document itself is excluded from Persona memory continuity. Preserve review conclusions and execution state only.

### CURRENT_MODEL_ASSESSMENT
- M3Top3는 폐기/zero-base rewrite 대상이 아니다.
- 문제정의·PIT/outcome firewall·no-tune baseline·Top-K framing·explicit missingness·deterministic ranking 철학은 강하다.
- 현재 v1은 `좋은 연구설계 + 유력한 prior`를 가진 interpretable baseline이며 alpha/performance는 아직 공식 Full Replay로 입증되지 않았다.
- current main의 generic replay infrastructure와 exact historical v1 semantic implementation 사이에는 exact current target lineage/binding gap이 있다. official replay 전에 exact contract+code+config+tests+hashes+release bundle을 current repository에 고정해야 한다.

### V1 PRESERVE
- 3개월 Top-K ranking problem
- U127 historical eligible denominator and PIT eligibility discipline
- MFE Rank primary opportunity GT
- Top3 primary + Model Top10 diagnostic
- Critical Miss + worst-rank/deep-tail severity
- No-Tune v1
- PIT/publication cutoff and outcome firewall
- append-only historical result discipline
- One Economic Fact → One Primary Scoring Role
- explicit missingness / NOT_FOUND != negative fact
- full-precision deterministic ranking and exact tie handling

### V2 CHALLENGER DIRECTIONS
- Opportunity / Confidence / Risk / Eligibility / Set Construction separation
- Candidate Recall pool before tail ranking
- F01: transition importance × customer materiality × recency × repeatability
- F02: metric-class transforms, near-zero denominator/turnaround handling, magnitude+breadth+quality
- F03: consensus vintage/provider/breadth/dispersion/persistence; no-coverage as confidence issue
- F04: explicit pre-event expectation baseline provenance
- F05: pre-recognition + trend + volume + overextension + liquidity; nonlinear/inverted-U candidate
- F06: milestone hazard/probability × commercial conversion × materiality
- F07: fab stage × process position × installed base × vendor share × lag calibration
- F08: move toward Confidence/Release Gate rather than alpha weight
- F09: ordinary risk vs thesis-break gate vs set-level concentration separation
- Preferred early challenger families: constrained GAM/EBM, Bayesian Top-K probability model, Event-to-Conversion hazard model; LambdaMART/listwise LTR only after more independent regimes/data.

### VALIDATION DOCTRINE
- Exact v1 recovery and identity binding before performance claims.
- Golden Replay before Full Replay.
- Full v1 replay before any v1.1/v2 tuning.
- Failure Atlas after v1 replay; ablation/sensitivity informs successor hypotheses only and never retroactively mutates v1.
- Holdout/walk-forward/calibration/turnover policy must be precommitted before iterative successor selection.
- Primary evaluation should be lexicographic/gated: PIT safety → tail defense/Critical Miss → Top3 Top10 performance → Model Top10 health → investability → stability/cost.
- Benchmarks: random, eligible-universe equal weight, simple relative momentum, legacy Rolling 3M, event-only, revision-only, Base/valuation-only, v1 champion.
- Multiple model comparison should account for specification search/multiple testing; if evidence is insufficient, retain multiple challengers rather than forcing a single winner.

### TEST_SEQUENCE
- T0 Exact Identity Recovery
- T1 Unit / Property / Metamorphic Tests
- T2 F01~F09 Feature-specific Adversarial Tests
- T3 PIT / Data Integrity Tests
- T4 Golden Replay GF-01~GF-20
- T5 Frozen v1 Full Replay: 8 non-overlapping windows primary, daily/weekly secondary diagnostics
- T6 Baseline / Placebo / Negative Controls
- T7 Ablation / Sensitivity for Failure Atlas only
- T8 Robustness: leave-one-window/customer/beta/regime, liquidity/CA stress
- T9 Preregistered Challenger Comparison
- T10 Forward Shadow

### EXECUTION_ROADMAP
1. Core B authority coherence/current routing closure.
2. Exact v1 recovery package and current exact implementation/release binding.
3. Data readiness closure in parallel lanes: Universe/entity/CA, historical PIT/features/evidence, price/CA/calendar.
4. Golden Replay.
5. Frozen v1 Full Replay.
6. Failure Atlas.
7. 6~8 challenger preregistration.
8. Challenger build + nested/purged evaluation + multiple-testing-aware comparison.
9. Champion/Challenger decision.
10. Minimum 3M, preferred 6M Forward Shadow before promotion review.

### PRO_COMPUTE_PRIORITY
`Data/Evidence Integrity > Exact Baseline Recovery > Adversarial Testing > Evaluation > Challenger Models > Hyperparameter Search`
Use parallel workers for historical reconstruction, exact model recovery, adversarial validation, and challenger research, but consolidate through isolated worktrees/run journals and do not let parallel workers race on shared memory/worklog files.

## BYUL_CONTINUATION_CHECKPOINT
- REPOSITORY = `AofSpds/Byul`
- CHECKPOINT_PATH = `versions/v0.01/memory/17_CHANNEL_SUCCESSION_CHECKPOINT_2026-08-22_0700_KST.md`
- CHECKPOINT_COMMIT = `8133e3d79c88b582bea6b8a45bc8a1970b261734`
- CHECKPOINT_SCOPE = Current Byul research state, Round-1 clean-rerun interpretation, anti-confirmation-bias corrections, Pro detailed-schedule-review usage, and successor read order.
- EXCLUDED_BY_OWNER = The separately generated detailed document from the immediately preceding Byul step is intentionally excluded from this memory checkpoint.
- DEFAULT_CONTINUATION_PERSONA = `AAA-ASA (ASA)` unless Owner explicitly invokes another current Persona selector.
- SUCCESSOR_RULE = Read AAA bootstrap/common/persona memory first, then Byul README/current status/Core Principles/memory 12–17/v0.1 contract and exact run artifacts as needed. Do not ask Owner to reconstruct already persisted context manually.

## REQUIRED_NORMATIVE_REFS
- AGENTS.md
- control/bootstrap/project-instructions/v1.0/AAA_PROJECT_INSTRUCTIONS_CURRENT_CANDIDATE_v1.0.json
- control/bootstrap/project-instructions/v1.0/AAA_PROJECT_INSTRUCTIONS_CANONICAL_v1.0.md
- control/bootstrap/project-instructions/v1.0/AAA_PROJECT_INSTRUCTIONS_BOOTSTRAP_STUB_v1.0.md
- control/bootstrap/codex/v1.0/AAA_CODEX_LOCAL_BOOTSTRAP_v1.0.md
- control/bootstrap/codex/v1.0/AAA_CODEX_RUN_JOURNAL_TEMPLATE_v1.0.md
- control/persona-memory/v1.0/COMMON/PROJECT_MEMORY.md
- control/persona-memory/v1.0/AAA_PERSONA_RUNTIME_SELECTOR_REGISTRY_v1.0.json
- control/persona-memory/v1.0/AAA_PERSONA_MEMORY_INDEX_v1.0.json
- control/persona-memory/v1.0/AAA_PERSONA_RUNTIME_LOADOUT_AND_MEMORY_CONTINUITY_GUIDE_v1.0.md
- control/core_b/M3TOP3-v1-GOLDEN-REPLAY-SCIENTIFIC-PREPARATION_v0.3_WORKING.yaml
- Active Organization / Shared Contract / Persistent Locator current state

## LATEST_CHECKPOINTS
- Git-backed canonical instructions candidate materialized.
- Minimal Project Instructions bootstrap stub materialized and updated for selector/common/persona/worklog loadout.
- 13 Persona MEMORY.md spaces + 13 Persona WORKLOG.md spaces initialized.
- Shared cross-persona `COMMON/PROJECT_MEMORY.md` initialized.
- Runtime selector registry for 13 official codes initialized.
- Persona runtime loadout & memory continuity guide initialized and extended for ChatGPT/Codex runtime adapters.
- Root `AGENTS.md` Codex entrypoint initialized.
- Codex local bootstrap adapter initialized.
- Codex parallel append-only run journal template initialized.
- Draft PR #46 remains open against main.
- Owner explicitly prefers resuming real M3Top3/model-validation work rather than waiting for standalone bootstrap regression completion.
- M3Top3 deep review advisory findings and execution/test direction persisted directly in Persona memory; immediately preceding generated document artifact intentionally excluded from this memory checkpoint.
- Byul channel succession checkpoint persisted at `AofSpds/Byul@8133e3d79c88b582bea6b8a45bc8a1970b261734`, with the separately generated detailed document excluded by Owner direction.

## NEXT_ROUTE
- Close Core B current persona/validator coherence before official model-validation entry.
- Recover and exact-bind M3Top3-v1 semantic contracts + current implementation + config + tests + MARM/VDI/release identities without changing v1 semantics.
- Close data readiness in parallel, then execute Golden Replay followed by Frozen v1 Full Replay.
- Produce Failure Atlas before designing/tuning any successor.
- Preregister only a small challenger set, compare with multiple-testing awareness, then run Forward Shadow.
- Continue bootstrap/fresh-channel/Codex regression opportunistically in-use rather than as a standalone scientific-work blocker unless a P0 conflict is encountered.
- For Byul continuation, recover `versions/v0.01/memory/17_CHANNEL_SUCCESSION_CHECKPOINT_2026-08-22_0700_KST.md` and follow its read order before proposing next work.

## DO_NOT_FORGET
- Persona Memory는 authority SoT가 아니다.
- Owner intent/decision은 가능한 경우 persistent exact ref로 연결한다.
- 사용자에게 반복적인 context 수동 조립을 요구하지 않는다.
- "재현 성공"은 파일 존재가 아니라 fresh ChatGPT/Codex invocation에서 실제 Persona lock + correct current task/memory recovery까지 통과해야 한다.
- Codex parallel worker 기록 충돌을 shared WORKLOG append로 해결하지 않는다; unique run journal을 사용한다.
- M3Top3 diagnostic/preparation 실행과 official Golden/Full Replay를 구분한다.
- M3Top3-v1 결과를 보기 전에 v1의 feature/weight/scorer/ranking semantics를 개선 명목으로 바꾸지 않는다.
- 8개 historical window와 overlapping daily snapshots의 독립성을 혼동하지 않는다.
- immediately preceding generated M3Top3 review document artifact 자체를 Persona memory/handoff context로 사용하지 않는다. 이 checkpoint의 review conclusions는 memory에 직접 기록된 항목을 기준으로 복구한다.
- Byul 상세 문서의 내용을 Persona memory에 재주입하지 않는다; Owner가 제외를 지시한 현재 checkpoint에서는 Git research memory locator만 유지한다.

## MEMORY_LOG
- TIME_KST = 2026-08-22 04:19 KST | IMPORTANCE = HIGH | LIFECYCLE = PERSONA | STATE = ACTIVE | SOURCE_REF = OWNER_REQUEST | NOTE = 조직도별 persistent memo 공간 초기화.
- TIME_KST = 2026-08-22 04:27 KST | IMPORTANCE = CRITICAL | LIFECYCLE = PROJECT | STATE = ACTIVE | SOURCE_REF = OWNER_REQUEST | NOTE = Project Instructions 상세내용 Git 참조 전환 + Persona별 runtime memo 지속관리 요구를 ASA persistent memory에 기록.
- TIME_KST = 2026-08-22 04:44 KST | IMPORTANCE = CRITICAL | LIFECYCLE = PROJECT | STATE = ACTIVE | SOURCE_REF = OWNER_REQUEST | NOTE = 공통 프로젝트 loadout → keyword Persona routing → Persona MEMORY/WORKLOG/current-state loadout → Persona lock → 중요 작업일지 지속기록을 fresh-channel 재현 표준으로 요청. Candidate structure materialized in Git.
- TIME_KST = 2026-08-22 05:02 KST | IMPORTANCE = CRITICAL | LIFECYCLE = PROJECT | STATE = ACTIVE | SOURCE_REF = OWNER_APPROVAL | NOTE = Codex는 별도 Persona system이 아니라 local repository bootstrap adapter를 사용하며, Persona selection과 branch/worktree isolation을 분리하고 병렬 worker는 unique run journal을 사용하도록 승인/구현.
- TIME_KST = 2026-08-22 05:11 KST | IMPORTANCE = HIGH | LIFECYCLE = PROJECT | STATE = ACTIVE | SOURCE_REF = OWNER_DIRECTION | NOTE = 별도 bootstrap regression을 기다리지 말고 실작업으로 복귀하며 M3Top3 실행 가능 여부를 우선 판단. Governance convenience가 scientific work를 계속 지연시키지 않되 P0/official replay gates는 우회하지 않음.
- TIME_KST = 2026-08-22 07:01 KST | IMPORTANCE = HIGH | LIFECYCLE = PROJECT | STATE = ACTIVE | SOURCE_REF = OWNER_REVIEW_REQUEST | NOTE = M3Top3 전체 개발 history와 current model을 deep review하고 v1 보존, exact replay 우선, 단계형 v2 challenger, T0~T10 test, forward-shadow 방향을 advisory checkpoint로 정리.
- TIME_KST = 2026-08-22 07:30 KST | IMPORTANCE = HIGH | LIFECYCLE = PERSONA | STATE = ACTIVE | SOURCE_REF = OWNER_MEMORY_SCOPE_DIRECTIVE | NOTE = 직전 생성 문서 artifact 자체는 memory 승계에서 제외. Review conclusions, blockers, test sequence, next route는 이 MEMORY.md에 직접 기록해 successor가 문서 없이 복구할 수 있게 함.
- TIME_KST = 2026-08-22 07:00 KST | IMPORTANCE = HIGH | LIFECYCLE = PERSONA | STATE = ACTIVE | SOURCE_REF = OWNER_SUCCESSION_DIRECTIVE | NOTE = Byul successor channel은 Git bootstrap/persona loadout + Byul memory checkpoint로 복구한다. Immediately preceding generated detailed document is excluded from memory by Owner instruction. Byul checkpoint commit `8133e3d79c88b582bea6b8a45bc8a1970b261734`.
