from pathlib import Path

import pytest

from qamomile_ai_harness.cases import iter_cases, load_case
from qamomile_ai_harness.evaluator import evaluate_solution
from qamomile_ai_harness.models import StatusCode


@pytest.mark.parametrize("case_path", iter_cases(Path("benchmarks/cases")))
def test_reference_solutions_are_accepted(case_path: Path) -> None:
    case = load_case(case_path)
    solution = Path("tests/fixtures/solutions") / f"{case.id}.py"
    result = evaluate_solution(case, solution)
    assert result.status == StatusCode.AC, result.message
    assert result.state_match
