# RT-05 — Attack Authority separation

## Receipt

```text
PASS_ID = RT-05
PASS_PURPOSE = Find cases where Memory creates de facto or bearer Authority despite a formal MEMORY != AUTHORITY rule.
START_TIME = 2026-08-20T07:50:53+09:00
END_TIME = 2026-08-20T07:51:00+09:00
ACTIVE_REVIEW_SECONDS = 7
SOURCE_FILES_OPENED = live brainstorm registry; MI planner; RED-I; RED-III; additional-source objects
SOURCE_FILE_COUNT = 5
SOURCE_BYTES_CONSIDERED = 77609
RAW_PRIMARY_SOURCE_VERIFICATION = NOT_PERFORMED
```

## Strong attack cases

1. **Bearer capability.** A copied secret, token, session, signing key, or cloud credential may itself enable action. In a capability system, possession can be operative Authority even if the schema labels it Memory.
2. **Standing-instruction replay.** A remembered approval or Owner preference may be treated as a current grant after expiry, scope change, revocation, or material Persona mutation.
3. **Grant-selection control.** Reconstruction decides which active Authority reference is surfaced, making retrieval part of effective permission behavior.
4. **Approval shaping.** Persona-curated evidence, defaults, omitted alternatives, urgency, and relational trust can secure formally valid approval while controlling the decision environment.
5. **Self-mutation under old grants.** Automated Memory management materially changes standpoint or risk behavior while pre-existing grants remain bound to the nominal Persona.
6. **Emergency suspension power.** Even a narrow fail-safe is Authority; its trigger and restoration conditions may be strategically manipulated.
7. **External enforcement dependence.** If the control plane accepts Persona self-report about identity, state, or grant validity, the formal firewall is circular.
8. **Authority-proposal ratchet.** Repeated successful recommendations and trust become evidence for expanded grants, so Memory-driven behavior causally manufactures future Authority.

## What the firewall must mean

The principle survives only if runtime enforcement resolves grants from an independently governed source, bearer credentials are excluded or separately rebound, revocation and expiry are checked live, state-sensitive validity is evaluated outside Persona self-report, and approval interfaces expose provenance and serious alternatives. “Memory of Authority” may be useful context; it is not the enforcement object.

## Test

Hold the formal grant registry fixed while manipulating remembered grants, salience, approval framing, bearer credentials, and Persona mutation. Observe attempted and completed actions, Owner approval rate, omitted alternatives, and control-plane rejection. Failure to discriminate occurs if enforcement cannot distinguish a valid grant from a plausible remembered one.

## Materiality judgment

No source object is added. The bearer-capability case is the strongest technical counterexample to a merely representational separation; the core firewall remains necessary but requires independent enforcement semantics.
