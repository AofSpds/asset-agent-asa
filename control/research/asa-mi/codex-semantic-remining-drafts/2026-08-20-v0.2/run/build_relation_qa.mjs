import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const v01 = path.join(root, "control/research/asa-mi/codex-source-mining-drafts/2026-08-20-v0.1");
const relations = fs.readFileSync(path.join(v01, "crosswalk/relations_candidates.jsonl"), "utf8").trim().split(/\r?\n/).map(JSON.parse);
const objectFiles = ["source-derived/objects.jsonl", "live-brainstorm/objects.jsonl", "codex-inferred/objects.jsonl"];
const objects = new Map(objectFiles.flatMap((file) => fs.readFileSync(path.join(v01, file), "utf8").trim().split(/\r?\n/).map(JSON.parse)).map((object) => [object.OBJECT_ID, object]));

const overrides = {
  "CX-REL-0001": {relation: "WEAKENS", rationale: "The endpoint is an unconfirmed question-mark hypothesis; the counterclaim attacks a literal reading rather than contradicting every interpretation."},
  "CX-REL-0008": {relation: "WEAKENS", rationale: "Portable State != Portable Persona weakens state/Memory sufficiency; it is not a complete alternative identity theory."},
  "CX-REL-0012": {relation: "REFINES", rationale: "Shared-evidence/separate-interpretation specifies a candidate partition within Common/Local Memory rather than replacing the whole model."},
  "CX-REL-0013": {relation: "POSSIBLE_CORROBORATION", rationale: "Similar RED outputs may share ancestry; agreement cannot be labeled independent strengthening."},
  "CX-REL-0015": {relation: "MOTIVATES", from: "CX-SRC-SRC-R3-0020", to: "CX-SRC-SRC-R3-0021", rationale: "DELETE_SOURCE != DELETE_INFLUENCE motivates dependency/invalidation machinery; v0.1 direction was reversed."},
  "CX-REL-0017": {relation: "CONSTRAINS", rationale: "Separate Authority rebinding constrains successor construction but does not refine what successor identity means."},
  "CX-REL-0018": {relation: "DOES_NOT_VALIDATE", rationale: "NOT_PROVEN behavioral compatibility does not weaken the provider-replacement design intent; it blocks an empirical inference from it."},
  "CX-REL-0019": {relation: "POSSIBLE_SEMANTIC_EQUIVALENCE", rationale: "The two source objects use the same formula; preserve both provenance records and do not call one a preservation operation on the other."},
  "CX-REL-0021": {relation: "POSSIBLE_CORROBORATION", rationale: "Same-root audit risks coexist and may corroborate, but source independence is not established."},
  "CX-REL-0025": {relation: "TENSION_WITH", rationale: "MEMORY != CURRENT STATE is not semantically equivalent to CURRENT_STATUS as a view over Memory; the latter may refine or challenge the boundary."},
  "CX-REL-0027": {relation: "MAPS_TO", rationale: "CURRENT is a live operator candidate relevant to reconstruction, not a demonstrated refinement of the historical reconstruction hypothesis."},
  "CX-REL-0033": {relation: "COEXISTS_WITH", rationale: "Reality-first and reality-proximity align, but grounding direction and dependency are not established."},
  "CX-REL-0035": {relation: "MOTIVATES", rationale: "Representation/index uncertainty motivates applying the CS-prior method; it does not logically require a specific prior."},
  "CX-REL-0037": {relation: "UNSUPPORTED_RELATION", rationale: "Origin preservation and environment-bound function state are both relevant but no direct refinement relation is expressed."},
  "CX-REL-0038": {relation: "COEXISTS_WITH", rationale: "Perceived-realism separation is an evaluation axis adjacent to multidimensional continuity, not a direct refinement."},
  "CX-REL-0046": {relation: "TESTS", to: "CX-LIVE-BRAINSTORM-0019", rationale: "Reference-memory migration directly tests external/reference Memory identity."},
  "CX-REL-0047": {relation: "TESTS", to: "CX-LIVE-BRAINSTORM-0021", rationale: "Function-binding portability directly tests environment-bound function state."},
  "CX-REL-0049": {relation: "TESTS", to: "CX-LIVE-BRAINSTORM-0038", rationale: "Current-status ablation directly compares the four preserved Status models."},
  "CX-REL-0050": {relation: "TESTS", to: "CX-LIVE-BRAINSTORM-0026", rationale: "Self-model ablation directly tests the optional derived self-model candidate."},
  "CX-REL-0051": {relation: "TESTS", to: "CX-SRC-SRC-MI1-0045", rationale: "Learning decomposition directly tests multiple experience-derived product families."},
  "CX-REL-0052": {relation: "TESTS", to: "CX-LIVE-BRAINSTORM-0036", rationale: "Ghost-influence audit directly tests DELETE_SOURCE != DELETE_INFLUENCE."},
  "CX-REL-0053": {relation: "TESTS", to: "CX-SRC-SRC-R3-0026", rationale: "Fission Authority variation directly tests explicit/attenuated/no-inheritance policy."}
};

const qa = relations.map((relation, index) => {
  const override = overrides[relation.RELATION_ID];
  const from = override?.from || relation.FROM_OBJECT_ID;
  const to = override?.to || relation.TO_OBJECT_ID;
  const endpointExists = objects.has(from) && objects.has(to);
  return {
    RELATION_QA_ID: `V02-REL-QA-${String(index + 1).padStart(4, "0")}`,
    PREDECESSOR_RELATION_ID: relation.RELATION_ID,
    QA_STATUS: override ? override.relation === "UNSUPPORTED_RELATION" ? "REJECT_RELATION_CANDIDATE" : "NEEDS_RELATION_CORRECTION" : "ACCURATE_CANDIDATE",
    PREDECESSOR_FROM_OBJECT_ID: relation.FROM_OBJECT_ID,
    PREDECESSOR_RELATION: relation.RELATION,
    PREDECESSOR_TO_OBJECT_ID: relation.TO_OBJECT_ID,
    CORRECTED_FROM_OBJECT_ID: from,
    CORRECTED_RELATION: override?.relation || relation.RELATION,
    CORRECTED_TO_OBJECT_ID: to,
    ENDPOINTS_RESOLVE: endpointExists,
    RELATION_CERTAINTY: override?.relation === "POSSIBLE_CORROBORATION" || override?.relation === "POSSIBLE_SEMANTIC_EQUIVALENCE" ? "LOW_TO_MEDIUM_CANDIDATE" : "MEDIUM_CODEX_CANDIDATE",
    ENDPOINT_STATUS_SEPARATE: true,
    OWNER_TAGGED: false,
    SOURCE_EXPLICIT_RELATION: false,
    RATIONALE: override?.rationale || relation.NOTES,
    DOES_NOT_ASSERT: "SEMANTIC_EQUIVALENCE_OR_OWNER_ADOPTION_UNLESS_EXPLICITLY_STATED"
  };
});

const outFile = path.join(root, "control/research/asa-mi/codex-semantic-remining-drafts/2026-08-20-v0.2/crosswalk/relation_qa.jsonl");
fs.mkdirSync(path.dirname(outFile), {recursive: true});
fs.writeFileSync(outFile, qa.map((row) => JSON.stringify(row)).join("\n") + "\n");
const counts = qa.reduce((map, row) => (map[row.QA_STATUS] = (map[row.QA_STATUS] || 0) + 1, map), {});
console.log(JSON.stringify({relations: relations.length, output: qa.length, statuses: counts, endpoints_all_resolve: qa.every((row) => row.ENDPOINTS_RESOLVE)}, null, 2));
