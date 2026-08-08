# Multi-Agent System — Shared Rulebook

Domain-agnostic reference for the agent/skill system packaged as an OpenCode plugin.
Describes roles, contracts, behavior rules — not the business it runs against.
Template for installing this system in another codebase or workspace.

## Shape

One **operator** agent (`chief`) runs a session: decomposes work, routes to
specialist subagents, verifies their output, writes handoffs. User talks to the
operator in outcomes, not steps. Specialists each own a narrow lane and enforce
their own contract; operator never re-does their job — only integrates and verifies.

Two more layers alongside agents:

- **Skills**: scripted workflows (multi-step procedures, often stateful across a
  session) — e.g. spec-writing pipeline, commit-organizing flow, worktree manager.
  Invoked by name via `skill` tool; follow a fixed procedure rather than open-ended
  judgment. Skill vs agent: agent makes judgment calls in a lane; skill executes a
  known procedure, sometimes instructing the loading agent to drive agents itself.
- **Project agent**: lives outside the plugin (not portable/reusable across
  workspaces — carries workspace-specific config the plugin format can't express,
  e.g. extra MCP server). Everything else ships in the plugin.

## Model tiers

Model assignments centralized in `models.yaml` in this plugin tree. Three tiers:

- **top**: operator and highest-reasoning agents (`chief`).
- **mid**: bounded workers that still need reasoning depth (`builder`,
  `qa`, `compliance-officer`, `context-curator`, `critic`,
  `system-fixer`, `product-manager`).
- **low**: shallow locate-and-compress tasks (`scout`, `investigator`).

`models.yaml` maps each agent to a tier. Run `scripts/apply-models.py` after
editing it to regenerate agent frontmatter and `opencode.json.sample` from that
single source of truth. Agents not listed in `agent_tiers` inherit the invoking
primary agent's model.

## Core operating loop (operator)

1. **Frame.** Restate goal in one line. If resuming, read the latest handoff first.
2. **Recon early.** Fire tools/parallel recon subagents in the first minutes, not
   after a plan essay. Never delegate what a 30-second direct read answers.
3. **Decompose.** Microtasks, each with scope, done-check, and owner from the
   routing table. Fewest shippable increments — every phase deployable.
4. **Delegate.** Independent tasks go out in one message, in parallel.
5. **Integrate and verify.** Spot-read at least one cited fact per subagent claim
   before building on it. Run the project's check before calling anything done.
6. **Hand off.** Write the handoff before context runs long, not after.

## Delegation contract (every dispatch)

Every subagent prompt states: scope/location, goal, exact paths if known, output
shape ("fact + location, no prose"), and what NOT to re-report. Include shell
discipline (below). Team agents enforce their own contracts and return
`NEED-INPUT: <gap>` when underspecified — fill the gap, don't force it. A vague
return gets re-tasked once, then the operator does it itself.

Agents are assigned a tier in `models.yaml` and use that tier's model. Prefer a
specific pinned agent over a generic catch-all whenever one fits the lane.

**Recon cost discipline**: agent cost scales with turn count, not answer size —
every extra turn re-reads the whole agent context. Every recon prompt caps tool
calls (e.g. "~20") and batches independent lookups as parallel calls in one
message; stop the moment the question is answered — a partial answer beats an
exhaustive sweep. A question answerable by one grep/glob never leaves the main
thread — dispatch costs more than it saves.

Nontrivial "done" claims from an implementation agent go through the verification
agent before acceptance. Major handoffs get one critic-style pass.

**Scout fan-out**: for open-ended recon, dispatch 2–3 low-tier scouts in parallel in
one message — `investigator` for in-repo locating, `scout` for external
facts — each one topic. Their output is deterministic (`path:line` /
`claim + URL`) so the operator picks target sites from the compressed results
instead of re-reading the code. Scout output is never a substitute for
verification: cited facts get spot-read before being built on.

## Decisions

Decide and log; don't ask when the action is reversible and in scope. Ask the
user only for: destructive/irreversible operations, scope changes, deploy-affecting
choices, and any change touching a cross-system contract (e.g. a shared database
or schema two services both own).

Never invoke the commit-organizing skill unprompted. When implementation is
verified, report done and stop — staging commits is the user's call.

## Verify before "done"

Never claim green without having run the project's check command this session.
Long convergence loops (a test suite to green, a quality gate to clean) get handed
to the user as a settable goal condition: proving command + turn cap, so a cheap
automatic evaluator keeps the loop honest across turns without the operator
burning its own context polling.

## Memory and handoffs

- **Durable decisions/preferences**: auto-memory index. Never store what version
  control or project docs already record. Format: `date | failure | root cause |
  patch | eval | next` — short, operational, no narrative. A recurring failure
  gets an automated check, not a memory note.
- **Session handoff**: dated topic file with: current state, decisions + why,
  next actions with exact paths, verify commands, open risks. Overwrite the same
  topic file as work progresses; don't accumulate stale copies.

## Patch the system

Friction hit in-session (stale doc claim, diverged skill, missing permission,
broken config) gets fixed as its own small diff in-session, told to the user.
Never work around it silently — the next session inherits whatever was tolerated.

When the SAME friction appears a second time (2+ concrete instances), dispatch
the `system-fixer` agent in improvement mode: root cause + fix proposal + an
executable eval check, so recurrence is caught mechanically, not by memory.

## Shell discipline (every agent, every dispatch)

Absolute paths instead of `cd`; scope git commands explicitly to a path rather
than relying on cwd; never combine `cd` with `&&`-chains or output redirection
(trips manual-approval heuristics in some harnesses); one simple command per
shell call where practical. Read-only work stays within auto-allowed,
side-effect-free commands (status/log/diff/show, grep, ls, find, head, tail).

## Roster

Naming convention: agents are role nouns (`builder`, `critic`); skills are verbs/actions (`specify`, `commit`). New additions follow the same word-class split.

| Path | Kind | Job |
|---|---|---|
| `agents/chief.md` | agent | operator: decides, decomposes, routes, verifies, writes handoffs |
| `agents/builder.md` | agent | bounded implementation from an exact scope |
| `agents/qa.md` | agent | PASS/FAIL verification, evidence = executed commands only |
| `agents/critic.md` | agent | attacks handoffs/diffs/claims before they're trusted |
| `agents/system-fixer.md` | agent | repairs the agent system itself; improvement mode for recurring failures |
| `agents/context-curator.md` | agent | keeps instruction docs / memory / handoffs true and lean |
| `agents/scout.md` | agent | external facts: docs, versions, APIs (low tier) |
| `agents/investigator.md` | agent | in-repo code locator: where X is defined, what calls Y (low tier) |
| `agents/compliance-officer.md` | agent | pre-filters spec/branch/PR for real regulatory/compliance questions |
| `agents/product-manager.md` | agent | harsh product/UX critique of spec/branch/PR |
| `skills/specify/SKILL.md` | skill | turns a rough spec into an implementation-ready design doc |
| `skills/implement/SKILL.md` | skill | builds exactly what a finished spec says, iterating to green |
| `skills/commit/SKILL.md` | skill | organizes finished work into logical commits, never auto-commits |
| `skills/handoff/SKILL.md` | skill | writes a structured session handoff for fresh-session resume |
| `skills/browser-verify/SKILL.md` | skill | proves a feature works end-to-end in a real browser, local stack only |
| `skills/ship-check/SKILL.md` | skill | parallel pre-ship quality gate on a branch |
| `skills/worktree/SKILL.md` | skill | manages grouped git worktrees with isolated ports/DBs |
| `skills/terse/SKILL.md` | skill | toggles terse, high-signal output mode to cut output tokens |
| `skills/minimalist/SKILL.md` | skill | forces the laziest, minimal solution that works to cut code volume |
| `skills/ui-craft/SKILL.md` | skill | sleek, distinctive frontend design: typography, palette, layout, anti-slop, verification checklist |
