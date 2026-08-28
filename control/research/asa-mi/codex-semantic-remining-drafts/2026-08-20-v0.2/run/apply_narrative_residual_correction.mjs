import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const v02 = path.join(root, "control/research/asa-mi/codex-semantic-remining-drafts/2026-08-20-v0.2");
const v01File = path.join(root, "control/research/asa-mi/codex-source-mining-drafts/2026-08-20-v0.1/live-brainstorm/objects.jsonl");
const read = (file) => fs.readFileSync(file, "utf8").split(/\r?\n/).filter(Boolean).map(JSON.parse);
const write = (file, rows) => fs.writeFileSync(file, `${rows.map((row) => JSON.stringify(row)).join("\n")}\n`, "utf8");
const predecessorId = "CX-LIVE-WORLDVIEW-0002";
const source = read(v01File).find((row) => row.OBJECT_ID === predecessorId);

const qaFile = path.join(v02, "extraction-qa/v01_object_qa.jsonl");
const qa = read(qaFile);
const disposition = qa.find((row) => row.PREDECESSOR_OBJECT_ID === predecessorId);
disposition.QA_STATUS = "NEEDS_CORRECTION";
disposition.STATEMENT_CHECK = { result: "INCOMPLETE_LEAD_IN", note: "The statement ends with a colon and omits the three-way distinction and action-without-finalization claim carried by the source section." };
disposition.WORDING_CHECK = { materially_altered: true, note: "The parser selected only the section lead-in; successor restores the operative distinction." };
disposition.REVIEWED_IN_PASS = "OBJECT-QA-ALL-487 + MANUAL-REAUDIT-ALL-487 + NARRATIVE-RESIDUAL-01";
write(qaFile, qa);

const correctionsFile = path.join(v02, "extraction-qa/corrections.jsonl");
const corrections = read(correctionsFile);
if (!corrections.some((row) => row.PREDECESSOR_OBJECT_ID === predecessorId)) {
  const nextCorrection = Math.max(...corrections.map((row) => Number(row.CORRECTION_ID.match(/(\d+)$/)?.[1] ?? 0))) + 1;
  const nextSuccessor = Math.max(...corrections.map((row) => Number(row.SUCCESSOR_OBJECT_ID.match(/(\d+)$/)?.[1] ?? 0))) + 1;
  corrections.push({
    CORRECTION_ID: `V02-COR-${String(nextCorrection).padStart(4, "0")}`,
    PREDECESSOR_OBJECT_ID: predecessorId,
    SUCCESSOR_OBJECT_ID: `V02-SUCCESSOR-${String(nextSuccessor).padStart(4, "0")}`,
    ORIGIN_OBJECT_ID: source.ORIGIN_OBJECT_ID,
    CORPUS_GROUP: source.CORPUS_GROUP,
    CORRECTION_TYPE: ["STATEMENT", "SOURCE_CONTEXT"],
    PREDECESSOR_STATEMENT: source.STATEMENT,
    CORRECTED_STATEMENT: "The project distinguishes FINAL_TRUTH, CURRENT_BEST_HYPOTHESIS, and CURRENT_OPERATIONAL_DECISION; it may act on the current best hypothesis while preserving replaceability and without claiming final truth.",
    PREDECESSOR_CLASS: source.CLASS,
    CORRECTED_CLASS: source.CLASS,
    PREDECESSOR_SOURCE_LOCATOR: source.SOURCE_LOCATOR,
    CORRECTED_SOURCE_LOCATOR: source.SOURCE_LOCATOR,
    SOURCE_POSITION_STATE: source.SOURCE_POSITION_STATE,
    SOURCE_LEVEL: source.SOURCE_LEVEL,
    OWNER_POSITION_STATE: source.OWNER_POSITION_STATE,
    DOES_NOT_ASSERT: "A_CURRENT_OPERATIONAL_DECISION_IS_FINAL_TRUTH",
    CORRECTION_RATIONALE: "Narrative residual reread found that the v0.1 statement retained only an incomplete lead-in and omitted the operative three-way distinction.",
    RAW_PRIMARY_SOURCE_VERIFICATION: "NOT_APPLICABLE_LIVE_REPOSITORY_RECORD",
  });
}
write(correctionsFile, corrections);
write(path.join(v02, "source-derived/corrected_objects.jsonl"), corrections.filter((row) => row.CORPUS_GROUP.startsWith("C_")));
write(path.join(v02, "live/corrected_live_objects.jsonl"), corrections.filter((row) => row.CORPUS_GROUP.startsWith("D_")));
console.log(JSON.stringify({ qa: qa.length, corrections: corrections.length, liveCorrections: corrections.filter((row) => row.CORPUS_GROUP.startsWith("D_")).length }));
