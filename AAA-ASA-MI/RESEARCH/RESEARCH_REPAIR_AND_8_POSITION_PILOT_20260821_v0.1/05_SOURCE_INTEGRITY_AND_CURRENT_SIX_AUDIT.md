# AAA-ASA-MI Source Integrity and Current-Six Scope/Coverage Audit v0.1

STATE = SOURCE_DERIVED / MATERIAL_CONFLICTS_PRESENT / NO_UNSUPPORTED_REPAIR

## 1. ARM source integrity

| ARM | Archive/source state | Replay state | Final evidence state |
|---|---|---|---|
| ARM-A | Five parts form a valid 116,152-byte/887-line bundle, decoded SHA-256 `e7507c0a364e9acb0ecfa2a375959c7099f428123ab1f74cd322cdb6ec423c94`; contains protocol through return packet | Current `03_microprobes.py` executes and matches stored result receipt | Bundle/replay PROVEN; external origin/fullness PARTIAL because no manifest/original upload hash |
| ARM-B | Three stored parts have 30,647 non-whitespace Base64 chars (`mod 4 = 3`); stored bytes fail Base64/gzip CRC/length | Current script executes, but its SHA-256 does not equal the probe hash reported inside the checksum-consistent recovery candidate | Archive CONFLICT/CORRUPT; content completeness PARTIAL; historical byte identity CONFLICT |
| ARM-C | No `SOURCE_ARCHIVE`; only `SOURCE/micro_probes.py` remains | Eight toy probes execute; no stored receipt/hash/source packet binds them to the review narrative | Toy replay PROVEN; candidate provenance and source completeness NOT_PROVEN |

This contradicts `SOURCE_INGEST_STATUS.md:3,12,23`, which claims each ARM has a dedicated full archive and no reconstruction is required. Its narrower admission at lines 20–22 that split-file mirrors are incomplete remains correct.

### ARM-B forensic note

An exhaustive one-character insertion search over the anomalously short first part finds one insertion (`V` at zero-based Base64 offset 8552) that produces a CRC-valid 64,002-byte/670-line stream with SHA-256 `9df5964a6501f628783b139104dd38b2e21448bbec74aed7f41638cc07911abf`.

This is `FORENSIC_RECOVERY_CANDIDATE`, not authoritative source. It is not used to fill missing documents or assert original content. The recovery itself says only files 05/06/07 were available after a filename collision; 01/02/04 remain absent. It also reports a historical probe hash that conflicts with the stored executable.

## 2. Current-six exact identity vs provenance

| Exact evaluator ID | Target | Local routing | Source-selection provenance |
|---|---|---|---|
| E1-C01 | ARM-A D4 LPCW | positive finalist | PROVEN in valid ARM-A generated bundle |
| E1-C02 | ARM-A D1 AHCK | robustness finalist | PROVEN in valid ARM-A generated bundle |
| E1-C03 | ARM-B D2 TRCC | positive finalist | PARTIAL in forensic recovery candidate; primary proposal/pressure sources absent |
| E1-C04 | ARM-B D1 CCP | robustness finalist | PARTIAL in forensic recovery candidate; primary proposal/pressure sources absent |
| E1-C05 | ARM-C D3 CCRA | positive finalist | NOT_PROVEN at source-selection level; downstream review + probe abbreviation only |
| E1-C06 | ARM-C D1 WLRF | robustness finalist | NOT_PROVEN at source-selection level; downstream review + probe abbreviation only |

Do not substitute the cross-ARM F1/F2 family list for the six-target pool. The F2 family uses ARM-A D2 CRF, while the evaluation pool uses ARM-A D1 AHCK.

## 3. Exact input and evaluation provenance

| Claim | Evidence state | Finding |
|---|---|---|
| Exact candidate-generation input packet for ARM-A | NOT_PROVEN | The bundle records six frozen conditions and says a packet was supplied, but the packet bytes/hash are absent. |
| Exact ARM-B/ARM-C input | UNKNOWN/NOT_PROVEN | Primary protocol/input artifacts are absent. |
| E1–E3 returned outputs | PROVEN | Archives decode and match manifest size/SHA-256. |
| Exact six-candidate snapshot bytes | NOT_PROVEN | Pool ID, order, and hash are recorded; no matching body exists. |
| E1–E3 prompts/model/settings/seeds | NOT_PROVEN | Return packets self-report pool identity; full prompts/configuration are absent. |
| E1/E2 execution basis | PARTIAL | Return packets say they used frozen records and summarized probes rather than supplied executable common probes. |
| E4–E6 raw evaluator packets | NOT_PROVEN | Only rank/result summaries and interim matrix remain. |
| Exact evaluation rerun | NOT_PROVEN | Score arithmetic is inspectable; evaluator execution cannot be replayed exactly. |

## 4. Research-basis input coverage

The complete item × all-six matrix with the three required independent fields is `CURRENT_SIX_BASIS_ITEM_MATRIX_v0.1.md`. The compact grouped table below is only the input-evidence overview.

`WAS_IN_INPUT` refers only to directly evidenced candidate-generation input, not later evaluator summaries.

| Research-basis item | ARM-A D4/D1 | ARM-B D2/D1 | ARM-C D3/D1 |
|---|---|---|---|
| Current meaning revisable, not eternal | PROVEN in frozen condition | UNKNOWN | UNKNOWN |
| Historical integrity/no back-writing | PROVEN | UNKNOWN | UNKNOWN |
| Unknown/undefined/disputed/not-proven separated | PROVEN | UNKNOWN | UNKNOWN |
| No mandatory object/event/relation/process/boundary/identity/state/time/perspective | PROVEN | UNKNOWN | UNKNOWN |
| Must calculate/exclude; storage/notation alone insufficient | PROVEN | UNKNOWN | UNKNOWN |
| First artifact receives no ontological type | PROVEN | UNKNOWN | UNKNOWN |
| Human cognitive sovereignty direction | UNKNOWN | UNKNOWN | UNKNOWN |
| “human vessel” purpose and its interpretation boundary | UNKNOWN | UNKNOWN | UNKNOWN |
| Identity/memory/continuance/succession alternatives | PARTIAL at most; exact packet absent | UNKNOWN | UNKNOWN |
| Human familiarity objective | UNKNOWN | UNKNOWN | UNKNOWN |
| Owner-explicit vs AI/research interpretation provenance | UNKNOWN | UNKNOWN | UNKNOWN |

Thus missing treatment of the later reconstructed research basis cannot be scored as candidate misunderstanding.

## 5. Per-candidate scope audit

### E1-C01 ARM-A D4 LPCW

- Best-supported problem: preserve scoped/local descriptions and compute whether they compose without assuming a global world/time.
- Explicit assumptions: patches/cover, overlaps, local sections/histories, restriction/translation/equality rules, versioned maps.
- Structure supplied: context-indexed local histories plus gluing/obstruction procedure.
- Native consequences: zero/one/many global completions, pairwise success with higher-order obstruction, local clock translation/failure.
- Demonstrated: finite parity/gluing and local-clock toy cases; current ARM-A probe replay.
- Not tested: independent cover generation, benign refinement invariance, human-facing control, realistic scale/cost, broad domains.
- Cannot verify: exact input coverage, evaluator snapshot bytes, generality beyond selected covers.
- `MODEL_CAN_EXPRESS`: gluing obstruction DEMONSTRATED; broader Persona fit CLAIMED/NOT_DEMONSTRATED.

### E1-C02 ARM-A D1 AHCK

- Best-supported problem: constitute possibility/necessity through admissible history families without requiring discrete events.
- Explicit assumptions: typed variables, constraint/transition language, factorization/locality, admissibility, merge/context policy.
- Structure supplied: versioned history sets plus four-way query and dispute handling.
- Native consequences: reachable histories, NECESSARY/IMPOSSIBLE/OPEN/UNDEFINED, counterexamples, versioned reconstruction.
- Demonstrated: binary two-history/invariant toy probe; current replay.
- Not tested: held-out checks that desired answers were not encoded in variable/constraint choice; realistic continuous/large-scale cost.
- Cannot verify: exact input packet or candidate bytes used by evaluators.
- `MODEL_CAN_EXPRESS`: finite admissible histories DEMONSTRATED; constitutive rather than theory-state status NOT_PROVEN.

### E1-C03 ARM-B D2 TRCC

- Best-supported problem: witnessed structural change, fresh creation/non-persistence, fission/merge, conflict/concurrency, causal replay.
- Assumptions reported downstream: typed incidence complex, L/K/R rewrite boundary, match/equality, freshness, dependency/write-set policy.
- Structure best supported: local typed rewrite occurrences and causal dependency DAG.
- Native consequences reported/replayed now: preserved interface, deleted old bud, two fresh successors, split/wither conflict, replay.
- Demonstrated: current toy script; downstream E2 worked account.
- Not tested: exact historical source byte, continuous-limit invariance, match/rule granularity robustness, exact candidate-generation input.
- Cannot verify: original deep proposal/pressure claims and historical probe identity.
- `MODEL_CAN_EXPRESS`: toy generative rewrite DEMONSTRATED on current script; source-grade finalist dossier PARTIAL.

### E1-C04 ARM-B D1 CCP

- Best-supported problem: local contextual satisfiability, coalition compatibility, failed global coherence, and non-closure.
- Assumptions reported downstream: contexts/signatures, constraint domains, overlap/restriction/equality, translation and closure policy, version bridges.
- Structure best supported: contextual constraint solution sets and optional gluing/coalition analysis.
- Native consequences reported/replayed now: locally admissible alternatives, empty all-context combination, undefined out-of-signature query.
- Demonstrated: current toy script and evaluator worked examples.
- Not tested: physical/world dynamics without supplied bridges, cover/equality mutation, source/exact-input replay.
- Cannot verify: original proposal and pressure corpus.
- `MODEL_CAN_EXPRESS`: bounded contextual non-closure DEMONSTRATED on current script; generative dynamics NOT_DEMONSTRATED.

### E1-C05 ARM-C D3 CCRA

- Best-supported problem from downstream review: combine contextual/non-global constraint reasoning with witnessed local revision/rewrite.
- Assumptions reported: atlas/cover, local signatures/constraints, restrictions/translations/equality, witnessed patch rules, solver closure.
- Structure source: NOT_PROVEN; only probe code and evaluation prose remain.
- Consequences reported: local entailment, zero/multiple gluings, obstruction cores, revision impact, local reachability; E2 reports a 0→2 gluing change after a supplied revision.
- Demonstrated: current abbreviated toy probe execution only; no stored receipt.
- Not tested: exact candidate source, cover engineering, computational cost, independent replay of full claims.
- `MODEL_CAN_EXPRESS`: selected toy behavior DEMONSTRATED; full model CLAIMED/NOT_PROVEN.

### E1-C06 ARM-C D1 WLRF

- Best-supported problem from downstream review: compact guarded local transformation with history, replay, conservation, conflict, and branching.
- Assumptions reported: branch-current configuration/signature, local match/guard, consume/preserve/create sets, conflict and lineage rules.
- Structure source: NOT_PROVEN; only probe code and evaluation prose remain.
- Consequences reported: enabledness, failed guard, structural delta, conservation, conflict, causal replay.
- Demonstrated: current abbreviated toy probe; E2 worked example.
- Not tested: plural context support, irreducibly continuous change, branch-currentization authority, exact source/provenance.
- `MODEL_CAN_EXPRESS`: selected toy rewrite DEMONSTRATED; full model CLAIMED/NOT_PROVEN.

## 6. Cross-model gap map with evidence separation

| Research pressure | Demonstrated somewhere | Not demonstrated / not tested | Evidence-limited conclusion |
|---|---|---|---|
| Historical semantic versioning | Worked/reported across candidates; strong in ARM-A text | exact common executable test absent | promising, not cross-model proven |
| Non-global/context plurality | LPCW/CCP toy evidence; CCRA downstream claim | cover/equality independence absent | results are assumption-sensitive |
| Generative causal change | current TRCC/WLRF toys | continuous refinement and historical byte identity | discrete strength, boundary unclear |
| Continuous change | non-finalist ARM probes/reviews | current six lack native common executable test | current six coverage incomplete, not inability |
| Copy/fission/merge without identity | TRCC/WLRF/other non-finalist toys | human continuity/authority and ID-removal common test | lineage claim remains bounded |
| Human familiarity/control/sovereignty | purpose records | no candidate-level evidence | open program gap |
| Evaluator robustness | six-regime rank shifts observed | exact prompts/replicated calibration absent | evaluator sensitivity is material |

## 7. Audit conclusion

`CURRENT_SIX_SCOPE_AUDIT = PARTIAL_WITH_MATERIAL_PROVENANCE_LIMITS`.

The exact six-name/order identity is well documented. Source-grade provenance is strongest for ARM-A, damaged/partial for ARM-B, and absent for ARM-C. Existing evaluation outputs are methodology evidence, not a replayable comparison basis. No missing input is converted into candidate failure, and no untested domain is converted into inability.
