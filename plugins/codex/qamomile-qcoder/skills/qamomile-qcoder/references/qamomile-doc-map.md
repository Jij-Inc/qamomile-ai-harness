# Qamomile Documentation Map

Use this map when Qamomile syntax, execution, or algorithm structure is unclear. Prefer the local
files under `references/qamomile/` when working inside this harness; use the online URLs only as
human-facing pointers when web access is allowed.

## Primary Entry Points

- `references/qamomile/README.md`
  - Use for installation, package overview, supported backends, and the high-level workflow.
  - Key quote: `@qkernel define -> draw() / estimate_resources() -> transpile() -> sample() / run() -> .result()`
  - Online: `https://github.com/Jij-Inc/Qamomile`
- `references/qamomile/docs/ja/tutorial/index.md`
  - Use as the tutorial table of contents. It points to tutorials 01-10 and the algorithm section.
  - Online: `https://jij-inc-qamomile.readthedocs-hosted.com/latest/ja/tutorial/`
- `references/qamomile/docs/ja/myst.yml`
  - Use as the docs site map, including API reference locations for `circuit`, `observable`, `qiskit`, and other backends.

## Core Kernel Writing

- First kernel, affine handles, `draw()`, `estimate_resources()`, and execution:
  - `references/qamomile/docs/ja/tutorial/01_your_first_quantum_kernel.py`
  - Key quote: `q = qmc.ry(q, theta)` followed by reassignment is "重要".
- Symbolic sizes, `qmc.UInt`, `qmc.Float`, `qubit_array`, `qmc.range`, and bind/sweep:
  - `references/qamomile/docs/ja/tutorial/02_parameterized_kernels.py`
  - Use this when deciding which values belong in `bindings` versus `parameters`.
  - Key quote: `UInt` controls circuit structure; `Float` is for gate parameters.
- Vector slicing, `VectorView`, slice assignment, and borrow errors:
  - `references/qamomile/docs/ja/tutorial/03_vector_slicing.py`
  - Use this before writing `q[0::2]`, nested slices, or helper calls over slices.
- Controlled gates and controlled sub-kernels:
  - `references/qamomile/docs/ja/tutorial/04_controlled_gates.py`
  - Use this for `qmc.control`, concrete versus symbolic controls, argument order, `power=`, and controlled helper kernels.

## Evaluation And Debugging

- Resource estimation and scaling:
  - `references/qamomile/docs/ja/tutorial/05_resource_estimation.py`
  - Use this for `estimate_resources()`, symbolic `ResourceEstimate`, and `.substitute(...)`.
- `sample()` versus `run()`, observables, `expval`, and bit ordering:
  - `references/qamomile/docs/ja/tutorial/06_execution_models.py`
  - Key quote: Qamomile output uses "ビッグエンディアン" order.
- Classical flow patterns:
  - `references/qamomile/docs/ja/tutorial/07_classical_flow_patterns.py`
  - Use this for loops, sparse data, and branch patterns inside `@qkernel`.
- Reuse patterns:
  - `references/qamomile/docs/ja/tutorial/08_reuse_patterns.py`
  - Use this for helper kernels, `@composite_gate`, and stub/oracle style top-down design.
- Compilation and transpilation internals:
  - `references/qamomile/docs/ja/tutorial/10_compilation_and_transpilation.py`
  - Use this when a kernel fails in tracing, shape resolution, affine validation, partial evaluation, or backend emission.

## Algorithms And Primitives

- Algorithm index:
  - `references/qamomile/docs/ja/algorithm/index.md`
  - Use it to choose examples for QAOA, VQE, Hamiltonian simulation, quantum kernels, QSCI, amplitude encoding, and PCE.
- MaxCut QAOA:
  - `references/qamomile/docs/ja/algorithm/qaoa_maxcut.py`
  - Use this for a complete MaxCut/QAOA pattern and comparison with built-in QAOA helpers.
- Hamiltonian simulation:
  - `references/qamomile/docs/ja/algorithm/hamiltonian_simulation.py`
  - Use this for Suzuki-Trotter patterns and validating against exact statevectors.
- Hermitian decomposition and `pauli_evolve`:
  - `references/qamomile/docs/ja/tutorial/09_hermitian_decomposition.py`
  - Use this for `np.ndarray -> HermitianMatrix -> Hamiltonian -> pauli_evolve -> circuit`.
- Möttönen amplitude encoding:
  - `references/qamomile/docs/ja/algorithm/mottonen_amplitude_encoding.py`
  - Use this for arbitrary state preparation, angle precomputation, and statevector fidelity checks.
- VQE:
  - `references/qamomile/docs/ja/algorithm/vqe_for_hydrogen.py`
  - Use this for `expval`-based objectives, observable conversion, and classical optimizer loops.
- Quantum kernel classification:
  - `references/qamomile/docs/ja/algorithm/quantum_kernel_classification.py`
  - Use this for feature maps, inverse/overlap circuits, and sample-based Gram matrices.

## Known Limitations

- `references/qamomile/LIMITATIONS.md`
  - Use before attempting advanced recursion, shape-dependent QFT/QPE, alias-imported primitives, symbolic slices inside `expval`, or `qmc.inverse` over unresolved control flow.
  - Practical rule: prefer direct `import qamomile.circuit as qmc`, concrete smoke tests, and small statevector checks when using advanced features.
