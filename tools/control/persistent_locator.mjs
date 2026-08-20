#!/usr/bin/env node

import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
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
  if (scpLike) {
    pathname = scpLike[2];
  } else {
    try {
      pathname = new URL(trimmed).pathname;
    } catch {
      return null;
    }
  }
  const segments = pathname.replace(/^\/+/, "").split("/").filter(Boolean);
  if (segments.length !== 2) return null;
  return `${segments[0]}/${segments[1]}`;
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

function verifyAuthorizationEvidence(locator, evidence, repositoryPath, proofField, claimProfile, authorizationRef) {
  if (!evidence || evidence.repository !== locator.repository) {
    return { ok: false, proof_state: "PARTIAL", message: `${proofField} authorization evidence is incomplete.` };
  }
  if (claimProfile !== "AAA_OWNER_DECISION_ACCEPTED_EXACT_TARGET_v0.1") {
    return { ok: false, proof_state: "PARTIAL", message: `${proofField} authorization claim profile is missing or unsupported.` };
  }
  const verified = verifyExactIdentityRecord(evidence, repositoryPath);
  if (!verified.ok) {
    return {
      ok: false,
      proof_state: verified.reason === "PARTIAL_IDENTITY_RECORD" ? "PARTIAL" : "NOT_PROVEN",
      message: `${proofField} authorization evidence exact identity was not proven.`,
    };
  }
  const remoteReachability = runGit(repositoryPath, [
    "for-each-ref",
    "--format=%(refname)",
    `--contains=${evidence.exact_commit}`,
    "refs/remotes/",
  ]);
  if (!remoteReachability.ok || remoteReachability.stdout.toString("utf8").trim().length === 0) {
    return { ok: false, proof_state: "NOT_PROVEN", message: `${proofField} authorization evidence remote reachability was not proven.` };
  }
  let authorizationArtifact;
  try {
    authorizationArtifact = JSON.parse(verified.blob.toString("utf8"));
  } catch {
    return { ok: false, proof_state: "CONFLICT", message: `${proofField} authorization evidence is not valid JSON.` };
  }
  const accepted = authorizationArtifact.accepted_exact_s0_target;
  const acceptedIdentity = accepted && {
    repository: accepted.repository,
    exact_commit: accepted.commit,
    exact_path: accepted.path,
    git_blob: accepted.git_blob,
    sha256: accepted.sha256,
    byte_size: accepted.byte_size,
  };
  if (
    authorizationArtifact.artifact_id !== authorizationRef
    || evidence.artifact_id !== authorizationRef
    || authorizationArtifact.approved_semantic_scope?.s0_result_accepted !== true
    || authorizationArtifact.approved_semantic_scope?.apply_validated_s0_capability !== true
    || !identityMatches(acceptedIdentity, locator)
  ) {
    return { ok: false, proof_state: "CONFLICT", message: `${proofField} authorization evidence does not accept the exact subject identity.` };
  }
  return { ok: true };
}

function verifyRepositoryBinding(locator, context, repositoryPath) {
  const bindings = Array.isArray(context?.repository_bindings) ? context.repository_bindings : [];
  const selected = requireExactlyOne(bindings.filter((binding) => binding?.repository === locator.repository));
  if (!selected.ok) {
    return { ok: false, proof_state: selected.proof_state, reason: "REPOSITORY_IDENTITY_NOT_PROVEN" };
  }
  const binding = selected.record;
  if (
    binding.authorized !== true
    || typeof binding.authorization_ref !== "string"
    || typeof binding.remote_name !== "string"
    || !Array.isArray(binding.allowed_remote_urls)
    || binding.require_commit_reachable_from_remote_tracking_ref !== true
  ) {
    return { ok: false, proof_state: "PARTIAL", reason: "REPOSITORY_IDENTITY_NOT_PROVEN" };
  }
  const authorization = verifyAuthorizationEvidence(
    locator,
    binding.authorization_evidence,
    repositoryPath,
    "repository",
    binding.authorization_claim_profile,
    binding.authorization_ref,
  );
  if (!authorization.ok) {
    return { ok: false, proof_state: authorization.proof_state, reason: "REPOSITORY_IDENTITY_NOT_PROVEN", message: authorization.message };
  }
  const remoteRead = runGit(repositoryPath, ["remote", "get-url", binding.remote_name]);
  if (!remoteRead.ok) {
    return { ok: false, proof_state: "NOT_PROVEN", reason: "REPOSITORY_IDENTITY_NOT_PROVEN", message: remoteRead.message };
  }
  const observedRemote = remoteRead.stdout.toString("utf8").trim();
  const normalizedRepository = normalizeRemoteRepository(observedRemote);
  if (!binding.allowed_remote_urls.includes(observedRemote) || normalizedRepository !== locator.repository) {
    return {
      ok: false,
      proof_state: "CONFLICT",
      reason: "REPOSITORY_IDENTITY_CONFLICT",
      message: `Observed remote does not bind to authorized repository ${locator.repository}.`,
    };
  }
  const remoteNamespace = `refs/remotes/${binding.remote_name}/`;
  const reachability = runGit(repositoryPath, [
    "for-each-ref",
    "--format=%(refname)",
    `--contains=${locator.exact_commit}`,
    remoteNamespace,
  ]);
  if (!reachability.ok || reachability.stdout.toString("utf8").trim().length === 0) {
    return {
      ok: false,
      proof_state: "NOT_PROVEN",
      reason: "REPOSITORY_COMMIT_REACHABILITY_NOT_PROVEN",
      message: `Exact commit is not reachable from ${remoteNamespace}.`,
    };
  }
  return {
    ok: true,
    state: "REPOSITORY_VERIFIED",
    remote_name: binding.remote_name,
    observed_remote: observedRemote,
    remote_tracking_ref_evidence: reachability.stdout.toString("utf8").trim().split(/\r?\n/),
    authorization_ref: binding.authorization_ref,
  };
}

function verifySemanticDigest(locator, context, repositoryPath, blobBytes) {
  if (locator.semantic_content_digest_if_applicable === null) {
    return { ok: true, state: "NOT_APPLICABLE", profile_id: null };
  }
  const profiles = Array.isArray(context?.semantic_profiles) ? context.semantic_profiles : [];
  const selected = requireExactlyOne(profiles.filter((profile) => identityMatches(profile?.applies_to, locator)));
  if (!selected.ok) {
    return { ok: false, proof_state: selected.proof_state, reason: "SEMANTIC_PROFILE_NOT_PROVEN" };
  }
  const profile = selected.record;
  if (
    profile.authorized !== true
    || typeof profile.authorization_ref !== "string"
    || typeof profile.profile_id !== "string"
    || profile.digest_algorithm !== "SHA256"
    || profile.canonicalization !== CANONICAL_JSON_PROFILE
    || profile.selection?.type !== "TOP_LEVEL_VALUE"
    || typeof profile.selection?.field !== "string"
  ) {
    return { ok: false, proof_state: "PARTIAL", reason: "SEMANTIC_PROFILE_NOT_PROVEN" };
  }
  const authorization = verifyAuthorizationEvidence(
    locator,
    profile.authorization_evidence,
    repositoryPath,
    "semantic profile",
    profile.authorization_claim_profile,
    profile.authorization_ref,
  );
  if (!authorization.ok) {
    return { ok: false, proof_state: authorization.proof_state, reason: "SEMANTIC_PROFILE_NOT_PROVEN", message: authorization.message };
  }
  let artifact;
  try {
    artifact = JSON.parse(blobBytes.toString("utf8"));
  } catch {
    return { ok: false, proof_state: "CONFLICT", reason: "SEMANTIC_PROFILE_INPUT_INVALID" };
  }
  if (artifact.semantic_digest_profile !== profile.profile_id || !(profile.selection.field in artifact)) {
    return { ok: false, proof_state: "CONFLICT", reason: "SEMANTIC_PROFILE_ARTIFACT_BINDING_CONFLICT" };
  }
  const canonicalInput = Buffer.from(JSON.stringify(stableValue(artifact[profile.selection.field])), "utf8");
  const observedDigest = createHash("sha256").update(canonicalInput).digest("hex");
  if (observedDigest !== locator.semantic_content_digest_if_applicable.toLowerCase()) {
    return {
      ok: false,
      proof_state: "CONFLICT",
      reason: "SEMANTIC_DIGEST_MISMATCH",
      observed_semantic_content_digest: observedDigest,
    };
  }
  return {
    ok: true,
    state: "SEMANTIC_DIGEST_VERIFIED",
    profile_id: profile.profile_id,
    canonical_input_byte_size: canonicalInput.length,
    semantic_content_digest: observedDigest,
    authorization_ref: profile.authorization_ref,
  };
}

function verifyLineage(locator, context, repositoryPath) {
  const records = Array.isArray(context?.lineage_records) ? context.lineage_records : [];
  const selected = requireExactlyOne(records.filter((record) => record?.lineage_ref === locator.lineage_ref));
  if (!selected.ok) {
    return { ok: false, proof_state: selected.proof_state, reason: "LINEAGE_NOT_VERIFIED" };
  }
  const record = selected.record;
  if (!identityMatches(record.subject, locator) || typeof record.relationship_type !== "string" || record.relationship_type.length === 0) {
    return { ok: false, proof_state: "CONFLICT", reason: "LINEAGE_CONFLICT" };
  }
  if (record.authorized_relation !== true || typeof record.authorization_ref !== "string" || !record.referenced_artifact) {
    return { ok: false, proof_state: "PARTIAL", reason: "LINEAGE_NOT_VERIFIED" };
  }
  if (record.referenced_artifact.repository !== locator.repository) {
    return { ok: false, proof_state: "CONFLICT", reason: "LINEAGE_CONFLICT" };
  }
  const referencedArtifact = verifyExactIdentityRecord(record.referenced_artifact, repositoryPath);
  if (!referencedArtifact.ok) {
    return {
      ok: false,
      proof_state: referencedArtifact.reason === "PARTIAL_IDENTITY_RECORD" ? "PARTIAL" : "NOT_PROVEN",
      reason: "LINEAGE_REFERENCED_ARTIFACT_NOT_PROVEN",
    };
  }
  let referencedArtifactContent;
  try {
    referencedArtifactContent = JSON.parse(referencedArtifact.blob.toString("utf8"));
  } catch {
    return { ok: false, proof_state: "CONFLICT", reason: "LINEAGE_REFERENCED_ARTIFACT_INVALID" };
  }
  if (referencedArtifactContent.work_item_id !== locator.lineage_ref) {
    return { ok: false, proof_state: "CONFLICT", reason: "LINEAGE_REF_BINDING_CONFLICT" };
  }
  const authorization = verifyAuthorizationEvidence(
    locator,
    record.authorization_evidence,
    repositoryPath,
    "lineage",
    record.authorization_claim_profile,
    record.authorization_ref,
  );
  if (!authorization.ok) {
    return { ok: false, proof_state: authorization.proof_state, reason: "LINEAGE_AUTHORIZATION_NOT_PROVEN", message: authorization.message };
  }
  return {
    ok: true,
    state: "LINEAGE_VERIFIED",
    lineage_ref: locator.lineage_ref,
    relationship_type: record.relationship_type,
    referenced_artifact_id: record.referenced_artifact.artifact_id ?? null,
    authorization_ref: record.authorization_ref,
  };
}

function verifyProvenance(locator, context, repositoryPath, verifiedLineage) {
  const records = Array.isArray(context?.provenance_records) ? context.provenance_records : [];
  const selected = requireExactlyOne(records.filter((record) => (
    record?.lineage_ref === locator.lineage_ref && identityMatches(record?.subject, locator)
  )));
  if (!selected.ok) {
    return { ok: false, proof_state: selected.proof_state, reason: "PROVENANCE_NOT_VERIFIED" };
  }
  const record = selected.record;
  if (
    record.authorized !== true
    || record.provenance_assertion !== "EXPLICIT_PROVENANCE_EVIDENCE"
    || record.relationship_type !== verifiedLineage.relationship_type
    || typeof record.authorization_ref !== "string"
    || !record.evidence
  ) {
    return { ok: false, proof_state: "PARTIAL", reason: "PROVENANCE_NOT_VERIFIED" };
  }
  if (record.evidence.repository !== locator.repository) {
    return { ok: false, proof_state: "CONFLICT", reason: "PROVENANCE_CONFLICT" };
  }
  const evidence = verifyAuthorizationEvidence(
    locator,
    record.evidence,
    repositoryPath,
    "provenance",
    record.authorization_claim_profile,
    record.authorization_ref,
  );
  if (!evidence.ok) {
    return { ok: false, proof_state: evidence.proof_state, reason: "PROVENANCE_EVIDENCE_NOT_PROVEN", message: evidence.message };
  }
  return {
    ok: true,
    state: "PROVENANCE_VERIFIED",
    relationship_type: record.relationship_type,
    evidence_artifact_id: record.evidence.artifact_id ?? null,
    authorization_ref: record.authorization_ref,
  };
}

export function verifyLocator(locator, options = {}) {
  const schemaFailure = validateLocatorRecord(locator);
  if (schemaFailure) return schemaFailure;

  const repositoryPath = resolve(options.repositoryPath ?? process.cwd());
  const verificationContext = options.verificationContext;
  if (!verificationContext || typeof verificationContext !== "object" || Array.isArray(verificationContext)) {
    return proofFailure(
      locator,
      "VERIFICATION_CONTEXT_REQUIRED",
      {
        repository_identity_state: "NOT_PROVEN",
        semantic_content_digest_state: "NOT_PROVEN",
        lineage_state: "NOT_PROVEN",
        provenance_state: "NOT_PROVEN",
      },
      "VERIFIED_EXACT requires governed repository, semantic-profile, lineage, and provenance evidence.",
    );
  }

  try {
    const repositoryCheck = runGit(repositoryPath, ["rev-parse", "--is-inside-work-tree"]);
    if (!repositoryCheck.ok) return failure(locator, repositoryCheck);

    const commitCheck = runGit(repositoryPath, ["cat-file", "-e", `${locator.exact_commit}^{commit}`]);
    if (!commitCheck.ok) return failure(locator, commitCheck);

    const exactIdentity = verifyExactIdentityRecord(locator, repositoryPath);
    if (!exactIdentity.ok) {
      return failure(
        locator,
        exactIdentity,
        {
          mismatch_fields: exactIdentity.mismatch_fields,
          repository_identity_state: "NOT_PROVEN",
          semantic_content_digest_state: "NOT_PROVEN",
          lineage_state: "NOT_PROVEN",
          provenance_state: "NOT_PROVEN",
        },
      );
    }

    const repositoryBinding = verifyRepositoryBinding(locator, verificationContext, repositoryPath);
    if (!repositoryBinding.ok) {
      return proofFailure(
        locator,
        repositoryBinding.reason,
        {
          repository_identity_state: repositoryBinding.proof_state,
          semantic_content_digest_state: "NOT_PROVEN",
          lineage_state: "NOT_PROVEN",
          provenance_state: "NOT_PROVEN",
        },
        repositoryBinding.message,
      );
    }

    const semanticVerification = verifySemanticDigest(locator, verificationContext, repositoryPath, exactIdentity.blob);
    if (!semanticVerification.ok) {
      return proofFailure(
        locator,
        semanticVerification.reason,
        {
          repository_identity_state: repositoryBinding.state,
          semantic_content_digest_state: semanticVerification.proof_state,
          lineage_state: "NOT_PROVEN",
          provenance_state: "NOT_PROVEN",
          observed_semantic_content_digest: semanticVerification.observed_semantic_content_digest,
        },
      );
    }

    const lineageVerification = verifyLineage(locator, verificationContext, repositoryPath);
    if (!lineageVerification.ok) {
      return proofFailure(
        locator,
        lineageVerification.reason,
        {
          repository_identity_state: repositoryBinding.state,
          semantic_content_digest_state: semanticVerification.state,
          lineage_state: lineageVerification.proof_state,
          provenance_state: "NOT_PROVEN",
        },
        lineageVerification.message,
      );
    }

    const provenanceVerification = verifyProvenance(locator, verificationContext, repositoryPath, lineageVerification);
    if (!provenanceVerification.ok) {
      return proofFailure(
        locator,
        provenanceVerification.reason,
        {
          repository_identity_state: repositoryBinding.state,
          semantic_content_digest_state: semanticVerification.state,
          lineage_state: lineageVerification.state,
          provenance_state: provenanceVerification.proof_state,
        },
      );
    }

    return {
      state: "VERIFIED_EXACT",
      verified: true,
      repository: locator.repository,
      exact_commit: locator.exact_commit.toLowerCase(),
      exact_path: locator.exact_path,
      git_blob: exactIdentity.observed_blob,
      sha256: locator.sha256.toLowerCase(),
      byte_size: locator.byte_size,
      repository_identity_state: repositoryBinding.state,
      repository_authorization_ref: repositoryBinding.authorization_ref,
      repository_remote_tracking_ref_evidence: repositoryBinding.remote_tracking_ref_evidence,
      semantic_content_digest_state: semanticVerification.state,
      semantic_profile_id: semanticVerification.profile_id,
      semantic_canonical_input_byte_size: semanticVerification.canonical_input_byte_size,
      semantic_content_digest: semanticVerification.semantic_content_digest,
      lineage_state: lineageVerification.state,
      lineage_ref: lineageVerification.lineage_ref,
      lineage_relationship_type: lineageVerification.relationship_type,
      lineage_authorization_ref: lineageVerification.authorization_ref,
      provenance_state: provenanceVerification.state,
      provenance_evidence_artifact_id: provenanceVerification.evidence_artifact_id,
      provenance_authorization_ref: provenanceVerification.authorization_ref,
      discovery_branch_used_for_identity: false,
    };
  } catch (error) {
    return failure(
      locator,
      {
        state: "UNKNOWN",
        reason: "UNCLASSIFIED_VERIFIER_EXCEPTION",
        message: error instanceof Error ? error.message : String(error),
      },
      {
        repository_identity_state: "UNKNOWN",
        semantic_content_digest_state: "UNKNOWN",
        lineage_state: "UNKNOWN",
        provenance_state: "UNKNOWN",
      },
    );
  }
}

function parseArguments(argv) {
  if (argv.length < 2 || argv[0] !== "verify") {
    throw new Error(
      "Usage: persistent_locator.mjs verify <locator.json> --context <verification-context.json> [--repo <git-worktree>]",
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
  if (!contextPath) throw new Error("--context is required for repository, lineage, semantic, and provenance proof.");
  return { locatorPath, repositoryPath, contextPath };
}

function main() {
  try {
    const { locatorPath, repositoryPath, contextPath } = parseArguments(process.argv.slice(2));
    const parsed = JSON.parse(readFileSync(resolve(locatorPath), "utf8"));
    const verificationContext = JSON.parse(readFileSync(resolve(contextPath), "utf8"));
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
