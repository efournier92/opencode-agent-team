#!/usr/bin/env python3
"""Sync agent model assignments from models.yaml.

Reads the tier mapping and agent-to-tier mapping in models.yaml, then updates:
- agents/*.md frontmatter `model:` lines
- opencode.json.sample `model` and `agent.*.model` values

Run from the plugin root directory:
    python3 scripts/apply-models.py
"""

import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
MODELS_YAML = ROOT / "models.yaml"
AGENTS_DIR = ROOT / "agents"
SAMPLE_CONFIG = ROOT / "opencode.json.sample"


def load_models():
    with open(MODELS_YAML) as f:
        data = yaml.safe_load(f)
    return data["tiers"], data.get("agent_tiers", {})


def update_agent_frontmatter(agent_name: str, model_id: str):
    path = AGENTS_DIR / f"{agent_name}.md"
    if not path.exists():
        print(f"Warning: {path} not found, skipping")
        return

    content = path.read_text()
    if not content.startswith("---"):
        print(f"Warning: {path} has no frontmatter, skipping")
        return

    # Split frontmatter and body
    _, fm, body = content.split("---", 2)
    fm_lines = fm.splitlines(keepends=True)

    # Update or insert model line after mode line
    new_lines = []
    inserted = False
    has_model = any(line.strip().startswith("model:") for line in fm_lines)

    for line in fm_lines:
        if line.strip().startswith("mode:"):
            new_lines.append(line)
            if not has_model:
                # Insert model line right after mode
                indent = ""
                if line[:1] in " \t":
                    indent = line[: len(line) - len(line.lstrip())]
                new_lines.append(f"{indent}model: {model_id}\n")
                inserted = True
            continue
        if line.strip().startswith("model:"):
            indent = line[: len(line) - len(line.lstrip())]
            new_lines.append(f"{indent}model: {model_id}\n")
            inserted = True
            continue
        new_lines.append(line)

    if not inserted:
        print(f"Warning: could not insert model into {path}")
        return

    new_content = "---" + "".join(new_lines) + "---" + body
    path.write_text(new_content)
    print(f"Updated {path.name}: model={model_id}")


def update_sample_config(tiers, agent_tiers):
    with open(SAMPLE_CONFIG) as f:
        config = json.load(f)

    config["model"] = tiers["top"]

    # Keep only agents we know about; remove stale ones not in mapping
    config["agent"] = {}
    for agent_name, tier in agent_tiers.items():
        mode = "primary" if agent_name == "chief" else "subagent"
        config["agent"][agent_name] = {
            "mode": mode,
            "model": tiers[tier],
        }

    with open(SAMPLE_CONFIG, "w") as f:
        json.dump(config, f, indent=2)
        f.write("\n")
    print(f"Updated {SAMPLE_CONFIG.name}")


def main():
    tiers, agent_tiers = load_models()
    print(f"Tiers: {tiers}")
    print(f"Agent tiers: {agent_tiers}")

    for agent_name, tier in agent_tiers.items():
        update_agent_frontmatter(agent_name, tiers[tier])

    update_sample_config(tiers, agent_tiers)
    print("Done.")


if __name__ == "__main__":
    main()
