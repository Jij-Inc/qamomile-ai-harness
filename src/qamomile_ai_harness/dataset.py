from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


PYTHON_FENCE = re.compile(r"```python\s*(.*?)```|'''python\s*(.*?)'''", re.DOTALL)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def extract_code(markdown: str) -> str:
    matches = PYTHON_FENCE.findall(markdown)
    if not matches:
        return markdown
    last = matches[-1]
    return (last[0] or last[1]).strip()


def summarize_dataset(raw_path: Path, output_dir: Path) -> dict[str, Any]:
    rows = read_jsonl(raw_path)
    by_problem: dict[str, Counter[str]] = defaultdict(Counter)
    first_ac: dict[str, dict[str, Any]] = {}
    for row in rows:
        problem = row["problem"]
        result = row["result"]
        by_problem[problem][result] += 1
        if result == "AC" and problem not in first_ac:
            first_ac[problem] = {
                "user": row["user"],
                "submission_order": row["submission_order"],
                "code": extract_code(row["code"]),
            }

    summary = {
        "row_count": len(rows),
        "problem_count": len(by_problem),
        "problems": {
            problem: {
                "total": sum(counter.values()),
                "results": dict(sorted(counter.items())),
                "has_accepted_submission": problem in first_ac,
            }
            for problem, counter in sorted(by_problem.items())
        },
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (output_dir / "first_accepted.json").write_text(
        json.dumps(first_ac, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return summary
