import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const v01 = path.join(root, "control/research/asa-mi/codex-source-mining-drafts/2026-08-20-v0.1");
const files = [
  "source-derived/objects.jsonl",
  "live-brainstorm/objects.jsonl",
  "codex-inferred/objects.jsonl",
];

const objects = files.flatMap((relativePath) =>
  fs.readFileSync(path.join(v01, relativePath), "utf8")
    .trimEnd()
    .split(/\r?\n/)
    .map((line, index) => ({ ...JSON.parse(line), _file: relativePath, _line: index + 1 })),
);

const counter = (values) => Object.fromEntries(
  [...values.reduce((map, value) => map.set(value, (map.get(value) ?? 0) + 1), new Map())]
    .sort((a, b) => b[1] - a[1] || String(a[0]).localeCompare(String(b[0]))),
);

const issues = new Map();
const add = (kind, value) => issues.set(kind, [...(issues.get(kind) ?? []), value]);

for (const object of objects) {
  const statement = String(object.STATEMENT ?? "").trim();
  const record = String(object.SOURCE_RECORD_TEXT ?? "");
  if (!statement) add("EMPTY_STATEMENT", object.OBJECT_ID);
  if (statement === object.OBJECT_ID || statement === object.ORIGIN_OBJECT_ID) add("ID_AS_STATEMENT", object.OBJECT_ID);
  if (statement && !record.includes(statement) && object.INFERENCE_STATE !== "CODEX_INFERRED_CANDIDATE") {
    add("STATEMENT_NOT_IN_RECORD", { object_id: object.OBJECT_ID, statement, record_excerpt: record.slice(0, 180) });
  }
  if (object.SHORT_FORM === object.OBJECT_ID || object.SHORT_FORM === object.ORIGIN_OBJECT_ID) add("ID_AS_SHORT_FORM", object.OBJECT_ID);
  if (object.INFERENCE_STATE !== "CODEX_INFERRED_CANDIDATE") {
    const [relativePath, anchor = ""] = String(object.SOURCE_LOCATOR ?? "").split("#", 2);
    const target = path.join(root, relativePath);
    if (!fs.existsSync(target)) add("BAD_PATH", { object_id: object.OBJECT_ID, locator: object.SOURCE_LOCATOR });
    else if (anchor && !fs.readFileSync(target, "utf8").includes(anchor)) add("BAD_ANCHOR", { object_id: object.OBJECT_ID, locator: object.SOURCE_LOCATOR });
  }
}

const normalized = new Map();
for (const object of objects) {
  const key = String(object.STATEMENT ?? "").toLocaleLowerCase().replace(/[\p{P}\p{S}\s]+/gu, "");
  if (!key) continue;
  normalized.set(key, [...(normalized.get(key) ?? []), object.OBJECT_ID]);
}
const lexicalDuplicateGroups = [...normalized.values()].filter((ids) => ids.length > 1);

console.log(JSON.stringify({
  total: objects.length,
  corpus_group: counter(objects.map((object) => object.CORPUS_GROUP)),
  class: counter(objects.map((object) => object.CLASS)),
  subclass: counter(objects.map((object) => object.SUBCLASS ?? "")),
  recovery_pass: counter(objects.map((object) => object.RECOVERY_PASS ?? "")),
  issues: Object.fromEntries([...issues].map(([kind, values]) => [kind, { count: values.length, examples: values.slice(0, 40) }])),
  lexical_duplicate_groups: lexicalDuplicateGroups.length,
  lexical_duplicate_objects: lexicalDuplicateGroups.reduce((sum, ids) => sum + ids.length, 0),
  lexical_duplicate_examples: lexicalDuplicateGroups.slice(0, 60),
}, null, 2));
