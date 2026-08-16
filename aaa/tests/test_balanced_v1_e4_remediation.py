from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "aaa" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aaa.core.release_v1 import CompatibleVersionSet, ComponentKind, ReleaseComponentRef


class BalancedV1E4RemediationTests(unittest.TestCase):
    def test_python_component_hash_matches_sql_certifying_fixtures(self) -> None:
        old = CompatibleVersionSet(
            "RELEASE-OLD",
            (
                ReleaseComponentRef(
                    ComponentKind.MODEL,
                    "MODEL-OLD",
                    "v1",
                    "a" * 64,
                    byte_size=100,
                    persistent_locator="s3://immutable/model-old",
                ),
            ),
            "COMPAT-E4-OLD",
            "DEC-E4-OLD",
        )
        new = CompatibleVersionSet(
            "RELEASE-NEW",
            (
                ReleaseComponentRef(
                    ComponentKind.MODEL,
                    "MODEL-NEW",
                    "v2",
                    "b" * 64,
                    byte_size=120,
                    persistent_locator="s3://immutable/model-new",
                ),
                ReleaseComponentRef(
                    ComponentKind.SHARED_CONTRACT,
                    "SHARED-CONTRACT",
                    "v0.7",
                    "c" * 40,
                    byte_size=4096,
                    persistent_locator="git:shared-contract-v0.7",
                ),
            ),
            "COMPAT-E4-NEW",
            "DEC-E4-NEW",
        )
        unverified = CompatibleVersionSet(
            "RELEASE-UNVERIFIED",
            (
                ReleaseComponentRef(
                    ComponentKind.MODEL,
                    "MODEL-UNVERIFIED",
                    "v3",
                    "d" * 64,
                    byte_size=130,
                    persistent_locator="s3://staging/model-unverified",
                    verified=False,
                ),
            ),
            "COMPAT-E4-UNVERIFIED",
            "DEC-E4-UNVERIFIED",
        )
        self.assertEqual(
            old.component_set_sha256,
            "f6ecabbe7d5c06e1986c0ed84ef1fb5878b8ffcd6ae1aa280b047f2188c23919",
        )
        self.assertEqual(
            new.component_set_sha256,
            "43429f105a0876d54ebde4b30bdd436c61391688fafab89ab1456f8ad0033f27",
        )
        self.assertEqual(
            unverified.component_set_sha256,
            "4ef9c561fdccca82b008f087adb67f94cbcaa3ab7946aeb4848acd5533a399f8",
        )

    def test_migration_0010_is_forward_only_and_exact_hash_registered(self) -> None:
        manifest = json.loads((ROOT / "aaa" / "db" / "MIGRATIONS.json").read_text(encoding="utf-8"))
        observed = {item["version"]: item for item in manifest["migrations"]}
        self.assertEqual(
            observed["0009"]["sha256"],
            "86c4827a834e62d4319ba2a1c3c238320f095f3e2bbb199ff42f5c90e1e22ec2",
        )
        self.assertEqual(
            observed["0010"]["sha256"],
            "07b4244fc007ca5a0d5488ed4675b25a4e81d6e787a75d19258cb43c8ead7b7a",
        )
        self.assertEqual(
            hashlib.sha256((ROOT / observed["0010"]["path"]).read_bytes()).hexdigest(),
            observed["0010"]["sha256"],
        )
        self.assertTrue(manifest["balanced_v1"]["e4_migration_0009_integrated_immutable"])
        self.assertTrue(manifest["balanced_v1"]["e4_forward_remediation_migration_0010"])

    def test_certifying_postgresql_workflow_executes_e4_smoke(self) -> None:
        workflow = (ROOT / ".github" / "workflows" / "aaa-build-tests.yml").read_text(encoding="utf-8")
        self.assertIn(
            "aaa/db/tests/e4_version_set_promotion_restore_smoke.sql",
            workflow,
        )
        self.assertIn(
            "Balanced-v1 E1/E2/E3/E4 PostgreSQL migrations and contract smoke",
            workflow,
        )


if __name__ == "__main__":
    unittest.main()
