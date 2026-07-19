# Claude Code Personal Configuration Directory

This directory (`~/.claude`) contains the personal configuration, custom commands, skills, agents, and plugins for Claude Code.

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
| `CLAUDE.md` | System documentation loaded into agent context |
| `README.md` | This file — directory overview and usage guide |
| `AGENTS.md` | Developer/AI agent guidelines (structure, conventions, commands) |
| `commands/` | Custom slash commands (e.g., `/swordy-solo-orchestrator`) |
| `skills/` | Custom agent skills with `SKILL.md` entrypoints |
| `agents/` | Specialized sub-agent definitions (Planner, Executor, Reviewer, etc.) |
| `projects/` | Per-project CLAUDE.md files and settings overrides |
| `plugins/` | Installed plugins and marketplace cache |
| `memory/` | File-based memory entries |
| `memories/` | Historical memory notes |
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
- `/swordy-docs-sync-inline` — Sync README.md and AGENTS.md with actual project state (inline execution, no sub-agents)
- `/swordy-refactor-docs` — Refactor documentation files into organized sub-files
- `/swordy-verify-docs` — Verify documentation accuracy against actual project state
- `/swordy-manage-llama-model` — Add or edit llama.cpp server provider models from HuggingFace GGUF repos. For vLLM models, use /swordy-manage-vllm-model instead.

See [`AGENTS.md`](AGENTS.md) for skill invocation protocols and technical details.

## Memory System

Memory uses a file-based approach indexed in `MEMORY.md`. Individual memory files live in `memory/` with YAML frontmatter to categorize entries (`user`, `feedback`, `project`, `reference`). Memory is loaded automatically into conversation context.

Historical memory notes are stored in `memories/`.

## Project Overrides

Per-project configuration lives in `projects/<project-name>/`. Each project can have its own CLAUDE.md and settings overrides, allowing Claude Code to adapt behavior per-project.

## Utility Scripts

- `scripts/md-prettier-hook.sh` — Runs markdown prettier after Write/Edit operations (configured as a post-write hook)
- `scripts/skill-guard/` — Skill execution guard (Python project with tests)

---
