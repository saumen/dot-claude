# GDrive Sync

Sync a Google Doc with its local markdown file (bi-directional, interactive conflict resolution per section).

**Usage:**

```text
/gdrive-sync <local-file-path> [gdrive-url]
```

**Arguments:**

- `<local-file-path>`: Path to the local markdown file (relative to CWD or absolute)
- `[gdrive-url]`: Optional GDrive URL. If omitted, resolved automatically (see Step 1)

---

## Process

### Step 1: Resolve the GDrive URL

Try in this order:

1. **Explicit argument** — use URL provided in the command
2. **Frontmatter** — parse the local file for `**Google doc:**` field (supports `<url>` and `[text](url)` formats)
3. **CLAUDE.md mapping** — look up the file's project-root-relative path in the `## GDrive Mappings` → `### Document Links` table in the nearest `CLAUDE.md`
4. **Error** — if none found, stop and print:
   > "No GDrive URL found. Add a `**Google doc:** <url>` field to the file's frontmatter, or add an entry to CLAUDE.md's GDrive Mappings table."

Extract the **GDrive file ID** from the URL (the segment between `/d/` and the next `/`).

Also extract the **tab fragment** if present in the URL (`?tab=t.xxxxx` → store `t.xxxxx` as `tabFragment`; no `?tab=` → `tabFragment = null`). Tab fragments appear in frontmatter URLs and explicit arguments. Resolution priority for `tabFragment` mirrors the file ID:

1. Explicit URL argument
2. Local file's `**Google doc:**` frontmatter
3. None (`tabFragment = null`)

### Step 2: Fetch the GDoc

Use `mcp__gdrive__get_file(fileId)` with the extracted file ID.

### Step 3: Extract the relevant section

GDocs are often composite — a single file containing multiple logical documents separated by top-level `# H1` headings.

- Read the local file's H1 title (first `# Heading` line)
- Collect all top-level H1 sections from the GDoc content
- Find the matching section(s) by H1 title (case-insensitive, ignoring punctuation differences like escaped `\)`)
- Use `tabFragment` (from Step 1) to disambiguate:
  - **`tabFragment` available, one H1 match**: confirm the match and note it: `"Tab fragment t.xxx available — H1 match confirmed (single candidate)."`
  - **`tabFragment` available, multiple H1 matches**: the tab fragment is a tie-breaker signal — note ambiguity and select the first match, but warn: `"Multiple H1 sections match — tab fragment t.xxx cannot disambiguate programmatically. Verify the correct section was extracted."`
  - **`tabFragment` available, zero H1 matches**: include the tab fragment in the error to help diagnose: `"No H1 section matching '<local title>' found. Tab fragment: t.xxx. Check that the GDoc tab's H1 matches the local file's H1."`
  - **`tabFragment` null**: current behavior — match by H1 title only, no verification note
- Extract only the matched section's content (from its H1 to the next H1 or end of document)
- If no H1 match is found and `tabFragment` is null, treat the entire GDoc content as the relevant section

### Step 4: Load local file and identify structure

- Read the full local markdown file
- Parse both the GDoc section and local file into `##`-level sections (by heading name)
- Classify each section:
  - **Shared section** — heading exists in both GDoc and local → compare content (see Step 6)
  - **GDoc-only section** — heading exists only in GDoc → will be auto-applied to local
  - **Local-only section** — heading exists only in local file → will be preserved verbatim

### Step 5: Link translation (GDrive → local paths)

Read the `## GDrive Mappings` section from the nearest project `CLAUDE.md`:

```text
<!-- gdrive-base: https://docs.google.com/document/d/ -->
<!-- ghe-base: https://code.corp.creditkarma.com/ck-private/ -->
<!-- local-repo-base: /Users/ssealshami/git-repos/ -->
```

And the `### Document Links` table:

```text
| Local Path (project-root-relative) | GDrive ID |
```

For every GDrive URL in the fetched GDoc section:

1. Extract the file ID from the URL
2. Look up the file ID in the Document Links table
3. **Match found** → compute the relative path from the target file's directory to the mapped local file, and replace the GDrive URL with that relative path
4. **No match, but URL is a project document** (same `gdrive-base` domain, document type) → prompt:
   > "GDrive URL `<url>` has no local mapping. What is the local path for this document? (project-root-relative, e.g. `technical-design-doc/foo.md`) Or press Enter to keep as external URL."
   - If local path provided → add entry to CLAUDE.md mapping table, then replace URL with computed relative path
   - If skipped → keep URL as-is (treat as external)
5. **External URL** (Jira, Google Sheets, GHE code links, other teams' GDocs) → keep as-is

**Always preserve** the file's own `**Google doc:**` frontmatter field as a GDrive URL — never replace it with a local path.

### Step 6: Section-level diff

Compare the GDoc content (after link translation) against the local file, section by section. Classify every section with one of four labels:

| Label | Meaning |
| --- | --- |
| `[DIFFERS]` | Shared section — content differs; requires user resolution in Step 7 |
| `[UNCHANGED]` | Shared section — content matches; no action needed |
| `[GDOC-ONLY]` | Heading exists only in GDoc — will be auto-applied to local |
| `[LOCAL]` | Heading exists only in local file — will be preserved verbatim |

Produce a summary:

```text
## Sync diff summary
- [DIFFERS]   ## In Scope          (3 items added/modified)
- [DIFFERS]   ## Launch Plan       (section replaced)
- [UNCHANGED] ## Tech Requirements
- [GDOC-ONLY] ## New Section               (new in GDoc — will apply)
- [LOCAL]     ## TDD Sections (Extracted)  (local-only — will preserve)
- [LOCAL]     ## Related Repositories      (local-only — will preserve)
```

If `--dry-run` flag is passed, print this summary and stop — do not write any files.

### Step 7: Interactive conflict resolution

Process sections sequentially in the order they appear in the GDoc, with local-only sections interleaved at their relative positions.

Per classification:

- **`[UNCHANGED]`** — no action; keep as-is.
- **`[LOCAL]`** — preserve verbatim; no user input needed.
- **`[GDOC-ONLY]`** — auto-insert into local file at the matching position; no user input needed.
- **`[DIFFERS]`** — resolve interactively (see below).

**For each `[DIFFERS]` section**, use `AskUserQuestion` to present:

1. The section heading
2. GDoc version (fenced markdown block)
3. Local version (fenced markdown block)
4. A brief diff summary (lines added / removed / changed)

Then ask: "How should `## <Section>` be resolved?"

Options:

- **1. GDoc wins** — Claude applies the GDoc version to the local file automatically.
- **2. Local wins** — Claude displays the local section content in a fenced block with instructions to paste it into the GDoc; then uses `AskUserQuestion` to confirm the user has updated the GDoc before continuing to the next section.
- **3. Skip** — leave both sides unchanged; do not modify local file or GDoc for this section.

Resolve one section at a time — do not batch. After all `[DIFFERS]` sections are resolved, apply all "GDoc wins" edits to the local file in a single write operation.

**Frontmatter fields** (`**Status**`, `**Author**`) remain GDoc-authoritative — always sync from GDoc without an interactive prompt.

### Step 8: Update mapping and frontmatter

**Mapping** (do this before writing the local file):

- For any newly prompted GDrive → local path mappings from Step 5, add rows to the `### Document Links` table in project `CLAUDE.md`

**Frontmatter** — set `**Last updated**` based on what was synced:

| Outcome | Value |
| --- | --- |
| Only GDoc changes applied to local | `YYYY-MM-DD (synced from GDrive)` |
| Only local changes confirmed pushed to GDoc | `YYYY-MM-DD (synced to GDrive)` |
| Both directions had updates | `YYYY-MM-DD (bi-directional sync)` |
| No shared sections changed | leave unchanged |

### Step 9: Lint

Run `/fix-markdown <local-file-path>` on the updated file.

This applies the project's documentation quality standards automatically.

### Step 10: Report

Print a completion summary:

```text
## Sync complete: <filename>
- Sections updated from GDoc (GDoc wins): N
- Sections pushed to GDoc (local wins, manual): M
- Sections skipped: K
- Sections auto-applied (GDoc-only): J
- Local-only sections preserved: L
- New GDrive mappings added to CLAUDE.md: P
- Last updated: YYYY-MM-DD (<sync direction>)
- Lint: PASSED (0 errors) | ISSUES: <list>
```

---

## Rules to Apply

### From `~/.claude/CLAUDE.md` (global)

- Use `/opt/homebrew/bin/markdownlint` directly — never `npx markdownlint-cli2`

### From `~/.claude/rules/markdown-linting.mdc`

- **Table style (MD060)**: compact — single space around content, simple `| --- |` delimiters, no alignment colons
- **Table column count (MD056)**: all rows must have same number of columns
- **Table spacing (MD058)**: blank line before and after every table
- **Headings (MD024)**: all headings must be unique; add context to differentiate if needed
- **Headings (MD003)**: ATX-style only (`##`), no skipped levels
- **Code blocks**: every fenced block must have a language tag (` ```text `, ` ```scala `, etc.)
- **Trailing spaces**: none allowed

### From `~/.claude/rules/documentation-authoring.mdc`

- **Table width**: keep narrow; move long cell content to footnotes below the table
- **Footnote style**: numbered `[1]` when table has no index column; lettered `[a]` when it does
- **Multi-byte char padding**: add one extra trailing space per `→` or `×` in a table cell (MD060 alignment)
- **Code references**: use stable symbol names, not line numbers
- **Deduplication**: before finalizing, scan for repeated content — remove or cross-reference the canonical location

### From project `CLAUDE.md` (Documentation Quality Standards)

- All files in `technical-design-doc/` must pass markdownlint with zero errors
- Use `/fix-markdown <path>` for lint + auto-fix

---

## GDrive Mappings Format Reference

The `## GDrive Mappings` section in project `CLAUDE.md` follows this format:

```markdown
## GDrive Mappings

<!-- gdrive-base: https://docs.google.com/document/d/ -->
<!-- ghe-base: https://code.corp.creditkarma.com/ck-private/ -->
<!-- local-repo-base: /Users/ssealshami/git-repos/ -->

### Document Links

| Local Path (project-root-relative) | GDrive ID |
| --- | --- |
| technical-design-doc/boulder-2-milestone-2/tdd-boulder2-milestone2-betterbox.md | 1ZD6OwOszs_cM_8OrqEiz4D3GrnuQzpmV_FA39hDoQZQ |
```

- **GDrive ID**: the file ID from the URL (between `/d/` and the next `/`). Tab fragments (`?tab=...`) are not stored — the file ID alone uniquely identifies the GDoc file. Multiple local files can map to the same GDrive file ID (composite docs with multiple tabs).
- **Local path**: project-root-relative (relative to directory containing `CLAUDE.md`). When writing links into local files, compute the relative path from that file's directory to this path.
- **Repository paths**: not stored in the table. Derived on the fly: `local-repo-base` + repo name = full local path; `ghe-base` + repo name = full remote URL.
