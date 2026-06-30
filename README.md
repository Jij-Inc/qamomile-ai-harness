# Qamomile AI Harness

AI harness, benchmark utilities, and agent skills for developing quantum
algorithm code with [Qamomile](https://github.com/Jij-Inc/Qamomile).

The project started as a no-web QCoder benchmark harness, but it is not limited
to offline use. It supports local QCoder-style evaluation, no-web agent prompts,
Codex/Claude skill packaging, and paper-derived Qamomile implementation notes.

## What Is Included

- A small local QCoder-style evaluator for Qamomile `@qmc.qkernel` solutions.
- Static checks for common AI-generated Qamomile mistakes.
- Fixture benchmark cases and reference solutions for smoke testing.
- Reusable no-web prompts and skills for coding agents.
- Codex and Claude Code plugin packages for the same Qamomile/QCoder skill.
- Notes from selected quantum-algorithm papers, distilled into Qamomile-focused
  implementation guidance.

This repository does not vendor the full QCoder dataset, Qamomile source tree,
arXiv PDFs, agent run logs, or local Python environment. Those are local working
inputs and are intentionally ignored.

## Quick Start

Install dependencies with `uv`, then run the local fixture benchmark:

```bash
UV_CACHE_DIR=.uv-cache uv sync
UV_CACHE_DIR=.uv-cache uv run pytest -q
UV_CACHE_DIR=.uv-cache uv run qcoder-batch tests/fixtures/solutions
```

The fixture benchmark currently covers three small state-preparation cases:

- `QPC001_A1`: prepare `|+>`.
- `QPC001_A2`: prepare a uniform superposition.
- `QPC001_A3`: prepare a Bell state.

Evaluate one solution file:

```bash
UV_CACHE_DIR=.uv-cache uv run qcoder-eval benchmarks/cases/QPC001_A3.json tests/fixtures/solutions/QPC001_A3.py
```

Run static checks over candidate solutions:

```bash
UV_CACHE_DIR=.uv-cache uv run qcoder-check tests/fixtures/solutions
```

## Benchmark Data

The committed `benchmarks/cases/` directory contains small local cases that are
safe to run without external services. If you have a QCoder Benchmark JSONL
export, place it at:

```text
data/raw/qcoder_benchmark/QCoder_Benchmark.jsonl
```

Then generate local summaries:

```bash
UV_CACHE_DIR=.uv-cache uv run qcoder-prepare
```

The public QCoder benchmark also has a web/API evaluation path. This harness is
designed so local simulator checks and agent iteration can be used alongside
external evaluation workflows when those are available.

## Agent Skills

The main skill lives at:

```text
skills/qamomile_qcoder/SKILL.md
```

Use it when an agent needs to write, debug, or review Qamomile kernels for
QCoder-style tasks. The skill is especially useful in restricted environments
where the agent can read local files but cannot browse the web. In connected
workflows, the same rules still help keep Qamomile code idiomatic and easy to
evaluate.

The no-web prompt template is:

```text
prompts/offline_qamomile_agent.md
```

Paper-derived implementation notes are under:

```text
docs/arxiv_papers/
```

See `docs/project_structure.md` and `skills/qamomile_qcoder/SKILL.md`.

## Repository Contents

This repository intentionally commits only the harness, small fixture cases,
skills, plugin packages, and derived notes. Large or externally sourced local
working data is excluded by `.gitignore`, including:

```text
.venv/
.uv-cache/
agent_runs/
data/
references/
```

To give agents local Qamomile documentation context, clone or export Qamomile
documentation/source under `references/qamomile/`. That local reference copy is
useful for development, but it is not part of the public release artifact.

## Agent Plugin Distribution

The Qamomile/QCoder skill is packaged for both Codex and Claude Code under:

```text
plugins/codex/qamomile-qcoder/
plugins/claude/qamomile-qcoder/
```

Marketplace catalogs:

```text
.agents/plugins/marketplace.json
.claude-plugin/marketplace.json
```

See `docs/plugin_distribution.md` for install and release notes.

Codex install from a cloned repo:

```bash
codex plugin marketplace add /path/to/qamomile-ai-harness
codex plugin add qamomile-qcoder@qamomile-ai-harness
```

Claude Code install from a cloned repo:

```bash
claude plugin marketplace add /path/to/qamomile-ai-harness
claude plugin install qamomile-qcoder@qamomile-ai-harness
```

## Development Checks

Before publishing changes, run:

```bash
UV_CACHE_DIR=.uv-cache uv run pytest -q
UV_CACHE_DIR=.uv-cache uv run qcoder-batch tests/fixtures/solutions
python3 ~/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/codex/qamomile-qcoder
claude plugin validate plugins/claude/qamomile-qcoder
claude plugin validate .
```

Qamomile is still evolving, so benchmark failures can come from the candidate
solution, the harness, or Qamomile itself. When a Qamomile behavior looks
surprising, reduce it to a small local reproduction before deciding whether to
work around it in the skill or report/fix it upstream.
