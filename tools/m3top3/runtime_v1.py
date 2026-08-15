from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

from .core import hash_file
from .scorer_v1 import M3Top3V1Engine

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent / "configs" / "m3top3_v1.0.json"


def load_config(path: str | Path = DEFAULT_CONFIG_PATH) -> tuple[dict[str, Any], str]:
    p = Path(path)
    config = json.loads(p.read_text(encoding="utf-8"))
    return config, hash_file(p)


def build_engine(code_identity: str, config_path: str | Path = DEFAULT_CONFIG_PATH) -> M3Top3V1Engine:
    config, config_sha256 = load_config(config_path)
    return M3Top3V1Engine(config=config, code_identity=code_identity, config_sha256=config_sha256)


def score_snapshot_records(records: Iterable[dict[str, Any]], code_identity: str, config_path: str | Path = DEFAULT_CONFIG_PATH) -> dict[str, Any]:
    return build_engine(code_identity=code_identity, config_path=config_path).score_snapshot(records)
