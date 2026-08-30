#!/usr/bin/env python3
"""Affected-scope tests T1-T10 for G10 read-only forensic S3."""

from __future__ import annotations

import json
import os
import pathlib
import unittest
from unittest import mock

import yaml

from tools.m3top3 import finance_page100_g10_forensic_s3 as s3


ROOT = pathlib.Path(__file__).resolve().parents[3]
WORKFLOW_PATHS = (s3.PRECHECK_WORKFLOW_PATH, s3.AUDIT_WORKFLOW_PATH)
WORKFLOWS = [ROOT / path for path in WORKFLOW_PATHS]
RUNNER = ROOT / s3.RUNNER_PATH
POLICIES = {
    "PRECHECK": ROOT / s3.PRECHECK_POLICY_PATH,
    "AUDIT": ROOT / s3.AUDIT_POLICY_PATH,
}
AUTHORITY = ROOT / s3.AUTHORITY_PATH
PRECHECK_TEMPLATE = ROOT / s3.PRECHECK_TEMPLATE_PATH
AUDIT_TEMPLATE = ROOT / s3.AUDIT_TEMPLATE_PATH

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


def canonical(path: pathlib.Path) -> dict:
    raw = path.read_bytes()
    value = json.loads(raw)
    assert raw == s3.canonical_json_bytes(value)
    return value


class G10ForensicS3FocusedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.workflow_texts = [path.read_text(encoding="utf-8") for path in WORKFLOWS]
        cls.workflows = [
            yaml.load(text, Loader=yaml.BaseLoader) for text in cls.workflow_texts
        ]
        cls.runner_text = RUNNER.read_text(encoding="utf-8")

    def _steps(self) -> list[dict]:
        rows: list[dict] = []
        for workflow in self.workflows:
            for job in workflow["jobs"].values():
                rows.extend(job["steps"])
        return rows

    def _event_envs(self) -> list[dict[str, str]]:
        rows: list[dict[str, str]] = []
        for step in self._steps():
            env = step.get("env", {})
            selected = {
                key: value for key, value in env.items() if key.startswith("EVENT_")
            }
            if selected:
                rows.append(selected)
        return rows

    def test_T1_complete_event_key_set_parity(self) -> None:
        envs = self._event_envs()
        self.assertEqual(len(envs), 4)
        for env in envs:
            self.assertEqual(set(env), set(EXPECTED_EVENT_ENV))

    def test_T2_identical_github_expressions(self) -> None:
        for env in self._event_envs():
            self.assertEqual(env, EXPECTED_EVENT_ENV)

    def test_T3_event_forced_is_direct_and_fail_closed(self) -> None:
        for env in self._event_envs():
            self.assertEqual(env["EVENT_FORCED"], "${{ github.event.forced }}")
        self.assertIn('"EVENT_FORCED": "false"', self.runner_text)
        with mock.patch.dict(
            os.environ,
            {
                "EVENT_ACTOR": s3.ACTOR,
                "EVENT_TRIGGERING_ACTOR": s3.ACTOR,
                "EVENT_REPOSITORY": s3.REPOSITORY,
                "EVENT_REF": "refs/heads/" + s3.BRANCH,
                "EVENT_FORCED": "true",
                "EVENT_HEAD_MESSAGE": s3.PRECHECK_MESSAGE,
                "EVENT_RUN_ATTEMPT": "1",
            },
            clear=True,
        ):
            with self.assertRaisesRegex(
                s3.S3ForensicError, "EVENT_ENV_EVENT_FORCED_MISMATCH"
            ):
                s3.validate_git_activation({}, "PRECHECK")

    def test_T4_before_after_message_and_exact_diff_guards_present(self) -> None:
        for token in (
            "EVENT_BEFORE",
            "EVENT_AFTER",
            "EVENT_HEAD_MESSAGE",
            "ACTIVATION_PARENT_MISMATCH",
            "ACTIVATION_RAW_MESSAGE_MISMATCH",
            "ACTIVATION_DIFF_NOT_EXACT_ONE_FILE",
            "PREPARATION_DIFF_NOT_EXACT_S3_FILES",
            "AUDIT_PARENT_NOT_PRECHECK_PASS_RECEIPT",
        ):
            self.assertIn(token, self.runner_text)

    def test_T5_consumed_activation_not_reused(self) -> None:
        precheck = canonical(PRECHECK_TEMPLATE)
        audit = canonical(AUDIT_TEMPLATE)
        self.assertEqual(precheck["current_terminal_head_sha"], s3.CURRENT_TERMINAL_HEAD)
        self.assertEqual(audit["current_terminal_head_sha"], s3.CURRENT_TERMINAL_HEAD)
        self.assertEqual(
            precheck["consumed_predecessor"]["activation_head_sha"],
            s3.FAILED_ACTIVATION_HEAD,
        )
        combined = "\n".join(self.workflow_texts)
        self.assertNotIn("forensic-s2", combined.lower())
        self.assertNotIn("FORENSIC_S2_", combined)
        self.assertNotIn(
            "M3TOP3_FINANCE_CA_PAGE100_G10_FORENSIC_ACTIVATION_v1.0.json",
            combined,
        )
        self.assertNotEqual(
            precheck["activation_commit_message"],
            "Arm G10 read-only issuer and S3 forensic audit once v1.0",
        )

    def test_T6_consumed_run_and_attempt_not_fresh_evidence(self) -> None:
        authority = canonical(AUTHORITY)
        predecessor = authority["predecessor_forensic_terminal"]
        self.assertEqual(predecessor["run_id"], s3.FAILED_RUN_ID)
        self.assertEqual(predecessor["run_attempt"], 1)
        self.assertEqual(predecessor["activation_head_sha"], s3.FAILED_ACTIVATION_HEAD)
        self.assertEqual(predecessor["terminal_head_sha"], s3.CURRENT_TERMINAL_HEAD)
        self.assertEqual(predecessor["terminal_tree_sha"], s3.CURRENT_TERMINAL_TREE)
        self.assertEqual(
            predecessor["receipt"],
            {
                "bytes": 6857,
                "git_blob_sha": "277c841416845f1797a9994c810537c8e19b5204",
                "path": s3.FAILED_RECEIPT_PATH,
                "sha256": "60bcdaee93b2d125d8c325db95b4c93756935b94083ae9a65234bb974fa0ad2c",
            },
        )
        self.assertFalse(authority["g10_live_rerun_authorized"])
        self.assertFalse(authority["g11_authorized"])
        combined = "\n".join(self.workflow_texts)
        self.assertIn("github.run_attempt == 1", combined)
        self.assertNotIn("rerun", combined.lower())
        self.assertEqual(
            authority["exact_g10_raw_versions"], list(s3.EXACT_RAW_VERSIONS)
        )

    def test_T7_phase_policies_are_exact_read_only_and_budgeted(self) -> None:
        for mode, path in POLICIES.items():
            policy = canonical(path)
            s3.validate_policy(policy, mode)
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
            self.assertEqual(configure["with"]["output-credentials"], "true")
            self.assertEqual(configure["with"]["role-skip-session-tagging"], "true")
            self.assertNotIn("managed-session-policies", configure["with"])
            self.assertNotIn("session-tags", configure["with"])
            self.assertNotIn("role-session-tags", configure["with"])
            self.assertLessEqual(
                len(json.dumps(policy, sort_keys=True, separators=(",", ":"))),
                2048,
            )
            if mode == "AUDIT":
                raw = path.read_bytes()
                self.assertEqual(len(raw), s3.AUDIT_POLICY_BYTES)
                self.assertEqual(len(raw) - 1, s3.AUDIT_POLICY_CHARACTERS)
                self.assertEqual(s3.sha256_bytes(raw), s3.AUDIT_POLICY_SHA256)
                self.assertEqual(s3.git_blob_sha(raw), s3.AUDIT_POLICY_GIT_BLOB_SHA)
        self.assertEqual(
            s3.BoundedFrozenAwsReadOnlyS3.CALL_CAPS,
            {
                "sts:get-caller-identity": 1,
                "s3api:list-object-versions": 3,
                "s3api:get-object": 33,
            },
        )
        self.assertEqual(
            s3._sorted_readbacks(
                [
                    {"key": "b", "version_id": "2"},
                    {"key": "a", "version_id": "9"},
                    {"key": "b", "version_id": "1"},
                ]
            ),
            [
                {"key": "a", "version_id": "9"},
                {"key": "b", "version_id": "1"},
                {"key": "b", "version_id": "2"},
            ],
        )

    def test_T8_no_write_or_wildcard_action(self) -> None:
        for policy_path in POLICIES.values():
            policy = canonical(policy_path)
            action_text = json.dumps(
                [statement["Action"] for statement in policy["Statement"]]
            )
            for fragment in (
                "PutObject",
                "DeleteObject",
                "DeleteObjectVersion",
                "AbortMultipartUpload",
                "CopyObject",
                "RestoreObject",
            ):
                self.assertNotIn(fragment, action_text)
            self.assertNotRegex(action_text, r'"s3:[^"]*\*"')
        audit_statements = canonical(POLICIES["AUDIT"])["Statement"]
        self.assertEqual(len(audit_statements), 2)
        self.assertEqual(
            audit_statements[1]["Resource"],
            [
                "arn:aws:s3:::" + s3.BUCKET + "/" + s3.frozen.RAW_PREFIX + "*",
                "arn:aws:s3:::" + s3.BUCKET + "/" + s3.frozen.CHECKPOINT_KEY,
                "arn:aws:s3:::" + s3.BUCKET + "/" + s3.frozen.CLAIM_KEY,
            ],
        )
        self.assertNotIn("Condition", audit_statements[1])
        self.assertTrue(audit_statements[1]["Resource"][0].endswith("/*"))
        self.assertNotIn("*", audit_statements[1]["Resource"][1])
        self.assertNotIn("*", audit_statements[1]["Resource"][2])

        raw_client = s3.BoundedFrozenAwsReadOnlyS3(s3.BUCKET)
        raw_client.aws_json = mock.Mock(
            return_value={
                "IsTruncated": False,
                "Versions": [
                    {
                        "Key": row["s3_object_key"],
                        "VersionId": row["version_id"],
                    }
                    for row in s3.EXACT_RAW_VERSIONS
                ],
                "DeleteMarkers": [],
            }
        )
        self.assertEqual(
            len(raw_client.list_versions(s3.frozen.RAW_PREFIX)["versions"]), 4
        )
        with self.assertRaisesRegex(
            s3.S3ForensicError, "AUDIT_GET_PAIR_OUTSIDE_EXACT_ALLOWED_SET"
        ):
            raw_client._listed_pairs.add((s3.frozen.RAW_PREFIX + "other", "v-other"))
            raw_client.read_exact_version(
                s3.frozen.RAW_PREFIX + "other",
                "v-other",
                pathlib.Path("unused"),
                expected_content_type="application/octet-stream",
                expected_metadata_keys=frozenset(),
            )

        for prefix, versions, code in (
            (
                s3.frozen.RAW_PREFIX,
                [{"Key": s3.EXACT_RAW_VERSIONS[0]["s3_object_key"], "VersionId": "wrong"}],
                "AUDIT_RAW_LIST_PAIR_SET_INVALID",
            ),
            (
                s3.frozen.CONTROL_PREFIX,
                [{"Key": s3.frozen.CHECKPOINT_KEY, "VersionId": "only-one"}],
                "AUDIT_CHECKPOINT_LIST_PAIR_SET_INVALID",
            ),
            (
                s3.frozen.CLAIM_KEY,
                [{"Key": s3.frozen.CLAIM_KEY, "VersionId": "wrong"}],
                "AUDIT_CLAIM_LIST_PAIR_SET_INVALID",
            ),
        ):
            with self.subTest(prefix=prefix):
                client = s3.BoundedFrozenAwsReadOnlyS3(s3.BUCKET)
                client.aws_json = mock.Mock(
                    return_value={
                        "IsTruncated": False,
                        "Versions": versions,
                        "DeleteMarkers": [],
                    }
                )
                with self.assertRaisesRegex(s3.S3ForensicError, code):
                    client.list_versions(prefix)

    def test_T9_provider_and_control_tokens_unreachable_from_aws_reads(self) -> None:
        combined = "\n".join(self.workflow_texts)
        self.assertNotIn("secrets.", combined)
        self.assertNotIn("DATA_GO_KR", combined)
        self.assertNotIn("api.data.go.kr", combined)
        self.assertNotIn("finance_page100_pilot.py", combined)
        self.assertNotIn("urllib.request.urlopen", self.runner_text)
        self.assertNotIn('os.environ.get("DATA_GO', self.runner_text)
        aws_steps = [
            step
            for step in self._steps()
            if step.get("name", "").startswith("Validate read-only AWS")
            or step.get("name", "").startswith("Read exact existing versions")
        ]
        self.assertEqual(len(aws_steps), 2)
        for step in aws_steps:
            env = step["env"]
            self.assertNotIn("GITHUB_TOKEN", env)
            self.assertNotIn("GH_TOKEN", env)
            self.assertEqual(
                {key for key in env if key.startswith("AWS_")},
                {"AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN"},
            )
        for step in self._steps():
            if step not in aws_steps:
                self.assertFalse(
                    {key for key in step.get("env", {}) if key.startswith("AWS_")}
                )

    def test_T10_exact_allowlist_and_secret_token_identity_rejection(self) -> None:
        self.assertNotIn("AES356", self.runner_text)
        self.assertNotIn("aes356", self.runner_text)
        self.assertIn('metadata.get("ServerSideEncryption") == "AES256"', self.runner_text)
        self.assertIn('"server_side_encryption": "AES256"', self.runner_text)
        self.assertIn('"exact_version_readbacks_sse_aes256": 33', self.runner_text)
        self.assertEqual(len(s3.AUDIT_OUTPUT_NAMES), 10)
        self.assertEqual(
            s3.AUDIT_OUTPUT_NAMES,
            {
                "precheck-receipt.json",
                "activation-readback.json",
                "aws-readonly-session-receipt.json",
                "raw-version-manifest.json",
                "checkpoint-version-history.json",
                "execution-claim-version-history.json",
                "issuer-conflict-reproduction.json",
                "exact-secret-scan.json",
                "sanitization-receipt.json",
                "terminal-summary.json",
            },
        )
        sentinels = (
            b'{"Authorization":"Basic SECRET"}',
            b'{"Authorization":"Bearer SECRET"}',
            b'{"AWS_SECRET_ACCESS_KEY":"SECRET"}',
            b'{"ACTIONS_ID_TOKEN_REQUEST_TOKEN":"SECRET"}',
            b'{"serviceKey":"SECRET"}',
            b"https://example.invalid/?X-Amz-Signature=abcdef",
            b"https://example.invalid/?signature=abcdef",
            b"https://example.invalid/?access_token=abcdef",
            b"https://user:password@example.invalid/path",
            b"AKIAABCDEFGHIJKLMNOP",
            b"ghp_abcdefghijklmnopqrstuvwxyz123456",
            b"eyJabcdefghijk.eyJabcdefghijk.abcdefghijk",
            b"RAW_SECRET_SENTINEL",
            b'{"issuCmpyKsdCustNo":"raw"}',
            b'{"crno":"raw"}',
            b"<stckIssuCmpyNm>raw</stckIssuCmpyNm>",
        )
        for payload in sentinels:
            with self.subTest(payload=payload):
                with self.assertRaises(s3.S3ForensicError):
                    s3._scan_bytes(payload, [])
        s3._scan_bytes(
            b'{"issuCmpyKsdCustNo_equal":false,"crno_sha256":"safe"}', []
        )
        with self.assertRaises(s3.S3ForensicError):
            s3._scan_bytes(b"prefix-abcdefghijklmnop-suffix", [b"abcdefghijklmnop"])


if __name__ == "__main__":
    unittest.main()
