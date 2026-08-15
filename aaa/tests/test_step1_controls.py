from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
CONTROL = ROOT / "control" / "aaa" / "v0.1"


class Step1ControlTests(unittest.TestCase):
    def read(self, name: str) -> str:
        path = CONTROL / name
        self.assertTrue(path.exists(), f"missing control asset: {path}")
        return path.read_text(encoding="utf-8")

    def test_naming_contract_uses_aaa(self):
        text = self.read("AAA-NAMING-TRANSITION-CONTRACT_v0.1_WORKING.yaml")
        self.assertIn("project: Asset Agent ASA", text)
        self.assertIn("short_name: AAA", text)
        self.assertIn("legacy_SEMI_OPS: HISTORICAL_ONLY", text)

    def test_build_contract_is_fail_closed(self):
        text = self.read("AAA-BUILD-CONTRACT_v0.1_WORKING.yaml")
        self.assertIn("general_agent_canonical_write: PROHIBITED", text)
        self.assertIn("deterministic_core_must_work_without_llm: true", text)
        self.assertIn("current_canonical_control_during_shadow: EXISTING_SEMI_CONTROL_PLANE", text)

    def test_build_matrix_has_eight_tracks_and_noninterference(self):
        text = self.read("AAA-BUILD-MATRIX_v0.1_WORKING.yaml")
        for n in range(1, 9):
            self.assertIn(f"AAA-T0{n}-", text)
        self.assertIn("hard_rule: NO_TWO_TRACKS_OWN_SAME_FILE", text)
        self.assertIn("active_m3top3_source_paths_initially_read_only: true", text)

    def test_step1_record_does_not_claim_cutover(self):
        text = self.read("AAA-STEP1-EXECUTION-RECORD_v0.1_WORKING.yaml")
        self.assertIn("canonical_state_cutover: false", text)
        self.assertIn("u127_modified: false", text)
        self.assertIn("frozen_architecture_modified: false", text)


if __name__ == "__main__":
    unittest.main()
