from __future__ import annotations

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "aaa" / "web" / "src" / "App.tsx"
GATE = ROOT / "control" / "aaa" / "v0.1" / "AAA-PROCESS-GATE-STATUS_v0.33_WORKING.yaml"


class PostIVOwnerConsoleAuthorityRemediationV11Tests(unittest.TestCase):
    def test_fnd03_owner_console_renders_exact_tristate_labels(self) -> None:
        source = APP.read_text(encoding="utf-8")
        self.assertIn("if (value === true) return 'TRUE'", source)
        self.assertIn("if (value === false) return 'FALSE'", source)
        self.assertIn("return 'UNKNOWN'", source)
        self.assertNotIn("OPEN / TRUE", source)
        self.assertNotIn("CLOSED / FALSE", source)

    def test_fnd03_persistent_gate_keeps_postgresql_operational_sot_closed(self) -> None:
        source = GATE.read_text(encoding="utf-8")
        self.assertIn("postgresql_operational_sot_authorized: false", source)
        self.assertIn("bounded_shadow_execution_authorized: false", source)
        self.assertIn("live_execution_authorized: false", source)


if __name__ == "__main__":
    unittest.main()
