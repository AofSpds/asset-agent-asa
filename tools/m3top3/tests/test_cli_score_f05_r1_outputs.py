from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from tools.m3top3 import cli_score_f05_r1_outputs as cli
from tools.m3top3.f05_r1_score_outputs import (
    AGGREGATE_VALIDATION_SCHEMA_VERSION,
    EXPECTED_CONFIG_SHA256,
    EXPECTED_F02_INPUT_BATCH_SHA256,
    EXPECTED_INDEPENDENCE_ASSERTION,
    EXPECTED_TARGET_AUTHOR_IDENTITY,
    EXPECTED_VALIDATION_LEVEL_BY_ROLE,
    F05ScoreArtifacts,
    F05ScoreOutputError,
    INDEPENDENT_VALIDATION_RECEIPT_SCHEMA_VERSION,
)


SOURCE_REPO = Path(__file__).resolve().parents[3]
SOURCE_F02 = SOURCE_REPO / cli.EXPECTED_F02_INPUT_PATH
SOURCE_CONFIG = SOURCE_REPO / cli.EXPECTED_CONFIG_PATH
RUN_ID = "AAA-M3TOP3-F05-R1-SYNTHETIC-CLI-TEST"
RUN_ROOT = (
    Path("control/m3top3/f05-r1-w1-market-positioning/v1.0/runs") / RUN_ID
)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class SyntheticValidatedRepo:
    """Small committed Git target; the real scoring helper is always mocked."""

    def __init__(self):
        self.temp = tempfile.TemporaryDirectory(prefix="f05-score-cli-")
        self.repo = Path(self.temp.name).resolve()
        self._git("init", "-q")
        self._git("config", "user.name", "Synthetic Validator")
        self._git("config", "user.email", "validator@example.invalid")
        self._git("config", "core.autocrlf", "false")

        self.f05_relative = (RUN_ROOT / cli.EXPECTED_F05_INPUT_FILENAME).as_posix()
        self.report_relative = (RUN_ROOT / cli.EXPECTED_REPORT_FILENAME).as_posix()
        self.output_dir = self.repo / RUN_ROOT / "score-output"

        required = set(cli.REQUIRED_VALIDATED_RUNTIME_PATHS)
        required.update(
            {self.f05_relative, cli.EXPECTED_F02_INPUT_PATH, cli.EXPECTED_CONFIG_PATH}
        )
        for relative in sorted(required):
            self._write(relative, f"synthetic validated target: {relative}\n".encode())

        self.f02_bytes = SOURCE_F02.read_bytes()
        self.config_bytes = SOURCE_CONFIG.read_bytes()
        self.f05_bytes = b'{"synthetic_f05_input":"hash-bound-only"}\n'
        self._write(cli.EXPECTED_F02_INPUT_PATH, self.f02_bytes)
        self._write(cli.EXPECTED_CONFIG_PATH, self.config_bytes)
        self._write(self.f05_relative, self.f05_bytes)
        self._commit("synthetic exact target")
        self.target_commit = self._git("rev-parse", "HEAD")
        self.target_tree = self._git("rev-parse", "HEAD^{tree}")

        self.merged_input_hash = "c" * 64
        self.target_revision = "D1"
        self.target_bundle = (
            f"AAA-M3TOP3-F05-R1-D1-{self.target_commit}-{self.target_tree}"
        )
        self.input_bindings = {
            "f05_input_jsonl_sha256": _sha(self.f05_bytes),
            "f02_model_input_batch_sha256": _sha(self.f02_bytes),
            "config_sha256": _sha(self.config_bytes),
        }
        self.validated_target_files = []
        for relative in sorted(required):
            data = (self.repo / Path(*relative.split("/"))).read_bytes()
            self.validated_target_files.append(
                {
                    "path": relative,
                    "sha256": _sha(data),
                    "git_blob": self._git("rev-parse", f"{self.target_commit}:{relative}"),
                }
            )

        self.receipt_relatives = {}
        self.receipt_bytes = {}
        descriptors = []
        for role in cli.REQUIRED_VALIDATOR_ROLES:
            receipt_id = (
                f"AAA-M3TOP3-F05-R1-D1-{role}-"
                f"{EXPECTED_VALIDATION_LEVEL_BY_ROLE[role]}-20260906-010000-01"
            )
            validator_identity = f"root/f05_r1_{role.lower()}_d1"
            receipt = {
                "schema_version": INDEPENDENT_VALIDATION_RECEIPT_SCHEMA_VERSION,
                "receipt_id": receipt_id,
                "run_id": RUN_ID,
                "target_revision": self.target_revision,
                "validator_role": role,
                "validation_level": EXPECTED_VALIDATION_LEVEL_BY_ROLE[role],
                "validator_identity": validator_identity,
                "author_identity": EXPECTED_TARGET_AUTHOR_IDENTITY,
                "independence_assertion": EXPECTED_INDEPENDENCE_ASSERTION,
                "supporting_not_self_pass": False,
                "role_verdicts": {role: "PASS"},
                "target_author": False,
                "target_edited": False,
                "no_pass_transfer": True,
                "verdict": "PASS",
                "findings": [],
                "target_commit": self.target_commit,
                "target_tree": self.target_tree,
                "target_bundle_identity": self.target_bundle,
                "target_input_hash": self.merged_input_hash,
                "input_bindings": self.input_bindings,
            }
            raw = json.dumps(receipt, sort_keys=True, separators=(",", ":")).encode()
            relative = (RUN_ROOT / "validation" / f"{role}_R1.json").as_posix()
            self.receipt_relatives[role] = relative
            self.receipt_bytes[role] = raw
            self._write(relative, raw)
            descriptors.append({
                "role": role,
                "validation_level": EXPECTED_VALIDATION_LEVEL_BY_ROLE[role],
                "receipt_id": receipt_id,
                "validator_identity": validator_identity,
                "path": relative,
                "sha256": _sha(raw),
            })

        self.report = {
            "schema_version": AGGREGATE_VALIDATION_SCHEMA_VERSION,
            "run_id": RUN_ID,
            "target_revision": self.target_revision,
            "status": "PASS",
            "scoring_permitted": True,
            "target_author": False,
            "blocking_findings": [],
            "target_commit": self.target_commit,
            "target_tree": self.target_tree,
            "target_bundle_identity": self.target_bundle,
            "target_input_hash": self.merged_input_hash,
            "input_bindings": self.input_bindings,
            "role_verdicts": {
                role: "PASS" for role in cli.REQUIRED_VALIDATOR_ROLES
            },
            "validation_receipts": descriptors,
            "validated_target_files": self.validated_target_files,
        }
        self.report_bytes = self._write_report(self.report)
        self._commit("synthetic validation evidence")
        self.args = self._args()

    def close(self):
        self.temp.cleanup()

    def _git(self, *args: str) -> str:
        result = subprocess.run(
            ["git", *args],
            cwd=self.repo,
            text=True,
            capture_output=True,
            check=True,
        )
        return result.stdout.strip()

    def _write(self, relative: str, data: bytes) -> None:
        path = self.repo / Path(*relative.split("/"))
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def _commit(self, message: str) -> None:
        self._git("add", "--all")
        self._git("commit", "-q", "-m", message)

    def _write_report(self, report: dict) -> bytes:
        raw = json.dumps(report, sort_keys=True, separators=(",", ":")).encode()
        self._write(self.report_relative, raw)
        return raw

    def update_report_and_commit(self, **changes) -> None:
        self.report.update(changes)
        self.report_bytes = self._write_report(self.report)
        self._commit("mutated synthetic report")
        self.args = self._args()

    def _args(self) -> SimpleNamespace:
        values = {
            "repo": self.repo,
            "run_id": RUN_ID,
            "f05_input": Path(self.f05_relative),
            "f05_input_sha256": _sha(self.f05_bytes),
            "f02_input": Path(cli.EXPECTED_F02_INPUT_PATH),
            "f02_input_sha256": EXPECTED_F02_INPUT_BATCH_SHA256,
            "config": Path(cli.EXPECTED_CONFIG_PATH),
            "config_sha256": EXPECTED_CONFIG_SHA256,
            "aggregate_validation": Path(self.report_relative),
            "aggregate_validation_sha256": _sha(self.report_bytes),
            "output_dir": self.output_dir,
        }
        for role in cli.REQUIRED_VALIDATOR_ROLES:
            prefix = role.lower()
            values[f"{prefix}_receipt"] = Path(self.receipt_relatives[role])
            values[f"{prefix}_receipt_sha256"] = _sha(self.receipt_bytes[role])
        return SimpleNamespace(**values)

    def artifacts(self) -> F05ScoreArtifacts:
        return F05ScoreArtifacts(
            score_jsonl=b'{"synthetic":"scores"}\n',
            provisional_ranking_csv=b"rank,company_id\n1,KRX:000001\n",
            f02_f05_exact_five_csv=b"rank,company_id\n1,KRX:000001\n",
            target_commit=self.target_commit,
            target_tree=self.target_tree,
            merged_input_hash=self.merged_input_hash,
            engine_run_id="m3run_synthetic_no_engine_call",
        )


class TestF05R1ScoreOutputCLI(unittest.TestCase):
    def setUp(self):
        self.fixture = SyntheticValidatedRepo()

    def tearDown(self):
        self.fixture.close()

    def test_exact_environment_calls_helper_once_then_create_once_persists(self):
        artifacts = self.fixture.artifacts()
        with patch.object(cli, "build_f05_r1_outputs", return_value=artifacts) as build:
            receipt = cli.execute(self.fixture.args)
        build.assert_called_once()
        self.assertEqual(receipt["score_engine_call_count"], 1)
        self.assertEqual(receipt["target_commit"], self.fixture.target_commit)
        self.assertEqual(receipt["target_tree"], self.fixture.target_tree)
        self.assertFalse(receipt["official_top3_or_top10"])
        expected_names = {cli.SCORE_FILENAME, cli.RANKING_FILENAME, cli.FIVE_FILENAME}
        self.assertEqual(set(receipt["artifacts"]), expected_names)
        self.assertEqual(
            {path.name for path in self.fixture.output_dir.iterdir()}, expected_names
        )
        with patch.object(cli, "build_f05_r1_outputs") as second_build:
            with self.assertRaises(FileExistsError):
                cli.execute(self.fixture.args)
            second_build.assert_not_called()

    def test_output_and_hash_preflight_fail_before_helper(self):
        preexisting = self.fixture.repo / RUN_ROOT / "already-exists"
        preexisting.mkdir()
        args = copy.copy(self.fixture.args)
        args.output_dir = preexisting
        with patch.object(cli, "build_f05_r1_outputs") as build:
            with self.assertRaises(FileExistsError):
                cli.execute(args)
            build.assert_not_called()

        args = copy.copy(self.fixture.args)
        args.f05_input_sha256 = "0" * 64
        with patch.object(cli, "build_f05_r1_outputs") as build:
            with self.assertRaisesRegex(cli.F05ScoreCLIError, "SHA-256 mismatch"):
                cli.execute(args)
            build.assert_not_called()

    def test_dirty_worktree_and_target_tree_drift_fail_before_helper(self):
        (self.fixture.repo / "untracked.txt").write_text("dirty", encoding="utf-8")
        with patch.object(cli, "build_f05_r1_outputs") as build:
            with self.assertRaisesRegex(cli.F05ScoreCLIError, "clean Git worktree"):
                cli.execute(self.fixture.args)
            build.assert_not_called()
        (self.fixture.repo / "untracked.txt").unlink()

        self.fixture.update_report_and_commit(target_tree="d" * 40)
        with patch.object(cli, "build_f05_r1_outputs") as build:
            with self.assertRaisesRegex(cli.F05ScoreCLIError, "tree does not match"):
                cli.execute(self.fixture.args)
            build.assert_not_called()

    def test_validated_target_blob_drift_fails_before_helper(self):
        changed = self.fixture.repo / "tools/m3top3/core.py"
        changed.write_bytes(changed.read_bytes() + b"committed drift\n")
        self.fixture._commit("unvalidated runtime drift")
        with patch.object(cli, "build_f05_r1_outputs") as build:
            with self.assertRaisesRegex(
                cli.F05ScoreCLIError, "(?:worktree bytes|Git blob) changed"
            ):
                cli.execute(self.fixture.args)
            build.assert_not_called()

    def test_receipt_escape_and_helper_failure_never_create_output(self):
        outside_relative = "control/outside-validation/CTLV.json"
        self.fixture._write(outside_relative, self.fixture.receipt_bytes["CTLV"])
        self.fixture._commit("outside receipt")
        escaped = copy.copy(self.fixture.args)
        escaped.ctlv_receipt = Path(outside_relative)
        with patch.object(cli, "build_f05_r1_outputs") as build:
            with self.assertRaisesRegex(cli.F05ScoreCLIError, "validation directory"):
                cli.execute(escaped)
            build.assert_not_called()
        self.assertFalse(self.fixture.output_dir.exists())

        with patch.object(
            cli,
            "build_f05_r1_outputs",
            side_effect=F05ScoreOutputError("synthetic gate failure"),
        ) as build:
            with self.assertRaisesRegex(F05ScoreOutputError, "synthetic gate failure"):
                cli.execute(self.fixture.args)
            build.assert_called_once()
        self.assertFalse(self.fixture.output_dir.exists())

    def test_falsified_or_nonexistent_descriptor_path_never_calls_helper(self):
        baseline = copy.deepcopy(self.fixture.report["validation_receipts"])
        cases = (
            (
                "falsified_existing_path",
                self.fixture.receipt_relatives["MODV"],
            ),
            (
                "nonexistent_path",
                (RUN_ROOT / "validation" / "DOES_NOT_EXIST.json").as_posix(),
            ),
        )
        for name, false_path in cases:
            with self.subTest(case=name):
                descriptors = copy.deepcopy(baseline)
                next(item for item in descriptors if item["role"] == "CTLV")["path"] = (
                    false_path
                )
                self.fixture.update_report_and_commit(validation_receipts=descriptors)
                with patch.object(cli, "build_f05_r1_outputs") as build:
                    with self.assertRaisesRegex(
                        cli.F05ScoreCLIError, "descriptor path does not match"
                    ):
                        cli.execute(self.fixture.args)
                    build.assert_not_called()
                self.assertFalse(self.fixture.output_dir.exists())

    def test_helper_time_committed_runtime_drift_blocks_persistence(self):
        artifacts = self.fixture.artifacts()

        def commit_runtime_drift(**_kwargs):
            changed = self.fixture.repo / "tools/m3top3/core.py"
            changed.write_bytes(changed.read_bytes() + b"helper-time committed drift\n")
            self.fixture._commit("adversarial helper-time runtime drift")
            return artifacts

        with (
            patch.object(
                cli, "build_f05_r1_outputs", side_effect=commit_runtime_drift
            ) as build,
            patch.object(cli, "persist_f05_r1_outputs") as persist,
        ):
            with self.assertRaisesRegex(cli.F05ScoreCLIError, "HEAD changed"):
                cli.execute(self.fixture.args)
            build.assert_called_once()
            persist.assert_not_called()
        self.assertFalse(self.fixture.output_dir.exists())


if __name__ == "__main__":
    unittest.main()
