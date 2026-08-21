#!/usr/bin/env node

import { createHash } from "node:crypto";
import { accessSync, constants as fsConstants, existsSync, mkdtempSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve, sep } from "node:path";
import { spawnSync } from "node:child_process";
import { pathToFileURL } from "node:url";

export const FAILURE_STATES = Object.freeze([
  "NOT_FOUND",
  "ACCESS_BLOCKED",
  "RETRIEVAL_FAILED",
  "UNKNOWN",
]);

export const PROOF_STATES = Object.freeze([
  "NOT_PROVEN",
  "PARTIAL",
  "CONFLICT",
  "UNKNOWN",
]);

export const REQUIRED_LOCATOR_FIELDS = Object.freeze([
  "repository",
  "exact_commit",
  "exact_path",
  "git_blob",
  "sha256",
  "byte_size",
  "semantic_content_digest_if_applicable",
  "lineage_ref",
]);

const REQUIRED_IDENTITY_FIELDS = Object.freeze([
  "repository",
  "exact_commit",
  "exact_path",
  "git_blob",
  "sha256",
  "byte_size",
]);

const NOT_FOUND_PATTERNS = [
  /not a valid object name/i,
  /not a valid object/i,
  /unknown revision/i,
  /bad object/i,
  /does not exist in/i,
  /path .* exists on disk, but not in/i,
  /invalid object name/i,
  /needed a single revision/i,
];

const ACCESS_BLOCKED_PATTERNS = [
  /permission denied/i,
  /access is denied/i,
  /authentication failed/i,
  /authorization failed/i,
  /could not read username/i,
  /repository access blocked/i,
  /operation not permitted/i,
];

const EXIT_CODES = Object.freeze({
  VERIFIED_EXACT: 0,
  NOT_FOUND: 3,
  ACCESS_BLOCKED: 4,
  RETRIEVAL_FAILED: 5,
  UNKNOWN: 6,
});

const CANONICAL_JSON_PROFILE = "JSON_SORT_KEYS_COMPACT_UTF8_NO_TRAILING_NEWLINE";
const EXACT_PREDECESSOR_RELATIONSHIP = "EXACT_SUCCESSOR_OF_DECLARED_PREDECESSOR";
const SUBJECT_DECLARED_PREDECESSOR_PROFILE = "AAA_SUBJECT_DECLARED_EXACT_PREDECESSOR_v0.1";
const ACCEPTED_TARGET_PROVENANCE_PROFILE = "AAA_OWNER_DECISION_ACCEPTED_EXACT_TARGET_PROVENANCE_v0.1";
const ARTIFACT_SPECIFIC_SEMANTIC_PROFILES = Object.freeze({
  SHA256_UTF8_CANONICAL_JSON_NORMATIVE_OVERLAY_SORT_KEYS_COMPACT_NO_TRAILING_NEWLINE: Object.freeze({
    digest_algorithm: "SHA256",
    canonicalization: CANONICAL_JSON_PROFILE,
    selection_type: "TOP_LEVEL_VALUE",
    selection_field: "normative_overlay",
  }),
});

const GOVERNED_WORK_ITEM = "AAA_TW_PERSISTENT_LOCATOR_ACTIVE_ADOPTION_v0.1";
const GOVERNED_LINEAGE_REF = "AAA-PERSISTENT-LOCATOR-CAPABILITY-PROOF-v0.1";
const GOVERNED_CANONICAL_REMOTE = "https://github.com/AofSpds/asset-agent-asa.git";
const GOVERNED_APPROVED_SCOPE = Object.freeze({
  adoption_scope: "EXACT_VALIDATED_PERSISTENT_LOCATOR_MECHANICS_ONLY",
  apply_validated_s0_capability: true,
  authoring_of_minimum_active_adoption_candidate: "AUTHORIZED",
  dedicated_candidate_branch_non_force_remote_push: "AUTHORIZED",
  extra_features_now: false,
  force_push_authorized: false,
  main_merge_authorized: false,
  model_semantic_change_authorized: false,
  non_semantic_registration_within_existing_allowlist: "AUTHORIZED",
  owner_acceptance_state: "ACCEPTED_FOR_THIS_BOUNDED_S0_MILESTONE",
  owner_reapproval_for_ordinary_in_scope_mechanical_work_required: false,
  pit_gt_change_authorized: false,
  proceed_to_application: true,
  production_authorized: false,
  release_authorized: false,
  s0_result_accepted: true,
  tag_authorized: false,
  track_a_mutation_authorized: false,
  unplanned_shared_contract_expansion_authorized: false,
});

const GOVERNED_BINDING = Object.freeze({
  object_id: "AAA-PERSISTENT-LOCATOR-SUBJECT-SCOPED-AUTHORITY-BINDING",
  version: "v0.3",
  work_item_id: GOVERNED_WORK_ITEM,
  lineage_ref: GOVERNED_LINEAGE_REF,
  relationship: EXACT_PREDECESSOR_RELATIONSHIP,
  canonical_remote: GOVERNED_CANONICAL_REMOTE,
  canonical_host: "github.com",
  subject: Object.freeze({
    artifact_id: "AAA-TW-S0-PLCP-SHADOW-INSTANCE-v0.5",
    version: "v0.5",
    repository: "AofSpds/asset-agent-asa",
    exact_commit: "d0b0d2c7a77ca00570151e89e70e092b10646bd2",
    exact_tree: "ca1e410f745c54d6d66579173739e28bbf54590e",
    exact_path: "control/architecture/working-candidates/transfer-workspace/s0/plcp-shadow/v0.5/control/AAA_TW_S0_PLCP_SHADOW_INSTANCE_v0.5.json",
    git_blob: "7bc6e4c2194bc2f06d61367434cab38947b40e0d",
    sha256: "abd1d42be8b2a9b25eba266cfd939905e1799c93dc975fedcb560478cbcefdd8",
    byte_size: 13947,
    semantic_content_digest_if_applicable: "370a934edfaf72dc2e06d5e45b7c38be8026e3cf85e8d11c2903d2e342be48f2",
    lineage_ref: GOVERNED_LINEAGE_REF,
  }),
  predecessor: Object.freeze({
    artifact_id: "AAA-TW-S0-PLCP-SHADOW-INSTANCE-v0.4",
    version: "v0.4",
    repository: "AofSpds/asset-agent-asa",
    exact_commit: "ba91403930c97db4e66e937d1ce7da04c342d4c1",
    exact_tree: "f1947d80bdb18170cf0ce47130af3c2493d52a1d",
    exact_path: "control/architecture/working-candidates/transfer-workspace/s0/plcp-shadow/v0.4/control/AAA_TW_S0_PLCP_SHADOW_INSTANCE_v0.4.json",
    git_blob: "528fbc9746c6e50f32b081013031a31281220d58",
    sha256: "00934140c17fc21992f5e51eb174b07c18c17f4d5f6a7e15a553eae5796b95c4",
    byte_size: 13677,
  }),
  owner_authority: Object.freeze({
    artifact_id: "AAA-OWNER-TW-VALIDATED-S0-TO-ACTIVE-MINIMUM-ADOPTION-DECISION-v0.1",
    repository: "AofSpds/asset-agent-asa",
    exact_commit: "bb974162a1c41331424819d7736b5c3f2d4f436f",
    exact_tree: "f5680fdafbcd464c78e0d3cb58ac2c47fe66157b",
    exact_path: "control/decisions/transfer-workspace/persistent-locator-adoption/v0.1/AAA_OWNER_TW_VALIDATED_S0_TO_ACTIVE_MINIMUM_ADOPTION_DECISION_v0.1.json",
    git_blob: "89556dc2524226bdf0d0ba516f4dddbde00e1c30",
    sha256: "79350f128f8bb4016011b32edfd35f2cde7c6aef093fccf4dc60fd8d658a309c",
    byte_size: 4482,
    semantic_digest: "5a48a1aaf52ff2e826c3b920dce9a534839c040115f9d6fd26cc6fa881e9dc4b",
  }),
  authority_principal: "HUMAN PROJECT OWNER",
  approved_scope: GOVERNED_APPROVED_SCOPE,
  approved_scope_digest: "5a48a1aaf52ff2e826c3b920dce9a534839c040115f9d6fd26cc6fa881e9dc4b",
  semantic_profile: Object.freeze({
    profile_id: "SHA256_UTF8_CANONICAL_JSON_NORMATIVE_OVERLAY_SORT_KEYS_COMPACT_NO_TRAILING_NEWLINE",
    digest_algorithm: "SHA256",
    canonicalization: CANONICAL_JSON_PROFILE,
    selection_type: "TOP_LEVEL_VALUE",
    selection_field: "normative_overlay",
  }),
});

function bufferToText(value) {
  if (!value) return "";
  return Buffer.isBuffer(value) ? value.toString("utf8") : String(value);
}

export function classifyGitFailure(stderr, error) {
  const errorCode = error?.code ?? "";
  const message = `${bufferToText(stderr)}\n${error?.message ?? ""}`.trim();
  if (errorCode === "EACCES" || errorCode === "EPERM") {
    return { state: "ACCESS_BLOCKED", reason: "LOCAL_REPOSITORY_ACCESS_DENIED", message };
  }
  if (ACCESS_BLOCKED_PATTERNS.some((pattern) => pattern.test(message))) {
    return { state: "ACCESS_BLOCKED", reason: "GIT_ACCESS_DENIED", message };
  }
  if (NOT_FOUND_PATTERNS.some((pattern) => pattern.test(message))) {
    return { state: "NOT_FOUND", reason: "EXACT_GIT_OBJECT_OR_PATH_NOT_FOUND", message };
  }
  if (errorCode === "ENOENT") {
    return { state: "RETRIEVAL_FAILED", reason: "GIT_OR_REPOSITORY_UNAVAILABLE", message };
  }
  return { state: "RETRIEVAL_FAILED", reason: "GIT_COMMAND_FAILED", message };
}

function runGit(repositoryPath, args) {
  const result = spawnSync("git", ["-C", repositoryPath, ...args], {
    encoding: null,
    windowsHide: true,
  });
  if (result.error || result.status !== 0) {
    return { ok: false, ...classifyGitFailure(result.stderr, result.error) };
  }
  return { ok: true, stdout: result.stdout ?? Buffer.alloc(0) };
}

function invalidLocator(message, field) {
  return {
    state: "RETRIEVAL_FAILED",
    verified: false,
    reason: "INVALID_LOCATOR_RECORD",
    field,
    message,
  };
}

function validateIdentityFields(identity, fields = REQUIRED_IDENTITY_FIELDS) {
  if (!identity || typeof identity !== "object" || Array.isArray(identity)) {
    return { ok: false, field: null, message: "Identity must be a JSON object." };
  }
  for (const field of fields) {
    if (!(field in identity)) {
      return { ok: false, field, message: `Missing required field: ${field}` };
    }
  }
  for (const field of ["repository", "exact_commit", "exact_path", "git_blob", "sha256"]) {
    if (typeof identity[field] !== "string" || identity[field].length === 0) {
      return { ok: false, field, message: `${field} must be a non-empty string.` };
    }
  }
  if (!/^[0-9a-f]{40}$/i.test(identity.exact_commit)) {
    return { ok: false, field: "exact_commit", message: "exact_commit must be a full 40-hex Git commit." };
  }
  if (!/^[0-9a-f]{40}$/i.test(identity.git_blob)) {
    return { ok: false, field: "git_blob", message: "git_blob must be a full 40-hex Git blob." };
  }
  if (!/^[0-9a-f]{64}$/i.test(identity.sha256)) {
    return { ok: false, field: "sha256", message: "sha256 must be a full 64-hex digest." };
  }
  if (!Number.isSafeInteger(identity.byte_size) || identity.byte_size < 0) {
    return { ok: false, field: "byte_size", message: "byte_size must be a non-negative safe integer." };
  }
  return { ok: true };
}

export function validateLocatorRecord(locator) {
  const identityValidation = validateIdentityFields(locator, REQUIRED_LOCATOR_FIELDS);
  if (!identityValidation.ok) {
    return invalidLocator(identityValidation.message, identityValidation.field);
  }
  if (typeof locator.lineage_ref !== "string" || locator.lineage_ref.length === 0) {
    return invalidLocator("lineage_ref must be a non-empty string.", "lineage_ref");
  }
  const semanticDigest = locator.semantic_content_digest_if_applicable;
  if (semanticDigest !== null && !/^[0-9a-f]{64}$/i.test(semanticDigest ?? "")) {
    return invalidLocator(
      "semantic_content_digest_if_applicable must be null or a full 64-hex digest.",
      "semantic_content_digest_if_applicable",
    );
  }
  return null;
}

function failure(locator, failureResult, extra = {}) {
  return {
    state: failureResult.state,
    verified: false,
    reason: failureResult.reason,
    repository: locator.repository,
    exact_commit: locator.exact_commit,
    exact_path: locator.exact_path,
    message: failureResult.message || undefined,
    ...extra,
  };
}

function proofFailure(locator, reason, proofFields, message) {
  return failure(locator, { state: "RETRIEVAL_FAILED", reason, message }, proofFields);
}

function stableValue(value) {
  if (Array.isArray(value)) return value.map(stableValue);
  if (value && typeof value === "object") {
    return Object.fromEntries(Object.keys(value).sort().map((key) => [key, stableValue(value[key])]));
  }
  return value;
}

function normalizeRemoteRepository(remoteUrl) {
  const trimmed = remoteUrl.trim().replace(/[\\/]$/, "").replace(/\.git$/i, "");
  const scpLike = trimmed.match(/^[^@]+@([^:]+):(.+)$/);
  let pathname;
  let host;
  if (scpLike) {
    host = scpLike[1].toLowerCase();
    pathname = scpLike[2];
  } else {
    try {
      const parsed = new URL(trimmed);
      host = parsed.hostname.toLowerCase();
      pathname = parsed.pathname;
    } catch {
      return null;
    }
  }
  const segments = pathname.replace(/^\/+/, "").split("/").filter(Boolean);
  if (segments.length !== 2) return null;
  return { host, repository: `${segments[0]}/${segments[1]}` };
}

function identityMatches(left, right) {
  return REQUIRED_IDENTITY_FIELDS.every((field) => {
    if (field === "byte_size") return left?.[field] === right?.[field];
    if (["exact_commit", "git_blob", "sha256"].includes(field)) {
      return String(left?.[field] ?? "").toLowerCase() === String(right?.[field] ?? "").toLowerCase();
    }
    return String(left?.[field] ?? "") === String(right?.[field] ?? "");
  });
}

function declaredPredecessorIdentity(subjectArtifact, repository) {
  const predecessor = subjectArtifact?.lineage?.predecessor_exact;
  if (!predecessor || typeof predecessor !== "object" || Array.isArray(predecessor)) return null;
  return {
    artifact_id: predecessor.artifact_id,
    version: predecessor.version,
    repository,
    exact_commit: predecessor.commit,
    exact_path: predecessor.path,
    git_blob: predecessor.git_blob,
    sha256: predecessor.artifact_sha256 ?? predecessor.sha256,
    byte_size: predecessor.byte_size,
  };
}

function verifyExactIdentityRecord(identity, repositoryPath) {
  const validation = validateIdentityFields(identity);
  if (!validation.ok) {
    return { ok: false, state: "RETRIEVAL_FAILED", reason: "PARTIAL_IDENTITY_RECORD", ...validation };
  }
  const commitCheck = runGit(repositoryPath, ["cat-file", "-e", `${identity.exact_commit}^{commit}`]);
  if (!commitCheck.ok) return commitCheck;
  const pathResolution = runGit(repositoryPath, [
    "rev-parse",
    "--verify",
    `${identity.exact_commit}:${identity.exact_path}`,
  ]);
  if (!pathResolution.ok) return pathResolution;
  const observedBlob = pathResolution.stdout.toString("ascii").trim().toLowerCase();
  if (observedBlob !== identity.git_blob.toLowerCase()) {
    return { ok: false, state: "RETRIEVAL_FAILED", reason: "IDENTITY_MISMATCH", mismatch_fields: ["git_blob"] };
  }
  const blobRead = runGit(repositoryPath, ["cat-file", "blob", observedBlob]);
  if (!blobRead.ok) return blobRead;
  const observedSha256 = createHash("sha256").update(blobRead.stdout).digest("hex");
  const observedByteSize = blobRead.stdout.length;
  const mismatchFields = [];
  if (observedSha256 !== identity.sha256.toLowerCase()) mismatchFields.push("sha256");
  if (observedByteSize !== identity.byte_size) mismatchFields.push("byte_size");
  if (mismatchFields.length > 0) {
    return { ok: false, state: "RETRIEVAL_FAILED", reason: "IDENTITY_MISMATCH", mismatch_fields: mismatchFields };
  }
  return { ok: true, blob: blobRead.stdout, observed_blob: observedBlob };
}

function requireExactlyOne(records, missingState = "NOT_PROVEN") {
  if (records.length === 0) return { ok: false, proof_state: missingState };
  if (records.length > 1) return { ok: false, proof_state: "CONFLICT" };
  return { ok: true, record: records[0] };
}

function identityAndTreeMatch(left, right) {
  return identityMatches(left, right)
    && (!left?.exact_tree || !right?.exact_tree
      || String(left.exact_tree).toLowerCase() === String(right.exact_tree).toLowerCase());
}

function jsonEquals(left, right) {
  return JSON.stringify(stableValue(left)) === JSON.stringify(stableValue(right));
}

function subjectMatchesBinding(locator, binding) {
  return identityMatches(locator, binding?.subject)
    && locator.semantic_content_digest_if_applicable === binding.subject.semantic_content_digest_if_applicable
    && locator.lineage_ref === binding.lineage_ref;
}

function selectGovernedBinding(locator, bindings = [GOVERNED_BINDING]) {
  const selected = bindings.filter((binding) => subjectMatchesBinding(locator, binding));
  if (selected.length === 0) {
    return { ok: false, proof_state: "NOT_PROVEN", reason: "GOVERNED_SUBJECT_NOT_SELECTED" };
  }
  if (selected.length !== 1) {
    return { ok: false, proof_state: "CONFLICT", reason: "GOVERNED_SUBJECT_BINDING_CONFLICT" };
  }
  const binding = selected[0];
  if (!binding.owner_authority || !binding.predecessor || !binding.approved_scope) {
    return { ok: false, proof_state: "NOT_PROVEN", reason: "GOVERNED_AUTHORITY_EVIDENCE_MISSING" };
  }
  return { ok: true, binding };
}

function assertionConflict(detail) {
  return {
    ok: false,
    proof_state: "CONFLICT",
    reason: "CALLER_AUTHORITY_ASSERTION_CONFLICT",
    message: detail,
  };
}

function verifyCallerCompatibility(locator, context, binding) {
  if (context === undefined || context === null) return { ok: true, asserted: false };
  if (typeof context !== "object" || Array.isArray(context)) {
    return assertionConflict("verificationContext must be an object when supplied.");
  }

  for (const [field, expected] of [
    ["work_item_id", binding.work_item_id],
    ["relationship_type", binding.relationship],
    ["authority_principal", binding.authority_principal],
    ["canonical_remote", binding.canonical_remote],
  ]) {
    if (field in context && context[field] !== expected) {
      return assertionConflict(`Caller ${field} conflicts with the governed binding.`);
    }
  }
  for (const field of ["authorized_scope", "approved_semantic_scope"]) {
    if (field in context && !jsonEquals(context[field], binding.approved_scope)) {
      return assertionConflict(`Caller ${field} conflicts with governed authorized scope.`);
    }
  }
  if ("owner_authority_evidence" in context
      && (!identityAndTreeMatch(context.owner_authority_evidence, binding.owner_authority)
        || context.owner_authority_evidence?.artifact_id !== binding.owner_authority.artifact_id)) {
    return assertionConflict("Caller selected alternate Owner authority evidence.");
  }

  const arrays = ["repository_bindings", "semantic_profiles", "lineage_records", "provenance_records"];
  for (const field of arrays) {
    if (field in context && !Array.isArray(context[field])) {
      return assertionConflict(`Caller ${field} must be an array when supplied.`);
    }
  }

  const repositoryAssertions = (context.repository_bindings ?? []).filter(
    (record) => record?.repository === locator.repository,
  );
  if (repositoryAssertions.length > 1) return assertionConflict("Caller supplied multiple authority bindings for the governed subject.");
  if (repositoryAssertions.length === 1) {
    const record = repositoryAssertions[0];
    if (
      record.authorized !== true
      || record.authorization_ref !== binding.owner_authority.artifact_id
      || record.authorization_claim_profile !== "AAA_OWNER_DECISION_ACCEPTED_EXACT_TARGET_v0.1"
      || !identityAndTreeMatch(record.authorization_evidence, binding.owner_authority)
      || record.authorization_evidence?.artifact_id !== binding.owner_authority.artifact_id
      || ("repository_host" in record && record.repository_host !== binding.canonical_host)
      || ("allowed_remote_urls" in record
        && (!Array.isArray(record.allowed_remote_urls)
          || record.allowed_remote_urls.length !== 1
          || record.allowed_remote_urls[0] !== binding.canonical_remote))
    ) {
      return assertionConflict("Caller repository binding conflicts with governed authority or canonical remote.");
    }
  }

  const semanticAssertions = (context.semantic_profiles ?? []).filter(
    (record) => identityMatches(record?.applies_to, locator),
  );
  if (semanticAssertions.length > 1) return assertionConflict("Caller supplied multiple semantic authority assertions.");
  if (semanticAssertions.length === 1) {
    const record = semanticAssertions[0];
    if (
      record.profile_id !== binding.semantic_profile.profile_id
      || record.digest_algorithm !== binding.semantic_profile.digest_algorithm
      || record.canonicalization !== binding.semantic_profile.canonicalization
      || record.selection?.type !== binding.semantic_profile.selection_type
      || record.selection?.field !== binding.semantic_profile.selection_field
      || record.authorization_ref !== binding.owner_authority.artifact_id
      || !identityAndTreeMatch(record.authorization_evidence, binding.owner_authority)
    ) {
      return assertionConflict("Caller semantic or authority assertion conflicts with the governed binding.");
    }
  }

  const lineageAssertions = (context.lineage_records ?? []).filter(
    (record) => record?.lineage_ref === locator.lineage_ref,
  );
  if (lineageAssertions.length > 1) return assertionConflict("Caller supplied multiple relationship assertions.");
  if (lineageAssertions.length === 1) {
    const record = lineageAssertions[0];
    if (
      !identityMatches(record.subject, binding.subject)
      || record.proof_profile !== SUBJECT_DECLARED_PREDECESSOR_PROFILE
      || record.relationship_type !== binding.relationship
      || !identityAndTreeMatch(record.referenced_artifact, binding.predecessor)
      || record.referenced_artifact?.artifact_id !== binding.predecessor.artifact_id
      || record.authorization_ref !== binding.owner_authority.artifact_id
      || !identityAndTreeMatch(record.authorization_evidence, binding.owner_authority)
    ) {
      return assertionConflict("Caller relationship assertion conflicts with the governed binding.");
    }
  }

  const provenanceAssertions = (context.provenance_records ?? []).filter(
    (record) => record?.lineage_ref === locator.lineage_ref || identityMatches(record?.subject, locator),
  );
  if (provenanceAssertions.length > 1) return assertionConflict("Caller supplied multiple provenance assertions.");
  if (provenanceAssertions.length === 1) {
    const record = provenanceAssertions[0];
    if (
      !identityMatches(record.subject, binding.subject)
      || record.relationship_type !== binding.relationship
      || record.evidence_profile !== ACCEPTED_TARGET_PROVENANCE_PROFILE
      || record.authorization_ref !== binding.owner_authority.artifact_id
      || !identityAndTreeMatch(record.evidence, binding.owner_authority)
      || record.evidence?.artifact_id !== binding.owner_authority.artifact_id
    ) {
      return assertionConflict("Caller provenance assertion conflicts with the governed binding.");
    }
  }
  return { ok: true, asserted: Object.keys(context).length > 0 };
}

function verifyGovernedOwnerAuthority(binding, repositoryPath) {
  const evidence = verifyExactIdentityRecord(binding.owner_authority, repositoryPath);
  if (!evidence.ok) {
    return {
      ok: false,
      proof_state: evidence.reason === "IDENTITY_MISMATCH" ? "CONFLICT" : "NOT_PROVEN",
      reason: "GOVERNED_OWNER_AUTHORITY_NOT_PROVEN",
    };
  }
  let artifact;
  try {
    artifact = JSON.parse(evidence.blob.toString("utf8"));
  } catch {
    return { ok: false, proof_state: "CONFLICT", reason: "GOVERNED_OWNER_AUTHORITY_INVALID" };
  }
  const accepted = artifact.accepted_exact_s0_target;
  const acceptedIdentity = accepted && {
    repository: accepted.repository,
    exact_commit: accepted.commit,
    exact_tree: accepted.tree,
    exact_path: accepted.path,
    git_blob: accepted.git_blob,
    sha256: accepted.sha256,
    byte_size: accepted.byte_size,
  };
  const canonicalScope = Buffer.from(JSON.stringify(stableValue(artifact.approved_semantic_scope)), "utf8");
  const scopeDigest = createHash("sha256").update(canonicalScope).digest("hex");
  if (
    artifact.artifact_id !== binding.owner_authority.artifact_id
    || artifact.artifact_kind !== "OWNER_DECISION_RECEIPT_AUTHORITY_ARTIFACT"
    || artifact.authority_principal !== binding.authority_principal
    || artifact.receipt_role !== "AUTHORITY_EVIDENCE_NOT_SECOND_SEMANTIC_SOT"
    || !jsonEquals(artifact.approved_semantic_scope, binding.approved_scope)
    || scopeDigest !== binding.approved_scope_digest
    || artifact.semantic_content_digest !== binding.approved_scope_digest
    || artifact.semantic_canonical_input_byte_size !== canonicalScope.length
    || !identityAndTreeMatch(acceptedIdentity, binding.subject)
    || accepted.artifact_id !== binding.subject.artifact_id
    || accepted.semantic_content_digest !== binding.subject.semantic_content_digest_if_applicable
  ) {
    return { ok: false, proof_state: "CONFLICT", reason: "GOVERNED_OWNER_AUTHORITY_CONFLICT" };
  }
  return {
    ok: true,
    state: "OWNER_AUTHORIZED",
    authority_artifact_id: binding.owner_authority.artifact_id,
    authority_principal: binding.authority_principal,
    approved_scope_digest: scopeDigest,
  };
}

function verifyGovernedSemanticDigest(locator, binding, subjectBlob) {
  let artifact;
  try {
    artifact = JSON.parse(subjectBlob.toString("utf8"));
  } catch {
    return { ok: false, proof_state: "CONFLICT", reason: "SEMANTIC_PROFILE_INPUT_INVALID" };
  }
  const profile = binding.semantic_profile;
  if (artifact.semantic_digest_profile !== profile.profile_id || !(profile.selection_field in artifact)) {
    return { ok: false, proof_state: "CONFLICT", reason: "SEMANTIC_PROFILE_ARTIFACT_BINDING_CONFLICT" };
  }
  const canonicalInput = Buffer.from(JSON.stringify(stableValue(artifact[profile.selection_field])), "utf8");
  const observedDigest = createHash("sha256").update(canonicalInput).digest("hex");
  if (observedDigest !== locator.semantic_content_digest_if_applicable.toLowerCase()) {
    return { ok: false, proof_state: "CONFLICT", reason: "SEMANTIC_DIGEST_MISMATCH", observed_digest: observedDigest };
  }
  return {
    ok: true,
    state: "SEMANTIC_DIGEST_VERIFIED",
    profile_id: profile.profile_id,
    canonical_input_byte_size: canonicalInput.length,
    semantic_content_digest: observedDigest,
  };
}

function verifyGovernedLineage(locator, binding, repositoryPath, subjectBlob) {
  let artifact;
  try {
    artifact = JSON.parse(subjectBlob.toString("utf8"));
  } catch {
    return { ok: false, proof_state: "CONFLICT", reason: "LINEAGE_SUBJECT_ARTIFACT_INVALID" };
  }
  const declared = declaredPredecessorIdentity(artifact, locator.repository);
  if (
    artifact.artifact_id !== binding.subject.artifact_id
    || artifact.version !== binding.subject.version
    || artifact.work_item_id !== binding.lineage_ref
    || artifact.lineage?.successor_of_version !== binding.predecessor.version
    || !declared
    || declared.artifact_id !== binding.predecessor.artifact_id
    || declared.version !== binding.predecessor.version
    || !identityAndTreeMatch(declared, binding.predecessor)
  ) {
    return { ok: false, proof_state: "CONFLICT", reason: "LINEAGE_NOT_VERIFIED" };
  }
  const predecessor = verifyExactIdentityRecord(binding.predecessor, repositoryPath);
  if (!predecessor.ok) {
    return { ok: false, proof_state: "NOT_PROVEN", reason: "LINEAGE_REFERENCED_ARTIFACT_NOT_PROVEN" };
  }
  let predecessorArtifact;
  try {
    predecessorArtifact = JSON.parse(predecessor.blob.toString("utf8"));
  } catch {
    return { ok: false, proof_state: "CONFLICT", reason: "LINEAGE_REFERENCED_ARTIFACT_INVALID" };
  }
  if (
    predecessorArtifact.artifact_id !== binding.predecessor.artifact_id
    || predecessorArtifact.version !== binding.predecessor.version
    || predecessorArtifact.work_item_id !== binding.lineage_ref
  ) {
    return { ok: false, proof_state: "CONFLICT", reason: "LINEAGE_NOT_VERIFIED" };
  }
  return {
    ok: true,
    state: "LINEAGE_VERIFIED",
    relationship: binding.relationship,
    referenced_artifact_id: binding.predecessor.artifact_id,
    referenced_artifact_version: binding.predecessor.version,
  };
}

function liveRemoteFailure(state, reason, message, extra = {}) {
  return {
    ok: false,
    state,
    reason,
    message: message || undefined,
    fresh_network_operation_attempted: true,
    isolated_temporary_proof_storage: true,
    governed_repository_mutated_for_proof: false,
    ...extra,
  };
}

function selectProofParent(governedRepositoryPath) {
  const governedRoot = governedRepositoryPath ? resolve(governedRepositoryPath) : null;
  const candidates = [process.env.TMPDIR, tmpdir(), governedRoot ? dirname(governedRoot) : null]
    .filter((candidate, index, values) => candidate && values.indexOf(candidate) === index);
  for (const candidate of candidates) {
    const resolvedCandidate = resolve(candidate);
    if (governedRoot && (resolvedCandidate === governedRoot || resolvedCandidate.startsWith(`${governedRoot}${sep}`))) {
      continue;
    }
    try {
      if (!existsSync(resolvedCandidate)) continue;
      accessSync(resolvedCandidate, fsConstants.W_OK);
      return resolvedCandidate;
    } catch {
      // Try the next isolated parent without weakening proof requirements.
    }
  }
  throw new Error("No writable isolated proof-storage parent is available outside the governed repository.");
}

function verifyLiveCanonicalRemoteProof(locator, binding, governedRepositoryPath) {
  let proofPath;
  try {
    proofPath = mkdtempSync(join(selectProofParent(governedRepositoryPath), "aaa-pl-live-canonical-remote-"));
    const init = runGit(proofPath, ["init", "--bare"]);
    if (!init.ok) {
      return liveRemoteFailure("LIVE_CANONICAL_REMOTE_ERROR", "ISOLATED_PROOF_STORAGE_FAILED", init.message);
    }
    const fetch = runGit(proofPath, [
      "-c",
      "protocol.version=2",
      "fetch",
      "--no-tags",
      "--depth=1",
      binding.canonical_remote,
      binding.subject.exact_commit,
    ]);
    if (!fetch.ok) {
      if (/couldn't find remote ref|not our ref|unadvertised object|no such ref/i.test(fetch.message ?? "")) {
        return liveRemoteFailure(
          "LIVE_CANONICAL_REMOTE_NOT_PROVEN",
          "EXACT_COMMIT_NOT_INDEPENDENTLY_PROVEN",
          fetch.message,
        );
      }
      return liveRemoteFailure(
        "LIVE_CANONICAL_REMOTE_ERROR",
        "REMOTE_NETWORK_FAILURE",
        fetch.message,
        { transport_failure_state: fetch.state },
      );
    }

    const fetchedCommit = runGit(proofPath, ["rev-parse", "--verify", "FETCH_HEAD^{commit}"]);
    if (!fetchedCommit.ok) {
      return liveRemoteFailure("LIVE_CANONICAL_REMOTE_NOT_PROVEN", "EXACT_COMMIT_NOT_INDEPENDENTLY_PROVEN", fetchedCommit.message);
    }
    const observedCommit = fetchedCommit.stdout.toString("ascii").trim().toLowerCase();
    if (observedCommit !== binding.subject.exact_commit.toLowerCase()) {
      return liveRemoteFailure("LIVE_CANONICAL_REMOTE_CONFLICT", "REMOTE_COMMIT_MISMATCH");
    }

    const treeRead = runGit(proofPath, ["rev-parse", "--verify", `${observedCommit}^{tree}`]);
    if (!treeRead.ok) return liveRemoteFailure("LIVE_CANONICAL_REMOTE_CONFLICT", "REMOTE_COMMIT_TREE_MISMATCH", treeRead.message);
    const observedTree = treeRead.stdout.toString("ascii").trim().toLowerCase();
    if (observedTree !== binding.subject.exact_tree.toLowerCase()) {
      return liveRemoteFailure(
        "LIVE_CANONICAL_REMOTE_CONFLICT",
        "REMOTE_COMMIT_TREE_MISMATCH",
        undefined,
        { observed_tree: observedTree },
      );
    }

    const pathRead = runGit(proofPath, ["rev-parse", "--verify", `${observedCommit}:${binding.subject.exact_path}`]);
    if (!pathRead.ok) return liveRemoteFailure("LIVE_CANONICAL_REMOTE_CONFLICT", "REMOTE_PATH_BLOB_CONFLICT", pathRead.message);
    const observedBlob = pathRead.stdout.toString("ascii").trim().toLowerCase();
    if (observedBlob !== locator.git_blob.toLowerCase() || observedBlob !== binding.subject.git_blob.toLowerCase()) {
      return liveRemoteFailure(
        "LIVE_CANONICAL_REMOTE_CONFLICT",
        "REMOTE_PATH_BLOB_CONFLICT",
        undefined,
        { observed_blob: observedBlob },
      );
    }

    const blobRead = runGit(proofPath, ["cat-file", "blob", observedBlob]);
    if (!blobRead.ok) return liveRemoteFailure("LIVE_CANONICAL_REMOTE_CONFLICT", "REMOTE_PATH_BLOB_CONFLICT", blobRead.message);
    const observedSha256 = createHash("sha256").update(blobRead.stdout).digest("hex");
    const observedByteSize = blobRead.stdout.length;
    if (observedSha256 !== locator.sha256.toLowerCase() || observedByteSize !== locator.byte_size) {
      return liveRemoteFailure(
        "LIVE_CANONICAL_REMOTE_CONFLICT",
        "REMOTE_PATH_CONTENT_IDENTITY_MISMATCH",
        undefined,
        { observed_sha256: observedSha256, observed_byte_size: observedByteSize },
      );
    }
    return {
      ok: true,
      state: "LIVE_CANONICAL_REMOTE_VERIFIED",
      canonical_remote: binding.canonical_remote,
      exact_commit: observedCommit,
      exact_tree: observedTree,
      exact_path: binding.subject.exact_path,
      git_blob: observedBlob,
      sha256: observedSha256,
      byte_size: observedByteSize,
      fresh_network_operation_attempted: true,
      fresh_network_readback_succeeded: true,
      isolated_temporary_proof_storage: true,
      governed_repository_mutated_for_proof: false,
    };
  } catch (error) {
    return liveRemoteFailure(
      "LIVE_CANONICAL_REMOTE_ERROR",
      "REMOTE_NETWORK_FAILURE",
      error instanceof Error ? error.message : String(error),
    );
  } finally {
    if (proofPath) rmSync(proofPath, { recursive: true, force: true });
  }
}

function allRequiredAxesVerified(axes) {
  return axes.artifact_identity_state === "ARTIFACT_IDENTITY_VERIFIED"
    && axes.owner_authority_state === "OWNER_AUTHORIZED"
    && axes.live_canonical_remote_state === "LIVE_CANONICAL_REMOTE_VERIFIED"
    && ["SEMANTIC_DIGEST_VERIFIED", "NOT_APPLICABLE"].includes(axes.semantic_content_digest_state)
    && axes.lineage_state === "LINEAGE_VERIFIED"
    && axes.provenance_state === "PROVENANCE_VERIFIED";
}

export const __testing = Object.freeze({
  allRequiredAxesVerified,
  selectGovernedBinding,
  verifyCallerCompatibility,
  verifyLiveCanonicalRemoteProof,
});

export function verifyLocator(locator, options = {}) {
  const schemaFailure = validateLocatorRecord(locator);
  if (schemaFailure) {
    return {
      ...schemaFailure,
      artifact_identity_state: "NOT_PROVEN",
      owner_authority_state: "NOT_PROVEN",
      live_canonical_remote_state: "LIVE_CANONICAL_REMOTE_NOT_PROVEN",
      semantic_content_digest_state: "NOT_PROVEN",
      lineage_state: "NOT_PROVEN",
      provenance_state: "NOT_PROVEN",
    };
  }

  const repositoryPath = resolve(options.repositoryPath ?? process.cwd());
  const axes = {
    artifact_identity_state: "NOT_PROVEN",
    owner_authority_state: "NOT_PROVEN",
    live_canonical_remote_state: "LIVE_CANONICAL_REMOTE_NOT_PROVEN",
    semantic_content_digest_state: "NOT_PROVEN",
    lineage_state: "NOT_PROVEN",
    provenance_state: "NOT_PROVEN",
  };
  const fail = (reason, state = "RETRIEVAL_FAILED", extra = {}) => ({
    state,
    verified: false,
    reason,
    repository: locator.repository,
    exact_commit: locator.exact_commit,
    exact_path: locator.exact_path,
    ...axes,
    ...extra,
  });

  try {
    const selected = selectGovernedBinding(locator);
    if (!selected.ok) {
      axes.owner_authority_state = selected.proof_state;
      return fail(selected.reason);
    }
    const binding = selected.binding;

    const repositoryCheck = runGit(repositoryPath, ["rev-parse", "--is-inside-work-tree"]);
    if (!repositoryCheck.ok) return fail(repositoryCheck.reason, repositoryCheck.state, { message: repositoryCheck.message });

    const artifactIdentity = verifyExactIdentityRecord(locator, repositoryPath);
    if (!artifactIdentity.ok) {
      axes.artifact_identity_state = artifactIdentity.reason === "IDENTITY_MISMATCH" ? "CONFLICT" : "NOT_PROVEN";
      return fail(artifactIdentity.reason, artifactIdentity.state, {
        message: artifactIdentity.message,
        mismatch_fields: artifactIdentity.mismatch_fields,
      });
    }
    axes.artifact_identity_state = "ARTIFACT_IDENTITY_VERIFIED";

    const compatibility = verifyCallerCompatibility(locator, options.verificationContext, binding);
    if (!compatibility.ok) {
      axes.owner_authority_state = compatibility.proof_state;
      axes.lineage_state = compatibility.proof_state;
      axes.provenance_state = compatibility.proof_state;
      return fail(compatibility.reason, "RETRIEVAL_FAILED", { message: compatibility.message });
    }

    const ownerAuthority = verifyGovernedOwnerAuthority(binding, repositoryPath);
    if (!ownerAuthority.ok) {
      axes.owner_authority_state = ownerAuthority.proof_state;
      return fail(ownerAuthority.reason);
    }
    axes.owner_authority_state = ownerAuthority.state;

    const semantic = verifyGovernedSemanticDigest(locator, binding, artifactIdentity.blob);
    if (!semantic.ok) {
      axes.semantic_content_digest_state = semantic.proof_state;
      return fail(semantic.reason, "RETRIEVAL_FAILED", { observed_semantic_content_digest: semantic.observed_digest });
    }
    axes.semantic_content_digest_state = semantic.state;

    const lineage = verifyGovernedLineage(locator, binding, repositoryPath, artifactIdentity.blob);
    if (!lineage.ok) {
      axes.lineage_state = lineage.proof_state;
      return fail(lineage.reason);
    }
    axes.lineage_state = lineage.state;
    axes.provenance_state = "PROVENANCE_VERIFIED";

    const liveRemote = verifyLiveCanonicalRemoteProof(locator, binding, repositoryPath);
    axes.live_canonical_remote_state = liveRemote.state;
    if (!liveRemote.ok) {
      return fail(liveRemote.reason, "RETRIEVAL_FAILED", {
        message: liveRemote.message,
        fresh_network_operation_attempted: liveRemote.fresh_network_operation_attempted,
        isolated_temporary_proof_storage: liveRemote.isolated_temporary_proof_storage,
        governed_repository_mutated_for_proof: liveRemote.governed_repository_mutated_for_proof,
        remote_transport_failure_state: liveRemote.transport_failure_state,
        artifact_invalid: false,
      });
    }

    if (!allRequiredAxesVerified(axes)) {
      return fail("REQUIRED_STATE_AXIS_NOT_VERIFIED");
    }
    return {
      state: "VERIFIED_EXACT",
      verified: true,
      repository: locator.repository,
      exact_commit: locator.exact_commit.toLowerCase(),
      exact_tree: binding.subject.exact_tree,
      exact_path: locator.exact_path,
      git_blob: artifactIdentity.observed_blob,
      sha256: locator.sha256.toLowerCase(),
      byte_size: locator.byte_size,
      ...axes,
      repository_identity_state: liveRemote.state,
      repository_authorization_ref: ownerAuthority.authority_artifact_id,
      authority_principal: ownerAuthority.authority_principal,
      approved_scope_digest: ownerAuthority.approved_scope_digest,
      semantic_profile_id: semantic.profile_id,
      semantic_canonical_input_byte_size: semantic.canonical_input_byte_size,
      semantic_content_digest: semantic.semantic_content_digest,
      lineage_ref: binding.lineage_ref,
      lineage_proof_profile: SUBJECT_DECLARED_PREDECESSOR_PROFILE,
      lineage_relationship_type: lineage.relationship,
      lineage_referenced_artifact_id: lineage.referenced_artifact_id,
      lineage_referenced_artifact_version: lineage.referenced_artifact_version,
      provenance_evidence_profile: ACCEPTED_TARGET_PROVENANCE_PROFILE,
      provenance_evidence_artifact_id: ownerAuthority.authority_artifact_id,
      fresh_network_operation_attempted: liveRemote.fresh_network_operation_attempted,
      fresh_network_readback_succeeded: liveRemote.fresh_network_readback_succeeded,
      isolated_temporary_proof_storage: liveRemote.isolated_temporary_proof_storage,
      governed_repository_mutated_for_proof: liveRemote.governed_repository_mutated_for_proof,
      discovery_branch_used_for_identity: false,
      caller_assertion_used_as_trust_root: false,
    };
  } catch (error) {
    axes.artifact_identity_state = axes.artifact_identity_state === "NOT_PROVEN" ? "UNKNOWN" : axes.artifact_identity_state;
    axes.owner_authority_state = axes.owner_authority_state === "NOT_PROVEN" ? "UNKNOWN" : axes.owner_authority_state;
    axes.live_canonical_remote_state = "LIVE_CANONICAL_REMOTE_ERROR";
    return fail("UNCLASSIFIED_VERIFIER_EXCEPTION", "UNKNOWN", {
      message: error instanceof Error ? error.message : String(error),
    });
  }
}

function parseArguments(argv) {
  if (argv.length < 2 || argv[0] !== "verify") {
    throw new Error(
      "Usage: persistent_locator.mjs verify <locator.json> [--context <compatibility-assertions.json>] [--repo <git-worktree>]",
    );
  }
  const locatorPath = argv[1];
  let repositoryPath = process.cwd();
  let contextPath = null;
  for (let index = 2; index < argv.length; index += 1) {
    if (argv[index] === "--repo" && argv[index + 1]) {
      repositoryPath = argv[index + 1];
      index += 1;
    } else if (argv[index] === "--context" && argv[index + 1]) {
      contextPath = argv[index + 1];
      index += 1;
    } else {
      throw new Error(`Unknown argument: ${argv[index]}`);
    }
  }
  return { locatorPath, repositoryPath, contextPath };
}

function main() {
  try {
    const { locatorPath, repositoryPath, contextPath } = parseArguments(process.argv.slice(2));
    const parsed = JSON.parse(readFileSync(resolve(locatorPath), "utf8"));
    const verificationContext = contextPath ? JSON.parse(readFileSync(resolve(contextPath), "utf8")) : undefined;
    const locator = parsed.locator ?? parsed;
    const result = verifyLocator(locator, { repositoryPath, verificationContext });
    process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
    process.exitCode = EXIT_CODES[result.state] ?? EXIT_CODES.UNKNOWN;
  } catch (error) {
    const result = {
      state: "UNKNOWN",
      verified: false,
      reason: "CLI_INPUT_OR_EXECUTION_ERROR",
      message: error instanceof Error ? error.message : String(error),
    };
    process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
    process.exitCode = EXIT_CODES.UNKNOWN;
  }
}

if (import.meta.url === pathToFileURL(process.argv[1] ?? "").href) {
  main();
}
