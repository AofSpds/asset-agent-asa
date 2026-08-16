from __future__ import annotations

from http.client import HTTPConnection
import json
from pathlib import Path
import shutil
import sys
import tempfile
import threading
import unittest

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "aaa" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aaa.api.operating_structure import build_operating_structure
from aaa.api.server import build_server


class OperatingStructureProjectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = Path(tempfile.mkdtemp(prefix="aaa-structure-"))
        self.continuity = self.temp / "control" / "continuity" / "v1.0"
        self.aaa_v01 = self.temp / "control" / "aaa" / "v0.1"
        self.aaa_architecture = self.temp / "control" / "aaa" / "architecture"
        self.aaa_runs = self.temp / "control" / "aaa" / "runs"
        for path in (self.continuity, self.aaa_v01, self.aaa_architecture, self.aaa_runs):
            path.mkdir(parents=True, exist_ok=True)
        self._write_baseline()

    def tearDown(self) -> None:
        shutil.rmtree(self.temp)

    def _write(self, path: Path, content: str) -> None:
        path.write_text(content, encoding="utf-8")

    def _write_baseline(self) -> None:
        self._write(
            self.continuity / "SEMI-ORG-MAP_v0.2_WORKING.yaml",
            """org_map_id: SEMI-ORG-MAP
version: v0.2_WORKING
status: OWNER_ACCEPTED
as_of: '2026-08-17T01:00:00+09:00'
project_owner:
  role_id: USER_PROJECT_OWNER
formal:
  a: SEMI-CONTROL-ARCHITECT
  b: SEMI-MODEL-VALIDATION-DESIGN-ARCHITECT
  r: SEMI-RESEARCH-ORCHESTRATOR
  v: SEMI-VALIDATION-AUDITOR
""",
        )
        self._write(
            self.continuity / "SEMI-CURRENT-STATE_v1.9.yaml",
            """state_id: SEMI-CURRENT-STATE
version: v1.9
status: WORKING
as_of: '2026-08-17T01:00:00+09:00'
model_v1:
  model_version: M3TOP3-v1.0
  baseline_source_commit: 1111111111111111111111111111111111111111
  independent_preflight:
    status: PASS
validation_channel:
  next_validation: DELTA_PREFLIGHT
""",
        )
        self._write_channel_registry("v1.4", core_a_active=False, validation_active=True)
        self._write(
            self.aaa_v01 / "AAA-PROCESS-GATE-STATUS_v0.32_WORKING.yaml",
            """control_id: AAA-PROCESS-GATE-STATUS
version: v0.32_WORKING
recorded_at: '2026-08-17T01:00:00+09:00'
current_position:
  current_controlled_activity: AAA_V1_MANAGED_POSTGRESQL_SHADOW_ENTRY_QUALIFICATION_PREPARATION
  validated_successor_target: 8a4aea0256bc630385bd463fc8969e5c88a74102
  independent_revalidation_state: COMPLETED_PASS
roadmap:
  stage_0_completed: true
  current_stage: STAGE_1
  current_gate: GATE_A_SHADOW_ENTRY
  current_state: READY_NOT_DISPATCHED
operational_authority:
  json_registry_operational_authority_during_shadow: true
  postgresql_authoritative: false
  bounded_shadow_execution_authorized: false
  live_execution_authorized: false
  postgresql_operational_sot_authorized: false
  production_canonical_promotion_authorized: false
  controlled_cutover_authorized: false
  production_release_authorized: false
next_gate:
  current_stage: STAGE_1
  current_gate: GATE_A_SHADOW_ENTRY
  state: READY_NOT_DISPATCHED
  owner_decision_required_before_any_authority_transition: true
""",
        )
        roadmap = {
            "roadmap_id": "AAA-v1-POST-IV-OPERATING-ROADMAP",
            "version": "v1.0",
            "status": "OWNER_APPROVED",
            "approved_at": "2026-08-17T01:00:00+09:00",
            "stages": [
                {"id": "STAGE_0", "name": "POST-IV FINAL PLAN INTEGRATION"},
                {"id": "STAGE_1", "name": "MANAGED POSTGRESQL SHADOW-ENTRY QUALIFICATION"},
                {"id": "STAGE_2", "name": "SINGLE GOVERNED NON-AUTHORITATIVE WORKER FAILURE CAMPAIGN"},
            ],
            "validator_modifications": [{"id": "P0-01", "requirement": "AUTHORITATIVE TIME / LEASE CLOCK"}],
            "legacy_run_governance": {
                "current_dispositions": {
                    "RUN-VALIDATION-AAA-INDEPENDENT-PREFLIGHT-20260816-002": "NOT_REGISTERED",
                    "RUN-VALIDATION-AAA-T18-INDEPENDENT-20260816-001": "NOT_REGISTERED",
                }
            },
        }
        self._write(
            self.aaa_architecture / "AAA-v1-POST-IV-OPERATING-ROADMAP_v1.0_OWNER-APPROVED.json",
            json.dumps(roadmap),
        )
        for run_id in (
            "RUN-VALIDATION-AAA-INDEPENDENT-PREFLIGHT-20260816-002",
            "RUN-VALIDATION-AAA-T18-INDEPENDENT-20260816-001",
        ):
            self._write(
                self.aaa_runs / f"{run_id}.json",
                json.dumps(
                    {
                        "run_id": run_id,
                        "state": "DISPATCHED_AWAITING_ACK",
                        "started_at": None,
                        "last_heartbeat_at": None,
                        "terminal_result": None,
                    }
                ),
            )

    def _write_channel_registry(self, version: str, *, core_a_active: bool, validation_active: bool, status: str = "WORKING") -> None:
        core_a_state = "ACTIVE" if core_a_active else "CLOSED"
        validation_state = "ACTIVE" if validation_active else "CLOSED"
        self._write(
            self.continuity / f"SEMI-CHANNEL-REGISTRY_{version}.yaml",
            f"""registry_id: SEMI-CHANNEL-REGISTRY
version: {version}
status: {status}
as_of: '2026-08-17T01:00:00+09:00'
current_structure:
  core_a_dedicated_active_channel: false
instances:
  - channel_instance_id: CTRL-A
    persona_id: SEMI-CONTROL-ARCHITECT
    channel_type: PERSONA_CHANNEL
    display_name: CORE A channel
    status: {core_a_state}
  - channel_instance_id: CORE-B
    persona_id: SEMI-MODEL-VALIDATION-DESIGN-ARCHITECT
    channel_type: PERSONA_CHANNEL
    display_name: CORE B channel
    status: ACTIVE
  - channel_instance_id: VALID
    persona_id: SEMI-VALIDATION-AUDITOR
    channel_type: VALIDATION
    display_name: Validation channel
    status: {validation_state}
  - channel_instance_id: AAA-ADVISER
    persona_id: null
    channel_type: ADVISORY
    display_name: AAA ADVISER
    status: ACTIVE
  - channel_instance_id: AAA-BUILDER
    persona_id: null
    channel_type: CONTROLLER
    display_name: AAA BUILDER CONTROLLER
    status: ACTIVE
""",
        )

    def test_formal_persona_exists_without_active_core_a_channel(self) -> None:
        payload = build_operating_structure(self.temp)
        core_a = next(row for row in payload["formal_personas"] if row["persona_id"] == "SEMI-CONTROL-ARCHITECT")
        self.assertEqual(core_a["status"], "ACTIVE")
        self.assertEqual(core_a["active_channel_binding_state"], "NOT_INSTANTIATED")
        self.assertEqual(core_a["active_channels"], [])
        builder = next(row for row in payload["active_channels"] if row["display_name"] == "AAA BUILDER CONTROLLER")
        adviser = next(row for row in payload["active_channels"] if row["display_name"] == "AAA ADVISER")
        self.assertEqual(builder["channel_type"], "CONTROLLER")
        self.assertIsNone(builder["persona_binding"])
        self.assertEqual(adviser["channel_type"], "ADVISORY")
        self.assertIsNone(adviser["persona_binding"])

    def test_projection_reloads_new_channel_registry_without_manual_diagram_edit(self) -> None:
        first = build_operating_structure(self.temp)
        research = next(row for row in first["formal_personas"] if row["persona_id"] == "SEMI-RESEARCH-ORCHESTRATOR")
        self.assertEqual(research["active_channel_binding_state"], "NOT_INSTANTIATED")

        self._write(
            self.continuity / "SEMI-CHANNEL-REGISTRY_v1.5.yaml",
            """registry_id: SEMI-CHANNEL-REGISTRY
version: v1.5
status: WORKING
as_of: '2026-08-17T01:10:00+09:00'
current_structure:
  core_a_dedicated_active_channel: false
instances:
  - channel_instance_id: RESEARCH-NEW
    persona_id: SEMI-RESEARCH-ORCHESTRATOR
    channel_type: PERSONA_CHANNEL
    display_name: Research current channel
    status: ACTIVE
""",
        )
        second = build_operating_structure(self.temp)
        research = next(row for row in second["formal_personas"] if row["persona_id"] == "SEMI-RESEARCH-ORCHESTRATOR")
        self.assertEqual(research["active_channel_binding_state"], "ACTIVE")
        self.assertEqual(research["active_channels"][0]["channel_instance_id"], "RESEARCH-NEW")

    def test_conflict_is_visible_instead_of_silently_resolved(self) -> None:
        self._write_channel_registry("v1.6", core_a_active=True, validation_active=True)
        payload = build_operating_structure(self.temp)
        self.assertEqual(payload["projection"]["status"], "CONFLICT")
        self.assertTrue(any(row["type"] == "CORE_A_CHANNEL_CURRENT_STATE_CONFLICT" for row in payload["projection"]["conflicts"]))

    def test_declared_stale_source_remains_stale(self) -> None:
        self._write_channel_registry("v1.6", core_a_active=False, validation_active=True, status="STALE")
        payload = build_operating_structure(self.temp)
        self.assertEqual(payload["projection"]["status"], "STALE")
        self.assertEqual(payload["projection"]["sources"]["channel_registry"]["availability"], "STALE")

    def test_missing_required_persistent_source_is_unavailable_not_guessed(self) -> None:
        (self.aaa_architecture / "AAA-v1-POST-IV-OPERATING-ROADMAP_v1.0_OWNER-APPROVED.json").unlink()
        payload = build_operating_structure(self.temp)
        self.assertEqual(payload["projection"]["status"], "UNAVAILABLE")
        self.assertEqual(payload["roadmap"]["current_stage"], "STAGE_1")
        self.assertIsNone(payload["roadmap"]["roadmap_id"])

    def test_authority_and_historical_current_disposition_are_separate(self) -> None:
        payload = build_operating_structure(self.temp)
        flags = payload["authority"]["operational_flags"]
        self.assertTrue(flags["json_registry_operational_authority_during_shadow"])
        for key in (
            "postgresql_authoritative",
            "bounded_shadow_execution_authorized",
            "live_execution_authorized",
            "production_canonical_promotion_authorized",
            "controlled_cutover_authorized",
            "production_release_authorized",
        ):
            self.assertFalse(flags[key])
        for run in payload["historical_runs"]:
            self.assertEqual(run["historical_state"], "DISPATCHED_AWAITING_ACK")
            self.assertEqual(run["current_disposition"], "NOT_REGISTERED")

    def test_projection_is_read_only(self) -> None:
        before = sorted(str(path.relative_to(self.temp)) for path in self.temp.rglob("*") if path.is_file())
        build_operating_structure(self.temp)
        after = sorted(str(path.relative_to(self.temp)) for path in self.temp.rglob("*") if path.is_file())
        self.assertEqual(before, after)


class OperatingStructureHTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.server = build_server(ROOT, host="127.0.0.1", port=0)
        cls.port = int(cls.server.server_address[1])
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def test_operating_structure_endpoint_is_read_only_and_exposes_source_provenance(self) -> None:
        connection = HTTPConnection("127.0.0.1", self.port, timeout=3)
        connection.request("GET", "/api/aaa/operating-structure")
        response = connection.getresponse()
        payload = json.loads(response.read().decode("utf-8"))
        status = response.status
        connection.close()
        self.assertEqual(status, 200)
        self.assertEqual(payload["project"], "Asset Agent ASA")
        self.assertEqual(payload["authority"]["authority_holder"]["authority_id"], "PROJECT_OWNER")
        self.assertIn("channel_registry", payload["projection"]["sources"])
        self.assertTrue(payload["ui_contract"]["read_only"])


if __name__ == "__main__":
    unittest.main()
