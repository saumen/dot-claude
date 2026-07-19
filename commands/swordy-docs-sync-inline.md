---
name: swordy-docs-sync-inline
description: Create or update README.md and AGENTS.md inline (no sub-agents). Detects running harness and adapts safety mechanisms accordingly.
disable-model-invocation: true
argument-hint: "[no args — runs against current working directory]"
---

# Docs-Sync Inline (Harness-Agnostic)

Create or update `README.md` and `AGENTS.md` in the **current working directory** using inline execution. No sub-agent delegation — all work happens in this session.

## Harness Detection

At startup, detect the running harness:

```bash
# Check for omp indicators
if [ -n "$OMP_HOME" ] || [ -n "$OMP_WORKSPACE" ]; then
  HARNESS_TYPE="omp"
elif [ -d ~/.omp/agent ]; then
  HARNESS_TYPE="omp"
else
  HARNESS_TYPE="standard"
fi

echo "Detected harness: $HARNESS_TYPE"
```

**Safety layer adapts based on detection:**
- **omp mode**: Use session snapshots, state variables if available
- **standard mode**: Use file-based *.backup and *.draft files

---

## Pre-Phase: Load & Prepare

### Step 1: Detect Harness

Run the detection script above. Store result as `HARNESS_TYPE`.

### Step 2: Load Workflow Specifications (Once, Cached)

Read and parse both reference documents:

| File | Purpose | Cached Rules |
|------|---------|--------------|
| `/Users/swordfish/.claude/commands/swordy-refactor-docs.md` | Refactoring workflow | 4 checks: lossless, non-overlapping, unique, links. Max 5 iterations (use 3 for inline). |
| `/Users/swordfish/.claude/commands/swordy-verify-docs.md` | Verification protocol | Claim extraction, P0/P1/P2/P3 classification, audit→fix loop. Max 5 iterations (use 3 for inline). |

**Store these rules in memory** — do NOT re-read them during loops.

### Step 3: Initialize Safety Layer

**If HARNESS_TYPE == "omp":**
- Use omp session state for caching (if available)
- Create backup snapshots using omp mechanisms

**If HARNESS_TYPE == "standard":**
- Create `backup/` directory
- Copy existing README.md and AGENTS.md to `backup/` with timestamp
- Use `*.draft` files for all intermediate work

---

## Phase 1: Inventory Current State

Scan the working directory:

1. **Directory structure**: `find . -maxdepth 3 -not -path './.git/*' -not -path '*/node_modules/*' | head -80`
2. **Check existing docs**: Read README.md and AGENTS.md if they exist
3. **Identify key artifacts**: Scripts, configs, package manifests, etc.
4. **Document dependencies**: Note package files and their purposes

Report inventory summary before proceeding.

---

## Phase 2: Audit & Refactor (Inline Loop)

### Audit Step

Check existing docs against audience separation principle:

**README.md violations:**
- Contains AI/developer-specific content → VIOLATION
- Focuses on setup, usage, workflow → CORRECT

**AGENTS.md violations:**
- Contains user-facing setup/usage → VIOLATION
- Focuses on structure, conventions, commands → CORRECT

### Refactor Loop (Max 3 Iterations)

If violations found, execute this loop:

```
For iteration = 1 to 3:
  1. Read current state of docs
  2. Apply refactoring per cached swordy-refactor-docs rules (Verify 'Lossless' via sha256sum)
  3. Create working copy (draft file or omp state)
  4. Run 4 verification checks:
     - Lossless: No factual content lost (verified via sha256sum)
     - Non-overlapping: No duplication between draft and extracted files
     - Unique: No cross-file duplication
     - Links: All internal links resolve
  5. If all 4 checks PASS → commit changes, exit loop
  6. If any check FAILS → fix issues, continue to next iteration
  7. After 3 iterations → commit best version, log unresolved findings

If NO violations found → skip to Phase 3
```

---

## Phase 3: Generate README.md (Human-Oriented)

Write or update `README.md`:

# <Project Name>

<Brief one-line description of what the project does. No fluff.>

## Setup

<How to get running: clone, install deps, env setup. Step-by-step commands.>

## Usage

<How to use the project: main workflow, scripts, commands. What inputs/outputs.>

## Expected Workspace Structure

<Directory layout with comments explaining each directory's purpose.>

## <Feature-Specific Sections>

<Per-feature usage sections as needed — one per major capability.>

---

_Note: This directory is managed by the docs-sync prompt. Manual edits should be handled with care to avoid disrupting system-managed files._

**Guidelines:**
- Include setup commands, env vars, config files
- Describe workflow end-to-end
- Document directory layout
- Cover major features
- **Exclude**: commit conventions, code structure, agent instructions

---

## Phase 4: Generate AGENTS.md (AI/Developer-Oriented)

Write or update `AGENTS.md`:
# <Project Name> — Repository Guidelines

## Documentation & File Purposes

This project uses multiple markdown files, each with a distinct audience and scope. Do not duplicate content across them.

| File | Audience | Scope |
|---|---|---|
| [`README.md`](README.md) | End users | Setup, workspace layout, workflow, feature usage |
| [`AGENTS.md`](AGENTS.md) (this file) | Developers & AI assistants | Project structure, testing commands, commit conventions, development guidance |
| [`.editorconfig`](.editorconfig) | All developers | Indentation, hard wrap, trailing newline rules for every file (include only if present) |
| [`docs/plans/*.md`](docs/plans/*.md) | Implementation tracking | Planning documents with TODO lists — no implementation snippets |
| [`PYTHON_GUIDELINES.md`](PYTHON_GUIDELINES.md) | Python contributors | Coding standards for Python scripts (include only if present) |
| [`SHELL_SCRIPTING_GUIDELINES.md`](SHELL_SCRIPTING_GUIDELINES.md) | Shell script contributors | Standards for shell scripting in the project (include only if present) |

**Rule:** If content belongs to a user-facing guide (setup, usage), it goes in README. If it's developer/AI guidance (standards, conventions, structure), it goes here or in the dedicated guideline files linked above. Planning docs stay in `docs/plans/`.

## Project Structure & Module Organization

<Directory tree showing actual project layout with comments explaining each component.>

## Build, Test, and Development Commands

| Command | Purpose |
|---|---|
| `<command>` | <What it does> |
| ... | ... |

### <Context-Specific Notes>

<Any important caveats about commands — e.g., "use python3 from conda env".>

- Use conventional commit prefixes (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`). Imperative mood, subject line under 72 characters, no trailing period.
- Example: `feat: Add <feature>`
- PRs should include a clear description, link related issues, and note any environment variable changes.

## Documentation & Planning

<Links to relevant docs, plans, specs, skills.>

## Agent-Specific Instructions

<Technical instructions for AI agents — what to read before modifying code, patterns to follow, etc.>

## <Domain-Specific Guidelines>

<Per-module or per-skill development guidelines as needed.>
```

**Guidelines:**
- Include file-purpose table
- Provide actual directory tree
- List all dev commands
- Document commit conventions
- Include agent-specific technical instructions
- **Exclude**: user-facing setup/usage

---

## Phase 5: Cross-Reference Verification

Before finalizing, ensure:

1. AGENTS.md links to README.md
2. No content duplicated across both files (cross-reference instead)
3. Directory tree matches actual filesystem
4. All referenced files exist

---

## Phase 6: Write Files

Write both files to disk:

**If HARNESS_TYPE == "omp":**
- Use omp state mechanisms if available
- Otherwise use standard file I/O

**If HARNESS_TYPE == "standard":**
- Write to `*.draft` first
- Validate against Phase 5 checks
- Replace originals only after validation passes

Confirm:
- README.md: human-oriented ✓
- AGENTS.md: AI/developer-oriented + links to README ✓
- No cross-contamination ✓

---

## Phase 7: Verify (Inline Loop)

### ⚠️ CRITICAL: Token Safety & Efficiency Protocol
To prevent token exhaustion and truncation:
- **NEVER** pass file content as a string literals into an `eval` cell (e.g., `content = \"\"\"...\"\"\").
- **ALWAYS** load content directly inside the `eval` cell using `content = read('path')`.
- **SINGLE-PASS**: Combine extraction, verification, and classification into a single `eval` call to minimize round-trips.

### 🛠️ Technical Implementation Strategy

To maintain maximum efficiency and prevent token exhaustion, adhere to these tool selection rules:

| Task Type | Recommended Tool | Why? |
| :--- | :--- | :--- |
| **Pattern Searching** | `ripgrep` (`rg`) | Respects `.gitignore` and is highly optimized for repo-wide searches. |
| **Integrity (Lossless)** | `sha256sum` | Use hashing to verify that a refactor did not accidentally change unmapped content. |
| **Structural Audit** | `glob` | Faster and less noisy than `find` for matching specific file patterns. |
| **Parsing** | `re` (Python) | Best for extracting claims from semi-structured Markdown within an `eval` cell. |
| **Data Loading** | `read()` | **Mandatory** for all `eval` cells to avoid token limit errors. |

### Verification Loop (Max 3 Iterations per Doc)

For each doc in [README.md, AGENTS.md]:

```
For iteration = 1 to 3:
  1. Execute a single `eval` cell performing "Single-Pass Analysis":
     - Use `read('path')` to load the document.
     - Use `re` to extract all verifiable claims.
     - For each claim, verify against source artifacts using the most efficient tool:
       - Config values/patterns $\rightarrow$ `rg` (ripgrep)
       - File/Directory existence $\rightarrow$ `glob` or `ls`
       - Implementation/Behavior $\rightarrow$ `bash` or `grep`
       - Structural Integrity $\rightarrow$ `sha256sum` (to ensure lossless refactor)
     - Classify findings: P0 (Critical), P1 (Major), P2 (Minor), P3 (Creative).
     - Return a structured list of findings (e.g., `[{'id': 'C-001', 'status': 'P0', 'reason': '...'}]`).

  2. If findings contain P0 or P1:
     - Apply fixes via `edit` or `write`.
     - Continue to next iteration.

  3. If findings contain only P2/P3 or are empty:
     - Mark as verified and exit loop.

  4. After 3 iterations:
     - Report final accuracy metrics: 
       (Total Claims, P0, P1, P2, P3, and % Accuracy).
```
```

---

## Phase 8: Final Report

Produce summary:

```markdown
## Docs Sync Report

| File | Action | Lines | Key Sections |
|------|--------|-------|--------------|
| README.md | Created/Updated | N | Setup, Usage, Features |
| AGENTS.md | Created/Updated | N | Structure, Commands, Conventions |

### Verification Results

- README.md: P0=0, P1=0, P2=N, P3=N — accuracy X%
- AGENTS.md: P0=0, P1=0, P2=N, P3=N — accuracy X%

### Harness

- Detected: $HARNESS_TYPE
- Safety layer: <omp session snapshots / file-based backups>

### Refactoring Applied

- [ ] Audience separation violations found and refactored
- [ ] No violations — files were already well-separated

### Unresolved Issues

<List any P0/P1 findings that remained after 3 iterations>
```

---

## Safety Guarantees

| Risk | Mitigation |
|------|------------|
| Corrupting original files | Always write to draft first, validate, then replace |
| Data loss | Lossless check before every replacement |
| Session state drift | Read-only zone for specs, working zone for drafts |
| Failed mid-execution | Backup before changes, documented rollback path |
| Infinite loops | Hard limit of 3 iterations with explicit exit |

---

## Rollback Instructions

If something goes wrong:

**For standard mode:**
```bash
# Restore from backup
cp backup/README.md.<timestamp> README.md
cp backup/AGENTS.md.<timestamp> AGENTS.md
```

**For omp mode:**
- Use omp's session rollback mechanism if available
- Otherwise restore from backup/ directory
```
