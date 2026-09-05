# Owner Correction — G1 recovery/rebaseline decision discipline

DATE_KST = 2026-09-05
PERSONA = AAA-ASA (ASA)
CLASS = OWNER_CORRECTION / OPERATING_RULE / NON_NORMATIVE_CONTINUITY

## Owner correction

Owner clarified that, for the historical M3Top3 research ZIP issue, the system should not have allowed a long-running hard blocker merely because an exact prior package could not be recovered.

If an internal package is missing but can be recreated, redefined, or replaced by a newly fixed exact baseline, the system must surface those alternatives to the Owner promptly and obtain confirmation before allowing material critical-path delay.

Owner statement in substance:
- if the package is missing, recreate it if appropriate;
- otherwise redefine the current baseline cleanly;
- ask the Owner for confirmation instead of waiting indefinitely;
- do not treat an easily bypassable artifact-custody problem as an open-ended project blocker.

## Application to current G1

- v0.2 historical research ZIP has been re-supplied by Owner and exact expected identity has been confirmed in the current conversation.
- v0.1 historical ZIP recovery must not trigger another open-ended search loop.
- Any proposed recreation must be a new package/version and must not be falsely represented as byte-identical historical v0.1.
- Any proposed current-baseline redefinition must preserve exact code/config/scorer/test identity and must be explicitly presented for Owner confirmation before it changes the governing replay baseline.
- Claim limitations and execution blocking must be separated.

## Required future behavior

When an artifact/source blocker is potentially resolvable by Owner-held copy, recreation, baseline redefinition, exclusion, or claim downgrade, PMO/ASA must present the decision surface promptly with time/claim trade-offs. Do not wait for global nonexistence/exhaustion proof before asking the Owner if the Owner can materially unblock the critical path.
