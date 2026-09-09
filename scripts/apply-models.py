#!/usr/bin/env python3
"""Sync OpenCode JSON config from models.yaml.

models.yaml is the single source of truth for agent model assignments.
This script renders it into opencode.json.sample so the JSON config is
the actual runtime source of truth.

It also enforces the architecture invariant:

    No agent or skill file may declare model: in its YAML frontmatter.
    Model pinning lives only in opencode.json / opencode.jsonc.

If any agent file still has a model: line (stale output from an older
version of this script, or a hand edit), this script strips it. If any
skill file has a model: line, it exits non-zero so the regression is
loud rather than silent.

Run from the plugin root directory:

    python3 scripts/apply-models.py
"""

import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
MODELS_YAML = ROOT / "models.yaml"
AGENTS_DIR = ROOT / "agents"
SKILLS_DIR = ROOT / "skills"
SAMPLE_CONFIG = ROOT / "opencode.json.sample"

# Matches a single `model:` line. Used only against the frontmatter
# slice of a file (extracted by strip_frontmatter_model_line), never
# against the whole document.
MODEL_LINE_RE = re.compile(r"^[ \t]*model:[ \t]*\S+[ \t]*$")


def load_models():
    with open(MODELS_YAML) as f:
        data = yaml.safe_load(f)
    if "tiers" not in data:
        raise SystemExit("models.yaml missing required key: tiers")
    if "agent_tiers" not in data:
        raise SystemExit("models.yaml missing required key: agent_tiers")
    return data["tiers"], data["agent_tiers"]


def validate_models(tiers, agent_tiers):
    """Fail loud on inconsistent models.yaml before touching any file."""
    for name, tier in agent_tiers.items():
        if tier not in tiers:
            raise SystemExit(
                f"unknown tier '{tier}' for agent '{name}'; "
                f"known tiers: {sorted(tiers)}"
            )
        if not (AGENTS_DIR / f"{name}.md").is_file():
            raise SystemExit(
                f"agent_tiers entry '{name}' has no agents/{name}.md"
            )


def strip_frontmatter_model_line(content):
    """Strip `model:` lines from the YAML frontmatter only; body untouched.

    Returns (new_content, n_stripped). Idempotent.
    """
    if not content.startswith("---"):
        return content, 0
    end = content.find("\n---", 3)
    if end == -1:
        return content, 0
    fm = content[3:end + 1]
    lines = fm.splitlines(keepends=True)
    kept = []
    n = 0
    for line in lines:
        if MODEL_LINE_RE.match(line.rstrip("\n")):
            n += 1
        else:
            kept.append(line)
    if n == 0:
        return content, 0
    new_fm = "".join(kept)
    return content[:3] + new_fm + content[end + 1:], n


def strip_agent_model_lines():
    """Remove any `model:` line from agents/*.md frontmatter.

    The JSON config is the source of truth; agent files must not pin
    a model or they will shadow opencode.json's agent.<name>.model.
    Idempotent: no-op when the line is already absent.
    """
    if not AGENTS_DIR.is_dir():
        return 0
    changed = 0
    for path in sorted(AGENTS_DIR.glob("*.md")):
        content = path.read_text()
        new_content, n = strip_frontmatter_model_line(content)
        if n:
            path.write_text(new_content)
            print(f"Stripped model: line from {path.name}")
            changed += 1
    return changed


def assert_no_skill_model_lines():
    """Skill frontmatter must never pin a model. Fail loud if one does."""
    if not SKILLS_DIR.is_dir():
        return
    offenders = []
    for path in sorted(SKILLS_DIR.rglob("SKILL.md")):
        content = path.read_text()
        if strip_frontmatter_model_line(content)[1] > 0:
            offenders.append(path)
    if offenders:
        for p in offenders:
            print(f"error: skill frontmatter pins a model: {p}", file=sys.stderr)
        raise SystemExit(
            "skills must not declare model: in frontmatter; "
            "model pinning belongs in opencode.json / opencode.jsonc"
        )


def render_sample_config(tiers, agent_tiers):
    with open(SAMPLE_CONFIG) as f:
        config = json.load(f)

    config["model"] = tiers["top"]

    # Keep only agents we know about; remove stale ones not in mapping.
    config["agent"] = {}
    for agent_name, tier in agent_tiers.items():
        mode = "primary" if agent_name == "chief" else "subagent"
        config["agent"][agent_name] = {
            "mode": mode,
            "model": tiers[tier],
        }
    return config


def write_sample_config(config):
    """Serialize the rendered config to disk. Returns (rendered_text, changed).

    Skip the write when the rendered text already matches the file on disk,
    so re-running with no changes leaves the mtime untouched.

    Returning the text lets main() verify the on-disk file equals the
    in-memory render (byte-identical write), so a future bug that lets
    the two diverge fails loud.
    """
    rendered = json.dumps(config, indent=2) + "\n"
    existing = SAMPLE_CONFIG.read_text() if SAMPLE_CONFIG.exists() else None
    if existing == rendered:
        return rendered, False
    with open(SAMPLE_CONFIG, "w") as f:
        f.write(rendered)
    return rendered, True


def main():
    tiers, agent_tiers = load_models()
    print(f"Tiers: {tiers}")
    print(f"Agent tiers: {agent_tiers}")

    validate_models(tiers, agent_tiers)

    assert_no_skill_model_lines()
    stripped = strip_agent_model_lines()

    rendered, changed = write_sample_config(render_sample_config(tiers, agent_tiers))
    if changed:
        print(f"Updated {SAMPLE_CONFIG.name}")
    else:
        print(f"{SAMPLE_CONFIG.name} already up to date")

    on_disk = SAMPLE_CONFIG.read_text()
    if on_disk != rendered:
        raise SystemExit(
            "internal: opencode.json.sample on disk does not match in-memory render"
        )

    if stripped:
        print(f"Stripped {stripped} stale agent model: line(s).")
    print("Done.")


if __name__ == "__main__":
    main()
