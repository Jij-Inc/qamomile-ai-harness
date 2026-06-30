from __future__ import annotations

import json
from pathlib import Path

from qamomile_ai_harness.models import BenchmarkCase


def load_case(path: Path) -> BenchmarkCase:
    return BenchmarkCase.model_validate_json(path.read_text(encoding="utf-8"))


def write_case(case: BenchmarkCase, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(case.model_dump(mode="json"), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def iter_cases(case_dir: Path) -> list[Path]:
    return sorted(case_dir.glob("*.json"))
