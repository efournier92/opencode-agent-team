# Multi-Agent Operating System For OpenCode

## Purpose

- A suite of agents and skills built for [OpenCode](https://opencode.ai/) TUI.

## Features

- Centralized model-tier config for frequent provider swapping in ever-changing world in which we're living
  - *See `models.yaml`.*

## Installation

### Overview

- See [`INSTALL.md`](INSTALL.md) for step-by-step instructions, meant for an agent to execute.
- **Supports:**
  - Global install *(recommended for personal use)*.
  - Per-project install *(team-shared, in a repo).*

### Quick Global Install

```bash
mkdir -p ~/.config/opencode/agents ~/.config/opencode/skills
cp -n agents/*.md ~/.config/opencode/agents/
cp -Rn skills/* ~/.config/opencode/skills/
cp -n AGENTS.md ~/.config/opencode/AGENTS.md
# merge opencode.json.sample into ~/.config/opencode/opencode.json or opencode.jsonc
```

### Verify

1. **Run `/agents` in the OpenCode TUI**
    - Expect all many agents available *(`chief`, `builder`, `critic`, etc).*
2. The `skill` tool description should list all 10 skills *(`specify`, `implement`, etc).*

## Contents

### `AGENTS.md`

- Shared rulebook *(operating loop, delegation contract, shell discipline, roster)*.
- Install to either:
  - `~/.config/opencode/AGENTS.md` *(global)*.
  - `<project-root>/AGENTS.md` *(per-project)*.

### `INSTALL.md`

- Agent-oriented install guide for global and per-project setups.

### `models.yaml`

- Single source of truth for model tiers and agent-to-tier mapping.
  - *Supports (`top`, `mid`, `low`).*

### `scripts/apply-models.py`

- Regenerates agent frontmatter and `opencode.json.sample` from `models.yaml`.

### `opencode.json.sample`

- Sample global config: `chief` as default agent, default model, `scout` pinned to the low tier, etc.

### `agents/`

- All agent files *(markdown + YAML frontmatter)*.

| Agent | Mode | Tier | Description |
|---|---|---|---|
| `chief` | primary | top | Operator agent that decides, decomposes, routes work to specialists, verifies output, and writes handoffs. |
| `builder` | subagent | mid | Bounded implementation worker for a well-specified task with a clear done-check. |
| `qa` | subagent | mid | PASS/FAIL verification agent that proves claims by executing commands; read-only on code. |
| `critic` | subagent | mid | Red-team reviewer that attacks handoffs, plans, diffs, and claims for fake progress before they are trusted. |
| `system-fixer` | subagent | mid | Repairs the agent system itself (configs, hooks, instruction docs) and runs improvement mode for recurring failures. |
| `context-curator` | subagent | mid | Hygiene agent for instruction docs, memory index, and handoffs; keeps context lean and claims true. |
| `scout` | subagent | low | Low-tier external-research agent for docs, versions, APIs, and changelogs outside the codebase. |
| `investigator` | subagent | low | Low-tier read-only in-repo code locator that finds where symbols are defined and what calls them, with compressed deterministic output. |
| `compliance-officer` | subagent | mid | Pre-filters specs, branches, and PRs for regulatory/legal/fiduciary/privacy questions worth a human compliance officer's time. |
| `product-manager` | subagent | mid | Harsh product/UX critique of specs, branches, and PRs from the user's perspective. |
| `photo-generator` | subagent | mid | Local AI photo-generation specialist: sets up a ComfyUI/SDXL rig, downloads models, produces identity-consistent artistic images via scripted runners. |

*Mode and tier are shipped defaults. Model IDs are user-configurable via `models.yaml` (see Model Tiers).*

### `skills/` (10 skills)

- 1 directory per skill, each with with a `SKILL.md` inside.

| Skill | Description |
|---|---|
| `specify` | Turn a rough design sketch into an implementation-ready spec document. |
| `implement` | Build exactly what a finished design spec says and iterate to a green test suite. |
| `commit` | Organize already-completed work into logical commits: stages chunks and suggests messages, never commits. |
| `handoff` | Write a structured session handoff so a fresh session resumes without re-exploring. |
| `browser-verify` | Prove a feature works end-to-end in a real browser against the local dev stack only. |
| `ship-check` | Run a parallel pre-ship quality gate on a feature branch with read-only reviewers. |
| `worktree` | Create, list, or remove grouped git worktrees across repos, each with isolated ports and its own database. |
| `terse` | Toggle terse, high-signal output: cut filler while keeping technical facts exact. |
| `minimalist` | Force the laziest, minimal solution that works: cut over-engineering, reuse existing code, ship the smallest diff. |
| `ui-craft` | Sleek, distinctive frontend design guidance: typography, palette, layout, and anti-AI-slop checks. |

## Model Tiers

### Configure

All model assignments driven by `models.yaml`:

```yaml
tiers:
  # Claude (shipped default)
  top:   anthropic/claude-opus-5
  mid:   anthropic/claude-sonnet-5
  low:   anthropic/claude-haiku-4-5

  # OpenAI (GPT-5.6 family, 2026-08):
  # top:   openai/gpt-5.6-sol
  # mid:   openai/gpt-5.6-terra
  # low:   openai/gpt-5.6-luna

  # DeepSeek (V4; deepseek-chat/deepseek-reasoner retired 2026-07-24):
  # top:   deepseek/deepseek-v4-pro    # thinking mode on
  # mid:   deepseek/deepseek-v4-pro
  # low:   deepseek/deepseek-v4-flash

agent_tiers:
  chief: top
  builder: mid
  scout: low
  ...
```

*Shipped default is Claude; commented OpenAI and DeepSeek alternatives live in `models.yaml`.*

### Update

To change model IDs, or move an agent between tiers, edit `models.yaml` and run:

```bash
python3 scripts/apply-models.py
```

