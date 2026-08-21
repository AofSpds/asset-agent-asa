import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { execFileSync } from "node:child_process";
import { mkdtempSync, mkdirSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { pathToFileURL, fileURLToPath } from "node:url";
import { after, before, test } from "node:test";

import { __testing, classifyGitFailure, verifyLocator } from "../persistent_locator.mjs";

const TEST_REPOSITORY = "AAA/TestFixture";
const TEST_LINEAGE_REF = "AAA-TEST-LINEAGE";
const TEST_RELATIONSHIP = "EXACT_SUCCESSOR_OF_DECLARED_PREDECESSOR";
const TEST_LINEAGE_PROFILE = "AAA_SUBJECT_DECLARED_EXACT_PREDECESSOR_v0.1";
const TEST_PROVENANCE_PROFILE = "AAA_OWNER_DECISION_ACCEPTED_EXACT_TARGET_PROVENANCE_v0.1";
const TEST_SEMANTIC_PROFILE = "SHA256_UTF8_CANONICAL_JSON_NORMATIVE_OVERLAY_SORT_KEYS_COMPACT_NO_TRAILING_NEWLINE";
const TEST_AUTHORITY_ID = "AAA-TEST-OWNER-AUTHORITY-v0.1";

let testRoot;
let sourcePath;
let remotePath;
let cachePath;
let locator;
let binding;
let previousTmpdir;

function gitAt(path, ...args) {
  return execFileSync("git", ["-C", path, ...args], { encoding: "utf8" }).trim();
}

function sha256(bytes) {
  return createHash("sha256").update(bytes).digest("hex");
}

function subjectIdentity(value) {
  return {
    repository: value.repository,
    exact_commit: value.exact_commit,
    exact_path: value.exact_path,
    git_blob: value.git_blob,
    sha256: value.sha256,
    byte_size: value.byte_size,
  };
}

function exactCompatibilityContext() {
  const subject = subjectIdentity(binding.subject);
  return {
    work_item_id: binding.work_item_id,
    relationship_type: binding.relationship,
    authority_principal: binding.authority_principal,
    canonical_remote: binding.canonical_remote,
    approved_semantic_scope: structuredClone(binding.approved_scope),
    owner_authority_evidence: structuredClone(binding.owner_authority),
    repository_bindings: [
      {
        repository: binding.subject.repository,
        authorized: true,
        authorization_ref: binding.owner_authority.artifact_id,
        authorization_claim_profile: "AAA_OWNER_DECISION_ACCEPTED_EXACT_TARGET_v0.1",
        authorization_evidence: structuredClone(binding.owner_authority),
        repository_host: binding.canonical_host,
        allowed_remote_urls: [binding.canonical_remote],
      },
    ],
    semantic_profiles: [
      {
        applies_to: subject,
        profile_id: binding.semantic_profile.profile_id,
        digest_algorithm: binding.semantic_profile.digest_algorithm,
        canonicalization: binding.semantic_profile.canonicalization,
        selection: {
          type: binding.semantic_profile.selection_type,
          field: binding.semantic_profile.selection_field,
        },
        authorization_ref: binding.owner_authority.artifact_id,
        authorization_evidence: structuredClone(binding.owner_authority),
      },
    ],
    lineage_records: [
      {
        lineage_ref: binding.lineage_ref,
        subject,
        proof_profile: TEST_LINEAGE_PROFILE,
        relationship_type: binding.relationship,
        referenced_artifact: structuredClone(binding.predecessor),
        authorization_ref: binding.owner_authority.artifact_id,
        authorization_evidence: structuredClone(binding.owner_authority),
      },
    ],
    provenance_records: [
      {
        lineage_ref: binding.lineage_ref,
        subject,
        relationship_type: binding.relationship,
        evidence_profile: TEST_PROVENANCE_PROFILE,
        authorization_ref: binding.owner_authority.artifact_id,
        evidence: structuredClone(binding.owner_authority),
      },
    ],
  };
}

before(() => {
  testRoot = mkdtempSync(join(resolve(process.cwd()), "aaa-persistent-locator-f01-f02-"));
  previousTmpdir = process.env.TMPDIR;
  process.env.TMPDIR = testRoot;
  sourcePath = join(testRoot, "source");
  remotePath = join(testRoot, "canonical.git");
  cachePath = join(testRoot, "cache");
  mkdirSync(sourcePath);
  execFileSync("git", ["init", "-b", "main", sourcePath]);
  gitAt(sourcePath, "config", "user.name", "AAA Test");
  gitAt(sourcePath, "config", "user.email", "aaa-test@example.invalid");
  mkdirSync(join(sourcePath, "control"));

  const predecessor = {
    artifact_id: "AAA-TEST-PREDECESSOR-v0.1",
    version: "v0.1",
    work_item_id: TEST_LINEAGE_REF,
  };
  writeFileSync(join(sourcePath, "control", "predecessor.json"), JSON.stringify(predecessor) + "\n");
  gitAt(sourcePath, "add", "control/predecessor.json");
  gitAt(sourcePath, "commit", "-m", "test: predecessor");
  const predecessorCommit = gitAt(sourcePath, "rev-parse", "HEAD");
  const predecessorTree = gitAt(sourcePath, "rev-parse", "HEAD^{tree}");
  const predecessorBlob = gitAt(sourcePath, "rev-parse", "HEAD:control/predecessor.json");
  const predecessorBytes = execFileSync("git", ["-C", sourcePath, "cat-file", "blob", predecessorBlob]);

  const target = {
    artifact_id: "AAA-TEST-TARGET-v0.2",
    version: "v0.2",
    work_item_id: TEST_LINEAGE_REF,
    normative_overlay: { enabled: true, value: 1 },
    semantic_digest_profile: TEST_SEMANTIC_PROFILE,
    lineage: {
      predecessor_exact: {
        artifact_id: predecessor.artifact_id,
        version: predecessor.version,
        commit: predecessorCommit,
        path: "control/predecessor.json",
        git_blob: predecessorBlob,
        artifact_sha256: sha256(predecessorBytes),
        byte_size: predecessorBytes.length,
      },
      successor_of_version: predecessor.version,
    },
  };
  writeFileSync(join(sourcePath, "control", "target.json"), JSON.stringify(target) + "\n");
  gitAt(sourcePath, "add", "control/target.json");
  gitAt(sourcePath, "commit", "-m", "test: exact target");
  const exactCommit = gitAt(sourcePath, "rev-parse", "HEAD");
  const exactTree = gitAt(sourcePath, "rev-parse", "HEAD^{tree}");
  const targetBlob = gitAt(sourcePath, "rev-parse", "HEAD:control/target.json");
  const targetBytes = execFileSync("git", ["-C", sourcePath, "cat-file", "blob", targetBlob]);
  const semanticDigest = sha256(Buffer.from(JSON.stringify({ enabled: true, value: 1 })));

  execFileSync("git", ["clone", "--bare", sourcePath, remotePath]);
  execFileSync("git", ["clone", remotePath, cachePath]);

  locator = {
    repository: TEST_REPOSITORY,
    exact_commit: exactCommit,
    exact_path: "control/target.json",
    git_blob: targetBlob,
    sha256: sha256(targetBytes),
    byte_size: targetBytes.length,
    semantic_content_digest_if_applicable: semanticDigest,
    lineage_ref: TEST_LINEAGE_REF,
    discovery_branch: "main",
  };
  binding = {
    object_id: "AAA-TEST-SUBJECT-SCOPED-BINDING",
    version: "v0.3",
    work_item_id: "AAA_TEST_WORK_ITEM",
    lineage_ref: TEST_LINEAGE_REF,
    relationship: TEST_RELATIONSHIP,
    canonical_remote: pathToFileURL(remotePath).href,
    canonical_host: "local.test",
    subject: {
      artifact_id: target.artifact_id,
      version: target.version,
      ...subjectIdentity(locator),
      exact_tree: exactTree,
      semantic_content_digest_if_applicable: semanticDigest,
      lineage_ref: TEST_LINEAGE_REF,
    },
    predecessor: {
      artifact_id: predecessor.artifact_id,
      version: predecessor.version,
      repository: TEST_REPOSITORY,
      exact_commit: predecessorCommit,
      exact_tree: predecessorTree,
      exact_path: "control/predecessor.json",
      git_blob: predecessorBlob,
      sha256: sha256(predecessorBytes),
      byte_size: predecessorBytes.length,
    },
    owner_authority: {
      artifact_id: TEST_AUTHORITY_ID,
      repository: TEST_REPOSITORY,
      exact_commit: "1".repeat(40),
      exact_tree: "2".repeat(40),
      exact_path: "control/authority.json",
      git_blob: "3".repeat(40),
      sha256: "4".repeat(64),
      byte_size: 100,
    },
    authority_principal: "HUMAN PROJECT OWNER",
    approved_scope: { mode: "EXACT_TEST_SCOPE", authorized: true },
    approved_scope_digest: "5".repeat(64),
    semantic_profile: {
      profile_id: TEST_SEMANTIC_PROFILE,
      digest_algorithm: "SHA256",
      canonicalization: "JSON_SORT_KEYS_COMPACT_UTF8_NO_TRAILING_NEWLINE",
      selection_type: "TOP_LEVEL_VALUE",
      selection_field: "normative_overlay",
    },
  };
});

after(() => {
  if (previousTmpdir === undefined) delete process.env.TMPDIR;
  else process.env.TMPDIR = previousTmpdir;
  if (testRoot) rmSync(testRoot, { recursive: true, force: true });
});

test("isolated exact readback mechanics pass over a new local transport operation (not Fresh external proof)", () => {
  const result = __testing.verifyLiveCanonicalRemoteProof(locator, binding);
  assert.equal(result.state, "LIVE_CANONICAL_REMOTE_VERIFIED");
  assert.equal(result.exact_commit, locator.exact_commit);
  assert.equal(result.exact_tree, binding.subject.exact_tree);
  assert.equal(result.git_blob, locator.git_blob);
  assert.equal(result.sha256, locator.sha256);
  assert.equal(result.byte_size, locator.byte_size);
});

test("proof storage is isolated and the governed repository is not fetched into", () => {
  const beforeHead = gitAt(cachePath, "rev-parse", "HEAD");
  const result = __testing.verifyLiveCanonicalRemoteProof(locator, binding);
  assert.equal(result.isolated_temporary_proof_storage, true);
  assert.equal(result.governed_repository_mutated_for_proof, false);
  assert.equal(gitAt(cachePath, "rev-parse", "HEAD"), beforeHead);
});

test("local remote-tracking refs alone are insufficient", () => {
  assert.ok(gitAt(cachePath, "for-each-ref", "--format=%(refname)", "refs/remotes/").includes("refs/remotes/origin/"));
  const unavailable = { ...binding, canonical_remote: pathToFileURL(join(testRoot, "missing-tracking.git")).href };
  const result = __testing.verifyLiveCanonicalRemoteProof(locator, unavailable);
  assert.notEqual(result.state, "LIVE_CANONICAL_REMOTE_VERIFIED");
});

test("local object cache alone is insufficient", () => {
  assert.equal(gitAt(cachePath, "cat-file", "-e", locator.exact_commit + "^{commit}"), "");
  const unavailable = { ...binding, canonical_remote: pathToFileURL(join(testRoot, "missing-cache.git")).href };
  const result = __testing.verifyLiveCanonicalRemoteProof(locator, unavailable);
  assert.notEqual(result.state, "LIVE_CANONICAL_REMOTE_VERIFIED");
});

test("generic branch or HEAD evidence is insufficient for a different exact commit", () => {
  assert.equal(gitAt(sourcePath, "rev-parse", "HEAD"), locator.exact_commit);
  const wrongCommit = "0".repeat(40);
  const changed = { ...binding, subject: { ...binding.subject, exact_commit: wrongCommit } };
  const result = __testing.verifyLiveCanonicalRemoteProof({ ...locator, exact_commit: wrongCommit }, changed);
  assert.notEqual(result.state, "LIVE_CANONICAL_REMOTE_VERIFIED");
});

test("wrong exact commit is not independently proven", () => {
  const wrongCommit = "f".repeat(40);
  const changed = { ...binding, subject: { ...binding.subject, exact_commit: wrongCommit } };
  const result = __testing.verifyLiveCanonicalRemoteProof({ ...locator, exact_commit: wrongCommit }, changed);
  assert.notEqual(result.state, "LIVE_CANONICAL_REMOTE_VERIFIED");
});

test("wrong exact tree is a remote conflict", () => {
  const changed = { ...binding, subject: { ...binding.subject, exact_tree: "a".repeat(40) } };
  const result = __testing.verifyLiveCanonicalRemoteProof(locator, changed);
  assert.equal(result.state, "LIVE_CANONICAL_REMOTE_CONFLICT");
  assert.equal(result.reason, "REMOTE_COMMIT_TREE_MISMATCH");
});

test("wrong governed path is a remote path/blob conflict", () => {
  const changedLocator = { ...locator, exact_path: "control/missing.json" };
  const changed = { ...binding, subject: { ...binding.subject, exact_path: changedLocator.exact_path } };
  const result = __testing.verifyLiveCanonicalRemoteProof(changedLocator, changed);
  assert.equal(result.state, "LIVE_CANONICAL_REMOTE_CONFLICT");
  assert.equal(result.reason, "REMOTE_PATH_BLOB_CONFLICT");
});

test("wrong governed blob is a remote path/blob conflict", () => {
  const wrongBlob = "b".repeat(40);
  const changedLocator = { ...locator, git_blob: wrongBlob };
  const changed = { ...binding, subject: { ...binding.subject, git_blob: wrongBlob } };
  const result = __testing.verifyLiveCanonicalRemoteProof(changedLocator, changed);
  assert.equal(result.state, "LIVE_CANONICAL_REMOTE_CONFLICT");
  assert.equal(result.reason, "REMOTE_PATH_BLOB_CONFLICT");
});

test("wrong fetched-content SHA256 is a content identity conflict", () => {
  const result = __testing.verifyLiveCanonicalRemoteProof({ ...locator, sha256: "c".repeat(64) }, binding);
  assert.equal(result.state, "LIVE_CANONICAL_REMOTE_CONFLICT");
  assert.equal(result.reason, "REMOTE_PATH_CONTENT_IDENTITY_MISMATCH");
});

test("wrong fetched-content byte size is a content identity conflict", () => {
  const result = __testing.verifyLiveCanonicalRemoteProof({ ...locator, byte_size: locator.byte_size + 1 }, binding);
  assert.equal(result.state, "LIVE_CANONICAL_REMOTE_CONFLICT");
  assert.equal(result.reason, "REMOTE_PATH_CONTENT_IDENTITY_MISMATCH");
});

test("network unavailable fails closed", () => {
  const unavailable = { ...binding, canonical_remote: "https://127.0.0.1:1/AAA/unavailable.git" };
  const result = __testing.verifyLiveCanonicalRemoteProof(locator, unavailable);
  assert.equal(result.state, "LIVE_CANONICAL_REMOTE_ERROR");
  assert.equal(result.reason, "REMOTE_NETWORK_FAILURE");
});

test("remote network failure is not artifact invalidity", () => {
  const unavailable = { ...binding, canonical_remote: "https://127.0.0.1:1/AAA/unavailable.git" };
  const result = __testing.verifyLiveCanonicalRemoteProof(locator, unavailable);
  assert.equal(result.reason, "REMOTE_NETWORK_FAILURE");
  assert.notEqual(result.reason, "IDENTITY_MISMATCH");
  assert.notEqual(result.reason, "ARTIFACT_INVALID");
});

test("Owner authority does not imply live canonical remote verification", () => {
  assert.equal(__testing.allRequiredAxesVerified({
    artifact_identity_state: "ARTIFACT_IDENTITY_VERIFIED",
    owner_authority_state: "OWNER_AUTHORIZED",
    live_canonical_remote_state: "LIVE_CANONICAL_REMOTE_ERROR",
    semantic_content_digest_state: "SEMANTIC_DIGEST_VERIFIED",
    lineage_state: "LINEAGE_VERIFIED",
    provenance_state: "PROVENANCE_VERIFIED",
  }), false);
});

test("live canonical remote verification does not imply Owner authority", () => {
  assert.equal(__testing.allRequiredAxesVerified({
    artifact_identity_state: "ARTIFACT_IDENTITY_VERIFIED",
    owner_authority_state: "NOT_PROVEN",
    live_canonical_remote_state: "LIVE_CANONICAL_REMOTE_VERIFIED",
    semantic_content_digest_state: "SEMANTIC_DIGEST_VERIFIED",
    lineage_state: "LINEAGE_VERIFIED",
    provenance_state: "PROVENANCE_VERIFIED",
  }), false);
});

test("top-level exact state requires every independent axis", () => {
  assert.equal(__testing.allRequiredAxesVerified({
    artifact_identity_state: "ARTIFACT_IDENTITY_VERIFIED",
    owner_authority_state: "OWNER_AUTHORIZED",
    live_canonical_remote_state: "LIVE_CANONICAL_REMOTE_VERIFIED",
    semantic_content_digest_state: "SEMANTIC_DIGEST_VERIFIED",
    lineage_state: "LINEAGE_VERIFIED",
    provenance_state: "PROVENANCE_VERIFIED",
  }), true);
});

test("exact governed subject selects exactly one trusted binding", () => {
  const result = __testing.selectGovernedBinding(locator, [binding]);
  assert.equal(result.ok, true);
  assert.equal(result.binding.owner_authority.artifact_id, TEST_AUTHORITY_ID);
});

test("a non-matching subject cannot select trusted Owner authority", () => {
  const result = __testing.selectGovernedBinding({ ...locator, exact_path: "control/other.json" }, [binding]);
  assert.equal(result.ok, false);
  assert.equal(result.reason, "GOVERNED_SUBJECT_NOT_SELECTED");
});

test("exact-matching caller data remains a compatibility assertion only", () => {
  const result = __testing.verifyCallerCompatibility(locator, exactCompatibilityContext(), binding);
  assert.equal(result.ok, true);
  assert.equal(result.asserted, true);
});

test("missing caller authority data does not select or request a trust root", () => {
  const result = __testing.verifyCallerCompatibility(locator, undefined, binding);
  assert.deepEqual(result, { ok: true, asserted: false });
  assert.equal(__testing.selectGovernedBinding(locator, [binding]).ok, true);
});

test("alternate caller-selected Owner evidence is rejected", () => {
  const context = exactCompatibilityContext();
  context.owner_authority_evidence = { ...binding.owner_authority, artifact_id: "AAA-ALTERNATE-OWNER" };
  const result = __testing.verifyCallerCompatibility(locator, context, binding);
  assert.equal(result.ok, false);
  assert.equal(result.reason, "CALLER_AUTHORITY_ASSERTION_CONFLICT");
});

test("caller relationship override is rejected", () => {
  const context = exactCompatibilityContext();
  context.lineage_records[0].relationship_type = "CALLER_SELECTED_RELATIONSHIP";
  const result = __testing.verifyCallerCompatibility(locator, context, binding);
  assert.equal(result.ok, false);
});

test("caller provenance override is rejected", () => {
  const context = exactCompatibilityContext();
  context.provenance_records[0].evidence_profile = "CALLER_SELECTED_PROVENANCE";
  const result = __testing.verifyCallerCompatibility(locator, context, binding);
  assert.equal(result.ok, false);
});

test("caller authorized-scope override is rejected", () => {
  const context = exactCompatibilityContext();
  context.approved_semantic_scope = { mode: "EXPANDED" };
  const result = __testing.verifyCallerCompatibility(locator, context, binding);
  assert.equal(result.ok, false);
});

test("caller canonical remote override is rejected", () => {
  const context = exactCompatibilityContext();
  context.repository_bindings[0].allowed_remote_urls = ["https://github.com/Caller/Selected.git"];
  const result = __testing.verifyCallerCompatibility(locator, context, binding);
  assert.equal(result.ok, false);
});

test("missing governed authority evidence fails closed", () => {
  const withoutAuthority = { ...binding, owner_authority: null };
  const result = __testing.selectGovernedBinding(locator, [withoutAuthority]);
  assert.equal(result.ok, false);
  assert.equal(result.reason, "GOVERNED_AUTHORITY_EVIDENCE_MISSING");
});

test("prior claimed network evidence cannot replace a new readback", () => {
  const context = exactCompatibilityContext();
  context.live_canonical_remote_state = "LIVE_CANONICAL_REMOTE_VERIFIED";
  context.prior_network_evidence = { state: "VERIFIED" };
  assert.equal(__testing.verifyCallerCompatibility(locator, context, binding).ok, true);
  const unavailable = { ...binding, canonical_remote: "https://127.0.0.1:1/AAA/unavailable.git" };
  assert.notEqual(__testing.verifyLiveCanonicalRemoteProof(locator, unavailable).state, "LIVE_CANONICAL_REMOTE_VERIFIED");
});

test("access denial remains distinct from absence", () => {
  const result = classifyGitFailure("fatal: Permission denied", null);
  assert.equal(result.state, "ACCESS_BLOCKED");
  assert.notEqual(result.state, "NOT_FOUND");
});

test("invalid locator identity fails before any trust selection", () => {
  const result = verifyLocator({ ...locator, git_blob: "invalid" }, { repositoryPath: cachePath });
  assert.equal(result.state, "RETRIEVAL_FAILED");
  assert.equal(result.reason, "INVALID_LOCATOR_RECORD");
  assert.equal(result.owner_authority_state, "NOT_PROVEN");
});

const runFreshExternal = process.env.AAA_RUN_FRESH_NETWORK_TESTS === "1";
test(
  "historically accepted S0 path reaches VERIFIED_EXACT with a Fresh authenticated external readback",
  { skip: runFreshExternal ? false : "Fresh authenticated external Git execution is not available in this author runtime." },
  () => {
    const projectRoot = resolve(dirname(fileURLToPath(import.meta.url)), "../../..");
    const s0 = {
      repository: "AofSpds/asset-agent-asa",
      exact_commit: "d0b0d2c7a77ca00570151e89e70e092b10646bd2",
      exact_path: "control/architecture/working-candidates/transfer-workspace/s0/plcp-shadow/v0.5/control/AAA_TW_S0_PLCP_SHADOW_INSTANCE_v0.5.json",
      git_blob: "7bc6e4c2194bc2f06d61367434cab38947b40e0d",
      sha256: "abd1d42be8b2a9b25eba266cfd939905e1799c93dc975fedcb560478cbcefdd8",
      byte_size: 13947,
      semantic_content_digest_if_applicable: "370a934edfaf72dc2e06d5e45b7c38be8026e3cf85e8d11c2903d2e342be48f2",
      lineage_ref: "AAA-PERSISTENT-LOCATOR-CAPABILITY-PROOF-v0.1",
    };
    const result = verifyLocator(s0, { repositoryPath: projectRoot });
    assert.equal(result.state, "VERIFIED_EXACT");
    assert.equal(result.artifact_identity_state, "ARTIFACT_IDENTITY_VERIFIED");
    assert.equal(result.owner_authority_state, "OWNER_AUTHORIZED");
    assert.equal(result.live_canonical_remote_state, "LIVE_CANONICAL_REMOTE_VERIFIED");
    assert.equal(result.semantic_content_digest_state, "SEMANTIC_DIGEST_VERIFIED");
    assert.equal(result.lineage_state, "LINEAGE_VERIFIED");
    assert.equal(result.provenance_state, "PROVENANCE_VERIFIED");
  },
);
