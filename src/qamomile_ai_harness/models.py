from __future__ import annotations

from enum import StrEnum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class StatusCode(StrEnum):
    AC = "AC"
    RE = "RE"
    TLE = "TLE"
    UGE = "UGE"
    DLE = "DLE"
    WA = "WA"


class ComplexAmplitude(BaseModel):
    index: int
    real: float = 0.0
    imag: float = 0.0


class CaseInput(BaseModel):
    bindings: dict[str, Any] = Field(default_factory=dict)
    target_state: list[ComplexAmplitude]


class BenchmarkCase(BaseModel):
    id: str
    title: str
    source_problem: str
    problem_statement: str
    qamomile_template: str
    inputs: list[CaseInput]
    allowed_gates: list[str] = Field(default_factory=list)
    max_depth: int | None = None
    ignore_global_phase: bool = True
    fidelity_threshold: float = 1.0 - 1e-9


class EvaluationResult(BaseModel):
    case_id: str
    solution_path: Path
    status: StatusCode
    runtime_error: bool = False
    gate_violation: bool = False
    depth_violation: bool = False
    state_match: bool = False
    fidelity: float | None = None
    used_gates: list[str] = Field(default_factory=list)
    depth: int | None = None
    message: str = ""
