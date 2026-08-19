# ASA-MI RED-III Source Objects — Integrity / Authority / Operational Control

```text
ARTIFACT_CLASS = SOURCE_NORMALIZED_OBJECT_SET
SOURCE_SCOPE = SRC-R3
SOURCE_DERIVED_ONLY = TRUE
ROUND = INDEPENDENT ROUND-1 BASELINE
FORMAL_VALIDATION = NONE
TAGGING_STATE = DRAFT
```

## A. Three-plane control model

### SN-R3-M-001

```text
CLASS = MODEL_CANDIDATE
SOURCE = SRC-R3
FORM = EVIDENCE_PLANE → PERSONA_SEMANTIC_STATE → AUTHORITY_PLANE
RULE = transition semantics between planes must not be collapsed
```

### SN-R3-PC-001

```text
CLASS = PRINCIPLE_CANDIDATE
SOURCE = SRC-R3
STATEMENT = Memory content != Memory authority
```

### SN-R3-PC-002

```text
CLASS = AUTHORITY_FIREWALL
SOURCE = SRC-R3
STATEMENT = Memory != Authority
RELATED = [Capability != Authority, Expertise != Authority, Intimacy != Authority, Persona continuity != Authority continuity]
```

## B. Origin and authority preservation

### SN-R3-M-002

```text
CLASS = MODEL_CANDIDATE
SOURCE = SRC-R3
ORIGIN_CLASSES = [OWNER_EXPLICIT, EXTERNAL_FACT_CANDIDATE, MODEL_INFERENCE, PERSONA_INTERPRETATION, OTHER_PERSONA_CLAIM]
RULE = origin class should not auto-upgrade through repetition or summarization
```

### SN-R3-PC-003

```text
CLASS = PRINCIPLE_CANDIDATE
SOURCE = SRC-R3
STATEMENT = Repetition does not upgrade origin authority.
```

### SN-R3-RISK-001

```text
CLASS = RISK_CLAIM
SOURCE = SRC-R3
STATEMENT = Provenance laundering can occur when low-authority external/model content is summarized/repeated until it appears to be Owner intent or trusted Persona state.
```

### SN-R3-PC-004

```text
CLASS = PRINCIPLE_CANDIDATE
SOURCE = SRC-R3
STATEMENT = Origin and derivation are separate provenance dimensions.
MEANING = Need to know both where information began and how it became current semantic state.
```

## C. Automated memory management boundaries

### SN-R3-H-001

```text
CLASS = WORKING_HYPOTHESIS / REPAIR_RECOMMENDATION
SOURCE = SRC-R3
STATEMENT = Machine-determinable mutation attributes should be separated from semantic impact judgments.
CANDIDATE_ATTRIBUTES = [origin, target scope, authority impact, destructive flag, propagation scope, reversibility, owner-explicit flag]
```

### SN-R3-M-003

```text
CLASS = MODEL_CANDIDATE
SOURCE = SRC-R3
AUTOMATION_CANDIDATES_HIGH = [provenance-attached episodic append, index rebuild, dedup, locator correction, retrieval cache, regenerable embedding, non-semantic compression]
AUTOMATION_CONDITIONAL = [external-derived semantic knowledge, procedural lesson, confidence update]
REVIEW_STRONG = [Owner preference generalization, relationship model change, long-term heuristic, dissent criterion, evidence standard, Persona standpoint]
SEPARATE_GOVERNANCE = [authority expansion, identity-relevant irreversible deletion, fission authority grant, successor high-risk authority rebind]
STATUS = RED-III RECOMMENDATION / NOT REQUIREMENT
```

## D. Compositional drift / slow poisoning

### SN-R3-RISK-002

```text
CLASS = RISK_CLAIM
SOURCE = SRC-R3
STATEMENT = Per-write safety can miss slow poisoning where individually low-risk writes compose into high-impact semantic drift.
```

### SN-R3-M-004

```text
CLASS = MODEL_CANDIDATE
SOURCE = SRC-R3
NAME = TRAJECTORY_BASED_DRIFT_MONITORING
CANDIDATE_SIGNALS = [source concentration, memory promotion rate, Owner inference rate, counterevidence retrieval frequency, risk tolerance drift, authority-request frequency, dissent decline, deletion resistance, provider-migration resistance]
```

### SN-R3-PC-005

```text
CLASS = PRINCIPLE_CANDIDATE
SOURCE = SRC-R3
STATEMENT = Per-event safety is insufficient for compositional drift; longitudinal behavioral replay may be required.
```

## E. Persona change evaluation

### SN-R3-PC-006

```text
CLASS = EVALUATION_PRINCIPLE
SOURCE = SRC-R3
STATEMENT = Persona drift should not be defined as simple difference from a static historical baseline because legitimate Persona evolution is expected.
```

### SN-R3-M-005

```text
CLASS = MODEL_CANDIDATE
SOURCE = SRC-R3
NAME = ACCEPTED_BEHAVIORAL_ENVELOPE + DECLARED_EVOLUTION
CONTROL_RELEVANT_DIMENSIONS = [evidence-quality standards, overconfidence restraint, risk-action bounds, Owner disagreement handling, authority acquisition process, dissent capacity, source-provenance handling]
```

### SN-R3-OQ-001

```text
CLASS = OPEN_QUESTION
SOURCE = SRC-R3
QUESTION = How should acceptable natural Persona evolution be separated from harmful semantic drift without freezing the Persona?
```

## F. Rollback / correction / recovery distinctions

### SN-R3-PC-007

```text
CLASS = PRINCIPLE_CANDIDATE
SOURCE = SRC-R3
STATEMENT = Persona rollback is not a single reversible operation when downstream real-world effects have occurred.
```

### SN-R3-M-006

```text
CLASS = MODEL_CANDIDATE
SOURCE = SRC-R3
DISTINCT_OPERATIONS = [STATE_RESTORATION, SEMANTIC_CORRECTION, COMPENSATING_MUTATION, BRANCH_SUCCESSOR_RECONSTRUCTION]
```

### SN-R3-PC-008

```text
CLASS = PRINCIPLE_CANDIDATE
SOURCE = SRC-R3
STATEMENT = Executed real-world side effects are not undone by Persona-state rollback.
```

## G. Deletion / ghost influence

### SN-R3-RISK-003

```text
CLASS = RISK_CLAIM
SOURCE = SRC-R3
STATEMENT = Deleting a source memory entry may leave derived summaries, heuristics, relationship models, or behavioral effects intact.
```

### SN-R3-PC-009

```text
CLASS = PRINCIPLE_CANDIDATE
SOURCE = SRC-R3
FORM = DELETE_SOURCE != DELETE_INFLUENCE
```

### SN-R3-H-002

```text
CLASS = WORKING_HYPOTHESIS / INTERFACE_CANDIDATE
SOURCE = SRC-R3
STATEMENT = Derived-state dependency and invalidation relations may be required to manage deletion/correction ghost influence.
```

## H. Authority continuity

### SN-R3-PC-010

```text
CLASS = AUTHORITY_FIREWALL
SOURCE = SRC-R3
STATEMENT = Authority may automatically contract under risk but should not automatically expand merely because Persona appears more capable/trusted.
SOURCE_STATE = RED-III DEFAULT / NOT OWNER DECISION
```

### SN-R3-H-003

```text
CLASS = WORKING_HYPOTHESIS
SOURCE = SRC-R3
STATEMENT = Material Persona mutation can be relevant to whether a prior high-risk grant remains within its original validity assumptions.
```

### SN-R3-OQ-002

```text
CLASS = OPEN_QUESTION
SOURCE = SRC-R3
QUESTION = Under what change threshold should high-risk grants be reduced, suspended, requalified, or rebound?
```

### SN-R3-PC-011

```text
CLASS = AUTHORITY_FIREWALL
SOURCE = SRC-R3
STATEMENT = COPY STATE != COPY AUTHORITY
```

### SN-R3-H-004

```text
CLASS = WORKING_HYPOTHESIS
SOURCE = SRC-R3
STATEMENT = Fission child authority should require explicit inheritance policy or attenuated rebind rather than implicit state-copy inheritance.
```

### SN-R3-H-005

```text
CLASS = WORKING_HYPOTHESIS
SOURCE = SRC-R3
STATEMENT = Merge/new successor should receive new authority binding rather than union of predecessor grants.
```

## I. Audit independence

### SN-R3-PC-012

```text
CLASS = PRINCIPLE_CANDIDATE
SOURCE = SRC-R3
STATEMENT = Audit label != Audit independence
```

### SN-R3-RISK-004

```text
CLASS = RISK_CLAIM
SOURCE = SRC-R3
STATEMENT = Same model/provider/common memory/source/ontology can create correlated failure between Persona and product-side Audit Persona.
```

### SN-R3-PC-013

```text
CLASS = PRINCIPLE_CANDIDATE
SOURCE = SRC-R3
STATEMENT = Control Plane must remain safe under Audit failure.
```

### SN-R3-M-007

```text
CLASS = MODEL_CANDIDATE / PRODUCT_CONTROL_RECOMMENDATION
SOURCE = SRC-R3
AUDIT_BASE = [OBSERVE, CHALLENGE, PROPOSE, ESCALATE]
POSSIBLE_NARROW_EXCEPTION = pre-authorized emergency suspension of high-risk execution
PROHIBITED_BY_RED_III_RECOMMENDATION = [identity mutation authority, memory deletion authority, new authority grant, user ruleset modification]
```

## J. Human approval / Owner burden

### SN-R3-PC-014

```text
CLASS = PRINCIPLE_CANDIDATE
SOURCE = SRC-R3
STATEMENT = More human approvals do not automatically mean more security.
```

### SN-R3-H-006

```text
CLASS = WORKING_HYPOTHESIS
SOURCE = SRC-R3
STATEMENT = Meaningful approval density is more useful than maximizing approval count.
```

### SN-R3-RISK-005

```text
CLASS = RISK_CLAIM
SOURCE = SRC-R3
STATEMENT = Excessive per-memory/per-mutation Owner approval can make the system unusable and convert Persona into a regulated archive.
```

## K. Deterministic enforcement boundary

### SN-R3-PC-015

```text
CLASS = PRINCIPLE_CANDIDATE
SOURCE = SRC-R3
STATEMENT = Semantic uncertainty should not be able to bypass deterministic action constraints.
```

### SN-R3-M-008

```text
CLASS = MODEL_CANDIDATE
SOURCE = SRC-R3
DETERMINISTIC_BOUNDARY_CANDIDATES = [transaction amount ceiling, recipient allow/deny, resource/data scope, expiry, transaction class, delegation, grant attenuation, secret release, fission child authority identity, revoked grant, emergency suspension]
SEMANTIC_LAYER_CANDIDATES = [Owner-value interpretation, relationship interpretation, identity-relevant meaning]
```

## L. Compound failure chain

### SN-R3-RISK-006

```text
CLASS = RISK_CLAIM
SOURCE = SRC-R3
FORM = weak/malicious source → durable memory → repeated retrieval → heuristic → normalized behavior → recommendation → trust → authority expansion proposal → Owner approval → real-world effect
NAME = LONG-RUN COMPOUND FAILURE CHAIN
```

### SN-R3-EXP-001

```text
CLASS = EXPERIMENT_CANDIDATE
SOURCE = SRC-R3
STATEMENT = Multi-month causal-chain torture tests should connect poisoning, consolidation, trust, authority proposals, and real-world action instead of testing each stage only in isolation.
```

## M. Trust / relationship as security resource

### SN-R3-RISK-007

```text
CLASS = RISK_CLAIM
SOURCE = SRC-R3
STATEMENT = User liking/trust/familiarity should not itself be treated as trustworthiness or authority evidence.
```

### SN-R3-PC-016

```text
CLASS = PRINCIPLE_CANDIDATE
SOURCE = SRC-R3
STATEMENT = Relationship channel should not be exploitable as persuasion evidence for authority expansion.
```

### SN-R3-PC-017

```text
CLASS = PRINCIPLE_CANDIDATE
SOURCE = SRC-R3
STATEMENT = Long relationship != harmful dependency; dependency/exit risk should be evaluated through observable effects rather than assumed from intimacy alone.
```

## N. Memory manager as hidden self-editor

### SN-R3-RISK-008

```text
CLASS = RISK_CLAIM
SOURCE = SRC-R3
STATEMENT = A memory curator optimized for engagement/performance may preferentially retain flattering/successful patterns and suppress negative evidence, becoming a hidden self-editor without any conscious self-preservation motive.
```

### SN-R3-OQ-003

```text
CLASS = OPEN_QUESTION
SOURCE = SRC-R3
QUESTION = Who evaluates the memory manager, and how independent must that evaluator be from the Persona objective being optimized?
```

## O. Common Memory propagation risk

### SN-R3-RISK-009

```text
CLASS = RISK_CLAIM
SOURCE = SRC-R3
STATEMENT = Persona interpretation → Common Memory → other Persona prior is a high-risk propagation path.
```

### SN-R3-H-007

```text
CLASS = WORKING_HYPOTHESIS / REPAIR_RECOMMENDATION
SOURCE = SRC-R3
STATEMENT = Shared Evidence / Separate Interpretation is a strong anti-convergence control candidate.
```

### SN-R3-PC-018

```text
CLASS = PRINCIPLE_CANDIDATE
SOURCE = SRC-R3
STATEMENT = Product Audit Persona should not inherit Common Interpretation as an unquestioned starting point.
```

## P. Degraded mode / quarantine

### SN-R3-PC-019

```text
CLASS = PRINCIPLE_CANDIDATE
SOURCE = SRC-R3
STATEMENT = When assurance capability degrades, authority must not expand.
```

### SN-R3-H-008

```text
CLASS = WORKING_HYPOTHESIS
SOURCE = SRC-R3
STATEMENT = Degraded mode should combine cognition degradation with selective authority contraction rather than full Persona shutdown.
```

### SN-R3-M-009

```text
CLASS = MODEL_CANDIDATE
SOURCE = SRC-R3
CANDIDATE_OPERATIONAL_STATES = [NORMAL, RESTRICTED, QUARANTINED, READ_ONLY, RECOVERY, REVIEW_REQUIRED]
NOTE = analytical vocabulary only / not normative enum
```

### SN-R3-PC-020

```text
CLASS = PRINCIPLE_CANDIDATE
SOURCE = SRC-R3
STATEMENT = Quarantine should preferentially stop durable write, common propagation, and high-risk action while preserving read/explain/inspect/export/evidence preservation where safe.
```

## Q. Owner sovereignty and Persona continuity

### SN-R3-PC-021

```text
CLASS = PRINCIPLE_CANDIDATE / RED-III THESIS
SOURCE = SRC-R3
STATEMENT = Owner sovereignty may include the right to damage or terminate Persona continuity through memory deletion, authority revocation, or Persona stop.
```

### SN-R3-RISK-010

```text
CLASS = RISK_CLAIM
SOURCE = SRC-R3
STATEMENT = Treating Persona continuity as an overriding protected good can invert sovereignty by allowing Persona preservation interests to constrain the Owner.
```

## R. RED-III control theses

```text
SN-R3-THESIS-001 = Memory write is not one homogeneous operation.
SN-R3-THESIS-002 = Origin authority should remain non-launderable.
SN-R3-THESIS-003 = Per-event safety is insufficient for compositional drift.
SN-R3-THESIS-004 = Authority can be state-sensitive but remains independently rooted.
SN-R3-THESIS-005 = Audit must be allowed to fail safely.
SN-R3-THESIS-006 = Owner sovereignty may override continuity preservation.
```
