---
name: "swordy-fix-markdown"
description: >
  Swordy Fix Markdown: Fix markdown lint errors in documents by running
  prettier, markdownlint, and automated Python-based fixes iteratively until
  zero errors remain. Use when fixing markdown lint errors, running the
  fix-markdown workflow, or cleaning up a document's lint issues.
when_to_use: >
  Use when fixing markdown lint errors, running the fix-markdown workflow on
  a file, or cleaning up a document's lint issues. Triggers on requests like
  "fix markdown lint errors", "run fix-markdown on this file", "clean up lint
  issues", or "make this pass markdownlint".
---

## Workflow

1. **Validate input:** Check that the target markdown file exists. If not, report the error and stop.

2. **Run the bundled fix script:** Execute the fix script which handles all common lint errors:

   ```bash
   ~/.claude/skills/swordy-fix-markdown/scripts/fix-markdown.sh "$FILE"
   ```

   The script:
   - Detects config — walks up the directory tree for `.markdownlint.json`, extracts `MD013.line_length` (defaults to 120)
   - Prettier — runs with `--print-width=<line_length>` to fix prose line wrapping
   - Auto-fixes — single-pass Python handles MD060, MD033, MD011, MD024 (MD040 skipped — user must specify language)
   - Loops — re-lints until clean or 5 iterations max

3. **Check results:** If the script reports remaining errors, they are semantic issues that require manual review:

   | Rule | Issue | Fix |
   | --- | --- | --- |
   | MD051 | Invalid link fragments | Check that anchor targets exist in the document |
   | MD056 | Column count mismatch | Ensure all rows have same number of `\|` characters |
   | MD058 | No blank line around table | Add blank line before and after each table |
   | MD040 | Code block without language | Skipped by auto-fix — user must specify appropriate language (not just `text`) |

4. **Verify and report:** The linter must return no output (exit code 0) before completion.

   Report to the user:
   - The file path that was fixed
   - Summary of fixes applied (e.g., "Fixed 3 MD060 table style errors, 1 MD024 duplicate heading")
   - Confirmation: "Linting complete with zero errors"

## Execution

The workflow runs inline directly — no sub-agent required. The bundled `fix-markdown.sh` script handles all
automation: prettier wrapping, iterative lint-fix cycles, and zero-error verification.
## Scope

**Use for:**

- Fixing markdown lint errors in a document.
- Running the fix-markdown workflow on a single file.
- Cleaning up a document's lint issues (MD013, MD060, MD033, MD011, MD024).
- Making a markdown file pass `markdownlint` with zero errors.

**Do NOT use for:**

- General markdown editing or content creation (use a text editor or general-purpose agent).
- Compacting documents to reduce line count (use `swordy-compact-markdown`).
- Converting markdown to Obsidian format (use `swordy-obsidian-format`).
- Formatting markdown for Obsidian (use `swordy-obsidian-format`).
