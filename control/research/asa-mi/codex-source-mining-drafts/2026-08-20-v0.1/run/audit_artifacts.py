#!/usr/bin/env python3
"""Read-only integrity audit for the generated ASA-MI draft package."""

from __future__ import annotations

import csv
import json
import sys
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve()
OUT = HERE.parents[1]
REPO = HERE.parents[6]


def load_jsonl(path: Path, errors: list[str]) -> list[dict]:
    rows = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            errors.append(f"JSON_PARSE:{path.relative_to(OUT)}:{line_no}:{exc}")
    return rows


def main() -> int:
    errors: list[str] = []
    source = load_jsonl(OUT / "source-derived" / "objects.jsonl", errors)
    live = load_jsonl(OUT / "live-brainstorm" / "objects.jsonl", errors)
    inferred = load_jsonl(OUT / "codex-inferred" / "objects.jsonl", errors)
    relations = load_jsonl(OUT / "crosswalk" / "relations_candidates.jsonl", errors)
    index = load_jsonl(OUT / "run" / "object_index.jsonl", errors)
    objects = source + live + inferred

    ids = [row.get("OBJECT_ID") for row in objects]
    if len(ids) != len(set(ids)):
        errors.append("OBJECT_ID_NOT_UNIQUE")
    relation_ids = [row.get("RELATION_ID") for row in relations]
    if len(relation_ids) != len(set(relation_ids)):
        errors.append("RELATION_ID_NOT_UNIQUE")
    if len(index) != len(objects) or {row["OBJECT_ID"] for row in index} != set(ids):
        errors.append("OBJECT_INDEX_MISMATCH")

    required_object_fields = {"OBJECT_ID", "CORPUS_GROUP", "CLASS", "STATEMENT", "SOURCE_LOCATOR", "SOURCE_LEVEL", "INFERENCE_STATE"}
    for row in objects:
        missing = required_object_fields - row.keys()
        if missing:
            errors.append(f"OBJECT_FIELDS:{row.get('OBJECT_ID')}:{sorted(missing)}")
    for row in source + live:
        if not row.get("ORIGIN_OBJECT_ID"):
            errors.append(f"ORIGIN_ID_MISSING:{row.get('OBJECT_ID')}")
        locator = row.get("SOURCE_LOCATOR", "").split("#", 1)[0]
        if locator and not (REPO / locator).is_file():
            errors.append(f"SOURCE_LOCATOR_MISSING:{row.get('OBJECT_ID')}:{locator}")
    if any(row.get("SOURCE_LEVEL") != "SECONDARY_NORMALIZED_SOURCE" for row in source):
        errors.append("SOURCE_LEVEL_SOURCE_DERIVED")
    if any(row.get("SOURCE_LEVEL") == "SECONDARY_NORMALIZED_SOURCE" for row in live):
        errors.append("SOURCE_LEVEL_LIVE_COLLAPSED_TO_HISTORICAL")
    if any(row.get("SOURCE_LEVEL") != "CODEX_INFERENCE" for row in inferred):
        errors.append("SOURCE_LEVEL_CODEX_INFERENCE")

    object_ids = set(ids)
    for row in relations:
        if row.get("FROM_OBJECT_ID") not in object_ids or row.get("TO_OBJECT_ID") not in object_ids:
            errors.append(f"RELATION_ENDPOINT:{row.get('RELATION_ID')}")
        if row.get("STATE") != "CANDIDATE_NOT_OWNER_TAGGED":
            errors.append(f"RELATION_STATE:{row.get('RELATION_ID')}")

    with (OUT / "run" / "02_SOURCE_INVENTORY.csv").open(encoding="utf-8-sig", newline="") as handle:
        inventory = list(csv.DictReader(handle))
    if len(inventory) != 18:
        errors.append(f"INVENTORY_COUNT:{len(inventory)}")
    inv_counts = Counter(row["CORPUS_CLASS"] for row in inventory)
    if inv_counts["HISTORICAL_SOURCE_NORMALIZED"] != 13:
        errors.append(f"HISTORICAL_FILE_COUNT:{inv_counts['HISTORICAL_SOURCE_NORMALIZED']}")
    if inv_counts["LIVE_RESEARCH"] + inv_counts["REFERENCE"] != 5:
        errors.append("LIVE_REFERENCE_FILE_COUNT")
    if any(row["MINED"] != "YES" for row in inventory):
        errors.append("UNMINED_INVENTORY_FILE")

    with (OUT / "tagging" / "02_TAGGING_QUEUE.csv").open(encoding="utf-8-sig", newline="") as handle:
        queue = list(csv.DictReader(handle))
    if len(queue) != len(objects):
        errors.append(f"TAGGING_QUEUE_COUNT:{len(queue)}:{len(objects)}")
    if {row["OBJECT_ID"] for row in queue} != object_ids:
        errors.append("TAGGING_QUEUE_OBJECT_SET")

    required = [
        "run/00_README_SCOPE_AND_ISOLATION.md", "run/01_SOURCE_INVENTORY.md", "run/02_SOURCE_INVENTORY.csv",
        "run/03_RAW_SOURCE_MISSINGNESS.md", "run/04_BASELINE_IDENTITY_RECEIPT.md", "run/05_PASS_MANIFEST.md",
        "run/06_OBJECT_COUNT_REPORT.md", "run/07_INTEGRITY_AUDIT.md", "run/08_REMOTE_MOVEMENT_CHECK.md", "run/09_RUN_MANIFEST.md",
        "source-derived/objects.jsonl", "live-brainstorm/objects.jsonl", "codex-inferred/objects.jsonl",
        "crosswalk/relations_candidates.jsonl", "crosswalk/04_HYPOTHESIS_FAMILY_MAP.md",
        "comparison/03_AS_IS_TO_BE_GAP_MATRIX.csv", "comparison/06_HISTORICAL_SOURCE_VS_LIVE_BRAINSTORM.md",
        "comparison/07_RECALL_GAIN_REPORT.md", "tagging/01_TAGGING_QUEUE.md", "tagging/02_TAGGING_QUEUE.csv",
        "tagging/03_TAGGING_GUIDE.md", "tagging/04_PRIORITY_REVIEW_SETS.md",
    ]
    for rel_path in required:
        if not (OUT / rel_path).is_file():
            errors.append(f"REQUIRED_FILE:{rel_path}")

    checkpoints = OUT / "run" / "checkpoints"
    if len(list(checkpoints.glob("FULL_SWEEP_*.md"))) != 4:
        errors.append("FULL_SWEEP_CHECKPOINT_COUNT")
    if len(list(checkpoints.glob("SPECIAL_PASS_*.md"))) != 11:
        errors.append("SPECIAL_PASS_CHECKPOINT_COUNT")
    if len(list(checkpoints.glob("SATURATION_*.md"))) != 2:
        errors.append("SATURATION_CHECKPOINT_COUNT")
    missingness = (OUT / "run" / "03_RAW_SOURCE_MISSINGNESS.md").read_text(encoding="utf-8")
    for source_id in ["SRC-WP1", "SRC-WP2", "SRC-MI0", "SRC-MI1", "SRC-R1", "SRC-R2", "SRC-R3"]:
        if source_id not in missingness:
            errors.append(f"RAW_SOURCE_MISSINGNESS:{source_id}")

    class_counts = Counter(row["CLASS"] for row in objects)
    summary = {
        "STATE": "PASS" if not errors else "FAIL",
        "ERRORS": errors,
        "REPOSITORY_CORPUS_FILE_COUNT": len(inventory),
        "HISTORICAL_NORMALIZED_FILE_COUNT": inv_counts["HISTORICAL_SOURCE_NORMALIZED"],
        "LIVE_RESEARCH_AND_REFERENCE_FILE_COUNT": inv_counts["LIVE_RESEARCH"] + inv_counts["REFERENCE"],
        "SOURCE_DERIVED_OBJECT_COUNT": len(source),
        "LIVE_OBJECT_COUNT": len(live),
        "CODEX_INFERRED_OBJECT_COUNT": len(inferred),
        "OBJECT_COUNT_BY_CLASS": dict(sorted(class_counts.items())),
        "RELATION_CANDIDATE_COUNT": len(relations),
        "POSSIBLE_SEMANTIC_EQUIVALENCE_COUNT": sum(row["RELATION"] == "POSSIBLE_SEMANTIC_EQUIVALENCE" for row in relations),
        "RAW_SOURCE_MISSING_COUNT": 7,
        "TAGGING_QUEUE_COUNT": len(queue),
        "OUTPUT_FILE_COUNT": sum(path.is_file() for path in OUT.rglob("*")),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
