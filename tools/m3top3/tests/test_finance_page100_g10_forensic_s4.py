#!/usr/bin/env python3
"""Owner-authorized affected-scope tests T1-T10 for G10 forensic S4."""

from __future__ import annotations

import ast
import copy
import json
import os
import pathlib
import tempfile
import types
import unittest
from collections.abc import Mapping, Sequence
from typing import Any
from unittest import mock

import yaml

from tools.m3top3 import finance_page100_g10_forensic_s4 as s4


ROOT = pathlib.Path(__file__).resolve().parents[3]
CORE = ROOT / s4.CORRECTED_CORE_PATH
WORKFLOW_PATHS = (s4.PRECHECK_WORKFLOW_PATH, s4.AUDIT_WORKFLOW_PATH)
WORKFLOWS = [ROOT / path for path in WORKFLOW_PATHS]
POLICIES = {
    "PRECHECK": ROOT / s4.PRECHECK_POLICY_PATH,
    "AUDIT": ROOT / s4.AUDIT_POLICY_PATH,
}
TEMPLATES = (ROOT / s4.PRECHECK_TEMPLATE_PATH, ROOT / s4.AUDIT_TEMPLATE_PATH)

EXPECTED_HISTORY_KEYS = {
    "raw",
    "control",
    "execution_claim",
    "all_delete_marker_counts",
}
EXPECTED_COUNT_KEYS = {"raw", "control", "execution_claim"}
EXPECTED_EVENT_ENV = {
    "EVENT_ACTOR": "${{ github.actor }}",
    "EVENT_TRIGGERING_ACTOR": "${{ github.triggering_actor }}",
    "EVENT_REPOSITORY": "${{ github.repository }}",
    "EVENT_REF": "${{ github.ref }}",
    "EVENT_BEFORE": "${{ github.event.before }}",
    "EVENT_AFTER": "${{ github.event.after }}",
    "EVENT_FORCED": "${{ github.event.forced }}",
    "EVENT_HEAD_MESSAGE": "${{ github.event.head_commit.message }}",
    "EVENT_RUN_ATTEMPT": "${{ github.run_attempt }}",
}


def canonical(path: pathlib.Path) -> dict[str, Any]:
    raw = path.read_bytes()
    value = json.loads(raw)
    assert raw == s4.canonical_json_bytes(value)
    return value


def recursive_exact_key_count(value: Any, target: str) -> int:
    if isinstance(value, Mapping):
        return sum(key == target for key in value) + sum(
            recursive_exact_key_count(child, target) for child in value.values()
        )
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return sum(recursive_exact_key_count(child, target) for child in value)
    return 0


def synthetic_histories() -> dict[str, Any]:
    raw_versions = [
        {"key": row["s3_object_key"], "version_id": row["version_id"]}
        for row in s4.EXACT_RAW_VERSIONS
    ]
    control_versions = [
        {"key": s4.frozen.CHECKPOINT_KEY, "version_id": f"checkpoint-version-{i:02d}"}
        for i in range(28)
    ]
    claim_versions = [
        {"key": s4.frozen.CLAIM_KEY, "version_id": s4.EXACT_CLAIM_VERSION_ID}
    ]
    return {
        "raw": {"versions": raw_versions, "delete_markers": []},
        "control": {"versions": control_versions, "delete_markers": []},
        "execution_claim": {"versions": claim_versions, "delete_markers": []},
        "all_delete_marker_counts": {
            "raw": 0,
            "control": 0,
            "execution_claim": 0,
        },
    }


def synthetic_evidence() -> dict[str, Any]:
    return {
        "artifact": "SYNTHETIC_CORRECTED_CORE_EVIDENCE",
        "aws_read_only_session": {
            "aws_cli_read_call_counts": {
                "s3api:get-object": 33,
                "s3api:list-object-versions": 3,
                "sts:get-caller-identity": 1,
            },
            "caller_arn_sha256": "0" * 64,
        },
        "checkpoint_versions": [
            {"revision": i, "version_id": f"checkpoint-version-{i:02d}"}
            for i in range(28)
        ],
        "claim_ceiling": {
            "model_semantic_change": False,
            "pit_semantic_change": False,
            "evidence_semantic_change": False,
            "validation_claim": "NONE",
            "production_authority": False,
        },
        "effect_classification": {
            "finance_provider_api_calls": 0,
            "quota_reservations": 0,
            "s3_put_object_calls": 0,
            "s3_delete_object_calls": 0,
            "remote_custody_mutations": 0,
            "aws_read_only_session_established": 1,
            "raw_exact_version_gets": 4,
            "checkpoint_exact_version_gets": 28,
            "execution_claim_exact_version_gets": 1,
            "normalization_records": 0,
            "promotion_actions": 0,
        },
        "issuer_identity_replay": {
            "rows_checked": 40,
            "match_rows": 38,
            "conflict_rows": 2,
            "missing_rows": 0,
            "conflict_rows_exact": [],
        },
        "version_histories": synthetic_histories(),
    }


def readback(key: str, version_id: str) -> dict[str, Any]:
    return {
        "bytes": 1,
        "content_type": "application/json",
        "etag": "synthetic-etag",
        "key": key,
        "server_side_encryption": "AES256",
        "sha256": "1" * 64,
        "version_id": version_id,
    }


class G10ForensicS4FocusedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.workflow_texts = [path.read_text(encoding="utf-8") for path in WORKFLOWS]
        cls.workflows = [
            yaml.load(text, Loader=yaml.BaseLoader) for text in cls.workflow_texts
        ]
        cls.core_text = CORE.read_text(encoding="utf-8")
        cls.evidence = synthetic_evidence()
        cls.artifact_temp: tempfile.TemporaryDirectory[str] | None = None
        cls.artifact_dir: pathlib.Path | None = None
        cls.artifacts: dict[str, dict[str, Any]] = {}
        cls.core_receipt: dict[str, Any] = {}

    @classmethod
    def tearDownClass(cls) -> None:
        if cls.artifact_temp is not None:
            cls.artifact_temp.cleanup()

    @classmethod
    def _steps(cls) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for workflow in cls.workflows:
            for job in workflow["jobs"].values():
                rows.extend(job["steps"])
        return rows

    @classmethod
    def _ensure_complete_synthetic_artifact(cls) -> pathlib.Path:
        if cls.artifact_dir is not None:
            return cls.artifact_dir

        evidence = copy.deepcopy(cls.evidence)
        evidence_bytes = s4.canonical_json_bytes(evidence)
        core_receipt = {
            "artifact": "SYNTHETIC_CORRECTED_CORE_RUN_RECEIPT",
            "evidence": {
                "bytes": len(evidence_bytes),
                "filename": "g10-readonly-forensic-evidence.json",
                "sha256": s4.sha256_bytes(evidence_bytes),
            },
            "state": "PASS",
        }
        core_receipt_bytes = s4.canonical_json_bytes(core_receipt)

        raw_readbacks = [
            readback(row["s3_object_key"], row["version_id"])
            for row in s4.EXACT_RAW_VERSIONS
        ]
        checkpoint_readbacks = [
            readback(s4.frozen.CHECKPOINT_KEY, f"checkpoint-version-{i:02d}")
            for i in range(28)
        ]
        claim_readbacks = [
            readback(s4.frozen.CLAIM_KEY, s4.EXACT_CLAIM_VERSION_ID)
        ]
        all_readbacks = raw_readbacks + checkpoint_readbacks + claim_readbacks
        all_pairs = {(row["key"], row["version_id"]) for row in all_readbacks}
        fake_client = types.SimpleNamespace(
            readbacks=all_readbacks,
            _listed_prefixes={
                s4.frozen.RAW_PREFIX,
                s4.frozen.CONTROL_PREFIX,
                s4.frozen.CLAIM_KEY,
            },
            _listed_pairs=all_pairs,
            _read_pairs=set(all_pairs),
        )

        def fake_core_run(
            _old_authority: Mapping[str, Any],
            _old_activation: Mapping[str, Any],
            _receipt: Mapping[str, Any],
            _predecessor: Mapping[str, Any],
            _git_lineage: Mapping[str, str],
            output_dir: pathlib.Path,
        ) -> dict[str, Any]:
            s4.BoundedCorrectedAwsReadOnlyS3.last_instance = fake_client
            s4.write_canonical_json(
                output_dir / "g10-readonly-forensic-evidence.json", evidence
            )
            s4.write_canonical_json(
                output_dir / "g10-readonly-forensic-run-receipt.json", core_receipt
            )
            s4.write_canonical_json(
                output_dir / "sanitization-receipt.json",
                {
                    "files": {
                        "g10-readonly-forensic-evidence.json": {
                            "bytes": len(evidence_bytes),
                            "sha256": s4.sha256_bytes(evidence_bytes),
                        },
                        "g10-readonly-forensic-run-receipt.json": {
                            "bytes": len(core_receipt_bytes),
                            "sha256": s4.sha256_bytes(core_receipt_bytes),
                        },
                    },
                    "state": "PASS",
                },
            )
            return copy.deepcopy(core_receipt)

        authority = {
            "aws_read_only_scope": {
                "oidc_trust_binding": {"repository": s4.REPOSITORY}
            },
            "corrected_forensic_core": {
                "path": s4.CORRECTED_CORE_PATH,
                "semantic_delta": "NESTED_NAMESPACE_ONLY",
            },
            "current_owner_authorization": {"state": "AUTHORIZED"},
            "execution_bindings": {"audit_policy": {"mode": "READ_ONLY"}},
        }
        activation = {"audit_attempt_latch": s4._attempt_latch("AUDIT")}
        git_lineage = {"activation_head_sha": "a" * 40}
        precheck_binding = {"artifact_id": 1, "run_id": 1}
        precheck_receipt_bytes = s4.canonical_json_bytes(
            {
                "artifact": "M3TOP3_FINANCE_CA_PAGE100_G10_FORENSIC_S4_PRECHECK_RECEIPT_v1.0",
                "audit_attempt_latch": s4._attempt_latch("PRECHECK"),
                "current_owner_authorization": authority[
                    "current_owner_authorization"
                ],
                "generation_id": s4.GENERATION_ID,
                "precheck_act_id": s4.PRECHECK_ACT_ID,
                "runtime_lock_id": s4.RUNTIME_LOCK_ID,
                "state": "PASS_ZERO_EFFECT_READ_ONLY_PRECHECK",
            }
        )

        temp = tempfile.TemporaryDirectory(prefix="g10-s4-focused-")
        output_dir = pathlib.Path(temp.name) / "audit-artifact"
        cls.artifact_temp = temp
        try:
            with (
                mock.patch.object(
                    s4,
                    "validate_frozen_base",
                    return_value=({}, {}, {}, {}, {}),
                ),
                mock.patch.object(s4.frozen, "run_audit", side_effect=fake_core_run),
                mock.patch.object(
                    s4.subprocess,
                    "run",
                    side_effect=AssertionError("network or AWS subprocess is unreachable"),
                ),
                mock.patch.dict(
                    os.environ,
                    {
                        "GITHUB_JOB": "audit",
                        "GITHUB_RUN_ATTEMPT": "1",
                        "GITHUB_RUN_ID": "4242",
                    },
                    clear=True,
                ),
            ):
                s4.run_audit_projection(
                    authority,
                    activation,
                    git_lineage,
                    output_dir,
                    precheck_binding,
                    precheck_receipt_bytes,
                )
        except Exception:
            temp.cleanup()
            cls.artifact_temp = None
            raise

        cls.artifact_dir = output_dir
        cls.artifacts = {
            path.name: s4.load_canonical_json(path)
            for path in sorted(output_dir.iterdir())
        }
        cls.core_receipt = core_receipt
        return output_dir

    def test_T1_version_histories_has_exact_children(self) -> None:
        histories = self.evidence["version_histories"]
        self.assertEqual(set(histories), EXPECTED_HISTORY_KEYS)
        self.assertEqual(set(histories), set(s4.VERSION_HISTORY_KEYS))

    def test_T2_delete_marker_counts_has_exact_nested_keys(self) -> None:
        counts = self.evidence["version_histories"]["all_delete_marker_counts"]
        self.assertEqual(set(counts), EXPECTED_COUNT_KEYS)
        self.assertEqual(set(counts), set(s4.DELETE_MARKER_COUNT_KEYS))

    def test_T3_obsolete_claim_key_absent_recursively(self) -> None:
        histories = self.evidence["version_histories"]
        self.assertEqual(recursive_exact_key_count(histories, "claim"), 0)
        obsolete = copy.deepcopy(histories)
        obsolete["all_delete_marker_counts"]["claim"] = 0
        del obsolete["all_delete_marker_counts"]["execution_claim"]
        with self.assertRaisesRegex(s4.S4ForensicError, "CONTROL_LOOP_DETECTED"):
            s4.validate_version_history_projection(
                obsolete, require_zero_delete_markers=True
            )

    def test_T4_zero_delete_marker_counts(self) -> None:
        histories = self.evidence["version_histories"]
        self.assertEqual(
            s4.validate_version_history_projection(
                histories, require_zero_delete_markers=True
            ),
            {"control": 0, "execution_claim": 0, "raw": 0},
        )
        for name in EXPECTED_COUNT_KEYS:
            self.assertEqual(histories[name]["delete_markers"], [])

    def test_T5_nonzero_counts_are_independent_and_live_rejected(self) -> None:
        prefixes = {
            "raw": s4.frozen.RAW_PREFIX,
            "control": s4.frozen.CONTROL_PREFIX,
            "execution_claim": s4.frozen.CLAIM_KEY,
        }
        for name in sorted(EXPECTED_COUNT_KEYS):
            with self.subTest(name=name):
                histories = copy.deepcopy(self.evidence["version_histories"])
                histories[name]["delete_markers"] = [
                    {"key": prefixes[name], "version_id": "synthetic-delete-marker"}
                ]
                histories["all_delete_marker_counts"][name] = 1
                expected = {"control": 0, "execution_claim": 0, "raw": 0}
                expected[name] = 1
                self.assertEqual(
                    s4.validate_version_history_projection(
                        histories, require_zero_delete_markers=False
                    ),
                    expected,
                )
                with self.assertRaisesRegex(
                    s4.S4ForensicError, "AUDIT_DELETE_MARKER_PRESENT"
                ):
                    s4.validate_version_history_projection(
                        histories, require_zero_delete_markers=True
                    )

                client = s4.BoundedCorrectedAwsReadOnlyS3(s4.BUCKET)
                marker_key = (
                    s4.frozen.CLAIM_KEY
                    if name == "execution_claim"
                    else prefixes[name] + "synthetic-delete-marker"
                )
                client.aws_json = mock.Mock(
                    return_value={
                        "DeleteMarkers": [
                            {"Key": marker_key, "VersionId": "synthetic-marker-v1"}
                        ],
                        "IsTruncated": False,
                        "Versions": [],
                    }
                )
                with self.assertRaisesRegex(
                    s4.S4ForensicError, "AUDIT_DELETE_MARKER_PROHIBITED"
                ):
                    client.list_versions(prefixes[name])

    def test_T6_corrected_core_and_wrapper_keysets_match(self) -> None:
        tree = ast.parse(self.core_text)
        candidates: list[tuple[set[str], set[str]]] = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.Dict):
                continue
            for key, value in zip(node.keys, node.values, strict=True):
                if not (
                    isinstance(key, ast.Constant)
                    and key.value == "version_histories"
                    and isinstance(value, ast.Dict)
                ):
                    continue
                outer = {
                    child.value
                    for child in value.keys
                    if isinstance(child, ast.Constant) and isinstance(child.value, str)
                }
                nested: set[str] = set()
                for child_key, child_value in zip(
                    value.keys, value.values, strict=True
                ):
                    if (
                        isinstance(child_key, ast.Constant)
                        and child_key.value == "all_delete_marker_counts"
                        and isinstance(child_value, ast.Dict)
                    ):
                        nested = {
                            item.value
                            for item in child_value.keys
                            if isinstance(item, ast.Constant)
                            and isinstance(item.value, str)
                        }
                candidates.append((outer, nested))
        self.assertEqual(candidates, [(EXPECTED_HISTORY_KEYS, EXPECTED_COUNT_KEYS)])
        self.assertEqual(candidates[0][0], set(s4.VERSION_HISTORY_KEYS))
        self.assertEqual(candidates[0][1], set(s4.DELETE_MARKER_COUNT_KEYS))
        self.assertNotIn(s4.OBSOLETE_PROJECTION_LINE, CORE.read_bytes())
        self.assertEqual(CORE.read_bytes().count(s4.CORRECTED_PROJECTION_LINE), 1)

    def test_T7_complete_mocked_production_wrapper_emits_exact_ten_files(self) -> None:
        output_dir = self._ensure_complete_synthetic_artifact()
        self.assertEqual(len(list(output_dir.iterdir())), 10)
        self.assertEqual({path.name for path in output_dir.iterdir()}, s4.AUDIT_OUTPUT_NAMES)
        self.assertEqual(set(self.artifacts), set(s4.AUDIT_OUTPUT_NAMES))
        self.assertEqual(
            self.artifacts["terminal-summary.json"]["state"],
            "TERMINAL_SUCCESS_READ_ONLY_FORENSIC_OBJECTIVE_COMPLETE",
        )

    def test_T8_artifact_is_canonical_sanitized_hashed_and_accepted(self) -> None:
        output_dir = self._ensure_complete_synthetic_artifact()
        for path in output_dir.iterdir():
            raw = path.read_bytes()
            self.assertTrue(raw.endswith(b"\n"))
            self.assertFalse(raw.endswith(b"\n\n"))
            self.assertEqual(raw, s4.canonical_json_bytes(json.loads(raw)))
            s4._scan_bytes(raw, [])

        scan = self.artifacts["exact-secret-scan.json"]
        self.assertEqual(scan["state"], "PASS")
        self.assertEqual(scan["target_file_names"], sorted(s4.AUDIT_OUTPUT_NAMES))
        sanitization = self.artifacts["sanitization-receipt.json"]
        self.assertEqual(sanitization["state"], "PASS")
        self.assertEqual(
            set(sanitization["files"]),
            set(s4.AUDIT_OUTPUT_NAMES) - {"sanitization-receipt.json"},
        )
        for name, binding in sanitization["files"].items():
            data = (output_dir / name).read_bytes()
            self.assertEqual(
                binding,
                {"bytes": len(data), "sha256": s4.sha256_bytes(data)},
            )

        terminal = self.artifacts["terminal-summary.json"]
        core_bindings = terminal["corrected_core_output_bindings"]
        evidence_bytes = s4.canonical_json_bytes(self.evidence)
        receipt_bytes = s4.canonical_json_bytes(self.core_receipt)
        self.assertEqual(
            core_bindings,
            {
                "evidence": {
                    "bytes": len(evidence_bytes),
                    "filename": "g10-readonly-forensic-evidence.json",
                    "sha256": s4.sha256_bytes(evidence_bytes),
                },
                "run_receipt": {
                    "bytes": len(receipt_bytes),
                    "filename": "g10-readonly-forensic-run-receipt.json",
                    "sha256": s4.sha256_bytes(receipt_bytes),
                },
            },
        )
        self.assertEqual(
            terminal["findings"]["delete_marker_counts"],
            {"control": 0, "execution_claim": 0, "raw": 0},
        )
        self.assertEqual(recursive_exact_key_count(self.artifacts, "claim"), 0)

    def test_T9_read_only_policies_caps_and_subordinate_lineage(self) -> None:
        expected_actions = {
            "PRECHECK": s4.PRECHECK_POLICY_ACTIONS,
            "AUDIT": s4.AUDIT_POLICY_ACTIONS,
        }
        for mode, path in POLICIES.items():
            policy = canonical(path)
            s4.validate_policy(policy, mode)
            actions: set[str] = set()
            for statement in policy["Statement"]:
                raw_actions = statement["Action"]
                actions.update(
                    raw_actions if isinstance(raw_actions, list) else [raw_actions]
                )
            self.assertEqual(actions, expected_actions[mode])
            self.assertFalse(any("*" in action for action in actions))
            self.assertFalse(
                any(
                    fragment in action
                    for action in actions
                    for fragment in s4.BANNED_ACTION_FRAGMENTS
                )
            )
            workflow = self.workflows[0 if mode == "PRECHECK" else 1]
            configure = next(
                step
                for step in next(iter(workflow["jobs"].values()))["steps"]
                if "configure-aws-credentials@" in step.get("uses", "")
            )
            self.assertEqual(
                json.loads(configure["with"]["inline-session-policy"]), policy
            )
            self.assertEqual(configure["with"]["output-env-credentials"], "false")
            self.assertEqual(configure["with"]["role-skip-session-tagging"], "true")

        self.assertEqual(
            s4.frozen.ALLOWED_AWS_CALLS,
            {
                ("sts", "get-caller-identity"),
                ("s3api", "list-object-versions"),
                ("s3api", "get-object"),
            },
        )
        self.assertEqual(
            s4.BoundedCorrectedAwsReadOnlyS3.CALL_CAPS,
            {
                "sts:get-caller-identity": 1,
                "s3api:list-object-versions": 3,
                "s3api:get-object": 33,
            },
        )

        # Event and consumed-predecessor lineage remain subordinate guards.
        event_envs = []
        for step in self._steps():
            selected = {
                key: value
                for key, value in step.get("env", {}).items()
                if key.startswith("EVENT_")
            }
            if selected:
                event_envs.append(selected)
        self.assertEqual(len(event_envs), 4)
        self.assertTrue(all(env == EXPECTED_EVENT_ENV for env in event_envs))
        self.assertTrue(
            all("github.run_attempt == 1" in text for text in self.workflow_texts)
        )
        for template_path in TEMPLATES:
            template = canonical(template_path)
            self.assertEqual(template["current_terminal_head_sha"], s4.CURRENT_TERMINAL_HEAD)
            self.assertEqual(
                template["consumed_predecessor"]["activation_head_sha"],
                s4.FAILED_ACTIVATION_HEAD,
            )
            self.assertEqual(
                template["consumed_predecessor"]["run_id"], s4.FAILED_RUN_ID
            )

    def test_T10_provider_quota_put_delete_paths_are_unreachable(self) -> None:
        self._ensure_complete_synthetic_artifact()
        terminal = self.artifacts["terminal-summary.json"]
        self.assertEqual(
            terminal["write_effect_counts"],
            {
                "finance_provider_api_calls": 0,
                "quota_reservations": 0,
                "remote_custody_mutations": 0,
                "s3_delete_object_calls": 0,
                "s3_put_object_calls": 0,
            },
        )

        client = s4.BoundedCorrectedAwsReadOnlyS3(s4.BUCKET)
        with mock.patch.object(
            s4.frozen.AwsReadOnlyS3,
            "aws_json",
            side_effect=AssertionError("banned command reached base AWS client"),
        ) as base_aws:
            for command in (
                "put-object",
                "delete-object",
                "delete-objects",
                "copy-object",
                "create-multipart-upload",
            ):
                with self.subTest(command=command):
                    with self.assertRaisesRegex(
                        s4.S4ForensicError, "AUDIT_AWS_COMMAND_NOT_ALLOWED"
                    ):
                        client.aws_json("s3api", command)
            self.assertEqual(base_aws.call_count, 0)

        workflow_text = "\n".join(self.workflow_texts)
        self.assertNotIn("DATA_GO_KR", workflow_text)
        self.assertNotIn("serviceKey", workflow_text)
        self.assertNotIn("api.data.go.kr", workflow_text)
        audit_source = ast.parse(self.core_text)
        run_audit = next(
            node
            for node in audit_source.body
            if isinstance(node, ast.FunctionDef) and node.name == "run_audit"
        )
        called_attributes = {
            node.func.attr
            for node in ast.walk(run_audit)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
        }
        self.assertTrue(
            called_attributes.isdisjoint(
                {
                    "urlopen",
                    "open_url",
                    "reserve_quota",
                    "put_object",
                    "delete_object",
                    "delete_objects",
                }
            )
        )


if __name__ == "__main__":
    unittest.main()
