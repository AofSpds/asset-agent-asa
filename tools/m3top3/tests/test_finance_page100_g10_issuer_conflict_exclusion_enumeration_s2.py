#!/usr/bin/env python3
"""Focused offline tests for the exact-four-version S2 enumeration."""

from __future__ import annotations

import copy
import datetime as dt
import io
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from tools.m3top3 import (
    finance_page100_g10_issuer_conflict_exclusion_enumeration_s2 as subject,
)


ROOT = pathlib.Path(__file__).resolve().parents[3]
PREP_COMMIT = "a" * 40
PREP_TREE = "b" * 40
NOW = dt.datetime(2026, 8, 31, 13, 15, tzinfo=dt.timezone.utc)


def activation(mode: str) -> dict[str, object]:
    precheck = mode == "PRECHECK"
    fresh: dict[str, object] = {
        "generation_id": subject.GENERATION_ID,
        "precheck_attempt_ordinal": 1,
        "prior_s1_precheck_or_pass_reused": False,
        "prior_s1_authority_or_session_reused": False,
        "prior_s1_activation_or_latch_reused": False,
        "runtime_lock_id": subject.RUNTIME_LOCK_ID,
    }
    if not precheck:
        fresh["live_attempt_ordinal"] = 1
    timestamp = "2026-08-31T13:14:56Z"
    prefix = (
        "G10-ISSUER-GROUP-EXCLUSION-ENUMERATION-S2-PRECHECK-ACTIVATION-"
        if precheck
        else "G10-ISSUER-GROUP-EXCLUSION-ENUMERATION-S2-LIVE-ACTIVATION-"
    )
    value: dict[str, object] = {
        "activated_at_utc": timestamp,
        "activation_id": prefix + "20260831131456",
        "armed": True,
        "artifact": (
            subject.PRECHECK_ACTIVATION_ARTIFACT
            if precheck
            else subject.LIVE_ACTIVATION_ARTIFACT
        ),
        "authority_sha256": subject.sha256_bytes(b"authority\n"),
        "branch": subject.BRANCH,
        "expected_commit_message": (
            subject.PRECHECK_MESSAGE if precheck else subject.LIVE_MESSAGE
        ),
        "fresh_runtime_and_latch": fresh,
        "manifest_sha256": subject.sha256_bytes(b"manifest\n"),
        "policy_sha256": subject.sha256_bytes(b"policy\n"),
        "preparation_commit_sha": PREP_COMMIT,
        "preparation_parent": {
            "terminal_commit_sha": subject.PREDECESSOR_TERMINAL_COMMIT,
            "terminal_tree_sha": subject.PREDECESSOR_TERMINAL_TREE,
        },
        "preparation_tree_sha": PREP_TREE,
        "repository": subject.REPOSITORY,
        "state": (
            "ARMED_FRESH_ZERO_EXTERNAL_EFFECT_S2_PRECHECK_ONCE"
            if precheck
            else "ARMED_FRESH_EXACT_FOUR_VERSION_READ_ONLY_ENUMERATION_ONCE"
        ),
    }
    if not precheck:
        value["precheck_pass_binding"] = {
            "bytes": 1,
            "commit_sha": "c" * 40,
            "git_blob_sha": "d" * 40,
            "path": subject.PRECHECK_PASS_PATH,
            "sha256": "e" * 64,
            "tree_sha": "f" * 40,
        }
    return value


class FakeStdout:
    def __init__(self) -> None:
        self.buffer = io.BytesIO()


class S2EnumerationTests(unittest.TestCase):
    def test_authority_and_compact_policy_are_exact(self) -> None:
        authority_value = subject.load_canonical_json(ROOT / subject.AUTHORITY_PATH)
        subject.validate_authority(ROOT, authority_value)
        policy = subject.load_canonical_json(ROOT / subject.POLICY_PATH)
        subject.validate_policy(policy)
        self.assertEqual(
            len(subject.canonical_json_bytes(policy)), subject.EXPECTED_POLICY_BYTES
        )
        self.assertEqual(policy["Statement"][0]["Resource"], subject.POLICY_RESOURCE_PATTERN)

        mutations = []
        changed = copy.deepcopy(policy)
        changed["Statement"][0]["Action"] = "s3:ListBucketVersions"
        mutations.append(changed)
        changed = copy.deepcopy(policy)
        changed["Statement"][0]["Resource"] = (
            f"arn:aws:s3:::{subject.BUCKET}/*"
        )
        mutations.append(changed)
        changed = copy.deepcopy(policy)
        changed["Statement"][0]["Resource"] = str(
            changed["Statement"][0]["Resource"]
        ).replace("quota_day_kst=2026-08-30", "quota_day_kst=*")
        mutations.append(changed)
        changed = copy.deepcopy(policy)
        del changed["Statement"][0]["Condition"]
        mutations.append(changed)
        changed = copy.deepcopy(policy)
        changed["Statement"][0]["Condition"]["StringEquals"]["s3:VersionId"].pop()
        mutations.append(changed)
        changed = copy.deepcopy(policy)
        changed["Statement"][0]["Condition"]["StringEquals"]["s3:VersionId"].reverse()
        mutations.append(changed)
        changed = copy.deepcopy(policy)
        changed["Statement"].append(copy.deepcopy(changed["Statement"][0]))
        mutations.append(changed)
        for mutation in mutations:
            with self.subTest(mutation=mutation), self.assertRaisesRegex(
                subject.S2EnumerationError, "POLICY_NOT_EXACT"
            ):
                subject.validate_policy(mutation)

    def test_activation_schema_freshness_and_exact_latch(self) -> None:
        for mode in ("PRECHECK", "LIVE"):
            value = activation(mode)
            subject.validate_activation(
                mode,
                value,
                b"authority\n",
                b"manifest\n",
                b"policy\n",
                PREP_COMMIT,
                PREP_TREE,
                now=NOW,
            )
            stale = copy.deepcopy(value)
            stale["activated_at_utc"] = "2026-08-30T00:00:00Z"
            stale["activation_id"] = str(stale["activation_id"])[:-14] + "20260830000000"
            with self.assertRaisesRegex(subject.S2EnumerationError, "NOT_FRESH"):
                subject.validate_activation(
                    mode,
                    stale,
                    b"authority\n",
                    b"manifest\n",
                    b"policy\n",
                    PREP_COMMIT,
                    PREP_TREE,
                    now=NOW,
                )
        bad = activation("LIVE")
        bad["fresh_runtime_and_latch"]["live_attempt_ordinal"] = True
        with self.assertRaisesRegex(subject.S2EnumerationError, "FRESH_RUNTIME"):
            subject.validate_activation(
                "LIVE",
                bad,
                b"authority\n",
                b"manifest\n",
                b"policy\n",
                PREP_COMMIT,
                PREP_TREE,
                now=NOW,
            )
        extra = activation("PRECHECK")
        extra["note"] = "unbound-value"
        with self.assertRaisesRegex(subject.S2EnumerationError, "IDENTITY_INVALID"):
            subject.validate_activation(
                "PRECHECK",
                extra,
                b"authority\n",
                b"manifest\n",
                b"policy\n",
                PREP_COMMIT,
                PREP_TREE,
                now=NOW,
            )

    def test_event_lineage_is_enforced_for_both_modes(self) -> None:
        base = {
            "EVENT_ACTOR": subject.ACTOR,
            "EVENT_TRIGGERING_ACTOR": subject.ACTOR,
            "EVENT_REPOSITORY": subject.REPOSITORY,
            "EVENT_REF": f"refs/heads/{subject.BRANCH}",
            "EVENT_AFTER": "9" * 40,
            "EVENT_FORCED": "false",
            "EVENT_RUN_ATTEMPT": "1",
        }
        for mode in ("PRECHECK", "LIVE"):
            value = activation(mode)
            expected_before = (
                PREP_COMMIT
                if mode == "PRECHECK"
                else value["precheck_pass_binding"]["commit_sha"]
            )
            env = {
                **base,
                "EVENT_BEFORE": expected_before,
                "EVENT_HEAD_MESSAGE": (
                    subject.PRECHECK_MESSAGE
                    if mode == "PRECHECK"
                    else subject.LIVE_MESSAGE
                ),
            }
            with mock.patch.dict(os.environ, env, clear=True):
                subject.validate_event_lineage(mode, value, PREP_COMMIT)
            env["EVENT_HEAD_MESSAGE"] = "wrong"
            with mock.patch.dict(os.environ, env, clear=True), self.assertRaisesRegex(
                subject.S2EnumerationError, "EVENT_LINEAGE_MISMATCH"
            ):
                subject.validate_event_lineage(mode, value, PREP_COMMIT)

    def test_precheck_pass_exact_effects_activation_and_workflow_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            root = pathlib.Path(temp_name)
            precheck_path = root / subject.PRECHECK_ACTIVATION_PATH
            receipt_path = root / subject.PRECHECK_PASS_PATH
            precheck_path.parent.mkdir(parents=True)
            precheck_value = activation("PRECHECK")
            current = dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=1)
            precheck_value["activated_at_utc"] = current.strftime("%Y-%m-%dT%H:%M:%SZ")
            precheck_value["activation_id"] = (
                "G10-ISSUER-GROUP-EXCLUSION-ENUMERATION-S2-PRECHECK-ACTIVATION-"
                + current.strftime("%Y%m%d%H%M%S")
            )
            precheck_path.write_bytes(subject.canonical_json_bytes(precheck_value))
            activation_binding = {
                **subject.file_binding(precheck_path),
                "commit_sha": "1" * 40,
                "path": subject.PRECHECK_ACTIVATION_PATH,
                "tree_sha": "2" * 40,
            }
            run_id = 123456
            receipt = {
                "activation_binding": activation_binding,
                "artifact": subject.PRECHECK_PASS_ARTIFACT,
                "branch": subject.BRANCH,
                "effects": dict(subject.EXPECTED_PRECHECK_EFFECTS),
                "exact_enumeration_started": False,
                "generation_id": subject.GENERATION_ID,
                "preparation": {"head_sha": PREP_COMMIT, "tree_sha": PREP_TREE},
                "repository": subject.REPOSITORY,
                "state": "PASS_FRESH_BOUNDED_S2_PRECHECK_LIVE_NOT_STARTED",
                "workflow": {
                    "actor": subject.ACTOR,
                    "completed_at_utc": dt.datetime.now(dt.timezone.utc).strftime(
                        "%Y-%m-%dT%H:%M:%SZ"
                    ),
                    "conclusion": "success",
                    "event": "push",
                    "head_sha": activation_binding["commit_sha"],
                    "job_id": 654321,
                    "path": subject.PRECHECK_WORKFLOW_PATH,
                    "run_attempt": 1,
                    "run_id": run_id,
                    "triggering_actor": subject.ACTOR,
                    "url": f"https://github.com/{subject.REPOSITORY}/actions/runs/{run_id}",
                },
            }
            receipt_path.write_bytes(subject.canonical_json_bytes(receipt))
            live_value = activation("LIVE")
            live_value["precheck_pass_binding"] = {
                **subject.file_binding(receipt_path),
                "commit_sha": "3" * 40,
                "path": subject.PRECHECK_PASS_PATH,
                "tree_sha": "4" * 40,
            }
            subject.validate_precheck_pass(
                root,
                receipt,
                live_value,
                b"authority\n",
                b"manifest\n",
                b"policy\n",
                PREP_COMMIT,
                PREP_TREE,
            )
            bad_effect = copy.deepcopy(receipt)
            bad_effect["effects"]["g10_or_g11_runs"] = 1
            with self.assertRaisesRegex(subject.S2EnumerationError, "EFFECTS_NOT_ZERO"):
                subject.validate_precheck_pass(
                    root,
                    bad_effect,
                    live_value,
                    b"authority\n",
                    b"manifest\n",
                    b"policy\n",
                    PREP_COMMIT,
                    PREP_TREE,
                )
            bad_provenance = copy.deepcopy(receipt)
            bad_provenance["workflow"]["head_sha"] = "5" * 40
            with self.assertRaisesRegex(subject.S2EnumerationError, "WORKFLOW_INVALID"):
                subject.validate_precheck_pass(
                    root,
                    bad_provenance,
                    live_value,
                    b"authority\n",
                    b"manifest\n",
                    b"policy\n",
                    PREP_COMMIT,
                    PREP_TREE,
                )

    def _fake_reader_fixture(self):
        bodies = [b"one", b"two-two", b"three", b"four-four"]
        bindings = tuple(
            {
                "bytes": len(body),
                "page_no": ordinal,
                "s3_object_key": f"sealed/page-{ordinal}.entity",
                "sha256": subject.sha256_bytes(body),
                "version_id": f"version-{ordinal}",
            }
            for ordinal, body in enumerate(bodies, 1)
        )
        calls: list[tuple[list[str], dict[str, str]]] = []

        def fake_run(command, **kwargs):
            calls.append((list(command), dict(kwargs["env"])))
            key = command[command.index("--key") + 1]
            version = command[command.index("--version-id") + 1]
            ordinal = next(
                index
                for index, row in enumerate(bindings)
                if row["s3_object_key"] == key and row["version_id"] == version
            )
            pathlib.Path(command[-1]).write_bytes(bodies[ordinal])
            user_metadata = {
                key: f"synthetic-{key}"
                for key in subject.EXPECTED_RAW_METADATA_KEYS
            }
            user_metadata["sha256"] = bindings[ordinal]["sha256"]
            value = {
                "ContentLength": len(bodies[ordinal]),
                "ContentType": subject.EXPECTED_CONTENT_TYPE,
                "Metadata": user_metadata,
                "ServerSideEncryption": "AES256",
                "VersionId": version,
            }
            return subprocess.CompletedProcess(
                command, 0, stdout=json.dumps(value).encode(), stderr=b""
            )

        return bodies, bindings, calls, fake_run

    def test_fake_aws_exact_one_plus_four_success_and_no_retry(self) -> None:
        bodies, bindings, calls, fake_run = self._fake_reader_fixture()
        with mock.patch.object(subject, "EXPECTED_RAW_VERSIONS", bindings), mock.patch.object(
            subject, "EXPECTED_TOTAL_BYTES", sum(map(len, bodies))
        ):
            reader = subject.ExactAwsCli(
                fake_run, configured_account_id=subject.ACCOUNT_ID
            )
            self.assertEqual(reader.read_all(), bodies)
        self.assertEqual(reader.call_counts, {"s3api:get-object": 4})
        self.assertEqual(len(calls), 4)
        self.assertTrue(all(env["AWS_MAX_ATTEMPTS"] == "1" for _, env in calls))
        self.assertTrue(all("--version-id" in cmd for cmd, _ in calls))
        self.assertFalse(any("list" in token or "head" in token for cmd, _ in calls for token in cmd))

        rejected = subject.ExactAwsCli(fake_run, configured_account_id="000000000000")
        with self.assertRaisesRegex(subject.S2EnumerationError, "ACCOUNT_ID_INVALID"):
            rejected.read_all()
        self.assertEqual(rejected.call_counts, {"s3api:get-object": 0})

    def test_fifth_wrong_order_and_failed_call_stop_without_retry(self) -> None:
        bodies, bindings, calls, fake_run = self._fake_reader_fixture()
        with mock.patch.object(subject, "EXPECTED_RAW_VERSIONS", bindings), mock.patch.object(
            subject, "EXPECTED_TOTAL_BYTES", sum(map(len, bodies))
        ):
            reader = subject.ExactAwsCli(
                fake_run, configured_account_id=subject.ACCOUNT_ID
            )
            reader.read_all()
            with self.assertRaisesRegex(subject.S2EnumerationError, "BUDGET_EXCEEDED"):
                reader._invoke("s3api:get-object", ("s3api", "get-object"))
            wrong = subject.ExactAwsCli(
                fake_run, configured_account_id=subject.ACCOUNT_ID
            )
            wrong.validate_configured_identity()
            with tempfile.TemporaryDirectory() as name:
                with self.assertRaisesRegex(subject.S2EnumerationError, "NOT_SEQUENTIAL"):
                    wrong.read_exact(2, pathlib.Path(name) / "wrong")

            failure_calls = 0

            def fail_once(command, **kwargs):
                nonlocal failure_calls
                failure_calls += 1
                return subprocess.CompletedProcess(command, 1, stdout=b"", stderr=b"secret")

            failed = subject.ExactAwsCli(
                fail_once, configured_account_id=subject.ACCOUNT_ID
            )
            with self.assertRaisesRegex(subject.S2EnumerationError, "AWS_CLI_CALL_FAILED"):
                failed.read_all()
            self.assertEqual(failure_calls, 1)
            self.assertEqual(failed.call_counts["s3api:get-object"], 1)

    def test_missing_or_extra_raw_metadata_key_fails_before_parse(self) -> None:
        bodies, bindings, _, fake_run = self._fake_reader_fixture()

        def mutated_run(mode):
            def invoke(command, **kwargs):
                result = fake_run(command, **kwargs)
                if command[1:3] == ["s3api", "get-object"]:
                    value = json.loads(result.stdout)
                    if mode == "missing":
                        value["Metadata"].pop("http-status")
                    else:
                        value["Metadata"]["unexpected"] = "x"
                    return subprocess.CompletedProcess(
                        command, 0, stdout=json.dumps(value).encode(), stderr=b""
                    )
                return result

            return invoke

        with mock.patch.object(subject, "EXPECTED_RAW_VERSIONS", bindings), mock.patch.object(
            subject, "EXPECTED_TOTAL_BYTES", sum(map(len, bodies))
        ):
            for mode in ("missing", "extra"):
                with self.subTest(mode=mode), self.assertRaisesRegex(
                    subject.S2EnumerationError, "RAW_USER_METADATA_EXACT_SET"
                ):
                    subject.ExactAwsCli(
                        mutated_run(mode), configured_account_id=subject.ACCOUNT_ID
                    ).read_all()

    def test_output_is_hash_only_and_accounted(self) -> None:
        reader = subject.ExactAwsCli(
            lambda *args, **kwargs: None,
            configured_account_id=subject.ACCOUNT_ID,
        )
        reader.call_counts = {"s3api:get-object": 4}
        projection = {
            "eligible_projection": {"row_count": 37, "sha256": "1" * 64},
            "partition_accounting": {
                "eligible_match_rows": 37,
                "excluded_conflict_occurrences": 2,
                "excluded_prior_matching_occurrences": 1,
                "excluded_total_occurrences": 3,
                "missing_rows": 0,
                "source_rows": 40,
            },
            "target_occurrences": [
                {"global_row_ordinal": 1, "page_item_ordinal": 1, "page_no": 1},
                {"global_row_ordinal": 37, "page_item_ordinal": 7, "page_no": 4},
                {"global_row_ordinal": 39, "page_item_ordinal": 9, "page_no": 4},
            ],
        }
        result = subject.build_live_output(projection, reader)
        self.assertEqual(result["target_global_row_ordinals"], [1, 37, 39])
        self.assertEqual(result["target_occurrence_count"], 3)
        self.assertEqual(result["effects"]["oidc_assume_role_with_web_identity_calls"], 1)
        self.assertEqual(result["effects"]["sts_get_caller_identity_calls"], 1)
        self.assertEqual(result["effects"]["s3_get_object_version_calls"], 4)
        encoded = subject.canonical_json_bytes(result)
        self.assertEqual(encoded, subject.canonical_json_bytes(json.loads(encoded)))
        self.assertFalse(subject._contains_clear_identity_key(result))
        self.assertNotIn(b"issuCmpy", encoded)

    def test_live_preflight_command_is_offline(self) -> None:
        output = FakeStdout()
        with mock.patch.object(subject, "_validated_live_inputs") as validate, mock.patch.object(
            sys, "stdout", output
        ):
            self.assertEqual(subject.command_live_preflight(object()), 0)
        validate.assert_called_once()
        parsed = json.loads(output.buffer.getvalue())
        self.assertEqual(parsed["state"], "PASS_LIVE_PREFLIGHT_ZERO_EXTERNAL_EFFECT")
        self.assertEqual(parsed["effects"], subject.EXPECTED_PRECHECK_EFFECTS)


if __name__ == "__main__":
    unittest.main()
