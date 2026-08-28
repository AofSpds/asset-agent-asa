import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const v01 = path.join(root, "control/research/asa-mi/codex-source-mining-drafts/2026-08-20-v0.1");
const out = path.join(root, "control/research/asa-mi/codex-semantic-remining-drafts/2026-08-20-v0.2");
const inputFiles = ["source-derived/objects.jsonl", "live-brainstorm/objects.jsonl", "codex-inferred/objects.jsonl"];
const objects = inputFiles.flatMap((file) => fs.readFileSync(path.join(v01, file), "utf8").trim().split(/\r?\n/).map((line) => ({...JSON.parse(line), _input: file})));

const manual = new Map(Object.entries({
  "CX-SRC-SRC-WP1-SRC-WP2-0001": "Tension: 'Persona State is not a memory dump' versus a later proposition that may treat a much broader range of Persona state as Memory; unresolved and requires Memory-semantics reconciliation.",
  "CX-SRC-SRC-WP1-SRC-WP2-0002": "Tension: history may require integrity/preservation while Persona/Memory must support lifecycle, forgetting, deletion, and correction; unresolved and requires a layered model.",
  "CX-SRC-SRC-WP1-SRC-WP2-0003": "Tension: provider replacement is a design intent, while behavioral continuity across models/providers is not empirically established; design intent is not empirical proof.",
  "CX-SRC-SRC-MI0-SRC-MI1-0002": "The source proposes OWNER_EXPLICIT, OBSERVED_EVENT, EXTERNAL_EVIDENCE, PERSONA_INTERPRETATION, and EXTERNAL_MODEL_INFERENCE as origin classes and says origin should survive consolidation.",
  "CX-SRC-SRC-MI1-0004": "The source proposes raw experience, episodic and semantic memory, relationship memory, procedural expertise, heuristics, standpoint, interpretations, meta-memory, provenance, and conflict/supersession relations as components, without assuming all are truly Memory.",
  "CX-SRC-SRC-MI1-0011": "The source proposes distinct Common-Memory and Persona-local candidate sets, including shared history/evidence on one side and specialized experience/heuristics/interpretation on the other.",
  "CX-SRC-SRC-MI1-0019": "The source proposes a current-instance input set spanning autobiographical core, local memory, standpoint, expertise, events, episodes, conflicts, relationship, governance, and Authority references, while rejecting loading all history into every context.",
  "CX-SRC-SRC-MI1-0042": "Evaluate Persona continuity across evidence weighting, uncertainty, risk tolerance, recall, causal interpretation, self-history use, expertise, dissent, error, permission, task decomposition, relationship interpretation, and decision tendencies.",
  "CX-SRC-SRC-R1-0028": "Retrieval suppression, dormancy, supersession, compression, archival, content deletion, and cryptographic erasure are distinct operations and must not be collapsed into one FORGET operation.",
  "CX-SRC-SRC-R2-0018": "Local continuity candidates include Owner-relation recognition, core constraints, critical-history retrieval, calibrated unknown handling, safe new-experience preservation, and export/recovery.",
  "CX-SRC-SRC-R2-0026": "Possible reconstruction layers include identity/lineage core, current standpoint, task-relevant evidence, procedural playbook, relationship state, conflict/uncertainty, and runtime/model binding.",
  "CX-SRC-SRC-R3-0004": "The source proposes OWNER_EXPLICIT, EXTERNAL_FACT_CANDIDATE, MODEL_INFERENCE, PERSONA_INTERPRETATION, and OTHER_PERSONA_CLAIM origin classes and says repetition/summarization must not upgrade origin.",
  "CX-SRC-SRC-R3-0009": "The RED-III recommendation separates highly automatable mutations, conditional automation, strong-review semantic changes, and separately governed Authority/identity operations; it is not a Requirement.",
  "CX-SRC-SRC-R3-0017": "State restoration, semantic correction, compensating mutation, and branch-successor reconstruction are distinct operations.",
  "CX-SRC-SRC-R3-0031": "The RED-III Audit model allows observe/challenge/propose/escalate, considers only a narrow pre-authorized emergency suspension exception, and withholds identity mutation, deletion, grant, and ruleset authority.",
  "CX-SRC-SRC-R3-0036": "The source separates deterministic Authority boundaries (amount, recipient, scope, expiry, delegation, attenuation, secrets, successor identity, revocation, suspension) from semantic interpretation layers.",
  "CX-SRC-SRC-R3-0049": "NORMAL, RESTRICTED, QUARANTINED, READ_ONLY, RECOVERY, and REVIEW_REQUIRED are analytical operational-state candidates, not a normative enum.",
  "CX-SRC-SRC-MI0-0019": "The source proposes separate Memory-evaluation dimensions including importance, durability, identity relevance, usefulness, confidence, origin, scope, applicability, freshness, conflict, supersession, provenance, sensitivity, Authority class, and retrieval priority; their independence remains open.",
  "CX-SRC-SRC-MI0-0026": "Cold-start recovery must evaluate identity, intent, cognitive, execution, and Authority continuity separately.",
  "CX-SRC-SRC-MI0-0028": "Cold-start targets include Persona identity, Owner-explicit content, shared history, expertise, Owner relationship, learned style, current workstream, and separately represented authoritative state.",
  "CX-SRC-SRC-MI1-0043": "Compare Persona self-description, observed behavior, supporting Memory evidence, and Owner audit interpretation.",
  "CX-LIVE-PLANNING-0008": "Natural language is allowed and structured notation is not mandatory for ASA-MI planning and review.",
  "CX-LIVE-PLANNING-0009": "Attach structured expression when meaning can be reliably normalized; otherwise it is not required.",
  "CX-LIVE-PLANNING-0010": "Failure to normalize does not invalidate content; unclassified does not mean low value; structured expression is not the thought boundary; schema is not reality.",
  "CX-LIVE-PLANNING-0011": "Use the least ambiguous available representation, without treating the formula as measured precision.",
  "CX-LIVE-PLANNING-0012": "Do not assign numeric confidence without a measurement basis; a state enum is preferable to fake precision.",
  "CX-LIVE-PLANNING-0013": "Record claims separately when they can change independently, unless decomposition destroys context or meaning.",
  "CX-LIVE-PLANNING-0014": "Use an open, revisable relation vocabulary when explicit object-to-object meaning improves review.",
  "CX-LIVE-PLANNING-0015": "Record DOES_NOT_ASSERT when it materially prevents a likely misreading.",
  "CX-LIVE-PLANNING-0016": "Structured expression and natural-language explanation may coexist; neither structured-only nor natural-language-only is mandatory.",
  "CX-LIVE-PLANNING-0017": "Do not force structured representation when it adds more ambiguity or cognitive cost than it removes.",
  "CX-LIVE-PLANNING-0018": "The shared representational layer may be used by planners, RED teams, facilitators, and successor research Personas; its class list is open.",
  "CX-LIVE-PLANNING-0019": "When an idea does not fit the schema, preserve the original and optionally extend the schema or use an unclassified state.",
  "CX-LIVE-BRAINSTORM-0006": "Computer-science prior is not reality; revise the model when the prior conflicts with observed reality.",
  "CX-LIVE-BRAINSTORM-0008": "Precision is not accuracy; representation is not reality; schema is not ontological truth.",
  "CX-LIVE-BRAINSTORM-0016": "Memory value types may include values, objects, references, relations, functions/bindings, execution results, status, events, and derived views.",
  "CX-LIVE-BRAINSTORM-0019": "An external reference may itself participate in Memory, exemplified by Persona --REMEMBERS_BY_REFERENCE--> External_URL.",
  "CX-LIVE-BRAINSTORM-0031": "Context is provisionally mapped to the relevant state, bindings, and conditions needed to execute or evaluate an operation; this prior is not final truth.",
  "CX-LIVE-BRAINSTORM-0032": "Context may include evaluation coordinates, relevant state, bindings, and conditions.",
  "CX-LIVE-BRAINSTORM-0033": "Global, per-function local, and hybrid projected Context structures remain unresolved candidates.",
  "CX-LIVE-BRAINSTORM-0034": "Persona and Memory objects may transition among create, active, update, dormant, reactivate, supersede, archive, and delete without one fixed path.",
  "CX-LIVE-BRAINSTORM-0035": "Deletion is a valid Persona/Memory lifecycle-operation candidate.",
  "CX-LIVE-BRAINSTORM-0037": "Forgetting may map to accessibility decay, activation decay, relation weakening, retrieval failure, or deletion; the mapping remains unresolved.",
  "CX-LIVE-BRAINSTORM-0038": "Minimal, rich, derived, and hybrid Current Status representations remain unresolved competing candidates.",
  "CX-SRC-SRC-R2-0046": "Cloud-to-local SLM migration should separate capability degradation from continuity loss.",
  "CX-SRC-SRC-R2-0047": "Provider-disappearance testing should measure actual portability and survivability."
}));

const priorArtStatements = {
  "CX-LIVE-PLANNING-0020": "AIDA is a low-weight, not-adopted prior similar to atomic natural-language claim objects; similarity does not make it the ASA-MI representation model.",
  "CX-LIVE-PLANNING-0021": "Nanopublications are a low-weight, not-adopted prior for small assertions with provenance and publication metadata; they are not the ASA-MI hypothesis lifecycle.",
  "CX-LIVE-PLANNING-0022": "RDF 1.2 is a low-weight, not-adopted prior for explicit subject-predicate-object relation graphs.",
  "CX-LIVE-PLANNING-0023": "PROV-O is a low-weight, not-adopted prior for entity/activity/agent provenance and derivation relations.",
  "CX-LIVE-PLANNING-0024": "SHACL is a low-weight, not-adopted prior for machine-checkable graph shape conformance, not a semantic-validation decision.",
  "CX-LIVE-PLANNING-0025": "SBVR is a low-weight, not-adopted prior for controlled vocabulary plus human- and machine-readable semantics.",
  "CX-LIVE-PLANNING-0026": "JSON-LD is a low-weight, not-adopted possible interoperability projection; no current adoption need is asserted."
};
for (const [id, statement] of Object.entries(priorArtStatements)) manual.set(id, statement);

const r1Experiments = new Set(Array.from({length: 12}, (_, i) => `CX-SRC-SRC-R1-${String(44 + i).padStart(4, "0")}`));
const r2Experiments = new Set(Array.from({length: 10}, (_, i) => `CX-SRC-SRC-R2-${String(39 + i).padStart(4, "0")}`));
const sourceFindingIds = new Set(Array.from({length: 8}, (_, i) => `CX-SRC-SRC-R2-${String(31 + i).padStart(4, "0")}`));
const badMetaLocators = new Set(Array.from({length: 9}, (_, i) => `CX-SRC-META-${String(i + 1).padStart(4, "0")}`));
const badCheckpointLocators = new Set(Array.from({length: 5}, (_, i) => `CX-LIVE-CHECKPOINT-${String(i + 1).padStart(4, "0")}`));
const splitIds = new Set(["CX-LIVE-BRAINSTORM-0042", "CX-LIVE-WORLDVIEW-0009"]);
const rawRequiredIds = new Set(Array.from({length: 10}, (_, i) => `CX-SRC-META-${String(i + 10).padStart(4, "0")}`));
const trueMergeIds = new Set(["CX-SRC-SRC-MI0-SRC-MI1-0003", "CX-SRC-SRC-R3-0003", "CX-SRC-SRC-R3-0020", "CX-LIVE-BRAINSTORM-0036"]);

function fields(record) {
  const result = {};
  for (const line of String(record).split(/\r?\n/)) {
    const match = line.match(/^([A-Z][A-Z0-9_ /-]*?)\s*=\s*(.*)$/);
    if (match && !result[match[1].trim()]) result[match[1].trim()] = match[2].trim();
  }
  return result;
}

function locatorCheck(object) {
  if (object.INFERENCE_STATE === "CODEX_INFERRED_CANDIDATE") return {result: "NOT_APPLICABLE", path_resolves: null, anchor_resolves: null};
  const [relative, anchor = ""] = String(object.SOURCE_LOCATOR || "").split("#", 2);
  const absolute = path.join(root, relative);
  const pathResolves = fs.existsSync(absolute);
  const anchorResolves = !anchor || (pathResolves && fs.readFileSync(absolute, "utf8").includes(anchor));
  return {result: pathResolves && anchorResolves ? "ACCURATE" : "INACCURATE", path_resolves: pathResolves, anchor_resolves: anchorResolves};
}

function classCheck(object) {
  const record = String(object.SOURCE_RECORD_TEXT || "");
  if (object.INFERENCE_STATE === "CODEX_INFERRED_CANDIDATE") return {result: "APPROPRIATE_CODEX_CLASS", note: "Class matches the v0.1 Codex-inference semantic role."};
  if (/CLASS = CANDIDATE_HYPOTHESIS/.test(record) && object.CLASS === "WORKING_HYPOTHESIS") return {result: "TOO_STRONG_NORMALIZATION", note: "CANDIDATE_HYPOTHESIS was normalized to WORKING_HYPOTHESIS; candidate status must remain explicit."};
  return {result: "APPROPRIATE_NORMALIZATION", note: "Class is a defensible normalization of the source class; source wording remains in SOURCE_RECORD_TEXT."};
}

function correctedStatement(object) {
  if (manual.has(object.OBJECT_ID)) return manual.get(object.OBJECT_ID);
  const parsed = fields(object.SOURCE_RECORD_TEXT);
  if (r1Experiments.has(object.OBJECT_ID) || r2Experiments.has(object.OBJECT_ID)) {
    const lines = String(object.SOURCE_RECORD_TEXT).split(/\r?\n/).filter(Boolean);
    return lines.join("; ").replace(/^TARGET = /, "Target: ");
  }
  if (sourceFindingIds.has(object.OBJECT_ID)) return `${parsed.OBJECT || object.STATEMENT}: source state = ${parsed.SOURCE_STATE || "NOT_RECORDED"}.`;
  return object.STATEMENT;
}

function materialSourceState(object) {
  const parsed = fields(object.SOURCE_RECORD_TEXT);
  for (const key of ["SOURCE_VERDICT", "SOURCE_STATE", "CONFIRMATION", "STATUS", "STATE"]) if (parsed[key]) return `${key}=${parsed[key]}`;
  return "NOT_EXPLICIT";
}

const qa = [];
const corrections = [];
let correctionNumber = 0;
for (const [index, object] of objects.entries()) {
  const record = String(object.SOURCE_RECORD_TEXT || "");
  const loc = locatorCheck(object);
  const metadataFallback = /^(?:OBJECT_ID|CLASS|TARGET|TYPE)\s*=/.test(String(object.STATEMENT)) || object.STATEMENT === "TENSION";
  const candidateClassError = classCheck(object).result === "TOO_STRONG_NORMALIZATION";
  const needsStatementCorrection = manual.has(object.OBJECT_ID) || r1Experiments.has(object.OBJECT_ID) || r2Experiments.has(object.OBJECT_ID) || sourceFindingIds.has(object.OBJECT_ID);
  const needsLocatorCorrection = badMetaLocators.has(object.OBJECT_ID) || badCheckpointLocators.has(object.OBJECT_ID);
  let status;
  if (splitIds.has(object.OBJECT_ID)) status = "SPLIT_REQUIRED";
  else if (needsStatementCorrection || needsLocatorCorrection || candidateClassError || metadataFallback) status = "NEEDS_CORRECTION";
  else if (rawRequiredIds.has(object.OBJECT_ID)) status = "RAW_SOURCE_REQUIRED";
  else if (object.INFERENCE_STATE === "CODEX_INFERRED_CANDIDATE") status = "REVIEW_REQUIRED";
  else if (trueMergeIds.has(object.OBJECT_ID)) status = "MERGE_CANDIDATE";
  else if (materialSourceState(object) !== "NOT_EXPLICIT" && object.SOURCE_POSITION_STATE === "NOT_RECORDED") status = "ACCURATE_WITH_MINOR_NORMALIZATION";
  else status = "ACCURATE";

  const exactStatement = record.includes(String(object.STATEMENT));
  const qaItem = {
    QA_ID: `V02-QA-${String(index + 1).padStart(4, "0")}`,
    PREDECESSOR_OBJECT_ID: object.OBJECT_ID,
    ORIGIN_OBJECT_ID: object.ORIGIN_OBJECT_ID || "",
    CORPUS_GROUP: object.CORPUS_GROUP,
    QA_STATUS: status,
    STATEMENT_CHECK: object.INFERENCE_STATE === "CODEX_INFERRED_CANDIDATE"
      ? {result: "COHERENT_CODEX_INFERENCE", note: "Semantically coherent and distinct enough to retain, but it is not a source claim."}
      : {result: metadataFallback ? "PARSER_METADATA_FALLBACK" : exactStatement ? "SOURCE_TEXT_PRESENT" : "NORMALIZED_OR_CONTEXTUAL", note: needsStatementCorrection ? "Successor statement restores omitted semantic fields/context." : "Statement captures the primary source-record claim."},
    PARSER_USED_METADATA_AS_STATEMENT: metadataFallback,
    CLASS_CHECK: classCheck(object),
    SUBCLASS_CHECK: {result: object.SUBCLASS === "NEGATIVE_CLAIM" ? "NEGATIVE_SEMANTICS_FLAGGED" : "NO_MATERIAL_SUBCLASS_ERROR_FOUND"},
    SOURCE_POSITION_STATE_CHECK: {result: materialSourceState(object) === "NOT_EXPLICIT" ? "NO_EXPLICIT_SOURCE_STATE" : object.SOURCE_POSITION_STATE === "NOT_RECORDED" ? "EXPLICIT_STATE_LEFT_UNSTRUCTURED" : "PRESERVED", source_record_state: materialSourceState(object)},
    CURRENT_RESEARCH_STATE_CHECK: {result: object.CORPUS_GROUP === "D_LIVE_BRAINSTORM_AS_IS" ? "LIVE_STATE_RECORDED_NOT_FINAL" : object.CORPUS_GROUP === "E_CODEX_MINED_TO_BE_DRAFT" ? "NOT_YET_TAGGED_CORRECT" : "NOT_YET_TAGGED_CORRECT"},
    OWNER_POSITION_STATE_CHECK: {result: object.CORPUS_GROUP === "E_CODEX_MINED_TO_BE_DRAFT" ? "NOT_OWNER_POSITION_CORRECT" : object.CORPUS_GROUP === "D_LIVE_BRAINSTORM_AS_IS" ? "RECORDED_RESEARCH_POSITION_NOT_ACCEPTANCE" : "UNKNOWN_UNLESS_EXPLICIT_CORRECT"},
    SOURCE_LEVEL_CHECK: {result: object.CORPUS_GROUP === "C_EXISTING_SOURCE_NORMALIZED_AS_IS" ? "SECONDARY_NORMALIZED_NOT_RAW" : object.CORPUS_GROUP === "D_LIVE_BRAINSTORM_AS_IS" ? "LIVE_REPOSITORY_RECORD" : "CODEX_INFERENCE"},
    DOES_NOT_ASSERT_CHECK: {result: object.DOES_NOT_ASSERT ? "EXPLICIT_NEGATIVE_PRESERVED" : /DOES_NOT_ASSERT\s*=/.test(record) ? "MISSING_EXPLICIT_NEGATIVE" : "NO_EXPLICIT_FIELD_IN_RECORD", value: object.DOES_NOT_ASSERT || ""},
    SOURCE_LOCATOR_CHECK: loc,
    SPLIT_MERGE_CHECK: {split_required: splitIds.has(object.OBJECT_ID), possible_merge: trueMergeIds.has(object.OBJECT_ID), note: splitIds.has(object.OBJECT_ID) ? "One v0.1 record contains multiple independently reviewable claims." : trueMergeIds.has(object.OBJECT_ID) ? "Possible semantic equivalence only; preserve separate provenance/layers." : "No material split/merge issue found in this object review."},
    WORDING_CHECK: {materially_altered: needsStatementCorrection || metadataFallback, note: needsStatementCorrection || metadataFallback ? "v0.1 statement selected metadata or omitted a claim-bearing field." : "No material wording alteration found relative to repository-visible record."},
    HISTORICAL_CONTEXT_CHECK: {result: object.CORPUS_GROUP === "C_EXISTING_SOURCE_NORMALIZED_AS_IS" ? "HISTORICAL_LAYER_RETAINED" : "NOT_HISTORICAL_SOURCE_LAYER"},
    DUPLICATE_CHECK: {result: trueMergeIds.has(object.OBJECT_ID) ? "POSSIBLE_SEMANTIC_EQUIVALENCE" : "NO_CONFIRMED_SEMANTIC_DUPLICATE", lexical_equality_is_not_equivalence: true},
    RAW_PRIMARY_SOURCE_VERIFICATION: object.CORPUS_GROUP === "C_EXISTING_SOURCE_NORMALIZED_AS_IS" ? "NOT_PERFORMED" : "NOT_APPLICABLE",
    REVIEW_BASIS: "Direct full-corpus rereads plus object-by-object comparison of STATEMENT, SOURCE_RECORD_TEXT, class/state fields, and locator.",
    REVIEWED_IN_PASS: "OBJECT-QA-ALL-487"
  };
  qa.push(qaItem);

  if (status === "NEEDS_CORRECTION") {
    correctionNumber += 1;
    let locator = object.SOURCE_LOCATOR;
    if (badMetaLocators.has(object.OBJECT_ID)) {
      if (/^CX-SRC-META-000[1-3]$/.test(object.OBJECT_ID)) locator = "control/research/asa-mi/source-normalized-drafts/v0.1/00_README_SOURCE_NORMALIZATION_BOUNDARY.md";
      else locator = `control/research/asa-mi/source-normalized-drafts/v0.1/06_RED_III_SOURCE_OBJECTS.md#${object.ORIGIN_OBJECT_ID}`;
    }
    if (badCheckpointLocators.has(object.OBJECT_ID)) locator = "control/research/asa-mi/checkpoints/2026-08-20/AAA_ASA_MI_CURRENT_RESEARCH_STATE_CHECKPOINT_2026-08-20T0509KST_v0.1.md";
    corrections.push({
      CORRECTION_ID: `V02-COR-${String(correctionNumber).padStart(4, "0")}`,
      PREDECESSOR_OBJECT_ID: object.OBJECT_ID,
      SUCCESSOR_OBJECT_ID: `V02-SUCCESSOR-${String(correctionNumber).padStart(4, "0")}`,
      ORIGIN_OBJECT_ID: object.ORIGIN_OBJECT_ID || "",
      CORPUS_GROUP: object.CORPUS_GROUP,
      CORRECTION_TYPE: [needsStatementCorrection || metadataFallback ? "STATEMENT" : null, candidateClassError ? "CLASS" : null, needsLocatorCorrection ? "SOURCE_LOCATOR" : null].filter(Boolean),
      PREDECESSOR_STATEMENT: object.STATEMENT,
      CORRECTED_STATEMENT: correctedStatement(object),
      PREDECESSOR_CLASS: object.CLASS,
      CORRECTED_CLASS: candidateClassError ? "CANDIDATE_HYPOTHESIS" : object.CLASS,
      PREDECESSOR_SOURCE_LOCATOR: object.SOURCE_LOCATOR,
      CORRECTED_SOURCE_LOCATOR: locator,
      SOURCE_POSITION_STATE: materialSourceState(object),
      SOURCE_LEVEL: object.SOURCE_LEVEL,
      OWNER_POSITION_STATE: object.OWNER_POSITION_STATE,
      DOES_NOT_ASSERT: object.DOES_NOT_ASSERT,
      CORRECTION_RATIONALE: metadataFallback ? "Parser selected metadata/label rather than claim-bearing source fields." : needsLocatorCorrection ? "Synthetic fragment anchor did not resolve; successor points to the actual repository record." : candidateClassError ? "CANDIDATE_HYPOTHESIS must not be strengthened to WORKING_HYPOTHESIS by normalization." : "Successor restores material context omitted by the v0.1 statement.",
      RAW_PRIMARY_SOURCE_VERIFICATION: object.CORPUS_GROUP === "C_EXISTING_SOURCE_NORMALIZED_AS_IS" ? "NOT_PERFORMED" : "NOT_APPLICABLE"
    });
  }
}

const splitRecords = [
  {
    PREDECESSOR_OBJECT_ID: "CX-LIVE-BRAINSTORM-0042",
    REASON: "A single v0.1 object uses OBJECT_ID as statement and bundles ten independently testable experiment candidates.",
    SUCCESSORS: [
      "same Memory/state + different model/runtime -> compare instantiated Persona",
      "same model/runtime + different experience history -> compare Persona divergence",
      "remove persisted SELF_MODEL -> test self reconstruction",
      "change SELF/Memory root -> measure self/continuity interpretation",
      "alter selected Current Status dimensions -> measure loss after reinstantiation",
      "provider/environment swap -> re-bind functions and compare behavior",
      "mutate external-reference target while locator remains constant",
      "delete source memory while preserving derived heuristics",
      "shared evidence/separate interpretation versus shared interpretation",
      "reconstruct the same state with multiple fresh instances"
    ].map((statement, i) => ({SUCCESSOR_OBJECT_ID: `V02-SPLIT-EXP-${String(i + 1).padStart(2, "0")}`, STATEMENT: statement}))
  },
  {
    PREDECESSOR_OBJECT_ID: "CX-LIVE-WORLDVIEW-0009",
    REASON: "The parser let WORLDVIEW-H-05 consume later Memory-boundary, challenge, preservation, unresolved-question, and usage-rule sections.",
    SUCCESSORS: [
      "Digital discontinuity is a native operating condition.",
      "The Memory boundary is intentionally not fully defined.",
      "Too-narrow Memory excludes identity-bearing state.",
      "Too-broad Memory makes Identity=Memory unfalsifiable.",
      "The research baseline must remain attackable.",
      "Agreement count is not evidence weight.",
      "Material worldview change requires a preserved successor record.",
      "Seven continuity/Memory questions remain unresolved.",
      "Use the baseline as a starting reference while allowing attack."
    ].map((statement, i) => ({SUCCESSOR_OBJECT_ID: `V02-SPLIT-WORLDVIEW-${String(i + 1).padStart(2, "0")}`, STATEMENT: statement}))
  }
];

const mergeCandidates = [
  {MERGE_CANDIDATE_ID: "V02-MERGE-0001", OBJECT_IDS: ["CX-SRC-SRC-MI0-SRC-MI1-0003", "CX-SRC-SRC-R3-0003"], ASSESSMENT: "POSSIBLE_SEMANTIC_EQUIVALENCE", NOTE: "Both state MEMORY != AUTHORITY, but preserve separate source provenance and source-era status."},
  {MERGE_CANDIDATE_ID: "V02-MERGE-0002", OBJECT_IDS: ["CX-SRC-SRC-R3-0020", "CX-LIVE-BRAINSTORM-0036"], ASSESSMENT: "POSSIBLE_SEMANTIC_EQUIVALENCE", NOTE: "Same formula across historical normalized and later live layers; link rather than collapse provenance."},
  {MERGE_CANDIDATE_ID: "V02-MERGE-REJECT-0001", OBJECT_IDS: ["CX-SRC-SRC-WP1-SRC-WP2-0001", "CX-SRC-SRC-WP1-SRC-WP2-0002", "CX-SRC-SRC-WP1-SRC-WP2-0003"], ASSESSMENT: "NOT_EQUIVALENT", NOTE: "Lexical equality came from parser fallback TENSION; underlying A/B conflicts differ."},
  {MERGE_CANDIDATE_ID: "V02-MERGE-REJECT-0002", OBJECT_IDS: ["CX-SRC-SRC-MI1-0042", "CX-SRC-SRC-R2-0018"], ASSESSMENT: "NOT_EQUIVALENT", NOTE: "Both lost their dimension lists to CLASS fallback; their evaluation dimensions differ."}
];

for (const directory of ["extraction-qa", "source-derived", "live"]) fs.mkdirSync(path.join(out, directory), {recursive: true});
const writeJsonl = (relative, rows) => fs.writeFileSync(path.join(out, relative), rows.map((row) => JSON.stringify(row)).join("\n") + "\n");
writeJsonl("extraction-qa/v01_object_qa.jsonl", qa);
writeJsonl("extraction-qa/corrections.jsonl", corrections);
writeJsonl("extraction-qa/splits.jsonl", splitRecords);
writeJsonl("extraction-qa/merge_candidates.jsonl", mergeCandidates);
writeJsonl("source-derived/corrected_objects.jsonl", corrections.filter((row) => row.CORPUS_GROUP === "C_EXISTING_SOURCE_NORMALIZED_AS_IS"));
writeJsonl("live/corrected_live_objects.jsonl", corrections.filter((row) => row.CORPUS_GROUP === "D_LIVE_BRAINSTORM_AS_IS"));

const counts = qa.reduce((map, row) => (map[row.QA_STATUS] = (map[row.QA_STATUS] || 0) + 1, map), {});
console.log(JSON.stringify({objects: objects.length, qa: qa.length, corrections: corrections.length, split_predecessors: splitRecords.length, merge_reviews: mergeCandidates.length, statuses: counts}, null, 2));
