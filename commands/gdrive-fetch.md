# Fetch Google Doc

Download a Google Doc, apply formatting improvements, and store as Obsidian-compatible markdown.

**Usage:** `/fetch-gdoc <google-doc-url>`

---

## Arguments

- **$ARGUMENTS**: The Google Doc URL (e.g., `https://docs.google.com/document/d/FILE_ID/edit`)

---

## Process

### Step 1: Extract File ID

Parse the Google Doc URL to extract the file ID:

- URL format: `https://docs.google.com/document/d/{FILE_ID}/edit`
- Extract the `FILE_ID` portion between `/d/` and the next `/`

### Step 2: Fetch Document

Use the `mcp__gdrive__get_file` tool to retrieve the document content:

```text
mcp__gdrive__get_file(fileId: "{extracted-file-id}")
```

### Step 3: Apply Formatting Improvements

Transform the raw Google Doc content into clean, lint-compliant Obsidian markdown.

#### Table Structure

- Split dense multi-column tables into focused single-purpose tables
- Separate Role/Contact, Dependencies, and Reference tables
- Use markdown reference links at the bottom for URLs: `[link-name]: url`

#### Table Style (MD060 Compliance)

Use compact table style: single space around cell content, empty cells use `| |`, simple `| --- |` delimiters, no alignment colons.

#### Unique Headings (MD024 Compliance)

Ensure all headings are unique. If a heading repeats, add context to differentiate (e.g., "Overview" → "Overview (Implementation)").

#### Section Headers

- Convert inline phase descriptions into proper section headers (`### Phase 1`, etc.)
- Add subheadings for nested content (`#### Subsection`)
- Use step-by-step headers for processes (`##### Step 1: Description`)

#### Lists and Content

- Expand compact bullet points into structured lists with context
- Convert numbered inline items to proper markdown numbered lists
- Add blank lines between sections for readability

#### Images

> **Limitation**: The `mcp__gdrive__get_file` tool only extracts text content from Google Docs. Embedded images are not downloaded and appear as `[Image reference removed]` markers in the raw output. Images must be handled manually.

**Image Handling Process:**

1. When processing the document, identify image markers (e.g., `[image1]`, `[Image reference removed]`)
2. Generate descriptive placeholder filenames based on surrounding context (e.g., `ranking-step-1.png` for a ranking diagram)
3. Convert to Obsidian embed syntax: `![[descriptive-name.png]]`
4. Document all image placeholders in the completion report for manual download

**Manual Download Steps** (user must complete):

1. Open the source Google Doc in a browser
2. Right-click each image and select "Save image as..."
3. Save with the placeholder filename used in the markdown
4. Place the image file in the output directory

#### Consistency

- Standardize terminology across the document
- Remove status emojis from titles (keep in a blockquote if relevant)

### Step 4: Generate Filename

Create the output filename with date prefix:

- Format: `YYYY-MM-DD-{slugified-title}.md`
- Slugify: lowercase, replace spaces with hyphens, remove special characters
- Example: `2026-02-05-prd-home-on-recsys.md`

### Step 5: Save to product-docs

Write the formatted markdown to:

```text
product-docs/{date-prefix}-{slugified-title}.md
```

If `product-docs/` directory doesn't exist, create it in the current working directory.

### Step 6: Lint and Fix Markdown

Run the `/fix-markdown` command on the saved file to fix any remaining lint errors:

```text
/fix-markdown product-docs/{filename}.md
```

This runs `markdownlint`, applies fixes for common issues (MD060 table style, MD024 duplicate headings, MD056 column count, MD058 blank lines), and repeats until zero errors remain.

See `/fix-markdown` for detailed formatting rules and fix procedures.

---

## Output Requirements

The saved document should:

1. Have a clean H1 title (no emojis)
2. Include status as a blockquote if present: `> **Status**: Active`
3. Use proper markdown table syntax with header separators
4. Have consistent heading hierarchy (H2 for main sections, H3+ for subsections)
5. Include reference-style links at the bottom for external URLs
6. Use Obsidian image embeds: `![[filename.png]]`
7. Have blank lines between all sections
8. Pass markdown linting with zero errors (run `markdownlint` to verify)

---

## Example Transformation

**Before (raw Google Doc):**

```text
| Product | John Doe | Dependencies | Team A |
```

**After (formatted, lint-compliant):**

```markdown
## Team & Reference Documents

| Role | Contact |
| --- | --- |
| Product | John Doe |

| Dependency | Team |
| --- | --- |
| Core | Team A |
```

---

## After Completion

Report to the user:

1. The saved file path
2. **Images requiring manual download**: List each placeholder filename with:
   - The placeholder name used (e.g., `ranking-step-1.png`)
   - Context description to help locate the image in the source doc
   - Reminder to download from the source Google Doc and save to `product-docs/`
3. Any external links that were converted to reference-style
4. Linting status: confirm zero errors or list any unresolved issues
