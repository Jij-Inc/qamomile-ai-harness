# External Harness Learnings

This note records what we learned from the neighboring harness at
`../yu_workspace/projects/qamomile_ai_bench` and how it maps to this project.

## What To Adopt Now

- Run candidate solutions in an isolated subprocess. A benchmark candidate can
  hang, mutate globals, import surprising modules, or leave Qamomile in a bad
  state. The local `qcoder-eval` and `qcoder-batch` commands now use
  `qamomile_ai_harness.isolated.evaluate_paths_isolated` by default and report
  `TLE` for timeouts.
- Keep the verdict ladder simple and QCoder-like: runtime failure, unauthorized
  gate, depth limit, then state fidelity. This keeps agent feedback close to
  what it needs to repair.
- Treat Qamomile skills as part of the benchmark surface. The external harness
  had valuable failure notes that belonged in the agent prompt, not only in
  Python code.

## Agent Mistakes Worth Guarding Against

- Qubit handles are affine. Every Qamomile gate returns fresh handles, including
  multi-qubit gates and controlled gates.
- Qamomile kernels must be defined in real `.py` files because Qamomile inspects
  source text.
- `qmc.range(...)` is required for symbolic `qmc.UInt` loops. Plain Python
  `range(<concrete int>)` can still be useful to force small static unrolling,
  so the static checker warns rather than fails on all Python `range(...)`
  calls inside kernels.
- Do not iterate directly over `Vector[Qubit]`; use index-based updates.
- Keep `bindings` and `parameters` disjoint when using `transpile()`.
  Structure-like values such as sizes and graph data belong in `bindings`;
  sweep values such as QAOA angles belong in `parameters`.
- Qamomile sample tuples and statevector indices follow different conventions:
  sample tuples read naturally as measured bit order, while Qiskit statevector
  basis indices are little-endian. When comparing target states, validate with
  a tiny known circuit.
- Parameterized controlled rotations may expose missing formal parameters such
  as `angle`; smoke-test them and use explicit decompositions when needed.
- For official-style QCoder submissions that must return a Qiskit circuit, a
  practical bridge is to write a classical-output wrapper with measurements,
  call Qamomile `to_circuit()`, then strip final measurements before statevector
  judging. This local harness instead supports quantum-output kernels through a
  lower-level Qamomile build/emit path.
- `qmc.pauli_evolve` observables should span the full register in current
  Qamomile workflows. Pad with identity terms or avoid it for compact
  subregister demos until the upstream behavior is clarified.

## Future Extensions

- Add a richer case schema for `check: statevector | unitary`, `param_sets`,
  qubit limits, and reusable reference artifacts.
- Add a reference builder that derives local `.npz` targets from trusted
  accepted QCoder submissions, then stores provenance next to each case.
- Keep using subprocess workers even for richer checks so no-web subagents can
  safely attempt many flawed solutions.
