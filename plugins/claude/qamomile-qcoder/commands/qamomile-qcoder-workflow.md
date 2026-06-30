---
name: qamomile-qcoder-workflow
description: Work on an offline Qamomile/QCoder benchmark or paper-demo task
---

# Qamomile QCoder Command

Use the bundled `qamomile-qcoder` skill.

Process:

1. Read the target case, solution, or paper note from the local filesystem.
2. Write or repair Qamomile `@qmc.qkernel` code without web access.
3. Run static checks with `UV_CACHE_DIR=.uv-cache uv run qcoder-check`.
4. Run local benchmark checks with `UV_CACHE_DIR=.uv-cache uv run qcoder-batch` or `qcoder-eval`.
5. Iterate until the local result is accepted or the remaining blocker is explicit.
