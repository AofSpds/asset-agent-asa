# Eligibility Evidence-Recovery Request v0.1

`REQUEST_ID = M3TOP3-ELIGIBILITY-EVIDENCE-RECOVERY-20260823-01`

## Boundary

- Target: the frozen 32-cell procedure-validation sample plus one fixed negative control.
- Sample CSV SHA-256: `bd1dcef5e446591b25ee902c46e010618a3aef30f9ca58865ab01daceb89715b`.
- Queue SHA-256: `02bde437c04b1cc3d314b30e9bdd41bdb9a9164d0d2df4468728bdab8089eb62`.
- Executor requirement: outcome-blind retrieval/decision actors who have not accessed winner, rank, return, MFE or later-success surfaces for the sampled company-windows.
- IVA participation: `NONE`.
- PMO role: packet control, input/output hashing and blocker recording only; PMO does not code the eligibility decisions.

## Allowed work

1. Listing/tradability evidence first, using cutoff-safe KRX/KIND or admitted daily-ledger evidence.
2. Business-scope evidence only when listing/tradability is not deterministically false.
3. Preserve source bytes, timezone-aware publication time, retrieval sidecar and source SHA-256.
4. Produce two independent pre-adjudication decisions when interpretation is required.
5. Preserve `UNRECOVERABLE` or `UNRESOLVED` when evidence or the stopping rule does not support a deterministic decision.

## Prohibited work

- No winner/rank/return/MFE/current-success access.
- No post-cutoff evidence backfill.
- No use of current business position as historical fact.
- No silent denominator deletion or forced eligibility.
- No scoring, ranking, Golden, Replay or model-performance output.
- No sample-to-514 completion-rate extrapolation.

## Required per-cell output

- exact sample record ID and selection hash
- company/window/cutoff/entry identity
- listing/tradability state and source refs
- business-scope state and source refs
- combined eligibility state
- retrieval and access sidecar hashes
- two pre-adjudication outputs or a mechanical-decision flag
- adjudication state and conflict disposition
- terminal reason and stopping-rule receipt

This request prepares execution but does not assert that a suitable outcome-blind executor is currently assigned. `OWNER_ACTION_REQUIRED=FALSE` until new resources, cost, credentials or semantic changes are requested.
