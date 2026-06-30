from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from qamomile_ai_harness.models import EvaluationResult, StatusCode


def evaluate_paths_isolated(
    case_path: Path,
    solution_path: Path,
    timeout_seconds: float = 30.0,
) -> EvaluationResult:
    marker = "__QAMOMILE_HARNESS_RESULT__"
    try:
        proc = subprocess.run(
            [
                sys.executable,
                "-m",
                "qamomile_ai_harness.eval_worker",
                str(case_path),
                str(solution_path),
            ],
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired:
        return EvaluationResult(
            case_id=case_path.stem,
            solution_path=solution_path,
            status=StatusCode.TLE,
            runtime_error=True,
            message=f"execution exceeded {timeout_seconds:.1f}s",
        )

    payload = None
    for line in proc.stdout.splitlines():
        if line.startswith(marker):
            payload = json.loads(line[len(marker):])

    if payload is None:
        detail = (proc.stderr or proc.stdout)[-2000:]
        return EvaluationResult(
            case_id=case_path.stem,
            solution_path=solution_path,
            status=StatusCode.RE,
            runtime_error=True,
            message=f"WorkerCrash: {detail}",
        )

    if not payload.get("ok"):
        return EvaluationResult(
            case_id=case_path.stem,
            solution_path=solution_path,
            status=StatusCode.RE,
            runtime_error=True,
            message=f"{payload.get('error_type')}: {payload.get('error')}",
        )

    return EvaluationResult.model_validate(payload["result"])
