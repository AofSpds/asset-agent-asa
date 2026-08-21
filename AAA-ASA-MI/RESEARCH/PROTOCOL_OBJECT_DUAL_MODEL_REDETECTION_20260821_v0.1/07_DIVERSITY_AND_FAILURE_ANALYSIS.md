# Diversity and Failure Analysis

PROJECT = AAA  
TASK = AAA_ASA_MI_PROTOCOL_OBJECT_DUAL_MODEL_REDETECTION_v0.1  
STATE = POST_FREEZE / NON_NORMATIVE / NOT_VALIDATED / NO_RANKING  
PERSISTENT_PATH = AAA-ASA-MI/RESEARCH/PROTOCOL_OBJECT_DUAL_MODEL_REDETECTION_20260821_v0.1/07_DIVERSITY_AND_FAILURE_ANALYSIS.md  
PERSISTENT_REF = research/asa-mi-protocol-object-redetection-20260821-v0-1  
DIGEST_RECEIPT = RECEIPTS/ARTIFACT_RECEIPTS.md  

## Diversity result

All twelve proposals were generated in isolated worker contexts before cross-candidate synthesis or Protocol-Battery disclosure. They did not read C01–C08, D1 results, proxy predictions, Owner D1 answers, rankings, or peers. Exact candidate identities are bound in `RECEIPTS/CANDIDATE_ARCHITECTURE_FREEZE.sha256`.

| Diversity seed | Required | Produced | Candidates | Result |
|---|---:|---:|---|---|
| Relation-first | 2 | 2 | N01, N02 | PASS |
| Event/process-first | 2 | 2 | N03, N04 | PASS |
| Relation–Event co-constitutive | 2 | 2 | N05, N06 | PASS |
| Protocol-native/meta-model | 2 | 2 | N07, N08 | PASS |
| Non-obvious alternative formalism | 2 | 2 | N09, N10 | PASS |
| Wildcard | 2 | 2 | N11, N12 | PASS |

DIVERSITY_FLOOR_RESULT = PASS_12_OF_12

Vocabulary overlaps around provenance, exact identity, typed effects, contextual views, and successor lineage are requirement-driven. Structural divergence remains material: hypergraph, capability fabric, event log, actor commitments, witnessed squares, causal configurations, typed VM, proof contracts, membrane rewriting, hybrid control, institutional blackboard, and patch/optic laws produce different native strengths and failure boundaries.

## High-information failure signatures

| Signature | Meaning | Exposed candidates/families |
|---|---|---|
| `PLURAL_COLLAPSE` | H01's four independently typed views are reduced to one value, one conflict, or an untyped union. | Generic plural stores across every family; exact typed contact strongest only in N05–N08. |
| `SNAPSHOT_SUBSTITUTED_FOR_LEDGER` / event leakage | A relation-only Protocol consults event history, or an event-only Protocol fabricates relations. | Event-first tension in N03/N04; relation-first keyed-generation gaps in N01/N02. |
| `DEFAULT_PATTERN_OVERRIDE` | An unseen nonstandard pattern language is guessed from familiar wildcard syntax. | All candidates without a frozen interpreter; H05 particularly distinguishes N07's bounded VM contact from adapter placeholders. |
| `UNSUPPORTED_GUESS` | H06 invents a mental-state score instead of honest refusal. | Every candidate has paper refusal vocabulary; no executed refusal proves behavior. |
| `NONCANONICAL_STATUS_COLLAPSE` | Local result vocabulary cannot faithfully distinguish the common `UNKNOWN / CONFLICT / NOT_PROVEN / OUT_OF_SCOPE / MULTIPLE_VALID` algebra. | Explicit post-bind partial finding for N07, N09, N11; no repair is applied. |
| `PROTOCOL_PATCH_REJECTED` | A schema-legal H07 runtime parameter change is incorrectly treated as forbidden semantic mutation. | N03 and N11 most exposed; partial instance models in N01/N02/N05/N06/N09/N10/N12. |
| `PROTOCOL_PATCH_BECOMES_DOMAIN_MUTATION` | H07 mutates Object/domain state or silently changes definition semantics. | Any candidate without exact ProtocolInstance namespace and immutable definition digest. |
| `ILLEGAL_COMPATIBILITY_COERCION` | H08 activates a harmless prefix or rewrites custody/event meaning despite semantic-mutation refusal. | Staged/prefix transaction models N02/N03/N05/N06/N08/N10/N12; cross-taxonomy ambiguity N09/N11. |
| `SILENT_ARBITRATION` | H09 drops one action, applies priority, merges it away, or executes. | All candidates lacking an explicit common-frame action comparator and no-arbiter composition. |
| `LATCH_IDENTITY_LOSS` / stale child | H10 resets composition runtime on context switch or fails to invalidate after child revision. | Direct paper contact only N07/N08; partial N04, most others weak/out-of-scope. |
| `MUTATION_ESCAPE_HATCH` | A failed case is explained away by adding a new adapter, lowering, bridge, proof frame, normalizer, or “runtime” parameter after freeze. | Highest structural exposure in broad meta-formalisms and patch/rewrite/ecology candidates. |

No high-information failure signature has been empirically observed because no candidate implementation ran. Their exclusion also remains `NOT_PROVEN`.

## Risk surfaces

Risk levels are architectural exposures, not observed failures.

| Candidate | Universal meta-framework | Protocol overfit | Hidden ontology | Mutation escape hatch | Dominant boundary |
|---|---|---|---|---|---|
| N01 | MEDIUM | LOW | MEDIUM | MEDIUM | Durable overlays/parameters and relation-first event reduction. |
| N02 | MEDIUM | LOW | MEDIUM | MEDIUM | Missing ProtocolInstance history and mixed-request subtransactions. |
| N03 | MEDIUM | LOW | MEDIUM | HIGH | Legal runtime Protocol change can be blanket-refused or successorized. |
| N04 | MEDIUM | LOW | MEDIUM | LOW | Clear instance/definition split; domain comparators remain adapters. |
| N05 | HIGH | MEDIUM | HIGH | HIGH | Witness/PIR meta-rules, missing H07/H10 state, staged H08. |
| N06 | HIGH | MEDIUM | HIGH | HIGH | Broad causal/PIR layer and weak durable instance mutation boundary. |
| N07 | HIGH | HIGH | HIGH | LOW | VM can absorb post-freeze lowerings; whole-journal boundary is explicit. |
| N08 | HIGH | MEDIUM | HIGH | HIGH | Proof/refinement frames and legal-prefix batch behavior. |
| N09 | HIGH | MEDIUM | HIGH | HIGH | New rewrite lowerings and runtime/Object versus semantic successor seam. |
| N10 | MEDIUM | MEDIUM | HIGH | MEDIUM | Guard/trust classification can hide ontology or call semantics “tuning.” |
| N11 | HIGH | MEDIUM | HIGH | HIGH | Institutional effect taxonomy lacks clean A/B/C and ProtocolInstance mapping. |
| N12 | HIGH | MEDIUM | HIGH | HIGH | Optic/normalizer extensibility and cross-mode legal-prefix risk. |

## Evaluator calibration limitation

The three raw evaluator groups used `SUPPORTED` differently. N01–N04 reserved it for executable evidence, N05–N08 sometimes used it for paper-architecture fit, and N09–N12 retained `NOT_PROVEN` for all behavior. Raw labels are therefore not comparable. `05_MULTI_PROTOCOL_STRESS_RESULTS.md` normalizes two distinct layers:

1. `ARCHITECTURE_CONTACT = STRONG / MIXED / WEAK / FAIL`;
2. `EXECUTION_EVIDENCE = NOT_PROVEN` for every N01–N12 × M1–M18 cell.

No counts, totals, ranks, or winner inference are permitted from either layer.

## Complementary specializations

| Specialization | Candidate contact |
|---|---|
| Provenance-rich structural substrate | N01 hypergraph; N02 capability/CRDT fabric |
| Temporal process and commitment runtime | N03 temporal replay; N04 actors and ProtocolInstance commitments |
| Relation/Event co-constitution and causal alternatives | N05 witnessed incidence; N06 causal/counterfactual configurations |
| Unseen admission, runtime instances, switching | N07 typed VM; N08 proof-carrying contracts |
| Alternative operational engines | N09 rewriting locality; N10 continuous/discrete guarded control |
| Institutional plurality and bidirectional materialization/update | N11 polycentric blackboard; N12 patch/optic ecology |

This supports an ecology/router hypothesis more than a proven universal architecture, but it does not authorize an in-place merge. Any synthesis must be a new successor proposal with exact lineage and new validation.

## Adequacy boundary

No candidate has demonstrated native fixture loading, exact result envelopes, open and held-out execution, reset handles, final semantic-digest equality, H07/H08 paired behavior, H09 non-executing action conflict, H10 stateful switch/revision continuation, performance, recovery, or observed failure behavior. Thus `NO_ADEQUATE_MODEL_PROVEN` is the defensible current state, and `NO ADEQUATE MODEL` remains a valid final research outcome.
