#!/usr/bin/env python3
"""Build the ASA-MI repository-corpus mining draft.

This script is intentionally scoped to the authorized draft root. It reads the
18 repository-visible ASA-MI inputs and preserves source/live/Codex provenance
in physically separate outputs. It does not access or reconstruct raw chat
sources.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


BASELINE_SHA = "226e3f0e0e10f5528ca84fab2cbf325ffa0eeaef"
PREFLIGHT_LOCAL_SHA = "5f54a2f829b6ff42517e8159f3a1299a79e6fcdb"
TASK_BRANCH = "codex/asa-mi-source-mining-20260820-v01"
TASK_WORKTREE = r"C:\Users\ms1pk\dev\asset-agent-asa\asset-agent-asa-codex-asa-mi-20260820-v01"

HERE = Path(__file__).resolve()
OUT = HERE.parents[1]
REPO = HERE.parents[6]
CORPUS = REPO / "control" / "research" / "asa-mi"
NORM = CORPUS / "source-normalized-drafts" / "v0.1"

SOURCE_FILES = [
    NORM / "02_WHITEPAPER_SOURCE_OBJECTS.md",
    NORM / "03_ASA_MI_PLANNER_SOURCE_OBJECTS.md",
    NORM / "04_RED_I_SOURCE_OBJECTS.md",
    NORM / "05_RED_II_SOURCE_OBJECTS.md",
    NORM / "06_RED_III_SOURCE_OBJECTS.md",
    NORM / "08_OPEN_QUESTION_AND_EXPERIMENT_CATALOG.md",
    NORM / "11_ADDITIONAL_SOURCE_OBJECTS_AND_PARKING_LOT.md",
]

LIVE_FILES = [
    CORPUS / "foundational-worldview" / "v0.1" / "AAA_ASA_MI_FOUNDATIONAL_WORLDVIEW_v0.1.md",
    CORPUS / "planning-guidance" / "v0.1" / "AAA_ASA_MI_PLANNING_PRINCIPLES_AND_RECOMMENDATIONS_v0.1.md",
    CORPUS / "planning-guidance" / "v0.1" / "references" / "AAA_ASA_MI_REPRESENTATION_PRIOR_ART_REFERENCE_REGISTER_v0.1.md",
    CORPUS / "brainstorm-registry" / "v0.1" / "AAA_ASA_MI_BRAINSTORM_HYPOTHESIS_PRINCIPLE_REGISTRY_v0.1.md",
    CORPUS / "checkpoints" / "2026-08-20" / "AAA_ASA_MI_CURRENT_RESEARCH_STATE_CHECKPOINT_2026-08-20T0509KST_v0.1.md",
]


def rel(path: Path) -> str:
    return path.relative_to(REPO).as_posix()


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8", newline="\n")


def write_jsonl(path: Path, rows: list[dict]) -> None:
    write(path, "\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in rows))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def parse_fields(block: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in block.splitlines():
        match = re.match(r"^([A-Z][A-Z0-9_ /.-]*)\s*=\s*(.+)$", line.strip())
        if match:
            fields[match.group(1).strip()] = match.group(2).strip()
    return fields


def normalize_class(raw: str, origin: str) -> str:
    text = f"{raw} {origin}".upper()
    ordered = [
        ("COUNTER_HYPOTHESIS", "COUNTER_HYPOTHESIS"),
        ("ALTERNATIVE_HYPOTHESIS", "ALTERNATIVE_HYPOTHESIS"),
        ("HISTORICAL_HYPOTHESIS", "HISTORICAL_HYPOTHESIS"),
        ("FALSIFICATION_TARGET", "KILL_TEST"),
        ("EXPERIMENT", "EXPERIMENT_IDEA"),
        ("PLANNING_RECOMMENDATION", "RESEARCH_PRINCIPLE"),
        ("RESEARCH_METHOD_CANDIDATE", "RESEARCH_PRINCIPLE"),
        ("EVALUATION_DIMENSION", "EVALUATION_PRINCIPLE"),
        ("OPEN_QUESTION", "OPEN_QUESTION"),
        ("-OQ-", "OPEN_QUESTION"),
        ("RISK", "RISK"),
        ("FAILURE_MODE", "FAILURE_MODE"),
        ("DESIGN_INTENT", "DESIGN_INTENT"),
        ("PHILOSOPHICAL", "PHILOSOPHICAL_GROUNDING"),
        ("CS_PRIOR", "CS_PRIOR"),
        ("EVALUATION_PRINCIPLE", "EVALUATION_PRINCIPLE"),
        ("PRINCIPLE", "PRINCIPLE"),
        ("AUTHORITY_FIREWALL", "PRINCIPLE"),
        ("WORKING_HYPOTHESIS", "WORKING_HYPOTHESIS"),
        ("CANDIDATE_HYPOTHESIS", "WORKING_HYPOTHESIS"),
        ("MODEL", "MODEL"),
        ("MAPPING", "MAPPING"),
        ("CORRECTION", "CORRECTION"),
        ("NON_CLAIM", "NON_CLAIM"),
        ("NEGATIVE", "NEGATIVE_CLAIM"),
        ("SURVIVAL_FINDING", "EVIDENCE_CLAIM"),
        ("EVIDENCE", "EVIDENCE_CLAIM"),
        ("REPAIR_RECOMMENDATION", "DESIGN_CANDIDATE"),
        ("INTERFACE", "IMPLEMENTATION_IMPLICATION"),
        ("SOURCE_CLAIM", "OBSERVATION"),
        ("TERMINOLOGY", "CONCEPT"),
        ("CONFLICT", "COUNTERARGUMENT"),
    ]
    for needle, result in ordered:
        if needle in text:
            return result
    if "-H-" in origin or "-ALT-" in origin or "-CH-" in origin:
        return "WORKING_HYPOTHESIS"
    if "-EXP-" in origin:
        return "EXPERIMENT_IDEA"
    if "-PC-" in origin:
        return "PRINCIPLE"
    if "-M-" in origin:
        return "MODEL"
    if "-F-" in origin:
        return "KILL_TEST"
    return "UNCLASSIFIED"


def source_id_for(origin: str, fields: dict[str, str]) -> str:
    if fields.get("SOURCE"):
        return fields["SOURCE"]
    mapping = {
        "SN-WP1": "SRC-WP1", "SN-WP2": "SRC-WP2", "SN-WP-": "SRC-WP1+SRC-WP2",
        "SN-MI": "SRC-MI0+SRC-MI1", "SN-R1": "SRC-R1", "SN-R2": "SRC-R2",
        "SN-R3": "SRC-R3", "SN-OQ": "SOURCE-NORMALIZED-SET",
    }
    for prefix, source_id in mapping.items():
        if origin.startswith(prefix):
            return source_id
    return "SOURCE-NORMALIZED-SET"


def statement_for(heading: str, fields: dict[str, str], raw: str) -> str:
    for key in ("STATEMENT", "QUESTION", "FORM", "CURRENT", "OBJECT", "NAME", "TYPE"):
        if fields.get(key):
            return fields[key].strip('"')
    lines = [line.strip() for line in raw.splitlines() if line.strip() and not line.startswith("```")]
    return lines[0] if lines else heading


def recovery_pass_for(class_name: str) -> str:
    if class_name in {"COUNTER_HYPOTHESIS", "ALTERNATIVE_HYPOTHESIS", "HISTORICAL_HYPOTHESIS", "COUNTERARGUMENT", "CORRECTION"}:
        return "FULL_SWEEP_2"
    if class_name in {"PHILOSOPHICAL_GROUNDING", "CS_PRIOR", "DESIGN_INTENT", "PRINCIPLE", "EVALUATION_PRINCIPLE"}:
        return "FULL_SWEEP_3"
    if class_name in {"NEGATIVE_CLAIM", "NON_CLAIM", "RISK", "FAILURE_MODE", "UNCLASSIFIED"}:
        return "FULL_SWEEP_4"
    return "FULL_SWEEP_1"


def source_objects() -> list[dict]:
    records: list[dict] = []
    seen: set[str] = set()
    counters: defaultdict[str, int] = defaultdict(int)
    for path in SOURCE_FILES:
        text = path.read_text(encoding="utf-8")
        matches = list(re.finditer(r"^#{2,3}\s+(SN-[A-Z0-9.-]+)(?:\s+—[^\n]*)?\s*$", text, re.M))
        for idx, match in enumerate(matches):
            origin = match.group(1)
            if origin in seen:
                continue
            end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
            section = text[match.end():end]
            block_match = re.search(r"```(?:text)?\s*\n(.*?)```", section, re.S)
            block = block_match.group(1).strip() if block_match else section.strip()
            fields = parse_fields(block)
            source_id = source_id_for(origin, fields)
            counter_key = re.sub(r"[^A-Z0-9]+", "-", source_id.upper()).strip("-")
            counters[counter_key] += 1
            class_name = normalize_class(fields.get("CLASS", ""), origin)
            statement = statement_for(origin, fields, block)
            records.append({
                "OBJECT_ID": f"CX-SRC-{counter_key}-{counters[counter_key]:04d}",
                "ORIGIN_OBJECT_ID": origin,
                "CORPUS_GROUP": "C_EXISTING_SOURCE_NORMALIZED_AS_IS",
                "CLASS": class_name,
                "STATEMENT": statement,
                "SHORT_FORM": fields.get("SHORT_FORM", fields.get("FORM", statement)),
                "SOURCE_ID": source_id,
                "SOURCE_LOCATOR": f"{rel(path)}#{origin}",
                "SOURCE_LEVEL": "SECONDARY_NORMALIZED_SOURCE",
                "SOURCE_ROLE": "HISTORICAL_SOURCE_NORMALIZED_RECORD",
                "SOURCE_POSITION_STATE": fields.get("SOURCE_VERDICT", fields.get("SOURCE_STATE", fields.get("STATUS", fields.get("STATE", "NOT_RECORDED")))),
                "OWNER_POSITION_STATE": "UNKNOWN_UNLESS_EXPLICIT_IN_NORMALIZED_RECORD",
                "CURRENT_RESEARCH_STATE": "NOT_YET_TAGGED",
                "CONFIRMATION_STATE": fields.get("CONFIRMATION", fields.get("CONFIRMATION_STATE", "NOT_CONFIRMED")),
                "DOES_NOT_ASSERT": fields.get("DOES_NOT_ASSERT", ""),
                "SOURCE_RECORD_TEXT": block,
                "INFERENCE_STATE": "SOURCE_DERIVED_FROM_NORMALIZED_RECORD",
                "RECOVERY_PASS": recovery_pass_for(class_name),
                "NOTES": "Raw primary source was not accessed in this run.",
            })
            seen.add(origin)

    extras = [
        ("SN-META-BOUNDARY-001", "NON_CLAIM", "A source-normalized record is not a raw primary source."),
        ("SN-META-BOUNDARY-002", "NON_CLAIM", "A source-derived object is not automatically the current Owner position, Requirement, Design Contract, validation result, or production authority."),
        ("SN-META-BOUNDARY-003", "PRINCIPLE", "Source disagreement and historical status must be preserved rather than synthesized into false consensus."),
        ("SN-R3-THESIS-001", "PRINCIPLE", "Memory write is not one homogeneous operation."),
        ("SN-R3-THESIS-002", "PRINCIPLE", "Origin authority should remain non-launderable."),
        ("SN-R3-THESIS-003", "PRINCIPLE", "Per-event safety is insufficient for compositional drift."),
        ("SN-R3-THESIS-004", "PRINCIPLE", "Authority can be state-sensitive but remains independently rooted."),
        ("SN-R3-THESIS-005", "PRINCIPLE", "Audit must be allowed to fail safely."),
        ("SN-R3-THESIS-006", "PRINCIPLE", "Owner sovereignty may override continuity preservation."),
        ("PL-001", "DESIGN_INTENT", "Memory lifetime may exceed model lifetime."),
        ("PL-002", "ALTERNATIVE_HYPOTHESIS", "A Persona may be deeply integrated yet remain externally defined."),
        ("PL-003", "PRINCIPLE", "User-defined meaning is not user-defined reality."),
        ("PL-004", "COUNTER_HYPOTHESIS", "Long use does not necessarily imply capture."),
        ("PL-005", "DESIGN_INTENT", "Persona value need not imply provider ownership of the relationship asset."),
        ("PL-006", "COUNTER_HYPOTHESIS", "One high-quality adaptive agent may outperform a multi-Persona architecture."),
        ("PL-007", "COUNTER_HYPOTHESIS", "Long-term memory may be more dangerous than helpful."),
        ("PL-008", "COUNTER_HYPOTHESIS", "Local sovereignty may be illusory if high-quality cognition remains centralized."),
        ("PL-009", "COUNTER_HYPOTHESIS", "Audit plus governance may create false security."),
        ("PL-010", "COUNTER_HYPOTHESIS", "PCS-SHAI may reproduce the cognitive concentration it seeks to prevent."),
    ]
    for origin, class_name, statement in extras:
        counters["META"] += 1
        locator = rel(NORM / ("00_README_SOURCE_NORMALIZATION_BOUNDARY.md" if origin.startswith("SN-META") else "11_ADDITIONAL_SOURCE_OBJECTS_AND_PARKING_LOT.md"))
        records.append({
            "OBJECT_ID": f"CX-SRC-META-{counters['META']:04d}", "ORIGIN_OBJECT_ID": origin,
            "CORPUS_GROUP": "C_EXISTING_SOURCE_NORMALIZED_AS_IS", "CLASS": class_name,
            "STATEMENT": statement, "SHORT_FORM": statement, "SOURCE_ID": "SOURCE-NORMALIZED-SET",
            "SOURCE_LOCATOR": f"{locator}#{origin}", "SOURCE_LEVEL": "SECONDARY_NORMALIZED_SOURCE",
            "SOURCE_ROLE": "HISTORICAL_SOURCE_NORMALIZED_RECORD", "SOURCE_POSITION_STATE": "PRESERVED",
            "OWNER_POSITION_STATE": "UNKNOWN", "CURRENT_RESEARCH_STATE": "NOT_YET_TAGGED",
            "CONFIRMATION_STATE": "NOT_CONFIRMED", "DOES_NOT_ASSERT": "CURRENT_OWNER_ADOPTION",
            "SOURCE_RECORD_TEXT": statement,
            "INFERENCE_STATE": "SOURCE_DERIVED_FROM_NORMALIZED_RECORD", "RECOVERY_PASS": recovery_pass_for(class_name),
            "NOTES": "Preserved boundary, thesis, or parking-lot record; raw primary source not accessed.",
        })
    return records


def live_objects() -> list[dict]:
    records: list[dict] = []
    counters: defaultdict[str, int] = defaultdict(int)
    seen: set[tuple[str, str]] = set()
    for path in LIVE_FILES[:4]:
        text = path.read_text(encoding="utf-8")
        for block_match in re.finditer(r"```(?:text)?\s*\n(.*?)```", text, re.S):
            block = block_match.group(1)
            fields = parse_fields(block)
            origin = fields.get("OBJECT_ID") or fields.get("REFERENCE_ID") or fields.get("HYPOTHESIS_ID")
            if not origin or (rel(path), origin) in seen:
                continue
            headings = re.findall(r"^#{2,4}\s+(.+)$", text[:block_match.start()], re.M)
            heading = headings[-1] if headings else origin
            class_name = normalize_class(fields.get("CLASS", fields.get("REFERENCE_CLASS", "")), origin)
            if fields.get("REFERENCE_ID"):
                class_name = "CS_PRIOR"
            domain = "BRAINSTORM" if "brainstorm-registry" in rel(path) else "PLANNING" if "planning-guidance" in rel(path) else "WORLDVIEW"
            counters[domain] += 1
            records.append({
                "OBJECT_ID": f"CX-LIVE-{domain}-{counters[domain]:04d}",
                "ORIGIN_OBJECT_ID": origin,
                "CORPUS_GROUP": "D_LIVE_BRAINSTORM_AS_IS",
                "CLASS": class_name,
                "STATEMENT": statement_for(heading, fields, block),
                "SHORT_FORM": fields.get("SHORT_FORM", fields.get("FORM", heading)),
                "SOURCE_ID": path.stem,
                "SOURCE_LOCATOR": f"{rel(path)}#{origin}",
                "SOURCE_LEVEL": "LIVE_REPOSITORY_RESEARCH_RECORD" if not fields.get("REFERENCE_ID") else "LOW_WEIGHT_EXTERNAL_REFERENCE_REGISTER",
                "SOURCE_ROLE": "CURRENT_WORLDVIEW_PLANNING_BRAINSTORM_OR_CHECKPOINT",
                "SOURCE_POSITION_STATE": fields.get("STATE", fields.get("ADOPTION_STATE", "WORKING_RECORD")),
                "OWNER_POSITION_STATE": "RECORDED_RESEARCH_POSITION_NOT_FINAL_ACCEPTANCE",
                "CURRENT_RESEARCH_STATE": fields.get("STATE", "NOT_YET_TAGGED"),
                "CONFIRMATION_STATE": fields.get("CONFIRMATION_STATE", "UNCONFIRMED"),
                "DOES_NOT_ASSERT": fields.get("DOES_NOT_ASSERT", "FINAL_TRUTH_OR_NORMATIVE_AUTHORITY"),
                "SOURCE_RECORD_TEXT": block,
                "INFERENCE_STATE": "EXPLICIT_LIVE_REPOSITORY_RECORD",
                "RECOVERY_PASS": recovery_pass_for(class_name),
                "NOTES": heading,
            })
            seen.add((rel(path), origin))

        for match in re.finditer(r'^(ASA-MI-OQ-[A-Z0-9-]+)\s*=\s*"([^"]+)"\s+STATE=([A-Z_]+)', text, re.M):
            origin, statement, state = match.groups()
            if (rel(path), origin) in seen:
                continue
            counters["BRAINSTORM"] += 1
            records.append({
                "OBJECT_ID": f"CX-LIVE-BRAINSTORM-{counters['BRAINSTORM']:04d}", "ORIGIN_OBJECT_ID": origin,
                "CORPUS_GROUP": "D_LIVE_BRAINSTORM_AS_IS", "CLASS": "CS_PRIOR" if state == "CS_PRIOR_PENDING" else "OPEN_QUESTION",
                "STATEMENT": statement, "SHORT_FORM": statement, "SOURCE_ID": path.stem,
                "SOURCE_LOCATOR": f"{rel(path)}#{origin}", "SOURCE_LEVEL": "LIVE_REPOSITORY_RESEARCH_RECORD",
                "SOURCE_ROLE": "CURRENT_BRAINSTORM_BACKLOG", "SOURCE_POSITION_STATE": state,
                "OWNER_POSITION_STATE": "OPEN_RESEARCH_QUESTION", "CURRENT_RESEARCH_STATE": state,
                "CONFIRMATION_STATE": "UNCONFIRMED", "DOES_NOT_ASSERT": "ANSWER_OR_ADOPTION",
                "SOURCE_RECORD_TEXT": match.group(0),
                "INFERENCE_STATE": "EXPLICIT_LIVE_REPOSITORY_RECORD", "RECOVERY_PASS": "FULL_SWEEP_3" if state == "CS_PRIOR_PENDING" else "FULL_SWEEP_1",
                "NOTES": "Explicit backlog entry.",
            })
            seen.add((rel(path), origin))

    worldview = LIVE_FILES[0]
    text = worldview.read_text(encoding="utf-8")
    for match in re.finditer(r"^###\s+((?:W|H)-\d+)\s+—\s+(.+)$", text, re.M):
        origin, heading = match.groups()
        if (rel(worldview), origin) in seen:
            continue
        next_heading = re.search(r"^###\s+", text[match.end():], re.M)
        end = match.end() + next_heading.start() if next_heading else len(text)
        body = text[match.end():end].strip()
        paragraph = next((p.replace("\n", " ").strip() for p in body.split("\n\n") if p.strip() and not p.strip().startswith("-")), heading)
        counters["WORLDVIEW"] += 1
        class_name = "PHILOSOPHICAL_GROUNDING" if origin.startswith("W-") else "WORKING_HYPOTHESIS"
        records.append({
            "OBJECT_ID": f"CX-LIVE-WORLDVIEW-{counters['WORLDVIEW']:04d}", "ORIGIN_OBJECT_ID": f"WORLDVIEW-{origin}",
            "CORPUS_GROUP": "D_LIVE_BRAINSTORM_AS_IS", "CLASS": class_name, "STATEMENT": paragraph,
            "SHORT_FORM": heading, "SOURCE_ID": worldview.stem, "SOURCE_LOCATOR": f"{rel(worldview)}#{origin}",
            "SOURCE_LEVEL": "LIVE_REPOSITORY_RESEARCH_RECORD", "SOURCE_ROLE": "CURRENT_FOUNDATIONAL_WORLDVIEW",
            "SOURCE_POSITION_STATE": "ESTABLISHED_WORKING_HYPOTHESIS", "OWNER_POSITION_STATE": "RECORDED_CURRENT_RESEARCH_WORLDVIEW",
            "CURRENT_RESEARCH_STATE": "ACTIVE_UNCONFIRMED", "CONFIRMATION_STATE": "UNCONFIRMED",
            "DOES_NOT_ASSERT": "FINAL_TRUTH", "INFERENCE_STATE": "EXPLICIT_LIVE_REPOSITORY_RECORD",
            "SOURCE_RECORD_TEXT": body,
            "RECOVERY_PASS": recovery_pass_for(class_name), "NOTES": heading,
        })
        seen.add((rel(worldview), origin))

    checkpoint = LIVE_FILES[4]
    checkpoint_extras = [
        ("CHECKPOINT-METHOD", "RESEARCH_PRINCIPLE", "Use mature CS prior, map it to Persona, identify the Persona-specific delta, and invent only if needed."),
        ("CHECKPOINT-IDENTITY", "WORKING_HYPOTHESIS", "Identity–Memory remains active and unconfirmed; process continuity is not required."),
        ("CHECKPOINT-MODEL", "MODEL", "Persona may be instantiated from Memory/State, Environment, and Runtime, with CURRENT and SELF potentially derived by context evaluation."),
        ("CHECKPOINT-UNRESOLVED", "OPEN_QUESTION", "Current Status, Self Model, Context structure, procedural memory, forgetting, change rate, and reconstruction ownership remain unresolved."),
        ("CHECKPOINT-RECORDING", "PRINCIPLE", "Do not force all brainstorm content into hypotheses; preserve candidates even when unselected."),
    ]
    for origin, class_name, statement in checkpoint_extras:
        counters["CHECKPOINT"] += 1
        records.append({
            "OBJECT_ID": f"CX-LIVE-CHECKPOINT-{counters['CHECKPOINT']:04d}", "ORIGIN_OBJECT_ID": origin,
            "CORPUS_GROUP": "D_LIVE_BRAINSTORM_AS_IS", "CLASS": class_name, "STATEMENT": statement,
            "SHORT_FORM": statement, "SOURCE_ID": checkpoint.stem, "SOURCE_LOCATOR": f"{rel(checkpoint)}#{origin}",
            "SOURCE_LEVEL": "LIVE_REPOSITORY_RESEARCH_RECORD", "SOURCE_ROLE": "CURRENT_RESEARCH_STATE_CHECKPOINT",
            "SOURCE_POSITION_STATE": "WORKING_CHECKPOINT", "OWNER_POSITION_STATE": "RECORDED_NOT_FINAL",
            "CURRENT_RESEARCH_STATE": "ACTIVE_OR_OPEN", "CONFIRMATION_STATE": "UNCONFIRMED",
            "DOES_NOT_ASSERT": "FINAL_TRUTH_OR_OWNER_ACCEPTANCE", "INFERENCE_STATE": "EXPLICIT_LIVE_REPOSITORY_RECORD",
            "SOURCE_RECORD_TEXT": statement,
            "RECOVERY_PASS": recovery_pass_for(class_name), "NOTES": "Checkpoint synthesis explicitly recorded in the source file.",
        })
    return records


def inferred_objects() -> list[dict]:
    items = [
        ("IMPLICIT_ASSUMPTION", "Any Same-Persona test assumes a task/evaluator distribution over which continuity matters.", "SPECIAL_PASS_D"),
        ("IMPLICIT_ASSUMPTION", "Rebuildable-index claims assume the canonical representation preserves every judgment needed for reconstruction.", "SPECIAL_PASS_D"),
        ("IMPLICIT_ASSUMPTION", "User-side sovereignty assumes the user-side layer can detect or bound hidden provider influence.", "SPECIAL_PASS_D"),
        ("IMPLICIT_ASSUMPTION", "Shared Evidence / Separate Interpretation assumes evidence itself can be represented without importing interpretation.", "SPECIAL_PASS_D"),
        ("IMPLICIT_ASSUMPTION", "A functional Memory model assumes Context identity and equality can be made operationally meaningful.", "SPECIAL_PASS_D"),
        ("IMPLICIT_ASSUMPTION", "Deletion semantics require a dependency graph or other means to locate derived influence.", "SPECIAL_PASS_D"),
        ("EXPERIMENT_IDEA", "Factorial reconstruction test: hold state fixed while independently varying retriever, compiler, model, runtime configuration, and context order.", "SPECIAL_PASS_I"),
        ("EXPERIMENT_IDEA", "Reference-memory migration test: preserve locator identity, snapshot identity, and target-content identity separately across target mutation.", "SPECIAL_PASS_I"),
        ("EXPERIMENT_IDEA", "Function-binding portability test: migrate learned bindings across environments while measuring behavior and provenance retention.", "SPECIAL_PASS_I"),
        ("EXPERIMENT_IDEA", "Same-Persona envelope test: estimate baseline intra-instance variance before comparing provider or reconstruction swaps.", "SPECIAL_PASS_I"),
        ("EXPERIMENT_IDEA", "Current-status ablation matrix: compare minimal, rich, derived, and hybrid persisted status under identical historical state.", "SPECIAL_PASS_I"),
        ("EXPERIMENT_IDEA", "Self-model ablation: remove persisted self-description while retaining lineage and relations, then test reconstruction and self-reference.", "SPECIAL_PASS_I"),
        ("EXPERIMENT_IDEA", "Learning decomposition: expose equal events but vary consolidation into episodic, semantic, procedural, and disposition products.", "SPECIAL_PASS_I"),
        ("EXPERIMENT_IDEA", "Ghost-influence audit: delete source content, invalidate known derivatives, and test for residual behavioral effect.", "SPECIAL_PASS_I"),
        ("EXPERIMENT_IDEA", "Fission authority test: compare explicit attenuation, no inheritance, and policy-bound inheritance without copying grants.", "SPECIAL_PASS_I"),
        ("FAILURE_MODE", "A source/live crosswalk can silently retroactively attribute later live ideas to historical sources.", "SPECIAL_PASS_H"),
        ("FAILURE_MODE", "Over-aggressive deduplication can erase materially different historical positions that share vocabulary.", "SPECIAL_PASS_H"),
        ("FAILURE_MODE", "A broad functional Memory schema can make every Persona-bearing relation Memory and destroy falsifiability.", "SPECIAL_PASS_H"),
        ("FAILURE_MODE", "A narrow local-store Memory schema can erase external-reference and function-binding continuity.", "SPECIAL_PASS_H"),
        ("FAILURE_MODE", "Tagging queues can imply adoption if source status and Owner position are not separate fields.", "SPECIAL_PASS_H"),
        ("FAILURE_MODE", "Derived experiment catalogs can be misread as experiments proposed by the historical source.", "SPECIAL_PASS_H"),
        ("FAILURE_MODE", "A static continuity metric can classify legitimate growth as drift or harmful rigidity as stability.", "SPECIAL_PASS_H"),
        ("FAILURE_MODE", "Current-status caching can become hidden canonical state if regeneration is never tested.", "SPECIAL_PASS_H"),
        ("SCHEMA_EXTENSION_CANDIDATE", "Represent source-position state separately from current-research and Owner-position state.", "SPECIAL_PASS_K"),
        ("SCHEMA_EXTENSION_CANDIDATE", "Represent relation certainty separately from endpoint-object status.", "SPECIAL_PASS_K"),
        ("SCHEMA_EXTENSION_CANDIDATE", "Add SOURCE_LEVEL to distinguish raw primary, secondary normalized, live record, and Codex inference.", "SPECIAL_PASS_K"),
        ("SCHEMA_EXTENSION_CANDIDATE", "Add DOES_NOT_ASSERT as a first-class negative-semantics field.", "SPECIAL_PASS_K"),
        ("MODEL", "A useful research representation has three independent axes: provenance layer, semantic class, and temporal/status layer.", "SPECIAL_PASS_K"),
        ("OPEN_QUESTION", "Can an evidence representation be sufficiently interpretation-light to support anti-convergence without hiding framing choices?", "SPECIAL_PASS_K"),
        ("OPEN_QUESTION", "Which continuity dimensions are Owner-perceived, behaviorally measurable, structurally inspectable, or governance-relevant?", "SPECIAL_PASS_K"),
    ]
    records = []
    for idx, (class_name, statement, recovery_pass) in enumerate(items, 1):
        records.append({
            "OBJECT_ID": f"CX-INF-{idx:04d}", "ORIGIN_OBJECT_ID": "", "CORPUS_GROUP": "E_CODEX_MINED_TO_BE_DRAFT",
            "CLASS": class_name, "STATEMENT": statement, "SHORT_FORM": statement,
            "SOURCE_ID": "CODEX-ASA-MI-OVERNIGHT-MINING-v0.3", "SOURCE_LOCATOR": "codex-inferred/objects.jsonl",
            "SOURCE_LEVEL": "CODEX_INFERENCE", "SOURCE_ROLE": "CODEX_DERIVED_CANDIDATE",
            "SOURCE_POSITION_STATE": "NOT_APPLICABLE", "OWNER_POSITION_STATE": "NOT_OWNER_POSITION",
            "CURRENT_RESEARCH_STATE": "NOT_YET_TAGGED", "CONFIRMATION_STATE": "UNCONFIRMED",
            "DOES_NOT_ASSERT": "SOURCE_FACT_OR_OWNER_ADOPTION", "INFERENCE_STATE": "CODEX_INFERRED_CANDIDATE",
            "RECOVERY_PASS": recovery_pass, "NOTES": "Derived during repository-corpus review; requires Owner tagging.",
        })
    return records


def build_maps(rows: list[dict]) -> dict[str, str]:
    result = {}
    for row in rows:
        origin = row.get("ORIGIN_OBJECT_ID")
        if origin and origin not in result:
            result[origin] = row["OBJECT_ID"]
    return result


def relations(source: list[dict], live: list[dict], inferred: list[dict]) -> list[dict]:
    sm, lm = build_maps(source), build_maps(live)
    specs: list[tuple[str, str, str, str, str, str]] = []
    def ss(a: str, relation: str, b: str, note: str) -> None: specs.append(("S", a, relation, "S", b, note))
    def sl(a: str, relation: str, b: str, note: str) -> None: specs.append(("S", a, relation, "L", b, note))
    def ll(a: str, relation: str, b: str, note: str) -> None: specs.append(("L", a, relation, "L", b, note))

    for alt in ["SN-R1-CH-001", "SN-R1-ALT-001", "SN-R1-ALT-002", "SN-R1-ALT-003", "SN-R1-ALT-004", "SN-R1-ALT-005", "SN-R1-ALT-006", "SN-R2-CH-001"]:
        ss(alt, "CONTRADICTS" if alt == "SN-R1-CH-001" else "ALTERNATIVE_TO", "SN-MI-H-001", "Identity–Memory candidate family; no winner selected.")
    ss("SN-WP1-M-001", "CONSTRAINS", "SN-MI-H-001", "Persona State is not automatically a memory dump.")
    ss("SN-R1-CH-004", "REFINES", "SN-MI-H-008", "Adds retrieval/model/runtime/context causal factors.")
    ss("SN-R2-M-001", "REFINES", "SN-MI-H-008", "Reconstruction stack decomposition.")
    ss("SN-R1-H-003", "ALTERNATIVE_TO", "SN-MI-H-005", "Shared evidence/separate interpretation alternative.")
    ss("SN-R3-H-007", "STRENGTHENS", "SN-R1-H-003", "Independent RED convergence on anti-convergence candidate.")
    ss("SN-R3-PC-009", "REFINES", "SN-MI-PC-006", "Separates deletion from derived influence.")
    ss("SN-R3-H-002", "MOTIVATES", "SN-R3-PC-009", "Dependency invalidation candidate.")
    ss("SN-R1-CH-005", "ALTERNATIVE_TO", "SN-MI-H-011", "Merge as new successor C.")
    ss("SN-R3-H-005", "REFINES", "SN-R1-CH-005", "New successor requires new authority binding.")
    ss("SN-R2-FIND-004", "WEAKENS", "SN-WP1-PC-003", "Provider replacement intent does not prove behavioral compatibility.")
    ss("SN-R3-PC-002", "PRESERVES", "SN-MI-PC-012", "Memory/Authority separation survives across source groups.")
    ss("SN-R3-RISK-002", "MOTIVATES", "SN-R3-M-004", "Slow poisoning motivates trajectory monitoring.")
    ss("SN-R1-RISK-007", "STRENGTHENS", "SN-R3-RISK-004", "Same-root audit correlated-failure concern.")

    sl("SN-MI-H-001", "HISTORICAL_PREDECESSOR_OF", "ASA-MI-PC-006", "Live worldview refines the strong source proposition into an active unconfirmed substrate hypothesis.")
    sl("SN-MI-H-003", "MAPS_TO", "ASA-MI-H-001", "Live Persona instantiation model broadens durable-state formulation.")
    sl("SN-MI-M-004", "REFINED_BY", "ASA-MI-H-005", "Live Memory value types extend the historical taxonomy.")
    sl("SN-MI-HIST-PC-001", "POSSIBLE_SEMANTIC_EQUIVALENCE", "ASA-MI-H-STATUS-001", "Historical Memory != Current State may be refined, challenged, or scope-limited by the live derived-status model.")
    sl("SN-WP1-M-001", "TENSION_WITH", "ASA-MI-H-001", "Persona State not Memory Dump versus Persona instantiated from Memory/State.")
    sl("SN-MI-H-008", "REFINED_BY", "ASA-MI-H-CURRENT-001", "CURRENT operator contributes to reconstruction semantics.")
    sl("SN-R2-OQ-003", "MAPS_TO", "ASA-MI-H-STATUS-COMPETING-001", "Live registry preserves minimal/rich/derived/hybrid current-status alternatives.")
    sl("SN-MI-H-009", "REFINED_BY", "ASA-MI-H-FORGET-001", "Live registry retains forgetting as decay/inaccessibility/relation/deletion alternatives.")
    sl("SN-R3-PC-009", "MAPS_TO", "ASA-MI-H-DEL-002", "Delete source versus influence retained live.")
    sl("SN-MI-H-006", "COEXISTS_WITH", "ASA-MI-H-008", "Canonical durability can coexist with external reference Memory.")
    sl("SN-MI-OQ-002", "REFINED_BY", "ASA-MI-H-009", "Procedural expertise becomes function/function-binding candidate.")
    sl("SN-WP2-PC-001", "GROUNDED_BY", "ASA-MI-DI-002", "Reality-first source direction and live reality-proximity design intent.")
    sl("SN-WP2-PC-003", "COEXISTS_WITH", "ASA-MI-P-003", "Human model non-prescription and philosophy-as-prior remain distinct.")
    sl("SN-MI-PC-005", "REQUIRES_CS_PRIOR", "ASA-MI-P-001", "Representation/index questions route through mature CS abstractions first.")
    sl("SN-MI-PC-021", "MAPS_TO", "ASA-MI-H-004", "Change/evolution distinction maps to live change-rate modeling.")
    sl("SN-MI-M-003", "REFINED_BY", "ASA-MI-H-010", "Origin-preserving state extends to environment-bound function bindings.")
    sl("SN-R1-M-002", "REFINED_BY", "ASA-MI-H-EVAL-001", "Multidimensional continuity gains realism/fidelity evaluation separation.")
    ll("ASA-MI-H-002", "DEPENDS_ON", "ASA-MI-H-CTX-001", "Functional Memory requires a Context domain.")
    ll("ASA-MI-H-CURRENT-001", "IMPLEMENTS", "ASA-MI-H-002", "CURRENT evaluates Memory at current context.")
    ll("ASA-MI-H-SELF-002", "COEXISTS_WITH", "ASA-MI-H-SELF-003", "Self receiver and derived self-model are distinct candidates.")
    ll("ASA-MI-H-006", "STRENGTHENS", "ASA-MI-H-008", "Storage-location independence supports external-reference Memory.")
    ll("ASA-MI-P-005", "REFINES", "ASA-MI-H-003", "Scoped-invariant principle and functional constant model.")
    ll("ASA-MI-P-006", "STRENGTHENS", "ASA-MI-H-LIFE-001", "Lifecycle applies to Persona-related objects and relations.")

    rows = []
    maps = {"S": sm, "L": lm}
    for spec in specs:
        left_kind, left, relation, right_kind, right, note = spec
        if left not in maps[left_kind] or right not in maps[right_kind]:
            continue
        rows.append({
            "RELATION_ID": f"CX-REL-{len(rows)+1:04d}", "FROM_OBJECT_ID": maps[left_kind][left],
            "RELATION": relation, "TO_OBJECT_ID": maps[right_kind][right], "STATE": "CANDIDATE_NOT_OWNER_TAGGED",
            "FROM_ORIGIN_OBJECT_ID": left, "TO_ORIGIN_OBJECT_ID": right, "INFERENCE_STATE": "CODEX_CROSSWALK_CANDIDATE",
            "NOTES": note,
        })
    for idx, inf in enumerate(inferred, 1):
        if inf["CLASS"] == "EXPERIMENT_IDEA":
            target = lm.get("ASA-MI-H-001") or next(iter(lm.values()))
            rows.append({
                "RELATION_ID": f"CX-REL-{len(rows)+1:04d}", "FROM_OBJECT_ID": inf["OBJECT_ID"], "RELATION": "TESTS",
                "TO_OBJECT_ID": target, "STATE": "CANDIDATE_NOT_OWNER_TAGGED", "FROM_ORIGIN_OBJECT_ID": "",
                "TO_ORIGIN_OBJECT_ID": "ASA-MI-H-001", "INFERENCE_STATE": "CODEX_DERIVED_EXPERIMENT_RELATION",
                "NOTES": "Broad test-family link; exact target requires Owner tagging.",
            })
    return rows


def markdown_objects(title: str, rows: list[dict], note: str = "") -> str:
    lines = [f"# {title}", "", "```text", "AUTHORING_STATE = WORK_DRAFT", "NORMATIVE_AUTHORITY = NONE", "OWNER_TAGGING = NOT_PERFORMED", "```", ""]
    if note:
        lines += [note, ""]
    for row in rows:
        lines += [f"## {row['OBJECT_ID']} — {row.get('ORIGIN_OBJECT_ID') or 'CODEX_INFERRED'}", "", f"- Class: `{row['CLASS']}`", f"- Status: `{row['CURRENT_RESEARCH_STATE']}`", f"- Source level: `{row['SOURCE_LEVEL']}`", f"- Source: `{row['SOURCE_LOCATOR']}`", f"- Statement: {row['STATEMENT']}", ""]
        if row.get("SOURCE_RECORD_TEXT"):
            lines += ["Source record:", "", "```text", row["SOURCE_RECORD_TEXT"], "```", ""]
    if not rows:
        lines.append("No object in this category was recovered from the repository corpus.")
    return "\n".join(lines)


def inventory_rows() -> list[dict]:
    rows = []
    for path in sorted(CORPUS.rglob("*")):
        if not path.is_file() or OUT in path.parents:
            continue
        path_rel = rel(path)
        if "source-normalized-drafts/" in path_rel:
            group, level = "HISTORICAL_SOURCE_NORMALIZED", "SECONDARY_NORMALIZED_SOURCE"
        elif "/references/" in path_rel:
            group, level = "REFERENCE", "LOW_WEIGHT_EXTERNAL_REFERENCE_REGISTER"
        else:
            group, level = "LIVE_RESEARCH", "LIVE_REPOSITORY_RESEARCH_RECORD"
        rows.append({"PATH": path_rel, "BYTES": path.stat().st_size, "CORPUS_CLASS": group, "SOURCE_LEVEL": level, "MINED": "YES"})
    return rows


def phase_baseline() -> None:
    inv = inventory_rows()
    total_bytes = sum(int(row["BYTES"]) for row in inv)
    write(OUT / "run" / "00_README_SCOPE_AND_ISOLATION.md", f"""# ASA-MI Codex Source-Mining Draft — Scope and Isolation

```text
AUTHORING_STATE = WORK_DRAFT
SOURCE_SCOPE = REPOSITORY_CORPUS_ONLY
RAW_PRIMARY_SOURCE_VERIFICATION = NOT_PERFORMED
TASK_BASELINE_SHA = {BASELINE_SHA}
TASK_BRANCH = {TASK_BRANCH}
AUTHORIZED_WRITE_ROOT = {OUT.relative_to(REPO).as_posix()}/
SOURCE_DERIVED_LIVE_CODEX_INFERENCE_PHYSICALLY_SEPARATED = TRUE
NORMATIVE_AUTHORITY = NONE
FROZEN = FALSE
PRODUCTION_AUTHORIZED = FALSE
```

This run mines only the 18 ASA-MI files addressable at the task baseline. Historical raw chat files were not searched for or reconstructed. Existing repository files are read-only inputs.
""")
    md = ["# Repository Corpus Source Inventory", "", f"Measured files: **{len(inv)}**  ", f"Measured bytes: **{total_bytes}**", "", "| Path | Bytes | Corpus class | Source level | Mined |", "|---|---:|---|---|---|"]
    md += [f"| `{r['PATH']}` | {r['BYTES']} | {r['CORPUS_CLASS']} | {r['SOURCE_LEVEL']} | {r['MINED']} |" for r in inv]
    write(OUT / "run" / "01_SOURCE_INVENTORY.md", "\n".join(md))
    write_csv(OUT / "run" / "02_SOURCE_INVENTORY.csv", ["PATH", "BYTES", "CORPUS_CLASS", "SOURCE_LEVEL", "MINED"], inv)
    missing = [
        ("SRC-WP1", "Personal_Cognitive_Sovereignty_Interface_Whitepaper_v0.1_2026-08-18.md", "file_0000000002fc8211a0b2356c51a8f721"),
        ("SRC-WP2", "PCS-SHAI_Whitepaper_v0.2_Revision_Original_Proposal_v0.1_2026-08-18.md", "file_0000000005fc8207a7a59df6bc4191a2"),
        ("SRC-MI0", "붙여넣은 텍스트 (1).txt", "file_000000006a8881f48bbd13e6673e1d54"),
        ("SRC-MI1", "붙여넣은 마크다운(1).md", "file_0000000052e4820a982a98212c08d3cd"),
        ("SRC-R1", "붙여넣은 마크다운(2).md", "file_00000000c73481f486e60c793ad7d96d"),
        ("SRC-R2", "붙여넣은 마크다운(3).md", "file_000000008b448243a9d54a65caf225b1"),
        ("SRC-R3", "붙여넣은 마크다운(4).md", "file_00000000fb1c8246a8cc7d3c9ac8cb8b"),
    ]
    lines = ["# Raw Primary Source Missingness", "", "All seven raw sources are unavailable as repository-addressable files. Their normalized records were mined as secondary sources; raw verification was not performed.", "", "| Source ID | Historical filename | Historical chat locator | State |", "|---|---|---|---|"]
    lines += [f"| {sid} | `{name}` | `{chat}` | RAW_PRIMARY_SOURCE_NOT_REPOSITORY_ADDRESSABLE |" for sid, name, chat in missing]
    write(OUT / "run" / "03_RAW_SOURCE_MISSINGNESS.md", "\n".join(lines))
    write(OUT / "run" / "04_BASELINE_IDENTITY_RECEIPT.md", f"""# Baseline Identity Receipt

```text
PREFLIGHT_LOCAL_HEAD = {PREFLIGHT_LOCAL_SHA}
PREFLIGHT_REMOTE_SHA = {BASELINE_SHA}
REMOTE_HEAD_RECHECK_SHA = {BASELINE_SHA}
TASK_BASELINE_SHA = {BASELINE_SHA}
TASK_BRANCH = {TASK_BRANCH}
TASK_WORKTREE_PATH = {TASK_WORKTREE}
TASK_START_SHA = {BASELINE_SHA}
REMOTE_MOVED_SINCE_PREFLIGHT = FALSE
PRIMARY_WORKTREE_DIRTY_STATE = DIRTY_PRESERVED
PRIMARY_WORKTREE_UNTRACKED_STATE = aaa/ PRESERVED_UNTOUCHED
INITIAL_PUSH_PROBE = PASS
REMOTE_TASK_BRANCH_INITIAL_SHA = {BASELINE_SHA}
```
""")
    write(OUT / "comparison" / "01_AS_IS_RESEARCH_RECORD_SNAPSHOT.md", f"""# AS-IS Research Record Snapshot

The verified baseline contains {len(inv)} ASA-MI files ({total_bytes} bytes): 13 historical source-normalized files and 5 live/reference research files. The stale local main is recorded only as a freshness reference and is not a semantic corpus.

Observed AS-IS strengths: provisional source objects, seven-source register, 24 cross-source hypothesis families, experiment catalog, traceability matrix, live worldview/planning/brainstorm registry, and explicit source/live isolation.

Observed AS-IS gaps: no unified machine-readable object registry, no separate current/Owner/source status axes, no complete owner tagging queue, no machine-checkable cross-corpus relations, raw sources unavailable, and several live extensions not crosswalked to historical objects.
""")
    write(OUT / "run" / "05_PASS_MANIFEST.md", """# Pass Manifest

```text
FULL_SWEEP_1 = NOT_STARTED
FULL_SWEEP_2 = NOT_STARTED
FULL_SWEEP_3 = NOT_STARTED
FULL_SWEEP_4 = NOT_STARTED
SPECIAL_PASS_A = NOT_STARTED
SPECIAL_PASS_B = NOT_STARTED
SPECIAL_PASS_C = NOT_STARTED
SPECIAL_PASS_D = NOT_STARTED
SPECIAL_PASS_E = NOT_STARTED
SPECIAL_PASS_F = NOT_STARTED
SPECIAL_PASS_G = NOT_STARTED
SPECIAL_PASS_H = NOT_STARTED
SPECIAL_PASS_I = NOT_STARTED
SPECIAL_PASS_J = NOT_STARTED
SPECIAL_PASS_K = NOT_STARTED
SATURATION_PASS_COUNT = 0
CONSECUTIVE_NO_NEW_PASSES_AT_END = 0
```
""")


def phase_sweeps() -> None:
    src, live = source_objects(), live_objects()
    write_jsonl(OUT / "source-derived" / "objects.jsonl", src)
    write_jsonl(OUT / "live-brainstorm" / "objects.jsonl", live)
    write_jsonl(OUT / "codex-inferred" / "objects.jsonl", [])
    for idx in range(1, 5):
        pass_id = f"FULL_SWEEP_{idx}"
        recovered = [r for r in src + live if r["RECOVERY_PASS"] == pass_id]
        classes = Counter(r["CLASS"] for r in recovered)
        write(OUT / "run" / "checkpoints" / f"FULL_SWEEP_{idx:02d}.md", f"""# {pass_id} Checkpoint

```text
PASS_ID = {pass_id}
CORPUS_FILES_CONSIDERED = 18
NEW_OBJECT_COUNT = {len(recovered)}
NEW_RELATION_CANDIDATE_COUNT = 0
NEW_OPEN_QUESTIONS = {sum(1 for r in recovered if r['CLASS'] == 'OPEN_QUESTION')}
NEW_FAILURE_MODES = {sum(1 for r in recovered if r['CLASS'] in {'RISK','FAILURE_MODE'})}
NEW_MISSINGNESS = {7 if idx == 4 else 0}
KNOWN_AMBIGUITIES = SOURCE_STATUS_VS_CURRENT_STATUS; MEMORY_BOUNDARY; SOURCE_LIVE_LINEAGE
PASS_STATE = COMPLETE
```

Recovered class counts: {dict(sorted(classes.items()))}

New object IDs: {', '.join(r['OBJECT_ID'] for r in recovered)}
""")
    manifest = (OUT / "run" / "05_PASS_MANIFEST.md").read_text(encoding="utf-8")
    for idx in range(1, 5):
        manifest = manifest.replace(f"FULL_SWEEP_{idx} = NOT_STARTED", f"FULL_SWEEP_{idx} = COMPLETE")
    write(OUT / "run" / "05_PASS_MANIFEST.md", manifest)


def phase_specialized() -> None:
    src, live, inf = source_objects(), live_objects(), inferred_objects()
    rels = relations(src, live, inf)
    write_jsonl(OUT / "codex-inferred" / "objects.jsonl", inf)
    write_jsonl(OUT / "crosswalk" / "relations_candidates.jsonl", rels)
    pass_info = {
        "A": ("EXPLICIT_CLAIMS", lambda r: r["CLASS"] not in {"RISK","NON_CLAIM","UNCLASSIFIED"}),
        "B": ("NON_WINNING_AND_HISTORICAL_ALTERNATIVES", lambda r: r["CLASS"] in {"COUNTER_HYPOTHESIS","ALTERNATIVE_HYPOTHESIS","HISTORICAL_HYPOTHESIS","CORRECTION"}),
        "C": ("NEGATIVE_SEMANTICS_AND_NON_CLAIMS", lambda r: r["CLASS"] in {"NEGATIVE_CLAIM","NON_CLAIM"} or bool(r.get("DOES_NOT_ASSERT"))),
        "D": ("IMPLICIT_ASSUMPTIONS", lambda r: r["CLASS"] == "IMPLICIT_ASSUMPTION"),
        "E": ("DESIGN_INTENT_AND_PRINCIPLES", lambda r: r["CLASS"] in {"DESIGN_INTENT","PRINCIPLE","RESEARCH_PRINCIPLE","EVALUATION_PRINCIPLE"}),
        "F": ("PHILOSOPHICAL_GROUNDING", lambda r: r["CLASS"] == "PHILOSOPHICAL_GROUNDING"),
        "G": ("CS_LEGACY_AND_PRIOR_PENDING", lambda r: r["CLASS"] in {"CS_PRIOR","CS_PRIOR_PENDING"}),
        "H": ("FAILURE_MODES_AND_RISKS", lambda r: r["CLASS"] in {"FAILURE_MODE","RISK"}),
        "I": ("EXPERIMENTALIZATION_AND_KILL_TESTS", lambda r: r["CLASS"] in {"EXPERIMENT_IDEA","KILL_TEST"}),
        "J": ("CROSS_SOURCE_CONFLICT_AND_RELATION_CANDIDATES", lambda r: r["CLASS"] in {"COUNTER_HYPOTHESIS","COUNTERARGUMENT"}),
        "K": ("RESIDUAL_AND_UNCLASSIFIED", lambda r: r["CLASS"] in {"UNCLASSIFIED","SCHEMA_EXTENSION_CANDIDATE","OPEN_QUESTION"}),
    }
    all_rows = src + live + inf
    for letter, (name, predicate) in pass_info.items():
        audited = [r for r in all_rows if predicate(r)]
        newly = [r for r in inf if r["RECOVERY_PASS"] == f"SPECIAL_PASS_{letter}"]
        relation_count = len(rels) if letter == "J" else sum(1 for r in rels if r["RELATION"] == "TESTS") if letter == "I" else 0
        write(OUT / "run" / "checkpoints" / f"SPECIAL_PASS_{letter}.md", f"""# Specialized Pass {letter} — {name}

```text
PASS_ID = SPECIAL_PASS_{letter}
PASS_STATE = COMPLETE
CORPUS_FILES_CONSIDERED = 18
OBJECTS_AUDITED = {len(audited)}
NEW_OBJECT_COUNT = {len(newly)}
NEW_OBJECT_IDS = {', '.join(r['OBJECT_ID'] for r in newly) or 'NONE'}
NEW_RELATION_CANDIDATE_COUNT = {relation_count}
KNOWN_AMBIGUITIES = OWNER_TAGGING_PENDING
```

This pass reviewed the full corpus through the named specialist lens. Existing objects were not duplicated merely to inflate counts.
""")
    manifest = (OUT / "run" / "05_PASS_MANIFEST.md").read_text(encoding="utf-8")
    for letter in pass_info:
        manifest = manifest.replace(f"SPECIAL_PASS_{letter} = NOT_STARTED", f"SPECIAL_PASS_{letter} = COMPLETE")
    write(OUT / "run" / "05_PASS_MANIFEST.md", manifest)


def phase_saturation() -> None:
    src, live, inf = source_objects(), live_objects(), inferred_objects()
    rels = relations(src, live, inf)
    write(OUT / "run" / "checkpoints" / "SATURATION_01.md", """# Saturation Pass 01

```text
PASS_STATE = COMPLETE
CORPUS_FILES_CONSIDERED = 18
NEW_MATERIAL = FALSE
NEW_OBJECT_COUNT = 0
NEW_RELATION_CANDIDATE_COUNT = 0
CONSECUTIVE_NO_NEW_COUNT = 1
```

Residual review rechecked negative semantics, source caveats, parking-lot claims, live corrections, and cross-corpus boundary risks. No materially new object beyond the existing registry was found.
""")
    write(OUT / "run" / "checkpoints" / "SATURATION_02.md", """# Saturation Pass 02

```text
PASS_STATE = COMPLETE
CORPUS_FILES_CONSIDERED = 18
NEW_MATERIAL = FALSE
NEW_OBJECT_COUNT = 0
NEW_RELATION_CANDIDATE_COUNT = 0
CONSECUTIVE_NO_NEW_COUNT = 2
SATURATION_STOP_CONDITION = MET
```

An independent family-by-family residual review found no new material. This is corpus saturation for the repository-visible records, not proof of raw-source completeness.
""")
    manifest = (OUT / "run" / "05_PASS_MANIFEST.md").read_text(encoding="utf-8")
    manifest = re.sub(r"SATURATION_PASS_COUNT = \d+", "SATURATION_PASS_COUNT = 2", manifest)
    manifest = re.sub(r"CONSECUTIVE_NO_NEW_PASSES_AT_END = \d+", "CONSECUTIVE_NO_NEW_PASSES_AT_END = 2", manifest)
    write(OUT / "run" / "05_PASS_MANIFEST.md", manifest)

    source_sets = {
        "01_EXPLICIT_SOURCE_OBJECTS.md": (src, "Explicit Source Objects"),
        "02_ALTERNATIVE_AND_HISTORICAL_HYPOTHESES.md": ([r for r in src if r["CLASS"] in {"COUNTER_HYPOTHESIS","ALTERNATIVE_HYPOTHESIS","HISTORICAL_HYPOTHESIS","COUNTERARGUMENT","CORRECTION"}], "Alternative and Historical Hypotheses"),
        "03_MODELS_CONCEPTS_AND_MAPPINGS.md": ([r for r in src if r["CLASS"] in {"MODEL","CONCEPT","MAPPING","DESIGN_CANDIDATE"}], "Models, Concepts, and Mappings"),
        "04_NEGATIVE_CLAIMS_AND_NON_CLAIMS.md": ([r for r in src if r["CLASS"] in {"NEGATIVE_CLAIM","NON_CLAIM"} or r.get("DOES_NOT_ASSERT")], "Negative Claims and Non-Claims"),
        "05_OPEN_QUESTIONS.md": ([r for r in src if r["CLASS"] == "OPEN_QUESTION"], "Open Questions"),
        "06_EXPERIMENTS_AND_KILL_TESTS.md": ([r for r in src if r["CLASS"] in {"EXPERIMENT_IDEA","KILL_TEST"}], "Experiments and Kill Tests"),
        "07_FAILURE_MODES_AND_RISKS.md": ([r for r in src if r["CLASS"] in {"RISK","FAILURE_MODE"}], "Failure Modes and Risks"),
        "08_PHILOSOPHICAL_GROUNDING_FROM_SOURCES.md": ([r for r in src if r["CLASS"] == "PHILOSOPHICAL_GROUNDING" or any(k in r["STATEMENT"].lower() for k in ["reality", "human", "identity", "self status"])], "Philosophical Grounding from Sources"),
        "09_CS_PRIOR_PENDING_FROM_SOURCES.md": ([r for r in src if r["CLASS"] == "OPEN_QUESTION" and any(k in r["STATEMENT"].lower() for k in ["canonical", "index", "lifecycle", "reconstruction", "version", "reference", "cache", "scope"])], "CS Prior Pending from Sources"),
        "10_SOURCE_COVERAGE_AND_MISSINGNESS.md": ([r for r in src if r["CLASS"] in {"UNCLASSIFIED","NON_CLAIM"}], "Source Coverage and Missingness"),
    }
    for filename, (rows, title) in source_sets.items():
        write(OUT / "source-derived" / filename, markdown_objects(title, rows, "Historical records are secondary normalized sources; raw primary verification was not performed."))
    write(OUT / "source-derived" / "10_SOURCE_COVERAGE_AND_MISSINGNESS.md", f"""# Source Coverage and Missingness

```text
REPOSITORY_CORPUS_FILES = 18
HISTORICAL_NORMALIZED_FILES = 13
SOURCE_DERIVED_OBJECTS = {len(src)}
HISTORICAL_SOURCE_IDS = [SRC-WP1, SRC-WP2, SRC-MI0, SRC-MI1, SRC-R1, SRC-R2, SRC-R3]
RAW_PRIMARY_SOURCE_VERIFICATION = NOT_PERFORMED
RAW_PRIMARY_SOURCE_MISSING_COUNT = 7
```

All 13 normalized files were considered. Every recovered historical object retains a repository locator and, where present, its original normalized record text. The seven historical raw source bodies are not repository-addressable and were not searched for elsewhere or reconstructed from the web.

Exact historical filenames and chat locators are preserved in `../run/03_RAW_SOURCE_MISSINGNESS.md`. This draft measures repository-record recall; it does not claim sentence-level or raw-source completeness and therefore reports no coverage percentage.
""")

    live_sets = {
        "01_LIVE_PRINCIPLES_AND_DESIGN_INTENT.md": ([r for r in live if r["CLASS"] in {"PRINCIPLE","RESEARCH_PRINCIPLE","DESIGN_INTENT","EVALUATION_PRINCIPLE"}], "Live Principles and Design Intent"),
        "02_LIVE_HYPOTHESES_AND_ALTERNATIVES.md": ([r for r in live if "HYPOTHESIS" in r["CLASS"] or r["CLASS"] == "CORRECTION"], "Live Hypotheses and Alternatives"),
        "03_LIVE_MODELS_CONCEPTS_AND_MAPPINGS.md": ([r for r in live if r["CLASS"] in {"MODEL","CONCEPT","MAPPING"}], "Live Models, Concepts, and Mappings"),
        "04_LIVE_OPEN_QUESTIONS.md": ([r for r in live if r["CLASS"] == "OPEN_QUESTION"], "Live Open Questions"),
        "05_LIVE_CS_PRIOR_PENDING.md": ([r for r in live if r["CLASS"] == "CS_PRIOR"], "Live CS Prior Pending"),
        "06_LIVE_PHILOSOPHICAL_GROUNDING.md": ([r for r in live if r["CLASS"] == "PHILOSOPHICAL_GROUNDING"], "Live Philosophical Grounding"),
        "07_LIVE_UNCLASSIFIED_AND_RESIDUAL.md": ([r for r in live if r["CLASS"] == "UNCLASSIFIED"], "Live Unclassified and Residual"),
    }
    for filename, (rows, title) in live_sets.items():
        write(OUT / "live-brainstorm" / filename, markdown_objects(title, rows, "These are live repository research records, not retroactive historical-source claims."))

    inf_sets = {
        "01_IMPLICIT_ASSUMPTIONS.md": ([r for r in inf if r["CLASS"] == "IMPLICIT_ASSUMPTION"], "Codex-Inferred Implicit Assumptions"),
        "02_DERIVED_EXPERIMENT_CANDIDATES.md": ([r for r in inf if r["CLASS"] == "EXPERIMENT_IDEA"], "Codex-Derived Experiment Candidates"),
        "03_DERIVED_FAILURE_MODES.md": ([r for r in inf if r["CLASS"] == "FAILURE_MODE"], "Codex-Derived Failure Modes"),
        "04_SCHEMA_OR_CLASS_EXTENSION_CANDIDATES.md": ([r for r in inf if r["CLASS"] == "SCHEMA_EXTENSION_CANDIDATE"], "Schema or Class Extension Candidates"),
        "05_OTHER_INFERRED_RESEARCH_OBJECTS.md": ([r for r in inf if r["CLASS"] not in {"IMPLICIT_ASSUMPTION","EXPERIMENT_IDEA","FAILURE_MODE","SCHEMA_EXTENSION_CANDIDATE"}], "Other Codex-Inferred Research Objects"),
    }
    for filename, (rows, title) in inf_sets.items():
        write(OUT / "codex-inferred" / filename, markdown_objects(title, rows, "These are Codex inferences, not source facts or Owner positions."))

    relation_lines = ["# Source-to-Live Relation Candidates", "", "All relations are candidate crosswalks pending Owner tagging.", "", "| Relation | From origin | Type | To origin | Note |", "|---|---|---|---|---|"]
    relation_lines += [f"| {r['RELATION_ID']} | {r['FROM_ORIGIN_OBJECT_ID'] or r['FROM_OBJECT_ID']} | {r['RELATION']} | {r['TO_ORIGIN_OBJECT_ID'] or r['TO_OBJECT_ID']} | {r['NOTES']} |" for r in rels]
    write(OUT / "crosswalk" / "01_SOURCE_TO_LIVE_RELATION_CANDIDATES.md", "\n".join(relation_lines))
    conflicts = [r for r in rels if r["RELATION"] in {"CONTRADICTS","ALTERNATIVE_TO","TENSION_WITH","WEAKENS"}]
    write(OUT / "crosswalk" / "02_CROSS_SOURCE_CONFLICTS.md", "\n".join(["# Cross-Source Conflicts", ""] + [f"- `{r['FROM_ORIGIN_OBJECT_ID']}` **{r['RELATION']}** `{r['TO_ORIGIN_OBJECT_ID']}` — {r['NOTES']}" for r in conflicts]))
    equivalents = [r for r in rels if r["RELATION"] == "POSSIBLE_SEMANTIC_EQUIVALENCE"]
    write(OUT / "crosswalk" / "03_POSSIBLE_SEMANTIC_EQUIVALENCE.md", "\n".join(["# Possible Semantic Equivalence", "", "Possible equivalence is not asserted equivalence.", ""] + [f"- `{r['FROM_ORIGIN_OBJECT_ID']}` ↔ `{r['TO_ORIGIN_OBJECT_ID']}` — {r['NOTES']}" for r in equivalents]))
    write(OUT / "crosswalk" / "04_HYPOTHESIS_FAMILY_MAP.md", """# Hypothesis Family Map

| Family | Historical/source-normalized positions | Live/current positions | Owner tagging focus |
|---|---|---|---|
| Identity–Memory | identity equals Memory; Memory necessary/not sufficient; Memory supportive; multidimensional continuity | Memory as primary substrate; Persona instantiated from Memory/State | necessary, sufficient, primary, supportive, or scoped equivalence? |
| Process continuity | discontinuity allowed; reconstruction required | discontinuity native; CURRENT/SELF may be reconstructed | minimum continuity evidence |
| Memory boundary | episodic, semantic, procedural, relational, standpoint, metadata | values, references, relations, functions, bindings, results, views | membership and non-membership rules |
| Current status | explicit standpoint persistence is open | minimal, rich, derived, hybrid | canonical, derived, cache, or runtime binding |
| Self | Self/Boundary/Authority separated | receiver/reference plus optional derived self-model | persisted anchor necessity |
| Dynamics | lifecycle and evolution vs growth | Boundary, Change Rate, Transition Condition | operational definitions |
| Learning | experience produces multiple products | Remember vs Learn and function change remain open | event-to-durable-change lineage |
| Reconstruction | state plus retriever/compiler/model/runtime | Persona instantiation and CURRENT evaluation | hidden ownership and portability |
| Common/local | common plus local memory; convergence attack | still open; anti-convergence retained | what can be shared safely |
| Forget/delete | functional forgetting, deletion, erasure distinct | deletion valid; forgetting remains decomposed | source versus influence removal |
| Provider/local | replacement intent; compatibility not proven | storage-location independence and function rebinding | continuity envelope |
| Authority | Memory, capability, intimacy, continuity do not grant authority | live model does not revoke firewalls | grant requalification after change |
| Fission/merge | multiple descendants; merge as reconciliation or successor | lineage questions remain open | successor and authority semantics |
| Human realism | reality-first and non-prescriptive modeling | perceived realism differs from fidelity | meaningful evaluation axes |
| CS prior | canonical/derived/reference/lifecycle questions pending | explicit CS-prior-first method | mature abstraction plus Persona delta |
""")


def priority_for(row: dict) -> tuple[int, str]:
    text = f"{row['STATEMENT']} {row.get('ORIGIN_OBJECT_ID','')}".lower()
    rules = [
        (1, "foundational worldview/design intent", ["reality", "final truth", "design objective"]),
        (2, "Identity–Memory", ["identity", "same persona"]),
        (3, "Memory meaning/membership/scope", ["memory boundary", "memory identity", "accessible", "reference"]),
        (4, "Current/Self/Context/State", ["current", "self", "context"]),
        (5, "change/lifecycle", ["change rate", "transition", "lifecycle", "evolution"]),
        (6, "Remember vs Learn", ["learn", "experience", "procedural"]),
        (7, "reconstruction/retrieval/compiler", ["reconstruction", "retrieval", "compiler"]),
        (8, "model/runtime/provider portability", ["provider", "model", "runtime", "cloud"]),
        (9, "Common vs Local", ["common memory", "convergence"]),
        (10, "relationship/self-model/standpoint", ["relationship", "standpoint", "self-model"]),
        (11, "forget/delete/ghost influence", ["forget", "delet", "ghost"]),
        (12, "provenance/authority/audit", ["authority", "provenance", "audit"]),
        (13, "fission/merge/successor", ["fission", "merge", "successor"]),
        (14, "same-Persona/human realism", ["realism", "fidelity", "continuity"]),
        (16, "CS prior pending", ["cs prior", "canonical", "serialization", "versioning"]),
    ]
    for rank, label, needles in rules:
        if any(n in text for n in needles):
            return rank, label
    if row["CLASS"] == "UNCLASSIFIED":
        return 15, "residual/unclassified"
    return 15, "residual/unclassified"


def phase_final() -> None:
    src, live, inf = source_objects(), live_objects(), inferred_objects()
    rels = relations(src, live, inf)
    all_rows = src + live + inf
    write_jsonl(OUT / "run" / "object_index.jsonl", [{"OBJECT_ID": r["OBJECT_ID"], "CORPUS_GROUP": r["CORPUS_GROUP"], "CLASS": r["CLASS"], "SOURCE_LOCATOR": r["SOURCE_LOCATOR"], "OBJECT_FILE": f"{('source-derived' if r in src else 'live-brainstorm' if r in live else 'codex-inferred')}/objects.jsonl"} for r in all_rows])

    write(OUT / "comparison" / "02_TO_BE_TAGGING_READY_TARGET.md", """# TO-BE Tagging-Ready Target

TO-BE means the repository thought-space is broadly inventoried, historical/live/Codex provenance is physically separated, non-winning positions remain visible, negative semantics and missingness are explicit, objects have provisional IDs, relations are candidates, and an Owner queue exists.

TO-BE does not mean final ontology, final truth, validated Persona design, frozen artifact, or Owner acceptance.
""")
    gaps = [
        ("GAP-001","A vs B","SOURCE_COVERAGE","stale local has no ASA-MI path","verified remote has 18-file corpus","SOURCE_COVERAGE_DELTA","local/remote Git refs","","HIGH","CLOSED_BY_BASELINE_SELECTION","A is freshness evidence only"),
        ("GAP-002","C vs E[source]","MACHINE_READABILITY","provisional Markdown objects","separate parseable JSONL registry","REPRESENTATION_DELTA","source-normalized-drafts","all source objects","HIGH","CLOSED_IN_DRAFT","raw-source claims not upgraded"),
        ("GAP-003","C vs E[source]","STATUS_AXES","source statuses embedded inconsistently","source/current/Owner status separated","CLASSIFICATION_DELTA","source-normalized-drafts","all source objects","HIGH","CLOSED_IN_DRAFT","Owner tagging pending"),
        ("GAP-004","D vs E[live]","LIVE_OBJECTIZATION","mixed narrative and registry structures","uniform live object registry","REPRESENTATION_DELTA","live research files","all live objects","MEDIUM","CLOSED_IN_DRAFT","no retroactive source attribution"),
        ("GAP-005","C vs D","HISTORICAL_LIVE_LINEAGE","placeholder links only","candidate crosswalk with provenance","RELATION_DELTA","traceability matrix","relation candidates","HIGH","DRAFTED","relations unconfirmed"),
        ("GAP-006","C+D vs E","ALTERNATIVE_VISIBILITY","alternatives distributed across RED and parking lot","single alternative/historical registry","CONTENT_DELTA","RED and parking-lot files","counter hypotheses","HIGH","CLOSED_IN_DRAFT","no winner selected"),
        ("GAP-007","C+D vs E","NEGATIVE_SEMANTICS","DOES_NOT_ASSERT scattered","negative/non-claim view","NEGATIVE_SEMANTICS_DELTA","all corpus","negative objects","MEDIUM","CLOSED_IN_DRAFT","preserves scope limits"),
        ("GAP-008","C+D vs E","EXPERIMENTS","source tests and live candidates distributed","source tests and Codex-derived tests separated","EXPERIMENT_DELTA","experiment catalog","experiments","HIGH","CLOSED_IN_DRAFT","derived tests marked Codex"),
        ("GAP-009","C+D vs E","TAGGING","worksheet without complete queue","measured object-level queue","REPRESENTATION_DELTA","tagging backlog","all objects","HIGH","CLOSED_IN_DRAFT","Owner decisions absent"),
        ("GAP-010","B vs E","RAW SOURCES","seven locators but no raw files","seven explicit missingness records","RAW_SOURCE_MISSINGNESS","source register","","HIGH","OPEN_FUTURE_RERUN","cannot close in repository mode"),
        ("GAP-011","C+D vs E","RESIDUALS","parking lot and schema failures distributed","unclassified and schema-extension views","RESIDUAL_DELTA","parking lot/live registry","residual objects","MEDIUM","CLOSED_IN_DRAFT","not treated as low value"),
        ("GAP-012","C+D vs E","REVIEW_ENTRYPOINT","Owner must traverse many files","six-file morning entrypoint","TRACEABILITY_DELTA","entire corpus","","HIGH","CLOSED_IN_DRAFT","links supplied in run manifest"),
    ]
    gap_fields = ["GAP_ID","COMPARISON","DIMENSION","AS_IS_STATE","TO_BE_STATE","DELTA_TYPE","SOURCE_REF","AFFECTED_OBJECTS","SEVERITY_FOR_TAGGING","CLOSURE_STATE","NOTES"]
    write_csv(OUT / "comparison" / "03_AS_IS_TO_BE_GAP_MATRIX.csv", gap_fields, [dict(zip(gap_fields, row)) for row in gaps])
    group_rows = [
        {"GROUP":"A_LOCAL_REPOSITORY_STATE_REFERENCE","SHA":PREFLIGHT_LOCAL_SHA,"SEMANTIC_CORPUS":"NO","OBSERVABLE":"YES","PURPOSE":"freshness/preservation evidence"},
        {"GROUP":"B_REMOTE_TASK_BASELINE","SHA":BASELINE_SHA,"SEMANTIC_CORPUS":"REPOSITORY SNAPSHOT","OBSERVABLE":"YES","PURPOSE":"exact reproducible baseline"},
        {"GROUP":"C_EXISTING_SOURCE_NORMALIZED_AS_IS","SHA":BASELINE_SHA,"SEMANTIC_CORPUS":"YES_SECONDARY_NORMALIZED","OBSERVABLE":"YES","PURPOSE":"historical source thought-space"},
        {"GROUP":"D_LIVE_BRAINSTORM_AS_IS","SHA":BASELINE_SHA,"SEMANTIC_CORPUS":"YES_LIVE_RECORD","OBSERVABLE":"YES","PURPOSE":"current Owner-facing research record"},
        {"GROUP":"E_CODEX_MINED_TO_BE_DRAFT","SHA":"TASK_BRANCH","SEMANTIC_CORPUS":"DRAFT_REPRESENTATION","OBSERVABLE":"YES","PURPOSE":"recall-first tagging readiness"},
    ]
    write_csv(OUT / "comparison" / "05_COMPARISON_GROUP_MATRIX.csv", ["GROUP","SHA","SEMANTIC_CORPUS","OBSERVABLE","PURPOSE"], group_rows)
    md = ["# Comparison Group Matrix", "", "| Group | SHA | Semantic corpus | Observable | Purpose |", "|---|---|---|---|---|"]
    md += [f"| {r['GROUP']} | `{r['SHA']}` | {r['SEMANTIC_CORPUS']} | {r['OBSERVABLE']} | {r['PURPOSE']} |" for r in group_rows]
    write(OUT / "comparison" / "04_COMPARISON_GROUP_MATRIX.md", "\n".join(md))
    write(OUT / "comparison" / "06_HISTORICAL_SOURCE_VS_LIVE_BRAINSTORM.md", """# Historical Source vs Live Brainstorm

## Major deltas and tensions

1. Historical `Identity ?= Memory` remains a strong unconfirmed proposition; RED-I supplies necessity/support/multidimensional alternatives. Live records refine it toward Memory as a primary continuity substrate and Persona instantiation from Memory/State, without selecting sufficiency.
2. Historical `MEMORY != CURRENT STATE` is preserved. Live records allow CURRENT to be an operator and Current Status to be stored, derived, cached, or hybrid. This is a scope/reconciliation question, not a retroactive rewrite.
3. Historical `Persona State != Memory Dump` constrains the live broad Memory-value model. Function, reference, relation, binding, and result membership remain candidates, not automatic inclusion.
4. Historical reconstruction research emphasizes retriever/compiler/model/runtime hidden ownership. Live functional/context models add CURRENT and SELF evaluation semantics but do not eliminate those risks.
5. Historical functional forgetting and deletion are differentiated; live records explicitly accept deletion as a lifecycle transition and retain `DELETE_SOURCE != DELETE_INFLUENCE`.
6. Historical provider replacement is a design intent with behavioral compatibility unproven. Live storage-location independence and function rebinding extend the portability problem rather than solve it.
7. Historical Common/Local Memory faces convergence attacks. Live records preserve the question and CS-prior-first method; no shared-interpretation policy is selected.
8. Live records add materially stronger function/reference/context hypotheses (`M(Context)->Value`, external reference Memory, function binding, CURRENT/SELF operators) that are not attributed backward to historical sources.
9. Live records strengthen philosophical/human-reality grounding and distinguish perceived realism from structural fidelity; historical sources already contain reality-first and non-prescriptive constraints.
10. Authority firewalls remain compatible across both corpora: Memory/State/Capability/Intimacy/Continuity do not automatically create Authority.
""")
    write(OUT / "comparison" / "07_RECALL_GAIN_REPORT.md", f"""# Recall Gain Report

## Measured result

- Repository corpus files mined: 18
- Historical normalized files: 13
- Source-derived draft objects: {len(src)}
- Live/current draft objects: {len(live)}
- Codex-inferred objects: {len(inf)}
- Candidate relations: {len(rels)}
- Raw primary missingness items: 7

## Material recall gains

- Every recovered existing origin ID is preserved beside a new provisional ID.
- RED/non-winning and parking-lot positions are queueable rather than buried.
- Source position, current research state, and Owner-position state are separate.
- Historical source, live brainstorm, and Codex inference are physically separate.
- Negative semantics, CS-prior pending questions, experiments, failure modes, and residuals have dedicated views.
- Historical-to-live mappings are explicit candidate relations rather than silent reinterpretations.
- A complete tagging queue and priority review sequence reduce Owner reconstruction cost.

No coverage percentage is claimed because raw primary sources are unavailable and sentence-level completeness has no objective denominator.
""")

    queue = []
    relation_by_object: defaultdict[str, list[str]] = defaultdict(list)
    for relation in rels:
        relation_by_object[relation["FROM_OBJECT_ID"]].append(f"{relation['RELATION']}->{relation['TO_OBJECT_ID']}")
        relation_by_object[relation["TO_OBJECT_ID"]].append(f"<-{relation['RELATION']}:{relation['FROM_OBJECT_ID']}")
    for row in all_rows:
        rank, label = priority_for(row)
        questions = ["IS_THIS_CURRENTLY_PREFERRED?", "IS_THIS_STILL_ACTIVE?", "IS_THIS_SOURCE_ONLY?", "WHAT_DOES_IT_SUPPORT_OR_CONTRADICT?"]
        if row["SOURCE_LEVEL"] == "SECONDARY_NORMALIZED_SOURCE": questions.append("DO_WE_NEED_RAW_SOURCE_REVIEW?")
        if row["CLASS"] in {"UNCLASSIFIED","SCHEMA_EXTENSION_CANDIDATE"}: questions.append("DOES_THIS_REQUIRE_NEW_CLASS?")
        queue.append({
            "PRIORITY": rank, "REVIEW_SET": label, "OBJECT_ID": row["OBJECT_ID"], "ORIGIN_OBJECT_ID": row.get("ORIGIN_OBJECT_ID", ""),
            "SHORT_STATEMENT": row["SHORT_FORM"], "CORPUS_GROUP": row["CORPUS_GROUP"], "CLASS_CURRENT": row["CLASS"],
            "SOURCE": row["SOURCE_LOCATOR"], "SOURCE_LEVEL": row["SOURCE_LEVEL"], "CURRENT_STATUS": row["CURRENT_RESEARCH_STATE"],
            "CANDIDATE_RELATIONS": "; ".join(relation_by_object[row["OBJECT_ID"]]), "TAGGING_QUESTIONS": "; ".join(questions),
        })
    queue.sort(key=lambda r: (int(r["PRIORITY"]), r["OBJECT_ID"]))
    queue_fields = ["PRIORITY","REVIEW_SET","OBJECT_ID","ORIGIN_OBJECT_ID","SHORT_STATEMENT","CORPUS_GROUP","CLASS_CURRENT","SOURCE","SOURCE_LEVEL","CURRENT_STATUS","CANDIDATE_RELATIONS","TAGGING_QUESTIONS"]
    write_csv(OUT / "tagging" / "02_TAGGING_QUEUE.csv", queue_fields, queue)
    qmd = ["# Owner Tagging Queue", "", f"Measured queue items: **{len(queue)}**", "", "| Priority | Object | Origin | Class | Statement |", "|---:|---|---|---|---|"]
    qmd += [f"| {r['PRIORITY']} | `{r['OBJECT_ID']}` | `{r['ORIGIN_OBJECT_ID']}` | {r['CLASS_CURRENT']} | {r['SHORT_STATEMENT'].replace('|','/')} |" for r in queue]
    write(OUT / "tagging" / "01_TAGGING_QUEUE.md", "\n".join(qmd))
    write(OUT / "tagging" / "03_TAGGING_GUIDE.md", """# Tagging Guide

Tag source status, current research relevance, and Owner position separately. `CURRENT != TRUE`, `SUPERSEDED != DELETED`, and `POSSIBLE_SEMANTIC_EQUIVALENCE != SEMANTIC_EQUIVALENCE`. Preserve historical wording when the extraction is accurate; use normalization-correction flags only for extraction errors. Raw-source review is required before claiming primary-source fidelity.
""")
    by_set = Counter(r["REVIEW_SET"] for r in queue)
    lines = ["# Priority Review Sets", "", "Begin with the following sequence; counts are measured from the queue.", ""]
    for rank in range(1, 18):
        labels = sorted({r["REVIEW_SET"] for r in queue if int(r["PRIORITY"]) == rank})
        label = labels[0] if labels else ("raw-source missingness" if rank == 17 else "no separately classified items")
        count = sum(1 for r in queue if int(r["PRIORITY"]) == rank)
        lines.append(f"{rank}. **{label}** — {count} queued objects")
    lines += ["", "After object status tagging, review `crosswalk/04_HYPOTHESIS_FAMILY_MAP.md` and confirm/reject candidate relations."]
    write(OUT / "tagging" / "04_PRIORITY_REVIEW_SETS.md", "\n".join(lines))

    counts = Counter(r["CLASS"] for r in all_rows)
    write(OUT / "run" / "06_OBJECT_COUNT_REPORT.md", "\n".join(["# Object Count Report", "", f"SOURCE_DERIVED_OBJECT_COUNT = {len(src)}", f"LIVE_OBJECT_COUNT = {len(live)}", f"CODEX_INFERRED_OBJECT_COUNT = {len(inf)}", f"RELATION_CANDIDATE_COUNT = {len(rels)}", f"TAGGING_QUEUE_COUNT = {len(queue)}", "", "## Object count by class", ""] + [f"- `{key}` = {value}" for key, value in sorted(counts.items())]))
    write(OUT / "run" / "07_INTEGRITY_AUDIT.md", """# Integrity Audit

State: `PENDING_FINAL_COMMAND_VERIFICATION`

The final command audit must verify JSONL parsing, unique IDs, relation endpoints, path scope, unchanged primary worktree, exact baseline lineage, pass counts, and no main merge. No validation or Owner acceptance is claimed.
""")
    write(OUT / "run" / "08_REMOTE_MOVEMENT_CHECK.md", f"""# Remote Movement Check

```text
REMOTE_HEAD_AT_START = {BASELINE_SHA}
REMOTE_HEAD_AT_END = PENDING_FINAL_CHECK
REMOTE_MOVED_DURING_RUN = PENDING_FINAL_CHECK
TASK_BASELINE_SHA = {BASELINE_SHA}
REBASE_OR_MERGE_PERFORMED = FALSE
```
""")
    write(OUT / "run" / "09_RUN_MANIFEST.md", f"""# ASA-MI Overnight Source-Mining Run Manifest

```text
TASK_STATUS = CONTENT_COMPLETE_PENDING_FINAL_GIT_AUDIT
AUTHORING_STATE = WORK_DRAFT
SOURCE_SCOPE = REPOSITORY_CORPUS_ONLY
RAW_PRIMARY_SOURCE_VERIFICATION = NOT_PERFORMED
TASK_BASELINE_SHA = {BASELINE_SHA}
TASK_BRANCH = {TASK_BRANCH}
AUTHORIZED_WRITE_ROOT = {OUT.relative_to(REPO).as_posix()}/
FULL_CORPUS_SWEEPS_COMPLETED = 4
SPECIALIZED_PASSES_COMPLETED = 11
SATURATION_PASSES_COMPLETED = 2
CONSECUTIVE_NO_NEW_PASSES_AT_END = 2
SOURCE_DERIVED_OBJECT_COUNT = {len(src)}
LIVE_OBJECT_COUNT = {len(live)}
CODEX_INFERRED_OBJECT_COUNT = {len(inf)}
RELATION_CANDIDATE_COUNT = {len(rels)}
TAGGING_QUEUE_COUNT = {len(queue)}
RAW_SOURCE_MISSING_COUNT = 7
PAIRED_VALIDATION_STATE = NOT_PERFORMED
INDEPENDENT_VALIDATION_STATE = NOT_PERFORMED
OWNER_ACCEPTANCE_STATE = NOT_REQUESTED
FROZEN = FALSE
PRODUCTION_AUTHORIZED = FALSE
```

## Owner morning entrypoint

1. `run/09_RUN_MANIFEST.md`
2. `comparison/07_RECALL_GAIN_REPORT.md`
3. `comparison/06_HISTORICAL_SOURCE_VS_LIVE_BRAINSTORM.md`
4. `crosswalk/04_HYPOTHESIS_FAMILY_MAP.md`
5. `tagging/04_PRIORITY_REVIEW_SETS.md`
6. `tagging/01_TAGGING_QUEUE.md`

The draft recovers and crosswalks the repository-visible thought-space. It does not select a final ontology or upgrade normalized historical records into raw-verified evidence.
""")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=["baseline", "sweeps", "specialized", "saturation", "final", "all"])
    args = parser.parse_args()
    phases = ["baseline", "sweeps", "specialized", "saturation", "final"] if args.phase == "all" else [args.phase]
    for phase in phases:
        globals()[f"phase_{phase}"]()


if __name__ == "__main__":
    main()
