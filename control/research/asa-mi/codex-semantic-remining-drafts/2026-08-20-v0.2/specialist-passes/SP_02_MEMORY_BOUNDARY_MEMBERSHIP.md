# SP-02 — Memory definition, membership, and boundary

## Receipt

```text
PASS_ID = SP-02
PASS_PURPOSE = Re-read source candidates for Memory membership without forcing them into Status/Reference or data-only buckets.
START_TIME = 2026-08-20T07:33:09+09:00
END_TIME = 2026-08-20T07:33:17+09:00
ACTIVE_REVIEW_SECONDS = 8
SOURCE_FILES_OPENED = live brainstorm registry; foundational worldview; MI planner source objects; planning guidance
SOURCE_FILE_COUNT = 4
SOURCE_BYTES_CONSIDERED = 60887
RAW_PRIMARY_SOURCE_VERIFICATION = NOT_PERFORMED
```

## Boundary dimensions recovered

The source does not offer one taxonomy. It offers orthogonal dimensions:

- **temporal role:** historical, current, prospective, superseded;
- **representation:** value, event, relation, reference, function, binding, result, self-model, policy;
- **derivation:** observed/source, interpreted, consolidated, derived view, cache;
- **activation:** accessible, retrievable, selected, current-context active;
- **scope:** Owner, project, Persona, workstream, task, fission branch;
- **causal role:** evidence, reconstruction input, disposition, procedure, transition rule;
- **location/binding:** local content, snapshot, external target, locator, environment binding;
- **authority status:** content/origin/semantic state/Authority reference, which must not be collapsed.

`STATUS_MEMORY / REFERENCE_MEMORY` can classify temporal/materialization roles, but cannot replace these axes.

## Membership pressure tests

1. Accessible external data is not automatically Memory; a Persona-specific bound relation may be.
2. A locator can remain stable while target content changes, so reference identity, target identity, and snapshot identity differ.
3. A function can be a runtime capability, acquired procedure, or environment-bound state; only some readings are Persona Memory.
4. A result saved for reuse may become Memory, but preservation alone does not establish Persona membership.
5. A self-model can be Memory, a derived view, or optional representation; self-reference need not be materialized.
6. Retrieval/reconstruction policy can be outside Memory yet causally identity-bearing, or included in a broad functional Memory definition.
7. Model/runtime priors may shape the Persona while remaining unavailable for user-side persistence.
8. Provenance and conflict relations can be metadata about Memory or constitutive semantic state; the source keeps this open.
9. A current standpoint can be a persisted member, derived view, or runtime result.
10. A Memory function that returns or changes its own transition rules creates a recursive boundary case absent from two buckets.

## Candidate membership test (Codex inference, not source position)

A useful research predicate may require independent answers to:

```text
PERSONA_BOUND(X)?
PERSISTED_OR_RECONSTRUCTABLE(X)?
CAUSALLY_AVAILABLE_TO_CURRENT_STATE(X)?
ACQUIRED_OR_ADOPTED_BY_PERSONA(X)?
INTENDED_FOR_FUTURE_RECALL_OR_USE(X)?
SOURCE_OR_DERIVATION_PRESERVED(X)?
```

This is an experimentable membership frame, not an ontology and not an Owner position.

## Relations recovered

1. Accessibility `DOES_NOT_IMPLY` Memory membership.
2. Persona-bound reference `POSSIBLY_CONSTITUTES` Reference Memory.
3. Reference identity `DIFFERS_FROM` target-content identity and snapshot identity.
4. Procedural Memory `POSSIBLY_MAPS_TO` acquired function or binding, not base capability.
5. Current standpoint `POSSIBLY_IN` Status Memory and `POSSIBLY_DERIVED_FROM` Reference Memory.
6. Retrieval policy `ALTERNATIVE_TO` Memory membership as an external co-determinant.
7. Two-bucket Memory `COEXISTS_WITH` orthogonal provenance, scope, activation, and authority axes.

## Double-crux

If two Personas have byte-identical accessible data but only one has a stable Persona-specific relation that causes future recall/use, is the data Memory for both? The answer determines whether membership is content-based, relational, dispositional, or operational.

## Materiality judgment

No source object is added. Ten boundary cases and seven relation candidates constrain the later two-bucket discussion without rejecting it.
