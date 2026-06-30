# Plugin Distribution

This repo can be distributed as both a Codex plugin marketplace and a Claude Code plugin marketplace.

## Canonical Plugin

The shared skill is packaged through two platform-specific plugin wrappers:

```text
plugins/codex/qamomile-qcoder/
plugins/claude/qamomile-qcoder/
```

Each wrapper contains only the manifest that its host expects:

```text
plugins/codex/qamomile-qcoder/.codex-plugin/plugin.json
plugins/claude/qamomile-qcoder/.claude-plugin/plugin.json
plugins/*/qamomile-qcoder/skills/qamomile-qcoder/SKILL.md
```

Do not put both `.codex-plugin` and `.claude-plugin` manifests in the same plugin root. Claude Code
component discovery can report duplicate components when the Codex manifest is present in the same
root. The older top-level `skills/qamomile_qcoder/` folder is retained for direct local harness use.

## Codex

Codex marketplace catalog:

```text
.agents/plugins/marketplace.json
```

Install from a cloned repo:

```bash
codex plugin marketplace add /path/to/qamomile_ai_harness
codex plugin add qamomile-qcoder@qamomile-ai-harness
```

For the default personal marketplace flow, copy or scaffold this plugin under `~/plugins` and use
`~/.agents/plugins/marketplace.json` instead.

## Claude Code

Claude Code marketplace catalog:

```text
.claude-plugin/marketplace.json
```

Install from a cloned repo:

```bash
claude plugin marketplace add /path/to/qamomile_ai_harness
claude plugin install qamomile-qcoder@qamomile-ai-harness
```

The marketplace file follows the local Claude Code plugin layout: repo root
`.claude-plugin/marketplace.json`, plugin root `.claude-plugin/plugin.json`, and default component
discovery under `skills/` and `commands/`.

## Public Release Checklist

- Replace placeholder repository/homepage metadata in plugin manifests once the public GitHub URL exists.
- Keep generated caches, raw datasets, external clones, and agent run traces out of the release.
- Run `UV_CACHE_DIR=.uv-cache uv run pytest -q`.
- Run `python3 /Users/yuyamashiro/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/codex/qamomile-qcoder` for Codex manifest validation.
- Run `claude plugin validate plugins/claude/qamomile-qcoder`.
- Run `claude plugin validate .`.
- JSON-parse both marketplace files and both plugin manifests.
