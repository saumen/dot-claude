---
description:
  Converts existing Markdown files into a standardized Obsidian-compatible format with YAML frontmatter and
  Obsidian-specific syntax (wikilinks, callouts, etc.).
when_to_use:
  When you need to format a markdown file for use in Obsidian, or when converting existing notes to include proper
  metadata, tags, and Obsidian-flavored syntax.
---

- **Must be executed by spawning the `swordy-agent-execute` sub-agent.** Do not execute inline.
- **Fallback:** If the `swordy-agent-execute` agent fails twice (stream disconnect or other error), run the workflow
  inline using this skill's steps. Do not retry the agent.

## Workflow

1. **Discovery:** Identify the target file(s) or directory provided by the user.
2. **Documentation Fetch:** Search and fetch the latest Obsidian Markdown guidance (specifically for Wikilinks,
   Callouts, and Properties/Frontmatter) to ensure compliance with the latest Obsidian version.
3. **Normalization (Optional):**
   - If requested, or if the file is identified as containing significant noise/redundancy, invoke
     `swordy-compact-markdown` to clean the content.
   - Ensure the process remains **lossless** regarding the core information.
4. **Metadata Extraction & Generation:**
   - Extract or generate a clean `title` from the filename.
   - Determine relevant `tags` based on the content (see [Obsidian Tagging Specialist](./swordfish-obsidian-tag-reference.md) for specialized logic).
   - Capture current date/time for `created` and `updated` fields.
5. **Transformation (Obsidian Flavor):**
   - Apply the standard Obsidian template:

     ```markdown
     ---
     title: "{{TITLE}}"
     created: { { DATE } }
     updated: { { DATE } }
     tags: [{ { TAGS } }]
     status: processed
     ---

     # {{TITLE}}

     {{CONTENT}}
     ```

   - **Tag Validation:** Ensure all generated tags follow Obsidian's tag rules (e.g., use letters, numbers, hyphens `-`, or forward slashes `/` for nesting; avoid spaces, periods `.`, or other special characters). For more detailed tagging logic, refer to the [Obsidian Tagging Specialist prompt](./swordfish-obsidian-tag-reference.md).
   - Convert standard Markdown links to `[[wikilinks]]` if appropriate for the context.
   - Ensure any admonitions or alerts are converted to Obsidian callout syntax (e.g., `> [!info]`).

6. **Verification:**
   - Confirm that the transformed file contains all original text (lossless check).
   - Verify the YAML frontmatter is valid and the Obsidian-specific syntax is correctly applied.

## Agent Routing

- **Implementation phase:** Must be executed by spawning the `swordy-agent-execute` sub-agent using the Agent tool with
  `subagent_type: swordy-agent-execute`. Do not implement inline.
- **Fallback:** If the `swordy-agent-execute` agent fails twice, run the workflow inline using this skill's steps.

## Parallelization Guidance

Not Applicable. The conversion of individual files is typically handled sequentially by the agent to ensure accuracy and
verification, although multiple files could theoretically be processed in parallel if the agent manages them as a batch.

## Scope

**Use for:**

- Converting standard GFM or plain Markdown files into Obsidian-ready notes.
- Adding structured YAML metadata (tags, dates, titles) to existing notes.
- Updating notes to use Obsidian-specific features like callouts and wikilinks.

**Do NOT use for:**

- General code refactoring.
- Complex document restructuring that changes the meaning of the content.
- Creating entirely new documents from scratch without existing content.

## References

- [Obsidian Flavored Markdown (Official Help)](https://obsidian.md/help/obsidian-flavored-markdown)
- [Obsidian Basic Formatting Syntax](https://obsidian.md/help/syntax)
- [Obsidian Internal Links & Wikilinks](https://github.com/obsidianmd/obsidian-help/blob/master/en/Linking%20notes%20and%20files/Internal%20links.md)
- [Obsidian Tags Rules & Syntax](https://obsidian.md/help/tags)
