# KA-U127-CONTINUITY-INCIDENT

Version: v0.1_WORKING  
Authority: WORKING_HIGH_CONFIDENCE_MULTI_FACTOR_INCIDENT  
Primary Owner: SEMI-CONTROL-ARCHITECT  
Project: semiconductor-research

## 1. Incident summary

U127 logical Ground Truth progressed beyond the last byte-verified historical workbook while artifact version labels, Research state, Control state, and transient FILE_OUTPUT references became conflated.

The result was a successor continuity gap: accepted logical state survived, but later workbook byte lineage did not survive as a clean persistent artifact chain.

## 2. Known anchor

Highest byte-verified historical workbook currently recovered:

- File: U127_Data_Expansion_Working_v0.7_2026-08-15.xlsx
- Byte size: 550774
- SHA256: 1fc47fd131479e6ebb4375206853f39a730610d8b9f29160c33aa292881ad50a
- Authority: HISTORICAL_LEVEL_3_FORENSIC_ANCHOR
- Final Ground Truth authority: NO

v0.7 state:

- Certified: 353 / 1016
- Populated: 370 / 1016
- Complete histories: 44 / 127
- Listing coverage: 58 / 127

Final accepted logical state:

- READY: 1013
- UNRESOLVED: 3
- ADJUDICATED: 1016 / 1016
- Complete histories: 125 / 127
- U127_FROZEN: NO
- Physical artifact freeze: BLOCKED

## 3. Materialization boundary

Current forensic classification indicates:

- v0.8 / v0.9 / v1.1: logical-only on present evidence.
- v1.0 / v1.2-v1.7: FILE_OUTPUT-reference-only on present evidence.
- v1.8: materialization conflict.
- v1.9: physical creation strongly supported, but bytes unrecovered and artifact forensic-only due Control-rejected Zenics W1 provisional promotion.

Logical progression first outruns provable physical artifact progression at v0.8.

## 4. Effective post-v0.7 system of record

Current Control adjudication:

POST_v0_7_EFFECTIVE_SYSTEM_OF_RECORD = MIXED_CONTROL_LOGICAL_STATE_DOMINANT.

The actual mechanism included combinations of:

- Research RETURN packets;
- Control adjudication;
- logical working baselines;
- occasional/reported workbook outputs;
- later rounds proceeding without authoritative parent bytes.

This means the accepted logical state does not depend on recovery of v1.8/v1.9 bytes for its logical validity, although final machine-artifact materialization remains blocked.

## 5. Confirmed failure mechanisms

### A. Logical state outran physical artifact state

At least RC4.5 has a preserved execution in which parent bytes were unavailable, physical write was not executed, but a logical Control baseline advanced.

### B. Version namespace collision

Research state version, Control state version, working workbook target, and artifact output filename used overlapping version labels.

A label such as v1.8 therefore did not uniquely mean a verified workbook byte identity.

### C. Transient sandbox dependence

FILE_OUTPUT and sandbox references survived as text even where bytes did not survive successor rotation.

### D. Persistent artifact registry failure

Important later output references were not paired with verified persistent locators and SHA256 identities before the workflow relied on their existence or version meaning.

### E. Persona/channel continuity failure

Too much operational authority and application-state context remained channel-local. Successor runtime did not automatically inherit predecessor artifact custody or hidden working state.

Control assessment:

PERSONA_CHANNEL_CONTINUITY_BREAK_ROLE = MAJOR_CONTRIBUTING_FACTOR.

It is not certified as the sole root cause.

## 6. Owner operational evidence

Project Owner reports that normally delivered XLSX artifacts would ordinarily have been received/retained. This supports the hypothesis that much of the later U127 progression was carried through a mixed/non-file mechanism rather than a clean sequence of user-delivered Excel versions.

This is OPERATIONAL_PROCESS_EVIDENCE, not proof that no later file ever existed.

## 7. Recovery result so far

Aggregate v0.7 -> v1.3 membership expansion arithmetic is reconciled:

- Certified: 353 -> 974, +621 PASS
- Populated: 370 -> 997, +627 PASS
- Complete histories: 44 -> 119, +75 PASS
- Listing coverage: 58 -> 127, +69 PASS

RC1 through final logical state has strong cell-level lineage recovery.

Largest remaining early deterministic gap:

- membership 46-60 executed result packet/cell payload.

Secondary gap:

- membership 61-75 full per-cell prestate/provenance/listing payload.

Missing fields remain UNKNOWN and are not inferred from aggregate counts.

## 8. Recovery versus reconstruction

RECOVERY != REMATERIALIZATION.

During forensic recovery:

- preserve exact historical bytes;
- do not resave them;
- hash and read-only inspect;
- do not reconstruct missing workbooks from final counts;
- do not infer missing cell values;
- do not make reconstructed bytes masquerade as historical originals.

A future deterministic rematerialization, if authorized after recovery exhaustion, must receive a new identity and explicit reconstructed lineage.

## 9. Prevention controls derived from incident

Mandatory controls:

1. CONTROL_STATE_VERSION_SEPARATE_FROM_ARTIFACT_VERSION.
2. RESEARCH_EVENT_ID_SEPARATE_FROM_CONTROL_PROMOTION_STATE.
3. NO_IMPORTANT_ARTIFACT_WITHOUT_SHA256.
4. NO_CANONICAL_ARTIFACT_WITHOUT_PERSISTENT_LOCATOR.
5. REOPEN/REIMPORT exported bytes before treating output as valid artifact.
6. Parent workbook dependency must reference registered asset_id and verified locator.
7. If no physical parent is required, explicitly identify the logical System of Record.
8. RETURN_PACKET is transport/evidence, not source of truth.
9. Channel rotation requires immutable checkpoint.
10. Successor must load/reconcile checkpoint before normal authority.
11. Important accepted deltas must be represented in typed durable ledger, not only chat history.
12. Unknown historical fields must remain unknown.

## 10. Organizational lesson

The project needs persistent organizational personas rather than channel-based identity.

CORE A and CORE B must be durable peer personas with explicit authority domains, shared-contract rules, separate channel lineages, and checkpoints.

Research, Engineering, Validation, and Recovery are execution/assurance nodes and must not acquire canonical authority simply by performing work.

## 11. Current incident status

INCIDENT_CLASSIFICATION = MULTIPLE.

Components:

- transient sandbox artifact loss;
- some logical states never physically materialized;
- version namespace collision;
- persona/channel continuity break;
- persistent artifact registry failure.

Confidence:

- High that the incident is multi-factor.
- Medium for exact causal ordering.
- Sole root cause not certified.

## 12. Closure criteria

Incident prevention is not considered closed until:

- Persona Persistence Protocol is in force;
- Artifact Persistence Gate is operationally tested;
- CORE A and CORE B authority map is reconciled;
- successor recovery drill passes for both cores;
- important U127 recovery/delta assets are durably registered;
- no critical active workflow depends solely on chat/runtime state.