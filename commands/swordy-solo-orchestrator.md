---
name: swordy-solo-orchestrator
description: Orchestrates a multi-phase challenge-solving workflow within the same session using swordy-* skills. Each phase reads its SKILL.md for workflow knowledge and executes directly — no agents spawned. Phase artifacts are stored as handover documents that feed the next phase.
argument-hint: "[file_path] [problem_statement] [plan_file]"
usage: /swordy-solo-orchestrator [file_path] [problem_statement] [plan_file_path]
---

# Swordy Solo Orchestrator: Same-Session Workflow Orchestration

## Objective

Solve an independent, deterministic challenge using a phased workflow executed entirely within the **same session**. No agents are spawned. Each phase reads its `swordy-*` SKILL.md for workflow knowledge and executes directly using the current agent's tools. Phase artifacts serve as handovers to the next phase.

## Phase-to-Skill Mapping

| Phase | SKILL.md (read for workflow) | Artifact | Input | Output |
|-------|------------------------------|----------|-------|--------|
| Explore | `.../swordy-explore/SKILL.md` | `exploration.md` | None | Problem understanding, constraints, patterns, approach notes |
| Plan | `.../swordy-plan-feature/SKILL.md` | `plan.md` | Exploration handover | Decomposition, milestone checklist (TASK/TEST/VERIFY-XX), acceptance criteria |
| Execute | `.../swordy-plan-execute/SKILL.md` | Solution files + updated `plan.md` + `handover.md` | Plan checklist | Solution files, updated plan (all `- [x]`), handover |
| Review | `.../swordy-review/SKILL.md` | `review.md` | Executor handover + solution files | Audit of correctness/security/performance/coverage; verdict: Success→Deliver, Fail→Fix |
| Fix | *(current agent, no skill)* | Updated solution files | Review findings | Fixed solution → returns to Review (max 3 iterations) |
| Deliver | `.../swordy-git-commit-message/SKILL.md` | Commit message | Staged changes | Commit message + summary table |
| Retro | `.../swordy-retro/SKILL.md` | `retro.md` | All prior handovers + solution files | Timeline, Compliance Audit, What Went Wrong/Well, Summary Table, Key Insight → Teardown |

## Handover Protocol (Same-Session Artifacts)

All artifacts are written to the **project repo** under `docs/{phase}/`. The workspace directory is the project root (inferred from CWD or the repo containing the problem statement file).

### Artifact Paths

| Phase | Artifact | Path |
|-------|----------|------|
| Explore | `exploration.md` | `{workspace_dir}/docs/explorations/{YYYYMMDDHHMM}__{feature-slug}/exploration.md` |
| Plan | `plan.md` | `{workspace_dir}/docs/plans/{YYYYMMDDHHMM}__{feature-slug}/plan.md` |
| Execute | `handover.md` + solution files | `{workspace_dir}/docs/executions/{YYYYMMDDHHMM}__{feature-slug}/handover.md` |
| Review | `review.md` | `{workspace_dir}/docs/reviews/{YYYYMMDDHHMM}__{feature-slug}/review.md` |
| Retro | `retro.md` | `{workspace_dir}/docs/retros/{YYYYMMDDHHMM}__{feature-slug}/retro.md` |

### Handoff Map (artifact feeds the next phase)

| From Phase | Artifact | To Phase |
|------------|----------|----------|
| Explore | `exploration.md` | Plan |
| Plan | `plan.md` | Execute |
| Execute | Handover + solution files | Review |
| Review | `review.md` | Fix (if failed) or Deliver |
| Fix | Updated solution files | Review (re-entry) |
| Deliver | Commit message + summary table | Retro |
| Retro | `retro.md` | Teardown |

### Artifact Verification & Transition Contract

After writing each artifact:

1. **Append a "Phase Transition Contract" section** to the bottom of the artifact (see `docs/designs/phase-transition-contract.md` for schema).
   - Include: Start/End timestamps, SHA256 hash, and a bulleted **Proof of Work (PoW)** list of actual tool calls made.
2. **Read it back** to confirm content and contract were written correctly.
3. **Lead Verification Gate:** Before proceeding to the next phase, the Lead must verify:
   - **Integrity:** SHA256 matches.
   - **Evidence:** PoW list matches actual session history tool calls.
   - **Substance:** Artifact is substantive (not "thin").
   - **Duration:** Timing is reasonable.
4. **Verdict:** If verification fails, the phase is **REJECTED**; the agent must perform missing work and regenerate the artifact. If it passes, the transition is **APPROVED**.

## Orchestration Protocol (Same Session)

### Golden Rules

1. **Sequential execution only** — one phase at a time, in order.
2. **Read SKILL.md at the start of each phase** — summarize the workflow in 3 bullet points **and identify the required template path (e.g., `references/*.md`)** before executing.
3. **Execute directly** — use your own tools (read, edit, write, bash). Do NOT spawn sub-agents or use the Skill tool.
4. **Write handover artifacts** after each phase — they are the contract for the next phase.
5. **Use accurate timestamps** — Always use `bash` with `TZ="America/Los_Angeles"` to get the current datetime in PT for filenames and any timeline entries. Do not assume or hallucinate the time.

### Phase Sequence

```
Explore → Plan → Execute → Review → (Fix if review failed) → Review again → ... → Deliver → Retro → Teardown
```

### Phase Execution Template

For each phase, follow this pattern:

```
1. Read the SKILL.md at {skill_path}, summarize the workflow in 3 bullet points, and identify the required template path.
2. Read the input handover artifact from the previous phase (if any).
3. Execute the {phase} workflow directly using your own tools.
4. Produce the {phase} artifact at {workspace_dir}/docs/{phase}/{YYYYMMDDHHMM}__{feature-slug}/{artifact_name}.
   **IMPORTANT: Ensure the artifact strictly adheres to the structure and sections of the identified template.**
5. **Create the Phase Transition Contract:** Append the contract section (Timestamps, SHA256, PoW) to the artifact.
6. **Lead Verification Gate:** Cross-reference PoW vs Session History and validate substance. 
7. **Verdict:** If APPROVED, read back the artifact and present a concise summary to the user. If REJECTED, return to step 3.
8. Proceed to the next phase (unless a checkpoint requires user input).
```

### Safeguards

#### Fix Loop

- Maximum **3 iterations** of Review → Fix → Review.
- If the review still fails after 3 fix iterations, report the verdict to the user and proceed to Deliver with a note about remaining issues.

#### Stuck Detection

- If a phase produces no meaningful output after 2 attempts, interrupt and ask the user for guidance.
- Never loop more than 2 times on the same phase without user input.

#### Prerequisite Checks

| Phase | Prerequisite | Action if missing |
|-------|-------------|-------------------|
| Plan | Explore handover exists | Skip to Plan with empty context |
| Execute | Plan checklist section exists | Ask user to run Plan phase first |
| Review | Execute handover exists | Skip to Review with "no solution" note |
| Deliver | Review verdict is Success | Skip if review failed and max iterations reached |
| Deliver | Git repo exists | Skip with note: "no git repo — deliver phase skipped" |
| Retro | All prior phase handovers exist | Use available handovers; mark missing as "N/A" |

## Problem Statement

**`$1` — file path:** If `$1` is a file path, `Read` the file and use its content as the problem statement.

**`$2` — problem string:** If `$1` is a string (not a file), use it directly as the problem statement.

**`$3` — plan file:** If `$3` is a file path, skip Explore and Plan, proceed to Execute using it as the plan artifact.

**Default problem (no args):** Deterministic topological sort on DAG `{"X":["Y","Z"],"Y":["W"],"Z":["W"],"W":[]}` with cycle detection, returning `["X","Z","Y","W"]`.

## Plan File (`$3`)

A pre-existing plan file path. If `$3` is provided, the agent **skips Explore and Plan**, goes directly to **Execute**.

- The plan file must follow the same structure as `docs/plans/{YYYYMMDDHHMM}__{feature-slug}/plan.md` (see `references/plan_template.md`).
- If `$3` is given but does not exist, the agent falls back to running Explore then Plan as normal.
- If `$3` is not provided, the agent runs Explore then Plan as normal.

## Quick Reference

- Same-session execution — no agents spawned.
- Fix loop max iterations — 3.
- Checkpoint after Plan and Review verdicts.
- SKILL.md read for workflow knowledge only; execute directly.
