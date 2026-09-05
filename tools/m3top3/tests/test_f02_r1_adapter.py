"""P3 author verification of F02-R1 input admission; no scoring or outcome access."""

from __future__ import annotations

import copy
import hashlib
import json
import shutil
import tempfile
import unittest
from collections import Counter
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from tools.m3top3 import f02_r1_adapter as adapter
from tools.m3top3 import cli_run_real_input_replay as cli
from tools.m3top3 import real_input_replay_v1 as replay
from tools.m3top3.core import sha256_hex
from tools.m3top3.coverage_limited_replay_v1 import (
    FEATURE_IDS,
    load_population_bytes,
    parse_population_bytes,
)


REPO = Path(__file__).resolve().parents[3]
RUN_ID = "AAA-M3TOP3-F02-R1-20260905-171755-CODEX-01"
RUN_ROOT = (
    REPO / "control/m3top3/f02-r1-multi-company-input-repair/v1.0/runs" / RUN_ID
)
CUTOFF = "2024-08-09T23:59:59+09:00"
CODE_ID = "M3TOP3-REAL-INPUT-EXECUTABLE-BUNDLE-SHA256:F02-R1-ADMISSION-TEST"
SCIENTIFIC_STATE = "EXPLORATORY_AFTER_W1_OUTCOME_EXPOSURE"
OPERATOR_ID = "M3TOP3_F02_RELATIVE_FROM_OBSERVED_PAIR_v1"
EXPECTED = {
    "KRX:003160": ("KRW", "2024Q1", "2023Q1", "34732575950", "39216899579", "-1836830457", "865831578"),
    "KRX:025560": ("KRW", "2024Q1", "2023Q1", "5162565692", "4785829491", "2040268633", "-442977057"),
    "KRX:031980": ("KRW", "2024Q1", "2023Q1", "38094447594", "14913281644", "15420952017", "3496296368"),
    "KRX:036200": ("KRW", "2024Q1", "2023Q1", "55186952755", "51753687853", "4559702713", "4333422148"),
    "KRX:005290": ("KRW_MILLION", "2024Q2", "2023Q2", "355414", "331317", "49972", "45565"),
}


class TestF02R1Admission(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.population = parse_population_bytes(load_population_bytes(REPO))
        cls.mapping, cls.manifest, cls.leaves = adapter.build_inputs(REPO)
        cls.manifest_hash = hashlib.sha256(adapter.json_bytes(cls.manifest)).hexdigest()
        cls.sources = adapter.validate_source_manifest(
            cls.manifest,
            manifest_content_sha256=cls.manifest_hash,
            repo=REPO,
            expected_run_id=RUN_ID,
        )

    def _manifest(self, manifest, *, repo=REPO, expected_run_id=RUN_ID, content_hash=None):
        return adapter.validate_source_manifest(
            manifest,
            manifest_content_sha256=content_hash or hashlib.sha256(adapter.json_bytes(manifest)).hexdigest(),
            repo=repo,
            expected_run_id=expected_run_id,
        )

    def _leaves(self, leaves, *, population=None):
        return adapter.validate_feature_leaves(
            leaves,
            manifest=self.manifest,
            manifest_content_sha256=self.manifest_hash,
            sources=self.sources,
            population_rows=self.population if population is None else population,
            expected_run_id=RUN_ID,
        )

    def _mis(self, *, leaves=None, population=None, code_identity=CODE_ID):
        # Admission tests may never silently advance to engine scoring.
        with patch.object(replay, "build_engine", side_effect=AssertionError("scoring is outside this test act")):
            return replay.build_strict_w1_mis(
                self.population if population is None else population,
                pmo_run_id=RUN_ID,
                manifest=self.manifest,
                manifest_content_sha256=self.manifest_hash,
                leaf_records=self.leaves if leaves is None else leaves,
                repo=REPO,
                code_identity=code_identity,
            )

    def _changed_leaf(self, *, company="KRX:003160", path="/metric_pairs/revenue/current"):
        leaves = copy.deepcopy(self.leaves)
        leaf = next(item for item in leaves if item["company_id"] == company and item["input_path"] == path)
        return leaves, leaf

    def test_five_exact_sources_and_native_units_are_admitted(self):
        self.assertEqual(self.manifest["schema_version"], adapter.SOURCE_MANIFEST_SCHEMA)
        self.assertEqual({source["company_id"] for source in self.sources.values()}, set(EXPECTED))
        self.assertEqual(len(self.sources), 5)
        leaves = self._leaves(self.leaves)
        self.assertEqual(len(leaves), 40)
        self.assertEqual(Counter(item["evidence_kind"] for item in leaves), {"OBSERVED": 20, "DERIVED": 20})
        for company, (unit, current_period, prior_period, *values) in EXPECTED.items():
            with self.subTest(company=company):
                selected = {item["input_path"]: item for item in leaves if item["company_id"] == company}
                self.assertEqual(len(selected), 8)
                for (metric, field), value in zip(
                    [("revenue", "current"), ("revenue", "prior"), ("operating_profit", "current"), ("operating_profit", "prior")],
                    values,
                ):
                    leaf = selected[f"/metric_pairs/{metric}/{field}"]
                    self.assertEqual(leaf["value"], value)
                    self.assertEqual(leaf["unit_or_category"], unit)
                    self.assertEqual(leaf["effective_period"]["label"], current_period if field == "current" else prior_period)
                    self.assertFalse(leaf["contains_estimated_input"])
                for metric in ("revenue", "operating_profit"):
                    self.assertEqual(selected[f"/metric_pairs/{metric}/change_mode"]["value"], "RELATIVE")
                    self.assertEqual(selected[f"/metric_pairs/{metric}/operator_id"]["value"], OPERATOR_ID)

    def test_public_dates_remain_conservative_date_only_intervals(self):
        for source in self.sources.values():
            with self.subTest(company=source["company_id"]):
                date = source["publication_date"]
                self.assertEqual(source["publication_precision"], "DATE_ONLY")
                self.assertIsNone(source["publication_at"])
                self.assertEqual(source["publication_interval"], {
                    "earliest_at": f"{date}T00:00:00+09:00",
                    "latest_at": f"{date}T23:59:59+09:00",
                    "bound_method_id": "DATE_ONLY_KST_CLOSED_DAY_v1",
                })
                self.assertLessEqual(source["publication_interval"]["latest_at"], CUTOFF)

    def test_input_builder_is_deterministic(self):
        mapping, manifest, leaves = adapter.build_inputs(REPO)
        self.assertEqual((mapping, manifest, leaves), (self.mapping, self.manifest, self.leaves))

    def test_mis_preserves_population_missingness_and_consumed_scope_without_scoring(self):
        w1 = [row for row in self.population if row["window_id"] == "W1"]
        self.assertEqual(len(w1), 127)
        self.assertEqual(Counter(row["historical_eligibility_status"] for row in w1),
                         {"ELIGIBLE": 57, "INELIGIBLE_BY_TRADABILITY": 8, "UNRESOLVED": 62})
        rows, custody = self._mis()
        self.assertEqual(len(rows), 57)
        available = {row["company_id"] for row in rows
                     if row["feature_raw_inputs"][replay.F02]["availability_state"] == "AVAILABLE"}
        self.assertEqual(available, set(EXPECTED))
        expected_consumed = {f"metric_pairs.{metric}.{field}" for metric in ("revenue", "operating_profit")
                             for field in ("current", "prior", "change_mode", "operator_id")}
        for row in rows:
            self.assertEqual(row["snapshot_cutoff_at"], CUTOFF)
            self.assertEqual(set(row["feature_raw_inputs"]), set(FEATURE_IDS))
            for feature_id, block in row["feature_raw_inputs"].items():
                if feature_id == replay.F02 and row["company_id"] in EXPECTED:
                    self.assertEqual(set(block["consumed_fields"]), expected_consumed)
                    self.assertEqual(set(block["consumed_value_provenance"]), expected_consumed)
                else:
                    self.assertEqual(block["availability_state"], "NOT_FOUND")
        self.assertEqual(custody["source_count"], 5)
        self.assertEqual(custody["sidecar_leaf_count"], 40)
        self.assertEqual(custody["observed_numeric_leaf_count"], 20)
        self.assertEqual(custody["derived_control_leaf_count"], 20)
        self.assertEqual(custody["estimated_leaf_count"], 0)

    def test_reordered_leaves_do_not_change_materialized_input(self):
        self.assertEqual(self._mis(), self._mis(leaves=list(reversed(copy.deepcopy(self.leaves)))))

    def test_old_bundle_identity_is_rejected(self):
        with self.assertRaises(ValueError):
            self._mis(code_identity=replay.PREDECESSOR_EXECUTABLE_BUNDLE_IDENTITY)

    def test_source_identity_and_schema_mutations_are_rejected(self):
        for key, value in (("schema_version", "UNREVIEWED_SCHEMA"), ("run_id", "OTHER_RUN")):
            with self.subTest(key=key):
                manifest = copy.deepcopy(self.manifest)
                manifest[key] = value
                with self.assertRaises(ValueError):
                    self._manifest(manifest)
        for key, value in (("company_id", "KRX:999999"), ("krx_code", "999999"),
                           ("source_id", "OTHER_SOURCE"), ("publisher", "OTHER_PROVIDER"),
                           ("canonical_locator", "https://example.invalid/report.htm")):
            with self.subTest(key=key):
                manifest = copy.deepcopy(self.manifest)
                manifest["sources"][0][key] = value
                with self.assertRaises(ValueError):
                    self._manifest(manifest)

    def test_source_raw_hash_blob_and_size_mutations_are_rejected(self):
        for key, value in (("sha256", "0" * 64), ("git_blob", "0" * 40), ("byte_size", 1)):
            with self.subTest(key=key):
                manifest = copy.deepcopy(self.manifest)
                manifest["sources"][0]["raw_artifact"][key] = value
                with self.assertRaises(ValueError):
                    self._manifest(manifest)

    def test_duplicate_or_removed_source_is_rejected(self):
        for sources in (self.manifest["sources"][:-1], [*self.manifest["sources"], self.manifest["sources"][0]]):
            with self.subTest(count=len(sources)):
                manifest = copy.deepcopy(self.manifest)
                manifest["sources"] = copy.deepcopy(sources)
                with self.assertRaises(ValueError):
                    self._manifest(manifest)

    def test_source_path_escape_and_cross_issuer_path_are_rejected(self):
        other_source = self.manifest["sources"][1]["raw_storage_ref"]
        for path in ("../outside.htm", str(REPO / self.manifest["sources"][0]["raw_storage_ref"]),
                     "tools/m3top3/scorer_v1.py", other_source):
            with self.subTest(path=path):
                manifest = copy.deepcopy(self.manifest)
                manifest["sources"][0]["raw_storage_ref"] = path
                with self.assertRaises(ValueError):
                    self._manifest(manifest)

    def test_post_cutoff_promoted_precision_and_interval_mutations_are_rejected(self):
        for field, value in (("publication_date", "2024-08-10"),
                             ("publication_at", "2024-05-16T12:00:00+09:00"),
                             ("publication_precision", "SECOND")):
            with self.subTest(field=field):
                manifest = copy.deepcopy(self.manifest)
                manifest["sources"][0][field] = value
                with self.assertRaises(ValueError):
                    self._manifest(manifest)
        manifest = copy.deepcopy(self.manifest)
        manifest["sources"][0]["publication_interval"]["latest_at"] = "2024-08-10T00:00:00+09:00"
        with self.assertRaises(ValueError):
            self._manifest(manifest)

    def test_fixed_population_denominator_cannot_be_rewritten(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["windows"][0]["include_count"] = 5
        with self.assertRaises(ValueError):
            self._manifest(manifest)
        population = copy.deepcopy(self.population)
        next(row for row in population if row["window_id"] == "W1")["historical_eligibility_status"] = "UNAPPROVED"
        with self.assertRaises(ValueError):
            self._mis(population=population)

    def test_partial_duplicate_and_extra_feature_leaves_are_rejected(self):
        for leaves in (self.leaves[:-1], [*self.leaves, self.leaves[0]]):
            with self.subTest(count=len(leaves)), self.assertRaises(ValueError):
                self._leaves(copy.deepcopy(leaves))
        leaves, leaf = self._changed_leaf()
        leaf["feature_id"] = "F03_FORWARD_REVISION_MOMENTUM"
        with self.assertRaises(ValueError):
            self._leaves(leaves)

    def test_leaf_manifest_source_hash_and_locator_mutations_are_rejected(self):
        leaves, leaf = self._changed_leaf()
        leaf["source_manifest_sha256"] = "0" * 64
        with self.assertRaises(ValueError):
            self._leaves(leaves)
        for key, value in (("source_id", "OTHER_SOURCE"), ("source_content_sha256", "0" * 64),
                           ("locator", "normalized-html:line-945")):
            with self.subTest(key=key):
                leaves, leaf = self._changed_leaf()
                leaf["source_refs"][0][key] = value
                with self.assertRaises(ValueError):
                    self._leaves(leaves)

    def test_wrong_period_scope_and_unit_are_rejected(self):
        for field, value in (("label", "2024Q2"), ("basis", "HALF_YEAR_CUMULATIVE"), ("scope", "STANDALONE")):
            with self.subTest(field=field):
                leaves, leaf = self._changed_leaf()
                leaf["effective_period"][field] = value
                with self.assertRaises(ValueError):
                    self._leaves(leaves)
        leaves, leaf = self._changed_leaf()
        leaf["unit_or_category"] = "KRW_MILLION"
        with self.assertRaises(ValueError):
            self._leaves(leaves)

    def test_negative_signs_and_restated_prior_cannot_be_silently_changed(self):
        for company, field, value in (("KRX:003160", "current", "1836830457"),
                                      ("KRX:025560", "prior", "442977057"),
                                      ("KRX:025560", "prior", "-448371497")):
            with self.subTest(company=company, value=value):
                leaves, leaf = self._changed_leaf(company=company, path=f"/metric_pairs/operating_profit/{field}")
                leaf["value"] = value
                with self.assertRaises(ValueError):
                    self._leaves(leaves)

    def test_zero_prior_nonfinite_and_binary_float_are_rejected(self):
        for value in ("0", "NaN", "Infinity", "-Infinity", 39216899579.0):
            with self.subTest(value=value):
                leaves, leaf = self._changed_leaf(path="/metric_pairs/revenue/prior")
                leaf["value"] = value
                with self.assertRaises(ValueError):
                    self._leaves(leaves)

    def test_operator_mode_and_derived_lineage_are_required(self):
        for field, value in (("change_mode", "ABSOLUTE"), ("operator_id", "UNREGISTERED_OPERATOR")):
            with self.subTest(field=field):
                leaves, leaf = self._changed_leaf(path=f"/metric_pairs/revenue/{field}")
                leaf["value"] = value
                with self.assertRaises(ValueError):
                    self._leaves(leaves)
        for lineage in ([], ["UNRESOLVED_UPSTREAM"]):
            leaves, leaf = self._changed_leaf(path="/metric_pairs/revenue/operator_id")
            leaf["input_lineage_refs"] = lineage
            with self.assertRaises(ValueError):
                self._leaves(leaves)

    def test_untracked_transform_estimation_and_outcome_fields_are_rejected(self):
        for field, value in (("transform_or_estimation_method_id", "UNTRACKED_SCALE"),
                             ("contains_estimated_input", True), ("evidence_kind", "ESTIMATED"),
                             ("future_return", "123")):
            with self.subTest(field=field):
                leaves, leaf = self._changed_leaf()
                leaf[field] = value
                with self.assertRaises(ValueError):
                    self._leaves(leaves)

    def test_strict_json_rejects_duplicate_keys_floats_and_nonfinite_constants(self):
        cases = ('{"source_id":"a","source_id":"b"}', '{"value":1.25}', '{"value":NaN}')
        with tempfile.TemporaryDirectory(prefix="f02-r1-json-test-") as temp:
            for index, payload in enumerate(cases):
                path = Path(temp) / f"invalid-{index}.json"
                path.write_text(payload, encoding="utf-8")
                with self.subTest(payload=payload), self.assertRaises(ValueError):
                    replay.load_source_manifest(path)

    def test_false_blind_actor_custody_is_rejected(self):
        profile = adapter.scientific_profile(self.manifest)
        self.assertIn(SCIENTIFIC_STATE, json.dumps(profile))
        manifest = copy.deepcopy(self.manifest)
        manifest["sources"][0]["outcome_custody"]["prior_actor_w1_outcome_exposure"] = False
        manifest["sources"][0]["outcome_custody"]["blind_process_claim"] = True
        with self.assertRaises(ValueError):
            self._manifest(manifest)

    def test_dependency_hash_and_registry_binding_tampering_are_rejected(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["input_profile"]["dependencies"][0]["sha256"] = "0" * 64
        with self.assertRaises(ValueError):
            self._manifest(manifest)
        manifest = copy.deepcopy(self.manifest)
        manifest["input_profile"]["consumed_registry_git_blob"] = "0" * 40
        with self.assertRaises(ValueError):
            self._manifest(manifest)

    def test_new_bundle_covers_adapter_and_every_declared_input_dependency(self):
        identity, components = cli._bind_successor_bundle(REPO, manifest=self.manifest)
        by_path = {item["path"]: item for item in components}
        self.assertIn("tools/m3top3/f02_r1_adapter.py", by_path)
        for dependency in self.manifest["input_profile"]["dependencies"]:
            self.assertIn(dependency["path"], by_path)
            self.assertEqual(by_path[dependency["path"]]["sha256"], dependency["sha256"])
        self.assertEqual(identity, "M3TOP3-REAL-INPUT-EXECUTABLE-BUNDLE-SHA256:" + sha256_hex(components))
        self.assertNotEqual(identity, replay.PREDECESSOR_EXECUTABLE_BUNDLE_IDENTITY)

    def test_bundle_rejects_manifest_dependency_digest_mismatch(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["input_profile"]["dependencies"][0]["sha256"] = "0" * 64
        with self.assertRaises(ValueError):
            cli._bind_successor_bundle(REPO, manifest=manifest)

    def _cli_args(self, root=REPO):
        run_root = root / "control/m3top3/f02-r1-multi-company-input-repair/v1.0/runs" / RUN_ID
        return SimpleNamespace(
            repo=root,
            pmo_run_id=RUN_ID,
            source_manifest=run_root / "inputs/SOURCE_MANIFEST.json",
            feature_sidecar=run_root / "inputs/FEATURE_SIDECAR.jsonl",
            affected_validation_report=run_root / "AFFECTED_VALIDATION_REPORT.json",
            output_dir=run_root / "score-and-seal",
            input_profile="F02_R1_EXPLORATORY_V1",
        )

    def test_cli_missing_gate_and_profile_mismatch_cannot_reach_engine(self):
        for mutation in ("missing_gate", "profile_mismatch"):
            args = self._cli_args()
            if mutation == "missing_gate":
                args.affected_validation_report = None
            else:
                args.input_profile = "LEGACY_STRICT_V1"
            with self.subTest(mutation=mutation), \
                 patch.object(cli, "_assert_clean_repo"), \
                 patch.object(cli, "_verify_preserved_predecessor", return_value={}), \
                 patch.object(cli, "_verify_r1_preserved_outputs", return_value={}), \
                 patch.object(cli, "load_source_manifest", return_value=(self.manifest, self.manifest_hash)), \
                 patch.object(cli, "load_feature_sidecar", return_value=(self.leaves, "1" * 64)), \
                 patch.object(cli, "_bind_successor_bundle", return_value=(CODE_ID, [])), \
                 patch.object(cli, "execute_strict_w1_model_stage", side_effect=AssertionError("engine reached before validation")) as engine:
                with self.assertRaises(ValueError):
                    cli._score_and_seal(args, [])
                engine.assert_not_called()

    def test_gate_rejects_wrong_run_wrong_path_and_existing_output(self):
        with tempfile.TemporaryDirectory(prefix="f02-r1-gate-test-") as temp:
            repo = Path(temp)
            for mutation in ("wrong_run", "wrong_output", "existing_output", "missing_report"):
                args = self._cli_args(repo)
                if mutation == "wrong_run":
                    args.pmo_run_id = "OTHER_RUN"
                elif mutation == "wrong_output":
                    args.output_dir = repo / "wrong-output"
                elif mutation == "existing_output":
                    args.output_dir.mkdir(parents=True)
                with self.subTest(mutation=mutation), self.assertRaises((ValueError, FileNotFoundError)):
                    cli._verify_r1_validation_gate(repo, args, self.manifest, self.manifest_hash, "1" * 64, CODE_ID, [])
                if mutation == "existing_output":
                    args.output_dir.rmdir()

    def test_seal_creation_rejects_missing_p4_gate_without_scoring(self):
        # Isolate the seal's admission guard with a deliberately incomplete payload;
        # this fixture does not execute the scorer or produce a valid seal.
        for binding in (None, {"state": "PENDING"}):
            payload = {
                "input_profile": {"scientific_state": SCIENTIFIC_STATE},
                "affected_validation_binding": binding,
            }
            with self.subTest(binding=binding), patch.object(replay, "_seal_payload", return_value=payload):
                with self.assertRaises(ValueError):
                    replay.create_selection_seal(
                        {"model_stage_state": "COMPLETED_NONEMPTY_STRICT_SCORE"},
                        sealed_at_kst="2026-09-05T18:30:00+09:00",
                    )

    def _clone_input_repo(self, root):
        paths = {item["path"] for item in self.manifest["input_profile"]["dependencies"]}
        paths.update(source["raw_storage_ref"] for source in self.manifest["sources"])
        paths.update((adapter.MANIFEST_PATH, adapter.SIDECAR_PATH))
        for relative in paths:
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(REPO / relative, target)

    def test_changed_raw_bytes_cannot_be_readmitted_by_self_rehash(self):
        with tempfile.TemporaryDirectory(prefix="f02-r1-raw-test-") as temp:
            repo = Path(temp)
            self._clone_input_repo(repo)
            manifest = copy.deepcopy(self.manifest)
            source = next(item for item in manifest["sources"] if item["company_id"] == "KRX:003160")
            path = repo / source["raw_storage_ref"]
            original = path.read_bytes()
            changed = original.replace(b"34,732,575,950", b"34,732,575,951")
            self.assertNotEqual(original, changed)
            path.write_bytes(changed)
            source["raw_artifact"]["sha256"] = hashlib.sha256(changed).hexdigest()
            source["raw_artifact"]["byte_size"] = len(changed)
            source["raw_artifact"]["git_blob"] = hashlib.sha1(f"blob {len(changed)}\0".encode() + changed).hexdigest()
            with self.assertRaises(ValueError):
                self._manifest(manifest, repo=repo)

    def test_changed_mapping_registry_cannot_be_readmitted_by_self_rehash(self):
        with tempfile.TemporaryDirectory(prefix="f02-r1-map-test-") as temp:
            repo = Path(temp)
            self._clone_input_repo(repo)
            mapping = copy.deepcopy(self.mapping)
            mapping["consumed_registry_git_blob"] = "0" * 40
            data = adapter.json_bytes(mapping)
            (repo / adapter.MAPPING_PATH).write_bytes(data)
            manifest = copy.deepcopy(self.manifest)
            manifest["input_profile"]["mapping"]["sha256"] = hashlib.sha256(data).hexdigest()
            manifest["input_profile"]["mapping"]["byte_size"] = len(data)
            for dependency in manifest["input_profile"]["dependencies"]:
                if dependency["path"] == adapter.MAPPING_PATH:
                    dependency.update(manifest["input_profile"]["mapping"])
            with self.assertRaises(ValueError):
                self._manifest(manifest, repo=repo)

    def test_parser_checks_semantics_beyond_raw_hash_gate(self):
        spec = copy.deepcopy(next(item for item in adapter.SOURCE_SPECS if item["company_id"] == "KRX:003160"))
        original = (REPO / spec["raw_storage_ref"]).read_text(encoding="utf-8")
        mutations = {
            "wrong_issuer": ("(주)디아이", "(주)다른기업"),
            "wrong_cover_issuer_only": (
                "<TD width='400' height='20' class='TD' valign='TOP'>(주)디아이</TD>",
                "<TD width='400' height='20' class='TD' valign='TOP'>(주)다른기업</TD>",
            ),
            "wrong_current_period": ("2024.01.01 부터 2024.03.31 까지", "2024.04.01 부터 2024.06.30 까지"),
            "wrong_prior_period": ("2023.01.01 부터 2023.03.31 까지", "2022.01.01 부터 2022.03.31 까지"),
            "standalone_statement": ("연결 손익계산서", "별도 손익계산서"),
            "wrong_unit": ("(단위 : 원)", "(단위 : 백만원)"),
            "cumulative_column": ("<P>3개월</P>", "<P>누적</P>"),
            "data_cells_masquerading_as_headers": ("<TH ", "<TD "),
            "wrong_metric": (">매출액</P>", ">당기순이익</P>"),
            "negative_sign_removed": ("(1,836,830,457)", "1,836,830,457"),
            "partial_numeric_match": ("34,732,575,950</P>", "34,732,575,950 extra</P>"),
            "zero_prior": ("39,216,899,579", "0"),
        }
        with tempfile.TemporaryDirectory(prefix="f02-r1-parser-test-") as temp:
            for name, (before, after) in mutations.items():
                with self.subTest(mutation=name):
                    self.assertIn(before, original)
                    fixture = Path(temp) / f"{name}.htm"
                    fixture.write_bytes(original.replace(before, after).encode("utf-8"))
                    with self.assertRaises(ValueError):
                        adapter.parse_source_html(fixture.read_bytes(), spec)

    def test_parser_rejects_wrong_public_date_and_missing_restatement_explanation(self):
        spec = copy.deepcopy(next(item for item in adapter.SOURCE_SPECS if item["company_id"] == "KRX:025560"))
        original = (REPO / spec["raw_storage_ref"]).read_text(encoding="utf-8")
        mutations = {
            "wrong_public_date": ("2024년 &nbsp;05월 &nbsp;14일", "2024년 &nbsp;08월 &nbsp;14일"),
            "missing_restatement": ("영업이익이 조정", "설명 생략"),
            "unrestated_comparator": ("(442,977,057)", "(448,371,497)"),
        }
        with tempfile.TemporaryDirectory(prefix="f02-r1-restatement-test-") as temp:
            for name, (before, after) in mutations.items():
                with self.subTest(mutation=name):
                    self.assertIn(before, original)
                    fixture = Path(temp) / f"{name}.htm"
                    fixture.write_bytes(original.replace(before, after).encode("utf-8"))
                    with self.assertRaises(ValueError):
                        adapter.parse_source_html(fixture.read_bytes(), spec)


if __name__ == "__main__":
    unittest.main()
