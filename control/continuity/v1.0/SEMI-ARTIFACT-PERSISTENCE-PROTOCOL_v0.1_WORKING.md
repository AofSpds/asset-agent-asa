# SEMI ARTIFACT PERSISTENCE PROTOCOL

Version: v0.1_WORKING  
Status: CORE_A_DRAFT  
Project: semiconductor-research  
Owner Persona: SEMI-CONTROL-ARCHITECT

## 1. Purpose

Prevent important project artifacts from existing only as chat attachments, sandbox paths, temporary runtimes, filenames, or unverified output claims.

## 2. Storage roles

- GitHub = Control Plane: metadata, protocols, manifests, ledgers, schemas, checkpoints, control state, small text assets.
- AWS S3 ap-northeast-2 = Primary Data Plane for durable artifact bytes.
- Cloudflare R2 = Secondary Data Plane / backup where required.
- Chat runtime, sandbox, /mnt/data = ephemeral workspace only.

This protocol defines the control gate. It does not claim a storage write occurred unless a locator is actually verified.

## 3. Artifact lifecycle

Required sequence for an important artifact:

RECOVER_OR_CREATE
-> REOPEN_OR_REIMPORT
-> STRUCTURAL_VALIDATION
-> CONTENT_RECONCILIATION
-> SHA256_AND_BYTE_SIZE
-> PRIMARY_PERSISTENCE
-> SECONDARY_PERSISTENCE_IF_REQUIRED
-> ASSET_REGISTRATION
-> EVENT_LEDGER_ENTRY
-> COMMIT
-> FREEZE_OR_CANONICAL_PROMOTION_IF_ELIGIBLE

No skipped state may be implied by a later label.

## 4. Important artifact definition

An artifact is important when loss or ambiguity would materially affect any of:

- Ground Truth or PIT history.
- Price / CA / market-data readiness.
- Model definition or scorer behavior.
- Backtest reproducibility.
- Freeze or release evidence.
- Persona continuity.
- High reconstruction-cost research or adjudication lineage.

## 5. Required identity fields

Every important machine artifact must register at minimum:

- asset_id
- title
- artifact version
- parent_asset / lineage if known
- format
- authority_state
- artifact_state
- owner_persona
- byte_size
- sha256
- primary_locator
- secondary_locator or explicit NOT_REQUIRED / NOT_YET
- created_or_recovered_at
- last_verified
- verification method
- blockers

Filename is descriptive metadata, not identity.

## 6. Persistence gate states

### P0 EPHEMERAL
Bytes exist only in a temporary runtime.

### P1 IDENTITY_VERIFIED
Bytes have been hashed and structurally/content checked.

### P2 PRIMARY_PERSISTED
Exact bytes are verified at a durable primary locator.

### P3 REDUNDANTLY_PERSISTED
Exact bytes are also verified at approved secondary storage where required.

### P4 CONTROL_REGISTERED
Asset Registry and Event Ledger record the exact identity and locators.

### P5 FREEZE_ELIGIBLE
Required validation and authority gates are satisfied.

An artifact cannot be called CANONICAL or FROZEN below P4, and normally cannot be freeze-eligible below P3 for critical data artifacts unless an explicit exception is approved.

## 7. Reopen / reimport requirement

A tool reporting FILE_OUTPUT, export success, or a sandbox link does not prove a valid artifact.

After creation/export, the artifact must be reopened or reimported from the produced bytes and checked independently of the in-memory object that generated it.

For spreadsheets, inspect expected sheets, key tables/ranges, formulas/errors where applicable, and control totals.

## 8. Hash discipline

- SHA256 is mandatory for important artifacts.
- Hash is computed on exact persisted bytes, not a logical representation.
- Resave/re-export creates a new byte identity even if logical content appears unchanged.
- Historical recovered bytes must never be resaved before hashing.

## 9. Historical recovery rule

RECOVERY != REMATERIALIZATION.

When historical bytes are being recovered:

- preserve exact bytes;
- read-only inspect;
- hash and register;
- never patch the recovered historical file;
- never infer missing cells from later state;
- never assign a historical filename to reconstructed bytes.

If later deterministic reconstruction is authorized, it must receive a new artifact identity and explicit reconstructed lineage.

## 10. Primary and secondary persistence verification

A persistence claim requires a verified durable locator.

Verification should establish, where tooling permits:

- object exists;
- object size matches;
- checksum/hash identity matches or bytes are re-downloaded and re-hashed;
- storage version/object key is recorded;
- access permissions comply with project policy.

Do not mark PRIMARY_PERSISTED or SECONDARY_PERSISTED based only on an intended bucket/key.

## 11. Asset Registry authority

The global Asset Registry is the authoritative index for artifact identity and custody state.

Project-specific ledgers may reference assets but must not create competing artifact identity truth.

## 12. Mutation and versioning

- Frozen artifacts are immutable.
- A changed artifact receives a new version/asset identity.
- Logical state version and artifact version use separate namespaces.
- Reconstructed artifacts must be labeled reconstructed and linked to sources and replay method.
- Forensic artifacts with known contamination remain immutable evidence and cannot be silently cleaned in place.

## 13. Transfer between persona instances

A successor does not inherit artifact custody merely because a predecessor reported a path or hash.

Successor custody is verified only when it can access the bytes or a verified durable locator.

For critical artifacts, channel rotation must record:

- exact asset_id;
- SHA256;
- byte size;
- persistent locator;
- artifact state;
- unresolved custody risk.

## 14. U127 incident-derived prevention rule

The U127 incident established that logical state may outrun physical workbook materialization and that FILE_OUTPUT/version labels can survive after actual bytes disappear.

Therefore:

- workbook/artifact versions must not be used as Control-state versions;
- every important exported workbook must pass P1-P4 before the workflow relies on it as a parent;
- any next-round dependency on physical parent bytes must reference a registered asset_id and verified locator;
- if no physical parent is required, the workflow must explicitly state the logical System of Record rather than pretending a workbook parent exists.

## 15. Freeze eligibility

For a critical machine artifact, freeze requires:

- exact identity verified;
- persistent locator verified;
- required redundant storage verified or exception approved;
- structural/content validation PASS;
- lineage sufficiently resolved;
- independent validation completed when required;
- Control promotion recorded;
- final Owner approval where applicable.

## 16. Current known exception / blocker

U127 v0.7 is byte-verified in successor custody but not yet marked primary/secondary persisted. It remains a historical forensic anchor, not final Ground Truth authority.

No storage-state promotion may be made until actual durable locators are verified.