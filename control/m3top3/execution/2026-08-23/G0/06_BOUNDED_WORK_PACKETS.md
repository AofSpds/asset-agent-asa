# M3Top3 G0 Bounded Work Packets

Common parent: `AAA-M3TOP3-P0-VALIDATION-REBASE-G0-20260823-0045-01`  
Authority cap: `G0 + bounded WP0–WP4 preflight only`  
Mutation isolation: `READ_ONLY until a separately reviewed remediation packet is admitted`  
IVA: `NO PARTICIPATION / NO WORK PACKET / NO EXECUTION SURFACE`

## WP0 — Bootstrap and authority binding

```text
WORK_PACKET_ID = AAA-M3TOP3-G0-WP0-20260823-01
AUTHOR = AAA-PMO-ORCHESTRATOR
OUTPUTS_REQUIRED = Receipt, Docket, Registry, Master Status, Findings, Transition Register, Input Manifest, Journal
VALIDATION_ROUTE = PMOV audits PMO status/omission/decision trace; NOT IVA
COMPLETION_CRITERIA = exact inputs PASS; control objects open; no false state claim
OWNER_ACTION_REQUIRED = FALSE
```

## WP1 — Exact baseline identity

```text
WORK_PACKET_ID = AAA-M3TOP3-G0-WP1-20260823-01
AUTHOR_ROUTE = AAA-MODEL-ARCHITECT + AAA-ENGINEERING-ORCHESTRATOR + AAA-CONTROL-ARCHITECT
VALIDATOR_ROUTE = AAA-MODEL-VALIDATOR + AAA-ENGINEERING-VALIDATOR + AAA-CONTROL-VALIDATOR
AUTHORIZED_SCOPE = semantic/code/config/environment/provenance inventory and exact recovery classification
PRESERVE_SET = v1 feature meanings, weights, scorer, missingness, gates, PIT and GT
OUTPUTS_REQUIRED = exact identity manifest; missing evidence list; EXACT/SEMANTIC/APPROXIMATE verdict
COMPLETION_CRITERIA = S0→S1 evidence candidate; no outcome-tuned mutation
OWNER_ACTION_REQUIRED = FALSE
```

## WP2 — Universe, eligibility, windows and exposure

```text
WORK_PACKET_ID = AAA-M3TOP3-G0-WP2-20260823-01
AUTHOR_ROUTE = AAA-CONTROL-ARCHITECT + AAA-RESEARCH-ORCHESTRATOR + AAA-ENGINEERING-ORCHESTRATOR
VALIDATOR_ROUTE = AAA-CONTROL-VALIDATOR + AAA-RESEARCH-VALIDATOR + AAA-ENGINEERING-VALIDATOR
AUTHORIZED_SCOPE = U127 current release/provenance; denominator_T; W1-W8 dates; outcome access ledger; sealed holdout determination
OUTPUTS_REQUIRED = universe release manifest; exposure manifest; deterministic eligibility specification
COMPLETION_CRITERIA = no denominator drift; no false population/holdout claim
OWNER_ACTION_REQUIRED = FALSE
```

## WP3 — Historical PIT, data and annotation readiness

```text
WORK_PACKET_ID = AAA-M3TOP3-G0-WP3-20260823-01
AUTHOR_ROUTE = AAA-RESEARCH-ORCHESTRATOR + CTL/ENG/MOD support
VALIDATOR_ROUTE = AAA-RESEARCH-VALIDATOR + affected paired validators
AUTHORIZED_SCOPE = company-window-feature census; PIT vintage; price/CA/calendar/entity releases; blinded annotation protocol
OUTPUTS_REQUIRED = readiness matrix; admission ledger; source/provenance hashes; schedule rebaseline
COMPLETION_CRITERIA = no invented values; explicit RECOVERABLE/PARTIAL/UNRECOVERABLE/PIT_UNVERIFIED status
OWNER_ACTION_REQUIRED = FALSE
```

## WP4 — Fail-closed runtime and immutable lineage

```text
WORK_PACKET_ID = AAA-M3TOP3-G0-WP4-20260823-01
AUTHOR_ROUTE = AAA-ENGINEERING-ORCHESTRATOR + CTL/MOD support
VALIDATOR_ROUTE = AAA-ENGINEERING-VALIDATOR + AAA-CONTROL-VALIDATOR
AUTHORIZED_SCOPE = read-only defect confirmation and remediation specification; no official run
OUTPUTS_REQUIRED = P0 defect register; fail-closed acceptance tests; lineage/readback contract; implementation change packet
COMPLETION_CRITERIA = official execution remains blocked until all mandatory failures are non-zero/blocking and rank/store lineage is immutable
OWNER_ACTION_REQUIRED = FALSE
```

