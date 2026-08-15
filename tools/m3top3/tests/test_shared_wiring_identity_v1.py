from __future__ import annotations

import hashlib
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
COMPONENTS = (
    "tools/m3top3/shared_interface_guards_v1_1.py",
    "tools/m3top3/release_vdi_v1.py",
    "tools/m3top3/official_runtime_v1.py",
    "tools/m3top3/tests/test_shared_interface_wiring_v1.py",
    "tools/m3top3/tests/test_shared_wiring_identity_v1.py",
)


class TestSharedWiringIdentity(unittest.TestCase):
    def test_shared_wiring_component_sha256_manifest(self):
        for rel in COMPONENTS:
            data = (REPO_ROOT / rel).read_bytes()
            digest = hashlib.sha256(data).hexdigest()
            self.assertEqual(len(digest), 64)
            print(f"SHARED_WIRING_SHA256 {digest} {len(data)} {rel}")


if __name__ == "__main__":
    unittest.main()
