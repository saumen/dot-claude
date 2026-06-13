# Claude Code Personal Configuration Directory

This directory (`~/.claude`) contains the personal configuration, custom commands,
skills, and plugins for Claude Code.

## Directory Structure

| `agents/` | Specialized sub-agents (e.g., Planner, Executor, Reviewer) |
| `commands/` | Custom slash commands (e.g., `/code-refactor`, `/doc-feature`) |
| `skills/` | Custom agent skills with `SKILL.md` entrypoints |
| `settings.json` | Global Claude Code settings |
| `MEMORY.md` | Index for the memory system |

## Key Components

### Custom Commands (Slash Commands)

Located in `commands/*.md`. Triggered using the `/command-name` syntax.

### Custom Skills

Located in `skills/`. Skills are structured workflows that can often leverage
specialized sub-agents to perform complex tasks.

### Memory System

Uses a file-based approach indexed in `MEMORY.md`. Individual memory files use
YAML frontmatter to categorize entries as `user`, `feedback`, `project`, or `reference`.

## Best Practices

- **Agents:** Place in `agents/` as `.md` files for specialized sub-agent definitions.
- **Skills:** Place in `skills/` with a `SKILL.md` entrypoint.
- **Commands:** Place in `commands/` as `.md` files with appropriate frontmatter.
- **Projects:** Use `projects/<project-name>/` for project-specific overrides.
- **Memory:** Ensure all new memory files are indexed in `MEMORY.md`.
- **Automation:** Do not manually edit `history.jsonl` or plugin catalog files; these are managed by the system.

---

_Note: This directory is managed by Claude Code. Manual edits should be handled with care to avoid disrupting
system-managed files._
