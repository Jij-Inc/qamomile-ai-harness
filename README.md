# Qamomile AI Harness

Offline AI harness for solving small QCoder-style quantum programming tasks with Qamomile.

```bash
UV_CACHE_DIR=.uv-cache uv sync
UV_CACHE_DIR=.uv-cache uv run qcoder-prepare
UV_CACHE_DIR=.uv-cache uv run qcoder-batch tests/fixtures/solutions
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

To regenerate local benchmark summaries, place the QCoder JSONL export at
`data/raw/qcoder_benchmark/QCoder_Benchmark.jsonl` and run `qcoder-prepare`.
To give agents local Qamomile documentation context, clone or export the
Qamomile documentation under `references/qamomile/`.

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
codex plugin marketplace add /path/to/qamomile_ai_harness
codex plugin add qamomile-qcoder@qamomile-ai-harness
```

Claude Code install from a cloned repo:

```bash
claude plugin marketplace add /path/to/qamomile_ai_harness
claude plugin install qamomile-qcoder@qamomile-ai-harness
```
