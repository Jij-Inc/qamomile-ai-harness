from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from qamomile_ai_harness.cases import iter_cases, load_case
from qamomile_ai_harness.dataset import summarize_dataset
from qamomile_ai_harness.evaluator import evaluate_paths, evaluate_solution
from qamomile_ai_harness.isolated import evaluate_paths_isolated
from qamomile_ai_harness.static_check import check_paths

console = Console()


def _prepare_command(
    raw_path: Path = Path("data/raw/qcoder_benchmark/QCoder_Benchmark.jsonl"),
    output_dir: Path = Path("data/processed/qcoder_benchmark"),
) -> None:
    """Summarize the downloaded QCoder Benchmark JSONL."""
    summary = summarize_dataset(raw_path, output_dir)
    console.print(f"Wrote summary for {summary['row_count']} submissions across {summary['problem_count']} problems.")


def _evaluate_command(
    case_path: Path = typer.Argument(..., help="Path to a local benchmark case JSON."),
    solution_path: Path = typer.Argument(..., help="Path to a Python file defining qamomile @qmc.qkernel solve."),
    json_output: bool = typer.Option(False, "--json", help="Print machine-readable JSON."),
    in_process: bool = typer.Option(False, "--in-process", help="Evaluate in this Python process instead of an isolated worker."),
    timeout_seconds: float = typer.Option(30.0, "--timeout", help="Timeout for isolated worker execution."),
) -> None:
    """Evaluate one Qamomile solution against one local case."""
    result = (
        evaluate_paths(case_path, solution_path)
        if in_process
        else evaluate_paths_isolated(case_path, solution_path, timeout_seconds=timeout_seconds)
    )
    if json_output:
        console.print(json.dumps(result.model_dump(mode="json"), ensure_ascii=False, indent=2))
    else:
        console.print(f"{result.case_id}: {result.status} - {result.message}")


def _batch_command(
    solution_dir: Path = typer.Argument(..., help="Directory containing <case-id>.py solutions."),
    case_dir: Path = Path("benchmarks/cases"),
    json_output: bool = typer.Option(False, "--json", help="Print machine-readable JSON."),
    in_process: bool = typer.Option(False, "--in-process", help="Evaluate in this Python process instead of isolated workers."),
    timeout_seconds: float = typer.Option(30.0, "--timeout", help="Timeout for each isolated worker execution."),
) -> None:
    """Evaluate all local cases against matching solution files."""
    results = []
    for case_path in iter_cases(case_dir):
        case = load_case(case_path)
        solution_path = solution_dir / f"{case.id}.py"
        if in_process:
            results.append(evaluate_solution(case, solution_path))
        else:
            results.append(evaluate_paths_isolated(case_path, solution_path, timeout_seconds=timeout_seconds))

    if json_output:
        console.print(json.dumps([r.model_dump(mode="json") for r in results], ensure_ascii=False, indent=2))
        return

    table = Table(title="Qamomile QCoder Local Benchmark")
    table.add_column("Case")
    table.add_column("Status")
    table.add_column("Fidelity")
    table.add_column("Depth")
    table.add_column("Message")
    for result in results:
        table.add_row(
            result.case_id,
            result.status,
            "" if result.fidelity is None else f"{result.fidelity:.12f}",
            "" if result.depth is None else str(result.depth),
            result.message,
        )
    console.print(table)


def _check_command(
    paths: list[Path] = typer.Argument(..., help="Python files or directories to statically check."),
    json_output: bool = typer.Option(False, "--json", help="Print machine-readable JSON."),
) -> None:
    """Statically check Qamomile solution files for common AI mistakes."""
    findings = check_paths(paths)
    if json_output:
        console.print(json.dumps([finding.__dict__ for finding in findings], ensure_ascii=False, indent=2))
        raise typer.Exit(1 if any(f.severity == "error" for f in findings) else 0)

    if not findings:
        console.print("No findings.")
        return

    table = Table(title="Qamomile Static Check")
    table.add_column("Severity")
    table.add_column("Code")
    table.add_column("File")
    table.add_column("Line")
    table.add_column("Message")
    for finding in findings:
        table.add_row(
            finding.severity,
            finding.code,
            finding.path,
            str(finding.line),
            finding.message,
        )
    console.print(table)
    raise typer.Exit(1 if any(f.severity == "error" for f in findings) else 0)


def prepare() -> None:
    typer.run(_prepare_command)


def evaluate() -> None:
    typer.run(_evaluate_command)


def batch() -> None:
    typer.run(_batch_command)


def check() -> None:
    typer.run(_check_command)
