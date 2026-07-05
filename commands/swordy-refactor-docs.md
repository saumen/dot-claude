---
name: swordy-refactor-docs
description: Refactor markdown docs into smaller files with iterative audit. Extracts content into well-organized files with lossless, non-overlapping, unique, and link-valid guarantees.
disable-model-invocation: true
---

# Refactor documentation files

Extract content into smaller, well-organized files. Execute the following loop until ALL checks pass (lossless,
non-overlapping, unique, links valid). Do NOT stop after a single pass — iterate until the audit reports zero findings.

## Input

The user provides natural language describing what to refactor. Determine the following from the conversation:

- **Source file(s)**: The file(s) the user wants refactored — inferred from the conversation context.
- **Target directory**: Where extracted files should go — default to a `docs/` subdirectory next to the source, unless
  the user specifies otherwise.
- **Extraction plan**: Determine from source structure which sections belong in which target files. Group by logical
  topic (e.g., per-component, per-module, per-feature).

## Pre-Flight Assessment

Before creating the plan, assess whether extraction is warranted:

1. Count total lines of the source file(s).
2. Count distinct sections with clear topic boundaries.
3. **Skip extraction** (report and stop) if:
   - Source file is under 200 lines of content, OR
   - Fewer than 3 sections are independently extractable, OR
   - No single section exceeds 30 lines of substantive content
4. If extraction is warranted, proceed to Phase 0.

Report your assessment: `Source: N lines, M extractable sections → extraction warranted: yes/no`.

## Workflow — Iterative Loop

Run these phases in order. After Phase 4, if ANY check failed, go back to Phase 3 (Fix) and iterate. Repeat until Phase
4 reports all green.

**MAX_ITERATIONS**: 5. If all 4 checks have not passed after 5 iterations:

1. Stop the fix loop.
2. Go back to Phase 0 and revise the extraction boundaries (some sections may need to stay together, or be split
   differently).
3. Reset the iteration counter and resume from Phase 1.
4. If re-planning also fails to converge after a second round of 5 iterations, present the current state to the user
   with the remaining failures and recommended resolutions.

**CRITICAL**: At the start of every phase, re-read the plan file to ground yourself in the current state. The plan file
is your source of truth — do not rely on memory or context window alone.

### Phase 0 — Create Plan (persist to disk)

Before any extraction, create a plan document at `TARGET_DIR/plan.md`. This file is your authoritative reference for the
entire workflow. Write it immediately and update it after every phase.

The plan file must contain:

````markdown
# Refactoring Plan

## Objectives

- [ ] Extract [section/topic] from [source file] → [target file]
- [ ] Extract [section/topic] from [source file] → [target file]
- [ ] ... (one per planned extraction)

## Extraction Map

| Source Section | Lines | Target File | Status |
| --- | --- | --- | --- |
| [section name] | [start-end] | [target.md] | planned / done |
| ... | ... | ... | ... |

## Verification Checklist

### Lossless (original vs draft + extracted)

- [ ] All removed lines from diff accounted for in extracted files
- [ ] All URLs from original present in draft + extracted combined
- [ ] No factual content lost (data, explanations, rationale)

### Non-overlapping (draft vs extracted)

- [ ] No content lines duplicated between draft and any extracted file
- [ ] Only structural lines (empty, `---`, ` ``` `) shared

### Unique across files (extracted vs extracted)

- [ ] No content lines duplicated between any pair of extracted files
- [ ] Source reference sections contain only topic-relevant links

### Links

- [ ] All internal links in draft resolve to existing files
- [ ] All internal links in extracted files resolve to existing files

## Shared Content Registry

Content intentionally kept in multiple files (excluded from overlap checks):

| Content | Files | Reason |
| --- | --- | --- |
| [e.g., glossary terms] | [fileA, fileB] | [each file needs standalone readability] |

Leave empty if no shared content is needed.

## Iteration Log

| Iteration | Date | Changes | Findings (L/N/U/Lk) | Checks |
| --- | --- | --- | --- | --- |
| 1 | [date] | Initial extraction | L:3 N:5 U:2 Lk:1 | L:FAIL N:FAIL U:FAIL Lk:FAIL |
| 2 | [date] | Fixed overlaps in X | L:0 N:2 U:0 Lk:0 | L:PASS N:FAIL U:PASS Lk:PASS |

Findings column = count of individual issues per check (tracks convergence toward zero).
````

**Rules for the plan file:**

- Update the Status column after each extraction
- Check off verification items as they pass
- Log every iteration with what changed, findings count, and check results
- Re-read this file at the start of every phase
- After iteration 3+, compact older iterations into a single "iterations 1-N: summary" row to keep the plan under 100
  lines

### Phase 1 — Extract (to draft)

#### Extraction Heuristics

Extract a section if it meets **at least 2** of these criteria:

- More than 30 lines of substantive content
- References 3 or more distinct sub-topics
- Would be useful as a standalone document
- Is referenced from 2 or more other sections

Do **NOT** extract if:

- Section is fewer than 10 lines
- Removing it breaks the narrative flow of the parent document
- Content is intrinsically cross-cutting (glossary, index, table of contents)

#### File Naming Convention

- Use `kebab-case`: `topic-name.md`
- Prefix with category when multiple categories exist: `api-auth.md`, `api-data.md`
- Avoid generic names: `readme.md`, `info.md`, `details.md`
- Include parent context if ambiguous: `parent-child-topic.md`

#### Content Type Rules

Handle these content types with care during extraction:

- **YAML frontmatter**: Keep in the source file. Extracted files may have their own frontmatter if needed, but do not
  split a single frontmatter block.
- **Code blocks**: Extract with their surrounding explanatory text. Do not orphan a code block from its description.
- **Callouts/admonitions** (`> [!NOTE]`): If a callout spans multiple topics, keep it where it is most relevant and add
  a cross-reference in other files.
- **Math blocks** (`$$...$$`): Keep with the section that defines the variables they reference.
- **Mermaid diagrams**: Keep with the section they illustrate. If referenced from multiple sections, keep canonical copy
  in one file and link from others.

#### Extraction Steps

1. Read the full source file(s).
2. Identify extractable sections using the heuristics above.
3. Write a **draft** of the modified source to a temporary file (e.g. `SOURCE.draft` or `SOURCE.refactored.md`). **Do
   NOT overwrite the original yet.**
4. Create target files in the target directory following the naming convention. Each file should contain ONLY content
   specific to that topic — no tables, data, lists, or source links that also appear elsewhere.
5. In the draft, replace extracted content with:
   - A brief cross-reference sentence (e.g. "See per-topic docs for details:")
   - Links to the extracted files (e.g. `- [Topic](./docs/topic.md)`)
6. **Do NOT duplicate** any content block (table, bullet list, paragraph) between draft and extracted files. If a table
   has rows for multiple topics, split it: keep only the overview/summary in the draft, move full details to extracted
   files.
7. Update the plan file: mark extraction map rows as `done` and add an iteration log entry with findings counts.

### Phase 2 — Audit

Run each check independently. Report findings as a structured list.

#### 2A — Lossless Check (before vs. after)

Compare the **original** source against the combined content of the **draft** + all extracted files. The original must
remain untouched until all checks pass.

- Extract all removed lines: `diff ORIGINAL DRAFT | grep '^<' | grep -v '^<---'` (or `git diff ORIGINAL DRAFT`).
- For each removed content block, verify its factual content exists in at least one extracted file.
- Check all URLs preserved:
  `comm -23 <(grep -oE 'https?://[^ )]+' ORIGINAL | sort -u)
  <(cat DRAFT TARGET_DIR/*.md | grep -oE 'https?://[^ )]+' | sort -u)`
  — must be empty (no URLs lost).
- **PASS** if every removed fact is preserved somewhere. Format changes (table → per-file sections) are acceptable as
  long as no information is lost.
- **FAIL** if any factual content (data, explanations, source links, rationale) is missing from the combined output.

#### 2B — Non-overlapping Check (draft vs. extracted)

- Find exact line duplicates:
  `comm -12 <(grep -v '^$' DRAFT | grep -v '^---$' | grep -v '^```' | sort -u)
  <(cat TARGET_DIR/*.md | grep -v '^$' | grep -v '^---$' | grep -v '^```' | sort -u)`
  — count non-structural duplicates.
- **Exclude** any lines registered in the plan's Shared Content Registry.
- **PASS** if duplicate lines are only structural (empty lines, `---`, ` ``` `). Content lines (table rows, bullet
  points, paragraphs) must NOT appear in both draft and extracted files.
- **FAIL** if any content line is duplicated. Common failures: data tables, bullet lists, configuration instructions,
  source reference links.

#### 2C — Unique Across Files Check (extracted vs. extracted)

- For every pair of extracted files:
  `comm -12 <(grep -v '^$' TARGET_DIR/fileA.md | grep -v '^---$' | grep -v '^```' | sort -u)
  <(grep -v '^$' TARGET_DIR/fileB.md | grep -v '^---$' | grep -v '^```' | sort -u)`
- Also check triple overlap: `comm -12 <(comm -12 <(sort -u fileA) <(sort -u fileB)) <(sort -u fileC)` — use
  content-filtered versions (no structural lines).
- **PASS** if shared lines are only structural headers/formatting that are necessary for each file to be independently
  readable (e.g. `## Sources`). Even then, minimize — only keep headers each file actually needs.
- **FAIL** if substantive content (source links, data, explanations) is repeated across files. Source reference sections
  are the most common offender — each file should only include sources relevant to its topic, not the full shared set.

#### 2D — Link Audit

- Find all internal links in draft: `grep -noE '\]\([^)]*\.[a-zA-Z]' DRAFT`
- For each link target, verify the file exists relative to the draft's directory:
  `test -f "$(dirname DRAFT)/LINK_TARGET"`
- Check links in extracted files too: `grep -rnoE '\]\([^)]*\.[a-zA-Z]' TARGET_DIR/`
- **PASS** if all internal links resolve to existing files.
- **FAIL** if any link points to a non-existent path. Common failure: linking `./topic.md` when the file is actually at
  `./docs/topic.md`.

### Phase 3 — Fix

For every FAIL from Phase 2, fix the **draft** and/or extracted files. The original source remains untouched.

#### Error Priority Classification

Fix issues in this order — higher priority first:

| Priority | Check | Impact | Example |
| --- | --- | --- | --- |
| **P0 (block)** | Lossless gaps | Factual content lost | Data table row missing from all files |
| **P1 (major)** | Broken links | Navigation broken | `./topic.md` doesn't exist |
| **P2 (minor)** | Overlaps / cross-file dup | Redundant but not wrong | Same source link in 3 files |
| **P3 (style)** | Header duplication | Cosmetic | `## Sources` in every file |

Do not spend iterations fixing P3 issues while P0/P1 remain.

#### Fix Strategies

- **Lossless gap (P0)**: Add the missing content to the appropriate extracted file. If it belongs to multiple topics,
  put it in the most relevant one and reference from others.
- **Broken links (P1)**: Fix the path in the link to match the actual file location. Verify with `test -f`.
- **Overlap (P2)**: Remove the duplicated content from whichever file has the less authoritative copy. Keep the
  canonical version in the extracted file; replace the draft copy with a link.
- **Cross-file duplication (P2)**: Remove from all but one file. If multiple files need the same source link, keep it
  only in the file where it's most relevant. Consider whether a shared "common sources" section makes sense — if so, put
  it in ONE file and link from others.
- **Header duplication (P3)**: Keep structural headers each file needs for standalone readability. Remove redundant
  subsection headers.

#### Dynamic Re-Plan Trigger

If the **same check fails 2 consecutive iterations** with the same root cause, the extraction boundaries are likely
wrong. Before fixing again:

1. Revisit Phase 0's extraction map.
2. Consider merging sections that keep creating overlaps, or splitting sections that keep creating lossless gaps.
3. Update the plan file with revised boundaries.
4. Resume from Phase 1 with the revised plan.

#### After Fixing

- After all fixes, update the plan file: append a new iteration log row with what was fixed and updated findings counts.

### Phase 4 — Re-audit

Run Phase 2 checks again on the fixed draft and extracted files. If any FAIL, go back to Phase 3. If all PASS, proceed
to Phase 4.5.

Track the iteration count. If you reach MAX_ITERATIONS (5) without all checks passing, stop and follow the escalation
procedure defined in the Workflow section above.

### Phase 4.5 — User Review Gate

Before replacing the original, present a review summary:

1. Show the final audit report (all 4 checks must be PASS).
2. Show `diff ORIGINAL DRAFT` so the user can see what the source file will look like.
3. List all new files created with their paths.
4. **Wait for user approval** before proceeding to Phase 5.

If the user requests changes, go back to Phase 3. If approved, proceed.

### Phase 5 — Replace

1. **If git is available** (`test -d .git`): Stage all changes first for rollback safety:
   - `git add ORIGINAL TARGET_DIR/`
   - This ensures `git restore --staged` can undo the replacement if needed.
2. Replace the original source with the draft: `cp DRAFT ORIGINAL` (use `cp`, not `mv`, to preserve the draft as a
   backup until verification).
3. Update the plan file: mark all verification checklist items as `[x]` and append the final iteration row.
4. Produce a summary:

```markdown
## Refactoring Audit Report

| Check | Result | Findings | Details |
| --- | --- | --- | --- |
| Lossless | PASS/FAIL | N gaps | X removed lines, Y preserved in docs/ |
| Non-overlapping | PASS/FAIL | N overlaps | X duplicate lines between source and docs/ |
| Unique across files | PASS/FAIL | N dupes | X duplicate lines across docs/ files |
| Links valid | PASS/FAIL | N broken | X broken links found |

Iterations: N (max: 5 per plan)
Files created: list
Files modified: list
Convergence: findings trend [decreasing / stable / increasing]
```

### Rollback Procedure

If post-replacement issues are discovered:

1. **If git was used** (Phase 5 step 1): `git restore --staged ORIGINAL TARGET_DIR/ && git restore ORIGINAL TARGET_DIR/`
2. **If draft backup exists**: `cp DRAFT ORIGINAL` to restore, then investigate.
3. Restore the plan file to the last known-good iteration from the iteration log.
4. Document the rollback reason in the plan file.

## Lessons Learned — What Goes Wrong

Apply these guardrails from the start to avoid common failures:

1. **Tables are the #1 overlap source** — When a table has rows for multiple topics, DO NOT keep the full table in both
   source and extracted files. Split: overview in source, full detail in extracted files.
2. **Source reference sections multiply fast** — Each extracted file will want to cite the same external references.
   Include only sources directly relevant to that file's topic. Do not repeat the full shared source list in every file.
3. **Structural headers are acceptable overlap** — `## Sources`, `## Maintenance` in each file is fine (each file needs
   to be independently readable). Content under those headers should NOT be duplicated.
4. **Links break when paths change** — If files move from `./topic.md` to `./docs/topic.md`, ALL references must update.
   Audit links in Phase 2D, not as an afterthought.
5. **"All X" vs "All Y X" semantic shifts** — If the source says "All items" and you move a subset elsewhere, update the
   qualifier accordingly — but verify the moved items actually exist in their new home.
6. **Verify with git diff, not memory** — Always compare against the pre-extraction version (`git show HEAD:file`) to
   detect what was actually removed.

## Execution Rules

- Work in a single pass per iteration. Do not fix one check and move on — fix ALL findings before re-auditing.
- Fix issues by priority: P0 → P1 → P2 → P3. Never fix P3 while P0/P1 remain.
- Use `git diff` to track changes between iterations.
- After each Phase 4, report the current state of all 4 checks AND the findings counts before deciding to continue.
- Track convergence: findings counts should decrease monotonically. If counts increase or stay flat for 2 iterations,
  trigger a dynamic re-plan (Phase 3 re-plan trigger).
- Enforce MAX_ITERATIONS (5 per plan). Do not silently continue beyond the limit.
- Stop only when all 4 checks report PASS.