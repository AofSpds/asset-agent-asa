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

export function validateLocatorRecord(locator) {
  if (!locator || typeof locator !== "object" || Array.isArray(locator)) {
    return invalidLocator("Locator must be a JSON object.", null);
  }
  for (const field of REQUIRED_LOCATOR_FIELDS) {
    if (!(field in locator)) {
      return invalidLocator(`Missing required field: ${field}`, field);
    }
  }
  for (const field of ["repository", "exact_commit", "exact_path", "git_blob", "sha256", "lineage_ref"]) {
    if (typeof locator[field] !== "string" || locator[field].length === 0) {
      return invalidLocator(`${field} must be a non-empty string.`, field);
    }
  }
  if (!/^[0-9a-f]{40}$/i.test(locator.exact_commit)) {
    return invalidLocator("exact_commit must be a full 40-hex Git commit.", "exact_commit");
  }
  if (!/^[0-9a-f]{40}$/i.test(locator.git_blob)) {
    return invalidLocator("git_blob must be a full 40-hex Git blob.", "git_blob");
  }
  if (!/^[0-9a-f]{64}$/i.test(locator.sha256)) {
    return invalidLocator("sha256 must be a full 64-hex digest.", "sha256");
  }
  if (!Number.isSafeInteger(locator.byte_size) || locator.byte_size < 0) {
    return invalidLocator("byte_size must be a non-negative safe integer.", "byte_size");
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

export function verifyLocator(locator, options = {}) {
  const schemaFailure = validateLocatorRecord(locator);
  if (schemaFailure) return schemaFailure;

  const repositoryPath = resolve(options.repositoryPath ?? process.cwd());
  try {
    const repositoryCheck = runGit(repositoryPath, ["rev-parse", "--is-inside-work-tree"]);
    if (!repositoryCheck.ok) return failure(locator, repositoryCheck);

    const commitCheck = runGit(repositoryPath, ["cat-file", "-e", `${locator.exact_commit}^{commit}`]);
    if (!commitCheck.ok) return failure(locator, commitCheck);

    const pathResolution = runGit(repositoryPath, [
      "rev-parse",
      "--verify",
      `${locator.exact_commit}:${locator.exact_path}`,
    ]);
    if (!pathResolution.ok) return failure(locator, pathResolution);

    const observedBlob = pathResolution.stdout.toString("ascii").trim().toLowerCase();
    const expectedBlob = locator.git_blob.toLowerCase();
    if (observedBlob !== expectedBlob) {
      return failure(
        locator,
        { state: "RETRIEVAL_FAILED", reason: "IDENTITY_MISMATCH" },
        { mismatch_fields: ["git_blob"], expected_git_blob: expectedBlob, observed_git_blob: observedBlob },
      );
    }

    const blobRead = runGit(repositoryPath, ["cat-file", "blob", observedBlob]);
    if (!blobRead.ok) return failure(locator, blobRead);

    const observedSha256 = createHash("sha256").update(blobRead.stdout).digest("hex");
    const observedByteSize = blobRead.stdout.length;
    const mismatchFields = [];
    if (observedSha256 !== locator.sha256.toLowerCase()) mismatchFields.push("sha256");
    if (observedByteSize !== locator.byte_size) mismatchFields.push("byte_size");
    if (mismatchFields.length > 0) {
      return failure(
        locator,
        { state: "RETRIEVAL_FAILED", reason: "IDENTITY_MISMATCH" },
        {
          mismatch_fields: mismatchFields,
          observed_sha256: observedSha256,
          observed_byte_size: observedByteSize,
        },
      );
    }

    return {
      state: "VERIFIED_EXACT",
      verified: true,
      repository: locator.repository,
      exact_commit: locator.exact_commit.toLowerCase(),
      exact_path: locator.exact_path,
      git_blob: observedBlob,
      sha256: observedSha256,
      byte_size: observedByteSize,
      semantic_content_digest_state:
        locator.semantic_content_digest_if_applicable === null
          ? "NOT_APPLICABLE"
          : "REGISTERED_PROFILE_SPECIFIC_RECOMPUTATION_REQUIRED",
      lineage_ref: locator.lineage_ref,
      discovery_branch_used_for_identity: false,
    };
  } catch (error) {
    return failure(locator, {
      state: "UNKNOWN",
      reason: "UNCLASSIFIED_VERIFIER_EXCEPTION",
      message: error instanceof Error ? error.message : String(error),
    });
  }
}

function parseArguments(argv) {
  if (argv.length < 2 || argv[0] !== "verify") {
    throw new Error("Usage: persistent_locator.mjs verify <locator.json> [--repo <git-worktree>]");
  }
  const locatorPath = argv[1];
  let repositoryPath = process.cwd();
  for (let index = 2; index < argv.length; index += 1) {
    if (argv[index] === "--repo" && argv[index + 1]) {
      repositoryPath = argv[index + 1];
      index += 1;
    } else {
      throw new Error(`Unknown argument: ${argv[index]}`);
    }
  }
  return { locatorPath, repositoryPath };
}

function main() {
  try {
    const { locatorPath, repositoryPath } = parseArguments(process.argv.slice(2));
    const parsed = JSON.parse(readFileSync(resolve(locatorPath), "utf8"));
    const locator = parsed.locator ?? parsed;
    const result = verifyLocator(locator, { repositoryPath });
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
