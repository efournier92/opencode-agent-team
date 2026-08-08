# Installation Guide

Install this plugin into OpenCode so the multi-agent system is available in every session.

## What gets installed

- **10 agents** in `agents/` → `<config-dir>/agents/`
- **10 skills** in `skills/` → `<config-dir>/skills/`
- **Shared rulebook** `AGENTS.md` → `~/.config/opencode/AGENTS.md` (global) or `<project-root>/AGENTS.md` (per-project)
- **OpenCode config** `opencode.json.sample` → merged into `~/.config/opencode/opencode.json` or `opencode.jsonc`
- **Model tiers** `models.yaml` → `<config-dir>/models.yaml` (copied only if not already present — never overwrites a customized copy on reinstall)

## Prerequisites

- OpenCode installed and able to locate `~/.config/opencode/`.
- Know the install type: **global install** (personal, applies to every workspace) or **per-project install** (team-shared, applies to one repo).

## Global install (recommended)

Makes agents and skills available everywhere OpenCode runs.

1. Open a terminal in this plugin directory.

2. Copy agents and skills:

```bash
mkdir -p ~/.config/opencode/agents
cp -n agents/*.md ~/.config/opencode/agents/

mkdir -p ~/.config/opencode/skills
cp -Rn skills/* ~/.config/opencode/skills/
```

3. Copy the shared rulebook:

```bash
cp -n AGENTS.md ~/.config/opencode/AGENTS.md
```

4. Copy the model-tier mapping (preserved on reinstall), then merge the sample config into your global OpenCode config.

OpenCode reads both `~/.config/opencode/opencode.json` and `~/.config/opencode/opencode.jsonc`. The model-tier mapping is copied only if you don't already have one — reinstalling never overwrites a customized `models.yaml`:

```bash
if [ -f ~/.config/opencode/models.yaml ]; then
  echo "Keeping existing ~/.config/opencode/models.yaml (edit it to change model tiers)."
else
  cp models.yaml ~/.config/opencode/models.yaml
fi
```

If you already have an OpenCode config, add the keys from `opencode.json.sample` into it. If neither config exists, copy the sample directly:

```bash
if [ -f ~/.config/opencode/opencode.jsonc ]; then
  # Manually merge: add model, default_agent, permission, and agent keys
  # from opencode.json.sample into the existing JSONC object.
  echo "Merge opencode.json.sample into ~/.config/opencode/opencode.jsonc"
elif [ -f ~/.config/opencode/opencode.json ]; then
  echo "Merge opencode.json.sample into ~/.config/opencode/opencode.json"
else
  cp opencode.json.sample ~/.config/opencode/opencode.jsonc
fi
```

The sample sets:
- `default_agent`: `chief` — every new session starts as the operator agent.
- `model`: the current `top` tier model from `models.yaml` (used by `chief`).
- `agent.*.model`: per-agent overrides for every agent listed in `models.yaml`'s `agent_tiers`.
- `permission`: `edit`/`bash` ask, `skill` allow.

To change model IDs later, edit the repo's `models.yaml`, run `python3 scripts/apply-models.py` (prerequisite: Python 3 with PyYAML installed — `pip install pyyaml`), then reinstall the regenerated agents and `opencode.json.sample`. Note: `apply-models.py` reads the **repo** copy, not the installed `<config-dir>/models.yaml` — the installed copy is preserved across reinstalls and documents your chosen tiers.

5. Restart OpenCode or reload config.

6. Verify:
   - Run `/agents` in the TUI — expect `chief` (subagents appear via `@` mention or the `task` tool).
   - Check the `skill` tool description — it should list all 10 skills.
   - Start a new session; it should begin as `chief`.

## Per-project install

Use when the plugin should travel with a specific repo.

1. Open a terminal in the project root.

2. Copy agents and skills into `.opencode/`:

```bash
mkdir -p .opencode/agents
cp -n agents/*.md .opencode/agents/

mkdir -p .opencode/skills
cp -Rn skills/* .opencode/skills/
```

3. Copy the shared rulebook to the project root (not inside `.opencode/`):

```bash
cp -n AGENTS.md ./AGENTS.md
```

If the repo already has an `AGENTS.md`, merge this plugin's `AGENTS.md` into it.

4. Optional: copy the model-tier mapping (preserved on reinstall), then copy or merge the sample config:

```bash
mkdir -p .opencode
if [ -f .opencode/models.yaml ]; then
  echo "Keeping existing .opencode/models.yaml (edit it to change model tiers)."
else
  cp models.yaml .opencode/models.yaml
fi
if [ -f .opencode/opencode.jsonc ] || [ -f .opencode/opencode.json ]; then
  echo "Merge opencode.json.sample into the existing project config"
else
  cp -n opencode.json.sample .opencode/opencode.jsonc
fi
```

5. Restart OpenCode or switch into the project directory and reload config.

6. Verify the same way as the global install.

## Mixed installs

Combine global and per-project pieces. Example:
- Keep agents/skills globally in `~/.config/opencode/`.
- Put a project-specific `AGENTS.md` at `<project-root>/AGENTS.md` for repo-specific rules.

OpenCode merges config and rules from all discovered locations; later sources override earlier ones.

## Reinstalling / upgrading

`cp -n` and `cp -Rn` only add files — they never remove renamed or deleted ones. Reinstalling over an older version therefore leaves stale agents/skills behind (e.g. old names like `caveman`, `specifier`, `qa-engineer` alongside their renames `terse`, `specify`, `qa`). Before upgrading, clear the agent/skill dirs and reinstall fresh:

```bash
# global
rm -rf ~/.config/opencode/agents ~/.config/opencode/skills
# then re-run the copy commands from the global install section

# per-project
rm -rf .opencode/agents .opencode/skills
# then re-run the copy commands from the per-project section
```

Your `models.yaml` and `opencode.json`/`opencode.jsonc` are untouched by this.

## Uninstall

Remove the files you copied:

```bash
# global
rm -rf ~/.config/opencode/agents
rm -rf ~/.config/opencode/skills
rm ~/.config/opencode/AGENTS.md
# edit ~/.config/opencode/opencode.jsonc (or opencode.json) to remove the plugin keys

# per-project
rm -rf .opencode/agents
rm -rf .opencode/skills
rm AGENTS.md
# edit .opencode/opencode.jsonc (or opencode.json) to remove the plugin keys
```

## Troubleshooting

- **Agents not listed**: confirm the `.md` files are in a directory OpenCode searches (`~/.config/opencode/agents/` or `.opencode/agents/`) and that YAML frontmatter is valid.
- **Skills not listed**: confirm each skill is in its own folder with a file named exactly `SKILL.md` and that the frontmatter `name` matches the folder name.
- **Chief is not the default**: confirm `default_agent: chief` is set in the active `opencode.json` or `opencode.jsonc`.
- **Model overrides not applied**: confirm the provider prefix in `models.yaml` and the frontmatter `model:` lines match your OpenCode provider (current default is `anthropic/`).
