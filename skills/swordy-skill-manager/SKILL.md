---
description: >
  Swordy Skill Manager: Plan and execute agent-skill pair creation with
  architecture compliance. Scaffold new Claude Code skills paired with custom
  sub-agents, update existing agent-skill configurations, and validate
  that agents and skills follow established architecture conventions.
when_to_use: Use when creating or updating agent-skill pairs, scaffolding new skills with custom sub-agents, or validating agent-skill architecture conventions.
---

# Swordy Skill Manager

Plans and executes **agent-skill pair** creation and updates — where a skill is the *user entry point* and an agent is the *backend executor* — with full architecture compliance.

## Agent-Skill Pairing Model

- **Skill** (`~/.claude/skills/<name>/SKILL.md`) — the "how" + **user entry point**: workflow, process, domain knowledge. Users invoke as `/skill-name`.
- **Agent** (`~/.claude/agents/<name>.md`) — the "who" + **backend executor**: role, tools, permission mode, description. Spawned by the skill's workflow.
- **Pairing** — Skills are auto-discovered from `~/.claude/skills/`. The skill's workflow spawns the agent.

**Skills do NOT require a 1:1 dedicated agent.** Multiple skills can reuse the same agent (e.g., `swordy-plan-refactor`, `swordy-plan-coverage`, and `swordy-plan-feature` all reuse `swordy-agent-planner`). Only create a new agent when the skill needs a distinct role, tool set, or permission mode.

This skill uses `swordy-agent-planner` for architecture decisions and `swordy-agent-execute` for implementation.

## Pre-Flight Checklist

Before starting any workflow, complete these checks:

1. **Naming convention** — Skill names use `swordy-` prefix.
2. **Agent reuse** — Check if an existing agent can handle this skill's role (Step 3).

If any check fails, **STOP** and ask the user for clarification.

## Naming Convention

**Rule:** Skills use `swordy-` prefix.

| Component | Format | Example |
|-----------|--------|---------|
| Skill | `swordy-<name>` | `swordy-git-commit-message` |
| Agent | `swordy-agent-<name>` | `swordy-agent-git-commit-message` |

**Validation:** If the skill name lacks `swordy-` prefix, propose renaming it.

## Workflow

### Step 1: Fetch Latest Documentation

Fetch the latest content from official Claude Code documentation before creating or updating anything:

- Skills: `https://code.claude.com/docs/en/skills`
- Sub-agents: `https://code.claude.com/docs/en/sub-agents`

See [CLAUDE.md](CLAUDE.md) for the full list of documentation sources.

### Step 2: Plan with Planner

Spawn `swordy-agent-planner` to evaluate agent reuse and produce an architecture plan:

1. **List existing agents** — Read `~/.claude/agents/` to identify available agents.
2. **Match by role** — Compare the skill's required executor role against existing agents:
   - Planning tasks → `swordy-agent-planner` (workspace-write)
   - Exploration/context gathering → `swordy-agent-explorer` (read-only)
   - Code review/audit → `swordy-agent-reviewer` (read-only)
   - Plan execution/implementation → `swordy-agent-execute` (workspace-write)
3. **Provide rationale** — Present findings to the user:
   - **Reuse recommended:** "Skill X can reuse `swordy-agent-<existing>` because [reason: matching role/tools/permissionMode]."
   - **New agent needed:** "Skill X requires a dedicated agent because [reason: distinct role, different tools, unique permission needs]."
4. **Confirm with user** — Ask the user to approve the decision before proceeding.

**CHECKPOINT:** Present the architecture plan to the user. Ask:
- "Should I proceed with [reuse/create]ing agent `<name>`?"
- "Is the naming convention correct: skill=`swordy-<name>`, agent=`swordy-agent-<name>`?"

**DO NOT proceed to Step 3 until the user confirms.**

**Output:** architecture plan specifying whether to reuse an existing agent or create a new one.

### Step 3: Execute with Executor

After the user approves the plan, spawn `swordy-agent-execute` to implement:

1. **Create the skill** — Follow the skill scaffolding process for creating the skill directory, SKILL.md with YAML frontmatter, and bundled resources.
   - **YAML frontmatter is always created** — with `description` and `when_to_use` fields.
   - **No `openai.yaml`** — metadata is in SKILL.md frontmatter.
   - **Spawn directive is mandatory** — the SKILL.md must include an explicit directive telling the model which agent to spawn, plus a fallback. Place it right before the `## Workflow` section:
     ```markdown
     - **Must be executed by spawning a `<agent>` sub-agent.** Do not execute inline.
     - **Fallback:** If the `<agent>` agent fails twice (stream disconnect or other error), run the workflow inline using this skill's steps. Do not retry the agent.
     ```

2. **Create the agent file (if new agent needed):**

```yaml
---
name: swordy-agent-<name>
description: "..."
tools: Read, Grep, Glob, Bash, Write, Edit
effort: high
permissionMode: acceptEdits
---

<role definition only — no process steps>
```

   - **Rationale comments:** Add inline `#` comments before each attribute explaining the design choice (tools, permissionMode, effort). This ensures future maintainers understand *why* each setting was selected.
   - **`description`** = role and mandate only. Process steps belong in SKILL.md.
   - **`permissionMode`:** `acceptEdits` for agents that write files; `default` for read-only.
   - **`tools`:** Explicit tool list (not inherited). `Explore` for read-only agents that need search; `Read, Grep, Glob, Bash` for file inspection; `Read, Grep, Glob, Bash, Write, Edit` for writers.
   - The agent file does **not** include skill registration (skills are auto-discovered from `~/.claude/skills/`).

3. **Validate:**

```bash
python3 ~/.claude/skills/swordy-skill-manager/scripts/verify_skill_architecture.py ~/.claude/skills/swordy-skill-manager
```

   Runs all architecture checks. Fix any failures before proceeding.

## Key Reminders

- **Agent `description` = role, SKILL.md = process** — don't duplicate
- **`permissionMode`:** `default` for pure readers (e.g., explorers, reviewers); `acceptEdits` for agents that produce output files (e.g., planners, implementers)
- **Spawn directive is mandatory:** every SKILL.md paired with an agent must include the explicit spawn directive + fallback. Without it, the skill runs inline instead of delegating to its backend executor. See [Architecture Rules](references/architecture_rules.md).
- **Skills are auto-discovered** from `~/.claude/skills/` — no registration needed
- **Skill descriptions:** front-load trigger words, include explicit "when to use" scenarios in the frontmatter, not the body

## Required SKILL.md Sections

Every skill's `SKILL.md` must contain the following four sections (headers are case-insensitive). If a section has no special instructions for a given skill, it must contain at least a one-liner: `Not Applicable. [Rationale].`

1. **## Workflow** — The canonical section defining the step-by-step process.
2. **## Agent Routing** — Specifies which agent to spawn and fallback behavior.
3. **## Parallelization Guidance** — Instructions for parallel vs. sequential execution.
4. **## Scope** — Defines when to use and when NOT to use the skill.

## When to Ask Questions

Ask the user when:
- The skill name doesn't follow `swordy-` prefix convention
- Agent reuse is ambiguous (multiple agents could handle the role)
- The user's request is unclear or incomplete
- There are conflicting requirements

**Ask concise, specific questions with options.** Present 2–3 choices when possible.

## Agent Routing

- **Architecture planning phase:** Must be executed by spawning the planner sub-agent using the Agent tool with subagent_type: swordy-agent-planner. Do not plan inline.
- **Implementation phase:** Must be executed by spawning the execute sub-agent using the Agent tool with subagent_type: swordy-agent-execute. Do not implement inline.
- **Fallback:** If either agent fails twice (stream disconnect or other error), run the workflow inline using this skill's steps. Do not retry the agent.

## Parallelization Guidance

Not Applicable. Agent-skill pair creation is a sequential, two-phase process (plan then execute).

## Scope

**Use for:**
- Creating new agent-skill pairs from scratch
- Updating existing agent or skill configurations
- Validating that agents and skills follow architecture conventions
- Auditing agent-skill alignment across the skill set

**Do NOT use for:**
- Planning feature implementations (use swordy-plan-feature)
- Code review (use swordy-review)
- Exploring codebases (use swordy-explore)

## References

- [CLAUDE.md](CLAUDE.md) — documentation URLs and references index
- [Architecture Rules](references/architecture_rules.md) — all rules with embedded good/bad examples
