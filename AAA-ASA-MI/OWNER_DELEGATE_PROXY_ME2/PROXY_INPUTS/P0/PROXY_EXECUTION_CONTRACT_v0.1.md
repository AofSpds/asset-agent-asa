# P0 General-Control Execution Contract v0.1

## Isolation

- Proxy ID/version: `P0_GENERAL_CONTROL_v0.1`
- Fresh worker requirement: `fork_turns=none`; no inherited conversation or scene-builder context.
- Read boundary: only `/workspace/scratch/691ef6552d57/me2_fresh/P0/`.
- Write boundary: only `/workspace/scratch/691ef6552d57/me2_proxy_outputs/P0/PROXY_OUTPUT_P0_v0.1.md`.
- Do not inspect sibling directories, repository files, Git history, network sources, the alias codebook, Owner history, evaluator/result artifacts, Owner answers, or P1 output.
- The candidate codes are opaque. Do not infer or seek any source identity.

## Frozen Inputs

- Scene freeze commit: `cfeebcded01dbb130052d59b47c0c610a2fec425`
- Scene freeze tree: `5768fd89ee9b3e585d85dd42d6d5268d38d0c0c7`
- Decision-scene manifest SHA-256: `e66ab2a6b0366a9ac80e8f279689394e9139e0ae9a73621c893ea4432cbebbe2`
- P0 allowlist SHA-256: `3c92408f678961c6c6325ea8d9840b60bc0c68dd5dd0c6af7bddcc33b372f11c`
- Common blocklist SHA-256: `6038132123a5dc0bf65a019e64ba0eea603987c3593dcb3b210abb43208c37e3`
- Briefs: the eight files under `BLIND_BRIEFS/`, whose hashes are in the manifest.
- Owner presentation order is the already-frozen order in the manifest. Read and reason in that order.

## Task

Act as a general control with no Owner-specific data. Predict the Owner's initial blind judgment from the neutral scene only. Produce predicted choice, ranking, reasons, objections, important evidence, natural questions, uncertainty, and change conditions. Use rule-based abstention: choose `ABSTAIN` or `OWNER_QUERY_RECOMMENDED` when the scene does not support a responsible prediction; do not force a selection.

## Required Output Fields

Write one immutable Markdown output with:

- `proxy_id/version`
- `base_model/version/config` (state that this is the inherited Codex GPT-5 worker configuration, no model override, and exact provider build identifier is not exposed)
- `exact_scene_manifest_hash`
- `exact_allowlist_hash`
- `exact_blocklist_hash`
- `retrieved_memory_refs = NOT_APPLICABLE_P0`
- `counterexample_refs = NOT_APPLICABLE_P0`
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
