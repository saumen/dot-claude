---
name: swordy-verify-docs
description: Verify documentation accuracy against actual project state — source files, configs, scripts. Iteratively audits claims, applies P0/P1 fixes, and re-scans until factual accuracy reaches 100% or max iterations reached.
disable-model-invocation: true
argument-hint: "[file_path]"
---

# Verify documentation accuracy

Verify that `$1` accurately reflects the current project. Cross-reference every claim against actual source artifacts. Run an iterative audit→fix→re-audit loop targeting 100% factual accuracy (P0+P1 = 0). Report P2/P3 findings as informational only.

## Input

The user provides a **file path** as `$1` to the documentation to verify. The path is relative to the project/repo root (or git root).

**CRITICAL**: Never guess or pick a file with the same name in a different location. If `$1` is `src/docs/api-reference.md`, you must read that exact nested file — NOT the `README.md` at the project root, even if both exist.

Resolve the path by:

1. Starting from the project root (or git repo root if available)
2. Navigating to the exact relative path in `$1`
3. Confirming the file exists at that location before proceeding

Example: `/swordy-verify-docs src/docs/api-reference.md` → read `<repo-root>/src/docs/api-reference.md`, NOT `<repo-root>/README.md`

## Scope Definition

Before starting verification, determine the scope:

1. **Primary file**: `$1` — the documentation file passed as argument.
2. **Related artifacts**: Identify all source files, configs, scripts, and other ground-truth materials that the documentation references or could reasonably be expected to describe accurately.
3. **Out of scope**: Files not referenced by the documentation and not logically connected to its subject matter.

Report the determined scope before proceeding: `Primary: <file>, Related: <list>, Out of scope: <brief>`

## Verification Workflow

Run these phases in order. Do NOT skip any phase. Choose the most appropriate verification approach for each claim type based on the project's tools and file formats.

### Phase 1 — Map Claims

Read the documentation file and extract every verifiable claim into a structured list. Each claim must have:

- **Claim ID**: `C-001`, `C-002`, etc.
- **Section**: Where in the doc the claim appears (heading path)
- **Claim text**: The actual statement being made
- **Claim type**: `config` / `file-path` / `behavior` / `number` / `table-data` / `link` / `other`
- **Source referenced**: Which source artifact(s) would verify this claim

Example:

```
C-001 | Section: "Configuration" | Claim: "Database timeout is set to 30s" | Type: config | Source: config/database.yaml [production]
C-002 | Section: "Links" | Claim: "README.md link to docs/architecture.md resolves" | Type: link | Source: filesystem check
```

**Rules for claim extraction:**

- Every table row is a separate claim per cell
- Every code block value is a claim
- Every file path mentioned is a claim (must exist)
- Every URL/link is a claim (must resolve)
- Numbers (ports, timeouts, counts, thresholds) are claims
- Behavioral statements ("X does Y") are claims
- Inheritance or default-value chains described in docs are claims

### Phase 2 — Cross-Reference

For each claim, check against the actual source of truth. Use whatever tools and methods are appropriate for the project's file formats and tooling:

#### Config Value Claims

For claims about configuration values in any format (YAML, JSON, TOML, INI, env files, etc.):

1. Locate the referenced config artifact
2. Find the exact key/section being claimed
3. Compare value exactly (including type: string vs number vs boolean)
4. Note inheritance chains — defaults, environment overrides, or parent sections that influence the effective value

#### File Path Claims

For claims about file paths existing:

1. Verify local files exist on disk
2. For remote URLs, note as unverified unless fetching is warranted by claim criticality

#### Behavioral Claims

For claims about how things work (ports, flags, execution behavior):

1. Read the referenced scripts, configs, or source code
2. Trace the relevant logic path to confirm claimed behavior
3. Verify the claim matches actual implementation

#### Link Validity

For all internal and external links:

1. Internal links: verify target files exist relative to the doc's directory
2. External links: note as unverified unless critical

### Phase 3 — Classify Findings

Every discrepancy found is a "finding." Classify each by severity:

| Severity | Label | Criteria | Example |
|---|---|---|---|
| **P0** | Critical | Factual error that would mislead usage or cause failure | Wrong port number, missing config key, broken file path |
| **P1** | Major | Information is outdated but not immediately harmful | Stale version numbers, deprecated feature still mentioned |
| **P2** | Minor | Content is correct but unclear, incomplete, or could be improved | Missing context, ambiguous wording, formatting issues |
| **P3** | Creative | Suggestion for improvement that goes beyond current scope | New section suggestion, restructuring, additional docs |

### Phase 4 — Audit→Fix Loop

Run an iterative loop targeting 100% factual accuracy. Factual accuracy = `(total_claims - P0_count - P1_count) / total_claims`. Only P0 and P1 findings reduce factual accuracy; P2/P3 are informational.

**Loop procedure (max 5 iterations):**

1. **Audit**: Run Phases 1-3 on the current file state. Produce a full claim map and classification.
2. **Check**: If P0_count == 0 AND P1_count == 0, factual accuracy = 100%. Exit loop successfully.
3. **Fix**: Apply all recommended P0/P1 diffs to the source file. Do NOT touch P2/P3 suggestions.
4. **Re-audit**: Run Phases 1-3 again on the updated file. (Claim IDs reset each iteration — no carry-over.)
5. **Repeat**: Go to step 2. If iteration count reaches 5 and factual accuracy < 100%, stop and report unresolved findings.

**Iteration limits:**

- Max 5 iterations total (including the initial audit as iteration 1).
- If after 5 iterations there are still P0/P1 findings, save the report with unresolved findings marked. Do not continue looping.
- If an iteration produces zero new findings but also has no P0/P1, accuracy = 100% — exit immediately.

**Final report**: Save a single report at the end of the loop (whether accuracy hit 100% or max iterations reached). See Output Format below.

## Output Format

```markdown
## Documentation Verification Report

**File verified**: <absolute file path>
**Date**: <date>

### Scope

- **Primary file**: <path>
- **Related artifacts**: <list each on its own line>
- **Out of scope**: <brief description>

---

### Verification Summary

| Metric | Value |
|---|---|
| Total claims analyzed | N |
| Factual accuracy | X% (N - P0 - P1)/N correct |

### Findings by Severity

#### P0 — Critical (N findings)

| # | Claim ID | Location | Expected | Actual | Fix |
|---|---|---|---|---|---|
| 1 | C-042 | Table row 3, column timeout | 30s | 60s in config.yaml | Update to `30s` |

#### P1 — Major (N findings)

| # | Claim ID | Location | Expected | Actual | Fix |
|---|---|---|---|---|---|
| 1 | C-015 | Section "Deployment" | Docker image uses `v2.3` tag | Latest commit is on `v2.4` branch | Update to `v2.4` |

#### P2 — Minor (N findings)

| # | Claim ID | Location | Issue | Suggestion |
|---|---|---|---|---|
| 1 | C-067 | "Links" section | External link not verified | Mark as "(unverified)" or fetch |

#### P3 — Creative (N findings)

| # | Claim ID | Location | Suggestion |
|---|---|---|---|
| 1 | C-089 | No section on prerequisites | Add environment and dependency requirements section |

---

### Not Applied

Items considered but rejected (with justification):

| Item | Reason |
|---|---|
| <suggestion> | <why not applied> |

---

### Gaps Summary

| Category | Count | Severity | Description |
|---|---|---|---|
| Config drift | N | P0/P1 | Doc values differ from config files |
| File paths | N | P0/P1 | Referenced files don't exist or wrong path |
| Behavioral | N | P0/P1 | Claims about behavior don't match implementation |
| Links | N | P0/P2 | Broken or unverified links |
| Completeness | N | P2/P3 | Correct but missing context |

---

### Recommended Changes (verbatim)

For each P0 and P1 finding, provide the exact text to replace:

```diff
- <current doc text>
+ <corrected doc text>
```

```

## Execution Rules

- **Resolve paths exactly as given**: The provided file path is relative to the project root (or git root). Never substitute a different file with the same name in another directory. If the user provides `src/docs/api-reference.md`, read that exact nested file — not the root `README.md`. Use `find` or equivalent to confirm the file exists at the specified path before proceeding.
- **Read source files before claiming**: Never verify a claim without reading the actual source artifact. If a source file is not found, note it as "source unavailable" and mark the finding accordingly.
- **Claim IDs are persistent**: Use sequential C-NNN numbering throughout the session. Reference them in findings and recommended fixes.
- **Inheritance matters**: For config files with inheritance (defaults, environment overrides, parent sections), verify both the explicit override AND the inherited value. A claim about an inherited value is valid only if the parent section actually defines it.
- **Code blocks are claims too**: Every line in a code block in the documentation is a verifiable claim.
- **Tables = many claims**: Each cell in a table is a separate claim. Don't treat "the table is correct" as one claim — verify each cell.
- **Iterative audit→fix loop**: Run Phases 1-3, apply P0/P1 fixes to the file, re-run Phases 1-3 on the updated file. Repeat until factual accuracy = 100% or 5 iterations reached. Each iteration resets claim IDs.
- **Apply only P0/P1 fixes during loop**: Do not modify the file for P2/P3 findings. They are reported in the final output but do not drive the loop.
- **Factual accuracy = (total - P0 - P1) / total**: Only P0 and P1 count as factual failures. P2/P3 are informational — they do not reduce the factual accuracy score.
- **Be precise with diffs**: When recommending changes, show exact before/after text. No vague suggestions.
- **Verify links exist**: For internal links (`./docs/foo.md`), check file existence relative to the doc's directory.

## Lessons Learned — Common Documentation Drift Patterns

1. **Config values drift first** — Config files are edited frequently; docs lag behind. Always cross-reference every config value mentioned in docs against the actual config artifact.
2. **Table rows become stale** — When new entries or variants are added, old tables may not be updated. Check that every row has a corresponding entry in source configs.
3. **File paths rot** — Renamed files break doc links. Verify all `./relative/path` references resolve.
4. **Numeric values lie** — Scripts and configs change ports, timeouts, counts; docs don't. Every number mentioned must match the actual implementation.
5. **Inheritance assumptions** — Docs may claim a value is "set in section X" when it's actually inherited from a parent/default. Verify the inheritance chain, not just the explicit override.
6. **Stale metrics and versions** — Version numbers and performance figures become outdated quickly. Mark as projected/measured/unverified.
7. **Removed features still documented** — When code removes a flag or option, docs may still reference it. Check that every mentioned feature actually exists in current source.