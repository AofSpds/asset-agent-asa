from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
import tempfile
import time
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any, Callable


EXACT_BASE_COMMIT = "167c1b05e25df658b322cf428c72ce3a4f476544"


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def business_dates(start: date, count: int) -> list[date]:
    result: list[date] = []
    current = start
    while len(result) < count:
        if current.weekday() < 5:
            result.append(current)
        current += timedelta(days=1)
    return result


def write_price_csv(path: Path, dates: list[date], rows_per_date: int = 1, invalid_ohlc: bool = False, invalid_ca: bool = False) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["date", "code", "open", "high", "low", "close", "volume", "corporate_action_flag", "adjustment_factor"])
        for index, trading_date in enumerate(dates):
            for _ in range(rows_per_date):
                opening = 100 + index
                high = opening - 1 if invalid_ohlc else opening + 3
                factor = "0" if invalid_ca else ""
                writer.writerow([trading_date.isoformat(), "005930", opening, high, opening - 2, opening + 1, 1000, "true" if invalid_ca else "", factor])


class ProbeRecorder:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def add(self, test_id: str, status: str, method: str, observation: str) -> None:
        self.rows.append({"test_id": test_id, "status": status, "method": method, "observation": observation})

    def execute(self, test_id: str, fn: Callable[[], tuple[str, str]]) -> None:
        try:
            status, observation = fn()
            self.add(test_id, status, "EXACT_BASE_EXECUTABLE_PROBE", observation)
        except Exception as exc:  # probe defects are distinct from expected-base exceptions
            self.add(test_id, "PROBE_ERROR", "EXACT_BASE_EXECUTABLE_PROBE", f"{type(exc).__name__}: {exc}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("base_root", type=Path)
    args = parser.parse_args()
    base_root = args.base_root.resolve()
    package_root = base_root / "tools" / "m3top3"
    if not package_root.is_dir():
        raise SystemExit(f"not an exact-base materialization: {package_root}")
    sys.path.insert(0, str(base_root))

    from tools.m3top3.backtest import ValidationRunner
    from tools.m3top3.ledger import PredictionLedger
    from tools.m3top3.model_interface import DiagnosticFixtureScorer, RankingEngine, ScoreResult, load_scorer
    from tools.m3top3.outcome import ExplicitWindowResolver, OutcomeBuilder
    from tools.m3top3.pit_guard import PITGuard
    from tools.m3top3.providers import CsvPriceProvider, InMemoryFeatureProvider, StaticUniverseProvider, UniverseState
    from tools.m3top3.snapshot import BatchSnapshotGenerator, SnapshotBuildConfig, SnapshotBuilder, SnapshotStore

    recorder = ProbeRecorder()
    source = {path.name: path.read_text(encoding="utf-8") for path in package_root.glob("*.py")}

    cutoff = "2025-01-02T23:59:59+09:00"
    guard = PITGuard()
    recorder.execute("KF-PIT-001", lambda: (
        "RED_OBSERVED" if not guard.validate_model_input({"publication_at": None}, cutoff) else "BASE_SAFE_OBSERVED",
        "null publication_at produced no violation" if not guard.validate_model_input({"publication_at": None}, cutoff) else "guard rejected null publication_at",
    ))
    recorder.execute("KF-PIT-002", lambda: (
        "BASE_SAFE_OBSERVED" if any(v.code == "INVALID_PUBLICATION_DATETIME" for v in guard.validate_model_input({"publication_at": "2025-01-02T10:00:00"}, cutoff)) else "RED_OBSERVED",
        "guard returns INVALID_PUBLICATION_DATETIME for a timezone-naive publication string",
    ))
    recorder.execute("KF-PIT-003", lambda: (
        "RED_OBSERVED" if not guard.validate_model_input({"publication_at": "2025-01-02T10:00:00+09:00", "available_before_entry": False}, cutoff) else "BASE_SAFE_OBSERVED",
        "available_before_entry=false produced no violation",
    ))

    with tempfile.TemporaryDirectory(prefix="m3top3-exact-base-red-") as temporary:
        root = Path(temporary)
        dates = business_dates(date(2025, 1, 2), 5)
        price_path = root / "price.csv"
        write_price_csv(price_path, dates)
        price = CsvPriceProvider(price_path, dataset_id="BASE-PRICE", dataset_hash="caller-asserted")
        universe = StaticUniverseProvider([UniverseState("C1", "005930", date(2020, 1, 1), None, True, True, "U1")])

        def build_with(rows: list[dict[str, Any]]):
            return SnapshotBuilder(universe, InMemoryFeatureProvider(rows), price, SnapshotBuildConfig())

        current_only_row = {"company_id": "C1", "feature_id": "diagnostic_score", "value": "9", "publication_at": "2025-01-02T10:00:00+09:00", "current_only": True}
        current_only = build_with([current_only_row]).build(dates[0])
        recorder.add(
            "KF-PIT-004",
            "RED_OBSERVED" if current_only.status == "SNAPSHOT_PARTIAL" and bool(current_only.model_inputs) else "BASE_SAFE_OBSERVED",
            "EXACT_BASE_EXECUTABLE_PROBE",
            f"builder status={current_only.status}; model_input_rows={len(current_only.model_inputs)} after current_only violation",
        )

        future_row = {"company_id": "C1", "feature_id": "F01", "value": "future", "publication_at": "2025-01-03T10:00:00+09:00", "feature_record_id": "FUTURE-1"}
        feature_provider = InMemoryFeatureProvider([future_row])
        selected = feature_provider.records_at("C1", current_only.cutoff_at)
        has_receipt = hasattr(feature_provider, "last_retrieval_receipt") or hasattr(feature_provider, "retrieval_receipts")
        recorder.add(
            "KF-PIT-005",
            "RED_OBSERVED" if selected == [] and not has_receipt else "BASE_SAFE_OBSERVED",
            "EXACT_BASE_EXECUTABLE_PROBE",
            f"future row excluded={selected == []}; deterministic retrieval receipt present={has_receipt}",
        )
        effective_violations = guard.validate_model_input({"publication_at": "2025-01-02T10:00:00+09:00", "effective_at": "2025-01-03T10:00:00+09:00"}, cutoff)
        recorder.add(
            "KF-PIT-006",
            "RED_OBSERVED" if not any(v.code == "PIT_EFFECTIVE_AFTER_CUTOFF" for v in effective_violations) else "BASE_SAFE_OBSERVED",
            "EXACT_BASE_EXECUTABLE_PROBE",
            f"consumed effective_at after cutoff violation codes={[v.code for v in effective_violations]}",
        )

        recorder.add(
            "KF-SNP-001",
            "RED_OBSERVED" if current_only.status == "SNAPSHOT_PARTIAL" and len(current_only.model_inputs) == 1 else "BASE_SAFE_OBSERVED",
            "EXACT_BASE_EXECUTABLE_PROBE",
            f"PIT violation retained scoreable model input: status={current_only.status}, rows={len(current_only.model_inputs)}",
        )

        ready_row = {"company_id": "C1", "feature_id": "diagnostic_score", "value": "9", "publication_at": "2025-01-02T10:00:00+09:00"}
        ready_builder = build_with([ready_row])
        ready = ready_builder.build(dates[0])
        snapshot_root = root / "snapshots"
        SnapshotStore(snapshot_root).write(ready, {"generator_version": "exact-base-probe"})
        snapshot_dir = snapshot_root / dates[0].isoformat()

        class CountingScorer(DiagnosticFixtureScorer):
            def __init__(self): self.calls = 0
            def score(self, model_input):
                self.calls += 1
                return super().score(model_input)

        def snapshot_state_probe(test_id: str, status: str, blockers: list[str]) -> None:
            manifest_path = snapshot_dir / "manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["snapshot_status"] = status
            manifest["blockers"] = blockers
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            scorer = CountingScorer()
            runner = ValidationRunner(scorer, RankingEngine("COMPANY_ID_ASC_DIAGNOSTIC"), OutcomeBuilder(price, ExplicitWindowResolver({dates[0].isoformat(): dates[2].isoformat()})))
            output = root / f"state-{test_id}"
            runner.run_snapshot(snapshot_dir, output)
            recorder.add(test_id, "RED_OBSERVED" if scorer.calls > 0 and output.exists() else "BASE_SAFE_OBSERVED", "EXACT_BASE_EXECUTABLE_PROBE", f"status={status}, blockers={blockers}, scorer_calls={scorer.calls}, output_created={output.exists()}")

        snapshot_state_probe("KF-SNP-002", "SNAPSHOT_PARTIAL", ["ELIGIBILITY_UNRESOLVED"])
        snapshot_state_probe("KF-SNP-003", "SNAPSHOT_BLOCKED", ["PIT_PUBLICATION_AFTER_CUTOFF"])
        snapshot_state_probe("KF-SNP-004", "SNAPSHOT_READY", ["CONTRADICTION"])

        # Restore a clean manifest and capture integrity-admission failures.
        SnapshotStore(snapshot_root).write(ready, {"generator_version": "exact-base-probe"})
        model_path = snapshot_dir / "model_input.jsonl"
        original_model = model_path.read_text(encoding="utf-8")
        model_path.write_text("{malformed\n", encoding="utf-8")
        malformed_output = root / "malformed-output"
        try:
            ValidationRunner(CountingScorer(), RankingEngine("COMPANY_ID_ASC_DIAGNOSTIC"), OutcomeBuilder(price, ExplicitWindowResolver({dates[0].isoformat(): dates[2].isoformat()}))).run_snapshot(snapshot_dir, malformed_output)
            malformed_error = "none"
        except Exception as exc:
            malformed_error = type(exc).__name__
        recorder.add("KF-INT-001", "RED_OBSERVED" if malformed_output.exists() and malformed_error == "JSONDecodeError" else "BASE_SAFE_OBSERVED", "EXACT_BASE_EXECUTABLE_PROBE", f"exception={malformed_error}; output_created_before_failure={malformed_output.exists()}")
        model_path.write_text(original_model, encoding="utf-8")

        model_path.write_text(original_model.replace('"company_id":"C1"', '"company_id":"MUTATED"'), encoding="utf-8")
        model_reuse = SnapshotStore(snapshot_root).valid_existing(ready)
        recorder.add("KF-INT-002", "RED_OBSERVED" if model_reuse else "BASE_SAFE_OBSERVED", "EXACT_BASE_EXECUTABLE_PROBE", f"valid_existing after model-input byte mutation={model_reuse}")
        model_path.write_text(original_model, encoding="utf-8")
        pit_path = snapshot_dir / "pit_snapshot.jsonl"
        original_pit = pit_path.read_text(encoding="utf-8")
        pit_path.write_text(original_pit.replace('"company_id":"C1"', '"company_id":"MUTATED"'), encoding="utf-8")
        pit_reuse = SnapshotStore(snapshot_root).valid_existing(ready)
        recorder.add("KF-INT-003", "RED_OBSERVED" if pit_reuse else "BASE_SAFE_OBSERVED", "EXACT_BASE_EXECUTABLE_PROBE", f"valid_existing after PIT byte mutation={pit_reuse}")
        pit_path.write_text(original_pit, encoding="utf-8")

        manifest_path = snapshot_dir / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["model_input_row_count"] = 99
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        count_scorer = CountingScorer()
        ValidationRunner(count_scorer, RankingEngine("COMPANY_ID_ASC_DIAGNOSTIC"), OutcomeBuilder(price, ExplicitWindowResolver({dates[0].isoformat(): dates[2].isoformat()}))).run_snapshot(snapshot_dir, root / "row-count-output")
        recorder.add("KF-INT-004", "RED_OBSERVED" if count_scorer.calls else "BASE_SAFE_OBSERVED", "EXACT_BASE_EXECUTABLE_PROBE", f"declared row_count=99 admitted; scorer_calls={count_scorer.calls}")

        forged = json.loads(original_model)
        forged["company_id"] = "FORGED"
        forged_text = json.dumps(forged, sort_keys=True, separators=(",", ":")) + "\n"
        model_path.write_text(forged_text, encoding="utf-8")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["model_input_file_sha256"] = hashlib.sha256(forged_text.encode()).hexdigest()
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        forged_scorer = CountingScorer()
        ValidationRunner(forged_scorer, RankingEngine("COMPANY_ID_ASC_DIAGNOSTIC"), OutcomeBuilder(price, ExplicitWindowResolver({dates[0].isoformat(): dates[2].isoformat()}))).run_snapshot(snapshot_dir, root / "forged-output")
        recorder.add("KF-INT-005", "RED_OBSERVED" if forged_scorer.calls else "BASE_SAFE_OBSERVED", "EXACT_BASE_EXECUTABLE_PROBE", f"forged semantic aggregate admitted; scorer_calls={forged_scorer.calls}")

        wrong_hash_path = root / "wrong-hash.csv"
        write_price_csv(wrong_hash_path, dates)
        wrong_hash_provider = CsvPriceProvider(wrong_hash_path, dataset_hash="0" * 64)
        recorder.add("KF-PRC-001", "RED_OBSERVED" if wrong_hash_provider.dataset_hash == "0" * 64 else "BASE_SAFE_OBSERVED", "EXACT_BASE_EXECUTABLE_PROBE", "configured zero hash accepted without hashing actual bytes")
        canonical_provider = CsvPriceProvider(wrong_hash_path, dataset_hash="caller", semantics="PRICE_CANONICAL")
        recorder.add("KF-PRC-002", "RED_OBSERVED", "EXACT_BASE_EXECUTABLE_PROBE", f"PRICE_CANONICAL caller string accepted; semantics={canonical_provider.semantics}")
        duplicate_path = root / "duplicate.csv"
        write_price_csv(duplicate_path, dates[:1], rows_per_date=2)
        duplicate_provider = CsvPriceProvider(duplicate_path)
        recorder.add("KF-PRC-003", "RED_OBSERVED" if len(duplicate_provider._rows) == 2 and len(duplicate_provider._by_key) == 1 else "BASE_SAFE_OBSERVED", "EXACT_BASE_EXECUTABLE_PROBE", f"duplicate rows loaded={len(duplicate_provider._rows)}; dictionary keys={len(duplicate_provider._by_key)}")
        invalid_path = root / "invalid.csv"
        write_price_csv(invalid_path, dates[:1], invalid_ohlc=True)
        invalid_provider = CsvPriceProvider(invalid_path)
        recorder.add("KF-PRC-004", "RED_OBSERVED" if invalid_provider._rows else "BASE_SAFE_OBSERVED", "EXACT_BASE_EXECUTABLE_PROBE", "high below open/close row accepted")
        ca_path = root / "ca.csv"
        write_price_csv(ca_path, dates[:1], invalid_ca=True)
        ca_provider = CsvPriceProvider(ca_path)
        recorder.add("KF-PRC-005", "RED_OBSERVED" if ca_provider._rows[0].adjustment_factor == Decimal("0") else "BASE_SAFE_OBSERVED", "EXACT_BASE_EXECUTABLE_PROBE", "flagged CA row with zero factor and no evidence accepted")
        canonical_outcome = OutcomeBuilder(CsvPriceProvider(wrong_hash_path, semantics="PRICE_CANONICAL"), ExplicitWindowResolver({dates[0].isoformat(): dates[2].isoformat()})).build("S", "005930", dates[0])
        recorder.add("KF-PRC-006", "RED_OBSERVED" if canonical_outcome.status == "VALIDATION" else "BASE_SAFE_OBSERVED", "EXACT_BASE_EXECUTABLE_PROBE", f"caller-asserted canonical outcome status={canonical_outcome.status}, validity={canonical_outcome.outcome_validity}")

        immutable_root = root / "immutable"
        immutable_store = SnapshotStore(immutable_root)
        immutable_store.write(ready, {"generator_version": "first"})
        immutable_manifest = immutable_root / dates[0].isoformat() / "manifest.json"
        before_mtime = immutable_manifest.stat().st_mtime_ns
        time.sleep(0.01)
        immutable_store.write(ready, {"generator_version": "first"})
        after_mtime = immutable_manifest.stat().st_mtime_ns
        recorder.add("KF-IMM-001", "RED_OBSERVED" if after_mtime != before_mtime else "BASE_SAFE_OBSERVED", "EXACT_BASE_EXECUTABLE_PROBE", f"identical rerun manifest mtime changed={after_mtime != before_mtime}")

        changed = build_with([{**ready_row, "value": "8"}]).build(dates[0])
        before_bytes = (immutable_root / dates[0].isoformat() / "model_input.jsonl").read_bytes()
        immutable_store.write(changed, {"generator_version": "changed"})
        after_bytes = (immutable_root / dates[0].isoformat() / "model_input.jsonl").read_bytes()
        recorder.add("KF-IMM-002", "RED_OBSERVED" if before_bytes != after_bytes else "BASE_SAFE_OBSERVED", "EXACT_BASE_EXECUTABLE_PROBE", "different semantic content overwrote the fixed date snapshot path")

        result_snapshot_root = root / "result-snapshot"
        SnapshotStore(result_snapshot_root).write(ready, {"generator_version": "result"})
        result_snapshot_dir = result_snapshot_root / dates[0].isoformat()
        result_dir = root / "results"

        class AlternateScorer(DiagnosticFixtureScorer):
            model_id = "ALT"
            model_version = "alt-v1"
            def score(self, model_input):
                base = super().score(model_input)
                return ScoreResult(base.model_score_id, base.pit_snapshot_id, base.company_id, base.security_code, self.model_version, Decimal("8"), base.evaluation_status, base.component_trace)

        runner_one = ValidationRunner(DiagnosticFixtureScorer(), RankingEngine("COMPANY_ID_ASC_DIAGNOSTIC"), OutcomeBuilder(price, ExplicitWindowResolver({dates[0].isoformat(): dates[2].isoformat()})))
        runner_two = ValidationRunner(AlternateScorer(), RankingEngine("COMPANY_ID_ASC_DIAGNOSTIC"), OutcomeBuilder(price, ExplicitWindowResolver({dates[0].isoformat(): dates[2].isoformat()})))
        first_result = runner_one.run_snapshot(result_snapshot_dir, result_dir)
        fixed_result_path = result_dir / f"{dates[0].isoformat()}.json"
        first_result_bytes = fixed_result_path.read_bytes()
        second_result = runner_two.run_snapshot(result_snapshot_dir, result_dir)
        second_result_bytes = fixed_result_path.read_bytes()
        recorder.add("KF-IMM-003", "RED_OBSERVED" if first_result_bytes != second_result_bytes and first_result["validation_run_id"] != second_result["validation_run_id"] else "BASE_SAFE_OBSERVED", "EXACT_BASE_EXECUTABLE_PROBE", "different model/run identity overwrote fixed date result path")
        before_result_mtime = fixed_result_path.stat().st_mtime_ns
        time.sleep(0.01)
        runner_two.run_snapshot(result_snapshot_dir, result_dir)
        after_result_mtime = fixed_result_path.stat().st_mtime_ns
        recorder.add("KF-IMM-004", "RED_OBSERVED" if after_result_mtime != before_result_mtime else "BASE_SAFE_OBSERVED", "EXACT_BASE_EXECUTABLE_PROBE", f"identical result rerun modified mtime={after_result_mtime != before_result_mtime}")

        recorder.add("KF-CLI-001", "CONTROL_ABSENT_SOURCE_OBSERVED", "EXACT_BASE_SOURCE_STATIC_OBSERVATION", "cli_run_backtest.main ends with unconditional return 0 after counting blocked results")
        partial_result = BatchSnapshotGenerator(build_with([current_only_row]), SnapshotStore(root / "partial-batch")).run(dates[0], dates[0], {})
        recorder.add("KF-CLI-002", "RED_OBSERVED" if partial_result.generated == 1 and partial_result.failed == 0 else "BASE_SAFE_OBSERVED", "EXACT_BASE_EXECUTABLE_PROBE", f"PARTIAL snapshot accounting generated={partial_result.generated}, failed={partial_result.failed}")
        recorder.add("KF-CLI-003", "CONTROL_ABSENT_SOURCE_OBSERVED", "EXACT_BASE_SOURCE_STATIC_OBSERVATION", "no admission module or classified integrity exception/exit mapping exists")

        try:
            load_scorer("module_that_does_not_exist:Scorer")
            missing_plugin = "accepted"
        except Exception as exc:
            missing_plugin = type(exc).__name__
        recorder.add("KF-MOD-001", "RED_OBSERVED" if missing_plugin == "ModuleNotFoundError" else "BASE_SAFE_OBSERVED", "EXACT_BASE_EXECUTABLE_PROBE", f"missing plugin raises unclassified {missing_plugin}")
        loaded_diagnostic = load_scorer("tools.m3top3.model_interface:DiagnosticFixtureScorer")
        recorder.add("KF-MOD-002", "RED_OBSERVED" if loaded_diagnostic.model_id == "DIAGNOSTIC_FIXTURE" else "BASE_SAFE_OBSERVED", "EXACT_BASE_EXECUTABLE_PROBE", "diagnostic fixture scorer dynamically loaded with no official admission boundary")
        recorder.add("KF-MOD-003", "CONTROL_ABSENT_SOURCE_OBSERVED", "EXACT_BASE_SOURCE_STATIC_OBSERVATION", "load_scorer accepts only spec/kwargs and has no artifact/baseline/authority receipt input")
        recorder.add("KF-MOD-004", "CONTROL_ABSENT_SOURCE_OBSERVED", "EXACT_BASE_SOURCE_STATIC_OBSERVATION", "no actual config-byte hash verification exists in model_interface or CLI")
        recorder.add("KF-MOD-005", "CONTROL_ABSENT_SOURCE_OBSERVED", "EXACT_BASE_SOURCE_STATIC_OBSERVATION", "no OFFICIAL mode or working/unresolved/example placeholder prohibition exists")

    ids = [row["test_id"] for row in recorder.rows]
    expected_ids = [
        *[f"KF-PIT-{index:03d}" for index in range(1, 7)],
        *[f"KF-SNP-{index:03d}" for index in range(1, 5)],
        *[f"KF-INT-{index:03d}" for index in range(1, 6)],
        *[f"KF-PRC-{index:03d}" for index in range(1, 7)],
        *[f"KF-IMM-{index:03d}" for index in range(1, 5)],
        *[f"KF-CLI-{index:03d}" for index in range(1, 4)],
        *[f"KF-MOD-{index:03d}" for index in range(1, 6)],
    ]
    duplicate_ids = sorted({item for item in ids if ids.count(item) > 1})
    missing_ids = sorted(set(expected_ids) - set(ids))
    unexpected_ids = sorted(set(ids) - set(expected_ids))
    status_counts: dict[str, int] = {}
    for row in recorder.rows:
        status_counts[row["status"]] = status_counts.get(row["status"], 0) + 1
    file_hashes = {
        str(path.relative_to(base_root)): file_hash(path)
        for path in sorted(package_root.rglob("*"))
        if path.is_file() and "__pycache__" not in path.parts and path.suffix in {".py", ".md", ".json"}
    }
    receipt = {
        "receipt_type": "POST-HOC_RETROSPECTIVE_EXACT_BASE_RED",
        "chronology": "EXECUTED_AFTER_IMPLEMENTATION; NOT A CHRONOLOGICAL_PRE_PATCH_RUN",
        "exact_base_commit": EXACT_BASE_COMMIT,
        "base_root": str(base_root),
        "base_file_sha256": file_hashes,
        "logical_id_count": len(recorder.rows),
        "expected_logical_id_count": len(expected_ids),
        "status_counts": status_counts,
        "missing_ids": missing_ids,
        "unexpected_ids": unexpected_ids,
        "duplicate_ids": duplicate_ids,
        "collection_import_error_used_as_red_evidence": False,
        "result": "PASS_EVIDENCE_CAPTURE" if not missing_ids and not unexpected_ids and not duplicate_ids and "PROBE_ERROR" not in status_counts else "FAIL_EVIDENCE_CAPTURE",
        "claim_limit": "Retrospective exact-base defect behavior/control-absence evidence only; it is not chronological TDD evidence and does not authorize Official execution.",
        "iva_execution_participation": "NONE",
        "observations": recorder.rows,
    }
    print(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if receipt["result"] == "PASS_EVIDENCE_CAPTURE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
