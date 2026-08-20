import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { execFileSync } from "node:child_process";
import { mkdtempSync, mkdirSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { after, before, test } from "node:test";

import { classifyGitFailure, verifyLocator } from "../persistent_locator.mjs";

let repositoryPath;
let locator;

function git(...args) {
  return execFileSync("git", ["-C", repositoryPath, ...args], { encoding: "utf8" }).trim();
}

before(() => {
  repositoryPath = mkdtempSync(join(tmpdir(), "aaa-persistent-locator-"));
  execFileSync("git", ["init", "-b", "main", repositoryPath]);
  git("config", "user.name", "AAA Test");
  git("config", "user.email", "aaa-test@example.invalid");
  mkdirSync(join(repositoryPath, "control"));
  const bytes = Buffer.from('{"artifact_id":"AAA-TEST-TARGET","value":1}\n', "utf8");
  writeFileSync(join(repositoryPath, "control", "target.json"), bytes);
  git("add", "control/target.json");
  git("commit", "-m", "test: add exact target");
  const exactCommit = git("rev-parse", "HEAD");
  const gitBlob = git("rev-parse", `${exactCommit}:control/target.json`);
  locator = {
    repository: "AofSpds/asset-agent-asa",
    exact_commit: exactCommit,
    exact_path: "control/target.json",
    git_blob: gitBlob,
    sha256: createHash("sha256").update(bytes).digest("hex"),
    byte_size: bytes.length,
    semantic_content_digest_if_applicable: null,
    lineage_ref: "AAA-TEST-LINEAGE",
    discovery_branch: "main",
  };
});

after(() => {
  rmSync(repositoryPath, { recursive: true, force: true });
});

test("exact commit/path/blob/hash/size resolves VERIFIED_EXACT", () => {
  const result = verifyLocator(locator, { repositoryPath });
  assert.equal(result.state, "VERIFIED_EXACT");
  assert.equal(result.verified, true);
  assert.equal(result.discovery_branch_used_for_identity, false);
});

test("branch movement cannot change pinned content identity", () => {
  writeFileSync(join(repositoryPath, "control", "target.json"), '{"artifact_id":"AAA-TEST-TARGET","value":2}\n');
  git("add", "control/target.json");
  git("commit", "-m", "test: move discovery branch");
  const result = verifyLocator(locator, { repositoryPath });
  assert.equal(result.state, "VERIFIED_EXACT");
  assert.equal(result.exact_commit, locator.exact_commit);
});

test("wrong commit is NOT_FOUND", () => {
  const result = verifyLocator({ ...locator, exact_commit: "0".repeat(40) }, { repositoryPath });
  assert.equal(result.state, "NOT_FOUND");
  assert.equal(result.verified, false);
});

test("wrong path is NOT_FOUND", () => {
  const result = verifyLocator({ ...locator, exact_path: "control/missing.json" }, { repositoryPath });
  assert.equal(result.state, "NOT_FOUND");
  assert.equal(result.verified, false);
});

test("modified expected identity is RETRIEVAL_FAILED, not NOT_FOUND", () => {
  const result = verifyLocator({ ...locator, sha256: "f".repeat(64) }, { repositoryPath });
  assert.equal(result.state, "RETRIEVAL_FAILED");
  assert.equal(result.reason, "IDENTITY_MISMATCH");
  assert.deepEqual(result.mismatch_fields, ["sha256"]);
});

test("access denial maps to ACCESS_BLOCKED without an absence inference", () => {
  const result = classifyGitFailure("fatal: Permission denied", null);
  assert.equal(result.state, "ACCESS_BLOCKED");
  assert.notEqual(result.state, "NOT_FOUND");
});
