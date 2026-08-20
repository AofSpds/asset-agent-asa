import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { execFileSync } from "node:child_process";
import { mkdtempSync, mkdirSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { after, before, test } from "node:test";

import { classifyGitFailure, verifyLocator } from "../persistent_locator.mjs";

const TEST_REPOSITORY = "AAA/TestFixture";
const TEST_REMOTE = "https://github.com/AAA/TestFixture.git";
const TEST_LINEAGE_REF = "AAA-TEST-LINEAGE";
const TEST_RELATIONSHIP = "EXACT_SUCCESSOR_OF_DECLARED_PREDECESSOR";
const TEST_LINEAGE_PROFILE = "AAA_SUBJECT_DECLARED_EXACT_PREDECESSOR_v0.1";
const TEST_PROVENANCE_PROFILE = "AAA_OWNER_DECISION_ACCEPTED_EXACT_TARGET_PROVENANCE_v0.1";
const TEST_AUTHORIZATION_REF = "AAA-TEST-OWNER-DECISION";
const TEST_SEMANTIC_PROFILE = "SHA256_UTF8_CANONICAL_JSON_NORMATIVE_OVERLAY_SORT_KEYS_COMPACT_NO_TRAILING_NEWLINE";

let repositoryPath;
let locator;
let verificationContext;
let predecessorIdentity;
let nonPredecessorIdentity;

function git(...args) {
  return execFileSync("git", ["-C", repositoryPath, ...args], { encoding: "utf8" }).trim();
}

function stableValue(value) {
  if (Array.isArray(value)) return value.map(stableValue);
  if (value && typeof value === "object") {
    return Object.fromEntries(Object.keys(value).sort().map((key) => [key, stableValue(value[key])]));
  }
  return value;
}

function sha256(bytes) {
  return createHash("sha256").update(bytes).digest("hex");
}

function identityAt(exactCommit, exactPath, artifactId) {
  const gitBlob = git("rev-parse", `${exactCommit}:${exactPath}`);
  const blobBytes = execFileSync("git", ["-C", repositoryPath, "cat-file", "blob", gitBlob]);
  return {
    artifact_id: artifactId,
    repository: TEST_REPOSITORY,
    exact_commit: exactCommit,
    exact_path: exactPath,
    git_blob: gitBlob,
    sha256: sha256(blobBytes),
    byte_size: blobBytes.length,
  };
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

before(() => {
  repositoryPath = mkdtempSync(join(tmpdir(), "aaa-persistent-locator-correction-"));
  execFileSync("git", ["init", "-b", "main", repositoryPath]);
  git("config", "user.name", "AAA Test");
  git("config", "user.email", "aaa-test@example.invalid");
  git("remote", "add", "origin", TEST_REMOTE);
  mkdirSync(join(repositoryPath, "control"));

  const predecessorArtifact = {
    artifact_id: "AAA-TEST-PREDECESSOR-v0.1",
    version: "v0.1",
    work_item_id: TEST_LINEAGE_REF,
  };
  const nonPredecessorArtifact = {
    artifact_id: "AAA-TEST-NON-PREDECESSOR-v0.1",
    version: "v0.1-alternative",
    work_item_id: TEST_LINEAGE_REF,
  };
  writeFileSync(join(repositoryPath, "control", "predecessor.json"), `${JSON.stringify(predecessorArtifact, null, 2)}\n`);
  writeFileSync(join(repositoryPath, "control", "non-predecessor.json"), `${JSON.stringify(nonPredecessorArtifact, null, 2)}\n`);
  git("add", "control/predecessor.json", "control/non-predecessor.json");
  git("commit", "-m", "test: add exact predecessor and substitution candidate");
  const predecessorCommit = git("rev-parse", "HEAD");
  predecessorIdentity = identityAt(predecessorCommit, "control/predecessor.json", predecessorArtifact.artifact_id);
  predecessorIdentity.version = predecessorArtifact.version;
  nonPredecessorIdentity = identityAt(predecessorCommit, "control/non-predecessor.json", nonPredecessorArtifact.artifact_id);
  nonPredecessorIdentity.version = nonPredecessorArtifact.version;

  const targetArtifact = {
    artifact_id: "AAA-TEST-TARGET-v0.2",
    version: "v0.2",
    work_item_id: TEST_LINEAGE_REF,
    normative_overlay: { enabled: true, value: 1 },
    semantic_digest_profile: TEST_SEMANTIC_PROFILE,
    lineage: {
      predecessor_exact: {
        artifact_id: predecessorIdentity.artifact_id,
        version: predecessorIdentity.version,
        commit: predecessorIdentity.exact_commit,
        path: predecessorIdentity.exact_path,
        git_blob: predecessorIdentity.git_blob,
        artifact_sha256: predecessorIdentity.sha256,
        byte_size: predecessorIdentity.byte_size,
      },
      successor_of_version: predecessorIdentity.version,
    },
  };
  writeFileSync(join(repositoryPath, "control", "target.json"), `${JSON.stringify(targetArtifact, null, 2)}\n`);
  git("add", "control/target.json");
  git("commit", "-m", "test: add exact successor target");
  const exactCommit = git("rev-parse", "HEAD");

  const targetIdentity = identityAt(exactCommit, "control/target.json", targetArtifact.artifact_id);
  const semanticDigest = sha256(Buffer.from(JSON.stringify(stableValue(targetArtifact.normative_overlay))));

  const authorizationArtifact = {
    artifact_id: TEST_AUTHORIZATION_REF,
    artifact_kind: "OWNER_DECISION_RECEIPT_AUTHORITY_ARTIFACT",
    authority_principal: "HUMAN PROJECT OWNER",
    receipt_role: "AUTHORITY_EVIDENCE_NOT_SECOND_SEMANTIC_SOT",
    approved_semantic_scope: {
      s0_result_accepted: true,
      apply_validated_s0_capability: true,
    },
    accepted_exact_s0_target: {
      artifact_id: targetIdentity.artifact_id,
      repository: targetIdentity.repository,
      commit: targetIdentity.exact_commit,
      path: targetIdentity.exact_path,
      git_blob: targetIdentity.git_blob,
      sha256: targetIdentity.sha256,
      byte_size: targetIdentity.byte_size,
    },
  };
  writeFileSync(join(repositoryPath, "control", "authorization.json"), `${JSON.stringify(authorizationArtifact, null, 2)}\n`);
  git("add", "control/authorization.json");
  git("commit", "-m", "test: add explicit authorization evidence");

  const authorizationCommit = git("rev-parse", "HEAD");
  const authorizationIdentity = identityAt(authorizationCommit, "control/authorization.json", TEST_AUTHORIZATION_REF);

  locator = {
    ...subjectIdentity(targetIdentity),
    semantic_content_digest_if_applicable: semanticDigest,
    lineage_ref: TEST_LINEAGE_REF,
    discovery_branch: "main",
  };

  const subject = subjectIdentity(locator);
  verificationContext = {
    repository_bindings: [
      {
        repository: TEST_REPOSITORY,
        authorized: true,
        authorization_ref: TEST_AUTHORIZATION_REF,
        authorization_claim_profile: "AAA_OWNER_DECISION_ACCEPTED_EXACT_TARGET_v0.1",
        authorization_evidence: authorizationIdentity,
        remote_name: "origin",
        repository_host: "github.com",
        allowed_remote_urls: [TEST_REMOTE],
        require_commit_reachable_from_remote_tracking_ref: true,
      },
    ],
    semantic_profiles: [
      {
        applies_to: subject,
        authorized: true,
        authorization_ref: TEST_AUTHORIZATION_REF,
        authorization_claim_profile: "AAA_OWNER_DECISION_ACCEPTED_EXACT_TARGET_v0.1",
        authorization_evidence: authorizationIdentity,
        profile_id: TEST_SEMANTIC_PROFILE,
        digest_algorithm: "SHA256",
        canonicalization: "JSON_SORT_KEYS_COMPACT_UTF8_NO_TRAILING_NEWLINE",
        selection: { type: "TOP_LEVEL_VALUE", field: "normative_overlay" },
      },
    ],
    lineage_records: [
      {
        lineage_ref: TEST_LINEAGE_REF,
        subject,
        proof_profile: TEST_LINEAGE_PROFILE,
        referenced_artifact: predecessorIdentity,
        relationship_type: TEST_RELATIONSHIP,
        authorization_ref: TEST_AUTHORIZATION_REF,
        authorization_claim_profile: "AAA_OWNER_DECISION_ACCEPTED_EXACT_TARGET_v0.1",
        authorization_evidence: authorizationIdentity,
      },
    ],
    provenance_records: [
      {
        subject,
        lineage_ref: TEST_LINEAGE_REF,
        relationship_type: TEST_RELATIONSHIP,
        evidence_profile: TEST_PROVENANCE_PROFILE,
        authorization_ref: TEST_AUTHORIZATION_REF,
        authorization_claim_profile: "AAA_OWNER_DECISION_ACCEPTED_EXACT_TARGET_v0.1",
        evidence: authorizationIdentity,
      },
    ],
  };

  git("update-ref", "refs/remotes/origin/main", authorizationCommit);
});

after(() => {
  rmSync(repositoryPath, { recursive: true, force: true });
});

test("explicit repository, lineage, semantic profile, and provenance evidence succeeds", () => {
  const result = verifyLocator(locator, { repositoryPath, verificationContext });
  assert.equal(result.state, "VERIFIED_EXACT");
  assert.equal(result.verified, true);
  assert.equal(result.repository_identity_state, "REPOSITORY_VERIFIED");
  assert.equal(result.semantic_content_digest_state, "SEMANTIC_DIGEST_VERIFIED");
  assert.equal(result.lineage_state, "LINEAGE_VERIFIED");
  assert.equal(result.lineage_proof_profile, TEST_LINEAGE_PROFILE);
  assert.equal(result.lineage_referenced_artifact_id, predecessorIdentity.artifact_id);
  assert.equal(result.provenance_state, "PROVENANCE_VERIFIED");
  assert.equal(result.provenance_evidence_profile, TEST_PROVENANCE_PROFILE);
  assert.equal(result.discovery_branch_used_for_identity, false);
});

test("branch movement cannot change pinned content identity", () => {
  writeFileSync(join(repositoryPath, "control", "target.json"), '{"artifact_id":"AAA-TEST-TARGET","value":2}\n');
  git("add", "control/target.json");
  git("commit", "-m", "test: move discovery branch");
  const result = verifyLocator(locator, { repositoryPath, verificationContext });
  assert.equal(result.state, "VERIFIED_EXACT");
  assert.equal(result.exact_commit, locator.exact_commit);
});

test("wrong commit is NOT_FOUND", () => {
  const result = verifyLocator(
    { ...locator, exact_commit: "0".repeat(40) },
    { repositoryPath, verificationContext },
  );
  assert.equal(result.state, "NOT_FOUND");
  assert.equal(result.verified, false);
});

test("wrong path is NOT_FOUND", () => {
  const result = verifyLocator(
    { ...locator, exact_path: "control/missing.json" },
    { repositoryPath, verificationContext },
  );
  assert.equal(result.state, "NOT_FOUND");
  assert.equal(result.verified, false);
});

test("modified expected content identity is RETRIEVAL_FAILED", () => {
  const result = verifyLocator(
    { ...locator, sha256: "f".repeat(64) },
    { repositoryPath, verificationContext },
  );
  assert.equal(result.state, "RETRIEVAL_FAILED");
  assert.equal(result.reason, "IDENTITY_MISMATCH");
  assert.deepEqual(result.mismatch_fields, ["sha256"]);
});

test("access denial maps to ACCESS_BLOCKED without absence inference", () => {
  const result = classifyGitFailure("fatal: Permission denied", null);
  assert.equal(result.state, "ACCESS_BLOCKED");
  assert.notEqual(result.state, "NOT_FOUND");
});

test("missing verification context is rejected", () => {
  const result = verifyLocator(locator, { repositoryPath });
  assert.equal(result.state, "RETRIEVAL_FAILED");
  assert.equal(result.reason, "VERIFICATION_CONTEXT_REQUIRED");
  assert.equal(result.provenance_state, "NOT_PROVEN");
});

test("wrong repository identity is rejected", () => {
  const result = verifyLocator(
    { ...locator, repository: "WrongOwner/WrongRepository" },
    { repositoryPath, verificationContext },
  );
  assert.equal(result.state, "RETRIEVAL_FAILED");
  assert.equal(result.reason, "REPOSITORY_IDENTITY_NOT_PROVEN");
  assert.equal(result.repository_identity_state, "NOT_PROVEN");
});

test("wrong lineage reference is rejected as NOT_PROVEN", () => {
  const result = verifyLocator(
    { ...locator, lineage_ref: "BOGUS-UNPROVEN-LINEAGE" },
    { repositoryPath, verificationContext },
  );
  assert.equal(result.state, "RETRIEVAL_FAILED");
  assert.equal(result.reason, "LINEAGE_NOT_VERIFIED");
  assert.equal(result.lineage_state, "NOT_PROVEN");
});

test("exact non-predecessor with the same work item cannot verify lineage", () => {
  const context = structuredClone(verificationContext);
  context.lineage_records[0].referenced_artifact = nonPredecessorIdentity;
  context.lineage_records[0].authorized_relation = true;
  const result = verifyLocator(locator, { repositoryPath, verificationContext: context });
  assert.equal(result.state, "RETRIEVAL_FAILED");
  assert.equal(result.reason, "LINEAGE_NOT_VERIFIED");
  assert.equal(result.lineage_state, "CONFLICT");
  assert.notEqual(result.state, "VERIFIED_EXACT");
});

test("caller relationship metadata cannot replace the code-bound successor relation", () => {
  const context = structuredClone(verificationContext);
  context.lineage_records[0].relationship_type = "VALIDATED_CAPABILITY_PROOF_SOURCE";
  context.lineage_records[0].authorized_relation = true;
  const result = verifyLocator(locator, { repositoryPath, verificationContext: context });
  assert.equal(result.state, "RETRIEVAL_FAILED");
  assert.equal(result.reason, "LINEAGE_NOT_VERIFIED");
  assert.equal(result.lineage_state, "CONFLICT");
  assert.notEqual(result.state, "VERIFIED_EXACT");
});

test("missing artifact-specific semantic profile is rejected", () => {
  const context = structuredClone(verificationContext);
  context.semantic_profiles = [];
  const result = verifyLocator(locator, { repositoryPath, verificationContext: context });
  assert.equal(result.state, "RETRIEVAL_FAILED");
  assert.equal(result.reason, "SEMANTIC_PROFILE_NOT_PROVEN");
  assert.equal(result.semantic_content_digest_state, "NOT_PROVEN");
});

test("generic raw digest equality cannot create VERIFIED_EXACT", () => {
  const genericDigestLocator = { ...locator, semantic_content_digest_if_applicable: locator.sha256 };
  const result = verifyLocator(genericDigestLocator, { repositoryPath, verificationContext });
  assert.equal(result.state, "RETRIEVAL_FAILED");
  assert.equal(result.reason, "SEMANTIC_DIGEST_MISMATCH");
  assert.notEqual(result.state, "VERIFIED_EXACT");
});

test("verification context cannot redefine an artifact-specific profile selection", () => {
  const context = structuredClone(verificationContext);
  context.semantic_profiles[0].selection.field = "work_item_id";
  const wrongSelectionDigest = sha256(Buffer.from(JSON.stringify(TEST_LINEAGE_REF)));
  const result = verifyLocator(
    { ...locator, semantic_content_digest_if_applicable: wrongSelectionDigest },
    { repositoryPath, verificationContext: context },
  );
  assert.equal(result.state, "RETRIEVAL_FAILED");
  assert.equal(result.reason, "SEMANTIC_PROFILE_NOT_PROVEN");
  assert.notEqual(result.state, "VERIFIED_EXACT");
});

test("hash and metadata equality without explicit provenance cannot verify provenance", () => {
  const context = structuredClone(verificationContext);
  context.provenance_records = [];
  const result = verifyLocator(locator, { repositoryPath, verificationContext: context });
  assert.equal(result.state, "RETRIEVAL_FAILED");
  assert.equal(result.reason, "PROVENANCE_NOT_PROVEN");
  assert.equal(result.provenance_state, "NOT_PROVEN");
});

test("unbound caller provenance assertion cannot elevate proof state", () => {
  const context = structuredClone(verificationContext);
  context.provenance_records = [
    {
      subject: subjectIdentity(locator),
      lineage_ref: locator.lineage_ref,
      relationship_type: TEST_RELATIONSHIP,
      provenance_assertion: "EXPLICIT_PROVENANCE_EVIDENCE",
      authorized: true,
      authorization_ref: TEST_AUTHORIZATION_REF,
      authorization_claim_profile: "AAA_OWNER_DECISION_ACCEPTED_EXACT_TARGET_v0.1",
      sha256: locator.sha256,
      byte_size: locator.byte_size,
    },
  ];
  const result = verifyLocator(locator, { repositoryPath, verificationContext: context });
  assert.equal(result.state, "RETRIEVAL_FAILED");
  assert.equal(result.reason, "PROVENANCE_NOT_PROVEN");
  assert.equal(result.provenance_state, "PARTIAL");
  assert.notEqual(result.state, "VERIFIED_EXACT");
});

test("invalid locator identity is rejected", () => {
  const result = verifyLocator(
    { ...locator, git_blob: "invalid" },
    { repositoryPath, verificationContext },
  );
  assert.equal(result.state, "RETRIEVAL_FAILED");
  assert.equal(result.reason, "INVALID_LOCATOR_RECORD");
});

test("existing exact S0 locator remains VERIFIED_EXACT with explicit governed proof", () => {
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
    discovery_branch: "DISCOVERY_ONLY_NOT_USED",
  };
  const subject = subjectIdentity(s0);
  const ownerDecision = {
    artifact_id: "AAA-OWNER-TW-VALIDATED-S0-TO-ACTIVE-MINIMUM-ADOPTION-DECISION-v0.1",
    repository: s0.repository,
    exact_commit: "bb974162a1c41331424819d7736b5c3f2d4f436f",
    exact_path: "control/decisions/transfer-workspace/persistent-locator-adoption/v0.1/AAA_OWNER_TW_VALIDATED_S0_TO_ACTIVE_MINIMUM_ADOPTION_DECISION_v0.1.json",
    git_blob: "89556dc2524226bdf0d0ba516f4dddbde00e1c30",
    sha256: "79350f128f8bb4016011b32edfd35f2cde7c6aef093fccf4dc60fd8d658a309c",
    byte_size: 4482,
  };
  const exactPredecessor = {
    artifact_id: "AAA-TW-S0-PLCP-SHADOW-INSTANCE-v0.4",
    version: "v0.4",
    repository: s0.repository,
    exact_commit: "ba91403930c97db4e66e937d1ce7da04c342d4c1",
    exact_path: "control/architecture/working-candidates/transfer-workspace/s0/plcp-shadow/v0.4/control/AAA_TW_S0_PLCP_SHADOW_INSTANCE_v0.4.json",
    git_blob: "528fbc9746c6e50f32b081013031a31281220d58",
    sha256: "00934140c17fc21992f5e51eb174b07c18c17f4d5f6a7e15a553eae5796b95c4",
    byte_size: 13677,
  };
  const context = {
    repository_bindings: [
      {
        repository: s0.repository,
        authorized: true,
        authorization_ref: ownerDecision.artifact_id,
        authorization_claim_profile: "AAA_OWNER_DECISION_ACCEPTED_EXACT_TARGET_v0.1",
        authorization_evidence: ownerDecision,
        remote_name: "origin",
        repository_host: "github.com",
        allowed_remote_urls: ["https://github.com/AofSpds/asset-agent-asa.git"],
        require_commit_reachable_from_remote_tracking_ref: true,
      },
    ],
    semantic_profiles: [
      {
        applies_to: subject,
        authorized: true,
        authorization_ref: ownerDecision.artifact_id,
        authorization_claim_profile: "AAA_OWNER_DECISION_ACCEPTED_EXACT_TARGET_v0.1",
        authorization_evidence: ownerDecision,
        profile_id: "SHA256_UTF8_CANONICAL_JSON_NORMATIVE_OVERLAY_SORT_KEYS_COMPACT_NO_TRAILING_NEWLINE",
        digest_algorithm: "SHA256",
        canonicalization: "JSON_SORT_KEYS_COMPACT_UTF8_NO_TRAILING_NEWLINE",
        selection: { type: "TOP_LEVEL_VALUE", field: "normative_overlay" },
      },
    ],
    lineage_records: [
      {
        lineage_ref: s0.lineage_ref,
        subject,
        proof_profile: TEST_LINEAGE_PROFILE,
        referenced_artifact: exactPredecessor,
        relationship_type: TEST_RELATIONSHIP,
        authorization_ref: ownerDecision.artifact_id,
        authorization_claim_profile: "AAA_OWNER_DECISION_ACCEPTED_EXACT_TARGET_v0.1",
        authorization_evidence: ownerDecision,
      },
    ],
    provenance_records: [
      {
        subject,
        lineage_ref: s0.lineage_ref,
        relationship_type: TEST_RELATIONSHIP,
        evidence_profile: TEST_PROVENANCE_PROFILE,
        authorization_ref: ownerDecision.artifact_id,
        authorization_claim_profile: "AAA_OWNER_DECISION_ACCEPTED_EXACT_TARGET_v0.1",
        evidence: ownerDecision,
      },
    ],
  };
  const result = verifyLocator(s0, { repositoryPath: projectRoot, verificationContext: context });
  assert.equal(result.state, "VERIFIED_EXACT");
  assert.equal(result.repository_identity_state, "REPOSITORY_VERIFIED");
  assert.equal(result.semantic_content_digest_state, "SEMANTIC_DIGEST_VERIFIED");
  assert.equal(result.semantic_canonical_input_byte_size, 4992);
  assert.equal(result.lineage_state, "LINEAGE_VERIFIED");
  assert.equal(result.lineage_referenced_artifact_id, exactPredecessor.artifact_id);
  assert.equal(result.lineage_referenced_artifact_version, exactPredecessor.version);
  assert.equal(result.provenance_state, "PROVENANCE_VERIFIED");
});
