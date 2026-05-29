---
description: >
  Swordy Markdown Compactor: Compact markdown documents to under 200 lines in a lossless way.
  Evaluates examples (retain/discard/compact), removes duplication and repetitive content, and asks user about conflicts.
  Use when the user wants to compact a markdown file, reduce the size of a long document, make a markdown file shorter, or trim repetitive content.
  Triggers on requests like 'compact this markdown', 'reduce this doc to under 200 lines', 'trim this document', 'make this shorter', 'condense the markdown'.
when_to_use: Use when the user wants to compact a markdown file, reduce the size of a long document, make a markdown file shorter, or trim repetitive content. Triggers on requests like "compact this markdown", "reduce this doc to under 200 lines", "trim this document", "make this shorter", "condense the markdown".
---

# Markdown Compactor

Compact markdown documents to under 200 lines while preserving all essential information.

## Agent Routing

- **Must be executed by spawning the swordy-agent-markdown-compact sub-agent using the Agent tool with subagent_type: swordy-agent-markdown-compact. Do not execute inline.**
- **Fallback:** If the markdown-compact agent fails twice (stream disconnect or other error), run the workflow inline using this skill's steps. Do not retry the agent.

## Workflow

### 1. Input
- Accept a markdown file path from the user. If none provided, ask for one.

### 2. Check line count
- Count the total lines. If < 200, report the document is already compact and stop.

### 3. Analyze structure
- Parse the document:
  - Identify top-level and nested sections (headings)
  - Catalog all examples, code blocks, and reference links
  - Flag sections with high repetition or overlapping content

### 4. Classify examples
- For each example or code snippet, assign one of three categories:
  - **Retain**: Critical, unique, or illustrative examples that serve a distinct purpose
  - **Discard**: Redundant examples that duplicate information already covered
  - **Compact**: Examples that can be merged, simplified, or represented more concisely

### 5. Draft compacted document
- Apply the classifications:
  - Remove discarded content entirely
  - Merge/rewrite compacted examples into fewer, clearer lines
  - Preserve all retained content verbatim
  - Track line count after each modification

### 6. Review against target
- If the draft is still >= 200 lines, repeat compaction on the least-critical remaining content until the target is met.

### 7. Identify conflicts
- Flag any cases where:
  - Two sections are nearly identical but cover different use cases
  - Removing content would lose domain-specific nuance
  - The user must choose between competing interpretations
  Present each conflict to the user with options and recommended resolution.

### 8. Finalize
- After resolving all conflicts, output the compacted document and report:
  - Original line count
  - Final line count
  - Number of examples retained / discarded / compacted
  - Number of conflicts resolved

## Parallelization Guidance

Not Applicable. Markdown compaction is a sequential process.

## Scope

Not Applicable. The skill's frontmatter description defines when to use it.
