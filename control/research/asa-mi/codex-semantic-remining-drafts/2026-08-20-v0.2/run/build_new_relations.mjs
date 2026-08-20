import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const out = path.join(root, "control/research/asa-mi/codex-semantic-remining-drafts/2026-08-20-v0.2/crosswalk/new_relation_candidates.jsonl");
const relations = [];
const add = (from, type, to, rationale, certainty = "MEDIUM") => relations.push({ from, type, to, rationale, certainty });

add("V02-LIVE-NEW-0001", "CONSTRAINS", "CX-LIVE-PLANNING-0013", "The recovered prose limits atomic decomposition when it destroys context or meaning.", "HIGH");
for (let n = 20; n <= 26; n += 1) add("V02-LIVE-NEW-0002", "CONSTRAINS", `CX-LIVE-PLANNING-${String(n).padStart(4, "0")}`, "The register-wide rule prevents a prior-art reference from implying adoption, semantic equivalence, endorsement, or Authority.", "HIGH");
add("V02-LIVE-NEW-0003", "CONSTRAINS", "CX-LIVE-BRAINSTORM-0010", "Persona-object lifecycle policy must not be inferred from research-history preservation policy.", "HIGH");
add("V02-LIVE-NEW-0004", "REFINES", "CX-LIVE-BRAINSTORM-0038", "Each possible Status dimension receives an independent realization classification rather than membership by bundle.", "HIGH");
add("V02-LIVE-NEW-0005", "REFINES", "CX-LIVE-BRAINSTORM-0004", "Quantification intent retains UNKNOWN as distinct from numeric zero.", "HIGH");
add("V02-LIVE-NEW-0006", "REFINES", "CX-LIVE-BRAINSTORM-0004", "Quantification intent retains UNOBSERVED as distinct from ABSENT.", "HIGH");

const counterLinks = [
  ["CX-SRC-SRC-MI0-0001", "ALTERNATIVE_TO", "Identity may be relational rather than identical to Memory."],
  ["CX-SRC-SRC-WP2-0005", "CONSTRAINS", "External recognition may be constitutive for governed relational identity."],
  ["CX-SRC-META-0016", "REFINES", "Memory danger can arise from faithful preservation of harmful state."],
  ["CX-SRC-SRC-MI1-0001", "TENSION_WITH", "Operational continuity need not settle first-person persistence."],
  ["CX-LIVE-PLANNING-0006", "WEAKENS", "Sincere recognition of fabricated history is a counterexample to recognition sufficiency."],
  ["CX-SRC-SRC-MI1-0018", "ALTERNATIVE_TO", "Reconstruction-policy invariance may explain continuity better than content invariance."],
  ["CX-SRC-SRC-R1-0042", "REFINES", "Divergent dimensions may resist aggregation to one same-Persona fact."],
  ["CX-LIVE-BRAINSTORM-0027", "REFINES", "Memory membership may be relative to the current operation and Context."],
  ["CX-LIVE-BRAINSTORM-0050", "CONSTRAINS", "Accessible data needs causal sensitivity before counting as operative Memory."],
  ["CX-SRC-SOURCE-NORMALIZED-SET-0008", "REFINES", "Implicit learned weights may realize procedural/dispositional Memory."],
  ["CX-SRC-SRC-MI1-0010", "REFINES", "Memory capability may be distributed across state, tools, references, and relations."],
  ["CX-LIVE-BRAINSTORM-0038", "ALTERNATIVE_TO", "Transition and authority categories challenge exhaustive two-bucket classification."],
  ["CX-LIVE-BRAINSTORM-0029", "WEAKENS", "A Current Status view is necessarily an editorial, potentially lossy projection."],
  ["CX-SRC-SRC-R2-0028", "ALTERNATIVE_TO", "Fresh derivation may outperform a stale persisted standpoint under context change."],
  ["CX-LIVE-BRAINSTORM-0026", "WEAKENS", "Explicit self-models may harm adaptation and fidelity."],
  ["CX-SRC-SRC-MI1-0018", "TENSION_WITH", "A functional Memory definition may absorb retriever and compiler mechanisms."],
  ["CX-SRC-SRC-MI1-0028", "WEAKENS", "Portable state can remain behaviorally provider-dependent."],
  ["CX-SRC-SRC-WP1-0001", "STRENGTHENS", "Calibrated heterogeneous implementations may preserve Persona mappings."],
  ["CX-SRC-SRC-R1-0019", "REFINES", "Shared priors and objectives may drive convergence more than shared evidence."],
  ["CX-SRC-SRC-MI1-0010", "WEAKENS", "Separate local Memory does not prevent convergence under common selection pressure."],
  ["CX-SRC-SRC-R3-0020", "WEAKENS", "Full influence deletion may be empirically undecidable without a counterfactual."],
  ["CX-SRC-SRC-MI0-SRC-MI1-0003", "WEAKENS", "Formal separation can coexist with de facto power through agenda and framing."],
  ["CX-SRC-SRC-MI1-0024", "REFINES", "Both fission successors may continue genuinely while neither is numerically identical."],
  ["CX-SRC-SRC-MI1-0026", "ALTERNATIVE_TO", "A nontrivial merge may create successor C rather than reconcile identity."],
  ["CX-LIVE-BRAINSTORM-0041", "WEAKENS", "Human sameness judgments may track narrative fluency rather than causal fidelity."],
  ["CX-SRC-SRC-MI1-0028", "ALTERNATIVE_TO", "External counterparties and artifacts may restore some continuity after internal loss."],
  ["CX-SRC-SRC-WP2-0008", "REFINES", "Factual event persistence and current ownership as my history are separate variables."],
];
counterLinks.forEach(([to, type, rationale], index) => add(`V02-INF-CH-${String(index + 1).padStart(3, "0")}`, type, to, rationale));

const experimentTargets = [6, 17, 16, 6, 17, 17, 10, 13, 14, 15, 19, 5, 21, 22, 24, 17, 2, 17, 18, 8, 9, 10, 26, 5, 12, 17, 8, 23];
experimentTargets.forEach((target, index) => add(`V02-INF-EXP-${String(index + 1).padStart(3, "0")}`, "TESTS", `V02-INF-CH-${String(target).padStart(3, "0")}`, "The experiment manipulates a variable intended to discriminate the linked counterhypothesis from its target.", "HIGH"));

const modelTargets = [1, 8, 16, 21, 5, 7, 16, 13, 18, 21, 22, 11, 23, 24];
modelTargets.forEach((target, index) => add(`V02-INF-MODEL-${String(index + 1).padStart(3, "0")}`, "MAPS_TO", `V02-INF-CH-${String(target).padStart(3, "0")}`, "The model candidate provides an explicit representation for the linked counterhypothesis."));

add("V02-INF-MODEL-002", "ALTERNATIVE_TO", "V02-INF-MODEL-003", "Typed membership categories and a functional operator offer competing ways to bound Memory.");
add("V02-INF-MODEL-013", "COEXISTS_WITH", "V02-INF-MODEL-014", "Branching succession and merge-as-new-successor can share one lineage framework.", "HIGH");
add("V02-INF-MODEL-005", "CONSTRAINS", "V02-INF-MODEL-001", "Recognition and attestation restrict which relational graph paths support continuity.");
add("V02-INF-MODEL-006", "CONSTRAINS", "V02-INF-MODEL-009", "Operational equivalence must report separate continuity dimensions rather than one hidden scalar.");
add("V02-INF-MODEL-010", "TENSION_WITH", "V02-INF-MODEL-004", "Immutable evidence aids causal audit but conflicts with complete erasure and privacy requirements.");

const records = relations.map((r, index) => ({
  RELATION_ID: `V02-REL-${String(index + 1).padStart(4, "0")}`,
  FROM_OBJECT_ID: r.from,
  RELATION_TYPE: r.type,
  TO_OBJECT_ID: r.to,
  RELATION_CERTAINTY: r.certainty,
  ENDPOINT_OBJECT_STATUS: "SEPARATELY_RECORDED_NOT_IMPLIED_BY_RELATION_CERTAINTY",
  RATIONALE: r.rationale,
  SOURCE_LEVEL: "V02_RELATION_CANDIDATE",
  OWNER_POSITION_STATE: "NOT_OWNER_POSITION",
}));
fs.writeFileSync(out, `${records.map((record) => JSON.stringify(record)).join("\n")}\n`, "utf8");
console.log(`WROTE=${records.length}`);
