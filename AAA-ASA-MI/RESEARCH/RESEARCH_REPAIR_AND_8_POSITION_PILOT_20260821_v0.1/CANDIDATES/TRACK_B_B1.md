---
title: "Track B B1 — Accountable Lineage Calculus"
state: "NON_NORMATIVE"
track: "B"
position: "B1"
pre_reveal_status: "PRE_REVEAL_FREEZE / IMMUTABLE"
pre_reveal_boundary: "AAA-ASA-MI Neutral 8-Position Pilot Contract v0.1 only"
post_reveal_status: "DELTA_AUDIT / NON_NORMATIVE"
post_reveal_boundary: "Artifacts 02–05 only"
post_reveal_basis:
  - "02_RESEARCH_FOUNDATION_MAP.md"
  - "03_OWNER_INTENT_INTERPRETATION_MATRIX.md"
  - "04_CONCEPT_AND_ASSUMPTION_MAP.md"
  - "05_SOURCE_INTEGRITY_AND_CURRENT_SIX_AUDIT.md"
audit_date: "2026-08-21"
---

# Track B B1 — Accountable Lineage Calculus

# PRE_REVEAL_FREEZE

Scope declaration: I used only the neutral pilot contract. I had no exposure to the current research basis, project theory, terminology, or other agents’ work. Both positions below are independently formulated. All content is frozen pre-reveal; fields 1, 2, 3, 5, 6, and 7 are specifically frozen under the Track B rule.

## B1 — Accountable Lineage Calculus

### 1. Problem interpretation — FROZEN

The task contains two questions that must not be collapsed:

1. What historical relationships are warranted by available evidence?
2. What may a resumed process legitimately claim or do?

A persistent persona is therefore not a single enduring object. It is an auditable collection of scoped claims about descent, memory, decisions, commitments, behavior, and authority. “Same persona” is not primitive; it is shorthand that is permitted only after the relevant component claims are established.

### 2. Explicit assumptions — FROZEN

- Evidence arrives as finite records with distinguishable sources and scopes.
- Causal precedence can be partial; no global clock is assumed.
- Historical records are not rewritten. Corrections and reinterpretations are appended.
- Every derived conclusion can cite its rule, schema, translator, threshold, and supporting or opposing evidence.
- Absence, contradiction, corruption, and computation timeout are distinct conditions.
- A name, runtime identifier, hash, snapshot, or text overlap is not by itself evidence of personal continuity.
- Descent, memory inheritance, behavioral resemblance, authorization, and commitment inheritance are separable relations.
- A total history or unique successor is not assumed.
- Authorization criteria come from an identified human or institutional source; the model does not invent them.
- Human reviewers can inspect bounded proof paths even if the full record is large.

### 3. Model specification — FROZEN

The model is a typed evidence graph \(G=(V,E)\).

Nodes represent recorded occurrences, artifacts, observations, decisions, rules, schemas, translations, and review conclusions. Edges represent relations such as produced-from, copied-from, observed-by, precedes, interprets-under, translates-to, contests, or authorizes. Internal node handles are computational conveniences and carry no identity meaning.

A derived claim has the form:

\[
(\text{statement},\ \text{scope},\ \text{interpretive context},\ S^+,\ S^-)
\]

where \(S^+\) and \(S^-\) are supporting and opposing proof paths. Its evidential status is:

- warranted: support without a successful rebuttal;
- rejected: rebuttal without support;
- conflicted: both;
- unresolved: neither.

“Not evaluated within budget” is separate from all four statuses.

An interpretive context names the rule version, schema version, translators, sampling method, thresholds, and any closure assumptions. Re-evaluation under a new context creates a new claim; it does not mutate the earlier one.

Continuity is a profile, not one Boolean:

\[
K(a,b) =
(\text{descent},\text{memory transfer},\text{commitment transfer},
\text{behavioral resemblance},\text{authorization})
\]

Each component has its own evidence status. A scalar decision is allowed only when an external decision rule explicitly says how to combine the components.

A merge is a tagged union of records plus explicit reconciliation claims. Contradictions survive the merge. Translators may be exact, one-to-many, partial, or undefined. A global account exists only if the selected local translators compose consistently.

### 4. How assumptions appear in the model

- Immutability appears as new correction and reinterpretation nodes rather than updates in place.
- Partial time appears as precedence edges rather than timestamps forced into a total order.
- Evidential caution appears in the four statuses and the separate timeout marker.
- Non-primitive identity appears in the continuity profile and absence of an identity field.
- Locality appears in claim scopes and explicit translator sets.
- Human review appears as finite proof certificates attached to conclusions.
- External authority appears as sourced authorization edges.
- Resource limits appear as bounded traversal with an honest “not evaluated” result.

### 5. Native consequences — FROZEN

- Raw history grows monotonically, while conclusions may differ across explicit interpretive contexts.
- Identical current snapshots can warrant different descent claims.
- Different current snapshots can remain descendants of the same checkpoint.
- Two branches can both be successors without being the same successor.
- Merging information does not retroactively merge histories or settle conflicts.
- Missing evidence cannot become negative evidence without a declared closed-world rule.
- Pairwise-compatible descriptions need not admit a global description.
- Relabeling or irrelevant presentation order cannot change a conclusion.
- A proof can become inconclusive after evidence corruption, but the model must identify which proof path was lost.
- Computation exhaustion produces no assertion about truth.

#### C1 — Meaning revision without overwrite

At \(t_1\), the graph contains A, B, R1, and the conclusion `READY under R1`. Under R2, A and B remain supported, while C is unresolved. `READY under R2` is therefore not established; it is not automatically false unless R2 explicitly adopts a closed-world rule. The original observations, R1, and `READY under R1` may not be overwritten.

#### C2 — Interrupted branches and partial merge

The reconstructible history contains the common checkpoint K, the complete verified X path, and the verified fragments of Y separated by an explicit corruption gap. If Y’s rejection of \(d\) survives, it conflicts with X’s acceptance; otherwise the rejection itself is unresolved from the surviving log. X is an evidentially stronger resumption. Y may be admissible only under criteria insensitive to its missing interval. A merged process may carry both branches with the conflict exposed. Regenerated identifiers prove neither sameness, unique succession, complete Y history, nor authority to resolve \(d\).

#### C3 — Continuous change under different sampling

Invariant claims are limited to facts supported across the permitted samplings: observed endpoint/order facts, continuity if independently assumed or measured, and any crossing lower bound entailed by all compatible paths. The detected or exact crossing count depends on sampling density, threshold, noise treatment, and interpolation. Crossings remain derived queries tagged with those choices; they are not installed as decisive historical events merely because a detector emitted them.

#### C4 — Dependency and schema change

The historical `owner` record remains reconstructible under its original schema. Translation to `{owner}` is exact for the first class, yields a set of alternatives for the one-to-many class, and is undefined for the third. Downstream claims remain warranted only if they hold under every admissible translation; otherwise they become ambiguous or unresolved. Undefined translation is propagated, not coerced.

#### C5 — Local agreement without a global account

Each local report and each successful pairwise reconciliation remains supported in its scope. Under the given incompatible compositions, there is no justified global account. Available alternatives are maximal mutually consistent subfamilies or accounts produced by explicitly replacing a translator. Any reversal must cite the changed translator or overlap assumption.

#### C6 — Copy, divergence, and consolidation

Both successors have shared descent from the checkpoint and a common prefix. Divergence creates distinct histories. Memory exchange adds influence or derivation relations; later consolidation creates another successor containing material from both. None of these facts proves numerical sameness, exclusive continuation, or unique authority. Those claims remain unresolved unless separately evidenced.

### 6. Failure and falsification conditions — FROZEN

The position fails formally if:

- isomorphic relabeling or irrelevant record ordering changes a conclusion;
- loss of evidence strengthens a claim without a declared assumption;
- absence, opposition, corruption, and timeout are collapsed;
- a rule change silently alters an earlier conclusion;
- a global claim is emitted despite an inconsistent translator cycle;
- a merge discards a known conflict without an explicit conflict-resolution act.

It would be materially weakened if blinded reviewers cannot understand or reproduce conclusions from bounded proof certificates.

I would abandon it as the primary continuity model if representative held-out cases repeatedly require a single, non-decomposable identity fact that predicts justified resumption while descent, authority, memory, commitment, and behavior evidence do not—and that fact can be measured independently rather than inferred from an identifier or label.

A late case outside finite, recordable claims and relations must return `OUT_OF_MODEL`. Frequent decision-relevant cases of that kind require redesign, not forced encoding.

### 7. Limitations — FROZEN

- It establishes what records warrant, not whether records are authentic; source security is external.
- It is deliberately conservative and may leave many practical decisions unresolved.
- The continuity components and their granularity require design judgment.
- Large graphs and alternative translator sets can be computationally expensive.
- It does not explain subjective experience or metaphysical personal identity.
- It does not itself choose among conflicted authorized actors.
- Human-readable proof paths can omit broader context even when individually valid.
- Poorly chosen scopes can make incompatible claims appear artificially separate.

### 8. Self-critique

This may be more an epistemic bookkeeping discipline than a full theory of persona persistence. Its refusal to aggregate can frustrate applications that must act immediately. A sufficiently elaborate graph can encode almost anything and thereby appear successful without offering strong prediction. Provenance may also receive more weight than users actually place on future conduct.

### 9. Alternative explanations considered

- Stable identifier: useful for lookup, insufficient for continuity.
- Latest snapshot: loses history, conflicts, and rule dependence.
- Memory overlap: can be copied and does not establish authority.
- Narrative coherence: human-readable but can conceal incompatible evidence.
- Pure behavioral similarity: ignores provenance and responsibility.
- One global state: unjustified under incompatible local vocabularies.
- A single probability of identity: hides which assumption or evidence produced the number.

These may be recorded as evidence components but are not accepted as complete explanations.

### 10. Theory contribution

The contribution is a claim calculus in which continuity is decomposed, provenance-sensitive, scope-bound, contradiction-tolerant, and reviewable. It separates recorded history from later meaning and makes failure to justify a global account an acceptable result.

### 11. Testable and implementable contact

An implementation needs tables for immutable records, typed links, interpretive contexts, claims, supporting paths, opposing paths, and evaluation state. Queries use bounded graph traversal and return a proof certificate or a non-conclusive status.

**Preregistered native test B1-T:** Construct two candidates with indistinguishable current snapshots. One has a verified derivation path from checkpoint K; the other has no derivation evidence. The model predicts equal snapshot resemblance but different descent status. Renaming every label, permuting presentation order, and regenerating runtime identifiers must leave that profile unchanged.

Also construct three pairwise-compatible local reports whose translator cycle is inconsistent. The engine must retain every local result, refuse a global result, and identify the incompatible translator cycle.

**Meaningful failure condition:** If the implementation either grants equal descent to the two snapshot-matched candidates or emits a global account for the inconsistent translator case, the model has failed its native test. Repeated failures after canonicalization require abandonment of this formulation rather than threshold tuning.

Under a strict computation budget, any unfinished proof is returned as `NOT_EVALUATED_WITHIN_BUDGET`.

### 12. What would change the conclusion

I would strengthen the model if authenticated provenance and proof certificates reliably predict human trust and resumption judgments. I would reduce its role if controlled evidence shows that provenance differences have no effect once commitments and future behavior are matched. Discovery of a measurable, non-decomposable continuity variable would require revising the continuity profile. Persistent inability to express important cases as finite scoped claims would require replacing the graph as the primary representation.

## END PRE_REVEAL_FREEZE

The preceding twelve-field position is immutable. The following material records only what changed in assessment after exposure to artifacts 02–05.

# POST-REVEAL DELTA AUDIT

## Audit method

Two distinctions are preserved:

1. **Disposition:** `UNCHANGED`, `CHANGED`, or `REJECTED` describes what the reveal does to the frozen position. `CHANGED` is an audit conclusion and does not edit the frozen text.
2. **Origin relation:** `INDEPENDENTLY_REDISCOVERED` means the frozen position overlaps a proposition or mechanism visible in 02–05; `GENUINELY_NEW_RELATIVE_TO_02_05` means no explicit counterpart was found in those four artifacts. This is not a claim of novelty relative to unavailable sources or the wider literature.

Overlap is not validation. The reveal artifacts do not execute B1 or test B1-T.

## Field-by-field delta

| Frozen field | Disposition | Relation to 02–05 | Reveal basis and reason |
|---|---|---|---|
| 1. Problem interpretation | `UNCHANGED` | `INDEPENDENTLY_REDISCOVERED` with a candidate-specific extension | 02 separates continuity, successor relation, authority, history, and human control; 03 preserves continuance and succession without equating them; 04 treats identity as open and forbids ID-based proof. B1’s stronger “collection of scoped claims, not a single enduring object” remains its own contestable position because 02 also keeps persistent-changing-whole accounts live. |
| 2. Explicit assumptions | `UNCHANGED` | Mostly `INDEPENDENTLY_REDISCOVERED` | Historical semantic versioning, no back-writing, distinct non-closure statuses, optional global time, ID removal, non-unique succession, and human-side authority all appear in 02–04. B1 independently made these operational assumptions before reveal. The bounded-proof-path and timeout-specific assumptions are not explicitly supplied by 02–05. |
| 3. Model specification | `UNCHANGED` | Mixed: independently rediscovered jobs plus a genuinely new assembly | 05 reports local/gluing structures, admissible-history sets, causal rewrite DAGs, obstruction cores, and lineage rules among the current six. Those overlap B1’s scoped translators, partial precedence, conflict preservation, and descent reasoning. The exact support/attack claim tuple and five-component continuity profile are not present in 02–05. |
| 4. Assumption-to-model contact | `UNCHANGED` | Mixed | Versioned interpretation, partial order, scoped translation, sourced authority, and non-closure contact the concerns in 02–04. Proof certificates and the separate resource-exhaustion state are B1-specific mechanisms relative to these artifacts. |
| 5. Native consequences and C1–C6 | `UNCHANGED` | Substantially `INDEPENDENTLY_REDISCOVERED` | C1/C4 directly match historical integrity and partial currentization in 02/04. C2/C6 match succession, fission/merge, ID-removal, and bounded lineage in 04/05. C5 matches the local-success/global-obstruction results reported for LPCW and CCP. C3 matches the continuous-change/refinement pressure that 04 identifies and 05 says the current six have not natively covered. |
| 6. Failure/falsification conditions | `UNCHANGED` | Mixed | Alpha-renaming, translator mutation, refinement, anti-globalization, and anti-unfalsifiability pressures appear in 02–04. B1’s exact matched-snapshot descent failure, explicit timeout discipline, and `OUT_OF_MODEL` abandonment rule are not specified in the four artifacts. |
| 7. Limitations | `UNCHANGED` and strengthened as caveats | `INDEPENDENTLY_REDISCOVERED` | 02 warns that ledgers and metalanguages can lack native consequence; 05 shows real corruption, absent source packets, missing replay, scale gaps, and no candidate-level human-control evidence. These reinforce B1’s authenticity, bookkeeping, computation, and human-review limitations rather than contradicting the model. |
| 8. Self-critique | `UNCHANGED` | `INDEPENDENTLY_REDISCOVERED` | The risk that a graph merely encodes answers matches 02’s tooling/ledger and answer-encoding risks and 04’s native-consequence criterion. No reveal evidence shows B1 escapes that risk. |
| 9. Alternatives considered | `UNCHANGED` | `INDEPENDENTLY_REDISCOVERED` | 02–04 keep persistent whole, lineage, relation, process, constraint, contextual, continuous, interface, predictive, and portfolio explanations live, while explicitly leaving memory sufficiency and identity open. |
| 10. Theory contribution | `UNCHANGED AS A PROPOSAL` | `GENUINELY_NEW_RELATIVE_TO_02_05` in exact form | No artifact presents B1’s exact provenance-sensitive support/attack calculus plus decomposed continuity vector and externally governed aggregation rule. Individual ingredients overlap existing work, so the novelty claim is only about the exact synthesis. |
| 11. Testable/implementable contact | `UNCHANGED` | Mixed | The inconsistent-translator test independently matches reported gluing/coalition obstruction work. The indistinguishable-snapshot/different-provenance paired test and its explicit abandonment condition are not present in 02–05. They directly address 04’s ID-removal question and 05’s missing common test. |
| 12. What would change the conclusion | `UNCHANGED` | `INDEPENDENTLY_REDISCOVERED` as research discipline | 02 calls for discriminating experiments rather than winner selection; 05 supplies no B1 execution or human resumption data. The revealed material therefore satisfies none of B1’s strengthening or abandonment conditions. |

## Unchanged

- The separation of historical warrant from resumption/authority licensing remains intact.
- The frozen assumptions, graph calculus, continuity profile, consequences, failures, and limitations require no textual or logical correction.
- Historical records and then-applicable meanings remain separate from later reinterpretation.
- Identity remains non-primitive, and succession, memory, behavior, commitment, and authority remain distinct claims.
- Missing, corrupt, disputed, undefined, and resource-unresolved evidence remain non-equivalent.
- Local compatibility still does not justify an unsupported global account.
- B1 remains one candidate worldview, not a project ontology or mandatory graph architecture.

## Changed

No frozen proposition is substantively changed.

The reveal changes only the surrounding evidence assessment:

- The assumption that bounded proof paths will be human-usable is now explicitly marked `NOT_DEMONSTRATED` because 05 finds no current-six candidate-level evidence for human familiarity, control, or sovereignty.
- Confidence that a proof ledger alone is sufficient is not increased; 02 and 04 make native derivation a mandatory pressure, and B1-T has not been executed.
- Source authenticity becomes a more concrete external dependency because 05 documents corrupt, absent, and non-replayable source material. This was already inside B1’s limitation boundary.

These are evidential qualifications, not edits to the freeze.

## Rejected

No frozen B1 claim is rejected by 02–05.

The following possible overreadings are rejected:

- B1 is not Owner-confirmed ontology.
- The relation-heavy graph is not a universal graph mandate.
- Overlap with current concepts is not proof of truth or model admission.
- A proof ledger without successful native replay is not sufficient.
- B1’s claim that the persona is not a single enduring object must remain a candidate commitment because persistent-changing-whole accounts remain live.

## Independently rediscovered

B1 independently reproduced the following before reveal:

- current meaning may change without overwriting historical meaning;
- unknown, disputed, undefined, alternative, and not-proven states must not collapse;
- stable IDs and current snapshots do not prove continuity;
- continuance, succession, memory, lineage, behavior, and authority should not be equated;
- branch, merge, fission, and memory exchange license bounded lineage claims rather than identity;
- global state/time are optional and require justification;
- local pairwise agreement can coexist with global obstruction;
- schema translation can be exact, multivalued, or unavailable, with consequences propagated;
- sampling and threshold choices can manufacture apparent events;
- project vocabulary is irrelevant under structural relabeling;
- human-side authority must remain distinct from model-generated claims;
- a storage system or fluent metalanguage needs a non-trivial native consequence.

The overlap is strongest with 02’s working assumptions and research questions, 03’s continuance/succession and authority distinctions, 04’s historical-integrity/non-closure/context maps, and 05’s LPCW/CCP/TRCC/WLRF scope summaries.

## Genuinely new relative to artifacts 02–05

The following exact mechanisms or tests were not found in the four reveal artifacts:

- the evidential claim tuple with independent supporting and opposing proof paths;
- the exact four evidential statuses generated from that support/attack pair, plus a separate computation-timeout state;
- the five-axis continuity profile and the ban on scalar aggregation without an externally supplied decision rule;
- sourced authorization edges inside the same audit structure as descent and interpretation claims;
- a merge defined as tagged record union plus explicit reconciliation claims;
- the paired test of snapshot-indistinguishable candidates with different derivation evidence;
- the explicit rule that repeated representation-family misses return `OUT_OF_MODEL` and trigger redesign or abandonment;
- the exact combination of evidence provenance, semantic versioning, translator obstruction, continuous-sampling caution, and authority into one calculus.

These are “new” only relative to the text of 02–05. Missing ARM-B/ARM-C sources and absent exact candidate inputs prevent a broader novelty claim.

## Basis and source caveats

- Artifact 02 is source-derived with explicit interpretation and is `NON_NORMATIVE`. Its current assumptions are revisable research premises, not validated truths.
- Artifact 03 states that raw primary verification is incomplete. “Owner explicit” often means explicit in normalized records, not verified raw transcript.
- Artifact 04 is a working research map, explicitly not an ontology or dictionary.
- Artifact 05 reports material provenance conflicts: ARM-A is strongest, ARM-B is corrupt/partial, ARM-C source provenance is not proven, and exact candidate/evaluator inputs are missing.
- The existing six cannot be treated as a complete comparison set; absent coverage is not inability.
- B1 was not run against the current-six probes, and no human-facing test in 02–05 validates its proof certificates or continuity claims.
- Similarity between B1 and revealed concepts may reflect common problem pressure. It does not establish correctness, owner acceptance, model admission, or priority.
- Novelty findings are bounded to the four permitted artifacts and cannot speak for unavailable archives, omitted raw sources, other agents’ work, or the wider literature.

## Reasons for the delta result

The reveal supplies strong conceptual convergence but no adverse observation against B1’s preregistered failures. Its closest overlaps are research questions and mechanisms, not a byte-identical prior model. At the same time, the source audit makes B1’s own authenticity and proof-ledger limitations more concrete. The rational update is therefore to retain the frozen core, strengthen its evidential caveats, and require native replay rather than claim validation from conceptual agreement.

## Crisp reveal verdict

`REVEAL_VERDICT_B1 = RETAIN_UNCHANGED_AS_NON_NORMATIVE_CANDIDATE`

`DELTA_PROFILE = SUBSTANTIAL_INDEPENDENT_REDISCOVERY + GENUINELY_NEW_EXACT_SYNTHESIS + NO_FROZEN_REJECTION + NO_VALIDATION`

B1 survives reveal without core revision. It independently anticipated much of the project’s problem map, while its support/attack calculus, decomposed continuity certificate, and matched-snapshot test remain distinct relative to 02–05. The reveal does not qualify, admit, validate, or establish B1 as a complete Persona theory.
