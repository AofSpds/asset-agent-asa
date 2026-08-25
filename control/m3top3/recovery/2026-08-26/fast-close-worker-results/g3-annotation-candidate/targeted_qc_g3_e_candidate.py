#!/usr/bin/env python3
"""Single-pass structural QC for the exact G3-E queue candidate."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent
FIELDS = [
    "valuation_observation_status",
    "latest_revenue",
    "latest_OP",
    "latest_margin",
    "Forward_EPS",
    "Forward_OP",
    "EPS_OP_revision",
    "consensus_provider",
    "observation_at",
    "guidance",
    "PO_order_status",
    "backlog_status",
    "qualification_status",
    "volume_repeat_order_status",
    "design_win_customer_adoption_status",
    "fab_capex_state_status",
    "latest_material_earnings_guidance_refs",
]


def main() -> None:
    keys: list[str] = []
    windows: Counter[str] = Counter()
    slots = 0
    queue_path = ROOT / "G3_E_ANNOTATION_INGEST_QUEUE_v0.1.jsonl"
    with queue_path.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, 1):
            row = json.loads(line)
            assert row["queue_id"] == "AAA-M3TOP3-G3E-ANNOTATION-INGEST-QUEUE-v0.1"
            assert row["row_ingest_state"] == "QUEUE_ONLY_NOT_ADMITTED"
            assert row["source_bundle_plan_state"] == "UNFROZEN"
            assert row["annotation_sidecar_state"] == "ABSENT"
            assert row["outcome_access_flag"] is None
            assert row["company_id"] == f'KRX:{row["krx_code"]}'
            assert set(row["field_slots"]) == set(FIELDS)
            for field in FIELDS:
                slot = row["field_slots"][field]
                assert slot == {
                    "source_sheet_state": "NEEDS_RESEARCH",
                    "value": None,
                    "collection_state": "NOT_COLLECTED",
                    "local_recovery_state": "BLOCKED_EXTERNAL_HISTORICAL_RETRIEVAL_REQUIRED",
                    "source_evidence_ref": None,
                    "publication_at": None,
                    "available_before_cutoff": None,
                    "admission_state": "BLOCKED_NO_LOCAL_CUTOFF_SAFE_EVIDENCE",
                }, (line_no, field, slot)
            keys.append(row["row_key"])
            windows[row["window_id"]] += 1
            slots += len(row["field_slots"])

    assert len(keys) == 1016
    assert len(set(keys)) == 1016
    assert windows == Counter({f"W{i}": 127 for i in range(1, 9)})
    assert slots == 17272

    registry = json.loads(
        (ROOT / "G3_E_ANNOTATION_INGEST_FIELD_REGISTRY_v0.1.json").read_text(encoding="utf-8")
    )
    assert registry["field_count"] == 17
    assert [item["field_name"] for item in registry["fields"]] == FIELDS

    summary = json.loads(
        (ROOT / "G3_E_LOCAL_RECOVERABILITY_SUMMARY_v0.1.json").read_text(encoding="utf-8")
    )
    assert summary["counts"]["content_values_recoverable"] == 0
    assert summary["counts"]["publication_at_recoverable_for_annotation"] == 0
    assert summary["counts"]["source_evidence_ref_recoverable_for_annotation"] == 0

    print(
        json.dumps(
            {
                "queue_rows_passed": len(keys),
                "unique_row_keys": len(set(keys)),
                "field_slots_passed": slots,
                "window_counts": dict(sorted(windows.items())),
                "content_values_recovered": 0,
                "qc_class": "TARGETED_SINGLE_PASS_MECHANICAL",
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
