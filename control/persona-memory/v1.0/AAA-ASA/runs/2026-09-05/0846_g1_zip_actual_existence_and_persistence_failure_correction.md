# G1 ZIP actual-existence / persistence-failure correction — 2026-09-05 08:46 KST

CURRENT_PERSONA_LOCK = AAA-ASA (ASA)

OWNER QUESTION = Was the ZIP actually created before, and how was recovery searching for it?

CORRECTED FACTS:
- Prior File Library / execution records prove both exact ZIP source files were physically present in the 2026-08-19 runtime before Git registration.
- v0.2 was explicitly created as a local runtime successor artifact at `/mnt/data/AAA_M3TOP3_GR_RESEARCH_PACKAGE_v0.2_WORKING.zip`, SHA256 `5bbe75a4c9966abcb9f10d2f1e84df983977c1cf76d69e7bda6dfe4f24e60836`, 40,210 bytes, 10 entries.
- Prior redelivery packet states the exact v0.2 ZIP was physically attached and PMO reverified ZIP hash/size/entry count, manifest hash, all 9 component hashes/sizes, and component digest.
- Registration execution preflight independently reported BOTH source ZIPs present and exact SHA256/size/native Git blob identities matching.
- The persistent Git registration failed during binary Git blob staging: create-blob returned blob identities different from the independently computed native Git blob IDs. No tree, registration commit, target-path add, or ref advance was made.
- Recovery R1 reproduced the same Package-01 blob mismatch even when `encoding=base64` was attempted. Root mechanism remained `BINARY_GIT_BLOB_TRANSPORT_BYTE_IDENTITY_NOT_PROVEN`; source corruption was not proven.
- At the time of failure, reports explicitly stated exact source objects were still available locally and should be preserved unchanged.
- Because persistent registration never completed, those exact bytes remained runtime-only. Later successor runtimes no longer had the old `/mnt/data` artifact.
- Issue #52 recovery then searched the then-current `/workspace` (~2,980 files), default branch, four registration/recovery branches, and available custodian/archive/attachment locators. It did not recover the exact bytes.
- Current File Library search found the historical return packets and runtime locator/proofs, but not an actual ZIP file object.

CORRECTION TO PRIOR ASA EXPLANATION:
- Do NOT say the ZIP may never have existed. The durable execution records prove it did exist in the prior runtime.
- Do NOT describe G1 primarily as unknown provenance/source origin. The proximate incident is a failed persistence/transport handoff of known-good runtime bytes, followed by loss of the ephemeral runtime bytes across runtime succession.

PROGRAM IMPLICATION:
- G1 is a persistence/custody incident, not evidence that the research/model source itself was absent or unknown.
- This strengthens the case for treating the missing historical ZIP as nonblocking provenance/custody debt if Owner elects to freeze the current exact baseline and proceed.
