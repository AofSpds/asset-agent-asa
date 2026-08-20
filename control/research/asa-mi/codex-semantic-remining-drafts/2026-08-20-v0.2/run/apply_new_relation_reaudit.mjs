import fs from "node:fs";
import path from "node:path";

const file = path.join(process.cwd(), "control/research/asa-mi/codex-semantic-remining-drafts/2026-08-20-v0.2/crosswalk/new_relation_candidates.jsonl");
const rows = fs.readFileSync(file, "utf8").split(/\r?\n/).filter(Boolean).map(JSON.parse);
const byId = new Map(rows.map((row) => [row.RELATION_ID, row]));
for (const row of rows) row.MANUAL_QA_STATUS = "ACCURATE_CANDIDATE";

const fix = (id, changes) => Object.assign(byId.get(id), { MANUAL_QA_STATUS: "CORRECTED_CANDIDATE", ...changes });
fix("V02-REL-0018", { RELATION_TYPE: "REFINES", RATIONALE: "Reconstruction-policy invariance elaborates, rather than opposes, the historical claim that reconstruction may be more central than storage." });
fix("V02-REL-0021", { TO_OBJECT_ID: "CX-LIVE-BRAINSTORM-0018", RATIONALE: "Causal sensitivity constrains the explicit live claim ACCESSIBLE(X) != MEMORIZED(X); the original reference-identity question endpoint was too indirect." });
fix("V02-REL-0030", { RELATION_TYPE: "REFINES", RATIONALE: "Calibrated heterogeneous implementations elaborate the Persona != Model principle without counting a Codex inference as independent strengthening evidence." });
fix("V02-REL-0031", { RELATION_TYPE: "CONSTRAINS", RATIONALE: "Shared-evidence/separate-interpretation is insufficient if common priors and objectives still drive convergence." });
fix("V02-REL-0033", { RELATION_TYPE: "REFINES", RATIONALE: "Counterfactual undecidability extends DELETE_SOURCE != DELETE_INFLUENCE into a verification limit rather than weakening it." });
fix("V02-REL-0034", { RELATION_TYPE: "CONSTRAINS", RATIONALE: "De facto agenda and framing power constrains the practical adequacy of the formal MEMORY != AUTHORITY firewall without asserting their identity." });
fix("V02-REL-0037", { RELATION_TYPE: "REFINES", RATIONALE: "Expectation and fluency bias explain one mechanism by which perceived realism can diverge from causal or historical fidelity." });
fix("V02-REL-0038", { RELATION_TYPE: "REFINES", RATIONALE: "External relational reconstruction extends the cloud-loss continuity claim to a case with internal-state loss; it is not a mutually exclusive alternative." });
fix("V02-REL-0040", { TO_OBJECT_ID: "CX-SRC-SRC-MI0-0001", RATIONALE: "Same runtime with different experience histories directly tests whether Memory/history differences materially alter identity-like continuity." });
fix("V02-REL-0051", { TO_OBJECT_ID: "V02-INF-FM-013", RATIONALE: "The gradual poison trajectory directly tests the slow-poison consolidation failure mode rather than only fabricated-history recognition." });
fix("V02-REL-0053", { TO_OBJECT_ID: "CX-SRC-SRC-R3-0026", RATIONALE: "Authority inherited, attenuated, revoked, or rebound directly tests the source fission-authority policy candidate." });
fix("V02-REL-0066", { TO_OBJECT_ID: "V02-INF-FM-011", RATIONALE: "Provider round-trips of UNKNOWN/null/absent/deleted/conflict/zero directly test the unknown-default collapse failure mode." });

fs.writeFileSync(file, `${rows.map((row) => JSON.stringify(row)).join("\n")}\n`, "utf8");
console.log(JSON.stringify({ accurate: rows.filter((row) => row.MANUAL_QA_STATUS === "ACCURATE_CANDIDATE").length, corrected: rows.filter((row) => row.MANUAL_QA_STATUS === "CORRECTED_CANDIDATE").length }));
