# AGENTS.md — Repository Guidelines

**Read [`README.md`](README.md)** for human-oriented documentation about this directory.

## Documentation & File Purposes

This project uses multiple markdown files, each with a distinct audience and scope. Do not duplicate content across them.

| File | Audience | Scope |
|---|---|---|
| [`README.md`](README.md) | End users | Directory overview, setup, workflow, feature usage |
| `CLAUDE.md` | End users | Primary human-facing documentation (legacy — see README.md) |
| `AGENTS.md` (this file) | Developers & AI assistants | Project structure, commands, skills, conventions, commit guidelines |
| [`MEMORY.md`](MEMORY.md) | All | Index for the file-based memory system |
| `memory/*.md` | All | Individual memory entries with YAML frontmatter |
| `memories/*.md` | All | Historical memory notes |
| `docs/plans/*.md` | Implementation tracking | Planning documents — no implementation snippets |

**Rule:** If content belongs to a user-facing guide (setup, usage, overview), it goes in README/CLAUDE. If it's developer/AI guidance (structure, conventions, commands, scripts), it goes in this file or in the dedicated guideline files linked above.

## Project Structure & Module Organization

```
~/.claude/
├── CLAUDE.md              # Primary human-facing docs (legacy — see README.md)
├── README.md              # Human-facing directory overview (primary)
├── AGENTS.md              # This file — developer/AI guidelines
├── MEMORY.md              # Memory index (max 200 lines, entries <150 chars)
├── settings.json          # Global Claude Code settings (env, permissions, model, hooks)
├── .gitignore             # Git ignore rules (system-managed dirs, caches)
├── agents/                # 7 specialized sub-agent definitions
│   ├── swordy-agent-execute.md
│   ├── swordy-agent-explorer.md
│   ├── swordy-agent-fix-markdown.md
│   ├── swordy-agent-git-commit-message.md
│   ├── swordy-agent-markdown-compact.md
│   ├── swordy-agent-planner.md
│   └── swordy-agent-reviewer.md
├── commands/              # 5 custom slash commands
│   ├── migrate-skills.md
│   ├── review-skill-migration-plan.md
│   ├── swordy-plan-self-improve.md
│   ├── swordy-solo-orchestrator.md
│   └── swordy-team-orchestrator.md
├── skills/                # 13 custom skills (12 swordy-*, 1 trip-drive-times)
│   ├── swordy-compact-markdown/
│   ├── swordy-explore/
│   ├── swordy-fix-markdown/
│   ├── swordy-git-commit-message/
│   ├── swordy-kid-mode/
│   ├── swordy-obsidian-format/
│   ├── swordy-plan-execute/
│   ├── swordy-plan-feature/
│   ├── swordy-plan-refactor/
│   ├── swordy-retro/
│   ├── swordy-review/
│   ├── swordy-skill-manager/
│   └── trip-drive-times/
├── scripts/               # Utility scripts
│   ├── md-prettier-hook.sh  # Post-write markdown prettier hook
│   └── skill-guard/       # Skill execution guard (Python project)
├── projects/              # 46 per-project CLAUDE.md files and settings
├── plugins/               # Installed plugins and marketplace cache
├── memory/                # 2 memory files (YAML frontmatter)
├── memories/              # 1 historical memory note
├── env-models             # Environment-specific model configuration file (JSON)
├── docs/plans/            # Implementation planning documents
├── history.jsonl          # Conversation history (auto-managed — do not edit)
├── todos/                 # Task/todo JSON files
├── sessions/              # Active session state
├── session-env/           # Session environment snapshots
├── file-history/          # File change history
├── paste-cache/           # Paste cache
├── jobs/                  # Job state (pins.json)
├── backups/               # Backup files
├── downloads/             # Downloaded files
├── debug/                 # Debug output
├── daemon/                # Daemon state (roster.json, dispatch)
├── shell-snapshots/       # Zsh snapshot files
├── statsig/               # Statsig telemetry cache
├── telemetry/             # Telemetry data
├── teams/                 # Team state
├── ide/                   # IDE integration state
├── .pi-lens/              # Pi lens cache and state
├── .active-skill          # Currently active skill
└── .last-cleanup          # Last cleanup timestamp
```

## Build, Test, and Development Commands

| Command | Purpose |
|---|---|
| `claude --permission-mode auto --model <model>` | Launch Claude Code in auto mode |
| `/swordy-solo-orchestrator` | Launch solo agent orchestration |
| `/swordy-team-orchestrator` | Launch multi-agent team orchestration |
| `/swordy-plan-self-improve` | Self-improvement planning command |
| `/migrate-skills` | Migrate skills workflow |
| `/review-skill-migration-plan` | Review skill migration plan |

### Post-Write Hook

`scripts/md-prettier-hook.sh` runs automatically after `Write` or `Edit` tool use (configured in `settings.json` hooks).

### Skill Guard

`scripts/skill-guard/` is a Python project that guards skill execution. It includes tests under `scripts/skill-guard/tests/`.

## Commit & Pull Request Guidelines

- Use conventional commit prefixes (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`). Imperative mood, subject line under 72 characters, no trailing period.
- Example: `feat: Add <feature>`
- PRs should include a clear description, link related issues, and note any environment variable changes.

## Documentation & Planning

- Planning documents go in `docs/plans/`
- Do not include implementation snippets in planning docs
- Cross-reference between README.md (user-facing) and AGENTS.md (developer-facing)

## Agent-Specific Instructions

### Swordy Skill Invocation Protocol

When a swordy skill's SKILL.md specifies **"Must be executed by spawning the [X] sub-agent"**:

1. Spawn the correct sub-agent via `Agent` tool with the right `subagent_type`
2. Never skip agent spawning for swordy skills

### Launching Sub-agents

When teammates are spawned, the following environment must be respected. Teammates must use `sonnet` or `opus`.

- For exploratory tasks, planning use `sonnet`.
- For precise implementation, execution use `opus`.

Example: launch sub-agent

```bash
export ANTHROPIC_BASE_URL=http://192.168.4.110:8080
export ANTHROPIC_AUTH_TOKEN=none
export CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY=1
claude --permission-mode auto --model [sonnet|opus]
```

### Naming Convention

All custom skills, prompts, and agents must be prefixed with `swordy-` (e.g., `swordy-verify-docs`, `swordy-plan-feature`). This keeps them distinguishable from built-in or third-party components.

### Generic Examples

Prompts, skills, and agents must use generic, domain-agnostic examples. Never expose project-specific domains (file names, tool names, config formats) when authoring reusable agentic components.

### Read Docs Before Implementing

Before writing prompts, skills, agents, or any code that uses Claude Code-specific features, always read the relevant Claude Code documentation first.

## Memory System

- `MEMORY.md` — Index file (max 200 lines, each entry <150 chars)
- Individual memory files live in `memory/` with `.md` extension and YAML frontmatter
- Types: `user`, `feedback`, `project`, `reference`
- Memory is loaded automatically into conversation context
- Do not manually edit `history.jsonl` — it is auto-managed

## Auto-Managed Files (Do Not Edit)

The following files are managed by the system — do not manually edit:

- `history.jsonl` — Conversation history
- `plugins/plugin-catalog-cache.json` — Plugin catalog cache
- `plugins/blocklist.json` — Plugin blocklist
- `mcp-needs-auth-cache.json` — MCP auth cache
- `stats-cache.json` — Stats cache
- `session-env/*` — Session environment snapshots
- `file-history/*` — File change history
- `backups/*` — Backup files
- `daemon/*` — Daemon state
- `statsig/*` — Statsig telemetry
- `telemetry/*` — Telemetry data
