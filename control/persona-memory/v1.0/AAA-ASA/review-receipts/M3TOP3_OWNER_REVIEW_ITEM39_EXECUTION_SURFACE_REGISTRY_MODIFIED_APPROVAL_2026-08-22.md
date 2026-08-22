# M3Top3 Owner Review Receipt — Item 39

PROJECT = AAA
PRODUCT = ASSET AGENT ASA
PERSONA = AAA-ASA
PERSONA_CODE = ASA
DATE = 2026-08-22
ITEM = 39
TITLE = Execution Surface Registry
STATE = OWNER_APPROVED_WITH_MODIFICATION
AUTHORITY_SOT = FALSE

## OWNER DISPOSITION
Owner approved the modified Item 39 proposal after Item 38's record-preservation / curated-continuity separation was established.

## APPROVED DESIGN
- Introduce an `Execution Surface Registry` as a thin current operational projection/index of execution surfaces that are actually active or recently lifecycle-transitioned.
- It is NOT an Authority Registry, semantic SoT, workflow engine, or substitute for Work Packets, Run Journals, Checkpoints, Return Packets, validation receipts, or governed authority artifacts.
- Its purpose is rapid runtime recovery of what execution instances exist, what they are doing, how they are related, and where their durable evidence lives.
- Distinguish three persistence/view layers:
  1. Historical Record = Run Journal / WORKLOG / receipts / checkpoints / immutable evidence preserved as history.
  2. Curated Continuity = current-state recovery view of what a Persona/program must know now.
  3. Execution Surface Registry = current operational view of what channels/threads/audit contexts/worktrees are presently alive or recently transitioned.
- Minimum registry fields should include, as applicable: `SURFACE_ID`, `SURFACE_KIND`, `TARGET_PERSONA`, `CONTROLLER`, `LIFECYCLE_STATE`, `WORK_PACKET_REF`, `AUTHORITY_CAP_REF`, `PARENT_SURFACE`, `JOURNAL_REF`, `CHECKPOINT_REF`, `WORKTREE_REF`, `VALIDATOR_RELATION`, `BLOCKER_STATE`, `NEXT_ROUTE`.
- PMO coordinates and is the default single-writer for the operational registry within an Owner-approved execution plan.
- Threads submit their own lifecycle/checkpoint/return state; PMO updates the operational projection from those durable inputs.
- PMOV may audit omission, stale state, suppression, or distortion of material execution-surface state.
- ASA supervises program-level coherence and Owner-facing escalation, but does not become the day-to-day registry operator.
- Registry lifecycle should support at least `OPEN / RUNNING / BLOCKED / RETURNED / CLOSED / HISTORICAL / SUPERSEDED / ABORTED` where applicable.
- Closing a surface removes it from the active operational view only; its durable historical evidence remains preserved and addressable by exact refs.
- Persona != Thread != Channel != Worktree remains preserved; the Registry records relations among them but does not collapse their identities.

## DOCUMENT REVISION RULE
Carry this disposition into the single consolidated successor revision after the itemized Owner review is complete. Do not regenerate the advisory DOCX files item-by-item.
