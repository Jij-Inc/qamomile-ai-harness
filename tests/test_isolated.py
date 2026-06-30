from pathlib import Path

from qamomile_ai_harness.isolated import evaluate_paths_isolated
from qamomile_ai_harness.models import StatusCode


def test_isolated_reference_solution_is_accepted() -> None:
    result = evaluate_paths_isolated(
        Path("benchmarks/cases/QPC001_A1.json"),
        Path("tests/fixtures/solutions/QPC001_A1.py"),
        timeout_seconds=10.0,
    )

    assert result.status == StatusCode.AC, result.message
    assert result.state_match
