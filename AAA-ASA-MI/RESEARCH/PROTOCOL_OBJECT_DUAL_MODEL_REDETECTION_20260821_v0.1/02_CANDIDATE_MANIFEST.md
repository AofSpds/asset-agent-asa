# N01–N12 Frozen Candidate Manifest

PROJECT = AAA
TASK = AAA_ASA_MI_PROTOCOL_OBJECT_DUAL_MODEL_REDETECTION_v0.1
STATE = ARCHITECTURE_FROZEN / NON_NORMATIVE / NOT_VALIDATED
FREEZE_RECEIPT = RECEIPTS/CANDIDATE_ARCHITECTURE_FREEZE.md
DIGEST_RECEIPT = RECEIPTS/ARTIFACT_RECEIPTS.md

## Manifest

| ID | Working name | Family seed | Object Model | Protocol Model | Interaction discriminator | Frozen SHA-256 |
|---|---|---|---|---|---|---|
| N01 | Evidentiary Typed Hypergraph | Relation-first | Immutable typed attributed hypergraph snapshots | Sandboxed signed adapters with explicit capabilities | Protocol queries/plans over graph; graph evidence and triggers constrain Protocol | `c7745acf9ffe…` |
| N02 | Capability Relational Fabric | Relation-first | Revisioned objects plus addressable n-ary relations and conservative CRDT primitives | Versioned capability-bounded rule/merge/materialization descriptor | Exact-Protocol operations over named snapshots with typed capability proofs | `4c447d7a1228…` |
| N03 | Event-Sourced Temporal World | Event/process-first | Versioned object definitions projected from immutable temporal event logs | Temporal evaluator and transition descriptor | Replay/cut queries and authorized event append; projections never become source truth | `c9ee69330d10…` |
| N04 | Commitment Actor Ecology | Event/process-first | Addressable actor boundaries with mailboxes, commitments, and causal frontiers | Actor/process protocol with routing and effect profile | Messages activate Protocol actors; object responses alter commitments only by authorized events | `0adc320c14a1…` |
| N05 | Witnessed Relation/Event Incidence | Relation–Event co-constitutive | Typed objects/relations and before/after revisions | Finite Protocol IR with witness policies | Validated squares witness how transitions preserve or change relations | `7930088b30ca…` |
| N06 | Causal-Incidence Co-Constitution | Relation–Event co-constitutive | Structural incidence plus causal event configurations and explicit branches | Evaluators with support envelopes and bridge contracts | Relations constrain admissible events; events revise relations with causal/counterfactual receipts | `9a7354671a5b…` |
| N07 | Evidence-Kernel Protocol VM | Protocol-native/meta | Minimal stable evidence kernel with exact identities, observations, provenance, and frontiers | Typed metered bytecode/IR admitted to a sandboxed VM | VM runs explicit Protocol instances; kernel can challenge, suspend, or request evidence | `96cfbcd01e33…` |
| N08 | Proof-Carrying Contract Lattice | Protocol-native/meta | Stable typed substrate with versioned objects and observations | Proof-carrying contracts in a context-indexed partial refinement lattice | Engagement requires frame-specific witnesses; failed proof remains `NOT_PROVEN` | `9aba672416d6…` |
| N09 | Membrane Rewrite World | Alternative formalism | Typed terms in nested local membranes | Provenance-bearing bounded rewrite rules | Critical pairs expose conflicts; localized rewrites type each effect and preserve traces | `5c7d053e8c7f…` |
| N10 | Guarded Viability Field | Alternative formalism | Hybrid continuous/discrete state with exact symbolic records | Viability/control policy plus symbolic authority/provenance guard | Control proposals can shape trajectories; only symbolic guards authorize mutation | `6302d127b8e9…` |
| N11 | Polycentric Institutional Blackboard | Wildcard | Append-only board of claims, commitments, dissent, authority, and evidence | Polycentric institutional rule ecology with explicit jurisdictions and powers | Posts activate/contest/suspend Protocols; Protocols create scoped institutional positions | `ae72465cc71f…` |
| N12 | Patch–Lens Ecology | Wildcard | Canonical typed patch ledger and plural state branches | Versioned contextual bidirectional lenses with round-trip/loss laws | Materialization and guarded write-back use law receipts; nonrepresentable changes refuse | `a24e973501bb…` |

## Diversity floor

| Required seed | Count | Candidates | Result |
|---|---:|---|---|
| Relation-first | 2 | N01, N02 | PASS |
| Event/process-first | 2 | N03, N04 | PASS |
| Relation–Event co-constitutive | 2 | N05, N06 | PASS |
| Protocol-native/meta-model | 2 | N07, N08 | PASS |
| Non-obvious alternative formalism | 2 | N09, N10 | PASS |
| Wildcard without forced family assignment | 2 | N11, N12 | PASS |

DIVERSITY_FLOOR_RESULT = PASS_12_OF_12

The labels above describe generation seeds, not a ranking or an assertion that a candidate is confined to one family. None reuses or repairs C01–C08, and no D1 result or prediction informed generation.

## Mandatory-schema completeness check

This check occurred after architecture text binding. It does not edit or repair a candidate.

| State | Candidates | Finding |
|---|---|---|
| `PASS` | N01–N06, N08, N10, N12 | All mandatory surfaces, including the common result-status distinctions, are explicit enough for paper stress. |
| `PARTIAL_NONCANONICAL_STATUS_ALGEBRA` | N07 | Plural/conflict/refusal mechanics are explicit, but the frozen paper does not provide a complete exact crosswalk for `UNKNOWN / CONFLICT / NOT_PROVEN / OUT_OF_SCOPE / MULTIPLE_VALID`. |
| `PARTIAL_NONCANONICAL_STATUS_ALGEBRA` | N09 | Local `unknown / contested / inapplicable / unsupported` semantics are explicit, but `NOT_PROVEN` and `OUT_OF_SCOPE` are not completely separated in the common result algebra. |
| `PARTIAL_NONCANONICAL_STATUS_ALGEBRA` | N11 | Institutional `undetermined / contested / opaque / declined` states are explicit, but mapping them to the common status algebra is lossy and incomplete. |

REQUIREMENT_MATRIX_STATE = COMPLETE_REQUIREMENTS / CANDIDATE_COMPLIANCE_PASS_9_PARTIAL_3

The three partial candidates remain evidence; post-freeze status repair is prohibited. Their M8 architecture contact is not credited as full common-algebra support.

## Frozen state rule

All later battery responses are external evaluation records against the listed hashes. A failed test cannot edit the candidate. A new semantic design must be named as a successor with new exact identity and lineage.
