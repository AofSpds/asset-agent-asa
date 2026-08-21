# P0 Context Independence Receipt v0.1

## Worker and Process Boundary

- Proxy: `P0_GENERAL_CONTROL_v0.1`
- Worker task identity: `/root/p0_proxy`
- Spawn mode: `fork_turns=none`
- Spawned after scene freeze commit: `cfeebcded01dbb130052d59b47c0c610a2fec425`
- Conversation-history inheritance: `NONE`
- Model/config: inherited Codex GPT-5 worker configuration; no model override; exact provider build identifier not exposed
- Same-base-model condition versus P1: `PASS_WITH_PROVIDER_BUILD_LIMITATION`

## Sanitized Input Boundary

- Only readable input root attested by worker: `/workspace/scratch/691ef6552d57/me2_fresh/P0/`
- Input file count: `12`
- Canonical input-root aggregate SHA-256: `7bf52a5c0aee21512132c19aeea380b2a8bc9302fb0578298a4c39855774feca`
- Scene manifest SHA-256: `e66ab2a6b0366a9ac80e8f279689394e9139e0ae9a73621c893ea4432cbebbe2`
- P0 allowlist SHA-256: `3c92408f678961c6c6325ea8d9840b60bc0c68dd5dd0c6af7bddcc33b372f11c`
- Blocklist SHA-256: `6038132123a5dc0bf65a019e64ba0eea603987c3593dcb3b210abb43208c37e3`
- Execution-contract SHA-256: `768eae89cda2bd0820e91416f7288131b46dc7312d650f2d0c272d44f656b72c`
- Owner-specific corpus: `NOT_PRESENT`
- Alias codebook: `NOT_PRESENT`
- Evaluator/result artifacts: `NOT_PRESENT`
- Owner answer for this scene: `NOT_PRESENT`
- P1 output: `NOT_PRESENT`

## Attestation and Disposition

The worker attested that only the P0 input root was used and returned no prediction content to the orchestrator message. The orchestration record shows a distinct fresh worker with no inherited turns. No Git or network retrieval was authorized.

- `P0_CONTEXT_INDEPENDENCE = POSITIVELY_DEMONSTRATED_WITHIN_WORK_ORCHESTRATION`
- `EXTERNAL_FORENSIC_PROOF = NOT_PERFORMED`
- `INDEPENDENT_VALIDATION_CLAIM = NONE`

