from __future__ import annotations

from pathlib import Path

import numpy as np
from qamomile.qiskit import QiskitTranspiler
from qiskit.quantum_info import Statevector

from qamomile_ai_harness.cases import load_case
from qamomile_ai_harness.models import BenchmarkCase, CaseInput, EvaluationResult, StatusCode
from qamomile_ai_harness.solutions import load_solve


def _target_vector(case_input: CaseInput, num_qubits: int) -> np.ndarray:
    size = 2**num_qubits
    vector = np.zeros(size, dtype=complex)
    for amplitude in case_input.target_state:
        vector[amplitude.index] = complex(amplitude.real, amplitude.imag)
    norm = np.linalg.norm(vector)
    if norm == 0:
        raise ValueError("Target state must contain at least one non-zero amplitude.")
    return vector / norm


def _state_matches(
    actual: np.ndarray,
    expected: np.ndarray,
    ignore_global_phase: bool,
    threshold: float,
) -> tuple[bool, float]:
    if ignore_global_phase:
        fidelity = float(abs(np.vdot(expected, actual)) ** 2)
        return fidelity >= threshold, fidelity
    distance = float(np.linalg.norm(actual - expected))
    fidelity = float(abs(np.vdot(expected, actual)) ** 2)
    return distance <= (1.0 - threshold), fidelity


def _gate_names(circuit) -> list[str]:
    return [instruction.operation.name for instruction in circuit.data]


def _to_circuit_allowing_quantum_outputs(transpiler: QiskitTranspiler, kernel, bindings: dict):
    block = transpiler.to_block(kernel, bindings=bindings)
    substituted = transpiler.substitute(block)
    shape_resolved = transpiler.resolve_parameter_shapes(substituted, bindings)
    affine = transpiler.inline(shape_resolved)
    affine = transpiler.unroll_recursion(affine, bindings)
    validated = transpiler.affine_validate(affine)
    partially_evaluated = transpiler.partial_eval(validated, bindings)
    partially_evaluated = transpiler.slice_borrow_check(partially_evaluated)
    partially_evaluated = transpiler.strip_slice_ops(partially_evaluated)
    separated = transpiler.plan(partially_evaluated)
    executable = transpiler.emit(separated, bindings)
    circuit = executable.get_first_circuit()
    if circuit is None:
        raise ValueError("No quantum circuit was emitted.")
    return circuit


def evaluate_solution(case: BenchmarkCase, solution_path: Path) -> EvaluationResult:
    try:
        solve = load_solve(solution_path)
        transpiler = QiskitTranspiler()
        worst_fidelity: float | None = None
        last_depth: int | None = None
        all_gates: list[str] = []

        for case_input in case.inputs:
            circuit = _to_circuit_allowing_quantum_outputs(transpiler, solve, case_input.bindings)
            gates = _gate_names(circuit)
            all_gates.extend(gates)
            used_gate_set = sorted(set(all_gates))

            if case.allowed_gates:
                unauthorized = sorted(set(gates) - set(case.allowed_gates))
                if unauthorized:
                    return EvaluationResult(
                        case_id=case.id,
                        solution_path=solution_path,
                        status=StatusCode.UGE,
                        gate_violation=True,
                        used_gates=used_gate_set,
                        depth=circuit.depth(),
                        message=f"Unauthorized gates: {', '.join(unauthorized)}",
                    )

            depth = circuit.depth()
            last_depth = depth
            if case.max_depth is not None and depth > case.max_depth:
                return EvaluationResult(
                    case_id=case.id,
                    solution_path=solution_path,
                    status=StatusCode.DLE,
                    depth_violation=True,
                    used_gates=used_gate_set,
                    depth=depth,
                    message=f"Circuit depth {depth} exceeds max_depth {case.max_depth}.",
                )

            actual = np.asarray(Statevector.from_instruction(circuit).data, dtype=complex)
            expected = _target_vector(case_input, circuit.num_qubits)
            ok, fidelity = _state_matches(
                actual,
                expected,
                ignore_global_phase=case.ignore_global_phase,
                threshold=case.fidelity_threshold,
            )
            worst_fidelity = fidelity if worst_fidelity is None else min(worst_fidelity, fidelity)
            if not ok:
                return EvaluationResult(
                    case_id=case.id,
                    solution_path=solution_path,
                    status=StatusCode.WA,
                    state_match=False,
                    fidelity=fidelity,
                    used_gates=used_gate_set,
                    depth=depth,
                    message=f"State fidelity {fidelity:.12f} is below threshold {case.fidelity_threshold:.12f}.",
                )

        return EvaluationResult(
            case_id=case.id,
            solution_path=solution_path,
            status=StatusCode.AC,
            state_match=True,
            fidelity=worst_fidelity,
            used_gates=sorted(set(all_gates)),
            depth=last_depth,
            message="Accepted.",
        )
    except Exception as exc:
        return EvaluationResult(
            case_id=case.id,
            solution_path=solution_path,
            status=StatusCode.RE,
            runtime_error=True,
            message=f"{type(exc).__name__}: {exc}",
        )


def evaluate_paths(case_path: Path, solution_path: Path) -> EvaluationResult:
    return evaluate_solution(load_case(case_path), solution_path)
