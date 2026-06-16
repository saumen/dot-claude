# Fix Markdown Lint Errors

Fix markdown lint errors in a document by applying formatting rules and running the linter iteratively until zero errors remain.

**Usage:** `/fix-markdown <file-path>`

---

## Arguments

- **$ARGUMENTS**: Path to the markdown file to fix (e.g., `docs/my-document.md`)

---

## Process

### Step 1: Run the Fix Script

Run the automated fix script which handles all common lint errors:

```bash
~/.claude/scripts/fix-markdown.sh "$ARGUMENTS"
```

The script:
1. **Detects config** — walks up the directory tree for `.markdownlint.json`, extracts `MD013.line_length` (defaults to 120)
2. **Prettier** — runs with `--print-width=<line_length>` to fix prose line wrapping
3. **Auto-fixes** — single-pass perl handles MD060, MD040, MD033, MD011, MD024
4. **Loops** — re-lints until clean or 5 iterations max

### Step 2: Check Results

If the script reports remaining errors, they are semantic issues that require manual review:

| Rule | Issue | Fix |
| --- | --- | --- |
| MD051 | Invalid link fragments | Check that anchor targets exist in the document |
| MD056 | Column count mismatch | Ensure all rows have same number of `\|` characters |
| MD058 | No blank line around table | Add blank line before and after each table |
| MD040 | Code block without language | Specify an appropriate language (not just `text`) |

### Step 3: Verify and Report

The linter must return no output (exit code 0) before completion.

Report to the user:

1. The file path that was fixed
2. Summary of fixes applied (e.g., "Fixed 3 MD060 table style errors, 1 MD024 duplicate heading")
3. Confirmation: "Linting complete with zero errors"

---

## Auto-Fix Reference

The script handles these rules automatically:

| Rule | Issue | Fix |
| --- | --- | --- |
| MD060 | Table column style inconsistent | Compact style: single space, no `:---` colons, simple `\| --- \|` delimiters |
| MD024 | Duplicate heading | Appends `(2)`, `(3)`, etc. to make headings unique |
| MD040 | Fenced code block without language | Adds `text` as default language |
| MD033 | Inline HTML | `<br>` → `<br/>` |
| MD011 | Reversed link syntax | Adds space before `[[N]](#sources)` after closing parens |
| MD013 | Line length | Prettier with matching `--print-width` (from `.markdownlint.json`) |

---

## Output Requirements

The fixed document should:

1. Pass `markdownlint` with zero errors
2. Use compact table style with single spaces
3. Have unique headings throughout
4. Have blank lines between all sections and around tables
5. Have consistent column counts in all table rows
