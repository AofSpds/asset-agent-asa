#!/usr/bin/env python3
"""Affected-scope tests T1-T10 for G10 read-only forensic S2."""

from __future__ import annotations

import json
import os
import pathlib
import unittest
from unittest import mock

import yaml

from tools.m3top3 import finance_page100_g10_forensic_s2 as s2


ROOT = pathlib.Path(__file__).resolve().parents[3]
WORKFLOW_PATHS = (s2.PRECHECK_WORKFLOW_PATH, s2.AUDIT_WORKFLOW_PATH)
WORKFLOWS = [ROOT / path for path in WORKFLOW_PATHS]
RUNNER = ROOT / s2.RUNNER_PATH
POLICIES = {
    "PRECHECK": ROOT / s2.PRECHECK_POLICY_PATH,
    "AUDIT": ROOT / s2.AUDIT_POLICY_PATH,
}
AUTHORITY = ROOT / s2.AUTHORITY_PATH
PRECHECK_TEMPLATE = ROOT / s2.PRECHECK_TEMPLATE_PATH
AUDIT_TEMPLATE = ROOT / s2.AUDIT_TEMPLATE_PATH

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
    assert raw == s2.canonical_json_bytes(value)
    return value


class G10ForensicS2FocusedTests(unittest.TestCase):
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
                "EVENT_ACTOR": s2.ACTOR,
                "EVENT_TRIGGERING_ACTOR": s2.ACTOR,
                "EVENT_REPOSITORY": s2.REPOSITORY,
                "EVENT_REF": "refs/heads/" + s2.BRANCH,
                "EVENT_FORCED": "true",
                "EVENT_HEAD_MESSAGE": s2.PRECHECK_MESSAGE,
                "EVENT_RUN_ATTEMPT": "1",
            },
            clear=True,
        ):
            with self.assertRaisesRegex(
                s2.S2ForensicError, "EVENT_ENV_EVENT_FORCED_MISMATCH"
            ):
                s2.validate_git_activation({}, "PRECHECK")

    def test_T4_before_after_message_and_exact_diff_guards_present(self) -> None:
        for token in (
            "EVENT_BEFORE",
            "EVENT_AFTER",
            "EVENT_HEAD_MESSAGE",
            "ACTIVATION_PARENT_MISMATCH",
            "ACTIVATION_RAW_MESSAGE_MISMATCH",
            "ACTIVATION_DIFF_NOT_EXACT_ONE_FILE",
            "PREPARATION_DIFF_NOT_EXACT_S2_FILES",
            "AUDIT_PARENT_NOT_PRECHECK_PASS_RECEIPT",
        ):
            self.assertIn(token, self.runner_text)

    def test_T5_consumed_activation_not_reused(self) -> None:
        precheck = canonical(PRECHECK_TEMPLATE)
        audit = canonical(AUDIT_TEMPLATE)
        self.assertEqual(precheck["current_terminal_head_sha"], s2.CURRENT_TERMINAL_HEAD)
        self.assertEqual(audit["current_terminal_head_sha"], s2.CURRENT_TERMINAL_HEAD)
        self.assertEqual(
            precheck["consumed_predecessor"]["activation_head_sha"],
            s2.FAILED_ACTIVATION_HEAD,
        )
        combined = "\n".join(self.workflow_texts)
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
        self.assertEqual(predecessor["run_id"], s2.FAILED_RUN_ID)
        self.assertEqual(predecessor["run_attempt"], 1)
        self.assertFalse(authority["g10_live_rerun_authorized"])
        self.assertFalse(authority["g11_authorized"])
        combined = "\n".join(self.workflow_texts)
        self.assertIn("github.run_attempt == 1", combined)
        self.assertNotIn("rerun", combined.lower())
        self.assertEqual(
            authority["exact_g10_raw_versions"], list(s2.EXACT_RAW_VERSIONS)
        )

    def test_T7_phase_policies_are_exact_read_only_and_budgeted(self) -> None:
        for mode, path in POLICIES.items():
            policy = canonical(path)
            s2.validate_policy(policy, mode)
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
            self.assertLessEqual(
                len(json.dumps(policy, sort_keys=True, separators=(",", ":"))),
                2048,
            )
        self.assertEqual(
            s2.BoundedFrozenAwsReadOnlyS3.CALL_CAPS,
            {
                "sts:get-caller-identity": 1,
                "s3api:list-object-versions": 3,
                "s3api:get-object": 33,
            },
        )
        self.assertEqual(
            s2._sorted_readbacks(
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
        self.assertEqual(len(audit_statements), 4)
        self.assertEqual(
            audit_statements[1]["Condition"]["StringEquals"]["s3:VersionId"],
            [row["version_id"] for row in s2.EXACT_RAW_VERSIONS],
        )
        self.assertTrue(audit_statements[1]["Resource"].endswith("/*"))
        self.assertNotIn("*", audit_statements[2]["Resource"])
        self.assertNotIn("*", audit_statements[3]["Resource"])

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
        self.assertEqual(len(s2.AUDIT_OUTPUT_NAMES), 10)
        self.assertEqual(
            s2.AUDIT_OUTPUT_NAMES,
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
                with self.assertRaises(s2.S2ForensicError):
                    s2._scan_bytes(payload, [])
        s2._scan_bytes(
            b'{"issuCmpyKsdCustNo_equal":false,"crno_sha256":"safe"}', []
        )
        with self.assertRaises(s2.S2ForensicError):
            s2._scan_bytes(b"prefix-abcdefghijklmnop-suffix", [b"abcdefghijklmnop"])


if __name__ == "__main__":
    unittest.main()
