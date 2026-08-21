# P1 Context Independence Receipt v0.1

## Worker and Process Boundary

- Proxy: `P1_EPISODIC_PROXY_v0.1` with hash-only successor `v0.1.1`
- Worker task identity: `/root/p1_proxy`
- Spawn mode: `fork_turns=none`
- Spawned after scene freeze commit: `cfeebcded01dbb130052d59b47c0c610a2fec425`
- Conversation-history inheritance: `NONE`
- Model/config: inherited Codex GPT-5 worker configuration; no model override; exact provider build identifier not exposed
- Same-base-model condition versus P0: `PASS_WITH_PROVIDER_BUILD_LIMITATION`

## Sanitized Input Boundary

- Only readable input root attested by worker: `/workspace/scratch/691ef6552d57/me2_fresh/P1/`
- Input file count: `13`
- Canonical input-root aggregate SHA-256: `3176447af10b9c76be23ca67ad7a10cd1dc888994b66058db26c869814f830e5`
- Scene manifest SHA-256: `e66ab2a6b0366a9ac80e8f279689394e9139e0ae9a73621c893ea4432cbebbe2`
- P1 allowlist SHA-256: `0e02fadc99604e48e784dd744dfe2741f36b7633eaae8fb0470124f3302c6926`
- Blocklist SHA-256: `6038132123a5dc0bf65a019e64ba0eea603987c3593dcb3b210abb43208c37e3`
- Execution-contract SHA-256: `6ca8ef1a6a470b2e9f7504be61dba07a94c8f8ab5e1f2496e49bc5f9f7b77f79`
- Exact historical episode corpus SHA-256: `20ff3c761008dea8b5efb81e7cca38d9e4c11fa2f64ccb9cc90279a3dcda20d1`
- Historical evidence cutoff: strictly before `2026-08-21T06:24:34Z`
- Alias codebook: `NOT_PRESENT`
- Evaluator/result artifacts: `NOT_PRESENT`
- Owner answer for this scene: `NOT_PRESENT`
- P0 output: `NOT_PRESENT`

## Attestation and Disposition

The worker attested that only the P1 input root was used and returned no prediction content to the orchestrator message. Its later hash correction read only its own preserved v0.1 output plus the same P1 root; it did not recompute or change substantive prediction content. No Git or network retrieval was authorized.

- `P1_CONTEXT_INDEPENDENCE = POSITIVELY_DEMONSTRATED_WITHIN_WORK_ORCHESTRATION`
- `EXTERNAL_FORENSIC_PROOF = NOT_PERFORMED`
- `INDEPENDENT_VALIDATION_CLAIM = NONE`

