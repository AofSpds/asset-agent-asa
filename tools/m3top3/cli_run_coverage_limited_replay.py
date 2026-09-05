from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from .core import atomic_write_json, atomic_write_text, sha256_hex
from .coverage_limited_replay_v1 import (
    execute_model_stage,
    finalize_without_scored_rows,
    load_population_bytes,
    parse_population_bytes,
    scorecard_markdown,
    selection_ledger_jsonl,
)


PRICE_BINDINGS = {
    "2024": {
        "name": "marcap-2024.parquet",
        "bytes": 24_572_111,
        "sha256": "b0c38943e67637d5faf88429880092cf0f46a394be39860dd3bcd0b04231bccb",
    },
    "2025": {
        "name": "marcap-2025.parquet",
        "bytes": 25_153_419,
        "sha256": "2bfd93c217eb74263bc5020b23fa6debb6b02531c11eaccc2826639bc191559e",
    },
    "2026": {
        "name": "marcap-2026.parquet",
        "bytes": 16_198_533,
        "sha256": "5da710a2fc56f8fe9b1f5126295cc30c3b15c0ee35d28ba808a505ec4a2243c1",
    },
}
PRICE_DATASET_IDENTITY = "419893f0dc8c08019a746182135630cc5f94d6e7ebc2874d5bd23cb54c0a72f7"
MODEL_COMPONENTS = (
    "tools/m3top3/__init__.py",
    "tools/m3top3/cli_run_coverage_limited_replay.py",
    "tools/m3top3/contracts_v1.py",
    "tools/m3top3/core.py",
    "tools/m3top3/features_v1.py",
    "tools/m3top3/features_v1_narrow_patch.py",
    "tools/m3top3/pit_guard.py",
    "tools/m3top3/runtime_v1.py",
    "tools/m3top3/scorer_v1.py",
    "tools/m3top3/shared_interface_guards_v1.py",
    "tools/m3top3/window_mapping_v11.py",
    "tools/m3top3/configs/m3top3_v1.0.json",
    "tools/m3top3/coverage_limited_replay_v1.py",
)


def _hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _bind_code(repo: Path) -> tuple[str, list[dict[str, object]]]:
    components = []
    for relative in MODEL_COMPONENTS:
        path = repo / relative
        components.append(
            {
                "path": relative,
                "bytes": path.stat().st_size,
                "sha256": _hash_file(path),
            }
        )
    identity = "M3TOP3-EXECUTABLE-BUNDLE-SHA256:" + sha256_hex(components)
    return identity, components


def _assert_clean_repo(repo: Path) -> None:
    status = subprocess.check_output(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=repo,
        text=True,
    )
    if status:
        raise ValueError("replay requires a clean worktree so bound Git and executable bytes cannot diverge")


def _bind_prices(paths: dict[str, Path]) -> dict[str, object]:
    components = []
    for year in sorted(PRICE_BINDINGS):
        expected = PRICE_BINDINGS[year]
        path = paths[year]
        observed = {"bytes": path.stat().st_size, "sha256": _hash_file(path)}
        if observed["bytes"] != expected["bytes"] or observed["sha256"] != expected["sha256"]:
            raise ValueError(f"{year} price component identity mismatch: {observed}")
        components.append({"year": year, "path": str(path), **expected})
    return {
        "binding_state": "EXACT_COMPONENT_IDENTITIES_VERIFIED_AFTER_MODEL_STAGE",
        "dataset_identity_sha256": PRICE_DATASET_IDENTITY,
        "source_semantics": "RAW_IMMUTABLE_NOT_PRICE_CANONICAL",
        "components": components,
        "future_value_columns_loaded": False,
        "outcome_values_loaded": False,
        "reason_outcome_values_not_loaded": "ZERO_MODEL_SCORED_SELECTIONS",
        "known_bounded_ca_note": (
            "KRX:183300/W8 has a source-verified material split and suspension; if a score is later "
            "available, result measurement must remain excluded until a comparable post-relisting price is bound."
        ),
    }


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the first coverage-limited M3Top3 replay")
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--pmo-run-id", required=True)
    parser.add_argument("--price-2024", type=Path, required=True)
    parser.add_argument("--price-2025", type=Path, required=True)
    parser.add_argument("--price-2026", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    effective_argv = sys.argv[1:] if argv is None else argv
    args = _parse_args(effective_argv)
    repo = args.repo.resolve()
    output_dir = args.output_dir.resolve()
    started_at = datetime.now(ZoneInfo("Asia/Seoul")).isoformat()
    _assert_clean_repo(repo)
    code_identity, code_components = _bind_code(repo)
    population = parse_population_bytes(load_population_bytes(repo))

    # Scientific firewall: the complete eight snapshot batches are scored before
    # even hashing the supplied future price files. No outcome value column is loaded.
    model_stage = execute_model_stage(
        population,
        pmo_run_id=args.pmo_run_id,
        code_identity=code_identity,
        config_path=repo / "tools/m3top3/configs/m3top3_v1.0.json",
    )
    price_manifest = _bind_prices(
        {"2024": args.price_2024.resolve(), "2025": args.price_2025.resolve(), "2026": args.price_2026.resolve()}
    )
    scorecard = finalize_without_scored_rows(model_stage)
    scorecard["price_input_binding"] = price_manifest
    scorecard["calendar_binding"] = {
        "identity": "REPLAY_ONLY_PRICE_DATE_X_OFFICIAL_KRX_CLOSURE_BINDING-v1",
        "window_registry_revision": "e59ed048d6da76edcad82c9a58b0d083c6452471",
        "window_registry_blob": "033817e6335865e411d2bb4b5837434167091458",
        "window_registry_csv_sha256": "96d63cc98a01b6332cf9486440e7f3fdaa0ec5a2d605f21bc14a4025b46e69fe",
        "observed_price_date_count": 637,
        "reconciliation_state": "EXACT_PRICE_DATE_SET_EQUALS_WEEKDAYS_MINUS_BOUND_OFFICIAL_CLOSURES",
        "authority_ceiling": "APPROVED_REPLAY_ONLY_NOT_PRODUCTION_CALENDAR_RELEASE",
        "closure_components": [
            {"year": 2024, "git_blob": "98c93ecb5dafe38723ee06fb07cbd80c7c8a2a4d", "sha256": "d5961ae5998036cc1710fe28e22d324db0233b570dd5c417b088fba1408f857f"},
            {"year": 2025, "git_blob": "583c4c6dc374408bca2c8a8eadbd9ee168468210", "sha256": "c90dcd0f9fd59498f239bbed32f63a300d64f25f9e03020f26a15c40cf017fa8"},
            {"year": 2026, "git_blob": "92c3815e6b8b5383620ec916716e777b51fdd142", "sha256": "89ccce131de8d0c4baa6a30d62b7d2e8e3bdc872c71a21d7d81d4b667330d384"},
        ],
    }
    finished_at = datetime.now(ZoneInfo("Asia/Seoul")).isoformat()
    execution_manifest = {
        "pmo_run_id": args.pmo_run_id,
        "started_at_kst": started_at,
        "finished_at_kst": finished_at,
        "execution_environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "repo": str(repo),
            "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip(),
            "git_branch": subprocess.check_output(["git", "branch", "--show-current"], cwd=repo, text=True).strip(),
        },
        "execution_argv": [
            sys.executable,
            "-m",
            "tools.m3top3.cli_run_coverage_limited_replay",
            *effective_argv,
        ],
        "model_code_identity": code_identity,
        "model_code_components": code_components,
        "runner": {
            "path": "tools/m3top3/cli_run_coverage_limited_replay.py",
            "sha256": _hash_file(Path(__file__)),
        },
        "stage_sequence": scorecard["stage_sequence"],
        "status": "COMPLETED",
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    atomic_write_json(output_dir / "REPLAY_RUN_MANIFEST.json", execution_manifest)
    atomic_write_json(output_dir / "PRICE_CALENDAR_INPUT_CUSTODY.json", {
        "price": price_manifest,
        "calendar": scorecard["calendar_binding"],
    })
    atomic_write_json(output_dir / "FIRST_COVERAGE_LIMITED_SCORECARD.json", {
        key: value for key, value in scorecard.items() if key != "selection_ledger"
    })
    atomic_write_text(
        output_dir / "MODEL_SELECTION_LEDGER.jsonl",
        selection_ledger_jsonl(scorecard["selection_ledger"]),
    )
    atomic_write_text(output_dir / "FIRST_COVERAGE_LIMITED_SCORECARD.md", scorecard_markdown(scorecard))
    print(json.dumps({
        "status": scorecard["scorecard_state"],
        "pmo_run_id": args.pmo_run_id,
        "totals": scorecard["totals"],
        "output_dir": str(output_dir),
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
