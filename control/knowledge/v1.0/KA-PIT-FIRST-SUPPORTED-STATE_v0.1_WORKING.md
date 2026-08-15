# KA-PIT-FIRST-SUPPORTED-STATE

Version: v0.1_WORKING  
Authority: ACCEPTED_CORE_A_DOCTRINE / FREEZE_PENDING  
Primary Owner: SEMI-CONTROL-ARCHITECT  
Project: semiconductor-research

## 1. Core distinction

FACT_EXISTED_AT_TIME != PUBLIC_EVIDENCE_AVAILABLE_AT_TIME.

A fact may have been economically true before a cutoff, but PIT certification requires evidence that was publicly available, attributable, and usable by that cutoff under the applicable source/provenance rules.

Later evidence proving that a fact existed earlier does not automatically certify earlier PIT windows.

## 2. First-supported-state rule

For a state S:

1. Find the earliest supported point at which the required content, entity binding, publication timing, and provenance conditions are satisfied.
2. Do not project S backward before that support point.
3. Forward reuse is allowed only while the evidence and effective-history rules support continuity.
4. A supported change point closes prior-state reuse.
5. Absence of a discovered change is not proof of eternal continuity.

## 3. Open interval semantics

An open effective interval means:

NO_SUPPORTED_CHANGE_THROUGH_LAST_AUDITED_CUTOFF.

It does not mean:

STATE_VALID_FOREVER.

Future audits may discover a later change point.

## 4. Separate state axes

The following must remain distinct:

- Evidence State
- Content State
- Provenance State
- Publication / PIT State
- Entity State
- Source Role
- Source Family
- Temporal Use
- Exhaustion State
- Control Adjudication State
- Promotion State
- Artifact State

Examples:

CONTENT_VERIFIED != PROVENANCE_RESOLVED.

RESEARCH_ACCEPTED != CONTROL_PROMOTED.

ARTIFACT_REFERENCE != AUTHORITY.

## 5. Source temporal use

A source can support a window only if its publication/use timing meets the PIT rule for that window.

Retrospective sources may be useful for:

- legal identity confirmation;
- listing history;
- forensic provenance reconstruction;
- proving a later state;

but may not be backfilled into an earlier Historical_BP window unless the required evidence was publicly available by that earlier cutoff.

## 6. Effective-history reuse

Forward reuse requires all of:

- same bound entity;
- state semantics unchanged;
- no supported change point before the reused window;
- source role allows temporal reuse;
- provenance/publication requirements remain satisfied.

A later source may corroborate continuity but cannot erase the need for the original first-supported point.

## 7. Unresolved is legitimate

UNRESOLVED is a valid epistemic/control state.

UNRESOLVED != FALSE.
UNRESOLVED != ZERO.
UNRESOLVED != EMPTY.
UNRESOLVED != MISSING_BY_DEFAULT.

A bounded unresolved state is preferable to fabricated certainty.

## 8. Exhaustion

Exhaustion records whether the allowed source/search space has been reasonably tested for a specific question.

Exhaustion does not transform unsupported content into false content.

A control decision may legitimately retain UNRESOLVED after reasonable exhaustion.

## 9. Promotion path

Research returns a recommendation with evidence and uncertainty.

CORE A adjudicates:

- scope;
- evidence;
- cutoff;
- entity;
- provenance;
- arithmetic;
- forbidden outcomes/leakage;
- firewall compliance;
- research result versus promotion state.

Allowed decisions:

- ACCEPT
- PARTIAL_ACCEPT
- REJECT
- REQUEST_NARROW_FOLLOWUP

Research-local PASS cannot self-promote to Project PASS.

## 10. Outcome firewall

Historical Ground Truth adjudication must not use future performance outcomes such as:

- future return;
- future MFE;
- future rank;
- later model success/failure;

to decide whether an earlier PIT fact was true or supported.

## 11. Reconstruction rule

When recovering lost lineage, later aggregate/control states can verify arithmetic consistency but must not be used to invent missing cell-level PIT evidence, provenance, publication dates, or state-before values.

UNKNOWN must remain UNKNOWN until source-supported.

## 12. Freeze note

This doctrine reflects the accepted CORE A operating semantics currently used in U127/PIT control. The file is working-form materialization pending formal knowledge-asset registry binding and Continuity v1 freeze.