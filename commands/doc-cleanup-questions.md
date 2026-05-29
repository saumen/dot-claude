# Cleanup Open Questions

Blend resolved questions into the body of a document and clean up the open questions section to contain only genuinely unresolved items.

**Usage:** `/cleanup-open-questions <file-path>`

---

## Arguments

- **$ARGUMENTS**: Path to the document containing an open questions section (e.g., `docs/design-doc.md`)

---

## Process

### Step 1: Read the Document

Read the full document and locate the open questions section. This is typically a table with columns like `#`, `Question`, `Answer`/`Notes`, and `Status` — but adapt to whatever format is used.

Identify:

- **Resolved questions**: Questions marked as "Resolved", "Closed", "Done", or that have definitive answers
- **Open questions**: Questions marked as "Open", "TBD", "Pending", or that lack definitive answers

### Step 2: Blend Resolved Questions

For each resolved question, determine where its answer belongs in the document body:

| Answer Type | Blend Strategy |
| --- | --- |
| Field behavior or value | Add to the relevant field's description/notes in the domain model or mapping table |
| Design decision | Add as a callout, note, or inline statement in the relevant section |
| Scope clarification | Add to scope, assumptions, or responsibility boundary sections |
| Implementation detail | Add to the relevant technical section (e.g., processing steps, mapping logic) |
| Already captured | Skip — the answer is already reflected in the document body |

**Rules:**

- Keep blended content concise — a clause or sentence, not a paragraph
- Match the tone and format of the surrounding content
- Do not add a "Resolved from Q#" attribution — the answer should read as native content
- If an answer is already fully captured in the document body, skip it (no redundant additions)

### Step 3: Rebuild the Open Questions Section

Replace the existing open questions section with only the genuinely unresolved items:

- Renumber sequentially starting from 1
- Remove the `Status` column (all remaining items are open by definition)
- Keep `#`, `Question`, and `Notes` columns (or equivalent)
- If a question is partially resolved (e.g., decision made but implementation approach TBD), keep it with updated notes reflecting what's resolved and what remains

### Step 4: Handle Edge Cases

| Scenario | Action |
| --- | --- |
| All questions resolved | Remove the open questions section entirely, or replace with "No open questions." |
| Question references removed content | Drop the question (it's no longer relevant) |
| Answer contradicts document body | Flag to the user — do not silently resolve the conflict |
| Question is resolved but spawns a new question | Add the new question as an open item |

### Step 5: Verify Consistency

After edits, scan the document for:

- References to old question numbers (e.g., "see Q7") that need updating to new numbering
- Sections that reference the open questions table and need adjustment
- Callouts or notes that say "see §8 Q{N}" — update to new question numbers or replace with inline content

### Step 6: Report

Summarize changes to the user:

1. How many questions were resolved vs remain open
2. Where resolved answers were blended (section references)
3. Any conflicts or items flagged for review

---

## Output Requirements

The updated document should:

1. Have no resolved questions in the open questions section
2. Have resolved answers blended naturally into the document body
3. Have open questions renumbered sequentially
4. Have no stale cross-references to old question numbers
