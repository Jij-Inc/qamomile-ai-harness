# arXiv 2606.19502v1: QAOA MaxCut Entanglement Scaling

## Metadata

- Title: "Entanglement Scaling and Problem Structure in Quantum Approximate and Adiabatic Optimization Algorithms"
- Authors: Georgios Arapantonis, Paraj Titum, Gregory Quiroz
- arXiv: 2606.19502v1 `[quant-ph]`
- Local paper text: `references/arxiv/2026-05-19_to_2026-06-19/2606.19502v1.txt`
- Local paper PDF: `references/arxiv/2026-05-19_to_2026-06-19/2606.19502v1.pdf`
- Local Qamomile references read: `skills/qamomile_qcoder/SKILL.md`, `prompts/offline_qamomile_agent.md`, `references/qamomile/docs/en/algorithm/qaoa_maxcut.py`, `references/qamomile/docs/en/integration/ommx_quantum_benchmarks_qaoa.py`, `references/qamomile/docs/en/tutorial/02_parameterized_kernels.py`, `references/qamomile/docs/en/tutorial/06_execution_models.py`, `references/qamomile/docs/en/tutorial/09_hermitian_decomposition.py`.

## Paper Summary

The paper studies noiseless QAOA and adiabatic quantum computation for weighted MaxCut, focusing on how bipartite von Neumann entanglement depends on training quality and graph structure. For a graph \(G=(V,E)\), the paper uses the Ising cost Hamiltonian

\[
H_C = \sum_{(i,j)\in E} w_{ij} Z_i Z_j
\]

and the canonical QAOA ansatz

\[
|\psi_p(\vec\beta,\vec\gamma)\rangle =
\prod_{j=1}^p e^{-i\beta_j H_M} e^{-i\gamma_j H_C} |+\rangle^{\otimes N},
\quad H_M=\sum_i X_i.
\]

The main practical finding is that entanglement profiles are optimizer-sensitive. Randomly initialized training can hide the entanglement peak in dense complete-graph instances, while an informed initialization routine plus L-BFGS-B reveals a peak near shallow depths and continued improvement in approximation ratio. The paper's training strategy combines exhaustive/grid initialization for \(p=1,2\), then chooses between INTERP and bilinear initialization for \(p \ge 3\), with bounds \(\beta_j \in [-\pi/4,\pi/4]\), \(\gamma_j \in [0,2\pi)\), `maxiter=3000`, and `ftol=1e-6`.

For entanglement, the paper evaluates layerwise entropy \(S^p_\ell(N_1;N)\), the within-depth maximum \(S^p(N_1;N)=\max_{\ell \le p} S^p_\ell(N_1;N)\), and required entanglement \(S^{req}(N_1;N)=\max_{p \le p_{max}} S^p(N_1;N)\), with \(p_{max}=10\). Across graph families, balanced-partition required entanglement scales approximately linearly with system size. In dense regimes, normalized required entanglement is well modeled as a function of edge density \(\alpha=2|E|/(N(N-1))\), and the unbalanced-bipartition profile collapses onto a curve consistent with fermionic Gaussian state entanglement up to a scaling factor.

## Qamomile Implementation Plan

Implement a small MaxCut QAOA kernel as a state-preparation kernel plus two wrappers:

1. Build an Ising coefficient dictionary from a small weighted graph, using only \(Z_iZ_j\) quadratic terms for MaxCut. Keep a `linear` dictionary for compatibility with the existing Qamomile QAOA pattern, but leave it empty unless testing a spin-glass variant.
2. Build a `qamomile.observable.Hamiltonian` for optimization with `qmc.expval`, using one `PauliOperator(Pauli.Z, i)` per linear term and two per quadratic term.
3. Define `superposition`, `cost_layer`, `mixer_layer`, and `qaoa_state` as `@qmc.qkernel` functions.
4. Define `qaoa_expval(...) -> qmc.Float` for the optimizer and `qaoa_sampling(...) -> qmc.Vector[qmc.Bit]` for final bitstring counts.
5. Transpile once with structure bound: `p`, `quad`, `linear`, `n`, and `H`; keep `gammas` and `betas` as runtime parameters.
6. For a compact offline demo, use small \(N\) and shallow \(p\), run exact expectation values with `run()`, and optionally sample final bitstrings with `sample()`.

This reproduces the paper's QAOA circuit form, but not the full entanglement-scaling experiment. Full reproduction would need statevector access after each intermediate layer, entropy calculation across sampled bipartitions, ensembles of KR/CW/ED graphs, and the paper's depth-progressive optimizer.

## Exact Qamomile Code Patterns

Use Qamomile circuit APIs, not direct Qiskit kernels:

```python
import qamomile.circuit as qmc
import qamomile.observable as qmo
from qamomile.qiskit import QiskitTranspiler


def maxcut_hamiltonian(n, quad):
    H = qmo.Hamiltonian(num_qubits=n)
    for (i, j), wij in quad.items():
        H.add_term(
            (qmo.PauliOperator(qmo.Pauli.Z, i), qmo.PauliOperator(qmo.Pauli.Z, j)),
            wij,
        )
    return H
```

Use affine qubit reassignment and `qmc.range()`:

```python
@qmc.qkernel
def superposition(n: qmc.UInt) -> qmc.Vector[qmc.Qubit]:
    q = qmc.qubit_array(n, name="q")
    for i in qmc.range(n):
        q[i] = qmc.h(q[i])
    return q
```

Use `rzz` for \(Z_iZ_j\) cost terms and `rx(2.0 * beta)` for the mixer:

```python
@qmc.qkernel
def cost_layer(
    quad: qmc.Dict[qmc.Tuple[qmc.UInt, qmc.UInt], qmc.Float],
    linear: qmc.Dict[qmc.UInt, qmc.Float],
    q: qmc.Vector[qmc.Qubit],
    gamma: qmc.Float,
) -> qmc.Vector[qmc.Qubit]:
    for (i, j), Jij in quad.items():
        q[i], q[j] = qmc.rzz(q[i], q[j], angle=Jij * gamma)
    for i, hi in linear.items():
        q[i] = qmc.rz(q[i], angle=hi * gamma)
    return q


@qmc.qkernel
def mixer_layer(q: qmc.Vector[qmc.Qubit], beta: qmc.Float) -> qmc.Vector[qmc.Qubit]:
    n = q.shape[0]
    for i in qmc.range(n):
        q[i] = qmc.rx(q[i], angle=2.0 * beta)
    return q
```

Compose a reusable state kernel, then wrap for expectation or sampling:

```python
@qmc.qkernel
def qaoa_state(
    p: qmc.UInt,
    quad: qmc.Dict[qmc.Tuple[qmc.UInt, qmc.UInt], qmc.Float],
    linear: qmc.Dict[qmc.UInt, qmc.Float],
    n: qmc.UInt,
    gammas: qmc.Vector[qmc.Float],
    betas: qmc.Vector[qmc.Float],
) -> qmc.Vector[qmc.Qubit]:
    q = superposition(n)
    for layer in qmc.range(p):
        q = cost_layer(quad, linear, q, gammas[layer])
        q = mixer_layer(q, betas[layer])
    return q


@qmc.qkernel
def qaoa_expval(
    p: qmc.UInt,
    quad: qmc.Dict[qmc.Tuple[qmc.UInt, qmc.UInt], qmc.Float],
    linear: qmc.Dict[qmc.UInt, qmc.Float],
    n: qmc.UInt,
    gammas: qmc.Vector[qmc.Float],
    betas: qmc.Vector[qmc.Float],
    H: qmc.Observable,
) -> qmc.Float:
    q = qaoa_state(p, quad, linear, n, gammas, betas)
    return qmc.expval(q, H)


@qmc.qkernel
def qaoa_sampling(
    p: qmc.UInt,
    quad: qmc.Dict[qmc.Tuple[qmc.UInt, qmc.UInt], qmc.Float],
    linear: qmc.Dict[qmc.UInt, qmc.Float],
    n: qmc.UInt,
    gammas: qmc.Vector[qmc.Float],
    betas: qmc.Vector[qmc.Float],
) -> qmc.Vector[qmc.Bit]:
    q = qaoa_state(p, quad, linear, n, gammas, betas)
    return qmc.measure(q)
```

Bind structure at transpile time and sweep angles at runtime:

```python
transpiler = QiskitTranspiler()
exe = transpiler.transpile(
    qaoa_expval,
    bindings={"p": p, "quad": quad, "linear": {}, "n": n, "H": H},
    parameters=["gammas", "betas"],
)
energy = exe.run(
    transpiler.executor(),
    bindings={"gammas": gammas, "betas": betas},
).result()
```

## Limitations

- The paper's MaxCut Hamiltonian omits the usual constant and sign conventions used when directly maximizing cut value. For QAOA training, this is acceptable if the objective and interpretation are kept consistent; for reporting cut values, convert sampled bitstrings back to the classical MaxCut score.
- Qamomile's `RZZ(theta)` convention includes a \(1/2\) in the exponent. The local Qamomile tutorial passes `Jij * gamma`, allowing the optimizer to absorb the factor; use `2.0 * Jij * gamma` only when exact physical time evolution under \(H_C\) is required.
- The small kernel does not compute entanglement. Entanglement scaling requires intermediate statevectors for every layer and depth, reduced-density-matrix entropy, and averaging over sampled bipartitions.
- The paper's optimizer is more elaborate than a minimal SciPy loop. Random initial angles are useful for smoke tests but are specifically warned against for interpreting entanglement profiles on dense graphs.
- Full reproduction is expensive: the paper uses ensembles of 150 graphs, \(8 \le N \le 16\), \(p_{max}=10\), weighted complete graphs, \(k\)-regular graphs, and arbitrary-edge-density graphs.

## Offline-Agent Hints

- Follow the offline Qamomile prompt: define real `.py` qkernels, import `qamomile.circuit as qmc`, annotate with Qamomile types, use `qmc.qubit_array`, and always reassign consumed qubit handles.
- Use `qmc.range()` for symbolic loops. Do not iterate directly over a `Vector[Qubit]`.
- Use `qmc.expval` plus `run()` for optimizer objective values; use `qmc.measure` plus `sample()` only for final bitstring distributions.
- Keep Qiskit usage behind Qamomile's transpiler/executor. Do not write direct Qiskit circuits when the target is a Qamomile implementation.
- For QCoder-style harness tasks, return unmeasured qubits for state-preparation kernels; for this QAOA workflow, keep both unmeasured `qaoa_state` and measured/expval wrappers.
