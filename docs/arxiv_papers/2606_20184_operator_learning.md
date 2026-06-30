# arXiv 2606.20184v1: Operator Learning for Efficient Quantum Computation

## Metadata and Local Sources

- Title: "Operator Learning for efficient Quantum Computation"
- Authors: Paul Over, Sergio Bengoechea, Leonardo Borello Busilacchi, Martin Kiffner, Thomas Rung, Alexios A. Michailidis
- arXiv: 2606.20184v1 [quant-ph]
- Dated: June 18, 2026
- Local text: `references/arxiv/2026-05-19_to_2026-06-19/2606.20184v1.txt`
- Local PDF: `references/arxiv/2026-05-19_to_2026-06-19/2606.20184v1.pdf`
- Qamomile references read:
  - `skills/qamomile_qcoder/SKILL.md`
  - `prompts/offline_qamomile_agent.md`
  - `references/qamomile/docs/en/tutorial/01_your_first_quantum_kernel.py`
  - `references/qamomile/docs/en/tutorial/02_parameterized_kernels.py`
  - `references/qamomile/docs/en/tutorial/04_controlled_gates.py`
  - `references/qamomile/docs/en/tutorial/05_resource_estimation.py`
  - `references/qamomile/docs/en/tutorial/08_reuse_patterns.py`
  - `references/qamomile/docs/en/tutorial/09_hermitian_decomposition.py`
  - `references/qamomile/docs/en/tutorial/10_compilation_and_transpilation.py`

## Paper Summary

The paper proposes a full-stack variational quantum circuit synthesis method for learning target operators as compact circuits. The target operator `A` may be unitary, non-unitary, dense, sparse, square, or initially non-square. Non-square operators are zero-padded to square shape; unitary targets are learned directly; non-unitary targets are represented by block encoding.

For a non-unitary operator, the paper uses a single ancilla qubit. With `n_s` system qubits and `n_a = 1`, the learned unitary `G` acts on `n = n_s + n_a` qubits, and the target is recovered from the ancilla-`|0>` block:

```text
E(c, G, A) = A - c Tr_anc[P G]
P = |0><0|_ancilla tensor I_system
```

The objective combines Frobenius reconstruction error, a residual-smoothing regularizer, and a stabilization term for the block-encoding normalization:

```text
J = ||E(c,G,A)||_fro^2 / 2^n_s
    + rho ||R(E(c,G,A))||_fro^2 / 2^n_s
    + mu c^2
```

`R` is a five-point stencil on the residual matrix. Its purpose is not just smaller average error, but fewer localized residual outliers. The paper reports that this is useful for non-unitary engineering operators such as finite-difference Laplace operators and dense airfoil-flow operators.

The ansatz is a product of local trainable gates:

```text
G = product over layers j and gates i of G_ji
```

Each local primitive acts on a chosen qubit subset. That subset encodes hardware assumptions: nearest-neighbor, ladder, 2D layout, long-range gates, or ancilla-centered interactions. Updates are performed on local gate matrices rather than full embedded matrices. After a Euclidean gradient step, each local gate is projected back onto the unitary group by SVD/polar retraction:

```text
G_bar = G - eta dJ/dG
SVD(G_bar) = U^dagger Sigma V
G_next = U^dagger V
```

The hierarchical optimizer trains a prefix of the circuit first: gate by gate within early layers, then all gates in trained layers, and finally the full circuit. This lowers early optimization cost and can reduce sensitivity to local minima or barren plateau behavior. The paper uses L-BFGS for its reported implementation, with ADAM discussed as an option for harder non-convex cases.

## Qamomile Implementation Plan

Qamomile should be used for the circuit surface, resource checks, transpilation, and offline demos after small learned angles or local primitives are known. The dense operator-learning loop itself should remain a classical NumPy/SciPy prototype outside `@qmc.qkernel`, because Qamomile kernels describe circuits with typed affine qubit handles; they are not the right place for SVD, dense matrix contractions, or backpropagation.

Recommended small-scope implementation:

1. Start with two- or three-system-qubit targets only.
2. Prototype the paper's optimizer in ordinary Python:
   - build a target matrix `A`;
   - choose `n_s` and optional `n_a = 1`;
   - maintain local one- and two-qubit unitary primitives or a restricted Euler-angle ansatz;
   - compute the `|0>` ancilla block for non-unitary demos;
   - track `epsilon = ||A - c block(G)||_fro / ||A||_fro`.
3. Convert the learned restricted ansatz into a Qamomile `@qkernel`.
4. Use Qamomile to draw, estimate resources, transpile, and sample or simulate through the local backend.

For a first Qamomile demo, prefer parameterized rotation/CX layers rather than arbitrary learned `SU(4)` matrices. This keeps the code portable through the harness and avoids relying on unavailable custom-unitary support.

## Exact Qamomile Code Patterns

Use the offline Qamomile imports and affine-handle update style:

```python
import qamomile.circuit as qmc


@qmc.qkernel
def ansatz_2q(theta0: qmc.Float, theta1: qmc.Float, theta2: qmc.Float) -> qmc.Vector[qmc.Qubit]:
    q = qmc.qubit_array(2, name="q")
    q[0] = qmc.ry(q[0], theta0)
    q[1] = qmc.ry(q[1], theta1)
    q[0], q[1] = qmc.cx(q[0], q[1])
    q[1] = qmc.rz(q[1], theta2)
    return q
```

For a small one-ancilla block-encoding scaffold, put the ancilla in slot `0` and system qubits after it. Controlled rotations are built with `qmc.control`, with controls passed before targets:

```python
import qamomile.circuit as qmc

cry = qmc.control(qmc.ry)
crz = qmc.control(qmc.rz)


@qmc.qkernel
def one_ancilla_block_demo(alpha: qmc.Float, beta: qmc.Float) -> qmc.Vector[qmc.Qubit]:
    q = qmc.qubit_array(3, name="q")
    anc = 0
    s0 = 1
    s1 = 2

    q[anc] = qmc.h(q[anc])
    q[anc], q[s0] = cry(q[anc], q[s0], angle=alpha)
    q[anc], q[s1] = crz(q[anc], q[s1], angle=beta)
    q[s0], q[s1] = qmc.cx(q[s0], q[s1])
    q[anc] = qmc.h(q[anc])
    return q
```

For symbolic circuit size and layer count, bind `UInt` structure parameters at transpile time and keep rotation angles sweepable:

```python
import qamomile.circuit as qmc


@qmc.qkernel
def lnn_layer(n: qmc.UInt, theta: qmc.Float) -> qmc.Vector[qmc.Qubit]:
    q = qmc.qubit_array(n, name="q")
    q = qmc.ry(q, theta)
    for i in qmc.range(n - 1):
        q[i], q[i + 1] = qmc.cx(q[i], q[i + 1])
    return q
```

Resource and transpilation patterns:

```python
from qamomile.qiskit import QiskitTranspiler

transpiler = QiskitTranspiler()

estimate = lnn_layer.estimate_resources()
concrete = estimate.substitute(n=4)

exe = transpiler.transpile(
    lnn_layer,
    bindings={"n": 4},
    parameters=["theta"],
)
job = exe.sample(
    transpiler.executor(),
    shots=256,
    bindings={"theta": 0.25},
)
result = job.result()
```

For Hermitian unitary targets, Qamomile already has a useful path through Pauli evolution:

```python
import qamomile.circuit as qmc
from qamomile.linalg import HermitianMatrix

H_op = HermitianMatrix(matrix).to_hamiltonian()


@qmc.qkernel
def time_step(n: qmc.UInt, hamiltonian: qmc.Observable, t: qmc.Float) -> qmc.Vector[qmc.Qubit]:
    q = qmc.qubit_array(n, name="q")
    q = qmc.pauli_evolve(q, hamiltonian, t)
    return q
```

This is a baseline for comparing learned compact ansatz circuits against standard Hamiltonian-simulation construction.

## Limitations

- The paper optimizes arbitrary local matrix primitives in `SU(2^r)`. The Qamomile demos above use portable native gates (`ry`, `rz`, `h`, `cx`, controlled rotations), so they demonstrate the workflow but not the full arbitrary-gate optimizer.
- Qamomile's current documented dense-matrix helper is for Hermitian matrices converted to Hamiltonians. Non-Hermitian block encoding should be prototyped manually for now.
- Actual block-encoding validation needs statevector/unitary extraction from the transpiled backend or a separate classical matrix builder; sampling alone only estimates post-selection behavior.
- The paper's full-space method has exponential classical memory/contraction cost. Keep demos tiny unless a tensor-network contraction layer is added later.
- A single ancilla is attractive, but success probability can be small. Track both reconstruction error and `||P G P||_fro^2 / 2^n_s`.

## Offline-Agent Hints

- Do not use web access for this paper task; all cited material is local.
- For QCoder-style outputs, follow `skills/qamomile_qcoder/SKILL.md` and `prompts/offline_qamomile_agent.md`: `import qamomile.circuit as qmc`, define a top-level `@qmc.qkernel`, use Qamomile annotations, use `qmc.qubit_array`, use `qmc.range` for symbolic loops, and reassign every consumed qubit handle.
- Do not write Qiskit circuits directly in solutions. Qiskit belongs only in local evaluation/transpilation code, not in submitted Qamomile kernels.
- If implementing a paper-inspired benchmark, begin with a fixed small ansatz and learned scalar angles. Treat arbitrary `SU(4)` gate learning and SVD projection as a classical helper layer that emits a restricted Qamomile circuit afterward.
