from __future__ import annotations

import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "aaa" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aaa.api.operating_structure import build_operating_structure


class PostIVIndependentValidationRemediationV11Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = Path(tempfile.mkdtemp(prefix="aaa-postiv-remediation-"))
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

    def _org(self, version: str = "v0.2_WORKING", status: str = "OWNER_ACCEPTED", supersedes: str | None = None) -> str:
        line = f"supersedes: {supersedes}\n" if supersedes else ""
        return f"""org_map_id: SEMI-ORG-MAP
version: {version}
status: {status}
as_of: '2026-08-17T01:00:00+09:00'
{line}formal:
  a: SEMI-CONTROL-ARCHITECT
  b: SEMI-MODEL-VALIDATION-DESIGN-ARCHITECT
  r: SEMI-RESEARCH-ORCHESTRATOR
  v: SEMI-VALIDATION-AUDITOR
"""

    def _current_state_v211(self, status: str = "WORKING_INDEPENDENT_DELTA_FAILED_F06_BOUNDED_FIX_ROUTED") -> str:
        return f"""state_id: SEMI-CURRENT-STATE
version: v2.11
status: {status}
as_of: '2026-08-17T01:00:00+09:00'
model_v1:
  model_version: M3TOP3-v1.0
  baseline_source_commit: 32c8a0f31428273d76b4e7b3f2cea76f955770aa
  control_fix_successor:
    source_commit: 5ee82d15a27237ed2ad142ae877c6595f0489f80
    independent_delta_verdict: FAIL_FND_02_F06_ECONOMIC_EVENT_ID_ROTATION_BYPASS
independent_delta_preflight:
  current_status: WAITING_NEW_F06_HARDENING_SUCCESSOR
  prior_exact_target_commit: 5ee82d15a27237ed2ad142ae877c6595f0489f80
  prior_result: FAIL_FND_02
  rerun_required: true
"""

    def _write_baseline(self) -> None:
        self._write(self.continuity / "SEMI-ORG-MAP_v0.2_WORKING.yaml", self._org())
        self._write(
            self.continuity / "SEMI-CHANNEL-REGISTRY_v1.4.yaml",
            """registry_id: SEMI-CHANNEL-REGISTRY
version: v1.4
status: WORKING_OWNER_APPROVED_CURRENT_OPERATING_STRUCTURE
as_of: '2026-08-17T01:00:00+09:00'
current_structure:
  core_a_dedicated_active_channel: false
instances:
  - channel_instance_id: CORE-B
    persona_id: SEMI-MODEL-VALIDATION-DESIGN-ARCHITECT
    channel_type: PERSONA_CHANNEL
    display_name: CORE B channel
    status: ACTIVE
  - channel_instance_id: VALID
    persona_id: SEMI-VALIDATION-AUDITOR
    channel_type: VALIDATION
    display_name: Validation channel
    status: ACTIVE
""",
        )
        self._write(self.continuity / "SEMI-CURRENT-STATE_v2.11.yaml", self._current_state_v211())
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
            "stages": [{"id": "STAGE_1", "name": "MANAGED POSTGRESQL SHADOW-ENTRY QUALIFICATION"}],
            "legacy_run_governance": {"current_dispositions": {}},
        }
        self._write(
            self.aaa_architecture / "AAA-v1-POST-IV-OPERATING-ROADMAP_v1.0_OWNER-APPROVED.json",
            json.dumps(roadmap),
        )

    def test_fnd01_forward_roadmap_binds_all_detailed_acceptance_semantics(self) -> None:
        roadmap_path = ROOT / "control" / "aaa" / "architecture" / "AAA-v1-POST-IV-OPERATING-ROADMAP_v1.1_OWNER-APPROVED.json"
        payload = json.loads(roadmap_path.read_text(encoding="utf-8"))
        self.assertEqual(payload["version"], "v1.1")
        self.assertEqual(
            payload["supersedes"],
            "control/aaa/architecture/AAA-v1-POST-IV-OPERATING-ROADMAP_v1.0_OWNER-APPROVED.json",
        )
        contracts = payload["acceptance_contracts"]
        self.assertEqual(set(contracts), {"P0-01", "P0-02", "P0-03", "P0-04", "P0-05", "P0-06"})
        self.assertFalse(contracts["P0-01"]["worker_local_clock_authority"])
        self.assertEqual(contracts["P0-01"]["future_timestamp_behavior"], "FAIL_CLOSED")
        self.assertEqual(set(contracts["P0-02"]["failure_cases"]), {"A", "B", "C"})
        self.assertEqual(contracts["P0-03"]["explicit_acceptance_example"], "999 / 1000 required shards != COMPLETE")
        self.assertIn("AI adjudication != Ground Truth", contracts["P0-04"]["hard_rules"])
        self.assertIn("FAIL_CLOSED", contracts["P0-05"]["negative_test"])
        self.assertIn("U127", contracts["P0-06"]["p0_operational_fitness"])
        self.assertIn("1M", contracts["P0-06"]["p1_deferred_nonblocking"])

    def test_fnd02_organization_missing_fails_closed(self) -> None:
        (self.continuity / "SEMI-ORG-MAP_v0.2_WORKING.yaml").unlink()
        payload = build_operating_structure(self.temp)
        self.assertEqual(payload["projection"]["status"], "UNAVAILABLE")
        self.assertEqual(payload["projection"]["sources"]["organization"]["availability"], "UNAVAILABLE")
        self.assertEqual(payload["authority"]["authority_holder"]["authority_id"], "UNKNOWN")
        self.assertTrue(all(row["status"] == "UNKNOWN" for row in payload["formal_personas"]))

    def test_fnd02_organization_declared_stale_fails_closed(self) -> None:
        self._write(self.continuity / "SEMI-ORG-MAP_v0.2_WORKING.yaml", self._org(status="STALE"))
        payload = build_operating_structure(self.temp)
        self.assertEqual(payload["projection"]["status"], "STALE")
        self.assertEqual(payload["projection"]["sources"]["organization"]["availability"], "STALE")
        self.assertTrue(all(row["status"] == "STALE" for row in payload["formal_personas"]))

    def test_fnd02_organization_unproven_status_is_not_current(self) -> None:
        self._write(self.continuity / "SEMI-ORG-MAP_v0.2_WORKING.yaml", self._org(status="UNPROVEN"))
        payload = build_operating_structure(self.temp)
        self.assertEqual(payload["projection"]["status"], "UNAVAILABLE")
        self.assertEqual(payload["projection"]["sources"]["organization"]["availability"], "UNAVAILABLE")

    def test_fnd02_current_state_missing_fails_science_closed(self) -> None:
        (self.continuity / "SEMI-CURRENT-STATE_v2.11.yaml").unlink()
        payload = build_operating_structure(self.temp)
        science = next(row for row in payload["workstreams"] if row["workstream_id"] == "M3TOP3_SCIENTIFIC_VALIDATION")
        self.assertEqual(payload["projection"]["status"], "UNAVAILABLE")
        self.assertEqual(science["status"], "UNKNOWN")
        self.assertIsNone(science["current_activity"])
        self.assertIsNone(science["exact_target"])

    def test_fnd02_current_state_declared_stale_fails_science_closed(self) -> None:
        self._write(self.continuity / "SEMI-CURRENT-STATE_v2.11.yaml", self._current_state_v211(status="STALE"))
        payload = build_operating_structure(self.temp)
        science = next(row for row in payload["workstreams"] if row["workstream_id"] == "M3TOP3_SCIENTIFIC_VALIDATION")
        self.assertEqual(payload["projection"]["status"], "STALE")
        self.assertEqual(science["status"], "STALE")
        self.assertIsNone(science["current_activity"])

    def test_fnd02_current_state_unproven_status_is_not_current(self) -> None:
        self._write(self.continuity / "SEMI-CURRENT-STATE_v2.11.yaml", self._current_state_v211(status="UNPROVEN"))
        payload = build_operating_structure(self.temp)
        self.assertEqual(payload["projection"]["status"], "UNAVAILABLE")
        self.assertEqual(payload["projection"]["sources"]["current_state"]["availability"], "UNAVAILABLE")

    def test_fnd02_higher_numeric_ineligible_source_does_not_win(self) -> None:
        self._write(
            self.continuity / "SEMI-ORG-MAP_v9.9_WORKING.yaml",
            self._org(version="v9.9", status="UNPROVEN"),
        )
        payload = build_operating_structure(self.temp)
        source = payload["projection"]["sources"]["organization"]
        self.assertEqual(source["availability"], "AVAILABLE")
        self.assertTrue(source["path"].endswith("SEMI-ORG-MAP_v0.2_WORKING.yaml"))
        self.assertEqual(source["selection"]["skipped"][0]["reason"], "UNSUPPORTED_OR_UNPROVEN_GOVERNED_STATUS")

    def test_fnd02_dependent_facts_do_not_render_current_when_provenance_unavailable(self) -> None:
        (self.continuity / "SEMI-ORG-MAP_v0.2_WORKING.yaml").unlink()
        (self.continuity / "SEMI-CURRENT-STATE_v2.11.yaml").unlink()
        payload = build_operating_structure(self.temp)
        self.assertNotEqual(payload["projection"]["status"], "CURRENT")
        self.assertEqual(payload["authority"]["authority_holder"]["display_name"], "UNKNOWN")
        science = next(row for row in payload["workstreams"] if row["workstream_id"] == "M3TOP3_SCIENTIFIC_VALIDATION")
        self.assertEqual(science["status"], "UNKNOWN")

    def test_fnd03_postgresql_operational_sot_flag_is_exact_false(self) -> None:
        payload = build_operating_structure(self.temp)
        flags = payload["authority"]["operational_flags"]
        self.assertIn("postgresql_operational_sot_authorized", flags)
        self.assertIs(flags["postgresql_operational_sot_authorized"], False)

    def test_fnd04_v211_current_scientific_state_does_not_substitute_baseline(self) -> None:
        payload = build_operating_structure(self.temp)
        science = next(row for row in payload["workstreams"] if row["workstream_id"] == "M3TOP3_SCIENTIFIC_VALIDATION")
        self.assertEqual(science["schema_binding"], "SEMI-CURRENT-STATE_V2_EXPLICIT")
        self.assertEqual(science["current_activity"], "WAITING_NEW_F06_HARDENING_SUCCESSOR")
        self.assertEqual(science["current_target_state"], "NOT_REGISTERED")
        self.assertIsNone(science["exact_target"])
        self.assertEqual(science["last_control_fix_target"], "5ee82d15a27237ed2ad142ae877c6595f0489f80")
        self.assertEqual(science["historical_baseline_target"], "32c8a0f31428273d76b4e7b3f2cea76f955770aa")
        self.assertNotEqual(science["exact_target"], science["historical_baseline_target"])

    def test_fnd04_v2_current_successor_is_bound_when_present_and_not_waiting_new(self) -> None:
        text = self._current_state_v211().replace(
            "WAITING_NEW_F06_HARDENING_SUCCESSOR",
            "WAITING_INDEPENDENT_VALIDATION_ON_CONTROL_FIX_SUCCESSOR",
        )
        self._write(self.continuity / "SEMI-CURRENT-STATE_v2.11.yaml", text)
        payload = build_operating_structure(self.temp)
        science = next(row for row in payload["workstreams"] if row["workstream_id"] == "M3TOP3_SCIENTIFIC_VALIDATION")
        self.assertEqual(science["exact_target"], "5ee82d15a27237ed2ad142ae877c6595f0489f80")
        self.assertEqual(science["current_target_state"], "BOUND")

    def test_fnd04_absent_current_field_stays_unknown_without_baseline_fallback(self) -> None:
        text = self._current_state_v211().replace(
            "independent_delta_preflight:\n  current_status: WAITING_NEW_F06_HARDENING_SUCCESSOR\n",
            "independent_delta_preflight:\n",
        )
        self._write(self.continuity / "SEMI-CURRENT-STATE_v2.11.yaml", text)
        payload = build_operating_structure(self.temp)
        science = next(row for row in payload["workstreams"] if row["workstream_id"] == "M3TOP3_SCIENTIFIC_VALIDATION")
        self.assertEqual(science["status"], "UNKNOWN")
        self.assertIsNone(science["exact_target"])
        self.assertEqual(science["historical_baseline_target"], "32c8a0f31428273d76b4e7b3f2cea76f955770aa")

    def test_operational_pass_and_scientific_pass_remain_distinct(self) -> None:
        payload = build_operating_structure(self.temp)
        aaa = next(row for row in payload["workstreams"] if row["workstream_id"] == "AAA_OPERATIONALIZATION")
        science = next(row for row in payload["workstreams"] if row["workstream_id"] == "M3TOP3_SCIENTIFIC_VALIDATION")
        self.assertEqual(aaa["status"], "AWAITING_DISPATCH")
        self.assertNotEqual(science["current_validation_verdict"], "PASS")


if __name__ == "__main__":
    unittest.main()
