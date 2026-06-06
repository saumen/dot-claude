---
name: swordy-team-orchestrator
description: Runs a multi-agent team-based orchestration to solve a challenge using swordy-* skills. A teammate read an assigned SKILL.md files for workflow knowledge and execute work directly — they do NOT use the Skill tool (that would create a circular agent spawn loop).
usage: /swordy-team-orchestrator [problem_statement | file_path]
---

# Swordy Team Orchestrator: Team-Based Orchestration

## Objective

Solve an independent, deterministic challenge using a coordinated team of agents. The orchestration spawns typed agents that **read** `swordy-*` SKILL.md files for workflow knowledge and execute the work directly using their own tools. Agents read SKILL.md for workflow; see Golden Rules.

## Agent-to-Skill Mapping

| Phase | Agent (spawned) | SKILL.md (read for workflow) | Artifact | Input | Output |
|-------|----------------|------------------------------|----------|-------|--------|
| Explore | `swordy-agent-explorer` | `.../swordy-explore/SKILL.md` | `exploration.md` | None | Problem understanding, constraints, patterns, approach notes |
| Plan | `swordy-agent-planner` | `.../swordy-plan-feature/SKILL.md` | `plan.md` | Exploration handover | Decomposition, milestone checklist (TASK/TEST/VERIFY-XX), acceptance criteria |
| Execute | `swordy-agent-execute` | `.../swordy-plan-execute/SKILL.md` | `solution.py` + updated `plan.md` + `handover.md` | Plan checklist | Solution files, updated plan (all `- [x]`), handover |
| Review | `swordy-agent-reviewer` | `.../swordy-review/SKILL.md` | `review.md` | Executor handover (TEST-OUTPUT + SOLUTIONS) | Audit of correctness/security/performance/coverage; verdict: Success→Deliver, Fail→Fix |
| Fix | `swordy-agent-execute` | *(none)* | Updated solution files | Review findings | Fixed solution → returns to Review (max 3 iterations) |
| Deliver | `swordy-agent-git-commit-message` | `.../swordy-git-commit-message/SKILL.md` | Commit message (no file) | Staged changes | Commit message + summary table (compiled by Team Lead) |
| Retro | `swordy-agent-execute` | `.../swordy-retro/SKILL.md` | `retro.md` | All prior handovers + solution files | Timeline, What Went Wrong/Well, Summary Table, Key Insight → Teardown |

## CWD-Independent Handover Protocol

**The benchmark runner does not guarantee a shared CWD between the main session and spawned agents.**

1. **Team Lead passes the absolute workspace directory** (`workspace_dir`) to every spawned agent.
2. **Agents resolve artifact paths** as `{workspace_dir}/docs/{phase}/{timestamp}__{slug}/{artifact_template}`.
3. **Agents return** the absolute file path and `sha256sum` checksum after writing.
4. **Team Lead verifies** the artifact — see Team Lead Verification below.

Agent return format:
```
Artifact: {artifact_template}
Path: /absolute/path/to/workspace/docs/{phase}/{timestamp}__{slug}/{artifact_template}
Checksum: <sha256sum>
```

**Handoff Map** (artifact feeds the next phase):

| From Phase | Artifact | Resolved Path | To Phase |
|------------|----------|---------------|----------|
| Explore | `exploration.md` | `{workspace_dir}/docs/explorations/{timestamp}__{slug}/exploration.md` | Plan |
| Plan | `plan.md` | `{workspace_dir}/docs/plans/{timestamp}__{slug}/plan.md` | Execute |
| Execute | Solution files + updated plan (all `- [x]`) + `handover.md` | {workspace_dir}/docs/executions/{timestamp}__{slug}/handover.md | Review / Retro |
| Review | `review.md` | `{workspace_dir}/docs/reviews/{timestamp}__{slug}/review.md` | Fix (if failed) or Deliver |
| Fix | Updated solution files | (solution-specific paths) | Review (re-entry) |
| Deliver | Commit message + summary table | (no file) | Retro |
| Retro | `retro.md` | `{workspace_dir}/docs/retros/{timestamp}__{slug}/retro.md` | Teardown |

### Team Lead Verification

1. Read the handover at the returned absolute path.
2. Run `sha256sum <path>` and **compare the output against the checksum the agent returned**.
3. Validate meaningful content (non-empty, relevant to the phase).
**If checksums don't match → protocol violation. Reject the artifact and ask the agent to rewrite.** Do not proceed past a checksum mismatch.
**If passes → spawn next phase. If fails → send follow-up with specific feedback (do not proceed).**

## Orchestration Protocol (Team of Agents)

### Golden Rules

1. **Sequential execution only** — NEVER spawn multiple teammates in parallel. One `Agent` call per turn.
2. **Agents execute directly** — they do NOT invoke skills. `subagent_type` encodes the role; SKILL.md is read for workflow knowledge only.
3. **Anti-patterns (FORBIDDEN):** Creating all teammates upfront; using `parallel()` or any concurrent mechanism; telling an agent to use the `Skill` tool (circular dependency).

### Phase Sequence

```
Explore → Plan → Execute → Review → (Fix if review failed) → Review again → ... → Deliver → Retro → Teardown
```

**Shared prompt template** (use for Explore, Plan, Review phases — replace `{phase}`, `{artifact_template}`, `{skill_path}`, and `{input_doc}`):

```
Your workspace directory is {workspace_dir}.
Phase: {phase}. Artifact template: {artifact_template}

1. Read the SKILL.md at {skill_path} and summarize the workflow in 3 bullet points.
2. {input_doc}
3. Execute the {phase} workflow directly using your own tools — see Golden Rules for skill invocation policy.
4. Produce the {phase} handover document at {workspace_dir}/docs/{phase}/{YYYYMMDDHHMM}__{feature-slug}/{artifact_template}.
5. Compute the SHA256 of your artifact using `sha256sum <path>` and include the
   actual output in your return. Do not fabricate or estimate checksums.
6. After writing your artifact, follow the Shutdown Protocol section to terminate.
```

### Safeguards

#### Escalation

If an agent stalls, send **one** follow-up with specific feedback. If it stalls again, intervene directly. Never wait more than 2 follow-up turns per agent.

#### Health-Check Thresholds

- **5-minute tool-call timeout:** Agent is stalled if no tool calls for >5 minutes.
- **10-minute no-artifact escalation:** If no artifact within 10 minutes, check tmux panes. If pane is gone, intervene directly. If pane exists but agent is silent, send follow-up.

#### Prerequisite Checks

| Phase | Prerequisite | Action if missing |
|-------|-------------|-------------------|
| Plan | Explore handover exists | Skip to Plan with empty context |
| Execute | Plan checklist section exists | Ask user to run Plan phase first |
| Review | Execute handover exists | Skip to Review with "no solution" note |
| Deliver | Review verdict is Success | Skip if review failed and max iterations reached |
| Deliver | Git repo exists | Skip with note: "no git repo — deliver phase skipped" |
| Retro | All prior phase handovers exist | Use available handovers; mark missing as "N/A" |

### Version-Pinning Artifacts

At the start of each phase, **copy** the artifacts the receiving agent will read, referencing those copies by SHA256.

- Use `cp` (not `cp -l`) for artifacts that may be modified after the receiving phase reads them.
- Only use `cp -l` for read-only artifacts (e.g., the exploration handover).
- If the source artifact does not exist yet, wait and retry up to 3 times with 10-second intervals. If still missing, report the error and skip.

## Shutdown Protocol

### Agent Self-Termination (Primary + Secondary Signals)

1. **Write the `.done` marker file** (primary signal) at `{workspace_dir}/docs/artifacts/{phase}.done`:
   `artifact_path: {path} | sha256: {checksum} | timestamp: {ISO-8601}`
2. **Send shutdown response** (secondary signal): `{type: 'shutdown_response', request_id: 'self', approve: true}` to itself (Shutdown Response Path B). Updates `isActive` if processed; file-based signal ensures cleanup regardless.

### Team Lead Batch-Shutdown Ordering

Shutdown completed agents *before* spawning the next phase:
`Verify handover → Shutdown completed agent → Spawn next phase → Update isActive`

**Tertiary fallback:** If an agent does not self-shutdown, the Team Lead sends a shutdown message via the batch-shutdown step. Best-effort only -- never the first option.

**Batch shutdown:** Send shutdown messages to all teammates in a single parallel Agent call (the spec forbids parallel *work* agents, but shutdown messages are just notifications).

### Teardown

After Retro completes, shut down all remaining teammates and delete the team.

## Problem Statement
**The problem statement is provided as an argument to this command.**

- If the argument is a string, use it directly.
- If the argument is a file path, `Read` the file and use its content.

**Default Problem Statement (if no argument):** Perform deterministic topological sort on DAG `{"X":["Y","Z"],"Y":["W"],"Z":["W"],"W":[]}` with cycle detection, returning `["X","Z","Y","W"]`.

## Quick Reference

- Sequential execution — see Golden Rules.
- Agent self-termination — see Shutdown Protocol.
- Fix loop max iterations — see Phase Sequence.
