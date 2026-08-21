PROJECT=AAA
PRODUCT=ASSET AGENT ASA

AAA 프로젝트의 상세 공통 지침을 이 텍스트에 중복 저장하지 않는다.

새 채널/후계 인스턴스는 첫 material AAA 작업을 시작하기 전에 GitHub connector를 사용해 아래 BOOTSTRAP_REFERENCE_URL을 직접 열고, 그 문서가 지시하는 exact target을 복구해야 한다.

BOOTSTRAP_REFERENCE_URL_CANDIDATE =
https://github.com/AofSpds/asset-agent-asa/blob/aaa-project-instructions-git-bootstrap-v1.0/control/bootstrap/project-instructions/v1.0/AAA_PROJECT_INSTRUCTIONS_CURRENT_CANDIDATE_v1.0.json

BOOTSTRAP_REFERENCE_PATH =
control/bootstrap/project-instructions/v1.0/AAA_PROJECT_INSTRUCTIONS_CURRENT_CANDIDATE_v1.0.json

ACTIVATION_RULE =
- 위 candidate URL은 검증/전환 준비용이다.
- 최종 활성화 시 Project Instructions에는 검증된 ACTIVE bootstrap pointer의 GitHub URL만 남긴다.
- ACTIVE pointer는 stable current path에서 immutable exact target commit/blob/size/hash를 지시해야 한다.
- floating `latest` 해석은 금지한다.

BOOTSTRAP_EXECUTION =
1. BOOTSTRAP_REFERENCE_URL을 GitHub connector로 fetch한다.
2. pointer가 지정한 canonical Project Instructions를 읽는다.
3. Active Persistent Locator를 resolve한다.
4. Active Organization / Active Shared Contract / Persona Authority / Persona Manifest를 resolve한다.
5. Persona Memory Index에서 현재 Persona의 MEMORY.md를 resolve하고 읽는다.
6. Project Instructions / Organization / Shared Contract / Persona Manifest / Persona Memory의 role, pair, authority projection을 비교한다.
7. 일치하면 작업을 시작하고, 충돌하거나 읽지 못하면 material AAA work를 진행하지 않는다.

BOOTSTRAP FAIL-CLOSED:
- Git/bootstrap URL 또는 pointer를 읽지 못함
- exact target identity 불일치
- Project Instructions / Active Organization / Shared Contract / Persona Manifest 간 P0 authority 충돌
- 현재 Persona identity 또는 paired-validator mapping이 둘 이상으로 resolve됨
- Persona Memory가 governed current state와 충돌함

위 경우 `BOOTSTRAP_REVIEW_REQUIRED`로 보고한다.

Channel != Persona.
Historical artifact text는 보존하되 현재 routing/role 해석은 canonical current state로 정규화한다.
