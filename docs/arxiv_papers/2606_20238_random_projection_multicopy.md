# Random Projections for Multi-Copy Quantum Algorithms

## Metadata and Local Sources

- Paper: "Random Projections for Multi-Copy Quantum Algorithms"
- arXiv: 2606.20238v1 `[quant-ph]`
- Authors: Xiaoyu Liu, Jordi Tura, Johannes Knoerzer
- Version date in local text: June 19, 2026; arXiv stamp: June 18, 2026
- Local text: `references/arxiv/2026-05-19_to_2026-06-19/2606.20238v1.txt`
- Local PDF: `references/arxiv/2026-05-19_to_2026-06-19/2606.20238v1.pdf`
- Qamomile references read: `skills/qamomile_qcoder/SKILL.md`, `prompts/offline_qamomile_agent.md`, and tutorial files under `references/qamomile/docs/en/tutorial/`.

## Algorithm 2 Summary

Algorithm 2 estimates moments `{p_k = tr(rho^k)}_{k=2..K}` by replacing a full `n`-qubit, `k`-copy generalized swap test with a randomized projected test on only `q` retained qubits per copy.

For each order `k = 2..K`, sample `NU` random unitaries `U_s` from the Haar ensemble or an approximate design. For each sampled unitary, run `NM` executions: prepare `k` copies of `rho`, apply the same `U_s` to every copy, measure the discarded `n - q` qubits of each copy, and keep the run only when all copies produce the same discarded-register outcome. On success, perform the generalized swap/Hadamard test on the retained `q`-qubit compressed copies and record `Y in {+1, -1}`; on failure record `Y = 0`. With `d = 2^n`, `m = 2^q`, and `L = d / m`, estimate the Haar-averaged projected moment as:

```text
sigma_bar_hat_k^(d,m) = (1 / (L * NU * NM)) * sum_s sum_j Y_s,j^(k)
```

Then reconstruct moments recursively using precomputed relations:

```text
sigma_bar_k^(d,m) = gamma^(k)(d,m) * p_k + F_k(p_1, ..., p_{k-1}),  p_1 = 1
p_hat_k = (sigma_bar_hat_k^(d,m) - F_k(p_hat_1, ..., p_hat_{k-1})) / gamma^(k)(d,m)
```

For `K=2`, purity is recovered directly from the averaged projected moment. For `K=3`, the projected third moment has the hierarchy form `sigma_bar_3 = gamma^(3) p_3 + alpha p_2 + beta`, so the implementation must estimate `p_2` before `p_3`.

## Qamomile Implementation Plan

Use Qamomile for the small coherent circuit fragments: random-unitary ansatz, discarded-qubit measurement, and the compressed generalized swap-test style circuit for `K=2` or `K=3`. Keep the Algorithm 2 loops, equality check of discarded outcomes, `L^-1` normalization, and recursive moment reconstruction in ordinary Python outside the qkernel.

For a small proof of concept, fix `n`, `q`, and `K` at transpile time:

- `K=2`: allocate one ancilla plus two `n`-qubit copies. Apply the same random projection circuit to each copy, measure the first `n - q` qubits of each copy, then run a controlled swap between the retained `q`-qubit suffixes. The ancilla measurement gives `+1` for `0` and `-1` for `1`; the classical driver overwrites the value with `0` unless discarded outcomes match.
- `K=3`: allocate one ancilla plus three `n`-qubit copies. Apply the same random projection circuit to all copies, measure discarded qubits, then apply a controlled cyclic permutation on each retained qubit lane. A 3-cycle can be decomposed as two controlled swaps per retained lane, for example swap copy 1 with copy 2, then copy 0 with copy 1, with the same ancilla as control.
- Random projections: start with a shallow brickwork-style ansatz using `qmc.ry`, `qmc.rz`, and `qmc.cx` with runtime `qmc.Float` angles. Bind structure (`n`, `q`, layer count) at transpile time; sweep random angles per sampled `U_s`.
- Driver shape: run one Qamomile sampling kernel per `(k, U_s)` with `shots=NM`, parse returned bits into discarded-copy registers and ancilla bits, and compute `Y_s,j`.

## Exact Qamomile Code Patterns

Use the affine handle style from the local QCoder prompt:

```python
import qamomile.circuit as qmc


@qmc.qkernel
def projected_swap_k2(
    n: qmc.UInt,
    q_keep: qmc.UInt,
    theta: qmc.Float,
) -> tuple[qmc.Vector[qmc.Bit], qmc.Vector[qmc.Bit], qmc.Bit]:
    anc = qmc.qubit(name="anc")
    a = qmc.qubit_array(n, name="a")
    b = qmc.qubit_array(n, name="b")
    anc = qmc.h(anc)

    for i in qmc.range(n):
        a[i] = qmc.ry(a[i], theta)
        b[i] = qmc.ry(b[i], theta)

    discard = n - q_keep
    ma = qmc.measure(a[0:discard])
    mb = qmc.measure(b[0:discard])

    ccx = qmc.control(qmc.x, num_controls=2)
    for i in qmc.range(discard, n):
        anc, a[i], b[i] = ccx(anc, a[i], b[i])
        anc, b[i], a[i] = ccx(anc, b[i], a[i])
        anc, a[i], b[i] = ccx(anc, a[i], b[i])

    anc = qmc.h(anc)
    return ma, mb, qmc.measure(anc)
```

For `K=3`, reuse the same controlled-swap block twice per retained lane:

```python
ccx = qmc.control(qmc.x, num_controls=2)
for i in qmc.range(discard, n):
    # controlled swap b[i] <-> c[i]
    anc, b[i], c[i] = ccx(anc, b[i], c[i])
    anc, c[i], b[i] = ccx(anc, c[i], b[i])
    anc, b[i], c[i] = ccx(anc, b[i], c[i])
    # controlled swap a[i] <-> b[i], completing a controlled 3-cycle
    anc, a[i], b[i] = ccx(anc, a[i], b[i])
    anc, b[i], a[i] = ccx(anc, b[i], a[i])
    anc, a[i], b[i] = ccx(anc, a[i], b[i])
```

Patterns to preserve:

- Import as `import qamomile.circuit as qmc`; do not write Qiskit circuits inside the solution kernel.
- Decorate kernels with `@qmc.qkernel` and annotate arguments/returns with Qamomile types such as `qmc.UInt`, `qmc.Float`, `qmc.Qubit`, `qmc.Vector[qmc.Qubit]`, and `qmc.Vector[qmc.Bit]`.
- For multi-register sampling output, return a Python tuple of measured values, for example `tuple[qmc.Vector[qmc.Bit], qmc.Vector[qmc.Bit], qmc.Bit]`.
- Allocate registers with `qmc.qubit_array(n, name="...")`.
- Use `qmc.range(...)` for loops over symbolic sizes.
- Reassign every consumed handle: `q[i] = qmc.ry(q[i], theta)` and `q0, q1 = qmc.cx(q0, q1)`.
- Use slices for logical subregisters, for example `a[0:discard]` and `a[discard:n]`; return borrowed slices immediately when a helper kernel consumes them.
- Use `qmc.control(qmc.x, num_controls=2)` for Toffoli-style controlled-X and build controlled swaps from three such calls.
- Bind structure parameters at transpile time and sweep random angles at execution time, following the tutorial bind/sweep pattern.

## Limitations and Offline-Agent Hints

- The Qamomile kernel only produces raw circuit samples. Algorithm 2's postselection, `Y = 0` failed-run convention, `1/L` normalization, and recursive reconstruction should live in the offline Python driver.
- The code above is a template pattern, not a finished benchmark solution. Real random projections need richer random circuits, ideally approximate unitary `K`-designs; a single shared `theta` is only a placeholder.
- For the imaginary part of a general multivariate trace, the paper uses the imaginary-branch generalized swap/Hadamard test. For state moments `tr(rho^K)`, the moment is real, so a real-branch Hadamard test is the natural first target.
- Postselection by equality of discarded outcomes is easier offline than inside Qamomile because comparing `Vector[Bit]` values across registers is classical bookkeeping.
- Keep small first: test `n=2 or 3`, `q=1`, `K=2`; then add `K=3` and verify the recursive use of `p_hat_2`.
- Follow the offline Qamomile agent rules: no web, no Qiskit in qkernel solutions, use local docs, and avoid defining qkernels through `exec` or a REPL string because Qamomile inspects source code.
