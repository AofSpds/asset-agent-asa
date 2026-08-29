#!/usr/bin/env python3
from __future__ import annotations

import ast
import hashlib
import json
import pathlib
import re
import subprocess
from copy import deepcopy

BASE_HEAD = "ee7cd5f6f48c9f13ad43071b8c7c3648c9bdd1d0"
BASE_TREE = "8888b6d7208b5c4b72d17eb887827d09c2b0c61c"
RESULT_BRANCH = "aaa-pmo-g6-generated-20260829-2215"
OLD_STAMP = "20260829204006"
NEW_STAMP = "20260829221500"
OLD_ISO = "2026-08-29T20:40:06+09:00"
NEW_ISO = "2026-08-29T22:15:00+09:00"
OLD_TOKEN_HASH = "3f5daecc1277bf12a50a6f8dcb9e92e99ca3ec5e913038b805dc4836adc59c26"
NEW_TOKEN_HASH = "3ecb5ad567e05208d76e892164d91d4a408d9ca50ab775c43c0ea294905c3c1d"
OLD_OWNER_HASH = "e30516b34e5d381856f405a0490c54c688c83ae84294d124f9931ce9d54fd2db"
NEW_OWNER_HASH = "584bb1d3ca0359f18dc4f9ac3de7644a88bb43fe4362c6c67a705e30ac27f309"

RUNTIME = "PMO-FINANCE-PAGE100-G6-20260829221500"
PILOT = "FINANCE-PAGE100-PILOT-G6-20260829221500"
GENERATION = "FINANCE-PAGE100-G6-20260829221500"
PRECHECK_ACT = "FINANCE-PAGE100-PRECHECK-ACT-G6-20260829221500"
LIVE_ACT = "FINANCE-PAGE100-LIVE-ACT-G6-20260829221500"
LATCH_EVENT = "FINANCE-PAGE100-LATCH-G6-20260829221500"
PREPARATION_MESSAGE = "Prepare M3Top3 Finance page100 G6 immutable dual-profile 20260829221500 v1.0"
PRECHECK_MESSAGE = "Arm M3Top3 Finance page100 G6 precheck 20260829221500 v1.0"
LIVE_MESSAGE = "Arm M3Top3 Finance page100 G6 bounded live pilot 20260829221500 v1.0"

WORKFLOW = pathlib.Path(".github/workflows/m3top3-finance-page100-bounded-pilot-v1.yml")
ROOT = pathlib.Path("control/m3top3/public-data-source-admission/v1.0")
AUTHORITY = ROOT / "M3TOP3_FINANCE_CA_PAGE100_PILOT_AUTHORITY_v1.0.json"
PLAN = ROOT / "M3TOP3_FINANCE_CA_PAGE100_PILOT_PLAN_v1.0.json"
CHECKPOINT = ROOT / "M3TOP3_FINANCE_CA_PAGE100_CHECKPOINT_SEED_v1.0.json"
LATCH = ROOT / "M3TOP3_FINANCE_CA_PAGE100_PILOT_LATCH_v1.0.json"
RUNNER = pathlib.Path("tools/m3top3/finance_page100_pilot.py")
STATIC_PATHS = [WORKFLOW, CHECKPOINT, AUTHORITY, PLAN, RUNNER]

G5_FAILURE = {
    "actions_artifact_digest": "sha256:05853717a7b9af6f107bd8747a7c44a6fd817a5fd5b123059898d092fc639be4",
    "actions_artifact_id": 9715080560,
    "actions_artifact_size_in_bytes": 344,
    "conclusion": "failure",
    "disposition": "TERMINAL_FAILED_PRECHECK_DO_NOT_RERUN_DO_NOT_REUSE",
    "do_not_rerun": True,
    "do_not_reuse_latch": True,
    "exact_blocker": "PREPARATION_COMMIT_MESSAGE_MISMATCH",
    "failing_step_name": "Fail-closed authority and latch preflight",
    "failing_step_number": 4,
    "generation_id": "FINANCE-PAGE100-G5-20260829204006",
    "head_sha": BASE_HEAD,
    "pilot_run_id": "FINANCE-PAGE100-PILOT-G5-20260829204006",
    "provider_api_network_attempts": 0,
    "quota_reservations": 0,
    "raw_commit_message_ascii_bytes": 76,
    "raw_commit_message_terminal_lf_count": 0,
    "remote_raw_custody_writes": 0,
    "runtime_lock_id": "PMO-FINANCE-PAGE100-G5-20260829204006",
    "side_effect_scope": "ZERO_OIDC_AWS_PROVIDER_QUOTA_S3",
    "status": "completed",
    "tree_sha": BASE_TREE,
    "workflow_job_id": 99103056660,
    "workflow_run_attempt": 1,
    "workflow_run_id": 33253477005,
}

REPLACEMENTS = [
    ("PMO-FINANCE-PAGE100-G5-20260829204006", RUNTIME),
    ("FINANCE-PAGE100-PILOT-G5-20260829204006", PILOT),
    ("FINANCE-PAGE100-PRECHECK-ACT-G5-20260829204006", PRECHECK_ACT),
    ("FINANCE-PAGE100-LIVE-ACT-G5-20260829204006", LIVE_ACT),
    ("FINANCE-PAGE100-LATCH-G5-20260829204006", LATCH_EVENT),
    ("FINANCE-PAGE100-G5-20260829204006", GENERATION),
    ("Prepare M3Top3 Finance page100 G5 immutable dual-profile 20260829204006 v1.0", PREPARATION_MESSAGE),
    ("Arm M3Top3 Finance page100 G5 precheck 20260829204006 v1.0", PRECHECK_MESSAGE),
    ("Arm M3Top3 Finance page100 G5 bounded live pilot 20260829204006 v1.0", LIVE_MESSAGE),
    (OLD_ISO, NEW_ISO),
    (OLD_TOKEN_HASH, NEW_TOKEN_HASH),
    (OLD_OWNER_HASH, NEW_OWNER_HASH),
    ("G5", "G6"),
    (OLD_STAMP, NEW_STAMP),
]


def run(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(args), check=check, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )


def canonical_text(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"


def canonical_hash(value: object) -> str:
    return hashlib.sha256(canonical_text(value).encode("utf-8")).hexdigest()


def file_hash(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def transform_string(value: str) -> str:
    for old, new in REPLACEMENTS:
        value = value.replace(old, new)
    return value


def transform(value: object) -> object:
    if isinstance(value, dict):
        return {key: transform(child) for key, child in value.items()}
    if isinstance(value, list):
        return [transform(child) for child in value]
    if isinstance(value, str):
        return transform_string(value)
    return value


def exact_replace(value: object, mapping: dict[str, str]) -> object:
    if isinstance(value, dict):
        return {key: exact_replace(child, mapping) for key, child in value.items()}
    if isinstance(value, list):
        return [exact_replace(child, mapping) for child in value]
    if isinstance(value, str):
        return mapping.get(value, value)
    return value


def strict_json(path: pathlib.Path) -> dict:
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise SystemExit("DUPLICATE_JSON_KEY:" + str(path))
            result[key] = value
        return result
    value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=pairs)
    if not isinstance(value, dict):
        raise SystemExit("TOP_LEVEL_JSON_NOT_OBJECT:" + str(path))
    return value


def replace_assignment(text: str, name: str, rendered: str) -> str:
    pattern = rf"^(\s*{re.escape(name)}\s*=\s*).+$"
    updated, count = re.subn(
        pattern, lambda match: match.group(1) + rendered,
        text, count=1, flags=re.M,
    )
    if count != 1:
        raise SystemExit("ASSIGNMENT_REPLACEMENT_COUNT:" + name + ":" + str(count))
    return updated


def assert_branch_state() -> None:
    head = run("git", "rev-parse", "HEAD").stdout.strip()
    tree = run("git", "rev-parse", "HEAD^{tree}").stdout.strip()
    if head != BASE_HEAD or tree != BASE_TREE:
        raise SystemExit("BASE_HEAD_OR_TREE_MOVED")
    remote = run(
        "git", "ls-remote", "--heads", "origin",
        "refs/heads/" + RESULT_BRANCH,
    ).stdout.strip()
    if remote:
        raise SystemExit("RESULT_BRANCH_ALREADY_EXISTS")
    if run("git", "status", "--porcelain").stdout.strip():
        raise SystemExit("WORKTREE_NOT_CLEAN")


def main() -> None:
    assert_branch_state()
    originals = {
        "workflow": WORKFLOW.read_bytes(),
        "authority": AUTHORITY.read_bytes(),
        "plan": PLAN.read_bytes(),
        "checkpoint": CHECKPOINT.read_bytes(),
        "latch": LATCH.read_bytes(),
        "runner": RUNNER.read_bytes(),
    }
    old_hashes = {
        name: hashlib.sha256(data).hexdigest()
        for name, data in originals.items()
    }

    authority = transform(strict_json(AUTHORITY))
    plan = transform(strict_json(PLAN))
    checkpoint = transform(strict_json(CHECKPOINT))
    latch = transform(strict_json(LATCH))

    authority["activation_anchor"]["activation_base_head"] = BASE_HEAD
    authority["activation_anchor"]["activation_base_tree"] = BASE_TREE
    for mode in ("PRECHECK_ARMED", "LIVE_ARMED"):
        item = authority["mode_profiles"][mode]["finance_page100_pilot_authority"]
        item["activation_base_head_commit"] = BASE_HEAD
        item["activation_base_tree"] = BASE_TREE

    plan["activation_anchor"]["resume_base_head"] = BASE_HEAD
    plan["activation_anchor"]["resume_base_tree"] = BASE_TREE
    plan["precheck_freeze_register"]["resume_base_head"] = BASE_HEAD
    plan["precheck_freeze_register"]["resume_base_tree"] = BASE_TREE
    checkpoint["activation_base_head_commit"] = BASE_HEAD
    checkpoint["activation_base_tree"] = BASE_TREE

    authority["issued_at_kst"] = NEW_ISO
    plan["updated_at_kst"] = NEW_ISO
    checkpoint["updated_at_kst"] = NEW_ISO
    checkpoint["state"] = "GENERATION_6_S3_DURABLE_CAS_SEED_STAGED_NOT_EXECUTED"
    for value in (authority, plan, checkpoint, latch):
        value["failed_generation_terminal"] = deepcopy(G5_FAILURE)
    authority["owner_packet_binding"]["successor_execution_token_sha256"] = NEW_TOKEN_HASH

    runner = originals["runner"].decode("utf-8")
    for old, new in REPLACEMENTS:
        runner = runner.replace(old, new)
    runner = replace_assignment(runner, "ACTIVATION_BASE_HEAD_COMMIT", json.dumps(BASE_HEAD))
    runner = replace_assignment(runner, "FAILED_PRECHECK_WORKFLOW_RUN_ID", "33253477005")
    runner = replace_assignment(runner, "FAILED_PRECHECK_WORKFLOW_JOB_ID", "99103056660")
    runner = replace_assignment(runner, "FAILED_PRECHECK_HEAD_SHA", json.dumps(BASE_HEAD))
    ast.parse(runner)

    workflow = originals["workflow"].decode("utf-8")
    for old, new in REPLACEMENTS:
        workflow = workflow.replace(old, new)
    workflow = replace_assignment(workflow, "EXPECTED_RESUME_BASE_HEAD", json.dumps(BASE_HEAD))
    workflow = replace_assignment(workflow, "EXPECTED_RESUME_BASE_TREE", json.dumps(BASE_TREE))
    workflow = replace_assignment(workflow, "EXPECTED_FAILED_RUN_ID", "33253477005")
    workflow = replace_assignment(workflow, "EXPECTED_FAILED_JOB_ID", "99103056660")
    workflow = replace_assignment(workflow, "EXPECTED_FAILED_HEAD", json.dumps(BASE_HEAD))
    workflow = replace_assignment(workflow, "EXPECTED_FAILED_TREE", json.dumps(BASE_TREE))
    workflow = replace_assignment(workflow, "FAILED_RUN_ID", "33253477005")
    workflow = replace_assignment(workflow, "FAILED_JOB_ID", "99103056660")
    workflow = replace_assignment(workflow, "FAILED_HEAD_SHA", json.dumps(BASE_HEAD))
    workflow = replace_assignment(workflow, "FAILED_ARTIFACT_ID", "9715080560")
    workflow = replace_assignment(
        workflow, "FAILED_ARTIFACT_DIGEST",
        json.dumps("sha256:05853717a7b9af6f107bd8747a7c44a6fd817a5fd5b123059898d092fc639be4"),
    )
    workflow = replace_assignment(workflow, "FAILED_ARTIFACT_SIZE", "344")

    old_contract = (
        '          require(\n'
        '              prep_message == (EXPECTED_PREPARATION_MESSAGE + "\\n").encode("utf-8"),\n'
        '              "PREPARATION_COMMIT_MESSAGE_MISMATCH",\n'
        '          )'
    )
    new_contract = (
        '          expected_preparation_body = EXPECTED_PREPARATION_MESSAGE.encode("utf-8")\n'
        '          require(\n'
        '              prep_message in {expected_preparation_body, expected_preparation_body + b"\\n"},\n'
        '              "PREPARATION_COMMIT_MESSAGE_MISMATCH",\n'
        '          )'
    )
    if workflow.count(old_contract) != 1:
        raise SystemExit("RAW_COMMIT_MESSAGE_CONTRACT_TARGET_MISMATCH")
    workflow = workflow.replace(old_contract, new_contract)

    runner_hash = hashlib.sha256(runner.encode("utf-8")).hexdigest()
    workflow_hash = hashlib.sha256(workflow.encode("utf-8")).hexdigest()
    authority_text = canonical_text(authority)
    authority_hash = hashlib.sha256(authority_text.encode("utf-8")).hexdigest()

    plan = exact_replace(plan, {
        old_hashes["authority"]: authority_hash,
        old_hashes["runner"]: runner_hash,
        old_hashes["workflow"]: workflow_hash,
    })
    plan_text = canonical_text(plan)
    plan_hash = hashlib.sha256(plan_text.encode("utf-8")).hexdigest()

    checkpoint = exact_replace(checkpoint, {
        old_hashes["authority"]: authority_hash,
        old_hashes["plan"]: plan_hash,
        old_hashes["runner"]: runner_hash,
        old_hashes["workflow"]: workflow_hash,
    })
    checkpoint_text = canonical_text(checkpoint)
    checkpoint_hash = hashlib.sha256(checkpoint_text.encode("utf-8")).hexdigest()

    WORKFLOW.write_text(workflow, encoding="utf-8")
    AUTHORITY.write_text(authority_text, encoding="utf-8")
    PLAN.write_text(plan_text, encoding="utf-8")
    CHECKPOINT.write_text(checkpoint_text, encoding="utf-8")
    RUNNER.write_text(runner, encoding="utf-8")

    actual = {
        "authority": file_hash(AUTHORITY),
        "plan": file_hash(PLAN),
        "checkpoint": file_hash(CHECKPOINT),
        "runner": file_hash(RUNNER),
        "workflow": file_hash(WORKFLOW),
    }
    expected = {
        "authority": authority_hash,
        "plan": plan_hash,
        "checkpoint": checkpoint_hash,
        "runner": runner_hash,
        "workflow": workflow_hash,
    }
    if actual != expected:
        raise SystemExit("STATIC_HASH_RECOMPUTATION_MISMATCH")

    run("git", "add", *[str(path) for path in STATIC_PATHS])
    staged = run("git", "diff", "--cached", "--name-status", "--no-renames").stdout.splitlines()
    expected_staged = [
        "M\t" + str(WORKFLOW),
        "M\t" + str(CHECKPOINT),
        "M\t" + str(AUTHORITY),
        "M\t" + str(PLAN),
        "M\t" + str(RUNNER),
    ]
    if staged != expected_staged:
        raise SystemExit("PREPARATION_TOUCH_SET_MISMATCH:" + repr(staged))
    run("git", "commit", "--no-gpg-sign", "--cleanup=verbatim", "-m", PREPARATION_MESSAGE)
    preparation_head = run("git", "rev-parse", "HEAD").stdout.strip()
    preparation_tree = run("git", "rev-parse", "HEAD^{tree}").stdout.strip()
    preparation_parent = run("git", "rev-parse", "HEAD^").stdout.strip()
    preparation_parent_tree = run("git", "rev-parse", "HEAD^^{tree}").stdout.strip()
    if preparation_parent != BASE_HEAD or preparation_parent_tree != BASE_TREE:
        raise SystemExit("PREPARATION_PARENT_MISMATCH")

    latch = exact_replace(latch, {
        old_hashes["authority"]: authority_hash,
        old_hashes["plan"]: plan_hash,
        old_hashes["checkpoint"]: checkpoint_hash,
        old_hashes["runner"]: runner_hash,
        old_hashes["workflow"]: workflow_hash,
    })
    latch["preparation_commit"]["exact_commit_message"] = PREPARATION_MESSAGE
    latch["preparation_commit"]["head_sha"] = preparation_head
    latch["preparation_commit"]["tree_sha"] = preparation_tree
    latch["preparation_commit"]["parent_sha"] = BASE_HEAD
    latch["preparation_commit"]["parent_tree_sha"] = BASE_TREE
    latch["mode"] = "PRECHECK_ARMED"
    latch["state"] = "ARMED"
    latch["activation_commit_message"] = PRECHECK_MESSAGE
    latch["provider_api_calls_authorized"] = False
    latch["quota_reservations_authorized"] = False
    latch["remote_raw_custody_writes_authorized"] = False
    latch["execution_material_sha256"] = canonical_hash(latch["execution_material"])
    LATCH.write_text(canonical_text(latch), encoding="utf-8")

    run("git", "add", str(LATCH))
    latch_staged = run("git", "diff", "--cached", "--name-status", "--no-renames").stdout.splitlines()
    if latch_staged != ["M\t" + str(LATCH)]:
        raise SystemExit("LATCH_TOUCH_SET_MISMATCH:" + repr(latch_staged))
    run("git", "commit", "--no-gpg-sign", "--cleanup=verbatim", "-m", PRECHECK_MESSAGE)
    latch_head = run("git", "rev-parse", "HEAD").stdout.strip()
    latch_tree = run("git", "rev-parse", "HEAD^{tree}").stdout.strip()
    if run("git", "rev-parse", "HEAD^").stdout.strip() != preparation_head:
        raise SystemExit("LATCH_PARENT_MISMATCH")

    run("git", "push", "origin", "HEAD:refs/heads/" + RESULT_BRANCH)
    manifest = {
        "artifact": "M3TOP3_FINANCE_PAGE100_G6_GENERATION_MANIFEST_v1.0",
        "state": "GENERATED_NOT_ACTIVATED",
        "base_head": BASE_HEAD,
        "base_tree": BASE_TREE,
        "result_branch": RESULT_BRANCH,
        "preparation_head": preparation_head,
        "preparation_tree": preparation_tree,
        "preparation_message": PREPARATION_MESSAGE,
        "latch_head": latch_head,
        "latch_tree": latch_tree,
        "latch_message": PRECHECK_MESSAGE,
        "static_hashes": actual,
        "latch_sha256": file_hash(LATCH),
        "execution_material_sha256": latch["execution_material_sha256"],
        "execution_token_sha256": NEW_TOKEN_HASH,
        "owner_cap_spec_sha256": NEW_OWNER_HASH,
        "failed_g5_run": 33253477005,
        "failed_g5_disposition": "TERMINAL_DO_NOT_RERUN_DO_NOT_REUSE",
        "provider_calls": 0,
        "quota_reservations": 0,
        "remote_writes": 0,
        "validation_claim": "NONE",
        "gate_effect": "NONE",
    }
    pathlib.Path("/tmp/g6-generation-manifest.json").write_text(
        canonical_text(manifest), encoding="utf-8"
    )
    print(canonical_text(manifest), end="")


if __name__ == "__main__":
    main()
