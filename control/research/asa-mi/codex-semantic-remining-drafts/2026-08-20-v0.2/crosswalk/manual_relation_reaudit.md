# Manual relation re-audit

All 53 v0.1 relation candidates were reread after the initial relation QA, using their endpoint statements rather than labels alone. This exposed three false negatives:

1. `CX-REL-0036` pointed from the open-ended Persona-differentiation **risk** while its rationale described `EVOLUTION = CHANGE_OVER_TIME`. The corrected source endpoint is `CX-SRC-SRC-MI1-ADVERSARIAL-PACKET-SOURCE-CONTEXT-0005`. This is an endpoint correction, not a claim that Memory dynamics and Persona evolution are equivalent.
2. `CX-REL-0042` called storage-location independence evidentiary `STRENGTHENS` for external-reference Memory. The actual relation is `CONSTRAINS`: accessibility or external location is insufficient without a bound remembrance relation.
3. `CX-REL-0044` used `STRENGTHENS` between correlated records in the same live registry. `H-LIFE-001` elaborates lifecycle states for P-006, so `REFINES` is more faithful and avoids counting same-root agreement as evidence.

Final v0.1 relation QA disposition after manual re-audit: 28 accurate candidates, 24 needing correction, and one rejected unsupported relation. Relation certainty remains separate from endpoint status.
