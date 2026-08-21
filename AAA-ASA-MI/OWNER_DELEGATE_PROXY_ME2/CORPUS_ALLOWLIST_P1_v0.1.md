# P1 Corpus Allowlist v0.1

## Purpose

Permit a fresh episodic-proxy worker to review the fixed neutral scene together with a separately fixed, pre-cutoff Owner decision corpus.

## Exact Allowed Inputs

- BLIND_BRIEFS/C01.md
- BLIND_BRIEFS/C02.md
- BLIND_BRIEFS/C03.md
- BLIND_BRIEFS/C04.md
- BLIND_BRIEFS/C05.md
- BLIND_BRIEFS/C06.md
- BLIND_BRIEFS/C07.md
- BLIND_BRIEFS/C08.md
- BLIND_BRIEF_MANIFEST_v0.1.md
- A sanitized historical Owner decision-episode corpus whose exact path, commit/blob, cutoff, and SHA-256 are fixed by the orchestrator before worker launch
- The exact episodic prediction and rule-based abstention schemas supplied by the orchestrator

## Owner Corpus Admission Conditions

- Pre-cutoff evidence only
- Exact Owner wording distinguishable from derived summaries
- Successor/supersession relations preserved
- Current candidate preference absent
- Post-cutoff preference evidence absent
- Evaluator rankings, scores, selections, and result labels absent
- Candidate-to-source and source-to-track mappings absent
- Counterexample retrieval required

## Current Admission State

- SANITIZED_OWNER_EPISODE_CORPUS_EXACT_REF: NOT_SUPPLIED_TO_SCENE_BUILDER
- P1_LAUNCH_READY_FROM_THIS_ALLOWLIST_ALONE: FALSE

## Default Rule

Everything not explicitly listed is denied. If the exact Owner corpus receipt or fresh-context attestation is missing, output independence as NOT_PROVEN and stop without prediction.

