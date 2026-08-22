# M3Top3 Owner Review Receipt — Item 37

PROJECT = AAA
PRODUCT = ASSET AGENT ASA
PERSONA = AAA-ASA
DATE = 2026-08-22
ITEM = 37
STATE = OWNER_PASS
AUTHORITY_SOT = FALSE

## OWNER DISPOSITION
Owner passed the modified shared MEMORY/WORKLOG race-prevention and Persona memory-consolidation design.

## PRESERVED DECISION
- Parallel Persona Agent Threads do not directly and concurrently write shared Persona `MEMORY.md` or `WORKLOG.md`; each Thread writes only its own unique append-only Run Journal during execution.
- Thread Return Packets / material Checkpoints may submit `DURABLE_MEMORY_CANDIDATES` containing target Persona, class, importance, proposed durable memory, exact source ref, valid-from state and supersession information where applicable.
- Preserve three distinct persistence layers: Thread Run Journal = high-detail execution ledger; Persona WORKLOG = chronological material execution history; Persona MEMORY = compact current durable continuity state.
- PMO coordinates/schedules consolidation and routes memory candidates, but does not unilaterally rewrite another Persona's durable semantic memory.
- Each Persona owns a serialized single-writer consolidation path for its own MEMORY/WORKLOG.
- `COMMON/PROJECT_MEMORY.md` has a higher admission threshold and is reserved for cross-Persona/global operating rules, global state, P0 blockers, organization/authority/runtime continuity, and other information every current Persona must know.
- Memory should summarize and point to exact evidence/decision refs rather than duplicating large artifacts; Memory/Worklog never replaces governed authority or evidence.
- Conflicting memory candidates remain explicit as unresolved conflicts with source refs; consolidation does not silently choose a winner. Only the affected path is held when the conflict prevents safe authority/input resolution.
- Consolidation triggers include Thread return, material checkpoint, Work Packet closure, Work Process Bundle closure, material Owner directive/correction, channel/runtime succession, and material blocker creation/resolution.
- At Work Process Bundle closure, perform final Persona-memory consolidation before the next Owner+ASA planning cycle so successor channels/runs can reconstruct current state without replaying chat history.
- Persona currentization proposal shall include: Thread Personas submit memory candidates rather than racing shared files; PMO schedules/routes consolidation; each Persona retains single-writer durable-memory ownership; ASA supervises cross-Persona/common-memory consolidation; PMOV may audit whether material execution decisions/findings disappeared during consolidation.

## DOCUMENT REVISION RULE
Carry this disposition into the single consolidated successor revision after the itemized Owner review is complete.
