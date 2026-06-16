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
# Extract line_length from .markdownlint.json (default 120)
PRINT_WIDTH=120
if [ -f ".markdownlint.json" ]; then
  # Try to extract line_length from MD013 config; fall back to 120
  PL=$(python3 -c "import json; c=json.load(open('.markdownlint.json')); print(c.get('MD013',{}).get('line_length',120))" 2>/dev/null || echo 120)
  [ -n "$PL" ] && PRINT_WIDTH="$PL"
fi
prettier --write --prose-wrap=always --print-width="$PRINT_WIDTH" "$ARGUMENTS"
```

Prettier automatically handles:
- Line wrapping to fit within print-width (matches `.markdownlint.json` MD013 `line_length`, default 120)
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

#### Table Cell Spacing (MD060)

Prettier does not remove trailing spaces before `|`. Use compact style — single space around cell content:

```bash
# Remove trailing spaces before | in table rows
perl -pi -e 's/ +\|/ |/g' "$ARGUMENTS"
```

#### Table Delimiter Rows (MD060)

Prettier does not fix delimiter rows. Replace padding/alignment with simple dashes:

```bash
# Find delimiter rows with alignment colons
grep -n '^| :.*-.* |$' "$ARGUMENTS"

# Fix: replace with simple | --- | --- | --- | (match column count)
# Example: line 42 has 6 columns
sed -i '' '42s/.*/| --- | --- | --- | --- | --- | --- |/' "$ARGUMENTS"
```

#### Inline HTML (MD033)

Replace `<br>` with `<br/>` or add to allowed_elements in `.markdownlint.json`:

```bash
sed -i '' 's/<br>/<br\/>/g' "$ARGUMENTS"
```

Or update `.markdownlint.json`:
```json
{ "MD033": { "allowed_elements": ["br"] } }
```

#### Reversed Links (MD011)

Add space before `[[N]](#sources)` citations that follow closing parens:

```bash
sed -i '' 's/\)\[\[6\]\](#sources)/) [[6]](#sources)/g' "$ARGUMENTS"
# Repeat for each citation number
```

#### Common Fix Reference

| Rule | Issue | Fix |
| --- | --- | --- |
| MD060 | Table column style inconsistent | Compact style: single space, no `:---` colons, simple `\| --- \|` delimiters |
| MD024 | Duplicate heading | Add context to make headings unique |
| MD056 | Column count mismatch | Ensure all rows have same number of `\|` characters |
| MD058 | No blank line around table | Add blank line before and after each table |
| MD033 | Inline HTML | Use `<br/>` or add to `allowed_elements` in `.markdownlint.json` |
| MD011 | Reversed link syntax | Add space before `[[N]](#sources)` after closing parens |
| MD013 | Line length | Prettier with matching `--print-width` (from `.markdownlint.json`) |

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
