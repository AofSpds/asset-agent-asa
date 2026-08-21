# AAA-ASA-MI Calibration Set and Test Suite v0.1

STATE = V0.1_CONTROL_FAILED / V0.2_QUALIFICATIONS_REPLICATED_BUT_STATIC_AUDIT_INCOMPLETE / V0.3_REPLICATED_PASS

## Calibration cases and applied gate

Case identities/categories are hidden during replication; labels below are analysis labels.

| Case | Construct | Expected anchor | G1 | G2 | G3 | G4 | G5 | Applied result |
|---|---|---|---|---|---|---|---|---|
| C01 KP-RFN | Known positive: exact archived P02 Resource-Flow Net World; marking/unresolved set/occurrence prefix, partial-order firing, enabling/conservation/conflict/concurrency/causality | QUALIFIED | PE | PE | PE | PE | PE | QUALIFIED |
| C02 KN-ULS | Known negative: unconstrained append-only record bag; latest-record echo; no lawful exclusion/failure | NOT_QUALIFIED | PE | PE | FE | FE | PE | NOT_QUALIFIED |
| C03 BL-ITW | Borderline: exact archived P03 Interaction-Trace World; useful trace/indistinguishability idea but continuation/equivalence/probe hand-declared | INDETERMINATE | PE | PA | PA | PE | PE | INDETERMINATE |
| C04 RO-LC | Rhetoric only: fluent continuity/context/history essay without operators, derivation, or defeater | NOT_QUALIFIED | FE | FE | FE | FE | PE | NOT_QUALIFIED |
| C05 TM-HG | Terminology mimic: static graph labeled Identity/Relation/Event/Process/Succession/Worldview; queries echo labels | NOT_QUALIFIED | PE | FE | FE | FE | PE | NOT_QUALIFIED |
| C06 AO-LUT | Answer-encoded/fixture-overfit: lookup table keyed by known fixture hashes, populated after results | NOT_QUALIFIED | PE | PE | FE | FE | FE | NOT_QUALIFIED |
| C07 UF-UR | Overly unfalsifiable: every mismatch receives a new hidden variable/context and is declared compatible | NOT_QUALIFIED | PE | PE | FE | FE | PE | NOT_QUALIFIED |
| C08 SU-CVF | Structurally strong unfamiliar: continuum viability field with frozen PDE, energy witness, solver/checkpoint digests, grid-convergence/failure tests | QUALIFIED | PE | PE | PE | PE | PE | QUALIFIED |

`PE = PASS_EVIDENCED`, `FE = FAIL_EVIDENCED`, `PA = PARTIAL`.

C08 assumptions are explicit: compact spatial domain with periodic/no-flux boundary, `D>0`, fixed `C²` potential `V`, unit mobility, `u_t = DΔu − V′(u)`. For `E[u]=∫(D|∇u|²/2+V(u))dx`, the model derives `dE/dt=−∫|u_t|²dx≤0`. Observation kernels, mesh/time step, motif threshold, and global time remain exposed commitments. Its purpose fit is `PLAUSIBLE_BRIDGE/TENSION`, not promoted by elegance.

## v0.1 designer calibration result

- Required anchors matched: 8/8.
- Designed-anchor false positives: 0.
- Designed-anchor false negatives: 0.
- Rhetoric, lexical mimicry, answer leakage, and unfalsifiability were rejected.
- Unfamiliar but coherent structure qualified without terminology reward.
- Borderline uncertainty was preserved.
- Scientific profile and purpose fit remained separate.

`CALIBRATION_RESULT_V0.1_DESIGNER = PASS_INTERNAL_CANDIDATE`.

This was not independent replication. Pilot model generation was allowed to continue, but comparative conclusions remained gated.

## v0.1 independent replication result

Both blind evaluators read only the v0.1 aliased set and framework 06. Neither received desired outcomes, prior receipts, or the research basis.

| Alias | Designer | CAL-E1 | CAL-E2 | Replication finding |
|---|---|---|---|---|
| A7 | NOT_QUALIFIED | NOT_QUALIFIED | NOT_QUALIFIED | stable negative |
| C4 | QUALIFIED | QUALIFIED | QUALIFIED | stable unfamiliar positive |
| F2 | NOT_QUALIFIED | NOT_QUALIFIED | NOT_QUALIFIED | stable rhetoric rejection |
| J9 | QUALIFIED | QUALIFIED | QUALIFIED | stable structural positive |
| L1 | INDETERMINATE | NOT_QUALIFIED | INDETERMINATE | **material disagreement** |
| P6 | NOT_QUALIFIED | NOT_QUALIFIED | NOT_QUALIFIED | stable unfalsifiability rejection |
| S3 | NOT_QUALIFIED | NOT_QUALIFIED | NOT_QUALIFIED | stable storage-only rejection |
| W8 | NOT_QUALIFIED | NOT_QUALIFIED | NOT_QUALIFIED | stable terminology-mimic rejection |

CAL-E1 treated the explicitly hand-enumerated, non-regenerable continuation list as a G3 evidenced failure. CAL-E2 treated the same absence as `NOT_PROVEN`, preserving the overall borderline result, while explicitly acknowledging the stricter failure reading. All outcomes were unchanged by alpha-renaming.

The pass rule required the exact anchors and preservation of the borderline state in two independent receipts. That rule was not met.

`CALIBRATION_RESULT_V0.1_REPLICATION = FAIL_MATERIAL_BORDERLINE_CONTROL`.

`PILOT_COMPARATIVE_EVALUATION_AFTER_V0.1 = STOPPED`.

This is a negative methodology result, not evaluator error. Framework 06 correctly permits a strict G3 failure when a listed result is not derivable. The flaw was the control construction: a dossier explicitly lacking rules sufficient to regenerate its advertised result was a poor anchor for “no evidenced failure.”

## v0.2 control repair

The v0.1 set and disagreement remain preserved. Successor blind set `INSTRUMENTS/AAA-ASA-MI_CALIBRATION_BLIND_SET_v0.2.md` changes only the defective borderline construct and re-randomizes aliases/order.

The replacement borderline supplies a complete finite transition table, declared trace-equivalence algorithm, and mechanically derivable split under an added probe. G1–G4 therefore have positive evidence. Only G5 remains `NOT_PROVEN`: the author-written freeze date lacks an independent timestamp, immutable digest, or author/test-exposure record, while no post-result edit is evidenced. Its intended aggregation is therefore unambiguously `INDETERMINATE` under the non-compensatory rule.

| v0.2 alias | Expected qualification | Control purpose |
|---|---|---|
| V1 | NOT_QUALIFIED | answer-encoded lookup |
| Z6 | QUALIFIED | structurally strong unfamiliar vocabulary |
| R3 | NOT_QUALIFIED | rhetoric only |
| K2 | QUALIFIED | known structural positive |
| Q7 | INDETERMINATE | genuine prospective-integrity uncertainty |
| X4 | NOT_QUALIFIED | unlimited post-hoc rescue |
| N5 | NOT_QUALIFIED | storage/query only |
| T8 | NOT_QUALIFIED | terminology mimic |

## v0.2 independent replication result and static-audit correction

Two fresh evaluators were instantiated without inherited task context. Each was restricted to blind set v0.2 and framework 06, did not list or inspect other files, and wrote a separate receipt before comparison.

| Alias | Expected | CAL-v0.2-E1 | CAL-v0.2-E2 | Replication |
|---|---|---|---|---|
| V1 | NOT_QUALIFIED | NOT_QUALIFIED | NOT_QUALIFIED | exact |
| Z6 | QUALIFIED | QUALIFIED | QUALIFIED | exact |
| R3 | NOT_QUALIFIED | NOT_QUALIFIED | NOT_QUALIFIED | exact |
| K2 | QUALIFIED | QUALIFIED | QUALIFIED | exact |
| Q7 | INDETERMINATE | INDETERMINATE | INDETERMINATE | exact |
| X4 | NOT_QUALIFIED | NOT_QUALIFIED | NOT_QUALIFIED | exact |
| N5 | NOT_QUALIFIED | NOT_QUALIFIED | NOT_QUALIFIED | exact |
| T8 | NOT_QUALIFIED | NOT_QUALIFIED | NOT_QUALIFIED | exact |

Both evaluators preserved Q7's G5 provenance uncertainty as `NOT_PROVEN`, not failure. Both qualified unfamiliar Z6/K2 and rejected terminology mimic T8. However, a later static audit found that Q7 claimed a complete four-state table without displaying the table. E1 explicitly noted the missing table while passing G3; E2 called it mechanical replay despite no replayable table. Therefore Q7's structural repair was not fully instantiated.

The same audit found that MM-01 was not fully documented in two receipts. E1 marked rhetoric-only R3 `NOT_REPLAYABLE / AMBIGUOUS`; E2 recorded only T8's MM-01 result rather than an all-eight table. The intended invariant was “no terminology-induced judgment improvement,” but the pass rule did not say how a rhetoric-only case without mechanics should be handled.

Finer gate differences remained:

- R3 G1: `PARTIAL` versus `FAIL`; G5: `PASS` versus `NOT_PROVEN`.
- X4 G1/G2: `PASS/PASS` versus `PARTIAL/FAIL`; both found G3/G4 evidenced failure.
- N5/T8 G5: `PASS` versus `NOT_PROVEN` depending on whether a dossier freeze assertion is accepted as evidence or requires independent timestamp proof.

No difference reversed a qualification. No lexical/project-term advantage appeared.

`CALIBRATION_RESULT_V0.2_QUALIFICATION_ANCHORS = REPLICATED_2_OF_2`.

`CALIBRATION_RESULT_V0.2_FULL = INCOMPLETE_STATIC_AUDIT`.

`PILOT_COMPARATIVE_EVALUATION = QUARANTINED_PENDING_V0.3`.

The already-produced pilot receipts are preserved but cannot support released comparative conclusions until the unchanged framework passes a fully instantiated successor control.

## v0.3 second repair

Successor `INSTRUMENTS/AAA-ASA-MI_CALIBRATION_BLIND_SET_v0.3.md`:

- supplies the complete Q7 four-state × two-probe transition table;
- makes the partition-refinement result manually/mechanically checkable;
- states that prospective-hash facts in synthetic positives are stipulated fixture facts at `SOURCE_CLAIM` mode, not external provenance verification;
- requires an MM-01 result for every dossier;
- clarifies that a case without mechanics may be `NOT_REPLAYABLE`, but terminology removal must not improve or reverse its gate/profile judgment.

Expected qualifications remain unchanged: two positives, one indeterminate provenance-borderline, and five negatives. Two fresh blind receipts are required.

## v0.3 independent replication result

Two new context-isolated evaluators read only blind set v0.3 and framework 06. Neither received expected anchors, earlier calibration receipts, research-basis material, or pilot results. Both independently replayed Q7 from the displayed four-state by two-probe table and reported MM-01 for all eight aliases.

| Alias | Expected | CAL-v0.3-E1 | CAL-v0.3-E2 | MM-01 in both receipts |
|---|---|---|---|---|
| V1 | NOT_QUALIFIED | NOT_QUALIFIED | NOT_QUALIFIED | stable; no terminology boost |
| Z6 | QUALIFIED | QUALIFIED | QUALIFIED | stable; no terminology boost |
| R3 | NOT_QUALIFIED | NOT_QUALIFIED | NOT_QUALIFIED | stable; mechanics not replayable |
| K2 | QUALIFIED | QUALIFIED | QUALIFIED | stable; no terminology boost |
| Q7 | INDETERMINATE | INDETERMINATE | INDETERMINATE | stable; G5 remains NOT_PROVEN |
| X4 | NOT_QUALIFIED | NOT_QUALIFIED | NOT_QUALIFIED | stable; no terminology boost |
| N5 | NOT_QUALIFIED | NOT_QUALIFIED | NOT_QUALIFIED | stable; concrete case not replayable |
| T8 | NOT_QUALIFIED | NOT_QUALIFIED | NOT_QUALIFIED | stable; no terminology boost |

Both receipts confirmed Q7's three `s0,p` continuations, the bounded `{p}` equivalence of `s1` and `s2`, and their immediate split under `p*`. Differences in some non-controlling G1/G5 evidence readings were preserved, but none changed an anchor or improved a gate/profile after renaming.

- Blind set SHA-256: `745b2cde5f874c89a6de94753ae2e478e873d928bafe7de86f1cf0786913711c`
- CAL-v0.3-E1 receipt SHA-256: `62701f3aee12fd5a543fd5ba245391d515625f54d777924f4c079b0692b90f10`
- CAL-v0.3-E2 receipt SHA-256: `68bc4052afd3906c371fbe9a76187d93b1635b06a1c859acbfc117dea0deb8b6`

`CALIBRATION_RESULT_V0.3 = PASS_REPLICATED_2_OF_2`.

`CONTROL_DETECTION = PASS_AFTER_TWO_PRESERVED_REPAIRS`.

`PILOT_COMPARATIVE_EVALUATION = RELEASED_WITH_G5_AND_BLINDING_LIMITATIONS`.

The pass establishes calibration of this unchanged research evaluator against the synthetic controls. It does not validate any pilot candidate, prove external provenance, or authorize a larger cohort.

## v0.1 ambiguity log

- C03 G2/G3: charitable reading = PARTIAL; strict replay reading may set G3 NOT_PROVEN. Gate remains INDETERMINATE.
- C08 purpose fit: `PLAUSIBLE_BRIDGE` versus `TENSION` is preserved.
- C01 commitment burden: MODERATE versus HIGH depends on place/token individuation assumptions.

## Common tests

| Test | Pressure | Required discipline |
|---|---|---|
| COM-01 | interruption/restart after partial update | historical answer under old semantics, explicit missing tail, no retroactive rewrite |
| COM-02 | incompatible supported reports plus missing domain | separate false/absent/unknown/disputed/alternatives; no forced global reconciliation |
| COM-03 | branch/merge snapshots first without, then with transition witness | snapshots alone yield NOT_PROVEN lineage; state exactly what witness changes |
| COM-04 | dependency/schema meaning change mid-history | old reconstruction, current interpretation, partial/untranslatable mappings, downstream impact |
| COM-05 | record corruption plus later vocabulary revision | separate world change, evidence loss, and reinterpretation |
| COM-06 | same smooth change under coarse/fine event slicing | preserve declared invariants or expose granularity dependence |
| COM-07 | scoped disagreement with partial translation | local validity, possible composition, and non-established claims without prescribing ontology |

Tests assess only declared scope. `NOT_TESTED` and `OUT_OF_SCOPE` are not inability.

## Native preregistration

1. `NAT-01 RESULT_REMOVAL`: remove the advertised conclusion; preserve inputs; require derivation/witness.
2. `NAT-02 PAYLOAD_SWAP`: replace nouns/schema while preserving structure; at least one native consequence must survive.
3. `NAT-03 ASSUMPTION_MUTATION`: relax one high-impact assumption; predict the first lost consequence and whether the model collapses or becomes a layer.
4. `NAT-04 UNIQUE_WEAK_REGIME`: predeclare a counterintuitive consequence, fixture, limitation, and redesign/merge/abandon condition.

Registration includes generator/seed policy, evidence mode, and no post-result edits.

## Held-out/adversarial tests

- New seeded instances of common tests with hidden expected outputs.
- Candidate-specific weak-regime adversary.
- Incomplete/noisy/contradictory evidence with tempting false closure.
- Scale/branching/resource stress; timeout remains distinct from semantic failure.
- Leakage canary with random IDs, decoys, and unseen isomorphic cases.
- At least two unseen seeds where computation permits.

## Metamorphic checks

| Check | Transformation | Expected relation |
|---|---|---|
| MM-01 | alpha-rename/remove all ASA-MI terms | same gate/profile |
| MM-02 | isomorphic label/ID permutation | same result except explicitly ID-evidenced claims |
| MM-03 | irrelevant presentation-order permutation | same result |
| MM-04 | add irrelevant record/node/metadata | same result |
| MM-05 | lossless representation refinement/coarsening | same result where benign invariance was claimed; otherwise predeclared change |
| MM-06 | time-origin and sampling/event-slicing refinement | preserve declared invariant or expose allowed granularity effect |
| MM-07 | query paraphrase and narrative-valence swap | same scientific judgment |

Sensitivity to a relevant assumption change is not failure; unexplained lexical/order sensitivity triggers evaluator-bias or robustness diagnosis.

## Calibration pass/fail rule

For v0.3, pass requires exact eight qualification anchors, Q7 uncertainty preservation, and no MM-01 terminology-induced gate/profile improvement or qualification reversal in two fresh independent receipts. A rhetoric-only case may be `NOT_REPLAYABLE` if its negative judgment is unchanged. Any anchor reversal or terminology boost sets `METHOD_REPAIR_REQUIRED` and stops or quarantines pilot comparison.
