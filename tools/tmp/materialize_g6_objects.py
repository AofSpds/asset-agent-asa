#!/usr/bin/env python3
from __future__ import annotations

import base64
import hashlib
import importlib.util
import json
import os
import pathlib
import subprocess
import urllib.error
import urllib.request

REPOSITORY = "AofSpds/asset-agent-asa"
BASE_HEAD = "ee7cd5f6f48c9f13ad43071b8c7c3648c9bdd1d0"
BASE_TREE = "8888b6d7208b5c4b72d17eb887827d09c2b0c61c"
PREPARATION_MESSAGE = "Prepare M3Top3 Finance page100 G6 immutable dual-profile 20260829221500 v1.0"
PRECHECK_MESSAGE = "Arm M3Top3 Finance page100 G6 precheck 20260829221500 v1.0"
LATCH_PATH = "control/m3top3/public-data-source-admission/v1.0/M3TOP3_FINANCE_CA_PAGE100_PILOT_LATCH_v1.0.json"
STATIC_PATHS = [
    ".github/workflows/m3top3-finance-page100-bounded-pilot-v1.yml",
    "control/m3top3/public-data-source-admission/v1.0/M3TOP3_FINANCE_CA_PAGE100_CHECKPOINT_SEED_v1.0.json",
    "control/m3top3/public-data-source-admission/v1.0/M3TOP3_FINANCE_CA_PAGE100_PILOT_AUTHORITY_v1.0.json",
    "control/m3top3/public-data-source-admission/v1.0/M3TOP3_FINANCE_CA_PAGE100_PILOT_PLAN_v1.0.json",
    "tools/m3top3/finance_page100_pilot.py",
]


def run(*args: str) -> str:
    return subprocess.run(
        list(args), check=True, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    ).stdout.strip()


def canonical_text(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"


def canonical_hash(value: object) -> str:
    return hashlib.sha256(canonical_text(value).encode("utf-8")).hexdigest()


def api(method: str, path: str, payload: object | None = None) -> dict:
    token = os.environ.get("GH_TOKEN", "")
    if not token:
        raise SystemExit("GH_TOKEN_MISSING")
    url = "https://api.github.com/repos/" + REPOSITORY + path
    body = None if payload is None else json.dumps(payload, separators=(",", ":")).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        method=method,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": "Bearer " + token,
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "AAA-M3Top3-G6-GitObjectMaterializer/1.0",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            data = response.read(10_000_001)
    except urllib.error.HTTPError as exc:
        detail = exc.read(20_001).decode("utf-8", "replace")
        raise SystemExit("GITHUB_API_HTTP_ERROR:" + str(exc.code) + ":" + detail) from None
    if len(data) > 10_000_000:
        raise SystemExit("GITHUB_API_RESPONSE_TOO_LARGE")
    value = json.loads(data)
    if not isinstance(value, dict):
        raise SystemExit("GITHUB_API_RESPONSE_NOT_OBJECT")
    return value


def create_blob(path: pathlib.Path) -> str:
    result = api("POST", "/git/blobs", {
        "content": base64.b64encode(path.read_bytes()).decode("ascii"),
        "encoding": "base64",
    })
    sha = str(result.get("sha", ""))
    if len(sha) != 40:
        raise SystemExit("BLOB_SHA_INVALID:" + str(path))
    return sha


def create_tree(base_tree: str, entries: list[dict]) -> str:
    result = api("POST", "/git/trees", {"base_tree": base_tree, "tree": entries})
    sha = str(result.get("sha", ""))
    if len(sha) != 40:
        raise SystemExit("TREE_SHA_INVALID")
    return sha


def create_commit(message: str, tree: str, parent: str) -> str:
    result = api("POST", "/git/commits", {
        "message": message,
        "tree": tree,
        "parents": [parent],
    })
    sha = str(result.get("sha", ""))
    if len(sha) != 40:
        raise SystemExit("COMMIT_SHA_INVALID")
    if result.get("tree", {}).get("sha") != tree:
        raise SystemExit("COMMIT_TREE_READBACK_MISMATCH")
    parents = [item.get("sha") for item in result.get("parents", [])]
    if parents != [parent]:
        raise SystemExit("COMMIT_PARENT_READBACK_MISMATCH")
    return sha


def main() -> None:
    generator_path = pathlib.Path(os.environ["GENERATOR_SCRIPT"])
    spec = importlib.util.spec_from_file_location("g6_generator", generator_path)
    if spec is None or spec.loader is None:
        raise SystemExit("GENERATOR_IMPORT_SPEC_FAILED")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    original_run = module.run

    def patched_run(*args: str, check: bool = True):
        if len(args) >= 2 and args[0] == "git" and args[1] == "push":
            return subprocess.CompletedProcess(args=list(args), returncode=0, stdout="", stderr="")
        return original_run(*args, check=check)

    module.run = patched_run
    module.main()

    local_c = run("git", "rev-parse", "HEAD")
    local_p = run("git", "rev-parse", "HEAD^")
    local_p_tree = run("git", "rev-parse", local_p + "^{tree}")
    if run("git", "rev-parse", local_p + "^") != BASE_HEAD:
        raise SystemExit("LOCAL_PREPARATION_PARENT_MISMATCH")

    static_entries = []
    static_hashes = {}
    for path_text in STATIC_PATHS:
        path = pathlib.Path(path_text)
        blob_sha = create_blob(path)
        static_entries.append({
            "path": path_text,
            "mode": "100644",
            "type": "blob",
            "sha": blob_sha,
        })
        static_hashes[path_text] = hashlib.sha256(path.read_bytes()).hexdigest()
    remote_p_tree = create_tree(BASE_TREE, static_entries)
    if remote_p_tree != local_p_tree:
        raise SystemExit("REMOTE_PREPARATION_TREE_MISMATCH")
    remote_p = create_commit(PREPARATION_MESSAGE, remote_p_tree, BASE_HEAD)

    latch_path = pathlib.Path(LATCH_PATH)
    latch = json.loads(latch_path.read_text(encoding="utf-8"))
    latch["preparation_commit"]["head_sha"] = remote_p
    latch["preparation_commit"]["tree_sha"] = remote_p_tree
    latch["preparation_commit"]["parent_sha"] = BASE_HEAD
    latch["preparation_commit"]["parent_tree_sha"] = BASE_TREE
    latch["execution_material_sha256"] = canonical_hash(latch["execution_material"])
    latch_path.write_text(canonical_text(latch), encoding="utf-8")

    latch_blob = create_blob(latch_path)
    remote_c_tree = create_tree(remote_p_tree, [{
        "path": LATCH_PATH,
        "mode": "100644",
        "type": "blob",
        "sha": latch_blob,
    }])
    remote_c = create_commit(PRECHECK_MESSAGE, remote_c_tree, remote_p)

    manifest = {
        "artifact": "M3TOP3_FINANCE_PAGE100_G6_REMOTE_GIT_OBJECT_MANIFEST_v1.0",
        "state": "REMOTE_OBJECTS_CREATED_REFS_NOT_MOVED",
        "base_head": BASE_HEAD,
        "base_tree": BASE_TREE,
        "local_preparation_head": local_p,
        "local_latch_head": local_c,
        "remote_preparation_head": remote_p,
        "remote_preparation_tree": remote_p_tree,
        "remote_latch_head": remote_c,
        "remote_latch_tree": remote_c_tree,
        "preparation_message": PREPARATION_MESSAGE,
        "precheck_message": PRECHECK_MESSAGE,
        "static_sha256": static_hashes,
        "latch_sha256": hashlib.sha256(latch_path.read_bytes()).hexdigest(),
        "execution_material_sha256": latch["execution_material_sha256"],
        "failed_g5_run": 33253477005,
        "failed_g5_disposition": "TERMINAL_DO_NOT_RERUN_DO_NOT_REUSE",
        "refs_updated": False,
        "provider_calls": 0,
        "quota_reservations": 0,
        "remote_s3_writes": 0,
        "validation_claim": "NONE",
        "gate_effect": "NONE",
    }
    output = pathlib.Path("/tmp/g6-remote-object-manifest.json")
    output.write_text(canonical_text(manifest), encoding="utf-8")
    print(canonical_text(manifest), end="")


if __name__ == "__main__":
    main()
