---
description: >
  Swordy Git Commit Message: Generate detailed git commit messages with body
  from staged changes. Use when generating a commit message, writing a commit
  message, or crafting a conventional commit message for staged git changes.
when_to_use: Use when generating a commit message, writing a commit message, or crafting a conventional commit message for staged git changes.
---

# Generate Git Commit Message

Analyze staged git changes and generate a clear, concise commit message following best practices.

## Agent Routing

- **Must be executed by spawning the swordy-agent-git-commit-message sub-agent.** Do not execute inline.
- **Fallback:** If the swordy-agent-git-commit-message agent fails twice (stream disconnect or other error), run the workflow inline using this skill's steps. Do not retry the agent.

## Workflow

1. **Analyze staged changes** — Run `git diff --cached` to understand what was modified.
2. **Review recent commits** — Run `git log --oneline -10` to understand the project's commit message style and avoid duplication.
3. **Generate the commit message** following these rules:
   - Use imperative mood (e.g., "Add", "Fix", "Update" — not "Added", "Fixed", "Updated")
   - Keep the subject line under 72 characters
   - Start with a capital letter
   - Do not end with a period
   - Clearly describe the change and its purpose
   - Use conventional commit prefixes when appropriate (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, etc.)

## Parallelization Guidance

Not Applicable. This skill performs a single, sequential task.

## Scope

Not Applicable. The skill's frontmatter description defines when to use it.

## Output Format

Provide only the commit message with no leading whitespace, no code block wrapper, no markdown formatting around the message itself.

### Example output

docs: Update configuration documentation

Add README and project documentation files.
Remove deprecated provider entries and update
docs to match current configuration state.

## Examples

- Add Bank of America checking account plugin
- Fix plugin selection logic for Bank of America files
- Refactor CSV preprocessing to handle amount formatting
- Update test cases to reflect new plugin architecture
- docs: Add plugin development guidelines
