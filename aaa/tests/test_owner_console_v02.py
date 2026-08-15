from __future__ import annotations

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "aaa" / "web" / "src" / "App.tsx"


class OwnerConsoleV02Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.source = APP.read_text(encoding="utf-8")

    def test_console_reads_live_deterministic_api(self) -> None:
        self.assertIn("/status", self.source)
        self.assertIn("/work", self.source)
        self.assertIn("/gates", self.source)
        self.assertIn("cache: 'no-store'", self.source)
        self.assertIn("API {apiState}", self.source)

    def test_console_does_not_embed_stale_current_state(self) -> None:
        self.assertNotIn("SEMI-CURRENT-STATE v2.10", self.source)
        self.assertNotIn("SEMI-CURRENT-STATE v2.11", self.source)
        self.assertIn("SHADOW / READ-ONLY", self.source)
        self.assertIn("PROHIBITED", self.source)

    def test_console_keeps_llm_optional(self) -> None:
        self.assertIn("llm_required_for_control_plane", self.source)
        self.assertIn("NOT REQUIRED", self.source)
        self.assertIn("Owner-visible state without requiring an LLM connection.", self.source)


if __name__ == "__main__":
    unittest.main()
