# Recent Quantum Algorithm Papers for Qamomile Skills

Date window: 2026-05-19 through 2026-06-19.

Candidate metadata was collected from arXiv API into:

- `references/arxiv/2026-05-19_to_2026-06-19/candidates.json`
- `references/arxiv/2026-05-19_to_2026-06-19/candidates.md`

Selected papers:

1. `2606.19502v1` - Entanglement Scaling and Problem Structure in Quantum Approximate and Adiabatic Optimization Algorithms.
   - Why: gives a clean MaxCut QAOA form with cost/mixer Hamiltonians that maps naturally to Qamomile parameterized kernels.
2. `2606.20238v1` - Random Projections for Multi-Copy Quantum Algorithms.
   - Why: gives an explicit random-projection protocol and generalized swap-test structure that can be prototyped as small Qamomile circuit blocks.
3. `2606.20184v1` - Operator Learning for efficient Quantum Computation.
   - Why: gives a hardware-aware variational operator-learning and one-ancilla block-encoding framework; good for Qamomile ansatz-generation skills.

Not selected for this first skill update:

- `2606.20504v1` focuses on multi-qutrit systems. Qamomile is currently qubit-oriented in this harness.
- `2606.19457v1` is interesting for CAS wavefunction state preparation, but its full method needs chemistry-specific encodings and MPS/QPT machinery beyond a compact offline skill.
- `2606.19083v1` is compelling for MPO block-encoding compilers, but the tensor-network compiler layer should be a later, dedicated extension.
