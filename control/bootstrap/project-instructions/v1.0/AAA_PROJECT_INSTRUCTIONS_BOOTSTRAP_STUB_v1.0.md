PROJECT=AAA
PRODUCT=ASSET AGENT ASA

AAA 프로젝트의 상세 공통 지침을 이 텍스트에 중복 저장하지 않는다.

새 채널/후계 인스턴스는 작업 시작 전에 GitHub repository `AofSpds/asset-agent-asa`의 다음 bootstrap pointer를 읽고 exact target을 복구해야 한다:

`control/bootstrap/project-instructions/v1.0/AAA_PROJECT_INSTRUCTIONS_CURRENT_CANDIDATE_v1.0.json`

그 pointer가 지시하는 canonical project instructions와 persona runtime memo/current-state를 우선 적용한다.

BOOTSTRAP FAIL-CLOSED:
- Git/bootstrap pointer를 읽지 못함
- exact target identity 불일치
- Project Instructions / Active Organization / Shared Contract / Persona Manifest 간 P0 authority 충돌
- 현재 Persona identity 또는 paired-validator mapping이 둘 이상으로 resolve됨

위 경우 material AAA work를 진행하지 말고 `BOOTSTRAP_REVIEW_REQUIRED`로 보고한다.

Channel != Persona.
Historical artifact text는 보존하되 현재 routing/role 해석은 canonical current state로 정규화한다.
