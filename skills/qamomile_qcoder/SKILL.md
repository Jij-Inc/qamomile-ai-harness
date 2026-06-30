---
name: qamomile-qcoder
description: This skill should be used when the user asks to solve QCoder-style quantum programming tasks, implement Qamomile kernels, debug Qamomile benchmark failures, run offline Qamomile evaluations, or build paper-derived quantum algorithm demos without web access.
---

# Qamomile QCoder Offline Skill

Use this skill when solving QCoder-style state-preparation or oracle problems with Qamomile under no-web conditions.

## Inputs

- Read the target case JSON under `benchmarks/cases/`.
- The case contains `problem_statement`, `qamomile_template`, `allowed_gates`, optional `max_depth`, and one or more concrete test `bindings`.

## Required Output

Write a Python solution file containing a top-level `solve` function decorated with `@qmc.qkernel`.

Do not write Qiskit code. The harness transpiles Qamomile to Qiskit for evaluation.

## Qamomile Rules

- Use `import qamomile.circuit as qmc`.
- Annotate kernel arguments and returns with Qamomile types.
- Use `qmc.qubit_array(n, name="q")` for registers.
- Reassign every consumed qubit handle.
- For two-qubit gates, reassign both handles.
- Use `qmc.range()` for symbolic `qmc.UInt` loops.
- Use plain Python `range(<concrete int>)` only when intentionally forcing a small static unroll.
- Return qubits, not measurements, for state-vector preparation cases.

## Qamomile Documentation References

When Qamomile details are unclear, read `references/qamomile-doc-map.md` in this skill. It cites
the relevant Qamomile documentation files and explains where to look next.

Fast routing:

- Kernel basics, affine handle reassignment, `draw()`, and `estimate_resources()`: `references/qamomile/docs/ja/tutorial/01_your_first_quantum_kernel.py`.
- Symbolic sizes, `qmc.UInt`, `qmc.Float`, `qmc.range`, and `bindings`/`parameters`: `references/qamomile/docs/ja/tutorial/02_parameterized_kernels.py`.
- Vector slicing and `VectorView`: `references/qamomile/docs/ja/tutorial/03_vector_slicing.py`.
- Controlled gates and controlled helper kernels: `references/qamomile/docs/ja/tutorial/04_controlled_gates.py`.
- `sample()` versus `run()`, `expval`, observables, and bit ordering: `references/qamomile/docs/ja/tutorial/06_execution_models.py`.
- Compiler/transpiler debugging: `references/qamomile/docs/ja/tutorial/10_compilation_and_transpilation.py`.
- Known limitations and sharp edges: `references/qamomile/LIMITATIONS.md`.

## Common AI Mistakes To Avoid

These are the mistakes agents most often make when translating ordinary Qiskit habits into Qamomile.

- Do not define `@qmc.qkernel` functions inside `exec`, `eval`, `python -c`, or a REPL string. Qamomile inspects source code with `inspect.getsource`, so kernels must live in real `.py` files.
- Do not write direct Qiskit code in Qamomile solutions. Qiskit is only for the harness/transpiler layer.
- Do not call Python `range(n)` when `n` is `qmc.UInt`. Use `qmc.range(n)`.
- Do not treat every loop the same: concrete Python loops can be safer than dynamic Qamomile loops for small flat circuits that must become a simple statevector simulation circuit.
- Do not iterate directly over `Vector[Qubit]` with `for qi in q:`. Use index-based updates such as `for i in qmc.range(n): q[i] = qmc.h(q[i])`.
- Do not index Python lists or tuples with symbolic `qmc.UInt` loop variables. Move the classical data lookup outside the kernel or bind a fixed-size structure that Qamomile can trace.
- Keep Qamomile `bindings` and `parameters` disjoint. Bind structure (`n`, graph edges, layer count) during `transpile`; list sweep variables (`theta`, `gammas`, `betas`) in `parameters` and provide their values only at `run()` or `sample()` time.
- Do not assume bit ordering without a smoke test. Qamomile sample tuples and Qiskit statevector basis indices are easy to mix up; validate `|01>`/`|10>` with a tiny circuit before writing target vectors by hand.
- Do not ignore returned handles. Every gate consumes handles and returns fresh ones.
  - Correct: `q[0] = qmc.h(q[0])`
  - Correct: `q[0], q[1] = qmc.cx(q[0], q[1])`
  - Wrong: `qmc.h(q[0])`
  - Wrong: `qmc.cx(q[0], q[1])`
- Do not treat controlled gates as in-place operations. If `cg = qmc.control(qmc.rx)`, then `c, t = cg(c, t, angle=theta)`.
- Be careful with parameterized controlled gates such as `qmc.control(qmc.rx)`, `qmc.control(qmc.ry)`, and `qmc.control(qmc.rz)`. They can leave formal parameter names such as `angle` unbound when reused inside larger parameterized kernels. Always run a tiny Qamomile transpile/sample smoke test. If you see `Missing parameter bindings: ['angle']`, avoid the controlled-rotation helper, bind the reported formal parameter explicitly, or use an explicit decomposition.
- Do not measure state-preparation outputs unless the case asks for samples. Returning measured bits changes the object being judged.
- Do not pass a quantum-output state-preparation kernel directly to Qamomile `transpile()` or `to_circuit()` in custom harness code. Those shortcuts expect classical-I/O entrypoints. For state-vector judging, use the harness evaluator or Qamomile's lower-level build/emit path.
- If a QCoder bridge must return a Qiskit circuit, use a measured classical-output wrapper, call Qamomile `to_circuit()`, and strip final measurements before statevector judging.
- Do not put postselection, recursive moment reconstruction, SVD, dense matrix optimization, or entropy calculations inside `@qmc.qkernel`. Keep classical algorithms in ordinary Python drivers and use Qamomile only for quantum circuit fragments.
- Do not assume Qamomile gate angle conventions are identical to every paper formula. In particular, check `rzz`/controlled-rotation exponent conventions against the local Qamomile docs or validate with a tiny statevector test.
- Do not use `qmc.pauli_evolve` on a subregister-sized observable unless you have validated it locally. In current workflows, pad observables so they span the full qubit register or use explicit gates for compact demos.
- Do not add imports outside the allowed/local stack for benchmark solutions. Prefer `math`, Qamomile, and plain Python unless the harness explicitly allows more.

## Validation Workflow

Use both static and runtime checks. Syntax-only checks are not enough because Qamomile traces kernels at runtime.

For QCoder-style local cases:

```bash
UV_CACHE_DIR=.uv-cache uv run qcoder-check path/to/solutions
UV_CACHE_DIR=.uv-cache uv run qcoder-batch path/to/solutions
```

For paper-inspired demos:

```bash
UV_CACHE_DIR=.uv-cache uv run qcoder-check path/to/demo_files_or_directory
UV_CACHE_DIR=.uv-cache uv run python -m py_compile path/to/demo_files_or_directory/*.py
```

Then run at least one Qamomile `transpile(...).sample(...)` or `transpile(...).run(...)` smoke test with concrete bindings for every exported kernel pattern. This catches missing runtime bindings, unsupported return shapes, controlled-gate parameter leaks, and symbolic-loop mistakes that static checks cannot prove.

## Local Evaluation

Run one case:

```bash
UV_CACHE_DIR=.uv-cache uv run qcoder-eval benchmarks/cases/QPC001_A1.json path/to/solution.py
```

Run a directory of matching `<case-id>.py` files:

```bash
UV_CACHE_DIR=.uv-cache uv run qcoder-batch path/to/solutions
```

Status meanings:

- `AC`: accepted.
- `RE`: Python/Qamomile runtime error.
- `TLE`: isolated worker timed out.
- `UGE`: unauthorized gate.
- `DLE`: depth limit exceeded.
- `WA`: state-vector mismatch.

## Recent arXiv Algorithm Recipes

Use these local notes when a task asks for paper-inspired quantum algorithm implementations. They were prepared from arXiv papers dated 2026-05-19 through 2026-06-19, plus local Qamomile documentation. Do not browse the web; read the local note and cited local paper text/PDF instead.

Index:

- `docs/arxiv_papers/README.md`

### MaxCut QAOA And Entanglement Diagnostics

Paper note:

- `docs/arxiv_papers/2606_19502_qaoa_maxcut.md`
- Source paper text: `references/arxiv/2026-05-19_to_2026-06-19/2606.19502v1.txt`

Use this recipe for small MaxCut QAOA kernels:

- Initialize `|+>^N` with `qmc.h`.
- Use a cost layer for `H_C = sum_(i,j) w_ij Z_i Z_j`.
- Use `qmc.rzz` for `Z_i Z_j` phase terms.
- Use an `X` mixer via `qmc.rx(q[i], angle=2.0 * beta)`.
- Keep `gammas` and `betas` as runtime `qmc.Vector[qmc.Float]` parameters.
- Use an unmeasured `qaoa_state` helper, plus separate `qaoa_expval` and `qaoa_sampling` wrappers.

Important caveat: the paper studies entanglement scaling and training quality, not just the circuit. A compact Qamomile implementation can reproduce the QAOA ansatz; full reproduction also needs statevector access after intermediate layers and classical entropy analysis.

### Random Projection Multi-Copy Protocols

Paper note:

- `docs/arxiv_papers/2606_20238_random_projection_multicopy.md`
- Source paper text: `references/arxiv/2026-05-19_to_2026-06-19/2606.20238v1.txt`

Use this recipe for small projected swap-test circuits:

- Keep Algorithm 2's outer loops, postselection, normalization, and moment reconstruction in ordinary Python.
- Use Qamomile only for coherent fragments: random projection ansatz, measuring discarded qubits, and compressed generalized swap tests.
- Start with `K=2`, `n=2 or 3`, `q_keep=1`.
- Allocate one ancilla plus `K` copies of an `n`-qubit state.
- Apply the same shallow random ansatz to each copy.
- Measure discarded qubits and postselect equality in the Python driver.
- Build controlled swaps from `qmc.control(qmc.x, num_controls=2)`.

Important caveat: Qamomile kernels should return raw samples; the paper's `Y = 0` failed-run convention and recursive moment equations belong outside the kernel.

### Operator Learning And One-Ancilla Block-Encoding Demos

Paper note:

- `docs/arxiv_papers/2606_20184_operator_learning.md`
- Source paper text: `references/arxiv/2026-05-19_to_2026-06-19/2606.20184v1.txt`

Use this recipe for small operator-learning or block-encoding scaffolds:

- Keep dense matrix optimization, SVD/polar projection, and Frobenius-norm objective calculation in ordinary Python.
- Use Qamomile for the learned or restricted ansatz once scalar angles are available.
- For non-unitary demos, use one ancilla qubit in slot `0`; system qubits follow.
- Use native portable gates (`ry`, `rz`, `h`, `cx`, controlled rotations) instead of arbitrary `SU(4)` matrices.
- Prefer controlled rotations only after a smoke test. If controlled `rz`/`ry` leaves a missing `angle` binding, replace it with an explicit supported-gate decomposition or bind the formal `angle` in the driver.
- Track both reconstruction error and block-encoding success probability in the Python driver.

Important caveat: the paper optimizes arbitrary local matrix primitives. The Qamomile recipe is a small demonstrator unless a separate classical compiler emits supported gates.
