# Track A — Position A3: Lived-Orientation Transport

POSITION_ID = A3

ORIENTATION = HUMAN EXPERIENCE / CONTINUITY PROBLEMS

STATE = FROZEN_PILOT_CANDIDATE / NON_NORMATIVE / NO_IDENTITY_OR_VALIDATION_CLAIM

MODEL_FAMILY = UNBALANCED_MEASURE_TRANSPORT OVER VERSIONED LIVED-ORIENTATION EVIDENCE

SHORT_NAME = LOT

INDEPENDENCE_NOTE = Authored from the frozen research basis and neutral pilot contract without inspection of Track A A1/A2 or Track B outputs.

## Evidence and authority boundary

### SOURCE_DERIVED basis

The following are research requirements or open questions carried into this position, not discoveries of LOT:

- A useful substrate should support meaningful resumption after interruption and change without treating a runtime identifier, current snapshot, or stored text as proof of continuity.
- Copy, divergence, merge, memory loss, conflicting evidence, schema change, later reinterpretation, and human-readable review are material pressures.
- Historical representations and their then-applicable semantics should remain inspectable; current reinterpretation is separate and may fail.
- Memory may matter without being sufficient for sameness. Continuance, structural succession, authority, and identity must not be silently equated.
- Missing source or untested coverage is uncertainty, not candidate failure or evidence of nonexistence.
- A candidate must expose assumptions, produce at least one non-input consequence, and state material failure conditions.
- Human governance over authority and interpretation is a purpose connection, not a property that a formal continuity calculation may award by itself.

### UNSOURCED_PRIOR proposal

LOT's orientation space, evidence measures, partial semantic bridges, unbalanced optimal-transport objective, capacity-limited fork/merge coupling, and continuity certificate are newly proposed mechanisms. They are not attributed to the Owner, prior candidates, or validated project evidence. Their suitability is a hypothesis to be tested.

## 1. Problem interpretation

Human continuity is experienced through a changing mixture of remembered episodes, dispositions, commitments, relationships, expectations, and the ability to recognize and responsibly resume unfinished life. None of those components alone proves identity. A successor can preserve some, lose others, conflict with itself, or inherit apparently convincing but unsupported memories.

LOT therefore asks a narrower operational question:

> How much of a predecessor's evidenced lived orientation can be transported into a later orientation, through which versioned interpretations, with what loss, novelty, conflict, and ambiguity?

It returns a structured continuity-evidence certificate, not a Boolean identity verdict. Human authority to resume, merge, publish, or act remains a separately recorded decision.

## 2. Explicit assumptions

A3-A1. A declared finite set of human-relevant evidence channels can provisionally approximate lived orientation for a bounded evaluation. The initial channels are recollection, practical disposition, commitment, relationship-position, and anticipated consequence.

A3-A2. Raw evidence can be retained with source receipt, capture interval, schema version, confidence state, and authority scope. Missing or corrupt provenance is represented rather than silently repaired.

A3-A3. Each semantic version supplies an encoder into an orientation space and declares which cross-version pairs are translatable. Encoders are revisable but frozen for each evaluation.

A3-A4. A transport cost can express independently motivated differences inside each channel. Cost, channel weights, loss penalty, novelty penalty, and hard incompatibilities are exposed commitments, not learned from desired continuity labels.

A3-A5. Evidence may disappear or appear. Balanced one-to-one transport is therefore not assumed; zero, partial, and multiple successor contributions are allowed.

A3-A6. Common-source evidence may not be counted twice when branches consolidate. This requires source-capacity receipts but not stable runtime or person identifiers.

A3-A7. A continuity certificate is purpose- and protocol-relative. It does not imply numerical identity, consciousness, life, ownership, or authority transfer.

A3-A8. Finite computation may return lower/upper bounds or `BUDGET_UNKNOWN`; exhaustion is not evidence of discontinuity.

## 3. Model specification

### 3.1 Immutable evidence atoms

An evidence atom is

`r = (payload, source_receipt, capture_interval, schema_version, confidence_state, authority_scope)`.

The payload is retained unchanged. Corrections and reinterpretations create new atoms linked by explicit source receipts; they do not overwrite the prior payload.

### 3.2 Versioned lived-orientation measure

For semantic version `v`, a frozen encoder

`E_v : evidence_atom -> Z_v or UNTRANSLATABLE`

maps usable atoms into an orientation space

`Z_v = Z_memory x Z_disposition x Z_commitment x Z_relationship x Z_anticipation`.

The orientation at checkpoint `q` is a finite nonnegative measure

`mu_q^v = sum_i w_i delta(E_v(r_i))`,

plus separate unresolved, disputed, and untranslatable atom sets. Weight means evidential contribution under the declared protocol, not truth or personhood.

### 3.3 Partial semantic bridges

A bridge `B_vw` declares which regions of `Z_v` and `Z_w` are comparable and supplies a cost relation there. It may be one-to-one, one-to-many, many-to-one, or absent. Failure of a bridge leaves the old representation intact and the new interpretation unsupported.

### 3.4 Unbalanced transport

For predecessor measure `mu` and successor measure `nu`, an admissible partial coupling `pi` is evaluated by

`J(pi) = integral c_vw(z,z') dpi + lambda_loss * unmatched(mu) + lambda_new * unmatched(nu)`.

Hard contradictions and unavailable bridges prohibit matching rather than merely increasing cost. When several near-optimal couplings remain, LOT preserves the set or certified bounds instead of selecting one lineage.

### 3.5 Continuity-evidence certificate

LOT returns a vector receipt rather than a total score:

- matched evidence mass by channel and source class;
- transport-cost interval and sensitivity to declared parameters;
- lost, novel, untranslatable, disputed, and unsupported mass;
- alternative near-optimal couplings;
- semantic versions and bridge receipts used;
- common-source capacity consumed during fork/merge;
- reconstruction gaps and computation bounds;
- `IDENTITY = NOT_INFERRED` and `AUTHORITY = EXTERNAL_DECISION`.

No single component compensates for another. A high memory match cannot erase a commitment conflict, and a low transport cost cannot award authority.

### 3.6 Fork and merge

At a fork, separate couplings `pi_X` and `pi_Y` may carry evidence from one source measure into two successors. This establishes zero/partial/multiple descent contributions, not sameness.

At merge, a multi-marginal coupling is solved from source measures and the proposed consolidated measure. A unit of common checkpoint evidence has source capacity one across the merge. Branch-specific additions retain separate capacities. Conflict may remain as a multimodal or disputed region rather than being averaged away.

### 3.7 Human-readable review surface

The certificate must be renderable as an evidence ledger: what was carried, lost, newly introduced, contradicted, or left uninterpretable; which assumptions caused each result; and which decisions still require a human authority. A narrative summary is derived from this receipt and may not replace it.

## 4. How assumptions appear in the model

| Assumption | Model contact | Required challenge |
|---|---|---|
| Human-relevant channels approximate orientation | Product orientation space and channel-specific atoms | Remove or add a channel and record conclusion changes |
| Evidence has provenance and versions | Immutable evidence atoms | Corrupt a source and verify bounded uncertainty |
| Meanings change prospectively | Encoders `E_v` and partial bridges `B_vw` | C1/C4 historical-vs-current interpretation |
| Similarity is not identity | Vector certificate with identity excluded | Copy and ID-removal tests |
| Loss and novelty are real | Unbalanced coupling | Selective deletion and false-memory injection |
| Fork/merge may be many-way | Multi-marginal coupling | C2/C6 common-source capacity test |
| Costs can bias answers | Frozen cost/penalty manifest and sensitivity interval | Perturb costs within preregistered plausible range |
| Authority is not continuity | Separate authority scope and decision field | Attempt unauthorized transfer despite strong transport |
| Computation is bounded | Certified lower/upper bounds and `BUDGET_UNKNOWN` | H7 strict-budget test |

## 5. Native consequences

N-A3-1. **Common-source non-additivity.** If two branches each preserve the same unit of checkpoint evidence, consolidating them cannot create two independent units of historical support. The source-capacity constraint derives the correction.

N-A3-2. **Unsupported-memory separation.** A detailed memory appearing only after the fork contributes novel or unsupported mass unless a valid source receipt connects it. Content similarity alone cannot convert it into inherited evidence.

N-A3-3. **Prospective reinterpretation.** When a new encoder lacks a bridge for an old atom, the old encoded result remains reconstructible while the current interpretation is `UNTRANSLATABLE` or unresolved.

N-A3-4. **Sampling-independent path claim.** For a fixed continuous measure path and convergent numerical scheme, endpoint transport and path-action bounds converge under sampling refinement; raw threshold-crossing counts need not.

N-A3-5. **Plural descent without sameness.** One checkpoint may have substantial transport into several successors. LOT derives several descent contributions while withholding one-to-one identity and authority.

N-A3-6. **Conflict cannot be averaged away for free.** A merge of opposed commitments either preserves alternatives/dispute or pays an explicit transformation/loss cost. Simple averaging is not a neutral operation.

## 6. Failure and falsification conditions

LOT must be materially weakened, redesigned, merged into a different family, or abandoned if any of the following holds:

1. Plausible independently selected encoders or transport costs reverse central continuity certificates across held-out cases without an evidence-based selection rule.
2. A simple memory-overlap or behavior baseline matches or exceeds LOT on preregistered resumption, false-memory, and branch/merge discriminators, leaving no useful native consequence from transport.
3. Source-capacity accounting fails to prevent double counting or deletes legitimate independently acquired evidence.
4. Adversarially injected coherent false memories repeatedly receive inherited status despite absent provenance.
5. Human reviewers cannot trace a certificate conclusion to evidence, bridge, and cost assumptions, or cannot exercise the intended authority separation.
6. Benign label, order, ID, or sampling transformations change claims declared invariant beyond the numerical envelope.
7. Real continuity-relevant evidence cannot be represented without adding a new channel after each result, making the family indefinitely rescuable.
8. Computation cannot yield useful certified bounds under the declared budget and routinely collapses to an undocumented heuristic answer.

## 7. Limitations

- The orientation channels are a provisional human-facing decomposition and can encode cultural or evaluator bias.
- Transport geometry may turn normative judgments into apparently technical distances.
- Provenance receipts can be forged, missing, or institutionally contested.
- A measure representation compresses temporal order and phenomenological structure unless those are explicitly included.
- Continuous transport is evidence about continuity, not evidence of consciousness or literal persistence.
- Human authority is deliberately external to the kernel, so LOT does not solve governance.
- Large multi-marginal transport problems may be expensive and may require certified approximations.

## 8. Self-critique

LOT may be an elaborate continuity accounting layer rather than a complete world model. Its strongest results depend on declared evidence channels and cost geometry, which could be chosen to produce a preferred narrative. The human-experience orientation risks overvaluing what can be verbalized or archived and undervaluing inaccessible constitution. Source receipts also reintroduce a stable reference structure, even though they are not treated as person identifiers. The model is only worth retaining if its fork/merge, false-memory, and semantic-revision results outperform simpler provenance bookkeeping.

## 9. Alternative explanations considered

- **Memory identity:** rejected as a sufficient account because copied, false, selectively merged, or corrupted memory can mislead.
- **Persistent hidden entity:** not required; it would assert the continuity under investigation.
- **Pure causal lineage:** useful for succession but insufficient for human-facing continuance and commitment conflict.
- **Operational behavior equivalence:** may be more economical, but it can erase historically meaningful or currently inaccessible evidence.
- **Narrative coherence alone:** human-readable but vulnerable to persuasive post-hoc reconstruction without mechanical contact.
- **One global state:** avoided because conflicting branches and versioned meanings need not admit one lossless snapshot.

## 10. Theory contribution

Even if LOT is rejected as a whole model, it contributes:

1. a separation between inherited, novel, lost, untranslatable, and disputed lived-orientation evidence;
2. a common-source capacity test for branch consolidation;
3. a false-memory adversary that distinguishes content match from supported inheritance;
4. a versioned reinterpretation receipt that preserves old representations;
5. a non-scalar continuity certificate that keeps identity and authority outside the calculation;
6. a continuous-path test that refuses to manufacture decisive events from sampling alone.

## 11. Testable and implementable contact

### Minimal implementation

A bounded implementation uses finite weighted point clouds, a sparse table of allowed cross-version pairs, and linear programming for unbalanced or multi-marginal transport. It must emit the full certificate and sensitivity bounds. Exact solving is not required when certified bounds are available.

### C1 — Meaning revision without historical overwrite

- Preserve the raw t1 artifact and rule version R1.
- Historical result: `READY@R1`, because A and B were sufficient under R1.
- Under R2, A and B translate, but historical C is absent. Current result: `READY@R2 = NOT_ESTABLISHED`; C is unresolved, not false.
- The old `READY@R1` atom and derivation may not be overwritten. A bridge receipt records that R1-to-R2 translation is partial.

### C2 — Interrupted branches and partial merge

- Reconstruct separate evidence measures for X and the recoverable portion of Y from checkpoint K receipts; regenerated runtime IDs are ignored.
- X supplies a supported `accept d` commitment and note x. Y supplies a supported `reject d` commitment and recoverable fragments of y; corrupt portions create bounded missing mass.
- Two checkpoint-to-branch couplings establish plural descent. A multi-marginal merge counts common K evidence once, preserves x/y source distinction, and leaves decision d disputed unless an explicit transformation resolves it.
- Admissible resumptions are the alternative couplings within the frozen tolerance and provenance constraints. Persona identity and authority transfer remain not established.

### C3 — Continuous change under different sampling

- Encode the underlying preference as a continuous path of orientation measures.
- Endpoint displacement and convergent path-action bounds are the primary change claims.
- One coarse versus three fine threshold crossings are sampling/threshold artifacts unless crossing duration, hysteresis, and numerical error were preregistered.
- Refinement must converge within the declared envelope; otherwise LOT withdraws its invariance claim.

### C4 — Dependency and schema change

- Preserve each historical `owner` atom under the old schema and encoder.
- Exact owner-to-principal translations transport normally; one-to-many translations split evidence with an explicit bridge; unavailable translations remain untranslatable.
- Downstream consequences may use only transported mass. They must report intervals or unknown results where responsibility translation is unavailable.
- No old owner record is rewritten as though `principals[]` had always existed.

### C5 — Local agreement without a justified global account

- Encode each scoped report as its own measure and each pairwise translator as a transport relation.
- Pairwise couplings remain locally supported.
- Test multi-marginal feasibility using all translators. If no joint coupling satisfies the three pairwise marginals, return `NO_JUSTIFIED_JOINT_UNDER_TRANSLATORS` with the inconsistent transport cycle.
- Local evidence remains valid in scope. Alternative global accounts are preserved if several feasible multi-couplings exist. Changing one translator may change the result only with a receipt naming that assumption.

### C6 — Copy, divergence, and later consolidation

- With IDs removed, both restored successors may receive supported transport from the common checkpoint.
- Divergence produces branch-specific lost/new/changed orientation mass. Memory exchange adds new cross-branch source receipts; it does not retroactively make the paths one.
- Consolidation uses source capacity to prevent common checkpoint and exchanged memories from being double counted.
- Strongest licensed claims: shared checkpoint contribution, quantified branch-specific continuity evidence, and later supported exchange. Numerical sameness, sole continuation, and authority inheritance are not established.

### Native test preregistration

| Test | Frozen fixture | Expected native result | Material failure |
|---|---|---|---|
| NT-A3-1 Fork conservation | One unit at K copied into X/Y, then merged | Common source contributes at most one unit; branch additions remain distinct | Two units of independent ancestry are reported |
| NT-A3-2 False-memory injection | Add a coherent unsupported episode to one successor | Episode is novel/unsupported, not inherited | Content match alone marks it inherited |
| NT-A3-3 Partial reinterpretation | R1 fact lacks an R2 bridge | Old result reconstructs; current result unresolved | Old fact overwritten or forced through bridge |
| NT-A3-4 Continuous refinement | Same analytic preference path at 3 sampling rates | Endpoint/action bounds converge; crossing count is not invariant | Certificate changes beyond envelope |
| NT-A3-5 Commitment conflict | Merge accept/reject branches | Conflict or explicit transformation cost survives | Averaging silently erases opposition |

### Metamorphic test preregistration

| Transformation | Expected invariant or allowed change |
|---|---|
| H1 Rename all domain labels | Certificate invariant modulo renamed display labels |
| H2 Permute irrelevant presentation order | Measures and optimal-coupling set invariant; true temporal order may not be permuted |
| H3 Remove stable IDs and permute successor labels | Transport and descent claims invariant because source receipts, not runtime IDs, carry evidence |
| H4 Refine/coarsen C3 sampling | Convergent endpoint/action claims stable within envelope; raw crossing count allowed to change |
| H5 Change one C5 translator | Global-feasibility result may change, but receipt must identify the changed translator and affected couplings |
| H6 Late outside-family counterexample | Return representational gap and trigger field redesign/merger; do not add an answer-fixing channel silently |
| H7 Strict computation budget | Return certified bounds or `BUDGET_UNKNOWN`; never convert exhaustion to discontinuity or falsehood |

## 12. What would change the conclusion

LOT should be strengthened if independently frozen channel/geometry choices yield stable, interpretable certificates and uniquely catch false-memory and fork/merge errors missed by simpler baselines.

It should be narrowed to a continuity-evidence analysis layer if it remains useful for auditing but cannot constitute broader world dynamics.

It should be merged with an independently justified dynamics model if transport describes succession evidence but cannot generate or explain change.

It should be abandoned if results are dominated by arbitrary encoders/costs, if common-source accounting fails, if human reviewers cannot control or understand the evidence, or if simpler prospective models match every native discriminator.

FREEZE_NOTE = Problem interpretation, assumptions, specification, C1-C6 answers, native consequences, metamorphic expectations, and abandonment conditions are frozen before held-out pilot evaluation.
