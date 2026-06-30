# Offline Qamomile QCoder Agent Prompt

You are solving QCoder-style quantum programming tasks with Qamomile. You have no web access. Use only the files provided in this repository.

Return exactly one Python file defining a top-level `solve` decorated with `@qmc.qkernel`. Do not use Qiskit directly in your solution. Do not add markdown fences when writing the final `.py` file.

Important Qamomile rules:

- Import with `import qamomile.circuit as qmc`.
- A quantum kernel is a normal Python function decorated with `@qmc.qkernel`.
- Use Qamomile types in annotations: `qmc.Qubit`, `qmc.Vector[qmc.Qubit]`, `qmc.UInt`, `qmc.Float`.
- Allocate qubits with `qmc.qubit(name="q")` or `qmc.qubit_array(n, name="q")`.
- Qubit handles are affine. After a gate, always reassign the returned handle:
  - `q = qmc.h(q)`
  - `q[0] = qmc.h(q[0])`
  - `q[0], q[1] = qmc.cx(q[0], q[1])`
- For symbolic sizes, use `qmc.range(n)`, not Python `range(n)`.
- For small fixed loops, plain Python `range(<concrete int>)` is allowed when you intentionally want Qamomile to unroll the circuit.
- Do not iterate directly over `Vector[Qubit]`, and do not index Python lists with symbolic Qamomile loop variables.
- Broadcasting is allowed for one-qubit gates: `q = qmc.h(q)` applies H to every qubit in a vector.
- Return unmeasured qubits for state-preparation tasks: `return q`.
- Qamomile kernels must live in `.py` files. They cannot be defined from `exec`, `eval`, or a REPL string because Qamomile inspects source code.
- Qamomile gates are not in-place. Always reassign returned handles, including every qubit touched by multi-qubit or controlled gates.
- Parameterized controlled gates can be tricky. After using `qmc.control(qmc.rx/ry/rz/p)`, run a tiny transpile/sample smoke test with concrete bindings. If Qamomile reports a missing formal binding such as `angle`, avoid that helper or use an explicit decomposition.
- Keep Qamomile `bindings` and `parameters` disjoint: structure goes in `bindings` at transpile time, sweep values go in `parameters` and are passed at `run()`/`sample()` time.
- Be careful with bit order. Sample tuples and statevector basis indices are easy to confuse; verify with a tiny `|01>` or `|10>` circuit before hand-writing target states.
- Avoid `qmc.pauli_evolve` on a partial register unless a local smoke test proves it works; pad observables to the full register or use explicit gates.
- Keep classical work outside `@qmc.qkernel`: optimization loops, postselection, matrix algebra, entropy, and moment reconstruction belong in ordinary Python drivers.
- For state-vector judging, return unmeasured qubits. For sampling/expectation workflows, write separate measured or `qmc.expval` wrapper kernels.

When using recent paper-inspired algorithms, read local notes only:

- `docs/arxiv_papers/README.md`
- `docs/arxiv_papers/2606_19502_qaoa_maxcut.md`
- `docs/arxiv_papers/2606_20238_random_projection_multicopy.md`
- `docs/arxiv_papers/2606_20184_operator_learning.md`

Do not browse. These notes cite local arXiv text/PDF files under `references/arxiv/2026-05-19_to_2026-06-19/`.

Minimal patterns:

```python
import qamomile.circuit as qmc


@qmc.qkernel
def solve() -> qmc.Vector[qmc.Qubit]:
    q = qmc.qubit_array(1, name="q")
    q[0] = qmc.h(q[0])
    return q
```

```python
import qamomile.circuit as qmc


@qmc.qkernel
def solve(n: qmc.UInt) -> qmc.Vector[qmc.Qubit]:
    q = qmc.qubit_array(n, name="q")
    q = qmc.h(q)
    return q
```
