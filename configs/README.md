# Vendor Configs

Drop-in `opencode.jsonc` variants for the multi-agent plugin.

Each file is a complete OpenCode config aligned with the project's `opencode.json.sample` roster (14 agents as of 2026-09-08). Swap one in to switch every chat lane to a single provider; swap back to revert.

## Files

| File | Provider focus | Subscription |
|---|---|---|
| `opencode.jsonc.deepseek` | DeepSeek for chat, reasoning, vision, and prose | None (DeepSeek direct API) |
| `opencode.jsonc.minimax` | MiniMax for chat and reasoning | MiniMax Token Plan Plus ($22/mo) |
| `opencode.jsonc.2026-09-mixed` | Snapshot of the prior DeepSeek config (preserved) | None |

Notes per file:

- `opencode.jsonc.deepseek` runs every chat, reasoning, vision, and prose lane on the direct DeepSeek API. The single exception is `photo-generator`: DeepSeek ships zero image-generation models on its direct API, so that lane stays on `google/gemini-3-pro-image`. `visual-critic` and `visual-builder` use `deepseek-v4-flash-vision-exp` (the only DeepSeek vision model; experimental and flash-tier, so visual-critic loses some quality vs the qwen3.8-max baseline). `wordsmith` uses `deepseek-v4-pro`; DeepSeek's prose recommendation is the same chat model with low effort, so `reasoningEffort` here is what the mixed variant had (`high`).
- `opencode.jsonc.minimax` keeps `reasoningEffort` unset because M3 effort-param support is unverified; a 400 would break every call.
- `opencode.jsonc.2026-09-mixed` is a frozen snapshot of the previous DeepSeek variant that mixed providers (`openrouter/qwen3.8-max` for visual-critic, `openrouter/glm-5.3` for wordsmith). Swap back to it if the pure-DeepSeek vision or prose lanes regress unacceptably.

Both active files list the same 14 agents as `../opencode.json.sample`, use direct provider prefixes (`deepseek/`, `minimax/`, plus `google/` for image generation), and are valid `.jsonc` (JSON with comments). Comments at the top of each explain per-lane model choices.

## Prerequisites

Install the plugin itself first. From the repo root:

```bash
mkdir -p ~/.config/opencode/agents ~/.config/opencode/skills
cp -n agents/*.md ~/.config/opencode/agents/
cp -Rn skills/* ~/.config/opencode/skills/
cp -n AGENTS.md ~/.config/opencode/AGENTS.md
```

Then merge `opencode.json.sample` into `~/.config/opencode/opencode.json` or `opencode.jsonc` if you have neither yet:

```bash
cp -n opencode.json.sample ~/.config/opencode/opencode.jsonc
```

Full instructions: `../INSTALL.md`.

## Install a vendor config

All commands assume you are at the repo root. Substitute `$VENDOR` with `deepseek` or `minimax`.

### Global install (recommended)

Backs up the current global config (if any), then copies the vendor config into place.

```bash
if [ -f ~/.config/opencode/opencode.jsonc ]; then
  ts=$(date +%Y-%m-%d_%H%M%S)
  cp ~/.config/opencode/opencode.jsonc ~/.config/opencode/opencode.jsonc.bak-$ts
fi
cp configs/opencode.jsonc.$VENDOR ~/.config/opencode/opencode.jsonc
```

If `~/.config/opencode/opencode.json` exists (instead of the `.jsonc` form), swap that path in the same block:

```bash
if [ -f ~/.config/opencode/opencode.json ]; then
  ts=$(date +%Y-%m-%d_%H%M%S)
  cp ~/.config/opencode/opencode.json ~/.config/opencode/opencode.json.bak-$ts
fi
cp configs/opencode.jsonc.$VENDOR ~/.config/opencode/opencode.json
```

### Per-project install

Puts the vendor config inside the project's `.opencode/` directory so it travels with that repo.

```bash
mkdir -p .opencode
if [ -f .opencode/opencode.jsonc ]; then
  ts=$(date +%Y-%m-%d_%H%M%S)
  cp .opencode/opencode.jsonc .opencode/opencode.jsonc.bak-$ts
fi
cp configs/opencode.jsonc.$VENDOR .opencode/opencode.jsonc
```

## Swap between vendors

Both active files live in the same place, so swapping is the same copy as installing.

```bash
# to DeepSeek (pure)
cp configs/opencode.jsonc.deepseek ~/.config/opencode/opencode.jsonc

# to MiniMax
cp configs/opencode.jsonc.minimax ~/.config/opencode/opencode.jsonc

# to DeepSeek (mixed snapshot, kept for fallback)
cp configs/opencode.jsonc.2026-09-mixed ~/.config/opencode/opencode.jsonc
```

To revert to the shipped sample (one-step undo), copy `opencode.json.sample` back:

```bash
cp opencode.json.sample ~/.config/opencode/opencode.jsonc
```

## Verify

After any swap:

1. Restart OpenCode or reload the config.
2. Run `/agents` in the TUI; expect all 14 agents (`chief`, `builder`, `qa`, `critic`, `system-fixer`, `product-manager`, `compliance-officer`, `context-curator`, `scout`, `investigator`, `wordsmith`, `visual-critic`, `visual-builder`, `photo-generator`).
3. Confirm `default_agent: chief` is still the default.
4. Run `/models` and confirm every `model` value in the swapped config appears in the listed providers; missing IDs fail at first call, not at config load.

## Reinstalling after a project update

The plugin's agent and skill roster changes over time. After pulling a newer plugin version:

1. Re-run the global install steps in `../INSTALL.md` to refresh `agents/` and `skills/` (`cp -n` and `cp -Rn` only add files; clean stale entries first if you renamed or dropped agents).
2. Compare `opencode.json.sample` against your active config; any new agent that appears in the sample but is missing from the vendor config needs to be added before the swap will pick it up.
3. Re-copy the vendor config:

```bash
cp configs/opencode.jsonc.$VENDOR ~/.config/opencode/opencode.jsonc
```

## Uninstall

Restore the backup taken at install time:

```bash
latest=$(ls -t ~/.config/opencode/opencode.jsonc.bak-* 2>/dev/null | head -1)
if [ -n "$latest" ]; then
  cp "$latest" ~/.config/opencode/opencode.jsonc
  echo "Restored $latest"
else
  cp opencode.json.sample ~/.config/opencode/opencode.jsonc
  echo "No backup found; restored shipped sample."
fi
```

Then delete this `configs/` directory if you no longer want any vendor variants.

## Troubleshooting

- **Missing agents after swap**: the vendor config lists 14 agents; if `/agents` shows fewer, the active config got truncated somewhere. Diff `~/.config/opencode/opencode.jsonc` against `configs/opencode.jsonc.$VENDOR` and re-copy if mismatched.
- **`reasoningEffort` rejected**: the DeepSeek file uses this on most lanes; if your DeepSeek API key is on a tier that rejects the param, edit the file and remove the lines (`reasoningEffort` is optional). The MiniMax file already omits it.
- **Model IDs not in `/models` output**: the provider prefix may have changed. Run `/models`, then update the affected `model` values in the vendor config to match the IDs the active provider exposes. Keep the rest of the file intact.
- **Pure-DeepSeek vision or prose regressed unacceptably**: revert to the preserved mixed snapshot: `cp configs/opencode.jsonc.2026-09-mixed ~/.config/opencode/opencode.jsonc`. That variant routes `visual-critic` to `openrouter/qwen3.8-max` and `wordsmith` to `openrouter/glm-5.3`.
- **Want to revert after a broken swap**: the install step always creates a timestamped backup; pick the most recent and copy it back into place. No backup means no `~/.config/opencode/opencode.jsonc` existed before install, so copy `opencode.json.sample` instead.