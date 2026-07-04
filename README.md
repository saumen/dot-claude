# Claude Code Personal Configuration Directory

This directory (`~/.claude`) contains the personal configuration, custom commands,
skills, agents, and plugins for Claude Code.

## What This Directory Is

A centralized workspace for extending Claude Code with custom behavior:

- **Custom commands** — Slash commands (`/command-name`) that automate workflows
- **Custom skills** — Structured, reusable agent workflows
- **Custom agents** — Specialized sub-agent definitions for complex tasks
- **Plugins** — Marketplace-installed extensions
- **Memory** — File-based knowledge indexed for automatic context loading
- **Project overrides** — Per-project CLAUDE.md files and settings

## Directory Overview

| Component | Description |
| :--- | :--- |
| `settings.json` | Global Claude Code settings (env vars, permissions, model, theme, hooks) |
| `CLAUDE.md` | Primary human-facing documentation for this directory |
| `README.md` | This file — directory overview and usage guide |
| `commands/` | Custom slash commands (e.g., `/swordy-solo-orchestrator`) |
| `skills/` | Custom agent skills with `SKILL.md` entrypoints |
| `agents/` | Specialized sub-agent definitions (Planner, Executor, Reviewer, etc.) |
| `projects/` | Per-project CLAUDE.md files and settings overrides |
| `plugins/` | Installed plugins and marketplace cache |
| `memory/` | File-based memory entries |
| `scripts/` | Utility scripts (hooks, guards) |
| `env-models` | Environment-specific model configuration overrides (JSON file) |
| `docs/plans/` | Implementation planning documents |

For detailed file-purpose mappings, developer conventions, and agent-specific instructions, see [`AGENTS.md`](AGENTS.md).

## Custom Commands

Slash commands live in `commands/*.md` and are triggered with `/command-name`. Available commands:

- `/swordy-solo-orchestrator` — Solo agent orchestration for planning and execution
- `/swordy-team-orchestrator` — Multi-agent team orchestration
- `/swordy-plan-self-improve` — Self-improvement planning
- `/migrate-skills` — Migrate skills workflow
- `/review-skill-migration-plan` — Review skill migration plan

See [`AGENTS.md`](AGENTS.md) for the full command list with descriptions.

## Custom Skills

Skills live in `skills/` with a `SKILL.md` entrypoint. Each skill defines a structured workflow. Available skills:

| Skill | Description |
| :--- | :--- |
| **trip-drive-times** | Query Google Maps for traffic-adjusted drive times |
| **swordy-compact-markdown** | Compact markdown documents losslessly |
| **swordy-explore** | Structured codebase exploration workflow |
| **swordy-fix-markdown** | Fix markdown lint errors iteratively |
| **swordy-git-commit-message** | Generate git commit messages from staged changes |
| **swordy-kid-mode** | Kid-friendly AI assistant |
| **swordy-obsidian-format** | Convert Markdown to Obsidian format |
| **swordy-plan-execute** | Execute structured plan documents |
| **swordy-plan-feature** | Plan new features with decomposition |
| **swordy-plan-refactor** | Plan code restructuring and improvements |
| **swordy-retro** | Generate retrospective reports |
| **swordy-review** | Structured code review workflow |
| **swordy-skill-manager** | Plan and execute agent-skill pair creation |

See [`AGENTS.md`](AGENTS.md) for skill invocation protocols and technical details.

## Custom Agents

Agents live in `agents/*.md` as specialized sub-agent definitions:

- **swordy-agent-execute** — Task execution agent
- **swordy-agent-explorer** — Codebase exploration agent
- **swordy-agent-fix-markdown** — Markdown lint fixing agent
- **swordy-agent-git-commit-message** — Git commit message agent
- **swordy-agent-markdown-compact** — Markdown compaction agent
- **swordy-agent-planner** — Planning agent
- **swordy-agent-reviewer** — Code review agent

## Memory System

Memory uses a file-based approach indexed in [`MEMORY.md`](MEMORY.md). Individual memory files live in `memory/` with YAML frontmatter to categorize entries (`user`, `feedback`, `project`, `reference`). Memory is loaded automatically into conversation context.

Historical memory notes are stored in `memories/`.

## Project Overrides

Per-project configuration lives in `projects/<project-name>/`. Each project can have its own CLAUDE.md and settings overrides, allowing Claude Code to adapt behavior per-project.

## Utility Scripts

- `scripts/md-prettier-hook.sh` — Runs markdown prettier after Write/Edit operations (configured as a post-write hook)
- `scripts/skill-guard/` — Skill execution guard (Python project with tests)

---

_Note: This directory is managed by Claude Code. Manual edits should be handled with care to avoid disrupting system-managed files._
