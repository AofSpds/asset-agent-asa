# ME-2 Corpus Blocklist v0.1

## Absolute Content Blocks Before Both Proxy Outputs and Owner Initial Judgment Are Fixed

- Any evaluator rank, score, preference conclusion, comparative verdict, or assessment narrative
- Any champion, winner, recommended-track, selected-candidate, or final-selection label
- Any Track-to-source, Track-to-old-alias, source-to-Track, or candidate-to-source mapping
- The prior pilot alias key and any derivative alias lookup
- Current Owner candidate preference
- Post-cutoff Owner preference evidence
- Earlier Proxy predictions or Owner-choice forecasts
- Candidate status metadata and research-position provenance metadata

## Repository Path and Filename Blocks

- Any path under an evaluation, ranking, score, result, selection, or champion directory
- Any PILOT_ALIAS_KEY file or similarly named alias-key artifact
- Any old Track mapping artifact
- Any original CANDIDATES body
- Any file not explicitly admitted by the applicable P0 or P1 allowlist

## Private Scene Artifacts Blocked From Proxies and Owner Bundle

- ALIAS_CODEBOOK_PRIVATE_v0.1.json
- RANDOMNESS_RECEIPT_PRIVATE_v0.1.json
- PRIVATE_SOURCE/**
- Any temporary file or tool output that can reconstruct candidate-to-source mapping

## Known Defect Tokens Blocked From Public Briefs

- Source-position identifiers for the eight permitted inputs
- The malformed duplicated assumption labels identified in the delegated task
- Prior-track language
- Evaluator, winner, champion, or result cues
- Old alias-key language
- Freeze-note metadata
- The residual phrase research basis

## Enforcement

Default deny. The only exceptions are files explicitly listed in the applicable allowlist. Any uncertainty about access scope causes the worker to stop and record independence as NOT_PROVEN.

