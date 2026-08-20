import fs from "node:fs";
import path from "node:path";

const file = path.join(process.cwd(), "control/research/asa-mi/codex-semantic-remining-drafts/2026-08-20-v0.2/crosswalk/relation_qa.jsonl");
const rows = fs.readFileSync(file, "utf8").split(/\r?\n/).filter(Boolean).map(JSON.parse);
const byId = new Map(rows.map((row) => [row.PREDECESSOR_RELATION_ID, row]));

Object.assign(byId.get("CX-REL-0036"), {
  QA_STATUS: "NEEDS_RELATION_CORRECTION",
  CORRECTED_FROM_OBJECT_ID: "CX-SRC-SRC-MI1-ADVERSARIAL-PACKET-SOURCE-CONTEXT-0005",
  CORRECTED_RELATION: "MAPS_TO",
  CORRECTED_TO_OBJECT_ID: "CX-LIVE-BRAINSTORM-0015",
  RATIONALE: "The v0.1 edge names the open-ended Persona differentiation risk object, but its rationale concerns EVOLUTION = CHANGE_OVER_TIME. Correct the source endpoint to SN-MI-PC-021; the change-over-time principle then maps, with medium certainty, to the live Memory-dynamics/change-rate model.",
});
Object.assign(byId.get("CX-REL-0042"), {
  QA_STATUS: "NEEDS_RELATION_CORRECTION",
  CORRECTED_RELATION: "CONSTRAINS",
  RATIONALE: "ACCESSIBLE(X) != MEMORIZED(X) constrains external-reference Memory: a reachable URL is insufficient without a bound remembrance relation. It is not independent evidence that strengthens the example.",
});
Object.assign(byId.get("CX-REL-0044"), {
  QA_STATUS: "NEEDS_RELATION_CORRECTION",
  CORRECTED_RELATION: "REFINES",
  RATIONALE: "P-006 and H-LIFE-001 are correlated live records in the same registry. The latter supplies lifecycle states to the broader principle; this is refinement, not evidentiary strengthening.",
});

fs.writeFileSync(file, `${rows.map((row) => JSON.stringify(row)).join("\n")}\n`, "utf8");
const counts = Object.fromEntries([...new Set(rows.map((row) => row.QA_STATUS))].sort().map((status) => [status, rows.filter((row) => row.QA_STATUS === status).length]));
console.log(JSON.stringify(counts));
