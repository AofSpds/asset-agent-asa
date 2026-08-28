import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const base = path.join(root, "control/research/asa-mi/codex-source-mining-drafts/2026-08-20-v0.1");
const inputs = [
  "source-derived/objects.jsonl",
  "live-brainstorm/objects.jsonl",
  "codex-inferred/objects.jsonl",
];
const objects = inputs.flatMap((file) => fs.readFileSync(path.join(base, file), "utf8").trim().split(/\r?\n/).map((line) => ({...JSON.parse(line), file})));
const start = Number(process.argv[2] ?? 1);
const count = Number(process.argv[3] ?? objects.length);
for (const [offset, object] of objects.slice(start - 1, start - 1 + count).entries()) {
  const record = String(object.SOURCE_RECORD_TEXT ?? "").replace(/\r?\n/g, " ␞ ");
  console.log(`${start + offset}\t${object.OBJECT_ID}\t${object.ORIGIN_OBJECT_ID || "-"}\t${object.CLASS}/${object.SUBCLASS || "-"}\t${object.STATEMENT}\tREC=${record}`);
}
