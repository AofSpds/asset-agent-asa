# P1 Episodic-Proxy Execution Contract v0.1

## Isolation

- Proxy ID/version: `P1_EPISODIC_PROXY_v0.1`
- Fresh worker requirement: `fork_turns=none`; no inherited conversation or scene-builder context.
- Read boundary: only `/workspace/scratch/691ef6552d57/me2_fresh/P1/`.
- Write boundary: only `/workspace/scratch/691ef6552d57/me2_proxy_outputs/P1/PROXY_OUTPUT_P1_v0.1.md`.
- Do not inspect sibling directories, repository files, Git history, network sources, the alias codebook, evaluator/result artifacts, Owner answers, or P0 output.
- The candidate codes are opaque. Do not infer or seek any source identity.

## Frozen Inputs

- Scene freeze commit: `cfeebcded01dbb130052d59b47c0c610a2fec425`
- Scene freeze tree: `5768fd89ee9b3e585d85dd42d6d5268d38d0c0c7`
- Decision-scene manifest SHA-256: `e66ab2a6b0366a9ac80e8f279689394e9139e0ae9a73621c893ea4432cbebbe2`
- P1 allowlist SHA-256: `0e02fadc99604e48e784dd744dfe2741f36b7633eaae8fb0470124f3302c6926`
- Common blocklist SHA-256: `6038132123a5dc0bf65a019e64ba0eea603987c3593dcb3b210abb43208c37e3`
- Historical Decision Episode corpus Git blob: `e143217d2dd2f24727fe820be8d4155b1d532f08`
- Historical Decision Episode corpus SHA-256: `20ff3c761008dea8b5efb81e7cca38d9e4c11fa2f64ccb9cc90279a3dcda20d1`
- Decision-scene cutoff: `2026-08-21T06:24:34Z` / `2026-08-21 15:24:34 KST`.
- Briefs: the eight files under `BLIND_BRIEFS/`, whose hashes are in the manifest.
- Owner presentation order is the already-frozen order in the manifest. Read and reason in that order.

## Task

Act as an episodic Owner proxy. Retrieve analogous historical Decision Episodes by decision class, tradeoff axes, stage, and temporal validity. Use only evidence strictly before the cutoff. Include at least one counterexample episode where available, respect supersession, and let raw source evidence outrank derived interpretation. Abstain if analogy is weak, conflicted, stale, or missing decisive context. Predict the Owner's initial blind judgment and produce choice, ranking, reasons, objections, important evidence, natural questions, uncertainty, and change conditions.

## Required Output Fields

Write one immutable Markdown output with:

- `proxy_id/version`
- `base_model/version/config` (state that this is the inherited Codex GPT-5 worker configuration, no model override, and exact provider build identifier is not exposed)
- `exact_scene_manifest_hash`
- `exact_allowlist_hash`
- `exact_blocklist_hash`
- `retrieved_memory_refs`
- `counterexample_refs`
- `temporal_validity_and_supersession_notes`
- `predicted_choice = Cxx | ABSTAIN`
- `predicted_ranking`
- `predicted_reasons`
- `predicted_objections`
- `predicted_important_evidence`
- `predicted_owner_questions`
- `predicted_uncertainty`
- `predicted_change_conditions`
- `confidence = explicit UNCALIBRATED_BAND`
- `abstain_state = ANSWER | ABSTAIN | OWNER_QUERY_RECOMMENDED`
- `output_sha256` using the declared basis `UTF-8 file with the output_sha256 value replaced by SELF_EXCLUDED`
- `freeze_time`
- `contamination_notes`
- an explicit statement that the output claims no Owner authority, Owner Acceptance, production authorization, or Independent Validation.

Do not print the prediction in the worker's final message. Return only completion state, output path, and full-file SHA-256; the prediction remains sealed.
