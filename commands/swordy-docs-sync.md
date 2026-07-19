---
name: swordy-docs-sync
description: Create or update README.md and AGENTS.md for the current working directory. README targets humans (usage, manual). AGENTS.md targets AI agents (technical details, structure, conventions). Links back to README.md. Refactors via swordy-refactor-docs.md if principles violated. Verifies via swordy-verify-docs.md.
disable-model-invocation: true
argument-hint: "[no args — runs against current working directory]"
---
---
> **⚠️ DEPRECATED**: This command has been replaced by `swordy-docs-sync-inline.md`.
>
> **Why?** The inline version eliminates sub-agent delegation overhead, runs entirely in the current session, and adapts to different harness environments (omp vs standard).
>
> **Migration**: Use `/swordy-docs-sync-inline` instead. All functionality is preserved with improved efficiency and harness-agnostic operation.
> ---

# Sync README.md and AGENTS.md

Create or update `README.md` and `AGENTS.md` in the **current working directory**. Both must reflect the actual current state of the project at runtime.

## Core Principle — Audience Separation

| File | Audience | Content Focus |
|---|---|---|
| `README.md` | Humans (end users, contributors) | Setup, usage, workflow, concepts, manual-style guidance |
| `AGENTS.md` (this file) | AI agents & developers | Project structure, technical conventions, build/test commands, file-purpose map, links to README.md |

**Rule:** If content belongs to user-facing guide (setup, usage), it goes in README. If it's developer/AI guidance (standards, conventions, structure, commands), it goes here. Planning docs stay in `docs/plans/`. Never duplicate content across both files — cross-reference instead.

## Prerequisites

Resolve path aliases before any operation:

| Alias | Full Path |
|---|---|
| `$REFAC` | `/Users/swordfish/.claude/commands/swordy-refactor-docs.md` |
| `$VERIFY` | `/Users/swordfish/.claude/commands/swordy-verify-docs.md` |

Read both reference prompts before starting. They contain the detailed workflows for refactoring and verification.

---

## Phase 1 — Inventory Current State

Scan the working directory to understand what exists:

1. **Directory tree** — Run `find . -maxdepth 3 -not -path './.git/*' -not -path '*/node_modules/*' -not -path '*/__pycache__/*' | head -80` to get the structure.
2. **Existing files** — Check if `README.md` and `AGENTS.md` already exist. Read them if they do.
3. **Key artifacts** — Identify: scripts, configs, source dirs, docs/, tests/, package manifests, Makefiles, Dockerfiles, etc.
4. **Dependencies** — Note package files (`package.json`, `requirements.txt`, `Cargo.toml`, `go.mod`, etc.) and their purpose.

Report the inventory summary before proceeding.

---

## Phase 2 — Audit Existing Docs Against Principles

If either file exists, audit it against the audience separation principle:

### README.md Audit

- Does it contain AI/developer-specific content (conventions, commit rules, code structure details)? → **VIOLATION**
- Does it capture setup, usage, workflow, and conceptual guidance? → **CORRECT**
- Is it oriented toward humans who need to understand how to use the project? → **CORRECT**

### AGENTS.md Audit

- Does it contain user-facing setup/usage instructions that belong in README? → **VIOLATION**
- Does it capture technical structure, conventions, commands, and file-purpose mapping? → **CORRECT**
- Does it link to `README.md` for human-oriented content? → **CORRECT**

### If EITHER violation is found

1. **Delegate** to a sub-agent for the refactoring workflow (saves context window):
   Use the `Agent` tool with `subagent_type: swordy-agent-execute`:
   ```
   Agent({ subagent_type: "swordy-agent-execute", prompt: "Read /Users/swordfish/.claude/commands/swordy-refactor-docs.md and execute its Phase 0-5 loop on README.md and AGENTS.md in the current working directory" })
   ```

2. Use the existing files as input — the refactoring tool will extract, reorganize, and redistribute content losslessly.
3. After the subagent completes and returns the refactored files, read the updated files to confirm changes.
4. Proceed to Phase 3 with the new file contents.

### If NO violations found

Proceed directly to Phase 3. The existing structure is sound; you will refine and update it.

---

## Phase 3 — Generate README.md (Human-Oriented)

Write or update `README.md` following this structure:

```markdown
# <Project Name>

<Brief one-line description of what the project does. No fluff.>

## Setup

<How to get running: clone, install deps, env setup. Step-by-step commands.>

## Usage

<How to use the project: main workflow, scripts, commands. What inputs/outputs.>

## Expected Workspace Structure

<Directory layout with comments explaining each directory's purpose.>

## <Feature-Specific Sections>

<Per-feature usage sections as needed — one per major capability.>

---

_Note: This directory is managed by the docs-sync prompt. Manual edits should be handled with care to avoid disrupting system-managed files._
```

**Guidelines:**

- Write in clear, imperative prose. Assume a human reader who needs to understand and use the project.
- Include setup commands (shell commands, env vars, config files).
- Describe the workflow end-to-end: input → process → output.
- Document directory layout with explanations.
- Cover major features/capabilities with their own sections.
- **Do NOT** include: commit conventions, code structure details, agent-specific instructions, testing commands (unless they're part of user workflow), file-purpose tables for developers.
- If the project has no clear "usage" (e.g., it's a config-only project), adapt accordingly — describe what each component does and how to configure/use it.

---

## Phase 4 — Generate AGENTS.md (AI/Developer-Oriented)

Write or update `AGENTS.md` following this structure:

```markdown
# <Project Name> — Repository Guidelines

## Documentation & File Purposes

This project uses multiple markdown files, each with a distinct audience and scope. Do not duplicate content across them.

| File | Audience | Scope |
|---|---|---|
| [`README.md`](README.md) | End users | Setup, workspace layout, workflow, feature usage |
| `AGENTS.md` (this file) | Developers & AI assistants | Project structure, testing commands, commit conventions, development guidance |
| [`.editorconfig`](.editorconfig) | All developers | Indentation, hard wrap, trailing newline rules for every file (include only if present) |
| `docs/plans/*.md` | Implementation tracking | Planning documents with TODO lists — no implementation snippets |
| [`PYTHON_GUIDELINES.md`](PYTHON_GUIDELINES.md) | Python contributors | Coding standards for Python scripts (include only if present) |
| [`SHELL_SCRIPTING_GUIDELINES.md`](SHELL_SCRIPTING_GUIDELINES.md) | Shell script contributors | Standards for shell scripting in the project (include only if present) |

**Rule:** If content belongs to a user-facing guide (setup, usage), it goes in README. If it's developer/AI guidance (standards, conventions, structure), it goes here or in the dedicated guideline files linked above. Planning docs stay in `docs/plans/`.

## Project Structure & Module Organization

<Directory tree showing actual project layout with comments explaining each component.>

## Build, Test, and Development Commands

| Command | Purpose |
|---|---|
| `<command>` | <What it does> |
| ... | ... |

### <Context-Specific Notes>

<Any important caveats about commands — e.g., "use python3 from conda env".>

## Commit & Pull Request Guidelines

- Use conventional commit prefixes (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`). Imperative mood, subject line under 72 characters, no trailing period.
- Example: `feat: Add <feature>`
- PRs should include a clear description, link related issues, and note any environment variable changes.

## Documentation & Planning

<Links to relevant docs, plans, specs, skills.>

## Agent-Specific Instructions

<Technical instructions for AI agents — what to read before modifying code, patterns to follow, etc.>

## <Domain-Specific Guidelines>

<Per-module or per-skill development guidelines as needed.>
```

**Guidelines:**

- Include a file-purpose table mapping every markdown/doc file in the project to its audience and scope.
- Provide an actual directory tree (not abstract — the real structure).
- List all build/test/development commands with purposes.
- Document commit conventions and PR guidelines.
- Link to relevant documentation, specs, plans, and skills.
- Include agent-specific technical instructions (what to read before modifying code, patterns to follow).
- **Do NOT** include: user-facing setup instructions, usage workflows, conceptual explanations that belong in README.

---

## Phase 5 — Cross-Reference Verification

Before writing files, ensure:

1. `AGENTS.md` links to `README.md` (at minimum in the file-purpose table).
2. No content appears in both files (cross-reference instead of duplicating).
3. Every section in README has a corresponding entry in AGENTS.md's file-purpose table if it's a document file.
4. The directory tree in AGENTS.md matches the actual filesystem.

---

## Phase 6 — Write Files

Write both files to disk. Use `write` tool for new files, `edit` for updates.

After writing, confirm:

- `README.md`: human-oriented, usage/manual focus ✓
- `AGENTS.md`: AI/developer-oriented, technical focus + links to README ✓
- No cross-contamination of content between the two files ✓

---

## Phase 7 — Verify with $VERIFY

**Delegate** the verification workflow to subagents (saves context window, each audit is iterative and heavy):

1. **Verify README.md**:
   Use the `Agent` tool with `subagent_type: swordy-agent-reviewer`:
   ```
   Agent({ subagent_type: "swordy-agent-reviewer", prompt: "Read /Users/swordfish/.claude/commands/swordy-verify-docs.md and execute its full audit→fix→re-audit loop on README.md in $(pwd)" })
   ```

2. **Verify AGENTS.md**:
   Use the `Agent` tool with `subagent_type: swordy-agent-reviewer`:
   ```
   Agent({ subagent_type: "swordy-agent-reviewer", prompt: "Read /Users/swordfish/.claude/commands/swordy-verify-docs.md and execute its full audit→fix→re-audit loop on AGENTS.md in $(pwd)" })
   ```

3. Read both subagent outputs. If either reports P0 or P1 findings:
   - Apply the recommended fixes to the affected file(s) from the subagent's output.
   - Re-delegate verification for that specific file until factual accuracy reaches 100% (max 5 iterations per file).
4. If both subagents report 0 P0 and 0 P1 findings, proceed to Phase 8.

---

## Phase 8 — Final Report

Produce a summary of what was created/updated:

```markdown
## Docs Sync Report

| File | Action | Lines | Key Sections |
|---|---|---|---|
| `README.md` | Created/Updated | N | Setup, Usage, Features |
| `AGENTS.md` | Created/Updated | N | Structure, Commands, Conventions |

### Verification Results

- README.md: P0=0, P1=0, P2=N, P3=N — accuracy X%
- AGENTS.md: P0=0, P1=0, P2=N, P3=N — accuracy X%

### Refactoring Applied

- [ ] Audience separation violations found and refactored via `$REFAC`
- [ ] No violations — files were already well-separated
```
