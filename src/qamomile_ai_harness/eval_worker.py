from __future__ import annotations

import json
import sys
import traceback
from pathlib import Path

from qamomile_ai_harness.evaluator import evaluate_paths


def main() -> int:
    case_path = Path(sys.argv[1])
    solution_path = Path(sys.argv[2])
    try:
        result = evaluate_paths(case_path, solution_path)
        payload = {"ok": True, "result": result.model_dump(mode="json")}
    except BaseException as exc:  # noqa: BLE001 - worker must report every candidate failure
        payload = {
            "ok": False,
            "error_type": type(exc).__name__,
            "error": str(exc),
            "traceback": traceback.format_exc()[-4000:],
        }
    print("__QAMOMILE_HARNESS_RESULT__" + json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
