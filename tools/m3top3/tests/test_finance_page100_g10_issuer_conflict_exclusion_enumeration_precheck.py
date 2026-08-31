#!/usr/bin/env python3
"""Focused offline tests for G10 issuer-group exclusion PRECHECK."""

from __future__ import annotations

import ast
import copy
import datetime as dt
import json
import os
import pathlib
import unittest
from collections.abc import Callable
from typing import Any

from tools.m3top3 import (
    finance_page100_g10_issuer_conflict_exclusion_enumeration_precheck as subject,
)


ROOT = pathlib.Path(__file__).resolve().parents[3]
TARGET_CUSTODY = "7000000000001"
TARGET_CRNO = "1101110000001"
TARGET_FROZEN_NAME = "SYNTHETIC FROZEN ISSUER"
TARGET_OBSERVED_NAME = "SYNTHETIC OBSERVED ISSUER"
PREPARATION_COMMIT_SHA = "a" * 40
PREPARATION_TREE_SHA = "b" * 40
VALIDATION_TIME_UTC = dt.datetime(2026, 8, 31, 12, 35, tzinfo=dt.timezone.utc)


def authority() -> dict[str, Any]:
    return subject.load_canonical_json(ROOT / subject.AUTHORITY_PATH)


def baseline() -> dict[str, str]:
    value = authority()["baseline_identity_projection"]
    result = dict(value["identity_hashes_by_custody_sha256"])
    assert value["count"] == 12 and len(result) == 12
    assert all(subject.HASH_RE.fullmatch(key) for key in result)
    assert all(subject.HASH_RE.fullmatch(item) for item in result.values())
    return result


def target_items() -> tuple[dict[str, str], dict[str, str]]:
    frozen = {
        "basDt": subject.EXPECTED_BASE_DATE,
        "crno": TARGET_CRNO,
        "issuCmpyKsdCustNo": TARGET_CUSTODY,
        "stckIssuCmpyNm": TARGET_FROZEN_NAME,
    }
    observed = {**frozen, "stckIssuCmpyNm": TARGET_OBSERVED_NAME}
    return frozen, observed


def synthetic_items(*, extra_frozen_target: bool = False) -> list[dict[str, Any]]:
    frozen, observed = target_items()
    rows: list[dict[str, Any]] = []
    for ordinal in range(1, 41):
        item: dict[str, Any] = {
            "basDt": subject.EXPECTED_BASE_DATE,
            "crno": f"120111{ordinal:07d}",
            "issuCmpyKsdCustNo": f"8000000{ordinal:06d}",
            "stckIssuCmpyNm": f"SYNTHETIC ISSUER {ordinal:03d}",
        }
        if ordinal == 1 or (extra_frozen_target and ordinal == 2):
            item = copy.deepcopy(frozen)
        elif ordinal in subject.KNOWN_CONFLICT_GLOBAL_ORDINALS:
            item = copy.deepcopy(observed)
        rows.append(item)
    return rows


def encode_pages(
    rows: list[dict[str, Any]],
) -> tuple[list[bytes], list[dict[str, Any]]]:
    assert len(rows) == 40
    bodies: list[bytes] = []
    exact_raw_versions: list[dict[str, Any]] = []
    for page_no in range(1, 5):
        start = (page_no - 1) * 10
        entity = {
            "response": {
                "body": {
                    "items": {"item": copy.deepcopy(rows[start : start + 10])},
                    "numOfRows": "10",
                    "pageNo": str(page_no),
                    "totalCount": str(subject.EXPECTED_TOTAL_COUNT),
                },
                "header": {"resultCode": "00", "resultMsg": "NORMAL SERVICE"},
            }
        }
        body = subject.canonical_json_bytes(entity)
        bodies.append(body)
        exact_raw_versions.append(
            {
                "bytes": len(body),
                "page_no": page_no,
                "s3_object_key": f"synthetic/exact/page-{page_no}.entity",
                "sha256": subject.sha256_bytes(body),
                "version_id": f"synthetic-version-{page_no}",
            }
        )
    return bodies, exact_raw_versions


def fixture(
    *, extra_frozen_target: bool = False
) -> tuple[list[dict[str, Any]], list[bytes], list[dict[str, Any]], dict[str, str]]:
    rows = synthetic_items(extra_frozen_target=extra_frozen_target)
    bodies, exact_raw_versions = encode_pages(rows)
    frozen, observed = target_items()
    digests = {
        "frozen": subject.issuer_identity_digest(frozen),
        "observed": subject.issuer_identity_digest(observed),
        "target": subject.sha256_bytes(TARGET_CUSTODY.encode("utf-8")),
    }
    return rows, bodies, exact_raw_versions, digests


def parse_synthetic_bodies(bodies: list[bytes]) -> list[dict[str, Any]]:
    return [
        subject.parse_finance_entity(
            body,
            subject.EXPECTED_BASE_DATE,
            page_no,
            expected_page_size=10,
            expected_total_count=subject.EXPECTED_TOTAL_COUNT,
        )
        for page_no, body in enumerate(bodies, 1)
    ]


def project(
    *, extra_frozen_target: bool = False
) -> tuple[dict[str, Any], tuple[Any, ...]]:
    rows, bodies, exact_raw_versions, digests = fixture(
        extra_frozen_target=extra_frozen_target
    )
    inherited = baseline()
    inputs = (rows, bodies, exact_raw_versions, inherited, digests)
    result = subject._build_hash_only_exclusion_projection_from_verified_pages(
        parse_synthetic_bodies(bodies),
        inherited_identity_hashes_by_custody_sha256=inherited,
        target_custody_key_sha256=digests["target"],
        frozen_identity_sha256=digests["frozen"],
        observed_identity_sha256=digests["observed"],
    )
    return result, inputs


def invoke(
    rows: list[dict[str, Any]],
    digests: dict[str, str],
) -> dict[str, Any]:
    bodies, _ = encode_pages(rows)
    return subject._build_hash_only_exclusion_projection_from_verified_pages(
        parse_synthetic_bodies(bodies),
        inherited_identity_hashes_by_custody_sha256=baseline(),
        target_custody_key_sha256=digests["target"],
        frozen_identity_sha256=digests["frozen"],
        observed_identity_sha256=digests["observed"],
    )


def valid_activation(
    authority_value: dict[str, Any], manifest_value: dict[str, Any]
) -> dict[str, Any]:
    return {
        "activated_at_utc": "2026-08-31T12:34:56Z",
        "activation_id": (
            "G10-ISSUER-GROUP-EXCLUSION-ENUMERATION-PRECHECK-ACTIVATION-"
            "20260831123456"
        ),
        "armed": True,
        "artifact": subject.ACTIVATION_ARTIFACT,
        "authority_sha256": subject.sha256_bytes(
            subject.canonical_json_bytes(authority_value)
        ),
        "branch": subject.BRANCH,
        "expected_commit_message": subject.ACTIVATION_MESSAGE,
        "external_effects_authorized": {
            "aws_or_s3_calls": 0,
            "finance_provider_api_calls": 0,
            "g10_or_g11_runs": 0,
            "normalization_pit_promotion_release_production": 0,
            "provider_quota_reservations": 0,
            "remote_mutations": 0,
        },
        "fresh_runtime_and_latch": {
            "precheck_attempt_ordinal": 1,
            "prior_s4_authority_or_session_reused": False,
            "prior_s4_latch_reused": False,
            "runtime_lock_id": (
                "PMO-G10-ISSUER-GROUP-EXCLUSION-ENUMERATION-PRECHECK-"
                "20260831123456"
            ),
        },
        "manifest_sha256": subject.sha256_bytes(
            subject.canonical_json_bytes(manifest_value)
        ),
        "preparation_commit_sha": PREPARATION_COMMIT_SHA,
        "preparation_parent": {
            "decision_commit_sha": subject.PREPARATION_PARENT_HEAD_SHA,
            "decision_tree_sha": subject.PREPARATION_PARENT_TREE_SHA,
        },
        "preparation_tree_sha": PREPARATION_TREE_SHA,
        "repository": subject.REPOSITORY,
        "state": subject.ACTIVATION_STATE,
    }


class IssuerGroupExclusionPrecheckTests(unittest.TestCase):
    def assert_projection_error(
        self,
        code: str,
        rows: list[dict[str, Any]],
        digests: dict[str, str],
    ) -> None:
        with self.assertRaisesRegex(subject.ExclusionPrecheckError, code):
            invoke(rows, digests)

    def test_t1_json_four_by_ten_body_projection_and_accounting(self) -> None:
        frozen, _ = target_items()
        self.assertEqual(
            subject.issuer_identity_digest(frozen),
            "449bcbe71d0fbf03df3b0d80a684daaad88283ce5f9042b323c125d14656ce59",
        )
        result, inputs = project()
        rows, bodies, exact_raw_versions, inherited, _ = inputs
        self.assertEqual(len(rows), 40)
        self.assertEqual(len(bodies), 4)
        self.assertEqual([row["page_no"] for row in exact_raw_versions], [1, 2, 3, 4])
        self.assertEqual(len(inherited), 12)
        row_custody_hashes = {
            subject.sha256_bytes(str(row["issuCmpyKsdCustNo"]).encode("utf-8"))
            for row in rows
        }
        # The sealed S4 classifier treats a nonempty first observation as MATCH;
        # MISSING is reserved for an absent/empty custody key.
        self.assertTrue(row_custody_hashes.isdisjoint(inherited))
        self.assertEqual(
            result["sealed_source_pre_exclusion"],
            {"conflict_rows": 2, "match_rows": 38, "missing_rows": 0, "rows": 40},
        )
        self.assertEqual(
            result["partition_accounting"],
            {
                "eligible_match_rows": 37,
                "excluded_conflict_occurrences": 2,
                "excluded_prior_matching_occurrences": 1,
                "excluded_total_occurrences": 3,
                "missing_rows": 0,
                "source_rows": 40,
            },
        )
        self.assertEqual(
            [row["global_row_ordinal"] for row in result["target_occurrences"]],
            [1, 37, 39],
        )

    def test_t2_company_wide_exclusion_removes_every_prior_match(self) -> None:
        result, _ = project(extra_frozen_target=True)
        accounting = result["partition_accounting"]
        self.assertEqual(accounting["excluded_prior_matching_occurrences"], 2)
        self.assertEqual(accounting["excluded_conflict_occurrences"], 2)
        self.assertEqual(accounting["excluded_total_occurrences"], 4)
        self.assertEqual(accounting["eligible_match_rows"], 36)
        self.assertEqual(result["eligible_projection"]["target_selector_occurrences"], 0)

    def test_t3_non_target_conflict_fails_before_filter_accounting(self) -> None:
        rows, _, _, digests = fixture()
        rows[2]["issuCmpyKsdCustNo"] = rows[1]["issuCmpyKsdCustNo"]
        rows[2]["crno"] = rows[1]["crno"]
        rows[2]["stckIssuCmpyNm"] = "NON TARGET CONFLICT"
        self.assert_projection_error("NON_TARGET_CONFLICT_REMAINS", rows, digests)

    def test_t4_raw_body_and_binding_mutations_fail_closed(self) -> None:
        _, bodies, exact_raw_versions, digests = fixture()
        with self.assertRaisesRegex(
            subject.ExclusionPrecheckError,
            "RAW_VERSION_AUTHORITY_BINDING_MISMATCH",
        ):
            subject.build_hash_only_exclusion_projection(
                bodies,
                exact_raw_versions=exact_raw_versions,
                inherited_identity_hashes_by_custody_sha256=baseline(),
                target_custody_key_sha256=digests["target"],
                frozen_identity_sha256=digests["frozen"],
                observed_identity_sha256=digests["observed"],
            )

        incomplete_official_bindings = [
            {
                "bytes": row["bytes"],
                "page_no": row["page_no"],
                "sha256": row["sha256"],
            }
            for row in subject.EXPECTED_EXACT_RAW_VERSIONS
        ]
        with self.assertRaisesRegex(
            subject.ExclusionPrecheckError,
            "RAW_VERSION_AUTHORITY_BINDING_MISMATCH",
        ):
            subject.build_hash_only_exclusion_projection(
                bodies,
                exact_raw_versions=incomplete_official_bindings,
                inherited_identity_hashes_by_custody_sha256=baseline(),
                target_custody_key_sha256=subject.TARGET_CUSTODY_KEY_SHA256,
                frozen_identity_sha256=subject.FROZEN_IDENTITY_SHA256,
                observed_identity_sha256=subject.OBSERVED_IDENTITY_SHA256,
            )

        with self.assertRaisesRegex(
            subject.ExclusionPrecheckError, "RAW_BODY_BINDING_MISMATCH"
        ):
            subject.build_hash_only_exclusion_projection(
                bodies,
                exact_raw_versions=list(subject.EXPECTED_EXACT_RAW_VERSIONS),
                inherited_identity_hashes_by_custody_sha256=baseline(),
                target_custody_key_sha256=subject.TARGET_CUSTODY_KEY_SHA256,
                frozen_identity_sha256=subject.FROZEN_IDENTITY_SHA256,
                observed_identity_sha256=subject.OBSERVED_IDENTITY_SHA256,
            )

        mutated_baseline = baseline()
        first_key = next(iter(mutated_baseline))
        mutated_baseline[first_key] = "0" * 64
        with self.assertRaisesRegex(
            subject.ExclusionPrecheckError, "BASELINE_AUTHORITY_BINDING_MISMATCH"
        ):
            subject._build_hash_only_exclusion_projection_from_verified_pages(
                parse_synthetic_bodies(bodies),
                inherited_identity_hashes_by_custody_sha256=mutated_baseline,
                target_custody_key_sha256=digests["target"],
                frozen_identity_sha256=digests["frozen"],
                observed_identity_sha256=digests["observed"],
            )

    def test_t5_item_base_date_drift_fails_with_valid_body_binding(self) -> None:
        rows, _, _, digests = fixture()
        rows[4]["basDt"] = "20240130"
        self.assert_projection_error("ITEM_BASE_DATE_MISMATCH", rows, digests)

    def test_t6_custody_type_and_whitespace_fail_closed(self) -> None:
        for replacement, code in (
            (8000000000002, "CUSTODY_TYPE_INVALID"),
            (" 8000000000002 ", "CUSTODY_FORMAT_INVALID"),
            ("   ", "CUSTODY_FORMAT_INVALID"),
        ):
            with self.subTest(replacement=repr(replacement)):
                rows, _, _, digests = fixture()
                rows[1]["issuCmpyKsdCustNo"] = replacement
                self.assert_projection_error(code, rows, digests)

    def test_t7_output_allowlist_clear_scan_immutability_and_determinism(self) -> None:
        rows, bodies, exact_raw_versions, digests = fixture()
        inherited = baseline()
        before = copy.deepcopy((bodies, exact_raw_versions, inherited))
        kwargs = {
            "inherited_identity_hashes_by_custody_sha256": inherited,
            "target_custody_key_sha256": digests["target"],
            "frozen_identity_sha256": digests["frozen"],
            "observed_identity_sha256": digests["observed"],
        }
        pages = parse_synthetic_bodies(bodies)
        first = subject._build_hash_only_exclusion_projection_from_verified_pages(
            pages, **kwargs
        )
        second = subject._build_hash_only_exclusion_projection_from_verified_pages(
            pages, **kwargs
        )
        self.assertEqual(first, second)
        self.assertEqual((bodies, exact_raw_versions, inherited), before)

        self.assertEqual(
            set(first),
            {
                "artifact",
                "basDt",
                "clear_issuer_values_persisted",
                "company_master_or_universe_mutated",
                "eligible_projection",
                "final_hash_only_identity_map",
                "issuer_identity_selected",
                "partition_accounting",
                "sealed_source_pre_exclusion",
                "selector",
                "target_occurrences",
            },
        )
        self.assertEqual(
            set(first["eligible_projection"]),
            {"row_count", "sha256", "target_selector_occurrences"},
        )
        self.assertEqual(
            set(first["partition_accounting"]),
            {
                "eligible_match_rows",
                "excluded_conflict_occurrences",
                "excluded_prior_matching_occurrences",
                "excluded_total_occurrences",
                "missing_rows",
                "source_rows",
            },
        )
        self.assertEqual(
            set(first["sealed_source_pre_exclusion"]),
            {"conflict_rows", "match_rows", "missing_rows", "rows"},
        )
        self.assertEqual(
            set(first["final_hash_only_identity_map"]), {"count", "sha256"}
        )
        self.assertEqual(
            set(first["selector"]), {"algorithm", "custody_key_sha256", "scope"}
        )
        target_keys = {
            "basDt",
            "custody_key_sha256",
            "disposition",
            "global_row_ordinal",
            "identity_class",
            "observed_identity_sha256",
            "page_item_ordinal",
            "page_no",
            "source_classification",
        }
        self.assertTrue(first["target_occurrences"])
        self.assertTrue(
            all(set(item) == target_keys for item in first["target_occurrences"])
        )

        serialized = json.dumps(first, ensure_ascii=False, sort_keys=True)
        clear_values = {
            str(row[key])
            for row in rows
            for key in subject.CLEAR_IDENTITY_KEYS
            if str(row[key])
        }
        self.assertTrue(clear_values)
        self.assertTrue(all(value not in serialized for value in clear_values))
        self.assertTrue(all(key not in serialized for key in subject.CLEAR_IDENTITY_KEYS))
        self.assertFalse(first["issuer_identity_selected"])
        self.assertFalse(first["company_master_or_universe_mutated"])

    def test_t8_activation_strict_schema_binding_and_freshness_negatives(self) -> None:
        authority_value = authority()
        manifest_value = subject.load_canonical_json(ROOT / subject.MANIFEST_PATH)
        activation = valid_activation(authority_value, manifest_value)
        subject.validate_activation(
            activation,
            authority_value,
            manifest_value,
            expected_preparation_commit_sha=PREPARATION_COMMIT_SHA,
            expected_preparation_tree_sha=PREPARATION_TREE_SHA,
            validation_time_utc=VALIDATION_TIME_UTC,
        )

        cases: tuple[tuple[str, Callable[[dict[str, Any]], None], str], ...] = (
            (
                "wrong_artifact",
                lambda value: value.update(artifact="WRONG"),
                "ACTIVATION_ARTIFACT_INVALID",
            ),
            (
                "not_armed",
                lambda value: value.update(armed=False),
                "ACTIVATION_NOT_ARMED",
            ),
            (
                "template_state",
                lambda value: value.update(state="TEMPLATE_NOT_AUTHORITY_NOT_ARMED"),
                "ACTIVATION_STATE_INVALID",
            ),
            (
                "placeholder_id",
                lambda value: value.update(activation_id="REPLACE_WITH_FRESH_ACTIVATION_ID"),
                "ACTIVATION_ID_INVALID",
            ),
            (
                "bad_timestamp",
                lambda value: value.update(activated_at_utc="REPLACE_WITH_ACTIVATION_TIMESTAMP"),
                "ACTIVATION_TIMESTAMP_INVALID",
            ),
            (
                "impossible_calendar",
                lambda value: (
                    value.update(
                        activated_at_utc="2026-99-99T99:99:99Z",
                        activation_id=(
                            "G10-ISSUER-GROUP-EXCLUSION-ENUMERATION-PRECHECK-"
                            "ACTIVATION-20269999999999"
                        ),
                    ),
                    value["fresh_runtime_and_latch"].update(
                        runtime_lock_id=(
                            "PMO-G10-ISSUER-GROUP-EXCLUSION-ENUMERATION-PRECHECK-"
                            "20269999999999"
                        )
                    ),
                ),
                "ACTIVATION_TIMESTAMP_INVALID",
            ),
            (
                "stale_timestamp",
                lambda value: (
                    value.update(
                        activated_at_utc="2026-08-01T12:34:56Z",
                        activation_id=(
                            "G10-ISSUER-GROUP-EXCLUSION-ENUMERATION-PRECHECK-"
                            "ACTIVATION-20260801123456"
                        ),
                    ),
                    value["fresh_runtime_and_latch"].update(
                        runtime_lock_id=(
                            "PMO-G10-ISSUER-GROUP-EXCLUSION-ENUMERATION-PRECHECK-"
                            "20260801123456"
                        )
                    ),
                ),
                "ACTIVATION_TIMESTAMP_NOT_FRESH",
            ),
            (
                "id_timestamp_mismatch",
                lambda value: value.update(
                    activation_id=(
                        "G10-ISSUER-GROUP-EXCLUSION-ENUMERATION-PRECHECK-"
                        "ACTIVATION-20260831123457"
                    )
                ),
                "ACTIVATION_ID_TIMESTAMP_MISMATCH",
            ),
            (
                "wrong_preparation_commit",
                lambda value: value.update(preparation_commit_sha="c" * 40),
                "ACTIVATION_PREPARATION_COMMIT_MISMATCH",
            ),
            (
                "wrong_preparation_tree",
                lambda value: value.update(preparation_tree_sha="d" * 40),
                "ACTIVATION_PREPARATION_TREE_MISMATCH",
            ),
            (
                "prior_latch_reuse",
                lambda value: value["fresh_runtime_and_latch"].update(
                    prior_s4_latch_reused=True
                ),
                "ACTIVATION_FRESH_RUNTIME_OR_LATCH_INVALID",
            ),
            (
                "prior_s4_session_reuse",
                lambda value: value["fresh_runtime_and_latch"].update(
                    prior_s4_authority_or_session_reused=True
                ),
                "ACTIVATION_FRESH_RUNTIME_OR_LATCH_INVALID",
            ),
            (
                "placeholder_runtime",
                lambda value: value["fresh_runtime_and_latch"].update(
                    runtime_lock_id="REPLACE_WITH_FRESH_RUNTIME_LOCK_ID"
                ),
                "ACTIVATION_FRESH_RUNTIME_OR_LATCH_INVALID",
            ),
            (
                "runtime_timestamp_mismatch",
                lambda value: value["fresh_runtime_and_latch"].update(
                    runtime_lock_id=(
                        "PMO-G10-ISSUER-GROUP-EXCLUSION-ENUMERATION-PRECHECK-"
                        "20260831123457"
                    )
                ),
                "ACTIVATION_RUNTIME_TIMESTAMP_MISMATCH",
            ),
            (
                "nonzero_external_effect",
                lambda value: value["external_effects_authorized"].update(
                    aws_or_s3_calls=1
                ),
                "ACTIVATION_EFFECT_CEILING_INVALID",
            ),
            (
                "boolean_zero_external_effect",
                lambda value: value["external_effects_authorized"].update(
                    aws_or_s3_calls=False
                ),
                "ACTIVATION_EFFECT_CEILING_INVALID",
            ),
            (
                "boolean_attempt_ordinal",
                lambda value: value["fresh_runtime_and_latch"].update(
                    precheck_attempt_ordinal=True
                ),
                "ACTIVATION_FRESH_RUNTIME_OR_LATCH_INVALID",
            ),
            (
                "extra_clear_key",
                lambda value: value.update(stckIssuCmpyNm="PROHIBITED"),
                "ACTIVATION_SCHEMA_INVALID",
            ),
        )
        for name, mutate, code in cases:
            with self.subTest(name=name):
                candidate = copy.deepcopy(activation)
                mutate(candidate)
                with self.assertRaisesRegex(subject.ExclusionPrecheckError, code):
                    subject.validate_activation(
                        candidate,
                        authority_value,
                        manifest_value,
                        expected_preparation_commit_sha=PREPARATION_COMMIT_SHA,
                        expected_preparation_tree_sha=PREPARATION_TREE_SHA,
                        validation_time_utc=VALIDATION_TIME_UTC,
                    )

    def test_t9_bundle_validation_and_unarmed_preparation_boundary(self) -> None:
        authority_value = authority()
        manifest_value = subject.load_canonical_json(ROOT / subject.MANIFEST_PATH)
        subject.validate_preparation_bundle(
            ROOT,
            authority_value,
            manifest_value,
            allow_missing_predecessor_checkpoint_for_local_test=True,
        )
        boolean_effect_authority = copy.deepcopy(authority_value)
        boolean_effect_authority["effect_ceiling"]["aws_or_s3_calls"] = False
        with self.assertRaisesRegex(
            subject.ExclusionPrecheckError, "PRECHECK_EFFECT_CEILING_INVALID"
        ):
            subject.validate_preparation_bundle(
                ROOT,
                boolean_effect_authority,
                manifest_value,
                allow_missing_predecessor_checkpoint_for_local_test=True,
            )
        activation_path = ROOT / subject.ACTIVATION_PATH
        if os.environ.get("EXPECT_ACTIVATION_PRESENT") == "1":
            self.assertTrue(activation_path.is_file())
            expected_commit = os.environ.get("EXPECTED_PREPARATION_COMMIT", "")
            expected_tree = os.environ.get("EXPECTED_PREPARATION_TREE", "")
            self.assertRegex(expected_commit, r"^[0-9a-f]{40}$")
            self.assertRegex(expected_tree, r"^[0-9a-f]{40}$")
            subject.validate_activation(
                subject.load_canonical_json(activation_path),
                authority_value,
                manifest_value,
                expected_preparation_commit_sha=expected_commit,
                expected_preparation_tree_sha=expected_tree,
            )
        else:
            self.assertFalse(activation_path.exists())
            template = subject.load_canonical_json(
                ROOT / subject.ACTIVATION_TEMPLATE_PATH
            )
            self.assertFalse(template["armed"])
            self.assertEqual(template["state"], "TEMPLATE_NOT_AUTHORITY_NOT_ARMED")
        self.assertEqual(
            len(authority_value["baseline_identity_projection"][
                "identity_hashes_by_custody_sha256"
            ]),
            12,
        )

    def test_t10_runner_and_test_have_no_frozen_core_or_external_effect_imports(self) -> None:
        runner = ROOT / subject.RUNNER_PATH
        test_file = ROOT / subject.TEST_PATH
        forbidden_module = "finance_page100_g10_forensic_" + "s4_core"
        for path in (runner, test_file):
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source)
            imported_modules = {
                alias.name
                for node in ast.walk(tree)
                if isinstance(node, ast.Import)
                for alias in node.names
            }
            imported_modules.update(
                str(node.module)
                for node in ast.walk(tree)
                if isinstance(node, ast.ImportFrom) and node.module
            )
            self.assertTrue(
                all(forbidden_module not in module for module in imported_modules)
            )

        source = runner.read_text(encoding="utf-8")
        tree = ast.parse(source)
        imports = {
            alias.name.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        }
        imports.update(
            str(node.module).split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module
        )
        self.assertTrue(
            {"boto3", "os", "requests", "subprocess", "urllib"}.isdisjoint(imports)
        )

        workflow = (ROOT / subject.WORKFLOW_PATH).read_text(encoding="utf-8").lower()
        for forbidden in (
            "configure-aws-credentials",
            "id-token: write",
            "upload-artifact",
            "aws ",
            "curl ",
            "gh api",
            "servicekey",
        ):
            self.assertNotIn(forbidden, workflow)


if __name__ == "__main__":
    unittest.main()
