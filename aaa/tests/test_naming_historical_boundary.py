from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
AAA_CONTROL = ROOT / "control" / "aaa" / "v0.1"


class NamingBoundaryTests(unittest.TestCase):
    def test_current_aaa_assets_use_current_product_name(self):
        for path in AAA_CONTROL.glob("AAA-*.yaml"):
            text = path.read_text(encoding="utf-8")
            self.assertIn("Asset Agent ASA", text, path.name)

    def test_legacy_name_is_explicitly_historical(self):
        text = (AAA_CONTROL / "AAA-NAMING-TRANSITION-CONTRACT_v0.1_WORKING.yaml").read_text(encoding="utf-8")
        self.assertIn("new_usage: PROHIBITED_AS_CURRENT_PRODUCT_PROJECT_NAME", text)
        self.assertIn("history_policy: PRESERVE_NO_REWRITE", text)


if __name__ == "__main__":
    unittest.main()
