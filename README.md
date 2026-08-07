# Multi-Agent System — OpenCode Plugin

OpenCode-native port of the domain-agnostic multi-agent plugin. Contains agents,
skills, the shared rulebook (`AGENTS.md`), and a centralized model-tier config
(`models.yaml`).

## What is inside

- `AGENTS.md` — shared rulebook (operating loop, delegation contract, shell discipline, roster). Install at `~/.config/opencode/AGENTS.md` (global) or `<project-root>/AGENTS.md` (per-project) so OpenCode loads it.
- `models.yaml` — single source of truth for model tiers (`top`, `mid`, `cheap`) and agent-to-tier mapping.
- `scripts/apply-models.py` — regenerates agent frontmatter and `opencode.json.sample` from `models.yaml`.
- `INSTALL.md` — install guide for global and per-project setups.
- `opencode.json.sample` — sample global config: `chief` as default agent, default model, `research-scout` pinned to the cheap model.
- `agents/` — 10 agent files (markdown + YAML frontmatter).
  - `chief` (primary/operator)
  - `builder`, `qa-engineer`, `adversarial-critic`, `system-fixer`, `context-librarian`, `research-scout`, `investigator`, `compliance-officer`, `product-manager` (subagents)
- `skills/` — 11 skills, one folder per skill with a `SKILL.md` inside.
  - `specifier`, `implementer`, `committer`, `handoff`, `qa`, `ship-check`, `worktree`, `autofill-generation`, `caveman`, `ponytail`, `frontend-design`

## Install

See [`INSTALL.md`](INSTALL.md) for step-by-step instructions. Global install (recommended for personal use) or per-project (team-shared in a repo). The sample config in `opencode.json.sample` makes `chief` the default agent and sets the model tiers from `models.yaml`.

Quick global install:

```bash
mkdir -p ~/.config/opencode/agents ~/.config/opencode/skills
cp -n agents/*.md ~/.config/opencode/agents/
cp -Rn skills/* ~/.config/opencode/skills/
cp -n AGENTS.md ~/.config/opencode/AGENTS.md
# merge opencode.json.sample into ~/.config/opencode/opencode.json or opencode.jsonc
```

## Verify the install

After copying:

1. Run `/agents` in the OpenCode TUI — expect all 10 agents (`chief`, `builder`, `qa-engineer`, `adversarial-critic`, `system-fixer`, `context-librarian`, `research-scout`, `investigator`, `compliance-officer`, `product-manager`).
2. The `skill` tool description should list all 11 skills (`specifier`, `implementer`, `committer`, `handoff`, `qa`, `ship-check`, `worktree`, `autofill-generation`, `caveman`, `ponytail`, `frontend-design`).

## Model configuration

All model assignments driven by `models.yaml`:

```yaml
tiers:
  top:   deepseek/deepseek-reasoner
  mid:   deepseek/deepseek-v4-pro
  cheap: deepseek/deepseek-v4-flash

agent_tiers:
  chief: top
  adversarial-critic: mid
  system-fixer: mid
  product-manager: mid
  builder: mid
  qa-engineer: mid
  compliance-officer: mid
  context-librarian: mid
  research-scout: cheap
```

To change model IDs or move an agent between tiers, edit `models.yaml` and run:

Prerequisite: Python 3 with PyYAML installed (`pip install pyyaml`).

```bash
python3 scripts/apply-models.py
```

That regenerates the `model:` lines in every agent frontmatter and updates `opencode.json.sample` so the whole plugin stays consistent from a single source of truth.

## Notes

- `AGENTS.md` is the single shared rulebook, placed in the plugin tree so it travels with the plugin when copied.
- Skills are instruction files loaded via the `skill` tool. Skills that "drive agents" (e.g. `specifier`, `implementer`, `ship-check`, `qa`) instruct the loading agent to dispatch subagents via the `task` tool; the skill itself does not spawn agents directly.
- No references to the old Claude plugin paths remain in this tree.
