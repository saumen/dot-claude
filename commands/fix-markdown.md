# Fix Markdown Lint Errors

Fix markdown lint errors in a document by applying formatting rules and running the linter iteratively until zero errors remain.

**Usage:** `/fix-markdown <file-path>`

---

## Arguments

- **$ARGUMENTS**: Path to the markdown file to fix (e.g., `docs/my-document.md`)

---

## Process

### Step 1: Run Initial Lint Check

Run the markdown linter to identify errors:

```bash
markdownlint "$ARGUMENTS"
```

If no errors are reported (exit code 0), the file is already compliant. Report success and exit.

### Step 2: Apply Formatting with Prettier

Use Prettier to automatically fix markdown formatting and line lengths:

```bash
# Check for project .markdownlint.json configuration
if [ -f ".markdownlint.json" ]; then
  prettier --write --prose-wrap=always "$ARGUMENTS"
else
  prettier --write --prose-wrap=always --print-width=120 "$ARGUMENTS"
fi
```

Prettier automatically handles:
- Line wrapping to fit within print-width (default 80 chars)
- Table formatting consistency
- Spacing around headings and lists
- Code block preservation

### Step 2b: Manual Fixes for Remaining Issues

For any errors not fixed by Prettier, apply the appropriate fix based on the rule:

#### Table Style (MD060 Compliance)

Use **compact table style** consistently:

- Single space around all cell content: `| content |`
- Empty cells must have a space: `| |` (not `||`)
- Simple delimiter row: `| --- | --- |`
- No alignment colons (`:---`) - they cause style inconsistency

**Correct:**

```markdown
| Role | Contact |
| --- | --- |
| Product | John Doe |
| Engineering | Jane Smith |
| | Additional contact |
| Support | |
```

**Incorrect:**

```markdown
| Role           | Contact    |   <- aligned padding
| :------------- | :--------- |   <- alignment colons
| Engineering    ||                <- missing space in empty cell
```

#### Unique Headings (MD024 Compliance)

Ensure all headings are unique within the document:

- If a heading repeats, add context to differentiate
- Example: "Overview" appearing twice → rename to "## Overview" and "## Overview (Implementation)"

#### Table Structure (MD056 Compliance)

Ensure all rows have the same number of columns:

- Count `|` characters in header row
- Ensure all data rows match that count
- Add empty cells `| |` if needed to balance columns

#### Blank Lines Around Tables (MD058 Compliance)

Add blank lines before and after each table:

```markdown
Some text here.

| Header | Header |
| --- | --- |
| Data | Data |

More text here.
```

#### Common Fix Reference

| Rule | Issue | Fix |
| --- | --- | --- |
| MD060 | Table column style inconsistent | Ensure all cells use `\| content \|` with single space; empty cells use `\| \|` |
| MD024 | Duplicate heading | Add context to make headings unique |
| MD056 | Column count mismatch | Ensure all rows have same number of `\|` characters |
| MD058 | No blank line around table | Add blank line before and after each table |

### Step 3: Re-run Linter

After applying fixes, run the linter again:

```bash
markdownlint "$ARGUMENTS"
```

If errors remain, return to Step 2 and fix them. Repeat until zero errors.

### Step 4: Verify and Report

The linter must return no output (exit code 0) before completion.

Report to the user:

1. The file path that was fixed
2. Summary of fixes applied (e.g., "Fixed 3 MD060 table style errors, 1 MD024 duplicate heading")
3. Confirmation: "Linting complete with zero errors"

---

## Output Requirements

The fixed document should:

1. Pass `markdownlint` with zero errors
2. Use compact table style with single spaces
3. Have unique headings throughout
4. Have blank lines between all sections and around tables
5. Have consistent column counts in all table rows
