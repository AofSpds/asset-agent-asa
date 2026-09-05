"""Create-once F02-R1 inputs from five previously preserved KIND sources.

This is a fixed versioned admission profile, not a discovery/parser service.
No network, model arithmetic, scores, outcomes or file writes occur here.
"""
from __future__ import annotations

import copy
import hashlib
import json
import re
import stat
from decimal import Decimal
from datetime import date
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

SOURCE_MANIFEST_SCHEMA = "M3TOP3-F02-R1-SOURCE-MANIFEST-v1.0"
FEATURE_LEAF_SCHEMA = "M3TOP3-F02-R1-FEATURE-LEAF-v1.0"
ADMISSION_METHOD = "F02_R1_LATEST_CONFIRMED_QUARTER_NATIVE_UNITS_v1"
RUN_ID = "AAA-M3TOP3-F02-R1-20260905-171755-CODEX-01"
RUN_ROOT = "control/m3top3/f02-r1-multi-company-input-repair/v1.0/runs/" + RUN_ID
CREATED_AT = "2026-09-05T18:35:50.3101487+09:00"
PROFILE_DESIGN_AT = "2026-09-05T18:24:00+09:00"
SCIENTIFIC_STATE = "EXPLORATORY_AFTER_W1_OUTCOME_EXPOSURE"
PROFILE_ID = "F02_R1_EXPLORATORY_V1"
MANIFEST_ID = RUN_ID + "-SOURCE-MANIFEST-R1"
MAPPING_PATH = RUN_ROOT + "/inputs/INPUT_MAPPING_R1.json"
MANIFEST_PATH = RUN_ROOT + "/inputs/SOURCE_MANIFEST.json"
SIDECAR_PATH = RUN_ROOT + "/inputs/FEATURE_SIDECAR.jsonl"
PC1_RECEIPT = (
    "control/m3top3/process-calibration/v1.0/runs/"
    "AAA-M3TOP3-PROCESS-CALIBRATION-PC1-20260905-143739-CODEX-01/F02_DISCOVERY_RECEIPT.json"
)
CACHE_ROOT = (
    "control/m3top3/real-input-replay/v1.0/runs/"
    "AAA-M3TOP3-REAL-INPUT-STRICT-PRAGMATIC-20260905-114150-CODEX-01"
)
DEPENDENCY_PINS = {
    RUN_ROOT + "/INPUT_POLICY_R1.json": "fb62b4afb0f4e3edddcbc8b95e15cd2ea4288be72b9a93c135a9b687f9e0d680",
    RUN_ROOT + "/OWNER_AUTHORIZATION_BINDING.json": "96aff4ada2cc2a816bbc0b2536d58b4fed54680489cb15f88f78e63598d59404",
    RUN_ROOT + "/P2_DISPOSITION_AND_IMPLEMENTATION_SCOPE.json": "da75fea80d60bf32c530d2bd04cbffdb0da4e8a2edc40212db34dc95ac3e3df0",
    RUN_ROOT + "/worker-results/P2_MODEL_MEANING_CLASSIFICATION.json": "59108fb5b82bcc6622aaeaa1fff475cc7c3563bbe97c9dbd124bd332d7b5e42c",
    RUN_ROOT + "/worker-results/P2_CONTROL_PROVENANCE_CLASSIFICATION.json": "8c763b1924c210db7ea97b5e19ea53a62e7532e1b101af72b42113dab30cb1b6",
    RUN_ROOT + "/worker-ledgers/source_research_a.jsonl": "5a71fc2fa25e20a5ffc66b72e015cb4de56d7fc3bb34adba2754fe9f51d9eb81",
    RUN_ROOT + "/worker-ledgers/source_research_b.jsonl": "5c06bfe4831510f642af39cb6f1aa9209e15bdf7c14aeaefa5195961c44ee73d",
    RUN_ROOT + "/worker-ledgers/source_research_a_result.json": "d84925e78e5fc7e20051a2fac7421e3b7ee0d269666bd7844db380ba96355603",
    RUN_ROOT + "/worker-results/source_research_b_result.json": "9b5f8d1bcb2140456a9b78de2c3758efdf52dd3cb754aa1ef4ada3e1d7d09f2a",
    PC1_RECEIPT: "57cf0a0a7e7d316f86c6591a240cbcddadb894830c827a4d207219631d33b9af",
    CACHE_ROOT + "/inputs/SOURCE_MANIFEST.json": "4752fdad038681d6c09381176bdd8ca1837f9ecdd9201eafb3bd4ea682d534de",
}


def _q1(code, issuer, date, directory, receipt, size, sha, blob, group_line,
        sequence, revenue_label, op_label, op_row, pairs, acquired, action, q2_url, q2_action):
    return {
        "company_id": "KRX:" + code, "krx_code": code, "issuer": issuer,
        "source_id": f"SRC-KRX-KIND-{code}-{date.replace('-', '')}-{receipt}",
        "publication_date": date,
        "canonical_locator": f"https://kind.krx.co.kr/external/{date.replace('-', '/')}/{directory}/{receipt}/11013.htm",
        "raw_storage_ref": f"{RUN_ROOT}/sources/KRX-{code}/KRX_{code}_{date.replace('-', '')}_Q1_REPORT_11013.htm",
        "raw_artifact": {"byte_size": size, "sha256": sha, "git_blob": blob, "media_type": "text/html", "charset": "UTF-8"},
        "title": "분기보고서", "basis": "CONSOLIDATED", "unit": "KRW",
        "current_period": "2024Q1", "prior_period": "2023Q1", "quarter_length": "3_MONTHS",
        "context_table_line": group_line + 1, "table_line": group_line + 28,
        "statement_title": "연결 손익계산서" if code == "003160" else "연결 포괄손익계산서",
        "sequence": sequence, "metric_labels": {"revenue": revenue_label, "operating_profit": op_label},
        "metric_rows": {"revenue": 3, "operating_profit": op_row},
        "value_columns": {"current": 2, "prior": 4}, "metric_pairs": pairs,
        "acquired_at": acquired, "acquisition_action_id": action,
        "source_receipt_path": RUN_ROOT + "/worker-ledgers/source_research_" + ("a.jsonl" if code in {"003160", "025560"} else "b.jsonl"),
        "q2_evidence": {"selected": False, "after_cutoff_candidate_url": q2_url,
                        "after_cutoff_candidate_public_date": "2024-08-14",
                        "bounded_query_action_id": q2_action,
                        "supplementary_receipt_path": None if code in {"003160", "025560"} else PC1_RECEIPT,
                        "global_absence_state": "NOT_PROVEN",
                        "selection": "LATEST_CONFIRMED_CUTOFF_SAFE_IN_BOUNDED_SET_Q1_FALLBACK"},
        "limitations": ["Q1_FALLBACK", "DATE_ONLY_PUBLICATION", "NOT_GLOBAL_Q2_ABSENCE", "HETEROGENEOUS_Q1_Q2_OBSERVED_COHORT"],
        "restatement_note": None,
    }


SOURCE_SPECS = (
    _q1("003160", "(주)디아이", "2024-05-16", "001334", "20240516003155", 1404585,
        "2ab621a3862041c57040524aaa3c084c81304685015cbc2be7e6b57ba5fa3fe3", "b99d90f62b47c52389356318ccb328395dcf1130", 6515, 64, "매출액", "영업이익", 8,
        {"revenue": ["34732575950", "39216899579"], "operating_profit": ["-1836830457", "865831578"]},
        "2026-09-05T17:36:24.3732978+09:00", "SRA-003160-0009",
        "https://kind.krx.co.kr/external/2024/08/14/002471/20240814007837/11012.htm", "SRA-003160-0010"),
    _q1("025560", "미래산업 주식회사", "2024-05-14", "001496", "20240514003275", 1325372,
        "a547f8b383ecb85f39d5826ab08bf6641c6716a85ba12ddc90efb5c9f303537f", "44a8179c1a003db97cc4e1bc733208edcc0b1df4", 3983, 34, "수익(매출액)", "영업이익(손실)", 7,
        {"revenue": ["5162565692", "4785829491"], "operating_profit": ["2040268633", "-442977057"]},
        "2026-09-05T17:30:31.7466136+09:00", "SRA-025560-0005",
        "https://kind.krx.co.kr/external/2024/08/14/001390/20240814004272/11012.htm", "SRA-025560-0002"),
    _q1("031980", "피에스케이홀딩스 주식회사", "2024-05-16", "000652", "20240516001477", 961791,
        "8323d301baa3f62a872f2dec7f846d98d0effc0e9e06f7ea6dca5c7c78a598a9", "89a0ebd92b90207ba8e0f5e947f5350c92714039", 4222, 35, "수익(매출액)", "영업이익(손실)", 7,
        {"revenue": ["38094447594", "14913281644"], "operating_profit": ["15420952017", "3496296368"]},
        "2026-09-05T17:37:43.2995087+09:00", "SRB-031980-0008",
        "https://kind.krx.co.kr/external/2024/08/14/003322/20240814010557/11012.htm", "SRB-031980-0009"),
    _q1("036200", "유니셈 주식회사", "2024-05-10", "000637", "20240510001413", 1083117,
        "63152e6f1ba5c1b063c6466b54c3d7b7382d948de0aa36f19f8a208a3cb58ab2", "0e451a3feb018cc4d38bd53915d535a44674e267", 4380, 29, "Ⅰ.매출액", "Ⅴ.영업이익", 7,
        {"revenue": ["55186952755", "51753687853"], "operating_profit": ["4559702713", "4333422148"]},
        "2026-09-05T17:37:43.2995087+09:00", "SRB-036200-0008",
        "https://kind.krx.co.kr/external/2024/08/14/003029/20240814009619/11012.htm", "SRB-036200-0009"),
    {
        "company_id": "KRX:005290", "krx_code": "005290", "issuer": "(주)동진쎄미켐",
        "source_id": "SRC-KRX-KIND-005290-20240802-70956", "publication_date": "2024-08-02",
        "canonical_locator": "https://kind.krx.co.kr/external/2024/08/02/000210/20240730000320/70956.htm",
        "raw_storage_ref": CACHE_ROOT + "/sources/W1/KRX-005290/KRX_005290_20240802_PROVISIONAL_EARNINGS_70956.htm",
        "raw_artifact": {"byte_size": 16221, "sha256": "5c361107cbd2dc35b236b5358595e036ecb1dd9dc8b06471bca7bf9e550c7db7", "git_blob": "82be77ca6edb47695ca52ccf0ac2b1c69605129f", "media_type": "text/html", "charset": "UTF-8"},
        "title": "연결재무제표 기준 영업(잠정)실적(공정공시)", "basis": "CONSOLIDATED", "unit": "KRW_MILLION",
        "current_period": "2024Q2", "prior_period": "2023Q2", "quarter_length": "3_MONTHS",
        "context_table_line": 18, "table_line": 18, "statement_title": "1. 연결실적내용", "sequence": None,
        "metric_labels": {"revenue": "매출액", "operating_profit": "영업이익"},
        "metric_rows": {"revenue": 5, "operating_profit": 7}, "value_columns": {"current": 3, "prior": 6},
        "metric_pairs": {"revenue": ["355414", "331317"], "operating_profit": ["49972", "45565"]},
        "acquired_at": "2026-09-05T12:04:39.4397484+09:00", "acquisition_action_id": "NETWORK_ATTEMPT_18_PRESERVED_FETCH",
        "source_receipt_path": CACHE_ROOT + "/inputs/SOURCE_MANIFEST.json",
        "q2_evidence": {"selected": True, "selection": "EXACT_CACHED_CONTROL_NO_REFETCH", "global_absence_state": "NOT_ASSESSED"},
        "limitations": ["PROVISIONAL_NOT_FINAL", "AUDITOR_REVIEW_REPORT_NOT_YET_ISSUED", "MAY_CHANGE_DURING_AUDIT", "CACHED_CONTROL_NO_REFETCH", "HETEROGENEOUS_Q1_Q2_OBSERVED_COHORT"],
        "restatement_note": None,
    },
)
SOURCE_SPECS[0]["limitations"].append("NEGATIVE_CURRENT_OPERATING_PROFIT_PROFIT_TO_LOSS")
SOURCE_SPECS[1]["limitations"].extend(["RESTATED_PRIOR_OPERATING_PROFIT", "NEGATIVE_PRIOR_OPERATING_PROFIT_TURNAROUND", "SIGNED_CHANGE_VS_ABSOLUTE_PRIOR_NOT_CONVENTIONAL_POSITIVE_BASE_GROWTH"])
SOURCE_SPECS[1]["restatement_note"] = {
    "raw_note_line": 23818, "prior_before": "-448371497", "adjustment": "5394440", "prior_after": "-442977057",
    "raw_value_lines": [23874, 23875, 23876], "prior_revenue_unchanged": True,
    "reason": "SAME_CUTOFF_SAFE_SOURCE_DISCLOSED_DISCONTINUED_OPERATION_RECLASSIFICATION",
}
for _spec in SOURCE_SPECS:
    _q1_period = _spec["current_period"] == "2024Q1"
    _spec.update({
        "current_period_start": "2024-01-01" if _q1_period else "2024-04-01",
        "current_period_end": "2024-03-31" if _q1_period else "2024-06-30",
        "prior_period_start": "2023-01-01" if _q1_period else "2023-04-01",
        "prior_period_end": "2023-03-31" if _q1_period else "2023-06-30",
        "period_date_provenance": "EXPLICIT_SOURCE_PERIOD_DATES" if _q1_period else "EXPLICIT_SOURCE_CALENDAR_QUARTER_LABEL_TO_DATES",
        "disclosure_type": "FILED_QUARTERLY_REPORT" if _q1_period else "PROVISIONAL_EARNINGS_FAIR_DISCLOSURE",
        "confirmation_status": "OFFICIAL_FILED_QUARTERLY_STATEMENT_NO_AUDIT_ATTESTATION" if _q1_period else "PROVISIONAL_NOT_FINAL_AUDITOR_REVIEW_NOT_YET_ISSUED",
        "age_days_from_publication_to_cutoff": (date(2024, 8, 9) - date.fromisoformat(_spec["publication_date"])).days,
        "age_days_from_period_end_to_cutoff": (date(2024, 8, 9) - (date(2024, 3, 31) if _q1_period else date(2024, 6, 30))).days,
        "age_basis": "CALENDAR_DATE_DIFFERENCE_TO_W1_CUTOFF_DATE;NO_INTRADAY_PRECISION",
    })


def _legacy():
    from . import real_input_replay_v1
    return real_input_replay_v1


def _fail(message):
    raise _legacy().RealInputReplayError("F02-R1: " + message)


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")


def _equal(actual, expected, context):
    # Canonical JSON equality distinguishes bool from integer and rejects floats.
    l = _legacy()
    try:
        parsed = l._strict_json_loads(json.dumps(actual, ensure_ascii=False, allow_nan=False), context)
        same = l.canonical_json_bytes(parsed) == l.canonical_json_bytes(expected)
    except (TypeError, ValueError):
        _fail(context + ": invalid/non-exact JSON types")
    if not same:
        _fail(context + ": fixed versioned profile mismatch")


def _read_bound(repo: Path, relative: str, sha256: str | None = None) -> tuple[Path, bytes]:
    pure = PurePosixPath(relative)
    if pure.is_absolute() or "\\" in relative or ":" in relative or any(p in {"", ".", ".."} for p in relative.split("/")):
        _fail("invalid relative artifact path")
    target = repo
    try:
        for part in pure.parts:
            target = target / part
            info = target.lstat()
            if target.is_symlink() or getattr(info, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400):
                _fail("symlink/reparse artifact path is forbidden")
        target.resolve().relative_to(repo)
        data = target.read_bytes()
    except (OSError, ValueError) as exc:
        _fail("bound artifact is missing or path escaped: " + relative)
    if sha256 is not None and hashlib.sha256(data).hexdigest() != sha256:
        _fail("bound artifact SHA-256 mismatch: " + relative)
    return target, data


def _squash(text):
    return re.sub(r"\s+", "", text)


class _Tables(HTMLParser):
    """Record physical table/row/cell topology and whole decoded cell text."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tables = []
        self.stack = []

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            table = {"line": self.getpos()[0], "rows": [], "row": None, "cell": None}
            self.tables.append(table)
            self.stack.append(table)
        elif self.stack and tag == "tr":
            table = self.stack[-1]
            table["row"] = []
            table["rows"].append(table["row"])
        elif self.stack and tag in {"td", "th"}:
            table = self.stack[-1]
            if table["row"] is None:
                _fail("cell outside table row")
            cell = {"line": self.getpos()[0], "text": "", "tag": tag, "attrs": dict(attrs)}
            table["row"].append(cell)
            table["cell"] = cell
        elif self.stack and tag == "br" and self.stack[-1]["cell"] is not None:
            self.stack[-1]["cell"]["text"] += " "

    def handle_endtag(self, tag):
        if self.stack and tag in {"td", "th"}:
            self.stack[-1]["cell"] = None
        elif self.stack and tag == "table":
            self.stack.pop()

    def handle_data(self, data):
        if self.stack and self.stack[-1]["cell"] is not None:
            self.stack[-1]["cell"]["text"] += data


def _numeric_cell(text):
    value = text.strip()
    if not re.fullmatch(r"(?:0|[1-9]\d{0,2}(?:,\d{3})*|[1-9]\d*|\((?:[1-9]\d{0,2}(?:,\d{3})*|[1-9]\d*)\))", value):
        _fail("whole numeric cell has unsupported/extra text")
    negative = value.startswith("(")
    digits = value.strip("()").replace(",", "")
    return str(-int(digits) if negative else int(digits))


def parse_source_html(raw_bytes: bytes, spec: dict[str, Any]) -> dict[str, Any]:
    """Validate source semantics independently of the public validator's byte pins."""
    try:
        text = raw_bytes.decode("utf-8")
    except UnicodeDecodeError:
        _fail("source is not UTF-8")
    parser = _Tables()
    parser.feed(text)
    parser.close()
    by_line = {table["line"]: table for table in parser.tables}
    try:
        table = by_line[spec["table_line"]]
        context = by_line[spec["context_table_line"]]
    except KeyError:
        _fail("fixed financial table not found")
    rows = table["rows"]
    all_cells = [cell for t in parser.tables for row in t["rows"] for cell in row]
    issuer_cell = spec["issuer"] if spec["current_period"] == "2024Q1" else spec["issuer"] + " 금융팀"
    issuer_line = 86 if spec["current_period"] == "2024Q1" else 135
    issuer_cells = [c for c in all_cells if c["line"] == issuer_line]
    if len(issuer_cells) != 1 or _squash(issuer_cells[0]["text"]) != _squash(issuer_cell):
        _fail("exact issuer cell absent")
    date = spec["publication_date"]
    if spec["current_period"] == "2024Q1":
        year, month, day = date.split("-")
        date_cells = [c for c in all_cells if c["line"] == 46]
        date_pattern = rf"{year}년0?{int(month)}월0?{int(day)}일"
        if len(date_cells) != 1 or re.fullmatch(date_pattern, _squash(date_cells[0]["text"])) is None:
            _fail("exact publication-date cell absent")
        seq = spec["sequence"]
        expected_context = [
            [_squash(spec["statement_title"])],
            [f"제{seq}기1분기2024.01.01부터2024.03.31까지"],
            [f"제{seq-1}기1분기2023.01.01부터2023.03.31까지"],
            ["(단위:원)"],
        ]
        observed_context = [[_squash(c["text"]) for c in row] for row in context["rows"]]
        _equal(observed_context, expected_context, "consolidated period/unit context")
        _equal([_squash(c["text"]) for c in rows[0]], ["", f"제{seq}기1분기", f"제{seq-1}기1분기"], "quarter group headers")
        _equal([_squash(c["text"]) for c in rows[1]], ["3개월", "누적", "3개월", "누적"], "three-month/cumulative headers")
        if any(c["tag"] != "th" for row in rows[:2] for c in row):
            _fail("quarter header cells must be headers")
        if [c["attrs"].get("colspan") for c in rows[0][1:]] != ["2", "2"] or rows[0][0]["attrs"].get("rowspan") != "2":
            _fail("quarter header spans changed")
    else:
        if date.replace("-", ".") not in text or spec["title"] not in text:
            _fail("cached source title/date absent")
        _equal([_squash(c["text"]) for c in rows[1]], ["1.연결실적내용"], "cached consolidated statement")
        _equal([_squash(c["text"]) for c in rows[2]], ["구분(단위:백만원,%)", "당기실적", "전기실적", "전기대비증감액(증감율)", "전년동기실적", "전년동기대비증감액(증감율)"], "cached units/column headers")
        _equal([_squash(c["text"]) for c in rows[3]], ["(24년2분기)", "(24년1분기)", "(23년2분기)"], "cached quarter columns")
    parsed = {}
    for metric, pair in spec["metric_pairs"].items():
        row_number = spec["metric_rows"][metric]
        try:
            row = rows[row_number - 1]
            if _squash(row[0]["text"]) != _squash(spec["metric_labels"][metric]):
                _fail("metric row label mismatch")
            if spec["current_period"] == "2024Q1":
                _equal([_numeric_cell(c["text"]) for c in row[1:]], [pair[0], pair[0], pair[1], pair[1]], "whole current/prior and cumulative cells")
            elif len(row) != 7 or _squash(row[1]["text"]) != "당해실적":
                _fail("cached current-quarter row topology mismatch")
            for offset, field in enumerate(("current", "prior")):
                column = spec["value_columns"][field]
                observed = _numeric_cell(row[column - 1]["text"])
                if observed != pair[offset] or (field == "prior" and Decimal(observed) == 0):
                    _fail("whole numeric cell value/sign/zero-prior mismatch")
                parsed[f"/metric_pairs/{metric}/{field}"] = {
                    "value": observed,
                    "locator": f"html:table-line-{spec['table_line']}/row-{row_number}/cell-{column}",
                    "cell_start_line": row[column - 1]["line"],
                }
        except IndexError:
            _fail("fixed metric row/cell absent")
    if spec["restatement_note"] is not None:
        lines = text.splitlines()
        note = spec["restatement_note"]
        if not all(part in lines[note["raw_note_line"] - 1] for part in ("중단영업", "영업이익이 조정")):
            _fail("same-source restatement explanation absent")
        for line, expected in zip(note["raw_value_lines"], (note["prior_before"], note["adjustment"], note["prior_after"])):
            matching = [c for c in all_cells if c["line"] == line]
            if len(matching) != 1 or _numeric_cell(matching[0]["text"]) != expected:
                _fail("same-source restatement amount mismatch")
    return parsed


def _dependencies(repo):
    result = []
    for path, sha in sorted(DEPENDENCY_PINS.items()):
        _, data = _read_bound(repo, path, sha)
        result.append({"path": path, "byte_size": len(data), "sha256": sha})
    return result


def _source(spec):
    date = spec["publication_date"]
    return {
        "source_id": spec["source_id"], "company_id": spec["company_id"], "krx_code": spec["krx_code"],
        "source_type": "FILING", "source_tier": None, "title": spec["title"],
        "publisher": "KOREA_EXCHANGE_KIND_OFFICIAL", "publication_at": None,
        "publication_date": date, "publication_precision": "DATE_ONLY",
        "publication_interval": {"earliest_at": date + "T00:00:00+09:00", "latest_at": date + "T23:59:59+09:00", "bound_method_id": "DATE_ONLY_KST_CLOSED_DAY_v1"},
        "canonical_locator": spec["canonical_locator"], "raw_storage_ref": spec["raw_storage_ref"],
        "raw_artifact": copy.deepcopy(spec["raw_artifact"]), "acquired_at": spec["acquired_at"],
        "acquisition": {"actor_id": "AAA-PMO-ORCHESTRATOR", "method": "REUSE_EXACT_PRESERVED_BYTES_NO_REFETCH", "request_ref": spec["source_receipt_path"] + "#" + spec["acquisition_action_id"]},
        "status": "PRESERVED_RAW", "source_limitations": copy.deepcopy(spec["limitations"]),
        "outcome_custody": {"state": SCIENTIFIC_STATE, "prior_actor_w1_outcome_exposure": True, "continuation_source_refetch_count": 0, "blind_process_claim": False},
        "admission": {"state": "ADMITTED_EXPLORATORY_CUTOFF_SAFE", "temporal_status": "CUTOFF_SAFE", "cutoff_at": _legacy().W1_MAPPING["snapshot_cutoff_at"], "reason_code": ADMISSION_METHOD, "evaluated_at": CREATED_AT},
    }


def _make_leaves(manifest, manifest_sha, parsed_by_id):
    l = _legacy()
    leaves = []
    for spec in SOURCE_SPECS:
        date = spec["publication_date"]
        cid = spec["company_id"]
        for metric in ("operating_profit", "revenue"):
            for field in ("change_mode", "current", "operator_id", "prior"):
                observed = field in {"current", "prior"}
                pointer = f"/metric_pairs/{metric}/{field}"
                numeric = parsed_by_id[spec["source_id"]].get(pointer)
                value = numeric["value"] if observed else ("RELATIVE" if field == "change_mode" else l.F02_OPERATOR_ID)
                leaves.append({
                    "schema_version": FEATURE_LEAF_SCHEMA, "record_id": l._record_id(cid, metric, field),
                    "run_id": RUN_ID, "source_manifest_id": MANIFEST_ID, "source_manifest_sha256": manifest_sha,
                    "population_row_key": "W1|" + cid, "window_id": "W1", "snapshot_cutoff_at": l.W1_MAPPING["snapshot_cutoff_at"],
                    "company_id": cid, "krx_code": spec["krx_code"], "feature_id": l.F02, "input_path": pointer,
                    "value": value, "value_type": "DECIMAL" if observed else ("ENUM" if field == "change_mode" else "IDENTIFIER"),
                    "unit_or_category": spec["unit"] if observed else ("UNITLESS_ENUM" if field == "change_mode" else "METHOD_ID"),
                    "availability_state": "AVAILABLE", "evidence_kind": "OBSERVED" if observed else "DERIVED", "temporal_status": "CUTOFF_SAFE",
                    "publication_at_or_interval": {"precision": "DATE_ONLY", "publication_at": None, "publication_date": date, "latest_possible_at": date + "T23:59:59+09:00", "bound_method_id": "DATE_ONLY_KST_CLOSED_DAY_v1"},
                    "effective_period": {"label": spec["current_period"] if field == "current" else spec["prior_period"] if field == "prior" else spec["current_period"] + "_VS_" + spec["prior_period"], "basis": "QUARTER" if observed else "QUARTER_COMPARISON", "scope": "CONSOLIDATED"},
                    "produced_at": CREATED_AT,
                    "source_refs": [{"source_id": spec["source_id"], "source_content_sha256": spec["raw_artifact"]["sha256"], "locator": numeric["locator"]}] if observed else [],
                    "transform_or_estimation_method_id": None if observed else l.F02_OPERATOR_ID,
                    "input_lineage_refs": [] if observed else sorted([l._record_id(cid, metric, "current"), l._record_id(cid, metric, "prior")]),
                    "contains_estimated_input": False, "missing_reason": None,
                    "admission": {"state": "ADMITTED", "reason_code": ADMISSION_METHOD + (":OBSERVED" if observed else ":DERIVED_CONTROL"), "decided_at": CREATED_AT},
                })
    return sorted(leaves, key=lambda row: (row["window_id"], row["company_id"], row["feature_id"], row["input_path"]))


def build_inputs(repo) -> tuple[dict, dict, list[dict]]:
    """Return deterministic input objects; never write or fetch anything."""
    repo = Path(repo).resolve()
    l = _legacy()
    dependencies = _dependencies(repo)
    parsed = {}
    for spec in SOURCE_SPECS:
        _, data = _read_bound(repo, spec["raw_storage_ref"], spec["raw_artifact"]["sha256"])
        if len(data) != spec["raw_artifact"]["byte_size"] or l._git_blob_oid(data) != spec["raw_artifact"]["git_blob"]:
            _fail("source size/Git blob mismatch")
        parsed[spec["source_id"]] = parse_source_html(data, spec)
    mapping = {
        "schema_version": "M3TOP3-F02-R1-INPUT-MAPPING-v1.0", "run_id": RUN_ID,
        "created_at": CREATED_AT, "profile_design_at": PROFILE_DESIGN_AT, "admission_method": ADMISSION_METHOD, "scientific_state": SCIENTIFIC_STATE,
        "feature_id": l.F02, "change_mode": "RELATIVE", "operator_id": l.F02_OPERATOR_ID,
        "consumed_registry_git_blob": "5faa4d5739bf9ecb0c11d16f6d7d697ff3983977",
        "consumed_registry_historical_locator": l.FEATURE_INPUT_REGISTRY_REF,
        "registry_resolution": "EXACT_READABLE_GIT_BLOB_NOT_CLAIMED_HISTORICAL_PATH_RESOLUTION",
        "numeric_policy": "SOURCE_NATIVE_SIGNED_DECIMAL_NO_UNIT_CONVERSION_NO_ROUNDING",
        "input_selection": "D1_LATEST_CONFIRMED_CUTOFF_SAFE_Q2_PREFERRED_Q1_FALLBACK",
        "claim_ceiling": "F02_ONLY_OBSERVED_COHORT_PROVISIONAL_NO_OFFICIAL_TOP3_TOP10",
        "sources": copy.deepcopy(list(SOURCE_SPECS)), "parsed_cell_bindings": parsed,
        "dependencies": dependencies,
    }
    mapping_bytes = json_bytes(mapping)
    mapping_ref = {"path": MAPPING_PATH, "byte_size": len(mapping_bytes), "sha256": hashlib.sha256(mapping_bytes).hexdigest()}
    manifest = {
        "schema_version": SOURCE_MANIFEST_SCHEMA, "manifest_id": MANIFEST_ID, "run_id": RUN_ID,
        "created_at": CREATED_AT, "purpose": "MODEL_INPUT_ONLY",
        "population_binding": {"revision": l.POPULATION_REVISION, "path": l.POPULATION_PATH, "git_blob": l.POPULATION_GIT_BLOB, "compressed_sha256": l.POPULATION_SHA256, "row_count": l.POPULATION_ROW_COUNT},
        "windows": [{"window_id": "W1", "window_anchor_date": l.W1_MAPPING["window_anchor_date"], "snapshot_cutoff_at": l.W1_MAPPING["snapshot_cutoff_at"], "entry_date": l.W1_MAPPING["entry_trade_date"], "include_count": 57}],
        "sources": [_source(spec) for spec in SOURCE_SPECS],
        "input_profile": {"profile_id": PROFILE_ID, "admission_method": ADMISSION_METHOD,
                          "scientific_state": SCIENTIFIC_STATE, "prior_actor_w1_outcome_exposure": True,
                          "blind_process_claim": False, "new_source_actions_in_materialization": 0,
                          "fixed_company_ids": sorted(spec["company_id"] for spec in SOURCE_SPECS),
                          "mapping": mapping_ref, "dependencies": dependencies + [mapping_ref],
                          "consumed_registry_git_blob": "5faa4d5739bf9ecb0c11d16f6d7d697ff3983977",
                          "heterogeneous_periods": "FOUR_2024Q1_VS_2023Q1_AND_CACHED_005290_2024Q2_VS_2023Q2",
                          "unit_policy": "NATIVE_PAIR_UNITS_DIMENSIONLESS_RELATIVE_NO_CONVERSION",
                          "claim_ceiling": "F02_ONLY_OBSERVED_COHORT_PROVISIONAL_NO_OFFICIAL_TOP3_TOP10"},
    }
    manifest_sha = hashlib.sha256(json_bytes(manifest)).hexdigest()
    return mapping, manifest, _make_leaves(manifest, manifest_sha, parsed)


def validate_source_manifest(manifest, *, manifest_content_sha256, repo, expected_run_id):
    if expected_run_id != RUN_ID:
        _fail("run identity mismatch")
    repo = Path(repo).resolve()
    mapping, expected, _ = build_inputs(repo)
    _equal(manifest, expected, "source manifest")
    _, mapping_data = _read_bound(repo, MAPPING_PATH)
    _, manifest_data = _read_bound(repo, MANIFEST_PATH)
    if mapping_data != json_bytes(mapping) or manifest_data != json_bytes(expected):
        _fail("persisted mapping/manifest bytes differ from fixed profile")
    if manifest_content_sha256 != hashlib.sha256(manifest_data).hexdigest():
        _fail("manifest content digest mismatch")
    by_id = {}
    for spec, source in zip(SOURCE_SPECS, expected["sources"]):
        path, data = _read_bound(repo, spec["raw_storage_ref"], spec["raw_artifact"]["sha256"])
        by_id[source["source_id"]] = {**source, "_repo": repo, "_raw_path": path, "_raw_text_lines": data.decode("utf-8").splitlines(), "_parsed_cells": parse_source_html(data, spec)}
    return by_id


def validate_feature_leaves(records: Iterable[dict], *, manifest, manifest_content_sha256,
                            sources, population_rows, expected_run_id):
    l = _legacy()
    if not isinstance(sources, dict) or set(sources) != {s["source_id"] for s in SOURCE_SPECS}:
        _fail("all five validated sources are required")
    repos = {str(source.get("_repo")) for source in sources.values()}
    if len(repos) != 1 or "None" in repos:
        _fail("validated source context missing")
    verified = validate_source_manifest(manifest, manifest_content_sha256=manifest_content_sha256,
                                        repo=next(iter(repos)), expected_run_id=expected_run_id)
    for source_id, source in sources.items():
        _equal({k: v for k, v in source.items() if not k.startswith("_")},
               {k: v for k, v in verified[source_id].items() if not k.startswith("_")}, "validated source envelope")
    population = {(r["window_id"], r["company_id"]): r for r in l.validate_population(population_rows)}
    for spec in SOURCE_SPECS:
        row = population.get(("W1", spec["company_id"]))
        if row is None or row["row_key"] != "W1|" + spec["company_id"] or row["historical_eligibility_status"] != "ELIGIBLE":
            _fail("source issuer is not frozen W1 eligible population")
    materialized = list(records)
    if len(materialized) != 40:
        _fail("all forty leaves are required")
    for record in materialized:
        l._assert_exact_keys(record, l.LEAF_KEYS, "R1 leaf")
        l.assert_no_outcome_fields(record)
    expected = _make_leaves(manifest, manifest_content_sha256, {sid: s["_parsed_cells"] for sid, s in verified.items()})
    try:
        materialized.sort(key=lambda r: (r["window_id"], r["company_id"], r["feature_id"], r["input_path"]))
    except (KeyError, TypeError):
        _fail("invalid leaf sort identity")
    _equal(materialized, expected, "complete observed and derived leaves")
    return materialized


def scientific_profile(manifest) -> dict:
    if manifest.get("schema_version") != SOURCE_MANIFEST_SCHEMA:
        _fail("scientific profile schema mismatch")
    return copy.deepcopy(manifest["input_profile"])
