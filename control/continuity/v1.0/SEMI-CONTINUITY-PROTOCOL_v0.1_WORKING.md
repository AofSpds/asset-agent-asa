# SEMI CONTINUITY PROTOCOL

Version: v0.1_WORKING  
Status: CORE_A_DRAFT_PENDING_CORE_B_RECONCILIATION  
Project: semiconductor-research  
Owner Persona: SEMI-CONTROL-ARCHITECT

## 1. Purpose

Preserve project authority, state, rationale, assets, open work, and persona identity independently of any single chat channel, runtime, sandbox, or local mount.

## 2. Core identity model

- Persona = persistent organizational identity.
- Channel = ephemeral persona instance.
- Runtime = disposable execution environment.
- Handoff prompt = transport mechanism, not source of truth.
- Checkpoint = immutable succession baseline.
- Current State = materialized latest control view.
- Event Ledger = append-only accepted decision history.
- Asset Registry = durable artifact identity and custody record.

## 3. Mandatory persistence primitives

A persistent core persona must have:

1. Persona Manifest.
2. Global Asset Registry.
3. Append-only Event / Decision Ledger.
4. Materialized Current State.
5. Immutable Checkpoints.
6. Channel Registry containing predecessor/successor lineage.
7. Open Work / blocker state represented in Current State or referenced workplan.

Do not create competing authoritative registries for the same object class.

## 4. Authority invariants

1. NO_ACCEPTED_DECISION_WITHOUT_LEDGER_EVENT.
2. NO_IMPORTANT_ARTIFACT_WITHOUT_SHA256.
3. NO_CANONICAL_ARTIFACT_WITHOUT_PERSISTENT_LOCATOR.
4. NO_CHANNEL_ROTATION_WITHOUT_CHECKPOINT.
5. NO_SUCCESSOR_CHANNEL_WITHOUT_CHECKPOINT_LOAD.
6. NO_SELF_VALIDATION_BY_CONTROL_PERSONA.
7. NO_FROZEN_ARTIFACT_MUTATION.
8. EPHEMERAL_RUNTIME_IS_NOT_STORAGE.
9. LOGICAL_STATE_VERSION_NE_ARTIFACT_VERSION.
10. RETURN_PACKET_IS_TRANSPORT_NOT_SOURCE_OF_TRUTH.

## 5. Persona state classes

### Authority state

Examples:
- WORKING
- CONTROL_ACCEPTED
- FROZEN
- CANONICAL
- REJECTED
- FORENSIC_ONLY

### Artifact state

Examples:
- CREATED
- REOPENED
- STRUCTURALLY_VALIDATED
- CONTENT_RECONCILED
- HASHED
- PRIMARY_PERSISTED
- SECONDARY_PERSISTED
- REGISTERED
- FROZEN

These state axes must not be collapsed into a single word such as DONE.

## 6. Channel rotation gate

Before rotating a core persona instance, the active instance must:

1. Reconcile Current State against latest accepted decisions.
2. Append missing Event Ledger entries.
3. Update Asset Registry for all important artifacts.
4. Register all open lanes, blockers, pending returns, and unresolved conflicts.
5. Verify important artifact persistence state and record any unpersisted custody risk.
6. Create immutable checkpoint.
7. Commit checkpoint and supporting state to GitHub Control Plane.
8. Update Channel Registry with end checkpoint and intended successor.
9. Stop normal state mutation after handoff except explicit forensic recovery.

Rotation status remains ROTATING until successor load is verified.

## 7. Successor bootstrap gate

A successor instance must:

1. Load the designated checkpoint.
2. Verify repository and branch access.
3. Verify Persona Manifest and Channel Registry identity.
4. Reconcile Current State, Event Ledger tail, Asset Registry, and active workplan.
5. Confirm predecessor/successor linkage.
6. Verify critical artifact locators or explicitly record missing custody.
7. Compare core-domain state with any peer-core checkpoint/handoff.
8. Raise CONTROL_SYNC_REQUIRED for conflicts; never silently reconcile.
9. Append SUCCESSOR_BOOTSTRAP_VERIFIED event before taking normal authority.

## 8. Checkpoint strategy

Use two checkpoint forms:

- Delta checkpoint: normal channel rotation, compact record of changes since latest full baseline.
- Compacted full checkpoint: major milestone, freeze candidate, or after substantial schema/organization change.

Old checkpoints are immutable.

A checkpoint should minimally identify:

- checkpoint_id
- persona_id
- persona_instance_id
- predecessor_instance
- current Git SHA / branch
- Current State locator
- Asset Registry locator
- Event Ledger locator / tail event
- organization / authority contract version
- open blockers
- active work
- pending returns
- critical artifact custody summary
- unresolved CONTROL_SYNC_REQUIRED items

## 9. Knowledge persistence rule

High reconstruction-cost knowledge must be persisted as a KNOWLEDGE_ASSET rather than living only in conversation.

Priority examples:

- Five-axis model rationale.
- MFE / Top3 / Top10 / Critical Miss doctrine.
- PIT and first-supported-state logic.
- CA adjudication semantics.
- no-tune / overfit governance.
- Market Positioning theory.
- important edge-case precedent.
- incident postmortems and prevention rules.

Each knowledge asset must carry authority label such as ACCEPTED, WORKING, HYPOTHESIS, or FUTURE_EXTENSION.

## 10. Cross-core continuity

CORE A and CORE B are peer persistent personas.

Each core owns a separate persona manifest and channel lineage, while shared contracts are represented as shared Control assets.

Neither core may overwrite the other core's authority domain through handoff prose.

Shared-contract change requires:

CORE proposal / decision -> peer reconciliation -> versioned Control event -> implementation -> independent validation where required -> promotion.

## 11. Failure recovery

If a channel disappears before clean rotation:

1. Load latest immutable checkpoint.
2. Compare checkpoint Git SHA against repository HEAD and Event Ledger tail.
3. Recover post-checkpoint deltas from durable Control assets first.
4. Treat chat history and sandbox references as secondary forensic evidence only.
5. Mark missing artifact bytes UNLOCATED, not LOST, until recovery space is reasonably exhausted.
6. Never reconstruct historical bytes while operating in recovery mode.

## 12. Freeze gate for Continuity v1

Continuity v1 is not freeze-eligible until:

- CORE A successor recovery drill passes.
- CORE B successor recovery drill passes.
- Dual-core authority matrix is reconciled by both cores.
- Shared asset ownership is explicit.
- Artifact Persistence Protocol is operationally tested.
- Channel rotation gate is executed successfully at least once under the new protocol.
- No critical project state depends solely on chat history or ephemeral runtime.

## 13. Current status

This protocol is a CORE A working draft.
It becomes a v1 freeze candidate only after CORE B successor reconciliation and continuity recovery drill.