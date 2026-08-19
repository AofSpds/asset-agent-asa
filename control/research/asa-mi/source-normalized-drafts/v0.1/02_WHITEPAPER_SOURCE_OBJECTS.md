# PCS-SHAI Source Objects Relevant to ASA-MI

```text
ARTIFACT_CLASS = SOURCE_NORMALIZED_OBJECT_SET
SOURCE_SCOPE = SRC-WP1 + SRC-WP2
SOURCE_DERIVED_ONLY = TRUE
CURRENT_OWNER_POSITION = NOT_INFERRED
TAGGING_STATE = DRAFT
```

## A. Reality / epistemic grounding

### SN-WP2-PC-001

```text
CLASS = PRINCIPLE_CANDIDATE
SOURCE = SRC-WP2
STATEMENT = Reality > Current Interpretation > Implementation Hypothesis > Protocol Commitment
MEANING = Current models and protocols remain subordinate to observed reality.
DOES_NOT_ASSERT = A FINAL THEORY OF REALITY
```

### SN-WP2-PC-002

```text
CLASS = PRINCIPLE_CANDIDATE
SOURCE = SRC-WP2
STATEMENT = UNKNOWN != FALSE
RELATED = [UNCLASSIFIED != INVALID, DISPUTED != ERROR]
IMPLICATION_FOR_MEMORY = uncertain/conflicting/partially supported memory states must remain representable
```

### SN-WP2-PC-003

```text
CLASS = PRINCIPLE_CANDIDATE
SOURCE = SRC-WP2
STATEMENT = Model of the Human != Prescription for the Human
IMPLICATION = A technical Persona representation must not be promoted into a universal ontology of human identity.
```

## B. Persona / model / compute separation

### SN-WP1-PC-001

```text
CLASS = PRINCIPLE_CANDIDATE
SOURCE = SRC-WP1
STATEMENT = Persona != Model
IMPLICATION = Foundation model replacement must not automatically imply Persona destruction.
```

### SN-WP1-PC-002

```text
CLASS = PRINCIPLE_CANDIDATE
SOURCE = SRC-WP1
STATEMENT = Compute != Governance
IMPLICATION = Better reasoning capability does not itself grant governance or authority.
```

### SN-WP1-PC-003

```text
CLASS = PRINCIPLE_CANDIDATE
SOURCE = SRC-WP1
STATEMENT = Provider Replacement Must Be Possible
STATUS_NOTE = source-level architecture invariant candidate / later v0.2 framing may refine scope
```

### SN-WP1-PC-004

```text
CLASS = AUTHORITY_FIREWALL
SOURCE = SRC-WP1
STATEMENT = Copy(Persona State) != Copy(Authority)
```

### SN-WP1-PC-005

```text
CLASS = AUTHORITY_FIREWALL
SOURCE = SRC-WP1
STATEMENT = Authority Cannot Self-Escalate
SOURCE_SCOPE_NOTE = subject to later governance-profile interpretation; not promoted here
```

## C. Self / Boundary / relation semantics

### SN-WP2-PC-004

```text
CLASS = PRINCIPLE_CANDIDATE
SOURCE = SRC-WP2
STATEMENT = Observed Integration != System Interpretation != User-Defined Self Status
```

### SN-WP2-M-001

```text
CLASS = MODEL_CANDIDATE
SOURCE = SRC-WP2
STATEMENT = Boundary may be modeled as Governed Relational Status
FORM = BOUNDARY ?= GOVERNED_RELATIONAL_STATUS
STATE = STRONG_SOURCE_DIRECTION / NOT UNIVERSAL FACT
```

### SN-WP2-PC-005

```text
CLASS = AUTHORITY_FIREWALL
SOURCE = SRC-WP2
STATEMENT = Self Membership != Authority
```

### SN-WP2-PC-006

```text
CLASS = PRINCIPLE_CANDIDATE
SOURCE = SRC-WP2
STATEMENT = Protocol standardizes definability, not the definition
IMPLICATION = Protocol should enable people to define/change relational statuses without prescribing their metaphysical meaning.
```

## D. History / meaning / evolution

### SN-WP2-PC-007

```text
CLASS = PRINCIPLE_CANDIDATE
SOURCE = SRC-WP2
STATEMENT = History may be immutable; meaning may evolve
IMPLICATION_FOR_ASA_MI = historical event/evidence integrity can coexist with changing interpretation, salience, relation, and status
```

### SN-WP2-H-001

```text
CLASS = WORKING_HYPOTHESIS
SOURCE = SRC-WP2
STATEMENT = Functional integration may be a useful observation axis for plural cognition
MEASUREMENT = OPEN
DOES_NOT_ASSERT = HIGH_INTEGRATION_IMPLIES_SELF_MEMBERSHIP
```

### SN-WP2-PC-008

```text
CLASS = PRINCIPLE_CANDIDATE
SOURCE = SRC-WP2
STATEMENT = Persona Evolution is broader than model update
CANDIDATE_COMPONENTS = [history accumulation, memory change, relationship change, role specialization, capability change, Person interpretation change, status transition]
```

### SN-WP2-PC-009

```text
CLASS = PRINCIPLE_CANDIDATE
SOURCE = SRC-WP2
STATEMENT = EVOLUTION != GROWTH
MEANING = Growth is a positively evaluated subset of change; change can also be harmful drift, poisoning, corruption, rigidity, or complexity.
```

## E. Persona State / Memory relationship

### SN-WP1-M-001

```text
CLASS = MODEL_CANDIDATE
SOURCE = SRC-WP1
STATEMENT = Persona State is not a memory dump
CANDIDATE_SEPARATION = [Identity/Manifest, relationships, episodic memory, evidence-linked beliefs, preferences/heuristics, standpoint, policy bindings, lineage, provider bindings, validation history]
```

### SN-WP1-OQ-001

```text
CLASS = OPEN_QUESTION
SOURCE = SRC-WP1 + SRC-MI0
QUESTION = Which Persona-state components are memory, metadata about memory, governance state, authority, or identity manifestations?
```

### SN-WP1-M-002

```text
CLASS = MODEL_CANDIDATE
SOURCE = SRC-WP1
STATEMENT = Persona lifecycle and Memory lifecycle are distinct lifecycle domains
PERSONA_EVENT_CANDIDATES = [CREATE_CANDIDATE, ADMIT/RECOGNIZE, GRANT, ACTIVATE, EVOLVE, FORK/CLONE, RETIRE, RECOVER/SUCCESSOR]
```

## F. Memory promotion / semantic mutation

### SN-WP1-M-003

```text
CLASS = MODEL_CANDIDATE
SOURCE = SRC-WP1
STATEMENT = External Event / User Input / Tool Result → Evidence Capture → FACT/INTERPRETATION separation → Memory Candidate → State/Risk class → Write Gate → Persona State Mutation Receipt
STATUS = WORKING_SOURCE_DIRECTION
```

### SN-WP1-PC-006

```text
CLASS = PRINCIPLE_CANDIDATE
SOURCE = SRC-WP1
STATEMENT = No Silent Semantic Mutation
ASA_MI_RELEVANCE = persistent memory or derived Persona state must not silently rewrite high-impact meaning
```

### SN-WP1-RISK-001

```text
CLASS = RISK_CLAIM
SOURCE = SRC-WP1
STATEMENT = Persistent memory is an attack surface
EXAMPLES = external text silently becoming preference / identity / standpoint / Owner intent
```

## G. Sovereignty / optionality / irreversibility

### SN-WP2-H-002

```text
CLASS = WORKING_HYPOTHESIS
SOURCE = SRC-WP2
STATEMENT = Loss of meaningful change/replacement/fork/recovery/reconfiguration/exit options may reduce long-run survivability
```

### SN-WP2-PC-010

```text
CLASS = PRINCIPLE_CANDIDATE
SOURCE = SRC-WP2
STATEMENT = Chosen Commitment != Captured Irreversibility
MEANING = Irreversibility is not automatically bad if deliberately chosen under applicable governance.
```

### SN-WP2-RISK-001

```text
CLASS = RISK_CLAIM
SOURCE = SRC-WP2
STATEMENT = PCS-SHAI itself can become a new centralization / protocol-capture / cognitive-monoculture mechanism
```

### SN-WP2-PC-011

```text
CLASS = PRINCIPLE_CANDIDATE
SOURCE = SRC-WP2
STATEMENT = Protocol itself must remain falsifiable
```

## H. INIT semantics

### SN-WP2-PC-012

```text
CLASS = PRINCIPLE_CANDIDATE
SOURCE = SRC-WP2
STATEMENT = INIT is a seed, not a sovereign
IMPLICATION = A useful bootstrap implementation must not silently become a universal Persona/identity theory.
```

### SN-WP2-PC-013

```text
CLASS = PRINCIPLE_CANDIDATE
SOURCE = SRC-WP2
STATEMENT = INIT update != local rule update
IMPLICATION = New defaults should not silently mutate already established Person/Community local semantics.
```

## I. Whitepaper-to-ASA-MI mapping notes

These are **mapping candidates extracted from the source**, not current final conclusions.

```text
SN-WP2-PC-001 SUPPORTS research method: reality-first hypothesis revision
SN-WP2-PC-007 SUPPORTS separation of historical event/evidence from current interpretation
SN-WP1-PC-001 SUPPORTS provider/model replaceability as a design target
SN-WP1-M-001 CONSTRAINS overly broad equation PersonaState = MemoryDump
SN-WP2-PC-004 CONSTRAINS automatic Self inference from integration
SN-WP1-PC-004 SUPPORTS Memory/State and Authority separation
SN-WP2-RISK-001 SUPPORTS anti-convergence / anti-capture falsification
```

## J. Unresolved tensions preserved from source

### SN-WP-CONFLICT-001

```text
TYPE = TENSION
A = Persona State is not a memory dump
B = later Owner/ASA-MI proposition may treat a much broader range of Persona state as Memory
STATUS = UNRESOLVED / REQUIRES MEMORY-SEMANTICS RECONCILIATION
```

### SN-WP-CONFLICT-002

```text
TYPE = TENSION
A = History may require integrity/preservation
B = Persona/Memory must support lifecycle, forgetting, deletion, correction
STATUS = UNRESOLVED / REQUIRES LAYERED DELETE-FORGET-HISTORY MODEL
```

### SN-WP-CONFLICT-003

```text
TYPE = TENSION
A = Provider Replacement Must Be Possible
B = empirical behavioral continuity across models/providers is not established by the Whitepaper
STATUS = DESIGN_INTENT != EMPIRICAL_PROOF
```
