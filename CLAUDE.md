# CLAUDE.md

This directory is Claude Code's personal configuration directory (`~/.claude`). It is managed by Claude Code and
contains user-level configuration, commands, skills, and plugins.

## Directory Structure

| Path                          | Purpose                                                                        |
| ----------------------------- | ------------------------------------------------------------------------------ |
| `settings.json`               | Global Claude Code settings (env vars, permissions, model, theme, etc.)        |
| `.claude/settings.local.json` | Local permission overrides                                                     |
| `commands/*.md`               | Custom slash commands (e.g., `/code-refactor`, `/doc-feature`, `/gdrive-sync`) |
| `skills/trip-drive-times/`    | Custom skill for updating drive times in Marp road trip plans                  |
| `plugins/`                    | Installed plugins and marketplace cache                                        |
| `projects/`                   | Per-project CLAUDE.md files and settings                                       |
| `history.jsonl`               | Conversation history                                                           |
| `MEMORY.md`                   | Index for the file-based memory system                                         |

## Custom Commands (Slash Commands)

Located in `commands/*.md`. Trigger with `/command-name`:

- `/swordy-team-orchestrator` — Orchestrates a team of agents to solve an algorithmic challenge.
- `/code-refactor` — Pattern-based refactor across a scope
- `/doc-cleanup-questions` — Resolve open questions in a document
- `/doc-feature` — Document a feature implementation
- `/fix-markdown` — Fix markdown lint errors
- `/gdrive-fetch` — Fetch a Google Doc
- `/gdrive-sync` — Sync with Google Drive
- `/git-commit-msg` — Print a commit message
- `/git-pr-desc` — Create PR description
- `/unit-tests-compact` — Compact unit tests

## Custom Skills

Located in `skills/`:

- **trip-drive-times** — Query Google Maps for traffic-adjusted drive times and update Marp road trip plan slide decks.
  Uses `skills/trip-drive-times/scripts/query-legs.py`.

## Plugins

Installed via `plugins/marketplaces/`. The official marketplace is `claude-plugins-official`. Plugins are managed
through the plugin catalog system — do not manually edit `plugin-catalog-cache.json` or `blocklist.json`.

## Memory System

- `MEMORY.md` — Index file (max 200 lines, each entry <150 chars)
- Individual memory files live alongside `MEMORY.md` with `.md` extension and YAML frontmatter
- Types: `user`, `feedback`, `project`, `reference`
- Memory is loaded automatically into conversation context

## Settings

Global config is in `settings.json`. Key settings:

- `env.CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`: enabled
- `env.CLAUDE_CODE_USE_TMUX`: enabled (teamate mode uses tmux)
- `permissions.defaultMode`: `plan`
- `model`: `Qwen3.6-35B-A3B`
- `editorMode`: `vim`
- `preferences.terminal_integration`: `ghostty`

Local overrides go in `.claude/settings.local.json`.

## Best Practices

- **Custom commands** should be placed in `commands/` as `.md` files with frontmatter headers
- **Skills** should be placed in `skills/` with a `SKILL.md` entrypoint
- **Per-project settings** go in `projects/<project-name>/` (CLAUDE.md + settings)
- **Memory files** should use the frontmatter format (`name`, `description`, `metadata.type`) and be referenced from
  `MEMORY.md`
- **Plugins** should be installed via the marketplace, not manually
- **history.jsonl** is auto-managed — do not edit manually
- **plugin-catalog-cache.json** is auto-managed — do not edit manually

## Swordy Skill Invocation Protocol

When a swordy skill's SKILL.md specifies **"Must be executed by spawning the [X] sub-agent"**:

1. Spawn the correct sub-agent via `Agent` tool with the right `subagent_type`

## Launching Sub-agents

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

## Useful Links

- Claude Code docs: https://code.claude.com/docs/en/overview
- Claude directory: https://code.claude.com/docs/en/claude-directory
- MCP servers: https://code.claude.com/docs/en/mcp
- Skills: https://code.claude.com/docs/en/skills
- Slash commands: https://code.claude.com/docs/en/slash-commands
- Memory system: https://code.claude.com/docs/en/memory
- subagent tools: https://code.claude.com/docs/en/sub-agents#available-tools
- Team of agents: https://code.claude.com/docs/en/agent-team
