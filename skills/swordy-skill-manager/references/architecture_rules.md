# Architecture Rules

## 1. SKILL.md = Process, Agent description = Role
**Agent `description`** defines **WHO** (role + mandate). **SKILL.md** defines **HOW** (workflow + process). No duplication.

| Component | ✅ Correct (Role/Process Separation) | ❌ Incorrect (Mixing Role/Process) |
| :--- | :--- | :--- |
| **Agent (`.md`)** | `description: "You are a codebase explorer."` | `description: "You are an explorer. Step 1: Read README, Step 2: Use rg..."` |
| **Skill (SKILL.md)** | `## Workflow \n 1. Read README \n 2. Use rg...` | `## About \n You are a codebase explorer whose role is to...` |

---

## 2. Skills Own Their Output Paths
Output paths belong in **SKILL.md**, never in Agent description.

| Component | ✅ Correct | ❌ Incorrect |
| :--- | :--- | :--- |
| **Agent (`.md`)** | `description: "You are a code reviewer."` | `description: "...Write findings to docs/review.md."` |
| **Skill (SKILL.md)** | `## Workflow \n 1. Review code \n 2. Write to docs/review.md` | (Missing output guidance) |

---

## 3. Skills are Auto-Discovered
Skills are automatically discovered from `~/.claude/skills/`. No registration, config file, or manifest is needed.

- ✅ `~/.claude/skills/swordy-plan-feature/SKILL.md` (auto-discovered)
- ❌ Adding skill registration in a config file or manifest

---

## 4. Agent-Skill Alignment
- **Agent files** live in `~/.claude/agents/<name>.md` with YAML frontmatter.
- **Skill files** live in `~/.claude/skills/<name>/SKILL.md`.

**Correct Agent File:**
```yaml
---
name: swordy-agent-planner
description: "You are a planning specialist..."
tools: Read, Grep, Glob, Bash, Write, Edit
effort: high
permissionMode: acceptEdits
---

<Role definition only — no process steps>
```

**Correct Skill Frontmatter:**
```yaml
---
description: >
  Swordy Plan Feature: Plan new features with structured decomposition.
when_to_use: Use when adding a feature, building a new capability, or extending functionality.
---
```

---

## 5. Handover Templates
- **Portable:** Store templates in skill-local `references/` (Preferred).
- **Shared:** Store in `~/.claude/agents/` (Must be documented).
- **Forbidden:** Hardcoding template paths in Agent files.

---

## 6. Fetch Latest Documentation
Always fetch live content from official Claude Code documentation URLs before creating/updating skills. Do **not** rely on cached or bundled knowledge.
- `https://code.claude.com/docs/en/skills` (Conventions)
- `https://code.claude.com/docs/en/sub-agents` (Configuration)

---

## 7. Skill Invocation & Discovery
**Skills** are user-facing entry points (`/skill-name`). **Agents** are backend executors spawned by the skill's workflow.

| Mechanism | Location | Effect |
| :--- | :--- | :--- |
| `~/.claude/skills/` | SKILL.md in subdirectory | Auto-discovered by Claude Code |
| Agent tool call | SKILL.md workflow | Skill spawns agent as sub-agent |

**Key Insight:** Skills are discovered from `~/.claude/skills/`. The skill's workflow spawns the agent via the Agent tool.

---

## 8. Spawn Directive is Mandatory
Every SKILL.md paired with an agent must include an explicit spawn directive + fallback. Place it right before the `## Workflow` section:

```markdown
- **Must be executed by spawning a `<agent>` sub-agent.** Do not execute inline.
- **Fallback:** If the `<agent>` agent fails twice (stream disconnect or other error), run the workflow inline using this skill's steps. Do not retry the agent.
```

Without the spawn directive, the skill runs inline instead of delegating to its backend executor.
