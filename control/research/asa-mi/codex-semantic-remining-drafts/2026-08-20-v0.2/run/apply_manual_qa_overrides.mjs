import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const v02 = path.join(root, "control/research/asa-mi/codex-semantic-remining-drafts/2026-08-20-v0.2");
const v01 = path.join(root, "control/research/asa-mi/codex-source-mining-drafts/2026-08-20-v0.1");
const readJsonl = (file) => fs.readFileSync(file, "utf8").split(/\r?\n/).filter((line) => line.trim()).map(JSON.parse);
const writeJsonl = (file, rows) => fs.writeFileSync(file, `${rows.map((row) => JSON.stringify(row)).join("\n")}\n`, "utf8");

const objectFiles = ["source-derived/objects.jsonl", "live-brainstorm/objects.jsonl", "codex-inferred/objects.jsonl"];
const v01Objects = objectFiles.flatMap((file) => readJsonl(path.join(v01, file)));
const byId = new Map(v01Objects.map((object) => [object.OBJECT_ID, object]));

const survivalFindingIds = [
  "CX-SRC-SRC-R1-0030",
  "CX-SRC-SRC-R1-0034",
  "CX-SRC-SRC-R2-0010",
  "CX-SRC-SRC-R2-0011",
  "CX-SRC-SRC-R2-0019",
  "CX-SRC-SRC-R2-0031",
  "CX-SRC-SRC-R2-0032",
  "CX-SRC-SRC-R2-0033",
  "CX-SRC-SRC-R2-0037",
];
const ambiguousVerdictId = "CX-SRC-SRC-R1-0001";

const qaFile = path.join(v02, "extraction-qa/v01_object_qa.jsonl");
const qa = readJsonl(qaFile);
for (const row of qa) {
  if (survivalFindingIds.includes(row.PREDECESSOR_OBJECT_ID)) {
    row.QA_STATUS = "NEEDS_CORRECTION";
    row.CLASS_CHECK = {
      result: "SOURCE_FINDING_MISCLASSIFIED_AS_EVIDENCE_CLAIM",
      note: "SURVIVAL_FINDING is a conclusion/status inside a normalized RED source, not evidence that an experiment was executed. Use SOURCE_SURVIVAL_FINDING and retain its exact source-state qualifier.",
    };
    row.REVIEWED_IN_PASS = "OBJECT-QA-ALL-487 + MANUAL-REAUDIT-ALL-487";
  }
  if (row.PREDECESSOR_OBJECT_ID === ambiguousVerdictId) {
    row.QA_STATUS = "ACCURATE_WITH_MINOR_NORMALIZATION";
    row.SOURCE_POSITION_STATE_CHECK = {
      result: "TARGET_HYPOTHESIS_REJECTED_BY_COUNTERFORCE",
      source_record_state: "REJECTED BY COUNTERFORCE",
      note: "The source register explicitly states literal Identity = Memory -> REJECTED BY COUNTERFORCE. This is a RED source verdict, not raw verification, formal validation, or Owner adoption.",
    };
    row.REVIEWED_IN_PASS = "OBJECT-QA-ALL-487 + MANUAL-REAUDIT-ALL-487 + VERDICT-CONTEXT-RESOLUTION";
  }
}
writeJsonl(qaFile, qa);

const correctionsFile = path.join(v02, "extraction-qa/corrections.jsonl");
const corrections = readJsonl(correctionsFile);
const correctionByPredecessor = new Map(corrections.map((row) => [row.PREDECESSOR_OBJECT_ID, row]));
let nextCorrection = Math.max(...corrections.map((row) => Number(row.CORRECTION_ID.match(/(\d+)$/)?.[1] ?? 0))) + 1;
let nextSuccessor = Math.max(...corrections.map((row) => Number(row.SUCCESSOR_OBJECT_ID.match(/(\d+)$/)?.[1] ?? 0))) + 1;
for (const predecessorId of survivalFindingIds) {
  const object = byId.get(predecessorId);
  let correction = correctionByPredecessor.get(predecessorId);
  if (!correction) {
    correction = {
      CORRECTION_ID: `V02-COR-${String(nextCorrection++).padStart(4, "0")}`,
      PREDECESSOR_OBJECT_ID: predecessorId,
      SUCCESSOR_OBJECT_ID: `V02-SUCCESSOR-${String(nextSuccessor++).padStart(4, "0")}`,
      ORIGIN_OBJECT_ID: object.ORIGIN_OBJECT_ID,
      CORPUS_GROUP: object.CORPUS_GROUP,
      CORRECTION_TYPE: ["CLASS"],
      PREDECESSOR_STATEMENT: object.STATEMENT,
      CORRECTED_STATEMENT: object.STATEMENT,
      PREDECESSOR_CLASS: object.CLASS,
      CORRECTED_CLASS: "SOURCE_SURVIVAL_FINDING",
      PREDECESSOR_SOURCE_LOCATOR: object.SOURCE_LOCATOR,
      CORRECTED_SOURCE_LOCATOR: object.SOURCE_LOCATOR,
      SOURCE_POSITION_STATE: object.SOURCE_POSITION_STATE,
      SOURCE_LEVEL: object.SOURCE_LEVEL,
      OWNER_POSITION_STATE: object.OWNER_POSITION_STATE,
      DOES_NOT_ASSERT: object.DOES_NOT_ASSERT,
      CORRECTION_RATIONALE: "Manual all-object re-audit found that SURVIVAL_FINDING was overstated as EVIDENCE_CLAIM; no executed experiment or independent validation is established.",
      RAW_PRIMARY_SOURCE_VERIFICATION: "NOT_PERFORMED",
    };
    corrections.push(correction);
    correctionByPredecessor.set(predecessorId, correction);
  } else {
    if (!correction.CORRECTION_TYPE.includes("CLASS")) correction.CORRECTION_TYPE.push("CLASS");
    correction.CORRECTED_CLASS = "SOURCE_SURVIVAL_FINDING";
    correction.CORRECTION_RATIONALE = `${correction.CORRECTION_RATIONALE} Manual re-audit also corrected SURVIVAL_FINDING misclassification as EVIDENCE_CLAIM; the source records a RED-source finding/status, not executed empirical evidence.`;
  }
}
writeJsonl(correctionsFile, corrections);

writeJsonl(path.join(v02, "source-derived/corrected_objects.jsonl"), corrections.filter((row) => row.CORPUS_GROUP.startsWith("C_")));
writeJsonl(path.join(v02, "live/corrected_live_objects.jsonl"), corrections.filter((row) => row.CORPUS_GROUP.startsWith("D_")));

const overrides = [
  ...survivalFindingIds.map((id) => ({ PREDECESSOR_OBJECT_ID: id, MANUAL_OVERRIDE: "CLASS_TO_SOURCE_SURVIVAL_FINDING", RESULTING_QA_STATUS: "NEEDS_CORRECTION" })),
  { PREDECESSOR_OBJECT_ID: ambiguousVerdictId, MANUAL_OVERRIDE: "VERDICT_SCOPE_AMBIGUOUS", RESULTING_QA_STATUS: "SOURCE_CONTEXT_REQUIRED" },
  { PREDECESSOR_OBJECT_ID: ambiguousVerdictId, MANUAL_OVERRIDE: "VERDICT_DIRECTION_RESOLVED_BY_SOURCE_REGISTER", RESULTING_QA_STATUS: "ACCURATE_WITH_MINOR_NORMALIZATION" },
];
writeJsonl(path.join(v02, "extraction-qa/manual_qa_overrides.jsonl"), overrides);

console.log(JSON.stringify({ qa: qa.length, corrections: corrections.length, sourceCorrections: corrections.filter((row) => row.CORPUS_GROUP.startsWith("C_")).length, liveCorrections: corrections.filter((row) => row.CORPUS_GROUP.startsWith("D_")).length, overrides: overrides.length }));
