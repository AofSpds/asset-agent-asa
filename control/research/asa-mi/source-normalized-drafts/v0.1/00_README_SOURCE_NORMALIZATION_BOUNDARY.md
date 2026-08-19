# ASA-MI Source-Normalized Drafts v0.1

```text
ARTIFACT_CLASS = SOURCE_DERIVED_RESEARCH_DRAFT_SET
PROJECT = AAA
PRODUCT = ASSET AGENT ASA
WORKSTREAM = ASA-MI
SCOPE = ASA-MI_ONLY
NORMALIZATION_SET_VERSION = v0.1
AUTHORING_STATE = WORKING_SOURCE_NORMALIZATION_DRAFT
NORMATIVE_AUTHORITY = NONE
FROZEN = FALSE
PAIRED_VALIDATION = NOT_PERFORMED
INDEPENDENT_VALIDATION = NOT_PERFORMED
OWNER_FINAL_ACCEPTANCE = FALSE
PRODUCTION_AUTHORIZED = FALSE
SOURCE_DERIVED_ONLY = TRUE
LIVE_BRAINSTORM_IMPORT = PROHIBITED_UNLESS_EXPLICITLY_PRESENT_IN_SOURCE
TAGGING_STATE = DEFERRED_FOR_OWNER_REVIEW
```

## 1. Purpose

This directory is intentionally isolated from the live ASA-MI brainstorming / planning-guidance records.

It exists to normalize **already existing project/source material** into object-like records that can later be tagged, compared, linked, promoted, weakened, superseded, or left unresolved without forcing the Owner to reread long narrative source documents.

The objective is not to rewrite the source, clean up its disagreements, or create a new canonical design.

```text
SOURCE_TEXT
→ SOURCE-FAITHFUL OBJECT EXTRACTION
→ CLASSIFIED DRAFT OBJECTS
→ LATER OWNER TAGGING / REVIEW
```

## 2. Hard separation from live brainstorming

The following are separate research surfaces:

```text
A. LIVE_BRAINSTORM / OWNER-DIALOGUE RECORDS
B. SOURCE-NORMALIZED DRAFTS (THIS DIRECTORY)
```

This directory SHALL NOT silently import later live dialogue merely because it looks compatible with a source claim.

```text
SOURCE_DERIVED_OBJECT != CURRENT_OWNER_POSITION
SOURCE_DERIVED_OBJECT != CURRENT_BEST_HYPOTHESIS
SOURCE_DERIVED_OBJECT != REQUIREMENT
SOURCE_DERIVED_OBJECT != DESIGN CONTRACT
SOURCE_DERIVED_OBJECT != VALIDATION RESULT
```

A source-derived object can later be linked to a live hypothesis or principle, but that is a separate tagging/reconciliation act.

## 3. Extraction classes used in this draft

The class vocabulary is deliberately open. Current draft classes include:

```text
SOURCE_CLAIM
OWNER_PROPOSITION_IN_SOURCE
DESIGN_INTENT_IN_SOURCE
PRINCIPLE_CANDIDATE
WORKING_HYPOTHESIS
COUNTER_HYPOTHESIS
MODEL_CANDIDATE
MAPPING_CANDIDATE
RISK_CLAIM
SURVIVAL_FINDING
REPAIR_RECOMMENDATION
OPEN_QUESTION
FALSIFICATION_TARGET
EXPERIMENT_CANDIDATE
EVALUATION_DIMENSION
AUTHORITY_FIREWALL
SOURCE_STATUS
NON_CLAIM / DOES_NOT_ASSERT
```

Classification is a draft aid, not an ontology commitment.

```text
CLASSIFICATION_ERROR
→ RECLASSIFY
not
→ DELETE_SOURCE_CONTENT
```

## 4. Preservation rule

Source disagreement is preserved.

If Source A says:

```text
Identity = Memory
```

and Source B says:

```text
Identity != Memory
```

this directory records both objects and their conflict relation. It does not synthesize them into a compromise unless a source itself made that synthesis.

## 5. Historical source semantics

Older source statements are not rewritten to match later Owner discussion.

```text
PAST_SOURCE_STATE != CURRENT_RESEARCH_STATE
```

This matters especially for:

- `Identity = Memory` formulations;
- Memory vs Persona State boundaries;
- Common Memory;
- Fission / Merge;
- forgetting vs deletion;
- reconstruction ownership;
- Authority continuity;
- Self / Boundary interpretations.

## 6. Source groups in v0.1

This draft set covers the currently available ASA-MI source cluster:

```text
SRC-WP1   PCS-SHAI Founding Whitepaper v0.1
SRC-WP2   PCS-SHAI v0.2 Revision Original Proposal v0.1
SRC-MI0   ASA-MI activation / continuity packet
SRC-MI1   ASA-MI deep-search synthesis / implementation research output
SRC-R1    ASA-MI RED-I independent state/data-plane attack
SRC-R2    ASA-MI RED-II independent reconstruction/runtime attack
SRC-R3    ASA-MI RED-III independent integrity/authority/control attack
```

The source register provides exact file identifiers where available.

## 7. Draft object identity

Object IDs in this directory are provisional extraction IDs, for example:

```text
SN-WP2-PC-001
SN-MI1-H-004
SN-R1-CH-003
SN-R2-F-006
SN-R3-RISK-011
```

They are **not** canonical AAA stable IDs and should not be referenced as normative objects outside this draft set until the later tagging/reconciliation session.

## 8. What this draft deliberately does not do

```text
NO_OWNER_ACCEPTANCE
NO_REQUIREMENT_PROMOTION
NO_ARCHITECTURE_FREEZE
NO_VALIDATION_PASS
NO_SOURCE_CORRECTION
NO_SYNTHETIC_CONSENSUS
NO_LIVE_BRAINSTORM_MERGE
```

## 9. Expected next human review

The intended next step is an Owner-assisted tagging session that can decide, object by object:

```text
KEEP_AS_SOURCE_ONLY
LINK_TO_CURRENT_HYPOTHESIS
LINK_TO_PRINCIPLE
WEAKEN
SUPERSEDE
ALTERNATIVE_TO
CONTRADICTS
REQUIRES_EXPERIMENT
OUT_OF_SCOPE
NEEDS_SOURCE_CHECK
```

Until then, this directory is a **source-normalized draft corpus**, not a current design baseline.
